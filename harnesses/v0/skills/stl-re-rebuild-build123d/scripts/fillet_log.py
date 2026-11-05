#!/usr/bin/env python3
"""fillet_log.py - logged fillets/chamfers with target vs used radius (CHK-FILLET).

PROVENANCE
  * try/except per feature with an OK/FAILED log line: generalised from
    golden-examples/dreame_brush-caps/report/source/build_screw.py:44-98 and
    build_snap.py:37-75 (every fillet wrapped, log in report/*_build_log.txt).
  * descending-radius fallback: from
    golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/build_OOM-B02.py:288-298
    (tries R0.8, 0.5, 0.3). FIXED here: the golden printed the radius but never stored
    which one was used, so a smaller radius could ship silently (CHK-FILLET, B02).
  * empty-selection detection: from the P03 failure
    golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/rebuild_OOM-P03.py:148-156, where an
    `if top_edges:` guard and a bare except could skip the fillet with only a print
    (CHK-FILLET, P03). Here an empty selection is logged as NO_EDGES.

STATUS VALUES
  OK             target radius applied, result valid
  REDUCED        a smaller fallback radius was applied (must be declared in MODELING_PLAN.md)
  FAILED         every radius failed; shape returned unchanged (must be declared or fixed)
  NO_EDGES       the selector found no edges; nothing applied (selector bug or geometry changed)
  SELECTOR_ERROR the selector itself raised (a real code bug, distinct from a legitimate
                 empty match) - nothing applied
A result that is not a valid single solid counts as a failed attempt. SELECTOR_ERROR and
NO_EDGES both mean nothing was applied, but only NO_EDGES means the selector ran cleanly
and legitimately matched nothing; treat SELECTOR_ERROR as a bug to fix, not a geometry fact.

LIBRARY USE (inside build/model.py)
  from fillet_log import FilletLog
  flog = FilletLog()
  body = flog.apply(body, "F04 disc top", lambda s: s.edges().filter_by(GeomType.CIRCLE)...,
                    radii=[P["disc_top_fillet"]], param="disc_top_fillet")
  flog.write(build_dir / "fillets.json", build_dir / "build_log.txt")

CLI
  fillet_log.py summarize build/fillets.json   -> table; exit 2 if any non-OK entry
Deterministic: no randomness; entries are kept in call order.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, write_json  # noqa: E402

EdgeSelector = Callable[[Any], Iterable[Any]]


def _is_valid(shape: Any) -> bool:
    """build123d drift: `is_valid` is a property in 0.13 and a method in older releases
    (golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/rebuild_OOM-P03.py:161 shim)."""
    v = getattr(shape, "is_valid", None)
    return bool(v() if callable(v) else v)


class FilletLog:
    """Collects one entry per fillet/chamfer feature, in build order."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.lines: list[str] = []

    def log(self, line: str) -> None:
        """Free-text build-log line (non-fillet features: e.g. 'F05 dimples: tilt <deg> deg')."""
        self.lines.append(line)
        print(line)

    def apply(self, shape: Any, feature: str, select: EdgeSelector, radii: Sequence[float],
              op: str = "fillet", param: str | None = None, why_fallback: str = "") -> Any:
        """Try radii[0] (the target), then each fallback in order. Returns the new shape,
        or the unchanged shape if every radius failed. Never raises."""
        if not radii:
            raise ValueError("radii must hold at least the target radius")
        target = float(radii[0])
        entry: dict[str, Any] = {"feature": feature, "op": op, "param": param, "target": target,
                                 "used": None, "status": "FAILED", "n_edges": 0, "tried": [],
                                 "why_fallback": why_fallback}
        try:
            edges = list(select(shape))
        except Exception as ex:  # selector crashed: record it as a bug, not an empty match
            entry["tried"].append({"radius": None, "error": f"selector: {str(ex)[:160]}"})
            entry["n_edges"] = 0
            entry["status"] = "SELECTOR_ERROR"
            self._record(entry)
            return shape
        entry["n_edges"] = len(edges)
        if not edges:
            entry["status"] = "NO_EDGES"
            self._record(entry)
            return shape
        n_solids_before = len(shape.solids()) if hasattr(shape, "solids") else None
        for r in radii:
            r = float(r)
            try:
                if op == "fillet":
                    new = shape.fillet(r, edges)
                elif op == "chamfer":
                    new = shape.chamfer(r, None, edges)
                else:
                    raise ValueError(f"unknown op {op}")
                if not _is_valid(new):
                    raise RuntimeError("result not valid")
                if n_solids_before is not None and len(new.solids()) != n_solids_before:
                    raise RuntimeError(f"solid count changed {n_solids_before}->{len(new.solids())}")
                entry["tried"].append({"radius": r, "error": None})
                entry["used"] = r
                entry["status"] = "OK" if r == target else "REDUCED"
                self._record(entry)
                return new
            except Exception as ex:
                entry["tried"].append({"radius": r, "error": str(ex)[:160]})
        self._record(entry)
        return shape

    def _record(self, e: dict[str, Any]) -> None:
        self.entries.append(e)
        pre = "R" if e["op"] == "fillet" else "C"
        used = "-" if e["used"] is None else f"{pre}{e['used']:g}"
        self.log(f"{e['feature']} {e['op']} target {pre}{e['target']:g} used {used} on {e['n_edges']} edges "
                 f"{e['status']}" + ("" if e["status"] == "OK" else f" tried={[t['radius'] for t in e['tried']]}"))

    def summary(self) -> dict[str, int]:
        out: dict[str, int] = {"OK": 0, "REDUCED": 0, "FAILED": 0, "NO_EDGES": 0, "SELECTOR_ERROR": 0}
        for e in self.entries:
            out[e["status"]] += 1
        return out

    def write(self, json_path: Path, log_path: Path | None = None, inputs: list[Path] | None = None) -> None:
        res: dict[str, Any] = header("fillets", "fillet_log.py", inputs or [])
        res["check"] = "CHK-FILLET"
        res["fillets"] = self.entries
        res["summary"] = self.summary()
        write_json(json_path, res)
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def summarize(path: Path) -> int:
    d = json.loads(path.read_text(encoding="utf-8"))
    bad = 0
    print(f"{'feature':32s} {'op':8s} {'target':>7s} {'used':>7s} {'edges':>5s} status")
    for e in d.get("fillets", []):
        used = "-" if e["used"] is None else f"{e['used']:g}"
        print(f"{e['feature'][:32]:32s} {e['op']:8s} {e['target']:7g} {used:>7s} {e['n_edges']:5d} {e['status']}")
        bad += e["status"] != "OK"
    print(json.dumps(d.get("summary", {}), sort_keys=True))
    if bad:
        print(f"CHK-FILLET: {bad} non-OK entr{'y' if bad == 1 else 'ies'}; each must be fixed or declared "
              "in build/MODELING_PLAN.md (target vs used radius).", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Logged fillets (CHK-FILLET). CLI summarises a fillets.json.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ps = sub.add_parser("summarize", help="print the fillet table; exit 2 if any entry is not OK")
    ps.add_argument("json", type=Path)
    a = ap.parse_args(argv)
    if not a.json.is_file():
        print(f"no such file: {a.json}", file=sys.stderr)
        return 1
    return summarize(a.json)


if __name__ == "__main__":
    sys.exit(main())
