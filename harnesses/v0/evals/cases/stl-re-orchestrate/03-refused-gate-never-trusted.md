# Case: `init_run.py status` never trusts a `gate.json` verdict that verify itself refused

## Skill
`stl-re-orchestrate`

## Input (repo paths)
A run folder from `init_run.py init`, with a synthetic `qa/gate.json`:
```json
{"verdict": "APPROVED", "errors": ["deviation not run"],
 "allowed_verdicts": ["BAND_NOT_MET", "HALT", "REVISE"]}
```
(this is the exact shape `stl-re-verify/scripts/verdict.py assemble` writes when it refuses a
proposed verdict — it writes `gate.json` **before** returning a non-zero exit, per
`harnesses/v0/reviews/stl-re-orchestrate.md` MAJOR O-1.)

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-orchestrate/scripts/init_run.py status <run>
```
(`init_run.py --help`: subcommand `status` "print run state as JSON".)

## Expected outcome
Cited from `harnesses/v0/reviews/stl-re-orchestrate.md` MAJOR O-1 and its fix: `status` must report
`verdict: null` (not the refused `"APPROVED"`) plus a finding naming the refusal, whenever
`gate.json#errors` is non-empty or the proposed verdict is not in `allowed_verdicts`. This is an
exact contract — the refused verdict must never surface as if it were trustworthy — not a
tolerance.

## Baseline behaviour (cited)
Before the fix, `status` (and, per the review, `stl-re-deliver` downstream) trusted
`gate.json#verdict` unconditionally: `harnesses/v0/reviews/stl-re-orchestrate.md` O-1 reproduced "gate.json
`{"verdict":"APPROVED","errors":["…"],"allowed_verdicts":["BAND_NOT_MET","HALT","REVISE"]}` →
`status` prints verdict `APPROVED`, stage `verify`, findings `[]`." The baseline pipeline has no
equivalent "verify refused its own verdict" state at all (its gate is a simple blocking
PASS/FAIL, `analysis/baseline/stl2step-skills.md` §7), so this specific fail-open mode is unique
to the multi-skill hand-off this project introduces.

## Last observed result
**Run this session** (2026-09-25): `status` on the run with the synthetic refused `gate.json`
above returned `"verdict": null` and `"findings": ["qa/gate.json verdict refused by verify
(errors: ['deviation not run']); re-run stl-re-verify", "no filled input/MEASUREMENTS.md: ..."]`.
This matches `harnesses/v0/reviews/stl-re-orchestrate.md` "Fixes applied (round 1)" O-1: "`read_verdict()`
now returns `None` whenever `qa/gate.json#errors` is non-empty or `verdict` is not a member of
`allowed_verdicts`... `cmd_status` adds the refusal as a finding." **PASS.**
