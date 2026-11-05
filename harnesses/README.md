# Harness versions

A harness is a complete, installable set of skills and scripts that turns a scan into a STEP.
Versions live side by side so they can be benchmarked against each other and across LLMs.

| Version | Status | Idea |
|---|---|---|
| [`v0`](v0/) | frozen (tag `harness-v0`, commit `29cb4cb`) | Plan-first linear pipeline: one-shot `params.json`, the agent writes `model.py`, independent verify. |
| [`v1`](v1/) | in development | JSON feature tree + generic builder, staged deviation loop with a scripted region classifier, decision cards. |

## Rules for every version

- `harnesses/<id>/HARNESS.json` is the manifest: `id`, `status`, `entry_skill`, `skills`,
  `doctor`, `selftests`, `python_deps`, `start_prompt`. `tools/harness.py` reads it.
- Versions may reuse skill names. Install exactly one version per skills directory:
  `python3 tools/harness.py install <id> [--dest DIR]`. The tool removes every other
  version's skills from `DIR` first.
- A frozen version is never edited except for repo-layout fixes that do not change behaviour.
  Behaviour changes go into a new version.
- Shared evidence stays at the repo root: `golden-examples/`, `baseline/`, `analysis/` and
  `QUESTIONS.md` (owner decisions).
- Skills and scripts stay model-agnostic: plain `SKILL.md` and Python CLIs that print JSON,
  with no dependency on one vendor's agent features. Where a version needs a fresh agent
  (for example independent verify), it says so in the skill text. Each agent CLI provides
  that its own way.
- From v1 on, every run writes `run_metrics.json` (see `v1/README.md`) for the benchmark.
