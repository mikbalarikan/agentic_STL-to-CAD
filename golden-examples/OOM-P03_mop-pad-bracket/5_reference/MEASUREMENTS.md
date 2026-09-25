# MEASUREMENTS — OOM-P03 Mop Pad Bracket

<!-- Analyst PRE-FILLED the ID/Feature/Type/Why columns (the MEASUREMENT REQUEST).
     Muhammed fills "Caliper (mm)". Record AS READ (no rounding). Measure critical dims
     twice; if reads differ >0.05 mm record both. Soft/flexible features: note "soft".
     Unreachable: write N/A, never guess.
     NOTE: several photos already show a caliper ON the feature — the cited reading is a
     hint only; please re-measure and enter your own value. -->

Instrument: digital caliper ±0.02 mm (Mitutoyo Absolute; use depth gauge where noted)
Date measured: 2026-07-29 (readings TRANSCRIBED FROM CALIPER PHOTOS by line manager on
Muhammed's direction "use measurement images and proceed" — no separate re-measure.
Dims with no photo coverage fall back to SCAN authority per RE_SPEC §2 and are NOT
Tier-1 gated; they are listed as `scan` below.)

## A. Envelope (mandatory — drives the unit check & global scale correction)
| ID | Feature | Caliper (mm) | Notes |
|---|---|---|---|
| ENV-D1 | Outer diameter across the **solid rim** (jaws on the white rim body, NOT on the tread castellations) — one axis. Photo `IMG_20260729_140327.jpg` (shows ≈127.5) | 127.54 | photo-read `140327` (display 127.54); consistent with scan back-solve 127–129 → **no global scale correction** (single-axis check only) |
| ENV-D2 | Outer diameter, **second axis ~90° to ENV-D1** (same solid rim) — roundness/scale cross-check | scan | no photo; scan authority (roundness check by verifier on scan) |
| ENV-Z | Overall height: PAD face plane → tip of the hex drive boss (depth gauge or caliper depth blade). Profile photos `IMG_20260729_140345/140347.jpg` | scan | no direct photo reading; scan ≈21.5 + F03 cross-check |

## B. Functional dimensions (analyst-requested, priority order)
| ID | Feature | Type | Why it matters | Caliper (mm) | Notes |
|---|---|---|---|---|---|
| F01 | Central hex drive boss — **across flats (AF)** | OD/flat | Motor torque-coupling fit — critical | 13.96 / 13.92 / 13.97 | photo-read `140217/140235/140238`, three different flat pairs; **mean 13.95** → use 13.95, hex regularity good (spread 0.05) |
| F02 | Central hex drive boss — **across corners** | OD | Confirms hex size/orientation | scan | no photo; geometric AF×2/√3 ≈ 16.11 — verifier checks on scan |
| F03 | Hex drive boss — **protrusion height** above the drive-face floor around it | depth | Coupling engagement length | 11.05 | photo-read `140242` (display 11.05); `140245` second read blurry but consistent ≈11.0 |
| F04 | Central **bore at hex-boss tip / pad-side centre**, if present — diameter & depth | ID/depth | Retention screw vs mold gate (see intake §4) | N/A (solid) | photo-inferred from `140419`: pad-side centre shows only a small mold-gate dimple, no bore; hex tip closed in `140217/140235/140238` → model SOLID |
| F05 | Pad-side **central round boss OD** (Ø≈33.5) | OD | Cloth centring / coupling housing | 33.46 | photo-read `140419` (display 33.46) |
| F06 | **Central hub disc OD** on drive face (Ø≈68.6) | OD | Inner structural ring diameter | 68.61 | photo-read `140306` (display 68.61) |
| F07 | **Spoke-disc / mid-ring OD** (Ø≈89.3) | OD | Mid structural ring diameter | 89.33 | photo-read `140345` AND `140347` — both display 89.33 (two independent shots agree) |
| F08 | Outer diameter **over the tread castellations** (max, over the "tread" tips) | OD | Distinguishes styled-rim OD from ENV-D1 solid-rim OD | scan | no photo; scan authority (envelope ~139–141) |
| F09 | **Tread-slot pitch**: measure across N adjacent rim slots (e.g. span of 10 slots) and note N | pitch | Locks the rim polar-pattern count | scan | no photo; modeler locks count from scan sections |

## C. Walls
| ID | Feature | Type | Why it matters | Caliper (mm) | Notes |
|---|---|---|---|---|---|
| W01 | Outer rim / plate edge **wall thickness** | wall | Mold wall; base revolve thickness | 3.25 / 3.28 | photo-read `140403` (3.25) and `140456` (3.28), two spots → **use 3.27 ±0.02** |
| W02 | **Spoke web thickness** (a single radial spoke on the drive face) | wall | Rib/web thickness for pattern | scan | no photo; scan authority |
| W03 | PAD-face **plate thickness** near centre (pad face → drive-face floor, excluding boss) | wall | Dish/plate body thickness | scan | no photo; scan authority |

## D. Extra dims Muhammed measured on his own initiative
| ID | Feature | Caliper (mm) | Notes |
|---|---|---|---|
| X01 | | | |
