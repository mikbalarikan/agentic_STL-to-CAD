# Intent rules: snap, keep or declare

Every parameter ends in exactly one of three states. **Snap**: the chosen value differs from
the estimate by an allowed rule. **Keep**: the chosen value is the estimate. **Declare**: the
value is not measured (or is simplified), and the table says so and names the cost. This file
gives the decision table and, for each row, a pointer to the golden precedent that established
it — read the cited file if you need the actual figures; do not expect this table to restate
them (`analysis/SYNTHESIS.md` §4).

## 1. Authority first (who owns the number)

`baseline/oomwoo-re-pipeline/RE_SPEC.md:86-98`:

1. **Caliper / operator spec** for every dimension it covers. Use it directly
   (`rule: caliper-direct`), but only after CHK-ACHIEVABLE (§4).
2. **Scan** for form and topology: positions, profiles, blends, and anything a caliper can't
   reach.
3. **Photos** for intent: what the part is, functional vs cosmetic, expected symmetry, real
   feature vs artefact. A photo is never a dimension, except a *photo-transcribed caliper
   reading* (§3).

| Situation | Do | Golden precedent (see the cited file for the actual values) |
|---|---|---|
| Operator/caliper value disagrees with a scan-derived candidate | The operator value governs. Record the scan candidate in `measured` or a note. | M02: an operator-specified tooth count and diameter replaced a wrong scan-derived candidate (`golden-examples/M02-02-03_watertight-design-intent/DESIGN_NOTES.md:5`) |
| Caliper and scan differ by more than noise on one dim | Caliper, used directly. Do **not** scale the whole part: a non-uniform scan/caliper gap is local scanner dilation, not scale (CHK-SCALE belongs to intake). | B02 cup bore: caliper vs scan disagreed by more than noise, and several ratios across the part were non-uniform, so no global scale was applied (`OOM-B02/2_mesh_cleaned/alignment.json#scale_correction_note`); P03 had a similar single-dimension gap (`analysis/golden/OOM-P03.md` §5) |
| Caliper value at one station, scan gives the shape | Caliper at the station plus the scan shape, shifted by the difference. Log both. | B02 arm thickness: one caliper station plus the scan's taper shape, shifted to match (`OOM-B02/6_RE_work/PARAM_TABLE.md:41,97`) |
| Several reads of one dim | `mean-of-n`; list every read in `measured`. | P03 averaged several independent reads of the same feature (`analysis/golden/OOM-P03.md` §5) |
| No caliper at all (scan-only job) | Scan authority throughout. Say so in the table header. | DRM caps, OD pump (`analysis/golden/dreame_brush-caps.md` §4, `analysis/golden/OD-H12.md` §4) |

## 2. Rounding and snapping (scan values)

| Case | Rule | Allowed move | Precedent (see cited file for values) |
|---|---|---|---|
| Scan estimate, noise known | `round-within-noise` | \|chosen − estimate\| ≤ `scan_noise_mm` from `intake/alignment.json` | DRM rounded several small scan-estimate moves inside its measured noise (`golden-examples/dreame_brush-caps/README.md:23,81`); B02 did the same for a cup-floor dimension (`OOM-B02/6_RE_work/PARAM_TABLE.md:57`) |
| Scan estimate is a range (several stations, sub-features) | `round-within-noise` or `keep-measured`, chosen **inside the measured range** | Chosen ∈ [min − noise, max + noise] | B02 rounded a draft angle and a flat half-angle inside their measured spreads; DRM rounded a fillet radius the same way (`analysis/golden/OOM-B02.md` §5, `analysis/golden/dreame_brush-caps.md` §5) |
| Noise not known | **No rounding.** Keep the estimate, then get the noise floor (§6 of SKILL.md). | none | M02 used operator values verbatim (`analysis/golden/M02-02-03.md` §5) |
| Fixed 0.1 / 0.5 / 1.0 mm grid | **Never.** Dropped baseline rule. | — | No golden did it (`analysis/SYNTHESIS.md` §3) |
| Caliper value within ±0.1 mm of a standard size (drill, thread, bearing) | `std-size-snap`, **(heuristic, doctrine only)**: `RE_SPEC.md:92` allows it, but no golden applied it (`analysis/SYNTHESIS.md` §6; `analysis/golden/OOM-B02.md` §5 "No standard-size snap … was applied") | ≤ 0.1 mm, caliper sources only | none |
| **Critical interface without a caliper** (drive socket, bearing seat, snap hook) | `keep-measured` + `critical: true` + `rerun_trigger`. **Never snap it**, not even to an "obvious" standard size. | 0 | B02 held a critical hex-across-flats interface at its scan fit rather than snapping to a nearby standard size, with a rerun trigger for the first real caliper reading (`OOM-B02/6_RE_work/VERDICT.md:28-30`, `PARAM_TABLE.md:48`) |
| Angles | Round only inside the measured spread of the sub-features. State the frame. | as above | B02 rounded an angle to the value where several independent sub-feature estimates converged, inside their measured spread (`PARAM_TABLE.md:49,78`) |

## 3. Photo-transcribed caliper readings

A caliper value read off a photo of the display is a real reading only when **all** of these hold
(`analysis/golden/OOM-B02.md` §12.3; `OOM-B02/5_reference/MEASUREMENTS.md:19-24`):

- `source: caliper-photo`, and `evidence` holds the photo id (P03 lists one per value:
  `golden-examples/OOM-P03_mop-pad-bracket/5_reference/MEASUREMENTS.md:78-98`).
- `attribution` names who confirmed which feature and jaw placement. Without it the reading is
  unused (B02 left several readings unused for exactly this reason: `MEASUREMENTS.md:91-116`).
- `uncertainty_mm ≥ 0.1` (effective, screen parallax plus inferred jaw placement), never the
  instrument's ±0.02 (`MEASUREMENTS.md:24`; `baseline/oomwoo-re-pipeline/TRACKER.md:13`). P03 did
  not state its uncertainty; that is a record gap, not a precedent (`analysis/golden/OOM-P03.md`
  Questions).
- It passed CHK-ACHIEVABLE (§4).

## 4. CHK-ACHIEVABLE: can the scan produce this reading?

Earned by a B02 lobed feature. A caliper reads a **support width**, not a radius, on a
non-round cross-section, so a two-jaw reading applied directly as a radius parameter can be
geometrically unachievable. On B02, exactly this happened: a photo-transcribed reading was
applied as a radius parameter, the built solid re-measured well outside the Tier-1 band, and the
result was REVISE — even though the impossibility had already been flagged and the value was
applied anyway "per the rebuild brief" (`OOM-B02/6_RE_work/PARAM_TABLE.md:108-121`,
`VERDICT.md:58-74`; `analysis/golden/OOM-B02.md` §8). **A flagged impossibility is a stop, not a
note.** The actual reading, the applied parameter, the achievable window and the rebuilt
solid's deviation are in the cited files; they are not restated here.

Procedure: run `scripts/sim_caliper.py` on the aligned scan at the reading's station, in the
jaw mode the photo shows (outside or inside). Inside-jaw mode needs `--r-band` to isolate the
bore section: an open scan section has no single closed "innermost loop" to pick, so the
script pools the in-band points and builds an inner (min-radius) envelope, the dual of the
outer envelope, with its own real angular coverage (orchestrator decision B1, 2026-09-25 —
inside-jaw mode previously picked the smallest-max-radius polyline fragment and assumed full
coverage, which wrongly struck a B02 reading that the golden had in fact accepted; the fixed
mode reports it achievable, `window_min`/`window_max` computed on the full-res scan).

A caliper reading can also sit legitimately below the scan window when the scan itself reads
oversize at that station: on B02, one arm-width caliper reading read measurably below the scan
mean at the same station (`MEASUREMENTS.md:61`, `PARAM_TABLE.md:41`, "Scanner dilation on thin
sections (intake R6)"). `--scan-offset d` carries that **measured, per-scan** dilation — the
largest scan-minus-caliper gap among the *other* calipered dims of the same scan — into the
classification (orchestrator decision B2, 2026-09-25). `d` is never a constant and is never
invented: omit it when no other caliper exists on this scan.

| Result | Action |
|---|---|
| reading ∈ [min − u, max + u] | Use it (`caliper-direct`). |
| reading < min − u − d | **Strike.** Add a `struck[]` entry with the window, the proof, and a re-measure hook. Build the feature from the scan (`source: scan`). The proof holds even with occlusion gaps, because a partial outline can only under-read widths. |
| min − u − d ≤ reading < min − u | **Unproven (within the measured scan dilation).** Do not build to it, do not strike it. Ask for a jaw-placement photo or re-measure. If `d` is unknown (no other calipers on this scan), any below-window reading is unproven, not struck. |
| reading > max + u, full coverage | Strike, as above (`d` does not apply on this side: dilation only explains an under-reading caliper, not an over-reading one). |
| reading > max + u, coverage < 1 | **Unproven.** The missing arc may hold the extreme. Ask for a re-measure or a jaw-placement photo; do not build to it yet. |

The B02 it2 ruling is the template: the flagged reading was struck from Tier-1 and its parameter
reverted to scan authority, with a re-measure hook for if the caliper reading turns out to have
been taken a different way — exactly one parameter changed between iterations
(`PARAM_TABLE.md:117-121`; `analysis/golden/OOM-B02.md` §8). On a fresh reproduction of this
part (`references/validation.md`), the computed margin below the full-res-scan window came out
smaller than the measured scan dilation on the same scan, which would classify that reading as
**unproven** rather than struck — see `references/validation.md` for the open question this
leaves about how the golden computed its own (narrower) scan window, and for the actual figures.

## 5. Symmetry, equal pitch, identical instances

| Measured scatter | Do | Precedent (see cited file for values) |
|---|---|---|
| Within noise | Enforce (`rule: symmetry`), and record `scatter_mm`. | P03: a repeated feature pattern matched an exact even angular spacing within noise (`OOM-P03/6_RE_work/PARAM_TABLE.md:38,59`) |
| Beyond noise, but the design intent is clear and a pattern test supports it | Enforce, and give `scatter_note` with the reason and the residual it leaves. | B02 arms: measured spacing scattered beyond noise but a rotational self-registration test supported equal spacing, so it was enforced with a declared residual (`analysis/golden/OOM-B02.md` §5); DRM equalised a measured PCD spread the same way, declared as an assumption (`analysis/golden/dreame_brush-caps.md` §5) |
| Beyond noise, intent not clear | `keep-measured`, and declare the asymmetry. | DRM's snap-leg angles were kept unequal rather than symmetrised; OD's coil and screw centres were likewise kept as measured, not forced onto a symmetric layout (`golden-examples/OD-H12_delonghi-dedica-pump/README.md:51`) |

Repeated features share one parameter set unless the measurement shows a difference beyond
noise (facet-film T27, `analysis/baseline/facet-film-transferable.md`). Mirror only for
intent, and still measure both sides and report the delta (T25).

## 6. Provenance for unscanned or occluded geometry

Never tag unscanned geometry `scan`. Use `photo-inferred`, `standard` or `assumed`, with
`measured: null` and a note on what would confirm it (facet-film T7/T8).

| Precedent | Tag |
|---|---|
| P03 has a bridged interior feature the scanner could not resolve; it was photo-set, flagged "confirm physically", and its deviation was excluded from the verdict with a reason | photo-inferred (`OOM-P03/6_RE_work/PARAM_TABLE.md:44`, `VERDICT.md:55`) |
| B02 has occluded interior geometry (an interior slot depth, a hole's inner end) | photo-inferred, not gated (`OOM-B02/6_RE_work/PARAM_TABLE.md:83-85,102`) |
| OD has unseen internal bores/depths | assumed "design-intent guess", declared (`analysis/golden/OD-H12.md` §5) |
| M02's gear parameters beyond the operator-specified ones (profile, phase, fillet, backlash) | assumed / standard, explicitly declared as not invented (`golden-examples/M02-02-03_watertight-design-intent/README.md:21-27`) |

## 7. Declared simplifications (C14)

When the model uses a simpler form than the scan shows, add a `simplifications[]` entry with
the deviation cost measured on the scan. Otherwise the verify skill finds the cost later as an
unexplained band miss.

| Precedent | Simplification | Cost declared (see cited file for the value) |
|---|---|---|
| OD coil | one cylinder over a tapered/wavy region | form deviation, part of the explained p95 miss (`OD-H12/README.md:35-36`) |
| B02 arms | a mean z-path over free-state droop, per arm | per-arm deviation from the mean path (`OOM-B02/6_RE_work/50_overlays_it2.py:74-78`) |
| DRM snap ramp | one plane over a small undulation | form deviation (`analysis/golden/dreame_brush-caps.md` §5) |

## 8. The counter-example: OD-H12

OD kept most values unsnapped at fine resolution, which was good. But it produced **no
measured→chosen log**: final values only, and at least one internal parameter conflict between
two of its own documents (a tooth/parameter count in one place vs another, a hub diameter in a
docstring vs the params file — see `analysis/golden/OD-H12.md` §5, Questions, for what
conflicted). The resulting band miss could then be explained only per region, not per
parameter. Every row needs `measured`, `rule`, `source` and `estimator`. `scripts/param_table.py`
refuses a table without them.
