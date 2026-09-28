# CLAUDE.md — standing rules for every session in this repo

## A new STL → CAD job ("yeni bir STL tersine mühendislik görevi")

1. Drive it with `skills/stl-re-orchestrate/SKILL.md` (it calls the other five `stl-re-*` skills).
   In a cloud session the skills are not installed under `~/.claude/skills`; run their scripts
   from `skills/stl-re-*/scripts/` directly. Install deps once:
   `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`,
   then `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor`.
2. Put the run folder in the session scratchpad (`<scratchpad>/runs/<part>/`), never inside the repo.
3. Owner shorthand for the band regime: "p95 plastik parça toleransı" = `baseline-skill`, class
   `plastic` (p95 ≤ 0.30 / max ≤ 0.80 mm). Record it as the owner's `REGIME` decision. No calipers
   given = scan-only (`MEASUREMENTS` decision).
4. Verify runs in a separate agent (CHK-INDEP); the builder never grades its own model.

## Delivery format (owner decision 2026-09-26, standing — do not ask again)

The job is handed over as **one downloadable zip with the deliverables and all source files**:
`<part>_RE_<VERDICT>_<YYYY-MM-DD>.zip` from `skills/stl-re-deliver/scripts/package_zip.py`
(layout and exclusions: `skills/stl-re-deliver/references/delivery-package.md`).

- Build it only after `make_manifest.py` succeeded (the CHK-PUBLISH / ACCEPT-BAND rules still apply).
- Copy the zip and its `.sha256` into the scratchpad `outputs/` folder and send it to the owner
  with `SendUserFile` (`display: "attach"`), together with the verdict, regime, numbers read from
  `qa/gate.json`, limitations with re-run triggers, loop count and whether verify was independent.
- Reply to the owner in the language they wrote in (usually Turkish).

## Record the real run in the repo

After delivery, copy the run's records (not the STEP/STL, not the scan) to
`evals/real-runs/<part>/` — `DECISIONS.md`, `BUILDER_REPORT.md`, `deliver/README.md`,
`qa/VERDICT.md`, `qa/gate.json`, one overlay PNG — and write `evals/real-runs/<part>.md`
(inputs, decisions, result, skill defects found) in the style of `evals/real-runs/OD-H22.md`.
Commit and push on the session's designated branch.
