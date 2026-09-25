# PARAMETER TABLE — OOM-B02_Side-brush-3-arm

REBUILD **iteration 2 of 3**, 2026-07-29.
Build script: `6_RE_work/build_OOM-B02.py` (re-runnable) · Solid: `4_STEP/OOM-B02.step`
Gate result: `6_RE_work/VERDICT.md` (APPROVED it2). Assumptions ledger: `6_RE_work/ASSUMPTIONS.md`.

**it1 → it2 change (one parameter):** `SKIRT_R_FLAT` 12.420 → **12.550**. it1 applied the
photo-transcribed F06 (24.84) as a radius; the built solid then re-measured F06 = 25.487 (Δ +0.647,
OUT OF BAND). §G-1 proves 24.84 is not achievable as a two-jaw diametral reading on a 3-lobed skirt,
so F06 is **STRUCK from Tier-1** and the flat radius reverts to **scan authority**. Nothing else moved.

**SOURCE column** — `caliper-photo` = a real instrument reading transcribed from a caliper photo whose
feature attribution Muhammed confirmed 2026-07-30 (effective uncertainty **±0.1 mm**, not ±0.02) ·
`scan` = measured on the datum-aligned 798 874-tri raw scan by this agent · `photo-inferred` = neither
scan nor caliper resolves it; taken from the photographs / standard practice and **not gated**.

**No global scale correction is applied** (RE_SPEC §2). The RE_SPEC §2 envelope check could not be run
(ENV-1/2/3 empty). Absolute scale is UNVERIFIED. Confirmed caliper values are used directly as CAD
parameters, which absorbs the scan/caliper discrepancy locally.

---

## A. Datum

| name | value | SOURCE | measured | snapped | note |
|---|---|---|---|---|---|
| Datum A — rim annular face | z = 0.000 | scan | plane fit rms 0.052 over 30 342 faces; re-fit by modeller: mean z 0.0213, std 0.0849, n 17 027 | 0.000 | frozen; material occupies +Z |
| Datum B — rotation axis | +Z | scan | converged < 0.0001° | +Z | cup bore + skirt + hex common axis |
| Datum C — arm 1 centreline | θ = 0 (+X) | scan | re-measured arm centres 0.04 / 120.30 / −118.96° | 0 / 120 / −120 | 3-fold **enforced at exactly 120.00°** |
| raw-scan → datum 4×4 | see `2_mesh_cleaned/alignment.json` | scan | — | — | key `matrix_4x4`, row-major (RE_SPEC §8) |

## B. Tier-1 dimensions (caliper-photo authority — used DIRECTLY)

| name | value | SOURCE | measured | snapped | note |
|---|---|---|---|---|---|
| `CUP_BORE_D` (F03) | **20.750** | caliper-photo | caliper 20.75 · scan 20.93 | 20.750 | used directly; CAD sits 0.09 mm/side inside the scan bore |
| `HEX_DEPTH` (F02) | **3.440** | caliper-photo | caliper 3.44 · scan 3.565 (my fit) / 3.48 (intake) | 3.440 | pocket floor lands at z = 5.895 (scan reads 6.020) |
| `SKIRT_R_LOBE` (F05) | **13.425** | caliper-photo | caliper OD 26.85 · scan lobe R 13.55 | 13.425 = 26.85/2 | **scan offset −0.125 mm on the radius**, not split. F05 is the weakest of the promoted set (a max-lobe reading under-reads if the crest is missed) |
| `SKIRT_R_FLAT` (F06 STRUCK) | **12.550** | **scan** | caliper OD 24.84 (STRUCK) · scan flat R 12.55 | 12.550 | **it2 change.** F06 removed from Tier-1 per §G-1 — 24.84 is *not achievable* as a two-jaw diametral reading on a 3-lobed skirt (min achievable 25.99). Reverted to scan authority; it1's 12.420 read back +0.647 OUT OF BAND |
| `ARM_W` (F10) | **5.330** | caliper-photo | caliper 5.33 · scan mean 5.89 at the same station | 5.330 | held CONSTANT along the blade (scan width is flat to ±0.15 over r 14→37). Scanner dilation on thin sections (intake R6) → CAD sits 0.28 mm/side inside the scan |
| arm thickness @ r 36.5 (F11) | **4.070** | caliper-photo | caliper 4.07 · scan mean 4.106 at r 36.5 | 4.070 | taper toward the hub taken from the SCAN SHAPE, shifted by the −0.036 mm station offset |
| bristle ribbon fan width (X01) | 10.85 | caliper-photo | 10.85 | — | **soft, NOT modelled, NOT gated** — free-state fan |

## C. F01 — hex drive socket (the single largest risk on the part)

| name | value | SOURCE | measured | snapped | note |
|---|---|---|---|---|---|
| `HEX_AF` | **7.358** | **scan** | intake area-fit 7.358 (rms 0.037, n 7295). **Modeller's independent area-weighted opposite-flat-pair fit: 7.377** (only one of the three opposite pairs is fully scanned; the other four flats give 7.19–7.32 individually because the pocket is not perfectly axis-centred) | **NOT SNAPPED** | **NO caliper reading of any kind exists** — no photo captures it. Explicitly NOT snapped to 7.0 or 7.5 per the rebuild brief. Scan sees only ~2/3 of the hexagon (largest angular gap 92–124°). **One caliper reading on F01 changes the part's fit and must trigger a re-run.** |
| `HEX_PHASE_DEG` | 59.0 | scan | area-weighted fit **59.04°** (azimuth of a hex FLAT NORMAL, from arm 1) | 59.04 → 59.0 | equivalently −0.96° from arm 1 mod 60 — a flat normal sits essentially ON the arm-1 centreline. The intake's "50.7°" was measured in the pre-rotation frame and is not comparable |
| `HEX_CORNER_R` | 0.35 | scan | pocket AC/2 p99.5 = 4.126 vs sharp 4.248 | 0.35 | moulded corner relief |
| `HEX_FLOOR_Z` | 5.895 | derived | = cup floor 2.455 + caliper depth 3.440 | — | scan reads 6.020 → CAD 0.125 mm shallower (caliper wins) |

## D. Hub, scan authority (no caliper coverage)

| name | value | SOURCE | measured | snapped | note |
|---|---|---|---|---|---|
| `CUP_FLOOR_Z` (F04) | 2.455 | scan | p50 z = 2.456–2.459 over r 4.2–6.4 | 2.455 | intake quoted 2.566 |
| `CUP_BORE_STEP_Z` | 1.30 | scan | bore is cylindrical rim → z ≈ 1.3, then drafts | 1.30 | two-diameter bore per intake §4.6 |
| `CUP_DRAFT_DEG` | 8.0 | scan | measured p50 radius slope 7.1–10.4° over z 0.6→2.1 | 8.0 | mould draft on the upper bore |
| **annular relief GROOVE** in the cup floor | r 6.60→9.80, depth **0.337**, arc R 3.97 | scan | floor z 2.456 at r 5–6.4, rising to **2.793 at r 8.2** | — | ⚠ **The intake called this a 0.25 mm RIDGE (proud of the floor). It is a GROOVE — recessed 0.337 mm into the floor.** Present in all three sectors; corrected here |
| `BORE_D` | 2.70 | scan / photo-inferred | 2.70 at the hex-floor mouth (intake, rms 0.10) | 2.70 | interior length/profile is **100 % occluded by the fitted screw** → modelled as a **plain through-bore**, `photo-inferred`, NOT gated |
| `CBORE_D` | 7.07 | scan | intake 7.07 (rms 0.33); modeller p10 of the wall 7.0–7.2 (screw head contaminates) | 7.07 | dome-side counterbore |
| `CBORE_FLOOR_Z` | 9.543 | scan | p50 9.543 (intake 9.483) | 9.543 | counterbore wall height above the local dome = 1.08; 1.32 below the apex |
| `DOME_APEX_Z` (F07) | 10.866 | scan | p99 of clean (off-arm, off-SAF-1) sectors at r = 5.0 | 10.866 | intake quoted 10.97 (percentile choice) |
| dome meridian | 39-point spline | scan | z_hi per 0.25 mm radius ring, clean sectors, r 3.535→13.425 | — | reproduced verbatim in the script |
| `FLAT_HALF_DEG` | 16.0 | scan | folded 3-fold profile: R = 12.55 over −17…+18° about each arm | 16.0 | 3 flats sit ON the arms |
| `RAMP_DEG` | 9.0 | scan | lobe↔flat transition 8–10° | 9.0 | smoothstep |
| rim annulus width | 10.375 → 13.425 (lobe) / 12.550 (flat) | derived | scan rim band populated r 10.4→13.5 | — | the axial seating face |

## E. SAF-1 — the single 3-fold-breaking FUNCTIONAL KEY (Q1 ruling: modelled + gated ≤ 0.8 mm)

⚠ **Clocking correction.** In the frozen datum frame (`matrix_4x4`, arm 1 → +X) SAF-1 sits at
**θ = +59°**, not −71°. It is the same physical feature — the arm-1/arm-2 mid-gap — the intake used the
opposite angular sign convention. All three sub-features were re-measured by this agent.

| name | value | SOURCE | measured | snapped | note |
|---|---|---|---|---|---|
| `SAF_THETA` | **59.0°** | scan | nub centre 57.6 · skirt recess centre 60.0 · internal boss centre 61.5 | 59.0 | **coincides with a hex flat normal (59.04°) to 0.04°** — almost certainly the design intent, and it answers F15 (the key's phase to the hex) |
| `SAF_NUB_R` | 15.07 | scan | r max 15.068 | 15.07 | external nub |
| `SAF_NUB_HALF` | 4.2° | scan | θ span 53.5…61.9 = 8.4° (≈2.0 mm at r 13.5) | 4.2 | |
| `SAF_NUB_Z0/Z1` | 2.35 / 4.02 | scan | first/last z with r > 14 | — | |
| **skirt recess** `SAF_RECESS_R` | 12.40 | scan | local skirt flattening 13.44 → **12.35–12.45** over θ 42…78°, at every z from 0 to 4.6 | 12.40 | ⚠ **Not described in the intake card.** ~1.05 mm deep, 36° wide, and unique (the two 3-fold-equivalent positions read 13.55 / 13.35). Modelled — omitting it would leave a >1 mm residual at a gated interface |
| `SAF_HOLE_D` | 2.00 | scan / photo-inferred | intake Ø ≈ 2; scan resolves a radial penetration to r ≈ 11.0 at z 1.6–2.0 but cannot see the bottom | 2.00 | **held as the KEY DATUM** per the Q5 fallback |
| `SAF_HOLE_Z` | 1.75 | scan | deepest penetration z 1.6–2.0 | 1.75 | |
| `SAF_HOLE_RIN` | 9.50 | **photo-inferred** | bottom fully occluded | — | modelled as a plain radial hole through the skirt wall into the internal boss; depth NOT gated |
| **internal boss**, footprint | θ 45…78°, r 4.30…10.45 | scan | cup-interior min-z map: the pad spans θ 45–78, r 4.3–10.4 | — | two levels — see below |
| boss inner face `SAF_BOSS_Z_IN` | 1.45 | scan | z ≈ 1.35–1.60 over r 4.3–8.0 → **1.01 mm proud** of the floor | 1.45 | |
| boss outer face `SAF_BOSS_Z_OUT` | 0.35 | scan | z ≈ 0.20–0.50 over r 8.0–10.4 → **2.11 mm proud** (nearly flush with the rim) | 0.35 | intake quoted a single "1.7 mm proud"; it is a **two-level** pad |

## F. Arms (PolarArray 3 × 120.00°, path PLANAR in r–z per the Q4 ruling)

| name | value | SOURCE | measured | snapped | note |
|---|---|---|---|---|---|
| arm z-path z(r) | 22-station table in the script | scan | **3-arm MEAN** of the measured blade mid-line; per-arm zmid at r 36 = 13.50 / 14.46 / 14.75 | mean | the 1.25 mm arm-to-arm spread is free-state droop. The mean minimises the worst-case residual (0.74 mm) vs picking arm 1 (1.25 mm) |
| arm tangential drift | **NOT modelled** | — | 0.97 / 1.49 / 2.20 mm over r 13→38 | — | Q4 ruling: free-state deformation. Surfaces as a Tier-2 residual on the arm flanks — correct per RE_SPEC §3, not chased |
| blade width | 5.330 constant | caliper-photo | see §B (F10) | 5.330 | |
| blade thickness | 5.42 @ r 14 → 4.07 @ r 36.5 | scan shape + caliper | 3-arm mean thickness curve, shifted −0.036 to hit F11 exactly at the station | — | |
| `ARM_CORNER_R` | 1.05 | scan | rounded-rectangular blade section | 1.05 | |
| arm root | tapered to 41 % section at r 7.0 | scan | scan arm z_hi holds 10.50–10.57 flat from r 10 to 15 while the clean dome is 9.40 at r 10 | — | the inner extension is buried inside the dome so the union produces the observed root ridge without a floating end face |
| arm/hub blend fillet | R 0.8 (16 edges) | scan | scan blend ≈ 1–2 mm | 0.8 | **fillets applied LAST**, from the sections (RE_SPEC §3) |
| `ARM_R_END` | **38.20** | scan | plastic/bristle junction 38.23 / 38.22 / 38.19, spread 0.08 | 38.20 | hard radial trim. **Nothing beyond it is modelled** (R4). Rigid-arm swept Ø = 76.40 vs scan 76.43 |
| tuft slot | 4.60 × 3.50, R 0.40, depth 3.00 | **photo-inferred** | scan ribbon envelope 5.0 × 3.9, less the F10/F11 dilation offsets; socket interior fully occluded | — | **NOT gated.** Leaves a 0.37 / 0.29 mm collar wall — this is the "~0.5 mm collar step" of the intake |
| bristle filaments | **NOT modelled** | — | swept Ø 124.9 mean, 2.5 mm spread | — | soft ±3 mm; r > 38.5 excluded from Tier-2 (R4) |
| centre Phillips screw | **NOT modelled** | — | present in the scan at r < 3.6, z 8.6–10.4 | — | COTS. Mask it out of the Tier-2 gate reference |

## G. Honest reconciliation notes (RE_SPEC §4 honesty rule)

**G-1 — F06 (24.84) cannot be a two-jaw skirt OD.**
On a 3-lobed skirt a caliper reads `R(θ) + R(θ+180)`. The three flats are only ~34° wide and are 120°
apart, so **no antipodal flat–flat pair exists**: the minimum achievable diametral reading is
lobe + flat. Measured on the scan the achievable window is **25.99 … 27.08 mm**; on the delivered CAD it
is **25.62 … 26.85 mm** (it2). The value 24.84 is 1.15 mm below anything the scanned geometry can produce.
it1 applied it *as a radius* (`SKIRT_R_FLAT = 12.420`) and the built solid re-measured
**F06 = 25.487, Δ +0.647 — OUT OF the Tier-1 ±0.15 band.** This is a data problem, not a modelling
error: either D-05 is not a skirt OD, or the jaws were on something else.

**it2 ruling: F06 is STRUCK from Tier-1** and `SKIRT_R_FLAT` reverts to scan authority **12.550**.
Tier-1 now gates 5 dims (F02, F03, F05, F10, F11), worst **0.026 mm**. F06 is reported ungated at
CAD 25.617. Nothing was silently loosened — the dim is removed with a stated geometric proof, and
**re-measure hook:** if 24.84 was a real skirt dimension taken some other way (e.g. flat-to-axis ×2,
or a lobe-to-flat reading mis-attributed), the flat radius is 0.13 mm large and this must be re-run.

**G-2 — Tier-1 is PARTIAL: 7 of 24 dims carry a value.** The other 17 are ABSENT, not passed.

**G-3 — F01 has no caliper reading at all.** The CAD takes the scan fit 7.358 on a hexagon that is only
~2/3 scanned. This is the drive interface. One caliper reading changes the part's fit.

**G-4 — Two intake-card errors were found and corrected against the scan** (both re-measured
independently, both reproducible):
* SAF-1 sits at **θ = +59°** in the frozen datum frame, not −71° (sign convention).
* The cup-floor annular feature is a **0.337 mm GROOVE**, not a 0.25 mm proud ridge.

**G-5 — A third SAF-1 sub-feature exists that the intake did not list**: a 36°-wide, ~1.05 mm deep
**recess in the skirt outer wall** under the nub. It is modelled.

**G-6 — the arm root/tuft-collar interior, the central bore interior and the SAF-1 hole bottom are
occluded.** They are `photo-inferred` and are reported, not gated.

---

## H. Modeller's self-check — RE-MEASURED ON THE BUILT SOLID

**Method (not echoed from parameters):** `4_STEP/OOM-B02.step` re-imported with `build123d.import_step`,
tessellated at **5 µm chordal / 0.05 rad** (it2: 714 968 tri, `is_watertight = True`, volume 5799.219 mm³),
then measured geometrically with `trimesh` plane sections + **support-function (two-parallel-jaw) widths**
— i.e. the caliper is modelled as two parallel planes closing on the section, which is what the
instrument actually does. Section polylines are resampled at 0.02 mm so nothing is vertex-limited.
Script: `6_RE_work/` → `40_verify.py` pattern (kept in local scratch).

| dim | caliper | CAD (re-measured) | Δ | band ±0.15 | how it was taken |
|---|---|---|---|---|---|
| F02 hex pocket depth | 3.440 | **3.440** | +0.000 | PASS | meridian section θ=180: cup-floor z 2.4550 → pocket-floor z 5.8950 |
| F03 cup bore ID | 20.750 | **20.750** | +0.000 | PASS | plan section z=1.00, inner contour, 2·r_max (= inside-jaw max span 20.750) |
| F05 skirt OD MAX | 26.850 | **26.850** | +0.000 | PASS | plan section z=1.00, outer envelope R(θ), support width max (jaws @ 92.75°) |
| F06 skirt OD MIN *(STRUCK, ungated)* | ~~24.840~~ | **25.617** | n/a | **not gated (§G-1)** | same section, support width min (jaws @ 59.00°). **24.84 is not achievable on a 3-lobed skirt; the scan itself only reaches 25.99.** Struck at it2; flat radius reverts to scan 12.550 |
| F10 arm width @ r 36.5 | 5.330 | **5.330** | +0.000 | PASS | section normal to the arm path at the caliper station |
| F11 arm thickness @ r 36.5 | 4.070 | **4.096** | +0.026 | PASS | same section (Δ is the section-plane normal estimate, not a modelling error) |
| F01 hex AF *(scan, ungated)* | 7.358 | **7.358** | −0.000 | n/a | plan section at mid-pocket, minimum support width; AC 8.388 |

**Envelope / form checks on the built solid**

| quantity | CAD | scan | note |
|---|---|---|---|
| rigid arm-tip swept Ø | 76.400 | 76.43 | plastic ends at r = 38.20 |
| overall height, rim → highest plastic | 17.156 | 17.10 (p99.9) / 17.29 (max) | |
| dome apex z | 10.866 | 10.866 | |
| volume | 5799.2 mm³ (tess) / 5801.1 mm³ (BRep) | — | ≈5.3 g in PP |
| bbox | x −21.357…38.200 · y −34.332…34.332 · z 0.000…17.156 | | |

**Tier-2 — the gate that counts is in `6_RE_work/VERDICT.md`** (independent ICP + outer-skin mask,
QA script `q20_tier2.py`). Headline it2 result, reproduced here for convenience:

| zone | n | mean | p95 | max | band | verdict |
|---|---|---|---|---|---|---|
| **WHOLE PART** (outer skin, bristles + screw excluded) | 234 850 | 0.221 | **0.742** | **2.523** | p95 ≤ 1.6 / max ≤ 4.0 | **PASS** |
| rim annulus (datum A) | 13 125 | 0.099 | 0.246 | **0.650** | max ≤ 0.8 | **PASS** |
| hex pocket F01 *(124° gap masked, A6)* | 5 157 | 0.099 | 0.235 | **0.314** | max ≤ 0.8 | **PASS** |
| SAF-1 external nub | 476 | 0.176 | 0.528 | **0.649** | max ≤ 0.8 | **PASS** |
| SAF-1 skirt recess | 482 | 0.179 | 0.470 | **0.751** | max ≤ 0.8 | **PASS** |
| SAF-1 internal boss *(interior, A7)* | 2 572 | 0.242 | 0.798 | 1.560 | reported | not gated |
| cup bore wall *(Tier-1 F03)* | 8 118 | 0.118 | 0.264 | 1.402 | reported | not gated |
| cup floor *(interior)* | 18 706 | 0.060 | 0.132 | 0.513 | reported | not gated |
| skirt band z 0–4.5 *(Tier-1 F05)* | 19 923 | 0.113 | 0.213 | 2.523 | reported | not gated |
| dome, off-arm off-SAF *(cosmetic)* | 33 940 | 0.144 | 0.279 | 1.529 | reported | not gated |
| arms r 14–38.2 *(free-state droop, A11)* | 95 900 | 0.335 | 0.891 | 1.326 | reported | not gated |
| arm/hub root r 7–14 *(blend)* | 46 063 | 0.181 | 0.617 | 2.523 | reported | not gated |

The three it1 sub-band failures are all resolved or correctly re-scoped at it2: the **hex pocket**
1.846 → **0.314** once the 124° scan gap is masked (it was distance to a hole edge, not to a surface);
the **SAF-1 skirt recess** 0.826 → **0.751** under the independent ICP fit; the **SAF-1 internal boss**
is declared an interior/occluded bucket per RE_SPEC §4 (A7) and reported at 1.560, not gated.
The arm tail is the un-modelled free-state droop and tangential drift (Q4 ruling, A11).
