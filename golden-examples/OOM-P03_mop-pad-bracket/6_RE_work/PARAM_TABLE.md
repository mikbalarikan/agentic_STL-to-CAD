# PARAM TABLE — OOM-P03 Mop Pad Bracket  (rebuild it2, stl2step-build123d)

> it2 changes (QA REVISE): (1) added the central drive STEM (hexagonal AF~11, top +18.56)
> + square drive socket above the hex — the scan "spike" I wrongly dismissed as occlusion in
> it1 was REAL (verifier confirmed, 158k coherent verts). F03=11.05 still governs the HEX
> protrusion; the stem sits above it. (2) ENV-Z re-derived to 21.57. (3) alignment.json
> matrix_4x4 refined by best-fit ICP (0.405° / 0.093 mm correction). Tier-1 unchanged (dead-on).

Datum: hex/rotation axis → +Z (toward DRIVE side); PAD-attach velcro field plane → Z=0;
origin on rotation axis (least-squares rim-circle centre). Composite raw-scan→datum
transform in `2_mesh_cleaned/alignment.json` (`matrix_4x4`, row-major 4×4). No scale
applied (caliper ENV-D1 127.54 vs scan rim 127.84, ratio 0.998 — single-axis check, RE_SPEC §2).

SOURCE = caliper (Tier-1 authority, used directly) / scan / photo-inferred.
"CAD re-measure" = value re-measured on the built STEP solid in the self-gate.

## Tier-1 CALIPER parameters (used DIRECTLY as CAD params; verifier gates |CAD−caliper| ≤ 0.15)
| Param | Feature | Caliper | CAD param | CAD re-measure | Δ | SOURCE | Snap note |
|---|---|---|---|---|---|---|---|
| ENV-D1 | solid-rim OD | 127.54 | 127.54 | 127.540 | +0.000 | caliper | no snap (used as read) |
| W01 | rim edge wall thickness | 3.27 | 3.27 | 3.270 | +0.000 | caliper | mean of 3.25/3.28 |
| F01 | hex boss across-flats | 13.95 | 13.95 (AF) | 13.951 | +0.001 | caliper | mean of 3 reads 13.96/13.92/13.97 (spread 0.05) |
| F03 | hex protrusion above drive-face floor | 11.05 | 11.05 | 11.050 | −0.000 | caliper | hex tip = drive face(+2.85) + 11.05 = +13.90 |
| F05 | pad-side central boss OD | 33.46 | 33.46 | 33.460 | +0.000 | caliper | no snap |
| F06 | hub disc OD (= kidney-opening INNER edge) | 68.61 | 68.61 | 68.603 | −0.007 | caliper | hub is solid disc; openings start at this Ø |
| F07 | spoke-disc / mid-ring OD (= opening OUTER edge) | 89.33 | 89.33 | 89.313 | −0.017 | caliper | openings end at this Ø; solid band beyond |
| **Tier-1 worst |Δ|** | | | | **0.022 mm** | | | all ≪ 0.15 |

## SCAN-authority parameters (form / axial levels; not Tier-1 gated)
| Param | Feature | Value | SOURCE | Note |
|---|---|---|---|---|
| — | plate/pad field plane Z | 0.000 | datum | pad-attach (velcro) field |
| — | drive-face plane Z | +2.85 | scan | W03 plate thickness ≈ 2.85 |
| — | rim pad-side face Z | −0.42 | derived | = drive(+2.85) − W01(3.27) |
| — | pad-boss bottom Z | −3.01 | scan | boss proud 3.01 below pad field |
| F02 | hex across-corners | 16.11 | scan/geom | = AF·2/√3 (auto from regular hex); CAD 16.09 |
| F09 | tread slot count | ~51 (pitch 7.0°) | scan | cosmetic "tyre tread"; modeled 51 through-slots r58.6–63.4 |
| — | kidney opening count | **8** | scan | FFT F[8]=144.6 dominant; spokes @45° (25°+k·45°); openings @2.5°+k·45° |
| — | kidney angular width | ~29.2° (spoke ~15.8°) | scan | matfrac 0.35 solid at opening ring |
| — | kidney radial span | Ø68.61–89.33 | caliper bounds | inner=F06, outer=F07 |
| W02 | spoke web | ang. width ~15.8° | scan | spoke = solid bit between kidneys |
| — | central drive STEM across-flats | 10.96 (hex) | scan | hexagonal post above the hex; flats r5.48, corners r6.41, F[6]=20.2 dominant; corners @48°+k·60° |
| — | STEM top Z | +18.56 | scan | 158k coherent raw verts; solid flat top |
| — | STEM square drive socket | 5.5 sq × 2.5 deep | photo-inferred | recess in stem tip (IMG_140345/347); scanner bridged it so depth is photo-set, shallow |
| ENV-Z | overall height (pad-boss-bottom → stem top) | **21.57** | scan-derived | −3.01 → +18.56; matches intake scan ~21.5; CAD re-measure 21.570 |

## PHOTO-INFERRED / intent
| Param | Decision | SOURCE | Note |
|---|---|---|---|
| F04 | NO central bore through hex/boss — modeled SOLID (stem has a shallow square socket only) | photo-inferred | pad-side centre shows only mold-gate dimple; hex is solid, drive socket is in the stem tip |
| velcro grip field | nominal flat plane (Z=0), texture NOT modeled | photo/intake | scanner cannot resolve micro-texture |
| cosmetics (red ring, "FlexiArm Design", QR, "A2") | NOT modeled | photo | printed/engraved, not geometry |
| hub concentric styling rings | NOT modeled (hub = plain solid disc) | photo | cosmetic grooves; F06 Ø68.61 preserved as opening inner edge |

## REJECTED / corrected source values
| Item | Intake/sheet value | Correction | Basis |
|---|---|---|---|
| F08 tread OD | scan-guess ~139–141 | REJECTED → true OD tips Ø128.6; rim body Ø127.54 | raw-frame PCA radial was tilt-inflated; BOTH raw (12.5M-vert) and work meshes cap at r=64.32 in datum frame; clean rim circle fit Ø127.84 resSD 0.039 |
| kidney openings | intake "≈6 outer + ≈6 inner" | CORRECTED → 8 openings, single ring; hub disc SOLID (no inner ring) | angular FFT F[8]=144.6, spokes at exact 45° spacing |
