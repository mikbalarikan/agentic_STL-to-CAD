"""Progress renders for a facet-film run: 2D kit plots and 3D sheet-over-scan views.

Two entry points, both callable as functions or via CLI:

  render_kit_2d(dxf_path, png_path)
      Deterministic matplotlib plot of a kit DXF (equal aspect, piece labels from
      TEXT entities, closed loops in ink, holes dashed). Needs ezdxf + matplotlib.

  render_sheets_3d(mesh_path, pieces, png_path, camera=None)
      The walkthrough view: 3D boundary curves / ruled sheets drawn over the scan
      mesh with pyvista (off-screen). `pieces` is a list of dicts with 3D data:
        {"id": str, "A": Nx3, "B": Nx3}   -> ruled strip triangulated from A/B
      Builders should persist each recipe-C/D piece's matched boundary samples
      (A, B) in its piece JSON as "curves3d"; that is all this needs. Skipped
      with a message when pyvista is missing (it is optional, not a gate).

CLI:  python render_progress.py kit  <kit.dxf> <out.png>
      python render_progress.py 3d   <mesh.stl> <pieces.json>... <out.png>
"""

from __future__ import annotations

import json
import sys

import numpy as np

PAL = ["#e6553f", "#3f8fe6", "#3fb96b", "#e6a83f", "#9a5fe0", "#e05fa0", "#40c4c4", "#b0b840"]


def render_kit_2d(dxf_path: str, png_path: str) -> None:
    import ezdxf
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.math import bulge_to_arc

    fig, ax = plt.subplots(figsize=(14, 10))
    doc = ezdxf.readfile(dxf_path)
    for e in doc.modelspace():
        t = e.dxftype()
        if t == "LWPOLYLINE":
            pts = list(e.get_points())
            xy = []
            n = len(pts)
            for i in range(n):
                x, y, _, _, b = pts[i]
                xy.append((x, y))
                if abs(b) > 1e-12:
                    x2, y2 = pts[(i + 1) % n][:2]
                    c, sa, ea, r = bulge_to_arc((x, y), (x2, y2), b)
                    if ea < sa:
                        ea += 2 * np.pi
                    th = np.linspace(sa, ea, 24)
                    xy += [(c[0] + r * np.cos(a), c[1] + r * np.sin(a)) for a in th]
            xy.append(xy[0])
            X, Y = zip(*xy, strict=False)
            dashed = e.dxf.layer == "CUT_INNER"
            ax.plot(X, Y, lw=0.9, color="#20242a", ls="--" if dashed else "-")
        elif t == "CIRCLE":
            c, r = e.dxf.center, e.dxf.radius
            th = np.linspace(0, 2 * np.pi, 120)
            ax.plot(c[0] + r * np.cos(th), c[1] + r * np.sin(th), lw=0.9, color="#20242a")
        elif t == "TEXT":
            p = e.dxf.insert
            ax.text(p[0], p[1], e.dxf.text, fontsize=5, color="#2f6f9f", ha="center")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_sheets_3d(mesh_path: str, pieces: list[dict], png_path: str, camera=None) -> bool:
    try:
        import pyvista as pv
    except ImportError:
        print("render_sheets_3d skipped: pyvista not installed (optional)")
        return False
    import trimesh

    m = trimesh.load(mesh_path, process=False, force="mesh")
    if len(m.faces) > 800_000:
        try:
            import fast_simplification

            v, f = fast_simplification.simplify(
                m.vertices.astype(np.float32), m.faces.astype(np.int32), target_count=400_000
            )
            m = trimesh.Trimesh(v, f, process=False)
        except ImportError:
            pass
    grid = pv.PolyData(m.vertices, np.c_[np.full(len(m.faces), 3), m.faces].ravel())
    p = pv.Plotter(off_screen=True, window_size=(1500, 1000))
    p.set_background("white")
    p.add_mesh(grid, color="#dcdcdc", smooth_shading=True, ambient=0.25, diffuse=0.85)
    for k, piece in enumerate(pieces):
        A = np.asarray(piece["A"], float)
        B = np.asarray(piece["B"], float)
        n = len(A)
        V = np.vstack([A, B])
        tris = []
        for i in range(n - 1):
            tris += [[i, n + i, n + i + 1], [i, n + i + 1, i + 1]]
        F = np.asarray(tris)
        sheet = pv.PolyData(V, np.c_[np.full(len(F), 3), F].ravel())
        p.add_mesh(sheet, color=PAL[k % len(PAL)], ambient=0.55, specular=0.15)
    b = grid.bounds
    c = np.array([(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2])
    d = max(b[1] - b[0], b[3] - b[2]) * 0.62
    p.camera_position = camera or [
        tuple(c + np.array([0.5 * d, -0.72 * d, 0.65 * d])),
        tuple(c),
        (0, 0, 1),
    ]
    p.screenshot(png_path)
    p.close()
    return True


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "kit":
        render_kit_2d(sys.argv[2], sys.argv[3])
    elif mode == "3d":
        mesh, *piece_files, out = sys.argv[2:]
        pieces = []
        for pf in piece_files:
            data = json.load(open(pf, encoding="utf-8"))
            for pc in data.get("pieces", []):
                c3 = pc.get("curves3d")
                if c3 and "A" in c3:
                    pieces.append({"id": pc["id"], "A": c3["A"], "B": c3["B"]})
        render_sheets_3d(mesh, pieces, out)
    print("ok")
