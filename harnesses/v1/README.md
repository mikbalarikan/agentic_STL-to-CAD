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
| M1 ✅ | `features/` library, profile sketcher, `feature_tree.json` schema, `build_tree.py` with per-node checks and rollback; port v0 intake/measure/verify/deliver scripts that do not change | the OD-H22 valve rebuilds from a hand-written tree with the same deviation as v0, with no `model.py`. **Met:** see "M1 result" below |
| M2 ⚠️ | observability fix, `deviate.py`, `clusters.py`, `classify.py`, `loop.py`, decision cards answered by the agent | OD-H22 and one golden part rebuild from datum + base body through the loop. **Partly met:** see "M2 result" below |
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

## M1 result

Code: `skills/stl-re-build/` (`scripts/treexpr.py`, `sketch2d.py`, `features.py`,
`build_tree.py`; schema in `references/feature-tree.md`). The OD-H22 acceptance tree is
`skills/stl-re-build/examples/od_h22/feature_tree.json`.

| | v0 `model.py` | v1 `feature_tree.json` |
|---|---|---|
| What the agent writes | 297 lines, 14.6 KB of Python | 109 lines, 6.9 KB of JSON (5.8 KB minified) |
| Geometry | 1 solid, 162 faces, 6395.5936 mm³ | identical: 162 faces, 6395.5936 mm³, symmetric difference 0.000000 mm³ (datum and scan frame) |
| Fillets | 5/5 OK | 5/5 OK (2 in the sketch as concave-vertex fillets, 3 logged in `fillets.json`) |
| scan→CAD (v0 deviation gate, same registration and masks) | p50 0.0677 / p95 0.2483 / max 1.4269 | p50 0.0677 / p95 0.2483 / max 1.4269 |
| observable CAD→scan | p95 1.4843 / max 4.858 | p95 1.4771 / max 4.858 (same geometry; the CAD surface sampling follows the STEP face order) |
| Unused params, tree literals | none | none |

Tests: `tests/test_features.py` 27/27 (expressions incl. injection refusals, arcs through both
end points, concave-vertex fillet, offset, draft, revolve, repeated cuts, rollback of a cut
that misses, a second solid caught, fillet fallback REDUCED, lint of fillet order, ruled-loft
refusal, unused params) and `tests/test_od_h22.py` PASS.

Note: authored size is a proxy for token use. Actual tokens per run will be measured by the
benchmark runner.

## M2 result

Code: `skills/stl-re-refine/`:
- `scripts/devmap.py`: signed deviation maps and clusters.
- `scripts/classify.py`: RANSAC hypotheses.
- `scripts/loop.py`: the loop.
- `scripts/cards.py`: decision cards.
- `scripts/compare.py`: like-for-like scoring against a reference STEP.

Observability: `skills/stl-re-verify/scripts/observability.py` gets the `sky` method (now the
default; `--obs-method cone` = v0).

### What the loop does

Each round:
1. Measure the signed scan→CAD deviation.
2. Split the red regions into clusters by sign.
3. Fit hypotheses by RANSAC to the subset of the cluster each one explains:
   - cylinder hole or boss (2-point RANSAC);
   - stepped revolve on the cylinder's axis;
   - prism along datum axes, normal eigen-directions and dominant normal directions, with a
     line/arc footprint from `sketchfit.auto_topology`, a rectangle, or a convex-hull
     rectangle, and draft ±;
   - offset pocket of an existing profile, inserted right after its parent node;
   - lathe cut about Z;
   - RANSAC plane cut.

   The cluster is also classified together with its same-sign neighbours.
4. Build every candidate for real. Keep one only if all of these hold:
   - J falls by at least 30 % of what its cluster could give;
   - it brings ≥ 60 % of the points it claims inside the threshold;
   - the build passes the builder's per-node checks.
5. Merge sibling clusters into one repeated node when the sizes match within 5 % and the axes
   are equal, mirrored or polar.

A short arc of small radius is recorded as a **blend candidate** and never built. A cluster
that fails 3 times becomes an **open point**.

### Results

Builder self-check, scored by `compare.py` with the same 150k scan samples and no ICP for both
models. Run records: `skills/stl-re-refine/examples/*/run_m2/`.

| Part | Start (base body) | Loop result | Reference | Rounds, builds, time |
|---|---|---|---|---|
| OD-H22 (base: flange prism + core revolve) | p95 13.996 | p95 0.345, 93.8 % of the scan within 0.30, CAD→scan p95 0.91, 149 faces, 1 open point (gussets) | v0 `model.py`: p95 0.235, 97.5 % within 0.30, CAD→scan p95 1.62, 162 faces | 18 rounds, 225 builds, 18 min |
| DRM screw cap, decimated scan (base: pentagon prism) | p95 2.018 | p95 0.741, 80.4 % within 0.30, 16 faces | golden STEP: p95 0.089, 100 % | 2 rounds, then no hypothesis helped |

**OD-H22: what it found.** Values in parentheses are v0's.
- Both ports as stepped revolves on their measured skew axes.
- The tray pocket as the outline offset by 1.483 (`rim_wall_t` 1.447), floor z 2.278 (2.26).
- The tube bore, r 4.530 (4.561).
- Both port bores, r 4.326 / 4.306 (4.339).
- Both ear holes, r 1.931 / 1.941 (1.936).
- The ends of the port clip blocks: full rounds of r ≈ 1.88, equal to half the block
  thickness. v0 assumed a box with 0.5 mm rounds (`port_block_corner_R`, source `assumed`).
  v0's own gate has max 0.675 mm in that zone (B4), which fits that difference.
- Late rounds (12–18) add small prisms and plane cuts that each lower J by < 1 %.

**DRM: what it found.** The through hole r 1.944 and a lathe cut. It did not find the drafted
pentagon frustum, the five dimples, the double-D flats or the counterbore.

**Acceptance.**
- OD-H22: rebuilt through the loop, but it does not meet the 0.30 band. It is 0.11 mm short of
  v0, which was measured by hand.
- DRM: not met.

**Observability fix (v0 defect #3).** The `sky` test needs two lines of sight at least 20°
apart, each within 65° of the normal. On v0's OD-H22 STEP it moved the observable CAD→scan p95
from 1.484 only to 1.405. The cause was measured: 66 % of the far CAD points lie on bores whose
depths are `assumed` params (`tube_bore_bottom_z`, `port_bore2_end_t`). Most of the rest lie
on the rib (`rib_half_len`, assumed). These surfaces are physically visible, so physics cannot
excuse them. The right fix is provenance: surfaces built from `assumed` params become a named
mask declared before grading. That is planned for M3.

### Open points carried to M3

1. **Design-intent merge.** The block ends were found as cylinder bosses (a 5-instance pattern
   plus one more). They should be one stadium (slot) prism per block along X. Needed: a
   stadium/slot footprint fit, and a merge step that rewrites a pattern of bosses on one body
   into that body.
2. **Gussets.** Thin plates whose footprint ends exactly at the CAD surface still give 2 solids,
   even with the silhouette bridge.
3. **Parameter re-fit.** The loop only adds features. A wrong size of an existing node (for
   example the revolve step ends) shows up as thin clusters and gets patched by late small
   prisms. Next: a "re-fit node" hypothesis that adjusts the params of the node that owns the
   face.
4. **Diminishing returns.** Rounds 12–18 on OD-H22 each lower J by < 1 %. A stricter gain rule,
   or a card to the agent/user for these, would stop the loop earlier with a cleaner tree.
5. **DRM-type parts.** Drafted polygonal frustums, tilted dimple cylinders and double-D flats
   need hypotheses for intersections with an envelope, tilted cylinder cuts, and pairs of
   parallel flats.
6. **Speed.** About 4.7 s per candidate build+measure on OD-H22. A cached CAD distance per
   unchanged region would cut that a lot.
7. **Masks from provenance** (see the observability paragraph).

Tests: `skills/stl-re-refine/tests/test_refine.py` 9/9. It builds a synthetic box with a hole,
a boss and a pocket, checks classify on each, then runs the loop from the bare box: exactly 3
features are accepted, and the final p95 is 0.0087 mm.
