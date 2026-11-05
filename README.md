# agentic_STL-to-CAD

Agentic STL→CAD reverse-engineering harnesses. A harness is a set of skills (`SKILL.md`,
[agentskills.io](https://agentskills.io) format) plus Python scripts that turn a scanned mesh
into a design-intent parametric STEP with build123d. Several harness versions live side by
side so they can be compared with each other and across LLMs.

| Version | Status | Idea |
|---|---|---|
| [`v0`](harnesses/v0/) | frozen (tag `harness-v0`) | Plan-first linear pipeline: intake → measure (one-shot `params.json`) → rebuild (agent writes `model.py`) → independent verify → deliver. |
| [`v1`](harnesses/v1/) | in development | JSON feature tree + generic builder, staged deviation loop with a scripted region classifier, decision cards (agent or user as arbiter). Design: [`harnesses/v1/README.md`](harnesses/v1/README.md). |

## Install a version

Only one version may be installed in a skills directory at a time, because versions reuse
skill names. The installer removes every other version's skills first.

```bash
git clone https://github.com/mikbalarikan/agentic_STL-to-CAD.git
cd agentic_STL-to-CAD
python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib

python3 tools/harness.py list
python3 tools/harness.py install v0                 # into ~/.claude/skills (or --dest DIR, --link)
python3 tools/harness.py doctor v0                  # checks deps and sibling skills
python3 tools/harness.py selftest v0
```

Python 3.10+ is required. v0 was checked with build123d 0.13. FreeCAD is not required.

Then ask the agent to convert a scan (for example "turn scan.stl into a STEP, calipers are in
MEASUREMENTS.md"). The version's entry skill (`stl-re-orchestrate`) takes it from there. An
agent opened in this repo reads [`AGENTS.md`](AGENTS.md), so "use v0" or "use v1" is enough.

## v0 at a glance

Six skills: [`stl-re-orchestrate`](harnesses/v0/skills/stl-re-orchestrate/SKILL.md) (entry,
state machine, [run contract](harnesses/v0/skills/stl-re-orchestrate/references/run-contract.md)),
[`stl-re-intake-datum`](harnesses/v0/skills/stl-re-intake-datum/SKILL.md),
[`stl-re-measure-intent`](harnesses/v0/skills/stl-re-measure-intent/SKILL.md),
[`stl-re-rebuild-build123d`](harnesses/v0/skills/stl-re-rebuild-build123d/SKILL.md),
[`stl-re-verify`](harnesses/v0/skills/stl-re-verify/SKILL.md) and
[`stl-re-deliver`](harnesses/v0/skills/stl-re-deliver/SKILL.md).

Verdicts: `APPROVED`, `APPROVED_WITH_LIMITATIONS`, `BAND_NOT_MET` (delivery needs a recorded
human `ACCEPT-BAND`), `REVISE`, `HALT`. The band regime (RE_SPEC, baseline-skill or a project
spec) is declared at intake and named in the verdict; there is no silent default.

## Repository layout

- `harnesses/`: one folder per version, each with a `HARNESS.json` manifest
  ([rules](harnesses/README.md)).
  - `v0/skills/`: the six v0 skills.
  - `v0/evals/`, `v0/reviews/`, `v0/examples/`, `v0/PLAN.md`, `v0/prompts/`: how v0 was
    produced, evaluated and reviewed. The worked example is the OD-H22 valve run.
  - `v1/`: the version under development.
- `tools/harness.py`: list, install, check and self-test a version.
- `bench/`: the planned model-agnostic benchmark across harness versions and LLMs.
- `analysis/`: the evidence base. Per-golden and per-baseline extractions, `SYNTHESIS.md`
  (rules, named checks, allowed numbers) and `SKILL_ARCHITECTURE.md`.
- `QUESTIONS.md`: owner decisions, record conflicts and open evidence gaps (shared by all
  versions).
- `golden-examples/`: successful RE projects (primary evidence, read-only). See its README.
- `baseline/`: the pre-v0 skills and agent briefs (read-only).
- NX reference projects (scripts, logs, transcripts of the NX-based RE work) are on branch
  `nx-re-intake` under `nx-reference/`, kept off `main` because of their size.
