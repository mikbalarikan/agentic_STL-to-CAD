# OD-S01 steam valve assembly: scan to STEP

The second real run of the v1 skills (2026-09-28), on a part with no golden record. Ikbal supplied the
scan and five catalogue photos, no calipers, and asked for the plastic tolerance ("p95 plastik parça
toleransı"). Ikbal accepted the result and marked the run finished as a successful example.

The part is a rotary steam valve assembly: a cap with a splined spindle and a 3-fold cam ring, the
valve body with a top clip port, two side hose ports, a hose barb and a microswitch. It was scanned
as one mesh and delivered as one fused solid.

## Result

Band regime: `baseline-skill` plastic, p95 ≤ 0.30 / max ≤ 0.80 mm. Scan-only, full-res scan confirmed
by the owner.

| QA pass | scan→CAD p95 / max (mm) | observable CAD→scan p95 / max (mm) | verdict |
|---|---|---|---|
| Iteration 1 | 0.520 / 2.270 | 0.800 / 3.129 | `REVISE` |
| Iteration 2 (final) | 0.449 / 1.940 | 0.761 / 2.890 | `BAND_NOT_MET`, owner-accepted |

- The final CAD is one valid closed solid, 351 faces, all analytic, and all 3 fillets are at their
  target radius. It is exported in both the datum frame and the scan frame.
- Each iteration was graded by a fresh, independent QA agent with its own ICP.
- Iteration 1's findings were concrete, and all of them were fixed in iteration 2. The port blocks
  were about 1 mm short, two features were missing from intake, and a sloped shoulder had been
  built as steps.
- Only the barb zone meets the band. The 1.94 mm max is an iteration-2 regression at the port
  junction box. A QA probe (not a gate) showed that fixing every cluster over 0.8 mm would still
  leave about p95 0.34. That is why the owner accepted the miss instead of running a third loop
  ([DECISIONS](../../evals/real-runs/OD-S01/DECISIONS.md), ACCEPT-BAND on gate `19f6d742b0ae`).
- Known limits: Tier-1 did not run and scale is not caliper-checked, because there were no calipers.
  The spline tooth count could not be resolved from the scan, so the spindle is modelled as a plain
  cylinder. Unscanned interiors (valve bore, flow passages) are not modelled.

## Files

The run's records are in [`evals/real-runs/OD-S01/`](../../evals/real-runs/OD-S01/):

- [Delivery README](../../evals/real-runs/OD-S01/README.md): frames, the parameter table and limitations.
- [VERDICT](../../evals/real-runs/OD-S01/VERDICT.md) and [gate.json](../../evals/real-runs/OD-S01/gate.json) for iteration 2. Iteration 1 is under [`it1/`](../../evals/real-runs/OD-S01/it1/).
- [INTAKE_CARD](../../evals/real-runs/OD-S01/INTAKE_CARD.md), [MODELING_PLAN](../../evals/real-runs/OD-S01/MODELING_PLAN.md), [PARAM_TABLE](../../evals/real-runs/OD-S01/PARAM_TABLE.md) and [DECISIONS](../../evals/real-runs/OD-S01/DECISIONS.md).
- [QA overlay](../../evals/real-runs/OD-S01/overlay_theta.png) (θ view, iteration 2).
- The run log, lessons and the 10 skill defects it found are in [`evals/real-runs/OD-S01.md`](../../evals/real-runs/OD-S01.md).

## Not in the repo

The run folder lived in the working session's temporary workspace and was not kept. The only full
copy is the delivery zip sent to the owner, `OD-S01_steam-valve_RE_BAND_NOT_MET_2026-09-28.zip`
(27.8 MiB, sha256 on its `.sha256` sidecar). So these files are missing here, unlike the
[OD-H22 example](../OD-H22_3-way-valve/):

- The STEP files (`build/OD-S01_steam-valve.step` and `build/OD-S01_steam-valve_datum.step`) and the CAD STL.
- The editable intent: `build/model.py` and `measure/params.json`.
- The measurement scripts and figures, `MANIFEST.json`, `repro.json` and the QA JSONs apart from the gate.
- The inputs: the raw scan and the photos.

To complete the example, unzip the delivery zip into `run/` here, following the OD-H22 layout.
