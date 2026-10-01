# dreame_brush_core — STL → STEP reverse-engineering delivery

**Verdict: `BAND_NOT_MET`** (from `qa/gate.json`; full reasoning in `qa/VERDICT.md`).  
**Band regime:** baseline-skill — source `baseline/skills/stl2step-build123d/SKILL.md:87`.  
**Iteration:** 2 of 3 (earlier iterations kept: `_it1_SUPERSEDED/`).  
**Verification independence (CHK-INDEP):** pass — separate agent context, QA-owned scripts; organisational independence not claimed (same orchestrator session)  

> **A deviation band was NOT met.** Delivered only under the recorded human acceptance below (by owner (Ikbal), chat answer, 2026-10-01, record `decisions/accept_band_it2.md`).

## 1. The part

_No reference photo was supplied with the scan._

Main brush-roll core of a Dreame robot vacuum (scanned with its bristles in place): a twisted constant-profile core with four T-slots, two pairs of grooves and two helical rows of tuft holes, a four-blade pinwheel drive dog and two hub discs at the drive end, and a counterbored idler bore at the other end.

## 2. Deliverables

| file | frame | solids | valid | closed | faces | volume mm³ | bbox mm |
|---|---|---|---|---|---|---|---|
| `build/dreame_brush_core_datum.step` | datum | 1 | yes | yes | 200 | 28731.5452 | max: [16.436, 16.436, 163.284]; min: [-16.436, -16.436, -6.471]; size: [32.872, 32.872, 169.755] |
| `build/dreame_brush_core.step` | scan | 1 | yes | yes | 200 | 28731.5452 | max: [14.6356, 49.2708, -99.1868]; min: [-18.3409, -64.3179, -253.8243]; size: [32.9766, 113.5887, 154.6375] |

Source of the table: `build/export_check.json`. The editable design intent is `build/model.py` driven by `measure/params.json`.

## 3. Method

1. Intake: sha256 of the owner's scan, largest body kept, scanner table under the hub removed, noise floor on the hub drive face and the hub cylinder.
2. Datum: hub drive face as primary (z = 0, +Z into the core), hub cylinder axis as origin, four-fold blade phase as clock; core-axis tilt checked separately on the core lands over the full length.
3. Measure: twist rate by profile-entropy minimisation and slab phase correlation, untwisted profile fits (slots, grooves, base circle), tuft rows by occupancy blobs and FFT along z, hub and idler ends by axial and radial point sets.
4. Rebuild: one profile sketch extruded with a linear twist, idler end trimmed by a revolved envelope, revolved bore cut, tuft holes as fused cut tools, hub from a blade sketch patterned four times plus revolved discs; one fused solid exported in the datum and scan frames.
5. Verify (separate agent, own ICP): two-way deviation with named masks, observability split, zones; iteration 1 REVISE (missing slot undercut), iteration 2 BAND_NOT_MET accepted by the owner.

## 4. Coordinate frames

Two STEP files carry the same solid (SYNTHESIS D14): the **datum frame** (design frame, below) and the **scan frame** (the original STL coordinates; the CAD overlays the raw scan).

| element | definition | fit residual (rms / max mm) | why |
|---|---|---|---|
| origin | hub cylinder r15.2 axis ∩ hub drive face | — | — |
| primary (plane) | hub drive face (pinwheel blades, core-facing side) | 0.0449 / 0.1063 | functional drive face of the brush roll: the pinwheel drive dog seats against it; flat, clean, fully scanned; +Z points from the hub into the bristle core |
| secondary (axis) | hub cylinder r15.2 | 0.019 / 0.1383 | clean full-circle cylinder of the drive-end hub |
| clock | fourier_mass: pinwheel drive-dog blades (angle -37.6524°) | — | — |

Measured tilt: 0.0524° (common slope, per-feature intercept, 6 stations over 1 feature(s), z -2.850..-2.100 vs frame Z). Scale factor applied: 1. Scan noise floor: 0.0449 mm (rms of RANSAC+SVD plane on hub drive face (pinwheel blades, core-facing side) (2181 faces)).

Scan → datum matrix (row-major, `intake/alignment.json#matrix_4x4`); the scan-frame STEP uses its inverse:

```
 0.996583   0.082356  -0.006308   4.405199
-0.072087   0.829961  -0.553143  -93.496749
-0.040319   0.551708   0.833062   225.255873
 0.000000   0.000000   0.000000   1.000000
```

## 5. Parameters

Sources: assumed 4, scan 36 (total 40). Rendered from `measure/params.json`; never edited by hand.

| name | value | unit | measured | rule | source | ± mm | critical | evidence |
|---|---|---|---|---|---|---|---|---|
| `blade_arcB_R` | 4.634 | mm | 4.6477 | round-within-noise | scan | 0.062 | no | measure/figures/m07_blade_fit.json |
| `blade_count` | 4 | count | 4 | keep-measured | scan | 0 | no | measure/figures/pc_blades.json |
| `blade_edge_y` | 1.141 | mm | 1.1411 | round-within-noise | scan | 0.045 | yes | measure/figures/m07_blade_fit.json |
| `blade_outer_r` | 15.125 | mm | 15.1252 | round-within-noise | scan | 0.023 | yes | measure/figures/m07_blade_fit.json |
| `blade_top_z` | 0 | mm | -0.0268 | round-within-noise | scan | 0.045 | yes | measure/figures/m08_hub_axial.json |
| `blade_wall_x` | 0.652 | mm | [0.785, 0.519] | mean-of-n | scan | 0.133 | no | measure/figures/m07_blade_fit.json |
| `bore_bottom_z` | 158.17 | mm | — | assumed | assumed | 0 | no | measure/figures/m09_idler.json |
| `bore_r` | 4.281 | mm | 4.2813 | round-within-noise | scan | 0.1 | yes | measure/figures/m09_idler.json |
| `bristles` | 0 | count | — | assumed | assumed | 0 | no | intake/INTAKE_CARD.md#4 |
| `cbore_floor_z` | 161.989 | mm | 161.9893 | round-within-noise | scan | 0.045 | no | measure/figures/m09_idler.json |
| `cbore_r` | 5.925 | mm | 5.9254 | round-within-noise | scan | 0.045 | yes | measure/figures/m09_idler.json |
| `core_r_base` | 7.464 | mm | 7.4644 | round-within-noise | scan | 0.104 | yes | measure/figures/m03_profile_fit.json |
| `core_twist_deg_per_mm` | -1.5971 | deg | -1.5971 | round-within-noise | scan | 0.028 | yes | measure/figures/m01_twist.json |
| `core_z_end` | 163.284 | mm | 163.2839 | round-within-noise | scan | 0.045 | no | measure/figures/m09_idler.json |
| `core_z_start` | 0 | mm | 0 | keep-measured | scan | 0.045 | no | measure/figures/m05_ends_rz.png |
| `end_round_R` | 1.593 | mm | 1.593 | round-within-noise | scan | 0.065 | no | measure/figures/m10_end_round.json |
| `gap_floor_z` | -1.918 | mm | -1.9181 | round-within-noise | scan | 0.045 | yes | measure/figures/m08_hub_axial.json |
| `groove_big_R` | 3.654 | mm | [3.269, 4.04] | mean-of-n | scan | 0.4 | no | measure/figures/m03_profile_fit.json |
| `groove_big_bottom_r` | 6.266 | mm | [6.275, 6.256] | mean-of-n | scan | 0.2 | no | measure/figures/m03_profile_fit.json |
| `groove_big_theta_deg` | [135.62, 315.64] | deg | [135.62, 315.64] | keep-measured | scan | 0.05 | no | measure/figures/m03_profile_fit.json |
| `groove_small_R` | 0.906 | mm | [0.872, 0.94] | mean-of-n | scan | 0.04 | no | measure/figures/m03_profile_fit.json |
| `groove_small_centre_rho` | 7.838 | mm | [7.835, 7.84] | mean-of-n | scan | 0.03 | no | measure/figures/m03_profile_fit.json |
| `groove_small_theta_deg` | [59.96, 240.02] | deg | [59.96, 240.02] | keep-measured | scan | 0.02 | no | measure/figures/m03_profile_fit.json |
| `hub_disc_r` | 15.204 | mm | 15.2041 | round-within-noise | scan | 0.019 | yes | measure/figures/m08_hub_axial.json |
| `hub_inner_r` | 4.96 | mm | 4.9603 | round-within-noise | scan | 0.08 | no | measure/figures/m08_hub_axial.json |
| `hub_step_z` | -3.215 | mm | -3.2153 | round-within-noise | scan | 0.12 | yes | measure/figures/m08_hub_axial.json |
| `rim_end_z` | -6.471 | mm | — | assumed | assumed | 0 | no | measure/figures/m08_hub_axial.json |
| `rim_r` | 16.436 | mm | 16.4361 | round-within-noise | scan | 0.06 | yes | measure/figures/m08_hub_axial.json |
| `slot_bottom_r` | 4.872 | mm | [4.871, 4.879, 4.87, 4.867] | mean-of-n | scan | 0.045 | no | measure/figures/m03_profile_fit.json |
| `slot_count` | 4 | count | 4 | keep-measured | scan | 0 | no | measure/figures/m03_profile_fit.json |
| `slot_foot_halfwidth` | 1.173 | mm | [1.119, 1.227] | mean-of-n | scan | 0.06 | no | measure/figures/m12_slot_foot.json |
| `slot_neck_end_r` | 6 | mm | 6 | round-within-noise | scan | 0.05 | no | measure/figures/m13_slot_flare.json |
| `slot_theta0_deg` | 1.107 | deg | [1.21, 1.07, 0.994, 1.153] | symmetry | scan | 0.023 | no | measure/figures/m03_profile_fit.json |
| `slot_width` | 1.235 | mm | [1.236, 1.255, 1.218, 1.233] | mean-of-n | scan | 0.036 | no | measure/figures/m03_profile_fit.json |
| `tuft_count_per_row` | 27 | count | [27, 27] | keep-measured | scan | 0 | no | measure/figures/m11_tuft_fft.json |
| `tuft_hole_d` | 2 | mm | [2.015, 1.98] | round-within-noise | scan | 0.05 | no | measure/figures/m04_tufts.json |
| `tuft_hole_depth` | 2.5 | mm | — | assumed | assumed | 0 | no | intake/INTAKE_CARD.md#3 |
| `tuft_pitch` | 4.899 | mm | [4.9025, 4.8954] | mean-of-n | scan | 0.01 | no | measure/figures/m04_tufts.json |
| `tuft_row_theta_deg` | [35.83, 215.83] | deg | [37.11, 214.56] | symmetry | scan | 0.17 | no | measure/figures/m04_tufts.json |
| `tuft_z0` | 3.295 | mm | [3.172, 3.418] | symmetry | scan | 0.1 | no | measure/figures/m04_tufts.json |

## 6. Model tree (design intent)

The STEP is a neutral B-Rep; it carries no feature history. The editable design intent is `build/model.py` driven by `measure/params.json`, and the ordered feature plan is `build/MODELING_PLAN.md`.

| id | feature | params |
|---|---|---|
| F01 | twisted core profile (base circle, 4 T-slots, 2+2 grooves) | [core_r_base, core_twist_deg_per_mm, slot_width, slot_neck_end_r, slot_foot_halfwidth, slot_bottom_r, groove_small_R, groove_big_R] |
| F02 | idler end round (revolved envelope) | [end_round_R, core_z_end] |
| F03 | idler counterbore and bore | [cbore_r, cbore_floor_z, bore_r, bore_bottom_z] |
| F04 | tuft holes, 2 rows | [tuft_row_theta_deg, tuft_z0, tuft_pitch, tuft_count_per_row, tuft_hole_d, tuft_hole_depth] |
| F05-F07 | hub: inner disc, 4 pinwheel blades, disc and rim | [hub_inner_r, blade_edge_y, blade_outer_r, blade_arcB_R, blade_wall_x, gap_floor_z, hub_disc_r, hub_step_z, rim_r, rim_end_z] |

## 7. Tier-1 — caliper dims re-measured on the STEP

**Tier-1 not run: no caliper dimensions exist.** Every dimension is scan authority (or operator spec); see the source column in §5. Absent is not passed.

## 8. Deviation gate (scan ↔ CAD)

Regime **baseline-skill** (`baseline/skills/stl2step-build123d/SKILL.md:87`); bands: p95_mm: 0.3; max_mm: 0.8; tier1_abs_mm: —; interface_max_mm: —.

Registration: point-to-point ICP, CAD samples -> scan samples, masked correspondences (B02 q20_tier2.py), iterations 94/1000, converged yes, correction 0.4349° / 0.0454 mm.  
Unobservable CAD fraction: 0.0667.

| direction | n | rms | p50 | p95 | p99 | max | sampling | source |
|---|---|---|---|---|---|---|---|---|
| scan → CAD **unmasked** | 210548 | 5.5564 | 3.1155 | 10.4493 | 11.3781 | 15.6138 | — | `qa/gate.json#deviation` |
| scan → CAD (masked) | 78181 | 0.1032 | 0.0481 | 0.213 | 0.3471 | 1.1771 | — | `qa/gate.json#deviation` |
| CAD → scan **unmasked** (all) | 300000 | 1.1094 | 0.0748 | 2.3183 | 5.2233 | 6.691 | — | `qa/gate.json#deviation` |
| CAD → scan (masked) | 237843 | 0.3484 | 0.0525 | 0.6604 | 1.8535 | 2.655 | — | `qa/gate.json#deviation` |
| CAD → scan (observable) | 15209 | 0.263 | 0.0478 | 0.4149 | 1.2158 | 2.6361 | — | `qa/gate.json#deviation` |

### Gate results (what the verdict was graded on)

| item | band | measured | result |
|---|---|---|---|
| scan_to_cad:masked | p95 ≤0.3 / max ≤0.8 | p95 0.213 max 1.1771 (n 78181) | FAIL |
| cad_to_scan_observable | p95 ≤0.3 / max ≤0.8 | p95 0.4149 max 2.6361 (n 15209) | FAIL |
| zone:Z1 drive dog (blades + gap floor):scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.2249 max 0.8526 (n 4486) | FAIL |
| zone:Z1 drive dog (blades + gap floor):cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 0.2032 max 0.7345 (n 17459) | PASS |
| zone:Z2 hub discs r15.20 r16.44:scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.3093 max 0.8162 (n 6451) | FAIL |
| zone:Z2 hub discs r15.20 r16.44:cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 0.1902 max 0.462 (n 10975) | PASS |
| zone:Z3 idler counterbore and bore:scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.2882 max 0.8649 (n 1969) | FAIL |
| zone:Z3 idler counterbore and bore:cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 1.3639 max 2.5313 (n 5785) | FAIL |
| zone:Z4 core profile (twisted, slots, grooves):scan_to_cad | p95 ≤0.3 / max ≤0.8 | p95 0.1957 max 1.1771 (n 64228) | FAIL |
| zone:Z4 core profile (twisted, slots, grooves):cad_to_scan | p95 ≤0.3 / max ≤0.8 | p95 0.7274 max 2.655 (n 204865) | FAIL |

### Per zone (unmasked and masked side by side)

| zone | kind | direction | unmasked | masked | unmasked stats | masked stats | note |
|---|---|---|---|---|---|---|---|
| B core z 0-80 | region | scan_to_cad | reported | reported | n 114552 · p95 10.6823 · max 12.9096 | n 33113 · p95 0.1901 · max 1.1771 | z-band bucket |
| B core z 0-80 | region | cad_to_scan | reported | reported | n 131336 · p95 1.3088 · max 2.6038 | n 115500 · p95 0.4426 · max 1.5728 | z-band bucket |
| B core z 80-140 | region | scan_to_cad | reported | reported | n 64865 · p95 10.0577 · max 13.3131 | n 22876 · p95 0.1759 · max 0.5276 | z-band bucket |
| B core z 80-140 | region | cad_to_scan | reported | reported | n 92245 · p95 1.9971 · max 2.6727 | n 69038 · p95 1.0603 · max 2.5196 | z-band bucket |
| B hub z<0 | region | scan_to_cad | reported | reported | n 18451 · p95 11.3828 · max 15.6138 | n 10497 · p95 0.2888 · max 0.8526 | z-band bucket |
| B hub z<0 | region | cad_to_scan | reported | reported | n 38603 · p95 5.521 · max 6.691 | n 22139 · p95 0.2087 · max 0.7345 | z-band bucket |
| B idler end z>140 | region | scan_to_cad | reported | reported | n 12680 · p95 5.5686 · max 10.432 | n 11695 · p95 0.2503 · max 0.8649 | z-band bucket |
| B idler end z>140 | region | cad_to_scan | reported | reported | n 37816 · p95 2.0103 · max 3.6227 | n 31166 · p95 1.4192 · max 2.655 | z-band bucket |
| I1 rim end face (unscanned) | interior | cad_to_scan | reported | reported | n 16464 · p95 5.9689 · max 6.691 | n 0 | assumed, reported only |
| I2 idler bore bottom (unscanned) | interior | cad_to_scan | reported | reported | n 1178 · p95 2.9442 · max 3.6227 | n 0 | assumed, reported only |
| N1 hub recess beside slot entry (named local miss, not masked) | region | scan_to_cad | reported | reported | n 172 · p95 1.0472 · max 1.1771 | n 172 · p95 1.0472 · max 1.1771 | DECISIONS.md 2026-10-01: not modelled, not masked; reported as a named local miss (it1 cluster 3) |
| N1 hub recess beside slot entry (named local miss, not masked) | region | cad_to_scan | reported | reported | n 143 · p95 0.4659 · max 0.5225 | n 143 · p95 0.4659 · max 0.5225 | DECISIONS.md 2026-10-01: not modelled, not masked; reported as a named local miss (it1 cluster 3) |
| Z1 drive dog (blades + gap floor) | whole | scan_to_cad | FAIL | FAIL | n 4486 · p95 0.2249 · max 0.8526 | n 4486 · p95 0.2249 · max 0.8526 | functional (INTAKE_CARD §4 Z1, band = regime); kind 'whole' gates it at the regime p95/max because baseline-skill has no interface_max |
| Z1 drive dog (blades + gap floor) | whole | cad_to_scan | PASS | PASS | n 17459 · p95 0.2032 · max 0.7345 | n 17459 · p95 0.2032 · max 0.7345 | functional (INTAKE_CARD §4 Z1, band = regime); kind 'whole' gates it at the regime p95/max because baseline-skill has no interface_max |
| Z2 hub discs r15.20 r16.44 | whole | scan_to_cad | FAIL | FAIL | n 6451 · p95 0.3093 · max 0.8162 | n 6451 · p95 0.3093 · max 0.8162 | functional (INTAKE_CARD §4 Z2, band = regime) |
| Z2 hub discs r15.20 r16.44 | whole | cad_to_scan | PASS | PASS | n 10975 · p95 0.1902 · max 0.462 | n 10975 · p95 0.1902 · max 0.462 | functional (INTAKE_CARD §4 Z2, band = regime) |
| Z3 idler counterbore and bore | whole | scan_to_cad | FAIL | FAIL | n 1992 · p95 0.3028 · max 0.8649 | n 1969 · p95 0.2882 · max 0.8649 | functional (INTAKE_CARD §4 Z3, band = regime) |
| Z3 idler counterbore and bore | whole | cad_to_scan | FAIL | FAIL | n 6989 · p95 2.2085 · max 3.6227 | n 5785 · p95 1.3639 · max 2.5313 | functional (INTAKE_CARD §4 Z3, band = regime) |
| Z4 core profile (twisted, slots, grooves) | whole | scan_to_cad | FAIL | FAIL | n 67523 · p95 0.2128 · max 1.1771 | n 64228 · p95 0.1957 · max 1.1771 | functional (INTAKE_CARD §4 Z4, band = regime); tuft holes inside it are masked by M3 |
| Z4 core profile (twisted, slots, grooves) | whole | cad_to_scan | FAIL | FAIL | n 250558 · p95 1.7629 · max 3.6227 | n 204865 · p95 0.7274 · max 2.655 | functional (INTAKE_CARD §4 Z4, band = regime); tuft holes inside it are masked by M3 |
| Z5 bristle zone | region | scan_to_cad | reported | reported | n 121100 · p95 10.7035 · max 13.3131 | n 0 | soft, excluded from gate (INTAKE_CARD §4 Z5); reported only |
| Z5 bristle zone | region | cad_to_scan | reported | reported | n 0 | n 0 | soft, excluded from gate (INTAKE_CARD §4 Z5); reported only |

### Masks (masked and unmasked are both shown above)

| mask | direction | why | fraction removed | stats inside |
|---|---|---|---|---|
| M1 bristle tufts and loose bristle fragments | scan_to_cad | soft feature, not modelled: two helical rows of bristle tufts (and loose bristle bits) = scan material radially outside the Ø14.93 core (r 7.465); no rigid feature of the part lies at r>7.6 for z>0 (INTAKE_CARD §1, §4 Z5, §5 #6) | 0.5752 | n: 121100; rms: 7.0808; mean: 6.3861; p50: 6.5903; p95: 10.7035; p99: 11.3714; max: 13.3131 |
| M2 scanner table remnants | scan_to_cad | scanner turntable surface under the hub rim (the part stood on its drive end); not part of the part; the rim r16.44 is the largest radius of the part | 0.028 | n: 5891; rms: 6.5262; mean: 5.5788; p50: 5.0693; p95: 12.3378; p99: 13.9169; max: 15.0341 |
| M2b scanner table fringe upturn | scan_to_cad | same table remnant curling up to z -3.5 at theta 210-330 deg, r 18.5-32; the part has no material beyond the rim r16.44 below the hub disc; the scan shows an empty radial gap r 17.5-19.5 between rim surface and fringe, so r>=18 cannot hold rim surface | 0.0098 | n: 2063; rms: 9.2543; mean: 8.7037; p50: 8.263; p95: 14.132; p99: 15.0364; max: 15.6138 |
| M3 tuft holes (bristle-filled) | scan_to_cad | 54 radial tuft holes Ø2.0 are filled with bristle tufts: scan points there are bristle roots (soft), and the CAD hole walls/bottoms (depth assumed) were never seen by the scanner; region = hole cylinder +0.25 mm, located from the 54 Ø2 hole-bottom faces of the frozen STEP and cross-checked against scan tuft roots (52 scan clusters, median offset 1.05 mm = tuft lean) | 0.0109 | n: 2289; rms: 0.0987; mean: 0.0692; p50: 0.0472; p95: 0.2132; p99: 0.3542; max: 0.4664 |
| M6s slot occupants (scan side) | scan_to_cad | declared slot-occupant occlusion (DECISIONS.md 2026-10-01 OTHER, before the it2 re-grade): material lodged in the slots (ragged surface at r 6-7.2: hair/bristle/debris) is not part of the rigid core, and where it hides the slot floor the CAD slot walls/foot/floor were never seen. Located from the scan per slot and 1 mm z-bin; bins without an occupant are not masked | 0.0049 | n: 1024; rms: 0.3586; mean: 0.3204; p50: 0.2961; p95: 0.5934; p99: 0.6421; max: 0.7121 |
| M3 tuft holes (bristle-filled) | cad_to_scan | 54 radial tuft holes Ø2.0 are filled with bristle tufts: scan points there are bristle roots (soft), and the CAD hole walls/bottoms (depth assumed) were never seen by the scanner; region = hole cylinder +0.25 mm, located from the 54 Ø2 hole-bottom faces of the frozen STEP and cross-checked against scan tuft roots (52 scan clusters, median offset 1.05 mm = tuft lean) | 0.0776 | n: 23268; rms: 1.3861; mean: 1.137; p50: 1.1578; p95: 2.418; p99: 2.5424; max: 2.6727 |
| M4 rim end face (assumed, rested on table) | cad_to_scan | the hub rim end face z -6.47 rested on the scanner table and was never scanned; the CAD closes it flat (assumed); its CAD->scan distance is a coverage fact, not a surface deviation | 0.0549 | n: 16464; rms: 3.9727; mean: 3.4765; p50: 4.3291; p95: 5.9689; p99: 6.4463; max: 6.691 |
| M5 idler bore bottom (assumed) | cad_to_scan | idler bore seen only to 3.8 mm depth; the flat bottom at the deepest seen z (158.17) is assumed geometry, never scanned | 0.0039 | n: 1178; rms: 1.794; mean: 1.5879; p50: 1.5785; p95: 2.9442; p99: 3.3163; max: 3.6227 |
| M6c slot occupants (CAD side, floor hidden) | cad_to_scan | declared slot-occupant occlusion (DECISIONS.md 2026-10-01 OTHER, before the it2 re-grade): material lodged in the slots (ragged surface at r 6-7.2: hair/bristle/debris) is not part of the rigid core, and where it hides the slot floor the CAD slot walls/foot/floor were never seen. Located from the scan per slot and 1 mm z-bin; bins without an occupant are not masked | 0.0708 | n: 21247; rms: 1.2275; mean: 1.0094; p50: 1.0709; p95: 2.1728; p99: 2.4172; max: 2.5469 |

### Mask sensitivity

| band | direction | stats | variant |
|---|---|---|---|
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 10.1049; max_over_by: 12.5131 | scan_to_cad | n: 199281; rms: 5.5202; mean: 3.9083; p50: 3.0364; p95: 10.4049; p99: 11.1969; max: 13.3131 | all masks except M1 bristle tufts and loose bristle fragments |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 3.0529; max_over_by: 14.2341 | scan_to_cad | n: 84072; rms: 1.7304; mean: 0.4563; p50: 0.0529; p95: 3.3529; p99: 9.411; max: 15.0341 | all masks except M2 scanner table remnants |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 14.8138 | scan_to_cad | n: 80244; rms: 1.4873; mean: 0.2923; p50: 0.0498; p95: 0.2694; p99: 9.6489; max: 15.6138 | all masks except M2b scanner table fringe upturn |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.3771 | scan_to_cad | n: 80470; rms: 0.1031; mean: 0.0703; p50: 0.048; p95: 0.213; p99: 0.3473; max: 1.1771 | all masks except M3 tuft holes (bristle-filled) |
| p95_band: 0.3; max_band: 0.8; pass: no; max_over_by: 0.3771 | scan_to_cad | n: 79205; rms: 0.1103; mean: 0.0736; p50: 0.0489; p95: 0.2253; p99: 0.4064; max: 1.1771 | all masks except M6s slot occupants (scan side) |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.128; max_over_by: 1.8727 | cad_to_scan | n: 261111; rms: 0.5308; mean: 0.2429; p50: 0.0596; p95: 1.428; p99: 2.3459; max: 2.6727 | all masks except M3 tuft holes (bristle-filled) |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 1.9586; max_over_by: 5.891 | cad_to_scan | n: 254307; rms: 1.0655; mean: 0.3704; p50: 0.0586; p95: 2.2586; p99: 5.344; max: 6.691 | all masks except M4 rim end face (assumed, rested on table) |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 0.3963; max_over_by: 2.8227 | cad_to_scan | n: 239021; rms: 0.3696; mean: 0.1625; p50: 0.0529; p95: 0.6963; p99: 2.0103; max: 3.6227 | all masks except M5 idler bore bottom (assumed) |
| p95_band: 0.3; max_band: 0.8; pass: no; p95_over_by: 0.991; max_over_by: 1.855 | cad_to_scan | n: 259090; rms: 0.4847; mean: 0.2254; p50: 0.0595; p95: 1.291; p99: 2.1849; max: 2.655 | all masks except M6c slot occupants (CAD side, floor hidden) |

### Over-band point clusters, scan → CAD (> 0.8 mm)

125157 points (0.5944 fraction) in 4 clusters ≥ 20 pts.

| # | n | centroid | r range | θ range (deg) | d max | explanation |
|---|---|---|---|---|---|---|
| 0 | 59806 | [5.17, -6.494, 63.853] | [8.14, 20.777] | [0, 360] | 13.3131 | bristle tuft row (soft), inside named mask M1. Clusters are computed on UNMASKED distances |
| 1 | 57658 | [-4.404, 6.897, 64.335] | [7.989, 19.626] | [0, 360] | 12.163 | second bristle tuft row (soft), inside M1 |
| 2 | 7649 | [-4.424, -3.776, -6.416] | [17.216, 32.049] | [0, 359.9] | 15.6138 | scanner table and its upturned fringe, inside M2/M2b |
| 3 | 35 | [1.998, 5.933, 1.268] | [5.721, 6.655] | [68, 76.3] | 1.1771 | NAMED LOCAL MISS, not an artefact: the hub recess beside one slot entry, NOT modelled and NOT masked by DECISIONS.md 2026-10-01. It sets the whole-part scan->CAD max (36 points over 0.8, max 1.177). It stays a band miss |

### Over-band point clusters, CAD → scan (> 0.8 mm)

50989 points (0.17 fraction) in 54 clusters ≥ 20 pts.

| # | n | centroid | r range | θ range (deg) | d max | explanation |
|---|---|---|---|---|---|---|
| 0 | 14089 | [-0.012, 0.054, -6.471] | [0.04, 15.582] | [0, 360] | 6.691 | **UNEXPLAINED** |
| 1 | 12730 | [3.545, 0.554, 136.858] | [0.114, 6.957] | [0, 360] | 3.6227 | **UNEXPLAINED** |
| 2 | 6699 | [-4.405, -0.976, 114.037] | [4.862, 6.869] | [120.2, 268.6] | 2.6727 | **UNEXPLAINED** |
| 3 | 2638 | [-3.834, -3.326, 144.368] | [4.862, 6.505] | [182.9, 262.3] | 2.4609 | **UNEXPLAINED** |
| 4 | 1836 | [3.02, -3.771, 88.423] | [4.862, 5.908] | [265.6, 345.5] | 1.5723 | **UNEXPLAINED** |
| 5 | 1231 | [-4.711, -1.399, 46.963] | [4.862, 5.792] | [168.3, 223.4] | 1.7627 | **UNEXPLAINED** |
| 6 | 1037 | [2.101, 4.602, 84.501] | [4.863, 6.804] | [26.9, 96.4] | 2.6019 | **UNEXPLAINED** |
| 7 | 297 | [5.013, -2.301, 37.594] | [4.964, 6.774] | [324.7, 347.1] | 2.4568 | **UNEXPLAINED** |
| 8 | 297 | [5.54, 0.628, 18.066] | [4.964, 6.816] | [0, 359.9] | 2.5429 | **UNEXPLAINED** |
| 9 | 289 | [-2.51, 5.069, 62.049] | [4.964, 6.709] | [105.3, 128] | 2.4791 | **UNEXPLAINED** |
| 10 | 287 | [5.407, 1.39, 13.122] | [4.964, 6.715] | [3.6, 26.1] | 2.516 | **UNEXPLAINED** |
| 11 | 286 | [5.353, -1.565, 32.667] | [4.964, 6.83] | [332.3, 354.7] | 2.4604 | **UNEXPLAINED** |

**Datum audit (report-only, QUESTIONS Q2):** angle 0.8883°, origin offset 0.0337 mm, point disagreement p95 0.3222 mm; reference band ≤0.3° / ≤0.15 mm (RE_SPEC.md:241) (OUTSIDE).

## 9. Band miss: where and what next

| region | cause | options |
|---|---|---|
| hub recess beside one slot entry (scan->CAD whole-part max, Z1/Z4 max) | declared unmodelled local feature (DECISIONS.md 2026-10-01): 36 scan points over 0.8 mm, max 1.177; asymmetric (1 of 4 entries), so feature vs damage cannot be told without a photo. Outside the recess the masked scan->CAD has 8 isolated points over 0.8 (max 0.969, no cluster >= 20 pts). Whole-part masked scan->CAD p95 0.213 passes | (a) human accepts the recess miss (ACCEPT-BAND); (b) photo of the drive end -> model it as a feature (it3) or declare damage; (c) full-res scan |
| slot foot/flare/floor coverage, CAD->scan observable (Z4, idler end) | COVERAGE, not geometry: 97.6 % of masked CAD->scan points over 0.8 lie in the slots; 8757 of them have no scan point within 0.3 mm / 1 mm z (only 22 do). These are undercut flare/foot surfaces and floor spans the decimated scan never saw, outside the M6c bins (M6c covers only bins where an occupant hides the floor). Diagnostic only: masked CAD->scan without slot interiors p95 0.206. The ray test counts many of these surfaces as line-of-sight observable | (a) full-res scan or a re-scan with cleaned slots aimed into the slots; (b) a declared coverage-gap mask located from the scan (intake decision, with leave-one-out); (c) human acceptance. More geometry cannot fix it |
| Z2 hub discs, Z3 idler bore/counterbore (small scan->CAD overs) | hub step/rim edge break (declared simplification, hub-step chamfer) and bore wall near the assumed bottom; 215 CAD->scan points over 0.8 at z >= 158 outside the slots (bore wall just above the masked bottom, counterbore/slot crossing) | optional it3: model the hub-step chamfer; bore depth needs a caliper or photo |

Missed band(s): `scan_to_cad:masked: p95 0.213 max 1.177 vs 0.3/0.8`; `cad_to_scan_observable: p95 0.415 max 2.636 vs 0.3/0.8`; `zone:Z1 drive dog (blades + gap floor):scan_to_cad: p95 0.225 max 0.853 vs 0.3/0.8`; `zone:Z2 hub discs r15.20 r16.44:scan_to_cad: p95 0.309 max 0.816 vs 0.3/0.8`; `zone:Z3 idler counterbore and bore:scan_to_cad: p95 0.288 max 0.865 vs 0.3/0.8`; `zone:Z3 idler counterbore and bore:cad_to_scan: p95 1.364 max 2.531 vs 0.3/0.8`; `zone:Z4 core profile (twisted, slots, grooves):scan_to_cad: p95 0.196 max 1.177 vs 0.3/0.8`; `zone:Z4 core profile (twisted, slots, grooves):cad_to_scan: p95 0.727 max 2.655 vs 0.3/0.8`.

## 10. Named checks

| check | stage | ran | result | note |
|---|---|---|---|---|
| CHK-ACHIEVABLE | verify (`qa/gate.json#checks`) | yes | n/a | no Tier-1 run (no calipers) |
| CHK-CIRCULAR | verify (`qa/gate.json#checks`) | yes | pass | graded after QA's own ICP; T_refine not written back; no expected values from params.json. M6 was located from the scan (qa/make_m6_slot_occupants.py); M3 holes come from the STEP's own hole-bottom faces, unchanged since it1 |
| CHK-CLUSTER | verify (`qa/gate.json#checks`) | yes | pass | 4 scan->CAD over-band clusters; unexplained: [] |
| CHK-ENUM | verify (`qa/gate.json#checks`) | yes | finding | T-slot foot now modelled (it1 finding closed: stacked section qa/overlays/slot_xsection_it2_qa.png). Still open: (a) the hub recess beside one slot entry is not modelled, by DECISIONS.md 2026-10-01; (b) DECISIONS.md says INTAKE_CARD §5 feature 2 'now reads 4 T-slots...', but intake/INTAKE_CARD.md is unchanged (still '4 slots, width ≈1.24, flat bottom'), so the record is inconsistent; (c) no photos |
| CHK-FILLET | verify (`qa/gate.json#checks`) | yes | pass | export_check.json fillets: []; no fillet ops planned (MODELING_PLAN §5) |
| CHK-INDEP | verify (`qa/gate.json#checks`) | yes | pass | separate agent context, QA-owned scripts; organisational independence not claimed (same orchestrator session) |
| CHK-LIKE4LIKE | verify (`qa/gate.json#checks`) | yes | finding | protocol changed it1->it2 (declared M6 slot-occupant mask added to the gate and to the ICP reference), so the it2 STEP was also graded under the exact it1 protocol. it1 gate (it1 STEP, it1 protocol): scan->CAD masked p95 0.311 / max 1.392, CAD->scan observable p95 0.671 / max 2.568. it2 STEP under the IDENTICAL it1 protocol (it1 masks, it1 ICP reference; qa/it1_protocol/): scan->CAD masked p95 0.225 / max 1.170, CAD->scan observable p95 0.598 / max 2.640, so this is the geometry-only change. it2 gate (adds the declared M6 slot-occupant mask, also removed from the ICP reference): scan->CAD masked p95 0.213 / max 1.177, CAD->scan observable p95 0.415 / max 2.636, so the remaining improvement comes from the M6 mask (protocol), not from geometry |
| CHK-MASK | verify (`qa/gate.json#checks`) | yes | pass | no pass depends on a mask |
| CHK-OVERLAY | verify (`qa/gate.json#checks`) | yes | pass | every panel shows scan |
| CHK-PATCHWORK | verify (`qa/gate.json#checks`) | yes | pass | census 200 faces, analytic area share 0.234; extra bspline faces = T-slot flare walls from the same single twisted extrude (extrude_linear_with_rotation); model.py grep: no loft / ruled loft / polyline stack |
| PHOTO-PLAUSIBILITY | verify (`qa/gate.json#checks`) | yes | n/a | no photos supplied |
| CHK-PUBLISH | deliver (preflight) | yes | pass | verdict BAND_NOT_MET |
| CHK-SUPERSEDED | deliver (preflight) | yes | pass | all earlier iterations kept intact |
| inputs_unchanged | deliver (preflight) | yes | pass | 1 input file(s) unchanged |
| hash_frozen | deliver (preflight) | yes | pass | every build/ STEP matches hash_frozen |
| regime_declared | deliver (preflight) | yes | pass | regime 'baseline-skill' |

## 11. Declared limitations (each with its re-run trigger)

| id | limitation | re-run trigger | evidence |
|---|---|---|---|
| L1 | Decimated scan only (the owner's own decimated export): every deviation number is INSPECTION ONLY, not an official grade. | full-res scan available | qa/gate.json#auto_limitations |
| BAND | Band NOT met, accepted by the owner: scan-to-CAD masked max 1.1771 mm (p95 0.213 passes) is set by an unmodelled local recess beside one slot entry at the hub; observable CAD-to-scan p95 0.4149 / max 2.6361 mm comes from slot foot, flare and floor surfaces the scan never saw. | full-res scan or a re-scan with cleaned slots aimed into them; photos of the drive end | decisions/accept_band_it2.md |
| L2 | no Tier-1 (no calipers run): every dimension is ABSENT, not passed. | caliper sheet intake/MEASUREMENTS.md filled | qa/gate.json#limitations |
| L3 | Absolute scale not caliper-verified (CHK-SCALE flag); units assumed mm. | caliper sheet intake/MEASUREMENTS.md filled | intake/alignment.json#checks |
| L4 | No photos: the local recess beside one slot entry cannot be classified as a feature or as damage, so it is not modelled. | photos of the drive end supplied | measure/figures/m14_hub_recess.png |
| L5 | Masked numbers: bristle tufts and fragments, scanner table and fringe, bristle-filled tuft holes, slot occupants (scan side); tuft holes, rim end face, idler bore bottom and slot occupants (CAD side). Fractions and the slot-occupant leave-one-out are in qa/VERDICT.md; unmasked numbers are reported next to every masked one. The observable CAD-to-scan figure excludes CAD-side masks through a verifier workaround. | observable_split fixed to honour CAD masks in stl-re-verify; re-run verify | qa/masks.json |
| L6 | Assumed, never-scanned surfaces: rim end face and hub interior (modelled flat and solid), tuft-hole depth, idler bore bottom. | caliper sheet intake/MEASUREMENTS.md filled or a scan of the drive end face | build/MODELING_PLAN.md#6 |
| L7 | Declared simplifications: big-groove floor depth varies along z but is modelled at one depth; core ovality; slot-mouth, groove-edge, slot-floor-corner and hub-step edge breaks not modelled; rim modelled as a cylinder; blade trailing wall modelled vertical. | one caliper reading on these features should trigger a re-run | measure/params.json#simplifications |
| L8 | Verification ran in a separate agent with its own code and ICP, but inside the same orchestrating session: this is not an organisationally independent verification. | an independent reviewer re-runs stl-re-verify | qa/VERDICT.md |

## 12. Assumptions and invented geometry

Parameters not measured on the scan or by caliper (source tag from `measure/params.json`):

| parameter | value | source | evidence |
|---|---|---|---|
| `bore_bottom_z` | 158.17 | assumed | measure/figures/m09_idler.json |
| `bristles` | 0 | assumed | intake/INTAKE_CARD.md#4 |
| `rim_end_z` | -6.471 | assumed | measure/figures/m08_hub_axial.json |
| `tuft_hole_depth` | 2.5 | assumed | intake/INTAKE_CARD.md#3 |

- Bristle tufts are not modelled (soft feature); the tuft holes are modelled empty with an assumed depth. _(source: assumed; measure/params.json#params.bristles)_
- Tuft rows set exactly half a turn apart and at the same axial positions (symmetry), within the bristle zone. _(source: assumed; measure/params.json#params.tuft_row_theta_deg)_

## 13. Claim boundary — what this result is NOT

- **Not fit for:** manufacture, tooling or fit checks until the drive dog, hub discs, idler bore and core OD are calipered and a full-res scan confirms the slots
- **Not fit for:** statements about the unscanned rim end face, hub interior, tuft-hole depth or idler bore bottom
- Fit for: visual reference, design study and as an editable parametric starting point (build/model.py, measure/params.json)
- The verdict covers only the Tier-1, deviation and named-check gates above, under the **baseline-skill** regime.

- Verify's own claim boundary (`qa/gate.json#claim_boundary`): Not deliverable without a recorded ACCEPT-BAND. This is an iteration-2, inspection-only (decimated), scan-only result. The slot-foot shape is supported by the scan only where the foot was seen. The hub recess is absent from the CAD. Not fit for tooling or fit checks of the slots or the drive-end recess. No claim about the unscanned rim end face, hub interior, tuft-hole depth or bore bottom.

## 14. Human acceptance of the band miss

Accepted by **owner (Ikbal), chat answer** on 2026-10-01 (`DECISIONS.md`, ACCEPT-BAND): accept scan_to_cad and cad_to_scan_observable (and zone) band misses for delivery, gate 830ff7000088. Record: `decisions/accept_band_it2.md` (sha256 `498c16e0fff3bd0ee756d583bd6ad86b0b5043f127bb726341db7355646f31c3`).

## 15. Reproduction

```
cd build && python3 model.py --params ../measure/params.json --alignment ../intake/alignment.json --out . --part dreame_brush_core --scripts <skills>/stl-re-rebuild-build123d/scripts
```

Fresh-process rebuild check (`deliver/repro.json`): reproducible **yes**; method 2 fresh subprocess rebuild(s) of build/model.py in a scratch copy; STEP re-imported; solids, faces, surface census, volume, bbox compared (raw hash reported, not required); environment python: 3.11.15; platform: Linux-6.18.44-fc-v50-x86_64-with-glibc2.39; build123d: 0.13.0; OCP: 8.0.1.0; numpy: 2.4.6.

| file | volume mm³ | |Δ volume| | max |Δ bbox| | faces equal | identical | raw sha equal |
|---|---|---|---|---|---|---|
| dreame_brush_core.step | 28731.5452 | 0 | 0 | yes | yes | no |
| dreame_brush_core_datum.step | 28731.5452 | 0 | 0 | yes | yes | no |

_Raw STEP hashes differ between runs because STEP headers carry a timestamp; the geometry is compared._

## 16. Provenance of every number in this file

| file | sha256 |
|---|---|
| `qa/gate.json` | 830ff7000088db1a12aed6898afc0a6a691d35dceabd25cd998a31e1f5c01963 |
| `measure/params.json` | 5f1a1e6d40fb57f37fa74e89c73df09b8c52c68e7b05367bc1e53cabe3880bad |
| `build/export_check.json` | 5a346857b3a244ef4c9ee3f9dbc34c39cdf6ecd7572938ebba33c5316b337187 |
| `intake/alignment.json` | 09d955099db399c512f0e3d9befa7399920c2c3b0c8dfe25a0ae8e0cc31dabcb |
| `deliver/repro.json` | 99aa834e1336de6f18fa554272de14d9043a9956a228a9ed11ddbde058dfebb0 |
| `deliver/limitations.json` | 93f42781358269c3496d2830d9016b10efa9637dc769bbe8632672a408110c7e |

Generated by `stl-re-deliver/scripts/make_readme.py`. Do not edit numbers by hand; fix the JSON and re-render.
