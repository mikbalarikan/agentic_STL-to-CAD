# Case: `face_stats.py` reproduces the OD-H12 NX surface-type census (213 = 139/48/24/2)

## Skill
`stl-re-rebuild-build123d`

## Input (repo paths)
- `golden-examples/OD-H12_delonghi-dedica-pump/OD-H12-Pump_datum.step`
- Golden NX census: `golden-examples/OD-H12_delonghi-dedica-pump/OD-H12-Pump.log:26,35,37,53,67`

## Command or procedure
```
python3 skills/stl-re-rebuild-build123d/scripts/face_stats.py \
  golden-examples/OD-H12_delonghi-dedica-pump/OD-H12-Pump_datum.step \
  --json <run>/build/face_stats.json
```
(`face_stats.py --help`: positional `step`, `--json` "write the census JSON here",
`--expect-faces MIN MAX` "expected face-count range from build/MODELING_PLAN.md (reported
only)". "Surface-type census of a STEP (CHK-PATCHWORK, reported not gated).")

## Expected outcome
Exact match to the golden NX log: **213** total faces = **139 plane / 48 cylinder / 24 cone /
2 torus** (`OD-H12-Pump.log:26,35,37,53,67`, cited in `reviews/stl-re-rebuild-build123d.md`
"What I ran"). CHK-PATCHWORK is reported, never gated (`face_stats.py` writes `"gated": false`).

## Baseline behaviour (cited)
No baseline skill or golden-project script for an OCP/build123d surface-type census exists in
the repo; the golden OD project's census came from a proprietary NX log, not from any
reproducible open-source tool (`analysis/golden/OD-H12.md` §4). A baseline agent following only
`analysis/baseline/stl2step-skills.md` (which has no §-level census/patchwork check) would have
no automated way to compare a rebuilt STEP's surface-type mix against the original CAD/scan
census at all, and would not catch a planar-facet approximation standing in for a curved
surface, or vice versa.

## Last observed result
**Run this session** (2026-09-25): `face_stats.py` on `OD-H12-Pump_datum.step` gave `faces:
213`, `surface_types`: plane count **139** (area 17904.63 mm², share 0.6119), cylinder count
**48**, cone count **24**, torus count **2** (area 374.12 mm², share 0.0128); `plane_face_count:
139`, `plane_face_median_area_mm2: 10.27`. This matches `reviews/stl-re-rebuild-build123d.md`
"What I ran" exactly ("213 faces ... 139 plane / 48 cylinder / 24 cone / 2 torus, which matches
`OD-H12-Pump.log:26,35,37,53,67`") and the post-fix verification ("plane_face_count 139").
**PASS.**
