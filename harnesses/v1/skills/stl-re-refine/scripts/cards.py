#!/usr/bin/env python3
"""cards.py - list and answer refine-loop decision cards (harness v1).

  python3 cards.py list <refine_dir>
  python3 cards.py answer <refine_dir>/cards/003.json <index> --by "<who>" [--why "..."]

After answering, re-run loop.py with the same arguments: the loop is deterministic, reaches the
same card and applies the answer. Every answer is also a DECISIONS.md line (OTHER) for the run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("dir", type=Path)
    p = sub.add_parser("answer")
    p.add_argument("card", type=Path)
    p.add_argument("index", type=int)
    p.add_argument("--by", required=True)
    p.add_argument("--why", default="")
    a = ap.parse_args()
    if a.cmd == "list":
        for f in sorted((a.dir / "cards").glob("*.json")):
            c = json.loads(f.read_text())
            print(f"{f.name}: round {c['round']} cluster {c['cluster']} answer={c['answer']} by={c['answered_by']}")
            for i, k in enumerate(c["candidates"]):
                print(f"   [{i}] {k['kind']:14s} {k['variant']:12s} J={k['J']:.4f}  {k['name']}")
        return 0
    c = json.loads(a.card.read_text())
    if not 0 <= a.index < len(c["candidates"]):
        print(f"index must be 0..{len(c['candidates']) - 1}", file=sys.stderr)
        return 2
    c["answer"], c["answered_by"], c["why"] = a.index, a.by, a.why
    a.card.write_text(json.dumps(c, indent=2))
    k = c["candidates"][a.index]
    print(f"- <date> | {a.by} | OTHER | refine card {c['card']} (cluster {c['cluster']}): chose {k['kind']} "
          f"{k['variant']} ({k['name']}) {a.why} | {a.card}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
