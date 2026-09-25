# VERDICT: REVISE

Regime: **baseline-skill** (baseline/skills/stl2step-build123d/SKILL.md:87); bands {'p95_mm': 0.3, 'max_mm': 0.8, 'tier1_abs_mm': None, 'interface_max_mm': None}.
Independence: fresh agent (CHK-INDEP verifier) that did not build the model; stl-re-verify scripts plus QA-own probes in qa/qa_scripts/; BUILDER_REPORT.md, build_log.txt, measure/params.json not read; model.py only grepped for CHK-PATCHWORK. MODELING_PLAN.md (an allowed input) quotes builder self-check numbers; none were used.

Scan: `input/scan.stl` (full-res), label **OFFICIAL (full-res)**.

## Gate table

| Gate | Band | Measured | Result |
|---|---|---|---|
| Hash freeze | unchanged | unchanged | PASS |
| Validity `OD-S03_steam-knob_datum.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 11657.117 mm³ | PASS |
| Validity `OD-S03_steam-knob.step` | 1 valid closed solid | solids 1, valid True, naked edges 0, V 11657.117 mm³ | PASS |
| Datum audit (report-only) | ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) | 3.875° / origin 0.021 mm / points p95 1.632 max 1.863 mm | outside (not blocking) |
| Registration (ICP) | converged | 44/60 its, 0.073° / 0.022 mm | PASS |
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | n 182580 · rms 0.090 · p50 0.026 · p95 0.150 · p99 0.278 · max 2.348 | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | n 19951 · rms 0.269 · p50 0.035 · p95 0.450 · p99 1.428 · max 2.796 | FAIL |
| zone:Z1 threaded sleeve OD:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 13841 · rms 0.085 · p50 0.055 · p95 0.185 · p99 0.245 · max 0.288 | PASS |
| zone:Z1 threaded sleeve OD:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 18986 · rms 0.117 · p50 0.052 · p95 0.200 · p99 0.577 · max 0.893 | FAIL |
| zone:Z2 sleeve bore visible:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 1701 · rms 0.085 · p50 0.051 · p95 0.166 · p99 0.247 · max 0.370 | PASS |
| zone:Z2 sleeve bore visible:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 2935 · rms 0.094 · p50 0.053 · p95 0.167 · p99 0.356 · max 0.514 | PASS |
| zone:Z3 stem ribs and core:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 26608 · rms 0.078 · p50 0.045 · p95 0.158 · p99 0.240 · max 0.516 | PASS |
| zone:Z3 stem ribs and core:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 38218 · rms 0.097 · p50 0.052 · p95 0.213 · p99 0.317 · max 0.469 | PASS |
| zone:Z4 crown cap wall lever:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 105817 · rms 0.089 · p50 0.018 · p95 0.110 · p99 0.225 · max 2.348 | FAIL |
| zone:Z4 crown cap wall lever:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 135130 · rms 0.049 · p50 0.019 · p95 0.103 · p99 0.179 · max 0.390 | PASS |
| zone:Z5 step face and collar:scan_to_cad | p95 ≤0.3 / max ≤0.8 | n 21231 · rms 0.081 · p50 0.030 · p95 0.141 · p99 0.379 · max 0.724 | PASS |
| zone:Z5 step face and collar:cad_to_scan | p95 ≤0.3 / max ≤0.8 | n 35472 · rms 0.069 · p50 0.031 · p95 0.139 · p99 0.287 · max 0.453 | PASS |

## Deviation detail (masked and unmasked side by side)

- scan→CAD unmasked: n 182580 · rms 0.090 · p50 0.026 · p95 0.150 · p99 0.278 · max 2.348
- scan→CAD masked: n 182580 · rms 0.090 · p50 0.026 · p95 0.150 · p99 0.278 · max 2.348
- CAD→scan unmasked: n 300000 · rms 0.268 · p50 0.035 · p95 0.480 · p99 1.397 · max 2.990
- CAD→scan masked: n 251986 · rms 0.076 · p50 0.028 · p95 0.156 · p99 0.289 · max 0.893
- CAD→scan observable only: n 19951 · rms 0.269 · p50 0.035 · p95 0.450 · p99 1.428 · max 2.796; unobservable fraction 0.24 %

Masks:

- **M1 open boundary** (cad_to_scan): CAD->scan distance measured to the EDGE of a scan hole (17 chrome-reflection holes, unscanned pocket floor, crevice floor, deep bore) is a coverage gap, not a surface deviation; fraction 15.67 %; inside n 47020 · rms 0.651 · p50 0.234 · p95 1.519 · p99 2.218 · max 2.990
- **M2 skin normal** (cad_to_scan): a CAD point whose nearest scan point faces >70 deg away is corresponding to a different (occluded/opposite) wall, not an outer-skin deviation; fraction 0.84 %; inside n 2524 · rms 0.494 · p50 0.405 · p95 0.865 · p99 1.206 · max 1.544

Zones:

- Z1 threaded sleeve OD [whole] scan_to_cad: unmasked n 13841 · rms 0.085 · p50 0.055 · p95 0.185 · p99 0.245 · max 0.288 | masked n 13841 · rms 0.085 · p50 0.055 · p95 0.185 · p99 0.245 · max 0.288
- Z1 threaded sleeve OD [whole] cad_to_scan: unmasked n 19594 · rms 0.128 · p50 0.054 · p95 0.229 · p99 0.590 · max 0.893 | masked n 18986 · rms 0.117 · p50 0.052 · p95 0.200 · p99 0.577 · max 0.893
- Z2 sleeve bore visible [whole] scan_to_cad: unmasked n 1701 · rms 0.085 · p50 0.051 · p95 0.166 · p99 0.247 · max 0.370 | masked n 1701 · rms 0.085 · p50 0.051 · p95 0.166 · p99 0.247 · max 0.370
- Z2 sleeve bore visible [whole] cad_to_scan: unmasked n 4095 · rms 0.104 · p50 0.060 · p95 0.208 · p99 0.330 · max 0.514 | masked n 2935 · rms 0.094 · p50 0.053 · p95 0.167 · p99 0.356 · max 0.514
- Z3 stem ribs and core [whole] scan_to_cad: unmasked n 26608 · rms 0.078 · p50 0.045 · p95 0.158 · p99 0.240 · max 0.516 | masked n 26608 · rms 0.078 · p50 0.045 · p95 0.158 · p99 0.240 · max 0.516
- Z3 stem ribs and core [whole] cad_to_scan: unmasked n 43475 · rms 0.177 · p50 0.060 · p95 0.432 · p99 0.694 · max 0.953 | masked n 38218 · rms 0.097 · p50 0.052 · p95 0.213 · p99 0.317 · max 0.469
- Z4 crown cap wall lever [whole] scan_to_cad: unmasked n 105817 · rms 0.089 · p50 0.018 · p95 0.110 · p99 0.225 · max 2.348 | masked n 105817 · rms 0.089 · p50 0.018 · p95 0.110 · p99 0.225 · max 2.348
- Z4 crown cap wall lever [whole] cad_to_scan: unmasked n 158696 · rms 0.283 · p50 0.024 · p95 0.522 · p99 1.495 · max 2.782 | masked n 135130 · rms 0.049 · p50 0.019 · p95 0.103 · p99 0.179 · max 0.390
- Z5 step face and collar [whole] scan_to_cad: unmasked n 21231 · rms 0.081 · p50 0.030 · p95 0.141 · p99 0.379 · max 0.724 | masked n 21231 · rms 0.081 · p50 0.030 · p95 0.141 · p99 0.379 · max 0.724
- Z5 step face and collar [whole] cad_to_scan: unmasked n 39217 · rms 0.090 · p50 0.034 · p95 0.192 · p99 0.371 · max 0.566 | masked n 35472 · rms 0.069 · p50 0.031 · p95 0.139 · p99 0.287 · max 0.453
- I1 lever pocket floor [interior] scan_to_cad: unmasked n 2493 · rms 0.123 · p50 0.031 · p95 0.306 · p99 0.522 · max 0.675 | masked n 2493 · rms 0.123 · p50 0.031 · p95 0.306 · p99 0.522 · max 0.675
- I1 lever pocket floor [interior] cad_to_scan: unmasked n 9053 · rms 0.925 · p50 0.292 · p95 2.012 · p99 2.435 · max 2.782 | masked n 2891 · rms 0.050 · p50 0.026 · p95 0.103 · p99 0.171 · max 0.259
- I2 stem collar crevice [interior] scan_to_cad: unmasked n 6380 · rms 0.188 · p50 0.077 · p95 0.411 · p99 0.640 · max 1.095 | masked n 6380 · rms 0.188 · p50 0.077 · p95 0.411 · p99 0.640 · max 1.095
- I2 stem collar crevice [interior] cad_to_scan: unmasked n 28294 · rms 0.292 · p50 0.122 · p95 0.657 · p99 0.807 · max 1.138 | masked n 13451 · rms 0.131 · p50 0.062 · p95 0.299 · p99 0.388 · max 0.693
- I3 bore below visible depth [interior] scan_to_cad: unmasked n 270 · rms 0.166 · p50 0.119 · p95 0.332 · p99 0.393 · max 0.598 | masked n 270 · rms 0.166 · p50 0.119 · p95 0.332 · p99 0.393 · max 0.598
- I3 bore below visible depth [interior] cad_to_scan: unmasked n 3873 · rms 1.164 · p50 0.769 · p95 2.301 · p99 2.737 · max 2.990 | masked n 10 · rms 0.117 · p50 0.098 · p95 0.163 · p99 0.168 · max 0.170
- B z 0-5 [region] scan_to_cad: unmasked n 59604 · rms 0.052 · p50 0.016 · p95 0.106 · p99 0.229 · max 0.393 | masked n 59604 · rms 0.052 · p50 0.016 · p95 0.106 · p99 0.229 · max 0.393
- B z 0-5 [region] cad_to_scan: unmasked n 80527 · rms 0.213 · p50 0.021 · p95 0.380 · p99 1.117 · max 2.120 | masked n 67609 · rms 0.052 · p50 0.017 · p95 0.105 · p99 0.231 · max 0.390
- B z 5-13.2 [region] scan_to_cad: unmasked n 46213 · rms 0.121 · p50 0.021 · p95 0.117 · p99 0.201 · max 2.348 | masked n 46213 · rms 0.121 · p50 0.021 · p95 0.117 · p99 0.201 · max 2.348
- B z 5-13.2 [region] cad_to_scan: unmasked n 78169 · rms 0.341 · p50 0.027 · p95 0.751 · p99 1.759 · max 2.782 | masked n 67521 · rms 0.045 · p50 0.023 · p95 0.101 · p99 0.152 · max 0.259
- B z 13.2-17 [region] scan_to_cad: unmasked n 27419 · rms 0.107 · p50 0.035 · p95 0.228 · p99 0.458 · max 1.095 | masked n 27419 · rms 0.107 · p50 0.035 · p95 0.228 · p99 0.458 · max 1.095
- B z 13.2-17 [region] cad_to_scan: unmasked n 57976 · rms 0.179 · p50 0.045 · p95 0.449 · p99 0.724 · max 1.138 | masked n 45809 · rms 0.077 · p50 0.034 · p95 0.159 · p99 0.295 · max 0.693
- B z 17-29.5 [region] scan_to_cad: unmasked n 27507 · rms 0.073 · p50 0.044 · p95 0.149 · p99 0.214 · max 0.335 | masked n 27507 · rms 0.073 · p50 0.044 · p95 0.149 · p99 0.214 · max 0.335
- B z 17-29.5 [region] cad_to_scan: unmasked n 46815 · rms 0.154 · p50 0.059 · p95 0.331 · p99 0.637 · max 0.953 | masked n 40927 · rms 0.101 · p50 0.053 · p95 0.227 · p99 0.328 · max 0.469
- B z 29.5-32.2 neck [region] scan_to_cad: unmasked n 4363 · rms 0.105 · p50 0.051 · p95 0.221 · p99 0.274 · max 0.467 | masked n 4363 · rms 0.105 · p50 0.051 · p95 0.221 · p99 0.274 · max 0.467
- B z 29.5-32.2 neck [region] cad_to_scan: unmasked n 6222 · rms 0.116 · p50 0.056 · p95 0.238 · p99 0.374 · max 0.533 | masked n 5703 · rms 0.116 · p50 0.055 · p95 0.239 · p99 0.384 · max 0.533
- B z 32.2-38.4 sleeve [region] scan_to_cad: unmasked n 17474 · rms 0.089 · p50 0.057 · p95 0.190 · p99 0.250 · max 0.598 | masked n 17474 · rms 0.089 · p50 0.057 · p95 0.190 · p99 0.250 · max 0.598
- B z 32.2-38.4 sleeve [region] cad_to_scan: unmasked n 30291 · rms 0.434 · p50 0.065 · p95 1.019 · p99 2.092 · max 2.990 | masked n 24417 · rms 0.123 · p50 0.055 · p95 0.222 · p99 0.550 · max 0.893

Over-band scan→CAD points (> 0.8 mm): 231 (0.127 %) in 2 clusters ≥ 20 pts.

- cluster 0: n 206, centroid [-2.715, 10.983, 9.338], r [10.633, 12.064], θ [99.6, 108.9], max 2.348 — SCAN ARTEFACT (scan wrong, CAD right). 206 scan pts, r 10.6-12.1, z 6.9-11.0, theta 100-109, d up to 2.35 mm: a curled skin flap hanging 1-2 mm inside the cap wall at the edge of intake hole B (chrome reflection). Every point lies <=0.75 mm from a scan open boundary (qa/cluster_probe.json); overlay theta=104 and Z=9.3 show the flap detached from the wall; photos 1,2,4,5 show an intact smooth cap wall. Not modelled; not maskable after the fact.
- cluster 1: n 25, centroid [2.841, -4.753, 15.174], r [5.247, 5.883], θ [295.1, 307.7], max 1.095 — REAL SCAN GEOMETRY the CAD lacks (CAD approximation). 25 scan pts, r 5.25-5.9, z 14.9-15.4, theta 295-308, d up to 1.10 mm: at theta ~300 the stem wall is seen continuing down to z~15 inside the collar/stem crevice, deeper than the CAD's axisymmetric inner-groove arc (bottom ~16.0); at theta 45/104/120 the scan groove matches the CAD (overlay theta panels). The as-assembled crevice is non-axisymmetric; photos 4/5 show only a dark gap (depth not resolvable). Points lie <=0.55 mm from a scan open boundary (crevice floor partly unscanned).

## Checks

| Check | Result | Note |
|---|---|---|
| CHK-MASK | finding | zone Z3 stem ribs and core cad_to_scan; zone Z4 crown cap wall lever cad_to_scan |
| CHK-CLUSTER | pass | 2 scan->CAD over-band clusters; unexplained: [] |
| CHK-OVERLAY | pass | every panel shows scan |
| CHK-CIRCULAR | pass | graded after QA's own ICP (44/60 its, converged); T_refine not written back; no expected value from params.json or the builder; datum audited on the raw scan |
| CHK-LIKE4LIKE | n/a | iteration 1; no _itN_SUPERSEDED to compare |
| CHK-INDEP | pass | fresh verifier context, own ICP and scripts |
| CHK-FILLET | pass | export_check.json: 4 fillet ops (F04 x2, F06, F07), target == used, all OK |
| CHK-PATCHWORK | finding | census 88 faces, analytic area 97.5% (QA), 10 B-spline faces (1.4%) only on the two helical sleeve ramps (plan-declared helicoids); no loft/ruled/polyline/slice in model.py (grep). FINDING: QA 0.005 mm tessellation is NOT watertight in either frame (3 / 12 non-manifold edges, 0 open) at z 15.99, r 6.42, theta 175-182 deg: the 180 deg rib foot touches the inner-groove torus along a line (self-contact). B-rep edge-face multiplicity is clean, BRepCheck valid; step_check.py does not fold tessellation watertightness into single_valid_closed_solid (skill defect). SKILL §3 counts a non-watertight fine tessellation as a validity failure -> REVISE. Evidence qa/tess_probe.json |
| CHK-ENUM | finding | E01-E19 present in CAD and consistent with photos 1-5 and overlays; E20 bore notch at theta~180 (z 36-37, visible in overlay Z=36.5) not modelled (plan-declared). No hallucinated feature except assumed closures (bore floor disc z~34.7, lever pocket floor z~8.5) which are CAD->scan clusters 0/1 with no scan behind them. Scan->CAD cluster 1 (crevice, theta ~300) is real scan material the CAD lacks. |
| CHK-ACHIEVABLE | n/a | no Tier-1 dims (scan-only) |
| PHOTO-PLAUSIBILITY | pass | photos 1-5 walked: chrome cap with one lever and through-slot pocket (2,4,5), two chrome rings, white 4-rib stem, neck, chrome threaded sleeve, white splined bore (5). The cap wall is smooth and intact in every view (1,2,4,5): the inward scan flap at theta ~100-109 is not a real dent. |

## Misses, per region

- scan_to_cad:masked: p95 0.150 max 2.348 vs 0.3/0.8
- cad_to_scan_observable: p95 0.450 max 2.796 vs 0.3/0.8
- zone:Z1 threaded sleeve OD:cad_to_scan: p95 0.200 max 0.893 vs 0.3/0.8
- zone:Z4 crown cap wall lever:scan_to_cad: p95 0.110 max 2.348 vs 0.3/0.8
- **VALIDITY (geometry fail, drives REVISE)**: QA 0.005 mm tessellation non-watertight in both frames: 180 deg stem rib foot (z 15.99, r 6.42) meets the inner-groove torus along a line (self-contact), qa/tess_probe.json. BRepCheck valid, so step_check.py passes it; SKILL §3 does not. Options: geometry loop (--route geometry): lift the rib foot off the groove bottom by a clearance or bury it by OV so the contact becomes a volume overlap; re-export and re-verify.
- **whole part scan->CAD max 2.348 (band 0.8) / zone Z4 cap wall theta 100-109**: scan artefact: chrome skin flap at intake hole B (cluster 0); CAD matches the photos. Options: cannot be cleared by geometry. After the geometry fix expect BAND_NOT_MET and a recorded ACCEPT-BAND naming this miss; or rescan with matting spray; a scan-side mask would now be after-the-fact and is not added.
- **stem/collar crevice theta ~290-310, z 14.9-16.4 (scan->CAD cluster 1, max 1.10; Z3 CAD->scan max 0.953)**: non-axisymmetric as-assembled crevice modelled as one revolve groove; floor partly unscanned. Options: in the geometry loop, optionally deepen the inner groove locally where the scan sees wall to z~15 (would cost CAD->scan where the floor is shallow); or accept as declared simplification.
- **observable CAD->scan p95 0.450 / max 2.796; zones Z4 CAD->scan (pocket floor), Z1 CAD->scan max 0.893, Z3 CAD->scan**: CAD surfaces with no scan behind them: assumed lever-pocket floor (z~8.5), assumed bore floor disc (z~34.7), chrome holes A/B; the ray test counts them observable (L4). Sleeve Z1 CAD->scan max 0.893 is local at the helical ends/E20 notch. Options: not fixable without data (pocket/bore depth unobserved); declare after the geometry loop, or obtain calipers/depth readings for pocket floor and bore depth.

## Declared limitations (each with its re-run trigger)

1. Tier-1 not run: no calipers (owner, scan-only). Every dimension is ABSENT, not passed. — **Re-run trigger:** any caliper reading supplied -> re-run Tier-1 and this gate
2. Absolute scale not caliper-verified (CHK-SCALE FLAG at intake): units assumed mm, scale_factor 1.0. — **Re-run trigger:** one caliper reading on any feature (e.g. sleeve OD over crests or cap OD)
3. scan_resolution 'full' is an orchestrator inference (DECISIONS.md OTHER), not owner-confirmed. — **Re-run trigger:** owner states the scan is a decimated copy -> relabel INSPECTION ONLY
4. Observability ray test (OD-H22 defect #3) counts open-mouthed unscanned regions (lever pocket floor, bore floor, crevice floor) as observable: unobservable fraction only 0.24%, so the gated observable CAD->scan number is inflated. QA coverage proxy (qa/c2s_residual_probe.json, NOT the gate) puts CAD->scan outside scan-hole neighbourhoods at p95 0.160 / max 0.934. — **Re-run trigger:** observability.py fixed to treat unreached cavities as unobservable -> re-run deviation_gate.py
5. Datum audit clock differs 3.88 deg: datum_audit.py's Fourier clock is vertex-count weighted (same density bias intake documented); QA area-weighted Fourier and lever-flank bisector reproduce the builder clock within ~0.2 deg (qa/clock_crosscheck.json). Axis 0.02 deg, origin 0.02 mm. — **Re-run trigger:** datum_audit.py fourier clock made area-weighted -> re-run audit

## Claim boundary

Not a delivered result: REVISE (geometry validity). Even after the fix this is a scan-only reconstruction with unverified absolute scale, unobserved pocket floor / bore floor / crevice depth, and no Tier-1; not fit for manufacture or tooling of the spindle interface (sleeve thread form, bore splines) until calipered.

_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: BAND_NOT_MET, HALT, REVISE._
