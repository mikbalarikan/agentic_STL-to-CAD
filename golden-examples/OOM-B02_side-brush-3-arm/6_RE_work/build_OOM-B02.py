#!/usr/bin/env python3
"""
OOM-B02_Side-brush-3-arm  --  build123d parametric rebuild (REBUILD iteration 1)
=================================================================================
Reverse-engineered from Revopoint scan `2_mesh_cleaned/OOM-B02.stl` (798,874 tri)
+ photo-transcribed caliper readings (5_reference/MEASUREMENTS.md, PARTIAL sheet).

DATUM (frozen, RE_SPEC 3):
    cup rim annular face -> XY plane at Z = 0, material in +Z
    rotation axis        -> +Z
    arm 1 centreline     -> +X  (theta = 0);  arms 2/3 at +120 / -120 deg
    raw-scan -> datum 4x4 is in 2_mesh_cleaned/alignment.json ("matrix_4x4")

AUTHORITY (RE_SPEC 2):
    caliper-photo  F02 3.44 / F03 20.75 / F05 26.85 / F06 24.84 / F10 5.33 / F11 4.07
                   used DIRECTLY as CAD parameters (effective uncertainty +/-0.1 mm)
    scan           everything else (form + topology)
    NO global scale correction is applied (RE_SPEC 2 - the disagreement is not uniform)
    F01 hex AF = 7.358 from the scan fit, NOT intent-snapped to 7.0 / 7.5 (no caliper exists)

NOT MODELLED:  centre Phillips screw (COTS), bristle filaments (r > 38.5 mm)

Run:  /root/work/venv/bin/python build_OOM-B02.py [outdir]
"""
import sys, os, math
import numpy as np
from build123d import *

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# PARAMETERS   (see PARAM_TABLE.md for source tagging of every number)
# =============================================================================
# ---- hub, revolved meridian ----------------------------------------------
CUP_BORE_D      = 20.75      # caliper-photo F03  (scan 20.93)
CUP_BORE_R      = CUP_BORE_D / 2.0
CUP_BORE_STEP_Z = 1.30       # scan: bore is cylindrical rim -> this height, then draft
CUP_DRAFT_DEG   = 8.0        # scan-derived draft of the upper bore
CUP_FLOOR_Z     = 2.455      # scan (F04 uncalipered)
GROOVE_R0       = 6.60       # scan: annular relief groove in the cup floor
GROOVE_R1       = 9.80
GROOVE_RMID     = 8.20
GROOVE_DEPTH    = 0.337      # scan
RIM_Z           = 0.0        # DATUM A

SKIRT_R_LOBE    = 26.85 / 2  # caliper-photo F05 -> 13.425  (scan lobe 13.55)
SKIRT_R_FLAT    = 12.55      # it2/A2: F06 (24.84) STRUCK - not achievable as a two-jaw
                             # diametral reading on a 3-lobed skirt (PARAM_TABLE G-1).
                             # reverts to SCAN authority. it1 used 12.420 -> F06 +0.647 OOB.
FLAT_HALF_DEG   = 16.0       # scan: half-width of the arc that sits on an arm
RAMP_DEG        = 9.0        # scan: lobe<->flat transition
SKIRT_TOP_Z     = 8.0        # extent of the lobe cut (dome is inside R_FLAT above this)

HEX_AF          = 7.358      # SCAN FIT  (rms 0.037; NO caliper exists; NOT snapped)
HEX_PHASE_DEG   = 59.0       # scan: azimuth of a hex FLAT NORMAL, from arm 1
HEX_CORNER_R    = 0.35       # scan (AC/2 measured 4.126 vs sharp 4.248)
HEX_DEPTH       = 3.44       # caliper-photo F02 (scan 3.565)
HEX_FLOOR_Z     = CUP_FLOOR_Z + HEX_DEPTH        # 5.895

BORE_D          = 2.70       # scan at the hex-floor mouth; interior photo-inferred
CBORE_D         = 7.07       # scan (dome-side counterbore)
CBORE_FLOOR_Z   = 9.543      # scan
DOME_APEX_Z     = 10.866     # scan (clean sectors, arms excluded)

# dome meridian, scan-measured  (r, z) - clean (off-arm, off-SAF-1) sectors
DOME_PTS = [
    (13.425, 3.30), (13.38, 4.20), (13.25, 5.010), (13.00, 5.733), (12.75, 6.283),
    (12.50, 6.740), (12.25, 7.132), (12.00, 7.488), (11.75, 7.812), (11.50, 8.095),
    (11.25, 8.360), (11.00, 8.605), (10.75, 8.823), (10.50, 9.023), (10.25, 9.214),
    (10.00, 9.395), (9.75, 9.560), (9.50, 9.718), (9.25, 9.856), (9.00, 9.988),
    (8.75, 10.105), (8.50, 10.216), (8.25, 10.315), (8.00, 10.403), (7.75, 10.489),
    (7.50, 10.562), (7.25, 10.626), (7.00, 10.687), (6.75, 10.734), (6.50, 10.776),
    (6.25, 10.807), (6.00, 10.829), (5.75, 10.850), (5.50, 10.862), (5.00, 10.866),
    (4.50, 10.854), (4.00, 10.811), (3.75, 10.760), (CBORE_D / 2, 10.620),
]

# ---- SAF-1  (single-instance functional key, ruled 2026-07-29) -------------
SAF_THETA       = 59.0       # scan consensus: nub 57.6, recess 60.0, boss 61.5
SAF_RECESS_R    = 12.40      # scan: local skirt flattening
SAF_RECESS_HALF = 7.0        # deg, half-width of the flat part of the recess
SAF_RECESS_RAMP = 7.0        # deg
SAF_NUB_R       = 15.07      # scan
SAF_NUB_HALF    = 4.2        # deg  (measured span 53.5..61.9 = 8.4 deg)
SAF_NUB_Z0      = 2.35       # scan
SAF_NUB_Z1      = 4.02       # scan
SAF_HOLE_D      = 2.00       # scan / photo-inferred  -- KEY DATUM (Q5 fallback)
SAF_HOLE_Z      = 1.75       # scan (deepest penetration z 1.6-2.0)
SAF_HOLE_RIN    = 9.50       # photo-inferred (bottom occluded)
SAF_BOSS_TH0    = 45.0       # scan footprint
SAF_BOSS_TH1    = 78.0
SAF_BOSS_RI     = 4.30
SAF_BOSS_RM     = 8.00
SAF_BOSS_RO     = CUP_BORE_R + 0.075   # 0.075 into the bore wall so the union is not tangent
SAF_BOSS_Z_IN   = 1.45       # scan: inner pad face  (1.01 proud of the floor)
SAF_BOSS_Z_OUT  = 0.35       # scan: outer pad face  (2.11 proud of the floor)

# ---- arms -----------------------------------------------------------------
ARM_W           = 5.33       # caliper-photo F10 (scan mean 5.89 - R6 dilation)
ARM_CORNER_R    = 1.05       # scan (rounded-rectangular blade section)
ARM_R_END       = 38.20      # scan: plastic/bristle junction radius (38.23/38.22/38.19,
                             # spread 0.08). Everything beyond is bristle (R4) and is NOT modelled.
TUFT_SLOT_W     = 4.60       # scan 5.0 less the F10 width offset
TUFT_SLOT_T     = 3.50       # scan 3.9 less the F11 thickness offset
TUFT_SLOT_DEPTH = 3.00       # PHOTO-INFERRED (socket interior fully occluded), NOT gated
TUFT_SLOT_R     = 0.40

# arm stations: (r, z_mid, thickness, width)   z & thickness = 3-arm scan mean
#   r <= 13 : root extension, tapered so it is swallowed by the dome (scan shape)
ARM_STATIONS = [
    ( 7.00,  8.70, 2.20, 2.60),
    ( 8.00,  8.75, 2.80, 3.30),
    ( 9.00,  8.70, 3.40, 3.90),
    (10.00,  8.55, 4.00, 4.40),
    (11.00,  8.35, 4.50, 4.80),
    (12.00,  8.10, 5.00, 5.10),
    (13.00,  7.90, 5.45, ARM_W),
    (14.00,  7.93, 5.42, ARM_W),
    (16.00,  8.04, 5.33, ARM_W),
    (18.00,  8.16, 5.18, ARM_W),
    (20.00,  8.33, 4.91, ARM_W),
    (22.00,  8.56, 4.62, ARM_W),
    (24.00,  8.91, 4.34, ARM_W),
    (26.00,  9.43, 4.19, ARM_W),
    (28.00, 10.12, 4.10, ARM_W),
    (30.00, 10.96, 4.09, ARM_W),
    (32.00, 12.00, 4.14, ARM_W),
    (34.00, 13.04, 4.20, ARM_W),
    (36.00, 14.24, 4.15, ARM_W),
    (36.50, 14.58, 4.07, ARM_W),     # <-- caliper station F10/F11
    (37.50, 14.98, 3.98, ARM_W),
    (38.45, 15.40, 3.84, 5.08),   # trimmed back to r = 38.20 (plastic/bristle junction)
]

# =============================================================================
# 1. HUB - revolved meridian
# =============================================================================
bore_r_floor = CUP_BORE_R - (CUP_FLOOR_Z - CUP_BORE_STEP_Z) * math.tan(math.radians(CUP_DRAFT_DEG))

with BuildPart() as hub_b:
    with BuildSketch(Plane.XZ) as mer:
        with BuildLine() as ln:
            # --- cup interior (floor, annular relief groove, bore) -----------
            p_start = (BORE_D / 2, CUP_FLOOR_Z)
            Polyline(p_start, (GROOVE_R0, CUP_FLOOR_Z))
            ThreePointArc((GROOVE_R0, CUP_FLOOR_Z),
                          (GROOVE_RMID, CUP_FLOOR_Z + GROOVE_DEPTH),
                          (GROOVE_R1, CUP_FLOOR_Z))
            Polyline((GROOVE_R1, CUP_FLOOR_Z), (bore_r_floor, CUP_FLOOR_Z),
                     (CUP_BORE_R, CUP_BORE_STEP_Z), (CUP_BORE_R, RIM_Z),
                     (SKIRT_R_LOBE, RIM_Z), (SKIRT_R_LOBE, DOME_PTS[0][1]))
            # --- outer skirt -> dome (scan spline) ---------------------------
            Spline(*DOME_PTS, tangents=((0, 1), (-1, 0)))
            # --- dome-side counterbore + central through-bore -----------------
            Polyline(DOME_PTS[-1], (CBORE_D / 2, CBORE_FLOOR_Z),
                     (BORE_D / 2, CBORE_FLOOR_Z), p_start)
        make_face()
    revolve(axis=Axis.Z)
hub = hub_b.part

# =============================================================================
# 2. HEX DRIVE POCKET  (AF 7.358, clocked HEX_PHASE_DEG from arm 1)
# =============================================================================
Rc = HEX_AF / math.sqrt(3.0)                       # circumradius
hex_pts = [(Rc * math.cos(math.radians(HEX_PHASE_DEG + 30 + 60 * k)),
            Rc * math.sin(math.radians(HEX_PHASE_DEG + 30 + 60 * k))) for k in range(6)]
with BuildPart() as hexcut_b:
    with BuildSketch(Plane.XY.offset(-2.0)) as hs:
        with BuildLine():
            Polyline(*hex_pts, close=True)
        make_face()
        fillet(hs.vertices(), HEX_CORNER_R)
    extrude(amount=HEX_FLOOR_Z + 2.0)
hub = hub - hexcut_b.part

# =============================================================================
# 3. SKIRT 3-LOBE OUTLINE (+ SAF-1 recess) - cut the flats
# =============================================================================
def smoothstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)

# the lobe crest radius comes from the REVOLVE (exactly SKIRT_R_LOBE); the cut tool is
# held 0.02 mm clear of it so the two cylindrical faces are never tangent-coincident
# (tangent faces make the OCC boolean fail).
LOBE_TOOL = SKIRT_R_LOBE + 0.02

def skirt_r(theta_deg):
    """3-fold lobed skirt outline (cut-tool boundary), with the SAF-1 local recess."""
    d = ((theta_deg + 60.0) % 120.0) - 60.0          # -60..+60 from the nearest arm
    a = abs(d)
    if a <= FLAT_HALF_DEG:
        r = SKIRT_R_FLAT
    elif a >= FLAT_HALF_DEG + RAMP_DEG:
        r = LOBE_TOOL
    else:
        r = SKIRT_R_FLAT + (LOBE_TOOL - SKIRT_R_FLAT) * smoothstep((a - FLAT_HALF_DEG) / RAMP_DEG)
    ds = ((theta_deg - SAF_THETA + 180.0) % 360.0) - 180.0
    b = abs(ds)
    if b <= SAF_RECESS_HALF:
        rs = SAF_RECESS_R
    elif b >= SAF_RECESS_HALF + SAF_RECESS_RAMP:
        rs = 1e9
    else:
        rs = SAF_RECESS_R + (LOBE_TOOL - SAF_RECESS_R) * smoothstep(
            (b - SAF_RECESS_HALF) / SAF_RECESS_RAMP)
    return min(r, rs)

TH = np.arange(0.0, 360.0, 1.0)
outline = [(skirt_r(t) * math.cos(math.radians(t)), skirt_r(t) * math.sin(math.radians(t))) for t in TH]
with BuildPart() as lobecut_b:
    with BuildSketch(Plane.XY.offset(-1.0)):
        Circle(25.0)
        with BuildLine():
            Spline(*outline, *outline[:1])
        make_face(mode=Mode.SUBTRACT)
    extrude(amount=SKIRT_TOP_Z + 1.0)
hub = hub - lobecut_b.part

# =============================================================================
# 4. SAF-1  (nub + internal cup-floor boss + through hole)
# =============================================================================
def polar_sector(th0, th1, r0, r1, z0, z1, n=24):
    """solid polar sector between two radii / two angles / two heights"""
    pts = [(r1 * math.cos(math.radians(t)), r1 * math.sin(math.radians(t)))
           for t in np.linspace(th0, th1, n)]
    pts += [(r0 * math.cos(math.radians(t)), r0 * math.sin(math.radians(t)))
            for t in np.linspace(th1, th0, n)]
    with BuildPart() as b:
        with BuildSketch(Plane.XY.offset(z0)):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        extrude(amount=z1 - z0)
    return b.part

# 4a external nub
nub = polar_sector(SAF_THETA - SAF_NUB_HALF, SAF_THETA + SAF_NUB_HALF,
                   SAF_RECESS_R - 0.6, SAF_NUB_R, SAF_NUB_Z0, SAF_NUB_Z1)
hub = hub + nub
# 4b internal boss on the cup floor (two levels, scan-measured)
hub = hub + polar_sector(SAF_BOSS_TH0, SAF_BOSS_TH1, SAF_BOSS_RI, SAF_BOSS_RM,
                         SAF_BOSS_Z_IN, CUP_FLOOR_Z + GROOVE_DEPTH + 0.05)
hub = hub + polar_sector(SAF_BOSS_TH0, SAF_BOSS_TH1, SAF_BOSS_RM, SAF_BOSS_RO,
                         SAF_BOSS_Z_OUT, CUP_FLOOR_Z + GROOVE_DEPTH + 0.05)
# 4c the hole - KEY DATUM
u = (math.cos(math.radians(SAF_THETA)), math.sin(math.radians(SAF_THETA)), 0.0)
hole = Plane(origin=(SAF_HOLE_RIN * u[0], SAF_HOLE_RIN * u[1], SAF_HOLE_Z),
             z_dir=u) * Cylinder(SAF_HOLE_D / 2, 16.0,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
hub = hub - hole

# =============================================================================
# 5. ARMS  (one swept/lofted blade, then PolarArray 3 x 120.00 deg)
# =============================================================================
st = np.array(ARM_STATIONS)
sections = []
for i, (rr, zz, tt, ww) in enumerate(st):
    if i == 0:
        dr, dz = st[1][0] - st[0][0], st[1][1] - st[0][1]
    elif i == len(st) - 1:
        dr, dz = st[-1][0] - st[-2][0], st[-1][1] - st[-2][1]
    else:
        dr, dz = st[i + 1][0] - st[i - 1][0], st[i + 1][1] - st[i - 1][1]
    n = math.hypot(dr, dz)
    pl = Plane(origin=(rr, 0, zz), z_dir=(dr / n, 0, dz / n), x_dir=(0, 1, 0))
    rad = min(ARM_CORNER_R, 0.45 * min(ww, tt))
    sections.append(pl * RectangleRounded(ww, tt, rad))
arm = loft(sections)

# tuft slot: blind, cut from the r = ARM_R_END end face inward
r_e, z_e, t_e, w_e = st[-1]
dr, dz = st[-1][0] - st[-2][0], st[-1][1] - st[-2][1]
n = math.hypot(dr, dz)
pl_e = Plane(origin=(r_e, 0, z_e), z_dir=(dr / n, 0, dz / n), x_dir=(0, 1, 0))
slot = pl_e * extrude(RectangleRounded(TUFT_SLOT_W, TUFT_SLOT_T, TUFT_SLOT_R),
                      amount=-TUFT_SLOT_DEPTH)
arm = arm - slot

for k in range(3):
    hub = hub + Rotation(0, 0, 120.0 * k) * arm

# hard radial limit: everything beyond the plastic/bristle junction is NOT modelled (R4)
hub = hub & Cylinder(ARM_R_END, 60.0)

# =============================================================================
# 6. FILLETS (last, from the sections)
# =============================================================================
part = hub
# arm / hub blend: the union seam sits on the dome flank, r ~ 11-14, z ~ 8-11
seam = [e for e in part.edges()
        if 7.0 < e.center().Z < 11.2 and 6.0 < math.hypot(e.center().X, e.center().Y) < 15.0]
for rad in (0.8, 0.5, 0.3):
    try:
        part = fillet(seam, rad)
        print("  arm/hub blend fillet R%.1f on %d edges" % (rad, len(seam)))
        break
    except Exception as exc:
        print("  [fillet R%.1f failed] %s" % (rad, str(exc)[:70]))

# =============================================================================
# 7. VALIDATE + EXPORT
# =============================================================================
solids = part.solids()
iv = part.is_valid
print("is_valid      :", iv() if callable(iv) else iv)
print("solid count   :", len(solids))
print("volume  (mm3) : %.3f" % part.volume)
print("area    (mm2) : %.3f" % part.area)
print("bbox          :", [round(v, 3) for v in list(part.bounding_box().min) + list(part.bounding_box().max)])

os.makedirs(OUT, exist_ok=True)
export_step(part, os.path.join(OUT, "OOM-B02.step"))
export_stl(part, os.path.join(OUT, "OOM-B02_cad.stl"), tolerance=0.02, angular_tolerance=0.15)
print("wrote", os.path.join(OUT, "OOM-B02.step"))
