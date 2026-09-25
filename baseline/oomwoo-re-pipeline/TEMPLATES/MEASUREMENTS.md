# MEASUREMENTS — <OOM-Xnn part name>
<!-- Copy this file to <PART>\5_reference\MEASUREMENTS.md.
     The re-mesh-analyst PRE-FILLS the ID/Feature/Type/Why columns at intake
     (the MEASUREMENT REQUEST). Muhammed fills "Caliper (mm)".
     Rules: record the value AS READ (no rounding — snapping is the modeler's job,
     and every snap is logged). Measure critical dims twice; if the two reads differ
     by >0.05 mm, record both. Soft/flexible features (tires, seals, bristles): note
     "soft" — they get a wider band. Unreachable: write N/A, never guess. -->

Instrument: digital caliper ±0.02 mm (state if different, e.g. depth gauge, mic)
Date measured: YYYY-MM-DD
Caliper guide: open the annotated views posted on this part's GitHub issue
(`<part>/views/intake/caliper_guide_*.png`) — every row ID below is drawn there
(RED = blocking, BLUE = second tier) with jaw placement and the scan-predicted
value. If your reading differs wildly from the prediction, re-check the feature
before writing it down.

## A. Envelope (mandatory — drives the unit check & global scale correction)
| ID | Feature | Caliper (mm) | Notes |
|---|---|---|---|
| ENV-X | overall length (X per photo …) | | |
| ENV-Y | overall width | | |
| ENV-Z | overall height | | |

## B. Functional dimensions (analyst-requested, priority order)
<!-- "Datum ref" ties the dim to the part's named datums (RE_SPEC §3) so Tier-1
     re-measurement on the STEP is unambiguous: e.g. "base plane → top of boss",
     "Ø about datum axis", "pitch in base plane". Envelope dims (§A) stay as-is. -->
| ID | Feature | Type | Datum ref | Why it matters | Caliper (mm) | Notes |
|---|---|---|---|---|---|---|
| F01 | | OD / ID / depth / pitch / wall / flat | | | | |
| F02 | | | | | | |
| F03 | | | | | | |

## C. Extra dims Muhammed measured on his own initiative
| ID | Feature | Caliper (mm) | Notes |
|---|---|---|---|
| X01 | | | |
