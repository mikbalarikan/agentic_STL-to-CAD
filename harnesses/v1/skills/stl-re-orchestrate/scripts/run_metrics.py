#!/usr/bin/env python3
"""run_metrics.py - machine-readable summary of one v1 run for the benchmark (bench/README.md).

  python3 run_metrics.py <run>            -> writes <run>/run_metrics.json, prints it

Only what the harness itself can know. Tokens, cost and the agent CLI are recorded by the
benchmark runner, so the numbers stay comparable across models. Every field is read from the
run folder. Nothing is remembered from the conversation, and a missing artefact gives null,
never a guess.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SKILLS_DIR = Path(__file__).resolve().parents[2]


def harness_manifest() -> tuple[dict[str, Any], Path | None]:
    """HARNESS.json of the repo copy (harnesses/<id>/skills/...), or the installer marker
    (.stl_re_harness.json, written by tools/harness.py install) of an installed copy."""
    for d in (SKILLS_DIR.parent, *SKILLS_DIR.parents):
        if (d / "HARNESS.json").is_file():
            return json.loads((d / "HARNESS.json").read_text(encoding="utf-8")), d
    mk = SKILLS_DIR / ".stl_re_harness.json"
    if mk.is_file():
        m = json.loads(mk.read_text(encoding="utf-8"))
        src = Path(m.get("source", "")).parent
        if (src / "HARNESS.json").is_file():
            return json.loads((src / "HARNESS.json").read_text(encoding="utf-8")), src
        return {"id": m.get("version"), "status": None}, None
    return {}, None


def _j(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _commit(where: Path | None) -> str | None:
    if where is None:
        return None
    try:
        return subprocess.run(["git", "-C", str(where), "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip() or None
    except Exception:
        return None


def _stats(block: Any) -> dict[str, Any] | None:
    if not isinstance(block, dict):
        return None
    return {k: block.get(k) for k in ("p50", "p95", "max", "n") if k in block}


def collect(run: Path) -> dict[str, Any]:
    manifest, hdir = harness_manifest()
    gate = _j(run / "qa" / "gate.json") or {}
    regime = _j(run / "intake" / "regime.json") or {}
    refine = _j(run / "refine" / "refine_log.json")
    tlog = _j(run / "build" / "tree_log.json") or {}
    export = _j(run / "build" / "export_check.json") or {}
    repro = _j(run / "deliver" / "repro.json") or {}
    loops = len(list(run.glob("_it*_SUPERSEDED")))

    decisions = {"human": 0, "agent": 0}
    dm = run / "DECISIONS.md"
    if dm.is_file():
        for line in dm.read_text(encoding="utf-8").splitlines():
            if line.startswith("- ") and line.count("|") >= 4:
                who = line.split("|")[1].lower()
                decisions["agent" if any(w in who for w in ("agent", "orchestrator", "builder", "auto"))
                          else "human"] += 1

    ref: dict[str, Any] | None = None
    if refine:
        rounds = refine.get("rounds", [])
        acc = [r["accepted"] for r in rounds if r.get("accepted")]
        cards = refine.get("cards", [])
        ref = {
            "rounds": len(rounds),
            "accepted": len(acc),
            "accepted_kinds": sorted({a["kind"] for a in acc}),
            "refits": sum(1 for a in acc if a["kind"] == "refit"),
            "merges": sum(1 for a in acc if a["kind"] == "slot-merge") + (1 if refine.get("consolidated") else 0),
            "candidates_built": sum(len(r.get("tried", [])) for r in rounds),
            "open_points": len(refine.get("open_points", [])),
            "blend_candidates": len(refine.get("blend_candidates", [])),
            "cards": len(cards),
            "cards_by": {k: sum(1 for c in cards if str(c.get("answered_by", "")).startswith(k))
                         for k in ("auto", "agent", "user")},
            "cards_unanswered": sum(1 for c in cards if c.get("answer") is None),
            "start": (refine.get("start") or {}).get("metrics"),
            "final": (refine.get("final") or {}).get("metrics"),
            "builds": (refine.get("final") or {}).get("builds"),
            "seconds": (refine.get("final") or {}).get("seconds"),
        }

    datum = export.get("datum") or {}
    out = {
        "schema": "run_metrics@v1",
        "harness": {"id": manifest.get("id"), "status": manifest.get("status"), "commit": _commit(hdir)},
        "run": str(run),
        "part": next((p.name[: -len("_datum.step")] for p in (run / "build").glob("*_datum.step")), None),
        "regime": regime.get("name"),
        "verdict": gate.get("verdict"),
        "gate_errors": gate.get("errors"),
        "loops": loops,
        "decisions": decisions,
        "deviation": {
            "label": (gate.get("deviation") or {}).get("label"),
            "scan_to_cad": _stats((gate.get("deviation") or {}).get("scan_to_cad")),
            "scan_to_cad_masked": _stats((gate.get("deviation") or {}).get("scan_to_cad_masked")),
            "cad_to_scan_observable": _stats((gate.get("deviation") or {}).get("cad_to_scan_observable")),
            "unobservable_fraction": (gate.get("deviation") or {}).get("unobservable_fraction"),
            "registration_converged": ((gate.get("registration") or {}).get("converged")),
            "band_fails": gate.get("band_fails"),
            "blockers": gate.get("blockers"),
        },
        "model": {
            "solids": datum.get("solids"), "valid": datum.get("valid"), "faces": datum.get("faces"),
            "volume_mm3": datum.get("volume_mm3"),
            "nodes": len(_j(run / "build" / "feature_tree.json").get("nodes", []))
            if (run / "build" / "feature_tree.json").is_file() else None,
            "build_status": tlog.get("status"), "unused_params": len(tlog.get("unused_params", []) or []),
            "tree_literals": len(tlog.get("literals", []) or []),
        },
        "refine": ref,
        "reproducible": repro.get("reproducible"),
    }
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    run = Path(sys.argv[1]).resolve()
    m = collect(run)
    (run / "run_metrics.json").write_text(json.dumps(m, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(m, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
