# Limitations, claim boundary and band-miss wording

How the golden deliveries worded what they could NOT claim. Quote the pattern, not the
numbers: in `deliver/limitations.json` every number goes in as a placeholder
(`{{gate:...}}`, `{{params:...}}`), never typed (CHK-NUMBERS). Numbers in the quotes
below belong to those projects and are shown only as evidence.

## 1. The shape of a good limitation

Each limitation says four things (SYNTHESIS F1, F7, F10):

1. **What is missing or weak**, in plain words, with its status word: ABSENT, UNVERIFIED,
   ASSUMED, PHOTO-INFERRED, MASKED PASS, NOT MET.
2. **Why** (no caliper, occluded, soft, scanner artefact, not uniform enough to scale).
3. **What the model holds instead** (scan fit, un-snapped; mean path; assumed value).
4. **The re-run trigger**: the one measurement or event that would change the model.

Absent is not passed. A masked pass is not a clean pass. A consistency check against
values taken from the same scan is not independent evidence.

## 2. Good examples (verbatim or close, with source)

### OOM-B02 — three limitations that "must travel with the part"

`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:20-30`

> 1. **Tier-1 is PARTIAL — 5 of 24 sheet dims are gated. 17 are ABSENT, not passed.** No
>    caliper session was run; … The 7 dims that carry values are photo-transcribed
>    (effective ±0.1 mm, not the instrument's ±0.02).
> 2. **Absolute scale is UNVERIFIED.** ENV-1/2/3 are empty, so the RE_SPEC §2 envelope scale
>    check could not be run. No global scale was applied (the 0.4–1.6 % scan/caliper
>    disagreement on four mid-size dims is not uniform enough to justify one).
> 3. **F01, the hex drive socket, has no caliper reading of any kind.** The CAD holds the scan
>    fit **AF 7.358**, deliberately NOT intent-snapped to 7.0 or 7.5. This is the torque
>    interface and the largest single risk on the part. **One caliper reading on F01 should
>    trigger a re-run.**

Masked pass, declared (`VERDICT.md:138-145`):

> Two gated interfaces *are* [mask-dependent]: unmasked … the **hex pocket reads max 1.624 —
> 0.824 over band** … the hex-pocket PASS is a *masked* pass, and it is the same feature (F01)
> that carries no caliper reading.

Fitness / claim boundary (`VERDICT.md:204-213`, repeated in `70_report.py:340-347`):

> **Fit for:** envelope / packaging / clearance work …; visualisation; the functional-interface
> geometry … as a design-intent reference.
> **Not yet fit for manufacture or tooling** until F01 is calipered — the drive socket AF is
> the one dimension that decides whether the part fits the motor shaft …

Independence declared (`VERDICT.md:189-194`):

> **This is not an organisationally independent verification.** … The QA code was written
> separately from the build code and re-derives every number from the raw scan — but the same
> context wrote both.

### OD-H12 — band NOT MET, reported per region with options (translated from Turkish)

`golden-examples/OD-H12_delonghi-dedica-pump/README.md:32-44`

> **Verdict (honest):** the skill's consumer-plastic band p95 ≤ 0.30 / max ≤ 0.80 mm →
> **NOT MET** (p95 0.448, max 2.49). Why, and how the remaining gap is distributed:
> - Even on a clean cylinder the scan carries p95 0.13 mm noise; the coil surface is ±0.1 mm
>   slightly conical/wavy, and one cylinder was fitted.
> - Only 0.16 % of points exceed 1.2 mm; the clusters are [named regions] … all
>   cosmetic/internal — deliberately not modelled.
> - Raw CAD→scan includes surfaces the scanner physically cannot see … 25.6 % of the CAD
>   surface is "unobservable" by ray test; the observable part is p95 0.567.
>
> If a tighter band is needed, the next steps are: [three geometric options] — but without
> caliper/photo confirmation, guessing them is risky.

Assumptions flagged for operator approval (`README.md:62-71`, heading "Varsayımlar ve sınırlar
(operatör onayı gerekli)" = "assumptions and limits (operator approval required)"):

> **Scale:** the STL is unitless; mm assumed … Not verified by caliper.
> **Unobservable interior geometry:** sheet thickness, core tube Ø16, pocket depth, hole
> depths — the scan does not prove these; design-intent estimates.
> Validator 13/13 PASS — but the expected values also came from the scan; this is not an
> independent verification, it is a topology + dimension consistency check. The independent
> evidence is the deviation gate.

### OOM-P03 — photo-inferred feature with a physical-confirmation flag

`golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:55`

> Square drive socket (5.5×2.5) is photo-inferred; scanner bridged it, so its scan deviation
> (stem-zone max 2.424) is expected and correct, not a defect. … flag for physical
> confirmation if the coupling interface is ever manufactured to fit.

Caveat: the stem zone was never a named intake zone, so the ≤0.8 interface band was never
applied to it (`analysis/golden/OOM-P03.md` §9). Name the band status explicitly.

### M02-02-03 — claim boundary and "nothing invented"

`golden-examples/M02-02-03_watertight-design-intent/README.md:21-31`

> No unmeasured hub projection, relief, chamfer, backlash, profile shift or root fillet was
> invented.
> **Claim boundary:** Digital design-intent model constrained by operator measurements.
> Physical interchangeability and manufacturing release require mating-part or physical fit
> verification.

`VERDICT.md:30`: "PASS establishes the listed local exported-artifact geometry, topology,
mesh, dimensions, periodic counts, zero-twist, and visual-evidence gates only."

### dreame_brush-caps — declared simplifications

`golden-examples/dreame_brush-caps/README.md:80-86`: legs modelled identical though one
measures ~0.1 mm further out; cups on a common PCD though one measured r 9.02; ramp a single
plane over ±0.07 mm undulation. Each names what was measured and what was modelled.

## 3. Anti-patterns (do not repeat)

| Anti-pattern | Where | Why it is wrong | Rule |
|---|---|---|---|
| Index row omits a failed gate | `golden-examples/README.md:14` says "Delivered: … snap p95 0.157"; the official gate is `overall_pass: false`, max 1.226 > 0.80 (`golden-examples/dreame_brush-caps/report/snap_official_gate.json`; `README.md:64` "max FAIL") | A reader of the index sees a pass. No acceptance of the max miss is recorded anywhere (`analysis/golden/dreame_brush-caps.md` Questions 1) | The README headline carries the verdict word from `gate.json`; BAND_NOT_MET needs an ACCEPT-BAND record |
| Report quotes an intermediate run | B02 verdict draft, corrected later: "An earlier draft of this verdict quoted an intermediate run …" (`OOM-B02/6_RE_work/VERDICT.md:95-99`) | Numbers drifted up to 0.02 mm from the artefact | CHK-NUMBERS: render from JSON; placeholders in prose |
| Published before the gate | "Iteration 1 was published to 4_STEP before the gate finished" (`OOM-B02/6_RE_work/70_report.py:376`) | A non-verified STEP reached users | CHK-PUBLISH |
| Verdict overwritten in place | "CAD under test: … (it2, overwritten in place)" (`OOM-P03/6_RE_work/VERDICT.md:6`) | it1 evidence is only second-hand | CHK-SUPERSEDED |
| Circular validator shown as a pass | OD validator 13/13 with scan-derived expected values (`OD-H12/README.md:70-71`) | It is a consistency check | Label it so; never list it as independent evidence |
| Re-scoping a failing interface to "interior" silently | B02 SAF-1 boss 1.540 re-scoped (`OOM-B02/6_RE_work/VERDICT.md:135-136`) | The gate got weaker, not the geometry better | Declare it as a limitation (B02 did) |

## 4. Wording checklist for `limitations.json`

- One limitation per risk; the highest-risk item first (B02 put F01 first in its open items,
  `70_report.py:349`).
- Use status words: ABSENT, UNVERIFIED, ASSUMED, PHOTO-INFERRED, MASKED PASS, NOT MET.
- Put every number in a placeholder. Integers used as counts should also come from JSON when
  one exists (for example the Tier-1 dims count).
- A re-run trigger is a concrete observation: "one caliper reading of X", "photo of Y face",
  "screw removed and bore rescanned". Not "more data".
- The claim boundary always has at least one "not fit for" line. For a scan-only run, say
  that absolute scale is not caliper-verified (B02 limitation 2; OD scale assumption).
