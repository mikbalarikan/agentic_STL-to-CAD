# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: fresh verify agent that did not build the model; QA scripts from skills/stl-re-verify only; build/model.py only grepped read-only for CHK-PATCHWORK; measure/params.json values, build/build_log.txt, measure/figures and the builder's scratchpad/work were not read; every number re-derived on the raw full-res scan (input/scan.stl sha256 41448c67...).

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `OD-E01_Power-PCB_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 20648.327 mm³ | PASS |
| Validity `OD-E01_Power-PCB.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 20648.327 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.074° / origin 0.080 mm / points p95 0.064 max 0.088 mm | within (not blocking) |
| Registration (ICP) | converged | 62/200 its, 0.162° / 0.726 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 203996 · rms 0.455 · p50 0.287 · p95 0.764 · p99 0.794 · max 1.501 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 18436 · rms 0.836 · p50 0.669 · p95 1.623 · p99 2.744 · max 4.408 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 203996 · rms 0.455 · p50 0.287 · p95 0.764 · p99 0.794 · max 1.501
- scan→CAD masked: n 203996 · rms 0.455 · p50 0.287 · p95 0.764 · p99 0.794 · max 1.501
- CAD→scan unmasked: n 300000 · rms 0.940 · p50 0.691 · p95 1.982 · p99 3.131 · max 5.133
- CAD→scan masked: n 135926 · rms 0.578 · p50 0.581 · p95 0.891 · p99 1.171 · max 4.478
- CAD→scan observable only: n 18436 · rms 0.836 · p50 0.669 · p95 1.623 · p99 2.744 · max 4.408; unobservable fraction 7.82 %

Masks:

- **M1 solder side unscanned** (cad_to_scan): the board bottom (solder side) was never scanned, so CAD->scan distance there measures the invented flat bottom face against the board top/edges, not a surface deviation; fraction 24.04 %; inside n 72128 · rms 1.021 · p50 0.855 · p95 1.814 · p99 2.658 · max 4.425
- **M2 scan open boundary** (cad_to_scan): distance measured to a scan hole EDGE (55 open-boundary loops: connector cavities, under heatsink, hole bores) is not a surface deviation; fraction 31.39 %; inside n 94160 · rms 1.298 · p50 0.729 · p95 2.788 · p99 3.706 · max 5.133
- **M3 skin normal disagreement** (cad_to_scan): a CAD point whose nearest scan triangle faces > 70 deg away is an occluded/interior correspondence, not an outer-skin deviation; fraction 9.29 %; inside n 27861 · rms 1.326 · p50 0.638 · p95 2.931 · p99 3.869 · max 4.999

Zones:

- I1 board top face [functional_interface] scan_to_cad: unmasked n 1932 · rms 0.479 · p50 0.467 · p95 0.694 · p99 0.742 · max 0.890 | masked n 1932 · rms 0.479 · p50 0.467 · p95 0.694 · p99 0.742 · max 0.890
- I1 board top face [functional_interface] cad_to_scan: unmasked n 58628 · rms 0.743 · p50 0.706 · p95 0.956 · p99 1.564 · max 3.375 | masked n 48947 · rms 0.730 · p50 0.717 · p95 0.917 · p99 1.045 · max 1.727
- I1 board outline edges [functional_interface] scan_to_cad: unmasked n 3957 · rms 0.139 · p50 0.098 · p95 0.277 · p99 0.363 · max 0.448 | masked n 3957 · rms 0.139 · p50 0.098 · p95 0.277 · p99 0.363 · max 0.448
- I1 board outline edges [functional_interface] cad_to_scan: unmasked n 5991 · rms 0.436 · p50 0.280 · p95 0.847 · p99 1.044 · max 1.231 | masked n 4073 · rms 0.465 · p50 0.360 · p95 0.851 · p99 1.035 · max 1.231
- I2 mounting holes H1 H2 [functional_interface] scan_to_cad: unmasked n 314 · rms 0.086 · p50 0.053 · p95 0.160 · p99 0.275 · max 0.427 | masked n 314 · rms 0.086 · p50 0.053 · p95 0.160 · p99 0.275 · max 0.427
- I2 mounting holes H1 H2 [functional_interface] cad_to_scan: unmasked n 504 · rms 0.441 · p50 0.232 · p95 0.890 · p99 0.988 · max 1.076 | masked n 278 · rms 0.264 · p50 0.081 · p95 0.588 · p99 0.804 · max 1.033
- I3 faston tab row [functional_interface] scan_to_cad: unmasked n 12728 · rms 0.145 · p50 0.071 · p95 0.318 · p99 0.502 · max 0.795 | masked n 12728 · rms 0.145 · p50 0.071 · p95 0.318 · p99 0.502 · max 0.795
- I3 faston tab row [functional_interface] cad_to_scan: unmasked n 11461 · rms 0.222 · p50 0.079 · p95 0.588 · p99 0.790 · max 0.920 | masked n 10570 · rms 0.206 · p50 0.075 · p95 0.562 · p99 0.791 · max 0.920
- I4 heatsink top and tallest parts [functional_interface] scan_to_cad: unmasked n 28922 · rms 0.299 · p50 0.147 · p95 0.646 · p99 0.823 · max 1.501 | masked n 28922 · rms 0.299 · p50 0.147 · p95 0.646 · p99 0.823 · max 1.501
- I4 heatsink top and tallest parts [functional_interface] cad_to_scan: unmasked n 42571 · rms 0.972 · p50 0.512 · p95 2.251 · p99 2.887 · max 3.648 | masked n 15205 · rms 0.488 · p50 0.232 · p95 0.987 · p99 1.138 · max 2.564
- X solder side [interior] scan_to_cad: unmasked n 8738 · rms 0.422 · p50 0.285 · p95 0.786 · p99 0.964 · max 1.293 | masked n 8738 · rms 0.422 · p50 0.285 · p95 0.786 · p99 0.964 · max 1.293
- X solder side [interior] cad_to_scan: unmasked n 73331 · rms 1.013 · p50 0.853 · p95 1.802 · p99 2.651 · max 4.425 | masked n 253 · rms 0.077 · p50 0.057 · p95 0.127 · p99 0.221 · max 0.319
- X under heatsink clip TO-220 [interior] scan_to_cad: unmasked n 15568 · rms 0.256 · p50 0.138 · p95 0.560 · p99 0.835 · max 1.367 | masked n 15568 · rms 0.256 · p50 0.138 · p95 0.560 · p99 0.835 · max 1.367
- X under heatsink clip TO-220 [interior] cad_to_scan: unmasked n 38121 · rms 1.562 · p50 0.775 · p95 3.320 · p99 4.108 · max 5.133 | masked n 11438 · rms 0.722 · p50 0.238 · p95 1.550 · p99 2.876 · max 4.478
- X between caps [interior] scan_to_cad: unmasked n 5237 · rms 0.215 · p50 0.061 · p95 0.582 · p99 0.742 · max 0.988 | masked n 5237 · rms 0.215 · p50 0.061 · p95 0.582 · p99 0.742 · max 0.988
- X between caps [interior] cad_to_scan: unmasked n 6421 · rms 0.447 · p50 0.081 · p95 1.076 · p99 1.591 · max 2.141 | masked n 3799 · rms 0.203 · p50 0.056 · p95 0.599 · p99 0.745 · max 1.371
- Z1 board band z<0.3 [region] scan_to_cad: unmasked n 95613 · rms 0.603 · p50 0.647 · p95 0.772 · p99 0.782 · max 1.293 | masked n 95613 · rms 0.603 · p50 0.647 · p95 0.772 · p99 0.782 · max 1.293
- Z1 board band z<0.3 [region] cad_to_scan: unmasked n 143870 · rms 0.884 · p50 0.776 · p95 1.406 · p99 2.450 · max 4.425 | masked n 56537 · rms 0.698 · p50 0.702 · p95 0.909 · p99 1.043 · max 2.285
- Z2 low parts z 0.3-3 [region] scan_to_cad: unmasked n 27047 · rms 0.286 · p50 0.106 · p95 0.689 · p99 0.830 · max 1.431 | masked n 27047 · rms 0.286 · p50 0.106 · p95 0.689 · p99 0.830 · max 1.431
- Z2 low parts z 0.3-3 [region] cad_to_scan: unmasked n 35768 · rms 0.702 · p50 0.304 · p95 1.488 · p99 2.381 · max 3.574 | masked n 20334 · rms 0.469 · p50 0.143 · p95 0.855 · p99 1.113 · max 2.195
- Z3 mid parts z 3-12 [region] scan_to_cad: unmasked n 52414 · rms 0.227 · p50 0.092 · p95 0.537 · p99 0.728 · max 1.367 | masked n 52414 · rms 0.227 · p50 0.092 · p95 0.537 · p99 0.728 · max 1.367
- Z3 mid parts z 3-12 [region] cad_to_scan: unmasked n 77791 · rms 1.104 · p50 0.298 · p95 2.770 · p99 3.817 · max 5.133 | masked n 43850 · rms 0.475 · p50 0.120 · p95 0.831 · p99 1.709 · max 4.478
- Z4 high parts z>12 [region] scan_to_cad: unmasked n 28922 · rms 0.299 · p50 0.147 · p95 0.646 · p99 0.823 · max 1.501 | masked n 28922 · rms 0.299 · p50 0.147 · p95 0.646 · p99 0.823 · max 1.501
- Z4 high parts z>12 [region] cad_to_scan: unmasked n 42571 · rms 0.972 · p50 0.512 · p95 2.251 · p99 2.887 · max 3.648 | masked n 15205 · rms 0.488 · p50 0.232 · p95 0.987 · p99 1.138 · max 2.564

Over-band scan→CAD points (> 0.8 mm): 1853 (0.908 %) in 22 clusters ≥ 20 pts.

- cluster 0: n 136, centroid [10.037, -51.299, 2.047], r [49.202, 55.073], θ [278.6, 283.4], max 0.865 — ICP-bias artefact, not a geometry miss: flat top of a low box (x 7.4-11.7, y -53.9..-48.2); QA ICP lifted the CAD +0.72 mm in z, so the scanned top reads 0.83-0.87 mm below the CAD top. Same scan points in the builder datum frame: p50 0.010 / max 0.041 mm.
- cluster 1: n 131, centroid [47.961, -22.397, 20.935], r [50.887, 55.041], θ [331.1, 341.3], max 1.140 — Scanned surface INSIDE the modelled heatsink spine at z~21 (datum z~21.6, x 47.0-48.4, y -26.6..-16.3) under a spine top at 25.3. Datum frame p50 0.73 / max 0.96 (38 % > 0.8). Either a real slot in the spine above the TO-220 tab (seen obliquely from the spine ends) or a reconstruction artefact continuing the tab top; not decidable from scan or photos (photos 2-4 show a different heatsink). UNRESOLVED finding, route to measure (side view / owner photo).
- cluster 2: n 122, centroid [0.239, 0.439, -2.548], r [1.753, 2.167], θ [5.5, 354.8], max 1.293 — ICP-bias artefact: H1 bore lower rim / board-bottom edge fringe (z -2.4..-2.8 in the ICP frame). Datum frame p50 0.26 / max 0.57 (within band).
- cluster 3: n 80, centroid [27.598, -50.924, 1.526], r [55.765, 59.614], θ [296.2, 301.3], max 0.930 — ICP-bias artefact: SMD box top x 25.5-29.8, y -52.7..-48.5. Datum frame p50 0.015 / max 0.13.
- cluster 4: n 74, centroid [-0.294, -31.325, 2.371], r [30.048, 33.092], θ [265.6, 272.0], max 0.956 — ICP-bias artefact: block top x -2.3..1.1, y -33..-30. Datum frame p50 0.030 / max 0.16.
- cluster 5: n 69, centroid [47.563, -21.581, 5.067], r [50.471, 53.615], θ [332.4, 340.6], max 1.367 — Scan points inside the modelled spine notch / TO-220 box at z~5 (x 47.4-47.7, y -24.9..-16.8). Datum frame p50 0.33 / max 0.69: within band before ICP; over band only through the +0.72 mm ICP bias. Minor fit residual under the heatsink (partly occluded zone).
- cluster 6: n 53, centroid [46.328, -20.427, 18.269], r [50.388, 51.091], θ [335.7, 336.7], max 1.501 — Real geometry miss: TO-220 tab / spine screw hole (x 46.2-46.9, y -20.9..-20.0, z 17.7-19.1). The scanned hole wall (or a screw in it) sits about 0.8 mm off the CAD hole centre (the scan arc is centred near y -21.3, the CAD circle near y -20.6). Datum frame p50 0.90 / max 1.20. Fixable by re-measuring the hole position/diameter (route measure/geometry).
- cluster 7: n 50, centroid [49.645, -55.897, -2.432], r [71.302, 78.55], θ [308.3, 314.6], max 0.990 — ICP-bias artefact: board bottom edge fringe along the y -56 edge (x 44-55). Datum frame p50 0.085 / max 0.20.
- cluster 8: n 50, centroid [90.741, -0.628, -0.631], r [89.855, 91.849], θ [0.0, 359.9], max 1.057 — Real geometry miss: ring-shaped part at (90.7,-0.6) near the +X/+Y corner. The scan sees board-level surface (z~0) inside the ring walls; the CAD models the part as a solid cylinder, so these scan points lie inside the CAD. Datum frame p50 0.87 / max 1.50 (the whole-part scan->CAD max). Fixable: model the part open (tube) or its real top (route measure/geometry).
- cluster 9: n 48, centroid [47.271, -22.835, 17.087], r [51.825, 52.721], θ [333.6, 335.0], max 1.182 — Real geometry miss: other side of the same TO-220 / spine hole as cluster 6 (x 46.9-47.5, y -23.4..-22.0, z 16.3-18.2); the scanned hole wall lies outside the CAD circle. Datum frame p50 0.80 / max 1.04. Fixable with cluster 6.
- cluster 10: n 48, centroid [9.093, -2.454, 1.234], r [9.038, 10.067], θ [341.3, 350.9], max 1.431 — Real geometry miss: connector cavity next to H1 (x 8.7-9.7, y -3.0..-1.6). The scan sees the cavity floor at z~1.9-2.0 (datum), the CAD cavity floor is at board level (MODELING_PLAN §6: J3 floor taken to the board). Datum frame p50 1.08 / max 1.49, 100 % over band. Fixable: set the floor at the scanned height (route measure/geometry).
- cluster 11: n 48, centroid [7.729, 3.762, -2.472], r [5.555, 12.556], θ [17.7, 43.6], max 1.100 — ICP-bias artefact: board bottom edge fringe along the y +3.8 edge (x 4-12). Datum frame p50 0.19 / max 0.40.

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 12 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | finding | QA gate is independent: QA's own datum audit on the raw scan, QA's own ICP (T_refine never written back to intake/alignment.json), no expected value taken from params.json or the scan. Finding: the builder's record carries self-referential checks (MODELING_PLAN §8 builder self-check against the same scan; intake datum try 2 used the board-top noise floor measured on the board top itself, DECISIONS.md) -- these are consistency checks, not independent evidence. |
| CHK-LIKE4LIKE | n/a | iteration 1 of 3; no _itN_SUPERSEDED folder, nothing to compare. Within this QA: ICP run 1 (cap 60, not converged) and run 2 (cap 200, converged at 62) use identical parameters except the cap; the diagnostic ICP (max_corr 1.0 mm) and its deviation run are labelled DIAGNOSTIC and are not the gate. |
| CHK-INDEP | pass | fresh agent; see independence |
| CHK-FILLET | pass | MODELING_PLAN §5 plans no fillet/chamfer operation; build/fillets.json and export_check.json fillets are empty (0 OK / 0 REDUCED / 0 FAILED / 0 NO_EDGES / 0 SELECTOR_ERROR); nothing skipped or shrunk silently. |
| CHK-PATCHWORK | pass | QA census (step_check.json): 1212 faces, 100 % analytic area (plane 1039, cylinder 172, torus 1), no B-spline or ruled faces; median plane face ~1.08 mm2 reflects ~60 SMD boxes, not facetting. model.py grep: no loft(ruled=True); make_polygon used only for small parametric profiles (can r-z profile, faston blade, K riser trapezoid), no stack of scan slices. Note: the plan expected cone faces (can frusta); the census has none (cans built from cylinders) -- reported, not gated. |
| CHK-ENUM | finding | Every intake feature family E01-E15 exists in the CAD (checked on overlays Z=-0.8/0.1/1.9/4.2/10/18.4/21.6/24.5 and x/y planes): board + slot + H1/H2 + small holes, star heatsink with hubs/fins, TO-220 + clip, 5 cans, X2 box, Y-cap, 6 fastons, J1-J3 + K1/K2, axial parts, SMD boxes; E16/E17 declared not modelled. No hallucinated body found: CAD->scan clusters all sit on declared unscanned/invented surfaces (board bottom, heatsink fin/spine sides, lower can walls between caps, connector cavities, Y-cap back). Finding: scan->CAD clusters show wrong or missing detail on existing features -- connector cavity floor near H1 (scan floor z~1.9, CAD at board level), ring-shaped part at (90.7,-0.8) modelled solid where the scan sees the board inside it, TO-220/spine hole position (y ~0.8 mm off), a ~1 mm bump on the block at (-1.1,-32.8,4.2), material inside the heatsink hub channel at (48.5,-37.6,z 10.7-13.3), and a scanned surface inside the spine at z~21.6. |
| CHK-ACHIEVABLE | n/a | no Tier-1 dims (scan-only run), so no Tier-1 miss to attribute |
| PHOTO-PLAUSIBILITY | finding | Photos 1-4 walked. Photo 1 matches the scanned configuration (heatsink with TO-220 held by a gold spring strap, 3 large cans + small cans, grey X2 box, blue Y-cap, 6 faston tabs, 5 white connectors, SOIC, edge pads): every photographed feature family exists in the CAD. Photos 2-4 are catalogue/installed photos of a variant: their heatsink has no spring clip and a different fin layout, so they cannot confirm heatsink/clip geometry. No photo shows the solder side, the spine top slot region (z~21.6) or the ring part's interior, so those stay unresolved by photo. |

## Misses, per region

- scan_to_cad:masked: p95 0.764 max 1.501 vs 0.3/0.8
- cad_to_scan_observable: p95 1.623 max 4.408 vs 0.3/0.8
- **whole part scan->CAD (official, post-ICP)**: p95 miss is mostly the QA ICP +0.72 mm z bias (L3): board-level points and box tops shift by ~0.7 mm; in the builder datum frame the same statistic is p95 0.294 / max 1.499 and with the diagnostic ICP p95 0.289 / max 1.509, so p95 is within band before the biased ICP. The max miss (1.50) is real in every frame and comes from localized modelling errors: ring part at (90.7,-0.8) solid instead of open (1.50), connector cavity floor near H1 at board level instead of z~1.9 (1.49), TO-220/spine hole about 0.8 mm off (1.20), bump missing on the block at (-1.1,-32.8,4.2) (1.14-1.19), material in the heatsink hub channel at (48.5,-37.6) (0.96-0.98), scanned surface inside the spine at z~21.6 (0.96, unresolved). Options: REVISE (route measure -> geometry): re-measure and model the ring part, the cavity floor, the TO-220 hole, the block bump and the hub-channel content; decide the spine z~21.6 surface with a side photo or owner input. The ICP-bias share cannot be fixed by geometry (see L3).
- **whole part CAD->scan observable (gated)**: p95 1.623 / max 4.408 post-ICP (datum frame 1.878 / 4.419). The invented board bottom (24 % of CAD samples, ray-observable from below but never scanned) and the deep heatsink fin/spine faces (zone 'X under heatsink clip TO-220' CAD->scan p95 3.32 / max 5.13), lower can walls between the caps, connector cavities and the Y-cap back have no scan behind them. With all three CAD masks the number is still p95 0.891 / max 4.478, so the masks do not clear the band. Not fixable by geometry without data. Options: a solder-side scan plus oblique heatsink/cavity scans, or, after the REVISE loop, owner ACCEPT-BAND (BAND_NOT_MET) quoting the unmasked number.
- **I1 board top face (named zone, reported)**: post-ICP the zone captures only 1,932 scan points because the +0.72 mm bias moves the scanned board top out of the zone window; datum frame p95 0.173 / max 1.499 (the max is the ring-part cluster). CAD->scan 0.956 / 3.375 post-ICP is the bias plus the invented component footprints. Options: as above: fix the ring part; resolve L3.

## Declared limitations (each with its re-run trigger)

1. No Tier-1: scan-only run, no caliper reading exists (dims.json: 12 requested dims all ABSENT, not passed); the regime has no Tier-1 band. Absolute scale is not caliper-verified (CHK-SCALE flag at intake, units assumed mm). — **Re-run trigger:** caliper readings for ENV-X, ENV-Y, F01 (H1 dia), F02 (H1-H2 pitch) and F03 (board thickness) entered in input/MEASUREMENTS.md -> re-run intake CHK-SCALE and verify
2. Unscanned surfaces are invented: the whole solder side (board bottom, 24.0 % of CAD samples), deep heatsink fin/spine sides and fin roots, connector cavity floors, lower can walls between the caps, undersides of raised parts and the Y-cap back. They are graded as CAD->scan 'observable' by the ray test and drive the CAD->scan miss. — **Re-run trigger:** a scan of the solder side and oblique scans of the heatsink / connector cavities -> re-run verify on the merged full-res scan
3. QA ICP bias: with the golden parameters (sign-free 70 deg normal test, 3.0 mm correspondence radius) the invented board bottom corresponds to the scanned board top 1.6 mm away, so ICP lifts the CAD +0.72 mm in z (0.162 deg / 0.726 mm). The official post-ICP scan->CAD p95 differs from the datum-frame p95 by more than the band. The datum audit (0.074 deg / 0.080 mm origin, within the RE_SPEC reference) and a DIAGNOSTIC ICP with max_corr 1.0 mm (0.063 deg / 0.092 mm; scan->CAD p95 0.289 / max 1.509) show the datum is sound and the gap is a registration artefact of an unscanned face, not a datum error. The diagnostic run is not the gate. — **Re-run trigger:** a solder-side scan (gives the bottom face real data) or a recorded owner/skill decision on the ICP correspondence radius for thin plates with one unscanned face -> re-run tier2_icp and deviation_gate
4. Board warp (datum-frame board top -0.35..+0.1 mm) is not modelled: flat design-intent board (declared simplification, INTAKE_CARD §8). It is inside band in the datum frame (zone I1 board top scan->CAD p95 0.173). — **Re-run trigger:** owner asks for the as-scanned warped board, or an enclosure fit check needs the warp
5. ICP did not converge at the default cap 60 (step 5e-6 > tol 1e-6 at it 60); the cap was raised once to 200 (reason: plate part with a large planar datum slides slowly while the correspondence set of the unscanned bottom jitters) and converged at 62 with the same correction. Both runs are kept (registration_run1_cap60.json, registration.json). — **Re-run trigger:** any rebuild -> re-run ICP with the same cap and report both again
6. Photos are catalogue photos; photos 2-4 show a variant heatsink without the spring clip, so the heatsink, clip and spine details are confirmed by photo 1 only. — **Re-run trigger:** photos of the scanned unit (top, both heatsink sides) supplied -> re-run PHOTO-PLAUSIBILITY / CHK-ENUM

## Claim boundary

This is a component-side envelope / fit reference only, iteration 1, NOT approved. Not fit for manufacture, tooling, PCB footprint or electrical work, or any solder-side fit: the solder side, heatsink fin roots/sides, connector cavity floors and part undersides are invented, absolute scale is not caliper-verified, and the board is modelled flat. Known modelling errors (ring part, cavity floor near H1, TO-220 hole, block bump, hub-channel content) are open and routed back.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
