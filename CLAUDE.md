# CLAUDE.md — agentic_STL-to-CAD

Standing instructions for every session in this repo. The owner (Ikbal) writes in Turkish;
answer in Turkish.

## An STL → CAD job

- Entry point: `skills/stl-re-orchestrate/SKILL.md`. The six `skills/stl-re-*` skills can be
  used in place from this repo (they call each other by relative path). Deps:
  `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`,
  then `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor`.
- Put the run folder outside the repo (cloud session: `<scratchpad>/jobs/<part>/`). Inputs are
  copied read-only by `init_run.py init`.
- Owner shorthand: "p95 plastik (parça toleransı)" = regime `baseline-skill`, class `plastic`
  (p95 ≤ 0.30 / max ≤ 0.80 mm). Record it as the owner's `REGIME` decision.
- No caliper sheet in the request = the owner wants a scan-only run: record the `MEASUREMENTS`
  decision and carry the two scan-only limitations (Tier-1 not run, scale not caliper-verified).
- Verify always runs in a fresh subagent (CHK-INDEP).

## Delivery format (standing owner decision, 2026-09-26; restated 2026-09-28)

Do not ask for it again. Every finished job is handed over as **one downloadable zip that holds
the deliverables and all source files of the run**:

1. `stl-re-deliver` steps 0–5 (preflight, limitations, repro, README, manifest).
2. `python3 skills/stl-re-deliver/scripts/package_zip.py --run <run>` →
   `<part>_RE_<VERDICT>_<date>.zip` + `.sha256` next to the run folder. Layout
   (`deliverables/`, `source/`, `PACKAGE_INDEX.md`) and exclusion rules:
   `skills/stl-re-deliver/references/delivery-package.md`.
3. Copy the zip and its `.sha256` into a folder the owner can open (cloud session: the
   scratchpad or the working directory) and send both with `SendUserFile` (`display: attach`),
   together with the verdict, regime, iteration (n of 3), limitations with re-run triggers,
   and whether verify was independent.
4. A `BAND_NOT_MET` verdict gets no zip until the owner's `ACCEPT-BAND` is recorded.

## After a real run

Record it under `evals/real-runs/<part>.md` (inputs, decisions, result, skill defects found)
with small copies of `DECISIONS.md`, `qa/gate.json`, `qa/VERDICT.md`, `deliver/README.md` and an
overlay PNG in `evals/real-runs/<part>/` (see `evals/real-runs/OD-H22.md`). Never commit the
scan, STEP files or the zip. Commit and push to the session's designated branch.
