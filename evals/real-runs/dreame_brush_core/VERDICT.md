# VERDICT: BAND_NOT_MET

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: Verify ran in a separate agent context from the builder, with its own code: stl-re-verify scripts, its own ICP, and its own masks/zones/datum spec. No builder number, params.json, PARAM_TABLE, build_log or measure/figures were used. model.py was only grepped. Organisational independence is NOT claimed: the same orchestrator session spawned both builder and verifier.

Scan: `input/scan.stl` (DECIMATED, inspection only), label **INSPECTION ONLY**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `dreame_brush_core_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 28731.545 mm³ | PASS |
| Validity `dreame_brush_core.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 28731.545 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.888° / origin 0.034 mm / points p95 0.322 max 0.499 mm | outside (not blocking) |
| Registration (ICP) | converged | 94/1000 its, 0.435° / 0.045 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 78181 · rms 0.103 · p50 0.048 · p95 0.213 · p99 0.347 · max 1.177 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 15209 · rms 0.263 · p50 0.048 · p95 0.415 · p99 1.216 · max 2.636 | FAIL |
| zone:Z1 drive dog (blades + gap floor):scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 4486 · rms 0.109 · p50 0.048 · p95 0.225 · p99 0.416 · max 0.853 | FAIL |
| zone:Z1 drive dog (blades + gap floor):cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 17459 · rms 0.099 · p50 0.052 · p95 0.203 · p99 0.347 · max 0.734 | PASS |
| zone:Z2 hub discs r15.20 r16.44:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 6451 · rms 0.146 · p50 0.077 · p95 0.309 · p99 0.457 · max 0.816 | FAIL |
| zone:Z2 hub discs r15.20 r16.44:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 10975 · rms 0.092 · p50 0.051 · p95 0.190 · p99 0.268 · max 0.462 | PASS |
| zone:Z3 idler counterbore and bore:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 1969 · rms 0.147 · p50 0.077 · p95 0.288 · p99 0.481 · max 0.865 | FAIL |
| zone:Z3 idler counterbore and bore:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 5785 · rms 0.615 · p50 0.157 · p95 1.364 · p99 2.117 · max 2.531 | FAIL |
| zone:Z4 core profile (twisted, slots, grooves):scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 64228 · rms 0.096 · p50 0.045 · p95 0.196 · p99 0.314 · max 1.177 | FAIL |
| zone:Z4 core profile (twisted, slots, grooves):cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 204865 · rms 0.372 · p50 0.052 · p95 0.727 · p99 1.989 · max 2.655 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 210548 · rms 5.556 · p50 3.116 · p95 10.449 · p99 11.378 · max 15.614
- scan→CAD masked: n 78181 · rms 0.103 · p50 0.048 · p95 0.213 · p99 0.347 · max 1.177
- CAD→scan unmasked: n 300000 · rms 1.109 · p50 0.075 · p95 2.318 · p99 5.223 · max 6.691
- CAD→scan masked: n 237843 · rms 0.348 · p50 0.053 · p95 0.660 · p99 1.853 · max 2.655
- CAD→scan observable only: n 15209 · rms 0.263 · p50 0.048 · p95 0.415 · p99 1.216 · max 2.636; unobservable fraction 6.67 %

Masks:

- **M1 bristle tufts and loose bristle fragments** (scan_to_cad): soft feature, not modelled: two helical rows of bristle tufts (and loose bristle bits) = scan material radially outside the Ø14.93 core (r 7.465); no rigid feature of the part lies at r>7.6 for z>0 (INTAKE_CARD §1, §4 Z5, §5 #6); fraction 57.52 %; inside n 121100 · rms 7.081 · p50 6.590 · p95 10.704 · p99 11.371 · max 13.313
- **M2 scanner table remnants** (scan_to_cad): scanner turntable surface under the hub rim (the part stood on its drive end); not part of the part; the rim r16.44 is the largest radius of the part; fraction 2.80 %; inside n 5891 · rms 6.526 · p50 5.069 · p95 12.338 · p99 13.917 · max 15.034
- **M2b scanner table fringe upturn** (scan_to_cad): same table remnant curling up to z -3.5 at theta 210-330 deg, r 18.5-32; the part has no material beyond the rim r16.44 below the hub disc; the scan shows an empty radial gap r 17.5-19.5 between rim surface and fringe, so r>=18 cannot hold rim surface; fraction 0.98 %; inside n 2063 · rms 9.254 · p50 8.263 · p95 14.132 · p99 15.036 · max 15.614
- **M3 tuft holes (bristle-filled)** (scan_to_cad): 54 radial tuft holes Ø2.0 are filled with bristle tufts: scan points there are bristle roots (soft), and the CAD hole walls/bottoms (depth assumed) were never seen by the scanner; region = hole cylinder +0.25 mm, located from the 54 Ø2 hole-bottom faces of the frozen STEP and cross-checked against scan tuft roots (52 scan clusters, median offset 1.05 mm = tuft lean); fraction 1.09 %; inside n 2289 · rms 0.099 · p50 0.047 · p95 0.213 · p99 0.354 · max 0.466
- **M6s slot occupants (scan side)** (scan_to_cad): declared slot-occupant occlusion (DECISIONS.md 2026-10-01 OTHER, before the it2 re-grade): material lodged in the slots (ragged surface at r 6-7.2: hair/bristle/debris) is not part of the rigid core, and where it hides the slot floor the CAD slot walls/foot/floor were never seen. Located from the scan per slot and 1 mm z-bin; bins without an occupant are not masked; fraction 0.49 %; inside n 1024 · rms 0.359 · p50 0.296 · p95 0.593 · p99 0.642 · max 0.712
- **M3 tuft holes (bristle-filled)** (cad_to_scan): 54 radial tuft holes Ø2.0 are filled with bristle tufts: scan points there are bristle roots (soft), and the CAD hole walls/bottoms (depth assumed) were never seen by the scanner; region = hole cylinder +0.25 mm, located from the 54 Ø2 hole-bottom faces of the frozen STEP and cross-checked against scan tuft roots (52 scan clusters, median offset 1.05 mm = tuft lean); fraction 7.76 %; inside n 23268 · rms 1.386 · p50 1.158 · p95 2.418 · p99 2.542 · max 2.673
- **M4 rim end face (assumed, rested on table)** (cad_to_scan): the hub rim end face z -6.47 rested on the scanner table and was never scanned; the CAD closes it flat (assumed); its CAD->scan distance is a coverage fact, not a surface deviation; fraction 5.49 %; inside n 16464 · rms 3.973 · p50 4.329 · p95 5.969 · p99 6.446 · max 6.691
- **M5 idler bore bottom (assumed)** (cad_to_scan): idler bore seen only to 3.8 mm depth; the flat bottom at the deepest seen z (158.17) is assumed geometry, never scanned; fraction 0.39 %; inside n 1178 · rms 1.794 · p50 1.578 · p95 2.944 · p99 3.316 · max 3.623
- **M6c slot occupants (CAD side, floor hidden)** (cad_to_scan): declared slot-occupant occlusion (DECISIONS.md 2026-10-01 OTHER, before the it2 re-grade): material lodged in the slots (ragged surface at r 6-7.2: hair/bristle/debris) is not part of the rigid core, and where it hides the slot floor the CAD slot walls/foot/floor were never seen. Located from the scan per slot and 1 mm z-bin; bins without an occupant are not masked; fraction 7.08 %; inside n 21247 · rms 1.228 · p50 1.071 · p95 2.173 · p99 2.417 · max 2.547

Zones:

- Z1 drive dog (blades + gap floor) [whole] scan_to_cad: unmasked n 4486 · rms 0.109 · p50 0.048 · p95 0.225 · p99 0.416 · max 0.853 | masked n 4486 · rms 0.109 · p50 0.048 · p95 0.225 · p99 0.416 · max 0.853
- Z1 drive dog (blades + gap floor) [whole] cad_to_scan: unmasked n 17459 · rms 0.099 · p50 0.052 · p95 0.203 · p99 0.347 · max 0.734 | masked n 17459 · rms 0.099 · p50 0.052 · p95 0.203 · p99 0.347 · max 0.734
- Z2 hub discs r15.20 r16.44 [whole] scan_to_cad: unmasked n 6451 · rms 0.146 · p50 0.077 · p95 0.309 · p99 0.457 · max 0.816 | masked n 6451 · rms 0.146 · p50 0.077 · p95 0.309 · p99 0.457 · max 0.816
- Z2 hub discs r15.20 r16.44 [whole] cad_to_scan: unmasked n 10975 · rms 0.092 · p50 0.051 · p95 0.190 · p99 0.268 · max 0.462 | masked n 10975 · rms 0.092 · p50 0.051 · p95 0.190 · p99 0.268 · max 0.462
- Z3 idler counterbore and bore [whole] scan_to_cad: unmasked n 1992 · rms 0.154 · p50 0.077 · p95 0.303 · p99 0.540 · max 0.865 | masked n 1969 · rms 0.147 · p50 0.077 · p95 0.288 · p99 0.481 · max 0.865
- Z3 idler counterbore and bore [whole] cad_to_scan: unmasked n 6989 · rms 0.928 · p50 0.236 · p95 2.208 · p99 2.889 · max 3.623 | masked n 5785 · rms 0.615 · p50 0.157 · p95 1.364 · p99 2.117 · max 2.531
- Z4 core profile (twisted, slots, grooves) [whole] scan_to_cad: unmasked n 67523 · rms 0.105 · p50 0.046 · p95 0.213 · p99 0.386 · max 1.177 | masked n 64228 · rms 0.096 · p50 0.045 · p95 0.196 · p99 0.314 · max 1.177
- Z4 core profile (twisted, slots, grooves) [whole] cad_to_scan: unmasked n 250558 · rms 0.659 · p50 0.071 · p95 1.763 · p99 2.391 · max 3.623 | masked n 204865 · rms 0.372 · p50 0.052 · p95 0.727 · p99 1.989 · max 2.655
- Z5 bristle zone [region] scan_to_cad: unmasked n 121100 · rms 7.081 · p50 6.590 · p95 10.704 · p99 11.371 · max 13.313 | masked n 0
- Z5 bristle zone [region] cad_to_scan: unmasked n 0 | masked n 0
- I1 rim end face (unscanned) [interior] cad_to_scan: unmasked n 16464 · rms 3.973 · p50 4.329 · p95 5.969 · p99 6.446 · max 6.691 | masked n 0
- I2 idler bore bottom (unscanned) [interior] cad_to_scan: unmasked n 1178 · rms 1.794 · p50 1.578 · p95 2.944 · p99 3.316 · max 3.623 | masked n 0
- B hub z<0 [region] scan_to_cad: unmasked n 18451 · rms 4.815 · p50 0.190 · p95 11.383 · p99 14.006 · max 15.614 | masked n 10497 · rms 0.134 · p50 0.065 · p95 0.289 · p99 0.444 · max 0.853
- B hub z<0 [region] cad_to_scan: unmasked n 38603 · rms 2.595 · p50 0.123 · p95 5.521 · p99 6.289 · max 6.691 | masked n 22139 · rms 0.099 · p50 0.050 · p95 0.209 · p99 0.319 · max 0.734
- B core z 0-80 [region] scan_to_cad: unmasked n 114552 · rms 6.003 · p50 4.337 · p95 10.682 · p99 11.380 · max 12.910 | masked n 33113 · rms 0.098 · p50 0.044 · p95 0.190 · p99 0.326 · max 1.177
- B core z 0-80 [region] cad_to_scan: unmasked n 131336 · rms 0.481 · p50 0.059 · p95 1.309 · p99 2.144 · max 2.604 | masked n 115500 · rms 0.194 · p50 0.049 · p95 0.443 · p99 0.718 · max 1.573
- B core z 80-140 [region] scan_to_cad: unmasked n 64865 · rms 5.410 · p50 3.130 · p95 10.058 · p99 10.663 · max 13.313 | masked n 22876 · rms 0.082 · p50 0.042 · p95 0.176 · p99 0.263 · max 0.528
- B core z 80-140 [region] cad_to_scan: unmasked n 92245 · rms 0.775 · p50 0.080 · p95 1.997 · p99 2.446 · max 2.673 | masked n 69038 · rms 0.461 · p50 0.049 · p95 1.060 · p99 2.290 · max 2.520
- B idler end z>140 [region] scan_to_cad: unmasked n 12680 · rms 1.890 · p50 0.068 · p95 5.569 · p99 9.532 · max 10.432 | masked n 11695 · rms 0.121 · p50 0.061 · p95 0.250 · p99 0.415 · max 0.865
- B idler end z>140 [region] cad_to_scan: unmasked n 37816 · rms 0.785 · p50 0.106 · p95 2.010 · p99 2.458 · max 3.623 | masked n 31166 · rms 0.557 · p50 0.079 · p95 1.419 · p99 2.388 · max 2.655
- N1 hub recess beside slot entry (named local miss, not masked) [region] scan_to_cad: unmasked n 172 · rms 0.616 · p50 0.536 · p95 1.047 · p99 1.147 · max 1.177 | masked n 172 · rms 0.616 · p50 0.536 · p95 1.047 · p99 1.147 · max 1.177
- N1 hub recess beside slot entry (named local miss, not masked) [region] cad_to_scan: unmasked n 143 · rms 0.281 · p50 0.190 · p95 0.466 · p99 0.495 · max 0.522 | masked n 143 · rms 0.281 · p50 0.190 · p95 0.466 · p99 0.495 · max 0.522

Over-band scan→CAD points (> 0.8 mm): 125157 (59.443 %) in 4 clusters ≥ 20 pts.

- cluster 0: n 59806, centroid [5.17, -6.494, 63.853], r [8.14, 20.777], θ [0.0, 360.0], max 13.313 — bristle tuft row (soft), inside named mask M1. Clusters are computed on UNMASKED distances
- cluster 1: n 57658, centroid [-4.404, 6.897, 64.335], r [7.989, 19.626], θ [0.0, 360.0], max 12.163 — second bristle tuft row (soft), inside M1
- cluster 2: n 7649, centroid [-4.424, -3.776, -6.416], r [17.216, 32.049], θ [0.0, 359.9], max 15.614 — scanner table and its upturned fringe, inside M2/M2b
- cluster 3: n 35, centroid [1.998, 5.933, 1.268], r [5.721, 6.655], θ [68.0, 76.3], max 1.177 — NAMED LOCAL MISS, not an artefact: the hub recess beside one slot entry, NOT modelled and NOT masked by DECISIONS.md 2026-10-01. It sets the whole-part scan->CAD max (36 points over 0.8, max 1.177). It stays a band miss

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 4 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | graded after QA's own ICP; T_refine not written back; no expected values from params.json. M6 was located from the scan (qa/make_m6_slot_occupants.py); M3 holes come from the STEP's own hole-bottom faces, unchanged since it1 |
| CHK-LIKE4LIKE | finding | protocol changed it1->it2 (declared M6 slot-occupant mask added to the gate and to the ICP reference), so the it2 STEP was also graded under the exact it1 protocol. it1 gate (it1 STEP, it1 protocol): scan->CAD masked p95 0.311 / max 1.392, CAD->scan observable p95 0.671 / max 2.568. it2 STEP under the IDENTICAL it1 protocol (it1 masks, it1 ICP reference; qa/it1_protocol/): scan->CAD masked p95 0.225 / max 1.170, CAD->scan observable p95 0.598 / max 2.640, so this is the geometry-only change. it2 gate (adds the declared M6 slot-occupant mask, also removed from the ICP reference): scan->CAD masked p95 0.213 / max 1.177, CAD->scan observable p95 0.415 / max 2.636, so the remaining improvement comes from the M6 mask (protocol), not from geometry |
| CHK-INDEP | pass | separate agent context, QA-owned scripts; organisational independence not claimed (same orchestrator session) |
| CHK-FILLET | pass | export_check.json fillets: []; no fillet ops planned (MODELING_PLAN §5) |
| CHK-PATCHWORK | pass | census 200 faces, analytic area share 0.234; extra bspline faces = T-slot flare walls from the same single twisted extrude (extrude_linear_with_rotation); model.py grep: no loft / ruled loft / polyline stack |
| CHK-ENUM | finding | T-slot foot now modelled (it1 finding closed: stacked section qa/overlays/slot_xsection_it2_qa.png). Still open: (a) the hub recess beside one slot entry is not modelled, by DECISIONS.md 2026-10-01; (b) DECISIONS.md says INTAKE_CARD §5 feature 2 'now reads 4 T-slots...', but intake/INTAKE_CARD.md is unchanged (still '4 slots, width ≈1.24, flat bottom'), so the record is inconsistent; (c) no photos |
| CHK-ACHIEVABLE | n/a | no Tier-1 run (no calipers) |
| PHOTO-PLAUSIBILITY | n/a | no photos supplied |

## Misses, per region

- scan_to_cad:masked: p95 0.213 max 1.177 vs 0.3/0.8
- cad_to_scan_observable: p95 0.415 max 2.636 vs 0.3/0.8
- zone:Z1 drive dog (blades + gap floor):scan_to_cad: p95 0.225 max 0.853 vs 0.3/0.8
- zone:Z2 hub discs r15.20 r16.44:scan_to_cad: p95 0.309 max 0.816 vs 0.3/0.8
- zone:Z3 idler counterbore and bore:scan_to_cad: p95 0.288 max 0.865 vs 0.3/0.8
- zone:Z3 idler counterbore and bore:cad_to_scan: p95 1.364 max 2.531 vs 0.3/0.8
- zone:Z4 core profile (twisted, slots, grooves):scan_to_cad: p95 0.196 max 1.177 vs 0.3/0.8
- zone:Z4 core profile (twisted, slots, grooves):cad_to_scan: p95 0.727 max 2.655 vs 0.3/0.8
- **hub recess beside one slot entry (scan->CAD whole-part max, Z1/Z4 max)**: declared unmodelled local feature (DECISIONS.md 2026-10-01): 36 scan points over 0.8 mm, max 1.177; asymmetric (1 of 4 entries), so feature vs damage cannot be told without a photo. Outside the recess the masked scan->CAD has 8 isolated points over 0.8 (max 0.969, no cluster >= 20 pts). Whole-part masked scan->CAD p95 0.213 passes Options: (a) human accepts the recess miss (ACCEPT-BAND); (b) photo of the drive end -> model it as a feature (it3) or declare damage; (c) full-res scan
- **slot foot/flare/floor coverage, CAD->scan observable (Z4, idler end)**: COVERAGE, not geometry: 97.6 % of masked CAD->scan points over 0.8 lie in the slots; 8757 of them have no scan point within 0.3 mm / 1 mm z (only 22 do). These are undercut flare/foot surfaces and floor spans the decimated scan never saw, outside the M6c bins (M6c covers only bins where an occupant hides the floor). Diagnostic only: masked CAD->scan without slot interiors p95 0.206. The ray test counts many of these surfaces as line-of-sight observable Options: (a) full-res scan or a re-scan with cleaned slots aimed into the slots; (b) a declared coverage-gap mask located from the scan (intake decision, with leave-one-out); (c) human acceptance. More geometry cannot fix it
- **Z2 hub discs, Z3 idler bore/counterbore (small scan->CAD overs)**: hub step/rim edge break (declared simplification, hub-step chamfer) and bore wall near the assumed bottom; 215 CAD->scan points over 0.8 at z >= 158 outside the slots (bore wall just above the masked bottom, counterbore/slot crossing) Options: optional it3: model the hub-step chamfer; bore depth needs a caliper or photo

## Declared limitations (each with its re-run trigger)

1. Decimated scan only: every deviation number is INSPECTION ONLY — **Re-run trigger:** full-res scan available
2. Tier-1 not run: no calipers. Every dimension is ABSENT, not passed — **Re-run trigger:** caliper sheet intake/MEASUREMENTS.md filled
3. Absolute scale not caliper-verified (CHK-SCALE) — **Re-run trigger:** caliper sheet intake/MEASUREMENTS.md filled
4. No photos: the hub recess cannot be classified as feature or damage — **Re-run trigger:** photos of the drive end supplied
5. Masked numbers: M1 bristle tufts and loose bristle fragments (scan_to_cad) 57.52 %, M2 scanner table remnants (scan_to_cad) 2.80 %, M2b scanner table fringe upturn (scan_to_cad) 0.98 %, M3 tuft holes (bristle-filled) (scan_to_cad) 1.09 %, M6s slot occupants (scan side) (scan_to_cad) 0.49 %, M3 tuft holes (bristle-filled) (cad_to_scan) 7.76 %, M4 rim end face (assumed, rested on table) (cad_to_scan) 5.49 %, M5 idler bore bottom (assumed) (cad_to_scan) 0.39 %, M6c slot occupants (CAD side, floor hidden) (cad_to_scan) 7.08 %. M6 leave-one-out: scan->CAD p95 0.225 / max 1.177, CAD->scan p95 1.291 / max 2.655. The observable CAD->scan figure excludes CAD-side masks (wrapper workaround for a skill defect) — **Re-run trigger:** observable_split fixed to honour CAD masks in stl-re-verify; re-run verify
6. Assumed, never-scanned surfaces (rim end face, hub interior, tuft-hole depth, idler bore bottom) unverified — **Re-run trigger:** caliper sheet intake/MEASUREMENTS.md filled or a scan of the drive end face

## Claim boundary

Not deliverable without a recorded ACCEPT-BAND. This is an iteration-2, inspection-only (decimated), scan-only result. The slot-foot shape is supported by the scan only where the foot was seen. The hub recess is absent from the CAD. Not fit for tooling or fit checks of the slots or the drive-end recess. No claim about the unscanned rim end face, hub interior, tuft-hole depth or bore bottom.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._

## it1 → it2 change (CHK-LIKE4LIKE)

| Run | STEP | protocol | scan→CAD masked | CAD→scan masked | CAD→scan observable | verdict |
|---|---|---|---|---|---|---|
| it1 gate | it1 | it1 (M1-M5) | n 79172 · p95 0.311 · max 1.392 | n 256703 · p95 0.996 · max 2.678 | n 16562 · p95 0.671 · max 2.568 | REVISE |
| it2 STEP, it1 protocol (`qa/it1_protocol/`) | it2 | it1 (M1-M5) | n 79184 · p95 0.225 · max 1.170 | n 259090 · p95 1.291 · max 2.659 | n 16051 · p95 0.598 · max 2.640 | not graded |
| it2 gate | it2 | it1 + declared M6 | n 78181 · p95 0.213 · max 1.177 | n 237843 · p95 0.660 · max 2.655 | n 15209 · p95 0.415 · max 2.636 | BAND_NOT_MET |

Row 1 → row 2 is the like-for-like effect of the geometry change (T-slot foot). Row 2 → row 3 is the effect of the protocol change (the M6 mask declared in DECISIONS.md before this re-grade). ICP: it2 gate 94/1000 iterations, 0.4349° / 0.0454 mm; it1-protocol replay 99/1000 iterations, 0.4285° / 0.0387 mm (same cap 1000 as the it1 gate run).

## Supplementary evidence (appended by qa/append_verdict_notes.py; numbers read from JSON)

- **gate.json**: verdict `BAND_NOT_MET`, errors [], allowed ['BAND_NOT_MET', 'HALT', 'REVISE'], hash unchanged True. Iteration 2 of 3. BAND_NOT_MET needs a recorded human ACCEPT-BAND before delivery.
- **M6 slot occupants** (`qa/m6_slot_occupants.json`, located from the scan): 415 of 648 slot × 1 mm bins hold scan material inside the neck void (scan side masked there); 148 bins also hide the floor (CAD side masked there); 63 bins with neither floor nor occupant are NOT masked (plain coverage gap, still graded).
- **Builder datum frame vs post-ICP** (`deviation_datum.json`): scan→CAD masked n 77053 · p95 0.210 · max 1.146 vs n 78181 · p95 0.213 · max 1.177; CAD→scan observable n 15215 · p95 0.415 · max 2.705 vs n 15209 · p95 0.415 · max 2.636. They agree.
- **Datum audit** (report-only; intake unchanged): axis 0.0462°, origin 0.0337 mm, rotation 0.8883°.
- **Observability**: unobservable fraction 6.67 % (the T-slot undercut adds occluded surface). Observable WITHOUT the CAD masks: n 18666 · p95 2.309 · max 6.481. Params: chunk 100, cone 60.0°, seed 5.
- **Raw CAD→scan** (reported): n 300000 · p95 2.318 · max 6.691. **Raw scan→CAD**: n 210548 · p95 10.449 · max 15.614.
- **Residual diagnostic** (`qa/it2_diagnostic.json`): slot CAD→scan points over 0.8 locally unseen 8757, seen-but-off 22.
- **Tier-1**: not run. Scan-only job: no input/MEASUREMENTS.md exists and the caliper request intake/MEASUREMENTS.md was not filled by the owner (DECISIONS.md 2026-09-30 MEASUREMENTS). Regime baseline-skill has tier1_abs_mm = null. sim_caliper.py therefore not run; every dimension is ABSENT, not passed.
- **Overlays**: `qa/overlays/overlay.png` (same panels as it1, every panel has scan) and `qa/overlays/slot_xsection_it2_qa.png` (stacked untwisted T-slot sections, scan vs CAD; CAD points still over 0.8 shown in orange).

## Skill defects found

Carried from it1 (see `_it1_SUPERSEDED/qa/VERDICT.md`), still present and still worked around with the same wrapper: (1) observability chunk OOM; (2) observable split ignores CAD masks; (3) clusters computed on unmasked distances, top 12 only; (4) functional_interface zones ungated under baseline-skill; (5) render lacks sections; (6) overlay.py has no registration or zoom; (7) low default ICP cap; (8) suspected datum-audit clock bias; (9) validity ignores the watertight tessellation.

New in it2:
10. The predicate language has no twisted/helical (theta-vs-z) term. A mask that follows a twisted slot had to be written as an `any_of` of 1126 short z-bin boxes, each of which re-computes features for every point.
11. `verdict.py` has no slot for a like-for-like replay under the previous protocol (CHK-LIKE4LIKE evidence). It only lists `deviation_run*.json` written by `--supersede` in the same qa/ folder, so the it1-protocol replay lives in `qa/it1_protocol/` and is quoted here.
12. (process, not a script) DECISIONS.md says INTAKE_CARD §5 feature 2 was updated to the T-slot, but intake/INTAKE_CARD.md is unchanged. Nothing in the skills checks that a cited intake edit actually happened.
