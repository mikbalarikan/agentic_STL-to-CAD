# Case: `make_readme.py`/`make_manifest.py` refuse a stale `repro.json` after `model.py` changes

## Skill
`stl-re-deliver`

## Input (repo paths)
- A fixture run (`skills/stl-re-deliver/tests/fixture_run/`) with a valid `deliver/repro.json`
  from a passing `repro_check.py` run, then `build/model.py` edited afterward (e.g. a changed
  numeric literal such as `plate_x*2`) without re-running `repro_check.py`.

## Command or procedure
```
python3 skills/stl-re-deliver/scripts/repro_check.py --run <run>
# ... then edit build/model.py ...
python3 skills/stl-re-deliver/scripts/make_readme.py --run <run>
python3 skills/stl-re-deliver/scripts/make_manifest.py --run <run>
```
(`repro_check.py --help`: "Rebuild build/model.py twice in fresh processes and compare the
geometry with the delivered STEP"; `--runs` default 2 (facet-film T32), `--tol-mm` default
"exact (M02)". `make_readme.py --help`/`make_manifest.py --help`: render the delivery README /
manifest from the run's JSON artefacts.)

## Expected outcome
Cited from `reviews/stl-re-deliver.md` MAJOR D3 and its intended fix: README and manifest
generation must refuse (raise `DeliverError`, non-zero exit) when any `repro.json#inputs` sha256
(covering `build/model.py`, `measure/params.json`, the delivered STEPs) no longer matches the
current file on disk — "deliver/repro.json is stale (<path> changed); re-run repro_check.py".
This is an exact pass/fail contract, not a tolerance.

## Baseline behaviour (cited)
The baseline pipeline has no repro-freshness concept at all
(`analysis/baseline/stl2step-skills.md` §8; `analysis/baseline/oomwoo-re-pipeline/RE_SPEC.md`
documents a reproducibility rebuild step for M02 but not a hash-freshness check tied to
delivery). Pre-fix, `reviews/stl-re-deliver.md` D3 reproduced exactly this scenario: "I ran
repro, then changed `build/model.py` (`plate_x*2`). `make_readme.py` exited 0 and
`make_manifest.py` exited 0, both still claiming reproducible" — a stale reproducibility claim
would ship uncaught.

## Last observed result
**Not run this session — skill under edit** (see case 01; `skills/stl-re-deliver/` has
uncommitted, in-progress changes to its qa fixtures at the time this suite was written). Cited
historical result: `reviews/stl-re-deliver.md` D3 "Reproduced: I ran repro, then changed
`build/model.py`... `make_readme.py` exited 0 and `make_manifest.py` exited 0, both still
claiming reproducible" (the defect, pre-fix); no "Fixes applied" entry for D3 appears in
`reviews/stl-re-deliver.md` (unlike the other five skills' reviews, this one has no recorded fix
round yet). **not run (skill under edit)**.
