# Case: `verdict.py assemble` grades OD/DRM-snap BAND_NOT_MET and B02 APPROVED_WITH_LIMITATIONS

## Skill
`stl-re-verify`

## Input (repo paths)
- OD: `golden-examples/OD-H12_delonghi-dedica-pump/report/deviation_gate.json` (real, in repo)
- DRM snap: `golden-examples/dreame_brush-caps/report/snap_params.json` /
  `dreame_brush_snap_cap.log` (official gate `overall_pass: false`, `analysis/golden/
  dreame_brush-caps.md` §7, §9)
- B02: `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md`,
  `6_RE_work/PARAM_TABLE.md` (Tier-1 5/24 gated, hex-pocket mask-dependent pass)

## Command or procedure
```
python3 skills/stl-re-verify/scripts/verdict.py --qa <run>/qa assemble
python3 skills/stl-re-verify/scripts/verdict.py --qa <run>/qa render
```
(`verdict.py --help`: `--qa QA` "the run's qa/ folder"; subcommands `assemble` (build
`gate.json` from the QA block files and check the proposed verdict against evidence) and
`render` (write `qa/VERDICT.md`).)

## Expected outcome
Cited from `analysis/SYNTHESIS.md` §0.1 "Honest outcome table": OD — **Band NOT MET** (p95
0.448/max 2.49 vs the 0.30/0.80 baseline-skill band, or worse vs RE_SPEC); DRM snap — **Band NOT
MET** (official gate `overall_pass: false`, masked max 1.226/1.246 mm > 0.80 mm band); B02 —
**APPROVED_WITH_LIMITATIONS** (declared limitations, Tier-1 covering only 5 of 24 dims, a masked
hex-pocket pass). These are the exact golden verdicts (or, for OD/DRM-snap, the honest verdict
the golden record's own numbers support even though the projects were historically delivered as
"good result"/"delivered" without stating the miss) — exact match to the cited outcome, not a
tolerance.

## Baseline behaviour (cited)
The baseline skill has no `BAND_NOT_MET` or `APPROVED_WITH_LIMITATIONS` verdict at all — only a
binary blocking PASS/FAIL (`analysis/baseline/stl2step-skills.md` §5.6/§6.11, "the gate is
'blocking'... the skills define no verdict for a missed band. They do not describe an honest
partial delivery, a waiver or a per-region explanation"). Both OD and DRM-snap were historically
delivered (by the golden projects, following practices close to but not identical to the
baseline skill) as if the gate had simply passed, with no verdict machinery available to record
the actual miss (`analysis/SYNTHESIS.md` §0.1 column "What the record really shows").

## Last observed result
Cited from `reviews/stl-re-verify.md` "Golden grades" and the post-fix "Verification performed
this round": "**OD-H12**: `BAND_NOT_MET` accepted, `APPROVED` refused (real re-run, not
synthetic). **DRM snap**: masked max 1.246 mm > 0.80 mm band → `BAND_NOT_MET` accepted,
`APPROVED` refused. **OOM-B02**: Tier-1 5/24 gated + hex-pocket mask-dependent pass (masked
0.307 mm, unmasked 1.813 mm vs 0.8 mm interface band) → `APPROVED_WITH_LIMITATIONS` accepted,
plain `APPROVED` refused." All three built from each project's published numbers in synthetic
`qa/` folders (only OD's full-resolution scan is present in this checkout to actually re-run
`deviation_gate.py` against). **PASS** (per the review; not independently re-run in this eval
session — reconstructing DRM-snap's and B02's full `qa/` block files was judged out of scope for
this pass).
