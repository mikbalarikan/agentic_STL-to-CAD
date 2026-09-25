# Working conventions for this repo

## New STL → CAD job (a scan + photos arrives in a session)

Use the `stl-re-*` skills in `skills/` (entry point `skills/stl-re-orchestrate/SKILL.md`).
Owner standing decisions, so they are not asked again every session:

- **Run folder:** `runs/<part-id>_<short-name>/` (git-ignored; scans and STEP files do not go
  into git). Create it with `python3 skills/stl-re-orchestrate/scripts/init_run.py init ...`.
- **Tolerance words:** "p95 plastik parça toleransı" = regime `baseline-skill`, class `plastic`
  (p95 ≤ 0.30 / max ≤ 0.80 mm). Record it as a `REGIME` line in `DECISIONS.md`.
- **Deliver format: one zip.** Every finished job is handed over as a single downloadable zip
  with all source files and the deliverables:
  `python3 skills/stl-re-deliver/scripts/package_zip.py --run runs/<run>` →
  `runs/<run>_delivery.zip` (+ `.sha256`), sent to the user as a file (`SendUserFile`).
  Details: `skills/stl-re-deliver/SKILL.md` step 6.
- **Repo record:** after delivery, copy the small records (VERDICT.md, gate.json, DECISIONS.md,
  deliver/README.md, a builder report, one overlay PNG) to `evals/real-runs/<part>/`, add
  `evals/real-runs/<part>.md` (inputs, result, skill defects found), commit and push. Never
  commit the zip or the meshes.
- **Verify independence:** run `stl-re-verify` in a fresh subagent, as the orchestrator skill says.

## Environment notes

- Deps: `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`,
  then `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor`.
- Script CLIs use argparse: pass negative numbers as `--flag=-1.5,...`.
