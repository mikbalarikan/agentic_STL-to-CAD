# OD-E02 control button board: scan to STEP

A real run of the v1 skills (2026-09-28) on a part with no golden record. Ikbal supplied the scan
and two catalogue photos and no calipers. Ikbal accepted the result, delivered it, and marked the
run a successful example.

The part is the front control button board of a DeLonghi espresso machine: a stepped moulded
housing with a snap-fitted back cover, a PCB connector shroud, two screw holes, a bent mounting
tab, four latch hoops and three loose push-button caps. It is delivered as one fused solid of the
assembly as scanned.

## Result

Band regime: plastic, p95 ≤ 0.30 / max ≤ 0.80 mm ("p95 plastik parça toleransı").

- CAD: one valid closed solid, 374 faces (95.4 % analytic area), driven by 120 parameters (118
  from the scan, 2 assumed). 22 fillets: 20 at target radius, 2 reduced because the wall is too
  thin for both. The housing tiers are offsets of one core outline, so one sketch drives every tier.
- Three loops, each checked by a fresh independent verifier with the same protocol:

  | | it1 | it2 | it3 |
  |---|---|---|---|
  | scan→CAD p95 / max (mm) | 0.243 / 1.690 | 0.243 / 1.062 | 0.237 / 0.922 |
  | scan points over 0.8 mm | 81 | 24 | 9 |
  | observable CAD→scan p95 / max (mm) | 0.674 / 5.119 | 0.650 / 5.358 | 0.633 / 5.422 |
  | verdict | REVISE | REVISE | BAND_NOT_MET |

- scan→CAD: p95 passes. The max misses on 9 of 294,367 points, all at the B1 side-collar cut,
  which is modelled as a plane where the scan curves.
- Observable CAD→scan: 98.5 % of the over-band points lie in openings the scanner never reached
  (the connector shroud interior, the shroud-to-rim slot and the two screw bores). That geometry is
  assumed and cannot be fixed without a re-scan or depth readings.
- Datum audit: 0.068° / 0.014 mm against the verifier's own re-fit. ICP correction 0.087° / 0.023 mm.
- Official verdict `BAND_NOT_MET`, accepted for delivery by the owner (record `ACCEPT-BAND`, gate
  `1e9b7dcea587`). The fresh-process reproducibility check passed.

## Records

The run's records are in [`evals/real-runs/OD-E02/`](../../evals/real-runs/OD-E02/):

- Delivery report with the full parameter table, frames and limitations:
  [`README.md`](../../evals/real-runs/OD-E02/README.md).
- Verdict: [`VERDICT.md`](../../evals/real-runs/OD-E02/VERDICT.md) and
  [`gate.json`](../../evals/real-runs/OD-E02/gate.json). Deviation overlay:
  [`overlay.png`](../../evals/real-runs/OD-E02/overlay.png).
- [`DECISIONS.md`](../../evals/real-runs/OD-E02/DECISIONS.md),
  [`accept_band.md`](../../evals/real-runs/OD-E02/accept_band.md) and
  [`MODELING_PLAN.md`](../../evals/real-runs/OD-E02/MODELING_PLAN.md).

The skill defects and lessons this run surfaced (7, of which 1 is fixed on this branch) are in
[`evals/real-runs/OD-E02.md`](../../evals/real-runs/OD-E02.md).

## Not in the repo

The run folder lived in the working session's temporary storage and was not kept after delivery.
Only the delivery zip given to Ikbal (`OD-E02_control-button-board_RE_BAND_NOT_MET_2026-09-28.zip`,
22.9 MiB) holds these files, so this example cannot be rebuilt from the repo alone:

- The STEP files `build/OD-E02_control-button-board_datum.step` and
  `build/OD-E02_control-button-board.step`, and the CAD STL.
- The editable intent `build/model.py` and `measure/params.json`, plus the measurement scripts,
  figures and the intake card.
- The earlier iterations (`_it1_SUPERSEDED/`, `_it2_SUPERSEDED/`).
- The rest of `qa/`: registration, deviation JSON, datum audit, step check and hash freeze.
- The input scan (586,137 faces) and the two photos. The scan was not put in the zip because the
  owner already has it.

Adding the zip's `deliverables/` and `source/` folders here (with the scan and photos) would make
the example complete.
