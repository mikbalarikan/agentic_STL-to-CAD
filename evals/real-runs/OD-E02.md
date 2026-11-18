# Real run: OD-E02 DeLonghi control button board (2026-09-28)

The second real run of the v1 skills on a part with no golden record. Ikbal supplied a scan and two
product photos, with no calipers, and asked for "p95 plastik parça toleransı" and one zip holding every
source file. The small records are copied under `OD-E02/`. The full run folder, with the STEP files, went
out in the delivery zip.

## Inputs and decisions
- Scan: 586,137 faces, one body, not watertight (23 open loops), 71 × 72 × 44 mm raw, mean edge 0.247 mm.
  Ikbal confirmed it is the original full-resolution export (question card).
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm. It comes from the owner's message and is
  recorded in `DECISIONS.md` before any gate existed.
- Scan-only run: Tier-1 did not run and scale is not verified.
- Part: a stepped moulded housing, snap cover, connector shroud, bent tab, four latch hoops and three
  loose button caps. It is delivered as one fused solid of the assembly as scanned.

## Result
- **Datum:** the primary is the back cover floor (trimmed rms 0.022 mm). The origin is the middle button
  collar axis. The loose cap was tried as origin first and rejected: it is tilted in its bore and noisier.
- **Measure:** 120 parameters, and the validator reported 0 warnings.
  - The housing tiers turned out to be offsets of one core outline. The corner centres are constant
    across tiers and only the radius changes, so one core sketch drives every tier.
- **Build:** 374 faces, one valid closed solid. 22 fillets: 20 OK, 2 REDUCED (declared).
- **Verify:** three independent QA agents, one per iteration, all using the same protocol.

  | | it1 | it2 | it3 |
  |---|---|---|---|
  | scan→CAD p95 / max | 0.243 / 1.690 | 0.243 / 1.062 | 0.237 / 0.922 |
  | observable CAD→scan p95 / max | 0.674 / 5.119 | 0.650 / 5.358 | 0.633 / 5.422 |
  | verdict | REVISE | REVISE | BAND_NOT_MET |

- **Why the band was missed:** 98.5 % of the CAD→scan over-band points lie in openings the scanner never
  reached (the shroud interior, the shroud-to-rim slot and the screw bores).
- **Delivery:** Ikbal accepted the miss for delivery (`ACCEPT-BAND`, gate `1e9b7dcea587`). repro_check
  reported reproducible = true.

## Skill defects and lessons found (status on this branch)

| # | Where | What happened | Status |
|---|---|---|---|
| 1 | `stl-re-deliver/scripts/package_zip.py` | `qa/dev_arrays.npz` (about 18 MB per iteration) was not treated as regenerable. The 3-iteration zip came to 89 MiB, over the 30 MiB SendUserFile limit, and was not delivered | fixed: `*.npz` is regenerable; the size rule is documented in `references/delivery-package.md` (`--max-source-mb 5`) |
| 2 | `stl-re-intake-datum` STOP rule | The origin circle residual tied the circle noise floor (0.0294 vs 0.0266), the same D1 defect as OD-H22. The run used a self-referential noise floor, declared in the card | open (D1) |
| 3 | intake CHK-ENUM | Four sub-features were missed at intake and found by the builder's self-check: inner latch bosses, hoop catch ramps, cap-collar recesses, and a tilted side-collar cut | open: add "look behind every latch/hoop and inside every cap gap" to the enumeration list |
| 4 | rebuild idioms | A bottom-edge fillet on one tier ran along the tangent chain onto edges it was not meant for (OCC propagation). A coplanar union left a zero-thickness seam. Verify saw both as CAD→scan clusters | open: add to `build123d-idioms.md` (fillet before tangent junction rounds; overlap coplanar unions) |
| 5 | `stl-re-verify/scripts/deviation_gate.py` | The default batch size ran out of memory at 15 GB, so each verifier needed a batch-size wrapper | open |
| 6 | verify observability | Openings the scanner never reached still count as "observable", the same issue as OD-H22 #3. Here they held 98.5 % of the CAD→scan miss | open (OD-H22 #3) |
| 7 | measure | Scan distance at the sharp corner (r = d / 0.414) worked well as an edge-round estimator. The self-check showed 2/3 of the >0.3 mm points within 1 mm of a sharp CAD edge | lesson; candidate for `stl-re-measure-intent` |
