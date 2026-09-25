#!/usr/bin/env python3
"""Run-folder helper for the stl-re-* skills: init, status, supersede, doctor.

Provenance: NEW CODE. No golden project shipped a run-folder tool; this script
implements the layout in ../references/run-contract.md §1-§2 and the rules it
enforces are cited below:
  - inputs hashed with sha256, never modified   (analysis/SYNTHESIS.md A1, A5; facet-film T4)
  - superseded iterations moved intact           (CHK-SUPERSEDED; golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/_it1_SUPERSEDED/)
  - 3 full loops per part, then HALT             (baseline/oomwoo-re-pipeline/RE_SPEC.md:248-250)
  - nothing in deliver/ before a verdict         (CHK-PUBLISH; baseline/oomwoo-re-pipeline/TRACKER.md:13)
  - environment parity before a run              (baseline/oomwoo-re-pipeline/RE_SPEC.md:364-373)

Subcommands
  init       create <run>/ layout, copy (or --link) inputs, write input/INPUT_HASHES.json
  status     print the run state (stage reached, iteration, verdict) as JSON
  supersede  move measure/ build/ qa/ to _itN_SUPERSEDED/ (REVISE); refuses past loop 3
  doctor     check python deps and that the six stl-re-* skills sit side by side
  --selftest run all of the above on a temporary directory

Determinism: files are processed in sorted order, JSON is written with sorted keys.
The only wall-clock value is the provenance field `created` (run-contract.md §2); set
SOURCE_DATE_EPOCH to pin it. Exit codes: 0 ok, 1 usage/IO error, 2 check failed, 3 HALT.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

TOOL = "init_run.py"
TOOL_VERSION = "stl-re-orchestrate@1"
MAX_LOOPS = 3  # baseline/oomwoo-re-pipeline/RE_SPEC.md:250 (per-part breaker)

SKILLS = (
    "stl-re-orchestrate",
    "stl-re-intake-datum",
    "stl-re-measure-intent",
    "stl-re-rebuild-build123d",
    "stl-re-verify",
    "stl-re-deliver",
)
VERDICTS = ("APPROVED_WITH_LIMITATIONS", "APPROVED", "BAND_NOT_MET", "REVISE", "HALT")
DELIVERABLE = {"APPROVED", "APPROVED_WITH_LIMITATIONS", "BAND_NOT_MET"}
ITERATED = ("measure", "build", "qa")
# Directories created by init (run-contract.md §1). deliver/ is NOT created: it may
# only appear after qa/VERDICT.md exists (CHK-PUBLISH).
LAYOUT = ("input/photos", "intake", "measure/figures", "build", "qa/overlays")

# Stage exit artefacts (run-contract.md §1). "<part>" is substituted.
STAGE_EXIT: dict[str, tuple[str, ...]] = {
    "intake": ("intake/INTAKE_CARD.md", "intake/intake.json", "intake/MEASUREMENTS.md",
               "intake/alignment.json", "intake/work.stl", "intake/aligned_work.stl"),
    "measure": ("measure/params.json", "measure/PARAM_TABLE.md"),
    "rebuild": ("build/MODELING_PLAN.md", "build/model.py", "build/build_log.txt",
                "build/<part>_datum.step", "build/<part>.step", "build/<part>_cad.stl",
                "build/export_check.json"),
    "verify": ("qa/gate.json", "qa/VERDICT.md"),
    "deliver": ("deliver/README.md", "deliver/MANIFEST.json", "deliver/repro.json"),
}
STAGES = tuple(STAGE_EXIT)


class HaltError(Exception):
    """The iteration bound is reached; the run must HALT to a human."""

DECISIONS_TEMPLATE = """# DECISIONS — {part}

Human decisions that gate this run. One entry per decision; never edit an old entry,
append a new one. Format: `- <date> | <who> | <decision id> | <decision> | <evidence path>`

Decision ids: REGIME (band regime chosen at intake), MEASUREMENTS (calipers supplied /
proceed scan-only), PART-CLASS (unsupported class: proceed or stop), ACCEPT-BAND
(BAND_NOT_MET accepted for delivery), HALT (reason and options), INDEP (verify could not
run in a fresh context), OTHER.

"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def created_stamp() -> str:
    """Provenance-only timestamp; SOURCE_DATE_EPOCH pins it for reproducible output."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    moment = (_dt.datetime.fromtimestamp(int(epoch), tz=_dt.timezone.utc) if epoch
              else _dt.datetime.now(tz=_dt.timezone.utc))
    return moment.replace(microsecond=0).isoformat()


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_part(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError(f"part name {name!r}: use letters, digits, '.', '_' or '-'")
    return name


def place(src: Path, dst: Path, link: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if link:
        dst.symlink_to(src.resolve())
    else:
        shutil.copyfile(src, dst)
        dst.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # evidence is read-only


# ----------------------------------------------------------------------------- init
def cmd_init(run: Path, part: str, scan: Path, photos: list[Path], measurements: Path | None,
             resolution: str, link: bool) -> dict[str, Any]:
    part = safe_part(part)
    if not scan.is_file():
        raise FileNotFoundError(f"scan not found: {scan}")
    if (run / "input" / "INPUT_HASHES.json").exists():
        raise FileExistsError(f"{run} is already initialised; use `status` or a new run folder")
    for d in LAYOUT:
        (run / d).mkdir(parents=True, exist_ok=True)

    plan: list[tuple[Path, str, str]] = [(scan, "input/scan.stl", "scan")]
    photo_files: list[Path] = []
    for p in photos:
        photo_files.extend(sorted(x for x in p.iterdir() if x.is_file()) if p.is_dir() else [p])
    names: set[str] = set()
    for p in sorted(photo_files, key=lambda x: x.name):
        if p.name in names:
            raise ValueError(f"duplicate photo file name {p.name}")
        names.add(p.name)
        plan.append((p, f"input/photos/{p.name}", "photo"))
    if measurements is not None:
        plan.append((measurements, "input/MEASUREMENTS.md", "measurements"))

    files: list[dict[str, Any]] = []
    inputs: dict[str, str] = {}
    for src, rel, role in plan:
        if not src.is_file():
            raise FileNotFoundError(f"input not found: {src}")
        digest = sha256_file(src)
        dst = run / rel
        place(src, dst, link)
        if sha256_file(dst) != digest:
            raise IOError(f"hash mismatch after placing {src} -> {dst}")
        inputs[rel] = digest
        files.append({"path": rel, "role": role, "sha256": digest,
                      "bytes": src.stat().st_size, "source": str(src.resolve()),
                      "mode": "symlink" if link else "copy"})

    doc = {"schema": "stl-re/INPUT_HASHES@1", "tool": TOOL, "tool_version": TOOL_VERSION,
           "inputs": inputs, "seed": 0, "created": created_stamp(), "part": part,
           "scan_resolution": resolution, "files": files}
    write_json(run / "input" / "INPUT_HASHES.json", doc)
    dec = run / "DECISIONS.md"
    if not dec.exists():
        dec.write_text(DECISIONS_TEMPLATE.format(part=part), encoding="utf-8")
    return doc


# --------------------------------------------------------------------------- status
def read_verdict(run: Path) -> str | None:
    gate = run / "qa" / "gate.json"
    if gate.is_file():
        try:
            v = json.loads(gate.read_text(encoding="utf-8")).get("verdict")
            if isinstance(v, str) and v in VERDICTS:
                return v
        except (json.JSONDecodeError, OSError):
            pass
    vmd = run / "qa" / "VERDICT.md"
    if vmd.is_file():
        text = vmd.read_text(encoding="utf-8", errors="replace")
        for v in VERDICTS:  # longest first so APPROVED_WITH_LIMITATIONS wins over APPROVED
            if re.search(rf"\b{v}\b", text):
                return v
    return None


def superseded(run: Path) -> list[int]:
    out = []
    for p in run.iterdir() if run.is_dir() else []:
        m = re.fullmatch(r"_it(\d+)_SUPERSEDED", p.name)
        if m and p.is_dir():
            out.append(int(m.group(1)))
    return sorted(out)


def cmd_status(run: Path) -> dict[str, Any]:
    hashes = run / "input" / "INPUT_HASHES.json"
    if not hashes.is_file():
        raise FileNotFoundError(f"{run} is not an initialised run (no input/INPUT_HASHES.json)")
    meta = json.loads(hashes.read_text(encoding="utf-8"))
    part = meta["part"]
    tampered = sorted(rel for rel, h in meta["inputs"].items()
                      if not (run / rel).is_file() or sha256_file(run / rel) != h)
    stages: dict[str, dict[str, Any]] = {}
    reached = "init"
    for st in STAGES:
        need = [r.replace("<part>", part) for r in STAGE_EXIT[st]]
        missing = [r for r in need if not (run / r).exists()]
        stages[st] = {"complete": not missing, "missing": missing}
        if not missing and reached == (STAGES[STAGES.index(st) - 1] if STAGES.index(st) else "init"):
            reached = st
    verdict = read_verdict(run)
    findings: list[str] = []
    if tampered:
        findings.append("input files changed or missing since init: " + ", ".join(tampered))
    if (run / "deliver").exists() and verdict not in DELIVERABLE:
        findings.append("CHK-PUBLISH: deliver/ exists without a deliverable verdict")
    if not (run / "input" / "MEASUREMENTS.md").is_file():
        findings.append("no filled input/MEASUREMENTS.md: calipers missing, scan-only needs a "
                        "MEASUREMENTS decision in DECISIONS.md")
    its = superseded(run)
    return {"run": str(run), "part": part, "iteration": len(its) + 1, "max_loops": MAX_LOOPS,
            "superseded": [f"_it{n}_SUPERSEDED" for n in its], "last_complete_stage": reached,
            "stages": stages, "verdict": verdict, "findings": findings}


# ------------------------------------------------------------------------ supersede
def cmd_supersede(run: Path, carry: bool) -> dict[str, Any]:
    st = cmd_status(run)
    if st["verdict"] != "REVISE":
        raise RuntimeError(f"supersede needs verdict REVISE, found {st['verdict']!r}")
    if (run / "deliver").exists():
        raise RuntimeError("deliver/ exists; a delivered iteration is not superseded silently")
    n = st["iteration"]
    if n >= MAX_LOOPS:
        raise HaltError(f"HALT: iteration {n} of {MAX_LOOPS} ended in REVISE "
                            "(RE_SPEC.md:250). Record HALT in DECISIONS.md and ask the human.")
    dest = run / f"_it{n}_SUPERSEDED"
    if dest.exists():
        raise FileExistsError(f"{dest} already exists")
    dest.mkdir()
    moved = []
    for d in ITERATED:
        if (run / d).exists():
            shutil.move(str(run / d), str(dest / d))
            moved.append(d)
    for d in LAYOUT:
        (run / d).mkdir(parents=True, exist_ok=True)
    carried = []
    if carry:  # copies, so the superseded folder stays intact and diffable
        for rel in ("measure", "build/MODELING_PLAN.md", "build/model.py"):
            src = dest / rel
            if src.is_dir():
                shutil.copytree(src, run / rel, dirs_exist_ok=True)
                carried.append(rel)
            elif src.is_file():
                shutil.copy2(src, run / rel)
                carried.append(rel)
    return {"superseded_to": dest.name, "moved": moved, "carried_forward": carried,
            "iteration_now": n + 1, "max_loops": MAX_LOOPS}


# --------------------------------------------------------------------------- doctor
def cmd_doctor(skills_root: Path) -> dict[str, Any]:
    deps: dict[str, str | None] = {}
    for mod in ("numpy", "scipy", "trimesh", "build123d"):
        try:
            deps[mod] = str(getattr(importlib.import_module(mod), "__version__", "present"))
        except Exception:  # noqa: BLE001 - any import failure means missing
            deps[mod] = None
    skills = {s: (skills_root / s / "SKILL.md").is_file() for s in SKILLS}
    ok = all(v is not None for k, v in deps.items() if k in ("trimesh", "build123d")) and all(skills.values())
    return {"python": sys.version.split()[0], "deps": deps, "skills_root": str(skills_root),
            "skills": skills, "ok": ok}


# ------------------------------------------------------------------------- selftest
def selftest() -> int:
    os.environ.setdefault("SOURCE_DATE_EPOCH", "0")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        src = t / "src"
        (src / "photos").mkdir(parents=True)
        (src / "part.stl").write_bytes(b"solid t\nendsolid t\n")
        (src / "photos" / "b.jpg").write_bytes(b"B")
        (src / "photos" / "a.jpg").write_bytes(b"A")
        (src / "MEAS.md").write_text("| ID | caliper |\n", encoding="utf-8")

        docs = []
        for name in ("run1", "run2"):
            docs.append(cmd_init(t / name, "cap", src / "part.stl", [src / "photos"],
                                 src / "MEAS.md", "unknown", link=False))
        a, b = ((t / n / "input" / "INPUT_HASHES.json").read_bytes() for n in ("run1", "run2"))
        assert a == b, "INPUT_HASHES.json not deterministic"
        assert docs[0]["inputs"]["input/scan.stl"] == hashlib.sha256(b"solid t\nendsolid t\n").hexdigest()
        assert [f["path"] for f in docs[0]["files"]] == [
            "input/scan.stl", "input/photos/a.jpg", "input/photos/b.jpg", "input/MEASUREMENTS.md"]
        assert not (t / "run1" / "deliver").exists(), "deliver/ must not exist before a verdict"
        try:
            cmd_init(t / "run1", "cap", src / "part.stl", [], None, "unknown", False)
            raise AssertionError("re-init must be refused")
        except FileExistsError:
            pass

        run = t / "run1"
        st = cmd_status(run)
        assert st["iteration"] == 1 and st["last_complete_stage"] == "init" and not st["findings"]

        def fake_iteration(verdict: str) -> None:
            for d in LAYOUT:
                (run / d).mkdir(parents=True, exist_ok=True)
            for st_name in ("intake", "measure", "rebuild"):
                for rel in STAGE_EXIT[st_name]:
                    p = run / rel.replace("<part>", "cap")
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text("x", encoding="utf-8")
            write_json(run / "qa" / "gate.json", {"verdict": verdict})
            (run / "qa" / "VERDICT.md").write_text(f"# VERDICT: {verdict}\n", encoding="utf-8")

        fake_iteration("REVISE")
        st = cmd_status(run)
        assert st["last_complete_stage"] == "verify" and st["verdict"] == "REVISE", st
        r1 = cmd_supersede(run, carry=True)
        assert r1["superseded_to"] == "_it1_SUPERSEDED" and r1["iteration_now"] == 2
        assert (run / "_it1_SUPERSEDED" / "qa" / "gate.json").is_file()
        assert (run / "measure" / "params.json").is_file(), "carry-forward failed"
        assert not (run / "qa" / "gate.json").exists()
        fake_iteration("REVISE")
        cmd_supersede(run, carry=False)
        fake_iteration("REVISE")
        try:
            cmd_supersede(run, carry=True)
            raise AssertionError("loop 3 REVISE must HALT")
        except HaltError:
            pass
        assert cmd_status(run)["iteration"] == MAX_LOOPS

        (run / "qa" / "VERDICT.md").write_text("APPROVED_WITH_LIMITATIONS\n", encoding="utf-8")
        (run / "qa" / "gate.json").unlink()
        assert read_verdict(run) == "APPROVED_WITH_LIMITATIONS"
        (run / "qa" / "VERDICT.md").unlink()
        (run / "deliver").mkdir()
        assert any("CHK-PUBLISH" in f for f in cmd_status(run)["findings"])

        os.chmod(t / "run2" / "input" / "scan.stl", 0o644)
        (t / "run2" / "input" / "scan.stl").write_bytes(b"tampered")
        assert any("changed" in f for f in cmd_status(t / "run2")["findings"])

        lk = cmd_init(t / "run3", "cap", src / "part.stl", [], None, "full", link=True)
        assert (t / "run3" / "input" / "scan.stl").is_symlink() and lk["scan_resolution"] == "full"
        cmd_doctor(Path(__file__).resolve().parents[2])
    print("selftest OK")
    return 0


# ---------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--selftest", action="store_true", help="run the self-test on a temp dir")
    sub = ap.add_subparsers(dest="cmd")
    pi = sub.add_parser("init", help="create a run folder and hash the inputs")
    pi.add_argument("run", type=Path, help="run folder to create")
    pi.add_argument("--part", required=True, help="part name used for build/<part>*.step")
    pi.add_argument("--scan", required=True, type=Path, help="scan STL (copied to input/scan.stl)")
    pi.add_argument("--photos", type=Path, nargs="*", default=[], help="photo files or folders")
    pi.add_argument("--measurements", type=Path, help="filled MEASUREMENTS.md (calipers), if any")
    pi.add_argument("--scan-resolution", choices=("full", "decimated", "unknown"), default="unknown",
                    help="official gates need the full-resolution scan (golden-examples/README.md)")
    pi.add_argument("--link", action="store_true", help="symlink inputs instead of copying")
    ps = sub.add_parser("status", help="print run state as JSON")
    ps.add_argument("run", type=Path)
    pv = sub.add_parser("supersede", help="move measure/ build/ qa/ to _itN_SUPERSEDED/ after REVISE")
    pv.add_argument("run", type=Path)
    pv.add_argument("--no-carry", action="store_true",
                    help="do not copy measure/ and build/model.py forward into the new iteration")
    pd = sub.add_parser("doctor", help="check dependencies and sibling skills")
    pd.add_argument("--skills-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    try:
        if args.cmd == "init":
            out = cmd_init(args.run, args.part, args.scan, args.photos, args.measurements,
                           args.scan_resolution, args.link)
        elif args.cmd == "status":
            out = cmd_status(args.run)
        elif args.cmd == "supersede":
            out = cmd_supersede(args.run, carry=not args.no_carry)
        elif args.cmd == "doctor":
            out = cmd_doctor(args.skills_root)
            print(json.dumps(out, indent=2, sort_keys=True))
            return 0 if out["ok"] else 2
        else:
            ap.print_help()
            return 1
    except HaltError as e:
        print(str(e), file=sys.stderr)
        return 3
    except (OSError, ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
