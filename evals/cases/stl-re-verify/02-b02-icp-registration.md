# Case: `tier2_icp.py` reproduces the B02 golden ICP registration (0.698° / 0.186 mm)

## Skill
`stl-re-verify`

## Input (repo paths)
- `golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/OOM-B02.stl` (full-res scan)
- `golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/alignment.json`
- `golden-examples/OOM-B02_side-brush-3-arm/4_STEP/OOM-B02.step`
- Golden reference: the golden's own `_tier2_it2.log` (48 iterations, 0.6981°/0.1869 mm,
  0.5031 mm max point move, 233,423/300,000 correspondences kept, 77.8%)

## Command or procedure
```
python3 skills/stl-re-verify/scripts/tier2_icp.py \
  --scan golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/OOM-B02.stl --scan-kind full \
  --align golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/alignment.json \
  --cad golden-examples/OOM-B02_side-brush-3-arm/4_STEP/OOM-B02.step \
  --scan-masks <region masks: cup rim r>38.5; screw/bristle region per q20_tier2.py:35-40> \
  --out <run>/qa/registration.json
```
(`tier2_icp.py --help`: required `--scan`, `--scan-kind`, `--align`, `--cad`; optional
`--scan-masks` (JSON list of region masks removed from the ICP reference), `--ns`, `--nc`,
`--max-iter`, `--tol`.)

## Expected outcome
Cited from `analysis/golden/OOM-B02.md` §7-9 and the golden `_tier2_it2.log`: pose convergence
around **0.698° / 0.186 mm** (rotation/translation residual), with roughly 77.8% of
correspondences kept after masking. No fixed numeric tolerance is recorded for "reproduces the
golden ICP" beyond the reviewer's own observation that the pose agrees to within 0.0005 mm;
iteration count is explicitly *not* expected to match exactly, since it depends on the exact
mask predicates and tessellation given to the solver (qualitative match on the converged pose,
not on iteration count).

## Baseline behaviour (cited)
The baseline skill's registration step, where documented at all, has no masked/unmasked ICP
distinction and no independent re-registration by the verifier separate from the builder's own
alignment (`analysis/baseline/stl2step-skills.md` §2 "Datum"; SYNTHESIS row B8: "Independent
datum audit by the verifier with its own code" is a RULE earned from B02/P03, not baseline
doctrine). A baseline-only verifier would trust the builder's alignment directly rather than
re-deriving a registration and comparing it, so a mis-masked or non-converged builder alignment
would go undetected.

## Last observed result
**Not run this session** (reconstructing the exact `--scan-masks` predicate used by the review —
"M1 r>38.5; M2 screw from q20:35-40" — was judged too time-consuming for this pass; the
independent review already ran and recorded it). Cited from `reviews/stl-re-verify.md`
"Addendum: B02 ICP re-run (full-res)": converged in **53/60** iterations, **0.6980° / 0.1864
mm**, max point move 0.5026 mm, 77.8% of correspondences kept (233,423-equivalent), vs the
golden's 48 iterations, 0.6981°/0.1869 mm, 0.5031 mm, 77.8% — "The pose agrees to within 0.0005
mm... not a reproducibility defect" (the iteration-count difference is attributed to the mask/
tessellation dependency, not an error). **PASS** (per the review; not independently re-run in
this eval session).
