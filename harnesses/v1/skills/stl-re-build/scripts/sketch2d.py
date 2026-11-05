"""sketch2d.py - 2D profiles for feature trees (stl-re-build, harness v1).

A profile is a JSON spec evaluated in local 2D coordinates (u, v) and returned as one
build123d Face (or several disjoint faces) on the global XY plane. The caller places it
on a sketch plane.

Profile spec:
  {"items": [item, ...], "offset": d, "fillet_vertices": {...}}
Items are combined in order with each item's `mode`: "add" (default), "sub" or "intersect".
Each item may carry `let` and `repeat`, the same as tree nodes.

Item types:
  circle   {c:[u,v], r}
  rect     {c:[u,v], w, h, angle?, r?}        r = corner radius (RectangleRounded)
  slot     {c:[u,v], length, width, angle?}   overall length (SlotOverall)
  polygon  {pts:[[u,v], ...]}
  ngon     {c:[u,v], r, n, angle?}            regular polygon, r = circumradius
  chain    {pts:[[u,v], ...], arcs:{"i": arc}}  closed vertex chain; segment i runs from
           pts[i] to pts[i+1]; a segment is a line unless `arcs` names it.

Arc specs (lesson from the NX sketcher, nx-reference dreame_bottom_cover/work/nxlib/ps.py):
an arc always runs exactly through BOTH end points, and the measured data only picks the
side and the size.
  {"center":[u,v]}       the centre is projected onto the chord bisector (a measured centre
                         is never equidistant from two computed junctions); minor arc unless
                         "major": true. A half circle by centre is ambiguous and needs "side".
  {"r": R, "side": "left"|"right"}   centre on that side of the chord p0->p1; minor arc.
  {"mid":[u,v]}          three-point arc through a point on the arc.
  {"sagitta": h}         signed bulge height (+ = left of p0->p1).

Post-processing:
  offset: d               2D offset (negative = inward), arcs kept (Kind.ARC)
  fillet_vertices: {r, select: "concave"|"convex"|"all"|"near", pts?, tol?}
     concave/convex is found by a small-disc area test, so tangent joints are never filleted.
"""
from __future__ import annotations

import math
from typing import Any

from build123d import (Axis, Edge, Face, Kind, Location, Pos, Rot, SlotOverall, Vector, Wire,
                       offset)
from build123d import Circle as _Circle
from build123d import Rectangle as _Rect
from build123d import RectangleRounded as _RectR
from build123d import RegularPolygon as _NGon

from treexpr import ExprError, Scope, bind_let, repeat_instances


class SketchError(ValueError):
    pass


def _v(p: list[float]) -> Vector:
    return Vector(p[0], p[1], 0)


def _arc_mid(p0: list[float], p1: list[float], spec: dict[str, Any], S: Scope) -> list[float]:
    """Point on the arc between p0 and p1 (exact end points, spec picks side/size)."""
    x0, y0 = p0
    x1, y1 = p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 1e-9:
        raise SketchError("arc with coincident end points")
    nx, ny = -dy / L, dx / L                     # unit normal, left of p0->p1
    if "mid" in spec:
        return S.vec(spec["mid"], 2)
    if "sagitta" in spec:
        h = S.num(spec["sagitta"])
        return [mx + nx * h, my + ny * h]
    if "r" in spec:
        R = S.num(spec["r"])
        if R < L / 2 - 1e-9:
            raise SketchError(f"arc radius {R:g} < half chord {L / 2:g}")
        d = math.sqrt(max(R * R - (L / 2) ** 2, 0.0))
        side = spec.get("side", "left")
        s = 1.0 if side == "left" else -1.0
        cx, cy = mx + s * nx * d, my + s * ny * d
        major = bool(S.eval(spec.get("major", False)))
    elif "center" in spec:
        c = S.vec(spec["center"], 2)
        t = (c[0] - mx) * nx + (c[1] - my) * ny   # projection onto the bisector
        cx, cy = mx + nx * t, my + ny * t
        R = math.hypot(x0 - cx, y0 - cy)
        major = bool(S.eval(spec.get("major", False)))
        if abs(t) < 1e-9:
            side = spec.get("side")
            if side not in ("left", "right"):
                raise SketchError("half-circle arc by centre is ambiguous: add side left|right")
            s = 1.0 if side == "left" else -1.0
            return [cx + s * nx * R, cy + s * ny * R]
    else:
        raise SketchError(f"arc spec needs center, r, mid or sagitta: {spec}")
    # minor arc midpoint lies on the far side of the chord from the centre
    ux, uy = mx - cx, my - cy
    n = math.hypot(ux, uy)
    if n < 1e-12:   # centre on the chord: half circle, side given by `side`
        s = 1.0 if spec.get("side", "left") == "left" else -1.0
        return [cx + s * nx * R, cy + s * ny * R]
    ux, uy = ux / n, uy / n
    if major:
        ux, uy = -ux, -uy
    return [cx + ux * R, cy + uy * R]


def _chain(item: dict[str, Any], S: Scope) -> Face:
    pts = [S.vec(p, 2) for p in item["pts"]]
    if len(pts) < 2:
        raise SketchError("chain needs >= 2 points")
    arcs = {int(k): v for k, v in (item.get("arcs") or {}).items()}
    edges = []
    n = len(pts)
    for i in range(n):
        p0, p1 = pts[i], pts[(i + 1) % n]
        if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < 1e-9:
            continue
        if i in arcs:
            m = _arc_mid(p0, p1, arcs[i], S)
            edges.append(Edge.make_three_point_arc(_v(p0), _v(m), _v(p1)))
        else:
            edges.append(Edge.make_line(_v(p0), _v(p1)))
    return _up(Face(Wire(edges)))


def _up(f: Face) -> Face:
    """Profiles live on local XY with +Z normal; a clockwise chain gives -Z and would not fuse."""
    return -f if f.normal_at().Z < 0 else f


def _item_face(item: dict[str, Any], S: Scope) -> Face:
    t = item.get("type")
    if t == "circle":
        c, r = S.vec(item["c"], 2), S.num(item["r"])
        return Pos(c[0], c[1]) * _Circle(r).faces()[0]
    if t == "rect":
        c = S.vec(item["c"], 2)
        w, h = S.num(item["w"]), S.num(item["h"])
        r = S.opt(item, "r", 0)
        f = (_RectR(w, h, r) if r > 0 else _Rect(w, h)).faces()[0]
        return Pos(c[0], c[1]) * Rot(0, 0, S.opt(item, "angle", 0)) * f
    if t == "slot":
        c = S.vec(item["c"], 2)
        f = SlotOverall(S.num(item["length"]), S.num(item["width"])).faces()[0]
        return Pos(c[0], c[1]) * Rot(0, 0, S.opt(item, "angle", 0)) * f
    if t == "ngon":
        c = S.vec(item["c"], 2)
        f = _NGon(S.num(item["r"]), int(S.num(item["n"]))).faces()[0]
        return Pos(c[0], c[1]) * Rot(0, 0, S.opt(item, "angle", 0)) * f
    if t == "polygon":
        pts = [S.vec(p, 2) for p in item["pts"]]
        return _up(Face(Wire.make_polygon([_v(p) for p in pts], close=True)))
    if t == "chain":
        return _chain(item, S)
    raise SketchError(f"unknown profile item type {t!r}")


def _combine(acc: Any, f: Any, mode: str) -> Any:
    if acc is None:
        if mode != "add":
            raise SketchError(f"first profile item cannot be mode {mode!r}")
        return f
    if mode == "add":
        return acc + f
    if mode == "sub":
        return acc - f
    if mode == "intersect":
        return acc & f
    raise SketchError(f"unknown item mode {mode!r}")


def faces_of(shape: Any) -> list[Face]:
    return list(shape.faces()) if hasattr(shape, "faces") else [shape]


def _vertex_kind(face: Face, v: Vector, probe: float) -> float:
    """Fraction of a small disc around v that lies inside the face: >0.5 concave, <0.5 convex."""
    disc = Pos(v.X, v.Y) * _Circle(probe).faces()[0]
    inter = face & disc
    a = sum(f.area for f in faces_of(inter)) if inter is not None else 0.0
    return a / (math.pi * probe * probe)


def fillet_vertices(shape: Any, spec: dict[str, Any], S: Scope) -> tuple[Any, dict[str, Any]]:
    r = S.num(spec["r"])
    select = spec.get("select", "concave")
    tol = S.opt(spec, "tol", 0.05)
    out_faces = []
    report = {"r": r, "select": select, "n_vertices": 0, "status": "OK"}
    for face in faces_of(shape):
        span = max(face.bounding_box().size.X, face.bounding_box().size.Y)
        probe = min(max(span * 1e-3, 1e-3), r / 4)
        chosen = []
        pts = [S.vec(p, 2) for p in spec.get("pts", [])]
        for vx in face.vertices():
            v = Vector(vx.X, vx.Y, 0)
            if select == "near":
                if any(math.hypot(v.X - p[0], v.Y - p[1]) < tol for p in pts):
                    chosen.append(vx)
                continue
            k = _vertex_kind(face, v, probe)
            if (select == "concave" and k > 0.52) or (select == "convex" and k < 0.48) or \
               (select == "all" and abs(k - 0.5) > 0.02):
                chosen.append(vx)
        if chosen:
            face = face.fillet_2d(r, chosen)
        report["n_vertices"] += len(chosen)
        out_faces.append(face)
    if report["n_vertices"] == 0:
        report["status"] = "NO_VERTICES"
    res = out_faces[0] if len(out_faces) == 1 else out_faces[0].fuse(*out_faces[1:])
    return res, report


def build_profile(spec: dict[str, Any], S: Scope, reports: list[dict[str, Any]] | None = None) -> Any:
    """Evaluate a profile spec into a Face (or a compound of disjoint faces) on global XY."""
    acc = None
    for item in spec.get("items", []):
        layer = bind_let(S, item.get("let"))
        S.push(layer)
        try:
            for inst in repeat_instances(S, item.get("repeat")):
                S.push(inst)
                try:
                    il = bind_let(S, item.get("let_each"))
                    S.push(il)
                    try:
                        acc = _combine(acc, _item_face(item, S), item.get("mode", "add"))
                    finally:
                        S.pop()
                finally:
                    S.pop()
        finally:
            S.pop()
    if acc is None:
        raise SketchError("profile has no items")
    if "fillet_vertices" in spec:
        acc, rep = fillet_vertices(acc, spec["fillet_vertices"], S)
        if reports is not None:
            reports.append(rep)
    if "offset" in spec:
        d = S.num(spec["offset"])
        if abs(d) > 0:
            acc = offset(faces_of(acc), amount=d, kind=Kind.ARC)
    return acc


__all__ = ["build_profile", "SketchError", "ExprError", "fillet_vertices", "faces_of"]
