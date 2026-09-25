# Case: `deviation_gate.py` refuses an unrecognised regime band-key spelling instead of gating open

## Skill
`stl-re-verify`

## Input (repo paths)
- `golden-examples/OD-H12_delonghi-dedica-pump/0_input/OD-H12-Pump.stl`
- `golden-examples/OD-H12_delonghi-dedica-pump/report/alignment_T1.json`
- `golden-examples/OD-H12_delonghi-dedica-pump/OD-H12-Pump_datum.stl`
- A regime.json using the pre-fix, non-canonical key names:
  `{"name":"baseline-skill-old","bands":{"tier2_p95_mm":0.30,"tier2_max_mm":0.80}}`

## Command or procedure
```
python3 skills/stl-re-verify/scripts/deviation_gate.py \
  --scan golden-examples/OD-H12_delonghi-dedica-pump/0_input/OD-H12-Pump.stl \
  --scan-kind full \
  --align golden-examples/OD-H12_delonghi-dedica-pump/report/alignment_T1.json \
  --cad golden-examples/OD-H12_delonghi-dedica-pump/OD-H12-Pump_datum.stl \
  --regime <bad_regime.json> --out <run>/qa/deviation.json
```

## Expected outcome
Cited from `skills/stl-re-orchestrate/references/run-contract.md` §12 ("Band keys (canonical)":
`p95_mm, max_mm, tier1_abs_mm, interface_max_mm`) and `reviews/stl-re-verify.md` BLOCKER V1's
fix: an unknown band key must cause a **refusal** (non-zero exit, no grading at all), never a
silent `None` that lets every band pass. This is an exact contract (refuse-or-not), not a
tolerance.

## Baseline behaviour (cited)
Before the fix, this exact scenario "failed open": `reviews/stl-re-verify.md` BLOCKER V1
reproduced it end-to-end — "`intake.py regime --name baseline-skill --class plastic`, then
`deviation_gate.py` on the full-res OD scan with that regime.json (p95 0.448, max 2.49).
`deviation.bands` came out all `None`, and `verdict.py assemble` printed `band fails 0 | allowed
[... 'APPROVED' ...]` and exited 0 with verdict APPROVED." An OD-scale band miss was silently
gradeable as a clean APPROVED. The baseline skill itself defines bands per material class with
no shared key contract across a multi-skill pipeline at all
(`analysis/baseline/stl2step-skills.md` §3 "Gates and thresholds").

## Last observed result
**Run this session** (2026-09-25): the bad-key regime gave **exit code 2**, stderr `ERROR:
regime refused: unknown band key(s) ['tier2_max_mm', 'tier2_p95_mm']; canonical keys are
('p95_mm', 'max_mm', 'tier1_abs_mm', 'interface_max_mm') (run-contract §12)`. No deviation.json
was graded. This matches `reviews/stl-re-verify.md` "Fixes applied (round 1)" V1 verification:
"a regime with the old `tier2_p95_mm`/`tier2_max_mm` keys ... is refused with `exit=2` and an
'unknown band key(s)' error, not silently graded as `APPROVED`." **PASS.**
