#!/usr/bin/env python3
"""Simulated two-parallel-jaw caliper on a mesh section: the ACHIEVABLE reading window.

Provenance: lifted from
  golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q10_solid_tess_tier1.py
  (`densify` ds 0.02 mm, `jaws` support-function width over jaw azimuth step 0.05 deg,
  `zsec`, and the outer-envelope R(theta) block at :80-82 with 0.25 deg stations and a
  +/-0.3 deg window) and 6_RE_work/40_verify.py:62-65 (support_width) / inside-jaw bore block.
  B02 used it (a) to prove one Tier-1 caliper reading unachievable on the scan (see
  analysis/golden/OOM-B02.md and PARAM_TABLE.md:108-121 for the reading and window) and
  (b) for Tier-1 on the finished STEP.
Changes: generalised (any z station, any mesh, optional r-band filter, optional arbitrary
section plane), empty envelope bins are skipped and reported as angular gaps instead of
raising, a reading is classified against the window (CHK-ACHIEVABLE), typed, argparse,
run-contract §2 JSON header. Shared with stl-re-verify (Tier-1 on the STEP tessellation).

Gap logic (why a struck-low reading survives partial coverage): widths measured on a
subset of the true outline are <= the true widths in every jaw direction, so the reported
MIN is <= the true minimum. A reading below the reported min minus its uncertainty is
therefore unachievable even with occlusion gaps. A reading ABOVE the reported max is only
provably unachievable when angular coverage is complete. This holds for both the outer
(outside-jaw) and inner (inside-jaw) envelope: both are support widths of a point set built
from whatever the scan actually shows, so a gap can only narrow the sampled window, never
widen it.

Scan dilation (`--scan-offset`, orchestrator decision B2, 2026-09-25): a caliper reading can
sit legitimately below the scan window when the scan itself reads oversize at that station
(B02 arm width is a worked case: see analysis/golden/OOM-B02.md, `MEASUREMENTS.md:61`,
`PARAM_TABLE.md:41`). `d` is measured per scan by the caller (the largest scan-minus-caliper
gap among the *other* calipered dims of the same scan) and passed in; it is never a constant.
A margin below the window but within `d` is `UNPROVEN`, not struck: only a miss that exceeds
the measured offset is a clear STRIKE. When `d` is unknown (no other calipers on this scan),
any below-window reading is `UNPROVEN` rather than struck.
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


def inner_envelope(pts: np.ndarray, dtheta: float = 0.25, half_window: float = 0.3
                   ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Min radius per angular station (bore/inside-jaw dual of `outer_envelope`).

    Same station/window mechanics as `outer_envelope`, but takes the MIN radius in each
    window instead of the MAX, so it tracks the inner (bore) wall on an open scan section
    instead of picking a whole polyline and hoping it is the bore (B1). Returns TH, Rin
    (NaN = gap), env xy.
    """
    rr = np.hypot(pts[:, 0], pts[:, 1])
    tt = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
    TH = np.arange(-180, 180, dtheta)
    order = np.argsort(tt)
    tt_s, rr_s = tt[order], rr[order]
    Rin = np.full(len(TH), np.nan)
    tt_ext = np.r_[tt_s - 360, tt_s, tt_s + 360]
    rr_ext = np.r_[rr_s, rr_s, rr_s]
    lo = np.searchsorted(tt_ext, TH - half_window, side="left")
    hi = np.searchsorted(tt_ext, TH + half_window, side="right")
    for i, (a, b) in enumerate(zip(lo, hi)):
        if b > a:
            Rin[i] = rr_ext[a:b].min()
    ok = np.isfinite(Rin)
    env = np.c_[Rin[ok] * np.cos(np.radians(TH[ok])), Rin[ok] * np.sin(np.radians(TH[ok]))]
    return TH, Rin, env


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


def classify(reading: float, unc: float, wmin: float, wmax: float, full_coverage: bool,
             offset: Optional[float] = None) -> dict[str, Any]:
    """offset = `d`, the measured per-scan dilation (B2). None = not measured on this scan."""
    if wmin - unc <= reading <= wmax + unc:
        return {"achievable": True, "state": "PASS", "action": "use (within window)"}
    if reading < wmin - unc:
        margin = wmin - reading
        if offset is None:
            return {"achievable": None, "state": "UNPROVEN", "margin_mm": rnd(margin),
                    "action": "UNPROVEN: below the window but no measured scan-offset for this scan "
                              "(d); measure d from another calipered dim on the same scan before "
                              "striking (SYN B2)",
                    "proof_valid_with_gaps": True, "scan_offset_mm": None}
        if margin <= offset + 1e-9:
            return {"achievable": None, "state": "UNPROVEN", "margin_mm": rnd(margin),
                    "action": "UNPROVEN: below the window but within the measured scan dilation "
                              "offset; do not build to it, do not strike it — ask for a "
                              "jaw-placement photo or re-measure",
                    "proof_valid_with_gaps": True, "scan_offset_mm": offset}
        return {"achievable": False, "state": "STRIKE", "margin_mm": rnd(margin),
                "action": "STRIKE: below the minimum achievable two-jaw reading by more than the "
                          "measured scan offset; record proof + re-measure hook; do not build to it",
                "proof_valid_with_gaps": True, "scan_offset_mm": offset}
    margin = reading - wmax
    if full_coverage:
        return {"achievable": False, "state": "STRIKE", "margin_mm": rnd(margin),
                "action": "STRIKE: above the maximum achievable reading", "proof_valid_with_gaps": False}
    return {"achievable": None, "state": "UNPROVEN", "margin_mm": rnd(margin),
            "action": "UNPROVEN: above the measured max but coverage has gaps; ask for a re-measure / photo of jaw placement",
            "proof_valid_with_gaps": False}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, help="scan STL or STEP tessellation (STL)")
    ap.add_argument("--alignment", help="alignment.json raw->datum (omit if mesh is in the datum frame)")
    ap.add_argument("--z", type=float, required=True, help="section height in the datum frame (B02 skirt: 1.00)")
    ap.add_argument("--mode", choices=["outside", "inside"], default="outside",
                    help="outside jaws on the outer envelope; inside jaws on the inner (bore) "
                         "envelope built from --r-band points (required in this mode)")
    ap.add_argument("--r-band", help="rlo,rhi: keep only section points in this radius band")
    ap.add_argument("--dtheta", type=float, default=0.25, help="envelope station step, deg (B02: 0.25)")
    ap.add_argument("--half-window", type=float, default=0.3, help="envelope half window, deg (B02: 0.3)")
    ap.add_argument("--jaw-step", type=float, default=0.05, help="jaw azimuth step, deg (B02: 0.05)")
    ap.add_argument("--ds", type=float, default=0.02, help="polyline resample step, mm (B02: 0.02)")
    ap.add_argument("--reading", type=float, action="append", default=[], help="caliper reading(s) to classify")
    ap.add_argument("--reading-unc", type=float, default=0.1,
                    help="reading uncertainty, mm (photo-transcribed: 0.1 effective, OOM-B02 MEASUREMENTS.md:24)")
    ap.add_argument("--scan-offset", type=float, default=None,
                    help="d: measured per-scan dilation, mm (largest scan-minus-caliper gap among "
                         "the OTHER calipered dims of this same scan; see analysis/golden/OOM-B02.md "
                         "for a worked case, MEASUREMENTS.md:61 / PARAM_TABLE.md:41). Not a "
                         "threshold, and never invented: omit it when no other caliper exists on "
                         "this scan, and a below-window reading is then UNPROVEN, not struck (B2)")
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
        if not a.r_band:
            sys.exit("--mode inside requires --r-band lo,hi to isolate the bore section "
                     "(B1: an open scan section has no single 'innermost loop' to pick)")
        pts = np.vstack(polys)
        TH, R, env = inner_envelope(pts, a.dtheta, a.half_window)
        if not np.isfinite(R).any():
            sys.exit(f"no in-band points at z={a.z}, r-band {a.r_band}")
        w = jaws(env, a.jaw_step)
        cov = float(np.isfinite(R).mean())
        res.update({"envelope_r_min": rnd(np.nanmin(R)), "envelope_r_max": rnd(np.nanmax(R)),
                    "angular_coverage": rnd(cov, 4), "gaps_deg": gaps(TH, R, a.dtheta),
                    "note": "inside jaws: two-jaw support width of the inner (bore) envelope built "
                            "from in-band points only; gaps reduce provable width the same way as "
                            "the outside envelope (see module docstring)"})
    i0, i1 = int(np.argmin(w[:, 1])), int(np.argmax(w[:, 1]))
    wmin, wmax = float(w[i0, 1]), float(w[i1, 1])
    res.update({"window_min": rnd(wmin, 4), "window_min_jaw_deg": rnd(w[i0, 0], 3),
                "window_max": rnd(wmax, 4), "window_max_jaw_deg": rnd(w[i1, 0], 3)})
    readings = []
    for r in a.reading:
        readings.append({"reading": r, "uncertainty_mm": a.reading_unc,
                         **classify(r, a.reading_unc, wmin, wmax, cov >= 1.0, a.scan_offset)})
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
