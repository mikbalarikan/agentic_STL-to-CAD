# Real run: cliff bumper sensor housing (2026-09-30)

Second real run of the skills, on a new part class: a prismatic moulded housing with no round feature, made of two
pieces (clear cover and black body) and fitted with a transparent lens. Ikbal supplied the STL and five product photos,
with no calipers. Records are copied under `cliff_bumper_sensor/`. The full run folder and the delivery zip
(`cliff_bumper_sensor_RE_BAND_NOT_MET_2026-09-30.zip`) were handed over in the session. No STEP, STL or scan files are
kept in this repo.

## Inputs and decisions
- Scan: 499,218 faces, 3 bodies (0.35 % fragments removed), not watertight, datum extents 34.9 × 38.3 × 10.0 mm.
  Ikbal confirmed it is the original full-resolution export (decision card).
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm. The owner's message said "p95 plastik parça toleransı kullan".
- No calipers, so the run was scan-only and Tier-1 did not run.
- Delivery format: one zip. This was already the standing format; the owner restated it and asked that it be written
  into the repo, which is now done in `CLAUDE.md`.

## Result
- Datum:
  - Primary: the top face, cropped to the clear-cover plateau, fit rms 0.012.
  - Clock: +Y side wall normal pointed at +Y.
  - Origin: X at the lower-body rear wall, Y at the side-wall mid-plane.
  - This needed a new `align.py` feature (see below).
  - CHK-TILT reads 0.345°, which is wall draft. It is report-only.
- Measure: 67 parameters from a run-local plane/circle fitter (`measure_box.py`). The validator gave 0 warnings.
- Build:
  - One valid closed solid with 106 faces, 83 of them planar, and no ruled faces.
  - All 9 rounds were built at their target radius, in one loop.
  - The build is reproducible in fresh processes.
- Independent verify (a separate agent with its own ICP and datum audit): `BAND_NOT_MET`.
  - Masked scan→CAD p95 0.225 passes and max 1.936 fails. The max comes from a detached 684-face scan fragment that
    intake had removed but the gate grades, and from points seen through the transparent windows.
  - Observable CAD→scan is p95 0.331 / max 1.920. The misses sit on the window faces, the unscanned slot roof and
    the pocket ceiling corners.
  - Z-TOP passes, and so does Z-TAB, but only with mask M2 on the E14 blob.
  - Datum audit: 0.075° / 0.034 mm.
- Ikbal accepted delivery through a decision card. The `ACCEPT-BAND` entry cites gate `78728df9af7e`.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-intake-datum/scripts/align.py` | A plane primary could only get its X/Y origin from circle fits, so a prismatic part could not be datumed | fixed: `origin.xy_planes` and `clock.target_deg` (cookbook §3.1, §5) |
| 2 | same | A crowned or two-piece datum face tripped STOP on form error, not noise (whole top face rms 0.038 vs wall noise 0.0275) | fixed: `crop_point_raw`/`crop_radius` on plane fits |
| 3 | `stl-re-verify/scripts/datum_audit.py` | Cannot express a plane origin or a clock to +Y; verify used its own `qa/scripts/datum_audit_planes.py` | open |
| 4 | `stl-re-verify` masks/zones | Predicates are axis-aligned only, so an inclined lens plane needs a box staircase | open |
| 5 | `stl-re-verify/scripts/deviation_gate.py` | Grades the raw scan including the fragments intake removed; there is no pre-registered mask type for them. This set the scan→CAD max | open |
| 6 | baseline-skill regime | `interface_max_mm` is null, so a `functional_interface` zone is not gated; verify used `kind: whole` | open |
| 7 | `stl-re-verify/scripts/step_check.py` | Watertightness is not in its pass criteria | open |
| 8 | `stl-re-measure-intent/scripts` | Tools target turned or lobed parts; a prismatic part needed a run-local fitter | open |
| 9 | `stl-re-verify/scripts/observability.py` | Unobservable fraction 0.02 % although the slot roof and pocket corners were never scanned (same as OD-H22 #3) | open |
| 10 | `stl-re-deliver/scripts/make_manifest.py` | `decisions/accept_band.md` classified as `unclassified` | open (minor) |
| 11 | `stl-re-deliver/scripts/package_zip.py` | verify's `qa/dev_arrays*.npz` point caches were not in the regenerable list, so the zip came out at 45 MiB, over the 30 MiB `SendUserFile` limit | fixed: `*.npz` is now regenerable, and the size note is in `delivery-package.md`. The re-packaged zip is 2.4 MB and the fixture test passes 33/33 |
