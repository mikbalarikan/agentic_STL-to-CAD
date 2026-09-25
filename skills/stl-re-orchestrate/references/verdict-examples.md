# Worked verdicts: the six golden outcomes

The six golden parts, re-read through this skill set's verdict vocabulary
(`run-contract.md` §7). Each entry gives the *kind* of outcome the record shows, which checks
fire and why, and what the orchestrator does next — it deliberately does not restate the
part's own measured numbers or its final pass/fail result, since a blind run of this skill
should not be able to read its own answer key here. If you need the actual figures or the
final verdict for a specific part, read the cited record or `analysis/golden/<part>.md`
yourself; do not infer them from this file. Summary table: `analysis/SYNTHESIS.md` §0.1.

Most runs in the golden set end in a qualified state, not a flat pass. Do not assume a part
you have not yet evaluated will land cleanly; work the checks below on your own measurements.

Paths: `GE/` = `golden-examples/`.

---

## 1. DRM screw cap: a scan-only baseline-skill run

- **Record:** an official scan-deviation gate result is on file
  (`GE/dreame_brush-caps/report/screw_official_gate.json`) — read it for the actual pass/fail
  and numbers.
- **Regime:** `baseline-skill`, consumer plastic, p95 ≤ 0.30 / max ≤ 0.80
  (`#limits`; `baseline/skills/stl2step-build123d/SKILL.md:87`).
- **Caveat in the record:** no calipers, so every dimension is scan authority
  (`GE/dreame_brush-caps/README.md:81`).
- **Lesson:** under §6 of the orchestrator SKILL, a scan-only run — even one whose scan gate
  passes cleanly with no masks — still carries "Tier-1 not run" and "absolute scale not
  caliper-verified" as declared limitations. A clean scan gate on a scan-only part is
  **`APPROVED_WITH_LIMITATIONS`**, never a flat `APPROVED`: the limitations come from the lack
  of caliper verification, not from the gate result. `SKILL_ARCHITECTURE.md` §4 draws exactly
  this contrast against a project-spec part that has no scan gate at all
  (`analysis/SKILL_ARCHITECTURE.md:269`).
- **Next:** if the gate passes with no masks and no caveats beyond the scan-only ones, deliver
  with those limitations stated.

## 2. DRM snap cap: a masked band miss, with no recorded acceptance

- **Record:** an official scan-deviation gate result and README are on file
  (`GE/dreame_brush-caps/report/snap_official_gate.json`, `GE/dreame_brush-caps/README.md`) —
  read them for the actual numbers; the max band was missed while p95 was in band.
- **The golden index** summarises only the in-band number and omits the max miss
  (`GE/README.md:14`) — a lesson in itself: don't let a summary elsewhere in the record stand
  in for the actual gate result.
- **Masks:** several named artefact masks remove a small fraction of the points. The masked
  max is still over the band (`GE/dreame_brush-caps/report/snap_masked_gate.json`). The masks
  do not clear the band.
- **Verdict here:** **`BAND_NOT_MET`** (max, whole part, regime `baseline-skill`).
  - CHK-MASK result `finding`: the masked and unmasked numbers are shown side by side, and
    both miss.
  - A per-region explanation (a floating scan flap affecting a small fraction of points)
    belongs in `VERDICT.md` as the cause. It does not change the verdict.
- **Next:** show the user the miss and the options. Deliver only after an `ACCEPT-BAND`
  entry in `DECISIONS.md`. The record has **no recorded acceptance** (`QUESTIONS.md` B,
  "DRM snap outcome"). Under this contract, the part could not have been delivered as it
  was.

## 3. OD-H12 pump: band missed, explained per region

- **Record:** an operator note calling it a "good result" (`GE/README.md:11`) sits alongside
  the README's own stated verdict of "NOT MET" against the `baseline-skill` band
  (`GE/OD-H12_delonghi-dedica-pump/README.md:32-33`, `report/deviation_gate.json`) — read the
  cited files for the actual figures.
- **Regime:** `baseline-skill`, consumer plastic.
- **Lesson — per-region breakdown:** the whole-part number misses the band, but the record
  breaks it down per region, and a ray test flags a large fraction of the CAD surface as
  unobservable from the scan (`README.md:29,41`; `deviation_gate.json#cad_to_scan_unobservable_fraction`).
  A single whole-part number without that breakdown would hide which surfaces are actually
  driving the miss.
- **Circularity:** a validator used elsewhere in the record got its expected values from the
  same scan it is checking. The record itself calls this "not independent"
  (`README.md:70-71`) → CHK-CIRCULAR `finding`. It is a consistency check only, never treated
  as an independent pass.
- **Verdict here:** **`BAND_NOT_MET`**, per region, with the cause for each region and
  options.
  - The record's proposed design options were withheld because guessing without calipers or
    photos is risky (`README.md:43-44`).
  - A different (tighter) regime's band would have been met by the same numbers. Switching
    the regime after the fact to make that happen is not allowed (orchestrator SKILL §3.3).
- **Next:** an operator's informal "good result" comment is not a recorded acceptance. In this
  contract, delivering a band-missed part requires an explicit `ACCEPT-BAND` entry in
  `DECISIONS.md` (who, date, band, the actual p95/max) before `deliver/` is written.

## 4. OOM-B02 side brush

### it1: `REVISE`

- **Tier-1 finding:** a Tier-1 skirt dimension came back out of the ±0.15 mm band
  (`RE_SPEC.md:170`) (`GE/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md` §2, §6) — see the
  cited record for the actual reading and margin.
- **Cause:** the caliper reading was not achievable as a two-jaw diametral reading on a
  3-lobed skirt (a two-jaw caliper reads a support width, not a radius, on a non-round
  cross-section) → CHK-ACHIEVABLE → route to **measure**. See `analysis/golden/OOM-B02.md`
  §8 for the achievable window and the reading that missed it.
- **Process fault:** it1 was published before the gate finished
  (`baseline/oomwoo-re-pipeline/TRACKER.md:13`) → CHK-PUBLISH `fail`. Withdraw it to
  `_it1_SUPERSEDED/`.
- **Fix:** exactly one parameter changed between it1 and it2 — the flagged reading was struck
  and its parameter reverted to the scan fit
  (`GE/OOM-B02_side-brush-3-arm/6_RE_work/_it1_SUPERSEDED/build_OOM-B02_it1.py` vs
  `build_OOM-B02.py`; see `analysis/golden/OOM-B02.md` §8 for which parameter and its value).

### it2: recorded APPROVED; here `APPROVED_WITH_LIMITATIONS`

- **Record:** "APPROVED (iteration 2 of 3) — with three declared limitations"
  (`VERDICT.md:3`). Read `VERDICT.md:15-17` for the actual Tier-1/Tier-2/interface numbers;
  they are not restated here.
- **Regime:** `RE_SPEC`.
- **Limitations, each with a trigger** (`VERDICT.md:20-30`):
  1. Tier-1 is partial: most dims are absent, not passed — an absent dim is not the same as a
     passed one, and the limitation must say so explicitly.
  2. Absolute scale is unverified.
  3. A critical hex-across-flats feature has no caliper and is held at its scan fit rather
     than snapped to a nearby standard size, with a rerun trigger for the first real caliper
     reading on it.
- **Checks:**
  - **CHK-MASK `finding`:** the hex-pocket pass is a **masked** pass; the unmasked reading
    misses the band (`VERDICT.md` §3, "Mask sensitivity") — a masked pass and an unmasked
    pass are different claims, and only the honest one should be reported as the verdict.
  - **CHK-INDEP `finding`:** "not an organisationally independent verification"
    (`VERDICT.md` §7).
  - **CHK-LIKE4LIKE `finding`:** the it1 → it2 Tier-2 improvement came from protocol changes
    (ICP, masks) and re-scoping, not from a geometry fix (`VERDICT.md` §6) — an improved
    number is not evidence of a better model unless you can rule this out.
  - **CHK-NUMBERS:** the first draft quoted an intermediate run rather than the final one
    (`VERDICT.md:94-99`) — always re-render the table from the final `params.json`/gate JSON,
    never carry a number forward by hand.
  - **Datum audit:** report-only, above the RE_SPEC reference of ≤ 0.3° / ≤ 0.15 mm
    (`QUESTIONS.md` A/Q2) — see `analysis/golden/OOM-B02.md` for the actual figures.
- **Next:** deliver, with the limitations and the fitness boundary: "not yet fit for
  manufacture or tooling until [the critical feature] is calipered" (`VERDICT.md` §8).

## 5. OOM-P03 mop-pad bracket

### it1: `REVISE`

- **Finding:** the central drive stem was missing, and a coherent cluster of outer-skin
  points sat well beyond the Tier-2 max band in that zone (`RE_SPEC.md:174`)
  (`GE/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:8,41`) — see the cited record for the
  actual point count and location.
- **Cause:** the modeller "wrongly dismissed [the spike] as occlusion" (`PARAM_TABLE.md:4`).
  The intake never listed a stem.
- **Checks:** CHK-ENUM and CHK-CLUSTER → route to **intake** (feature enumeration), then
  measure and rebuild. `alignment.json` was also measurably off the QA best fit
  (`VERDICT.md:50`).
- **Record gap:** the it1 verdict was overwritten ("it2, overwritten in place",
  `VERDICT.md:6`) → CHK-SUPERSEDED `fail`. Use `init_run.py supersede`.

### it2: recorded APPROVED; here `APPROVED_WITH_LIMITATIONS`

- **Regime:** `RE_SPEC`. Read `VERDICT.md:16-41` for the actual Tier-1/Tier-2 numbers; they
  are not restated here.
- **Declared (non-blocking notes):**
  - The square socket is photo-inferred.
  - Several dims fall back to scan authority (`baseline/oomwoo-re-pipeline/TRACKER.md:31`).
- **Checks:**
  - **CHK-CIRCULAR `finding`:** `alignment.json` was ICP-refined to the part's own CAD
    "to match verifier ICP frame"
    (`GE/OOM-P03_mop-pad-bracket/2_mesh_cleaned/alignment.json#refinement`).
  - **Stem zone:** its deviation exceeded the interface band, but the stem was not a named
    interface, so the band was never applied (`VERDICT.md:42`). In this contract the stem
    must become a named zone once it has been found.
  - **Two-way deviation** was not run (`analysis/golden/OOM-P03.md` §7).

## 6. M02-02-03 gear: spec conformance, no scan gate

- **Record:** a full spec-conformance QA pass with every check fired and hash frozen before
  and after (`GE/M02-02-03_watertight-design-intent/qa_report.json`).
- **Regime:** `project-spec` (`OPERATOR_SPEC.json`, operator-measured counts and
  diameters — the operator spec is authoritative input here, not something to re-derive).
- **No scan comparison:** there is no scan datum and no scan deviation gate, and the
  source scan is not in the repo (`analysis/golden/M02-02-03.md` §7, Questions).
- **Earlier failure:** a scan-derived tooth-count/diameter candidate was wrong before the
  operator spec corrected it (`DESIGN_NOTES.md:5`) → CHK-COUNT. Lesson: an operator spec, when
  it exists, overrides a scan-derived candidate for the dimensions it covers.
- **Verdict here:** **`APPROVED`** under the `project-spec` regime, with the record's
  claim boundary: PASS covers "the listed … gates only" (`VERDICT.md:30`), and "physical
  interchangeability … require[s] … physical fit verification" (`README.md:31`).
- **Wording:** the verdict must not imply a scan fit.
- **Next:** deliver with that claim boundary.

---

## Open questions carried from these examples

- **DRM snap: who accepted the max miss?** The acceptance is not recorded, and the gate's
  `exclusions: []` conflicts with the README's "table excluded" (`QUESTIONS.md` B).
