#!/usr/bin/env python3
"""Pre-delivery gate: may this run be delivered? Prints the checks as JSON; writes nothing.

Runs CHK-PUBLISH (qa/VERDICT.md + qa/gate.json, deliverable verdict, headline agrees with gate.json),
ACCEPT-BAND for BAND_NOT_MET (DECISIONS.md), CHK-SUPERSEDED, input hashes unchanged, STEP hash freeze,
and regime declared at intake. Logic lives in _common.preflight (provenance there).

Exit codes: 0 deliverable; 2 refused (message names the check and the next action).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DeliverError, fail, preflight  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True, type=Path)
    a = ap.parse_args()
    try:
        pf = preflight(a.run.resolve())
    except DeliverError as exc:
        fail(str(exc))
    print(json.dumps({"verdict": pf["verdict"], "acceptance": pf["acceptance"], "checks": pf["checks"]}, indent=2))


if __name__ == "__main__":
    main()
