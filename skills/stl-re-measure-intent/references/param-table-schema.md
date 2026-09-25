# `measure/params.json` schema and `PARAM_TABLE.md`

The binding base schema is `skills/stl-re-orchestrate/references/run-contract.md` §4. This file
repeats it and adds the keys this skill needs. Per the contract, keys may be added but never
renamed or dropped. `scripts/param_table.py` validates the file and renders `PARAM_TABLE.md`
from it. The table is never edited by hand (run-contract §4; CHK-NUMBERS downstream).

## 1. Top level

```json
{
  "schema": "stl-re/params.json@1", "tool": "...", "tool_version": "...",
  "inputs": {"<path>": "<sha256>"}, "seed": 0, "created": "<ISO-8601, provenance only>",
  "part": "<part id>",
  "frame": "<datum frame and theta sign convention, copied from alignment.json + 'theta CCW about +Z from +X'>",
  "scan_noise_mm": 0.0,
  "params": { "<NAME>": { ... } },
  "struck": [ ... ],
  "simplifications": [ ... ],
  "checks": { "CHK-COUNT": {...}, "CHK-ACHIEVABLE": {...}, "CHK-CLUSTER": {...}, "CHK-FRAME": {...} },
  "open_questions": [ "..." ]
}
```

- `inputs` hashes the aligned scan, `alignment.json`, the filled `MEASUREMENTS.md` and every
  photo cited.
- `scan_noise_mm` is copied from `intake/alignment.json#scan_noise_mm.value`. When it is
  absent, the validator refuses every `round-within-noise` row.

## 2. Per-parameter entry

| Key | Req. | Meaning | Evidence for the rule |
|---|---|---|---|
| `value` | yes | The chosen CAD value (int for counts). | run-contract §4 |
| `unit` | yes | `mm`, `deg` or `count`. | run-contract §4 |
| `measured` | yes | Number, list of reads, `"lo..hi"` range, or `null` (unmeasured only). | C7: measured → chosen for every row (`analysis/SYNTHESIS.md`) |
| `rule` | yes | One of `caliper-direct`, `round-within-noise`, `std-size-snap`, `symmetry`, `mean-of-n`, `keep-measured`, `photo-inferred`, `assumed`. | run-contract §4; `references/intent-rules.md` |
| `source` | yes | One of `caliper`, `caliper-photo`, `operator-spec`, `scan`, `photo-inferred`, `standard`, `assumed`. | C4, C11 |
| `estimator` | yes | How it was measured: point set, fit, percentile, stations, script + output file. | C13; facet-film T5 |
| `uncertainty_mm` | yes | Caliper ±, photo ≥0.1, scan: the fit rms or the noise floor. | `SYNTHESIS.md` §4 |
| `evidence` | yes | Figure/JSON path, photo id, or `file:line`. | C13 |
| `critical` | yes | A functional interface (mating, drive, seat). | C9 |
| `attribution` | caliper-photo | Who confirmed which feature and which jaw placement, and when. | C5; B02 `MEASUREMENTS.md:19-24` |
| `derivation` | when value ≠ measured under `caliper-direct` | E.g. `"radius = D/2"`, `"AF·2/√3"`. | B02 `SKIRT_R_LOBE = 26.85/2` (`PARAM_TABLE.md:38`) |
| `scatter_mm` | `symmetry` | Measured spread across instances. | C10 |
| `scatter_note` | `symmetry` beyond noise, or on a `deg` value | Intent reason plus the residual it leaves. | C10; B02 arms 120° |
| `rerun_trigger` | critical and not calipered | What reading would force a re-run. | B02 `VERDICT.md:28-30` |
| `frame` | angles | Frame and sign convention if it differs from the top level (it should not). | CHK-FRAME, B02 −71° vs +59° |
| `note` | optional | Free text; rendered under the table. | — |

## 3. `struck[]` (CHK-ACHIEVABLE)

```json
{"name": "F06 skirt OD MIN", "reading": 24.84, "source": "caliper-photo D-05",
 "window": "24.99..27.25 at z=1.00 (sim_caliper.json)",
 "proof": "3-lobed skirt: two jaws read a support width; reading + 0.1 < window min",
 "rerun_trigger": "if 24.84 was taken another way (flat-to-axis x2 ...), re-measure with a jaw-placement photo"}
```
All five keys except `source` are required. Template: `OOM-B02/6_RE_work/PARAM_TABLE.md:108-121`.

## 4. `simplifications[]`

`{"name": "...", "modelled_as": "...", "deviation_cost": "<measured on the scan, mm>"}`.
`deviation_cost` is required (C14).

## 5. `checks{}`

`{"ran": true, "result": "pass|finding|fail", "note": "..."}`, the same shape as
`qa/gate.json#checks` (run-contract §6). A `fail` blocks rendering. Resolve it first (strike,
re-measure, re-count), then record the check as `finding` with a note on what was done.

## 6. What the validator enforces

| Condition | Result | Why |
|---|---|---|
| Missing required key; bad enum | error | run-contract §4 |
| `caliper-photo` without photo id, `attribution`, or with `uncertainty_mm` < 0.1 | error | C5 |
| `std-size-snap` on a non-caliper source, or a move > 0.1 mm | error | `RE_SPEC.md:92`; C9 |
| `std-size-snap` at all | warning "heuristic" | no golden applied it (`SYNTHESIS.md` §6) |
| `round-within-noise` without a noise floor, or moved outside measured range ± noise | error | C8 |
| `keep-measured` value outside the measured range | error | C7 |
| `symmetry` with `scatter_mm` > noise and no `scatter_note` | error | C10 |
| `symmetry` without `scatter_mm`, or with a scalar/prose `measured` instead of a per-instance list | error | C10 (round 1, M1) |
| Critical `scan` value with a snapping rule | error | C9 |
| Critical `scan` value moved beyond the scan noise floor by ANY rule, `scatter_note` included | error | C9 (round 1, M1: closes the symmetry/`scatter_note` bypass — B02 hex AF 7.358) |
| Critical and uncalipered without `rerun_trigger` | warning | B02 limitation 3 |
| `count` from scan whose estimator doesn't name rotational order/FFT | error | CHK-COUNT |
| `photo-inferred`/`assumed`/`standard` source with a measuring rule, **or** `assumed`/`photo-inferred` rule with a measured source (e.g. `source: scan, rule: assumed`), **or** an unmeasured source with non-null `measured` | error | C11 (round 1, M4: enforced both ways) |
| `mean-of-n` without a `measured` list of ≥2 numbers, or `value` not within uncertainty/noise of their mean | error | C7 (round 1, M3) |
| A list `value` (run-contract §11) checked against a `measured` of a different length, or reduced to a mean instead of compared element-wise | error | run-contract §11 (round 1, M2) |
| `struck` entry without window/proof/trigger; simplification without cost | error | CHK-ACHIEVABLE, C14 |
| Missing CHK-COUNT/ACHIEVABLE/CLUSTER/FRAME record | warning | this skill's checks |

## 7. Rendered table

`PARAM_TABLE.md` contains a header with the params.json sha256, the frame and the noise floor.
Below that come the main table (name, value, unit, measured, rule, source, ±, estimator,
evidence, critical), the notes/attributions/re-run triggers, struck readings, simplifications,
checks and open questions. The column set is the union of the golden PARAM_TABLEs (B02, P03)
and facet-film T8.
