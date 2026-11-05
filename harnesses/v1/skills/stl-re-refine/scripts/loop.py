#!/usr/bin/env python3
"""loop.py - staged deviation refine loop (harness v1, M2).

Start: a feature tree that holds the datum-frame base body (dominant silhouette). Each round:
  1. build the tree, compute the signed scan->CAD map and CAD->scan distances;
  2. split the red regions into clusters (+ material missing, - extra CAD material);
  3. for the largest unexhausted cluster, classify.py proposes hypotheses (cylinder, revolve,
     prism with variants for extent and draft);
  4. every candidate is really built and measured. The best one is kept only if the loop
     objective J falls (devmap.metrics). Otherwise the body is unchanged and the cluster
     counts one failed attempt;
  5. pattern step: sibling clusters with the same hypothesis become ONE repeated node (one
     instance + placements). Sizes within noise share one param; per-instance values stay
     as measured;
  6. if the two best candidates of different kinds are within CARD_MARGIN of each other, a
     decision card is written. The arbiter `auto` takes the lower J and records that. The
     arbiter `agent` stops the loop so the agent (or, in M4, the user) answers the card.
A cluster that fails MAX_ATTEMPTS times becomes an open point, never a free-form pad.

Outputs (--out): feature_tree.json (base + accepted nodes), params_refine.json (params the
loop measured, source "scan"), refine_log.json (rounds, candidates with J, accepted
nodes, open points), cards/NNN.json, rounds/<k>_metrics.json.

  python3 loop.py --tree base_tree.json --params measure/params.json --scan input/scan.stl \
      --alignment intake/alignment.json --band 0.30 --out refine/
Builder self-check only (CHK-INDEP). The final grade is stl-re-verify.
"""
from __future__ import annotations

import argparse
import copy
import json
import string
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "stl-re-build" / "scripts"))

import devmap  # noqa: E402
from build_tree import build, load_params  # noqa: E402
from classify import Namer, classify  # noqa: E402

CARD_MARGIN = 0.01
MAX_ATTEMPTS = 3
MIN_FIXED = 0.6      # a feature must bring most of the points it claims (its inliers) inside the threshold


class Evaluator:
    def __init__(self, scan: devmap.ScanSample, band: float, c2s_n: int) -> None:
        self.scan = scan
        self.band = band
        self.c2s_n = c2s_n
        self.n_evals = 0

    def __call__(self, tree: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        t0 = time.time()
        self.n_evals += 1
        body, log, flog = build(tree, params)
        if log["status"] != "OK" or body is None:
            failed = [n for n in log["nodes"] if n["status"] != "OK"]
            return {"ok": False, "why": failed[-1]["error"] if failed else log["status"], "log": log}
        cad = devmap.body_mesh(body)
        d = devmap.signed_s2c(self.scan.P, cad)
        _, dc = devmap.c2s(cad, self.scan.P, n=self.c2s_n)
        m = devmap.metrics(d, dc, self.band)
        return {"ok": True, "body": body, "cad": cad, "d": d, "dc": dc, "m": m, "log": log,
                "faces": log["final"]["faces"], "seconds": round(time.time() - t0, 2)}


def tree_profiles2d(tree: dict[str, Any], params: dict[str, Any]) -> list[tuple[str, Any, Any]]:
    """Named profiles used by XY-plane extrude nodes, as shapely polygons (for offset pockets)."""
    from shapely.geometry import Polygon
    from sketch2d import build_profile, faces_of
    from treexpr import Scope, bind_let
    consts = {k: v["value"] for k, v in (tree.get("constants") or {}).items()}
    S = Scope(params, consts)
    S.push(bind_let(S, tree.get("let")))
    out = []
    for n in tree["nodes"]:
        sk = n.get("sketch") or {}
        prof = sk.get("profile") or {}
        if n.get("op") != "extrude" or sk.get("plane", "XY") != "XY" or "ref" not in prof or "offset" in prof:
            continue
        face = faces_of(build_profile(dict(tree["profiles"][prof["ref"]]), S))[0]
        pts = []
        for e in face.outer_wire().edges():
            pts += [(q.X, q.Y) for q in (e.position_at(t) for t in np.linspace(0, 1, 60, endpoint=False))]
        ztop = n.get("z1", "0")
        if "CUT_OVERSHOOT" in consts:
            ztop = f"({ztop}) + CUT_OVERSHOOT"
        out.append((prof["ref"], Polygon(pts).buffer(0), ztop, n["id"]))
    return out


def cluster_key(c: dict[str, Any]) -> str:
    return f"{c['sign']:+d}@" + ",".join(f"{x:.0f}" for x in c["centroid"])


def base_key(h: dict[str, Any]) -> str:
    return f"{h['kind']}|{np.round(h['axis'], 2).tolist()}"


def rename(node: Any, mapping: dict[str, str]) -> Any:
    if isinstance(node, str):
        for old, new in mapping.items():
            if node == old:
                return new
            node = node.replace(old + "[", new + "[") if old + "[" in node else node
        return mapping.get(node, node)
    if isinstance(node, list):
        return [rename(x, mapping) for x in node]
    if isinstance(node, dict):
        return {k: rename(v, mapping) for k, v in node.items()}
    return node


def related_axes(a: list[float], b: list[float]) -> bool:
    """Pattern instances share the axis (up to sign), or mirror each other about a datum plane,
    or are rotated copies about the datum Z axis (same angle to Z: a polar pattern)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if abs(abs(a @ b) - 1) < 1e-3:
        return True
    for k in range(3):
        m = b.copy()
        m[k] = -m[k]
        if abs(abs(a @ m) - 1) < 1e-3:
            return True
    return abs(abs(a[2]) - abs(b[2])) < 1e-3 and abs(a[2]) < 0.999


def make_pattern(hs: list[dict[str, Any]], tag: str, noise: float) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge same-structure hypotheses into one repeated node with per-instance lists."""
    nm = Namer(tag)
    first = hs[0]
    mapping = {}
    def by_field(h: dict[str, Any]) -> dict[str, Any]:
        return {n.split("_", 1)[1]: v for n, v in h["params"].items()}
    fields = [by_field(h) for h in hs]
    for name, spec in first["params"].items():
        field = name.split("_", 1)[1]
        vals = [f[field]["value"] for f in fields]
        try:
            arr = np.asarray(vals, float)
        except ValueError:
            return None, {}              # instances differ in structure (e.g. step counts): no pattern
        tol = 0.01 if spec["unit"] == "-" else max(3 * noise, 0.05)
        spread = float(np.max(np.abs(arr - arr.mean(0)))) if arr.size else 0.0
        est = spec["estimator"] + f"; pattern of {len(hs)}"
        if spread <= tol and spec["unit"] != "-" and arr.ndim == 1:
            mapping[name] = nm.p(field, float(arr.mean()), spec["unit"], est + " (equal within noise)", spec["evidence"])
        else:
            mapping[name] = nm.p(field, arr.tolist(), spec["unit"], est + " (per instance, as measured)",
                                 spec["evidence"]) + "[i]"
    node = rename(copy.deepcopy(first["node"]), mapping)
    if "frame" in node:
        node["frame_each"] = node.pop("frame")
    node["repeat"] = {"i": list(range(len(hs)))}
    node["name"] = f"{first['node'].get('name', '')} x{len(hs)} (pattern)"
    return node, nm.params


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Staged deviation refine loop (builder self-check).")
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--params", type=Path, action="append", default=[])
    ap.add_argument("--scan", type=Path, required=True)
    ap.add_argument("--alignment", type=Path, required=True)
    ap.add_argument("--band", type=float, required=True, help="regime band (mm), e.g. p95 limit")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rounds", type=int, default=20)
    ap.add_argument("--samples", type=int, default=150_000)
    ap.add_argument("--c2s-samples", type=int, default=80_000)
    ap.add_argument("--max-cands", type=int, default=14)
    ap.add_argument("--min-gain", type=float, default=0.002, help="minimum relative J improvement")
    ap.add_argument("--min-area", type=float, default=1.0, help="minimum cluster area (mm^2)")
    ap.add_argument("--arbiter", choices=["auto", "agent"], default="auto")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)

    out = a.out
    (out / "cards").mkdir(parents=True, exist_ok=True)
    (out / "rounds").mkdir(parents=True, exist_ok=True)
    tree = json.loads(a.tree.read_text(encoding="utf-8"))
    params: dict[str, Any] = {}
    for p in a.params:
        params.update(load_params(p, {}))
    params.update(load_params(None, tree))
    prev_refine = out / "params_refine.json"
    refine_params: dict[str, Any] = {}

    scan = devmap.sample_scan(a.scan, a.alignment, a.samples, a.seed, cache=out / "scan_samples.npz")
    ev = Evaluator(scan, a.band, a.c2s_samples)
    eps = 3 * scan.spacing
    min_pts = max(40, int(a.min_area / scan.area_per_pt))
    thr = max(a.band, 4 * scan.noise)
    log: dict[str, Any] = {"band": a.band, "threshold_mm": thr, "noise": scan.noise, "spacing": scan.spacing,
                           "samples": a.samples, "rounds": [], "open_points": [], "cards": []}
    cur = ev(tree, params)
    if not cur["ok"]:
        print(f"base tree does not build: {cur['why']}", file=sys.stderr)
        return 2
    log["start"] = {"metrics": cur["m"], "faces": cur["faces"]}
    print(f"start J={cur['m']['J']:.4f} p95={cur['m']['s2c_p95']:.3f} faces={cur['faces']}")
    attempts: dict[str, int] = {}
    n_card = 0
    t_start = time.time()
    for rnd in range(1, a.rounds + 1):
        cl = devmap.clusters(scan.P, cur["d"], thr, eps, min_pts)
        prof2d = tree_profiles2d(tree, params)
        rec: dict[str, Any] = {"round": rnd, "before": cur["m"], "n_clusters": len(cl), "tried": []}
        accepted = None
        for c in cl:
            key = cluster_key(c)
            if attempts.get(key, 0) >= MAX_ATTEMPTS:
                continue
            tag = f"R{rnd:02d}"
            H = classify(scan.P[c["idx"]], scan.N[c["idx"]], c["sign"], scan.noise, scan.spacing, tag,
                         f"refine round {rnd} cluster {key} n={c['n']}", cur["cad"], prof2d)
            # neighbours of the same sign may be one body split by an earlier feature: classify the union
            lo, hi = np.array(c["bbox"][0]), np.array(c["bbox"][1])
            reach = max(2.0, 2.0 * float(np.linalg.norm(hi - lo)))
            nb = [c2 for c2 in cl if c2 is not c and c2["sign"] == c["sign"] and
                  np.all(np.array(c2["bbox"][0]) < hi + reach) and np.all(np.array(c2["bbox"][1]) > lo - reach)]
            if nb:
                U = np.concatenate([c["idx"]] + [c2["idx"] for c2 in nb])
                HU = classify(scan.P[U], scan.N[U], c["sign"], scan.noise, scan.spacing, tag + "u",
                              f"refine round {rnd} cluster {key} + {len(nb)} neighbours", cur["cad"], prof2d)
                for h in HU:
                    if h["node"] is not None:
                        h["union_idx"] = U
                        h["kind"] = h["kind"] + "+nb"
                        H.append(h)
                H.sort(key=lambda h: h["geom_score"])
            blends = [h for h in H if h["node"] is None]
            if blends:
                log.setdefault("blend_candidates", []).append({"cluster": key, "centroid": c["centroid"],
                                                               "note": blends[0]["note"]})
            H = [h for h in H if h["node"] is not None]
            if not H:
                attempts[key] = MAX_ATTEMPTS
                continue
            bases: list[str] = []
            for h in H:
                if base_key(h) not in bases:
                    bases.append(base_key(h))
            cands = [h for h in H if base_key(h) in bases[:4]][:a.max_cands]
            results = []
            for j, h in enumerate(cands):
                node = dict(h["node"], id=f"{tag}{string.ascii_lowercase[j % 26]}")
                ids = [n_["id"] for n_ in tree["nodes"]]
                at = ids.index(h["insert_after"]) + 1 if h.get("insert_after") in ids else len(ids)
                t2 = dict(tree, nodes=tree["nodes"][:at] + [node] + tree["nodes"][at:])
                p2 = {**params, **h["params"]}
                r = ev(t2, p2)
                item = {"cluster": key, "kind": h["kind"], "variant": h["variant"], "name": node.get("name"),
                        "ok": r["ok"]}
                if r["ok"]:
                    base_idx = h.get("union_idx", c["idx"])
                    mem = base_idx[h["members"]] if h.get("members") is not None and h["members"].sum() else base_idx
                    fixed = float((np.abs(r["d"][mem]) < thr).mean())
                    item.update(J=r["m"]["J"], p95=r["m"]["s2c_p95"], faces=r["faces"], fixed=round(fixed, 3))
                    if fixed >= MIN_FIXED:
                        results.append((r["m"]["J"], h, node, p2, t2, r))
                    else:
                        item["why"] = f"fixes only {fixed:.0%} of the points it claims (< {MIN_FIXED:.0%})"
                else:
                    item["why"] = str(r["why"])[:200]
                rec["tried"].append(item)
            results.sort(key=lambda x: x[0])
            # a candidate must fix a real part of its own cluster, not ride on a side effect
            expected = c["n"] / len(scan.P) * min(c["d_med"], 2.0) * min(1.0, max(
                (h_["members"].mean() for h_ in cands if h_.get("members") is not None), default=1.0))
            need = max(a.min_gain * cur["m"]["J"], 0.3 * expected)
            gain_ok = bool(results) and cur["m"]["J"] - results[0][0] >= need
            if not gain_ok:
                attempts[key] = attempts.get(key, 0) + 1
                if attempts[key] >= MAX_ATTEMPTS:
                    log["open_points"].append({"cluster": key, "sign": c["sign"], "n": c["n"],
                                               "centroid": c["centroid"], "bbox": c["bbox"],
                                               "why": "no hypothesis lowered J in 3 rounds"})
                continue
            best = results[0]
            if len(results) > 1 and results[1][1]["kind"] != best[1]["kind"] and \
                    results[1][0] - best[0] < CARD_MARGIN * best[0]:
                n_card += 1
                cpath = out / "cards" / f"{n_card:03d}.json"
                cands = [{"kind": r_[1]["kind"], "variant": r_[1]["variant"], "name": r_[2].get("name"),
                          "J": r_[0]} for r_ in results[:3]]
                old = json.loads(cpath.read_text()) if cpath.is_file() else None
                if old and old.get("cluster") == key and old.get("answer") is not None:
                    card = old                     # answered on an earlier run: apply it (deterministic rerun)
                    pick = card["candidates"][int(card["answer"])]
                    match = [r_ for r_ in results if r_[1]["kind"] == pick["kind"] and r_[1]["variant"] == pick["variant"]]
                    if match:
                        best = match[0]
                else:
                    card = {"card": n_card, "round": rnd, "cluster": key,
                            "question": "Two feature types explain this region almost equally well. "
                                        "Which is the design intent?",
                            "candidates": cands, "answer": None, "answered_by": None}
                    if a.arbiter == "auto":
                        card["answer"], card["answered_by"] = 0, "auto: lower J"
                    cpath.write_text(json.dumps(card, indent=2), encoding="utf-8")
                log["cards"].append(card)
                if card["answer"] is None:
                    log["stopped"] = f"waiting for card {n_card}: python3 cards.py answer {cpath} <index> --by <who>"
                    rec["accepted"] = None
                    log["rounds"].append(rec)
                    break
            # pattern step
            J_b, h_b, node_b, p_b, t_b, r_b = best
            sib = []
            for c2 in cl:
                if c2 is c or c2["sign"] != c["sign"]:
                    continue
                H2 = classify(scan.P[c2["idx"]], scan.N[c2["idx"]], c2["sign"], scan.noise, scan.spacing,
                              f"{tag}s{len(sib)}", f"refine round {rnd} cluster {cluster_key(c2)}", cur["cad"], prof2d)
                m2 = [h for h in H2 if h["kind"] == h_b["kind"] and h["variant"] == h_b["variant"]
                      and np.allclose(np.abs(h["size"]), np.abs(h_b["size"]), rtol=0.05, atol=4 * scan.noise)
                      and len(h["params"]) == len(h_b["params"]) and related_axes(h["axis"], h_b["axis"])]
                if m2:
                    sib.append((c2, m2[0]))
            pnode = None
            if sib:
                pnode, pparams = make_pattern([h_b] + [s[1] for s in sib], f"{tag}p", scan.noise)
            if pnode is not None:
                pnode["id"] = f"{tag}p"
                t3 = dict(tree, nodes=tree["nodes"] + [pnode])
                p3 = {**params, **pparams}
                r3 = ev(t3, p3)
                rec["tried"].append({"cluster": key, "kind": h_b["kind"] + " pattern", "n_instances": 1 + len(sib),
                                     "ok": r3["ok"], **({"J": r3["m"]["J"], "faces": r3["faces"]} if r3["ok"] else
                                                        {"why": str(r3["why"])[:200]})})
                if r3["ok"] and r3["m"]["J"] < J_b:
                    best = (r3["m"]["J"], h_b, pnode, p3, t3, r3)
                    refine_params.update(pparams)
                else:
                    refine_params.update(h_b["params"])
            else:
                refine_params.update(h_b["params"])
            accepted = best
            break
        if log.get("stopped"):
            break
        if accepted is None:
            rec["accepted"] = None
            log["rounds"].append(rec)
            print(f"round {rnd}: no hypothesis lowered J; stop")
            break
        J_new, h, node, p_new, t_new, r_new = accepted
        tree, params, cur = t_new, p_new, r_new
        rec["accepted"] = {"id": node["id"], "name": node.get("name"), "kind": h["kind"], "J": J_new,
                           "after": cur["m"], "faces": cur["faces"]}
        log["rounds"].append(rec)
        (out / "rounds" / f"{rnd:02d}_metrics.json").write_text(json.dumps(rec, indent=2, default=float))
        print(f"round {rnd}: + {node['id']} {node.get('name')}  J={J_new:.4f} p95={cur['m']['s2c_p95']:.3f} "
              f"faces={cur['faces']}  ({time.time() - t_start:.0f}s, {ev.n_evals} builds)")
        (out / "feature_tree.json").write_text(json.dumps(tree, indent=1), encoding="utf-8")
        prev_refine.write_text(json.dumps({"schema": "params_refine@v1", "params": refine_params}, indent=1))
        if cur["m"]["s2c_p95"] <= a.band and not devmap.clusters(scan.P, cur["d"], thr, eps, min_pts):
            print("band met and no clusters left")
            break
    log["final"] = {"metrics": cur["m"], "faces": cur["faces"], "nodes": len(tree["nodes"]),
                    "builds": ev.n_evals, "seconds": round(time.time() - t_start, 1)}
    (out / "feature_tree.json").write_text(json.dumps(tree, indent=1), encoding="utf-8")
    prev_refine.write_text(json.dumps({"schema": "params_refine@v1", "params": refine_params}, indent=1))
    (out / "refine_log.json").write_text(json.dumps(log, indent=1, default=float), encoding="utf-8")
    print(json.dumps(log["final"], indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
