#!/usr/bin/env python3
"""Planar and radial half-plane sections, (r,z)/(theta,r) density maps and R(theta) profiles.

Provenance:
  - planar z-sections with closed-loop filtering, Kasa circle per loop and the (r,z) /
    (theta,r) hist2d density maps: golden-examples/dreame_brush-caps/report/source/align.py
    (:55-84 loops, :128-141 maps).
  - radial half-plane sections (plane through +Z at azimuth theta, keep r>0 chunks):
    golden-examples/dreame_brush-caps/report/source/overlay.py:rsec and
    golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/50_overlays_it2.py:meridian_segs.
  - R(theta) outer/inner envelope: OOM-B02 40_verify.py:62-65 (0.25 deg stations,
    +/-0.3 deg window) via sim_caliper.outer_envelope.
Changes: loop matching across stations by centroid (NEW), area-weighted face-centroid maps
(tessellation-density independent) saved as .npz (PNG only if matplotlib is installed),
no networkx dependency, typed, argparse, run-contract §2 header. All angles in the frozen
DATUM frame, theta CCW about +Z from +X (CHK-FRAME).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (densify, face_components, header, is_closed, load_alignment, load_mesh, rnd,  # noqa: E402
                    section_polylines, shoelace, write_json)
from fits import circle_kasa  # noqa: E402
from sim_caliper import gaps, outer_envelope  # noqa: E402


def planar(mesh, zs: list[float], min_area: float) -> list[dict[str, Any]]:
    out = []
    for z in zs:
        loops = []
        for i, p in enumerate(section_polylines(mesh, [0, 0, z], [0, 0, 1])):
            xy = p[:, :2]
            closed = is_closed(xy, 1e-6)
            a, c = shoelace(xy) if closed else (0.0, xy.mean(axis=0))
            if closed and abs(a) < min_area:
                continue
            r = np.hypot(xy[:, 0], xy[:, 1])
            L = float(np.linalg.norm(np.diff(xy, axis=0), axis=1).sum())
            rec: dict[str, Any] = {"id": f"z{z:g}_l{i}", "closed": closed, "n": int(len(xy)),
                                   "area": rnd(a), "centroid": [rnd(c[0]), rnd(c[1])],
                                   "perimeter": rnd(L), "r_min": rnd(r.min()), "r_max": rnd(r.max())}
            if len(xy) >= 5:
                k = circle_kasa(densify(xy))
                rec["circle"] = {"cx": k["cx"], "cy": k["cy"], "r": k["r"], "rms": k["residual"]["rms"],
                                 "max": k["residual"]["max"]}
            loops.append(rec)
        out.append({"z": z, "loops": loops})
    return out


def match_tracks(stations: list[dict[str, Any]], tol: Optional[float]) -> list[list[str]]:
    """Chain loops station-to-station by nearest centroid (greedy, deterministic order)."""
    tracks: list[list[str]] = []
    prev: list[tuple[int, np.ndarray]] = []
    for st in stations:
        cur = [(l["id"], np.array(l["centroid"], float), abs(l["area"] or 0.0)) for l in st["loops"] if l["closed"]]
        used: set[int] = set()
        new_prev: list[tuple[int, np.ndarray]] = []
        for lid, c, _a in sorted(cur, key=lambda t: -t[2]):
            best, bd = None, np.inf
            for ti, pc in prev:
                if ti in used:
                    continue
                d = float(np.linalg.norm(c - pc))
                if d < bd:
                    best, bd = ti, d
            if best is not None and (tol is None or bd <= tol):
                tracks[best].append(lid)
                used.add(best)
                new_prev.append((best, c))
            else:
                tracks.append([lid])
                new_prev.append((len(tracks) - 1, c))
        prev = new_prev
    return tracks


def radial(mesh, thetas: list[float]) -> dict[str, list[np.ndarray]]:
    res: dict[str, list[np.ndarray]] = {}
    for th in thetas:
        t = np.radians(th)
        d = np.array([np.cos(t), np.sin(t), 0.0])
        n = np.array([-np.sin(t), np.cos(t), 0.0])
        chunks = []
        for P in section_polylines(mesh, [0, 0, 0], n):
            r = P @ d
            k = r > 0
            if k.sum() < 2:
                continue
            idx = np.where(k)[0]
            br = np.where(np.diff(idx) > 1)[0]
            for ch in np.split(idx, br + 1):
                if len(ch) >= 2:
                    chunks.append(np.c_[r[ch], P[ch, 2]])
        res[f"theta_{th:g}"] = chunks
    return res


def maps(mesh, rz_bins: tuple[int, int], tr_bins: tuple[int, int]) -> dict[str, np.ndarray]:
    c = mesh.triangles_center
    a = mesh.area_faces
    r = np.hypot(c[:, 0], c[:, 1])
    th = np.degrees(np.arctan2(c[:, 1], c[:, 0]))
    H1, re, ze = np.histogram2d(r, c[:, 2], bins=rz_bins, weights=a)
    H2, te, re2 = np.histogram2d(th, r, bins=tr_bins, range=[[-180, 180], [0, r.max()]], weights=a)
    return {"rz": H1, "rz_r_edges": re, "rz_z_edges": ze, "thr": H2, "thr_theta_edges": te, "thr_r_edges": re2}


def cluster(mesh, zb: Optional[str], rb: Optional[str], tb: Optional[str], top_band: Optional[float]) -> dict[str, Any]:
    """CHK-CLUSTER evidence: how much coherent scan material sits in a box (P03 it1 stem)."""
    from fits import plane_svd, select_box

    def pair(s: Optional[str]):
        return tuple(float(v) for v in s.split(",")) if s else None

    c = mesh.triangles_center
    k = select_box(c, pair(zb), pair(rb), pair(tb))
    kv = select_box(mesh.vertices, pair(zb), pair(rb), pair(tb))
    res: dict[str, Any] = {"box": {"z": zb, "r": rb, "theta": tb}, "n_vertices": int(kv.sum()),
                           "n_faces": int(k.sum()), "area_mm2": rnd(mesh.area_faces[k].sum())}
    if k.sum() == 0:
        return res
    z = c[k, 2]
    res["z_p50"], res["z_p99"], res["z_max"] = rnd(np.percentile(z, 50)), rnd(np.percentile(z, 99)), rnd(z.max())
    # connected pieces inside the box: one coherent body vs scattered speckle
    fidx = np.where(k)[0]
    lab = face_components(mesh, fidx)
    areas = sorted(np.bincount(lab, weights=mesh.area_faces[fidx]).tolist(), reverse=True)
    res["components"] = len(areas)
    res["largest_component_area_fraction"] = rnd(areas[0] / sum(areas), 4) if areas else None
    if top_band is not None:
        up = k & (mesh.face_normals[:, 2] > 0) & (c[:, 2] >= z.max() - top_band)
        if up.sum() >= 3:
            f = plane_svd(c[up])
            res["top_plane"] = {"n_faces": int(up.sum()), "tilt_from_z_deg": f["tilt_from_z_deg"],
                                "z": f["centroid"][2], "residual": f["residual"]}
    return res


def _png(path: Path, H: np.ndarray, xe: np.ndarray, ye: np.ndarray, xl: str, yl: str, title: str) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    fig, ax = plt.subplots(figsize=(12, 6), dpi=110)
    Hm = np.ma.masked_where(H.T <= 0, np.log10(np.where(H.T > 0, H.T, 1)))
    ax.pcolormesh(xe, ye, Hm, cmap="magma")
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title); ax.grid(True, lw=0.3, alpha=0.4)
    fig.savefig(path); plt.close(fig)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["planar", "radial", "maps", "rtheta", "cluster"])
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--alignment", help="alignment.json raw->datum (omit if the mesh is in the datum frame)")
    ap.add_argument("--z", help="planar/rtheta: comma list of z stations")
    ap.add_argument("--nz", type=int, help="planar: N evenly spaced stations inside the z extent (DRM used 25)")
    ap.add_argument("--thetas", help="radial: comma list of azimuths, deg")
    ap.add_argument("--min-loop-area", type=float, default=0.3, help="planar: drop closed loops smaller than this, mm^2 (DRM align.py: 0.3)")
    ap.add_argument("--match-tol", type=float, default=None, help="planar: max centroid jump to continue a loop track, mm (default: unlimited)")
    ap.add_argument("--r-band", help="rtheta/cluster: rlo,rhi")
    ap.add_argument("--z-band", help="cluster: zlo,zhi")
    ap.add_argument("--theta-band", help="cluster: thlo,thhi deg")
    ap.add_argument("--top-band", type=float, help="cluster: fit a plane to up-facing faces within this distance of the cluster's top, mm")
    ap.add_argument("--dtheta", type=float, default=0.25); ap.add_argument("--half-window", type=float, default=0.3)
    ap.add_argument("--bins", default="600,300,720,300", help="maps: rz_r,rz_z,theta,r (DRM align.py used 600x300 and 720x300)")
    ap.add_argument("--out", required=True, help="output .json (a sibling .npz holds arrays)")
    a = ap.parse_args()

    m = load_mesh(a.mesh, load_alignment(a.alignment))
    out = header(f"sections_{a.mode}.json", "sections.py", [p for p in (a.mesh, a.alignment) if p])
    out["frame"] = "datum; z along +Z, theta CCW about +Z from +X"
    npz = Path(a.out).with_suffix(".npz")
    arrays: dict[str, np.ndarray] = {}
    if a.mode == "planar":
        if a.z:
            zs = [float(v) for v in a.z.split(",")]
        else:
            z0, z1 = m.bounds[0][2], m.bounds[1][2]
            n = a.nz or 25
            pad = (z1 - z0) / (2 * n)
            zs = [float(v) for v in np.linspace(z0 + pad, z1 - pad, n)]
        st = planar(m, zs, a.min_loop_area)
        out["stations"] = st
        out["tracks"] = match_tracks(st, a.match_tol)
        print(f"{len(zs)} stations, {sum(len(s['loops']) for s in st)} loops, {len(out['tracks'])} tracks")
    elif a.mode == "radial":
        ths = [float(v) for v in a.thetas.split(",")]
        rs = radial(m, ths)
        out["planes"] = {k: {"chunks": len(v), "r_range": [rnd(min(c[:, 0].min() for c in v)), rnd(max(c[:, 0].max() for c in v))] if v else None,
                             "z_range": [rnd(min(c[:, 1].min() for c in v)), rnd(max(c[:, 1].max() for c in v))] if v else None}
                         for k, v in rs.items()}
        for k, v in rs.items():
            for i, c in enumerate(v):
                arrays[f"{k}_{i}"] = c
        empty = [k for k, v in rs.items() if not v]
        if empty:
            print(f"WARNING: empty half-planes {empty} (CHK-OVERLAY-style: a panel with no scan trace proves nothing)")
    elif a.mode == "maps":
        b = [int(v) for v in a.bins.split(",")]
        mp = maps(m, (b[0], b[1]), (b[2], b[3]))
        arrays.update(mp)
        pngs = []
        base = Path(a.out).with_suffix("")
        if _png(Path(f"{base}_rz.png"), mp["rz"], mp["rz_r_edges"], mp["rz_z_edges"], "r (mm)", "z (mm)", "(r,z) area density, all azimuths"):
            pngs.append(f"{base}_rz.png")
        if _png(Path(f"{base}_theta_r.png"), mp["thr"], mp["thr_theta_edges"], mp["thr_r_edges"], "theta (deg)", "r (mm)", "(theta,r) area density"):
            pngs.append(f"{base}_theta_r.png")
        out["pngs"] = pngs or "matplotlib not installed: arrays only (.npz)"
    elif a.mode == "cluster":
        out["cluster"] = cluster(m, a.z_band, a.r_band, a.theta_band, a.top_band)
        print(out["cluster"])
    else:
        zs = [float(v) for v in a.z.split(",")]
        prof = []
        for z in zs:
            polys = [densify(p[:, :2]) for p in section_polylines(m, [0, 0, z], [0, 0, 1])]
            if not polys:
                prof.append({"z": z, "error": "no section"})
                continue
            pts = np.vstack(polys)
            if a.r_band:
                lo, hi = (float(v) for v in a.r_band.split(","))
                r = np.hypot(pts[:, 0], pts[:, 1])
                pts = pts[(r >= lo) & (r <= hi)]
            TH, R, _ = outer_envelope(pts, a.dtheta, a.half_window)
            arrays[f"z{z:g}_theta"] = TH
            arrays[f"z{z:g}_Rout"] = R
            i0, i1 = int(np.nanargmin(R)), int(np.nanargmax(R))
            prof.append({"z": z, "coverage": rnd(np.isfinite(R).mean(), 4), "gaps_deg": gaps(TH, R, a.dtheta),
                         "R_min": rnd(R[i0]), "theta_at_R_min": rnd(TH[i0], 3),
                         "R_max": rnd(R[i1]), "theta_at_R_max": rnd(TH[i1], 3)})
        out["profiles"] = prof
    if arrays:
        np.savez_compressed(npz, **arrays)
        out["arrays"] = str(npz)
    write_json(a.out, out)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
