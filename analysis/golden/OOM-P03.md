# OOM-P03 — evidence extraction

Project root: `golden-examples/OOM-P03_mop-pad-bracket/` (abbreviated `P03/` below; every `P03/...` path = `golden-examples/OOM-P03_mop-pad-bracket/...`).

## 0. Record inventory

Method-bearing:
- `P03/6_RE_work/INTAKE_CARD.md`: intake by "re-mesh-analyst" (the v2 role), covering scan health, functional zones Z1–Z7, interior enumeration, datum plan, strategy, risks and the measurement request.
- `P03/5_reference/MEASUREMENTS.md`: caliper sheet. Values were **transcribed from caliper photos** by the line manager; nobody re-measured at the bench (`:70-73`).
- `P03/6_RE_work/PARAM_TABLE.md`: it2 parameter table with a SOURCE tag on each row, the it2 change log (`:119-123`) and rejected/corrected values (`:171-175`).
- `P03/6_RE_work/rebuild_OOM-P03.py`: the only code in the record, a build123d rebuild with a self-check print block.
- `P03/6_RE_work/VERDICT.md`: independent QA verdict for it2 (APPROVED). It includes the it1 finding closeout. The it1 VERDICT was overwritten and is not in the record.
- `P03/2_mesh_cleaned/alignment.json`: datum transform `matrix_4x4`, with prose fields for axis source and refinement.
- `P03/6_RE_work/sections/*.png`: 3 CAD-over-scan section overlays (axial meridian, drive-face polar at the kidney level, tread polar).
- `P03/7_docs/OOM-P03_RE_report.pdf`: 7-page report. It repeats PARAM_TABLE/VERDICT and adds the "partial scan ~270°" caveat (p.7 §6.3) and a Figure 1 caption interpreting the overlay (p.5).
- `P03/MANIFEST.json`: file list, exclusions, and the provenance of the decimated scan (`#excluded[path=2_mesh_cleaned/OOM-P03.stl].decimated_copy`).
- `P03/Context images/`: 11 phone photos `IMG_20260729_*.jpg` (most show a caliper on a feature) plus 2 web product images (`images.jpg`, `S85960...avif`).
- `baseline/oomwoo-re-pipeline/TRACKER.md:31`: the P03 tracker row, which carries extra facts (see §9).

Pure outputs: `P03/4_STEP/OOM-P03.step` (build123d/OCC export, `:1-8` header), `P03/4_STEP/OOM-P03_cad.stl`, `P03/4_STEP/OOM-P03-exported.stp` + `.log` (NX2206 AP242 re-export, 559 advanced_face; `P03/4_STEP/OOM-P03-exported.log:17`), `P03/7_docs/OOM-P03_{front,iso,side,top,scan_vs_cad}.png`, `P03/2_mesh_cleaned/OOM-P03_work_250k.stl`, `P03/2_mesh_cleaned/OOM-P03_scan_decimated.stl` (950k-tri stand-in for the excluded 209 MB `OOM-P03.stl`).

Missing from the record: no MODELING_PLAN and no intake views or caliper-guide images. The it1 STEP, the it1 VERDICT, the QA scripts and the analysis scripts (circle fit, FFT, ICP) are also absent. `alignment_v2.json`, which VERDICT cites (`P03/6_RE_work/VERDICT.md:50`), is absent too.

## 1. Part class and geometry type

- **Part:** the rotating mop-pad carrier plate for the OOMWOO robot mop. A disposable round microfibre cloth attaches to its velcro face, and the plate is spun through a central hex coupling (`P03/6_RE_work/INTAKE_CARD.md:6-23`).
- **Material/process:** "molded white ABS/PP" (`INTAKE_CARD.md:11`). This comes from the intake reading and was never confirmed.
- **Geometry class:** a turned/revolved thin plate with polar patterns, i.e. mixed revolve + polar cuts + prismatic hex boss/stem (`INTAKE_CARD.md:85-96`).
- **Envelope:**
  - Solid rim Ø127.54 (caliper)
  - Tread tips Ø128.6 (scan)
  - Overall height 21.57, from the pad-boss bottom at −3.01 to the stem top at +18.56 (`P03/6_RE_work/PARAM_TABLE.md:136,161,174`)
  - STEP bbox 127.540 × 127.540 × 21.570 (`P03/6_RE_work/VERDICT.md:14`)
- **Symmetry:**
  - Rotational about Z
  - 8-fold kidney openings
  - 6-fold hex boss and hex stem
  - 51-fold cosmetic tread slots
  - No mirror plane (`PARAM_TABLE.md:153-158`, `INTAKE_CARD.md:95-96`)
- **Cosmetics not modelled:** red ring, "FlexiArm Design" text, QR code, "A2", hub styling rings, velcro micro-texture (`PARAM_TABLE.md:163-169`).

## 2. Stages actually run, in order

This part was delivered on 2026-07-29 (`baseline/oomwoo-re-pipeline/TRACKER.md:31`). That is **before** RE_SPEC v3 (2026-08-01, `baseline/oomwoo-re-pipeline/CHANGES_V3.md:1`) and v4 (2026-08-02, `baseline/oomwoo-re-pipeline/RE_SPEC.md:2`). It therefore ran the **v2 line**: re-mesh-analyst → modeler → re-qa-verifier → docs, with a PDF report. It did not run the v3/v4 re-planner / re-drafter / manager feature loop, and the baseline `agents/re-*.md` do not describe how it ran. Evidence: the "re-mesh-analyst" byline (`P03/6_RE_work/INTAKE_CARD.md:3`); the rebuild docstring citing "RE_SPEC v2 s2" (`P03/6_RE_work/rebuild_OOM-P03.py:9`); the PDF deliverable, which v3 retired (`CHANGES_V3.md:63-64`).

1. **Scan** (raw 4,187,542 tris, exported unwelded) → `1_scan_raw_STL/`, excluded (`P03/MANIFEST.json#excluded`); original `2_mesh_cleaned/OOM-P03.stl`, excluded.
2. **Weld + decimate working copy** → `P03/2_mesh_cleaned/OOM-P03_work_250k.stl`, quadric, 250k tris (`INTAKE_CARD.md:31-34`).
3. **Intake (re-mesh-analyst)**, using photos + mesh → `P03/6_RE_work/INTAKE_CARD.md` (dated 2026-07-29, `:4`).
4. **Measurement request → external gate.** The sheet was pre-filled (`P03/5_reference/MEASUREMENTS.md:62-67`). The gate was closed by a waiver: Muhammed directed "use measurement images and proceed", and the line manager transcribed 7 dims from caliper photos (`MEASUREMENTS.md:70-73`; `TRACKER.md:31` "Muhammed waived re-measure").
5. **Datum/alignment** → `P03/2_mesh_cleaned/alignment.json` (PCA normal + Kåsa rim-circle fit).
6. **Scan analysis:** angular FFT for counts; radial cap for OD; levels for the axial planes → recorded only as numbers in `PARAM_TABLE.md:145-161`. The scripts are not in the record.
7. **Rebuild it1** → `4_STEP/OOM-P03.step`, overwritten. It had no drive stem (`PARAM_TABLE.md:119-121`).
8. **Modeler self-gate:** Tier-1 CAD re-measure, worst |Δ| 0.022 → `PARAM_TABLE.md:133-143`. The it1 self-gate numbers were not recorded.
9. **Independent QA it1 → REVISE**, missing central drive stem. VERDICT was overwritten; summary at `P03/6_RE_work/VERDICT.md:8,41,49-50`.
10. **Rebuild it2:** stem + socket added, ENV-Z re-derived, alignment ICP-refined → `P03/6_RE_work/rebuild_OOM-P03.py`, `P03/4_STEP/OOM-P03.step` (header 2026-07-29T16:16:07), `alignment.json#refinement`.
11. **Independent QA it2 → APPROVED**, 4 gates → `P03/6_RE_work/VERDICT.md`.
12. **Section overlays** → `P03/6_RE_work/sections/*.png`.
13. **DOCS:** renders + PDF report → `P03/7_docs/*.png`, `P03/7_docs/OOM-P03_RE_report.pdf`.
14. **NX re-export of the STEP** (AP242, 17:37 on 2026-07-29) → `P03/4_STEP/OOM-P03-exported.stp`/`.log`. Nothing in the record says who did it or why.

v3/v4 stages that did **not** run: MODELING_PLAN + feature budget; F00 datum gate with `--datum` views; per-feature manager review; GitHub issue/PR; caliper-guide images; Tier-0 surface-quality audit; QA datum audit against the 0.3°/0.15 mm thresholds; reverse-direction Tier-2; README.md deliverable. No such artefacts exist in `P03/`.

## 3. Datum / alignment method

- **Primary axis:** the disc normal ≈[0.334, 0.846, −0.415] in raw coordinates is mapped to +Z, pointing toward the DRIVE/hex side (`P03/6_RE_work/INTAKE_CARD.md:77-78`). Direction = "PCA flat-face normal (126k verts)" (`P03/2_mesh_cleaned/alignment.json#axis_source`).
- **Z = 0:** the PAD-attach velcro field plane, taken as the median (`alignment.json#axis_source`). This is a textured, scanner-unresolvable surface (`INTAKE_CARD.md:42-44`), used anyway as the level datum.
- **Origin XY:** least-squares Kåsa circle fit on the outer edge of the solid rim, with a residual SD of 0.039 mm (`alignment.json#axis_source`; `P03/6_RE_work/PARAM_TABLE.md:174`).
- **Clocking (rotation about Z):** not recorded. The kidney phase (openings at 2.5°+k·45°) and stem phase (corners at 48°+k·60°) were measured in the resulting frame (`PARAM_TABLE.md:154,158`). The tread slots were given phase 0 (`P03/6_RE_work/rebuild_OOM-P03.py:134`), which the tracker calls "phase unaligned" (`baseline/oomwoo-re-pipeline/TRACKER.md:31`).
- **Scale:** none applied. ENV-D1 caliper 127.54 vs scan rim 127.84 gives a ratio of 0.998. Only one axis was checked, because ENV-D2 has no reading (`alignment.json#description`; `P03/5_reference/MEASUREMENTS.md:79`).
- **Refinement (it2):** `matrix_4x4` refined by best-fit ICP (Kabsch, 90%-trimmed) of the scan's outer skin **to the CAD**. The correction was 0.405° / 0.093 mm, made "to match verifier ICP frame" (`alignment.json#refinement`; `PARAM_TABLE.md:122-123`).
- **QA comparison:** the verifier's own best-fit ICP sits 0.154° / 0.600 mm from the refined alignment (it1: 1.651 mm) (`P03/6_RE_work/VERDICT.md:50`).
- **Missing schema fields:** the file has no schema-v2 keys (`scale_factor`, `scan_noise_mm`, `primary`/`secondary` fit RMS/max, `origin.definition`) (compare `baseline/oomwoo-re-pipeline/RE_SPEC.md:142-157`).
- **Rejected datum reading:** a naive PCA radial p99.9 read an OD of 139 mm, inflated by axis tilt, and was rejected. Both the raw and work meshes cap at r = 64.32 in the datum frame (`INTAKE_CARD.md:45-47`; `alignment.json#notes`).
- *Inspection only* (my run, applying `matrix_4x4` to the decimated scan `P03/2_mesh_cleaned/OOM-P03_scan_decimated.stl`): aligned bounds x −62.42…63.99, y −60.82…64.00, z −3.07…18.50. The −X/−Y side stops short of the rim radius, which is consistent with the report's "partial scan ~270°" (`P03/7_docs/OOM-P03_RE_report.pdf` p.7 §6.3).

## 4. Measurement methods

| Method | Tool/function | What | Result | Source |
|---|---|---|---|---|
| Caliper photos, transcribed | Mitutoyo digital caliper ±0.02; value read off the display in a photo by the line manager | ENV-D1, F01 ×3, F03, F05, F06, F07 ×2, W01 ×2 | 127.54; 13.96/13.92/13.97 → mean 13.95; 11.05; 33.46; 68.61; 89.33/89.33; 3.25/3.28 → 3.27 | `P03/5_reference/MEASUREMENTS.md:69-98` |
| Photo IDs per read | photos `140327`, `140217/140235/140238`, `140242` (`140245` blurry), `140419`, `140306`, `140345/140347`, `140403/140456` | per-dim provenance | — | `MEASUREMENTS.md:78-98` |
| Mesh health | trimesh 4.12.2 vertex merge | watertight, components, boundary edges | NO; 1 component; euler −129; 16,578 open boundary edges; 2,101,931 merged verts | `P03/6_RE_work/INTAKE_CARD.md:31-36` |
| Axis direction | PCA on flat-face verts | disc normal | 126k verts; normal ≈[0.334,0.846,−0.415] raw | `alignment.json#axis_source`; `INTAKE_CARD.md:30` |
| Rim circle | Kåsa least-squares circle fit | rim OD / XY centre | Ø127.84, resSD 0.039 | `P03/6_RE_work/PARAM_TABLE.md:174` |
| Radial cap | max radius in datum frame | tread tip OD | r = 64.32 → Ø128.6 | `PARAM_TABLE.md:174` |
| Angular FFT of radius/material vs θ | FFT, not recorded which library | kidney count | F[8] = 144.6 dominant → 8; spokes 25°+k·45° | `PARAM_TABLE.md:154` |
| Material fraction vs θ | "matfrac 0.35 solid" | kidney angular width | ~29.2° opening, ~15.8° spoke | `PARAM_TABLE.md:155-157` |
| Angular FFT, stem band | FFT | stem shape | F[6] = 20.2 dominant; flats r5.48, corners r6.41 → hex AF 10.96; corners at 48°+k·60° | `PARAM_TABLE.md:158` |
| Axial levels | scan levels (method not recorded) | drive face, pad-boss bottom, stem top | +2.85; −3.01; +18.56 ("158k coherent raw verts") | `PARAM_TABLE.md:149-161` |
| Tread pitch | scan | slot count | ~51, pitch 7.0° | `PARAM_TABLE.md:153` |
| Photo intent | visual | F04 bore vs mould gate; socket | no bore (dimple only, `140419`); square socket 5.5 × 2.5 deep (`140345/347`) | `PARAM_TABLE.md:160,166`; `MEASUREMENTS.md:88` |
| QA stem check | angular FFT of raw-scan r(θ) in the stem band | stem polygon order | order 6, mag 9.41; r min 5.54 / max 6.87 | `P03/6_RE_work/VERDICT.md:49` |
| QA Tier-1 | STEP feature queries (analytic radii, opposite-flat plane distance, cap-plane Z) | 7 caliper dims | all \|Δ\| < 0.005 | `VERDICT.md:17-29` |
| QA Tier-2 | trimmed KDTree ICP, 120k pts, 30 iters; 900k scan samples → 700k CAD-sample KDTree; skin mask scan·CAD-normal > 0.3 | deviation | see §7 | `VERDICT.md:31-42` |
| Section overlays | not recorded (matplotlib-style PNGs) | meridian at a spoke of 25°; polar z = 1.4; tread band | visual | `P03/6_RE_work/sections/*.png` |

Photo use: the photos drove (a) all Tier-1 values, through caliper-on-feature shots; (b) part identification and the functional-vs-cosmetic split (`INTAKE_CARD.md:6-23,41-44`); (c) intent decisions F04 and the socket; (d) QA Gate 4 plausibility (`VERDICT.md:44-46`).

The profile photo `P03/Context images/IMG_20260729_140345.jpg`, used for F07, clearly shows the square-socketed stem standing proud of the hex. So does the web image `P03/Context images/images.jpg`. The stem was therefore visible in the inputs before it1, yet the intake did not enumerate it (`INTAKE_CARD.md:60-74` lists only "central hex boss … check for a central bore").

## 5. Design-intent rounding

| Feature | Measured | Chosen | Rule used | Source |
|---|---|---|---|---|
| ENV-D1 rim OD | 127.54 (photo caliper); scan 127.84 | 127.54 | caliper used directly, no snap | `PARAM_TABLE.md:136` |
| W01 wall | 3.25 / 3.28 | 3.27 | mean of two reads | `PARAM_TABLE.md:137` |
| F01 hex AF | 13.96 / 13.92 / 13.97 | 13.95 | mean of 3 reads; no standard-size snap | `PARAM_TABLE.md:138` |
| F02 hex across-corners | — | 16.11 (CAD 16.09) | derived from AF·2/√3 | `PARAM_TABLE.md:152` |
| F03 hex protrusion | 11.05 | 11.05 | caliper direct | `PARAM_TABLE.md:139` |
| F05, F06, F07 | 33.46, 68.61, 89.33 | same | caliper direct; F06/F07 reused as kidney inner/outer radii | `PARAM_TABLE.md:140-142,156` |
| Drive-face Z | scan | +2.85 | scan level (no rounding stated) | `PARAM_TABLE.md:149` |
| Pad-boss bottom Z | scan | −3.01 | scan level | `PARAM_TABLE.md:150` |
| Rim underside Z | derived | −0.42 | = 2.85 − W01 (wall forced to caliper) | `PARAM_TABLE.md:151` |
| Stem AF | flats r5.48 | 10.96 | 2 × r_flat; hex (FFT order 6) | `PARAM_TABLE.md:158` |
| Stem top | scan | +18.56 | scan level; drives ENV-Z = 21.57 | `PARAM_TABLE.md:159-161` |
| Kidney count/phase/width | FFT F[8]; ~29.2° | 8, 2.5°+k·45°, half-width 14.6° | polar symmetry enforced | `PARAM_TABLE.md:154-155`; `rebuild_OOM-P03.py:29-31` |
| Tread | ~51, pitch 7.0° | 51 slots, r58.6–63.4, half-width 2.4°, phase 0 | polar count; phase not fitted | `PARAM_TABLE.md:153`; `rebuild_OOM-P03.py:32-35` |
| Socket | not scan-visible | 5.5 sq × 2.5 deep | photo-inferred | `PARAM_TABLE.md:160` |
| Kidney corner R / tread corner R / stem-top fillet | not recorded | 3.0 / 1.0 / 0.4 | not recorded (in code only) | `rebuild_OOM-P03.py:131,136,154` |
| Velcro field | textured | flat plane Z = 0 | nominal restoration | `PARAM_TABLE.md:167` |
| F08 tread OD | intake guess ~139–141 | rejected; tips Ø128.6 | tilt artefact | `PARAM_TABLE.md:174` |
| Opening layout | intake "≈6 outer + ≈6 inner" | 8, single ring, solid hub | FFT correction | `PARAM_TABLE.md:175` |

## 6. Feature tree

From `P03/6_RE_work/rebuild_OOM-P03.py`:

1. **Base revolve** (`:56-79`): an 8-point closed half-section on Plane.XZ, revolved about Axis.Z. Points: axis at Z_DRIVE (2.85) → R_RIM at Z_DRIVE → R_RIM at Z_RIMBOT (−0.42) → R_MID (44.665) at Z_RIMBOT → R_MID at Z_PAD (0) → R_BOSS (16.73) at Z_PAD → R_BOSS at Z_PADBOSS (−3.01) → axis.
   - The plate is solid between Z 0 and 2.85. It has no dish.
   - There is a safety mirror if the volume is ≤ 0.
2. **Hex boss** (`:81-86`): RegularPolygon(radius = HEX_AF/√3, 6, major_radius = True) on Z_DRIVE, extruded by HEX_PROTR = 11.05.
3. **Drive stem** (it2, `:88-94`): hex RegularPolygon(radius = STEM_AF/√3 = 6.328, rotation = STEM_ROT 48°) at Z_HEXTIP 13.90, extruded to STEM_TOP 18.56.
4. **Socket tool** (it2, `:96-101`): Rectangle(SOCKET_SQ 5.5) at STEM_TOP − SOCKET_DEPTH 2.5, extruded 3.0.
5. **Cut tools** (`:103-136`): `sector_tool` = an annular sector with 2D vertex fillets, extruded.
   - 8 kidney sectors between R_HUB and R_MID, corner R 3.0, Z −1 → 3.85.
   - 51 tread sectors between r 58.6 and 63.4, corner R 1.0, Z −0.92 → 3.35.
   - The loop comment still says "6-fold" (`:127`) while N_KIDNEY = 8.
6. **Boolean assembly** (`:138-146`): base + hex + stem; minus the fused tools; minus the socket.
7. **Fillet** (`:148-156`): stem-top outer edges R0.4, with socket-rim edges filtered out by `center().length > SOCKET_SQ`. This runs inside try/except. `FILLET_SMALL = 0.6` is defined but unused (`:36`).
8. **Validate & export** (`:158-184`): prints volume, is_valid, bbox and solid count; asserts v > 0; exports STEP, STL and a fine gauge STL (tol 0.02).

## 7. Gates run, with actual numbers

All bands come from `_PIPELINE/RE_SPEC.md §4` as cited in `P03/6_RE_work/VERDICT.md:7`: Tier-1 ≤0.15; Tier-2 p95 ≤1.6, max ≤4.0; non-caliper functional ≤0.8. The same numbers appear in `baseline/oomwoo-re-pipeline/RE_SPEC.md:166-177`.

| Gate | Threshold (origin) | Measured | Result | Source |
|---|---|---|---|---|
| G1 validity | 1 valid solid, positive volume | 1 solid, 1 shell, BRepCheck IsValid True; vol 35535.0 mm³; 500 faces / 2986 edges; dz 21.570; COM x,y = 0 | PASS | `VERDICT.md:12-14` |
| G2 Tier-1 (QA) | \|Δ\| ≤ 0.15 (RE_SPEC §4) | worst 0.000 (ENV-D1 127.540, F01 13.950, F03 11.050, F05 33.460, F06 68.610, F07 89.330, W01 3.270) | PASS | `VERDICT.md:16-29` |
| Tier-1 modeler self-gate | ≤ 0.15 | worst 0.022 (F07 −0.017, F06 −0.007) | PASS (not authoritative) | `PARAM_TABLE.md:133-143` |
| G3 Tier-2 outer skin | p95 ≤ 1.6, max ≤ 4.0 | n 769k; p95 0.971; max 2.949 | PASS | `VERDICT.md:34-36` |
| Tier-2 skin, r < 9 | — | n 37k; p95 0.882; max 2.949 | reported | `VERDICT.md:37` |
| Tier-2 skin, excluding r < 9 | — | n 731k; p95 0.972; max 2.604 | reported | `VERDICT.md:38` |
| Interior/occluded | not gated | n 131k; p95 2.101; max 2.968 | reported | `VERDICT.md:39` |
| Skin points > 4.0 / > 1.6 | — | 0 (it1: 4907); 0.26% | — | `VERDICT.md:41` |
| Functional zones (skin) | ≤ 0.8 for non-caliper interfaces | rim OD p95 0.296 / max 0.565; pad boss p95 0.241; hex r6–12 p95 0.689 (max not recorded); stem r<7, z>13 p95 0.810 / max 2.424 | not tabulated as PASS/FAIL. Stem max 2.424 accepted as intent deviation at the photo-inferred socket | `VERDICT.md:42` |
| G4 photo plausibility | visual | 8 kidneys, hex, ~51 tread, pad boss, stem + socket present; nothing hallucinated | PASS | `VERDICT.md:44-46` |
| Alignment vs QA best fit | none stated in v2 (v3 audit ≤ 0.3° / ≤ 0.15 mm, `baseline/oomwoo-re-pipeline/RE_SPEC.md:239-242`) | 0.154° / 0.600 mm (it1: 1.651 mm) | "within tolerance for the doc-overlay render"; non-blocking note | `VERDICT.md:50,56` |
| Decimated-copy fidelity | — | decimated → original p50 0.00104 / p95 0.00521 / max 0.0277 (20k samples, seed 0) | provenance only | `P03/MANIFEST.json#excluded[2_mesh_cleaned/OOM-P03.stl].decimated_copy.dev_decimated_to_original_mm` |
| Tier-0 surface quality | not run (v3 concept) | STEP has 500 faces (`VERDICT.md:13`); % analytic not recorded | not run | — |
| Reverse direction (scan → CAD vs CAD → scan) | not run as a separate report | only one direction is described (scan samples → CAD KDTree) | — | `VERDICT.md:32` |

Scan used by QA: "900k raw-scan surface samples" (`VERDICT.md:32`). That points to the full-resolution scan, but the file actually used is not recorded.

*Inspection only, not a grade* (my run: decimated scan + `alignment.json` + `OOM-P03_cad.stl`, 200k/400k random samples, no ICP, no skin mask, unseeded):
- Unmasked scan→CAD p50 0.240 / p95 1.382 / max 2.947.
- Stem zone (r < 7, z > 13) p95 1.126 on 2,215 points.
- CAD STL volume 35519.0 mm³, watertight, bbox ±63.77 × −3.01…18.56.

## 8. Iterations

**Iteration 1: REVISE** (the it1 VERDICT was overwritten; evidence is reconstructed from the it2 record).
- **What QA found:**
  - **Finding 1, missing central drive stem.** The it1 CAD ended at the hex tip (z +13.90). The scan has material on the axis up to z ≈ 18.56: 4907 outer-skin points deviated > 4.0 mm, at r < 6.4, z ~18. That breaks the Tier-2 max band of 4.0 (`P03/6_RE_work/VERDICT.md:8,41`; `P03/7_docs/OOM-P03_RE_report.pdf` p.2 "Verdict history").
  - **Finding 3, alignment.json 1.651 mm off QA best fit** (`VERDICT.md:50`).
  - **Finding 2:** not recorded. PARAM_TABLE lists "(2) ENV-Z re-derived to 21.57" among the it2 changes, which suggests ENV-Z was wrong in it1, but the it1 value is not recorded (`P03/6_RE_work/PARAM_TABLE.md:122`).
  - The it1 Tier-1 and Tier-2 p95 numbers are not recorded.
- **Root cause:**
  - The modeler saw a scan "spike" on the axis and **"wrongly dismissed [it] as occlusion"** (`PARAM_TABLE.md:119-121`). QA proved it real: 158k coherent raw verts, a solid flat top (`PARAM_TABLE.md:159`; report p.2).
  - Upstream, the intake's interior/feature enumeration never listed a stem. It anticipated only a possible bore at the hex tip (`P03/6_RE_work/INTAKE_CARD.md:69-72`).
  - ENV-Z was defined as "PAD face plane → tip of the hex drive boss" (`P03/5_reference/MEASUREMENTS.md:80`), which bakes the omission into the envelope definition.
  - The intake's own risk list primed the dismissal: it named "occlusion holes under the hex boss" (`INTAKE_CARD.md:37-40,99-101`).
  - The profile photos `140345/140347` (used for F07) and `images.jpg` show the socketed stem. The photo evidence was available but not cross-checked against the "occlusion" reading (my visual read of `P03/Context images/IMG_20260729_140345.jpg`).
- **Fix (it2):**
  1. Added a hexagonal stem AF 10.96 (flats r5.48 from scan; FFT order 6), rotated 48°, from +13.90 to +18.56, plus a photo-inferred square socket 5.5 × 2.5 (`P03/6_RE_work/rebuild_OOM-P03.py:44-52,88-101,146`).
  2. ENV-Z re-derived as −3.01 → +18.56 = 21.57 (`PARAM_TABLE.md:161`).
  3. `alignment.json` refined by trimmed Kabsch ICP to the CAD, 0.405° / 0.093 mm (`P03/2_mesh_cleaned/alignment.json#refinement`).
  4. Tier-1 was "unchanged (dead-on)": F03 still governs the hex, and the stem sits above it (`PARAM_TABLE.md:123`; `VERDICT.md:29`).

**Iteration 2: APPROVED.**
- The verifier checked the stem independently (FFT order 6, mag 9.41; r 5.54/6.87; stem p95 0.810) and found no skin points > 4 mm (`VERDICT.md:41,49,54`).
- Outer skin p95 0.971 / max 2.949; Tier-1 worst 0.000.
- Non-blocking notes carried forward: the socket is photo-inferred (stem max 2.424 where the scanner bridged the cavity), and the alignment is 0.600 mm from QA best fit (`VERDICT.md:53-59`).
- The part used 2 of 3 allowed loops (`VERDICT.md:3`).

## 9. Declared limitations and assumptions

- **Calipers transcribed from photos**, not a bench session; Muhammed waived the re-measure (`P03/5_reference/MEASUREMENTS.md:70-73`; `P03/7_docs/OOM-P03_RE_report.pdf` p.2 "Measurement provenance"). The tracker lists them as "7 dims photo-transcribed … 8 dims → scan authority" (`baseline/oomwoo-re-pipeline/TRACKER.md:31`). ENV-D2, ENV-Z, F02, F08, F09, W02 and W03 have no caliper and fall back to scan authority, not Tier-1 gated (`MEASUREMENTS.md:79-100`).
- **Scale was checked on one axis only**: ratio 0.998, no scale applied (`P03/2_mesh_cleaned/alignment.json#description`).
- **Square socket 5.5 × 2.5 is photo-inferred**; the scanner bridged it. Flag for physical confirmation "if the coupling interface is ever manufactured to fit" (`P03/6_RE_work/VERDICT.md:55`; report p.7 §6.1).
- **F04 no bore** is photo-inferred; the part is modelled SOLID (`P03/6_RE_work/PARAM_TABLE.md:166`).
- **Scan not watertight**: 16,578 boundary edges. Occluded/interior buckets are reported, not gated (interior p95 2.101 / max 2.968) (`P03/6_RE_work/INTAKE_CARD.md:35-40`; `VERDICT.md:39`).
- **Velcro texture** is modelled as a flat nominal surface and excluded from the gate (`PARAM_TABLE.md:167`).
- **Cosmetics and hub styling rings** are not modelled (`PARAM_TABLE.md:168-169`). The report's Figure 1 caption says orange (larger deviation) concentrates at "the cosmetic hub-ring band (not modelled), the photo-inferred stem socket, and one under-covered tread arc — all reported-not-gated zones" (report p.5).
- **Partial scan ~270°**, one face better covered, carried by rotational symmetry (report p.7 §6.3; `TRACKER.md:31`). The intake card does not state this.
- **Source STL exported unwelded**, welded on import (report p.7 §6.3; `INTAKE_CARD.md:32-34`).
- **Tread slots:** ~51, cosmetic, "phase unaligned" (`TRACKER.md:31`). This caveat is not in VERDICT or the report.
- **Alignment** is 0.600 mm from QA best fit, "adequate for renders" (`VERDICT.md:56`).
- **Stem-zone max 2.424** exceeds the ≤0.8 functional-interface band (`baseline/oomwoo-re-pipeline/RE_SPEC.md:175`). QA explained it as intent deviation at the bridged socket (`VERDICT.md:42`). The stem was not a named intake zone (`INTAKE_CARD.md:49-58`), so the band was never formally applied to it.

## 10. Deviations from the baseline skill

- **Pipeline version.** The project ran the v2 roles (re-mesh-analyst / modeler / verifier + PDF), not v3/v4 (re-planner / re-drafter / manager feature loop, MODELING_PLAN, F00, GitHub, README), per `baseline/agents/re-planner.md`, `baseline/agents/re-drafter.md` and `baseline/oomwoo-re-pipeline/RE_SPEC.md:185-253`. It is grandfathered under `RE_SPEC.md:338-340`. **Did it help?** It is unclear. The it1 miss (stem) is the kind of failure v3 feature review plus an ENV-Z caliper would plausibly catch earlier. On the other hand, a single script with ~8 features passed at it2.
- **Caliper authority vs photo transcription.** RE_SPEC treats calipers as measured with ±0.05 mm (`RE_SPEC.md:89-92`). Here the values were read off photos. Tier-1 then gates CAD against numbers whose own uncertainty is not re-established (the tracker records ±0.1 effective for similar parts B02/E05, `TRACKER.md:13,17`, but not for P03).
- **Datum.** The baseline skill says to use the largest flat facet plus RANSAC for the primary, and to fit the axis from normals, never from bbox (`baseline/skills/stl2step-build123d/SKILL.md:23-39,95`). P03 used a PCA normal plus a Kåsa rim-circle centre (not from normals, but also not bbox) and a *median* Z of a textured field (`alignment.json#axis_source`). No fit residual was recorded for the plane, contrary to `RE_SPEC.md:126-129`. It then **refined the datum by ICP to its own CAD** (`alignment.json#refinement`). That makes the datum partly CAD-derived, circular with respect to the gate. v3 later requires an independent datum audit ≤ 0.15 mm (`RE_SPEC.md:239-242`); P03's 0.600 mm would FAIL that audit.
- **Deviation bands.** The skill's default bands are p95 ≤ 0.3 / max ≤ 0.8 for consumer plastics (`SKILL.md:87`). P03 used RE_SPEC's scan-adjusted p95 ≤ 1.6 / max ≤ 4.0 (`VERDICT.md:7`). Its unmasked p95 of 0.971 would FAIL the skill's band.
- **Deviation direction.** The skill asks for two-way deviation (`SKILL.md:75-86`); VERDICT reports one direction plus a skin mask (`VERDICT.md:32`).
- **Pattern modelling.** The skill says to model one instance plus `PolarLocations` (`SKILL.md:70`). The script builds 59 tool solids in Python loops and fuses them (`rebuild_OOM-P03.py:126-145`). The result is equivalent geometrically, but it is not a pattern feature.
- **Section overlays** were produced as the skill requires (`SKILL.md:90`; `P03/6_RE_work/sections/`). This helped: the polar FFT corrected the intake's "6 + 6" openings to 8 (`PARAM_TABLE.md:175`).
- **Standard-size snap** (`RE_SPEC.md:92,160`; `SKILL.md:54`) was not applied. Calipers were used as read (e.g. hex AF 13.95, not snapped to 14). This is consistent with caliper authority.

## 11. Reusable code

| file:function | What it does | Generality | Determinism concerns |
|---|---|---|---|
| `P03/6_RE_work/rebuild_OOM-P03.py` (top-level, `:56-79`) | closed r–z polyline half-profile → `revolve(Axis.Z)` | needs generalising (profile points → parameter) | deterministic |
| `rebuild_OOM-P03.py:sector_tool` (`:104-124`) | annular-sector cut solid with 2D corner fillets (try/except skip) | reusable as-is for polar slots/windows | a silent fillet skip changes geometry without failing (prints only) |
| `rebuild_OOM-P03.py` hex/stem blocks (`:82-94`) | RegularPolygon(AF/√3, major_radius=True) extrude; rotation param | reusable (hex AF → circumradius idiom) | deterministic |
| `rebuild_OOM-P03.py` fillet block (`:148-156`) | edge filter by Z position + radius, fillet in try/except | needs generalising | a silent skip is possible |
| `rebuild_OOM-P03.py` validate/export (`:158-184`) | volume / is_valid / bbox / solid-count print; STEP + STL + fine gauge STL (tol 0.02) | reusable pattern | `is_valid` getattr shim for build123d version drift |
| Analysis/QA code (circle fit, FFT, ICP, skin mask, Tier-1 feature queries) | — | **not in record** | — |

## 12. Lessons

1. **Treat an unexplained on-axis or above-feature point cluster as real until disproven.** Count the coherent verts, check a flat top, and cross-check the profile photos before calling it occlusion. (Failure: `P03/6_RE_work/PARAM_TABLE.md:119-121`; `P03/6_RE_work/VERDICT.md:41,49`.)
2. **Intake must enumerate features from the profile photos.** An envelope height should be defined to the true topmost feature, not to the "expected" one. (Failure: `P03/5_reference/MEASUREMENTS.md:80` hex-tip ENV-Z; `P03/Context images/IMG_20260729_140345.jpg` shows the stem.)
3. **QA Tier-2 zone buckets (e.g. r < 9 on the axis) and a "points > max band" location report pinpoint missing features.** It1's 4907 points at r < 6.4, z ~18 localised the defect. (Success: `VERDICT.md:37,41`.)
4. **Lock polar counts by angular FFT on sections, not by eye.** The intake's "6 + 6" became 8 (F[8] = 144.6), and QA re-used FFT for the stem polygon order. (Success: `PARAM_TABLE.md:154,175`; `VERDICT.md:49`.)
5. **Reject PCA/percentile radial reads on a tilted raw frame; measure radii only after datuming.** 139 → 128.6. (Success: `P03/6_RE_work/INTAKE_CARD.md:45-47`; `P03/2_mesh_cleaned/alignment.json#notes`.)
6. **For revolved parts, a circle fit on a clean rim gives the axis origin**, here with resSD 0.039. (Success: `alignment.json#axis_source`.)
7. **Do not refine the datum by ICP against your own CAD and then gate with it.** Keep an independent datum, and report the QA datum offset against an explicit threshold (0.600 mm here would fail v3's 0.15 mm). (Limitation: `alignment.json#refinement`; `VERDICT.md:50`; `baseline/oomwoo-re-pipeline/RE_SPEC.md:239-242`.)
8. **Photo-transcribed calipers must carry the photo ID per value and a provenance note in every deliverable.** This worked well here. Their effective uncertainty should be stated. (Success/limitation: `MEASUREMENTS.md:70-98`; report p.2.)
9. **Record intent-inferred features (socket, no-bore) with an explicit "confirm physically" flag, and exclude their scan deviation from the verdict with a stated reason.** (Success: `VERDICT.md:55`; report p.7.)
10. **Features discovered after intake (the stem) must be added as named functional zones with a band.** Otherwise the ≤0.8 interface band is silently never applied (stem max 2.424). (Limitation: `VERDICT.md:42`; `INTAKE_CARD.md:49-58`.)
11. **Phase-align cosmetic polar patterns to the scan, or declare them unaligned in the verdict/report, not only in the tracker.** (Limitation: `rebuild_OOM-P03.py:134`; `baseline/oomwoo-re-pipeline/TRACKER.md:31`.)
12. **State partial angular coverage in the intake card** (it appeared first in the report) and show it in the aligned bounds. (Limitation: report p.7 §6.3; §3 inspection here.)
13. **Keep the previous iteration's VERDICT and STEP** (e.g. `_it1_SUPERSEDED/`) rather than overwriting in place. Here the it1 evidence is only reconstructible second-hand. (Limitation: `VERDICT.md:6` "overwritten in place".)
14. **Keep code comments in sync with parameters** ("6-fold" vs N_KIDNEY = 8). (Minor: `rebuild_OOM-P03.py:127`.)

## Questions

- **it1 record absent.** The it1 VERDICT was overwritten (`VERDICT.md:6`). Finding 2's content, the it1 Tier-1/Tier-2 numbers, and the it1 ENV-Z value are not recorded.
- **`alignment_v2.json`.** `VERDICT.md:50` compares against "refined `alignment_v2.json`", but only `2_mesh_cleaned/alignment.json` exists. Are they the same content?
- **Photo ID mismatch.** `MEASUREMENTS.md:85,88` cite photo `140238`, which is not in `Context images/` (the folder has 140217, 140235, 140242, 140245, …). This may be a typo for 140242/140245. F03 is attributed to 140242.
- **Face-count mismatch.** VERDICT reports 500 faces (`VERDICT.md:13`); the NX re-export has 559 advanced_face (`4_STEP/OOM-P03-exported.log:17`). Who made `OOM-P03-exported.stp`, why, and which file is the deliverable?
- **Dish vs flat plate.** The report says the base revolve includes "walls and dish" (report p.2), but the code profile is a flat solid slab from Z 0 to 2.85 (`rebuild_OOM-P03.py:58-67`). The meridian overlay (`6_RE_work/sections/section_axial_meridian.png`) shows scan contours (a step near r ≈ 17–20; a surface at z ≈ −1 for r ≈ 7–14) that the CAD does not follow. This is my visual read; it was not quantified.
- **Tier-2 source file.** The file behind QA's "900k raw-scan surface samples" (full-res `OOM-P03.stl` or another copy) is not recorded, and neither are the ICP seed and trim fraction.
- **Kidney count vs photos.** In the photo `IMG_20260729_140345.jpg` the drive face appears to show fewer and larger openings than 8. The count was decided by scan FFT; no photo count is recorded.
- **Uncertainty of photo-transcribed calipers.** Not stated for P03. The tracker states ±0.1 mm effective for B02/E05, but not for P03.
