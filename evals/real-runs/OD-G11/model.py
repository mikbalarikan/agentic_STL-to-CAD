#!/usr/bin/env python3
"""OD-G11 portafilter: params-driven build123d model (datum frame, see measure/params.json#frame).

Feature order follows build/MODELING_PLAN.md (F01..F15). Every dimension comes from
measure/params.json through Params; the only literals are documented tool clearances
(overshoots so cut/extrude tools pass cleanly through a face) and the ramp-plane reference
radius, which is the centre of the band the ramp was measured on (m04: r 31.8..35.0).

Run (from build/):
  python model.py --params ../measure/params.json --alignment ../intake/alignment.json --out . \
                  --part OD-G11_portafilter --scripts <stl-re-rebuild-build123d/scripts>
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

from build123d import (Align, Axis, Box, Cylinder, Edge, Face, GeomType, Keep, Location, Part, Plane, Pos, Rot,
                       Sphere, Torus, Vector, Wire, extrude, revolve, split)

HERE = Path(__file__).resolve().parent
CLR = 1.0          # documented clearance: tool overshoot past a face (mm)
BIG = 200.0        # documented: half-size of half-space boxes (larger than the part)
RAMP_R_REF = 33.4  # centre of the r band (31.8..35.0) on which the lug ramps were measured (m04/m11)


def find_scripts(explicit: Path | None) -> Path:
    cands = [explicit, Path(os.environ["STL_RE_REBUILD_SCRIPTS"]) if "STL_RE_REBUILD_SCRIPTS" in os.environ else None,
             HERE.parent / "scripts", Path.home() / ".claude/skills/stl-re-rebuild-build123d/scripts"]
    for c in cands:
        if c is not None and (c / "export_frames.py").is_file():
            return c
    raise SystemExit("cannot find stl-re-rebuild-build123d/scripts; pass --scripts")


class Params:
    def __init__(self, path: Path) -> None:
        self.raw: dict[str, dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))["params"]
        for k, v in self.raw.items():
            if "value" not in v or "source" not in v:
                raise SystemExit(f"param {k}: needs value and source")
        self.used: set[str] = set()

    def __getitem__(self, key: str) -> Any:
        self.used.add(key)
        return self.raw[key]["value"]

    def unused(self) -> list[str]:
        return sorted(set(self.raw) - self.used)


# ------------------------------------------------------------------ helpers
def V(r: float, z: float) -> Vector:          # point in the XZ half-plane (revolve about Z)
    return Vector(r, 0, z)


def face_from_edges(edges: list[Edge]) -> Face:
    return Face(Wire(edges))


def revolve_z(edges: list[Edge]) -> Part:
    return revolve(face_from_edges(edges), Axis.Z, 360)


def poly_edges(pts: list[Vector]) -> list[Edge]:
    return [Edge.make_line(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def halfspace(origin: tuple[float, float, float], normal: tuple[float, float, float], keep_side: str) -> Part:
    """A big box cut by a plane; keep_side 'pos' keeps the side the normal points to."""
    b = Box(2 * BIG, 2 * BIG, 2 * BIG)
    return split(b, bisect_by=Plane(origin=origin, z_dir=normal), keep=Keep.TOP if keep_side == "pos" else Keep.BOTTOM)


def line_z(a: float, b: float, z: float) -> float:
    return a + b * z


def sphere_z(zc: float, R: float, r: float) -> float:   # lower cap of a sphere centred on the axis
    return zc - math.sqrt(R * R - r * r)


# ------------------------------------------------------------------ features
def cup_body(P: Params, flog: Any) -> Part:
    # F01 outer revolve: dome arc (true arc) -> drafted wall line -> rim top
    zc, R = P["dome_centre_z"], P["dome_R"]
    a, b = P["outer_wall_r_at_z0"], P["outer_wall_dr_dz"]
    zt = P["rim_top_z"]
    # wall line meets the dome sphere: (a + b z)^2 + (z - zc)^2 = R^2
    A2, B2, C2 = b * b + 1, 2 * a * b - 2 * zc, a * a + zc * zc - R * R
    z1 = (-B2 - math.sqrt(B2 * B2 - 4 * A2 * C2)) / (2 * A2)
    r1 = a + b * z1
    rm = r1 / 2
    e = [Edge.make_three_point_arc(V(0, zc - R), V(rm, sphere_z(zc, R, rm)), V(r1, z1)),
         Edge.make_line(V(r1, z1), V(line_z(a, b, zt), zt)),
         Edge.make_line(V(line_z(a, b, zt), zt), V(0, zt)),
         Edge.make_line(V(0, zt), V(0, zc - R))]
    body = revolve_z(e)
    flog.log(f"F01 outer revolve: wall/dome corner at r={r1:.3f} z={z1:.3f}")

    # F02 cavity: interior revolve (bore, ledge, taper, insert wall) ∩ funnel region
    ab, bb = P["bore_r_at_z0"], P["bore_dr_dz"]
    zl = P["ledge_z"]
    at, bt = P["ledge_taper_r_at_z0"], P["ledge_taper_dr_dz"]
    aw, bw = P["insert_wall_r_at_z0"], P["insert_wall_dr_dz"]
    zi = (aw - at) / (bt - bw)                  # taper meets the insert wall
    z_top, z_bot = zt + CLR, zc - R - CLR       # tool overshoots the rim and the lowest floor
    pts = [V(0, z_top), V(line_z(ab, bb, z_top), z_top), V(line_z(ab, bb, zl), zl), V(line_z(at, bt, zl), zl),
           V(line_z(aw, bw, zi), zi), V(line_z(aw, bw, z_bot), z_bot), V(0, z_bot)]
    interior = revolve_z(poly_edges(pts))
    fz, fk = P["funnel_apex_z"], P["funnel_slope"]
    fx, fy = P["funnel_axis_x"], P["funnel_axis_y"]
    rho = 2 * BIG / 4
    # the cone starts at rho = 1 (a 1 mm notch around the apex, which lies inside the trough cut below): a cone face
    # containing its apex singularity failed BRepMesh at 0.003 mm (it1 attempt 2), so the apex is kept out of the face
    fun = revolve_z(poly_edges([V(1.0, fz + fk * 1.0), V(rho, fz + fk * rho), V(rho, z_top + CLR), V(0, z_top + CLR),
                                V(0, fz + fk * 1.0 + 1.0), V(1.0, fz + fk * 1.0 + 1.0)]))
    fun = Pos(fx, fy, 0) * fun
    cavity = interior & fun
    # F02b outlet trough (+X, m16): circular (r,z) section revolved about the cup axis between the two spout
    # angles; cavity union, so the floor is the lower of the funnel and the trough
    rc_, zc_, rh_ = P["trough_rc"], P["trough_zc"], P["trough_rho"]
    z_up = zi - 1.0   # trough tool top: below the taper corner, above any floor (clearance)
    ta = math.degrees(math.atan2(P["spout2_y"], P["spout2_x"])); tb = math.degrees(math.atan2(P["spout1_y"], P["spout1_x"]))
    sec = Face(Wire([Edge.make_line(V(rc_ - rh_, zc_), V(rc_ - rh_, z_up)), Edge.make_line(V(rc_ - rh_, z_up), V(rc_ + rh_, z_up)),
                     Edge.make_line(V(rc_ + rh_, z_up), V(rc_ + rh_, zc_)),
                     Edge.make_three_point_arc(V(rc_ + rh_, zc_), V(rc_, zc_ - rh_), V(rc_ - rh_, zc_))]))
    basin = interior & (Rot(0, 0, ta) * revolve(sec, Axis.Z, tb - ta))
    flog.log(f"F02 cavity: taper/insert-wall corner z={zi:.3f}; funnel apex ({fx:.3f},{fy:.3f},{fz:.3f}) slope {fk:.4f}")
    # floor-to-wall fillet on the cavity tool's convex edge (= the body's concave edge)
    rw_floor = P["floor_fillet_R"]
    cavity = flog.apply(cavity, "F03 floor-to-wall fillet (on cavity tool)",
                        lambda s: [ed for ed in s.edges() if ed.geom_type != GeomType.LINE
                                   and ed.bounding_box().max.Z < zi - 1.0 and ed.bounding_box().min.Z > z_bot + 0.5
                                   and ed.bounding_box().size.X > 30],
                        radii=[rw_floor], param="floor_fillet_R")
    body = body - cavity - basin
    flog.log(f"F02b outlet trough: section centre r {rc_:.3f} z {zc_:.3f} R {rh_:.3f}, theta {ta:.2f}..{tb:.2f}")

    # F03 local rounds on the revolve edges (circles about Z)
    def circ_at(rr: float, zz: float, tol: float = 0.05):
        return lambda s: [ed for ed in s.edges().filter_by(GeomType.CIRCLE)
                          if abs(ed.arc_center.Z - zz) < tol and abs(ed.radius - rr) < tol and abs(ed.arc_center.X) < 1e-3 and abs(ed.arc_center.Y) < 1e-3]
    body = flog.apply(body, "F03 bottom corner round", circ_at(r1, z1), radii=[P["bottom_corner_R"]], param="bottom_corner_R")
    body = flog.apply(body, "F03 rim outer round", circ_at(line_z(a, b, zt), zt), radii=[P["rim_outer_round_R"]], param="rim_outer_round_R")
    body = flog.apply(body, "F03 rim inner round", circ_at(line_z(ab, bb, zt), zt), radii=[P["rim_inner_round_R"]], param="rim_inner_round_R")
    P["rim_inner_round_cr"]  # recorded fit centre; used only as a cross-check below
    flog.log(f"F03 rim inner round: fit centre r {P['rim_inner_round_cr']:.3f} vs bore+R {line_z(ab, bb, zt) + P['rim_inner_round_R']:.3f}")
    return body


def spouts(P: Params, body: Part, flog: Any) -> Part:
    # F04: each spout is a revolve about its own vertical axis
    zc, R = P["dome_centre_z"], P["dome_R"]
    for i in (1, 2):
        sx, sy = P[f"spout{i}_x"], P[f"spout{i}_y"]
        aw, bw = P[f"spout{i}_wall_r_at_z0"], P[f"spout{i}_wall_dr_dz"]
        zr, zt, zh = P[f"spout{i}_ring_z"], P[f"spout{i}_tip_z"], P[f"spout{i}_head_z_r3p2"]
        rh = P["spout_head_r"]
        # head = spherical cap through the tip (r=0, zt) and (3.2, zh): derivation, not a new number
        r32 = 3.2  # radius at which spout{i}_head_z_r3p2 was measured (m11: r 3.0..3.4)
        dz = zh - zt
        Rs = (r32 * r32 + dz * dz) / (2 * dz)
        zcs = zt + Rs
        zhb = zcs - math.sqrt(Rs * Rs - rh * rh)            # cap z at the head rim radius
        z_in = sphere_z(zc, R, math.hypot(sx, sy)) + 3.0 + CLR   # start inside the body: 3 mm above the local dome (clearance)
        e = [Edge.make_line(V(0, z_in), V(line_z(aw, bw, z_in), z_in)),
             Edge.make_line(V(line_z(aw, bw, z_in), z_in), V(line_z(aw, bw, zr), zr)),
             Edge.make_line(V(line_z(aw, bw, zr), zr), V(rh, zr)),
             Edge.make_line(V(rh, zr), V(rh, zhb)),
             Edge.make_three_point_arc(V(rh, zhb), V(rh / 2, zcs - math.sqrt(Rs * Rs - rh * rh / 4)), V(0, zt)),
             Edge.make_line(V(0, zt), V(0, z_in))]
        sp = Pos(sx, sy, 0) * revolve_z(e)
        body = body + sp
        flog.log(f"F04 spout{i} at ({sx:.3f},{sy:.3f}): head cap R {Rs:.3f}, rim z {zhb:.3f}")
        rr = math.hypot(sx, sy)
        body = flog.apply(body, f"F04 spout{i} root round",
                          lambda s: [ed for ed in s.edges()
                                     if ed.bounding_box().min.Z > sphere_z(zc, R, rr) - 3.0 and ed.bounding_box().max.Z < sphere_z(zc, R, rr) + 2.0
                                     and abs(ed.bounding_box().center().X - sx) < 1.0 and abs(ed.bounding_box().center().Y - sy) < 1.0
                                     and ed.bounding_box().size.X > 8],
                          radii=[P["spout_boss_root_R"]], param="spout_boss_root_R")
    return body


def pockets(P: Params, body: Part, flog: Any) -> Part:
    # F05: outlet bore at each spout (the interior below the floor is unscanned: depth assumed)
    rb, zbot = P["pocket_bore_r"], P["pocket_bore_bottom_z"]
    for i in (1, 2):
        sx, sy = P[f"spout{i}_x"], P[f"spout{i}_y"]
        body = body - Pos(sx, sy, zbot) * Cylinder(rb, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))  # 20 mm: up through the floor (clearance)
    flog.log("F05 pockets: bores (depth assumed)")
    return body


def u_plateau_and_ribs(P: Params, body: Part, flog: Any) -> Part:
    yi, yo = P["urib_inner_absy"], P["urib_outer_absy"]
    x0 = P["urib_open_end_x"]
    xc = P["urib_round_end_outer_x"] - yo                     # round-end centre from the outer extreme
    ztop = P["urib_top_z"]
    zlow = P["funnel_apex_z"] - 2 * CLR                       # below the lowest floor

    def u_region(r_in: float | None, r_out: float) -> Part:
        """Prism of the U band (r_in..r_out) or the U interior (r_in None), z zlow..ztop+CLR."""
        h = ztop + CLR - zlow
        def stadium(rr: float, xs: float = x0) -> Part:
            box = Pos((xs + xc) / 2, 0, zlow + h / 2) * Box(xc - xs, 2 * rr, h)
            cyl = Pos(xc, 0, zlow) * Cylinder(rr, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
            return box + cyl
        s = stadium(r_out)
        if r_in is not None:
            s = s - stadium(r_in, x0 - CLR)   # inner stadium starts CLR before the open end so it is cut through (it1 shifted the whole stadium, which moved the round end too)
        return s

    # F06 plateau: U interior below the fitted plane
    z0, gx, gy = P["uplat_z0"], P["uplat_dz_dx"], P["uplat_dz_dy"]
    n = (-gx, -gy, 1.0)
    plat = u_region(None, yi) & halfspace((0, 0, z0), n, "neg")
    body = body + plat
    # F07 U rib: band between the inner and outer faces, full-round top
    rib = u_region(yi, yo)
    rib = rib & halfspace((0, 0, ztop), (0, 0, 1), "neg")
    t = yo - yi
    rib = flog.apply(rib, "F07 U-rib top full round", lambda s: [ed for ed in s.edges() if ed.bounding_box().min.Z > ztop - 0.01],
                     radii=[t / 2 * 0.98], param=None, why_fallback="full round = half the measured rib thickness (x0.98 so the two rounds do not meet)")
    body = body + rib
    flog.log(f"F06/F07 U plateau + rib: x {x0:.2f}..{xc:.2f}+R, faces |y| {yi:.3f}/{yo:.3f}")
    # F08 V ribs: drafted section (width law from m13), centre offset u (+u toward the cup centre), round inner end
    wt, wb = P["vrib_width_top"], P["vrib_width_base"]; zwt, zwb = P["vrib_width_z_top"], P["vrib_width_z_base"]
    hwz = lambda z: (wt + (wb - wt) * (zwt - z) / (zwt - zwb)) / 2
    def drafted_segment(pa, pb, zt, ext_b=0.0):
        """Drafted rib prism from pa to pb (+ext_b past pb), crest centred on the segment, plus a drafted round cap at pa."""
        L = math.hypot(pb[0] - pa[0], pb[1] - pa[1]); ang = math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0]))
        sec = Face(Wire.make_polygon([Vector(0, -hwz(zlow), zlow), Vector(0, hwz(zlow), zlow),
                                      Vector(0, hwz(zt), zt), Vector(0, -hwz(zt), zt)], close=True))
        bar = extrude(sec, L + ext_b, dir=(1, 0, 0))
        cap = revolve_z(poly_edges([V(0, zlow), V(hwz(zlow), zlow), V(hwz(zt), zt), V(0, zt)]))
        return Pos(pa[0], pa[1], 0) * Rot(0, 0, ang) * (bar + cap)
    for i in (1, 2):
        po, pj, pt = P[f"vrib{i}_outer_end"], P[f"vrib{i}_joint"], P[f"vrib{i}_tip"]
        zt = P[f"vrib{i}_top_z"]
        ext = 3.0  # extend the outer end 3 mm so it runs into the insert wall (clearance)
        v = drafted_segment(pj, po, zt, ext) + drafted_segment(pt, pj, zt)   # caps at the joint and at the tip
        v = flog.apply(v, f"F08 V-rib {i} top full round", lambda s: [ed for ed in s.edges() if ed.bounding_box().min.Z > zt - 0.01],
                       radii=[hwz(zt) * 0.98], param="vrib_width_top", why_fallback="full round = half the top width (x0.98)")
        body = body + v
    flog.log("F08 V ribs added")
    return body


def lugs_and_notches(P: Params, body: Part, flog: Any) -> Part:
    zt = P["rim_top_z"]
    a, b = P["outer_wall_r_at_z0"], P["outer_wall_dr_dz"]
    for i in (1, 2, 3):
        c, span, ro = P[f"lug{i}_centre_deg"], P[f"lug{i}_span_deg"], P[f"lug{i}_r_outer"]
        zu, kz = P[f"lug{i}_under_z_centre"], P[f"lug{i}_under_dz_per_deg"]
        r_in = line_z(a, b, -8.0) - CLR       # inside the wall (clearance)
        zlo = zu - 1.5 - CLR                   # below the lowest ramp point
        prof = poly_edges([V(r_in, zlo), V(ro, zlo), V(ro, zt), V(r_in, zt)])
        sec = Rot(0, 0, c - span / 2) * revolve(face_from_edges(prof), Axis.Z, span)
        th = math.radians(c)
        er, et = (math.cos(th), math.sin(th), 0.0), (-math.sin(th), math.cos(th), 0.0)
        s = kz * 180.0 / (math.pi * RAMP_R_REF)            # dz per mm of tangential travel
        nrm = (-s * et[0], -s * et[1], 1.0)
        org = (RAMP_R_REF * er[0], RAMP_R_REF * er[1], zu)
        lug = sec & halfspace(org, nrm, "pos")
        # trailing lead-out (m17): a second ramp plane, same construction
        zo, ko = P[f"lug{i}_leadout_z_centre"], P[f"lug{i}_leadout_dz_per_deg"]
        so = ko * 180.0 / (math.pi * RAMP_R_REF)
        lug = lug & halfspace((RAMP_R_REF * er[0], RAMP_R_REF * er[1], zo), (-so * et[0], -so * et[1], 1.0), "pos")
        body = body + lug
        flog.log(f"F09 lug{i} centre {c:.1f} span {span:.1f} r_out {ro:.3f} under z {zu:.3f} + {kz:.4f}/deg")
    for i in (1, 2):
        c, span, zf = P[f"notch{i}_centre_deg"], P[f"notch{i}_span_deg"], P[f"notch{i}_floor_z"]
        prof = poly_edges([V(P["bore_r_at_z0"] - CLR, zf), V(a + CLR, zf), V(a + CLR, zt + CLR), V(P["bore_r_at_z0"] - CLR, zt + CLR)])
        tool = Rot(0, 0, c - span / 2) * revolve(face_from_edges(prof), Axis.Z, span)
        body = body - tool
    flog.log("F10 rim notches cut")
    return body


def pad(P: Params, body: Part, flog: Any) -> Part:
    x0, y0, R0, k = P["pad_axis_x"], P["pad_axis_y"], P["pad_R_at_z0"], P["pad_dR_dz"]
    zt = P["rim_top_z"]
    zb = P["dome_centre_z"] - P["dome_R"] + 4.0  # pad cone ends 4 mm above the dome apex (inside the body; clearance)
    cone = Pos(x0, y0, 0) * revolve_z(poly_edges([V(0, zt), V(R0 + k * zt, zt), V(R0 + k * zb, zb), V(0, zb)]))
    ha, hb = P["pad_halfwidth_at_z0"], P["pad_halfwidth_dz"]
    ca, cb = P["pad_underchamfer_x_at_z0"], P["pad_underchamfer_dx_dz"]
    w = (halfspace((0, ha, 0), (0, 1, -hb), "neg") & halfspace((0, -ha, 0), (0, 1, hb), "pos")
         & halfspace((ca, 0, 0), (1, 0, -cb), "neg") & halfspace((P["outer_wall_r_at_z0"] - 8.0, 0, 0), (1, 0, 0), "pos")
         & halfspace((0, 0, zt), (0, 0, 1), "neg"))
    # exclusion = the cup wall cone moved 0.8 mm inward (inside the wall material everywhere; clearance)
    aw_, bw_ = P["outer_wall_r_at_z0"], P["outer_wall_dr_dz"]
    inner = revolve_z(poly_edges([V(0, zt + CLR), V(aw_ + bw_ * (zt + CLR) - 0.8, zt + CLR), V(aw_ + bw_ * (zb - CLR) - 0.8, zb - CLR), V(0, zb - CLR)]))
    body = body + ((cone & w) - inner)
    flog.log(f"F11 pad: cone axis ({x0:.3f},{y0:.3f}) R0 {R0:.3f} dR/dz {k:.4f}")
    return body


def handle_frame(P: Params) -> Location:
    y0, z0, sy, sz = P["handle_axis_y0"], P["handle_axis_z0"], P["handle_axis_dy_dx"], P["handle_axis_dz_dx"]
    d = Vector(1, sy, sz).normalized()
    up = Vector(0, 0, 1); up = (up - d * up.dot(d)).normalized()
    return Plane(origin=(0, y0, z0), x_dir=d, z_dir=up).location


def arch_and_handle(P: Params, body: Part, flog: Any) -> Part:
    loc = handle_frame(P)
    ra, hw, rr, wf = P["arch_outer_r"], P["channel_halfwidth"], P["channel_roof_r"], P["arch_foot_w"]
    t_ch_end = P["channel_end_t"]
    a_nc, b_nc = P["neck_cone_r_at_t0"], P["neck_cone_dr_dt"]
    t_cone0 = (ra - a_nc) / b_nc                    # neck cone starts where it reaches the arch radius
    t_cup = P["insert_wall_r_at_z0"] + P["insert_wall_dr_dz"] * P["handle_axis_z0"] + 1.5  # arch starts 1.5 mm outside the insert wall, i.e. inside the cup wall (clearance)
    # F12 arch: cylinder along local X, minus channel, minus below the foot plane
    L = t_cone0 + 0.5 - t_cup                       # 0.5 mm overlap into the handle revolve
    arch = Pos(t_cup + L / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(ra, L)
    wc = rr - hw                                    # roof arc centre (roof top = channel_roof_r above the axis)
    ch_len = t_ch_end - (t_cup - CLR)
    chan = (Pos((t_cup - CLR + t_ch_end) / 2, 0, wc) * Rot(0, 90, 0) * Cylinder(hw, ch_len)
            + Pos((t_cup - CLR + t_ch_end) / 2, 0, wc - BIG / 2) * Box(ch_len, 2 * hw, BIG))
    # legs end in rounded feet (m18): cut at the foot-round centre level, add one round rod per leg (clipped
    # to the arch cylinder); P["arch_foot_w"] (lowest point) is kept as a cross-check in the log
    fr, fv, fw = P["arch_foot_round_R"], P["arch_foot_centre_v"], P["arch_foot_centre_w"]
    foot = Pos(0, 0, fw - BIG) * Box(2 * BIG, 2 * BIG, 2 * BIG)
    rods = (Pos(t_cup + L / 2, fv, fw) * Rot(0, 90, 0) * Cylinder(fr, L)) + (Pos(t_cup + L / 2, -fv, fw) * Rot(0, 90, 0) * Cylinder(fr, L))
    arch = ((arch - foot) + (rods & arch)) - chan
    flog.log(f"F12 feet: round R {fr:.3f} at v +-{fv:.3f}, w {fw:.3f}; lowest point w {fw - fr:.3f} vs measured {wf:.3f}")
    # F13 handle revolve about local X: profile in the local XY plane (x = t, y = r)
    t_step = P["collar_step_t"]
    a_cf, b_cf = P["collar_flank_r_at_t0"], P["collar_flank_dr_dt"]
    r_pk = P["collar_peak_r"]; t_pk = (r_pk - a_cf) / b_cf
    t_back = P["collar_back_t"]
    a_g, b_g = P["grip_r_at_t0"], P["grip_dr_dt"]
    a_e, b_e = P["end_chamfer_r_at_t0"], P["end_chamfer_dr_dt"]
    t_ch = (a_e - a_g) / (b_g - b_e)                # grip cone meets the end chamfer
    t_end = P["end_face_t"]
    # it2 (m20): neck cone and collar are revolved about their own measured axis offsets; the grip about the grip axis
    a_nc, b_nc = P["neck_cone_r_at_t0"], P["neck_cone_dr_dt"]
    t_cone0 = (ra - a_nc) / b_nc
    def rev_x(pts, dy, dz):
        return Pos(0, dy, dz) * revolve(Face(Wire.make_polygon([Vector(t, r, 0) for t, r in pts], close=True)), Axis.X, 360)
    neck = rev_x([(t_cone0, 0), (t_cone0, ra), (t_step, a_nc + b_nc * t_step), (t_step, 0)], P["neck_cone_axis_dy"], P["neck_cone_axis_dz"])
    cdy, cdz = P["collar_flank_axis_dy"], P["collar_flank_axis_dz"]
    col = rev_x([(t_step, 0), (t_step, a_cf + b_cf * t_step), (t_pk, r_pk), (t_back, r_pk), (t_back, 0)], cdy, cdz)
    grip = rev_x([(t_back, 0), (t_back, a_g + b_g * t_back), (t_ch, a_g + b_g * t_ch), (t_end, a_e + b_e * t_end), (t_end, 0)], 0.0, 0.0)
    hnd = neck + col
    hnd = flog.apply(hnd, "F13 collar crest rounds",
                     lambda s: [ed for ed in s.edges().filter_by(GeomType.CIRCLE)
                                if abs(ed.radius - r_pk) < 1e-3 and (abs(ed.arc_center.X - t_pk) < 1e-3 or abs(ed.arc_center.X - t_back) < 1e-3)],
                     radii=[P["collar_top_round_R"]], param="collar_top_round_R")
    grip = flog.apply(grip, "F13 end edge round",
                      lambda s: [ed for ed in s.edges().filter_by(GeomType.CIRCLE) if abs(ed.arc_center.X - t_end) < 1e-3],
                      radii=[P["end_round_R"]], param="end_round_R")
    hnd = hnd - chan
    # feet on the flared neck-cone part (t_cone0..channel end): round the channel-wall/cone edges (m18 radius)
    hnd = flog.apply(hnd, "F13 cone-part leg-foot rounds",
                     lambda s: [ed for ed in s.edges() if ed.bounding_box().max.X < t_ch_end + 0.01 and ed.bounding_box().min.X > t_cone0 - 0.01
                                and ed.bounding_box().max.Z < wc - 1.0 and abs(abs(ed.bounding_box().center().Y) - hw) < 0.6
                                and ed.bounding_box().size.X > 1.0],
                     radii=[fr, fr * 0.8, fr * 0.6, fr * 0.4], param="arch_foot_round_R",
                     why_fallback="plan §6: the cone-part edges are short and end on the neck-cone start face; smaller radii allowed, declared")
    flog.log(f"F12/F13 arch t {t_cup:.2f}..{t_cone0:.2f}, channel to t {t_ch_end:.2f}; collar peak t {t_pk:.2f}; "
             f"grip->chamfer at t {t_ch:.2f}; end t {t_end:.3f}")
    body = body + loc * arch + loc * hnd + loc * grip
    # channel mouth: the pad (added before) must not close the channel between its scanned start and the arch
    t0c = P["channel_start_t"]
    mouth = (Pos((t0c + t_ch_end) / 2, 0, wc) * Rot(0, 90, 0) * Cylinder(hw, t_ch_end - t0c)
             + Pos((t0c + t_ch_end) / 2, 0, wc - BIG / 2) * Box(t_ch_end - t0c, 2 * hw, BIG))
    body = body - loc * mouth
    return body


def screws(P: Params, body: Part, flog: Any) -> Part:
    zc, R = P["dome_centre_z"], P["dome_R"]
    arm, dep, wid = P["recess_arm"], P["recess_depth"], P["recess_width"]
    # F14 centre screw: counterbore to the disc level, then the cross recess
    cx, cy, rd, raise_ = P["cscrew_x"], P["cscrew_y"], P["cscrew_disc_r"], P["cscrew_disc_raise"]
    z_disc = sphere_z(zc, R, math.hypot(cx, cy)) + raise_
    cb = Pos(cx, cy, z_disc) * Cylinder(rd, 10.0, align=(Align.CENTER, Align.CENTER, Align.MAX))  # 10 mm tool depth below the disc (clearance)
    cross = (Box(2 * arm, wid, dep + CLR, align=(Align.CENTER, Align.CENTER, Align.MIN))
             + Box(wid, 2 * arm, dep + CLR, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    body = body - cb - Pos(cx, cy, sphere_z(zc, R, math.hypot(cx, cy)) - CLR) * cross
    for i in (1, 2):
        sx, sy, zt = P[f"spout{i}_x"], P[f"spout{i}_y"], P[f"spout{i}_tip_z"]
        body = body - Pos(sx, sy, zt - CLR) * cross
    flog.log(f"F14 screws: centre counterbore r {rd:.2f} at z {z_disc:.3f}; cross recess arm {arm:.2f} depth {dep:.2f}")
    return body


def wire(P: Params, body: Part, flog: Any) -> Part:
    # it2 (m19): V groove in the rim bore that seats the wire, revolved over its measured theta span
    ab, bb = P["bore_r_at_z0"], P["bore_dr_dz"]
    zu, za, zl, dep = P["groove_upper_z"], P["groove_apex_z"], P["groove_lower_z"], P["groove_depth"]
    tri = poly_edges([V(line_z(ab, bb, zu) - CLR, zu), V(line_z(ab, bb, zu), zu), V(line_z(ab, bb, za) + dep, za),
                      V(line_z(ab, bb, zl), zl), V(line_z(ab, bb, zl) - CLR, zl)])
    g0, g1 = P["groove_theta_start"], P["groove_theta_end"]
    body = body - Rot(0, 0, g0) * revolve(face_from_edges(tri), Axis.Z, g1 - g0)
    flog.log(f"F15b wire groove: depth {dep:.3f} at z {za:.3f}, theta {g0:.0f}..{g1:.0f}")
    rw = P["wire_r"]
    for i in (1, 2, 3):
        cx, cy, R, zc = P[f"wire{i}_cx"], P[f"wire{i}_cy"], P[f"wire{i}_R"], P[f"wire{i}_zc"]
        P[f"wire{i}_theta_span"]  # exposed span; the modelled arc runs between its bore-wall crossings instead
        rb = P["bore_r_at_z0"] + P["bore_dr_dz"] * zc + rw  # the wire centreline enters the wall one wire radius beyond the bore
        d = math.hypot(cx, cy)
        # circle-circle intersection: |p| = rb and |p - c| = R
        aa = (rb * rb - R * R + d * d) / (2 * d); hh = math.sqrt(max(rb * rb - aa * aa, 0.0))
        ux, uy = cx / d, cy / d
        p1 = (aa * ux - hh * uy, aa * uy + hh * ux); p2 = (aa * ux + hh * uy, aa * uy - hh * ux)
        a1 = math.atan2(p1[1] - cy, p1[0] - cx); a2 = math.atan2(p2[1] - cy, p2[0] - cx)
        am = math.atan2(-cy, -cx)                    # the arc part nearest the cup axis
        # choose the angular interval [lo, hi] (length < pi) that contains am
        lo, hi = sorted([a1, a2])
        if not (lo <= am <= hi):
            lo, hi = hi, lo + 2 * math.pi
        tor = Pos(cx, cy, zc) * Torus(R, rw)
        wedge = Pos(cx, cy, zc - 5) * extrude(Face(Wire.make_polygon(
            [Vector(0, 0, 0), Vector(3 * R * math.cos(lo), 3 * R * math.sin(lo), 0),
             Vector(3 * R * math.cos((lo + hi) / 2), 3 * R * math.sin((lo + hi) / 2), 0),
             Vector(3 * R * math.cos(hi), 3 * R * math.sin(hi), 0)], close=True)), 10)
        body = body + (tor & wedge)
        flog.log(f"F15 wire{i}: arc R {R:.2f} at z {zc:.3f}, {math.degrees(hi - lo):.1f} deg about its centre")
    return body


def build(P: Params, flog: Any) -> Part:
    body = cup_body(P, flog)
    body = spouts(P, body, flog)
    body = pockets(P, body, flog)
    body = u_plateau_and_ribs(P, body, flog)
    body = lugs_and_notches(P, body, flog)
    body = pad(P, body, flog)
    body = arch_and_handle(P, body, flog)
    body = screws(P, body, flog)
    body = wire(P, body, flog)
    return body.clean()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--params", type=Path, required=True)
    ap.add_argument("--alignment", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--part", default="OD-G11_portafilter")
    ap.add_argument("--scripts", type=Path)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(find_scripts(a.scripts)))
    from export_frames import ExportAbort, ScaleFrameSkipped, export_frames
    from fillet_log import FilletLog
    import build123d
    P = Params(a.params)
    flog = FilletLog()
    flog.log(f"build123d {build123d.__version__}  params={a.params.name}")
    body = build(P, flog)
    if P.unused():
        flog.log(f"UNUSED params (plan/measure mismatch?): {P.unused()}")
    flog.log(f"solids={len(body.solids())} faces={len(body.faces())} volume={body.volume:.1f}")
    a.out.mkdir(parents=True, exist_ok=True)
    flog.write(a.out / "fillets.json", a.out / "build_log.txt", inputs=[a.params, Path(__file__)])
    try:
        chk = export_frames(body, a.alignment, a.out, a.part, fillets_json=a.out / "fillets.json",
                            model_py=Path(__file__).resolve(), params_json=a.params)
    except ScaleFrameSkipped as ex:
        print(f"DATUM-ONLY: {ex}", file=sys.stderr); return 3
    except ExportAbort as ex:
        print(f"ABORT: {ex}", file=sys.stderr); return 2
    s = chk["datum"]
    print(json.dumps({"solids": s["solids"], "valid": s["valid"], "closed": s["closed"], "faces": s["faces"],
                      "volume_mm3": s["volume_mm3"], "fillets": flog.summary()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
