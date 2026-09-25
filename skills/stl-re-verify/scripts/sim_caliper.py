#!/usr/bin/env python3
"""Tier-1: re-measure every caliper/operator dimension on the FINAL STEP with QA's own code,
by a simulated two-parallel-jaw caliper on sections of a fine tessellation or an analytic
B-rep face query. No build parameter is read back.

Provenance: QA's own copy lifted from
golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q10_solid_tess_tier1.py
  - densify() 0.02 mm resample, jaws() support-function width over jaw azimuth, step 0.05 deg (q10:61-73)
  - zsec()/meridian() planar and half-plane sections (q10:75-84)
  - outer envelope R(theta) (0.25 deg step, +-0.3 deg window) then jaws, for lobed ODs (q10:89-99)
  - innermost loop = bore / pocket (q10:102-104, 113-115)
  - depth as a difference of medians on a meridian (q10:106-112)
  - fine tessellation 0.005 mm / 0.05 rad (q10:52)
Analytic cylinder/plane queries are NEW CODE (OCP BRepAdaptor_Surface), used when a feature is a
single analytic face (P03 used "feature queries", analysis/golden/OOM-P03.md §7 G2).
The measure skill keeps its own copy for CHK-ACHIEVABLE; QA must not reuse builder helpers
(analysis/baseline/facet-film-transferable.md T18).

Band: |CAD - caliper| <= tier1_abs_mm from the declared regime (RE_SPEC regime: ±0.15 mm,
baseline/oomwoo-re-pipeline/RE_SPEC.md:170). Grey zone flag (facet-film T15): a pass whose margin
to the band is smaller than the reading's uncertainty (photo-transcribed readings: ±0.1 mm
effective, analysis/golden/OOM-B02.md §4) is flagged for a human, not silently passed.
"""
from __future__ import annotations

import argparse
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (RegimeError, header, load_matrix, merge_into_gate, normalise_bands, read_json,  # noqa: E402
                     select, step_to_mesh, write_json)

TOOL = "sim_caliper.py"


def densify(p: np.ndarray, ds: float = 0.02) -> np.ndarray:
    o = []
    for i in range(len(p) - 1):
        d = np.linalg.norm(p[i + 1] - p[i])
        n = max(int(d / ds), 1)
        for k in range(n):
            o.append(p[i] + (p[i + 1] - p[i]) * (k / n))
    o.append(p[-1])
    return np.array(o)


def jaws(pts2d: np.ndarray, step: float = 0.05) -> np.ndarray:
    """Support-function width over jaw azimuth: what two parallel jaws actually read (q10:67-72)."""
    a = np.radians(np.arange(0, 180, step))
    v = np.stack([np.cos(a), np.sin(a)], 1)
    q = pts2d @ v.T
    return np.c_[np.degrees(a), q.max(0) - q.min(0)]


def plane_basis(normal: np.ndarray) -> np.ndarray:
    n = normal / np.linalg.norm(normal)
    ref = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = ref - (ref @ n) * n
    u /= np.linalg.norm(u)
    return np.stack([u, np.cross(n, u), n])


def section_loops(m: Any, origin: list[float], normal: list[float]) -> list[np.ndarray]:
    s = m.section(plane_origin=origin, plane_normal=normal)
    if s is None:
        return []
    return [np.asarray(s.vertices[e.points]) for e in s.entities]


def meridian_pts(m: Any, th_deg: float) -> np.ndarray:
    a = math.radians(th_deg)
    u = np.array([math.cos(a), math.sin(a), 0.0])
    n = np.array([-math.sin(a), math.cos(a), 0.0])
    loops = section_loops(m, [0, 0, 0], n.tolist())
    P = np.vstack([densify(L) for L in loops])
    return np.c_[P @ u, np.zeros(len(P)), P[:, 2]]    # pseudo-3D: x = signed radial s, z = z


def measure_jaw(m: Any, spec: dict[str, Any]) -> dict[str, Any]:
    o = np.asarray(spec["plane"]["origin"], float)
    n = np.asarray(spec["plane"]["normal"], float)
    B = plane_basis(n)
    loops = [densify(L) for L in section_loops(m, o.tolist(), n.tolist())]
    if not loops:
        return {"value": None, "error": "empty section"}
    if spec.get("loop", "all") == "innermost":
        loops = [min(loops, key=lambda p: np.hypot(*(p - o)[:, :2].T).max())]
    elif spec.get("loop") == "outermost":
        loops = [max(loops, key=lambda p: np.hypot(*(p - o)[:, :2].T).max())]
    P = np.vstack(loops)
    if "region" in spec:
        P = P[select(spec["region"], P)]
    Q = (P - o) @ B[:2].T
    if spec.get("envelope"):
        rr, tt = np.hypot(*Q.T), np.degrees(np.arctan2(Q[:, 1], Q[:, 0]))
        TH = np.arange(-180, 180, spec.get("envelope_step_deg", 0.25))
        hw = spec.get("envelope_half_window_deg", 0.3)
        R = np.full(len(TH), np.nan)
        for i, t in enumerate(TH):
            w_ = np.abs(((tt - t + 180) % 360) - 180) < hw
            if w_.any():
                R[i] = rr[w_].max()
        ok = np.isfinite(R)
        Q = np.c_[R[ok] * np.cos(np.radians(TH[ok])), R[ok] * np.sin(np.radians(TH[ok]))]
    if "dir" in spec:                                   # jaws closing along an explicit 3D direction
        dvec = np.asarray(spec["dir"], float)
        dvec = dvec - (dvec @ B[2]) * B[2]
        dvec /= np.linalg.norm(dvec)
        q = (P - o) @ dvec
        return {"value": float(q.max() - q.min()), "reduce": "along dir"}
    w = jaws(Q, spec.get("step_deg", 0.05))
    red = spec.get("reduce", "max")
    val = float(w[:, 1].max() if red == "max" else w[:, 1].min())
    return {"value": val, "reduce": red, "window": [float(w[:, 1].min()), float(w[:, 1].max())]}


def measure_bore(m: Any, spec: dict[str, Any]) -> dict[str, Any]:
    o = np.asarray(spec["plane"]["origin"], float)
    n = np.asarray(spec["plane"]["normal"], float)
    B = plane_basis(n)
    loops = [densify(L) for L in section_loops(m, o.tolist(), n.tolist())]
    L = min(loops, key=lambda p: np.hypot(*((p - o) @ B[:2].T).T).max())
    Q = (L - o) @ B[:2].T
    r = np.hypot(*Q.T)
    A = np.c_[2 * Q, np.ones(len(Q))]
    sol, *_ = np.linalg.lstsq(A, (Q ** 2).sum(1), rcond=None)
    fit_d = 2 * math.sqrt(sol[2] + sol[0] ** 2 + sol[1] ** 2)
    vals = {"2rmax": float(2 * r.max()), "2rmin": float(2 * r.min()), "fit": float(fit_d)}
    return {"value": vals[spec.get("stat", "2rmax")], **{f"d_{k}": v for k, v in vals.items()}}


def measure_height(m: Any, spec: dict[str, Any]) -> dict[str, Any]:
    P = meridian_pts(m, spec.get("meridian_deg", 0.0))
    za = float(np.median(P[select(spec["a"], P), 2]))
    zb = float(np.median(P[select(spec["b"], P), 2]))
    return {"value": zb - za, "z_a": za, "z_b": zb, "note": "meridian: x = signed radial coordinate"}


def analytic_faces(step: str) -> list[dict[str, Any]]:
    from build123d import import_step
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane

    out = []
    for f in import_step(step).faces():
        ad = BRepAdaptor_Surface(f.wrapped)
        t = ad.GetType()
        if t == GeomAbs_Cylinder:
            c = ad.Cylinder()
            loc, d = c.Axis().Location(), c.Axis().Direction()
            out.append({"type": "cylinder", "radius": c.Radius(), "p": [loc.X(), loc.Y(), loc.Z()],
                        "dir": [d.X(), d.Y(), d.Z()], "area": f.area})
        elif t == GeomAbs_Plane:
            pl = ad.Plane()
            loc, d = pl.Location(), pl.Axis().Direction()
            nrm = np.array([d.X(), d.Y(), d.Z()])
            out.append({"type": "plane", "normal": nrm.tolist(), "offset": float(nrm @ [loc.X(), loc.Y(), loc.Z()]),
                        "area": f.area})
    return out


def measure_cylinder(faces: list[dict[str, Any]], spec: dict[str, Any], T: np.ndarray) -> dict[str, Any]:
    p0 = np.asarray(spec["axis_point"], float)
    d0 = np.asarray(spec["axis_dir"], float)
    d0 /= np.linalg.norm(d0)
    lo, hi = spec["radius_window"]
    hits = []
    for f in faces:
        if f["type"] != "cylinder" or not (lo <= f["radius"] <= hi):
            continue
        p = T[:3, :3] @ np.asarray(f["p"]) + T[:3, 3]
        d = T[:3, :3] @ np.asarray(f["dir"])
        if abs(d @ d0) < math.cos(math.radians(spec.get("axis_tol_deg", 0.5))):
            continue
        off = (p - p0) - ((p - p0) @ d0) * d0
        if np.linalg.norm(off) <= spec.get("axis_tol_mm", 0.1):
            hits.append(2 * f["radius"])
    if not hits:
        return {"value": None, "error": "no matching cylindrical face"}
    u = sorted(set(round(h, 9) for h in hits))
    pick = spec.get("pick", "only")
    val = u[0] if pick == "min" else u[-1] if pick == "max" else (u[0] if len(u) == 1 else None)
    return {"value": val, "diameters_found": u, **({"error": "ambiguous: several diameters"} if val is None else {})}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--step", required=True, help="frozen FINAL STEP (datum frame preferred)")
    ap.add_argument("--step-matrix", help="optional 4x4 bringing the STEP into the datum frame")
    ap.add_argument("--dims", required=True, help="dims spec JSON: {dims:[...], total_requested:N}")
    ap.add_argument("--regime", required=True, help="qa/regime.json; canonical flat bands "
                    "{p95_mm,max_mm,tier1_abs_mm,interface_max_mm} (run-contract §12). "
                    "bands.tier1_abs_mm is the Tier-1 band. Required: a missing regime never "
                    "falls back to a default.")
    ap.add_argument("--tolerance", type=float, default=0.005)
    ap.add_argument("--angular-tolerance", type=float, default=0.05)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gate", help="merge into gate.json under 'tier1'")
    a = ap.parse_args(argv)

    spec = read_json(a.dims)
    regime = read_json(a.regime)
    try:
        bands = normalise_bands(regime.get("bands", {}))
    except RegimeError as e:
        print(f"ERROR: regime refused: {e}", file=sys.stderr)
        return 2
    band = bands["tier1_abs_mm"]
    tmp = Path(tempfile.mkdtemp(prefix="qa_t1_")) / "fine.stl"
    m = step_to_mesh(a.step, tmp, a.tolerance, a.angular_tolerance)
    T = load_matrix(a.step_matrix) if a.step_matrix else np.eye(4)
    m.apply_transform(T)
    faces = None
    rows: dict[str, Any] = {}
    worst = 0.0
    for d in spec["dims"]:
        meth = d["method"]
        kind = meth["kind"]
        if kind == "jaw":
            r = measure_jaw(m, meth)
        elif kind == "bore":
            r = measure_bore(m, meth)
        elif kind == "height":
            r = measure_height(m, meth)
        elif kind == "analytic_cylinder":
            faces = faces if faces is not None else analytic_faces(a.step)
            r = measure_cylinder(faces, meth, T)
        else:
            raise KeyError(f"{d['id']}: unknown method kind {kind}")
        cal = d.get("caliper")
        cad = r.get("value")
        row: dict[str, Any] = {"name": d.get("name", ""), "caliper": cal, "cad": cad,
                               "source": d.get("source", "caliper"), "gated": bool(d.get("gated", cal is not None)),
                               "uncertainty_mm": d.get("uncertainty_mm"), "method": kind, "detail": r}
        if cal is not None and cad is not None:
            row["delta"] = cad - cal
            if row["gated"] and band is not None:
                row["pass"] = abs(row["delta"]) <= band
                worst = max(worst, abs(row["delta"]))
                unc = d.get("uncertainty_mm")
                row["grey_zone"] = bool(row["pass"] and unc is not None and band - abs(row["delta"]) < unc)
            else:
                row["pass"] = None
        else:
            row["delta"], row["pass"] = None, None
            if row["gated"] and cal is not None and cad is None:
                # review V4: a gated dim that cannot be measured on the STEP is a finding, never a
                # silent pass -- verdict.py turns this into a blocker, not an absent/allowed gap.
                row["unmeasurable"] = True
        rows[d["id"]] = row
    gated = [k for k, v in rows.items() if v["gated"] and v["caliper"] is not None]
    out = {**header("tier1", TOOL, [a.step, a.dims] + ([a.regime] if a.regime else []), None),
           "band_abs_mm": band, "band_source": regime.get("source"),
           "tessellation": {"tolerance": a.tolerance, "angular_tolerance": a.angular_tolerance},
           "dims": rows, "worst_gated_abs_delta": worst if gated else None,
           "coverage": {"gated": len(gated), "requested_total": spec.get("total_requested"),
                        "absent": spec.get("absent", [])},
           "all_pass": all(rows[k]["pass"] for k in gated) if gated and band is not None else None}
    write_json(a.out, out)
    if a.gate:
        merge_into_gate(a.gate, "tier1", out)
    for k, v in rows.items():
        cad = "None" if v["cad"] is None else "%.4f" % v["cad"]
        dl = "-" if v["delta"] is None else "%+.4f" % v["delta"]
        print(f"{k:6s} {v['name'][:30]:30s} caliper {v['caliper']} CAD {cad} delta {dl} pass {v['pass']}")
    print(f"Tier-1 coverage {len(gated)}/{spec.get('total_requested')} gated; worst {out['worst_gated_abs_delta']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
