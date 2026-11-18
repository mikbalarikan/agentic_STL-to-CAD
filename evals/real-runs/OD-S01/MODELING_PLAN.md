# MODELING PLAN: OD-S01_steam-valve

Iteration: **it2 of 3** (after the it1 REVISE, `_it1_SUPERSEDED/qa/VERDICT.md`). The it1 plan is carried forward and
changed only where the QA it1 findings required (§8 it2 rows).

## 0. Build deviations (after the build)

| Item | Planned | Built | Why | Declared to verify/deliver |
|---|---|---|---|---|
| Plan written iteratively | whole plan before model.py | v0 plan (§3 rows F01..F08) came first; F09 and the cuts C01..C08 were added after builder self-checks v0..v9 showed unplanned geometry (cam ring, windows, slots) | the lower cam ring and the port junctions were not understood until the first self-check | yes, §8 change log |
| Spline teeth | tooth form | median cylinder | tooth count not resolved (CHK-COUNT finding) | yes, `measure/params.json#simplifications` |
| Fillets | 3 | 3 OK (C0.7, R1.5, R1.7 ×4) | — | `export_check.json#fillets` |

## 1. Strategy summary

The part is a rotary steam valve, scanned as one assembly, axis-dominant. ONE (r,z) revolve
carries the cap disc, the two-level cam pocket floor, the column (with its rounded top edge),
the neck and the neck groove. A 3-fold cam ring is added as sector solids: 3 posts with radial
flanks and 3 trapezoid teeth whose sloped flanks are planar half-spaces. The shoulder blocks,
collar sectors and ribs are sector solids at their measured angles. The top clip port, the two
side ports (drafted tube + drafted clip plates), the barb and the microswitch with its
bracket/holder are sub-bodies unioned onto the core. All cut tools (bores, orifices, windows,
slots, conical column windows, finger slots) are fused and subtracted once at the end.
Strategy rows used: revolve (D2), sub-bodies (D3), one instance + placements (D4), cut tools (D5),
sketch + extrude (plates, the barb collar).

## 2. Expectations (reported, not gated)

- Expected ops before fillets: about 30 (revolve 1, cam ring 1 pattern + 4 blocks + 10 sectors,
  top port 2, ports 2 × 3, barb 4, switch/bracket 6, cut pattern 10).
- Expected face count: **250–450** (revolve about 20, cam ring about 90, ports about 60, top port
  about 30, barb about 12, switch and bracket about 50, cuts about 90). Built: **314**, 100 %
  analytic (plane 221, cylinder 74, cone 18, torus 1), 0 freeform (`face_stats.json`).
- Surface types: planes, cylinders, cones, one torus (the column-top round). No B-splines.

## 3. Ordered feature list

| F## | Operation | Datum / plane | Driving params (source) | Acceptance (checkable on the STEP) |
|---|---|---|---|---|
| F02 | revolve (r,z) core + local round of the column top edge | axis Z | cap_r, cap_top_z, cam_floor_1/2, cam_top_z, column_r, column_top_z, neck_lo_r, groove_profile_1..7, neck_up_r, top_blk_bot_z, col_top_fillet (scan) | radii equal the params; fillet OK |
| F01 | spindle cylinder − D-flat + key, tip chamfer | axis Z | spindle_r, spindle_tip_z, spindle_flat_x, spindle_key_x, spindle_key_y, spindle_tip_chamfer (scan) | flat at x 2.43, key 1.50 wide |
| F09 | cam ring (3 posts + 3 teeth, 120° pattern), shoulder blocks, collar sectors, ribs, rib_320 | axis Z, sectors | cam_phase, cam_post_half, cam_post_r, cam_tooth_r, cam_flank_z, cam_tooth_half_bot/top, blk120, blk120_top, blk240, collar_z, collar_sectors_1..4, rib_sectors_1..5, rib_top_z, rib_320 (scan) | 6 pockets; flanks at the measured angles |
| F03 | top clip port: box, 4 X-parallel edge rounds, round rim | XY | top_blk_x/y, top_blk_bot/top_z, top_blk_edge_r, top_round_r, top_z (scan) | block 12.69 × 12.42; rounds OK |
| F04/F05 | side ports: drafted tube (cone) + 2 drafted plates each (YZ-section slab ∩ plan prism) | port axes along X | pu/pl_axis_yz, port_end_x, port_r_end, port_r_root, pu/pl_plate_edge_1/2, pu/pl_plate_faces_1/2 (scan) | OD 10.94 at the end; plates at the measured slopes |
| F06 | barb: shaft, back cone, crest cone, collar disc | axis along −Y | barb_axis_xz, barb_shaft_r, barb_back_y, barb_crest, barb_tip, barb_collar (scan) | crest r 3.45 at y −19.25 |
| F07 | microswitch box, 2 blades, side tab, fin | XY | sw_x/y/z, sw_blade_x, sw_blade_y_1/2, sw_blade_top_z, sw_tab, fin (scan) | box 5.92 × 19.68 × 9.37 |
| F08 | bracket plate + holder prism (open inside its measured diagonal edge) | XY | brk_box, holder_y0, holder_edge (scan) | no material at the scanned opening |
| F10 (it2) | port junction boxes x −4..−0.12, ports and plates run to the scanned end wall, lip under the upper block | XY | port_col_x, port_junction_x0, pu_lip (scan) | end walls at x −0.12 |
| F11 (it2) | switch bump, bar at 330°, column lug at 320°, barb top rib | XY / YZ | sw_bump, bar330, lug320, barb_rib (scan) | present |
| F12 (it2) | shoulder block: lower sector to z 12.4 + upper shell r 10.05..14 with a planar sloped top | axis Z | blk120_lo, blk120_up, blk120_slope (scan) | slope through the measured left-edge line |
| C01 | top bore + counterbore + lower bore to the floor | axis Z | top_bore_r, top_bore_bot_z, top_cbore, top_bore2 (scan) | floor at z 43.0 (it2) |
| C02 | port bores with orifice webs | port axes | port_bore_r, port_web_x0/x1, port_orifice_r (scan) | bore r 4.00, orifice r 2.0 |
| C03 | barb bore | barb axis | barb_bore_r (scan) | r 1.42 |
| C04 | conical column windows (revolved tool ∩ wedge) | axis Z | col_window_cone_1..3, col_windows_1/2 (scan) | floor r 6.15 at z 14.4 |
| C05 | finger slots behind the 3 teeth | axis Z | finger_slot, cam_tooth_half_top (scan) | — |
| C06 | top clip slots, 2 per side, through both lug walls | along X | top_slot (scan, mirror symmetry) | 4 slots |
| C07 | cap slots ×3 | Z | cap_slot_1..3 (scan; slot 3 partly from the render) | 3 through slots |
| C08 | port U-windows + junction flats | along Y | port_window, port_trim (scan) | windows open into the bores |

## 4. Intake feature map (CHK-ENUM)

| Intake feature | Built by | Or: out of scope because |
|---|---|---|
| E01 spindle | F01 | tip hole r ~0.9: not modelled (tiny, only partly scanned) |
| E02 cap disc, slots, dimples | F02, C07 | dimples not modelled (declared simplification) |
| E03 cam ring | F09, C05 | — |
| E04 shoulder blocks | F09, F12 | — (slope modelled in it2) |
| E05 collar, ribs, column windows | F09, C04 | — |
| E06 column | F02 | — |
| E07 neck and groove | F02 | — |
| E08 top clip port | F03, C01, C06 | internal ribs averaged (declared) |
| E09/E10 side ports | F04/F05, C02, C08 | plate lips/hooks not modelled (declared) |
| E11 barb | F06, F11, C03 | — (rib added in it2) |
| E12 microswitch | F07 | labels, blade holes not modelled (declared) |
| E13 bracket/holder | F08 | — |
| E14 fin | F07 | — |
| E15 interior | — | not scanned, not invented: the column is solid below the top bore |
| E16 switch bump / E17 column lug / E18 bar | F11 | — (added in it2) |

## 5. Fillet / chamfer plan (CHK-FILLET)

| F## | Edges (selector rule) | Target param | Fallback radii | Order |
|---|---|---|---|---|
| F02 | circle at z = column_top_z, r = column_r | col_top_fillet 1.5 | none | local, on the core before the ports/plates are fused (they would split the edge) |
| F01 | circle at z = spindle_tip_z | spindle_tip_chamfer 0.7 | none | local, before the flat/key cut |
| F03 | the 4 block edges parallel to X | top_blk_edge_r 1.7 | none | local, on the block before it is fused |

Result: 3/3 OK, target == used (`fillets.json`).

## 6. Unscanned or invented geometry (provenance)

| Item | Value | Source tag | Why |
|---|---|---|---|
| column interior | solid | assumed (not scanned) | a single solid; no scan evidence of the passages |
| finger-slot bottom | z 6.5 (visibility limit) | measured limit, not a floor | the slot floor is occluded |
| port blocks between the neck and x −0.12 | box to the neck | scan end wall measured; the part inside the neck is buried | to fuse (it2: the visible end wall is modelled; the it1 assumption that it was hidden was wrong) |
| barb root 1 mm inside the neck | connector | assumed | to fuse |
| holder from inside the column to the switch | x 5.6..9.73 | the scan face y −4.97 is measured; the inner end is buried | to fuse |

## 7. Known risks

The cam flank edges and port junction corners carry local 0.3..1.0 mm deviation. The switch
labels and cap slots are only partly scanned. The spline is not toothed. All of these are
declared in `measure/params.json#simplifications`; verify reports them per zone.

## 8. Change log (inside iteration 1; builder self-checks, NOT QA, datum frame, no ICP)

| Build | Change | Self-check p95 / >0.3 mm share |
|---|---|---|
| v0 | core revolve with a plain skirt, spindle, top block, ports + plates, barb, switch, bracket | 1.67 / 26.5 % |
| v1 | cam ring (posts, trapezoid teeth, blocks) replaces the plain skirt; column windows | 1.01 / 21.5 % |
| v2 | plate extrusion direction bug fixed (the lower plates were 1 mm low); orifice webs; fin; side tab from the bracket | 0.73 / 16.7 % |
| v3 | port U-windows and junction flats | 0.71 / 16.5 % |
| v4 | top clip slots, block rounds, collar ring; port bores to x 0 | 0.59 / 14.4 % |
| v5 | collar split into measured sectors plus vertical ribs; cap slots | 0.56 / 13.8 % |
| v6 | measured groove profile, column top round, bracket plate/holder corrected, top counterbore | 0.53 / 12.6 % |
| v7–v8 | conical column windows, finger slots, rib_320; restored the top slots (lost in an edit at v7) | 0.495 / 11.8 % |
| v9 | drafted port plates (measured face slopes) | 0.489 / 10.8 % |
| final | params validated (`param_table.py`: 0 errors), grouped params, `cam_flank_z` param replaces a literal | 0.490 / 10.8 % (`selfcheck/selfcheck_final.txt`) |
| **it2** | QA it1 REVISE, `--route datum`: intake re-run (identical), E16–E18 enumerated; ports/plates to x −0.12 + junction boxes + lip; switch bump; bar 330 re-measured; column lug; barb rib; top bore floor lowered to z 43.0; shoulder block shell with a sloped top; holder opened inside its measured diagonal edge; cap slot 3 resized. Built 351 faces, 3/3 fillets OK | 0.414 / 9.0 % (`selfcheck/selfcheck_it2_final.txt`) |
