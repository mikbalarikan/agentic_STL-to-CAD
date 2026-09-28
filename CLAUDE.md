# CLAUDE.md — standing instructions for every session in this repo

## STL → CAD (STEP) reverse-engineering jobs

When the owner attaches an STL/scan (with or without photos) and asks for CAD/STEP:

1. **Use the skills in `skills/`**, entry point `skills/stl-re-orchestrate/SKILL.md`. They sit side by
   side and call each other by relative path, so they run from `skills/` directly (no copy to
   `~/.claude/skills` needed). Install deps first if `init_run.py doctor` says so:
   `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`
   then `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor`.
2. **Run folder** in the session scratchpad (`<scratchpad>/jobs/<part>/`), created with
   `init_run.py init`. Never write run folders into the repo.
3. **Tolerance phrases.** "p95 plastik (parça) toleransı" / "p95 plastic" = regime `baseline-skill`,
   `material_class plastic` (p95 ≤ 0.30 / max ≤ 0.80 mm). "machined/metal" = `baseline-skill machined`.
   Record it as a `REGIME` line in `DECISIONS.md` citing the owner's message. No calipers in the
   message = scan-only (`MEASUREMENTS` line, limitations "Tier-1 not run", "scale not caliper-verified").
4. Ask only what the skills say must be asked (e.g. full-res scan? one fused solid vs multi-body?);
   record every answer in `DECISIONS.md`.
5. **Verify in a fresh subagent** (CHK-INDEP, orchestrate §5), never in the builder's context.

## Delivery format (owner decision 2026-09-26 — do not ask again)

Every job ends with **ONE downloadable zip** holding the deliverables **and all source files** of the
run: `skills/stl-re-deliver/scripts/package_zip.py`, layout and exclusions in
`skills/stl-re-deliver/references/delivery-package.md`. Send the zip to the owner with
`SendUserFile` (`display: attach`) together with the verdict, regime, numbers read from
`qa/gate.json`, limitations and the loop count. For `BAND_NOT_MET`, the zip is made only after a
recorded `ACCEPT-BAND`.

## After a real run

- Record it under `evals/real-runs/<part>.md` (+ `evals/real-runs/<part>/` with DECISIONS.md,
  VERDICT.md, gate.json, an overlay) the way `evals/real-runs/OD-H22.md` does, including the table of
  skill defects found and their status.
- Fix skill defects you hit in `skills/` (small, backward compatible, documented in the skill's
  SKILL.md/references) and add open owner questions to `QUESTIONS.md`.
- Never commit scans, STEP files or zips to the repo (they go to the owner in the zip).
- Develop on the session's designated branch; commit and push when done.
