# OD-H12 — evidence extraction

Project folder: `golden-examples/OD-H12_delonghi-dedica-pump/` (abbreviated `OD-H12/` below; every
`OD-H12/...` path means `golden-examples/OD-H12_delonghi-dedica-pump/...`).
Headline: validity/topology gates PASS, validator 13/13 PASS (circular, see §7), **the skill's own deviation
band was MISSED** (scan→CAD p95 0.448 / max 2.49 vs p95 ≤ 0.30 / max ≤ 0.80) and the miss is explained per
region in `OD-H12/README.md:21-44`. The README is in Turkish; quotes below are translated.

## 0. Record inventory

Method-bearing:
- `OD-H12/README.md` — the only narrative: input, method, deliverables, deviation table, per-region explanation, verdict, model tree, assumptions, repro commands.
- `OD-H12/report/src/build_pump.py` — full build123d model (parameter dict `P` + 6 sub-body builders + `build()`).
- `OD-H12/report/src/export_final.py` — builds, exports datum-frame and scan-frame STEP/STL, re-imports and checks → writes `export_check.json`.
- `OD-H12/report/src/gate.py` — two-way deviation gate, z-band regions, deviation-map PNG, ray-cast observability test.
- `OD-H12/report/src/ovl.py` — planar section overlay (scan blue vs CAD red) → `overlay_*.png`.
- `OD-H12/report/src/render.py` — point-splat 6-view renderer → `views_*.png`.
- `OD-H12/report/src/T1.npy`, `OD-H12/report/alignment_T1.json` — 4×4 original-STL→datum transform (the only alignment record).
- `OD-H12/report/params.json` — final parameter values (105 top-level keys; README says 104, see Questions).
- `OD-H12/report/deviation_gate.json` — gate numbers (global, per-region, observable-only).
- `OD-H12/report/expected.json`, `OD-H12/report/validator_report.json` — "oguz" validator input and 13-check result.
- `OD-H12/report/export_check.json` — STEP re-import check (solids, valid, closed, faces, volume, bbox) for both frames.
- `OD-H12/OD-H12-Pump.log` — Siemens NX 2206 STEP import log (independent-kernel import: 1 solid, 0 validation faults).
- `OD-H12/MANIFEST.json` — provenance; excluded `COMPOUND.prt`, `OD-H12-Pump_step.prt` (NX natives).

Pure outputs / evidence images: `OD-H12/OD-H12-Pump.step`, `OD-H12/OD-H12-Pump_datum.step`,
`OD-H12/OD-H12-Pump_cad.stl`, `OD-H12/OD-H12-Pump_datum.stl`, `OD-H12/report/deviation_map.png`,
`OD-H12/report/overlay_axial.png`, `OD-H12/report/overlay_radial.png`, `OD-H12/report/views_cad.png`,
`OD-H12/report/views_scan.png`. Input: `OD-H12/0_input/OD-H12-Pump.stl` (full-resolution original, 48,991,034 B,
`OD-H12/MANIFEST.json#included[24]`; not decimated).

Missing from the record: any datum-fitting script, any measurement/section/circle-fit script, any
iteration log, the validator tool itself (see Questions).

## 1. Part class and geometry type

- Part: ULKA-type vibration pump from a DeLonghi Dedica — coil + sheet-metal U-frame + plastic body + outlet tube + hose barb (`OD-H12/README.md:4`).
- Function: espresso-machine water pump (solenoid vibration pump) (`OD-H12/README.md:4`; `OD-H12/report/src/build_pump.py:1`).
- Material/process: mixed — steel sheet frame, plastic body, wound coil, screws, spade tabs, all merged into one solid by user request ("solid body") (`OD-H12/README.md:67-68`). Processes not recorded.
- Geometry class: **mixed** — revolved axial body (outlet + inlet), cylindrical coil, bent-sheet prismatic frame, prismatic terminal block, lozenge flange (`OD-H12/README.md:46-58`).
- Envelope (CAD, datum frame): 54.05 × 55.15 × 121.95 mm (`OD-H12/report/export_check.json#exports.datum.bbox_min/bbox_max`; `OD-H12/README.md:19`). Full-res scan in datum frame (my inspection, not a grade): 54.20 × 56.44 × 122.18 mm.
- Symmetry: nominal axis of revolution = pump axis +Z (`OD-H12/README.md:14`); frame roughly symmetric about X, but measured asymmetries kept (coil offset (−0.2, 0.1), screw centres (19.0, −0.3)/(−19.2, 0.15), frame x −27.2…26.85) (`OD-H12/report/params.json#coil_cx,coil_cy,screw_centers,fx0,fx1`).
- Input mesh: 979,819 triangles, not watertight, single-shell scan (`OD-H12/README.md:3`; confirmed: 979,819 faces, 493,060 vertices, `is_watertight=False`).
- Unit: STL unitless, assumed mm, not caliper-checked (`OD-H12/README.md:64`).

## 2. Stages actually run, in order

Reconstructed from README + scripts; no stage log exists.
1. Intake of scan `pipeline/tasks/OD-H12-Pump.stl` → no artefact (`OD-H12/README.md:3`; file stored as `OD-H12/0_input/OD-H12-Pump.stl`, `OD-H12/MANIFEST.json#included[24].note`).
2. Datum alignment → `T1` 4×4 → `OD-H12/report/src/T1.npy`, `OD-H12/report/alignment_T1.json`. Method code not included.
3. Measurement "from the scan: section/circle fit/normal histogram" (`OD-H12/README.md:60`) → values in `OD-H12/report/params.json`. Measurement code/outputs not included.
4. Visual comparison renders → `OD-H12/report/views_scan.png`, `OD-H12/report/views_cad.png` via `OD-H12/report/src/render.py`.
5. Build123d rebuild (`build()`) → part in datum frame (`OD-H12/report/src/build_pump.py:269-287`).
6. Export + re-import check in datum and original-scan frames → `OD-H12/OD-H12-Pump_datum.step/.stl`, `OD-H12/OD-H12-Pump.step`, `OD-H12/OD-H12-Pump_cad.stl`, `OD-H12/report/export_check.json` (`OD-H12/report/src/export_final.py`).
7. Section overlays → `OD-H12/report/overlay_axial.png` (y=0, x=0, y=10), `OD-H12/report/overlay_radial.png` (z=15, −15, −5, −55, 37, 6) via `OD-H12/report/src/ovl.py`.
8. Two-way deviation gate + regions + observability → `OD-H12/report/deviation_gate.json`, `OD-H12/report/deviation_map.png` (`OD-H12/report/src/gate.py`).
9. Validator (oguz-validator-report-v0) on `final\OD-H12-Pump_datum.step` → `OD-H12/report/validator_report.json` against `OD-H12/report/expected.json`.
10. Independent repeat of scan→CAD in the original STL frame: median 0.102 / p95 0.448 (`OD-H12/README.md:30`) — no artefact file.
11. NX import of `OD-H12-Pump.step` (STEP written 2026-09-25T09:29:54, imported 09:41) → `COMPOUND.prt`, `OD-H12-Pump_step.prt` (excluded), `OD-H12/OD-H12-Pump.log:4-13,80-108`.

## 3. Datum / alignment method

- Frame definition: pump axis = +Z (outlet −Z, inlet barb +Z); X = normal of the sheet-frame side plates; origin on the axis (`OD-H12/README.md:14`; `OD-H12/report/src/build_pump.py:3-6`).
- Primary: pump revolution axis (axis-primary part). Secondary (clocking): side-plate normal → X. Origin: "on the axis"; the Z position of the origin is not defined by a named feature in the record (Z values such as `fz0=-12.4`, `z_rear=37.65` are all offsets from an unnamed z=0).
- How the axis/plane were fitted (normal eigen-method, RANSAC, cylinder fit?) — **not recorded**. Fit residuals — **not recorded**. Scale factor / scan noise fields — **not recorded** (alignment_T1.json has only the matrix).
- Numbers: T1 (row-major, original STL → datum), rotation rows [0.6762, −0.2781, −0.6822], [0.7154, 0.0264, 0.6983], [−0.1761, −0.9602, 0.2168]; translation (−153.149, 155.874, 33.867) (`OD-H12/report/alignment_T1.json#T1_original_stl_to_datum`). det = 1.000, orthonormality error 2e-16 (my check on `T1.npy`).
- Inverse used for scan-frame export is re-orthonormalised by SVD because OCP `transform_shape` rejects near-orthonormal matrices (`OD-H12/report/src/export_final.py:17-22`).
- Residual coil offset: coil centre measured at (−0.2, 0.1) from the datum axis and deliberately **not** snapped (`OD-H12/README.md:51`; `OD-H12/report/params.json#coil_cx,coil_cy`). Datum axis presumably from the plastic body/tube; not recorded.
- Alignment-loss check: gate repeated in original STL frame gives same p95 0.448 → "no alignment loss" (`OD-H12/README.md:30`).

## 4. Measurement methods

No measurement script or per-measurement output was kept; everything below is from the README narrative, params and overlays.

| Method | Tool/function | Measured | Result | Source |
|---|---|---|---|---|
| Sections, circle fits, normal histograms | not recorded | all 104/105 params | final values only | `OD-H12/README.md:60`, `OD-H12/report/params.json` |
| Coil cylinder | circle fit (method not recorded) | coil radius varies along Z (slightly conical/wavy, ±0.1) | r 23.50–23.84 → single cylinder Ø47.30 | `OD-H12/README.md:35-36`, `OD-H12/report/params.json#r_coil` |
| Scan noise floor | "clean cylinder" self-fit (which cylinder not recorded) | intrinsic scan noise | p95 0.13 mm | `OD-H12/README.md:35` |
| Sheet thickness | partial inner face only | frame plate | 3.1 (inferred, not proven) | `OD-H12/README.md:65`, `OD-H12/report/params.json#ft` |
| Low land on terminal block | section (not recorded) | step height | 0.48 mm lower area | `OD-H12/README.md:57`, `OD-H12/report/src/build_pump.py:243` |
| Housing rotation | not recorded | terminal housing box angle | 29.6° | `OD-H12/report/params.json#hs_ang` |
| Screw head profile | "measured (r, z) profile" | dome | 8-point revolve profile | `OD-H12/report/src/build_pump.py:206-209` |
| Section overlays (visual) | `trimesh.intersections.mesh_plane` | 3 axial + 6 radial planes | images only | `OD-H12/report/src/ovl.py:13`, `OD-H12/report/overlay_*.png` |
| Photos / calipers | none | — | "no caliper measurement; all dims from scan (scan is sole authority)" | `OD-H12/README.md:6-7` |

Visual note (my reading of `OD-H12/report/overlay_radial.png`, z=−55 panel): the outlet-tube section is visibly out-of-round relative to the CAD circle (scan inside CAD on part of the perimeter) — consistent with the outlet-tube region's residual, not discussed in the README.

## 5. Design-intent rounding

The record gives chosen values only; a measured→chosen table (required by `baseline/skills/stl2step-build123d/SKILL.md:54,90`) was **not** produced. Most values are kept at 0.05-mm resolution (e.g. r_t1 6.92, r_t2 6.78, r_t3 6.57, r_t4 6.74, r_coil 23.65), i.e. effectively unsnapped.

| feature | measured | chosen | rule used | source path |
|---|---|---|---|---|
| Coil OD | r 23.50–23.84 (taper/wave) | Ø47.30 (r 23.65) | single cylinder over a varying surface; rule not stated | `OD-H12/README.md:35-36`, `OD-H12/report/params.json#r_coil` |
| Coil centre | (−0.2, 0.1) | (−0.2, 0.1) | kept as measured, explicitly not snapped concentric | `OD-H12/README.md:51` |
| Body OD | not recorded | Ø24.0 | not stated (round value) | `OD-H12/report/params.json#r_body`, `OD-H12/report/expected.json#critical_dims` |
| Outlet nozzle OD | not recorded | Ø14.0 | not stated | `OD-H12/report/params.json#r_nozzle` |
| Step OD | not recorded | Ø20.5 | not stated | `OD-H12/report/params.json#r_s1` |
| Outlet tube steps | not recorded | Ø13.84 → 13.56 → 13.14 → 13.48 | none (0.02-mm values) | `OD-H12/README.md:48`, `OD-H12/report/params.json#r_t1..r_t4` |
| Wrench flats | not recorded | A/F 11.6 | not stated | `OD-H12/report/params.json#flat_af` |
| Inlet boss / barb | not recorded | Ø13.0 / Ø5.9, ridge Ø6.96 | not stated | `OD-H12/report/params.json#r_boss,r_barb,r_barb_ridge` |
| Sheet thickness | partial inner face | 3.1 | inferred | `OD-H12/README.md:65` |
| Core tube | not visible | Ø16 | design-intent guess (hidden) | `OD-H12/README.md:54,65` |
| Nozzle bore / barb bore depth | not visible | 7 / 12 mm | design-intent guess | `OD-H12/README.md:66` |
| Screw centres | as measured | (19.0, −0.3), (−19.2, 0.15) | not symmetrised | `OD-H12/report/params.json#screw_centers` |
| Flange hub | not recorded | r 12.05 (Ø24.1) | not stated; docstring says Ø24.4 | `OD-H12/report/params.json#dia_r_center`, `OD-H12/report/src/build_pump.py:182` |

## 6. Feature tree

All in datum frame, single final solid (`OD-H12/report/src/build_pump.py:269-287`):
1. `revolve_body()` — two closed `Polyline` half-profiles on Plane.XZ revolved about Z and unioned: outlet side (tip_z, tip_chamfer, r_nozzle/z_nozzle, r_t1..r_t4, z_t1..z_t3, z_step, r_s1, z_cone0/1, r_body) and inlet side (z_rear, r_washer, z_washer, r_boss, z_boss, r_ring, z_ring, r_barb, r_barb_ridge, z_barb1/2, z_ridge1/2, z_tip_in; two hard-coded radii 3.05, 2.95, 2.6) (`:80-128`). Cuts: nozzle bore (bore_r, bore_depth), barb bore (r_in_bore), ±X wrench-flat boxes (flat_af, flat_z0/1) (`:129-135`).
2. `+ coil()` — cylinder r_coil at (coil_cx, coil_cy), z_coil0…z_coil1, end edges filleted coil_fillet (`:138-144`).
3. `+ core tube` — cylinder r_core between inner plate faces (fz0+ft … fz1−ft) (`:272-274`).
4. `+ frame()` — RectangleRounded ring (fx0/fx1/fz0/fz1, fr_out, ft) on XZ extruded ±fy; subtract side-plate notches (notch_x/y/z), front-plate slot (slot_front_w/y0), two rear-plate slots (rear_slot_w/y0/depth) (`:147-178`).
5. `+ diamond_flange()` — hull(hub dia_r_center + 2 lobes dia_lobe_r at ±dia_lobe_x) extruded dia_z1→dia_z0; underside pocket = hull offset −pocket_rim minus body circle and screw bosses boss_r, to pocket_z (`:181-202`).
6. `+ screws()` — revolved dome profile (screw_r, screw_z1, hard-coded z stations −21.0/−20.5/−20.0/−19.2) at screw_centers; two crossed recess boxes per screw at recess_ang (`:205-225`).
7. `+ terminal_block()` — YZ profile (tb_*) extruded across X; fillet tb_fillet on selected end edges; lowered land (tb_step_*); tab pockets (tabA/tabB, tabpk_*); spade tabs (tab_*); sloped rib (rib_x, hard-coded YZ polyline); rotated housing box (hs_cx, hs_cy, hs_ang, hs_l, hs_w, hs_z1) with vertical-edge fillet hs_fillet; housing top closed ("pocket not resolved by scan") (`:228-266`).
8. `− U-windows` — two slots win_w at ±win_y through flange + hub, win_z0…win_z1, cut last "because the hub fills them otherwise" (`:279-286`).

Fillets: coil ends, terminal-block edges, housing edges — done inside sub-bodies, not globally last. Result: 213 faces, planes 139 / cylinders 48 / cones 24 / tori 2 (`OD-H12/OD-H12-Pump.log:26,35,37,53,67`).

## 7. Gates run, with actual numbers

All deviation numbers are against the **full-resolution** scan (n = 493,060 = all vertices of `OD-H12/0_input/OD-H12-Pump.stl`), datum frame, unsigned distances.

| gate | threshold (origin) | measured | PASS/FAIL | source |
|---|---|---|---|---|
| scan→CAD global | p95 ≤ 0.30, max ≤ 0.80 (skill consumer-plastic band, `baseline/skills/stl2step-build123d/SKILL.md:87`; quoted `OD-H12/README.md:32`) | RMS 0.217, mean 0.152, p95 **0.448**, p99 0.674, max **2.49** | **FAIL** (declared "NOT MET") | `OD-H12/report/deviation_gate.json#scan_to_cad`, `OD-H12/README.md:25,32-33` |
| scan→CAD outlet tube z<−24.5 | same band | p95 0.389, max 1.57 (n 74,246) | FAIL (p95, max) | `#scan_to_cad_regions."outlet_tube z<-24.5"` |
| scan→CAD front body/flange −24.5…−9.6 | same band | p95 0.489, max 1.83 (n 97,832) | FAIL — worst region | `#scan_to_cad_regions."front_body -24.5..-9.6"` |
| scan→CAD coil+frame −9.6…37.7 | same band | p95 0.445, max 2.49 (n 296,001) | FAIL | `#scan_to_cad_regions."coil+frame -9.6..37.7"` |
| scan→CAD inlet z≥37.7 | same band | p95 0.273, max 1.23 (n 24,981) | p95 PASS, max FAIL | `#scan_to_cad_regions."inlet z>=37.7"` |
| CAD→scan raw (300k CAD samples) | same band | RMS 1.61, p95 3.43, p99 5.45, max 9.03 | FAIL (explained as unobservable surfaces) | `#cad_to_scan`, `OD-H12/README.md:27` |
| CAD→scan per region (raw) | — | outlet p95 0.571; front 0.670; coil+frame 3.62 (max 9.03); inlet 1.63 | reported | `#cad_to_scan_regions` |
| CAD→scan observable only | none set | RMS 0.354, p95 0.567, p99 1.56, max 8.65 (n 14,870 of 20k subsample) | not gated; >0.30 | `#cad_to_scan_observable`, `OD-H12/README.md:26` |
| Unobservable CAD fraction | — | 25.65 % | reported | `#cad_to_scan_unobservable_fraction`, `OD-H12/README.md:41` |
| Scan→CAD in original STL frame | — | median 0.102, p95 0.448 | "no alignment loss" | `OD-H12/README.md:30` (no file) |
| Points > 1.2 mm | — | 0.16 % | reported | `OD-H12/README.md:37` (no file) |
| STEP re-import, both frames | 1 solid, valid, closed (script abort rule `export_final.py:25-26`) | 1 solid, valid, closed, 213 faces, V 114,903.3 mm³, A 29,258.9 mm² | PASS | `OD-H12/report/export_check.json#exports` |
| Independent kernel import (NX 2206) | no validation faults | 1 solid, 0 faults, 0 sheet bodies | PASS | `OD-H12/OD-H12-Pump.log:100-106` |
| Validator (oguz v0) 13 checks: closed, count, bbox x/y/z, 7 cyl Ø, length | `OD-H12/report/expected.json` tolerances (0.15–0.5 mm) | all equal to expected (bbox y 55.15 vs 55.2) | 13/13 PASS — but expected values came from the scan/CAD itself, "not independent validation" | `OD-H12/report/validator_report.json#overall_pass`, `OD-H12/README.md:70-71` |
| Surface quality (Tier-0-like) | not set | 213 analytic faces (no B-spline surfaces) | not formally gated | `OD-H12/OD-H12-Pump.log:26-67` |
| Visual | none | overlays + 6-view renders | not formally gated | `OD-H12/report/*.png` |
| Operator acceptance | — | "Operator: good result" | accepted | `golden-examples/README.md` table row |

Reproduction check (mine, full-resolution scan, same algorithm as `gate.py:8-17`, seed 0, trimesh 5.1.0): scan→CAD RMS 0.2174, p50 0.1012, p95 0.4478, max 2.4934, fraction > 1.2 mm = 0.159 % — matches `deviation_gate.json#scan_to_cad` exactly and confirms the README's 0.16 %.

For comparison only (not claimed by the project): the scan→CAD numbers would fall inside `baseline/oomwoo-re-pipeline/RE_SPEC.md:171-172` Tier-2 band (p95 ≤ 1.6, max ≤ 4.0); the observable CAD→scan max 8.65 would not.

## 8. Iterations

No iteration log, no intermediate gate results, no earlier versions kept — **not recorded**. Traces of fixes in code comments only:
- U-window cut moved to after all unions because the hub refilled it (`OD-H12/report/src/build_pump.py:279`).
- Inverse transform re-orthonormalised via SVD after OCP rejected the near-orthonormal matrix (`OD-H12/report/src/export_final.py:19`).
- Terminal housing left closed-top because the scan did not resolve the pocket (`OD-H12/report/src/build_pump.py:260`).
- Flange docstring says hub Ø24.4 while final param is Ø24.1 — suggests a later value change (`OD-H12/report/src/build_pump.py:182` vs `OD-H12/report/params.json#dia_r_center`).
- The README lists, but did not do, the next iteration to close the band: conical/lofted coil, embossed lettering, terminal-slot blades — withheld because guessing without caliper/photo is risky (`OD-H12/README.md:43-44`).

## 9. Declared limitations and assumptions

Per-region explanation of the band miss (`OD-H12/README.md:32-44`, translated):
- Verdict: "the skill's consumer-plastic band p95 ≤ 0.30 / max ≤ 0.80 mm → **NOT MET** (p95 0.448, max 2.49)."
- Scan noise: "even on a clean cylinder the scan carries p95 0.13 mm noise"; the coil surface is ±0.1 mm slightly conical/wavy (r 23.50–23.84) but one cylinder Ø47.30 was fitted.
- Outliers: only 0.16 % of points exceed 1.2 mm; clusters = shadowed inside of the flange pocket, blades inside the terminal slot, embossed lettering on the terminal block ("ULKA / 230V 50Hz"), small embossings on the sheet side plates, the screw star-recess detail — "all cosmetic/internal — deliberately not modelled."
- CAD→scan raw includes surfaces the scanner physically cannot see (gap between sheet plate and coil, hole interiors, flange pocket): 25.6 % of CAD surface classified unobservable by ray test; observable part p95 0.567.
- Region table: outlet 0.39 · front body/flange 0.49 · coil+frame 0.45 · inlet 0.27 (`OD-H12/README.md:29`).

Assumptions ("operator approval required", `OD-H12/README.md:62-71`):
- Scale: STL unitless, mm assumed (122 mm length consistent with ULKA EX5), not caliper-verified.
- Unobservable interior: sheet thickness 3.1 (partial inner face only), core tube Ø16, flange pocket depth, hole depths (outlet 7 mm, barb bore 12 mm) — "the scan does not prove these; design-intent guesses."
- Single body: user asked for "solid body" → all pump parts fused; multi-body STEP would be a separate job.
- Embossed text, cable/blade internals, screw star-recess approximated/omitted.
- Validator 13/13 PASS is not independent — expected values came from the scan; it is a topology + dimension-consistency check; "the independent evidence is the deviation gate."
- Code-level: core tube "hidden inside the coil; ties coil to frame" (`OD-H12/report/src/build_pump.py:272`) — i.e. an invented connector to make one solid.

## 10. Deviations from the baseline skill

| Topic | Baseline says | OD-H12 did | Helped? |
|---|---|---|---|
| Decimated working copy | decimate > 400k faces for work, keep original for gate (`baseline/skills/stl2step-build123d/SKILL.md:19-21`) | whether a working copy was decimated is not recorded; the gate used all 493,060 original vertices (`OD-H12/report/deviation_gate.json#scan_to_cad.n`) | gate complies |
| Datum | largest flat face primary, RANSAC, record transform (`SKILL.md:24-34`); RE_SPEC DOF ladder with named origin + fit residuals + alignment.json v2 (`baseline/oomwoo-re-pipeline/RE_SPEC.md:109-157`) | axis-primary + side-plate-normal secondary; only a bare 4×4 kept; no residuals, scale_factor, scan_noise, or named Z origin (`OD-H12/report/alignment_T1.json`) | frame is functional; the record is weaker than RE_SPEC's contract |
| Scale/units | verify against caliper (`SKILL.md:96`); scale check before datum (`RE_SPEC.md:105-107`) | assumed mm, plausibility vs ULKA EX5 only (`OD-H12/README.md:64`) | unverified; declared |
| Data authority | calipers for dimensions, scan for form (`RE_SPEC.md:87-99`) | scan is sole authority (`OD-H12/README.md:6-7`) | limits band achievability; declared |
| Snapping | snap to 0.1/0.5/1.0, concentric, symmetric, standards; log measured→snapped (`SKILL.md:51-54,90`; `RE_SPEC.md:159-164`) | mostly unsnapped 0.01–0.05-mm values; coil offset and asymmetric screws kept "as measured"; no measured→snapped table (`OD-H12/report/params.json`, `OD-H12/README.md:51`) | fits scan closer but loses intent; contradicts doctrine |
| Rebuild strategy | prismatic tri-axis extrude-intersect; revolve-then-trim (`SKILL.md:68-69`) | revolve for axial body; sub-bodies (coil, frame, flange, screws, terminal block) unioned; no extrude-intersect | sub-body union handled a multi-component assembly; face count stayed low (213) |
| Patterns | model one + PolarLocations/GridLocations (`SKILL.md:70`) | screws looped over two measured, non-symmetric centres with different recess angles (`build_pump.py:218-224`) | faithful to scan, not pattern intent |
| Fillets last | (`SKILL.md:71`; `RE_SPEC.md:162`) | fillets inside sub-bodies before union (`build_pump.py:143,242,264`) | no reported harm |
| Deviation gate algorithm | `trimesh.proximity.closest_point`, cKDTree fallback (`SKILL.md:79-97`) | KD-tree on 3 M surface samples → exact point-triangle on k=8 candidate triangles (`gate.py:8-17`) | fast on 1 M-triangle scan; reproduced exactly |
| Per-region reporting | "per-region notes" (`SKILL.md:90`) | fixed z-bands along axis, both directions (`gate.py:30-37`) | made the miss explainable |
| Occluded surfaces | RE_SPEC: interior/occluded buckets reported, not gated (`RE_SPEC.md:174`) | new ray-cast observability test (7 rays in a 60° cone, 60 mm) to split CAD→scan into observable/unobservable (`gate.py:57-84`) | yes — turned a 3.43 p95 into an explained 0.567; not in the build123d skill |
| Band honesty | "exclude worn zones by region and note" (`SKILL.md:87`); honesty rule HALT with gap + options (`RE_SPEC.md:178-180`) | declared NOT MET, gave options, did not loosen band (`OD-H12/README.md:32-44`) | matches RE_SPEC honesty rule |
| Deliverables | STEP+STL, param table, deviation report, section overlays (`SKILL.md:89-90`) | all present plus scan-frame STEP (overlays on scan) and datum-frame STEP (`OD-H12/README.md:11-16`) | dual-frame delivery is an addition |
| Independent re-import | not in skill | STEP re-imported (`export_final.py:37-50`), NX import 0 faults (`OD-H12-Pump.log:100-106`) | extra evidence of validity |
| Anti-lego / Tier-0 | analytic surfaces, face count ~hundreds (`RE_SPEC.md:263-270`) | 213 faces, all plane/cylinder/cone/torus (`OD-H12-Pump.log`) | complies |
| Photos / intent | photos authoritative for intent (`RE_SPEC.md:96-97`) | no photos; cosmetic vs real decided from scan only | cosmetic classification unverified |

## 11. Reusable code

| file:function | what it does | generality | determinism concerns |
|---|---|---|---|
| `OD-H12/report/src/gate.py:dist_to_mesh` (`:8-17`) | point→mesh distance: KD-tree on n_samp surface samples, exact closest point on k candidate triangles | reusable as-is | seeded (`seed=0`); approximate — true nearest triangle may be outside the k candidates (overestimates only); memory ≈ n·k triangles |
| `OD-H12/report/src/gate.py:stats` (`:19-20`) | rms/p95/p99/max/mean/n | reusable as-is | none |
| `OD-H12/report/src/gate.py` region split (`:30-37`) | per-band stats along datum Z | needs generalising (hard-coded z bands) | none |
| `OD-H12/report/src/gate.py` observability (`:57-84`) | ray-cast CAD points (d>0.5) along normal + 6 rays at 60°; all hit → unobservable | needs generalising (60°, 0.5, 20k subsample, arbitrary helper vector `[0.3,0.5,0.8]`) | seeded rng(5); ray engine choice may change results; the "60 mm" in the comment is not enforced in code (`intersects_any` has no range) |
| `OD-H12/report/src/gate.py` deviation map (`:44-55`) | turbo scatter of scan points coloured 0–1 mm, 3 views + CAD→scan | reusable as-is | rng(0) subsample |
| `OD-H12/report/src/export_final.py` | build, export datum+scan-frame STEP/STL via SVD-orthonormalised inverse, re-import, abort unless 1 valid solid, JSON report | needs generalising (module name, filenames, cwd-relative `T1.npy`) | deterministic |
| `OD-H12/report/src/ovl.py` | scan vs CAD planar section overlays from a spec string | reusable as-is (expects `pump.stl` + `T1.npy` in cwd — hard-coded) | deterministic |
| `OD-H12/report/src/render.py:splat` | dependency-light z-buffer point-splat 6-view render | reusable as-is | seeded; 1.5 M samples, 0.25 mm pixel; dead `sample_surface_even ... if False` branch |
| `OD-H12/report/src/build_pump.py` builders | revolve from (r,z) polyline, rounded-rect sheet frame, hull flange with offset pocket, domed screws, rotated housing | project-specific (patterns reusable: revolve profile from param dict; `make_hull` + `offset(kind=INTERSECTION)` pocket) | edge selection by position/lambda (`:241,264`) can be fragile if params change |

## 12. Lessons

1. **Report the band miss, per region, with causes and options — never loosen.** Evidence: `OD-H12/README.md:21-44`; matches `baseline/oomwoo-re-pipeline/RE_SPEC.md:178-180`. (limitation, handled well)
2. **Measure the scan's own noise floor on a known-clean primitive before choosing a band.** Here intrinsic noise p95 0.13 mm (`OD-H12/README.md:35`) already eats ~40 % of a 0.30 p95 budget on a mixed metal/plastic assembly; the band should be set from measured noise + part class, not a fixed default. (failure → rule)
3. **Split CAD→scan into observable / unobservable by line-of-sight test** before judging; 25.65 % of this CAD was unobservable and drove raw p95 3.43 → observable 0.567 (`OD-H12/report/deviation_gate.json#cad_to_scan_unobservable_fraction`; `OD-H12/report/src/gate.py:57-84`). (success)
4. **Region the gate by functional zones** (here z-bands along the axis) so a miss can be localised (`OD-H12/report/src/gate.py:30-37`). (success)
5. **A validator whose expected values come from the same scan is not independent evidence** — label it a consistency check (`OD-H12/README.md:70-71`; `OD-H12/report/expected.json`). (limitation)
6. **Without calipers/photos, don't guess cosmetic/internal detail to chase the band** — declare it (`OD-H12/README.md:43-44,62-69`). (limitation)
7. **Single-surface fits over tapered/wavy real surfaces cost p95**; either model taper (cone/loft) or accept and declare (`OD-H12/README.md:35-36,43`). (failure)
8. **Always log measured → chosen with a rule**; this record has chosen values only and mostly unsnapped 0.01-mm radii, so intent vs noise can't be audited (`OD-H12/report/params.json`; required by `baseline/skills/stl2step-build123d/SKILL.md:54,90`). (gap)
9. **Keep the datum derivation and residuals** (alignment.json v2 fields); a bare 4×4 can't be audited (`OD-H12/report/alignment_T1.json` vs `RE_SPEC.md:142-157`). (gap)
10. **Deliver both datum-frame and scan-frame STEP**, re-import both, and optionally cross-check in a second kernel (NX) (`OD-H12/report/export_check.json`; `OD-H12/OD-H12-Pump.log:100-106`). (success)
11. **KD-tree-candidate + exact point-triangle distance** is a fast, deterministic, reproducible gate for ~1 M-triangle scans (reproduced bit-for-bit here; `OD-H12/report/src/gate.py:8-17`). (success)
12. **For multi-part assemblies requested as one solid, build sub-bodies and union; declare invented connectors** (core tube, `OD-H12/report/src/build_pump.py:272`; `OD-H12/README.md:54,67-68`). Result stayed Tier-0-clean at 213 analytic faces (`OD-H12/OD-H12-Pump.log`). (success)
13. **Re-orthonormalise transforms before handing them to OCP** (`OD-H12/report/src/export_final.py:17-22`). (success, ops)
14. **Operator acceptance can coexist with a missed numeric band** when the miss is explained — skills need a verdict state for "delivered, band not met, explained" (`golden-examples/README.md` OD-H12 row; `OD-H12/README.md:32`). (limitation)

## Questions

- Parameter count: README says 104 parameters (`OD-H12/README.md:60`) but `OD-H12/report/params.json` has 105 top-level keys. Counting convention not recorded.
- Flange hub: docstring "Ø24.4 hub" (`OD-H12/report/src/build_pump.py:182`) vs `dia_r_center=12.05` → Ø24.1 (`OD-H12/report/params.json`; `OD-H12/README.md:55`, validator Ø24.1 in `OD-H12/report/validator_report.json#measured.cyl_diameters_mm`). Which was measured?
- How was T1 derived (axis fit method, residuals, what defines z=0)? No script or record.
- Noise figure p95 0.13 mm, coil r 23.50–23.84, 0.16 % > 1.2 mm, and the original-frame repeat (median 0.102 / p95 0.448) have no artefact files (`OD-H12/README.md:30,35-37`). My full-res re-run reproduced 0.16 % and p95 0.448 (datum frame, p50 0.101); the 0.13 noise and coil range remain unverified.
- Scan bbox in datum frame (my inspection of the full-res scan): 54.20 × 56.44 × 122.18 vs CAD 54.05 × 55.15 × 121.95; Y differs by ~1.3 mm (scan y_min −32.38 vs CAD tb_y0 −31.4). `OD-H12/report/expected.json#bbox_mm.y` = 55.2 matches the CAD, not the scan, although labelled as scan-derived. Stray points or unmodelled feature? Not explained.
- Validator tool (oguz-validator-report-v0) source and its cylinder-diameter measurement method are not in the repo.
- Which thresholds were intended for this project? Only the skill default (p95 ≤ 0.30 / max ≤ 0.80) is quoted; no project-specific band was set.
- README repro commands expect `pump.stl` and `T1.npy` in `report/src` and a Windows venv (`OD-H12/README.md:75-79`); the input is stored as `0_input/OD-H12-Pump.stl`. Not a conflict in results, but the repro path is not runnable as written.
- Whether a decimated working copy was used during measurement is not recorded.
