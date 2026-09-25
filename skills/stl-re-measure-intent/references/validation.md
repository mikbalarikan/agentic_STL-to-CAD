# Script validation against golden numbers

These runs are **inspection only**. None re-grades a project. Decimated scans are marked as
such (`golden-examples/README.md`: decimated copies deviate ≤0.028 mm from the originals). The
runs used Python 3.11, trimesh 5.1.0, numpy 2.4.6, scipy 1.17.1, build123d 0.13.0. A
determinism check ran `pattern_count.py` twice in fresh processes and got identical JSON
apart from `created`.

## pattern_count.py (new code: no golden code exists)

| Case | Command (abridged) | Result | Golden |
|---|---|---|---|
| M02 big gear, delivered STEP tessellated at 0.005 mm | `--stations 0.5,1.5,2.5 --orders 10,40 --tol 0.002` | **30** at 3/3 stations; qualified {10, 15, 30}; residual at 30 = 2.1e-6 mm, at 29/31 = 0.66 mm; tip Ø 19.049997; crest peaks 31/32/31 | 30; qualified {10, 15, 30}; OD 19.049996889; peaks 31 (`qa_report.json#gears.big`) |
| M02 small gear | `--stations 3.5,6.5,9.5 --orders 10,40 --tol 0.002` | **17** at 3/3; qualified {17}; tip Ø 11.199998; crest peaks 18/18/18 | 17; qualified {17}; OD 11.199998555; peaks 16 at z 9.5 |
| P03 kidneys, decimated scan + `2_mesh_cleaned/alignment.json` | `--signal mass --stations 0.5,1.4,2.2 --z-half 0.3 --r-band 35,44 --rays 3600` | **8** (FFT-dominant at 3/3; residual local minimum); mass crest phase 25.2–25.5° | 8, F[8] dominant, spokes 25° + k·45° (`OOM-P03/6_RE_work/PARAM_TABLE.md:38`) |
| P03 stem, same scan | `--signal radius --stations 14.5,15.5,16.0 --r-band 0,8` | **6** at 3/3, coverage 0.67–0.70; flats r 5.48–5.50, corners r 6.44; crest phase 48.0–48.3° | order 6; flats r 5.48, corners r 6.41, corners 48° + k·60° (`PARAM_TABLE.md:42`); QA r 5.54/6.87 (`VERDICT.md:49`) |
| P03 tread slots, same scan (extra) | `--signal mass --r-band 58.6,63.4 --orders 20,80` | FFT 49 / 49 / 51 → **CHK-COUNT finding** (stations disagree) | "~51 (pitch 7.0°)" (`PARAM_TABLE.md:37`); the partial ~270° scan is a likely cause, unconfirmed |

The absolute FFT magnitudes are not comparable with P03's "F[8] = 144.6", because P03's
normalisation and signal are not recorded. Compare only which order is dominant.

## sim_caliper.py (lifted from B02 q10/40_verify)

| Case | Result | Golden |
|---|---|---|
| B02 delivered STEP (`4_STEP/OOM-B02.step`, tess 0.005 mm), z = 1.00, outside jaws | window **25.617 … 26.850**, min jaws @ 59.00°, max @ 30.00° | CAD 25.617 @ 59.00°, 26.850 (`OOM-B02/6_RE_work/PARAM_TABLE.md:154-155`): **exact** |
| B02 full-res scan `2_mesh_cleaned/OOM-B02.stl` + `alignment.json`, z = 1.00, r-band 12–14, outside jaws | window **24.988 … 27.246**, min jaws @ 59.0°; coverage 0.878, gaps 96–107° and 109–143° (the recorded occlusion 96–140°) | "25.99 … 27.08" (`PARAM_TABLE.md:111`) |
| Reading 24.84 ± 0.1 against the scan window, no `--scan-offset` | **UNPROVEN** (0.148 below the min; `d` not measured on this scan) | struck, "1.15 mm below" |
| Reading 24.84 ± 0.1, `--scan-offset 0.56` (B02 F10: scan mean 5.89 − caliper 5.33, `MEASUREMENTS.md:61`/`PARAM_TABLE.md:41`) | **UNPROVEN, within the measured scan offset** (margin 0.148 < d 0.56) | — |
| B02 full-res scan, z = 1.00, r-band 9.5–11 (cup bore), inside jaws, reading 20.75 ± 0.1 | window **18.388 … 21.024**, coverage 0.692 (two gaps: −35.75…39.75° and 43.75…79°) — **20.75 is achievable, PASS** | `CUP_BORE_D` (F03) used directly at 20.750, PASS at Tier-1 (`PARAM_TABLE.md:36,153`) |

**Round-1 fixes applied here (orchestrator decisions B1, B2 — `reviews/stl-re-measure-intent.md`):**
inside-jaw mode now requires `--r-band`, pools the in-band points from every polyline of the
open scan section, and builds an inner (min-radius) envelope with its own real angular
coverage instead of picking one polyline and assuming full coverage. This is what fixes the
cup bore case above: the old inside-jaw code struck the golden-accepted F03 (20.75). Below
the outside-jaw window, a reading is only struck when the margin exceeds a measured, per-scan
`--scan-offset d`; within `d` (or when `d` is unknown) it is unproven, not struck. This is why
F06 (24.84) now reads UNPROVEN above rather than STRUCK: F10's dilation on the same scan
(0.56 mm) exceeds F06's window margin (0.148 mm).

**Explained (was "not recorded"): the B02 caliper window.** On this reproduction's scan the
outside-jaw window minimum sits at jaw azimuth 59°, opposite the arm-3 flat at −121° (R
12.53). The golden's own analysis gives the method: "minimum achievable diametral reading is
*lobe + flat*", R(θ) + R(θ+180°) (`OOM-B02/6_RE_work/VERDICT.md:64-66`). Evaluating that
analytic pair — R(30°) = 13.444 (a lobe crest) + R(−121°) = 12.530 (the arm-3 flat) = **25.97
≈ the golden's 25.99** (`PARAM_TABLE.md:108-111` and §G-5) — reproduces the golden's window
almost exactly. That argument leaves out the SAF-1 recess (§G-5 in the golden's own notes: a
36°-wide, ~1.05 mm deep dip in the skirt wall at θ ≈ 59°, R(59°) ≈ 12.28). The CAD recess is
narrow (flat half-width 7° + 7° ramp, `build_OOM-B02.py:79-81`), so flat jaws bridge it and
the CAD minimum stays at 25.617; but on the real scan section the support-function window
(what a physical two-jaw caliper actually reads, recess included) is 24.99, not 25.99. So:
the golden's recorded window used the analytic lobe+flat argument and excluded the SAF-1
recess; this skill's full support-function window includes it. Both give the same STRIKE/
UNPROVEN call region-wise, but the margin differs (0.15 mm vs 1.15 mm before B2, now UNPROVEN
either way once F10's 0.56 mm dilation is applied). D-06 = 25.79 (A3, "also below the
achievable window") falls **inside** both windows; combined with B2 it is "use/ask", not
"below window".

## sections.py cluster (CHK-CLUSTER)

P03 decimated scan, box z 13.9–20, r 0–7: 4564 vertices, 9021 faces, 222.6 mm² in **one**
connected component. Up-facing top plane z 18.41 (max 18.49), tilt 0.45°, rms 0.057 mm. The
golden reports a "158k coherent raw verts; solid flat top" stem to +18.56
(`OOM-P03/6_RE_work/PARAM_TABLE.md:43`). The vertex counts differ because this run used the
decimated copy.

## fits.py / sections.py planar

On the M02 tessellation, the bore loop Kåsa radius is 0.97497 (Ø1.950, operator 1.95). Loop
tracks chain the outer loops across the 30T→17T transition and keep the bore as a separate
track.
