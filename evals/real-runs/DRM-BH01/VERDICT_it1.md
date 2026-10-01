# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: fresh verifier subagent context that did not build the model; QA scripts from skills/stl-re-verify only plus QA-own diagnostics in qa/tools/; build/model.py only grepped read-only; measure/params.json, measure/geometry.json, builder self-check numbers (DECISIONS dev v7 p95 ~2.9) and scratchpad builder tools NOT used as expected values

Scan: `input/scan.stl` (DECIMATED, inspection only), label **INSPECTION ONLY**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `dreame_brushes_housing_datum.step` | 1 valid closed solid | solids 1, valid False, naked edges 0, V 136435.021 mm³ | FAIL |
| Validity `dreame_brushes_housing.step` | 1 valid closed solid | solids 1, valid False, naked edges 0, V 136435.021 mm³ | FAIL |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.526° / origin 0.223 mm / points p95 0.685 max 0.800 mm | outside (not blocking) |
| Registration (ICP) | converged | 48/60 its, 0.061° / 0.151 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 191658 · rms 1.303 · p50 0.127 · p95 1.937 · p99 6.018 · max 16.303 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 19098 · rms 0.635 · p50 0.095 · p95 1.309 · p99 2.912 · max 7.709 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 196686 · rms 1.354 · p50 0.130 · p95 2.067 · p99 6.700 · max 16.303
- scan→CAD masked: n 191658 · rms 1.303 · p50 0.127 · p95 1.937 · p99 6.018 · max 16.303
- CAD→scan unmasked: n 300000 · rms 0.853 · p50 0.102 · p95 1.940 · p99 4.172 · max 7.885
- CAD→scan masked: n 275443 · rms 0.765 · p50 0.095 · p95 1.657 · p99 3.772 · max 7.885
- CAD→scan observable only: n 19098 · rms 0.635 · p50 0.095 · p95 1.309 · p99 2.912 · max 7.709; unobservable fraction 4.51 %

Masks:

- **M1 loose motor wires F11** (scan_to_cad): loose, non-rigid motor wires; declared not modelled at intake; fraction 0.82 %; inside n 1613 · rms 4.396 · p50 2.211 · p95 9.052 · p99 10.137 · max 11.119
- **M2 gearbox cover screw heads** (scan_to_cad): COTS screw heads in the 4 gearbox-cover sockets; screw-head detail declared not modelled; fraction 1.74 %; inside n 3415 · rms 1.062 · p50 0.494 · p95 2.170 · p99 3.356 · max 4.123
- **M2 gearbox cover screw heads** (cad_to_scan): COTS screw heads in the 4 gearbox-cover sockets; screw-head detail declared not modelled; fraction 1.29 %; inside n 3867 · rms 0.744 · p50 0.145 · p95 1.175 · p99 3.929 · max 4.852
- **M3 open boundary** (cad_to_scan): distance from CAD to a scan hole EDGE is not a surface deviation (scan has 192 open loops); fraction 7.09 %; inside n 21266 · rms 1.625 · p50 0.532 · p95 3.866 · p99 5.759 · max 7.288

Zones:

- T1 bore wall [functional_interface] scan_to_cad: unmasked n 35324 · rms 0.389 · p50 0.094 · p95 0.842 · p99 1.742 · max 4.147 | masked n 35324 · rms 0.389 · p50 0.094 · p95 0.842 · p99 1.742 · max 4.147
- T1 bore wall [functional_interface] cad_to_scan: unmasked n 59687 · rms 0.260 · p50 0.075 · p95 0.427 · p99 1.235 · max 3.646 | masked n 58553 · rms 0.259 · p50 0.073 · p95 0.417 · p99 1.247 · max 3.646
- T2 bore wall [functional_interface] scan_to_cad: unmasked n 34725 · rms 0.520 · p50 0.095 · p95 0.764 · p99 2.138 · max 9.718 | masked n 34725 · rms 0.520 · p50 0.095 · p95 0.764 · p99 2.138 · max 9.718
- T2 bore wall [functional_interface] cad_to_scan: unmasked n 71359 · rms 1.023 · p50 0.099 · p95 2.066 · p99 5.291 · max 7.321 | masked n 66328 · rms 0.882 · p50 0.093 · p95 1.994 · p99 4.792 · max 7.321
- flange top cover mating [functional_interface] scan_to_cad: unmasked n 2805 · rms 0.219 · p50 0.127 · p95 0.221 · p99 0.994 · max 1.834 | masked n 2805 · rms 0.219 · p50 0.127 · p95 0.221 · p99 0.994 · max 1.834
- flange top cover mating [functional_interface] cad_to_scan: unmasked n 6130 · rms 0.271 · p50 0.139 · p95 0.216 · p99 1.302 · max 3.884 | masked n 6096 · rms 0.272 · p50 0.139 · p95 0.216 · p99 1.304 · max 3.884
- labyrinth edge [functional_interface] scan_to_cad: unmasked n 37617 · rms 2.544 · p50 0.134 · p95 6.319 · p99 12.573 · max 16.303 | masked n 36919 · rms 2.406 · p50 0.129 · p95 4.122 · p99 12.588 · max 16.303
- labyrinth edge [functional_interface] cad_to_scan: unmasked n 48430 · rms 0.670 · p50 0.081 · p95 1.192 · p99 3.521 · max 7.091 | masked n 45110 · rms 0.669 · p50 0.077 · p95 1.093 · p99 3.653 · max 7.091
- gearbox end face [functional_interface] scan_to_cad: unmasked n 1860 · rms 0.106 · p50 0.063 · p95 0.212 · p99 0.428 · max 0.731 | masked n 1600 · rms 0.075 · p50 0.062 · p95 0.106 · p99 0.185 · max 0.671
- gearbox end face [functional_interface] cad_to_scan: unmasked n 11218 · rms 0.395 · p50 0.067 · p95 0.578 · p99 2.189 · max 4.240 | masked n 9804 · rms 0.388 · p50 0.063 · p95 0.396 · p99 2.230 · max 4.240
- motor can region [functional_interface] scan_to_cad: unmasked n 18690 · rms 0.749 · p50 0.188 · p95 1.781 · p99 2.791 · max 4.911 | masked n 17775 · rms 0.714 · p50 0.181 · p95 1.655 · p99 2.740 · max 4.911
- motor can region [functional_interface] cad_to_scan: unmasked n 22813 · rms 1.372 · p50 0.156 · p95 3.749 · p99 5.675 · max 6.828 | masked n 18286 · rms 1.130 · p50 0.118 · p95 2.703 · p99 5.555 · max 6.828
- gearbox block interior [interior] scan_to_cad: unmasked n 8510 · rms 0.919 · p50 0.207 · p95 2.130 · p99 2.902 · max 4.123 | masked n 6925 · rms 0.816 · p50 0.187 · p95 1.985 · p99 2.540 · max 3.785
- gearbox block interior [interior] cad_to_scan: unmasked n 13392 · rms 1.398 · p50 0.208 · p95 3.223 · p99 4.706 · max 7.833 | masked n 9018 · rms 1.347 · p50 0.148 · p95 3.145 · p99 4.954 · max 7.833
- zband gearbox z-1_13 [region] scan_to_cad: unmasked n 19832 · rms 0.713 · p50 0.164 · p95 1.779 · p99 2.528 · max 4.123 | masked n 16417 · rms 0.617 · p50 0.148 · p95 1.655 · p99 2.419 · max 3.785
- zband gearbox z-1_13 [region] cad_to_scan: unmasked n 37786 · rms 1.036 · p50 0.124 · p95 2.524 · p99 3.971 · max 7.885 | masked n 30336 · rms 0.979 · p50 0.105 · p95 2.341 · p99 3.854 · max 7.885
- zband motor_troughstart z13_66 [region] scan_to_cad: unmasked n 62298 · rms 2.138 · p50 0.145 · p95 4.027 · p99 11.468 · max 16.303 | masked n 60685 · rms 2.045 · p50 0.141 · p95 3.476 · p99 11.523 · max 16.303
- zband motor_troughstart z13_66 [region] cad_to_scan: unmasked n 94378 · rms 0.848 · p50 0.107 · p95 1.969 · p99 4.146 · max 7.837 | masked n 85594 · rms 0.726 · p50 0.098 · p95 1.680 · p99 3.409 · max 7.837
- zband mid z66_150 [region] scan_to_cad: unmasked n 56588 · rms 0.735 · p50 0.094 · p95 0.832 · p99 4.419 · max 8.279 | masked n 56588 · rms 0.735 · p50 0.094 · p95 0.832 · p99 4.419 · max 8.279
- zband mid z66_150 [region] cad_to_scan: unmasked n 94723 · rms 0.198 · p50 0.079 · p95 0.251 · p99 0.882 · max 2.466 | masked n 91708 · rms 0.175 · p50 0.079 · p95 0.219 · p99 0.742 · max 2.466
- zband plusX_end z150_up [region] scan_to_cad: unmasked n 57968 · rms 0.775 · p50 0.167 · p95 1.883 · p99 3.119 · max 4.723 | masked n 57968 · rms 0.775 · p50 0.167 · p95 1.883 · p99 3.119 · max 4.723
- zband plusX_end z150_up [region] cad_to_scan: unmasked n 73113 · rms 1.206 · p50 0.143 · p95 2.863 · p99 5.507 · max 7.321 | masked n 67805 · rms 1.115 · p50 0.131 · p95 2.592 · p99 5.251 · max 7.321

Over-band scan→CAD points (> 0.8 mm): 27621 (14.043 %) in 118 clusters ≥ 20 pts.

- cluster 0: n 3098, centroid [-20.773, 9.56, 22.99], r [18.108, 35.947], θ [117.8, 183.7], max 9.580 — REAL, missing/misplaced feature: trough-start region under T1 (F07 pockets/funnel; z 10.8-37.8, x -31..-10). Scan walls at y~5 and y~18 and a pocket floor (overlay Z=23) are absent from the CAD; scan material OUTSIDE the CAD (qa/inside_outside.json), p50 2.0 / max 9.6 mm
- cluster 1: n 2200, centroid [-15.45, 58.165, 23.033], r [47.399, 66.284], θ [92.8, 111.8], max 16.303 — REAL, missing body: closed rectangular box beyond the labyrinth edge at the gearbox end (x -24..-3, y 46-63, z 15-28; overlays y=58 and x=-22). Prismatic, so not a wire. Entirely absent from the CAD (p50 9.6 / max 16.3 mm). Part feature or unmodelled assembly item (connector/clip) cannot be decided without photos
- cluster 2: n 1781, centroid [-21.68, 22.415, 68.677], r [23.293, 37.574], θ [122.4, 144.5], max 8.279 — REAL, missing ribs: underside rib/wall structures between the troughs past the motor end (z 59-77, x -28..-13, y 19-30; overlay Z=68). Outside the CAD, p50 3.2 / max 8.3 mm (F09 rib frame incomplete)
- cluster 3: n 1444, centroid [-10.06, 56.659, 163.876], r [51.583, 64.347], θ [90.5, 110.6], max 3.794 — Scan surface INSIDE the CAD solid (latch box on the labyrinth side, z 161-167, y 50-62; overlay Z=165). The scan shows a hollow box, the CAD fills it solid. This is CAD material where the part is hollow (scanned interior surface), p50 1.8 / max 3.8 mm
- cluster 4: n 1387, centroid [-9.176, 39.928, 195.407], r [31.818, 50.925], θ [88.5, 116.9], max 4.428 — REAL, shape error: T2 rounded/ramped +X end (z 186-203; overlay Z=195). The scan curve runs from (-15,25) to (0,48), and the CAD block edges do not follow it. Outside the CAD
- cluster 5: n 1031, centroid [-41.207, 52.168, 45.753], r [62.579, 71.797], θ [124.1, 131.7], max 11.119 — ARTEFACT, declared not modelled: F11 loose motor wires (x -43..-39, y 47-59, z 41-59; organic loops in overlay x=-41). Inside mask M1 (intake F11, DECISIONS PART-CLASS); with or without the mask the band misses
- cluster 6: n 843, centroid [-20.497, 38.83, 204.913], r [33.898, 54.159], θ [104.7, 131.4], max 2.299 — REAL, +X end wall/latch mismatch: z 203.7-205.2, x -27..-12, y 30-48. Overlay Z=204.5 shows scan end-wall area the CAD lacks (drafted end-wall position/extent). Outside the CAD, max 2.3 mm
- cluster 7: n 693, centroid [-35.642, 34.37, 60.516], r [35.451, 61.682], θ [119.1, 149.8], max 2.751 — Scan surface INSIDE the CAD motor envelope at its end (z 58-61). The scanned motor end face/cap lies 1.0-2.75 mm inside the CAD cylinder end, so the motor envelope is over-long or the end cap is recessed
- cluster 8: n 646, centroid [-9.831, 55.327, 202.579], r [51.008, 61.988], θ [90.9, 114.9], max 2.683 — Scan surface INSIDE the CAD at the +X end latch box (z 198-205, y 51-57). A hollow latch box is modelled solid (CAD material where the part is hollow)
- cluster 9: n 547, centroid [-13.937, -2.781, 204.026], r [9.993, 21.133], θ [142.1, 230.7], max 1.984 — Mixed (about half inside, half outside) at the +X end wall near the T1 end (z 203-205, x -19..-7). End-wall position/draft mismatch. This also coincides with the CAD's own tessellation defect (face 1288 at (-11.6, 8.9, 204.0) triangulates 138 mm2 short, qa/tools/tess_diag_datum.json), so part of it is a hole in the CAD mesh
- cluster 10: n 488, centroid [-26.405, 42.545, 64.499], r [42.701, 60.816], θ [118.4, 129.2], max 5.091 — REAL, missing material past the CAD motor end (z 62.6-67.8, x -38..-20): motor end boss/bearing cap or wire exit beyond the modelled can. Outside the CAD, p50 2.6 / max 5.1 mm. Boss vs wires undecidable without photos, so it is treated as an under-modelled motor end
- cluster 11: n 438, centroid [-39.108, 28.329, 49.364], r [42.816, 53.987], θ [141.6, 148.3], max 2.723 — Scan surface INSIDE the CAD motor cylinder (z 47-53, x -45..-35, y 24-33; overlay Z=52, where the scan departs from the CAD circle). The motor can is not cylindrical there (flat/recess), so the CAD envelope is locally oversized

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 12 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | QA ICP (qa/registration.json) is QA-only, never written back to alignment.json; no expected value taken from measure/ or builder code; datum audit fits on raw scan with QA-written regions (qa/datum_spec.json) |
| CHK-LIKE4LIKE | n/a | iteration 1: no _itN_SUPERSEDED/ folder, nothing to compare |
| CHK-INDEP | pass | fresh subagent, own scripts; see independence |
| CHK-FILLET | pass | build/export_check.json and build/fillets.json: fillets [] (none planned, none applied, none FAILED/REDUCED); moulded blends left sharp and declared in MODELING_PLAN §0/§5 -- their deviation is inside the gate numbers |
| CHK-PATCHWORK | pass | census (qa/step_check.json): 1572 faces = 1474 plane + 98 cylinder, analytic area share 100 %, 0 B-spline/ruled; model.py grep: no loft/ruled/spline, make_polygon used only for extruded constant sections and cutting half-spaces (not a stack of scan slices). High planar-face count comes from ribs/slabs/region prisms, reported not gated |
| CHK-ENUM | finding | no photos (cross-check impossible). Scan clusters show features absent or wrong in the CAD: box-shaped body beyond the labyrinth edge at z 15-28 (cluster 1), trough-start walls/pockets (cluster 0), underside ribs z 59-90 (cluster 2), motor end boss (cluster 10), hollow latch boxes at the +X end modelled solid (clusters 3, 8), T2 +X end shape (cluster 4) |
| CHK-ACHIEVABLE | n/a | no Tier-1 (no calipers), nothing to attribute |
| PHOTO-PLAUSIBILITY | n/a | no photos supplied (input/photos empty) |

## Misses, per region

- scan_to_cad:masked: p95 1.937 max 16.303 vs 0.3/0.8
- cad_to_scan_observable: p95 1.309 max 7.709 vs 0.3/0.8
- **GEOMETRY VALIDITY (blocks delivery; REVISE)**: step_check: single_valid_closed_solid = false in both frames. BRepCheck is valid as imported, but after the 0.005 mm / 0.05 rad fine mesh 6 faces and 4 edges are invalid, and the fine tessellation is NOT watertight (17 open edges datum / 14 scan frame). It stays non-watertight at every tolerance tried, 0.005-0.1 mm (qa/tools/tess_sweep.txt). There are 2 non-manifold edges (4 faces each) at datum (-19.6, 26.9, 200.4-202.0) (qa/brep_diag_datum.json). Everything sits at the +X end window/latch-box area, x -19..-10, y 9..27, z 200-204: faces 1265/1266/1269/1287/1288 (1288 triangulates 138 mm2 short). The builder's export_check reported nonmanifold_edges 2 but pass true Options: Rebuild the +X end window/latch-box features (F10/R4) so no two solids touch along a single edge (overlap or separate them by >= 0.05 mm); re-export; confirm BRepCheck valid AFTER meshing and a watertight 0.005/0.05 tessellation in both frames
- **gearbox end z < 13**: scan->CAD p95 1.78 / max 4.12, CAD->scan p95 2.52 / max 7.89. The CAD block is filled where the scan shows the cover plate recesses, screw sockets and inter-part surfaces behind the cover (inside-CAD clusters at z 10-15). Several edge pockets on the +x side of the block do not match (CAD->scan clusters 4, 5, 9, 11) Options: model the cover-plate recesses and screw sockets as cuts; re-place the gearbox outline against the scan; the owner decides whether interior/inter-part surfaces are to be modelled
- **trough start + motor z 13-66**: scan->CAD p95 4.03 / max 16.30. Missing trough-start walls/pockets (cluster 0), a missing box body beyond the labyrinth edge (cluster 1, up to 16.3 mm), motor envelope locally oversized/over-long (clusters 7, 11) and under-modelled motor end (cluster 10). CAD->scan cluster 0 (10,213 pts, z 11-83) is partly scan coverage (34 % of it within 1 mm of a scan open boundary) and partly the misplaced trough-start geometry Options: remeasure and model F07 trough-start walls/funnel and the box at x -24..-3, y 46-63, z 15-28 (photos to decide part vs assembly item); refit the motor can segments and end boss
- **underside ribs z 59-90**: cluster 2 (1,781 pts, max 8.3) and a 285-pt cluster at z 86-90: rib walls between the troughs present in the scan, absent in the CAD Options: add the missing F09 rib walls from scan sections
- **mid troughs z 66-150**: closest to band: scan->CAD p95 0.83 / max 8.28 (the max is rib cluster 2 at the zone edge), CAD->scan p95 0.25 / max 2.47. T1 bore wall zone p95 0.84 / 0.43 (two-way) includes the offset strip and the ~0.3 deg bore bow (warp, L5) Options: after the rib fixes, the remaining warp can only be arbitrated with a full-res scan or calipers
- **+X end z > 150**: scan->CAD p95 1.88 / max 4.72, CAD->scan p95 2.86 / max 7.32. Hollow latch boxes modelled solid (clusters 3, 8; CAD->scan clusters 1, 2, 3, 6, 8), T2 +X end shape (cluster 4), end-wall position/draft (clusters 6, 9), plus the CAD tessellation hole at face 1288 Options: model the latch boxes hollow per the scan sections; refit the T2 end ramp and end-wall planes; fix validity first (same area)

## Declared limitations (each with its re-run trigger)

1. Decimated scan only (owner's ~20 MB export, 391,997 faces): every deviation number is INSPECTION ONLY, not an official grade — **Re-run trigger:** full-res scan available
2. Tier-1 not run: no calipers, scan-only (DECISIONS MEASUREMENTS). No dimension is caliper-verified — **Re-run trigger:** any caliper reading on T1/T2 bore radius, flange height or gearbox end face -> re-run Tier-1
3. Absolute scale not caliper-verified (CHK-SCALE flag at intake; units assumed mm) — **Re-run trigger:** one caliper reading of overall length (~206 mm) or a bore diameter
4. No photos: CHK-ENUM/photo plausibility not possible; clusters 1 and 10 cannot be classed as part feature vs assembly item — **Re-run trigger:** photos of the gearbox end, the labyrinth-side box at z 15-28 and the motor end
5. Datum audit outside the report-only reference: 0.526 deg rotation (axis 0.084 deg, the rest is clock) / 0.223 mm origin; with a tighter flange region 0.486 deg (qa/datum_audit_sens_tightflange.json). The bore axis bows ~0.3 deg (CHK-TILT finding at intake). QA ICP moved only 0.061 deg / 0.151 mm, and datum-frame vs post-ICP scan->CAD p95 differ by 0.02 mm — **Re-run trigger:** full-res scan or a second part to separate warp from design intent
6. Scanned interior/inter-part surfaces: 11357 over-band scan points (5.8 % of all scan vertices) lie INSIDE the closed CAD solid (gearbox internals behind the cover, hollow latch boxes, motor end). They are counted in the gate, not masked. Gearbox/motor interiors were declared solid at intake (PART-CLASS) — **Re-run trigger:** owner decision on which hollow features must be modelled hollow, or a scan of the separated housing
7. Masks M1 (wires, scan 0.82 %), M2 (screw heads, scan 1.74 % / CAD 1.29 %) and M3 (open boundary 0.8 mm, CAD 7.09 %) are declared from intake. No gated item passes because of a mask; unmasked and masked numbers both miss the band — **Re-run trigger:** none needed for the masks; re-run with the same masks after rebuild (CHK-LIKE4LIKE)

## Claim boundary

Not a deliverable. The STEP fails geometry validity (non-manifold edges, non-watertight tessellation at the +X end), and the whole-part scan band is missed by a wide margin (scan->CAD p95 2.07 mm vs 0.30) on a decimated, inspection-only scan with no calipers. Not fit for tooling, manufacture or fit-checking of the lid or brush rollers. The main trough bores (z 66-150) agree to ~0.25-0.8 mm and may serve as a visual/reference model only.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: HALT, REVISE._
