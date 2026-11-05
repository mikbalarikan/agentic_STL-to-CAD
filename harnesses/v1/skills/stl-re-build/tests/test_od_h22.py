#!/usr/bin/env python3
"""M1 acceptance: the OD-H22 valve built from examples/od_h22/feature_tree.json must equal the
STEP that v0's hand-written model.py produced (harnesses/v0/examples/OD-H22_3-way-valve/run/build/).

Checks: build status OK with no unused params and no tree literals; 1 valid solid; same face
count; the symmetric-difference volume of the two solids is below 1e-3 mm^3 in the datum frame.

  python3 tests/test_od_h22.py [--out DIR]
Exit 0 = pass.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "scripts"))
REPO = next(p for p in SKILL.parents if (p / "harnesses").is_dir())
V0RUN = REPO / "harnesses/v0/examples/OD-H22_3-way-valve/run"

from build_tree import build, load_params  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    from build123d import export_step, import_step

    tree = json.loads((SKILL / "examples/od_h22/feature_tree.json").read_text(encoding="utf-8"))
    params = load_params(V0RUN / "measure/params.json", tree)
    body, log, flog = build(tree, params)
    fails = []
    if log["status"] != "OK":
        fails.append(f"build status {log['status']}: {[n for n in log['nodes'] if n['status'] != 'OK']}")
    if log.get("unused_params"):
        fails.append(f"unused params {log['unused_params']}")
    if log.get("literals"):
        fails.append(f"tree literals {log['literals']}")
    if any(e["status"] != "OK" for e in flog.entries):
        fails.append("a fillet is not OK")
    if body is not None:
        ref = import_step(str(V0RUN / "build/OD-H22_3-way-valve_datum.step"))
        out = a.out or Path(tempfile.mkdtemp(prefix="v1_odh22_"))
        out.mkdir(parents=True, exist_ok=True)
        export_step(body, str(out / "OD-H22_3-way-valve_datum.step"))
        got = import_step(str(out / "OD-H22_3-way-valve_datum.step"))
        d1, d2 = (ref - got).volume, (got - ref).volume
        print(f"v0 vol {ref.volume:.4f} faces {len(ref.faces())} | v1 vol {got.volume:.4f} faces "
              f"{len(got.faces())} | v0-v1 {d1:.6f} v1-v0 {d2:.6f} mm3")
        if len(got.solids()) != 1 or not got.is_valid:
            fails.append("not one valid solid")
        if len(got.faces()) != len(ref.faces()):
            fails.append(f"faces {len(got.faces())} != v0 {len(ref.faces())}")
        if d1 > 1e-3 or d2 > 1e-3:
            fails.append(f"symmetric difference {d1:.6f} / {d2:.6f} mm3")
    for f in fails:
        print("FAIL", f)
    print("PASS od_h22 tree == v0 model.py" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
