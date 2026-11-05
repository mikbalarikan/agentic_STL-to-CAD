---
name: stl-re-orchestrate
description: Entry point for turning a scanned STL mesh into design-intent parametric CAD (STEP) with build123d, harness v1. Use when asked to convert a scan, STL or mesh into STEP/CAD, remodel a part from a 3D scan, or resume, re-run or check the status of such a job. Runs intake → measure → refine (staged deviation loop on a JSON feature tree) → build → verify → deliver with bounded iterations and honest verdicts.
---

# stl-re-orchestrate (harness v1)

You run the job as a state machine and do no geometry math yourself. Each stage is a sibling
skill. The folder is the state: never trust a remembered state over it.

- Paths and JSON keys are fixed in `references/run-contract.md`.
- Worked verdicts are in `references/verdict-examples.md`.
- The golden evidence behind each rule is cited in the v0 text,
  `harnesses/v0/skills/stl-re-orchestrate/SKILL.md`. The rules are the same; only the build
  stage changed.

## 0. Prerequisites

`python3 scripts/init_run.py doctor`. Exit 2 means a missing dependency or a missing sibling
skill. In that case HALT and report; never improvise a missing stage.

The siblings are:
- `stl-re-intake-datum`
- `stl-re-measure-intent`
- `stl-re-refine`
- `stl-re-build`
- `stl-re-verify`
- `stl-re-deliver`

Install a harness version with `tools/harness.py install v1`, which keeps only one version in
a skills folder. Load meshes only inside scripts and print summaries, never vertex dumps.

## 1. Start or resume

- **New job:**
  ```
  python3 scripts/init_run.py init <run> --part <name> --scan <scan.stl> \
      [--photos ...] [--measurements <filled sheet>] --scan-resolution full|decimated|unknown
  ```
- **Resume:** `python3 scripts/init_run.py status <run>`. Continue at the first incomplete
  stage.
- **Human decisions:** every one goes into `DECISIONS.md` (append-only). That covers REGIME,
  MEASUREMENTS, PART-CLASS, ACCEPT-BAND, HALT, INDEP, and card answers (OTHER).
- **Decimated scan:** inspection only. It can reach `APPROVED_WITH_LIMITATIONS`, never plain
  `APPROVED`.

## 2. Stage machine

```
init → intake → [human: REGIME + calipers or scan-only] → intake* → measure → refine → build → verify
     → APPROVED / APPROVED_WITH_LIMITATIONS → deliver
     → BAND_NOT_MET → [human ACCEPT-BAND] → deliver
     → REVISE (loop < 3) → supersede --route {measure,geometry,datum} → re-enter
     → HALT, or REVISE at loop 3 → stop, ask
```

| Stage | Skill | Exit (all must exist) |
|---|---|---|
| intake | `stl-re-intake-datum` | `intake/INTAKE_CARD.md`, `intake.json`, `regime.json`, `MEASUREMENTS.md`, `alignment.json` with `status OK`, `work.stl`, `aligned_work.stl` |
| human gate | you | a REGIME entry; a filled `input/MEASUREMENTS.md` (registered with `init_run.py rehash`) or a MEASUREMENTS scan-only entry |
| measure | `stl-re-measure-intent` | `measure/params.json` (every value has `source` + `rule`), `PARAM_TABLE.md` |
| refine | `stl-re-build` (base tree) + `stl-re-refine` (loop) | `build/base_tree.json` (datum + dominant silhouette only), `refine/feature_tree.json`, `refine/refine_log.json` |
| build | `stl-re-build` | the reviewed `build/feature_tree.json`, `tree_log.json` with status OK, `fillets.json`, both STEPs, `export_check.json` with one valid closed solid |
| verify | `stl-re-verify`, in a **fresh context** | `qa/gate.json`, `VERDICT.md`, `masks.json` |
| deliver | `stl-re-deliver` | `deliver/README.md`, `MANIFEST.json`, `repro.json`, the delivery zip |

After deliver, or after a HALT, run `python3 scripts/run_metrics.py <run>`. It writes
`run_metrics.json` for the benchmark.

**Review between refine and build.** This is your job; the loop does not do it.
1. Read `refine_log.json`:
   - the accepted nodes;
   - the open points;
   - the blend candidates;
   - the cards.
2. Copy `refine/feature_tree.json` to `build/feature_tree.json`, and the loop's values to
   `measure/params_refine.json`.
3. Remove any node that is a patch rather than a design feature. Its cluster becomes an open
   point.
4. Add the fillets from the blend candidates as the last nodes, with radii from
   `stl-re-measure-intent`.

Record each removal or addition as an OTHER line in `DECISIONS.md`.

**Cards.**
- `--arbiter auto` answers ties by lower J, and answers low-gain cards with "open point".
- To decide yourself, run refine with `--arbiter agent`, answer with
  `stl-re-refine/scripts/cards.py`, then re-run the loop.
- A user who wants to steer (guided mode) answers the same cards.

## 3. Regime: declared at intake, never defaulted

Present the options and ask:

| Regime | Bands | Source |
|---|---|---|
| `RE_SPEC` | Tier-1 \|CAD − caliper\| ≤ 0.15; Tier-2 p95 ≤ 1.6 / max ≤ 4.0; interfaces ≤ 0.8 | `baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175` |
| `baseline-skill` | plastic p95 ≤ 0.30 / max ≤ 0.80; machined p95 ≤ 0.15 / max ≤ 0.50 | `baseline/skills/stl2step-build123d/SKILL.md:87` |
| `project-spec` | the user's numbers, cited by path | the user's file |

- Record the choice in `DECISIONS.md` and in `intake/regime.json`.
- "You pick" means "delegated to agent" plus your reason.
- Never change the regime after seeing gate numbers. A later change needs a reason that has
  nothing to do with the numbers, plus a re-verify, and the result is reported under both
  regimes.
- The datum audit and the face count are reported, never gated.

## 4. Verdicts

Act on a verdict only when `qa/gate.json#errors` is empty and the verdict is in
`allowed_verdicts`.

| Verdict | Action |
|---|---|
| `APPROVED` | deliver |
| `APPROVED_WITH_LIMITATIONS` | deliver. Each limitation needs a re-run trigger. |
| `BAND_NOT_MET` | Show the miss per region and the options. **ACCEPT-BAND** must meet all three rules, or deliver refuses: (1) the evidence file is outside the stage folders, e.g. `decisions/`; (2) it cites the first 12 hex characters of `qa/gate.json`'s sha256; (3) it names one entry of `gate.json#band_fails`. |
| `REVISE` | `init_run.py supersede <run> --route …` (CHK-SUPERSEDED), then re-enter the stage that owns the cause. At loop 3, HALT. |
| `HALT` | Stop. Write a HALT entry with the reason, the evidence and the options. |

Route a REVISE by the finding:

| Finding | Route |
|---|---|
| missing feature or dismissed cluster | `datum` |
| caliper not achievable, or wrong count | `measure` |
| geometry, fillet, patchwork | `geometry`: carries `measure/`, `base_tree.json` and `feature_tree.json` forward; re-run refine or build from there |

## 5. Independence (CHK-INDEP)

Run `stl-re-verify` in a fresh agent context.
- **Give it only:**
  - the run folder;
  - `input/`;
  - `intake/INTAKE_CARD.md`, `alignment.json` and `regime.json`;
  - `build/*.step`, `export_check.json` and `feature_tree.json` (read-only, for the
    patchwork census).
- **Never give it:** the refine metrics or your conversation.
- **If no fresh context is possible:** add an INDEP entry to `DECISIONS.md`. Verify then sets
  CHK-INDEP to `finding`.

## 6. HALT / ask

| Situation | Action |
|---|---|
| Missing deps or siblings | HALT |
| No calipers | Ask. Scan-only needs a MEASUREMENTS entry and carries "Tier-1 not run" and "scale not caliper-verified" as limitations. |
| Sheet metal, freeform/styled surface, multi-body deliverable | HALT and ask. There is no supported strategy (see the v1 README, v2 candidates). |
| Refine card waiting (`--arbiter agent`) | Answer it, or ask the user |
| Band missed | `BAND_NOT_MET`, then a recorded human acceptance |
| REVISE at loop 3; the same feature fails 3 times | HALT |
| Input hash changed | HALT |
