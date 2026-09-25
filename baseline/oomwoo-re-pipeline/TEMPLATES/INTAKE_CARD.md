# INTAKE CARD — <OOM-Xnn part name>
<!-- Produced by re-mesh-analyst into <PART>\6_RE_work\INTAKE_CARD.md.
     Presented verbatim at the external gate. Keep it under one page. -->

## 1. What it is (from photos + mesh)
Function, how it mounts/interfaces with the OOMWOO chassis, moving vs static.

## 2. Scan health
Units verdict (vs photo plausibility — confirmed later by ENV calipers), bbox,
watertight?, hole/occlusion map, artifact zones, decimation applied (raw → working tri count).

## 3. Functional surfaces & interfaces (each becomes a gate zone)
| Zone | Surface | Why functional | Caliper-coverable? |
|---|---|---|---|

## 4. INTERIOR structure (mandatory — v1 lesson: ribs were missed)
Ribs, bosses, webs, pockets visible through openings or inferred from photos.

## 5. Datum plan
Name all three, each with a WHY tied to part function (mating face beats biggest face):
- **Primary** (levels): which flat region → XY @ Z=0, and why it's the functional seat.
- **Secondary** (clocks): which bore axis or second plane → +X/+Z (axis fit from
  normals, never bbox center).
- **Origin** (pins): the feature intersection defining (0,0,0), e.g. bore axis ∩ base
  plane, or symmetry-plane intersection.
This becomes F00 in the MODELING PLAN — a gated feature the manager must approve
before any sketch is drawn.

## 6. Rebuild strategy per region
extrude-intersect / revolve / loft / sweep per region; expected symmetry
(revolve axis, polar patterns, mirror planes). The full ordered feature list with the
FEATURE BUDGET lives in the separate MODELING PLAN (`TEMPLATES\MODELING_PLAN.md`) —
this section is the summary the plan expands.

## 7. Risk flags
Occlusions, wear, soft features, multi-body scans, anything likely to HALT.

## 8. MEASUREMENT REQUEST (→ pre-filled into 5_reference\MEASUREMENTS.md)
8–15 dims, priority order: 3 envelope dims first, then every caliper-coverable
functional dim from §3, then wall thicknesses. State per dim WHERE to place the
caliper jaws (reference the photo).
