#!/usr/bin/env python3
"""Simulated two-parallel-jaw caliper on a mesh section: the ACHIEVABLE reading window.

Provenance: lifted from
  golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q10_solid_tess_tier1.py
  (`densify` ds 0.02 mm, `jaws` support-function width over jaw azimuth step 0.05 deg,
  `zsec`, and the outer-envelope R(theta) block at :224-229 with 0.25 deg stations and a
  +/-0.3 deg window) and 6_RE_work/40_verify.py:support_width / inside-jaw bore block.
  B02 used it (a) to prove caliper F06 = 24.84 unachievable on the scan (window
  25.99...27.08, PARAM_TABLE.md:108-121) and (b) for Tier-1 on the finished STEP.
Changes: generalised (any z station, any mesh, optional r-band filter, optional arbitrary
section plane), empty envelope bins are skipped and reported as angular gaps instead of
raising, a reading is classified against the window (CHK-ACHIEVABLE), typed, argparse,
run-contract §2 JSON header. Shared with stl-re-verify (Tier-1 on the STEP tessellation).

Gap logic (why a struck-low reading survives partial coverage): widths measured on a
subset of the true outline are <= the true widths in every jaw direction, so the reported
MIN is <= the true minimum. A reading below the reported min minus its uncertainty is
therefore unachievable even with occlusion gaps. A reading ABOVE the reported max is only
provably unachievable when angular coverage is complete.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (densify, header, load_alignment, load_mesh, rnd,  # noqa: E402
                    section_polylines, write_json)


def jaws(pts2d: np.ndarray, step: float = 0.05) -> np.ndarray:
    """Support-function width over jaw azimuth: what two parallel jaws actually read."""
    a = np.radians(np.arange(0, 180, step))
    v = np.stack([np.cos(a), np.sin(a)], 1)
    q = pts2d @ v.T
    return np.c_[np.degrees(a), q.max(0) - q.min(0)]


def outer_envelope(pts: np.ndarray, dtheta: float = 0.25, half_window: float = 0.3
                   ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Max radius per angular station (B02 40_verify.py:62-65). Returns TH, Rout (NaN = gap), env xy."""
    rr = np.hypot(pts[:, 0], pts[:, 1])
    tt = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
    TH = np.arange(-180, 180, dtheta)
    order = np.argsort(tt)
    tt_s, rr_s = tt[order], rr[order]
    Rout = np.full(len(TH), np.nan)
    tt_ext = np.r_[tt_s - 360, tt_s, tt_s + 360]
    rr_ext = np.r_[rr_s, rr_s, rr_s]
    lo = np.searchsorted(tt_ext, TH - half_window, side="left")
    hi = np.searchsorted(tt_ext, TH + half_window, side="right")
    for i, (a, b) in enumerate(zip(lo, hi)):
        if b > a:
            Rout[i] = rr_ext[a:b].max()
    ok = np.isfinite(Rout)
    env = np.c_[Rout[ok] * np.cos(np.radians(TH[ok])), Rout[ok] * np.sin(np.radians(TH[ok]))]
    return TH, Rout, env


def gaps(TH: np.ndarray, R: np.ndarray, dtheta: float) -> list[list[float]]:
    miss = ~np.isfinite(R)
    out: list[list[float]] = []
    if not miss.any():
        return out
    i = 0
    n = len(TH)
    while i < n:
        if miss[i]:
            j = i
            while j + 1 < n and miss[j + 1]:
                j += 1
            out.append([float(TH[i]), float(TH[j] + dtheta)])
            i = j + 1
        else:
            i += 1
    if len(out) > 1 and out[0][0] == -180 and out[-1][1] >= 180:
        out[0] = [out[-1][0], out[0][1] + 360]
        out.pop()
    return out


def classify(reading: float, unc: float, wmin: float, wmax: float, full_coverage: bool) -> dict[str, Any]:
    if wmin - unc <= reading <= wmax + unc:
        return {"achievable": True, "action": "use (within window)"}
    if reading < wmin - unc:
        return {"achievable": False, "margin_mm": rnd(wmin - reading),
                "action": "STRIKE: below the minimum achievable two-jaw reading; record proof + re-measure hook; do not build to it",
                "proof_valid_with_gaps": True}
    return {"achievable": (None if not full_coverage else False), "margin_mm": rnd(reading - wmax),
            "action": ("STRIKE: above the maximum achievable reading" if full_coverage else
                       "UNPROVEN: above the measured max but coverage has gaps; ask for a re-measure / photo of jaw placement"),
            "proof_valid_with_gaps": False}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, help="scan STL or STEP tessellation (STL)")
    ap.add_argument("--alignment", help="alignment.json raw->datum (omit if mesh is in the datum frame)")
    ap.add_argument("--z", type=float, required=True, help="section height in the datum frame (B02 skirt: 1.00)")
    ap.add_argument("--mode", choices=["outside", "inside"], default="outside",
                    help="outside jaws on the outer envelope; inside jaws on the innermost loop (bores)")
    ap.add_argument("--r-band", help="rlo,rhi: keep only section points in this radius band")
    ap.add_argument("--dtheta", type=float, default=0.25, help="envelope station step, deg (B02: 0.25)")
    ap.add_argument("--half-window", type=float, default=0.3, help="envelope half window, deg (B02: 0.3)")
    ap.add_argument("--jaw-step", type=float, default=0.05, help="jaw azimuth step, deg (B02: 0.05)")
    ap.add_argument("--ds", type=float, default=0.02, help="polyline resample step, mm (B02: 0.02)")
    ap.add_argument("--reading", type=float, action="append", default=[], help="caliper reading(s) to classify")
    ap.add_argument("--reading-unc", type=float, default=0.1,
                    help="reading uncertainty, mm (photo-transcribed: 0.1 effective, OOM-B02 MEASUREMENTS.md:10)")
    ap.add_argument("--name", default="caliper")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    m = load_mesh(a.mesh, load_alignment(a.alignment))
    polys = [densify(p[:, :2], a.ds) for p in section_polylines(m, [0, 0, a.z], [0, 0, 1])]
    if not polys:
        sys.exit(f"no section at z={a.z}")
    if a.r_band:
        lo, hi = (float(v) for v in a.r_band.split(","))
        polys = [p[(np.hypot(p[:, 0], p[:, 1]) >= lo) & (np.hypot(p[:, 0], p[:, 1]) <= hi)] for p in polys]
        polys = [p for p in polys if len(p) >= 2]
    res: dict[str, Any] = {"z": a.z, "mode": a.mode, "r_band": a.r_band}
    if a.mode == "outside":
        pts = np.vstack(polys)
        TH, R, env = outer_envelope(pts, a.dtheta, a.half_window)
        w = jaws(env, a.jaw_step)
        cov = float(np.isfinite(R).mean())
        res.update({"envelope_r_min": rnd(np.nanmin(R)), "envelope_r_max": rnd(np.nanmax(R)),
                    "angular_coverage": rnd(cov, 4), "gaps_deg": gaps(TH, R, a.dtheta)})
    else:
        inner = min(polys, key=lambda p: np.hypot(p[:, 0], p[:, 1]).max())
        w = jaws(inner, a.jaw_step)
        ri = np.hypot(inner[:, 0], inner[:, 1])
        cov = 1.0
        res.update({"inner_2rmax_about_axis": rnd(2 * ri.max()),
                    "note": "inside jaws: window = support widths of the innermost loop (convex-hole approximation)"})
    i0, i1 = int(np.argmin(w[:, 1])), int(np.argmax(w[:, 1]))
    wmin, wmax = float(w[i0, 1]), float(w[i1, 1])
    res.update({"window_min": rnd(wmin, 4), "window_min_jaw_deg": rnd(w[i0, 0], 3),
                "window_max": rnd(wmax, 4), "window_max_jaw_deg": rnd(w[i1, 0], 3)})
    readings = []
    for r in a.reading:
        readings.append({"reading": r, "uncertainty_mm": a.reading_unc,
                         **classify(r, a.reading_unc, wmin, wmax, cov >= 1.0)})
    res["readings"] = readings
    results = [x["achievable"] for x in readings]
    chk = "pass" if results and all(x is True for x in results) else ("fail" if any(x is False for x in results) else
                                                                        ("finding" if results else "not-run"))
    out = header("sim_caliper.json", "sim_caliper.py", [p for p in (a.mesh, a.alignment) if p])
    out.update({"name": a.name, "frame": "datum; jaw azimuth deg CCW from +X", "result": res,
                "check": {"CHK-ACHIEVABLE": {"ran": bool(readings), "result": chk}}})
    write_json(a.out, out)
    print(f"{a.name} z={a.z} {a.mode}: two-jaw window {wmin:.3f} .. {wmax:.3f} "
          f"(jaws @ {w[i0, 0]:.2f} / {w[i1, 0]:.2f} deg), coverage {cov:.3f}")
    for x in readings:
        print(f"  reading {x['reading']:.3f} +/- {x['uncertainty_mm']}: {x['action']}")


if __name__ == "__main__":
    main()
