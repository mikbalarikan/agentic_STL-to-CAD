---
name: stl-re-rebuild-build123d
description: Build a clean parametric build123d model and STEP from a measured parameter table in a scan-to-CAD job. Covers the written modeling plan, revolve/sub-body/pattern/cut-tool strategies, logged fillets, the anti-patchwork census, single-solid validation and datum- plus scan-frame export. Use once measure/params.json exists, or when a verdict sends the CAD back for a rebuild.
---

# stl-re-rebuild-build123d

Stage 3 of the `stl-re-*` pipeline (`../stl-re-orchestrate/SKILL.md`). The input is a frozen
datum and a parameter table. The output is a design-intent B-rep: one valid closed solid,
exported in two frames. The binding hand-off contract is
`../stl-re-orchestrate/references/run-contract.md` (paths §1, header §2, params §4,
`export_check.json` §5).

**Boundary.** This skill does not measure, does not grade deviation against the scan and does
not write the delivery README. Those belong to `stl-re-measure-intent`, `stl-re-verify` and
`stl-re-deliver`. Verification must run independently of the builder (CHK-INDEP;
`analysis/SYNTHESIS.md` E16). Any check you run on your own model is a **self-check,
not QA**. Label it that way, as M02 did
(`golden-examples/M02-02-03_watertight-design-intent/model.py:90`,
`status: MODELING_SELFCHECK_COMPLETE_NOT_QA`).

## Inputs → outputs

| Reads | Writes (`<run>/build/`) |
|---|---|
| `measure/params.json` (every value carries a `source`) | `MODELING_PLAN.md`: written **before** `model.py` |
| `measure/PARAM_TABLE.md` | `model.py`: params-driven, deterministic, no hard-coded paths |
| `intake/INTAKE_CARD.md` (feature list, occlusion map) | `build_log.txt`, `fillets.json` |
| `intake/alignment.json` (`matrix_4x4`: raw scan → datum) | `<part>_datum.step`, `<part>.step` (scan frame), `<part>_cad.stl` (scan frame) |
| photos (for intent only) | `export_check.json` (run-contract §5) |

`<skill>` below is this skill's own folder (`.../stl-re-rebuild-build123d`), which holds
`scripts/`; `<run>` is the run folder, which holds `build/`, `intake/` and `measure/`. A
script path is always skill-relative and a data path always run-relative, regardless of the
shell's cwd (run-contract.md §1).

Scripts (all typed, argparse, JSON header per run-contract §2, provenance header):

| Script | Job |
|---|---|
| `scripts/export_frames.py` | Datum STEP + scan STEP (inverse T, SVD re-orthonormalised) + CAD STL. Re-imports both STEPs, validates them, writes `export_check.json`, aborts on failure. |
| `scripts/validate_step.py` | Checks for exactly 1 solid and 1 shell, closed, 0 naked edges, BRepCheck valid and volume > 0. Optional self-intersection check. Exit 2 = abort. |
| `scripts/fillet_log.py` | `FilletLog.apply()`: tries the target radius first, then the fallbacks. Logs target vs used radius and OK / REDUCED / FAILED / NO_EDGES. The `summarize` subcommand exits 2 on any non-OK entry. |
| `scripts/face_stats.py` | Surface census: face count, count and area share per surface type, analytic share, ruled-like B-spline faces. Reported, never gated. |
| `templates/model_template.py` | Skeleton showing every pattern below. Smoke test: `python templates/model_template.py --example`. |
| `templates/MODELING_PLAN.md` | Plan template. |

## Preconditions: HALT and ask instead of improvising

1. `measure/params.json` exists, and every param has `value` and `source` (run-contract §4).
   If it is missing, go back to `stl-re-measure-intent`.
2. `intake/alignment.json` has a `matrix_4x4`. If `scale_factor != 1`, `export_frames.py`
   does not abort: it writes the datum-frame STEP and its `export_check.json#datum` entry,
   skips the scan-frame export (`export_check.json#scan = {"skipped": ...}`), and exits 3
   (run-contract.md section 11). Add
   `- <date> | builder | OTHER | scan-frame STEP not delivered: scale_factor=<s> | build/export_check.json`
   to `DECISIONS.md` when this happens.
3. The part class is covered by a golden strategy (`references/strategy-catalogue.md`). There
   is no golden evidence for sheet metal, freeform or styled surfaces with no analytic
   intent, or multi-body STEP deliverables. For those, HALT and ask
   (`analysis/SYNTHESIS.md` §6; OD called multi-body "a separate job",
   `golden-examples/OD-H12_delonghi-dedica-pump/README.md:67-68`).
4. Gears: read `../stl-re-measure-intent/references/gears.md`
   (heuristic, n=1: M02) before planning the tooth.

## Step 0: iteration housekeeping (CHK-SUPERSEDED)

The **orchestrator** runs `init_run.py supersede <run>` after a `REVISE` verdict
(`../stl-re-orchestrate/SKILL.md:107,163`); it moves `measure/ build/ qa/` into
`_itN_SUPERSEDED/` intact and copies `MODELING_PLAN.md` and `model.py` forward. **Do not run
`init_run.py supersede` here** - `cmd_supersede` refuses unless the verdict is `REVISE`
(`../stl-re-orchestrate/scripts/init_run.py:235-236`), and after the orchestrator has already
superseded, `build/` holds the carried-forward `model.py`/`MODELING_PLAN.md`, so calling it
again fails or double-supersedes.

- On entry, if `qa/VERDICT.md` exists and `build/` was not superseded (i.e. this is a fresh
  rebuild after a REVISE that has not gone through the orchestrator's supersede step yet),
  stop and hand back to the orchestrator (CHK-SUPERSEDED) instead of overwriting `build/`.
- Within one iteration, rebuild attempts (Step 6's 3-attempts-per-feature loop) overwrite
  `build/` in place. Log each attempt and the parameter diff in the plan's change log (§8
  in `templates/MODELING_PLAN.md`). B02's it1→it2 diff was a single parameter
  (`analysis/SYNTHESIS.md` §5).
- *Why this boundary matters:* P03 overwrote its it1 verdict by rebuilding in place
  (`analysis/golden/OOM-P03.md` §8). B02 kept `_it1_SUPERSEDED/` with the script, STEP and
  param table (`golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/_it1_SUPERSEDED/`), which
  is exactly what the orchestrator's supersede step reproduces.

## Step 1: write `build/MODELING_PLAN.md` first (D1)

Copy `templates/MODELING_PLAN.md`. Write no geometry code before the plan exists. Every
golden except OD wrote a plan or feature table first (`analysis/SYNTHESIS.md` D1). The W01
"Lego-slop" failure (5,485 faces against a 734-face reference) had no plan
(`analysis/baseline/oomwoo-re-pipeline.md` §5).

The plan must contain:
1. **Strategy summary** (3–6 lines): the dominant silhouette and the ONE sketch or profile
   that captures it, the main symmetry (revolve axis, mirror, polar pattern), and what is
   added to or cut from it. This is the anti-Lego rule 1–2 (`RE_SPEC.md:257-259`).
2. **Ordered feature table.** Each row has: `F##`, operation, datum or plane, driving params
   *by name*, each with its `source` tag from params.json, and an acceptance criterion that
   can be checked on the STEP. A pattern counts as one op
   (`baseline/oomwoo-re-pipeline/TEMPLATES/MODELING_PLAN.md`, §3 rules).
3. **Every intake feature mapped.** Each feature enumerated in `INTAKE_CARD.md`, interior
   ones included, maps to an `F##` or gets an explicit out-of-scope reason. This feeds
   CHK-ENUM. P03 it1 lost the drive stem because it was never planned
   (`analysis/golden/OOM-P03.md` §8).
4. **Unscanned or invented geometry.** List every connector, hidden depth or core with its
   provenance tag (`assumed`, `photo-inferred` or `standard`). OD declared its hidden
   core tube, sheet thickness and bore depths
   (`golden-examples/OD-H12_delonghi-dedica-pump/README.md:54,65-66`). M02 declared that
   nothing unmeasured was invented (`analysis/SYNTHESIS.md` C11).
5. **Expected op count and expected face-count range.** These are expectations, *reported,
   not gated* (`QUESTIONS.md` A/Q3). Estimate the face count from the feature table: faces
   per op × instances. Golden reference points, for scale only and not as bands:
   - DRM screw 56, DRM snap 63
   - B02 185
   - OD 213
   - P03 500 (559 in another record; `QUESTIONS.md` B)

   `analysis/SYNTHESIS.md` D10.
6. **Fillet plan.** List each fillet or chamfer with its target param, its position in the
   order (last, or local; see Step 4) and any allowed fallback radii with the reason.
7. **Known risks.** Occlusions, uncertain counts, soft features. Say what you will report if
   reality does not match the plan.

If the model later needs an op the plan lacks, **update the plan first** and log the change.
A silent deviation from the plan is the W01 pattern (`RE_SPEC.md:253,264`: silent overrun = automatic REVISE).

## Step 2: choose a strategy per feature

Details and worked golden trees are in `references/strategy-catalogue.md`. Idioms are in
`references/build123d-idioms.md`.

| Strategy | Use for | Evidence |
|---|---|---|
| **Revolve a closed (r,z) profile** about the datum axis | Every turned region: hubs, bores, discs, steps, chamfers in the profile | RULE D2: OD, B02, P03, DRM |
| **Sub-bodies built separately, then unioned** | Assemblies-as-one-solid, arms, cores, bridges. Declare every invented connector in the plan. | RULE D3: all 5. OD core tube (`build_pump.py:272-274`); M02 continuous core bridge (`model.py:74-81`) |
| **One instance + placements** | Repeated features. Place the instance at the *measured* angles, which may be unequal. Enforce equal pitch only when the measured scatter is within noise. | RULE D4, C10. DRM's legs were kept at their measured, unequal angles rather than symmetrised (`golden-examples/dreame_brush-caps/README.md:50`) |
| **Cut tools as separate solids** | Sectors, slots, pockets, holes. Build the tool, fuse the tools, subtract once. | RULE D5. P03 `sector_tool` (`rebuild_OOM-P03.py:103-146`) |
| **Sketch + extrude** | Prismatic silhouettes: hex, pentagon, double-D, rounded-rect frame | DRM F01, F06; OD frame; P03 hex |
| **Intersect with an envelope** | Turned corners on a prism (e.g. a polygon intersected with a cylinder), radial trims | DRM F02 (`build_screw.py:29-31`); B02 radial trim (`build_OOM-B02.py:283`) |
| **Non-ruled loft through fitted sections** | Only when no analytic profile exists. See Step 5. | D15; B02 arm (`build_OOM-B02.py:255-268`) |

**Dropped as a default:** tri-axis extrude-intersect. No golden build used it
(`analysis/SYNTHESIS.md` §3, D11). Use it only when the plan justifies it for a specific
feature.

**Order rule for cuts:** make a cut after every body that would refill it. OD cut its
U-windows last "because the hub fills them otherwise"
(`golden-examples/OD-H12_delonghi-dedica-pump/report/src/build_pump.py:279-286`).

## Step 3: write `build/model.py` (D6)

Start from `templates/model_template.py`.
- **Parameters only from `measure/params.json`**, read through the `Params` class. It
  records the params the model used, and the build log lists the unused ones: an unused
  param means the plan and the measurements disagree. All five goldens drove the model
  from one dict or JSON (`analysis/SYNTHESIS.md` D6).
  - For a placement group (hole/leg angles, etc.), use `P.group(prefix)`. It accepts both
    forms run-contract §11 allows: a single list-valued param (`"leg_theta": {"value": [60,
    150, -60], ...}`) or numbered keys (`leg_theta_1, leg_theta_2, ...`). It never returns
    `[]` silently - an empty list, or no keys of either form, raises, so a pattern can never
    place zero instances unnoticed.
- **No numeric literal in geometry** except documented clearances. Examples: a cut tool
  overshooting a face (e.g. `+1.0`, commented), and the tangent-boolean offset (heuristic,
  n=1: B02; see idioms).
  - *Counter-examples:* OD hard-coded the barb radii 3.05, 2.95 and 2.6 and the screw
    z-stations in its profiles (`analysis/golden/OD-H12.md` §6).
  - If a value is needed and absent from params.json, send it back to measure. Do not
    invent it here.
- **Select edges by geometry**: type, position and radius, evaluated on the *current*
  shape. Never select by list index. See the pitfalls in `references/build123d-idioms.md`.
- **Deterministic, with no hard-coded paths.**
  - Put the run paths on the CLI.
  - Seed any randomness.
  - The DRM build call site wrote to a fixed Windows path (`build_screw.py:106`). Do not
    copy that.
- Log one line per feature to `build_log.txt` (`FilletLog.log`). Include the parameters a
  feature derived, e.g. a tilt angle computed from measured depths (see
  `report/screw_build_log.txt` for a worked case).
- End with `.clean()`, then `export_frames(...)` (Step 6).

## Step 4: fillets and chamfers, logged (D7, D8, CHK-FILLET)

Apply every fillet and chamfer through `FilletLog.apply(shape, feature, selector, radii=[target,
*fallbacks], param=...)`:
- `radii[0]` is the **target** from params.json. Fallbacks are allowed only if the plan
  lists them with a reason.
- The log records `target`, `used`, `n_edges` and a status:
  - `OK`
  - `REDUCED`: a smaller fallback was used
  - `FAILED`: shape unchanged
  - `NO_EDGES`: the selector matched nothing
- A result that is invalid, or that changes the solid count, counts as a failed attempt.

**Why:**
- B02 tried a target fillet radius, then successively smaller fallbacks, and never stored
  which radius actually shipped. That is a silent fallback (`build_OOM-B02.py:288-298`).
- P03's `if top_edges:` guard and bare `except` could skip its fillet with only a print. That
  is a silent skip (`rebuild_OOM-P03.py:148-156`).
- DRM wrapped every fillet and logged OK/FAILED, and both final logs show all OK
  (`golden-examples/dreame_brush-caps/report/*_build_log.txt`).

**Order:**
- **Default: fillets last.** B02 and P03 did this (`analysis/SYNTHESIS.md` D8).
- **Exception: a local fillet right after its parent feature** when a later op would destroy
  or split the edge. Log the reason in the plan. Golden examples:
  - DRM snap filleted the OD top edge *before* adding the legs
    (`build_snap.py:44-48`).
  - DRM screw filleted a feature's corners before a later boolean would have destroyed the
    edge (`build_screw.py:44-48`; see the source for the exact operation order).
  - OD filleted inside its sub-bodies (coil, terminal block).
- The baseline "fillets strictly last" rule is rewritten accordingly
  (`analysis/SYNTHESIS.md` §3).

**After the build:** run `python3 <skill>/scripts/fillet_log.py summarize <run>/build/fillets.json`.
- **Exit 2** means a non-OK entry. Fix the selector or geometry, or declare the entry in
  `MODELING_PLAN.md` as "target R… → used R… / not applied, because …".
- A REDUCED or FAILED fillet is a geometry deviation. Verify must see it in
  `export_check.json#fillets`, and deliver must list it as a limitation.

## Step 5: loft policy (D15, anti-patchwork)

- **Never** use `loft(..., ruled=True)` or `Polyline` stacks of raw scan slices, and never
  stack prisms to approximate a smooth face. W01 attempt 1 did exactly that and was
  WITHDRAWN: 5,485 faces with 4,753 B-splines, while the Tier-2 deviation could not see the
  problem (`baseline/oomwoo-re-pipeline/RE_SPEC.md:258-273`;
  `analysis/baseline/oomwoo-re-pipeline.md` §5). This rule stands even though the face
  count is not gated (`QUESTIONS.md` A/Q3).
- **Allowed:** a *non-ruled* loft through a few **fitted** sections. Each section is an
  analytic or param-driven profile (e.g. `RectangleRounded(w, t, r)` from measured
  stations), placed normal to a measured path. B02 lofted its arm through many such sections
  (`build_OOM-B02.py:255-268`). Also allowed: a `Spline` through a fitted (r,z) meridian
  inside a revolve profile (B02 dome, `build_OOM-B02.py:152`; `RE_SPEC.md:262` "fitted
  `Spline` profiles").
- Try a revolve, a sweep or an extrude first. A loft needs one plan line saying why none of
  them fits.

## Step 6: validate, re-import, export in two frames (D12, D14)

In `model.py`, call
`export_frames(body, alignment, build_dir, part, fillets_json=..., model_py=...)`, or run the
CLI on a datum STEP:

```
python3 <skill>/scripts/export_frames.py --shape <run>/build/<part>_datum.step \
    --alignment <run>/intake/alignment.json --out <run>/build --part <part> \
    --fillets <run>/build/fillets.json
```

It does the following, in order, and **aborts (exit 2 / `ExportAbort`)** on any failure, or
exits **3** (`ScaleFrameSkipped`, not a failure) when `scale_factor != 1` (see step 3 below):
1. It requires the built body to be exactly 1 valid solid; otherwise nothing is exported.
   Source: OD `export_final.py:25-26`.
2. It inverts T and re-orthonormalises the rotation by SVD.
   - OCP rejects a near-orthonormal matrix, and a float inverse is only near-orthonormal
     (`golden-examples/OD-H12_delonghi-dedica-pump/report/src/export_final.py:19`).
   - A non-rigid rotation block (singular values off 1 by more than a 1e-6 float-noise
     tolerance) aborts: a hidden scale or shear in `matrix_4x4` must not be silently
     orthonormalised away. That 1e-6 is a numeric-precision guard, not an engineering
     threshold.
   - A reflection (det < 0) aborts, because a mirrored part passes every validity check.
   - If `scale_factor != 1`, this step is skipped for the scan frame (see below).
3. It writes `<part>_datum.step` always, and `<part>.step` + `<part>_cad.stl` (scan frame)
   only when `scale_factor == 1`.
   - When `scale_factor != 1`, the run contract folds the scale into `matrix_4x4`
     (run-contract.md section 11), so inverting it back out for the scan frame would be a
     similarity transform, not a rigid OCP transform. `export_frames.py` writes the
     datum-frame STEP and its `export_check.json#datum` entry, records
     `export_check.json#scan = {"skipped": "scale_factor != 1 (run-contract.md section
     11)"}`, and exits **3** (distinct from the exit-2 abort). Add the `OTHER` line to
     `DECISIONS.md` described in Precondition 2.
   - STL tolerance defaults to 0.003 / 0.05 rad, as DRM used (`frames.py:19`).
   - OD used 0.01 / 0.1 (`export_final.py:36`).
4. It re-imports both STEPs and runs `validate_step.validate_shape`: 1 solid, 1 shell, closed,
   0 naked edges, BRepCheck valid, volume > 0. Every golden delivered exactly this
   (`analysis/SYNTHESIS.md` D12; M02 `model.py:85-101`, B02 `qa/q01_solid.py`).
5. It writes `export_check.json` per run-contract §5. For each frame this includes solids,
   valid, closed, faces, volume, area, bbox, `surface_types` and `fillets`, plus a
   frame-agreement block (equal faces, volume difference, round-trip bbox error).

**On abort:** fix `model.py`. The usual causes:
- a tangent-coincident boolean (see idioms)
- a zero-thickness union (add an overlap or a declared bridge, as M02 did)
- a floating sub-body that is not touching the main body (W01 attempt 2's disconnected
  pivot boss, `analysis/baseline/oomwoo-re-pipeline.md` §5)

Never deliver a STEP that failed this step. If the same feature still cannot be built after
3 attempts, stop and report a plan mismatch to the orchestrator
(`RE_SPEC.md:248-249`, per-feature breaker).

When an independent kernel is available (NX, FreeCAD, another OCC build), import the STEP
there too and keep its log. OD, B02, P03 and DRM all did (`analysis/SYNTHESIS.md` D13).

## Step 7: CHK-PATCHWORK self-census (reported)

```
python3 <skill>/scripts/face_stats.py <run>/build/<part>_datum.step --expect-faces MIN MAX \
    --json <run>/build/face_stats.json
```

- Report in `build_log.txt` and the plan:
  - the face count against the plan's expected range
  - the count and area share per surface type
  - the analytic area share
  - `ruled_like_faces`
- These numbers are **reported, not gated** (`QUESTIONS.md` A/Q3). Verify repeats the
  census independently.
- `ruled_like_faces > 0` coming from a loft is a **rule violation** (Step 5): rebuild that
  feature. A degree-1 B-spline from some other op needs a one-line explanation.
- A face count far outside the plan means the plan or the model is wrong. Explain which.
  - Counter-example: M02's polygonal involute produced 2,354 faces, 2,306 of them planar
    facets, with no Tier-0 check (`analysis/golden/M02-02-03.md` §6).
- **Planar-facet patchwork (stacked prisms, a polygonal curve in place of a smooth one) is
  invisible to `analytic_area_share` and `ruled_like_faces`**: planes count as analytic and
  are not B-splines, so the census reports them as clean. M02's polygonal involute gave
  `analytic_area_share = 1.0`, `ruled_like_faces = 0` and 2,354 faces
  (`analysis/golden/M02-02-03.md` §6) - this census alone would not have caught it. The
  signals are the face count against the plan and `face_stats.py`'s `plane_face_count` /
  `plane_face_median_area_mm2` (a plan-sized part with far more planes than expected, or an
  unexpectedly small median plane area, needs a by-eye look). No threshold is set here.
- Tested reference: this script reproduces OD's NX-log census exactly (see `OD-H12-Pump.log`
  for the recorded face-type breakdown).

## Step 8: hand off

- Confirm that the `build/` files in the table above exist.
- Put the plan's deviations (fillets, invented geometry, unused params, plan changes) at
  the top of `MODELING_PLAN.md` under "Build deviations".
- Then return control to the orchestrator for `stl-re-verify`. Do not grade deviation here.
  Do not copy anything to `deliver/` (CHK-PUBLISH, `analysis/SYNTHESIS.md` F5).

## Named checks this skill runs or feeds

| Check | Here | On failure |
|---|---|---|
| CHK-FILLET | `fillet_log.py` statuses + `summarize` | Fix the selector or geometry, or declare target → used in the plan. Never ship silently. |
| CHK-PATCHWORK | `face_stats.py` census; loft policy | Ruled or polyline-stack faces: rebuild the feature. Count out of range: explain it (not gated). |
| CHK-SUPERSEDED | (feeds; orchestrator runs `init_run.py supersede`) | Never overwrite an iteration in `build/`. If found unsuperseded on entry, hand back to the orchestrator instead of building over it. |
| CHK-ENUM (feeds) | Plan maps every intake feature | Unmapped feature: plan it, or declare it out of scope with a reason. |
| CHK-INDEP (feeds) | Label builder checks as "self-check, not QA" | Leave verification to a fresh agent. |
| CHK-FRAME (feeds) | Angles are read from params.json in the frozen datum frame only | Sign or angle mismatch with the photos: back to measure. Do not flip it in code. |

## Heuristics (single-case; label them when used)

- Hold a cut tool 0.02 mm clear of a tangent-coincident face so the OCC boolean succeeds
  (heuristic, n=1: B02, `build_OOM-B02.py:182-185`).
- A continuous core cylinder at the smaller root radius bridges a coplanar axial transition
  between two gears (heuristic, n=1: M02, `model.py:76-81`).
- A tilted-cylinder cut for a finger dimple, with the tilt derived from two measured depths
  (heuristic, n=1: DRM, `build_screw.py:60-71`; declared ≤0.05 mm profile error,
  `README.md:84`).
- A profile revolved over a measured angular span (±half-angle) for legs or hooks
  (heuristic, n=1: DRM snap, `build_snap.py:50-64`).
- A "safety mirror" when a revolve returns negative volume
  (heuristic, n=1: P03, `rebuild_OOM-P03.py:78-79`). Prefer a counter-clockwise
  profile; `validate_step.py` fails on volume ≤ 0.

## Open questions (not decided here)

1. **Face-count expectation method.** No golden recorded an expected face count before
   building. The per-op estimate in Step 1 is new practice and has no calibration data
   (`analysis/baseline/oomwoo-re-pipeline.md` §6 item 3).
2. **P03 face count.** 500 vs 559 across records (`QUESTIONS.md` B). It is quoted only as a
   reference point.

Resolved by the orchestrator session (run-contract.md section 11, 2026-09-25): scale in the
scan-frame export (Precondition 2, Step 6) and list-valued params (`Params.group()`, Step 3).
