# Baseline audit — `stl2dxf-facet-film` → rules that transfer to STL→parametric-STEP

Scope: `baseline/skills/stl2dxf-facet-film/` (16 files). The product (developable film-kit DXF for
watch covers) is **out of scope as a deliverable**; this file mines it only for rules about gates,
evidence, verdicts, structure, scripts, failure handling, occluded regions and mesh measurement.
All paths are repo-relative. Film-specific numbers are quoted only as evidence of a *pattern*, never
as STEP thresholds.

Abbreviation: `FF/` = `baseline/skills/stl2dxf-facet-film/`.

---

## 1. Inventory

| File | Lines | Role |
|---|---:|---|
| `FF/SKILL.md` | 503 | Entry point: pipeline stages 0–5, five construction recipes, gates, parameter card, pitfalls, definition of done. ~39 KB; frontmatter `description` alone is ~120 words. |
| `FF/references/method-synthesis-full.md` | 676 | Exhaustive 10-stage synthesis from six extraction reports + six reviews; parameter table, 13 dead ends, API mapping, data model, open questions. Partly stale (see §5). |
| `FF/references/nx-method-evidence.md` | 348 | "What the operator actually did" — corrected record of NX sessions per stage; time profile; open questions carried as declarations. |
| `FF/references/e2e-126713-method.md` | 608 | End-to-end reconstruction of the unfinished third record (recipe N, gate-integrity problems, two mesh-measurement bugs, provisional parameter table). |
| `FF/references/piece-catalogue.md` | 174 | Per-piece dimensions of three kits; declares which kits are fixtures vs inventory-only. |
| `FF/references/dxf-contract.md` | 123 | Output contract, defect census of the delivered files, regression fixtures ("fixtures, not rules"). |
| `FF/references/e2e-228235-manual-diff.md` | 139 | Measured diff of the maintainer's manual kit vs the pipeline's kit; provenance/evidence-quality section; diff method. |
| `FF/references/e2e-228235-manual-rulings.md` | 35 | Ten maintainer rulings (decided), with measured fact vs proposal vs decision columns. |
| `FF/references/e2e-fullkit-rv02-diff.md` | 91 | Diff report of an earlier full kit vs the accepted DXF; verdict vs contract gate. |
| `FF/references/e2e-fullkit-verdict.md` | 49 | Independent skeptical review of that kit: `PASS_WITH_FINDINGS`, findings ranked MAJOR/MODERATE/MINOR/INFO. |
| `FF/references/validation-smoke-test.md` | 63 | First real-scan run of the skill: measured-vs-reference tables and 11 severity-ordered findings about the skill itself. |
| `FF/references/e2e-fullkit-manifest.json` | 1559 | Example run manifest: validator report + per-piece `recipe/gates/dim_check/flags/bbox_mm/iso_strain_pct` + `regularisations` log. |
| `FF/scripts/ruled_sheet.py` | 342 | Ruled sheet build, discrete-curvature gate, exact unroll, outlier-rejecting spline fit; `__main__` self-test. |
| `FF/scripts/curve_network_sheet.py` | 731 | Coons patch from 2+2 curve network, C-vs-N trigger measurement, LSCM; self-test against stored `EXPECTED` numbers. |
| `FF/scripts/dxf_kit_writer.py` | 333 | Deterministic DXF writer + hard-gate validator; self-test incl. cross-process SHA-256 identity. |
| `FF/scripts/render_progress.py` | 135 | 2D kit plot + 3D sheets-over-scan renders (pyvista optional, "not a gate"). |

---

## 2. Transferable rules

| # | Rule | Evidence (path:line) | Why it transfers | How it would read in an STL→STEP skill |
|---|---|---|---|---|
| T1 | Never read raw mesh bytes into context; all mesh facts come from short scripts printing compact summaries. | `FF/SKILL.md:69-71`; `FF/references/validation-smoke-test.md:3` | Same context-budget problem for any STL. | "Load the STL only inside scripts (`process=False`); print summaries (bbox, component count, face count), never vertex dumps." |
| T2 | Align to a declared canonical frame first, persist the transform, keep it in the manifest. | `FF/SKILL.md:75-77`, `FF/SKILL.md:95-99`; `FF/references/method-synthesis-full.md:577` ("persist T + input hash") | Every STEP feature is placed relative to datums; an unpersisted transform breaks reproducibility and deviation checks. | "Stage 0: fit primary datum(s), build T, persist T + input SHA-256; all later numbers are in that frame." |
| T3 | Print a cheap sanity line after alignment (where known features must land) before proceeding. | `FF/SKILL.md:100-104` (caught a wrong-side extraction); `FF/references/validation-smoke-test.md:59` | Sign/axis errors are the cheapest-to-catch, costliest-to-miss class in RE. | "After alignment, assert the expected sign/position of 3–5 landmark features; stop on mismatch." |
| T4 | Keep multiple mesh components; do not "repair" the scan. | `FF/SKILL.md:97-99` | Silent repair changes the evidence being measured. | "Report shells/components; never modify the input mesh — model from it." |
| T5 | Define every measurement operationally (what points, what percentile, what departure criterion) so numbers compare across runs. | `FF/SKILL.md:105-108`; `FF/references/validation-smoke-test.md:12` (three sane methods spread 0.49 mm on one radius), `:54-55` | A dimension without a definition is not reproducible; blend-rounded edges make "the edge" ambiguous on any scan. | "Each measured parameter records its definition (estimator, point set, threshold) next to the value." |
| T6 | A converged fit is not proof it found the intended feature; grade it against an independent estimator, not its own residual. Named failure: circle fit over a filled disc; wrong cluster picked as a plane. | `FF/SKILL.md:109-113`; `FF/references/e2e-126713-method.md:538-558` | Directly applicable to cylinder/plane/circle fits in STEP RE. | "Every primitive fit gets a second, independent check (percentile radius, histogram peak, section plot). Residual alone never accepts a fit." |
| T7 | Unscanned / scanner-bridged geometry is *typed*, not fitted — say so explicitly, and cross-check against what is measurable. | `FF/SKILL.md:144-146`; `FF/references/validation-smoke-test.md:21`, `:54` ("fit the bezel bore overpromises") | Occluded bores, grooves and undercuts are common in STL→STEP; pretending to fit them manufactures false precision. | "If a feature is not resolvable in the mesh, its value comes from a declared source (operator spec, standard, caliper) and is tagged `typed`/`assumed`, never `measured`." |
| T8 | Tag every parameter with its provenance class (typed / fitted / measured) and source. | `FF/references/e2e-126713-method.md:563-564`; `FF/SKILL.md:422-442` (parameter card with Source column, "override per watch, never silently") | Provenance is what makes a parametric model auditable. | "Parameter table columns: name, value, unit, provenance (measured/typed/derived), source path, estimator." |
| T9 | Declare fit thresholds per fit in the run manifest rather than assuming one global constant. | `FF/SKILL.md:80-85` | Fit rejection thresholds legitimately differ by region; a hidden constant is an undocumented choice. | "Record the outlier-rejection value used for each fit in the manifest." |
| T10 | Inventory the features (piece/feature list) and get it confirmed **before** any geometry. | `FF/SKILL.md:115-120`; `FF/references/nx-method-evidence.md:328-329` | Equivalent to a feature plan/budget before modelling; productivity jumped after it in the record. | "Stage 1: feature list (id, type, datum, source of each dimension) confirmed before the first CAD op." |
| T11 | The hardest, least-gated step (boundary / edge extraction) must be named, and downstream gates declared blind to it. Add an explicit dimension cross-check against independent extents. | `FF/SKILL.md:197-211`; `FF/scripts/ruled_sheet.py:30-32`; `FF/references/validation-smoke-test.md:37`, `:52` (four boundary choices, all passing every gate) | In STEP RE, a well-formed solid can have wrong feature boundaries and still pass validity checks. | "Validity gates (closed shell, manifold) do not validate feature extents; add a separate mesh-vs-model dimension/deviation gate per feature." |
| T12 | Never validate a result against itself; a gate that compares an output to its own inputs is vacuous. | `FF/SKILL.md:323-327`; `FF/references/validation-smoke-test.md:51` (gate hole); `FF/SKILL.md:244-246` (sagitta measured on the built sheet is 0 by construction) | Common QA trap: measuring deviation of the model against points sampled from the model. | "Deviation is always mesh→model on the original scan, never model→model-derived samples." |
| T13 | Hard gates fail, they do not warn; `ok: False` = do not deliver. | `FF/SKILL.md:320-321`, `FF/SKILL.md:412` | Gate semantics must be binary for an agent to act on them. | "A failed Tier gate blocks export; warnings are a separate, named list." |
| T14 | Report a measured gate value together with the sampling/grid it was measured on; prefer the analytic value when discrete and analytic disagree. | `FF/SKILL.md:329-339`; `FF/references/e2e-126713-method.md:397-406` | STEP deviation stats (max/percentile) also depend on sampling density. | "Every deviation number states sample count/spacing and statistic (max, p95); use B-rep analytic queries where available." |
| T15 | Resolution honesty: when the measurement uncertainty is the same order as the threshold, the result is a grey zone that needs a human call. | `FF/SKILL.md:248-253` | Prevents false PASS/FAIL near tolerance bands. | "If |value − threshold| < measurement uncertainty, verdict = NEEDS_REVIEW, not PASS/FAIL." |
| T16 | Failures are reported, never waived; no silent fix of an open question. | `FF/SKILL.md:340-345`, `FF/SKILL.md:496-498` | Core verdict-honesty rule. | "A failed gate appears in the verdict with its number; it can only be cleared by a recorded human decision." |
| T17 | Verdict vocabulary with severity-ranked findings, and a "bottom line" that says what the result is **not**. | `FF/references/e2e-fullkit-verdict.md:3`, `:25`, `:46-49`; `FF/references/validation-smoke-test.md:47-59` | Gives an auditable, graded verdict instead of a binary claim. | "Verdict ∈ {PASS, PASS_WITH_FINDINGS, FAIL}; findings ordered MAJOR→INFO, each with measured number and fix." |
| T18 | Independent verification uses its own scripts, not the builder's. | `FF/references/e2e-fullkit-verdict.md:3-4` | QA that reuses the builder's code inherits its bugs. | "QA re-measures with independent code; reusing build helpers is disclosed." |
| T19 | Independence caveat: agreement with a reference built from the same source is expected, not validation; the disagreements are the informative results. | `FF/references/e2e-228235-manual-diff.md:139`; `FF/references/e2e-228235-manual-rulings.md:34-35` | Matching a golden model you were fed the dimensions of proves little. | "When a parameter was taken from the reference, exclude it from 'agreement' statistics." |
| T20 | Decided rulings vs open questions live in distinct namespaces; everything guarded by an open question is marked PROVISIONAL. | `FF/SKILL.md:23-29`; `FF/references/e2e-228235-manual-rulings.md:5-11` | Keeps decided doctrine separable from hypotheses. | "Rules cite a decision id; provisional defaults are tagged and link to the open question." |
| T21 | Measured facts of one reference are **fixtures, not rules**; fixtures from an incomplete record are never regression targets. | `FF/references/dxf-contract.md:94-103`; `FF/references/piece-catalogue.md:5-8` | Golden examples must not be over-generalised into doctrine. | "Golden-example numbers are regression fixtures for that part only; doctrine cites ≥1 decision or ≥2 independent examples." |
| T22 | Unknown ≠ absent: an uncaptured stage is reported as unknown. Evidence-quality caveats precede any claim about process. | `FF/SKILL.md:392`; `FF/references/e2e-228235-manual-diff.md:9`; `FF/references/e2e-126713-method.md:7-12` | Applies to golden examples with missing logs or intermediate states. | "When the evidence for a step is missing, say 'not in evidence' and do not infer a rule from it." |
| T23 | Trust geometry artifacts over event counts / logs; de-duplicate against the final model before concluding. | `FF/SKILL.md:470-489` | Applies to mining any recorded session or log in the golden examples. | "Final STEP/model state outranks build logs; log counts are not evidence of method." |
| T24 | Measure repeated-feature pitch from the mesh; eyeballed pitch drifts cumulatively. | `FF/SKILL.md:277-280`; `FF/references/method-synthesis-full.md:477-480` | Patterns (holes, ribs, teeth) are common STEP features. | "Pattern pitch = measured (autocorrelation/gap minima), with count also counted from the mesh." |
| T25 | Scans are not symmetric; mirror only for design intent, and verify each side against its own mesh region. | `FF/SKILL.md:300-303` | Mirror/symmetry assumptions are a standard STEP RE shortcut that hides asymmetry. | "Declare symmetry as intent; still measure both sides and report the delta." |
| T26 | Regularisation (snapping to primitives, unifying near-identical instances) is a real, logged step: *measured → chosen*. | `FF/SKILL.md:370-382`; `FF/references/e2e-fullkit-manifest.json` (`regularisations` array) | Identical to design-intent snapping in parametric CAD. | "Every snap (e.g. measured 9.97 → 10.00) is logged with its delta in the manifest." |
| T27 | One template per family; per-instance geometry only where the mesh region measurably differs. | `FF/SKILL.md:288-290`, `FF/SKILL.md:391` | Parametric models should share parameters across instances. | "Repeated features share one parameter set unless measurement shows a difference beyond tolerance." |
| T28 | Precondition vs check: some constraints (coincident corners) must be exact by construction, not "within tolerance". | `FF/SKILL.md:255-257` | Topology in B-rep is built exact; tolerant matching hides bad construction. | "Build shared edges/vertices from the same entity; do not rely on sewing tolerance." |
| T29 | Record dead ends and the cost of deciding, not only of doing. | `FF/SKILL.md:266-270`, `FF/SKILL.md:444-491` (pitfalls "each cost real time"); `FF/references/method-synthesis-full.md:448-501` | Pitfall lists derived from real failures save iterations. | "Pitfalls section: only failures observed in evidence, each with cited source." |
| T30 | Do not offset the raw mesh; build from fitted curves/primitives and offset those. | `FF/SKILL.md:455-456` | Mesh offsets self-intersect regardless of product. | "Never derive CAD offsets/shells from mesh normal offsets." |
| T31 | Visual diagnostics at every milestone, not only at the end; render is a diagnostic, optional renderer is "not a gate". | `FF/SKILL.md:51-54`; `FF/scripts/render_progress.py:14-16`; `FF/references/e2e-126713-method.md:548-549` (bugs caught visually, not by residual) | Model-over-mesh overlays catch errors numeric gates miss. | "Render model-over-scan views after each feature batch; state which views were inspected." |
| T32 | Determinism is verified cross-process (not in-process), with the pinned env documented; output hash goes into the manifest. | `FF/SKILL.md:405-408`; `FF/scripts/dxf_kit_writer.py:13-17`, `:309-332`; `FF/references/validation-smoke-test.md:50` | STEP writers can embed timestamps/ordering; reproducibility must be proven by two separate runs. | "Reproducibility = two fresh processes, same SHA-256 (or same geometric digest if the STEP header carries a timestamp); document env pins." |
| T33 | Bundled scripts carry a self-test that reproduces archived numbers at a stated tolerance; "import them, do not rewrite them". | `FF/SKILL.md:44-51`; `FF/scripts/curve_network_sheet.py:21-27`; `FF/scripts/ruled_sheet.py:306-341` | Stops agents re-deriving helpers each run. | "Each script: docstring with API + gates, `__main__` self-test with expected values and rtol." |
| T34 | Script docstrings state what the gate does **not** check. | `FF/scripts/ruled_sheet.py:30-32`; `FF/scripts/curve_network_sheet.py:28-30` | Prevents over-trust in a green check. | "Every validator documents its blind spots in its docstring." |
| T35 | Sidecar manifest per run: per-item source, recipe, gates passed (with numbers), flags, output SHA-256. | `FF/SKILL.md:326-327`, `FF/SKILL.md:418-420`; `FF/references/e2e-fullkit-manifest.json` | Maps directly onto a STEP run bundle (feature → source → gate result). | "MANIFEST.json: per feature {source, estimator, value, gates{name: value, pass}}, input + output hashes." |
| T36 | Definition of done is an explicit conjunctive checklist including re-read round-trip and determinism. | `FF/SKILL.md:493-503` | Clear stopping condition for an agent. | "Done = all hard gates pass + deviation cross-check + STEP re-import round-trip + determinism + manifest." |
| T37 | Findings outside the task are logged as separate fix tasks, not silently fixed in the current patch. | `FF/SKILL.md:409-411`; `FF/references/e2e-228235-manual-diff.md:138` | Keeps iteration bounded and diffs reviewable. | "Out-of-scope defects → logged finding with id; do not expand the current iteration." |
| T38 | Open questions the evidence cannot answer are carried into runs as explicit declarations. | `FF/references/nx-method-evidence.md:314`; `FF/references/method-synthesis-full.md:629+` | Operator-dependent facts (datum sign, intent) must be asked, not guessed. | "Intake lists what the mesh cannot decide (datum sign, hidden features, intent) as operator declarations." |
| T39 | Crop a region of interest before local fits. | `FF/references/method-synthesis-full.md:138-149` (§B4) | Local fits on sub-meshes are more robust and faster in any RE. | "Fit each feature on a cropped sub-mesh; persist the crop definition." |
| T40 | Surface fitting is a guide; boundaries/features measured directly from the mesh beat a freeform fit. | `FF/references/method-synthesis-full.md:463-466` | Supports primitive-first parametric modelling over freeform surfacing. | "Prefer analytic primitives measured from the mesh; freeform surface fit only as a visual guide." |

---

## 3. Structure lessons

**Split as found.**
- `SKILL.md` (503 lines) carries the full procedure *and* a large share of the evidence: per-watch numbers, ruling ids, record session ids, click counts (`FF/SKILL.md:346-360`), capture-tool traps (`FF/SKILL.md:470-489`). It is closer to a condensed reference than an entry point.
- `references/` holds three kinds of material mixed together: (a) doctrine-grade contracts (`dxf-contract.md`, `piece-catalogue.md`), (b) run evidence / reports (`validation-smoke-test.md`, `e2e-fullkit-*`, `e2e-228235-*`), (c) research history (`method-synthesis-full.md`, `nx-method-evidence.md`, `e2e-126713-method.md`).
- `scripts/` are tested, importable modules with docstring APIs and self-tests; the skill says to import, not rewrite (`FF/SKILL.md:51`).

**What works.**
- The reference index in `FF/SKILL.md:31-50` tells the reader *when* to open each file ("read when you need exact values or doubt a step"; "consult it before deviating from any recipe").
- Scripts encode the gates in code (e.g. `developability()` returns a `pass` flag, `FF/scripts/ruled_sheet.py:145`), so the doctrine and the check cannot drift silently — where it was done.
- Contract file separates *what the evidence teaches* from *the contract* from *fixtures* (`FF/references/dxf-contract.md:20`, `:61`, `:94`).
- Smoke-test and verdict files are good templates for QA reports: measured vs reference vs delta tables and severity-ranked findings.

**What is bloated / fragile.**
- Frontmatter `description` is ~120 words of trigger phrases and history (`FF/SKILL.md:3`); a skill description should state purpose + triggers only.
- `SKILL.md` repeats the ruling namespace and PROVISIONAL disclaimers inline dozens of times; the same namespace block is duplicated in `FF/references/method-synthesis-full.md:35-37` and `FF/references/piece-catalogue.md:10-12`.
- Run reports (dated, one-off) sit in `references/` next to doctrine; a new reader cannot tell which are current. `FF/references/e2e-fullkit-manifest.json` (1559 lines) is example data, not reference.
- `method-synthesis-full.md` is marked "COMPLETE (2026-08-23)" (`:3`) yet contradicted by later files (see §5); stale history is presented with the same weight as current doctrine.
- Dangling references to files outside the bundle: `tasks/NXLEARN-126713/run/RULINGS.md` (`FF/SKILL.md:18`, `:43`), `C:/spk/...` (`FF/references/validation-smoke-test.md:4`), "repo rules" / "CLAUDE.md rule 6" / "the stl2step skill" (`FF/SKILL.md:382`, `:420`; `FF/references/e2e-126713-method.md:414`). No `tasks/` directory exists in this repo.

**Lesson for the STEP skills:** keep `SKILL.md` to procedure + gates + pointers; put decided contracts in `references/`; put dated run reports and research history in a separate evidence area (or not in the skill at all); every number in `SKILL.md` should either be a rule with a decision/evidence citation or be absent.

---

## 4. Non-transferable content

- Five construction recipes A/B/C/N/D for developable sheets (`FF/SKILL.md:136-306`) — film construction, not solid modelling.
- Developability / Gaussian-curvature gate and its thresholds (`FF/SKILL.md:217-222`, `:321-322`) — a film-flattening concern; the numbers must not become STEP thresholds.
- Unroll / LSCM / ARAP flattening and iso-strain gates (`FF/SKILL.md:308-345`) — 2D development has no STEP analogue.
- Recipe C→N trigger 0.20 mm (`FF/SKILL.md:238-253`) — film-specific and n = 1 provisional.
- Clearances, insets, fillets R 0.3/0.4, link wrap, crown notch (`FF/SKILL.md:422-442`) — cutting-film manufacturing values.
- Nesting gaps, sheet layout (`FF/SKILL.md:394-402`) — 2D cutting layout.
- DXF contract: layers, LWPOLYLINE bulges, R2004, labels, XDATA, narrow-feature erosion (`FF/references/dxf-contract.md:61-86`) — output format differs; only the *pattern* of a defect census transfers.
- Watch canonical frame (crystal centre, crown = +X) (`FF/SKILL.md:75-77`) — part-specific; only the "declare + sanity-check frame" pattern transfers.
- NX dialog defaults, click counts, capture-tool traps (`FF/SKILL.md:346-360`, `:470-489`) — tool/session-recording specific.
- Windows MAX_PATH, cloud-drive save locks, igl.ARAP segfault (`FF/SKILL.md:452-469`) — environment-specific.
- Per-watch piece catalogues and regression fixtures (`FF/references/piece-catalogue.md`, `FF/references/dxf-contract.md:94-123`) — product fixtures.
- Bezel "do not develop the slope, TPU tolerates it" (`FF/SKILL.md:170-171`) — material-specific tolerance judgement.

---

## 5. Gaps and contradictions noticed

1. **Fillet default drift.** `FF/SKILL.md:382-385` and `FF/references/dxf-contract.md` rule 4 state R 0.3/R 0.4 per family (ruling R7), but `FF/scripts/dxf_kit_writer.py:92` defaults `corner_radius=0.4` and its docstring still calls R0.4 "the maintainer's final value"; `FF/references/method-synthesis-full.md:531`, `:648` also say "default 0.4". Code and doctrine disagree. *Transfer lesson: when a ruling changes a default, change code defaults and stale references in the same patch.*
2. **Nested-gap default vs rule.** Rule is ≥ 1.0 mm (`FF/SKILL.md:396-399`), but `FF/scripts/dxf_kit_writer.py:162` defaults `nested_gap=0.35`; the skill works around it with "pass explicitly". The earlier verdict accepted `min_gap 0.370` as ok (`FF/references/e2e-fullkit-verdict.md:8-9`) under the old default. *A safe default should be the rule.*
3. **Development-gate thresholds disagree across files.** `FF/SKILL.md:321-323` says strain/area ≤ 0.4 %; `FF/references/method-synthesis-full.md:587` says ΔA ≤ 0.1 %, Δperimeter ≤ 0.5 %, Δedge ≤ 0.1 mm.
4. **Refuted boundary method still recommended in reference.** `FF/references/method-synthesis-full.md:581` and `:656` recommend dihedral-angle ridge extraction ("non-issue for the port"); the smoke test showed it fails on blend-rounded edges (`FF/references/validation-smoke-test.md:52`) and SKILL.md agrees (`FF/SKILL.md:207-208`). The "COMPLETE" synthesis was never reconciled.
5. **Boundary extraction remains the weakest step and is only partially gated.** SKILL.md makes the dimension cross-check mandatory (`FF/SKILL.md:209-211`, `:495-497`) but for a new part with no catalogue the only comparator is "facet region's measured extents", which is derived by the same boundary criterion — risk of self-reference (cf. T12).
6. **Open gate conflicts left in doctrine.** A maintainer-kept piece fails the stated gates (`FF/SKILL.md:340-345`); the discrete K max swings with grid (`FF/SKILL.md:329-339`). The skill handles this honestly (report, don't waive), but the gate itself is not pinned — an agent cannot produce a reproducible PASS.
7. **Dangling paths.** `tasks/NXLEARN-126713/run/RULINGS.md` holds all open-ruling text but is not bundled (`FF/SKILL.md:18`, `:43`); several `C:/spk/...` and `H:\...` artifacts are cited as evidence but not in the repo (`FF/references/validation-smoke-test.md:4`; `FF/references/e2e-228235-manual-diff.md:7`; `FF/references/e2e-fullkit-rv02-diff.md:88`). Claims depending on them cannot be re-verified here.
8. **No iteration bound.** Nothing caps retries per piece or per run; the only cost signal is anecdotal ("six abandoned re-opens, 158 s", `FF/SKILL.md:269-270`). STEP skills need an explicit bound.
9. **Precision reporting without uncertainty in places.** Many values are quoted to 3–6 decimals (e.g. `FF/SKILL.md:167-169`) while the skill itself states 0.2–0.5 mm boundary uncertainty (`FF/SKILL.md:208`). Significant figures do not track measurement uncertainty.
10. **Smoke-test findings partially folded in.** Findings #1, #2, #8, #10, #11 (`FF/references/validation-smoke-test.md:49-59`) appear addressed in current code/SKILL (`FF/scripts/dxf_kit_writer.py:145`, `:309-332`; `FF/scripts/ruled_sheet.py:145`, `:268`; `FF/SKILL.md:100-104`), but the smoke-test file does not record which were closed, so it reads as open.
