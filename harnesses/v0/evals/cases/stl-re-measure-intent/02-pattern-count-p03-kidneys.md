# Case: `pattern_count.py` reproduces P03 mop-pad-bracket 8 kidneys

## Skill
`stl-re-measure-intent`

## Input (repo paths)
- `golden-examples/OOM-P03_mop-pad-bracket/2_mesh_cleaned/` decimated scan (aligned with the
  golden's own `alignment.json`)
- Golden reference: `golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/PARAM_TABLE.md:38,42`,
  `VERDICT.md:49` (FFT dominant order F[8]=144.6, "8 kidneys")

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-measure-intent/scripts/pattern_count.py \
  --mesh <p03_scan_aligned.stl> --signal mass --stations <3 z stations> --orders 9,60 \
  --out <run>/measure/p03_kidneys.json
```
(`pattern_count.py --help`: `--signal mass` is the "area-weighted histogram of face centroids
... robust on non-watertight scans" mode, appropriate for an open scan; `--stations` must list
>=3 z values per CHK-COUNT.)

## Expected outcome
Cited from the golden (`PARAM_TABLE.md:38`, `VERDICT.md:49`): **8**-fold kidney pattern
(dominant FFT order 8, F[8]=144.6). Crest-phase should land near the golden's stated spoke
angles (25° + k·45°, `PARAM_TABLE.md:38`). This is a discrete count with no tolerance (exact
match); the phase alignment is qualitative (near the stated spoke angle, not an exact-to-decimal
match).

## Baseline behaviour (cited)
As with the M02 gear count, no golden or baseline script for this rotational-order method
exists in the repo (`analysis/golden/OOM-P03.md` §11); `pattern_count.py`'s provenance header
states the P03 evidence used was an angular FFT of "radius / material vs theta", re-implemented
from the recorded numbers, not lifted code. A baseline agent without this tool would likely fall
back to counting features visually from a section image, which is exactly the practice
SYNTHESIS row C3 rules out ("count patterns by rotational order... never by crest peaks").

## Last observed result
**Not run this session** (requires reconstructing the P03 alignment/z-station spec). Cited from
`harnesses/v0/reviews/stl-re-measure-intent.md` "What I ran": "pattern_count, P03 kidneys (decimated scan +
golden alignment): **8** at 3/3 stations, crest phase 25.45/25.22/25.20° (golden spokes
25°+k·45°, `PARAM_TABLE.md:38`). With `--orders 9,60` it gave an honest `finding` ([16, 40]),
not a fake count." Determinism: two fresh runs produced identical JSON apart from `created`.
**PASS** (per the review; not independently re-run in this eval session).
