# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: fresh agent (stl-re-verify), did not build the model; QA scripts from skills/stl-re-verify only, plus declared run-local helpers in qa/src/ (observability chunking wrapper, residual/mask composition analysis, datum supplement, zoom sections, heatmaps). Read only input/, intake/INTAKE_CARD.md, alignment.json, regime.json, build/*.step, build/export_check.json, build/MODELING_PLAN.md, DECISIONS.md; build/model.py grepped read-only for CHK-PATCHWORK, never imported. BUILDER_REPORT.md, build_log.txt, measure/ not opened. The STEP was tessellated by QA (0.005 mm / 0.05 rad); build/*_cad.stl not used. MODELING_PLAN.md quotes the builder's self-check numbers; they were not used as expectations.

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `OD-H21_antidrip-valve_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 19368.649 mm³ | PASS |
| Validity `OD-H21_antidrip-valve.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 19368.649 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 0.018° / origin 0.007 mm / points p95 0.014 max 0.016 mm | within (not blocking) |
| Registration (ICP) | converged | 39/60 its, 0.045° / 0.015 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 297871 · rms 0.088 · p50 0.042 · p95 0.177 · p99 0.296 · max 0.909 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 19959 · rms 0.186 · p50 0.044 · p95 0.258 · p99 0.651 · max 3.007 | FAIL |
| zone:I1 nozzle spigot OD lugs latch:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 30992 · rms 0.125 · p50 0.041 · p95 0.264 · p99 0.535 · max 0.888 | FAIL |
| zone:I1 nozzle spigot OD lugs latch:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 31843 · rms 0.121 · p50 0.039 · p95 0.296 · p99 0.425 · max 0.843 | FAIL |
| zone:I2 nozzle shoulder:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 4184 · rms 0.063 · p50 0.045 · p95 0.120 · p99 0.147 · max 0.204 | PASS |
| zone:I2 nozzle shoulder:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 13299 · rms 0.095 · p50 0.049 · p95 0.215 · p99 0.337 · max 0.524 | PASS |
| zone:I3 outlet thread and O-ring:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 18803 · rms 0.085 · p50 0.055 · p95 0.167 · p99 0.218 · max 0.718 | PASS |
| zone:I3 outlet thread and O-ring:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 13820 · rms 0.093 · p50 0.054 · p95 0.184 · p99 0.309 · max 0.576 | PASS |
| zone:I4 barb tube and bulb:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 16774 · rms 0.094 · p50 0.040 · p95 0.205 · p99 0.343 · max 0.777 | PASS |
| zone:I4 barb tube and bulb:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 16122 · rms 0.078 · p50 0.040 · p95 0.168 · p99 0.264 · max 0.410 | PASS |
| zone:I5 ring windows:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 7054 · rms 0.159 · p50 0.084 · p95 0.350 · p99 0.509 · max 0.769 | FAIL |
| zone:I5 ring windows:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 5894 · rms 0.230 · p50 0.094 · p95 0.516 · p99 0.774 · max 1.095 | FAIL |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 300181 · rms 0.091 · p50 0.042 · p95 0.180 · p99 0.309 · max 1.088
- scan→CAD masked: n 297871 · rms 0.088 · p50 0.042 · p95 0.177 · p99 0.296 · max 0.909
- CAD→scan unmasked: n 300000 · rms 0.189 · p50 0.044 · p95 0.265 · p99 0.690 · max 3.229
- CAD→scan masked: n 289487 · rms 0.105 · p50 0.043 · p95 0.220 · p99 0.399 · max 1.095
- CAD→scan observable only: n 19959 · rms 0.186 · p50 0.044 · p95 0.258 · p99 0.651 · max 3.007; unobservable fraction 0.20 %

Masks:

- **M1 unscanned bore interiors** (scan_to_cad): the three end bores (nozzle, outlet, barb) were seen only 1.5-4 mm deep; beyond that the scanner bridged them with a membrane (scan side: artefact, not a part surface) and the CAD bore wall/floor has no scan behind it (CAD side: coverage gap). Neither is a surface deviation of the modelled part.; fraction 0.77 %; inside n 2310 · rms 0.275 · p50 0.123 · p95 0.638 · p99 0.919 · max 1.088
- **M1 unscanned bore interiors** (cad_to_scan): the three end bores (nozzle, outlet, barb) were seen only 1.5-4 mm deep; beyond that the scanner bridged them with a membrane (scan side: artefact, not a part surface) and the CAD bore wall/floor has no scan behind it (CAD side: coverage gap). Neither is a surface deviation of the modelled part.; fraction 2.40 %; inside n 7199 · rms 0.988 · p50 0.344 · p95 2.259 · p99 2.754 · max 3.229
- **M2 open boundary** (cad_to_scan): distance from CAD to a scan hole EDGE (7 open loops: bore mouths, 2 ring windows, 2 skirt slits) is not a surface deviation; fraction 2.72 %; inside n 8159 · rms 0.906 · p50 0.375 · p95 2.097 · p99 2.734 · max 3.229

Zones:

- I1 nozzle spigot OD lugs latch [whole] scan_to_cad: unmasked n 30992 · rms 0.125 · p50 0.041 · p95 0.264 · p99 0.535 · max 0.888 | masked n 30992 · rms 0.125 · p50 0.041 · p95 0.264 · p99 0.535 · max 0.888
- I1 nozzle spigot OD lugs latch [whole] cad_to_scan: unmasked n 31843 · rms 0.121 · p50 0.039 · p95 0.296 · p99 0.425 · max 0.843 | masked n 31843 · rms 0.121 · p50 0.039 · p95 0.296 · p99 0.425 · max 0.843
- I2 nozzle shoulder [whole] scan_to_cad: unmasked n 4184 · rms 0.063 · p50 0.045 · p95 0.120 · p99 0.147 · max 0.204 | masked n 4184 · rms 0.063 · p50 0.045 · p95 0.120 · p99 0.147 · max 0.204
- I2 nozzle shoulder [whole] cad_to_scan: unmasked n 13299 · rms 0.095 · p50 0.049 · p95 0.215 · p99 0.337 · max 0.524 | masked n 13299 · rms 0.095 · p50 0.049 · p95 0.215 · p99 0.337 · max 0.524
- I3 outlet thread and O-ring [whole] scan_to_cad: unmasked n 18803 · rms 0.085 · p50 0.055 · p95 0.167 · p99 0.218 · max 0.718 | masked n 18803 · rms 0.085 · p50 0.055 · p95 0.167 · p99 0.218 · max 0.718
- I3 outlet thread and O-ring [whole] cad_to_scan: unmasked n 13844 · rms 0.093 · p50 0.054 · p95 0.185 · p99 0.311 · max 0.576 | masked n 13820 · rms 0.093 · p50 0.054 · p95 0.184 · p99 0.309 · max 0.576
- I4 barb tube and bulb [whole] scan_to_cad: unmasked n 16774 · rms 0.094 · p50 0.040 · p95 0.205 · p99 0.343 · max 0.777 | masked n 16774 · rms 0.094 · p50 0.040 · p95 0.205 · p99 0.343 · max 0.777
- I4 barb tube and bulb [whole] cad_to_scan: unmasked n 16241 · rms 0.084 · p50 0.040 · p95 0.173 · p99 0.287 · max 0.839 | masked n 16122 · rms 0.078 · p50 0.040 · p95 0.168 · p99 0.264 · max 0.410
- I5 ring windows [whole] scan_to_cad: unmasked n 7054 · rms 0.159 · p50 0.084 · p95 0.350 · p99 0.509 · max 0.769 | masked n 7054 · rms 0.159 · p50 0.084 · p95 0.350 · p99 0.509 · max 0.769
- I5 ring windows [whole] cad_to_scan: unmasked n 7496 · rms 0.270 · p50 0.111 · p95 0.647 · p99 0.865 · max 1.095 | masked n 5894 · rms 0.230 · p50 0.094 · p95 0.516 · p99 0.774 · max 1.095
- B1 nozzle bore interior [interior] scan_to_cad: unmasked n 1188 · rms 0.144 · p50 0.062 · p95 0.313 · p99 0.496 · max 0.738 | masked n 0
- B1 nozzle bore interior [interior] cad_to_scan: unmasked n 6034 · rms 1.062 · p50 0.355 · p95 2.341 · p99 2.776 · max 3.229 | masked n 0
- B2 outlet end bore interior [interior] scan_to_cad: unmasked n 673 · rms 0.400 · p50 0.207 · p95 0.872 · p99 1.030 · max 1.088 | masked n 0
- B2 outlet end bore interior [interior] cad_to_scan: unmasked n 693 · rms 0.466 · p50 0.377 · p95 0.826 · p99 0.923 · max 0.992 | masked n 0
- B3 barb end bore interior [interior] scan_to_cad: unmasked n 449 · rms 0.307 · p50 0.187 · p95 0.623 · p99 0.703 · max 0.763 | masked n 0
- B3 barb end bore interior [interior] cad_to_scan: unmasked n 472 · rms 0.399 · p50 0.241 · p95 0.801 · p99 0.892 · max 0.922 | masked n 0
- R nozzle [region] scan_to_cad: unmasked n 33509 · rms 0.126 · p50 0.043 · p95 0.263 · p99 0.526 · max 0.888 | masked n 32321 · rms 0.125 · p50 0.043 · p95 0.260 · p99 0.528 · max 0.888
- R nozzle [region] cad_to_scan: unmasked n 39453 · rms 0.431 · p50 0.047 · p95 0.849 · p99 2.182 · max 3.229 | masked n 33333 · rms 0.125 · p50 0.041 · p95 0.303 · p99 0.423 · max 0.843
- R nut [region] scan_to_cad: unmasked n 38429 · rms 0.089 · p50 0.048 · p95 0.188 · p99 0.249 · max 0.453 | masked n 38429 · rms 0.089 · p50 0.048 · p95 0.188 · p99 0.249 · max 0.453
- R nut [region] cad_to_scan: unmasked n 45069 · rms 0.100 · p50 0.048 · p95 0.223 · p99 0.321 · max 0.524 | masked n 45069 · rms 0.100 · p50 0.048 · p95 0.223 · p99 0.321 · max 0.524
- R band [region] scan_to_cad: unmasked n 38924 · rms 0.069 · p50 0.041 · p95 0.139 · p99 0.199 · max 0.320 | masked n 38924 · rms 0.069 · p50 0.041 · p95 0.139 · p99 0.199 · max 0.320
- R band [region] cad_to_scan: unmasked n 40089 · rms 0.094 · p50 0.048 · p95 0.179 · p99 0.340 · max 0.766 | masked n 40089 · rms 0.094 · p50 0.048 · p95 0.179 · p99 0.340 · max 0.766
- R body outlet web [region] scan_to_cad: unmasked n 67900 · rms 0.087 · p50 0.042 · p95 0.160 · p99 0.287 · max 1.088 | masked n 67227 · rms 0.078 · p50 0.041 · p95 0.154 · p99 0.246 · max 0.718
- R body outlet web [region] cad_to_scan: unmasked n 62521 · rms 0.114 · p50 0.043 · p95 0.232 · p99 0.462 · max 0.992 | masked n 61800 · rms 0.104 · p50 0.043 · p95 0.213 · p99 0.410 · max 0.846
- R ring skirt [region] scan_to_cad: unmasked n 43251 · rms 0.100 · p50 0.046 · p95 0.201 · p99 0.384 · max 0.909 | masked n 43251 · rms 0.100 · p50 0.046 · p95 0.201 · p99 0.384 · max 0.909
- R ring skirt [region] cad_to_scan: unmasked n 42285 · rms 0.169 · p50 0.051 · p95 0.383 · p99 0.744 · max 1.105 | masked n 39204 · rms 0.139 · p50 0.048 · p95 0.291 · p99 0.597 · max 1.095
- R cap [region] scan_to_cad: unmasked n 49194 · rms 0.068 · p50 0.035 · p95 0.131 · p99 0.232 · max 0.726 | masked n 48959 · rms 0.065 · p50 0.035 · p95 0.127 · p99 0.222 · max 0.491
- R cap [region] cad_to_scan: unmasked n 46816 · rms 0.077 · p50 0.034 · p95 0.145 · p99 0.329 · max 0.591 | masked n 46739 · rms 0.077 · p50 0.034 · p95 0.143 · p99 0.329 · max 0.591
- R barb above cap [region] scan_to_cad: unmasked n 28974 · rms 0.098 · p50 0.044 · p95 0.203 · p99 0.314 · max 0.777 | masked n 28760 · rms 0.094 · p50 0.044 · p95 0.199 · p99 0.294 · max 0.777
- R barb above cap [region] cad_to_scan: unmasked n 23767 · rms 0.107 · p50 0.046 · p95 0.203 · p99 0.354 · max 0.922 | masked n 23253 · rms 0.088 · p50 0.045 · p95 0.191 · p99 0.260 · max 0.410

Over-band scan→CAD points (> 0.8 mm): 106 (0.035 %) in 2 clusters ≥ 20 pts.

- cluster 0: n 48, centroid [28.298, -0.202, 2.459], r [28.135, 28.429], θ [0.1, 360.0], max 1.088 — outlet end bore (L3): scanner bridge membrane curling into the 1.6 mm bore at x 28.1-28.4 (qa/overlays/zoom_clusters.png 'outlet end'). Scanner artefact, inside declared mask M1; unmasked it sets the whole-part scan->CAD max.
- cluster 1: n 40, centroid [-3.178, 3.7, -25.005], r [4.79, 4.981], θ [122.1, 138.1], max 0.888 — nozzle latch window theta 122-138, z -25.3..-24.2, 40 pts, max 0.888: REAL geometric miss. The scan shows the window passing through the lug to the bore wall (r~4.1 at theta 114) with a bridged floor at r 4.8-5.0 at theta 122-138; the CAD cuts only the lug cut-back to r~5.8 there (zoom panels 'nozzle latch theta=114/131', overlay_z Z=-25). Not occlusion: fix by rebuild.

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | finding | zone I4 barb tube and bulb cad_to_scan |
| CHK-CLUSTER | pass | 2 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | datum not ICP'd to own CAD; QA T_refine (qa/registration.json) is QA-only and not written back; no expected value taken from the builder. The builder's build/selfcheck.json (frozen datum, no ICP) is a consistency check, not independent evidence. |
| CHK-LIKE4LIKE | n/a | first QA of this run; no _itN_SUPERSEDED/qa to compare. The builder's in-iteration build 1-3 self-check deltas are not QA runs and are not compared. |
| CHK-INDEP | pass | fresh context; see independence |
| CHK-FILLET | pass | export_check.json fillets: [] (0 3D fillet ops, as MODELING_PLAN §5 plans: every round is a profile arc); nothing silently skipped or reduced |
| CHK-PATCHWORK | pass | QA census: 142 faces, 100 % analytic area (plane 73, cylinder 36, cone 22, torus 11), 0 B-spline/ruled; model.py grep: no loft/sweep/spline; 2 make_polygon calls = a 4-point rectangle profile (model.py:112) and a 5-point web pentagon (model.py:238), not polyline stacks of scan slices |
| CHK-ENUM | pass | every INTAKE feature E01-E25 exists in the CAD (sections + heatmap renders) and every photographed feature is present; nothing hallucinated in kind. Extents of three cut features disagree with the scan (latch window under-cut; ring windows and skirt slits over-cut) -> reported as band misses, not as ENUM. Intake missed E21/E23/E25 (INTAKE addendum, CHK-CLUSTER finding at measure). |
| CHK-ACHIEVABLE | n/a | no Tier-1 (scan-only, no calipers) |
| PHOTO-PLAUSIBILITY | pass | photo_1, photo_2 (catalogue, no scale): nozzle with tip slot, 8-rib nut, band, body, side outlet with collar, black O-ring and thread, cap ring with rectangular windows, cap, hose barb - all present in CAD. Declared simplifications visible in photos: thread modelled as plain cylinder, O-ring fused to the outlet. |

## Misses, per region

- scan_to_cad:masked: p95 0.177 max 0.909 vs 0.3/0.8
- cad_to_scan_observable: p95 0.258 max 3.007 vs 0.3/0.8
- zone:I1 nozzle spigot OD lugs latch:scan_to_cad: p95 0.264 max 0.888 vs 0.3/0.8
- zone:I1 nozzle spigot OD lugs latch:cad_to_scan: p95 0.296 max 0.843 vs 0.3/0.8
- zone:I5 ring windows:scan_to_cad: p95 0.350 max 0.769 vs 0.3/0.8
- zone:I5 ring windows:cad_to_scan: p95 0.516 max 1.095 vs 0.3/0.8
- **nozzle latch window (E04/E23, I1), theta ~114-138, z -25.3..-24.2**: scan->CAD 40 pts up to 0.888 mm: the scanned window goes through the lug to the bore wall (bridged floor r 4.8-5.0); the CAD cut stops at the lug cut-back r ~5.8. Geometric under-cut; the photo_2 slot at the tip supports a through-window. Zone I1 fails max (s2c 0.888, c2s 0.843). Options: REVISE: cut the latch window through the nozzle wall into the bore over the scanned angular span (theta ~110-138 in the datum frame, z -25.3..-24.2), then re-check the phi-90 side (theta ~331: CAD cut-back 0.84 deeper than the scan over 8 pts).
- **ring windows (E17, I5) at theta ~112, ~285, 180, 0**: Zone I5 fails p95 and max (s2c p95 0.350; c2s p95 0.647, max 1.095). At theta ~121 the CAD window sector extends past the scanned window edge (scan skirt closed at r 12.7-13.3; c2s 29 pts up to 1.095); at theta ~285 the CAD pocket (r 12.1-13.3, z 11.8-14.4) is deeper/larger than the scanned dip (c2s 15 pts 1.062); at theta ~110 the scan membrane reaches r 10.4 while the CAD floor is at r ~11.3 (s2c 18 pts 0.909). Geometric extent/depth of the window sectors. Options: REVISE: re-measure each window's theta-span and z-span from the scan's open edges / wall faces (Z=14 section) and cut the windows at those spans; model them as through-windows into the skirt/body gap where the scan shows the opening (theta ~110) rather than a flat floor at r 11.3. Or: caliper the window width/height and accept (ACCEPT-BAND).
- **skirt slits (E21, F08b) at theta ~147 and ~229.5, z 10-11.7**: CAD->scan 17 pts up to 1.051 and 78 pts up to 1.038: the CAD sector pockets are wider in theta (and deeper in z) than the scanned slits (scan slit at Z=11 spans only ~theta 152-164 and ~211-223 and r 10-10.8); where the scan shows a closed ring bottom (theta 147, 229.5) the CAD pocket ceiling has no scan within ~1 mm. Over-cut, i.e. CAD void not supported by the scan. Options: REVISE: trim slit_theta0/1 and slit_u_top to the scan's open-loop extent (L5/L7) and the radial span to r ~10.0-10.8; or remove the slits if the owner does not need the assembly gap modelled.
- **bore interiors (nozzle, outlet, barb; M1) and gate term cad_to_scan_observable**: Unmasked scan->CAD max 1.088 (outlet bore bridge membrane) and CAD->scan observable max 3.007 (unscanned nozzle bore floor counted observable by the ray test through the open bore mouth; skill defect, L6). These are coverage/scanner facts, not fixable by geometry: any blind CAD bore floor has no scan behind it. Options: Keep M1 declared; after the REVISE above, the remaining miss will be this coverage term (a masked pass at best -> limitation) unless observability is made scan-coverage-aware; if not, the owner records ACCEPT-BAND citing the gate hash and 'cad_to_scan_observable'.

## Declared limitations (each with its re-run trigger)

1. Tier-1 not run: scan-only job, no caliper readings supplied (DECISIONS MEASUREMENTS). Every caliper-coverable dim is ABSENT, not passed. — **Re-run trigger:** any caliper reading (nozzle OD, lug span, thread OD, O-ring OD, barb OD, window width) -> re-run Tier-1 and the gate
2. Absolute scale not caliper-verified (CHK-SCALE flag at intake; units assumed mm, scale 1.0). — **Re-run trigger:** one caliper reading of any dimension
3. scan_resolution = full by agent inference (DECISIONS OTHER: 600,142 faces, mean edge 0.152 mm), not owner-confirmed. The gate is labelled OFFICIAL (full-res) on that inference. — **Re-run trigger:** owner confirms the scan is the original export; if it is decimated, re-label INSPECTION ONLY and re-grade on the original
4. Bore interiors (nozzle, outlet, barb) and all internal passages are unscanned/bridged; named mask M1 removes them (scan->CAD 0.77 %, CAD->scan 2.40 %). Masked and unmasked numbers are both quoted in gate.json; the CAD bore floors are placed at the scanner bridge, not at a design depth. — **Re-run trigger:** a sectioned part, CT scan or depth-gauge reading of the three bores
5. Assembly scanned as one closed shell: sub-part poses kept as scanned (nozzle 1.3 deg, cap part 3.4 deg tilt), O-ring fused into the single solid, thread modelled as a plain cylinder (MODELING_PLAN §4, §6). — **Re-run trigger:** owner asks for a nominal (coaxial) design, separate parts or a real thread
6. Observability ray test (observability.py) counts CAD surfaces inside open-mouthed bores, windows and slits as observable although no scan covers them (unobservable fraction only 0.20 %); the gated cad_to_scan_observable therefore contains the unscanned nozzle bore floor (max 3.007). QA's run-local composition observable AND NOT (M1, M2) is in qa/residual_analysis.json (p95 0.215 / max 0.995, still over band because of the window/slit over-cuts). — **Re-run trigger:** a scan-coverage-aware observability test (or mask composition in deviation_gate/verdict) -> re-run the gate
7. Datum audit (report-only) agrees with alignment.json within 0.018 deg / 0.007 mm; but the as-built origin is the nozzle axis at its measured mid-station projected along the band normal, while the literal 'nozzle axis ∩ band plane' along the 1.16-1.27 deg tilted axis lies 0.37 mm away (qa/datum_supplement.json). No effect on deviation (ICP delta 0.045 deg / 0.015 mm). — **Re-run trigger:** owner states which origin definition downstream users need

## Claim boundary

Outer-envelope reconstruction of a scanned assembly (one fused solid, sub-parts as scanned). Not a functional flow part (internal passages, valve seat, spring not modelled), not caliper-verified in scale or any dimension, bore depths are scanner-bridge depths, thread is a plain cylinder. Not fit for tooling, moulding, fits or thread engagement until calipered; fit for visual/envelope/packaging use only, and only after the listed misses are fixed or accepted.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
