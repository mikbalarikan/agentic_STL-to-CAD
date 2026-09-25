# Run contract (shared by all `stl-re-*` skills)

This file is the single source of the hand-off contract. Every `stl-re-*` skill reads
and writes these paths and keys. A skill may add keys; it may not rename or drop them.
Evidence: `analysis/SKILL_ARCHITECTURE.md` §3–§4, `analysis/SYNTHESIS.md`.

## 1. Folder layout

```
<run>/
  DECISIONS.md      append-only log of human decisions (§10)
  input/            scan.stl (never modified), photos/, MEASUREMENTS.md (filled by a human), INPUT_HASHES.json
  intake/           INTAKE_CARD.md, intake.json, regime.json (§12), coverage.json, MEASUREMENTS.md (request),
                     alignment.json, work.stl, aligned_work.stl
  measure/          params.json, PARAM_TABLE.md, figures/
  build/            MODELING_PLAN.md, model.py, build_log.txt, <part>_datum.step, <part>.step, <part>_cad.stl,
                     export_check.json, fillets.json, face_stats.json
  qa/               gate.json, regime.json (copy of intake/regime.json, §12), review.json, VERDICT.md,
                     masks.json, overlays/
  deliver/          README.md, MANIFEST.json, repro.json          (only after qa/VERDICT.md exists)
  _itN_SUPERSEDED/  the previous iteration's measure/ build/ qa/ (and intake/ for a --route datum REVISE,
                     §10), moved intact
```

The six skills are installed side by side (`~/.claude/skills/stl-re-*`). A skill may call
a sibling's script by the relative path `../stl-re-<name>/scripts/<file>.py`.

## 2. Common JSON header

Every JSON written by a script carries:

```json
{"schema": "stl-re/<file>@1", "tool": "<script name>", "tool_version": "<skill version>",
 "inputs": {"<path>": "<sha256>"}, "seed": 0, "created": "<ISO-8601, provenance only>"}
```

`created` is the only wall-clock value. It never feeds a computation, and the
determinism check (identical outputs from two fresh processes) ignores it.

## 3. `intake/alignment.json`

RE_SPEC schema v2 (`baseline/oomwoo-re-pipeline/RE_SPEC.md:143-157`) plus the fields the
goldens needed:

```json
{
  "matrix_4x4": [[...],[...],[...],[...]],      // row-major, raw scan -> datum frame
  "scale_factor": 1.0,                           // 1.0 unless CHK-SCALE applied ONE uniform scale
  "scan_noise_mm": {"value": 0.0, "method": "rms of RANSAC plane on <region>"},
  "primary":   {"type": "plane|axis", "mesh_region_desc": "", "fit_rms_mm": 0.0, "fit_max_mm": 0.0, "why": ""},
  "secondary": {"type": "axis|plane|symmetry|feature", "mesh_region_desc": "", "fit_rms_mm": 0.0, "fit_max_mm": 0.0, "why": ""},
  "clock":     {"rule": "", "angle_deg": 0.0},
  "tilt_deg":  {"value": 0.0, "method": ""},     // measured, never hard-coded (CHK-TILT)
  "origin":    {"definition": "<feature> ∩ <feature>"},
  "sanity_landmarks": [{"name": "", "expected": "", "observed": "", "ok": true}],
  "removed":   {"fragments_pct": 0.0, "table_pct": 0.0, "method": ""}
}
```

## 4. `measure/params.json`

```json
{"params": {"<name>": {
   "value": 0.0, "unit": "mm|deg|count",
   "measured": "<number, range or null>",
   "rule": "caliper-direct | round-within-noise | std-size-snap | symmetry | mean-of-n | keep-measured | photo-inferred | assumed",
   "source": "caliper | caliper-photo | operator-spec | scan | photo-inferred | standard | assumed",
   "estimator": "<how it was measured: point set, fit, percentile, stations>",
   "uncertainty_mm": 0.0,
   "evidence": "<path to figure / photo id / file:line>",
   "critical": false }}}
```

`PARAM_TABLE.md` is rendered from this file and never edited by hand.

## 5. `build/export_check.json`

For each of `datum` and `scan` frame: `solids`, `valid`, `closed`, `faces`,
`volume_mm3`, `area_mm2`, `bbox`, `surface_types` (count and area per type), and
`fillets` (every fillet/chamfer: target radius, used radius, OK/FAILED).

## 6. `qa/gate.json`

- `regime`: see §12 (canonical shape and file).
- `hash_frozen`: see §12 (canonical shape).
- `datum_audit`: `{"angle_deg", "origin_offset_mm", "point_disagreement_p95_mm", "reference_band": "≤0.3° / ≤0.15 mm (RE_SPEC.md:241)", "blocking": false}`.
- `validity`, `surface_census`: reported only.
- `tier1`: per-dim `{caliper, cad, delta, pass}`.
- `deviation`:
  - `{"registration": {"method", "iterations", "converged", "delta_deg", "delta_mm"}, "scan_to_cad": stats, "cad_to_scan": stats, "cad_to_scan_observable": stats, "unobservable_fraction", "zones": {...}, "masks": [{"name", "why", "fraction", "stats_inside"}], "unmasked": stats, "sensitivity": [...], "over_band_clusters": [...]}`
  - `stats` = `{n, rms, p50, p95, p99, max}` in mm, plus the sampling and seed.
  - `scan` names the file used; `full_res: true|false`.
- `checks`: `{"CHK-...": {"ran": true, "result": "pass|finding|fail", "note": ""}}`.
- `verdict`: one of §7, or `null` when `assemble` refused to produce one.
- `errors`: list of strings, non-empty exactly when `assemble` exited non-zero (a refused
  verdict). `allowed_verdicts`, when present, lists the verdict words the refusal still
  permits (e.g. a band fail may still become `REVISE`, `stl-re-verify/SKILL.md:262`).
  **A verdict is trustworthy only if `errors` is empty and, when `allowed_verdicts` is
  present, `verdict` is a member of it (O-1).** `stl-re-verify/scripts/verdict.py` writes
  `gate.json` with the refused verdict and its `errors` before returning a non-zero exit, so
  a reader that checks only `#verdict` would act on a rejected result; every consumer
  (`init_run.py status`, deliver's preflight, this SKILL's §4) must check `errors` and
  `allowed_verdicts` before treating `verdict` as final.

## 7. Verdict vocabulary

| Verdict | Meaning |
|---|---|
| `APPROVED` | Every gate in the declared regime passes with no mask-dependent passes. |
| `APPROVED_WITH_LIMITATIONS` | Gates pass; declared limitations exist, each with a re-run trigger. |
| `BAND_NOT_MET` | A band is missed; explained per region with options. Delivery needs a recorded human acceptance. |
| `REVISE` | Fixable in measurement or geometry. Loop back; counts toward the 3-loop limit. |
| `HALT` | 3 loops used, an unsupported part class, or a blocker only a human can clear. |

## 8. Named checks (ids are fixed)

CHK-SCALE, CHK-ENUM, CHK-CLUSTER, CHK-TILT, CHK-FRAME, CHK-CIRCULAR, CHK-COUNT,
CHK-ACHIEVABLE, CHK-FILLET, CHK-PATCHWORK, CHK-MASK, CHK-OVERLAY, CHK-SUPERSEDED,
CHK-PUBLISH, CHK-LIKE4LIKE, CHK-NUMBERS, CHK-INDEP. Definitions and evidence:
`analysis/SYNTHESIS.md` §2.

## 9. Owner decisions that bind the skills (2026-09-25)

- The band regime is declared at intake and named in the verdict. There is no silent default.
- The datum audit is **report-only**.
- The face count and surface census are **reported, not gated**. The rules against ruled
  lofts and polyline stacks still apply.

## 10. Clarifications added by `stl-re-orchestrate` (additions only; nothing above renamed)

- **`<run>/DECISIONS.md`** (run root, created by `scripts/init_run.py init`): append-only
  log of human decisions, one line each:
  `- <date> | <who> | <id> | <decision> | <evidence path>`, where `<id>` is one of
  `REGIME`, `MEASUREMENTS`, `PART-CLASS`, `ACCEPT-BAND`, `HALT`, `INDEP`, `OTHER`.
  A `BAND_NOT_MET` result reaches `deliver/` only with an `ACCEPT-BAND` entry.
- **`input/INPUT_HASHES.json`** carries the §2 header plus `part` (the `<part>` name used
  in `build/`), `scan_resolution` (`full | decimated | unknown`) and `files`
  (`[{path, role, sha256, bytes, source, mode}]`). Input files are copied read-only
  (or symlinked with `--link`). Verify can check `inputs` to prove that the evidence
  is unchanged. A filled `input/MEASUREMENTS.md` handed to the human gate after `init` is
  not covered by this file until it is registered: run `init_run.py rehash <run>
  [--measurements <file>]` to place/hash it into `INPUT_HASHES.json#inputs` (O-2). Until
  then, `status` reports a finding that the sheet is un-hashed; once hashed, a later edit
  is caught the same way any other tampered input is.
- ~~**`intake/intake.json#regime`**: the regime declared at intake, the same shape as
  `qa/gate.json#regime`. Verify copies it and does not choose its own.~~ **Superseded by
  §12: the regime lives at `intake/regime.json`, not `intake/intake.json#regime`.**
- **`deliver/` is not created by init.** Its existence before a deliverable verdict is a
  CHK-PUBLISH finding (`init_run.py status` reports it).
- **Iteration number** = number of `_itN_SUPERSEDED/` folders that were a REVISE loop, plus
  1 (a `--route repro` folder, below, is excluded from this count). `init_run.py supersede`
  requires `--route {measure,geometry,datum,repro}` (O-7): the route names the stage the
  REVISE is re-entering and decides what carries forward, so a wrong stage is never masked as
  already complete. For `measure`/`geometry`/`datum` it moves `measure/ build/ qa/` into
  `_itN_SUPERSEDED/` (also `intake/` for `--route datum`), then, unless `--no-carry`, copies
  forward only what that route says: `measure` and `datum` carry nothing (the stage being
  redone must not look done); `geometry` copies `measure/`, `build/MODELING_PLAN.md` and
  `build/model.py` forward (copies, so the superseded folder stays intact). It refuses when
  iteration = 3 (exit 3, HALT; `RE_SPEC.md:250`).
- **`--route repro` (R2-O1, `deliver`'s `repro_check.py` failure).** A `repro_check` failure
  is a rebuild-fidelity problem, not a verdict change, so this route is accepted **without**
  `qa/gate.json#verdict == REVISE` -- but only when `deliver/repro.json#reproducible` is
  `false` (the failure it is meant to fix), or the human passes `--confirm-repro-failure` (a
  documented override, never a silent default). It moves only `qa/` and `build/` into
  `_itN_SUPERSEDED/` (never `measure/` or `intake/`: the reproducibility problem is in
  `build/model.py`, not in what was measured), writes `_itN_SUPERSEDED/ROUTE` recording
  `repro` (so `init_run.py status` and `stl-re-deliver`'s CHK-SUPERSEDED can tell it apart
  from an ordinary loop), and, unless `--no-carry`, copies `build/MODELING_PLAN.md` and
  `build/model.py` forward as a diffable base (`measure/` was never moved, so it needs no
  carry-forward). **It does not count toward the 3-loop limit**: the iteration number above
  excludes it. Folder numbering itself (`_itN_SUPERSEDED`) is still monotonic and is never
  reused or renumbered, so a repro folder and a later ordinary REVISE folder never collide.
  CHK-SUPERSEDED accepts a `repro`-routed folder even though its `qa/gate.json#verdict` is
  not `REVISE`.
- **ACCEPT-BAND (R2-O2, matches `stl-re-deliver/scripts/_common.py check_acceptance`
  exactly).** A `BAND_NOT_MET` delivery needs a `DECISIONS.md` `ACCEPT-BAND` entry whose
  evidence satisfies all three:
  1. **Evidence lives outside the pipeline folders.** The evidence path is a file inside the
     run, but not under `qa/`, `build/`, `measure/`, `intake/`, `deliver/` or any
     `_itN_SUPERSEDED/` (those are pipeline output, not the owner's own written acceptance).
     Use `decisions/` or the run root.
  2. **The entry cites the current `qa/gate.json` by hash.** The decision text or the
     evidence file must contain the first 12 hex characters of the current
     `qa/gate.json`'s sha256, or its `created` timestamp -- so an acceptance can never
     survive into a later, different gate.
  3. **The entry names a missed band from `gate.json#band_fails`.** At least one
     `band_fails` entry's name (the text before its first `:`) must appear in the decision
     or its evidence.
  Example line: `- 2026-09-25 | J. Owner | ACCEPT-BAND | accept tier1 F01 plate_x miss, gate
  8dcbdc487808 | decisions/accept_band_miss.md`, where `decisions/accept_band_miss.md`
  itself also states the gate hash. Missing any of the three is refused, not merely a
  finding: none of "who, date, which band, the number" alone satisfies the check.

## 11. Clarifications added by the orchestrator session (2026-09-25)

- **List values in `params.json`.** `value` and `measured` may be a number or a list of
  numbers. Use a list for placements measured at unequal angles (DRM's leg angles are a
  worked example, `golden-examples/dreame_brush-caps/report/snap_params.json`). Numbered keys
  (`leg_theta_1`, …) are also valid. A consumer must accept both.
- **Scale correction.** When CHK-SCALE applies one uniform `scale_factor ≠ 1`, it is folded
  into `matrix_4x4` (raw scan → scaled datum frame), so the CAD is built in true mm
  (`RE_SPEC.md:98-101`). The scan-frame STEP then needs the inverse *similarity*, which
  cannot be a rigid OCP transform. Until a reviewed script supports it, `export_frames.py`
  aborts on `scale_factor ≠ 1`, and the run records a limitation in `DECISIONS.md`
  (`OTHER`): only the datum-frame STEP is delivered. No golden applied a scale, so there is
  no evidence to follow.

## 12. Integration decisions (orchestrator session, after Phase 3 drafts)

- **Regime file.** The canonical declaration is **`intake/regime.json`**, written at intake
  with the same shape as `qa/gate.json#regime`: `{"name", "source", "bands", "why",
  "declared_in"?}` (`declared_in` is optional and set by `verdict.py` when it copies the
  regime in, `stl-re-verify/scripts/verdict.py:277`). It replaces the
  `intake/intake.json#regime` key in §10. Verify copies it to `qa/regime.json` and never
  edits it. Deliver checks `gate.json#regime.name == intake/regime.json#name`.
  `DECISIONS.md` carries the matching `REGIME` line.
- **What the baseline-skill band applies to.** p95 and max apply to scan→CAD and to the
  *observable* part of CAD→scan. Raw CAD→scan is reported, not gated. Evidence: the DRM
  official gate applied the limits in both directions
  (`golden-examples/dreame_brush-caps/report/screw_official_gate.json#limits`), and OD
  showed that raw CAD→scan counts surfaces no scanner can see
  (`golden-examples/OD-H12_delonghi-dedica-pump/report/deviation_gate.json`).
- **Registration in every regime.** Verify always runs its own ICP (independence,
  `RE_SPEC.md:173`) and reports numbers both in the builder's datum frame and after ICP.
  The gate is evaluated after ICP. A large gap between the two is a datum finding.
- **`gate.json#hash_frozen`** = `{"before": {path: sha256}, "after": {path: sha256},
  "unchanged": bool}` (as written by `stl-re-verify/scripts/step_check.py verify`).
- **`build/export_check.json`** = `{"datum": {...}, "scan": {...}, ...}` at the top level (as
  written by `stl-re-rebuild-build123d/scripts/export_frames.py`). Readers may also accept
  the OD golden shape `{"exports": {...}}`.
- **ICP iteration cap.** Golden B02 used 60 (`q20_tier2.py`, converged at 48). This is a
  parameter, not a threshold. Non-convergence is reported and makes the Tier-2 gate invalid.
- **`export_check.json` fillets.** `fillets[].status` ∈ `OK | REDUCED | FAILED | NO_EDGES |
  SELECTOR_ERROR`; anything but `OK` is a CHK-FILLET finding. `face_stats` also reports
  `plane_face_count` and `plane_face_median_area_mm2` (reported, not gated).
- **Band keys (canonical, fixed after review V1).** `regime.json#bands` is one flat object with
  exactly these keys, all in mm, and `null` when the regime has no such band:
  `{"p95_mm", "max_mm", "tier1_abs_mm", "interface_max_mm"}`. RE_SPEC fills
  `p95_mm=1.6, max_mm=4.0, tier1_abs_mm=0.15, interface_max_mm=0.8` (`RE_SPEC.md:170-175`).
  baseline-skill picks one material class at intake, records it as `regime.json#material_class`
  (`plastic|machined`), and fills only `p95_mm`/`max_mm` from `stl2step-build123d/SKILL.md:87`.
  A consumer that finds no gated band key (all `null`) or an unknown key must refuse to grade
  (non-zero exit). A missing regime never falls back to a default.
