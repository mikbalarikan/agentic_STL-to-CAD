#!/usr/bin/env python3
"""Package a delivered run as ONE downloadable zip: every source file plus the deliverables.

This is the standing hand-off format the owner asked for (session 2026-09-25, OD-G04: "zip
dosyasında bütün source file ve deliverables olarak indirebilir şekilde deliver et"). It runs
after make_manifest.py and changes nothing in the run folder.

Zip layout (root folder = <run folder name>/):
  DELIVERABLES/   copies of what the customer opens first: the STEP files (datum and scan
                  frame), the CAD STL, deliver/README.md, qa/VERDICT.md, qa/gate.json,
                  measure/PARAM_TABLE.md, qa/overlays/*.png
  run/            the whole run folder as-is (input/, intake/, measure/, build/, qa/, deliver/,
                  _itN_SUPERSEDED/, decisions/, DECISIONS.md): every script, JSON, figure and
                  mesh needed to audit or re-run the job (build/model.py + measure/params.json)
  ZIP_INDEX.md    what is where, the verdict and regime from MANIFEST.json, and how to re-build

Integrity: every file listed in deliver/MANIFEST.json#included must still have the recorded
sha256, otherwise the zip is refused (the run changed after the manifest: re-run the deliver
steps). Files the manifest does not list (other than the manifest itself) are refused too.
Python caches (__pycache__, *.pyc) are skipped: they are not source.

Size limit: `--split-mb N` (default 28, below the 30 MiB file-send limit of the Claude apps; 0 =
never split) packs the files into several STANDALONE zips `<name>_partK-of-N.zip`, each a valid
zip that opens on its own, with the same root folder so extracting all parts into one place gives
the full layout. Part 1 always carries ZIP_INDEX.md and DELIVERABLES/ (the STEP files first);
ZIP_INDEX.md lists which part holds which file. Sizes are planned from each file's deflated
size; a single file larger than the limit is refused.

Each zip's sha256 is printed and written next to it as <zip>.sha256.
Exit codes: 0 written; 2 refused; 3 internal error.
"""
from __future__ import annotations

import argparse
import fnmatch
import sys
import zipfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DeliverError, fail, load_json, run_main, sha256_file  # noqa: E402

SKIP = ("*/__pycache__/*", "__pycache__/*", "*.pyc")
DELIVERABLE_GLOBS = ("build/*.step", "build/*_cad.stl", "deliver/README.md", "qa/VERDICT.md",
                     "qa/gate.json", "measure/PARAM_TABLE.md", "qa/overlays/*.png")


def skipped(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, g) for g in SKIP)


def index_md(run_name: str, man: dict, deliverables: list[str], parts: dict[str, int] | None = None, n_parts: int = 1) -> str:
    lines = [
        f"# {run_name} — delivery zip",
        "",
        f"- Part: `{man.get('part', '')}`",
        f"- Verdict: `{man.get('verdict')}` (from `run/qa/gate.json`; reasoning in `run/qa/VERDICT.md`)",
        f"- Band regime: `{man.get('regime')}`",
        f"- Iteration: {man.get('iteration')}",
        f"- Human acceptance (BAND_NOT_MET only): {'recorded, see run/DECISIONS.md' if man.get('acceptance') else 'none'}",
        "",
        "## DELIVERABLES/ (open these first)",
        "",
    ]
    lines += [f"- `{d}`" for d in deliverables]
    lines += [
        "",
        "`*_datum.step` is the design (datum) frame; the STEP without a suffix is the original scan",
        "frame and overlays the raw scan. The README explains both frames and every limitation.",
        "",
        "## run/ (all source files)",
        "",
        "The complete run folder, unchanged: `input/` (scan, photos, hashes), `intake/` (datum),",
        "`measure/` (params.json, figures, probe scripts), `build/` (model.py, STEP, logs), `qa/`",
        "(independent verification), `deliver/` (README, MANIFEST with sha256 of every file, repro).",
        "",
        "Re-build the CAD from source (Python 3.10+, build123d 0.13, stl-re-* skills installed):",
        "",
        "```",
        "cd run/build",
        "python3 model.py --params ../measure/params.json --alignment ../intake/alignment.json --out . "
        f"--part {man.get('part', '<part>')}",
        "```",
        "",
        "Every file in `run/` is listed with its sha256 in `run/deliver/MANIFEST.json`.",
        "",
    ]
    if n_parts > 1 and parts:
        lines += [f"## Parts ({n_parts} standalone zips; extract all into the same folder)", ""]
        for k in range(1, n_parts + 1):
            lines.append(f"- part {k}: " + ", ".join(f"`{p}`" for p, v in sorted(parts.items()) if v == k))
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="zip path (default: <run parent>/<run name>_delivery.zip)")
    ap.add_argument("--split-mb", type=float, default=28.0,
                    help="max size per zip in MiB; split into standalone parts above it (0 = never split)")
    a = ap.parse_args()
    run = a.run.resolve()
    out = (a.out or run.parent / f"{run.name}_delivery.zip").resolve()
    try:
        if out.is_relative_to(run):
            raise DeliverError("the zip must be written outside the run folder (the manifest covers the run)")
        man = load_json(run / "deliver" / "MANIFEST.json")
        listed = {x["path"]: x["sha256"] for x in man.get("included", [])}
        listed.update({x["path"]: x["sha256"] for x in man.get("excluded", [])})
        files = sorted(f for f in run.rglob("*") if f.is_file())
        rels = [f.relative_to(run).as_posix() for f in files]
        changed = [r for r, f in zip(rels, files)
                   if r in listed and sha256_file(f) != listed[r]]
        unlisted = [r for r in rels if r not in listed and r != "deliver/MANIFEST.json" and not skipped(r)]
        missing = [r for r in listed if not (run / r).is_file()]
        if changed or unlisted or missing:
            raise DeliverError("run folder no longer matches deliver/MANIFEST.json "
                               f"(changed {changed[:5]}, unlisted {unlisted[:5]}, missing {missing[:5]}); "
                               "re-run repro_check / make_readme / make_manifest before packaging")
    except DeliverError as exc:
        fail(str(exc))

    deliverables = sorted(r for r in rels if any(fnmatch.fnmatch(r, g) for g in DELIVERABLE_GLOBS))
    if not any(r.endswith(".step") for r in deliverables):
        fail("no build/*.step found: nothing to deliver")
    root = run.name
    # entries: (arcname, source path); deliverables first (they go in part 1), then the run
    entries = [(f"{root}/DELIVERABLES/{r}", run / r) for r in sorted(deliverables, key=lambda r: not r.endswith(".step"))]
    entries += [(f"{root}/run/{r}", f) for r, f in zip(rels, files) if not skipped(r)]
    limit = int(a.split_mb * 1024 * 1024) if a.split_mb > 0 else 0
    est = {arc: len(zlib.compress(src.read_bytes(), 6)) + 200 for arc, src in entries}
    total = sum(est.values()) + 8192
    part_of: dict[str, int] = {}
    if limit and total > limit:
        big = [arc for arc, _ in entries if est[arc] > limit - 16384]
        if big:
            fail(f"file(s) larger than --split-mb after compression: {big}; raise --split-mb")
        sizes = [16384]  # part 1 reserves room for ZIP_INDEX.md
        for arc, _src in entries:   # first fit, keeping order (deliverables land in part 1)
            k = next((i for i, sz in enumerate(sizes) if sz + est[arc] <= limit), None)
            if k is None:
                sizes.append(0)
                k = len(sizes) - 1
            sizes[k] += est[arc]
            part_of[arc] = k + 1
        n_parts = len(sizes)
    else:
        part_of = {arc: 1 for arc, _ in entries}
        n_parts = 1
    outs = [out] if n_parts == 1 else [out.with_name(f"{out.stem}_part{k}-of-{n_parts}.zip") for k in range(1, n_parts + 1)]
    out.parent.mkdir(parents=True, exist_ok=True)
    rel_parts = {arc.split("/", 1)[1]: k for arc, k in part_of.items()}
    idx = index_md(root, man, [f"DELIVERABLES/{d}" for d in deliverables], rel_parts, n_parts)
    for k, path in enumerate(outs, start=1):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            if k == 1:
                zf.writestr(f"{root}/ZIP_INDEX.md", idx)
            for arc, src in entries:
                if part_of[arc] == k:
                    zf.write(src, arc)
        digest = sha256_file(path)
        path.with_name(path.name + ".sha256").write_text(f"{digest}  {path.name}\n", encoding="utf-8")
        if path.stat().st_size > limit > 0:
            fail(f"{path.name} came out at {path.stat().st_size} bytes, over --split-mb; raise it or re-run")
        print(f"wrote {path} ({path.stat().st_size} bytes, {sum(1 for v in part_of.values() if v == k)} files) sha256 {digest}")
    print(f"{len(deliverables)} deliverables, {len(entries) - len(deliverables)} run files, {n_parts} zip(s)")

if __name__ == "__main__":
    run_main(main)
