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
                              + addons/<name>/{out,qa,README.md}: owner-requested add-on bodies (e.g. a
                              fitted bristle envelope) built on top of the verified part, with their own check
        source/               the whole run tree (same relative paths as the run folder), minus the
                              files already in deliverables/ and the declared exclusions below

Rules (CHK-PUBLISH still applies: this runs only after make_manifest.py succeeded):
- Refuses (exit 2) unless deliver/MANIFEST.json, deliver/README.md and qa/VERDICT.md exist.
- Nothing is dropped silently: every file left out is listed in PACKAGE_INDEX.md with bytes,
  sha256 and the reason. Default exclusions: input/scan.stl (the owner's own scan; pass
  --include-scan to ship it), files larger than --max-source-mb that are regenerable
  intermediates (work/aligned meshes, point caches), __pycache__/ and *.pyc.
- The zip is written next to the run folder (or --out-dir) with a sidecar <zip>.sha256.
- --max-zip-mb N (cloud sessions: 29, the chat upload limit is 30 MiB): files larger than
  --part-file-mb (source files and big deliverable meshes; STEPs normally stay) move out of the main zip into companion zips <root>_part<k>.zip, each kept under N MB
  (greedy by compressed size), with the same <root>/deliverables|source/ prefix, so unzipping all of them into one
  folder gives the whole package. PACKAGE_INDEX.md lists which file is in which part. Nothing is dropped.
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
    "addons/*/out*/*", "addons/*/qa*/*.md", "addons/*/qa*/*.json", "addons/*/README.md", "addons/*/render/*.png",
]
ALWAYS_SKIP = ["*/__pycache__/*", "__pycache__/*", "*.pyc"]
REGENERABLE = ["intake/work.stl", "intake/aligned_work.stl", "*.npy", "*.npz", "*.ply", "*/wip/*.stl",
               "measure/figures/*.stl", "intake/explore/*.stl", "_it*_SUPERSEDED/*.stl"]


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
    ap.add_argument("--max-source-mb", type=float, default=25.0,
                    help="regenerable intermediates above this size are listed, not zipped")
    ap.add_argument("--suffix", default="",
                    help="extra name tag, e.g. 'with-bristles' when repackaging after an add-on, so the new zip "
                         "is never mistaken for the earlier one with the same verdict/date")
    ap.add_argument("--max-zip-mb", type=float, default=0.0,
                    help="split large source files into companion zips so every zip stays under this size (0 = off)")
    ap.add_argument("--part-file-mb", type=float, default=5.0,
                    help="with --max-zip-mb: source files above this size go to the companion zips")
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
    root = f"{part}_RE_{verdict}_{date}" + (f"_{a.suffix}" if a.suffix else "")
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

    parts: list[list[tuple[Path, str, int]]] = []
    if a.max_zip_mb > 0:
        import zlib
        # large files (source, and deliverable meshes such as *_cad.stl) move to companion zips; their
        # archive path keeps the deliverables/ or source/ prefix, so unzipping every part rebuilds the tree
        big = [(p, f"source/{rel}") for p, rel in source if p.stat().st_size / 1e6 > a.part_file_mb]
        big += [(p, f"deliverables/{rel}") for p, rel in deliv if p.stat().st_size / 1e6 > a.part_file_mb]
        source = [(p, rel) for p, rel in source if p.stat().st_size / 1e6 <= a.part_file_mb]
        deliv = [(p, rel) for p, rel in deliv if p.stat().st_size / 1e6 <= a.part_file_mb]
        sized = sorted(((p, rel, len(zlib.compress(p.read_bytes(), 6))) for p, rel in big), key=lambda t: -t[2])
        cap = a.max_zip_mb * 1e6 * 0.98
        for item in sized:
            if item[2] > cap:
                print(f"REFUSED: {item[1]} alone compresses to {item[2] / 1e6:.1f} MB > --max-zip-mb", file=sys.stderr)
                return 2
            for part in parts:
                if sum(t[2] for t in part) + item[2] <= cap:
                    part.append(item)
                    break
            else:
                parts.append([item])

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
    if parts:
        lines += ["", "## Companion zips (large files, same folder layout)", "",
                  "Unzip the main zip and every part into the same folder.", "", "| part | file | bytes | sha256 |", "|---|---|---|---|"]
        for k, part in enumerate(parts, 1):
            for p, rel, _c in part:
                lines.append(f"| `{root}_part{k}.zip` | `{rel}` | {p.stat().st_size} | `{sha256(p)}` |")
    lines += ["", f"Counts: {len(deliv)} deliverable files, {len(source)} source files in the main zip, "
              f"{sum(len(x) for x in parts)} in {len(parts)} companion zip(s), {len(excluded)} excluded.", ""]
    index = "\n".join(lines)

    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr(f"{root}/PACKAGE_INDEX.md", index)
        for p, rel in deliv:
            z.write(p, f"{root}/deliverables/{rel}")
        for p, rel in source:
            z.write(p, f"{root}/source/{rel}")
    written = [zpath]
    for k, part in enumerate(parts, 1):
        pz = out_dir / f"{root}_part{k}.zip"
        with zipfile.ZipFile(pz, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for p, rel, _c in part:
                z.write(p, f"{root}/{rel}")
        written.append(pz)
    for w in written:
        w.with_suffix(".zip.sha256").write_text(f"{sha256(w)}  {w.name}\n")
    over = [w.name for w in written if a.max_zip_mb > 0 and w.stat().st_size > a.max_zip_mb * 1e6]
    print(json.dumps({"zip": str(zpath), "sha256": sha256(zpath), "bytes": zpath.stat().st_size,
                      "parts": [{"zip": str(w), "bytes": w.stat().st_size} for w in written[1:]],
                      "deliverables": len(deliv), "source": len(source), "excluded": len(excluded)}, indent=1))
    if over:
        print(f"REFUSED: still over --max-zip-mb: {over}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as ex:  # an internal error is never reported as a finding about the run
        print(f"INTERNAL ERROR: {ex!r}", file=sys.stderr)
        sys.exit(3)
