# CLAUDE.md — standing instructions for every session in this repo

## STL → CAD reverse-engineering jobs

When the owner attaches a scan (STL/mesh) and asks for CAD/STEP ("yeni bir STL tersine
mühendislik görevi", "turn this scan into STEP", …), run the `stl-re-*` skills in `skills/`
starting with `skills/stl-re-orchestrate/SKILL.md` (install: `README.md` → Install; the doctor is
`python3 skills/stl-re-orchestrate/scripts/init_run.py doctor`).

### Delivery format (owner decision 2026-09-26, re-confirmed 2026-09-30) — do not ask again

Every job is handed over as **one downloadable zip** that holds the deliverables **and all source
files** of the run:

- Built by `skills/stl-re-deliver/scripts/package_zip.py --run <run>` after `make_manifest.py`;
  layout and exclusions: `skills/stl-re-deliver/references/delivery-package.md`.
- `<part>_RE_<VERDICT>_<YYYY-MM-DD>.zip` (+ `.sha256`) with `deliverables/` (STEP datum + scan
  frame, CAD STL, README, VERDICT, gate.json, PARAM_TABLE, MANIFEST, repro.json, DECISIONS) and
  `source/` (the whole run tree: inputs' hashes, intake/measure/build/qa scripts and JSON).
  Every excluded file (raw scan, large regenerable meshes) is listed in `PACKAGE_INDEX.md`.
- `SendUserFile` refuses large files (a 49 MiB zip was refused, 16 MiB parts went through, 2026-10-02):
  if the zip is too big, send it as standalone part zips of ≤ ~20 MiB (deliverables / scan-frame
  STEP / current source / superseded source), each unpacking into the same folder tree; keep the
  full zip next to the run folder.
- Send the zip to the owner with `SendUserFile` (`display: attach`) together with the verdict,
  regime, numbers from `qa/gate.json`, limitations with re-run triggers, loop count and whether
  verify was independent (`skills/stl-re-orchestrate/SKILL.md` §8).
- CHK-PUBLISH still applies: no zip before a deliverable verdict (`BAND_NOT_MET` needs a recorded
  `ACCEPT-BAND` first).

### Owner shorthand

- "p95 plastik parça toleransı" = regime `baseline-skill`, material class `plastic`
  (p95 ≤ 0.30 mm / max ≤ 0.80 mm, `intake.py regime --name baseline-skill --class plastic`).
  Record it as the `REGIME` line in the run's `DECISIONS.md`.
- No caliper sheet attached = scan-only run (record a `MEASUREMENTS` entry and carry the two
  scan-only limitations). A scan file named `*decimated*` = inspection-only grading
  (`--scan-resolution decimated`), verdict capped at `APPROVED_WITH_LIMITATIONS`.

### Where runs live

Run folders are working state, not repo content: create them outside the repo (e.g. the session
scratchpad) and deliver through the zip. Findings that should change the skills go to
`QUESTIONS.md` (section per run) and are committed.
