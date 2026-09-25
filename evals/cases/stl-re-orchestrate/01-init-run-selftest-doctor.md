# Case: `init_run.py --selftest` and `doctor` pass cold

## Skill
`stl-re-orchestrate`

## Input (repo paths)
None (self-contained self-test on a temp dir; `doctor` checks the local Python environment and
sibling skill folders under `skills/`).

## Command or procedure
```
python3 skills/stl-re-orchestrate/scripts/init_run.py --selftest
python3 skills/stl-re-orchestrate/scripts/init_run.py doctor
```
(`init_run.py --help`: `--selftest` "run the self-test on a temp dir"; subcommand `doctor`
"check dependencies and sibling skills".)

## Expected outcome
Cited from `reviews/stl-re-orchestrate.md` "What I ran": `--selftest` → `selftest OK` (rc 0);
`doctor` → all six sibling skills found and all required Python dependencies present, rc 0. This
is an exact pass/fail contract (both must exit 0), including — per the review's fix O-17 — that
`doctor` now also probes `rtree`, `shapely` and `fast_simplification` (previously it "lists
numpy/scipy but ignores them in `ok`... does not check `rtree`, `fast_simplification` (intake) or
`shapely` (measure), so the doctor passes and intake then fails").

## Baseline behaviour (cited)
The baseline pipeline has no orchestrator self-test or dependency doctor at all
(`analysis/baseline/oomwoo-re-pipeline/RE_SPEC.md` and `analysis/baseline/stl2step-skills.md`
document stage content but no run-folder tooling); a baseline-following agent would discover a
missing dependency (e.g. `rtree`) only when the affected stage's script crashed mid-run, with no
upfront check.

## Last observed result
**Run this session** (2026-09-25): `--selftest` → `selftest OK` (exit 0). `doctor` → `"ok":
true`, all six skills (`stl-re-deliver`, `stl-re-intake-datum`, `stl-re-measure-intent`,
`stl-re-orchestrate`, `stl-re-rebuild-build123d`, `stl-re-verify`) reported `true`, and
`fast_simplification: 0.2.0`, `rtree: 1.4.1`, `shapely: 2.1.2` all present alongside
`numpy`/`scipy`/`trimesh`/`build123d`. Matches `reviews/stl-re-orchestrate.md` "What I ran" and
"Fixes applied (round 1)" O-17 verification. **PASS.**
