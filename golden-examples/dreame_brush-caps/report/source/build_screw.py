"""dreame_brush_screw_cap — design-intent rebuild in build123d (datum frame: top face z=0, bore axis Z,
a pentagon flat normal on +X). Feature order mirrors a SolidWorks tree."""
import json, math, sys
from pathlib import Path
import numpy as np
from build123d import *

P = {
    "z_top": 0.0, "z_pent": -0.45, "z_bot": -5.12,
    "pent_apothem": 4.50, "corner_dia": 10.90,
    "disc_r_top": 3.95, "disc_r_base": 4.38, "disc_top_fillet": 0.25,
    "dd_dia": 3.90, "dd_af": 3.28, "dd_bottom_z": -2.60,
    "web_bore_dia": 2.08, "web_top_z": -2.60, "web_bot_z": -4.05, "web_fillet_top": 0.55, "web_fillet_bot": 0.60,
    "cb_dia": 4.10, "cb_chamfer": 0.15,
    "chamfer_start_z": -2.93, "chamfer_angle_deg": 30.0, "chamfer_corner_fillet": 1.15, "bottom_fillet": 0.30,
    "dimple_R": 14.0, "dimple_depth_z0": -0.45, "dimple_depth_at_z3": 0.23, "dimple_z3": -3.0,
}
out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
log = []

def pent_face(apothem, z):
    R = apothem / math.cos(math.radians(36))
    pts = [Vector(R * math.cos(math.radians(36 + 72 * k)), R * math.sin(math.radians(36 + 72 * k)), z) for k in range(5)]
    return Face(Wire.make_polygon(pts, close=True))

# F01 pentagon prism (flats at 0,72,.. deg), z_bot..z_pent
h_pent = P["z_pent"] - P["z_bot"]
body = extrude(pent_face(P["pent_apothem"], P["z_bot"]), amount=h_pent)
# F02 corner turn: intersect with cylinder
cyl = Pos(0, 0, P["z_bot"]) * Cylinder(P["corner_dia"] / 2, h_pent + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
body = body & cyl
# F03 bottom chamfer zone: pentagon prism extruded upward with outward taper, corner edges filleted
tan_c = math.tan(math.radians(P["chamfer_angle_deg"]))
a_bot = P["pent_apothem"] - (P["chamfer_start_z"] - P["z_bot"]) * tan_c
L = 30.0
frustum = Pos(0, 0, P["z_bot"]) * Box(30, 30, h_pent + 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
ca, sa = math.cos(math.radians(P["chamfer_angle_deg"])), math.sin(math.radians(P["chamfer_angle_deg"]))
half = Pos(a_bot + ca * L / 2, 0, P["z_bot"] - sa * L / 2) * Rot(0, P["chamfer_angle_deg"], 0) * Box(L, L, L)
for k in range(5):
    frustum = frustum - (Rot(0, 0, 72 * k) * half)
side_edges = [e for e in frustum.edges().filter_by(GeomType.LINE) if abs(e.center().Z - P["z_bot"]) > 0.05 and abs(e.center().Z - (P["z_bot"] + h_pent + 1.5)) > 0.05]
log.append(f"F03 frustum valid={frustum.is_valid} faces={len(frustum.faces())} side_edges={len(side_edges)} types={sorted(set(str(f.geom_type) for f in frustum.faces()))}")
try:
    taper = frustum.fillet(P["chamfer_corner_fillet"], side_edges)
    log.append(f"F03 corner fillet R{P['chamfer_corner_fillet']} on {len(side_edges)} edges OK valid={taper.is_valid}")
except Exception as ex:
    taper = frustum
    log.append(f"F03 corner fillet FAILED: {ex}")
body = body & taper
# F04 top disc (revolve): cone frustum z_pent..z_top
prof = Face(Wire.make_polygon([Vector(0, 0, P["z_pent"]), Vector(P["disc_r_base"], 0, P["z_pent"]),
                               Vector(P["disc_r_top"], 0, P["z_top"]), Vector(0, 0, P["z_top"])], close=True))
disc = revolve(prof, Axis.Z, 360)
body = body + disc
try:
    top_edge = [e for e in body.edges().filter_by(GeomType.CIRCLE) if abs(e.center().Z - P["z_top"]) < 1e-3 and abs(e.radius - P["disc_r_top"]) < 1e-3]
    body = body.fillet(P["disc_top_fillet"], top_edge); log.append("F04 disc top fillet OK")
except Exception as ex:
    log.append(f"F04 disc top fillet FAILED: {ex}")
# F05 dimples: tilted cylinder cut on each flat (depth 0 at dimple_depth_z0, depth_at_z3 at dimple_z3)
dz = P["dimple_depth_z0"] - P["dimple_z3"]
slope = P["dimple_depth_at_z3"] / dz               # dx per dz
tilt = math.degrees(math.atan(slope))
zc = (P["dimple_depth_z0"] + P["dimple_z3"]) / 2
xc = P["pent_apothem"] + P["dimple_R"] - slope * (P["dimple_depth_z0"] - zc)
dimple = Cylinder(P["dimple_R"], 14.0)  # centred at origin, axis Z
dimple = Rot(0, tilt, 0) * dimple      # rotate about Y: axis tilts so x grows with z (axis dir ~(+sin, 0, cos))
dimple = Pos(xc, 0, zc) * dimple
for k in range(5):
    body = body - (Rot(0, 0, 72 * k) * dimple)
log.append(f"F05 dimples: R{P['dimple_R']} tilt {tilt:.2f} deg, axis x@zc={xc:.3f}")
# F06 double-D hole from top to dd_bottom_z
dd = Circle(P["dd_dia"] / 2) & Rectangle(20, P["dd_af"])
dd_solid = extrude(Pos(0, 0, P["dd_bottom_z"]) * dd, amount=P["z_top"] - P["dd_bottom_z"] + 0.5)
body = body - dd_solid
# F07 web bore Ø2.08 through, F08 counterbore Ø4.10 from bottom
body = body - Cylinder(P["web_bore_dia"] / 2, 20)
cb = Pos(0, 0, P["z_bot"] - 0.5) * Cylinder(P["cb_dia"] / 2, P["web_bot_z"] - P["z_bot"] + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
body = body - cb
# F09 web inner edge fillets
for zz, rad in [(P["web_top_z"], P["web_fillet_top"]), (P["web_bot_z"], P["web_fillet_bot"])]:
    try:
        es = [e for e in body.edges().filter_by(GeomType.CIRCLE) if abs(e.center().Z - zz) < 1e-3 and abs(e.radius - P["web_bore_dia"] / 2) < 1e-3]
        body = body.fillet(rad, es); log.append(f"F09 web fillet R{rad} at z={zz} OK ({len(es)} edges)")
    except Exception as ex:
        log.append(f"F09 web fillet at z={zz} FAILED: {ex}")
# F10 counterbore bottom chamfer
try:
    es = [e for e in body.edges().filter_by(GeomType.CIRCLE) if abs(e.center().Z - P["z_bot"]) < 1e-3 and abs(e.radius - P["cb_dia"] / 2) < 1e-3]
    body = body.chamfer(P["cb_chamfer"], None, es); log.append("F10 cb chamfer OK")
except Exception as ex:
    log.append(f"F10 cb chamfer FAILED: {ex}")
# F11 bottom outer edge round
try:
    es = [e for e in body.edges() if abs(e.center().Z - P["z_bot"]) < 1e-3 and not (e.geom_type == GeomType.CIRCLE and e.radius < 3)]
    body = body.fillet(P["bottom_fillet"], es); log.append(f"F11 bottom fillet OK ({len(es)} edges)")
except Exception as ex:
    log.append(f"F11 bottom fillet FAILED: {ex}")

body = body.clean()
print("\n".join(log))
print("valid", body.is_valid, "solids", len(body.solids()), "faces", len(body.faces()), "volume %.3f" % body.volume, "bbox", body.bounding_box())
export_step(body, str(out_dir / "screw_datum.step"))
export_stl(body, str(out_dir / "screw_cad.stl"), tolerance=0.003, angular_tolerance=0.05)
from frames import export_frames
fb = export_frames(body, "screw", "dreame_brush_screw_cap", Path("C:/Users/marya/Downloads/dreame_brush_screw_cap"))
print("delivered", fb)
(out_dir / "screw_params.json").write_text(json.dumps(P, indent=1))
(out_dir / "screw_build_log.txt").write_text("\n".join(log))
