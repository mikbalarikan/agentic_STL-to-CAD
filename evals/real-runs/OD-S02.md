# Real run: OD-S02 steam rod (2026-09-28)

The second real run of the v1 skills: a coffee-machine steam wand. It is an assembly (black connector rod
with O-ring seats, a knob with a lever paddle, a sleeve with a sealing band, a bent Ø6 steel tube, a
white bushing and a steel tip) scanned as one mesh. Ikbal supplied the STL and two photos, with no
calipers. Records are copied under `OD-S02/`; the delivered zip holds the full run.

## Inputs and decisions (`OD-S02/DECISIONS.md`)
- Scan: 499,164 faces, one body, not watertight, 33 open loops. Ikbal confirmed it is the original
  full-resolution export.
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm, from the message "p95 plastik parça toleransı".
- Scan-only. Owner decision PART-CLASS: one fused solid (multi-body is a separate job).
- Datum: axis primary on the tapered spigot (cone residual, section-circle refined), origin on the knob top
  face, clock on the steel tube leaving the elbow. The STOP rule was met only on the self-referential
  path, recorded as an estimator mismatch, same class as OD-H22 D1.

## Loops

| it | Verdict (independent verify) | Cause | Change |
|---|---|---|---|
| 1 | REVISE (geometry) | scan inside the CAD bushing window pockets (masked s→C max 1.265) | — |
| 2 | REVISE (geometry) | window depth / bore depth fixed; bend, lever perimeter and hub still off (Z2, Z3, Z4) | 2 params: assumed → scan lower bounds |
| 3 | REVISE (geometry) → **HALT** at loop 3 | Z4 s→C p95 0.301 from an unmodelled bushing-top collar; the other misses are non-geometric | bend on the scanned-centreline spline, lever round 1.2 → 1.946, tip neck |

Ikbal resolved the HALT with "Kabul et, teslim et". Verify re-assembled the same numbers as
`BAND_NOT_MET`, and `ACCEPT-BAND` cites gate `34a11505e84d`. Delivered as
`OD-S02_steam-rod_RE_BAND_NOT_MET_2026-09-28.zip` (deliverables + source; large regenerable
intermediates are listed in `PACKAGE_INDEX.md`).

Final gate (`OD-S02/gate.json`):
- scan→CAD masked (M1 = pre-declared torn-flash box) passes; unmasked it misses because of the torn flash.
- Observable CAD→scan misses. The cause is unscanned window floors and bore walls plus scan holes,
  which the observability ray test counts as visible.
- Zones Z1 rod, Z2 tube and Z3 lever pass. Z1/Z2 CAD→scan pass only with the QA-added M2 mask.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-intake-datum/scripts/align.py` | axis-primary crop is an infinite cylinder; a cone reads as residual; normals-eigen axis is 0.44–0.58° off on a partial cone; no clock for a second cylinder axis | fixed (opt-in `crop_axial`, `surface: cone`, `refine: section_circles`, `axis_direction` + `clock.noise`; datum-cookbook §3.1) |
| 2 | `datum_fit.py noise` vs `align.py` | STOP compares different estimators (one-loop IRLS vs Kåsa / face residual) | open (QUESTIONS F) |
| 3 | `stl-re-rebuild-build123d/scripts/export_frames.py` | a fused torus + tangent cylinders tessellated with holes in the CAD STL while every STEP check passed | fixed (STL must be one watertight body) |
| 4 | `stl-re-measure-intent` scripts | one datum Z only; multi-axis parts need run-local per-axis fits and a frame transform for `pattern_count.py` | open (QUESTIONS F) |
| 5 | trimesh `Path3D.discrete` | drops open section chains (known from dreame_mop) | hit again; `mesh_plane` used |
| 6 | `stl-re-verify` (12 items, three verify agents) | ungraded interface zones when `interface_max_mm` is null, zone/whole CAD→scan split mismatch, no section-circle datum audit, overlays pre-ICP, observability blind to holes/open bores, census definition mismatch, no revise/defects section in `verdict.py render`, no CHK-LIKE4LIKE tooling, no hole-edge treatment for s→C, frame-dependent zone pass/fail not flagged, `SKILL.md:58` path, silent OOM of parallel runs | open (details in `OD-S02/VERDICT.md`, QUESTIONS F) |
| 7 | `stl-re-deliver/scripts/make_manifest.py` | `decisions/accept_band.md` (the owner's acceptance evidence) is `unclassified` | open |
| 8 | `package_zip.py` | default `--max-source-mb 25` kept 25 MB mesh copies (zip 158 MB); ran with 5 → 80.7 MB | open (consider a lower default) |

Process deviations (declared in DECISIONS.md): the intake card and the modelling plan were written after the
measure/self-check passes.
