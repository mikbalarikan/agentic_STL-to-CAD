# Standing instructions for Claude sessions in this repo

This repo holds the `stl-re-*` skills (STL scan → parametric STEP). Read this before any
reverse-engineering job so the owner never has to repeat these points.

## A new STL → STEP job ("yeni bir STL tersine mühendislik görevi")

1. Install the skills side by side and check the deps (once per container):
   ```bash
   mkdir -p ~/.claude/skills
   for d in "$PWD"/skills/stl-re-*; do ln -sfn "$d" ~/.claude/skills/$(basename "$d"); done
   python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib
   python3 ~/.claude/skills/stl-re-orchestrate/scripts/init_run.py doctor
   ```
2. Drive the job with `skills/stl-re-orchestrate/SKILL.md` (intake → measure → rebuild →
   independent verify in a subagent → deliver).
3. Put the run folder outside the repos, in the session's working directory
   (e.g. `/home/user/re_runs/<part>/`), and pass the attached photos with `--photos`.

## Standing owner decisions (do not ask again)

- **Delivery = ONE downloadable zip** with the deliverables AND all source files of the run,
  written by `skills/stl-re-deliver/scripts/package_zip.py` (layout:
  `skills/stl-re-deliver/references/delivery-package.md`). Send it with `SendUserFile`
  (`display: attach`) together with the report (verdict, regime, numbers from `qa/gate.json`,
  limitations with re-run triggers, loop count, verify independence). Owner decision 2026-09-26,
  restated 2026-09-30.
- **"p95 plastik parça toleransı" / "tolerans = p95"** = regime `baseline-skill`, material class
  `plastic`: p95 ≤ 0.30 / max ≤ 0.80 mm. Record it as a `REGIME` line citing the owner's message.
- **STL + photos, no measurements** = scan-only run: record a `MEASUREMENTS` line and carry the
  "Tier-1 not run" and "absolute scale not caliper-verified" limitations. Photos are for feature
  identification only.
- **Scan resolution**: if the owner did not say, ask once (one question) whether the STL is the
  original full-resolution export; record the answer as an `OTHER` line.

## After a job

- Record the run under `evals/real-runs/<part>.md` (inputs, decisions, result, skill defects
  found and their status), with the small text records (DECISIONS, VERDICT, gate/params JSON,
  specs) under `evals/real-runs/<part>/`. No STEP/STL/scan files in this repo.
- Skill fixes found during a run go in the skill itself with a provenance note, plus a line in
  that real-run record.
