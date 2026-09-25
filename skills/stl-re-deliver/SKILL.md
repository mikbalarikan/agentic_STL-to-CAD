---
name: stl-re-deliver
description: Packages a verified STL→CAD (STEP) reverse-engineering run. Renders README.md from the gate and parameter JSON, writes MANIFEST.json with sha256 and roles, and re-runs the build in fresh processes. Use only after stl-re-verify has written qa/VERDICT.md and qa/gate.json, when asked to deliver, package, document or hand off the result.
---

# stl-re-deliver

Turn a verified run into a delivery: `deliver/README.md`, `deliver/MANIFEST.json`,
`deliver/repro.json`. This skill does not change geometry, gates or verdicts. It reads them
and refuses when they are missing, inconsistent or not deliverable.

Read `../stl-re-orchestrate/references/run-contract.md` first. It defines the folder
layout, the JSON keys, the verdicts, `DECISIONS.md` and the check ids used below.

## Why this is a separate skill

- The verifier must not write the report. The report reads its numbers from the gate JSON,
  and nothing is published before the verdict (`analysis/SKILL_ARCHITECTURE.md` §1).
- Every scan-gated golden except the DRM screw cap carried a limitation, a masked or
  circular gate, or a missed band (`analysis/SYNTHESIS.md` §0.1). The delivery has to carry
  those qualifiers. A pass/fail line cannot.

## Inputs and outputs

| Reads | Writes |
|---|---|
| `qa/gate.json`, `qa/VERDICT.md` (required, CHK-PUBLISH) | `deliver/limitations.json` (you write it, step 2) |
| `measure/params.json`, `build/export_check.json`, `intake/alignment.json`, `intake/regime.json` | `deliver/repro.json` (`scripts/repro_check.py`) |
| `build/model.py`, `build/*.step`, `input/INPUT_HASHES.json`, `DECISIONS.md` | `deliver/README.md` (`scripts/make_readme.py`) |
| `_itN_SUPERSEDED/` | `deliver/MANIFEST.json` (`scripts/make_manifest.py`, always last) |

Scripts live in `scripts/`. All take `--run <run folder>`. Exit 0 means done, 2 means
refused (the message names the check and the next action), and 1 means `repro_check.py`
found a non-reproducible build.

## Steps

### 0. Preflight: may this run be delivered?

```
python scripts/preflight.py --run <run>
```

It writes nothing. It runs:

| Check | Pass condition | Evidence |
|---|---|---|
| **CHK-PUBLISH** | `qa/VERDICT.md` and `qa/gate.json` exist, and the verdict is APPROVED, APPROVED_WITH_LIMITATIONS or BAND_NOT_MET | B02 it1 was "published to 4_STEP before the gate finished" (`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/70_report.py:376`) |
| **CHK-NUMBERS** (headline) | The first verdict word in `VERDICT.md` equals `gate.json#verdict` | B02 verdict prose drifted from its JSON (`.../6_RE_work/VERDICT.md:95-99`) |
| **ACCEPT-BAND** | Only for BAND_NOT_MET: `DECISIONS.md` has an `ACCEPT-BAND` entry, and its evidence path is a file inside the run | run-contract §7, §10; OD "operator approval required" (`golden-examples/OD-H12_delonghi-dedica-pump/README.md:62`); the DRM snap max miss has no recorded acceptance (`analysis/golden/dreame_brush-caps.md` Questions 1) |
| **CHK-SUPERSEDED** | `_it1…_itk_SUPERSEDED/` are numbered from 1 with no gaps, and each holds `qa/VERDICT.md`, `qa/gate.json` (verdict REVISE) and `build/model.py`. A missing STEP is a finding, not a failure. Iteration = k + 1 ≤ 3 | P03 it1 verdict "overwritten in place" (`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:6`); B02 kept `_it1_SUPERSEDED/`; 3 loops (`baseline/oomwoo-re-pipeline/RE_SPEC.md:248-250`) |
| inputs unchanged | Every file in `input/INPUT_HASHES.json` still has its sha256 | SYNTHESIS A1; evidence is never modified |
| hash freeze | Every `build/*.step` matches a sha256 in `gate.json#hash_frozen`, so the STEP you deliver is the one QA gated. If no STEP matches, that is a failure. If only some match, that is a finding. | (heuristic, n=1: M02) `golden-examples/M02-02-03_watertight-design-intent/VERDICT.md:6` |
| regime declared | `gate.json#regime.name` equals `intake/regime.json#name` (the canonical declaration, run-contract §12) | Owner decision Q1: the band regime is declared at intake and named in the verdict, never defaulted silently (`QUESTIONS.md` §A) |

### 1. Act on the verdict

| Verdict | Action |
|---|---|
| `APPROVED` | Continue. `limitations` must be empty. If VERDICT.md lists limitations, the verdict is wrong. Send it back to verify. |
| `APPROVED_WITH_LIMITATIONS` | Continue. Every limitation in VERDICT.md goes into `limitations.json` with a re-run trigger (SYNTHESIS F10). |
| `BAND_NOT_MET` | If there is no ACCEPT-BAND entry, **stop and ask the owner**. Show them the missed band with its number, the per-region explanation and the options, all read from `gate.json` and `VERDICT.md`. Write nothing to `deliver/`. Once an entry exists, continue. The README opens with a "band NOT met" banner and an acceptance section. |
| `REVISE`, `HALT` | Refuse. REVISE goes back to measure/rebuild. HALT goes to the orchestrator and a human. |

Never change a verdict, loosen a band, or edit `qa/` or `build/` from this skill
(`baseline/oomwoo-re-pipeline/RE_SPEC.md:181-183` honesty rule).

### 2. Write `deliver/limitations.json`

This is the only hand-written input. Its schema is in `references/readme-template.md`.
Take the content from `qa/VERDICT.md` and `measure/params.json`. Do not take it from memory.

- **Limitations:** one entry per risk, highest risk first. Each entry says what is missing,
  why, what the model holds instead, and the **re-run trigger**. Model it on B02's three
  limitations (`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:20-30`).
  Wording and anti-patterns are in `references/limitations-wording.md`.
- Always declare the following when they apply:
  - Tier-1 absent or partial (absent is not passed).
  - Absolute scale not caliper-verified (scan-only runs).
  - Every **masked pass**, with its unmasked number (CHK-MASK; B02 hex, `VERDICT.md:138-145`).
  - Every photo-inferred or assumed critical feature.
  - QA that was not independent (CHK-INDEP; B02 A13, `VERDICT.md:189-194`).
  - Circular validators, labelled as consistency checks (OD `README.md:70-71`).
- **Assumptions / invented geometry:** anything the model contains that was not measured.
  This includes connectors invented to make one solid (OD core tube). Params tagged
  `assumed`, `photo-inferred` or `standard` are listed automatically.
- **Claim boundary:** at least one "not fit for" line. Examples: "not fit for manufacture
  or tooling until F01 is calipered" (B02 `VERDICT.md:210`); "physical interchangeability
  and manufacturing release require mating-part or physical fit verification" (M02
  `README.md:31`). SYNTHESIS F7.
- **Numbers:** a literal decimal in any prose field fails CHK-NUMBERS. Cite values with
  placeholders, for example `{{gate:deviation.scan_to_cad.p95}}` or `{{params:hex_af.value}}`.

### 3. Reproducibility re-run

```
python scripts/repro_check.py --run <run> [--cmd python model.py] [--runs 2]
```

The script copies `build/` (without STEP or STL outputs), `measure/` and `intake/` (without
meshes) to a scratch folder. It runs the build in 2 fresh subprocesses and re-imports every
produced STEP whose name matches a delivered one. Then it compares solids, face count,
surface census, volume and bbox.

- The default tolerance is exact equality. The M02 rerun recorded
  `volume_abs_delta_mm3 0.0` and `bbox_max_abs_delta_mm 0.0`
  (`golden-examples/M02-02-03_watertight-design-intent/reproducibility_report.json`),
  (heuristic, n=1: M02).
- The raw sha256 is reported but not required, because STEP headers carry a timestamp
  (facet-film T32: two fresh processes, same geometric digest, env pinned;
  `analysis/baseline/facet-film-transferable.md`).
- If `build/model.py` does not write the STEPs itself (for example a separate export
  script), pass the full command with `--cmd`, and put the same command in
  `repro_commands`.

**On failure (exit 1):** do not deliver. Read `repro.json#runs[].stderr_tail`. The usual
causes are an unseeded random, a wall-clock value, a dict/set order, or an absolute path.
Loop back to `stl-re-rebuild-build123d`. That loop counts as a REVISE only if the geometry
changes. A tolerance other than 0 is a recorded parameter. Use one only with a
`DECISIONS.md` `OTHER` entry that says why.

### 4. Render the README

```
python scripts/make_readme.py --run <run>
```

The script refuses when:
- any required JSON is missing (the list is in Inputs and outputs);
- the verdict and the limitations disagree;
- a limitation has no trigger;
- the claim boundary is empty;
- a placeholder does not resolve;
- a literal decimal appears in prose;
- the reference photo is missing;
- `repro.json` is not reproducible.

The section list and the golden source of each section are in
`references/readme-template.md`.

Then **read the rendered README against `qa/VERDICT.md`** and check:
- [ ] Every limitation, masked pass, struck dimension and unmodelled region named in
      VERDICT.md appears in the README.
- [ ] Nothing says PASS where VERDICT.md says masked, partial, circular or NOT MET.
- [ ] The regime and its source are the ones in the verdict.
- [ ] Both frames are named. Origin and axes are stated in words.

If something is missing, fix `limitations.json` (or send it back to verify when the JSON
itself is wrong) and re-render. Never hand-edit `README.md`.

### 5. Manifest (last)

```
python scripts/make_manifest.py --run <run> [--exclude "GLOB=REASON" ...]
```

The manifest hashes every file under the run folder: bytes, sha256 and role. It follows
the golden `MANIFEST.json` shape (`golden-examples/*/MANIFEST.json`) and facet-film T35.

- Files can be excluded only with `--exclude GLOB=REASON`. They stay listed under
  `excluded` with bytes, sha256 and the reason, as in
  `golden-examples/dreame_brush-caps/MANIFEST.json`.
- Nothing disappears silently. `MANIFEST.json` does not list itself, and its `note` says so.
- It records the verdict, regime, iteration, acceptance and the preflight checks. It refuses
  if `README.md` or a reproducible `repro.json` is missing (definition of done, facet-film T36).
- If any role is `unclassified`, look at the file. It may be a stray intermediate that
  belongs in a stage folder.

### 6. Report to the user

Give the path to `deliver/README.md` and then state:
- the verdict word;
- the regime;
- the iteration (n of 3);
- the declared limitations with their triggers;
- whether verification was independent.

Quote numbers from the README. Do not retype them (CHK-NUMBERS). Never call a masked,
circular or partial pass a clean pass (`analysis/SYNTHESIS.md` §0.1).

## On failure (summary)

| Symptom | Cause | Do |
|---|---|---|
| CHK-PUBLISH fail | No verdict yet | Run stl-re-verify. Do not create `deliver/`. |
| CHK-NUMBERS headline mismatch | VERDICT.md and gate.json disagree | Send it back to verify. Do not edit either file. |
| ACCEPT-BAND stop | BAND_NOT_MET with no recorded acceptance | Ask the owner. Save their written answer in the run and append the `DECISIONS.md` line. |
| CHK-SUPERSEDED fail | An earlier iteration is lost or incomplete | Tell the user what is missing. Record `OTHER` in `DECISIONS.md` and name the gap as a limitation. Never fabricate the old files. |
| hash freeze fail | The STEP changed after QA | Re-run verify on the current STEP. |
| inputs changed | The evidence was modified | HALT (orchestrator §6). |
| regime mismatch | Verify applied a regime other than the declared one | Send it back to verify. |
| repro exit 1 | Non-deterministic build | Loop back to rebuild (step 3). |
| literal decimal / unresolved placeholder | Hand-typed number | Replace it with a placeholder that points at the JSON. |

## Test

`tests/run_fixture_test.py` copies `tests/fixture_run/` to a scratch folder. The fixture is
a synthetic plate with a bore: two iterations, APPROVED_WITH_LIMITATIONS. The script plays
the rebuild and verify outputs the fixture needs, then runs preflight, repro, README and
manifest. It also runs 8 refusal cases (one per check above, plus a missing re-run trigger
and a literal decimal), BAND_NOT_MET with an ACCEPT-BAND entry, and a non-deterministic
model. That is 21 assertions in total.

```
python tests/run_fixture_test.py            # needs build123d; prints N/N passed
```

## Open questions

- DRM snap: the golden delivery went out with `overall_pass: false` and no recorded
  acceptance (`QUESTIONS.md` §B). This skill will not reproduce that. Whether that
  delivery was accepted, and by whom, is still unknown.
- The exact-equality tolerance comes from one golden (M02) on one OCCT build. Across
  machines or OCCT versions, geometric digests may differ. No golden records such a
  cross-version run.
