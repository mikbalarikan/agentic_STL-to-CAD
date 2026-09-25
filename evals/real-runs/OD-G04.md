# Real run: OD-G04 brewing gasket support (2026-09-25)

The second real run of the v1 skills, on a part with no golden record. The owner (Ikbal) supplied a
scan, four catalogue photos and "p95 plastik parça toleransı". There were no calipers. Records are
copied under `OD-G04/`. The full run folder, with the scan and STEP files, was delivered as a split
zip (`package_zip.py`, 3 parts) and is not in git.

## Inputs and decisions
- Scan: 484,578 faces, one body, not watertight, mean edge 0.241 mm. Recorded as `full` from the
  evidence (DECISIONS `OTHER`).
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm, from the owner's wording (now in
  `CLAUDE.md`).
- Datum: the plate back face (noise 0.049 mm), the cup outer-wall axis (about 270° scanned) and the
  3-tab Fourier clock. Tilt was 0.277° ± 0.136° over a short span.

## Result
- Build: one valid solid with 174 faces and 100 % analytic surfaces. There are no fillet ops: every
  round is drawn as an arc in the revolve profiles. The build took one loop.
- Before verify, the builder compared the scan to its own CAD (a consistency check, not evidence).
  That comparison found features the plan had missed: the webs on the boss-A lines, the bead on the
  lip, the stepped hub bore and the flange inner round. Its max went from 1.02 to 0.69 mm and its
  p95 from 0.29 to 0.19 mm.
- Independent verify returned `BAND_NOT_MET`, with its own ICP:
  - scan→CAD p95 0.376 / max 0.832. The verifier traces the p95 miss to its ICP pairing faces across
    the 2.3–2.6 mm walls. In the datum frame p95 is 0.218, and a diagnostic ICP with a 1 mm
    correspondence distance gives 0.194. The max comes from 3 isolated points.
  - CAD→scan observable p95 2.325 / max 4.592. This comes from regions the scanner never reached
    (the front cavity, the hub interior and the gap in the outer wall).
- The owner accepted both misses for delivery (gate `6b2ca357f5c3`, `OD-G04/accept_band.md`). The
  repro check was reproducible. The README, MANIFEST and zip were delivered.

## Skill defects found
| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-verify/scripts/tier2_icp.py:50` | The normal test ignores sign and correspondences reach 3 mm, so thin walls are matched to the opposite skin. This caused the p95 miss. | open |
| 2 | `stl-re-verify/scripts/deviation_gate.py:338` → `observability.py:61` | A fixed ray chunk of 2000 ran out of memory at about 13.6 GB. The verifier wrapped the call with chunk 50. | open |
| 3 | `stl-re-verify/scripts/observability.py` | Surfaces the scanner could see but never scanned count as observable (also OD-H22 #3). | open |
| 4 | `stl-re-verify/scripts/verdict.py` | The gap between the datum frame and the ICP frame (0.158 mm) is below its 0.30 flag threshold, so it was not flagged. | open |
| 5 | `stl-re-measure-intent/scripts/pattern_count.py` (mass signal) | Thin ribs and slots give twice the order (12 for 6 ribs, 8 for 4 slots) because each feature has two walls. The count was resolved by line fits and back-face gaps. | open |
| 6 | `stl-re-measure-intent/scripts/param_table.py:210` | A non-pattern count (for example the rib span of an arc) is refused unless its estimator says "order/FFT". It was re-expressed as angles. | open |
| 7 | `stl-re-deliver/scripts/make_manifest.py` `role_of` | `decisions/*.md` is left `unclassified`. | open |
| 8 | `stl-re-rebuild-build123d/templates/model_template.py` `find_scripts` | `repro_check` copies `build/` to a scratch folder, where the sibling lookup fails. Pass `--scripts`. | open (workaround documented in the README repro command) |
| 9 | `stl-re-deliver` | There was no zip hand-off, and zips over 30 MiB cannot be sent. | fixed: `package_zip.py` with `--split-mb` |
| 10 | CLI (all) | Negative numbers must be passed as `--flag=-x` (also OD-H22). | documented in `CLAUDE.md` |
