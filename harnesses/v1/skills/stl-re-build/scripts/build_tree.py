#!/usr/bin/env python3
"""build_tree.py - build a feature tree (JSON) into a validated STEP (stl-re-build, harness v1).

Replaces v0's hand-written build/model.py. The agent writes `build/feature_tree.json` (data);
this one generic, tested script builds it.

  python3 build_tree.py --tree build/feature_tree.json --params measure/params.json \
      --alignment intake/alignment.json --out build --part <part>

Writes into --out:
  tree_log.json   one record per node: status, dv, volume, solids, faces, valid, seconds
  fillets.json    v0 CHK-FILLET format (every fillet/chamfer, target vs used radius)
  build_log.txt   human-readable log
  <part>_datum.step, <part>.step, <part>_cad.stl, export_check.json   (v0 export_frames)

Options: --no-export (build and log only), --datum-step (export the datum-frame STEP
without an alignment), --keep-going (do not stop at the first failed node).

Exit codes: 0 ok; 2 a node failed, the tree failed lint, or export aborted; 3 datum-only
export (scale_factor != 1, same as v0).
This is a builder self-check, not QA (CHK-INDEP).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _common import header, write_json  # noqa: E402
from features import Ctx, lint_tree, run_node  # noqa: E402
from fillet_log import FilletLog  # noqa: E402
from treexpr import Scope, bind_let  # noqa: E402


def load_params(path: Path | None, tree: dict[str, Any]) -> dict[str, dict[str, Any]]:
    params: dict[str, dict[str, Any]] = {}
    if path is not None:
        d = json.loads(path.read_text(encoding="utf-8"))
        params.update(d["params"] if "params" in d else d)
    for k, v in (tree.get("params") or {}).items():   # inline params (tests, examples)
        params[k] = v if isinstance(v, dict) else {"value": v, "source": "inline"}
    for k, v in params.items():
        if "value" not in v or "source" not in v:
            raise SystemExit(f"param {k}: needs value and source (run-contract section 4)")
    return params


def build(tree: dict[str, Any], params: dict[str, dict[str, Any]], keep_going: bool = False,
          until: str | None = None) -> tuple[Any, dict[str, Any], FilletLog]:
    consts = {k: v["value"] for k, v in (tree.get("constants") or {}).items()}
    S = Scope(params, consts)
    flog = FilletLog()
    ctx = Ctx(tree, S)
    errs = lint_tree(tree)
    log: dict[str, Any] = {"lint": errs, "nodes": [], "status": "OK"}
    if errs:
        log["status"] = "LINT_FAILED"
        return None, log, flog
    S.push(bind_let(S, tree.get("let")))
    body = None
    t0 = time.time()
    for node in tree["nodes"]:
        if node.get("skip"):
            log["nodes"].append({"id": node["id"], "status": "SKIPPED", "why": node.get("why", "")})
            continue
        body, rec = run_node(body, node, ctx, flog)
        log["nodes"].append(rec)
        flog.log(f"{rec['id']:6s} {rec['op']:9s} {rec['status']:6s} dv={rec.get('dv', 0):+.3f} "
                 f"vol={rec.get('volume', 0):.3f} solids={rec.get('solids', '-')} faces={rec.get('faces', '-')}"
                 + (f"  ERROR {rec['error']}" if rec["error"] else ""))
        if rec["status"] != "OK":
            log["status"] = "NODE_FAILED"
            if not keep_going and node.get("on_fail", "stop") == "stop":
                break
        if until is not None and node["id"] == until:
            break
    if body is not None:
        body = body.clean()
    log["seconds"] = round(time.time() - t0, 2)
    log["unused_params"] = sorted(set(params) - S.used)
    log["literals"] = [{"node": c, "value": v} for c, v in S.literals]
    log["sketch_fillets"] = ctx.sketch_reports
    if body is not None:
        log["final"] = {"volume": round(float(body.volume), 6), "faces": len(body.faces()),
                        "solids": len(body.solids()), "valid": bool(body.is_valid)}
    return body, log, flog


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build a JSON feature tree into a validated STEP.")
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--params", type=Path, action="append", default=[],
                    help="params file(s); later files override earlier ones (e.g. measure/params_refine.json)")
    ap.add_argument("--alignment", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--part", required=True)
    ap.add_argument("--no-export", action="store_true")
    ap.add_argument("--datum-step", action="store_true", help="export the datum STEP only (no alignment)")
    ap.add_argument("--keep-going", action="store_true")
    ap.add_argument("--until", help="stop after this node id (staged builds)")
    a = ap.parse_args(argv)

    tree = json.loads(a.tree.read_text(encoding="utf-8"))
    params: dict[str, dict[str, Any]] = {}
    for pf in a.params:
        params.update(load_params(pf, {}))
    params.update(load_params(None, tree))
    body, log, flog = build(tree, params, a.keep_going, a.until)
    a.out.mkdir(parents=True, exist_ok=True)
    inputs = [a.tree] + list(a.params)
    res = header("tree_log", "build_tree.py", inputs)
    res.update(log)
    res["part"] = a.part
    write_json(a.out / "tree_log.json", res)
    flog.write(a.out / "fillets.json", a.out / "build_log.txt", inputs=inputs)
    print(json.dumps({"status": log["status"], "lint": log["lint"], "final": log.get("final"),
                      "failed": [n["id"] for n in log["nodes"] if n["status"] == "FAILED"],
                      "unused_params": log.get("unused_params", []),
                      "literals": len(log.get("literals", []))}, indent=2))
    if log["status"] != "OK" or body is None:
        return 2
    if a.no_export:
        return 0
    if a.datum_step or a.alignment is None:
        from build123d import export_step
        export_step(body, str(a.out / f"{a.part}_datum.step"))
        return 0
    from export_frames import ExportAbort, ScaleFrameSkipped, export_frames
    try:
        export_frames(body, a.alignment, a.out, a.part, fillets_json=a.out / "fillets.json",
                      model_py=a.tree.resolve(), params_json=a.params[0] if a.params else None)
    except ScaleFrameSkipped as ex:
        print(f"DATUM-ONLY: {ex}", file=sys.stderr)
        return 3
    except ExportAbort as ex:
        print(f"ABORT: {ex}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
