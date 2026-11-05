# Gears (heuristic, n=1: M02-02-03)

One golden gear exists: M02-02-03, a 30T + 17T stacked spur gear. Everything here is
**(heuristic, n=1: M02)**. That record has **no scan datum and no scan deviation gate**. It is
spec-conformance only, driven by operator values (`analysis/SYNTHESIS.md` §0.1;
`analysis/golden/M02-02-03.md` §7, Questions 1–2). Use it for gear *parameter handling*, not
as proof that a scan-to-gear workflow is validated.

## 1. What to measure, and who owns it

| Parameter | Source in M02 | Rule for this skill |
|---|---|---|
| Tooth count z | operator 30 / 17 (`OPERATOR_SPEC.json`) | Operator value if given. Otherwise count by **rotational order at ≥3 strictly interior stations** (`scripts/pattern_count.py`); crest peaks are diagnostic only (CHK-COUNT). |
| Tip (outside) Ø | operator 19.05 / 11.2 | **Measured OD sets the tip** (it truncates the nominal addendum); do not force m·(z+2) (`golden-examples/M02-02-03_watertight-design-intent/README.md:25`; nominal would be 19.2 / 11.4, `analysis/golden/M02-02-03.md` §5). |
| Face width, bore, axial layout | operator | caliper-direct |
| Root Ø | derived rp − 1.25·m | `standard`, labelled (`model.py:33`) |
| Module m | **not measured**; 0.6 "common nominal" | `assumed`. The record does not say how 0.6 was chosen (`analysis/golden/M02-02-03.md` Questions 5). |
| Pressure angle | not measured; 20° | `standard` |
| Relative phase between stacked gears | not measured; 0° ("no phase datum supplied") | `assumed` |
| Backlash, profile shift, tip relief, root fillet, hub, chamfer | not measured → none modelled | list each as an assumption; **invent nothing** (`README.md:21-27`) |

## 2. The failure that earned CHK-COUNT here

- An earlier scan-derived candidate, **27 teeth / Ø21.75**, was wrong. It was replaced once
  the operator measured 30 / 19.05 (`golden-examples/M02-02-03_watertight-design-intent/DESIGN_NOTES.md:5`).
  The record does not say how 27 was produced (`analysis/golden/M02-02-03.md` Questions 3).
- In the QA, crest-peak counting on the exact CAD gave **31** (big, z 0.5) and **16** (small,
  z 9.5) (`qa_report.json#gears.*.station_details[*].diagnostic_peak_count`).
- The rotational-order residual gave 30 and 17 at all six stations. It qualified {10, 15, 30}
  and took the maximal order, and qualified {17} for the small gear (`qa_report.json`;
  `VERDICT.md:25`).
- Re-run with this skill's script on the delivered STEP (tessellated at 0.005 mm): **30 and 17
  at all six stations**, qualified {10, 15, 30} / {17}. Tip Ø from the rays was 19.049997 /
  11.199998 (golden 19.049996889 / 11.199998555). Crest peaks gave 31/32/31 and 18/18/18.
  See `references/validation.md`.

The M02 qualification threshold (0.002 mm max-abs) suits **exact CAD only**. On a scan, use
FFT dominance agreed at ≥3 stations plus a residual local minimum (`scripts/pattern_count.py`
without `--tol`).

## 3. What to hand the rebuild

- One involute tooth plus a polar pattern on a root-circle core. Module, PA, z and tip Ø are
  named parameters (`golden-examples/M02-02-03_watertight-design-intent/model.py:29-64`).
- For coplanar stacked gears, a continuous core "bridge" guarantees one solid (`model.py:76-81`).
- **Face-count issue (polygonal flanks):** M02 built each flank as a 20-sample polyline and the
  tip as 7 samples (`model.py:26-27,48-55`). That produced ~2354 planar faces (inspection-only
  count, `analysis/golden/M02-02-03.md` §12.13). This is the CHK-PATCHWORK pattern
  (`analysis/SYNTHESIS.md` D10). The owner ruled that the face count is **reported, not gated**
  (QUESTIONS.md Q3). Record in `params.json#simplifications` that the flank representation is
  the rebuild's choice, and ask the rebuild skill for a true involute or spline flank. The
  measurement side has nothing to "round" here.

## 4. Claim boundary to pass downstream

"Digital design-intent model constrained by operator measurements. Physical interchangeability
and manufacturing release require mating-part or physical fit verification"
(`golden-examples/M02-02-03_watertight-design-intent/README.md:31`). A gear rebuilt from a scan
without an operator tooth count or OD carries at least this boundary, plus the list of assumed
gear parameters.
