"""
Rebuild OOM-P03 Mop Pad Bracket (rotating mop-pad carrier plate) as a clean
parametric STEP solid.  stl2step-build123d pipeline.

Datum: hex/rotation axis -> +Z (toward DRIVE side); PAD-attach velcro field -> Z=0;
all rings concentric on Z.  Composite raw-scan->datum transform in
2_mesh_cleaned/alignment.json (matrix_4x4).

Data authority (RE_SPEC v2 s2): CALIPER for every covered dimension (used directly),
SCAN for form/levels, PHOTO for intent.  See PARAM_TABLE.md for source per param.
"""
from build123d import *
import math, os, sys

# ------------------------------------------------------------------ PARAMETERS
# --- CALIPER (Tier-1, used directly) ---
RIM_OD      = 127.54      # ENV-D1 solid-rim OD
W01_WALL    = 3.27        # rim edge wall thickness
HEX_AF      = 13.95       # F01 hex across-flats  (across-corners = 16.11 auto)
HEX_PROTR   = 11.05       # F03 hex protrusion above surrounding drive-face floor
PADBOSS_OD  = 33.46       # F05 pad-side central round boss OD
HUB_OD      = 68.61       # F06 hub disc OD  == inner edge of kidney-opening ring
MIDRING_OD  = 89.33       # F07 spoke-disc / mid-ring OD == outer edge of opening ring
# --- SCAN (form / axial levels), datum Z=0 = pad field ---
Z_PAD        = 0.0        # pad-attach (velcro) field plane
Z_DRIVE      = 2.85       # drive-face plane (plate top)   [W03 plate thk ~2.85, scan]
Z_RIMBOT     = Z_DRIVE - W01_WALL   # rim pad-side face (wall = W01)  = -0.42
Z_PADBOSS    = -3.01      # pad-boss bottom face (proud 3.01 below field, scan)
N_KIDNEY     = 8          # kidney openings (scan-confirmed 8-fold: F[8]=144.6, spokes @45deg)
KIDNEY_PHASE = math.radians(2.5)    # opening centers at 2.5 + k*45 deg (spokes at 25 + k*45)
KIDNEY_HALF  = math.radians(14.6)   # half angular width (~29 deg opening; ~16 deg spoke)
N_TREAD      = 51         # tread slots (scan, cosmetic; pitch ~7.0 deg)
TREAD_RIN    = 58.6       # tread slot inner radius (scan)
TREAD_ROUT   = 63.4       # tread slot outer radius (through the rim band, scan)
TREAD_WHALF  = math.radians(2.4)    # tread slot half angular width (~4.8 deg slot)
FILLET_SMALL = 0.6

R_RIM  = RIM_OD/2.0
R_HUB  = HUB_OD/2.0        # 34.305  opening inner edge
R_MID  = MIDRING_OD/2.0    # 44.665  opening outer edge
R_BOSS = PADBOSS_OD/2.0    # 16.73
HEX_CIRC = HEX_AF/math.sqrt(3.0)     # circumradius (across-corners/2) = 8.055
Z_HEXTIP = Z_DRIVE + HEX_PROTR       # 13.90
# --- central drive STEM above the hex (SCAN authority; no caliper covers it) ---
# scan (158k coherent raw verts): hexagonal post, flats r5.48 corners r6.41, solid top +18.556
STEM_AF     = 10.96      # across-flats (2*5.48), hexagonal
STEM_TOP    = 18.56      # stem top face Z (scan)  -> ENV-Z = STEM_TOP - Z_PADBOSS = 21.57
STEM_ROT    = 48.0       # deg, corner orientation (scan corners at ~48+k*60)
# square drive socket recess in the stem tip (photo IMG_140345/347; scan bridged it)
SOCKET_SQ   = 5.5        # square across-flats (photo-inferred)
SOCKET_DEPTH= 2.5        # recess depth (photo-inferred; scan supports shallow)
STEM_CIRC   = STEM_AF/math.sqrt(3.0)   # 6.328

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

# ------------------------------------------------------ 1. BASE REVOLVE PROFILE
# closed half-section in the X(=r)-Z plane, revolved about Z.
pts = [
    (0.0,      Z_DRIVE),         # axis, drive face
    (R_RIM,    Z_DRIVE),         # drive face out to rim OD
    (R_RIM,    Z_RIMBOT),        # rim outer wall down (wall = W01)
    (R_MID,    Z_RIMBOT),        # rim pad-side face inward
    (R_MID,    Z_PAD),           # step up to pad field
    (R_BOSS,   Z_PAD),           # pad field inward to boss
    (R_BOSS,   Z_PADBOSS),       # pad-boss outer wall down
    (0.0,      Z_PADBOSS),       # pad-boss bottom to axis
]
with BuildPart() as part:
    with BuildSketch(Plane.XZ) as prof:
        with BuildLine():
            n = len(pts)
            for i in range(n):
                Line(pts[i], pts[(i+1) % n])
        make_face()
    revolve(axis=Axis.Z)

    base = part.part
    if base.volume <= 0:
        base = base.mirror(Plane.XY)  # ensure positive orientation (safety)

# ------------------------------------------------------ 2. HEX BOSS (drive side)
with BuildPart() as hexb:
    with BuildSketch(Plane.XY.offset(Z_DRIVE)):
        RegularPolygon(radius=HEX_CIRC, side_count=6, major_radius=True)
    extrude(amount=HEX_PROTR)
hex_solid = hexb.part

# central drive STEM (hexagonal) on top of the hex, up to +18.56 (scan)
with BuildPart() as stemb:
    with BuildSketch(Plane.XY.offset(Z_HEXTIP)) as sst:
        RegularPolygon(radius=STEM_CIRC, side_count=6, major_radius=True,
                       rotation=STEM_ROT)
    extrude(amount=STEM_TOP - Z_HEXTIP)
stem_solid = stemb.part

# square drive socket recess in the stem tip
with BuildPart() as sock:
    with BuildSketch(Plane.XY.offset(STEM_TOP - SOCKET_DEPTH)):
        Rectangle(SOCKET_SQ, SOCKET_SQ)
    extrude(amount=SOCKET_DEPTH + 0.5)
socket_solid = sock.part

# --------------------------------------------- 3. CUT TOOLS (kidneys + tread)
def sector_tool(r_in, r_out, ang0, half, z_bot, z_top, corner_r):
    """annular-sector cut solid with rounded corners, spanning z_bot..z_top."""
    hd = math.degrees(half)
    a0 = math.degrees(ang0)
    with BuildPart() as tp:
        with BuildSketch(Plane.XY.offset(z_bot)) as sk:
            with BuildLine():
                CenterArc((0, 0), r_in,  a0 - hd, 2*hd)
                Line((r_in*math.cos(ang0+half),  r_in*math.sin(ang0+half)),
                     (r_out*math.cos(ang0+half), r_out*math.sin(ang0+half)))
                CenterArc((0, 0), r_out, a0 - hd, 2*hd)
                Line((r_in*math.cos(ang0-half),  r_in*math.sin(ang0-half)),
                     (r_out*math.cos(ang0-half), r_out*math.sin(ang0-half)))
            make_face()
            if corner_r > 0:
                try:
                    fillet(sk.vertices(), corner_r)
                except Exception as e:
                    print("sector corner-fillet skipped:", e)
        extrude(amount=(z_top - z_bot))
    return tp.part

cut_tools = []
# kidney openings through the plate, 6-fold
for k in range(N_KIDNEY):
    ang = 2*math.pi*k/N_KIDNEY + KIDNEY_PHASE
    cut_tools.append(sector_tool(R_HUB, R_MID, ang, KIDNEY_HALF,
                                 Z_PAD-1.0, Z_DRIVE+1.0, 3.0))
# tread slots through the rim band, N_TREAD-fold (cosmetic)
for k in range(N_TREAD):
    ang = 2*math.pi*k/N_TREAD
    cut_tools.append(sector_tool(TREAD_RIN, TREAD_ROUT, ang, TREAD_WHALF,
                                 Z_RIMBOT-0.5, Z_DRIVE+0.5, 1.0))

# ------------------------------------------------------ 4. BOOLEAN ASSEMBLY
solid = base
solid = solid + hex_solid
solid = solid + stem_solid
tools = cut_tools[0]
for t in cut_tools[1:]:
    tools = tools + t
solid = solid - tools
solid = solid - socket_solid     # square drive socket recess

# ------------------------------------------------------ 5. FILLETS (light breaks)
try:
    # break the stem top outer edges
    top_edges = solid.edges().filter_by_position(Axis.Z, STEM_TOP-0.05, STEM_TOP+0.05)
    top_edges = top_edges.filter_by(lambda e: e.center().length > SOCKET_SQ)  # skip socket rim
    if top_edges:
        solid = fillet(top_edges, 0.4)
except Exception as e:
    print("fillet stem-top skipped:", e)

# ------------------------------------------------------ 6. VALIDATE & EXPORT
v = solid.volume
print("volume mm3 = %.1f" % v)
_iv = getattr(solid, "is_valid", None)
print("is_valid   =", _iv() if callable(_iv) else _iv)
bb = solid.bounding_box()
print("bbox min", [round(x,3) for x in bb.min.to_tuple()])
print("bbox max", [round(x,3) for x in bb.max.to_tuple()])
# solid count
try:
    ns = len(solid.solids()); print("n_solids =", ns)
except Exception:
    ns = 1
assert v > 0, "non-positive volume"

step_path = os.path.join(OUT_DIR, "OOM-P03.step")
stl_path  = os.path.join(OUT_DIR, "OOM-P03_cad.stl")
export_step(solid, step_path)
export_stl(solid, stl_path)
# fine gauge mesh for self-gate re-measure (not a deliverable)
try:
    export_stl(solid, os.path.join(OUT_DIR, "OOM-P03_gauge.stl"),
               tolerance=0.02, angular_tolerance=0.1)
except Exception as e:
    print("fine export fallback:", e); export_stl(solid, os.path.join(OUT_DIR,"OOM-P03_gauge.stl"))
print("wrote", step_path)
print("wrote", stl_path)
