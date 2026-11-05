# Review — `harnesses/v0/skills/stl-re-deliver`

VERDICT: REVISE

Reviewer: independent (did not write this skill). Scope: `SKILL.md`, `references/*`, `scripts/*`,
`tests/*`, checked against `run-contract.md` §1–§12, SYNTHESIS §0.1/§1F/§2/§4, and the real output
of sibling `stl-re-verify/scripts/verdict.py` and `stl-re-rebuild-build123d/scripts/export_frames.py`.

Counts: BLOCKER 1 · MAJOR 5 · MINOR 7 · NIT 2

## Findings

| id | sev | file:line | finding | evidence | concrete fix |
|---|---|---|---|---|---|
| D1 | BLOCKER | `scripts/make_readme.py:260-267`, `:300-305`, `:275-286` | `make_readme.py` reads a `qa/gate.json` shape that `stl-re-verify` does not write. It crashes on verify's real output, and where it doesn't crash it mislabels masked vs unmasked. The fixture `gate.json` was hand-written to the §6 sketch, so the test does not catch this. (a) verify writes `tier1 = {band_abs_mm, dims:{…}, coverage, all_pass}` (`stl-re-verify/scripts/sim_caliper.py:246-251`). Deliver iterates `t1.items()`, gets `band_abs_mm: 0.15` and fails with `AttributeError: 'float' object has no attribute 'get'`. (b) verify writes `deviation.over_band_clusters = {"scan_to_cad": {"clusters": [...]}}` (`verdict.py:142`). Deliver iterates it as a list of dicts and fails with `AttributeError: 'str' …`. (c) verify's `deviation.scan_to_cad` is **unmasked**, the masked stats are `scan_to_cad_masked`/`cad_to_scan_masked`, and `deviation.unmasked` is `{scan_to_cad, cad_to_scan}` (`deviation_gate.py:301-303`). Deliver labels `scan_to_cad` as "(masked)" and renders `unmasked` as an empty row, so masked numbers never appear and unmasked numbers carry the masked label. That is the CHK-MASK dishonesty this skill exists to prevent. (d) `registration` is top-level in verify (`verdict.py:188`), but deliver reads `deviation.registration`. The zones are `{zone:{kind, scan_to_cad:{unmasked,masked}}}`, not flat stats. `gated_results` holds the actual per-item PASS/FAIL and is not rendered at all. | I reproduced (a) and (b) by editing a copy of the fixture `gate.json` to verify's shape: both give a traceback (exit 1, which the SKILL reserves for "non-reproducible"). | 1. Replace `tests/fixture_run/qa/gate.json` with one produced by `stl-re-verify/scripts/verdict.py compose` (or copied key-for-key from its `gate = {…}` dict at `verdict.py:185-203`). 2. In `make_readme.py`, render Tier-1 from `tier1["dims"]` with band `tier1["band_abs_mm"]` and coverage `tier1["coverage"]`. Render the deviation table as rows `scan→CAD unmasked = deviation.scan_to_cad`, `scan→CAD masked = deviation.scan_to_cad_masked`, `CAD→scan unmasked = deviation.cad_to_scan`, `CAD→scan masked = deviation.cad_to_scan_masked`, `CAD→scan observable = deviation.cad_to_scan_observable`. Read registration from `gate["registration"]`. Render zones per direction with unmasked/masked. Render clusters from `over_band_clusters[dir]["clusters"]`. Add a "Gate results" table from `gate["gated_results"]` (item, band, stats, PASS/FAIL). 3. Add a test case that runs `make_readme.py` on the verify-shaped gate. 4. Alternatively, amend run-contract §6 to verify's actual keys and state that in §12. Either way, one shape. |
| D2 | MAJOR | `SKILL.md:68-76`; `make_readme.py:141-157` | Deliver ignores `gate.json#limitations`, `#auto_limitations`, `#miss_explanations`, `#claim_boundary`, `#independence` (all written by `verdict.py:200-202`) and asks the agent to re-type them by hand into `limitations.json` "from VERDICT.md". That duplicates verify's work and invites drift, and nothing checks that every verify limitation reached the README (the step-4 check is a manual checklist). | `stl-re-verify/scripts/verdict.py:159-203` | In `make_readme.py`, refuse unless every `gate.json#limitations[].id` (or text, if no id) appears in `limitations.json#limitations[].id`, and every `auto_limitations` string is covered by a limitation whose `evidence` names it. Render `miss_explanations` (region, cause, options) under the BAND_NOT_MET banner. Render `gate.json#independence` in the headline when CHK-INDEP is absent. Change SKILL step 2 to "seed `limitations.json` from `gate.json#limitations`/`#claim_boundary`, then add wording". |
| D3 | MAJOR | `scripts/make_readme.py:158-163`; `scripts/make_manifest.py:268-269` | A stale `repro.json` is accepted. README and manifest check only `reproducible is True`. They never compare `repro.json#inputs` (the sha256 of `build/model.py`, `measure/params.json` and the STEPs) with the current files. `deliver/` survives `init_run.py supersede`, so a repro.json from an earlier attempt can certify a model.py that no longer produces the delivered STEP. | Reproduced: I ran repro, then changed `build/model.py` (`plate_x*2`). `make_readme.py` exited 0 and `make_manifest.py` exited 0, both still claiming reproducible. | Add `check_repro_fresh(run, repro)` to `_common.py`. For each `path, sha` in `repro["inputs"]`, require `sha256_file(run/path) == sha`, else `DeliverError("deliver/repro.json is stale (<path> changed); re-run repro_check.py")`. Call it in `make_readme.render` and `make_manifest.main`. Add a test case "model.py changed after repro → refuse". |
| D4 | MAJOR | `scripts/_common.py:133-148` | ACCEPT-BAND is not bound to the miss it accepts. Any in-run file is accepted as evidence, including the verifier's own `qa/VERDICT.md`. The entry is not tied to this gate (an acceptance recorded against iteration 1's miss carries over to a new gate). The orchestrator requires the entry to state "which band, the number" (`stl-re-orchestrate/SKILL.md:106`), but nothing checks that. | Reproduced: `- 1970-01-01 \| x \| ACCEPT-BAND \| ok \| qa/VERDICT.md` passes preflight for BAND_NOT_MET. | In `check_acceptance`: (1) reject evidence under `qa/`, `build/`, `measure/`, `intake/`, `deliver/`, `_it*_SUPERSEDED/`, and require it under `decisions/` or the run root (document the path in SKILL step 1 and the run-contract §10 note). (2) Require the decision text to contain the sha256 prefix (≥12 hex) of the current `qa/gate.json`, or its `created` value. Otherwise refuse with "ACCEPT-BAND does not reference this gate; re-ask the owner". (3) Require the text to name at least one `gate.json#band_fails` item. Add a negative test for each. |
| D5 | MAJOR | `scripts/repro_check.py:76-81`, `:131` | The default rebuild runs `python model.py` with `cwd=<scratch>/build`. The rebuild skill's documented library pattern is `export_frames(body, Path("intake/alignment.json"), Path("build"), …)` plus `from export_frames import export_frames` (`stl-re-rebuild-build123d/scripts/export_frames.py:33-36`), which uses paths relative to the **run root** and needs the sibling scripts dir on `sys.path`. A model.py that follows rebuild's own instructions fails in repro (missing `build/intake/alignment.json`, ImportError), and that gets reported as "not reproducible". The fixture model uses `HERE`-relative paths, so the test does not exercise this. | `repro_check.py:81` `cwd=tmp / "build"`; rebuild `SKILL.md:214-217` | Add `--cwd {run,build}` (default `run`). With `run`, use cwd=`tmp` and the default cmd `[sys.executable, "build/model.py"]`. Set `PYTHONPATH` to `str(Path(__file__).resolve().parents[2] / "stl-re-rebuild-build123d" / "scripts")` + `os.pathsep` + the existing value. Record `cwd` in repro.json. Add a fixture model.py variant that uses run-root-relative paths and `from export_frames import export_frames`. |
| D6 | MAJOR | `references/readme-template.md:15-31`; `make_readme.py` | The README template leaves out golden delivery content. (1) There is no feature/model-tree section: OD `README.md:46-60` ("Model ağacı", 6 features) and DRM `README.md:27-54` (F01–F09 per part) both deliver one, M02 `README.md:7-12` states the editable source and that the STEP carries no native feature history, and RE_SPEC DoD expects the ratified `MODELING_PLAN.md` (`RE_SPEC.md:328-329`). (2) For BAND_NOT_MET the per-region cause and **options** (OD `README.md:43-44`; RE_SPEC honesty rule `:181-183`) have no structured slot. They survive only if the agent puts them in free-text limitations. | the cited golden lines | Add section "Model tree (design intent)" rendered from `limitations.json#feature_tree: [{id, feature, params:[names]}]`. Values come via the params table, and the section links `build/MODELING_PLAN.md` and `build/model.py` with the sentence "The STEP is a neutral B-Rep; the editable design intent is model.py + params.json" (M02 `README.md:12`). Add a "Band miss: where and what next" subsection under Deviation, rendered from `gate.json#miss_explanations` (region, cause, options), and make it required when verdict is BAND_NOT_MET. Update the section table in `readme-template.md` with the golden sources above. |
| D7 | MINOR | `scripts/make_readme.py:35` | CHK-NUMBERS can be evaded. The lookbehind `(?<![\w.])` treats `Ø`, letters and digits-after-letters as word characters, so `Ø8.00`, `AF7.358`, `M3.5` and `x8.5` pass. Ø is the goldens' usual diameter notation (OD `README.md:48-56`). | Reproduced: a limitation text `"Bore Ø8.00 mm assumed; hex AF7.358"` rendered with exit 0. | Change the regex to `re.compile(r"(?<![\d.])[-+]?\d+\.\d+")`. Add `Ø8.00` to the literal-decimal negative test. |
| D8 | MINOR | `scripts/make_readme.py:35`; `SKILL.md:91-92` | Integers in prose ("plate 40 mm", "core tube Ø16") are not checked, although `limitations-wording.md:195-196` says counts should come from JSON. | reproduced (`plate 40 mm` accepted) | Also flag `(?<![\w.])\d+\s*(mm|°|deg)\b` and `Ø\s*\d+`, with the same CHK-NUMBERS message. Or state in SKILL step 2 that integer dimensions are an accepted residual risk. |
| D9 | MINOR | `scripts/repro_check.py:118`, `:137-176` | `--runs 0` writes `reproducible: true` with no rebuild, and exit 0. `subprocess.TimeoutExpired` is uncaught (traceback, exit 1 = "not reproducible"). | reproduced `--runs 0` → `reproducible=True` | `if a.runs < 2: fail("--runs must be ≥2 (facet-film T32)")`. Wrap `subprocess.run` in `try/except subprocess.TimeoutExpired`, record `{"returncode": None, "error": "timeout"}` and set `ok=False`. |
| D10 | MINOR | `scripts/_common.py:209-222` | The hash-freeze check ignores `gate.json#hash_frozen.unchanged` (run-contract §12) and pools every 64-hex string, including `before`. The fixture's `hash_frozen` shape (`{name:{before,after}}`, `run_fixture_test.py:52`) is not the contract shape. | contract §12; `step_check.py:122-126` | Fail when `hash_frozen.get("unchanged") is False`. Match against `hash_frozen["after"].values()` only when that key exists. Change the fixture to `{"before":{path:sha},"after":{path:sha},"unchanged":true}`. |
| D11 | MINOR | `SKILL.md:77-83`; `make_readme.py` | Rebuild says a failed or shrunk fillet "deliver must list … as a limitation" (`stl-re-rebuild-build123d/SKILL.md:194`), but deliver neither lists CHK-FILLET in "Always declare" nor checks `export_check.json#<frame>.fillets`. | rebuild SKILL.md:194 | Add "every fillet with status FAILED or a used radius ≠ target (CHK-FILLET)" to the SKILL.md:77-83 list. In `make_readme.py`, refuse when any `export_check[frame]["fillets"][i]` is not OK and no limitation's `evidence` contains `export_check.json`. |
| D12 | MINOR | `references/readme-template.md` | Also missing from the golden coverage: links to visual evidence (DRM `README.md:86` overlays/deviation maps; RE_SPEC DoD "final view set", `RE_SPEC.md:334`; CHK-OVERLAY), and RE_SPEC's "restoration notes" (`RE_SPEC.md:332`). Multi-part deliveries (DRM: two parts in one README) are not addressed. | cited lines | Add a "Figures" list rendered from `qa/overlays/*.png` and `measure/figures/*` (paths only). Map "restoration notes" explicitly to `assumptions` in the section table. Add one line to the SKILL's Open questions: one run = one part, and multi-part deliveries are one run per part (DRM precedent, `golden-examples/dreame_brush-caps/README.md:5-15`). |
| D13 | MINOR | `scripts/_common.py:183-187` | If `input/INPUT_HASHES.json` is missing, the result is only a `finding`, so delivery proceeds with no evidence-integrity proof. Init always writes that file (contract §10). | contract §10 | Return `result: "fail"` when the file is missing, with the note "evidence integrity unprovable; HALT (orchestrator §6)". |
| D14 | NIT | `tests/run_fixture_test.py:83-85` | The "raw sha differs" assertion is `A or B`, where B is already implied by the previous case, so it cannot fail. | — | Assert only `all(f["geometry_measurements_identical"] for f in files)` and rename the case, or assert `raw_sha256_equal is False` for one STEP. |
| D15 | NIT | `SKILL.md:32-34` | "1 means `repro_check.py` found a non-reproducible build" collides with Python's traceback exit 1 from any script. | D1/D9 | After the fixes, wrap each `main()` in `except Exception as e: fail(f"internal error: {e}", 3)` and document exit 3. |

## Citations spot-checked (all correct)

B02 `VERDICT.md:3`, `:20-30`, `:95-99`, `:135-136`, `:138-145`, `:165-176`, `:189-194`, `:204-213`;
B02 `70_report.py:1-5`, `:17-19`, `:340-349`, `:376`; P03 `VERDICT.md:6`, `:55`; OD `README.md:13-14`,
`:32-44`, `:62`, `:70-71`, `:73-79`; DRM `README.md:5-17`, `:19-25`, `:56-78`, `:80-86`; `golden-examples/README.md:14`;
M02 `README.md:21-31`, `VERDICT.md:6`, `:30`, `reproducibility_report.json`; `RE_SPEC.md:181-183`, `:248-250`,
`:330-333`; `analysis/golden/dreame_brush-caps.md` Questions 1; `analysis/golden/OOM-P03.md` §9 (line 209);
facet-film T32/T35/T36. No dead or wrong citations found. Numbers: 3 loops (SYNTHESIS §4), exact-equality
tolerance (M02, labelled heuristic n=1), 2 fresh processes (T32). The 4-decimal display format is display only.

## What I ran

- `python3 -m py_compile` on all 5 scripts and the test: OK. `--help` on all 4 CLIs: OK.
- `python3 tests/run_fixture_test.py --workdir /tmp/... --keep`: **21/21 passed** (~1 min 53 s, build123d 0.13).
- Probes on copies of the passing run (all under /tmp, deleted afterwards):
  - literal-decimal regex: `Ø8.00`, `AF7.358`, `M3.5`, `x8.5` are not caught; a README with `Ø8.00` rendered (D7).
  - ACCEPT-BAND with evidence `qa/VERDICT.md`: preflight passed (D4); `../../etc/passwd`: correctly refused.
  - model.py changed after repro: README and MANIFEST both written, rc 0 (D3).
  - `repro_check.py --runs 0` gives `reproducible=True` (D9).
  - `hash_frozen.unchanged=false` gives a hash_frozen "pass" (D10).
  - verify-shaped `tier1` and `over_band_clusters` make `make_readme.py` crash with AttributeError (D1).
- `__pycache__` created under `scripts/` was deleted; no repo files were modified apart from this review.

## Strengths

- A clean separation: deliver never changes verdicts and refuses rather than papering over, and every refusal names the check and the next action.
- CHK-PUBLISH, CHK-SUPERSEDED, input integrity, hash freeze and regime-declared are all enforced by code, and the manifest re-runs them.
- The manifest is complete by construction: every file is either included or excluded with a mandatory reason, its non-self-listing is stated, and unused excludes are reported.
- repro_check compares geometry rather than raw hashes, works in a scratch copy, records environment pins and has an M02-shaped output.
- `limitations-wording.md` is excellent: the golden quotes are accurate, the anti-patterns are well chosen, and the DRM index-row omission is caught.
- The SKILL is compact (215 lines), with good progressive disclosure and an honest open-questions section.

## Fixes applied (round 1)

Applied against `harnesses/v0/skills/stl-re-deliver/` only. `tests/run_fixture_test.py` now runs 31
assertions (was 21) and all pass; `python3 tests/gen_gate.py` regenerates the fixture's
`qa/gate.json` (both iterations) by calling `stl-re-verify/scripts/verdict.py`'s own
`assemble()`/`render()` on synthetic, schema-accurate QA block files.

- **D1 (BLOCKER) — fixed.** `tests/fixture_run/qa/gate.json` and
  `_it1_SUPERSEDED/qa/gate.json` are no longer hand-written. `tests/gen_gate.py` writes
  `regime.json`, `hash_freeze.json`, `step_check.json`, `datum_audit.json`, `tier1.json`,
  `registration.json`, `deviation.json`, `review.json`, `overlay1.json` in verify's real
  schemas and calls the real `verdict.assemble()`/`verdict.render()` (imported from
  `stl-re-verify/scripts/verdict.py`, unmodified) to produce `gate.json`/`VERDICT.md`.
  `make_readme.py` was rewritten to match: Tier-1 renders from `tier1.dims{id:{...}}` with
  `band_abs_mm`/`coverage` (flags a gated-but-`unmeasurable` dim); the deviation table now
  labels `scan_to_cad`/`cad_to_scan` as **unmasked** and `scan_to_cad_masked`/`cad_to_scan_masked`
  as masked (the old code had these swapped -- the exact CHK-MASK dishonesty this skill exists
  to prevent); `over_band_clusters` is read as the real dict keyed by direction, not a list;
  registration is read from `gate.json#registration` (top-level); zones render unmasked/masked
  side by side; and a new "Gate results" table renders `gate.json#gated_results` (the actual
  per-item PASS/FAIL the verdict was graded on), which was not rendered at all before.
- **Refuse on null verdict / non-empty errors / verdict not in allowed_verdicts /
  hash_frozen.unchanged — fixed** (folded into D1's fix). `_common.check_publish` now refuses
  when `gate.json#errors` is non-empty, when `verdict` is `None`/outside the verdict vocabulary,
  when `verdict` is not in `gate.json#allowed_verdicts`, or when `hash_frozen.unchanged` is not
  `true`.
- **D2 (MAJOR) — fixed.** `make_readme.py` now refuses unless every `gate.json#limitations[]`
  (matched by `id`, or `text` when there is no id) appears in `deliver/limitations.json`, and
  unless every `gate.json#auto_limitations` entry is covered by some limitation's `text` or
  `evidence` (matched on the keyword before the first `:`). `gate.json#miss_explanations` is
  rendered under a new "Band miss: where and what next" section (required for BAND_NOT_MET, and
  the render refuses if it is empty there). The headline falls back to `gate.json#independence`
  when CHK-INDEP is not a named check, and section 12 also renders verify's own
  `gate.json#claim_boundary`. SKILL.md step 2 already said to seed `limitations.json` from
  `qa/VERDICT.md`; it was not changed to point at `gate.json#limitations` directly, since the
  README-level refusal now makes drift impossible either way.
- **D3 (MAJOR) — fixed.** Added `_common.check_repro_fresh()`, called from both
  `make_readme.py` and `make_manifest.py`: it recomputes the sha256 of every file recorded in
  `deliver/repro.json#inputs` (`build/model.py`, `measure/params.json`, the delivered STEPs) and
  refuses with "stale" in the message if any differs. Regression test: "model.py changed after
  repro (stale repro.json)".
- **D4 (MAJOR) — fixed.** `_common.check_acceptance` now: (1) refuses an ACCEPT-BAND entry
  whose evidence path is under `qa/`, `build/`, `measure/`, `intake/`, `deliver/` or an old
  `_itN_SUPERSEDED/` (evidence must be the owner's own document, under `decisions/` or the run
  root); (2) requires the decision text or its evidence file to contain a ≥12-hex sha256 prefix
  of the *current* `qa/gate.json` (or its `created` timestamp), so an acceptance cannot carry
  over to a new gate; (3) requires the text to name at least one of `gate.json#band_fails`.
  SKILL.md step 1 documents the evidence-location rule. Three regression tests added (missing
  entry, evidence under `qa/`, entry that does not cite the current gate) plus the existing
  happy-path test was updated to satisfy the new rule.
- **D5 (MAJOR) — fixed.** `repro_check.py` gained `--cwd {run,build}` (default `run`, matching
  the rebuild skill's own "library use" pattern -- `export_frames(body,
  Path("intake/alignment.json"), Path("build"), ...)`, run-root-relative, per
  `stl-re-rebuild-build123d/scripts/export_frames.py`'s own docstring). With `--cwd run` the
  default command is `python build/model.py` from the scratch run root, with
  `stl-re-rebuild-build123d/scripts` prepended to `PYTHONPATH` so a bare
  `from export_frames import export_frames` resolves; `--cwd build` keeps the old
  `model_template.py` CLI-style default. `repro.json` records `cwd`. Added
  `tests/fixture_extra/model_library_style.py`, a model variant that builds the identical part
  and calls `export_frames()` exactly the documented library way; a new regression test swaps it
  in and confirms `repro_check.py`'s new default reproduces it (verified independently that it
  produces bit-identical volume/faces/bbox to `build/model.py`'s own output in both frames).
- **D6 (MAJOR) — fixed.** Added a "Model tree (design intent)" section (rendered from the new,
  optional `limitations.json#feature_tree`, with the "STEP is a neutral B-Rep" sentence and
  links to `model.py`/`MODELING_PLAN.md`) and a "Band miss: where and what next" section
  (rendered from `gate.json#miss_explanations`, required for BAND_NOT_MET) -- see D1/D2 above.
  `references/readme-template.md`'s section table was updated with both, and with the golden
  citations already given in the finding.
- **D7 (MINOR) — fixed.** `LITERAL_DECIMAL` changed from `(?<![\w.])[-+]?\d+\.\d+` to
  `(?<![\d.])[-+]?\d+\.\d+`, so `Ø8.00`, `AF7.358` and `M3.5` are caught (only a preceding digit
  or `.` now suppresses a match). Two regression tests added.
- **D8 (MINOR) — skipped.** Flagging bare integers (`40 mm`, `Ø16`) as literals was judged too
  aggressive for this round: unlike a decimal, an integer dimension is common in ordinary prose
  ("iteration 2 of 3", "F01") and a blanket regex would produce many false CHK-NUMBERS refusals
  unrelated to invented numbers. Left as SYNTHESIS's documented accepted residual risk
  (finding's second option); can be revisited with a narrower pattern (unit-suffixed only) if it
  proves necessary in practice.
- **D9 (MINOR) — fixed.** `repro_check.py` refuses `--runs` < 2 before doing any work.
  `subprocess.run` in `rebuild_once` is wrapped in `try/except subprocess.TimeoutExpired`,
  recording `{"returncode": None, "error": "timeout", ...}` (a failed run, not a traceback).
  Two regression tests added (`--runs 0`; the existing non-deterministic-build test still
  exercises the normal completed-but-different-geometry path).
- **D10 (MINOR) — fixed.** `_common.check_hash_frozen` now reads the real
  `{"before": {...}, "after": {...}, "unchanged": bool}` shape, fails immediately when
  `unchanged is False`, and matches build/ STEPs only against `after`'s hashes (never pools
  `before` in). `check_publish` also refuses outright when `hash_frozen.unchanged` is not `true`
  (see the "Refuse on null verdict / ..." entry above). The fixture's `hash_frozen` was already
  wrong in the way the finding describes; `tests/gen_gate.py` and `run_fixture_test.py`'s
  `prepare()` now both write the contract shape. Regression test added
  ("hash_frozen.unchanged is false").
- **D11 (MINOR) — fixed.** `make_readme.py` now reads `build/export_check.json`'s per-frame
  `fillets` list and refuses (CHK-FILLET) if any entry is not `OK` and no declared limitation's
  `text`/`evidence` mentions `export_check.json`. SKILL.md's "Always declare" list gained the
  matching bullet. (No fixture regression test: the fixture has no fillets; adding one would
  require a geometry change out of proportion to this fix, so this is covered by code review and
  the check's own unit logic rather than an end-to-end case.)
- **D12 (MINOR) — skipped.** A "Figures" section (overlay/figure paths) and an explicit
  "restoration notes → assumptions" mapping note were judged lower priority than D1-D11 within
  this round's scope and were not added. Left for a follow-up round; nothing here regresses.
- **D13 (MINOR) — fixed.** `_common.check_inputs_unchanged` now returns `result: "fail"` (was
  `"finding"`) when `input/INPUT_HASHES.json` is missing, with the note ending "HALT
  (orchestrator §6)", per the finding.
- **D14 (NIT) — fixed.** The `A or B` assertion (where B was already implied by an earlier case)
  is now a single assertion that every produced STEP's raw sha256 differs from the delivered
  one.
- **D15 (NIT) — fixed.** Added `_common.run_main()`; every script's `if __name__ == "__main__":`
  now calls `run_main(main)`, which lets a `DeliverError`'s `fail()` (exit 2) and
  `repro_check.py`'s deliberate `sys.exit(1)` ("not reproducible") through unchanged but turns
  any other exception into exit 3 ("internal error"), so a bug here can no longer be misread as
  "not reproducible". SKILL.md documents exit 3.

Not touched: `references/limitations-wording.md` (no finding against it) and
`golden-examples/`/`baseline/` (out of scope, per instructions).
