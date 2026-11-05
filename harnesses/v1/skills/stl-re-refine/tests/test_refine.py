#!/usr/bin/env python3
"""Synthetic tests for the refine loop (no real scan needed). Exit 0 = all passed.

A known part is tessellated as the "scan". The loop starts from a base body without the
features, and must find them with the right type and size.

  python3 tests/test_refine.py [--keep DIR]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE.parents[1] / "stl-re-build" / "scripts"))

import devmap  # noqa: E402
from classify import classify  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def make_scan(part, d: Path, name: str):
    from build123d import export_stl
    p = d / f"{name}.stl"
    export_stl(part, str(p), tolerance=0.005, angular_tolerance=0.05)
    al = d / f"{name}_alignment.json"
    al.write_text(json.dumps({"matrix_4x4": np.eye(4).tolist(), "scan_noise_mm": {"value": 0.01}}))
    return p, al


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=Path)
    a = ap.parse_args()
    from build123d import Align, Box, Cylinder, Pos
    tmp = a.keep or Path(tempfile.mkdtemp(prefix="v1_refine_"))
    tmp.mkdir(parents=True, exist_ok=True)

    base = Box(30, 20, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hole = Pos(6, 2, -1) * Cylinder(2.0, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    boss = Pos(-7, 0, 8 - 0.5) * Cylinder(3.0, 4.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pocket = Pos(-2, -4, 5) * Box(8, 5, 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    truth = base - hole + boss - pocket
    scan, al = make_scan(truth, tmp, "truth")
    S = devmap.sample_scan(scan, al, 60_000, 0)
    cad = devmap.body_mesh(base)
    d = devmap.signed_s2c(S.P, cad)
    cl = devmap.clusters(S.P, d, 0.1, 3 * S.spacing, 30)
    check("clusters found (hole -, boss +, pocket -)", len(cl) >= 3, str([(c['sign'], c['n']) for c in cl]))

    def best_for(sign, near):
        cs = [c for c in cl if c["sign"] == sign and np.linalg.norm(np.array(c["centroid"][:2]) - near) < 4]
        if not cs:
            return None, []
        c = cs[0]
        return c, classify(S.P[c["idx"]], S.N[c["idx"]], sign, S.noise, S.spacing, "T", "test", cad)

    c, H = best_for(-1, np.array([6, 2]))
    hs = [h for h in H if h["kind"] == "cyl-hole"]
    check("hole -> cyl-hole r=2.0", bool(hs) and abs(hs[0]["size"][0] - 2.0) < 0.03,
          str(hs[0]["size"] if hs else [h["kind"] for h in H]))
    check("hole axis snapped to Z", bool(hs) and abs(abs(hs[0]["axis"][2]) - 1) < 1e-9)
    c, H = best_for(+1, np.array([-7, 0]))
    hb = [h for h in H if h["kind"] in ("cyl-boss", "revolve")]
    check("boss -> cylinder/revolve r=3.0", bool(hb) and abs(hb[0]["size"][0] - 3.0) < 0.05,
          str([(h['kind'], np.round(h['size'], 3).tolist()) for h in hb[:2]]))
    c, H = best_for(-1, np.array([-2, -4]))
    hp = [h for h in H if h["kind"].startswith("prism")]
    check("pocket -> prism along Z", bool(hp) and abs(abs(hp[0]["axis"][2]) - 1) < 1e-9,
          str([(h['kind'], h['variant']) for h in hp[:3]]))

    # end-to-end loop from the base box
    base_tree = {"schema": "feature_tree@v1", "part": "synthetic",
                 "params": {"L": {"value": 30.0, "source": "scan"}, "W": {"value": 20.0, "source": "scan"},
                            "H": {"value": 8.0, "source": "scan"}},
                 "nodes": [{"id": "F01", "op": "box", "combine": "new", "size": ["L", "W", "H"], "align": "min",
                            "place": [{"pos": ["-L/2", "-W/2", 0]}]}]}
    bt = tmp / "base_tree.json"
    bt.write_text(json.dumps(base_tree))
    out = tmp / "loop"
    from loop import main as loop_main
    rc = loop_main(["--tree", str(bt), "--scan", str(scan), "--alignment", str(al), "--band", "0.1",
                    "--out", str(out), "--rounds", "8", "--samples", "60000", "--c2s-samples", "30000",
                    "--min-area", "0.5"])
    log = json.loads((out / "refine_log.json").read_text())
    acc = [r["accepted"] for r in log["rounds"] if r.get("accepted")]
    kinds = sorted(x["kind"] for x in acc)
    check("loop rc 0", rc == 0)
    check("loop accepted hole, boss and pocket", {"cyl-hole"} <= set(kinds) and
          any(k in kinds for k in ("cyl-boss", "revolve")) and any(k.startswith("prism") for k in kinds), str(kinds))
    fm = log["final"]["metrics"]
    check("final scan->CAD p95 below 0.05 mm", fm["s2c_p95"] < 0.05, f"p95 {fm['s2c_p95']:.4f}")
    tree = json.loads((out / "feature_tree.json").read_text())
    ref = json.loads((out / "params_refine.json").read_text())["params"]
    used = set()
    for n in tree["nodes"][1:]:
        used |= {k for k in ref if k in json.dumps(n)}
    check("every accepted node is driven by named scan params", len(used) > 0 and all(
        ref[k]["source"] == "scan" for k in used))
    # --- refit: the base box is 0.4 mm too low; the loop must fix H, not add a feature -------------
    from build123d import Box as _Box
    tall = _Box(30, 20, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
    scan2, al2 = make_scan(tall, tmp, "tall")
    bt2 = tmp / "base_low.json"
    low = json.loads(json.dumps(base_tree))
    low["params"]["H"]["value"] = 7.6
    bt2.write_text(json.dumps(low))
    out2 = tmp / "loop_refit"
    rc = loop_main(["--tree", str(bt2), "--scan", str(scan2), "--alignment", str(al2), "--band", "0.1",
                    "--out", str(out2), "--rounds", "4", "--samples", "60000", "--c2s-samples", "30000",
                    "--min-area", "0.5"])
    log2 = json.loads((out2 / "refine_log.json").read_text())
    acc2 = [r["accepted"] for r in log2["rounds"] if r.get("accepted")]
    pr2 = json.loads((out2 / "params_refine.json").read_text())["params"]
    check("refit accepted instead of a new feature", bool(acc2) and acc2[0]["kind"] == "refit",
          str([(x["kind"], x.get("changes")) for x in acc2]))
    check("refit moved H to 8.0", "H" in pr2 and abs(pr2["H"]["value"] - 8.0) < 0.02,
          str(pr2.get("H", {}).get("value")))
    tree2 = json.loads((out2 / "feature_tree.json").read_text())
    check("refit added no node", len(tree2["nodes"]) == 1)

    # --- slot merge: two parallel equal-radius bosses become one stadium prism ---------------------
    from refine_ops import slot_merge
    rods_tree = {"nodes": [
        {"id": "A", "op": "cylinder", "combine": "add", "r": "ra", "h": "ha", "at": [0, 0, 0],
         "frame": {"origin": [0, -4, 10], "z_dir": [1, 0, 0], "x_dir": [0, 1, 0]}},
        {"id": "B", "op": "cylinder", "combine": "add", "r": "ra", "h": "ha", "at": [0, 0, 0],
         "frame": {"origin": [0, 4, 10], "z_dir": [1, 0, 0], "x_dir": [0, 1, 0]}}]}
    prm = {"ra": {"value": 1.5, "source": "scan"}, "ha": {"value": 5.0, "source": "scan"}}
    res = slot_merge(rods_tree, prm, "M", 0.01)
    ok = res is not None and res[2] == {"A", "B"}
    if ok:
        sp = res[1]
        Lv = next(v["value"] for k, v in sp.items() if k.endswith("_L"))
        Wv = next(v["value"] for k, v in sp.items() if k.endswith("_W"))
        ok = abs(Lv - 11.0) < 1e-6 and abs(Wv - 3.0) < 1e-6
    check("slot merge: 2 rods r1.5, 8 apart -> slot L 11 W 3", ok, str(res[1] if res else None))
    from build_tree import build as _build
    t3 = {"nodes": [{"id": "S", **{k: v for k, v in res[0].items()}, "combine": "new"}]} if res else None
    if t3:
        body3, log3, _ = _build(t3, {**prm, **res[1]})
        vol = body3.volume if body3 is not None else 0
        exp = (8 * 3 + np.pi * 1.5 ** 2) * 5
        check("slot prism builds with the stadium volume", log3["status"] == "OK" and abs(vol - exp) < 1e-3 * exp,
              f"{vol:.3f} vs {exp:.3f}")

    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - n_fail} passed, {n_fail} failed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
