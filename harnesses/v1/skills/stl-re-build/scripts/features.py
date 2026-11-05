"""features.py - feature-tree ops for build123d (stl-re-build, harness v1).

The builder runs the tree's nodes in order on one body. Each node builds a *tool* in its local
frame (primitive ops, possibly repeated and mirrored), then combines it with the body, or it
acts on the body directly (fillet, chamfer, mirror_body). After every node the builder checks
the result and rolls back on failure. A failed node never leaves a half-applied body behind.

Per-node checks (lessons from the NX staged builds, nx-reference left_thigh_clean_rebuild
stages2.py / nxh.mark+undo_to):
  * the result is a valid shape with the expected solid count (default 1);
  * the volume delta has the expected sign: add > 0, cut < 0, intersect <= 0, fillet != 0.
    A boolean that silently did nothing is a FAILED node, not a pass;
  * the face count is logged, so the anti-patchwork census can be read per node.

Primitive ops (local frame):
  extrude   {sketch:{plane?, profile|ref, offset?}, amount | z0+z1, both?, draft_deg?}
  revolve   {profile|ref, angle?}       profile in (u=r, v=h), revolved about local Z
  box       {size:[x,y,z], at?, align?}      align: center (default) | min | [ax,ay,az]
  cylinder  {r, h, at?, align?}         along local Z; align default "min" (base at `at`)
  cone      {r1, r2, h, at?, align?}
  loft      {sections:[{plane, profile|ref}], ruled?: false}  ruled lofts are refused
  group     {parts:[primitive, ...]}    union of several primitives in the same frame
Body ops:
  fillet / chamfer  {edges: selector, r, fallbacks?: [...]}  through v0 FilletLog
  mirror_body       {plane: "YZ"|"XZ"|"XY"}

Edge selector (all given predicates must hold; evaluated on the current shape):
  geom: line|circle|ellipse|bspline     parallel / perpendicular: X|Y|Z|[x,y,z]
  z: value (start, end and centre at that z), z_tol     near: [[x,y(,z)], ...], tol
  radius: r, r_tol                      in_box: [[xmin,ymin,zmin],[xmax,ymax,zmax]]
"""
from __future__ import annotations

import math
import time
import traceback
from typing import Any

from build123d import (Align, Axis, Box, Cone, Cylinder, Face, GeomType, Location, Part, Plane,
                       Pos, Rot, Vector, extrude, loft, mirror, revolve)

from sketch2d import build_profile, faces_of
from treexpr import ExprError, Scope, bind_let, repeat_instances

PRIMITIVES = {"extrude", "revolve", "box", "cylinder", "cone", "loft", "group"}
BODY_OPS = {"fillet", "chamfer", "mirror_body"}
COMBINES = {"new", "add", "cut", "intersect"}
NAMED_PLANES = {"XY": Plane.XY, "XZ": Plane.XZ, "YZ": Plane.YZ}
AXES = {"X": Vector(1, 0, 0), "Y": Vector(0, 1, 0), "Z": Vector(0, 0, 1)}
GEOMS = {"line": GeomType.LINE, "circle": GeomType.CIRCLE, "ellipse": GeomType.ELLIPSE,
         "bspline": GeomType.BSPLINE}


class TreeError(ValueError):
    pass


# --------------------------------------------------------------------------- frames
def make_plane(spec: Any, S: Scope) -> Plane:
    """Plane from "XY" | {"plane": "XZ", "offset": d} | {"origin", "x_dir", "z_dir"}."""
    if spec is None:
        return Plane.XY
    if isinstance(spec, str):
        if spec not in NAMED_PLANES:
            raise TreeError(f"unknown plane {spec!r}")
        return NAMED_PLANES[spec]
    if "plane" in spec:
        pl = make_plane(spec["plane"], S)
        return pl.offset(S.opt(spec, "offset", 0))
    origin = S.vec(spec.get("origin", [0, 0, 0]), 3)
    z = S.vec(spec["z_dir"], 3)
    x = S.vec(spec["x_dir"], 3) if "x_dir" in spec else None
    pl = Plane(origin=origin, x_dir=x, z_dir=z) if x else Plane(origin=origin, z_dir=z)
    if "offset" in spec:
        pl = pl.offset(S.num(spec["offset"]))
    return pl


def place(shape: Any, steps: list[dict[str, Any]] | None, S: Scope) -> Any:
    """Apply `place` steps in order: {"rot":[rx,ry,rz]} (degrees, about the origin), {"pos":[x,y,z]}."""
    for st in steps or []:
        if "rot" in st:
            r = S.vec(st["rot"], 3)
            shape = Rot(*r) * shape
        elif "pos" in st:
            shape = Pos(*S.vec(st["pos"], 3)) * shape
        else:
            raise TreeError(f"place step needs rot or pos: {st}")
    return shape


def _align(spec: Any, default: str) -> tuple[Align, Align, Align]:
    a = spec if spec is not None else default
    m = {"center": Align.CENTER, "min": Align.MIN, "max": Align.MAX}
    if isinstance(a, str):
        if a == "min_z":
            return (Align.CENTER, Align.CENTER, Align.MIN)
        return (m[a],) * 3
    return tuple(m[x] for x in a)


# --------------------------------------------------------------------------- primitives
class Ctx:
    def __init__(self, tree: dict[str, Any], S: Scope) -> None:
        self.tree = tree
        self.S = S
        self.profiles = tree.get("profiles", {})
        self.sketch_reports: list[dict[str, Any]] = []

    def profile(self, spec: dict[str, Any]) -> Any:
        """Resolve {"ref": name, ...overrides} against tree.profiles, then build it."""
        if "ref" in spec:
            if spec["ref"] not in self.profiles:
                raise TreeError(f"unknown profile ref {spec['ref']!r}")
            base = dict(self.profiles[spec["ref"]])
            base.update({k: v for k, v in spec.items() if k != "ref"})
            spec = base
        return build_profile(spec, self.S, self.sketch_reports)


def _sketch_faces(ctx: Ctx, sk: dict[str, Any], plane: Plane) -> list[Face]:
    prof = ctx.profile(sk.get("profile", sk) if "profile" in sk else sk)
    return [plane.location * f for f in faces_of(prof)]


def build_primitive(p: dict[str, Any], ctx: Ctx) -> Any:
    S = ctx.S
    op = p.get("op")
    layer = bind_let(S, p.get("let"))
    S.push(layer)
    try:
        insts = repeat_instances(S, p.get("repeat"))
        out = None
        for inst in insts:
            S.push(inst)
            try:
                el = bind_let(S, p.get("let_each"))
                S.push(el)
                try:
                    shp = _primitive_once(op, p, ctx)
                    shp = place(shp, p.get("place"), S)
                finally:
                    S.pop()
            finally:
                S.pop()
            out = shp if out is None else out + shp
        return out
    finally:
        S.pop()


def _primitive_once(op: str, p: dict[str, Any], ctx: Ctx) -> Any:
    S = ctx.S
    if op == "group":
        out = None
        for part in p["parts"]:
            s = build_primitive(part, ctx)
            out = s if out is None else out + s
        if out is None:
            raise TreeError("group with no parts")
        return out
    if op == "extrude":
        sk = p["sketch"]
        plane = make_plane(sk.get("plane"), S)
        if "z0" in p:
            z0, z1 = S.num(p["z0"]), S.num(p["z1"])
            plane = plane.offset(z0)
            amount = z1 - z0
        else:
            amount = S.num(p["amount"])
        faces = _sketch_faces(ctx, sk, plane)
        draft = S.opt(p, "draft_deg", 0)
        both = bool(S.eval(p.get("both", False)))
        res = None
        for f in faces:
            e = extrude(f, amount=amount, both=both, taper=draft)
            res = e if res is None else res + e
        return res
    if op == "revolve":
        prof = ctx.profile(p["profile"])
        faces = [Plane.XZ.location * f for f in faces_of(prof)]
        return revolve(faces, Axis.Z, S.opt(p, "angle", 360))
    if op == "box":
        size = S.vec(p["size"], 3)
        at = S.vec(p.get("at", [0, 0, 0]), 3)
        return Pos(*at) * Box(*size, align=_align(p.get("align"), "center"))
    if op == "cylinder":
        at = S.vec(p.get("at", [0, 0, 0]), 3)
        return Pos(*at) * Cylinder(S.num(p["r"]), S.num(p["h"]), align=_align(p.get("align"), "min_z"))
    if op == "cone":
        at = S.vec(p.get("at", [0, 0, 0]), 3)
        return Pos(*at) * Cone(S.num(p["r1"]), S.num(p["r2"]), S.num(p["h"]),
                               align=_align(p.get("align"), "min_z"))
    if op == "loft":
        if S.eval(p.get("ruled", False)):
            raise TreeError("ruled loft refused (anti-patchwork rule, v0 rebuild Step 5)")
        secs = []
        for sec in p["sections"]:
            fs = _sketch_faces(ctx, sec, make_plane(sec.get("plane"), S))
            if len(fs) != 1:
                raise TreeError("each loft section must be one face")
            secs.append(fs[0])
        return loft(secs, ruled=False)
    raise TreeError(f"unknown primitive op {op!r}")


# --------------------------------------------------------------------------- selectors
def _dir(spec: Any, S: Scope) -> Vector:
    if isinstance(spec, str) and spec in AXES:
        return AXES[spec]
    v = S.vec(spec, 3)
    return Vector(*v).normalized()


def edge_selector(spec: dict[str, Any], S: Scope):
    geom = GEOMS[spec["geom"]] if "geom" in spec else None
    par = _dir(spec["parallel"], S) if "parallel" in spec else None
    perp = _dir(spec["perpendicular"], S) if "perpendicular" in spec else None
    zval = S.num(spec["z"]) if "z" in spec else None
    ztol = S.opt(spec, "z_tol", 1e-4)
    near = [S.vec(p) for p in spec.get("near", [])]
    tol = S.opt(spec, "tol", 0.05)
    rad = S.num(spec["radius"]) if "radius" in spec else None
    rtol = S.opt(spec, "r_tol", 1e-3)
    box = [S.vec(b, 3) for b in spec["in_box"]] if "in_box" in spec else None

    def sel(shape: Any) -> list[Any]:
        out = []
        for ed in shape.edges():
            if geom is not None and ed.geom_type != geom:
                continue
            if par is not None or perp is not None:
                d = ed.end_point() - ed.start_point()
                if d.length < 1e-9:
                    d = ed.tangent_at(0)
                d = d.normalized()
                if par is not None and abs(abs(d.dot(par)) - 1) > 1e-6:
                    continue
                if perp is not None and abs(d.dot(perp)) > 1e-6:
                    continue
            c = ed.center()
            if zval is not None and not all(abs(q.Z - zval) < ztol
                                            for q in (ed.start_point(), ed.end_point(), c)):
                continue
            if near:
                ok = False
                for p in near:
                    if len(p) == 2:
                        ok |= math.hypot(c.X - p[0], c.Y - p[1]) < tol
                    else:
                        ok |= (c - Vector(*p)).length < tol
                if not ok:
                    continue
            if rad is not None:
                if ed.geom_type != GeomType.CIRCLE or abs(ed.radius - rad) > rtol:
                    continue
            if box is not None and not all(box[0][k] <= (c.X, c.Y, c.Z)[k] <= box[1][k] for k in range(3)):
                continue
            out.append(ed)
        return out
    return sel


# --------------------------------------------------------------------------- body helpers
def solids_of(shape: Any) -> int:
    return len(shape.solids()) if shape is not None else 0


def volume_of(shape: Any) -> float:
    return float(shape.volume) if shape is not None else 0.0


def is_valid(shape: Any) -> bool:
    try:
        return bool(shape.is_valid)
    except Exception:
        return False


def as_part(shape: Any) -> Any:
    """Keep Solid/Part as built: wrapping a TopoDS_Solid as a Part compound loses its volume."""
    return shape


def apply_fillets_to_tool(tool: Any, posts: list[dict[str, Any]], node_id: str, ctx: Ctx, flog: Any) -> Any:
    """`post` steps on a tool before it is placed: fillet/chamfer in the tool's local frame."""
    for k, st in enumerate(posts or []):
        op = st.get("op", "fillet")
        if op not in ("fillet", "chamfer"):
            raise TreeError(f"post op must be fillet or chamfer, got {op!r}")
        radii = [ctx.S.num(st["r"])] + [ctx.S.num(x) for x in st.get("fallbacks", [])]
        tool = flog.apply(tool, st.get("name", f"{node_id} post{k} {op}"), edge_selector(st["edges"], ctx.S),
                          radii=radii, op=op, param=st.get("param"), why_fallback=st.get("why_fallback", ""))
    return tool


def build_tool(node: dict[str, Any], ctx: Ctx, flog: Any) -> tuple[Any, int]:
    """Build a node's tool in global coordinates. Returns (tool, n_instances)."""
    S = ctx.S
    frame = make_plane(node.get("frame"), S) if "frame" in node else None
    insts = repeat_instances(S, node.get("repeat"))
    tool = None
    for inst in insts:
        S.push(inst)
        try:
            el = bind_let(S, node.get("let_each"))
            S.push(el)
            try:
                fr = make_plane(node.get("frame_each"), S) if "frame_each" in node else frame
                t = build_primitive({k: v for k, v in node.items()
                                     if k not in ("repeat", "let", "let_each", "place")}, ctx)
                t = apply_fillets_to_tool(t, node.get("post"), f"{node['id']}[{inst.get('_n', 0)}]", ctx, flog)
                t = place(t, node.get("place"), S)
                if fr is not None:
                    t = fr.location * t
            finally:
                S.pop()
        finally:
            S.pop()
        tool = t if tool is None else tool + t
    for m in node.get("mirror", []):
        tool = tool + mirror(tool, about=NAMED_PLANES[m])
    return tool, len(insts)


def expected_sign(node: dict[str, Any]) -> str:
    exp = (node.get("expect") or {}).get("dv")
    if exp:
        return exp
    c = node.get("combine", "add")
    return {"new": "+", "add": "+", "cut": "-", "intersect": "-0"}.get(c, "any")


def sign_ok(dv: float, want: str, vol: float) -> bool:
    eps = max(1e-6 * max(vol, 1.0), 1e-6)
    return {"+": dv > eps, "-": dv < -eps, "-0": dv <= eps, "any": True, "!0": abs(dv) > eps}[want]


def run_node(body: Any, node: dict[str, Any], ctx: Ctx, flog: Any) -> tuple[Any, dict[str, Any]]:
    """Execute one node. Returns (new_body, log). On failure new_body is the input body."""
    S = ctx.S
    t0 = time.time()
    op = node.get("op")
    nid = node.get("id", "?")
    S.context = nid
    rec: dict[str, Any] = {"id": nid, "name": node.get("name", ""), "op": op,
                           "combine": node.get("combine", "body" if op in BODY_OPS else "add"),
                           "status": "OK", "error": None}
    v0 = volume_of(body)
    n_fillets_before = len(flog.entries)
    layer = bind_let(S, node.get("let"))
    S.push(layer)
    try:
        for cond in node.get("assert", []):
            if not S.eval(cond):
                raise TreeError(f"assert failed: {cond}")
        if op in BODY_OPS:
            if body is None:
                raise TreeError(f"{op} on an empty body")
            if op in ("fillet", "chamfer"):
                radii = [S.num(node["r"])] + [S.num(x) for x in node.get("fallbacks", [])]
                new = flog.apply(body, f"{nid} {node.get('name', op)}", edge_selector(node["edges"], S),
                                 radii=radii, op=op, param=node.get("param"),
                                 why_fallback=node.get("why_fallback", ""))
                st = flog.entries[-1]["status"]
                rec["fillet_status"] = st
                rec["n_edges"] = flog.entries[-1]["n_edges"]
                if st not in ("OK", "REDUCED"):
                    rec["status"] = "FAILED"
                    rec["error"] = f"{op} {st}"
            else:  # mirror_body
                new = body + mirror(body, about=NAMED_PLANES[node["plane"]])
            rec["n_instances"] = 1
        elif op in PRIMITIVES:
            comb = node.get("combine", "add")
            if comb not in COMBINES:
                raise TreeError(f"unknown combine {comb!r}")
            tool, n = build_tool(node, ctx, flog)
            rec["n_instances"] = n
            rec["tool_volume"] = round(volume_of(tool), 6)
            try:
                bb = tool.bounding_box()
                rec["tool_bbox"] = [[round(bb.min.X, 4), round(bb.min.Y, 4), round(bb.min.Z, 4)],
                                    [round(bb.max.X, 4), round(bb.max.Y, 4), round(bb.max.Z, 4)]]
            except Exception:
                rec["tool_bbox"] = None
            if body is None or comb == "new":
                if body is not None and comb == "new":
                    raise TreeError("combine 'new' but a body already exists")
                new = tool
            elif comb == "add":
                new = body + tool
            elif comb == "cut":
                new = body - tool
            else:
                new = body & tool
        else:
            raise TreeError(f"unknown op {op!r}")
        new = as_part(new)
        dv = volume_of(new) - v0
        rec["dv"] = round(dv, 6)
        rec["volume"] = round(volume_of(new), 6)
        rec["solids"] = solids_of(new)
        rec["faces"] = len(new.faces())
        rec["valid"] = is_valid(new)
        want_solids = int((node.get("expect") or {}).get("solids", 1))
        want = expected_sign(node) if op not in ("fillet", "chamfer") else "!0"
        if rec["status"] == "OK":
            if not rec["valid"]:
                rec["status"], rec["error"] = "FAILED", "result not valid"
            elif rec["solids"] != want_solids:
                rec["status"], rec["error"] = "FAILED", f"solids {rec['solids']} != expected {want_solids}"
            elif not sign_ok(dv, want, v0):
                rec["status"], rec["error"] = "FAILED", f"volume delta {dv:+.6g} has the wrong sign (want {want})"
    except Exception as ex:  # OCP kernel errors (StdFail_NotDone, ...) are node failures, not crashes
        rec["status"] = "FAILED"
        rec["error"] = f"{type(ex).__name__}: {ex}"
        rec["trace"] = traceback.format_exc(limit=3)[-600:]
        new = body
    finally:
        S.pop()
    rec["seconds"] = round(time.time() - t0, 3)
    rec["fillet_entries"] = list(range(n_fillets_before, len(flog.entries)))
    if rec["status"] != "OK":
        rec["rolled_back"] = True
        return body, rec
    return new, rec


def lint_tree(tree: dict[str, Any]) -> list[str]:
    """Static rule checks. Errors returned as strings; an empty list means the tree may run."""
    errs = []
    nodes = tree.get("nodes", [])
    ids = [n.get("id") for n in nodes]
    if len(set(ids)) != len(ids) or None in ids:
        errs.append("every node needs a unique id")
    last_body_op = max((i for i, n in enumerate(nodes) if n.get("op") in PRIMITIVES), default=-1)
    for i, n in enumerate(nodes):
        if n.get("op") in ("fillet", "chamfer") and i < last_body_op and not n.get("local"):
            errs.append(f"{n.get('id')}: fillet before later add/cut nodes needs \"local\": true and a \"why\" "
                        "(fillets last by default, v0 rebuild Step 4)")
        if n.get("local") and not n.get("why"):
            errs.append(f"{n.get('id')}: local:true needs a why")
        if n.get("op") == "loft" and n.get("ruled"):
            errs.append(f"{n.get('id')}: ruled loft refused")
    for k, c in (tree.get("constants") or {}).items():
        if not isinstance(c, dict) or "value" not in c or not c.get("why"):
            errs.append(f"constant {k}: needs {{value, why}} (documented clearance)")
    return errs
