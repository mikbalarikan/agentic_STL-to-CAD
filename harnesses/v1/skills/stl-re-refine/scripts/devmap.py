"""devmap.py - signed scan<->CAD deviation maps and red clusters for the refine loop (harness v1).

Builder self-check only (CHK-INDEP): the official grade stays with stl-re-verify in a fresh
context. Distances follow v0 deviation_gate.dist_to_mesh: KD candidates, then the exact
point-to-triangle distance.

Sign convention (scan -> CAD):
  + scan point OUTSIDE the CAD: material missing in the CAD  -> an add feature
  - scan point INSIDE the CAD:  extra material in the CAD    -> a cut feature
The sign comes from the closest triangle's outward normal.

CAD -> scan: unsigned distance from CAD surface samples to the scan. A CAD point far from any
scan point is either CAD-only material (a phantom feature) or a surface the scanner could not
reach. The sky test in stl-re-verify/scripts/observability.py separates the two in the final
gate. Inside the loop the CAD->scan term only guards against tools that overshoot the scan.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class ScanSample:
    P: np.ndarray          # (n,3) points in the datum frame
    N: np.ndarray          # (n,3) unit normals of the scan faces
    area_per_pt: float     # scan area represented by one sample (mm^2)
    spacing: float         # mean sample spacing (mm)
    noise: float           # scan noise floor (mm) from alignment.json


def load_alignment(path: Path) -> tuple[np.ndarray, float]:
    a = json.loads(Path(path).read_text(encoding="utf-8"))
    T = np.asarray(a["matrix_4x4"], float)
    nz = a.get("scan_noise_mm")
    noise = float(nz["value"] if isinstance(nz, dict) else nz) if nz is not None else 0.05
    return T, noise


def sample_scan(scan: Path, alignment: Path, n: int = 200_000, seed: int = 0,
                cache: Path | None = None) -> ScanSample:
    """Area-uniform samples of the scan in the datum frame (seeded, cached as .npz)."""
    T, noise = load_alignment(alignment)
    if cache is not None and cache.is_file():
        z = np.load(cache)
        if int(z["n"]) == n and int(z["seed"]) == seed:
            return ScanSample(z["P"], z["N"], float(z["a"]), float(z["s"]), noise)
    import trimesh
    m = trimesh.load(str(scan), force="mesh", process=True)
    m.apply_transform(T)
    P, fi = trimesh.sample.sample_surface(m, n, seed=seed)
    N = m.face_normals[fi]
    area = float(m.area)
    a = area / n
    s = float(np.sqrt(a))
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache, P=P, N=N, a=a, s=s, n=n, seed=seed)
    return ScanSample(np.asarray(P), np.asarray(N), a, s, noise)


def body_mesh(body: Any, tol: float = 0.01, ang: float = 0.1):
    """Tessellate a build123d shape into a trimesh (datum frame)."""
    import trimesh
    verts, tris = body.tessellate(tol, ang)
    V = np.array([[v.X, v.Y, v.Z] for v in verts], float)
    F = np.asarray(tris, int)
    return trimesh.Trimesh(V, F, process=True)


def signed_s2c(P: np.ndarray, cad: Any, k: int = 4, n_samp: int = 400_000, seed: int = 0,
               chunk: int = 50_000) -> np.ndarray:
    """Signed distance scan point -> CAD surface (+ outside CAD, - inside)."""
    import trimesh
    from scipy.spatial import cKDTree
    samp, fid = trimesh.sample.sample_surface(cad, n_samp, seed=seed)
    tree = cKDTree(samp)
    tris = cad.triangles
    fn = cad.face_normals
    out = np.empty(len(P))
    for c0 in range(0, len(P), chunk):
        Q = P[c0:c0 + chunk]
        _, idx = tree.query(Q, k=k)
        cand = fid[idx]
        Qr = np.repeat(Q, k, axis=0)
        cp = trimesh.triangles.closest_point(tris[cand.reshape(-1)], Qr)
        d = np.linalg.norm(cp - Qr, axis=1).reshape(-1, k)
        j = d.argmin(1)
        r = np.arange(len(Q))
        best = d[r, j]
        cpb = cp.reshape(-1, k, 3)[r, j]
        nb = fn[cand[r, j]]
        sgn = np.sign(np.einsum("ij,ij->i", Q - cpb, nb))
        sgn[sgn == 0] = 1.0
        out[c0:c0 + chunk] = best * sgn
    return out


def c2s(cad: Any, scanP: np.ndarray, n: int = 100_000, seed: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """CAD surface samples and their unsigned distance to the scan samples (nearest point)."""
    import trimesh
    from scipy.spatial import cKDTree
    S, _ = trimesh.sample.sample_surface(cad, n, seed=seed)
    d, _ = cKDTree(scanP).query(S, k=1)
    return np.asarray(S), d


def clusters(P: np.ndarray, d: np.ndarray, thr: float, eps: float, min_pts: int) -> list[dict[str, Any]]:
    """Connected red regions, split by sign. Returns clusters sorted by size (largest first),
    each with point indices into P."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree
    out = []
    for sgn in (1, -1):
        sel = np.where(sgn * d > thr)[0]
        if len(sel) < min_pts:
            continue
        Q = P[sel]
        pairs = cKDTree(Q).query_pairs(eps, output_type="ndarray")
        if len(pairs) == 0:
            continue
        g = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(Q), len(Q)))
        _, lab = connected_components(g, directed=False)
        ids, cnt = np.unique(lab, return_counts=True)
        for i, c in zip(ids, cnt):
            if c < min_pts:
                continue
            idx = sel[lab == i]
            out.append({"sign": sgn, "idx": idx, "n": int(c),
                        "centroid": P[idx].mean(0).round(3).tolist(),
                        "bbox": [P[idx].min(0).round(3).tolist(), P[idx].max(0).round(3).tolist()],
                        "d_med": float(np.median(np.abs(d[idx]))), "d_max": float(np.abs(d[idx]).max())})
    out.sort(key=lambda c: -c["n"] * c["d_med"])
    return out


def metrics(d_s2c: np.ndarray, d_c2s: np.ndarray, band: float, clip: float = 2.0) -> dict[str, float]:
    """Loop objective. J is the clipped mean |d| scan->CAD plus half the clipped mean CAD->scan
    (CAD-only material counts against a hypothesis). Lower is better."""
    a = np.abs(d_s2c)
    js = float(np.minimum(a, clip).mean())
    jc = float(np.minimum(d_c2s, clip).mean())
    return {"J": js + 0.5 * jc, "s2c_mean_clip": js, "c2s_mean_clip": jc,
            "s2c_p50": float(np.percentile(a, 50)), "s2c_p95": float(np.percentile(a, 95)),
            "s2c_max": float(a.max()), "s2c_within_band": float((a <= band).mean()),
            "c2s_p95": float(np.percentile(d_c2s, 95))}
