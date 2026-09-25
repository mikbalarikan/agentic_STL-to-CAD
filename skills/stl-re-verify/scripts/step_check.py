#!/usr/bin/env python3
"""Hash-freeze, validity and surface census of the delivered STEP, with QA's own code.

Subcommands
  freeze   record sha256 of every STEP before QA starts         -> qa/hash_freeze.json
  verify   re-hash after QA; any change => hash_frozen.unchanged=false (fail closed)
  check    re-import each STEP; solids/shells/faces/edges, BRepCheck, closed shells, naked edges,
           volume/area/bbox, fine-tessellation health, surface-type census (count + area share)

Provenance:
  - hash freeze before/after QA: M02 qa_report.json checks[0] and checks[21]
    (analysis/golden/M02-02-03.md §7) -- (heuristic, n=1: M02)
  - BRep counts + BRepCheck + volume/area/bbox: golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q10_solid_tess_tier1.py:24-44
  - naked-edge count via edge->face ancestors: B02 6_RE_work/qa/q01_solid.py
  - tessellation health (watertight, winding, euler, components, degenerate, dVolume): q10:47-58
  - surface census: NEW CODE (OCP BRepAdaptor_Surface). REPORTED, NOT GATED (QUESTIONS.md Q3,
    run-contract.md §9); inputs to CHK-PATCHWORK reading (analysis/SYNTHESIS.md D10).
Deterministic: no randomness; the only wall-clock value is the provenance field `created`.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, load_mesh, merge_into_gate, read_json, sha256_file, write_json  # noqa: E402

TOOL = "step_check.py"


def check_step(step: str, tol: float, ang: float) -> dict[str, Any]:
    from build123d import export_stl, import_step
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.GeomAbs import (GeomAbs_BezierSurface, GeomAbs_BSplineSurface, GeomAbs_Cone, GeomAbs_Cylinder,
                             GeomAbs_OffsetSurface, GeomAbs_Plane, GeomAbs_Sphere, GeomAbs_SurfaceOfExtrusion,
                             GeomAbs_SurfaceOfRevolution, GeomAbs_Torus)
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer

    shape = import_step(step)
    tds = shape.wrapped
    cnt: dict[str, int] = {}
    for nm, tp in (("solid", TopAbs_SOLID), ("shell", TopAbs_SHELL), ("face", TopAbs_FACE),
                   ("edge", TopAbs_EDGE), ("vertex", TopAbs_VERTEX)):
        e, n = TopExp_Explorer(tds, tp), 0
        while e.More():
            n += 1
            e.Next()
        cnt[nm] = n
    uses: dict[Any, int] = {}
    for fc in shape.faces():
        for e in fc.edges():
            if BRep_Tool.Degenerated_s(e.wrapped):
                continue
            seam = BRep_Tool.IsClosed_s(e.wrapped, fc.wrapped)   # seam edge: used twice by one face
            uses[e] = uses.get(e, 0) + (2 if seam else 1)       # build123d Shape hash/eq = IsSame
    naked = sum(1 for n in uses.values() if n < 2)
    closed = [bool(BRep_Tool.IsClosed_s(sh.wrapped)) for sh in shape.shells()]
    names = {GeomAbs_Plane: "plane", GeomAbs_Cylinder: "cylinder", GeomAbs_Cone: "cone",
             GeomAbs_Sphere: "sphere", GeomAbs_Torus: "torus", GeomAbs_BSplineSurface: "bspline",
             GeomAbs_BezierSurface: "bezier", GeomAbs_SurfaceOfRevolution: "revolution",
             GeomAbs_SurfaceOfExtrusion: "extrusion", GeomAbs_OffsetSurface: "offset"}
    census: dict[str, dict[str, float]] = {}
    for f in shape.faces():
        t = names.get(BRepAdaptor_Surface(f.wrapped).GetType(), "other")
        c = census.setdefault(t, {"count": 0, "area_mm2": 0.0})
        c["count"] += 1
        c["area_mm2"] += f.area
    tot = sum(c["area_mm2"] for c in census.values()) or 1.0
    analytic = sum(c["area_mm2"] for k, c in census.items() if k in ("plane", "cylinder", "cone", "sphere", "torus"))
    bb = shape.bounding_box()
    tmp = Path(tempfile.mkdtemp(prefix="qa_fine_")) / "fine.stl"
    export_stl(shape, str(tmp), tolerance=tol, angular_tolerance=ang)
    m = load_mesh(tmp)
    return {
        "validity": {"counts": cnt, "brepcheck_valid": bool(BRepCheck_Analyzer(tds).IsValid()),
                     "shells_closed": closed, "naked_edges": naked, "volume_mm3": shape.volume,
                     "area_mm2": shape.area, "bbox": [*bb.min, *bb.max],
                     "single_valid_closed_solid": bool(cnt["solid"] == 1 and BRepCheck_Analyzer(tds).IsValid()
                                                       and all(closed) and naked == 0 and shape.volume > 0)},
        "tessellation": {"tolerance": tol, "angular_tolerance": ang, "tris": len(m.faces),
                         "watertight": bool(m.is_watertight), "winding": bool(m.is_winding_consistent),
                         "euler": int(m.euler_number), "components": int(m.body_count),
                         "degenerate_faces": int((m.area_faces < 1e-9).sum()), "volume_mm3": float(m.volume),
                         "volume_vs_brep_mm3": float(m.volume - shape.volume)},
        "surface_census": {"faces": cnt["face"], "by_type": census, "analytic_area_share": analytic / tot,
                           "gated": False, "note": "reported, not gated (QUESTIONS.md Q3)"},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--step", nargs="+", required=True)
    f.add_argument("--out", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--freeze", required=True)
    v.add_argument("--gate")
    c = sub.add_parser("check")
    c.add_argument("--step", nargs="+", required=True)
    c.add_argument("--tolerance", type=float, default=0.005)
    c.add_argument("--angular-tolerance", type=float, default=0.05)
    c.add_argument("--out", required=True)
    c.add_argument("--gate")
    a = ap.parse_args(argv)

    if a.cmd == "freeze":
        rec = {**header("hash_freeze", TOOL, a.step, None), "before": {s: sha256_file(s) for s in a.step}}
        write_json(a.out, rec)
        print("frozen:", rec["before"])
        return 0
    if a.cmd == "verify":
        rec = read_json(a.freeze)
        after = {s: sha256_file(s) if Path(s).is_file() else None for s in rec["before"]}
        rec["after"] = after
        rec["unchanged"] = after == rec["before"]
        write_json(a.freeze, rec)
        if a.gate:
            merge_into_gate(a.gate, "hash_frozen", {"before": rec["before"], "after": after,
                                                    "unchanged": rec["unchanged"]})
        print("hash unchanged" if rec["unchanged"] else "HASH CHANGED DURING QA -> QA invalid, re-run")
        return 0 if rec["unchanged"] else 2
    res = {s: check_step(s, a.tolerance, a.angular_tolerance) for s in a.step}
    out = {**header("step_check", TOOL, a.step, None), "steps": res,
           "all_single_valid_closed_solid": all(r["validity"]["single_valid_closed_solid"] for r in res.values())}
    write_json(a.out, out)
    if a.gate:
        merge_into_gate(a.gate, "validity", {s: {**r["validity"], "tessellation": r["tessellation"]} for s, r in res.items()})
        merge_into_gate(a.gate, "surface_census", {s: r["surface_census"] for s, r in res.items()})
    for s, r in res.items():
        vv, sc = r["validity"], r["surface_census"]
        print(f"{Path(s).name}: solids {vv['counts']['solid']} valid {vv['brepcheck_valid']} closed {vv['shells_closed']} "
              f"naked {vv['naked_edges']} faces {vv['counts']['face']} vol {vv['volume_mm3']:.3f} | analytic area "
              f"{100 * sc['analytic_area_share']:.1f}% | {sorted((k, c['count']) for k, c in sc['by_type'].items())}")
    return 0 if out["all_single_valid_closed_solid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
