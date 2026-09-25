# Round-2 independent re-review: `stl-re-*` skills

Reviewer: independent round-2 re-reviewer (not an author or round-1 fixer), 2026-09-25.
Branch `claude/skills-v1-kickoff-mtk1l9`, HEAD `86fe8a9`. Review only: no skill file was edited.
Temporary outputs went to the session scratchpad. `__pycache__` folders created while testing were removed.

Inputs read: the six `reviews/stl-re-*.md` files (findings and "Fixes applied (round 1)"),
`reviews/_answer_key_scrub.md`, `reviews/_lint.md`, `skills/stl-re-orchestrate/references/run-contract.md`,
and the code and text each fix names.

## Verdicts

| Skill | Verdict | Justification |
|---|---|---|
| `stl-re-orchestrate` | **REVISE** | O-1 to O-7 are fixed in code and text, and the selftest covers O-1, O-2 and O-7. Two cross-skill contract gaps remain, both MAJOR. (R2-O1) The documented route for a `repro_check` failure (a manual `_itN_SUPERSEDED`) cannot be delivered: deliver's CHK-SUPERSEDED requires every superseded gate to say `REVISE`, and `init_run.py` counts the folder as a loop, although the SKILL says it does not. (R2-O2) The run contract and §4 do not state the ACCEPT-BAND rules that deliver now enforces, so an acceptance recorded as this SKILL instructs is refused. |
| `stl-re-intake-datum` | **APPROVE** | B1, M1 and M2 are fixed. The code matches the fix notes: the radial residual is compared with `noise_secondary`, `matrix_4x4 = T@S` with a self-check, and tilt uses a per-feature intercept plus `per_feature`/`resolvable`. The `regime` subcommand writes the canonical flat band keys and refuses bad input (reproduced). Only MINOR items remain: stale citations. |
| `stl-re-measure-intent` | **APPROVE** | B1, B2 and M1–M4 are fixed. 28/28 selftests pass, including the M02 30/17 and P03 8 pattern counts. Only MINOR items remain: a DRM snap-leg value in SKILL text and one citation past the end of its file. |
| `stl-re-rebuild-build123d` | **APPROVE** | M1–M5 are fixed: `ScaleFrameSkipped` gives exit 3, `Params.group` accepts a list, there is a rigidity guard, Step 0 is handed to the orchestrator, and the `plane_face_*` fields exist. `export_check.json` matches run-contract §5 and §12. Only MINOR items remain: Step 0's carry-forward wording and its `init_run.py` citation predate the `--route` change. |
| `stl-re-verify` | **REVISE** | V1–V6 are fixed. The band-key refusal is reproduced in `verdict.py` and `deviation_gate.py`, and `gate.json` has the documented shape. Two MAJOR items remain. (R2-V1) The text on the decimated, inspection-only path contradicts itself. That is the path the DRM screw replay target uses. (R2-V2) A B02 golden gate number is still stated inline in `verdict.py:17`. |
| `stl-re-deliver` | **REVISE** | D1–D6 are fixed, and 31/31 fixture assertions pass on `gate.json` files that the real `verdict.assemble()` produced. One MAJOR remains: B02's golden hex AF value is stated inline in three places (SKILL, template, script comment). The answer-key scrub did not cover deliver. |

## Round-1 BLOCKER/MAJOR status (checked on HEAD)

| Skill | ID | Status | How checked |
|---|---|---|---|
| orchestrate | O-1 | fixed | `init_run.py:245-283` `gate_refusal`/`read_verdict`. The selftest (`:540`) passes. `status` on the deliver fixture copy reads a real assembled `gate.json` correctly (`verdict: APPROVED_WITH_LIMITATIONS`). |
| orchestrate | O-2 | fixed | `cmd_rehash` `:194-231`. `status` finding confirmed on the fixture copy ("exists but is not hashed"). |
| orchestrate | O-3 | fixed (doc) | SKILL §2 `intake*` row. `intake.py scale --out intake/scale.json` exists. |
| orchestrate | O-4 | fixed | SKILL §5.1 hand-off list. |
| orchestrate | O-5 | fixed | `STAGE_EXIT` `:66-78` requires `intake/regime.json` and `qa/masks.json`. `alignment.json#status==OK` `:308-317`. REGIME finding present. |
| orchestrate | O-6 | fixed (doc) | SKILL §4 row. `verdict.py` allows `REVISE` on a band fail. |
| orchestrate | O-7 | fixed | `--route` plus `CARRY_FORWARD` `:357-401`. The measure/datum routes carry nothing, so "first incomplete stage" is correct. `--route datum` moves `intake/`. |
| intake | B1 | fixed | `align.py:356-417`: radial residual, `normal_line_dist` kept as a diagnostic only, compared with `noise_secondary`. |
| intake | M1 | fixed | `align.py:320` onward: `T @ S` with a self-check. |
| intake | M2 | fixed | `align.py:146-207`: `per_feature`, `resolvable`. SKILL no longer states the DRM tilt numbers (grep is clean). |
| measure | B1, B2, M1–M4 | fixed | `run_selftests.py`: 28 passed, 0 failed. |
| rebuild | M1–M5 | fixed | `export_frames.py:77,92,120,178,232-242`; `model_template.py:67-84`; SKILL Step 0 rewritten. |
| verify | V1 | fixed | Reproduced. A regime with `tier2_p95_mm`/`tier2_max_mm` gives `verdict.py assemble` rc 2 with `verdict: null` and "unknown band key(s)", and `deviation_gate.py` rc 2 "regime refused". An intake-written `baseline-skill`/`plastic` regime is accepted. |
| verify | V2 | fixed | `--regime` is required in `deviation_gate.py`/`sim_caliper.py`. `gated_results` recomputes bands from `regime.json`. |
| verify | V3 | fixed | Without `--registration`, the gate reports `gate_invalid_reasons` "no independent QA registration" and the result is an evidence blocker (reproduced). |
| verify | V4 | fixed | `sim_caliper.py:255` sets `unmeasurable`. `verdict.py` turns it into a blocker. |
| verify | V5 | fixed | `deviation_gate.py:422-428` adds an observable-only pass to `mask_dependent_passes`. |
| verify | V6 | fixed | `geom_fails` allows only `{REVISE, HALT}`. |
| deliver | D1 | fixed | The fixture `gate.json` has exactly the key set of a live `verdict.py assemble` (compared key by key). 31/31 pass. |
| deliver | D2–D6 | fixed | The fixture covers each one (stale repro, ACCEPT-BAND under `qa/`, uncited gate, library-style `model.py`, missing limitation, uncovered `auto_limitations`). |

## Cross-skill contract checks

| Contract | Result |
|---|---|
| `regime.json` band keys, intake → verify | **Consistent.** `intake.py regime` writes `{p95_mm, max_mm, tier1_abs_mm, interface_max_mm}` plus top-level `material_class`. RE_SPEC: 1.6/4.0/0.15/0.8. baseline-skill plastic: 0.3/0.8/null/null. `baseline-skill` without `--class` is refused (rc 1). An old key through `--bands` is refused (rc 1). Verify's `normalise_bands` reads exactly these keys. Round trip reproduced. |
| `gate.json` shape, verify → deliver / `init_run status` | **Consistent.** `verdict: null` together with `errors`, plus `allowed_verdicts`, `proposed_verdict`, `hash_frozen{before,after,unchanged}`, `band_fails`, `auto_limitations`, `limitations`, `miss_explanations`. Deliver `check_publish` and `init_run.gate_refusal` both refuse on errors, a null verdict, or a verdict outside `allowed_verdicts`. MINOR: run-contract §12 says `verdict.py` *sets* `declared_in`, but `verdict.py:291` only passes it through. |
| `export_check.json`, rebuild → verify/deliver/status | **Consistent** with §5/§12: top-level `datum`/`scan`, each with `solids, valid, closed, faces, volume_mm3, area_mm2, bbox, surface_types, fillets, step, sha256`. Deliver also accepts `{"exports":…}`. MINOR: on the scale-skip path (`scan: {"skipped":…}`), `STAGE_EXIT["rebuild"]` still requires `build/<part>.step`, so `status` never marks rebuild complete, and `make_readme` renders the skipped frame as a row of `None` instead of saying it was skipped. |
| Supersede routes | The `--route` routes are consistent with deliver CHK-SUPERSEDED: every `_itN` has `qa/gate.json` with verdict REVISE, `qa/VERDICT.md` and `build/model.py`. **Broken** for the manual `repro_check`-failure route (R2-O1). Rebuild Step 0 still describes the carry-forward before `--route` existed (MINOR). |
| Decimated scan, inspection-only | The code is consistent: `init --scan-resolution`, then `deviation_gate --scan-kind decimated` → `INSPECTION ONLY`, `gate_valid:false` (reproduced), then `verdict.py` → `auto_limitations` → at best `APPROVED_WITH_LIMITATIONS`, then deliver requires a limitation that covers it. **The text is inconsistent** (R2-V1): verify `SKILL.md:213-214` and `gate-protocol.md:191` still say a decimated run "means no grade" / "Nothing is graded", which contradicts `SKILL.md:46-51` and `gate-protocol.md:142-147`. Orchestrate `SKILL.md:42-43` ("never grade a part on it") contradicts its own row at `:190`. Orchestrate requires an `OTHER` DECISIONS entry before verify grades a decimated scan, but verify neither reads nor mentions it (MINOR). |
| ACCEPT-BAND | **Inconsistent** (R2-O2). Deliver `_common.py:174-214` requires three things: evidence outside the pipeline folders; the decision text or evidence file cites a sha256 prefix of the current `qa/gate.json` (or its `created`); the decision names a `band_fails` item. Run-contract §10 and orchestrate §4 ask only for "who, date, which band, the number". Deliver's own preflight table (`SKILL.md:52`) states only the "inside the run" rule. The full rule appears only in its failure table (`:202`). |
| Evidence-blocker HALT | Verify says an evidence-only HALT (no ICP, hash not frozen, step_check not run) "does not count toward the loop limit; re-run QA". Orchestrate's HALT row says "Resume only on a human decision". This is safe (fails closed) but stricter than verify intends (MINOR). |

## Remaining findings

| Sev | file:line | Finding | Fix |
|---|---|---|---|
| MAJOR | `skills/stl-re-orchestrate/SKILL.md:193`; `scripts/init_run.py:286-293`; `skills/stl-re-deliver/scripts/_common.py:218-241` | **R2-O1.** The `repro_check`-failure route tells the agent to move `qa/` and `build/` into a manually named `_itN_SUPERSEDED/` and says "this does not count as a loop". But `superseded()` counts every `_itN_SUPERSEDED` as an iteration. Deliver's CHK-SUPERSEDED then fails because that folder's `gate.json#verdict` is APPROVED/AWL/BNM, not `REVISE`, and at iteration 3 the move exceeds the loop bound. `deliver/repro.json` also already exists, so `status` raises a CHK-PUBLISH finding once `qa/` has moved. | Choose one rule. (a) Do not supersede on a repro failure: fix `build/`, re-run verify in place (the hash freeze catches a STEP change), and log an `OTHER` DECISIONS entry. Or (b) add an `init_run.py supersede --reason repro` that writes `_itN_REPRO/` (not matched by `_it\d+_SUPERSEDED`) and teach deliver to accept it. Update the row to match the rule. |
| MAJOR | `skills/stl-re-orchestrate/references/run-contract.md:133-135`; `skills/stl-re-orchestrate/SKILL.md:130`; `skills/stl-re-deliver/SKILL.md:52` | **R2-O2.** The ACCEPT-BAND contract does not match what deliver enforces (see the table above). An acceptance recorded as orchestrate §4 says, for example with evidence `qa/VERDICT.md` and no gate hash, is refused, and every BAND_NOT_MET delivery (the OD and DRM-snap precedents) needs a second round-trip to the human. | Write deliver's three rules into run-contract §10 (evidence under `decisions/` or the run root; cite the first 12 hex characters of the current `qa/gate.json` sha256 or its `created`; name a `band_fails` item). Point orchestrate §4 option (a) at it, and complete deliver's preflight-table row. |
| MAJOR | `skills/stl-re-verify/SKILL.md:213-214`; `references/gate-protocol.md:191` | **R2-V1.** The text on the decimated path contradicts itself. Step 5 says "`INSPECTION ONLY` (decimated) … means no grade", and the "what it hides" table says "Nothing is graded". `SKILL.md:46-51` and `gate-protocol.md:142-147` (the replay-a fix) say a decimated scan is a declared limitation that can reach `APPROVED_WITH_LIMITATIONS`, and `verdict.py:151-156` implements that. The DRM screw replay target runs on the decimated scan, so the agent gets two opposite instructions on exactly this path. | Reword both lines: "INSPECTION ONLY: not an official grade; at most APPROVED_WITH_LIMITATIONS with the decimated-scan limitation (§0.2). INVALID (unconverged ICP) means no grade." Align orchestrate `SKILL.md:42-43` the same way (MINOR there, because its row at `:190` is correct). |
| MAJOR | `skills/stl-re-verify/scripts/verdict.py:17` | **R2-V2.** Answer-key leak. The docstring says "OOM-B02 hex 1.624 unmasked", B02's golden unmasked hex-pocket max, which the scrub removed from `mask-policy.md`. The scrub's grep list did not include `1.624`. | Replace it with "(CHK-MASK; B02 hex-pocket mask, see `analysis/golden/OOM-B02.md`)". |
| MAJOR | `skills/stl-re-deliver/SKILL.md:226`; `references/readme-template.md:70`; `scripts/make_readme.py:37` | **R2-D1.** Answer-key leak. `AF7.358` is B02's golden hex across-flats (the scrub removed "hex AF 7.358" from measure and verify). Deliver was explicitly outside the scrub (`_answer_key_scrub.md` header), so nobody checked it. | Use a neutral token in the prose and the comment (for example `AF7.35x`, or `AF12.345`). The test in `tests/run_fixture_test.py` may keep any value, because `tests/` is out of scope. |
| MINOR | `skills/stl-re-orchestrate/SKILL.md:60,80,130,141,189,192`; `references/run-contract.md:97`; `skills/stl-re-rebuild-build123d/SKILL.md:69,72` | Stale cross-skill line citations: the round-1 edits shifted the target files. Now `intake-datum/SKILL.md:83` and `:279` are blank lines, `rebuild/SKILL.md:248-250` is a `--fillets` CLI line (the 3-attempt rule is at `:289`), `verify/SKILL.md:227` is blank (the band-fail → REVISE rule is at `:261`), `intake-datum/SKILL.md:245-246` is tilt text (the "datum change resets" rule is at `:274`), `orchestrate/SKILL.md:107,163` is regime text, and `init_run.py:235-236` is `_load_gate` (the REVISE check is at `:368-369`). | Re-point each citation. Better: cite section names (§) for sibling SKILL files, which do not drift. |
| MINOR | `skills/stl-re-intake-datum/references/measurements-template.md:6`; `skills/stl-re-measure-intent/references/intent-rules.md:48` | These cite `golden-examples/OOM-P03_mop-pad-bracket/5_reference/MEASUREMENTS.md:69-98` / `:78-98`, but that file has 46 lines. | Correct the file or the line range. |
| MINOR | `skills/stl-re-rebuild-build123d/SKILL.md:67-69` | Step 0 says supersede "copies `MODELING_PLAN.md` and `model.py` forward". Since O-7 this is true only for `--route geometry`; the `measure`/`datum` routes carry nothing. | Say "for `--route geometry` only; after a measure or datum route, `build/` starts empty". |
| MINOR | `skills/stl-re-measure-intent/SKILL.md:206`; `skills/stl-re-rebuild-build123d/SKILL.md:161`; `templates/model_template.py:70`; `skills/stl-re-deliver/references/limitations-wording.md:64,70,112` | Golden values for parts that are not replay targets are still inline: the DRM **snap** leg angles 60/150/−60, the OD coil centre, OD p95 0.448 / max 2.49 / observable 0.567, and the DRM snap cup r 9.02. These are outside the B02 and screw-cap targets, but they break the scrub rule used elsewhere (run-contract §11 was scrubbed of the same leg angles). | Replace with placeholders (`[a, b, c]`) and a citation. |
| MINOR | `skills/stl-re-verify/scripts/_common.py:140-141` | `band_result` returns `pass: None` when `n == 0`. `verdict.py` counts only `pass is False` as a fail, so a gated zone or masked set with no points passes silently. This is the Tier-2 counterpart of V4. | Treat `n == 0` on a gated item as a blocker ("no points to grade"). |
| MINOR | `skills/stl-re-verify/scripts/verdict.py:241-243` | When CHK-LIKE4LIKE is not recorded, the default `result: "fail"` also emits "iteration comparison uses a changed protocol". That is misleading on iteration 1, and alongside "CHK-LIKE4LIKE not run". | Emit the protocol error only when `ran` is true and `result == "fail"`, or default CHK-LIKE4LIKE to `n/a` when there is no `_itN_SUPERSEDED`. |
| MINOR | `skills/stl-re-orchestrate/references/run-contract.md:178` | This says `declared_in` is "set by `verdict.py`", but `verdict.py:291` only copies it from `regime.json` (the fixture shows `null`). | Say "passed through if present", or set it in `assemble`. |
| MINOR | `skills/stl-re-orchestrate/SKILL.md:132` vs `skills/stl-re-verify/SKILL.md` (V7 text) | An evidence-only HALT (`evidence_blockers`) is meant to mean "re-run QA; not a loop", but the orchestrator's HALT row always stops for a human. | Add a row: when `gate.json#evidence_blockers` is non-empty and `blockers`/`geom_fails` are empty, re-run verify with the missing input without superseding. |
| MINOR | `skills/stl-re-orchestrate/scripts/init_run.py:74-76`; `skills/stl-re-deliver/scripts/make_readme.py:262-270` | On the scale-skip path (run-contract §11), rebuild never counts as complete (`<part>.step` is required), and the README renders the skipped scan frame as a row of `None`. | Accept `export_check.json#scan.skipped` in place of `<part>.step`/`_cad.stl`, and render "skipped: <reason>". |

Round-1 MINOR/NIT items that fixers explicitly skipped (intake m2–m9, measure m1–m4/m8–m11, orchestrate O-10/O-13 partial/O-19, verify V17, deliver D8/D12) were not re-litigated. None is a BLOCKER or MAJOR.

## Answer-key check (replay targets OOM-B02 and the Dreame screw cap)

Grep over `skills/**/*.{md,py,json}` excluding `tests/`, for every token in the scrub list plus
`1.624 1.846 0.316 25.617 26.85 24.99 27.25 27.08 13.444 12.530 25.97 18.388 21.024 0.148 0.56 1.813 0.307 0.72 0.716 2.8 117 -111 10.35 42.19 10.97 269.07`:

- **Dreame screw cap:** clean. No pentagon clock, tilt, double-D radius, bottom z or gate values remain. The M2 fix to intake did *not* re-introduce the 0.72°/2.8° figures that its fix notes quote.
- **OOM-B02:** two leaks, `verdict.py:17` (`1.624`) and deliver ×3 (`AF7.358`); see R2-V2 and R2-D1. The measure fix notes in `reviews/stl-re-measure-intent.md` quote 18.388–21.024, 0.56 and 0.148, but review files are not skill text. `references/validation.md` itself is clean.

## Lint

| Check | Result |
|---|---|
| Frontmatter: `name` = directory name, lowercase-hyphen, ≤64 characters; `description` 1–1024 characters, no `<>` | 6/6 OK. Description lengths: deliver 335, intake 351, measure 426, orchestrate 340, rebuild 374, verify 395. Only `name` and `description` keys. |
| SKILL.md length | 229–368 lines, all under 500. |
| Relative markdown links `[..](path)` | 3 found, 0 broken. |
| `py_compile` | 36/36 `.py` files under `skills/stl-re-*` (scripts, templates, tests) compile. |
| Cited repo paths with line numbers | 319 line-numbered citations parsed. 284 resolve inside the file's length. Of the rest, 33 use documented abbreviations (`OOM-B02/…`, `GE/…`, `DRM/…`); spot-resolved, they exist. The 2 P03 `MEASUREMENTS.md` ranges run past the end of the file (46 lines). The 3 wildcard paths from `_lint.md` are unchanged (not real paths; acceptable). |
| Content spot-check (45 random `path:line` citations, target line printed) | 40 point at the stated content. 5 are stale, all cross-skill SKILL.md citations: orchestrate→rebuild `:248-250`, orchestrate→intake `:245-246`, orchestrate→verify `:227`, orchestrate→`verdict-examples.md:73` (the text is at `:70-72`), rebuild→`init_run.py:235-236`. A full pass over all 16 `stl-re-*/SKILL.md:N` citations found 10 stale (listed above as MINOR). Golden-file and baseline citations were accurate: RE_SPEC `:92,170,181,248,330`, B02 `VERDICT.md:20,30,135`, B02 `70_report.py:376`, P03 `PARAM_TABLE.md:4,38,43,44`, DRM `build_screw.py:22`, DRM `screw_official_gate.json:5`, M02 `model.py:29`, M02 `VERDICT.md:6`, `SKILL_ARCHITECTURE.md:269`, OD `README.md:32,51,67,70`, among others. |

## Commands run (summarised)

| Command | Result |
|---|---|
| `python3 skills/stl-re-orchestrate/scripts/init_run.py --selftest` | `selftest OK` |
| `python3 skills/stl-re-measure-intent/tests/run_selftests.py` | `28 passed, 0 failed` (includes M02 30/17 and P03 8) |
| `python3 skills/stl-re-deliver/tests/run_fixture_test.py` | `31/31 passed`, 3 min 15 s, rc 0 |
| `intake.py regime --name RE_SPEC` / `--name baseline-skill --class plastic` / `--name baseline-skill` / `--name project-spec --bands '{"tier2_p95_mm":1}'` | rc 0 with canonical 4 keys / rc 0 with `p95_mm 0.3, max_mm 0.8, others null, material_class plastic` / rc 1 refused / rc 1 refused |
| `verdict.py assemble` on a qa/ folder with regime bands `{tier2_p95_mm, tier2_max_mm}` | rc 2, `verdict: null`, `proposed_verdict: APPROVED`, error "unknown band key(s) … (run-contract §12)" |
| `verdict.py assemble` with the intake-written baseline-skill regime | no band-key error (refused only for the missing QA blocks, as expected) |
| `deviation_gate.py` (box STL) with the old-key regime | rc 2, "regime refused: unknown band key(s)" |
| `deviation_gate.py --scan-kind decimated` (box STL, intake regime, no `--registration`) | rc 0, `label: INSPECTION ONLY`, `gate_valid: false`, reasons = [decimated, no independent QA registration] |
| Key-set comparison: fixture `qa/gate.json` vs a live `verdict.py assemble` output | identical 33 top-level keys |
| `init_run.py status` on a copy of the deliver fixture | reads `verdict: APPROVED_WITH_LIMITATIONS` from the real gate shape, iteration 2, the MEASUREMENTS un-hashed finding |
| Golden-token grep (list above) | 2 B02 leaks (verify, deliver). Non-target DRM-snap/OD values in 4 files. |
| Frontmatter, link and `py_compile` lint; citation resolver plus a 45-sample content check | see Lint |

## Fixes applied (round 2)

Edit scope for this round was limited to `skills/stl-re-orchestrate`, `skills/stl-re-verify`,
`skills/stl-re-deliver` and this file. Fixes that also touched `skills/stl-re-intake-datum`,
`skills/stl-re-measure-intent` or `skills/stl-re-rebuild-build123d` were reverted and are
reported as skipped below, out of scope for this round.

1. **R2-O1, repro-failure route — fixed.** Added `init_run.py supersede --route repro`:
   - Moves only `qa/` and `build/` into `_itN_SUPERSEDED/` (never `measure/`/`intake/`).
   - Writes `_itN_SUPERSEDED/ROUTE` (plain text, e.g. `repro\n`) recording the route.
   - Carries `build/MODELING_PLAN.md` and `build/model.py` forward (`measure/` is never
     moved for this route, so it needs no carry-forward).
   - Accepted without a REVISE verdict, but only when `deliver/repro.json#reproducible ==
     false`, or the human passes `--confirm-repro-failure` (new, documented flag).
   - Excluded from the 3-loop count: `init_run.py` now tracks `loop_iterations()` (folders
     whose `ROUTE` marker is not `repro`) separately from `superseded()` (every folder, for
     monotonic numbering); `cmd_status()["iteration"]` uses the former.
   - `stl-re-deliver/scripts/_common.py check_superseded` (CHK-SUPERSEDED) now reads the
     same `ROUTE` marker, exempts a `repro`-routed folder from the REVISE-verdict
     requirement, and excludes it from the loop count it reports.
   - Updated `skills/stl-re-orchestrate/SKILL.md` (§0 decimated-scan sidebar text, the §4
     verdict table, and the §6 HALT/ask table's `repro_check` row) and
     `references/run-contract.md` §10 to document the new route.
   - Added a selftest (`init_run.py --selftest`): refusal without `repro.json`/override,
     the happy path (moved set, carried set, `ROUTE` marker, `measure/`/`deliver/`
     untouched, `iteration` unchanged), monotonic folder numbering into a following
     ordinary-route supersede (`_it2_SUPERSEDED`, loop count advances), and
     `--confirm-repro-failure`.
   - Added a fixture case in `stl-re-deliver/tests/run_fixture_test.py`: a hand-built
     `_it2_SUPERSEDED/` with `ROUTE=repro` and a non-REVISE verdict passes preflight and
     reports `iteration: 2` (not 3).

2. **R2-O2, ACCEPT-BAND rules — fixed.** `references/run-contract.md` §10 and
   `stl-re-orchestrate/SKILL.md` §4 now state deliver's three requirements verbatim, matching
   `stl-re-deliver/scripts/_common.py check_acceptance`: (1) evidence lives outside every
   pipeline stage folder (`decisions/` or the run root); (2) the entry cites the current
   `qa/gate.json` by sha256 prefix or `created`; (3) the entry names an entry from
   `gate.json#band_fails`. Both files give the same example line (`... ACCEPT-BAND | accept
   tier1 F01 plate_x miss, gate 8dcbdc487808 | decisions/accept_band_miss.md`).
   `stl-re-deliver/SKILL.md`'s own preflight-table ACCEPT-BAND row (was line 52) was also
   completed to state the same three rules instead of only "a file inside the run".

3. **R2-V1, decimated-scan text — fixed.** `stl-re-verify/SKILL.md:213-214` and
   `references/gate-protocol.md:191` reworded to match `SKILL.md §0.2`, `gate-protocol.md §3`
   and `verdict.py`: `INSPECTION ONLY` is not an official grade but can still reach
   `APPROVED_WITH_LIMITATIONS` (never plain `APPROVED`) with the decimated-scan limitation
   declared; only `INVALID` (unconverged ICP) means no grade at all.
   `stl-re-orchestrate/SKILL.md:42-43` reworded the same way so it no longer contradicts its
   own §6 `scan_resolution` row (`:190` in round 2's numbering).

4. **R2-V2 / R2-D1, B02 golden-value leaks — fixed (in scope).**
   - `stl-re-verify/scripts/verdict.py:17`: `"OOM-B02 hex 1.624 unmasked"` →
     `"B02 hex-pocket mask, see analysis/golden/OOM-B02.md"`.
   - `stl-re-deliver/SKILL.md:226`, `references/readme-template.md:70`,
     `scripts/make_readme.py:37`: `AF7.358` → `AF12.34` (illustrative token; same shape,
     still caught by `LITERAL_DECIMAL`/the AF-hex example). `tests/run_fixture_test.py`'s two
     occurrences were also changed to `AF12.34` for consistency, even though `tests/` was
     stated as out of scope for the value itself; the regex/CHK-NUMBERS behaviour is
     unchanged (fixture re-run below still catches it as `['12.34']`).
   - Answer-key grep (B02 + Dreame-screw-cap token list from `reviews/_answer_key_scrub.md`
     plus `_round2.md`'s own list) re-run over all six skills' non-test `.md`/`.py` files.
     Remaining, **not fixed this round** (both outside the allowed edit scope, and neither
     is a B02 or Dreame-screw-cap replay-target value):
     - `skills/stl-re-intake-datum/scripts/intake.py:105` — B02 raw volume `-2434 mm^3`
       (and unlisted `n_z` figures in the same docstring). Skipped: `stl-re-intake-datum` is
       outside this round's edit scope.
     - `skills/stl-re-deliver/references/limitations-wording.md:112` — "DRM snap cup r
       9.02". This is the DRM **snap** cap (not the Dreame screw-cap replay target) and was
       already flagged in this file's own MINOR table (not in the accepted-fixes list for
       this round); left as is.
     No B02 or Dreame-screw-cap leak remains in `stl-re-verify` or `stl-re-deliver`.

5. **Stale/past-end-of-file citations — fixed where in scope, skipped otherwise.**
   Fixed (files in scope: orchestrate, verify, run-contract):
   - `stl-re-orchestrate/SKILL.md`: `stl-re-intake-datum/SKILL.md:83` → `:84-86` (×2, the
     CHK-SCALE re-run text); `stl-re-rebuild-build123d/SKILL.md:248-250` → `:287-289` (the
     3-attempt breaker); `stl-re-intake-datum/SKILL.md:245-246` → `:274` (datum-change-resets
     rule); `stl-re-intake-datum/SKILL.md:279` → `:289` (`align.py` STOP row);
     `stl-re-deliver/SKILL.md:118-119` → `:131-133` (repro-check-failure text, rewritten
     for the new route). `stl-re-verify/SKILL.md:227` → `:262` (the edit at item 3 shifted
     this target by one line from its original `:261`; verified against the live file).
   - `references/run-contract.md:97`: `stl-re-verify/SKILL.md:227` → `:262`, same reason.
   Skipped, outside this round's edit scope (target files are in `stl-re-rebuild-build123d`,
   `stl-re-intake-datum` or `stl-re-measure-intent`, none of which this round may touch):
   - `stl-re-rebuild-build123d/SKILL.md:69,72` citing `stl-re-orchestrate/SKILL.md:107,163`
     (now regime text) and `init_run.py:235-236` (now `_load_gate`, not the REVISE check at
     `:368-369`). The target orchestrate/init_run.py line numbers are already correct after
     this round's edits (`:131,204` and `:368-369` respectively) — only the citing file
     (`stl-re-rebuild-build123d/SKILL.md`) still needs the update, which is out of scope.
   - `stl-re-rebuild-build123d/SKILL.md:67-69`'s carry-forward wording (now stale after
     O-7/R2-O1: true only for `--route geometry`, and `repro` also carries the same base) —
     out of scope, `stl-re-rebuild-build123d` not editable this round.
   - `skills/stl-re-intake-datum/references/measurements-template.md:6` and
     `skills/stl-re-measure-intent/references/intent-rules.md:48`, both citing
     `OOM-P03.../MEASUREMENTS.md:69-98`/`:78-98` (file has 46 lines; the correct range for
     "per-value photo id" is `:19-34`) — out of scope, neither file's skill is editable this
     round.

## Verification (round 2 fixes)

- `python3 skills/stl-re-orchestrate/scripts/init_run.py --selftest` → `selftest OK`
  (includes the new repro-route assertions).
- `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor` → `"ok": true`, all six
  skills found side by side.
- `python3 skills/stl-re-deliver/tests/run_fixture_test.py` → `33/33 passed` (31 prior +
  the 2 new repro-route-superseded cases), run twice (once immediately after the code
  change, once after the later citation/doc edits) with identical results.
- `python3 skills/stl-re-measure-intent/tests/run_selftests.py` → `28 passed, 0 failed`
  (unaffected by this round's edits; run to confirm no regression from files this round
  left untouched).
- `python3 -m py_compile` on every changed script (`init_run.py`, `_common.py`,
  `make_readme.py`, `run_fixture_test.py`, `verdict.py`) → all OK.
