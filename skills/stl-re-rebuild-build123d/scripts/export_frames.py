#!/usr/bin/env python3
"""export_frames.py - dual-frame export: datum-frame STEP, scan-frame STEP, CAD STL,
re-import of both STEPs, abort unless one valid closed solid, build/export_check.json.

PROVENANCE
  * inverse alignment -> OCP gp_Trsf with the rotation re-orthonormalised by SVD, then
    body.moved(Location(trsf)): lifted from
    golden-examples/dreame_brush-caps/report/source/frames.py:8-21
    (stl_frame_location, export_frames). Changed: reads the run-contract
    intake/alignment.json (any path) instead of `<name>_alignment.json` in the cwd; no
    hard-coded output directory (the golden call site wrote to a fixed Windows path,
    build_screw.py:101).
  * abort unless 1 valid solid, export both frames, re-import both STEPs, JSON report of
    solids/valid/closed/faces/volume/area/bbox: lifted from
    golden-examples/OD-H12_delonghi-dedica-pump/report/src/export_final.py:14-50.
    Changed: T read from alignment.json (the golden loaded a cwd-relative `T1.npy`),
    closedness uses naked edges + shell flags (./validate_step.py), surface census and
    fillet log added (run-contract.md section 5).
  * SVD re-orthonormalisation is required: OCP rejects a near-orthonormal rotation
    ("transform_shape rejects near-orthonormal", export_frames.py comment in OD; the
    inverse of a float 4x4 is only near-orthonormal).

ADDED GUARDS (new code)
  * det(R) < 0 (a reflection) -> abort: a mirrored part would pass every validity check.
  * alignment scale_factor != 1.0 -> abort: how a CHK-SCALE uniform scale is carried in
    matrix_4x4 is not specified by the run contract (open question in SKILL.md).
  * round trip: the re-imported scan-frame STEP is moved back to the datum frame and its
    bbox compared with the datum-frame bbox (reported as `roundtrip_bbox_max_abs_mm`; not a gate).

STL tessellation defaults (tolerance 0.003 mm, angular 0.05 rad) are the values the DRM
golden used (frames.py:19); OD used 0.01 / 0.1 (export_final.py:36). They are parameters.

LIBRARY USE (end of build/model.py)
  from export_frames import export_frames
  check = export_frames(body, Path("intake/alignment.json"), Path("build"), "part",
                        fillets_json=Path("build/fillets.json"))

CLI (re-export an existing datum-frame STEP)
  export_frames.py --shape build/<part>_datum.step --alignment intake/alignment.json \
                   --out build --part <part> [--fillets build/fillets.json] [--datum-stl]
Exit codes: 0 ok, 1 usage/IO error, 2 abort (invalid solid, reflection, scale, re-import).
Deterministic: no randomness; JSON sorted; `created` is provenance only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, r6, write_json  # noqa: E402
from validate_step import validate_shape  # noqa: E402


class ExportAbort(RuntimeError):
    """Raised when the export must not be delivered."""


def load_alignment(path: Path) -> tuple[np.ndarray, float]:
    d = json.loads(path.read_text(encoding="utf-8"))
    if "matrix_4x4" not in d:
        raise ExportAbort(f"{path}: no matrix_4x4 (run-contract.md section 3)")
    T = np.asarray(d["matrix_4x4"], dtype=float)
    if T.shape != (4, 4):
        raise ExportAbort(f"{path}: matrix_4x4 has shape {T.shape}")
    return T, float(d.get("scale_factor", 1.0))


def scan_frame_trsf(T: np.ndarray) -> tuple[Any, dict[str, Any]]:
    """gp_Trsf for datum -> raw scan frame (inverse of T), rotation re-orthonormalised."""
    from OCP.gp import gp_Trsf

    Ti = np.linalg.inv(T)
    U, S, Vt = np.linalg.svd(Ti[:3, :3])
    R = U @ Vt
    det = float(np.linalg.det(R))
    info = {"singular_values": [r6(s) for s in S], "det": r6(det),
            "orthonormalisation_max_abs": float(f"{np.abs(R - Ti[:3, :3]).max():.3e}")}
    if det < 0:
        raise ExportAbort(f"alignment rotation is a reflection (det={det:.6f}); fix the datum, do not export")
    t = Ti[:3, 3]
    tr = gp_Trsf()
    tr.SetValues(*[float(v) for v in np.c_[R, t].ravel()])
    return tr, info


def _roundtrip_bbox_err(scan_shape: Any, trsf: Any, datum_bbox: dict[str, list[float]]) -> float:
    """Move the re-imported scan-frame shape back by the inverse trsf; max |bbox delta| (mm)."""
    from build123d import Location

    bb = scan_shape.moved(Location(trsf.Inverted())).bounding_box()
    lo = np.array([bb.min.X, bb.min.Y, bb.min.Z])
    hi = np.array([bb.max.X, bb.max.Y, bb.max.Z])
    return float(max(np.abs(lo - np.array(datum_bbox["min"])).max(), np.abs(hi - np.array(datum_bbox["max"])).max()))


def export_frames(body: Any, alignment: Path, out_dir: Path, part: str,
                  fillets_json: Path | None = None, model_py: Path | None = None,
                  stl_tol: float = 0.003, stl_ang: float = 0.05, datum_stl: bool = False,
                  selfint: bool = False) -> dict[str, Any]:
    """Export both frames + CAD STL, re-import, validate, write export_check.json.
    Raises ExportAbort (after writing export_check.json when possible) on failure."""
    from build123d import Location, export_step, export_stl, import_step

    out_dir.mkdir(parents=True, exist_ok=True)
    n_sol = len(body.solids())
    v = getattr(body, "is_valid", None)
    valid = bool(v() if callable(v) else v)
    if n_sol != 1 or not valid:
        raise ExportAbort(f"built body: expected 1 valid solid, got {n_sol} (valid={valid}); nothing exported")
    T, scale = load_alignment(alignment)
    if scale != 1.0:
        raise ExportAbort(f"scale_factor={scale}: scan-frame export with a scale is not specified "
                          "by the run contract; ask the orchestrator (open question)")
    trsf, tinfo = scan_frame_trsf(T)
    scan_body = body.moved(Location(trsf))

    paths = {"datum": out_dir / f"{part}_datum.step", "scan": out_dir / f"{part}.step"}
    export_step(body, str(paths["datum"]))
    export_step(scan_body, str(paths["scan"]))
    stl_scan = out_dir / f"{part}_cad.stl"
    export_stl(scan_body, str(stl_scan), tolerance=stl_tol, angular_tolerance=stl_ang)
    if datum_stl:
        export_stl(body, str(out_dir / f"{part}_datum.stl"), tolerance=stl_tol, angular_tolerance=stl_ang)

    fillets: list[dict[str, Any]] = []
    if fillets_json is not None and fillets_json.is_file():
        fillets = json.loads(fillets_json.read_text(encoding="utf-8")).get("fillets", [])

    inputs = [alignment] + [p for p in (fillets_json, model_py) if p is not None]
    res: dict[str, Any] = header("export_check", "export_frames.py", inputs)
    res.update({"part": part, "alignment_matrix_4x4": [[r6(x) for x in row] for row in T.tolist()],
                "inverse_rotation": tinfo, "stl": {"path": stl_scan.name, "frame": "scan",
                                                   "tolerance": stl_tol, "angular_tolerance": stl_ang}})
    back: dict[str, Any] = {}
    for key, p in paths.items():
        shp = import_step(str(p))
        back[key] = shp
        rep = validate_shape(shp.wrapped, selfint=selfint, census=True)
        rep["step"] = p.name
        rep["fillets"] = fillets
        res[key] = rep
    res["frames_agree"] = {
        "faces_equal": res["datum"]["faces"] == res["scan"]["faces"],
        "volume_rel_diff": float(f"{abs(res['datum']['volume_mm3'] - res['scan']['volume_mm3']) / max(abs(res['datum']['volume_mm3']), 1e-12):.3e}"),
        "roundtrip_bbox_max_abs_mm": float(f"{_roundtrip_bbox_err(back['scan'], trsf, res['datum']['bbox']):.3e}"),
        "note": "scan-frame STEP moved back to the datum frame; bbox compared; report only",
    }
    fails = [f"{k}: {'; '.join(res[k]['failures'])}" for k in paths if not res[k]["pass"]]
    res["pass"] = not fails
    res["failures"] = fails
    write_json(out_dir / "export_check.json", res)
    if fails:
        raise ExportAbort("re-import failed: " + " | ".join(fails))
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dual-frame STEP export + re-import check (run-contract section 5).")
    ap.add_argument("--shape", type=Path, required=True, help="datum-frame STEP of the built part")
    ap.add_argument("--alignment", type=Path, required=True, help="intake/alignment.json (raw scan -> datum)")
    ap.add_argument("--out", type=Path, required=True, help="output folder (build/)")
    ap.add_argument("--part", required=True, help="part name: writes <part>_datum.step, <part>.step, <part>_cad.stl")
    ap.add_argument("--fillets", type=Path, help="build/fillets.json from fillet_log.py")
    ap.add_argument("--model", type=Path, help="build/model.py (hashed into inputs)")
    ap.add_argument("--stl-tol", type=float, default=0.003, help="STL linear tolerance (DRM golden: 0.003)")
    ap.add_argument("--stl-ang", type=float, default=0.05, help="STL angular tolerance (DRM golden: 0.05)")
    ap.add_argument("--datum-stl", action="store_true", help="also write <part>_datum.stl")
    ap.add_argument("--selfint", action="store_true", help="also run BOPAlgo_CheckerSI on both frames")
    a = ap.parse_args(argv)
    for p in (a.shape, a.alignment):
        if not p.is_file():
            print(f"no such file: {p}", file=sys.stderr)
            return 1
    from build123d import import_step

    body = import_step(str(a.shape))
    try:
        res = export_frames(body, a.alignment, a.out, a.part, a.fillets, a.model,
                            a.stl_tol, a.stl_ang, a.datum_stl, a.selfint)
    except ExportAbort as ex:
        print(f"ABORT: {ex}", file=sys.stderr)
        return 2
    short = {k: {kk: res[k][kk] for kk in ("solids", "valid", "closed", "faces", "volume_mm3", "bbox")}
             for k in ("datum", "scan")}
    print(json.dumps({"pass": res["pass"], "frames_agree": res["frames_agree"], **short}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
