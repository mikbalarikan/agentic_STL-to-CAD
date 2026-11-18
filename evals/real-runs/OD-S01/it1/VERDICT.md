# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: Fresh QA agent that did not build the model; every gate number re-derived with the stl-re-verify scripts on the full-resolution input/scan.stl (own ICP, own tessellation of the frozen STEP). Not read: build/selfcheck/, build/build_log.txt, measure/params.json values, model.py (grep for loft/ruled/Polyline only). Read as allowed: build/MODELING_PLAN.md, which quotes the builder's own datum-frame self-check aggregates (change log §8); those were not used as expectations. Datum spec, zones and masks were written by QA from INTAKE_CARD.md / alignment.json / coverage.json, masks and zones declared before the first deviation run. Extra QA-only probes (qa/probe/*.py) localise clusters; they are not gates.

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `OD-S01_steam-valve_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 15599.094 mm³ | PASS |
| Validity `OD-S01_steam-valve.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 15599.094 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.256° / origin 0.166 mm / points p95 0.188 max 0.231 mm | outside (not blocking) |
| Registration (ICP) | converged | 38/60 its, 0.094° / 0.068 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 250308 · rms 0.237 · p50 0.079 · p95 0.520 · p99 0.923 · max 2.270 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 19391 · rms 0.367 · p50 0.078 · p95 0.800 · p99 1.596 · max 3.129 | FAIL |
| zone:Z1_spindle:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 16789 · rms 0.158 · p50 0.095 · p95 0.270 · p99 0.462 · max 1.327 | FAIL |
| zone:Z2_cap_cam_ring:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 46804 · rms 0.267 · p50 0.092 · p95 0.618 · p99 0.971 · max 1.626 | FAIL |
| zone:Z3_top_clip_port:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 17605 · rms 0.209 · p50 0.112 · p95 0.433 · p99 0.583 · max 0.890 | FAIL |
| zone:Z4_side_ports:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 42338 · rms 0.140 · p50 0.065 · p95 0.280 · p99 0.558 · max 0.962 | FAIL |
| zone:Z5_barb:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 7250 · rms 0.086 · p50 0.045 · p95 0.150 · p99 0.293 · max 0.742 | PASS |
| zone:Z6_microswitch:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 25271 · rms 0.265 · p50 0.103 · p95 0.516 · p99 0.956 · max 1.747 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 250308 · rms 0.237 · p50 0.079 · p95 0.520 · p99 0.923 · max 2.270
- scan→CAD masked: n 250308 · rms 0.237 · p50 0.079 · p95 0.520 · p99 0.923 · max 2.270
- CAD→scan unmasked: n 300000 · rms 0.432 · p50 0.083 · p95 1.037 · p99 1.809 · max 3.499
- CAD→scan masked: n 279859 · rms 0.380 · p50 0.076 · p95 0.884 · p99 1.585 · max 3.348
- CAD→scan observable only: n 19391 · rms 0.367 · p50 0.078 · p95 0.800 · p99 1.596 · max 3.129; unobservable fraction 3.04 %

Masks:

- **M1 open boundary** (cad_to_scan): a CAD point whose nearest scan point lies within 0.8 mm of a scan hole edge measures the distance to the edge of a coverage gap (22 open loops: port-web orifices, bore interiors, column windows, cap slots), not a surface deviation; fraction 6.71 %; inside n 20141 · rms 0.883 · p50 0.476 · p95 1.898 · p99 2.728 · max 3.499

Zones:

- Z1_spindle [whole] scan_to_cad: unmasked n 16789 · rms 0.158 · p50 0.095 · p95 0.270 · p99 0.462 · max 1.327 | masked n 16789 · rms 0.158 · p50 0.095 · p95 0.270 · p99 0.462 · max 1.327
- Z2_cap_cam_ring [whole] scan_to_cad: unmasked n 46804 · rms 0.267 · p50 0.092 · p95 0.618 · p99 0.971 · max 1.626 | masked n 46804 · rms 0.267 · p50 0.092 · p95 0.618 · p99 0.971 · max 1.626
- Z3_top_clip_port [whole] scan_to_cad: unmasked n 17605 · rms 0.209 · p50 0.112 · p95 0.433 · p99 0.583 · max 0.890 | masked n 17605 · rms 0.209 · p50 0.112 · p95 0.433 · p99 0.583 · max 0.890
- Z4_side_ports [whole] scan_to_cad: unmasked n 42338 · rms 0.140 · p50 0.065 · p95 0.280 · p99 0.558 · max 0.962 | masked n 42338 · rms 0.140 · p50 0.065 · p95 0.280 · p99 0.558 · max 0.962
- Z5_barb [whole] scan_to_cad: unmasked n 7250 · rms 0.086 · p50 0.045 · p95 0.150 · p99 0.293 · max 0.742 | masked n 7250 · rms 0.086 · p50 0.045 · p95 0.150 · p99 0.293 · max 0.742
- Z6_microswitch [whole] scan_to_cad: unmasked n 25271 · rms 0.265 · p50 0.103 · p95 0.516 · p99 0.956 · max 1.747 | masked n 25271 · rms 0.265 · p50 0.103 · p95 0.516 · p99 0.956 · max 1.747
- Z1_spindle_c2s [region] cad_to_scan: unmasked n 12455 · rms 0.142 · p50 0.080 · p95 0.288 · p99 0.493 · max 0.797 | masked n 12276 · rms 0.139 · p50 0.080 · p95 0.281 · p99 0.469 · max 0.765
- Z2_cap_cam_ring_c2s [region] cad_to_scan: unmasked n 58130 · rms 0.282 · p50 0.086 · p95 0.645 · p99 1.056 · max 2.003 | masked n 52672 · rms 0.229 · p50 0.077 · p95 0.547 · p99 0.846 · max 1.577
- Z3_top_clip_port_c2s [region] cad_to_scan: unmasked n 19655 · rms 0.493 · p50 0.178 · p95 1.058 · p99 2.067 · max 2.941 | masked n 17337 · rms 0.333 · p50 0.153 · p95 0.667 · p99 1.166 · max 2.466
- Z4_side_ports_c2s [region] cad_to_scan: unmasked n 58390 · rms 0.218 · p50 0.065 · p95 0.434 · p99 0.962 · max 1.764 | masked n 55464 · rms 0.170 · p50 0.061 · p95 0.321 · p99 0.742 · max 1.711
- Z5_barb_c2s [region] cad_to_scan: unmasked n 11339 · rms 0.653 · p50 0.066 · p95 1.306 · p99 1.349 · max 1.634 | masked n 10717 · rms 0.648 · p50 0.062 · p95 1.306 · p99 1.348 · max 1.634
- Z6_microswitch_c2s [region] cad_to_scan: unmasked n 18177 · rms 0.190 · p50 0.065 · p95 0.415 · p99 0.747 · max 1.183 | masked n 18110 · rms 0.190 · p50 0.066 · p95 0.416 · p99 0.747 · max 1.183
- I1_top_bore_interior [interior] scan_to_cad: unmasked n 2723 · rms 0.431 · p50 0.258 · p95 0.934 · p99 1.220 · max 1.383 | masked n 2723 · rms 0.431 · p50 0.258 · p95 0.934 · p99 1.220 · max 1.383
- I1_top_bore_interior [interior] cad_to_scan: unmasked n 2368 · rms 1.150 · p50 0.738 · p95 2.305 · p99 2.700 · max 2.941 | masked n 1173 · rms 0.721 · p50 0.433 · p95 1.579 · p99 2.061 · max 2.466
- I2_column_windows_below_switch [interior] scan_to_cad: unmasked n 799 · rms 0.303 · p50 0.120 · p95 0.722 · p99 0.899 · max 1.069 | masked n 799 · rms 0.303 · p50 0.120 · p95 0.722 · p99 0.899 · max 1.069
- I2_column_windows_below_switch [interior] cad_to_scan: unmasked n 1790 · rms 0.564 · p50 0.190 · p95 1.305 · p99 1.480 · max 1.616 | masked n 814 · rms 0.339 · p50 0.155 · p95 0.670 · p99 1.138 · max 1.295
- B1_z_below_0 [region] scan_to_cad: unmasked n 16789 · rms 0.158 · p50 0.095 · p95 0.270 · p99 0.462 · max 1.327 | masked n 16789 · rms 0.158 · p50 0.095 · p95 0.270 · p99 0.462 · max 1.327
- B1_z_below_0 [region] cad_to_scan: unmasked n 12455 · rms 0.142 · p50 0.080 · p95 0.288 · p99 0.493 · max 0.797 | masked n 12276 · rms 0.139 · p50 0.080 · p95 0.281 · p99 0.469 · max 0.765
- B2_z_0_8p2 [region] scan_to_cad: unmasked n 46804 · rms 0.267 · p50 0.092 · p95 0.618 · p99 0.971 · max 1.626 | masked n 46804 · rms 0.267 · p50 0.092 · p95 0.618 · p99 0.971 · max 1.626
- B2_z_0_8p2 [region] cad_to_scan: unmasked n 58130 · rms 0.282 · p50 0.086 · p95 0.645 · p99 1.056 · max 2.003 | masked n 52672 · rms 0.229 · p50 0.077 · p95 0.547 · p99 0.846 · max 1.577
- B3_z_8p2_15p4 [region] scan_to_cad: unmasked n 31098 · rms 0.325 · p50 0.090 · p95 0.716 · p99 1.332 · max 2.270 | masked n 31098 · rms 0.325 · p50 0.090 · p95 0.716 · p99 1.332 · max 2.270
- B3_z_8p2_15p4 [region] cad_to_scan: unmasked n 36289 · rms 0.519 · p50 0.107 · p95 1.225 · p99 2.339 · max 3.477 | masked n 32790 · rms 0.454 · p50 0.094 · p95 0.980 · p99 2.127 · max 3.337
- B4_z_15p4_27p7 [region] scan_to_cad: unmasked n 84059 · rms 0.214 · p50 0.080 · p95 0.466 · p99 0.831 · max 1.488 | masked n 84059 · rms 0.214 · p50 0.080 · p95 0.466 · p99 0.831 · max 1.488
- B4_z_15p4_27p7 [region] cad_to_scan: unmasked n 105603 · rms 0.464 · p50 0.083 · p95 1.155 · p99 2.112 · max 3.499 | masked n 100495 · rms 0.407 · p50 0.077 · p95 0.990 · p99 1.863 · max 3.348
- B5_z_27p7_43p4 [region] scan_to_cad: unmasked n 53953 · rms 0.214 · p50 0.057 · p95 0.453 · p99 0.946 · max 1.724 | masked n 53953 · rms 0.214 · p50 0.057 · p95 0.453 · p99 0.946 · max 1.724
- B5_z_27p7_43p4 [region] cad_to_scan: unmasked n 67868 · rms 0.450 · p50 0.064 · p95 1.267 · p99 1.590 · max 2.769 | masked n 64289 · rms 0.432 · p50 0.060 · p95 1.262 · p99 1.591 · max 2.769
- B6_z_above_43p4 [region] scan_to_cad: unmasked n 17605 · rms 0.209 · p50 0.112 · p95 0.433 · p99 0.583 · max 0.890 | masked n 17605 · rms 0.209 · p50 0.112 · p95 0.433 · p99 0.583 · max 0.890
- B6_z_above_43p4 [region] cad_to_scan: unmasked n 19655 · rms 0.493 · p50 0.178 · p95 1.058 · p99 2.067 · max 2.941 | masked n 17337 · rms 0.333 · p50 0.153 · p95 0.667 · p99 1.166 · max 2.466

Over-band scan→CAD points (> 0.8 mm): 4437 (1.773 %) in 31 clusters ≥ 20 pts.

- cluster 0: n 726, centroid [-0.181, 8.548, 30.834], r [4.999, 13.27], θ [90.3, 104.5], max 1.699 — REAL GEOMETRY ERROR (fixable). Upper side port: the scan has a +X-facing end wall at x -1.5..-0.05 (y 5..13.3, z 24..36.4, 726 pts, all OUTSIDE the CAD, mean scan normal +X) - the port body/clip-plate block ends visibly at x ~ -0.1 outside the neck, with its U-window. The CAD port block stops ~0.9 mm short in -X (MODELING_PLAN §6 assumed the port 'runs into the column to x -1 ... invisible'; the scan shows it is visible). Evidence: overlays x=-0.1 / x=-0.6 / Z=30.8; qa/probe/cluster_probe.json rank 0.
- cluster 1: n 657, centroid [-7.028, 6.328, 9.472], r [8.564, 12.757], θ [113.7, 149.3], max 2.270 — DECLARED SIMPLIFICATION, over band. Shoulder block on post 120 (x -10.5..-3.7, y 5..11.7, z 4..13.6, 657 pts, all INSIDE the CAD = CAD excess up to 2.27 mm, scan normal up/outward): the scan block has a sloped top, the CAD models it as 2 flat steps (MODELING_PLAN §4 E04 'sloped top simplified to 2 steps'). Fixable with one planar cut. Overlays x=-7, radial 121/135.
- cluster 2: n 350, centroid [-0.091, -10.45, 18.085], r [9.404, 13.199], θ [268.9, 270.0], max 1.064 — REAL GEOMETRY ERROR (fixable). Lower side port, same defect as cluster 0 on the -Y side: +X-facing end wall at x -0.2..0 (y -13.2..-9.4, z 13..24, 350 pts OUTSIDE the CAD); CAD port block/U-window ends ~0.9 mm short in -X. Overlay x=-0.6 (left half), radial 270.
- cluster 3: n 321, centroid [-0.067, -6.922, 36.48], r [4.924, 8.676], θ [266.9, 273.0], max 1.724 — DECLARED SIMPLIFICATION, over band. Hose barb top rib (x -0.3..0.3, y -8.7..-4.9, z 34.3..37.6, 321 pts OUTSIDE the CAD): a thin rib on top of the barb collar, 'collar top rib not modelled (declared)'. Overlays y=-6.2 and Z=36.5 show the rib clearly; simple extrusion.
- cluster 4: n 293, centroid [12.537, 2.918, 14.613], r [10.961, 14.38], θ [8.7, 18.7], max 1.418 — MISSING FEATURE, not enumerated (CHK-ENUM finding). Down-facing bump under the microswitch box at x 10.6..13.9, y 1.9..3.9, z 14.3..14.9 (293 pts OUTSIDE the CAD, scan normal -Z): overlays x=12.5 and Z=14.6 show a rounded boss below the switch that the CAD lacks (plausibly the switch actuator/boss; not visible in the catalogue photos).
- cluster 5: n 274, centroid [11.001, -6.285, 11.553], r [11.099, 13.425], θ [325.3, 335.3], max 1.957 — REAL GEOMETRY ERROR (fixable). Microswitch side tab: scan tab spans x ~6.8..12.3 at y -6.7..-5.6, z 10.8..12.2 (274 pts OUTSIDE the CAD, up to 1.96 mm); the CAD tab is only ~x 7.5..9 long. Overlays y=-6.2 and Z=11.5, radial 330.
- cluster 6: n 197, centroid [-1.084, 9.886, 6.592], r [9.477, 10.852], θ [93.2, 99.4], max 1.539 — GEOMETRY ERROR in the cam ring (fixable). +X-facing step wall at x -1.6..-0.6, theta 93..99, r 9.5..10.9, z 5.9..7.4 (197 pts INSIDE the CAD = CAD excess): the scan has a notch/step at x ~ -1 in the ring (part of the x~0 wall family also seen in clusters 0/2/7/14) that the CAD fills. Overlays radial 96, Z=6.5.
- cluster 7: n 141, centroid [-0.412, -10.309, 6.399], r [9.59, 11.161], θ [266.0, 269.0], max 1.216 — GEOMETRY ERROR in the cam ring (fixable), mirror of cluster 6 at theta 266..269 (x -0.7..-0.2, r 9.6..11.2, z 4.7..7.5, 141 pts INSIDE the CAD): radial 270 overlay shows a scan pocket (r 9..13, z 2..8) that the CAD leaves solid.
- cluster 8: n 138, centroid [7.463, -6.391, 22.816], r [9.4, 10.303], θ [313.1, 325.9], max 1.488 — MISSING FEATURE, not enumerated (CHK-ENUM finding). Small lug on the column at theta 313..326, r 9.4..10.3, z 22.2..23.2 (138 pts OUTSIDE the CAD, up to 1.49 mm); visible as a stub on overlay y=-6.2 at x 7..9, z ~23. Possibly the upper end of the rib at 320 deg; not in the CAD.
- cluster 9: n 123, centroid [-1.933, -2.373, 42.838], r [2.871, 3.58], θ [186.1, 278.6], max 1.421 — PARTLY OCCLUDED INTERIOR, CAD too shallow (fixable). Top-port bore floor: upward-facing scan surface at r 2.9..3.6, z 42.5..43.1 (123 pts INSIDE the CAD); the CAD bore floor sits ~1 mm higher (c2s cluster 3 at z ~43.9 has no scan behind it). Inside the coverage loop r 2.9..4.9, z 42.6..46.7 (INTAKE_CARD §3); 'internal ribs averaged' declared. Overlay Z=42.8.
- cluster 10: n 123, centroid [-1.303, 11.954, 23.162], r [9.453, 13.507], θ [94.8, 97.8], max 1.201 — REAL GEOMETRY ERROR (fixable), same family as cluster 0: -X-facing scan face at x ~ -1.3 (y 9.4..13.5, z 22.6..23.7, 123 pts OUTSIDE the CAD) at the lower edge of the upper port plate / U-window next to the column; the CAD U-window/junction flat is offset in X. Overlay x=-1.3.
- cluster 11: n 121, centroid [1.119, 8.95, 21.383], r [8.187, 10.764], θ [74.5, 87.1], max 1.360 — CAD EXCESS at the switch-holder / +Y bracket junction (fixable): scan face at x 0.4..2.5, y 8.2..10.8, z 18.4..22.5 lies INSIDE the CAD (121 pts); same place as the invented CAD wedge (c2s cluster 4, up to 3.5 mm) where the scan shows an opening (coverage loop theta 69..91). Overlays Z=18, Z=23, radial 80.

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 12 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | grading gate = QA's own ICP on the raw full-res scan against the frozen STEP; T_refine is QA-only, not written back to intake/alignment.json; no expected value taken from params.json. The builder's datum-frame self-checks and param_table validation (MODELING_PLAN §8) are consistency checks, not independent evidence, and were not used. |
| CHK-LIKE4LIKE | n/a | first QA run of iteration 1; no superseded QA gate to compare. Builder self-check trajectory v0..final (MODELING_PLAN §8) uses a different protocol (datum frame, no ICP) and is not compared with this gate. The QA datum-frame and post-ICP runs use the identical protocol (same regime, masks, zones, sampling, seeds). |
| CHK-INDEP | pass | fresh agent, own scripts; see independence |
| CHK-FILLET | pass | build/export_check.json + fillets.json: 3/3 OK (col_top_fillet 1.5, spindle_tip_chamfer 0.7, top_blk_edge_r 1.7 x4 edges), target == used, 0 FAILED/REDUCED/NO_EDGES. Note: no other edge rounds are modelled; scan edges are rounded but the probe (qa/probe/edge_share.json) shows the over-0.3 mm population is mostly face placement, not edge rounding. |
| CHK-PATCHWORK | pass | QA census (qa/step_check.json): 314 faces, 100 % analytic area (plane 221, cylinder 74, cone 18, torus 1), 0 B-spline/ruled faces; 221 planes are designed features (median area ~6 mm2 per face_stats.json, reported not gated). grep of build/model.py for loft|ruled|Polyline: 0 hits. No faceted skin. |
| CHK-ENUM | finding | Not enumerated at intake and not in the CAD: (a) a bump under the microswitch box (x 10.6..13.9, y 1.9..3.9, z 14.3..15.8; s2c cluster 4, overlay x=12.5 and Z=14.6), (b) a small lug on the column at theta ~320, z ~22.7 (s2c cluster 8). Enumerated but not built / declared simplifications that stay over band: barb top rib (cluster 3), spline teeth, spindle tip hole (probe rank 17), cap dimples. CAD material with no scan: a wedge at the switch-holder/+Y-bracket junction (c2s cluster 4, theta 49..75, z 16.5..22.6, up to 3.5 mm) where the scan shows an opening (coverage.json loop r 8.5..11.7, theta 69..91, z 17.3..22.1). |
| CHK-ACHIEVABLE | n/a | no Tier-1 (no calipers, DECISIONS.md MEASUREMENTS scan-only); nothing to attribute |
| PHOTO-PLAUSIBILITY | finding | photos 1..5 (catalogue, low-res, no scale) walked: spindle, cap disc with slots, cam ring, two side ports with clip plates, barb, top clip port, microswitch with blades all present in the CAD; nothing in the CAD is absent from photos+scan except the interior connector material inside the column (declared, not visible). Photographed but not modelled (declared): spline teeth (photos 1,2,4), cap dimples (photos 2,4). |

## Misses, per region

- scan_to_cad:masked: p95 0.520 max 2.270 vs 0.3/0.8
- cad_to_scan_observable: p95 0.800 max 3.129 vs 0.3/0.8
- zone:Z1_spindle:scan_to_cad: p95 0.270 max 1.327 vs 0.3/0.8
- zone:Z2_cap_cam_ring:scan_to_cad: p95 0.618 max 1.626 vs 0.3/0.8
- zone:Z3_top_clip_port:scan_to_cad: p95 0.433 max 0.890 vs 0.3/0.8
- zone:Z4_side_ports:scan_to_cad: p95 0.280 max 0.962 vs 0.3/0.8
- zone:Z6_microswitch:scan_to_cad: p95 0.516 max 1.747 vs 0.3/0.8
- **whole part scan->CAD (gated)**: Band missed on p95 and max (numbers in the gate table). 12.6 % of scan points are over 0.30 mm and 1.8 % over 0.80 mm. The scan is clean (noise ~0.04 mm) and full-res, scale is not the cause, and the over-band points sit on modelled surfaces placed or sized wrong, not on scan artefacts: (1) side-port end walls / U-windows about 1 mm short in -X on both ports (clusters 0, 2, 10; c2s 0, 2); (2) shoulder-block sloped top built as steps (cluster 1); (3) cam-ring x~0 step walls/pockets at theta ~96/270 filled (clusters 6, 7); (4) microswitch side tab too short (5); (5) unenumerated bump under the switch (4) and column lug at 320 deg (8); (6) barb top rib not modelled (3); (7) top-bore floor ~1 mm too high (9); (8) invented wedge at the switch-holder/+Y bracket junction (11; c2s 4). Probe (qa/probe/over_share.json, hypothetical, not a gate): making regions R1..R8 perfect alone would leave p95 ~0.41, so a diffuse 0.3..0.8 mm placement error in the cam ring (CAD mostly in excess, z 0..8.2), the collar/switch-base band (z 8.2..15.4) and the top clip port outline (scan lug outline rounded vs CAD rectangle, overlay Z=45.5) must also be refit. Options: REVISE (iteration 1 of 3): re-measure and rebuild the named regions from the scan: extend both port blocks and U-window planes to the scanned x ~ -0.1 wall; cut the shoulder-block slope; add the barb rib, switch bump, column lug; lengthen the side tab; lower the top-bore floor; remove the holder/bracket wedge; re-place cap slot 3; refit cam-ring post/tooth/pocket faces and the top-port lug outline. If a later loop still misses p95 0.30 after these, the remainder is a BAND_NOT_MET candidate needing ACCEPT-BAND.
- **whole part CAD->scan, observable subset (gated)**: Band missed on p95 and max. Unobservable fraction is small (~3 %), so the miss is not a coverage artefact: the largest CAD->scan clusters are CAD material placed where the scan shows a different wall (port junctions, c2s 0/2), an invented wedge (c2s 4, up to 3.5 mm), a too-high top-bore floor (c2s 3) and cap slot 3 placed off the scanned loop (c2s 6). The barb bore / port bore interiors are unscanned and count here only where the ray test found line of sight. Options: same REVISE items as above; the barb/port bore interiors are a coverage fact and cannot be graded without more scan data.
- **Z2_cap_cam_ring (gated, whole band)**: p95 and max over band: shoulder block slope (cluster 1), x~0 step walls/pockets at theta ~96/270 (6, 7), CAD excess on post/tooth flanks. Options: refit cam-ring posts/teeth/pockets, cut the block slope, model the x~0 steps
- **Z6_microswitch (gated)**: side tab too short (5), missing underside bump (4); labels/blade holes declared. Options: measure and model tab length and bump
- **Z3_top_clip_port (gated)**: top-bore floor ~1 mm high (9, 13), lug outline rounded in the scan vs rectangular CAD (overlay Z=45.5). Options: lower bore floor; model the lug outline
- **Z1_spindle (gated)**: p95 passes, max over band at the unmodelled tip hole (probe rank 17, r ~0.9) and spline teeth (median cylinder, CHK-COUNT unresolved). Options: model the tip hole; teeth need a tooth count (caliper/photo) or stay a declared miss
- **Z4_side_ports (gated)**: p95 passes, max over band at the port end walls / plate edges (clusters 0, 2, 10 edges; probe rank 15 plate lip). Options: fix port block X extent; model plate lips/hooks

## Declared limitations (each with its re-run trigger)

1. Tier-1 not run: no calipers (DECISIONS.md MEASUREMENTS, scan-only). Every intake/MEASUREMENTS.md row is ABSENT, not passed. — **Re-run trigger:** any caliper reading supplied
2. Absolute scale not caliper-verified (CHK-SCALE FLAG). QA probe: a uniform-scale fit to the well-fitting scan points reads about -0.13 % (qa/probe/signed_share.json), so scale does not explain the miss. — **Re-run trigger:** one caliper reading of any overall dimension
3. Datum audit is outside the RE_SPEC reference band (report-only, never blocking): see gate.json#datum_audit. The origin offset is the column-axis position projected along two primary normals that differ by about a quarter degree over the ~40 mm lever to the column stations; QA ICP correction is small (gate.json#registration), so this is not the cause of the band miss. — **Re-run trigger:** a rebuilt datum (route datum) or a new intake alignment
4. Overlays (qa/overlays/*.png) are drawn in the builder's alignment frame (overlay.py has no --registration option); the gate itself is post-ICP. The ICP correction is below the drawn line width at these scales. — **Re-run trigger:** overlay.py gains a --registration option
5. deviation_gate.py lists only the top 12 scan->CAD clusters in gate.json while 31 clusters of >=20 pts exist; the other 19 (all <=91 pts) are characterised in qa/probe/cluster_probe.json (ranks 12..30: spindle tip hole, top-bore floor, cap-slot edges, cam-ring x~0 walls, switch/bracket edges) and are not individually explained in gate.json. — **Re-run trigger:** re-run QA after the rebuild; fix of the 12-cluster cap in deviation_gate.py

## Claim boundary

Not an approved model. This QA result grades iteration 1 against the owner's baseline-skill plastic band on the scan only; it is not evidence of any dimension (no calipers, scale unverified), says nothing about the unscanned interior (bores, spool, passages are not modelled and not graded), and is not fit for tooling, manufacture or mating-part design. Zone Z5 (barb) passing is a local result and does not excuse the whole part.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._

## QA process notes (hand-written, no numbers; every figure is in gate.json or qa/probe/)

- Environment: no workaround was needed for any skill script. One QA-only probe (`qa/probe/signed_share.py`)
  was killed by the sandbox when it used `trimesh.contains` on a large point set; it was rewritten to take
  the sign from the nearest CAD sample's outward normal. Probes are localisation aids, never gate numbers.
- Skill/script defects met: (1) `deviation_gate.py` keeps only the top 12 over-band clusters in
  `over_band_clusters.clusters`, so `verdict.py`'s CHK-CLUSTER cannot see the remaining clusters of at
  least 20 points (listed in `qa/probe/cluster_probe.json`, limitation L5). (2) `overlay.py` has no
  `--registration` option, so overlays are in the builder alignment frame, not the graded post-ICP frame (L4).
  (3) Documentation gap: a zone of kind `functional_interface` is silently ungated when the regime has no
  `interface_max_mm` (baseline-skill); intake zones with band "regime" were therefore declared kind `whole`,
  restricted to scan→CAD because `verdict.py` would otherwise gate raw zone CAD→scan, which run-contract §12
  says is reported, not gated.
- REVISE route suggestion for the orchestrator: most fixes need new scan-measured values (port block X extent,
  side-tab length, underside bump, column lug, barb rib, bore floor, block slope, slot 3 position), so
  `--route measure` fits better than `--route geometry`; the datum is not implicated.
