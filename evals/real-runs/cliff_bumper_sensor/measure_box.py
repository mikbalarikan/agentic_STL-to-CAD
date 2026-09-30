#!/usr/bin/env python3
"""measure_box.py - scan measurements for the cliff bumper sensor housing (prismatic part).

The stl-re-measure-intent scripts target turned/lobed parts (sections about +Z, R(theta),
pattern counts). This part is a moulded box with no round feature, so each dimension here is a
plane or 2-D circle fit on a named region of the datum-aligned scan. Every region is a box in
the frozen datum frame (intake/alignment.json) plus a face-normal filter; every fit reports its
point count and residual. Output: measure/figures/measurements.json (+ section PNGs).

Estimators
  plane_coord : faces whose normal is within `cone` deg of +/-axis inside the box; offset =
                area-weighted median of the face-centre coordinate after a 2-sigma trim; the
                residual rms about that median is reported (the plane is datum-aligned by
                construction, so tilt shows up as rms; `plane_fit` reports the free tilt too).
  plane_fit   : SVD plane through the trimmed face centres (free orientation) -> normal, the
                coordinate at a stated point, angle to the datum axes, rms/max.
  corner_R    : Kasa circle through section points of a rounded edge, taken on several
                stations; median R and centre, spread across stations.
Deterministic: no random sampling (seed not used).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh

RUN = Path(__file__).resolve().parents[1]
MESH = RUN / "intake" / "aligned_work.stl"
OUT = RUN / "measure" / "figures"
AX = {"x": 0, "y": 1, "z": 2}


def sha(p: Path) -> str:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()


m = trimesh.load_mesh(MESH, process=True)
C, N, A = m.triangles_center, m.face_normals, m.area_faces


def sel(box, normal=None, cone=15.0):
    s = np.ones(len(C), bool)
    for k, (lo, hi) in box.items():
        s &= (C[:, AX[k]] >= lo) & (C[:, AX[k]] <= hi)
    if normal is not None:
        n = np.asarray(normal, float)
        n /= np.linalg.norm(n)
        s &= N @ n > math.cos(math.radians(cone))
    return s


def wmedian(v, w):
    o = np.argsort(v)
    cw = np.cumsum(w[o])
    return float(v[o][np.searchsorted(cw, cw[-1] / 2)])


def plane_coord(name, axis, sign, box, cone=15.0, excl=None):
    n = np.zeros(3)
    n[AX[axis]] = sign
    s = sel(box, n, cone)
    if excl:
        for b in excl:
            s &= ~sel(b)
    v, w = C[s, AX[axis]], A[s]
    if len(v) < 10:
        raise SystemExit(f"{name}: only {len(v)} faces in region")
    med = wmedian(v, w)
    sd = float(np.sqrt(np.average((v - med) ** 2, weights=w)))
    k = np.abs(v - med) <= max(2 * sd, 0.05)
    med = wmedian(v[k], w[k])
    r = v[k] - med
    return {"value": med, "n_faces": int(k.sum()), "area_mm2": float(w[k].sum()),
            "rms": float(np.sqrt(np.average(r ** 2, weights=w[k]))), "p95_abs": float(np.percentile(np.abs(r), 95)),
            "estimator": f"area-weighted median {axis} of faces with normal within {cone} deg of "
                         f"{'+' if sign > 0 else '-'}{axis}, region {box}, 2-sigma trim"
                         + (f", excluding {excl}" if excl else "")}


def plane_fit(name, normal, box, at, cone=15.0, excl=None):
    s = sel(box, normal, cone)
    if excl:
        for b in excl:
            s &= ~sel(b)
    P, w = C[s], A[s]
    if len(P) < 10:
        raise SystemExit(f"{name}: only {len(P)} faces in region")
    keep = np.ones(len(P), bool)
    for _ in range(4):
        c0 = np.average(P[keep], axis=0, weights=w[keep])
        _, _, vt = np.linalg.svd((P[keep] - c0) * np.sqrt(w[keep])[:, None], full_matrices=False)
        nn = vt[2] if vt[2] @ np.asarray(normal) > 0 else -vt[2]
        d = (P - c0) @ nn
        sd = np.sqrt(np.average(d[keep] ** 2, weights=w[keep]))
        keep = np.abs(d) <= max(2.5 * sd, 0.05)
    d = (P[keep] - c0) @ nn
    # coordinate along the dominant axis at the stated point
    ax = int(np.argmax(np.abs(nn)))
    pt = np.array(at, float)
    # solve nn . (p - c0) = 0 for p[ax]
    others = [i for i in range(3) if i != ax]
    val = c0[ax] - sum(nn[i] * (pt[i] - c0[i]) for i in others) / nn[ax]
    return {"normal": nn.tolist(), "centroid": c0.tolist(), "coord_at_point": float(val),
            "point": at, "axis": "xyz"[ax], "n_faces": int(keep.sum()),
            "rms": float(np.sqrt(np.average(d ** 2, weights=w[keep]))), "max_abs": float(np.abs(d).max()),
            "angle_to_axes_deg": {k: math.degrees(math.acos(min(1, abs(nn[i])))) for k, i in AX.items()},
            "estimator": f"SVD plane (iterative 2.5-sigma trim) on faces with normal within {cone} deg of "
                         f"{np.round(normal, 3).tolist()}, region {box}" + (f", excluding {excl}" if excl else "")}


def kasa(xy):
    x, y = xy[:, 0], xy[:, 1]
    Am = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    (cx, cy, c), *_ = np.linalg.lstsq(Am, b, rcond=None)
    r = math.sqrt(c + cx ** 2 + cy ** 2)
    res = np.hypot(x - cx, y - cy) - r
    return cx, cy, r, float(np.sqrt(np.mean(res ** 2))), float(np.abs(res).max())


def section_pts(axis, val):
    nrm = np.zeros(3)
    nrm[AX[axis]] = 1
    seg = trimesh.intersections.mesh_plane(m, nrm, nrm * val)
    return seg.reshape(-1, 3)


def corner_R(name, axis, stations, u, v, window, centre_guess=None):
    """window = (ulo, uhi, vlo, vhi) in the section plane coords (u, v)."""
    rows = []
    for s in stations:
        P = section_pts(axis, s)
        uu, vv = P[:, AX[u]], P[:, AX[v]]
        k = (uu >= window[0]) & (uu <= window[1]) & (vv >= window[2]) & (vv <= window[3])
        if k.sum() < 8:
            continue
        pts = np.c_[uu[k], vv[k]]
        if centre_guess is not None:
            # outer envelope only: per 4-deg bin about the guess keep the farthest point, so
            # material seen through a transparent wall or a local dent does not bias the arc
            d = pts - np.asarray(centre_guess, float)
            ang = np.degrees(np.arctan2(d[:, 1], d[:, 0]))
            rr = np.hypot(d[:, 0], d[:, 1])
            b = np.floor(ang / 4.0).astype(int)
            keep = [np.where(b == bb)[0][np.argmax(rr[b == bb])] for bb in np.unique(b)]
            pts = pts[keep]
            if len(pts) < 5:
                continue
        cx, cy, r, rms, mx = kasa(pts)
        rows.append({"station": s, "cu": cx, "cv": cy, "R": r, "rms": rms, "max": mx, "n": int(len(pts))})
    if not rows:
        raise SystemExit(f"{name}: no station had points in the window")
    R = [r["R"] for r in rows]
    return {"value": float(np.median(R)), "per_station": rows, "spread": float(np.ptp(R)),
            "cu_median": float(np.median([r["cu"] for r in rows])), "cv_median": float(np.median([r["cv"] for r in rows])),
            "estimator": f"Kasa circle on {axis}-section points in window {u}[{window[0]},{window[1]}] "
                         f"{v}[{window[2]},{window[3]}] at {axis}={stations}; median R"
                         + (f"; outer envelope (farthest point per 4-deg bin about {centre_guess})" if centre_guess is not None else "")}


def extreme(name, axis, which, box, q=None):
    s = sel(box)
    v = m.vertices
    vs = v[(v[:, 0] >= box.get("x", (-1e9, 1e9))[0]) & (v[:, 0] <= box.get("x", (-1e9, 1e9))[1])
           & (v[:, 1] >= box.get("y", (-1e9, 1e9))[0]) & (v[:, 1] <= box.get("y", (-1e9, 1e9))[1])
           & (v[:, 2] >= box.get("z", (-1e9, 1e9))[0]) & (v[:, 2] <= box.get("z", (-1e9, 1e9))[1])]
    col = vs[:, AX[axis]]
    if len(col) == 0:
        return {"value": None, "n_vertices": 0, "estimator": f"no vertices in region {box}"}
    qq = q if q is not None else (99.5 if which == "max" else 0.5)
    return {"value": float(np.percentile(col, qq)), "n_vertices": int(len(col)),
            "estimator": f"p{qq} of vertex {axis} in region {box}"}


R = {}
# ---------------------------------------------------------------- main body (clear cover)
R["body_y_pos"] = plane_coord("body_y_pos", "y", +1, {"x": (-20.8, -15.5), "z": (-8.0, -1.8)})
R["body_y_neg"] = plane_coord("body_y_neg", "y", -1, {"x": (-20.8, -15.5), "z": (-8.0, -1.8)})
R["body_y_pos_behind_tab"] = plane_coord("b", "y", +1, {"x": (-14.0, -7.0), "z": (-4.0, -1.8)})
R["body_y_neg_behind_tab"] = plane_coord("b", "y", -1, {"x": (-14.0, -7.0), "z": (-4.0, -1.8)})
R["body_y_pos_below_tab"] = plane_coord("b", "y", +1, {"x": (-14.0, -2.0), "z": (-8.3, -6.9)})
R["body_y_neg_below_tab"] = plane_coord("b", "y", -1, {"x": (-14.0, -2.0), "z": (-8.3, -6.9)})
R["body_bottom_plane"] = plane_fit("body_bottom", [0, 0, -1], {"x": (-14.5, -2.5), "y": (-13.5, 13.5), "z": (-10.5, -8.5)},
                                   at=[0, 0, 0], cone=10,
                                   excl=[{"y": (-2.2, 2.2), "x": (-3, 0)}])
R["body_bottom_z_at_x-20"] = plane_coord("bz20", "z", -1, {"x": (-21.0, -19.5), "y": (-13.0, -5.0), "z": (-10.5, -8.5)}, cone=10)
R["body_bottom_z_at_x-3"] = plane_coord("bz3", "z", -1, {"x": (-4.0, -2.5), "y": (-13.0, -3.0), "z": (-10.5, -8.5)}, cone=10)
R["body_front_x"] = plane_coord("body_front_x", "x", -1, {"x": (-22.2, -20.8), "y": (15.3, 16.2), "z": (-8.0, -1.5)}, cone=20)
R["body_front_x_neg"] = plane_coord("body_front_x_neg", "x", -1, {"x": (-22.2, -20.8), "y": (-16.2, -15.3), "z": (-8.0, -1.5)}, cone=20)
R["cover_top_edge_R"] = corner_R("cover_top_edge_R", "x", [-19, -17, -12.5, -9, -5], "y", "z", (13.3, 16.1, -2.4, 0.2), (13.5, -2.5))
R["cover_top_edge_R_neg"] = corner_R("cover_top_edge_R_neg", "x", [-19, -17, -12.5, -9, -5], "y", "z", (-16.1, -13.3, -2.4, 0.2), (-13.5, -2.5))
R["cover_bot_edge_R"] = corner_R("cover_bot_edge_R", "x", [-19, -17, -12.5, -9, -5, -3], "y", "z", (13.3, 16.2, -9.8, -7.0), (13.5, -7.0))
R["cover_bot_edge_R_neg"] = corner_R("cover_bot_edge_R_neg", "x", [-19, -17, -12.5, -9, -5, -3], "y", "z", (-16.2, -13.3, -9.8, -7.0), (-13.5, -7.0))
# ---------------------------------------------------------------- nose (lens cup)
R["nose_slope_plane"] = plane_fit("nose_slope", [-0.88, 0, 0.47], {"x": (-27.0, -22.9), "y": (-0.6, 0.6), "z": (-8.0, -0.8)},
                                  at=[0, 0, 0], cone=20)
R["nose_slope_plane_windows"] = plane_fit("nose_slope_w", [-0.88, 0, 0.47], {"x": (-27.0, -22.9), "y": (-13.0, 13.0), "z": (-7.5, -0.8)},
                                          at=[0, 0, 0], cone=20)
R["nose_half_width_top_pos"] = plane_coord("nhw", "y", +1, {"x": (-23.0, -21.8), "z": (-2.6, -1.0)}, cone=20)
R["nose_half_width_top_neg"] = plane_coord("nhw", "y", -1, {"x": (-23.0, -21.8), "z": (-2.6, -1.0)}, cone=20)
R["nose_cup_R_pos"] = corner_R("nose_cup_R_pos", "x", [-25.5, -25, -24.5, -24, -23.5, -23, -22.5, -22],
                               "y", "z", (6.0, 15.2, -9.3, -3.0), (6.0, -2.0))
R["nose_cup_R_neg"] = corner_R("nose_cup_R_neg", "x", [-25.5, -25, -24.5, -24, -23.5, -23, -22.5, -22],
                               "y", "z", (-15.2, -6.0, -9.3, -3.0), (-6.0, -2.0))
R["nose_bottom_z"] = plane_coord("nbz", "z", -1, {"x": (-26.0, -22.0), "y": (-6.0, 6.0), "z": (-10, -8.5)}, cone=10)
R["nose_tip_R"] = corner_R("nose_tip_R", "y", [-5, -3, 3, 5], "x", "z", (-27.8, -26.2, -9.3, -7.4))
R["nose_top_edge_x"] = extreme("nose_top_edge_x", "x", "min", {"y": (-10, 10), "z": (-0.25, 0.1)}, q=0.5)
# ---------------------------------------------------------------- seam groove (cover / cap)
R["seam_groove"] = corner_R("seam_groove", "y", [-10, -5, 5, 10], "x", "z", (-1.75, -0.65, -0.45, 0.0))
R["seam_groove_bottom_z"] = extreme("sgz", "z", "min", {"x": (-1.6, -0.8), "y": (-12, 12), "z": (-0.6, 0.1)}, q=1)
# ---------------------------------------------------------------- rear cap (x from seam to 0)
R["cap_y_pos"] = plane_coord("cap_y_pos", "y", +1, {"x": (-0.9, -0.1), "z": (-1.9, -0.8)}, cone=20)
R["cap_y_neg"] = plane_coord("cap_y_neg", "y", -1, {"x": (-0.9, -0.1), "z": (-1.9, -0.8)}, cone=20)
R["cap_y_pos_low"] = plane_coord("cap_y_pos_low", "y", +1, {"x": (-0.9, -0.1), "y": (15.5, 17.2), "z": (-8.3, -7.0)}, cone=20)
R["cap_y_neg_low"] = plane_coord("cap_y_neg_low", "y", -1, {"x": (-0.9, -0.1), "y": (-17.2, -15.5), "z": (-8.3, -7.0)}, cone=20)
R["cap_bottom_z"] = plane_coord("cap_bottom_z", "z", -1, {"x": (-0.9, -0.1), "y": (-13, -3), "z": (-10.5, -8.8)}, cone=10)
R["rear_wall_x"] = plane_coord("rear_wall_x", "x", +1, {"x": (-0.6, 0.6), "y": (-15, 15), "z": (-8.8, -4.0)},
                               excl=[{"y": (-2.5, 2.5)}])
# ---------------------------------------------------------------- connector shelf and pockets
R["shelf_end_x"] = plane_coord("shelf_end_x", "x", +1, {"x": (6.0, 8.0), "y": (-14, 14), "z": (-3.0, -0.8)})
R["shelf_y_pos"] = plane_coord("shelf_y_pos", "y", +1, {"x": (1.0, 6.5), "y": (15.8, 17.2), "z": (-3.2, -1.5)})
R["shelf_y_neg"] = plane_coord("shelf_y_neg", "y", -1, {"x": (1.0, 6.5), "y": (-17.2, -15.8), "z": (-3.2, -1.5)})
R["shelf_bottom_z"] = plane_coord("shelf_bottom_z", "z", -1, {"x": (5.9, 6.9), "y": (-15, 15), "z": (-4.2, -3.2)}, cone=20)
R["shelf_top_z"] = plane_coord("shelf_top_z", "z", +1, {"x": (0.5, 6.5), "y": (-14, 14), "z": (-0.6, 0.3)}, cone=10)
R["shelf_top_edge_R"] = corner_R("shelf_top_edge_R", "x", [2, 3, 4, 5, 6], "y", "z", (14.0, 16.6, -2.0, 0.2), (14.5, -2.0))
R["shelf_top_edge_R_neg"] = corner_R("shelf_top_edge_R_neg", "x", [2, 3, 4, 5, 6], "y", "z", (-16.6, -14.0, -2.0, 0.2), (-14.5, -2.0))
R["pocket_ceiling_z"] = plane_coord("pocket_ceiling_z", "z", -1, {"x": (1.6, 5.0), "y": (-15, 15), "z": (-2.0, -0.8)}, cone=15)
R["pocket_x_front"] = plane_coord("pocket_x_front", "x", +1, {"x": (0.6, 1.8), "y": (-15, 15), "z": (-3.2, -1.7)}, cone=20)
R["pocket_x_back"] = plane_coord("pocket_x_back", "x", -1, {"x": (4.8, 6.2), "y": (-15, 15), "z": (-3.0, -1.7)}, cone=20)
R["pocket_lip_front_z"] = plane_coord("plfz", "z", -1, {"x": (0.1, 0.9), "y": (-15, 15), "z": (-4.0, -3.0)}, cone=20)
for i, (lo, hi, side) in enumerate([(-16.2, -14.8, -1), (-7.0, -5.4, +1), (-5.6, -4.2, -1), (4.0, 5.3, +1), (5.2, 6.8, -1), (14.8, 16.2, +1)]):
    # pocket side walls: faces looking INTO the pocket (normal toward the pocket interior)
    R[f"pocket_wall_{i}"] = plane_coord(f"pocket_wall_{i}", "y", -side, {"x": (1.8, 4.8), "y": (lo, hi), "z": (-3.2, -1.7)}, cone=20)
# ---------------------------------------------------------------- side rails and tabs
for sgn, tag in ((+1, "pos"), (-1, "neg")):
    ylo, yhi = (17.0, 18.2) if sgn > 0 else (-18.2, -17.0)
    tlo, thi = (18.4, 19.8) if sgn > 0 else (-19.8, -18.4)
    R[f"rail_y_{tag}"] = plane_coord("rail_y", "y", sgn, {"x": (-5.5, -1.5), "y": (ylo, yhi), "z": (-4.2, -3.4)}, cone=20)
    R[f"rail_x_start_{tag}"] = plane_coord("rail_x", "x", -1, {"x": (-7.2, -5.6), "y": tuple(sorted((sgn * 16.3, sgn * 17.4))), "z": (-4.2, -3.4)}, cone=30)
    R[f"rail_top_z_{tag}"] = plane_coord("rail_top", "z", +1, {"x": (-5.5, -1.8), "y": tuple(sorted((sgn * 16.4, sgn * 17.4))), "z": (-3.6, -2.7)}, cone=20)
    R[f"rail_rear_top_z_{tag}"] = plane_coord("rail_rear_top", "z", +1, {"x": (-0.7, -0.15), "y": tuple(sorted((sgn * 16.8, sgn * 17.4))), "z": (-2.8, -1.9)}, cone=25)
    R[f"rail_rear_x_start_{tag}"] = plane_coord("rail_rear_x", "x", -1, {"x": (-1.4, -0.4), "y": tuple(sorted((sgn * 16.6, sgn * 17.5))), "z": (-2.9, -2.4)}, cone=35)
    R[f"tab_y_{tag}"] = plane_coord("tab_y", "y", sgn, {"x": (-14, -2.5), "y": (tlo, thi), "z": (-6.2, -4.8)}, cone=20)
    R[f"tab_top_z_{tag}"] = plane_coord("tab_top", "z", +1, {"x": (-14, -9), "y": tuple(sorted((sgn * 17.2, sgn * 18.8))), "z": (-5.0, -4.2)}, cone=15)
    R[f"tab_bot_z_{tag}"] = plane_coord("tab_bot", "z", -1, {"x": (-14, -2), "y": tuple(sorted((sgn * 16.8, sgn * 18.8))), "z": (-6.8, -6.0)}, cone=15)
    R[f"tab_x_start_{tag}"] = plane_coord("tab_x0", "x", -1, {"x": (-15.6, -14.2), "y": tuple(sorted((sgn * 16.8, sgn * 18.8))), "z": (-6.1, -4.9)}, cone=20)
    R[f"tab_x_end_{tag}"] = plane_coord("tab_x1", "x", +1, {"x": (-2.0, -0.8), "y": tuple(sorted((sgn * 18.0, sgn * 19.0))), "z": (-6.1, -4.9)}, cone=25)
    R[f"nub_top_z_{tag}"] = extreme("nub", "z", "max", {"x": (-8.6, -6.6), "y": tuple(sorted((sgn * 17.8, sgn * 19.2))), "z": (-4.5, -3.3)}, q=97)
    R[f"nub_x_{tag}"] = {"value": [extreme("nubx0", "x", "min", {"x": (-9.0, -6.0), "y": tuple(sorted((sgn * 17.8, sgn * 19.2))), "z": (-4.3, -3.6)}, q=1)["value"],
                                   extreme("nubx1", "x", "max", {"x": (-9.0, -6.0), "y": tuple(sorted((sgn * 17.8, sgn * 19.2))), "z": (-4.3, -3.6)}, q=99)["value"]],
                         "estimator": "p1 / p99 vertex x of the nub above the tab top (z -4.3..-3.6)"}
# ---------------------------------------------------------------- bottom slot (rear centre)
R["slot_y_pos"] = plane_coord("slot_y_pos", "y", -1, {"x": (-1.2, -0.2), "y": (0.8, 2.0), "z": (-9.0, -7.2)}, cone=25)
R["slot_y_neg"] = plane_coord("slot_y_neg", "y", +1, {"x": (-1.2, -0.2), "y": (-2.0, -0.8), "z": (-9.0, -7.2)}, cone=25)
R["slot_top_z"] = extreme("slot_top_z", "z", "max", {"x": (-0.8, -0.1), "y": (-1.8, 1.8), "z": (-9.0, -5.0)}, q=99)  # highest scanned slot-wall point: the slot roof is not in the scan
R["slot_x_end"] = extreme("slot_x_end", "x", "min", {"y": (-0.8, 0.8), "z": (-9.3, -8.9), "x": (-3.0, 0.2)}, q=0)
# ---------------------------------------------------------------- bottom ramps (two wedges under the cover, near the nose)
for sgn, tag in ((+1, "pos"), (-1, "neg")):
    yb = tuple(sorted((sgn * 1.7, sgn * 4.3)))
    R[f"ramp_peak_z_{tag}"] = extreme("ramp", "z", "min", {"x": (-15.8, -15.0), "y": yb, "z": (-10.5, -9.2)}, q=3)
    R[f"ramp_x_end_{tag}"] = plane_coord("ramp_x_end", "x", +1, {"x": (-15.6, -14.6), "y": yb, "z": (-9.9, -9.35)}, cone=40)
    # wedge width: vertices at least 0.2 mm below the local bottom face (bottom there ~ -9.25),
    # two stations near the tall end; p1/p99 of |y|
    for st in (-17.0, -16.0):
        vv = m.vertices
        k = (np.abs(vv[:, 0] - st) < 0.25) & (vv[:, 2] < -9.45) & (sgn * vv[:, 1] > 0.8) & (sgn * vv[:, 1] < 5.5)
        ay = np.abs(vv[k, 1])
        R[f"ramp_y_span_{tag}_x{st}"] = {"value": [float(np.percentile(ay, 1)), float(np.percentile(ay, 99))], "n_vertices": int(k.sum()),
                                           "estimator": f"p1/p99 |y| of vertices with z < -9.45 at x={st}+-0.25, {tag} side"}
    R[f"ramp_x_start_{tag}"] = extreme("ramp_x0", "x", "min", {"x": (-22, -15), "y": tuple(sorted((sgn * 2.3, sgn * 3.6))), "z": (-10.5, -9.28)}, q=1)

# ---------------------------------------------------------------- nose windows (recessed, transparent)
# coordinates in the rib/frame plane (nose_slope_plane): d = signed distance along its outward
# normal (0 = frame and centre rib face), s = in-plane distance up the slope, y = datum y.
_np = R["nose_slope_plane"]
_n, _c0 = np.array(_np["normal"]), np.array(_np["centroid"])
_s = np.cross(_n, [0, 1, 0]); _s /= np.linalg.norm(_s); _s = _s if _s[2] > 0 else -_s
_k = (C[:, 0] < -22.0) & (C[:, 2] > -9.6) & (N @ _n > 0.8)
_d, _ss, _y = (C[_k] - _c0) @ _n, (C[_k] - _c0) @ _s, C[_k][:, 1]
_kw = (_d < -0.55) & (_d > -1.1)
R["window_depth"] = {"value": float(-wmedian(_d[_kw], A[_k][_kw])), "n_faces": int(_kw.sum()),
                     "rms": float(np.std(_d[_kw])),
                     "estimator": "area-weighted median depth below the frame/rib plane of outward-facing nose faces with "
                                  "-1.1 < d < -0.55 (histogram peak; deeper hits are interior seen through the clear window)"}
for sgn, tag in ((+1, "pos"), (-1, "neg")):
    kk = _kw & (sgn * _y > 0)
    R[f"window_y_{tag}"] = {"value": [float(np.percentile(np.abs(_y[kk]), 1)), float(np.percentile(np.abs(_y[kk]), 99))],
                            "n_faces": int(kk.sum()), "estimator": f"p1/p99 |y| of recessed window faces, {tag} side"}
R["window_s"] = {"value": [float(np.percentile(_ss[_kw], 1)), float(np.percentile(_ss[_kw], 99))], "n_faces": int(_kw.sum()),
                 "estimator": "p1/p99 of in-plane slope coordinate s of recessed window faces (s=0 at the plane-fit centroid, +s up)"}
R["frame_s"] = {"value": [float(np.percentile(_ss[_d > -0.35], 0.5)), float(np.percentile(_ss[_d > -0.35], 99.5))],
                "estimator": "p0.5/p99.5 of s of frame/rib faces (d > -0.35)"}
R["cap_top_edge_R"] = corner_R("cap_top_edge_R", "x", [-0.7, -0.5, -0.3], "y", "z", (14.0, 16.6, -2.1, 0.2), (14.3, -2.0))
R["cap_top_edge_R_neg"] = corner_R("cap_top_edge_R_neg", "x", [-0.7, -0.5, -0.3], "y", "z", (-16.6, -14.0, -2.1, 0.2), (-14.3, -2.0))

doc = {"schema": "stl-re/measurements@1", "tool": "measure_box.py", "tool_version": "run-local@1",
       "inputs": {str(MESH.relative_to(RUN)): sha(MESH)}, "seed": 0,
       "frame": "datum frame of intake/alignment.json", "results": R}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "measurements.json").write_text(json.dumps(doc, indent=1))
for k, v in R.items():
    if "value" in v and v["value"] is None:
        print(f"{k:28s} NONE ({v['estimator']})")
    elif "value" in v:
        extra = f"rms {v['rms']:.3f} n {v['n_faces']}" if "rms" in v and "n_faces" in v else (
            f"spread {v['spread']:.2f} c=({v['cu_median']:.2f},{v['cv_median']:.2f})" if "spread" in v else "")
        val = v["value"] if isinstance(v["value"], list) else round(v["value"], 3)
        print(f"{k:28s} {val}  {extra}")
    else:
        print(f"{k:28s} coord@pt {v['coord_at_point']:.3f} n {np.round(v['normal'], 4).tolist()} ang {({a: round(b, 2) for a, b in v['angle_to_axes_deg'].items()})} rms {v['rms']:.3f}")
