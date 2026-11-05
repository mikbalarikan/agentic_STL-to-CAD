# VERDICT: BAND_NOT_MET

Regime: **RE_SPEC** (baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175); bands {'tier1_abs_mm': 0.15, 'tier2_p95_mm': 1.6, 'tier2_max_mm': 4.0, 'interface_max_mm': 0.8, 'tier1_abs': 0.15, 'p95': 1.6, 'max': 4.0, 'interface_max': 0.8}.
Independence: NOT independent: verify run by the same agent that measured and built the model (no fresh-context tool available). QA inputs (dims, zones, masks, datum spec) written separately; all numbers re-derived by the verify scripts on the full-res scan. In it1 the D-01/D-02 jaw azimuth (-1.1 deg) was copied from params.json (a builder number); it2 uses the scan-derived datum clock 0.0.

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `OOM-B02_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 5818.043 mm³ | PASS |
| Validity `OOM-B02.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 5818.043 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.046° / origin 0.019 mm / points p95 0.050 max 0.059 mm | within (not blocking) |
| Tier-1 D-01 arm thickness at tuft collar (arm 1 @ datum clock 0, r=36) | ±0.15 | caliper 4.07 CAD 4.075 Δ +0.005 | PASS |
| Tier-1 D-02 arm width at tuft collar (arm 1 @ datum clock 0, r=36) | ±0.15 | caliper 5.33 CAD 5.363 Δ +0.033 | PASS |
| Tier-1 D-03 skirt OD max (lobe) | ±0.15 | caliper 26.85 CAD 26.825 Δ -0.025 | PASS |
| Tier-1 D-05 skirt OD min (flat) - STRUCK at measure (CHK-ACHIEVABLE) | ±0.15 | caliper 24.84 CAD 25.014 Δ +0.174 | FAIL |
| Tier-1 D-07 skirt OD at a lobe | ±0.15 | caliper 26.8 CAD 26.825 Δ +0.025 | PASS |
| Tier-1 D-08 cup bore ID | ±0.15 | caliper 20.75 CAD 20.750 Δ +0.000 | PASS |
| Tier-1 D-11 hex pocket depth below cup floor (meridian 180) | ±0.15 | caliper 3.44 CAD 3.440 Δ +0.000 | PASS |
| Registration (ICP) | converged | 44/60 its, 0.394° / 0.069 mm | PASS |
| scan_to_cad:masked | p95 ≤1.6 / max ≤4.0 | n 318492 · rms 0.237 · p50 0.098 · p95 0.544 · p99 0.818 · max 1.167 | PASS |
| cad_to_scan_observable | p95 ≤1.6 / max ≤4.0 | n 19960 · rms 0.460 · p50 0.126 · p95 1.063 · p99 1.743 · max 3.049 | PASS |
| zone:Z-BORE cup bore:scan_to_cad | p95 ≤None / max ≤0.8 | n 12038 · rms 0.138 · p50 0.099 · p95 0.262 · p99 0.397 · max 0.475 | PASS |
| zone:Z-BORE cup bore:cad_to_scan | p95 ≤None / max ≤0.8 | n 7715 · rms 0.122 · p50 0.081 · p95 0.241 · p99 0.336 · max 0.497 | PASS |
| zone:Z-HEX hex pocket:scan_to_cad | p95 ≤None / max ≤0.8 | n 8472 · rms 0.139 · p50 0.086 · p95 0.249 · p99 0.280 · max 0.732 | PASS |
| zone:Z-HEX hex pocket:cad_to_scan | p95 ≤None / max ≤0.8 | n 4730 · rms 0.125 · p50 0.064 · p95 0.241 · p99 0.264 · max 0.347 | PASS |
| zone:Z-KEY key block/rib/flat/hole:scan_to_cad | p95 ≤None / max ≤0.8 | n 14878 · rms 0.263 · p50 0.096 · p95 0.630 · p99 0.877 · max 1.167 | FAIL |
| zone:Z-KEY key block/rib/flat/hole:cad_to_scan | p95 ≤None / max ≤0.8 | n 10258 · rms 0.390 · p50 0.097 · p95 1.049 · p99 1.367 · max 1.606 | FAIL |
| zone:Z-SEAT rim annulus:scan_to_cad | p95 ≤None / max ≤0.8 | n 16986 · rms 0.096 · p50 0.068 · p95 0.180 · p99 0.234 · max 0.289 | PASS |
| zone:Z-SEAT rim annulus:cad_to_scan | p95 ≤None / max ≤0.8 | n 10771 · rms 0.109 · p50 0.076 · p95 0.214 · p99 0.292 · max 0.386 | PASS |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 405114 · rms 7.507 · p50 0.142 · p95 22.107 · p99 27.906 · max 29.010
- scan→CAD masked: n 318492 · rms 0.237 · p50 0.098 · p95 0.544 · p99 0.818 · max 1.167
- CAD→scan unmasked: n 300000 · rms 0.465 · p50 0.129 · p95 1.066 · p99 1.812 · max 3.199
- CAD→scan masked: n 230060 · rms 0.311 · p50 0.102 · p95 0.737 · p99 1.161 · max 2.503
- CAD→scan observable only: n 19960 · rms 0.460 · p50 0.126 · p95 1.063 · p99 1.743 · max 3.049; unobservable fraction 0.20 %

Masks:

- **M1 bristles** (scan_to_cad): soft bristle tufts beyond the rigid collar end, not modelled (owner, BRIEF.md); fraction 19.09 %; inside n 77356 · rms 17.169 · p50 14.968 · p95 27.938 · p99 28.511 · max 29.010
- **M2 key tuft** (scan_to_cad): black bristle tuft protruding from the key hole, soft; fraction 0.28 %; inside n 1137 · rms 2.037 · p50 2.043 · p95 2.621 · p99 2.721 · max 2.752
- **M3 screw head** (scan_to_cad): COTS screw head, not modelled (owner); fraction 1.72 %; inside n 6987 · rms 0.934 · p50 0.789 · p95 1.506 · p99 1.545 · max 1.645
- **M4 screw tip** (scan_to_cad): COTS screw end in the hex pocket, not modelled; fraction 0.28 %; inside n 1142 · rms 0.802 · p50 0.659 · p95 1.414 · p99 1.601 · max 1.724
- **M5 hidden under screw** (cad_to_scan): CAD counterbore floor and screw hole are assumed geometry hidden by the COTS screw; no scan can see them; fraction 2.91 %; inside n 8730 · rms 0.702 · p50 0.433 · p95 1.312 · p99 1.520 · max 1.658
- **M6 open boundary** (cad_to_scan): distance to a scan hole edge is not a surface deviation; fraction 18.27 %; inside n 54821 · rms 0.820 · p50 0.393 · p95 1.802 · p99 2.503 · max 3.199
- **M7 skin normal** (cad_to_scan): occluded interior correspondence is not an outer-skin deviation; fraction 6.73 %; inside n 20198 · rms 0.913 · p50 0.500 · p95 1.929 · p99 2.635 · max 3.199

Zones:

- Z-SEAT rim annulus [functional_interface] scan_to_cad: unmasked n 16986 · rms 0.096 · p50 0.068 · p95 0.180 · p99 0.234 · max 0.289 | masked n 16986 · rms 0.096 · p50 0.068 · p95 0.180 · p99 0.234 · max 0.289
- Z-SEAT rim annulus [functional_interface] cad_to_scan: unmasked n 13526 · rms 0.106 · p50 0.072 · p95 0.206 · p99 0.287 · max 0.386 | masked n 10771 · rms 0.109 · p50 0.076 · p95 0.214 · p99 0.292 · max 0.386
- Z-HEX hex pocket [functional_interface] scan_to_cad: unmasked n 8472 · rms 0.139 · p50 0.086 · p95 0.249 · p99 0.280 · max 0.732 | masked n 8472 · rms 0.139 · p50 0.086 · p95 0.249 · p99 0.280 · max 0.732
- Z-HEX hex pocket [functional_interface] cad_to_scan: unmasked n 9831 · rms 0.587 · p50 0.172 · p95 1.418 · p99 1.653 · max 1.824 | masked n 4730 · rms 0.125 · p50 0.064 · p95 0.241 · p99 0.264 · max 0.347
- Z-BORE cup bore [functional_interface] scan_to_cad: unmasked n 12038 · rms 0.138 · p50 0.099 · p95 0.262 · p99 0.397 · max 0.475 | masked n 12038 · rms 0.138 · p50 0.099 · p95 0.262 · p99 0.397 · max 0.475
- Z-BORE cup bore [functional_interface] cad_to_scan: unmasked n 10141 · rms 0.280 · p50 0.106 · p95 0.656 · p99 0.917 · max 1.141 | masked n 7715 · rms 0.122 · p50 0.081 · p95 0.241 · p99 0.336 · max 0.497
- Z-KEY key block/rib/flat/hole [functional_interface] scan_to_cad: unmasked n 15102 · rms 0.305 · p50 0.098 · p95 0.700 · p99 1.232 · max 1.543 | masked n 14878 · rms 0.263 · p50 0.096 · p95 0.630 · p99 0.877 · max 1.167
- Z-KEY key block/rib/flat/hole [functional_interface] cad_to_scan: unmasked n 14682 · rms 0.419 · p50 0.133 · p95 1.040 · p99 1.341 · max 1.606 | masked n 10258 · rms 0.390 · p50 0.097 · p95 1.049 · p99 1.367 · max 1.606
- R-DOME dome + top [region] scan_to_cad: unmasked n 75065 · rms 0.216 · p50 0.066 · p95 0.548 · p99 0.852 · max 1.120 | masked n 75065 · rms 0.216 · p50 0.066 · p95 0.548 · p99 0.852 · max 1.120
- R-DOME dome + top [region] cad_to_scan: unmasked n 60808 · rms 0.308 · p50 0.071 · p95 0.813 · p99 1.191 · max 1.715 | masked n 57427 · rms 0.279 · p50 0.068 · p95 0.730 · p99 1.120 · max 1.430
- R-ARMS rigid arms r 13.6-38.6 [region] scan_to_cad: unmasked n 134538 · rms 0.353 · p50 0.182 · p95 0.665 · p99 0.998 · max 2.752 | masked n 133401 · rms 0.301 · p50 0.181 · p95 0.635 · p99 0.864 · max 1.114
- R-ARMS rigid arms r 13.6-38.6 [region] cad_to_scan: unmasked n 121828 · rms 0.536 · p50 0.218 · p95 1.108 · p99 2.147 · max 3.199 | masked n 95076 · rms 0.379 · p50 0.189 · p95 0.854 · p99 1.204 · max 2.219
- R-COLLAR underside (unscanned) [interior] scan_to_cad: unmasked n 25683 · rms 0.267 · p50 0.192 · p95 0.503 · p99 0.638 · max 0.960 | masked n 25683 · rms 0.267 · p50 0.192 · p95 0.503 · p99 0.638 · max 0.960
- R-COLLAR underside (unscanned) [interior] cad_to_scan: unmasked n 28534 · rms 0.836 · p50 0.278 · p95 2.072 · p99 2.683 · max 3.199 | masked n 14651 · rms 0.286 · p50 0.185 · p95 0.525 · p99 0.822 · max 2.219

Over-band scan→CAD points (> 4.0 mm): 66146 (16.328 %) in 3 clusters ≥ 20 pts.

- cluster 0: n 23521, centroid [52.364, -5.535, 27.234], r [41.91, 62.81], θ [0.0, 360.0], max 28.421 — bristle tuft arm 1 (r 41.9-62.8): soft, not modelled, masked M1
- cluster 1: n 22630, centroid [-26.372, 44.154, 26.361], r [41.897, 62.056], θ [117.8, 124.6], max 29.010 — bristle tuft arm 2: masked M1
- cluster 2: n 19995, centroid [-25.097, -45.901, 27.507], r [41.859, 62.728], θ [236.4, 245.1], max 28.540 — bristle tuft arm 3: masked M1

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | finding | whole part scan_to_cad; zone Z-HEX hex pocket cad_to_scan; zone Z-BORE cup bore cad_to_scan |
| CHK-CLUSTER | pass | 3 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | alignment.json frozen at intake; ICP T_refine QA-only; Tier-1 against photo calipers, not scan-derived values |
| CHK-LIKE4LIKE | finding | it1->it2: same regime adapter, zones, masks, ICP and sampling parameters, same full-res scan; ONE protocol change: D-01/D-02 jaw azimuth -1.1 -> 0.0 (values unchanged: 4.0746/5.3634 both runs). Improvements (Z-SEAT c2s max 0.808 -> 0.386, ICP 1.197 -> 0.394 deg, D-05 CAD 25.361 -> 25.014) come from geometry (relief shape + arm clock). |
| CHK-INDEP | finding | same agent built and verified; DECISIONS.md INDEP entry |
| CHK-FILLET | pass | no fillets planned or applied (no measured radii); sharp edges declared |
| CHK-PATCHWORK | pass | 75 faces, 0 ruled-like faces, no loft used |
| CHK-ENUM | pass | all 12 intake features built or declared out of scope |
| PHOTO-PLAUSIBILITY | pass | hex, key block/rib, skirt hole, polygonal skirt with reliefs, dome, arms, collars present; nothing in CAD absent from photos/scan |

## Misses, per region

- tier1 D-05: delta +0.1737 vs ±0.15
- zone:Z-KEY key block/rib/flat/hole:scan_to_cad: p95 0.630 max 1.167 vs None/0.8
- zone:Z-KEY key block/rib/flat/hole:cad_to_scan: p95 1.049 max 1.606 vs None/0.8
- **None**: ATTRIBUTION, not geometry: reading struck at measure (CHK-ACHIEVABLE) - the scan's two-jaw window min is 24.94..25.08 (z 0.5-2), so 24.84 +-0.1 is not achievable on the scan; the CAD reads 25.014, 0.03 mm from the scan window min at z=1 (24.977). Margin to achievability is small (0.004..0.14). Options: (a) accept (ACCEPT-BAND); (b) re-read D-05 with a jaw-placement photo across key flat vs opposite arm relief - if confirmed, lower KEY_FLAT_D and ARM_RELIEF_R ~0.08 each and re-run; (c) HALT
- **None**: key block, rib, flat and skirt hole modelled as simplified boxes/cylinder; hole diameter/axis photo-inferred; masked scan->CAD max 1.167, CAD->scan max 1.606 (rib/block edges and hole) Options: (a) accept; (b) caliper/photos of key block width, rib width, hole diameter and re-run (no loops left in the owner time-box); (c) HALT

## Declared limitations (each with its re-run trigger)

1. Tier-1 partial: 6 of 7 gated photo-caliper dims pass, D-05 fails (struck); D-04 soft and D-06/09/10/12 unassigned are ABSENT, not passed; all other dims are scan authority, ungated — **Re-run trigger:** any bench caliper reading
2. Absolute scale not caliper-verified (0 envelope dims; CHK-SCALE FLAG); units assumed mm — **Re-run trigger:** an overall envelope caliper reading
3. Hex AF 7.353 (drive interface) is scan authority, not snapped, uncalipered; hex and bore interface passes are MASKED passes (hex CAD->scan unmasked max 1.824, bore 1.141, open-boundary mask) — **Re-run trigger:** one caliper reading of the hex AF
4. Screw through-hole dia 3.2 and counterbore floor z 8.9 are assumed (hidden by the COTS screw) and masked (M5) — **Re-run trigger:** measurement with the screw removed
5. Verification not independent (same agent) — **Re-run trigger:** re-run stl-re-verify in a fresh context

## Claim boundary

Geometry fit for visualisation and fit-up studies of the rigid brush body; NOT fit for manufacture/tooling (hex AF uncalipered, key geometry approximate, D-05 and Z-KEY bands not met, no human acceptance).

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
