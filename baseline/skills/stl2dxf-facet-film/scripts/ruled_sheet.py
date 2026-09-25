"""Ruled facet sheets: build, check developability, and unroll to a 2D outline.

The core geometric objects of the facet-film method (learned from the maintainer's
NX sessions): each curved watch facet is covered by a sheet that is either
  - an EXTRUSION of a planar profile (exactly developable, K = 0), or
  - a RULED surface between two boundary curves drawn on the facet
    (near-developable; the NX record shows |K|max 0.001-0.039 mm^-2).

This module gives the three primitives a Python port needs:
  ruled_face(edge_a, edge_b)      -> OCP/build123d Face (exact ruled B-rep, for STEP/QA)
  developability(A, B, m=7)       -> discrete Gaussian-curvature gate before flattening
  unroll_strip(A, B)              -> exact isometric development of the sampled ruled
                                     surface (triangle strip); use for the DXF outline
  unroll_face(face, n=200)        -> convenience: sample an existing ruled/extruded
                                     B-rep sheet's two long boundary edges and unroll

Validation gates (from the NX record, measured on the maintainer's accepted kit):
  - developability: mean |K| <= 1.5e-2 mm^-2 AND max |K| <= 6.5e-2 (worst accepted
    piece); beyond that the facet must be split (it is not one film piece).
    developability() returns a "pass" flag for exactly these two gates.
  - development strain (flattening_report): interior iso-curve strain <= 0.4 %
    and, when an independent face area is supplied, area error <= 0.4 %.
    NOTE the strip development is isometric to its OWN samples by construction,
    so comparing the strip to itself proves nothing — the report therefore
    measures interior iso-curves (real strain of a skew ruled surface) and
    accepts an independent `face_area` (B-rep GProp area) as cross-check.
  - THE GATES DO NOT VALIDATE BOUNDARY CHOICE. A wrong facet boundary yields a
    wrong-size piece that passes every gate here; always cross-check the
    developed piece's principal dimensions against the facet region / catalogue.

Requires: numpy (scipy only for fit_smoothing_spline); build123d/OCP only for the
*_face helpers. Tested: cylinder patch unrolls to its exact arc-length rectangle
(31.4143 vs 31.4159), cone frustum area conserved to 1e-12; a skew ruled surface
reports K ~ 7e-4 mm^-2 and nonzero iso-curve strain.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "ruled_face",
    "sample_curve",
    "resample_polyline",
    "developability",
    "unroll_strip",
    "unroll_face",
    "outline_polygon",
    "polygon_area_2d",
    "strip_area_3d",
    "flattening_report",
]


# ---------------------------------------------------------------- B-rep helpers


def ruled_face(edge_a, edge_b):
    """Exact ruled sheet between two build123d Edges/Wires (NX 'Through Curves',
    2 sections, G0, parameter alignment). Returns a build123d Face.

    Both curves must run in the SAME direction (check with position_at(0/1);
    reverse one with .reversed() if the sheet comes out bow-tied).
    """
    from build123d import Face
    from OCP.BRepFill import BRepFill

    return Face(BRepFill.Face_s(edge_a.wrapped, edge_b.wrapped))


def sample_curve(curve, n: int) -> np.ndarray:
    """build123d Edge/Wire -> (n,3) points at equal parameter steps."""
    return np.array([tuple(curve.position_at(t)) for t in np.linspace(0.0, 1.0, n)], dtype=float)


def resample_polyline(pts: np.ndarray, n: int) -> np.ndarray:
    """Resample an ordered 3D polyline (e.g. a trimesh mesh-plane section) to n
    points equally spaced by arc length. Use before unroll_strip so A and B have
    matched samples."""
    pts = np.asarray(pts, dtype=float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    t = np.linspace(0.0, s[-1], n)
    out = np.empty((n, pts.shape[1]))
    for k in range(pts.shape[1]):
        out[:, k] = np.interp(t, s, pts[:, k])
    return out


# ------------------------------------------------------------- developability


def developability(A: np.ndarray, B: np.ndarray, m: int = 7) -> dict:
    """Discrete Gaussian curvature of the ruled surface S(u,v)=(1-v)A(u)+vB(u)
    on an n x m grid: angle defect at each interior vertex / (1/3 incident area).
    A truly developable sheet (cylinder, cone, torsal ruled) gives ~0; the gate
    for one film piece is K_abs_mean <= 1.5e-2 mm^-2 (NX record's worst kept piece
    had 1.4e-2). total_defect_rad is the strain budget a flattening must absorb.
    """
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    n = len(A)
    vs = np.linspace(0, 1, m)
    G = (1 - vs)[None, :, None] * A[:, None, :] + vs[None, :, None] * B[:, None, :]  # (n,m,3)

    def ang(p, q, r):
        a = q - p
        b = r - p
        c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-18)
        return np.arccos(np.clip(c, -1, 1))

    def tri_area(p, q, r):
        return 0.5 * np.linalg.norm(np.cross(q - p, r - p))

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
                area += tri_area(P, q, r)
            d = 2 * np.pi - s
            defects.append(d)
            Ks.append(d / max(area / 3.0, 1e-12))
    Ks = np.array(Ks)
    defects = np.array(defects)
    k_max = float(np.abs(Ks).max())
    k_mean = float(np.abs(Ks).mean())
    return {
        "K_abs_max": k_max,
        "K_abs_mean": k_mean,
        "total_defect_rad": float(np.abs(defects).sum()),
        "grid": (n, m),
        "pass": k_mean <= 1.5e-2 and k_max <= 6.5e-2,
    }


# --------------------------------------------------------------------- unroll


def unroll_strip(A: np.ndarray, B: np.ndarray):
    """Exact isometric development of the triangle strip through matched samples
    A,B (each (n,3), same direction). Returns (flatA (n,2), flatB (n,2), stats).

    Every triangle is laid flat with its true 3D edge lengths (circle-circle
    intersection), each new vertex on the opposite side of the shared edge from
    the previous triangle's third vertex so the strip never folds back.
    For a developable sheet this IS the flat pattern; for a near-developable one
    it is the minimum-bend development along the rulings - gate with
    developability() first, then verify with flattening_report().
    """
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    n = len(A)
    assert A.shape == B.shape and n >= 2
    d = np.linalg.norm
    fa = np.zeros((n, 2))
    fb = np.zeros((n, 2))
    fb[0] = (0.0, d(B[0] - A[0]))

    def place(p1, p2, r1, r2, opposite):
        v = p2 - p1
        L = d(v)
        if L < 1e-12:
            return p1 + np.array([r1, 0.0])
        a = (r1**2 - r2**2 + L**2) / (2 * L)
        h = np.sqrt(max(r1**2 - a**2, 0.0))
        base = p1 + a * v / L
        perp = np.array([-v[1], v[0]]) / L
        side_prev = np.sign(np.dot(opposite - p1, perp)) or 1.0
        return base - side_prev * h * perp

    for i in range(1, n):
        opp = fb[i - 2] if i >= 2 else np.array([-1.0, 0.0])
        fa[i] = place(fa[i - 1], fb[i - 1], d(A[i] - A[i - 1]), d(A[i] - B[i - 1]), opp)
        fb[i] = place(fb[i - 1], fa[i], d(B[i] - B[i - 1]), d(B[i] - A[i]), fa[i - 1])
    return fa, fb, {"n_rulings": n}


def outline_polygon(flatA: np.ndarray, flatB: np.ndarray) -> np.ndarray:
    """Closed 2D outline of an unrolled strip: A forward, B backward. (n*2, 2)."""
    return np.vstack([flatA, flatB[::-1]])


def strip_area_3d(A, B) -> float:
    tot = 0.0
    for i in range(1, len(A)):
        tot += 0.5 * np.linalg.norm(np.cross(B[i - 1] - A[i - 1], A[i] - A[i - 1]))
        tot += 0.5 * np.linalg.norm(np.cross(A[i] - B[i - 1], B[i] - B[i - 1]))
    return tot


def polygon_area_2d(P: np.ndarray) -> float:
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _polyline_len(P):
    return float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum())


def flattening_report(A, B, flatA, flatB, face_area: float | None = None, m: int = 5) -> dict:
    """Honest development-strain gate. The strip development preserves its own
    boundary and ruling lengths BY CONSTRUCTION, so those are not checked.
    What is checked:
      - interior iso-curve strain: for v in (1..m-1)/m, the 3D iso-polyline of
        the ruled surface ((1-v)A+vB) vs its image in the development
        ((1-v)flatA+v flatB — exact, since rulings map to straight segments with
        preserved length). Nonzero for skew (non-developable) ruled surfaces;
        gate 0.4 % (the NX record's worst accepted perimeter strain).
      - area error vs an INDEPENDENT area when supplied (e.g. B-rep GProp face
        area, or a much denser sampling); gate 0.4 %.
    A wrong boundary still passes — cross-check piece dimensions separately."""
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    strains = []
    for k in range(1, m):
        v = k / m
        iso3 = _polyline_len((1 - v) * A + v * B)
        iso2 = _polyline_len((1 - v) * flatA + v * flatB)
        strains.append(abs(iso2 / iso3 - 1.0) if iso3 else 0.0)
    a2 = polygon_area_2d(outline_polygon(flatA, flatB))
    rep = {
        "iso_strain_max_pct": 100.0 * max(strains),
        "area_2d": a2,
        "area_strip_3d": strip_area_3d(A, B),
    }
    if face_area is not None:
        rep["area_face_3d"] = float(face_area)
        rep["area_err_pct"] = 100.0 * abs(a2 / face_area - 1.0)
    rep["pass"] = rep["iso_strain_max_pct"] <= 0.4 and rep.get("area_err_pct", 0.0) <= 0.4
    return rep


def unroll_face(face, n: int = 200):
    """Convenience for an existing near-ruled B-rep sheet (e.g. imported STEP):
    sample the two v-iso boundary curves of the underlying surface and unroll.
    Uses the face's exact B-rep area as the independent area reference.
    Returns (flatA, flatB, dev_stats, fidelity_report)."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface

    ad = BRepAdaptor_Surface(face.wrapped)
    u0, u1, v0, v1 = (
        ad.FirstUParameter(),
        ad.LastUParameter(),
        ad.FirstVParameter(),
        ad.LastVParameter(),
    )
    us = np.linspace(u0, u1, n)
    A = np.array([[*_pnt(ad, u, v0)] for u in us])
    B = np.array([[*_pnt(ad, u, v1)] for u in us])
    dev = developability(A, B)
    fa, fb, _ = unroll_strip(A, B)
    return fa, fb, dev, flattening_report(A, B, fa, fb, face_area=float(face.area))


def fit_smoothing_spline(
    points: np.ndarray, reject: float = 0.07, degree: int = 5, n_out: int = 200, max_iter: int = 5
):
    """Outlier-rejecting smoothing-spline fit of an ordered 3D polyline — the
    Python port of NX 'Fit Curve / Fit Spline with Automatic Point Rejection'
    (the operator used reject=0.07 mm everywhere). Iteratively drops points
    farther than `reject` from the current fit, then resamples n_out points.
    NOTE: on real scans the boundary-extraction criterion contributes 0.2-0.5 mm
    of uncertainty — far more than `reject`; treat reject as a smoothing knob,
    not an accuracy guarantee. Returns (fitted_points (n_out,3), max_residual)."""
    from scipy.interpolate import splev, splprep

    P = np.asarray(points, float)
    keep = np.ones(len(P), bool)
    resid = np.zeros(len(P))
    for _ in range(max_iter):
        Q = P[keep]
        if len(Q) <= degree + 1:
            break
        s = len(Q) * (reject**2)  # smoothing prop. to allowed residual
        tck, u = splprep(Q.T, k=min(degree, len(Q) - 1), s=s)
        fitQ = np.array(splev(u, tck)).T
        resid_k = np.linalg.norm(fitQ - Q, axis=1)
        resid[keep] = resid_k
        bad = resid_k > reject
        if not bad.any():
            break
        idx = np.where(keep)[0][bad]
        keep[idx] = False
    out = np.array(splev(np.linspace(0, 1, n_out), tck)).T
    return out, float(resid[keep].max() if keep.any() else 0.0)


def _pnt(ad, u, v):
    p = ad.Value(u, v)
    return p.X(), p.Y(), p.Z()


if __name__ == "__main__":
    # self-test (no build123d needed)
    th = np.radians(np.linspace(0, 120, 60))
    R, H = 15.0, 8.0
    A = np.c_[R * np.cos(th), R * np.sin(th), np.zeros_like(th)]
    B = np.c_[R * np.cos(th), R * np.sin(th), np.full_like(th, H)]
    fa, fb, _ = unroll_strip(A, B)
    w = np.linalg.norm(fa[-1] - fa[0])
    exact = 2 * np.pi * R * 120 / 360
    rep = flattening_report(A, B, fa, fb, face_area=exact * H)
    dev = developability(A, B)
    print(
        f"cylinder: width {w:.4f} vs arc {exact:.4f}; iso_strain {rep['iso_strain_max_pct']:.5f}%; "
        f"area_err {rep['area_err_pct']:.4f}%; K {dev['K_abs_max']:.2e}; "
        f"pass={rep['pass']} dev_pass={dev['pass']}"
    )
    assert abs(w - exact) < 0.01 and rep["pass"] and dev["pass"] and dev["K_abs_max"] < 1e-9
    # skew (non-developable) ruled surface: K gate scale AND nonzero iso strain
    A = np.c_[np.linspace(0, 20, 60), np.zeros(60), np.zeros(60)]
    B = np.c_[np.linspace(0, 20, 60), np.full(60, 10.0), np.linspace(0, 6, 60)]
    dev = developability(A, B)
    fa, fb, _ = unroll_strip(A, B)
    rep = flattening_report(A, B, fa, fb)
    print(
        f"skew ruled: K_abs_mean {dev['K_abs_mean']:.2e} (gate 1.5e-2), "
        f"iso_strain {rep['iso_strain_max_pct']:.4f}%"
    )
    assert dev["K_abs_mean"] > 1e-4 and rep["iso_strain_max_pct"] > 1e-4
    # smoothing-spline fit with outlier rejection
    t = np.linspace(0, 1, 80)
    clean = np.c_[20 * t, 3 * np.sin(3 * t), np.zeros_like(t)]
    noisy = clean + np.random.default_rng(0).normal(0, 0.01, clean.shape)
    noisy[40] += (0.5, 0.5, 0)  # outlier
    fit, res = fit_smoothing_spline(noisy, reject=0.07)
    print(f"fit_smoothing_spline: max residual {res:.4f} (reject 0.07)")
    assert res <= 0.07
    print("ruled_sheet self-test OK")
