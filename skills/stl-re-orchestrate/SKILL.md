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
  missing calipers). Continue at the first incomplete stage. Artefacts are the state:
  never trust a remembered state over the folder.
- Official deviation gates run on the full-resolution scan. A decimated scan is for
  inspection only; never grade a part on it (`golden-examples/README.md` "What was left
  out"; `analysis/SYNTHESIS.md` A3).
- Every human decision goes into `<run>/DECISIONS.md` (append-only, format in the file):
  regime, calipers/scan-only, part class, band acceptance, HALT, independence.

## 2. Stage machine

```
init → intake → [human: MEASUREMENTS + REGIME] → measure → rebuild → verify ─┬─ APPROVED / APPROVED_WITH_LIMITATIONS ──→ deliver
                                                                              ├─ BAND_NOT_MET ─ [human: ACCEPT-BAND] ─→ deliver
                                                   ▲                          ├─ REVISE (loop < 3) ─ supersede ─┐
                                                   └──── route by finding ◄───┘                                │
                                                                              └─ HALT (or REVISE at loop 3) → stop, ask human
```

Run each stage by invoking its skill. Check the exit artefacts before moving on;
`init_run.py status` lists what is missing. A stage that cannot meet its exit criteria
does not hand off.

| Stage | Skill | Entry | Exit (all must exist and be non-empty) |
|---|---|---|---|
| intake | `stl-re-intake-datum` | `input/scan.stl` + `input/INPUT_HASHES.json` | `intake/INTAKE_CARD.md`, `intake.json`, `MEASUREMENTS.md` (request), `alignment.json`, `work.stl`, `aligned_work.stl`; regime declared (§3); part class supported (§6); CHK-SCALE, CHK-ENUM, CHK-TILT run |
| human gate | you | intake exit | filled `input/MEASUREMENTS.md`, **or** a `MEASUREMENTS` scan-only entry in `DECISIONS.md` (§6); a `REGIME` entry |
| measure | `stl-re-measure-intent` | human gate passed | `measure/params.json`, `measure/PARAM_TABLE.md` (rendered from JSON), `measure/figures/`; every param has `source` and `rule`; CHK-COUNT, CHK-ACHIEVABLE, CHK-CLUSTER, CHK-FRAME run |
| rebuild | `stl-re-rebuild-build123d` | measure exit | `build/MODELING_PLAN.md`, `model.py`, `build_log.txt`, `<part>_datum.step`, `<part>.step`, `<part>_cad.stl`, `export_check.json` showing one valid closed solid in both frames; CHK-FILLET, CHK-PATCHWORK run |
| verify | `stl-re-verify` (fresh context, §5) | rebuild exit | `qa/gate.json` (with `regime`, `checks`, `verdict`), `qa/VERDICT.md`, `qa/masks.json`, `qa/overlays/` |
| deliver | `stl-re-deliver` | `qa/VERDICT.md` exists, verdict deliverable (§4) | `deliver/README.md`, `deliver/MANIFEST.json`, `deliver/repro.json` |

Inside rebuild, a feature that fails 3 times → HALT to the human with the images and
options (`baseline/oomwoo-re-pipeline/RE_SPEC.md:248-249`). Rebuild-internal retries do
not count as loops; a loop is a post-verify REVISE (`RE_SPEC.md:250`).

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
4. The datum audit (≤ 0.3° / ≤ 0.15 mm, `RE_SPEC.md:241`) is report-only, and face count
   / surface census are reported, not gated (`QUESTIONS.md` A/Q2, Q3). Neither blocks a verdict.

## 4. Verdicts and what you do next

Only `stl-re-verify` writes a verdict (`qa/gate.json#verdict`). Vocabulary is fixed
(`references/run-contract.md` §7):

| Verdict | Your action |
|---|---|
| `APPROVED` | Go to deliver. |
| `APPROVED_WITH_LIMITATIONS` | Go to deliver. Check each limitation has a re-run trigger (e.g. "one caliper reading on F01 should trigger a re-run", `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:30`). If one lacks a trigger, send it back to verify to add one. |
| `BAND_NOT_MET` | Show the user the missed band with its number, the per-region explanation and the options from `VERDICT.md`: (a) accept for delivery, (b) REVISE if a geometric cause is named and loops remain, (c) supply calipers/photos and re-run, (d) HALT. Deliver only after an `ACCEPT-BAND` entry in `DECISIONS.md` (who, date, which band, the number). No entry → no `deliver/`. |
| `REVISE` | If iteration < 3: `python3 scripts/init_run.py supersede <run>` (CHK-SUPERSEDED), then route by finding (below). If iteration = 3: the script exits 3 → HALT. |
| `HALT` | Stop. Append a `HALT` entry to `DECISIONS.md` (reason, evidence path, options). Do not create `deliver/`. Resume only on a human decision. |

**Route a REVISE to the stage that owns the cause** (every golden REVISE began in intake
or measurement, not CAD code: `analysis/SKILL_ARCHITECTURE.md` §1):

| Finding | Re-enter at | Golden precedent |
|---|---|---|
| Missing feature, dismissed cluster (CHK-ENUM, CHK-CLUSTER) | intake (feature enumeration), then measure | P03 it1 stem: `golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/PARAM_TABLE.md:4`, `VERDICT.md:8,41` |
| Caliper reading not achievable / misattributed (CHK-ACHIEVABLE) | measure | B02 it1 F06 Δ +0.647: `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md` §2, §6 |
| Wrong count (CHK-COUNT) | measure | M02 27T candidate: `golden-examples/M02-02-03_watertight-design-intent/DESIGN_NOTES.md:5` |
| Geometry, fillet, patchwork (CHK-FILLET, CHK-PATCHWORK) | rebuild | `analysis/SYNTHESIS.md` §2 |

Change only what the finding requires and record it (B02 it2 changed exactly one
parameter: `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/_it1_SUPERSEDED/` vs
`build_OOM-B02.py`). Each re-verify uses the same gate protocol as the one before, or it
states that the comparison is not like-for-like (CHK-LIKE4LIKE; B02 `VERDICT.md` §6).

## 5. Independence (CHK-INDEP)

1. Run `stl-re-verify` in a fresh agent/context that did not build the model (e.g. a
   subagent). Give it only: the run folder path, `input/` (scan, MEASUREMENTS, photos),
   `intake/INTAKE_CARD.md` (regime, named interfaces), `intake/alignment.json` and
   `build/*.step`. Do not pass it `build/model.py`, the build log or your conversation.
   It uses its own code (`analysis/SYNTHESIS.md` E16; facet-film T18).
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
| Multi-body STEP deliverable | HALT and ask; a single fused solid is supported, and every invented connector is declared | `analysis/SYNTHESIS.md` §6; `golden-examples/OD-H12_delonghi-dedica-pump/README.md:67-68` (multi-body STEP is "a separate job") |
| Band missed | `BAND_NOT_MET` → recorded human acceptance before deliver (§4) | OD-H12, DRM snap (`references/verdict-examples.md`) |
| REVISE at loop 3 | HALT | `RE_SPEC.md:250` |
| Same feature fails 3 times in rebuild | HALT with images and options | `RE_SPEC.md:248-249` |
| Input hash changed (`status` finding) | HALT: evidence was modified | `analysis/SYNTHESIS.md` A1; facet-film T4 |
| Evidence conflicts you cannot resolve | Ask; do not pick a number | `analysis/SYNTHESIS.md` §0 (OPEN) |

## 7. CHK-PUBLISH and CHK-SUPERSEDED

- **CHK-PUBLISH:** nothing goes to `deliver/`, or to any user-facing location outside the
  run, before `qa/VERDICT.md` holds a deliverable verdict (plus `ACCEPT-BAND` for
  `BAND_NOT_MET`). Earned by B02 it1, "published to `4_STEP\` before the gate finished"
  (`baseline/oomwoo-re-pipeline/TRACKER.md:13`; `golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/70_report.py:376`).
  If it happened: withdraw the files into the current `_itN_SUPERSEDED/`, add an `OTHER`
  entry to `DECISIONS.md`, and have the verdict mention it.
- **CHK-SUPERSEDED:** after every REVISE, move `measure/ build/ qa/` intact to
  `_itN_SUPERSEDED/` with `init_run.py supersede` before changing anything. It copies
  `measure/` and `build/model.py` forward so the next iteration is a diffable edit
  (`--no-carry` to start clean). Never overwrite a verdict in place. Earned by P03, whose
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
