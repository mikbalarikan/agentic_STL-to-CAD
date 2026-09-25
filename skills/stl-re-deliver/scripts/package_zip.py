"""Pack a delivered run into one downloadable zip: deliverables up front, every source file behind them.

This is the last step of stl-re-deliver (SKILL.md step 6). It is the standing owner request for
how a finished job is handed over (owner instruction, 2026-09-25, OD-S03 run): "deliver it as a
zip with all source files and deliverables, downloadable".

The zip holds one top-level folder `<part>_delivery/`:

    DELIVERY.md        index: verdict, regime, what is where, how to rebuild (repro.json#command)
    deliverables/      <part>.step, <part>_datum.step, <part>_cad.stl, README.md, VERDICT.md,
                       gate.json, MANIFEST.json, qa/overlays/* (the files a reader opens first)
    run/               the whole run folder, byte for byte (input, intake, measure, build, qa,
                       deliver, decisions, DECISIONS.md, _itN_SUPERSEDED)
    skill_scripts/     stl-re-rebuild-build123d/scripts, which build/model.py imports, so the
                       build can be re-run from the zip alone
    input/photos/...   only the files README.md links to with ../, so its images resolve

It refuses (exit 2) unless deliver/MANIFEST.json exists and every file it lists still has its
sha256: the zip must carry exactly what the manifest vouches for. It never changes the run.
The zip is deterministic (sorted entries, fixed timestamps), so the same run gives the same bytes.
Above --max-mb (default 29 MiB, under the 30 MiB cloud file hand-off limit) it writes
<part>_delivery_partKofN.zip instead: each part is a normal zip of the same top folder, the
index and deliverables go in part 1, and extracting all parts into one folder rebuilds the tree.
"""
from __future__ import annotations

import argparse
import re
import shlex
import sys
import zipfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DeliverError, fail, load_json, run_main, sha256_file  # noqa: E402

ZIP_TIME = (1980, 1, 1, 0, 0, 0)  # fixed, so the zip bytes do not depend on the wall clock
RESERVE = 256 * 1024  # room for DELIVERY.md and the zip directory in each part
SKILLS = Path(__file__).resolve().parents[2]


def check_manifest(run: Path) -> dict:
    man = load_json(run / "deliver" / "MANIFEST.json")
    bad = []
    for e in man.get("included", []) + man.get("excluded", []):
        f = run / e["path"]
        if not f.is_file() or sha256_file(f) != e["sha256"]:
            bad.append(e["path"])
    listed = {e["path"] for e in man.get("included", []) + man.get("excluded", [])}
    new = [f.relative_to(run).as_posix() for f in run.rglob("*")
           if f.is_file() and f.relative_to(run).as_posix() not in listed | {"deliver/MANIFEST.json"}]
    if bad or new:
        raise DeliverError(f"MANIFEST.json is stale (changed: {bad[:5]}, unlisted: {new[:5]}); "
                           "re-run make_manifest.py, then package again")
    return man


def rebuild_cmd(run: Path) -> list[str]:
    """The command repro_check.py proved reproducible (repro.json#command, #cwd), made to find the
    helper scripts shipped in the zip: model.py looks for them via --scripts or
    STL_RE_REBUILD_SCRIPTS (rebuild templates/model_template.py find_scripts), a bare
    `from export_frames import ...` via PYTHONPATH. Setting both env vars covers either style."""
    repro = load_json(run / "deliver" / "repro.json")
    cmd = repro.get("command") or ["python3", "build/model.py"]
    cwd = repro.get("cwd", "run")
    up = "../" if cwd == "run" else "../../"
    helper = f"{up}skill_scripts/stl-re-rebuild-build123d/scripts"
    return [f"cd {'run' if cwd == 'run' else 'run/build'}",
            f"STL_RE_REBUILD_SCRIPTS={helper} PYTHONPATH={helper} {shlex.join(cmd)}"]


def delivery_md(part: str, man: dict, top: list[str], cmd: list[str], names: list[str]) -> str:
    lines = [
        f"# {part}: delivery package", "",
        f"Verdict: `{man.get('verdict')}`. Regime: `{man.get('regime')}`. "
        f"Iteration: {man.get('iteration')} of 3.", "",
        "Open `deliverables/README.md` first: it carries the numbers, the limitations with their "
        "re-run triggers and the claim boundary. `deliverables/VERDICT.md` is the verifier's own report.", "",
        *([] if len(names) == 1 else [
            f"This delivery is split into {len(names)} zips: " + ", ".join(f"`{x}`" for x in names) + ". "
            "Each is a normal zip; extract all of them into the same folder and they fill one "
            f"`{part}_delivery/` tree. The deliverables are in part 1.", ""]),
        "## Contents", "",
        "| path | what |", "|---|---|",
    ]
    for rel in top:
        lines.append(f"| `deliverables/{rel}` | deliverable |")
    lines += [
        "| `run/` | the full run folder, byte for byte; `run/deliver/MANIFEST.json` hashes every file |",
        "| `run/build/model.py` + `run/measure/params.json` | the editable design intent (parametric source) |",
        "| `skill_scripts/stl-re-rebuild-build123d/scripts/` | helpers `model.py` imports (`export_frames`) |",
        "", "## Rebuild from this zip", "",
        "```bash",
        "pip install build123d numpy",
        *cmd,
        "```", "",
        "This is the command `run/deliver/repro.json#command` proved reproducible; it rewrites the STEP "
        "files in `run/build/`.", "",
    ]
    return "\n".join(lines)


def deflated_size(data: bytes) -> int:
    """Compressed size zipfile will write (same raw-deflate settings as ZIP_DEFLATED)."""
    c = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
    return len(c.compress(data)) + len(c.flush())


def add(z: zipfile.ZipFile, arc: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arc, date_time=ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="zip path (default: <run>/../<part>_delivery.zip)")
    ap.add_argument("--max-mb", type=float, default=29.0,
                    help="max MiB per zip; above it, write <name>_partKofN.zip parts (default 29: the "
                         "cloud session file hand-off limit is 30 MiB)")
    a = ap.parse_args()
    run = a.run.resolve()
    try:
        man = check_manifest(run)
    except DeliverError as exc:
        fail(str(exc))
    part = man.get("part") or run.name
    out = (a.out or run.parent / f"{part}_delivery.zip").resolve()
    if run in out.parents:
        fail("--out must be outside the run folder, or the zip would change what the manifest hashed")
    root = f"{part}_delivery"

    picks: dict[str, Path] = {}
    for e in man.get("deliverables", []):
        picks[Path(e["path"]).name] = run / e["path"]
    for rel in ("deliver/README.md", "qa/VERDICT.md", "qa/gate.json", "deliver/MANIFEST.json"):
        if (run / rel).is_file():
            picks[Path(rel).name] = run / rel
    for stl in sorted((run / "build").glob("*_cad.stl")):
        picks[stl.name] = stl  # tessellated CAD (manifest role "preview"), still a deliverable to open
    for png in sorted((run / "qa" / "overlays").glob("*.png")):
        picks[f"overlays/{png.name}"] = png
    # README links such as ../input/photos/1.png: ship the target at the same relative place
    extra: dict[str, Path] = {}
    readme = run / "deliver" / "README.md"
    if readme.is_file():
        for link in re.findall(r"\]\((\.\./[^)\s]+)\)", readme.read_text(encoding="utf-8")):
            src = (run / "deliver" / link).resolve()
            if src.is_file() and run in src.parents:
                extra[src.relative_to(run).as_posix()] = src

    scripts = SKILLS / "stl-re-rebuild-build123d" / "scripts"
    # Entry order sets priority: part 1 gets the index, the deliverables and the rebuild helpers first.
    entries: list[tuple[str, Path]] = [(f"{root}/deliverables/{n}", picks[n]) for n in sorted(picks)]
    entries += [(f"{root}/{rel}", extra[rel]) for rel in sorted(extra)]
    entries += [(f"{root}/skill_scripts/stl-re-rebuild-build123d/scripts/{f.relative_to(scripts).as_posix()}", f)
                for f in sorted(scripts.rglob("*.py")) if "__pycache__" not in f.parts]
    entries += [(f"{root}/run/{f.relative_to(run).as_posix()}", f)
                for f in sorted(run.rglob("*"), key=lambda p: p.relative_to(run).as_posix()) if f.is_file()]

    # Split into self-contained zips under --max-mb (first fit, in entry order): one download can
    # be capped (the cloud file hand-off takes 30 MiB), and each part unzips on its own into the
    # same <part>_delivery/ folder, so no split-archive tool is needed.
    limit = int(a.max_mb * 1024 * 1024) - RESERVE
    parts: list[list[tuple[str, Path]]] = [[]]
    room = [limit]
    for arc, f in entries:
        size = deflated_size(f.read_bytes()) + len(arc) * 2 + 128
        i = next((k for k, r in enumerate(room) if size <= r), None)
        if i is None:
            if size > limit:
                print(f"WARNING: {arc} alone is over --max-mb; it gets a part of its own", file=sys.stderr)
            parts.append([])
            room.append(limit)
            i = len(parts) - 1
        parts[i].append((arc, f))
        room[i] -= size

    n = len(parts)
    names = [out.name] if n == 1 else [f"{out.stem}_part{k + 1}of{n}{out.suffix}" for k in range(n)]
    for old in out.parent.glob(f"{out.stem}_part*of*{out.suffix}"):
        old.unlink()  # a stale part from an earlier, differently split run would mislead
    if out.exists() and n > 1:
        out.unlink()
    out.parent.mkdir(parents=True, exist_ok=True)
    index = delivery_md(part, man, sorted(picks), rebuild_cmd(run), names).encode()
    for k, members in enumerate(parts):
        path = out.parent / names[k]
        with zipfile.ZipFile(path, "w") as z:
            if k == 0:
                add(z, f"{root}/DELIVERY.md", index)
            for arc, f in members:
                add(z, arc, f.read_bytes())
        print(f"wrote {path}  bytes={path.stat().st_size}  sha256={sha256_file(path)}  entries={len(members)}")
    print(f"parts={n}  deliverables={len(picks)}")

if __name__ == "__main__":
    run_main(main)
