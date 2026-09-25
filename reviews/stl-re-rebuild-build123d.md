# Review: `skills/stl-re-rebuild-build123d`

VERDICT: REVISE

Reviewer: independent Phase-4 reviewer (not the author). Date 2026-09-25.
Scope: `SKILL.md`, `references/*` (3), `scripts/*` (5), `templates/*` (4). Nothing in the
skill was edited.

Severity count: **BLOCKER 0 · MAJOR 5 · MINOR 7 · NIT 4**

The core engineering is sound. `export_frames.py` reproduces both golden scan-frame STEPs
exactly (details below), and `validate_step.py`/`face_stats.py` reproduce the OD NX census.
REVISE is for five contract, boundary and wording problems. Each one can be fixed
mechanically.

## Findings

| id | sev | file:line | finding | evidence | concrete fix |
|---|---|---|---|---|---|
| M1 | MAJOR | `scripts/export_frames.py:179-182`; `SKILL.md:47-48`, `SKILL.md:312-315` | When `scale_factor != 1` the script aborts **before writing anything**: no datum STEP and no `export_check.json`. Run-contract §11 already settled this case: the scale is folded into `matrix_4x4`, the scan-frame export is skipped, **only the datum-frame STEP is delivered**, and an `OTHER` line goes into `DECISIONS.md`. Precondition 2 and Open question 1 still call it undecided, so a cold agent HALTs where the contract says to proceed. | I ran it with `scale_factor=1.01`: rc=2, output folder empty (`/tmp/rev_rebuild/o_scale`). `run-contract.md:142-148`. | In `export_frames()`, when `scale != 1.0`: export and re-import only `<part>_datum.step` and validate it. Write `export_check.json` with `"scan": {"exported": false, "reason": "scale_factor=<s> (run-contract §11)"}`, then raise `ExportAbort` with a distinct message, or return exit code 3 = "datum-only". In `SKILL.md`, replace Precondition 2's clause "must be 1.0 … (see Open questions)" with "If `scale_factor ≠ 1`, export_frames writes the datum frame only (run-contract §11). Add `- <date> \| builder \| OTHER \| scan-frame STEP not delivered: scale_factor=<s> \| build/export_check.json` to `DECISIONS.md`." Delete Open question 1. |
| M2 | MAJOR | `templates/model_template.py:231-235`; `references/build123d-idioms.md:56`; `SKILL.md:316-318` | The contract allows list-valued `value` and says "a consumer must accept both" forms. `Params.group()` only reads numbered keys `prefix_1…`, so a DRM-style `leg_thetas: [60,150,-60]` returns `[]` and **silently places zero instances**. Open question 2 is stale. | `run-contract.md:138-141`. DRM `report/snap_params.json:18` (`leg_thetas` list). | In `group()`: `if prefix in self.raw and isinstance(self.raw[prefix]["value"], list): return list(self[prefix])`. Otherwise use numbered keys. If both are empty, `raise KeyError(f"no params for {prefix}")`, so an empty pattern cannot pass silently. Delete Open question 2 and cite run-contract §11 instead. |
| M3 | MAJOR | `scripts/export_frames.py:141-152` | A non-rigid `matrix_4x4` (hidden scale or shear with `scale_factor` still 1.0) is **silently snapped** to a rotation and exported with rc=0. The scan-frame STEP is then misplaced relative to the scan, and only `inverse_rotation.orthonormalisation_max_abs` records it. This is the exact case run-contract §11 says cannot be a rigid OCP transform. | I multiplied m[0][0] by 1.02: singular values 1.0012/1.0/0.9841, `orthonormalisation_max_abs` 0.0149, rc=0 (`/tmp/rev_rebuild/o_nonortho`). Golden matrices give 3e-13 (example) and float noise (DRM, OD). | Add a guard: `if max(abs(S - 1)) > 1e-6: raise ExportAbort("matrix_4x4 is not rigid (singular values …); a scale belongs in scale_factor (run-contract §11)")`. Label 1e-6 in the docstring as a float-noise tolerance, not a design threshold. In `SKILL.md` Step 6 item 2, add "a non-rigid matrix aborts". |
| M4 | MAJOR | `SKILL.md:57-67`, `SKILL.md:290` | Step 0 tells the **builder** to run `init_run.py supersede` whenever `build/` "already holds a previous iteration". Three problems: (a) the orchestrator already does this after REVISE (`stl-re-orchestrate/SKILL.md:107,163`); (b) `cmd_supersede` refuses unless the verdict is `REVISE` (`init_run.py:235-236`), and after the orchestrator's supersede, `build/` holds the carried-forward `model.py`/`MODELING_PLAN.md`, so a second call fails or double-supersedes; (c) Step 6's "3 attempts per feature" loop happens *within* one iteration and must overwrite `build/`. The boundary is ambiguous and the instruction is unrunnable as written. | `skills/stl-re-orchestrate/scripts/init_run.py:233-243`; `stl-re-orchestrate/SKILL.md:107`. | Rewrite Step 0 as follows: "The orchestrator runs `init_run.py supersede` after a REVISE verdict; do **not** run it here. On entry, if `qa/VERDICT.md` exists and `build/` was not superseded, stop and hand back to the orchestrator (CHK-SUPERSEDED). Within one iteration, rebuild attempts overwrite `build/` in place; log each attempt and the parameter diff in the plan's §8 change log." In the checks table, change the CHK-SUPERSEDED row's "Here" cell to "feeds (orchestrator runs it)". |
| M5 | MAJOR | `references/strategy-catalogue.md:141-143`; `SKILL.md:268-270`, `SKILL.md:289` | The census **cannot see planar-facet patchwork** (stacked prisms, polygonal profiles): planes count as analytic, so it reports `analytic_area_share = 1.0` and `ruled_like_faces = 0`. The catalogue says the M02 facets are "exactly what the census flags", and the CHK-PATCHWORK row ("Ruled or polyline-stack faces: rebuild") implies the census detects them. A cold agent would read 1.0 / 0 as clean. `ruled_like` *does* catch ruled lofts and lofts through polyline sections (verified). | `face_stats.py` on M02 STEP: 2354 faces, 2306 plane, analytic share **1.0**, ruled_like **0**. Test loft through 24-gon polyline sections: ruled=True gives 96 ruled_like, ruled=False gives 24 ruled_like, so both are caught. | (1) In the catalogue, replace "it is exactly what the census flags" with "the type census does **not** flag it: planar facets count as analytic. Only the face count against the plan exposes it." (2) In `SKILL.md` Step 7, add the bullet "Planar-facet patchwork (stacked prisms, polygonal curves) shows as analytic planes. The signals are the face count against the plan and `planar_faces`. Inspect them whenever the plane count exceeds the plan." (3) Optionally have `face_stats.py` report, without gating, `plane_plane_edges_dihedral_deg` as a histogram (p5/p50) of dihedral angles across plane–plane shared edges. Near-0° pairs are facets. Give no threshold. |
| m1 | MINOR | `scripts/export_frames.py:155-162, 211-216`; `SKILL.md:239-240` | `roundtrip_bbox_max_abs_mm` moves the scan STEP back with the **same** trsf inverted. It is tautological: it would pass even if T were applied in the wrong direction. The direction is only proven by overlaying the scan. (I checked this manually: DRM scan→CAD p50 0.026 / p95 0.087 on the regenerated STL.) | `/tmp/rev_rebuild/cmp.py` output. | Rename the key to `numeric_roundtrip_bbox_mm` and set the note to "numerical round-trip only; does not prove the direction of T; verify overlays the scan". Optionally add `--scan <stl>`, which reports (never gates) the median distance from 2,000 seeded scan vertices to `<part>_cad.stl`. |
| m2 | MINOR | `scripts/export_frames.py:170, 174-183` | The docstring says `ExportAbort` is raised "after writing export_check.json when possible". The early aborts (invalid body, scale, reflection) write nothing, so verify and deliver cannot see why the build stopped. | Reflection and scale runs gave empty folders. | Before each early `raise`, write `export_check.json` with the header, `"pass": false` and `"failures": [msg]`. |
| m3 | MINOR | `scripts/fillet_log.py:78-86` | A selector that **raises** is logged as `NO_EDGES`, which is the same label as a selector that legitimately matched nothing. This hides a code bug. | Test: `lambda s: 1/0` gave status NO_EDGES, tried=[selector: division by zero]. | Add a status `SELECTOR_ERROR` (count it in `summary()` and treat it as non-OK in `summarize`), and list it under STATUS VALUES and in `SKILL.md:164-168`. |
| m4 | MINOR | `scripts/export_frames.py:198-200`; `SKILL.md:238-240` | `export_check.json#inputs` hashes the alignment, fillets and model.py, but not `measure/params.json`. It also records no sha256 for the exported STEPs, although verify's `hash_frozen.before` needs exactly that (run-contract §12). | `export_check.json` from the template run. | Add a `params_json: Path \| None` argument (hashed into inputs), and a `"sha256"` field in `res["datum"]` and `res["scan"]` computed with `_common.sha256_file` after export. |
| m5 | MINOR | `SKILL.md:60, 190, 220, 258` | The commands mix a skill-relative script path (`scripts/…`, `../stl-re-orchestrate/…`) with run-relative data paths (`build/…`, `intake/…`). No single cwd satisfies both. | Run-contract §1 says sibling paths are skill-relative. | Write the commands as `python3 <skill>/scripts/fillet_log.py summarize <run>/build/fillets.json` (and the same for the others), and define `<skill>` = this skill's folder once, at the top of Inputs → outputs. |
| m6 | MINOR | `templates/model_template.py:282` | The template's fallback `r_f * 0.5` is an undocumented geometry literal. It teaches the pattern Step 3 forbids ("no numeric literal in geometry"), and Step 4 says the plan must list fallback radii. | `SKILL.md:140-146, 162-163`. | Read the fallbacks from params: `radii=[r_f, *P.group("hub_fillet_fallback")]`, add `hub_fillet_fallback_1` (source `assumed`, rule "plan fallback") to `example_params.json`, and comment that the fallbacks must appear in plan §5. |
| m7 | MINOR | `scripts/export_frames.py:76` | The provenance cites `build_screw.py:101` for the hard-coded Windows path. The line is **106**. `SKILL.md:152` and the catalogue say 106 correctly. | `golden-examples/dreame_brush-caps/report/source/build_screw.py:106`. | Change `:101` to `:106`. |
| n1 | NIT | `scripts/validate_step.py:58-71` | `naked_edge_count` flags edges used fewer than 2 times, but not non-manifold edges used more than 2 times. BRepCheck usually catches those, but the report cannot show it. | — | Also report `nonmanifold_edges = sum(n > 2 and not seam)` (report only). |
| n2 | NIT | `scripts/export_frames.py:180` | `scale != 1.0` is an exact float comparison. | — | Use `abs(scale - 1.0) > 1e-12`. |
| n3 | NIT | `SKILL.md:24-30` vs `run-contract.md:14` | The skill writes `fillets.json` and `face_stats.json`, which run-contract §1 does not list. Additions are allowed, but deliver's manifest (`stl-re-deliver/scripts/make_manifest.py:53-57`) does not register them. | — | Ask the orchestrator to add both to §1's `build/` line. Say "additions per run-contract preamble" in the table. |
| n4 | NIT | `SKILL.md:164-168` vs `run-contract.md:75` | The contract says fillet status is "OK/FAILED". The skill emits OK/REDUCED/FAILED/NO_EDGES. That is an additive superset, but verify (`stl-re-verify/SKILL.md:98`) should know about it. | — | Add one line to run-contract §12: "`fillets[].status` ∈ OK \| REDUCED \| FAILED \| NO_EDGES (\| SELECTOR_ERROR); anything but OK is a CHK-FILLET finding." |

## What I ran (all outputs under `/tmp/rev_rebuild/`, `/tmp/stl_re_template_example/`)

- `python3 -m py_compile` on all 5 scripts and `templates/model_template.py`: all OK. `--help`
  works for all 4 CLIs. Environment: build123d 0.13.0.
- **Template:** `model_template.py --example` gave rc 0 in 3.3 s: 1 solid, valid, closed,
  18 faces, fillets 2 OK. `fillet_log.py summarize` gave rc 0. Determinism: two fresh runs
  with `SOURCE_DATE_EPOCH=0` gave identical `fillets.json`, `build_log.txt` and CAD STL.
  `export_check.json` differs only in the out-dir path key of `inputs`.
- **export_frames on the DRM screw golden:** `--shape dreame_brush_screw_cap_datum_frame.step
  --alignment report/screw_alignment.json`, rc 0. Result against the **delivered**
  `dreame_brush_screw_cap.step`: identical bbox, volume 269.0776 (Δ 7e-8), 56 = 56 faces,
  boolean differences **0 / 0 mm³**, max vertex distance 7.7e-14 mm over 88 = 88 vertices. The
  regenerated CAD STL has the same bounds as the delivered one. Scan→CAD on the decimated scan
  (20k seeded vertices): p50 0.026 / p95 0.087, consistent with the golden 0.085.
- **export_frames on OD** (`alignment_T1.json` rewrapped as `matrix_4x4`): the scan bbox equals
  the golden `report/export_check.json` scan bbox (−39.218/−68.207/−259.806 …). Boolean
  differences 0 / 0.
- **validate_step on `OD-H12-Pump_datum.step`:** pass. 1 solid, 1 shell, **213 faces**, 0 naked
  edges, volume 114903.27 (golden 114903.3). `face_stats`: 139 plane / 48 cylinder / 24 cone /
  2 torus, which matches `OD-H12-Pump.log:26,35,37,53,67`. `--expect-faces 150 250` gives
  in-range, not gated.
- Census on the other goldens: DRM screw 56 (22 plane / 24 cyl / 2 cone / 3 torus / 5 bspline,
  0.9947), which matches the catalogue claim. DRM snap 63. B02 185 (40 bspline, 0 ruled_like,
  so the 22-section loft is correctly *not* flagged). P03 500. M02 2354 (share 1.0,
  ruled_like 0; see M5). All pass validity.
- **Abort paths:** a reflection matrix gives rc 2 (good). `scale_factor` 1.01 gives rc 2 with
  nothing written (M1). A 2 % non-rigid matrix gives rc 0 (M3).
- **FilletLog statuses:** OK, REDUCED (R5→R4.5), FAILED (R6/R5.5 on a 4 mm box, shape
  returned unchanged), NO_EDGES and a raising selector (see m3). `summarize` returns rc 2 on
  non-OK. The export_check `fillets` list carries target/used/status per frame (CHK-FILLET
  logging meets §5).
- **export_check.json against the run contract:** §5 keys are all present per frame (`solids`,
  `valid`, `closed`, `faces`, `volume_mm3`, `area_mm2`, `bbox`, `surface_types{count, area}`,
  `fillets`). The §12 top-level `{datum, scan}` shape matches. The §2 header is present.
  `stl-re-deliver/scripts/make_readme.py:199-208` reads it without change.
- **Citations spot-checked (22, all correct except m7):** M02 `model.py:76-81, 85-101, 90`;
  OD `README.md:54, 65-68`, `build_pump.py:181, 272-274, 279-286`, `export_final.py:19, 25-26, 36`;
  B02 `build_OOM-B02.py:152, 163-166, 171, 182-185, 222-226, 255-268, 283, 288-298`;
  P03 `rebuild_OOM-P03.py:78-79, 82-86, 103-146, 118-122, 148-156, 161`; DRM `build_screw.py:22-25,
  29-31, 44-48, 60-71, 100, 106`, `build_snap.py:44-48, 50-64`, `README.md:50, 82-84`,
  `frames.py:19`; `RE_SPEC.md:248-253, 257-270, 26-27`; `TRACKER.md:32`;
  `analysis/golden/M02-02-03.md:119`; `analysis/baseline/oomwoo-re-pipeline.md` §5, §6.3. An
  automated existence check of every full repo path cited in the skill found no dead paths.
- **Numbers:** every number is from SYNTHESIS §4 (3 loops) or is quoted as "the golden used
  X" (STL tolerances 0.003/0.05 and 0.01/0.1; 0.02 mm as heuristic, n=1; the face-count
  reference points as observed results, "not bands"). No invented thresholds. M3's proposed
  1e-6 is a float-noise tolerance and must be labelled that way.
- **Owner decisions:** the face census is reported, not gated (`face_stats.py:315`
  `"gated": false`, SKILL Step 7). The loft and polyline rules are kept (Step 5). The regime
  and the datum audit do not apply to this stage. CHK-INDEP self-check labelling is present.
- **Size:** `SKILL.md` has 323 lines, and progressive disclosure into 3 references is sensible.
  The frontmatter `name` equals the folder. The description gives what and when ("once
  measure/params.json exists, or when a verdict sends the CAD back"). No trigger collision
  with the siblings: verify owns grading, deliver owns the README.
- `__pycache__` created during testing was deleted. Nothing in the repo was modified except
  this file.

## Strengths

- The dual-frame export is correct and golden-exact on two independent goldens (DRM, OD). The
  reflection guard is a good addition.
- `FilletLog` closes both golden CHK-FILLET failures (B02 silent fallback, P03 silent skip):
  it logs target against used, counts edges, and rejects a result that is invalid or changes
  the solid count.
- `face_stats.py` reproduces the OD NX census exactly, and `ruled_like` correctly separates
  B02's fitted loft (0) from ruled and polyline-section lofts (>0).
- The loft policy is clearly worded and evidence-cited (W01 withdrawal, B02 22-section loft,
  RE_SPEC rule 3), and the owner's "reported, not gated" decision is respected.
- The local-fillet exception (D8) is backed by three concrete golden line citations.
  Heuristics are consistently labelled n=1.
- The OCP/build123d version-drift table comes from real testing, and the scripts include the
  shims.

## Fixes applied (round 1)

Applied by the fix agent, 2026-09-25, per orchestrator decisions 1–5. Only files under
`skills/stl-re-rebuild-build123d/` were edited; `run-contract.md` was read but not touched
(owned by another agent).

| id | status | notes |
|---|---|---|
| M1 | fixed | `scripts/export_frames.py`: `scale_factor != 1` no longer aborts before writing anything. `export_frames()` now exports/validates only `<part>_datum.step`, writes `export_check.json` with the `datum` entry and `"scan": {"skipped": "scale_factor=<s> != 1 (run-contract.md section 11): ..."}`, then raises the new `ScaleFrameSkipped` (carries `result`), which `main()` (CLI) and `model_template.py`'s `main()` both catch and turn into exit code **3**, distinct from the exit-2 `ExportAbort` path. `SKILL.md` Precondition 2, Step 6 and the exit-code line document this and the `DECISIONS.md` OTHER line; Open questions 1 removed. Verified: synthetic `scale_factor=1.01` on the DRM screw golden -> rc=3, `x_datum.step` written, `export_check.json#scan.skipped` present, `pass: true`. |
| M2 | fixed | `templates/model_template.py`: `Params.group()` now accepts a single list-valued param named `prefix` (run-contract §11) as well as numbered `prefix_1, prefix_2, ...` keys, and raises `KeyError` (never returns `[]` silently) when the list is empty or neither form is present. `SKILL.md` Step 3 documents both forms; Open question 2 removed. Verified with a synthetic `leg_theta: {"value": [60, 150, -60]}` (returns the list), numbered keys (unchanged behaviour), an empty list (raises), and a missing group (raises). Template `--example` smoke test (which now also exercises a fallback-radii group, see m6) still passes rc 0. |
| M3 | fixed | `scripts/export_frames.py`: `scan_frame_trsf()` now checks the SVD singular values of the inverted rotation block against 1 with a `RIGID_SINGULAR_VALUE_TOL = 1e-6` guard (commented as a float-noise tolerance, not an engineering threshold) and raises `ExportAbort` naming the singular values instead of silently orthonormalising. The guard only applies when `scale_factor == 1` (when it is not, run-contract §11 says the scale is legitimately folded into `matrix_4x4`, so a non-rigid rotation block there is expected, not a bug, and is moot since the scan frame is skipped anyway). `SKILL.md` Step 6 documents the abort. Verified: a synthetic 2% non-orthogonal perturbation of the DRM golden matrix (singular values 1.0017/1.0/0.9861) now aborts rc=2 with `export_check.json` written (previously rc=0, per the review's repro). |
| M4 | fixed | `SKILL.md` Step 0 rewritten: the orchestrator runs `init_run.py supersede`, not the builder; the builder only reads carried-forward `build/` files and hands back to the orchestrator (CHK-SUPERSEDED) if it finds an unsuperseded prior iteration. In-iteration rebuild attempts overwrite `build/` in place. Named-checks table's CHK-SUPERSEDED row updated to "(feeds; orchestrator runs `init_run.py supersede`)". |
| M5 | fixed | `references/strategy-catalogue.md`: M02 entry now says the type census does **not** flag the planar-facet patchwork (cites `analytic_area_share = 1.0`, `ruled_like_faces = 0` on that STEP) and that only the face count / new plane-area fields expose it. `SKILL.md` Step 7 adds a bullet stating the same, with the M02 evidence (2,354 faces / 2,306 planar facets) and naming `plane_face_count` / `plane_face_median_area_mm2` as the reported (not gated), no-invented-threshold signals. `scripts/face_stats.py` now computes and reports `plane_face_count` and `plane_face_median_area_mm2` (median area of plane faces only; `None` when there are no plane faces) alongside the existing per-type counts, with a docstring section explaining the blind spot and citing M02. Verified: `face_stats.py` on the M02 golden STEP gives faces=2354, analytic_area_share=1.0, ruled_like_faces=0 (confirming the blind spot), plane_face_count=2306, plane_face_median_area_mm2=0.17988 (confirming the new signal is visible). OD golden still reproduces the NX census exactly (213 = 139 plane / 48 cylinder / 24 cone / 2 torus) with plane_face_count=139. |
| m1 | fixed | `scripts/export_frames.py`: `roundtrip_bbox_max_abs_mm` renamed to `numeric_roundtrip_bbox_mm`; its `note` now says it is a numerical round-trip only, does not prove the direction of T, and that overlaying the scan is the real check. (The `--scan` seeded-vertex comparison suggested as optional was not added, to keep the change minimal and local; the note tells the reader what to do instead.) |
| m2 | fixed | `scripts/export_frames.py`: every early abort path (invalid body, bad/missing `matrix_4x4`, non-rigid matrix, reflection) now writes `export_check.json` (via a new `_abort_with_report` helper) with the run-contract §2 header, `part`, `pass: false` and `failures: [msg]` before raising `ExportAbort`, so verify/deliver can always see why a run stopped. |
| m3 | fixed | `scripts/fillet_log.py`: added a `SELECTOR_ERROR` status, distinct from `NO_EDGES`, for a selector that raises. Counted in `summary()`; `summarize` already treats any non-`OK` status (including this one) as failing. `STATUS VALUES` doc block updated. Verified with a selector that raises `ZeroDivisionError`: status is `SELECTOR_ERROR`, not `NO_EDGES`. |
| m4 | fixed | `scripts/export_frames.py`: added an optional `params_json` argument (hashed into `inputs`, wired through from `--params` on the CLI and from `model_template.py`), and each frame's report in `export_check.json` now carries a `sha256` of the exported STEP (computed with `_common.sha256_file`) so verify's `hash_frozen.before` (run-contract §12) has a value to read directly. Verified on the DRM golden reproduction: `datum`/`scan` `sha256` fields are present and non-empty. |
| m5 | fixed | `SKILL.md`: added a short "`<skill>`/`<run>`" convention paragraph under "Inputs → outputs", and rewrote the `fillet_log.py summarize`, `export_frames.py` and `face_stats.py` command blocks to use `<skill>/scripts/...` for the script and `<run>/build/...` for data paths consistently, instead of mixing skill-relative and run-relative paths under one implied cwd. |
| m6 | fixed | `templates/model_template.py`: F05's fallback radius is no longer the bare literal `r_f * 0.5`; it now reads `*P.group("hub_fillet_fallback")` from params.json. `templates/example_params.json` gained a `hub_fillet_fallback_1` entry (source `assumed`, estimator notes it is a plan fallback). Verified via the `--example` smoke test (still rc 0, fillets both OK). |
| m7 | fixed | `scripts/export_frames.py`: provenance comment now cites `build_screw.py:106` (was `:101`), matching `SKILL.md:152` and the catalogue. |
| n1 | fixed | `scripts/validate_step.py`: added `nonmanifold_edge_count()` (edges used more than twice, excluding degenerate ones) and a report-only `nonmanifold_edges` field in `validate_shape()`'s result, alongside the existing `naked_edges`. Not part of the pass/fail rule. Verified: OD golden gives `nonmanifold_edges: 0`. |
| n2 | fixed | `scripts/export_frames.py`: the scale check is now `abs(scale - 1.0) <= 1e-12` (`scale_rigid`) instead of an exact `!=` comparison; this was folded into the M1 rewrite rather than kept as a separate literal `scale != 1.0` line. |
| n3 | skipped | Requires adding `fillets.json`/`face_stats.json` to run-contract.md §1's `build/` line, which this agent was told not to edit (owned by another agent). Left as a note for the orchestrator; no local fix is possible without touching the shared contract. |
| n4 | skipped | Same reason as n3: the fix is a line in `run-contract.md` §12 documenting the `SELECTOR_ERROR` status addition (itself now shipped, see m3) for `stl-re-verify` to read. Out of scope for this pass; flagging for the orchestrator/verify owner. |

### Verification run (this pass)

- `python3 -m py_compile` on all 5 scripts + `templates/model_template.py`: OK.
- `templates/model_template.py --example`: rc 0, 1 solid, 18 faces, fillets `{OK: 2, REDUCED: 0,
  FAILED: 0, NO_EDGES: 0, SELECTOR_ERROR: 0}` (new key present).
- DRM screw reproduction (`export_frames.py` on `dreame_brush_screw_cap_datum_frame.step` +
  `report/screw_alignment.json`): rc 0, 56 = 56 faces, volume 269.077577 both frames,
  `numeric_roundtrip_bbox_mm` 3.5e-7, `sha256` present on both frame reports - matches the
  review's original repro.
- OD `face_stats.py` on `OD-H12-Pump_datum.step`: 213 faces = 139 plane / 48 cylinder /
  24 cone / 2 torus (matches golden log), `plane_face_count` 139, `plane_face_median_area_mm2`
  10.27, `nonmanifold_edges` 0 (via `validate_step.py`).
- M02 `face_stats.py` on `M02-02-03_WATERTIGHT_SOLID.step`: 2354 faces, `analytic_area_share`
  1.0, `ruled_like_faces` 0 (confirms the blind spot M5 documents), `plane_face_count` 2306,
  `plane_face_median_area_mm2` 0.17988 (confirms the new reported signal).
- Synthetic non-rigid matrix (DRM alignment with `matrix_4x4[0][0] *= 1.02`): rc 2, `ABORT:
  matrix_4x4 rotation block is not rigid (singular values [1.001674, 1.0, 0.986148], ...)`,
  `export_check.json` written with `pass: false` (previously rc 0 per the review's finding).
- Synthetic `scale_factor=1.01` on the DRM alignment: rc 3, `DATUM-ONLY: scale_factor=1.01: ...`,
  `<part>_datum.step` written, `export_check.json#scan == {"skipped": "scale_factor=1.01 != 1
  (run-contract.md section 11): ..."}`, `pass: true` (previously rc 2 with nothing written).
- `Params.group()`: verified list-valued, numbered-key, empty-list (raises `KeyError`) and
  missing-group (raises `KeyError`) cases directly against the class.
- `FilletLog.apply()` with a selector that raises `ZeroDivisionError`: status `SELECTOR_ERROR`
  (previously `NO_EDGES`), counted in `summary()`.
- All temporary output folders and `__pycache__` directories created while testing were
  removed; nothing outside `skills/stl-re-rebuild-build123d/` and this review file was edited.
