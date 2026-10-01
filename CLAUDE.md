# CLAUDE.md — agentic_STL-to-CAD

## STL → CAD jobs
- Entry point: `skills/stl-re-orchestrate/SKILL.md` (intake → measure → rebuild → verify → deliver).
  The skills call each other by relative path, so run them from `skills/` in this repo (or install
  them side by side, see README).
- Dependencies: `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`,
  then `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor`.

## Standing delivery format (owner decision 2026-09-26 — do not ask again)
Every job is handed over as **ONE downloadable zip** holding the deliverables **and all source files**
of the run (`skills/stl-re-deliver/references/delivery-package.md`):
- built by `python3 skills/stl-re-deliver/scripts/package_zip.py --run <run> --max-source-mb 5` after `make_manifest.py`
  (SendUserFile limit is 30 MiB; regenerable meshes/arrays are listed with sha256 in PACKAGE_INDEX.md, not shipped);
- name `<part>_RE_<VERDICT>_<YYYY-MM-DD>.zip` + `<zip>.sha256`, layout `deliverables/` + `source/` + `PACKAGE_INDEX.md`;
- send it to the owner with SendUserFile (`display: attach`) together with verdict, regime, loop count
  and limitations;
- `BAND_NOT_MET` is zipped only after a recorded `ACCEPT-BAND` in the run's `DECISIONS.md`.
- In a cloud session keep the run folder in the scratchpad (large meshes) and record the job under
  `evals/real-runs/<job>/` (README/VERDICT/DECISIONS/gate.json + overlay), like `evals/real-runs/OD-H22.md`
  and `evals/real-runs/DRM-BH01.md`.

## Tolerance shorthand
"p95 plastik parça toleransı" / "tolerans = p95" = regime `baseline-skill`, `material_class plastic`
(p95 ≤ 0.30 / max ≤ 0.80 mm). Record it as a `REGIME` line in `DECISIONS.md` before any gate runs.
