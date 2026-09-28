# BUILDER REPORT: OD-E01_Power-PCB (stl-re skills @ 2e8e159, 2026-09-28)

Populated power PCB (board id PCB00572-01), scan of the component side only, 4 catalogue photos, no calipers.
Regime baseline-skill / plastic (owner: "p95 plastik parça toleransı"). Scan-only. Delivered as one fused solid.

| Iteration | Verify verdict | Gate scan→CAD p95 / max | Gate observable CAD→scan p95 / max | Notes |
|---|---|---|---|---|
| it1 | REVISE | 0.764 / 1.501 | 1.623 / 4.408 | five fixable geometry findings (C5 underside, J3 cavity floor, TO-220 tab hole, K2 bump, clip hook) |
| it2 | BAND_NOT_MET, owner ACCEPT-BAND | 0.763 / 1.365 | 1.599 / 4.408 | all it1 findings fixed; datum-frame scan→CAD 0.292 / 1.027 |

Numbers are copied from `gate.json` / `VERDICT_it1_REVISE.md` in this folder.

What drove the result (details in `VERDICT.md`):
- The QA ICP (sign-free normal test, 3 mm radius) lifts the CAD +0.72 mm because the invented board bottom
  matches the scanned board top; this alone fails scan→CAD p95 (QUESTIONS.md §F).
- The observable CAD→scan set counts invented faces the scanner never saw (board bottom, deep fin sides).

Method (run-local scripts in `scripts/`): seeded 0.1 mm height map of the datum-frame scan, component
segmentation (> 0.18 mm above a quadratic board surface), per-part fits (edge lines, bore walls, side walls by
area-weighted peak, per-z-bin can circles with lean, heatsink arm PCA, rounded-disc SDF for the Y-cap, 3D lead
paths), params.json (179 rows, validator clean), build123d union of 101 sub-bodies, 1233 faces, no loft/B-spline.
Builder self-check tooling: nearest-sample KD distances (trimesh proximity on the 398k-face scan was OOM-killed).
