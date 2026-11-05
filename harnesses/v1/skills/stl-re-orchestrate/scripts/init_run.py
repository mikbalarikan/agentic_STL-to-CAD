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
  status     print the run state (stage reached, iteration, verdict) as JSON; only trusts
             qa/gate.json#verdict when errors is empty and verdict is in allowed_verdicts (O-1)
  rehash     hash a human-filled input/MEASUREMENTS.md into INPUT_HASHES.json (O-2)
  supersede  --route {measure,geometry,datum,repro} (required): move measure/ build/ qa/ (and
             intake/ for --route datum) to _itN_SUPERSEDED/ (REVISE); the route decides what
             carries forward (O-7); refuses past loop 3. --route repro (R2-O1) instead moves
             only qa/ and build/, needs no REVISE verdict (deliver/repro.json#reproducible ==
             false, or --confirm-repro-failure), writes a ROUTE marker in the superseded
             folder, and is excluded from the 3-loop count (folder numbering stays monotonic)
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

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff", ".bmp", ".webp"}

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
    # O-5: intake/regime.json (verify stops without it) and qa/masks.json (SKILL.md §2
    # exit table) are hard requirements the next stage checks; a run must not be reported
    # complete without them.
    "intake": ("intake/INTAKE_CARD.md", "intake/intake.json", "intake/regime.json",
               "intake/MEASUREMENTS.md", "intake/alignment.json", "intake/work.stl",
               "intake/aligned_work.stl"),
    "measure": ("measure/params.json", "measure/PARAM_TABLE.md"),
    "rebuild": ("build/MODELING_PLAN.md", "build/model.py", "build/build_log.txt",
                "build/<part>_datum.step", "build/<part>.step", "build/<part>_cad.stl",
                "build/export_check.json"),
    "verify": ("qa/gate.json", "qa/VERDICT.md", "qa/masks.json"),
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
        if p.is_dir():
            # O-15: a reference folder mixes photos with other files (e.g. B02's
            # 5_reference/MEASUREMENTS.md); only ingest actual images as role "photo".
            entries = sorted(x for x in p.iterdir() if x.is_file())
            for x in entries:
                if x.suffix.lower() in IMAGE_SUFFIXES:
                    photo_files.append(x)
                else:
                    print(f"skipping non-image file in --photos dir: {x}", file=sys.stderr)
        else:
            photo_files.append(p)
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


# -------------------------------------------------------------------------- rehash
def cmd_rehash(run: Path, measurements: Path | None) -> dict[str, Any]:
    """O-2: hash a human-filled `input/MEASUREMENTS.md` into INPUT_HASHES.json. The sheet
    is normally never hashed: intake writes `intake/MEASUREMENTS.md` (a request) and the
    human gate fills `input/MEASUREMENTS.md` *after* `init` runs, so CHK "inputs unchanged"
    cannot see edits to it unless it is registered here. Refuses to re-hash a path already
    covered (an edit to an already-hashed sheet is a tamper finding in `status`, not a
    rehash)."""
    hashes = run / "input" / "INPUT_HASHES.json"
    if not hashes.is_file():
        raise FileNotFoundError(f"{run} is not an initialised run (no input/INPUT_HASHES.json)")
    meta = json.loads(hashes.read_text(encoding="utf-8"))
    rel = "input/MEASUREMENTS.md"
    target = run / rel
    if rel in meta["inputs"]:
        raise RuntimeError(f"{rel} is already hashed; an edit to it is a tamper finding, "
                           "not a rehash")
    if measurements is not None:
        if target.exists():
            raise FileExistsError(f"{target} already exists; place it by hand, then rehash "
                                  "with no --measurements")
        digest = sha256_file(measurements)
        place(measurements, target, link=False)
        if sha256_file(target) != digest:
            raise IOError(f"hash mismatch after placing {measurements} -> {target}")
    if not target.is_file():
        raise FileNotFoundError(f"{target} does not exist: fill it, or pass --measurements")
    digest = sha256_file(target)
    meta["inputs"][rel] = digest
    meta.setdefault("files", []).append({"path": rel, "role": "measurements", "sha256": digest,
                                         "bytes": target.stat().st_size,
                                         "source": str(target.resolve()), "mode": "copy"})
    write_json(hashes, meta)
    dec = run / "DECISIONS.md"
    entry = f"- {created_stamp()[:10]} | orchestrator | MEASUREMENTS | filled sheet hashed via `init_run.py rehash` | {rel}\n"
    with dec.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    return meta


# --------------------------------------------------------------------------- status
def _load_gate(run: Path) -> dict[str, Any] | None:
    gate = run / "qa" / "gate.json"
    if not gate.is_file():
        return None
    try:
        doc = json.loads(gate.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return doc if isinstance(doc, dict) else None


def gate_refusal(run: Path) -> str | None:
    """O-1: `verdict.py assemble` writes gate.json with the refused verdict and its
    `errors` before returning a non-zero exit, so `#verdict` alone is not trustworthy.
    Return a human-readable reason when the gate was refused, else None."""
    doc = _load_gate(run)
    if doc is None:
        return None
    errors = doc.get("errors") or []
    v = doc.get("verdict")
    allowed = doc.get("allowed_verdicts")
    bad_word = v is not None and v not in VERDICTS
    bad_allowed = isinstance(v, str) and isinstance(allowed, list) and v not in allowed
    if errors or bad_word or bad_allowed:
        return (f"qa/gate.json verdict refused by verify (errors: {errors!r}); "
                "re-run stl-re-verify")
    return None


def read_verdict(run: Path) -> str | None:
    """Return the verdict only if it is trustworthy (O-1): `qa/gate.json` parses, has no
    `errors`, and (when `allowed_verdicts` is given) `verdict` is a member of it. A refused
    gate.json is never authoritative, even if `qa/VERDICT.md` prose also exists."""
    doc = _load_gate(run)
    if doc is not None:
        if gate_refusal(run) is not None:
            return None
        v = doc.get("verdict")
        return v if isinstance(v, str) and v in VERDICTS else None
    vmd = run / "qa" / "VERDICT.md"
    if vmd.is_file():
        text = vmd.read_text(encoding="utf-8", errors="replace")
        # O-16: match only the headline (a line with VERDICT in it), never any mention of a
        # verdict word buried in prose ("cannot be APPROVED", "it1: REVISE").
        headline = next((ln for ln in text.splitlines() if re.match(r"^#+.*VERDICT", ln)), None)
        if headline is not None:
            for v in VERDICTS:  # longest first so APPROVED_WITH_LIMITATIONS wins over APPROVED
                if re.search(rf"\b{v}\b", headline):
                    return v
    return None


def superseded(run: Path) -> list[int]:
    out = []
    for p in run.iterdir() if run.is_dir() else []:
        m = re.fullmatch(r"_it(\d+)_SUPERSEDED", p.name)
        if m and p.is_dir():
            out.append(int(m.group(1)))
    return sorted(out)


def superseded_route(run: Path, n: int) -> str:
    """The route recorded for `_itN_SUPERSEDED` in its `ROUTE` marker (round-2 R2-O1).

    A folder with no marker (written before this route existed, or moved by hand) is
    treated as an ordinary loop iteration, which is the safe default: it still counts
    toward the 3-loop bound rather than silently being excused."""
    marker = run / f"_it{n}_SUPERSEDED" / "ROUTE"
    if marker.is_file():
        route = marker.read_text(encoding="utf-8").strip()
        if route in ROUTES:
            return route
    return "measure"


def loop_iterations(run: Path) -> list[int]:
    """Superseded folders that count toward MAX_LOOPS. A `--route repro` folder is a
    reproducibility re-run, not a REVISE loop, so it is excluded (round-2 R2-O1); folder
    numbering itself (`superseded()`) stays monotonic and is never renumbered."""
    return [n for n in superseded(run) if superseded_route(run, n) != "repro"]


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
        if st == "intake" and not missing:
            # O-5: the intake exit needs a *passing* alignment, not merely a present file
            # (stl-re-intake-datum/SKILL.md:21 gates measure on alignment.json#status == "OK").
            try:
                align_status = json.loads((run / "intake" / "alignment.json")
                                          .read_text(encoding="utf-8")).get("status")
            except (json.JSONDecodeError, OSError):
                align_status = None
            if align_status != "OK":
                missing = missing + ["intake/alignment.json#status==OK"]
        stages[st] = {"complete": not missing, "missing": missing}
        if not missing and reached == (STAGES[STAGES.index(st) - 1] if STAGES.index(st) else "init"):
            reached = st
    verdict = read_verdict(run)
    findings: list[str] = []
    if stages["intake"]["complete"] and not re.search(r"\|\s*REGIME\s*\|",
                                                       (run / "DECISIONS.md").read_text(encoding="utf-8")
                                                       if (run / "DECISIONS.md").is_file() else ""):
        findings.append("DECISIONS.md has no REGIME entry: the regime must be declared, "
                        "never defaulted (run-contract.md §9)")
    if tampered:
        findings.append("input files changed or missing since init: " + ", ".join(tampered))
    if (run / "deliver").exists() and verdict not in DELIVERABLE:
        findings.append("CHK-PUBLISH: deliver/ exists without a deliverable verdict")
    refusal = gate_refusal(run)
    if refusal is not None:
        findings.append(refusal)
    meas = run / "input" / "MEASUREMENTS.md"
    if not meas.is_file():
        findings.append("no filled input/MEASUREMENTS.md: calipers missing, scan-only needs a "
                        "MEASUREMENTS decision in DECISIONS.md")
    elif "input/MEASUREMENTS.md" not in meta["inputs"]:
        # O-2: a filled sheet placed after init is not covered by INPUT_HASHES.json until
        # it is registered, so a silent edit to it would otherwise go undetected.
        findings.append("input/MEASUREMENTS.md exists but is not hashed in "
                        "INPUT_HASHES.json: run `init_run.py rehash <run>`")
    its = superseded(run)
    loop_its = loop_iterations(run)
    # R2-O1: `iteration` (and the 3-loop bound it feeds) excludes `--route repro` folders;
    # `superseded` still lists every folder, so folder numbering stays monotonic.
    return {"run": str(run), "part": part, "iteration": len(loop_its) + 1, "max_loops": MAX_LOOPS,
            "superseded": [f"_it{n}_SUPERSEDED" for n in its], "last_complete_stage": reached,
            "stages": stages, "verdict": verdict, "findings": findings}


# ------------------------------------------------------------------------ supersede
ROUTES = ("measure", "geometry", "datum", "repro")

# O-7: the route decides what a REVISE inherits, so the stage a finding was routed to is
# never masked as already complete by a blanket carry-forward. `measure` and `datum` carry
# nothing forward (the stage being redone must not look done); `geometry` carries the
# measurement and modeling-plan base forward as a diffable edit. run-contract.md §10.
# `repro` (R2-O1) carries the prior plan/model forward too, since only qa/ and build/ were
# superseded; measure/ is never moved for this route, so it needs no carry-forward entry --
# it was never taken away.
CARRY_FORWARD: dict[str, tuple[str, ...]] = {
    "measure": (),
    "geometry": ("measure", "build/MODELING_PLAN.md", "build/model.py"),
    "datum": (),
    "repro": ("build/MODELING_PLAN.md", "build/model.py"),
}

# R2-O1: `repro` supersedes only qa/ and build/ (a repro_check failure is a rebuild-fidelity
# problem, not a re-measure or a re-datum), and it does so without a REVISE verdict and
# without disturbing deliver/, which is exactly where the repro.json that triggered it lives.
ROUTE_MOVES: dict[str, tuple[str, ...]] = {
    "measure": ITERATED,
    "geometry": ITERATED,
    "datum": ("intake",) + ITERATED,
    "repro": ("qa", "build"),
}


def cmd_supersede(run: Path, route: str, carry: bool, confirm_repro_failure: bool = False) -> dict[str, Any]:
    if route not in ROUTES:
        raise ValueError(f"--route must be one of {ROUTES}, got {route!r}")
    st = cmd_status(run)
    if route == "repro":
        # R2-O1: accepted without a REVISE verdict, but only when deliver/repro.json already
        # says the rebuild is not reproducible, or the human explicitly overrides with
        # --confirm-repro-failure (a documented flag, never a silent default).
        repro_path = run / "deliver" / "repro.json"
        reproducible_false = False
        if repro_path.is_file():
            try:
                reproducible_false = json.loads(
                    repro_path.read_text(encoding="utf-8")).get("reproducible") is False
            except json.JSONDecodeError:
                reproducible_false = False
        if not reproducible_false and not confirm_repro_failure:
            raise RuntimeError(
                "supersede --route repro needs deliver/repro.json#reproducible == false "
                "(run `scripts/repro_check.py` first), or pass --confirm-repro-failure to "
                "record a documented override (run-contract.md §10)")
    else:
        if st["verdict"] != "REVISE":
            raise RuntimeError(f"supersede needs verdict REVISE, found {st['verdict']!r}")
        if (run / "deliver").exists():
            raise RuntimeError("deliver/ exists; a delivered iteration is not superseded silently")
    all_its = superseded(run)
    # Folder numbering is monotonic across every route, repro included, so two supersedes
    # never collide; the loop count used for MAX_LOOPS excludes repro folders (R2-O1).
    folder_n = (max(all_its) if all_its else 0) + 1
    loop_n = st["iteration"]
    if route != "repro" and loop_n >= MAX_LOOPS:
        raise HaltError(f"HALT: iteration {loop_n} of {MAX_LOOPS} ended in REVISE "
                            "(RE_SPEC.md:250). Record HALT in DECISIONS.md and ask the human.")
    dest = run / f"_it{folder_n}_SUPERSEDED"
    if dest.exists():
        raise FileExistsError(f"{dest} already exists")
    dest.mkdir()
    moved = []
    for d in ROUTE_MOVES[route]:
        if (run / d).exists():
            shutil.move(str(run / d), str(dest / d))
            moved.append(d)
    # R2-O1: record which route produced this folder, so a reader (this script, deliver's
    # CHK-SUPERSEDED) can tell a repro re-run apart from an ordinary REVISE loop.
    (dest / "ROUTE").write_text(route + "\n", encoding="utf-8")
    for d in LAYOUT:
        (run / d).mkdir(parents=True, exist_ok=True)
    carried = []
    if carry:  # copies, so the superseded folder stays intact and diffable
        for rel in CARRY_FORWARD[route]:
            src = dest / rel
            if src.is_dir():
                shutil.copytree(src, run / rel, dirs_exist_ok=True)
                carried.append(rel)
            elif src.is_file():
                shutil.copy2(src, run / rel)
                carried.append(rel)
    # A repro re-run does not consume a loop, so the loop count is unchanged (R2-O1).
    return {"superseded_to": dest.name, "route": route, "moved": moved,
            "carried_forward": carried,
            "iteration_now": loop_n if route == "repro" else loop_n + 1,
            "max_loops": MAX_LOOPS}


# --------------------------------------------------------------------------- doctor
DOCTOR_DEPS = ("numpy", "scipy", "trimesh", "build123d", "rtree", "shapely", "fast_simplification", "networkx")


def cmd_doctor(skills_root: Path) -> dict[str, Any]:
    # O-17: rtree (intake datum fitting), shapely (measure) and fast_simplification (intake
    # decimation) are all required by sibling skills; doctor must catch their absence too,
    # not just numpy/scipy/trimesh/build123d.
    # networkx: trimesh mesh sectioning (section / section_multiplane) assembles paths with it;
    # the baseline replay failed on its absence (harnesses/v0/evals/replay/artifacts/baseline_notes.md).
    deps: dict[str, str | None] = {}
    for mod in DOCTOR_DEPS:
        try:
            deps[mod] = str(getattr(importlib.import_module(mod), "__version__", "present"))
        except Exception:  # noqa: BLE001 - any import failure means missing
            deps[mod] = None
    skills = {s: (skills_root / s / "SKILL.md").is_file() for s in SKILLS}
    ok = all(v is not None for v in deps.values()) and all(skills.values())
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
                    if p.name == "alignment.json":
                        write_json(p, {"status": "OK"})
                    elif p.name == "regime.json":
                        write_json(p, {"name": "RE_SPEC", "source": "x", "bands": {}, "why": "t"})
                    else:
                        p.write_text("x", encoding="utf-8")
            write_json(run / "qa" / "masks.json", {})
            write_json(run / "qa" / "gate.json", {"verdict": verdict})
            (run / "qa" / "VERDICT.md").write_text(f"# VERDICT: {verdict}\n", encoding="utf-8")
            with (run / "DECISIONS.md").open("a", encoding="utf-8") as fh:
                fh.write("- 2026-01-01 | test | REGIME | RE_SPEC | x\n")

        fake_iteration("REVISE")
        st = cmd_status(run)
        assert st["last_complete_stage"] == "verify" and st["verdict"] == "REVISE", st
        assert not any("REGIME" in f for f in st["findings"]), st["findings"]

        # O-7: --route decides what carries forward, and a wrong route must be rejected.
        try:
            cmd_supersede(run, route="bogus", carry=True)
            raise AssertionError("an unknown --route must be rejected")
        except ValueError:
            pass
        r1 = cmd_supersede(run, route="geometry", carry=True)
        assert r1["superseded_to"] == "_it1_SUPERSEDED" and r1["iteration_now"] == 2
        assert r1["route"] == "geometry"
        assert (run / "_it1_SUPERSEDED" / "qa" / "gate.json").is_file()
        assert (run / "measure" / "params.json").is_file(), "geometry route must carry measure/ forward"
        assert (run / "build" / "model.py").is_file(), "geometry route must carry model.py forward"
        assert not (run / "qa" / "gate.json").exists()
        assert cmd_status(run)["last_complete_stage"] == "measure", \
            "geometry route: measure/ carried, so resume must land past it, at rebuild"
        fake_iteration("REVISE")
        cmd_supersede(run, route="geometry", carry=False)
        fake_iteration("REVISE")
        try:
            cmd_supersede(run, route="geometry", carry=True)
            raise AssertionError("loop 3 REVISE must HALT")
        except HaltError:
            pass
        assert cmd_status(run)["iteration"] == MAX_LOOPS

        # O-7, separate runs (so the 3-loop bound above does not interfere): a REVISE routed
        # to `measure` or `datum` must not carry the stage being redone forward, so `status`
        # resumes at that stage rather than skipping past it as "already complete".
        for route, want_resume in (("measure", "intake"), ("datum", "init")):
            rr = t / f"run_route_{route}"
            cmd_init(rr, "cap", src / "part.stl", [], None, "unknown", link=False)
            saved_run, run = run, rr
            try:
                fake_iteration("REVISE")
            finally:
                run = saved_run
            res = cmd_supersede(rr, route=route, carry=True)
            assert res["carried_forward"] == [], \
                f"O-7: --route {route} must not carry anything forward, got {res['carried_forward']}"
            if route == "datum":
                assert "intake" in res["moved"], "O-7: --route datum must also supersede intake/"
                assert (rr / f"{res['superseded_to']}" / "intake" / "regime.json").is_file()
                assert not (rr / "intake" / "regime.json").exists()
            assert cmd_status(rr)["last_complete_stage"] == want_resume, \
                f"--route {route}: resume must land at {want_resume!r}, not skip past it"

        # R2-O1: --route repro supersedes only qa/ and build/, without a REVISE verdict, and
        # must not count toward the 3-loop limit; folder numbering still stays monotonic.
        run_repro = t / "run_repro"
        cmd_init(run_repro, "cap", src / "part.stl", [], None, "unknown", link=False)
        saved_run, run = run, run_repro
        try:
            fake_iteration("APPROVED_WITH_LIMITATIONS")
        finally:
            run = saved_run
        try:
            cmd_supersede(run_repro, route="repro", carry=True)
            raise AssertionError("--route repro must refuse without a repro.json failure "
                                 "or --confirm-repro-failure")
        except RuntimeError:
            pass
        before_measure = (run_repro / "measure" / "params.json").read_bytes()
        (run_repro / "deliver").mkdir()
        write_json(run_repro / "deliver" / "repro.json", {"reproducible": False, "inputs": {}})
        res_repro = cmd_supersede(run_repro, route="repro", carry=True)
        assert res_repro["superseded_to"] == "_it1_SUPERSEDED" and res_repro["route"] == "repro"
        assert res_repro["moved"] == ["qa", "build"], \
            f"--route repro must move only qa/ and build/, got {res_repro['moved']}"
        assert res_repro["iteration_now"] == 1, "a repro re-run must not consume a loop"
        assert {"build/MODELING_PLAN.md", "build/model.py"} <= set(res_repro["carried_forward"])
        route_marker = run_repro / "_it1_SUPERSEDED" / "ROUTE"
        assert route_marker.is_file() and route_marker.read_text(encoding="utf-8").strip() == "repro"
        assert not (run_repro / "_it1_SUPERSEDED" / "measure").exists(), \
            "--route repro must not supersede measure/"
        assert (run_repro / "measure" / "params.json").read_bytes() == before_measure, \
            "--route repro must leave measure/ untouched"
        assert (run_repro / "build" / "model.py").is_file(), \
            "--route repro must carry model.py forward"
        assert (run_repro / "deliver" / "repro.json").is_file(), \
            "--route repro must not disturb deliver/"
        st_repro = cmd_status(run_repro)
        assert st_repro["iteration"] == 1, \
            "R2-O1: a repro-route superseded folder must not count toward the loop limit"
        assert st_repro["superseded"] == ["_it1_SUPERSEDED"]

        # Folder numbering is monotonic across routes even though the loop count is not: a
        # genuine REVISE loop afterward becomes _it2_SUPERSEDED, never a collision with it1.
        # (The stale deliver/ from the abandoned repro attempt is cleared first, as a human
        # would once the rebuild it pointed at has itself been superseded.)
        shutil.rmtree(run_repro / "deliver")
        saved_run, run = run, run_repro
        try:
            fake_iteration("REVISE")
        finally:
            run = saved_run
        res_repro2 = cmd_supersede(run_repro, route="measure", carry=False)
        assert res_repro2["superseded_to"] == "_it2_SUPERSEDED", res_repro2
        assert res_repro2["iteration_now"] == 2, \
            "the loop count must advance for an ordinary route after a repro folder"
        assert cmd_status(run_repro)["iteration"] == 2

        # --confirm-repro-failure: a documented override proceeds without repro.json.
        run_repro_ov = t / "run_repro_override"
        cmd_init(run_repro_ov, "cap", src / "part.stl", [], None, "unknown", link=False)
        saved_run, run = run, run_repro_ov
        try:
            fake_iteration("APPROVED")
        finally:
            run = saved_run
        res_override = cmd_supersede(run_repro_ov, route="repro", carry=False,
                                     confirm_repro_failure=True)
        assert res_override["route"] == "repro" and res_override["iteration_now"] == 1

        (run / "qa" / "VERDICT.md").write_text("# VERDICT: APPROVED_WITH_LIMITATIONS\n", encoding="utf-8")
        (run / "qa" / "gate.json").unlink()
        assert read_verdict(run) == "APPROVED_WITH_LIMITATIONS"
        # O-16: a verdict word buried in prose, not on the headline, must not match.
        (run / "qa" / "VERDICT.md").write_text(
            "# Notes\nThis cannot be APPROVED yet; it1 was a REVISE.\n", encoding="utf-8")
        assert read_verdict(run) is None, "O-16: prose mentions must not be read as a verdict"
        (run / "qa" / "VERDICT.md").unlink()
        (run / "deliver").mkdir()
        assert any("CHK-PUBLISH" in f for f in cmd_status(run)["findings"])
        (run / "deliver").rmdir()

        # O-1: a gate.json refused by verify's own `assemble` must never be trusted, even
        # though it still carries a verdict word and a VERDICT.md exists.
        write_json(run / "qa" / "gate.json", {"verdict": "APPROVED", "errors": ["Tier-1 missing"],
                                              "allowed_verdicts": ["BAND_NOT_MET", "HALT", "REVISE"]})
        (run / "qa" / "VERDICT.md").write_text("# VERDICT: APPROVED\n", encoding="utf-8")
        assert read_verdict(run) is None, "O-1: a refused gate.json must not be trusted"
        st_refused = cmd_status(run)
        assert st_refused["verdict"] is None
        assert any("refused" in f for f in st_refused["findings"]), st_refused["findings"]
        (run / "qa" / "gate.json").unlink()
        (run / "qa" / "VERDICT.md").unlink()

        os.chmod(t / "run2" / "input" / "scan.stl", 0o644)
        (t / "run2" / "input" / "scan.stl").write_bytes(b"tampered")
        assert any("changed" in f for f in cmd_status(t / "run2")["findings"])

        # O-2: a filled MEASUREMENTS.md placed after init is not hashed until `rehash` runs,
        # and once hashed, a later edit is caught like any other tampered input.
        run4 = t / "run4"
        cmd_init(run4, "cap", src / "part.stl", [], None, "unknown", link=False)
        assert any("no filled" in f for f in cmd_status(run4)["findings"])
        (run4 / "input" / "MEASUREMENTS.md").write_text("| ID | caliper |\n| ENV-X | 10.0 |\n",
                                                         encoding="utf-8")
        st4 = cmd_status(run4)
        assert any("not hashed" in f for f in st4["findings"]), st4["findings"]
        try:
            cmd_rehash(run4, src / "MEAS.md")  # target already exists: must be refused
            raise AssertionError("rehash must refuse to overwrite an already-placed sheet")
        except FileExistsError:
            pass
        cmd_rehash(run4, None)
        st4b = cmd_status(run4)
        assert not any("not hashed" in f for f in st4b["findings"]), st4b["findings"]
        try:
            cmd_rehash(run4, None)
            raise AssertionError("re-hashing an already-hashed sheet must be refused")
        except RuntimeError:
            pass
        (run4 / "input" / "MEASUREMENTS.md").write_text("tampered", encoding="utf-8")
        assert any("changed" in f for f in cmd_status(run4)["findings"]), \
            "O-2: an edit to an already-hashed MEASUREMENTS.md must be a tamper finding"

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
    pr = sub.add_parser("rehash", help="hash a filled input/MEASUREMENTS.md into "
                                        "INPUT_HASHES.json (O-2)")
    pr.add_argument("run", type=Path)
    pr.add_argument("--measurements", type=Path,
                    help="filled MEASUREMENTS.md to place at input/MEASUREMENTS.md, if not "
                         "already there")
    pv = sub.add_parser("supersede", help="move measure/ build/ qa/ (and intake/ for "
                                           "--route datum) to _itN_SUPERSEDED/ after REVISE")
    pv.add_argument("run", type=Path)
    pv.add_argument("--route", required=True, choices=ROUTES,
                    help="the stage the REVISE re-enters; decides what carries forward (O-7). "
                         "--route repro (R2-O1) supersedes only qa/ and build/ after a "
                         "repro_check failure, without a REVISE verdict, and does not count "
                         "toward the 3-loop limit")
    pv.add_argument("--no-carry", action="store_true",
                    help="do not copy anything forward into the new iteration, "
                         "regardless of --route")
    pv.add_argument("--confirm-repro-failure", action="store_true",
                    help="--route repro only: proceed even though deliver/repro.json does not "
                         "say reproducible=false (a documented human override)")
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
        elif args.cmd == "rehash":
            out = cmd_rehash(args.run, args.measurements)
        elif args.cmd == "supersede":
            out = cmd_supersede(args.run, route=args.route, carry=not args.no_carry,
                               confirm_repro_failure=args.confirm_repro_failure)
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
