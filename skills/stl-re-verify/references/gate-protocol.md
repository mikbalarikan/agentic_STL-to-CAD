# Gate protocol: regimes, order, inputs, and what each gate does not check

Every number here comes from `analysis/SYNTHESIS.md` §4 or a golden record, with its source.
Numbers marked "parameter" are the values a golden used. They are not thresholds.

## 1. Band regimes (declared at intake, named in the verdict)

The regime is chosen at intake (`INTAKE_CARD.md` / `DECISIONS.md` REGIME entry), written to
`intake/regime.json` (run-contract §12), and copied verbatim into `qa/regime.json` (e.g. `cp
intake/regime.json qa/regime.json`) — never edited. QA never picks one (QUESTIONS.md Q1,
run-contract.md §9, §12). If `intake/regime.json` is missing, stop and ask the human. Do not fall
back to a default.

| Regime | Tier-1 (caliper) | Tier-2 whole part | Named functional interfaces | Source | Golden use |
|---|---|---|---|---|---|
| `RE_SPEC` | \|CAD − caliper\| ≤ 0.15 mm per dim | p95 ≤ 1.6 / max ≤ 4.0 mm after independent ICP + skin mask | max ≤ 0.8 mm (interfaces not covered by calipers) | `baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175` | OOM-B02, OOM-P03 |
| `baseline-skill` plastic | none stated | p95 ≤ 0.30 / max ≤ 0.80 mm | none stated | `baseline/skills/stl2step-build123d/SKILL.md:87` (no source given there) | dreame caps, OD-H12 |
| `baseline-skill` machined | none stated | p95 ≤ 0.15 / max ≤ 0.50 mm | none stated | same line | none |
| `project-spec` | from the spec | from the spec | from the spec | the spec path:line | M02 (operator spec, ±0.03 / ±0.02, origin not recorded) |

Under RE_SPEC, interior/occluded zones are **reported, not gated** (`RE_SPEC.md:176`).

**What the baseline-skill band applies to** (run-contract §12): p95 and max apply to scan→CAD and
to the *observable* part of CAD→scan. Raw CAD→scan is reported, not gated. Evidence: the DRM
official gate applied the limits in both directions
(`golden-examples/dreame_brush-caps/report/screw_official_gate.json#limits`), and OD showed that
raw CAD→scan counts surfaces no scanner can see
(`golden-examples/OD-H12_delonghi-dedica-pump/report/deviation_gate.json`).

**Registration under every regime** (run-contract §12): Verify always runs its own ICP
(independence, `RE_SPEC.md:173`), including under `baseline-skill`, and reports numbers both in
the builder's datum frame and after ICP. The gate is evaluated after ICP. A large gap between the
two is a datum finding.

`qa/regime.json` format (read by `deviation_gate.py`, `sim_caliper.py`, `verdict.py`):

```json
{"name": "RE_SPEC", "source": "baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175",
 "declared_in": "intake/INTAKE_CARD.md §<n>",
 "bands": {"tier1_abs": 0.15, "p95": 1.6, "max": 4.0, "interface_max": 0.8},
 "gated": ["cad_to_scan:masked", "scan_to_cad:masked"]}
```

The optional `gated` key names the statistics that must meet the whole-part band. Without it,
`verdict.py` gates scan→CAD (masked) and CAD→scan (observable subset if the split ran, else masked).
Every `functional_interface` zone is always gated against `interface_max`.
- B02 gated CAD→scan outer skin (`q20_tier2.py:160-166`).
- OD and DRM compared both directions to the band (`analysis/golden/OD-H12.md` §7, `dreame_brush-caps.md` §7).

### Report-only numbers (never blocking)

- **Datum audit**: ≤ 0.3° / ≤ 0.15 mm (`RE_SPEC.md:241`). This is report-only
  (QUESTIONS.md Q2). Both approved OOM goldens exceeded it: B02 0.429° / 0.451 mm, P03
  0.154° / 0.600 mm (`analysis/golden/OOM-B02.md` §3, `OOM-P03.md` §3).
- **Face count / surface census**: reported, not gated (QUESTIONS.md Q3). The only numeric form
  is the W01 tracker cell (≤ ~600 faces, ≥ 60 % analytic area,
  `baseline/oomwoo-re-pipeline/TRACKER.md:32`). You may quote it for context. Never gate on it.

## 2. Gate order

| # | Gate | Script | Blocks the official grade when |
|---|---|---|---|
| 0 | Hash freeze (heuristic, n=1: M02) | `step_check.py freeze` … `verify` at the end | the hash changes during QA |
| 1 | Datum audit (report-only) | `datum_audit.py` | never |
| 2 | Validity: single valid closed solid, re-import, naked edges, tessellation | `step_check.py check` | it fails. This is a band fail, not a blocker. |
| 3 | Surface census (reported) | `step_check.py check` | never |
| 4 | Tier-1 re-measure on the STEP | `sim_caliper.py` | any gated \|Δ\| is over the band |
| 5 | Independent registration | `tier2_icp.py` | converged = false |
| 6 | Two-way deviation, zones, masks, sensitivity, observability, clusters | `deviation_gate.py` | the scan is decimated, or a band fails |
| 7 | Overlays with per-panel scan count | `overlay.py` | a panel has no scan trace (finding) |
| 8 | Photo plausibility, CHK-CIRCULAR, CHK-LIKE4LIKE, CHK-ENUM, CHK-FILLET, CHK-PATCHWORK, CHK-INDEP | agent → `qa/review.json` | a check is not run |
| 9 | Verdict | `verdict.py assemble` + `render` | the proposed verdict is not allowed by the evidence |

### Datum audit spec (`datum_audit.py --spec`)

Write the spec from the datum description in `INTAKE_CARD.md` and `alignment.json`
(`primary.mesh_region_desc` and so on). Never write it from the builder's code. Regions are
predicates in the builder's datum frame. They are used **only to select faces**; all fits use
the raw scan.

```json
{"primary":  {"type": "plane", "method": "vote|region", "cone_deg": 3.0, "band_mm": 0.30, "region": {...}},
 "level":    {"region": {...}},                        // axis-primary parts: plane that sets z = 0
 "position": {"type": "circle|axis_line|none", "region": {...}, "wall": "inner|outer|any"},
 "clock":    {"type": "fourier|plane_normal|none", "order": 3, "region": {"r": [20, 34]}}}
```

- Axis-primary parts: `"primary": {"type": "axis", "region": <cylindrical faces>}`. The axis is
  the smallest eigenvector of Σ a·nnᵀ (corrected form, SYNTHESIS §3).
- The B02 values (3° cone, 0.30 mm band, Cauchy scale 0.30, 6000 vote directions, 60k compare
  points) are parameters from `q03_datum_full.py`.

### Predicate language (zones, masks, datum regions)

Keys are AND-ed:
- `x y z r abs_x abs_y abs_z nx ny nz abs_nz d`: each takes `[lo, hi)`; `null` means unbounded.
- `theta_deg`: `[a, b]`, counter-clockwise, and may wrap through 360.
- `any_of`: a list of predicates (OR).
- `not`: a predicate.
- `all`: `true`.

All coordinates are in the datum frame. Example: DRM `flat_corner_skirt (x>8.3 & |y|>5.5 & z<-1.45)`
→ `{"x": [8.3, null], "abs_y": [5.5, null], "z": [null, -1.45]}`.

## 3. Deviation gate method (defaults = OD golden, reproduced bit-exact)

- **Distance.** Take `n_samp` seeded surface samples of the target and build a KD-tree. Find the
  k nearest samples and compute the exact point-to-triangle distance to each candidate triangle;
  keep the minimum (`OD gate.py:8-17`). This can only over-estimate.
- **Parameters** (OD): k = 8, n_samp = 3,000,000, seed 0.
  - scan→CAD uses every scan vertex.
  - CAD→scan uses 300,000 CAD samples, seed 2.
- **DRM variant.** DRM added target vertices as candidates (`--vertex-candidates`) and used a
  600k scan subsample, k = 6 (`fastgate.py`). Record which variant was run.
- **Stats.** n, rms, mean, p50, p95, p99, max, with the sampling and seeds (SYNTHESIS E3;
  facet-film T14).
- **Full-res only for grades.** Decimated scans are inspection only. The decimated copies deviate
  ≤ 0.028 mm from the originals (`golden-examples/README.md`). Even so, "official deviation gates
  must re-run against the original full-resolution scan". The script labels a decimated run
  `INSPECTION ONLY` and sets `gate_valid: false`.
- **Registration.** The RE_SPEC regime requires independent ICP (`RE_SPEC.md:174`). If ICP does
  not converge, the gate is invalid (`re-qa-verifier.md:37-38`; the W01 ICP hit its 50-iteration
  cap, per `analysis/baseline/oomwoo-re-pipeline.md` §5).
  - Golden ICP parameters (B02 `q20_tier2.py`): 3M scan samples seed 11, 300k CAD samples
    seed 13, normal agreement cos 70°, 0.8 mm off open boundaries, correspondences < 3.0 mm,
    cap 60, stop at step < 1e-6.
  - You may raise the cap once. Record both runs.
  - Axisymmetric parts converge slowly: they slide about their axis. Inspection example: the DRM
    screw decimated did not converge in 60 iterations and converged in 109 (see
    `verdict-template.md` §Worked numbers).
- **Observability.** (heuristic, n=1: OD; B02 used the open-boundary mask for the same purpose.)
  - Method: CAD points with CAD→scan distance > 0.5 mm are ray-tested. One ray goes along the
    normal and 6 more sit on a 60° cone, all starting 0.05 mm off the surface. The point is
    "unobservable" if every ray hits the CAD again. The test runs on a 20k subsample with seed 5.
  - These are OD parameters, not thresholds.
  - The ray range is unbounded, as in the golden. The "60 mm" in the OD comment was never
    enforced. `--obs-max-range-mm` makes a range explicit.
- **Over-band clusters.**
  - Points over the max band (default: the regime max; 0.8 if the regime has none) are grouped
    by a KD radius graph: eps 1.0 mm, ≥ 20 points (parameters; 20 is the DRM fastgate bin floor).
  - A scan→CAD cluster means scan material the CAD lacks. That is either a missing feature
    (P03 stem: 4907 points at r < 6.4) or an artefact (DRM flap).
  - A CAD→scan cluster means CAD material with no scan behind it: either invented or
    unobservable.

## 4. What each gate does NOT check (declare these; facet-film T11)

| Gate | Blind to |
|---|---|
| Validity | Wrong feature boundaries or extents. A well-formed solid can be the wrong part (T11). |
| Surface census | Whether the analytic faces are the *right* ones. It only catches re-tiled / faceted skin (W01, M02 2354 planar facets). |
| Tier-1 | Every dimension that was not calipered. B02 gated 5 of 24; the other 17 are ABSENT, not passed. |
| Tier-1 on a lobed OD | Jaw placement. A two-jaw caliper reads R(θ)+R(θ+180), and some readings are unachievable (B02 F06 Δ +0.647, CHK-ACHIEVABLE). |
| Scan deviation | Patchwork. W01 attempt 1 sat on the scan and was garbage CAD. It is also blind to occluded interiors, to dimensions the scanner cannot resolve (noise floor), and to soft features. |
| Scan→CAD only | Invented CAD material. Run CAD→scan too (SYNTHESIS E1; P03 ran one-way). |
| CAD→scan only | Missing features. Run scan→CAD too (W01 lesson; P03 stem). |
| Masked numbers | Anything inside the mask. Always show unmasked numbers and sensitivity next to them (CHK-MASK). |
| ICP-registered numbers | A datum error the ICP absorbed. Report `delta_deg` / `delta_mm` and the datum audit. |
| Observability split | Surfaces a scanner could see but that the scan still missed (low coverage). It is a CAD-only line-of-sight test. |
| Overlays | Everything between the panels. A panel with no scan proves nothing (CHK-OVERLAY). |
| A project validator with scan-derived expected values | Anything. It is a consistency check (OD 13/13, CHK-CIRCULAR). |
| Decimated-scan runs | Nothing is graded. They are inspection only. |
