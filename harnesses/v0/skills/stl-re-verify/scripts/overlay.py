#!/usr/bin/env python3
"""Section overlays, CAD (red) on scan (black), with a per-panel scan-trace count so an empty
panel is flagged instead of read as agreement (CHK-OVERLAY).

Provenance:
  - Z sections + radial half-plane sections: golden-examples/dreame_brush-caps/report/source/overlay.py
    (zsec, rsec: half-plane r>0 chains, scan black / CAD red)
  - axis-aligned planes with explicit limits: golden-examples/OD-H12_delonghi-dedica-pump/report/src/ovl.py
    (spec "axis:value:xmin,xmax,ymin,ymax"; scan blue / CAD red there)
  - per-panel scan count: NEW CODE. Earned by the dreame snap overlay whose 150 deg radial panel
    shows no scan trace (analysis/golden/dreame_brush-caps.md §12 lesson 11; analysis/SYNTHESIS.md E12).
Deterministic: no randomness; matplotlib Agg backend.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, load_matrix, load_mesh, merge_into_gate, step_to_mesh, write_json  # noqa: E402

TOOL = "overlay.py"


def _segments(m: Any, origin: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """(n, 2, 3) section segments (OD ovl.py: trimesh.intersections.mesh_plane; no networkx needed)."""
    import trimesh

    seg = trimesh.intersections.mesh_plane(m, normal, origin)
    return np.asarray(seg).reshape(-1, 2, 3)


def zsec(m: Any, z: float) -> np.ndarray:
    return _segments(m, np.array([0, 0, z]), np.array([0, 0, 1.0]))[:, :, :2]


def rsec(m: Any, th: float) -> np.ndarray:
    """Radial half-plane through the Z axis at angle th: (r, z) segments with r > 0 (DRM overlay.py:rsec)."""
    t = np.radians(th)
    d = np.array([np.cos(t), np.sin(t), 0.0])
    n = np.array([-np.sin(t), np.cos(t), 0.0])
    S = _segments(m, np.zeros(3), n)
    r = S @ d
    keep = (r > 0).all(1)
    return np.stack([r[keep], S[keep][:, :, 2]], axis=2)


def asec(m: Any, axis: int, v: float) -> np.ndarray:
    n = np.zeros(3)
    n[axis] = 1
    o = np.zeros(3)
    o[axis] = v
    oth = [i for i in range(3) if i != axis]
    return _segments(m, o, n)[:, :, oth]


def length(seg: np.ndarray) -> float:
    return float(np.linalg.norm(seg[:, 1] - seg[:, 0], axis=1).sum()) if len(seg) else 0.0


def main(argv: list[str] | None = None) -> int:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scan", required=True)
    ap.add_argument("--align", help="raw scan -> datum 4x4")
    ap.add_argument("--cad", required=True, help="STEP (tessellated here) or STL")
    ap.add_argument("--cad-matrix")
    ap.add_argument("--z", default="", help="comma list of Z planes")
    ap.add_argument("--theta", default="", help="comma list of radial half-plane angles (deg)")
    ap.add_argument("--planes", default="", help="'x:val;y:val' axis-aligned planes (OD ovl.py style)")
    ap.add_argument("--min-scan-length-mm", type=float, default=0.0,
                    help="panel flagged when scan trace length <= this (0 = flag only empty panels)")
    ap.add_argument("--out", required=True, help="PNG path, e.g. qa/overlays/overlay.png")
    ap.add_argument("--json", required=True, help="panel report, e.g. qa/overlays/overlay.json")
    ap.add_argument("--gate", help="merge into gate.json under 'overlays'")
    a = ap.parse_args(argv)

    scan = load_mesh(a.scan)
    if a.align:
        scan.apply_transform(load_matrix(a.align))
    cp = Path(a.cad)
    cad = (step_to_mesh(cp, Path(tempfile.mkdtemp(prefix="qa_ovl_")) / "cad.stl")
           if cp.suffix.lower() in (".step", ".stp") else load_mesh(cp))
    if a.cad_matrix:
        cad.apply_transform(load_matrix(a.cad_matrix))

    panels: list[tuple[str, np.ndarray, np.ndarray, str, str]] = []
    for z in [float(t) for t in a.z.split(",") if t.strip()]:
        panels.append((f"Z={z}", zsec(scan, z), zsec(cad, z), "x", "y"))
    for th in [float(t) for t in a.theta.split(",") if t.strip()]:
        panels.append((f"radial θ={th}°", rsec(scan, th), rsec(cad, th), "r", "z"))
    for spec in [s for s in a.planes.split(";") if s.strip()]:
        ax_, v = spec.split(":")[:2]
        i = "xyz".index(ax_)
        oth = [c for c in "xyz" if c != ax_]
        panels.append((f"{ax_}={v}", asec(scan, i, float(v)), asec(cad, i, float(v)), oth[0], oth[1]))
    if not panels:
        raise SystemExit("no panels requested")

    cols = min(3, len(panels))
    rows = (len(panels) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 7 * rows), dpi=100)
    axes = np.atleast_1d(axes).ravel()
    report = []
    for ax, (title, S, C, hx, vy) in zip(axes, panels):
        if len(S):
            ax.add_collection(LineCollection(S, colors="k", linewidths=0.7))
        if len(C):
            ax.add_collection(LineCollection(C, colors="r", linewidths=0.9))
        both = np.concatenate([x.reshape(-1, 2) for x in (S, C) if len(x)]) if (len(S) or len(C)) else np.zeros((1, 2))
        pad = 0.05 * max(np.ptp(both[:, 0]), np.ptp(both[:, 1]), 1.0)
        ax.set_xlim(both[:, 0].min() - pad, both[:, 0].max() + pad)
        ax.set_ylim(both[:, 1].min() - pad, both[:, 1].max() + pad)
        sl, cl = length(S), length(C)
        empty = sl <= a.min_scan_length_mm
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)
        ax.set_xlabel(hx)
        ax.set_ylabel(vy)
        ax.set_title(f"{title} — scan black / CAD red" + ("  [NO SCAN TRACE]" if empty else ""),
                     color="crimson" if empty else "black")
        report.append({"panel": title, "scan_segments": int(len(S)), "scan_length_mm": sl,
                       "cad_segments": int(len(C)), "cad_length_mm": cl, "scan_empty": bool(empty),
                       "cad_empty": cl == 0.0})
    for ax in axes[len(panels):]:
        ax.axis("off")
    fig.tight_layout()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out)
    plt.close(fig)
    flagged = [r["panel"] for r in report if r["scan_empty"]]
    out = {**header("overlay", TOOL, [a.scan, a.cad] + [p for p in (a.align, a.cad_matrix) if p], None),
           "png": a.out, "panels": report, "empty_scan_panels": flagged,
           "CHK-OVERLAY": {"ran": True, "result": "finding" if flagged else "pass",
                           "note": ("panels without scan trace: " + ", ".join(flagged)) if flagged
                           else "every panel shows scan"}}
    write_json(a.json, out)
    if a.gate:
        merge_into_gate(a.gate, "overlays", out)
    for r in report:
        print(f"{r['panel']:18s} scan {r['scan_segments']:6d} segs {r['scan_length_mm']:9.2f} mm | "
              f"CAD {r['cad_segments']:6d} segs {r['cad_length_mm']:9.2f} mm {'<-- NO SCAN' if r['scan_empty'] else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
