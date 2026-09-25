"""QA-1/2/4 on the delivered STEP: BRep validity, tessellation health, Tier-1 re-measure.

Every dimension is taken off the TESSELLATED SOLID with a simulated two-parallel-jaw
caliper (support function of the section polygon).  No build parameter is read back.
"""
import sys, os, math, json
import numpy as np, trimesh
from build123d import import_step, export_stl
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import (TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX)
from OCP.BRep import BRep_Tool
from OCP.TopoDS import TopoDS

STEP = sys.argv[1]
TAG  = sys.argv[2] if len(sys.argv) > 2 else "it2"
SC   = "/root/projects/oomwoo_b02/scratch"
FINE = f"{SC}/qa/_fine_{TAG}.stl"
out  = {}

# ---------------- QA-1  BRep validity -------------------------------------
shape = import_step(STEP)
tds = shape.wrapped
cnt = {}
for nm, tp in [("solid", TopAbs_SOLID), ("shell", TopAbs_SHELL), ("face", TopAbs_FACE),
               ("edge", TopAbs_EDGE), ("vertex", TopAbs_VERTEX)]:
    e = TopExp_Explorer(tds, tp); n = 0
    while e.More(): n += 1; e.Next()
    cnt[nm] = n
valid = BRepCheck_Analyzer(tds).IsValid()
out["qa1"] = dict(counts=cnt, brepcheck_valid=bool(valid),
                  volume=shape.volume, area=shape.area,
                  bbox=[*shape.bounding_box().min, *shape.bounding_box().max])
print("QA-1 BRep : valid=%s  solids=%d shells=%d faces=%d edges=%d  vol %.3f mm3"
      % (valid, cnt["solid"], cnt["shell"], cnt["face"], cnt["edge"], shape.volume))

# ---------------- QA-2  tessellation health -------------------------------
if not os.path.exists(FINE) or os.path.getmtime(FINE) < os.path.getmtime(STEP):
    export_stl(shape, FINE, tolerance=0.005, angular_tolerance=0.05)
m = trimesh.load(FINE, process=True)
deg = (m.area_faces < 1e-9).sum()
out["qa2"] = dict(tris=len(m.faces), watertight=bool(m.is_watertight),
                  winding=bool(m.is_winding_consistent), euler=int(m.euler_number),
                  components=int(m.body_count), volume=float(m.volume),
                  degenerate_faces=int(deg), volume_vs_brep=float(m.volume - shape.volume))
print("QA-2 tess : %d tri  watertight=%s winding=%s euler=%d comps=%d degen=%d  vol %.3f (Δbrep %+.3f)"
      % (len(m.faces), m.is_watertight, m.is_winding_consistent, m.euler_number,
         m.body_count, deg, m.volume, m.volume - shape.volume))

# ---------------- caliper simulation --------------------------------------
def densify(p, ds=0.02):
    o = []
    for i in range(len(p) - 1):
        d = np.linalg.norm(p[i + 1] - p[i]); n = max(int(d / ds), 1)
        for k in range(n): o.append(p[i] + (p[i + 1] - p[i]) * (k / n))
    o.append(p[-1]); return np.array(o)

def jaws(pts2d, step=0.05):
    """support-function width over jaw azimuth: what two parallel jaws actually read"""
    a = np.radians(np.arange(0, 180, step))
    v = np.stack([np.cos(a), np.sin(a)], 1)
    q = pts2d @ v.T
    return np.c_[np.degrees(a), q.max(0) - q.min(0)]

def zsec(zz):
    s = m.section(plane_origin=[0, 0, zz], plane_normal=[0, 0, 1])
    return [s.vertices[e.points][:, :2] for e in s.entities]

def meridian(th):
    a = math.radians(th)
    u = np.array([math.cos(a), math.sin(a), 0.0]); n = np.array([-math.sin(a), math.cos(a), 0.0])
    s = m.section(plane_origin=[0, 0, 0], plane_normal=n)
    return [np.c_[s.vertices[e.points] @ u, s.vertices[e.points][:, 2]] for e in s.entities]

# ---------------- QA-4  Tier-1 -------------------------------------------
T1 = {}
# --- skirt OD, jaws on the band 1 mm above the rim ---
pts = np.vstack([densify(p) for p in zsec(1.00)])
rr = np.hypot(pts[:, 0], pts[:, 1]); tt = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
TH = np.arange(-180, 180, 0.25)
Rout = np.array([rr[np.abs(((tt - t + 180) % 360) - 180) < 0.3].max() for t in TH])
env = np.c_[Rout * np.cos(np.radians(TH)), Rout * np.sin(np.radians(TH))]
w = jaws(env)
T1["F05"] = ("skirt OD MAX", 26.85, float(w[:, 1].max()), True)
T1["F06"] = ("skirt OD MIN (STRUCK, A2)", None, float(w[:, 1].min()), False)
print("QA-4 skirt: R env %.3f..%.3f ; two-jaw window %.3f .. %.3f"
      % (Rout.min(), Rout.max(), w[:, 1].min(), w[:, 1].max()))

# --- cup bore ID ---
inner = densify(min(zsec(1.00), key=lambda p: np.hypot(p[:, 0], p[:, 1]).max()))
T1["F03"] = ("cup bore ID", 20.75, float(2 * np.hypot(inner[:, 0], inner[:, 1]).max()), True)

# --- hex pocket depth + AF ---
P = np.vstack([densify(x) for x in meridian(180.0)])
cup_floor = float(np.median(P[(P[:, 0] > 4.6) & (P[:, 0] < 6.3) & (P[:, 1] > 2.0) & (P[:, 1] < 3.0), 1]))
hexf = float(np.median(P[(np.abs(P[:, 0]) > 1.5) & (np.abs(P[:, 0]) < 3.3)
                         & (P[:, 1] > 5.0) & (P[:, 1] < 6.6), 1]))
T1["F02"] = ("hex pocket depth", 3.44, hexf - cup_floor, True)
hexp = densify(min(zsec(0.5 * (cup_floor + hexf)), key=lambda p: np.hypot(p[:, 0], p[:, 1]).max()))
wh = jaws(hexp, step=0.02)
T1["F01"] = ("hex AF (SCAN authority, ungated)", 7.358, float(wh[:, 1].min()), False)

# --- arm section at the caliper station r = 36.5 ---
V = m.vertices
r = np.hypot(V[:, 0], V[:, 1]); z = V[:, 2]; th = np.degrees(np.arctan2(V[:, 1], V[:, 0]))
arm = np.abs(((th + 180) % 360) - 180) < 14
zc = {rr0: 0.5 * (z[arm & (np.abs(r - rr0) < 0.25)].min() + z[arm & (np.abs(r - rr0) < 0.25)].max())
      for rr0 in (35.5, 36.5, 37.5)}
tang = np.array([2.0, 0.0, zc[37.5] - zc[35.5]]); tang /= np.linalg.norm(tang)
sec = m.section(plane_origin=[36.5, 0, zc[36.5]], plane_normal=tang)
sp = np.vstack([densify(sec.vertices[e.points]) for e in sec.entities])
sp = sp[np.hypot(sp[:, 0], sp[:, 1]) > 30]
xd = np.array([0., 1., 0.]); yd = np.cross(tang, xd)
T1["F10"] = ("arm width @r36.5", 5.33, float((sp @ xd).max() - (sp @ xd).min()), True)
T1["F11"] = ("arm thickness @r36.5", 4.07, float((sp @ yd).max() - (sp @ yd).min()), True)

print("\n---- TIER-1 (band |CAD-caliper| <= 0.15 mm) ----")
worst = 0.0
for k in ["F02", "F03", "F05", "F10", "F11"]:
    nm, cal, cad, gated = T1[k]
    d = cad - cal; worst = max(worst, abs(d))
    print("  %s %-26s caliper %8.3f  CAD %8.3f  d %+7.3f  %s"
          % (k, nm, cal, cad, d, "PASS" if abs(d) <= 0.15 else "** FAIL **"))
for k in ["F01", "F06"]:
    nm, cal, cad, _ = T1[k]
    print("  %s %-26s ref %s  CAD %8.3f  (ungated)"
          % (k, nm, ("%8.3f" % cal) if cal else "   —    ", cad))
print("  Tier-1 worst gated |delta| = %.3f mm over 5 gated dims; 17 of 24 sheet dims ABSENT" % worst)

out["qa4"] = {k: dict(name=v[0], caliper=v[1], cad=v[2], gated=v[3]) for k, v in T1.items()}
out["qa4_worst_gated"] = worst
out["form"] = dict(rigid_tip_D=float(2 * r.max()), height=float(z.max()),
                   dome_apex=float(max(P[(np.abs(P[:, 0]) > 3.7) & (np.abs(P[:, 0]) < 7.0), 1])),
                   cup_floor_z=cup_floor, hex_floor_z=hexf)
print("\n---- form ----")
print("  rigid arm-tip swept D %.3f (scan 76.43) | height %.3f (scan p99.9 17.10) | dome apex %.3f (scan 10.866)"
      % (2 * r.max(), z.max(), out["form"]["dome_apex"]))
json.dump(out, open(f"{SC}/qa/_qa_{TAG}.json", "w"), indent=1)
print("saved _qa_%s.json" % TAG)
