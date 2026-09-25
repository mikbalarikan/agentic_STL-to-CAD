# Case: `param_table.py` refuses C9/C10/mean-of-n violations (B02 hex, mean-of-n)

## Skill
`stl-re-measure-intent`

## Input (repo paths)
- Synthetic `params.json` built from two golden-cited violation patterns:
  1. `HEX_SYM`: critical, uncalipered hex AF 7.358 → 7.0 under `rule: symmetry`
     (`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:28-30`, the exact case the
     skill's own docs cite as the thing CHK-... must catch)
  2. `MEAN_BAD`: a `mean-of-n` row, value 14.5 vs measured [13.96, 13.92, 13.97] → mean 13.95
     (`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/PARAM_TABLE.md` precedent, "13.96/13.92/
     13.97 → 13.95", cited in `references/intent-rules.md:86`)
- Schema: `skills/stl-re-measure-intent/references/param-table-schema.md` §1-2 (`params` is a
  dict keyed by parameter name, each value carrying `value/unit/measured/rule/source/estimator/
  uncertainty_mm/evidence/critical`).

## Command or procedure
```
python3 skills/stl-re-measure-intent/scripts/param_table.py <params.json> --out <run>/measure/PARAM_TABLE.md
```
(`param_table.py --help`: positional `params` (measure/params.json); `--alignment` (reads
`scan_noise_mm`); `--out`; `--strict` (warnings also fail). "Exit code 0 = valid; 1 = errors
(listed). Warnings never fail unless --strict.")

## Expected outcome
Cited from `reviews/stl-re-measure-intent.md`, MAJOR M1 and M3: a critical, uncalipered scan
value moved beyond the scan noise floor under `rule: symmetry` must be **refused** (error, not
warning) — this is exactly the B02 hex-AF case the skill's own `VERDICT.md:28-30` citation
describes as the one it must catch. A `mean-of-n` value that disagrees with the mean of its
`measured` list beyond `uncertainty_mm` must also be refused. Exit code 1, `PARAM_TABLE.md` not
written. This is an exact pass/fail contract (refuse or not), not a numeric tolerance case.

## Baseline behaviour (cited)
Before the review's fixes (M1, M3 in `reviews/stl-re-measure-intent.md`), `symmetry` without
`scatter_mm` was only a **warning**, `symmetry` with a scalar/prose `measured` passed with only
a warning, and `mean-of-n` had **no validation branch at all** — a value 14.5 against measured
mean 13.95 passed silently. The review reproduced this directly:
"`/tmp/mi_review/p1.json` rows `HEX_SYM`, `CRIT_PROSE`... Result: 'valid (3 warnings)', exit 0"
and "row `MEAN_BAD`... passes." This is the C9/C10 violation SYNTHESIS documents as the specific
failure the golden B02 record caught only through independent human judgement, not tooling
(`analysis/SYNTHESIS.md` row C9, "CHK-ACHIEVABLE (failure-earned)").

## Last observed result
**Run this session** (2026-09-25): the crafted `params.json` above gave **exit 1**, 4 errors / 5
warnings, `"INVALID: 4 errors, 5 warnings — PARAM_TABLE.md not written"`. Errors included:
`[HEX_SYM] symmetry without 'scatter_mm'`, `[HEX_SYM] symmetry needs a per-instance 'measured'
list`, `[HEX_SYM] critical scan-authority value moved 7.358 -> 7, beyond scan noise 0.01 (C9)`,
and `[MEAN_BAD] mean-of-n: value 14.5 != mean of measured [13.96, 13.92, 13.97] (13.95) within
+/-0.1`. This matches the fix record in `reviews/stl-re-measure-intent.md` "Fixes applied
(round 1)" M1 ("now refused: 4 separate errors fire") and M3 ("refused against the review's
MEAN_BAD case"). **PASS.**
