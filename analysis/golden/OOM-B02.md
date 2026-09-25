# OOM-B02 — evidence extraction

Project root below is abbreviated `B02/` = `golden-examples/OOM-B02_side-brush-3-arm/`.
All numbers are copied from the record unless explicitly labelled "inspection only".

## 0. Record inventory

Method-bearing files:
- `B02/6_RE_work/INTAKE_CARD.md`: intake: scan health, occlusion map, functional zones F01–F08, interior enumeration, datum plan, rebuild strategy, risk flags R1–R8, 3-fold test, 17-dim measurement request, owner rulings Q1–Q4.
- `B02/5_reference/MEASUREMENTS.md`: the caliper sheet. It is PARTIAL (7 of 24 values, all transcribed from photos). It records the proceed-without directive (:15-38), the rulings (:82-89), the photo-transcription table D-01…D-12 (:98-116) and open questions Q5/Q6 (:124-132).
- `B02/5_reference/IMG_20260729_*.jpg` (18 photos): part identity, and caliper-on-feature photos that were the only source of Tier-1 values (`MEASUREMENTS.md:98-111`).
- `B02/6_RE_work/proposed_alignment.json`: the intake's proposed raw→datum 4×4 plus intake Z stations.
- `B02/2_mesh_cleaned/alignment.json`: the frozen raw→datum 4×4 (the modeller's copy), `scale_correction` 1.0 with a note, the modeller's re-verification, and corrected Z stations.
- `B02/6_RE_work/PARAM_TABLE.md` (it2) and `B02/6_RE_work/_it1_SUPERSEDED/PARAM_TABLE_it1.md` (it1): every parameter with a SOURCE tag, the §G honesty notes, and the §H self-check re-measured on the solid. It1 also holds the indicative Tier-2.
- `B02/6_RE_work/ASSUMPTIONS.md`: assumptions ledger A1–A13.
- `B02/6_RE_work/build_OOM-B02.py` (it2) and `B02/6_RE_work/_it1_SUPERSEDED/build_OOM-B02_it1.py`: the build123d build. The two files differ only at line 47 (`diff` run for this extraction).
- `B02/6_RE_work/40_verify.py` (byte-identical to `verify_OOM-B02.py`, checked with `cmp`): the modeller's Tier-1 self-check on the built solid.
- `B02/6_RE_work/qa/q01_solid.py`, `q02_tess.py`, `q02b_selfint.py`, `q03_datum.py`, `q03_datum_full.py`, `q10_solid_tess_tier1.py`, `q20_tier2.py`: the QA scripts.
- `B02/6_RE_work/qa/_qa_it2.json`, `_tier2_it2.json`, `_tier2_it2.log`, `_datum_indep.json`, `_solid.json`, `_tess.json`: the QA outputs. `_solid.json` and `_tess.json` carry it1 volumes; see Questions.
- `B02/6_RE_work/VERDICT.md`: the final verdict with the full gate tables, the iteration history and the honesty notes.
- `B02/6_RE_work/50_overlays_it2.py`, `60_render.py`, `70_report.py`: overlay, render and PDF generators. `70_report.py` holds the PDF's text. The PDF itself could not be text-extracted because no pdftotext, pypdf backend or fitz was available.
- `baseline/oomwoo-re-pipeline/TRACKER.md:13`: the tracker row for B02. It adds that it1 was published before the gate finished.

Pure outputs:
- `B02/4_STEP/OOM-B02.step`, `B02/4_STEP/OOM-B02_cad.stl` (deliverable).
- `B02/4_STEP/OOM-B02-exported.stp` and `.log`: an NX AP242 re-export from `OOM-B02_objects.prt`, 30-JUL-2026, 158 advanced faces.
- `B02/7_docs/*.png`, `B02/7_docs/OOM-B02_RE_report.pdf`.
- `B02/6_RE_work/B02_A…J*.png` (intake plots) and `B02_S1…S5*.png` (it2 overlays).
- `B02/6_RE_work/_it1_SUPERSEDED/OOM-B02_it1.step`, `_it1_cad.stl`, and the it1 PNGs.
- `B02/2_mesh_cleaned/OOM-B02.stl`. This is the FULL-resolution scan (798 874 tri, not decimated). Its size is 39 943 784 B = 84 + 50×798 874; the check was done here, inspection only.

## 1. Part class and geometry type

- **Part:** a three-arm robot-vacuum side brush. It is one white moulding (PP/POM-like) carrying one flat in-moulded bristle tuft per arm and one installed Phillips screw (`INTAKE_CARD.md:13-25`). The report calls it a "Mi/Mijia" brush (`70_report.py:132`).
- **Function:** it mounts on the motor's male-hex output shaft. The hex pocket takes all drive torque, the screw gives axial retention, and the cup-rim annulus is the axial seat (`INTAKE_CARD.md:16-22`). The owner confirmed this reading as Q3 (`MEASUREMENTS.md:88`).
- **Material/process:** injection moulding is inferred; "≈5.3 g in PP" (`PARAM_TABLE.md:167`). No material spec is recorded.
- **Geometry class:** mixed.
  - The hub is a body of revolution with a 3-lobed skirt.
  - The arms are swept/lofted blades on a planar r–z spline.
  - It has a hex pocket (prismatic) and one single-instance asymmetric key feature, SAF-1 (`INTAKE_CARD.md:131-143`).
- **Envelope (datum frame):**
  - Scan incl. bristles: X −33.28…+62.12, Y −55.60…+53.88, Z −0.39…+36.72 (`INTAKE_CARD.md:35`).
  - CAD (rigid plastic only): x −21.357…38.200, y −34.332…34.332, z 0.000…17.156 (`PARAM_TABLE.md:168`).
  - Rigid swept Ø 76.40 (scan 76.43); soft bristle swept Ø 124.9 (`VERDICT.md:174-176`).
- **Symmetry:** 3-fold rotational at 120.00° was confirmed.
  - Raw self-registration gave 120.00°; the residual at 120° was p95 0.992 mm (`INTAKE_CARD.md:186-200`).
  - No mirror plane: SAF-1 breaks it and the sweep is chiral (`INTAKE_CARD.md:143`).

## 2. Stages actually run, in order

The project ran under the **v2** line: the roles were "re-mesh-analyst" and "re-modeler", and the report is authored "OOMWOO RE line v2" (`INTAKE_CARD.md:3`, `alignment.json#written_by`, `70_report.py:108,382`). The baseline v3/v4 files post-date it: CHANGES_V3 is dated 2026-08-01 and RE_SPEC v4 was ratified 2026-08-02, while B02 was delivered 2026-07-30 (`baseline/oomwoo-re-pipeline/CHANGES_V3.md:1`, `RE_SPEC.md:2`, `TRACKER.md:13`).

1. **Intake (re-mesh-analyst, 2026-07-29).**
   - Copied the raw scan and decimated a work copy: 798 874 → 199 999 tri. Every dimension was re-confirmed on the raw mesh to ≤0.06 mm (`INTAKE_CARD.md:3-7,38`).
   - Built the occlusion map, functional zones, interior enumeration, datum plan, strategy and risk flags.
   - Artefacts: `6_RE_work/INTAKE_CARD.md`, the plots `B02_A…J*.png`, and `6_RE_work/proposed_alignment.json`.
2. **Measurement request.** 17 dims (M1–M17) were requested and `5_reference/MEASUREMENTS.md` was pre-filled (`INTAKE_CARD.md:231-269`).
   - No caliper-guide images exist. That v3 duty, `RE_SPEC.md:195-206`, was not in force yet.
3. **Owner rulings Q1–Q4 (2026-07-29).** SAF-1 is a functional key; the screw may be removed; the functional reading is confirmed; the arm path is planar in r–z (`MEASUREMENTS.md:82-89`, `INTAKE_CARD.md:172-182`).
4. **Photo transcription of caliper readings.** Twelve readings D-01…D-12 were transcribed (`MEASUREMENTS.md:91-116`).
   - The owner then directed "I confirm all assumptions, go ahead, do not be blocked" (2026-07-30).
   - Seven values were promoted into the sheet; the other 17 dims are absent (`MEASUREMENTS.md:15-38`).
5. **REBUILD it1 (re-modeler).**
   - Froze the datum and wrote `2_mesh_cleaned/alignment.json`.
   - Wrote `6_RE_work/_it1_SUPERSEDED/build_OOM-B02_it1.py` and `PARAM_TABLE_it1.md`.
   - Ran a self-check with `40_verify.py`, which found F06 +0.647, out of band.
   - Ran an indicative Tier-2 with no ICP and no skin mask (`PARAM_TABLE_it1.md:159-190`).
   - It1 was **published to `4_STEP\` before the gate finished**, and was later withdrawn (`70_report.py:376`, `TRACKER.md:13`).
6. **QA on it1 → REVISE** (`VERDICT.md:180-183`). The QA scripts in `6_RE_work/qa/` were run by the same context (A13). `_solid.json` and `_tess.json` appear to be the it1 runs (see Questions).
7. **REBUILD it2.** One parameter changed: `SKIRT_R_FLAT` 12.420 → 12.550. Artefacts: `6_RE_work/build_OOM-B02.py`, `PARAM_TABLE.md`, `ASSUMPTIONS.md`, `4_STEP/OOM-B02.step`.
8. **QA on it2.** Each check and its output:
   - `q01`/`q10` BRep validity → `qa/_qa_it2.json#qa1`
   - `q02b` BOPAlgo self-intersection (no JSON; result quoted at `VERDICT.md:14`)
   - `q02`/`q10` tessellation → `#qa2`
   - `q10` Tier-1 → `#qa4`
   - `q03_datum_full` independent datum → `qa/_datum_indep.json`
   - `q20` Tier-2 → `qa/_tier2_it2.json` and `.log`
   - Verdict → `6_RE_work/VERDICT.md`, **APPROVED it2**.
9. **Documentation.**
   - Section overlays via `50_overlays_it2.py` → `B02_S1…S5*.png`.
   - Renders via a z-buffer rasteriser, `60_render.py` → `7_docs/*.png`. Blender was absent (A12).
   - PDF via `70_report.py` → `7_docs/OOM-B02_RE_report.pdf`.
   - Tracker row updated (`TRACKER.md:13`).
   - A later correction re-read the VERDICT §3 numbers from the JSON (`VERDICT.md:94-99`).
10. **NX re-export (2026-07-30 06:21).** `4_STEP/OOM-B02-exported.stp` and `.log` came from NX `OOM-B02_objects.prt`, 158 faces (`4_STEP/OOM-B02-exported.log`). Who did it and why is not recorded.

**Pipeline stages and gates versus the baseline (v3/v4 names):**

| Baseline stage / gate | Ran? | Evidence |
|---|---|---|
| re-planner intake card + measurement request | yes, as the v2 re-mesh-analyst | `INTAKE_CARD.md` |
| caliper guide images | no | none in record |
| MODELING_PLAN + FEATURE BUDGET | no; strategy table only | `INTAKE_CARD.md:131-143` |
| External gate (calipers + GO) | replaced by owner directive "proceed-without" | `MEASUREMENTS.md:15-17` |
| F00 datum gate with `--datum` views | no formal gate; datum frozen by modeller | `alignment.json` |
| Per-feature manager review / GitHub PR | no | none in record |
| QA datum audit | yes: 0.429° / max 0.451 mm, "PASS" with no threshold stated | `VERDICT.md:18,153-163` |
| Validity + self-intersection | yes | `VERDICT.md:12-14` |
| Tier-0 surface quality | not run (not in the verdict) | `VERDICT.md:10-18` |
| Tier-1 | yes, partial (5 dims gated) | `VERDICT.md:37-56` |
| Tier-2 (ICP + skin mask + reverse) | yes | `VERDICT.md:76-151` |
| Photo plausibility / visual QA with own renders | not recorded as a gate row | `VERDICT.md:10-18` |
| Organisational independence of QA | no; declared (A13) | `ASSUMPTIONS.md:20` |
| Circuit breaker 3 iterations | 2 used | `VERDICT.md:185` |

## 3. Datum / alignment method

- **Primary (A):** the cup rim annular face becomes XY at Z=0, with material in +Z. The plane fit was RMS 0.052 mm over 30 342 raw faces (`INTAKE_CARD.md:110-111`).
  - Modeller's re-fit: mean z 0.0213, std 0.0849, n 17 027 (`alignment.json#verified_by_modeller`).
- **Secondary (B):** the rotation axis, i.e. the common axis of cup bore, skirt and hex, becomes +Z. It came from an "iterated rim-plane fit + robust circle fit" and converged to <0.0001° / <0.001 mm (`INTAKE_CARD.md:112-113`).
- **Tertiary (C):** the arm-1 centreline becomes +X (`INTAKE_CARD.md:114`).
  - The modeller re-measured the arm centres at 0.04 / 120.30 / −118.96° (`alignment.json#verified_by_modeller.arm_angular_centres_deg`).
  - 3-fold symmetry was enforced at exactly 120.00° (`PARAM_TABLE.md:29`).
- **Origin:** axis ∩ rim plane. This is implicit and is not stated as a named feature intersection.
- **Matrix:** the row-major 4×4 is identical in `proposed_alignment.json` and `2_mesh_cleaned/alignment.json#matrix_4x4`, and is also printed at `INTAKE_CARD.md:119-124`.
- **Scale:** none applied (`alignment.json#scale_correction`). The four available caliper dims sit 0.4–1.6 % under the scan (ratios 0.984/0.996/0.991/0.989), which is judged non-uniform (`alignment.json#scale_correction_note`). The envelope check could not run because ENV-1/2/3 are empty.
- **Scan pre-processing:** `mesh.volume` is −2434 mm³, so the normals point inward and are flipped before any signed-distance work (`INTAKE_CARD.md:36`). The STL is unwelded, so `merge_vertices()` is required before boundary detection (`qa/q20_tier2.py:27`). Inspection here confirmed a welded volume of −2434.3 and a datum bbox matching `alignment.json` (inspection only).
- **Independent audit** (`qa/q03_datum_full.py`, output `qa/_datum_indep.json`):
  - Method: a sign-free spherical normal vote over 6000 Fibonacci directions (3° cone, area-weighted), refined, then an SVD plane fit on the rim band.
  - Rim RMS 0.0080 mm.
  - Axis position from an IRLS Cauchy-robust circle fit on the cup-bore wall, separated from the skirt by the sign of n·r̂. Bore R 10.2419.
  - Arm phase from the 3-fold Fourier phase of the angular mass in r 20–34, labelling tested mod 120°.
  - Result: rotation difference **0.429°**, point disagreement mean 0.203 / p95 0.320 / **max 0.451 mm** (`_datum_indep.json`, `VERDICT.md:153-163`).
- **Tier-2 ICP refinement** on top of the datum: 0.698° / 0.187 mm (`qa/_tier2_it2.json#icp_deg,icp_mm`).
- **Frame-convention hazard:** the intake reported SAF-1 at θ −71° and the hex phase at 50.7°. In the frozen frame they are +59° and 59.04° (`PARAM_TABLE.md:49,72-74`, `alignment.json#notes`).

## 4. Measurement methods

| Method | Tool / function | What | Result | Source |
|---|---|---|---|---|
| Plane fit | intake, on the raw mesh | rim annulus | RMS 0.052, flatness std 0.052 over 30 342 faces | `INTAKE_CARD.md:66,111` |
| Hex area-fit | intake | F01 AF / AC / phase | AF 7.358 (rms 0.037, n 7295), AC 8.496, largest gap 124° | `INTAKE_CARD.md:46,65` |
| Opposite-flat-pair fit | modeller | F01 AF | 7.377; individual flats 7.19–7.32; phase 59.04°; corner AC/2 p99.5 4.126 → corner R 0.35 | `PARAM_TABLE.md:48-50` |
| Robust circle fits | intake | cup bore Ø20.93 → 20.41 (≈1.4° draft); bore mouth Ø2.70 (rms 0.10); counterbore Ø7.07 (rms 0.33) | as stated | `INTAKE_CARD.md:67-68` |
| Folded 3-fold radial profile R(θ) | modeller | skirt lobe/flat | lobe R 13.55, flat R 12.55 over −17…+18°, ramp 8–10° | `PARAM_TABLE.md:66-67`, `INTAKE_CARD.md:69` |
| Percentile z per radius ring (clean sectors) | modeller | dome meridian (39 pts), floor, apex | floor p50 2.455; apex p99 10.866; counterbore floor p50 9.543 | `PARAM_TABLE.md:57-65` |
| Cup-interior min-z height map | intake and modeller | SAF-1 boss, groove | two-level boss 1.01 / 2.11 mm proud; groove 0.337 deep (the intake had called it a 0.25 ridge) | `PARAM_TABLE.md:60,86-88`, `B02_E` |
| Self-registration sweep | intake | 3-fold | 120.00° raw; residual median 0.125 / p95 0.992 / max 2.605 | `INTAKE_CARD.md:188-196` |
| Face-adjacency roughness | intake | plastic vs bristle | median 3–4° moulded vs 10–17° bristle; junction r 38.23/38.22/38.19 | `INTAKE_CARD.md:39,196`, `B02_D` |
| Arm mid-line and thickness per station | modeller | arm path z(r), thickness | 3-arm mean; per-arm zmid at r36 13.50/14.46/14.75; tangential drift 0.97/1.49/2.20 | `PARAM_TABLE.md:94-97` |
| Two-jaw support-function window | modeller | achievable skirt caliper readings | scan 25.99…27.08 → proves F06 = 24.84 impossible | `PARAM_TABLE.md:108-115` |
| Caliper photos (transcribed) | Mitutoyo digital ±0.02, effective ±0.1 | D-01…D-12 | F02 3.44, F03 20.75, F05 26.85, F06 24.84 (struck), F10 5.33, F11 4.07, X01 10.85 | `MEASUREMENTS.md:10,53-62,98-111` |
| Simulated caliper on the built solid | `q10_solid_tess_tier1.py::jaws`: section, densify 0.02, support width over azimuth | Tier-1 re-measure | see §7 | `qa/q10_solid_tess_tier1.py:215-272` |

## 5. Design-intent rounding

| Feature | Measured | Chosen | Rule used | Source |
|---|---|---|---|---|
| Cup bore Ø (F03) | scan 20.93 / caliper-photo 20.75 | 20.750 | caliper used directly | `PARAM_TABLE.md:36` |
| Hex depth (F02) | scan 3.565 (modeller) / 3.48 (intake) / caliper 3.44 | 3.440 | caliper used directly | `PARAM_TABLE.md:37` |
| Skirt lobe R (F05) | scan 13.55 / caliper OD 26.85 | 13.425 = 26.85/2 | caliper used directly (a max-lobe reading may under-read) | `PARAM_TABLE.md:38` |
| Skirt flat R (F06) | scan 12.55 / caliper 24.84 | it1 12.420 → it2 12.550 | it1 used the caliper as a radius; it2 struck the caliper by geometric proof and reverted to scan | `PARAM_TABLE.md:39`, `build_OOM-B02.py:47` |
| Arm width (F10) | scan 5.89 / caliper 5.33 | 5.330, constant along the blade | caliper; the scan width is flat ±0.15 | `PARAM_TABLE.md:40` |
| Arm thickness @ r36.5 (F11) | scan 4.106 / caliper 4.07 | 4.07; taper = scan shape shifted −0.036 | caliper at the station + scan shape | `PARAM_TABLE.md:41,97` |
| Hex AF (F01) | 7.358 / 7.377 | 7.358 | **explicitly NOT snapped** to 7.0/7.5 (no caliper) | `PARAM_TABLE.md:48` |
| Hex phase | 59.04° | 59.0 | round to 0.1°; coincides with SAF-1 θ (design-intent coincidence) | `PARAM_TABLE.md:49,78` |
| SAF-1 θ | nub 57.6 / recess 60.0 / boss 61.5 | 59.0 | consensus of the 3 sub-features | `PARAM_TABLE.md:78` |
| Cup floor Z | 2.456–2.459 | 2.455 | round to scan precision | `PARAM_TABLE.md:57` |
| Cup draft | 7.1–10.4° | 8.0° | round | `PARAM_TABLE.md:59` |
| Dome apex | 10.866 (intake 10.97) | 10.866 | p99 percentile choice | `PARAM_TABLE.md:64` |
| Flat half-angle / ramp | −17…+18 / 8–10° | 16.0 / 9.0° | round | `PARAM_TABLE.md:66-67` |
| Arm end R | 38.23/38.22/38.19 | 38.20 | mean of 3 | `PARAM_TABLE.md:101` |
| Arm angular spacing | 120.42/120.38/119.20 | 120.00 | symmetry enforced | `INTAKE_CARD.md:195`, `PARAM_TABLE.md:29` |
| Arm z-path | 3 arms, spread 1.25 at r36 | 3-arm mean | minimises the worst residual (0.74 vs 1.25 for arm 1) | `PARAM_TABLE.md:94` |
| Tuft slot | ribbon 5.0 × 3.9 | 4.60 × 3.50 × 3.00, R0.40 | ribbon minus the dilation offsets; depth photo-inferred | `PARAM_TABLE.md:102` |
| Blend fillet | scan ≈1–2 mm | R0.8 (fallback 0.5/0.3) | fillets last | `PARAM_TABLE.md:100`, `build_OOM-B02.py:292-298` |
| SAF hole Ø / inner end | ≈2 / occluded | 2.00 / r 9.50 | photo-inferred, not gated | `PARAM_TABLE.md:83-85` |

No standard-size snap (RE_SPEC §3.8) was applied to any dimension. None is recorded.

## 6. Feature tree

The tree as built, from `B02/6_RE_work/build_OOM-B02.py`:

1. **Hub revolve** (:137-158). A `BuildSketch(Plane.XZ)` meridian profile: bore mouth → cup floor `CUP_FLOOR_Z` → `ThreePointArc` groove (`GROOVE_R0/RMID/R1`, `GROOVE_DEPTH`) → drafted bore (`CUP_BORE_R`, `CUP_BORE_STEP_Z`, `CUP_DRAFT_DEG`) → rim `RIM_Z` → skirt `SKIRT_R_LOBE` → `Spline(*DOME_PTS)` 39-point scan dome → counterbore (`CBORE_D`, `CBORE_FLOOR_Z`) → bore `BORE_D`. Then `revolve(axis=Axis.Z)`.
2. **Hex pocket cut** (:163-173). A hexagon built from `HEX_AF`, `HEX_PHASE_DEG`, `fillet(HEX_CORNER_R)`, extruded to `HEX_FLOOR_Z` = `CUP_FLOOR_Z + HEX_DEPTH`.
3. **Skirt 3-lobe + SAF recess cut** (:178-217). `skirt_r(θ)` is a smoothstep flat/lobe function (`SKIRT_R_FLAT`, `FLAT_HALF_DEG`, `RAMP_DEG`), min'd with the SAF-1 recess (`SAF_RECESS_R/HALF/RAMP`). It is sampled at 1° into a 360-point `Spline` and cut as Circle(25) minus the outline, height `SKIRT_TOP_Z+1`. The tool is held 0.02 clear of the lobe to avoid tangent booleans (:182-185).
4. **SAF-1 nub** (:236-239). `polar_sector` from `SAF_NUB_HALF`, `SAF_NUB_R`, `SAF_NUB_Z0/Z1`.
5. **SAF-1 internal boss**, two levels (:240-244). `SAF_BOSS_TH0/TH1`, `RI/RM/RO`, `Z_IN/Z_OUT`.
6. **SAF-1 radial hole** (:245-250). Cylinder `SAF_HOLE_D` at `SAF_HOLE_Z`, starting at `SAF_HOLE_RIN`.
7. **Arm loft** (:255-268). 22 `RectangleRounded` sections on planes normal to the r–z path, from `ARM_STATIONS` (r, z_mid, thickness, width; `ARM_W`, `ARM_CORNER_R`), joined by `loft` (not ruled).
8. **Tuft slot cut** (:270-277). `TUFT_SLOT_W/T/R/DEPTH`, cut from the end face.
9. **Polar pattern ×3** (:279-280). `Rotation(0,0,120k)` unions.
10. **Radial trim** (:283). Intersect with `Cylinder(ARM_R_END, 60)`.
11. **Fillets last** (:288-298). Seam edges at 7<z<11.2 and 6<r<15, trying R 0.8, then 0.5, then 0.3. The record says R0.8 on 16 edges (`PARAM_TABLE.md:100`).
12. **Export** (:303-313). STEP, plus STL at tolerance 0.02 / angular 0.15.

Face composition of the delivered STEP, counted from STEP entities (inspection only): 185 ADVANCED_FACE = 108 PLANE + 40 B_SPLINE_SURFACE + 29 CYLINDRICAL + 5 SURFACE_OF_LINEAR_EXTRUSION + 1 SURFACE_OF_REVOLUTION + 1 CONICAL + 1 TOROIDAL. The it1 STEP has the same counts. No area share is recorded.

## 7. Gates run, with actual numbers

All deviation gates were run on the **full-resolution raw scan** (798 874 tri), not the decimated work copy (`VERDICT.md:78-79`, `qa/_tier2_it2.log:1`). Thresholds come from RE_SPEC §4 (`baseline/oomwoo-re-pipeline/RE_SPEC.md:166-183`; the numbers are unchanged from v2 per `CHANGES_V4.md:23`) and from intake R3/R4 for the named interfaces.

| Gate | Threshold (source) | Measured (it2) | Result | Source |
|---|---|---|---|---|
| BRep validity | single valid solid | 1 solid, 1 shell, 185 faces, 0 naked edges, BRepCheck valid, vol 5801.07 (BRep) | PASS | `qa/_qa_it2.json#qa1`, `VERDICT.md:6-12` |
| Self-intersection | none | `BOPAlgo_CheckerSI` level 9, HasErrors=False | PASS | `VERDICT.md:14`, `qa/q02b_selfint.py` (no JSON saved) |
| Tessellation | watertight | 714 968 tri, watertight, winding ok, euler 0, 1 comp, 0 degenerate, vol 5799.22 (Δ −1.86 vs BRep) | PASS | `qa/_qa_it2.json#qa2` |
| Tier-1 F02 hex depth | ±0.15 (RE_SPEC §4) | 3.440 vs 3.44, Δ 0.000 | PASS | `#qa4.F02` |
| Tier-1 F03 cup bore | ±0.15 | 20.750, Δ 0.000 | PASS | `#qa4.F03` |
| Tier-1 F05 skirt OD max | ±0.15 | 26.850, Δ 0.000 | PASS | `#qa4.F05` |
| Tier-1 F10 arm width | ±0.15 | 5.330, Δ +0.000 | PASS | `#qa4.F10` |
| Tier-1 F11 arm thickness | ±0.15 | 4.096, Δ **+0.026** (worst) | PASS | `#qa4.F11`, `#qa4_worst_gated` |
| Tier-1 F06 skirt OD min | struck | CAD 25.617 | not gated | `#qa4.F06` |
| Tier-1 F01 hex AF | no caliper | CAD 7.358 | not gated | `#qa4.F01` |
| Tier-1 coverage | all sheet dims | 5 of 24 gated; 17 ABSENT | PARTIAL | `VERDICT.md:15,54-56` |
| Tier-2 whole part (CAD→scan, outer skin, after ICP) | p95 ≤1.6, max ≤4.0 | n 233 423; mean 0.220; p50 0.136; p95 **0.740**; p99 1.003; max **2.524** (unsigned NN distance) | PASS | `qa/_tier2_it2.json#whole`, `.log` |
| Tier-2 rim annulus (datum A) | max ≤0.8 (named interface) | p95 0.245, max 0.651 | PASS | `#zones` |
| Tier-2 hex pocket F01 | max ≤0.8 | p95 0.216, max 0.316 (43.4 % masked) | PASS, **masked** | `#zones` |
| Tier-2 SAF-1 nub | max ≤0.8 (R3 ruling) | p95 0.524, max 0.648 (64.6 % masked) | PASS | `#zones` |
| Tier-2 SAF-1 skirt recess | max ≤0.8 | p95 0.467, max 0.751 (68.8 % masked) | PASS | `#zones` |
| Tier-2 SAF-1 internal boss | reported (re-scoped interior, A7) | p95 0.801, max 1.540 | not gated | `#zones` |
| Tier-2 arms r14–38.2 | reported (A11) | p95 0.890, max 1.325 | not gated | `#zones` |
| Tier-2 other reported zones | reported | cup bore max 1.404; floor 0.512; skirt band 2.524; dome 0.316; arm root 2.524 | not gated | `#zones` |
| Mask sensitivity (M3 radius 0→2.5) | informational | whole-part p95 0.894→0.712, max 3.049→2.524, PASS at every radius. Unmasked hex max **1.624 (0.824 over)**; recess **0.805 (0.005 over)** | declared | `#sensitivity`, `.log` |
| Reverse scan→CAD | informational | n 347 030, mean 0.212, p95 0.659, max 1.290 | no missing feature | `#reverse` |
| Datum independence | none stated (v4 would use ≤0.3° / ≤0.15 mm) | 0.429° / max 0.451 mm | "PASS" | `VERDICT.md:18`, `_datum_indep.json` |
| Volume | none | 5801.07 BRep / 5799.22 tess | n/a | `#qa1,#qa2` |
| Visual / photo plausibility | not recorded as a gate | overlays S1–S5 and renders produced | not recorded | `VERDICT.md:10-18` |
| Tier-0 surface quality | not in the v2 line | not run | — | `VERDICT.md` |

The masks applied before the Tier-2 numbers above (`qa/q20_tier2.py:35-44,99-104`, `.log`):

- **M1:** bristles r>38.5, 150 548 faces (18.8 %).
- **M2:** screw head plus screw end, 19 222 faces in the log (16 610 in the verdict).
- **M3:** open boundary <0.8 mm, drops 20.76 %.
- **M4:** skin |n·n| < cos 70°, drops 5.91 %.
- **A6:** hex wall coverage 263/360°.
- In total, 77.8 % of CAD samples were gated.

## 8. Iterations

**Iteration 1: REVISE** (`VERDICT.md:180-183`, `PARAM_TABLE_it1.md`, `70_report.py:356-360`).

What failed:
1. **Tier-1 F06 skirt OD MIN:** the CAD re-measured 25.487 against the caliper 24.84, **Δ +0.647, out of the ±0.15 band** (`PARAM_TABLE.md:113-114`, `ASSUMPTIONS.md:9`).
2. **Indicative Tier-2.** This check was one-way, with 300 k samples, the screw masked, **no ICP and no skin mask** (`PARAM_TABLE_it1.md:159-190`).
   - Whole part: p95 1.045 / max 3.134, inside the band.
   - Three named interfaces missed the 0.8 sub-band:
     - SAF-1 skirt recess 0.826 (0.026 over)
     - SAF-1 internal boss 1.681
     - hex pocket 1.846
3. **Process failure:** it1 was published to `4_STEP\` before the gate finished (`70_report.py:376`, `TRACKER.md:13`).

Root causes, as recorded:
- **F06:** a data-attribution problem, not a modelling error.
  - On a 3-lobed skirt a two-jaw caliper reads R(θ)+R(θ+180). The flats are ~34° wide and 120° apart, so no antipodal flat–flat pair exists.
  - The achievable window on the scan is 25.99…27.08, and 24.84 is 1.15 mm below it.
  - It1 had applied 24.84/2 as a radius (`PARAM_TABLE.md:108-115`, `VERDICT.md:58-68`).
  - Note: the it1 PARAM_TABLE already flagged the impossibility, but applied the value "per the rebuild brief" (`PARAM_TABLE_it1.md` §G-1, from the diff).
- **Hex pocket 1.846:** the scan never saw the whole wall (the record gives the gap as 124°; see Questions), so the number was distance to a hole edge, not a surface deviation (`VERDICT.md:131-132`).
- **SAF-1 recess 0.826:** it "rode the un-refined datum" (`VERDICT.md:133-134`).
- **SAF-1 boss 1.681:** it was modelled as a sharp polar sector, while the moulded pad has soft edges the scan cannot resolve from inside the cup (`PARAM_TABLE_it1.md`, cited above).

What fixed it:
- **Geometry:** exactly one parameter changed, `SKIRT_R_FLAT` 12.420 → 12.550 (scan authority). F06 was struck from Tier-1 with the proof and a re-measure hook. Confirmed by `diff`: the build scripts differ only at `build_OOM-B02.py:47`.
- **Gate protocol:** the full `q20_tier2.py` run added independent ICP (0.698°/0.187 mm), the M3 open-boundary mask, the M4 skin mask, the A6 hex-gap mask located from the scan, and a mask-sensitivity sweep.
  - Hex: 1.846 → 0.316, from masking.
  - Recess: 0.826 → 0.751, from ICP.
  - Boss: 1.681 → 1.540, and **re-scoped to interior/occluded and ungated (A7)**. The record says of this: "the one place the gate got *weaker* rather than the geometry getting better, and it is declared as such" (`VERDICT.md:135-136`).
- **Honest reading:** the it1 and it2 Tier-2 numbers are not like-for-like. It1 was indicative with no ICP and no masks; it2 was the full protocol (`VERDICT.md:182-183`). The Tier-2 sub-band "fixes" came from measurement protocol and re-scoping, not from geometry changes.

**Iteration 2: APPROVED.**
- Tier-1 worst 0.026 (F11).
- Tier-2 0.740 / 2.524.
- Named interfaces 4/4 PASS (`VERDICT.md:184`).
- A post-hoc correction re-read the Tier-2 table from `_tier2_it2.json`, because the first draft quoted an intermediate run. The deltas were ≤0.02 and no verdict changed (`VERDICT.md:94-99`). The intermediate numbers survive in `PARAM_TABLE.md:173-186`, e.g. whole part n 234 850, p95 0.742.

## 9. Declared limitations and assumptions

The three declared limitations (`VERDICT.md:20-30`, repeated at `70_report.py:108-111` and `TRACKER.md:13`):

1. "**Tier-1 is PARTIAL — 5 of 24 sheet dims are gated. 17 are ABSENT, not passed.** No caliper session was run; Muhammed directed proceed-without on 2026-07-30. The 7 dims that carry values are photo-transcribed (effective ±0.1 mm, not the instrument's ±0.02)."
2. "**Absolute scale is UNVERIFIED.** ENV-1/2/3 are empty, so the RE_SPEC §2 envelope scale check could not be run. No global scale was applied (the 0.4–1.6 % scan/caliper disagreement on four mid-size dims is not uniform enough to justify one)."
3. "**F01, the hex drive socket, has no caliper reading of any kind.** The CAD holds the scan fit **AF 7.358**, deliberately NOT intent-snapped to 7.0 or 7.5. This is the torque interface and the largest single risk on the part. **One caliper reading on F01 should trigger a re-run.**"

Other declared items:
- **Fitness:** "Not yet fit for manufacture or tooling until F01 is calipered" (`VERDICT.md:210-213`).
- **Assumptions ledger A1–A13** (`ASSUMPTIONS.md:8-20`):
  - A2: F06 struck.
  - A3: D-06 25.79 is also below the achievable window, so it is unused.
  - A6: hex masked over the scan gap.
  - A7: SAF-1 boss is interior, not gated.
  - A8: SAF-1 hole held as the key datum (Q5 fallback).
  - A9: bore, tuft-socket and hole-bottom interiors are photo-inferred.
  - A10: bristles excluded, soft ±3 mm.
  - A11: arm path planar, 3-arm mean; drift is a residual.
  - A12: Blender absent, rasteriser used.
  - A13: QA **not organisationally independent** (same context).
- **Masked pass:** the hex-pocket PASS is a *masked* pass. Unmasked it reads 1.624, 0.824 over band, on the feature with no caliper reading. The SAF recess reads 0.805 unmasked (`VERDICT.md:138-145`).
- **Intake errors corrected against the scan** (`VERDICT.md:198-202`, `PARAM_TABLE.md:128-134`):
  - SAF-1 is at +59°, not −71°.
  - The floor feature is a 0.337 groove, not a 0.25 ridge.
  - An unlisted 36°-wide, ~1.05 mm SAF-1 skirt recess exists.
- **Arm path:** the CAD arm reads ~0.74 mm high on arm 1 and ~0.51 mm low on arm 3 because of the mean path (`50_overlays_it2.py:74-78`).
- **Open, non-blocking:** caliper F01, ENV-1/2/3, F08/F17/F18 with the screw out, F06 re-attribution, Q5, Q6 (`VERDICT.md:239-240`, `MEASUREMENTS.md:131-132`).

## 10. Deviations from the baseline skill

B02 ran under v2. The baseline v3/v4 doctrine post-dates it (§2), so these are deviations from the *current* baseline and not violations at the time. Pre-v3 parts are grandfathered (`RE_SPEC.md:338-340`).

- **External gate replaced by an owner directive.**
  - Baseline: no rebuild before calipers + GO (`RE_SPEC.md:298-300,381-383`); scale verification before datum (`RE_SPEC.md:105-107`).
  - B02: built on photo-transcribed values, with scale unverified, under an explicit directive that is recorded in the sheet header (`MEASUREMENTS.md:15-38`).
  - Helped? The part shipped, with limitations carried honestly. It could not verify scale.
- **Photo-transcribed caliper values plus attribution confirmation.** This is not in the baseline, which assumes a bench session (`RE_SPEC.md:89-92`). B02 created a D-table with "confirm or strike" and an effective ±0.1 mm uncertainty (`MEASUREMENTS.md:91-116`).
  - Mixed result: 1 of 6 attributions (F06) proved physically impossible and caused the only REVISE.
- **Geometric-achievability check of a caliper reading** (two-jaw support-function window). Not in the baseline. It explained and resolved the it1 failure with proof (`PARAM_TABLE.md:108-121`). It helped.
- **Simulated-caliper Tier-1** (support function on a fine tessellation, `q10::jaws`).
  - Baseline: "feature queries on faces/edges" (`agents/re-qa-verifier.md:164-166`).
  - B02's method mimics the instrument and handles non-circular skirts. It helped.
- **Datum audit threshold.**
  - Baseline v3/v4: ≤0.3° and ≤0.15 mm (`agents/re-qa-verifier.md:151-157`, `RE_SPEC.md:239-243`).
  - B02: 0.429° / max 0.451 mm (mean 0.203), reported as "PASS" with no threshold (`VERDICT.md:18`).
  - Under v4 the angular value would exceed 0.3°. The origin offset proper is not separately recorded (see Questions).
- **Tier-0 surface quality** (`RE_SPEC.md:265-270`) was not run.
  - The STEP has 185 faces, 40 of them B-spline by entity count (inspection only).
  - The arm is a 22-section non-ruled loft of scan-station sections, and the skirt is a 360-point spline. That is arguably near the "fitted Spline profiles" allowance, not "ruled lofts of scan slices" (`RE_SPEC.md:260-262`), but no audit is recorded.
- **No MODELING_PLAN / FEATURE BUDGET / F00 / per-feature review / GitHub PR** (`RE_SPEC.md:185-253`). The strategy lived in the intake card §6. The single build script replays everything.
- **alignment.json schema:** v1 (`matrix_4x4` + `scale_correction` + notes). It lacks the v2 keys `scan_noise_mm`, `primary`/`secondary` fit records and `origin` (`RE_SPEC.md:142-157`).
- **Tier-2 masking went beyond the baseline:**
  - The baseline names ICP + skin mask (`RE_SPEC.md:173-176`).
  - B02 added the M3 open-boundary mask (drops 20.8 %), an A6 occlusion-arc mask computed from the scan, a mask-sensitivity sweep, per-zone masked fractions, and a reverse direction.
  - The sensitivity sweep made the masks auditable and exposed the masked-pass caveat. It helped honesty.
- **Re-scoping a failing named interface to interior** (SAF-1 boss, A7). RE_SPEC §4 allows interior buckets to be reported, but the honesty rule says a region that can't hit its band is HALTed with options (`RE_SPEC.md:181-183`). B02 re-scoped rather than HALTed, and declared it (`VERDICT.md:135-136`).
- **QA independence.** The baseline demands independent agents and HALT if agents are missing (`RE_SPEC.md:364-369`). B02 proceeded in-context and declared it (A13). This is a direct contradiction of v4, which was written partly because of such runs.
- **Renders:** a z-buffer rasteriser (A12). This became baseline v3 practice (`CHANGES_V3.md:37` cites B02 as precedent).
- **Photo guidance:** calipers on the feature in the photo, per `RE_SPEC.md:57-59`. B02 was the part that exploited this.

## 11. Reusable code

| File:function | What it does | Generality | Determinism concerns |
|---|---|---|---|
| `B02/6_RE_work/qa/q10_solid_tess_tier1.py:jaws` (+`densify`, `zsec`, `meridian`) | two-parallel-jaw caliper simulation on section polylines | reusable as-is | angular step 0.05°; resample 0.02 mm |
| `B02/6_RE_work/qa/q10_solid_tess_tier1.py` QA-1/QA-2 block (:178-205) | BRep counts, BRepCheck, fine tessellation health, Δvolume | reusable as-is | cached `_fine_*.stl` by mtime |
| `B02/6_RE_work/qa/q01_solid.py` | naked-edge count via edge→face ancestors, shell closed flags | reusable as-is | none |
| `B02/6_RE_work/qa/q02b_selfint.py` | `BOPAlgo_CheckerSI` level 9 | reusable as-is | `SetRunParallel(True)` |
| `B02/6_RE_work/qa/q03_datum_full.py` | independent datum: Fibonacci normal vote → SVD rim plane → IRLS Cauchy circle fit on the bore (inner/outer separated by the sign of n·r̂) → 3-fold Fourier phase → compare vs `matrix_4x4` mod 120° | needs generalising (radius bands and 3-fold are part-specific) | seeded `default_rng(0)`; hardcoded paths |
| `B02/6_RE_work/qa/q20_tier2.py` | Tier-2: weld, flip inward normals, masks, dense sampling, point-to-point ICP with masked correspondences, zone buckets, hex-gap coverage from the scan, sensitivity sweep, reverse check, JSON dump | core reusable; zones and masks project-specific | seeds 7/11/13; 60-iteration ICP cap (converged in 48); hardcoded Drive paths |
| `B02/6_RE_work/build_OOM-B02.py:skirt_r` + spline cut | smoothstep lobed outline R(θ) with a local recess, cut as Circle minus Spline | needs generalising | 1° sampling |
| `B02/6_RE_work/build_OOM-B02.py:polar_sector` | solid polar sector (r0, r1, θ0, θ1, z0, z1) | reusable as-is | Polyline n=24 facets the arcs |
| `B02/6_RE_work/build_OOM-B02.py` arm loft (:255-277) | rounded-rectangle sections normal to an r–z path → loft, end-face slot | needs generalising | none |
| `B02/6_RE_work/build_OOM-B02.py` fillet fallback (:288-298) | tries fillet radii descending, logs failures | reusable pattern | silently takes a smaller radius: the chosen radius must be logged |
| `B02/6_RE_work/40_verify.py` | modeller self-check (the same measurement as q10) | reusable | hardcoded scratch paths |
| `B02/6_RE_work/50_overlays_it2.py:meridian_segs/plan_segs/normal_segs/draw/finish/annot` | scan-vs-CAD section overlays with mm grids and annotation boxes | reusable as-is | none |
| `B02/6_RE_work/60_render.py:render` | orthographic z-buffer rasteriser with Lambert shading; deviation colouring clipped at 2.6 mm (:108) | superseded by baseline `render_views.py` | fixed full scale |
| `B02/6_RE_work/70_report.py:Page` | matplotlib PdfPages report layout that pulls numbers from the QA JSONs | needs generalising | numbers read from JSON (good) |

## 12. Lessons

1. **Check whether a caliper reading is geometrically achievable before using it.** On non-circular sections, compute the two-jaw support-function window on the scan. A reading outside the window is misattributed: strike it with the proof and a re-measure hook, and do not build to it.
   - Source: failure → fix. `PARAM_TABLE.md:108-121`, `VERDICT.md:58-74`.
2. **Take Tier-1 on the finished STEP with a simulated two-parallel-jaw caliper** on a fine (5 µm) tessellation, never echoed from parameters.
   - Source: success. `qa/q10_solid_tess_tier1.py:215-272`.
3. **Photo-transcribed readings count as real readings only after the owner confirms the attribution.** Carry them at ±0.1 mm effective uncertainty, and keep unconfirmed ones (D-09/10/12) unused.
   - Source: success, with one failure (F06). `MEASUREMENTS.md:21-24,91-116`.
4. **Never intent-snap the critical interface without a caliper.** Hold the scan fit, and declare it as a limitation with a re-run trigger.
   - Source: limitation. `VERDICT.md:28-30`, `PARAM_TABLE.md:48`.
5. **Mask occlusion arcs derived from the scan itself.** Measure wall coverage per degree on wall-normal faces only; including the floor makes the mask a no-op. Distance to a hole edge is not a surface deviation.
   - Source: failure → fix. `qa/q20_tier2.py:112-132`, `VERDICT.md:131-132`.
6. **Every Tier-2 mask needs a sensitivity sweep and a masked-fraction report.** State any named-interface PASS that depends on a mask as a "masked pass".
   - Source: honesty success. `_tier2_it2.log`, `VERDICT.md:138-145`.
7. **Run a reverse scan→CAD check** to prove no feature was omitted. A forward max can be CAD proud of the scan.
   - Source: success. `VERDICT.md:147-151`.
8. **Weld an unwelded STL before boundary detection. Check the sign of the scan volume and flip inward normals.**
   - Source: success. `qa/q20_tier2.py:27-30`, `INTAKE_CARD.md:36`.
9. **Compare iterations only with like-for-like gate protocols.** It1's indicative Tier-2 (no ICP, no masks) against it2's full protocol overstated the "improvement".
   - Source: failure/limitation. `VERDICT.md:182-183`.
10. **Never publish a deliverable to the output folder before the gate verdict.**
    - Source: failure. `70_report.py:376`, `TRACKER.md:13`.
11. **State and check angle conventions when the frame changes.** The intake's −71°/50.7° versus the frozen frame's +59°/59.04° was a sign-convention trap. Record θ only in the frozen datum frame.
    - Source: failure caught. `PARAM_TABLE.md:49,72-74`.
12. **Model re-measurement can overturn intake claims** (ridge versus groove, a missing recess). The modeller must re-measure every feature on the raw scan rather than copy the intake.
    - Source: success. `PARAM_TABLE.md:60,82,128-134`.
13. **Handle soft features by radius masks.** Bristles beyond the roughness-discriminated junction are soft (±3 mm), not modelled, and excluded from both gates. Model to the rigid anchor.
    - Source: success. `INTAKE_CARD.md:161-163,212-227`.
14. **Free-state deformation (arm droop/drift):** model the mean planar path and report the residual rather than chasing it. Use the mean to minimise the worst-case residual.
    - Source: success/limitation. `PARAM_TABLE.md:94-95`.
15. **Scanner dilation on thin sections is an offset, not a scale.** A non-uniform scan/caliper disagreement must not trigger a global scale; use the caliper locally.
    - Source: limitation. `INTAKE_CARD.md:55-57`, `alignment.json#scale_correction_note`.
16. **Re-scoping a failing named interface to "interior" weakens the gate.** Allow it only with explicit declaration, or HALT with options per the honesty rule.
    - Source: limitation. `VERDICT.md:135-136`, `RE_SPEC.md:181-183`.
17. **Keep the superseded iteration** (script, STEP, param table, images) in a `_itN_SUPERSEDED/` folder, and record "exactly one parameter changed" by diff.
    - Source: success. `6_RE_work/_it1_SUPERSEDED/`.
18. **A datum audit needs an explicit threshold.** B02 passed 0.429° with no threshold; v4 would fail it.
    - Source: gap. `VERDICT.md:18`, `agents/re-qa-verifier.md:155`.
19. **Avoid tangent-coincident boolean faces** by offsetting cut tools slightly (0.02 mm), and bury arm roots inside the dome so the union has no floating end faces.
    - Source: success. `build_OOM-B02.py:182-185`, `PARAM_TABLE.md:99`.

## Questions

- **Timeline conflict.** The proceed-without directive is dated 2026-07-30 (`MEASUREMENTS.md:17`, `VERDICT.md:23`). But the it2 STEP header timestamp is 2026-07-29T21:14:11, the Tier-2 JSON is from 2026-07-29 21:49 (`VERDICT.md:94`), and ASSUMPTIONS is dated 2026-07-29 and already cites the directive (`ASSUMPTIONS.md:1-4`). Was the build done before the directive, or is the date wrong?
- **Hex occlusion gap size.** The intake says 124° (`INTAKE_CARD.md:46`), PARAM_TABLE says 92–124° (:48), and the Tier-2 log says "largest gap 85 deg" with coverage 263/360 (`_tier2_it2.log`). The VERDICT still cites 124° (`VERDICT.md:92,167`).
- **Screw mask count.** The VERDICT and report say 16 610 faces (`VERDICT.md:89`, `70_report.py:180`). The final log says 19 222, because the script also masks the screw-end population (`q20_tier2.py:39`, `.log`).
- **`qa/_solid.json` and `qa/_tess.json`** (vol 5779.75 / 5778.67, 723 102 tri) match the it1 figures (`PARAM_TABLE_it1` §H: 5778.666, 723 102 tri), not it2 (5801.07 / 714 968). Is their iteration provenance labelled anywhere? Not recorded.
- **Datum audit metric.** "Point disagreement max 0.451 mm" is not the same quantity as the v4 "origin offset ≤ 0.15 mm". The origin offset itself is not recorded. The "—" band in `VERDICT.md:18` means no threshold existed.
- **Tier-1 count.** The VERDICT says 5 gated and 7 with values. `ASSUMPTIONS.md:11` (A4) says "6 surviving photo-transcribed dims (… + X01 soft)". The 17 absent plus 7 valued equals 24, but the absent list at `VERDICT.md:54` includes the unassigned D-09/10/12, which are not sheet rows. How the 24 is composed is unclear.
- **Self-intersection check.** `q02b_selfint.py` targets `scratch/out_it2/OOM-B02.step`, but no JSON or log output was saved. The PASS rests on the VERDICT text only.
- **NX export.** `4_STEP/OOM-B02-exported.stp` (158 faces, from `OOM-B02_objects.prt`, 2026-07-30) is not mentioned in the VERDICT, the tracker's deliverable list or the MANIFEST notes. Who made it and why, and is it the deliverable or the build123d `OOM-B02.step`? Not recorded.
- **PDF content.** `7_docs/OOM-B02_RE_report.pdf` could not be text-extracted here. Its content was inferred from the generator `70_report.py`, and it is not verified that the shipped PDF matches the script.
- **Face counts.** The it1 STEP and the it2 STEP have identical surface-entity counts (inspection only). This is consistent with a one-parameter change; no further check was done.
- **Brand.** The "Mi/Mijia" identification (`70_report.py:132`, `TRACKER.md:13`) has no photo or label cited as its evidence.
