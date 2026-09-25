# Case: ACCEPT-BAND acceptance must be tied to the specific gate it accepts

## Skill
`stl-re-deliver`

## Input (repo paths)
- A fixture run (`skills/stl-re-deliver/tests/fixture_run/`) with `qa/gate.json` in
  `BAND_NOT_MET` state, and a `DECISIONS.md`-style ACCEPT-BAND line whose evidence path points
  outside `decisions/`/the run root (e.g. `qa/VERDICT.md`), or whose text does not reference the
  current `gate.json`'s sha256/`created` value or name any `gate.json#band_fails` item.

## Command or procedure
```
python3 skills/stl-re-deliver/scripts/preflight.py --run <run>
```
(`preflight.py --help`: "Pre-delivery gate: may this run be delivered? Prints the checks as
JSON; writes nothing." Reads `_common.py`'s `check_acceptance` logic, `scripts/_common.py:133-148`.)

## Expected outcome
Cited from `reviews/stl-re-deliver.md` MAJOR D4 and its proposed fix: an ACCEPT-BAND entry must
be rejected as delivery evidence when its cited evidence sits under a run-generated folder
(`qa/`, `build/`, `measure/`, `intake/`, `deliver/`, `_it*_SUPERSEDED/`) rather than
`decisions/`/the run root, and it must be rejected unless its text contains the current
`gate.json`'s sha256 prefix (or `created` value) and names at least one `gate.json#band_fails`
item — otherwise `preflight.py` must refuse with "ACCEPT-BAND does not reference this gate;
re-ask the owner". This is an exact pass/fail contract, not a tolerance.

## Baseline behaviour (cited)
The baseline pipeline has no human-acceptance-of-a-band-miss mechanism at all
(`analysis/baseline/stl2step-skills.md` §7/§8; its gate is binary blocking PASS/FAIL with no
BAND_NOT_MET state to accept). Pre-fix, `reviews/stl-re-deliver.md` D4 reproduced the gap
directly in this skill's own code: "`- 1970-01-01 | x | ACCEPT-BAND | ok | qa/VERDICT.md` passes
preflight for BAND_NOT_MET" — i.e. an acceptance entry that cites the verifier's own report
(circular, and not tied to this specific gate) was accepted as valid delivery evidence, and an
acceptance recorded against one iteration's miss could carry over to a later, different gate.

## Last observed result
**Not run this session — skill under edit** (see case 01). Cited historical result:
`reviews/stl-re-deliver.md` D4 evidence: "Reproduced: `- 1970-01-01 | x | ACCEPT-BAND | ok |
qa/VERDICT.md` passes preflight for BAND_NOT_MET" (the defect, pre-fix) and, separately, that
same review's spot check: "`../../etc/passwd` [as evidence path]: correctly refused" (an
existing, working path-traversal guard). No "Fixes applied" section exists yet for
`stl-re-deliver` in `reviews/stl-re-deliver.md`. **not run (skill under edit)**.
