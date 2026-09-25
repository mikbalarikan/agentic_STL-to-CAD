# Real run: OD-S03 DeLonghi steam knob (2026-09-25)

The second run of the v1 skills on a part with no golden record. Ikbal supplied a scan and five
product photos, and asked for the p95 plastic tolerance and a zip delivery. There were no
calipers. Records are copied under `OD-S03/`; the full run and the zip lived in the session
scratchpad and were handed over as downloadable files.

## Inputs and decisions
- Scan: 363,988 faces, one body, not watertight, about 31 × 39 × 37 mm, mean edge 0.153 mm.
  Recorded as full-res by agent inference (same export profile as OD-H22), not owner-confirmed.
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm ("p95 plastik parça toleransı").
- No calipers, so Tier-1 did not run. Photos have no scale reference.
- Delivery format: one zip with every source file and deliverable (standing request, now in
  `CLAUDE.md` and `stl-re-deliver` step 6).

## Result
- Build: one fused solid (chrome cap + lever, collar, four-rib stem, threaded sleeve), 83 faces,
  volume 11,655.64 mm³, 4 fillets at target. The thread in the scan is not a uniform helix: flat
  rings at 1.231 mm pitch with a helical step at each end. It is modelled as tori plus two helical
  sweeps and declared; the real thread spec is an open owner question.
- Iteration 1 (independent verify): `REVISE`. The tessellation was not watertight because the
  rib foot touched the inner-groove torus along a line. `step_check` passed it; verify found it
  with its own tessellation probe. Routed `geometry`.
- Iteration 2: the rib foot was buried 0.5 mm, and a second defect was fixed: the bottom ramp
  cut tool left a wedge that grazed the sleeve bottom. That defect only shows at 0.1 rad angular
  tolerance. Both STEPs are watertight at 6 tessellation settings.
- Independent verify it2 (fresh agent, own ICP 0.073° / 0.024 mm, same protocol as it1):
  - scan→CAD: p95 0.150 (passes), max 2.348 (misses). 206 points in a chrome scan-skin flap
    curling inside the cap wall at a scan hole; photos show an intact wall. A smaller real miss
    (max about 1.09) sits in the stem/collar crevice, which is not rotationally symmetric.
  - Observable CAD→scan: p95 0.438 / max 2.792 (misses). Assumed pocket and bore floors that
    the scanner never reached, counted as observable (OD-H22 defect #3 again).
  - Datum audit (report-only): axis 0.02°, origin 0.02 mm. The clock reads 3.9° because of the
    vertex-count bias below.
- Verdict: `BAND_NOT_MET`. Ikbal accepted it for delivery (decision card; `ACCEPT-BAND` cites
  gate `f70ad05cf7ed`). Deliver: reproducible in two fresh runs; README, MANIFEST (193 files).
  The zip was 87 MiB, over the 30 MiB file hand-off limit, so it went out as 4 parts. A rebuild
  from the unpacked zip alone gave the same faces and volume.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-verify/scripts/step_check.py` | A non-watertight tessellation does not fail `single_valid_closed_solid`; one angular setting also hid a second defect | open |
| 2 | `stl-re-intake-datum/scripts/align.py:247-259`, `stl-re-verify/scripts/datum_audit.py` | Fourier-mass clock weights by vertex count, not area (density bias) | open |
| 3 | `stl-re-intake-datum/scripts/align.py:366`, `:102` | Axis primary crops radially only (no z window); no wall-face angle exclusion skews tilt | open |
| 4 | `stl-re-orchestrate/scripts/init_run.py:359-362` | `status` ignores the scan-only `MEASUREMENTS` entry | open |
| 5 | `stl-re-intake-datum/scripts/datum_fit.py:487` | Circle-noise measure needs a closed section loop | open |
| 6 | `stl-re-rebuild-build123d/references/strategy-catalogue.md:123`, `scripts/face_stats.py:180` | No thread guidance (3D sweeps listed as HALT class); helical sweep faces flagged as possible ruled lofts | open |
| 7 | `stl-re-verify/scripts/observability.py` | Unreached cavities count as observable (OD-H22 #3) | open |
| 8 | `stl-re-verify/scripts/verdict.py` | Verdict reason not carried into VERDICT.md (OD-H22 #2) | open |
| 9 | `stl-re-deliver/scripts/make_manifest.py` | `BUILDER_REPORT.md` and `decisions/*.md` get role `unclassified`; `_cad.stl` is "preview" | open |
| 10 | `stl-re-deliver/scripts/package_zip.py` | First version: no cad STL in `deliverables/`, wrong rebuild command, README photo link broken, no size cap | fixed: STL added, command from `repro.json#command` + `STL_RE_REBUILD_SCRIPTS`, linked photos shipped, `--max-mb` parts |
