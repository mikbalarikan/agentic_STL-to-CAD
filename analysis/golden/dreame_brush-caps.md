# dreame_brush-caps — evidence extraction

Base path: `golden-examples/dreame_brush-caps/` (abbreviated `GE/` below). The record's README is in Turkish; quotes are translated.

## 0. Record inventory

**Method-bearing:**
- `GE/README.md`: method (5 steps), feature trees with measured→chosen values for both parts, deviation table, artefact list, assumptions.
- `GE/MANIFEST.json`: file list; excluded raw scans (91.6 MB / 249.5 MB) with decimation provenance (`#excluded[0].decimated_copy`, `#excluded[2].decimated_copy`); excluded NX `.prt` files.
- `GE/report/intake.json`: raw scan stats (faces, bodies, watertight, top facets, working-copy decimation).
- `GE/report/screw_alignment.json`, `GE/report/snap_alignment.json`: F00 datum transforms and fit residuals.
- `GE/report/screw_params.json`, `GE/report/snap_params.json`: final parameter dictionaries `P`.
- `GE/report/screw_build_log.txt`, `GE/report/snap_build_log.txt`: per-feature OK/FAILED log of the fillet/chamfer operations.
- `GE/report/screw_fastgate.json`, `GE/report/snap_fastgate.json`: in-house KD-tree two-way deviation (600k/300k samples).
- `GE/report/screw_official_gate.json`, `GE/report/snap_official_gate.json`: "oguz-re-deviation-report-v0" gate (50k samples, limits, overall_pass).
- `GE/report/snap_masked_gate.json`: per-region artefact masks and the masked scan→CAD statistics.
- `GE/report/source/*.py`: intake, datum, align, build_screw, build_snap, frames, fastgate, overlay (see §11).
- `GE/dreame_brush_screw_cap.log`, `GE/dreame_brush_snap_cap.log`: Siemens NX 2206 STEP import logs (independent validity check).
- `GE/report/views/*.png`: overlays, deviation maps, hmaps, polar/rz plots, hook profiles, final renders (visual evidence).

**Pure outputs:** `GE/dreame_brush_*_cap.step` (STL frame), `GE/dreame_brush_*_cap_datum_frame.step` (datum frame), `GE/dreame_brush_*_cap_cad.stl`, and `GE/dreame_brush_*_cap_scan_decimated.stl` (inspection-only stand-ins for the excluded raw scans).

## 1. Part class and geometry type

| | Screw cap | Snap cap |
|---|---|---|
| Function | Brush screw cap: pentagon body with a double-D drive hole, web bore and counterbore (`GE/README.md` screw table F01–F09) | Snap-on cap: annular plate with 3 leg+hook snap features, 4 conical cups, flat cut (`GE/README.md` snap table F01–F06) |
| Material/process | not recorded (README calls the bands "consumer plastic", `GE/README.md` deviation section) | same |
| Geometry class | mixed: prismatic (pentagon, 30° chamfer planes) + turned (disc, bores) | mostly turned (revolved plate/legs) + prismatic cuts (flat, ramp plane) |
| Raw scan envelope | 10.19 × 10.49 × 5.59 mm (`GE/report/intake.json#dreame_brush_screw_cap.extents`) | 25.28 × 26.78 × 12.77 mm, including scanner table (`GE/report/intake.json#dreame_brush_snap_cap.extents`) |
| CAD envelope (datum frame) | total height 5.12, corner Ø10.90 (`GE/README.md` screw table; `GE/report/screw_params.json`) | Ø23.73 OD, z −1.84 … +6.25 (`GE/report/snap_params.json`) |
| Volume | 269.1 mm³ (`GE/README.md`) | 454.1 mm³ (`GE/README.md`) |
| Symmetry | 5-fold (pentagon, 5 dimples) (`GE/report/source/build_screw.py:39,69`) | no rotational symmetry: legs at 60°/150°/−60°, "NOT equally spaced, measured"; cups at 60/150/−60/−140° (`GE/README.md` snap F04/F05) |
| Scan mesh | 1,831,231 faces, not watertight, 104 bodies (`GE/report/intake.json`) | 4,990,880 faces, not watertight, 5 bodies (`GE/report/intake.json`) |

## 2. Stages actually run, in order

1. Intake: load both scans, record stats, and write 300k-face (`_work`) and 60k-face (`_lite`) decimated working copies → `report/intake.json` (`GE/report/source/intake.py:40-53`).
2. Dominant-plane survey: normal clustering, offset clustering and RANSAC → `<name>_planes.json`, which is not in the record (`GE/report/source/datum.py:63-76`).
3. F00 datum: level on the plane, origin on the bore, clock → `report/*_alignment.json` plus the aligned meshes and the section/rz/theta-r plots (`GE/report/source/align.py`). The output PNG names in the code (`*_sections_xy.png`, `*_rz.png`, `*_theta_r.png`) only partly match the files kept (`screw_rz.png`, `snap_raw_rz.png`).
4. Sections and fitting: 25 Z stations plus radial half-plane sections, (r,z) and (θ,r) density maps, least-squares circle/line fits (`GE/README.md` method step 2). Evidence: `report/views/*_hmap_up.png`, `*_hmap_down.png`, `screw_polar.png`, `screw_bore_loops.png`, `snap_hook_profiles.png`. The scripts that made the hmap, polar and hook-profile plots are not in `report/source/`.
5. Intent rounding → parameter dictionaries `report/*_params.json` (`GE/README.md` step 3).
6. Rebuild in build123d → `screw_datum.step`/`snap_datum.step`, then `frames.export_frames` writes the datum-frame STEP, the STL-frame STEP and the `_cad.stl` (`GE/report/source/build_screw.py:103-109`, `build_snap.py:79-85`, `frames.py:14-21`).
7. Fast gate: KD-tree two-way deviation plus the deviation maps `*_dev_s2c.png` and `*_dev_c2s.png` → `report/*_fastgate.json` (`GE/report/source/fastgate.py`). The snap run used a table exclusion at z < −1.75 (`GE/report/snap_fastgate.json#table_excluded_z`).
8. Section overlays (CAD red on scan black) → `report/views/*_overlay.png` (`GE/report/source/overlay.py`).
9. Snap only: region masking of scan artefacts → `report/snap_masked_gate.json`. The producing script is not in the record.
10. Official gate "oguz-re-deviation-report-v0" (50k samples, both directions) → `report/*_official_gate.json`. The tool is not in the record.
11. Final renders → `report/views/*_cad_final_*.png`.
12. NX STEP import check on 20-Sep-2026: 1 solid, 0 validity faults, 0 sheet bodies for both parts (`GE/dreame_brush_screw_cap.log:100-106`, `GE/dreame_brush_snap_cap.log:99-105`).

## 3. Datum / alignment method

Code: `GE/report/source/align.py` (uses `ransac_plane` from `datum.py:7-25`). Outputs are recorded in `alignment-v2-lite` schema.

1. **Largest body kept.** Scan fragments are dropped with `m.split` + max faces (`align.py:45-46`).
2. **Primary datum (levels the part).** The code picks faces whose normals are within 10° of an approximate normal given on the command line, takes an area-weighted histogram of their offsets (0.1 mm bins), and selects the peak bin ±0.15 mm. It then runs RANSAC (tol 0.05, 300 iterations, seed 0), widens to faces within 2·tol, and refines with SVD (`align.py:21-37`). The plane is rotated to +Z and translated so it sits at z = 0 (`align.py:49-53`).
   - Screw: top disc face. 19,219 faces, area 33.09 mm², rms 0.0072 mm, max 0.055 mm (`GE/report/screw_alignment.json#primary_plane`).
   - Snap: plate top face. 26,360 faces, area 187.84 mm², rms 0.0293 mm, max 0.078 mm (`GE/report/snap_alignment.json#primary_plane`).
   - README says "largest flat face" (`GE/README.md` method step 1). The code actually uses the peak-area offset bin near a user-supplied approximate normal.
3. **Origin (pins X/Y).** Z-sections at 25 stations; closed loops are Kåsa circle-fitted and filtered by a radius hint ± tolerance, fit rms and a z window. The origin is the median centre (`align.py:55-84`).
   - Screw: 10 stations, r_mean 1.873 (`GE/report/screw_alignment.json#bore`).
   - Snap: 2 stations, r_mean 7.005 (`GE/report/snap_alignment.json#bore`).
   - README claims centre scatter "< 0.01 mm" (`GE/README.md` step 1). The printed centre_std is not stored in the JSON.
   - `tilt_deg` is hard-coded to 0.0 (`align.py:79`). Bore-axis tilt against the plane normal was **not measured**: the frame's Z axis is the plane normal, not a fitted bore axis.
4. **Clocking (secondary).**
   - Screw uses mode `pent@zc`: a 5-fold phase fit of the r-peaks of the largest section loop, then the flat centre is rotated to +X (`align.py:99-104`). clock −34.23° (`GE/report/screw_alignment.json#clock_deg`).
   - Snap uses mode `flatmin@zc`: the angle of minimum radius (the flat cut) is rotated to +X (`align.py:96-97`). clock −42.19° (`GE/report/snap_alignment.json#clock_deg`).
5. **Transform.** `T = Rz·T3·T2·T1` (scan → datum), `scale_factor` 1.0, stored as `matrix_4x4` (`align.py:108-117`). The delivered STL-frame STEP applies inv(T), re-orthonormalised by SVD (`frames.py:8-12`). The datum-frame STEP is the body as built (`frames.py:16`).
6. **Named frames.**
   - Screw: top flat z = 0, bore axis = Z, pentagon-flat normal = +X.
   - Snap: plate top z = 0, bore axis = Z, flat-cut normal = +X.
   - Source: `GE/README.md` deliverables table.
7. **Consistency check (decimated, inspection only; mine).** I applied `matrix_4x4` to the delivered `_cad.stl`, giving bbox z 0 … −5.12 (screw) and −1.84 … 6.25 (snap). This matches the datum-frame parameters, so the STL-frame deliverable is the exact inverse of the recorded T. I could not load the `*_datum_frame.step` files: build123d is not installed here.
8. No independent datum audit exists (RE_SPEC's ≤0.3° / ≤0.15 mm audit). The official gate JSONs record `registration_converged: true` (`GE/report/*_official_gate.json#registration_converged`), which suggests the official tool did its own registration. Its method is not recorded.

## 4. Measurement methods

| Method | Tool/function | What | Result | Source |
|---|---|---|---|---|
| Plane RANSAC + SVD | `datum.ransac_plane`, `align.level_transform` | datum faces | rms 0.007 (screw), 0.029 (snap) | `GE/report/*_alignment.json` |
| Kåsa circle fit on Z-section loops | `align.fit_circle` | bore centre/radius | r 1.873 (screw, 10 st.), 7.005 (snap, 2 st.) | `GE/report/*_alignment.json#bore` |
| Pentagon phase (5-fold fold of r-peaks) | `align.py:99-104` | clocking | −34.23° | `GE/report/screw_alignment.json` |
| Min-radius angle | `align.py:96-97` | flat clocking | −42.19° | `GE/report/snap_alignment.json` |
| Z-station sections (25) + radial half-plane sections | trimesh `section` | profiles | tabulated measured values (see §5) | `GE/README.md` method step 2 |
| (r,z) / (θ,r) density maps | `align.py:128-141`, `hist2d` | profile/pattern | images | `GE/report/views/screw_rz.png`, `snap_raw_rz.png`, `*_hmap_*.png`, `screw_polar.png` |
| LS line/plane fit | not in source | snap ramp plane | z = −1.402 + 0.0835(x − 7.714), 4.77°, rms 0.07 | `GE/README.md` snap F02; `GE/report/snap_build_log.txt:1` |
| LS line fit | not in source | snap flat cut | x = 8.93, rms 0.008 | `GE/README.md` snap F03 |
| Dimple depth profile | not in source | screw finger dimples | depth 0.06 @ z −1.0, 0.19 @ −2.5, 0.23 @ −3.0 | `GE/README.md` screw F05 |
| Hook radial profiles per leg | not in source | snap legs/hooks | hook r 12.43–12.55; 150° leg ~0.1 mm further out | `GE/README.md` snap F04, assumptions; `GE/report/views/snap_hook_profiles.png` |
| Calipers | — | — | **none**: "No caliper measurement; all dimensions scan-authority" | `GE/README.md` method step 3, assumptions |
| Photos | — | — | not recorded | — |

## 5. Design-intent rounding

All values are scan-derived. README says rounding was kept within 0.01–0.05 mm, inside scan noise ≈0.02–0.05 (`GE/README.md` step 3, assumptions).

| Part | Feature | Measured | Chosen | Rule used | Source |
|---|---|---|---|---|---|
| screw | pentagon apothem | 4.48–4.52 | 4.50 | round to 0.05 / mid-range | `GE/README.md` F01 |
| screw | corner turn radius | 5.43–5.46 | Ø10.90 | round | `GE/README.md` F02 |
| screw | bottom chamfer angle | 29–30° from vertical | 30° | standard angle | `GE/README.md` F03 |
| screw | chamfer corner fillet | ρ 1.05–1.19 | R1.15 | mid-range | `GE/README.md` F03 |
| screw | disc base r | 4.36 | 4.38 @ z −0.45 | not stated | `GE/README.md` F04 |
| screw | disc top r | 3.90–3.95 | 3.95 @ z 0 (≈45°) | not stated | `GE/README.md` F04 |
| screw | dimple | depth profile (§4) | R14 cylinder, tilt 5.15° | fit to profile, "≤0.05 mm error" | `GE/README.md` F05, assumptions; `GE/report/screw_build_log.txt:4` |
| screw | double-D arc r | 1.949 | Ø3.90 | round | `GE/README.md` F06 |
| screw | double-D flats | ±1.63/1.65 | 3.28 A/F, parallel to pentagon flat | symmetry + parallelism | `GE/README.md` F06 |
| screw | web bore r | 1.04 | Ø2.08 | exact ×2 | `GE/README.md` F07 |
| screw | counterbore r | 2.04–2.05 | Ø4.10 | round | `GE/README.md` F08 |
| snap | bore r | 7.002 | Ø14.00 | round to integer | `GE/README.md` F01 |
| snap | OD r | 11.865 | Ø23.73 | no rounding (×2) | `GE/README.md` F01 |
| snap | flat fillet | 2.5–3.0 | R2.75 | mid-range | `GE/README.md` F03 |
| snap | hook outer r | 12.43–12.55 | 12.48 | mid-range | `GE/README.md` F04 |
| snap | legs | 3 legs, 150° leg ~0.1 mm further out | identical legs | pattern/identity assumption | `GE/README.md` assumptions |
| snap | leg angles | measured | 60°, 150°, −60° (not equal) | kept as measured | `GE/README.md` F04 |
| snap | cup PCD r | 8.81–9.02 | 8.90 (common PCD) | equalise | `GE/README.md` F05, assumptions |
| snap | cup top/bottom Ø | 3.04 / 2.76 | same; depth 0.43 | as measured | `GE/README.md` F05; `GE/report/snap_params.json` |
| snap | ramp | ±0.07 undulation | single plane | simplify | `GE/README.md` assumptions |

## 6. Feature tree

**Screw** (`GE/report/source/build_screw.py`, params `GE/report/screw_params.json`). Code comments and log numbering differ from the README's F-numbers; README numbers are in brackets.
1. F01 pentagon prism `pent_apothem` from `z_bot` to `z_pent` (`:26-28`).
2. F02 ∩ cylinder `corner_dia` (`:29-31`).
3. F03 taper body: box minus 5 rotated half-spaces at `chamfer_angle_deg` from `chamfer_start_z`, corner edges filleted `chamfer_corner_fillet`, then intersected with the body (`:32-49`).
4. F04 revolved disc cone `disc_r_base`→`disc_r_top`, union, top edge fillet `disc_top_fillet` (`:50-59`).
5. F05 5× tilted cylinder cut `dimple_R`, tilt derived from `dimple_depth_at_z3` (`:60-71`).
6. F06 double-D cut (Circle ∩ Rectangle) extruded down to `dd_bottom_z` (`:72-75`).
7. F07/F08 web bore `web_bore_dia` through, counterbore `cb_dia` from below to `web_bot_z` (`:76-79`).
8. "F09" [README F07] web edge fillets `web_fillet_top`/`web_fillet_bot` (`:80-86`).
9. "F10" [F08] counterbore chamfer `cb_chamfer` (`:87-92`).
10. "F11" [F09] bottom outer fillet `bottom_fillet` (`:93-98`).
11. `clean()`.

Result: 56 faces, 1 solid (`GE/README.md`; `GE/dreame_brush_screw_cap.log:26`).

**Snap** (`GE/report/source/build_snap.py`, params `GE/report/snap_params.json`):
1. F01 revolve of the 7-point (r,z) profile: `bore_dia`, `od`, `inner_bot_z`, `outer_bot_z`, step `step_r0`/`step_r1`, bore chamfer (`:23-28`).
2. F02 underside ramp: box slab tilted by atan(`ramp_slope_dz_dx`) through `ramp_z_at_x`, cut (`:29-36`).
3. F03 flat cut at `flat_x`, 2 vertical fillets `flat_fillet` (`:37-43`).
4. F06a OD/flat top-edge fillet `od_top_fillet`, applied **before** the legs (`:44-48`).
5. F04 leg+hook: one 10-point (r,z) profile revolved ±`leg_half_angle`, inner-top fillet `hook_inner_fillet`, unioned at `leg_thetas` (`:50-64`).
6. F05 4× cone-frustum cup cuts at `cup_r_pos` and `cup_thetas` (`:65-69`).
7. F06b bore top fillet `bore_top_fillet` (`:70-75`).
8. `clean()`.

Result: 63 faces (`GE/README.md`; `GE/dreame_brush_snap_cap.log:26`). Instances are made with explicit loops of `Rot`, not `PolarLocations`: the angles are unequal, and the screw uses `72*k` (`build_screw.py:39,69`).

Every fillet/chamfer is wrapped in try/except and logs OK or FAILED. Both final logs show all OK (`GE/report/*_build_log.txt`).

## 7. Gates run, with actual numbers

Band: p95 ≤ 0.30, max ≤ 0.80 mm, from the "repo `re-deviation` gate, consumer plastic" (`GE/README.md` deviation section; `GE/report/*_official_gate.json#limits`). This equals the baseline skill's consumer-plastic band (`baseline/skills/stl2step-build123d/SKILL.md:87`).

| Gate | Threshold (origin) | Measured | Result | Source |
|---|---|---|---|---|
| Screw official scan→CAD (50k, full-res raw scan) | p95 ≤0.30, max ≤0.80 | rms 0.0426, p95 0.0851, max 0.2448 | PASS | `GE/report/screw_official_gate.json#scan_to_cad` |
| Screw official CAD→scan (50k) | same | rms 0.0384, p95 0.0757, max 0.2683 | PASS | `#cad_to_scan` |
| Screw official overall | — | `overall_pass: true`, no exclusions | PASS | `GE/report/screw_official_gate.json` |
| Screw fastgate s2c (600k) / c2s (300k) | informal | p50 0.0246, p95 0.0860, p99 0.132, max 0.246 / p50 0.0212, p95 0.0750, max 0.269 | consistent | `GE/report/screw_fastgate.json` |
| Snap official scan→CAD (50k) | p95 ≤0.30, max ≤0.80 | rms 0.0851, **p95 0.1570**, **max 1.2260** | p95 within band, **max FAIL** | `GE/report/snap_official_gate.json#scan_to_cad` |
| Snap official CAD→scan (50k) | same | rms 0.0446, p95 0.0871, max 0.2729 | PASS | `#cad_to_scan` |
| Snap official overall | — | **`overall_pass: false`**, `exclusions: []` | **FAIL** | `GE/report/snap_official_gate.json` |
| Snap fastgate s2c (600k, table z<−1.75 & up-normal excluded) | informal | p50 0.0326, p95 0.1713, p99 0.363, max 1.246 | max over band | `GE/report/snap_fastgate.json` |
| Snap fastgate c2s (300k) | informal | p95 0.0869, max 0.279 | within band | `GE/report/snap_fastgate.json` |
| Snap masked s2c (6 artefact masks, 4.9% excluded, n 570,509) | reported, not gated | rms 0.0678, p95 0.1162, p99 0.2332, **max 1.2460** | max still over 0.8 | `GE/report/snap_masked_gate.json` |
| Per-mask stats | — | bore_edge_fuzz 1.44%, p95 0.41; OD_top_burr 0.93%, p95 0.44; hook_fringe_top 0.20%, p95 0.77; hook_underside_bridging 0.92%, p95 0.37; table_remnant 1.21%, p95 0.38; flat_corner_skirt 0.22%, p95 0.42 | — | `GE/report/snap_masked_gate.json#masks` |
| Solid validity | 1 closed valid solid | "BRep check OK", 56 / 63 faces | PASS | `GE/README.md` |
| NX import | no body faults | 1 solid, 0 faults, 0 sheet bodies (both) | PASS | `GE/dreame_brush_*_cap.log` |
| Volume | none | 269.1 / 454.1 mm³ | reported only | `GE/README.md` |
| Visual overlays | none (qualitative) | CAD red on scan black | reported only | `GE/report/views/*_overlay.png` |
| Caliper Tier-1 | — | not run (no calipers) | n/a | `GE/README.md` assumptions |

The README reports the snap result as "p95 PASS, **max FAIL**", explained by artefacts (`GE/README.md` deviation table). It lists 1.226 as the max even after masking: "the only remaining 1.2 mm deviation after masking is a floating scan flap … 315 of 570k points > 0.8 mm" (`GE/README.md` artefact list, last bullet). The README also calls the s2c row "table plane excluded", but the official JSON lists `exclusions: []` (see Questions).

The deviation maps are unsigned |dev|, clipped at 0.3 (`fastgate.py:56-58`). `GE/report/views/snap_dev_s2c.png` shows the red zones at the bore top edge, the OD top edge, the hook undersides and a large table remnant near the +X flat (bottom view).

My own inspection (**decimated, inspection only**) used a KD query of decimated-scan vertices against 1.5M CAD surface samples, with no masking or largest-body filter. Screw: p50 0.027, p95 0.089, max 0.258, which agrees with the official numbers. Snap: p95 0.468, max 1.263, inflated by the unfiltered table and fragments. These are not grades.

## 8. Iterations

No iteration history is recorded: no dated versions and no REVISE/FAIL log. Indirect evidence only:
- Snap gating escalated in three steps. (1) The fast gate added a table exclusion by z and up-normal (`fastgate.py:30,36-38`; `GE/report/snap_fastgate.json#table_excluded_z` −1.75). (2) Six artefact masks were added afterwards (`GE/report/snap_masked_gate.json`). (3) The max still failed and was attributed to a floating scan flap (`GE/README.md`). The CAD was not changed to chase these, because they are scan artefacts.
- The hook-underside "bridge" was a modelling decision, not an iteration. The scanner shadow filled the gap, so the modeller built "horizontal catch face + relief groove as design intent (consistent with the raw section at leg centre)" (`GE/README.md` artefact bullet 4).
- The try/except fallbacks in the build scripts (`build_screw.py:43-48` etc.) show fillets were expected to fail sometimes. The final logs show none failed.

## 9. Declared limitations and assumptions

From `GE/README.md` "Assumptions and limits" and the artefact list:
- No calipers; all dimensions are scan-authority. Rounding to standard values only within scan noise (≈0.02–0.05 mm).
- The three snap legs are modelled identical, although the 150° leg measures ~0.1 mm further out.
- The four cups are put on a common PCD r 8.90; the −60° cup measured r 9.02.
- Screw dimples are modelled as tilted-cylinder cuts (≤0.05 mm error to the measured concavity profile).
- The snap ramp is a single plane; the scan shows ±0.07 mm undulation.
- Snap scan artefacts were not modelled:
  - scanner table sheet at z ≈ −1.83, 9.3% of raw vertices;
  - bore-edge skirt, r 6.5–6.95, 1.4%;
  - OD top burr at θ −150…−60°, 0.9%;
  - hook-underside bridge, 0.9%;
  - hook-top fringes, 0.2%;
  - table-part bridges at the flat corners, 0.2%;
  - a floating flap at the 150° leg top, r 9.8–10.7, z ≈ 6.1: the residual 1.2 mm max, 315 of 570k points > 0.8.
- Screw: a 0.2–0.25 mm local pit on the top face near θ≈70° (damage/burr), not modelled.
- **Band miss:** snap scan→CAD max 1.226 > 0.80 (`overall_pass: false`, `GE/report/snap_official_gate.json`). It is explained as scan artefacts, not waived by any recorded sign-off. The golden-examples index lists the part as "Delivered: … snap p95 0.157" (`golden-examples/README.md:17`) and does not mention the max fail.

## 10. Deviations from the baseline skill

| Topic | Project | Baseline | Helped? |
|---|---|---|---|
| Primary datum choice | Peak-area offset bin near a user-given approximate normal, then RANSAC+SVD (`align.py:21-37`) | `argmax(facets_area)` then RANSAC refine (`SKILL.md:24-34`); RE_SPEC: "functional/mating surface beats largest" (`RE_SPEC.md` §3.3) | Yes. The snap scan's raw top facets are tilted pieces (`intake.json#top_facets`), so the facet-argmax approach would likely have missed the plate. Residuals are 0.007 / 0.029 mm. |
| Datum sits at the top face, part hangs to −Z | z = 0 at top flat (`README.md` deliverables) | skill example puts the base at −Z on the floor (`SKILL.md:30-32`) | Neutral; the frame is named and documented. |
| Origin from bore | Median of Kåsa circle centres on Z-sections, filtered by r-hint (`align.py:72-80`) | Axis from normals eigen method; "bbox centre is WRONG" (`SKILL.md:39,95`); RE_SPEC forbids bbox axes (`RE_SPEC.md` §3.3) | Partly. It avoids bbox, but assumes the bore axis is parallel to the plane normal (tilt hard-coded 0, `align.py:79`). The bbox fallback still exists in code (`align.py:82`). Snap used only 2 stations. |
| Two delivered frames | Datum-frame STEP + STL-frame STEP (inverse T) + CAD STL (`frames.py`) | Skill: "apply the SAME transform to the original mesh" for the gate (`SKILL.md:34`); no dual-frame deliverable | Yes. The customer STEP drops onto the original STL; my inspection confirms the inverse is consistent (§3.7). |
| Deviation gate on full-res scan | Official gate on the full-res raw scan (1.8M / 4.9M tri) (`README.md` step 5) | "ORIGINAL (undecimated)" (`SKILL.md:75`) | Compliant. |
| Gate implementation | KD-tree over dense samples + exact triangle closest point, k=6/8 (`fastgate.py:6-22`) plus an external 50k official gate | `trimesh.proximity.closest_point` over all vertices; cKDTree-on-vertices fallback (`SKILL.md:79-80,97`) | Yes. Fast and exact enough; fast and official numbers agree within ~0.015 mm on p95 (§7). |
| Visibility / artefact masking | Scan→CAD excludes the table (z & up-normal) and 6 named geometric masks, each with its own stats; the masked max is still reported | Skill: "Worn/damaged zones: exclude by region and note" (`SKILL.md:87`); RE_SPEC Tier-2 uses a "normal-based outer-skin mask" and bands p95 ≤ 1.6, max ≤ 4.0 (`RE_SPEC.md` §4) | Honest reporting, but the official gate still FAILs max. Masks are hand-set r/z/x boxes with no recorded justification per region beyond the README prose. |
| Bands | p95 ≤0.30, max ≤0.80 | Same as skill consumer-plastic (`SKILL.md:87`); much tighter than RE_SPEC Tier-2 (1.6 / 4.0) | The project held itself to the tighter skill band. Under RE_SPEC Tier-2 the snap would pass. |
| Caliper authority | None | RE_SPEC §2 calipers authoritative; Tier-1 ±0.15 (`RE_SPEC.md` §2, §4) | Limitation; scan-only. |
| Datum audit / F00 gate / independent QA | None recorded | RE_SPEC §3.5 F00 approval, §5 datum audit ≤0.3° / ≤0.15 mm | Missing. |
| Rebuild strategy | Revolve profiles + boolean cuts; screw uses a pentagon prism ∩ cylinder ∩ tapered frustum (intersect trick in spirit) | Tri-axis extrude-intersect for prismatic, revolve for revolute (`SKILL.md:68-69`) | Yes. Few features (≈10 / 8), 56 / 63 faces. |
| Patterns | Explicit loops over measured unequal angles | "Never model pattern instances individually … PolarLocations" (`SKILL.md:70`) | Justified: the legs/cups are not equally spaced (`README.md` F04). |
| Fillets last | Mostly; snap OD fillet applied before the legs (`build_snap.py:44-48`) | "Fillets/chamfers LAST" (`SKILL.md:71`) | Worked (log OK), but it is a deviation. |
| Working-copy decimation | 300k faces fixed target (`intake.py:40-43`) | 20% if > 400k (`SKILL.md:19`) | Neutral. |
| Section overlays | Z-planes + radial half-planes (`overlay.py`) | Required deliverable (`SKILL.md:90`) | Yes. The θ=150° snap overlay shows no scan trace, only CAD (`GE/report/views/snap_overlay.png`, bottom-left panel), so that leg is not visually verified there. |

## 11. Reusable code

| file:function | What | Generality | Determinism |
|---|---|---|---|
| `GE/report/source/datum.py:ransac_plane` | RANSAC plane + SVD refine → n, c, inlier frac, rms, max | reusable as-is | seeded rng (seed 0) |
| `datum.py:dominant_planes` | normal-cluster (3°) + offset-cluster (0.08) plane candidates | reusable as-is | deterministic |
| `datum.py:axis_from_normals` | eigen revolve-axis from normals | needs generalising: the point solve is odd, with a no-op line `a - (a@d)*d*0` (`:60`); not used by `align.py` | deterministic |
| `align.py:fit_circle` | Kåsa algebraic circle fit | reusable as-is | deterministic |
| `align.py:level_transform` | primary plane from approx normal + area histogram + RANSAC | reusable as-is | seeded |
| `align.py:__main__` | full F00: level, bore origin, clock (pent / flatmin), JSON, plots | needs generalising: positional CLI args, tilt hard-coded 0, bbox fallback, plot filenames | deterministic given args |
| `frames.py:stl_frame_location`, `export_frames` | inverse alignment → OCP `gp_Trsf` (SVD-orthonormalised); write datum and STL-frame STEP + STL | reusable as-is (reads `<name>_alignment.json` from cwd) | deterministic |
| `fastgate.py:dist_to_mesh` | exact point→mesh distance via KD candidate triangles (k nearest samples + vertices) | reusable as-is; can underestimate only if the true closest triangle is not among the k candidates | seeded sampling |
| `fastgate.py:__main__` | two-way stats, table exclusion, 4-view deviation maps, bad-point (r,z) histogram | needs generalising: file-name conventions, hard-coded vmax 0.3 | seeded (rng 0, seed 0/1) |
| `overlay.py` | Z and radial half-plane overlays CAD vs scan | reusable as-is | deterministic |
| `intake.py` | stats, bodies, top facets, 300k/60k decimation | needs generalising: hard-coded Windows path and part names | decimation deterministic (assumed) |
| `build_screw.py`, `build_snap.py` | parametric feature trees driven by `P` | project-specific; patterns are reusable: try/except fillet with log, edge selection by geometry type/Z/radius, tilted-cylinder dimple, profile-revolve-over-span leg | deterministic; hard-coded Windows output path in `export_frames` call |

## 12. Lessons

1. **Level on a RANSAC plane chosen near a stated approximate normal, not the argmax facet.** Record rms/max; here rms was 0.007 / 0.029. Success: `GE/report/*_alignment.json`, `align.py:21-37`.
2. **Deliver two frames: datum frame and original-STL frame (inverse of the recorded T).** Check that the CAD STL overlays the scan. Success: `GE/README.md` deliverables, `frames.py`.
3. **Clock by a named feature with an explicit rule** (pentagon flat phase, flat-cut min radius) and store `clock_deg`. Success: `align.py:86-105`.
4. **Measure bore-axis tilt; don't assume it.** Gap: `tilt_deg` hard-coded 0 (`align.py:79`). The snap origin came from only 2 stations (`snap_alignment.json#bore`).
5. **Always run the gate two-way on the full-res scan, and read CAD→scan as a "no invented material" check.** Success: both parts' c2s p95 ≤ 0.087 (`GE/report/*_official_gate.json`; `GE/README.md`).
6. **Mask scan artefacts by named region, with per-region counts/p95/max, and report masked and unmasked numbers side by side. Never let masking turn a FAIL into PASS silently.** Limitation: `GE/report/snap_masked_gate.json`, `snap_official_gate.json#overall_pass` false.
7. **Scanner table and support removal must be explicit:** z-threshold + up-normal filter, and largest-body split before datum. Limitation: 9.3% table vertices on the snap (`GE/README.md`; `fastgate.py:36-38`; `align.py:45-46`).
8. **Measure pattern angles; don't assume equal spacing.** Model identical instances only when the measured scatter is ≤ ~0.1 mm, and declare it. Success/limitation: `GE/README.md` F04, assumptions.
9. **Fillets in try/except with a per-feature OK/FAILED log, plus an external CAD import check (NX: 0 validity faults).** Success: `GE/report/*_build_log.txt`, `GE/dreame_brush_*_cap.log`.
10. **Occluded undercuts (hook underside) should be modelled to design intent from an unoccluded section, and the resulting deviation attributed.** Limitation: `GE/README.md` artefact bullet 4, `snap_masked_gate.json#masks.hook_underside_bridging`.
11. **Radial-section overlays must be checked for missing scan traces** (the 150° panel is empty of scan). Limitation: `GE/report/views/snap_overlay.png`.
12. **Keep a fast in-house gate and an official gate; agreement between them is itself a check.** Success: screw p95 0.0860 vs 0.0851 (`screw_fastgate.json`, `screw_official_gate.json`).

## Questions

1. **Snap outcome vs index wording.** The official gate says `overall_pass: false` because max 1.226 > 0.8 (`GE/report/snap_official_gate.json`). `golden-examples/README.md:17` says only "Delivered … snap p95 0.157". Was the max miss accepted or waived, and by whom? Not recorded.
2. **Exclusions in the official gate.** README says the snap s2c row excludes the table plane ("masa düzlemi hariç"), but the official JSON lists `exclusions: []` and `regions: []`. Its p95 0.157 is lower than the fastgate's 0.171, which did exclude the table. What sampling/exclusion did the official gate use?
3. **Official gate inputs don't match the delivered files.** `scan_sha256` and `cad_sha256` in the official gates match neither the raw-scan sha256 in `MANIFEST.json#excluded` nor the included `_cad.stl` sha256. Probably aligned/datum-frame copies, but not recorded.
4. **Missing tools.** The official gate tool "oguz-re-deviation-report-v0", its registration method (`registration_converged`), and the scripts behind `snap_masked_gate.json`, the hmap/polar/hook-profile plots and the ramp/flat/dimple fits are not in `report/source/`.
5. **Bore axis and radius.** Screw bore `r_mean` 1.873 (`screw_alignment.json`) differs from the README double-D arc r 1.949 and web bore r 1.04. Which loops were used, and the centre_std behind the "<0.01 mm" claim, are not recorded.
6. **Approximate normals and CLI arguments** passed to `align.py` (approx normal, r_hint, clock mode @zc) are not recorded for either part.
7. **Relief groove numbers.** README lists the relief groove at z 4.68–4.98. Params also have `relief_z0` 4.28, used as the start of the taper in the profile (`build_snap.py:52`). Not a conflict, but the README omits it.
8. **Datum-frame STEP files** could not be opened here (no build123d/OCP). Their frame is inferred from `frames.py:16` and the README, not verified directly.
9. **Process** (injection moulding?), material, and whether photos were used: not recorded.
