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
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - n_fail} passed, {n_fail} failed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
