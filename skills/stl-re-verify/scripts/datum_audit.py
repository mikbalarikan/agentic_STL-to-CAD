#!/usr/bin/env python3
"""Independent datum audit (REPORT-ONLY): re-derive the datum frame from the raw scan with QA's
own code and compare it with intake/alignment.json.

Provenance: generalised from golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q03_datum_full.py
  - sign-free Fibonacci normal vote (6000 dirs, 3 deg cone, area weighted) + refine    (q03:25-45)
  - flat-band height histogram (0.05 mm bins) -> biggest band -> SVD plane             (q03:47-66)
  - IRLS Cauchy-robust algebraic circle fit (scale 0.30) on wall faces perpendicular
    to the axis, inner/outer wall separated by the sign of n.r_hat                      (q03:68-100)
  - k-fold Fourier phase of the angular mass in a radial band, labelling tested mod 360/k,
    per-feature circular-mean refinement                                                (q03:102-121)
  - comparison: rotation difference, point disagreement over 60k scan vertices (seed 0) (q03:123-150)
Generalised: part-specific radius bands, the 3-fold order and the primary type move into an
audit spec JSON; axis-primary parts use the smallest eigenvector of sum(n n^T) (the corrected
eigen form, analysis/SYNTHESIS.md §3 row 1); an origin-offset metric is added because
RE_SPEC states the band as angle + origin offset while B02 reported point disagreement
(QUESTIONS.md Q2).

Independence statement written into the output: the builder's matrix is used ONLY to pick which
faces belong to a named region (selection); every fit is done by this script on raw-scan data.

Reference band ≤0.3 deg / ≤0.15 mm is RE_SPEC.md:241 and is REPORT-ONLY (QUESTIONS.md Q2,
run-contract.md §9). Both approved OOM goldens exceeded it: B02 0.429 deg / 0.451 mm max point
disagreement; P03 0.154 deg / 0.600 mm (analysis/golden/OOM-B02.md §3, OOM-P03.md §3).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, load_matrix, load_mesh, merge_into_gate, read_json, rot_angle_deg, select, write_json  # noqa: E402,E501

TOOL = "datum_audit.py"
REF_BAND = {"angle_deg": 0.3, "origin_offset_mm": 0.15, "source": "baseline/oomwoo-re-pipeline/RE_SPEC.md:241"}


def fib_dirs(n: int) -> np.ndarray:
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = np.pi * (1 + 5 ** 0.5) * i
    D = np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)
    return D[D[:, 2] >= 0]


def plane_by_vote(N: np.ndarray, A: np.ndarray, C: np.ndarray, V: np.ndarray, F: np.ndarray,
                  cone_deg: float, band_mm: float, cand: np.ndarray) -> dict[str, Any]:
    """Biggest area-weighted flat population among candidate faces (q03 steps 1-2)."""
    D = fib_dirs(6000)
    score = np.zeros(len(D))
    Nc, Ac = N[cand], A[cand]
    for s in range(0, len(Nc), 100_000):
        dots = np.abs(Nc[s:s + 100_000] @ D.T)
        score += ((dots > np.cos(np.deg2rad(cone_deg))) * Ac[s:s + 100_000, None]).sum(0)
    ax = D[int(np.argmax(score))]
    sel = cand.copy()
    for _ in range(40):
        sel = cand & (np.abs(N @ ax) > np.cos(np.deg2rad(cone_deg + 1.0)))
        Ns = N[sel] * np.sign(N[sel] @ ax)[:, None]
        v = (Ns * A[sel, None]).sum(0)
        v /= np.linalg.norm(v)
        if np.linalg.norm(v - ax) < 1e-13:
            ax = v
            break
        ax = v
    e1 = np.array([1.0, 0, 0]) if abs(ax[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(ax, e1)
    u /= np.linalg.norm(u)
    w = np.cross(ax, u)
    h = C @ np.stack([u, w, ax]).T[:, 2]
    bins = np.arange(h[sel].min(), h[sel].max() + 0.05, 0.05)
    hist, edges = np.histogram(h[sel], bins=bins, weights=A[sel])
    h0 = edges[int(np.argmax(hist))] + 0.025
    band = sel & (np.abs(h - h0) < band_mm)
    return svd_plane(V[F[band]].reshape(-1, 3), ax) | {"faces": int(band.sum()), "method": "normal vote + height histogram"}


def svd_plane(P: np.ndarray, hint: np.ndarray) -> dict[str, Any]:
    cen = P.mean(0)
    _, _, Vt = np.linalg.svd(P - cen, full_matrices=False)
    n = Vt[2] / np.linalg.norm(Vt[2])
    if n @ hint < 0:
        n = -n
    res = (P - cen) @ n
    return {"normal": n, "point": cen, "rms": float(res.std()), "max": float(np.abs(res).max())}


def axis_from_normals(N: np.ndarray, A: np.ndarray, hint: np.ndarray) -> np.ndarray:
    """Cylinder axis = eigenvector of the SMALLEST eigenvalue of sum(a n n^T) (SYNTHESIS §3)."""
    M = (N * A[:, None]).T @ N
    w, V = np.linalg.eigh(M)
    ax = V[:, 0]
    return ax if ax @ hint >= 0 else -ax


def circle_irls(Q: np.ndarray, W: np.ndarray, scale: float = 0.30, iters: int = 60) -> tuple[np.ndarray, float, float]:
    c2 = Q.mean(0) * 0.0 + np.average(Q, axis=0, weights=W)
    for _ in range(iters):
        d = np.hypot(*(Q - c2).T)
        Rm = np.average(d, weights=W)
        w2 = W / (1.0 + ((d - Rm) / scale) ** 2)
        Am = np.c_[2 * Q, np.ones(len(Q))] * w2[:, None]
        b = (Q ** 2).sum(1) * w2
        sol, *_ = np.linalg.lstsq(Am, b, rcond=None)
        if np.linalg.norm(sol[:2] - c2) < 1e-10:
            c2 = sol[:2]
            break
        c2 = sol[:2]
    d = np.hypot(*(Q - c2).T)
    Rm = float(np.average(d, weights=W))
    return c2, Rm, float(np.sqrt(np.average((d - Rm) ** 2, weights=W)))


def basis(ax: np.ndarray) -> np.ndarray:
    e1 = np.array([1.0, 0, 0]) if abs(ax[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(ax, e1)
    u /= np.linalg.norm(u)
    return np.stack([u, np.cross(ax, u), ax])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scan", required=True, help="raw scan (full-res preferred)")
    ap.add_argument("--align", required=True, help="builder's alignment.json (compared, not trusted)")
    ap.add_argument("--spec", required=True, help="audit spec JSON (see references/gate-protocol.md §2)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-compare", type=int, default=60000)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gate", help="merge into gate.json under 'datum_audit'")
    a = ap.parse_args(argv)

    spec = read_json(a.spec)
    m = load_mesh(a.scan, process=False)
    m.merge_vertices()                   # unwelded STL (B02 q20_tier2.py:27); normals left as scanned
    Tb = load_matrix(a.align)
    N, A, C, V, F = m.face_normals, m.area_faces, m.triangles_center, m.vertices, m.faces
    Cb = C @ Tb[:3, :3].T + Tb[:3, 3]      # builder frame: region SELECTION only
    Nb = N @ Tb[:3, :3].T
    zb = Tb[:3, :3].T @ np.array([0, 0, 1.0])  # builder +Z in raw coords (sign hint only)
    xb = Tb[:3, :3].T @ np.array([1.0, 0, 0])
    out: dict[str, Any] = {"independence": "builder matrix used only to select named regions; all fits are QA code on raw scan"}

    # ---- primary
    pr = spec["primary"]
    cand = select(pr.get("region", {"all": True}), Cb, Nb)
    if pr["type"] == "plane":
        if pr.get("method", "region") == "vote":
            pl = plane_by_vote(N, A, C, V, F, pr.get("cone_deg", 3.0), pr.get("band_mm", 0.30), cand)
        else:
            cone = np.abs(Nb[:, 2]) > np.cos(np.radians(pr.get("cone_deg", 10.0)))
            sel = cand & cone
            pl = svd_plane(V[F[sel]].reshape(-1, 3), zb) | {"faces": int(sel.sum()), "method": "region SVD"}
        ax, p0 = pl["normal"], pl["point"]
        out["primary"] = {"type": "plane", "method": pl["method"], "faces": pl["faces"],
                          "fit_rms_mm": pl["rms"], "fit_max_mm": pl["max"]}
    else:                                  # axis-primary
        sel = cand
        ax = axis_from_normals(N[sel], A[sel], zb)
        p0 = None
        out["primary"] = {"type": "axis", "method": "smallest eigenvector of sum(a n n^T)", "faces": int(sel.sum())}
    R0 = basis(ax)

    # ---- level (axis-primary parts: a named plane sets z=0)
    lv = spec.get("level")
    if lv:
        s_ = select(lv["region"], Cb, Nb)
        P = V[F[s_]].reshape(-1, 3)
        p0 = P.mean(0) if p0 is None else p0
        h = float(np.median(P @ ax))
        p0 = p0 + (h - p0 @ ax) * ax
        out["level"] = {"faces": int(s_.sum()), "method": "median height along audited axis"}
    if p0 is None:
        raise SystemExit("axis-primary spec needs a 'level' region to fix z=0")

    # ---- axis position
    po = spec.get("position", {"type": "none"})
    origin = p0.copy()
    if po["type"] == "circle":
        s_ = select(po["region"], Cb, Nb) & (np.abs(N @ ax) < po.get("perp_max_dot", 0.30))
        Cl = (C - p0) @ R0.T
        Q, W = Cl[s_][:, :2], A[s_]
        c_rough, _, _ = circle_irls(Q, W, po.get("cauchy_scale_mm", 0.30))
        rh = (Q - c_rough) / np.maximum(np.hypot(*(Q - c_rough).T), 1e-9)[:, None]
        ndr = ((N[s_] @ R0.T)[:, :2] * rh).sum(1)
        # Normal orientation of an open scan is not trustworthy (volume sign of a non-watertight
        # mesh is meaningless), so fix the convention empirically off the outermost faces of the
        # selection, as q03:80-84 did off the outer skirt.
        rq = np.hypot(*(Q - c_rough).T)
        ref = rq >= np.percentile(rq, 90)
        outer_sign = np.sign(np.average(ndr[ref], weights=W[ref])) or 1.0
        wall = po.get("wall", "any")
        keep = (np.ones(len(Q), bool) if wall == "any"
                else (np.sign(ndr) == -outer_sign) if wall == "inner" else (np.sign(ndr) == outer_sign))
        c2, Rm, rms = circle_irls(Q[keep], W[keep], po.get("cauchy_scale_mm", 0.30))
        origin = p0 + c2[0] * R0[0] + c2[1] * R0[1]
        out["position"] = {"type": "circle", "wall": wall, "faces": int(keep.sum()), "R_mm": Rm,
                           "fit_rms_mm": rms, "method": "IRLS Cauchy circle (q03:88-100)"}
    elif po["type"] == "axis_line":        # axis-primary: least-squares point on the axis
        s_ = select(po["region"], Cb, Nb)
        Cl = (C[s_] - p0) @ R0.T
        c2, Rm, rms = circle_irls(Cl[:, :2], A[s_], po.get("cauchy_scale_mm", 0.30))
        origin = p0 + c2[0] * R0[0] + c2[1] * R0[1]
        out["position"] = {"type": "axis_line", "faces": int(s_.sum()), "R_mm": Rm, "fit_rms_mm": rms}

    # ---- clock
    ck = spec.get("clock", {"type": "none"})
    xdir = xb - (xb @ ax) * ax             # default: builder clock (declared as NOT audited)
    clock_audited = False
    if ck["type"] == "fourier":
        k = int(ck["order"])
        Vl = (V - origin) @ R0.T
        Vbl = V @ Tb[:3, :3].T + Tb[:3, 3]
        rs = select(ck["region"], Vbl)
        th = np.degrees(np.arctan2(Vl[rs, 1], Vl[rs, 0]))
        ck_c = np.exp(1j * k * np.radians(th)).sum()
        ph = math.degrees(np.angle(ck_c)) / k
        # labelling mod 360/k: pick the candidate nearest the builder's +X (q03:131-139 tried all)
        bx = math.degrees(math.atan2(xb @ R0[1], xb @ R0[0]))
        cands = [ph + j * 360.0 / k for j in range(k)]
        best = min(cands, key=lambda c: abs(((c - bx + 180) % 360) - 180))
        d = ((th - best + 180) % 360) - 180
        s = np.abs(d) < ck.get("refine_window_deg", 25.0)
        best += math.degrees(np.angle(np.exp(1j * np.radians(d[s])).sum()))
        best += float(ck.get("offset_deg", 0.0))
        xdir = math.cos(math.radians(best)) * R0[0] + math.sin(math.radians(best)) * R0[1]
        clock_audited = True
        out["clock"] = {"type": "fourier", "order": k, "phase_deg_local": best,
                        "order_strength": float(abs(ck_c) / max(rs.sum(), 1))}
    elif ck["type"] == "plane_normal":
        s_ = select(ck["region"], Cb, Nb)
        pl = svd_plane(V[F[s_]].reshape(-1, 3), xb)
        xdir = pl["normal"] - (pl["normal"] @ ax) * ax
        clock_audited = True
        out["clock"] = {"type": "plane_normal", "faces": int(s_.sum()), "fit_rms_mm": pl["rms"]}
    else:
        out["clock"] = {"type": "none", "note": "clock not audited; builder clock adopted"}
    xdir /= np.linalg.norm(xdir)
    R = np.stack([xdir, np.cross(ax, xdir), ax])
    Tq = np.eye(4)
    Tq[:3, :3], Tq[:3, 3] = R, -R @ origin

    # ---- compare
    rng = np.random.default_rng(a.seed)
    smp = V[rng.choice(len(V), min(a.n_compare, len(V)), replace=False)]
    dq = smp @ Tq[:3, :3].T + Tq[:3, 3]
    db = smp @ Tb[:3, :3].T + Tb[:3, 3]
    dd = np.linalg.norm(dq - db, axis=1)
    o_b = Tb[:3, :3] @ origin + Tb[:3, 3]  # QA origin expressed in the builder's frame
    ang = rot_angle_deg(Tq[:3, :3] @ Tb[:3, :3].T)
    ax_ang = float(np.degrees(np.arccos(np.clip(ax @ zb, -1, 1))))
    res = {
        "angle_deg": ang, "axis_angle_deg": ax_ang, "clock_audited": clock_audited,
        "origin_offset_mm": float(np.linalg.norm(o_b)), "origin_offset_vec_mm": o_b.tolist(),
        "point_disagreement_mean_mm": float(dd.mean()),
        "point_disagreement_p95_mm": float(np.percentile(dd, 95)),
        "point_disagreement_max_mm": float(dd.max()),
        "reference_band": "≤0.3° / ≤0.15 mm (RE_SPEC.md:241)", "reference": REF_BAND,
        "within_reference": bool(ang <= 0.3 and np.linalg.norm(o_b) <= 0.15),
        "blocking": False,
        "note": "REPORT-ONLY (QUESTIONS.md Q2). Golden precedent: B02 0.429°/0.451 mm max and P03 "
                "0.154°/0.600 mm were both approved with this recorded.",
        "T_qa": Tq.tolist(),
    }
    out.update(res)
    full = {**header("datum_audit", TOOL, [a.scan, a.align, a.spec], a.seed), **out}
    write_json(a.out, full)
    if a.gate:
        merge_into_gate(a.gate, "datum_audit", full)
    print(f"datum audit: rot diff {ang:.4f} deg (axis {ax_ang:.4f}) | origin offset {res['origin_offset_mm']:.4f} mm | "
          f"points mean {dd.mean():.4f} p95 {res['point_disagreement_p95_mm']:.4f} max {dd.max():.4f} mm | "
          f"{'within' if res['within_reference'] else 'OUTSIDE'} RE_SPEC reference (report-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
