"""QA-5 — Tier-2 scan-skin gate.  Independent best-fit ICP + normal-based outer-skin mask.

Reference  : raw scan (798,874 tri) brought to the datum frame with alignment.json, then
             ICP-refined against the CAD (so a datum error cannot flatter the numbers).
Masks (all reported as masked fractions, RE_SPEC 4 honesty rule):
   M1 bristles      scan r > 38.5              -- not modelled, soft feature (R4/A10)
   M2 screw         scan r < 3.6, z 8.6..10.4  -- COTS, not modelled (A9)
   M3 open boundary CAD points whose nearest scan sample lies < 0.8 mm from an open
                    boundary loop -- distance to a hole EDGE is not a surface deviation
   M4 outer skin    normal agreement |n_cad . n_scan| < cos(70 deg) dropped -- an occluded
                    interior correspondence is not an outer-skin deviation
Gate: whole part p95 <= 1.6, max <= 4.0.  Named non-caliper interfaces: max <= 0.8.
"""
import sys, os, math, json
import numpy as np, trimesh
from scipy.spatial import cKDTree

SC = "/root/projects/oomwoo_b02/scratch"
ROOT = "/root/gdrive/111 UP UP UP/REMAKE AI - DIY/OOMWOO_CAD/01_SOURCED_reverse-engineered/OOM-B02_Side-brush-3-arm"
CAD = sys.argv[1]
TAG = sys.argv[2] if len(sys.argv) > 2 else "it2"
rng = np.random.default_rng(7)

# ---------------- scan -> datum frame -------------------------------------
Tm = np.array(json.load(open(f"{ROOT}/2_mesh_cleaned/alignment.json"))["matrix_4x4"], float)
s = trimesh.load(f"{SC}/OOM-B02_raw.stl", process=False)
s.merge_vertices()          # STL is unwelded: without this EVERY edge reads as a boundary
print("scan welded: %d verts / %d faces" % (len(s.vertices), len(s.faces)))
if s.volume < 0:
    s.invert(); print("scan normals were inward -> inverted")
s.apply_transform(Tm)

fc = s.triangles_center
fr = np.hypot(fc[:, 0], fc[:, 1]); fz = fc[:, 2]
m1 = fr > 38.5                                            # bristles
# screw (COTS, not modelled).  Two populations: the HEAD in the dome counterbore, and the
# screw END seen straight down the central bore -- a flat at z 5.091 spanning r 0.03..1.40
# (4.04 mm2) that reads as if it were the pocket floor.  Both must leave the gate reference.
m2 = ((fr < 3.6) & (fz > 8.6) & (fz < 10.4)) | ((fr < 1.60) & (fz > 4.50) & (fz < 10.60))
keep = ~(m1 | m2)
print("scan faces: %d total | bristle-masked %d (%.1f%%) | screw-masked %d | kept %d"
      % (len(fc), m1.sum(), 100 * m1.mean(), m2.sum(), keep.sum()))
s.update_faces(keep)
s.remove_unreferenced_vertices()

# open-boundary vertices of the MASKED scan (hole edges + the bristle cut)
eu, ct = np.unique(np.sort(s.edges, axis=1), axis=0, return_counts=True)
bverts = s.vertices[np.unique(eu[ct == 1])]
print("scan open-boundary vertices: %d" % len(bverts))
btree = cKDTree(bverts)

# dense point sampling of the scan surface (spacing ~0.04 mm >> nothing we gate on)
NS = 3_000_000
sp, sf = trimesh.sample.sample_surface(s, NS, seed=11)
sn = s.face_normals[sf]
stree = cKDTree(sp)
print("scan sampled: %d pts (~%.3f mm spacing over %.0f mm2)"
      % (len(sp), math.sqrt(s.area / NS), s.area))

# ---------------- CAD sampling --------------------------------------------
c = trimesh.load(CAD, process=True)
NC = 300_000
cp, cf = trimesh.sample.sample_surface(c, NC, seed=13)
cn = c.face_normals[cf]
print("CAD sampled : %d pts over %.0f mm2" % (len(cp), c.area))

# ---------------- ICP refine (point-to-point, masked correspondences) ------
def corr(P, Nn):
    d, i = stree.query(P, workers=-1)
    ok = (np.abs((Nn * sn[i]).sum(1)) > math.cos(math.radians(70.0))) \
         & (btree.query(sp[i], workers=-1)[0] > 0.8) & (d < 3.0)
    return d, i, ok

T = np.eye(4)
P, Nn = cp.copy(), cn.copy()
for it in range(60):
    d, i, ok = corr(P, Nn)
    A_, B_ = P[ok], sp[i][ok]
    ca, cb = A_.mean(0), B_.mean(0)
    H = (A_ - ca).T @ (B_ - cb)
    U, _, Vt = np.linalg.svd(H)
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    t = cb - R @ ca
    P = P @ R.T + t; Nn = Nn @ R.T
    step = np.linalg.norm(t) + math.degrees(math.acos(max(-1, min(1, (np.trace(R) - 1) / 2))))
    Tn = np.eye(4); Tn[:3, :3] = R; Tn[:3, 3] = t
    T = Tn @ T
    if it >= 54:
        print("   ICP it%2d: step %.3e  (rot %.5f deg, trans %.5f mm this iteration)"
              % (it, step, math.degrees(math.acos(max(-1, min(1, (np.trace(R) - 1) / 2)))),
                 np.linalg.norm(t)))
    if step < 1e-6:
        break
ang = math.degrees(math.acos(max(-1, min(1, (np.trace(T[:3, :3]) - 1) / 2))))
print("ICP converged in %d its | correction: %.4f deg, %.4f mm translation | %.4f mm max point move"
      % (it + 1, ang, np.linalg.norm(T[:3, 3]), np.abs(np.linalg.norm(P - cp, axis=1)).max()))

d, i, ok = corr(P, Nn)
skin = (np.abs((Nn * sn[i]).sum(1)) > math.cos(math.radians(70.0)))
edge = btree.query(sp[i], workers=-1)[0] > 0.8
gate = skin & edge
print("masking: outer-skin drops %.2f%% | open-boundary drops %.2f%% | gated points %d of %d (%.1f%%)"
      % (100 * (1 - skin.mean()), 100 * (1 - edge.mean()), gate.sum(), len(d), 100 * gate.mean()))

# ---------------- zone buckets (datum coords, on the CAD side) -------------
x, y, z = cp.T                                 # pre-ICP CAD coords = the design frame
r = np.hypot(x, y); th = (np.degrees(np.arctan2(y, x)) + 360) % 360
darm = np.minimum.reduce([np.abs(((th - a + 180) % 360) - 180) for a in (0, 120, 240)])
dsaf = np.abs(((th - 59.0 + 180) % 360) - 180)

# hex occlusion mask (A6): the scan saw only ~2/3 of the hexagon; the 124 deg gap is
# located here from the scan itself, not assumed.
hexcad = (r < 4.4) & (z > 2.5) & (z < 5.95)
# coverage must be measured on the hex WALL only (normals perpendicular to Z); including the
# pocket floor makes every azimuth look covered and the mask becomes a no-op.
sc_ = s.triangles_center; sn_ = s.face_normals
srw = np.hypot(sc_[:, 0], sc_[:, 1])
hz = (srw > 3.2) & (srw < 4.6) & (sc_[:, 2] > 2.7) & (sc_[:, 2] < 5.85) & (np.abs(sn_[:, 2]) < 0.5)
hth = (np.degrees(np.arctan2(sc_[hz, 1], sc_[hz, 0])) + 360) % 360
cov = np.zeros(360, bool); cov[np.unique(hth.astype(int))] = True
# close 1-deg pinholes so speckle does not count as coverage
cov = np.array([cov[(k - 1) % 360] or cov[k] or cov[(k + 1) % 360] for k in range(360)]) & cov
gaps, run = [], 0
for k in range(720):
    if not cov[k % 360]: run += 1
    else:
        if run: gaps.append(run)
        run = 0
hex_seen = np.isin(th.astype(int) % 360, np.where(cov)[0])
print("hex pocket WALL: scan covers %d of 360 deg (%.0f%%); largest gap %d deg -> masked (A6)"
      % (cov.sum(), 100 * cov.mean(), max(gaps) if gaps else 0))

ZONES = [
  ("rim annulus (datum A)",        (z < 0.06) & (r > 10.5) & (r < 13.5), 0.8,  "named, no caliper"),
  ("cup bore wall",                (r > 10.0) & (r < 10.6) & (z > 0.1) & (z < 2.3), None, "Tier-1 (F03)"),
  ("cup floor",                    (z > 2.3) & (z < 2.9) & (r > 4.0) & (r < 10.2) & (dsaf > 25), None, "interior"),
  ("hex pocket (F01)",             hexcad & hex_seen, 0.8, "named, no caliper, 124 deg gap masked"),
  ("dome, off-arm off-SAF",        (z > 3.0) & (z < 11.0) & (r < 13.5) & (darm > 25) & (dsaf > 25), None, "cosmetic"),
  ("skirt band z 0-4.5",           (r > 12.3) & (r < 13.5) & (z > 0.1) & (z < 4.5) & (dsaf > 25), None, "Tier-1 (F05)"),
  ("SAF-1 external nub",           (dsaf < 6.0) & (r > 13.4) & (z > 2.2) & (z < 4.2), 0.8, "named key, gated"),
  ("SAF-1 skirt recess",           (dsaf < 9.0) & (r > 12.0) & (r < 13.0) & (z > 0.1) & (z < 4.6), 0.8, "named key, gated"),
  ("SAF-1 internal boss",          (dsaf < 18.0) & (r > 4.3) & (r < 10.5) & (z > 0.2) & (z < 1.7), None, "interior/occluded (A7)"),
  ("arms r 14-38.2",               (darm < 20) & (r > 14.0) & (r < 38.2), None, "free-state droop (A11)"),
  ("arm/hub root r 7-14",          (darm < 25) & (r > 7.0) & (r < 14.0), None, "blend"),
]
print("\n---- Tier-2 zone report (CAD->scan, outer skin, after ICP) ----")
print("  %-32s %7s %7s %7s %7s   %s" % ("zone", "n", "mean", "p95", "max", "gate"))
rep = {}
for nm, sel, band, note in ZONES:
    g = sel & gate
    if g.sum() < 50:
        print("  %-32s %7d      -- too few gated points --   %s" % (nm, g.sum(), note)); continue
    dd = d[g]
    p95, mx = float(np.percentile(dd, 95)), float(dd.max())
    verd = ""
    if band:
        verd = "PASS" if mx <= band else "** %.3f OVER **" % (mx - band)
    print("  %-32s %7d %7.3f %7.3f %7.3f   [masked %4.1f%%] %s %s"
          % (nm, g.sum(), dd.mean(), p95, mx, 100 * (1 - g.sum() / max(sel.sum(), 1)), note, verd))
    rep[nm] = dict(n=int(g.sum()), mean=float(dd.mean()), p95=p95, max=mx,
                   band=band, note=note, verdict=verd, masked_frac=float(1 - g.sum() / max(sel.sum(), 1)))

# ---------------- whole-part gate -----------------------------------------
whole = gate & (r <= 38.2)
dd = d[whole]
p95, mx = float(np.percentile(dd, 95)), float(dd.max())
print("\n---- WHOLE PART (outer skin, bristles+screw excluded) ----")
print("  n %d  mean %.3f  p95 %.3f (band 1.6)  max %.3f (band 4.0)  -> %s"
      % (whole.sum(), dd.mean(), p95, mx, "PASS" if (p95 <= 1.6 and mx <= 4.0) else "FAIL"))
for q in (50, 90, 95, 99, 99.9):
    print("     p%-5s %.3f" % (q, np.percentile(dd, q)))

# ---------------- mask sensitivity: how much does the answer depend on M3? --
print("\n---- open-boundary mask sensitivity (M3 radius) ----")
bd = btree.query(sp[i], workers=-1)[0]
sens = {}
print("   [gated named interfaces, mask r = 0.0 vs 0.8 -- does the 0.8 PASS survive unmasked?]")
for nm, sel, band, note in ZONES:
    if not band: continue
    for rad in (0.0, 0.8):
        g = sel & skin & (bd > rad)
        if g.sum() < 30:
            print("      %-26s r=%.1f  n=%d too few" % (nm, rad, g.sum())); continue
        print("      %-26s r=%.1f  n=%6d  p95 %.3f  max %.3f  %s"
              % (nm, rad, g.sum(), np.percentile(d[g], 95), d[g].max(),
                 "PASS" if d[g].max() <= band else "** OVER by %.3f **" % (d[g].max() - band)))
for rad in (0.0, 0.2, 0.4, 0.8, 1.5, 2.5):
    g = skin & (bd > rad) & (r <= 38.2)
    sens[rad] = (int(g.sum()), float(np.percentile(d[g], 95)), float(d[g].max()))
    print("   r=%4.1f mm  kept %6d (%5.1f%%)  p95 %.3f  max %.3f  %s"
          % (rad, g.sum(), 100 * g.sum() / (r <= 38.2).sum(), sens[rad][1], sens[rad][2],
             "PASS" if (sens[rad][1] <= 1.6 and sens[rad][2] <= 4.0) else "FAIL"))

# ---------------- reverse: scan -> CAD (catches MISSING CAD material) -------
ctree = cKDTree(P)
sel_s = rng.choice(len(sp), 400_000, replace=False)
rs = np.hypot(sp[sel_s, 0], sp[sel_s, 1])
d2_, j2 = ctree.query(sp[sel_s], workers=-1)
ok2 = (np.abs((sn[sel_s] * Nn[j2]).sum(1)) > math.cos(math.radians(70.0))) \
      & (btree.query(sp[sel_s], workers=-1)[0] > 0.8) & (rs <= 38.2)
print("\n---- REVERSE scan->CAD (outer skin) : detects features the CAD is MISSING ----")
print("   n %d  mean %.3f  p95 %.3f  max %.3f" % (ok2.sum(), d2_[ok2].mean(),
      np.percentile(d2_[ok2], 95), d2_[ok2].max()))
far = ok2 & (d2_ > 1.6)
if far.sum():
    fp = sp[sel_s][far]
    fr_ = np.hypot(fp[:, 0], fp[:, 1]); fth = (np.degrees(np.arctan2(fp[:, 1], fp[:, 0])) + 360) % 360
    print("   %d pts (%.3f%%) beyond 1.6 mm: r %.1f-%.1f, z %.1f-%.1f"
          % (far.sum(), 100 * far.mean(), fr_.min(), fr_.max(), fp[:, 2].min(), fp[:, 2].max()))

json.dump(dict(icp_deg=ang, icp_mm=float(np.linalg.norm(T[:3, 3])),
               sensitivity={str(k): v for k, v in sens.items()},
               reverse=dict(n=int(ok2.sum()), mean=float(d2_[ok2].mean()),
                            p95=float(np.percentile(d2_[ok2], 95)), max=float(d2_[ok2].max())),
               whole=dict(n=int(whole.sum()), mean=float(dd.mean()), p95=p95, max=mx,
                          pass_=bool(p95 <= 1.6 and mx <= 4.0)),
               zones=rep, skin_drop=float(1 - skin.mean()), edge_drop=float(1 - edge.mean()),
               hex_cov_deg=int(cov.sum())),
          open(f"{SC}/qa/_tier2_{TAG}.json", "w"), indent=1)
np.save(f"{SC}/qa/_dev_{TAG}.npy", np.c_[cp, d, gate.astype(float)])
print("saved _tier2_%s.json / _dev_%s.npy" % (TAG, TAG))
