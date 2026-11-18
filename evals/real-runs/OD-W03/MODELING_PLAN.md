# MODELING PLAN: OD-W03 water tank valve

Iteration: it1 of 3. Written before `build/model.py`.

## 0. Build deviations (filled after the build; empty = none)

| Item | Planned | Built | Why | Declared to verify/deliver |
|---|---|---|---|---|
| cup and boss tops | flat at `cup_top_z` / `boss_top_z` | cones (`cup_top_z_r9` + `cup_top_slope_deg` ≈ 8.5°, `boss_top_z_r4` + `boss_top_slope_deg` ≈ 3.7°) | builder self-check showed a ring on the flat top; re-measured (m08), plan + params updated before verify | yes: params.json notes, §8 below |
| surface types | planes, cylinders, cones, tori | + 8 B-spline faces (5 fillets between cone faces and their blends) | OCC builds cone/cone rounds as B-splines | yes: build/face_stats.json |

## 1. Strategy summary
A stadium flange (sketch + extrude, skirt down to `skirt_bottom_z`) carries three turned bodies on the
X axis: cup A / cup B (one closed (r,z) meridian each: drafted lower wall, step cone, drafted upper wall,
top annulus, 31° shoulder cone, barb shank, 28° flare, lip, 7° tip taper) and a middle boss (drafted
cylinder). Cups use per-cup measured values (A/B differ beyond noise), not a mirrored copy. Four planar
webs, two tapered ear tabs (trapezoid in YZ extruded along X) and two slot-shaped lugs are fused on.
The hollow shell (owner decision) is one cut-tool set subtracted once: under-plate stadium pocket,
two cup cavities (inner meridian offset by `wall_t`), boss cavity, barb bores, boss hole, lug holes.

## 2. Expectations (reported, not gated)
- Ops before fillets: 9 (flange, cup revolve ×1 op/2 instances, boss revolve, webs, tabs, lugs, cavity tools, holes, fuse).
- Expected faces: 90–160 (flange+skirt ~8, each cup outer ~12 + inner ~8, boss ~6, webs ~4×4, tabs ~6×2, lugs ~8×2, pockets/holes ~15, fillets 5).
- Surface types: planes, cylinders, cones, tori (fillets); no B-spline expected.

## 3. Ordered feature list
| F## | Operation | Datum / plane | Driving params (source) | Acceptance |
|---|---|---|---|---|
| F01 | stadium sketch (2 arcs + tangents, trimmed at the end faces) extruded `skirt_bottom_z`..`flange_top_z` | XY | `flange_half_width`, `flange_centre_y`, `flange_end_arc_cx`, `end_face_x`, `skirt_bottom_z`, `flange_top_z` (scan) | outline on STEP section z=-1 matches params |
| F02 | revolve cup A / cup B outer meridian about x = ∓`cup_pitch`/2 | XZ half-plane per cup | `cup_pitch`, `cup_lower_r0`, `cup_lower_draft_deg`, `cup_upper_r0`, `cup_upper_draft_deg`, `cup_step_z_lo/hi`, `cup_top_z_r9`, `cup_top_slope_deg`, `shoulder_angle_deg`, `shoulder_z_at_r5`, `barb_shank_r`, `barb_flare_z0`, `barb_lip_r`, `barb_lip_z`, `barb_tip_r`, `barb_top_z` (scan) | 2 cups, profile radii at stations = params |
| F03 | local fillets on each cup: top outer round, shoulder→shank round | circular edges selected by z and radius | `cup_top_round_r`, `shank_fillet_r` (scan) | fillet_log OK |
| F04 | revolve boss (drafted cylinder) about x=0 + local top round | XZ | `boss_r0`, `boss_draft_deg`, `boss_top_z_r4`, `boss_top_slope_deg`, `boss_top_round_r` (scan) | r, top z = params |
| F05 | 4 webs: boxes y ±`web_half_width`, z to `web_top_z`, spanning the cup↔boss and cup↔tab gaps | XY | `web_half_width`, `web_top_z` (scan, symmetry) | web width on section = param |
| F06 | 2 ear tabs: trapezoid (half-width `tab_half_width_z0` − tan(`tab_side_draft_deg`)·z) in YZ, extruded from `tab_inner_x` to `end_face_x`, z `skirt_bottom_z`..`lug_top_z` | YZ | `tab_inner_x`, `tab_half_width_z0`, `tab_side_draft_deg`, `end_face_x`, `lug_top_z` (scan) | tab faces planar |
| F07 | 2 lugs: slot (rect + end semicircle R=`lug_half_width`, apex at `lug_end_x`) extruded `lug_bottom_z`..`lug_top_z` | XY | `lug_half_width`, `lug_end_x`, `lug_bottom_z`, `lug_top_z`, `tab_inner_x` (scan) | lug outline = params |
| F08 | fuse F01–F07 | — | — | 1 solid |
| F09 | cut tools fused and subtracted once: under-plate pocket (stadium inset `wall_t`, up to z = −`wall_t`), cup cavities (outer meridian offset `wall_t`), boss cavity, barb bores (`barb_bore_r`, through), boss hole (`boss_hole_r`), lug holes (`lug_hole_cx/cy/r`) | — | `wall_t` (assumed), `barb_bore_r`, `boss_hole_r`, `lug_hole_*` (scan) | 1 valid closed solid; holes present |

## 4. Intake feature map (CHK-ENUM)
| Intake feature | Built by | or out of scope |
|---|---|---|
| E01 flange plate | F01 | |
| E02 skirt | F01 + F09 pocket | |
| E03 cups | F02, F03 | |
| E04 shoulders | F02 | |
| E05 barbs | F02 | |
| E06 barb bores | F09 | depth assumed (through into the cavity) |
| E07 middle boss + hole | F04, F09 | |
| E08 webs | F05 | |
| E09 ear tabs | F06 | |
| E10 ear lugs + holes | F07, F09 | |
| E11 parting line ridge | — | cosmetic, not modelled (params simplifications) |
| E12 interior / underside | F09 | assumed hollow shell, `wall_t` 1.2 (owner decision) |

## 5. Fillet / chamfer plan
| F## | Edges | Target param | Fallback | Order |
|---|---|---|---|---|
| F03a | cup outer top corner (circle at z=`cup_top_z`, r = upper wall at that z), per cup | `cup_top_round_r` [A,B] | none | local on the cup sub-body before F05 (webs would split the edge) |
| F03b | shoulder→shank concave edge (circle at the shank radius), per cup | `shank_fillet_r` [A,B] | none | local, same reason |
| F04a | boss top outer corner | `boss_top_round_r` | none | local, same reason |

## 6. Unscanned or invented geometry (provenance)
| Item | Value | Source tag | Why |
|---|---|---|---|
| wall / plate / skirt thickness | `wall_t` 1.2 | assumed | underside and interiors unscanned; owner chose hollow shell |
| cup / boss cavities, under-plate pocket | offsets of the outer skin by `wall_t` | assumed | same |
| barb bore depth | through into the cup cavity | assumed | only the tip opening is scanned |
| boss hole depth | through into the boss cavity | assumed | ~1 mm seen |
| lug underside | flat at `lug_bottom_z` | scan bound | underside not seen; side walls seen down to it |
| web span inside cups/boss | buried, cut by the cavities | — | webs are only visible in the gaps |

## 7. Known risks
- CAD→scan observable will include the invented underside/interior surfaces (not scanned) → expected
  band miss in that direction; reported, not chased.
- Cup wall ripple (±0.15) and rough barb shanks may push scan→CAD p95 toward 0.3.
- Web tops 12.41 vs cup top 12.26–12.34: the webs stand ≤0.15 proud over the outer cup-top annulus.

## 8. Change log
- it1 attempt 1: initial plan; built OK (106 faces, 5/5 fillets OK). Builder self-check (NOT QA): scan->CAD p95 0.308 (datum frame, 200k seeded samples).
- it1 attempt 2 (same iteration, before verify): measure m08 added; `cup_top_z` -> `cup_top_z_r9` + `cup_top_slope_deg`, `boss_top_z` -> `boss_top_z_r4` + `boss_top_slope_deg` (tops are ~8.5° / 3.7° cones, rms of bin medians 0.009-0.016). Self-check p95 0.299, max 1.06 (barb A tip bridging + tab/lug junction scan junk). No other parameter changed.
