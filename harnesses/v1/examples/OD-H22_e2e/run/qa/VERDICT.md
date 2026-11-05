# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: Fresh sub-agent context spawned in the SAME session as the builder/orchestrator (not a separate session or agent process). QA used only stl-re-verify scripts; datum spec, zones and masks written by QA from INTAKE_CARD/alignment descriptions before any deviation was computed; refine/, params_refine.json, tree_log.json, builder metrics and params.json values were not read or used.

Scan: `input/scan.stl` (full-res), label **INVALID**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `OD-H22_3-way-valve_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 7184.734 mm³ | PASS |
| Validity `OD-H22_3-way-valve.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 7184.734 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.172° / origin 0.037 mm / points p95 0.100 max 0.112 mm | within (not blocking) |
| Registration (ICP) | converged | 300/300 its, 0.136° / 0.023 mm | INVALID |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 244617 · rms 0.225 · p50 0.077 · p95 0.417 · p99 0.943 · max 2.285 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 19845 · rms 0.440 · p50 0.082 · p95 0.777 · p99 2.261 · max 4.209 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 249510 · rms 0.230 · p50 0.078 · p95 0.435 · p99 0.970 · max 2.285
- scan→CAD masked: n 244617 · rms 0.225 · p50 0.077 · p95 0.417 · p99 0.943 · max 2.285
- CAD→scan unmasked: n 300000 · rms 0.455 · p50 0.085 · p95 0.848 · p99 2.305 · max 4.431
- CAD→scan masked: n 249774 · rms 0.204 · p50 0.072 · p95 0.399 · p99 0.768 · max 3.050
- CAD→scan observable only: n 19845 · rms 0.440 · p50 0.082 · p95 0.777 · p99 2.261 · max 4.209; unobservable fraction 0.78 %

Masks:

- **M1 +X ear tip damage** (scan_to_cad): the +X ear tip of this specimen is damaged/torn (jagged outline x>20.4); CAD follows the undamaged -X ear by symmetry, so deviation there is specimen damage, not a modelling deviation; fraction 1.96 %; inside n 4893 · rms 0.425 · p50 0.252 · p95 0.930 · p99 1.174 · max 1.261
- **M1 +X ear tip damage** (cad_to_scan): the +X ear tip of this specimen is damaged/torn (jagged outline x>20.4); CAD follows the undamaged -X ear by symmetry, so deviation there is specimen damage, not a modelling deviation; fraction 0.81 %; inside n 2421 · rms 0.336 · p50 0.253 · p95 0.654 · p99 0.784 · max 0.876
- **M2 open boundary** (cad_to_scan): distance from CAD to a scan hole EDGE (unscanned tube-bore floor, port bores beyond t≈13-16, small loops) is not a surface deviation; fraction 13.62 %; inside n 40873 · rms 1.048 · p50 0.324 · p95 2.541 · p99 3.479 · max 4.431
- **M3 skin normal** (cad_to_scan): a CAD point whose closest scan triangle disagrees in normal by >70 deg is an occluded/interior correspondence, not an outer-skin deviation; fraction 4.43 %; inside n 13291 · rms 1.336 · p50 0.841 · p95 2.827 · p99 3.652 · max 4.431

Zones:

- Z1 flange plate and ear holes [functional_interface] scan_to_cad: unmasked n 48595 · rms 0.164 · p50 0.067 · p95 0.397 · p99 0.518 · max 0.762 | masked n 47321 · rms 0.160 · p50 0.065 · p95 0.390 · p99 0.512 · max 0.668
- Z1 flange plate and ear holes [functional_interface] cad_to_scan: unmasked n 60116 · rms 0.259 · p50 0.078 · p95 0.626 · p99 0.801 · max 1.568 | masked n 51918 · rms 0.231 · p50 0.067 · p95 0.585 · p99 0.761 · max 1.568
- Z1b ear holes [functional_interface] scan_to_cad: unmasked n 6645 · rms 0.109 · p50 0.063 · p95 0.226 · p99 0.287 · max 0.353 | masked n 6645 · rms 0.109 · p50 0.063 · p95 0.226 · p99 0.287 · max 0.353
- Z1b ear holes [functional_interface] cad_to_scan: unmasked n 6840 · rms 0.337 · p50 0.099 · p95 0.842 · p99 1.210 · max 1.568 | masked n 5607 · rms 0.291 · p50 0.080 · p95 0.723 · p99 1.173 · max 1.568
- Z2 drive tube and collar [functional_interface] scan_to_cad: unmasked n 47959 · rms 0.202 · p50 0.080 · p95 0.502 · p99 0.774 · max 0.873 | masked n 47959 · rms 0.202 · p50 0.080 · p95 0.502 · p99 0.774 · max 0.873
- Z2 drive tube and collar [functional_interface] cad_to_scan: unmasked n 55094 · rms 0.727 · p50 0.099 · p95 1.742 · p99 3.065 · max 4.431 | masked n 42468 · rms 0.290 · p50 0.075 · p95 0.540 · p99 1.325 · max 3.050
- Z3 ports and clip blocks [functional_interface] scan_to_cad: unmasked n 69986 · rms 0.277 · p50 0.090 · p95 0.537 · p99 1.250 · max 2.285 | masked n 69986 · rms 0.277 · p50 0.090 · p95 0.537 · p99 1.250 · max 2.285
- Z3 ports and clip blocks [functional_interface] cad_to_scan: unmasked n 90345 · rms 0.537 · p50 0.101 · p95 1.155 · p99 2.642 · max 4.053 | masked n 68594 · rms 0.197 · p50 0.080 · p95 0.378 · p99 0.654 · max 2.507
- Z4 stem junction gussets [region] scan_to_cad: unmasked n 50250 · rms 0.258 · p50 0.069 · p95 0.340 · p99 1.430 · max 2.261 | masked n 50250 · rms 0.258 · p50 0.069 · p95 0.340 · p99 1.430 · max 2.261
- Z4 stem junction gussets [region] cad_to_scan: unmasked n 50509 · rms 0.209 · p50 0.077 · p95 0.450 · p99 0.876 · max 1.760 | masked n 46191 · rms 0.144 · p50 0.073 · p95 0.299 · p99 0.511 · max 1.018
- tray rim and floor [region] scan_to_cad: unmasked n 59301 · rms 0.152 · p50 0.066 · p95 0.254 · p99 0.683 · max 1.261 | masked n 55438 · rms 0.101 · p50 0.061 · p95 0.205 · p99 0.276 · max 0.394
- tray rim and floor [region] cad_to_scan: unmasked n 60445 · rms 0.118 · p50 0.062 · p95 0.233 · p99 0.368 · max 1.049 | masked n 56397 · rms 0.104 · p50 0.060 · p95 0.211 · p99 0.298 · max 0.629
- I1 tube bore lower interior [interior] scan_to_cad: unmasked n 3762 · rms 0.139 · p50 0.077 · p95 0.256 · p99 0.441 · max 0.955 | masked n 3762 · rms 0.139 · p50 0.077 · p95 0.256 · p99 0.441 · max 0.955
- I1 tube bore lower interior [interior] cad_to_scan: unmasked n 10206 · rms 1.494 · p50 0.614 · p95 3.106 · p99 3.900 · max 4.431 | masked n 2056 · rms 0.709 · p50 0.081 · p95 2.270 · p99 2.751 · max 3.050
- band tray side z>=0 [region] scan_to_cad: unmasked n 129274 · rms 0.187 · p50 0.077 · p95 0.417 · p99 0.734 · max 1.261 | masked n 124381 · rms 0.171 · p50 0.074 · p95 0.378 · p99 0.670 · max 0.955
- band tray side z>=0 [region] cad_to_scan: unmasked n 159146 · rms 0.461 · p50 0.080 · p95 0.889 · p99 2.305 · max 4.431 | masked n 134989 · rms 0.224 · p50 0.068 · p95 0.473 · p99 0.877 · max 3.050
- band stem side z<0 [region] scan_to_cad: unmasked n 120236 · rms 0.270 · p50 0.079 · p95 0.466 · p99 1.296 · max 2.285 | masked n 120236 · rms 0.270 · p50 0.079 · p95 0.466 · p99 1.296 · max 2.285
- band stem side z<0 [region] cad_to_scan: unmasked n 140854 · rms 0.448 · p50 0.089 · p95 0.806 · p99 2.303 · max 4.053 | masked n 114785 · rms 0.177 · p50 0.077 · p95 0.352 · p99 0.568 · max 2.507

Over-band scan→CAD points (> 0.8 mm): 3976 (1.594 %) in 18 clusters ≥ 20 pts.

- cluster 0: n 819, centroid [-1.218, 13.215, -21.169], r [11.361, 14.87], θ [78.5, 106.0], max 2.285 — +Y port clip block (819 pts, z -26..-18.5): scan material inside where the CAD's clip-slot cut/block outline sits (Z=-22, Z=-25 overlays): real clip-block/slot geometry mismatch (E12), not an artefact -> REVISE
- cluster 1: n 660, centroid [-8.579, 0.129, -1.968], r [7.349, 10.249], θ [174.2, 185.0], max 2.261 — -X gusset (660 pts, x -10.3..-7.3, y≈0, z -3.7..-0.8): gusset E09 missing in CAD (Z=-2 overlay, theta 180 overlay, photos 1/4) -> missing feature
- cluster 2: n 440, centroid [8.571, 0.248, -2.056], r [7.347, 10.214], θ [0.0, 360.0], max 2.244 — +X gusset (440 pts, mirror of cluster 1): gusset E09 missing in CAD -> missing feature
- cluster 3: n 271, centroid [21.185, -3.06, 4.073], r [21.039, 21.65], θ [350.7, 354.2], max 1.261 — +X ear tip (271 pts, x≈21.2): inside mask M1; damaged/torn ear tip of this specimen (INTAKE_CARD §2), artefact
- cluster 4: n 260, centroid [-4.31, 12.042, -27.285], r [11.891, 14.715], θ [105.1, 113.2], max 1.509 — port clip-block corner/side (260 pts, -X side of +Y port, z≈-27): clip-block flats/corner mismatch (E12) -> geometry
- cluster 5: n 218, centroid [5.012, -12.484, -26.815], r [12.043, 14.695], θ [290.1, 295.5], max 1.372 — port clip-block corner/side (218 pts, +X side of -Y port): clip-block mismatch (E12) -> geometry
- cluster 6: n 176, centroid [-4.8, 15.718, -22.303], r [15.306, 17.614], θ [104.7, 109.7], max 1.287 — port clip-block side near mouth (176 pts, -X side of +Y port, z≈-22): clip-block mismatch (E12) -> geometry
- cluster 7: n 175, centroid [4.747, 11.613, -26.802], r [12.046, 13.769], θ [65.5, 70.5], max 1.347 — port clip-block corner (175 pts, +X side of +Y port, z≈-27): clip-block mismatch (E12) -> geometry
- cluster 8: n 154, centroid [20.803, 3.482, 4.288], r [20.877, 21.206], θ [8.7, 10.2], max 1.034 — +X ear tip (154 pts, x≈20.8, y≈3.5): inside mask M1; specimen damage, artefact
- cluster 9: n 136, centroid [4.941, 16.0, -22.009], r [15.326, 17.919], θ [69.4, 75.7], max 1.306 — port clip-block side (136 pts, +X side of +Y port, z≈-22): clip-block mismatch (E12) -> geometry
- cluster 10: n 135, centroid [5.153, -15.375, -22.744], r [15.06, 17.464], θ [286.3, 291.3], max 1.173 — port clip-block side (135 pts, +X side of -Y port, z≈-22.7): clip-block mismatch (E12) -> geometry
- cluster 11: n 128, centroid [5.191, 0.074, 9.987], r [5.257, 5.401], θ [0.2, 359.6], max 0.873 — drive-tube +X slot side wall (128 pts, r 5.2-5.4, z 8.6-12.9): scan slot walls lie inside the CAD's unslotted tube wall -> E06 slots missing

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 12 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | QA ICP is QA-only (not written back); grading uses the raw full-res scan; no expected value taken from params.json or this scan. Datum audit fits are QA code on raw scan. |
| CHK-LIKE4LIKE | n/a | no previous iteration qa/ (_itN_SUPERSEDED) exists in this run; no comparison made |
| CHK-INDEP | finding | independence is a fresh sub-agent context in the same session, not a separate session; builder artefacts outside the allowed list were not read |
| CHK-FILLET | finding | build/fillets.json and export_check fillets are empty (0 targets, 0 FAILED/REDUCED): nothing silently skipped, but no blends were modelled at all although the part has moulded blends (e.g. plate back-edge round E02, DECISIONS refine entry: blend candidates not modelled); C2S cluster 11 sits on the back-edge round |
| CHK-PATCHWORK | pass | census (QA step_check): 109 faces, 1 cone / 42 cylinder / 66 plane, 100% analytic area, 0 B-spline/ruled; feature_tree.json (read-only) has extrudes, revolves, cylinder cuts and one 8-segment prism cut, no ruled loft, no per-station extrusion stack, no cluster-outline node |
| CHK-ENUM | finding | against INTAKE_CARD §5: E06 drive-tube 4 slots MISSING in CAD (Z=11 overlay: CAD full ring, scan 4 slots; C2S clusters 3-6, S2C cluster 11); E09 two gussets MISSING in CAD (Z=-2 overlay, theta 0/180 overlays; S2C clusters 1,2); E12 clip-block/slot shape mismatched (S2C clusters 0,4-7,9,10; C2S 1,2); E02 back-edge round not modelled; E07 bore floor assumed (CAD disc at z≈2.8, C2S cluster 0, unscanned). Present: E01,E03,E04,E05,E08,E10,E11,E13,E14. E15 cosmetic, E16 occluded. No hallucinated feature found beyond the assumed E07 floor. |
| CHK-ACHIEVABLE | n/a | no Tier-1 (no calipers); nothing to attribute |
| PHOTO-PLAUSIBILITY | finding | photo_1,2,3 clearly show the crenellated drive tube with 4 slots and photo_1/photo_4 show the gussets under the plate; both are absent from the CAD. Ports, clip blocks with two slots, ear holes, tray rim present in CAD. |

## Misses, per region

- scan_to_cad:masked: p95 0.417 max 2.285 vs 0.3/0.8
- cad_to_scan_observable: p95 0.777 max 4.209 vs 0.3/0.8
- **Z2 drive tube and collar**: the 4 drive slots (E06) are missing from the CAD; C2S clusters 3-6 (~800-950 pts each, max ≈1.7 mm) and S2C cluster 11; zone C2S p95 1.74 / max 4.43 (incl. assumed bore floor, C2S cluster 0, max 4.43) Options: add the 4 slot cuts (bottom z≈8.8, widths per scan ~3.06 on ear axis / ~2.65 across); review the assumed bore floor height
- **Z4 stem / gussets**: the two triangular gussets (E09) under the plate in the XZ plane are missing (S2C clusters 1,2, max 2.26 mm); C2S cluster 7 (641 pts) under the plate on -Y/+X is CAD material with no scan Options: add mirrored gusset triangles from the scan; check the stem-root geometry at x 0.7-9.4, y -6.5..0
- **Z3 ports and clip blocks**: clip blocks/through-slots do not match the scan (S2C clusters 0,4-7,9,10, max 2.28 mm; C2S clusters 1,2, ~3500/2800 pts, max ≈4 mm, partly unscanned slot interiors) Options: re-measure block flats and slot positions on the scan; the slot interiors are partly unscanned (coverage.json), so a caliper reading on block across-flats / slot width would arbitrate
- **Z1 flange / ear holes**: C2S clusters 8,10 at the ear-hole mouths on the back face and 11 on the back-edge round: un-modelled hole entry blends/chamfers and the E02 round; S2C max 0.76 in Z1 Options: model the back-edge round and hole-mouth blends

## Declared limitations (each with its re-run trigger)

1. Tier-1 not run: no caliper readings (scan-only run, DECISIONS.md MEASUREMENTS); all 20 MEASUREMENTS.md rows ABSENT, not passed — **Re-run trigger:** any caliper reading
2. absolute scale not caliper-verified (units assumed mm, CHK-SCALE flag at intake) — **Re-run trigger:** any caliper reading
3. independence is a fresh sub-agent context in the same session, not a separate session (CHK-INDEP finding) — **Re-run trigger:** re-run verify in a separate session if independence must be stronger
4. QA ICP did not converge at cap 60 nor at the single raised cap 300: a deterministic limit cycle (identical step trace ~5e-6..5e-5 at its 54-59 and 294-299, above tol 1e-6) with a stable correction 0.136 deg / 0.023 mm; per the skill the post-ICP gate is INVALID. Tolerance was not changed (it is not a tuning knob). Datum-frame and post-ICP stats agree within 0.005 mm p95. — **Re-run trigger:** re-run QA ICP on the revised CAD
5. unscanned interior (tube-bore floor/web E07, port bores beyond t≈13-16, flow passages E16) is assumed in the CAD and cannot be graded — **Re-run trigger:** a scan or section of the interior
6. ≈0.5 deg tilt between flange normal and the axis features is modelled as perpendicular (declared simplification at intake); moulded blends not modelled — **Re-run trigger:** operator answer on warp vs design intent

## Blockers (no official grade)

- registration did not converge: gate invalid

## Claim boundary

Not fit for manufacture, tooling, or as a drop-in replacement: drive slots and gussets are missing, clip blocks mismatched, the post-ICP gate is INVALID (ICP not converged), and no dimension is caliper-verified. Usable only as an inspection-grade shape reference for the iteration loop.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: HALT, REVISE._
