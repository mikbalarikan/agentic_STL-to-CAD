# Case: `export_frames.py` reproduces the delivered DRM screw STEP exactly

## Skill
`stl-re-rebuild-build123d`

## Input (repo paths)
- `golden-examples/dreame_brush-caps/dreame_brush_screw_cap_datum_frame.step` (datum-frame body)
- `golden-examples/dreame_brush-caps/report/screw_alignment.json` (raw→datum transform)
- Golden delivered STEP: `golden-examples/dreame_brush-caps/dreame_brush_screw_cap.step`
- Golden delivered scan-mesh comparison: `dreame_brush_screw_cap_cad.stl`

## Command or procedure
```
python3 skills/stl-re-rebuild-build123d/scripts/export_frames.py \
  --shape golden-examples/dreame_brush-caps/dreame_brush_screw_cap_datum_frame.step \
  --alignment golden-examples/dreame_brush-caps/report/screw_alignment.json \
  --out <run>/build --part screw
```
(`export_frames.py --help`: `--shape` "datum-frame STEP of the built part", `--alignment`
"intake/alignment.json (raw scan -> datum)", `--out` "output folder (build/)", `--part`
"part name: writes <part>_datum.step, <part>.step, <part>_cad.stl". Dual-frame export +
re-import check, run-contract §5.)

## Expected outcome
Exact match to the golden delivered STEP, cited from `reviews/stl-re-rebuild-build123d.md`
"What I ran": faces **56 = 56**, volume **269.0776** mm³ (Δ 7e-8), boolean differences
**0 / 0 mm³**, max vertex distance **7.7e-14 mm** over 88 = 88 vertices, and scan→CAD deviation
on the decimated scan of p50 0.026 / p95 0.087 mm, consistent with the golden's own recorded
p95 0.085 mm (`analysis/golden/dreame_brush-caps.md` §7). Exit code 0.

## Baseline behaviour (cited)
The baseline `stl2step-build123d` skill documents a single-frame STEP export
(`analysis/baseline/stl2step-skills.md` §6 "Rebuild") with no dual-frame (scan-frame vs
datum-frame) discipline, and run-contract §5/§11 records this dual export and its scale/rigidity
guards as new machinery earned from the golden record, not baseline doctrine. A baseline agent
exporting only the datum-frame STEP would produce a geometrically correct part but would not
reproduce or check against the original scan-frame delivered STEP at all, so any drift between
the two frames (a wrong-direction transform, a non-rigid matrix) would go undetected.

## Last observed result
**Run this session** (2026-09-25): rc 0. `export_check.json` reported: datum and scan frames
both `faces: 56, solids: 1, valid: true, closed: true, volume_mm3: 269.077577`;
`frames_agree.faces_equal: true`, `frames_agree.volume_rel_diff: 0.0`,
`frames_agree.numeric_roundtrip_bbox_mm: 3.528e-07`, `pass: true`. This matches the review's own
reproduction (`reviews/stl-re-rebuild-build123d.md` "What I ran": "identical bbox, volume
269.0776 (Δ 7e-8), 56 = 56 faces, boolean differences 0 / 0 mm³, max vertex distance 7.7e-14 mm")
and the post-fix verification run recorded in "Fixes applied (round 1)" ("rc 0, 56 = 56 faces,
volume 269.077577 both frames"). **PASS.**
