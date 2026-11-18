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
                       build/ (model.py, MODELING_PLAN.md, logs, export_check.json), qa/ (scripts, JSON),
                       _itN_SUPERSEDED/
```

Merging `deliverables/` and `source/` gives back the complete run tree, so the repro command in
`deliver/README.md` works from the unzipped folder.

## Exclusions (listed in PACKAGE_INDEX.md, never silent)

- `input/scan.stl`: the owner's own raw scan, identified by its sha256 in `input/INPUT_HASHES.json`.
  Ship it with `--include-scan` when the recipient does not have it.
- Regenerable intermediates larger than `--max-source-mb` (default 5 MB): working / aligned meshes,
  point and distance caches (`*.npy`, `*.npz`, `*.pkl`, `*.ply`), de-warped measurement copies, `wip/`,
  `qa/work/`, verify's `qa/_work/*.stl` tessellations. First real run: without this the zip was 662 MB, mostly caches. The stage script that writes each one is in `source/`.
- `__pycache__/`, `*.pyc`.

## Where it goes

Next to the run folder (the job folder the owner gave), plus `<zip>.sha256`. Then send the zip to the
owner (SendUserFile, display `attach`) together with the verdict, regime, iteration and limitations
(`SKILL.md` §6). For `BAND_NOT_MET` the zip exists only after a recorded `ACCEPT-BAND`.

## Size: ONE .zip under the 30 MiB upload limit (owner request, OD-S01 real run, 2026-09-28)

The owner wants a single `.zip` file, not parts. The session upload (SendUserFile) takes at most 30 MiB
per file, so `package_zip.py --max-zip-mib 29` (the default) keeps the zip under it. When the first
pass is too big, it leaves out **second-tier regenerable artefacts**, largest first, until the zip fits:

- `*.npz`: QA or measure deviation arrays; `stl-re-verify/scripts/deviation_gate.py` rewrites them.
- `*/selfcheck/*.png`: the builder's self-check renders (NOT QA); `build/selfcheck/*.py` redraws them.
- `_it*_SUPERSEDED/build/*_cad.stl`: a superseded iteration's CAD tessellation; its `model.py` rebuilds it.

Each one is listed in PACKAGE_INDEX.md with bytes, sha256 and the reason, and the script that makes it
stays in `source/`. On OD-S01, 72 MiB became 27.8 MiB this way (OD-E02, 3 iterations: 89 MiB with the
old 25 MB default, mostly three ~18 MB `qa/dev_arrays.npz`). OD-G10: a 52.9 MiB zip was refused by the upload.
OD-H21: QA's `dev_arrays.npz` made a 55.5 MiB zip; listing the regenerable arrays took it to 19 MiB. The default `--max-source-mb 5` already lists
the work/aligned meshes.

### Last resort: byte parts

Only if the zip is still over the limit after the tier-2 exclusions (the script prints a WARNING),
send it in byte parts:

```
split -b 28M -d -a 2 <zip> <zip>.part          # -> <zip>.part00, .part01, ...
cat <zip>.part* | sha256sum                    # must equal <zip>.sha256
```

Send the `.sha256` and all parts, with the rejoin command: `cat <zip>.part* > <zip>` (macOS/Linux) or
`copy /b <zip>.part00+<zip>.part01+... <zip>` (Windows).
