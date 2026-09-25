"""Fast two-way deviation: KD-tree over dense surface samples + exact closest point on candidate triangles."""
import sys, json, time
import numpy as np, trimesh
from scipy.spatial import cKDTree

def dist_to_mesh(target: trimesh.Trimesh, pts: np.ndarray, n_samples: int, k: int = 6, seed: int = 0):
    """Distance from pts to target surface: nearest k dense samples -> exact closest point on their triangles."""
    samp, fid = trimesh.sample.sample_surface(target, n_samples, seed=seed)
    # also include vertices (with one adjacent face each) so sharp edges are covered
    vf = target.vertex_faces[:, 0]
    ok = vf >= 0
    samp = np.vstack([samp, target.vertices[ok]]); fid = np.concatenate([fid, vf[ok]])
    tree = cKDTree(samp)
    _, nn = tree.query(pts, k=k, workers=-1)
    cand = fid[nn]                                   # (n, k) triangle ids
    best = np.full(len(pts), np.inf)
    tris = target.triangles
    for j in range(k):
        cp = trimesh.triangles.closest_point(tris[cand[:, j]], pts)
        d = np.linalg.norm(cp - pts, axis=1)
        best = np.minimum(best, d)
    return best

def stats(d):
    return dict(rms=float(np.sqrt((d**2).mean())), p50=float(np.percentile(d, 50)), p95=float(np.percentile(d, 95)),
                p99=float(np.percentile(d, 99)), max=float(d.max()), n=int(len(d)))

if __name__ == "__main__":
    name = sys.argv[1]; t0 = time.time()
    table_z = float(sys.argv[2]) if len(sys.argv) > 2 else None   # exclude scan-table sheet: z < table_z and normal up
    scan = trimesh.load_mesh(f"{name}_raw_aligned.stl", process=True)
    cad = trimesh.load_mesh(f"{name}_cad.stl", process=True)
    rng = np.random.default_rng(0)
    V = scan.vertices; N = scan.vertex_normals
    keep = np.ones(len(V), bool)
    if table_z is not None:
        keep = ~((V[:, 2] < table_z) & (N[:, 2] > 0.7))
        print(f"table exclusion: {(~keep).sum()} of {len(V)} scan vertices ({100*(~keep).mean():.1f}%) at z<{table_z} with up-normals")
    Vk = V[keep]
    idx = rng.choice(len(Vk), min(600_000, len(Vk)), replace=False); pts = Vk[idx]
    d_s2c = dist_to_mesh(cad, pts, n_samples=3_000_000)
    print(f"scan->CAD {stats(d_s2c)}  [{time.time()-t0:.0f}s]")
    cpts, cfid = trimesh.sample.sample_surface(cad, 300_000, seed=1)
    scan_t = scan if table_z is None else scan.submesh([np.where(keep[scan.faces].all(axis=1))[0]], append=True)
    d_c2s = dist_to_mesh(scan_t, cpts, n_samples=6_000_000, k=8)
    print(f"CAD->scan {stats(d_c2s)}  [{time.time()-t0:.0f}s]")
    np.savez(f"{name}_fastgate.npz", pts=pts, d_s2c=d_s2c, cpts=cpts, d_c2s=d_c2s, cfid=cfid)
    json.dump({"scan_to_cad": stats(d_s2c), "cad_to_scan": stats(d_c2s), "table_excluded_z": table_z}, open(f"{name}_fastgate.json", "w"), indent=1)
    # deviation maps
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    nrm = N[keep][idx]
    for tag, P, d, nn in [("s2c", pts, d_s2c, nrm), ("c2s", cpts, d_c2s, cad.face_normals[cfid])]:
        fig, axes = plt.subplots(2, 2, figsize=(18, 16), dpi=90)
        for ax, (title, i, j, sel, flip) in zip(axes.ravel(), [("top +Z", 0, 1, nn[:, 2] > 0.2, 1), ("bottom -Z (mirrored)", 0, 1, nn[:, 2] < -0.2, -1), ("front -Y", 0, 2, nn[:, 1] < -0.2, 1), ("right +X", 1, 2, nn[:, 0] > 0.2, 1)]):
            o = np.argsort(d[sel])
            sc = ax.scatter(P[sel][o, i] * flip, P[sel][o, j], c=d[sel][o], s=1, cmap="jet", vmin=0, vmax=0.3)
            ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.set_title(f"{name} {tag} deviation, {title}")
        plt.colorbar(sc, ax=axes.ravel().tolist(), label="|dev| mm (clip 0.3)", shrink=0.6)
        fig.savefig(f"views/{name}_dev_{tag}.png"); plt.close(fig)
    # where are the bad points? (r,z) table for dev > 0.2
    for lab, P, d in [("scan->CAD", pts, d_s2c), ("CAD->scan", cpts, d_c2s)]:
        bad = d > 0.2
        r = np.hypot(P[:, 0], P[:, 1]); z = P[:, 2]
        print(f"{lab}: {bad.sum()} pts > 0.2 ({100*bad.mean():.2f}%)")
        if bad.sum():
            H, re, ze = np.histogram2d(r[bad], z[bad], bins=[np.arange(0, r.max() + 1, 1.0), np.arange(np.floor(z.min()), np.ceil(z.max()) + 0.5, 0.5)])
            for i in range(H.shape[0]):
                row = H[i]
                if row.sum() < 20: continue
                print(f"   r[{re[i]:.0f},{re[i+1]:.0f}]: " + " ".join(f"z{ze[j]:+.1f}:{int(row[j])}" for j in range(len(row)) if row[j] >= 20))
