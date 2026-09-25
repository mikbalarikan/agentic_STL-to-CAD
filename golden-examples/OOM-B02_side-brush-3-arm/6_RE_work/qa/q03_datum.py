"""QA step 3 — INDEPENDENT datum derivation on the RAW scan.
No modeller inputs used: axis from area-weighted normal mode, rim plane from the extreme
flat population, axis position from a robust circle fit on the cup bore, arm phase from
angular mass distribution of the rigid arms.
"""
import numpy as np, trimesh, json

RAW = "/root/projects/oomwoo_b02/scratch/OOM-B02_raw.stl"
m = trimesh.load(RAW, process=False)
print("tris", len(m.faces), "verts", len(m.vertices), "volume", m.volume)
if m.volume < 0:
    m.invert()
    print("inverted -> volume", m.volume)

N = m.face_normals
A = m.area_faces
C = m.triangles_center

# ---- 1. dominant flat normal direction (area weighted, on the sphere, sign-free) ----
# Build the 3x3 second-moment of normals weighted by area -> but that finds the axis of a
# *plane-normal cluster* only if unimodal. Instead: coarse spherical histogram.
best = None
# Fibonacci sphere directions
n_dir = 4000
i = np.arange(n_dir) + 0.5
phi = np.arccos(1 - 2*i/n_dir)
gold = np.pi*(1+5**0.5)
theta = gold*i
D = np.stack([np.cos(theta)*np.sin(phi), np.sin(theta)*np.sin(phi), np.cos(phi)], 1)
D = D[D[:,2] >= 0]   # sign-free: only upper hemisphere
dots = np.abs(N @ D.T)               # nfaces x ndir
w = (dots > np.cos(np.deg2rad(3.0))).astype(np.float32) * A[:,None]
score = w.sum(0)
k = int(np.argmax(score))
ax = D[k]
print("coarse axis", ax, "area in 3deg cone", score[k])

# refine: least-squares plane-normal fit over the faces in that cone
for _ in range(30):
    sel = np.abs(N @ ax) > np.cos(np.deg2rad(4.0))
    Ns = N[sel]; As = A[sel]
    Ns = Ns * np.sign(Ns @ ax)[:,None]
    v = (Ns * As[:,None]).sum(0); v /= np.linalg.norm(v)
    if np.linalg.norm(v-ax) < 1e-12: ax = v; break
    ax = v
print("refined axis", ax, "n faces in cone", sel.sum(), "area", A[sel].sum())

# ---- 2. build a temp frame; find the flat plane populations along the axis ----
e1 = np.array([1.0,0,0])
if abs(np.dot(e1, ax)) > 0.9: e1 = np.array([0,1.0,0])
u = np.cross(ax, e1); u /= np.linalg.norm(u)
v = np.cross(ax, u)
R0 = np.stack([u, v, ax])          # rows: world -> local
Cl = C @ R0.T
h = Cl[:,2]
hs = h[sel]; As2 = A[sel]
lo, hi = hs.min(), hs.max()
bins = np.arange(lo, hi+0.05, 0.05)
hist, edges = np.histogram(hs, bins=bins, weights=As2)
order = np.argsort(hist)[::-1]
print("top flat-plane bands (h, area):")
for o in order[:12]:
    print(f"   h={edges[o]:+9.3f}..{edges[o+1]:+9.3f}  area={hist[o]:8.1f}")
np.save("/root/projects/oomwoo_b02/scratch/qa/_ax_R0.npy", R0)
np.save("/root/projects/oomwoo_b02/scratch/qa/_hist.npy", np.stack([edges[:-1], hist]))
