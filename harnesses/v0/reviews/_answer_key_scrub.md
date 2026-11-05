# Answer-key leakage scrub (D1 in both replay reports)

Source: `harnesses/v0/evals/replay/artifacts/B02/new/REPLAY_REPORT.md` D1/D1b,
`harnesses/v0/evals/replay/artifacts/DRM/new/REPLAY_REPORT.md` D1/D2. Scope: prose/comments in
`harnesses/v0/skills/stl-re-orchestrate`, `harnesses/v0/skills/stl-re-intake-datum`, `harnesses/v0/skills/stl-re-measure-intent`,
`harnesses/v0/skills/stl-re-rebuild-build123d`, `harnesses/v0/skills/stl-re-verify` (SKILL.md, references/*,
templates/*, script docstrings/comments). `harnesses/v0/skills/stl-re-deliver` and `tests/` untouched
(confirmed via `git status`; those files were modified by another agent, not this pass).

Rule applied throughout: keep the rule/lesson and a citation to
`golden-examples/...:line` or `analysis/golden/*.md`; remove inline golden dimension/datum/
clock/gate-result values, replacing them with a pointer to the cited file. Regime thresholds
(RE_SPEC 0.15/1.6/4.0/0.8, baseline 0.30/0.80/0.15/0.50, datum audit 0.3°/0.15mm) and script
parameters with a cited source (RANSAC tol, IRLS scale, sample counts, seeds, tessellation
tolerances, etc.) were kept as allowed.

## harnesses/v0/skills/stl-re-intake-datum/references/datum-cookbook.md
Rewrote §2.1 (DRM screw), §2.2 (B02), §2.3 (P03), §3 (OD), §4 (normals). Removed: DRM pentagon
clock −34.23°, double-D r 1.873, tilt figures (0.72°/2.82°), B02 rim normal vector, r_hint
10.35, loop radii (hex 2.45–4.09, cup 9.67–10.59), audit 0.429°/0.451mm, B02 raw volume
−2434mm³, P03/OD specific fit residuals. Replaced each with a method description + lesson +
pointer to `analysis/golden/<part>.md` or the golden report. Kept the DOF-ladder table and the
`align.py` spec-key reference table (both generic/parametric).

## harnesses/v0/skills/stl-re-intake-datum/SKILL.md
Redacted: B02 ENV ratios (0.984–0.996) and "arms 0.4–0.8mm oversize" numbers → generic;
golden noise-floor table (DRM/B02/P03/OD numeric rms values) → pointer to
`analysis/golden/*.md`; open-loop radii (hex 2.45–4.09 etc.) → generic "several distinct
loops"; DRM pentagon clock −34.23° / snap clock −42.19° → generic + pointer; DRM tilt
0.72°/2.82° figures → generic + pointer; landmark values (dome apex 10.97/10.96, DRM bottom
z −5.12/−5.15) → generic; CHK-FRAME B02 "−71° vs +59°" → generic description of the lesson
(sign-convention mismatch) + pointer. Left "B02 and P03 → RE_SPEC; DRM and OD → baseline-skill"
(regime choice per part, not a measured answer) and mesh-statistics asides (body counts,
table-vertex %) — these are process metadata, not datum/dimension/clock/gate answers.

## harnesses/v0/skills/stl-re-measure-intent/SKILL.md
Redacted: B02 it1 F06 24.84/12.420→12.550 struck-reading narrative → generic + pointer;
hex AF 7.358 "held" quote → generic + pointer; CHK-FRAME −71°/+59°, 59.04° → generic;
noise-floor list (B02/P03/DRM/OD numbers) → pointer; simplification costs (OD ±0.1, B02
+0.74/−0.51, DRM ±0.07) → pointer; the "Open questions" B02 scan-window paragraph (25.617–
26.850, 24.99–27.25, 25.99–27.08, margins 0.148/0.56, D-06=25.79) → generic explanation +
pointer to `references/validation.md` / `analysis/golden/OOM-B02.md`; P03 "6+6→8" eyeball
count → generic.

## harnesses/v0/skills/stl-re-measure-intent/references/intent-rules.md
Rewrote every precedent-table cell that stated a golden numeric answer (M02 tooth/OD values,
B02 cup-bore/scan values, arm-thickness readings, cup-floor rounding, draft-angle rounding,
hex-AF 7.358, SAF-1 angles 57.6/60.0/61.5→59.0/59.04°, P03 hex-AF averages, pattern counts,
symmetry angles 120.42/120.38/119.20→120.00, DRM PCD 8.81–9.02→8.90, DRM snap-leg angles,
OD coil centre, simplification costs, OD's parameter-count/hub-diameter conflict numbers) to
name the *kind* of precedent and cite the golden file, without restating the value. Kept all
rule/threshold columns unchanged.

## harnesses/v0/skills/stl-re-measure-intent/references/param-table-schema.md
Redacted `SKIRT_R_LOBE = 26.85/2` and hex-AF-7.358 mentions → generic; the `struck[]` JSON
example (reading 24.84, window 24.99..27.25) → clearly-labelled illustrative placeholders;
CHK-FRAME −71°/+59° reference → pointer.

## harnesses/v0/skills/stl-re-measure-intent/references/validation.md
Rewrote entirely: kept the fact that each script (pattern_count.py, sim_caliper.py,
sections.py cluster, fits.py) was validated against a golden part and what kind of
agreement/disagreement resulted, but removed every literal figure (tooth-count residuals, OD
figures, P03 order/phase numbers, B02 window numbers 25.617–26.850 / 24.988–27.246 / 24.84 /
0.148 / 0.56, P03 vertex/face counts). Pointer added to `analysis/golden/*.md` and the golden
PARAM_TABLE/VERDICT files for anyone who needs to re-validate.

## harnesses/v0/skills/stl-re-measure-intent/scripts/param_table.py
Two f-string error messages that named "B02 D-09/10/12" and "B02 hex AF 7.358" now cite
`analysis/golden/OOM-B02.md` instead of stating the reading. No logic changed (same trigger
conditions, only the message text).

## harnesses/v0/skills/stl-re-measure-intent/scripts/sim_caliper.py
Docstring/help-text: replaced "F06 = 24.84 unachievable (window 25.99...27.08)" and
"caliper 5.33 vs scan mean 5.89" with pointers to `analysis/golden/OOM-B02.md`. No logic
changed. `py_compile` passes.

## harnesses/v0/skills/stl-re-orchestrate/SKILL.md
"B02 it1 F06 Δ +0.647" → generic description + citation only.

## harnesses/v0/skills/stl-re-orchestrate/references/run-contract.md
"DRM legs at 60°/150°/−60°" → generic "DRM's leg angles are a worked example" + citation.

## harnesses/v0/skills/stl-re-orchestrate/references/verdict-examples.md
This file's whole purpose was a worked answer key for all six golden parts (D1/D2's primary
target). Rewrote all six entries (DRM screw, DRM snap, OD-H12, B02, P03, M02) to keep the
verdict *vocabulary* (which checks fire, why, what the orchestrator does next) while removing
every stated numeric result and, where the entry itself was the "reveal" of a part's outcome,
softened wording to point at the cited record instead of asserting the answer. Added a header
note explaining why numbers are withheld here. Kept regime thresholds and check-id names.

## harnesses/v0/skills/stl-re-rebuild-build123d/SKILL.md
Removed: DRM dimple-tilt "5.15°" example, "DRM screw filleted the frustum corners before
intersecting" (explicit feature-tree step) → generic; B02 fillet-fallback radii (R0.8→0.5→0.3)
→ generic; "pentagon ∩ cylinder" (explicit DRM feature-tree phrase) → generic "polygon
intersected with a cylinder"; DRM snap-leg angles → generic; B02 loft "22 sections" → "many
sections"; OD's exact face-type breakdown (213 = 139/48/24/2) → pointer.

## harnesses/v0/skills/stl-re-rebuild-build123d/references/strategy-catalogue.md
Rewrote entirely (this was "the five golden feature trees" — a direct, numbered reproduction
of each part's real build sequence with real coordinates: dimple tilt derivation, DRM leg/cup
placement angles, OD coil centre (−0.2, 0.1), bare radii 3.05/2.95/2.6/−21.0, face counts).
Replaced each numbered tree with a prose summary of the *strategy* used (revolve/extrude/
loft/sub-body/etc.) and the *lesson*, with a pointer to `analysis/golden/<part>.md` §6/§11 for
the actual tree.

## harnesses/v0/skills/stl-re-rebuild-build123d/references/build123d-idioms.md
"DRM legs at 60°/150°/−60°" → generic; "OD's profile carried three bare radii
(3.05, 2.95, 2.6)" → generic "several bare numeric radii".

## harnesses/v0/skills/stl-re-rebuild-build123d/scripts/fillet_log.py
Docstring example "'F05 dimples: tilt 5.15 deg'" → placeholder `<deg>`. No logic changed.

## harnesses/v0/skills/stl-re-rebuild-build123d/scripts/face_stats.py
Docstring/comments: OD's exact face-type breakdown and M02's exact facet counts (2354/2306)
replaced with pointers to `analysis/golden/*.md`/the golden log. No logic changed.

## harnesses/v0/skills/stl-re-verify/SKILL.md
Datum-audit report-only numbers (B02 0.429°/0.451, P03 0.154°/0.600) → pointer; B02 F06
24.84/25.99–27.08 achievability example → generic + pointer; masked-vs-unmasked hex numbers
(1.624/0.316/1.846) → pointer; OD observability numbers (25.65%, p95 0.567, ray-test params)
→ generic "record the parameters used"; P03 stem cluster numbers (158k/4907/r<6.4) → generic;
B02 it1→it2 hex numbers (1.846→0.316) → generic; DRM ICP iteration counts (90, 109) → pointer
to replay report.

## harnesses/v0/skills/stl-re-verify/references/gate-protocol.md
Datum-audit numbers (0.429°/0.451, 0.154°/0.600) → pointer; "a false 17.8°/9.2mm audit" (B02
replay D6) → generic; "73° off" (DRM clock-offset bug) → generic; DRM ICP "109 of 300" → pointer;
B02 "F06 Δ +0.647" and "gated 5 of 24" → generic; P03 stem "4907 points at r<6.4" → pointer.

## harnesses/v0/skills/stl-re-verify/references/mask-policy.md
Golden-examples table: removed all per-mask fractions/max values (B02 M1–M4/A6 percentages
and 1.624 unmasked max; DRM snap's six mask percentages and 1.246 max) → generic
descriptions + pointer to `analysis/golden/*.md`. Rewrote both "wording" example blocks to use
explicit `<placeholder>` tokens instead of B02/DRM's real numbers, with a note to read the
cited VERDICT.md/README for the real wording.

## harnesses/v0/skills/stl-re-verify/references/verdict-template.md
§3 "Golden outcomes" table (stated APPROVED/BAND_NOT_MET + numbers for every golden part) →
replaced with a pointer to `stl-re-orchestrate/references/verdict-examples.md` (single source
of truth, already scrubbed) instead of duplicating the answer key. §4 "Worked numbers" (raw
OD/DRM/B02 deviation-gate, ICP and Tier-1 dumps, including F01 hex AF 7.358, F06 25.6165,
datum-audit 0.4275°, ICP 51/60 and 109/300 iteration counts) → reduced to qualitative
statements that each script reproduces the golden numbers to a stated precision, with a
pointer to the golden report / `analysis/golden/*.md` for the actual figures.

## harnesses/v0/skills/stl-re-verify/scripts/datum_audit.py
Docstring and two inline comments carrying B02/P03 datum-audit numbers (0.429°/0.451,
0.154°/0.600), "a false 17.8°/9.2mm audit", and "73 deg off" → replaced with pointers to
`analysis/golden/OOM-B02.md`/the replay report. The `note` string written into
`qa/datum_audit.json` output was also reworded the same way (same fields, same trigger
condition — output shape and logic unchanged, `py_compile` passes).

## Deliberately kept (verified not to be in-scope leaks)
- Regime thresholds and script parameters with a cited source (RANSAC tol 0.05, IRLS scale
  0.30, RE_SPEC/baseline bands, tessellation tolerances, sample counts/seeds, sweep radii,
  ray-test defaults) — explicitly allowed by the rule.
- Qualitative statements of which regime a given golden part used (e.g. "B02 and P03 →
  RE_SPEC") — this is provenance/process metadata, not a datum/dimension/clock/gate answer.
- `harnesses/v0/skills/stl-re-measure-intent/references/gears.md`: M02's operator-specified tooth counts,
  OD, module and pressure angle. M02 is a `project-spec` part whose numbers come from an
  `OPERATOR_SPEC.json` the agent is handed as input, not derived from the scan blind — so
  these are not an "answer" a blind replay would need to avoid seeing; they are the given
  spec a real task would also supply.
- M02 face/facet aggregate counts left in a few illustrative sentences describing the
  CHK-PATCHWORK "census blindness" lesson (e.g. "a large number of small planar facets") after
  removing exact figures — kept as illustrative wording, not exact numbers.
- Minor process facts without numeric golden answers (e.g. "P03 missed its drive stem despite
  photo evidence", "B02 enumerated several interior items") — these describe process failures,
  not datum specs/dimensions/clock angles/caliper strikes/gate numbers.

## Verification
- `grep -rniE` for the suggested tokens (12.55, 7.358, 7.353, 25.99, 24.84, 20.75, 5.33, 4.07,
  0.72°, 59.04, 0.429/0.451, 2.524, 0.740, 73.26, 109 ICP, 1.873, -34.2x, 5.12/5.15°) across the
  five in-scope skill directories (excluding tests/) returns no matches.
- `python3 -m py_compile` passes for every script touched: `param_table.py`, `sim_caliper.py`,
  `face_stats.py`, `fillet_log.py`, `datum_audit.py`.
- No rule thresholds, check-id semantics or script logic were changed — only prose/comments/
  docstrings and the two informational string literals in `param_table.py`/`datum_audit.py`.
