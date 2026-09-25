# MEASUREMENTS template (`<run>/intake/MEASUREMENTS.md` → filled copy in `<run>/input/`)

Adapted from `baseline/oomwoo-re-pipeline/TEMPLATES/MEASUREMENTS.md`. Added from the goldens:
the photo-transcribed status with ±0.1 mm effective uncertainty
(`golden-examples/OOM-B02_side-brush-3-arm/5_reference/MEASUREMENTS.md:24`), the per-value photo id
(`golden-examples/OOM-P03_mop-pad-bracket/5_reference/MEASUREMENTS.md:69-98`), the "absent, not
passed" and scan-authority statuses (B02 `MEASUREMENTS.md` status block; DRM and OD had no calipers,
`analysis/golden/dreame_brush-caps.md` §5, `analysis/golden/OD-H12.md` §4), and the scan-predicted
value per row (`RE_SPEC.md:197-202`).

## Status vocabulary (one per row)

| Status | Meaning | Uncertainty used downstream | Tier-1 gated? |
|---|---|---|---|
| `caliper` | read at the bench by the operator, as read (no rounding) | instrument: ±0.02 (template) vs ±0.05 (RE_SPEC.md:91) — conflict, state which | yes, ±0.15 (RE_SPEC.md:170) |
| `caliper-photo` | reading legible in a caliper photo; jaw placement inferred and owner-confirmed | **±0.1 effective** (B02 MEASUREMENTS.md:24) | yes, but declare the photo id and the attribution |
| `caliper-photo-unconfirmed` | photo reading whose feature attribution is not confirmed | not used as a parameter | no |
| `operator-spec` | a value the operator states (drawing, datasheet, M02 OPERATOR_SPEC) | as stated | yes |
| `scan-authority` | no caliper; the scan value is the parameter | measured noise floor | **no — ungated, say so in the verdict** |
| `absent` | requested, not measured | — | **no — "absent, not passed"** |
| `N/A` | unreachable; never guess | — | no |
| `soft` | flexible feature (bristles, seals); wider band declared at intake (B02 used ±3 mm, heuristic, n=1: B02) | declared | no |

Rules carried from the baseline template: record the value as read; measure critical dims twice
and record both if the reads differ by > 0.05 mm (TEMPLATES/MEASUREMENTS.md:6-7); unreachable = N/A.

## Template

```markdown
# MEASUREMENTS — <part>

Instrument: <caliper model, stated resolution> — state if different (depth rod, pin gauge)
Date measured: <YYYY-MM-DD or "photos only">
Status summary: <n> of <N> rows carry a value; the rest are ABSENT, not passed.

"Scan says" is the scan-predicted value (datum frame, from intake/alignment.json and sections).
It is there so a gross misread (wrong feature, wrong jaws) is caught at the bench. Do NOT copy it
into the reading column.

## A. Envelope (first; drives CHK-SCALE)
| ID | Feature | Jaw placement (photo ref) | Scan says | Reading (mm) | Status | Photo id | Notes |
|---|---|---|---|---|---|---|---|
| ENV-X | overall length along datum X | | | | | | |
| ENV-Y | overall width | | | | | | |
| ENV-Z | overall height to the TRUE topmost feature (P03: define to the stem top, not the hex tip) | | | | | | |

## B. Functional dimensions (priority order; datum ref makes Tier-1 re-measurement unambiguous)
| ID | Feature | Type | Datum ref | Why it matters | Jaw placement | Scan says | Reading | Status | Photo id |
|---|---|---|---|---|---|---|---|---|---|

## C. Wall thicknesses / second tier
| ID | Feature | Jaw placement | Scan says | Reading | Status | Photo id |
|---|---|---|---|---|---|---|

## D. Photo-transcribed candidates — confirm the attribution or strike it
| ID | Photo | Reading | Inferred feature | Maps to | Confirmed by / date |
|---|---|---|---|---|---|

## E. Extra dims measured on the operator's own initiative
| ID | Feature | Reading | Notes |
|---|---|---|---|
```

## How many rows

The baseline template asks for 8–15 dims, envelope first (`TEMPLATES/INTAKE_CARD.md:39`); the
B02 intake requested 17 (`B02/6_RE_work/INTAKE_CARD.md` §8). Request every caliper-coverable
functional interface; the count follows the part, not a quota.

## Scan-predicted value: how to fill "Scan says"

- Envelope: `extents_aligned` / `bounds_aligned` in `intake/alignment.json` (exclude soft features).
- Diameters: circle fits on datum-frame sections (`datum_fit.py` circle fits, or the stations in
  `alignment.json#secondary.station_detail`).
- Depths / steps: offsets of fitted planes in the datum frame (`datum_fit.py plane` on the aligned mesh).
- Write the estimator next to the value when it is not obvious (facet-film T5). For a lobed or
  non-round feature give both extremes and ask for both readings (B02 M4/M5).
- If the scan cannot see the feature, write "not visible — needs <photo with ruler / screw removed>"
  instead of a number (B02 M11, RE_SPEC.md:201-202).
