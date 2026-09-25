#!/usr/bin/env python3
"""Write <run>/deliver/MANIFEST.json: every file in the run with bytes, sha256 and role.

Provenance:
- Shape of `included` / `excluded` (+ `reason`) copied from the golden manifests, e.g.
  golden-examples/OOM-B02_side-brush-3-arm/MANIFEST.json and
  golden-examples/dreame_brush-caps/MANIFEST.json ("excluded entries carry a reason",
  golden-examples/README.md "What was left out (and why)").
- Scan stats + sha256 at intake and hashes of every artefact: SYNTHESIS A1; facet-film T35
  (sidecar manifest with output sha256; analysis/baseline/facet-film-transferable.md).
- Pre-delivery checks (CHK-PUBLISH, ACCEPT-BAND, CHK-SUPERSEDED, input and hash-freeze integrity)
  come from _common.preflight and are recorded in the manifest.

Nothing is excluded silently: a file leaves `included` only through --exclude GLOB=REASON, and
it is then listed under `excluded` with bytes, sha256 and the reason. MANIFEST.json does not list
itself (it cannot hash itself); that is stated in `note`.

Run it LAST: it requires deliver/README.md and deliver/repro.json (definition of done, facet-film T36).
Exit codes: 0 written; 2 refused.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DeliverError, fail, header, load_json, preflight, sha256_file, write_json  # noqa: E402


def role_of(rel: str, part: str) -> str:
    m = re.match(r"_it(\d+)_SUPERSEDED/", rel)
    if m:
        return f"superseded: iteration {m.group(1)} kept intact (CHK-SUPERSEDED)"
    name = rel.rsplit("/", 1)[-1]
    fixed = {
        "input/scan.stl": "evidence: raw scan (never modified)",
        "input/MEASUREMENTS.md": "evidence: caliper sheet filled by a human",
        "input/INPUT_HASHES.json": "evidence: input hashes at init",
        "DECISIONS.md": "record: human decisions (append-only)",
        "intake/INTAKE_CARD.md": "intake: intake card",
        "intake/intake.json": "intake: scan stats and declared regime",
        "intake/MEASUREMENTS.md": "intake: measurement request",
        "intake/alignment.json": "intake: datum alignment (scan -> datum)",
        "measure/params.json": "measure: parameter table, source of truth",
        "measure/PARAM_TABLE.md": "measure: parameter table rendered from params.json",
        "build/MODELING_PLAN.md": "build: written feature plan",
        "build/model.py": "build: editable design-intent source",
        "build/build_log.txt": "build: build log (fillet OK/FAILED)",
        "build/export_check.json": "build: STEP re-import check, both frames",
        f"build/{part}_datum.step": "DELIVERABLE: STEP, datum frame",
        f"build/{part}.step": "DELIVERABLE: STEP, scan frame (overlays the raw scan)",
        f"build/{part}_cad.stl": "preview: tessellated CAD, scan frame",
        "qa/gate.json": "qa: gate numbers and verdict (source for the README)",
        "qa/VERDICT.md": "qa: verdict and reasoning",
        "qa/masks.json": "qa: deviation masks",
        "deliver/README.md": "DELIVERABLE: delivery document (rendered from JSON)",
        "deliver/repro.json": "deliver: fresh-process reproducibility check",
        "deliver/limitations.json": "deliver: limitations, assumptions, claim boundary (prose)",
    }
    if rel in fixed:
        return fixed[rel]
    for prefix, r in (("input/photos/", "evidence: photo"), ("measure/figures/", "measure: figure"),
                      ("qa/overlays/", "qa: overlay image"), ("intake/", "intake: working file"),
                      ("measure/", "measure: working file"), ("build/", "build: working file"),
                      ("qa/", "qa: working file"), ("deliver/", "deliver: file"), ("input/", "evidence: other")):
        if rel.startswith(prefix):
            return r
    return f"unclassified ({name}); review"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB=REASON",
                    help="exclude matching paths (relative to the run) with a stated reason")
    a = ap.parse_args()
    run = a.run.resolve()
    try:
        pf = preflight(run)
        for req in ("deliver/README.md", "deliver/repro.json"):
            if not (run / req).is_file():
                raise DeliverError(f"{req} missing; run repro_check.py and make_readme.py before the manifest")
        if load_json(run / "deliver" / "repro.json").get("reproducible") is not True:
            raise DeliverError("deliver/repro.json is not reproducible; loop back to rebuild")
    except DeliverError as exc:
        fail(str(exc))
    excludes: list[tuple[str, str]] = []
    for e in a.exclude:
        if "=" not in e or not e.split("=", 1)[1].strip():
            fail(f"--exclude {e!r}: use GLOB=REASON; a reason is mandatory")
        g, r = e.split("=", 1)
        excludes.append((g.strip(), r.strip()))

    hashes = run / "input" / "INPUT_HASHES.json"
    part = str(load_json(hashes).get("part", "")) if hashes.is_file() else ""
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for f in sorted(run.rglob("*"), key=lambda p: p.relative_to(run).as_posix()):
        rel = f.relative_to(run).as_posix()
        if f.is_dir() or rel == "deliver/MANIFEST.json":
            continue
        entry: dict[str, Any] = {"path": rel, "bytes": f.stat().st_size, "sha256": sha256_file(f)}
        if f.is_symlink():
            entry["symlink_to"] = str(f.resolve())
        hit = next((r for g, r in excludes if fnmatch.fnmatch(rel, g)), None)
        if hit:
            excluded.append({**entry, "reason": hit})
        else:
            included.append({**entry, "role": role_of(rel, part)})
    unused = [g for g, _ in excludes if not any(fnmatch.fnmatch(x["path"], g) for x in excluded)]

    doc = header("MANIFEST", "make_manifest.py", run,
                 [run / "qa" / "gate.json", run / "deliver" / "README.md", run / "deliver" / "repro.json"])
    doc.update({
        "part": part,
        "verdict": pf["verdict"],
        "regime": (pf["gate"].get("regime") or {}).get("name"),
        "iteration": pf["checks"]["CHK-SUPERSEDED"]["iteration"],
        "acceptance": pf["acceptance"],
        "checks": pf["checks"],
        "deliverables": [x for x in included if x["role"].startswith("DELIVERABLE")],
        "note": "Every file under the run folder is listed in included or excluded (with a reason). "
                "deliver/MANIFEST.json itself is not listed: a file cannot contain its own hash.",
        "unused_excludes": unused,
        "included": included,
        "excluded": excluded,
    })
    write_json(run / "deliver" / "MANIFEST.json", doc)
    unc = [x["path"] for x in included if x["role"].startswith("unclassified")]
    print(f"wrote {run / 'deliver' / 'MANIFEST.json'}  included={len(included)} excluded={len(excluded)}"
          + (f"  unclassified={unc}" if unc else ""))


if __name__ == "__main__":
    main()
