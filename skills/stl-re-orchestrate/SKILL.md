---
name: stl-re-orchestrate
description: Entry point for turning a scanned STL mesh into design-intent parametric CAD (STEP) with build123d. Use when asked to convert a scan, STL or mesh into STEP/CAD, remodel a part from a 3D scan, or resume, re-run or check the status of such a job. Runs intake → measure → rebuild → verify → deliver with bounded iterations and honest verdicts.
---

# stl-re-orchestrate

You run the job as a state machine. You own the run folder, the stage order, the
verdict vocabulary, the 3-loop bound, the HALT/ask rules, independence (CHK-INDEP),
CHK-PUBLISH and CHK-SUPERSEDED. You do no geometry math: each stage is a sibling skill.

Read `references/run-contract.md` before the first stage. It fixes every path and JSON
key the stages exchange. Worked verdicts: `references/verdict-examples.md`.

## 0. Prerequisites (check first, HALT if missing)

1. Run `python3 scripts/init_run.py doctor`. It checks `numpy`, `scipy`, `trimesh`,
   `build123d` and that all six skills sit side by side (`stl-re-orchestrate`,
   `stl-re-intake-datum`, `stl-re-measure-intent`, `stl-re-rebuild-build123d`,
   `stl-re-verify`, `stl-re-deliver`). Exit code 2 = something missing.
2. If anything is missing, HALT and report. Do not improvise a missing stage in your own
   context: missing agents/skills are how QA became "not organisationally independent"
   (`baseline/oomwoo-re-pipeline/RE_SPEC.md:364-373`; `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md` §7).
3. If an older copy of a skill with the same name exists elsewhere in the skills path,
   remove or rename it; a stale same-named verifier once shadowed the current gate
   (`baseline/oomwoo-re-pipeline/RE_SPEC.md:369-373`).
4. Load meshes only inside scripts and print compact summaries, never vertex dumps
   (`analysis/baseline/facet-film-transferable.md` T1).

## 1. Start or resume

- **New job:**
  `python3 scripts/init_run.py init <run> --part <name> --scan <scan.stl> [--photos <dir|files>] [--measurements <filled MEASUREMENTS.md>] --scan-resolution full|decimated|unknown`.
  It creates the layout, copies inputs read-only (or `--link`), writes
  `input/INPUT_HASHES.json` (sha256) and `DECISIONS.md`. It does not create `deliver/`.
- **Resume / status:** `python3 scripts/init_run.py status <run>` prints the iteration,
  the last complete stage, the verdict, and findings (changed inputs, CHK-PUBLISH breach,
  missing calipers, an un-hashed filled measurement sheet, a gate verdict verify refused).
  Continue at the first incomplete stage. Artefacts are the state: never trust a remembered
  state over the folder. After a `supersede`, the route already decided what carried
  forward (§4), so "first incomplete stage" lands correctly without a separate pointer.
- Official deviation gates run on the full-resolution scan. A decimated scan is for
  inspection only; never grade a part on it (`golden-examples/README.md` "What was left
  out"; `analysis/SYNTHESIS.md` A3).
- Every human decision goes into `<run>/DECISIONS.md` (append-only, format in the file):
  regime, calipers/scan-only, part class, band acceptance, HALT, independence.

## 2. Stage machine

```
init → intake → [human: MEASUREMENTS + REGIME] → intake* → measure → rebuild → verify ─┬─ APPROVED / APPROVED_WITH_LIMITATIONS ──→ deliver
                                                                                         ├─ BAND_NOT_MET ─ [human: ACCEPT-BAND] ─→ deliver
                                                          ▲                              ├─ REVISE (loop < 3) ─ supersede --route ─┐
                                                          └──────── route by finding ◄───┘                                        │
                                                                                         └─ HALT (or REVISE at loop 3) → stop, ask human
```

`intake*`: after the human gate, intake re-runs once more to apply CHK-SCALE to the now-filled
sheet (≥3 `ENV-*` dims) and, if a uniform scale is applied, to re-run the datum fit under it
(`stl-re-intake-datum/SKILL.md:83`; `RE_SPEC.md:98-101`). Skip `intake*` only when the run is
scan-only (no calipers, `DECISIONS.md` has a `MEASUREMENTS` scan-only entry).

Run each stage by invoking its skill. Check the exit artefacts before moving on;
`init_run.py status` lists what is missing. A stage that cannot meet its exit criteria
does not hand off.

| Stage | Skill | Entry | Exit (all must exist and be non-empty) |
|---|---|---|---|
| intake | `stl-re-intake-datum` | `input/scan.stl` + `input/INPUT_HASHES.json` | `intake/INTAKE_CARD.md`, `intake.json`, `regime.json`, `MEASUREMENTS.md` (request), `alignment.json` with `#status == "OK"`, `work.stl`, `aligned_work.stl`; regime declared (§3); part class supported (§6); CHK-SCALE, CHK-ENUM, CHK-TILT run |
| human gate | you | intake exit | filled `input/MEASUREMENTS.md`, hashed via `init_run.py rehash` (O-2), **or** a `MEASUREMENTS` scan-only entry in `DECISIONS.md` (§6); a `REGIME` entry |
| intake* (re-run) | `stl-re-intake-datum` | human gate passed, calipers supplied | CHK-SCALE run against the filled sheet; `intake/scale.json`; `alignment.json` re-fit and re-exits `#status == "OK"` if a scale was applied |
| measure | `stl-re-measure-intent` | human gate passed (or `intake*` exit if calipers arrived) | `measure/params.json`, `measure/PARAM_TABLE.md` (rendered from JSON), `measure/figures/`; every param has `source` and `rule`; CHK-COUNT, CHK-ACHIEVABLE, CHK-CLUSTER, CHK-FRAME run |
| rebuild | `stl-re-rebuild-build123d` | measure exit | `build/MODELING_PLAN.md`, `model.py`, `build_log.txt`, `<part>_datum.step`, `<part>.step`, `<part>_cad.stl`, `export_check.json` showing one valid closed solid in both frames; CHK-FILLET, CHK-PATCHWORK run |
| verify | `stl-re-verify` (fresh context, §5) | rebuild exit | `qa/gate.json` (with `regime`, `checks`, `verdict`, and `errors: []` / `verdict` in `allowed_verdicts` — §4), `qa/VERDICT.md`, `qa/masks.json`, `qa/overlays/` |
| deliver | `stl-re-deliver` | `qa/VERDICT.md` exists, verdict deliverable (§4) | `deliver/README.md`, `deliver/MANIFEST.json`, `deliver/repro.json` |

Per feature: 3 `REVISE` verdicts on the same feature (across verify loops) → HALT
(`RE_SPEC.md:248-249`). The rebuild skill also stops after 3 failed build attempts on one
feature inside a single iteration and reports a plan mismatch
(`stl-re-rebuild-build123d/SKILL.md:248-250`) — a heuristic with no golden precedent, and
distinct from the per-feature REVISE count above. Neither kind of rebuild-internal retry
counts as a loop; a loop is a post-verify REVISE (`RE_SPEC.md:250`).

## 3. Declare the band regime at intake (no silent default)

The owner decision is binding: the intake declares the regime, the verdict names it, and
there is no silent default (`QUESTIONS.md` A/Q1; `references/run-contract.md` §9).

1. Present the options to the user and ask which applies:

   | Regime | Bands | Source | Goldens that used it |
   |---|---|---|---|
   | `RE_SPEC` | Tier-1 \|CAD − caliper\| ≤ 0.15 mm per calipered dim; Tier-2 whole-part skin p95 ≤ 1.6 / max ≤ 4.0 mm after independent ICP + skin mask; named interfaces not covered by calipers max ≤ 0.8 mm | `baseline/oomwoo-re-pipeline/RE_SPEC.md:170,174,175` | OOM-B02, OOM-P03 (both with calipers) |
   | `baseline-skill` | p95 ≤ 0.30 / max ≤ 0.80 mm (consumer plastic); p95 ≤ 0.15 / max ≤ 0.50 mm (machined). Source not stated in that file | `baseline/skills/stl2step-build123d/SKILL.md:87` | dreame_brush-caps, OD-H12 (both scan-only) |
   | `project-spec` | the numbers in the user's spec, cited by path | the user's file | M02-02-03 (`OPERATOR_SPEC.json`) |

2. Record it in `DECISIONS.md` (`REGIME`, who chose, why) and in `INTAKE_CARD.md`; the
   intake skill also writes it to `intake/regime.json` (via
   `stl-re-intake-datum/scripts/intake.py regime`) with the same shape as
   `qa/gate.json#regime` (`references/run-contract.md` §6, §12). If the user says "you
   pick", record "delegated to agent" plus your reason. That is declared, not silent.
3. Never change the regime after seeing gate numbers to turn a miss into a pass. A missed
   band is reported, never loosened (`analysis/SYNTHESIS.md` F1). A later regime change
   needs a new `REGIME` entry and a re-verify of the current iteration; report both results.
   It is legitimate only for a reason independent of the gate numbers (e.g. calipers arrived
   after a scan-only run, or the user now supplies a spec) — never because the first regime's
   numbers failed. The `REGIME` entry names that reason, and the verdict reports the result
   under both regimes so the switch is auditable (`analysis/SYNTHESIS.md` F1;
   `references/verdict-examples.md:73` forbids a post-hoc OD-style switch).
4. The datum audit (≤ 0.3° / ≤ 0.15 mm, `RE_SPEC.md:241`) is report-only, and face count
   / surface census are reported, not gated (`QUESTIONS.md` A/Q2, Q3). Neither blocks a verdict.

## 4. Verdicts and what you do next

Only `stl-re-verify` writes a verdict (`qa/gate.json#verdict`). Vocabulary is fixed
(`references/run-contract.md` §7).

**Act on a verdict only if `qa/gate.json#errors` is empty and, when `allowed_verdicts` is
present, the verdict is a member of it.** Verify writes `gate.json` with the refused
verdict and its `errors` even when `assemble` exits non-zero, so a naive reader that only
checks `#verdict` would act on a rejected result (O-1; `stl-re-verify/scripts/verdict.py`
writes `verdict: null` plus `errors: [...]` on refusal). `init_run.py status` already
applies this rule and reports a finding instead of a verdict when the gate was refused;
otherwise send the run back to verify to re-run `assemble`.

| Verdict | Your action |
|---|---|
| `APPROVED` | Go to deliver. |
| `APPROVED_WITH_LIMITATIONS` | Go to deliver. Check each limitation has a re-run trigger (e.g. "one caliper reading on F01 should trigger a re-run", `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:30`). If one lacks a trigger, send it back to verify to add one. |
| `BAND_NOT_MET` | Show the user the missed band with its number, the per-region explanation and the options from `VERDICT.md`: (a) accept for delivery — record `ACCEPT-BAND` in `DECISIONS.md` (who, date, which band, the number), no entry → no `deliver/`; (b) REVISE if a geometric or measurement cause is named and loops remain — append an `OTHER` `DECISIONS.md` entry recording who chose REVISE and why, then ask verify to re-run `verdict.py assemble` with `review.json#verdict = "REVISE"` (a band fail is allowed to become REVISE, `stl-re-verify/SKILL.md:227`), then run `supersede --route <...>` as below (no script change needed: `supersede` already only requires verdict `REVISE`); (c) supply calipers/photos and re-run; (d) HALT. |
| `REVISE` | If iteration < 3: `python3 scripts/init_run.py supersede <run> --route {measure,geometry,datum}` (CHK-SUPERSEDED), then route by finding (below). If iteration = 3: the script exits 3 → HALT. |
| `HALT` | Stop. Append a `HALT` entry to `DECISIONS.md` (reason, evidence path, options). Do not create `deliver/`. Resume only on a human decision. |

**Route a REVISE to the stage that owns the cause** (every golden REVISE began in intake
or measurement, not CAD code: `analysis/SKILL_ARCHITECTURE.md` §1). `--route` is required
and decides what `supersede` carries forward into the new iteration (O-7): `measure` and
`datum` carry nothing (the stage being redone is the one that was wrong, so its old output
must not masquerade as done); `geometry` carries `measure/` and `build/MODELING_PLAN.md` +
`build/model.py` forward as a diffable base. `--route datum` additionally moves `intake/`
into `_itN_SUPERSEDED/` (never edited in place — the same loss CHK-SUPERSEDED prevents for
`measure/build/qa`, `stl-re-intake-datum/SKILL.md:245-246`).

| Finding | `--route` | Re-enter at | Golden precedent |
|---|---|---|---|
| Missing feature, dismissed cluster (CHK-ENUM, CHK-CLUSTER) | `datum` | intake (feature enumeration), then measure | P03 it1 stem: `golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/PARAM_TABLE.md:4`, `VERDICT.md:8,41` |
| Caliper reading not achievable / misattributed (CHK-ACHIEVABLE) | `measure` | measure | B02 it1 F06 Δ +0.647: `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md` §2, §6 |
| Wrong count (CHK-COUNT) | `measure` | measure | M02 27T candidate: `golden-examples/M02-02-03_watertight-design-intent/DESIGN_NOTES.md:5` |
| Geometry, fillet, patchwork (CHK-FILLET, CHK-PATCHWORK) | `geometry` | rebuild | `analysis/SYNTHESIS.md` §2 |

Change only what the finding requires and record it (B02 it2 changed exactly one
parameter: `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/_it1_SUPERSEDED/` vs
`build_OOM-B02.py`). Each re-verify uses the same gate protocol as the one before, or it
states that the comparison is not like-for-like (CHK-LIKE4LIKE; B02 `VERDICT.md` §6).

## 5. Independence (CHK-INDEP)

1. Run `stl-re-verify` in a fresh agent/context that did not build the model (e.g. a
   subagent). Give it only: the run folder path; `input/` (scan, MEASUREMENTS, photos,
   `INPUT_HASHES.json`); `intake/INTAKE_CARD.md` (regime, named interfaces),
   `intake/alignment.json`, `intake/regime.json` (verify stops without it,
   `stl-re-verify/SKILL.md:33-37`); `build/*.step`, `build/export_check.json` (CHK-FILLET
   needs it), `build/MODELING_PLAN.md`. `build/model.py` may be **read-only grepped** for
   CHK-PATCHWORK (checking for `loft(ruled=True)` or a polyline stack,
   `stl-re-verify/SKILL.md:96-97`) and must never be imported, executed, or used as a
   source of "expected" values (`stl-re-verify/SKILL.md:14`). Do not pass it the build log,
   `measure/params.json` values as expectations, or your conversation. It uses its own
   code (`analysis/SYNTHESIS.md` E16; facet-film T18).
2. If you cannot start a fresh context, run verify anyway and declare it: append an
   `INDEP` entry to `DECISIONS.md`; verify sets `checks.CHK-INDEP.result = "finding"` and
   writes an honesty note in `VERDICT.md` (precedent wording: "This is not an
   organisationally independent verification", `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md` §7).
3. A validator whose expected values came from the same scan is a consistency check, not
   independent evidence (CHK-CIRCULAR; `golden-examples/OD-H12_delonghi-dedica-pump/README.md:70`).

## 6. HALT / ask table

| Situation | Action | Evidence |
|---|---|---|
| Missing deps or sibling skills | HALT at §0 | `RE_SPEC.md:364-373` |
| No calipers supplied | Ask for the intake's measurement request to be filled. If the user declines, proceed scan-only only with a `MEASUREMENTS` entry in `DECISIONS.md`, and carry these limitations to the verdict: "Tier-1 not run" and "absolute scale not caliper-verified", each with its re-run trigger | B02 proceed-without + limitations 1-2 (`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:22-27`; `baseline/oomwoo-re-pipeline/TRACKER.md:13`); OD scale assumed (`golden-examples/OD-H12_delonghi-dedica-pump/README.md` "Varsayımlar ve sınırlar"); DRM no calipers (`golden-examples/dreame_brush-caps/README.md:81`) |
| Photo-transcribed readings only | Accept with photo ids and ±0.1 mm effective uncertainty; declare it | `analysis/SYNTHESIS.md` §4, C5 |
| Sheet metal part | HALT and ask: no golden evidence for a method | `analysis/SYNTHESIS.md` §6 |
| Freeform/styled surface with no analytic intent | HALT and ask | `analysis/SYNTHESIS.md` §6 |
| Multi-body STEP deliverable | HALT and ask; a single fused solid is supported, and every invented connector is declared | `analysis/SYNTHESIS.md` §6; `golden-examples/OD-H12_delonghi-dedica-pump/README.md:66-67` (multi-body STEP is "a separate job") |
| Band missed | `BAND_NOT_MET` → recorded human acceptance before deliver (§4) | OD-H12, DRM snap (`references/verdict-examples.md`) |
| REVISE at loop 3 | HALT | `RE_SPEC.md:250` |
| Same feature fails 3 times in rebuild | HALT with images and options | `RE_SPEC.md:248-249` |
| Input hash changed (`status` finding) | HALT: evidence was modified | `analysis/SYNTHESIS.md` A1; facet-film T4 |
| Datum `STOP` from `align.py` (no clean datum region) | Ask the user for a cleaner region, or HALT if none exists | `stl-re-intake-datum/SKILL.md:279` |
| `scan_resolution` is `decimated` or `unknown` at intake | Ask for the full-resolution scan before verify runs. If the user records that none exists (`DECISIONS.md` `OTHER`: "inspection-only, no full-res scan"), verify grades it as inspection-only: the verdict is at most `APPROVED_WITH_LIMITATIONS`, with the re-run trigger "full-res scan available". Plain `APPROVED` needs a full-res scan. Without that entry, do not grade; wait for the scan | `golden-examples/README.md` "What was left out"; `analysis/SKILL_ARCHITECTURE.md` verdict table (DRM screw, scan-only); `init_run.py init --scan-resolution`; DRM replay (`evals/replay/dreame_screw.md`) |
| CHK-SCALE applies a uniform `scale_factor ≠ 1` | Record an `OTHER` `DECISIONS.md` entry; only the datum-frame STEP is delivered, `export_frames.py` aborts on the scan-frame STEP | `references/run-contract.md` §11 |
| Filled `input/MEASUREMENTS.md` arrives after intake (calipers) | Re-run intake (`intake*`, §2) for CHK-SCALE before measure, not straight to measure | `stl-re-intake-datum/SKILL.md:83`; `RE_SPEC.md:98-101` |
| `deliver`'s `repro_check` fails | Send back to rebuild, then re-verify. `supersede` only accepts verdict `REVISE`, and a `repro_check` failure is not itself a verdict change, so move `qa/` and `build/` into a manually-named `_itN_SUPERSEDED/` yourself and record an `OTHER` `DECISIONS.md` entry before re-running rebuild; this does not count as a loop unless the STEP itself changes | `stl-re-deliver/SKILL.md:118-119` |
| Evidence conflicts you cannot resolve | Ask; do not pick a number | `analysis/SYNTHESIS.md` §0 (OPEN) |

## 7. CHK-PUBLISH and CHK-SUPERSEDED

- **CHK-PUBLISH:** nothing goes to `deliver/`, or to any user-facing location outside the
  run, before `qa/VERDICT.md` holds a deliverable verdict (plus `ACCEPT-BAND` for
  `BAND_NOT_MET`). Earned by B02 it1, "published to `4_STEP\` before the gate finished"
  (`baseline/oomwoo-re-pipeline/TRACKER.md:13`; `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/70_report.py:376`).
  If it happened: withdraw the files into the current `_itN_SUPERSEDED/`, add an `OTHER`
  entry to `DECISIONS.md`, and have the verdict mention it.
- **CHK-SUPERSEDED:** after every REVISE, move `measure/ build/ qa/` intact to
  `_itN_SUPERSEDED/` with `init_run.py supersede --route {measure,geometry,datum}` before
  changing anything (`--route datum` also moves `intake/`). What carries forward into the
  new iteration depends on the route, never a blanket default (`--no-carry` to start
  clean regardless): `measure` and `datum` carry nothing, since the stage the finding
  routed to is the one being redone; `geometry` copies `measure/` and
  `build/MODELING_PLAN.md` + `build/model.py` forward so the next iteration is a diffable
  edit (§4). Never overwrite a verdict in place. Earned by P03, whose
  it1 verdict was overwritten (`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:6`,
  "it2, overwritten in place"); B02 kept `_it1_SUPERSEDED/` and could prove a
  one-parameter diff.

## 8. Report to the user

At every stop (deliver done, BAND_NOT_MET awaiting acceptance, HALT) tell the user: the
regime and its source, the verdict word, the numbers as read from `qa/gate.json` (never
retyped: CHK-NUMBERS), the declared limitations with re-run triggers, the loop count
(n of 3), and whether verify was independent. Never call a masked, circular or partial
pass a clean pass (`analysis/SYNTHESIS.md` §0.1).

## References

- `references/run-contract.md`: folder layout, JSON keys, verdicts, check ids. Read first.
- `references/verdict-examples.md`: the six golden outcomes as worked verdicts. Read when
  deciding what a verdict means or how to word a limitation or band miss.
- `scripts/init_run.py`: `init`, `status`, `supersede`, `doctor`, `--selftest`.
