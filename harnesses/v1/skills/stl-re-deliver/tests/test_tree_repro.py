#!/usr/bin/env python3
"""v1: the repro check rebuilds a FEATURE TREE (not a model.py) in fresh processes, and gets the
delivered STEPs back exactly. It uses the OD-H22 tree (stl-re-build examples) with v0's params
and alignment. Exit 0 = pass.

  python3 tests/test_tree_repro.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
SKILLS = HERE.parents[1]
REPO = next(p for p in HERE.parents if (p / "harnesses").is_dir())
V0RUN = REPO / "harnesses/v0/examples/OD-H22_3-way-valve/run"
sys.path.insert(0, str(SCRIPTS))

from _common import design_sources, part_name, tree_rebuild_command  # noqa: E402
from repro_check import compare, measure_step, rebuild_once  # noqa: E402


def main() -> int:
    run = Path(tempfile.mkdtemp(prefix="v1_tree_repro_"))
    fails = []
    try:
        (run / "build").mkdir()
        (run / "measure").mkdir()
        (run / "intake").mkdir()
        shutil.copy(SKILLS / "stl-re-build/examples/od_h22/feature_tree.json", run / "build/feature_tree.json")
        shutil.copy(V0RUN / "measure/params.json", run / "measure/params.json")
        shutil.copy(V0RUN / "intake/alignment.json", run / "intake/alignment.json")
        part = "OD-H22_3-way-valve"
        # deliver the STEPs once, the way the build stage does
        cmd0 = [sys.executable, str(SKILLS / "stl-re-build/scripts/build_tree.py"), "--tree", "build/feature_tree.json",
                "--params", "measure/params.json", "--alignment", "intake/alignment.json", "--out", "build",
                "--part", part]
        p = subprocess.run(cmd0, cwd=run, capture_output=True, text=True)
        if p.returncode != 0:
            print(p.stderr[-2000:])
            return 1
        src = design_sources(run)
        ok_src = [x.name for x in src] == ["feature_tree.json", "params.json"]
        print(("PASS" if ok_src else "FAIL"), "design_sources picks the feature tree:", [str(x.relative_to(run)) for x in src])
        fails += [] if ok_src else ["design_sources"]
        ok_part = part_name(run) == part
        print(("PASS" if ok_part else "FAIL"), "part name from build/<part>_datum.step:", part_name(run))
        fails += [] if ok_part else ["part_name"]
        cmd = tree_rebuild_command(run, sys.executable)
        delivered = sorted((run / "build").glob("*.step"))
        originals = {q.name: measure_step(q) for q in delivered}
        for i in range(2):
            tmp, info = rebuild_once(run, cmd, 1800, "run")
            produced = {q.name: q for q in (tmp / "build").glob("*.step")}
            same = info["returncode"] == 0 and set(produced) == set(originals) and all(
                compare(originals[n], measure_step(produced[n]), 0.0)["geometry_measurements_identical"]
                for n in originals)
            print(("PASS" if same else "FAIL"), f"fresh-process rebuild {i + 1}: {sorted(produced)} identical={same}")
            if not same:
                fails.append(f"rebuild {i + 1}")
                print(info.get("stderr_tail", "")[-1500:])
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        shutil.rmtree(run, ignore_errors=True)
    print("\n" + ("all passed" if not fails else f"{len(fails)} failed: {fails}"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
