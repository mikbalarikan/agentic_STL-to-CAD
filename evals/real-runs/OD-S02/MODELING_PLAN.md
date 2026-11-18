# MODELING PLAN: OD-S02_steam-rod

Iteration: **it3 of 3** (it1 `_it1_SUPERSEDED/`, it2 `_it2_SUPERSEDED/`, both REVISE route geometry). **Process deviation (declared):** this plan was written after the first
build passes, not before `model.py` (SKILL step 1 / SYNTHESIS D1). The builder iterated
model.py against its own self-check (labelled self-check, not QA) and wrote this plan to
match the final feature tree. The change log (§8) records what changed between passes.

## 0. Build deviations

| Item | Planned | Built | Why | Declared to verify/deliver |
|---|---|---|---|---|
| Plan order | plan before model.py | plan after the self-check passes | see header | yes (this file, DECISIONS) |
| Hidden assembly interfaces | — | not modelled | one fused solid (PART-CLASS) | yes |
| D1 torn flash at knob/sleeve | — | not modelled | specimen damage (photos) | yes, intake card §2 |
| Tip bore depth | — | it2: 13.6 mm scan lower bound (it1: 8.0 assumed) | bore wall seen up to the bushing | yes, params `tip_bore_depth` |
| Bushing window depth | — | it2: 2.52 mm scan lower bound (it1: 1.5 assumed) | window surfaces seen that deep | yes, params `bush_window_depth` |
| Knob top outer edge, groove corners, band corners | — | sharp | no radius measured | yes (self-check residual) |

Unused params: `bend_R` (it3: the bend follows the scanned centreline spline; the circular-arc radius is kept in params as a measurement only).

## 1. Strategy summary

An assembly scanned as one mesh, built as sub-bodies each on its own measured axis and fused
(strategy D3). Dominant profile: the rod + knob (r,z) revolve about datum Z. Added: the knob
fairing (non-ruled loft through 6 fitted ellipse sections, clipped at the knob top), the lever
plate (outline extrude trimmed by two fitted planes, perimeter round, two sphere dishes), the
sleeve cone and sealing band (revolves on their own axes), the steel tube (ONE sweep along
line–arc–line), the bushing and tip (revolves on the tip axis) with 6 underside window pockets.

## 2. Expectations (reported, not gated)

- Ops before fillets: 14. Expected faces 80–140 (rod ≈27, knob ≈4, fairing ≈3, O-ring 2, lug 10,
  plate ≈14, sleeve/band 8, tube 3, bushing ≈30 with windows, tip 6). Built: 109 (face_stats.json).
- Surface types: planes, cylinders, cones, spheres, tori; B-splines on the knob meridian, the
  fairing loft and the bushing barrel (fitted splines).

## 3. Ordered feature list

| F## | Operation | Datum / plane | Driving params (source) | Acceptance |
|---|---|---|---|---|
| F01a | revolve knob meridian spline + cylinder | datum Z | knob_meridian_z/r, knob_r, knob_top_z, knob_bottom_z (scan; bottom assumed) | 1 solid |
| F01b | revolve rod profile (collar, groove, bead, body, flare, step, cone, taper, round nose) | datum Z | rod_* (scan) | re-measured radii on the STEP = params |
| F02 | O-ring cord (revolve) | datum Z | rod_oring_center, rod_oring_cord_r (scan) | bump peak r 5.77 |
| F02b | fairing loft through ellipses, clip z < knob top | x = const planes | fair_x/yc/zc/ay/az (scan) | non-ruled; clipped |
| F03 | lug box, corner round, placed at θ | datum Z | lug_* (scan; corner assumed) | lug at lug_theta |
| F04 | lever plate: outline (end circle + tangents + closing polygon) extruded, split by 2 planes | XZ | paddle_end_c/r, paddle_upper_line, paddle_lower_end, paddle_face_pos/neg (scan) | 1 solid |
| F05 | plate perimeter round (free outline only) | face planes | paddle_edge_fillet_r (assumed) | fillet_log OK |
| F06 | top dish sphere cut | +Y face normal | dish_c, dish_depth, dish_sphere_r (scan) | depth = param |
| F06b | underside dish sphere cut | — | under_dish_c, under_dish_R (scan) | apex y |
| F07 | sleeve cone (own axis) | sleeve axis | sleeve_* (scan) | — |
| F08 | sealing band revolve | tube B axis | band_* (scan) | — |
| F09–F11 | steel tube: cylinder B, bend swept along the scanned-centreline spline (bend_tube_r), cylinder C | B/C lines | tubeB_point/dir, tube_r, bend_vertex, bend_cl_x/y/z, bend_tube_r, tubeC_dir_up, bush_c_t (scan) | watertight tessellation |
| F12 | bushing revolve (conical top, flange, barrel spline, flat bottom) | tip axis | bush_* (scan) | — |
| F12b | 6 window pockets (ring tool minus spokes), cut once | bushing frame | bush_window_r, bush_spoke_count (CHK-COUNT pass), bush_spoke_phase, bush_spoke_w (scan), bush_window_depth (assumed) | 6 windows |
| F13 | tip revolve with the crimp neck under the bushing, end chamfer and bore | tip axis | tip_*, tip_neck_t/r (scan) | bore open |

## 4. Intake feature map (CHK-ENUM)

| Intake feature | Built by |
|---|---|
| 1 spigot + nose | F01b |
| 2 O-ring | F02 |
| 3 step + cone | F01b |
| 4 body bead/groove | F01b |
| 5 groove | F01b |
| 6 collar + lug | F01b, F03 |
| 7 knob + fairing | F01a, F02b |
| 8 lever plate + dishes | F04–F06b |
| 9 sleeve + band | F07, F08 |
| 10 tube B/bend/C | F09–F11 |
| 11 bushing + windows | F12, F12b |
| 12 tip + bore | F13 |
| 13 torn flash D1 | out of scope: specimen damage |

## 5. Fillet / chamfer plan (CHK-FILLET)

| F## | Edges | Target | Fallback | Order |
|---|---|---|---|---|
| F03 | lug edges parallel to the radial direction | lug_corner_r 0.6 | none | local, before placement |
| F05 | plate free-outline edges on both face planes | paddle_edge_fillet_r (it3: 1.946 scan fit; it1/it2 1.2 assumed) | none | local, before the dish cuts and the union (the closing polygon is buried) |
| rod nose | in the F01b profile (arc) | rod_tip_round_r 2.0 | — | in profile |
| tip end | in the F13 profile (chamfer) | tip_chamfer | — | in profile |

## 6. Unscanned or invented geometry

| Item | Value | Source tag | Why |
|---|---|---|---|
| knob bottom closing point | knob_bottom_z | assumed | inside the lever plate, unobservable |
| tip bore depth | 13.6 (it2) | scan lower bound | deeper not observable |
| bushing window depth | 2.52 (it2) | scan lower bound | deeper not observable |
| plate perimeter round | 1.946 (it3) | scan (mean of both sides) | measured in it3 |
| lug corner round | 0.6 | assumed | not measured |
| sub-body overlaps | EPS 0.02, 20·EPS, t_start 2.0, BIG | documented clearances in model.py | fuse without tangent booleans |

## 7. Known risks

- D1 torn flash dominates the scan→CAD max; verify decides the mask.
- Tube ovalised in the bend (rms 0.156 about the arc).
- Bushing/tip 4.8° off tube C; tube swept straight to the bushing centre.
- Knob off the rod axis by 0.22/0.10 mm (coaxial model).

## 8. Change log (self-check passes, same iteration)

1. First bend = revolved torus fused with two cylinders → tessellation holes → replaced by ONE sweep.
2. Knob fairing added (ellipse sections measured after the first self-check showed the +X half is not a revolve).
3. Underside dish added; underside plane refit outside the dish (was a peak-band plane).
4. Bushing: "neck" removed (was the tilted tube), axis changed from barrel circles to the tip axis
   (flat-face normals within 0.7°), top face made conical, 6 windows added (CHK-COUNT pass).
5. Rod bead/groove z 9.75..12.75 taken as the measured polyline.
6. Knob offset revolve tried and reverted (worse; meridian is measured about Z).
7. Plate round selector fixed to take both tangent lines and the arc (6 edges).

### Iteration 2 (REVISE, route geometry; `_it1_SUPERSEDED/qa/VERDICT.md`)
Verify it1 found scan material inside the CAD at the bushing (clusters 2 and 3, 96 points, masked
scan→CAD max). Probe (`measure/scripts/revise_it2_probe.py`): cluster 3 = window surfaces deeper
than the it1 pocket floor; cluster 2 = the tip bore wall seen below the bushing. Exactly two params
changed, both from `assumed` to a scan lower bound: `bush_window_depth` 1.5 → 2.52,
`tip_bore_depth` 8.0 → 13.6. No other geometry changed (params diff vs `_it1_SUPERSEDED/measure/params.json`).

### Iteration 3 (REVISE, route geometry; `_it2_SUPERSEDED/qa/VERDICT.md`), last loop
Verify it2 named three geometric causes; each was re-measured (`measure/scripts/measure_it3.py`,
`measure/figures/measure_it3.json`) and only those features changed:
- Z2 bend: circular arc → spline through 10 scanned centreline stations, bend radius `bend_tube_r`
  (the tube is thinner/ovalised in the bend); straight B and C unchanged. New params `bend_cl_x/y/z`,
  `bend_tube_r`; `bend_R` now unused.
- Z3 lever: perimeter round 1.2 (assumed) → 1.946 (scan fit, both sides).
- Z4 tip: crimp neck under the bushing (`tip_neck_t/r`, r down to 2.5).
Windows, bore depth and everything else are unchanged from it2.
