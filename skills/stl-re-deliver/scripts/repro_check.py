#!/usr/bin/env python3
"""Rebuild build/model.py twice in fresh processes and compare the geometry with the delivered STEP.

Provenance:
- Output schema follows golden-examples/M02-02-03_watertight-design-intent/reproducibility_report.json
  (original/rebuild volume, bbox, abs deltas, geometry_measurements_identical)
  -- heuristic, n=1: M02 (analysis/SYNTHESIS.md E11).
- Two separate processes, compare a geometric digest rather than the raw hash because STEP headers
  carry a timestamp: facet-film T32 (analysis/baseline/facet-film-transferable.md, T32).
- Env pins recorded (T32 "document env pins").

The rebuild runs in a scratch copy of the run (build/ without STEP/STL outputs, measure/,
intake/ without meshes), so the delivered build/ is never touched. Default tolerance is 0
(exact equality), because the M02 golden rerun showed zero deltas
(reproducibility_report.json: volume_abs_delta_mm3 0.0, bbox_max_abs_delta_mm 0.0).
A non-zero --tol-mm is a recorded parameter, not a threshold, and is written to repro.json.

Exit codes: 0 reproducible; 1 not reproducible (repro.json still written); 2 refused.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DeliverError, fail, header, preflight, sha256_file, write_json  # noqa: E402

OUTPUT_SUFFIXES = {".step", ".stp", ".stl"}


def measure_step(path: Path) -> dict[str, Any]:
    """Geometric digest of one STEP: solids, faces, surface census, volume, area, bbox."""
    from build123d import import_step  # heavy import only when needed

    shape = import_step(str(path))
    bb = shape.bounding_box()
    census: dict[str, int] = {}
    for f in shape.faces():
        k = str(getattr(f.geom_type, "name", f.geom_type))
        census[k] = census.get(k, 0) + 1
    valid = shape.is_valid() if callable(getattr(shape, "is_valid", None)) else bool(getattr(shape, "is_valid", False))
    return {
        "solids": len(shape.solids()),
        "faces": len(shape.faces()),
        "valid": bool(valid),
        "surface_census": dict(sorted(census.items())),
        "volume_mm3": float(shape.volume),
        "area_mm2": float(shape.area),
        "bbox_min": [float(bb.min.X), float(bb.min.Y), float(bb.min.Z)],
        "bbox_max": [float(bb.max.X), float(bb.max.Y), float(bb.max.Z)],
    }


def scratch_copy(run: Path, dst: Path) -> None:
    """Copy what model.py may read: build/ (no outputs), measure/, intake/ (no meshes)."""
    for sub, skip in (("build", OUTPUT_SUFFIXES), ("measure", set()), ("intake", {".stl", ".ply", ".obj"})):
        src = run / sub
        if not src.is_dir():
            continue
        for f in sorted(src.rglob("*")):
            if f.is_dir() or f.suffix.lower() in skip or "__pycache__" in f.parts:
                continue
            t = dst / sub / f.relative_to(src)
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, t)
    (dst / "build").mkdir(parents=True, exist_ok=True)


def rebuild_once(run: Path, cmd: list[str], timeout_s: int) -> tuple[Path, dict[str, Any]]:
    tmp = Path(tempfile.mkdtemp(prefix="stl-re-repro-"))
    scratch_copy(run, tmp)
    env = dict(os.environ, PYTHONHASHSEED="0", STL_RE_RUN=str(tmp),
               SOURCE_DATE_EPOCH=os.environ.get("SOURCE_DATE_EPOCH", "0"))
    proc = subprocess.run(cmd, cwd=tmp / "build", env=env, capture_output=True, text=True, timeout=timeout_s)
    info = {"returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
    return tmp, info


def compare(orig: dict[str, Any], new: dict[str, Any], tol: float) -> dict[str, Any]:
    dv = abs(orig["volume_mm3"] - new["volume_mm3"])
    db = max(abs(a - b) for a, b in zip(orig["bbox_min"] + orig["bbox_max"], new["bbox_min"] + new["bbox_max"]))
    size = lambda m: [hi - lo for lo, hi in zip(m["bbox_min"], m["bbox_max"])]  # noqa: E731
    same_topo = (orig["solids"] == new["solids"] and orig["faces"] == new["faces"]
                 and orig["surface_census"] == new["surface_census"])
    return {
        "original_volume_mm3": orig["volume_mm3"], "rebuild_volume_mm3": new["volume_mm3"],
        "volume_abs_delta_mm3": dv,
        "original_bbox_mm": size(orig), "rebuild_bbox_mm": size(new), "bbox_max_abs_delta_mm": db,
        "faces_equal": orig["faces"] == new["faces"], "solids_equal": orig["solids"] == new["solids"],
        "surface_census_equal": orig["surface_census"] == new["surface_census"],
        "geometry_measurements_identical": bool(same_topo and dv <= tol and db <= tol),
    }


def environment() -> dict[str, str]:
    env = {"python": platform.python_version(), "platform": platform.platform(terse=True)}
    for mod in ("build123d", "OCP", "numpy"):
        try:
            m = __import__(mod)
            env[mod] = str(getattr(m, "__version__", "unknown"))
        except ImportError:
            env[mod] = "not installed"
    return env


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--cmd", nargs="+", default=None,
                    help="rebuild command run in <scratch>/build (default: python model.py)")
    ap.add_argument("--runs", type=int, default=2, help="fresh processes (default 2, facet-film T32)")
    ap.add_argument("--tol-mm", type=float, default=0.0, help="recorded parameter; default exact (M02)")
    ap.add_argument("--timeout-s", type=int, default=1800)
    ap.add_argument("--keep-scratch", action="store_true")
    a = ap.parse_args()
    run = a.run.resolve()
    try:
        preflight(run)
    except DeliverError as exc:
        fail(str(exc))
    delivered = sorted(p for p in (run / "build").glob("*.step"))
    if not (run / "build" / "model.py").is_file() or not delivered:
        fail("build/model.py and at least one build/*.step are required")
    cmd = a.cmd or [sys.executable, "model.py"]
    originals = {p.name: measure_step(p) for p in delivered}

    runs: list[dict[str, Any]] = []
    per_file: dict[str, list[dict[str, Any]]] = {n: [] for n in originals}
    ok = True
    for i in range(a.runs):
        tmp, info = rebuild_once(run, cmd, a.timeout_s)
        info["run"] = i + 1
        produced = {p.name: p for p in (tmp / "build").glob("*.step")}
        info["produced"] = sorted(produced)
        if info["returncode"] != 0:
            ok = False
        for name, orig in originals.items():
            if name not in produced:
                ok = False
                per_file[name].append({"run": i + 1, "error": "not produced by the rebuild"})
                continue
            c = compare(orig, measure_step(produced[name]), a.tol_mm)
            c["run"] = i + 1
            c["raw_sha256_equal"] = sha256_file(produced[name]) == sha256_file(run / "build" / name)
            ok = ok and c["geometry_measurements_identical"]
            per_file[name].append(c)
        runs.append(info)
        if not a.keep_scratch:
            shutil.rmtree(tmp, ignore_errors=True)

    files = []
    for name, cs in per_file.items():
        good = [c for c in cs if "error" not in c]
        worst = max(good, key=lambda c: (c["volume_abs_delta_mm3"], c["bbox_max_abs_delta_mm"])) if good else {}
        files.append({"file": name, **{k: v for k, v in worst.items() if k != "run"},
                      "geometry_measurements_identical": bool(good) and len(good) == len(cs)
                      and all(c["geometry_measurements_identical"] for c in good),
                      "raw_sha256_equal": bool(good) and all(c["raw_sha256_equal"] for c in good),
                      "runs": cs, "original": originals[name]})
    doc = header("repro", "repro_check.py", run, [run / "build" / "model.py", run / "measure" / "params.json", *delivered])
    doc.update({
        "method": f"{a.runs} fresh subprocess rebuild(s) of build/model.py in a scratch copy; STEP re-imported; "
                  "solids, faces, surface census, volume, bbox compared (raw hash reported, not required)",
        "command": cmd, "tolerance_mm": a.tol_mm, "environment": environment(),
        "reproducible": bool(ok), "runs": runs, "files": files,
    })
    write_json(run / "deliver" / "repro.json", doc)
    print(f"wrote {run / 'deliver' / 'repro.json'}  reproducible={ok}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
