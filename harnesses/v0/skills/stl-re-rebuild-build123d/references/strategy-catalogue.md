# Strategy catalogue: lessons from the five golden feature trees

This file used to reproduce each golden part's full, numbered build sequence with its own
measured coordinates. That is the actual solution for a part in the golden set, so it is not
restated here: read `analysis/golden/<part>.md` §6 (the tree) and §11 (the reusable code) for
the real sequence and numbers if you need them. What follows is the strategy each part used,
the general lesson, and what to copy or avoid — enough to plan a rebuild without reading the
answer.

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

## DRM screw cap: prismatic + envelope

`golden-examples/dreame_brush-caps/report/source/build_screw.py`; `analysis/golden/dreame_brush-caps.md` §6.

Strategy: a prismatic silhouette intersected with a turned envelope for the corners, a
revolved cone body, a set of tilted-cylinder dimple cuts with a computed tilt, a compound cut
for a non-round drive hole, and fillets applied throughout with a full OK/FAILED log kept
(rather than assumed). See the golden source for the exact sequence, dimensions and derived
angles.

**Copy:** geometric edge selection (type + Z + radius), logged fillets, dual-frame export
(`frames.py`). **Avoid:** the hard-coded output path at the call site (`build_screw.py:106`).

## DRM snap cap: revolve + span-revolved legs (official max band missed)

`golden-examples/dreame_brush-caps/report/source/build_snap.py`.

Strategy: a revolved body, an underside ramp cut, a top-edge fillet applied *before* a later
union would have split it (the local-fillet exception), then a repeated leg/hook feature
revolved over a measured half-angle and unioned at its measured (unequal) placement angles,
plus a repeated frustum-cup feature at its own measured placement angles. See the golden
source for the exact profile points and angles.

Declared simplifications include treating legs as identical despite a small measured
difference, and using one common placement-circle diameter for the cups (`README.md:82-83`).
The official scan-deviation gate on this part failed on the whole-part max band
(`analysis/SYNTHESIS.md` §0.1) — the build itself was judged valid; the miss is a verify/deliver
matter, not a modelling error.

## OD-H12 pump: assembly as one solid via sub-bodies (100% analytic)

`golden-examples/OD-H12_delonghi-dedica-pump/report/src/build_pump.py:269-287`; `analysis/golden/OD-H12.md` §6.

Strategy: a revolved main body (two half-profiles, unioned, with bores and flats cut from
it), an off-axis coil cylinder kept at its measured (not snapped) centre, an invented hidden
core-tube connector (declared as invented, `README.md:54,65-66`), a sheet-metal-like frame
body, a flange as a hull of a hub and lobes, a repeated screw-boss feature at measured
centres, a terminal-block sub-body, and openings cut last so an earlier body does not refill
them. See the golden source for the exact profile points and placement coordinates.

Band NOT MET on this part's scan-deviation gate for scan-coverage and simplification reasons,
not CAD quality (`analysis/golden/OD-H12.md` §7).

**Copy:** sub-body functions, declared invented connectors, SVD-orthonormalised
dual-frame export (`export_final.py`). **Avoid:** bare, unnamed numeric literals inside
profiles and position-lambda edge filters that break when params change.

## OOM-B02 side brush: revolve + lobed cut + lofted arm × 3 (APPROVED with limitations)

`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/build_OOM-B02.py`; `analysis/golden/OOM-B02.md` §6.

Strategy: a hub revolve including a fitted spline dome, a hex-pocket cut from measured
across-flats and phase, a 3-lobed skirt cut built as a sampled outline, an internal boss and
radial hole, an arm built as a non-ruled loft through many sections normal to a fitted path
(with a tool held a small clearance off a tangent face to avoid an OCC boolean failure), a
3-fold rotational union, and a final radial trim. Fillets are applied last, with a fallback
chain of radii tried until one succeeded — **and the golden never stored which radius was
actually used**, which is the silent-fallback failure mode CHK-FILLET exists to catch. See the
golden source for the exact parameters.

**Copy:** fitted-section loft and the superseded-iteration folder. **Fix:** log the used
fillet radius (`fillet_log.py`), and make `polar_sector` keep true arcs.

## OOM-P03 mop bracket: revolve + polar cut tools (it1 REVISE)

`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/rebuild_OOM-P03.py`; `analysis/golden/OOM-P03.md` §6.

Strategy: a base revolve from a closed half-section with a safety mirror if the volume comes
out negative, a hex boss, a drive stem (added only in it2, after it1 missed it entirely —
CHK-ENUM, CHK-CLUSTER), a square socket tool, several repeated cut-tool families fused and
subtracted once, and a stem-top fillet applied inside a guard that can silently skip it. See
the golden source for the exact counts and dimensions.

**Copy:** fused cut tools with true-arc sectors. **Avoid:** stale comments that drift from
the parameter they describe, and silent fillet skips.

## M02 gear pair: one tooth + pattern + bridge core (counter-example)

`golden-examples/M02-02-03_watertight-design-intent/model.py`; `analysis/golden/M02-02-03.md` §6.

Strategy: one tooth face per gear, patterned around a root cylinder by an explicit loop, a
continuous core-bridge cylinder joining two coplanar gears across their shared transition, and
a through-bore cut guarded by a re-import self-check that raises on failure.

The involute flank was built as a **polygonal** approximation (a many-sided polyline per
flank), which produces a large number of small planar facets that a naive analytic-vs-ruled
face census does not flag, because planar facets count as analytic. Only comparing the face
count against the plan, or looking at the plane-face count and median area, exposes it. Use a
`Spline` through computed involute points instead
(`../stl-re-measure-intent/references/gears.md`, heuristic, n=1: M02).

## Not observed in any golden (use only with a plan justification)

- Tri-axis extrude-intersect as a default prismatic strategy (dropped:
  `analysis/SYNTHESIS.md` §3, D11).
- Shells, sweeps along 3D paths, sheet-metal unfolds and multi-body STEP. There is no
  golden evidence for any of them, so HALT/ask for those part classes
  (`analysis/SYNTHESIS.md` §6).
