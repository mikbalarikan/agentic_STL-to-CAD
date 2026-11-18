# CLAUDE.md: standing instructions for this repo

This repo holds the `stl-re-*` skills (STL scan → design-intent parametric STEP) and their
evidence base. Read `README.md` for the skill index.

## A new reverse-engineering job ("yeni bir STL tersine mühendislik görevi")

1. Run the job with `skills/stl-re-orchestrate/SKILL.md` (intake → measure → rebuild → verify →
   deliver). Install the deps first if `init_run.py doctor` reports them missing:
   `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`.
2. Put the run folder outside the repo: the session scratchpad, or the job folder the owner names.
   Scans and run folders are never committed.
3. An instruction like "p95 plastik parça toleransı" means regime `baseline-skill`, class `plastic`
   (p95 ≤ 0.30 / max ≤ 0.80 mm). Record it as the owner's `REGIME` decision. Scan resolution and
   calipers still need the owner's answer (orchestrate §6). No calipers supplied → scan-only run
   (limitations: Tier-1 not run, scale not caliper-verified).
4. Verify runs in a fresh subagent (CHK-INDEP), never in the builder's context.

## Delivery format: standing owner decision, do NOT ask again

Every job ends with **one downloadable zip that contains all deliverables AND all source files**:

- Build it with `skills/stl-re-deliver/scripts/package_zip.py --run <run>` after
  `make_manifest.py`. The owner wants ONE `.zip` file, never parts.
  The layout (`deliverables/` + `source/` + `PACKAGE_INDEX.md`) and the exclusion rules are in
  `skills/stl-re-deliver/references/delivery-package.md`.
- Send the zip to the owner with `SendUserFile` (display `attach`), together with its `.sha256`
  and a short report: verdict, regime, the numbers read from `qa/gate.json`, loop count,
  limitations with their re-run triggers, and whether verify was independent. Uploads are limited to 30 MiB per
  file. `package_zip.py` keeps the zip under that by listing, not zipping, regenerable artefacts
  (npz arrays, self-check renders, superseded tessellations). Byte parts are only a last resort, when
  the script warns (`delivery-package.md`, "Size").
- For `BAND_NOT_MET`, the zip exists only after a recorded `ACCEPT-BAND`. Ask the owner first,
  showing the missed band and the options.

## After a real run

Record it under `evals/real-runs/<PART>.md` (+ a folder with DECISIONS, VERDICT, gate.json and an
overlay). Include inputs, decisions, the result and the skill defects found, following
`evals/real-runs/OD-H22.md`. Commit that record, not the run folder.
