# MODELING PLAN — OD-G11_portafilter (iteration 1)

## Build deviations (iteration 2)
- Fillets: 11 of 12 at target radius; **F13 cone-part leg-foot rounds REDUCED: target arch_foot_round_R -> used 0.8 x target**
  (fillets.json; plan §6 fallback: the cone-part edges are short and end on the neck-cone start face).
- Iteration 2 changes (route measure, it1 verdict REVISE): outlet trough (m16) replaces the it1 gutter cone; V ribs as
  two drafted crest segments (m15) instead of one PCA line + offset; lug trailing lead-out planes (m17); rounded arch
  feet (m18); U-rib round end fixed (it1 code shifted the whole inner stadium, making the tip 2.4 mm thick); wire groove
  in the bore (m19); neck cone and collar revolved about their own measured axis offsets (m20).
- Known small step: the neck cone (own axis, dz offset) meets the arch cylinder (grip axis) with a step below 0.5 mm.
- Unused params: none (build_log.txt). Invented geometry: see params rows with source 'assumed'.
- Census (reported): build/face_stats.json. Builder self-check (NOT QA): build/selfcheck/selfcheck.json.

## 1. Strategy summary
The dominant silhouette is the turned cup: ONE closed (r,z) profile revolved about the datum Z axis
(dome bottom, drafted outer wall, rim). The interior cavity is ONE revolved profile (rim bore, ledge,
taper, insert wall) intersected with the funnel region (a vertical-axis cone about the funnel axis),
subtracted once. The handle is ONE (t,r) profile revolved about the fitted handle axis (neck cone,
collar, tapered grip, end chamfer). Everything else is added or cut as separate tool solids placed at
measured positions: 3 lugs (annular sectors cut by ramp planes), pad (offset reverse-draft cone ∩
wedge), open-bottom arch neck (cylinder − channel − foot half-space), 2 spouts (revolved about their
own axes), insert plateau and ribs, pockets, screw recesses, 3 wire arcs (torus sections).
Symmetry is NOT enforced anywhere (lugs, spouts, ribs, wire are placed at their measured values).

## 2. Ordered feature table
| F | Operation | Frame | Driving params (source: scan unless noted) | Acceptance on the STEP |
|---|---|---|---|---|
| F01 | revolve outer (r,z): dome arc → wall line → rim top | datum Z | dome_centre_z, dome_R, outer_wall_r_at_z0, outer_wall_dr_dz, rim_top_z | one solid, rim at z = 0 |
| F02 | cavity = revolve(bore, ledge, taper, insert wall) ∩ funnel cone region; subtract | datum Z; funnel axis | bore_*, ledge_z, ledge_taper_*, insert_wall_*, funnel_* | floor is a cone about the funnel axis |
| F02b | outlet trough: circular (r,z) section revolved about Z between the spout angles, ∩ interior; subtract (floor = min(funnel, trough)) | datum | trough_rc/zc/rho, spout{1,2}_x/y | — |
| F03 | fillets: bottom corner, rim outer/inner rounds, floor-to-wall | — | bottom_corner_R, rim_outer_round_R, rim_inner_round_R, floor_fillet_R | fillets.json all OK or declared |
| F04 | spouts ×2: revolve about each boss axis (wall line, ring, head cap) ∪; root round | boss axes | spout{1,2}_x/y/wall_*/ring_z/tip_z/head_z_r3p2, spout_head_r, spout_boss_root_R (assumed) | tips at measured z |
| F05 | pockets ×2: bore, subtract | boss axes | pocket_bore_r, pocket_bore_bottom_z (assumed, unscanned) | declared invented |
| F06 | U plateau: U inner region prism ∩ below plane, ∪ | datum | urib_inner_absy, urib_open_end_x, urib_round_end_outer_x, urib_outer_absy, uplat_* | — |
| F07 | U rib: U band (inner/outer faces) prism to top z, full-round top, ∪ | datum | urib_* | — |
| F08 | V ribs ×2: two drafted crest segments (outer end → joint → tip) with drafted round caps, full-round top, ∪ | datum | vrib{1,2}_outer_end/joint/tip/top_z, vrib_width_top/base, vrib_width_z_top/base | — |
| F09 | lugs ×3: annular sector (to r_outer) ∩ above the ramp plane ∩ above the lead-out plane, ∪ | datum | lug{i}_centre_deg/span_deg/r_outer/under_z_centre/under_dz_per_deg/leadout_* | 3 lugs at measured angles |
| F10 | rim notches ×2: annular sector cut to the notch floor | datum | notch{i}_* | — |
| F11 | pad: offset reverse-draft cone ∩ (side planes, under-chamfer plane), ∪ | datum | pad_* | — |
| F12 | arch neck: cylinder r − channel (slot + roof arc) − below foot plane; foot rounds | handle axis | arch_outer_r, channel_*, arch_foot_w | open bottom |
| F13 | neck cone, collar and grip revolved separately (neck/collar about their own axis offsets) − channel; collar/end rounds; cone-part foot rounds | handle axis | handle_axis_*, neck_cone_*, collar_*, grip_*, end_* | end face at measured t |
| F14 | screw recesses: centre counterbore + cross; spout-head crosses | datum; boss axes | cscrew_*, recess_arm, recess_depth, recess_width (assumed) | — |
| F15b | wire groove: V section behind the bore, revolved over its theta span; subtract | datum | groove_* | — |
| F15 | wire ×3: torus section between the bore crossings, ∪ | datum | wire{i}_cx/cy/R/zc, wire_r, bore_* | ends buried in the bore wall |

## 3. Intake features mapped
Card §5 rows 1→F01/F03, 2→F02, 3→F09, 4→F10, 5→F11, 6→F12/F13, 7→F04, 8→F14, 9→F02/F05–F08,
10→F15, 11 (cast lettering)→ out of scope: cosmetic relief at noise level.

## 4. Unscanned / invented geometry
- Spout pocket bore below the countersink and its depth (pocket_bore_r, pocket_bore_bottom_z: assumed).
- Neck channel interior beyond what the scan saw (roof extent measured, end wall measured).
- Solid material between all outer and inner scanned surfaces (one fused solid by owner decision): the
  real part is several bodies (cast cup, insert, grip, cap, screws, wire) with internal interfaces.
- Screw cross-recess width and orientation (recess_width assumed; crosses placed axis-aligned).

## 5. Expected op count and face count
~15 ops (patterns counted once). Faces: F01–F03 ≈ 12, lugs 3×7, notches 2×4, pad ≈ 6, arch ≈ 12,
handle ≈ 14, spouts 2×6, pockets 2×3, plateau+ribs ≈ 30, recesses 3×12, wire 3×3.
Expected range 150–300 (reported, not gated).

## 6. Fillet plan
| Fillet | Target param | Order | Fallback |
|---|---|---|---|
| bottom corner | bottom_corner_R | local, right after F02 (before spouts touch the dome) | none |
| rim outer / inner rounds | rim_outer_round_R, rim_inner_round_R | local, after F02 (lugs later cover part of the outer edge) | none |
| floor-to-wall | floor_fillet_R | local, after F02 (edge is later split by ribs) | none |
| spout root | spout_boss_root_R | local, right after F04 | none |
| rib tops | full round = half the rib thickness | on the rib solid before the union | none |
| collar crest, end edge | collar_top_round_R, end_round_R | on the collar / grip revolves before the union | none |
| cone-part leg feet (it2) | arch_foot_round_R | on the neck revolve after the channel cut | 0.8, 0.6, 0.4 × target (short edges ending on the cone start face) |

## 7. Known risks
Tangent unions (pad top meets the wall at z = 0; wire ends in the bore) may leave sliver faces; the
floor fillet is on a cone/cone intersection curve and may fail (then declared); ribs have one occluded
flank so their thickness is partly assumed; the spout pockets are invented below z ≈ −43.5.

## 8. Change log
- it2 (route measure after the it1 REVISE; see Build deviations): trough, V-rib segments, lug lead-outs, arch feet (rod construction in the arch part; the plan's earlier drop of the foot round was wrong, verify it1 CHK-FILLET), U-rib tip fix, wire groove, neck/collar axes. Attempt 1 self-check p95 0.316 -> attempt 2 0.283 (full-res, no ICP).
- it1 rebuild attempt 3 (self-check, same iteration): the F02b flat basin was wrong (ring medians mixed two zones); replaced by the gutter cone of m14 (region x >= 11, theta -33..29). Pocket countersink removed (same misreading); pocket = bore only. V ribs rebuilt with the measured draft and centre offset (m13) instead of an assumed 1.9 mm constant thickness.
- it1 rebuild attempt 2 (self-check, same iteration): added F02b outlet basin (measure/scripts/m12_basin.py; the m08 funnel fit had excluded the cells below -41.8); channel mouth cut from channel_start_t after the pad union (the pad closed the channel mouth); countersink tool extension reduced 3.0 -> 0.5 mm (it notched the wall).
- it1: initial build.
- it1 (before first run): dropped the planned arch-foot round; the x-sections show the leg 'foot curve' is the r = arch_outer_r cylinder itself meeting the foot plane (flat foot 0.8 mm wide), so no separate round exists.
