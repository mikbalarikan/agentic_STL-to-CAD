# Delivery package (owner decision, 2026-09-26)

Every `stl-re-*` job ends with **one downloadable zip** that holds the deliverables **and** all source
files of the run. This is the standing delivery format; do not ask for it again per session.

## When

Last step of `stl-re-deliver`, after `make_manifest.py` succeeded (so CHK-PUBLISH, ACCEPT-BAND,
hash freeze and repro are already enforced). A run without `deliver/MANIFEST.json` is never zipped.

```
python scripts/package_zip.py --run <run> [--out-dir <dir>] [--include-scan] [--max-source-mb 25]
```

## What the zip contains

```
<part>_RE_<VERDICT>_<YYYY-MM-DD>.zip
  <part>_RE_<VERDICT>_<YYYY-MM-DD>/
    PACKAGE_INDEX.md   verdict + regime line, layout, every excluded file with bytes/sha256/reason
    deliverables/      build/<part>_datum.step, build/<part>.step (scan frame), build/<part>_cad.stl,
                       deliver/ (README.md, MANIFEST.json, repro.json, limitations.json, extra docs),
                       qa/VERDICT.md, qa/gate.json, qa/overlays/, measure/PARAM_TABLE.md,
                       DECISIONS.md, decisions/
    source/            everything else in the run folder with its run-relative path: input/ (photos,
                       hashes, filled MEASUREMENTS), intake/, measure/ (scripts, params.json, figures),
                       build/ (model.py, MODELING_PLAN.md, logs, export_check.json), qa/ (scripts, JSON),
                       _itN_SUPERSEDED/
```

Merging `deliverables/` and `source/` gives back the complete run tree, so the repro command in
`deliver/README.md` works from the unzipped folder.

## Exclusions (listed in PACKAGE_INDEX.md, never silent)

- `input/scan.stl`: the owner's own raw scan, identified by its sha256 in `input/INPUT_HASHES.json`.
  Ship it with `--include-scan` when the recipient does not have it.
- Regenerable intermediates larger than `--max-source-mb` (working / aligned meshes, point caches,
  de-warped measurement copies, wip STLs). The stage script that writes each one is in `source/`.
- `__pycache__/`, `*.pyc`.
- Verify's deviation arrays (`qa/dev_arrays.npz`, one per iteration, ~18 MB each) count as regenerable
  (`*.npz`, `*.npy`).

## Size limit (found on the OD-E02 real run, 2026-09-28)

SendUserFile refuses files over **30 MiB**. With three iterations the default `--max-source-mb 25` gave an
89 MiB zip (three `dev_arrays.npz` plus the working meshes). If the zip is over 30 MiB, re-run with
`--max-source-mb 5`: only regenerable intermediates drop out, each still listed in PACKAGE_INDEX.md with
bytes, sha256 and reason. Deliverables are never dropped.

## Where it goes

Next to the run folder (the job folder the owner gave), plus `<zip>.sha256`. Then send the zip to the
owner (SendUserFile, display `attach`) together with the verdict, regime, iteration and limitations
(`SKILL.md` §6). For `BAND_NOT_MET` the zip exists only after a recorded `ACCEPT-BAND`.
