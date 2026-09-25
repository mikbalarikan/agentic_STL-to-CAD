# Run contract (shared by all `stl-re-*` skills)

This file is the single source of the hand-off contract. Every `stl-re-*` skill reads
and writes these paths and keys. A skill may add keys; it may not rename or drop them.
Evidence: `analysis/SKILL_ARCHITECTURE.md` §3–§4, `analysis/SYNTHESIS.md`.

## 1. Folder layout

```
<run>/
  input/            scan.stl (never modified), photos/, MEASUREMENTS.md (filled by a human), INPUT_HASHES.json
  intake/           INTAKE_CARD.md, intake.json, MEASUREMENTS.md (request), alignment.json, work.stl, aligned_work.stl
  measure/          params.json, PARAM_TABLE.md, figures/
  build/            MODELING_PLAN.md, model.py, build_log.txt, <part>_datum.step, <part>.step, <part>_cad.stl, export_check.json
  qa/               gate.json, VERDICT.md, masks.json, overlays/
  deliver/          README.md, MANIFEST.json, repro.json          (only after qa/VERDICT.md exists)
  _itN_SUPERSEDED/  the previous iteration's measure/ build/ qa/, moved intact
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

- `regime`: `{"name": "RE_SPEC|baseline-skill|project-spec", "source": "<path:line>", "bands": {...}}`
- `hash_frozen`: STEP sha256 before and after QA.
- `datum_audit`: `{"angle_deg", "origin_offset_mm", "point_disagreement_p95_mm", "reference_band": "≤0.3° / ≤0.15 mm (RE_SPEC.md:241)", "blocking": false}`.
- `validity`, `surface_census`: reported only.
- `tier1`: per-dim `{caliper, cad, delta, pass}`.
- `deviation`:
  - `{"registration": {"method", "iterations", "converged", "delta_deg", "delta_mm"}, "scan_to_cad": stats, "cad_to_scan": stats, "cad_to_scan_observable": stats, "unobservable_fraction", "zones": {...}, "masks": [{"name", "why", "fraction", "stats_inside"}], "unmasked": stats, "sensitivity": [...], "over_band_clusters": [...]}`
  - `stats` = `{n, rms, p50, p95, p99, max}` in mm, plus the sampling and seed.
  - `scan` names the file used; `full_res: true|false`.
- `checks`: `{"CHK-...": {"ran": true, "result": "pass|finding|fail", "note": ""}}`.
- `verdict`: one of §7.

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
