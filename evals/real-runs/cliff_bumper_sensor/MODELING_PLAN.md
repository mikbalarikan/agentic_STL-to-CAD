# MODELING PLAN: cliff_bumper_sensor

Iteration: it1 of 3. Written before `build/model.py`. Frame: datum frame of
`intake/alignment.json` (z=0 top face, material −z; y=0 side-wall mid-plane; x=0 lower-body rear
wall; −x toward the lens nose).

## 0. Build deviations (filled after the build)

See the bottom of this file ("Build deviations, as built").

## 1. Strategy summary

A moulded sensor housing: one rounded box (the clear cover) is the dominant silhouette. Added to
it: a lens-nose cup (box with large bottom-side rounds, cut by the measured lens plane), the
black rear cap and connector shelf (boxes), the two guide rails and two tabs (boxes on the side
walls), and two wedge ramps under the bottom. Cut from it: the 1.55° bottom plane (one half-space
for every body), three shelf pockets, the pocket lip relief, the wire slot, the top seam groove
and the two lens windows (inner cup ∩ slab behind the lens plane, minus the centre rib).
Strategies: sketch/box + extrude, sub-bodies unioned, cut tools subtracted once, intersect with an
envelope (`references/strategy-catalogue.md`). No revolve (no axis), no loft.

## 2. Expectations (reported, not gated)

- Expected ops before fillets: 13 (F01–F13).
- Expected face count: 100–220 (cover ≈10, cup ≈15, cap ≈10, shelf ≈8, pockets 3×5, lip 2,
  rails 4×5, tabs 2×5, ramps 2×4, slot 4, groove 2, windows 2×8, plus split faces).
- Surface types: planes, cylinders (edge rounds, groove), B-spline only where the lens-tip round
  crosses the cup round (fillet corner patches).

## 3. Ordered feature list

| F## | Operation | Datum / plane | Driving params (source) | Acceptance (checkable on the STEP) |
|---|---|---|---|---|
| F01 | cover box, bottom half-space cut, long-edge rounds | XY, bottom plane | `body_front_x`, `seam_x`, `body_y_pos/neg`, `bottom_z_at_x0`, `bottom_slope_deg`, `cover_top_R`, `cover_bot_R` (scan) | width 32.04, bottom slope 1.55° |
| F02 | lens cup: box → bottom cut → bottom-side rounds `nose_cup_R`, top rounds `nose_top_R` → split by lens plane → lens-outline round `nose_tip_R` | lens plane (normal+point) | `nose_half_w`, `nose_cup_R`, `nose_plane_normal`, `nose_plane_point`, `nose_tip_R` (scan), `nose_top_R` (assumed) | nose tip x ≈ −27.57; lens face angle 59.6° |
| F03 | rear cap box (seam..rear wall), top rounds, bottom rounds | XY | `seam_x`, `rear_wall_x`, `cap_y_pos/neg`, `shelf_top_z`, `cap_top_R` (scan), bottom round = `cover_bot_R` (reuse, §6) | cap width 32.54 |
| F04 | connector shelf box, top rounds | XY | `rear_wall_x`, `shelf_end_x`, `shelf_y_pos/neg`, `shelf_top_z`, `shelf_bottom_z`, `shelf_top_R` (scan) | length 7.07, thickness 3.61 |
| F05 | guide rails ×2 (front part + taller rear part) | side walls | `rail_y_*`, `rail_x_start_*`, `rail_top_z`, `rail_rear_top_z`, `rail_rear_x_start`, `tab_bot_z` (scan) | width over rails 35.47 |
| F06 | tabs ×2 | side walls | `tab_y_*`, `tab_x_start_*`, `tab_x_end_*`, `tab_top_z`, `tab_bot_z` (scan) | width over tabs 37.99, thickness 1.85 |
| F07 | bottom ramps ×2 (wedge prisms on the bottom plane) | XZ profile, extruded in y | `ramp_x_start`, `ramp_x_end`, `ramp_peak_z`, `ramp_y_in`, `ramp_y_out` (scan) | ramp tip z −9.89 |
| F08 | union F01–F07 | | | 1 solid |
| F09 | pockets ×3 (one tool each, subtracted once with F10–F13) | shelf underside | `pocket_x_front/back`, `pocket_ceiling_z`, `pocketA/B/C_y0/y1` (scan) | 3 pockets, ceiling −1.385 |
| F10 | pocket lip relief (x rear wall..pocket front, below `pocket_lip_z`) | | `pocket_lip_z` (scan) | |
| F11 | wire slot (rear bottom centre) | | `slot_x_end`, `slot_y_pos/neg`, `slot_top_z` (scan-extent) | slot width 3.06 |
| F12 | seam groove: cylinder along y | top face | `seam_x`, `seam_groove_zc`, `seam_groove_R` (scan) | groove floor z −0.23 |
| F13 | lens windows: inner cup (half-width `window_y_out`, round `window_corner_R`, concentric with F02) ∩ slab `window_depth` behind the lens plane ∩ band `window_s_lo..hi` − rib (±`window_y_in`) | lens plane | `window_*` (scan), `window_corner_R` (assumed) | 2 windows, depth 0.81 |
| F14 | clean, validate, export datum + scan frame | | | 1 valid closed solid |

## 4. Intake feature map (CHK-ENUM)

| Intake feature | Built by F## | or: out of scope because |
|---|---|---|
| E01 main box | F01 | |
| E02 long-edge rounds | F01, F03, F04 | |
| E03 lens cup | F02 | |
| E04 frame + rib + recessed windows | F02 (frame plane), F13 | |
| E05 nose tip round | F02 | |
| E06 seam groove | F12 | |
| E07 rear cap | F03 | |
| E08 shelf | F04 | |
| E09 three pockets | F09, F10 | |
| E10 guide rails | F05 | |
| E11 tabs | F06 | |
| E12 wire slot | F11 | roof height from the scan extent only |
| E13 bottom ramps | F07 | |
| E14 blob on +Y tab | — | out of scope: no flat top, not mirrored, debris/artefact (params `tab_blob_not_modelled`, open question) |
| E15 interior seen through the windows | — | out of scope: interior of a transparent part, not envelope |

## 5. Fillet / chamfer plan (CHK-FILLET)

| F## | Edges (selector rule) | Target param | Fallback radii (reason) | Order |
|---|---|---|---|---|
| F01 | cover box: lines ∥X at z≈0, |y|≈body_y | `cover_top_R` | none | local, before the union (the cap/cup would hide the edge ends) |
| F01 | cover box: lines ∥X on the bottom plane, |y|≈body_y | `cover_bot_R` | none | local |
| F02 | cup box: lines ∥X on the bottom plane, |y|≈nose_half_w | `nose_cup_R` | none | local, before the lens split |
| F02 | cup box: lines ∥X at z≈0, |y|≈nose_half_w | `nose_top_R` | none | local, before the lens split |
| F02 | cup: edges lying in the lens plane (whole outline, G1 chain) | `nose_tip_R` | none | local, after the lens split |
| F03 | cap box: top lines ∥X / bottom lines ∥X | `cap_top_R` / `cover_bot_R` | none | local |
| F04 | shelf box: top lines ∥X | `shelf_top_R` | none | local |

## 6. Unscanned or invented geometry (provenance)

| Item | Value | Source tag | Why it is needed |
|---|---|---|---|
| window outline round | `window_corner_R` 6.03 | assumed (concentric with the cup round) | windows' bottom corners are partly scanned only |
| cup top-edge round | `nose_top_R` = `cover_top_R` | assumed | 1.2 mm long edge, no separate fit |
| cap bottom-edge round | `cover_bot_R` reused | assumed (same moulding line as the cover) | cap is 1.07 mm long, no separate fit |
| slot roof | `slot_top_z` (highest scanned wall point) | scan extent | roof not scanned |
| overlaps: rails/tabs start 0.3 mm inside the side wall; ramp top 0.5 mm inside the body; cut tools overshoot by 1.0 mm | clearances | documented construction clearances, not geometry | robust booleans |

## 7. Known risks

- Lens-outline round (`nose_tip_R`) propagates around the whole G1 outline; if OCC fails, report
  FAILED in `fillets.json` and declare it (≤ 0.53·(1−1/√2) ≈ 0.16 mm local cost).
- Coplanar bottoms of the cover and cup (same half-space) → fuse must merge them; `.clean()`.
- Ramp start lies on the bottom plane (zero-thickness edge); if the union fails, hold the start
  0.02 mm inside (B02 tangent-boolean heuristic) and log it.
- The windows are transparent: verify will see interior scan hits there (declared, E15).

## 8. Change log

- it1: initial plan.

## Build deviations, as built (it1)

| Item | Planned | Built | Why | Declared to verify/deliver |
|---|---|---|---|---|
| fillets | 9 logged rounds at target | 9 OK at target (`fillets.json`) | — | export_check.json#fillets |
| lens-outline round | `nose_tip_R` on the lower outline | applied to the whole lens-plane outline (5 edges, G1 chain incl. sides and top) | OCC propagates along the tangent chain | yes (this row) |
| face count | 100–220 | 106 (83 planar, 6 freeform fillet-corner patches, 0 ruled-like) | — | face_stats.json |
| unused params | — | none (`build_log.txt`) | — | — |

Builder self-check (NOT QA, scratch only, 60k/40k seeded samples on the working mesh): scan→CAD
p95 0.25; points > 0.8 mm sit in the two lens windows (interior seen through clear plastic) and on
the +Y tab blob. Grading is left to the independent verify.
