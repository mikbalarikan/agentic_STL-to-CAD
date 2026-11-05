---
name: stl-re-measure-intent
description: Measures a datum-aligned scan and extracts design intent for STL→CAD reverse engineering. Covers sections, primitive fits, R(θ) maps, pattern counts by rotational order, caliper/photo authority with achievability checks, and noise-bounded rounding. Writes measure/params.json and PARAM_TABLE.md (measured→chosen, rule, source). Use after stl-re-intake-datum and before CAD modelling, or to re-measure a feature a gate flagged.
---

# stl-re-measure-intent

Stage 2 of `stl-re-orchestrate`. It turns an aligned scan, calipers and photos into one
parameter file. The rebuild reads that file and nothing else. Every golden REVISE and every
wrong candidate started here, not in CAD code: B02 F06 attribution, P03 stem dismissed as
occlusion, M02 wrong 27T count (`analysis/SKILL_ARCHITECTURE.md` §1). Measure carefully, and
write down why each number is what it is.

**Boundary.** This skill does not move the datum (stl-re-intake-datum owns `alignment.json`),
does not build CAD (stl-re-rebuild-build123d), and does not grade anything
(stl-re-verify). If the frame looks wrong, stop and send it back to intake. Never re-fit the
datum here, and never fit it to your own CAD (CHK-CIRCULAR, P03: `analysis/golden/OOM-P03.md` §3).

## Inputs → outputs (run-contract: `../stl-re-orchestrate/references/run-contract.md`)

| In | From |
|---|---|
| `intake/aligned_work.stl` (or the raw scan + `intake/alignment.json`) | intake |
| `intake/alignment.json`: `matrix_4x4`, `scan_noise_mm`, frame, clock rule | intake |
| `intake/INTAKE_CARD.md` feature list; `intake/MEASUREMENTS.md` request with scan-predicted values | intake |
| `input/MEASUREMENTS.md` (filled), `input/photos/` | human |

| Out | Content |
|---|---|
| `measure/params.json` | schema: run-contract §4 plus `references/param-table-schema.md` |
| `measure/PARAM_TABLE.md` | rendered by `scripts/param_table.py`; never hand-edited |
| `measure/figures/` | every JSON/NPZ/PNG a row cites as `evidence` |

## Numbers this skill may use (only these: `analysis/SYNTHESIS.md` §4)

| Number | Use | Source |
|---|---|---|
| `scan_noise_mm` (measured per scan) | the only rounding allowance for scan values | `intake/alignment.json`; SYN C8, A7 |
| ±0.1 mm | standard-size snap window, caliper values only | `baseline/oomwoo-re-pipeline/RE_SPEC.md:92` |
| ±0.1 mm effective | photo-transcribed caliper reading uncertainty | `golden-examples/OOM-B02_side-brush-3-arm/5_reference/MEASUREMENTS.md:24` |
| ±0.15 mm | Tier-1 band that a struck reading would have failed (context only; verify owns it) | `RE_SPEC.md:170` |
| 0.05–0.1 mm | RANSAC plane tolerance ≈ scan noise | `RE_SPEC.md:127` |
| ≥3 stations | minimum for any pattern count | SYN C3 / CHK-COUNT |

Script defaults such as the ray count, envelope window and resample step are **golden
parameters, not thresholds**. Each is labelled in `--help` with the golden that used it.

## Procedure

Work in the frozen datum frame from `alignment.json`. Write every output under `measure/`.
Scripts live in `scripts/`. Pass `--alignment intake/alignment.json` with the raw scan, or
omit it with `aligned_work.stl`.

### 0. Preconditions

1. Read `scan_noise_mm` from `alignment.json`. If it is missing, stop rounding. Measure it on a
   clean primitive, e.g. `fits.py plane-ransac --tol <0.05–0.1> --z … --r …` on a flat
   functional face, and record it as a finding for intake. Golden noise floors vary by part and
   surface; see `analysis/golden/*.md` if you need a reference point (SYN A7).
2. Copy the frame text (primary, secondary, clock rule, θ sign convention) into
   `params.json#frame`. Every angle you record is in this frame (CHK-FRAME, step 11).
3. Open one params row per INTAKE_CARD feature, plus every feature you find later. A feature
   you won't model gets a declared row (`rule: assumed`, note "not modelled: why"). B02 did
   this for bristles and the COTS screw (`OOM-B02/6_RE_work/PARAM_TABLE.md:103-104`).

### 1. Planar sections along the datum axis (SYN C1)

`python scripts/sections.py planar --mesh <scan> [--alignment A] --nz 25 --out measure/figures/planar.json`

- Stations sit **strictly inside** features, never on a face, edge or blend. M02 counted
  teeth at "three strictly interior stations per gear"
  (`golden-examples/M02-02-03_watertight-design-intent/VERDICT.md:25`). DRM used 25 stations
  (`golden-examples/dreame_brush-caps/report/source/align.py:56`).
- Each closed loop gets its area, centroid, r-range and a Kåsa circle with rms/max. `tracks`
  chains loops station to station by nearest centroid. Use a track to follow a bore or boss
  through z. A track that jumps means a feature starts or ends there, so add a station.

### 2. Radial half-plane sections (SYN C1)

`python scripts/sections.py radial --mesh <scan> --thetas 0,59,120,… --out measure/figures/radial.json`

- Place half-planes through every non-axisymmetric feature (arm, key, window, flat) and one
  between features. B02 cut meridians at arm 1 and at the SAF-1 key; P03 cut one at a spoke
  (`analysis/golden/OOM-B02.md` §4, `analysis/golden/OOM-P03.md` §4).
- A half-plane with no scan trace proves nothing: re-cut it where there is data. This is the
  failure mode that earned CHK-OVERLAY (DRM 150° panel, SYN E12).

### 3. (r,z) / (θ,r) maps and R(θ) for turned or lobed parts (SYN C2)

```
python scripts/sections.py maps   --mesh <scan> --out measure/figures/maps.json
python scripts/sections.py rtheta --mesh <scan> --z 1.0 --r-band 12,14 --out measure/figures/rtheta_z1.json
```

- The (r,z) map is the half-profile to revolve: read the levels, steps and blends from it
  (DRM, B02, P03). The (θ,r) map shows patterns, keys and clocking. The maps are area-weighted,
  so they don't depend on tessellation density.
- R(θ) gives the outer envelope per 0.25° station, with `coverage` and `gaps_deg`. **Read the
  gaps.** B02's skirt had no scan over θ 96–140° (`OOM-B02/2_mesh_cleaned/alignment.json#notes`).
  Nothing measured inside a gap is scan evidence.
- Take percentile levels per radius ring on clean sectors, as B02 did for its dome meridian and
  floor (floor p50, apex p99: `OOM-B02/6_RE_work/PARAM_TABLE.md:57-65`). Write the percentile
  into `estimator`.

### 4. Primitive fits with residuals (SYN B4, C13)

`python scripts/fits.py circle|circle-irls|line|plane|plane-ransac --mesh <scan> --z lo,hi --r lo,hi [--theta lo,hi] [--section-z Z --loop largest] --name BORE --out measure/figures/fit_BORE.json`

- Circles: start with Kåsa. When edges, chamfers or a second wall contaminate the points, use
  `circle-irls` (Cauchy). B02's audit used a 0.30 mm scale
  (`OOM-B02/6_RE_work/qa/q03_datum_full.py:89-101`).
- **A residual alone never accepts a fit.** Compare the fit against the independent
  percentile radius the script also reports, or against a section plot (facet-film T6,
  `analysis/baseline/facet-film-transferable.md`).
- Planes: `plane-ransac --tol` at the scan noise (`RE_SPEC.md:127`); the seed is fixed at 0.
- Copy `estimator`, `residual.rms` and the output path into the params row (C13).

### 5. Pattern counts by rotational order: CHK-COUNT (SYN C3)

```
# exact geometry (a STEP tessellation, operator CAD): M02 rule
python scripts/pattern_count.py --mesh cad.stl --stations 0.5,1.5,2.5 --orders 10,40 --tol 0.002 --out measure/figures/count_big.json
# scan: FFT dominance + residual local minimum, >=3 stations
python scripts/pattern_count.py --mesh <scan> --alignment A --signal mass --stations 0.5,1.4,2.2 --z-half 0.3 --r-band 35,44 --rays 3600 --out measure/figures/count_kidneys.json
```

- Signals: `radius` gives the outer r per centre-out ray (teeth, lobes, polygon flats);
  `inner` gives the innermost r (splines, bores); `mass` gives area in a z×r band per θ bin
  (windows, spokes, slots). `mass` also works on non-watertight scans.
- Set `--orders` above the expected count. M02's hard-coded 10–40 would miss a 41-tooth gear
  (`analysis/golden/M02-02-03.md` §11). Keep `kmin` above 2 on scans: orders 1–2 pick up
  eccentricity, ovality and partial coverage (inspection: P03 outer radius was dominated by
  order 2, `references/validation.md`).
- Use `count` only when `CHK-COUNT` is `pass`. The crest phase goes into the params as the
  pattern clock, in the datum frame.
- **Never count crest peaks.** On exact CAD they gave 31 and 16 for 30 and 17
  (`qa_report.json#gears.*.station_details[*].diagnostic_peak_count`). The script reports them
  as a diagnostic only. On P03, an eyeball count at intake was wrong and the FFT count
  corrected it (`OOM-P03/6_RE_work/PARAM_TABLE.md:59`; see `analysis/golden/OOM-P03.md` for the
  counts).
- Gears: `references/gears.md` (heuristic, n=1: M02).

### 6. Authority: caliper/operator > scan > photo (SYN C4, C5; `RE_SPEC.md:86-98`)

- A caliper or operator value governs the dimension it covers, and is used directly
  (`caliper-direct`, with a `derivation` such as `radius = D/2` when needed) **after step 7**.
  Operator values replaced M02's wrong scan candidate (`M02 DESIGN_NOTES.md:5`).
- The scan governs form, positions, profiles, blends and anything a caliper can't reach.
- Photos govern intent: functional vs cosmetic, real feature vs artefact, symmetry. A photo
  is never a dimension, except as a photo-transcribed caliper reading. That reading needs the
  photo id, an owner-confirmed `attribution`, and `uncertainty_mm ≥ 0.1`. Without the
  attribution it is unused (B02 D-09/10/12). Details: `references/intent-rules.md` §3.
- A caliper vs scan gap that is not uniform across dims is local dilation, not scale. Use the
  caliper locally and never rescale here (B02 lesson 15, `analysis/golden/OOM-B02.md` §12).

### 7. CHK-ACHIEVABLE: prove each caliper reading is possible on the scan (SYN C6)

For every width or diameter reading:

`python scripts/sim_caliper.py --mesh <scan> --alignment A --z <station> --mode outside|inside --r-band lo,hi --reading <value> --reading-unc <u> [--scan-offset d] --out measure/figures/cal_<ID>.json`

- The script builds the section, the outer (or, `--mode inside`, inner/bore) envelope and the
  two-jaw support width over jaw azimuth, then classifies the reading against the window.
  Code lifted from `OOM-B02/6_RE_work/qa/q10_solid_tess_tier1.py:jaws`. `--r-band` is required
  in `--mode inside`: an open scan section has no single closed "innermost loop" to pick, so
  the script pools the in-band points instead (B1, 2026-09-25).
- `d` (`--scan-offset`) is the measured, per-scan dilation: the largest scan-minus-caliper gap
  among the *other* calipered dims of the *same* scan (B02's arm-width reading is a worked
  case: see `analysis/golden/OOM-B02.md`, `MEASUREMENTS.md:61`/`PARAM_TABLE.md:41`). Compute it
  from those other rows before running this step; never invent it, and omit it when this scan
  has no other caliper.
- **Within the window** → use it.
  **Below min − u − d** → **strike**: add a `struck[]` entry with the window, the proof and a
  re-measure hook, and build that feature from the scan. The proof holds even with gaps,
  because a partial outline only under-reads.
  **Below min − u but within d of it** (or `d` unknown) → **unproven**: within the measured
  scan dilation, do not build to it and do not strike it; ask for a re-measure or a
  jaw-placement photo (B2, 2026-09-25).
  **Above max + u with gaps** → unproven: ask for a re-measure or a jaw-placement photo.
- For depths and heights, compare against the scan-predicted value from the measurement
  request (`RE_SPEC.md:197-202`). If they differ by more than u + noise, investigate the
  attribution before building. (No golden struck a depth, so there is no stronger rule.)
- **A flagged impossibility is a stop.** On B02 it1, a caliper reading was flagged as an
  unachievable two-jaw window and still built to that reading "per the rebuild brief" instead of
  being struck; the built solid read back outside tolerance and the loop went to REVISE
  (`analysis/golden/OOM-B02.md` §8). It2 struck that reading and changed exactly one parameter
  (see the golden analysis for which one and its value).

### 8. Rounding and snapping: noise-bounded, never a fixed grid (SYN C8, C9, C10)

Apply `references/intent-rules.md` §2 and §5. In short:

- A scan value moves only within `scan_noise_mm` of its estimate, or stays inside the measured
  range of its sub-features. **There is no 0.1 / 0.5 / 1.0 mm step.** That dropped baseline
  rule appears in no golden (`analysis/SYNTHESIS.md` §3). When noise is unknown, don't round.
- A standard-size snap is allowed only for caliper values within ±0.1 mm (`RE_SPEC.md:92`).
  Label it **(heuristic, doctrine only: no golden applied it; SYN §6)**.
- **Never snap an uncalipered critical interface.** Hold the scan fit and set
  `critical: true` and a `rerun_trigger`. On B02, a critical hex-across-flats interface was
  deliberately held at its scan fit rather than snapped to a nearby standard size, with the
  rerun trigger "one caliper reading on this feature should trigger a re-run"
  (`OOM-B02/6_RE_work/VERDICT.md:28-30`; see `analysis/golden/OOM-B02.md` for the held value).
- Enforce symmetry or equal pitch when the measured scatter is within noise. When it isn't,
  enforce it only with a `scatter_note` giving the intent reason and the residual it leaves
  (B02 arms 120°; DRM cup PCD). Otherwise keep the measured values and declare the asymmetry
  (DRM legs 60°/150°/−60°; OD coil centre −0.2, 0.1).

### 9. Provenance for unscanned or occluded geometry (SYN C11)

Anything the scan did not see gets `source: photo-inferred | standard | assumed`, `measured:
null`, and a note on what would confirm it. It is never tagged `scan`. Golden examples: P03
socket (photo-inferred, "confirm physically"), B02 tuft-slot depth, OD core tube Ø16, M02
module and pressure angle (`references/intent-rules.md` §6). Tell verify which features are
inferred, so their deviation is reported with that reason rather than chased.

### 10. CHK-CLUSTER: an unexplained coherent cluster is real until disproven (SYN C12)

Look for scan material the feature list doesn't explain: on-axis spikes, material above the
expected top, density in the (r,z) map with no planned feature.

`python scripts/sections.py cluster --mesh <scan> --z-band lo,hi --r-band lo,hi --top-band <noise-scale> --out measure/figures/cluster_<n>.json`

- **One connected component with a flat top is a feature.** Cross-check the profile photos,
  then add it to the params and record a CHK-ENUM finding for intake. On P03 it1, a real feature
  (a drive stem) was wrongly dismissed as occlusion; a later QA pass proved it real from a large,
  coherent, flat-topped cluster that a profile photo had already shown, and it cost an iteration
  (`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/PARAM_TABLE.md:4-6,43`; see
  `analysis/golden/OOM-P03.md` for the specifics).
- Dismiss a cluster as an artefact only with evidence: many small components, no flat top, and
  photos showing nothing there. Record that evidence in the check note.

### 11. CHK-FRAME: angles only in the frozen datum frame (SYN B10)

- Re-measure every angle on the aligned scan. **Never copy an angle from the intake card**:
  its frame or sign may differ. On B02, two angles recorded at intake used a different sign
  convention than the frozen datum frame, and copying them forward would have been wrong
  (`OOM-B02/6_RE_work/PARAM_TABLE.md:49,72-74`, `OOM-B02/2_mesh_cleaned/alignment.json#notes`;
  see `analysis/golden/OOM-B02.md` for the values in each frame).
- The scripts report θ CCW about +Z from +X in the datum frame. State that in
  `params.json#frame`. If an intake angle disagrees beyond the measured spread, record a
  CHK-FRAME finding with both values.

### 12. Declare simplifications with their deviation cost (SYN C14)

Wherever the model will be simpler than the scan (a single cylinder over a taper, a mean path
over free-state droop, a plane over a wave), measure the cost on the scan and add a
`simplifications[]` entry. Use the fit residual or the per-instance spread. Golden examples
(coil path, arm path, ramp geometry) are in `references/intent-rules.md` §7 with pointers to the
recorded costs, not restated here. An undeclared simplification becomes an unexplained band
miss at verify — see `analysis/golden/OD-H12.md` for a worked case.

### 13. Write, validate, render, hand off

1. Write `measure/params.json`: header per run-contract §2, and a row per parameter with
   `value, unit, measured, rule, source, estimator, uncertainty_mm, evidence, critical`
   (`references/param-table-schema.md`). Record `checks` for CHK-COUNT, CHK-ACHIEVABLE,
   CHK-CLUSTER and CHK-FRAME.
2. `python scripts/param_table.py measure/params.json --alignment intake/alignment.json`.
   Exit 1 lists every violation, and the table is not written until it passes.
3. Give the orchestrator: the path to `params.json`, and the lists of struck readings,
   critical uncalipered values with their re-run triggers, inferred features and open
   findings. The rebuild may not introduce a number that is not in `params.json`.

## Failure checks

| Check | Fails when | Do |
|---|---|---|
| **CHK-COUNT** | <3 stations; stations disagree; the FFT-dominant order is not a residual local minimum; exact-CAD residual method and FFT disagree | Add or move stations (strictly interior), narrow the `--r-band`/`--z-half` to the feature, check coverage gaps. If it still disagrees, record `finding`, keep the count open, and ask for an operator count. Never fall back to crest peaks. P03 tread gives FFT 49/49/51 on the partial scan (`references/validation.md`). |
| **CHK-ACHIEVABLE** | A reading lies outside the simulated two-jaw window, beyond the measured scan offset `d` | Strike it (proof + hook), build from the scan, and record the check as `finding` with the struck id. Below the window but within `d` (or `d` unknown), or above the window with gaps: mark it unproven and ask. |
| **CHK-CLUSTER** | A coherent cluster is not in the feature list | Treat it as a feature: measure it, add it, and send CHK-ENUM back to intake. |
| **CHK-FRAME** | An angle comes from another frame or sign, or no frame is stated | Re-measure in the datum frame and record both values. |
| param_table errors | Missing provenance; rounding beyond noise; a snap on a critical scan value; a scan count without order/FFT | Fix the row. Never hand-edit PARAM_TABLE.md. |

When a gate later sends the job back (REVISE), re-measure **only the flagged feature** and
change the fewest parameters possible. Log `old → new` with the reason in the row's `note`.
The orchestrator moves the previous `measure/` to `_itN_SUPERSEDED/` (CHK-SUPERSEDED).
B02 it1→it2 changed exactly one parameter (`analysis/golden/OOM-B02.md` §8). The loop limit
is 3 per part (`RE_SPEC.md:248-250`), and the orchestrator counts it.

## Scripts

| Script | Provenance | Purpose |
|---|---|---|
| `scripts/sections.py` | DRM `align.py`/`overlay.py`, B02 `50_overlays_it2.py`, `40_verify.py` | planar (+ loop tracks), radial, maps, rtheta, cluster |
| `scripts/fits.py` | DRM `align.py:fit_circle`, `datum.py:ransac_plane`; B02 `q03_datum_full.py` IRLS | circle, circle-irls, line, plane, plane-ransac, with residuals and a second estimator |
| `scripts/pattern_count.py` | **new code**; method from M02 `qa_report.json` and P03 PARAM_TABLE FFT | rotational-order count, CHK-COUNT |
| `scripts/sim_caliper.py` | B02 `q10_solid_tess_tier1.py:jaws/densify/zsec` | two-jaw window, CHK-ACHIEVABLE; shared with stl-re-verify for Tier-1 |
| `scripts/param_table.py` | new | validate params.json, render PARAM_TABLE.md |
| `scripts/sketchfit.py` | new (real run dreame_mop_bottom_cover it2) | design-intent line/arc sketch fitted to an averaged section; the rebuild extrudes it once (see rebuild SKILL Step 5) |
| `scripts/common.py` | new helpers; `densify` from B02 | header, hashing, alignment, sections |

All scripts are deterministic: fixed seeds, and no wall-clock value except the `created`
provenance field. Needs: numpy, scipy, trimesh, shapely; matplotlib is optional (PNG maps).
Golden-number reproduction and its discrepancies: `references/validation.md`.

## Heuristics (single-case) used here

- Gear parameter handling (heuristic, n=1: M02): `references/gears.md`.
- IRLS Cauchy scale 0.30 mm (heuristic, n=1: B02 audit).
- Scan dilation on thin sections treated as a local offset, measured per scan and passed to
  `sim_caliper.py --scan-offset` (heuristic, n=1: B02 F10, orchestrator decision B2).
- Standard-size snap (doctrine, n=0 goldens).

## Open questions (do not resolve silently)

- **B02 scan window.** This skill's port of the two-jaw window computation reproduces the
  golden's CAD-based window exactly, but on the full-res scan it gives a wider window than the
  one recorded in the golden report. The explanation: the golden's analytic argument
  (`VERDICT.md:64-66`) left one recess feature out of the envelope, while a real caliper section
  would see it. That changes a flagged reading's classification (struck vs. unproven) under
  orchestrator decision B2. The exact numbers and the margin math are worked in
  `references/validation.md` and `analysis/golden/OOM-B02.md` — read those, not this summary,
  before relying on a specific value.
- Photo-transcribed uncertainty for P03 is not stated (`analysis/golden/OOM-P03.md`
  Questions). This skill applies B02's ±0.1 to all photo readings.
- No golden recorded a residual tolerance for counting on **scans**. The scan rule (FFT
  dominance + residual local minimum at ≥3 stations) is validated here on P03 only
  (inspection, decimated scan).
- The golden P03 FFT magnitudes (F[8] = 144.6) cannot be compared, because the signal and its
  normalisation are not recorded.
