# Strategy catalogue: the five golden feature trees

Each entry records the part class, the dominant strategy, the tree as built, the face
result and what to copy or avoid. The full trees are in `analysis/golden/<p>.md` §6, and the
reusable code in §11. The face counts are observed results, **not bands**
(`QUESTIONS.md` A/Q3).

## Choosing a strategy (decision order)

1. **Is there a rotation axis?** Revolve the (r,z) profile first: the whole turned envelope
   in ONE profile, bores included. OD, B02, P03 and the DRM snap all did this.
2. **Is the silhouette prismatic?** Sketch + extrude the dominant outline (hex, pentagon,
   rounded rect), then intersect with an envelope for turned corners (DRM screw).
3. **Several physical parts as one solid?** Build sub-bodies separately and union them.
   Declare every invented connector or core (OD, M02).
4. **Repeated features?** One instance, placed at measured angles (all five).
5. **Openings, slots, pockets?** Build separate tool solids, fuse them and subtract once.
   Cut last whatever a later body would refill (OD U-windows).
6. **Freeform blade or arm?** Use a non-ruled loft through fitted param sections along a
   measured path (B02). Never loft raw scan slices (W01).
7. **Fillets:** last by default. A local fillet goes right after its parent only when a later
   op would destroy the edge, and the reason is logged.

---

## DRM screw cap: prismatic + envelope (56 faces, the only unmasked clean pass)

`golden-examples/dreame_brush-caps/report/source/build_screw.py`; `analysis/golden/dreame_brush-caps.md` §6.

1. Pentagon prism (`pent_apothem`) → ∩ cylinder (`corner_dia`) for turned corners.
2. Taper zone: box minus 5 rotated half-spaces at `chamfer_angle_deg`. Corner edges are
   filleted **on the tool** (local fillet), then the tool is intersected with the body.
3. Revolved disc cone, unioned. The top edge is filleted right after (local).
4. 5× tilted-cylinder dimple cuts (`dimple_R`, tilt derived from two measured depths).
5. Double-D (Circle ∩ Rectangle) cut, web bore, counterbore.
6. Web fillets, counterbore chamfer and the bottom outer fillet come last. Every one is in
   try/except with an OK/FAILED log (`report/screw_build_log.txt`: all OK).

Result: 56 faces, 1 solid (`dreame_brush_screw_cap.log:26`). The census from this skill's
`face_stats.py` is 22 plane, 24 cylinder, 2 cone, 3 torus and 5 B-spline (fillet corners),
with an analytic area share of 0.995. Scan gate p95 0.085 / max 0.245 on the full-res scan
(`analysis/golden/dreame_brush-caps.md` §7).

**Copy:** geometric edge selection (type + Z + radius), logged fillets, dual-frame export
(`frames.py`). **Avoid:** the hard-coded output path at the call site (`build_screw.py:106`).

## DRM snap cap: revolve + span-revolved legs (63 faces; official max band missed)

`golden-examples/dreame_brush-caps/report/source/build_snap.py`.

1. Revolve a 7-point (r,z) profile (bore, OD, step, bore chamfer).
2. Underside ramp: a tilted slab cut. The flat cut at `flat_x` gets two vertical fillets.
3. **OD top-edge fillet before the legs.** This is the local-fillet exception: after the leg
   union, the edge would be split (`build_snap.py:44-48`).
4. Leg + hook: one 10-point (r,z) profile revolved over ±`leg_half_angle`. Its inner-top
   fillet is applied to the instance, and the instance is unioned at the measured, unequal
   `leg_thetas`.
5. 4 cone-frustum cups at the measured `cup_thetas`, then the bore top fillet.

Declared simplifications: identical legs even though one sits ~0.1 mm further out, and a
common PCD for the cups (`README.md:82-83`). Official gate `overall_pass: false`,
max 1.226 > 0.80 (`analysis/SYNTHESIS.md` §0.1). The build itself was valid; the miss is a
verify/deliver matter.

## OD-H12 pump: assembly as one solid via sub-bodies (213 faces, 100 % analytic)

`golden-examples/OD-H12_delonghi-dedica-pump/report/src/build_pump.py:269-287`; `analysis/golden/OD-H12.md` §6.

1. `revolve_body()`: two (r,z) half-profiles (outlet, inlet) revolved and unioned. Bores
   and ±X wrench flats are cut from it.
2. `coil()`: an off-axis cylinder, centre (−0.2, 0.1) kept as measured, not snapped. Its end
   edges are filleted inside the sub-body.
3. **Core tube**: an *invented*, hidden connector tying the coil to the frame, declared in
   `README.md:54,65-66`.
4. `frame()`: rounded-rect sheet ring with notches and slots.
5. `diamond_flange()`: hull of hub + 2 lobes, with an underside pocket from an inward offset.
6. `screws()`: a revolved dome head placed at the measured centres, with crossed recess cuts.
7. `terminal_block()`: YZ profile extrude, fillets inside the sub-body, pockets, tabs, rib
   and a rotated housing.
8. **U-windows cut last**, "because the hub fills them otherwise" (`:279-286`).

Result: 213 faces = 139 plane / 48 cylinder / 24 cone / 2 torus
(`OD-H12-Pump.log`). `face_stats.py` reproduces this exactly. Band NOT MET (p95 0.448) for
scan-coverage and simplification reasons, not because of CAD quality
(`analysis/golden/OD-H12.md` §7).

**Copy:** sub-body functions, declared invented connectors, SVD-orthonormalised
dual-frame export (`export_final.py`). **Avoid:** bare radii and z-stations inside profiles
(3.05, 2.95, 2.6, −21.0 …) and position-lambda edge filters that break when params change.

## OOM-B02 side brush: revolve + lobed cut + lofted arm × 3 (185 faces; APPROVED with 3 limitations)

`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/build_OOM-B02.py`; `analysis/golden/OOM-B02.md` §6.

1. Hub revolve: a meridian of lines, `ThreePointArc` groove and a `Spline` dome through
   fitted points.
2. Hex pocket cut: vertices from `HEX_AF` and phase, corner fillet in the sketch.
3. Skirt 3-lobe + recess: a smoothstep R(θ) outline sampled into a `Spline`, cut as
   Circle − outline. The **tool is held 0.02 mm clear** of the lobe to avoid a tangent
   boolean (`:182-185`; heuristic, n=1).
4. Nub, internal boss (`polar_sector`) and a radial hole on a `Plane(z_dir=u)`.
5. Arm: **non-ruled loft** through 22 `RectangleRounded` sections normal to the r–z path,
   plus a tuft slot cut from the end face.
6. `Rotation(0,0,120k)` × 3 union, then a radial trim `& Cylinder(ARM_R_END)`.
7. Fillets last: seam edges selected by a z/r box, trying R0.8 → 0.5 → 0.3. **The radius
   actually used was never stored** (CHK-FILLET, silent fallback).

Result: 185 faces, including 40 B-spline from the loft and the spline cut (STEP entity grep,
inspection only).

**Copy:** fitted-section loft and the superseded-iteration folder. **Fix:** log the used
fillet radius (`fillet_log.py`), and make `polar_sector` keep true arcs.

## OOM-P03 mop bracket: revolve + polar cut tools (500 faces; it1 REVISE)

`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/rebuild_OOM-P03.py`; `analysis/golden/OOM-P03.md` §6.

1. Base revolve: an 8-point closed (r,z) half-section. A safety mirror is applied if the
   volume is ≤ 0.
2. Hex boss: `RegularPolygon(HEX_AF/√3, 6, major_radius=True)` extruded.
3. Drive stem (added in it2 after it1 **missed** it: CHK-ENUM, CHK-CLUSTER) and a square
   socket tool.
4. `sector_tool` cut tools: 8 kidney windows + 51 tread slots. All tools are fused and then
   subtracted once.
5. Stem-top fillet R0.4 in try/except with an `if top_edges:` guard, which is a **possible
   silent skip**. `FILLET_SMALL` is defined but unused.

Result: 500 faces (559 in another record; `QUESTIONS.md` B). **Copy:** fused cut tools with
true-arc sectors. **Avoid:** the stale "6-fold" comment beside `N_KIDNEY = 8` (a
param/comment drift) and silent fillet skips.

## M02 gear pair: one tooth + pattern + bridge core (2,354 faces: counter-example)

`golden-examples/M02-02-03_watertight-design-intent/model.py`; `analysis/golden/M02-02-03.md` §6.

1. One tooth face per gear, extruded, fused N times around a root cylinder (explicit loop).
2. A **continuous core bridge** cylinder at the smaller root radius joins the two gears across
   a coplanar axial transition (`model.py:76-81`; heuristic, n=1).
3. Through-bore cut. Re-import self-check that raises on failure (`model.py:85-101`).

The involute flank was a **polygonal** `Wire.make_polygon` of 20 samples per flank, which
gives 2,306 planar facets (inspection count). This is not a scan re-tile, but the type
census does **not** flag it: planar facets count as analytic (`face_stats.py` gives
`analytic_area_share = 1.0`, `ruled_like_faces = 0` on this STEP). Only the face count
against the plan, and `plane_face_count` / `plane_face_median_area_mm2`, expose it. Use a
`Spline` through computed involute points instead
(`../stl-re-measure-intent/references/gears.md`, heuristic, n=1: M02).

## Not observed in any golden (use only with a plan justification)

- Tri-axis extrude-intersect as a default prismatic strategy (dropped:
  `analysis/SYNTHESIS.md` §3, D11).
- Shells, sweeps along 3D paths, sheet-metal unfolds and multi-body STEP. There is no
  golden evidence for any of them, so HALT/ask for those part classes
  (`analysis/SYNTHESIS.md` §6).
