# Case: `export_frames.py` with `scale_factor != 1` delivers the datum frame only

## Skill
`stl-re-rebuild-build123d`

## Input (repo paths)
- `golden-examples/dreame_brush-caps/dreame_brush_screw_cap_datum_frame.step`
- `golden-examples/dreame_brush-caps/report/screw_alignment.json`, with `scale_factor` set to
  `1.01` (golden value is `1.0`; this is a synthetic non-unity value to exercise run-contract
  §11's rule)

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-rebuild-build123d/scripts/export_frames.py \
  --shape golden-examples/dreame_brush-caps/dreame_brush_screw_cap_datum_frame.step \
  --alignment <alignment_scale_1.01.json> --out <run>/build --part screw
```

## Expected outcome
Cited from `harnesses/v0/skills/stl-re-orchestrate/references/run-contract.md` §11 and
`harnesses/v0/reviews/stl-re-rebuild-build123d.md` MAJOR M1: when `scale_factor != 1`, the scale is folded
into `matrix_4x4` and **only the datum-frame STEP is delivered** — the scan-frame export is
skipped, not silently omitted or aborted with nothing written. Expect exit code **3**
(datum-only, distinct from the exit-2 abort path), `<part>_datum.step` written,
`export_check.json#scan` recording the skip reason, and `export_check.json#pass: true`. This is
an exact behavioural contract, not a numeric tolerance.

## Baseline behaviour (cited)
Before the fix, `harnesses/v0/reviews/stl-re-rebuild-build123d.md` M1 found the script aborted **before
writing anything at all**: "I ran it with `scale_factor=1.01`: rc=2, output folder empty." Both
Precondition 2 and the skill's own Open Question 1 called the non-unity-scale case "undecided,"
even though run-contract §11 had already settled it — so a cold agent following the pre-fix
skill would HALT with zero delivered artefacts exactly where the contract said to proceed with a
datum-only delivery.

## Last observed result
**Run this session** (2026-09-25): exit code **3**, stdout
`DATUM-ONLY: scale_factor=1.01: scan-frame STEP not delivered (run-contract.md section 11);
datum-frame STEP only`. Output folder contained `x_datum.step` and `export_check.json` (no
scan-frame STEP). This matches `harnesses/v0/reviews/stl-re-rebuild-build123d.md` "Fixes applied (round 1)"
M1 verification: "synthetic `scale_factor=1.01` ... -> rc=3, `x_datum.step` written,
`export_check.json#scan.skipped` present, `pass: true`". **PASS.**
