#!/usr/bin/env python3
"""OD-E01_Power-PCB — params-driven build123d model (stl-re-rebuild-build123d, it1).

Every dimension comes from measure/params.json through `Params`. The only literals are the
documented clearances EMBED (sub-bodies start 0.05 mm inside the board / spine so the union has
no coplanar or touching faces) and cut-tool overshoots (+1.0 through a face).

Run from the run root:   python3 build/model.py
      or with paths:      python3 build/model.py --params measure/params.json \
                              --alignment intake/alignment.json --out build --part OD-E01_Power-PCB
Deterministic: no randomness, no wall-clock value in the geometry.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

from build123d import (Align, Axis, Box, Cone, Cylinder, Face, Location, Part, Plane, Pos, Rectangle,
                       SlotCenterToCenter, Sketch, Circle, Vector, Wire, Edge, Polyline, extrude, revolve)

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
EMBED = 0.05     # documented clearance: sub-bodies overlap the board / spine by 0.05 mm (robust union)
OVER = 1.0       # documented clearance: cut tools overshoot the faces they cut through


def find_scripts(explicit: Path | None) -> Path:
    cands = [explicit, Path(os.environ["STL_RE_REBUILD_SCRIPTS"]) if "STL_RE_REBUILD_SCRIPTS" in os.environ else None,
             RUN.parents[2] / "skills" / "stl-re-rebuild-build123d" / "scripts",
             Path("/home/user/agentic_STL-to-CAD/skills/stl-re-rebuild-build123d/scripts"),
             Path.home() / ".claude/skills/stl-re-rebuild-build123d/scripts"]
    for c in cands:
        if c is not None and (c / "export_frames.py").is_file():
            return c
    raise SystemExit("cannot find stl-re-rebuild-build123d/scripts; pass --scripts or set STL_RE_REBUILD_SCRIPTS")


class Params:
    def __init__(self, path: Path) -> None:
        d = json.loads(path.read_text(encoding="utf-8"))
        self.raw: dict[str, dict[str, Any]] = d["params"]
        for k, v in self.raw.items():
            if "value" not in v or "source" not in v:
                raise SystemExit(f"param {k}: needs value and source (run-contract.md section 4)")
        self.used: set[str] = set()

    def __getitem__(self, key: str) -> Any:
        self.used.add(key)
        return self.raw[key]["value"]

    def keys(self, prefix: str) -> list[str]:
        ks = sorted(k for k in self.raw if k.startswith(prefix))
        if not ks:
            raise KeyError(f"no params with prefix {prefix!r}")
        return ks

    def unused(self) -> list[str]:
        return sorted(set(self.raw) - self.used)


# ----------------------------------------------------------------------------- primitives
def box(x0, x1, y0, y1, z0, z1) -> Part:
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))


def rod(p0, p1, r) -> Part:
    """Cylinder of radius r from point p0 to point p1."""
    a, b = Vector(*p0), Vector(*p1)
    d = b - a
    L = d.length
    cyl = Cylinder(r, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pl = Plane(origin=a, z_dir=d.normalized())
    return pl * cyl


def bar(p0, p1, w_y, t) -> Part:
    """Rectangular lead bar (w_y along world Y, t across) from p0 to p1 (both at the same y)."""
    a, b = Vector(*p0), Vector(*p1)
    d = b - a
    return Plane(origin=a, x_dir=(0, 1, 0), z_dir=d.normalized()) * Box(w_y, t, d.length, align=(Align.CENTER, Align.CENTER, Align.MIN))


def frustum(p0, p1, r0, r1) -> Part:
    a, b = Vector(*p0), Vector(*p1)
    d = b - a
    cone = Cone(r0, r1, d.length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Plane(origin=a, z_dir=d.normalized()) * cone


def slot(p0, p1, w) -> Sketch:
    """Round-ended slot (stadium) of width w from centre p0 to centre p1 (XY)."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * SlotCenterToCenter(L, w, rotation=ang)


# ----------------------------------------------------------------------------- features
def f01_board(P: Params, log) -> Part:
    x0, x1, y0, y1 = P["board_x_min"], P["board_x_max"], P["board_y_min"], P["board_y_max"]
    t = P["board_thickness"]
    plate = box(x0, x1, y0, y1, -t, 0.0)
    sy0, sy1 = P["slot_y"]
    w = sy1 - sy0
    xe = P["slot_x_end"]
    slot_tool = extrude(slot((x0 - OVER, (sy0 + sy1) / 2), (xe - w / 2, (sy0 + sy1) / 2), w), amount=t + 2 * OVER)
    tools = Pos(0, 0, -t - OVER) * slot_tool
    for k in P.keys("hole_"):
        cx, cy, r = P[k]
        tools = tools + Pos(cx, cy, -t - OVER) * Cylinder(r, t + 2 * OVER, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate = plate - tools
    log(f"F01 board {x1 - x0:.3f} x {y1 - y0:.3f} x {t:.3f}, slot w {w:.3f}, {len(P.keys('hole_'))} holes")
    return plate


def f02_heatsink(P: Params, log) -> Part:
    prof: Sketch | None = None
    hubs = [P["hs_hub_upper"], P["hs_hub_lower"]]
    for cx, cy, R, _hr, _c0, _c1 in hubs:
        c = Pos(cx, cy) * Circle(R)
        prof = c if prof is None else prof + c
    sx0, sx1 = P["hs_spine_x"]
    prof = prof + Pos(sx0, hubs[1][1]) * Rectangle(sx1 - sx0, hubs[0][1] - hubs[1][1], align=(Align.MIN, Align.MIN))
    nfin = 0
    for k in P.keys("hs_fin_0") + P.keys("hs_fin_1"):
        rx, ry, tx, ty, w = P[k]
        prof = prof + slot((rx, ry), (tx, ty), w)
        nfin += 1
    ws = P["hs_fin_width_short"]
    for k in P.keys("hs_shortfin_"):
        rx, ry, tx, ty = P[k]
        prof = prof + slot((rx, ry), (tx, ty), ws)
        nfin += 1
    for (cx, cy, R, hr, c0, c1), sgn in zip(hubs, (1.0, -1.0)):
        prof = prof - Pos(cx, cy) * Circle(hr)
        # C-shaped screw channel: open outward (away from the spine) between the short fins
        L = R + 0.2                    # the channel is cut through the hub only; beyond it the short fins bound it
        prof = prof - Pos(c0, cy if sgn > 0 else cy - L) * Rectangle(c1 - c0, L, align=(Align.MIN, Align.MIN))
    z0, z1 = P["hs_bottom_z"] - EMBED, P["hs_top_z"]
    hs = Pos(0, 0, z0) * extrude(prof, amount=z1 - z0)
    ny0, ny1, nzt = P["hs_spine_notch"]
    hs = hs - box(sx0 - OVER, sx1 + OVER, ny0, ny1, z0 - OVER, nzt)
    hy, hz, hd = P["hs_spine_hole"]          # TO-220 screw hole through the spine (measured separately from the tab hole)
    hs = hs - rod((sx0 - OVER, hy, hz), (sx1 + OVER, hy, hz), hd / 2)
    log(f"F02 heatsink profile: 2 hubs, spine, {nfin} fins; extrude {z0:.3f}..{z1:.3f}")
    return hs


def f03_to220(P: Params, log) -> Part:
    xf, xb, y0, y1, zb, zt = P["q1_body"]
    body = box(xf, xb, y0, y1, zb, zt)
    tf, tback, ty0, ty1, tzt = P["q1_tab"]
    tab = box(tf, tback, ty0, ty1, zb, tzt)
    hy, hz, hd = P["q1_tab_hole"]
    tab = tab - rod((tf - OVER, hy, hz), (tback + OVER, hy, hz), hd / 2)
    lw, lt = P["q1_lead_w"], P["q1_lead_t"]
    q = body + tab
    nl = 0
    for k in P.keys("q1_lead_") :
        if k in ("q1_lead_w", "q1_lead_t"):
            continue
        ly, *xz = P[k]
        pts = list(zip(xz[0::2], xz[1::2]))
        pts = [(pts[0][0], -EMBED)] + pts + [(pts[-1][0], zb + EMBED)]
        for (xa, za), (xe, ze) in zip(pts[:-1], pts[1:]):
            q = q + bar((xa, ly, za), (xe, ly, ze), lw, lt)
            q = q + Pos(xe, ly, ze) * Box(lt, lw, lt)   # square knuckle at each path vertex
        nl += 1
    log(f"F03 TO-220 body x {xf:.2f}..{xb:.2f} z {zb:.2f}..{zt:.2f}, tab x {tf:.2f}..{tback:.2f} to z {tzt:.2f}, "
        f"hole d {hd:.2f}, {nl} bent leads")
    return q


def f04_clip(P: Params, log) -> Part:
    v = P["clip_path"]
    pts = list(zip(v[0::2], v[1::2]))
    w = P["clip_width"]
    z0, z1 = P["clip_z"]
    sk = None
    for a, b in zip(pts[:-1], pts[1:]):
        s = slot(a, b, w)
        sk = s if sk is None else sk + s
    hv = P["clip_hook"]                       # lower hook around the short-fin tip (separate measured polyline)
    hpts = list(zip(hv[0::2], hv[1::2]))
    for a, b in zip(hpts[:-1], hpts[1:]):
        sk = sk + slot(a, b, w)
    clip = Pos(0, 0, z0) * extrude(sk, amount=z1 - z0)
    log(f"F04 clip strap: {len(pts) - 1} segments, w {w:.2f}, z {z0:.2f}..{z1:.2f}")
    return clip


def f05_caps(P: Params, log) -> list[Part]:
    """Electrolytic cans: ONE revolved (r, z) profile each - base band, sealing groove, body - on the measured
    (leaning) axis, flat top at z_top."""
    out = []
    for k in [k_ for k_ in P.keys("cap_") if not k_.endswith("_base")]:
        ax0, ay0, dxdz, dydz, rb, zg0, rg, zg1, rbody, zt = P[k]
        d = Vector(dxdz, dydz, 1.0)
        L = (zt + EMBED) * d.length                 # axis length from below the board top to the top plane
        pts = [(0.0, 0.0), (rb, 0.0)]
        if zg1 > zg0:
            pts += [(rb, zg0 + EMBED), (rg, zg0 + EMBED), (rg, zg1 + EMBED), (rbody, zg1 + EMBED)]
        else:
            pts += [(rbody, 0.0)]
        pts += [(rbody, L), (0.0, L)]
        prof = Face(Wire.make_polygon([Vector(r, 0, z) for r, z in pts], close=True))
        can = revolve(prof, Axis.Z, 360)
        sk_ = f"capstem_{k[4:]}"
        if sk_ in P.raw:                       # can raised on a stem: cut the ring below the stand-off height
            stem_r, so_z = P[sk_]
            ring = Cylinder(max(rb, rg, rbody) + OVER, so_z + EMBED, align=(Align.CENTER, Align.CENTER, Align.MIN)) - \
                Cylinder(stem_r, so_z + EMBED, align=(Align.CENTER, Align.CENTER, Align.MIN))
            can = can - ring
        base = Vector(ax0 - dxdz * EMBED, ay0 - dydz * EMBED, -EMBED)
        out.append(Plane(origin=base, z_dir=d.normalized()) * can)
        log(f"F05 {k}: r base/groove/body {rb:.3f}/{rg:.3f}/{rbody:.3f}, groove z {zg0:.1f}..{zg1:.1f}, top {zt:.3f}, "
            f"lean {math.degrees(math.atan(math.hypot(dxdz, dydz))):.2f} deg")
    x0, x1, y0, y1, zt = P["cap_C1_base"]
    out.append(box(x0, x1, y0, y1, -EMBED, zt))
    log(f"F05 cap_C1_base (SMD V-chip base plate) {x1 - x0:.2f} x {y1 - y0:.2f} x {zt:.2f}")
    return out


def f07_fastons(P: Params, log) -> list[Part]:
    xs, ys = P["faston_x"], P["faston_y"]
    W, T, H, C = P["faston_width"], P["faston_thickness"], P["faston_top_z"], P["faston_chamfer"]
    FL, FZ, FDX = P["faston_foot_len"], P["faston_foot_top_z"], P["faston_foot_dx"]
    HZ, HD, HDY = P["faston_hole_z"], P["faston_hole_d"], P["faston_hole_dy"]
    out = []
    for xc, yc in zip(xs, ys):
        y0, y1 = yc - W / 2, yc + W / 2
        prof = Wire.make_polygon([Vector(xc - T / 2, y, z) for y, z in
                                  [(y0, -EMBED), (y1, -EMBED), (y1, H - C), (y1 - C, H), (y0 + C, H), (y0, H - C)]], close=True)
        blade = extrude(Face(prof), amount=T, dir=(1, 0, 0))
        blade = blade - rod((xc - T / 2 - OVER, yc + HDY, HZ), (xc + T / 2 + OVER, yc + HDY, HZ), HD / 2)
        foot = box(xc + FDX - T / 2, xc + FDX + T / 2, yc - FL / 2, yc + FL / 2, -EMBED, FZ)
        out.append(blade + foot)
    log(f"F07 {len(xs)} fastons: blade {W:.3f} x {T:.3f} x {H:.3f}, chamfer {C:.3f}, hole d {HD:.2f} @ z {HZ:.2f}")
    return out


def f08_connectors(P: Params, log) -> list[Part]:
    out = []
    for k in P.keys("conn_"):
        x0, x1, y0, y1, zt, cx0, cx1, cy0, cy1, fz = P[k]
        h = box(x0, x1, y0, y1, -EMBED, zt) - box(cx0, cx1, cy0, cy1, max(fz, 0.0) if fz > 0 else EMBED, zt + OVER)
        pins = [kp for kp in P.keys("connpin_") if kp.startswith(f"connpin_{k[5:]}_")] if any(
            kp.startswith(f"connpin_{k[5:]}_") for kp in P.raw) else []
        for kp in pins:
            px0, px1, py0, py1, pzt = P[kp]
            h = h + box(px0, px1, py0, py1, -EMBED, pzt)
        out.append(h)
        log(f"F08 {k}: {x1 - x0:.2f} x {y1 - y0:.2f} x {zt:.2f}, cavity floor {fz:.2f}, {len(pins)} inner contacts/ribs")
    return out


def f09_blocks(P: Params, log) -> list[Part]:
    out = []
    for k in P.keys("blk_"):
        b = P[k]
        bx0, bx1, by0, by1, bzt, rx0, rxb0, rxb1, ry0, ry1, rzt = b
        # riser: XZ trapezoid (front vertical at rx0, back face sloped from rxb0 at the base top to rxb1 at its top)
        prof = Wire.make_polygon([Vector(x, ry0, z) for x, z in
                                  [(rx0, -EMBED), (rxb0, -EMBED), (rxb0, bzt), (rxb1, rzt), (rx0, rzt)]], close=True)
        riser = extrude(Face(prof), amount=ry1 - ry0, dir=(0, 1, 0))
        out.append(box(bx0, bx1, by0, by1, -EMBED, bzt) + riser)
        log(f"F09 {k}: base top {bzt:.2f}, riser top {rzt:.2f}, back {rxb0:.2f}->{rxb1:.2f}")
    return out


def f10_axial(P: Params, log) -> list[Part]:
    out = []
    ld = P["lead_d"]
    for k in P.keys("ax_"):
        v = P[k]
        xa, za, r, y0, y1 = v[:5]
        part = rod((xa, y0, za), (xa, y1, za), r)
        leads = v[5:]
        name = k[3:]
        for j, i in enumerate(range(0, len(leads), 3), 1):
            lx, yfar, lzt = leads[i:i + 3]
            zl = lzt - ld / 2
            if yfar > y1:
                ystart, yend = y1 - EMBED, yfar - ld / 2
            else:
                ystart, yend = y0 + EMBED, yfar + ld / 2
            dk = f"axlead_{name}_{j}"
            if dk in P.raw:     # measured descent path (x, y, z) from the board up
                dv = P[dk]
                path = [(x_, y_, z_) for x_, y_, z_ in zip(dv[0::3], dv[1::3], dv[2::3])]
                path = [(path[0][0], path[0][1], -EMBED)] + path + [(lx, yend, zl)]
            else:
                path = [(lx, yend, -EMBED), (lx, yend, zl)]
            part = part + rod((lx, ystart, zl), (lx, yend, zl), ld / 2)
            for pa, pb in zip(path[:-1], path[1:]):
                part = part + rod(pa, pb, ld / 2)
                part = part + Pos(*pb) * Box(ld, ld, ld)   # square knuckle at each path vertex (bends declared)
        out.append(part)
        log(f"F10 {k}: r {r:.3f} axis z {za:.3f}, y {y0:.2f}..{y1:.2f}, {len(leads) // 3} leads")
    return out


def f11_ycap(P: Params, log) -> Part:
    cx, cy, cz, nx, ny, nz, Rc, rho = P["ycap_CY1"]
    # rounded-disc (r,z) half profile: core flat faces + full-round rim, revolved about local Z
    e1 = Edge.make_line(Vector(0, 0, -rho), Vector(Rc, 0, -rho))
    e2 = Edge.make_three_point_arc(Vector(Rc, 0, -rho), Vector(Rc + rho, 0, 0), Vector(Rc, 0, rho))
    e3 = Edge.make_line(Vector(Rc, 0, rho), Vector(0, 0, rho))
    e4 = Edge.make_line(Vector(0, 0, rho), Vector(0, 0, -rho))
    disc = revolve(Face(Wire([e1, e2, e3, e4])), Axis.Z, 360)
    disc = Plane(origin=(cx, cy, cz), z_dir=(nx, ny, nz)) * disc
    ld = P["lead_d"]
    part = disc
    for k in ("ycap_lead_1", "ycap_lead_2"):
        x0, y0, z0, x1, y1, z1 = P[k]
        d = Vector(x1 - x0, y1 - y0, z1 - z0)
        # extend the low end down to the board and the high end 1 mm into the disc body
        t0 = (-EMBED - z0) / d.Z
        p0 = Vector(x0, y0, z0) + d * t0
        p1 = Vector(x1, y1, z1) + d.normalized() * OVER
        part = part + rod((p0.X, p0.Y, p0.Z), (p1.X, p1.Y, p1.Z), ld / 2)
    log(f"F11 Y-cap: D {2 * (Rc + rho):.3f}, t {2 * rho:.3f}, normal ({nx:.3f},{ny:.3f},{nz:.3f}); 2 leads")
    return part


def f12_boxes(P: Params, log) -> list[Part]:
    out = []
    for k in P.keys("box_"):   # includes box_side_* (shadowed parts beside an axial body)
        x0, x1, y0, y1, zt = P[k]
        out.append(box(x0, x1, y0, y1, -EMBED, zt))
    log(f"F12 {len(out)} SMD / low-part boxes")
    return out


def build(P: Params, log) -> Part:
    board = f01_board(P, log)
    parts: list[Part] = [f02_heatsink(P, log), f03_to220(P, log), f04_clip(P, log)]
    parts += f05_caps(P, log)
    x0, x1, y0, y1, zt = P["x2_CX1"]
    parts.append(box(x0, x1, y0, y1, -EMBED, zt))
    log(f"F06 X2 box {x1 - x0:.2f} x {y1 - y0:.2f} x {zt:.2f}")
    parts += f07_fastons(P, log)
    parts += f08_connectors(P, log)
    parts += f09_blocks(P, log)
    parts += f10_axial(P, log)
    parts.append(f11_ycap(P, log))
    parts += f12_boxes(P, log)
    body = board.fuse(*parts)
    body = body.clean()
    if not isinstance(body, Part):
        body = Part(body.wrapped)
    log(f"F13 union of board + {len(parts)} sub-bodies -> solids {len(body.solids())}, faces {len(body.faces())}, "
        f"valid {body.is_valid}")
    return body


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="OD-E01_Power-PCB build123d model")
    ap.add_argument("--params", type=Path, default=RUN / "measure" / "params.json")
    ap.add_argument("--alignment", type=Path, default=RUN / "intake" / "alignment.json")
    ap.add_argument("--out", type=Path, default=HERE)
    ap.add_argument("--part", default="OD-E01_Power-PCB")
    ap.add_argument("--scripts", type=Path)
    a = ap.parse_args(argv)
    try:
        import export_frames as _ef  # noqa: F401  (on PYTHONPATH, e.g. under repro_check.py)
    except ImportError:
        sys.path.insert(0, str(find_scripts(a.scripts)))
    from export_frames import ExportAbort, ScaleFrameSkipped, export_frames
    from fillet_log import FilletLog
    import build123d

    P = Params(a.params)
    flog = FilletLog()
    flog.log(f"build123d {build123d.__version__}  params={a.params.name}")
    body = build(P, flog.log)
    if P.unused():
        flog.log(f"UNUSED params (plan/measure mismatch?): {P.unused()}")
    a.out.mkdir(parents=True, exist_ok=True)
    flog.write(a.out / "fillets.json", a.out / "build_log.txt", inputs=[a.params, Path(__file__)])
    try:
        chk = export_frames(body, a.alignment, a.out, a.part, fillets_json=a.out / "fillets.json",
                            model_py=Path(__file__).resolve(), params_json=a.params)
    except ScaleFrameSkipped as ex:
        print(f"DATUM-ONLY: {ex}", file=sys.stderr)
        return 3
    except ExportAbort as ex:
        print(f"ABORT: {ex}", file=sys.stderr)
        return 2
    s = chk["datum"]
    print(json.dumps({"solids": s["solids"], "valid": s["valid"], "closed": s["closed"], "faces": s["faces"],
                      "volume_mm3": s["volume_mm3"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
