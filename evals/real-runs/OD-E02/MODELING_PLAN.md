# MODELING PLAN: OD-E02_control-button-board

<!-- Written before build/model.py. Iteration: it3 of 3 (it1, it2 in _it1_SUPERSEDED/, _it2_SUPERSEDED/, both verdict REVISE). -->

## 0. Build deviations (filled in after the build)

| Item | Planned | Built | Why | Declared to verify/deliver |
|---|---|---|---|---|
| F02 rim top outer edge | R `round_rim_top_outer_edge` 0.545 | R 0.478 (REDUCED) | rim wall 1.18 thick cannot hold both measured top rounds (0.649 inner + 0.545 outer); the inner one is built first at target | yes, `export_check.json#fillets`, fillets.json |
| F13 shroud top inner edge | R `round_shroud_top_inner_edge` 0.625 | R 0.503 (REDUCED) | shroud wall ~1.05–1.1 thick cannot hold 0.614 + 0.625 | yes |
| F01 rim concave junctions | `T0_concave_r` reused (plan v1) | `rim_concave_r` [1.194, 1.401] measured | measured after the self-check | params.json |
| pocket junction corners | sharp (assumed, plan v1) | `pocket_concave_r` [3.000, 2.791] measured, filleted on the pocket tool | self-check found the corners rounded | params.json |
| side collar outer cut | vertical wedge at the gap angles (plan v1) | tilted plane (`collar_B*_cut_plane`) + flat-floor wedge | the ring boundary follows a 27° plane; wedge walls left 1.8 mm misses | params.json, change log |
| unused params | — | none (build_log.txt has no UNUSED line) | | |
| connector header interior | not modelled | not modelled | unscanned header; three small scan patches at z ≈ 0 near the −Y inner wall (x ≈ −22, −16, −6.5) are header features | limitation |

## 1. Strategy summary

A stepped moulded housing whose plan-view tiers are **offsets of one core outline**: the corner
centres (`core_*`, `bump_*`) are constant across tiers and only the offset radius changes
(`measure/params.json`, core fits spread ≤ 0.13 mm except bump_TL 0.39). So the ONE sketch is the
core outline (a skewed quadrilateral + the +Y bump rectangle); each tier is `offset(core, R_tier)`
extruded over its measured z band (strategy: sketch + extrude, sub-bodies unioned). A 45.1° half-space
cut makes the −Y chamfer on T3 and the button-band bar. Sub-bodies add the button band disks, collars,
button caps (B2 circular with its measured tilt, B1/B3 oval with inclined top planes), the connector
shroud, the bent mounting tab (YZ profile extrude trimmed by its drafted side planes) and four latch
hoops. Cut tools make the rim pocket, screw holes, shroud interior, collar sector gaps and the tab hole.
No revolve (not a turned part), no loft.

## 2. Expectations (reported, not gated)

- Expected ops before fillets: **~26** (tier prisms 4, pocket 1, chamfer 1, band 4, collars 3,
  sector cuts 2, caps 3, holes 1 (6 tools), shroud 2, tab 4, hoops 4 (pattern-like, placed per measured x)).
- Expected face count: **300–520**. Estimate: tier prisms 4 × ~14 (8 walls incl. arcs + concave
  fillets + 2 caps) ≈ 60 minus merged caps; pocket ~14; chamfer 2; band 10; collars 6; sector cuts 8;
  caps 3 × 3; screw holes 2 × 7; shroud ~20; tab ~25; hoops 4 × ~14 ≈ 56; plus face splits where
  tiers meet ≈ ×1.5.
- Expected surface types: planes, cylinders (circular), elliptic cylinders (B1/B3 caps; OCC stores
  them as B-spline or ellipse-extrusion surfaces), no loft B-splines.

## 3. Ordered feature list

| F## | Operation | Datum / plane | Driving params (source) | Acceptance (checkable on the STEP) |
|---|---|---|---|---|
| F01 | rim prism: `outline(rim_out_R_main, rim_out_R_bump)` extruded z 0..`rim_top_z` | XY @ 0 | `core_*`, `bump_*`, `rim_out_R_*`, `rim_top_z` (scan) | outer rim offsets = params |
| F02 | pocket cut: `outline(rim_in_R_main, rim_in_R_bump)` z 0..rim_top+1 | XY @ 0 | `rim_in_R_*` (scan), `pocket_concave_r` (assumed sharp) | floor at z 0, wall t ≈ 1.2 |
| F03 | T0 prism z `T0_bottom_z`..0, concave fillets `T0_concave_r` (local, before union) | XY | `T0_R_*`, `T0_bottom_z`, `T0_concave_r` (scan) | tier wall offset = T0_R_main |
| F04 | T2 prism z `T2_bottom_z`..`T0_bottom_z`, concave fillets [L,R] | XY | `T2_*` (scan) | |
| F05 | T3 prism z `T3_bottom_z`..`T2_bottom_z`, concave fillets [L,R], then −Y chamfer half-space cut | XY; chamfer plane | `T3_*`, `chamfer_normal`, `chamfer_offset` (scan) | chamfer at 45.1°, plane = params |
| F06 | band bar: polygon x from `band_disk_L.cx` to `band_disk_R.cx`, +Y edge through `band_top_y` at x = ∓16, z `band_bottom_z`..`T3_bottom_z`, chamfer cut | XY | `band_top_y`, `band_disk_*`, `band_bottom_z` | |
| F07 | band end disks L/R (cylinders) z band_bottom..T3_bottom | XY | `band_disk_L/R` [cx, cy, r] | |
| F08 | B2 collar cylinder r `collar_B2_r` at the origin, z `collar_bottom_z`..`T3_bottom_z` | origin axis | `collar_B2_r`, `collar_bottom_z` | |
| F09 | B1/B3 collars (cylinders) z collar_bottom..band_bottom | XY | `collar_B1`, `collar_B3` | |
| F10 | outer collar cuts: material under the fitted tilted plane `collar_B*_cut_plane` (ramps) within r + 2 of each side collar, plus a flat-floor wedge (`collar_B*_floor_sector_deg`, up to `collar_B*_sector_floor_z`) | about each collar centre | `collar_B*_cut_plane`, `collar_B*_floor_sector_deg`, `collar_B*_sector_floor_z` (scan) | ring open on the outer side, ramp follows the plane |
| F11 | B2 cap: cylinder r `cap_B2_r` on the axis (`cap_B2_axis_dir`, `cap_B2_axis_xy0`), trimmed below by the top plane | tilted axis | `cap_B2_*` | top plane = params |
| F12 | B1/B3 caps: elliptic cylinders (`cap_B*_ellipse`) z top-plane..−14.5 (−14.5 lies inside the band disks: documented overlap), trimmed by the inclined top plane | XY | `cap_B1_*`, `cap_B3_*` | oval a/b = params |
| F13 | connector shroud: rounded-rect tube (`shroud_outer`, `shroud_outer_corner_r`, inner `shroud_inner`) z 0..`shroud_top_z` | XY @ 0 | shroud params | |
| F14 | shroud interior cut down to `shroud_inner_floor_z` | XY | `shroud_inner`, `shroud_inner_floor_z` | |
| F14b | (it2) scanned header-base pads on the interior floor against the −Y inner wall | XY | `header_pad_1`, `header_pad_2` (scan) | pad tops = params |
| F15 | screw holes ×2 (one tool set per hole): counterbore r to `screw_cb_floor_z`, through r to the front bore, front bore r from below band_bottom up to `screw_*_front_top_z` | XY | `screw_*` | radii = params |
| F16 | mounting tab sub-body: YZ profile (plate + leg + flange region) built from the fitted plane lines, extruded ±25 and trimmed by the drafted outer flange planes; channel (flange region) trimmed by the inner flange planes and subtracted; hole cut | YZ + tilted planes | `tab_*_plane`, `tab_end_y`, `tab_flange_bottom_z`, `tab_hole` | 1 solid, hole r = param |
| F02b | inner latch bosses ×3 (behind H1, H2, H4): boxes from the rim wall (0.3 overlap) to the measured inner face, z 0..`boss_top_z` | XY | `boss_mY_L`, `boss_mY_R`, `boss_pY_R`, `boss_top_z` (scan) | boss faces = params |
| F10b | cap-to-collar clearance recesses: cylinder r `collar_*_recess[0]` up to the inner ceiling; B1 ramp under `collar_B1_recess_ramp_plane` (capped at the floor); floor sector up to the collar floor | about each collar | `collar_B2_recess`, `collar_B*_recess`, `collar_B1_recess_ramp_plane`, `collar_B*_recess_floor_sector_deg` (scan) | recess ceilings = params |
| F17 | latch hoops ×4: U-frame box from the T0 wall (+0.3 overlap) to `outer_y`, z `hoop_bottom_z`..top, window cut between the legs, floored by the measured catch ramp plane | XZ | `hoop_H1..H4`, `hoop_H*_ramp_plane` | |
| F18 | union everything, `.clean()`, export in two frames | — | `intake/alignment.json` | 1 valid closed solid in both frames |

## 4. Intake feature map (CHK-ENUM)

| Intake feature | Built by | or: out of scope because |
|---|---|---|
| E01 back floor | F02 (pocket floor at z 0) | |
| E02 rim wall + bump | F01, F02 | |
| E03 tiers | F03–F05 | |
| E04 −Y chamfer | F05, F06 | |
| E05 button band | F06, F07, F08 | bar/disk junction blends not modelled (declared) |
| E06 collars | F08, F09, F10 | |
| E07 B2 cap | F11 | |
| E08 B1/B3 caps | F12 | |
| E09 screw holes | F15 | unscanned mid-bore assumed continuous |
| E10 connector shroud | F13, F14 | header pins / interior not modelled (unscanned) |
| E11 mounting tab | F16 | |
| E12 latch hoops | F17 | catch lips / ramps not modelled |
| E13 logos, icons | — | cosmetic relief (≈0.1–0.3 mm) |
| E14 small edge blends | — | declared simplification (params.json simplifications) |

## 5. Fillet / chamfer plan (CHK-FILLET)

| F## | Edges (selector rule) | Target param | Fallback radii | Order |
|---|---|---|---|---|
| F03 | the 2 vertical concave edges of the T0 prism at the bump junctions (line edges ∥ Z within 0.6 mm of the computed junction) | `T0_concave_r` | none | local, on the tier prism before the union (the union merges the edge with neighbouring tiers) |
| F04 | same on T2, L and R separately | `T2_concave_r` [L, R] | none | local |
| F05 | same on T3, L and R separately | `T3_concave_r` [L, R] | none | local |
| F01 | rim outer concave junctions | `rim_concave_r` [L, R] | none | local |
| F02 | pocket junction (on the pocket tool) | `pocket_concave_r` [L, R] | none | local, before the cut |
| F02 | rim top inner edges, then outer edges | `round_rim_top_inner_edge`, `round_rim_top_outer_edge` | outer: wall − inner − 0.05 (wall too thin for both) | after the pocket cut, before bosses/tab/hoops are fused |
| F03/F04 | T0 / T2 bottom outer edges | `round_T0_bottom_edge`, `round_T2_bottom_edge` | none | local on the tier prism |
| F05 | T3 bump bottom edges | `round_T3_bump_bottom_edge` | none | local, before the chamfer cut |
| F06 | band bar +Y bottom edge | `round_band_top_bottom_edge` | none | local on the bar |
| F11/F12 | cap top edges | `round_cap_B*_top_edge` | none | local on each cap |
| F13 | shroud top outer / inner edges; inner vertical corners in the cut tool | `round_shroud_top_*`, `round_shroud_inner_vertical_corner` | 0.5 × wall − 0.02 (wall too thin for both) | local on the tube |
| F16 | tab end top edge | `round_tab_end_top_edge` | none | local on the tab |

## 6. Unscanned or invented geometry (provenance)

| Item | Value | Source tag | Why it is needed |
|---|---|---|---|
| shroud interior floor | `shroud_inner_floor_z` (deepest scanned wall point) | scan extent; true floor assumed | interior header not scanned |
| screw through-bore between z −5.9 and the front bore | r = `screw_*_through_r` | assumed continuous | unscanned; photo 2 shows open holes |
| front bore depth | `screw_*_front_top_z` (scan extent) | assumed stop | bore continues in reality |
| slot between shroud and rim | closed at z 0 (`shroud_slot_note`) | assumed | unscanned below z 0 |
| B1/B3 cap upper end / B2 cap upper end | −14.5 / collar region | construction overlap inside the band/collar solid | caps must join the housing (assembly fused into one solid) |
| hoop overlap into the wall | 0.3 mm | construction overlap | hoops must fuse to the wall |
| cut-tool overshoots | 1.0 mm (documented clearance) | construction | booleans |

## 7. Known risks

- Assembly fused into one solid: the cap/collar clearance gaps (unscanned) are closed.
- Many coincident planar faces between tiers (z levels shared): unions may leave extra seam faces.
- The ellipse caps: OCC may build elliptic-cylinder faces as B-splines; census will show them.
- Tab trimming by drafted planes: planes nearly parallel to X faces; checked by volume and validity.

## 8. Change log

All inside iteration 1, before verify (builder self-check on the full-res scan, datum frame, no ICP;
NOT QA). Each step went back to measure first (params regenerated and re-validated), then rebuilt.
- build 1: 205 faces. Self-check scan→CAD p95 0.343 / max 1.76. Hot spots: rim inner wall behind
  three latch hoops (missed at intake: inner latch bosses, CHK-ENUM finding E15), front screw bores
  (offset from the counterbore axis).
- build 2: + F02b bosses, front bore centres → p95 0.289. 2/3 of the >0.3 mm points lay within 1 mm
  of a sharp CAD edge.
- build 3: + measured edge rounds (`round_*`, measure_edges.py) → p95 0.240, max 1.76 (side collar gaps).
- builds 4–6: side collar outer cut re-measured as a tilted plane + floor wedge (E18), cap-to-collar
  clearance recesses (E17) → >0.8 mm points 655 → 105.
- builds 7–9: B1 recess ramp plane, hoop catch-ramp planes (E16), measured rim / pocket junction
  fillets → p95 0.216, p99 0.394, 14 points > 0.8 mm (header interior patches, one B1 cap hook).
- final: 375 faces (plan 300–520), 20 fillets OK + 2 REDUCED (declared in §0).

### it2 (after verify it1 REVISE, `_it1_SUPERSEDED/qa/VERDICT.md`)

Route geometry (`init_run.py supersede --route geometry`). Changes, and nothing else:
- measure: + `header_pad_1`, `header_pad_2` (verify it1 scan→CAD cluster 0, pin-header base at z ≈ 0).
  Param diff vs it1: only these two rows (edge rounds re-used from it1 `m_edges.json`).
- model: (a) the T3 bump bottom-edge round is applied before the junction fillets, because in it1 it ran
  along the tangent chain onto the main +Y and end edges (verify it1 CAD→scan clusters at z −13.19:
  "lip" on the band +Y edge, band ends x ≈ ±33.5); (b) band bar, end disks and B2 collar reach
  `FUSE_OVERLAP` into T3 so the union leaves no zero-thickness seam at the T3 bottom; (c) F14b pads.
- Builder self-check (not QA): scan→CAD p95 0.215, max 0.813 (1 of 200k samples over 0.8); the it1
  CAD→scan band clusters are gone. The unscanned openings (shroud interior, shroud-to-rim slot,
  screw bores) are unchanged: nothing measured can close them.
- 367 faces.

### it3 (after verify it2 REVISE, `_it2_SUPERSEDED/qa/VERDICT.md`) — last allowed loop

Route geometry. Changes, and nothing else:
- measure: + `collar_B1_recess_mid_1`, `collar_B3_recess_mid_1` (10-deg bins where the cap-collar gap reaches
  0.6–1.3 mm below the floor: the B1 cap lip found by verify it2). Param diff vs it2: only these two rows.
- model: the cap-collar recesses are revolved bore-entrance profiles (flat ceiling out to the cap radius,
  straight slope down to the collar bottom at the recess radius) instead of flat-topped cylinders, because
  verify it2 found the flat ceilings over-deep; + the two middle sectors.
- Builder self-check (not QA): scan→CAD p95 0.211, max 0.736 (0 of 200k samples over 0.8). 374 faces.
