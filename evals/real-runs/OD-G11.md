# Real run: OD-G11 portafilter (2026-09-28)

Second real run of the v1 skills (HEAD `2e8e159` + `CLAUDE.md`). Ikbal sent the scan and two photos with
"p95 plastik parça toleransı kullan" and asked for delivery as one zip of deliverables and all source files. The
records are copied under `OD-G11/` (`it1/` holds the iteration-1 verdict). The full run and zip were delivered to
the owner and are not in the repo.

## Inputs and decisions
- **Scan:** 500,182 faces, one body, not watertight (15 open loops), 183 × 110 × 113 mm raw. Ikbal confirmed it is the
  original full-resolution export (decision card).
- **Scope:** the scan is an assembly: cast cup, pressurised insert, grip + cap, screws and a wire spring. Ikbal chose
  one fused solid (decision card, `PART-CLASS`).
- **Regime:** baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm, from the owner's message. No calipers, so the run
  was scan-only.

## Result
- **Iteration 1:** one valid solid, 171 faces, 11/11 fillets OK. Verify (fresh agent) returned `REVISE`: scan→CAD
  p95 0.365 / max 2.441, observable CAD→scan p95 0.464 / max 4.984. Named causes:
  - an insert-floor trough the model lacked
  - the V-rib inner ends
  - the U-rib tip, which was a code bug
  - the lug ramp ends
  - a dropped arch-foot round
  - the wire
- **Iteration 2 (route `measure`):**
  - Six new measurements: trough, two-segment V-rib crests, lug lead-outs, arch feet, wire groove, neck/collar axes.
  - The U-rib code was fixed; one fillet was reduced and declared.
  - Verify (another fresh agent, same protocol, like-for-like) returned `BAND_NOT_MET`:
    - scan→CAD p95 **0.284** (passes) / max **1.346** (fails);
    - observable CAD→scan p95 0.378 / max 4.902 (fails);
    - over-band scan points fell from 2713 to 469.
  - The remaining misses are unscanned regions (pocket bores, insert floor inside the U rib, a grip strip) and
    declared simplifications (wire arcs, screw recesses). Verify judged that a third loop could not clear the band
    without new scan data.
- **Datum audit (report-only):** 0.0025° / 0.063 mm.
- **Acceptance:** Ikbal accepted the band miss ("tamam, band kaçarsa kabul ediyorum, teslim et"). The `ACCEPT-BAND`
  entry cites gate `0f2d41f2bdd2`.
- **Delivery:** README, MANIFEST and repro.json (reproducible) were written. The zip is 16 MB with 18 deliverables,
  183 source files and 6 large regenerable files listed but not shipped.

## Lessons (process)
- **The builder self-check must use the full-resolution scan.** A check on the 300k-face working copy read p95 0.281
  when the official number was 0.365. The same script run on every full-res vertex reproduced verify's it1 number
  exactly (0.3653) and it2's closely (0.283 vs 0.284).
- **Height-map selections bias fits.** Masking cells by a z window (e.g. `H > -41.8`) silently removed a real lower
  zone (the trough). Ring medians around a feature mixed two surfaces and produced a countersink that does not exist.
  Plot the residual map before trusting a fit.
- **The first delivery zip (77 MiB) could not be sent:** the `SendUserFile` limit is 30 MiB. `package_zip.py` now
  defaults to `--max-source-mb 5`, treats `*.npz` as regenerable and warns above 30 MiB.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-deliver/scripts/package_zip.py` | Zip exceeded the 30 MiB send limit: QA `*.npz` arrays were shipped and the regenerable threshold was 25 MB | fixed: default 5 MB, `*.npz` regenerable, size warning; `references/delivery-package.md` §Size |
| 2 | `stl-re-rebuild-build123d/scripts/export_frames.py:200` | The CAD STL is written without a watertight check. A cone face containing its apex failed BRepMesh at 0.003 mm, and export still passed with a non-watertight STL | open (workaround in `CLAUDE.md`) |
| 3 | `stl-re-rebuild-build123d/SKILL.md` Step 7 / self-check | No guidance to self-check on the full-res scan; the working-copy number misled iteration 1 | open |
| 4 | `stl-re-verify/scripts/observability.py:61,237`, `deviation_gate.py:338` | Ray chunk hard-coded (2000), not on the CLI; OOM-killed on a 15 GB box, so both verifies used a memory-only wrapper | open |
| 5 | `stl-re-verify/scripts/step_check.py:84,338` | Validity flag ignores tessellation watertightness (zero-area triangles) | open |
| 6 | `stl-re-verify/scripts/tier2_icp.py:71-72`, `_common.py:175` | ICP stop test adds degrees to mm; a rotation that rounds to 0 ends the run; default cap 60 did not converge on either iteration | open |
| 7 | `stl-re-verify/scripts/verdict.py:362` | `render` would crash on a Tier-1 row whose CAD value is None | open |
| 8 | `stl-re-intake-datum/scripts/align.py:404` | STOP on a 0.4 µm tie (same as OD-H22 #4) | open (self-referential noise path used again) |
| 9 | `stl-re-intake-datum/scripts/datum_fit.py` CLI | Negative vectors must be passed as `--flag=-x,y,z` | open (in `CLAUDE.md`) |
| 10 | `stl-re-deliver/scripts/make_manifest.py` | `decisions/accept_band.md` classified `unclassified` although `decisions/` is the required home of acceptance evidence | open |
