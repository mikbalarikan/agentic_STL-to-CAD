# MODELING PLAN: <part>

<!-- Written by stl-re-rebuild-build123d BEFORE build/model.py (SYNTHESIS D1).
     Adapted from baseline/oomwoo-re-pipeline/TEMPLATES/MODELING_PLAN.md. The org-specific
     manager/PR loop is dropped (analysis/SYNTHESIS.md section 3). The anti-Lego rules and
     the expected op count are kept, and an expected face-count range is added (reported,
     not gated: QUESTIONS.md A/Q3).
     Iteration: it<N> of 3 (RE_SPEC.md:248-250). -->

## 0. Build deviations (fill in after the build; empty = none)

| Item | Planned | Built | Why | Declared to verify/deliver |
|---|---|---|---|---|
| e.g. F05 fillet | R1.5 (hub_fillet) | R0.75 (REDUCED) | R1.5 fails against F03 hole edge | yes, export_check.json#fillets |
| e.g. unused param | `rib_h` | not used | rib merged into F02 profile | yes |

## 1. Strategy summary (3–6 lines)

What the part is. The dominant silhouette and the ONE profile or sketch that captures it.
The main symmetry (revolve axis / mirror / polar pattern). What is added to or cut from it.
Which strategy rows from `references/strategy-catalogue.md` apply.

## 2. Expectations (reported, not gated)

- Expected ops before fillets: **N** (a pattern counts as one op).
- Expected face count: **MIN–MAX**. Show the estimate as faces per op × instances.
- Expected surface types: e.g. planes + cylinders + cones; B-spline only at fillet corners
  or in the F## loft.

## 3. Ordered feature list

| F## | Operation | Datum / plane | Driving params (source) | Acceptance (checkable on the STEP) |
|---|---|---|---|---|
| F01 | revolve (r,z) profile | axis Z, XZ half-plane | `bore_dia` (caliper), `od` (scan), … | Ø re-measured on STEP = param; 1 solid |
| F02 | extrude hex, cut | XY @ `hub_top_z` | `hex_af` (caliper-photo), `hex_phase_deg` (scan) | AF on STEP section = param |
| F03 | cut tool × n at measured θ | XY | `hole_theta_1..n` (scan, unequal kept), `hole_dia` | n holes present, θ within param |
| … | | | | |
| Fnn | fillets / chamfers (last unless noted in §5) | named edges | `*_fillet` params | fillet_log all OK, or declared in §0 |

Allowed operations: sketch-on-plane, extrude, revolve, non-ruled loft through fitted
sections, sweep, boolean, fillet/chamfer, pattern. Forbidden: `ruled` lofts or
`Polyline` stacks of scan slices, and stacked prisms for smooth faces
(`RE_SPEC.md:258-273`).

## 4. Intake feature map (CHK-ENUM)

| Intake feature (INTAKE_CARD.md) | Built by F## | or: out of scope because |
|---|---|---|
| | | |

## 5. Fillet / chamfer plan (CHK-FILLET)

| F## | Edges (selector rule) | Target param | Fallback radii (reason) | Order: last / local-after-F## (reason) |
|---|---|---|---|---|

## 6. Unscanned or invented geometry (provenance)

| Item | Value | Source tag (assumed / photo-inferred / standard) | Why it is needed |
|---|---|---|---|
| e.g. core tube tying sub-bodies | Ø… | assumed | single solid needs a connector (cf. OD core tube) |

## 7. Known risks

Occlusions, uncertain counts, soft features, near-tangent booleans. For each one, say
what will be reported if the build meets it.

## 8. Change log (plan edits during the build, and the parameter diff vs the previous iteration)
