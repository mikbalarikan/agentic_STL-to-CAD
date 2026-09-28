# agentic_STL-to-CAD — standing instructions for every session

This repo holds the `stl-re-*` skills (`skills/`) and the evidence they were built from. When the
owner hands you a scan (STL) + photos and asks for reverse engineering ("tersine mühendislik",
"STL → STEP/CAD"), run the job with the skills; do not improvise a pipeline.

## Standing owner decisions (do not ask again)

1. **Delivery format = ONE downloadable zip** with all deliverables AND all source files of the run
   (owner decision 2026-09-26, repeated 2026-09-28). Made by
   `skills/stl-re-deliver/scripts/package_zip.py` after `make_manifest.py`; layout and exclusions in
   `skills/stl-re-deliver/references/delivery-package.md`. Send the zip to the owner
   (`SendUserFile`, display `attach`) with the verdict, regime, iteration (n of 3), limitations with
   re-run triggers, and whether verify was independent. Never ask which format.
2. **Band regime shorthand.** "p95 plastik parça toleransı" / "plastic tolerance" = regime
   `baseline-skill`, material class `plastic` (p95 ≤ 0.30 / max ≤ 0.80 mm,
   `baseline/skills/stl2step-build123d/SKILL.md:87`). "machined" = p95 ≤ 0.15 / max ≤ 0.50.
   Record it as a `REGIME` line in the run's `DECISIONS.md` citing the owner's words
   (save the brief under `<run>/decisions/owner_brief.md`).
3. **No calipers given + "deliver when done"** = scan-only run: record a `MEASUREMENTS` scan-only line
   and carry the limitations "Tier-1 not run" and "absolute scale not caliper-verified".
4. A `BAND_NOT_MET` verdict still needs the owner's written `ACCEPT-BAND`
   (`skills/stl-re-orchestrate/SKILL.md` §4); ask for it with the numbers, do not self-accept.

## How to run a job in this environment

```bash
python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib scikit-image
S=/home/user/agentic_STL-to-CAD/skills          # the skills are used in place (not copied to ~/.claude/skills)
python3 $S/stl-re-orchestrate/scripts/init_run.py doctor
J=<scratchpad>/<PART>                           # job folder: run/ inside it, the zip lands next to run/
python3 $S/stl-re-orchestrate/scripts/init_run.py init $J/run --part <PART> --scan <scan.stl> \
    --photos <photo dir> --scan-resolution full|decimated|unknown
```

Then follow `skills/stl-re-orchestrate/SKILL.md` stage by stage (intake → measure → rebuild →
verify in a fresh subagent → deliver). Keep the run folder outside the repo (scans are large); after
delivery record a short real-run summary under `evals/real-runs/<PART>/` (VERDICT.md, gate.json,
README.md, DECISIONS.md, BUILDER_REPORT.md) and new skill gaps in `QUESTIONS.md`.

## Practical notes from real runs

- Large meshes: `trimesh.proximity` on a ~400k-face scan can be OOM-killed on a 15 GB box; use the
  skill scripts' sampling / KD-tree approach for self-checks.
- Assemblies and prismatic parts (PCBs, housings) need run-local measurement scripts under
  `<run>/measure/` (height map, per-part fits); keep them seeded and ship them in the zip
  (see `evals/real-runs/OD-E01/`).
