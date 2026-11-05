#!/usr/bin/env python3
"""Package a delivered run as ONE downloadable zip: deliverables + all source files.

Owner decision (2026-09-26): every stl-re job ends with a single zip the owner can download,
holding the deliverables AND every source file needed to audit or re-run the job. The layout
is fixed here so it never has to be re-explained per session (references/delivery-package.md).

    <part>_RE_<VERDICT>_<YYYY-MM-DD>.zip
      <part>_RE_<VERDICT>_<YYYY-MM-DD>/
        PACKAGE_INDEX.md      what is where, verdict/regime line, excluded files + how to regenerate
        deliverables/         STEP (datum + scan frame), CAD STL, README, VERDICT, gate.json,
                              PARAM_TABLE, MANIFEST, repro.json, DECISIONS, overlays/, extra deliver/ docs
        source/               the whole run tree (same relative paths as the run folder), minus the
                              files already in deliverables/ and the declared exclusions below

Rules (CHK-PUBLISH still applies: this runs only after make_manifest.py succeeded):
- Refuses (exit 2) unless deliver/MANIFEST.json, deliver/README.md and qa/VERDICT.md exist.
- Nothing is dropped silently: every file left out is listed in PACKAGE_INDEX.md with bytes,
  sha256 and the reason. Default exclusions: input/scan.stl (the owner's own scan; pass
  --include-scan to ship it), files larger than --max-source-mb (default 5) that are regenerable
  intermediates (work/aligned meshes, point caches .npy/.npz/.pkl/.ply, wip/, qa/work/), __pycache__/, *.pyc.
- The zip is written next to the run folder (or --out-dir) with a sidecar <zip>.sha256.
Exit codes: 0 written; 2 refused; 3 internal error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import sys
import zipfile
from pathlib import Path

DELIVERABLE_GLOBS = [
    "build/*_datum.step", "build/*.step", "build/*_cad.stl",
    "deliver/*", "qa/VERDICT.md", "qa/gate.json", "qa/overlays/*",
    "measure/PARAM_TABLE.md", "DECISIONS.md", "decisions/*",
]
ALWAYS_SKIP = ["*/__pycache__/*", "__pycache__/*", "*.pyc"]
REGENERABLE = ["intake/work.stl", "intake/aligned_work.stl", "*.npy", "*.npz", "*.pkl", "*.ply",
               "*/wip/*", "measure/figures/*.stl", "intake/explore/*.stl", "_it*_SUPERSEDED/*.stl",
               "qa/work/*"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def match(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, help="default: the run folder's parent")
    ap.add_argument("--include-scan", action="store_true", help="also ship input/scan.stl")
    ap.add_argument("--max-source-mb", type=float, default=5.0,
                    help="regenerable intermediates above this size are listed, not zipped")
    a = ap.parse_args(argv)
    run = a.run.resolve()
    for need in ("deliver/MANIFEST.json", "deliver/README.md", "qa/VERDICT.md"):
        if not (run / need).is_file():
            print(f"REFUSED (CHK-PUBLISH): {need} missing - run preflight/repro/make_readme/make_manifest first",
                  file=sys.stderr)
            return 2
    man = json.loads((run / "deliver/MANIFEST.json").read_text(encoding="utf-8"))
    gate = json.loads((run / "qa/gate.json").read_text(encoding="utf-8"))
    verdict = str(gate.get("verdict") or man.get("verdict") or "UNKNOWN")
    part = man.get("part") or json.loads((run / "input/INPUT_HASHES.json").read_text())["part"]
    regime = gate.get("regime", {}).get("name", "?")
    date = _dt.date.today().isoformat()
    root = f"{part}_RE_{verdict}_{date}"
    out_dir = (a.out_dir or run.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    zpath = out_dir / f"{root}.zip"

    files = sorted(p for p in run.rglob("*") if p.is_file())
    deliv, source, excluded = [], [], []
    for p in files:
        rel = p.relative_to(run).as_posix()
        if match(rel, ALWAYS_SKIP):
            continue
        if match(rel, DELIVERABLE_GLOBS):
            deliv.append((p, rel))
            continue
        size_mb = p.stat().st_size / 1e6
        if rel == "input/scan.stl" and not a.include_scan:
            excluded.append((p, rel, "owner's raw scan (sha256 in input/INPUT_HASHES.json); pass --include-scan to ship it"))
        elif size_mb > a.max_source_mb and match(rel, REGENERABLE):
            excluded.append((p, rel, f"regenerable intermediate > {a.max_source_mb:g} MB (re-run the stage script that wrote it)"))
        else:
            source.append((p, rel))

    lines = [f"# {root}", "",
             f"Verdict **{verdict}** under regime **{regime}** (from qa/gate.json; read deliverables/qa/VERDICT.md "
             f"and deliverables/deliver/README.md before using the CAD).", "",
             "## Layout",
             "- `deliverables/` - the files to use: STEP in the datum frame (`build/*_datum.step`) and in the scan "
             "frame (`build/<part>.step`), CAD STL, README, VERDICT, gate.json, PARAM_TABLE, MANIFEST, repro.json, "
             "DECISIONS, QA overlays. Paths keep their run-relative folders.",
             "- `source/` - every other file of the run with its run-relative path (scripts, JSON, figures, logs, "
             "superseded iterations). Put `deliverables/*` and `source/*` back into one folder to get the run tree.",
             "", "## Excluded (listed, not shipped)", "",
             "| file | bytes | sha256 | reason |", "|---|---|---|---|"]
    for p, rel, why in excluded:
        lines.append(f"| `{rel}` | {p.stat().st_size} | `{sha256(p)}` | {why} |")
    if not excluded:
        lines.append("| - | - | - | nothing excluded |")
    lines += ["", f"Counts: {len(deliv)} deliverable files, {len(source)} source files, {len(excluded)} excluded.", ""]
    index = "\n".join(lines)

    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr(f"{root}/PACKAGE_INDEX.md", index)
        for p, rel in deliv:
            z.write(p, f"{root}/deliverables/{rel}")
        for p, rel in source:
            z.write(p, f"{root}/source/{rel}")
    digest = sha256(zpath)
    zpath.with_suffix(".zip.sha256").write_text(f"{digest}  {zpath.name}\n")
    print(json.dumps({"zip": str(zpath), "sha256": digest, "bytes": zpath.stat().st_size,
                      "deliverables": len(deliv), "source": len(source), "excluded": len(excluded)}, indent=1))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as ex:  # an internal error is never reported as a finding about the run
        print(f"INTERNAL ERROR: {ex!r}", file=sys.stderr)
        sys.exit(3)
