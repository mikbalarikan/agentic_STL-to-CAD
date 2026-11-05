# VERDICT.md template and `qa/review.json`

`verdict.py render` writes `qa/VERDICT.md` from `qa/gate.json`. Never write numbers into it by
hand (CHK-NUMBERS: the B02 first draft quoted an intermediate run, `analysis/golden/OOM-B02.md` §8).
Your judgement goes into `qa/review.json`, which `verdict.py assemble` checks against the evidence.

## 1. VERDICT.md structure

1. `# VERDICT: <APPROVED | APPROVED_WITH_LIMITATIONS | BAND_NOT_MET | REVISE | HALT>`
2. **Regime.** Name, source path:line, bands. State it before any number (QUESTIONS.md Q1).
3. **Independence.** Either "fresh agent, own scripts" or the declared exception (CHK-INDEP; B02 A13).
4. **Scan.** Path, full-res or decimated, and the label (OFFICIAL / INSPECTION ONLY / INVALID).
5. **Gate table.** Gate · band · measured (n, rms, p50, p95, p99, max) · result.
6. **Deviation detail.**
   - Unmasked and masked, for both directions.
   - Observable CAD→scan and the unobservable fraction.
   - Each mask with its why, fraction and inside-stats.
   - Zones.
   - Over-band clusters, each with an explanation or `UNEXPLAINED`.
7. **Checks table.** Every CHK id: ran, result, note.
8. **Misses, per region.** Number, band, cause, options. Required for BAND_NOT_MET
   (SYNTHESIS F1; OD `README.md:21-44` is the model).
9. **Declared limitations.** Each one needs a re-run trigger (SYNTHESIS F10).
10. **Blockers.** List them if any exist. With a blocker there is no official grade.
11. **Claim boundary.** What the result is NOT.
    - B02: "Not yet fit for manufacture or tooling until F01 is calipered."
    - M02: "the listed local exported-artifact … gates only."
12. Footer: numbers were read from gate.json, plus the allowed verdict set.

## 2. `qa/review.json` (the agent's inputs)

```json
{"verdict": "APPROVED_WITH_LIMITATIONS",
 "independence": "fresh agent; QA scripts from stl-re-verify only; builder numbers not used",
 "checks": {
   "CHK-CIRCULAR":  {"ran": true, "result": "pass|finding|fail", "note": "datum not ICP'd to own CAD; no expected value taken from this scan"},
   "CHK-LIKE4LIKE": {"ran": true, "result": "pass|finding|n/a", "note": "it1 vs it2 used the same protocol / or: protocol changed, deltas labelled"},
   "CHK-INDEP":     {"ran": true, "result": "pass|finding", "note": ""},
   "CHK-FILLET":    {"ran": true, "result": "pass|finding", "note": "export_check fillets: every target radius == used radius, no FAILED"},
   "CHK-PATCHWORK": {"ran": true, "result": "pass|finding", "note": "census: faces, analytic share; no ruled lofts / polyline stacks"},
   "CHK-ENUM":      {"ran": true, "result": "pass|finding", "note": "every photographed/intake feature exists in CAD; clusters reviewed"},
   "CHK-ACHIEVABLE": {"ran": true, "result": "pass|finding|n/a", "note": "same jaw run on the scan section, on a Tier-1 miss (§4 step 4); n/a when nothing missed"},
   "PHOTO-PLAUSIBILITY": {"ran": true, "result": "pass|finding|n/a", "note": "photo ids checked; n/a when the run has no photos"}},
 "photos": ["<photo id>", "..."],
 "cluster_explanations": {"0": "scan flap at 150° leg (artefact, photo 1234)", "1": "..."},
 "limitations": [{"id": "L1", "text": "...", "rerun_trigger": "one caliper reading on F01"}],
 "miss_explanations": [{"region": "front_body", "cause": "...", "options": "..."}],
 "claim_boundary": "Not fit for tooling until ..."}
```

`photos: []` (an empty list, declared explicitly) makes `PHOTO-PLAUSIBILITY` default to `n/a` when
the check itself is omitted from `checks`; leaving `photos` out entirely still requires the check to
be recorded, so an agent cannot skip it by simply forgetting the field.

`verdict.py assemble` computes the **allowed** set and refuses (exit 2) a verdict outside it:

| Evidence | Allowed |
|---|---|
| Evidence simply missing/invalid: hash changed, no step check, no independent ICP (run-contract §12: required in every regime) (review V7) | **HALT** (re-run QA; does not count toward the 3-loop limit) |
| Any other blocker: ICP did not converge, Tier-1 gated dim not measurable on the STEP, CHK-CIRCULAR = fail | REVISE, HALT |
| Geometry validity failure: not a single valid closed solid (review V6) | REVISE, HALT (never BAND_NOT_MET -- an invalid solid is not a band a human can accept) |
| Any band fail (Tier-1, whole part, functional interface) | BAND_NOT_MET, REVISE, HALT |
| All pass, but a decimated-scan limitation (DRM new-skill replay: not a blocker), a mask-dependent pass (including an observable-only pass, review V5), partial Tier-1 coverage, a grey-zone reading, or any declared limitation | APPROVED_WITH_LIMITATIONS, REVISE, HALT |
| All pass, nothing else | APPROVED, REVISE, HALT (review V8: never BAND_NOT_MET here -- nothing missed a band) |

`verdict.py assemble` never writes a refused verdict into `gate.json#verdict` (review V12 /
orchestrate review O-1): on refusal (`errors` non-empty) it writes `verdict: null` and keeps the
reviewer's proposal in `proposed_verdict`, and it deletes any stale `qa/VERDICT.md` so a downstream
reader cannot mistake an old render for a current one.

How to choose inside the allowed set:
- **REVISE:** the cause is fixable in measurement or geometry. Examples: a misattributed
  caliper reading on B02 it1; a missing feature on P03 it1. It counts toward the 3-loop limit
  (`RE_SPEC.md:248-250`).
- **BAND_NOT_MET:** the cause is outside geometry, such as scan artefacts, unobservable surfaces,
  or no calipers to arbitrate. Examples: OD, DRM snap. It needs recorded human acceptance before
  delivery.
- **HALT:** 3 loops are used up, or only a human can clear the blocker (missing calipers on a
  critical interface, unsupported part class).

## 3. Golden outcomes, as this skill would grade them

This skill's grade for each golden part, and why, is worked in
`harnesses/v0/skills/stl-re-orchestrate/references/verdict-examples.md` — read that file, not a table here,
so that this file does not become a second copy of the same answer key. In short: the six
golden parts land across the full range this contract defines (APPROVED,
APPROVED_WITH_LIMITATIONS, BAND_NOT_MET), for reasons ranging from an unmasked clean scan gate
to masked passes, unobservable surfaces, and a circular self-check. Do not assume any specific
part's outcome before you have re-derived it.

## 4. Worked numbers from this skill's own test runs (2026-09-25, trimesh 5.1.0)

These are test records for the scripts, confirming each script reproduces (or, where noted,
knowingly differs from) the golden project's own numbers to a stated precision. The actual
figures are not restated here — see the golden report and `analysis/golden/*.md` for them, and
re-run the script yourself against the golden inputs if you need to re-validate it.

- **OD-H12, full-res, official-grade reproduction.** Inputs: `0_input/OD-H12-Pump.stl` +
  `report/alignment_T1.json` + `OD-H12-Pump_datum.stl`, default parameters. The reproduction's
  max absolute difference from `report/deviation_gate.json` is **0** across every statistic
  (scan→CAD, CAD→scan, and the observable-only split). QA's own STEP check of
  `OD-H12-Pump_datum.step` also matches the golden's recorded solid/face/volume facts exactly.
- **Dreame screw, DECIMATED, INSPECTION ONLY.** Scan-frame STEP tessellated by QA. The
  decimated-scan deviation numbers are close to, but not identical to, the official full-res
  run (expected: it's a different, coarser scan). ICP did not converge at the default cap and
  needed a higher cap to converge; see the golden's own ICP report for a comparison.
- **OOM-B02, full-res (bonus).** `datum_audit.py`, `tier2_icp.py`, `sim_caliper.py` and
  `deviation_gate.py` all reproduce the golden's own QA numbers closely (agreement is within a
  few percent or better on every statistic checked, with any small differences explained by a
  masking or sampling detail noted next to each script's entry in the Scripts table below). The
  hex pocket is flagged as a mask-dependent pass in both the golden and this reproduction.
  `step_check.py`'s solid/face/volume facts match the golden's exactly.
