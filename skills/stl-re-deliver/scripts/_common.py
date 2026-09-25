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


def run_main(main_fn: Any) -> None:
    """D15: SKILL.md documents exit 1 as `repro_check.py`'s own "not reproducible" signal, which
    collides with the exit 1 a bare Python traceback gives from any script. Call every script's
    `main()` through this so an unexpected internal error gets its own exit code (3), distinct
    from a deliberate `fail()` (2, `DeliverError`) or `repro_check.py`'s `sys.exit(1)`."""
    try:
        main_fn()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - last-resort guard, see docstring
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(3)


# ------------------------------------------------------------------------ CHK-PUBLISH
def first_verdict_token(text: str) -> str | None:
    """First verdict-vocabulary token in reading order (longest alternative wins)."""
    pat = re.compile(r"(?<![A-Z_])(" + "|".join(sorted(VERDICTS, key=len, reverse=True)) + r")(?![A-Z_])")
    m = pat.search(text)
    return m.group(1) if m else None


def check_publish(run: Path) -> tuple[str, dict[str, Any]]:
    """CHK-PUBLISH + headline-verdict agreement. Returns (verdict, gate).

    verdict.py writes `verdict: null` whenever `errors` is non-empty (a refused proposal must
    never be mistaken for a trustworthy verdict, verdict.py:295-299), and always records which
    verdicts the evidence actually allows in `allowed_verdicts`. Deliver refuses on all three
    failure shapes: a null verdict, a non-empty `errors` list, and a verdict outside
    `allowed_verdicts` (D-review D1/D4: never trust a verdict word alone)."""
    verdict_md = run / "qa" / "VERDICT.md"
    gate_path = run / "qa" / "gate.json"
    if not verdict_md.is_file() or not gate_path.is_file():
        raise DeliverError("CHK-PUBLISH fail: qa/VERDICT.md and qa/gate.json must both exist before "
                           "anything is written to deliver/. Run stl-re-verify first.")
    gate = load_json(gate_path)
    errors = gate.get("errors") or []
    if errors:
        raise DeliverError(f"CHK-PUBLISH fail: qa/gate.json#errors is non-empty ({errors}); verdict.py "
                           "refused to grade this run and wrote verdict: null. Fix the evidence and "
                           "re-run stl-re-verify; never deliver a refused gate.")
    verdict = gate.get("verdict")
    if verdict is None or verdict not in VERDICTS:
        raise DeliverError(f"CHK-PUBLISH fail: qa/gate.json verdict is {verdict!r}; it must be one of "
                           f"{VERDICTS} (run-contract §7). Return to stl-re-verify.")
    allowed = gate.get("allowed_verdicts")
    if allowed and verdict not in allowed:
        raise DeliverError(f"CHK-PUBLISH fail: qa/gate.json verdict {verdict!r} is not one of its own "
                           f"allowed_verdicts {allowed}; the gate is internally inconsistent. Return to "
                           "stl-re-verify.")
    hf = gate.get("hash_frozen") or {}
    if "unchanged" in hf and hf.get("unchanged") is not True:
        raise DeliverError("CHK-PUBLISH fail: qa/gate.json#hash_frozen.unchanged is not true; the STEP "
                           "changed during QA (run-contract §12). Re-run stl-re-verify on the current STEP.")
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


# D4: evidence for an accepted band miss must not live under a stage folder the pipeline
# itself writes (qa/, build/, measure/, intake/, deliver/, an old _itN_SUPERSEDED/) -- otherwise
# any in-run file, including the verifier's own qa/VERDICT.md, would count as the owner's written
# acceptance. It must be a document the owner actually wrote: decisions/ or the run root.
ACCEPT_BAND_FORBIDDEN_PREFIXES = ("qa/", "build/", "measure/", "intake/", "deliver/")


def check_acceptance(run: Path, verdict: str, gate: dict[str, Any]) -> dict[str, str] | None:
    """BAND_NOT_MET: need an ACCEPT-BAND entry in DECISIONS.md whose evidence file exists in the run,
    is not one of verify's/deliver's own output files, names the current gate by hash, and names at
    least one of `gate.json#band_fails` (run-contract §10; orchestrate SKILL.md:106: "which band,
    the number"). This ties the acceptance to THIS gate, so it cannot carry over from an earlier
    iteration's miss (review D4)."""
    if verdict != "BAND_NOT_MET":
        return None
    entries = [e for e in decisions(run, "ACCEPT-BAND") if e["date"] and e["who"] and e["decision"]]
    if not entries:
        raise DeliverError("BAND_NOT_MET stop: DECISIONS.md has no ACCEPT-BAND entry. Stop and ask the "
                           "owner: show the missed band with its number, the per-region explanation and "
                           "the options from qa/VERDICT.md. Write nothing to deliver/ until they answer.")
    acc = entries[-1]
    ev_rel = acc["evidence"].strip("` ")
    if any(ev_rel.startswith(p) or f"/{p}" in ev_rel for p in ACCEPT_BAND_FORBIDDEN_PREFIXES) or \
            re.search(r"_it\d+_SUPERSEDED/", ev_rel):
        raise DeliverError(f"BAND_NOT_MET stop: ACCEPT-BAND evidence {ev_rel!r} is a pipeline output "
                           "(qa/build/measure/intake/deliver or a superseded iteration), not the owner's "
                           "own written acceptance. Save their answer under decisions/ or the run root "
                           "and record that path instead.")
    ev = (run / ev_rel).resolve() if ev_rel else None
    if ev is None or not ev.is_file() or run.resolve() not in ev.parents:
        raise DeliverError(f"BAND_NOT_MET stop: the ACCEPT-BAND evidence path {acc['evidence']!r} is not a "
                           "file inside the run folder. Save the owner's written acceptance there first.")
    gate_path = run / "qa" / "gate.json"
    gate_sha = sha256_file(gate_path) if gate_path.is_file() else ""
    text_and_ev = f"{acc['decision']} {ev.read_text(encoding='utf-8', errors='replace')}"
    cites_gate = (gate_sha and gate_sha[:12] in text_and_ev) or (str(gate.get("created", "")) and
                                                                 str(gate["created"]) in text_and_ev)
    if not cites_gate:
        raise DeliverError("BAND_NOT_MET stop: ACCEPT-BAND does not reference this gate (no sha256 "
                           f"prefix of the current qa/gate.json, {gate_sha[:12]!r}, or its `created` "
                           "timestamp in the decision or its evidence file); re-ask the owner. An "
                           "acceptance must name the gate it accepts, so it cannot survive into a new one.")
    band_fails = gate.get("band_fails") or []
    if band_fails and not any(bf.split(":", 1)[0].strip() in text_and_ev for bf in band_fails):
        raise DeliverError(f"BAND_NOT_MET stop: ACCEPT-BAND does not name any of gate.json#band_fails "
                           f"{band_fails}; re-ask the owner to say which band they are accepting.")
    acc["evidence"] = ev.relative_to(run.resolve()).as_posix()
    return acc


# ---------------------------------------------------------------------- CHK-SUPERSEDED
def _superseded_route(run: Path, n: int) -> str:
    """The route recorded in `_itN_SUPERSEDED/ROUTE` by `init_run.py supersede` (R2-O1). A
    folder with no marker (pre-dates the marker, or was moved by hand) counts as an ordinary
    REVISE loop, which is the safe default."""
    marker = run / f"_it{n}_SUPERSEDED" / "ROUTE"
    if marker.is_file():
        route = marker.read_text(encoding="utf-8").strip()
        if route:
            return route
    return "measure"


def check_superseded(run: Path) -> dict[str, Any]:
    """Every earlier iteration must be kept intact in _itN_SUPERSEDED/ (N = 1..k, contiguous).

    R2-O1: a `--route repro` folder (`init_run.py supersede --route repro`, after a
    `repro_check.py` failure) is accepted without `qa/gate.json#verdict == REVISE` -- it was
    never a REVISE loop -- and does not count toward the 3-loop bound. Folder numbering
    (`its`) still includes it, since `init_run.py` never renumbers folders."""
    its = sorted(int(m.group(1)) for p in run.iterdir()
                 if p.is_dir() and (m := re.fullmatch(r"_it(\d+)_SUPERSEDED", p.name)))
    problems: list[str] = []
    notes: list[str] = []
    if its != list(range(1, len(its) + 1)):
        problems.append(f"superseded folders are not contiguous from 1: {its}")
    loop_its = []
    for n in its:
        d = run / f"_it{n}_SUPERSEDED"
        route = _superseded_route(run, n)
        is_repro = route == "repro"
        if not is_repro:
            loop_its.append(n)
        required = ("qa/VERDICT.md", "qa/gate.json") if is_repro else \
            ("qa/VERDICT.md", "qa/gate.json", "build/model.py")
        for rel in required:
            if not (d / rel).is_file():
                problems.append(f"_it{n}_SUPERSEDED/{rel} missing")
        if (d / "qa" / "gate.json").is_file():
            try:
                v = json.loads((d / "qa" / "gate.json").read_text(encoding="utf-8")).get("verdict")
            except json.JSONDecodeError:
                v = None
            if not is_repro and v != "REVISE":
                problems.append(f"_it{n}_SUPERSEDED/qa/gate.json verdict is {v!r}, expected REVISE")
        if not list((d / "build").glob("*.step")) if (d / "build").is_dir() else True:
            notes.append(f"_it{n}_SUPERSEDED has no STEP (finding, not a failure: the build may have aborted)")
    iteration = len(loop_its) + 1
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
        # run-contract §10: init_run.py always writes this file. Its absence means evidence
        # integrity is simply unprovable, not merely unchecked, so this fails rather than a
        # softer "finding" (review D13); the caller HALTs (orchestrator §6).
        return {"ran": True, "result": "fail",
                "note": "input/INPUT_HASHES.json missing; evidence integrity unprovable; HALT (orchestrator §6)"}
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
    """The STEP files in build/ must be the ones QA hashed (qa/gate.json#hash_frozen).

    Shape (run-contract §12): `{"before": {path: sha256}, "after": {path: sha256}, "unchanged":
    bool}`. `unchanged is False` means the STEP changed mid-QA and is a hard fail regardless of
    what build/ holds now (review D10); CHK-PUBLISH already refuses this earlier, so reaching
    here with `unchanged: False` should not happen, but this check still fails closed. When
    `after` exists, match against `after`'s hashes only (never pool `before` in with it: a STEP
    that merely matches the PRE-QA hash was never actually gated)."""
    hf = gate.get("hash_frozen") or {}
    if hf.get("unchanged") is False:
        return {"ran": True, "result": "fail", "note": "qa/gate.json#hash_frozen.unchanged is false: "
                "the STEP changed during QA"}
    frozen = _hexes(hf["after"]) if isinstance(hf.get("after"), dict) else _hexes(hf)
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


# ------------------------------------------------------------------------- repro freshness
def check_repro_fresh(run: Path, repro: dict[str, Any]) -> None:
    """D3: `deliver/repro.json#inputs` records the sha256 (run-contract §2 header) of every file
    the rebuild read (`build/model.py`, `measure/params.json`, the delivered STEPs) at the moment
    it was checked. `deliver/` survives an `init_run.py supersede`, so an old repro.json can
    otherwise certify a `model.py` that no longer produces the delivered STEP. Recompute each
    hash now and refuse if any differ."""
    stale = []
    for rel, sha in (repro.get("inputs") or {}).items():
        f = run / rel
        if not f.is_file() or sha256_file(f) != sha:
            stale.append(rel)
    if stale:
        raise DeliverError(f"deliver/repro.json is stale ({', '.join(stale)} changed since the repro "
                           "check ran); re-run scripts/repro_check.py before rendering the README or "
                           "the manifest.")


def preflight(run: Path) -> dict[str, Any]:
    """All blocking pre-delivery checks. Raises DeliverError on the first refusal."""
    verdict, gate = check_publish(run)
    acc = check_acceptance(run, verdict, gate)
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
