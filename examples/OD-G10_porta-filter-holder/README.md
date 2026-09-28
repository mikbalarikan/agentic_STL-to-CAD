# OD-G10 porta filter holder: scan to STEP

A real run of the v1 skills (2026-09-28) on a part with no golden record. Ikbal supplied the scan
(400,123 faces in one body, not watertight) and two photos, and no calipers. Ikbal had the result
delivered as it stood and marked the run a successful example.

The part is the portafilter holder cup of an espresso machine: Ø 80.2 mm outer wall, 31 mm of
scanned height, a stepped rim with six notches, three bayonet lugs with stops and top channels,
a drafted bore and a plate with a keyhole, two bosses and a side hole.

## Result

Band regime: plastic, p95 ≤ 0.30 / max ≤ 0.80 mm ("p95 plastik parça toleransı").

- CAD: one valid closed solid, 182 faces, 100 % analytic area (98 planes, 57 cylinders, 8 cones,
  19 tori), driven by 67 parameters (49 from the scan, 15 photo-inferred, 3 assumed). One (r,z)
  profile is revolved for the cup; the inner ring is revolved sectors per gap and per lug; one lug
  instance is placed three times at 120°; cut tools come last. The under-lug floors are fitted
  concave horizontal-axis cylinders (R ≈ 170–240 mm). 7 fillets, all at target radius.
- Datum: primary on the lug top pads, axis on the outer wall, clock on the 3-fold lug phase.
  Tilt 0.20°.
- One loop. The fresh independent verifier returned **HALT**: its own ICP did not converge (60,
  then 500 iterations), so the gate label is INVALID and there is **no official grade**. Its
  diagnosis is a script limit, not a geometry error: about 13 % of the kept ICP pairs join
  unscanned CAD faces to the opposite wall, and `tier2_icp.py` accepts them.
- Datum-frame numbers (inspection only, no ICP), from [`gate.json`](../../evals/real-runs/OD-G10/gate.json):

  | Measure | p95 / max (mm) | Against the band |
  |---|---|---|
  | scan→CAD | 0.244 / 0.878 | p95 within; max from 6 points at the lug-3 end, no cluster |
  | CAD→scan, masked | 0.357 / 5.13 | outside, mostly unscanned CAD (underside, θ 38–151° outer wall, plate interior) |
  | datum audit (report-only) | axis 0.010°, origin 0.005 mm, clock 1.89° | clock outside the reference |

- The owner decided "bu haliyle deliver et" (deliver it as it is). The verdict stays HALT. The
  delivery scripts refuse HALT by design, so they ran through a run-local wrapper that adds HALT
  to the deliverable list for this run only; every other preflight check ran. The decision is in
  [`owner_override_2026-09-28.md`](../../evals/real-runs/OD-G10/owner_override_2026-09-28.md),
  bound to gate `a415ac1263b6`. The fresh-process reproducibility check passed.

## Records

The run's records are in [`evals/real-runs/OD-G10/`](../../evals/real-runs/OD-G10/):

- Delivery report with the full parameter table, frames and limitations:
  [`README.md`](../../evals/real-runs/OD-G10/README.md).
- Verdict: [`VERDICT.md`](../../evals/real-runs/OD-G10/VERDICT.md) and
  [`gate.json`](../../evals/real-runs/OD-G10/gate.json). Deviation overlay:
  [`overlay.png`](../../evals/real-runs/OD-G10/overlay.png).
- [`DECISIONS.md`](../../evals/real-runs/OD-G10/DECISIONS.md) (regime, scan-only, HALT and the
  override), [`INTAKE_CARD.md`](../../evals/real-runs/OD-G10/INTAKE_CARD.md) and
  [`MODELING_PLAN.md`](../../evals/real-runs/OD-G10/MODELING_PLAN.md).

The skill defects this run surfaced (8, of which 1 is fixed on this branch: `package_zip.py`
treats `qa/dev_arrays*.npz` as regenerable, with a size rule in `delivery-package.md`) are in
[`evals/real-runs/OD-G10.md`](../../evals/real-runs/OD-G10.md). The top open one is
`tier2_icp.py`: it needs CAD-side coverage masks and a facing-normal test. With that fixed, this
part can be re-verified and officially graded.

## Not in the repo

The run folder lived in the working session's temporary storage and was not kept after delivery.
Only the delivery zip given to Ikbal (`OD-G10_porta_filter_holder_RE_HALT_2026-09-28.zip`, 7.7 MiB)
holds these files, so this example cannot be rebuilt from the repo alone:

- The STEP files `build/OD-G10_porta_filter_holder_datum.step` and
  `build/OD-G10_porta_filter_holder.step`, and the CAD STL.
- The editable intent `build/model.py` and `measure/params.json`, plus the measurement scripts
  and figures.
- The rest of `qa/`: registration runs, deviation JSON, ICP diagnosis, datum audit, step check and
  hash freeze. Large regenerable intermediates were left out of the zip and are listed in its
  `PACKAGE_INDEX.md`.
- The input scan and the two photos.

Adding the zip's `deliverables/` and `source/` folders here (with the scan and photos) would make
the example complete.
