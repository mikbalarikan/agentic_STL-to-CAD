# VERDICT: BAND_NOT_MET

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: Fresh agent/context that did not build the model; QA scripts from stl-re-verify plus QA-owned workarounds in qa/scripts/ (datum_audit_planes.py, make_masks.py, probes). Inputs: input/, intake/INTAKE_CARD.md, intake/alignment.json (selection + gate frame only), intake/regime.json, build/*.step, export_check/fillets/face_stats/MODELING_PLAN; build/model.py only grepped read-only for CHK-PATCHWORK. measure/params.json, PARAM_TABLE.md, measure/figures, build_log.txt and the builder's self-check numbers were not used. No INDEP entry needed in DECISIONS.md.

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `cliff_bumper_sensor_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 7736.382 mm³ | PASS |
| Validity `cliff_bumper_sensor.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 7736.382 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.075° / origin 0.034 mm / points p95 0.043 max 0.048 mm | within (not blocking) |
| Registration (ICP) | converged | 60/60 its, 0.122° / 0.019 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 243829 · rms 0.124 · p50 0.042 · p95 0.225 · p99 0.578 · max 1.936 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 19996 · rms 0.170 · p50 0.043 · p95 0.331 · p99 0.776 · max 1.920 | FAIL |
| zone:Z-LENS lens frame rib and windows:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 39263 · rms 0.231 · p50 0.074 · p95 0.589 · p99 0.752 · max 0.915 | FAIL |
| zone:Z-LENS lens frame rib and windows:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 26955 · rms 0.200 · p50 0.052 · p95 0.518 · p99 0.744 · max 0.856 | FAIL |
| zone:Z-POCKET shelf underside pockets:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 31874 · rms 0.083 · p50 0.038 · p95 0.170 · p99 0.292 · max 0.719 | PASS |
| zone:Z-POCKET shelf underside pockets:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 29310 · rms 0.136 · p50 0.036 · p95 0.234 · p99 0.665 · max 1.261 | FAIL |
| zone:Z-TAB tabs and guide rails:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 21143 · rms 0.077 · p50 0.043 · p95 0.160 · p99 0.223 · max 0.332 | PASS |
| zone:Z-TAB tabs and guide rails:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 21658 · rms 0.085 · p50 0.045 · p95 0.179 · p99 0.247 · max 0.441 | PASS |
| zone:Z-TOP top seating face:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 59768 · rms 0.047 · p50 0.024 · p95 0.095 · p99 0.160 · max 0.307 | PASS |
| zone:Z-TOP top seating face:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 74365 · rms 0.055 · p50 0.023 · p95 0.105 · p99 0.216 · max 0.564 | PASS |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 251181 · rms 0.260 · p50 0.044 · p95 0.376 · p99 1.386 · max 3.077
- scan→CAD masked: n 243829 · rms 0.124 · p50 0.042 · p95 0.225 · p99 0.578 · max 1.936
- CAD→scan unmasked: n 300000 · rms 0.175 · p50 0.044 · p95 0.341 · p99 0.800 · max 2.018
- CAD→scan masked: n 261694 · rms 0.103 · p50 0.039 · p95 0.190 · p99 0.426 · max 1.261
- CAD→scan observable only: n 19996 · rms 0.170 · p50 0.043 · p95 0.331 · p99 0.776 · max 1.920; unobservable fraction 0.02 %

Masks:

- **M1 window interior seen through clear lens** (scan_to_cad): The two lens windows are transparent (photo_2, photo_4; INTAKE E15, §2 artefact zones, §8): the scanner saw through them and returned interior material. Scan points deeper than 1.3 mm behind the scan-fitted lens-frame plane (window face nominal ~0.8 mm, INTAKE E04) inside the window aperture and above the nose-bottom envelope are interior, not envelope. Located from the scan only (qa/scripts/make_masks.py).; fraction 2.70 %; inside n 6790 · rms 1.372 · p50 1.089 · p95 2.228 · p99 2.831 · max 3.077
- **M2 E14 tab blob (declared debris, open question)** (scan_to_cad): Irregular ~1.6 mm lump on the +Y tab top at x -8.2..-7.1 (INTAKE E14): single component, no flat top, not mirrored on the -Y tab, not resolvable in photos; intake declared it debris/artefact (not modelled) with an OPEN QUESTION. Masked as an artefact; carried as a limitation because it is not proven debris.; fraction 0.22 %; inside n 562 · rms 0.810 · p50 0.664 · p95 1.412 · p99 1.495 · max 1.540
- **M3 wire-slot roof not scanned** (cad_to_scan): The wire-slot roof was never scanned: open-boundary loop (283 verts, x -1.12..1.16, z up to -2.59) at the rear bottom centre (INTAKE §3, E12). CAD roof height is scan-extent provenance (MODELING_PLAN §6); CAD->scan distance there measures missing coverage, not a surface deviation.; fraction 0.00 %; inside n 0
- **M4 open boundary** (cad_to_scan): Distance from a CAD point to a scan hole EDGE is not a surface deviation (18 open loops, 3,216 boundary edges, INTAKE §2/§3). B02 parameter 0.8 mm; radius sweep reported.; fraction 11.16 %; inside n 33476 · rms 0.415 · p50 0.167 · p95 0.907 · p99 1.358 · max 2.018
- **M5 transparent window faces (CAD side)** (cad_to_scan): CAD window faces / lower recess walls (0.3..1.3 mm behind the scan-fitted lens-frame plane, inside the aperture): the clear window face was only partly registered by the scanner (large open loops 789/704 verts in the windows, INTAKE §3), so CAD->scan distance there measures transparency (hole or interior behind), not the envelope.; fraction 4.77 %; inside n 14313 · rms 0.487 · p50 0.220 · p95 1.084 · p99 1.572 · max 2.018

Zones:

- Z-TAB tabs and guide rails [whole] scan_to_cad: unmasked n 21705 · rms 0.151 · p50 0.045 · p95 0.185 · p99 0.799 · max 1.540 | masked n 21143 · rms 0.077 · p50 0.043 · p95 0.160 · p99 0.223 · max 0.332
- Z-TAB tabs and guide rails [whole] cad_to_scan: unmasked n 22371 · rms 0.088 · p50 0.046 · p95 0.186 · p99 0.264 · max 0.475 | masked n 21658 · rms 0.085 · p50 0.045 · p95 0.179 · p99 0.247 · max 0.441
- Z-TOP top seating face [whole] scan_to_cad: unmasked n 59768 · rms 0.047 · p50 0.024 · p95 0.095 · p99 0.160 · max 0.307 | masked n 59768 · rms 0.047 · p50 0.024 · p95 0.095 · p99 0.160 · max 0.307
- Z-TOP top seating face [whole] cad_to_scan: unmasked n 74662 · rms 0.055 · p50 0.023 · p95 0.104 · p99 0.216 · max 0.564 | masked n 74365 · rms 0.055 · p50 0.023 · p95 0.105 · p99 0.216 · max 0.564
- Z-POCKET shelf underside pockets [whole] scan_to_cad: unmasked n 31874 · rms 0.083 · p50 0.038 · p95 0.170 · p99 0.292 · max 0.719 | masked n 31874 · rms 0.083 · p50 0.038 · p95 0.170 · p99 0.292 · max 0.719
- Z-POCKET shelf underside pockets [whole] cad_to_scan: unmasked n 38583 · rms 0.192 · p50 0.044 · p95 0.425 · p99 0.876 · max 1.261 | masked n 29310 · rms 0.136 · p50 0.036 · p95 0.234 · p99 0.665 · max 1.261
- Z-LENS lens frame rib and windows [whole] scan_to_cad: unmasked n 45896 · rms 0.555 · p50 0.098 · p95 1.394 · p99 2.038 · max 2.983 | masked n 39263 · rms 0.231 · p50 0.074 · p95 0.589 · p99 0.752 · max 0.915
- Z-LENS lens frame rib and windows [whole] cad_to_scan: unmasked n 50140 · rms 0.327 · p50 0.086 · p95 0.728 · p99 1.180 · max 2.018 | masked n 26955 · rms 0.200 · p50 0.052 · p95 0.518 · p99 0.744 · max 0.856
- I-window-interior (reported) [interior] scan_to_cad: unmasked n 29383 · rms 0.706 · p50 0.195 · p95 1.731 · p99 2.286 · max 3.077 | masked n 22593 · rms 0.287 · p50 0.117 · p95 0.663 · p99 0.787 · max 0.915
- I-window-interior (reported) [interior] cad_to_scan: unmasked n 28056 · rms 0.409 · p50 0.161 · p95 0.844 · p99 1.377 · max 2.018 | masked n 10124 · rms 0.298 · p50 0.093 · p95 0.700 · p99 0.789 · max 0.856
- R-nose x<-21.2 [region] scan_to_cad: unmasked n 45896 · rms 0.555 · p50 0.098 · p95 1.394 · p99 2.038 · max 2.983 | masked n 39263 · rms 0.231 · p50 0.074 · p95 0.589 · p99 0.752 · max 0.915
- R-nose x<-21.2 [region] cad_to_scan: unmasked n 50140 · rms 0.327 · p50 0.086 · p95 0.728 · p99 1.180 · max 2.018 | masked n 26955 · rms 0.200 · p50 0.052 · p95 0.518 · p99 0.744 · max 0.856
- R-cover -21.2<=x<-1.2 [region] scan_to_cad: unmasked n 126390 · rms 0.133 · p50 0.039 · p95 0.165 · p99 0.383 · max 3.077 | masked n 125671 · rms 0.095 · p50 0.039 · p95 0.158 · p99 0.276 · max 1.936
- R-cover -21.2<=x<-1.2 [region] cad_to_scan: unmasked n 152673 · rms 0.088 · p50 0.037 · p95 0.156 · p99 0.274 · max 1.499 | masked n 150016 · rms 0.071 · p50 0.037 · p95 0.149 · p99 0.236 · max 0.564
- R-cap -1.2<=x<0 [region] scan_to_cad: unmasked n 17983 · rms 0.092 · p50 0.044 · p95 0.169 · p99 0.400 · max 0.596 | masked n 17983 · rms 0.092 · p50 0.044 · p95 0.169 · p99 0.400 · max 0.596
- R-cap -1.2<=x<0 [region] cad_to_scan: unmasked n 27203 · rms 0.183 · p50 0.048 · p95 0.257 · p99 1.003 · max 1.511 | masked n 24756 · rms 0.082 · p50 0.046 · p95 0.175 · p99 0.260 · max 0.462
- R-shelf x>=0 [region] scan_to_cad: unmasked n 60912 · rms 0.079 · p50 0.039 · p95 0.170 · p99 0.264 · max 0.719 | masked n 60912 · rms 0.079 · p50 0.039 · p95 0.170 · p99 0.264 · max 0.719
- R-shelf x>=0 [region] cad_to_scan: unmasked n 69984 · rms 0.159 · p50 0.042 · p95 0.305 · p99 0.761 · max 1.281 | masked n 59967 · rms 0.114 · p50 0.038 · p95 0.212 · p99 0.410 · max 1.261
- R-bottom z<-8.5 [region] scan_to_cad: unmasked n 54705 · rms 0.073 · p50 0.046 · p95 0.149 · p99 0.206 · max 0.561 | masked n 54705 · rms 0.073 · p50 0.046 · p95 0.149 · p99 0.206 · max 0.561
- R-bottom z<-8.5 [region] cad_to_scan: unmasked n 72392 · rms 0.070 · p50 0.045 · p95 0.142 · p99 0.212 · max 0.462 | masked n 71374 · rms 0.069 · p50 0.044 · p95 0.138 · p99 0.209 · max 0.462

Over-band scan→CAD points (> 0.8 mm): 6421 (2.556 %) in 4 clusters ≥ 20 pts.

- cluster 0: n 3072, centroid [-23.76, -7.689, -7.406], r [22.752, 27.623], θ [184.3, 208.3], max 2.181 — Window interior (-Y window): material seen THROUGH the transparent lens window (INTAKE E15; photo_2/photo_4). Mostly inside M1; the residual (masked max 0.915) is the see-through layer just shallower than M1's conservative 1.3 mm staircase depth / above the nose-bottom floor (qa/posthoc_sensitivity.json, qa/lens_breakdown.json). Artefact, not a missing feature.
- cluster 1: n 2877, centroid [-23.384, 4.439, -7.156], r [20.985, 26.806], θ [158.7, 176.7], max 3.077 — Window interior (+Y window), same cause as cluster 0; also contains the intake-removed 1,063-face disconnected fragment (x -25.8..-23.4, y 6.6..10.0, z -8.1..-7.0) that floats behind the +Y window (qa/probe_cluster_s2c2.json). Artefact, not a missing feature.
- cluster 2: n 254, centroid [-3.563, -17.029, -1.207], r [16.558, 18.226], θ [256.2, 259.2], max 1.936 — Disconnected scan fragment: the 684-face, 2.94 mm2 separate body (x -4.11..-3.12, y -17.88..-15.69, z -2.16..-0.12) floating ~1.5-1.9 mm outside the -Y side wall near the top; intake removed it as a fragment before modelling (alignment.json removed.fragments_pct 0.3499, INTAKE §2 'wire stubs'), but the gate runs on the raw full-res scan. Not connected to the part (qa/probe_cluster_s2c2.json, overlay x=-3.6). NOT masked (would be a post-hoc mask); it alone sets the masked scan->CAD max 1.936.
- cluster 3: n 215, centroid [-7.411, 18.275, -3.329], r [19.247, 20.082], θ [111.0, 113.7], max 1.540 — E14 blob on the +Y tab (x -8.0..-7.1, y 17.8..18.6, up to z -2.8): irregular lump, single component, no flat top, not mirrored on the -Y tab (overlay y=18.5 / x=-7.6); intake declared debris with an open question. Inside M2. Stays an open question (limitation L3).

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | finding | zone Z-TAB tabs and guide rails scan_to_cad |
| CHK-CLUSTER | pass | 4 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | Graded after QA's own ICP (qa/registration.json, T_refine QA-only, never written back); datum re-derived by QA code on the raw scan; no expected value taken from params.json or the builder. The builder's 'self-check' in MODELING_PLAN.md (working mesh, 60k/40k samples) is a consistency check, not independent evidence, and was not used. |
| CHK-LIKE4LIKE | n/a | Iteration 1; no _itN_SUPERSEDED/ to compare against. |
| CHK-INDEP | pass | Fresh context; see independence. |
| CHK-FILLET | pass | export_check.json / fillets.json: 9 of 9 fillets OK, target == used (2.072, 2.137, 7.758, 2.072, 0.53, 1.74, 2.137, 1.107, 6.033 mm); no REDUCED/FAILED. Declared: nose_tip_R propagated to the whole 5-edge lens outline (MODELING_PLAN as-built); window_corner_R and nose_top_R are assumed values (plan §6). |
| CHK-PATCHWORK | pass | QA census (qa/step_check.json): 106 faces = 83 plane / 17 cylinder / 6 B-spline; analytic area share 98.95 %. The 6 B-spline faces are fillet-corner patches the plan anticipated (lens-outline round x cup round). No thousands of facets. grep of build/model.py: no loft/ruled/Polyline/spline/sweep/slice stack. |
| CHK-ENUM | finding | E01-E13 all present in the CAD (overlays: box, rounds, nose cup, lens frame + rib + 2 recessed windows, seam groove, cap, shelf, 3 pockets, rails, tabs, wire slot, 2 bottom ramps). E15 correctly not modelled. Finding: E14 (+Y tab blob) stays an OPEN QUESTION - not modelled and masked (M2); if it is a real detent the CAD lacks it. All scan->CAD over-band clusters reviewed: no missing moulded feature found (clusters = window interior, a disconnected scan fragment, the E14 blob). |
| CHK-ACHIEVABLE | n/a | Tier-1 not run (no calipers, DECISIONS.md MEASUREMENTS); nothing to attribute. |
| PHOTO-PLAUSIBILITY | pass | photo_1..photo_5 walked (low-res, no scale): clear cover over black body, lens nose with two clear windows split by a black rib (photo_2, photo_4), side tab flanges (photo_1, 3, 4), black rear end with harness leaving at the bottom centre (photo_5 = wire slot), flat top. All present in the CAD. Pockets (E09) and ramps (E13) are not resolvable in the photos but are in the scan; E14 not resolvable. No CAD feature is absent from both photos and scan (nothing hallucinated). |

## Misses, per region

- scan_to_cad:masked: p95 0.225 max 1.936 vs 0.3/0.8
- cad_to_scan_observable: p95 0.331 max 1.920 vs 0.3/0.8
- zone:Z-LENS lens frame rib and windows:scan_to_cad: p95 0.589 max 0.915 vs 0.3/0.8
- zone:Z-LENS lens frame rib and windows:cad_to_scan: p95 0.518 max 0.856 vs 0.3/0.8
- zone:Z-POCKET shelf underside pockets:cad_to_scan: p95 0.234 max 1.261 vs 0.3/0.8
- **whole part scan->CAD (masked max 1.936 > 0.80; p95 0.225 passes; unmasked p95 0.377 / max 3.077)**: The masked max is set by a disconnected 684-face scan fragment floating outside the -Y wall (intake removed it before modelling, but the gate uses the raw full-res scan; not masked post hoc). Post-hoc, NOT gated: excluding the intake-removed fragments leaves max 0.915, set by 178 see-through interior points just outside the conservative window mask M1 (qa/posthoc_sensitivity.json). Unmasked p95 is driven by the window interior (M1 inside p95 2.228). Options: (a) human ACCEPT-BAND with these causes; (b) next QA run: pre-register a mask for intake-removed disconnected fragments and a less conservative window-interior mask, declared before results; (c) rescan with the windows matted and the fragment cleaned. No geometry change indicated.
- **whole part CAD->scan observable (p95 0.331 > 0.30, max 1.920 > 0.80; masked p95 0.190 / max 1.261)**: Observability removed only 0.02 % (everything is in line of sight); the excess is CAD surface with no scan behind it: transparent window faces (M5 inside p95 1.084), scan hole edges (M4 inside p95 0.907), the unscanned wire slot (cluster, max 1.511) and unscanned pocket ceiling corners (max 1.261, remains after masks). Options: rescan with window matting and pocket/slot coverage; caliper the slot roof and pocket depth; or human ACCEPT-BAND.
- **Z-LENS (masked scan->CAD p95 0.589 / max 0.915, CAD->scan p95 0.518 / max 0.856; unmasked 1.394/2.983 and 0.728/2.018)**: Transparency: 80 % of masked points >0.30 are in the 0.3-1.3 mm window/see-through layer where window face and interior cannot be separated; frame/rib p95 0.297, cup outer skin p95 0.246 / max 0.803, cup-body junction p95 0.290 (qa/lens_breakdown.json). Options: rescan with matted windows or depth-gauge the recess; human ACCEPT-BAND for the window zone.
- **Z-POCKET CAD->scan (max 1.261 masked and unmasked; unmasked p95 0.425, masked p95 0.234)**: Pocket ceiling corners / back walls unscanned (open loops at z -3.7..-1.4); scanned pocket surfaces agree (Z-POCKET scan->CAD p95 0.170 / max 0.719). Options: caliper pocket width/depth, or rescan the pockets; human ACCEPT-BAND.

## Declared limitations (each with its re-run trigger)

1. Tier-1 not run: scan-only run, no caliper readings (DECISIONS.md MEASUREMENTS). No dimension is caliper-verified. — **Re-run trigger:** any caliper reading -> fill input/MEASUREMENTS.md, rehash, re-run verify with Tier-1
2. Absolute scale not caliper-verified (CHK-SCALE flag at intake; units assumed mm, no scale applied). — **Re-run trigger:** any caliper reading (e.g. width over tabs, overall height) -> re-run intake scale check and verify
3. Mask-dependent zone pass: Z-TAB scan->CAD passes only with mask M2 (E14 blob): masked max 0.332 mm; UNMASKED max 1.540 mm, 0.740 over the 0.80 band. E14 is an open question (debris vs real detent). — **Re-run trigger:** owner confirms E14 (close-up photo or physical check): debris -> M2 stands; real feature -> REVISE (model it) and re-verify
4. Transparent lens windows: all Z-LENS and much of the whole-part numbers depend on masks M1 (scan interior, 2.70 % of scan points) and M5 (CAD window faces, 4.77 % of CAD samples); the window-face recess depth cannot be verified from this scan (80 % of Z-LENS masked points >0.30 lie in the 0.3-1.3 mm window/see-through layer, qa/lens_breakdown.json). — **Re-run trigger:** rescan with the windows matted (developer spray) or a depth-gauge reading of the window recess
5. Unscanned geometry: wire-slot roof/walls and pocket ceiling corners have no scan (open loops); CAD there is scan-extent provenance. Mask M3 (slot roof) was mis-located at z -2.59 and removed 0 points; it was deliberately NOT re-located after results were seen, so the slot shows as an unmasked CAD->scan cluster (max 1.511). — **Re-run trigger:** slot roof height / pocket depth by caliper or a rescan covering the slot and pockets
6. Datum audit re-derived with QA's own plane-origin code (datum_audit.py cannot express origin.xy_planes); result within the reference band (0.075 deg / 0.034 mm), but it is crop- and rule-sensitive: a wider side-wall crop gives 0.53 deg (the wall steps ~0.06-0.1 mm at x~-15), a literal plane-intersection origin gives 0.26 mm (rear wall 1.0 deg out of perpendicular). Report-only. — **Re-run trigger:** datum_audit.py gains plane-origin support, or the datum is redone -> re-run the audit
7. Validity note: B-rep is one valid closed solid (BRepCheck valid, 0 naked edges) in both frames, but the 0.005/0.05 QA tessellation is not strictly watertight: one zero-area triangle at a B-spline fillet-corner patch (datum x -23.45, y 14.32, z -2.08) makes one edge used 4x; watertight after dropping it; no short edges (<0.05 mm) or sliver faces in the B-rep (qa/tess_watertight_probe.json, qa/brep_near_probe.json). — **Re-run trigger:** any rebuild -> re-run step_check
8. ICP converged on the last permitted iteration of the default cap (60/60, final step 2.9e-7 < 1e-6); a check run with cap 120 converged at the same iteration with the identical correction (qa/registration_cap120_check.json). — **Re-run trigger:** none required; re-check if the STEP or masks change

## Claim boundary

BAND_NOT_MET under baseline-skill plastic (p95 0.30 / max 0.80). The CAD matches the opaque, scanned envelope closely (Z-TOP scan->CAD max 0.307, Z-TAB masked max 0.332, R-bottom max 0.561, R-cover masked CAD->scan max 0.564, scan->CAD p95 0.225 masked), but it is NOT verified: at the lens windows (transparent), the wire-slot roof and pocket ceilings (unscanned), for E14 (open question) or in absolute scale (no calipers). Not fit for tooling, mould or fit-critical manufacture of the bumper interface until calipered; delivery requires a recorded human ACCEPT-BAND.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
