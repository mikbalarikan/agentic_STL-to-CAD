# Case: `init_run.py supersede` requires `--route`, so a REVISE resumes at the right stage

## Skill
`stl-re-orchestrate`

## Input (repo paths)
A run folder created with:
```
python3 harnesses/v0/skills/stl-re-orchestrate/scripts/init_run.py init <run> --part TESTPART \
  --scan golden-examples/dreame_brush-caps/dreame_brush_screw_cap_scan_decimated.stl --link
```

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-orchestrate/scripts/init_run.py supersede <run>
python3 harnesses/v0/skills/stl-re-orchestrate/scripts/init_run.py supersede <run> --route {measure,geometry,datum}
```
(`init_run.py supersede --help`: "move measure/ build/ qa/ (and intake/ for --route datum) to
_itN_SUPERSEDED/ after REVISE"; `--route {measure,geometry,datum}` is required, plus optional
`--no-carry`.)

## Expected outcome
Cited from `harnesses/v0/reviews/stl-re-orchestrate.md` MAJOR O-7 and its fix: `supersede` must **refuse**
(non-zero exit, usage error) when `--route` is omitted, since without it "the route is not
persisted anywhere" and a REVISE that should resume at `measure` or `intake` could instead
silently resume at `rebuild` (the carried-forward `measure/params.json`/`PARAM_TABLE.md` making
`status` report `last_complete_stage: measure`). This is an exact contract (refuse without the
flag), not a tolerance.

## Baseline behaviour (cited)
The baseline pipeline's REVISE loop has no persisted "which stage to re-enter" concept at all
(`analysis/baseline/oomwoo-re-pipeline/RE_SPEC.md` describes iteration counts and a HALT
condition, `:248-250`, but not a resume-stage mechanism); before this fix, the orchestrator's own
`supersede` had the same gap — reproduced in `harnesses/v0/reviews/stl-re-orchestrate.md`: "fake a full
iteration, verdict REVISE, run `supersede` → `status` gives iteration 2, `last_complete_stage`
`measure`" even when the finding that triggered REVISE pointed at intake or rebuild.

## Last observed result
**Run this session** (2026-09-25): `init_run.py supersede <run>` (no `--route`) gave **exit code
2** with `usage: init_run.py supersede [-h] --route {measure,geometry,datum} [--no-carry] run` /
`init_run.py supersede: error: the following arguments are required: --route`. This matches the
argparse contract described in `harnesses/v0/reviews/stl-re-orchestrate.md` "Fixes applied (round 1)" O-7:
"Added required `--route {measure,geometry,datum}` to `supersede`." **PASS.**
