# QUESTIONS — conflicts and missing evidence

The skills will not pick an answer to any of these on their own. Q1–Q5 affect the skill
architecture or gate numbers and need an answer from the owner. The rest are record gaps.
They are listed so no skill states them as fact. Per-project details are in the
`## Questions` section of each `analysis/golden/*.md` and `analysis/baseline/*.md` file.

## A. Decisions needed from the owner

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
  `golden-examples/README.md:17` "Delivered … p95 0.157". Was the max miss accepted,
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
