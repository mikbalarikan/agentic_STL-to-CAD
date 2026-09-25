# PLAN — skills v1 (STL → design-intent parametric STEP)

Run plan: `prompts/cloud-kickoff-skills-v1.md`. This file records how the run
is executed: phases, agent roster, models, and file outputs.

Branch: `claude/skills-v1-kickoff-mtk1l9` (the session's designated branch;
the prompt names `feat/skills-v1`, but this environment only pushes to the
designated branch. Rename at PR time if wanted).

## Phases and outputs

| Phase | What | Output | Gate |
|---|---|---|---|
| 0 Setup | branch, plan, inventory, extraction schema | `PLAN.md`, `analysis/INVENTORY.md`, `analysis/golden/_SCHEMA.md` | pushed |
| 1 Evidence | 5 golden extractions + 3 baseline audits, in parallel | `analysis/golden/<project>.md`, `analysis/baseline/<group>.md` | every claim cites a path |
| 2 Synthesis | cross-project matrix; rule / heuristic / dropped / named checks; skill architecture | `analysis/SYNTHESIS.md`, `analysis/SKILL_ARCHITECTURE.md`, `QUESTIONS.md` | **STOP: user approves architecture** |
| 3 Drafting | one author per skill | `skills/<name>/SKILL.md` + `references/`, `scripts/` | ≤~500 lines, cited rules |
| 4 Review + replay | independent reviewer per skill; lint; blind replay new vs baseline | `reviews/<skill>.md`, `evals/replay/<project>.md` | APPROVE, ≤2 revise rounds |
| 5 Evals + PR | ≥3 eval cases per skill, README index, PR to `main` (not merged) | `evals/`, `README.md` | PR open |

## Agent roster (budget ≈ 25)

| # | Phase | Agent | Model | Output |
|---|---|---|---|---|
| 1 | 1 | golden: `M02-02-03_watertight-design-intent` | Opus | `analysis/golden/M02-02-03.md` |
| 2 | 1 | golden: `OD-H12_delonghi-dedica-pump` | Opus | `analysis/golden/OD-H12.md` |
| 3 | 1 | golden: `OOM-B02_side-brush-3-arm` | Opus | `analysis/golden/OOM-B02.md` |
| 4 | 1 | golden: `OOM-P03_mop-pad-bracket` | Opus | `analysis/golden/OOM-P03.md` |
| 5 | 1 | golden: `dreame_brush-caps` | Opus | `analysis/golden/dreame_brush-caps.md` |
| 6 | 1 | baseline: `stl2step-build123d` + `stl2step-freecad` | Opus | `analysis/baseline/stl2step-skills.md` |
| 7 | 1 | baseline: RE agents + `oomwoo-re-pipeline` (RE_SPEC, TRACKER, changes, templates) | Opus | `analysis/baseline/oomwoo-re-pipeline.md` |
| 8 | 1 | baseline: `stl2dxf-facet-film` (transferable rules only) | Opus | `analysis/baseline/facet-film-transferable.md` |
| 9–14 | 3 | one author per approved skill (count set by architecture) | Opus | `skills/<name>/` |
| 15–20 | 4 | one independent reviewer per skill | Opus | `reviews/<skill>.md` |
| 21 | 4 | lint (frontmatter, links, cited paths, py_compile) | Haiku | `reviews/_lint.md` |
| 22–23 | 4 | blind replay: new skills vs baseline, ≥2 projects | Opus | `evals/replay/<project>.md` |
| 24 | 4 | apply accepted review fixes | Sonnet | edits |
| 25 | 5 | eval cases + README index | Sonnet | `evals/`, `README.md` |

The OOM-E01 stub is ignored for method. Pure inventory was done by the
orchestrator with `find`/`stat` (`analysis/INVENTORY.md`) instead of spending
an agent on it.

## Rules every agent gets

- Do not modify `golden-examples/` or `baseline/`. Do not commit or push (the
  orchestrator commits).
- Write the full output to the named file; return ≤250 words + the path.
- Every claim cites a repo path. Never invent a number; gaps go to a
  `## Questions` section of the output, which the orchestrator merges into
  `QUESTIONS.md`.
- `*_scan_decimated.stl` are inspection copies. Never re-grade a project on them.
- Record honesty: misses, REVISE iterations and limitations stay as they are.
