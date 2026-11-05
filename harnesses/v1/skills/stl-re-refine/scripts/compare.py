#!/usr/bin/env python3
"""compare.py - score a refine result against a reference STEP on the same scan samples.

Builder self-check (CHK-INDEP): one sampling, one metric definition for both models, so the
comparison is like-for-like. The official grade is still stl-re-verify.

  python3 compare.py --tree refine/feature_tree.json --params measure/params.json \
      --params refine/params_refine.json --scan input/scan.stl --alignment intake/alignment.json \
      --ref-step <v0 datum STEP> --band 0.30 --out refine/compare.json [--samples refine/scan_samples.npz]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "stl-re-build" / "scripts"))

import devmap  # noqa: E402
from build_tree import build, load_params  # noqa: E402


def score(body, scan, band):
    cad = devmap.body_mesh(body)
    d = devmap.signed_s2c(scan.P, cad)
    _, dc = devmap.c2s(cad, scan.P, n=100_000)
    m = devmap.metrics(d, dc, band)
    m.update(faces=len(body.faces()), solids=len(body.solids()), volume=float(body.volume))
    return m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--params", type=Path, action="append", default=[])
    ap.add_argument("--scan", type=Path, required=True)
    ap.add_argument("--alignment", type=Path, required=True)
    ap.add_argument("--ref-step", type=Path, required=True)
    ap.add_argument("--band", type=float, required=True)
    ap.add_argument("--samples", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    from build123d import import_step
    tree = json.loads(a.tree.read_text())
    params = {}
    for p in a.params:
        d = json.loads(p.read_text())
        params.update(d["params"] if "params" in d else d)
    params.update(load_params(None, tree))
    body, log, _ = build(tree, params)
    if body is None or log["status"] != "OK":
        print("tree does not build", log["status"], file=sys.stderr)
        return 2
    scan = devmap.sample_scan(a.scan, a.alignment, 150_000, 0, cache=a.samples)
    res = {"refine": score(body, scan, a.band), "reference": score(import_step(str(a.ref_step)), scan, a.band),
           "nodes": len(tree["nodes"]), "reference_step": str(a.ref_step)}
    a.out.write_text(json.dumps(res, indent=1))
    keys = ["s2c_p50", "s2c_p95", "s2c_max", "s2c_within_band", "c2s_p95", "J", "faces"]
    print(f"{'':10s}" + "".join(f"{k:>16s}" for k in keys))
    for n in ("refine", "reference"):
        print(f"{n:10s}" + "".join(f"{res[n][k]:16.4f}" for k in keys))
    return 0


if __name__ == "__main__":
    sys.exit(main())
