# MODELING PLAN: OD-G10_porta_filter_holder

Iteration: it1 of 3. Written before `build/model.py`. Every value is read from
`measure/params.json` by name; the only literals are documented tool overshoots.

## 0. Build deviations (filled after the build)

| Item | Planned | Built | Why | Declared |
|---|---|---|---|---|
| F03 pocket floors | flat inner/outer step per lug | concave horizontal-axis cylinders per lug (inner floor, outer band), cut from a blank at max(SHELF_Z) | builder self-check (NOT QA) showed flat steps 0.5–0.96 mm off; measure re-fitted the floors (valley_fit.json) | §8, params.json change notes |
| F02 shelf edge | R1.0 (read by eye) | R 2.426 / 2.483 / 1.961 per gap (arc fit) | same | §8 |
| F06 groove | groove r 36.7–37.4 in the lug span | bore recess r 37.379 + groove over the pocket span, z GROOVE_BOTTOM_Z..CHANNEL_Z, cut before the lugs are added | scan shows the bore recessed behind the lugs | §8 |
| F04b | not planned | concave fillet R1.0 at the stop bottom / recess wall | scan shows the rounding (prof_stop_start.png) | fillets.json |
| unused params | — | none (build_log lists none) | | |
Fillets: 2D profile fillets applied to the (r,z) sketches before revolving (logged as
`fillet_2d`), plus one 3D fillet (F04b). All OK at target radius (`fillets.json`).

## 1. Strategy summary

A cup: ONE (r,z) profile revolved 360° gives the outer wall, the stepped rim, the drafted bore,
the plate and the lower wall (closure at the scan extent). The inner stepped ring is built as
angular sectors of revolved profiles: three gap sectors (shelf at its own measured level, lip with
rounded edge) and three lug sectors (two-step pocket, lip). Three bayonet lugs are one instance
each (revolved rectangle over 54°, split by two underside planes, stop block, channel cut) placed
at 120° pitch from the measured lug-1 start. Cut tools last: six rim notches, bore-base grooves
under the lugs, the plate keyhole and holes (photo-inferred). Strategy rows: revolve (D2),
sub-bodies unioned (D3), one instance + placements (D4), cut tools (D5).

## 2. Expectations (reported, not gated)

- Ops before fillets: 9 (F01 revolve, F02 gap sectors, F03 lug sectors, F04 lugs, F05 notches,
  F06 grooves, F07 keyhole, F08 bosses + holes, F09 side hole).
- Faces: base revolve ~14, gap sector ~8 × 3, lug sector ~8 × 3, lug ~14 × 3, notch 4 × 6,
  groove 4 × 3, keyhole ~10, bosses ~4 × 2, side hole 1 → **~150–260**.
- Surface types: planes, cylinders, cones (bore draft, rim ledge, shelf-edge fillet torus),
  tori from the 2D fillets. No B-splines expected.

## 3. Ordered feature list

| F## | Operation | Datum / plane | Driving params (source) | Acceptance |
|---|---|---|---|---|
| F01 | revolve (r,z) profile 360° | axis Z, XZ | WALL_R_OUT, Z_BOTTOM, RIM_LIP_TOP_Z, RIM_LIP_OUTER_R, RIM_LEDGE_Z_AT_38p5/39p8, RIM_OUTER_FILLET_R, RIM_LIP_FILLET_R, BORE_R_Z0, BORE_DRAFT_DEG, FLOOR_Z (scan); PLATE_T, LOWER_WALL_R_IN (assumed) | 1 solid; outer Ø 80.22; rim top z 3.30 |
| F02 | 3 gap sectors: revolve shelf/lip profile over [θs+POCKET_END, θs+120+POCKET_START] | axis Z | SHELF_Z[k], SHELF_EDGE_FILLET_R, LIP_UPPER_R, LIP_LOWER_R, LIP_STEP_Z (scan) | shelf z per gap = param |
| F03 | 3 lug sectors: revolve a blank (lip r LIP_LUG_R to the wall, top at max SHELF_Z) over [θs+POCKET_START, θs+POCKET_END] | axis Z | LIP_LUG_R, SHELF_Z (scan) | blank |
| F04 | lug instance × 3 at θs = LUG1_START_DEG + k·LUG_PITCH_DEG: revolve rect over LUG_SPAN_DEG; stop block to STOP_BOTTOM_Z over STOP_END_OFF_DEG; rest split by the shallow and the ramp underside planes; channel cut | axis Z | LUG_COUNT, LUG1_START_DEG, LUG_PITCH_DEG, LUG_SPAN_DEG, LUG_INNER_R, STOP_END_OFF_DEG, STOP_BOTTOM_Z, UNDERSIDE_Z_AT_7, RAMP_START_OFF_DEG, UNDERSIDE_Z_AT_RAMP, RAMP_Z_AT_54, CHANNEL_INNER_R, CHANNEL_Z, CHANNEL_START/END_OFF_DEG (scan) | lug top z 0, inner r 31.68 |
| F05 | 6 rim-notch cut tools (2 per lug) | axis Z | NOTCH1_START_OFF_DEG, NOTCH2_START_OFF_DEG, NOTCH_WIDTH_DEG, NOTCH_FLOOR_Z (scan) | lip absent in 6 × 7.5° |
| F03b | per lug: cut the band by two fitted concave cylinders (outer valley, pocket inner floor) | horizontal axes at θc | VALLEY_OUTER_THETA_C/ZMIN/RC, POCKET_INNER_THETA_C/ZMIN/RC, POCKET_RISER_R (scan) | floors follow the fits |
| F06 | 3 bore recess + groove cuts over the pocket span (before the lugs) | axis Z | BORE_RECESS_R, GROOVE_R_IN, GROOVE_BOTTOM_Z, CHANNEL_Z (scan) | recess r 37.38 |
| F04b | stop root fillet | stop bottom arc edges | STOP_ROOT_FILLET_R (scan) | fillet OK |
| F07 | keyhole through-cut: central circle + two lobes | plate | KEY_* (photo-inferred) | opening present (photos 1, 2) |
| F08 | 2 raised bosses + through holes | plate top | BOSS_THETA_1, BOSS_PITCH_DEG, BOSS_PCR, BOSS_OD, BOSS_HOLE_D (photo-inferred), BOSS_H (assumed) | 2 holes |
| F09 | side through-hole | plate | SIDE_HOLE_* (photo-inferred) | 1 hole |

Allowed ops only (revolve, split by plane, boolean). No lofts.

## 4. Intake feature map (CHK-ENUM)

| Intake feature | Built by | or out of scope because |
|---|---|---|
| F01 outer wall | F01 | |
| F02 rim lip + ledge | F01 | |
| F03 rim notches | F05 | |
| F04 drafted bore | F01 | |
| F05 lugs | F04 | |
| F06 lug channel | F04 | |
| F07 lug stop | F04 | |
| F08 lug underside | F04 (planes through the scanned lower edge; surfaces assumed) | |
| F09 shelf | F02 | |
| F10 under-lug pockets | F03 | |
| F11 lip ring | F02, F03 | bead detail beyond the two radii simplified |
| F12 plate top | F01 | |
| F13 keyhole | F07 | |
| F14 screw bosses | F08 | |
| F15 side hole / dimples | F09 / — | dimples cosmetic, not modelled |
| F16 flange below z −27.84 | — | outside the scan (coverage C2) |
| F17 bore-base groove | F06 (lug sectors) | gap-sector groove 0.2–0.3 deep, not modelled (declared simplification) |

## 5. Fillet / chamfer plan (CHK-FILLET)

| F## | Edges | Target param | Fallback | Order |
|---|---|---|---|---|
| F01 | rim lip outer corner, bore top corner (2D profile vertices) | RIM_LIP_FILLET_R | none | in the sketch, before revolve |
| F01 | rim outer corner (ledge → outer wall) | RIM_OUTER_FILLET_R | none | in the sketch |
| F02 | shelf → lip upper wall corner | SHELF_EDGE_FILLET_R | none | in the sketch |
Sketch fillets are applied with `Face.fillet_2d` and logged through `FilletLog.log`; a 2D fillet
that fails aborts the build (no silent skip).

## 6. Unscanned or invented geometry (provenance)

| Item | Value | Source tag | Why |
|---|---|---|---|
| plate thickness | PLATE_T 2.5 | assumed | the underside is not scanned (C1) |
| wall below the plate, inner r | LOWER_WALL_R_IN 37.0 | assumed | a solid needs a closure (C1, C2) |
| bottom closure face | Z_BOTTOM | scan extent | the scan ends there (C2); not a real face |
| lug undersides, stop block radial depth | planes through the scanned lower edge; stop to the bore | scan edge + assumed | hidden (C4) |
| region under the shelf/pockets | solid down to the plate | assumed | hidden (C1) |
| keyhole, bosses, holes | KEY_*, BOSS_*, SIDE_HOLE_* | photo-inferred / assumed | photo-only (C3) |

## 7. Known risks

- Shelf/pocket waviness (up to ~0.4 mm in-sector) and the 0.19 mm lug-ring offset are not modelled
  (params.json#simplifications); they will show as moderate scan→CAD deviation there.
- Lug 3's lower inner face beyond +44° is a scan coverage gap; its ramp copies lugs 1–2.
- Unscanned CAD faces (C1–C4) will show up in raw CAD→scan; the intake card lists the coverage
  facts that verify may use.

## 8. Change log (all within it1; no verify has run yet)

Every change below came from the **builder self-check** (`build/selfcheck/selfcheck.py`, datum
frame, no ICP, NOT QA). Each geometry change went back through measure (new fitted params from
the scan, `measure/src/valley_fit.py`), never a number tuned in the model.

| Attempt | Change | Self-check scan→CAD p95 / max (NOT QA) |
|---|---|---|
| 1 | initial plan (flat per-lug pocket steps, shelf edge R1.0, groove in the lug span) | 0.341 / 0.958 |
| 2 | floors → fitted concave cylinders; shelf edge → arc fit; bore recess behind the lugs | 0.235 / 0.890 |
| 3 | recess/groove extended to the pocket span (scan: r 37.2–37.46 at the pocket ends) | 0.217 / 0.805 |
| 4 | F04b stop root fillet R1.0 (measured) | 0.217 / 0.761 |
Also found in the self-check: the outer wall is unscanned over θ 38–151 at all heights; the
intake card coverage row C6 was corrected from the scan (not from the CAD).
Final: 1 solid, 182 faces, all analytic (`face_stats.json`), volume 40,425 mm³.
