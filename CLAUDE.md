# Working in this repo

## A new STL → CAD job (scan + photos from the owner)

- Run it with the skills in `skills/` (entry point `skills/stl-re-orchestrate/SKILL.md`).
  Install deps first if `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor` fails:
  `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`.
- Put the run folder in the session scratchpad (the owner can open it there), not in the repo.
- "p95 plastik parça toleransı" = regime `baseline-skill`, `material_class` plastic
  (p95 ≤ 0.30 / max ≤ 0.80 mm). No calipers given = scan-only (`MEASUREMENTS` entry).
- Verify runs in a separate agent (CHK-INDEP), never in the builder's context.
- A `BAND_NOT_MET` needs the owner's written `ACCEPT-BAND` before deliver; ask, don't assume.

## Delivery format (standing owner request, 2026-09-25)

Every finished job is delivered as **one downloadable zip with all source files and all
deliverables**. Do not ask again each session:

1. Finish `stl-re-deliver` (README, repro, MANIFEST).
2. `python3 skills/stl-re-deliver/scripts/package_zip.py --run <run>` → `<run>/../<part>_delivery.zip`
   (layout: `DELIVERY.md`, `deliverables/`, `run/`, `skill_scripts/`; see
   `skills/stl-re-deliver/SKILL.md` step 6).
3. Send the zip to the owner as a downloadable file (`SendUserFile` in cloud sessions).
4. Copy the run's small text records (README, VERDICT, DECISIONS, gate.json, builder report,
   one overlay) to `evals/real-runs/<part>/`, add `evals/real-runs/<part>.md` (inputs,
   decisions, result, skill defects found), then commit and push. The scan, STEP files and the
   zip stay out of git.
