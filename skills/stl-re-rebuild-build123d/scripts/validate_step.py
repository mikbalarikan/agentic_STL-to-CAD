#!/usr/bin/env python3
"""validate_step.py - single-valid-closed-solid check of a STEP after re-import (D12).

PROVENANCE
  * Re-import + solid/shell counts + BRepCheck + closed shell + volume > 0 + raise on
    failure: lifted from golden-examples/M02-02-03_watertight-design-intent/model.py:66-101
    (topo_counts, main self-check). Changed: function returning a dict, bbox/area added,
    no parameters written, exit code instead of RuntimeError.
  * Naked-edge count (an edge used by only one face = open shell): lifted from
    golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q01_solid.py:61-70. Changed: the
    golden used TopTools_IndexedDataMapOfShapeListOfShape, which newer OCP releases no
    longer export under that name (build123d 0.13 / OCP drift), so edge uses are counted
    per face with TopExp_Explorer. A seam edge is used twice by its own face, so it is not
    naked; degenerate edges (cone apex, sphere pole) are skipped.
  * Optional self-intersection check (BOPAlgo_CheckerSI): from
    golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q02b_selfint.py. Changed: run
    single-threaded for determinism (the golden used SetRunParallel(True)).
  * Surface census: ./face_stats.py (reported, not gated; QUESTIONS.md A/Q3).

PASS RULE (every golden delivered exactly this; analysis/SYNTHESIS.md D12)
  solids == 1 and shells == 1 and every shell closed and naked_edges == 0 and
  BRepCheck valid and volume > 0 (and no self-intersection when --selfint is given).
  Anything else -> exit 2 = ABORT the export (do not deliver a broken solid).

Blind spots: validity says nothing about design intent or scan fit; a valid solid can
still be patchwork (see census) or the wrong part.

CLI
  validate_step.py PART.step [--json out.json] [--selfint] [--no-census]
Exit codes: 0 pass, 1 usage/IO error, 2 validity failed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, r6, write_json  # noqa: E402
from face_stats import surface_census, unique_subshapes  # noqa: E402

from OCP.BRep import BRep_Tool  # noqa: E402
from OCP.BRepBndLib import BRepBndLib  # noqa: E402
from OCP.BRepCheck import BRepCheck_Analyzer  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.Bnd import Bnd_Box  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopoDS import TopoDS, TopoDS_Shape  # noqa: E402

_TO_SHELL = getattr(TopoDS, "Shell_s", None) or getattr(TopoDS, "Shell")
_TO_EDGE = getattr(TopoDS, "Edge_s", None) or getattr(TopoDS, "Edge")


def naked_edge_count(shape: TopoDS_Shape) -> int:
    """Edges used by fewer than two face-occurrences (open boundary). Seams count twice."""
    uses: dict[int, int] = {}
    degenerate: set[int] = set()
    for face in unique_subshapes(shape, TopAbs_FACE):
        ex = TopExp_Explorer(face, TopAbs_EDGE)
        while ex.More():
            e = ex.Current()
            k = hash(e)
            uses[k] = uses.get(k, 0) + 1
            if BRep_Tool.Degenerated_s(_TO_EDGE(e)):
                degenerate.add(k)
            ex.Next()
    return sum(1 for k, n in uses.items() if n < 2 and k not in degenerate)


def self_intersections(shape: TopoDS_Shape) -> int:
    """Number of self-interference pairs found by BOPAlgo_CheckerSI (0 = clean)."""
    from OCP.BOPAlgo import BOPAlgo_CheckerSI

    chk = BOPAlgo_CheckerSI()
    chk.AddArgument(shape)  # AddArgument avoids TopTools_ListOfShape (renamed in newer OCP)
    chk.SetRunParallel(False)
    chk.Perform()
    return 1 if chk.HasErrors() else 0


def validate_shape(shape: TopoDS_Shape, selfint: bool = False, census: bool = True) -> dict[str, Any]:
    """Validity report for an OCP shape (usually a re-imported STEP)."""
    res: dict[str, Any] = {}
    res["solids"] = len(unique_subshapes(shape, TopAbs_SOLID))
    shells = unique_subshapes(shape, TopAbs_SHELL)
    res["shells"] = len(shells)
    res["faces"] = len(unique_subshapes(shape, TopAbs_FACE))
    res["edges"] = len(unique_subshapes(shape, TopAbs_EDGE))
    res["vertices"] = len(unique_subshapes(shape, TopAbs_VERTEX))
    res["valid"] = bool(BRepCheck_Analyzer(shape).IsValid())
    res["shell_closed"] = [bool(BRep_Tool.IsClosed_s(_TO_SHELL(s))) for s in shells]
    res["naked_edges"] = naked_edge_count(shape)
    res["closed"] = bool(shells) and all(res["shell_closed"]) and res["naked_edges"] == 0
    vp = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, vp)
    res["volume_mm3"] = r6(vp.Mass())
    sp = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, sp)
    res["area_mm2"] = r6(sp.Mass())
    bb = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, bb, False, False)
    lo, hi = bb.CornerMin(), bb.CornerMax()  # Bnd_Box.Get() does not bind in newer OCP
    xm, ym, zm, xM, yM, zM = lo.X(), lo.Y(), lo.Z(), hi.X(), hi.Y(), hi.Z()
    res["bbox"] = {"min": [r6(xm), r6(ym), r6(zm)], "max": [r6(xM), r6(yM), r6(zM)],
                   "size": [r6(xM - xm), r6(yM - ym), r6(zM - zm)]}
    if selfint:
        res["self_intersections"] = self_intersections(shape)
    if census:
        c = surface_census(shape)
        res["surface_types"] = c["by_type"]
        res["analytic_area_share"] = c["analytic_area_share"]
        res["ruled_like_faces"] = c["ruled_like_faces"]
    failures = []
    if res["solids"] != 1:
        failures.append(f"solids={res['solids']} (need 1)")
    if res["shells"] != 1:
        failures.append(f"shells={res['shells']} (need 1)")
    if not res["valid"]:
        failures.append("BRepCheck invalid")
    if not res["closed"]:
        failures.append(f"not closed (naked_edges={res['naked_edges']})")
    if res["volume_mm3"] <= 0:
        failures.append(f"volume={res['volume_mm3']} (need > 0)")
    if selfint and res.get("self_intersections"):
        failures.append("self-intersections found")
    res["pass"] = not failures
    res["failures"] = failures
    return res


def validate_step(path: Path, selfint: bool = False, census: bool = True) -> dict[str, Any]:
    from build123d import import_step

    return validate_shape(import_step(str(path)).wrapped, selfint=selfint, census=census)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Re-import a STEP and check single valid closed solid.")
    ap.add_argument("step", type=Path)
    ap.add_argument("--json", type=Path, help="write the report JSON here")
    ap.add_argument("--selfint", action="store_true", help="also run BOPAlgo_CheckerSI (slow)")
    ap.add_argument("--no-census", action="store_true", help="skip the surface census")
    a = ap.parse_args(argv)
    if not a.step.is_file():
        print(f"no such file: {a.step}", file=sys.stderr)
        return 1
    res: dict[str, Any] = header("validate_step", "validate_step.py", [a.step])
    res["step"] = str(a.step)
    res["validity"] = validate_step(a.step, selfint=a.selfint, census=not a.no_census)
    if a.json:
        write_json(a.json, res)
    print(json.dumps(res, indent=2, sort_keys=True))
    if not res["validity"]["pass"]:
        print("ABORT: " + "; ".join(res["validity"]["failures"]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
