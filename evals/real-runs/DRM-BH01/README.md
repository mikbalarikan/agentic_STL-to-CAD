# dreame_brushes_housing — STL → STEP reverse-engineering delivery

**Verdict: `BAND_NOT_MET`** (from `qa/gate.json`; full reasoning in `qa/VERDICT.md`).  
**Band regime:** baseline-skill — source `baseline/skills/stl2step-build123d/SKILL.md:87`.  
**Iteration:** 2 of 3 (earlier iterations kept: `_it1_SUPERSEDED/`).  
**Verification independence (CHK-INDEP):** pass — fresh subagent context, own QA runs; see independence  

> **A deviation band was NOT met.** Delivered only under the recorded human acceptance below (by owner (decision card), 2026-10-01, record `decisions/accept_band.md`).

## 1. The part

_No reference photo was supplied with the scan._

Dreame brush-roller housing scanned as a rigid assembly (two half-bore troughs, cover flange and labyrinth edge, gearbox end block with cover, drive motor can). Delivered as ONE fused solid of housing + gearbox block + motor envelope (owner decision); loose wires and screw heads are not modelled.

## 2. Deliverables

| file | frame | solids | valid | closed | faces | volume mm³ | bbox mm |
|---|---|---|---|---|---|---|---|
| `build/dreame_brushes_housing_datum.step` | datum | 1 | yes | yes | 1873 | 138726.0512 | max: [16.8452, 66.05, 206.26]; min: [-48.17, -31.26, -0.2314]; size: [65.0152, 97.31, 206.4914] |
| `build/dreame_brushes_housing.step` | scan | 1 | yes | yes | 1873 | 138726.0512 | max: [48.9622, 57.0096, -123.1834]; min: [-158.4371, -77.0629, -278.1578]; size: [207.3993, 134.0724, 154.9744] |

Source of the table: `build/export_check.json`. The editable design intent is `build/model.py` driven by `measure/params.json`.

## 3. Method

1. Intake: owner's decimated scan, largest body kept; datum = T1 trough bore axis (primary), gearbox end-face plane (origin), flange-top normal (clock); band regime baseline-skill declared before any gate.
2. Measure: per-station circle fits of both bores, flat-face medians of the constant cross-section, fitted line+arc sketch of the gearbox outline, motor can steps, drafted end planes, paired-plane rib slabs, and five region feature sets (R1-R5), each with its own measurement script and evidence.
3. Rebuild: build123d, constant section extruded per trough group on its measured axis line, region add/cut primitives (box, cylinder, few-vertex prism, exact diff); single solid exported in datum and scan frames.
4. Verify: independent fresh-context verifier, own ICP, two-way deviation with named masks, zones, clusters; iteration 1 REVISE (validity + band), iteration 2 valid geometry, band missed, owner accepted the miss (ACCEPT-BAND).

## 4. Coordinate frames

Two STEP files carry the same solid (SYNTHESIS D14): the **datum frame** (design frame, below) and the **scan frame** (the original STL coordinates; the CAD overlays the raw scan).

| element | definition | fit residual (rms / max mm) | why |
|---|---|---|---|
| origin | +Y trough axis ∩ gearbox end-wall outer face | — | — |
| primary (axis) | +Y trough inner bore (brush-roller half-bore, R~18.1), model x 85-125 mm, arc -100..-10 deg | 0.0128 / 0.0426 | the brush roller turns in this half-bore; its axis is the functional axis of the housing and the longest clean primitive on the part |
| secondary (plane) | +Y flange top face (cover mating face) normal -> +X | 0.0317 / 0.1676 | the flange top is the cover mating face; its normal defines 'up' (open side of the troughs) |
| clock | plane_normal: +Y flange top face (cover mating face) normal -> +X (angle 149.6495°) | — | — |

Measured tilt: —° (not measured). Scale factor applied: 1. Scan noise floor: 0.0366 mm (rms of RANSAC+SVD plane on +Y flange underside face (1736 faces)).

Scan → datum matrix (row-major, `intake/alignment.json#matrix_4x4`); the scan-frame STEP uses its inverse:

```
 0.482664  -0.437156   0.758900   166.338333
 0.024163  -0.859540  -0.510497  -89.298861
 0.875472   0.264735  -0.404306   66.508613
 0.000000   0.000000   0.000000   1.000000
```

## 5. Parameters

Sources: scan 42 (total 42). Rendered from `measure/params.json`; never edited by hand.

| name | value | unit | measured | rule | source | ± mm | critical | evidence |
|---|---|---|---|---|---|---|---|---|
| `corner_mY_r` | 7.5417 | mm | 7.5417 | keep-measured | scan | 0.4329 | no | measure/figures/m11_corners.json |
| `corner_pY_r` | 9.81 | mm | 9.8124 | round-within-noise | scan | 0.0255 | no | measure/figures/m11_corners.json |
| `end_inner_plane` | [203.608, 0.1238] | mm | [203.608, 0.1238] | keep-measured | scan | 0.2179 | no | measure/figures/m10_details.json |
| `end_outer_plane` | [205.3547, 0.0975] | mm | [205.3547, 0.0975] | keep-measured | scan | 0.3298 | no | measure/figures/m10_details.json |
| `endface_plane` | [0.0712, -0.0004, 0.0067] | mm | [0.0712, -0.0004, 0.0067] | keep-measured | scan | 0.0538 | no | measure/figures/m09_endface.json |
| `motor_cy` | -34.59 | mm | [-34.596, -34.594, -34.594, -34.59, -34.575, -34.558] | mean-of-n | scan | 0.03 | no | measure/figures/m06_motor.json |
| `motor_cz` | -33.44 | mm | [-33.413, -33.428, -33.447, -33.46, -33.459, -33.456] | mean-of-n | scan | 0.03 | no | measure/figures/m06_motor.json |
| `my_bot` | -0.52 | mm | -0.677..-0.162 | round-within-noise | scan | 0.2576 | no | measure/figures/m03_profile.json |
| `my_chan_y_in` | -53.4 | mm | -53.4 | keep-measured | scan | 0.15 | no | measure/figures/section_x110_minusY.png |
| `my_chan_y_out` | -54.45 | mm | -54.45 | keep-measured | scan | 0.15 | no | measure/figures/section_x110_minusY.png |
| `my_chan_z` | 0.4 | mm | 0.4 | keep-measured | scan | 0.15 | no | measure/figures/section_x110_minusY.png |
| `my_hook_end` | -60.71 | mm | -60.939..-60.565 | round-within-noise | scan | 0.1867 | no | measure/figures/m03_profile.json |
| `my_hook_knee_y` | -58.5 | mm | -58.5 | keep-measured | scan | 0.15 | no | measure/figures/section_x110_minusY.png |
| `my_hook_top` | 7.28 | mm | 7.062..7.603 | round-within-noise | scan | 0.2703 | no | measure/figures/m03_profile.json |
| `my_hook_under` | 5.73 | mm | 5.525..6.053 | round-within-noise | scan | 0.2642 | no | measure/figures/m03_profile.json |
| `my_rim_in` | -51.67 | mm | -51.836..-51.609 | round-within-noise | scan | 0.1134 | no | measure/figures/m03_profile.json |
| `my_rim_top` | 1.43 | mm | 1.277..1.702 | round-within-noise | scan | 0.2124 | no | measure/figures/m03_profile.json |
| `my_step_z` | 1.57 | mm | 1.396..1.819 | round-within-noise | scan | 0.2115 | no | measure/figures/m03_profile.json |
| `my_up_in` | -55.81 | mm | -55.996..-55.672 | round-within-noise | scan | 0.1622 | no | measure/figures/m03_profile.json |
| `my_up_out` | -57.99 | mm | -58.193..-57.834 | round-within-noise | scan | 0.1793 | no | measure/figures/m03_profile.json |
| `my_up_top` | 8.69 | mm | 8.461..8.964 | round-within-noise | scan | 0.2515 | no | measure/figures/m03_profile.json |
| `my_up_top_y` | -56.7 | mm | -56.7 | keep-measured | scan | 0.15 | no | measure/figures/section_x110_minusY.png |
| `py_lip_bot` | -5.19 | mm | -5.249..-5.129 | round-within-noise | scan | 0.0599 | no | measure/figures/m03_profile.json |
| `py_lip_in` | 26.3 | mm | 26.202..26.430 | round-within-noise | scan | 0.1138 | no | measure/figures/m03_profile.json |
| `py_lip_out` | 27.78 | mm | 27.703..27.894 | round-within-noise | scan | 0.0955 | no | measure/figures/m03_profile.json |
| `py_top` | -0.16 | mm | -0.239..-0.063 | round-within-noise | scan | 0.0883 | no | measure/figures/m03_profile.json |
| `py_under` | -2.22 | mm | -2.332..-2.122 | round-within-noise | scan | 0.1048 | no | measure/figures/m03_profile.json |
| `rec_slope` | 0.1325 | mm | 0.1325 | keep-measured | scan | 0 | no | measure/figures/m04_recess.json |
| `rec_y0` | -22.1793 | mm | -22.1793 | keep-measured | scan | 0.15 | no | measure/figures/m04_recess.json |
| `ridge_top_z` | -7.88 | mm | -7.908..-7.707 | round-within-noise | scan | 0.1008 | no | measure/figures/m03_profile.json |
| `t1_line` | [0.0216, 0.0913, -0.0023, -0.0015] | mm | [0.0216, 0.0913, -0.0023, -0.0015] | keep-measured | scan | 0.1113 | no | measure/figures/m07_axislines.json |
| `t1_rec_ri` | 19.21 | mm | [19.109, 19.156, 19.182, 19.207, 19.226, 19.228, 19.235, 19.222, 19.205, 19.171] | round-within-noise | scan | 0.0377 | no | measure/figures/m04_recess.json |
| `t1_rec_ro` | 21.28 | mm | [21.123, 21.192, 21.257, 21.271, 21.292, 21.298, 21.292, 21.28, 21.268, 21.326] | round-within-noise | scan | 0.0563 | no | measure/figures/m04_recess.json |
| `t1_ri` | 18.14 | mm | [18.124, 18.126, 18.11, 18.1, 18.118, 18.148, 18.112, 18.137, 18.168, 18.209, 18.148] | round-within-noise | scan | 0.0298 | yes | measure/figures/m01_troughs.json, m02_t2.json |
| `t1_ro` | 20.17 | mm | [20.358, 20.319, 20.016, 20.162, 20.256, 20.146, 20.13, 20.101, 20.159, 20.032] | round-within-noise | scan | 0.1071 | no | measure/figures/m01_troughs.json, m02_t2.json |
| `t2_cy` | -34.53 | mm | -34.5279 | round-within-noise | scan | 0.125 | no | measure/figures/m07_axislines.json |
| `t2_cz` | 0.82 | mm | 0.8206 | round-within-noise | scan | 0.125 | no | measure/figures/m07_axislines.json |
| `t2_line` | [0.0021, 0.0006, -0.0039, -0.0035] | mm | [0.0021, 0.0006, -0.0039, -0.0035] | keep-measured | scan | 0.125 | no | measure/figures/m07_axislines.json |
| `t2_ri` | 17.3 | mm | [17.31, 17.275, 17.302, 17.314, 17.318, 17.304, 17.308, 17.299, 17.292, 17.278, 17.279, 17.288, 17.272] | round-within-noise | scan | 0.0151 | yes | measure/figures/m01_troughs.json, m02_t2.json |
| `t2_ro` | 19.38 | mm | [19.178, 19.333, 19.476, 19.451, 19.412, 19.344, 19.431, 19.444] | round-within-noise | scan | 0.091 | no | measure/figures/m01_troughs.json, m02_t2.json |
| `window` | [165.4154, 200.6253, -23.7083, 9.7425, 1.5] | mm | [165.4154, 200.6253, -23.7083, 9.7425, 1.5] | keep-measured | scan | 0.15 | no | measure/figures/m10_details.json |
| `x0` | 13.112 | mm | 13.112 | keep-measured | scan | 0.1 | no | measure/figures/slabs_all.json; R2_planes.json |

## 6. Model tree (design intent)

The STEP is a neutral B-Rep; it carries no feature history. The editable design intent is `build/model.py` driven by `measure/params.json`, and the ordered feature plan is `build/MODELING_PLAN.md`.

_No `feature_tree` was declared in `deliver/limitations.json`; see `build/MODELING_PLAN.md` for the ordered feature plan._

## 7. Tier-1 — caliper dims re-measured on the STEP

**Tier-1 not run: no caliper dimensions exist.** Every dimension is scan authority (or operator spec); see the source column in §5. Absent is not passed.

## 8. Deviation gate (scan ↔ CAD)

Regime **baseline-skill** (`baseline/skills/stl2step-build123d/SKILL.md:87`); bands: p95_mm: 0.3; max_mm: 0.8; tier1_abs_mm: —; interface_max_mm: —.

Registration: point-to-point ICP, CAD samples -> scan samples, masked correspondences (B02 q20_tier2.py), iterations 48/60, converged yes, correction 0.0526° / 0.1564 mm.  
Unobservable CAD fraction: 0.0606.

| direction | n | rms | p50 | p95 | p99 | max | sampling | source |
|---|---|---|---|---|---|---|---|---|
| scan → CAD **unmasked** | 196686 | 0.7034 | 0.1164 | 1.2842 | 3.0255 | 11.1459 | — | `qa/gate.json#deviation` |
| scan → CAD (masked) | 191655 | 0.573 | 0.1141 | 1.1613 | 2.6405 | 5.9652 | — | `qa/gate.json#deviation` |
| CAD → scan **unmasked** (all) | 300000 | 0.8395 | 0.1001 | 1.9036 | 4.1337 | 7.8945 | — | `qa/gate.json#deviation` |
| CAD → scan (masked) | 273270 | 0.7527 | 0.093 | 1.5497 | 3.7611 | 7.8945 | — | `qa/gate.json#deviation` |
| CAD → scan (observable) | 18788 | 0.5909 | 0.093 | 1.0039 | 2.9364 | 7.6934 | — | `qa/gate.json#deviation` |

### Gate results (what the verdict was graded on)

| item | band | measured | result |
|---|---|---|---|
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | p95 1.1613 max 5.9652 (n 191655) | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | p95 1.0039 max 7.6934 (n 18788) | FAIL |

### Per zone (unmasked and masked side by side)

| zone | kind | direction | unmasked | masked | unmasked stats | masked stats | note |
|---|---|---|---|---|---|---|---|
| T1 bore wall | functional_interface | scan_to_cad | reported | reported | n 35294 · p95 0.6888 · max 2.8174 | n 35294 · p95 0.6888 · max 2.8174 | brush roller 1 half-bore, inner+outer wall incl. offset strip |
| T1 bore wall | functional_interface | cad_to_scan | reported | reported | n 57898 · p95 0.3841 · max 3.7413 | n 56590 · p95 0.3735 · max 3.7413 | brush roller 1 half-bore, inner+outer wall incl. offset strip |
| T2 bore wall | functional_interface | scan_to_cad | reported | reported | n 34751 · p95 0.6356 · max 4.6685 | n 34751 · p95 0.6356 · max 4.6685 | brush roller 2 half-bore wall |
| T2 bore wall | functional_interface | cad_to_scan | reported | reported | n 70015 · p95 2.0708 · max 7.2027 | n 64784 · p95 1.9973 · max 7.2027 | brush roller 2 half-bore wall |
| flange top cover mating | functional_interface | scan_to_cad | reported | reported | n 2805 · p95 0.226 · max 1.8289 | n 2805 · p95 0.226 · max 1.8289 | +Y (model) flange top = cover mating face |
| flange top cover mating | functional_interface | cad_to_scan | reported | reported | n 5828 · p95 0.2212 · max 3.6229 | n 5788 · p95 0.2216 · max 3.6229 | +Y (model) flange top = cover mating face |
| gearbox block interior | interior | scan_to_cad | reported | reported | n 8480 · p95 1.8817 · max 4.107 | n 6903 · p95 1.6581 · max 3.7913 | inside the gearbox outline, behind the cover: scanned inter-part surfaces; reported only |
| gearbox block interior | interior | cad_to_scan | reported | reported | n 13616 · p95 3.1535 · max 7.8945 | n 9241 · p95 3.1288 · max 7.8945 | inside the gearbox outline, behind the cover: scanned inter-part surfaces; reported only |
| gearbox end face | functional_interface | scan_to_cad | reported | reported | n 1861 · p95 0.2636 · max 0.7598 | n 1601 · p95 0.1113 · max 0.6264 | mounting face |
| gearbox end face | functional_interface | cad_to_scan | reported | reported | n 10647 · p95 0.5739 · max 4.2942 | n 9505 · p95 0.4293 · max 4.2942 | mounting face |
| labyrinth edge | functional_interface | scan_to_cad | reported | reported | n 37645 · p95 1.9021 · max 11.1459 | n 36939 · p95 1.4796 · max 4.7379 | -Y (model) labyrinth edge, lid sealing |
| labyrinth edge | functional_interface | cad_to_scan | reported | reported | n 49614 · p95 1.2418 · max 7.0955 | n 45759 · p95 1.1106 · max 7.0955 | -Y (model) labyrinth edge, lid sealing |
| motor can region | functional_interface | scan_to_cad | reported | reported | n 18678 · p95 1.5228 · max 4.8127 | n 17768 · p95 1.3726 · max 4.8127 | motor can envelope (assembly part, owner-fused) |
| motor can region | functional_interface | cad_to_scan | reported | reported | n 22666 · p95 3.6766 · max 6.8972 | n 17918 · p95 2.3615 · max 6.6604 | motor can envelope (assembly part, owner-fused) |
| zband gearbox z-1_13 | region | scan_to_cad | reported | reported | n 19840 · p95 1.4402 · max 4.107 | n 16425 · p95 1.1926 · max 3.7913 | — |
| zband gearbox z-1_13 | region | cad_to_scan | reported | reported | n 37427 · p95 2.5052 · max 7.8945 | n 29820 · p95 2.3863 · max 7.8945 | — |
| zband mid z66_150 | region | scan_to_cad | reported | reported | n 56584 · p95 0.5965 · max 5.9652 | n 56584 · p95 0.5965 · max 5.9652 | — |
| zband mid z66_150 | region | cad_to_scan | reported | reported | n 93603 · p95 0.2693 · max 2.7291 | n 90126 · p95 0.222 · max 2.6454 | — |
| zband motor_troughstart z13_66 | region | scan_to_cad | reported | reported | n 62294 · p95 1.3267 · max 11.1459 | n 60678 · p95 1.0632 · max 4.8127 | — |
| zband motor_troughstart z13_66 | region | cad_to_scan | reported | reported | n 98662 · p95 1.9384 · max 7.6783 | n 88151 · p95 1.5009 · max 7.6783 | — |
| zband plusX_end z150_up | region | scan_to_cad | reported | reported | n 57968 · p95 1.8071 · max 4.7379 | n 57968 · p95 1.8071 · max 4.7379 | — |
| zband plusX_end z150_up | region | cad_to_scan | reported | reported | n 70308 · p95 2.9058 · max 7.2027 | n 65173 · p95 2.6381 · max 7.2027 | — |

### Masks (masked and unmasked are both shown above)

| mask | direction | why | fraction removed | stats inside |
|---|---|---|---|---|
| M1 loose motor wires F11 | scan_to_cad | loose, non-rigid motor wires; declared not modelled at intake | 0.0082 | n: 1616; rms: 4.4048; mean: 3.1463; p50: 2.2317; p95: 9.0772; p99: 10.1633; max: 11.1459 |
| M2 gearbox cover screw heads | scan_to_cad | COTS screw heads in the 4 gearbox-cover sockets; screw-head detail declared not modelled | 0.0174 | n: 3415; rms: 0.9431; mean: 0.6214; p50: 0.3278; p95: 2.0766; p99: 3.3396; max: 4.107 |
| M2 gearbox cover screw heads | cad_to_scan | COTS screw heads in the 4 gearbox-cover sockets; screw-head detail declared not modelled | 0.0129 | n: 3873; rms: 0.7292; mean: 0.3483; p50: 0.1367; p95: 1.1111; p99: 3.9866; max: 4.8919 |
| M3 open boundary | cad_to_scan | distance from CAD to a scan hole EDGE is not a surface deviation (scan has 192 open loops) | 0.0779 | n: 23356; rms: 1.5441; mean: 0.9664; p50: 0.4914; p95: 3.6375; p99: 5.6059; max: 7.1635 |

### Mask sensitivity

| band | direction | stats | variant |
|---|---|---|---|
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 0.9473; max_over_by: 10.3459 | scan_to_cad | n: 193271; rms: 0.6984; mean: 0.3069; p50: 0.1151; p95: 1.2473; p99: 3.0168; max: 11.1459 | all masks except M1 loose motor wires F11 |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 0.9; max_over_by: 5.1652 | scan_to_cad | n: 195070; rms: 0.5815; mean: 0.2889; p50: 0.1154; p95: 1.2; p99: 2.6624; max: 5.9652 | all masks except M2 gearbox cover screw heads |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.2321; max_over_by: 7.0945 | cad_to_scan | n: 276644; rms: 0.7503; mean: 0.2954; p50: 0.0934; p95: 1.5321; p99: 3.7594; max: 7.8945 | all masks except M2 gearbox cover screw heads |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.6092; max_over_by: 7.0945 | cad_to_scan | n: 296127; rms: 0.8408; mean: 0.3476; p50: 0.0996; p95: 1.9092; p99: 4.1391; max: 7.8945 | all masks except M3 open boundary |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.4275; max_over_by: 7.0945 | cad_to_scan | n: 292234; rms: 0.7919; mean: 0.3235; p50: 0.0979; p95: 1.7275; p99: 3.9264; max: 7.8945 | M3 open boundary radius 0.0 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.3597; max_over_by: 7.0945 | cad_to_scan | n: 287473; rms: 0.777; mean: 0.3124; p50: 0.0961; p95: 1.6597; p99: 3.8637; max: 7.8945 | M3 open boundary radius 0.2 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.2745; max_over_by: 7.0945 | cad_to_scan | n: 282030; rms: 0.7591; mean: 0.3015; p50: 0.0945; p95: 1.5745; p99: 3.7698; max: 7.8945 | M3 open boundary radius 0.4 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.2497; max_over_by: 7.0945 | cad_to_scan | n: 273270; rms: 0.7527; mean: 0.2959; p50: 0.093; p95: 1.5497; p99: 3.7611; max: 7.8945 | M3 open boundary radius 0.8 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.3105; max_over_by: 7.0945 | cad_to_scan | n: 253623; rms: 0.7628; mean: 0.2961; p50: 0.0913; p95: 1.6105; p99: 3.8423; max: 7.8945 | M3 open boundary radius 1.5 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.4728; max_over_by: 7.0945 | cad_to_scan | n: 213902; rms: 0.7866; mean: 0.2986; p50: 0.0879; p95: 1.7728; p99: 4.0311; max: 7.8945 | M3 open boundary radius 2.5 mm |

### Over-band point clusters, scan → CAD (> 0.8 mm)

18800 points (0.0956 fraction) in 119 clusters ≥ 20 pts.

| # | n | centroid | r range | θ range (deg) | d max | explanation |
|---|---|---|---|---|---|---|
| 0 | 1441 | [-10.035, 56.637, 163.87] | [51.559, 64.321] | [90.5, 110.6] | 3.8039 | REAL, NOT FIXED since it1 (it1 cluster 3; over-band pts in the same bbox 1443 -> 1433): -Y latch box at z 161-167, y 50-62 (overlay Z=165). Scan surface lies INSIDE the CAD (qa/inside_outside.json): the part is a hollow box, the CAD fills it solid. p50 1.78 / max 3.80 mm |
| 1 | 1403 | [-9.177, 39.938, 195.328] | [31.777, 51.015] | [88.5, 116.9] | 4.4561 | REAL, NOT FIXED since it1 (it1 cluster 4; 1390 -> 1401, max 4.43 -> 4.46) although MODELING_PLAN lists it as fixed: T2 rounded/ramped +X end, z 186-203 (overlays Z=187, Z=195, Z=200). The scan curve runs from about (-16,31) to (1,51); the CAD keeps a block/wedge outline. Scan material outside the CAD, p50 1.66 / max 4.46 |
| 2 | 1037 | [-41.201, 52.172, 45.815] | [62.582, 71.818] | [124.1, 131.7] | 11.1459 | ARTEFACT, declared not modelled: F11 loose motor wires (x -43..-39, y 47-59, z 41-60; organic loops in overlay x=-41). Inside mask M1. Unmasked whole-part max 11.15 comes from here; masked max is 5.97 |
| 3 | 844 | [-20.48, 38.793, 204.919] | [33.859, 54.121] | [104.7, 131.5] | 2.3074 | REAL, NOT FIXED since it1 (it1 cluster 6; 842 -> 837) although listed as fixed: +X end wall / latch area z 203.7-205.3, x -27..-12, y 30-48 (overlay Z=204.5). Scan end-wall area the CAD lacks (drafted end-wall position/extent). Outside the CAD, max 2.31 |
| 4 | 676 | [-25.586, 41.622, 64.193] | [38.355, 60.829] | [115.3, 129] | 5.0916 | REAL, NOT FIXED since it1 (it1 cluster 10; 498 -> 490, max 5.09) although 'motor end' is listed as fixed: scan material past the CAD motor end, z 61.8-69, x -38..-19, y 32-48 (overlay Z=64 shows scan arcs around the CAD end boss that the CAD lacks). Motor end bracket/bearing cap or wire exit; boss vs wires undecidable without photos. Outside the CAD, p50 1.83 / max 5.09 |
| 5 | 498 | [-43.757, 32.552, 64.127] | [46.766, 60.474] | [130, 149.1] | 5.9652 | REAL (present in it1 as a smaller cluster, 417 over -> 498): same motor-end structure on the far side, x -46..-38.6, y 24-46, z 61.8-67.9 (overlay Z=64). Outside the CAD, p50 1.94 / max 5.97 = the masked whole-part max. Just below the M1 wire box (y < 46), so it is NOT masked; motor end cap rim/bracket vs wire exit undecidable without photos |
| 6 | 432 | [-3.146, 35.826, 204.183] | [3.945, 47.308] | [91.3, 120] | 2.041 | REAL, partly improved (it1 bbox 818 -> 706): +X end, z 202.3-205.4, x -17.6..-0.8, y 3.6-47. Scan surface INSIDE the CAD by up to 2.04 mm: the CAD end wall/draft plane sits too far +z or is too thick on the open side (overlay Z=204.5) |
| 7 | 428 | [-21.058, 38.586, 170.217] | [39.922, 46.533] | [114.9, 122.4] | 4.5347 | REAL, unchanged (it1 427 -> 426): z 167-174.4, x -22.7..-18.8, y 34.5-41.2, outside the CAD, max 4.53. Overlay Z=170 shows a scan detail at about (-22,38) under the T2 +X end (rib/peg) that the CAD lacks |
| 8 | 424 | [-19.024, 0.426, 66.612] | [18.793, 19.319] | [173.7, 182.7] | 1.0211 | REAL, small unmodelled feature, unchanged: a 3 mm wide strip at x = -19.0, y -0.9..2.1, z 45.6-84.9 on the T1 underside. Scan surface INSIDE the CAD by 0.92-1.02 mm (overlay x=-19): a flat land or groove on the T1 outer bottom cylinder that the CAD leaves full round |
| 9 | 386 | [1.669, 56.739, 79.755] | [56.494, 57.103] | [87.6, 89.9] | 1.1208 | REAL, unchanged: labyrinth (-Y) lip at y 56.5-57.1, x 0.1-2.4, z 45.8-123.4. Scan INSIDE the CAD by 0.94-1.12 mm: the CAD lip top/edge stands ~1 mm proud of the scan along 78 mm (lip chamfer or lower lip not modelled) |
| 10 | 363 | [4.211, -19.632, 4.081] | [14.886, 24.388] | [268.5, 298.7] | 4.107 | REAL, slightly improved (it1 bbox 479 -> 387): gearbox end, x -0.5..8.1, y -24.1..-13.1, z 0.9-8.6. Scan INSIDE the CAD, max 4.11. Partly inside the M2 screw-socket box 3 but extends past it (x to 8.1, y to -24.1): the socket counterbore/recess around the screw boss is modelled solid |
| 11 | 361 | [-2.359, 57.111, 173.108] | [54.875, 58.885] | [91.5, 92.8] | 1.9506 | REAL, unchanged (362 -> 373): labyrinth edge near the +X end, y 54.8-58.8, x -2.7..-1.5, z 168.9-185.3. Scan wall face outside the CAD, max 1.95 (labyrinth upstand set back or missing at the +X end; overlay y=58) |

### Over-band point clusters, CAD → scan (> 0.8 mm)

33264 points (0.1109 fraction) in 110 clusters ≥ 20 pts.

| # | n | centroid | r range | θ range (deg) | d max | explanation |
|---|---|---|---|---|---|---|
| 0 | 8661 | [-18.064, 25.251, 38.33] | [19.934, 45.273] | [111.9, 147.3] | 6.8972 | **UNEXPLAINED** |
| 1 | 4830 | [-19.286, 44.766, 191.791] | [35.438, 58.364] | [93.4, 131.7] | 7.2027 | **UNEXPLAINED** |
| 2 | 1857 | [-9.987, 43.511, 195.855] | [35.848, 51.891] | [89.7, 117.5] | 5.4521 | **UNEXPLAINED** |
| 3 | 1039 | [6.021, 57.928, 197.053] | [56.246, 61.495] | [81.5, 88] | 7.0955 | **UNEXPLAINED** |
| 4 | 1033 | [6.082, -20.644, 4.016] | [15.634, 26.639] | [265.2, 302.6] | 4.2942 | **UNEXPLAINED** |
| 5 | 854 | [11.332, 46.711, 7.703] | [44.465, 53.784] | [71, 81.5] | 4.3344 | **UNEXPLAINED** |
| 6 | 696 | [-6.454, 61.314, 165.801] | [54.622, 64.706] | [90, 103.1] | 4.7947 | **UNEXPLAINED** |
| 7 | 653 | [-12.181, -18.861, 12.138] | [18.414, 27.766] | [216.1, 254.4] | 7.8945 | **UNEXPLAINED** |
| 8 | 643 | [-4.432, -26.865, 180.773] | [26.258, 28.112] | [258.7, 264.1] | 3.2611 | **UNEXPLAINED** |
| 9 | 561 | [13.437, 12.219, 7.646] | [15.626, 21.187] | [32, 50.9] | 3.1945 | **UNEXPLAINED** |
| 10 | 521 | [12.161, -12.622, 8.333] | [15.675, 20.534] | [306.8, 327.6] | 3.3978 | **UNEXPLAINED** |
| 11 | 504 | [10.56, 42.667, 7.343] | [41.822, 45.937] | [72, 80] | 5.254 | **UNEXPLAINED** |

**Datum audit (report-only, QUESTIONS Q2):** angle 0.5261°, origin offset 0.2234 mm, point disagreement p95 0.6845 mm; reference band ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) (OUTSIDE).

## 9. Band miss: where and what next

| region | cause | options |
|---|---|---|
| whole part (gated) | scan->CAD masked p95 1.161 / max 5.965 and observable CAD->scan p95 1.004 / max 7.693 vs 0.30 / 0.80. 22.8 % of masked scan points are > 0.30 mm (band allows 5 %). Report-only headroom (qa/headroom.json): even if every point in the 12 listed scan->CAD clusters were perfect, masked p95 would still be ~0.80 and 18.3 % of points > 0.30, so the residual is diffuse as well as clustered: sharp unmodelled blends (qa/edge_share.json), the ~0.1-0.3 deg bore warp (L5), scanned inter-part/interior surfaces (L6) | it3 (last loop): fix the named, fixable clusters below; consider modelling the main moulded blends; the 0.30 p95 band is unlikely to be reached on this assembly scan even then, so before spending loop 3 the owner may prefer to decide now between (a) one more geometry loop, (b) BAND_NOT_MET with a recorded ACCEPT-BAND, or (c) a full-res scan / separated-housing scan / calipers -- Owner chose (b) on 2026-10-01: no loop 3; BAND_NOT_MET pending a recorded ACCEPT-BAND. |
| +X end z > 150 | scan->CAD p95 1.807 / max 4.738 (it1 1.883 / 4.723), CAD->scan p95 2.906 / max 7.203 (it1 2.863 / 7.321): essentially unchanged. Hollow -Y latch box modelled solid (cluster 0), T2 rounded +X end shape (cluster 1), end-wall position (clusters 3, 6), rib/peg at z 170 (cluster 7), labyrinth upstand at the +X end (cluster 11); CAD->scan clusters 1-3 and 6 (~8,400 pts, max 7.2) are the CAD side of the same T2 end/latch mismatch. Three of these were listed as fixed in MODELING_PLAN but did not move | remeasure the T2 +X end from Z sections 185-203 and model it as the scanned curve; model the -Y latch box hollow; re-place the +X end wall/draft planes against the scan at z 202-205; add the z 170 peg/rib |
| motor end z 60-69 | clusters 4 and 5 (1,174 pts, max 5.97 = masked whole-part max): scan structure beyond the modelled can end; motor-can region zone scan->CAD p95 1.523 / CAD->scan p95 3.677 (CAD->scan cluster 0 is partly coverage, L9) | model the motor end bracket/cap from Z=62-68 sections, or with photos decide it is a wire exit and declare/mask it BEFORE the next gate (never after) |
| gearbox end z < 13 | scan->CAD p95 1.440 / max 4.107 (it1 1.779 / 4.123); CAD->scan p95 2.505 / max 7.895 unchanged. Socket recesses around the screw bosses modelled solid (cluster 10), CAD->scan clusters 4, 5, 7, 9-11 (edge pockets on the +x side of the block, max 7.9) unchanged since it1 | cut the socket counterbores/recesses; re-place the block's +x edge pockets against the scan; owner decides whether inter-part surfaces behind the cover are modelled |
| trough start + motor z 13-66 | largely fixed: scan->CAD masked p95 3.476 -> 1.063, max 16.303 -> 4.813 (it1 clusters 0, 1, 2 cleared). Remaining: T1 underside strip (cluster 8, ~1 mm) and motor-end structure | add the T1 underside flat strip; see motor end |
| mid troughs z 66-150 | closest to band: scan->CAD p95 0.597 / max 5.965 (max is cluster 5 at the zone edge), CAD->scan p95 0.269 / max 2.729. T1 bore wall zone p95 0.689 / 0.384 (two-way); labyrinth lip ~1 mm proud (cluster 9); 11.4 % of masked points > 0.30 here, 87 % of the 0.30-0.80 points near sharp CAD edges | model the labyrinth lip and main blends; the remaining warp can only be arbitrated with a full-res scan or calipers |

Missed band(s): `scan_to_cad:masked: p95 1.161 max 5.965 vs 0.3/0.8`; `cad_to_scan_observable: p95 1.004 max 7.693 vs 0.3/0.8`.

## 10. Named checks

| check | stage | ran | result | note |
|---|---|---|---|---|
| CHK-ACHIEVABLE | verify (`qa/gate.json#checks`) | yes | n/a | no Tier-1 (no calipers), nothing to attribute |
| CHK-CIRCULAR | verify (`qa/gate.json#checks`) | yes | pass | QA ICP (qa/registration.json) is QA-only and never written back; no expected value from measure/ or builder code; datum audit fits on the raw scan with QA-written regions (qa/datum_spec.json, same as it1); no Tier-1 expected values exist |
| CHK-CLUSTER | verify (`qa/gate.json#checks`) | yes | pass | 12 scan->CAD over-band clusters; unexplained: [] |
| CHK-ENUM | verify (`qa/gate.json#checks`) | yes | finding | no photos, so photo cross-check impossible. Features present in the scan and still wrong/absent in the CAD: hollow -Y latch box at z 161-167 modelled solid (cluster 0), T2 rounded/ramped +X end (cluster 1), +X end wall position (clusters 3, 6), motor end structure beyond the can (clusters 4, 5), peg/rib at the T2 +X end underside (cluster 7), T1 underside flat strip (cluster 8), labyrinth lip (clusters 9, 11), gearbox socket recess (cluster 10). Builder-claim check: MODELING_PLAN 'it2 region fixes ... verifier clusters 0,1,2,4,6,7,8,10,11' - it1 clusters 0,1,2 are fixed (over-band pts in their bboxes 3247->555, 2200->345, 2058->302) and 7,8,9,11 partly, but it1 clusters 4 (T2 +X end, 1390->1401), 6 (+X end wall, 842->837) and 10 (motor end, 498->490) are numerically unchanged although listed as fixed; it1 cluster 3 (hollow latch box, 1443->1433) was not addressed. MODELING_PLAN 0 also says 15 detached pieces ~300 mm3 dropped while build_log.txt lists 10 pieces ~122 mm3 (stale plan text) |
| CHK-FILLET | verify (`qa/gate.json#checks`) | yes | pass | build/export_check.json fillets [] in both frames, build/fillets.json empty; none planned, none FAILED/REDUCED. Moulded blends are left sharp (declared, MODELING_PLAN 0/5); qa/edge_share.json: 72 % of masked-band 0.30-0.80 mm scan points lie within 1.5 mm of a sharp CAD edge (87 % in z 66-150) vs 55 % / 49 % for points <= 0.30, so unmodelled blends carry part of the residual |
| CHK-INDEP | verify (`qa/gate.json#checks`) | yes | pass | fresh subagent context, own QA runs; see independence |
| CHK-LIKE4LIKE | verify (`qa/gate.json#checks`) | yes | pass | it1 vs it2 under the SAME protocol: regime baseline-skill plastic (identical file), masks.json/zones.json/icp_scan_masks.json/datum_spec.json copied byte-identical from _it1_SUPERSEDED/qa (same sha256 in deviation inputs), --scan-kind decimated, ICP ns 3M seed 11 / nc 300k seed 13 / 70 deg / 0.8 mm / 3.0 mm / cap 60 / tol 1e-6, gate sampling all scan verts + 300k CAD samples seed 2, k 8, n_samp 3M, observability 20k seed 5 cone 60, same open-boundary sweep, same 18 overlay panels. Only differences: the CAD itself (1873 vs 1572 faces; QA tessellation 0.005/0.05 watertight in it2, 17 open edges in it1) and a data-dependent helper count in the ray test (47 vs 50). Side by side in qa/it1_vs_it2_summary.json and per-it1-cluster in qa/it1_vs_it2_clusters.json. The improvement is geometry, not protocol: scan->CAD masked p95 1.937 -> 1.161, max 16.303 -> 5.965; observable CAD->scan p95 1.309 -> 1.004, max 7.709 -> 7.693 (unchanged) |
| CHK-MASK | verify (`qa/gate.json#checks`) | yes | pass | no pass depends on a mask |
| CHK-OVERLAY | verify (`qa/gate.json#checks`) | yes | pass | every panel shows scan |
| CHK-PATCHWORK | verify (`qa/gate.json#checks`) | yes | pass | QA census (qa/step_check.json): 1873 faces = 1714 plane + 159 cylinder, analytic area share 100 %, 0 B-spline/ruled. model.py grep: no loft/ruled/spline/import_stl; make_polygon only for extruded constant sections, few-vertex prisms and cutting half-spaces. it2 adds ShapeUpgrade_ShapeDivideArea (MaxArea 1500 mm2) + ShapeFix: 1832 -> 1873 faces, splits large analytic faces, adds no faceting. High plane count from ribs/slabs/region prisms (reported, not gated) |
| PHOTO-PLAUSIBILITY | verify (`qa/gate.json#checks`) | yes | n/a | no photos supplied (input/photos empty) |
| CHK-PUBLISH | deliver (preflight) | yes | pass | verdict BAND_NOT_MET |
| CHK-SUPERSEDED | deliver (preflight) | yes | pass | all earlier iterations kept intact |
| inputs_unchanged | deliver (preflight) | yes | pass | 1 input file(s) unchanged |
| hash_frozen | deliver (preflight) | yes | pass | every build/ STEP matches hash_frozen |
| regime_declared | deliver (preflight) | yes | pass | regime 'baseline-skill' |

## 11. Declared limitations (each with its re-run trigger)

| id | limitation | re-run trigger | evidence |
|---|---|---|---|
| L1 | Decimated scan only: every deviation number is INSPECTION ONLY, not an official grade (decimated scan). | full-res scan available | qa/gate.json#limitations.0; input/INPUT_HASHES.json#scan_resolution |
| L2 | Tier-1 not run - no Tier-1 (no calipers run) - no calipers were supplied, so no dimension is caliper-verified; absent is not passed. | any caliper reading on a bore radius, the flange height or the gearbox end face -> re-run Tier-1 | qa/gate.json#limitations.1; intake/MEASUREMENTS.md |
| L3 | Absolute scale not caliper-verified (CHK-SCALE flag at intake; units assumed mm). | one caliper reading of the overall length or a bore diameter | qa/gate.json#limitations.2 |
| L4 | No photos: feature enumeration and photo plausibility could not be cross-checked; the motor-end structures cannot be classed as part feature vs wire exit. | photos of the motor end, the -Y latch box and the +X end | qa/gate.json#limitations.3 |
| L5 | Datum audit outside the report-only reference (0.5261 deg / 0.2234 mm); the bore axis bows along the part (warp vs intent not separable from one scan). | full-res scan or a second part to separate warp from design intent | qa/gate.json#limitations.4; intake/datum_crop.py |
| L6 | Scan points that lie INSIDE the closed CAD solid are counted in the gate, not masked: hollow latch boxes modelled solid, gearbox socket recesses, inter-part surfaces behind the gearbox cover, motor end; gearbox and motor interiors were declared solid at intake. | owner decision on which hollow features must be modelled hollow, or a scan of the separated housing | qa/gate.json#limitations.5 |
| L7 | Masks M1 (loose motor wires), M2 (gearbox screw heads) and M3 (scan open boundary) are declared from intake and unchanged since iteration 1; no gated item passes because of a mask (masked and unmasked both miss). | none for the masks; re-run with the same masks after any rebuild | qa/gate.json#limitations.6; qa/masks.json |
| L8 | Validity holds at the gated fine tessellation in both frames (one valid closed solid, no non-manifold edges), but coarse tessellations are not watertight. | a downstream slicer/CAM/FEA tool reports a non-closed mesh -> re-check at its tessellation | qa/gate.json#limitations.7 |
| L9 | Observability: part of the CAD surface is not observable from the scan; observable CAD->scan is graded, raw CAD->scan is reported only, and part of the largest CAD->scan cluster is a scan coverage gap in the motor/T2 crevice. | full-res scan with coverage of the motor/T2 crevice | qa/gate.json#limitations.8 |
| L10 | Band NOT met and accepted by the owner: scan->CAD masked p95 1.1613 / max 5.9652 mm and observable CAD->scan p95 1.0039 / max 7.6934 mm against the plastic band; the +X end (hollow latch box, T2 end ramp, end wall), the motor end and the gearbox cover recesses remain the largest misses. MODELING_PLAN lists some of these as addressed in iteration 2, but the verifier found their numbers unchanged. | a further geometry loop on the +X end, motor end and gearbox recesses, or a full-res scan of the separated housing | qa/gate.json#band_fails; qa/gate.json#miss_explanations; decisions/accept_band.md |
| L11 | Moulded blends are left sharp and the part warp is modelled as a rigid tilt of each trough group; both leave diffuse deviation near edges and at the part ends. | a request for blend-accurate CAD, or calipers/second part to arbitrate warp | build/MODELING_PLAN.md; measure/params.json#simplifications |

## 12. Assumptions and invented geometry

- Rib slabs under the troughs are extended upward to merge with the trough wall (connection only; trough voids re-cut). _(source: assumed; measure/geometry.json#slab_top_extension)_
- The -Y flange tab roots are extended into the upstand wall so the tabs are attached. _(source: assumed; measure/scripts/make_params.py)_
- Small detached pieces from region primitives were dropped and three enclosed cavities were filled to keep one closed solid (listed in build_log.txt). _(source: assumed; build/build_log.txt)_
- Gearbox and motor interiors are solid (scanned as closed outer skins); the motor is an envelope of stepped cylinders. _(source: assumed; intake/INTAKE_CARD.md; DECISIONS.md PART-CLASS)_
- The +X end group values read from renders/sections (T2 pocket end radius and position, ridge plateau) carry larger uncertainty. _(source: assumed; measure/geometry.json#xend)_

## 13. Claim boundary — what this result is NOT

- **Not fit for:** tooling, manufacture or release: the band is missed, the scan is decimated and nothing is caliper-verified
- **Not fit for:** fit-checking of the lid, the brush rollers or the motor
- Fit for: visual/reference model and layout of the housing; the trough bodies are the closest-fitting region (see the zone table)
- Fit for: a starting model for a caliper-driven or full-res-scan rework (parametric model.py + params.json + region feature sets)
- The verdict covers only the Tier-1, deviation and named-check gates above, under the **baseline-skill** regime.

- Verify's own claim boundary (`qa/gate.json#claim_boundary`): VERDICT NOTE: Verdict word set to BAND_NOT_MET after the owner's decision not to spend loop 3 (DECISIONS.md, OTHER 2026-10-01: 'BAND_NOT_MET kabul, teslim et', citing the prior it2 gate 15818f79d016 whose proposed verdict was REVISE). This is a reason for the verdict choice inside the unchanged allowed set {BAND_NOT_MET, REVISE, HALT}, NOT a regrade: same it2 evidence, same numbers, no geometry change, bands not loosened, no mask added. Delivery still needs a recorded ACCEPT-BAND entry citing THIS gate.json by hash and naming a band_fails item (run-contract 10). Not a deliverable without that ACCEPT-BAND. The it2 STEP is now a valid single closed solid (BRepCheck valid after fine meshing, 0 non-manifold edges, watertight 0.005/0.05 tessellation in both frames, no self-intersection), but the whole-part scan band is still missed by ~4x on p95 (scan->CAD masked 1.161 vs 0.30) on a decimated, inspection-only scan with no calipers or photos. Not fit for tooling, manufacture, or fit-checking of the lid, brush rollers or motor. The trough bores (z 66-150) agree to ~0.27-0.6 mm p95 and may serve as a visual/reference model only.

## 14. Human acceptance of the band miss

Accepted by **owner (decision card)** on 2026-10-01 (`DECISIONS.md`, ACCEPT-BAND): accept scan_to_cad and cad_to_scan_observable band misses, gate 6a97111efe32 (created 2026-10-01T07:05:48+00:00): scan->CAD masked p95 1.161 / max 5.965 and observable CAD->scan p95 1.004 / max 7.693 vs 0.30 / 0.80 (baseline-skill plastic); deliver as BAND_NOT_MET, no loop 3. Record: `decisions/accept_band.md` (sha256 `c17f790c609d0fd64f15d3fb96d03bd2d4dcc2320903cadb4c8331595838b60e`).

## 15. Reproduction

```
cd build && python3 model.py --params ../measure/params.json --alignment ../intake/alignment.json --out . --part dreame_brushes_housing
```

Fresh-process rebuild check (`deliver/repro.json`): reproducible **yes**; method 2 fresh subprocess rebuild(s) of build/model.py in a scratch copy; STEP re-imported; solids, faces, surface census, volume, bbox compared (raw hash reported, not required); environment python: 3.11.15; platform: Linux-6.18.44-fc-v50-x86_64-with-glibc2.39; build123d: 0.13.0; OCP: 8.0.1.0; numpy: 2.4.6.

| file | volume mm³ | |Δ volume| | max |Δ bbox| | faces equal | identical | raw sha equal |
|---|---|---|---|---|---|---|
| dreame_brushes_housing.step | 138726.0512 | 0 | 0 | yes | yes | no |
| dreame_brushes_housing_datum.step | 138726.0512 | 0 | 0 | yes | yes | no |

_Raw STEP hashes differ between runs because STEP headers carry a timestamp; the geometry is compared._

## 16. Provenance of every number in this file

| file | sha256 |
|---|---|
| `qa/gate.json` | 6a97111efe328fd998d1bbf57ea1f09f49d0b1cfc0e4fcadc6a04f05657dbabd |
| `measure/params.json` | 1abb84f96f10a07ca12c55feb07376910cfe6dcd1a234ab277d5998c5b9a5bd6 |
| `build/export_check.json` | 023821192309aff425798ad8ba6201a52e5a685d01e0444a7816bce7726d9d0d |
| `intake/alignment.json` | 99c3154266f1c76a733bc7a09c79d3e8a2f26ff84dc7babf8648d6154044d4e9 |
| `deliver/repro.json` | 4e0162cc8abd14f124006521a0003c71a186f6f13ded84607e1c0b55c33f2c6d |
| `deliver/limitations.json` | d163953fa42cd69e92bedfa405c79a772e1d31b4c964059e49a75ac8751972b6 |

Generated by `stl-re-deliver/scripts/make_readme.py`. Do not edit numbers by hand; fix the JSON and re-render.
