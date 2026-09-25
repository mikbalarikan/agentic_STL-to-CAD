# Baseline audit — `stl2step-build123d` and `stl2step-freecad` (v0)

Scope: `baseline/skills/stl2step-build123d/` (abbrev. **B**) and `baseline/skills/stl2step-freecad/` (abbrev. **F**), checked against `baseline/oomwoo-re-pipeline/RE_SPEC.md` and spot-checked against three golden projects. Citations are `path:line`. `B:n` = `baseline/skills/stl2step-build123d/SKILL.md:n`; `F:n` = `baseline/skills/stl2step-freecad/SKILL.md:n`; `RS:n` = `baseline/oomwoo-re-pipeline/RE_SPEC.md:n`. Golden prefixes: `DB/` = `golden-examples/dreame_brush-caps/`, `OD/` = `golden-examples/OD-H12_delonghi-dedica-pump/`, `M02/` = `golden-examples/M02-02-03_watertight-design-intent/`.

---

## 1. Inventory

| File | Lines | Holds |
|---|---|---|
| `baseline/skills/stl2step-build123d/SKILL.md` | 101 | Frontmatter (B:1-4); doctrine para (B:8); 8-step pipeline with inline snippets (B:10-90); 6 traps (B:92-98); companions/bake-off pointer (B:100-101). |
| `baseline/skills/stl2step-freecad/SKILL.md` | 102 | Same 8-step pipeline re-expressed for `freecadcmd` / Mesh / Part / MeshPart / Reen (F:10-91); 6 traps (F:93-99); bake-off protocol (F:101-102). |

Nothing else is in either folder: no `scripts/`, no `references/`, no tests, no example data. Both skills link `[[cad-qa-gate]]` and `[[cad-section]]` (B:90, B:101, F:91, F:102), but neither skill exists in `baseline/skills/` (only `stl2dxf-facet-film`, `stl2step-build123d`, `stl2step-freecad` are present). F:8 points to "exe path in the local-toolchain memory", which is not in the repo.

---

## 2. Rules (numbered, with agree/differ)

Legend: **=** both skills say this; **B only** / **F only**; **≠** both skills cover it but say different things.

### Doctrine
1. Rebuild design intent, do not wrap triangles. **=** (B:8, F:8)
2. Success is measured by a CAD-vs-STL deviation gate, not judged by eye. **=** (B:8, F:8)
3. Follow the pipeline steps in order. **=** (B:10, F:10)

### §1 Intake and hygiene
4. Load the mesh and print bbox, watertightness and face count. **≠** in API: B uses trimesh (B:16-18). F uses `Mesh.Mesh`, `harmonizeNormals()` and `removeDuplicatedPoints()` (F:16-20), which is normal/duplicate repair that B does not do.
5. Units sanity: if the bbox is about 0.05–0.5, the mesh is in metres, so ×1000. **=** (B:17, F:21). B frames this as "a vacuum housing should be ~50–500 mm".
6. Decimate a working copy when the mesh has more than 400k faces. **≠**: B keeps 20% (B:19). F gives no ratio and says "check signature on 1.1" (F:23).
7. Keep the ORIGINAL mesh for the deviation gate. **=** (B:21, F:23)
8. F only: fit dimensions on the fine mesh "where it matters" (F:23).
9. B only: non-watertight scans are fine, so do not "repair" away real geometry (B:21). F repairs normals and duplicates by default (F:17-18).

### §2 Datum
10. Primary datum = plane fitted to the **largest flat region**, aligned to XY. **=** (B:24, F:26)
11. Map the base normal to −Z ("base on floor"), then translate so the part sits on Z=0. **=** (B:30-32, F:33-35)
12. Lock rotation with a second feature (a large cylinder axis or a second plane). **=** (B:24, F:37). F adds the convention "large bore axis → +Z/+X" (F:37).
13. Put the origin at a feature intersection, e.g. bore axis ∩ base plane. **=** (B:24, F:26)
14. Refine with RANSAC at tol ≈ scan noise, 0.05–0.1 mm. **=** (B:34, F:29-30). B applies it "when the flat is noisy". F makes it the default.
15. B only: take the seed plane from `m.facets_area` argmax (B:27-29).
16. Record the full transform and reuse it for the gate. **=** (B:34, F:35-37)

### §3 Segmentation
17. Classify regions as planes, revolutes or freeform before choosing a strategy. **=** (B:37-40, F:39-42)
18. Planes: trimesh facets (B:38) vs `msh.getPlanarSegments(tol)` or normal clustering (F:40). **≠** in tool only.
19. Revolute axis: least-squares fit from normals, "direction = smallest eigenvector of Σ(I − n nᵀ)", radius = mean distance to the axis, cone if the radius is linear along the axis. **=** (B:39, F:41). §5 shows this formula is wrong in both skills.
20. Freeform: handle last with loft/fillets (B:40), or earmark for Reen/loft (F:42). **≠**

### §4 Sections
21. Stack of planar sections, denser where geometry changes (B:44-46), or `crossSections` in one call (F:45-51). **≠** in tool only.
22. Prismatic parts: slice along all three axes to get three sketches. **=** (B:48, F:52)
23. Revolutes: use half-planes through the fitted axis to get the profile. **=** (B:48, F:52)

### §5 Fitting and snapping
24. Fit lines and arcs, with corners found by turning angle. B names Kåsa/Taubin (B:51). F says "least-squares circle" (F:55). **=**
25. Round dimensions to 0.1 / 0.5 / 1.0 mm "when within scan noise". **=** (B:52, F:55)
26. Snap near-equal radii equal, and force concentric, parallel, perpendicular and symmetric relations. **=** (B:53, F:55)
27. Recognise standard sizes (drill/thread, hex A/F). **=** (B:54, F:55)
28. Log every measured → snapped pair. **=** (B:54, F:55)
29. F only: sculpted profiles use `BSplineCurve.approximate(DegMax=3, Tolerance=0.05)` (F:56-59).

### §6 Rebuild
30. Prismatic: three extrudes, then boolean intersect (the "tri-axis NX trick"). **=** (B:68, F:66)
31. Revolute: fitted half-profile, revolve about the fitted axis, then union or cut. **=** (B:69, F:67-68)
32. Patterns: model one instance and replicate it. **=** (B:70, F:70). B adds "equal radius, equal angular/linear pitch" and "Never model pattern instances individually" (B:70).
33. Fillets/chamfers last, with radii measured from sections. **=** (B:71, F:71). B only: leave tiny scan-noise blends out unless they are functional (B:71).
34. Freeform: `loft()` through sections and flag it (B:72), or `Reen.approxSurface` / `Part.makeLoft` and flag it (F:72). **≠**
35. F only: validate with `check()`, `isValid()`, single solid and `removeSplitter()` (F:73). **B has no validity step.**

### §7 Deviation gate
36. Two-way distance against the ORIGINAL aligned mesh. **=** (B:75, F:76)
37. Method **≠**. B uses `trimesh.proximity.closest_point` on all scan vertices, plus 20k unseeded CAD samples (B:77-85). F uses a cKDTree from CAD-mesh points to scan *points* (vertex, not surface, distance), plus exact `distToShape` on 2000 seeded scan points (F:78-86).
38. Report RMS / p95 / max in both directions. **=** (B:84, F:86)
39. Bands: see §3. **=** (B:87, F:88)
40. Intent-snap deviation is correct: report it, don't chase it. **=** (B:87, F:88)
41. Exclude worn/damaged zones by region and note the restoration. **=** (B:87, F:88)

### §8 Deliverables
42. STEP (+ STL), parameter table, deviation report and section-overlay images. **=** (B:90, F:91). F only: plot in system Python if FreeCAD lacks matplotlib (F:91).

### Traps
43. B only: average 2–3 nearby stations, or fit on one and verify on its neighbours (B:93).
44. B only: extrude-intersect over-cuts concave parts, so decompose and union (B:94).
45. Never take a revolve axis from the bbox centre. **=** (B:95, F:97)
46. B only: verify units against a caliper dimension (B:96).
47. B only: rtree dependency, with a cKDTree fallback (B:97).
48. Copy heavy meshes to local scratch. **=** (B:98, F:99)
49. F only: bundled-Python package visibility (F:94); `crossSections` loop order is arbitrary, so match loops by centroid (F:95); `distToShape` is slow, so subsample (F:96); `makeShapeFromMesh` is a flagged last resort (F:98).

### Companions
50. Run BOTH skills on a shared benchmark and record the winner in BAKEOFF.md before committing to a tool (B:101, F:102). F makes this a protocol ("BAKE-OFF PROTOCOL").

---

## 3. Gates and thresholds

| Gate | Threshold | Where stated | Source of the number |
|---|---|---|---|
| Unit sanity | bbox ≈0.05–0.5 → metres, ×1000 | B:17, F:21 | Not stated (B: "a vacuum housing should be ~50–500mm") |
| Decimation trigger | >400,000 faces; keep 20% (B only) | B:19, F:23 | Not stated |
| RANSAC plane tol | 0.05–0.1 mm ("≈ scan noise") | B:34, F:29 | Not stated. RS:127 repeats it. RS:25 claims a scanner noise floor of ~0.5–0.8 mm (see §5) |
| Intent rounding step | 0.1 / 0.5 / 1.0 mm, "within scan noise" | B:52, F:55 | Not stated |
| B-spline approx tol | 0.05, DegMax 3 | F:58 | Not stated |
| CAD tessellation for gate | LinearDeflection 0.05 | F:79 | Not stated |
| Exact-distance subsample | ~2000 pts (seed 0) | F:84, F:96 | Stated as a speed trade-off (F:96) |
| CAD→scan samples | 20,000 (unseeded) | B:80 | Not stated |
| PASS, machined | p95 ≤ 0.15 mm, max ≤ 0.5 mm | B:87, F:88 | Not stated ("default; tighten per project") |
| PASS, scanned consumer plastic | p95 ≤ 0.3 mm, max ≤ 0.8 mm | B:87, F:88 | Not stated |
| *Comparison:* RE_SPEC Tier-1 caliper | \|CAD − caliper\| ≤ 0.15 mm per dim | RS:168-170 | "unchanged numbers" (RS:166) |
| *Comparison:* RE_SPEC Tier-2 skin | p95 ≤ 1.6 mm, max ≤ 4.0 mm after ICP + outer-skin mask | RS:172-174 | "ratified 2026-07-26 scan-adjusted bands" (RS:172) |
| *Comparison:* RE_SPEC functional interfaces | max ≤ 0.8 mm | RS:175 | Not stated |
| *Comparison:* RE_SPEC datum audit | ≤ 0.3°, ≤ 0.15 mm | RS:241 | Not stated |
| *Comparison:* RE_SPEC circuit breakers | 3 REVISE per feature; 3 loops per part | RS:248-250 | "unchanged from v2" |

Neither skill has any gate other than the deviation bands. The skills carry no datum-fit residual gate, no B-rep validity gate (F:73 lists checks but no pass/fail), no face-count/anti-patchwork gate and no iteration cap.

---

## 4. Gaps (what a cold agent would not know)

1. **Datum selection beyond "largest flat".** Neither skill says what to do when the largest flat is non-functional, warped or artefactual. It does not say functional/mating beats largest (RS:118), or how to handle axis-primary parts (turned/revolute parts with no dominant flat; OD/README.md:14 uses the pump axis as +Z). It never asks for a *named* origin with a reason (RS:114-115, RS:124).
2. **Datum-fit acceptance.** There is no residual limit and no STOP when the fit is worse than scan noise (compare RS:126-129). The skills never say how to estimate scan noise for a given part. OD/README.md:35 measured p95 0.13 mm on a clean cylinder; DB/README.md:21 reports plane rms 0.007 / 0.029 mm.
3. **Scan fragments and scanner furniture.** Nothing covers disconnected shells or table sheets. DB/report/intake.json shows 104 bodies. DB/report/source/align.py:45-46 keeps the largest body, and DB/README.md:71 found a scanner-table sheet (9.3% of vertices) fused to the part.
4. **Design-intent rounding policy.** Fixed 0.1/0.5/1.0 steps without a decision rule. The skills do not say when to keep the measured value, how to justify a standard-size claim without calipers, or where the authority hierarchy (caliper > scan > photo, RS:89-98) sits. Neither skill mentions calipers except as a trap (B:96).
5. **When not to snap.** Neither skill covers deliberate asymmetry, unequal patterns or small real offsets. Compare DB/README.md:50 (unequal leg angles) and OD/README.md:51 (0.2 mm coil offset, not snapped).
6. **Iteration limits.** There is no cap on fit-rebuild-gate loops and no halt/escalation rule (compare RS:247-253).
7. **Failure verdicts.** The gate is "blocking" (B:74, F:75), but the skills define no verdict for a missed band. They do not describe an honest partial delivery, a waiver or a per-region explanation (compare RS:181-183). Both goldens that used this skill shipped with a band miss (§6).
8. **Visibility masking of unscanned regions.** CAD→scan distance counts CAD surfaces that no scanner could see (bores, gaps, pockets). The skills give no method to classify or exclude them. OD/report/src/gate.py:57-84 does this with a ray-cone test, and OD/README.md:40-41 reports 25.6% of the CAD surface as unobservable.
9. **Scan-artefact masking (scan→CAD).** Only "worn/damaged zones" are covered (B:87). The skills say nothing about burrs, fringes, shadow-bridging or how to define and report masks with their fractions (DB/report/snap_masked_gate.json).
10. **Hidden/interior geometry.** The skills do not say whether to invent unscanned internals, or how to label them. OD/README.md:54, :65-66 invents a core tube and depths. M02/README.md:27 invents nothing.
11. **Output frame.** The skills do not say which coordinate frame the STEP is delivered in. Both golden build123d projects deliver STL-frame and datum-frame STEPs (DB/README.md:9-10; OD/README.md:13-14).
12. **Solid validity (B).** There is no single-solid / closed / valid check, and no STEP re-import check (compare OD/report/export_check.json; M02/model.py:88-101).
13. **Feature failure handling.** Fillets and booleans fail in OCC, but the skills give no try/log/fallback pattern (compare DB/report/source/build_screw.py:44-48, :57-59).
14. **Anti-patchwork / face-count sanity.** Missing entirely (compare RS:255-270).
15. **Determinism.** No seeds are required. RANSAC and sampling are unseeded in B.
16. **Gate density.** The skills do not say how many samples are enough, or vertex vs area-weighted sampling (see §7).

---

## 5. Internal contradictions

**Within or between the skills**

1. **Revolve-axis formula is wrong in both skills.** The axis direction `d` is ⟂ to all normals, so it is the eigenvector of the *smallest* eigenvalue of Σ n nᵀ. That is the *largest* eigenvalue of Σ(I − n nᵀ), because Σ(I − n nᵀ) = N·I − Σ n nᵀ. The skills instead say "smallest eigenvalue of Σ(I − n nᵀ)" (B:39, F:41), which returns a direction close to a surface normal. The golden code uses the correct form: `S = nrm.T @ nrm; eigh(S); v[:,0]` (DB/report/source/datum.py:55-57).
2. **Frame mismatch in the B gate snippet.** The datum transform is applied only to `work` (B:31-32). The gate then measures against `m.vertices` (B:79), and `m` was never transformed in the snippet. Only the prose at B:34 prevents a wrong-frame gate.
3. **"Keep original / don't repair" vs F's default repair.** B:21 says do not repair, but F:17-18 runs `harmonizeNormals`/`removeDuplicatedPoints` unconditionally.
4. **Different gate estimators behind identical bands.** B measures scan-vertex → CAD surface. F measures CAD-mesh vertices → nearest scan *vertex*, which overestimates on coarse scans and is not a surface distance (F:82). The two skills' p95/max are not comparable, which defeats the bake-off rule (F:102).
5. **Loft fallback vs the facet-chasing ban.** B:72 and F:72 recommend lofting through section curves. RS:260-262 forbids "ruled lofts of scan slices" and "Polyline section stacks".
6. **The skills use the deviation gate as the only quality bar.** B:74 calls it "this is the quality bar". RS:268-269 says deviation "can NEVER excuse patchwork", and RS:179 says feature review and the gate are both mandatory.

**vs RE_SPEC §4 tolerance bands (RS:166-183)**

7. **Bands differ by 5×.** The skills use p95 ≤ 0.3 / max ≤ 0.8 for consumer plastic (B:87, F:88). RE_SPEC Tier-2 is p95 ≤ 1.6 / max ≤ 4.0 after ICP + outer-skin mask (RS:174). The skills' 0.8 mm max matches only RE_SPEC's functional-interface max (RS:175).
8. **Registration.** The skills gate in the builder's own datum frame. RE_SPEC requires the verifier's *independent* best-fit ICP (RS:173) and a datum audit first (RS:239-242).
9. **No caliper tier.** RE_SPEC's tight gate is caliper-based, ≤ 0.15 mm (RS:168-170). The skills have no caliper tier, and their "machined" band reuses the same 0.15 as a scan p95 (B:87).
10. **Noise-floor assumption.** RS:25 says "scanner noise floor ~0.5–0.8 mm → calipers are the dimensional authority". The skills treat 0.05–0.1 mm as scan noise (B:34, F:29) and round "within scan noise" to 0.1 mm steps (B:52). The two cannot both be defaults.
11. **Datum rule.** "Largest flat region" (B:24, F:26) vs "Functional/mating surface beats largest surface" (RS:118).
12. **Bake-off status.** The skills mandate a bake-off (B:101, F:102), but RS:26-27 says "tool bake-off is CLOSED — build123d won".
13. **Snapping.** The skills round to 0.1/0.5/1.0 (B:52). RE_SPEC snaps caliper values to a standard only within ±0.1 mm, and scan values only "within scan noise" (RS:160-161). RE_SPEC also requires a SOURCE column (RS:162).

---

## 6. Rules the golden evidence contradicts or refines

Spot checks only. Each item gives the baseline claim first, then the golden evidence.

1. **Largest flat via `m.facets_area`** (B:27-29).
   - Evidence: on the Dreame raw scan the largest trimesh facets are about 0.27 mm² (DB/report/intake.json, `top_facets`). The project instead used normal-cluster + offset-histogram plane grouping, then RANSAC + SVD refinement (DB/report/source/datum.py:27-46, DB/report/source/align.py:21-37).
   - Effect: **refines/contradicts** the seed method for noisy scans.
2. **Base normal → −Z, part on floor** (B:30-32, F:33).
   - Evidence: Dreame levelled the *top* face to +Z with z_top = 0 (DB/report/source/align.py:49-53; DB/README.md:10). OD-H12 is axis-primary: pump axis = +Z, X = frame side-plate normal (OD/README.md:14).
   - Effect: **refines**. The primary datum is a choice per part, not always the base.
3. **Origin at bore axis ∩ plane** (B:24).
   - Evidence: consistent with Dreame, which found the bore axis by circle fits on Z sections with centre spread < 0.01 mm (DB/README.md:21; DB/report/source/align.py:72-82). Note that align.py:82 silently falls back to the bbox centre when no bore is found, which B:95 forbids for axes.
   - Effect: **agrees**, with a caveat.
4. **Rounding to 0.1/0.5/1.0 steps** (B:52, F:55).
   - Evidence: Dreame kept values such as Ø23.73, A/F 3.28, 4.77° and R2.75, with rounding "only within scan noise (≈0.02–0.05 mm)" (DB/README.md:23, :36, :47-48, :81). OD-H12 kept Ø47.30 and A/F 11.6 (OD/README.md:36, :49).
   - Effect: **contradicts** fixed steps. Snap tolerance tracks measured noise.
5. **Snap near-concentric to concentric** (B:53).
   - Evidence: OD-H12 left the coil 0.2 mm off-axis, "measured, not snapped" (OD/README.md:51). Dreame *did* force three identical legs and a common PCD despite 0.1 mm spreads, and declared them as assumptions (DB/README.md:82-83).
   - Effect: **refines**. Snap or keep is a judgement that must be logged either way.
6. **Patterns need equal pitch; model one + PolarLocations** (B:70).
   - Evidence: Dreame legs sit at 60°/150°/−60°, "NOT equally spaced, measured" (DB/README.md:50), and cups at four unequal θ (DB/report/snap_params.json:40-45). The project used one profile placed at measured angles.
   - Effect: **refines**. "One instance, many placements" holds; "equal pitch" does not.
7. **Tri-axis extrude-intersect as the prismatic strategy** (B:68).
   - Evidence: not observed in the spot-checked build scripts. Dreame intersects a pentagon prism with a cylinder and a tapered frustum (DB/report/source/build_screw.py:28-31, :49). OD-H12 uses revolve + extrudes (OD/report/src/build_pump.py:80-126). M02 uses sketch → extrude → pattern (M02/DESIGN_NOTES.md:9-16).
   - Effect: **not supported** as a default by these three projects.
8. **Fillets LAST** (B:71, F:71).
   - Evidence: Dreame applies local fillets right after their parent feature, each wrapped in try/except with a log line (DB/report/source/build_screw.py:44-48, :57-59; DB/report/screw_build_log.txt). Only the global edge fillets come last (F11, build_screw.py:96).
   - Effect: **refines**.
9. **Gate on the original, undecimated mesh** (B:75).
   - Evidence: Dreame used the full-resolution raw scan (1.8 M / 4.9 M triangles) (DB/README.md:25). The golden README also says official gates must re-run on the original scan, not the decimated copy (golden-examples/README.md, "What was left out").
   - Effect: **agrees**.
10. **Gate estimator** (B:79-80).
    - Evidence: both golden gates use KD-tree candidates plus exact point-triangle distance on k nearest triangles, with fixed seeds (DB/report/source/fastgate.py:6-22; OD/report/src/gate.py:8-17). Dreame also ran a separate official 50k/50k gate that matched the fast gate (DB/README.md:68; DB/report/screw_official_gate.json).
    - Effect: **refines**. Keep the method, add seeds and density.
11. **"Blocking" consumer band p95 ≤ 0.3 / max ≤ 0.8** (B:87).
    - Dreame snap cap: the official gate reports `overall_pass: false`, with max 1.226 (DB/report/snap_official_gate.json:10, :24). It was delivered with named artefact masks (4.9% of points) and a masked p95 of 0.116 (DB/README.md:64-76; DB/report/snap_masked_gate.json:9-16).
    - OD-H12: p95 0.448 / max 2.49, band "NOT MET". It was delivered with a per-region explanation (OD/README.md:25, :32-44), and golden-examples/README.md records the operator's view as "good result".
    - Effect: **contradicts** "blocking". The actual practice was an honest verdict plus region attribution, which matches RS:181-183, not the skills.
12. **CAD→scan raw stats** (B:80-85).
    - Evidence: OD-H12 raw CAD→scan p95 was 3.43. The observable-only value was 0.567 after a 60° ray-cone visibility test (OD/README.md:26-27, :40-41; OD/report/src/gate.py:57-84).
    - Effect: **refines**. Unmasked CAD→scan is meaningless for parts with occluded regions.
13. **Deviation gate as the success criterion** (B:8).
    - Evidence: M02 has **no scan deviation gate**. Operator measurements govern (M02/OPERATOR_SPEC.json; M02/DESIGN_NOTES.md:5), and QA re-measures the exact STEP for counts, ODs, widths, bore and twist (M02/VERDICT.md:8-19, :24-28). The scan-derived 27-tooth / 21.75 mm candidate was invalidated by operator data (M02/DESIGN_NOTES.md:5).
    - Effect: **contradicts**. When authoritative measurements exist they outrank scan fit, and a scan-inferred count can be wrong.
14. **Validity checks** (F:73 only).
    - Evidence: all three goldens check single-solid / closed / valid after STEP re-import (DB/README.md:17; OD/README.md:18 and OD/report/export_check.json; M02/model.py:88-101, M02/VERDICT.md:10-14).
    - Effect: **refines**. The check should be mandatory in both skills.
15. **Hidden geometry.**
    - Evidence: the baseline is silent. OD-H12 invents an unscanned core tube and depths and declares them (OD/README.md:54, :65-66). M02 explicitly invents nothing unmeasured (M02/README.md:27).
    - Effect: a **gap**; the evidence differs by project, and a new rule must make the choice explicit.
16. **Validator ≠ independent evidence.**
    - Evidence: OD-H12 notes that its 13/13 validator pass uses scan-derived expected values and is only a consistency check (OD/README.md:70-71; OD/report/expected.json).
    - Effect: **refines** B:8. An expected-value check built from the same scan is not an independent gate.

---

## 7. Reusable code in the baseline

The two baseline skills ship **no scripts**, only inline snippets. What is worth keeping:

| Snippet | Where | Keep? | Determinism / correctness concerns |
|---|---|---|---|
| Unit-scale heuristic | B:17, F:21 | As a check, not an auto-fix | Domain-specific range ("vacuum housing"). Needs a caliper or photo cross-check (RS:106-107). |
| Facet-based plane seed + `align_vectors` | B:27-32 | `align_vectors` + translate yes; facet seed no | Facet seed is unreliable on scans (§6.1). `align_vectors` leaves the in-plane rotation arbitrary, so clocking must follow. |
| Normals-based revolve axis | B:39, F:41 (prose) | Yes, **with the corrected eigen formula** | Wrong eigenvector as written (§5.1). Lift the correct form from DB/report/source/datum.py:48-61. Note that line 60 there is a no-op (`* 0`). |
| `section_multiplane` stack | B:44-46 | Yes | Deterministic. Loop order within a plane must be matched by centroid (the F:95 trap applies to trimesh too). |
| `crossSections` | F:47-51 | FreeCAD appendix only | Tolerance 0.0001 is unexplained. |
| Two-way gate | B:77-85 | Replace | `rebuilt.sample(20000)` is unseeded (B:80). Scan→CAD uses all vertices with no subsample cap (B:79). Frame bug (§5.2). `part.part.export_stl` differs from the golden `export_stl(shape, path, tolerance=…)` call (DB/report/source/frames.py:19), and no tessellation tolerance is set, so the result depends on defaults. |
| FreeCAD gate | F:79-86 | Pattern only | Seeded (`default_rng(0)`, F:84). The KD-tree is vertex-to-vertex, not a surface distance (§5.4). `LinearDeflection=0.05` is coarse against a 0.15 mm band. |
| `BSplineCurve.approximate` | F:57-58 | Appendix | Deterministic. Tolerance 0.05 has no stated source. |

Better code for the same jobs exists in the goldens. Other agents are doing the full extraction, so these are pointers only: seeded RANSAC + SVD (DB/report/source/datum.py:7-25), normal-cluster plane finder (datum.py:27-46), Kåsa circle fit (DB/report/source/align.py:11-19), dual-frame STEP export (DB/report/source/frames.py), seeded KD + exact-triangle gate (DB/report/source/fastgate.py:6-22, OD/report/src/gate.py:8-17) and ray-cone observability (OD/report/src/gate.py:57-84).

Determinism note on the ray-cone code: its perpendicular basis uses `np.cross(nrm, [0.3,0.5,0.8])`, which degenerates when a normal is parallel to that vector (OD/report/src/gate.py:66). It is seeded (`default_rng(5)`, gate.py:62).

Outside this group, `baseline/oomwoo-re-pipeline/tools/render_views.py` (604 lines) is the only real baseline tool. RS:272 and baseline/oomwoo-re-pipeline/CHANGES_V3.md:37 describe it; its owner should audit it.

---

## 8. FreeCAD: what belongs in a short `references/` appendix

The build123d toolchain is what the goldens actually used (DB/README.md:3; OD/README.md:5; M02/model.py:14), and RS:26-27 records the bake-off as closed. No golden project in this spot check used FreeCAD. FreeCAD should therefore not have its own skill. At most it gets a ≤1-page `references/freecad-equivalents.md` with:

1. **Invocation facts:** run headless via `freecadcmd script.py`. The bundled Python does not see system pip packages. numpy ships with it, scipy usually does, matplotlib often does not. Split geometry and plotting, and exchange data as `.npy`/`.csv` (F:8, F:94). Record the FreeCAD version (F:8 assumes 1.1; F:23 flags an unverified `decimate` signature).
2. **API map** (trimesh/build123d → FreeCAD), each entry unverified here:
   - `section_multiplane` → `Mesh.crossSections(planes, tol)`. Loop order is arbitrary (F:47-51, F:95).
   - Planar segmentation → `getPlanarSegments(tol)` (F:40).
   - Profile face → `Part.Wire`/`Part.Face`/`extrude`/`revolve`/`common`/`fuse`/`cut` (F:63-68).
   - Fillets → `makeFillet` (F:71).
   - Validity → `check()`/`isValid()`/`removeSplitter()` (F:73).
   - Exact point-to-B-rep distance → `distToShape`, which is slow (~2k points) (F:85, F:96).
   - Export → `exportStep` (F:91).
3. **Fallbacks unique to FreeCAD, each flagged:** `Reen.approxSurface` for freeform patches (F:72). `Part.makeShapeFromMesh` produces a tessellated STEP, which RS:260-270 forbids as a deliverable. It belongs only as a "never ship this" warning (F:98).
4. **Do not carry over:** the bake-off protocol (F:101-102; superseded by RS:26-27), the wrong eigen formula (F:41), the vertex-to-vertex gate (F:82), the default mesh repair (F:17-18) and the "local-toolchain memory" pointer (F:8).
