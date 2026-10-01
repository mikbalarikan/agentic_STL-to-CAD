# CLAUDE.md — agentic_STL-to-CAD

Standing instructions for every session in this repo. The owner should never have to repeat them.

## A new STL → CAD job

- Run the job with the skills in `skills/` (entry point `skills/stl-re-orchestrate/SKILL.md`).
  Install the Python deps listed in `README.md` and run `init_run.py doctor` first.
- Put the run folder outside the repo (cloud sessions: `/home/user/runs/<part>`). Never commit a
  run folder, scan or zip; commit only the short record under `evals/real-runs/` (see `OD-H22.md`).
- Decisions the owner did not state (regime, scan-only, inspection-only scan) are recorded in the run's
  `DECISIONS.md` as "delegated to agent" with the reason, and repeated in the final report.

## Delivery format (standing owner decision — do not ask again)

Every job ends with **ONE downloadable zip holding the deliverables and all source files**
(`skills/stl-re-deliver/references/delivery-package.md`):

```bash
python3 skills/stl-re-deliver/scripts/package_zip.py --run <run> --out-dir <dir> --include-scan
```

- `--include-scan`: the owner asked for *all* source files (2026-09-30), so the input scan ships too.
- Cloud sessions: write the zip (and its `.sha256`) to the session scratchpad or the working directory
  — only those are downloadable — and hand it over with `SendUserFile` (`display: "attach"`), together
  with the verdict, regime, iteration, limitations and whether verify was independent.
- The zip exists only after `make_manifest.py` succeeded (CHK-PUBLISH, ACCEPT-BAND, repro enforced).
