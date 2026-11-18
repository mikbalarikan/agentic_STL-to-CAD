#!/usr/bin/env python3
"""align.py - build the raw-scan -> datum transform from a JSON spec, measure tilt,
check fit residuals against the measured noise floor, write intake/alignment.json
(run-contract section 3) and intake/aligned_work.stl.

PROVENANCE
  Lifted from golden-examples/dreame_brush-caps/report/source/align.py (__main__:
  level on a plane near an approximate normal, origin = median centre of Kasa circle
  fits on Z sections filtered by radius hint / rms / z window, clock modes `pent@z`
  and `flatmin@z`, T = Rz T3 T2 T1). Changed:
    * positional CLI replaced by a JSON spec (primary / origin / clock / landmarks);
    * tilt is MEASURED from the circle-centre drift along Z (golden hard-coded
      tilt_deg = 0.0 at align.py:79 -> CHK-TILT, SYNTHESIS B5);
    * the silent bbox-centre fallback (align.py:82) is removed: no origin -> exit 3;
    * axis-primary parts (OD-H12, P03 class) via normals-eigen axis (datum_fit.py);
    * IRLS Cauchy circle option (B02 qa/q03_datum_full.py:98-111);
    * n-fold Fourier-mass clock (B02 q03_datum_full.py:117-121) and plane-normal clock
      (OD-H12 README.md:14 "X = side-plate normal");
    * STOP when a datum fit rms exceeds the measured noise floor (RE_SPEC.md:126-129);
    * sanity landmarks (SYNTHESIS B11, facet-film T3);
    * plotting removed (use the measure skill's section tools);
    * shapely dependency removed (shoelace area).

Exit codes: 0 OK, 2 STOP (fit residual > noise floor; alignment.json written with
status STOP), 3 spec/geometry error (nothing trustworthy written).
Deterministic: seeded RANSAC (spec "seed", default 0); no clock value in computation.

Blind spots: does not decide which surface is functional (you do, from photos and
function), does not detect a wrong but well-fitting feature (check the landmarks and a
section plot), and is not an independent audit (the verify skill re-derives the datum
with its own code).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datum_fit import (axis_from_normals, closed_loops_at_z, fit_circle, fit_circle_irls, json_header,  # noqa: E402
                       level_plane, polygon_area, section_polylines, sha256_file, unit)


class SpecError(RuntimeError):
    pass


def rot_z(deg: float) -> np.ndarray:
    return trimesh.transformations.rotation_matrix(math.radians(deg), [0, 0, 1])


def apply(T: np.ndarray, m: trimesh.Trimesh) -> trimesh.Trimesh:
    m2 = m.copy()
    m2.apply_transform(T)
    return m2


def ang_between(a: np.ndarray, b: np.ndarray) -> float:
    return math.degrees(math.acos(float(np.clip(abs(unit(a) @ unit(b)), -1, 1))))


# ----------------------------------------------------------------------------- origin / tilt
def circle_stations(m: trimesh.Trimesh, spec: dict[str, Any]) -> list[dict[str, float]]:
    """Circle fits on Z sections of the (levelled) mesh; filter per golden align.py:72-76."""
    lo, hi = spec["z_range"]
    n = int(spec.get("stations", 25))          # golden used 25 stations (align.py:56)
    zs = np.linspace(lo, hi, n)
    out = []
    allow_open = bool(spec.get("allow_open_arcs", False))
    for z in zs:
        if allow_open:
            # partial coverage (occluded wall): fit arcs too; min 8 points as for loops
            curves = [p[:, :2] for p, _c in section_polylines(m, [0, 0, float(z)], [0, 0, 1]) if len(p) >= 8]
        else:
            curves = [xy for xy in closed_loops_at_z(m, float(z))
                      if polygon_area(xy) >= spec.get("min_loop_area", 0.0)]
        for xy in curves:
            c = fit_circle(xy, spec.get("method", "kasa"), spec.get("irls_scale", 0.30))
            if abs(c["r"] - spec["r_hint"]) < spec["r_tol"] and c["rms"] < spec["rms_max"]:
                out.append({"z": float(z), **c})
    return out


def wall_face_stations(m: trimesh.Trimesh, spec: dict[str, Any], c0: np.ndarray) -> list[dict[str, float]]:
    """Axis position from the FACES of a cylindrical wall (B02 q03_datum_full.py:78-111):
    faces with |n.z| < perp_max in z_range and r < r_max about a provisional centre c0,
    inner/outer wall separated by the sign of n.r_hat (outward normals: inner bore wall
    points to the axis), area-weighted IRLS circle per z slab. Robust to partial angular
    coverage (occluded wall) where section loops do not close."""
    C, N, A = m.triangles_center, m.face_normals, m.area_faces
    lo, hi = spec["z_range"]
    q = C[:, :2] - c0
    r = np.hypot(q[:, 0], q[:, 1])
    rhat = q / np.maximum(r, 1e-9)[:, None]
    ndr = (N[:, :2] * rhat).sum(1)
    sel = (np.abs(N[:, 2]) < spec.get("perp_max", 0.30)) & (C[:, 2] > lo) & (C[:, 2] < hi)
    sel &= (r < spec["r_max"]) & (r > spec.get("r_min", 0.0))
    sel &= (ndr < 0) if spec.get("wall", "inner") == "inner" else (ndr > 0)
    if sel.sum() < 8:
        return []
    n = int(spec.get("stations", 5))
    edges = np.linspace(lo, hi, n + 1)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        s = sel & (C[:, 2] >= a) & (C[:, 2] < b)
        if s.sum() < 8:
            continue
        c = fit_circle_irls(C[s, :2], A[s], scale=spec.get("irls_scale", 0.30))
        if abs(c["r"] - spec["r_hint"]) < spec["r_tol"] and c["rms"] < spec["rms_max"]:
            out.append({"z": float(0.5 * (a + b)), **c})
    return out


def _line_tilt(zs: np.ndarray, cx: np.ndarray, cy: np.ndarray) -> dict[str, float]:
    """Least-squares line cx = a + b z, cy = c + d z, with a 1-sigma standard error from the
    residual scatter. Shared by the pooled and the per-feature fits."""
    A = np.c_[np.ones(len(zs)), zs]
    (ax_, bx), *_ = np.linalg.lstsq(A, cx, rcond=None)
    (ay_, by), *_ = np.linalg.lstsq(A, cy, rcond=None)
    sxx = float(((zs - zs.mean()) ** 2).sum())
    dof = max(len(zs) - 2, 1)
    rx = cx - (ax_ + bx * zs)
    ry = cy - (ay_ + by * zs)
    se = math.sqrt(((rx ** 2).sum() + (ry ** 2).sum()) / (2 * dof) / max(sxx, 1e-12))
    return {"value": float(math.degrees(math.atan(math.hypot(bx, by)))),
            "stderr_deg": float(math.degrees(math.atan(se))),
            "direction_deg": float(math.degrees(math.atan2(by, bx))),
            "z_span_mm": float(zs.max() - zs.min())}


def tilt_from_stations(st: list[dict[str, float]]) -> dict[str, Any]:
    """Tilt of the axis through circle centres relative to frame Z.

    review M2: pooling every station into ONE line with one shared intercept reads
    between-feature centre bias (a genuine offset, or shape error on a non-circular
    feature) as tilt. The pooled fit here instead uses a COMMON slope with a
    PER-FEATURE intercept (design matrix = one-hot(feature) | z), so a constant
    per-feature offset is absorbed into that feature's intercept, not into the slope.
    Each feature with >= 3 of its own stations is ALSO fit independently
    (`per_feature`), and `resolvable` is set False - the CHK-TILT note says
    "not resolvable" - when two per-feature tilt vectors differ by more than their
    combined 1-sigma stderr (a heuristic disagreement test, not a calibrated one).
    Needs >= 3 distinct stations overall; else not measured (CHK-TILT finding)."""
    zs_all = np.array([s["z"] for s in st])
    nz = len(np.unique(zs_all.round(6)))
    if nz < 3:
        return {"value": None, "method": f"not measured: {nz} distinct stations (<3)",
                "per_feature": [], "resolvable": None}
    feats = sorted({s.get("feature", "") for s in st})
    fidx = {f: i for i, f in enumerate(feats)}
    onehot = np.zeros((len(st), len(feats)))
    for i, s in enumerate(st):
        onehot[i, fidx[s.get("feature", "")]] = 1.0
    A = np.c_[onehot, zs_all]
    cx = np.array([s["cx"] for s in st])
    cy = np.array([s["cy"] for s in st])
    solx, *_ = np.linalg.lstsq(A, cx, rcond=None)
    soly, *_ = np.linalg.lstsq(A, cy, rcond=None)
    bx, by = float(solx[-1]), float(soly[-1])
    sxx = float(((zs_all - zs_all.mean()) ** 2).sum())
    dof = max(len(zs_all) - len(feats) - 2, 1)
    rx = cx - A @ solx
    ry = cy - A @ soly
    se = math.sqrt(((rx ** 2).sum() + (ry ** 2).sum()) / (2 * dof) / max(sxx, 1e-12))
    pooled: dict[str, Any] = {
        "value": float(math.degrees(math.atan(math.hypot(bx, by)))),
        "stderr_deg": float(math.degrees(math.atan(se))),
        "direction_deg": float(math.degrees(math.atan2(by, bx))),
        "method": f"common slope, per-feature intercept, {len(st)} stations over "
                  f"{len(feats)} feature(s), z {zs_all.min():.3f}..{zs_all.max():.3f} vs frame Z",
        "z_span_mm": float(zs_all.max() - zs_all.min())}
    # per-feature independent fits (own slope AND intercept), to test agreement
    per_feature: list[dict[str, Any]] = []
    for f in feats:
        rows = [s for s in st if s.get("feature", "") == f]
        zf = np.array([s["z"] for s in rows])
        if len(np.unique(zf.round(6))) < 3:
            continue
        fit = _line_tilt(zf, np.array([s["cx"] for s in rows]), np.array([s["cy"] for s in rows]))
        per_feature.append({"feature": f, "n_stations": len(rows), **fit})
    resolvable: bool | None = None
    disagreement = ""
    if len(per_feature) >= 2:
        resolvable = True
        for i in range(len(per_feature)):
            for j in range(i + 1, len(per_feature)):
                fi, fj = per_feature[i], per_feature[j]
                vi = fi["value"] * np.array([math.cos(math.radians(fi["direction_deg"])),
                                             math.sin(math.radians(fi["direction_deg"]))])
                vj = fj["value"] * np.array([math.cos(math.radians(fj["direction_deg"])),
                                             math.sin(math.radians(fj["direction_deg"]))])
                gap = float(np.linalg.norm(vi - vj))
                combined = fi["stderr_deg"] + fj["stderr_deg"]
                if gap > combined:
                    resolvable = False
                    disagreement = (f"{fi['feature']!r} ({fi['value']:.2f} deg @ "
                                    f"{fi['direction_deg']:.1f} deg) vs {fj['feature']!r} "
                                    f"({fj['value']:.2f} deg @ {fj['direction_deg']:.1f} deg) "
                                    f"differ by {gap:.2f} deg > combined stderr {combined:.2f} deg")
    pooled["per_feature"] = per_feature
    pooled["resolvable"] = resolvable
    if disagreement:
        pooled["disagreement"] = disagreement
        pooled["method"] += "; NOT RESOLVABLE (heuristic): " + disagreement
    return pooled


def refine_axis_sections(m: trimesh.Trimesh, point: np.ndarray, direction: np.ndarray, crop_radius: float,
                         axial: Sequence[float], step: float = 0.5, halfw: float = 0.2,
                         iters: int = 5) -> dict[str, Any]:
    """Axis from section-circle centres (datum-cookbook §1: "axis from section circle fits"):
    slice the cropped VERTICES perpendicular to the current axis every `step` mm (slab
    +/- halfw), Kasa circle per slice (>= 30 points), least-squares line through the centres,
    repeat. Normals-eigen alone is biased on a cone or a partially covered cylinder (OD-S02 run:
    0.44 deg / 0.16 mm off the section-circle axis on the rod taper, residual 0.080 vs 0.022)."""
    p0 = np.asarray(point, float)
    d = unit(direction)
    V = m.vertices
    stations: list[list[float]] = []
    for _ in range(max(1, iters)):
        a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
        u = unit(np.cross(d, a))
        v = np.cross(d, u)
        q = V - p0
        t = q @ d
        x, y = q @ u, q @ v
        keep = (np.hypot(x, y) < crop_radius) & (t >= axial[0]) & (t <= axial[1])
        stations = []
        for z in np.arange(axial[0] + halfw, axial[1] - halfw + 1e-9, step):
            sl = keep & (np.abs(t - z) < halfw)
            if sl.sum() < 30:
                continue
            xy = np.c_[x[sl], y[sl]]
            A = np.c_[2 * xy, np.ones(len(xy))]
            sol = np.linalg.lstsq(A, (xy ** 2).sum(1), rcond=None)[0]
            r = math.sqrt(max(sol[2] + sol[0] ** 2 + sol[1] ** 2, 0.0))
            res = np.hypot(xy[:, 0] - sol[0], xy[:, 1] - sol[1]) - r
            stations.append([float(z), float(sol[0]), float(sol[1]), r, float(np.sqrt((res ** 2).mean()))])
        if len(stations) < 3:
            raise SpecError("refine section_circles: fewer than 3 stations with >= 30 points")
        st = np.array(stations)
        A = np.c_[np.ones(len(st)), st[:, 0]]
        cx = np.linalg.lstsq(A, st[:, 1], rcond=None)[0]
        cy = np.linalg.lstsq(A, st[:, 2], rcond=None)[0]
        p0 = p0 + cx[0] * u + cy[0] * v
        d = unit(d + cx[1] * u + cy[1] * v)
    st = np.array(stations)
    return {"point": p0, "direction": d, "stations": len(st),
            "station_rms_median_mm": float(np.median(st[:, 4])), "station_rms_max_mm": float(st[:, 4].max()),
            "method": f"Kasa circles on vertex slabs every {step} mm (+/-{halfw}), line through centres, "
                      f"{iters} iterations"}


# ----------------------------------------------------------------------------- clock
def largest_loop(m: trimesh.Trimesh, z: float) -> np.ndarray:
    loops = closed_loops_at_z(m, z)
    if not loops:
        raise SpecError(f"clock: no closed section loop at z={z}")
    return max(loops, key=polygon_area)


def clock_angle(m: trimesh.Trimesh, R_cur: np.ndarray, c: dict[str, Any], seed: int) -> tuple[float, dict[str, Any]]:
    """Returns the rotation about Z (deg) that brings the named feature to +X, and details."""
    rule = c["rule"]
    if rule == "none":
        if not c.get("why"):
            raise SpecError("clock rule 'none' needs a 'why' (only fully axisymmetric parts)")
        return 0.0, {"note": "no clocking feature; rotation about Z is arbitrary"}
    if rule in ("polygon_flat", "polygon_corner"):
        # dreame align.py:99-104 (5-fold r-peak phase), generalised to n
        n = int(c["n"])
        xy = largest_loop(m, float(c["z"]))
        r = np.hypot(xy[:, 0], xy[:, 1])
        th = np.degrees(np.arctan2(xy[:, 1], xy[:, 0]))
        w = np.clip(r - np.median(r), 0, None)
        f = np.radians(th * n)
        corner = math.degrees(math.atan2((w * np.sin(f)).sum(), (w * np.cos(f)).sum())) / n
        target = corner + (180.0 / n if rule == "polygon_flat" else 0.0)
        return -target, {"corner_phase_deg": corner, "n": n, "z": c["z"]}
    if rule == "min_radius":
        # dreame align.py:96-97 (flat cut = angle of minimum radius)
        xy = largest_loop(m, float(c["z"]))
        r = np.hypot(xy[:, 0], xy[:, 1])
        th = np.degrees(np.arctan2(xy[:, 1], xy[:, 0]))
        k = int(np.argmin(r))
        return -float(th[k]), {"r_min": float(r[k]), "theta_deg": float(th[k]), "z": c["z"]}
    if rule == "fourier_mass":
        # B02 q03_datum_full.py:117-121: arg(sum e^{i n theta})/n over a radius band
        n = int(c["n"])
        v = m.vertices
        rr = np.hypot(v[:, 0], v[:, 1])
        s = (rr > c["r_range"][0]) & (rr < c["r_range"][1])
        if "z_range" in c:
            s &= (v[:, 2] > c["z_range"][0]) & (v[:, 2] < c["z_range"][1])
        th = np.arctan2(v[s, 1], v[s, 0])
        cn = np.exp(1j * n * th).sum()
        ph = math.degrees(np.angle(cn)) / n
        cands = sorted(((ph + 360.0 / n * k + 180) % 360) - 180 for k in range(n))
        pick = c.get("pick_nearest_deg", 0.0)
        chosen = min(cands, key=lambda a: abs(((a - pick + 180) % 360) - 180))
        return -chosen, {"n": n, "candidates_deg": cands, "chosen_deg": chosen,
                         "strength": float(abs(cn) / max(s.sum(), 1)), "n_vertices": int(s.sum()),
                         "label_rule": c.get("label_rule", "candidate nearest pick_nearest_deg")}
    if rule == "plane_normal":
        an = R_cur[:3, :3] @ unit(c["approx_normal_raw"])
        pl = level_plane(m, an, c.get("cone_deg", 10.0), c.get("tol", 0.05),
                         offset_range=c.get("offset_range"), seed=seed)
        nrm = pl["normal"]
        perp = 90.0 - ang_between(nrm, np.array([0, 0, 1.0]))
        return -math.degrees(math.atan2(nrm[1], nrm[0])), {
            "plane_fit_rms_mm": pl["fit_rms_mm"], "plane_fit_max_mm": pl["fit_max_mm"],
            "plane_n_faces": pl["n_faces"], "plane_out_of_perpendicular_deg": perp}
    if rule == "axis_direction":
        # clock by the direction of a second (non-coaxial) cylinder axis, e.g. a tube leaving an
        # elbow: fit its axis (normals-eigen, cropped like an axis primary), project it onto XY
        # and rotate so it points at target_deg (OD-S02 run, 2026-09-28: the only flat clocking
        # face was noisier than the scan noise floor; the tube axis is the functional exit).
        for k in ("approx_axis_raw", "crop_point_raw", "crop_radius"):
            if k not in c:
                raise SpecError(f"clock axis_direction requires {k}")
        ax0 = unit(R_cur[:3, :3] @ unit(c["approx_axis_raw"]))
        cp = (R_cur @ np.r_[np.asarray(c["crop_point_raw"], float), 1.0])[:3]
        ax = ax0
        sel = np.zeros(len(m.faces), bool)
        for _ in range(max(1, int(c.get("iters", 3)))):
            q = m.triangles_center - cp
            sel = np.abs(m.face_normals @ ax) < c.get("perp_max", 0.30)
            sel &= np.linalg.norm(q - np.outer(q @ ax, ax), axis=1) < c["crop_radius"]
            if "crop_axial" in c:
                t_ax = q @ ax
                sel &= (t_ax >= c["crop_axial"][0]) & (t_ax <= c["crop_axial"][1])
            if sel.sum() < 10:
                raise SpecError("clock axis_direction: fewer than 10 faces in the crop")
            af = axis_from_normals(m.triangles_center[sel], m.face_normals[sel], m.area_faces[sel])
            d = af["direction"]
            ax = d if d @ ax0 >= 0 else -d
        refine = None
        if c.get("refine") == "section_circles":
            if "crop_axial" not in c:
                raise SpecError("clock refine section_circles needs crop_axial")
            t_shift = float((af["point"] - cp) @ ax)
            rf = refine_axis_sections(m, af["point"], ax, c["crop_radius"],
                                      [c["crop_axial"][0] - t_shift, c["crop_axial"][1] - t_shift],
                                      c.get("refine_step", 0.5), c.get("refine_halfw", 0.2))
            refine = {k: v for k, v in rf.items() if k not in ("point", "direction")}
            refine["normals_eigen_vs_refined_deg"] = ang_between(ax, rf["direction"])
            ax = rf["direction"] if rf["direction"] @ ax0 >= 0 else -rf["direction"]
            af = dict(af, point=rf["point"], direction=ax)
        qc = m.triangles_center[sel] - af["point"]
        rad = np.linalg.norm(qc - np.outer(qc @ ax, ax), axis=1)
        rres = rad - np.median(rad)
        ang = math.degrees(math.atan2(ax[1], ax[0]))
        target = float(c.get("target_deg", 0.0))
        return -(ang - target), {
            "axis_dir_before_clock": ax.tolist(), "axis_point_before_clock": af["point"].tolist(),
            "axis_azimuth_deg": ang, "target_deg": target,
            "axis_elevation_deg": float(math.degrees(math.asin(float(np.clip(ax[2], -1, 1))))),
            "median_radius_mm": float(np.median(rad)), "n_faces": int(sel.sum()),
            "fit_rms_mm": float(np.sqrt((rres ** 2).mean())), "fit_max_mm": float(np.max(np.abs(rres))),
            "fit_metric": "radial residual of the cropped cylinder faces about the fitted axis",
            "refine": refine}
    raise SpecError(f"unknown clock rule {rule!r}")


# ----------------------------------------------------------------------------- landmarks
def landmark(m: trimesh.Trimesh, L: dict[str, Any]) -> dict[str, Any]:
    v = m.vertices
    s = np.ones(len(v), bool)
    r = np.hypot(v[:, 0], v[:, 1])
    if "r_range" in L:
        s &= (r >= L["r_range"][0]) & (r <= L["r_range"][1])
    if "z_range" in L:
        s &= (v[:, 2] >= L["z_range"][0]) & (v[:, 2] <= L["z_range"][1])
    if not s.any():
        return {"name": L["name"], "expected": L["expected"], "observed": None, "ok": False,
                "note": "no vertices in the landmark window"}
    col = {"x": v[s, 0], "y": v[s, 1], "z": v[s, 2], "r": r[s]}[L["stat"][0]]
    fn = {"max": np.max, "min": np.min, "median": np.median}[L["stat"][1:]]
    obs = float(fn(col))
    return {"name": L["name"], "stat": L["stat"], "expected": L["expected"], "tol": L["tol"],
            "observed": obs, "ok": bool(abs(obs - L["expected"]) <= L["tol"]),
            "tol_source": L.get("tol_source", "")}


# ----------------------------------------------------------------------------- main
def run(spec: dict[str, Any], spec_path: Path) -> tuple[int, dict[str, Any]]:
    base = spec_path.parent
    mesh_p = (base / spec["mesh"]).resolve()
    out_dir = (base / spec.get("out_dir", ".")).resolve()
    seed = int(spec.get("seed", 0))
    inputs = {str(mesh_p): sha256_file(mesh_p), str(spec_path.resolve()): sha256_file(spec_path)}
    if spec.get("raw_scan"):
        rp = (base / spec["raw_scan"]).resolve()
        inputs[str(rp)] = sha256_file(rp)
    noise = spec.get("noise")
    if noise and noise.get("from"):
        noise = json.loads((base / noise["from"]).read_text())["scan_noise_mm"]
    ns = spec.get("noise_secondary")
    if ns and ns.get("from"):
        spec["noise_secondary"] = json.loads((base / ns["from"]).read_text())["scan_noise_mm"]
    if not noise or noise.get("value") is None or not noise.get("method"):
        raise SpecError("spec.noise {value, method} is required: measure the noise floor first "
                        "(datum_fit.py noise); RE_SPEC.md:126-129 compares fit residuals to it")
    m = trimesh.load_mesh(mesh_p, process=True)
    sf = float(spec.get("scale_factor", 1.0))
    S = np.eye(4)
    S[:3, :3] *= sf
    # review M1: keep a small sample of the RAW (pre-scale) vertices to self-check that
    # matrix_4x4 (= T @ S, folded below) actually maps raw -> the datum frame.
    check_idx = np.linspace(0, len(m.vertices) - 1, min(20, len(m.vertices))).astype(int)
    raw_check_pts = m.vertices[check_idx].copy()
    m.apply_transform(S)

    P = spec["primary"]
    stop: list[str] = []
    findings: list[str] = []
    res: dict[str, Any] = {}
    # ---- primary
    if P["type"] == "plane":
        pl = level_plane(m, P["approx_normal"], P.get("cone_deg", 10.0), P.get("tol", 0.05),
                         P.get("bin_mm", 0.1), P.get("halfwidth_mm", 0.15), P.get("offset_range"),
                         seed=seed)
        n = pl["normal"]
        side = P.get("material_side", "-z")
        zdir = n if side == "-z" else -n
        T1 = trimesh.geometry.align_vectors(zdir, [0, 0, 1])
        zc = (T1[:3, :3] @ pl["centroid"])[2]
        T2 = np.eye(4)
        T2[2, 3] = -zc
        T = T2 @ T1
        primary = {"type": "plane", "mesh_region_desc": P["desc"], "why": P["why"],
                   "fit_rms_mm": pl["fit_rms_mm"], "fit_max_mm": pl["fit_max_mm"],
                   "fit_p95_mm": pl["fit_p95_mm"], "n_faces": pl["n_faces"], "area_mm2": pl["area_mm2"],
                   # review m1: the gated rms/max above are trimmed to |d| < 2*tol around the
                   # RANSAC plane, which structurally caps fit_max_mm; the untrimmed residual
                   # over the whole peak offset bin is reported alongside it (STOP still gates
                   # rms only, RE_SPEC's "RMS + max" vs QUESTIONS SS C).
                   "fit_untrimmed": pl["fit_untrimmed"], "inlier_frac": pl["inlier_frac"],
                   "normal_raw": n.tolist(), "centroid_raw": pl["centroid"].tolist(),
                   "material_side": side, "ransac": pl["ransac"]}
        res["primary_inlier_z_median"] = None
        prim_faces = pl["faces"]
    elif P["type"] == "axis":
        # review B1: crop to ONE clean cylinder is required, because the STOP-check
        # residual below is a radial residual about the fitted axis, which is only
        # meaningful for a single, non-mixed cylindrical crop.
        if "crop_radius" not in P or "crop_point" not in P:
            raise SpecError("axis primary requires crop_point and crop_radius (crop to one "
                            "clean cylinder; the radial residual is meaningless on a mixed crop)")
        ax = unit(P["approx_axis"])
        sel = np.zeros(len(m.faces), bool)
        for _ in range(max(1, int(P.get("iters", 3)))):  # review n2: iters=0 must not skip the fit
            sel = np.abs(m.face_normals @ ax) < P.get("perp_max", 0.30)
            q = m.triangles_center - np.asarray(P["crop_point"], float)
            dist = np.linalg.norm(q - np.outer(q @ ax, ax), axis=1)
            sel &= dist < P["crop_radius"]
            if "crop_axial" in P:
                # crop_radius alone is an infinite cylinder about the line through crop_point;
                # a long axis part (a stepped rod, a cone next to a cylinder) needs an axial
                # window too, or the radial residual mixes radii (OD-S02 run, 2026-09-28)
                t_ax = q @ ax
                sel &= (t_ax >= P["crop_axial"][0]) & (t_ax <= P["crop_axial"][1])
            if sel.sum() < 10:
                raise SpecError("axis primary: fewer than 10 faces perpendicular to approx_axis")
            af = axis_from_normals(m.triangles_center[sel], m.face_normals[sel], m.area_faces[sel])
            d = af["direction"]
            ax = d if d @ unit(P["approx_axis"]) >= 0 else -d
        refine = None
        if P.get("refine") == "section_circles":
            if "crop_axial" not in P:
                raise SpecError("refine section_circles needs crop_axial")
            # the axial window is kept on the same stretch of the part as the face crop
            cp = np.asarray(P["crop_point"], float)
            t_shift = float((af["point"] - cp) @ ax)
            rf = refine_axis_sections(m, af["point"], ax, P["crop_radius"],
                                      [P["crop_axial"][0] - t_shift, P["crop_axial"][1] - t_shift],
                                      P.get("refine_step", 0.5), P.get("refine_halfw", 0.2))
            refine = {k: v for k, v in rf.items() if k not in ("point", "direction")}
            refine["normals_eigen_vs_refined_deg"] = ang_between(ax, rf["direction"])
            d_r = rf["direction"]
            ax = d_r if d_r @ ax >= 0 else -d_r
            af = dict(af, point=rf["point"], direction=ax)
        T1 = trimesh.geometry.align_vectors(ax, [0, 0, 1])
        pt = T1[:3, :3] @ af["point"]
        T2 = np.eye(4)
        T2[0, 3], T2[1, 3] = -pt[0], -pt[1]
        T = T2 @ T1
        ld = af["line_dist"] or {"rms": float("nan"), "max": float("nan")}
        # review B1: the STOP-checked residual is the RADIAL residual of the cropped
        # cylinder faces about the fitted axis (rad = |(C - a) - ((C - a).d) d|, then
        # rad - median(rad)) - comparable to a circle noise floor. `line_dist` (the
        # normal-line distance from the fitted axis) is roughly radius x normal-angle
        # noise, a different metric; it is kept only as a diagnostic.
        a_pt, d_ax = af["point"], af["direction"]
        qc = m.triangles_center[sel] - a_pt
        rad = np.linalg.norm(qc - np.outer(qc @ d_ax, d_ax), axis=1)
        cone: dict[str, Any] | None = None
        if P.get("surface", "cylinder") == "cone":
            # a conical crop (tapered spigot): residual about the fitted line r = a + b*t along
            # the axis instead of about one median radius, which would read the taper itself
            # as residual (OD-S02 run, 2026-09-28). A cylinder is the b = 0 case.
            t_c = qc @ d_ax
            b_c, a_c = np.polyfit(t_c, rad, 1)
            rres = rad - (a_c + b_c * t_c)
            cone = {"half_angle_deg": float(math.degrees(math.atan(abs(b_c)))),
                    "dr_dt": float(b_c), "t_range_mm": [float(t_c.min()), float(t_c.max())]}
        else:
            rres = rad - np.median(rad)
        axis_rms = float(np.sqrt((rres ** 2).mean()))
        axis_max = float(np.max(np.abs(rres)))
        primary = {"type": "axis", "mesh_region_desc": P["desc"], "why": P["why"],
                   "fit_rms_mm": axis_rms, "fit_max_mm": axis_max,
                   "fit_metric": "radial residual of the cropped cylinder faces about the "
                                 "fitted axis, vs the median radius (review B1)",
                   "normal_line_dist": ld,
                   "eig_ratio": af["eig_ratio"], "n_faces": int(sel.sum()),
                   "direction_raw": ax.tolist(), "point_raw": af["point"].tolist(),
                   "crop": {"point": list(P["crop_point"]), "radius": P["crop_radius"],
                            "axial": P.get("crop_axial")},
                   "surface": P.get("surface", "cylinder"), "cone": cone, "refine": refine}
        if cone:
            primary["fit_metric"] = ("radial residual of the cropped cone faces about the fitted "
                                     "axis, vs a linear r(t) fit along the axis (surface: cone)")
        prim_faces = None
    else:
        raise SpecError(f"primary.type must be plane|axis, got {P['type']!r}")
    if P["type"] == "plane":
        if primary["mesh_region_desc"] and primary["mesh_region_desc"] in noise.get("method", ""):
            findings.append("primary STOP check is self-referential (noise measured on the "
                            "primary itself)")
        if primary["fit_rms_mm"] > noise["value"]:
            stop.append(f"primary fit rms {primary['fit_rms_mm']:.4f} > noise floor {noise['value']:.4f}")
    else:
        # review B1: an axis-primary's radial residual is a circle-type residual, so it is
        # compared with the circle noise floor (noise_secondary), never the flat noise floor.
        ns_primary = spec.get("noise_secondary")
        if ns_primary:
            if primary["fit_rms_mm"] > ns_primary["value"]:
                stop.append(f"primary fit rms {primary['fit_rms_mm']:.4f} > secondary (circle) "
                            f"noise floor {ns_primary['value']:.4f} ({ns_primary['method']})")
        else:
            findings.append("axis-primary radial residual not compared: no noise_secondary "
                            "(circle noise) measured on a clean circle (plane noise is not "
                            "comparable to a radial residual)")

    mc = apply(T, m)
    # ---- origin
    O = spec["origin"]
    secondary: dict[str, Any] | None = None
    tilt: dict[str, Any] = {"value": None, "method": "not measured"}
    if "xy" in O:
        feats = O["xy"] if isinstance(O["xy"], list) else [O["xy"]]
        c0 = (np.median(mc.triangles_center[prim_faces][:, :2], axis=0) if prim_faces is not None
              else np.zeros(2))
        st = []
        for f in feats:
            if "centre_guess" in f:
                c0f = np.asarray(f["centre_guess"], float)
            else:
                c0f = c0
            got = (wall_face_stations(mc, f, c0f) if f.get("method") == "wall_faces"
                   else circle_stations(mc, f))
            st += [dict(x, feature=f.get("desc", "")) for x in got]
        if not st:
            raise SpecError("origin.xy: no section circle matched r_hint/r_tol/rms_max/z_range. "
                            "No bbox fallback (dreame align.py:82 removed) - fix the spec.")
        feat_centres = {}
        for f in feats:
            fs = [s for s in st if s["feature"] == f.get("desc", "")]
            if fs:
                feat_centres[f.get("desc", "")] = (float(np.mean([s["cx"] for s in fs])),
                                                   float(np.mean([s["cy"] for s in fs])))
        if O.get("combine", "median") == "midpoint":
            # OD-W03 real run: the median over the pooled stations of TWO features is the
            # centre of whichever feature has more surviving stations, not their midpoint.
            # "midpoint" = mean of the per-feature mean centres (every feature must match).
            missing = [f.get("desc", "") for f in feats if f.get("desc", "") not in feat_centres]
            if missing:
                raise SpecError(f"origin.combine=midpoint: no station matched for {missing}")
            ox = float(np.mean([c[0] for c in feat_centres.values()]))
            oy = float(np.mean([c[1] for c in feat_centres.values()]))
        else:
            ox = float(np.median([s["cx"] for s in st]))
            oy = float(np.median([s["cy"] for s in st]))
        T3 = np.eye(4)
        T3[0, 3], T3[1, 3] = -ox, -oy
        T = T3 @ T
        mc = apply(T3, mc)
        tilt = tilt_from_stations(st)
        rms = [s["rms"] for s in st]
        secondary = {"type": "axis", "mesh_region_desc": " + ".join(f.get("desc", "") for f in feats),
                     "why": " / ".join(f.get("why", "") for f in feats if f.get("why")),
                     "fit_rms_mm": float(np.median(rms)), "fit_max_mm": float(np.max([s["max"] for s in st])),
                     "fit_metric": "median / worst circle residual over stations ("
                                   + ",".join(f.get("method", "kasa") for f in feats) + ")",
                     "stations": len(st),
                     "r_by_feature": {f.get("desc", ""): {
                         "n": len([s for s in st if s["feature"] == f.get("desc", "")]),
                         "r_mean": float(np.mean([s["r"] for s in st if s["feature"] == f.get("desc", "")] or [np.nan])),
                         "r_std": float(np.std([s["r"] for s in st if s["feature"] == f.get("desc", "")] or [np.nan]))}
                         for f in feats},
                     "centre_std_mm": [float(np.std([s["cx"] for s in st])), float(np.std([s["cy"] for s in st]))],
                     "station_detail": [{k: round(v, 5) if isinstance(v, float) else v
                                         for k, v in s.items()} for s in st]}
        ns = spec.get("noise_secondary")
        if ns:
            secondary["noise_ref"] = ns
            if secondary["fit_rms_mm"] > ns["value"]:
                stop.append(f"origin circle median rms {secondary['fit_rms_mm']:.4f} > secondary noise "
                            f"floor {ns['value']:.4f} ({ns['method']})")
        else:
            secondary["noise_ref"] = None
            findings.append("secondary circle residual not compared: no noise_secondary measured on a "
                            "clean circle (plane noise is not comparable to section-circle residuals)")
    elif P["type"] == "plane":
        raise SpecError("plane primary needs origin.xy (axis or feature that pins X/Y)")
    if P["type"] == "axis":
        Z = O.get("z")
        if not Z:
            raise SpecError("axis primary needs origin.z (plane or extreme)")
        if Z["type"] == "plane":
            pz = level_plane(mc, Z["approx_normal_datum"], Z.get("cone_deg", 10.0), Z.get("tol", 0.05),
                             offset_range=Z.get("offset_range"), seed=seed)
            z0 = float(pz["centroid"][2])
            res["origin_z_plane"] = {"fit_rms_mm": pz["fit_rms_mm"], "fit_max_mm": pz["fit_max_mm"],
                                     "out_of_perpendicular_deg": ang_between(pz["normal"], np.array([0, 0, 1.0]))}
        elif Z["type"] == "extreme":
            z0 = float(mc.vertices[:, 2].max() if Z["which"] == "max" else mc.vertices[:, 2].min())
        else:
            raise SpecError("origin.z.type must be plane|extreme")
        T4 = np.eye(4)
        T4[2, 3] = -z0
        T = T4 @ T
        mc = apply(T4, mc)

    # ---- clock
    C = spec["clock"]
    if C["rule"] == "feature_line":
        # OD-W03 real run: clock a two-feature part (cup pair, boss pair) by the line through
        # two origin-feature centres, A -> B onto +X. fourier_mass (n=2) was biased 0.7 deg by
        # asymmetric mass (necks, ears) on that part. Centres are the per-feature station means
        # re-expressed after the origin shift T3.
        if "xy" not in O:
            raise SpecError("clock feature_line needs origin.xy features")
        try:
            a = np.asarray(feat_centres[C["from"]]) - [ox, oy]
            b = np.asarray(feat_centres[C["to"]]) - [ox, oy]
        except KeyError as e:
            raise SpecError(f"clock feature_line: {e} is not an origin.xy feature desc with stations")
        v = b - a
        cdeg = -math.degrees(math.atan2(v[1], v[0]))
        cdet = {"from": C["from"], "to": C["to"], "centre_from": a.tolist(), "centre_to": b.tolist(),
                "separation_mm": float(np.linalg.norm(v))}
    else:
        cdeg, cdet = clock_angle(mc, T, C, seed)
    Rz = rot_z(cdeg)
    T = Rz @ T
    mc = apply(Rz, mc)
    if P["type"] == "axis" and C["rule"] == "axis_direction":
        if secondary is None:   # origin.xy circle stations, when given, stay the secondary record
            secondary = {"type": "axis", "mesh_region_desc": C.get("desc", ""), "why": C.get("why", ""),
                         "fit_rms_mm": cdet["fit_rms_mm"], "fit_max_mm": cdet["fit_max_mm"],
                         "fit_metric": cdet["fit_metric"]}
        # a clock cylinder of another material (e.g. a steel tube on a plastic part) may carry its
        # own noise floor measured on a DISJOINT stretch of the same material (clock.noise.from);
        # otherwise the circle noise floor (noise_secondary) gates it
        ns = spec.get("noise_secondary")
        cn = C.get("noise")
        if cn and cn.get("from"):
            cn = json.loads((base / cn["from"]).read_text())["scan_noise_mm"]
        if cn:
            if not cn.get("method"):
                raise SpecError("clock.noise needs {value, method} (or from: a noise JSON)")
            ns = cn
        if ns:
            cdet["noise_ref"] = ns
            if cdet["fit_rms_mm"] > ns["value"]:
                stop.append(f"clock axis rms {cdet['fit_rms_mm']:.4f} > secondary (circle) noise "
                            f"floor {ns['value']:.4f} ({ns['method']})")
        else:
            findings.append("clock axis residual not compared: no noise_secondary measured")
    if P["type"] == "axis" and C["rule"] == "plane_normal":
        secondary = {"type": "plane", "mesh_region_desc": C.get("desc", ""), "why": C.get("why", ""),
                     "fit_rms_mm": cdet["plane_fit_rms_mm"], "fit_max_mm": cdet["plane_fit_max_mm"]}
        if cdet["plane_fit_rms_mm"] > noise["value"]:
            stop.append(f"clock plane rms {cdet['plane_fit_rms_mm']:.4f} > noise floor {noise['value']:.4f}")

    # ---- sanity landmarks (auto + spec)
    lms: list[dict[str, Any]] = []
    if prim_faces is not None:
        zmed = float(np.median(mc.triangles_center[prim_faces][:, 2]))
        lms.append({"name": "primary plane at z=0", "expected": 0.0, "observed": zmed,
                    "tol": noise["value"], "tol_source": "measured noise floor",
                    "ok": abs(zmed) <= noise["value"]})
    for L in spec.get("landmarks", []):
        lms.append(landmark(mc, L))

    # ---- removed fractions come from intake.json (never retyped, CHK-NUMBERS spirit)
    removed: dict[str, Any] = {"fragments_pct": None, "table_pct": None, "method": "not recorded"}
    if spec.get("intake_json"):
        ij = (base / spec["intake_json"]).resolve()
        rj = json.loads(ij.read_text())["removed"]
        removed = {"fragments_pct": rj["fragments_pct"], "table_pct": rj["table_pct"],
                   "method": "; ".join(rj["method"]) or "nothing removed"}
        inputs[str(ij)] = sha256_file(ij)
    # ---- write
    out_dir.mkdir(parents=True, exist_ok=True)
    aligned = out_dir / spec.get("aligned_name", "aligned_work.stl")
    mc.export(aligned)
    ext = (mc.bounds[1] - mc.bounds[0]).tolist()
    tilt_ref = float(spec.get("tilt_reference_deg", 0.3))  # RE_SPEC.md:241 audit angle, report-only (Q2)
    if tilt["value"] is None:
        tilt_res = "finding"
    elif tilt.get("resolvable") is False:
        tilt_res = "finding"
    else:
        tilt_res = "pass" if tilt["value"] <= tilt_ref else "finding"
    tilt_note = f"{tilt['method']}; reference {tilt_ref} deg (RE_SPEC.md:241, report-only)"
    if tilt.get("resolvable") is False:
        tilt_note = ("not resolvable: per-feature tilt vectors disagree beyond their combined "
                    "stderr (heuristic, review M2); " + tilt_note)
    checks = {"CHK-TILT": {"ran": tilt["value"] is not None, "result": tilt_res, "note": tilt_note},
              "CHK-SCALE": spec.get("chk_scale", {"ran": False, "result": "finding",
                                                  "note": "no CHK-SCALE record passed in spec"})}
    status = "STOP" if stop else ("CHECK_LANDMARKS" if not all(l["ok"] for l in lms) else "OK")
    # review M1: matrix_4x4 folds scale_factor in (T @ S), so it maps the RAW scan directly
    # to the datum frame (run-contract SS11), matching what consumers like
    # stl-re-measure-intent/scripts/common.py apply to the raw scan. scale_factor stays a
    # recorded field. Self-check on a sample of raw vertices vs the aligned mesh (mc).
    TS = T @ S
    homog = np.c_[raw_check_pts, np.ones(len(raw_check_pts))]
    predicted = (TS @ homog.T).T[:, :3]
    check_err = float(np.abs(predicted - mc.vertices[check_idx]).max()) if len(check_idx) else 0.0
    if check_err > 1e-6:
        raise SpecError(f"internal error: apply(matrix_4x4, raw) disagrees with aligned_work.stl "
                        f"by {check_err:.3g} mm (review M1 self-check)")
    doc = {**json_header("alignment", "align.py", inputs, seed),
           "status": status, "stop_reasons": stop, "findings": findings,
           "matrix_4x4": TS.tolist(),
           "scale_factor": sf,
           "scan_noise_mm": {"value": noise["value"], "method": noise["method"]},
           "primary": primary,
           "secondary": secondary,
           "clock": {"rule": C["rule"] + (f": {C['desc']}" if C.get("desc") else ""),
                     "angle_deg": float(cdeg), "why": C.get("why", ""), "detail": cdet},
           "tilt_deg": tilt,
           "origin": {"definition": O["definition"]},
           "sanity_landmarks": lms,
           "removed": removed,
           "bounds_aligned": mc.bounds.tolist(),
           "extents_aligned": ext,
           "aligned_mesh": {"path": str(aligned), "sha256": sha256_file(aligned)},
           "checks": checks,
           "note": "matrix_4x4 maps the RAW scan to the datum frame, row-major; scale_factor is "
                   "folded in (T @ S, run-contract SS11). aligned_work.stl is exported at the "
                   "scaled size (unchanged)."}
    if "origin_z_plane" in res:
        doc["origin"]["z_plane_fit"] = res["origin_z_plane"]
    (out_dir / "alignment.json").write_text(json.dumps(doc, indent=1, default=lambda o: o.tolist()))
    return (2 if stop else 0), doc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec", type=Path, help="datum spec JSON (see references/datum-cookbook.md)")
    a = ap.parse_args(argv)
    try:
        spec = json.loads(a.spec.read_text())
        code, doc = run(spec, a.spec)
    except SpecError as e:
        print(f"ALIGN FAILED: {e}", file=sys.stderr)
        return 3
    summ = {k: doc[k] for k in ("status", "stop_reasons", "findings", "scale_factor", "tilt_deg", "sanity_landmarks")}
    summ["primary"] = {k: doc["primary"].get(k) for k in ("type", "fit_rms_mm", "fit_max_mm", "n_faces")}
    if doc["secondary"]:
        summ["secondary"] = {k: doc["secondary"].get(k) for k in ("type", "fit_rms_mm", "fit_max_mm", "stations", "r_by_feature", "centre_std_mm")}
    summ["clock"] = {"rule": doc["clock"]["rule"], "angle_deg": doc["clock"]["angle_deg"]}
    summ["extents_aligned"] = doc["extents_aligned"]
    print(json.dumps(summ, indent=1))
    if code == 2:
        print("STOP: a datum fit residual exceeds the measured noise floor (RE_SPEC.md:126-129). "
              "Do not proceed; pick a cleaner region or report.", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
