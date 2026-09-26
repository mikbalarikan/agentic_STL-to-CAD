# agentic_STL-to-CAD

Agentic STL→CAD reverse-engineering skills (`SKILL.md`, [agentskills.io](https://agentskills.io)
format), rebuilt from scratch by distilling successful projects. Every rule in the skills is
traced to evidence in `golden-examples/` or to the RE_SPEC in `baseline/`.

## Skills

| Skill | What it does | Use it when |
|---|---|---|
| [`stl-re-orchestrate`](skills/stl-re-orchestrate/SKILL.md) | Entry point. Creates the run folder, drives intake → measure → rebuild → verify → deliver, counts loops (max 3), handles supersede and verdict routing. Owns the shared [run contract](skills/stl-re-orchestrate/references/run-contract.md). | You are asked to turn a scan/STL/mesh into STEP/CAD, or to resume or check such a job. |
| [`stl-re-intake-datum`](skills/stl-re-intake-datum/SKILL.md) | Scan hash and health, working copy, scale/noise checks, feature enumeration, measurement request, declared band regime, and a named datum frame (`alignment.json`). | Start of every job, or when the datum must be redone. |
| [`stl-re-measure-intent`](skills/stl-re-measure-intent/SKILL.md) | Sections, primitive fits, R(θ) maps, pattern counts, caliper/photo authority with achievability checks (STRIKE/UNPROVEN), noise-bounded rounding → `params.json` + `PARAM_TABLE.md`. | After intake, before modelling, or to re-measure a flagged feature. |
| [`stl-re-rebuild-build123d`](skills/stl-re-rebuild-build123d/SKILL.md) | Modelling plan, build123d strategies, logged fillets, anti-patchwork census, single-solid validation, datum- and scan-frame STEP export. | Once `params.json` exists, or when a verdict sends the CAD back. |
| [`stl-re-verify`](skills/stl-re-verify/SKILL.md) | Independent QA: hash freeze, datum audit (report-only), Tier-1 on the STEP, own ICP, two-way full-res deviation with zones and named masks, observability, overlays, verdict under the declared regime. | After a rebuild, before delivery, ideally in a fresh agent. |
| [`stl-re-deliver`](skills/stl-re-deliver/SKILL.md) | README from the gate and params JSON, `MANIFEST.json` with hashes and roles, fresh-process reproducibility check, then ONE downloadable zip with deliverables + all source files ([delivery package](skills/stl-re-deliver/references/delivery-package.md)). Refuses stale or untrusted verdicts. | Only after verify wrote a trusted `qa/gate.json` and `VERDICT.md`. |

Verdicts: `APPROVED`, `APPROVED_WITH_LIMITATIONS`, `BAND_NOT_MET` (delivery needs a recorded
human `ACCEPT-BAND`), `REVISE`, `HALT`. The band regime (RE_SPEC, baseline-skill or a project
spec) is declared at intake and named in the verdict; there is no silent default.

## Install

The six skills are meant to sit side by side, because they call each other's scripts by
relative path (`../stl-re-<name>/scripts/...`).

```bash
git clone https://github.com/mikbalarikan/agentic_STL-to-CAD.git
mkdir -p ~/.claude/skills
cp -r agentic_STL-to-CAD/skills/stl-re-* ~/.claude/skills/
# or symlink to track the repo:  ln -s "$PWD"/agentic_STL-to-CAD/skills/stl-re-* ~/.claude/skills/

python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib
python3 ~/.claude/skills/stl-re-orchestrate/scripts/init_run.py doctor   # checks deps and siblings
```

Python 3.10+ is required. The skills were checked with build123d 0.13. FreeCAD is not
required; `stl-re-rebuild-build123d/references/freecad-equivalents.md` is a reference only.

Then ask Claude to convert a scan (for example "turn scan.stl into a STEP, calipers are in
MEASUREMENTS.md"), and `stl-re-orchestrate` takes it from there.

## Repository layout

- `skills/`: the six skills (this is what you install).
- `evals/`: per-skill eval cases (`evals/cases/`) and the blind replays against the baseline
  (`evals/replay/`). Read `evals/README.md` for how to run them and for the caveats.
- `analysis/`: the evidence base. Per-golden and per-baseline extractions, `SYNTHESIS.md`
  (rules, named checks, allowed numbers) and `SKILL_ARCHITECTURE.md`.
- `reviews/`: the independent review of each skill and the fixes applied.
- `QUESTIONS.md`: owner decisions, record conflicts and open evidence gaps.
- `PLAN.md`: how this version was produced.
- `golden-examples/`: successful RE projects (primary evidence). See its README.
- `baseline/`: the v0 skills and agent briefs being replaced (read-only).
- `prompts/cloud-kickoff-skills-v1.md`: project goal and run plan for the multi-agent
  skill-writing session.
