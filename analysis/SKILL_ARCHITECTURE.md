# SKILL ARCHITECTURE — proposal for approval (Phase 2)

Evidence base: `analysis/SYNTHESIS.md` (rows cited as `SYN A1`, `SYN CHK-…`). Nothing
here is drafted yet; Phase 3 starts only after approval.

## 1. Shape: 1 orchestrator + 5 stage skills

```
stl-re-orchestrate  (state machine, verdict states, iteration bound, run-folder contract)
   │
   ├─ 1 stl-re-intake-datum      scan → INTAKE_CARD + MEASUREMENTS request + alignment.json
   ├─ 2 stl-re-measure-intent    aligned scan (+calipers/photos) → params.json + PARAM_TABLE.md
   ├─ 3 stl-re-rebuild-build123d plan + params → model.py → STEP (datum + scan frame) + export_check
   ├─ 4 stl-re-verify            frozen STEP + raw scan → gate.json + VERDICT.md   (independent)
   └─ 5 stl-re-deliver           verdict + artefacts → README.md + MANIFEST.json + claim boundary
```

**Why this split** (evidence, not taste):
- Verification must be a separate skill that another agent can run cold with its own
  code. Self-verification caused both circularity failures (P03 datum refined to its own
  CAD; OD validator with scan-derived expectations) and the undeclared-independence
  finding (B02 A13) (`SYN CHK-CIRCULAR`, `SYN E16`).
- Measurement/intent is split from the rebuild. Every golden REVISE and wrong candidate
  started in measurement or attribution, not in CAD code: B02 F06 attribution, P03
  stem dismissed as occlusion, M02 wrong 27T count (`SYN CHK-ACHIEVABLE`,
  `CHK-CLUSTER`, `CHK-COUNT`).
- Intake and datum stay together. The datum plan comes out of the intake reading
  (functional surfaces, axis-primary or not), and both run before any measurement
  (`SYN B1–B2`, RE_SPEC §3.1 order of operations).
- Delivery is separate from verify. The verifier must not author the report, the
  report reads numbers from the gate JSON (`SYN CHK-NUMBERS`), and nothing is
  published before the verdict (`SYN CHK-PUBLISH`).

**Naming:** new `stl-re-*` names, deliberately different from the baseline's
`stl2step-*`. A stale same-named copy in `~/.claude/skills` would otherwise shadow the
new skill. That exact failure is recorded in `RE_SPEC.md:372-373` (stale v2 verifier
shadowing v4).

## 2. Per-skill specification

For each skill: trigger description (the frontmatter draft), boundary, inputs → outputs,
SKILL.md vs `references/` vs `scripts/`.

### 2.0 `stl-re-orchestrate`

- **Description (draft):** "Orchestrates reverse-engineering a scanned STL mesh into
  design-intent parametric CAD (STEP) with build123d. Use when asked to turn a scan,
  STL or mesh into a STEP/CAD model, remodel a part from a 3D scan, or resume or
  re-run such a job. Runs the stages intake → measure → rebuild → verify → deliver
  with bounded iterations and honest verdicts."
- **Owns:**
  - the run-folder contract (§3)
  - the stage state machine with entry/exit criteria
  - the verdict vocabulary (§4)
  - the iteration bound: 3 loops per part (`RE_SPEC.md:248-250`; B02, P03 used 2/3)
  - the HALT/ask rules: missing calipers, unsupported part class, band miss
  - the independence rule (verify runs in a fresh agent/context; if it can't, declare it)
  - CHK-PUBLISH and CHK-INDEP
- **Does not own:** any geometry math.
- **Layout:**
  - SKILL.md (~200 lines): the state machine, verdicts, HALT table, hand-off artefacts.
  - `references/run-contract.md`: folder layout and JSON schemas.
  - `references/verdict-examples.md`: the six golden outcomes from `SYN §0.1`, as worked
    verdict examples, including the snap-cap fail and the OD miss.
  - No scripts beyond `scripts/init_run.py`, which creates the folder and hashes the inputs.

### 2.1 `stl-re-intake-datum`

- **Description (draft):** "Intake and datum alignment for STL→CAD reverse
  engineering: scan health, units/scale check, noise floor, fragment/table removal,
  feature enumeration from mesh and photos, measurement request, and a named 3-2-1
  datum frame with fit residuals written to alignment.json. Use at the start of any
  scan-to-STEP job, or when a datum must be redone."
- **Steps:**
  1. Intake stats and hash (`SYN A1`).
  2. Decimated working copy with provenance (`A2`).
  3. Largest body, table removal, weld, normals (`A4–A5`).
  4. CHK-SCALE (`A6`).
  5. Noise floor on a clean primitive (`A7`).
  6. Occlusion/coverage map (`A9`).
  7. Feature enumeration from mesh + profile photos, with CHK-ENUM (`A8`).
  8. Measurement request with scan-predicted values per requested dim. This is the
     early catch for CHK-ACHIEVABLE (`RE_SPEC.md:197-202`).
  9. Datum: DOF ladder, functional/axis primary, RANSAC+SVD plane, robust circle/axis
     fits, clock rule, CHK-TILT, sanity landmarks (`B1–B7`, `B11`).
- **Layout:**
  - `scripts/intake.py`: stats, components, decimation.
  - `scripts/datum_fit.py`: seeded RANSAC plane, offset-histogram plane finder, Kåsa +
    IRLS circle, axis from normals (corrected eigen form).
  - `scripts/align.py`: builds T and writes alignment.json.
  - `references/`:
    - `intake-card-template.md` (from the baseline template, re-mesh-analyst naming removed)
    - `measurements-template.md` (adds the photo-transcribed and scan-authority statuses seen in the goldens)
    - `datum-cookbook.md` (plane-primary vs axis-primary examples from DRM/B02/P03/OD)
- **Hand-off:**
  - `intake/INTAKE_CARD.md`
  - `intake/intake.json`
  - `intake/MEASUREMENTS.md`
  - `intake/alignment.json` (schema §3.2)
  - aligned working mesh

### 2.2 `stl-re-measure-intent`

- **Description (draft):** "Measure an aligned scan and extract design intent:
  planar and radial sections, primitive fits, angular profiles, pattern counts by
  rotational order, caliper and photo authority, and noise-aware rounding. Produces a
  parameter table where every value has measured→chosen, rule and source. Use after
  datum alignment and before CAD modelling, or to re-measure a feature a gate flagged."
- **Steps:**
  1. Sections along Z and radial half-planes (`C1`).
  2. (r,z) / (θ,r) maps and R(θ) (`C2`).
  3. Counts by FFT or rotational-order residual at ≥3 stations, with CHK-COUNT (`C3`).
  4. Authority hierarchy (`C4`) and photo-transcribed readings (`C5`).
  5. CHK-ACHIEVABLE, a simulated two-jaw window on the scan (`C6`).
  6. Rounding within noise, with no fixed step (`C8`).
  7. Keep uncalipered critical interfaces unsnapped (`C9`).
  8. Symmetry only within noise (`C10`).
  9. Provenance tags for unscanned geometry (`C11`).
  10. CHK-CLUSTER (`C12`) and CHK-FRAME (`B10`).
  11. Declare simplifications (`C14`).
- **Layout:**
  - `scripts/sections.py`: planar + half-plane sections, loop matching by centroid.
  - `scripts/fits.py`: circle/line/plane fits with residuals.
  - `scripts/pattern_count.py`: FFT / rotational-order residual. **Written new**, from
    the method recorded in the M02 qa_report and P03 PARAM_TABLE. No golden code
    exists; the provenance header will say so.
  - `scripts/sim_caliper.py`: two-jaw support function, lifted from B02 `q10::jaws`.
    Shared with verify.
  - `references/param-table-schema.md`
  - `references/intent-rules.md`: when to snap, keep or declare, with golden examples.
  - `references/gears.md`: heuristic, n=1 M02.
- **Hand-off:** `measure/params.json` and `measure/PARAM_TABLE.md` (schema §3.3).

### 2.3 `stl-re-rebuild-build123d`

- **Description (draft):** "Build a clean parametric build123d model from a
  measured parameter table: written feature plan with expected op and face counts,
  revolve-profile and sub-body strategies, one-instance patterns, logged fillets,
  anti-patchwork rules, single-solid validity, STEP re-import and dual-frame export.
  Use when the parameters are ready and the CAD must be (re)built."
- **Steps:**
  1. Write the plan (`D1`).
  2. Strategy catalogue: revolve (r,z) profiles, sub-body union, one instance +
     placements, cut tools (`D2–D6`).
  3. Fillets via try/log/fallback with the radius recorded, CHK-FILLET (`D7–D8`).
  4. Loft policy (`D15`).
  5. CHK-PATCHWORK self-check (`D10`).
  6. Validity + re-import + abort (`D12`).
  7. Dual-frame export (`D14`).
  8. Superseded iteration kept (`F4`).
- **Layout:**
  - `scripts/export_frames.py`: from DRM `frames.py` + OD `export_final.py`,
    re-orthonormalised inverse.
  - `scripts/validate_step.py`: from M02 `model.py` self-check and B02 `q01`/`q10` QA-1.
  - `scripts/fillet_log.py`: from the DRM/B02 patterns.
  - `scripts/face_stats.py`: surface-type census for CHK-PATCHWORK.
  - `references/build123d-idioms.md`: hex AF→circumradius, polar sector, revolve from a
    param dict, hull + offset pocket, tangent-boolean offset (heuristic).
  - `references/strategy-catalogue.md`: worked golden feature trees.
  - `references/freecad-equivalents.md`: one page, per `analysis/baseline/stl2step-skills.md` §8.
- **Hand-off:**
  - `build/MODELING_PLAN.md`
  - `build/model.py`
  - `build/build_log.txt`
  - `build/<part>_datum.step`
  - `build/<part>.step` (scan frame)
  - `build/export_check.json`

### 2.4 `stl-re-verify`

- **Description (draft):** "Independently verify a reverse-engineered STEP
  against its scan and measurements: hash freeze, datum audit, validity,
  surface-quality census, caliper re-measure on the STEP, two-way scan deviation with
  independent registration, named masks with sensitivity, observability split,
  per-zone buckets and overlays, then a verdict. Use after a rebuild, before any
  delivery, ideally in a fresh agent that did not build the model."
- **Steps:**
  1. Hash freeze (heuristic M02).
  2. Datum audit (`B8`; threshold Q2).
  3. Validity (`D12`).
  4. CHK-PATCHWORK (`D10`; threshold Q3).
  5. Tier-1 simulated caliper / analytic query (`E8`).
  6. Tier-2 two-way deviation with exact KD-candidate distance and seeded sampling
     (`E1–E3`).
  7. Independent ICP with convergence reported (`E7`).
  8. Zones (`E4`).
  9. Masks with fraction and sensitivity, CHK-MASK (`E5`).
  10. Observability split (`E6`).
  11. Over-band point localisation (`E14`).
  12. Overlays, CHK-OVERLAY (`E12`).
  13. Photo plausibility (`E15`).
  14. CHK-CIRCULAR and CHK-LIKE4LIKE.
  15. Verdict (§4).
- **Layout:**
  - `scripts/deviation_gate.py`: from DRM `fastgate.py:dist_to_mesh` + OD `gate.py`
    stats/regions.
  - `scripts/observability.py`: from OD `gate.py:57-84`, with the degenerate
    helper-vector fixed.
  - `scripts/tier2_icp.py`: from B02 `q20_tier2.py`, generalised.
  - `scripts/datum_audit.py`: from B02 `q03_datum_full.py`, generalised.
  - `scripts/sim_caliper.py` (shared).
  - `scripts/overlay.py`: from DRM `overlay.py` / OD `ovl.py`.
  - `references/gate-protocol.md`: bands with sources, band-selection rule (Q1).
  - `references/mask-policy.md`
  - `references/verdict-template.md`
- **Hand-off:** `qa/gate.json`, `qa/VERDICT.md`, `qa/overlays/*.png`.

### 2.5 `stl-re-deliver`

- **Description (draft):** "Package a verified STL→CAD result: README with
  method, parameter table with sources, gate tables read from gate.json, declared
  limitations with re-run triggers, claim boundary, both coordinate frames, manifest
  with hashes and a reproducibility re-run. Use only after stl-re-verify has written a
  verdict."
- **Steps:**
  1. Refuse without a verdict (CHK-PUBLISH).
  2. Numbers from JSON only (CHK-NUMBERS).
  3. Limitations and re-run triggers (`F10`).
  4. Claim boundary (`F7`).
  5. Reproducibility re-run in a fresh process (heuristic M02 + facet-film T32).
  6. MANIFEST with sha256 (`A1`).
- **Layout:**
  - `scripts/make_manifest.py`
  - `scripts/repro_check.py`
  - `references/readme-template.md`: modelled on the OD/DRM README structure and the
    B02 limitation wording.

## 3. Run-folder contract (hand-offs)

```
<run>/
  input/            scan.stl (never modified), photos/, MEASUREMENTS.md (filled), INPUT_HASHES.json
  intake/           INTAKE_CARD.md, intake.json, MEASUREMENTS.md (request), alignment.json, work mesh
  measure/          params.json, PARAM_TABLE.md, figures/
  build/            MODELING_PLAN.md, model.py, build_log.txt, <part>_datum.step, <part>.step, export_check.json
  qa/               gate.json, VERDICT.md, overlays/, masks.json
  deliver/          README.md, MANIFEST.json, repro.json      (written only after a verdict exists)
  _itN_SUPERSEDED/  previous iteration, moved intact             (CHK-SUPERSEDED)
```

### 3.1 JSON rules

- Every JSON carries `schema`, `tool_version`, `inputs: {path: sha256}` and `seed`.
- JSON contains no wall-clock values other than a provenance timestamp field. The
  determinism rule for shipped scripts is kept.

### 3.2 alignment.json

Keys: RE_SPEC schema v2 (`RE_SPEC.md:143-157`) plus the fields the goldens needed:
- `clock_rule`
- `tilt_deg` (measured)
- `noise_floor` (method + value)
- `sanity_landmarks`

### 3.3 params.json

Each entry holds:
- `value`
- `measured`
- `rule`
- `source` ∈ {caliper, caliper-photo, operator-spec, scan, photo-inferred, standard, assumed}
- `estimator`
- `uncertainty`

## 4. Verdict vocabulary

| Verdict | Meaning | Golden precedent |
|---|---|---|
| `APPROVED` | Every gate in the declared band set passes; no mask-dependent passes | DRM screw; M02 (spec regime) |
| `APPROVED_WITH_LIMITATIONS` | Gates pass, but declared limitations exist, each with a re-run trigger | B02 (3 limitations, masked hex); P03 (photo-inferred socket) |
| `BAND_NOT_MET` | One or more bands missed. Explained per region with options. **Delivery needs an explicit human acceptance, which is recorded.** | OD (p95 0.448); DRM snap (max 1.226) |
| `REVISE` | Fixable in geometry or measurement; loop back (count toward 3) | P03 it1; B02 it1 |
| `HALT` | 3 loops used, unsupported part class, or a blocker only a human can clear | RE_SPEC breakers |

## 5. Band selection (pending Q1)

The verify skill will not hard-code one band set. The intake declares the regime in
`INTAKE_CARD.md`, and the verdict states which regime was applied:
- **RE_SPEC regime** (when calipers exist): Tier-1 ±0.15, Tier-2 p95 ≤1.6 / max ≤4.0,
  interfaces ≤0.8.
- **Baseline-skill regime** (scan-only or user-chosen): p95 ≤0.30 / max ≤0.80 plastic,
  ≤0.15 / ≤0.50 machined.
- **Project spec**, with its source path.

The skill says which regime each golden used, and does not invent a new one. Q1 asks
you to confirm this or pick a single default.

## 6. Phase 3–4 plan implied by this architecture

- **Phase 3:** 6 Opus authors in parallel, one per skill. Each gets SYNTHESIS, the
  relevant golden extractions and this file. Scripts are lifted with provenance headers
  and made deterministic and typed.
- **Phase 4 reviews:** 6 independent Opus reviewers, plus Haiku lint and a Sonnet fixer.
- **Phase 4 blind replay:** 2 Opus, new skills vs baseline. **Change from the prompt:**
  the M02 scan is not in the repo (`analysis/golden/M02-02-03.md` Q1), so M02 can't be
  replayed. Proposed targets:
  - **OOM-B02**: full-resolution scan, photos and MEASUREMENTS in repo.
  - **DRM screw cap**: decimated scan, labelled inspection-only.
  build123d 0.13.0 installs in this environment (checked), so the replay goes as far as
  a STEP plus a deviation gate on the available scan.
- **Budget:** 8 (Phase 1) + 6 + 6 + 3 + 2 + ~2 ≈ 27 agents, slightly over the ~25
  guide. To stay under it, merge `stl-re-deliver` into the orchestrator
  (5 skills → 23 agents).
