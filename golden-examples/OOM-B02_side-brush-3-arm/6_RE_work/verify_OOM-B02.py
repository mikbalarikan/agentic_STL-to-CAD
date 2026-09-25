"""Independent re-measure of the Tier-1 dims ON THE BUILT SOLID.

Method: re-import 4_STEP/OOM-B02.step with build123d -> tessellate at 5 um chordal
tolerance -> measure with plane sections + support (caliper) widths.  Nothing is read
back from the build parameters; every number below comes off the tessellated solid.
"""
import sys, os, math
import numpy as np
import trimesh
from build123d import import_step, export_stl

SC = "/root/projects/oomwoo_b02/scratch"
STEP = sys.argv[1] if len(sys.argv) > 1 else f"{SC}/out/OOM-B02.step"
FINE = f"{SC}/_verify_fine.stl"
if not os.path.exists(FINE) or os.path.getmtime(FINE) < os.path.getmtime(STEP):
    export_stl(import_step(STEP), FINE, tolerance=0.005, angular_tolerance=0.05)
m = trimesh.load(FINE, process=True)
print("CAD tessellation : %d tri  watertight=%s  volume=%.3f mm3" % (len(m.faces), m.is_watertight, m.volume))
res = {}

def zsec(zz):
    s = m.section(plane_origin=[0, 0, zz], plane_normal=[0, 0, 1])
    return [s.vertices[e.points][:, :2] for e in s.entities]

def meridian(th_deg):
    """section on the plane containing +Z at azimuth th; returns (r_signed, z)"""
    a = math.radians(th_deg)
    u = np.array([math.cos(a), math.sin(a), 0.0])
    n = np.array([-math.sin(a), math.cos(a), 0.0])
    s = m.section(plane_origin=[0, 0, 0], plane_normal=n)
    segs = []
    for e in s.entities:
        p = s.vertices[e.points]
        segs.append(np.c_[p @ u, p[:, 2]])
    return segs

def densify(p, ds=0.02):
    """resample a polyline so angular/positional statistics are not vertex-limited"""
    out = []
    for i in range(len(p) - 1):
        d = np.linalg.norm(p[i + 1] - p[i])
        n = max(int(d / ds), 1)
        for k in range(n):
            out.append(p[i] + (p[i + 1] - p[i]) * (k / n))
    out.append(p[-1])
    return np.array(out)


def support_width(pts2d, step=0.05):
    w = []
    for d in np.arange(0, 180, step):
        v = np.array([math.cos(math.radians(d)), math.sin(math.radians(d))])
        q = pts2d @ v
        w.append((d, q.max() - q.min()))
    return np.array(w)

print("\n================  TIER-1 SELF-CHECK ON THE BUILT SOLID  ================")

# ---- F05 / F06 : skirt OD, outside jaws ~1 mm above the rim ---------------
# a caliper cannot enter the SAF-1 hole -> take the OUTER envelope R(theta)
pts = np.vstack([densify(p) for p in zsec(1.00)])
rr = np.hypot(pts[:, 0], pts[:, 1]); tt = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
TH = np.arange(-180, 180, 0.25)
Rout = np.array([rr[np.abs(((tt - t + 180) % 360) - 180) < 0.3].max() for t in TH])
env = np.c_[Rout * np.cos(np.radians(TH)), Rout * np.sin(np.radians(TH))]
w = support_width(env)
res['F05'] = (26.85, w[:, 1].max()); res['F06'] = (24.84, w[:, 1].min())
print("F05 skirt OD MAX  caliper 26.850  CAD %.3f  (jaws @ %.2f deg)" % (w[:, 1].max(), w[np.argmax(w[:, 1]), 0]))
print("F06 skirt OD MIN  caliper 24.840  CAD %.3f  (jaws @ %.2f deg)" % (w[:, 1].min(), w[np.argmin(w[:, 1]), 0]))
print("     CAD skirt radius envelope %.3f .. %.3f   -> 2*Rmin %.3f / 2*Rmax %.3f"
      % (Rout.min(), Rout.max(), 2 * Rout.min(), 2 * Rout.max()))

# ---- F03 : cup bore ID, inside jaws ~1 mm above the rim -------------------
inner = densify(min(zsec(1.00), key=lambda p: np.hypot(p[:, 0], p[:, 1]).max()))
ri = np.hypot(inner[:, 0], inner[:, 1])
# inside jaws seek the LARGEST separation they can reach = the bore diameter
wi = support_width(inner)
res['F03'] = (20.75, 2 * ri.max())
print("F03 cup bore ID   caliper 20.750  CAD %.3f  (bore wall r=%.4f; inside-jaw max span %.3f)"
      % (2 * ri.max(), ri.max(), wi[:, 1].max()))

# ---- F02 : hex pocket depth below the cup floor ---------------------------
segs = meridian(180.0)
P = np.vstack([densify(x) for x in segs])
k = (P[:, 0] > 4.6) & (P[:, 0] < 6.3)
cup_floor = np.median(P[k & (P[:, 1] > 2.0) & (P[:, 1] < 3.0), 1])
k2 = (np.abs(P[:, 0]) > 1.5) & (np.abs(P[:, 0]) < 3.3) & (P[:, 1] > 5.0) & (P[:, 1] < 6.6)
hex_floor = np.median(P[k2, 1])
res['F02'] = (3.44, hex_floor - cup_floor)
print("F02 hex depth     caliper  3.440  CAD %.3f  (cup floor z=%.4f, pocket floor z=%.4f)"
      % (hex_floor - cup_floor, cup_floor, hex_floor))

# ---- F01 : hex across-flats (SCAN authority, ungated - no caliper exists) --
zh = 0.5 * (cup_floor + hex_floor)
hexp = densify(min(zsec(zh), key=lambda p: np.hypot(p[:, 0], p[:, 1]).max()))
wh = support_width(hexp, step=0.02)
res['F01'] = (7.358, wh[:, 1].min())
print("F01 hex AF        scan     7.358  CAD %.4f (min jaw span @ %.2f deg); AC %.4f"
      % (wh[:, 1].min(), wh[np.argmin(wh[:, 1]), 0], wh[:, 1].max()))

# ---- F10 / F11 : arm width & thickness at the caliper station r = 36.5 ----
V = m.vertices
r = np.hypot(V[:, 0], V[:, 1]); z = V[:, 2]; th = np.degrees(np.arctan2(V[:, 1], V[:, 0]))
arm = np.abs(((th + 180) % 360) - 180) < 14
zc = {}
for rr0 in (35.5, 36.5, 37.5):
    s = arm & (np.abs(r - rr0) < 0.25)
    zc[rr0] = 0.5 * (z[s].min() + z[s].max())
tang = np.array([2.0, 0.0, zc[37.5] - zc[35.5]]); tang /= np.linalg.norm(tang)
sec = m.section(plane_origin=[36.5, 0, zc[36.5]], plane_normal=tang)
pts = np.vstack([densify(sec.vertices[e.points]) for e in sec.entities])
pts = pts[np.hypot(pts[:, 0], pts[:, 1]) > 30]
xdir = np.array([0., 1., 0.]); ydir = np.cross(tang, xdir)
wid = (pts @ xdir).max() - (pts @ xdir).min()
thk = (pts @ ydir).max() - (pts @ ydir).min()
res['F10'] = (5.33, wid); res['F11'] = (4.07, thk)
print("F10 arm width  @r36.5 caliper 5.330  CAD %.3f" % wid)
print("F11 arm thick  @r36.5 caliper 4.070  CAD %.3f" % thk)

print("\n---- Tier-1 deltas (CAD - caliper); band |d| <= 0.15 mm ----")
for k in ['F02', 'F03', 'F05', 'F06', 'F10', 'F11']:
    cal, cad = res[k]
    d = cad - cal
    print("  %s  caliper %8.3f  CAD %8.3f  delta %+7.3f  %s"
          % (k, cal, cad, d, "PASS" if abs(d) <= 0.15 else "** OUT OF BAND **"))
cal, cad = res['F01']
print("  F01  SCAN    %8.3f  CAD %8.3f  delta %+7.3f  (ungated - no caliper exists)" % (cal, cad, cad - cal))

print("\n---- envelope / form checks on the built solid ----")
print("  rigid arm-tip swept D  %.3f   (scan 76.43)" % (2 * r.max()))
print("  overall height rim->top %.3f  (scan p99.9 17.10)" % z.max())
print("  dome apex z            %.3f   (scan 10.866)" % max(P[(np.abs(P[:, 0]) > 3.7) & (np.abs(P[:, 0]) < 7.0), 1]))
print("  bbox                   %s" % np.round(m.bounds, 3).tolist())
