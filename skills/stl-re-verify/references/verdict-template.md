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
- **REVISE:** the cause is fixable in measurement or geometry. Examples: B02 it1 F06 misattributed;
  P03 it1 stem missing. It counts toward the 3-loop limit (`RE_SPEC.md:248-250`).
- **BAND_NOT_MET:** the cause is outside geometry, such as scan artefacts, unobservable surfaces,
  or no calipers to arbitrate. Examples: OD, DRM snap. It needs recorded human acceptance before
  delivery.
- **HALT:** 3 loops are used up, or only a human can clear the blocker (missing calipers on a
  critical interface, unsupported part class).

## 3. Golden outcomes, as this skill would grade them

| Project | Official | Grade under this skill | Why |
|---|---|---|---|
| DRM screw | PASS | APPROVED (baseline-skill regime) | p95 0.085 / max 0.245 full-res, no masks (`screw_official_gate.json`) |
| DRM snap | Delivered | BAND_NOT_MET | max 1.226 > 0.80; masks leave 1.246 (`snap_official_gate.json`, `snap_masked_gate.json`) |
| OD-H12 | Delivered | BAND_NOT_MET | scan→CAD p95 0.448 / max 2.49 vs 0.30 / 0.80; validator 13/13 is circular |
| B02 it2 | APPROVED | APPROVED_WITH_LIMITATIONS | Tier-1 5 of 24; hex pocket is a masked pass (1.624 unmasked); scale unverified |
| P03 it2 | APPROVED | APPROVED_WITH_LIMITATIONS, with CHK-CIRCULAR finding | datum refined to own CAD; stem max 2.424 never banded; socket photo-inferred |
| M02 | QA PASS | APPROVED under project-spec only; no scan claim | spec-conformance only; no scan deviation run |

## 4. Worked numbers from this skill's own test runs (2026-09-25, trimesh 5.1.0)

These are test records for the scripts, not grades of the projects.

- **OD-H12, full-res, official-grade reproduction.** Inputs: `0_input/OD-H12-Pump.stl` +
  `report/alignment_T1.json` + `OD-H12-Pump_datum.stl`, default parameters. Output:
  - scan→CAD n 493,060, rms 0.2174, p95 0.4478, p99 0.6745, max 2.4934.
  - CAD→scan n 300,000, p95 3.4303, max 9.0269.
  - Observable n 14,870, p95 0.5671, max 8.6481; unobservable 25.65 %.
  - All four z-bands match. The max absolute difference to `report/deviation_gate.json` is **0**
    across every statistic.
  - QA's own STEP check of `OD-H12-Pump_datum.step`: 1 solid, 213 faces, 0 naked edges,
    V 114,903.269 mm³, 100 % analytic area.
- **Dreame screw, DECIMATED, INSPECTION ONLY.** Scan-frame STEP tessellated by QA.
  - scan→CAD p95 0.0888 / max 0.2573; CAD→scan p95 0.0748 / max 0.2444.
  - Compare the official full-res run: 0.0851 / 0.2448 and 0.0757 / 0.2683.
  - ICP did not converge in 60 iterations; it converged in 109 of 300 (0.364°, 0.015 mm).
- **OOM-B02, full-res (bonus).**
  - `datum_audit.py`: 0.4275°, point disagreement p95 0.3185 / max 0.4471 (golden 0.4289°,
    0.3197 / 0.4511).
  - `tier2_icp.py`: converged in 51 of 60 iterations, 0.6993° / 0.1877 mm (golden 48, 0.698° /
    0.187 mm).
  - `sim_caliper.py`: F05 26.850, F03 20.750 (analytic 20.750), F02 3.440, F01 7.358, F06 25.6165
    (golden `_qa_it2.json#qa4` identical).
  - `deviation_gate.py` with M1–M4, exact distances rather than golden NN:
    - Whole CAD→scan masked p95 0.755 / max 2.549 (golden 0.740 / 2.524).
    - Rim p95 0.249 / max 0.652 (golden 0.245 / 0.651).
    - Hex pocket with M3 masked max 0.307; unmasked 1.813. The A6 coverage mask was not
      replicated; golden 0.316 / 1.624.
    - The hex pocket is flagged as a mask-dependent pass.
  - `step_check.py`: 1 solid, 185 faces, 0 naked edges, V 5801.075 (golden 185, 0, 5801.07).
