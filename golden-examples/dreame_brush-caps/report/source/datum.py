"""Datum analysis: dominant planes (normal clustering + offset clustering + RANSAC refine),
revolve-axis fit from normals. Prints a summary and writes <name>_planes.json."""
import sys, json
from pathlib import Path
import numpy as np, trimesh

def ransac_plane(pts, tol, iters=300, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(iters):
        idx = rng.choice(len(pts), 3, replace=False)
        p0, p1, p2 = pts[idx]
        n = np.cross(p1 - p0, p2 - p0)
        if np.linalg.norm(n) < 1e-9: continue
        n /= np.linalg.norm(n)
        d = (pts - p0) @ n
        inl = np.abs(d) < tol
        if best is None or inl.sum() > best[0]:
            best = (inl.sum(), n, p0, inl)
    _, n, p0, inl = best
    # refine by SVD on inliers
    P = pts[inl]; c = P.mean(axis=0)
    u, s, vt = np.linalg.svd(P - c, full_matrices=False)
    n = vt[2]; d = (P - c) @ n
    return n, c, inl.sum() / len(pts), np.sqrt((d**2).mean()), np.abs(d).max()

def dominant_planes(m, angle_deg=3.0, off_bin=0.08, min_area=2.0, top=8):
    n = m.face_normals; a = m.area_faces; c = m.triangles_center
    groups = trimesh.grouping.group_vectors(n, angle=np.radians(angle_deg), include_negative=False)[1]
    out = []
    for g in groups:
        if a[g].sum() < min_area: continue
        nn = n[g].mean(axis=0); nn /= np.linalg.norm(nn)
        off = c[g] @ nn
        # 1D clustering by offset
        order = np.argsort(off); off_s = off[order]; g_s = np.asarray(g)[order]
        cuts = np.where(np.diff(off_s) > off_bin)[0] + 1
        for seg in np.split(np.arange(len(g_s)), cuts):
            fi = g_s[seg]
            area = a[fi].sum()
            if area < min_area: continue
            out.append({"normal": nn.round(5).tolist(), "offset": float(off[order][seg].mean()),
                        "area": float(area), "centroid": c[fi].mean(axis=0).round(3).tolist(),
                        "faces": fi.tolist()})
    out.sort(key=lambda d: -d["area"])
    return out[:top]

def axis_from_normals(pts, nrm):
    """Least-squares revolve axis: direction = smallest eigvec of sum(I - n n^T)... (all normals ⟂ axis);
    point = LS solution of lines (p_i, n_i) intersection."""
    M = np.zeros((3, 3)); b = np.zeros(3)
    for p, n in zip(pts, nrm):
        A = np.eye(3) - np.outer(n, n)
        M += A; b += A @ p
    # direction: normals are perpendicular to axis -> axis = eigvec of min eigenvalue of sum(n n^T)
    S = nrm.T @ nrm
    w, v = np.linalg.eigh(S); d = v[:, 0]
    # point: minimize sum ||(I - n n^T)(a - p)||^2 restricted to plane ⟂ d
    a = np.linalg.lstsq(M + 1e-9 * np.eye(3), b, rcond=None)[0]
    a = a - (a @ d) * d * 0  # keep
    return d, a, w

if __name__ == "__main__":
    mesh_path, name = Path(sys.argv[1]), sys.argv[2]
    m = trimesh.load_mesh(mesh_path, process=False)
    print("faces", len(m.faces), "bounds", m.bounds.round(3).tolist(), "extents", m.extents.round(3).tolist())
    planes = dominant_planes(m)
    res = []
    for i, p in enumerate(planes):
        pts = m.triangles_center[p["faces"]]
        n, c, frac, rms, mx = ransac_plane(pts, tol=0.05)
        if n @ np.array(p["normal"]) < 0: n = -n
        print(f"P{i}: area={p['area']:.2f} n={n.round(4)} c={c.round(3)} inl={frac:.2f} rms={rms:.4f} max={mx:.3f}")
        res.append({"id": i, "area": p["area"], "normal": n.tolist(), "centroid": c.tolist(),
                    "inlier_frac": float(frac), "rms": float(rms), "max": float(mx)})
    Path(f"{name}_planes.json").write_text(json.dumps(res, indent=1))
