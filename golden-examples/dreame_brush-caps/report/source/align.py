"""F00 datum: level on the dominant plane near an approximate normal, pin origin on the
central bore axis (circle centres of Z-sections), save aligned meshes + alignment.json,
and plot (a) Z-section outline stack and (b) the (r,z) half-profile density."""
import sys, json
from pathlib import Path
import numpy as np, trimesh
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datum import ransac_plane

def fit_circle(xy):
    """Kasa algebraic circle fit -> (cx, cy, r, rms)."""
    x, y = xy[:, 0], xy[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x**2 + y**2
    sol = np.linalg.lstsq(A, b, rcond=None)[0]
    cx, cy = sol[0], sol[1]; r = np.sqrt(sol[2] + cx**2 + cy**2)
    d = np.sqrt((x - cx)**2 + (y - cy)**2) - r
    return cx, cy, r, np.sqrt((d**2).mean())

def level_transform(m, approx_n, ang_deg=10.0, tol=0.05):
    approx_n = np.asarray(approx_n, float); approx_n /= np.linalg.norm(approx_n)
    n = m.face_normals; c = m.triangles_center; a = m.area_faces
    cand = np.where(n @ approx_n > np.cos(np.radians(ang_deg)))[0]
    off = c[cand] @ approx_n
    hist, edges = np.histogram(off, bins=int((off.max() - off.min()) / 0.1) + 1, weights=a[cand])
    k = np.argmax(hist); sel = cand[(off >= edges[k] - 0.15) & (off < edges[k + 1] + 0.15)]
    nn, cc, frac, rms, mx = ransac_plane(c[sel], tol=tol)
    if nn @ approx_n < 0: nn = -nn
    # widen: all candidate faces within tol of the refined plane
    d = (c[cand] - cc) @ nn
    sel2 = cand[np.abs(d) < 2 * tol]
    P = c[sel2]; cc = P.mean(axis=0)
    u, s, vt = np.linalg.svd(P - cc, full_matrices=False); nn = vt[2]
    if nn @ approx_n < 0: nn = -nn
    d = (P - cc) @ nn
    return nn, cc, dict(faces=int(len(sel2)), area=float(a[sel2].sum()), rms=float(np.sqrt((d**2).mean())), max=float(np.abs(d).max()))

if __name__ == "__main__":
    mesh_path, name = Path(sys.argv[1]), sys.argv[2]
    approx = [float(v) for v in sys.argv[3].split(",")]
    r_hint = float(sys.argv[4]); rms_lim = float(sys.argv[5]); r_tol = float(sys.argv[6]); zlo, zhi = [float(v) for v in sys.argv[7].split(",")]; clock_mode = sys.argv[8] if len(sys.argv) > 8 else "none"
    m = trimesh.load_mesh(mesh_path, process=True)
    # keep the largest connected body only (scan fragments off)
    parts = m.split(only_watertight=False)
    m = max(parts, key=lambda p: len(p.faces)); print("bodies", len(parts), "kept faces", len(m.faces))
    nn, cc, fit = level_transform(m, approx)
    print("plane fit:", fit, "normal", nn.round(5).tolist())
    T1 = trimesh.geometry.align_vectors(nn, [0, 0, 1])
    m.apply_transform(T1)
    z_top = (T1[:3, :3] @ cc + T1[:3, 3])[2]
    T2 = np.eye(4); T2[2, 3] = -z_top
    m.apply_transform(T2)
    # sections along Z: find the bore (loop with small area near part centre)
    z0, z1 = m.bounds[0][2], m.bounds[1][2]
    zs = np.linspace(z0 + 0.15, z1 - 0.15, 25)
    ctr_xy = m.bounds.mean(axis=0)[:2]
    bore = []
    all_loops = []
    from shapely.geometry import Polygon as _P
    for z in zs:
        s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if s is None: continue
        for seg in s.discrete:
            xy = np.asarray(seg)[:, :2]
            if len(xy) < 8 or np.linalg.norm(xy[0] - xy[-1]) > 0.2: continue
            ar = _P(xy).area
            if ar < 0.3: continue
            all_loops.append((z, xy, ar))
    areas = np.array([l[2] for l in all_loops])
    print("loop areas per station (min/median/max):", areas.min().round(2), np.median(areas).round(2), areas.max().round(2))
    # bore candidates: loops whose area is < 30% of the max loop area and centre near part centre
    for z, xy, ar in all_loops:
        cx, cy, r, rms = fit_circle(xy)
        if abs(r - r_hint) < r_tol and rms < rms_lim and zlo <= z <= zhi:
            bore.append((z, cx, cy, r, rms))
    bore = np.array(bore)
    if len(bore) >= 1:
        ox, oy = np.median(bore[:, 1]), np.median(bore[:, 2]); tilt = 0.0
        print(f"bore stations={len(bore)} r_mean={bore[:,3].mean():.4f} r_std={bore[:,3].std():.4f} centre=({ox:.4f},{oy:.4f}) centre_std=({bore[:,1].std():.3f},{bore[:,2].std():.3f})")
    else:
        print("bore not found; using bbox centre"); ox, oy = ctr_xy; tilt = None
    T3 = np.eye(4); T3[0, 3] = -ox; T3[1, 3] = -oy
    m.apply_transform(T3)
    clock_deg = 0.0
    if clock_mode.startswith("pent") or clock_mode.startswith("flatmin"):
        zc = float(clock_mode.split("@")[1])
        sc = m.section(plane_origin=[0, 0, zc], plane_normal=[0, 0, 1])
        best = None
        for seg in sc.discrete:
            xy = np.asarray(seg)[:, :2]
            if len(xy) < 8 or np.linalg.norm(xy[0] - xy[-1]) > 0.2: continue
            ar = _P(xy).area
            if best is None or ar > best[0]: best = (ar, xy)
        xy = best[1]; r = np.hypot(xy[:, 0], xy[:, 1]); th = np.degrees(np.arctan2(xy[:, 1], xy[:, 0]))
        if clock_mode.startswith("flatmin"):
            clock_deg = -th[np.argmin(r)]
        else:
            # pentagon: corner phase from the 5 r-peaks (fold theta mod 72)
            o = np.argsort(th); th_s, r_s = th[o], r[o]
            fold = np.radians(th_s * 5.0)  # 72 deg period -> 360
            w = np.clip(r_s - np.median(r_s), 0, None)
            phase = np.degrees(np.arctan2((w * np.sin(fold)).sum(), (w * np.cos(fold)).sum())) / 5.0
            clock_deg = -(phase + 36.0)   # flat centre -> +X
        print(f"clocking {clock_mode}: rotate by {clock_deg:.3f} deg")
    Rz = trimesh.transformations.rotation_matrix(np.radians(clock_deg), [0, 0, 1])
    m.apply_transform(Rz)
    T = Rz @ T3 @ T2 @ T1
    out = Path(f"{name}_aligned.stl"); m.export(out)
    lite = m.simplify_quadric_decimation(face_count=60000) if len(m.faces) > 60000 else m
    lite.export(f"{name}_aligned_lite.stl")
    Path(f"{name}_alignment.json").write_text(json.dumps({
        "schema": "alignment-v2-lite", "matrix_4x4": T.tolist(), "scale_factor": 1.0,
        "primary_plane": {"normal_src": nn.tolist(), "centroid_src": cc.tolist(), **fit},
        "bore": {"stations": len(bore), "r_mean": float(bore[:, 3].mean()) if len(bore) else None,
                 "tilt_deg": None if tilt is None else float(tilt)}, "clock_deg": float(clock_deg),
        "bounds_aligned": m.bounds.tolist()}, indent=1))
    print("aligned bounds", m.bounds.round(3).tolist())
    # plot 1: outline stack
    fig, ax = plt.subplots(figsize=(10, 10), dpi=110)
    cmap = plt.get_cmap("viridis")
    for z, xy, ar in all_loops:
        xy2 = (xy - [ox, oy]) @ Rz[:2, :2].T
        ax.plot(xy2[:, 0], xy2[:, 1], lw=0.6, color=cmap((z - z0) / (z1 - z0)))
    ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.set_title(f"{name}: Z-section outlines (dark=low z, yellow=high z)")
    ax.set_xlabel("X"); ax.set_ylabel("Y")
    fig.savefig(f"views/{name}_sections_xy.png"); plt.close(fig)
    # plot 2: (r,z) density
    v = m.vertices; r = np.hypot(v[:, 0], v[:, 1])
    fig, ax = plt.subplots(figsize=(12, 7), dpi=110)
    ax.hist2d(r, v[:, 2], bins=[600, 300], cmap="magma", cmin=1)
    ax.set_aspect("equal"); ax.grid(True, lw=0.3, color="w", alpha=0.3)
    ax.set_xlabel("r"); ax.set_ylabel("z"); ax.set_title(f"{name}: (r,z) half-profile density, all azimuths")
    fig.savefig(f"views/{name}_rz.png"); plt.close(fig)
    # plot 3: (theta, z) unwrapped at outer radius band → shows patterns/clocking
    th = np.degrees(np.arctan2(v[:, 1], v[:, 0]))
    fig, ax = plt.subplots(figsize=(14, 5), dpi=110)
    ax.hist2d(th, r, bins=[720, 300], cmap="magma", cmin=1)
    ax.set_xlabel("theta (deg)"); ax.set_ylabel("r"); ax.set_title(f"{name}: (theta, r) density")
    ax.grid(True, lw=0.3, color="w", alpha=0.3)
    fig.savefig(f"views/{name}_theta_r.png"); plt.close(fig)
    print("plots written")
