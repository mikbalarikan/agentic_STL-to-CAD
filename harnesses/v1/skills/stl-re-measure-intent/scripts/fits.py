#!/usr/bin/env python3
"""Primitive fits with residuals: circle (Kasa, IRLS-Cauchy), 2D line (TLS), plane (SVD, seeded RANSAC).

Provenance:
  - circle_kasa: golden-examples/dreame_brush-caps/report/source/align.py:fit_circle (Kasa
    algebraic fit), unchanged maths; now also returns max/p95 residual.
  - circle_irls: golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q03_datum_full.py:89-101
    (weighted algebraic circle fit with a Cauchy robustifier, scale 0.30 mm in the golden).
    Changes: centre initialised from Kasa instead of (0,0); scale is a CLI parameter.
  - plane_ransac: golden-examples/dreame_brush-caps/report/source/datum.py:ransac_plane
    (seeded RANSAC + SVD refine). Unchanged maths, typed.
  - line_tls / plane_svd: NEW (standard total-least-squares via SVD).
Every fit reports n, rms, p95, max residual and a second, independent estimator where one
exists (percentile radius for circles) - evidence rule T6 (analysis/baseline/
facet-film-transferable.md: residual alone never accepts a fit).

CLI: select points from a mesh in the DATUM frame by a cylindrical box (z, r, theta) or
from a z-section, then fit. Writes a JSON with the run-contract §2 header.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (densify, header, load_alignment, load_mesh, rnd, write_json,  # noqa: E402
                    z_section_xy)


def _stats(d: np.ndarray) -> dict[str, Any]:
    a = np.abs(d)
    return {"n": int(len(d)), "rms": rnd(np.sqrt((d ** 2).mean())), "p95": rnd(np.percentile(a, 95)),
            "max": rnd(a.max())}


def circle_kasa(xy: np.ndarray) -> dict[str, Any]:
    x, y = xy[:, 0], xy[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    sol = np.linalg.lstsq(A, b, rcond=None)[0]
    cx, cy = sol[0], sol[1]
    r = float(np.sqrt(sol[2] + cx ** 2 + cy ** 2))
    d = np.hypot(x - cx, y - cy) - r
    rr = np.hypot(x - cx, y - cy)
    return {"method": "kasa", "cx": rnd(cx), "cy": rnd(cy), "r": rnd(r), "d": rnd(2 * r),
            "residual": _stats(d),
            "check_percentile_r": {"p50": rnd(np.percentile(rr, 50)), "p5": rnd(np.percentile(rr, 5)),
                                   "p95": rnd(np.percentile(rr, 95))}}


def circle_irls(xy: np.ndarray, cauchy_c: float, weights: Optional[np.ndarray] = None,
                iters: int = 60) -> dict[str, Any]:
    W = np.ones(len(xy)) if weights is None else np.asarray(weights, float)
    k = circle_kasa(xy)
    c2 = np.array([k["cx"], k["cy"]], float)
    for _ in range(iters):
        d = np.hypot(*(xy - c2).T)
        Rm = np.average(d, weights=W)
        w2 = W / (1.0 + ((d - Rm) / cauchy_c) ** 2)
        A = np.c_[2 * xy, np.ones(len(xy))] * w2[:, None]
        b = (xy ** 2).sum(1) * w2
        sol = np.linalg.lstsq(A, b, rcond=None)[0]
        cn = sol[:2]
        if np.linalg.norm(cn - c2) < 1e-10:
            c2 = cn
            break
        c2 = cn
    d = np.hypot(*(xy - c2).T)
    Rm = float(np.average(d, weights=W))
    return {"method": f"irls-cauchy(c={cauchy_c})", "cx": rnd(c2[0]), "cy": rnd(c2[1]), "r": rnd(Rm),
            "d": rnd(2 * Rm), "residual": _stats(d - Rm),
            "check_percentile_r": {"p50": rnd(np.percentile(d, 50)), "p5": rnd(np.percentile(d, 5)),
                                   "p95": rnd(np.percentile(d, 95))},
            "kasa": {"cx": k["cx"], "cy": k["cy"], "r": k["r"]}}


def line_tls(uv: np.ndarray) -> dict[str, Any]:
    c = uv.mean(axis=0)
    _, _, vt = np.linalg.svd(uv - c, full_matrices=False)
    t, n = vt[0], vt[1]
    d = (uv - c) @ n
    ang = float(np.degrees(np.arctan2(t[1], t[0])))
    return {"method": "tls-svd", "point": [rnd(c[0]), rnd(c[1])], "dir": [rnd(t[0]), rnd(t[1])],
            "angle_deg_from_u": rnd(((ang + 90) % 180) - 90), "residual": _stats(d)}


def plane_svd(P: np.ndarray) -> dict[str, Any]:
    c = P.mean(axis=0)
    _, _, vt = np.linalg.svd(P - c, full_matrices=False)
    n = vt[2] if vt[2][2] >= 0 else -vt[2]
    d = (P - c) @ n
    tilt = float(np.degrees(np.arccos(min(1.0, abs(n[2])))))
    return {"method": "svd", "normal": [rnd(v) for v in n], "centroid": [rnd(v) for v in c],
            "tilt_from_z_deg": rnd(tilt), "residual": _stats(d)}


def plane_ransac(P: np.ndarray, tol: float, iters: int = 300, seed: int = 0) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(iters):
        idx = rng.choice(len(P), 3, replace=False)
        p0, p1, p2 = P[idx]
        n = np.cross(p1 - p0, p2 - p0)
        nn = np.linalg.norm(n)
        if nn < 1e-9:
            continue
        n /= nn
        inl = np.abs((P - p0) @ n) < tol
        if best is None or inl.sum() > best.sum():
            best = inl
    if best is None:
        raise ValueError("RANSAC found no non-degenerate sample")
    out = plane_svd(P[best])
    out["method"] = f"ransac(tol={tol},iters={iters},seed={seed})+svd"
    out["inlier_fraction"] = rnd(best.sum() / len(P))
    return out


def select_box(V: np.ndarray, z: Optional[tuple[float, float]], r: Optional[tuple[float, float]],
               theta: Optional[tuple[float, float]]) -> np.ndarray:
    k = np.ones(len(V), bool)
    rr = np.hypot(V[:, 0], V[:, 1])
    th = np.degrees(np.arctan2(V[:, 1], V[:, 0]))
    if z:
        k &= (V[:, 2] >= z[0]) & (V[:, 2] <= z[1])
    if r:
        k &= (rr >= r[0]) & (rr <= r[1])
    if theta:
        lo, hi = theta
        span = (hi - lo) % 360.0
        k &= ((th - lo) % 360.0) <= span
    return k


def _pair(s: Optional[str]) -> Optional[tuple[float, float]]:
    if s is None:
        return None
    a, b = (float(v) for v in s.split(","))
    return (a, b)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fit", choices=["circle", "circle-irls", "line", "plane", "plane-ransac"])
    ap.add_argument("--mesh", help="STL (datum frame, or raw + --alignment)")
    ap.add_argument("--alignment", help="intake/alignment.json (applies matrix_4x4 raw->datum)")
    ap.add_argument("--points", help=".npy (N,2|3) point file instead of a mesh")
    ap.add_argument("--section-z", type=float, help="circle: fit the z-section loop points instead of vertices")
    ap.add_argument("--loop", default="all", help="with --section-z: 'all', 'largest', 'smallest' or index")
    ap.add_argument("--z", help="zlo,zhi vertex box (CAD tessellations have few vertices mid-face: use --section-z there)"); ap.add_argument("--r", help="rlo,rhi")
    ap.add_argument("--theta", help="thlo,thhi deg (datum frame, CCW about +Z)")
    ap.add_argument("--proj", default="xy", choices=["xy", "rz", "xz", "yz"], help="2D projection for circle/line")
    ap.add_argument("--cauchy-c", type=float, default=0.30,
                    help="IRLS Cauchy scale, mm (golden B02 q03_datum_full.py:92 used 0.30)")
    ap.add_argument("--tol", type=float, help="RANSAC inlier tol, mm (RE_SPEC.md:127: 0.05-0.1 ~ scan noise)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="fit", help="label written to the output")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    inputs: list[str] = [p for p in (a.mesh, a.alignment, a.points) if p]
    if a.points:
        P = np.load(a.points)
        estimator = f"points file {a.points}"
    else:
        m = load_mesh(a.mesh, load_alignment(a.alignment))
        if a.section_z is not None:
            loops = [densify(p) for p in z_section_xy(m, a.section_z)]
            if not loops:
                sys.exit(f"no section at z={a.section_z}")
            if a.loop == "largest":
                loops = [max(loops, key=lambda p: np.ptp(p, axis=0).prod())]
            elif a.loop == "smallest":
                loops = [min(loops, key=lambda p: np.ptp(p, axis=0).prod())]
            elif a.loop != "all":
                loops = [loops[int(a.loop)]]
            P = np.vstack(loops)
            P = np.c_[P, np.full(len(P), a.section_z)]
            estimator = f"z-section z={a.section_z} loop={a.loop}, densified 0.02 mm"
        else:
            P = m.vertices
            estimator = "mesh vertices"
        k = select_box(P, _pair(a.z), _pair(a.r), _pair(a.theta))
        P = P[k]
        estimator += f"; box z={a.z} r={a.r} theta={a.theta}"
    if len(P) < 3:
        sys.exit(f"only {len(P)} points selected")

    def proj(P3: np.ndarray) -> np.ndarray:
        if P3.shape[1] == 2:
            return P3
        if a.proj == "xy":
            return P3[:, :2]
        if a.proj == "xz":
            return P3[:, [0, 2]]
        if a.proj == "yz":
            return P3[:, [1, 2]]
        return np.c_[np.hypot(P3[:, 0], P3[:, 1]), P3[:, 2]]

    if a.fit == "circle":
        res = circle_kasa(proj(P))
    elif a.fit == "circle-irls":
        res = circle_irls(proj(P), a.cauchy_c)
    elif a.fit == "line":
        res = line_tls(proj(P))
    elif a.fit == "plane":
        res = plane_svd(P)
    else:
        if a.tol is None:
            sys.exit("plane-ransac needs --tol (use the scan noise; RE_SPEC.md:127 gives 0.05-0.1 mm)")
        res = plane_ransac(P, a.tol, seed=a.seed)
    out = header("fit.json", "fits.py", inputs, a.seed)
    out.update({"name": a.name, "fit": a.fit, "projection": a.proj, "estimator": estimator, "result": res})
    write_json(a.out, out)
    print(f"{a.name}: {a.fit} -> " + ", ".join(f"{k}={v}" for k, v in res.items() if not isinstance(v, (dict, list))))
    print(f"  residual {res['residual']}")


if __name__ == "__main__":
    main()
