# Case: `export_frames.py` refuses a non-rigid `matrix_4x4` instead of silently snapping it

## Skill
`stl-re-rebuild-build123d`

## Input (repo paths)
- `golden-examples/dreame_brush-caps/dreame_brush_screw_cap_datum_frame.step`
- `golden-examples/dreame_brush-caps/report/screw_alignment.json`, perturbed: `matrix_4x4[0][0]`
  multiplied by 1.02 (a synthetic 2% non-orthogonality, simulating a hidden scale/shear that
  `scale_factor` does not record — the case run-contract §11 says cannot be a rigid OCP transform)

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-rebuild-build123d/scripts/export_frames.py \
  --shape golden-examples/dreame_brush-caps/dreame_brush_screw_cap_datum_frame.step \
  --alignment <perturbed_alignment.json> --out <run>/build --part screw
```

## Expected outcome
Cited from `harnesses/v0/reviews/stl-re-rebuild-build123d.md`, MAJOR M3, and its fix: a non-rigid rotation
block (singular values departing from 1 by more than a stated float-noise tolerance, `1e-6`,
explicitly labelled a tolerance for numerical noise, not a design threshold) must **abort**
(`ExportAbort`, exit code 2) rather than be silently orthonormalised and exported at rc 0. This
is an exact pass/fail contract on the guard triggering, not a numeric-value tolerance case.

## Baseline behaviour (cited)
Before the fix, exactly this perturbation gave **rc 0** with the matrix silently
orthonormalised (`harnesses/v0/reviews/stl-re-rebuild-build123d.md` M3 evidence: "I multiplied m[0][0] by
1.02: singular values 1.0012/1.0/0.9841, `orthonormalisation_max_abs` 0.0149, rc=0"). The
scan-frame STEP would then be misplaced relative to the scan with only a buried diagnostic field
recording the mismatch — nothing in the baseline `stl2step-build123d` skill or run-contract §11
prior to this fix checked rotation-block rigidity at all.

## Last observed result
**Run this session** (2026-09-25): the perturbed alignment gave **exit code 2** with
`ABORT: matrix_4x4 rotation block is not rigid (singular values [1.001674, 1.0, 0.986148], max
deviation from 1 = 1.385e-02 > 1e-06 float-noise tolerance); a scale or shear belongs in
scale_factor, not matrix_4x4 (run-contract.md section 11) - refusing rather than silently
orthonormalising`. This matches `harnesses/v0/reviews/stl-re-rebuild-build123d.md` "Fixes applied (round 1)"
M3 verification: "singular values 1.0017/1.0/0.9861 ... now aborts rc=2 with `export_check.json`
written". **PASS.**
