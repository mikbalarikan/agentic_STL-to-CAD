# cliff_bumper_sensor — STL → STEP reverse-engineering delivery

**Verdict: `BAND_NOT_MET`** (from `qa/gate.json`; full reasoning in `qa/VERDICT.md`).  
**Band regime:** baseline-skill — source `baseline/skills/stl2step-build123d/SKILL.md:87`.  
**Iteration:** 1 of 3 (earlier iterations kept: none).  
**Verification independence (CHK-INDEP):** pass — Fresh context; see independence.  

> **A deviation band was NOT met.** Delivered only under the recorded human acceptance below (by Ikbal (owner, decision card), 2026-09-30, record `decisions/accept_band.md`).

## 1. The part

![reference photo](../input/photos/photo_1.png)

Cliff / bumper IR sensor module housing: black moulded body with a clear cover and a clear two-window lens nose, side tabs and guide rails that slide into the host bumper, and a rear shelf with three harness pockets. Delivered as one fused envelope solid of the two moulded pieces.

## 2. Deliverables

| file | frame | solids | valid | closed | faces | volume mm³ | bbox mm |
|---|---|---|---|---|---|---|---|
| `build/cliff_bumper_sensor_datum.step` | datum | 1 | yes | yes | 106 | 7736.3821 | max: [7.073, 19.004, 0]; min: [-27.329, -18.988, -9.889]; size: [34.402, 37.992, 9.889] |
| `build/cliff_bumper_sensor.step` | scan | 1 | yes | yes | 106 | 7736.3821 | max: [25.9274, -17.3559, -150.9329]; min: [7.1042, -59.3796, -193.7583]; size: [18.8232, 42.0237, 42.8254] |

Source of the table: `build/export_check.json`. The editable design intent is `build/model.py` driven by `measure/params.json`.

## 3. Method

1. Intake: full-resolution scan hashed; working copy decimated for measuring only; regime baseline-skill (plastic) declared from the owner's message; scan-only (no calipers).
2. Datum: top face (clear-cover plateau) = XY at z=0, material below; +Y side wall clocks the frame; X origin = lower-body rear wall, Y origin = side-wall mid-plane (plane-based origin, no round feature on this part).
3. Measure: plane and 2-D circle fits on named regions of the aligned scan (measure/measure_box.py), every value kept as measured or averaged over its own stations; nothing snapped.
4. Rebuild: build123d boxes, a lens cup with measured bottom-side rounds cut by the measured lens plane, rails, tabs and ramps unioned; pockets, lip, wire slot, seam groove and two recessed windows cut once; all nine rounds built at target radius.
5. Verify: independent agent with its own ICP and plane-origin datum audit, two-way full-resolution deviation with named masks and zones.

## 4. Coordinate frames

Two STEP files carry the same solid (SYNTHESIS D14): the **datum frame** (design frame, below) and the **scan frame** (the original STL coordinates; the CAD overlays the raw scan).

| element | definition | fit residual (rms / max mm) | why |
|---|---|---|---|
| origin | top face (z=0) ∩ side-wall mid-plane (y=0) ∩ lower-body rear wall (x=0) | — | — |
| primary (plane) | top face, clear-cover plateau (datum x -14.5..-1.5; crop excludes the cover/cap seam groove at x=-1.2 and the crowned cap) | 0.012 / 0.0685 | largest continuous moulded flat; the housing's back face that seats against the bumper pocket; both housing halves are flush on it |
| secondary (plane) | +Y side wall (between nose blend and tab) normal -> +Y | 0.0156 / 0.0608 | the long side walls carry the mounting tabs; X runs nose(-) to connector shelf(+) |
| clock | plane_normal: +Y side wall (between nose blend and tab) normal -> +Y (angle 29.4435°) | — | — |

Measured tilt: 0.3447° (clock wall out-of-perpendicularity to the primary plane (prismatic part, no coaxial stations); a draft or a moulding error reads the same). Scale factor applied: 1. Scan noise floor: 0.0275 mm (rms of RANSAC+SVD plane on +Y side wall of the main body (4986 faces)).

Scan → datum matrix (row-major, `intake/alignment.json#matrix_4x4`); the scan-frame STEP uses its inverse:

```
 0.409423  -0.441681   0.798305   105.727355
-0.036346   0.866413   0.498004   119.101205
-0.911620  -0.232910   0.338676   60.944209
 0.000000   0.000000   0.000000   1.000000
```

## 5. Parameters

Sources: assumed 3, scan 64 (total 67). Rendered from `measure/params.json`; never edited by hand.

| name | value | unit | measured | rule | source | ± mm | critical | evidence |
|---|---|---|---|---|---|---|---|---|
| `body_front_x` | -21.209 | mm | [-21.164, -21.255] | mean-of-n | scan | 0.045 | no | measure/figures/measurements.json#body_front_x, measure/figures/measurements.json#body_front_x_neg |
| `body_y_neg` | -16.015 | mm | [-15.974, -15.979, -16.091] | mean-of-n | scan | 0.054 | no | measure/figures/measurements.json#body_y_neg, measure/figures/measurements.json#body_y_neg_behind_tab, measure/figures/measurements.json#body_y_neg_below_tab |
| `body_y_pos` | 16.029 | mm | [15.973, 16.049, 16.065] | mean-of-n | scan | 0.04 | no | measure/figures/measurements.json#body_y_pos, measure/figures/measurements.json#body_y_pos_behind_tab, measure/figures/measurements.json#body_y_pos_below_tab |
| `bottom_slope_deg` | 1.554 | deg | 1.554 | keep-measured | scan | 0.03 | no | measure/figures/measurements.json#body_bottom_plane |
| `bottom_z_at_x0` | -9.675 | mm | -9.675 | keep-measured | scan | 0.03 | no | measure/figures/measurements.json#body_bottom_plane |
| `cap_top_R` | 1.74 | mm | [1.705, 1.776] | mean-of-n | scan | 0.035 | no | measure/figures/measurements.json#cap_top_edge_R, measure/figures/measurements.json#cap_top_edge_R_neg |
| `cap_y_neg` | -16.329 | mm | [-16.314, -16.345] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#cap_y_neg, measure/figures/measurements.json#cap_y_neg_low |
| `cap_y_pos` | 16.208 | mm | [16.123, 16.292] | mean-of-n | scan | 0.085 | no | measure/figures/measurements.json#cap_y_pos, measure/figures/measurements.json#cap_y_pos_low |
| `cover_bot_R` | 2.137 | mm | [2.165, 2.118, 2.057, 2.086, 2.139, 2.17, 2.125, 2.178, 2.105, 2.114, 2.136, 2.257] | mean-of-n | scan | 0.049 | no | measure/figures/measurements.json#cover_bot_edge_R, measure/figures/measurements.json#cover_bot_edge_R_neg |
| `cover_top_R` | 2.072 | mm | [2.215, 2.194, 2.152, 2.023, 2.09, 2.341, 2.55, 1.506, 1.778, 1.871] | mean-of-n | scan | 0.282 | no | measure/figures/measurements.json#cover_top_edge_R, measure/figures/measurements.json#cover_top_edge_R_neg |
| `nose_cup_R` | 7.758 | mm | [7.567, 7.551, 7.827, 7.717, 7.747, 7.783, 7.741, 7.577, 8.422, 7.296, 7.523, 7.677, 7.855, 7.93, 7.957, 7.956] | mean-of-n | scan | 0.244 | no | measure/figures/measurements.json#nose_cup_R_pos, measure/figures/measurements.json#nose_cup_R_neg |
| `nose_half_w` | 14.906 | mm | [14.923, 14.889] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#nose_half_width_top_pos, measure/figures/measurements.json#nose_half_width_top_neg |
| `nose_plane_normal` | [-0.8623, 0.0098, 0.5062] | mm | [-0.8623, 0.0098, 0.5062] | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#nose_slope_plane |
| `nose_plane_point` | [-24.7547, -0.0313, -4.0283] | mm | [-24.7547, -0.0313, -4.0283] | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#nose_slope_plane |
| `nose_tip_R` | 0.53 | mm | 0.53 | keep-measured | scan | 0.028 | no | measure/figures/measurements.json#nose_tip_R |
| `nose_top_R` | 2.072 | mm | — | assumed | assumed | 0.3 | no | same as cover_top_R |
| `pocketA_y0` | -15.593 | mm | -15.593 | keep-measured | scan | 0.046 | yes | measure/figures/measurements.json#pocket_wall_0 |
| `pocketA_y1` | -5.91 | mm | -5.91 | keep-measured | scan | 0.037 | yes | measure/figures/measurements.json#pocket_wall_1 |
| `pocketB_y0` | -5.108 | mm | -5.108 | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#pocket_wall_2 |
| `pocketB_y1` | 4.771 | mm | 4.771 | keep-measured | scan | 0.045 | yes | measure/figures/measurements.json#pocket_wall_3 |
| `pocketC_y0` | 5.703 | mm | 5.703 | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#pocket_wall_4 |
| `pocketC_y1` | 15.31 | mm | 15.31 | keep-measured | scan | 0.06 | yes | measure/figures/measurements.json#pocket_wall_5 |
| `pocket_ceiling_z` | -1.385 | mm | -1.385 | keep-measured | scan | 0.04 | yes | measure/figures/measurements.json#pocket_ceiling_z |
| `pocket_lip_z` | -3.536 | mm | -3.536 | keep-measured | scan | 0.055 | no | measure/figures/measurements.json#pocket_lip_front_z |
| `pocket_x_back` | 5.925 | mm | 5.925 | keep-measured | scan | 0.075 | yes | measure/figures/measurements.json#pocket_x_back |
| `pocket_x_front` | 1.128 | mm | 1.128 | keep-measured | scan | 0.044 | yes | measure/figures/measurements.json#pocket_x_front |
| `rail_rear_top_z` | -2.282 | mm | [-2.302, -2.263] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#rail_rear_top_z_pos, measure/figures/measurements.json#rail_rear_top_z_neg |
| `rail_rear_x_start` | -0.882 | mm | [-0.853, -0.911] | mean-of-n | scan | 0.029 | no | measure/figures/measurements.json#rail_rear_x_start_pos, measure/figures/measurements.json#rail_rear_x_start_neg |
| `rail_top_z` | -3.164 | mm | [-3.183, -3.146] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#rail_top_z_pos, measure/figures/measurements.json#rail_top_z_neg |
| `rail_x_start_neg` | -6.396 | mm | -6.396 | keep-measured | scan | 0.029 | no | measure/figures/measurements.json#rail_x_start_neg |
| `rail_x_start_pos` | -6.176 | mm | -6.176 | keep-measured | scan | 0.068 | no | measure/figures/measurements.json#rail_x_start_pos |
| `rail_y_neg` | -17.732 | mm | -17.732 | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#rail_y_neg |
| `rail_y_pos` | 17.74 | mm | 17.74 | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#rail_y_pos |
| `ramp_peak_z` | -9.889 | mm | [-9.883, -9.896] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#ramp_peak_z_pos, measure/figures/measurements.json#ramp_peak_z_neg |
| `ramp_x_end` | -14.881 | mm | [-14.882, -14.881] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#ramp_x_end_pos, measure/figures/measurements.json#ramp_x_end_neg |
| `ramp_x_start` | -19.618 | mm | [-19.616, -19.62] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#ramp_x_start_pos, measure/figures/measurements.json#ramp_x_start_neg |
| `ramp_y_in` | 1.954 | mm | [1.96, 1.948] | mean-of-n | scan | 0.028 | no | measure/figures/measurements.json#ramp_y_span_pos_x-16.0, measure/figures/measurements.json#ramp_y_span_neg_x-16.0 |
| `ramp_y_out` | 4.034 | mm | [4.08, 3.987] | mean-of-n | scan | 0.046 | no | measure/figures/measurements.json#ramp_y_span_pos_x-16.0, measure/figures/measurements.json#ramp_y_span_neg_x-16.0 |
| `rear_wall_x` | -0.022 | mm | -0.022 | keep-measured | scan | 0.048 | no | measure/figures/measurements.json#rear_wall_x |
| `seam_groove_R` | 0.533 | mm | [0.653, 0.545, 0.454, 0.482] | mean-of-n | scan | 0.076 | no | measure/figures/measurements.json#seam_groove |
| `seam_groove_zc` | 0.301 | mm | [0.418, 0.277, 0.23, 0.28] | mean-of-n | scan | 0.07 | no | measure/figures/measurements.json#seam_groove |
| `seam_x` | -1.065 | mm | [-1.125, -1.089, -1.002, -1.045] | mean-of-n | scan | 0.046 | no | measure/figures/measurements.json#seam_groove |
| `shelf_bottom_z` | -3.691 | mm | -3.691 | keep-measured | scan | 0.041 | no | measure/figures/measurements.json#shelf_bottom_z |
| `shelf_end_x` | 7.073 | mm | 7.073 | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#shelf_end_x |
| `shelf_top_R` | 1.107 | mm | [1.05, 1.165] | mean-of-n | scan | 0.057 | no | measure/figures/measurements.json#shelf_top_edge_R, measure/figures/measurements.json#shelf_top_edge_R_neg |
| `shelf_top_z` | -0.077 | mm | -0.077 | keep-measured | scan | 0.037 | no | measure/figures/measurements.json#shelf_top_z |
| `shelf_y_neg` | -16.388 | mm | -16.388 | keep-measured | scan | 0.028 | no | measure/figures/measurements.json#shelf_y_neg |
| `shelf_y_pos` | 16.189 | mm | 16.189 | keep-measured | scan | 0.028 | no | measure/figures/measurements.json#shelf_y_pos |
| `slot_top_z` | -6.084 | mm | -6.084 | keep-measured | scan | 0.3 | no | measure/figures/measurements.json#slot_top_z |
| `slot_x_end` | -1.502 | mm | -1.502 | keep-measured | scan | 0.028 | no | measure/figures/measurements.json#slot_x_end |
| `slot_y_neg` | -1.558 | mm | -1.558 | keep-measured | scan | 0.04 | no | measure/figures/measurements.json#slot_y_neg |
| `slot_y_pos` | 1.504 | mm | 1.504 | keep-measured | scan | 0.034 | no | measure/figures/measurements.json#slot_y_pos |
| `tab_blob_not_modelled` | 0 | mm | — | assumed | assumed | 0.3 | no | measure/figures/measurements.json#nub_top_z_pos |
| `tab_bot_z` | -6.403 | mm | [-6.415, -6.391] | mean-of-n | scan | 0.028 | yes | measure/figures/measurements.json#tab_bot_z_pos, measure/figures/measurements.json#tab_bot_z_neg |
| `tab_top_z` | -4.558 | mm | [-4.54, -4.575] | mean-of-n | scan | 0.028 | yes | measure/figures/measurements.json#tab_top_z_pos, measure/figures/measurements.json#tab_top_z_neg |
| `tab_x_end_neg` | -1.404 | mm | -1.404 | keep-measured | scan | 0.037 | no | measure/figures/measurements.json#tab_x_end_neg |
| `tab_x_end_pos` | -1.263 | mm | -1.263 | keep-measured | scan | 0.028 | no | measure/figures/measurements.json#tab_x_end_pos |
| `tab_x_start_neg` | -15.05 | mm | -15.05 | keep-measured | scan | 0.042 | yes | measure/figures/measurements.json#tab_x_start_neg |
| `tab_x_start_pos` | -14.77 | mm | -14.77 | keep-measured | scan | 0.031 | yes | measure/figures/measurements.json#tab_x_start_pos |
| `tab_y_neg` | -18.988 | mm | -18.988 | keep-measured | scan | 0.028 | yes | measure/figures/measurements.json#tab_y_neg |
| `tab_y_pos` | 19.004 | mm | 19.004 | keep-measured | scan | 0.039 | yes | measure/figures/measurements.json#tab_y_pos |
| `window_corner_R` | 6.033 | mm | — | assumed | assumed | 0.3 | no | nose_cup_R - (nose_half_w - window_y_out) |
| `window_depth` | 0.809 | mm | 0.809 | keep-measured | scan | 0.122 | no | measure/figures/measurements.json#window_depth |
| `window_s_hi` | 3.102 | mm | 3.102 | keep-measured | scan | 0.028 | no | measure/figures/measurements.json#window_s |
| `window_s_lo` | -4.193 | mm | -4.193 | keep-measured | scan | 0.028 | no | measure/figures/measurements.json#window_s |
| `window_y_in` | 1.042 | mm | [0.931, 1.153] | mean-of-n | scan | 0.111 | no | measure/figures/measurements.json#window_y_pos, measure/figures/measurements.json#window_y_neg |
| `window_y_out` | 13.181 | mm | [13.075, 13.287] | mean-of-n | scan | 0.106 | no | measure/figures/measurements.json#window_y_pos, measure/figures/measurements.json#window_y_neg |

## 6. Model tree (design intent)

The STEP is a neutral B-Rep; it carries no feature history. The editable design intent is `build/model.py` driven by `measure/params.json`, and the ordered feature plan is `build/MODELING_PLAN.md`.

| id | feature | params |
|---|---|---|
| F01 | cover box, sloped bottom, long-edge rounds | [body_front_x, seam_x, body_y_pos, body_y_neg, bottom_z_at_x0, bottom_slope_deg, cover_top_R, cover_bot_R] |
| F02 | lens cup cut by the lens plane | [nose_half_w, nose_cup_R, nose_top_R, nose_plane_normal, nose_plane_point, nose_tip_R] |
| F03 | rear cap | [cap_y_pos, cap_y_neg, cap_top_R, shelf_top_z] |
| F04 | connector shelf | [rear_wall_x, shelf_end_x, shelf_y_pos, shelf_y_neg, shelf_bottom_z, shelf_top_R] |
| F05 | guide rails | [rail_y_pos, rail_y_neg, rail_x_start_pos, rail_x_start_neg, rail_top_z, rail_rear_top_z, rail_rear_x_start] |
| F06 | tabs | [tab_y_pos, tab_y_neg, tab_x_start_pos, tab_x_start_neg, tab_x_end_pos, tab_x_end_neg, tab_top_z, tab_bot_z] |
| F07 | bottom ramps | [ramp_x_start, ramp_x_end, ramp_peak_z, ramp_y_in, ramp_y_out] |
| F09 | three pockets and lip relief | [pocket_x_front, pocket_x_back, pocket_ceiling_z, pocket_lip_z, pocketA_y0, pocketA_y1, pocketB_y0, pocketB_y1, pocketC_y0, pocketC_y1] |
| F11 | wire slot | [slot_x_end, slot_y_pos, slot_y_neg, slot_top_z] |
| F12 | seam groove | [seam_x, seam_groove_R, seam_groove_zc] |
| F13 | two recessed lens windows | [window_depth, window_y_in, window_y_out, window_s_lo, window_s_hi, window_corner_R] |

## 7. Tier-1 — caliper dims re-measured on the STEP

**Tier-1 not run: no caliper dimensions exist.** Every dimension is scan authority (or operator spec); see the source column in §5. Absent is not passed.

## 8. Deviation gate (scan ↔ CAD)

Regime **baseline-skill** (`baseline/skills/stl2step-build123d/SKILL.md:87`); bands: p95_mm: 0.3; max_mm: 0.8; tier1_abs_mm: —; interface_max_mm: —.

Registration: point-to-point ICP, CAD samples -> scan samples, masked correspondences (B02 q20_tier2.py), iterations 60/60, converged yes, correction 0.1223° / 0.0194 mm.  
Unobservable CAD fraction: 0.0002.

| direction | n | rms | p50 | p95 | p99 | max | sampling | source |
|---|---|---|---|---|---|---|---|---|
| scan → CAD **unmasked** | 251181 | 0.2596 | 0.0442 | 0.3765 | 1.3856 | 3.0771 | — | `qa/gate.json#deviation` |
| scan → CAD (masked) | 243829 | 0.1243 | 0.0425 | 0.225 | 0.5779 | 1.9364 | — | `qa/gate.json#deviation` |
| CAD → scan **unmasked** (all) | 300000 | 0.1753 | 0.0435 | 0.3405 | 0.7997 | 2.0182 | — | `qa/gate.json#deviation` |
| CAD → scan (masked) | 261694 | 0.1029 | 0.0391 | 0.1901 | 0.4255 | 1.2611 | — | `qa/gate.json#deviation` |
| CAD → scan (observable) | 19996 | 0.17 | 0.0434 | 0.3311 | 0.7765 | 1.9196 | — | `qa/gate.json#deviation` |

### Gate results (what the verdict was graded on)

| item | band | measured | result |
|---|---|---|---|
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | p95 0.225 max 1.9364 (n 243829) | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | p95 0.3311 max 1.9196 (n 19996) | FAIL |
| zone:Z-LENS lens frame rib and windows:scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.5891 max 0.9152 (n 39263) | FAIL |
| zone:Z-LENS lens frame rib and windows:cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 0.5182 max 0.8557 (n 26955) | FAIL |
| zone:Z-POCKET shelf underside pockets:scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.1699 max 0.7187 (n 31874) | PASS |
| zone:Z-POCKET shelf underside pockets:cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 0.2335 max 1.2611 (n 29310) | FAIL |
| zone:Z-TAB tabs and guide rails:scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.1597 max 0.3318 (n 21143) | PASS |
| zone:Z-TAB tabs and guide rails:cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 0.1794 max 0.4412 (n 21658) | PASS |
| zone:Z-TOP top seating face:scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.0949 max 0.3073 (n 59768) | PASS |
| zone:Z-TOP top seating face:cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 0.1045 max 0.5642 (n 74365) | PASS |

### Per zone (unmasked and masked side by side)

| zone | kind | direction | unmasked | masked | unmasked stats | masked stats | note |
|---|---|---|---|---|---|---|---|
| I-window-interior (reported) | interior | scan_to_cad | reported | reported | n 29383 · p95 1.731 · max 3.0771 | n 22593 · p95 0.6628 · max 0.9152 | Interior/occluded region behind the clear windows: reported only. |
| I-window-interior (reported) | interior | cad_to_scan | reported | reported | n 28056 · p95 0.8443 · max 2.0182 | n 10124 · p95 0.7002 · max 0.8557 | Interior/occluded region behind the clear windows: reported only. |
| R-bottom z<-8.5 | region | scan_to_cad | reported | reported | n 54705 · p95 0.1489 · max 0.5614 | n 54705 · p95 0.1489 · max 0.5614 | region bucket (bottom plane, ramps) |
| R-bottom z<-8.5 | region | cad_to_scan | reported | reported | n 72392 · p95 0.1416 · max 0.462 | n 71374 · p95 0.1382 · max 0.462 | region bucket (bottom plane, ramps) |
| R-cap -1.2<=x<0 | region | scan_to_cad | reported | reported | n 17983 · p95 0.1688 · max 0.5956 | n 17983 · p95 0.1688 · max 0.5956 | region bucket (black cap) |
| R-cap -1.2<=x<0 | region | cad_to_scan | reported | reported | n 27203 · p95 0.2575 · max 1.5106 | n 24756 · p95 0.1747 · max 0.462 | region bucket (black cap) |
| R-cover -21.2<=x<-1.2 | region | scan_to_cad | reported | reported | n 126390 · p95 0.1654 · max 3.0771 | n 125671 · p95 0.1584 · max 1.9364 | region bucket (clear cover main box) |
| R-cover -21.2<=x<-1.2 | region | cad_to_scan | reported | reported | n 152673 · p95 0.1564 · max 1.4991 | n 150016 · p95 0.1485 · max 0.5642 | region bucket (clear cover main box) |
| R-nose x<-21.2 | region | scan_to_cad | reported | reported | n 45896 · p95 1.3936 · max 2.9833 | n 39263 · p95 0.5891 · max 0.9152 | region bucket |
| R-nose x<-21.2 | region | cad_to_scan | reported | reported | n 50140 · p95 0.7277 · max 2.0182 | n 26955 · p95 0.5182 · max 0.8557 | region bucket |
| R-shelf x>=0 | region | scan_to_cad | reported | reported | n 60912 · p95 0.1703 · max 0.7187 | n 60912 · p95 0.1703 · max 0.7187 | region bucket (connector shelf) |
| R-shelf x>=0 | region | cad_to_scan | reported | reported | n 69984 · p95 0.3048 · max 1.2809 | n 59967 · p95 0.2116 · max 1.2611 | region bucket (connector shelf) |
| Z-LENS lens frame rib and windows | whole | scan_to_cad | FAIL | FAIL | n 45896 · p95 1.3936 · max 2.9833 | n 39263 · p95 0.5891 · max 0.9152 | Functional interface (INTAKE §4 Z-LENS: lens frame + centre rib plane, two recessed transparent windows); band = regime p95/max per intake, transparent-window artefacts expected (masks M1/M5). |
| Z-LENS lens frame rib and windows | whole | cad_to_scan | FAIL | FAIL | n 50140 · p95 0.7277 · max 2.0182 | n 26955 · p95 0.5182 · max 0.8557 | Functional interface (INTAKE §4 Z-LENS: lens frame + centre rib plane, two recessed transparent windows); band = regime p95/max per intake, transparent-window artefacts expected (masks M1/M5). |
| Z-POCKET shelf underside pockets | whole | scan_to_cad | PASS | PASS | n 31874 · p95 0.1699 · max 0.7187 | n 31874 · p95 0.1699 · max 0.7187 | Functional interface (INTAKE §4 Z-POCKET: three harness/connector pockets under the shelf, ceiling z≈-1.39); band = regime p95/max per intake. Pockets have open scan loops (coverage). |
| Z-POCKET shelf underside pockets | whole | cad_to_scan | FAIL | FAIL | n 38583 · p95 0.4247 · max 1.2611 | n 29310 · p95 0.2335 · max 1.2611 | Functional interface (INTAKE §4 Z-POCKET: three harness/connector pockets under the shelf, ceiling z≈-1.39); band = regime p95/max per intake. Pockets have open scan loops (coverage). |
| Z-TAB tabs and guide rails | whole | scan_to_cad | FAIL | PASS | n 21705 · p95 0.1846 · max 1.5396 | n 21143 · p95 0.1597 · max 0.3318 | Functional interface (INTAKE §4 Z-TAB: tabs y ±19.0 z -6.40..-4.56, rails y ±17.74; slide into the bumper slot). Intake declared band = regime p95/max (regime has no interface_max), so kind 'whole' gates this zone at p95 0.30 / max 0.80. |
| Z-TAB tabs and guide rails | whole | cad_to_scan | PASS | PASS | n 22371 · p95 0.1855 · max 0.4753 | n 21658 · p95 0.1794 · max 0.4412 | Functional interface (INTAKE §4 Z-TAB: tabs y ±19.0 z -6.40..-4.56, rails y ±17.74; slide into the bumper slot). Intake declared band = regime p95/max (regime has no interface_max), so kind 'whole' gates this zone at p95 0.30 / max 0.80. |
| Z-TOP top seating face | whole | scan_to_cad | PASS | PASS | n 59768 · p95 0.0949 · max 0.3073 | n 59768 · p95 0.0949 · max 0.3073 | Functional interface (INTAKE §4 Z-TOP: top face z=0 seats against the bumper pocket); band = regime p95/max per intake. |
| Z-TOP top seating face | whole | cad_to_scan | PASS | PASS | n 74662 · p95 0.1043 · max 0.5642 | n 74365 · p95 0.1045 · max 0.5642 | Functional interface (INTAKE §4 Z-TOP: top face z=0 seats against the bumper pocket); band = regime p95/max per intake. |

### Masks (masked and unmasked are both shown above)

| mask | direction | why | fraction removed | stats inside |
|---|---|---|---|---|
| M1 window interior seen through clear lens | scan_to_cad | The two lens windows are transparent (photo_2, photo_4; INTAKE E15, §2 artefact zones, §8): the scanner saw through them and returned interior material. Scan points deeper than 1.3 mm behind the scan-fitted lens-frame plane (window face nominal ~0.8 mm, INTAKE E04) inside the window aperture and above the nose-bottom envelope are interior, not envelope. Located from the scan only (qa/scripts/make_masks.py). | 0.027 | n: 6790; rms: 1.3724; mean: 1.2689; p50: 1.0895; p95: 2.2279; p99: 2.8312; max: 3.0771 |
| M2 E14 tab blob (declared debris, open question) | scan_to_cad | Irregular ~1.6 mm lump on the +Y tab top at x -8.2..-7.1 (INTAKE E14): single component, no flat top, not mirrored on the -Y tab, not resolvable in photos; intake declared it debris/artefact (not modelled) with an OPEN QUESTION. Masked as an artefact; carried as a limitation because it is not proven debris. | 0.0022 | n: 562; rms: 0.81; mean: 0.7038; p50: 0.6642; p95: 1.4116; p99: 1.4948; max: 1.5396 |
| M3 wire-slot roof not scanned | cad_to_scan | The wire-slot roof was never scanned: open-boundary loop (283 verts, x -1.12..1.16, z up to -2.59) at the rear bottom centre (INTAKE §3, E12). CAD roof height is scan-extent provenance (MODELING_PLAN §6); CAD->scan distance there measures missing coverage, not a surface deviation. | 0 | n: 0; rms: —; mean: —; p50: —; p95: —; p99: —; max: — |
| M4 open boundary | cad_to_scan | Distance from a CAD point to a scan hole EDGE is not a surface deviation (18 open loops, 3,216 boundary edges, INTAKE §2/§3). B02 parameter 0.8 mm; radius sweep reported. | 0.1116 | n: 33476; rms: 0.4146; mean: 0.2815; p50: 0.1673; p95: 0.9069; p99: 1.3584; max: 2.0182 |
| M5 transparent window faces (CAD side) | cad_to_scan | CAD window faces / lower recess walls (0.3..1.3 mm behind the scan-fitted lens-frame plane, inside the aperture): the clear window face was only partly registered by the scanner (large open loops 789/704 verts in the windows, INTAKE §3), so CAD->scan distance there measures transparency (hole or interior behind), not the envelope. | 0.0477 | n: 14313; rms: 0.4875; mean: 0.3372; p50: 0.2197; p95: 1.0837; p99: 1.5725; max: 2.0182 |

**CHK-MASK: mask-dependent pass(es):** [zone Z-TAB tabs and guide rails scan_to_cad].

### Mask sensitivity

| band | direction | stats | variant |
|---|---|---|---|
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 0.0588; max_over_by: 2.2771 | scan_to_cad | n: 250619; rms: 0.257; mean: 0.1038; p50: 0.044; p95: 0.3588; p99: 1.3733; max: 3.0771 | all masks except M1 window interior seen through clear lens |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 1.1364 | scan_to_cad | n: 244391; rms: 0.13; mean: 0.0728; p50: 0.0426; p95: 0.2304; p99: 0.6015; max: 1.9364 | all masks except M2 E14 tab blob (declared debris, open question) |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.4611 | cad_to_scan | n: 261694; rms: 0.1029; mean: 0.0615; p50: 0.0391; p95: 0.1901; p99: 0.4255; max: 1.2611 | all masks except M3 wire-slot roof not scanned |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.7106 | cad_to_scan | n: 285687; rms: 0.1427; mean: 0.0765; p50: 0.0416; p95: 0.2606; p99: 0.6764; max: 1.5106 | all masks except M4 open boundary |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.753 | cad_to_scan | n: 266524; rms: 0.114; mean: 0.0648; p50: 0.0396; p95: 0.201; p99: 0.5137; max: 1.553 | all masks except M5 transparent window faces (CAD side) |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.565 | cad_to_scan | n: 280840; rms: 0.1187; mean: 0.0684; p50: 0.0408; p95: 0.2201; p99: 0.5368; max: 1.365 | M4 open boundary radius 0.0 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.4611 | cad_to_scan | n: 273736; rms: 0.1078; mean: 0.064; p50: 0.0399; p95: 0.2004; p99: 0.4642; max: 1.2611 | M4 open boundary radius 0.2 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.4611 | cad_to_scan | n: 269815; rms: 0.1055; mean: 0.0628; p50: 0.0396; p95: 0.1958; p99: 0.4458; max: 1.2611 | M4 open boundary radius 0.4 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.4611 | cad_to_scan | n: 261694; rms: 0.1029; mean: 0.0615; p50: 0.0391; p95: 0.1901; p99: 0.4255; max: 1.2611 | M4 open boundary radius 0.8 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.4611 | cad_to_scan | n: 234348; rms: 0.0923; mean: 0.0579; p50: 0.0385; p95: 0.1781; p99: 0.3306; max: 1.2611 | M4 open boundary radius 1.5 mm |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.4062 | cad_to_scan | n: 192324; rms: 0.0806; mean: 0.0548; p50: 0.038; p95: 0.1668; p99: 0.2785; max: 1.2062 | M4 open boundary radius 2.5 mm |

### Over-band point clusters, scan → CAD (> 0.8 mm)

6421 points (0.0256 fraction) in 4 clusters ≥ 20 pts.

| # | n | centroid | r range | θ range (deg) | d max | explanation |
|---|---|---|---|---|---|---|
| 0 | 3072 | [-23.76, -7.689, -7.406] | [22.752, 27.623] | [184.3, 208.3] | 2.1805 | Window interior (-Y window): material seen THROUGH the transparent lens window (INTAKE E15; photo_2/photo_4). Mostly inside M1; the residual (masked max 0.915) is the see-through layer just shallower than M1's conservative 1.3 mm staircase depth / above the nose-bottom floor (qa/posthoc_sensitivity.json, qa/lens_breakdown.json). Artefact, not a missing feature. |
| 1 | 2877 | [-23.384, 4.439, -7.156] | [20.985, 26.806] | [158.7, 176.7] | 3.0771 | Window interior (+Y window), same cause as cluster 0; also contains the intake-removed 1,063-face disconnected fragment (x -25.8..-23.4, y 6.6..10.0, z -8.1..-7.0) that floats behind the +Y window (qa/probe_cluster_s2c2.json). Artefact, not a missing feature. |
| 2 | 254 | [-3.563, -17.029, -1.207] | [16.558, 18.226] | [256.2, 259.2] | 1.9364 | Disconnected scan fragment: the 684-face, 2.94 mm2 separate body (x -4.11..-3.12, y -17.88..-15.69, z -2.16..-0.12) floating ~1.5-1.9 mm outside the -Y side wall near the top; intake removed it as a fragment before modelling (alignment.json removed.fragments_pct 0.3499, INTAKE §2 'wire stubs'), but the gate runs on the raw full-res scan. Not connected to the part (qa/probe_cluster_s2c2.json, overlay x=-3.6). NOT masked (would be a post-hoc mask); it alone sets the masked scan->CAD max 1.936. |
| 3 | 215 | [-7.411, 18.275, -3.329] | [19.247, 20.082] | [111, 113.7] | 1.5396 | E14 blob on the +Y tab (x -8.0..-7.1, y 17.8..18.6, up to z -2.8): irregular lump, single component, no flat top, not mirrored on the -Y tab (overlay y=18.5 / x=-7.6); intake declared debris with an open question. Inside M2. Stays an open question (limitation L3). |

### Over-band point clusters, CAD → scan (> 0.8 mm)

2996 points (0.01 fraction) in 11 clusters ≥ 20 pts.

| # | n | centroid | r range | θ range (deg) | d max | explanation |
|---|---|---|---|---|---|---|
| 0 | 984 | [-24.642, 4.027, -5.488] | [23.595, 26.864] | [166.1, 174.8] | 2.0182 | **UNEXPLAINED** |
| 1 | 726 | [-0.571, -0.078, -5.433] | [0.022, 2.16] | [5.5, 357.4] | 1.5106 | **UNEXPLAINED** |
| 2 | 442 | [-23.969, -10.292, -4.063] | [24.484, 27.305] | [198.7, 205.5] | 1.2817 | **UNEXPLAINED** |
| 3 | 253 | [5.777, -4.721, -1.88] | [6.936, 7.819] | [315.6, 326.9] | 1.2611 | **UNEXPLAINED** |
| 4 | 178 | [-25.049, -3.219, -6.066] | [24.673, 25.729] | [184.7, 189.9] | 1.2158 | **UNEXPLAINED** |
| 5 | 142 | [1.302, -6.092, -1.79] | [6.018, 6.623] | [279.8, 286.9] | 1.1805 | **UNEXPLAINED** |
| 6 | 102 | [5.786, 4.604, -1.677] | [6.965, 7.606] | [34, 41.5] | 1.2062 | **UNEXPLAINED** |
| 7 | 48 | [-21.209, -14.195, -7.578] | [25.095, 25.863] | [212.3, 214.9] | 0.9779 | **UNEXPLAINED** |
| 8 | 32 | [0.07, -3.579, -3.559] | [3.03, 3.96] | [269.6, 273.2] | 0.9383 | **UNEXPLAINED** |
| 9 | 27 | [-26.615, -3.929, -7.23] | [26.687, 27.212] | [184.7, 192.1] | 0.827 | **UNEXPLAINED** |
| 10 | 20 | [-23.197, -5.252, -1.316] | [23.671, 24.099] | [191.6, 195.4] | 0.8905 | **UNEXPLAINED** |

**Datum audit (report-only, QUESTIONS Q2):** angle 0.0748°, origin offset 0.0336 mm, point disagreement p95 0.0431 mm; reference band ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) (within).

## 9. Band miss: where and what next

| region | cause | options |
|---|---|---|
| whole part scan->CAD (masked max 1.936 > 0.80; p95 0.225 passes; unmasked p95 0.377 / max 3.077) | The masked max is set by a disconnected 684-face scan fragment floating outside the -Y wall (intake removed it before modelling, but the gate uses the raw full-res scan; not masked post hoc). Post-hoc, NOT gated: excluding the intake-removed fragments leaves max 0.915, set by 178 see-through interior points just outside the conservative window mask M1 (qa/posthoc_sensitivity.json). Unmasked p95 is driven by the window interior (M1 inside p95 2.228). | (a) human ACCEPT-BAND with these causes; (b) next QA run: pre-register a mask for intake-removed disconnected fragments and a less conservative window-interior mask, declared before results; (c) rescan with the windows matted and the fragment cleaned. No geometry change indicated. |
| whole part CAD->scan observable (p95 0.331 > 0.30, max 1.920 > 0.80; masked p95 0.190 / max 1.261) | Observability removed only 0.02 % (everything is in line of sight); the excess is CAD surface with no scan behind it: transparent window faces (M5 inside p95 1.084), scan hole edges (M4 inside p95 0.907), the unscanned wire slot (cluster, max 1.511) and unscanned pocket ceiling corners (max 1.261, remains after masks). | rescan with window matting and pocket/slot coverage; caliper the slot roof and pocket depth; or human ACCEPT-BAND. |
| Z-LENS (masked scan->CAD p95 0.589 / max 0.915, CAD->scan p95 0.518 / max 0.856; unmasked 1.394/2.983 and 0.728/2.018) | Transparency: 80 % of masked points >0.30 are in the 0.3-1.3 mm window/see-through layer where window face and interior cannot be separated; frame/rib p95 0.297, cup outer skin p95 0.246 / max 0.803, cup-body junction p95 0.290 (qa/lens_breakdown.json). | rescan with matted windows or depth-gauge the recess; human ACCEPT-BAND for the window zone. |
| Z-POCKET CAD->scan (max 1.261 masked and unmasked; unmasked p95 0.425, masked p95 0.234) | Pocket ceiling corners / back walls unscanned (open loops at z -3.7..-1.4); scanned pocket surfaces agree (Z-POCKET scan->CAD p95 0.170 / max 0.719). | caliper pocket width/depth, or rescan the pockets; human ACCEPT-BAND. |

Missed band(s): `scan_to_cad:masked: p95 0.225 max 1.936 vs 0.3/0.8`; `cad_to_scan_observable: p95 0.331 max 1.920 vs 0.3/0.8`; `zone:Z-LENS lens frame rib and windows:scan_to_cad: p95 0.589 max 0.915 vs 0.3/0.8`; `zone:Z-LENS lens frame rib and windows:cad_to_scan: p95 0.518 max 0.856 vs 0.3/0.8`; `zone:Z-POCKET shelf underside pockets:cad_to_scan: p95 0.234 max 1.261 vs 0.3/0.8`.

## 10. Named checks

| check | stage | ran | result | note |
|---|---|---|---|---|
| CHK-ACHIEVABLE | verify (`qa/gate.json#checks`) | yes | n/a | Tier-1 not run (no calipers, DECISIONS.md MEASUREMENTS); nothing to attribute. |
| CHK-CIRCULAR | verify (`qa/gate.json#checks`) | yes | pass | Graded after QA's own ICP (qa/registration.json, T_refine QA-only, never written back); datum re-derived by QA code on the raw scan; no expected value taken from params.json or the builder. The builder's 'self-check' in MODELING_PLAN.md (working mesh, 60k/40k samples) is a consistency check, not independent evidence, and was not used. |
| CHK-CLUSTER | verify (`qa/gate.json#checks`) | yes | pass | 4 scan->CAD over-band clusters; unexplained: [] |
| CHK-ENUM | verify (`qa/gate.json#checks`) | yes | finding | E01-E13 all present in the CAD (overlays: box, rounds, nose cup, lens frame + rib + 2 recessed windows, seam groove, cap, shelf, 3 pockets, rails, tabs, wire slot, 2 bottom ramps). E15 correctly not modelled. Finding: E14 (+Y tab blob) stays an OPEN QUESTION - not modelled and masked (M2); if it is a real detent the CAD lacks it. All scan->CAD over-band clusters reviewed: no missing moulded feature found (clusters = window interior, a disconnected scan fragment, the E14 blob). |
| CHK-FILLET | verify (`qa/gate.json#checks`) | yes | pass | export_check.json / fillets.json: 9 of 9 fillets OK, target == used (2.072, 2.137, 7.758, 2.072, 0.53, 1.74, 2.137, 1.107, 6.033 mm); no REDUCED/FAILED. Declared: nose_tip_R propagated to the whole 5-edge lens outline (MODELING_PLAN as-built); window_corner_R and nose_top_R are assumed values (plan §6). |
| CHK-INDEP | verify (`qa/gate.json#checks`) | yes | pass | Fresh context; see independence. |
| CHK-LIKE4LIKE | verify (`qa/gate.json#checks`) | yes | n/a | Iteration 1; no _itN_SUPERSEDED/ to compare against. |
| CHK-MASK | verify (`qa/gate.json#checks`) | yes | finding | zone Z-TAB tabs and guide rails scan_to_cad |
| CHK-OVERLAY | verify (`qa/gate.json#checks`) | yes | pass | every panel shows scan |
| CHK-PATCHWORK | verify (`qa/gate.json#checks`) | yes | pass | QA census (qa/step_check.json): 106 faces = 83 plane / 17 cylinder / 6 B-spline; analytic area share 98.95 %. The 6 B-spline faces are fillet-corner patches the plan anticipated (lens-outline round x cup round). No thousands of facets. grep of build/model.py: no loft/ruled/Polyline/spline/sweep/slice stack. |
| PHOTO-PLAUSIBILITY | verify (`qa/gate.json#checks`) | yes | pass | photo_1..photo_5 walked (low-res, no scale): clear cover over black body, lens nose with two clear windows split by a black rib (photo_2, photo_4), side tab flanges (photo_1, 3, 4), black rear end with harness leaving at the bottom centre (photo_5 = wire slot), flat top. All present in the CAD. Pockets (E09) and ramps (E13) are not resolvable in the photos but are in the scan; E14 not resolvable. No CAD feature is absent from both photos and scan (nothing hallucinated). |
| CHK-PUBLISH | deliver (preflight) | yes | pass | verdict BAND_NOT_MET |
| CHK-SUPERSEDED | deliver (preflight) | yes | pass | all earlier iterations kept intact |
| inputs_unchanged | deliver (preflight) | yes | pass | 6 input file(s) unchanged |
| hash_frozen | deliver (preflight) | yes | pass | every build/ STEP matches hash_frozen |
| regime_declared | deliver (preflight) | yes | pass | regime 'baseline-skill' |

## 11. Declared limitations (each with its re-run trigger)

| id | limitation | re-run trigger | evidence |
|---|---|---|---|
| L1 | Tier-1 not run: no Tier-1 (no calipers run) because this is a scan-only job; no dimension is caliper-verified. | any caliper reading: fill input/MEASUREMENTS.md from the request in intake/MEASUREMENTS.md, rehash, re-run intake scale check and verify with Tier-1 | DECISIONS.md MEASUREMENTS; qa/gate.json#tier1 |
| L2 | Absolute scale not caliper-verified: CHK-SCALE flagged at intake, units assumed mm, no scale applied. | any caliper reading of an envelope dimension (overall length, width over tabs, thickness) | intake/alignment.json#checks |
| L3 | Mask-dependent pass: zone Z-TAB passes scan to CAD only with mask M2 on the E14 blob on the +Y tab (masked max 0.3318 mm, unmasked max 1.5396 mm). The blob was not modelled; whether it is debris or a real detent is an open question. | owner confirms what E14 is (close-up photo or physical check): debris keeps M2; a real feature means REVISE (model it) and re-verify | qa/masks.json; intake/INTAKE_CARD.md E14 |
| L4 | Transparent lens windows: the scanner saw through them, so the lens numbers depend on masks M1 (interior seen through the window, scan side) and M5 (window faces, CAD side); the window recess depth cannot be verified from this scan. The lens zone Z-LENS misses the band even after masking. | rescan with the windows matted (developer spray) or a depth-gauge reading of the window recess | qa/masks.json; qa/lens_breakdown.json; qa/gate.json#band_fails |
| L5 | Unscanned geometry: the wire-slot roof and walls and the pocket ceiling corners were never scanned; CAD there is scan-extent provenance. Mask M3 (slot roof) selected no points and was deliberately not moved after results were seen, so the slot appears as an unmasked CAD to scan cluster; zone Z-POCKET misses on CAD to scan max. | slot roof height and pocket depth by caliper or depth rod, or a rescan that covers the slot and pockets | qa/masks.json; qa/review.json#cluster_explanations |
| L6 | Datum audit re-derived with QA's own plane-origin code because datum_audit.py cannot express origin.xy_planes; within the reference band (0.0748 deg, 0.0336 mm) but sensitive to the side-wall crop and the origin rule. Report-only. | datum_audit.py gains plane-origin support, or the datum is redone | qa/datum_audit.json#sensitivity_variants |
| L7 | Validity note: the B-rep is one valid closed solid with no naked edges in both frames, but the fine QA tessellation has one zero-area triangle at a B-spline fillet-corner patch; watertight after dropping it; no short edges or sliver faces in the B-rep. | any rebuild: re-run step_check and the tessellation probe | qa/tess_watertight_probe.json; qa/brep_near_probe.json |
| L8 | ICP converged on the last permitted iteration of the default cap (60 iterations); a check with a doubled cap converged at the same iteration with the same correction. | none required; re-check if the STEP or the masks change | qa/registration_cap120_check.json |
| L9 | Scan fragments that intake removed before modelling are still graded by the gate: a detached scan piece outside the -Y wall sets the scan to CAD masked max; it was not masked after the fact. | a verify mask type for intake-removed fragments declared before grading (skill change), then re-verify | qa/review.json#cluster_explanations; qa/posthoc_sensitivity.json |

## 12. Assumptions and invented geometry

Parameters not measured on the scan or by caliper (source tag from `measure/params.json`):

| parameter | value | source | evidence |
|---|---|---|---|
| `nose_top_R` | 2.072 | assumed | same as cover_top_R |
| `tab_blob_not_modelled` | 0 | assumed | measure/figures/measurements.json#nub_top_z_pos |
| `window_corner_R` | 6.033 | assumed | nose_cup_R - (nose_half_w - window_y_out) |

- Window outline round is concentric with the lens-cup round (constant side frame). _(source: assumed; measure/params.json#window_corner_R)_
- Lens-cup top-edge round equals the cover top-edge round; the rear cap bottom round equals the cover bottom round. _(source: assumed; build/MODELING_PLAN.md section 6)_
- Small vertical-edge and pocket-corner rounds are modelled sharp; the bottom parting lip and a shallow dent along the -Y top edge are not modelled. _(source: assumed; measure/params.json#simplifications)_
- The two moulded pieces (clear cover and black body) are one fused envelope solid; no internal geometry. _(source: assumed; intake/INTAKE_CARD.md section 8)_

## 13. Claim boundary — what this result is NOT

- **Not fit for:** tooling, moulds or fit-critical manufacture of the bumper interface until the tabs, rails and envelope are calipered
- **Not fit for:** optical design of the lens windows (transparent surfaces not verified)
- **Not fit for:** the wire-slot roof and pocket depths (not scanned)
- Fit for: packaging and clearance studies of the sensor envelope in the bumper assembly
- Fit for: designing a mating pocket or holder, with calipers on the tabs and rails before release
- The verdict covers only the Tier-1, deviation and named-check gates above, under the **baseline-skill** regime.

- Verify's own claim boundary (`qa/gate.json#claim_boundary`): BAND_NOT_MET under baseline-skill plastic (p95 0.30 / max 0.80). The CAD matches the opaque, scanned envelope closely (Z-TOP scan->CAD max 0.307, Z-TAB masked max 0.332, R-bottom max 0.561, R-cover masked CAD->scan max 0.564, scan->CAD p95 0.225 masked), but it is NOT verified: at the lens windows (transparent), the wire-slot roof and pocket ceilings (unscanned), for E14 (open question) or in absolute scale (no calipers). Not fit for tooling, mould or fit-critical manufacture of the bumper interface until calipered; delivery requires a recorded human ACCEPT-BAND.

## 14. Human acceptance of the band miss

Accepted by **Ikbal (owner, decision card)** on 2026-09-30 (`DECISIONS.md`, ACCEPT-BAND): Accept and deliver: accepts scan_to_cad:masked, cad_to_scan_observable, zone:Z-LENS and zone:Z-POCKET band misses, gate 78728df9af7e (created 2026-09-30T15:48:31+00:00); causes are lens transparency, a detached scan fragment and unscanned slot/pocket corners, not modelled geometry.. Record: `decisions/accept_band.md` (sha256 `73e905e48d844d259f142acfb8cfaa50cc923aa76d04050f809eb8e34d635fee`).

## 15. Reproduction

```
cd build && python3 model.py --params ../measure/params.json --alignment ../intake/alignment.json --out . --part cliff_bumper_sensor --scripts <stl-re-rebuild-build123d>/scripts
```

Fresh-process rebuild check (`deliver/repro.json`): reproducible **yes**; method 2 fresh subprocess rebuild(s) of build/model.py in a scratch copy; STEP re-imported; solids, faces, surface census, volume, bbox compared (raw hash reported, not required); environment python: 3.11.15; platform: Linux-6.18.44-fc-v50-x86_64-with-glibc2.39; build123d: 0.13.0; OCP: 8.0.1.0; numpy: 2.4.6.

| file | volume mm³ | |Δ volume| | max |Δ bbox| | faces equal | identical | raw sha equal |
|---|---|---|---|---|---|---|
| cliff_bumper_sensor.step | 7736.3821 | 0 | 0 | yes | yes | no |
| cliff_bumper_sensor_datum.step | 7736.3821 | 0 | 0 | yes | yes | no |

_Raw STEP hashes differ between runs because STEP headers carry a timestamp; the geometry is compared._

## 16. Provenance of every number in this file

| file | sha256 |
|---|---|
| `qa/gate.json` | 78728df9af7ef9b3c47d3cd741cb22f8fb8b75fbe136cf933c3ff2ba8d190c47 |
| `measure/params.json` | a4918f594fa0f117b850bd62ec7a7ae9aa6edc23d166f6eeb3b7e6d7cadbec12 |
| `build/export_check.json` | a71fc113e930254d80eeaf7485c97da009f1b0dea800f695f7d34f1ca0521aac |
| `intake/alignment.json` | 4ab4f99084d33f5a7e041698841d6adf885fb423bb8d92d36f85ceebe1552bd7 |
| `deliver/repro.json` | cf3fd71ecc2c4e753c6f0033d50328c79da879bc3e4170727f2dd3e3598cc3d2 |
| `deliver/limitations.json` | b737a8e429bbdd3a070db5c7eac81b23be2b25558297baa2f65977590b1f397b |

Generated by `stl-re-deliver/scripts/make_readme.py`. Do not edit numbers by hand; fix the JSON and re-render.
