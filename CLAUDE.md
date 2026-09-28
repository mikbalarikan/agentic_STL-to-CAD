# CLAUDE.md — standing instructions for this repo

## STL → CAD jobs

When the owner hands over a scan (STL/mesh), optionally with photos or calipers, and asks for CAD/STEP,
run the `stl-re-*` skills in `skills/` starting at `skills/stl-re-orchestrate/SKILL.md` (install steps
and the skill index are in `README.md`). Put the run folder outside the repo (e.g. the session
scratchpad); only the run record goes into the repo (below).

## Delivery format (owner decision 2026-09-26, standing; do not ask again)

Every job is handed over as **one downloadable zip** that holds the deliverables **and** all source
files of the run:

- Built by `skills/stl-re-deliver/scripts/package_zip.py --run <run>` after `make_manifest.py`
  (layout, exclusions and naming: `skills/stl-re-deliver/references/delivery-package.md`).
- Name: `<part>_RE_<VERDICT>_<YYYY-MM-DD>.zip`, next to the run folder, plus `<zip>.sha256`.
- Send it to the owner with SendUserFile (`display: attach`) together with the verdict, the regime,
  the key gate numbers (read from `qa/gate.json`), the limitations with re-run triggers and the loop
  count.
- Pass `--include-scan` only when the owner does not already have the scan.
- A `BAND_NOT_MET` run is zipped only after a recorded `ACCEPT-BAND` (orchestrate §4).

## Record each real run

After delivery, add `evals/real-runs/<part>.md` (inputs, decisions, result, skill defects found) and
copy the small records (`DECISIONS.md`, `VERDICT.md`, `gate.json`, README, an overlay) under
`evals/real-runs/<part>/`, as done for OD-H22. Commit on the session's designated branch.

## Owner shorthand seen so far

- "p95 plastik parça toleransı" / "tolerans = p95" → regime `baseline-skill`, material class
  `plastic` (p95 ≤ 0.30 / max ≤ 0.80 mm), declared at intake and recorded in `DECISIONS.md`.
- No calipers supplied → scan-only run (limitations: Tier-1 not run, scale not caliper-verified).
