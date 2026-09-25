# Intent rules: snap, keep or declare

Every parameter ends in exactly one of three states. **Snap**: the chosen value differs from
the estimate by an allowed rule. **Keep**: the chosen value is the estimate. **Declare**: the
value is not measured (or is simplified), and the table says so and names the cost. This file
gives the decision table and the golden precedent for each row. The numbers are the only ones
allowed (`analysis/SYNTHESIS.md` §4); everything else is "the golden used X".

## 1. Authority first (who owns the number)

`baseline/oomwoo-re-pipeline/RE_SPEC.md:86-98`:

1. **Caliper / operator spec** for every dimension it covers. Use it directly
   (`rule: caliper-direct`), but only after CHK-ACHIEVABLE (§4).
2. **Scan** for form and topology: positions, profiles, blends, and anything a caliper can't
   reach.
3. **Photos** for intent: what the part is, functional vs cosmetic, expected symmetry, real
   feature vs artefact. A photo is never a dimension, except a *photo-transcribed caliper
   reading* (§3).

| Situation | Do | Golden precedent |
|---|---|---|
| Operator/caliper value disagrees with a scan-derived candidate | The operator value governs. Record the scan candidate in `measured` or a note. | M02: operator 30T / Ø19.05 replaced the 27T / Ø21.75 scan candidate (`golden-examples/M02-02-03_watertight-design-intent/DESIGN_NOTES.md:5`) |
| Caliper and scan differ by more than noise on one dim | Caliper, used directly. Do **not** scale the whole part: a non-uniform scan/caliper gap is local scanner dilation, not scale (CHK-SCALE belongs to intake). | B02 cup bore 20.75 vs scan 20.93; ratios 0.984–0.996 non-uniform → no scale (`OOM-B02/2_mesh_cleaned/alignment.json#scale_correction_note`); P03 ENV-D1 127.54 vs 127.84 (`analysis/golden/OOM-P03.md` §5) |
| Caliper value at one station, scan gives the shape | Caliper at the station plus the scan shape, shifted by the difference. Log both. | B02 arm thickness F11: 4.07, taper = scan shape shifted −0.036 (`OOM-B02/6_RE_work/PARAM_TABLE.md:41,97`) |
| Several reads of one dim | `mean-of-n`; list every read in `measured`. | P03 hex AF 13.96/13.92/13.97 → 13.95; wall 3.25/3.28 → 3.27 (`analysis/golden/OOM-P03.md` §5) |
| No caliper at all (scan-only job) | Scan authority throughout. Say so in the table header. | DRM caps, OD pump (`analysis/golden/dreame_brush-caps.md` §4, `analysis/golden/OD-H12.md` §4) |

## 2. Rounding and snapping (scan values)

| Case | Rule | Allowed move | Precedent |
|---|---|---|---|
| Scan estimate, noise known | `round-within-noise` | \|chosen − estimate\| ≤ `scan_noise_mm` from `intake/alignment.json` | DRM: 0.01–0.05 mm moves inside ≈0.02–0.05 noise (`golden-examples/dreame_brush-caps/README.md:23,81`); B02 cup floor 2.456–2.459 → 2.455 (`OOM-B02/6_RE_work/PARAM_TABLE.md:57`) |
| Scan estimate is a range (several stations, sub-features) | `round-within-noise` or `keep-measured`, chosen **inside the measured range** | Chosen ∈ [min − noise, max + noise] | B02 draft 7.1–10.4° → 8.0°, flat half-angle −17…+18 → 16°; DRM fillet ρ 1.05–1.19 → R1.15 (`analysis/golden/OOM-B02.md` §5, `analysis/golden/dreame_brush-caps.md` §5) |
| Noise not known | **No rounding.** Keep the estimate, then get the noise floor (§6 of SKILL.md). | none | M02 used operator values verbatim (`analysis/golden/M02-02-03.md` §5) |
| Fixed 0.1 / 0.5 / 1.0 mm grid | **Never.** Dropped baseline rule. | — | No golden did it (`analysis/SYNTHESIS.md` §3) |
| Caliper value within ±0.1 mm of a standard size (drill, thread, bearing) | `std-size-snap`, **(heuristic, doctrine only)**: `RE_SPEC.md:92` allows it, but no golden applied it (`analysis/SYNTHESIS.md` §6; `analysis/golden/OOM-B02.md` §5 "No standard-size snap … was applied") | ≤ 0.1 mm, caliper sources only | none |
| **Critical interface without a caliper** (drive socket, bearing seat, snap hook) | `keep-measured` + `critical: true` + `rerun_trigger`. **Never snap it**, not even to an "obvious" standard size. | 0 | B02 hex AF 7.358 held, "deliberately NOT intent-snapped to 7.0 or 7.5 … One caliper reading on F01 should trigger a re-run" (`OOM-B02/6_RE_work/VERDICT.md:28-30`, `PARAM_TABLE.md:48`) |
| Angles | Round only inside the measured spread of the sub-features. State the frame. | as above | B02 SAF-1 θ: nub 57.6 / recess 60.0 / boss 61.5 → 59.0, which coincides with the hex flat normal 59.04° (`PARAM_TABLE.md:49,78`) |

## 3. Photo-transcribed caliper readings

A caliper value read off a photo of the display is a real reading only when **all** of these hold
(`analysis/golden/OOM-B02.md` §12.3; `OOM-B02/5_reference/MEASUREMENTS.md:10,19-24`):

- `source: caliper-photo`, and `evidence` holds the photo id (P03 lists one per value:
  `golden-examples/OOM-P03_mop-pad-bracket/5_reference/MEASUREMENTS.md:78-98`).
- `attribution` names who confirmed which feature and jaw placement. Without it the reading is
  unused. B02 kept D-09/10/12 unused (`MEASUREMENTS.md:91-116`).
- `uncertainty_mm ≥ 0.1` (effective, screen parallax plus inferred jaw placement), never the
  instrument's ±0.02 (`MEASUREMENTS.md:10`; `baseline/oomwoo-re-pipeline/TRACKER.md:13`). P03 did
  not state its uncertainty; that is a record gap, not a precedent (`analysis/golden/OOM-P03.md`
  Questions).
- It passed CHK-ACHIEVABLE (§4).

## 4. CHK-ACHIEVABLE: can the scan produce this reading?

Earned by B02 F06. The skirt is 3-lobed, and a two-jaw caliper reads a support width, not a
radius. The photo reading 24.84 was applied as `SKIRT_R_FLAT = 12.420`. The built solid
re-measured 25.487: Δ +0.647, out of the ±0.15 Tier-1 band, and the result was REVISE
(`OOM-B02/6_RE_work/PARAM_TABLE.md:108-121`, `VERDICT.md:58-74`). It1 had already flagged
the impossibility and applied the value anyway "per the rebuild brief"
(`analysis/golden/OOM-B02.md` §8). **A flagged impossibility is a stop, not a note.**

Procedure: run `scripts/sim_caliper.py` on the aligned scan at the reading's station, in the
jaw mode the photo shows (outside or inside).

| Result | Action |
|---|---|
| reading ∈ [min − u, max + u] | Use it (`caliper-direct`). |
| reading < min − u | **Strike.** Add a `struck[]` entry with the window, the proof, and a re-measure hook. Build the feature from the scan (`source: scan`). The proof holds even with occlusion gaps, because a partial outline can only under-read widths. |
| reading > max + u, full coverage | Strike, as above. |
| reading > max + u, coverage < 1 | **Unproven.** The missing arc may hold the extreme. Ask for a re-measure or a jaw-placement photo; do not build to it yet. |

The B02 it2 ruling is the template: "F06 is STRUCK from Tier-1 and `SKIRT_R_FLAT` reverts to
scan authority 12.550 … re-measure hook: if 24.84 was a real skirt dimension taken some other
way … this must be re-run" (`PARAM_TABLE.md:117-121`). Exactly one parameter changed between
iterations (`analysis/golden/OOM-B02.md` §8).

## 5. Symmetry, equal pitch, identical instances

| Measured scatter | Do | Precedent |
|---|---|---|
| Within noise | Enforce (`rule: symmetry`), and record `scatter_mm`. | P03 kidneys: 8 at exact 45° (`OOM-P03/6_RE_work/PARAM_TABLE.md:38,59`) |
| Beyond noise, but the design intent is clear and a pattern test supports it | Enforce, and give `scatter_note` with the reason and the residual it leaves. | B02 arms 120.42/120.38/119.20 → 120.00, 3-fold self-registration test (`analysis/golden/OOM-B02.md` §5); DRM cup PCD 8.81–9.02 → 8.90 "equalise", declared as an assumption (`analysis/golden/dreame_brush-caps.md` §5) |
| Beyond noise, intent not clear | `keep-measured`, and declare the asymmetry. | DRM snap legs kept at 60°/150°/−60° (unequal); OD coil centre (−0.2, 0.1) and screw centres not symmetrised (`golden-examples/OD-H12_delonghi-dedica-pump/README.md:51`) |

Repeated features share one parameter set unless the measurement shows a difference beyond
noise (facet-film T27, `analysis/baseline/facet-film-transferable.md`). Mirror only for
intent, and still measure both sides and report the delta (T25).

## 6. Provenance for unscanned or occluded geometry

Never tag unscanned geometry `scan`. Use `photo-inferred`, `standard` or `assumed`, with
`measured: null` and a note on what would confirm it (facet-film T7/T8).

| Precedent | Tag |
|---|---|
| P03 square drive socket 5.5 × 2.5: the scanner bridged it. Photo-set, flagged "confirm physically", its deviation excluded from the verdict with a reason | photo-inferred (`OOM-P03/6_RE_work/PARAM_TABLE.md:44`, `VERDICT.md:55`) |
| B02 tuft-slot depth, SAF hole inner end: interiors occluded | photo-inferred, not gated (`OOM-B02/6_RE_work/PARAM_TABLE.md:83-85,102`) |
| OD core tube Ø16, nozzle/barb bore depths: not visible | assumed "design-intent guess", declared (`analysis/golden/OD-H12.md` §5) |
| M02 module 0.6, PA 20°, phase 0, no backlash/fillet | assumed / standard; "No unmeasured hub projection, relief, chamfer, backlash, profile shift or root fillet was invented" (`golden-examples/M02-02-03_watertight-design-intent/README.md:21-27`) |

## 7. Declared simplifications (C14)

When the model uses a simpler form than the scan shows, add a `simplifications[]` entry with
the deviation cost measured on the scan. Otherwise the verify skill finds the cost later as an
unexplained band miss.

| Precedent | Simplification | Cost declared |
|---|---|---|
| OD coil | one cylinder Ø47.30 over r 23.50–23.84 (taper/wave) | ±0.1 mm form, part of the explained p95 miss (`OD-H12/README.md:35-36`) |
| B02 arms | 3-arm mean z-path over free-state droop | arm 1 +0.74 / arm 3 −0.51 mm (`OOM-B02/6_RE_work/50_overlays_it2.py:74-78`) |
| DRM snap ramp | one plane over a ±0.07 undulation | ±0.07 mm (`analysis/golden/dreame_brush-caps.md` §5) |

## 8. The counter-example: OD-H12

OD kept most values unsnapped at 0.02–0.05 mm resolution, which was good. But it produced
**no measured→chosen log**: final values only, 104 vs 105 parameter-count conflict, flange hub
Ø24.4 in the docstring vs Ø24.1 in params (`analysis/golden/OD-H12.md` §5, Questions). The
band miss (p95 0.448) could then be explained only per region, not per parameter. Every row
needs `measured`, `rule`, `source` and `estimator`. `scripts/param_table.py` refuses a table
without them.
