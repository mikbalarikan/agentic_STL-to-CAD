# OD-W03 water tank valve: scan to STEP

The second real run of the v1 skills (2026-09-28), on a part with no golden record. Ikbal supplied
the scan and one catalogue photo and no calipers. Ikbal accepted the result, delivered it, and
marked the run a successful example.

The part is a translucent moulded valve cover: a stadium flange with a skirt, two valve cups with
conical shoulders and single-barb hose nipples, a middle boss, four ribs, and an L-shaped ear with
a fixing hole at each end.

## Result

Band regime: plastic, p95 ≤ 0.30 / max ≤ 0.80 mm ("p95 plastik parça toleransı").

- CAD: one valid closed solid, 106 faces (98.6 % analytic area), all 5 fillets at target radius,
  and the build is reproducible across two fresh rebuilds.
- scan→CAD: p95 0.320 mm unmasked and 0.307 mm masked. Max 1.113 mm unmasked and 0.785 mm with two
  scanner artifacts masked (the film across a barb tip and the junk facets at a tab/lug junction).
  The p95 overshoot is spread out. Most of it comes from the lower skirt edge and from cup B's
  upper wall, which is about 0.11 mm short and could be fixed.
- Observable CAD→scan: p95 1.512 mm. Almost all of it is the hollow interior. The owner chose that
  interior (1.2 mm walls), and the scanner never saw it.
- Datum audit: 0.020° / 0.003 mm against the verifier's own re-fit.
- Official verdict `BAND_NOT_MET`, accepted for delivery by the owner (record `ACCEPT-BAND`, gate
  `2fe9569f1fa0`).

## Records

The run's records are in [`evals/real-runs/OD-W03/`](../../evals/real-runs/OD-W03/):

- Delivery report with the full parameter table, frames and limitations:
  [`README.md`](../../evals/real-runs/OD-W03/README.md).
- Verdict: [`VERDICT.md`](../../evals/real-runs/OD-W03/VERDICT.md) and
  [`gate.json`](../../evals/real-runs/OD-W03/gate.json). Deviation overlay:
  [`overlay.png`](../../evals/real-runs/OD-W03/overlay.png).
- [`INTAKE_CARD.md`](../../evals/real-runs/OD-W03/INTAKE_CARD.md),
  [`DECISIONS.md`](../../evals/real-runs/OD-W03/DECISIONS.md),
  [`datum_spec.json`](../../evals/real-runs/OD-W03/datum_spec.json),
  [`PARAM_TABLE.md`](../../evals/real-runs/OD-W03/PARAM_TABLE.md) and
  [`MODELING_PLAN.md`](../../evals/real-runs/OD-W03/MODELING_PLAN.md).
- The verifier's workaround scripts: [`qa_scripts/`](../../evals/real-runs/OD-W03/qa_scripts/).

The skill defects this run surfaced (12, of which 5 are fixed) are in
[`evals/real-runs/OD-W03.md`](../../evals/real-runs/OD-W03.md).

## Not in the repo

The run folder lived in the working session's temporary storage and was not kept after delivery.
Only the delivery zip given to Ikbal (`OD-W03_RE_BAND_NOT_MET_2026-09-28.zip`, 11 MB) holds these
files, so unlike the OD-H22 example this one cannot be rebuilt from the repo alone:

- The STEP files `build/OD-W03_datum.step` and `build/OD-W03.step`, and the CAD STL.
- The editable intent `build/model.py` and `measure/params.json`, plus the measurement scripts and figures.
- The input scan (400,657 faces) and the catalogue photo.
- The rest of `qa/`: registration, deviation JSON, the Tier-1 dimensions and hash freeze.

Adding the zip's `deliverables/` and `source/` folders here (with the scan and photo) would make
the example complete.
