#!/usr/bin/env python3
"""Select, install and check STL-to-CAD harness versions (harnesses/v0, v1, ...).

Every version lives in harnesses/<id>/ with a HARNESS.json manifest. Versions may reuse the
same skill names (for example every version has an `stl-re-orchestrate` entry skill), so only
ONE version may be installed in a given skills directory at a time. `install` removes every
skill directory that belongs to any known version before copying (or linking) the chosen one,
and writes a marker file so `which` can tell what is installed. This prevents the stale
same-named skill shadowing that v0's doctor warns about.

The skills directory is agent-agnostic: ~/.claude/skills for Claude Code, a project-local
.claude/skills or .agents/skills, or a per-run folder used by the benchmark runner.

Usage:
  python3 tools/harness.py list
  python3 tools/harness.py install v0 [--dest ~/.claude/skills] [--link]
  python3 tools/harness.py which   [--dest ~/.claude/skills]
  python3 tools/harness.py doctor v0
  python3 tools/harness.py selftest v0

Exit codes: 0 ok, 2 refused or check failed.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARNESSES = REPO / "harnesses"
MARKER = ".stl_re_harness.json"
DEFAULT_DEST = Path.home() / ".claude" / "skills"


def manifests() -> dict[str, dict]:
    out = {}
    for f in sorted(HARNESSES.glob("*/HARNESS.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        m["_dir"] = f.parent
        out[m["id"]] = m
    return out


def get(version: str) -> dict:
    ms = manifests()
    if version not in ms:
        sys.exit(f"unknown harness {version!r}; known: {', '.join(ms)}")
    return ms[version]


def cmd_list(_: argparse.Namespace) -> int:
    for vid, m in manifests().items():
        n = len(m.get("skills", []))
        print(f"{vid:4} {m['status']:15} {n} skills  {m['name']}")
    return 0


def cmd_install(a: argparse.Namespace) -> int:
    m = get(a.version)
    if not m.get("skills"):
        print(f"{a.version} has no installable skills yet (status: {m['status']})", file=sys.stderr)
        return 2
    dest = Path(a.dest).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    known = {s for mm in manifests().values() for s in mm.get("skills", [])}
    for name in sorted(known):
        p = dest / name
        if p.is_symlink() or p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
    src_root = m["_dir"] / m["skills_dir"]
    for name in m["skills"]:
        src = src_root / name
        if not (src / "SKILL.md").is_file():
            print(f"missing {src}/SKILL.md", file=sys.stderr)
            return 2
        if a.link:
            (dest / name).symlink_to(src, target_is_directory=True)
        else:
            shutil.copytree(src, dest / name, ignore=shutil.ignore_patterns("__pycache__"))
    (dest / MARKER).write_text(json.dumps(
        {"version": a.version, "mode": "link" if a.link else "copy", "source": str(src_root),
         "skills": m["skills"]}, indent=2) + "\n", encoding="utf-8")
    print(f"installed {a.version} ({len(m['skills'])} skills) into {dest}")
    return 0


def cmd_which(a: argparse.Namespace) -> int:
    f = Path(a.dest).expanduser() / MARKER
    if not f.is_file():
        print("none")
        return 2
    print(json.loads(f.read_text(encoding="utf-8"))["version"])
    return 0


def _run(m: dict, cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=m["_dir"])


def cmd_doctor(a: argparse.Namespace) -> int:
    m = get(a.version)
    if not m.get("doctor"):
        print(f"{a.version} has no doctor yet", file=sys.stderr)
        return 2
    return 0 if _run(m, m["doctor"]) == 0 else 2


def cmd_selftest(a: argparse.Namespace) -> int:
    m = get(a.version)
    rcs = [_run(m, c) for c in m.get("selftests", [])]
    if not rcs:
        print(f"{a.version} has no selftests yet", file=sys.stderr)
        return 2
    return 0 if all(rc == 0 for rc in rcs) else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("install")
    p.add_argument("version")
    p.add_argument("--dest", default=str(DEFAULT_DEST))
    p.add_argument("--link", action="store_true", help="symlink instead of copy (tracks the repo)")
    p.set_defaults(fn=cmd_install)
    p = sub.add_parser("which")
    p.add_argument("--dest", default=str(DEFAULT_DEST))
    p.set_defaults(fn=cmd_which)
    for name, fn in (("doctor", cmd_doctor), ("selftest", cmd_selftest)):
        p = sub.add_parser(name)
        p.add_argument("version")
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
