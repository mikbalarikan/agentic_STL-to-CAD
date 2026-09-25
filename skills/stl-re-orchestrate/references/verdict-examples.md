# Worked verdicts: the six golden outcomes

The six golden parts, re-read through this skill set's verdict vocabulary
(`run-contract.md` §7). Each entry gives what the record says, the numbers with their
source, the regime, the verdict this contract would give, which checks fire, and what the
orchestrator does next. Summary table: `analysis/SYNTHESIS.md` §0.1.

Only one of the six parts (DRM screw) passes a scan-deviation band with no masks and no
caveats. Most runs end in a qualified state. Say so; do not round it up to "PASS".

Paths: `GE/` = `golden-examples/`.

---

## 1. DRM screw cap: the one unmasked clean pass

- **Record:** official gate `overall_pass: true`, `exclusions: []`
  (`GE/dreame_brush-caps/report/screw_official_gate.json`).
- **Regime:** `baseline-skill`, consumer plastic, p95 ≤ 0.30 / max ≤ 0.80
  (`#limits`; `baseline/skills/stl2step-build123d/SKILL.md:87`).
- **Numbers (full-res scan, 50k samples):** scan→CAD rms 0.0426, p95 0.0851, max 0.2448;
  CAD→scan p95 0.0757, max 0.2683 (`screw_official_gate.json#scan_to_cad`, `#cad_to_scan`).
- **Caveat in the record:** no calipers, so every dimension is scan authority
  (`GE/dreame_brush-caps/README.md:81`).
- **Verdict here:** the gates pass with no masks. Under §6 of the orchestrator SKILL, a
  scan-only run carries "Tier-1 not run" and "absolute scale not caliper-verified" as
  declared limitations. That gives **`APPROVED_WITH_LIMITATIONS`**.
  `analysis/SKILL_ARCHITECTURE.md` §4 lists this part as the `APPROVED` precedent. That
  holds only if the scan-only authority is treated as a claim boundary, not a limitation
  (open question; see the end).
- **Next:** deliver.

## 2. DRM snap cap: official gate FAILED on max

- **Record:** official gate **`overall_pass: false`**, `exclusions: []`. Scan→CAD rms 0.0851,
  p95 0.1570 (in band), **max 1.2260 > 0.80**. CAD→scan p95 0.0871, max 0.2729
  (`GE/dreame_brush-caps/report/snap_official_gate.json`).
- **The README** reports "p95 PASS, **max FAIL**" and attributes the max to scan artefacts
  (`GE/dreame_brush-caps/README.md:64`).
- **The golden index** says "Delivered: … snap p95 0.157" and does not mention the max fail
  (`GE/README.md:14`).
- **Masks:** six named artefact masks remove 4.9 % of the points. The masked max is still
  1.246 (`GE/dreame_brush-caps/report/snap_masked_gate.json`). The masks do not clear the
  band.
- **Verdict here:** **`BAND_NOT_MET`** (max, whole part, regime `baseline-skill`).
  - CHK-MASK result `finding`: the masked and unmasked numbers are shown side by side, and
    both miss.
  - The per-region explanation (a floating scan flap, 315 of 570k points > 0.8) belongs in
    `VERDICT.md` as the cause. It does not change the verdict.
- **Next:** show the user the miss and the options. Deliver only after an `ACCEPT-BAND`
  entry in `DECISIONS.md`. The record has **no recorded acceptance** (`QUESTIONS.md` B,
  "DRM snap outcome"). Under this contract, the part could not have been delivered as it
  was.

## 3. OD-H12 pump: band missed, explained per region

- **Record:** "operator: good result" (`GE/README.md:11`). The README's own verdict is
  "NOT MET" for p95 ≤ 0.30 / max ≤ 0.80 (`GE/OD-H12_delonghi-dedica-pump/README.md:32-33`).
- **Regime:** `baseline-skill`, consumer plastic.
- **Numbers (full-res, n 493,060):** scan→CAD rms 0.217, **p95 0.448, max 2.49**
  (`GE/OD-H12_delonghi-dedica-pump/report/deviation_gate.json#scan_to_cad`).
  - Per region, scan→CAD p95: outlet 0.39, front body/flange 0.49, coil+frame 0.45,
    inlet 0.27 (`README.md:29`).
  - CAD→scan, observable surfaces only: p95 0.567 (`README.md:26`). The ray test classifies 25.6 % of the
    CAD surface as unobservable (`README.md:41`; `deviation_gate.json#cad_to_scan_unobservable_fraction`).
- **Circularity:** the 13/13 validator got its expected values from the same scan. The
  record itself calls it "not independent" (`README.md:70-71`). → CHK-CIRCULAR `finding`.
  It is a consistency check only.
- **Verdict here:** **`BAND_NOT_MET`**, per region, with the cause for each region and
  options.
  - The record's options are a conical coil, lettering, and terminal blades. They were
    withheld because guessing without calipers or photos is risky (`README.md:43-44`).
  - The scan→CAD numbers would sit inside the RE_SPEC Tier-2 band. Switching the regime
    after the fact is not allowed (orchestrator SKILL §3.3).
- **Next:** the operator's "good result" is the human acceptance. In this contract it
  must be written to `DECISIONS.md` as `ACCEPT-BAND` (who, date, band, p95 0.448 /
  max 2.49) before `deliver/` is written.

## 4. OOM-B02 side brush

### it1: `REVISE`

- **Tier-1 F06:** skirt OD min. CAD 25.487 vs caliper 24.84, **Δ +0.647**, outside ±0.15
  (`RE_SPEC.md:170`) (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md` §2, §6).
- **Cause:** the caliper reading was not achievable as a two-jaw diametral reading on a
  3-lobed skirt. The achievable window is 25.99…27.08 → CHK-ACHIEVABLE → route to
  **measure**.
- **Process fault:** it1 was published before the gate finished
  (`baseline/oomwoo-re-pipeline/TRACKER.md:13`) → CHK-PUBLISH `fail`. Withdraw it to
  `_it1_SUPERSEDED/`.
- **Fix:** exactly one parameter changed, `SKIRT_R_FLAT` 12.420 → 12.550
  (`GE/OOM-B02_side-brush-3-arm/6_RE_work/_it1_SUPERSEDED/build_OOM-B02_it1.py` vs
  `build_OOM-B02.py`).

### it2: recorded APPROVED; here `APPROVED_WITH_LIMITATIONS`

- **Record:** "APPROVED (iteration 2 of 3) — with three declared limitations"
  (`VERDICT.md:3`).
- **Regime:** `RE_SPEC`.
- **Numbers:**
  - Tier-1 worst 0.026 (F11), but only 5 of 24 dims gated.
  - Tier-2 whole part p95 0.740 / max 2.524.
  - Named interfaces 4/4, worst 0.751 (`VERDICT.md:15-17`).
- **Limitations, each with a trigger** (`VERDICT.md:20-30`):
  1. Tier-1 is partial: 17 dims absent, not passed.
  2. Absolute scale is unverified.
  3. F01 hex AF has no caliper and is held at the scan fit 7.358, not snapped. "One
     caliper reading on F01 should trigger a re-run."
- **Checks:**
  - **CHK-MASK `finding`:** the hex-pocket pass is a **masked** pass. Unmasked it reads
    1.624 (0.824 over); the recess reads 0.805 unmasked (`VERDICT.md` §3, "Mask
    sensitivity").
  - **CHK-INDEP `finding`:** "not an organisationally independent verification"
    (`VERDICT.md` §7).
  - **CHK-LIKE4LIKE `finding`:** the it1 → it2 Tier-2 "fixes" came from the protocol
    (ICP, masks) and from re-scoping, not from geometry (`VERDICT.md` §6).
  - **CHK-NUMBERS:** the first draft quoted an intermediate run (`VERDICT.md:94-99`).
  - **Datum audit:** 0.429° / 0.451 mm, above the RE_SPEC reference ≤ 0.3° / ≤ 0.15 mm.
    It is report-only (`QUESTIONS.md` A/Q2).
- **Next:** deliver, with the limitations and the fitness boundary: "not yet fit for
  manufacture or tooling until F01 is calipered" (`VERDICT.md` §8).

## 5. OOM-P03 mop-pad bracket

### it1: `REVISE`

- **Finding:** the central drive stem was missing. 4907 outer-skin points were > 4.0 mm
  at r < 6.4, z ≈ 18, which breaks the Tier-2 max ≤ 4.0 (`RE_SPEC.md:174`)
  (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:8,41`).
- **Cause:** the modeller "wrongly dismissed [the spike] as occlusion" (`PARAM_TABLE.md:4`).
  The intake never listed a stem.
- **Checks:** CHK-ENUM and CHK-CLUSTER → route to **intake** (feature enumeration), then
  measure and rebuild. `alignment.json` was also 1.651 mm off the QA best fit
  (`VERDICT.md:50`).
- **Record gap:** the it1 verdict was overwritten ("it2, overwritten in place",
  `VERDICT.md:6`) → CHK-SUPERSEDED `fail`. Use `init_run.py supersede`.

### it2: recorded APPROVED; here `APPROVED_WITH_LIMITATIONS`

- **Regime:** `RE_SPEC`.
- **Numbers:**
  - Tier-1 worst 0.000 over 7 photo-transcribed dims.
  - Outer skin p95 0.971 / max 2.949.
  - 0 skin points > 4 mm (`VERDICT.md:16-41`).
- **Declared (non-blocking notes):**
  - The square socket is photo-inferred.
  - 8 dims fall back to scan authority (`baseline/oomwoo-re-pipeline/TRACKER.md:31`).
- **Checks:**
  - **CHK-CIRCULAR `finding`:** `alignment.json` was ICP-refined to the part's own CAD
    "to match verifier ICP frame"
    (`GE/OOM-P03_mop-pad-bracket/2_mesh_cleaned/alignment.json#refinement`).
  - **Stem zone:** max 2.424 > 0.8, but the stem was not a named interface, so the band
    was never applied (`VERDICT.md:42`). In this contract the stem must become a named
    zone once it has been found.
  - **Two-way deviation** was not run (`analysis/golden/OOM-P03.md` §7).

## 6. M02-02-03 gear: spec conformance, no scan gate

- **Record:** QA PASS, 22/22 checks, `fail_closed`, hash frozen before and after
  (`GE/M02-02-03_watertight-design-intent/qa_report.json`).
- **Regime:** `project-spec` (`OPERATOR_SPEC.json`, operator-measured counts and
  diameters).
- **Numbers:** OD 19.05 and 11.2, tooth counts 30 / 17 at 3 stations each
  (`qa_report.json#checks`).
- **No scan comparison:** there is no scan datum and no scan deviation gate, and the
  source scan is not in the repo (`analysis/golden/M02-02-03.md` §7, Questions).
- **Earlier failure:** a scan-derived 27T / Ø21.75 candidate was wrong
  (`DESIGN_NOTES.md:5`) → CHK-COUNT.
- **Verdict here:** **`APPROVED`** under the `project-spec` regime, with the record's
  claim boundary: PASS covers "the listed … gates only" (`VERDICT.md:30`), and "physical
  interchangeability … require[s] … physical fit verification" (`README.md:31`).
- **Wording:** the verdict must not imply a scan fit.
- **Next:** deliver with that claim boundary.

---

## Open questions carried from these examples

- **DRM screw: `APPROVED` or `APPROVED_WITH_LIMITATIONS`?** `SKILL_ARCHITECTURE.md` §4
  lists it as `APPROVED`. The scan-only rule in the orchestrator SKILL §6 makes it
  `APPROVED_WITH_LIMITATIONS`. The owner has not ruled on whether scan-only authority is a
  limitation or a claim boundary.
- **DRM snap: who accepted the max miss?** The acceptance is not recorded, and the gate's
  `exclusions: []` conflicts with the README's "table excluded" (`QUESTIONS.md` B).
