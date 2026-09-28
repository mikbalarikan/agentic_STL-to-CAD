# CLAUDE.md — agentic_STL-to-CAD

This repo holds the `stl-re-*` skills (`skills/`) that turn a scanned STL into design-intent STEP
with build123d, plus the evidence they were distilled from. Read `README.md` for the skill index.

## When the owner sends a new STL job ("yeni bir STL tersine mühendislik görevi")

1. **Skills:** use them straight from `skills/` (they call each other by relative path; no copy to
   `~/.claude/skills` is needed). Install deps once per session:
   `python3 -m pip install numpy scipy trimesh build123d rtree shapely fast_simplification networkx matplotlib`
   then `python3 skills/stl-re-orchestrate/scripts/init_run.py doctor` (must print `"ok": true`).
2. **Run folder:** outside the repo (scans and STEPs are large): in cloud sessions use the scratchpad,
   `<scratchpad>/jobs/<part>/run`, created with `init_run.py init`. Attached files arrive under
   `/root/.claude/uploads/...`; pass them to `init` so they are hashed read-only.
3. **Drive the job with `skills/stl-re-orchestrate/SKILL.md`** (intake → measure → rebuild → verify →
   deliver). Verify always runs in a fresh subagent (CHK-INDEP).
4. **Standing owner defaults** (record each one in the run's `DECISIONS.md`, quoting the message):
   - "p95 plastik (parça) toleransı" / "tolerans = p95" → regime `baseline-skill`, class `plastic`
     (p95 ≤ 0.30 / max ≤ 0.80 mm). "machined/işlenmiş" → class `machined`.
   - STL + photos with no caliper sheet → scan-only (`MEASUREMENTS` entry; limitations "Tier-1 not run"
     and "absolute scale not caliper-verified", trigger "any caliper reading").
   - Ask the owner only what the files cannot answer, in ONE question card: is the STL the original
     full-resolution export; and, if the scan is an assembly, the delivery scope (one fused solid, or
     which body).
5. **Delivery format — standing owner decision (2026-09-26, reconfirmed 2026-09-28); never ask again:**
   every job ends with ONE downloadable zip holding the deliverables AND all source files of the run,
   written by `skills/stl-re-deliver/scripts/package_zip.py` after `make_manifest.py`
   (layout and exclusions: `skills/stl-re-deliver/references/delivery-package.md`). Send the zip and its
   `.sha256` to the owner with `SendUserFile` (`display: attach`) together with the report: verdict,
   regime, numbers from `qa/gate.json`, limitations with re-run triggers, loop count, independence.
   For `BAND_NOT_MET` the zip exists only after the owner's recorded `ACCEPT-BAND`.
6. **After the job:** record it under `evals/real-runs/<part-id>.md` with copies of the small records
   (`README.md`, `VERDICT.md`, `gate.json`, `DECISIONS.md`, one overlay) in `evals/real-runs/<part-id>/`
   (see `OD-H22.md`), add any skill defect you hit to that file's defect table and open owner questions
   to `QUESTIONS.md`, then commit and push on the session branch. Never commit scans, STEPs or zips.

## Known workarounds (open defects; details in `evals/real-runs/*.md`)

- CLI numbers that start with `-` must be passed as `--flag=-1.0,2.0` (argparse reads them as options).
- `align.py` STOP on a tie (primary rms a hair above a noise floor from the same estimator on another
  flat): re-run with the noise measured on the primary itself; `align.py` records it as a finding.
- `repro_check.py`: put the build command after a bare `--` (`--cwd build -- python3 model.py ...`).
- trimesh 4+/5: `mesh.section(plane_normal=..., plane_origin=...)` — keyword arguments; positional
  order is (normal, origin).
- build123d `Edge.center()` is a point on the curve; select circles by `edge.arc_center`.
- A cone face that contains its apex can fail BRepMesh at 0.003 mm (the export tolerance): build
  cone tools from r ≥ 1 mm when the apex region is cut away anyway.
