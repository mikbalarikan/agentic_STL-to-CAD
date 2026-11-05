# Review: `harnesses/v0/skills/stl-re-verify`

VERDICT: REVISE

Reviewer: independent Opus reviewer (not the author), 2026-09-25. Review only; no skill files edited.

Counts: BLOCKER 1 · MAJOR 5 · MINOR 7 · NIT 4

## Findings

| id | sev | file:line | finding | evidence | concrete fix |
|---|---|---|---|---|---|
| V1 | BLOCKER | `scripts/deviation_gate.py:226-228`, `scripts/sim_caliper.py:205`, `references/gate-protocol.md:35-41`; sibling `harnesses/v0/skills/stl-re-intake-datum/scripts/intake.py:298-300` | **The band keys differ between the two skills, so the gate fails open.** Intake writes `intake/regime.json#bands` as `{tier1_abs_mm, tier2_p95_mm, tier2_max_mm, interface_max_mm}` (RE_SPEC) or `{p95_mm, max_mm}` (baseline-skill). Verify copies that file and reads `bands.p95 / max / tier1_abs / interface_max`. Every band then resolves to `None`, `band_result` returns `None`, `verdict.py` finds no failed band, and `APPROVED` is allowed. | End-to-end reproduction: `intake.py regime --name baseline-skill --class plastic`, then `deviation_gate.py` on the full-res OD scan with that regime.json (p95 0.448, max 2.49). `deviation.bands` came out all `None`, and `verdict.py assemble` printed `band fails 0 | allowed [... 'APPROVED' ...]` and exited 0 with verdict APPROVED. | (a) Add `normalise_bands(b)` to `_common.py`. It maps `p95_mm→p95`, `tier2_p95_mm→p95`, `max_mm→max`, `tier2_max_mm→max`, `tier1_abs_mm→tier1_abs` and `interface_max_mm→interface_max`, and raises if none of `p95/max/tier1_abs` is left. Call it in `deviation_gate.py:226`, `sim_caliper.py:205` and `verdict.py assemble`. (b) In `verdict.py assemble`, add an error when `dev["regime"]["bands"] != normalise_bands(qa/regime.json bands)` or when any gated `result` is `None` while the regime has a whole-part band. (c) Write the canonical key names into run-contract §12 (orchestrator's file) so intake and verify share one spelling. |
| V2 | MAJOR | `scripts/deviation_gate.py:196,225`; `scripts/sim_caliper.py:196,204`; `scripts/verdict.py:52-79,121-127` | **The gate also fails open when `--regime` is left out** (it is optional). `verdict.py` never re-evaluates bands against `qa/regime.json`. It trusts whatever `band_result` the deviation run stored. | Simulated OD `deviation.json` with the bands a no-`--regime` run writes: `assemble` allowed APPROVED (q7 in the /tmp test). | Make `--regime` `required=True` in `deviation_gate.py` and `sim_caliper.py`. In `verdict.py gated_results`, recompute `band_result(stats, p95, max)` from `qa/regime.json` rather than reading `dev["bands"]`. |
| V3 | MAJOR | `SKILL.md:140-141` vs `references/gate-protocol.md:30-33` and run-contract §12; `scripts/verdict.py:110-111`; `scripts/deviation_gate.py:237-243,416` | **Regime handling breaks run-contract §12.** §12 says verify always runs its own ICP in every regime, reports numbers both in the builder's datum frame and after ICP, and gates after ICP. SKILL.md §5 instead says "OD and DRM graded in the alignment frame. The regime decides. If you apply ICP…". `verdict.py` blocks a missing ICP only under `RE_SPEC`, and `deviation_gate` labels an alignment-only run `OFFICIAL`. Nothing runs or compares the two frames, and nothing reports "a large gap is a datum finding". The DRM claim is also wrong: the DRM official gates record `registration_converged: true` (`analysis/golden/dreame_brush-caps.md:74`). | OD run without `--registration` was labelled `OFFICIAL (full-res)`. q3 test: baseline-skill with no ICP gave allowed = any. | Replace SKILL.md:140-141 with: "Always run ICP (run-contract §12). Run `deviation_gate.py` twice: once without `--registration` (`--out qa/deviation_datum.json`) and once with it (`--out qa/deviation.json`). The gate is `deviation.json`." In `verdict.py:110`, drop the `regime.get("name") == "RE_SPEC"` condition. Load `deviation_datum.json` when it exists, write `gate.json#deviation_datum_frame`, and add a `limits_auto` entry when the p95 of the two frames differs by more than the regime p95 band. In `deviation_gate.py:416`, set `label = "NO QA REGISTRATION"` and `gate_valid=false` when `--registration` is absent. |
| V4 | MAJOR | `scripts/sim_caliper.py:232-243,251`; `scripts/verdict.py:112-119` | **A gated Tier-1 dimension that cannot be measured passes silently.** When the caliper value is present but the CAD value is `None` (for example an empty section or no matching cylinder), `pass=None` and `all_pass=False`. `verdict.py` collects only `pass is False`, so there is no failure and no limitation. A missing `tier1.json` is also ignored, even under RE_SPEC, where Tier-1 is "per-dim, blocking" (`RE_SPEC.md:170`). | q5 test: RE_SPEC regime, converged ICP, one gated dim with `cad: null` → `blockers 0, band fails 0`, APPROVED allowed. | In `verdict.py`: (i) add every gated row with `pass is None` to `blockers` as "tier1 <id>: not measurable on STEP". (ii) When `regime.bands.tier1_abs` is set and `tier1.json` is missing, add the blocker "Tier-1 not run". (iii) When `tier1.json` is missing under another regime, add the `limits_auto` entry "no Tier-1 (no calipers)". |
| V5 | MAJOR | `scripts/deviation_gate.py:311-320,387-398`; `scripts/verdict.py:55-57`; `references/mask-policy.md` | **CHK-MASK is not applied to the observability split.** By default, CAD→scan is gated on the observable subset, which drops the "unobservable" points (OD 25.65 %) that the SKILL calls "a coverage fact, not a pass". The open-boundary mask, which B02 used for the same purpose (SYNTHESIS E6), is checked for mask-dependent passes, but the observability filter is not. A part can reach clean `APPROVED` when raw CAD→scan fails and only the observable subset passes. Also, observable stats ignore the `cad` masks, and under RE_SPEC the default gates `cad_to_scan_observable` instead of the skin-masked CAD→scan that `RE_SPEC.md:174` defines. | q3 test: raw CAD→scan max 9.03, observable passing → APPROVED allowed. | In `deviation_gate.py` after line 398: `if bands raw cad_to_scan fails and cad_to_scan_observable passes: mdp.append("whole part cad_to_scan (observable-only pass; unobservable X %)")`. In `verdict.py:55`, make the default gated key regime-dependent: `RE_SPEC → ["cad_to_scan:masked"]` (B02 `q20_tier2.py:165`) plus `scan_to_cad:masked` if the regime lists it; baseline-skill → the current default. Document both in gate-protocol §1. |
| V6 | MAJOR | `scripts/verdict.py:104-105,167-168` vs `SKILL.md:89` | **An invalid solid can be delivered.** A validity failure goes into `fails`, which allows `BAND_NOT_MET`. BAND_NOT_MET plus a human acceptance leads to delivery. SKILL.md says "A failure here is a band fail → REVISE", and gate-protocol:65 says "band fail, not a blocker". Delivering a non-solid STEP contradicts the validity rule (SYNTHESIS D12/D14). | Code path `sc["all_single_valid_closed_solid"] False → fails → allowed {BAND_NOT_MET, REVISE, HALT}`. | Add a separate list `geom_fails`. When it is non-empty, set `allowed = {"REVISE","HALT"}`. Change SKILL.md:89 and gate-protocol:65 to "validity failure → REVISE (never BAND_NOT_MET)". |
| V7 | MINOR | `scripts/verdict.py:165-166`; `SKILL.md:45-49,226`; verdict-template §2 | Every blocker allows REVISE, which counts toward the 3-loop limit. A decimated scan, a missing step check or a changed hash is not "fixable in measurement or geometry" (run-contract §7). | Run-contract §7 wording. | Split the blockers. For evidence blockers (decimated scan, hash changed, step check or deviation not run), set `allowed = {"HALT"}` and tell the agent to re-run QA; this does not count as a loop. Keep `{"REVISE","HALT"}` for ICP non-convergence and CHK-CIRCULAR=fail. Update SKILL.md:48 and verdict-template §2. |
| V8 | MINOR | `scripts/verdict.py:171-172` | When nothing fails, the allowed set includes `BAND_NOT_MET`. Run-contract §7 says BAND_NOT_MET means "a band is missed". | Code. | `allowed = {"APPROVED","REVISE","HALT"}` in the all-pass branch. |
| V9 | MINOR | `scripts/deviation_gate.py:419-420`; `SKILL.md:242-244`; `mask-policy.md` rule 8 | "Never add a mask after the fact" / "report both runs" is not enforced. Re-running overwrites `--out`, so an earlier unmasked or looser run disappears. The mask-limitation check in `verdict.py:179-182` is a substring test for "mask". | Code. | In `deviation_gate.py`, refuse to overwrite an existing `--out` unless `--supersede` is given, which renames the old file to `deviation_runN.json`. `verdict.py` lists every `deviation_run*.json` in `gate.json#deviation_runs` and renders them. |
| V10 | MINOR | `SKILL.md:123-125` | The B02 F06 window "25.99…27.08, 1.15 mm below" is stated as fact. `QUESTIONS.md` §C records that the skill's own jaw on the full-res scan gives 24.99–27.25, so the window is disputed. | `QUESTIONS.md:84-89`. | Add: "(window disputed: QUESTIONS.md §C, B02 caliper window)". |
| V11 | MINOR | `SKILL.md:21-22` | "B02 did not declare this at first (A13)". The record says B02 proceeded in-context **and declared it** (A13). | `analysis/golden/OOM-B02.md:103,326`. | Change to "B02 ran QA in the builder's context and declared it (A13, `analysis/golden/OOM-B02.md` §2, §10)". |
| V12 | MINOR | `scripts/verdict.py:131-158` | `gate.json#checks` never records CHK-ACHIEVABLE (SKILL §4 runs it) or CHK-NUMBERS. Also, `assemble` writes `verdict` into gate.json even when `errors` is non-empty, so a stale VERDICT.md combined with an erroring gate.json is not detected downstream. | Code; run-contract §6 `checks`. | Add `CHK-ACHIEVABLE` to `REVIEW_CHECKS` (result `n/a` when there is no Tier-1 miss). When `errors` is non-empty, write `"verdict": null`, write `proposed_verdict` separately, and delete any existing `qa/VERDICT.md`. |
| V13 | MINOR | `scripts/verdict.py:72-78` | Zones of `kind: "whole"` get band results in `deviation_gate.py:328-329`, but `verdict.py` never gates them. | Code. | In `gated_results`, also include zones with `kind == "whole"`. |
| V14 | NIT | `references/mask-policy.md:179`, `scripts/deviation_gate.py:16,214` | The radius sweep is cited as `q20_tier2.py:183`. The sweep loop is at line 188. | `grep -n "for rad in" q20_tier2.py` → 181, 188. | Cite `q20_tier2.py:181-190`. |
| V15 | NIT | `SKILL.md:160-161`, verdict-template §4 | "The defaults reproduce the OD golden bit-exact" holds only with the builder's STL (`OD-H12-Pump_datum.stl`) as `--cad`. The documented command passes the STEP, which QA re-tessellates at 0.005 mm. | Reviewer run below used the STL. | Add "(with `--cad OD-H12-Pump_datum.stl`, as OD did)". |
| V16 | NIT | `scripts/verdict.py:61` | `k.split(":")` breaks on a zone name that contains ":". | Code. | Use `k.split(":", 2)` and forbid ":" in zone names in gate-protocol §2. |
| V17 | NIT | sibling `harnesses/v0/skills/stl-re-measure-intent/scripts/sim_caliper.py:14` | That docstring says the script is "Shared with stl-re-verify", but verify keeps its own copy (correctly, T18). Two copies of one lift can drift apart. | Code. | In the measure copy, change to "verify keeps an independent copy (T18)". |

## What I ran

- `py_compile` on all 9 scripts: OK. `--help` on all 8 CLIs: OK.
- **OD-H12 reproduction, full-res** (`0_input/OD-H12-Pump.stl`, `report/alignment_T1.json`, `OD-H12-Pump_datum.stl`, default params, 4 z-band zones, baseline-skill regime with `p95/max` keys):
  - scan→CAD n 493,060, p95 0.4478, max 2.4934.
  - CAD→scan p95 3.4303, max 9.0269.
  - Observable n 14,870, p95 0.5671; unobservable 25.65 %.
  - Max absolute difference to `report/deviation_gate.json` over every statistic and all 8 region blocks: **0**.
  - Bands fail in both gated items, label `OFFICIAL (full-res)` (no ICP; see V3). The helper-vector fix switched 7 points with no numeric effect.
- **`verdict.py` scenarios** (synthetic `qa/` folders built around the real OD deviation):
  - OD + APPROVED → refused (exit 2).
  - OD + BAND_NOT_MET with a miss explanation → accepted; `render` wrote a correct VERDICT.md.
  - Decimated scan + BAND_NOT_MET → refused, allowed = REVISE/HALT.
  - Passing whole-part, no ICP, no Tier-1, observable-only CAD→scan pass → APPROVED allowed (V3, V5).
  - Gated Tier-1 dim unmeasurable, RE_SPEC, ICP converged → APPROVED allowed (V4).
  - No `--regime` → OD APPROVED (V2).
  - **Intake-written regime.json → OD APPROVED (V1).**
- **Golden outcomes under verdict logic:**
  - With correct band keys, the OD result is BAND_NOT_MET ✓.
  - DRM snap: its masks are scan-side and the masked max is 1.246 > 0.80, so `scan_to_cad:masked` fails → BAND_NOT_MET ✓.
  - B02: 5/24 Tier-1 plus the hex mask-dependent pass force APPROVED_WITH_LIMITATIONS ✓. The default also gates scan→CAD, which B02 never ran, so that grade assumes scan→CAD passes (see V5 on the regime-specific default).
  - All of these hold only after V1 is fixed. With the intake-written regime file every one of them can be APPROVED.
- **Independence:** no verify script imports builder or sibling code. `datum_audit` uses the builder matrix only to select regions (stated). ✓
- **Citations spot-checked (15):** RE_SPEC.md:170-175, :241, :248-250; stl2step SKILL.md:87; re-qa-verifier.md:37-38; TRACKER.md:32; OD gate.py:8-17, 30-37, 57-84; B02 q20 (:35 masks, :121 coverage, :165 whole, :181-190 sweep → V14); B02 VERDICT.md:138-145; M02 qa_report checks[0]/[21]; OOM-P03.md 4907/158k; dreame 315/570k flap; facet-film T11/T12/T15/T18. All resolve except V14 (off by 5 lines) and V11 (misread).
- **Numbers:** every threshold traces to SYNTHESIS §4. Sample counts, seeds and radii are labelled parameters ✓.
- ICP B02 re-run: see the addendum below.

## Strengths

- The deviation distance is a faithful, bit-exact lift of the OD gate, with added masked/unmasked, zones, sensitivity and clusters output.
- The honesty machinery (allowed-verdict set, mask-dependent passes, grey zone, INSPECTION ONLY label, re-run triggers, claim boundary) is the right design. It only needs the fail-open holes closed.
- The owner decisions are followed: the datum audit is report-only (`blocking: false` is hard-wired), the census is reported and not gated, and the regime is required with no default.
- SKILL.md is 269 lines, with good progressive disclosure into three references. The trigger is clear and does not collide with sibling skills.

## Addendum: B02 ICP re-run (full-res)

Command: `tier2_icp.py --scan 2_mesh_cleaned/OOM-B02.stl --scan-kind full --align 2_mesh_cleaned/alignment.json --cad 4_STEP/OOM-B02.step --scan-masks <M1 r>38.5; M2 screw from q20:35-40>`

Result: converged in **53/60** iterations, 0.6980° / 0.1864 mm, max point move 0.5026 mm, 77.8 % of correspondences kept. The golden `_tier2_it2.log` gives 48 iterations, 0.6981° / 0.1869 mm, 0.5031 mm and 233,423 of 300,000 kept (77.8 %). The pose agrees to within 0.0005 mm.

The iteration count differs from the golden (48) and from the skill's own record (51, verdict-template §4). It depends on the mask predicates and the tessellation that the ICP is given, so it is not a reproducibility defect. Recording the exact `--scan-masks` file in verdict-template §4 would make the 51 reproducible (NIT). Runtime was about 4 minutes.

## Fixes applied (round 1)

Fixer: independent Claude Code session, 2026-09-25. Scope: `harnesses/v0/skills/stl-re-verify/` only (plus this
file). `harnesses/v0/skills/stl-re-orchestrate/references/run-contract.md` was read, not edited — the canonical
band-key spelling it now records in §12 ("Band keys (canonical)") is what this round's fixes read.

| id | status | notes |
|---|---|---|
| V1 | **fixed** | `_common.normalise_bands()` reads only the canonical flat keys `p95_mm`, `max_mm`, `tier1_abs_mm`, `interface_max_mm` (run-contract §12) and raises `RegimeError` on an unknown key or when every gated key is null. `deviation_gate.py`, `sim_caliper.py` and `verdict.py` all call it and refuse to grade (non-zero exit; `verdict.py` records the error in `gate.json#errors` and forces `verdict: null`) rather than silently reading `None` from a mismatched key. Verified end-to-end: a regime with the old `tier2_p95_mm`/`tier2_max_mm` keys (as `stl-re-intake-datum/scripts/intake.py:298` still writes for RE_SPEC — an intake-side bug, out of scope here, left for that skill's fixer) is refused with `exit=2` and an "unknown band key(s)" error, not silently graded as `APPROVED`. |
| V2 | **fixed** | `--regime` is `required=True` in both `deviation_gate.py` and `sim_caliper.py` (argparse refuses to run without it). `verdict.py`'s `gated_results()` now recomputes every `band_result` from `qa/regime.json`'s normalised bands, never from `deviation.json`'s cached bands (a stale `deviation.json` from an earlier regime can no longer produce a stale pass). A consistency check flags `tier1.json`'s `band_abs_mm` disagreeing with `regime.json#tier1_abs_mm`. |
| V3 | **fixed** | `deviation_gate.py`: an alignment-only run (`--registration` omitted) is now labelled `NO QA REGISTRATION` and `gate_valid: false`, in every regime — never `OFFICIAL`. `verdict.py` drops the old RE_SPEC-only ICP condition; the missing-ICP reason from `deviation_gate.py`'s own `gate_invalid_reasons` is what blocks (as an `evidence_blocker`, HALT-only, review V7). `verdict.py assemble` now also reads `qa/deviation_datum.json` (the builder's-datum-frame run) when present, exposes it as `gate.json#deviation_datum_frame`, and adds a declared-limitation-forcing finding when its `scan_to_cad` p95 differs from the post-ICP p95 by more than the regime's p95 band. SKILL.md §5 rewritten to instruct running `deviation_gate.py` twice (`qa/deviation_datum.json` then `qa/deviation.json`) and to remove the false "OD and DRM graded in the alignment frame" claim; it now cites `golden-examples/dreame_brush-caps/report/screw_official_gate.json:5` and `snap_official_gate.json:5` (`registration_converged: true`). |
| V4 | **fixed** | `sim_caliper.py` marks a gated dim with a caliper reading but no CAD value (`cad is None`) as `unmeasurable: true`. `verdict.py` turns any gated+unmeasurable dim into a blocker ("tier1 not measurable on STEP"), turns a missing `tier1.json` into a blocker when the regime bands `tier1_abs_mm`, and into an auto-limitation ("no Tier-1 (no calipers run)") otherwise — so `APPROVED`/`APPROVED_WITH_LIMITATIONS` can no longer follow a silent Tier-1 gap. Verified: an RE_SPEC dim with an empty section (`cad: null`) now blocks even `APPROVED_WITH_LIMITATIONS`. |
| V5 | **fixed** | `deviation_gate.py` now also flags the observability split under `CHK-MASK`: when raw `cad_to_scan` fails the whole-part band but `cad_to_scan_observable` passes, `mask_dependent_passes` gets an entry naming the excluded unobservable fraction, ruling out plain `APPROVED` (at most `APPROVED_WITH_LIMITATIONS`). The regime-name-keyed default-gated-key hardcoding the review sketched was not added on top of this — `regime.json#gated` (already documented in gate-protocol §1) is the existing, more general mechanism for a regime (e.g. RE_SPEC) to name a different default; that's an intake-declaration concern, not a verify-code gap. |
| V6 | **fixed** | `verdict.py` now keeps a separate `geom_fails` list (validity failure only) with its own allowed set `{REVISE, HALT}` — `BAND_NOT_MET` can never follow an invalid/non-closed solid. Verified: a `step_check.json` with `all_single_valid_closed_solid: false` refuses a proposed `BAND_NOT_MET` (`allowed: ['HALT', 'REVISE']`). SKILL.md §3 and gate-protocol.md §2 wording updated accordingly. |
| V7 | **fixed** | `verdict.py` splits `blockers` into `evidence_blockers` (hash not frozen/changed, `step_check` not run, `deviation` gate not run, decimated scan, no independent ICP recorded — evidence is simply missing, so only `HALT` is allowed and it is documented as not counting toward the 3-loop limit) and `blockers` (ICP non-convergence, CHK-CIRCULAR fail — stays `{REVISE, HALT}`, as these may need re-measurement, not just a re-run). `gate.json` carries both lists. verdict-template.md §2 table and SKILL.md updated. |
| V8 | **fixed** | The all-pass branch now yields `allowed = {"APPROVED", "REVISE", "HALT"}` (`BAND_NOT_MET` removed — nothing missed a band). |
| V9 | **fixed** | `deviation_gate.py` refuses to overwrite an existing `--out` unless `--supersede` is passed, in which case the old file is renamed to `deviation_run<N>.json` first. `verdict.py` lists every `deviation_run*.json` (label + `scan_to_cad`/`cad_to_scan` stats) under `gate.json#deviation_runs`. Verified: a second run without `--supersede` is refused (exit 2); with `--supersede` the old file is preserved as `deviation_run1.json`. |
| V10 | **fixed** | SKILL.md §4 now appends "(window disputed: `QUESTIONS.md` §C ...)" to the B02 F06 achievable-window claim. |
| V11 | **fixed** | SKILL.md's independence section now reads "B02 ran QA in the builder's own context and declared it (A13, `analysis/golden/OOM-B02.md` §2, §10)" — citations checked against the file (§2 line 103, §10 line 326). |
| V12 | **fixed** | `CHK-ACHIEVABLE` added to `verdict.py`'s `REVIEW_CHECKS`, defaulting to `{"ran": true, "result": "n/a"}` when there is no Tier-1 miss (so a run with nothing to attribute is not forced to record it) and to a real `"fail"`/not-run error when there is a miss and it wasn't recorded. `verdict.py assemble` now writes `verdict: null` whenever `errors` is non-empty (the reviewer's proposal moves to a new `proposed_verdict` key) and deletes any stale `qa/VERDICT.md` next to an erroring `gate.json`, per the orchestrator's O-1-aligned decision. |
| V13 | **fixed** | `gated_results()` now also gates zones of `kind: "whole"` (against the whole-part `p95_mm`/`max_mm` band), not just `functional_interface` zones. |
| V14 | **fixed** | Citation corrected to `q20_tier2.py:181-190` in both `mask-policy.md:17` and `deviation_gate.py`'s `--sweep-radii` help text. |
| V15 | **fixed** | SKILL.md §6 and the "Test record" section both now state the bit-exact reproduction holds only with `--cad OD-H12-Pump_datum.stl` (the builder's own tessellation), not the STEP. |
| V16 | **fixed** | `gated_results()` splits zone keys with `k.split(":", 2)`, so a zone name may safely contain no more than the fixed `zone:<name>:<direction>` structure; gate-protocol.md's predicate-language section now states zone/mask names must not contain `:`. |
| V17 | **skipped** | Out of scope: the finding is entirely in `harnesses/v0/skills/stl-re-measure-intent/scripts/sim_caliper.py`'s docstring, a sibling skill this round was not authorized to touch. |

**Verification performed this round** (see the fixer's own working notes for exact commands):
- `py_compile` on all 4 touched scripts, `--help` on `deviation_gate.py`/`sim_caliper.py`/`verdict.py`: OK.
- **OD-H12 reproduction, full-res, re-run after the fix**: `scan_to_cad`, `cad_to_scan` and `cad_to_scan_observable` all match `report/deviation_gate.json` with **zero** difference in every statistic (n, rms, mean, p50, p95, p99, max) and the unobservable fraction — the band-key and required-`--regime`/ICP-labelling changes do not touch the distance computation. Without `--registration` the run is now labelled `NO QA REGISTRATION` (was `OFFICIAL (full-res)` before the fix); with a (synthetic, identity) `--registration` it is `OFFICIAL (full-res)`.
- **Regime refusal**: an unknown-key regime (`tier2_p95_mm`/`tier2_max_mm`), an all-null-bands regime, and an omitted `--regime` are all refused (exit 2) by `deviation_gate.py`; `verdict.py` records the same refusal in `gate.json#errors` and forces `verdict: null`.
- **Selftest scenario** (OD-like numbers, p95 0.448 / max 2.49, baseline-skill plastic band): `verdict.py assemble` accepts `BAND_NOT_MET` and refuses a proposed `APPROVED` (`allowed: ['BAND_NOT_MET', 'HALT', 'REVISE']`).
- **V6 scenario**: an invalid/non-closed solid refuses a proposed `BAND_NOT_MET` (`allowed: ['HALT', 'REVISE']`).
- **V4 scenario**: a gated Tier-1 dim with an empty section (`cad: null`) blocks even `APPROVED_WITH_LIMITATIONS`.
- **Golden grades**, built from each project's published numbers (synthetic `qa/` folders, since only OD's full-resolution scan is present in this checkout to actually re-run `deviation_gate.py` against):
  - **OD-H12**: `BAND_NOT_MET` accepted, `APPROVED` refused (real re-run, not synthetic).
  - **DRM snap**: masked max 1.246 mm > 0.80 mm band → `BAND_NOT_MET` accepted, `APPROVED` refused.
  - **OOM-B02**: Tier-1 5/24 gated + hex-pocket mask-dependent pass (masked 0.307 mm, unmasked 1.813 mm vs 0.8 mm interface band) → `APPROVED_WITH_LIMITATIONS` accepted, plain `APPROVED` refused.
- **`gate.json` top-level shape after these fixes** (keys and types, from a real `assemble` run):

  | key | type | notes |
  |---|---|---|
  | `schema`, `tool`, `tool_version`, `created` | `str` | run-contract §2 header |
  | `inputs` | `dict[str,str]` | path → sha256, run-contract §2 |
  | `seed` | `null` | header field, unused here |
  | `regime` | `dict` | `{name, source, bands, declared_in}`; `bands` as declared in `regime.json` (not necessarily normalised) |
  | `hash_frozen` | `dict \| null` | stripped `hash_freeze.json` |
  | `datum_audit` | `dict` | `{..., "blocking": false}` or `{"ran": false, "blocking": false}` |
  | `validity` | `dict \| null` | stripped `step_check.json` |
  | `surface_census` | `dict \| null` | per-step surface census |
  | `tier1` | `dict \| null` | stripped `tier1.json` (`dims` rows now carry `unmeasurable: true` where relevant) |
  | `registration` | `dict \| null` | stripped `registration.json` |
  | `deviation` | `dict \| null` | stripped `deviation.json` |
  | `deviation_datum_frame` | `dict \| null` | **new**: stripped `deviation_datum.json` (builder's-datum-frame run), run-contract §12 |
  | `deviation_runs` | `list[dict]` | **new**: `{file, label, scan_to_cad, cad_to_scan}` for every superseded `deviation_run*.json` (V9) |
  | `gated_results` | `list[dict]` | `{item, result, stats, ...}`, now recomputed from `regime.json` (V2), includes `kind:"whole"` zones (V13) |
  | `overlays` | `list[dict]` | stripped overlay JSONs |
  | `checks` | `dict[str,dict]` | `CHK-*` ids → `{ran, result, note}`; now includes `CHK-ACHIEVABLE` |
  | `blockers` | `list[str]` | REVISE/HALT-allowed evidence problems (ICP non-convergence, CHK-CIRCULAR fail, Tier-1 not run when banded, Tier-1 unmeasurable) |
  | `evidence_blockers` | `list[str]` | **new** (V7): HALT-only, does not count toward the 3-loop limit (hash not frozen/changed, `step_check`/`deviation` not run, decimated scan, no independent ICP) |
  | `geom_fails` | `list[str]` | **new** (V6): REVISE/HALT-only, never `BAND_NOT_MET` (invalid/non-closed solid) |
  | `band_fails` | `list[str]` | band misses |
  | `auto_limitations` | `list[str]` | facts forcing a declared limitation |
  | `limitations` | `list[dict]` | from `review.json`, each with `rerun_trigger` |
  | `miss_explanations` | `list[dict]` | from `review.json` |
  | `claim_boundary` | `str \| null` | from `review.json` |
  | `independence` | `str \| null` | from `review.json` |
  | `cluster_explanations` | `dict` | from `review.json` |
  | `allowed_verdicts` | `list[str]` | sorted allowed set |
  | `proposed_verdict` | `str \| null` | **renamed** from the old `verdict` input field: the reviewer's proposal from `review.json`, kept even on refusal |
  | `verdict` | `str \| null` | **changed** (V12/O-1): `null` whenever `errors` is non-empty; only ever a trustworthy value when `errors == []` |
  | `errors` | `list[str]` | hard failures; non-empty ⇒ exit 2 and `verdict: null` |

Not applied: none of the BLOCKER/MAJOR findings were skipped. Only V17 (sibling-skill docstring, out of scope) was left for that skill's own fixer.

### Additional fixes from parallel new-skill replays (round 1, continued)

The coordinator forwarded defects found while replaying this skill on fresh DRM and B02 runs (not
part of the original review table above, but accepted and applied in this same round):

| id | status | notes |
|---|---|---|
| replay-a (DRM) | **fixed** | A decimated-only scan is now a declared **limitation** in `verdict.py` (`limits_auto`, re-run trigger "full-res scan available"), not a blocker — it can reach `APPROVED_WITH_LIMITATIONS` (matching the DRM screw golden: scan-only, decimated, approved with the limitation declared) instead of being forced to `REVISE`/`HALT`. Plain `APPROVED` still requires the full-res original, since `limits_auto` being non-empty excludes it from the allowed set. `deviation_gate.py`'s `label`/`gate_invalid_reasons` for a decimated scan are unchanged (still `INSPECTION ONLY` / `gate_valid: false`) — only `verdict.py`'s classification of that reason changed. SKILL.md §0.2, gate-protocol.md §2/§3 and verdict-template.md §2 updated. |
| replay-b (DRM), part 1 | **fixed** | `datum_audit.py`'s `position.wall="inner"` no longer crashes on a bore-only (or boss-only) `region`: when the requested wall matches nothing after filtering (a single-wall selection with a degenerate `outer_sign` reference), it now falls back to keeping every point in the region rather than calling `circle_irls` on an empty array. A caller can also assert `position.single_wall: "inner"\|"outer"` to skip the empirical sign inference entirely for a region that is deliberately one wall. |
| replay-b (DRM), part 2 | **fixed** | The Fourier clock's `offset_deg` is now folded in **before** picking the nearest 360°/k candidate against the builder's declared +X, not after. Applying it only at the end let a different candidate look nearer and pick the wrong flat (the replay was 73° off); the refinement step still measures its residual window against the un-offset phase, and `offset_deg` is added once, at the end, to the final result. |
| replay-c (DRM) | **fixed** | `PHOTO-PLAUSIBILITY` now defaults to `{"ran": true, "result": "n/a"}` when `review.json` explicitly declares `"photos": []` (no photos taken for the run), instead of forcing every run to record a check with nothing to check. Omitting `photos` entirely still requires the check to be recorded (an agent cannot skip it by simply forgetting the field). Documented in verdict-template.md §2. |
| replay-d (DRM) | **fixed** | No code change to `tier2_icp.py`: `--max-iter` was already a parameter (default 60, not a hard threshold) and non-convergence was already reported clearly. SKILL.md §5 now explicitly says the cap may be raised with the reason recorded (citing the replay needing 90) and warns against inventing a new default — it stays a per-run, per-part decision. |
| D6 (B02 replay) | **fixed** | `datum_audit.py`'s `position.wall` fix now *detects* a missing outer/inner wall pair before trusting the empirical sign convention: it compares the normal sign of the innermost-10%-by-radius faces against the outermost-10%-by-radius faces. If they agree (no real wall split exists in the selection), it **refuses with a clear `SystemExit`** naming the fix (`position.single_wall`) instead of silently keeping an arbitrary near-random half of the points, which is what produced the replay's false 17.8°/9.2 mm audit. A genuine two-wall selection (inner and outer signs disagree, the common case, verified against a synthetic annulus) is unaffected — same `keep` computation as before. gate-protocol.md §2 and SKILL.md §2 document the requirement and the `single_wall` escape hatch. |

**Verification for the new items:**
- `datum_audit.py --help` and `py_compile`: OK.
- Synthetic point-set check: a single-wall (bore) selection gives `inner_sign == outer_sign` (triggers the new refuse path); a genuine two-wall (inner+outer) annulus gives opposite signs (unaffected, same behaviour as before the fix).
- Re-ran the OD-H12 full-res `deviation_gate.py` reproduction after all changes in this round (including the decimated-scan reclassification, which touches `verdict.py` only): still **zero** difference against `report/deviation_gate.json` in every statistic.
- Verified the decimated-scan reclassification with a synthetic `qa/` folder: `gate_invalid_reasons = ["decimated scan: ..."]` now lands in `auto_limitations`, `allowed_verdicts` includes `APPROVED_WITH_LIMITATIONS` (not just `HALT`), and plain `APPROVED` is still refused.
- Did not reconstruct a full B02 `datum_spec.json` to re-run `datum_audit.py` end-to-end against real B02 geometry in this round (out of scope for the time available); the synthetic-array checks above exercise the exact branch condition that changed.
