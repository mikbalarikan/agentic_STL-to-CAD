"""Shared helpers and delivery pre-checks for the stl-re-deliver scripts.

Provenance:
- JSON header, verdict vocabulary, DECISIONS.md, INPUT_HASHES.json, _itN_SUPERSEDED layout:
  skills/stl-re-orchestrate/references/run-contract.md §2, §7, §10 and
  skills/stl-re-orchestrate/scripts/init_run.py (DECISIONS_TEMPLATE, cmd_supersede, created_stamp).
- CHK-PUBLISH: analysis/SYNTHESIS.md §2, earned by OOM-B02 it1 published before its gate
  (golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/70_report.py:376).
- BAND_NOT_MET needs a recorded human acceptance: run-contract §7; OD-H12 "operatör onayı gerekli"
  (golden-examples/OD-H12_delonghi-dedica-pump/README.md:62); the unrecorded DRM snap max miss
  (analysis/golden/dreame_brush-caps.md Questions 1).
- CHK-SUPERSEDED: P03 it1 verdict overwritten (golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/VERDICT.md:6);
  B02 kept golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/_it1_SUPERSEDED/.
- Hash freeze (heuristic, n=1: M02): golden-examples/M02-02-03_watertight-design-intent/VERDICT.md:6.

Deterministic: no wall-clock value feeds any computation; `created` is provenance only and
honours SOURCE_DATE_EPOCH (same convention as init_run.py).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

TOOL_VERSION = "1.0.0"

VERDICTS = ("APPROVED", "APPROVED_WITH_LIMITATIONS", "BAND_NOT_MET", "REVISE", "HALT")
DELIVERABLE_VERDICTS = ("APPROVED", "APPROVED_WITH_LIMITATIONS", "BAND_NOT_MET")
MAX_LOOPS = 3  # RE_SPEC.md:248-250 (SYNTHESIS §4)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class DeliverError(Exception):
    """A blocking refusal. The message names the check id and what to do next."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise DeliverError(f"required file missing: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DeliverError(f"invalid JSON in {path}: {exc}") from exc


def created_stamp() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    moment = (_dt.datetime.fromtimestamp(int(epoch), tz=_dt.timezone.utc) if epoch
              else _dt.datetime.now(tz=_dt.timezone.utc))
    return moment.replace(microsecond=0).isoformat()


def header(schema_file: str, tool: str, run: Path, inputs: list[Path], seed: int = 0) -> dict[str, Any]:
    """Common JSON header, run-contract §2. Input paths are stored relative to the run folder."""
    ins: dict[str, str] = {}
    for p in sorted(set(inputs)):
        if p.is_file():
            ins[p.resolve().relative_to(run.resolve()).as_posix()] = sha256_file(p)
    return {"schema": f"stl-re/{schema_file}@1", "tool": tool, "tool_version": TOOL_VERSION,
            "inputs": ins, "seed": seed, "created": created_stamp()}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fail(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------------ CHK-PUBLISH
def first_verdict_token(text: str) -> str | None:
    """First verdict-vocabulary token in reading order (longest alternative wins)."""
    pat = re.compile(r"(?<![A-Z_])(" + "|".join(sorted(VERDICTS, key=len, reverse=True)) + r")(?![A-Z_])")
    m = pat.search(text)
    return m.group(1) if m else None


def check_publish(run: Path) -> tuple[str, dict[str, Any]]:
    """CHK-PUBLISH + headline-verdict agreement. Returns (verdict, gate)."""
    verdict_md = run / "qa" / "VERDICT.md"
    gate_path = run / "qa" / "gate.json"
    if not verdict_md.is_file() or not gate_path.is_file():
        raise DeliverError("CHK-PUBLISH fail: qa/VERDICT.md and qa/gate.json must both exist before "
                           "anything is written to deliver/. Run stl-re-verify first.")
    gate = load_json(gate_path)
    verdict = gate.get("verdict")
    if verdict not in VERDICTS:
        raise DeliverError(f"CHK-PUBLISH fail: qa/gate.json verdict is {verdict!r}; it must be one of "
                           f"{VERDICTS} (run-contract §7). Return to stl-re-verify.")
    first = first_verdict_token(verdict_md.read_text(encoding="utf-8"))
    if first != verdict:
        raise DeliverError(f"CHK-NUMBERS fail: the headline verdict in qa/VERDICT.md is {first!r} but "
                           f"qa/gate.json says {verdict}. Return to stl-re-verify to reconcile; do not "
                           "edit either file here.")
    if verdict not in DELIVERABLE_VERDICTS:
        raise DeliverError(f"CHK-PUBLISH stop: verdict {verdict} is not deliverable. REVISE loops back "
                           "to measure/rebuild; HALT goes to the orchestrator and a human.")
    return verdict, gate


def decisions(run: Path, decision_id: str) -> list[dict[str, str]]:
    """Parse `- <date> | <who> | <id> | <decision> | <evidence path>` lines of DECISIONS.md."""
    path = run / "DECISIONS.md"
    out: list[dict[str, str]] = []
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- "):
            continue
        parts = [p.strip() for p in line[2:].split("|")]
        if len(parts) >= 5 and parts[2] == decision_id:
            out.append({"date": parts[0], "who": parts[1], "id": parts[2],
                        "decision": parts[3], "evidence": "|".join(parts[4:]).strip()})
    return out


def check_acceptance(run: Path, verdict: str) -> dict[str, str] | None:
    """BAND_NOT_MET: need an ACCEPT-BAND entry in DECISIONS.md whose evidence file exists in the run."""
    if verdict != "BAND_NOT_MET":
        return None
    entries = [e for e in decisions(run, "ACCEPT-BAND") if e["date"] and e["who"] and e["decision"]]
    if not entries:
        raise DeliverError("BAND_NOT_MET stop: DECISIONS.md has no ACCEPT-BAND entry. Stop and ask the "
                           "owner: show the missed band with its number, the per-region explanation and "
                           "the options from qa/VERDICT.md. Write nothing to deliver/ until they answer.")
    acc = entries[-1]
    ev = (run / acc["evidence"].strip("` ")).resolve() if acc["evidence"] else None
    if ev is None or not ev.is_file() or run.resolve() not in ev.parents:
        raise DeliverError(f"BAND_NOT_MET stop: the ACCEPT-BAND evidence path {acc['evidence']!r} is not a "
                           "file inside the run folder. Save the owner's written acceptance there first.")
    acc["evidence"] = ev.relative_to(run.resolve()).as_posix()
    return acc


# ---------------------------------------------------------------------- CHK-SUPERSEDED
def check_superseded(run: Path) -> dict[str, Any]:
    """Every earlier iteration must be kept intact in _itN_SUPERSEDED/ (N = 1..k, contiguous)."""
    its = sorted(int(m.group(1)) for p in run.iterdir()
                 if p.is_dir() and (m := re.fullmatch(r"_it(\d+)_SUPERSEDED", p.name)))
    problems: list[str] = []
    notes: list[str] = []
    if its != list(range(1, len(its) + 1)):
        problems.append(f"superseded folders are not contiguous from 1: {its}")
    for n in its:
        d = run / f"_it{n}_SUPERSEDED"
        for rel in ("qa/VERDICT.md", "qa/gate.json", "build/model.py"):
            if not (d / rel).is_file():
                problems.append(f"_it{n}_SUPERSEDED/{rel} missing")
        if (d / "qa" / "gate.json").is_file():
            try:
                v = json.loads((d / "qa" / "gate.json").read_text(encoding="utf-8")).get("verdict")
            except json.JSONDecodeError:
                v = None
            if v != "REVISE":
                problems.append(f"_it{n}_SUPERSEDED/qa/gate.json verdict is {v!r}, expected REVISE")
        if not list((d / "build").glob("*.step")) if (d / "build").is_dir() else True:
            notes.append(f"_it{n}_SUPERSEDED has no STEP (finding, not a failure: the build may have aborted)")
    iteration = len(its) + 1
    if iteration > MAX_LOOPS:
        problems.append(f"iteration {iteration} exceeds the {MAX_LOOPS}-loop bound (RE_SPEC.md:248-250)")
    return {"ran": True, "result": "fail" if problems else ("finding" if notes else "pass"),
            "iteration": iteration, "superseded": [f"_it{n}_SUPERSEDED" for n in its],
            "note": "; ".join(problems + notes) or "all earlier iterations kept intact"}


# ------------------------------------------------------------------ evidence integrity
def check_inputs_unchanged(run: Path) -> dict[str, Any]:
    """input/ files still match input/INPUT_HASHES.json (evidence is never modified; SYNTHESIS A1)."""
    p = run / "input" / "INPUT_HASHES.json"
    if not p.is_file():
        return {"ran": False, "result": "finding", "note": "input/INPUT_HASHES.json missing"}
    doc = load_json(p)
    changed = []
    entries = doc.get("files") or [{"path": k, "sha256": v} for k, v in (doc.get("inputs") or {}).items()]
    for e in entries:
        f = run / e["path"]
        if not f.is_file() or sha256_file(f) != e["sha256"]:
            changed.append(e["path"])
    return {"ran": True, "result": "fail" if changed else "pass",
            "note": f"changed or missing: {changed}" if changed else f"{len(entries)} input file(s) unchanged"}


def _hexes(obj: Any) -> set[str]:
    if isinstance(obj, str):
        return {obj} if HEX64.match(obj) else set()
    if isinstance(obj, dict):
        return set().union(*(_hexes(v) for v in obj.values())) if obj else set()
    if isinstance(obj, list):
        return set().union(*(_hexes(v) for v in obj)) if obj else set()
    return set()


def check_hash_frozen(run: Path, gate: dict[str, Any]) -> dict[str, Any]:
    """The STEP files in build/ must be the ones QA hashed (qa/gate.json#hash_frozen)."""
    frozen = _hexes(gate.get("hash_frozen"))
    steps = sorted((run / "build").glob("*.step"))
    if not frozen:
        return {"ran": False, "result": "finding", "note": "qa/gate.json has no hash_frozen sha256"}
    if not steps:
        return {"ran": True, "result": "fail", "note": "no STEP in build/"}
    unmatched = [s.name for s in steps if sha256_file(s) not in frozen]
    if len(unmatched) == len(steps):
        return {"ran": True, "result": "fail",
                "note": f"no STEP in build/ matches a hash_frozen sha256 (changed after QA?): {unmatched}"}
    return {"ran": True, "result": "finding" if unmatched else "pass",
            "note": (f"not QA-hashed: {unmatched}" if unmatched else "every build/ STEP matches hash_frozen")}


def check_regime(run: Path, gate: dict[str, Any]) -> dict[str, Any]:
    """The regime in gate.json must be the one declared at intake (run-contract §12): compare
    gate.json#regime.name with intake/regime.json#name (the canonical declaration)."""
    intake = run / "intake" / "regime.json"
    g = (gate.get("regime") or {}).get("name")
    if not g:
        return {"ran": True, "result": "fail", "note": "qa/gate.json has no regime.name"}
    if not intake.is_file():
        return {"ran": False, "result": "finding", "note": "intake/regime.json missing; regime not cross-checked"}
    i = load_json(intake).get("name")
    if i and i != g:
        return {"ran": True, "result": "fail", "note": f"intake declared {i!r} but gate applied {g!r}"}
    return {"ran": True, "result": "pass" if i else "finding",
            "note": f"regime {g!r}" + ("" if i else " (intake/regime.json has no name to compare)")}


def preflight(run: Path) -> dict[str, Any]:
    """All blocking pre-delivery checks. Raises DeliverError on the first refusal."""
    verdict, gate = check_publish(run)
    acc = check_acceptance(run, verdict)
    checks = {
        "CHK-PUBLISH": {"ran": True, "result": "pass", "note": f"verdict {verdict}"},
        "CHK-SUPERSEDED": check_superseded(run),
        "inputs_unchanged": check_inputs_unchanged(run),
        "hash_frozen": check_hash_frozen(run, gate),
        "regime_declared": check_regime(run, gate),
    }
    bad = {k: v["note"] for k, v in checks.items() if v["result"] == "fail"}
    if bad:
        raise DeliverError("pre-delivery check failed: " + json.dumps(bad) +
                           ". Fix the cause (see SKILL.md 'On failure'); never edit qa/ or build/ here.")
    return {"verdict": verdict, "gate": gate, "acceptance": acc, "checks": checks}
