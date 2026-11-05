# Case: DRM screw scan intake hygiene (fragments, orientation, decimation)

## Skill
`stl-re-intake-datum`

## Input (repo paths)
- `golden-examples/dreame_brush-caps/dreame_brush_screw_cap_scan_decimated.stl`

## Command or procedure
```
python3 harnesses/v0/skills/stl-re-intake-datum/scripts/intake.py stats \
  golden-examples/dreame_brush-caps/dreame_brush_screw_cap_scan_decimated.stl \
  --out-dir <run>/intake --work-faces 300000
```
(`intake.py --help` → subcommand `stats`: "stats + sha256 + working copy -> intake/intake.json,
intake/work.stl"; `--work-faces` is the only stats-relevant flag besides the positional scan
path and the global `--seed`.)

## Expected outcome
Qualitative / cited-value match to the independent review's reproduction of this same script on
this same file (`harnesses/v0/reviews/stl-re-intake-datum.md` "What I ran"):
- largest-body fragment removal on the order of **1017 bodies, fragments ≈1.98%**
- open-mesh normal orientation resolved by ray vote to **outward** (hit-along-normal ≈0.29 vs
  hit-against-normal ≈0.96)
- decimated working copy vs full mesh: **p95 ≈0.0009 mm / max ≈0.0099 mm**
No tolerance band is recorded for these figures beyond "reproduces the reviewer's own run";
treat as exact match to the recorded value (the script is deterministic with `--seed 0`).

## Baseline behaviour (cited)
The baseline skills record scan stats at intake (SYNTHESIS §1A row A1, RULE) but do not
document explicit scanner-furniture/fragment removal by largest-body selection, nor an
open-mesh ray-vote normal orientation check — `analysis/SYNTHESIS.md` row A4/A5 marks these as
practices earned from the golden projects (B02, DRM), not present in the baseline skill
doctrine (`analysis/baseline/stl2step-skills.md` §1 "Intake and hygiene" lists hashing and
counts only). A baseline-following agent would report scan stats but would not flag or quantify
the 1017-body fragmentation or the outward-normal ambiguity of this open scan.

## Last observed result
**Run this session** (2026-09-25): `intake.py stats` on the file above gave
`removed.method: "kept largest of 1017 bodies (931220 faces)"`, `fragments_pct: 1.9767`,
orientation `hit_along_normal: 0.29`, `hit_against_normal: 0.96`, `verdict: "outward"`,
`decimation.work_vs_full_dev_mm: {p95: 0.0009307533680727171, max: 0.009888021173211366}`.
This matches `harnesses/v0/reviews/stl-re-intake-datum.md` "What I ran" (1017 bodies, fragments 1.98%, ray
vote outward 0.29/0.96, p95 0.0009/max 0.0099) exactly. **PASS.**
