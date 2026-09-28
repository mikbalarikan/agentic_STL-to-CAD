# MODELING PLAN: OD-E01_Power-PCB

Iteration: it2 of 3 (it1 REVISE, `_it1_SUPERSEDED/qa/VERDICT.md`). Written before `build/model.py` (SYNTHESIS D1).

## 0. Build deviations (filled after the build)

| Item | Planned | Built | Why | Declared to verify/deliver |
|---|---|---|---|---|
| F02 heatsink | solid hubs | hubs with a C-shaped screw channel opening outward (`hs_hub_*` channel x0/x1), spine notch under the TO-220 (`hs_spine_notch`), screw hole through the spine (`q1_tab_hole`) | found by the builder self-check (scan points inside the modelled solid) and re-measured | yes (params rows) |
| F03 TO-220 | straight leads | 3 bent leads following the measured (x, z) paths (`q1_lead_1..3`); body front from faces above the clip | side views: the outer leads bend forward to x ≈ 41 | yes |
| F05 caps | vertical cylinders | leaning cans (2.1–3.0 deg, measured axis) with a base band, sealing groove and body (`cap_C1..C5`); C1 has an SMD V-chip base plate (`cap_C1_base`); C5 is flanged (base 3.85 / waist 3.41 / top 3.91) | per-z-bin wall circles | yes |
| F09 K1/K2 | two boxes | base box + riser with a sloped back (`blk_K*`) | +X face line fit | yes |
| F10 leads | horizontal + vertical | horizontal run + measured 3D descent path (`axlead_*`) | lead bends | yes |
| F08 connectors | housing − cavity | + inner contacts / ribs as boxes (`connpin_*`) | CHK-CLUSTER inside the cavities | yes |
| F12 boxes | top-view footprint | tall parts (> 1.4 mm) use the dominant side-wall faces; terminals / lead rows outside the body get their own boxes; shadowed parts beside R1 / D2 (`box_side_*`) | self-check: top-edge flare and lead toes were read as walls | yes |
| fillets | none | none (`fillets.json` empty by design) | chamfers/rounds are in profiles | yes |
| face count | 700–1300 | 1212 (planes 1039, median plane area 1.08 mm²) | many small SMD boxes; no ruled/B-spline faces | `build/face_stats.json` |

## 1. Strategy summary

A populated power PCB delivered as ONE fused envelope solid. Dominant silhouette: the board
plate — one rectangle sketch with the routed slot and 6 holes, extruded down by the board
thickness from the datum top face (z 0). Everything else is added on top as separate sub-bodies
at their measured positions and unioned once (strategy catalogue: "sub-bodies built separately,
then unioned", "one instance + placements", "sketch + extrude", "cut tools as separate solids").
The heatsink is ONE extruded 2D profile (hub discs + spine + round-ended fin slots − screw
channels). No revolve symmetry, no mirror: every instance keeps its measured position.

## 2. Expectations (reported, not gated)

- Expected ops before union: board (1 extrude + 1 cut group), heatsink (1 profile extrude), TO-220
  (body, tab − hole, 3 leads), clip (1 extruded strap), 5 can frusta, X2 box, 6 faston instances,
  3 connector housings − cavities, 2 base+riser blocks, 4 axial bodies + 7 leads, Y-cap revolve +
  2 leads, 60 SMD boxes → one union.
- Expected face count: **700–1300** (board ~25, 60 boxes × 5 = 300, heatsink ~110, clip ~90,
  fastons 6 × 14 = 84, caps 15, connectors 30, blocks 18, axial + leads ~60, Y-cap ~10, TO-220 ~20,
  plus split faces from the union).
- Expected surface types: planes, cylinders, cones (can frusta), one torus (Y-cap rim). No B-spline.

## 3. Ordered feature list

| F## | Operation | Datum / plane | Driving params (source) | Acceptance (checkable on the STEP) |
|---|---|---|---|---|
| F01 | board: rectangle − slot (rect + round end) − holes H1..H6, extrude z −t..0 | XY @ z 0 | `board_x_min/x_max/y_min/y_max`, `board_thickness`, `slot_y`, `slot_x_end`, `hole_H1..H6` (scan) | outline and hole Ø on STEP = params |
| F02 | heatsink profile: hub discs + spine rect + 12 fin slots + 4 short fin slots − 2 channels; extrude `hs_bottom_z`..`hs_top_z` | XY | `hs_hub_*`, `hs_spine_x`, `hs_fin_01..12`, `hs_shortfin_01..04`, `hs_fin_width_short`, `hs_top_z` (scan), `hs_bottom_z` (assumed) | one extrusion, top at `hs_top_z` |
| F03 | TO-220: body box, tab box − Ø hole (along X), 3 lead boxes | XY / YZ | `q1_body`, `q1_tab`, `q1_tab_hole`, `q1_leads` (scan), `q1_lead_w/t` (standard) | tab against spine face |
| F04 | spring clip: round-ended strap slots along the path, extruded `clip_z` | XY | `clip_path`, `clip_width`, `clip_z` (scan) | strap touches TO-220 and fins |
| F05 | 5 electrolytic cans: cone frustum on the axis through the two wall circles, flat top | axis per can | `cap_C1..C5` (scan) | Ø at the two stations = params |
| F06 | X2 film cap box | XY | `x2_CX1` (scan) | box = param |
| F07 | 6 faston tabs: chamfered blade profile (YZ) extruded by thickness − detent hole; foot box | YZ | `faston_x/y` (scan list), `faston_width/thickness/top_z/chamfer/foot_*/hole_*` (mean-of-n) | 6 tabs at listed x |
| F08 | 3 connector housings − cavity pockets | XY | `conn_J1..J3` (scan) | pocket present |
| F09 | 2 base + riser blocks | XY | `blk_K1`, `blk_K2` (scan) | |
| F10 | 4 axial bodies along Y (cylinders) + horizontal/vertical lead wires | XZ | `ax_R1/D1/D2/L2` (scan), `lead_d` (standard) | |
| F11 | Y-cap: revolve of a rounded-disc (r,z) profile, oriented on the fitted normal; 2 straight leads | fitted axis | `ycap_CY1`, `ycap_lead_1/2` (scan), `lead_d` (standard) | |
| F12 | 60 SMD / low-part boxes | XY | `box_001..060` (scan) | |
| F13 | union of F01..F12 in one fuse, `.clean()`, export both frames | — | — | 1 valid closed solid |

Allowed operations only (extrude, revolve, boolean). No loft, no polyline stacks of scan slices.

## 4. Intake feature map (CHK-ENUM)

| Intake feature | Built by | or: out of scope because |
|---|---|---|
| E01 PCB plate + slot | F01 | |
| E02 H1, H2 | F01 | |
| E03 small holes | F01 (H3..H6) | |
| E04 heatsink | F02 | |
| E05 TO-220 | F03 | |
| E06 spring clip | F04 | |
| E07 electrolytic caps ×5 | F05 | |
| E08 X2 film cap | F06 | |
| E09 Y-cap | F11 | |
| E10 axial resistor | F10 (`ax_R1`) | |
| E11 fastons ×6 | F07 | |
| E12 connectors | F08 (J1..J3), F09 (K1, K2) | |
| E13 8-pin THT device | F10 (`ax_D1`, `ax_D2`) | measure found two axial bodies side by side (Ø≈2.6–2.7), not a DIP |
| E14 SMD power inductor | F12 (box) | |
| E15 SOIC, DPAK, SOT/SOD, passives | F12 | |
| E16 edge pads | — | copper, no height |
| E17 silkscreen, traces, solder joints, label | — | texture < 0.1 mm / solder fillets, declared simplification |
| (measure) axial part between the caps | F10 (`ax_L2`) | found by CHK-CLUSTER in measure |

## 5. Fillet / chamfer plan (CHK-FILLET)

No fillet or chamfer operation. The faston top chamfers are part of the blade profile polygon and
the Y-cap full-round rim is part of its revolved profile (both param-driven), so `fillets.json` is
empty by design.

## 6. Unscanned or invented geometry (provenance)

| Item | Value | Source tag | Why it is needed |
|---|---|---|---|
| board bottom face | flat at z = −`board_thickness` | scan (edge walls) + invented face | solder side not scanned |
| heatsink root | `hs_bottom_z` = 0 | assumed | fin roots occluded |
| component bottoms | every sub-body starts 0.05 mm below z 0 | clearance (documented) | robust union with the board top (no coplanar faces) |
| TO-220 tab back | extends 0.05 mm into the spine | clearance (documented) | robust union (touching faces) |
| connector cavity floors | lowest scan point seen (J1, J2); J3 to the board | scan (partial) | floors not visible |
| TO-220 lead section | 0.8 × 0.5 | standard | not resolvable |
| lead wire Ø | 0.8 | standard | not resolvable |
| Y-cap back face | from the rounded-disc fit | scan (fit of the front) | back not visible |

## 7. Known risks

- Many-body union: OCC may leave the result invalid; report which sub-body, and fall back to
  fusing in groups (same geometry).
- Near-coincident faces: fastons foot vs blade, clip vs TO-220 front face, clip vs fin tips.
- Deviation expectations: occluded regions (under the heatsink, between caps, inside connectors)
  have no scan; board warp (±0.2, corners to −0.35) and unmodelled solder / leads / SMD
  terminations will show as scan→CAD residuals.

## 8. Change log

- it1, build attempt 1: 739 faces; builder self-check (NOT QA: nearest-sample distances, datum frame)
  scan→CAD p95 0.394 / max 1.86.
- it1, attempts 2–6 (same iteration, before any verify): measurement methods refined where the
  self-check showed scan material inside or far from the model — X2 / tall-box walls from side faces,
  heatsink C-channel + spine notch + screw hole, TO-220 bent leads, can profiles and lean, connector
  inner walls and contacts, K riser slopes, 3D lead descents, shadowed SMD parts. Final self-check:
  scan→CAD p95 0.260, p99 0.431, max 1.53 (0.09 % of samples > 0.8). These are builder numbers, not a
  gate; verify re-derives everything.

- it2 (after the it1 REVISE, route measure): params added ['box_bump_K2_1', 'box_bump_K2_2', 'capstem_C5', 'clip_hook', 'hs_spine_hole']; removed ['connpin_J1_08']; values changed ['conn_J1', 'conn_J3', 'connpin_J1_04', 'connpin_J1_05', 'connpin_J1_06', 'connpin_J1_07', 'connpin_J3_02', 'connpin_J3_03', 'q1_tab_hole'].
  Fixes: C5 raised on a stem (board seen under it); J3 cavity floor at the median up-facing face height;
  TO-220 tab hole measured in the tab (it is not coaxial with the spine hole, now `hs_spine_hole`); bump on
  K2's base; clip lower hook around the lower-right short fin. Builder self-check (datum frame, not QA):
  scan→CAD p95 0.259 / max 0.968.

## 9. Notes for verify (facts, not expectations)

- Not scanned, therefore invented: the whole solder side (board bottom face), the lower fin roots and
  the deep fin side faces between the heatsink fins, connector cavity floors, the Y-cap back face,
  the underside of every raised body (R1, D1, D2, L2, Y-cap). The builder's own observability
  estimate put 26 % of the observable CAD sample on the unscanned board bottom.
- A scanned surface lies INSIDE the heatsink spine at z ≈ 21.5 (x 47.4–49.0, y −24.6…−16.7), in the
  plane of the TO-220 tab top; from above the spine top reads 25.3 at the same x, y. Cannot be reached
  by a straight line from outside the scanned spine; looks like a reconstruction artefact continuing
  the tab-top surface. Not modelled.
- Board warp (−0.35…+0.1 mm) is not modelled (flat board, declared simplification).
