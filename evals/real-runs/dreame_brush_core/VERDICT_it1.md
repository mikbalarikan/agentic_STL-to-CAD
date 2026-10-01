# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: Verify ran in a separate agent context from the builder, with its own code: stl-re-verify scripts, its own ICP, and its own masks/zones/datum spec written from INTAKE_CARD/DECISIONS. No builder number, params.json, PARAM_TABLE, build_log or measure/figures were used. model.py was only grepped, never imported. Organisational independence is NOT claimed: the same orchestrator session spawned both builder and verifier.

Scan: `input/scan.stl` (DECIMATED, inspection only), label **INSPECTION ONLY**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `dreame_brush_core_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 29137.588 mm³ | PASS |
| Validity `dreame_brush_core.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 29137.588 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.888° / origin 0.034 mm / points p95 0.322 max 0.499 mm | outside (not blocking) |
| Registration (ICP) | converged | 88/1000 its, 0.404° / 0.037 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 79172 · rms 0.137 · p50 0.051 · p95 0.311 · p99 0.510 · max 1.392 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 16562 · rms 0.333 · p50 0.051 · p95 0.671 · p99 1.630 · max 2.568 | FAIL |
| zone:Z1 drive dog (blades + gap floor):scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 4488 · rms 0.113 · p50 0.048 · p95 0.225 · p99 0.422 · max 1.113 | FAIL |
| zone:Z1 drive dog (blades + gap floor):cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 18471 · rms 0.099 · p50 0.051 · p95 0.205 · p99 0.334 · max 0.761 | PASS |
| zone:Z2 hub discs r15.20 r16.44:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 6454 · rms 0.145 · p50 0.074 · p95 0.311 · p99 0.454 · max 0.825 | FAIL |
| zone:Z2 hub discs r15.20 r16.44:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 11588 · rms 0.090 · p50 0.046 · p95 0.193 · p99 0.272 · max 0.472 | PASS |
| zone:Z3 idler counterbore and bore:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 1992 · rms 0.157 · p50 0.078 · p95 0.327 · p99 0.561 · max 0.881 | FAIL |
| zone:Z3 idler counterbore and bore:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 5784 · rms 0.580 · p50 0.145 · p95 1.331 · p99 2.035 · max 2.548 | FAIL |
| zone:Z4 core profile (twisted, slots, grooves):scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 65196 · rms 0.137 · p50 0.049 · p95 0.318 · p99 0.516 · max 1.392 | FAIL |
| zone:Z4 core profile (twisted, slots, grooves):cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 221743 · rms 0.436 · p50 0.054 · p95 1.105 · p99 1.983 · max 2.678 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 210548 · rms 5.557 · p50 3.115 · p95 10.452 · p99 11.380 · max 15.616
- scan→CAD masked: n 79172 · rms 0.137 · p50 0.051 · p95 0.311 · p99 0.510 · max 1.392
- CAD→scan unmasked: n 300000 · rms 1.109 · p50 0.068 · p95 2.326 · p99 5.269 · max 6.700
- CAD→scan masked: n 256703 · rms 0.407 · p50 0.054 · p95 0.996 · p99 1.918 · max 2.678
- CAD→scan observable only: n 16562 · rms 0.333 · p50 0.051 · p95 0.671 · p99 1.630 · max 2.568; unobservable fraction 3.15 %

Masks:

- **M1 bristle tufts and loose bristle fragments** (scan_to_cad): soft feature, not modelled: two helical rows of bristle tufts (and loose bristle bits) = scan material radially outside the Ø14.93 core (r 7.465); no rigid feature of the part lies at r>7.6 for z>0 (INTAKE_CARD §1, §4 Z5, §5 #6); fraction 57.54 %; inside n 121140 · rms 7.080 · p50 6.587 · p95 10.705 · p99 11.373 · max 13.301
- **M2 scanner table remnants** (scan_to_cad): scanner turntable surface under the hub rim (the part stood on its drive end); not part of the part; the rim r16.44 is the largest radius of the part; fraction 2.77 %; inside n 5836 · rms 6.515 · p50 5.063 · p95 12.294 · p99 13.893 · max 15.047
- **M2b scanner table fringe upturn** (scan_to_cad): same table remnant curling up to z -3.5 at theta 210-330 deg, r 18.5-32; the part has no material beyond the rim r16.44 below the hub disc; the scan shows an empty radial gap r 17.5-19.5 between rim surface and fringe, so r>=18 cannot hold rim surface; fraction 1.00 %; inside n 2114 · rms 9.234 · p50 8.225 · p95 14.140 · p99 15.043 · max 15.616
- **M3 tuft holes (bristle-filled)** (scan_to_cad): 54 radial tuft holes Ø2.0 are filled with bristle tufts: scan points there are bristle roots (soft), and the CAD hole walls/bottoms (depth assumed) were never seen by the scanner; region = hole cylinder +0.25 mm, located from the 54 Ø2 hole-bottom faces of the frozen STEP and cross-checked against scan tuft roots (52 scan clusters, median offset 1.05 mm = tuft lean); fraction 1.09 %; inside n 2286 · rms 0.099 · p50 0.047 · p95 0.209 · p99 0.357 · max 0.458
- **M3 tuft holes (bristle-filled)** (cad_to_scan): 54 radial tuft holes Ø2.0 are filled with bristle tufts: scan points there are bristle roots (soft), and the CAD hole walls/bottoms (depth assumed) were never seen by the scanner; region = hole cylinder +0.25 mm, located from the 54 Ø2 hole-bottom faces of the frozen STEP and cross-checked against scan tuft roots (52 scan clusters, median offset 1.05 mm = tuft lean); fraction 8.19 %; inside n 24584 · rms 1.385 · p50 1.159 · p95 2.424 · p99 2.536 · max 2.669
- **M4 rim end face (assumed, rested on table)** (cad_to_scan): the hub rim end face z -6.47 rested on the scanner table and was never scanned; the CAD closes it flat (assumed); its CAD->scan distance is a coverage fact, not a surface deviation; fraction 5.82 %; inside n 17471 · rms 3.972 · p50 4.316 · p95 5.983 · p99 6.456 · max 6.700
- **M5 idler bore bottom (assumed)** (cad_to_scan): idler bore seen only to 3.8 mm depth; the flat bottom at the deepest seen z (158.17) is assumed geometry, never scanned; fraction 0.41 %; inside n 1242 · rms 1.789 · p50 1.557 · p95 2.942 · p99 3.363 · max 3.623

Zones:

- Z1 drive dog (blades + gap floor) [whole] scan_to_cad: unmasked n 4488 · rms 0.113 · p50 0.048 · p95 0.225 · p99 0.422 · max 1.113 | masked n 4488 · rms 0.113 · p50 0.048 · p95 0.225 · p99 0.422 · max 1.113
- Z1 drive dog (blades + gap floor) [whole] cad_to_scan: unmasked n 18471 · rms 0.099 · p50 0.051 · p95 0.205 · p99 0.334 · max 0.761 | masked n 18471 · rms 0.099 · p50 0.051 · p95 0.205 · p99 0.334 · max 0.761
- Z2 hub discs r15.20 r16.44 [whole] scan_to_cad: unmasked n 6454 · rms 0.145 · p50 0.074 · p95 0.311 · p99 0.454 · max 0.825 | masked n 6454 · rms 0.145 · p50 0.074 · p95 0.311 · p99 0.454 · max 0.825
- Z2 hub discs r15.20 r16.44 [whole] cad_to_scan: unmasked n 11588 · rms 0.090 · p50 0.046 · p95 0.193 · p99 0.272 · max 0.472 | masked n 11588 · rms 0.090 · p50 0.046 · p95 0.193 · p99 0.272 · max 0.472
- Z3 idler counterbore and bore [whole] scan_to_cad: unmasked n 1992 · rms 0.157 · p50 0.078 · p95 0.327 · p99 0.561 · max 0.881 | masked n 1992 · rms 0.157 · p50 0.078 · p95 0.327 · p99 0.561 · max 0.881
- Z3 idler counterbore and bore [whole] cad_to_scan: unmasked n 7026 · rms 0.918 · p50 0.208 · p95 2.205 · p99 2.901 · max 3.623 | masked n 5784 · rms 0.580 · p50 0.145 · p95 1.331 · p99 2.035 · max 2.548
- Z4 core profile (twisted, slots, grooves) [whole] scan_to_cad: unmasked n 67482 · rms 0.136 · p50 0.049 · p95 0.314 · p99 0.512 · max 1.392 | masked n 65196 · rms 0.137 · p50 0.049 · p95 0.318 · p99 0.516 · max 1.392
- Z4 core profile (twisted, slots, grooves) [whole] cad_to_scan: unmasked n 247569 · rms 0.614 · p50 0.063 · p95 1.656 · p99 2.372 · max 3.623 | masked n 221743 · rms 0.436 · p50 0.054 · p95 1.105 · p99 1.983 · max 2.678
- Z5 bristle zone [region] scan_to_cad: unmasked n 121140 · rms 7.080 · p50 6.587 · p95 10.705 · p99 11.373 · max 13.301 | masked n 0
- Z5 bristle zone [region] cad_to_scan: unmasked n 0 | masked n 0
- I1 rim end face (unscanned) [interior] cad_to_scan: unmasked n 17471 · rms 3.972 · p50 4.316 · p95 5.983 · p99 6.456 · max 6.700 | masked n 0
- I2 idler bore bottom (unscanned) [interior] cad_to_scan: unmasked n 1242 · rms 1.789 · p50 1.557 · p95 2.942 · p99 3.363 · max 3.623 | masked n 0
- B hub z<0 [region] scan_to_cad: unmasked n 18425 · rms 4.821 · p50 0.191 · p95 11.396 · p99 14.009 · max 15.616 | masked n 10475 · rms 0.135 · p50 0.063 · p95 0.289 · p99 0.445 · max 1.113
- B hub z<0 [region] cad_to_scan: unmasked n 40334 · rms 2.615 · p50 0.121 · p95 5.530 · p99 6.300 · max 6.700 | masked n 22863 · rms 0.098 · p50 0.047 · p95 0.212 · p99 0.321 · max 0.761
- B core z 0-80 [region] scan_to_cad: unmasked n 114574 · rms 6.003 · p50 4.335 · p95 10.682 · p99 11.381 · max 12.913 | masked n 33653 · rms 0.152 · p50 0.049 · p95 0.363 · p99 0.536 · max 1.392
- B core z 0-80 [region] cad_to_scan: unmasked n 130215 · rms 0.479 · p50 0.053 · p95 1.314 · p99 2.169 · max 2.572 | masked n 115666 · rms 0.190 · p50 0.045 · p95 0.404 · p99 0.807 · max 1.571
- B core z 80-140 [region] scan_to_cad: unmasked n 64866 · rms 5.411 · p50 3.130 · p95 10.060 · p99 10.668 · max 13.301 | masked n 23246 · rms 0.118 · p50 0.044 · p95 0.245 · p99 0.498 · max 0.808
- B core z 80-140 [region] cad_to_scan: unmasked n 91144 · rms 0.702 · p50 0.068 · p95 1.848 · p99 2.438 · max 2.669 | masked n 81109 · rms 0.539 · p50 0.056 · p95 1.397 · p99 2.212 · max 2.560
- B idler end z>140 [region] scan_to_cad: unmasked n 12683 · rms 1.887 · p50 0.070 · p95 5.569 · p99 9.513 · max 10.414 | masked n 11798 · rms 0.127 · p50 0.064 · p95 0.263 · p99 0.441 · max 0.881
- B idler end z>140 [region] cad_to_scan: unmasked n 38307 · rms 0.697 · p50 0.096 · p95 1.806 · p99 2.409 · max 3.623 | masked n 37065 · rms 0.628 · p50 0.090 · p95 1.667 · p99 2.261 · max 2.678

Over-band scan→CAD points (> 0.8 mm): 125182 (59.455 %) in 4 clusters ≥ 20 pts.

- cluster 0: n 59805, centroid [5.179, -6.497, 63.849], r [8.135, 20.764], θ [0.0, 360.0], max 13.301 — bristle tuft row (soft, not modelled), inside named mask M1. Clusters are computed by deviation_gate.py on UNMASKED distances
- cluster 1: n 57658, centroid [-4.403, 6.889, 64.342], r [7.984, 19.621], θ [0.0, 360.0], max 12.158 — second bristle tuft row (soft), inside named mask M1
- cluster 2: n 7647, centroid [-4.437, -3.793, -6.413], r [17.222, 32.051], θ [0.0, 359.9], max 15.616 — scanner table and its upturned fringe under the hub rim, inside named masks M2/M2b
- cluster 3: n 49, centroid [1.917, 5.798, 1.385], r [5.598, 6.644], θ [68.0, 76.4], max 1.392 — UNEXPLAINED

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | finding | 4 scan->CAD over-band clusters; unexplained: [3] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | graded after QA's own ICP onto the raw scan; T_refine never written back; datum audit report-only; no expected value from params.json. M3 hole regions were located from the frozen STEP's 54 hole-bottom faces (they only select the CAD's own assumed surfaces) and cross-checked against scan tuft roots. The builder's self-check (MODELING_PLAN §8) is a consistency check, not evidence, and was not used. |
| CHK-LIKE4LIKE | n/a | iteration 1: no superseded QA to compare |
| CHK-INDEP | pass | separate agent context, QA-owned scripts; organisational independence not claimed (same orchestrator session) |
| CHK-FILLET | pass | export_check.json fillets: [] and MODELING_PLAN §5 plans none; nothing silently skipped. Unmodelled hub-step chamfer / slot-mouth blends are declared simplifications |
| CHK-PATCHWORK | pass | census 184 faces, analytic area share 0.249; the bspline faces come from one twisted extrude (extrude_linear_with_rotation, helicoids). model.py grep: no loft / ruled loft / polyline stack of scan slices (make_polygon only in a revolved (r,z) helper) |
| CHK-ENUM | finding | MISSING FEATURE: all 4 slots have an undercut foot in the scan. Slot 0 scan floor tangential p2/p98 -1.038/1.133 mm vs CAD -0.524/0.714; it is absent from the intake feature list and the CAD. Also a local hub/core recess beside the theta~72 deg slot entry. No photos, so no photo cross-check. 54 CAD tuft holes vs 52 scan tuft-root clusters (merged tufts). |
| CHK-ACHIEVABLE | n/a | no Tier-1 run (no calipers) |
| PHOTO-PLAUSIBILITY | n/a | no photos supplied (input/photos empty) |

## Misses, per region

- scan_to_cad:masked: p95 0.311 max 1.392 vs 0.3/0.8
- cad_to_scan_observable: p95 0.671 max 2.568 vs 0.3/0.8
- zone:Z1 drive dog (blades + gap floor):scan_to_cad: p95 0.225 max 1.113 vs 0.3/0.8
- zone:Z2 hub discs r15.20 r16.44:scan_to_cad: p95 0.311 max 0.825 vs 0.3/0.8
- zone:Z3 idler counterbore and bore:scan_to_cad: p95 0.327 max 0.881 vs 0.3/0.8
- zone:Z3 idler counterbore and bore:cad_to_scan: p95 1.331 max 2.548 vs 0.3/0.8
- zone:Z4 core profile (twisted, slots, grooves):scan_to_cad: p95 0.318 max 1.392 vs 0.3/0.8
- zone:Z4 core profile (twisted, slots, grooves):cad_to_scan: p95 1.105 max 2.678 vs 0.3/0.8
- **core slots, scan->CAD (whole part p95, Z4)**: MODELLING: the real slots have an undercut foot at r about 4.9-5.3 that is wider than the 1.24 mm neck. The CAD slot is straight. 5021 scan points lie in the undercut lobes inside the CAD solid (s2c p95 0.535, max 0.755), which is 53.1 % of the masked scan->CAD points over 0.3 mm. They are the largest single contributor to the masked p95 of 0.311 vs 0.30. Options: measure the foot width/height on scan sections (qa/overlays/slot_xsection_qa.png) and add it to the swept profile (still one twisted extrude); re-verify
- **hub/core junction beside the slot entry at theta ~68-76 deg (Z1 and scan->CAD cluster 3)**: UNRESOLVED rigid-geometry miss: 57 scan points over 0.8 mm at z -0.250..2.133, r 5.346..6.644, max 1.392. Scan surface sits inside the CAD solid. A recess or slot run-out the CAD lacks, at one of the four slot entries only. Treated as a missing feature until disproven (P03 lesson) Options: inspect it on scan sections or a photo; model it if real; if it is debris, declare that at intake with evidence
- **core slot interiors, CAD->scan (observable p95/max, Z4, idler end)**: COVERAGE: 98.2 % of masked CAD->scan points over 0.8 mm lie on slot walls/floors. Where the scan sees the slot floor it matches the CAD (scan floor r p50 4.976 vs CAD 4.882, slot 0). In 8-40 mm z-windows per slot the floor is hidden under a ragged surface at r 6-7.2 (material lodged in the slots: bristles/hair/debris; qa/overlays/slot_floor_profile_qa.png). As a diagnostic (not a gate), the masked CAD->scan without slot interiors reads p95 0.206. The ray test counts these surfaces as line-of-sight observable. Options: this cannot be fixed in geometry. Re-scan with cleaned slots, or have an intake/DECISIONS entry declare a slot-occupant occlusion mask with evidence (then re-verify with that mask's leave-one-out reported). It was NOT masked here because it was not declared before grading
- **Z2 hub discs, Z3 idler bore/counterbore (scan->CAD p95 just over)**: hub step/rim edge breaks not modelled (declared simplification, hub-step chamfer) and the slot/counterbore crossing at the idler end; bore wall below ~z 159 only partly seen Options: model the hub-step chamfer from scan sections; recheck after the slot-foot fix

## Declared limitations (each with its re-run trigger)

1. Decimated scan only (391,998 faces, owner's export): every deviation number is INSPECTION ONLY, not an official grade — **Re-run trigger:** full-res scan available
2. Tier-1 not run: no calipers. Every dimension is ABSENT, not passed — **Re-run trigger:** caliper sheet intake/MEASUREMENTS.md filled
3. Absolute scale not caliper-verified (CHK-SCALE finding at intake; units assumed mm, no scale applied) — **Re-run trigger:** caliper sheet intake/MEASUREMENTS.md filled
4. No photos: CHK-ENUM/photo plausibility could only use the scan — **Re-run trigger:** photos of the part supplied
5. Masked numbers: the named masks remove M1 bristle tufts and loose bristle fragments (scan_to_cad) 57.54 %, M2 scanner table remnants (scan_to_cad) 2.77 %, M2b scanner table fringe upturn (scan_to_cad) 1.00 %, M3 tuft holes (bristle-filled) (scan_to_cad) 1.09 %, M3 tuft holes (bristle-filled) (cad_to_scan) 8.19 %, M4 rim end face (assumed, rested on table) (cad_to_scan) 5.82 %, M5 idler bore bottom (assumed) (cad_to_scan) 0.41 %. Unmasked numbers are reported beside the masked ones. The observable CAD->scan figure also excludes the CAD-side masks, via the wrapper workaround for a skill defect — **Re-run trigger:** observable_split fixed to honour CAD masks in stl-re-verify; re-run verify
6. Assumed, never-scanned CAD surfaces (rim end face, hub interior, tuft-hole depth, idler bore bottom) are unverified — **Re-run trigger:** caliper sheet intake/MEASUREMENTS.md filled (ENV-Z, bore depth) or a scan of the drive end face

## Claim boundary

Not a deliverable. This is an iteration-1, inspection-only (decimated scan), scan-only result. The CAD lacks the slot undercut and a local hub recess, and must not be used for manufacture, tooling or fit checks. It is not evidence about the unscanned rim end face, hub interior, tuft-hole depth or bore bottom.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._

## Supplementary evidence (appended by qa/append_verdict_notes.py; numbers read from JSON)

- **gate.json**: verdict `REVISE`, errors [], allowed ['BAND_NOT_MET', 'HALT', 'REVISE'], hash unchanged True.
- **ICP, both runs** (the cap was raised once, as SKILL §5 allows). Run 1 (`registration_run1_cap60.json`): converged False after 60/60 iterations, 0.4017° / 0.0369 mm, still sliding by about 0.00027° per iteration. Run 2 (`registration.json`, the gate): converged True after 88/1000 iterations, 0.4045° / 0.0371 mm. Why the cap was raised: a constant-twist helicoid is invariant under a screw motion, so only the hub and the idler end pin rotation and axial shift. ICP reference masks M1/M2/M2b/M3 removed 249315 scan faces.
- **Builder datum frame vs post-ICP** (run-contract §12, `deviation_datum.json`): scan→CAD masked n 78533 · p95 0.314 · max 1.353 vs post-ICP n 79172 · p95 0.311 · max 1.392; CAD→scan observable n 16564 · p95 0.672 · max 2.638 vs post-ICP n 16562 · p95 0.671 · max 2.568. The two frames agree, so this is not a datum problem.
- **Datum audit** (report-only, `qa/datum_spec.json` written from INTAKE_CARD §6): axis 0.0462°, origin 0.0337 mm, total rotation 0.8883°, which is almost all clock (Fourier on 4 blades with a ±25° circular-mean refinement). The QA ICP clock correction is 0.4045°. Not blocking.
- **Observability** (`observability.params`): {'method': 'ray cone on CAD (OD gate.py:57-84)', 'subsample': 20000, 'seed': 5, 'far_mm': 0.5, 'cone_deg': 60.0, 'n_ring': 6, 'offset_mm': 0.05, 'max_range_mm': None, 'helper': [0.3, 0.5, 0.8], 'helper_switched_for_n_points': 100, 'ray_engine': 'trimesh.ray.ray_triangle.RayMeshIntersector', 'chunk_used': 100, 'workaround': 'qa/workaround_deviation_wrapper.py (D-a chunk, D-b CAD masks on observable)'}. Ray-test unobservable fraction 3.15 %. Observable CAD→scan WITHOUT the CAD masks (the script's own semantics, kept for the record): n 19370 · p95 2.297 · max 6.510. With CAD masks M3/M4/M5 (gated): n 16562 · p95 0.671 · max 2.568. CAD-mask share of the subsample: 0.1460.
- **Raw CAD→scan** (reported, not gated): n 300000 · p95 2.326 · max 6.700. **Raw scan→CAD** (unmasked): n 210548 · p95 10.452 · max 15.616.
- **Tier-1**: not run. Scan-only job: no input/MEASUREMENTS.md exists and the caliper request intake/MEASUREMENTS.md was not filled by the owner (DECISIONS.md 2026-09-30 MEASUREMENTS). Regime baseline-skill has tier1_abs_mm = null. sim_caliper.py therefore not run; every dimension is ABSENT, not passed. Re-run trigger: caliper sheet intake/MEASUREMENTS.md filled (and registered via init_run.py rehash).
- **Unobservable / not chased**: the rim end face (M4), tuft-hole walls and depth (M3, CAD side) and the idler bore bottom (M5) are reported as unobservable assumed geometry; see the I1/I2 zones for their raw CAD→scan. The hub interior is modelled solid and has no CAD surface, so there is nothing to grade. The scan pieces intake called 'loose bristle fragments' at r<7.6 sit on the slot floors (r about 4.7-5.5), so they were NOT masked and are graded as rigid geometry.
- **Overlays**: `qa/overlays/overlay.png` (+ `overlay.json`, every panel has scan trace; drawn in the builder datum frame because overlay.py takes no registration). QA's own zoomed plots: `qa/overlays/slot_xsection_qa.png` (stacked, untwisted slot sections: the undercut foot) and `qa/overlays/slot_floor_profile_qa.png` (slot-floor radius along z: floor seen = matches CAD; floor gaps = ragged material at r 6-7.2). Diagnostic numbers: `qa/slot_diagnostic.json` (not a gate).
- **Masks were declared before any deviation run** (`qa/masks.json#policy`). No mask was added after seeing results. The slot-interior coverage gap was deliberately left unmasked.

## Skill defects found

1. `observability.py observable_split`: the ray chunk is hard-coded to 2000 with no CLI option. On this 170 mm part (455k-triangle CAD tessellation, long axial cone rays) `deviation_gate.py` was OOM-killed (exit 137) on a 15 GB box. Workaround: `qa/workaround_deviation_wrapper.py` patches chunk=100. Rays are independent, so the per-ray results are unchanged.
2. `observable_split` ignores the `--masks` CAD-side masks. Declared never-scanned surfaces that are line-of-sight visible (the rim end face that sat on the table) therefore enter the gated `cad_to_scan_observable`. Same wrapper: CAD region masks are also removed from the observable subset, and the unmasked observable stats are kept as `observability.observable_unmasked`.
3. `deviation_gate.py over_band_clusters` is computed on UNMASKED distances and lists only the top 12. Masked bristle/table/tuft-hole clusters crowd out rigid-geometry clusters, and CHK-CLUSTER is keyed to that list. Here CAD→scan had 69 clusters with only 12 listed, and the rigid slot-interior clusters were found only by QA's own analysis.
4. `verdict.py gated_results` gates `functional_interface` zones only at the regime's `interface_max_mm`, ignoring the zone's own `band_max` that `deviation_gate.py` honours. Under baseline-skill (`interface_max_mm` null), functional zones declared 'band = regime' at intake would go ungated. Workaround: Z1-Z4 declared as kind `whole`.
5. `verdict.py render` has no section for ICP run history, datum-frame stats, unmasked observable stats, Tier-1 skip reason or skill defects. They are appended here by script.
6. `overlay.py` takes no `--registration`, so it cannot draw post-ICP. It also has no zoom, which leaves 170 mm radial panels unreadable at feature scale. Supplemented with QA's own zoomed plots.
7. ICP default cap 60 (B02 parameter) is too low for twisted/axisymmetric parts (a known open question in SKILL.md). Converged at the raised cap.
8. (suspected) `datum_audit.py` clock: the ±25° circular-mean refinement after the Fourier phase is biased on an asymmetric (pinwheel) blade mass. Its 0.89° clock difference disagrees with QA's own ICP (0.40°). Report-only, not investigated further.
9. `step_check.py single_valid_closed_solid` does not include the fine-tessellation watertight result that SKILL §3 lists as part of validity. It was watertight here, so there is no effect on this run.
