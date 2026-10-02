# QUESTIONS — conflicts and missing evidence

The skills will not pick an answer to any of these on their own. Q1–Q5 affect the skill
architecture or gate numbers and need an answer from the owner. The rest are record gaps.
They are listed so no skill states them as fact. Per-project details are in the
`## Questions` section of each `analysis/golden/*.md` and `analysis/baseline/*.md` file.

## A. Owner decisions (resolved 2026-09-25: Ikbal approved the architecture and the recommendations)

- **Q1 → resolved:** the intake declares the band regime (RE_SPEC / baseline-skill / project spec, each with its source); the verdict names it. No single silent default.
- **Q2 → resolved:** the datum audit is run and reported against the RE_SPEC ≤0.3° / ≤0.15 mm numbers, but it is **report-only**, not blocking.
- **Q3 → resolved:** face count and surface-type census are **reported, not gated**. The qualitative anti-patchwork rules (no ruled lofts / polyline stacks of scan slices) stay.
- **Q4 → resolved:** blind replay targets are OOM-B02 and the Dreame screw cap.
- **Q5 → resolved:** `stl-re-deliver` stays a separate skill. Branch stays `claude/skills-v1-kickoff-mtk1l9`.

Original questions, kept for the record:

**Q1. Default deviation band.** Two regimes exist and the goldens used both:
- RE_SPEC Tier-2: p95 ≤1.6 / max ≤4.0 after ICP + skin mask, plus Tier-1 ±0.15 and
  interfaces ≤0.8 (`baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175`). Used by B02 and P03.
- Baseline skill: p95 ≤0.30 / max ≤0.80 plastic, ≤0.15 / ≤0.50 machined, no source
  stated (`baseline/skills/stl2step-build123d/SKILL.md:87`). Used by DRM and OD. DRM snap
  and OD missed it.

Proposal: the intake declares the regime and the verdict names it
(`analysis/SKILL_ARCHITECTURE.md` §5). Should there be a single default? If so, which?

**Q2. Datum audit threshold.** RE_SPEC says ≤0.3° / ≤0.15 mm (`RE_SPEC.md:241`). Both
approved OOM goldens exceeded it: B02 0.429° / 0.451 mm, P03 0.154° / 0.600 mm
(`analysis/golden/OOM-B02.md` §3, `analysis/golden/OOM-P03.md` §3). The metrics also
differ: B02 reports point disagreement, not origin offset. Should the band be kept as
blocking, kept as report-only, or be changed?

**Q3. Surface-quality (Tier-0) numbers.** RE_SPEC is qualitative ("hundreds, not
thousands", `RE_SPEC.md:265-270`). The only numeric form is the W01 tracker cell
(≤ ~600 faces, ≥60 % analytic area, `baseline/oomwoo-re-pipeline/TRACKER.md:32`). M02 has
~2354 planar faces from a polygonal involute (inspection-only count). Should the skills
gate on those numbers, or report face count and surface-type census only?

**Q4. Blind replay targets.** The prompt names M02, but the M02 source scan is not in
the repo and not listed as excluded (`analysis/golden/M02-02-03.md` Q1). Proposed
replacements:
- OOM-B02: full-resolution scan, photos and calipers present.
- DRM screw cap: decimated scan, inspection-only.

Alternatively, can the M02 scan be added?

**Q5. Branch name.** The prompt says `feat/skills-v1`. This environment only pushes to
`claude/skills-v1-kickoff-mtk1l9`, so the work is there. Rename at PR time?

## B. Record conflicts (skills must not state these as fact)

- **DRM snap outcome:** official `overall_pass: false` (max 1.226 > 0.80) vs
  `golden-examples/README.md:14` "Delivered … p95 0.157". Was the max miss accepted,
  and by whom? The README says the table was excluded, but the gate JSON has
  `exclusions: []`. The gate's sha256 inputs match no manifest file. The gate tool
  and masking script are missing (`analysis/golden/dreame_brush-caps.md` Q1–Q4).
- **OD-H12:** 104 vs 105 params; flange hub Ø24.4 (docstring) vs Ø24.1 (params). The
  scan Y extent is ~1.3 mm larger than the CAD and `expected.json`. The T1 derivation
  and residuals are not recorded (`analysis/golden/OD-H12.md` Questions).
- **M02:** how the 27T/Ø21.75 candidate was produced; where module 0.6 came from; where
  the QA tolerances (±0.03/±0.02) came from; missing QA script and `expected.json`.
  Possible link to tracker OOM-M02 (scan-only waiver). RE_SPEC calls "the verifier's
  M02 protocol" the Tier-2 reference (`RE_SPEC.md:174`), but M02 here has no Tier-2 run
  (`analysis/golden/M02-02-03.md` Questions).
- **B02:** the proceed-without directive (07-30) is dated after the it2 build (07-29).
  Hex gap is 124° vs 85°. Screw mask is 16,610 vs 19,222 faces. `_solid.json` and
  `_tess.json` look like it1 outputs. The NX `.stp` is unexplained
  (`analysis/golden/OOM-B02.md` Questions).
- **P03:** it1 verdict overwritten; `alignment_v2.json` cited but missing; photo `140238`
  missing; 500 vs 559 faces; report says "dish" but the code builds a flat slab; the
  photo-transcribed caliper uncertainty is not stated (`analysis/golden/OOM-P03.md`
  Questions).
- **Baseline pipeline:** the "OOM-M02 blend STOP" named in the prompt is not in this
  TRACKER snapshot (`analysis/baseline/oomwoo-re-pipeline.md` §5). Other conflicts:
  - caliper uncertainty ±0.05 (spec) vs ±0.02 (template)
  - scan noise 0.5–0.8 mm vs RANSAC tol 0.05–0.1 mm in the same spec
- **Facet-film:** code defaults disagree with its own rulings. This only matters as a
  lesson (`analysis/baseline/facet-film-transferable.md` §5).

## C. Evidence gaps found while drafting (Phase 3)

- **Datum-fit acceptance:** RE_SPEC says STOP if the residual "RMS + max" exceeds scan noise
  (`RE_SPEC.md:126-129`). The DRM screw plane max was 0.055 mm against rms 0.0072
  (`golden-examples/dreame_brush-caps/report/screw_alignment.json`) and was accepted. The
  intake skill enforces rms only and reports max.
- **No threshold exists** for "uniform" scale disagreement (CHK-SCALE) or for an acceptable
  axis tilt (CHK-TILT). The skills report the values and ask.
- **B02 caliper window:** the skill's simulated two-jaw window on the full-res B02 scan gives
  24.99–27.25. The record says 25.99–27.08 (`OOM-B02/6_RE_work/PARAM_TABLE.md:108-115`).
  F06 = 24.84 is still outside the window, but D-06 = 25.79 (recorded as below the window)
  falls inside it. The window on the delivered STEP matches exactly (25.617–26.850). The
  method difference, probably azimuth or z-station selection around the SAF-1 recess, is
  not recorded.
  *Update (Phase 4 review):* the measure-intent reviewer reproduced the recorded window from
  the golden's lobe+flat argument with the SAF-1 recess left out: R(30°) 13.444 + R(−121°)
  12.530 ≈ 25.99 (`reviews/stl-re-measure-intent.md`,
  `skills/stl-re-measure-intent/references/validation.md`). The skill now reports F06 as
  UNPROVEN (margin smaller than the measured scan offset), not struck.
- **B02 open-edge count:** the intake records 3561; the skill counts 11,466 on the full-res
  scan. The counting convention is not recorded.

## E. Findings from the real run `dreame_mop_bottom_cover` (2026-09-26, prismatic frame, scan-only)

Open for the owner; the run worked around each one and declared it in its `DECISIONS.md`.

- **No prismatic datum in `align.py`.** `origin.xy` accepts only circle / wall-face fits, so a
  rectangular frame with no round feature cannot be datumed. The run used a run-local
  `align_prismatic.py` (3 planes via `datum_fit.level_plane`, same STOP rule, same
  `alignment.json` keys). Candidate: add a `plane` method to `origin.xy` + a tertiary plane.
- **`trimesh` sections drop open chains.** `Path3D.discrete` only returns closed paths; open
  (dangling) section chains of an open scan are silently missing. Use `entities[*].discrete()`
  when you need every trace (`stl-re-measure-intent/scripts/sections.py` should be checked).
- **Warped part vs flat design intent.** The flange drooped ~1.1 mm over 190 mm. No skill says how
  to measure design intent on a warped scan. The run fitted a smooth dz(x,y) field to the flange top
  and measured on a de-warped copy (declared), keeping verify on the original scan. Needs an owner rule.
- **Nested list params.** `param_table.py` rejects lists of points (meridians, outlines); the run
  flattened them into n-tuples with a `note`. A `points` type would be cleaner.
- **Station-profile extrusions and CHK-PATCHWORK.** Extruding fitted scan sections per constant
  x-range gives many narrow planar strips (median plane area ≪ 1 mm²). Not ruled/polyline, but a
  planar-facet warning sign; the census reported it, no rule decides it.

## F. Findings from the real run `dreame_mop_assembly_bottom_cover` (2026-09-30, prismatic frame, scan-only, decimated)

Open for the owner; the run worked around each one with run-local scripts and declared them.

- **Prismatic datum again.** Same gap as §E: `align.py` has no plane origin. The run used a run-local
  3-plane script on `datum_fit.level_plane` (same STOP rule). Draft on the walls (0.74° / 1.08°)
  shows up as CHK-TILT "finding" because the prismatic squareness check has no draft allowance.
- **Open scans → sections by generalized winding number.** Plain `trimesh` sections of this holey
  decimated scan (6,504 boundary loops) cannot be filled. The run measured every section as the
  0.5–0.7 iso-contour of libigl's fast winding number averaged over several stations (mean-of-n),
  then fitted lines + arcs (`measure/occ.py`, `profile_fit.py`). Candidate for
  `stl-re-measure-intent/scripts/sections.py` (new dependency: `libigl`, `scikit-image`).
- **Piecewise-prismatic zones.** A moulded rail = core section + ribs/pockets at definite stations.
  Automatic segmentation by occupancy change works; *gradual* runs (tapers, ramps) must not become
  prism stacks: the run re-sectioned them along another axis, or used a two/three-view envelope.
  No skill describes this; strategy-catalogue could get a "piecewise prismatic zone" row.
- **Lofts and booleans (build123d 0.13 / OCC).** A non-ruled loft through line/arc sections was
  BRepCheck-valid but silently lost volume in later booleans (slab test). Rebuilding each level as
  ONE interpolating spline (241 pts) + closing line, `CheckCompatibility(False)`, fixed it. Coplanar
  faces between a loft cap and a box face also broke unions. Worth an idiom in
  `build123d-idioms.md`.
- **Enclosed voids / zero-area faces after many booleans.** In-memory `is_valid` was True but the
  STEP round-trip had 7 shells and one zero-area face; `export_frames.py` correctly refused. The run
  kept the outer shell (voids filled, logged) and applied `ShapeFix_FixSmallFace` (logged).
- **Build time.** ~150 prisms + 2 lofts: ~30 min per build in this container; `repro_check.py`
  runs it twice more.
- **Single-sided sheets.** Zero-thickness, coherent surfaces (on the wall bead and under the window
  edge) — gasket/film or scanner artefact? CHK-CLUSTER has no rule for zero-thickness clusters.
- **Fine-tessellation validity is a construction problem, not a repair problem (it2→it3).** The
  verify gate (0.005 mm / 0.05 rad, exact vertex merge, BOTH frames) failed on micron-scale defects
  that BRepCheck accepts. Causes found in it3, in order of importance:
  1. *Independently fitted adjacent profiles.* One moulded edge comes out as two curves microns
     apart in neighbouring segments; in the shared cap plane they cross at a grazing angle and the
     boolean leaves tolerant (0.005–0.02 mm) vertices whose faces tessellate with mismatched nodes.
     Fix that worked: snap each segment's vertices (0.03 mm) and supporting lines/circles to the
     axially adjacent segment (optionally to the base), extrude profiles made identical as ONE prism,
     and pick the first construction variant that is closed (logged per zone). Snapping inside a
     segment, or inside a re-sectioned sub-zone, corrupted later fuses silently.
  2. *Planes nearly parallel to a lofted wall.* Zone stations (x = const) inside the x-band of a
     slanted cup wall, or at the x-extremes of a curved cup wall, meet the loft at grazing angles.
     Re-sectioning that band along the perpendicular axis (`force_sub`) removed it in the datum
     frame. Rule of thumb for `stl-re-rebuild-build123d`: no section/station plane within ~1 mm of
     being tangent to a loft surface.
  3. *The QA reads the STEP, not the in-memory body.* The STEP reader heals microns-wide faces into
     degenerate ones; a body closed in memory failed after a round trip, and the scan-frame copy
     (large coordinates) failed where the datum copy passed. A builder-side check should tessellate
     after a STEP round trip in BOTH export frames (proposal: `export_frames.py` runs it and records
     it in `export_check.json`, so rebuild sees what verify will see).
  Repairs that did NOT work on the finished body: global sewing, defeaturing, ShapeFix small
  face > 1e-5 mm, face division, fuzzy loft booleans (out of memory at 15 GB), micron jitter of the
  loft wall (chaotic). The run ended with the scan-frame STEP still showing 21 non-manifold mesh
  edges; the owner accepted it for delivery (run DECISIONS.md 2026-10-02). Open question: should
  `stl-re-verify` grade a tessellation-only defect (B-rep valid, closed, 0 naked edges, open mesh
  edges = 0, non-manifold > 0) differently from a non-closed solid?
- **Variant search cost.** Selecting zone construction variants by a STEP round-trip check made a
  build ~35–60 min in this container; `repro_check.py --timeout-s` needs ≥ 5400.
- **Verify script gap (found by the it3 verifier).** `stl-re-verify/scripts/step_check.py` leaves the
  fine-tessellation watertight result out of `single_valid_closed_solid`, so `verdict.py` recorded
  `geom_fails: []` and still listed BAND_NOT_MET as allowed although SKILL §3 makes a non-watertight
  tessellation a geometry fail; the verifier applied the rule by hand (HALT at loop 3). Fix:
  include `tessellation.watertight` (both frames) in the validity gate, or state that it is
  report-only. The it3 package was delivered on an explicit owner decision despite HALT
  (`make_readme.py`/`repro_check.py` refuse HALT; README written by the orchestrator).
