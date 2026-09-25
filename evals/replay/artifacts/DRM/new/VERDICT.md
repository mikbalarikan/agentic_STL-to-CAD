# VERDICT: HALT

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8}.
Independence: NOT independent: verify ran in the same agent context that built the model (no subagent available). Mitigation: only stl-re-verify scripts were used; model.py/params.json were not imported; datum audit re-fitted on the raw scan. This is not an organisationally independent verification.

Scan: `input/scan.stl` (DECIMATED, inspection only), label **INSPECTION ONLY**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `drm_screw_cap_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 268.399 mm³ | PASS |
| Validity `drm_screw_cap.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 268.399 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 1.262° / origin 0.002 mm / points p95 0.117 max 0.123 mm | outside (not blocking) |
| Registration (ICP) | converged | 90/200 its, 0.242° / 0.035 mm | PASS |
| scan_to_cad:masked | p95 ≤None / max ≤None | n 475724 · rms 0.038 · p50 0.018 · p95 0.078 · p99 0.137 · max 0.309 | reported |
| cad_to_scan_observable | p95 ≤None / max ≤None | n 20000 · rms 0.032 · p50 0.015 · p95 0.066 · p99 0.106 · max 0.277 | reported |
| zone:Z-BORE bottom bore:scan_to_cad | p95 ≤None / max ≤0.8 | n 16971 · rms 0.032 · p50 0.025 · p95 0.061 · p99 0.076 · max 0.092 | PASS |
| zone:Z-BORE bottom bore:cad_to_scan | p95 ≤None / max ≤0.8 | n 11353 · rms 0.031 · p50 0.024 · p95 0.059 · p99 0.072 · max 0.091 | PASS |
| zone:Z-DD double-D drive hole:scan_to_cad | p95 ≤None / max ≤0.8 | n 45669 · rms 0.046 · p50 0.032 · p95 0.086 · p99 0.130 · max 0.195 | PASS |
| zone:Z-DD double-D drive hole:cad_to_scan | p95 ≤None / max ≤0.8 | n 29080 · rms 0.043 · p50 0.031 · p95 0.081 · p99 0.112 · max 0.170 | PASS |
| zone:Z-PENT pentagon side faces:scan_to_cad | p95 ≤None / max ≤0.8 | n 143452 · rms 0.032 · p50 0.018 · p95 0.067 · p99 0.099 · max 0.199 | PASS |
| zone:Z-PENT pentagon side faces:cad_to_scan | p95 ≤None / max ≤0.8 | n 52290 · rms 0.026 · p50 0.014 · p95 0.055 · p99 0.093 · max 0.156 | PASS |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 475724 · rms 0.038 · p50 0.018 · p95 0.078 · p99 0.137 · max 0.309
- scan→CAD masked: n 475724 · rms 0.038 · p50 0.018 · p95 0.078 · p99 0.137 · max 0.309
- CAD→scan unmasked: n 300000 · rms 0.032 · p50 0.015 · p95 0.066 · p99 0.107 · max 0.280
- CAD→scan masked: n 230515 · rms 0.029 · p50 0.014 · p95 0.061 · p99 0.100 · max 0.272
- CAD→scan observable only: n 20000 · rms 0.032 · p50 0.015 · p95 0.066 · p99 0.106 · max 0.277; unobservable fraction 0.00 %

Masks:

- **M1 open boundary 0.5 mm** (cad_to_scan): CAD points whose nearest scan point lies within 0.5 mm of a scan hole edge measure distance to a hole edge, not a surface deviation (22 open loops on the kept body: neck wall, pentagon corners under the shoulder); fraction 23.16 %; inside n 69485 · rms 0.040 · p50 0.020 · p95 0.077 · p99 0.131 · max 0.280

Zones:

- Z-DD double-D drive hole [functional_interface] scan_to_cad: unmasked n 45669 · rms 0.046 · p50 0.032 · p95 0.086 · p99 0.130 · max 0.195 | masked n 45669 · rms 0.046 · p50 0.032 · p95 0.086 · p99 0.130 · max 0.195
- Z-DD double-D drive hole [functional_interface] cad_to_scan: unmasked n 29661 · rms 0.043 · p50 0.031 · p95 0.081 · p99 0.112 · max 0.170 | masked n 29080 · rms 0.043 · p50 0.031 · p95 0.081 · p99 0.112 · max 0.170
- Z-BORE bottom bore [functional_interface] scan_to_cad: unmasked n 16971 · rms 0.032 · p50 0.025 · p95 0.061 · p99 0.076 · max 0.092 | masked n 16971 · rms 0.032 · p50 0.025 · p95 0.061 · p99 0.076 · max 0.092
- Z-BORE bottom bore [functional_interface] cad_to_scan: unmasked n 11353 · rms 0.031 · p50 0.024 · p95 0.059 · p99 0.072 · max 0.091 | masked n 11353 · rms 0.031 · p50 0.024 · p95 0.059 · p99 0.072 · max 0.091
- Z-PENT pentagon side faces [functional_interface] scan_to_cad: unmasked n 143452 · rms 0.032 · p50 0.018 · p95 0.067 · p99 0.099 · max 0.199 | masked n 143452 · rms 0.032 · p50 0.018 · p95 0.067 · p99 0.099 · max 0.199
- Z-PENT pentagon side faces [functional_interface] cad_to_scan: unmasked n 71951 · rms 0.025 · p50 0.014 · p95 0.050 · p99 0.086 · max 0.156 | masked n 52290 · rms 0.026 · p50 0.014 · p95 0.055 · p99 0.093 · max 0.156
- Z-TOP top face [region] scan_to_cad: unmasked n 26660 · rms 0.010 · p50 0.006 · p95 0.022 · p99 0.033 · max 0.041 | masked n 26660 · rms 0.010 · p50 0.006 · p95 0.022 · p99 0.033 · max 0.041
- Z-TOP top face [region] cad_to_scan: unmasked n 24963 · rms 0.011 · p50 0.007 · p95 0.022 · p99 0.033 · max 0.041 | masked n 24961 · rms 0.011 · p50 0.007 · p95 0.022 · p99 0.033 · max 0.041
- boss [region] scan_to_cad: unmasked n 30331 · rms 0.053 · p50 0.022 · p95 0.104 · p99 0.242 · max 0.281 | masked n 30331 · rms 0.053 · p50 0.022 · p95 0.104 · p99 0.242 · max 0.281
- boss [region] cad_to_scan: unmasked n 22884 · rms 0.055 · p50 0.019 · p95 0.136 · p99 0.237 · max 0.280 | masked n 15814 · rms 0.048 · p50 0.017 · p95 0.106 · p99 0.219 · max 0.272
- neck (occluded) [interior] scan_to_cad: unmasked n 37146 · rms 0.051 · p50 0.024 · p95 0.104 · p99 0.191 · max 0.302 | masked n 37146 · rms 0.051 · p50 0.024 · p95 0.104 · p99 0.191 · max 0.302
- neck (occluded) [interior] cad_to_scan: unmasked n 17567 · rms 0.030 · p50 0.018 · p95 0.064 · p99 0.091 · max 0.142 | masked n 5953 · rms 0.024 · p50 0.011 · p95 0.050 · p99 0.089 · max 0.112
- lower frustum [region] scan_to_cad: unmasked n 110000 · rms 0.033 · p50 0.012 · p95 0.071 · p99 0.147 · max 0.251 | masked n 110000 · rms 0.033 · p50 0.012 · p95 0.071 · p99 0.147 · max 0.251
- lower frustum [region] cad_to_scan: unmasked n 78425 · rms 0.021 · p50 0.012 · p95 0.039 · p99 0.069 · max 0.132 | masked n 67084 · rms 0.019 · p50 0.012 · p95 0.037 · p99 0.058 · max 0.132
- zband 0..-1 [region] scan_to_cad: unmasked n 143259 · rms 0.043 · p50 0.021 · p95 0.082 · p99 0.156 · max 0.281 | masked n 143259 · rms 0.043 · p50 0.021 · p95 0.082 · p99 0.156 · max 0.281
- zband 0..-1 [region] cad_to_scan: unmasked n 94384 · rms 0.040 · p50 0.016 · p95 0.076 · p99 0.156 · max 0.280 | masked n 58600 · rms 0.036 · p50 0.012 · p95 0.071 · p99 0.136 · max 0.272
- zband -1..-3 [region] scan_to_cad: unmasked n 160345 · rms 0.036 · p50 0.019 · p95 0.078 · p99 0.115 · max 0.246 | masked n 160345 · rms 0.036 · p50 0.019 · p95 0.078 · p99 0.115 · max 0.246
- zband -1..-3 [region] cad_to_scan: unmasked n 93116 · rms 0.033 · p50 0.017 · p95 0.073 · p99 0.110 · max 0.170 | masked n 78429 · rms 0.032 · p50 0.017 · p95 0.071 · p99 0.107 · max 0.170
- zband -3..-5.2 [region] scan_to_cad: unmasked n 172120 · rms 0.035 · p50 0.014 · p95 0.072 · p99 0.147 · max 0.309 | masked n 172120 · rms 0.035 · p50 0.014 · p95 0.072 · p99 0.147 · max 0.309
- zband -3..-5.2 [region] cad_to_scan: unmasked n 112500 · rms 0.022 · p50 0.013 · p95 0.043 · p99 0.067 · max 0.132 | masked n 93486 · rms 0.021 · p50 0.013 · p95 0.042 · p99 0.064 · max 0.132

Over-band scan→CAD points (> 0.8 mm): 0 (0.000 %) in 0 clusters ≥ 20 pts.


## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 0 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | alignment.json never ICP'd to the CAD; QA ICP T_refine kept in qa/ only; no expected values from the scan used as a gate |
| CHK-LIKE4LIKE | pass | first iteration; no previous gate to compare |
| CHK-INDEP | finding | same agent built and verified (DECISIONS.md INDEP) |
| CHK-FILLET | finding | F08e transition fillet target R0.548 used R0.3 (REDUCED) on 15 edges, declared in MODELING_PLAN.md; all others OK |
| CHK-PATCHWORK | pass | 98 faces; plane 40 / cylinder 36 / torus 7 / bspline 15 (fillet blends at panel-wall junctions); analytic area 98.6 %; no lofts, no polyline stacks |
| CHK-ENUM | finding | all 11 intake features present in CAD; no over-band clusters; no photos exist so photo cross-check not possible; boss r(theta) flattening at theta ~30-80 deg (overlay z=-0.2) is modelled round (declared simplification) |
| PHOTO-PLAUSIBILITY | n/a | no photos exist (BRIEF.md); marked ran=true only because verdict.py refuses ran=false for a check with nothing to run on |

## Declared limitations (each with its re-run trigger)

1. Graded on a DECIMATED scan only: every deviation number is INSPECTION ONLY — **Re-run trigger:** supply the full-resolution original scan and re-run stl-re-verify unchanged
2. Tier-1 not run: 0 of 10 requested dims calipered (all ABSENT, not passed) — **Re-run trigger:** any caliper reading of M1-M6 (double-D, bore, neck) or ENV-X/Y/Z
3. Absolute scale not caliper-verified (units assumed mm) — **Re-run trigger:** three envelope caliper readings (ENV-X/Y/Z) -> CHK-SCALE
4. Verification not independent (same agent) — **Re-run trigger:** re-run stl-re-verify in a fresh agent
5. Transition fillet reduced R0.548 -> R0.3; boss modelled round; neck radius partly unscanned — **Re-run trigger:** photo of the boss and the neck, or a pin-gauge reading of the neck

## Blockers (no official grade)

- decimated scan: INSPECTION ONLY, not an official grade

## Claim boundary

Inspection-grade model only: not an official grade, not fit for manufacture or tooling until graded on the full-resolution scan and the drive interfaces (double-D, bore) are calipered.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: HALT, REVISE._
