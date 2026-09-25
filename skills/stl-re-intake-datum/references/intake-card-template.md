# INTAKE CARD template (`<run>/intake/INTAKE_CARD.md`)

Adapted from `baseline/oomwoo-re-pipeline/TEMPLATES/INTAKE_CARD.md` (8 sections, which both
golden OOM intakes followed: `analysis/baseline/oomwoo-re-pipeline.md` §8). Changes: role
names removed; band-regime declaration added (owner decision Q1, `QUESTIONS.md` §A); feature
enumeration cross-check (CHK-ENUM) and coverage map made explicit; every number is copied from
`intake.json` / `alignment.json` / `coverage.json`, never retyped from memory.

Copy the block below, fill every field, write "not in evidence" where you have nothing.

```markdown
# INTAKE CARD — <part id / name>

Scan: `input/scan.stl` sha256 <from intake.json inputs>. Working copy: `intake/work.stl`
(<from_faces> → <to_faces> faces, work-vs-full p95 <..> / max <..> mm, seed <..>).
Official gates run on the full-resolution original, never on the working copy.

## 0. Band regime (declared here, named again in the verdict)
Regime: RE_SPEC | baseline-skill | project-spec   ← pick one, give the source path:line
- RE_SPEC (when calipers exist): Tier-1 |CAD − caliper| ≤ 0.15; Tier-2 p95 ≤ 1.6 / max ≤ 4.0 after
  independent ICP + skin mask; named interfaces not caliper-covered max ≤ 0.8 (`RE_SPEC.md:168-175`).
- baseline-skill: p95 ≤ 0.30 / max ≤ 0.80 (consumer plastic), ≤ 0.15 / ≤ 0.50 (machined); no source
  given in the baseline (`baseline/skills/stl2step-build123d/SKILL.md:87`).
- project-spec: <path:line>.
Why this regime: <calipers available? scan-only? operator instruction?>

## 1. What it is (photos + mesh)
Function, how it mounts / mates, moving vs static, material/process if known (say "inferred").

## 2. Scan health (numbers from intake.json)
| Item | Value |
|---|---|
| Faces / verts (welded) | |
| Bodies; kept; removed fragments % | |
| Scanner table removed % (rule used) | |
| Watertight; open boundary edges / loops | |
| Normal orientation (method, verdict, flipped?) | |
| bbox raw; bbox datum (from alignment.json) | |
| Units verdict (CHK-SCALE) | uniform scale applied / none / FLAG (why) |
| Noise floor (value, method, region) | |
| Artefact zones | burrs, bridging, fringes, scanner furniture, soft features |

## 3. Coverage / occlusion map (datum frame; from `intake.py coverage`)
| Zone | r | z | θ | Note |
|---|---|---|---|---|
Angular coverage per radial band: <bands with θ covered < 360 on a round part>.
Partial angular coverage stated here, not first in the report (P03 lesson, SYNTHESIS A9).

## 4. Functional surfaces & interfaces (each becomes a gate zone)
| Zone | Surface | Why functional | Caliper-coverable? | Band |
|---|---|---|---|---|

## 5. Feature enumeration — interior included (CHK-ENUM)
| # | Feature | Seen in mesh (where) | Seen in photo (id) | Status |
|---|---|---|---|---|
Status ∈ {both, mesh-only, photo-only → investigate, occluded → provenance tag}.
CHK-ENUM result: every profile photo checked (ids …); on-axis / above-top material checked
(radial-band z extents from coverage.json); unexplained clusters: <none | list with point counts>.

## 6. Datum plan and result (from alignment.json)
- Primary (levels): <region> → XY @ z = 0 (or axis → +Z). WHY: <function>. Fit rms / max: <..>.
- Secondary: <axis/plane>. WHY: <..>. Fit rms / max: <..>.
- Clock: rule <..>, angle <..>°. WHY: <..>.
- Origin: <feature ∩ feature>.
- Tilt (CHK-TILT): <value ± stderr over span, or "not measured" + why>.
- Sanity landmarks: <name expected / observed / ok>.
- Status: OK | STOP (reason) | CHECK_LANDMARKS.

## 7. Rebuild strategy summary
Per region: revolve / sub-body / cut tool / pattern; expected symmetry (only where measured
within noise). The ordered plan lives in `build/MODELING_PLAN.md`.

## 8. Risk flags and operator declarations
Occlusions, soft features, multi-body scans, anything the mesh cannot decide (datum sign, hidden
features, intent) listed as questions for the operator (facet-film T38).

## 9. Measurement request → `intake/MEASUREMENTS.md`
See `references/measurements-template.md`. Every row carries a scan-predicted value.
```
