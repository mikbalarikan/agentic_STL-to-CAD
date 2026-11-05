# Case: `sim_caliper.py` inside-jaw mode does not strike B02 F03 (cup bore)

## Skill
`stl-re-measure-intent`

## Input (repo paths)
- `golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/OOM-B02.stl` (full-res scan)
- `golden-examples/OOM-B02_side-brush-3-arm/2_mesh_cleaned/alignment.json`
- Golden reference: `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/PARAM_TABLE.md:36`
  (F03 = 20.75 mm, Tier-1 PASS at `:153`)

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-measure-intent/scripts/sim_caliper.py \
  --mesh <OOM-B02.stl> --alignment <alignment.json> \
  --z 1.0 --mode inside --r-band 9.5,11 --reading 20.75 --reading-unc 0.1 \
  --out <run>/measure/f03.json
```
(`sim_caliper.py --help`: `--mode {outside,inside}`, "inside jaws on the inner (bore) envelope
built from --r-band points (required in this mode)"; `--z` the section height; `--reading`/
`--reading-unc` classify the caliper value against the achievable window, CHK-ACHIEVABLE.)

## Expected outcome
Cited from the golden PARAM_TABLE (`PARAM_TABLE.md:36,153`): F03 = 20.75 mm is a
**golden-accepted Tier-1 PASS**, not a struck reading. The skill must classify it as achievable
("use"/within window), never STRIKE. No numeric tolerance beyond the recorded `--reading-unc`
0.1 mm (photo-transcribed caliper uncertainty, `MEASUREMENTS.md:24`) is defined; the pass
criterion is qualitative — "not struck".

## Baseline behaviour (cited)
Before the review's fix (`harnesses/v0/reviews/stl-re-measure-intent.md`, BLOCKER B1), `--mode inside` on a
scan picked the polyline with the smallest max-radius, which on an open scan section is a
fragment rather than the bore, and coverage was hard-coded to `1.0`. Running exactly this
command on the pre-fix script **struck** the golden-accepted F03 reading with "STRIKE: above
the maximum" (`harnesses/v0/reviews/stl-re-measure-intent.md` B1 evidence: window 0.109…0.618 with
`--r-band`, or 1.125…5.650 without it). The lifted golden code
(`OOM-B02/6_RE_work/40_verify.py:74`) only ever worked on closed CAD loops, so it never
exercised this bug; the pre-fix `sim_caliper.py` would have discarded a real, golden-accepted
measurement.

## Last observed result
**Run this session** (2026-09-25), on the post-fix script: window **18.388 .. 21.024** (jaws @
4.05° / 85.75°), coverage 0.692, reading 20.750 ± 0.1 → **"use (within window)"** — not struck.
This matches the fix record in `harnesses/v0/reviews/stl-re-measure-intent.md` "Fixes applied (round 1)", B1:
"window 18.388..21.024, coverage 0.692 — no longer struck." **PASS.**
