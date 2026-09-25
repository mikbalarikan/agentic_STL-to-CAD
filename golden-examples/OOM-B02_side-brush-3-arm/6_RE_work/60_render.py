"""OOM-B02 documentation renders — orthographic z-buffer rasteriser + Lambert shading.

RE_SPEC 6.3 asks for Blender studio renders via _PIPELINE/tools/blender_doc_render.py.
Blender is NOT installed on this machine (ledger A12), so the W01 precedent is used: a
purpose-written orthographic rasteriser.  The geometry is the DELIVERED STEP tessellation,
so the renders are dimensionally faithful; only the shading is diagrammatic.
"""
import numpy as np, trimesh, time
from scipy.spatial import cKDTree
from PIL import Image

SC = "/root/projects/oomwoo_b02/scratch"
OUT = f"{SC}/docs"
cad = trimesh.load(f"{SC}/out_it2/OOM-B02_cad.stl", process=False)
V = cad.vertices
F = cad.faces
print("mesh %d faces" % len(F))


def basis(d, up=(0, 0, 1)):
    d = np.array(d, float); d /= np.linalg.norm(d)
    up = np.array(up, float)
    if abs(d @ up) > 0.98:
        up = np.array([0, 1.0, 0])
    rt = np.cross(up, d); rt /= np.linalg.norm(rt)
    tu = np.cross(d, rt)
    return np.array([rt, tu, d])            # rows: right, up, view


def render(view_dir, W=1500, H=1150, SS=2, vcol=None, bg=(247, 247, 249)):
    t0 = time.time(); w, h = W * SS, H * SS
    R = basis(view_dir)
    C = V @ R.T
    mn, mx = C[:, :2].min(0), C[:, :2].max(0)
    ctr = (mn + mx) / 2; span = (mx - mn).max() * 1.12
    s = min(w, h) / span
    sx = (C[:, 0] - ctr[0]) * s + w / 2
    sy = h / 2 - (C[:, 1] - ctr[1]) * s
    dep = C[:, 2]
    n = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1; n = n / ln[:, None]
    nv = n @ R.T
    front = nv[:, 2] < 0                                   # cull back faces
    key = np.array([-0.45, 0.60, -0.66]); key /= np.linalg.norm(key)
    fil = np.array([0.65, 0.25, -0.72]); fil /= np.linalg.norm(fil)
    lam = 0.72 * np.clip(nv @ key, 0, 1) + 0.26 * np.clip(nv @ fil, 0, 1) + 0.20
    rim = 0.30 * np.clip(1 - np.abs(nv[:, 2]), 0, 1) ** 3
    sh = np.clip(lam + rim, 0, 1.35)
    zb = np.full((h, w), np.inf); cb = np.zeros((h, w, 3))
    bgc = np.array(bg, float) / 255
    yy = np.arange(h)[:, None]; grad = (0.965 + 0.05 * yy / h)
    cb[:] = bgc[None, None, :] * grad[:, :, None]
    idx = np.where(front)[0]
    order = idx[np.argsort(-dep[F[idx]].mean(1))]
    base = np.array([0.62, 0.655, 0.70])
    for f in order:
        a, b, c = F[f]
        x0, x1 = sx[[a, b, c]].min(), sx[[a, b, c]].max()
        y0, y1 = sy[[a, b, c]].min(), sy[[a, b, c]].max()
        ix0, ix1 = int(max(0, np.floor(x0))), int(min(w - 1, np.ceil(x1)))
        iy0, iy1 = int(max(0, np.floor(y0))), int(min(h - 1, np.ceil(y1)))
        if ix1 < ix0 or iy1 < iy0:
            continue
        X, Y = np.meshgrid(np.arange(ix0, ix1 + 1), np.arange(iy0, iy1 + 1))
        x_a, y_a = sx[a], sy[a]; x_b, y_b = sx[b], sy[b]; x_c, y_c = sx[c], sy[c]
        den = (y_b - y_c) * (x_a - x_c) + (x_c - x_b) * (y_a - y_c)
        if abs(den) < 1e-9:
            continue
        l1 = ((y_b - y_c) * (X - x_c) + (x_c - x_b) * (Y - y_c)) / den
        l2 = ((y_c - y_a) * (X - x_c) + (x_a - x_c) * (Y - y_c)) / den
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not m.any():
            continue
        zz = l1 * dep[a] + l2 * dep[b] + l3 * dep[c]
        sub = zb[iy0:iy1 + 1, ix0:ix1 + 1]
        upd = m & (zz < sub)
        if not upd.any():
            continue
        sub[upd] = zz[upd]
        if vcol is None:
            col = base * sh[f]
        else:
            cc = (l1[..., None] * vcol[a] + l2[..., None] * vcol[b] + l3[..., None] * vcol[c])
            col = cc * np.clip(sh[f], 0.35, 1.2)
        tgt = cb[iy0:iy1 + 1, ix0:ix1 + 1]
        tgt[upd] = (col[upd] if vcol is not None else col)
    img = (np.clip(cb, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img).resize((W, H), Image.LANCZOS)
    print("   rendered in %.0fs" % (time.time() - t0))
    return im


# camera sits on -view_dir.  Azimuth 45.9 deg is chosen to fall BETWEEN arms (0/120/240)
# so no arm is foreshortened onto the hub.  _iso = dome side (all three arms), _iso_cup =
# cup side (the drive interface: rim annulus, cup bore, hex socket).
views = {"iso": (-0.60, -0.62, -0.50), "iso_cup": (-0.60, -0.62, 0.50),
         "front": (0, -1, 0), "side": (-1, 0, 0), "top": (0, 0, -1)}
for k, d in views.items():
    render(d).save(f"{OUT}/OOM-B02_{k}.png"); print("saved OOM-B02_%s.png" % k)

# ---- scan-vs-CAD deviation render: colour the CAD skin by the GATED Tier-2 deviation
A = np.load(f"{SC}/qa/_dev_it2.npy")
Q = A[:, :3]; D = A[:, 3]; O = A[:, 4] > 0.5
print("deviation cloud: %d gated of %d samples, max %.3f mm" % (O.sum(), len(A), D[O].max()))
tree = cKDTree(Q[O])
dd, ii = tree.query(V, workers=-1)
dv = np.clip(D[O][ii], 0, 2.6) / 2.6          # 2.6 mm full scale = the it2 whole-part max
import matplotlib as mpl
vcol = mpl.colormaps["RdYlGn_r"](dv)[:, :3]
render((-0.60, -0.62, -0.50), vcol=vcol).save(f"{OUT}/OOM-B02_scan_vs_cad.png")
render((-0.60, -0.62, 0.50), vcol=vcol).save(f"{OUT}/OOM-B02_scan_vs_cad_cup.png")
print("saved OOM-B02_scan_vs_cad.png / _cup.png")

# colour-bar legend for the deviation renders (0 .. 2.6 mm, RdYlGn_r)
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.0, 0.85))
fig.subplots_adjust(bottom=0.55, left=0.06, right=0.94)
cb = mpl.colorbar.ColorbarBase(ax, cmap=mpl.colormaps["RdYlGn_r"],
                               norm=mpl.colors.Normalize(0, 2.6), orientation="horizontal")
cb.set_label("CAD -> scan deviation (mm), gated outer skin;  full scale 2.6 = the it2 whole-part max "
             "(band 4.0)", size=8)
cb.ax.tick_params(labelsize=8)
fig.savefig(f"{OUT}/OOM-B02_scan_vs_cad_scale.png", dpi=150, facecolor="white")
print("saved OOM-B02_scan_vs_cad_scale.png")
