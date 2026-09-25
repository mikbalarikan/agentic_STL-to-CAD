# SYNTHESIS — what the evidence earns

Inputs: `analysis/golden/{M02-02-03,OD-H12,OOM-B02,OOM-P03,dreame_brush-caps}.md` and
`analysis/baseline/{stl2step-skills,oomwoo-re-pipeline,facet-film-transferable}.md`.
Every row below cites the extraction file that holds the primary-path citations; follow
it to the golden record. `OOM-E01` is a stub and is not counted.

## 0. Classification rules (from the run plan)

- **RULE**: done in ≥ 2 successful projects (or ≥ 2 parts with independent records).
- **HEURISTIC**: seen in 1 success. Labelled `(heuristic, n=1: <project>)` in the skills.
- **CHECK**: a named failure check. Earned by a recorded failure, REVISE, band miss or
  limitation. It gets a name (`CHK-…`) so skills, reviews and verdicts can refer to it.
- **DROPPED**: a baseline rule the evidence contradicts, with the reason.
- **OPEN**: evidence conflicts or is missing → `QUESTIONS.md`. The skills state the
  conflict and do not pick a number.

Column keys: **M02** gear · **OD** OD-H12 pump · **B02** side brush · **P03** mop bracket ·
**DRM** Dreame caps (screw + snap). Cell values: `Y` done · `–` not done / not recorded ·
`F` done and failed or missed · `L` declared limitation · `n/a` not applicable.

### 0.1 Honest outcome table (the starting point)

| Project | Official outcome | What the record really shows | Source |
|---|---|---|---|
| M02 | QA PASS (22/22) | Spec-conformance only. **No scan datum, no scan deviation gate.** The source scan is not in the repo. An earlier scan-derived 27T/Ø21.75 candidate was wrong. | `analysis/golden/M02-02-03.md` §7, §8, Questions 1–2 |
| OD | Delivered, operator "good result" | Validity PASS. **Band NOT MET**: scan→CAD p95 0.448 / max 2.49 vs 0.30 / 0.80. Explained per region. The 13/13 validator is circular. | `analysis/golden/OD-H12.md` §7, §9 |
| B02 | APPROVED it2/3 | 3 declared limitations. Tier-1 covers 5 of 24 dims. The hex pocket is a **masked** pass (unmasked 1.624). Datum audit 0.429° with no threshold. QA not independent (A13). | `analysis/golden/OOM-B02.md` §7–§9 |
| P03 | APPROVED it2/3 (it1 REVISE) | it1 missed the drive stem. The datum was ICP-refined to its own CAD. It sits 0.600 mm from QA best fit. Stem max 2.424 > 0.8 was never banded. | `analysis/golden/OOM-P03.md` §7–§9 |
| DRM screw | PASS | p95 0.085 / max 0.245 on the full-res scan, no exclusions. | `analysis/golden/dreame_brush-caps.md` §7 |
| DRM snap | Delivered | **Official gate `overall_pass: false`**: max 1.226 > 0.80, p95 0.157 within band. Artefact masks do not clear it. The golden index does not mention the fail. | `analysis/golden/dreame_brush-caps.md` §7, §9, Questions 1 |

Of six parts, one (DRM screw) passes a scan-deviation band with no masks and no caveats.
Every other success carries a declared limitation, a masked or circular gate, or a missed
band. The new skills must make that normal state *expressible*. The baseline skill offers
only "blocking PASS" (`analysis/baseline/stl2step-skills.md` §5.6, §6.11), and practice
routinely stepped outside it.

## 1. Cross-project matrix

### 1A. Intake and scan hygiene

| # | Practice | M02 | OD | B02 | P03 | DRM | Class |
|---|---|---|---|---|---|---|---|
| A1 | Record scan stats at intake: faces, vertices, components/bodies, watertight, bbox, sha256 | Y | Y | Y | Y | Y | **RULE** |
| A2 | Decimated working copy for analysis; keep the original; decimation provenance logged | – | – | Y | Y | Y | **RULE** |
| A3 | Official deviation gate runs on the full-resolution scan | n/a | Y | Y | Y | Y | **RULE** |
| A4 | Remove scanner furniture and fragments explicitly (largest body; table by z + up-normal) and report the fraction | – | – | Y (bristles, screw) | – | Y (table 9.3 %) | **RULE** |
| A5 | Weld an unwelded STL; check the volume sign and flip inward normals | – | – | Y | Y (weld) | – | **RULE** |
| A6 | Units/scale check against a measured reference; ONE uniform scale only if the disagreement is uniform, otherwise flag | Y (operator) | L (assumed mm) | Y (non-uniform → none) | Y (1 axis) | L | **RULE** (+ CHK-SCALE) |
| A7 | Measure the scan noise floor on a clean primitive; use it to set datum and rounding tolerances | – | Y (p95 0.13) | Y (rim rms 0.052) | Y (rim resSD 0.039) | Y (plane rms 0.007 / 0.029) | **RULE** |
| A8 | Enumerate every feature, including interior, from BOTH the mesh and the profile photos, before building | – | – | Y (intake had errors) | F (stem missed) | – | **RULE** + CHK-ENUM |
| A9 | State partial angular coverage / occlusion map at intake | – | Y (in gate) | Y (occlusion map) | L (270° only in report) | – | **RULE** |
| A10 | Soft or deformable features (bristles) are modelled to the rigid anchor and excluded | – | – | Y | – | – | HEURISTIC (n=1 B02) |

Evidence: `analysis/golden/*.md` §0–§2; `analysis/golden/OOM-P03.md` §8 (stem);
`analysis/golden/OOM-B02.md` §3 (weld, normals), §12.13 (bristles).

### 1B. Datum and alignment

| # | Practice | M02 | OD | B02 | P03 | DRM | Class |
|---|---|---|---|---|---|---|---|
| B1 | Named design frame: primary levels, secondary clocks, origin pins; each has a functional reason | – (spec frame) | Y (axis + plate normal) | Y (rim + axis + arm 1) | Y (disc + rim circle; clocking not recorded) | Y (plane + bore + flat) | **RULE** |
| B2 | Primary = functional/mating surface **or** axis for axis-primary parts; never "largest facet" by default | – | Y (axis) | Y (rim seat) | Y | Y (plane near a stated normal) | **RULE** |
| B3 | Plane by RANSAC + SVD refine; record rms/max residual | – | – | Y | – (PCA) | Y (seeded) | **RULE** |
| B4 | Axis / origin from robust circle fits on sections (Kåsa / IRLS) or from normals (correct eigen form); never bbox | – | ? | Y | Y | Y | **RULE** |
| B5 | Measure axis tilt; do not hard-code it | – | – | Y (audit) | – | L (tilt = 0) | CHK-TILT |
| B6 | Clock by a named feature with an explicit rule; store the angle | – | Y | Y | L (not recorded) | Y | **RULE** |
| B7 | Persist `alignment.json` with matrix, scale, noise, fit residuals, named origin | – | L (bare 4×4) | partial | partial | Y (lite schema) | **RULE** (from 2 partial + 2 gaps) |
| B8 | Independent datum audit by the verifier with its own code | – | – | Y (0.429° / 0.451) | Y (0.154° / 0.600) | – | **RULE**; threshold OPEN (Q2) |
| B9 | Never refine the datum by ICP against your own CAD and then gate with it | – | – | – | F | – | CHK-CIRCULAR |
| B10 | Record angles only in the frozen datum frame; state the sign convention | – | – | F (−71° vs +59°) | – | – | CHK-FRAME |
| B11 | Sanity landmarks after alignment (known features land where expected) | – | – | Y | Y | Y | **RULE** (+ facet-film T3) |

Evidence: `analysis/golden/*.md` §3; `analysis/baseline/oomwoo-re-pipeline.md` §3 (DOF
ladder, audit band), §7; `analysis/baseline/stl2step-skills.md` §5.1 (eigen formula).

### 1C. Measurement and design intent

| # | Practice | M02 | OD | B02 | P03 | DRM | Class |
|---|---|---|---|---|---|---|---|
| C1 | Planar sections along the datum axis and radial half-plane sections through the axis | – | Y | Y | Y | Y | **RULE** |
| C2 | (r,z) / (θ,r) density maps and angular profiles R(θ) for turned and lobed parts | – | – | Y | Y | Y | **RULE** |
| C3 | Count patterns by rotational order (FFT / residual per order), never by crest peaks | Y (peaks gave 31, 16) | – | Y (3-fold Fourier) | Y (FFT F[8]) | – | **RULE** + CHK-COUNT |
| C4 | Authority: operator/caliper > scan > photo for dimensions; photo for intent | Y | L (scan only) | Y | Y | L (scan only) | **RULE** |
| C5 | Photo-transcribed caliper readings carry a photo id, owner-confirmed attribution and ±0.1 effective uncertainty | – | – | Y | Y (±0.1 not stated) | – | **RULE** |
| C6 | Check each caliper reading is geometrically achievable on the scan (two-jaw support window) before building to it | – | – | Y (caught F06) | – | – | CHK-ACHIEVABLE (failure-earned) |
| C7 | Log every parameter as measured → chosen, with rule and SOURCE tag | Y (assumptions) | F (chosen only) | Y | Y | Y | **RULE** |
| C8 | Round only within measured noise; **no fixed 0.1/0.5/1.0 step** | Y (verbatim) | Y (unsnapped) | Y | Y | Y (0.01–0.05) | **RULE** (drops baseline) |
| C9 | Do not intent-snap an uncalipered critical interface; hold the scan fit and declare it | – | – | Y (hex AF 7.358) | – | – | **RULE** via B02 + OD (coil kept) |
| C10 | Symmetry / equal pitch is enforced only when measured scatter is within noise; otherwise keep measured and declare | Y | Y (asym screws) | Y (120° enforced) | Y (8-fold) | Y (unequal legs kept, cups equalised) | **RULE** |
| C11 | Unscanned or occluded geometry gets a provenance tag (photo-inferred / assumed / standard), never "measured" | Y (nothing invented) | Y (core tube declared) | Y (A9) | Y (socket) | Y (hook underside) | **RULE** |
| C12 | Treat an unexplained coherent cluster as real until disproven (count points, check photos) | – | – | – | F (stem) | – | CHK-CLUSTER |
| C13 | Each measurement records its estimator and point set | – | – | Y | partial | partial | **RULE** (facet-film T5) |
| C14 | Model a tapered/wavy surface as such, or declare the p95 cost of the simplification | – | L (coil) | L (arm mean path) | – | L (ramp ±0.07) | **RULE** (declare) |
| C15 | Gear: one involute tooth + pattern; measured OD sets the tip; unmeasured gear params listed as assumptions | Y | – | – | – | – | HEURISTIC (n=1 M02) |

Evidence: `analysis/golden/*.md` §4–§5; `analysis/golden/M02-02-03.md` §4 (peak count);
`analysis/golden/OOM-B02.md` §8 (F06); `analysis/golden/OOM-P03.md` §8 (stem).

### 1D. Rebuild (build123d)

| # | Practice | M02 | OD | B02 | P03 | DRM | Class |
|---|---|---|---|---|---|---|---|
| D1 | A written, ordered feature plan before code (plan or strategy table) | Y (feature chain) | – | Y (intake §6) | Y (intake §6) | Y (README tree) | **RULE** |
| D2 | Revolve an (r,z) profile as the primary body for turned regions | – | Y | Y | Y | Y | **RULE** |
| D3 | Sub-bodies built separately then unioned (assemblies, arms, cores) | Y (core bridge) | Y | Y | Y | Y | **RULE** |
| D4 | One instance + placements for repeated features (loop or `PolarLocations`) | Y | Y | Y | Y | Y | **RULE** |
| D5 | Cut tools (sectors, slots, pockets) as separate solids subtracted | – | Y | Y | Y | Y | **RULE** |
| D6 | Parameters in one dict/JSON drive the whole model | Y | Y | Y | Y | Y | **RULE** |
| D7 | Fillet/chamfer in try/except with a per-feature OK/FAILED log; log the radius actually used | – | – | Y (silent fallback) | Y (silent skip) | Y | **RULE** + CHK-FILLET |
| D8 | Fillets last, *except* local fillets right after their parent when a later op would destroy the edge | – | Y (inside sub-bodies) | Y (last) | Y (last) | Y (mixed) | **RULE** (refines baseline) |
| D9 | Offset cut tools slightly (0.02 mm) to avoid tangent-coincident booleans | – | – | Y | – | – | HEURISTIC (n=1 B02) |
| D10 | Analytic surfaces dominate; face count stays in the hundreds | F (2354 planar facets) | Y (213 analytic) | Y (185; 40 B-spline) | Y (500) | Y (56 / 63) | **RULE** + CHK-PATCHWORK; threshold OPEN (Q3) |
| D11 | Tri-axis extrude-intersect as the default prismatic strategy | – | – | – | – | – (intersect in spirit once) | **DROPPED** (see §3) |
| D12 | Single valid closed solid; STEP re-import check; abort on failure | Y | Y | Y | Y | Y | **RULE** |
| D13 | Independent-kernel import (e.g. NX) when available | – | Y | Y (re-export) | Y (re-export) | Y | **RULE** (when available) |
| D14 | Deliver two frames: datum-frame STEP and scan-frame STEP (inverse T, re-orthonormalised) | – | Y | – | – | Y | **RULE** |
| D15 | Loft only through fitted sections (non-ruled); never ruled lofts or polyline stacks of raw scan slices | – | – | Y (22-section loft) | – | – | **RULE** from baseline W01 failure + B02 |

Evidence: `analysis/golden/*.md` §6, §11; `analysis/baseline/oomwoo-re-pipeline.md` §5 (W01).

### 1E. Verification

| # | Practice | M02 | OD | B02 | P03 | DRM | Class |
|---|---|---|---|---|---|---|---|
| E1 | Two-way deviation (scan→CAD and CAD→scan) | – | Y | Y | F (one way) | Y | **RULE** |
| E2 | Distance = exact point-to-triangle over KD-tree candidates, seeded sampling | – | Y | – (NN) | – | Y | **RULE** |
| E3 | Stats p50 / p95 / p99 / max / rms, with n and sampling stated | – | Y | Y | Y | Y | **RULE** |
| E4 | Per-region / per-zone buckets (z-bands, named interfaces, interior) | – | Y | Y | Y | Y (masks) | **RULE** |
| E5 | Masks are named, justified, reported with masked fraction; masked and unmasked shown side by side | – | – | Y (+ sensitivity sweep) | – | Y | **RULE** + CHK-MASK |
| E6 | CAD→scan split into observable / unobservable (ray test or open-boundary mask) | – | Y (ray cone, 25.65 %) | Y (M3 boundary mask) | – | – | **RULE** (purpose); ray method HEURISTIC (n=1 OD) |
| E7 | Independent registration (ICP) by the verifier, convergence reported | – | – | Y (48 of 60 iters) | Y (30 iters) | ? (official gate) | **RULE** |
| E8 | Tier-1: re-measure every calipered dim on the final STEP with independent code (simulated caliper or analytic query) | Y | – | Y (jaws) | Y (feature queries) | – | **RULE** |
| E9 | Validator with expected values from the same scan is labelled a consistency check, not independent evidence | – | Y | – | – | – | CHK-CIRCULAR |
| E10 | Hash-freeze the STEP before QA; verify unchanged after | Y | – | – | – | – | HEURISTIC (n=1 M02) |
| E11 | Reproducibility rerun (fresh process → same volume/bbox or hash) | Y | – | – | – | – | HEURISTIC (n=1 M02) + facet-film T32 |
| E12 | Section overlays CAD-on-scan; check every panel actually shows scan | – | Y | Y | Y | Y (150° panel empty) | **RULE** + CHK-OVERLAY |
| E13 | Fast in-house gate cross-checked against an official gate | – | – | – | – | Y (p95 0.0860 vs 0.0851) | HEURISTIC (n=1 DRM) |
| E14 | Locate points over the max band spatially (they reveal missing features) | – | Y (0.16 % clusters) | – | Y (4907 pts at r<6.4) | Y (flap) | **RULE** |
| E15 | Photo plausibility check (every photographed feature exists; nothing hallucinated) | – | – | Y | Y | – | **RULE** |
| E16 | QA runs in a separate context/agent; if not, declared | Y | – | L (A13) | Y | – | **RULE** |

Evidence: `analysis/golden/*.md` §7, §11; `analysis/golden/OD-H12.md` §7 (observability).

### 1F. Verdict, iteration and delivery

| # | Practice | M02 | OD | B02 | P03 | DRM | Class |
|---|---|---|---|---|---|---|---|
| F1 | A missed band is reported with its number, per region, cause and options. It is never loosened or faked. | n/a | Y | Y (masked pass) | Y (stem note) | Y (snap) | **RULE** |
| F2 | Verdict vocabulary beyond pass/fail: approved with declared limitations; delivered with band not met (needs human acceptance) | Y (claim boundary) | Y | Y | Y | Y | **RULE** |
| F3 | Iterations bounded (3 loops per part) with a HALT | – | – | Y (2/3) | Y (2/3) | – | **RULE** (RE_SPEC + 2 goldens) |
| F4 | Keep each superseded iteration (script, STEP, params, verdict) | – | – | Y | F (overwritten) | – | **RULE** + CHK-SUPERSEDED |
| F5 | Nothing is published to the delivery folder before the verdict | – | – | F | – | – | CHK-PUBLISH |
| F6 | Compare iterations only with like-for-like gate protocols | – | – | F | – | – | CHK-LIKE4LIKE |
| F7 | Claim boundary: what the result is NOT (e.g. not fit for tooling until X) | Y | Y | Y | Y | – | **RULE** |
| F8 | Report numbers are read from the gate JSON, never retyped | – | – | F (drift ≤0.02) | – | – | CHK-NUMBERS |
| F9 | Delivery doc: method, parameter table with sources, gate tables, limitations, frames, reproduction commands | Y | Y | Y (PDF) | Y (PDF) | Y | **RULE** |
| F10 | A re-run trigger is named for each limitation (e.g. "one caliper on F01 → re-run") | – | Y (next steps) | Y | Y (socket) | – | **RULE** |

## 2. Named failure checks

Each check has a name, the failure that earned it and the stage that runs it.

| Check | Catches | Earned by | Runs in |
|---|---|---|---|
| **CHK-SCALE** | Wrong units or a scanner scale error. Uniform → ONE scale; non-uniform → flag, no scale. | OD unverified mm; B02 non-uniform 0.4–1.6 % | intake |
| **CHK-ENUM** | Features missing from intake. Cross-check the profile photos and on-axis/above-feature material against the feature list. | P03 it1 missing stem; B02 intake errors | intake, verify |
| **CHK-CLUSTER** | A coherent point cluster dismissed as "occlusion". Count the points, check for a flat top, check the photos. | P03 it1 | measure, verify |
| **CHK-TILT** | Bore/axis tilt assumed 0. | DRM `tilt_deg` hard-coded; snap origin from 2 stations | intake |
| **CHK-FRAME** | Angle/sign convention drift between intake and the frozen frame. | B02 −71° vs +59° | measure |
| **CHK-CIRCULAR** | A gate that checks a result against itself: datum ICP-refined to own CAD; expected values from the same scan. | P03 datum; OD 13/13 validator | verify |
| **CHK-COUNT** | Wrong tooth/lobe/slot count. Use rotational order at ≥3 stations; peak counting is diagnostic only. | M02 peaks 31 / 16; M02 wrong 27T candidate; P03 "6+6" → 8 | measure, verify |
| **CHK-ACHIEVABLE** | A caliper reading the scan geometry cannot produce (misattributed jaw placement). | B02 F06 Δ +0.647 | measure |
| **CHK-FILLET** | A fillet silently skipped or silently shrunk. | B02 fallback, P03 skip | rebuild, verify |
| **CHK-PATCHWORK** | Faceted or re-tiled surfaces: face count, analytic-area share, no ruled lofts or polyline stacks. | baseline W01 (5,485 faces); M02 2354 planar facets | rebuild, verify |
| **CHK-MASK** | A PASS that exists only because of a mask. Report sensitivity and masked vs unmasked. | B02 hex 1.624 unmasked; DRM snap masks | verify |
| **CHK-OVERLAY** | Overlay panels with no scan trace. | DRM 150° panel | verify |
| **CHK-SUPERSEDED** | Lost iteration evidence. | P03 it1 verdict overwritten | deliver |
| **CHK-PUBLISH** | Deliverable published before the gate verdict. | B02 it1 | orchestrator |
| **CHK-LIKE4LIKE** | Iteration "improvement" produced by a changed gate protocol. | B02 it1 → it2 Tier-2 | verify |
| **CHK-NUMBERS** | Report numbers retyped or taken from an intermediate run. | B02 verdict drift | deliver |
| **CHK-INDEP** | QA done in the builder's context without declaring it. | B02 A13; baseline E03/E05 | orchestrator |

## 3. Baseline rules dropped or rewritten

| Baseline rule | Where | Verdict | Reason (evidence) |
|---|---|---|---|
| Revolve axis = smallest eigenvector of Σ(I − nnᵀ) | `stl2step-build123d/SKILL.md:39`, freecad `:41` | **DROPPED (wrong math)** | That formula returns a near-normal direction. The axis is the smallest eigenvector of Σ nnᵀ, as the golden code does (`analysis/baseline/stl2step-skills.md` §5.1). |
| Primary datum = largest trimesh facet | `SKILL.md:24-29` | **DROPPED** | On the DRM scan the largest facets are ~0.27 mm² pieces. Goldens used functional planes, axes and offset histograms. RE_SPEC also says functional beats largest (`analysis/baseline/stl2step-skills.md` §6.1). |
| Round to fixed 0.1 / 0.5 / 1.0 mm steps | `SKILL.md:52` | **DROPPED** | No golden did this. All rounded within measured noise or kept caliper values verbatim (matrix C8). |
| Snap near-concentric / near-equal always | `SKILL.md:53` | **REWRITTEN** | Snap only within noise; keep measured asymmetry and declare it (OD coil, DRM legs) (matrix C10). |
| Patterns need equal pitch; never model instances individually | `SKILL.md:70` | **REWRITTEN** | Keep "one instance + placements"; placements may be measured unequal (DRM legs) (matrix D4, C10). |
| Tri-axis extrude-intersect as the prismatic strategy | `SKILL.md:68` | **DROPPED as default** | Not observed in any golden build. Kept at most as a named option in a reference (matrix D11). |
| Loft through section curves as the freeform fallback | `SKILL.md:72` | **REWRITTEN** | Only non-ruled lofts through fitted sections. Never polyline stacks or ruled lofts of raw scan slices (W01 failure; matrix D15). |
| Fillets strictly last | `SKILL.md:71` | **REWRITTEN** | Last by default; local fillets directly after the parent feature are allowed when later ops destroy the edge, and must be logged (matrix D8). |
| Deviation gate is the single blocking quality bar | `SKILL.md:8,74` | **REWRITTEN** | Deviation cannot detect patchwork (W01). Authoritative dims outrank scan fit (M02). Every scan-gated golden but one carried a miss or caveat. The gate stays mandatory, and the verdict gains explicit limitation states (§0.1, matrix F2). |
| p95 ≤0.3 / max ≤0.8 (plastic), ≤0.15 / ≤0.5 (machined) as defaults | `SKILL.md:87` | **OPEN** (Q1) | No source is given. RE_SPEC Tier-2 is p95 ≤1.6 / max ≤4.0 with a caliper tier. Goldens used both regimes. The skills must not pick silently. |
| Gate snippet measures an untransformed mesh | `SKILL.md:31` vs `:79` | **DROPPED (bug)** | Frame mismatch (`analysis/baseline/stl2step-skills.md` §5.2). |
| FreeCAD vertex-to-vertex gate | freecad `SKILL.md:82` | **DROPPED** | Not a surface distance, so its numbers aren't comparable to the build123d gate (`analysis/baseline/stl2step-skills.md` §5.4). |
| Build123d vs FreeCAD bake-off before choosing a tool | both skills, last line | **DROPPED** | RE_SPEC closed the bake-off. Every golden used build123d. FreeCAD → one-page reference appendix. |
| Default mesh repair (harmonise normals, remove duplicates) | freecad `SKILL.md:17-18` | **REWRITTEN** | Never modify the evidence. Weld and flip normals only on a working copy, and log it (matrix A5; facet-film T4). |
| GitHub issue/PR per part, per-feature PRs, Drive sync, Slack relay, model-tier rules | RE_SPEC §8–§12 | **DROPPED from skills** | Org-specific process. No golden record shows the v3/v4 feature loop (both OOM goldens pre-date v3). Only the transferable core stays: plan before code, independent QA, bounded iterations. |
| Per-feature manager review with a FEATURE BUDGET | RE_SPEC §5–§6 | **KEPT as a lighter rule** | Motivated by W01 (baseline evidence), but no golden ran it. Skills keep a written plan with an expected op/face count (matrix D1, D10), not the PR loop. |

## 4. Numbers the skills may state (with source)

Only these numbers enter a SKILL.md. Each carries its source.

| Number | Meaning | Source |
|---|---|---|
| ±0.15 mm | Tier-1 caliper band: \|CAD − caliper\| per dim | `baseline/oomwoo-re-pipeline/RE_SPEC.md:170` |
| p95 ≤1.6 / max ≤4.0 mm | Tier-2 whole-part skin band after independent ICP + skin mask (RE_SPEC regime) | `RE_SPEC.md:174` |
| max ≤0.8 mm | Tier-2 named functional interfaces not covered by calipers | `RE_SPEC.md:175` |
| p95 ≤0.30 / max ≤0.80; p95 ≤0.15 / max ≤0.50 | Baseline skill bands (consumer plastic / machined), source unstated | `baseline/skills/stl2step-build123d/SKILL.md:87` (see Q1) |
| ≤0.3° / ≤0.15 mm | Datum audit (RE_SPEC); both approved goldens exceeded it | `RE_SPEC.md:241` (see Q2) |
| 3 | Max full-loop iterations per part; 3 REVISE per feature | `RE_SPEC.md:248-250` |
| ±0.1 mm | Standard-size snap window for caliper values | `RE_SPEC.md:92` |
| ±0.1 mm effective | Uncertainty of photo-transcribed caliper readings | `analysis/golden/OOM-B02.md` §4 (`MEASUREMENTS.md:10`), `baseline/oomwoo-re-pipeline/TRACKER.md:13` |
| ≤0.028 mm | Max decimated→original deviation of the repo's inspection copies | `golden-examples/README.md` |
| 0.05–0.1 mm | RANSAC plane tolerance ≈ scan noise (both baseline docs); golden plane rms 0.007–0.052 | `RE_SPEC.md:127`; golden §3 |

Any other number (sample counts, ray-cone angles, mask radii) is written as "the golden
used X (source)" and treated as a parameter, not a threshold.

## 5. What each project uniquely contributes (heuristics worth keeping)

- **M02:** gear modelling (involute tooth + pattern, OD sets the tip); rotational-order
  tooth count; hash-frozen fail-closed QA; reproducibility rerun; explicit "nothing
  unmeasured was invented" list.
- **OD:** ray-cast observability split; z-band regional gate; honest band-miss report
  with next steps withheld for lack of calipers; single-solid assembly via sub-bodies
  with declared invented connectors.
- **B02:** simulated two-jaw caliper (Tier-1 on the STEP and achievability of a reading);
  independent datum audit code; mask sensitivity sweep; superseded-iteration folder with
  a one-parameter diff.
- **P03:** angular FFT counts; photo-transcribed calipers with photo ids; missed-feature
  localisation via over-band point clusters. Also the counter-example of a datum
  refined to its own CAD.
- **DRM:** seeded RANSAC + offset-histogram datum; dual-frame export; exact KD-candidate
  gate; named artefact masks; fast vs official gate agreement; the only unmasked clean
  pass (screw).

## 6. Coverage gaps (no golden evidence either way)

- Sheet-metal, freeform / styled surfaces with no analytic intent, and multi-body STEP
  deliverables have no golden example. The skills must say so and HALT or ask, rather
  than improvise a method (`analysis/golden/OD-H12.md` §9: multi-body "a separate job").
- Standard-size snapping (threads, drill sizes) is doctrine (`RE_SPEC.md:92,160`) but no
  golden applied it, so it stays a heuristic.
- The v3/v4 per-feature review loop has no golden evidence (§3).
