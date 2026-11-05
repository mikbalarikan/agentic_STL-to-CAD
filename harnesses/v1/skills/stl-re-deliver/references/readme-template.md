# deliver/README.md template

`scripts/make_readme.py` renders this structure. Do not write the README by hand. To change
a number, fix the JSON it comes from and re-render (CHK-NUMBERS). This file records where
each section comes from, so a reviewer can check that it was earned.

Baseline: RE_SPEC §9 DoD item 3 asks for "reference photo, method summary, parameter table
with source tags (caliper / scan / inferred), caliper check table, deviation stats,
restoration notes" (`baseline/oomwoo-re-pipeline/RE_SPEC.md:330-333`). The goldens add
frames, the claim boundary, limitations with triggers and reproduction commands
(SYNTHESIS F9).

## Section list

| # | Section | Rendered from | Golden source of the section |
|---|---|---|---|
| — | Headline: verdict word, regime and its source, iteration n of 3 with the superseded folders, CHK-INDEP; a NOT MET banner for BAND_NOT_MET | `qa/gate.json#verdict,regime,checks`; `_itN_SUPERSEDED/` | B02 `6_RE_work/VERDICT.md:3` ("APPROVED (iteration 2 of 3) — with three declared limitations"); OD `README.md:32` (NOT MET stated first) |
| 1 | The part: reference photo, what it is | `limitations.json#part`; `input/photos/` | RE_SPEC §9 (reference photo); OD `README.md:3-4` (part, input) |
| 2 | Deliverables: both STEP files with frame, solids, valid, closed, faces, volume, bbox | `build/export_check.json` | OD `README.md:9-19` + `report/export_check.json`; DRM `README.md:5-17` |
| 3 | Method summary | `limitations.json#method_summary` | DRM `README.md:19-25` (5 steps); OD `README.md:5-7` |
| 4 | Coordinate frames: origin, primary, secondary, clock (with fit residuals and why), named axes, tilt, scale, noise floor, the 4×4 matrix | `intake/alignment.json` | OD `README.md:13-14` (scan-frame and datum-frame STEP, named axes); DRM `README.md:10,13,21` (plane, bore axis, clock feature); SYNTHESIS B1, B7, D14 |
| 5 | Parameter table with source column and source counts | `measure/params.json` | B02 `PARAM_TABLE.md` (SOURCE tag per row); DRM `README.md:27-54` (measured → chosen); SYNTHESIS C7 |
| 6 | Model tree (design intent): feature list with params, links `model.py`/`MODELING_PLAN.md` | `limitations.json#feature_tree` (optional); `build/MODELING_PLAN.md` | OD `README.md:46-60` (6 features); DRM `README.md:27-54` (F01-F09); M02 `README.md:12` (STEP carries no feature history) |
| 7 | Tier-1 table: real shape is `tier1.dims{id:{name,caliper,cad,delta,pass,gated,unmeasurable?,grey_zone?}}`, band `tier1.band_abs_mm`, coverage `tier1.coverage`; a gated-but-unmeasurable dim is flagged, never a silent pass | `qa/gate.json#tier1` (as `stl-re-verify/scripts/sim_caliper.py` writes it) | B02 `VERDICT.md:37-56`; P03 `VERDICT.md:16-29`; review V4 |
| 8 | Deviation: regime and bands, registration, two-way stats (`scan_to_cad`/`cad_to_scan` are UNMASKED; `scan_to_cad_masked`/`cad_to_scan_masked` are masked — never swap the labels), observable split, a **gate-results table** from `gate.json#gated_results` (the numbers the verdict was actually graded on), per-zone (unmasked/masked side by side), masks with fraction, sensitivity, over-band clusters (`over_band_clusters` is a dict keyed `scan_to_cad`/`cad_to_scan`, each with a `clusters` list), datum audit (report-only) | `qa/gate.json#deviation,gated_results,datum_audit` (as `stl-re-verify/scripts/deviation_gate.py` and `verdict.py` write them) | OD `README.md:21-44` (two-way, observable, regions); B02 `VERDICT.md:76-151` (zones, masks, sensitivity); DRM `README.md:56-78` (masked vs unmasked) |
| 8b | Band miss: where and what next (region, cause, options); required for BAND_NOT_MET | `qa/gate.json#miss_explanations,band_fails` | OD `README.md:43-44`; honesty rule `baseline/oomwoo-re-pipeline/RE_SPEC.md:181-183` |
| 9 | Named checks: verify's `checks` plus deliver's preflight | `qa/gate.json#checks`; preflight | SYNTHESIS §2 |
| 9 | Declared limitations, each with a re-run trigger | `limitations.json#limitations` | B02 `VERDICT.md:20-30`; SYNTHESIS F10 |
| 10 | Assumptions and invented geometry: params tagged assumed / photo-inferred / standard, plus stated assumptions; or "Nothing unmeasured was invented" | `measure/params.json`; `limitations.json#assumptions` | M02 `README.md:21-27`; OD `README.md:62-71`; B02 `VERDICT.md:165-176` |
| 11 | Claim boundary: "Not fit for" first, then "Fit for" | `limitations.json#claim_boundary` | M02 `README.md:29-31`; B02 `VERDICT.md:204-213`; SYNTHESIS F7 |
| 12 | Human acceptance of a band miss (only for BAND_NOT_MET) | `DECISIONS.md` ACCEPT-BAND entry + its evidence file | run-contract §7, §10; OD `README.md:62` ("operator approval required") |
| 13 | Reproduction: commands and the fresh-process result | `limitations.json#repro_commands`; `deliver/repro.json` | OD `README.md:73-79`; M02 `reproducibility_report.json` |
| 14 | Provenance: sha256 of every JSON the numbers came from | computed | B02 `70_report.py:1-5` ("read from the saved QA JSON, never retyped") |

Sections are numbered in order by the script as it renders (the "#" above is only this table's
own reference). "Human acceptance of a band miss" and "Band miss: where and what next" only
appear for BAND_NOT_MET.

## `deliver/limitations.json` (the only hand-written input)

Write it only after `preflight.py` passes (deliver/ must not exist earlier: CHK-PUBLISH).

```json
{
  "schema": "stl-re/limitations@1",
  "part": {"name": "<part>", "what_it_is": "<one or two sentences>",
           "reference_photo": "input/photos/<file>.jpg | null"},
  "method_summary": ["<step>", "..."],
  "limitations": [{"id": "L1", "text": "<what, why, what the model holds>",
                   "rerun_trigger": "<the observation that forces a re-run>",
                   "evidence": "<path or path#key>"}],
  "assumptions": [{"text": "...", "source": "assumed|photo-inferred|standard|operator-spec",
                   "evidence": "..."}],
  "claim_boundary": {"not_fit_for": ["..."], "fit_for": ["..."]},
  "repro_commands": ["optional; default: build + repro_check"],
  "feature_tree": [{"id": "F1", "feature": "<name>", "params": ["<param names it drives>"]}]
}
```

Rules the renderer enforces:
- `limitations` must be empty for APPROVED and non-empty for APPROVED_WITH_LIMITATIONS and
  BAND_NOT_MET. Every entry needs a `rerun_trigger`.
- Every limitation verify declared (`qa/gate.json#limitations`, written by `verdict.py` from
  `review.json`) must appear here too, matched by `id` (or by `text` when it carries no id):
  it is re-cited, never re-typed from memory and never dropped.
- Every automatic finding verify recorded (`qa/gate.json#auto_limitations` -- a mask-dependent
  pass, a partial Tier-1, a grey-zone reading, a decimated scan, ...) must be covered by some
  limitation's `text` or `evidence` mentioning its keyword (the phrase before the first `:`).
- `claim_boundary.not_fit_for` must not be empty.
- No literal decimal in any prose field, including `Ø8.00`-, `AF12.34`- and `M3.5`-style
  tokens. Use a placeholder: `{{gate:<dotted.path>}}`, `{{params:<name>.<key>}}`,
  `{{export:<frame>.<key>}}`, `{{align:<dotted.path>}}`, `{{repro:<dotted.path>}}`. List items
  use numeric indices (`{{gate:deviation.masks.0.fraction}}`). An unresolvable placeholder fails.
- `reference_photo`, when given, must exist in the run folder.
- `deliver/repro.json#inputs` (its recorded sha256 of `build/model.py`, `measure/params.json`
  and the delivered STEPs) must match those files' current hashes; a stale repro.json (an
  earlier attempt's check, surviving an `init_run.py supersede`) is refused, not trusted.

Display format: floats at 4 decimals with trailing zeros stripped. The JSON stays the
authority; the README never rounds a number to make it pass.
