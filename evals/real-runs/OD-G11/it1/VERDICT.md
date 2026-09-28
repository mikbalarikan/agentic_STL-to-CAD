# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: Fresh agent/context that did not build the model; QA scripts from stl-re-verify only (plus two QA-owned helpers in qa/scripts/: a memory-only wrapper around deviation_gate.py and a tessellation probe). model.py was only grepped; measure/params.json and build/selfcheck/ numbers were not used. Disclosure: build/build_log.txt (not on the allowed input list) was read once by accident while listing build/; none of its numbers were used as expectations (spout axis positions for zones come from INTAKE_CARD §5 / MEASUREMENTS request F04).

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `OD-G11_portafilter_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 137894.887 mm³ | PASS |
| Validity `OD-G11_portafilter.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 137894.887 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.003° / origin 0.063 mm / points p95 0.063 max 0.063 mm | within (not blocking) |
| Tier-1 F01 rim bore ID just above the ledge (CAD only, ungated) | ungated | CAD 54.644 | reported |
| Registration (ICP) | converged | 85/400 its, 0.176° / 0.047 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 250812 · rms 0.191 · p50 0.058 · p95 0.365 · p99 0.828 · max 2.441 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 19236 · rms 0.352 · p50 0.055 · p95 0.464 · p99 1.891 · max 4.984 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 250812 · rms 0.191 · p50 0.058 · p95 0.365 · p99 0.828 · max 2.441
- scan→CAD masked: n 250812 · rms 0.191 · p50 0.058 · p95 0.365 · p99 0.828 · max 2.441
- CAD→scan unmasked: n 300000 · rms 0.578 · p50 0.058 · p95 1.194 · p99 2.988 · max 5.727
- CAD→scan masked: n 280076 · rms 0.429 · p50 0.053 · p95 0.432 · p99 2.627 · max 5.727
- CAD→scan observable only: n 19236 · rms 0.352 · p50 0.055 · p95 0.464 · p99 1.891 · max 4.984; unobservable fraction 3.82 %

Masks:

- **M1 open boundary** (cad_to_scan): distance from a CAD point to a scan hole EDGE is not a surface deviation: the scan has 15 open-boundary loops (spout/outlet pockets inside the insert, neck-channel roof end, bore/wire gaps, a slit along the grip); fraction 6.09 %; inside n 18273 · rms 1.603 · p50 0.849 · p95 3.398 · p99 4.366 · max 5.715
- **M2 skin normal** (cad_to_scan): a CAD point whose nearest scan triangle faces >70 deg away is matched to an occluded/other surface (one fused solid of an assembly: internal faces, pocket walls in shadow, rib flanks in shadow), not an outer-skin deviation; fraction 1.08 %; inside n 3232 · rms 1.560 · p50 0.706 · p95 3.359 · p99 4.227 · max 5.359

Zones:

- RIM [functional_interface] scan_to_cad: unmasked n 6473 · rms 0.099 · p50 0.062 · p95 0.197 · p99 0.262 · max 0.299 | masked n 6473 · rms 0.099 · p50 0.062 · p95 0.197 · p99 0.262 · max 0.299
- RIM [functional_interface] cad_to_scan: unmasked n 6640 · rms 0.150 · p50 0.066 · p95 0.314 · p99 0.581 · max 1.208 | masked n 6617 · rms 0.148 · p50 0.066 · p95 0.312 · p99 0.566 · max 1.208
- LUGS [functional_interface] scan_to_cad: unmasked n 6073 · rms 0.326 · p50 0.103 · p95 0.740 · p99 1.150 · max 1.394 | masked n 6073 · rms 0.326 · p50 0.103 · p95 0.740 · p99 1.150 · max 1.394
- LUGS [functional_interface] cad_to_scan: unmasked n 6399 · rms 0.429 · p50 0.098 · p95 1.011 · p99 1.588 · max 1.995 | masked n 6297 · rms 0.414 · p50 0.096 · p95 0.974 · p99 1.576 · max 1.935
- BORE [functional_interface] scan_to_cad: unmasked n 9690 · rms 0.153 · p50 0.106 · p95 0.249 · p99 0.422 · max 1.084 | masked n 9690 · rms 0.153 · p50 0.106 · p95 0.249 · p99 0.422 · max 1.084
- BORE [functional_interface] cad_to_scan: unmasked n 10017 · rms 0.148 · p50 0.099 · p95 0.244 · p99 0.474 · max 1.252 | masked n 9664 · rms 0.131 · p50 0.097 · p95 0.237 · p99 0.274 · max 0.797
- SPOUTS [functional_interface] scan_to_cad: unmasked n 10836 · rms 0.197 · p50 0.092 · p95 0.422 · p99 0.770 · max 1.083 | masked n 10836 · rms 0.197 · p50 0.092 · p95 0.422 · p99 0.770 · max 1.083
- SPOUTS [functional_interface] cad_to_scan: unmasked n 13544 · rms 1.657 · p50 0.132 · p95 3.350 · p99 4.492 · max 5.727 | masked n 12430 · rms 1.558 · p50 0.118 · p95 3.247 · p99 4.242 · max 5.727
- INSERT_FLOOR [interior] scan_to_cad: unmasked n 42351 · rms 0.334 · p50 0.128 · p95 0.727 · p99 1.393 · max 2.441 | masked n 42351 · rms 0.334 · p50 0.128 · p95 0.727 · p99 1.393 · max 2.441
- INSERT_FLOOR [interior] cad_to_scan: unmasked n 59427 · rms 0.961 · p50 0.153 · p95 2.314 · p99 3.689 · max 5.727 | masked n 47271 · rms 0.650 · p50 0.128 · p95 1.724 · p99 2.569 · max 5.727
- WIRE [region] scan_to_cad: unmasked n 12258 · rms 0.229 · p50 0.109 · p95 0.500 · p99 0.725 · max 1.333 | masked n 12258 · rms 0.229 · p50 0.109 · p95 0.500 · p99 0.725 · max 1.333
- WIRE [region] cad_to_scan: unmasked n 8658 · rms 0.270 · p50 0.117 · p95 0.611 · p99 1.008 · max 1.526 | masked n 6755 · rms 0.193 · p50 0.099 · p95 0.377 · p99 0.758 · max 1.477
- CENTRE_SCREW [region] scan_to_cad: unmasked n 1165 · rms 0.102 · p50 0.059 · p95 0.214 · p99 0.316 · max 0.448 | masked n 1165 · rms 0.102 · p50 0.059 · p95 0.214 · p99 0.316 · max 0.448
- CENTRE_SCREW [region] cad_to_scan: unmasked n 1071 · rms 0.151 · p50 0.062 · p95 0.342 · p99 0.589 · max 0.857 | masked n 1053 · rms 0.150 · p50 0.062 · p95 0.339 · p99 0.597 · max 0.857
- CUP_OUTER [region] scan_to_cad: unmasked n 45979 · rms 0.047 · p50 0.033 · p95 0.092 · p99 0.119 · max 0.234 | masked n 45979 · rms 0.047 · p50 0.033 · p95 0.092 · p99 0.119 · max 0.234
- CUP_OUTER [region] cad_to_scan: unmasked n 47184 · rms 0.049 · p50 0.035 · p95 0.093 · p99 0.120 · max 0.222 | masked n 47184 · rms 0.049 · p50 0.035 · p95 0.093 · p99 0.120 · max 0.222
- NECK [region] scan_to_cad: unmasked n 22349 · rms 0.203 · p50 0.125 · p95 0.420 · p99 0.553 · max 0.841 | masked n 22349 · rms 0.203 · p50 0.125 · p95 0.420 · p99 0.553 · max 0.841
- NECK [region] cad_to_scan: unmasked n 22790 · rms 0.223 · p50 0.117 · p95 0.457 · p99 0.692 · max 1.392 | masked n 22348 · rms 0.213 · p50 0.116 · p95 0.444 · p99 0.619 · max 1.294
- HANDLE [region] scan_to_cad: unmasked n 58508 · rms 0.063 · p50 0.040 · p95 0.126 · p99 0.199 · max 0.405 | masked n 58508 · rms 0.063 · p50 0.040 · p95 0.126 · p99 0.199 · max 0.405
- HANDLE [region] cad_to_scan: unmasked n 87342 · rms 0.363 · p50 0.039 · p95 0.171 · p99 2.062 · max 5.212 | masked n 82990 · rms 0.093 · p50 0.036 · p95 0.112 · p99 0.183 · max 4.894
- ZB_0_10 [region] scan_to_cad: unmasked n 47330 · rms 0.228 · p50 0.075 · p95 0.544 · p99 0.897 · max 1.394 | masked n 47330 · rms 0.228 · p50 0.075 · p95 0.544 · p99 0.897 · max 1.394
- ZB_0_10 [region] cad_to_scan: unmasked n 42781 · rms 0.236 · p50 0.069 · p95 0.523 · p99 1.001 · max 1.995 | masked n 40428 · rms 0.215 · p50 0.065 · p95 0.441 · p99 0.935 · max 1.935
- ZB_10_20 [region] scan_to_cad: unmasked n 46068 · rms 0.097 · p50 0.043 · p95 0.209 · p99 0.330 · max 0.616 | masked n 46068 · rms 0.097 · p50 0.043 · p95 0.209 · p99 0.330 · max 0.616
- ZB_10_20 [region] cad_to_scan: unmasked n 50268 · rms 0.086 · p50 0.038 · p95 0.191 · p99 0.290 · max 0.482 | masked n 50141 · rms 0.086 · p50 0.038 · p95 0.190 · p99 0.289 · max 0.482
- ZB_20_30 [region] scan_to_cad: unmasked n 47369 · rms 0.141 · p50 0.060 · p95 0.254 · p99 0.556 · max 1.403 | masked n 47369 · rms 0.141 · p50 0.060 · p95 0.254 · p99 0.556 · max 1.403
- ZB_20_30 [region] cad_to_scan: unmasked n 61752 · rms 0.169 · p50 0.053 · p95 0.257 · p99 0.825 · max 1.624 | masked n 60132 · rms 0.142 · p50 0.052 · p95 0.221 · p99 0.562 · max 1.624
- ZB_30_40 [region] scan_to_cad: unmasked n 54848 · rms 0.197 · p50 0.061 · p95 0.437 · p99 0.732 · max 1.374 | masked n 54848 · rms 0.197 · p50 0.061 · p95 0.437 · p99 0.732 · max 1.374
- ZB_30_40 [region] cad_to_scan: unmasked n 75257 · rms 0.762 · p50 0.077 · p95 1.985 · p99 3.244 · max 5.212 | masked n 63506 · rms 0.457 · p50 0.060 · p95 0.706 · p99 2.230 · max 4.894
- ZB_40_50 [region] scan_to_cad: unmasked n 47242 · rms 0.243 · p50 0.054 · p95 0.309 · p99 1.360 · max 2.441 | masked n 47242 · rms 0.243 · p50 0.054 · p95 0.309 · p99 1.360 · max 2.441
- ZB_40_50 [region] cad_to_scan: unmasked n 61295 · rms 0.782 · p50 0.056 · p95 2.025 · p99 3.679 · max 5.727 | masked n 57531 · rms 0.601 · p50 0.053 · p95 0.623 · p99 3.299 · max 5.727
- ZB_50_60 [region] scan_to_cad: unmasked n 7955 · rms 0.220 · p50 0.105 · p95 0.489 · p99 0.815 · max 1.083 | masked n 7955 · rms 0.220 · p50 0.105 · p95 0.489 · p99 0.815 · max 1.083
- ZB_50_60 [region] cad_to_scan: unmasked n 8647 · rms 1.299 · p50 0.126 · p95 2.808 · p99 2.982 · max 3.287 | masked n 8338 · rms 1.302 · p50 0.122 · p95 2.813 · p99 2.983 · max 3.287

Over-band scan→CAD points (> 0.8 mm): 2713 (1.082 %) in 18 clusters ≥ 20 pts.

- cluster 0: n 645, centroid [20.712, -2.525, -41.229], r [20.754, 22.682], θ [0.0, 359.8], max 1.961 — REAL MODELLING MISS: 645 pts, ring r 20.8-22.7, z -42.3..-40.0, all round the insert floor-to-wall corner. Overlays theta=15/317/341 and x=12 show the scan floor dropping into a rounded trough (to z~-43.5) next to the insert wall where the CAD floor is flat at ~-40.5..-42 with a 2.7 mm fillet; paired with CAD->scan cluster 4 at the same ring. Fix: re-measure the floor/gutter profile near the wall.
- cluster 1: n 306, centroid [11.912, 3.361, -33.93], r [11.945, 13.193], θ [12.9, 21.9], max 1.374 — REAL MODELLING MISS: 306 pts, r 11.9-13.2, theta 13-22, z -41..-29: V-rib 1 flank. Overlays theta=15 and x=12 show the scan rib at r~12-13 while the CAD rib sits at r~13.5-15 (radial offset ~1.5 mm). Fix: re-fit the V-rib line/offset.
- cluster 2: n 277, centroid [15.605, 13.661, -42.168], r [18.829, 22.322], θ [31.7, 59.3], max 2.441 — REAL MODELLING MISS (partly unobserved): 277 pts, r 18.8-22.3, theta 32-59, z -43.3..-40.0: floor trough around outlet pocket 1 (spout 1, theta 56.3). Scan floor lower than the CAD gutter around the pocket mouth (overlay x=12, y=15).
- cluster 3: n 219, centroid [13.376, -11.673, -42.665], r [14.3, 21.703], θ [311.3, 324.6], max 2.321 — REAL MODELLING MISS (partly unobserved): 219 pts, r 14.3-21.7, theta 311-325, z -43.5..-40.9: same trough around outlet pocket 2 (theta -56.8); overlay theta=317 shows the scan floor at ~-43.3 vs CAD ~-40.5.
- cluster 4: n 162, centroid [-4.041, 25.965, -5.456], r [25.438, 26.817], θ [92.5, 110.0], max 1.353 — WIRE/BORE: 162 pts, r 25.4-26.8, theta 92-110, z -6.2..-4.9: lower side of wire arc near the 90 deg notch where the wire dives behind the bore (overlay theta=110, Z=-5.5); wire modelled as simplified torus arcs (owner PART-CLASS allows simplification) at a slightly different height/radius.
- cluster 5: n 158, centroid [5.417, 0.642, -30.44], r [5.425, 5.99], θ [0.2, 360.0], max 1.192 — REAL MODELLING MISS: 158 pts, r 5.4-6.0, all round, z -32.9..-28.1: the central post/opening of the insert (U-rib inner end / centre boss) -- scan surface at r~5.4-6.0 vs CAD cylinder at r~4.6 (paired CAD->scan cluster 9). Open-boundary loops at r 4.4-5.9 (coverage.json) show the scan is partly open here, but the scanned wall is ~1 mm outside the CAD.
- cluster 6: n 124, centroid [-2.218, 28.423, -3.425], r [28.495, 28.672], θ [86.2, 101.1], max 0.960 — WIRE/RIM: 124 pts, r 28.5-28.7, theta 86-101, z -3.6..-3.2: wire arc passing through the 90 deg rim notch region / wire end entering the bore wall; simplified wire geometry (overlay Z=-3.4).
- cluster 7: n 111, centroid [27.056, 9.471, -3.151], r [28.529, 28.904], θ [12.7, 26.3], max 1.183 — WIRE/BORE: 111 pts, r 28.5-28.9, theta 13-26, z -3.5..-2.6: wire arc end where it enters the bore wall (overlay Z=-3.4, theta=15 shows the scan wire kinked at the wall; CAD ends the torus buried in the wall).
- cluster 8: n 104, centroid [-31.255, -8.922, -3.346], r [30.421, 34.92], θ [194.8, 196.7], max 1.298 — REAL MODELLING MISS (functional LUGS): 104 pts, r 30.4-34.9, theta 195-197, z -3.9..-2.7: lug 2 end. Overlay theta=196 shows the scan lug under-face rising to z~-3 at the lug end while the CAD under-face stays at ~-4.7 (single linear ramp); paired CAD->scan cluster 6.
- cluster 9: n 103, centroid [8.088, 31.787, -3.177], r [30.531, 35.157], θ [74.4, 76.6], max 1.394 — REAL MODELLING MISS (functional LUGS): 103 pts, r 30.5-35.2, theta 74-77, z -4.0..-2.0: lug 1 end, same ramp-end mismatch (overlay theta=76); paired CAD->scan cluster 5.
- cluster 10: n 99, centroid [11.734, -3.843, -30.399], r [11.949, 13.051], θ [337.0, 345.1], max 1.403 — REAL MODELLING MISS: 99 pts, r 11.9-13.1, theta 337-345, z -33.4..-28.8: V-rib 2 flank, mirror of cluster 1 (overlay theta=341: scan rib at r~12-13.5, CAD at r~13.5-15).
- cluster 11: n 67, centroid [22.749, 17.273, -3.17], r [28.523, 28.913], θ [29.9, 42.1], max 1.189 — WIRE/BORE: 67 pts, r 28.5-28.9, theta 30-42, z -3.4..-2.8: wire arc end entering the bore wall; simplified wire (overlay Z=-3.4).

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | pass | no pass depends on a mask |
| CHK-CLUSTER | pass | 12 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | Datum audited independently on the raw full-res scan (0.0025 deg / 0.063 mm vs alignment.json). QA ICP (T_refine) is evaluation-only, never written back. No expected value taken from this scan or from params.json. The builder's self-check (build/selfcheck, working copy, no ICP) is a consistency check, not independent evidence, and was not used. |
| CHK-LIKE4LIKE | n/a | Iteration 1: no _itN_SUPERSEDED/qa to compare. The builder self-check number in MODELING_PLAN.md (scan->CAD p95 0.281) used a different protocol (300k-face working copy, no ICP) and is not comparable to QA's 0.365 on the full-res original. |
| CHK-INDEP | pass | Fresh context; see independence (build_log.txt read-by-accident disclosed; not used). |
| CHK-FILLET | finding | export_check/fillets.json: 11/11 fillets OK, target == used, none REDUCED/FAILED. But the planned arch-foot round was dropped before the first run (MODELING_PLAN §8), and overlay x=40 shows the scan's arch legs curving inward to a rounded foot (y~+-7.5, z~-38.3) where the CAD leg is straight to a sharp foot at z~-39.4: the dropped round is contradicted by the scan. |
| CHK-PATCHWORK | pass | QA census: 171 faces, analytic area 95.5 %, 11 B-spline (fillet) faces, 96 planes, 0 ruled-like; no loft(/ruled in model.py; the 3 make_polygon calls (model.py:244, 335, 391) are single closed profiles (rib section, handle revolve profile, pad wedge), not a stack of scan slices. |
| CHK-ENUM | finding | All 11 INTAKE_CARD §5 feature families exist in the CAD (cup, bore/ledge, 3 lugs, 2 rim notches, pad, arch neck + handle, 2 spouts with screw heads, centre screw, insert floor/U rib/V ribs/2 outlet pockets, 3 wire arcs); cast lettering not modelled (declared cosmetic). Nothing hallucinated except the declared invented pocket bores (z to ~-54). Finding: several features exist but are misplaced/misshaped against the scan (V-rib radial position, floor trough around the pockets, lug ramp ends, arch foot) -- see cluster explanations. |
| CHK-ACHIEVABLE | n/a | No Tier-1 reading exists (scan-only run), so no Tier-1 miss to attribute. |
| PHOTO-PLAUSIBILITY | pass | Photo 1 (top/inside): rim, 3 lugs, wire spring arcs across the bore, black insert with U rib, neck, collar ring, tapered black grip, cream end cap -- all in CAD. Photo 2 (bottom): two spout bosses with cross-recess screws, centre cross screw, lugs, arch neck, collar, grip, cap -- all in CAD. Rim notches not visible in photos (mesh-only, accepted at intake). |

## Misses, per region

- scan_to_cad:masked: p95 0.365 max 2.441 vs 0.3/0.8
- cad_to_scan_observable: p95 0.464 max 4.984 vs 0.3/0.8
- **INSERT_FLOOR (funnel floor, trough around the outlet pockets, V ribs, central post)**: Observed scan surface the CAD does not follow: floor trough near the wall and around both pockets 1-2 mm below the CAD floor; V ribs ~1.5 mm radially outboard of the scan ribs; central post r~4.6 in CAD vs ~5.5-6.0 in scan. Zone scan->CAD p95 0.727 / max 2.441. Clusters 0,1,2,3,5,10. Options: REVISE (route measure): re-measure the floor profile per azimuth (trough/gutter), the V-rib centre lines and the central post radius on the full-res scan, then rebuild.
- **LUGS (functional interface)**: Lug under-face ramp ends: scan rises to z~-3 at each lug's trailing end (theta ~76/196/317) while the CAD keeps a linear ramp to ~-4.7; zone scan->CAD p95 0.740 / max 1.394, CAD->scan max 1.995. Clusters 8,9 and CAD->scan 5,6,7. Options: REVISE: measure the under-face height at several stations per lug (the request already lists F03 lug under-face height at both ends) and model the end ramp; a caliper/feeler reading of F03 would arbitrate.
- **NECK (arch foot)**: Dropped arch-foot round: scan legs curve inward to a rounded foot, CAD legs are straight to a sharp foot ~1 mm lower (overlay x=40); zone scan->CAD p95 0.420 / max 0.841. Options: REVISE: reinstate the arch-foot round / leg curvature from sections.
- **WIRE and bore top (z -6..-2)**: Simplified torus wire arcs at slightly different height/radius and ends buried differently from the scan (clusters 4,6,7,11); zone WIRE scan->CAD p95 0.500 / max 1.333. Options: REVISE the arc fits (centre/height per arc) or declare the simplification and seek ACCEPT-BAND for this region only.
- **Unscanned: spout pockets, grip strip**: CAD->scan only: invented pocket bores and an interpolated grip where the scan has holes (L2). Not fixable by geometry without data. Options: rescan or accept (ACCEPT-BAND) after the fixable misses above are closed.

## Declared limitations (each with its re-run trigger)

1. Tier-1 not run: 0 of 8 requested dims have a caliper reading (owner chose scan-only, DECISIONS MEASUREMENTS); absolute scale not caliper-verified (CHK-SCALE FLAG). All 8 are ABSENT, not passed. F01 is reported CAD-only. — **Re-run trigger:** any caliper reading (e.g. F01 bore ID, F02 ledge depth, F04 spout spacing) -> fill input/MEASUREMENTS.md, rehash, re-run verify
2. Unscanned/occluded regions carry invented or interpolated CAD: the outlet/spout pocket bores (CAD->scan clusters 0/1, ~10.5k samples, d up to 5.7 mm), the unscanned strip along the +Y side of the grip (x 105-159, CAD->scan cluster 3, 2223 samples, d up to 5.2 mm; the ray test calls it observable, so it inflates the observable CAD->scan number), rib flanks in shadow. These residuals will remain after a geometry fix and may need an ACCEPT-BAND decision. — **Re-run trigger:** a rescan that covers the pocket interiors and the grip strip (e.g. matte spray), or a depth-gauge reading of the pocket depth
3. Fine tessellation (0.005 mm/0.05 rad) of both STEPs is not watertight by one zero-area triangle each (datum frame at (16.7, 19.0, -46.2), spout-1 root / bottom-round junction); with it removed the mesh is watertight (qa/tess_watertight_probe.json). BRep is valid, 1 closed shell, 0 naked edges. step_check.py does not include this in its validity flag. — **Re-run trigger:** any rebuild -> re-run step_check and the probe
4. ICP did not converge at the default cap (60 its, qa/registration_run1_cap60.json: 0.1760 deg / 0.0468 mm); cap raised once to 400 and converged at 85 its (0.1761 deg / 0.0469 mm). Stop was reached on one iteration whose rotation fell under arccos precision; neighbouring steps were 1e-6..8e-6. Both runs agree to 1e-4 deg / 1e-4 mm. — **Re-run trigger:** any rebuild -> re-run ICP at the default cap first
5. Deliverable is ONE fused solid of an assembly (owner PART-CLASS): internal interfaces between cup, insert, grip, cap, screws and wire are not represented; screw heads and wire are simplified. — **Re-run trigger:** an owner decision to model the bodies separately
6. Observability split ran through qa/scripts/run_gate_lowmem.py (ray chunk 200 instead of the hard-coded 2000; memory only, per-point result identical) because the unmodified deviation_gate.py was OOM-killed on this 15 GB machine. — **Re-run trigger:** observability chunk exposed/fixed in the script -> re-run deviation_gate.py directly

## Claim boundary

Not a pass under baseline-skill plastic (p95<=0.30 / max<=0.80): QA does not certify this STEP for fit, tooling or manufacture. The cup outer wall (p95 0.092), rim face and handle agree with the scan well, but that is a regional observation, not a grade. No dimension is caliper-verified (absolute scale unverified); the one fused solid is not a model of the separate bodies; pocket interiors and a strip of the grip are invented/interpolated.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
