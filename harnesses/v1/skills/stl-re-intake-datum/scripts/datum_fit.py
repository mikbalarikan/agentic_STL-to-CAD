#!/usr/bin/env python3
"""datum_fit.py - primitive fits for datum work and the scan noise floor.

PROVENANCE
  * ransac_plane, dominant_planes: lifted from
    golden-examples/dreame_brush-caps/report/source/datum.py:7-46.
    Changed: typed, area-aware, returns a dict, deterministic seed parameter kept (default 0).
  * axis_from_normals: rewritten from datum.py:48-61. The golden direction formula was
    already correct (smallest eigenvector of sum n n^T) but the docstring stated the wrong
    form and the point solve contained a no-op line `a - (a@d)*d*0`. Here the direction is
    the eigenvector of the SMALLEST eigenvalue of sum(w n n^T) (all normals of a surface of
    revolution are perpendicular to its axis), and the point is the least-squares point
    closest to all normal lines, projected onto the plane through the centroid
    perpendicular to d (the component along d is undetermined and is dropped explicitly).
    The baseline form "smallest eigenvector of sum(I - n n^T)" is WRONG (returns a
    near-normal direction): analysis/baseline/stl2step-skills.md section 5.1.
  * fit_circle_kasa, level_plane: lifted from
    golden-examples/dreame_brush-caps/report/source/align.py:10-37 (fit_circle,
    level_transform). Changed: bin width / half-width / cone / tolerance are parameters
    (defaults = the values the golden used), returns a dict.
  * fit_circle_irls: lifted from
    golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q03_datum_full.py:98-111
    (weighted algebraic circle fit with a Cauchy robustifier). Changed: function with a
    scale parameter (default 0.30 mm = the value B02 used), returns residual stats.
  * normal_vote: lifted from q03_datum_full.py:24-44 (sign-free Fibonacci spherical vote,
    then iterative refinement). Changed: function, parameters exposed.

All randomness is seeded (default seed 0). No wall-clock value enters any computation.

CLI (all output JSON follows harnesses/v0/skills/stl-re-orchestrate/references/run-contract.md section 2):
  planes  : dominant-plane survey (candidates for a functional primary; never pick by area alone)
  plane   : level-plane fit near an approximate normal -> rms/max residual
  axis    : revolve axis from face normals in a crop (axis-primary parts)
  noise   : noise floor on a clean primitive (plane region or section circle)

Blind spots (what this does NOT check): whether the region you chose is functional,
whether a converged fit found the intended feature (always cross-check with a section
plot), or whether the scan is at the right scale (CHK-SCALE runs before this).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import trimesh

TOOL_VERSION = "stl-re-intake-datum/1.0"


# ----------------------------------------------------------------------------- helpers
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def json_header(schema: str, tool: str, inputs: dict[str, str], seed: int) -> dict[str, Any]:
    """Common header per run-contract section 2. `created` is provenance only."""
    return {"schema": f"stl-re/{schema}@1", "tool": tool, "tool_version": TOOL_VERSION,
            "inputs": inputs, "seed": seed,
            "created": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")}


def unit(v: Sequence[float]) -> np.ndarray:
    a = np.asarray(v, dtype=float)
    n = np.linalg.norm(a)
    if n < 1e-12:
        raise ValueError("zero-length vector")
    return a / n


def residual_stats(d: np.ndarray) -> dict[str, float]:
    d = np.abs(np.asarray(d, float))
    return {"n": int(d.size), "rms": float(np.sqrt((d ** 2).mean())),
            "p95": float(np.percentile(d, 95)), "max": float(d.max())}


# ----------------------------------------------------------------------------- planes
def ransac_plane(pts: np.ndarray, tol: float, iters: int = 300, seed: int = 0) -> dict[str, Any]:
    """RANSAC plane (3-point samples) then SVD refine on the inliers.
    Golden: tol 0.05, 300 iterations, seed 0 (dreame datum.py:7, align.py:24)."""
    pts = np.asarray(pts, float)
    if len(pts) < 3:
        raise ValueError("ransac_plane: fewer than 3 points")
    rng = np.random.default_rng(seed)
    best: tuple[int, np.ndarray] | None = None
    for _ in range(iters):
        p0, p1, p2 = pts[rng.choice(len(pts), 3, replace=False)]
        n = np.cross(p1 - p0, p2 - p0)
        nn = np.linalg.norm(n)
        if nn < 1e-12:
            continue
        n = n / nn
        inl = np.abs((pts - p0) @ n) < tol
        if best is None or int(inl.sum()) > best[0]:
            best = (int(inl.sum()), inl)
    if best is None:
        raise RuntimeError("ransac_plane: all samples degenerate")
    inl = best[1]
    P = pts[inl]
    c = P.mean(axis=0)
    _, _, vt = np.linalg.svd(P - c, full_matrices=False)
    n = vt[2]
    d = (P - c) @ n
    return {"normal": n, "centroid": c, "inlier_frac": float(inl.mean()), "inliers": inl,
            **{f"fit_{k}_mm" if k in ("rms", "max", "p95") else k: v
               for k, v in residual_stats(d).items()}}


def dominant_planes(m: trimesh.Trimesh, angle_deg: float = 3.0, off_bin: float = 0.08,
                    min_area: float = 2.0, top: int = 8) -> list[dict[str, Any]]:
    """Normal clustering then 1-D offset clustering. Golden defaults 3 deg / 0.08 mm / 2 mm^2
    (dreame datum.py:27). Returns candidates sorted by area. Area rank is NOT a datum rule:
    the primary must be functional (SYNTHESIS B2; baseline largest-facet rule dropped)."""
    n, a, c = m.face_normals, m.area_faces, m.triangles_center
    groups = trimesh.grouping.group_vectors(n, angle=np.radians(angle_deg), include_negative=False)[1]
    out: list[dict[str, Any]] = []
    for g in groups:
        g = np.asarray(g)
        if a[g].sum() < min_area:
            continue
        nn = unit(n[g].mean(axis=0))
        off = c[g] @ nn
        order = np.argsort(off, kind="stable")
        off_s, g_s = off[order], g[order]
        cuts = np.where(np.diff(off_s) > off_bin)[0] + 1
        for seg in np.split(np.arange(len(g_s)), cuts):
            fi = g_s[seg]
            area = float(a[fi].sum())
            if area < min_area:
                continue
            out.append({"normal": nn.round(5).tolist(), "offset": float(off_s[seg].mean()),
                        "area": area, "centroid": c[fi].mean(axis=0).round(4).tolist(),
                        "n_faces": int(len(fi)), "faces": fi})
    out.sort(key=lambda d: -d["area"])
    return out[:top]


def level_plane(m: trimesh.Trimesh, approx_normal: Sequence[float], cone_deg: float = 10.0,
                tol: float = 0.05, bin_mm: float = 0.1, halfwidth_mm: float = 0.15,
                offset_range: Sequence[float] | None = None, iters: int = 300,
                seed: int = 0) -> dict[str, Any]:
    """Primary plane near a stated approximate normal (dreame align.py:21-37).
    faces with normal within cone_deg of approx -> area-weighted offset histogram
    (bin_mm) -> peak bin +/- halfwidth_mm (or an explicit offset_range) -> RANSAC(tol)
    -> widen to |d| < 2 tol -> SVD refine. Golden: 10 deg, 0.1 mm bins, +/-0.15, tol 0.05."""
    an = unit(approx_normal)
    n, c, a = m.face_normals, m.triangles_center, m.area_faces
    cand = np.where(n @ an > np.cos(np.radians(cone_deg)))[0]
    if len(cand) < 3:
        raise RuntimeError(f"level_plane: no faces within {cone_deg} deg of {an.tolist()} - "
                           "check the approximate normal and the normal orientation")
    off = c[cand] @ an
    if offset_range is not None:
        lo, hi = float(offset_range[0]), float(offset_range[1])
        sel = cand[(off >= lo) & (off <= hi)]
        peak = [lo, hi]
    else:
        nb = max(1, int((off.max() - off.min()) / bin_mm) + 1)
        hist, edges = np.histogram(off, bins=nb, weights=a[cand])
        k = int(np.argmax(hist))
        sel = cand[(off >= edges[k] - halfwidth_mm) & (off < edges[k + 1] + halfwidth_mm)]
        peak = [float(edges[k]), float(edges[k + 1])]
    if len(sel) < 3:
        raise RuntimeError("level_plane: selected offset band is empty")
    r = ransac_plane(c[sel], tol=tol, iters=iters, seed=seed)
    nn, cc = r["normal"], r["centroid"]
    if nn @ an < 0:
        nn = -nn
    d = (c[cand] - cc) @ nn
    sel2 = cand[np.abs(d) < 2 * tol]
    P = c[sel2]
    cc = P.mean(axis=0)
    _, _, vt = np.linalg.svd(P - cc, full_matrices=False)
    nn = vt[2] if vt[2] @ an >= 0 else -vt[2]
    d = (P - cc) @ nn
    st = residual_stats(d)
    # review m1: also report the UNTRIMMED residual (all faces in the peak offset bin,
    # before the |d| < 2*tol widen/refine), so the trimming is visible next to the gated
    # trimmed rms (RE_SPEC.md's "RMS + max" vs the noise floor; the trimmed max is
    # structurally small, see QUESTIONS SS C).
    d_all = (c[sel] - cc) @ nn
    st_all = residual_stats(d_all)
    return {"normal": nn, "centroid": cc, "faces": sel2, "n_faces": int(len(sel2)),
            "area_mm2": float(a[sel2].sum()), "offset_peak_bin": peak,
            "fit_rms_mm": st["rms"], "fit_p95_mm": st["p95"], "fit_max_mm": st["max"],
            "fit_untrimmed": {"rms": st_all["rms"], "p95": st_all["p95"], "max": st_all["max"],
                              "n_faces": st_all["n"]},
            "inlier_frac": r["inlier_frac"],
            "ransac": {"tol_mm": tol, "iters": iters, "seed": seed,
                       "inlier_frac": r["inlier_frac"]}}


def normal_vote(m: trimesh.Trimesh, n_dir: int = 6000, cone_deg: float = 3.0,
                refine_cone_deg: float = 4.0, max_iter: int = 40) -> np.ndarray:
    """Sign-free area-weighted spherical vote for the dominant flat direction
    (B02 q03_datum_full.py:24-44; golden used 6000 directions, 3 deg, refine 4 deg)."""
    N, A = m.face_normals, m.area_faces
    i = np.arange(n_dir) + 0.5
    phi = np.arccos(1 - 2 * i / n_dir)
    theta = np.pi * (1 + 5 ** 0.5) * i
    D = np.stack([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)], 1)
    D = D[D[:, 2] >= 0]
    score = np.zeros(len(D))
    cth = np.cos(np.deg2rad(cone_deg))
    for s in range(0, len(N), 100000):
        dots = np.abs(N[s:s + 100000] @ D.T)
        score += ((dots > cth) * A[s:s + 100000, None]).sum(0)
    ax = D[int(np.argmax(score))]
    for _ in range(max_iter):
        sel = np.abs(N @ ax) > np.cos(np.deg2rad(refine_cone_deg))
        Ns = N[sel] * np.sign(N[sel] @ ax)[:, None]
        v = unit((Ns * A[sel, None]).sum(0))
        if np.linalg.norm(v - ax) < 1e-13:
            return v
        ax = v
    return ax


# ----------------------------------------------------------------------------- axis
def axis_from_normals(pts: np.ndarray, nrm: np.ndarray,
                      w: np.ndarray | None = None) -> dict[str, Any]:
    """Revolve axis from the normals of a surface of revolution.
    direction d = eigenvector of the SMALLEST eigenvalue of S = sum w n n^T.
    point a = least-squares point nearest all normal lines (p_i, n_i), with its
    component along d removed (undetermined) relative to the weighted centroid.
    Quality: eigenvalue ratio w0/w1 (near 0 = well-defined axis) and the rms distance
    of the normal lines from the axis point in the plane perpendicular to d."""
    pts = np.asarray(pts, float)
    nrm = np.asarray(nrm, float)
    w = np.ones(len(pts)) if w is None else np.asarray(w, float)
    S = (nrm * w[:, None]).T @ nrm
    ev, V = np.linalg.eigh(S)
    d = V[:, 0]
    # line-to-point least squares: minimise sum w ||(I - n n^T)(a - p)||^2
    M = np.zeros((3, 3))
    b = np.zeros(3)
    for p, n, wi in zip(pts, nrm, w):
        A = np.eye(3) - np.outer(n, n)
        M += wi * A
        b += wi * (A @ p)
    # the along-axis component of M is weakly determined (every normal is perpendicular
    # to d, so M is not literally singular there, but it carries no information along d);
    # pin that component to the weighted centroid (review n1).
    cen = (pts * w[:, None]).sum(0) / w.sum()
    M2 = M + np.outer(d, d) * w.sum()
    b2 = b + d * (d @ cen) * w.sum()
    a = np.linalg.solve(M2, b2)
    # residual: distance between each normal line and the axis line
    cr = np.cross(nrm, d)
    crn = np.linalg.norm(cr, axis=1)
    ok = crn > 1e-6
    dist = np.abs(((pts[ok] - a) * cr[ok]).sum(1)) / crn[ok]
    return {"direction": d, "point": a, "eigenvalues": ev.tolist(),
            "eig_ratio": float(ev[0] / max(ev[1], 1e-12)),
            "line_dist": residual_stats(dist) if ok.any() else None}


# ----------------------------------------------------------------------------- circles
def fit_circle_kasa(xy: np.ndarray) -> dict[str, float]:
    """Kasa algebraic circle fit (dreame align.py:10-18)."""
    xy = np.asarray(xy, float)
    x, y = xy[:, 0], xy[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    sol = np.linalg.lstsq(A, x ** 2 + y ** 2, rcond=None)[0]
    cx, cy = float(sol[0]), float(sol[1])
    r = float(np.sqrt(sol[2] + cx ** 2 + cy ** 2))
    d = np.hypot(x - cx, y - cy) - r
    st = residual_stats(d)
    return {"cx": cx, "cy": cy, "r": r, "rms": st["rms"], "max": st["max"], "n": st["n"]}


def fit_circle_irls(xy: np.ndarray, w: np.ndarray | None = None, scale: float = 0.30,
                    max_iter: int = 60) -> dict[str, float]:
    """Weighted algebraic circle fit, IRLS with a Cauchy robustifier
    (B02 q03_datum_full.py:98-111; golden scale 0.30 mm, 60 iterations)."""
    Q = np.asarray(xy, float)
    W = np.ones(len(Q)) if w is None else np.asarray(w, float)
    k = fit_circle_kasa(Q)
    c2 = np.array([k["cx"], k["cy"]])
    it = 0
    for it in range(1, max_iter + 1):
        d = np.hypot(*(Q - c2).T)
        Rm = np.average(d, weights=W)
        w2 = W / (1.0 + ((d - Rm) / scale) ** 2)
        A = np.c_[2 * Q, np.ones(len(Q))] * w2[:, None]
        b = (Q ** 2).sum(1) * w2
        sol = np.linalg.lstsq(A, b, rcond=None)[0]
        cn = sol[:2]
        if np.linalg.norm(cn - c2) < 1e-10:
            c2 = cn
            break
        c2 = cn
    d = np.hypot(*(Q - c2).T)
    Rm = float(np.average(d, weights=W))
    res = d - Rm
    st = residual_stats(res)
    return {"cx": float(c2[0]), "cy": float(c2[1]), "r": Rm,
            "rms": float(np.sqrt(np.average(res ** 2, weights=W))), "max": st["max"],
            "p95": st["p95"], "n": st["n"], "iterations": it}


def fit_circle(xy: np.ndarray, method: str = "kasa", scale: float = 0.30) -> dict[str, float]:
    if method == "kasa":
        return fit_circle_kasa(xy)
    if method == "irls":
        return fit_circle_irls(xy, scale=scale)
    raise ValueError(f"unknown circle method {method!r} (kasa|irls)")


# ----------------------------------------------------------------------------- sections
def polygon_area(xy: np.ndarray) -> float:
    x, y = xy[:, 0], xy[:, 1]
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def section_polylines(m: trimesh.Trimesh, origin: Sequence[float], normal: Sequence[float],
                      quant: float = 1e-5) -> list[tuple[np.ndarray, bool]]:
    """Chain the segments of a plane section into polylines without networkx.
    Returns (points, closed) pairs. Endpoints are matched after quantising to `quant` mm."""
    seg = trimesh.intersections.mesh_plane(m, plane_normal=normal, plane_origin=origin)
    if len(seg) == 0:
        return []
    keys = np.round(seg.reshape(-1, 3) / quant).astype(np.int64)
    _, inv = np.unique(keys, axis=0, return_inverse=True)
    inv = inv.reshape(-1, 2)
    pts = np.zeros((inv.max() + 1, 3))
    pts[inv.ravel()] = seg.reshape(-1, 3)
    adj: dict[int, list[int]] = {}
    for si, (a, b) in enumerate(inv):
        if a == b:
            continue
        adj.setdefault(int(a), []).append(si)
        adj.setdefault(int(b), []).append(si)
    used = np.zeros(len(inv), bool)
    out: list[tuple[np.ndarray, bool]] = []
    # start from open ends first (degree 1), then from any remaining segment
    starts = [v for v, e in sorted(adj.items()) if len(e) == 1] + sorted(adj)
    for v0 in starts:
        for si0 in adj[v0]:
            if used[si0]:
                continue
            chain = [v0]
            v, si = v0, si0
            while True:
                used[si] = True
                a, b = inv[si]
                v = int(b) if int(a) == v else int(a)
                chain.append(v)
                nxt = [e for e in adj[v] if not used[e]]
                if not nxt:
                    break
                si = nxt[0]
            closed = chain[0] == chain[-1] and len(chain) > 3
            out.append((pts[chain], closed))
    return out


def closed_loops_at_z(m: trimesh.Trimesh, z: float, close_tol: float = 0.2,
                      min_pts: int = 8) -> list[np.ndarray]:
    """Closed XY loops of the section z = const (mesh in datum frame).
    Golden closure tolerance 0.2 mm, >= 8 points (dreame align.py:66)."""
    loops = []
    for p, _closed in section_polylines(m, [0, 0, z], [0, 0, 1]):
        xy = p[:, :2]
        if len(xy) < min_pts or np.linalg.norm(xy[0] - xy[-1]) > close_tol:
            continue
        loops.append(xy[:-1] if np.allclose(xy[0], xy[-1]) else xy)
    return loops


# ----------------------------------------------------------------------------- CLI
def _load(path: Path) -> trimesh.Trimesh:
    m = trimesh.load_mesh(path, process=False)
    if not isinstance(m, trimesh.Trimesh):
        raise SystemExit(f"{path}: not a single triangle mesh")
    return m


def _vec(s: str) -> list[float]:
    v = [float(x) for x in s.split(",")]
    if len(v) != 3:
        raise argparse.ArgumentTypeError("expected x,y,z")
    return v


def _write(out: Path | None, obj: dict[str, Any]) -> None:
    txt = json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(txt)
    print(txt)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=0)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("planes", help="dominant-plane survey")
    p.add_argument("mesh", type=Path)
    p.add_argument("--angle-deg", type=float, default=3.0)
    p.add_argument("--off-bin", type=float, default=0.08)
    p.add_argument("--min-area", type=float, default=2.0)
    p.add_argument("--top", type=int, default=8)
    p.add_argument("--tol", type=float, default=0.05)
    p.add_argument("--out", type=Path)

    p = sub.add_parser("plane", help="level-plane fit near an approximate normal")
    p.add_argument("mesh", type=Path)
    p.add_argument("--approx-normal", type=_vec, required=True)
    p.add_argument("--cone-deg", type=float, default=10.0)
    p.add_argument("--tol", type=float, default=0.05)
    p.add_argument("--offset-range", type=float, nargs=2)
    p.add_argument("--out", type=Path)

    p = sub.add_parser("axis", help="revolve axis from normals of faces nearly perpendicular to an approximate axis")
    p.add_argument("mesh", type=Path)
    p.add_argument("--approx-axis", type=_vec, required=True)
    p.add_argument("--perp-max", type=float, default=0.30,
                   help="keep faces with |n.axis| < this (golden B02 q03 used 0.30)")
    p.add_argument("--iters", type=int, default=3)
    p.add_argument("--out", type=Path)

    p = sub.add_parser("noise", help="noise floor on a clean primitive")
    p.add_argument("mesh", type=Path, help="mesh in the frame the region is specified in")
    p.add_argument("--plane-normal", type=_vec, help="approx normal of a clean flat")
    p.add_argument("--offset-range", type=float, nargs=2)
    p.add_argument("--circle-z", type=float, help="datum-frame z of a clean circular section")
    p.add_argument("--r-range", type=float, nargs=2, help="radius window for the circle loop")
    p.add_argument("--region-desc", required=True, help="what the primitive is (goes in the JSON)")
    p.add_argument("--out", type=Path)

    a = ap.parse_args(argv)
    m = _load(a.mesh)
    hdr = json_header(f"datum_fit.{a.cmd}", "datum_fit.py", {str(a.mesh): sha256_file(a.mesh)}, a.seed)

    if a.cmd == "planes":
        res = []
        for i, pl in enumerate(dominant_planes(m, a.angle_deg, a.off_bin, a.min_area, a.top)):
            r = ransac_plane(m.triangles_center[pl["faces"]], tol=a.tol, seed=a.seed)
            n = r["normal"] if r["normal"] @ np.array(pl["normal"]) >= 0 else -r["normal"]
            res.append({"id": i, "area_mm2": pl["area"], "n_faces": pl["n_faces"],
                        "normal": n.round(6).tolist(), "centroid": r["centroid"].round(4).tolist(),
                        "inlier_frac": r["inlier_frac"], "fit_rms_mm": r["fit_rms_mm"],
                        "fit_max_mm": r["fit_max_mm"]})
        _write(a.out, {**hdr, "note": "candidates only; choose the FUNCTIONAL surface, not the largest",
                       "planes": res})
    elif a.cmd == "plane":
        r = level_plane(m, a.approx_normal, a.cone_deg, a.tol, offset_range=a.offset_range, seed=a.seed)
        r.pop("faces")
        _write(a.out, {**hdr, "plane": r})
    elif a.cmd == "axis":
        ax = unit(a.approx_axis)
        res: dict[str, Any] = {}
        for _ in range(a.iters):
            sel = np.abs(m.face_normals @ ax) < a.perp_max
            if sel.sum() < 10:
                raise SystemExit("axis: fewer than 10 faces perpendicular to the approximate axis")
            res = axis_from_normals(m.triangles_center[sel], m.face_normals[sel], m.area_faces[sel])
            d = res["direction"]
            ax = d if d @ ax >= 0 else -d
        res["direction"] = ax
        res["n_faces"] = int(sel.sum())
        _write(a.out, {**hdr, "axis": res})
    elif a.cmd == "noise":
        if a.plane_normal is not None:
            r = level_plane(m, a.plane_normal, offset_range=a.offset_range, seed=a.seed)
            out = {"value": r["fit_rms_mm"], "p95_mm": r["fit_p95_mm"], "max_mm": r["fit_max_mm"],
                   "method": f"rms of RANSAC+SVD plane on {a.region_desc} ({r['n_faces']} faces)"}
        elif a.circle_z is not None and a.r_range:
            loops = closed_loops_at_z(m, a.circle_z)
            best = None
            for xy in loops:
                c = fit_circle_irls(xy)
                if a.r_range[0] <= c["r"] <= a.r_range[1] and (best is None or c["rms"] < best["rms"]):
                    best = c
            if best is None:
                raise SystemExit("noise: no closed loop in the radius window at that z")
            out = {"value": best["rms"], "p95_mm": best["p95"], "max_mm": best["max"],
                   "method": f"rms of IRLS circle on {a.region_desc} at z={a.circle_z} (n={best['n']})",
                   "circle": best}
        else:
            raise SystemExit("noise: give --plane-normal or --circle-z with --r-range")
        _write(a.out, {**hdr, "scan_noise_mm": out})
    return 0


if __name__ == "__main__":
    sys.exit(main())
