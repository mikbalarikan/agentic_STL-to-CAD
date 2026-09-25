#!/usr/bin/env python3
"""_common.py - shared helpers for the stl-re-rebuild-build123d scripts.

PROVENANCE
  NEW CODE. Implements the common JSON header of
  skills/stl-re-orchestrate/references/run-contract.md section 2
  ({schema, tool, tool_version, inputs{path: sha256}, seed, created}).
  The `created` convention (SOURCE_DATE_EPOCH pins it) follows
  skills/stl-re-orchestrate/scripts/init_run.py:97-103.

Determinism: nothing here reads the clock except `created_stamp`, which is provenance
only and never feeds a computation. JSON is written with sorted keys.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any

TOOL_VERSION = "stl-re-rebuild-build123d@1"


def sha256_file(path: Path) -> str:
    """sha256 of a file, streamed."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def created_stamp() -> str:
    """Provenance-only ISO timestamp; SOURCE_DATE_EPOCH pins it (reproducible output)."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch is not None:
        t = _dt.datetime.fromtimestamp(int(epoch), tz=_dt.timezone.utc)
    else:
        t = _dt.datetime.now(tz=_dt.timezone.utc)
    return t.replace(microsecond=0).isoformat()


def header(schema_file: str, tool: str, inputs: list[Path], seed: int = 0) -> dict[str, Any]:
    """Run-contract section 2 header. `inputs` are hashed (missing files hash to null)."""
    return {
        "schema": f"stl-re/{schema_file}@1",
        "tool": tool,
        "tool_version": TOOL_VERSION,
        "inputs": {str(p): (sha256_file(p) if Path(p).is_file() else None) for p in inputs},
        "seed": seed,
        "created": created_stamp(),
    }


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def r6(x: float) -> float:
    """Round for JSON so tiny float noise does not break the two-process determinism check."""
    return float(round(float(x), 6))
