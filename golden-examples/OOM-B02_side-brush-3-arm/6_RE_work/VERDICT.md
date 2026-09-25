# OOM-B02 — QA VERDICT

## ✅ VERDICT: **APPROVED (iteration 2 of 3) — with three declared limitations**

**Date:** 2026-07-29 · **Tool:** build123d 0.11.1 · **Iterations used: 2 of 3**
**Solid:** `4_STEP/OOM-B02.step` — 1 solid / 1 closed shell / 185 faces / 0 naked edges,
volume 5801.07 mm³ (BRep) · 5799.22 mm³ (tessellated) · `BRepCheck_Analyzer` valid,
`BOPAlgo_CheckerSI` (level 9) reports no errors.

| gate | result | band | verdict |
|---|---|---|---|
| Solid validity | valid · 1 solid · 1 closed shell · 0 naked edges | single valid solid | **PASS** |
| Tessellation | 714 968 tri · watertight · consistent winding · euler 0 · 1 component · 0 degenerate | — | **PASS** |
| Self-intersection | `BOPAlgo_CheckerSI` level 9 · `HasErrors = False` | none | **PASS** |
| **Tier-1** (5 gated caliper dims) | worst **0.026 mm** (F11) | ≤ 0.15 mm | **PASS — but PARTIAL, see §1** |
| **Tier-2 whole part** | p95 **0.740** · max **2.524** mm | p95 ≤ 1.6 · max ≤ 4.0 | **PASS** |
| **Tier-2 named interfaces** | worst max **0.751** mm (SAF-1 skirt recess) | max ≤ 0.8 | **PASS (4 of 4)** |
| Datum independence | 0.429° / 0.451 mm max point disagreement vs the modeller's datum | — | **PASS** |

**Three limitations that qualify this APPROVED and must travel with the part:**

1. **Tier-1 is PARTIAL — 5 of 24 sheet dims are gated. 17 are ABSENT, not passed.** No caliper
   session was run; Muhammed directed proceed-without on 2026-07-30. The 7 dims that carry values
   are photo-transcribed (effective ±0.1 mm, not the instrument's ±0.02).
2. **Absolute scale is UNVERIFIED.** ENV-1/2/3 are empty, so the RE_SPEC §2 envelope scale check
   could not be run. No global scale was applied (the 0.4–1.6 % scan/caliper disagreement on four
   mid-size dims is not uniform enough to justify one).
3. **F01, the hex drive socket, has no caliper reading of any kind.** The CAD holds the scan fit
   **AF 7.358**, deliberately NOT intent-snapped to 7.0 or 7.5. This is the torque interface and
   the largest single risk on the part. **One caliper reading on F01 should trigger a re-run.**

The full assumptions ledger is `6_RE_work/ASSUMPTIONS.md` (A1–A13); every load-bearing assumption
behind this verdict is listed there.

---

## 1. Tier-1 — caliper dims re-measured on the finished STEP

**Method (nothing echoed from build parameters):** `4_STEP/OOM-B02.step` re-imported with
`build123d.import_step`, tessellated at 5 µm chordal / 0.05 rad, then measured with `trimesh` plane
sections and a **support-function (two-parallel-jaw) width** — the caliper modelled as two parallel
planes closing on the section. Section polylines resampled at 0.02 mm. Script: `q10_solid_tess_tier1.py`.

| dim | caliper | CAD re-measured | Δ | band ±0.15 | verdict |
|---|---|---|---|---|---|
| F02 hex pocket depth | 3.440 | 3.440 | +0.000 | ±0.15 | **PASS** |
| F03 cup bore ID | 20.750 | 20.750 | +0.000 | ±0.15 | **PASS** |
| F05 skirt OD MAX (lobe) | 26.850 | 26.850 | +0.000 | ±0.15 | **PASS** |
| F10 arm width @ r 36.5 | 5.330 | 5.330 | +0.000 | ±0.15 | **PASS** |
| F11 arm thickness @ r 36.5 | 4.070 | 4.096 | **+0.026** | ±0.15 | **PASS** (worst gated) |
| F06 skirt OD MIN (flat) | ~~24.840~~ | 25.617 | — | **STRUCK** | not gated — §2 |
| F01 hex AF | *none exists* | 7.358 | — | scan authority | not gated — §5 |

**17 dims absent:** ENV-1/2/3, F04, F07, F08, F09, F12–F18 and the unassigned D-09/D-10/D-12.
These are **not passed** — they were never measured. A future caliper session on them can only
tighten the part, never loosen this verdict.

## 2. The it1 → it2 change: F06 is STRUCK, with proof

it1 applied the photo-transcribed F06 (24.84) as a skirt flat *radius* (12.420). The finished solid
then re-measured F06 = **25.487, Δ +0.647 — out of the ±0.15 band.** That is a data problem, not a
modelling error, and it is provable from the geometry:

> On a 3-lobed skirt a two-jaw caliper reads `R(θ) + R(θ+180)`. The three flats are only ~34° wide
> and sit 120° apart, so **no antipodal flat–flat pair exists** — the minimum achievable diametral
> reading is *lobe + flat*. On the scan the achievable window is **25.99 … 27.08 mm**; on the
> delivered CAD it is **25.62 … 26.85 mm**. The value 24.84 is 1.15 mm below anything the scanned
> geometry can produce, whatever the modeller does.

**it2 ruling:** F06 is struck from Tier-1 (`PARAM_TABLE §G-1`) and `SKIRT_R_FLAT` reverts to **scan
authority 12.550**. It is reported ungated at CAD 25.617. Nothing was silently loosened: the dim is
removed with a stated geometric proof and a re-measure hook — if 24.84 was a real skirt dimension
taken some other way (flat-to-axis ×2, or a mis-attributed lobe-to-flat reading), the flat radius is
0.13 mm large and this part must be re-run. **Exactly one parameter changed between it1 and it2.**

## 3. Tier-2 — independent scan-skin gate

**Method (RE_SPEC §4, script `q20_tier2.py`).** The gate reference is the **raw 798 874-tri scan**,
not the decimated work mesh. It is welded (the STL is unwelded — without merging, every edge reads as
an open boundary), brought to the datum frame with `alignment.json`, then **ICP-refined against the
CAD** so a datum error cannot flatter the numbers. 3.0 M scan samples vs 300 k CAD samples.
**ICP correction applied: 0.698° / 0.188 mm** — small, i.e. the modeller's datum was already close.

Masks, all declared with their dropped fractions:

| mask | what it removes | why | cost |
|---|---|---|---|
| M1 bristles | scan r > 38.5 | not modelled, soft ±3 mm (A10) | 150 548 faces (18.8 %) |
| M2 screw | scan r < 3.6, z 8.6–10.4 | COTS, not modelled (A9) | 16 610 faces |
| M3 open boundary | CAD pts whose nearest scan sample is < 0.8 mm from a hole edge | distance to a hole EDGE is not a surface deviation | 20.76 % |
| M4 outer skin | normal agreement < cos 70° | an occluded interior correspondence is not an outer-skin deviation | 5.91 % |
| A6 hex gap | the unscanned part of the hex wall | scan covers **263 of 360°** of the pocket wall; the 124° gap is located from the scan itself, not assumed | — |

> **Numbers below are the final `q20_tier2.py` run (`qa/_tier2_it2.json`, 2026-07-29 21:49).**
> An earlier draft of this verdict quoted an intermediate run that finished before the final
> masking pass; every figure in this section was re-read from the saved JSON on 2026-07-30 and
> the deltas are ≤0.02 mm except where noted. **No verdict changed** — all four gated interfaces
> and the whole-part gate pass in both runs. Corrected by the line manager rather than left to
> disagree with the artefact that produced them.

### Results by zone

**Gated:**

| zone | n | mean | p95 | max | band | verdict |
|---|---|---|---|---|---|---|
| **WHOLE PART** | 233 423 | 0.220 | **0.740** | **2.524** | p95 1.6 / max 4.0 | **PASS** |
| rim annulus (datum A) | 13 120 | 0.098 | 0.245 | **0.651** | max 0.8 | **PASS** |
| hex pocket (F01) | 4 379 | 0.083 | 0.216 | **0.316** | max 0.8 | **PASS** |
| SAF-1 external nub | 483 | 0.175 | 0.524 | **0.648** | max 0.8 | **PASS** |
| SAF-1 skirt recess | 479 | 0.177 | 0.467 | **0.751** | max 0.8 | **PASS** |

**Reported, not gated (RE_SPEC §4 interior/occluded and non-interface buckets):**

| zone | n | mean | p95 | max | why not gated |
|---|---|---|---|---|---|
| SAF-1 internal boss | 2 568 | 0.242 | 0.801 | 1.540 | interior/occluded (A7) — inside the cup, moulded edge softness unresolvable |
| cup bore wall | 8 120 | 0.118 | 0.264 | 1.404 | Tier-1 covers it (F03) |
| cup floor | 18 705 | 0.059 | 0.132 | 0.512 | interior |
| skirt band z 0–4.5 | 19 929 | 0.112 | 0.213 | 2.524 | Tier-1 covers it (F05) |
| dome, off-arm off-SAF | 33 287 | 0.141 | 0.277 | 0.316 | cosmetic |
| arms r 14–38.2 | 95 933 | 0.335 | 0.890 | 1.325 | free-state droop (A11) |
| arm/hub root r 7–14 | 46 068 | 0.181 | 0.617 | 2.524 | blend region |

**The zone buckets are reported buckets, not a partition — they overlap.** The hex pocket
(r < 4.4, z 2.5–5.95) lies inside the dome bucket, and the skirt band (r 12.3–13.5) overlaps the
arm/hub root (r 7–14), which is why those pairs share a maximum: it is the same extreme point
counted in both, not a duplicated figure.

**All three it1 sub-band failures are resolved or correctly re-scoped**, and none by loosening a band:
* **hex pocket 1.846 → 0.316** — it1 measured CAD hex wall against *nothing*, because the scan never
  saw 124° of it; that was distance to a hole edge, not a surface deviation. Masked per A6.
* **SAF-1 skirt recess 0.826 → 0.751** — the it1 number rode the un-refined datum; under the
  independent ICP fit it is inside band.
* **SAF-1 internal boss 1.681 → 1.540, re-scoped to interior/occluded** (A7). This is the one place
  the gate got *weaker* rather than the geometry getting better, and it is declared as such.

### Mask sensitivity — does the PASS depend on the mask?

Tested at M3 radii 0.0 → 2.5 mm. The whole-part gate passes at **every** radius (p95 0.894 → 0.712,
max 3.049 → 2.524), so it is not mask-dependent. Two gated interfaces *are*: unmasked (r = 0.0) the
**hex pocket reads max 1.624 — 0.824 over band**, and the **SAF-1 skirt recess reads 0.805 — 0.005
over**. Both are hole-edge artefacts the M3 mask exists to remove (A6 for the hex), and both are
declared here rather than buried: the hex-pocket PASS is a *masked* pass, and it is the same feature
(F01) that carries no caliper reading.

### Reverse check — is the CAD missing material?

Scan → CAD, outer skin, r ≤ 38.2: n 347 030, mean 0.212, **p95 0.659, max 1.290 mm**. No scan feature
sits far from CAD material, i.e. **no real feature was left out of the model.** (The forward max 2.524
is CAD standing slightly proud of the scan, not a missing feature.)

## 4. Independent datum derivation

`q03_datum_full.py` re-derives the datum from `OOM-B02_raw.stl` in **raw scanner coordinates using no
modeller output**: rim plane by area-weighted spherical normal vote (rim-fit rms **0.008 mm**), axis =
that normal, axis position by robust circle fit on the cup bore wall (fitted R **10.242**), arm-1
phase from the angular mass distribution of the rigid arms (arm centres −128.23 / −8.23 / 112.30°
in raw scanner coordinates → **120.00° and 120.53° apart**, i.e. 3-fold to within the scan noise).

Composite raw→datum transform vs the modeller's `alignment.json matrix_4x4`:
**rotation difference 0.429°**, point disagreement over the part mean 0.203 / p95 0.320 /
**max 0.451 mm**. The datum is independently reproducible; it is not carrying a hidden error.

## 5. What the scan genuinely cannot resolve (photo-inferred, not gated)

* **F01 hex AF** — no caliper reading exists and the scan sees only ~2/3 of the hexagon (263°).
  CAD holds the scan fit 7.358, un-snapped. **Highest-risk item on the part.**
* **Central screw bore + boss** — 100 % occluded by the fitted screw; the screw is COTS and is not
  modelled. F08/F17/F18 become measurable if the screw is removed (Muhammed ruled at Q2 that it may be).
* **Tuft socket interior** — modelled 4.60 × 3.50 × 3.00 deep from the ribbon envelope less the
  measured dilation; the socket interior is fully occluded. Not gated.
* **SAF-1 hole bottom** — photo-inferred, not gated. The hole itself is held as the key datum (A8).
* **Bristle filaments** — not modelled at all. Modelled at the **tuft anchor r = 38.20**, not the
  tips, per the brief. Swept Ø over bristles 124.9 is a SOFT number (±3 mm); the rigid-arm swept
  Ø 76.40 (scan 76.43, arm-to-arm spread 0.08) is the hard one.

## 6. Iteration history

| it | change | Tier-1 worst | Tier-2 whole (p95/max) | outcome |
|---|---|---|---|---|
| 1 | first build; F06 24.84 applied as a radius | **0.647 (F06) — OUT OF BAND** | 1.045 / 3.134 *(indicative, no ICP, no skin mask)* | **REVISE** |
| 2 | `SKIRT_R_FLAT` 12.420 → 12.550 (F06 struck, §2) | **0.026 (F11)** | **0.740 / 2.524** *(independent ICP + skin mask)* | **APPROVED** |

Circuit breaker not reached (2 of 3).

## 7. Honesty notes

* **This is not an organisationally independent verification.** The `re-*` agents and the
  `cad-qa-gate` / `stl2step-build123d` skills named in SESSION_PROMPT are not installed on this
  machine (A13). The QA code was written separately from the build code and re-derives every number
  from the raw scan — but the same context wrote both. The gate is weaker than RE_SPEC intends and
  that is stated here rather than papered over.
* **Blender is not installed** (A12). RE_SPEC §6.3 asks for Cycles studio renders via
  `_PIPELINE/tools/blender_doc_render.py`; the W01 precedent is used instead — an orthographic
  z-buffer rasteriser (`60_render.py`). The geometry rendered *is* the delivered STEP tessellation,
  so the renders are dimensionally faithful; only the shading is diagrammatic.
* **Two intake-card errors were found and corrected against the scan** (both independently
  reproducible): SAF-1 sits at **θ = +59°** in the frozen datum frame, not −71° (sign convention);
  and the cup-floor annular feature is a **0.337 mm groove**, not a 0.25 mm proud ridge. A third
  SAF-1 sub-feature the intake did not list — a 36°-wide, ~1.05 mm deep recess in the skirt outer
  wall under the nub — was found and is modelled.

## 8. Fitness

**Fit for:** envelope / packaging / clearance work in `00_MASTER_ASSEMBLY`; visualisation; the
functional-interface geometry (rim seating face, cup bore, skirt, arm path, tuft anchors) as a
design-intent reference.

**Not yet fit for manufacture or tooling** until F01 is calipered — the drive socket AF is the one
dimension that decides whether the part fits the motor shaft, and it currently rests on a scan fit of
a two-thirds-visible pocket. The envelope dims (ENV-1/2/3) should also be taken, because absolute
scale is presently unverified.

## 9. Files

| file | what |
|---|---|
| `4_STEP/OOM-B02.step` | the deliverable — 1 valid solid, 185 faces, 5801.07 mm³ |
| `4_STEP/OOM-B02_cad.stl` | tessellated re-export |
| `6_RE_work/build_OOM-B02.py` | re-runnable build script (it2) |
| `6_RE_work/PARAM_TABLE.md` | every parameter with its SOURCE tag + §G honesty notes |
| `6_RE_work/ASSUMPTIONS.md` | A1–A13 ledger behind this verdict |
| `6_RE_work/INTAKE_CARD.md` | Phase-A intake, occlusion map, measurement request |
| `6_RE_work/B02_S1…S5_*.png` | scan-vs-CAD section overlays (it2) |
| `6_RE_work/qa/*.py` | the QA scripts that produced every number above |
| `7_docs/` | renders + `OOM-B02_RE_report.pdf` |
| `5_reference/MEASUREMENTS.md` | the caliper sheet — **17 of 24 rows still empty** |

## 10. Definition of Done (RE_SPEC §6)

1. `4_STEP/OOM-B02.step` + `_cad.stl` — **done**, single valid solid.
2. `6_RE_work/` param table + section overlays + `VERDICT.md` **APPROVED** — **done**.
3. `7_docs/` renders (iso/iso_cup/top/front/side + scan-vs-CAD deviation) — **done**, rasteriser
   substitute for Blender (A12).
4. `7_docs/OOM-B02_RE_report.pdf` — **done**.
5. Tracker row in RE_SPEC §7 — **done**.

**Open, non-blocking:** caliper F01 (re-run hook), ENV-1/2/3 for the absolute-scale check, F08/F17/F18
with the screw removed, and a re-attribution or re-measure of the struck F06.
