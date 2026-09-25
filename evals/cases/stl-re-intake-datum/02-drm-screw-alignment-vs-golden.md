# Case: DRM screw datum alignment vs golden `screw_alignment.json`

## Skill
`stl-re-intake-datum`

## Input (repo paths)
- `golden-examples/dreame_brush-caps/dreame_brush_screw_cap_scan_decimated.stl` (scan)
- `golden-examples/dreame_brush-caps/report/screw_alignment.json` (golden datum, the value this
  case checks against — a plane-primary + Kåsa-circle-origin + polygon-flat-clock fit)

## Command or procedure
```
python3 skills/stl-re-intake-datum/scripts/intake.py stats <scan> --out-dir <run>/intake
python3 skills/stl-re-intake-datum/scripts/datum_fit.py noise ... # top-face noise floor
python3 skills/stl-re-intake-datum/scripts/align.py <spec.json>
```
`align.py --help`: single positional `spec` (a JSON datum spec per
`references/datum-cookbook.md` §2.1, the DRM screw worked example: plane primary on the top
disc face, Kåsa-circle origin on the double-D drive hole, `polygon_flat` clock with n=5).
Compare the resulting `alignment.json#matrix_4x4` against the golden `screw_alignment.json`.

## Expected outcome
Cited from the golden record and the cookbook's own worked example
(`references/datum-cookbook.md` §2.1): the golden clock is **−34.2306614°**
(`screw_alignment.json#clock_deg`), bore `r_mean` **1.8728259928266318**, primary-plane fit
`rms 0.007205 / max 0.055067`. No numeric tolerance is recorded in the golden for "reproduces
the datum"; the standard used by the independent review is a qualitative one — rotation
difference and point disagreement small relative to the part's own noise floor (rms ≈0.007 mm).
Treat any stated tolerance below as the reviewer's own observed value, not an invented band.

## Baseline behaviour (cited)
The baseline skill's datum method uses an eigen-formula for axis-from-normals and a
RANSAC/SVD plane fit (`analysis/baseline/stl2step-skills.md` §2 "Datum", `§5.1`), but has no
documented Kåsa-circle-with-shape-error caveat and no `polygon_flat` clock convention; SYNTHESIS
row B4 marks the robust circle/axis fits as a RULE earned from the golden projects, not from
baseline doctrine. A baseline-only agent reproducing this part would very likely bbox-align or
pick "largest facet" as primary (SYNTHESIS row B2, explicitly ruled out by the golden evidence),
which would not reproduce the golden clock or origin at all.

## Last observed result
**Not run this session** (reconstructing the exact intake spec — `r_hint`, `z_range`, station
count for the double-D Kåsa fit — requires values the cookbook explicitly does not restate,
"see DRM/report; not restated here"). The independent reviewer built an equivalent spec and
reported, in `reviews/stl-re-intake-datum.md` "What I ran": `align.py` gave **OK**, rms/max
0.0069/0.031 mm over 17,997 faces, 25 stations, `r_mean` 1.886, clock **−34.255°** (golden
−34.231°), tilt 0.716° ± 0.109°. Against the golden `screw_alignment.json`: rotation difference
**0.0195°**, point disagreement **max 0.0140 mm** (60k seeded points), aligned bounds agreeing to
≤0.013 mm. Determinism: two fresh runs gave identical `alignment.json` apart from `created`.
**PASS** (per the review; not independently re-run in this eval session).
