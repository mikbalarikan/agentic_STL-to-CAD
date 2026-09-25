# Mission: rebuild the STL→CAD reverse-engineering skills from evidence

You are the **orchestrator** (Fable 5.1) of a multi-agent run in the repo
`mikbalarikan/agentic_STL-to-CAD`. I opt in to multi-agent orchestration: fan
out parallel subagents (Agent tool / workflows) as described below.

## Goal

Write a new, higher-quality set of **agent skills** (agentskills.io format:
`skills/<name>/SKILL.md` + optional `references/`, `scripts/`) for
**reverse-engineering a scanned STL mesh into clean, design-intent, parametric
CAD (STEP)**. Write them **from scratch**: the old skills are a baseline to
beat, not a draft to edit. Every rule in the new skills must be earned from
evidence in the successful projects.

## Inputs (read `README.md`, `baseline/README.md`, `golden-examples/README.md` first)

- `baseline/`: the v0 doctrine being replaced: skills `stl2step-build123d`,
  `stl2step-freecad`, `stl2dxf-facet-film`; agent briefs `re-planner`,
  `re-drafter`, `re-qa-verifier`; the OOMWOO RE pipeline (`RE_SPEC.md` with
  tolerance bands in §4, v3/v4 change logs, templates, `TRACKER.md` which
  includes failures).
- `golden-examples/`: 6 successful projects, the **primary evidence**.
  `M02-02-03` gear, `OOM-B02` side brush, `OOM-P03` mop bracket,
  `dreame_brush-caps` (2 parts), `OD-H12` pump: full records.
  `OOM-E01` battery: **stub, ignore it for method.**
  Each has `MANIFEST.json` (every source file with sha256, and why excluded
  files are missing).

Evidence caveats you must respect:
- `*_scan_decimated.stl` are 950k-tri copies (max dev ≤0.028 mm). They are fine
  for inspection. Official deviation numbers in the records came from the
  full-res originals (not in the repo). Never "re-grade" a project on a
  decimated scan.
- Record honesty matters: OD-H12 **missed** its deviation band (p95 0.448 vs
  ≤0.30) and explains why. OOM-B02 passed with 3 declared limitations.
  OOM-P03 it1 was REVISE. Learn from gaps and failures. Never paint them
  as passes.
- `stl2dxf-facet-film` is a different product (flat DXF film kits). It is out
  of scope as a deliverable. Mine it only for transferable rules (gates,
  evidence discipline, method-synthesis style).

## Scope decisions (defaults; flag disagreement in `QUESTIONS.md`)

- Target toolchain: **Python + trimesh (analysis) + build123d/OCP (rebuild)**.
  Every golden example used it. FreeCAD becomes, at most, a short
  `references/` appendix, not a parallel skill.
- Language: English for all skills.
- Units mm. Tolerances and bands come **only** from `RE_SPEC.md` or golden
  records. Never invent a number. If evidence conflicts or is missing, write it
  to `QUESTIONS.md` and move on.
- Do **not** modify anything under `golden-examples/` or `baseline/`.

## Model routing (use the Agent tool's `model` parameter)

| Work | Model |
|---|---|
| You: planning, cross-project synthesis, skill architecture, final judgment, merging agent output | **Fable 5.1** (you) |
| Deep per-project evidence extraction, skill drafting, independent skill review, replay tests | **Opus 5.5**, launched **in parallel** (one message, many Agent calls) |
| Mechanical work: file inventories, tabulating JSON metrics into tables, applying review fixes you already decided, link/citation checks | **Sonnet** |
| Trivial reads: listing, grep, counting, frontmatter/format lint | **Haiku** |

Context discipline: every subagent writes its full output to a file in the
repo and returns only a ≤250-word summary plus the file path. Give each
subagent a self-contained brief: it does not see this conversation. Budget:
about 25 agents in total. Do not duplicate work an agent is already doing.

## Phases

**Phase 0: Setup.** Branch `feat/skills-v1`. Write `PLAN.md` (phases,
agent roster with models, file outputs). Commit and push.

**Phase 1: Evidence extraction (parallel).**
- 5× Opus, one per full golden example, output
  `analysis/golden/<project>.md` using one fixed schema: part class and
  geometry type · stages actually run, in order · datum/alignment method (with
  numbers) · measurement methods (sections, fits, histograms) · design-intent
  rounding (measured→chosen) · feature tree · gates run with actual numbers ·
  iterations: what failed, why, what fixed it · declared limitations and
  assumptions · where it deviated from the baseline skill and whether that
  helped · reusable code (file:function, what it does) · lessons.
  Every claim cites a path in the project folder.
- 3× Opus (or Sonnet if thin), one per baseline group (build123d+freecad
  skills · RE agents + RE_SPEC + TRACKER · facet-film for transferable rules),
  output `analysis/baseline/<group>.md`: rules, gates, gaps, internal
  contradictions, rules the golden evidence contradicts.
- Haiku/Sonnet for any pure inventory work the Opus agents would otherwise
  burn tokens on.

**Phase 2: Synthesis (you).** `analysis/SYNTHESIS.md` holds a cross-project
matrix. Something done in ≥2 successes is a **rule**; single-case is a
**heuristic** (labelled); contradicted baseline rules are **dropped with
reason**; failure modes get a **named check**.
`analysis/SKILL_ARCHITECTURE.md` holds the proposed skill set: names,
trigger descriptions, boundaries, hand-offs, what goes in SKILL.md vs
`references/` vs `scripts/`. A likely shape (decide from evidence): an
orchestrating state-machine skill, plus skills for intake/datum, measurement
and design-intent extraction, build123d rebuild, deviation gate and
verification (incl. visibility masking), and delivery/report.
Commit and push, then **STOP and post the architecture summary for my
approval.** Do not draft skills before I approve.

**Phase 3: Drafting (parallel, after approval).** One Opus agent per skill.
Requirements:
- Frontmatter `name` and `description`. The description says what it does and
  exactly when to trigger.
- SKILL.md body ≤ ~500 lines. Use progressive disclosure into `references/`.
- Imperative, operational steps. State the concrete gate thresholds with
  their source. Name the failure checks. Say what to do when a gate fails
  (bounded iterations, honest verdict).
- `scripts/` lifts proven code from golden examples (generalised, typed,
  deterministic: seeds fixed, no wall-clock), with a provenance header naming
  the source file.
- Every non-obvious rule cites evidence
  (`golden-examples/<p>/<file>` or `analysis/...`).

**Phase 4: Review and replay (parallel).**
- One independent Opus reviewer per skill (not its author) checks for:
  evidence-backed rules, no invented numbers, clear triggers, no overlap or
  gaps between skills, and whether an agent could execute it cold. Output
  `reviews/<skill>.md` with a verdict of APPROVE or REVISE. Max 2 revise
  rounds. Sonnet applies fixes you accept.
- Haiku/Sonnet lint: frontmatter valid, all relative links and cited paths
  exist, script syntax (`python -m py_compile`).
- **Blind replay** (Opus, ≥2 golden examples, e.g. `dreame_brush-caps` screw
  cap and `M02-02-03`): give the agent only the scan (+ photos/measurements if
  the project had them) and the **new** skills, **not** the project record.
  Ask for the intake card, datum plan, and feature tree/modeling plan. If
  build123d installs in this environment (`pip install build123d trimesh`),
  go as far as a STEP and run the deviation gate on the decimated scan,
  labelled as such. Compare against the real record in
  `evals/replay/<project>.md`. Run the same replay with the **baseline**
  skill for an honest before/after.

**Phase 5: Evals and PR.** `evals/`: ≥3 cases per skill (inputs, expected
behaviour, pass criteria) drawn from golden examples. Record the baseline
honestly and never tune a case to the skill. Update root `README.md` (skill
index + how to install into `~/.claude/skills`). Open a PR to `main` with a
summary: skills, evidence coverage, replay before/after, open questions. Do
**not** merge.

## Standing rules

- Small commits: `area: imperative summary` (areas: `analysis`, `skills/<name>`,
  `evals`, `docs`). Push after every phase. No session ends with unpushed work.
- Ask, don't invent: gaps go to `QUESTIONS.md` and that thread stops. The run
  continues on other threads.
- Determinism and replayability for any script you ship.
- Report outcomes faithfully. If a replay fails or a skill is weaker than
  baseline somewhere, say so in the PR.
