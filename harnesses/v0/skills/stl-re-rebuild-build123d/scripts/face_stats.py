#!/usr/bin/env python3
"""face_stats.py - surface-type census of a STEP (CHK-PATCHWORK self-census).

PROVENANCE
  NEW CODE in this form. The golden records counted surface types by grepping STEP
  entities or reading an NX import log (see `OD-H12-Pump.log`, `analysis/golden/OOM-B02.md`
  section 6, and `analysis/golden/M02-02-03.md` section 6 for their actual face-type
  breakdowns; not restated here since they are per-part results, not a threshold).
  The W01 Tier-0 script `6_RE_work/surftypes.py` named in baseline/oomwoo-re-pipeline/TRACKER.md:32
  is not in the repo, so this is written from the RE_SPEC Tier-0 wording
  (baseline/oomwoo-re-pipeline/RE_SPEC.md:265-270: "dominant area on analytic surfaces
  (planes/cylinders/cones/tori/revolutions), zero ruled-loft patchwork").

WHAT IT REPORTS (owner decision QUESTIONS.md A/Q3: REPORTED, NOT GATED)
  faces, total area, per surface type {count, area_mm2, area_share}, analytic area share,
  B-spline / Bezier face count, and `ruled_like` = B-spline/Bezier faces with degree 1 in
  U or V (what `loft(ruled=True)` produces; the W01 failure). Optionally compares the
  face count with the plan's expected range (reported as in/out of range, never a gate).

PLANAR-FACET PATCHWORK IS NOT WHAT THIS CENSUS FLAGS
  A patchwork of planar facets (stacked prisms, a polygonal profile in place of a curve) is
  INVISIBLE to `analytic_area_share` and `ruled_like_faces`: every facet is a plane, so it
  counts as analytic, and it is not a B-spline, so `ruled_like_faces` stays 0. M02's polygonal
  involute (`Wire.make_polygon`, a fixed sample count per flank) produced a large number of
  planar facets with analytic_area_share == 1.0 and ruled_like_faces == 0
  (analysis/golden/M02-02-03.md section 6 has the actual counts) - a cold read of this census
  alone would call that clean. `plane_face_count` and `plane_face_median_area_mm2` are
  reported (never gated, no
  invented threshold) so a face count far above the plan, together with a small median plane
  area, can be inspected by eye instead of missed entirely.

Analytic set used for `analytic_area_share`: plane, cylinder, cone, sphere, torus,
surface of revolution (RE_SPEC.md:268 list; sphere added as a quadric). Surfaces of
extrusion (e.g. B02's extruded spline outline) are reported separately, not as analytic.

Blind spots: a clean census does not prove design intent (a correct face count can hide a
wrong feature); a B-spline face can be a legitimate fillet corner (DRM screw has 5).
Deterministic: OCP topology maps are ordered; no randomness.

CLI
  face_stats.py PART.step [--json out.json] [--expect-faces MIN MAX]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, r6, write_json  # noqa: E402

from OCP.BRepAdaptor import BRepAdaptor_Surface  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.GeomAbs import GeomAbs_SurfaceType as ST  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from OCP.TopAbs import TopAbs_FACE  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopoDS import TopoDS, TopoDS_Shape  # noqa: E402

TYPE_NAMES: dict[Any, str] = {
    ST.GeomAbs_Plane: "plane",
    ST.GeomAbs_Cylinder: "cylinder",
    ST.GeomAbs_Cone: "cone",
    ST.GeomAbs_Sphere: "sphere",
    ST.GeomAbs_Torus: "torus",
    ST.GeomAbs_SurfaceOfRevolution: "revolution",
    ST.GeomAbs_SurfaceOfExtrusion: "extrusion",
    ST.GeomAbs_BSplineSurface: "bspline",
    ST.GeomAbs_BezierSurface: "bezier",
    ST.GeomAbs_OffsetSurface: "offset",
    ST.GeomAbs_OtherSurface: "other",
}
# OCP drift: older OCP exposes static downcasts as TopoDS.Face_s, newer as TopoDS.Face.
_TO_FACE = getattr(TopoDS, "Face_s", None) or getattr(TopoDS, "Face")

ANALYTIC = ("plane", "cylinder", "cone", "sphere", "torus", "revolution")


def unique_subshapes(shape: TopoDS_Shape, kind: Any) -> list[TopoDS_Shape]:
    """Unique sub-shapes in explorer order (dedupe by hash, as build123d does).

    OCP renamed TopTools_IndexedMapOfShape between releases (build123d version drift),
    so this avoids the map classes entirely."""
    out: dict[int, TopoDS_Shape] = {}
    ex = TopExp_Explorer(shape, kind)
    while ex.More():
        cur = ex.Current()
        out.setdefault(hash(cur), cur)
        ex.Next()
    return list(out.values())


def surface_census(shape: TopoDS_Shape) -> dict[str, Any]:
    """Census of unique faces of an OCP shape: counts and area share per surface type."""
    faces = unique_subshapes(shape, TopAbs_FACE)
    by_type: dict[str, dict[str, float]] = {}
    areas_by_type: dict[str, list[float]] = {}
    total = 0.0
    ruled_like = 0
    for f in faces:
        face = _TO_FACE(f)
        ad = BRepAdaptor_Surface(face)
        st = ad.GetType()
        name = TYPE_NAMES.get(st, "other")
        if st == ST.GeomAbs_BSplineSurface:
            bs = ad.BSpline()
            if bs.UDegree() == 1 or bs.VDegree() == 1:
                ruled_like += 1
        elif st == ST.GeomAbs_BezierSurface:
            bz = ad.Bezier()
            if bz.UDegree() == 1 or bz.VDegree() == 1:
                ruled_like += 1
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        a = props.Mass()
        total += a
        d = by_type.setdefault(name, {"count": 0, "area_mm2": 0.0})
        d["count"] += 1
        d["area_mm2"] += a
        areas_by_type.setdefault(name, []).append(a)
    out_types: dict[str, dict[str, float]] = {}
    for name in sorted(by_type):
        d = by_type[name]
        out_types[name] = {
            "count": int(d["count"]),
            "area_mm2": r6(d["area_mm2"]),
            "area_share": r6(d["area_mm2"] / total) if total > 0 else 0.0,
        }
    analytic = sum(by_type[n]["area_mm2"] for n in by_type if n in ANALYTIC)
    plane_areas = areas_by_type.get("plane", [])
    return {
        "faces": len(faces),
        "total_area_mm2": r6(total),
        "by_type": out_types,
        "analytic_area_share": r6(analytic / total) if total > 0 else 0.0,
        "analytic_set": list(ANALYTIC),
        "freeform_faces": int(sum(by_type[n]["count"] for n in ("bspline", "bezier") if n in by_type)),
        "ruled_like_faces": ruled_like,
        # Reported only (owner decision Q3), no threshold: a patchwork of planar facets
        # (stacked prisms, a polygonal curve) is all-plane and non-ruled, so it does not move
        # analytic_area_share or ruled_like_faces at all. A high plane_face_count together
        # with a small plane_face_median_area_mm2, against the plan's expected face count,
        # is the signal to inspect by eye. Evidence case: M02's polygonal involute (see
        # analysis/golden/M02-02-03.md section 6 for the actual face/facet counts).
        "plane_face_count": int(len(plane_areas)),
        "plane_face_median_area_mm2": r6(statistics.median(plane_areas)) if plane_areas else None,
    }


def load_step(path: Path) -> TopoDS_Shape:
    from build123d import import_step

    return import_step(str(path)).wrapped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Surface-type census of a STEP (CHK-PATCHWORK, reported not gated).")
    ap.add_argument("step", type=Path)
    ap.add_argument("--json", type=Path, help="write the census JSON here")
    ap.add_argument("--expect-faces", type=int, nargs=2, metavar=("MIN", "MAX"),
                    help="expected face-count range from build/MODELING_PLAN.md (reported only)")
    a = ap.parse_args(argv)
    if not a.step.is_file():
        print(f"no such file: {a.step}", file=sys.stderr)
        return 1
    census = surface_census(load_step(a.step))
    res: dict[str, Any] = header("face_stats", "face_stats.py", [a.step])
    res["census"] = census
    res["check"] = "CHK-PATCHWORK"
    res["gated"] = False  # QUESTIONS.md A/Q3
    if a.expect_faces:
        lo, hi = a.expect_faces
        res["expected_faces"] = [lo, hi]
        res["faces_in_expected_range"] = bool(lo <= census["faces"] <= hi)
    notes = []
    if census["ruled_like_faces"]:
        notes.append("ruled-like B-spline faces present: find the loft that made them; ruled lofts of "
                     "scan slices are forbidden (RE_SPEC.md:258-273, W01)")
    res["notes"] = notes
    if a.json:
        write_json(a.json, res)
    print(json.dumps(res, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
