# CLAUDE.md — standing instructions for every session in this repo

This repo holds the `stl-re-*` skills (`skills/`) that turn a scanned STL into a design-intent
STEP. When the owner hands you an STL (plus photos) and asks for a reverse-engineering job, run
`skills/stl-re-orchestrate/SKILL.md` end to end. The rules below are owner decisions; do not ask
for them again.

## Delivery format (owner decision 2026-09-26, restated 2026-09-28)

Every job ends with **one downloadable zip** that holds the deliverables **and** every source file
of the run. Details: `skills/stl-re-deliver/references/delivery-package.md`.

1. Finish the pipeline: verify writes `qa/gate.json` + `qa/VERDICT.md`, then `stl-re-deliver`
   runs preflight → `limitations.json` → `repro_check.py` → `make_readme.py` →
   `make_manifest.py`.
2. Package: `python3 skills/stl-re-deliver/scripts/package_zip.py --run <run> [--out-dir <job folder>]`.
   It writes `<part>_RE_<VERDICT>_<YYYY-MM-DD>.zip` + `.sha256` next to the run, with
   `deliverables/` (STEP datum + scan frame, CAD STL, README, MANIFEST, VERDICT, gate,
   PARAM_TABLE, DECISIONS, overlays) and `source/` (the rest of the run tree: scripts, JSON,
   figures, model.py, measurement scripts). Exclusions are listed in `PACKAGE_INDEX.md`, never
   silent. Add `--include-scan` when the owner does not already hold the raw scan.
3. Hand it over with `SendUserFile` (`display: "attach"`), together with the verdict word, the
   regime, the numbers read from `qa/gate.json`, the limitations with their re-run triggers, the
   loop count and whether verify was independent.
4. A `BAND_NOT_MET` run gets a zip only after the owner's `ACCEPT-BAND` is recorded
   (`skills/stl-re-orchestrate/references/run-contract.md` §10).

## How the owner phrases the band regime

- "p95 plastik parça toleransı", "tolerans = p95", "plastic tolerance" → regime
  `baseline-skill`, `material_class plastic` (p95 ≤ 0.30 / max ≤ 0.80 mm,
  `baseline/skills/stl2step-build123d/SKILL.md:87`). Record it as a `REGIME` line in
  `DECISIONS.md` citing the owner's words; it is declared, not a silent default.
- "machined" → the same regime with `material_class machined`. RE_SPEC or a project spec only
  when the owner says so or supplies calipers/spec.

## Running a job in a cloud session

- Put the run folder in the session scratchpad (`<scratchpad>/job/<part>_<name>/`), not in the
  repo: scans are large and the run is delivered as the zip. Deps: see `README.md` Install.
- Ask the owner once, at the start, what the pipeline needs and cannot infer: whether the STL
  is the full-resolution original, and calipers vs scan-only. Record each answer in
  `DECISIONS.md`.
- Run `stl-re-verify` in a fresh subagent (CHK-INDEP), giving it only the inputs listed in
  `skills/stl-re-orchestrate/SKILL.md` §5.
- After delivery, record the run under `evals/real-runs/<part>.md` (inputs, decisions, result,
  skill defects found) with its small records (`DECISIONS.md`, `VERDICT.md`, `gate.json`,
  `README.md`, one overlay) in `evals/real-runs/<part>/`, as `evals/real-runs/OD-H22.md` does.
  Skill defects go in its defect table with a status; fix them in the skills when the fix is
  small and clear.
