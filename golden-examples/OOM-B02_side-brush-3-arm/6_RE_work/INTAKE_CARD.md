# INTAKE CARD — OOM-B02_Side-brush-3-arm

Produced by `re-mesh-analyst`, 2026-07-29. Scan: `2_mesh_cleaned/OOM-B02.stl` (Revopoint project in
`1_scan_raw_STL/OOM-B02`, voxel 0.1 mm, markers removed). Local work copies:
`OOM-B02_raw.stl` (798 874 tri) → `OOM-B02_work_200k.stl` (199 999 tri) → `OOM-B02_work_datum.stl` (datum-aligned).
Every number below was measured on the 200 k work mesh and **re-confirmed on the full 798 k raw mesh**
(all agreed within 0.06 mm; deltas noted where larger). Plots: `B02_A…B02_J*.png` in this folder.

---

## 1. What it is (from photos + mesh)

Three-arm robot-vacuum **side brush** (sweeper), single-piece white moulding (PP/POM-like) carrying
**one flat bristle tuft per arm**, plus **one installed cross-recess (Phillips) steel screw** at the centre.

* Mounts on the side-brush **motor output shaft**: the shaft is a **male hex** that enters the
  hex pocket in the hub cup; the screw passes through the hub from the floor-facing (dome) side and
  threads into the shaft end for axial retention. Cup **rim annulus** is the axial seating face.
* Rotating part. The **cup opens toward the motor (−Z in service)**; the domed side faces the floor;
  the three arms sweep out and downward and flick debris into the main-brush path.
* Drive torque is taken by the **hex** (form fit), not by friction — so hex AF and pocket depth are the
  two critical functional dims.
* The screw is a **COTS fastener that is present in the scan**; it is NOT part of the moulding and must be
  excluded from the STEP (or modelled as a separate body). Photo `IMG_20260729_181847.jpg`,
  `IMG_20260729_182318.jpg` (screw head), `IMG_20260729_182142.jpg`, `IMG_20260729_182250.jpg` (hex pocket).

---

## 2. Scan health

| Item | Value |
|---|---|
| Units | **mm confirmed** — scanner config voxel 0.1 mm; scan hub OD 25.0–27.3 brackets the photo-transcribed caliper 26.85/26.80 (`IMG_20260729_182048/182203`). **No global scale correction indicated — do not apply one until MEASUREMENTS.md exists.** |
| bbox (raw scanner coords) | 95.80 × 99.46 × 66.14 mm; min (−65.65, −62.54, −292.04), max (30.16, 36.92, −225.89) |
| bbox (datum coords, see §5) | X −33.28…+62.12, Y −55.60…+53.88, Z −0.39…+36.72 |
| Topology | 1 connected component, winding consistent, **NOT watertight**, Euler −56, **`mesh.volume` is NEGATIVE (−2434 mm³) → face normals point INWARD. Modeller/QA must flip before any signed-distance work.** |
| Open boundary | 3561 open edges in **21 boundary loops**; **9 loops lie entirely inside r < 20 mm (the hub)** |
| Decimation | 798 874 → 199 999 tri (quadric). Raw re-check reproduced every listed dim to ≤ 0.06 mm |
| Surface roughness floor | median face-adjacency angle 3–4° on moulded surfaces vs 10–17° on bristles (used as the plastic/bristle discriminator, `B02_D`) |

**Occlusion / hole map** (datum coords; `B02_E`, `B02_J`):

| Zone | r (mm) | z (mm) | θ (deg) | Note |
|---|---|---|---|---|
| 3 bristle-tuft envelopes | 32→63 | −2→+25 | at each arm | expected — filaments cannot be closed; 3 largest loops |
| **hex pocket wall** | 2.5–4.1 | +2.6→+6.1 | all | **largest angular gap 124° — only ~2/3 of the hex is scanned** |
| cup rim + inner wall under arm 2 | 12.2–19.4 | −0.3→+7.1 | −33…+40 | biggest single hub occlusion |
| cup inner wall patch | 9.6–10.7 | −0.2→+2.2 | −165…−88 | |
| rim outer edge | 13.3–13.8 | −0.2→+0.8 | +48…+88 | |
| **SAF‑1 wall hole** (see §4) | 10.8–14.7 | +1.2→+4.9 | −77…−64 | scanner could not see inside the hole |
| arm‑2 underside | 20.8–26.1 | +7.3→+8.5 | −2…+1 | small |

**Artifact zones:** (a) the fitted screw occludes the whole central bore — the moulded bore/boss under
the screw head **cannot be resolved**; (b) bristle tufts are splayed free-state, ±1.3 mm scatter arm-to-arm;
(c) scan reads ~0.4–0.8 mm **oversize on thin arm sections** vs the photo-transcribed caliper values
(5.8–6.3 scan vs 5.33 caliper on arm width) — classic scanner dilation, **an offset not a scale**;
calipers are authority per RE_SPEC §2.

---

## 3. Functional surfaces & interfaces (gate zones)

| Zone | Surface | Why functional | Caliper-coverable? |
|---|---|---|---|
| **F01 hex drive pocket** | 6-flat pocket, **AF = 7.358 mm** (raw fit, rms 0.037, n=7295), AC = 8.496; bottom at Z=+6.045; **depth 3.48 mm below cup floor / 6.05 mm below rim**; clocking phase 50.7° from arm 1 | takes ALL drive torque | YES (knife-edge jaws, 3.5 mm reach) |
| **F02 cup rim annular face** | flat annulus r 10.83→13.41 (width 2.58), **flat to 0.052 mm std over 30 342 faces** | axial seat against the motor boss; primary datum | YES (as a depth/step) |
| **F03 cup bore** | Ø **20.93** at the rim, Ø 20.41 higher up (≈1.4° draft), depth rim→floor **2.566 mm** | spigot/pilot onto the motor hub | YES |
| **F04 central screw bore** | Ø **2.70** measured at its mouth in the hex-pocket floor (rms 0.10); dome-side counterbore Ø **7.07** (rms 0.33), floor at Z=+9.48, i.e. 1.49 below the dome apex; screw head OD ≈ 5.4–6.0, head top 0.67 below apex | axial retention | YES **only after the screw is removed** |
| **F05 hub skirt OD (3-lobed)** | **R 13.55 at the three inter-arm lobes, R 12.56 on the three flats that sit at the arms**; caliper-equivalent width max **27.29** / min **24.95** (lug excluded) | clearance to the chassis pocket; visual | YES |
| **F06 rigid arm** | straight tapered blade, tangential width 5.8→6.3, thickness 5.3 (root) → 3.9 (tip), moulded upward sweep | drives the tufts; stiffness | YES |
| **F07 tuft socket / arm outer end** | last plastic section 5.8 × 4.5 mm at r = 38.2, then a **step/collar** and the tuft | holds the tuft | partly (outside only) |
| **F08 dome outer surface** | convex dome, apex Z = +10.97, r ≈ 2–6 | cosmetic + floor clearance | height only |
| SAF‑1 | see §4 — the only 3-fold-breaking feature | unknown | YES (hole Ø) |

---

## 4. INTERIOR structure (mandatory — explicit enumeration)

Looked *through* the cup opening and through every boundary loop (`B02_E` height map, `B02_F`, `B02_H`):

1. **Cup floor** — flat annulus at Z = +2.566, r 4.2 → 10.4.
2. **Shallow annular ridge on the cup floor** — r ≈ 6.5–9.5, ~**0.25 mm** proud of the floor (visible in
   `B02_B`/`B02_J` as the step at Z ≈ +2.8). Concentric; present in all three sectors.
3. **Hex drive pocket** — walls r 3.6 (flat) / 4.25 (corner), floor at Z = +6.045.
4. **Central through-bore** Ø ≈ 2.70 from the hex-pocket floor to the dome counterbore — **interior length
   and any internal boss/rib around it are FULLY OCCLUDED by the fitted screw: cannot resolve.**
5. **Dome-side counterbore** Ø ≈ 7.07 × 1.49 deep, with the screw head seated in it.
6. **Cup inner wall step** — the wall is Ø 20.93 from the rim up to Z ≈ +1.3, then Ø 20.41 (draft).
7. **SAF‑1 — the only asymmetric feature.** At **θ ≈ −71°** from arm 1 (exactly the arm‑1/arm‑2 mid-gap,
   nominal −60° in a 3-fold pattern → sits 11° off the mid-gap):
   * an **internal raised boss** on the cup floor, r ≈ 5–9, standing **1.7 mm** proud of the floor
     (up to Z ≈ +0.85, i.e. almost flush with the rim) — clearly present in sector 1/2, **absent in
     sector 3** (`B02_H` left panel: floor min-z −11.0 vs −9.3 baseline);
   * an **external nub** on the skirt, r 13.00 → **15.07**, Z +2.35…+4.02, ~8.6° wide (≈2.1 mm);
   * a **Ø ≈ 2 mm hole** through the skirt wall at the same clocking, with black debris/filament in it
     (photo `IMG_20260729_182109.jpg` — pad with dark hole; also visible at the rim in `IMG_20260729_182231.jpg`).
   * The skirt outer surface is **fully scanned all the way round**, so the other two positions are
     genuinely empty — this is a **real 3-fold break**, not an occlusion.
   * **Function not resolved** from scan or photos. Candidates: injection gate / runner witness,
     tufting-jig locating hole, or an assembly-orientation key. **→ Question for Muhammed (§7 Q1).**
8. **No ribs, webs, gussets or bosses of any other kind** exist inside the cup — the interior is a plain
   stepped cup. (Explicitly checked against the M02 v1 lesson; the height map `B02_E` top-left has full
   floor coverage across all 360°.)
9. **No tuft holes anywhere.** See §6/§7 — this is **not** a staple-set brush.

---

## 5. Datum plan

* **Primary (A):** cup **rim annular face** → **XY plane, Z = 0**; material occupies +Z.
  Fitted plane RMS **0.052 mm** over 30 342 raw faces — an excellent datum.
* **Secondary (B):** rotation axis = common axis of the cup bore + skirt + hex pocket → **+Z**.
  Axis found by iterated rim-plane fit + robust circle fit; converged to < 0.0001° / < 0.001 mm.
* **Tertiary (C):** **arm 1 centreline → +X (θ = 0)**; arms 2 and 3 then fall at +120° and −120°.
* Composite **raw-scan → datum 4×4** (row-major; apply to the RAW scan; also stored as
  `_final_transform.npy`, and must be written into `2_mesh_cleaned/alignment.json` as `matrix_4x4`
  by the modeller per RE_SPEC §8):

```
[[ 0.741893674, -0.488623777,  0.459173802, 115.342985717],
 [ 0.588848755,  0.802325404, -0.097627297,  -1.214737412],
 [-0.320703788,  0.342812996,  0.882965645, 262.877336658],
 [ 0.000000000,  0.000000000,  0.000000000,   1.000000000]]
```

Key Z stations in datum coords: rim 0 · cup floor +2.566 · hex-pocket floor +6.045 ·
counterbore floor +9.483 · dome apex +10.970 · top of rigid plastic +17.63 · highest bristle tip +36.72.

---

## 6. Rebuild strategy per region (build123d)

| Region | Strategy |
|---|---|
| Hub body of revolution | **Revolve** the meridian profile of `B02_B` about Z: rim face, cup bore + step, cup floor + 0.25 mm annular ridge, hex-pocket counterbore, central bore, dome, dome-side counterbore. This gets ~80 % of the hub in one operation. |
| Skirt 3-lobe outline | **Extrude-intersect / boolean**: revolve at R = 13.55, then cut three R‑12.56 scallops on a **polar pattern (3 × 120°) clocked ON the arms**; blend into the dome. |
| Hex pocket | **Extrude-cut** a regular hexagon (AF from calipers) from the cup floor, depth 3.48; clocked at 50.7° from arm 1 mod 60° (scan value — verify against a photo before freezing, `IMG_20260729_182142.jpg`). |
| Arms (×3) | Build **one** arm as a **sweep** of a rounded-rectangular section (5.8→6.3 wide × 5.3→3.9 thick, lofted/scaled along the path) along a spline path, then **PolarArray(3, 120°)**. Path: r 13 → 38.2 with **z rise 11.4 / 11.8 / 12.8 mm** (dominant, and repeatable → design intent). There is also a **tangential drift of 0.97 / 1.49 / 2.20 mm** over the same span — the arm-to-arm spread (1.2 mm) is as large as the value itself, so **treat the tangential component as free-state deformation and model the path planar in r–z** unless the photos say otherwise (`IMG_20260729_181846.jpg` shows the arms visually straight in plan). Flag in the report. |
| Arm/hub blend | Fillet from sections, last. |
| Tuft socket / collar | Model the collar + a blind slot at the arm end; **do not model filaments**. |
| Bristles | **Not modelled.** Exclude from the STEP and from the Tier‑2 gate (see §7). |
| Screw | **Not modelled** in `OOM-B02.step` (COTS). Mask it out of the Tier‑2 gate reference too — it occupies r < 3.6, Z +8.6…+10.4. |
| Symmetry to enforce | Revolve axis = Z; **PolarArray 3 × 120.00°** for arms + skirt scallops; **no mirror plane** (SAF‑1 breaks it; and it is a chiral moulded sweep). |

---

## 7. Risk flags

* **R1 — Hex AF is the single most important number and the scan only sees ~2/3 of it.**
  Fit is tight (rms 0.037) at **AF 7.358 / AC 8.496**, but 124° of the hexagon is missing. If calipers
  say 7.0 or 7.4, take the caliper. **Do not intent-snap to 7.0 without a caliper.**
* **R2 — Central bore, boss and thread-engagement depth are UNRESOLVABLE while the screw is fitted.**
  Ø 2.70 is measured at the pocket-floor mouth only. **Needs the screw out.** If Muhammed will not remove
  it, the bore becomes photo/standard-inferred (M3 clearance 3.2 or ST2.9) and must be flagged in the report.
* **R3 — SAF‑1 breaks 3-fold symmetry** (§4.7). **RULED 2026-07-29 (Muhammed): FUNCTIONAL KEY.**
  → SAF‑1 **is modelled** as a single-instance feature (hole + external nub + internal cup-floor boss) and is a
  **named functional interface**, so per RE_SPEC §4 it is gated at **Tier‑2 max ≤ 0.8 mm** wherever calipers do not
  cover it. Its **clocking relative to the hex** is now a held dim (MEASUREMENTS F15). Remaining open (non-blocking,
  Q5): what it keys into, and whether the hole / nub / boss is the working feature — fallback is to hold the hole.
* **R4 — Bristles are a SOFT feature.** Free-state splay gives per-arm swept diameters of
  126.18 / 123.67 / 124.85 mm → **2.52 mm spread with zero manufacturing meaning.**
  **Declared soft band: ±3 mm on any bristle dimension. Bristle zone (r > 38.5 mm) is EXCLUDED from the
  Tier‑2 scan gate** (mask by radius in datum coords). Only the plastic (r ≤ 38.5) is gated.
* **R5 — Arms are moulded curved, NOT deformed.** The three junction radii agree to **0.08 mm**
  (38.23/38.22/38.19) and the three angular spacings to ±0.8° — this is design intent and must be
  reproduced as a swept 3D path. Do **not** "straighten" the arms.
* **R6 — Scanner dilation ~0.4–0.8 mm on thin sections** (arm width scan 5.8–6.3 vs caliper 5.33).
  Expect the arm-section CAD (caliper-driven) to sit *inside* the scan skin; that deviation is CORRECT
  per RE_SPEC §3 — report it, don't chase it.
* **R7 — Hub OD is 3-lobed**, so a single caliper number is ambiguous. Two readings are requested (§8 M4/M5).
* **R8 — Not watertight + inward normals.** Any signed-distance/deviation work must flip normals first.
**RULINGS 2026-07-29 (Muhammed) — Q1–Q4 CLOSED, full text in `5_reference/MEASUREMENTS.md` §C2:**

* **Q1 SAF‑1 → FUNCTIONAL KEY.** Modelled and gated; dims promoted to F13–F16. See R3.
* **Q2 screw removal → YES.** The central bore, boss and thread engagement stop being photo-inferred;
  new dims F08 / F17 / F18. The screw itself stays a COTS item: excluded from `OOM-B02.step` and masked out
  of the Tier‑2 gate reference (r < 3.6, Z +8.6…+10.4).
* **Q3 functional reading → CONFIRMED** (cup toward the motor, dome to the floor, hex takes the torque,
  rim annulus is the axial seat). Datum plan of §5 stands.
* **Q4 arm path → PLANAR in r–z**, tangential drift treated as free-state deformation and NOT modelled.
  It will surface as a reported Tier‑2 deviation on the arm flanks — correct per RE_SPEC §3, not chased.
* *Open, non-blocking (Q5):* what SAF‑1 keys into, and whether hole / nub / boss is the working feature.

---

### 3-FOLD SYMMETRY — measured result (CONFIRMED)

| Test | Result |
|---|---|
| Best self-registration angle, hub r < 20 mm (200 k) | **120.30°** |
| Best self-registration angle, full rigid zone r < 40 mm (200 k) | **119.90°** |
| Best self-registration angle, hub r < 20 mm (**raw 798 k**) | **120.00°** |
| Residual at exactly 120°, raw hub (60 k sample pts, NN distance) | median **0.125**, p95 **0.992**, max **2.605** mm |
| Arm angular centres (raw, r 19–34 mm) | **−128.44° / −8.02° / +112.36°** |
| Measured spacings | **120.42° / 120.38° / 119.20°** → mean 120.00°, spread ±0.8° |
| Arm junction radii (bristle start) | 38.23 / 38.22 / 38.19 mm → spread **0.08 mm** |

**Verdict: 3-fold rotational symmetry at 120.00° is CONFIRMED** to within ±0.8° angular / ~1.0 mm p95
(scanner noise floor is 0.5–0.8 mm, so the residual is at the noise floor). Model with `PolarArray(3, 120°)`.
**Exception: SAF‑1 (§4.7) is a genuine single-instance feature.**

### SWEPT DIAMETERS — measured result

| Quantity | Value |
|---|---|
| **Bristle-tip swept Ø (SOFT)** | per arm 126.18 / 123.67 / 125.15 mm (raw) → **mean 124.9 mm, spread 2.5 mm** |
| **Rigid arm-tip Ø (hub structure only, bristles excluded)** | per arm 76.46 / 76.43 / 76.38 → **76.43 mm, spread 0.08 mm** |
| Rigid-arm developed arc length, r 12 → tuft junction | 35.3 / 34.8 / 36.4 mm |
| Tuft developed length (junction → tip) | 37.8 / 33.0 / 36.5 mm (soft) |
| Static plan footprint (not a swept circle) | 95.4 × 109.5 mm |

### BRISTLE / TUFT ANCHORS — measured result (REFUTES the multi-tuft-hole assumption)

* **Tufts per arm: exactly ONE. Three tufts total.** Confirmed independently by (a) the roughness step in
  `B02_D` — a single continuous rough band per arm from r 38.5 to the tip, and (b) every photo
  (`IMG_20260729_181846/181847/181853`).
* **There are NO tuft holes / sockets / staple pattern anywhere on the hub or arms.** The tuft is a flat
  filament ribbon anchored inside the **outer end of the arm** — an in-moulded / heat-staked flat bundle,
  not a drilled-and-stapled tuft. There is therefore **no anchor-hole diameter and no tuft pitch to report.**
* **Anchor position (per arm, datum coords):** junction at r = **38.2 mm**, Z = +3.6 / +4.3 / +4.5,
  θ = 0 / +120 / −120°. Last plastic cross-section **5.78–6.18 wide × 4.13–4.55 thick**; the tuft ribbon
  leaves at **4.92–5.14 wide × 3.78–4.09 thick**, i.e. the plastic forms a **~0.5 mm collar/step** round the
  ribbon (`B02_G`, right column — the step is unmistakable at r 37.3–38.5).
* **The socket interior (depth, taper, retention) is fully occluded — CANNOT RESOLVE from the scan.**
  Recommend modelling a blind slot ≈5.0 × 3.9 mm, depth photo-inferred, and declaring it non-gated.
* **SOFT-FEATURE DECLARATION:** everything at **r > 38.5 mm is bristle**. Declared tolerance band **±3 mm**;
  **excluded from the Tier‑2 scan gate** and from the Tier‑1 caliper gate except where marked "soft" in §8.

---

## 8. MEASUREMENT REQUEST → `5_reference/MEASUREMENTS.md`

Priority order. "Scan says" = value to expect; record what you actually read, do not copy it.
Photos referenced are in `5_reference/`.

**A. ENVELOPE (do these three first)**

| # | Dimension | Where to put the caliper jaws | Scan says |
|---|---|---|---|
| **M1** | **Overall Ø over bristle tips** *(SOFT — wider band ±3 mm)* | Lay the brush on the table, cup side UP, bristles falling naturally (photo `IMG_20260729_181846.jpg` orientation). Open the **outside** jaws and measure the largest tip-to-tip distance you can find, between the tuft ends of any two arms. Record which two arms. | ~108 mm tip-to-tip (≈124.9 mm swept Ø) |
| **M2** | **Overall Ø over the RIGID plastic arm ends** | Same orientation. Outside jaws on the **white plastic step where the bristles emerge** (the collar visible in `IMG_20260729_182035.jpg`), on two arms. Do not touch the filaments. | ~66 mm across two arms (≈76.4 mm rigid Ø) |
| **M3** | **Overall height, rim face → highest plastic** | Stand the brush on a flat table **cup rim face down** (rim annulus flat on the glass, as in `IMG_20260729_181852.jpg` flipped). Depth rod / height gauge from the table to the highest point of the **white plastic** arm (ignore filaments). | 17.6 mm |

**B. FUNCTIONAL (caliper-coverable) — in importance order**

| # | Dimension | Where to put the caliper jaws | Scan says |
|---|---|---|---|
| **M4** | **Hub skirt OD — MAX** | Cup side up (`IMG_20260729_182142.jpg`). Outside jaws on the round part of the skirt, rotating the caliper to find the **largest** reading. Keep the jaws on the cylindrical skirt band, ~1 mm above the rim — NOT on the dome. | 27.3 mm (lobe R 13.55) |
| **M5** | **Hub skirt OD — MIN** | Same band, rotate to find the **smallest** reading (the flat lands directly on an arm centreline). Report both M4 and M5 — the skirt is 3-lobed. | 25.0 mm (flat R 12.56) |
| **M6** | **HEX socket across-flats (AF)** — *the most important dim on the part* | Cup up. Knife-edge inside jaws down into the hexagonal pocket (`IMG_20260729_182250.jpg`, `IMG_20260729_181852.jpg`), square across **two opposite flats** (not corners). Take 3 readings at 60° apart and give the smallest. | **7.358 mm** |
| **M7** | **HEX pocket depth below the cup floor** | Depth rod of the caliper resting on the **flat cup floor** (the annulus around the hex), rod down to the hex pocket floor. `IMG_20260729_182142.jpg`. | 3.48 mm |
| **M8** | **Cup bore ID** | Inside jaws across the cup's inner cylindrical wall, ~1 mm above the rim face. `IMG_20260729_182203.jpg`. | 20.93 mm |
| **M9** | **Cup depth, rim face → cup floor** | Depth rod from the **rim face** (the flat annular ring the caliper body rests on) down to the cup floor. | 2.57 mm |
| **M10** | **Hub total thickness, rim face → dome apex** | Outside jaws: one jaw flat on the **cup rim annulus**, the other on the **highest point of the dome** near the screw. `IMG_20260729_182318.jpg` shows the dome side. | 10.97 mm |
| **M11** | **Central screw bore Ø** — *needs the screw REMOVED* | Unscrew the centre Phillips screw (`IMG_20260729_181847.jpg`). Inside jaws / pin gauges in the through-hole at the bottom of the hex pocket. Also report the **screw thread Ø and length** and whether the head is pan or countersunk. | 2.70 mm at the mouth |
| **M12** | **Dome-side counterbore Ø** | Inside jaws in the circular recess around the screw head, dome side (`IMG_20260729_182318.jpg`, centre). Measure the plastic bore, not the screw head. | 7.07 mm |
| **M13** | **Arm cross-section at mid-arm** | Pick the point ~25 mm from the hub centre (roughly half way along the white blade). Outside jaws (a) across the **width** and (b) across the **thickness** — two numbers. Same place as `IMG_20260729_182020.jpg` (4.07) / `IMG_20260729_182035.jpg` (5.33) but state where. | width 5.8–6.3, thick 3.8–4.5 (scan runs ~0.5 oversize) |
| **M14** | **Arm cross-section at the tuft collar** | Outside jaws immediately **before** the step where the filaments emerge (the collar in `IMG_20260729_182035.jpg`): width and thickness. | 5.8–6.2 × 3.9–4.1 |

**C. WALL THICKNESSES**

| # | Dimension | Where to put the caliper jaws | Scan says |
|---|---|---|---|
| **M15** | **Skirt wall thickness at the rim** | Outside jaws straddling the skirt wall at the rim: one jaw on the outer skirt, one inside the cup bore, at a **lobe** position (between two arms), then repeat at a **flat** (on an arm centreline). Two numbers. | **3.09 mm at a lobe, 2.10 mm at a flat** |
| **M16** | **Cup floor thickness** *(optional, needs a depth rod on both sides)* | M10 − M9 − (dome-apex-to-hex-floor). If awkward, skip and note it. | ≈4.9 mm floor+dome stack |
| **M17** | **SAF‑1 hole Ø + position** *(answers blocking question Q1)* | The small dark hole in the skirt at one inter-arm position, `IMG_20260729_182109.jpg`. Measure the hole Ø, and say **what it is** (gate mark / tufting-jig hole / key) and whether the other two inter-arm positions really have nothing there. | Ø ≈ 2 mm, nub to R 15.07 |

**Soft dims:** M1 only (bristle tips) — **wider band, ±3 mm, not Tier‑1 blocking.**
All other dims: Tier‑1 band |CAD − caliper| ≤ 0.15 mm.

---

*Plots in this folder:* `B02_A_overview_datum.png` (3 datum-aligned views) · `B02_B_hub_section_annotated.png`
(annotated hub meridian) · `B02_C_threefold_symmetry.png` (self-registration sweep + arm angles) ·
`B02_D_arm_roughness_profiles.png` (plastic/bristle discriminator) · `B02_E_cup_interior_and_skirt.png`
(interior height map + developed skirt) · `B02_F_hub_both_sides.png` · `B02_G_arm_ends_tuft_junction.png` ·
`B02_H_sector_compare_3fold.png` (SAF‑1 evidence) · `B02_I_bore_hex_counterbore_zoom.png` ·
`B02_J_meridian_sections.png`.
