# OD-H22 3-way valve: scan to STEP

The first real run of the v1 skills (2026-09-25), on a part with no golden record. Ikbal supplied the
scan and four catalogue photos and no calipers. Ikbal reviewed the result and approved it:
"quality very good, fully approve, test successful".

- Final STEP: [`run/build/OD-H22_3-way-valve.step`](run/build/OD-H22_3-way-valve.step) (scan frame) and
  [`run/build/OD-H22_3-way-valve_datum.step`](run/build/OD-H22_3-way-valve_datum.step) (datum frame).
  One valid closed solid, 162 analytic faces, 12 features, all 5 fillets at target radius.
- Editable intent: [`run/build/model.py`](run/build/model.py) driven by [`run/measure/params.json`](run/measure/params.json).
- Delivery report: [`run/deliver/README.md`](run/deliver/README.md). Verdict: [`run/qa/VERDICT.md`](run/qa/VERDICT.md).
- Inputs: [`run/input/scan.stl`](run/input/scan.stl) and [`run/input/photos/`](run/input/photos/).

## Result

Band regime: plastic, p95 ≤ 0.30 / max ≤ 0.80 mm (confirmed by Ikbal).

- scan→CAD: p95 0.235 mm (passes), max 1.427 mm. The max is scan material inside the +X ear hole,
  which the photos show open.
- Observable CAD→scan: p95 1.48 mm, almost all on interior bores and slots the scanner never reached.
- Official verdict `BAND_NOT_MET`; accepted for delivery by the owner
  ([`run/decisions/accept_band.md`](run/decisions/accept_band.md)).

Skill defects the run surfaced are tracked in [`evals/real-runs/OD-H22.md`](../../evals/real-runs/OD-H22.md).

## Left out of the repo

To keep the repo lean these files are not committed, though `run/deliver/MANIFEST.json` lists them:

- `run/intake/work.stl` and `run/intake/aligned_work.stl` (11.9 MB each): intermediate copies of the
  scan, regenerable by `stl-re-intake-datum` from `run/input/scan.stl`.
- `run/build/OD-H22_3-way-valve_cad.stl` (4.4 MB): a tessellation of the STEP, regenerable by `model.py`.
- The 37.5 MB delivery zip, which only repackages the files here.
- The duplicate `source/` folder (same scan and photos as `run/input/`).
