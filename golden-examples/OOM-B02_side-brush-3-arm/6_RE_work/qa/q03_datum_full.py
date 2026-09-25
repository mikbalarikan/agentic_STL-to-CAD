"""QA-3 — INDEPENDENT datum derivation on the RAW scan.

Uses NO modeller output.  Derives, from OOM-B02_raw.stl in raw scanner coordinates:
  1. the rim-annulus plane  (largest flat area population, area-weighted)
  2. the rotation axis      (= that plane's normal, refined)
  3. the axis position      (robust circle fit on the cup bore wall)
  4. the arm-1 phase        (angular mass distribution of the rigid arms)
and composes a raw->datum 4x4 which is compared against the modeller's
2_mesh_cleaned/alignment.json  matrix_4x4.
"""
import numpy as np, trimesh, json, math

SC  = "/root/projects/oomwoo_b02/scratch"
RAW = f"{SC}/OOM-B02_raw.stl"
ALIGN = "/root/gdrive/111 UP UP UP/REMAKE AI - DIY/OOMWOO_CAD/01_SOURCED_reverse-engineered/OOM-B02_Side-brush-3-arm/2_mesh_cleaned/alignment.json"

m = trimesh.load(RAW, process=False)
N, A, C = m.face_normals, m.area_faces, m.triangles_center
print("raw scan: %d tri  area %.1f mm2" % (len(m.faces), A.sum()))

# ---- 1. dominant flat normal direction (sign-free spherical vote) -----------
n_dir = 6000
i = np.arange(n_dir) + 0.5
phi = np.arccos(1 - 2 * i / n_dir)
theta = np.pi * (1 + 5 ** 0.5) * i
D = np.stack([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)], 1)
D = D[D[:, 2] >= 0]
score = np.zeros(len(D))
for s in range(0, len(N), 100000):                       # chunk to bound memory
    dots = np.abs(N[s:s + 100000] @ D.T)
    score += ((dots > np.cos(np.deg2rad(3.0))).astype(np.float32) * A[s:s + 100000, None]).sum(0)
ax = D[int(np.argmax(score))]
for _ in range(40):                                       # refine
    sel = np.abs(N @ ax) > np.cos(np.deg2rad(4.0))
    Ns = N[sel] * np.sign(N[sel] @ ax)[:, None]
    v = (Ns * A[sel, None]).sum(0); v /= np.linalg.norm(v)
    if np.linalg.norm(v - ax) < 1e-13:
        ax = v; break
    ax = v
print("axis (raw frame)      : [%+.9f %+.9f %+.9f]  (%d faces, %.1f mm2 in cone)"
      % (*ax, sel.sum(), A[sel].sum()))

# ---- 2. locate the flat planes along that axis -----------------------------
e1 = np.array([1.0, 0, 0]) if abs(ax[0]) < 0.9 else np.array([0, 1.0, 0])
u = np.cross(ax, e1); u /= np.linalg.norm(u)
v = np.cross(ax, u)
R0 = np.stack([u, v, ax])                                 # world -> local rows
h = (C @ R0.T)[:, 2]
hs, As = h[sel], A[sel]
bins = np.arange(hs.min(), hs.max() + 0.05, 0.05)
hist, edges = np.histogram(hs, bins=bins, weights=As)
top = np.argsort(hist)[::-1][:8]
print("flat bands (h, area)  :", ", ".join("%.2f:%.0f" % (edges[o], hist[o]) for o in sorted(top)))
h_rim = edges[top[0]] + 0.025                             # the biggest flat = rim annulus

# refine the rim plane by least squares on its own faces
band = sel & (np.abs(h - h_rim) < 0.30)
P = m.vertices[m.faces[band]].reshape(-1, 3)
cen = P.mean(0)
_, _, Vt = np.linalg.svd(P - cen, full_matrices=False)
n_rim = Vt[2] / np.linalg.norm(Vt[2])
if n_rim @ ax < 0: n_rim = -n_rim
rms = float(np.abs((P - cen) @ n_rim).std())
print("rim plane fit         : rms %.4f mm over %d faces (%.1f mm2)" % (rms, band.sum(), A[band].sum()))
ax = n_rim

# ---- 3. axis POSITION from a robust circle fit on the cup bore -------------
e1 = np.array([1.0, 0, 0]) if abs(ax[0]) < 0.9 else np.array([0, 1.0, 0])
u = np.cross(ax, e1); u /= np.linalg.norm(u)
v = np.cross(ax, u)
R0 = np.stack([u, v, ax])
Cl = (C - cen) @ R0.T
# cup bore wall: faces whose normal is perpendicular to the axis, 0.3..2.2 mm above the rim.
# The band r<14 contains TWO coaxial cylinders (cup bore ~R10.4 and outer skirt ~R13).
# Separate them by the sign of N.r_hat -- no prior radius knowledge used.  The raw scan has
# inward-pointing normals, so the convention is fixed empirically off the outer skirt.
perp = np.abs(N @ ax) < 0.30
rad_c = np.hypot(Cl[:, 0], Cl[:, 1])
rhat = np.c_[Cl[:, 0], Cl[:, 1]] / np.maximum(rad_c, 1e-9)[:, None]
Nl = N @ R0.T
ndotr = (Nl[:, :2] * rhat).sum(1)
band = perp & (Cl[:, 2] > 0.30) & (Cl[:, 2] < 2.20) & (rad_c < 14.0)
outer_sign = np.sign(np.average(ndotr[band & (rad_c > 12.8)], weights=A[band & (rad_c > 12.8)]))
inb = band & (np.sign(ndotr) == -outer_sign)          # faces of the INNER (cup bore) wall
Q = Cl[inb][:, :2]; W = A[inb]
print("cup-bore wall faces   : %d (outer-skirt normal sign %+.0f; band had %d)"
      % (inb.sum(), outer_sign, band.sum()))
c2 = np.zeros(2)
for _ in range(60):                                        # weighted algebraic circle fit, IRLS
    d = np.hypot(*(Q - c2).T)
    Rm = np.average(d, weights=W)
    w2 = W / (1.0 + ((d - Rm) / 0.30) ** 2)                # Cauchy robustifier
    Amat = np.c_[2 * Q, np.ones(len(Q))] * w2[:, None]
    b = (Q ** 2).sum(1) * w2
    sol, *_ = np.linalg.lstsq(Amat, b, rcond=None)
    cn = sol[:2]
    if np.linalg.norm(cn - c2) < 1e-10: c2 = cn; break
    c2 = cn
d = np.hypot(*(Q - c2).T); Rm = np.average(d, weights=W)
print("cup bore              : R %.4f (D %.4f)  fit rms %.4f  centre offset %.4f"
      % (Rm, 2 * Rm, np.sqrt(np.average((d - Rm) ** 2, weights=W)), np.linalg.norm(c2)))
origin = cen + c2[0] * u + c2[1] * v

# ---- 4. arm-1 phase from angular mass distribution -------------------------
V = m.vertices - origin
Vl = V @ R0.T
r = np.hypot(Vl[:, 0], Vl[:, 1]); th = np.degrees(np.arctan2(Vl[:, 1], Vl[:, 0]))
rig = (r > 20.0) & (r < 34.0)                              # rigid blade band, no bristles
# 3-fold Fourier phase of the angular mass distribution: arg(sum e^{3i*theta})/3
c3 = np.exp(3j * np.radians(th[rig])).sum()
ph = math.degrees(np.angle(c3)) / 3.0
ph = ((ph + 60.0) % 120.0) - 60.0                          # fold into (-60, 60]
arm1 = sorted(((ph + 120 * k + 180) % 360) - 180 for k in range(3))
# per-arm centroid refinement (circular mean inside +/-25 deg of each nominal centre)
refined = []
for a in arm1:
    d = ((th[rig] - a + 180) % 360) - 180
    s = np.abs(d) < 25.0
    refined.append(a + math.degrees(np.angle(np.exp(1j * np.radians(d[s])).sum())))
print("arm centres (deg)     :", ["%.2f" % a for a in refined],
      " spacings:", ["%.2f" % (((refined[(k + 1) % 3] - refined[k]) % 360)) for k in range(3)],
      " 3-fold |c3|/n = %.3f" % (abs(c3) / rig.sum()))
arm1 = refined
# ---- 5. compare against the modeller's alignment.json ----------------------
# WHICH physical arm is "arm 1" is a labelling convention (3-fold symmetric except SAF-1),
# so the comparison is made modulo 120 deg: all three labellings are tried, best reported.
Tm = np.array(json.load(open(ALIGN))["matrix_4x4"], float)
smp = m.vertices[np.random.default_rng(0).choice(len(m.vertices), 60000, replace=False)]
d2 = smp @ Tm[:3, :3].T + Tm[:3, 3]
print("\n---- INDEPENDENT vs MODELLER datum (arm-1 label taken mod 120 deg) ----")
best = None
for a1 in refined:
    Rz = np.array([[math.cos(math.radians(-a1)), -math.sin(math.radians(-a1)), 0],
                   [math.sin(math.radians(-a1)),  math.cos(math.radians(-a1)), 0], [0, 0, 1]])
    Rfull = Rz @ R0
    T = np.eye(4); T[:3, :3] = Rfull; T[:3, 3] = -Rfull @ origin
    Rd = Rfull @ Tm[:3, :3].T
    ang = math.degrees(math.acos(max(-1, min(1, (np.trace(Rd) - 1) / 2))))
    d1 = smp @ Rfull.T + T[:3, 3]
    dd = np.linalg.norm(d1 - d2, axis=1)
    print("   arm1=%+8.2f deg -> rot diff %.4f deg, point disagreement mean %.4f p95 %.4f max %.4f"
          % (a1, ang, dd.mean(), np.percentile(dd, 95), dd.max()))
    if best is None or dd.mean() < best[0]:
        best = (dd.mean(), a1, ang, T, Rfull, dd, d1)
_, a1, ang, T, Rfull, dd, d1 = best
print("  BEST: arm1 = %+.2f deg" % a1)
print("  rotation difference   : %.4f deg" % ang)
print("  point disagreement    : mean %.4f  p95 %.4f  max %.4f mm (60k scan points)"
      % (dd.mean(), np.percentile(dd, 95), dd.max()))
print("  z-height disagreement : mean %+.4f mm" % (d1[:, 2] - d2[:, 2]).mean())
arm1 = refined
np.save(f"{SC}/qa/_T_indep.npy", T)
json.dump({"axis": ax.tolist(), "rim_rms": rms, "bore_R": float(Rm), "arm_centres": arm1,
           "rot_diff_deg": ang, "pt_disagree_mean": float(dd.mean()),
           "pt_disagree_p95": float(np.percentile(dd, 95)), "pt_disagree_max": float(dd.max())},
          open(f"{SC}/qa/_datum_indep.json", "w"), indent=1)
print("saved _T_indep.npy / _datum_indep.json")
