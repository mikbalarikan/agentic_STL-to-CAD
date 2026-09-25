# Case: `face_stats.py` cannot see M02's planar-facet patchwork by itself (documented blind spot)

## Skill
`stl-re-rebuild-build123d`

## Input (repo paths)
- `golden-examples/M02-02-03_watertight-design-intent/M02-02-03_WATERTIGHT_SOLID.step`

## Command or procedure
```
python3 skills/stl-re-rebuild-build123d/scripts/face_stats.py \
  golden-examples/M02-02-03_watertight-design-intent/M02-02-03_WATERTIGHT_SOLID.step \
  --json <run>/build/face_stats.json
```
(same CLI as case 02; the M02 body is an involute-tooth polar-pattern build with many small
planar facets around the tooth profile, `analysis/golden/M02-02-03.md` §2 `model.py:76-101`.)

## Expected outcome
Cited from `reviews/stl-re-rebuild-build123d.md`, MAJOR M5: the census "cannot see
planar-facet patchwork (stacked prisms, polygonal profiles): planes count as analytic," so it
correctly reports `analytic_area_share = 1.0` and `ruled_like_faces = 0` on this STEP even
though the tooth flanks are a polygon-approximation, not a true analytic surface. The *new*
signal added by the fix (`plane_face_count`, `plane_face_median_area_mm2`) is reported, not
gated, and is expected to show a face count (2354, 2306 planar) far in excess of what a smooth
involute-tooth plan would predict — this is a qualitative "look at this" signal with no
threshold, matching the fixed skill's own stated design ("no invented threshold").

## Baseline behaviour (cited)
Before the review's fix, `references/strategy-catalogue.md:141-143` claimed the census "is
exactly what the census flags" for M02's planar facets — which the review showed to be false
(a plane is counted as fully analytic regardless of whether it approximates a curve). A cold
agent trusting `analytic_area_share = 1.0` / `ruled_like_faces = 0` at face value, as the
pre-fix documentation implied, would read this STEP as clean, fully-analytic geometry and miss
the patchwork entirely — the exact failure mode the golden M02 record's own crest-peak mistake
echoes (a plausible-looking but wrong reading, `G/VERDICT.md:25`).

## Last observed result
**Run this session** (2026-09-25): `faces: 2354`, `surface_types.plane.count: 2306`,
`analytic_area_share`-equivalent `plane` share ≈1.0 of area (plane 1155.14 mm² of total 1351.38
mm², cylinder 196.23 mm², `ruled_like_faces` not present as non-zero — `plane_face_count: 2306`,
`plane_face_median_area_mm2: 0.17988`. This matches `reviews/stl-re-rebuild-build123d.md`
"Fixes applied (round 1)" M5 verification: "faces=2354, analytic_area_share=1.0,
ruled_like_faces=0 ... plane_face_count=2306, plane_face_median_area_mm2=0.17988 (confirming the
new signal is visible)". **PASS** (the blind spot is confirmed present and the new reported-only
signal correctly exposes the facet count; this is the documented, accepted behaviour, not a
defect).
