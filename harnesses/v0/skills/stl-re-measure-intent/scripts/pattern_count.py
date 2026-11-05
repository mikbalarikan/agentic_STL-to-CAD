#!/usr/bin/env python3
"""Count a polar pattern (teeth, lobes, kidneys, flats) by ROTATIONAL ORDER at >=3 stations.

Provenance: NEW CODE - no golden source code exists for this method (the M02 QA script and
the P03 analysis code are not in the repo: analysis/golden/M02-02-03.md §11, Questions 8;
analysis/golden/OOM-P03.md §11). The method is re-implemented from the recorded evidence:
  - golden-examples/M02-02-03_watertight-design-intent/qa_report.json#gears.*.station_details:
    section -> largest-|area| loop -> 10,200 centre-out rays -> residual table per rotational
    order -> an order qualifies when its max-abs radial residual <= 0.002 mm (exact CAD) ->
    take the MAXIMAL qualified order; crest-peak count (prominence ~0.10 mm) kept as a
    diagnostic only (it gave 31 and 16 for 30 and 17: G/VERDICT.md:25).
  - golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/PARAM_TABLE.md:38,42 and VERDICT.md:49:
    angular FFT of radius / material vs theta, dominant order (F[8]=144.6 kidneys, F[6] stem).
  - golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q03_datum_full.py:108-113:
    n-fold Fourier phase of the angular mass distribution (arg(sum e^{in theta})/n).
Changes vs the recorded method: the order search range and the qualification tolerance are
CLI parameters (M02 hard-coded orders 10-40 and 0.002 mm, which suits exact CAD, not scans);
three signal types; phase of the selected order is reported.

Signals (all in the DATUM frame, theta CCW about +Z from +X - CHK-FRAME):
  radius : exact ray/segment intersections of the z-section, outermost r per ray (M02 method).
           Works on open scan polylines; rays with no hit are NaN (coverage reported).
  inner  : innermost r per ray (bores, internal splines).
  mass   : area-weighted histogram of face centroids in a z-band x r-band over theta
           (P03 "material vs theta", B02 "angular mass"). Robust on non-watertight scans.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (header, load_alignment, load_mesh, rnd, scan_noise_mm,  # noqa: E402
                    section_polylines, write_json)


# ----------------------------------------------------------------------------- signals
def ray_radii(polys: list[np.ndarray], n_rays: int, cx: float = 0.0, cy: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Outer and inner radius per centre-out ray over all section polylines (exact intersections)."""
    dphi = 2 * np.pi / n_rays
    rmax = np.full(n_rays, -np.inf)
    rmin = np.full(n_rays, np.inf)
    for p in polys:
        p = p[:, :2] - [cx, cy]
        p0, p1 = p[:-1], p[1:]
        e = p1 - p0
        t0 = np.arctan2(p0[:, 1], p0[:, 0])
        dt = np.arctan2(p1[:, 1], p1[:, 0]) - t0
        dt = (dt + np.pi) % (2 * np.pi) - np.pi
        ok = np.abs(dt) < np.pi * 0.999
        a, b = t0 / dphi, (t0 + dt) / dphi
        lo, hi = np.ceil(np.minimum(a, b)), np.floor(np.maximum(a, b))
        cnt = np.where(ok, np.maximum(hi - lo + 1, 0), 0).astype(int)
        if cnt.sum() == 0:
            continue
        sid = np.repeat(np.arange(len(p0)), cnt)
        off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        k = (lo[sid] + off).astype(int)
        phi = k * dphi
        d = np.c_[np.cos(phi), np.sin(phi)]
        q0, ee = p0[sid], e[sid]
        den = d[:, 0] * ee[:, 1] - d[:, 1] * ee[:, 0]
        good = np.abs(den) > 1e-15
        t = np.zeros_like(den)
        t[good] = -(d[good, 0] * q0[good, 1] - d[good, 1] * q0[good, 0]) / den[good]
        good &= (t >= -1e-9) & (t <= 1 + 1e-9)
        r = ((q0 + ee * t[:, None]) * d).sum(1)
        good &= r > 0
        kk = np.mod(k[good], n_rays)
        np.maximum.at(rmax, kk, r[good])
        np.minimum.at(rmin, kk, r[good])
    rmax[~np.isfinite(rmax)] = np.nan
    rmin[~np.isfinite(rmin)] = np.nan
    return rmax, rmin


def mass_signal(mesh, n_bins: int, zb: tuple[float, float], rb: tuple[float, float]) -> np.ndarray:
    c = mesh.triangles_center
    a = mesh.area_faces
    r = np.hypot(c[:, 0], c[:, 1])
    k = (c[:, 2] >= zb[0]) & (c[:, 2] <= zb[1]) & (r >= rb[0]) & (r <= rb[1])
    th = np.mod(np.arctan2(c[k, 1], c[k, 0]), 2 * np.pi)
    h, _ = np.histogram(th, bins=n_bins, range=(0, 2 * np.pi), weights=a[k])
    return h.astype(float)


def fill_periodic(s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(s)
    if valid.all():
        return s.copy(), valid
    if valid.sum() < 4:
        raise ValueError("signal has <4 valid samples")
    x = np.arange(len(s))
    xv, sv = x[valid], s[valid]
    xp = np.r_[xv - len(s), xv, xv + len(s)]
    sp = np.r_[sv, sv, sv]
    return np.interp(x, xp, sp), valid


# ----------------------------------------------------------------------------- analysis
def fold_residual(s: np.ndarray, valid: np.ndarray, n: int) -> tuple[float, float]:
    """Residual of s against its n-fold symmetric part (periodic linear interpolation)."""
    N = len(s)
    x = np.arange(N)
    xp = np.r_[x, N]
    sp = np.r_[s, s[0]]
    sym = np.zeros(N)
    for j in range(n):
        sym += np.interp((x + j * N / n) % N, xp, sp)
    sym /= n
    d = (s - sym)[valid]
    return float(np.sqrt((d ** 2).mean())), float(np.abs(d).max())


def analyse(s_raw: np.ndarray, kmin: int, kmax: int, tol: Optional[float], metric: str,
            prominence: Optional[float]) -> dict[str, Any]:
    s, valid = fill_periodic(s_raw)
    N = len(s)
    F = np.fft.rfft(s - s.mean())
    mag = np.abs(F)
    kmax_eff = min(kmax, N // 2 - 1)
    ks = np.arange(kmin, kmax_eff + 1)
    dom = int(ks[np.argmax(mag[ks])])
    top = ks[np.argsort(mag[ks])[::-1][:5]]
    table = []
    for n in ks:
        rms, mx = fold_residual(s, valid, int(n))
        table.append({"order": int(n), "rms": rnd(rms, 9), "max_abs": rnd(mx, 9), "fft_mag": rnd(mag[n], 6)})
    res_by_n = {t["order"]: (t["rms"] if metric == "rms" else t["max_abs"]) for t in table}
    qualified = [n for n, v in res_by_n.items() if tol is not None and v is not None and v <= tol]
    selected_res = max(qualified) if qualified else None
    best_min = min(res_by_n, key=lambda n: res_by_n[n])

    def contrast(n: int) -> Optional[float]:
        nb = [res_by_n[m] for m in (n - 1, n + 1) if m in res_by_n]
        return rnd(res_by_n[n] / min(nb), 6) if nb and min(nb) > 0 else None

    def local_min(n: int) -> bool:
        return all(res_by_n[n] < res_by_n[m] for m in (n - 1, n + 1) if m in res_by_n)

    ptp = float(np.nanmax(s_raw) - np.nanmin(s_raw))
    prom = prominence if prominence is not None else 0.08 * ptp
    ext = np.r_[s, s, s]
    pk, _ = find_peaks(ext, prominence=prom)
    pk = pk[(pk >= N) & (pk < 2 * N)] - N
    sel = selected_res if selected_res is not None else dom
    phase = float(np.degrees(-np.angle(F[sel])) / sel) % (360.0 / sel)
    return {
        "n_samples": N, "coverage": rnd(valid.mean(), 4), "signal_ptp": rnd(ptp),
        "fft_dominant_order": dom, "fft_top5": [int(v) for v in top],
        "residual_metric": metric, "tolerance": tol, "qualified_orders": qualified,
        "selected_maximal_order": selected_res,
        "min_residual_order": int(best_min),
        "contrast_selected_vs_neighbours": contrast(sel),
        "fft_dominant_is_residual_local_min": local_min(dom),
        "crest_phase_deg_of_selected": rnd(phase, 3),
        "diagnostic_peak_count": int(len(pk)), "diagnostic_peak_prominence": rnd(prom),
        "order_table": table,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, help="STL or STEP-tessellated STL")
    ap.add_argument("--alignment", help="alignment.json (raw->datum); omit if the mesh is already in the datum frame")
    ap.add_argument("--signal", choices=["radius", "inner", "mass"], default="radius")
    ap.add_argument("--stations", required=True, help="comma list of z stations (>=3 required by CHK-COUNT)")
    ap.add_argument("--z-half", type=float, default=None, help="mass: half-height of the z band around each station")
    ap.add_argument("--r-band", help="rlo,rhi: mass band, or radius/inner: keep only hits in this band")
    ap.add_argument("--rays", type=int, default=10200, help="rays/bins per revolution (M02 QA used 10,200)")
    ap.add_argument("--orders", default="2,60", help="kmin,kmax search range (M02 used 10,40; must exceed the expected count)")
    ap.add_argument("--tol", type=float, default=None,
                    help="residual qualification tolerance, EXACT CAD ONLY (M02 QA used 0.002 mm max-abs). "
                         "Omit for scans: the count then comes from FFT dominance + residual local minimum")
    ap.add_argument("--metric", choices=["rms", "max"], default=None, help="default: max if --tol given, else rms")
    ap.add_argument("--peak-prominence", type=float, default=None,
                    help="diagnostic crest-peak prominence (default 8%% of signal ptp; M02 used 0.102 mm on a 1.276 mm tooth depth)")
    ap.add_argument("--name", default="pattern")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    al = load_alignment(a.alignment)
    m = load_mesh(a.mesh, al)
    zs = [float(v) for v in a.stations.split(",")]
    kmin, kmax = (int(v) for v in a.orders.split(","))
    tol = a.tol
    metric = a.metric or ("max" if tol is not None else "rms")
    noise = scan_noise_mm(al)
    rb = tuple(float(v) for v in a.r_band.split(",")) if a.r_band else None

    stations = []
    for z in zs:
        if a.signal == "mass":
            if a.z_half is None or rb is None:
                sys.exit("mass signal needs --z-half and --r-band")
            s = mass_signal(m, a.rays, (z - a.z_half, z + a.z_half), rb)  # type: ignore[arg-type]
            extra: dict[str, Any] = {"z_band": [z - a.z_half, z + a.z_half], "r_band": list(rb)}
        else:
            polys = section_polylines(m, [0, 0, z], [0, 0, 1])
            if rb is not None:
                keep = []
                for p in polys:
                    r = np.hypot(p[:, 0], p[:, 1])
                    if ((r >= rb[0]) & (r <= rb[1])).mean() > 0.5:
                        keep.append(p)
                polys = keep
            if not polys:
                stations.append({"z": z, "error": "no section"})
                continue
            rmax, rmin = ray_radii(polys, a.rays)
            s = rmax if a.signal == "radius" else rmin
            extra = {"n_polylines": len(polys), "r_max": rnd(np.nanmax(s)), "r_min": rnd(np.nanmin(s)),
                     "d_from_rmax": rnd(2 * np.nanmax(s))}
        res = analyse(s, kmin, kmax, tol, metric, a.peak_prominence)
        stations.append({"z": z, **extra, **res})
        print(f"z={z:8.3f} cov={res['coverage']:.3f} FFT-dominant={res['fft_dominant_order']:3d} "
              f"selected-maximal={res['selected_maximal_order']} min-residual={res['min_residual_order']} "
              f"peaks(diag)={res['diagnostic_peak_count']}")

    ok = [s for s in stations if "error" not in s]
    fft_orders = sorted({s["fft_dominant_order"] for s in ok})
    sel_orders = sorted({s["selected_maximal_order"] for s in ok if s["selected_maximal_order"] is not None})
    count: Optional[int] = None
    notes = []
    if len(ok) < 3:
        result = "fail"
        notes.append(f"only {len(ok)} usable stations; CHK-COUNT needs >=3")
    elif tol is not None:
        # exact-geometry rule (M02 qa_report): maximal qualified order, identical at every station
        if len(sel_orders) == 1 and all(s["selected_maximal_order"] == sel_orders[0] for s in ok):
            count, result = sel_orders[0], "pass"
            notes.append("maximal qualified rotational order (M02 method)")
            if fft_orders != [count]:
                result = "finding"
                notes.append(f"FFT-dominant orders {fft_orders} differ from {count}: inspect")
        else:
            result = "finding"
            notes.append(f"residual method disagrees across stations: {sel_orders}; FFT {fft_orders}")
    elif len(fft_orders) == 1:
        count = fft_orders[0]
        lm = all(s["fft_dominant_is_residual_local_min"] for s in ok)
        result = "pass" if lm else "finding"
        notes.append("FFT-dominant order identical at every station (P03 method)"
                     + ("; residual is a local minimum at every station" if lm
                        else "; residual NOT a local minimum at every station - inspect the order table"))
    else:
        result = "finding"
        notes.append(f"stations disagree on the FFT-dominant order: {fft_orders}")
    cov = [s["coverage"] for s in ok]
    if cov and min(cov) < 1.0:
        notes.append(f"angular coverage {min(cov):.3f} < 1 at some station (partial scan): gaps were interpolated")
    peaks = [s["diagnostic_peak_count"] for s in ok]
    if count is not None and any(p != count for p in peaks):
        notes.append(f"crest-peak counts {peaks} disagree with {count}: expected, peaks are diagnostic only (M02 31/16)")

    out = header("pattern_count.json", "pattern_count.py", [a.mesh, a.alignment] if a.alignment else [a.mesh])
    out.update({"name": a.name, "signal": a.signal, "frame": "datum; theta CCW about +Z from +X",
                "tolerance": tol, "metric": metric, "scan_noise_mm": noise,
                "orders_searched": [kmin, kmax], "count": count,
                "check": {"CHK-COUNT": {"ran": True, "result": result, "note": "; ".join(notes)}},
                "stations": stations})
    write_json(a.out, out)
    print(f"COUNT = {count}   CHK-COUNT {result}   {'; '.join(notes)}")


if __name__ == "__main__":
    main()
