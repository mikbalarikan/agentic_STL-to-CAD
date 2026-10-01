# VERDICT: BAND_NOT_MET

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: fresh verifier subagent (it2) that did not build the model; QA scripts from skills/stl-re-verify/scripts plus QA-own diagnostics in qa/tools/ (it1 verifier's QA tools copied from _it1_SUPERSEDED/qa/tools/ and new QA-own scripts); build/model.py only grepped read-only (CHK-PATCHWORK); measure/*, builder self-check numbers, build/face_stats.json and builder tools NOT used as expected values; builder claims in MODELING_PLAN.md were checked against QA numbers, not trusted

Scan: `input/scan.stl` (DECIMATED, inspection only), label **INSPECTION ONLY**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `dreame_brushes_housing_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 138726.051 mm³ | PASS |
| Validity `dreame_brushes_housing.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 138726.051 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.526° / origin 0.223 mm / points p95 0.685 max 0.800 mm | outside (not blocking) |
| Registration (ICP) | converged | 48/60 its, 0.053° / 0.156 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 191655 · rms 0.573 · p50 0.114 · p95 1.161 · p99 2.640 · max 5.965 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 18788 · rms 0.591 · p50 0.093 · p95 1.004 · p99 2.936 · max 7.693 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 196686 · rms 0.703 · p50 0.116 · p95 1.284 · p99 3.026 · max 11.146
- scan→CAD masked: n 191655 · rms 0.573 · p50 0.114 · p95 1.161 · p99 2.640 · max 5.965
- CAD→scan unmasked: n 300000 · rms 0.839 · p50 0.100 · p95 1.904 · p99 4.134 · max 7.895
- CAD→scan masked: n 273270 · rms 0.753 · p50 0.093 · p95 1.550 · p99 3.761 · max 7.895
- CAD→scan observable only: n 18788 · rms 0.591 · p50 0.093 · p95 1.004 · p99 2.936 · max 7.693; unobservable fraction 6.06 %

Masks:

- **M1 loose motor wires F11** (scan_to_cad): loose, non-rigid motor wires; declared not modelled at intake; fraction 0.82 %; inside n 1616 · rms 4.405 · p50 2.232 · p95 9.077 · p99 10.163 · max 11.146
- **M2 gearbox cover screw heads** (scan_to_cad): COTS screw heads in the 4 gearbox-cover sockets; screw-head detail declared not modelled; fraction 1.74 %; inside n 3415 · rms 0.943 · p50 0.328 · p95 2.077 · p99 3.340 · max 4.107
- **M2 gearbox cover screw heads** (cad_to_scan): COTS screw heads in the 4 gearbox-cover sockets; screw-head detail declared not modelled; fraction 1.29 %; inside n 3873 · rms 0.729 · p50 0.137 · p95 1.111 · p99 3.987 · max 4.892
- **M3 open boundary** (cad_to_scan): distance from CAD to a scan hole EDGE is not a surface deviation (scan has 192 open loops); fraction 7.79 %; inside n 23356 · rms 1.544 · p50 0.491 · p95 3.638 · p99 5.606 · max 7.164

Zones:

- T1 bore wall [functional_interface] scan_to_cad: unmasked n 35294 · rms 0.292 · p50 0.087 · p95 0.689 · p99 1.044 · max 2.817 | masked n 35294 · rms 0.292 · p50 0.087 · p95 0.689 · p99 1.044 · max 2.817
- T1 bore wall [functional_interface] cad_to_scan: unmasked n 57898 · rms 0.242 · p50 0.072 · p95 0.384 · p99 1.043 · max 3.741 | masked n 56590 · rms 0.240 · p50 0.071 · p95 0.374 · p99 1.038 · max 3.741
- T2 bore wall [functional_interface] scan_to_cad: unmasked n 34751 · rms 0.314 · p50 0.091 · p95 0.636 · p99 1.530 · max 4.668 | masked n 34751 · rms 0.314 · p50 0.091 · p95 0.636 · p99 1.530 · max 4.668
- T2 bore wall [functional_interface] cad_to_scan: unmasked n 70015 · rms 1.012 · p50 0.100 · p95 2.071 · p99 5.250 · max 7.203 | masked n 64784 · rms 0.875 · p50 0.093 · p95 1.997 · p99 4.846 · max 7.203
- flange top cover mating [functional_interface] scan_to_cad: unmasked n 2805 · rms 0.219 · p50 0.128 · p95 0.226 · p99 0.996 · max 1.829 | masked n 2805 · rms 0.219 · p50 0.128 · p95 0.226 · p99 0.996 · max 1.829
- flange top cover mating [functional_interface] cad_to_scan: unmasked n 5828 · rms 0.259 · p50 0.142 · p95 0.221 · p99 0.919 · max 3.623 | masked n 5788 · rms 0.260 · p50 0.143 · p95 0.222 · p99 0.931 · max 3.623
- labyrinth edge [functional_interface] scan_to_cad: unmasked n 37645 · rms 1.099 · p50 0.121 · p95 1.902 · p99 5.721 · max 11.146 | masked n 36939 · rms 0.647 · p50 0.117 · p95 1.480 · p99 2.928 · max 4.738
- labyrinth edge [functional_interface] cad_to_scan: unmasked n 49614 · rms 0.671 · p50 0.083 · p95 1.242 · p99 3.405 · max 7.096 | masked n 45759 · rms 0.657 · p50 0.078 · p95 1.111 · p99 3.452 · max 7.096
- gearbox end face [functional_interface] scan_to_cad: unmasked n 1861 · rms 0.125 · p50 0.063 · p95 0.264 · p99 0.533 · max 0.760 | masked n 1601 · rms 0.075 · p50 0.061 · p95 0.111 · p99 0.166 · max 0.626
- gearbox end face [functional_interface] cad_to_scan: unmasked n 10647 · rms 0.431 · p50 0.067 · p95 0.574 · p99 2.525 · max 4.294 | masked n 9505 · rms 0.429 · p50 0.065 · p95 0.429 · p99 2.558 · max 4.294
- motor can region [functional_interface] scan_to_cad: unmasked n 18678 · rms 0.656 · p50 0.152 · p95 1.523 · p99 2.750 · max 4.813 | masked n 17768 · rms 0.614 · p50 0.147 · p95 1.373 · p99 2.690 · max 4.813
- motor can region [functional_interface] cad_to_scan: unmasked n 22666 · rms 1.346 · p50 0.141 · p95 3.677 · p99 5.657 · max 6.897 | masked n 17918 · rms 1.101 · p50 0.110 · p95 2.361 · p99 5.479 · max 6.660
- gearbox block interior [interior] scan_to_cad: unmasked n 8480 · rms 0.767 · p50 0.163 · p95 1.882 · p99 2.907 · max 4.107 | masked n 6903 · rms 0.647 · p50 0.147 · p95 1.658 · p99 2.502 · max 3.791
- gearbox block interior [interior] cad_to_scan: unmasked n 13616 · rms 1.369 · p50 0.197 · p95 3.153 · p99 4.692 · max 7.895 | masked n 9241 · rms 1.338 · p50 0.142 · p95 3.129 · p99 4.935 · max 7.895
- zband gearbox z-1_13 [region] scan_to_cad: unmasked n 19840 · rms 0.616 · p50 0.149 · p95 1.440 · p99 2.472 · max 4.107 | masked n 16425 · rms 0.523 · p50 0.137 · p95 1.193 · p99 2.243 · max 3.791
- zband gearbox z-1_13 [region] cad_to_scan: unmasked n 37427 · rms 1.032 · p50 0.121 · p95 2.505 · p99 4.013 · max 7.895 | masked n 29820 · rms 0.992 · p50 0.104 · p95 2.386 · p99 3.998 · max 7.895
- zband motor_troughstart z13_66 [region] scan_to_cad: unmasked n 62294 · rms 0.886 · p50 0.121 · p95 1.327 · p99 3.902 · max 11.146 | masked n 60678 · rms 0.537 · p50 0.119 · p95 1.063 · p99 2.517 · max 4.813
- zband motor_troughstart z13_66 [region] cad_to_scan: unmasked n 98662 · rms 0.822 · p50 0.107 · p95 1.938 · p99 4.059 · max 7.678 | masked n 88151 · rms 0.697 · p50 0.098 · p95 1.501 · p99 3.250 · max 7.678
- zband mid z66_150 [region] scan_to_cad: unmasked n 56584 · rms 0.395 · p50 0.088 · p95 0.597 · p99 1.298 · max 5.965 | masked n 56584 · rms 0.395 · p50 0.088 · p95 0.597 · p99 1.298 · max 5.965
- zband mid z66_150 [region] cad_to_scan: unmasked n 93603 · rms 0.216 · p50 0.078 · p95 0.269 · p99 1.060 · max 2.729 | masked n 90126 · rms 0.185 · p50 0.076 · p95 0.222 · p99 0.812 · max 2.645
- zband plusX_end z150_up [region] scan_to_cad: unmasked n 57968 · rms 0.744 · p50 0.149 · p95 1.807 · p99 3.121 · max 4.738 | masked n 57968 · rms 0.744 · p50 0.149 · p95 1.807 · p99 3.121 · max 4.738
- zband plusX_end z150_up [region] cad_to_scan: unmasked n 70308 · rms 1.196 · p50 0.131 · p95 2.906 · p99 5.490 · max 7.203 | masked n 65173 · rms 1.105 · p50 0.119 · p95 2.638 · p99 5.218 · max 7.203

Over-band scan→CAD points (> 0.8 mm): 18800 (9.558 %) in 119 clusters ≥ 20 pts.

- cluster 0: n 1441, centroid [-10.035, 56.637, 163.87], r [51.559, 64.321], θ [90.5, 110.6], max 3.804 — REAL, NOT FIXED since it1 (it1 cluster 3; over-band pts in the same bbox 1443 -> 1433): -Y latch box at z 161-167, y 50-62 (overlay Z=165). Scan surface lies INSIDE the CAD (qa/inside_outside.json): the part is a hollow box, the CAD fills it solid. p50 1.78 / max 3.80 mm
- cluster 1: n 1403, centroid [-9.177, 39.938, 195.328], r [31.777, 51.015], θ [88.5, 116.9], max 4.456 — REAL, NOT FIXED since it1 (it1 cluster 4; 1390 -> 1401, max 4.43 -> 4.46) although MODELING_PLAN lists it as fixed: T2 rounded/ramped +X end, z 186-203 (overlays Z=187, Z=195, Z=200). The scan curve runs from about (-16,31) to (1,51); the CAD keeps a block/wedge outline. Scan material outside the CAD, p50 1.66 / max 4.46
- cluster 2: n 1037, centroid [-41.201, 52.172, 45.815], r [62.582, 71.818], θ [124.1, 131.7], max 11.146 — ARTEFACT, declared not modelled: F11 loose motor wires (x -43..-39, y 47-59, z 41-60; organic loops in overlay x=-41). Inside mask M1. Unmasked whole-part max 11.15 comes from here; masked max is 5.97
- cluster 3: n 844, centroid [-20.48, 38.793, 204.919], r [33.859, 54.121], θ [104.7, 131.5], max 2.307 — REAL, NOT FIXED since it1 (it1 cluster 6; 842 -> 837) although listed as fixed: +X end wall / latch area z 203.7-205.3, x -27..-12, y 30-48 (overlay Z=204.5). Scan end-wall area the CAD lacks (drafted end-wall position/extent). Outside the CAD, max 2.31
- cluster 4: n 676, centroid [-25.586, 41.622, 64.193], r [38.355, 60.829], θ [115.3, 129.0], max 5.092 — REAL, NOT FIXED since it1 (it1 cluster 10; 498 -> 490, max 5.09) although 'motor end' is listed as fixed: scan material past the CAD motor end, z 61.8-69, x -38..-19, y 32-48 (overlay Z=64 shows scan arcs around the CAD end boss that the CAD lacks). Motor end bracket/bearing cap or wire exit; boss vs wires undecidable without photos. Outside the CAD, p50 1.83 / max 5.09
- cluster 5: n 498, centroid [-43.757, 32.552, 64.127], r [46.766, 60.474], θ [130.0, 149.1], max 5.965 — REAL (present in it1 as a smaller cluster, 417 over -> 498): same motor-end structure on the far side, x -46..-38.6, y 24-46, z 61.8-67.9 (overlay Z=64). Outside the CAD, p50 1.94 / max 5.97 = the masked whole-part max. Just below the M1 wire box (y < 46), so it is NOT masked; motor end cap rim/bracket vs wire exit undecidable without photos
- cluster 6: n 432, centroid [-3.146, 35.826, 204.183], r [3.945, 47.308], θ [91.3, 120.0], max 2.041 — REAL, partly improved (it1 bbox 818 -> 706): +X end, z 202.3-205.4, x -17.6..-0.8, y 3.6-47. Scan surface INSIDE the CAD by up to 2.04 mm: the CAD end wall/draft plane sits too far +z or is too thick on the open side (overlay Z=204.5)
- cluster 7: n 428, centroid [-21.058, 38.586, 170.217], r [39.922, 46.533], θ [114.9, 122.4], max 4.535 — REAL, unchanged (it1 427 -> 426): z 167-174.4, x -22.7..-18.8, y 34.5-41.2, outside the CAD, max 4.53. Overlay Z=170 shows a scan detail at about (-22,38) under the T2 +X end (rib/peg) that the CAD lacks
- cluster 8: n 424, centroid [-19.024, 0.426, 66.612], r [18.793, 19.319], θ [173.7, 182.7], max 1.021 — REAL, small unmodelled feature, unchanged: a 3 mm wide strip at x = -19.0, y -0.9..2.1, z 45.6-84.9 on the T1 underside. Scan surface INSIDE the CAD by 0.92-1.02 mm (overlay x=-19): a flat land or groove on the T1 outer bottom cylinder that the CAD leaves full round
- cluster 9: n 386, centroid [1.669, 56.739, 79.755], r [56.494, 57.103], θ [87.6, 89.9], max 1.121 — REAL, unchanged: labyrinth (-Y) lip at y 56.5-57.1, x 0.1-2.4, z 45.8-123.4. Scan INSIDE the CAD by 0.94-1.12 mm: the CAD lip top/edge stands ~1 mm proud of the scan along 78 mm (lip chamfer or lower lip not modelled)
- cluster 10: n 363, centroid [4.211, -19.632, 4.081], r [14.886, 24.388], θ [268.5, 298.7], max 4.107 — REAL, slightly improved (it1 bbox 479 -> 387): gearbox end, x -0.5..8.1, y -24.1..-13.1, z 0.9-8.6. Scan INSIDE the CAD, max 4.11. Partly inside the M2 screw-socket box 3 but extends past it (x to 8.1, y to -24.1): the socket counterbore/recess around the screw boss is modelled solid
- cluster 11: n 361, centroid [-2.359, 57.111, 173.108], r [54.875, 58.885], θ [91.5, 92.8], max 1.951 — REAL, unchanged (362 -> 373): labyrinth edge near the +X end, y 54.8-58.8, x -2.7..-1.5, z 168.9-185.3. Scan wall face outside the CAD, max 1.95 (labyrinth upstand set back or missing at the +X end; overlay y=58)

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 12 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | QA ICP (qa/registration.json) is QA-only and never written back; no expected value from measure/ or builder code; datum audit fits on the raw scan with QA-written regions (qa/datum_spec.json, same as it1); no Tier-1 expected values exist |
| CHK-LIKE4LIKE | pass | it1 vs it2 under the SAME protocol: regime baseline-skill plastic (identical file), masks.json/zones.json/icp_scan_masks.json/datum_spec.json copied byte-identical from _it1_SUPERSEDED/qa (same sha256 in deviation inputs), --scan-kind decimated, ICP ns 3M seed 11 / nc 300k seed 13 / 70 deg / 0.8 mm / 3.0 mm / cap 60 / tol 1e-6, gate sampling all scan verts + 300k CAD samples seed 2, k 8, n_samp 3M, observability 20k seed 5 cone 60, same open-boundary sweep, same 18 overlay panels. Only differences: the CAD itself (1873 vs 1572 faces; QA tessellation 0.005/0.05 watertight in it2, 17 open edges in it1) and a data-dependent helper count in the ray test (47 vs 50). Side by side in qa/it1_vs_it2_summary.json and per-it1-cluster in qa/it1_vs_it2_clusters.json. The improvement is geometry, not protocol: scan->CAD masked p95 1.937 -> 1.161, max 16.303 -> 5.965; observable CAD->scan p95 1.309 -> 1.004, max 7.709 -> 7.693 (unchanged) |
| CHK-INDEP | pass | fresh subagent context, own QA runs; see independence |
| CHK-FILLET | pass | build/export_check.json fillets [] in both frames, build/fillets.json empty; none planned, none FAILED/REDUCED. Moulded blends are left sharp (declared, MODELING_PLAN 0/5); qa/edge_share.json: 72 % of masked-band 0.30-0.80 mm scan points lie within 1.5 mm of a sharp CAD edge (87 % in z 66-150) vs 55 % / 49 % for points <= 0.30, so unmodelled blends carry part of the residual |
| CHK-PATCHWORK | pass | QA census (qa/step_check.json): 1873 faces = 1714 plane + 159 cylinder, analytic area share 100 %, 0 B-spline/ruled. model.py grep: no loft/ruled/spline/import_stl; make_polygon only for extruded constant sections, few-vertex prisms and cutting half-spaces. it2 adds ShapeUpgrade_ShapeDivideArea (MaxArea 1500 mm2) + ShapeFix: 1832 -> 1873 faces, splits large analytic faces, adds no faceting. High plane count from ribs/slabs/region prisms (reported, not gated) |
| CHK-ENUM | finding | no photos, so photo cross-check impossible. Features present in the scan and still wrong/absent in the CAD: hollow -Y latch box at z 161-167 modelled solid (cluster 0), T2 rounded/ramped +X end (cluster 1), +X end wall position (clusters 3, 6), motor end structure beyond the can (clusters 4, 5), peg/rib at the T2 +X end underside (cluster 7), T1 underside flat strip (cluster 8), labyrinth lip (clusters 9, 11), gearbox socket recess (cluster 10). Builder-claim check: MODELING_PLAN 'it2 region fixes ... verifier clusters 0,1,2,4,6,7,8,10,11' - it1 clusters 0,1,2 are fixed (over-band pts in their bboxes 3247->555, 2200->345, 2058->302) and 7,8,9,11 partly, but it1 clusters 4 (T2 +X end, 1390->1401), 6 (+X end wall, 842->837) and 10 (motor end, 498->490) are numerically unchanged although listed as fixed; it1 cluster 3 (hollow latch box, 1443->1433) was not addressed. MODELING_PLAN 0 also says 15 detached pieces ~300 mm3 dropped while build_log.txt lists 10 pieces ~122 mm3 (stale plan text) |
| CHK-ACHIEVABLE | n/a | no Tier-1 (no calipers), nothing to attribute |
| PHOTO-PLAUSIBILITY | n/a | no photos supplied (input/photos empty) |

## Misses, per region

- scan_to_cad:masked: p95 1.161 max 5.965 vs 0.3/0.8
- cad_to_scan_observable: p95 1.004 max 7.693 vs 0.3/0.8
- **whole part (gated)**: scan->CAD masked p95 1.161 / max 5.965 and observable CAD->scan p95 1.004 / max 7.693 vs 0.30 / 0.80. 22.8 % of masked scan points are > 0.30 mm (band allows 5 %). Report-only headroom (qa/headroom.json): even if every point in the 12 listed scan->CAD clusters were perfect, masked p95 would still be ~0.80 and 18.3 % of points > 0.30, so the residual is diffuse as well as clustered: sharp unmodelled blends (qa/edge_share.json), the ~0.1-0.3 deg bore warp (L5), scanned inter-part/interior surfaces (L6) Options: it3 (last loop): fix the named, fixable clusters below; consider modelling the main moulded blends; the 0.30 p95 band is unlikely to be reached on this assembly scan even then, so before spending loop 3 the owner may prefer to decide now between (a) one more geometry loop, (b) BAND_NOT_MET with a recorded ACCEPT-BAND, or (c) a full-res scan / separated-housing scan / calipers -- Owner chose (b) on 2026-10-01: no loop 3; BAND_NOT_MET pending a recorded ACCEPT-BAND.
- **+X end z > 150**: scan->CAD p95 1.807 / max 4.738 (it1 1.883 / 4.723), CAD->scan p95 2.906 / max 7.203 (it1 2.863 / 7.321): essentially unchanged. Hollow -Y latch box modelled solid (cluster 0), T2 rounded +X end shape (cluster 1), end-wall position (clusters 3, 6), rib/peg at z 170 (cluster 7), labyrinth upstand at the +X end (cluster 11); CAD->scan clusters 1-3 and 6 (~8,400 pts, max 7.2) are the CAD side of the same T2 end/latch mismatch. Three of these were listed as fixed in MODELING_PLAN but did not move Options: remeasure the T2 +X end from Z sections 185-203 and model it as the scanned curve; model the -Y latch box hollow; re-place the +X end wall/draft planes against the scan at z 202-205; add the z 170 peg/rib
- **motor end z 60-69**: clusters 4 and 5 (1,174 pts, max 5.97 = masked whole-part max): scan structure beyond the modelled can end; motor-can region zone scan->CAD p95 1.523 / CAD->scan p95 3.677 (CAD->scan cluster 0 is partly coverage, L9) Options: model the motor end bracket/cap from Z=62-68 sections, or with photos decide it is a wire exit and declare/mask it BEFORE the next gate (never after)
- **gearbox end z < 13**: scan->CAD p95 1.440 / max 4.107 (it1 1.779 / 4.123); CAD->scan p95 2.505 / max 7.895 unchanged. Socket recesses around the screw bosses modelled solid (cluster 10), CAD->scan clusters 4, 5, 7, 9-11 (edge pockets on the +x side of the block, max 7.9) unchanged since it1 Options: cut the socket counterbores/recesses; re-place the block's +x edge pockets against the scan; owner decides whether inter-part surfaces behind the cover are modelled
- **trough start + motor z 13-66**: largely fixed: scan->CAD masked p95 3.476 -> 1.063, max 16.303 -> 4.813 (it1 clusters 0, 1, 2 cleared). Remaining: T1 underside strip (cluster 8, ~1 mm) and motor-end structure Options: add the T1 underside flat strip; see motor end
- **mid troughs z 66-150**: closest to band: scan->CAD p95 0.597 / max 5.965 (max is cluster 5 at the zone edge), CAD->scan p95 0.269 / max 2.729. T1 bore wall zone p95 0.689 / 0.384 (two-way); labyrinth lip ~1 mm proud (cluster 9); 11.4 % of masked points > 0.30 here, 87 % of the 0.30-0.80 points near sharp CAD edges Options: model the labyrinth lip and main blends; the remaining warp can only be arbitrated with a full-res scan or calipers

## Declared limitations (each with its re-run trigger)

1. Decimated scan only (owner's ~20 MB export, 391,997 faces): every deviation number is INSPECTION ONLY, not an official grade — **Re-run trigger:** full-res scan available
2. Tier-1 not run: no calipers, scan-only (DECISIONS MEASUREMENTS). No dimension is caliper-verified — **Re-run trigger:** any caliper reading on the T1/T2 bore radius, flange height or gearbox end face -> re-run Tier-1
3. Absolute scale not caliper-verified (CHK-SCALE flag at intake; units assumed mm) — **Re-run trigger:** one caliper reading of overall length (~206 mm) or a bore diameter
4. No photos: CHK-ENUM/photo plausibility impossible; motor-end clusters 4/5 cannot be classed as part feature vs wire exit/assembly item — **Re-run trigger:** photos of the motor end, the -Y latch box and the +X end
5. Datum audit outside the report-only reference: 0.526 deg (axis 0.084 deg, rest is clock) / 0.223 mm origin, point p95 0.685 mm; tighter flange region 0.486 deg (qa/datum_audit_sens_tightflange.json). Bore axis bows ~0.3 deg (intake CHK-TILT finding). QA ICP moved 0.053 deg / 0.156 mm; datum-frame vs post-ICP scan->CAD masked p95 1.161 vs 1.161 — **Re-run trigger:** full-res scan or a second part to separate warp from design intent
6. Scan points INSIDE the closed CAD solid are counted, not masked: 9,114 over-band scan points (4.63 % of all scan vertices; it1 11,357 / 5.77 %) lie inside the CAD (hollow latch boxes, end wall, gearbox socket recesses, lip, T1 strip, inter-part surfaces). Gearbox/motor interiors were declared solid at intake (PART-CLASS) — **Re-run trigger:** owner decision on which hollow features must be modelled hollow, or a scan of the separated housing
7. Masks M1 (wires, scan 0.82 %), M2 (screw heads, scan 1.74 % / CAD 1.29 %) and M3 (open boundary 0.8 mm, CAD 7.79 %) are the it1 masks, unchanged. No gated item passes because of a mask; masked and unmasked both miss the band (unmasked scan->CAD p95 1.284 / max 11.146) — **Re-run trigger:** none for the masks; re-run with the same masks after rebuild (CHK-LIKE4LIKE)
8. Validity holds at the gated fine tessellation (0.005 mm / 0.05 rad, both frames, BRepCheck valid after meshing, 0 non-manifold edges, no BOP self-intersection) and at 0.01/0.1, but coarser meshes are NOT watertight (0.05/0.2 and 0.1/0.5 in both frames; 2 faces get null triangulation at 0.1/0.5, qa/tools/tess_sweep.txt). Downstream tools meshing coarsely may see holes — **Re-run trigger:** a downstream consumer (slicer/CAM/FEA) reports a non-closed mesh -> re-check at its tessellation
9. Observability: 6.06 % of the CAD subsample is unobservable from the scan (it1 4.51 %); CAD->scan observable p95 1.004 is graded, raw CAD->scan p95 1.904 is reported only. CAD->scan cluster 0 (8,661 pts around the motor/T2 crevice, z 12-68) is 40 % within 1 mm of a scan open boundary (qa/tools/c2s_cluster_coverage.json): partly a scan coverage gap — **Re-run trigger:** full-res scan with coverage of the motor/T2 crevice

## Claim boundary

VERDICT NOTE: Verdict word set to BAND_NOT_MET after the owner's decision not to spend loop 3 (DECISIONS.md, OTHER 2026-10-01: 'BAND_NOT_MET kabul, teslim et', citing the prior it2 gate 15818f79d016 whose proposed verdict was REVISE). This is a reason for the verdict choice inside the unchanged allowed set {BAND_NOT_MET, REVISE, HALT}, NOT a regrade: same it2 evidence, same numbers, no geometry change, bands not loosened, no mask added. Delivery still needs a recorded ACCEPT-BAND entry citing THIS gate.json by hash and naming a band_fails item (run-contract 10). Not a deliverable without that ACCEPT-BAND. The it2 STEP is now a valid single closed solid (BRepCheck valid after fine meshing, 0 non-manifold edges, watertight 0.005/0.05 tessellation in both frames, no self-intersection), but the whole-part scan band is still missed by ~4x on p95 (scan->CAD masked 1.161 vs 0.30) on a decimated, inspection-only scan with no calipers or photos. Not fit for tooling, manufacture, or fit-checking of the lid, brush rollers or motor. The trough bores (z 66-150) agree to ~0.27-0.6 mm p95 and may serve as a visual/reference model only.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
