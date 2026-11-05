#!/usr/bin/env python3
"""Unit tests for the v1 feature-tree builder (no scan needed). Exit 0 = all passed.

  python3 tests/test_features.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_tree import build  # noqa: E402
from sketch2d import build_profile, faces_of  # noqa: E402
from treexpr import ExprError, Scope  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def P(**kw):
    return {k: {"value": v, "source": "test"} for k, v in kw.items()}


def run(nodes, params=None, **tree):
    t = {"nodes": nodes, **tree}
    return build(t, params or {})


def near(a, b, rel=1e-4):
    return abs(a - b) <= rel * max(1.0, abs(b))


# --- expressions -----------------------------------------------------------------------
S = Scope(P(a=2.0, xs=[1, 2, 3]), {"BURY": 0.5})
check("expr arithmetic + params", near(S.num("a*3 + BURY"), 6.5))
check("expr index + conditional", S.num("xs[1] if a > 1 else 0") == 2)
check("expr trig", near(S.num("sind(30)"), 0.5))
for bad in ("__import__('os')", "a.__class__", "open('x')", "lambda: 1"):
    try:
        S.eval(bad)
        check(f"expr rejects {bad!r}", False)
    except ExprError:
        check(f"expr rejects {bad!r}", True)
S2 = Scope(P(a=1.0))
S2.num("a * 7.3")
check("literal 7.3 recorded", any(v == 7.3 for _, v in S2.literals))

# --- sketch ------------------------------------------------------------------------------
S3 = Scope({})
half = build_profile({"items": [{"type": "chain", "pts": [[0, 0], [10, 0]],
                                 "arcs": {"1": {"center": [5, 0], "side": "right"}}}]}, S3)
a = sum(f.area for f in faces_of(half))
check("chain half circle by centre + side", near(a, math.pi * 25 / 2, 1e-6), f"area={a:.5f}")
try:
    build_profile({"items": [{"type": "chain", "pts": [[0, 0], [10, 0]], "arcs": {"1": {"center": [5, 0]}}}]}, S3)
    check("half circle without side refused", False)
except ValueError:
    check("half circle without side refused", True)
# measured centre off the bisector: arc still passes through both end points
f = build_profile({"items": [{"type": "chain", "pts": [[0, 0], [10, 0], [10, 2], [0, 2]],
                              "arcs": {"1": {"center": [7.0, 1.3]}}}]}, S3)
check("off-bisector centre gives a closed face", len(faces_of(f)) == 1 and f.is_valid)
L = {"items": [{"type": "polygon", "pts": [[0, 0], [20, 0], [20, 10], [10, 10], [10, 20], [0, 20]]}]}
a0 = sum(x.area for x in faces_of(build_profile(L, S3)))
reps = []
fl = build_profile(dict(L, fillet_vertices={"r": 2, "select": "concave"}), S3, reps)
a1 = sum(x.area for x in faces_of(fl))
check("concave vertex fillet: exactly 1 vertex", reps[-1]["n_vertices"] == 1, str(reps[-1]))
check("concave fillet adds (1-pi/4) r^2", near(a1 - a0, (1 - math.pi / 4) * 4, 1e-6), f"da={a1 - a0:.5f}")
fo = build_profile(dict(L, offset=-1), S3)
check("inward offset shrinks", sum(x.area for x in faces_of(fo)) < a0)

# --- builder ------------------------------------------------------------------------------
rect = {"items": [{"type": "rect", "c": [0, 0], "w": "w", "h": "h"}]}
pr = P(w=10.0, h=20.0, t=5.0)
body, log, _ = run([{"id": "F01", "op": "extrude", "combine": "new", "sketch": {"plane": "XY", "profile": rect},
                     "amount": "t"}], pr)
check("extrude volume", log["status"] == "OK" and near(body.volume, 1000), f"{log['status']} {log.get('final')}")

body, log, _ = run([{"id": "F01", "op": "extrude", "sketch": {"profile": rect}, "amount": "t", "draft_deg": 5}], pr)
check("draft extrude is smaller", log["status"] == "OK" and body.volume < 1000, f"{body.volume:.2f}")

rz = {"items": [{"type": "polygon", "pts": [[0, 0], ["R", 0], ["R", "H"], [0, "H"]]}]}
body, log, _ = run([{"id": "F01", "op": "revolve", "profile": rz}], P(R=5.0, H=10.0))
check("revolve volume", log["status"] == "OK" and near(body.volume, math.pi * 250), f"{body.volume:.3f}")

base = {"id": "F01", "op": "box", "size": [20, 20, 10], "align": "min"}
body, log, _ = run([base, {"id": "F02", "op": "cylinder", "combine": "cut", "r": 2, "h": 12,
                           "repeat": {"x": [5, 15]}, "let_each": {}, "at": ["x", 10, -1]}])
check("repeated cut holes", log["status"] == "OK" and near(body.volume, 4000 - 2 * math.pi * 4 * 10),
      f"{body.volume:.3f}")

body, log, _ = run([base, {"id": "F02", "op": "cylinder", "combine": "cut", "r": 2, "h": 2, "at": [50, 50, 50]}])
n2 = log["nodes"][1]
check("cut that misses -> FAILED + rolled back", n2["status"] == "FAILED" and n2.get("rolled_back")
      and near(body.volume, 4000), n2["error"])

body, log, _ = run([base, {"id": "F02", "op": "box", "size": [2, 2, 2], "at": [50, 50, 50], "align": "min"}])
check("add that creates a 2nd solid -> FAILED", log["nodes"][1]["status"] == "FAILED", log["nodes"][1]["error"])

body, log, flog = run([base, {"id": "F09", "op": "fillet", "edges": {"geom": "line", "parallel": "Z"}, "r": 1}])
check("fillet vertical edges OK", log["status"] == "OK" and log["nodes"][1]["n_edges"] == 4
      and near(body.volume, 4000 - 4 * (1 - math.pi / 4) * 10)
      and flog.entries[-1]["status"] == "OK", str(log["nodes"][1].get("fillet_status")))

body, log, flog = run([base, {"id": "F09", "op": "fillet", "edges": {"geom": "line", "parallel": "Z"}, "r": 30,
                              "fallbacks": [2]}])
check("fillet falls back and is REDUCED", flog.entries[-1]["status"] == "REDUCED")

_, log, _ = run([base, {"id": "F02", "op": "fillet", "edges": {"parallel": "Z"}, "r": 1},
                 {"id": "F03", "op": "box", "combine": "cut", "size": [2, 2, 20], "at": [10, 10, 0]}])
check("lint: fillet before a later cut needs local", log["status"] == "LINT_FAILED", str(log["lint"]))

port = {"id": "F05", "op": "group", "frame": {"origin": [10, 10, 10], "z_dir": [1, 0, 0]},
        "parts": [{"op": "cylinder", "r": 1, "h": 5}], "combine": "add"}
body, log, _ = run([base, port])
check("frame + group add", log["status"] == "OK" and near(body.volume, 4000 + math.pi * 5 / 2), f"{body.volume:.4f}")

body, log, _ = run([base, {"id": "F06", "op": "box", "size": [2, 4, 4], "at": [21, 5, 5], "align": "min",
                           "mirror": ["YZ"]}])
n6 = log["nodes"][1]
check("mirrored tool off the body -> 2 extra solids caught", n6["status"] == "FAILED")

_, log, _ = run([{"id": "F01", "op": "loft", "ruled": True, "sections": []}])
check("ruled loft refused", log["status"] in ("LINT_FAILED", "NODE_FAILED"))

_, log, _ = run([base], P(unused_one=1.0))
check("unused params reported", log["unused_params"] == ["unused_one"])

n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
print(f"\n{len(RESULTS) - n_fail} passed, {n_fail} failed")
sys.exit(1 if n_fail else 0)
