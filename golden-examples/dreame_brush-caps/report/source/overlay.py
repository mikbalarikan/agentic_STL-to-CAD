"""Section overlays: CAD (red) on scan (black) at Z planes and radial half-planes — visual proof."""
import sys
import numpy as np, trimesh
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
name = sys.argv[1]; zs = [float(v) for v in sys.argv[2].split(",")]; ths = [float(v) for v in sys.argv[3].split(",")]
scan = trimesh.load_mesh(f"{name}_aligned.stl", process=True)   # 300k work mesh (largest body)
cad = trimesh.load_mesh(f"{name}_cad.stl", process=True)
def zsec(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    return [] if s is None else [np.asarray(sg)[:, :2] for sg in s.discrete]
def rsec(m, th):
    t = np.radians(th); d = np.array([np.cos(t), np.sin(t), 0]); n = np.array([-np.sin(t), np.cos(t), 0])
    s = m.section(plane_origin=[0, 0, 0], plane_normal=n); out = []
    if s is None: return out
    for sg in s.discrete:
        P = np.asarray(sg); r = P @ d; k = r > 0
        if k.sum() < 2: continue
        idx = np.where(k)[0]; br = np.where(np.diff(idx) > 1)[0]
        for ch in np.split(idx, br + 1):
            if len(ch) >= 2: out.append(np.c_[r[ch], P[ch, 2]])
    return out
n = len(zs) + len(ths); cols = 3; rows = (n + cols - 1) // cols
fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 7 * rows), dpi=100); axes = np.atleast_1d(axes).ravel()
i = 0
for z in zs:
    ax = axes[i]; i += 1
    for xy in zsec(scan, z): ax.plot(xy[:, 0], xy[:, 1], "k-", lw=0.7)
    for xy in zsec(cad, z): ax.plot(xy[:, 0], xy[:, 1], "r-", lw=0.9)
    ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.set_title(f"{name}: Z={z} section — scan black / CAD red")
for th in ths:
    ax = axes[i]; i += 1
    for rz in rsec(scan, th): ax.plot(rz[:, 0], rz[:, 1], "k-", lw=0.7)
    for rz in rsec(cad, th): ax.plot(rz[:, 0], rz[:, 1], "r-", lw=0.9)
    ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.set_title(f"{name}: radial θ={th}° — scan black / CAD red"); ax.set_xlabel("r"); ax.set_ylabel("z")
for ax in axes[i:]: ax.axis("off")
fig.tight_layout(); fig.savefig(f"views/{name}_overlay.png"); plt.close(fig); print("overlay written", name)
