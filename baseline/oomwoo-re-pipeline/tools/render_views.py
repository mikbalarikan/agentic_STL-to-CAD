"""OOMWOO RE-line standard view renderer (v3 — replaces blender_doc_render.py).

Pure Python, headless, cross-platform (Windows + Linux). No GUI, no Blender.
Renders shaded orthographic views of a STEP, STL, or build123d .py shape with true
feature edges, plus on-demand sections, wireframes, closeups, arbitrary rotations,
and a scan-vs-CAD overlay.

Usage (run against LOCAL copies, never Drive-streamed paths):
  python render_views.py INPUT --out DIR --name OOM-W02              # iso/front/top/right
  python render_views.py INPUT --out DIR --name OOM-W02 --views iso,top
  python render_views.py INPUT --out DIR --name OOM-W02 --dir 1,-2,0.5      # custom view
  python render_views.py INPUT --out DIR --name OOM-W02 --section Z 4.5     # cut at Z=4.5
  python render_views.py INPUT --out DIR --name OOM-W02 --wireframe
  python render_views.py INPUT --out DIR --name OOM-W02 --closeup x0,y0,z0,x1,y1,z1
  python render_views.py CAD.step --out DIR --name OOM-W02 \
      --overlay scan.stl --align alignment.json                      # scan-vs-CAD

INPUT: .step/.stp (OCP tessellation, true BRep edges), .stl (trimesh, dihedral
edges), or .py (exec'd; must expose `result` = build123d part or TopoDS_Shape).

Outputs <name>_<view>.png, <name>_sec<axis><offset>.png, <name>_wire_<view>.png,
<name>_closeup_<view>.png, <name>_scan_vs_cad.png into --out.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- constants
RES = (1600, 1200)
MARGIN = 0.08                      # view margin as a fraction of extent
BG = 0.965                         # background gray
EDGE_GRAY = 0.15
FEATURE_EDGE_ANGLE_STL = 40.0      # dihedral threshold for STL feature edges (deg)
STD_VIEWS = {
    # name: (view direction = vector from part TOWARD the camera, label)
    "iso": (1.0, -1.0, 0.8),
    "front": (0.0, -1.0, 0.0),
    "top": (0.0, 0.0, 1.0),
    "right": (1.0, 0.0, 0.0),
}


# ---------------------------------------------------------------- loading
class Model:
    """Unified geometry: vertices V (n,3), faces F (m,3), edge polylines [(k,3)...]."""

    def __init__(self, V, F, edges, label=""):
        self.V = np.asarray(V, dtype=np.float64)
        self.F = np.asarray(F, dtype=np.int64)
        self.edges = [np.asarray(e, dtype=np.float64) for e in edges if len(e) >= 2]
        self.label = label

    @property
    def bounds(self):
        return self.V.min(axis=0), self.V.max(axis=0)

    def transformed(self, m4):
        m4 = np.asarray(m4, dtype=np.float64)
        V = (m4[:3, :3] @ self.V.T).T + m4[:3, 3]
        edges = [(m4[:3, :3] @ e.T).T + m4[:3, 3] for e in self.edges]
        return Model(V, self.F, edges, self.label)


def _load_step_shape(path: Path):
    from OCP.STEPControl import STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone

    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {path}")
    reader.TransferRoots()
    return reader.OneShape()


def _load_py_shape(path: Path):
    ns: dict = {"__name__": "__render_views_input__", "__file__": str(path)}
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    exec(code, ns)  # noqa: S102 — pipeline-authored build scripts only
    obj = ns.get("result")
    if obj is None:
        raise RuntimeError(f"{path} defines no `result` (build123d part or shape)")
    for attr in ("part", "solid", "shape"):        # BuildPart et al.
        inner = getattr(obj, attr, None)
        if inner is not None and not callable(inner):
            obj = inner
            break
    return obj.wrapped if hasattr(obj, "wrapped") else obj


def _tessellate_shape(shape, deflection: float) -> Model:
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.GCPnts import GCPnts_QuasiUniformDeflection
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.TopExp import TopExp
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopoDS import TopoDS

    BRepMesh_IncrementalMesh(shape, deflection, False, 0.25, True)

    verts, faces = [], []
    fmap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_FACE, fmap)
    for i in range(1, fmap.Extent() + 1):
        face = TopoDS.Face_s(fmap.FindKey(i))
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:
            continue
        trsf = loc.Transformation()
        base = len(verts)
        for n in range(1, tri.NbNodes() + 1):
            p = tri.Node(n).Transformed(trsf)
            verts.append((p.X(), p.Y(), p.Z()))
        for t in range(1, tri.NbTriangles() + 1):
            i1, i2, i3 = tri.Triangle(t).Get()
            faces.append((base + i1 - 1, base + i2 - 1, base + i3 - 1))

    edges = []
    emap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, emap)
    for i in range(1, emap.Extent() + 1):
        try:
            edge = TopoDS.Edge_s(emap.FindKey(i))
            if BRep_Tool.Degenerated_s(edge):
                continue
            curve = BRepAdaptor_Curve(edge)
            disc = GCPnts_QuasiUniformDeflection(curve, max(deflection, 0.02))
            if not disc.IsDone() or disc.NbPoints() < 2:
                continue
            pts = [disc.Value(n) for n in range(1, disc.NbPoints() + 1)]
            edges.append([(p.X(), p.Y(), p.Z()) for p in pts])
        except Exception:
            continue                                   # skip pathological edges
    if not faces:
        raise RuntimeError("tessellation produced no triangles")
    return Model(verts, faces, edges)


def _load_stl(path: Path) -> Model:
    import trimesh

    mesh = trimesh.load(str(path), force="mesh")
    if mesh.faces.shape[0] == 0:
        raise RuntimeError(f"empty mesh: {path}")
    edges = []
    try:
        ang = np.degrees(mesh.face_adjacency_angles)
        sharp = mesh.face_adjacency_edges[ang > FEATURE_EDGE_ANGLE_STL]
        if len(sharp) > 60000:                        # scans: cap edge clutter
            sharp = sharp[:0]
        edges = [mesh.vertices[e] for e in sharp]
    except Exception:
        pass
    return Model(mesh.vertices, mesh.faces, edges)


def load_model(path: Path, deflection: float) -> Model:
    ext = path.suffix.lower()
    if ext in (".step", ".stp"):
        return _tessellate_shape(_load_step_shape(path), deflection)
    if ext == ".py":
        return _tessellate_shape(_load_py_shape(path), deflection)
    if ext == ".stl":
        return _load_stl(path)
    raise RuntimeError(f"unsupported input type: {path}")


def load_align_matrix(path: Path) -> np.ndarray:
    data = json.loads(path.read_text(encoding="utf-8"))
    m = data.get("matrix_4x4")
    if m is None:
        raise RuntimeError(f"{path} has no 'matrix_4x4' key (RE_SPEC alignment contract)")
    flat = [x for row in m for x in row] if isinstance(m[0], list) else list(m)
    if len(flat) != 16:
        raise RuntimeError(f"'matrix_4x4' must have 16 numbers, got {len(flat)}")
    return np.array(flat, dtype=np.float64).reshape(4, 4)


# ---------------------------------------------------------------- camera & raster
def camera_basis(direction):
    v = np.asarray(direction, dtype=np.float64)
    n = np.linalg.norm(v)
    if n < 1e-12:
        raise RuntimeError("--dir must be a non-zero vector")
    v = v / n                                          # toward the camera
    up0 = np.array([0.0, 0.0, 1.0])
    if abs(v @ up0) > 0.9:
        up0 = np.array([0.0, 1.0, 0.0])
    right = np.cross(up0, v)
    right /= np.linalg.norm(right)
    up = np.cross(v, right)
    return right, up, v


def project(V, basis):
    right, up, v = basis
    return V @ right, V @ up, V @ v                    # x, y, depth (larger = closer)


def view_fit(x, y, res):
    w, h = res
    x0, x1 = float(np.min(x)), float(np.max(x))
    y0, y1 = float(np.min(y)), float(np.max(y))
    ex, ey = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
    scale = min(w / (ex * (1 + 2 * MARGIN)), h / (ey * (1 + 2 * MARGIN)))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return scale, cx, cy


def to_px(x, y, fit, res):
    scale, cx, cy = fit
    w, h = res
    px = (x - cx) * scale + w / 2
    py = h / 2 - (y - cy) * scale                      # +y up
    return px, py


def rasterize(model: Model, basis, fit, res, base_rgb=(0.62, 0.64, 0.66)):
    """Z-buffer lambert render. Returns (rgb HxWx3, zbuf HxW, mask HxW)."""
    w, h = res
    x, y, z = project(model.V, basis)
    px, py = to_px(x, y, fit, res)
    P = np.stack([px, py], axis=1)
    tri = model.F
    zbuf = np.full((h, w), -np.inf)
    shade = np.zeros((h, w))
    mask = np.zeros((h, w), dtype=bool)

    v = basis[2]
    n = np.cross(model.V[tri[:, 1]] - model.V[tri[:, 0]],
                 model.V[tri[:, 2]] - model.V[tri[:, 0]])
    nl = np.linalg.norm(n, axis=1)
    ok = nl > 1e-12
    n[ok] = n[ok] / nl[ok][:, None]
    light = v + np.array([0.35, 0.25, 0.55])
    light /= np.linalg.norm(light)
    inten = 0.32 + 0.58 * np.abs(n @ light) + 0.10 * np.abs(n @ v)  # two-sided

    A, B, C = P[tri[:, 0]], P[tri[:, 1]], P[tri[:, 2]]
    ZA, ZB, ZC = z[tri[:, 0]], z[tri[:, 1]], z[tri[:, 2]]
    area = (B[:, 0] - A[:, 0]) * (C[:, 1] - A[:, 1]) - \
           (B[:, 1] - A[:, 1]) * (C[:, 0] - A[:, 0])
    xmin = np.clip(np.floor(np.minimum.reduce([A[:, 0], B[:, 0], C[:, 0]])), 0, w - 1).astype(int)
    xmax = np.clip(np.ceil(np.maximum.reduce([A[:, 0], B[:, 0], C[:, 0]])), 0, w - 1).astype(int)
    ymin = np.clip(np.floor(np.minimum.reduce([A[:, 1], B[:, 1], C[:, 1]])), 0, h - 1).astype(int)
    ymax = np.clip(np.ceil(np.maximum.reduce([A[:, 1], B[:, 1], C[:, 1]])), 0, h - 1).astype(int)

    for i in range(len(tri)):
        if not ok[i] or abs(area[i]) < 1e-9:
            continue
        x0, x1_, y0, y1_ = xmin[i], xmax[i], ymin[i], ymax[i]
        if x1_ < x0 or y1_ < y0:
            continue
        gx = np.arange(x0, x1_ + 1) + 0.5
        gy = np.arange(y0, y1_ + 1) + 0.5
        GX, GY = np.meshgrid(gx, gy)
        ax_, ay_ = A[i]
        w0 = ((B[i, 0] - ax_) * (GY - ay_) - (B[i, 1] - ay_) * (GX - ax_)) / area[i]
        w1 = ((GX - ax_) * (C[i, 1] - ay_) - (GY - ay_) * (C[i, 0] - ax_)) / area[i]
        # barycentric: l1*B + l2*C + (1-l1-l2)*A with orientation-safe formulation
        l2 = w0
        l1 = w1
        l0 = 1.0 - l1 - l2
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not inside.any():
            continue
        depth = l0 * ZA[i] + l1 * ZB[i] + l2 * ZC[i]
        sub_z = zbuf[y0:y1_ + 1, x0:x1_ + 1]
        upd = inside & (depth > sub_z)
        if not upd.any():
            continue
        sub_z[upd] = depth[upd]
        shade[y0:y1_ + 1, x0:x1_ + 1][upd] = inten[i]
        mask[y0:y1_ + 1, x0:x1_ + 1][upd] = True

    rgb = np.full((h, w, 3), BG)
    for c in range(3):
        ch = rgb[:, :, c]
        ch[mask] = np.clip(shade[mask] * base_rgb[c] / 0.66, 0, 1)
    return rgb, zbuf, mask


def draw_edges(rgb, zbuf, model: Model, basis, fit, res, diag, color=EDGE_GRAY):
    """Depth-tested feature edges, drawn 1px with a small bias."""
    w, h = res
    eps = 0.015 * diag
    for pl in model.edges:
        x, y, z = project(pl, basis)
        px, py = to_px(x, y, fit, res)
        for j in range(len(px) - 1):
            seg = math.hypot(px[j + 1] - px[j], py[j + 1] - py[j])
            n = max(int(seg), 1)
            t = np.linspace(0, 1, n + 1)
            sx = px[j] + (px[j + 1] - px[j]) * t
            sy = py[j] + (py[j + 1] - py[j]) * t
            sz = z[j] + (z[j + 1] - z[j]) * t
            ix = np.round(sx).astype(int)
            iy = np.round(sy).astype(int)
            valid = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h)
            ix, iy, sz = ix[valid], iy[valid], sz[valid]
            vis = sz >= zbuf[iy, ix] - eps
            rgb[iy[vis], ix[vis]] = color
    return rgb


def silhouette_edges(model: Model, basis):
    """Per-view silhouette: mesh edges whose two faces face opposite sides."""
    import trimesh

    mesh = trimesh.Trimesh(model.V, model.F, process=False)
    v = basis[2]
    fn = mesh.face_normals @ v
    adj = mesh.face_adjacency
    flip = (fn[adj[:, 0]] * fn[adj[:, 1]]) < 0
    segs = mesh.vertices[mesh.face_adjacency_edges[flip]]
    return [s for s in segs]


def save_png(rgb, out_path: Path, title: str, mm_per_px: float, annotations=None):
    h, w, _ = rgb.shape
    dpi = 100
    fig = plt.figure(figsize=(w / dpi, (h + 70) / dpi), dpi=dpi)
    ax = fig.add_axes([0, 70 / (h + 70), 1, h / (h + 70)])
    ax.imshow(rgb, interpolation="nearest")
    for px, py, text, color in (annotations or []):
        if 0 <= px < w and 0 <= py < h:
            ax.text(px, py, text, color=color, fontsize=15, fontweight="bold",
                    ha="center", va="center")
    ax.set_axis_off()
    # scale bar: a round length ~15% of width
    target_mm = mm_per_px * w * 0.15
    nice = min((s for s in (1, 2, 5, 10, 20, 25, 50, 100, 200)
                if s >= target_mm), default=200)
    bar_px = nice / mm_per_px
    ax2 = fig.add_axes([0, 0, 1, 70 / (h + 70)])
    ax2.set_xlim(0, w)
    ax2.set_ylim(0, 70)
    ax2.set_axis_off()
    ax2.plot([40, 40 + bar_px], [42, 42], color="k", lw=3)
    ax2.text(40, 18, f"{nice} mm", fontsize=13)
    ax2.text(w - 20, 18, title, fontsize=13, ha="right")
    fig.savefig(out_path, facecolor="white")
    plt.close(fig)
    print(f"[render_views] wrote {out_path}")


AXIS_COLORS = {"X": (0.85, 0.10, 0.10), "Y": (0.10, 0.62, 0.10), "Z": (0.10, 0.20, 0.90)}


def draw_line_px(rgb, p0, p1, color, thick=2):
    """Draw a 2D pixel line, no depth test (always on top)."""
    h, w, _ = rgb.shape
    seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = max(int(seg), 1)
    t = np.linspace(0, 1, n + 1)
    sx = np.round(p0[0] + (p1[0] - p0[0]) * t).astype(int)
    sy = np.round(p0[1] + (p1[1] - p0[1]) * t).astype(int)
    for dx in range(-(thick // 2), thick // 2 + 1):
        for dy in range(-(thick // 2), thick // 2 + 1):
            ix, iy = sx + dx, sy + dy
            ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h)
            rgb[iy[ok], ix[ok]] = color


def render_datum_view(model, view_name, direction, out_dir, name, res):
    """F00 submission view: shaded aligned mesh + RGB axes triad + origin marker."""
    basis = camera_basis(direction)
    lo, hi = model.bounds
    axis_len = 0.55 * float(np.max(hi - lo))
    # fit must include the triad tips so axes are never clipped
    tips = np.array([[0, 0, 0], [axis_len, 0, 0], [0, axis_len, 0], [0, 0, axis_len]])
    fit_pts = np.vstack([model.V, tips])
    x, y, _ = project(fit_pts, basis)
    fit = view_fit(x, y, res)
    diag = float(np.linalg.norm(hi - lo))
    rgb, zbuf, _ = rasterize(model, basis, fit, res)
    rgb = draw_edges(rgb, zbuf, model, basis, fit, res, diag)

    annotations = []
    ox, oy, _ = project(np.zeros((1, 3)), basis)
    opx, opy = to_px(ox, oy, fit, res)
    for ax_name, tip in (("X", tips[1]), ("Y", tips[2]), ("Z", tips[3])):
        tx, ty, _ = project(tip.reshape(1, 3), basis)
        tpx, tpy = to_px(tx, ty, fit, res)
        col = AXIS_COLORS[ax_name]
        if math.hypot(tpx[0] - opx[0], tpy[0] - opy[0]) < 3:
            continue                        # axis points at the camera in this view
        draw_line_px(rgb, (opx[0], opy[0]), (tpx[0], tpy[0]), col)
        lx = tpx[0] + 0.04 * (tpx[0] - opx[0]) / max(abs(tpx[0] - opx[0]), 1) * 30
        ly = tpy[0] + 0.04 * (tpy[0] - opy[0]) / max(abs(tpy[0] - opy[0]), 1) * 30
        annotations.append((lx, ly, ax_name, col))
    # origin marker: black crosshair + white ring
    for ang in np.linspace(0, 2 * math.pi, 32):
        px = opx[0] + 9 * math.cos(ang)
        py = opy[0] + 9 * math.sin(ang)
        draw_line_px(rgb, (px, py), (px, py), (1.0, 1.0, 1.0), thick=3)
    draw_line_px(rgb, (opx[0] - 12, opy[0]), (opx[0] + 12, opy[0]), (0, 0, 0), thick=1)
    draw_line_px(rgb, (opx[0], opy[0] - 12), (opx[0], opy[0] + 12), (0, 0, 0), thick=1)

    save_png(rgb, Path(out_dir) / f"{name}_datum_{view_name}.png",
             f"{name} — DATUM {view_name}  (X red / Y green / Z blue, ⊕ = origin)",
             mm_per_px=1.0 / fit[0], annotations=annotations)


# ---------------------------------------------------------------- view products
def render_view(model, view_name, direction, out_dir, name, res,
                overlay: Model | None = None, prefix=""):
    basis = camera_basis(direction)
    fit_src = model if overlay is None else Model(
        np.vstack([model.V, overlay.V]), [[0, 0, 0]], [])
    x, y, _ = project(fit_src.V, basis)
    fit = view_fit(x, y, res)
    lo, hi = fit_src.bounds
    diag = float(np.linalg.norm(hi - lo))
    rgb, zbuf, _ = rasterize(model, basis, fit, res)
    rgb = draw_edges(rgb, zbuf, model, basis, fit, res, diag)
    fname = f"{name}_{prefix}{view_name}.png"
    if overlay is not None:
        o_rgb, o_z, o_mask = rasterize(overlay, basis, fit, res,
                                       base_rgb=(1.0, 0.45, 0.08))
        blend = o_mask
        rgb[blend] = 0.55 * o_rgb[blend] + 0.45 * rgb[blend]
        fname = f"{name}_scan_vs_cad.png"
    save_png(rgb, Path(out_dir) / fname,
             f"{name} — {prefix}{view_name}" + ("  (scan=orange)" if overlay is not None else ""),
             mm_per_px=1.0 / fit[0])


def render_wireframe(model, view_name, direction, out_dir, name, res):
    basis = camera_basis(direction)
    x, y, _ = project(model.V, basis)
    fit = view_fit(x, y, res)
    lo, hi = model.bounds
    diag = float(np.linalg.norm(hi - lo))
    w, h = res
    rgb = np.full((h, w, 3), 1.0)
    zfree = np.full((h, w), -np.inf)                   # no occlusion in wireframe
    sil = silhouette_edges(model, basis)
    wire = Model(model.V, model.F, list(model.edges) + sil)
    rgb = draw_edges(rgb, zfree, wire, basis, fit, res, diag, color=0.1)
    save_png(rgb, Path(out_dir) / f"{name}_wire_{view_name}.png",
             f"{name} — wireframe {view_name}", mm_per_px=1.0 / fit[0])


def render_section(model, axis: str, offset: float, out_dir, name):
    import trimesh

    mesh = trimesh.Trimesh(model.V, model.F, process=False)
    normals = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}
    axes2d = {"X": (1, 2, "Y (mm)", "Z (mm)"),
              "Y": (0, 2, "X (mm)", "Z (mm)"),
              "Z": (0, 1, "X (mm)", "Y (mm)")}
    n = normals[axis]
    origin = np.array(n, dtype=float) * offset
    lines = trimesh.intersections.mesh_plane(mesh, plane_normal=n, plane_origin=origin)
    if len(lines) == 0:
        raise RuntimeError(f"section {axis}={offset} does not intersect the part")
    i, j, xl, yl = axes2d[axis]
    fig, ax = plt.subplots(figsize=(12, 9), dpi=110)
    for seg in lines:
        ax.plot(seg[:, i], seg[:, j], color="#1440a0", lw=1.2)
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_title(f"{name} — section {axis} = {offset:g} mm")
    # cad-section rule: expand limits so nothing is ever clipped at the frame
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 - 0.1 * (x1 - x0), x1 + 0.1 * (x1 - x0))
    ax.set_ylim(y0 - 0.1 * (y1 - y0), y1 + 0.1 * (y1 - y0))
    out = Path(out_dir) / f"{name}_sec{axis}{offset:g}.png"
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"[render_views] wrote {out}")


def clip_model(model: Model, bbox) -> Model:
    lo = np.array(bbox[:3], dtype=float)
    hi = np.array(bbox[3:], dtype=float)
    keep_v = np.all((model.V >= lo - 1e-9) & (model.V <= hi + 1e-9), axis=1)
    keep_f = keep_v[model.F].any(axis=1)
    F = model.F[keep_f]
    if len(F) == 0:
        raise RuntimeError("closeup bbox contains no geometry")
    # compact V to the vertices the clipped faces use — render_view fits the
    # camera from V, so leftover out-of-bbox vertices would defeat the zoom
    used = np.unique(F)
    remap = np.full(len(model.V), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    V = model.V[used]
    F = remap[F]
    edges = []
    for pl in model.edges:
        inside = np.flatnonzero(
            np.all((pl >= lo - 1e-9) & (pl <= hi + 1e-9), axis=1))
        # contiguous inside runs only — a polyline that dips into the bbox must
        # not drag its out-of-bbox tail into the closeup
        for run in np.split(inside, np.flatnonzero(np.diff(inside) > 1) + 1):
            if len(run) >= 2:
                edges.append(pl[run])
    return Model(V, F, edges)


# ---------------------------------------------------------------- main
def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help=".step/.stp, .stl, or build123d .py exposing `result`")
    p.add_argument("--out", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--views", default="iso,front,top,right",
                   help="comma list from iso,front,top,right (default: all four)")
    p.add_argument("--dir", default=None,
                   help="dx,dy,dz — additional arbitrary view direction")
    p.add_argument("--section", nargs=2, metavar=("AXIS", "OFFSET"), default=None,
                   help="X|Y|Z and offset in mm — 2D cut plot")
    p.add_argument("--wireframe", action="store_true",
                   help="also render wireframe versions of the selected views")
    p.add_argument("--closeup", default=None,
                   help="x0,y0,z0,x1,y1,z1 world-mm bbox to zoom into")
    p.add_argument("--overlay", default=None,
                   help="scan STL to composite over the CAD (orange, iso view)")
    p.add_argument("--align", default=None,
                   help="alignment.json with matrix_4x4; applied to --overlay if given, "
                        "otherwise to INPUT (e.g. a raw-coords scan for --datum)")
    p.add_argument("--datum", action="store_true",
                   help="F00 datum submission set: iso+front+top+right of the ALIGNED "
                        "mesh with RGB axes triad and origin marker")
    p.add_argument("--res", default=f"{RES[0]}x{RES[1]}")
    p.add_argument("--deflection", type=float, default=0.05,
                   help="tessellation deflection for STEP/.py inputs (mm)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    res = tuple(int(v) for v in args.res.lower().split("x"))

    model = load_model(Path(args.input), args.deflection)
    print(f"[render_views] {args.input}: {len(model.V)} verts, {len(model.F)} tris, "
          f"{len(model.edges)} edge polylines")
    if args.align and not args.overlay:
        model = model.transformed(load_align_matrix(Path(args.align)))
        print("[render_views] applied --align to input")

    views = {}
    for v in [s.strip() for s in args.views.split(",") if s.strip()]:
        if v not in STD_VIEWS:
            raise RuntimeError(f"unknown view '{v}' (have {list(STD_VIEWS)})")
        views[v] = STD_VIEWS[v]
    if args.dir:
        views["custom"] = tuple(float(c) for c in args.dir.split(","))

    if args.datum:
        for vname in ("iso", "front", "top", "right"):
            render_datum_view(model, vname, STD_VIEWS[vname], out_dir, args.name, res)
        print("[render_views] DONE")
        return

    target = model
    prefix = ""
    if args.closeup:
        target = clip_model(model, [float(c) for c in args.closeup.split(",")])
        prefix = "closeup_"

    overlay = None
    if args.overlay:
        overlay = _load_stl(Path(args.overlay))
        if args.align:
            overlay = overlay.transformed(load_align_matrix(Path(args.align)))
        render_view(model, "iso", views.get("iso", STD_VIEWS["iso"]), out_dir,
                    args.name, res, overlay=overlay)
        return

    for vname, vdir in views.items():
        render_view(target, vname, vdir, out_dir, args.name, res, prefix=prefix)
        if args.wireframe:
            render_wireframe(target, vname, vdir, out_dir, args.name, res)

    if args.section:
        render_section(model, args.section[0].upper(), float(args.section[1]),
                       out_dir, args.name)

    print("[render_views] DONE")


if __name__ == "__main__":
    sys.exit(main())
