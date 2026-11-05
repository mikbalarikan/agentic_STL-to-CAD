# Harness v1: feature tree + staged deviation loop (design, in development)

v0 (`../v0/`, tag `harness-v0`) measures everything once, writes `params.json` in a single
pass, then the agent writes `model.py` from scratch. One bad plan gives one bad output, and
every part costs a few hundred lines of fresh CAD code. v1 changes three things:

1. **Scripts instead of fresh code.** The model is a JSON feature tree built by one generic,
   tested builder. The agent writes data, not geometry code.
2. **Build, measure, correct, one feature at a time.** After the datum and a base body, a
   loop finds red deviation regions, classifies each one with scripted math tests, adds the
   winning feature, rebuilds and keeps it only if the fit improves.
3. **One decision interface.** Wherever the loop is unsure it emits a decision card. In
   autonomous mode the agent answers it. In guided mode (a later milestone) the user answers
   it in a UI. Both modes share the same pipeline.

Evidence for this direction: the NX projects on branch `nx-re-intake`
(`nx-reference/INVENTORY.md`), summarised in "Lessons carried in" below.

## Pipeline

```
init → intake + datum ──► base body ──► ┌──────────── inner loop (builder, self-check) ────────────┐
        [human: regime,                 │ deviation map → red clusters → classify each cluster    │
         calipers / scan-only]          │ → best hypothesis → add feature → rebuild → re-measure  │
                                        │ → accept (fit improved, no new red) or roll back        │
                                        │ ambiguous? → decision card → agent | user (guided mode) │
                                        └──── stop: band met / residue = noise or unobservable ───┘
                                                          │
                                     fillets + finishing ─┴─► independent verify (fresh agent) ─► deliver
```

The inner loop's deviation numbers are a **builder self-check** (CHK-INDEP still holds). The
final gate stays the v0-style independent verify in a fresh context with its own ICP.

## Components

| Component | Job | Ported from |
|---|---|---|
| `features/` library | Tested parametric ops: `revolve_profile`, `sketch_extrude(draft=)`, `boss`, `rib`, `pocket`, `hole`, `hole_pattern`, `polar_pattern`, `mirror`, `cut_tool`, `clip_to_envelope`, `shell`, `loft_sections` (non-ruled), `fillet_family`. Every op reports volume delta, solid count and face census. | v0 `model_template.py` idioms; NX `stages2.py`, `nxf.py` |
| Profile sketcher | Vertex chain of lines and arcs → closed build123d face with named dims. An arc goes through both end points and the centre only picks the side, a 180° arc is split at its apex, nothing is inferred. | NX `dreame_bottom_cover/work/nxlib/ps.py`, `geo.py` |
| `feature_tree.json` | Ordered nodes `{id, op, params (named, each with source), parent, stage, status}`. Order rules are enforced by the builder: bodies before cuts, voids and bores last, fillets last unless the node says `local`. | v0 MODELING_PLAN feature table |
| `build_tree.py` | Builds the tree, writes STEP/STL and a per-node log (volume delta with the expected sign, solids, faces, errors). A failing node rolls back to the previous good state. | NX `p_build3.py` stage runner, `nxh.mark/undo_to` |
| `deviate.py` | Signed two-way deviation with a cached ray-casting scene, area-weighted, per-zone and per-mask, masked and unmasked rows side by side. | NX `dev.py`, `lt_clean2/an/lib.py`, `g_gates.py`; v0 `deviation_gate.py` |
| Observability fix | Interior bores the scanner never reached must not count as observable CAD→scan surface (v0 defect #3, OD-H22). | v0 `observability.py` |
| `clusters.py` | Red regions → connected clusters on the scan mesh with sign (+ material missing in CAD, − extra CAD material), area, bounding frame. Minimum area set from the noise floor. | new |
| `classify.py` | Per cluster, run hypothesis tests and score each by fit residual plus a complexity penalty (see below). Writes a ranked hypothesis list. | NX `pw.py`, `fit.py`, `chain.py`/`fitchain.py`, `m_bowl7.py`, `m2_twist.py`, `hmap2.py`; v0 `fits.py`, `sketchfit.py`, `pattern_count.py` |
| `loop.py` | Drives the inner loop: pick the cluster, take the top hypothesis, add the node, rebuild, re-measure, accept or roll back, log a round. | NX `STATUS.md` loop, Dreame overlay loop |
| Decision cards | `decisions/cards/<n>.json`: `{question, candidates[], scores, previews[]}` plus the answer and who gave it. Mirrored into `DECISIONS.md`. | v0 `DECISIONS.md` |
| `run_metrics.json` | Machine-readable run summary for the benchmark (see below). | new |

### Hypothesis tests in `classify.py`

Each test works on the cluster's scan points and normals in the datum frame.

| Signal | Hypothesis | Parameters it yields |
|---|---|---|
| normals perpendicular to one direction d | extrude along d | profile from the stacked averaged section, depth range |
| n·d constant and non-zero over the side walls | extrude with draft | draft angle = asin(n·d), pull direction |
| normal lines meet a common axis | revolve | axis (Nelder-Mead on radial spread), meridian chain |
| cylinder or cone fit residual at the noise floor | hole / boss / counterbore | axis, radius, depth, through or blind |
| same cluster repeats at a rotational or linear pitch (≥ 3 instances) | pattern of one instance | count, pitch, measured per-instance angles |
| plane fit offset from a CAD face | face step / pad / pocket floor | offset, outline from a height map |
| narrow concave band along a CAD edge | fillet (deferred to the finishing stage) | radius |
| straight generators at an angle to the axes | skew extrude | vector from straight height contours |
| none fits within band | escalate (decision card) | – |

Score = residual RMS / noise floor + λ · (number of new parameters). The simplest
explanation wins when residuals are close. Two candidates within a set margin → decision card.

### Rules the loop must obey

- **No cluster-tracing pads.** A miss is fixed by changing a real feature's type, size or
  position. Irregular pads that copy a cluster outline were rejected by the owner even though
  the numbers improved (87.5 → 91.5 %, Left Thigh, "mud stains"). After 3 rounds on the same
  cluster it becomes an open point in the report.
- **Accept only on improvement.** A node is kept when global and local deviation drop and no
  new red cluster appears. Otherwise it is rolled back and the next hypothesis is tried.
- **Patchwork budget.** Minimum cluster area, a complexity penalty, a face budget per feature,
  and the v0 anti-patchwork rule (no ruled lofts, no per-station extrusions).
- **Datum and base body stay up front.** The plan becomes a starting hypothesis, not a
  frozen contract.
- **Masked and unmasked rows are always reported.** Masks are named before grading, never
  added after a miss.

## Metrics contract (for the benchmark)

Every v1 run writes `<run>/run_metrics.json`. Fields the harness can know:

- harness id and commit
- part, regime and verdict
- loop rounds, plus nodes accepted and rolled back
- decision cards, split into answered by the agent and answered by the user
- final deviation summary
- face and feature count
- wall time per stage

Token use and cost are recorded by the benchmark runner, not by the harness, so the numbers
stay comparable across models and agent CLIs.

## Milestones

| | Scope | Done when |
|---|---|---|
| M1 | `features/` library, profile sketcher, `feature_tree.json` schema, `build_tree.py` with per-node checks and rollback; port v0 intake/measure/verify/deliver scripts that do not change | the OD-H22 valve rebuilds from a hand-written tree with the same deviation as v0, with no `model.py` |
| M2 | observability fix, `deviate.py`, `clusters.py`, `classify.py`, `loop.py`, decision cards answered by the agent | OD-H22 and one golden part rebuild from datum + base body through the loop |
| M3 | skills (`SKILL.md`) for v1, slimmed: evidence citations moved to `references/`; `run_metrics.json`; doctor and selftests | `tools/harness.py install v1` works; v0 vs v1 comparison on the same parts |
| M4 | guided mode UI: datum candidates (axes, planes, circles) highlighted for the user to pick Z, X and origin; decision cards with side-by-side previews | the same pipeline runs with the user as arbiter |

## Lessons carried in (NX projects, `nx-re-intake`)

- Measure outside the CAD kernel on a datum-aligned numpy mesh. The NX MCP tools were almost
  never used: the agent wrote NXOpen journals and helper libraries did the work.
- Staged gates beat end-only checks. On the Left Thigh, an end-only check gave 79.6 / 76.7 %
  of area within 0.5 mm. Per-stage gates with a fresh verifier gave 94.7 / 94.1 %.
- The overlay-correct loop on the Dreame cover took masked p95 from 1.33 to 0.594 mm.
- The same Dreame cover was rejected three times as a build123d model and approved as an NX
  model built from fully constrained sketches with 109 named parameters and staged
  functions. That build discipline is what the `features/` library and sketcher port.
- Prove every cut and add by its volume delta. Prove a pattern pitch by a position: a pitch
  change does not change the volume.
- Pose-vs-shape test: a rigid refit of a part subset separates misalignment from model error
  (R385 pump).
- Known scan artefacts to budget for: filled interior corners, centre drift on cylinders with
  < 180° coverage, single-sheet regions, thickened wires and O-rings.
- Out of v1 scope for now (v0 HALTs on these too): multi-part assemblies (R385, Ulka) and
  freeform skins (Chest, Left Thigh). The NX package holds working recipes for both, so
  they are candidates for v2+.
