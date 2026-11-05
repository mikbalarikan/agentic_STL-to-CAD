# VERDICT: REVISE

Regime: **RE_SPEC** (baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175); bands {'p95_mm': 1.6, 'max_mm': 4.0, 'tier1_abs_mm': 0.15, 'interface_max_mm': 0.8}.
Independence: verify ran in a fresh agent (CHK-INDEP)

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `fixture_part_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 5975.000 mm³ | PASS |
| Validity `fixture_part.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 5975.000 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.050° / origin 0.020 mm / points p95 0.030 max 0.050 mm | within (not blocking) |
| Tier-1 F01 plate_x | ±0.15 | caliper 40.55 CAD 40.000 Δ +0.550 | FAIL |
| Tier-1 F02 plate_t | ±0.15 | caliper 5.01 CAD 5.000 Δ -0.010 | PASS |
| Tier-1 F03 bore_d | ungated | CAD 8.000 | reported |
| Registration (ICP) | converged | 12/60 its, 0.010° / 0.004 mm | PASS |
| scan_to_cad:masked | p95 ≤1.6 / max ≤4.0 | n 20000 · rms 0.041 · p50 0.030 · p95 0.088 · p99 0.120 · max 0.310 | PASS |
| cad_to_scan_observable | p95 ≤1.6 / max ≤4.0 | n 18000 · rms 0.050 · p50 0.020 · p95 0.090 · p99 0.140 · max 0.290 | PASS |
| zone:bore_wall:scan_to_cad | p95 ≤None / max ≤0.8 | n 900 · rms 0.050 · p50 0.030 · p95 0.100 · p99 0.200 · max 0.400 | PASS |
| zone:bore_wall:cad_to_scan | p95 ≤None / max ≤0.8 | n 900 · rms 0.050 · p50 0.030 · p95 0.100 · p99 0.200 · max 0.400 | PASS |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 20000 · rms 0.041 · p50 0.030 · p95 0.088 · p99 0.120 · max 0.310
- scan→CAD masked: n 20000 · rms 0.041 · p50 0.030 · p95 0.088 · p99 0.120 · max 0.310
- CAD→scan unmasked: n 20000 · rms 0.900 · p50 0.020 · p95 3.900 · p99 4.000 · max 4.000
- CAD→scan masked: n 20000 · rms 0.900 · p50 0.020 · p95 3.900 · p99 4.000 · max 4.000
- CAD→scan observable only: n 18000 · rms 0.050 · p50 0.020 · p95 0.090 · p99 0.140 · max 0.290; unobservable fraction 10.00 %

Masks:

- none

Zones:

- bore_wall [functional_interface] scan_to_cad: unmasked n 900 · rms 0.050 · p50 0.030 · p95 0.100 · p99 0.200 · max 0.400 | masked n 900 · rms 0.050 · p50 0.030 · p95 0.100 · p99 0.200 · max 0.400
- bore_wall [functional_interface] cad_to_scan: unmasked n 900 · rms 0.050 · p50 0.030 · p95 0.100 · p99 0.200 · max 0.400 | masked n 900 · rms 0.050 · p50 0.030 · p95 0.100 · p99 0.200 · max 0.400

Over-band scan→CAD points (> 0.8 mm): 0 (0.000 %) in 0 clusters ≥ 20 pts.


## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 0 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | fixture |
| CHK-LIKE4LIKE | pass | fixture |
| CHK-INDEP | pass | fixture |
| CHK-FILLET | pass | fixture |
| CHK-PATCHWORK | pass | fixture |
| CHK-ENUM | finding | fixture: bore too small vs photo |
| CHK-ACHIEVABLE | finding | fixture: F01 plate_x miss is a caliper reading, not an unachievable geometry |
| PHOTO-PLAUSIBILITY | n/a | no photos taken for this run |

## Misses, per region

- tier1 F01: delta +0.5500 vs ±0.15

## Declared limitations (each with its re-run trigger)

None.

## Claim boundary

Not fit for any physical use; the bore is not calipered. Fit for pipeline testing of stl-re-deliver only.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
