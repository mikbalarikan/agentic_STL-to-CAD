# Delivery package (owner decision, 2026-09-26)

Every `stl-re-*` job ends with **one downloadable zip** that holds the deliverables **and** all source
files of the run. This is the standing delivery format; do not ask for it again per session.

## When

Last step of `stl-re-deliver`, after `make_manifest.py` succeeded (so CHK-PUBLISH, ACCEPT-BAND,
hash freeze and repro are already enforced). A run without `deliver/MANIFEST.json` is never zipped.

```
python scripts/package_zip.py --run <run> [--out-dir <dir>] [--include-scan] [--max-source-mb 5]
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
                       build/ (feature_tree.json, base_tree.json, tree_log.json, logs, export_check.json; v0: model.py, MODELING_PLAN.md), qa/ (scripts, JSON),
                       _itN_SUPERSEDED/
```

Merging `deliverables/` and `source/` gives back the complete run tree, so the repro command in
`deliver/README.md` works from the unzipped folder.

## Exclusions (listed in PACKAGE_INDEX.md, never silent)

- `input/scan.stl`: the owner's own raw scan, identified by its sha256 in `input/INPUT_HASHES.json`.
  Ship it with `--include-scan` when the recipient does not have it.
- Regenerable intermediates larger than `--max-source-mb` (default 5 MB): working / aligned meshes,
  point and distance caches (`*.npy`, `*.npz`, `*.pkl`, `*.ply`), de-warped measurement copies, `wip/`,
  `qa/work/`. First real run: without this the zip was 662 MB, mostly caches. The stage script that writes each one is in `source/`.
- `__pycache__/`, `*.pyc`.

## Where it goes

Next to the run folder (the job folder the owner gave), plus `<zip>.sha256`. Then send the zip to the
owner (SendUserFile, display `attach`) together with the verdict, regime, iteration and limitations
(`SKILL.md` §6). For `BAND_NOT_MET` the zip exists only after a recorded `ACCEPT-BAND`.
