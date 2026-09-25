"""Curve-network facet sheets: NX `Through Curve Mesh` (2 primary + 2 cross) in OCP.

Recipe N of the facet-film method. Learned from record R3 (GMT-Master II 126713GRNR,
NX session `c4dbc89f48b4`, 2026-09-04): `Through Curve Mesh(17)`, 4 parent splines,
41.851 mm2, mirrored to all four lugs. Use it for a facet whose two *transverse ends*
are themselves curved, where the recipe-C 2-section ruled sheet can only put a straight
chord (see SKILL.md Stage 2 recipe N and `references/e2e-126713-method.md`).

Public API
    lug_facet_network()                 -> 4 boundary B-splines with exact corners (demo data)
    coons_patch(p0, p1, c0, c1)         -> Geom_BSplineSurface, INTERPOLATES all four curves
    filling_face(edges, interior=())    -> N-sided BRepFill_Filling face (APPROXIMATES)
    ruled_between(p0, p1)               -> the recipe-C candidate, for the trigger measurement
    developability_grid(G)              -> same angle-defect K as ruled_sheet.developability
    flatten_paths(surf, area)           -> Stage-3 path A (ruled strip) vs path B (LSCM)

Run as a script for the self-test (needs OCP + numpy + scipy; build123d only to route
`ruled_between` through `ruled_sheet.ruled_face`)::

    python curve_network_sheet.py            # self-test, prints gate pass/fail
    python curve_network_sheet.py out.json   # additionally writes the results JSON

The reference numbers in `EXPECTED` were produced on the VPS venv with OCP 7.9.3 and are
byte-reproducible there (`tasks/NXLEARN-126713/run/tcm_prototype_results.json`,
two consecutive runs gave an identical file). The self-test compares against them at 1e-4
relative tolerance so a patch-level OCC change does not trip it.

CAUTION on the discrete K gate: the angle-defect estimator's MAX is not grid-invariant
(`k_grid_sensitivity` below: 5.70e-2 at 41x7 vs 9.13e-2 at 41x41 on the SAME surface).
Always report the (n, m) it was measured on; prefer analytic curvature for a hard gate.
"""

from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

# --------------------------------------------------------------------------- OCP imports
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from OCP.BRepFill import BRepFill, BRepFill_Filling
from OCP.BRepGProp import BRepGProp
from OCP.GeomAbs import GeomAbs_C0
from OCP.GeomAPI import GeomAPI_Interpolate, GeomAPI_ProjectPointOnSurf
from OCP.GeomFill import GeomFill_BSplineCurves, GeomFill_CoonsStyle
from OCP.gp import gp_Pnt
from OCP.GProp import GProp_GProps
from OCP.TColgp import TColgp_HArray1OfPnt

HERE = os.path.dirname(os.path.abspath(__file__))
TOL_BOUNDARY_MM = 1e-4
GATE_K_MEAN = 1.5e-2
GATE_K_MAX = 6.5e-2
GATE_STRAIN_PCT = 0.4
GATE_AREA_ERR_PCT = 0.4

# ------------------------------------------------- the skill's own ruled_face, if importable
try:
    sys.path.insert(0, HERE)
    import ruled_sheet as RS  # noqa: E402

    HAVE_RULED_SHEET = True
except Exception:  # pragma: no cover - the module must also run standalone
    RS = None
    HAVE_RULED_SHEET = False


# ------------------------------------------------------------------------------ curve helpers
def interp_bspline(pts: np.ndarray):
    """C2 interpolating B-spline through pts (n,3). Deterministic."""
    arr = TColgp_HArray1OfPnt(1, len(pts))
    for i, p in enumerate(pts, start=1):
        arr.SetValue(i, gp_Pnt(float(p[0]), float(p[1]), float(p[2])))
    ip = GeomAPI_Interpolate(arr, False, 1e-9)
    ip.Perform()
    return ip.Curve()


def curve_pts(c, n: int) -> np.ndarray:
    a, b = c.FirstParameter(), c.LastParameter()
    return np.array([[(p := c.Value(float(t))).X(), p.Y(), p.Z()] for t in np.linspace(a, b, n)])


def edge_of(c):
    return BRepBuilderAPI_MakeEdge(c).Edge()


def edge_pts(e, n: int) -> np.ndarray:
    ac = BRepAdaptor_Curve(e)
    a, b = ac.FirstParameter(), ac.LastParameter()
    return np.array([[(p := ac.Value(float(t))).X(), p.Y(), p.Z()] for t in np.linspace(a, b, n)])


def face_area(f) -> float:
    p = GProp_GProps()
    BRepGProp.SurfaceProperties_s(f, p)
    return float(p.Mass())


def polyline_len(P: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum())


# ------------------------------------------------------------------- the synthetic lug facet
def lug_facet_network(scale_z: float = 0.80):
    """Four boundary curves shaped like the 126713 lug-flank/case-shoulder facet.

    Corners are constructed FIRST and reused verbatim by both curves that meet there, so
    corner coincidence is exact (0.0 mm) rather than merely tight. That is the port of the
    maintainer's own construction: `Spline(17)`'s parents are `Spline(14),Spline(15)`, i.e.
    the cross curve was bridged FROM the primaries' endpoints.

    Nominal size ~15 x 5 mm; doubly curved; both transverse ends genuinely curved. The real
    facet measured 15.70 / 9.92 mm primaries, 8.54 / 2.95 mm crosses, 41.85 mm2.
    """
    # corners: (u,v) = (0,0) (1,0) (0,1) (1,1)
    c00 = np.array([0.0, 0.0, 0.0])
    c10 = np.array([15.0, 1.2, -2.4 * scale_z])
    c01 = np.array([0.6, 5.0, 1.1 * scale_z])
    c11 = np.array([14.6, 5.6, -0.9 * scale_z])

    def bend(a, b, mids):
        """Interpolating spline a -> b through interior offsets `mids` (fraction, offset)."""
        pts = [a]
        for f, off in mids:
            base = a + (b - a) * f
            pts.append(base + np.array(off, dtype=float))
        pts.append(b)
        return interp_bspline(np.array(pts))

    # primary 0 (v=0): long, sags in +z then drops -- the "inner" primary
    p0 = bend(
        c00,
        c10,
        [
            (0.25, (0.0, 0.35, 0.95 * scale_z)),
            (0.50, (0.0, 0.55, 1.15 * scale_z)),
            (0.75, (0.0, 0.40, 0.30 * scale_z)),
        ],
    )
    # primary 1 (v=1): long, different curvature -> the two are NOT parallel
    p1 = bend(
        c01,
        c11,
        [
            (0.25, (0.0, -0.10, 1.85 * scale_z)),
            (0.50, (0.0, -0.25, 2.30 * scale_z)),
            (0.75, (0.0, -0.05, 1.20 * scale_z)),
        ],
    )
    # cross 0 (u=0): curved transverse end (this is what a ruled sheet cannot make)
    c0 = bend(
        c00, c01, [(0.35, (-0.55, 0.0, 0.30 * scale_z)), (0.70, (-0.60, 0.0, 0.45 * scale_z))]
    )
    # cross 1 (u=1): curved transverse end, opposite sense
    c1 = bend(c10, c11, [(0.35, (0.55, 0.0, 0.20 * scale_z)), (0.70, (0.50, 0.0, 0.35 * scale_z))])
    return {
        "p0": p0,
        "p1": p1,
        "c0": c0,
        "c1": c1,
        "corners": {"C00": c00, "C10": c10, "C01": c01, "C11": c11},
    }


# --------------------------------------------------------------------------------- surfaces
def coons_patch(p0, p1, c0, c1):
    """GeomFill_BSplineCurves Coons patch. Argument order must walk the boundary:
    c1 -> c2 -> c3 -> c4 as (primary0, cross1, primary1, cross0) i.e. around the loop."""
    gf = GeomFill_BSplineCurves(p0, c1, p1, c0, GeomFill_CoonsStyle)
    return gf.Surface()


def filling_face(edges, interior_curves=()):
    """BRepFill_Filling: N-sided plate surface with G0 edge constraints (+ optional
    interior constraint curves -> the approximate Gordon case)."""
    f = BRepFill_Filling()
    for e in edges:
        f.Add(e, GeomAbs_C0, True)
    for c in interior_curves:
        f.Add(edge_of(c), GeomAbs_C0, False)
    f.Build()
    if not f.IsDone():
        raise RuntimeError("BRepFill_Filling did not converge")
    return f.Face()


# ----------------------------------------------------------------------------- measurements
def dist_curve_to_surface(curve_pts_arr: np.ndarray, surf) -> float:
    """Max distance from sampled points to an OCC surface (exact projection)."""
    worst = 0.0
    for q in curve_pts_arr:
        pr = GeomAPI_ProjectPointOnSurf(gp_Pnt(*map(float, q)), surf)
        if pr.NbPoints() == 0:
            return float("inf")
        worst = max(worst, pr.LowerDistance())
    return float(worst)


def dist_curve_to_face_grid(curve_pts_arr: np.ndarray, grid: np.ndarray, chunk: int = 256) -> float:
    """Max distance from sampled points to a dense point grid (faces without a handy surf).

    Chunked over the query points purely to bound peak memory; every distance is computed
    exactly as it would be in one shot, so the result is unchanged.
    """
    g = grid.reshape(-1, 3)
    worst = 0.0
    for s in range(0, len(curve_pts_arr), chunk):
        block = curve_pts_arr[s : s + chunk]
        d = np.sqrt(((block[:, None, :] - g[None, :, :]) ** 2).sum(-1)).min(1)
        worst = max(worst, float(d.max()))
    return worst


def face_surface(face):
    """Underlying Geom_Surface of a face (for exact point projection)."""
    return BRep_Tool.Surface_s(face)


def surface_grid(surf, nu: int, nv: int) -> np.ndarray:
    u0, u1, v0, v1 = surf.Bounds()
    return np.array(
        [
            [
                [(p := surf.Value(float(u), float(v))).X(), p.Y(), p.Z()]
                for v in np.linspace(v0, v1, nv)
            ]
            for u in np.linspace(u0, u1, nu)
        ]
    )


def developability_grid(G: np.ndarray) -> dict:
    """Angle-defect Gaussian curvature on an (n,m,3) grid.

    IDENTICAL formula to `ruled_sheet.developability` (6-neighbour ring, K = defect /
    (incident area / 3)); the only difference is that the grid comes from a real surface
    instead of the bilinear blend of two curves, so the numbers are directly comparable.
    `ruled_sheet.developability` uses m = 7 by default -- an n x 7 grid; the returned
    `grid` field records the sampling this call actually used, and it must be reported
    with the number (see the module docstring).
    """
    n, m, _ = G.shape

    def ang(P, q, r):
        a, b = q - P, r - P
        c = a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-18)
        return math.acos(max(-1.0, min(1.0, c)))

    Ks, defects = [], []
    for i in range(1, n - 1):
        for j in range(1, m - 1):
            P = G[i, j]
            ring = [
                G[i + 1, j],
                G[i + 1, j + 1],
                G[i, j + 1],
                G[i - 1, j],
                G[i - 1, j - 1],
                G[i, j - 1],
            ]
            s = 0.0
            area = 0.0
            for k in range(6):
                q, r = ring[k], ring[(k + 1) % 6]
                s += ang(P, q, r)
                area += 0.5 * float(np.linalg.norm(np.cross(q - P, r - P)))
            d = 2 * math.pi - s
            defects.append(d)
            Ks.append(d / max(area / 3.0, 1e-12))
    K = np.abs(np.array(Ks))
    return {
        "K_abs_max": float(K.max()),
        "K_abs_mean": float(K.mean()),
        "total_defect_rad": float(np.abs(defects).sum()),
        "grid": [n, m],
        "gate_pass": bool(K.mean() <= GATE_K_MEAN and K.max() <= GATE_K_MAX),
    }


def ruled_between(p0, p1):
    """The recipe-C 2-section sheet. Uses the skill's own ruled_face when importable."""
    e0, e1 = edge_of(p0), edge_of(p1)
    if HAVE_RULED_SHEET:
        try:
            from build123d import Edge

            return RS.ruled_face(Edge(e0), Edge(e1)).wrapped, "ruled_sheet.ruled_face"
        except Exception:
            pass
    return BRepFill.Face_s(e0, e1), "BRepFill.Face_s"


# --------------------------------------------------------------------------- flattening (S3)
def lscm(V: np.ndarray, tris: np.ndarray) -> np.ndarray:
    """Least-squares conformal map (Levy 2002), scipy-only. Returns (n,2) UV, unscaled."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl

    n = len(V)
    rows, cols, vals = [], [], []
    row = 0
    for tri in tris:
        q = V[tri]
        e1, e2 = q[1] - q[0], q[2] - q[0]
        nrm = np.cross(e1, e2)
        a2 = float(np.linalg.norm(nrm))
        if a2 < 1e-14:
            continue
        x1 = float(np.linalg.norm(e1))
        ex = e1 / x1
        ey = np.cross(nrm / a2, ex)
        x2, y2 = float(e2 @ ex), float(e2 @ ey)
        W = [complex(x2 - x1, -y2), complex(-x2, y2), complex(x1, 0.0)]
        sc = math.sqrt(a2 / 2.0)
        for k in range(2):
            for j, t in enumerate(tri):
                w = W[j] / sc
                rows += [row, row]
                cols += [int(t), int(t) + n]
                vals += [w.real, -w.imag] if k == 0 else [w.imag, w.real]
            row += 1
    M = sp.coo_matrix((vals, (rows, cols)), shape=(row, 2 * n)).tocsr()
    p0i, p1i = 0, 1
    d = float(np.linalg.norm(V[p1i] - V[p0i]))
    fixed = {p0i: (0.0, 0.0), p1i: (d, 0.0)}
    free = [i for i in range(n) if i not in fixed]
    Mf = M[:, list(free) + [i + n for i in free]]
    bf = np.zeros(row)
    for t, (ux, uy) in fixed.items():
        bf -= M[:, t].toarray().ravel() * ux + M[:, t + n].toarray().ravel() * uy
    sol = spl.lsqr(Mf, bf, atol=1e-12, btol=1e-12, iter_lim=20000)[0]
    UV = np.zeros((n, 2))
    for k, i in enumerate(free):
        UV[i] = (sol[k], sol[k + len(free)])
    for t, uv in fixed.items():
        UV[t] = uv
    return UV


def _cross2(a, b):
    return float(a[0] * b[1] - a[1] * b[0])


def flatten_paths(surf, face_area_mm2: float) -> dict:
    """Path A = ruled-strip development between the two primaries (SKILL.md Stage 3 default).
    Path B = LSCM on a sampled triangulation of the real patch, area-normalised.

    A Coons patch is NOT ruled, so path A is not justified by construction on a recipe-N
    piece; the numbers here are the evidence for that (see SKILL.md Stage 3)."""
    res: dict = {}

    # -- Path A
    n = 200
    G2 = surface_grid(surf, n, 2)
    A = RS.resample_polyline(G2[:, 0, :], n) if HAVE_RULED_SHEET else G2[:, 0, :]
    B = RS.resample_polyline(G2[:, 1, :], n) if HAVE_RULED_SHEET else G2[:, 1, :]
    if HAVE_RULED_SHEET:
        fa, fb, _ = RS.unroll_strip(A, B)
        rep = RS.flattening_report(A, B, fa, fb, face_area=face_area_mm2, m=5)
        res["path_A_ruled_strip"] = {
            "iso_strain_max_pct": rep["iso_strain_max_pct"],
            "area_2d_mm2": rep["area_2d"],
            "area_err_pct": rep["area_err_pct"],
            "gate_pass": bool(rep["pass"]),
        }
    else:
        res["path_A_ruled_strip"] = {"skipped": "ruled_sheet.py not importable"}

    # -- Path B
    nu, nv = 61, 21
    G = surface_grid(surf, nu, nv)
    V = G.reshape(-1, 3)
    tris = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            tris += [(a, a + 1, a + nv), (a + 1, a + nv + 1, a + nv)]
    T = np.array(tris)
    UV = lscm(V, T)
    a3 = sum(0.5 * float(np.linalg.norm(np.cross(V[t[1]] - V[t[0]], V[t[2]] - V[t[0]]))) for t in T)
    a2 = sum(0.5 * abs(_cross2(UV[t[1]] - UV[t[0]], UV[t[2]] - UV[t[0]])) for t in T)
    sc = math.sqrt(a3 / a2)
    UV *= sc
    a2 *= sc * sc
    st = []
    for t in T:
        for k in range(3):
            i, j = int(t[k]), int(t[(k + 1) % 3])
            l3 = float(np.linalg.norm(V[i] - V[j]))
            if l3 > 1e-9:
                st.append(abs(float(np.linalg.norm(UV[i] - UV[j])) / l3 - 1.0))
    st = np.array(st) * 100.0
    area_err = 100.0 * abs(a2 / face_area_mm2 - 1.0)
    res["path_B_lscm"] = {
        "grid": [nu, nv],
        "area_2d_mm2": float(a2),
        "area_err_vs_face_pct": area_err,
        "edge_strain_max_pct": float(st.max()),
        "edge_strain_p99_pct": float(np.percentile(st, 99)),
        "edge_strain_mean_pct": float(st.mean()),
        "gate_pass": bool(st.max() <= GATE_STRAIN_PCT and area_err <= GATE_AREA_ERR_PCT),
    }
    return res


# ------------------------------------------------------------------------------------- main
def main() -> dict:
    """Build the demo network, measure everything, return the results dict."""
    out: dict = {
        "tolerances": {
            "boundary_mm": TOL_BOUNDARY_MM,
            "gate_K_abs_mean": GATE_K_MEAN,
            "gate_K_abs_max": GATE_K_MAX,
        },
        "have_ruled_sheet": HAVE_RULED_SHEET,
    }
    net = lug_facet_network()
    p0, p1, c0, c1 = net["p0"], net["p1"], net["c0"], net["c1"]

    out["input_curves_mm"] = {
        "primary_0": polyline_len(curve_pts(p0, 4000)),
        "primary_1": polyline_len(curve_pts(p1, 4000)),
        "cross_0": polyline_len(curve_pts(c0, 4000)),
        "cross_1": polyline_len(curve_pts(c1, 4000)),
    }

    # (iii-a) corner closure: the four curve ends must meet exactly
    ends = {
        "p0.s": curve_pts(p0, 2)[0],
        "p0.e": curve_pts(p0, 2)[-1],
        "p1.s": curve_pts(p1, 2)[0],
        "p1.e": curve_pts(p1, 2)[-1],
        "c0.s": curve_pts(c0, 2)[0],
        "c0.e": curve_pts(c0, 2)[-1],
        "c1.s": curve_pts(c1, 2)[0],
        "c1.e": curve_pts(c1, 2)[-1],
    }
    out["corner_gaps_mm"] = {
        "C00 p0.start vs c0.start": float(np.linalg.norm(ends["p0.s"] - ends["c0.s"])),
        "C10 p0.end   vs c1.start": float(np.linalg.norm(ends["p0.e"] - ends["c1.s"])),
        "C01 p1.start vs c0.end  ": float(np.linalg.norm(ends["p1.s"] - ends["c0.e"])),
        "C11 p1.end   vs c1.end  ": float(np.linalg.norm(ends["p1.e"] - ends["c1.e"])),
    }
    out["corners_closed"] = bool(max(out["corner_gaps_mm"].values()) <= TOL_BOUNDARY_MM)

    # (ii-a) Coons patch
    coons = coons_patch(p0, p1, c0, c1)
    coons_face = BRepBuilderAPI_MakeFace(coons, 1e-6).Face()
    out["coons"] = {
        "area_mm2": face_area(coons_face),
        "poles_u": coons.NbUPoles(),
        "poles_v": coons.NbVPoles(),
        "degree_u": coons.UDegree(),
        "degree_v": coons.VDegree(),
    }

    # (iii-b) boundary conformance of the Coons patch
    out["coons"]["boundary_max_dev_mm"] = {
        n: dist_curve_to_surface(curve_pts(c, 400), coons)
        for n, c in (("primary_0", p0), ("primary_1", p1), ("cross_0", c0), ("cross_1", c1))
    }
    out["coons"]["boundary_ok"] = bool(
        max(out["coons"]["boundary_max_dev_mm"].values()) <= TOL_BOUNDARY_MM
    )

    # (iv) developability of the Coons patch, several grids
    out["coons"]["developability"] = developability_grid(surface_grid(coons, 41, 7))
    out["k_grid_sensitivity"] = {
        f"{n}x{m}": developability_grid(surface_grid(coons, n, m))
        for n, m in ((41, 7), (41, 15), (41, 41))
    }

    # (ii-b) BRepFill_Filling from the same four edges
    edges = [edge_of(x) for x in (p0, c1, p1, c0)]
    fill_face = filling_face(edges)
    fs = BRepAdaptor_Surface(fill_face)
    fgrid = np.array(
        [
            [
                [(p := fs.Value(float(u), float(v))).X(), p.Y(), p.Z()]
                for v in np.linspace(fs.FirstVParameter(), fs.LastVParameter(), 41)
            ]
            for u in np.linspace(fs.FirstUParameter(), fs.LastUParameter(), 41)
        ]
    )
    fill_surf = face_surface(fill_face)
    out["filling"] = {
        "area_mm2": face_area(fill_face),
        "surface_type": int(fs.GetType()),
        "note": "BRepFill_Filling APPROXIMATES the boundary (energy-minimising plate); "
        "the Coons patch INTERPOLATES it exactly. Area is the trimmed-face area; "
        "the plate surface extends past the wire, so grid-based area is not comparable.",
        "boundary_max_dev_mm": {
            n: dist_curve_to_surface(curve_pts(c, 400), fill_surf)
            for n, c in (("primary_0", p0), ("primary_1", p1), ("cross_0", c0), ("cross_1", c1))
        },
        "developability": developability_grid(fgrid[:, ::7, :]),
    }
    out["filling"]["boundary_ok"] = bool(
        max(out["filling"]["boundary_max_dev_mm"].values()) <= TOL_BOUNDARY_MM
    )
    out["filling"]["area_vs_coons_pct"] = 100.0 * abs(
        out["filling"]["area_mm2"] / out["coons"]["area_mm2"] - 1.0
    )

    # (v) the 2-curve ruled sheet -- WHY a network was needed
    ruled_f, ruled_impl = ruled_between(p0, p1)
    rs = BRepAdaptor_Surface(ruled_f)
    rgrid = np.array(
        [
            [
                [(p := rs.Value(float(u), float(v))).X(), p.Y(), p.Z()]
                for v in np.linspace(rs.FirstVParameter(), rs.LastVParameter(), 201)
            ]
            for u in np.linspace(rs.FirstUParameter(), rs.LastUParameter(), 201)
        ]
    )
    out["ruled_2curve"] = {
        "impl": ruled_impl,
        "area_mm2": face_area(ruled_f),
        "area_err_vs_coons_pct": 100.0 * abs(face_area(ruled_f) / out["coons"]["area_mm2"] - 1.0),
        "cross_0_max_dev_mm": dist_curve_to_face_grid(curve_pts(c0, 400), rgrid),
        "cross_1_max_dev_mm": dist_curve_to_face_grid(curve_pts(c1, 400), rgrid),
        "coons_surface_max_dev_mm": dist_curve_to_face_grid(
            surface_grid(coons, 41, 41).reshape(-1, 3), rgrid
        ),
    }
    # sagitta of each cross curve: the error a straight ruling end must accept
    sags = {}
    for nm, c in (("cross_0", c0), ("cross_1", c1)):
        P = curve_pts(c, 400)
        d = P[-1] - P[0]
        L = np.linalg.norm(d)
        t = ((P - P[0]) @ d) / (L * L)
        sags[nm] = {
            "arc_mm": polyline_len(P),
            "chord_mm": float(L),
            "arc_over_chord": float(polyline_len(P) / L),
            "sagitta_max_mm": float(np.linalg.norm(P - (P[0] + t[:, None] * d), axis=1).max()),
        }
    out["cross_curve_straightness"] = sags

    # (vi) 3x2 network -> approximate Gordon via BRepFill_Filling with an interior constraint
    mid = interp_bspline(
        0.5 * (curve_pts(p0, 9) + curve_pts(p1, 9)) + np.array([0.0, 0.0, 0.9])
    )  # a real middle primary, not the average
    gordon_face = filling_face(edges, interior_curves=[mid])
    gs = BRepAdaptor_Surface(gordon_face)
    ggrid = np.array(
        [
            [
                [(p := gs.Value(float(u), float(v))).X(), p.Y(), p.Z()]
                for v in np.linspace(gs.FirstVParameter(), gs.LastVParameter(), 41)
            ]
            for u in np.linspace(gs.FirstUParameter(), gs.LastUParameter(), 41)
        ]
    )
    gsurf = face_surface(gordon_face)
    out["gordon_3x2_approx"] = {
        "method": "BRepFill_Filling with the middle primary as an interior G0 constraint "
        "(OCC has no Gordon primitive; cf. TiGL CTiglInterpolateCurveNetwork, which "
        "builds one as loft(primaries) + loft(crosses) - tensor interpolation on "
        "compatible B-splines). This is an APPROXIMATION, not a true Gordon surface.",
        "area_mm2": face_area(gordon_face),
        "mid_curve_max_dev_mm": dist_curve_to_surface(curve_pts(mid, 300), gsurf),
        "boundary_max_dev_mm": max(
            dist_curve_to_surface(curve_pts(c, 300), gsurf) for c in (p0, p1, c0, c1)
        ),
        "developability": developability_grid(ggrid[:, ::7, :]),
    }

    # (vi-b) flattening: which Stage-3 path can actually develop a network piece
    out["flattening"] = flatten_paths(coons, out["coons"]["area_mm2"])

    out["verdict"] = {
        "coons_boundary_ok": out["coons"]["boundary_ok"],
        "corners_closed": out["corners_closed"],
        "coons_gate_pass_41x7": out["coons"]["developability"]["gate_pass"],
        "ruled_is_insufficient": bool(
            out["ruled_2curve"]["cross_0_max_dev_mm"] > 0.2
            or out["ruled_2curve"]["area_err_vs_coons_pct"] > 0.4
        ),
    }
    return out


# -------------------------------------------------------------------------------- self-test
# Reference values: VPS venv, OCP 7.9.3, two byte-identical consecutive runs.
# Archived in full at tasks/NXLEARN-126713/run/tcm_prototype_results.json.
EXPECTED: dict[str, tuple[list[str], float]] = {
    "coons.area_mm2": (["coons", "area_mm2"], 74.19788826087),
    "coons.K_abs_mean@41x7": (["coons", "developability", "K_abs_mean"], 0.01117822446354659),
    "coons.K_abs_max@41x7": (["coons", "developability", "K_abs_max"], 0.057007647262248363),
    "K_abs_max@41x41": (["k_grid_sensitivity", "41x41", "K_abs_max"], 0.09128148166446322),
    "filling.area_vs_coons_pct": (["filling", "area_vs_coons_pct"], 14.074726611067522),
    "gordon.mid_curve_dev_mm": (["gordon_3x2_approx", "mid_curve_max_dev_mm"], 0.13530966784164572),
    "ruled.area_err_pct": (["ruled_2curve", "area_err_vs_coons_pct"], 8.075998572806132),
    "ruled.cross_0_dev_mm": (["ruled_2curve", "cross_0_max_dev_mm"], 0.7432970291371945),
    "cross_0.sagitta_mm": (
        ["cross_curve_straightness", "cross_0", "sagitta_max_mm"],
        0.7432744178541828,
    ),
    "pathA.area_err_pct": (["flattening", "path_A_ruled_strip", "area_err_pct"], 7.81103763633384),
    "pathB.area_err_pct": (
        ["flattening", "path_B_lscm", "area_err_vs_face_pct"],
        0.03318700751474557,
    ),
    "pathB.strain_max_pct": (
        ["flattening", "path_B_lscm", "edge_strain_max_pct"],
        2.855112640319568,
    ),
}
SELF_TEST_RTOL = 1e-4


def _dig(d: dict, path: list[str]):
    for k in path:
        d = d[k]
    return d


def self_test(res: dict, rtol: float = SELF_TEST_RTOL) -> bool:
    """Compare a fresh run against the archived reference; print a pass/fail line each."""
    ok = True
    print(f"--- reference check (rtol {rtol:g}, OCP 7.9.3 reference run) ---")
    for label, (path, want) in EXPECTED.items():
        try:
            got = float(_dig(res, path))
        except KeyError:
            print(f"  SKIP  {label:<28} (absent: needs ruled_sheet/build123d)")
            continue
        good = abs(got - want) <= rtol * max(abs(want), 1e-12)
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {label:<28} {got:.10g}  (want {want:.10g})")
    for label, got in (
        ("corners_closed", res["corners_closed"]),
        ("coons_boundary_ok", res["coons"]["boundary_ok"]),
        ("ruled_is_insufficient", res["verdict"]["ruled_is_insufficient"]),
    ):
        ok = ok and bool(got)
        print(f"  {'PASS' if got else 'FAIL'}  {label:<28} {got}")
    return ok


def _print_summary(res: dict) -> None:
    c, f, r = res["coons"], res["filling"], res["ruled_2curve"]
    print("=== curve_network_sheet.py (recipe N demo on the synthetic 126713 lug facet) ===")
    print(
        "input curves mm: " + "  ".join(f"{k}={v:.3f}" for k, v in res["input_curves_mm"].items())
    )
    print(
        f"corners closed        : {res['corners_closed']}  "
        f"(max gap {max(res['corner_gaps_mm'].values()):.2e} mm)"
    )
    print("COONS  GeomFill_BSplineCurves/CoonsStyle")
    print(
        f"  area                : {c['area_mm2']:.4f} mm2   "
        f"poles {c['poles_u']}x{c['poles_v']} deg {c['degree_u']}/{c['degree_v']}"
    )
    for k, v in c["boundary_max_dev_mm"].items():
        print(f"  boundary {k:<10}: {v:.3e} mm")
    print(f"  boundary_ok (<={TOL_BOUNDARY_MM:g} mm): {c['boundary_ok']}")
    d = c["developability"]
    print(
        f"  K_abs_mean {d['K_abs_mean']:.3e} / K_abs_max {d['K_abs_max']:.3e} on "
        f"{d['grid'][0]}x{d['grid'][1]}  GATE {'PASS' if d['gate_pass'] else 'FAIL'}"
    )
    print(
        "  grid sensitivity of K_abs_max: "
        + "  ".join(f"{g}={v['K_abs_max']:.3e}" for g, v in res["k_grid_sensitivity"].items())
    )
    print("FILLING BRepFill_Filling")
    print(
        f"  area {f['area_mm2']:.4f} mm2 ({f['area_vs_coons_pct']:.3f}% vs Coons)  "
        f"max boundary dev {max(f['boundary_max_dev_mm'].values()):.3e} mm"
    )
    print(
        f"  K_abs_mean {f['developability']['K_abs_mean']:.3e} / "
        f"K_abs_max {f['developability']['K_abs_max']:.3e}"
    )
    print(f"RULED 2-curve ({r['impl']})")
    print(f"  area {r['area_mm2']:.4f} mm2 = {r['area_err_vs_coons_pct']:.2f}% off the patch")
    print(
        f"  cross_0 misses by {r['cross_0_max_dev_mm']:.4f} mm; "
        f"cross_1 by {r['cross_1_max_dev_mm']:.4f} mm; "
        f"patch by {r['coons_surface_max_dev_mm']:.4f} mm"
    )
    for k, v in res["cross_curve_straightness"].items():
        print(
            f"  {k}: arc {v['arc_mm']:.3f} / chord {v['chord_mm']:.3f} = "
            f"{v['arc_over_chord']:.4f}, sagitta {v['sagitta_max_mm']:.4f} mm"
        )
    g = res["gordon_3x2_approx"]
    print("GORDON-approx 3x2 (Filling + interior constraint)")
    print(
        f"  area {g['area_mm2']:.4f} mm2  mid-curve dev {g['mid_curve_max_dev_mm']:.4e} mm  "
        f"boundary dev {g['boundary_max_dev_mm']:.3e} mm"
    )
    fl = res["flattening"]
    print("FLATTENING (Stage 3) on the Coons patch")
    a = fl.get("path_A_ruled_strip", {})
    if "iso_strain_max_pct" in a:
        print(
            f"  A ruled-strip: iso_strain {a['iso_strain_max_pct']:.4f}%  "
            f"area_err {a['area_err_pct']:.3f}%  gate {'PASS' if a['gate_pass'] else 'FAIL'}"
        )
    b = fl["path_B_lscm"]
    print(
        f"  B LSCM       : edge_strain max {b['edge_strain_max_pct']:.4f}% "
        f"p99 {b['edge_strain_p99_pct']:.4f}% mean {b['edge_strain_mean_pct']:.4f}%  "
        f"area_err {b['area_err_vs_face_pct']:.3f}%  gate {'PASS' if b['gate_pass'] else 'FAIL'}"
    )
    print(f"VERDICT {json.dumps(res['verdict'])}")


if __name__ == "__main__":
    result = main()
    _print_summary(result)
    passed = self_test(result)
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
        print(f"wrote {sys.argv[1]}")
    print("SELF-TEST " + ("OK" if passed else "FAILED"))
    sys.exit(0 if passed else 1)
