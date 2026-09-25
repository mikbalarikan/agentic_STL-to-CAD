# Review: `skills/stl-re-intake-datum`

VERDICT: REVISE

Reviewer: independent (did not write this skill). Scope: `SKILL.md`, `references/*` (3 files),
`scripts/{intake,datum_fit,align}.py`. Extra focus: the datum math, `alignment.json` against
run-contract §3/§11, the `align.py` STOP rule (QUESTIONS §C), and a real replay on the DRM screw
decimated scan.

Counts: 1 BLOCKER, 2 MAJOR, 8 MINOR, 2 NIT.

## Findings

| id | sev | file:line | finding | evidence | concrete fix |
|---|---|---|---|---|---|
| B1 | BLOCKER | `scripts/align.py:295-305`, `scripts/datum_fit.py:247-254`, `references/datum-cookbook.md:152-156` | The axis-primary path always ends in STOP. `primary.fit_rms_mm` is the rms distance of the face-normal lines from the fitted axis. That is roughly radius × normal-angle noise, and it is compared with a plane-rms noise floor (a different metric). SKILL.md 8.1 and cookbook §3 document this path as supported (OD class). | Synthetic test: open cylinder r = 10 plus flange, isotropic triangles (0.19 mm edges), vertex noise σ = 0.01 mm, tilted 11.5°. `datum_fit.py axis` recovers the direction to 0.007°. Then `align.py` gives **STOP, "primary fit rms 0.9017 > noise floor 0.0058"**, exit 2 (max 4.02 mm). The perfect faceted cylinder already gives line_dist 0.069. | In `align.py` axis branch: (1) require `crop_radius`/`crop_point` (one cylinder). (2) Compute `rad = ‖(C_sel − a) − ((C_sel − a)·d) d‖` for the selected face centres, then `res = rad − median(rad)`, and set `fit_rms_mm = rms(res)`, `fit_max_mm = max|res|`, `fit_metric = "radial residual of cropped faces about the fitted axis"`. (3) Compare it with `noise_secondary` (circle noise), not `noise`. If `noise_secondary` is absent, add the same "not compared" finding used for the secondary (align.py:358). (4) Keep `line_dist` only as the diagnostic `normal_line_dist`. Update cookbook §3 lines 152-156 to match. |
| M1 | MAJOR | `scripts/align.py:247-250, 268, 294, 427-443` | `scale_factor` is not folded into `matrix_4x4`. The mesh is pre-scaled by S, and T is built on the scaled mesh, so the matrix maps *scaled* raw → datum. The note at :443 says so. Run-contract §11 says scale is folded in (raw → scaled datum frame). `stl-re-measure-intent/scripts/common.py:64-82` applies `matrix_4x4` to the raw scan without a scale, so with a UNIFORM CHK-SCALE the measure stage reads unscaled dimensions while `aligned_work.stl` is scaled. The failure is latent (no golden scaled), but it is a hand-off break. | Code read. Contract §11 lines 142-148. `export_frames.py:115-117` aborts on scale ≠ 1, which does not protect measure. | At align.py:428 write `"matrix_4x4": (T @ S).tolist()` and change the note to "maps the RAW scan to the datum frame; scale_factor is folded in (run-contract §11)". `aligned_work.stl` is unchanged. Add a one-line check: `apply(T@S, raw) ≈ mc`. |
| M2 | MAJOR | `scripts/align.py:120-142, 334`; `SKILL.md:236`; `references/datum-cookbook.md:62` | The CHK-TILT estimator pools all origin features into one line with one intercept. The stderr comes only from residual scatter, so it ignores between-feature centre bias and the shape bias of non-circular features (double-D Kåsa). On DRM the per-feature tilts point in opposite directions. SKILL.md states "DRM screw measured 0.72° ± 0.11°" as a fact. | DRM replay (decimated, same z windows): double-D alone **0.716° ± 0.109° at 117°** (reproduces the skill). Counterbore F08 alone **2.82° ± 0.56° at −111°**. Both pooled (34 stations, z −5.0…−0.1): **0.52° ± 0.08° at −9.8°**. The tilt vectors differ by about 1.1°, 10× the quoted stderr. The feature mean centres differ by 0.04 mm, which the single intercept reads as tilt. Cookbook row 62 "0.71° ± 0.12° (counterbore + double-D, 19 stations over 4.6 mm)" cannot be reproduced: its spec is not given. | (1) In `tilt_from_stations`, fit a common slope with a per-feature intercept (design matrix = one-hot(feature) ‖ z) and pass `feature` in. (2) Add `per_feature: [{feature, value, stderr_deg, direction_deg, z_span_mm}]` for every feature with ≥ 3 stations. (3) Set `resolvable: false`, and make the CHK-TILT note "not resolvable", when two per-feature tilt vectors differ by more than their combined 1σ stderr (label it heuristic). (4) Replace SKILL.md:236 with: "DRM screw: double-D 0.72° ± 0.11° (dir 117°) vs counterbore 2.8° ± 0.56° (dir −111°), so tilt is not resolvable from these features. The golden assumed 0; record it as not resolvable." Fix cookbook row 62 the same way and give the spec used. |
| m1 | MINOR | `scripts/datum_fit.py:178-190`; `scripts/align.py:304-305` | The primary STOP check is self-referential when the noise floor is measured on the primary with the same parameters (DRM: `fit_rms_mm == noise == 0.006902104381003847`). Also, rms and max are trimmed to \|d\| < 2·tol, so `fit_max_mm` is structurally ≤ ~0.1 mm. On QUESTIONS §C: enforcing rms only is the sensible reading. RE_SPEC's "RMS + max" against noise would have STOPped the accepted golden (max 0.055 > rms 0.0072), and a trimmed max says little. The trimming should be visible, though. | DRM run output. Code read (`sel2 = |d| < 2*tol`). | Add `fit_untrimmed: {rms, p95, max}` over the peak-bin band `sel` and `inlier_frac` to `primary`. When `noise.method` mentions the primary's `desc`, append the finding "primary STOP check is self-referential (noise measured on the primary itself)". In SKILL.md Non-negotiable 5, add: "rms is gated, max is reported (RE_SPEC says RMS + max; see QUESTIONS §C)". |
| m2 | MINOR | `SKILL.md:103-186` (steps 3b, 4, 5, 6 vs 8) | The step order cannot be run cold. Step 3's circle noise, step 4's coverage, step 5's radial bands and step 6's "Scan says" all need `aligned_work.stl`/`alignment.json`, which come from step 8. `noise_secondary` also needs a second `align.py` pass. | Procedure text. | Insert under "## Procedure": "Execution order: 1 → 2 → 3 (plane noise) → 8 (first pass, no `noise_secondary`) → 3 (circle noise on `aligned_work.stl`) → 8 (second pass with `noise_secondary`) → 4 → 5 → 6 → 7 → 9." |
| m3 | MINOR | `scripts/align.py:394-425` | With zero spec landmarks and an axis primary (no auto landmark), `all([]) == True`, so the status is OK with no sanity check at all. SKILL.md 8.6 asks for 3–5. | Synthetic axis run: `sanity_landmarks: []`. | If `len(spec.get("landmarks", [])) == 0`, append the finding "no sanity landmarks supplied (SYNTHESIS B11)". |
| m4 | MINOR | `SKILL.md:101`; `scripts/align.py:423-424` | `intake.py scale` writes `decision` strings (UNIFORM / NO SCALE / FLAG). `align.py` expects `chk_scale` as `{ran, result, note}`. The mapping is unspecified. | Code read. | Accept `"chk_scale": {"from": "intake/scale.json"}` in align.py and map UNIFORM or NO SCALE → `pass` and FLAG → `finding`, with `note = decision`. Or state that mapping at SKILL.md:101. |
| m5 | MINOR | `scripts/align.py:328-331` | The origin X/Y is the median of the station centres at the stations' median z, not the named intersection at z = 0 ("drive-hole axis ∩ top face"). Under tilt that offsets the origin by \|z_med\|·tan(tilt) (DRM ≈ 1.3 mm × tan 0.72° ≈ 0.016 mm). | Code read. | When the tilt fit has ≥ 3 stations, use the fitted line's z = 0 intercept `(ax_, ay_)` (return it from `tilt_from_stations`). Record `origin.xy_method` and both values. |
| m6 | MINOR | `scripts/align.py:403-410` | `removed` becomes `{null, null, "not recorded"}` when `intake_json` is omitted. The contract §3 `removed` block is then empty. | Code read. | Raise `SpecError` when `intake_json` is missing, or add the finding "removed fractions not recorded". |
| m7 | MINOR | `SKILL.md:3` | The trigger overlaps the orchestrator. "Use at the start of any scan-to-CAD job" competes with `stl-re-orchestrate`, which is the declared entry point for "convert this STL". | Sibling descriptions. | Replace the last sentence with: "Use when stl-re-orchestrate reaches the intake stage, or when asked only to intake, level/align or re-datum a scan." |
| m8 | MINOR | `scripts/align.py:310, 387-389, 432` | `secondary` is `null` for an axis primary with no `origin.xy` and a clock other than `plane_normal`. Contract §3 lists `secondary` as a required block. | Code read. | Append a finding "no secondary datum recorded", or raise `SpecError` unless `origin.xy` or a `plane_normal` clock is given. |
| m9 | MINOR | `references/datum-cookbook.md:40-62` | The replay table depends on unstated inputs. The "19 stations over 4.6 mm" row gives no spec, and the "Golden window not recorded" row mixes z windows. | Replay (see M2). | Give the exact JSON for every row in the table, or drop the row. |
| n1 | NIT | `scripts/datum_fit.py:241-242` | The comment "M is singular along d" is wrong: (I − nnᵀ)d = d because n ⊥ d, so M·d = Σw·d. The regularisation is harmless because it pins the along-axis component to the centroid, which is also what the unregularised solve gives on a cylinder. | Algebra. The synthetic cylinder point is exact to 5e-14. | Reword: "the along-axis component is weakly determined; pin it to the weighted centroid". |
| n2 | NIT | `scripts/align.py:279-290` | `primary.iters: 0` leaves `af` undefined (NameError, not exit 3). | Code read. | `iters = max(1, int(P.get("iters", 3)))`. |

## Datum math: what is right

- **Axis from normals**: direction = eigenvector of the smallest eigenvalue of Σ w nnᵀ, which is correct (SYNTHESIS §3). The synthetic tilted cylinder gives 0.0° direction error and 5e-14 point error, and a cone gives 9e-7°. The golden's no-op line has been removed.
- **RANSAC + level_plane**: a faithful lift of DRM `align.py:21-37` / `datum.py:7-24`, seeded. Only the residual statistics are trimmed (m1).
- **IRLS circle**: a faithful lift of B02 `q03_datum_full.py:98-111` (Cauchy, scale 0.30), now started from Kåsa rather than (0,0). With 8 % gross outliers the centre error is 0.0013 vs Kåsa's 0.019. The returned `r` is the mean distance, not the robust radius: acceptable, but worth noting.
- **Clock**: `polygon_flat` matches DRM `align.py:99-104` exactly (+36° = 180/n). `fourier_mass` matches B02 `q03:117-121` and returns all n candidates. `plane_normal` sign is fixed by the approximate normal.
- **Tilt**: the slope maths is correct (a synthetic 0.700° input returns 0.700°). The problem is estimator design (M2), not arithmetic.

## What I ran

- `python3 -m py_compile` on all 3 scripts: OK. `--help` on all 3: OK. There is no selftest.
- **DRM real test** (inspection only, `dreame_brush_screw_cap_scan_decimated.stl`, outputs in the scratchpad):
  - `intake.py stats --work-faces 300000`: 1017 bodies, fragments 1.98 %, ray vote outward (0.29 vs 0.96), work-vs-full p95 0.0009 / max 0.0099. 39 s.
  - `datum_fit.py noise` (top face): 0.006902.
  - `align.py` with the cookbook §2.1 spec plus a bottom landmark: **OK**, rms/max 0.0069/0.031 over 17,997 faces, 25 stations r_mean 1.886, clock **−34.255°** (golden −34.231°), tilt 0.716 ± 0.109°, landmark z_min −5.150 (golden bounds −5.151).
  - **Against golden `screw_alignment.json`**: rotation difference **0.0195°**, point disagreement **max 0.0140 mm** (60k seeded points). This reproduces the cookbook claim, and the aligned bounds agree to ≤ 0.013 mm.
  - Adding `noise_secondary` from the counterbore (IRLS rms 0.0307) gives STOP, "origin circle median rms 0.1097 > 0.0307", exit 2, as the cookbook says. The STOP rule does its job on the secondary: it catches the double-D shape error.
  - Determinism: two fresh runs give identical `alignment.json` apart from `created`.
  - `coverage`: 19 loops. The outer band has 131° of θ coverage, which is the pentagon corners (expected on a non-round part).
  - `scale`: 3 ENV pairs → UNIFORM 0.990295, and 2 pairs → FLAG. `regime`: baseline-skill without `--class` is refused, and RE_SPEC gets its source filled in. `planes`: 8 candidates, and the functional top face is split into several ~3 mm² candidates (fine, since they are "candidates only").
- Synthetic tests: B1 (axis STOP), axis/cone eigen, IRLS vs Kåsa, and tilt slope.
- Citations spot-checked, all correct: RE_SPEC.md:91, 92, 98-101, 105-107, 120-122, 124, 126-129, 131-136, 143-157, 170-175, 197-202, 241, 248-250, 347; `fastgate.py:36-38`; B02 `INTAKE_CARD.md:5-7`, R4 (:160), R6 (:167); B02 `MEASUREMENTS.md:24`; `DRM/report/intake.json` (104 bodies, top facet 0.267 mm²); `golden-examples/README.md` 0.028; P03 photo `IMG_20260729_140345.jpg` exists; B02 `VERDICT.md` 0.429° / 0.451; DRM table 9.3 % (`analysis/golden/dreame_brush-caps.md:196`, DRM README:71); `stl2step-skills.md` §5.1 eigen formula.
- Numbers: the thresholds trace to SYNTHESIS §4 (0.3°, 0.05–0.1, bands, ±0.1, 0.028, 3 loops). The golden-code defaults (10°, 0.1 bins, ±0.15, 300 iterations, 0.30 Cauchy, 0.7 table normal) are labelled as parameters. Heuristics are labelled n=1.
- Owner decisions: the regime is declared at intake (`intake.py regime` → `intake/regime.json`, plus a DECISIONS line). CHK-TILT against 0.3° is report-only. The census is not applicable here. All honoured.
- Size: SKILL.md is 286 lines. The progressive disclosure to the cookbook and templates is sensible.
- I deleted the `__pycache__` I created in `skills/stl-re-intake-datum/scripts/`. No repo files were edited.

## Fixes applied (round 1)

- **B1 — fixed.** `align.py` axis-primary path now requires `crop_point`/`crop_radius`
  (SpecError otherwise), computes the RADIAL residual of the cropped cylinder faces about the
  fitted axis (`rad = |(C-a) - ((C-a).d)d|`, `res = rad - median(rad)`) as `primary.fit_rms_mm`/
  `fit_max_mm` with `fit_metric` naming it, and gates it against `noise_secondary` (a circle
  noise floor) instead of the plane `noise` floor. When `noise_secondary` is absent it appends
  the same "not compared" finding used for the secondary. The old normal-line distance is kept
  as the diagnostic `primary.normal_line_dist`, never gated. `references/datum-cookbook.md` §3
  and the spec-reference table, and `SKILL.md` step 8.1, are updated to match. Verified with a
  synthetic tilted cylinder (r=10, vertex noise sigma=0.01 mm, tilt 11.5°): the old metric
  (`normal_line_dist.rms` = 0.217) would still STOP against a 0.02 mm floor, but the new radial
  residual (rms 0.0061) correctly passes; a forced-low `noise_secondary` still STOPs, and a
  missing `crop_point`/`crop_radius` correctly raises `SpecError` (exit 3).
- **M1 — fixed.** `align.py` now writes `matrix_4x4 = (T @ S).tolist()` (raw scan -> datum
  frame, scale folded in per run-contract §11) and keeps `scale_factor` as its own recorded
  field. A one-line self-check compares `T @ S` applied to a sample of RAW (pre-scale) vertices
  against the corresponding vertices of `aligned_work.stl`; a mismatch > 1e-6 mm raises
  `SpecError` rather than writing a silently-wrong matrix. `note` states the folding explicitly.
  Verified on the DRM screw replay (scale_factor 1.0, no change) and on the same spec with
  `scale_factor: 1.05` injected: the rotation block of `matrix_4x4` scales to row-norm 1.05 as
  expected and the self-check passes (no internal-error abort).
- **M2 — fixed.** `tilt_from_stations` now fits a COMMON slope with a PER-FEATURE intercept
  (design matrix = one-hot(feature) | z) for the pooled `tilt_deg.value`, and additionally fits
  every feature with >= 3 of its own stations independently, reported in `tilt_deg.per_feature`
  (`feature`, `value`, `stderr_deg`, `direction_deg`, `z_span_mm`, `n_stations`). When two
  per-feature tilt vectors (as 2-D vectors) differ by more than their combined 1-sigma stderr,
  `tilt_deg.resolvable` is set `false` (heuristic, stated as such) and `checks.CHK-TILT.note`
  reads "not resolvable" with the disagreement spelled out; `align.py`'s CHK-TILT result is then
  `finding` regardless of the 0.3° reference. `SKILL.md` step 8.5 and non-negotiable text, and
  `datum-cookbook.md` §2.1 (table row + lessons), replace the stated-as-fact "DRM screw measured
  0.72°" with the per-feature disagreement (double-D 0.72° ± 0.11° @ 117° vs counterbore F08
  2.8° ± 0.56° @ -111°, review M2) as an example of a not-resolvable case. Verified on the DRM
  screw replay: the single-feature (double-D only) spec reproduces `0.716° ± 0.109°` at
  `116.7°` (matches the review's own replay to 3 decimals); adding a second feature
  (counterbore F08, spec built from `README.md:38`'s stated r/z window, since the review's own
  exact counterbore spec is not recorded — see m9, not fixed) reproduces the qualitative
  disagreement: pooled tilt is flagged `resolvable: false`, with per-feature values pointing in
  different directions or magnitudes than the double-D-only fit.
- **m1 (untrimmed fit stats) — fixed** (the part of this finding the orchestrator asked for).
  `level_plane` (`datum_fit.py`) now also returns `fit_untrimmed: {rms, p95, max, n_faces}` over
  the peak-offset-bin band (`sel`, before the `|d| < 2*tol` widen/refine) and `inlier_frac`, and
  `align.py`'s plane-primary dict carries both alongside the existing trimmed/gated
  `fit_rms_mm`/`fit_max_mm`. The STOP rule is unchanged (rms only, vs the noise floor).
  `align.py` also appends the "primary STOP check is self-referential" finding when
  `noise.method` mentions the primary's own `mesh_region_desc`. `SKILL.md` non-negotiable 5 now
  states "rms is gated, max is reported". Verified on the DRM replay: `fit_untrimmed.max`
  (0.143 mm) is well above the trimmed, gated `fit_max_mm` (0.047 mm), and the
  self-referential finding appears in `findings` for the single-primary-noise spec, as expected.
  The rest of m1 (rewording the `datum_fit.py:178-190` docstring block beyond what's above) was
  left as originally worded; it was not requested for this round.
- **n1 — fixed.** Reworded the `axis_from_normals` comment: the along-axis component of `M` is
  weakly determined, not literally singular, matching the review's algebra note.
- **n2 — fixed.** `align.py` axis-primary loop now uses `max(1, int(P.get("iters", 3)))` so
  `iters: 0` in a spec can no longer leave `af` undefined (previously a `NameError`, not the
  documented exit 3).
- **V1 (cross-skill, from the orchestrator's message mid-review) — fixed.** `intake.py`'s
  `regime` subcommand now writes `bands` as one flat object with exactly
  `{p95_mm, max_mm, tier1_abs_mm, interface_max_mm}` (`null` when the regime does not gate that
  band), rejecting any other key (`_normalize_bands`). RE_SPEC fills all four
  (1.6 / 4.0 / 0.15 / 0.8, unchanged values, `RE_SPEC.md:170-175`); baseline-skill fills only
  `p95_mm`/`max_mm` (the two existing per-class values, unchanged) and records the chosen class
  as the new top-level `regime.json#material_class` (`plastic|machined`), never nested inside
  `bands`. `SKILL.md` step 7 states the canonical shape. Verified: `RE_SPEC`, `baseline-skill
  --class plastic`, `baseline-skill` with no `--class`/`--bands` (correctly refused), and an
  explicit `--bands` payload using an old key name (`tier2_p95_mm`, correctly refused) all
  behave as specified.
- **m2, m3, m4, m5, m6, m7, m8, m9 — not fixed this round.** Out of the accepted scope for round
  1 (procedure reordering, `SpecError` on missing landmarks/`intake_json`/secondary, the
  `chk_scale` decision-string mapping, the trigger-sentence overlap with the orchestrator, the
  origin X/Y `z=0` intercept method, and giving every cookbook replay row its exact spec).
  None of them block B1/M1/M2/the STOP-rule change, and none were listed in the orchestrator's
  accepted set for this pass.

## Strengths

- The plane-primary replay reproduces the golden DRM datum to 0.02° / 0.014 mm, with measured tilt and no bbox fallback.
- The open-mesh normal orientation is fixed by a ray vote, with a clear B02 rationale.
- Contract keys are present, and the STOP / CHECK_LANDMARKS / exit-3 semantics are clear. The failure-handling table is actionable.
- The provenance headers are precise (file:line of each lift), blind spots are stated, and the output is deterministic.
