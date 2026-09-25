"""dreame_brush_snap_cap — design-intent rebuild in build123d (datum frame: plate top z=0, bore axis Z,
flat-cut normal on +X). Feature order mirrors a SolidWorks tree."""
import json, math, sys
from pathlib import Path
from build123d import *

P = {
    "bore_dia": 14.00, "od": 23.73, "z_top": 0.0,
    "inner_bot_z": -1.53, "outer_bot_z": -1.84, "step_r0": 9.58, "step_r1": 9.85,
    "bore_chamfer_r": 7.88, "bore_chamfer_z": -0.65,           # 45deg chamfer from (7.0,-0.65) to (7.88,-1.53)
    "flat_x": 8.93, "flat_fillet": 2.75,
    "ramp_slope_dz_dx": 0.0835, "ramp_z_at_x": (7.714, -1.402),
    "leg_thetas": [60.0, 150.0, -60.0], "leg_r_in": 11.0, "leg_r_out": 11.90, "leg_half_angle": 9.6,
    "hook_r_out": 12.48, "hook_catch_z": 5.25, "hook_ramp_z0": 5.62, "hook_ramp_r1": 11.78, "hook_top_z": 6.25,
    "hook_inner_fillet": 0.30, "relief_r": 11.73, "relief_z0": 4.28, "relief_z1": 4.68, "relief_z2": 4.98,
    "cup_r_pos": 8.90, "cup_r_top": 1.52, "cup_r_bot": 1.38, "cup_depth": 0.43, "cup_thetas": [60.0, 150.0, -60.0, -140.0],
    "od_top_fillet": 0.20, "bore_top_fillet": 0.15,
}
out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
log = []
rb = P["bore_dia"] / 2; ro = P["od"] / 2

# F01 plate: revolve of the (r,z) profile
prof = Face(Wire.make_polygon([
    Vector(rb, 0, P["z_top"]), Vector(ro, 0, P["z_top"]), Vector(ro, 0, P["outer_bot_z"]),
    Vector(P["step_r1"], 0, P["outer_bot_z"]), Vector(P["step_r0"], 0, P["inner_bot_z"]),
    Vector(P["bore_chamfer_r"], 0, P["inner_bot_z"]), Vector(rb, 0, P["bore_chamfer_z"])], close=True))
body = revolve(prof, Axis.Z, 360)
# F02 underside ramp in the +X sector: cut everything below the plane z = z0 + k (x - x0)
x0, z0 = P["ramp_z_at_x"]; k = P["ramp_slope_dz_dx"]
ang = math.degrees(math.atan(k))
wedge = Box(40, 40, 10, align=(Align.CENTER, Align.CENTER, Align.MAX))   # z<=0 slab
wedge = Rot(0, -ang, 0) * wedge          # tilt: top face normal (sin?,0,cos) -> plane z rises with x
wedge = Pos(x0, 0, z0) * wedge
body = body - wedge
log.append(f"F02 ramp plane angle {ang:.2f} deg through ({x0},{z0})")
# F03 flat cut x > flat_x, then fillets on the two vertical flat/OD edges
body = body - Pos(P["flat_x"] + 10, 0, 0) * Box(20, 40, 20)
try:
    es = [e for e in body.edges().filter_by(Axis.Z) if abs(e.center().X - P["flat_x"]) < 1e-3 and abs(abs(e.center().Y) - math.sqrt(ro**2 - P["flat_x"]**2)) < 0.05]
    body = body.fillet(P["flat_fillet"], es); log.append(f"F03 flat fillets OK ({len(es)} edges)")
except Exception as ex:
    log.append(f"F03 flat fillets FAILED: {ex}")
try:
    es = [e for e in body.edges() if abs(e.center().Z - P["z_top"]) < 1e-3 and ((e.geom_type == GeomType.CIRCLE and abs(e.radius - ro) < 1e-3) or (e.geom_type == GeomType.LINE and abs(e.center().X - P["flat_x"]) < 1e-3))]
    body = body.fillet(P["od_top_fillet"], es); log.append(f"F06 OD top fillet OK ({len(es)})")
except Exception as ex:
    log.append(f"F06 OD top fillet FAILED: {ex}")

# F04 leg + hook: (r,z) profile revolved over the leg's angular span, inner-top edge fillet, 3 instances
hp = Face(Wire.make_polygon([
    Vector(P["leg_r_in"], 0, 0), Vector(P["leg_r_out"], 0, 0), Vector(P["leg_r_out"], 0, P["relief_z0"]),
    Vector(P["relief_r"], 0, P["relief_z1"]), Vector(P["relief_r"], 0, P["relief_z2"]), Vector(P["leg_r_out"], 0, P["hook_catch_z"]),
    Vector(P["hook_r_out"], 0, P["hook_catch_z"]), Vector(P["hook_r_out"], 0, P["hook_ramp_z0"]),
    Vector(P["hook_ramp_r1"], 0, P["hook_top_z"]), Vector(P["leg_r_in"], 0, P["hook_top_z"])], close=True))
span = 2 * P["leg_half_angle"]
leg = revolve(Rot(0, 0, -P["leg_half_angle"]) * hp, Axis.Z, span)
try:
    es = [e for e in leg.edges().filter_by(GeomType.CIRCLE) if abs(e.center().Z - P["hook_top_z"]) < 1e-3 and abs(e.radius - P["leg_r_in"]) < 1e-3]
    leg = leg.fillet(P["hook_inner_fillet"], es); log.append(f"F04 hook inner fillet OK ({len(es)} edges)")
except Exception as ex:
    log.append(f"F04 hook inner fillet FAILED: {ex}")
for th in P["leg_thetas"]:
    body = body + (Rot(0, 0, th) * leg)
# F05 cups: drafted pockets (cone frustum), 4 instances
cup = Cone(P["cup_r_bot"], P["cup_r_top"] + (P["cup_r_top"] - P["cup_r_bot"]) * (1.0 / P["cup_depth"]), P["cup_depth"] + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
for th in P["cup_thetas"]:
    t = math.radians(th)
    body = body - (Pos(P["cup_r_pos"] * math.cos(t), P["cup_r_pos"] * math.sin(t), -P["cup_depth"]) * cup)
# F06 cosmetic edge rounds
try:
    es = [e for e in body.edges() if abs(e.center().Z - P["z_top"]) < 1e-3 and e.geom_type == GeomType.CIRCLE and abs(e.radius - rb) < 1e-3]
    body = body.fillet(P["bore_top_fillet"], es); log.append(f"F06 bore top fillet OK ({len(es)})")
except Exception as ex:
    log.append(f"F06 bore top fillet FAILED: {ex}")
body = body.clean()
print("\n".join(log))
print("valid", body.is_valid, "solids", len(body.solids()), "faces", len(body.faces()), "volume %.3f" % body.volume, "bbox", body.bounding_box())
export_step(body, str(out_dir / "snap_datum.step"))
export_stl(body, str(out_dir / "snap_cad.stl"), tolerance=0.003, angular_tolerance=0.05)
from frames import export_frames
fb = export_frames(body, "snap", "dreame_brush_snap_cap", Path("C:/Users/marya/Downloads/dreame_brush_screw_cap"))
print("delivered", fb)
(out_dir / "snap_params.json").write_text(json.dumps(P, indent=1))
(out_dir / "snap_build_log.txt").write_text("\n".join(log))
