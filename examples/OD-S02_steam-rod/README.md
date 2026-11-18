# OD-S02 steam rod: scan to STEP

A real run of the v1 skills (2026-09-28) on a part with no golden record. Ikbal supplied the scan
(499,164 faces, not watertight, 33 open loops) and two photos, and no calipers. Ikbal accepted the
result, delivered it, and marked the run a successful example.

The part is the steam wand of a coffee machine: a black connector rod with a tapered spigot and
O-ring seats, a knob with a lever paddle, a sleeve with a sealing band, a bent Ø6 steel tube, a
white windowed bushing and a steel tip. It was scanned as one mesh and, by owner decision
(PART-CLASS), is delivered as one fused solid of the assembly as scanned.

## Result

Band regime: plastic, p95 ≤ 0.30 / max ≤ 0.80 mm ("p95 plastik parça toleransı").

- CAD: one valid closed solid, 122 faces (77.2 % analytic by QA's count), driven by 88 parameters
  (86 from the scan, 2 assumed). The datum is axis-primary on the tapered spigot (cone fit, refined
  by section circles), origin on the knob top face, clock on the steel tube leaving the elbow. The
  tube bend is one sweep along a spline through 10 scanned centreline stations.
- Three loops, each checked by a fresh independent verifier with the same protocol:

  | it | Verdict | Cause | Change for the next loop |
  |---|---|---|---|
  | 1 | REVISE | scan inside the modelled bushing window pockets | window and tip bore depths set to scan lower bounds |
  | 2 | REVISE | tube bend, lever perimeter and bushing hub off | bend on the scanned centreline, lever round 1.2 → 1.946, tip neck |
  | 3 | REVISE → HALT (loop limit) | Z4 scan→CAD p95 0.301 from an unmodelled collar on the bushing top | owner: "Kabul et, teslim et" |

- Final gate (it3), from [`gate.json`](../../evals/real-runs/OD-S02/gate.json):

  | Measure | p95 / max (mm) | Result |
  |---|---|---|
  | scan→CAD, torn flash masked (M1) | 0.236 / 0.737 | pass (masked only) |
  | scan→CAD, unmasked | 0.312 / 4.518 | miss (torn rubber flash) |
  | observable CAD→scan | 0.766 / 2.601 | miss |
  | Z1 rod, Z2 tube, Z3 lever zones | ≤ 0.229 / ≤ 0.693 | pass (Z1, Z2 CAD→scan with mask M2) |
  | Z4 bushing + tip, scan→CAD | 0.301 / 0.737 | miss by 0.001 |
  | Z4 bushing + tip, CAD→scan | 1.063 / 2.602 | miss |

- The CAD→scan misses come from CAD surface the scanner never saw: the bushing window floors, the
  tip bore and the 33 scan holes. That cannot be fixed by geometry. The Z4 scan→CAD miss is the
  bushing-top collar, declared as limitation L6.
- ICP correction 0.053° / 0.059 mm. The datum audit is outside the reference with the
  normals-eigen method but agrees with the section-circle cross-check (report-only).
- Official verdict `BAND_NOT_MET`, accepted for delivery by the owner (record `ACCEPT-BAND`, gate
  `34a11505e84d`). The fresh-process reproducibility check passed.

## Records

The run's records are in [`evals/real-runs/OD-S02/`](../../evals/real-runs/OD-S02/):

- Delivery report with the full parameter table, frames and limitations:
  [`README.md`](../../evals/real-runs/OD-S02/README.md).
- Verdict: [`VERDICT.md`](../../evals/real-runs/OD-S02/VERDICT.md) and
  [`gate.json`](../../evals/real-runs/OD-S02/gate.json). Deviation overlay:
  [`overlay.png`](../../evals/real-runs/OD-S02/overlay.png).
- [`DECISIONS.md`](../../evals/real-runs/OD-S02/DECISIONS.md) (regime, part class, HALT and
  acceptance) and [`MODELING_PLAN.md`](../../evals/real-runs/OD-S02/MODELING_PLAN.md).

The skill defects and lessons this run surfaced (8, of which 3 are fixed on this branch: axis-datum
options in `align.py`, the watertight CAD STL check in `export_frames.py`, and the `package_zip.py`
size rules) are in [`evals/real-runs/OD-S02.md`](../../evals/real-runs/OD-S02.md). Open questions
are in `QUESTIONS.md` section F.

## Not in the repo

The run folder lived in the working session's temporary storage and was not kept after delivery.
Only the delivery zip given to Ikbal (`OD-S02_steam-rod_RE_BAND_NOT_MET_2026-09-28.zip`, 17.9 MB)
holds these files, so this example cannot be rebuilt from the repo alone:

- The STEP files `build/OD-S02_steam-rod_datum.step` and `build/OD-S02_steam-rod.step`, and the
  CAD STL.
- The editable intent `build/model.py` and `measure/params.json`, plus the measurement scripts,
  figures and the intake card.
- The earlier iterations (`_it1_SUPERSEDED/`, `_it2_SUPERSEDED/`).
- The rest of `qa/`: registration, deviation JSON, zone and attribution probes, datum audit, step
  check and hash freeze. Large regenerable intermediates were left out of the zip and are listed
  in its `PACKAGE_INDEX.md`.
- The input scan and the two photos.

Adding the zip's `deliverables/` and `source/` folders here (with the scan and photos) would make
the example complete.
