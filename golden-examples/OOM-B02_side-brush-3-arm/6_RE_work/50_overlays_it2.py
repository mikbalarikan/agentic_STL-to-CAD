"""Section overlays: datum-aligned SCAN vs CAD, same axes, mm gridlines, legend."""
import os, math, sys
import numpy as np
import trimesh
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SC = "/root/projects/oomwoo_b02/scratch"
SCAN = trimesh.load(f"{SC}/OOM-B02_raw_datum.stl", process=False)
CAD = trimesh.load(f"{SC}/qa/_fine_it2.stl", process=False)
CSCAN, CCAD = "#1f77b4", "#d62728"
LSCAN, LCAD = "SCAN (datum-aligned, 798k tri)", "CAD it2 (OOM-B02.step)"


def meridian_segs(mesh, th_deg):
    a = math.radians(th_deg)
    u = np.array([math.cos(a), math.sin(a), 0.0])
    n = np.array([-math.sin(a), math.cos(a), 0.0])
    s = mesh.section(plane_origin=[0, 0, 0], plane_normal=n)
    if s is None: return []
    return [np.c_[s.vertices[e.points] @ u, s.vertices[e.points][:, 2]] for e in s.entities]


def plan_segs(mesh, zz):
    s = mesh.section(plane_origin=[0, 0, zz], plane_normal=[0, 0, 1])
    if s is None: return []
    return [s.vertices[e.points][:, :2] for e in s.entities]


def normal_segs(mesh, origin, normal, u, v):
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    if s is None: return []
    out = []
    for e in s.entities:
        p = s.vertices[e.points] - np.asarray(origin)
        out.append(np.c_[p @ u, p @ v])
    return out


def draw(ax, segs, colour, label, lw=1.4):
    first = True
    for p in segs:
        ax.plot(p[:, 0], p[:, 1], color=colour, lw=lw, label=label if first else None,
                solid_joinstyle="round")
        first = False


def finish(ax, title, xlab, ylab, xlim=None, ylim=None, tick=2.0, minor=0.5):
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlab); ax.set_ylabel(ylab)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    ax.xaxis.set_major_locator(plt.MultipleLocator(tick)); ax.yaxis.set_major_locator(plt.MultipleLocator(tick))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(minor)); ax.yaxis.set_minor_locator(plt.MultipleLocator(minor))
    ax.grid(which="major", color="0.55", lw=0.7, alpha=0.8)
    ax.grid(which="minor", color="0.80", lw=0.4, alpha=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.92)


def annot(ax, txt, x=0.012, y=0.012):
    ax.text(x, y, txt, transform=ax.transAxes, fontsize=7.6, va="bottom", ha="left",
            family="monospace", bbox=dict(fc="white", ec="0.7", alpha=0.9, pad=3))


# ---------------------------------------------------------------- (a) meridian thru arm 1
fig, ax = plt.subplots(figsize=(15, 7.2))
draw(ax, meridian_segs(SCAN, 0.0), CSCAN, LSCAN)
draw(ax, meridian_segs(CAD, 0.0), CCAD, LCAD)
finish(ax, "OOM-B02  (a) HUB MERIDIAN through ARM 1  (theta = 0 / 180 deg)  --  scan vs CAD",
       "radius r (mm)   [+r = arm 1 at theta 0, -r = theta 180]", "z (mm)  [0 = cup rim annular face]",
       (-20, 42), (-2, 20), 2.0, 0.5)
annot(ax, "datum: rim annulus -> z=0, material +Z, axis -> +Z, arm 1 -> +X.  CAD plastic stops at r=38.20\n"
          "(scan plastic/bristle junction); the blue trace beyond that is filament and is NOT modelled.\n"
          "The CAD arm path is the 3-ARM MEAN z(r).  Arm 1 is the LOWEST of the three (per-arm zmid at\n"
          "r=36: 13.50 / 14.46 / 14.75) so the CAD reads ~0.74 mm HIGH here and ~0.51 mm LOW on arm 3.\n"
          "That 1.25 mm arm-to-arm spread is free-state droop (Q4 ruling) and is deliberately not chased.")
plt.tight_layout(); plt.savefig(f"{SC}/B02_S1_meridian_arm1.png", dpi=140); plt.close()

# ---------------------------------------------------------------- (b) meridian thru SAF-1
fig, ax = plt.subplots(figsize=(13, 7.5))
draw(ax, meridian_segs(SCAN, 59.0), CSCAN, LSCAN)
draw(ax, meridian_segs(CAD, 59.0), CCAD, LCAD)
finish(ax, "OOM-B02  (b) HUB MERIDIAN through the SAF-1 CLOCKING  (theta = 59 / 239 deg)  --  scan vs CAD",
       "radius r (mm)   [+r = SAF-1 side]", "z (mm)", (-18, 18), (-2, 13), 1.0, 0.25)
annot(ax, "SAF-1 = the single 3-fold-breaking functional key (Q1 ruling): skirt recess to R 12.40,\n"
          "external nub to R 15.07 (z 2.35-4.02), radial hole Oe2.0 @ z 1.75, internal cup-floor boss.\n"
          "Scan reads theta=-71 in the analyst's sign convention; +59 in the frozen datum frame.")
plt.tight_layout(); plt.savefig(f"{SC}/B02_S2_meridian_SAF1.png", dpi=140); plt.close()

# ---------------------------------------------------------------- (c) plan section thru arms
for tag, zz, lim, tick, minor, ttl, note in [
    ("c1", 1.00, 16.0, 2.0, 0.5, "z = 1.00 mm  (skirt band, 1 mm above the rim - the F05/F06 caliper station)",
     "3-lobed skirt, it2: R 13.425 lobes (caliper F05 26.85 / 2); R 12.550 flats on the arms = SCAN authority.\n"
     "it2/A2: F06 (24.84) was STRUCK - no antipodal flat-flat pair exists on a 3-lobed skirt, so 24.84 is not\n"
     "achievable as a two-jaw diametral reading (min achievable 25.99 scan / 25.62 CAD). The notch at theta 59\n"
     "is SAF-1 (skirt recess + the Oe2.0 radial hole)."),
    ("c2", 6.50, 42.0, 5.0, 1.0, "z = 6.50 mm  (through the three arm blades)",
     "PolarArray 3 x 120.00 deg. Arms modelled PLANAR in r-z (Q4 ruling): the measured 0.97-2.20 mm\n"
     "free-state tangential drift is NOT modelled and shows here as a residual on the arm flanks.\n"
     "Blade width 5.33 = caliper F10; the scan reads ~5.89 (scanner dilation on thin sections, intake R6).")]:
    fig, ax = plt.subplots(figsize=(11, 11))
    draw(ax, plan_segs(SCAN, zz), CSCAN, LSCAN, lw=1.3)
    draw(ax, plan_segs(CAD, zz), CCAD, LCAD, lw=1.3)
    for a, lab in [(0, "arm 1"), (120, "arm 2"), (-120, "arm 3")]:
        ax.plot([0, 0.93 * lim * math.cos(math.radians(a))], [0, 0.93 * lim * math.sin(math.radians(a))],
                color="0.45", ls="--", lw=0.9)
        ax.text(0.97 * lim * math.cos(math.radians(a)), 0.97 * lim * math.sin(math.radians(a)), lab,
                color="0.25", fontsize=9, ha="center", va="center")
    ax.plot([0, 0.80 * lim * math.cos(math.radians(59))], [0, 0.80 * lim * math.sin(math.radians(59))],
            color="m", lw=1.2)
    ax.text(0.86 * lim * math.cos(math.radians(59)), 0.86 * lim * math.sin(math.radians(59)),
            "SAF-1", color="m", fontsize=9, ha="center")
    finish(ax, "OOM-B02  (c) PLAN SECTION  " + ttl, "x (mm)", "y (mm)",
           (-lim, lim), (-lim, lim), tick, minor)
    annot(ax, note)
    plt.tight_layout(); plt.savefig(f"{SC}/B02_S3{tag}_plan_z{zz:.2f}.png", dpi=140); plt.close()

# ---------------------------------------------------------------- (d) hex pocket zoom
fig, axs = plt.subplots(1, 2, figsize=(18, 8))
draw(axs[0], meridian_segs(SCAN, 59.04), CSCAN, LSCAN)
draw(axs[0], meridian_segs(CAD, 59.04), CCAD, LCAD)
finish(axs[0], "(d1) HEX POCKET - meridian across two opposite FLATS (theta 59.04/239.04)",
       "radius r (mm)", "z (mm)", (-7, 7), (1.5, 11.5), 1.0, 0.25)
annot(axs[0], "F01 hex AF = 7.358 mm  SCAN FIT ONLY - no caliper reading exists.\n"
              "NOT intent-snapped to 7.0/7.5.  Pocket depth 3.44 below the cup floor = caliper F02.\n"
              "the centre Phillips screw is COTS and is NOT modelled (scan trace at r<3.0, z 8.6-10.4)")
draw(axs[1], plan_segs(SCAN, 4.20), CSCAN, LSCAN)
draw(axs[1], plan_segs(CAD, 4.20), CCAD, LCAD)
for k in range(6):
    a = math.radians(59.04 + 60 * k)
    axs[1].plot([0, 6 * math.cos(a)], [0, 6 * math.sin(a)], color="0.5", ls=":", lw=0.8)
finish(axs[1], "(d2) HEX POCKET - plan section at z = 4.20 mm (mid-pocket)", "x (mm)", "y (mm)",
       (-6, 6), (-6, 6), 1.0, 0.25)
annot(axs[1], "grey rays = the six CAD flat normals (phase 59.0 deg from arm 1).\n"
              "scan sees only ~2/3 of the hexagon (124 deg gap) - the missing flats are an\n"
              "occlusion, not a geometry error.")
plt.tight_layout(); plt.savefig(f"{SC}/B02_S4_hex_zoom.png", dpi=140); plt.close()

# ---------------------------------------------------------------- (e) arm end / tuft collar
fig, axs = plt.subplots(1, 2, figsize=(18, 8))
draw(axs[0], meridian_segs(SCAN, 0.0), CSCAN, LSCAN)
draw(axs[0], meridian_segs(CAD, 0.0), CCAD, LCAD)
axs[0].axvline(38.2, color="g", lw=1.2, ls="--")
axs[0].text(38.4, 11.0, "r = 38.20  CAD plastic/bristle cut-off", color="g", fontsize=8, rotation=90, va="bottom")
finish(axs[0], "(e1) ARM 1 END / TUFT COLLAR - meridian zoom", "radius r (mm)", "z (mm)",
       (30, 46), (9, 22), 1.0, 0.25)
annot(axs[0], "Everything beyond r = 38.20 (scan junction 38.23/38.22/38.19) is bristle: SOFT (+/-3 mm),\n"
              "NOT modelled, excluded from the Tier-2 gate.  The red inner outline is the blind tuft slot\n"
              "(4.60 x 3.50 x 3.0 deep) - depth is PHOTO-INFERRED and NOT gated.\n"
              "CAD sits ~0.9 mm high on ARM 1 because the path is the 3-arm mean (see panel (a)).")
# section normal to the arm path at r = 36.5, each mesh taken through ITS OWN local
# blade centre so the two SHAPES are comparable (the absolute z offset is the free-state
# droop already shown in panel (a) and is annotated instead of being hidden)
def blade_section(mesh, r_stat=36.5):
    V = mesh.vertices
    rr = np.hypot(V[:, 0], V[:, 1]); zz = V[:, 2]
    tt = np.degrees(np.arctan2(V[:, 1], V[:, 0]))
    k = np.abs(((tt + 180) % 360) - 180) < 12
    zc = {}
    for r0 in (r_stat - 1.0, r_stat, r_stat + 1.0):
        s2 = k & (np.abs(rr - r0) < 0.25) & (zz > 5)
        zc[r0] = 0.5 * (np.percentile(zz[s2], 1) + np.percentile(zz[s2], 99))
    t = np.array([2.0, 0.0, zc[r_stat + 1.0] - zc[r_stat - 1.0]]); t /= np.linalg.norm(t)
    xd = np.array([0., 1., 0.]); yd = np.cross(t, xd)
    org = [r_stat, 0.0, zc[r_stat]]
    sg = [p for p in normal_segs(mesh, org, t, xd, yd) if np.abs(p).max() < 8]
    return sg, zc[r_stat]

sg_s, z_s = blade_section(SCAN)
sg_c, z_c = blade_section(CAD)
draw(axs[1], sg_s, CSCAN, LSCAN)
draw(axs[1], sg_c, CCAD, LCAD)
finish(axs[1], "(e2) ARM BLADE SECTION normal to the path at r = 36.5 (the F10/F11 caliper station)",
       "tangential (mm)", "normal-to-path (mm)", (-4.5, 4.5), (-4.0, 4.0), 1.0, 0.25)
annot(axs[1], "Both sections are taken through their OWN local blade centre so the shapes compare.\n"
              "CAD 5.330 wide x 4.070 thick = caliper F10/F11 held exactly; the scan outline is\n"
              "~0.28 mm/side proud on the WIDTH only (dilation on thin sections, intake R6) - that\n"
              "deviation is CORRECT per RE_SPEC 3, not chased.  Absolute blade-centre z: scan %.2f,\n"
              "CAD %.2f (delta %+.2f = the 3-arm-mean path choice, see panel (a))." % (z_s, z_c, z_c - z_s))
plt.tight_layout(); plt.savefig(f"{SC}/B02_S5_arm_end.png", dpi=140); plt.close()

print("wrote 5 overlay PNGs to", SC)
