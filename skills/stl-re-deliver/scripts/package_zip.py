"""Pack a delivered run into one downloadable zip: deliverables up front, every source file behind them.

This is the last step of stl-re-deliver (SKILL.md step 7). It is the standing owner request for
how a finished job is handed over (owner instruction, 2026-09-25, OD-S03 run): "deliver it as a
zip with all source files and deliverables, downloadable".

The zip holds one top-level folder `<part>_delivery/`:

    DELIVERY.md        index: verdict, regime, what is where, how to rebuild
    deliverables/      <part>.step, <part>_datum.step, <part>_cad.stl, README.md, VERDICT.md,
                       gate.json, MANIFEST.json, qa/overlays/* (the files a reader opens first)
    run/               the whole run folder, byte for byte (input, intake, measure, build, qa,
                       deliver, decisions, DECISIONS.md, _itN_SUPERSEDED)
    skill_scripts/     stl-re-rebuild-build123d/scripts, which build/model.py imports, so the
                       build can be re-run from the zip alone

It refuses (exit 2) unless deliver/MANIFEST.json exists and every file it lists still has its
sha256: the zip must carry exactly what the manifest vouches for. It never changes the run.
The zip is deterministic (sorted entries, fixed timestamps), so the same run gives the same bytes.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DeliverError, fail, load_json, run_main, sha256_file  # noqa: E402

ZIP_TIME = (1980, 1, 1, 0, 0, 0)  # fixed, so the zip bytes do not depend on the wall clock
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


def delivery_md(part: str, man: dict, top: list[str]) -> str:
    lines = [
        f"# {part}: delivery package", "",
        f"Verdict: `{man.get('verdict')}`. Regime: `{man.get('regime')}`. "
        f"Iteration: {man.get('iteration')} of 3.", "",
        "Open `deliverables/README.md` first: it carries the numbers, the limitations with their "
        "re-run triggers and the claim boundary. `deliverables/VERDICT.md` is the verifier's own report.", "",
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
        "cd run",
        "PYTHONPATH=../skill_scripts/stl-re-rebuild-build123d/scripts python3 build/model.py",
        "```", "",
        "If `build/model.py` takes CLI flags, the exact command is in `run/deliver/repro.json#cmd`.", "",
    ]
    return "\n".join(lines)


def add(z: zipfile.ZipFile, arc: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arc, date_time=ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="zip path (default: <run>/../<part>_delivery.zip)")
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
    for png in sorted((run / "qa" / "overlays").glob("*.png")):
        picks[f"overlays/{png.name}"] = png

    scripts = SKILLS / "stl-re-rebuild-build123d" / "scripts"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        add(z, f"{root}/DELIVERY.md", delivery_md(part, man, sorted(picks)).encode())
        for name in sorted(picks):
            add(z, f"{root}/deliverables/{name}", picks[name].read_bytes())
        for f in sorted(run.rglob("*"), key=lambda p: p.relative_to(run).as_posix()):
            if f.is_file():
                add(z, f"{root}/run/{f.relative_to(run).as_posix()}", f.read_bytes())
        for f in sorted(scripts.rglob("*.py")):
            if "__pycache__" not in f.parts:
                add(z, f"{root}/skill_scripts/stl-re-rebuild-build123d/scripts/"
                       f"{f.relative_to(scripts).as_posix()}", f.read_bytes())
    print(f"wrote {out}  bytes={out.stat().st_size}  sha256={sha256_file(out)}  "
          f"deliverables={len(picks)}")


if __name__ == "__main__":
    run_main(main)
