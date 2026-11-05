"""refine_ops.py - re-fit existing nodes and merge features into design intent (harness v1, M2.1).

Two jobs the add-only loop could not do (open points 1 and 3, harnesses/v1/README.md):

refit_candidate()
  A thin cluster on a face of an EXISTING node usually means that node's size is a little off
  (a revolve step end, a pocket floor). Instead of patching it with a new feature, adjust the
  numeric params of the nodes whose tool lies at the cluster. Damped Gauss-Newton on the
  cluster's signed distances, with one finite-difference build per variable, measured on the
  cluster points only. A refit adds no faces. The new values keep source "scan" with an
  estimator that says they were refitted.

slot_merge() / consolidate()
  Parallel cylinder bosses of the same radius in pairs are the two round ends of ONE body: a
  stadium (slot) prism. The OD-H22 port clip blocks were found as corner cylinders (r 1.88 =
  half the block thickness). The merge rewrites them as one slot prism per pair and keeps it
  when J is not worse than the cylinders by more than OCCAM_TOL. Fewer, intent-ful features
  win near-ties.
"""
from __future__ import annotations

import copy
import json
import math
import re
from typing import Any, Callable

import numpy as np

from classify import Namer, basis, unit

OCCAM_TOL = 0.01          # a simpler model may be up to 1 % worse in J and still win
NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _names_in(node: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(node, str):
        out |= set(NAME_RE.findall(node))
    elif isinstance(node, list):
        for x in node:
            out |= _names_in(x)
    elif isinstance(node, dict):
        for k, v in node.items():
            if k not in ("id", "name", "op", "combine", "why", "type"):
                out |= _names_in(v)
    return out


def _overlap(bb: list | None, lo: np.ndarray, hi: np.ndarray, pad: float) -> bool:
    if not bb:
        return False
    return bool(np.all(np.array(bb[0]) < hi + pad) and np.all(np.array(bb[1]) > lo - pad))


def refit_variables(tree: dict[str, Any], params: dict[str, Any], log: dict[str, Any],
                    cluster: dict[str, Any], max_vars: int = 12) -> list[tuple[str, int | None]]:
    """(param, element index or None) of mm/deg params used by nodes whose tool lies at the cluster."""
    lo, hi = np.array(cluster["bbox"][0]), np.array(cluster["bbox"][1])
    bbs = {n["id"]: n.get("tool_bbox") for n in log.get("nodes", [])}
    consts = set((tree.get("constants") or {}).keys()) | set((tree.get("let") or {}).keys())
    out: list[tuple[str, int | None]] = []
    for n in tree["nodes"]:
        if not _overlap(bbs.get(n["id"]), lo, hi, 0.5):
            continue
        for name in sorted(_names_in(n) - consts):
            p = params.get(name)
            if p is None or p.get("unit") in ("-", "count") or p.get("source") in ("caliper", "operator-spec"):
                continue                      # directions, counts and caliper values are not refitted
            v = p["value"]
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append((name, None))
            elif isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v):
                out += [(name, k) for k in range(len(v))]
    return out[:max_vars]


def _with(params: dict[str, Any], var: tuple[str, int | None], delta: float) -> dict[str, Any]:
    name, k = var
    p2 = dict(params)
    spec = dict(p2[name])
    if k is None:
        spec["value"] = float(spec["value"]) + delta
    else:
        v = list(spec["value"])
        v[k] = float(v[k]) + delta
        spec["value"] = v
    p2[name] = spec
    return p2


def refit_candidate(tree: dict[str, Any], params: dict[str, Any], log: dict[str, Any], cluster: dict[str, Any],
                    P: np.ndarray, local_dist: Callable[[dict[str, Any], dict[str, Any], np.ndarray], np.ndarray | None],
                    tag: str) -> dict[str, Any] | None:
    """Gauss-Newton step on the cluster's signed distances over the nearby nodes' params."""
    vars_ = refit_variables(tree, params, log, cluster)
    if not vars_:
        return None
    Q = P[cluster["idx"]]
    if len(Q) > 3000:
        Q = Q[np.random.default_rng(0).choice(len(Q), 3000, replace=False)]
    d0 = local_dist(tree, params, Q)
    if d0 is None:
        return None
    r0 = np.clip(d0, -2.0, 2.0)
    cols, used = [], []
    for var in vars_:
        eps = 0.2 if params[var[0]].get("unit") == "deg" else 0.05
        d1 = local_dist(tree, _with(params, var, eps), Q)
        if d1 is None:
            continue
        g = (np.clip(d1, -2.0, 2.0) - r0) / eps
        if np.abs(g).max() < 1e-3:
            continue                          # this variable does not move the cluster
        cols.append(g)
        used.append(var)
    if not cols:
        return None
    Jm = np.stack(cols, 1)
    lam = 1e-2 * np.trace(Jm.T @ Jm) / Jm.shape[1]
    step = np.linalg.solve(Jm.T @ Jm + lam * np.eye(Jm.shape[1]), -Jm.T @ r0)
    step = np.clip(step, -2 * np.abs(r0).max(), 2 * np.abs(r0).max())
    p2 = params
    changes = {}
    for var, s in zip(used, step):
        if abs(s) < 1e-4:
            continue
        p2 = _with(p2, var, float(s))
        changes[f"{var[0]}" + (f"[{var[1]}]" if var[1] is not None else "")] = round(float(s), 4)
    if not changes:
        return None
    new_params = {}
    for name in {v[0] for v in used}:
        spec = dict(p2[name])
        spec["source"] = "scan"
        spec["estimator"] = (str(spec.get("estimator", "")) + f"; refit ({tag}) on cluster n={cluster['n']}").strip("; ")
        spec["rule"] = "keep-measured"
        new_params[name] = spec
    return {"kind": "refit", "variant": f"{len(changes)} vars", "geom_score": -5.0, "node": None,
            "params": new_params, "changes": changes, "size": [], "axis": [0, 0, 1], "explains": cluster["n"],
            "members": None, "name": "refit " + ", ".join(f"{k} {v:+.3f}" for k, v in list(changes.items())[:6])}


# --------------------------------------------------------------------------- slot merge
def move_before_cuts(tree: dict[str, Any], node_id: str, log_nodes: list[dict[str, Any]]) -> dict[str, Any] | None:
    """An add node placed after cuts it overlaps refills them (a block refilling a bore). Return the
    tree with that add moved just before the earliest overlapping cut, or None if nothing to move."""
    bbs = {n["id"]: n.get("tool_bbox") for n in log_nodes}
    ids = [n["id"] for n in tree["nodes"]]
    if node_id not in ids or not bbs.get(node_id):
        return None
    me = bbs[node_id]
    lo, hi = np.array(me[0]), np.array(me[1])
    k = ids.index(node_id)
    first = None
    for i, n in enumerate(tree["nodes"][:k]):
        if n.get("combine") == "cut" and _overlap(bbs.get(n["id"]), lo, hi, 0.0):
            first = i
            break
    if first is None:
        return None
    nodes = list(tree["nodes"])
    node = nodes.pop(k)
    nodes.insert(first, node)
    return dict(tree, nodes=nodes)


def cylinder_rods(tree: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
    """Every added cylinder instance (boss) as an axis rod: node id, r, axis d, centre line, t-range."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "stl-re-build" / "scripts"))
    from treexpr import Scope, bind_let, repeat_instances
    consts = {k: v["value"] for k, v in (tree.get("constants") or {}).items()}
    S = Scope(params, consts)
    S.push(bind_let(S, tree.get("let")))
    rods = []
    for n in tree["nodes"]:
        if n.get("op") != "cylinder" or n.get("combine", "add") != "add":
            continue
        fr_key = "frame_each" if "frame_each" in n else ("frame" if "frame" in n else None)
        if fr_key is None or not isinstance(n[fr_key], dict) or "origin" not in n[fr_key]:
            continue
        for inst in repeat_instances(S, n.get("repeat")):
            S.push(inst)
            try:
                c = np.array(S.vec(n[fr_key]["origin"], 3))
                d = unit(np.array(S.vec(n[fr_key]["z_dir"], 3)))
                r = S.num(n["r"])
                h = S.num(n["h"])
                t0 = S.num(n["at"][2]) if "at" in n else 0.0
            finally:
                S.pop()
            if d @ np.array([1.0, 1e-3, 1e-6]) < 0:          # orient all rods the same way
                d, c, t0 = -d, c, -(t0 + h)
            q = c - (c @ d) * d
            rods.append({"node": n["id"], "r": r, "d": d, "q": q, "t": (c @ d + t0, c @ d + t0 + h),
                         "p0": c + t0 * d, "p1": c + (t0 + h) * d})
    return rods


def slot_merge(tree: dict[str, Any], params: dict[str, Any], tag: str, noise: float,
               rods: list[dict[str, Any]] | None = None) -> tuple[dict[str, Any], dict[str, Any], set[str]] | None:
    """Pair parallel same-radius rods into stadium prisms. Returns (node, params, replaced node ids)."""
    rods = rods if rods is not None else cylinder_rods(tree, params)
    if len(rods) < 2:
        return None
    # group by (direction, radius), then merge rods that share a centre line
    groups: list[list[dict[str, Any]]] = []
    for rd in rods:
        for g in groups:
            if abs(abs(g[0]["d"] @ rd["d"]) - 1) < 1 - math.cos(math.radians(3)) and abs(g[0]["r"] - rd["r"]) < max(4 * noise, 0.05) + 0.03 * rd["r"]:
                g.append(rd)
                break
        else:
            groups.append([rd])
    nm = Namer(tag)
    slots = []
    replaced: set[str] = set()
    for g in groups:
        D = unit(sum(rd["d"] * np.sign(rd["d"] @ g[0]["d"]) for rd in g))
        for rd in g:                         # re-project every rod of the group on the common axis D
            a_, b_ = rd["p0"] @ D, rd["p1"] @ D
            rd["q"] = rd["p0"] - a_ * D
            rd["t"] = (min(a_, b_), max(a_, b_))
            rd["d"] = D
        lines: list[dict[str, Any]] = []
        for rd in g:
            for ln in lines:
                if np.linalg.norm(ln["q"] - rd["q"]) < max(0.5, 0.25 * rd["r"]):
                    ln["t"] = (min(ln["t"][0], rd["t"][0]), max(ln["t"][1], rd["t"][1]))
                    ln["nodes"].add(rd["node"])
                    break
            else:
                lines.append({"q": rd["q"].copy(), "t": rd["t"], "r": rd["r"], "d": rd["d"], "nodes": {rd["node"]}})
        if len(lines) < 2:
            continue
        free = list(range(len(lines)))
        while len(free) >= 2:                                # greedy mutual-nearest pairing
            best = None
            for i in free:
                for j in free:
                    if j <= i:
                        continue
                    dist = float(np.linalg.norm(lines[i]["q"] - lines[j]["q"]))
                    if dist > 2 * lines[i]["r"] and (best is None or dist < best[0]):
                        best = (dist, i, j)
            if best is None:
                break
            _, i, j = best
            free.remove(i)
            free.remove(j)
            A, B = lines[i], lines[j]
            d = A["d"]
            u = unit(B["q"] - A["q"])
            t0, t1 = min(A["t"][0], B["t"][0]), max(A["t"][1], B["t"][1])
            mid = (A["q"] + B["q"]) / 2
            r = (A["r"] + B["r"]) / 2
            slots.append({"origin": mid + t0 * d, "d": d, "u": u, "L": float(np.linalg.norm(B["q"] - A["q"])) + 2 * r,
                          "W": 2 * r, "len": t1 - t0})
            replaced |= A["nodes"] | B["nodes"]
    if not slots:
        return None
    est = "refine_ops.slot_merge: two parallel round ends of equal radius = one stadium prism"
    ev = f"merged cylinder nodes {sorted(replaced)}"
    k = len(slots)
    L = [s["L"] for s in slots]
    W = [s["W"] for s in slots]
    node = {"op": "extrude", "combine": "add", "name": f"slot prism x{k} (merged round ends)",
            "repeat": {"i": list(range(k))},
            "sketch": {"plane": {"origin": nm.p("c", [s["origin"] for s in slots], "mm", est, ev) + "[i]",
                                 "z_dir": nm.p("d", [s["d"] for s in slots], "-", est, ev) + "[i]",
                                 "x_dir": nm.p("u", [s["u"] for s in slots], "-", est, ev) + "[i]"},
                       "profile": {"items": [{"type": "slot", "c": [0, 0],
                                              "length": (nm.p("L", float(np.mean(L)), "mm", est, ev) if np.ptp(L) < 4 * noise
                                                         else nm.p("L", L, "mm", est, ev) + "[i]"),
                                              "width": (nm.p("W", float(np.mean(W)), "mm", est, ev) if np.ptp(W) < 4 * noise
                                                        else nm.p("W", W, "mm", est, ev) + "[i]")}]}},
            "amount": nm.p("len", [s["len"] for s in slots], "mm", est, ev) + "[i]"}
    return node, nm.params, replaced


def consolidate(tree: dict[str, Any], params: dict[str, Any], evaluate: Callable, cur_J: float, tag: str,
                noise: float, repair: Callable | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    """Replace paired cylinder bosses already in the tree by slot prisms if J allows (Occam).

    The merged body may fill cuts the cylinders never covered (the OD-H22 clip slots run through
    the block). So before comparing, `repair` gets up to two rounds of cut features inside the
    merged region. The merge wins when the repaired J is within OCCAM_TOL of the current J."""
    res = slot_merge(tree, params, tag, noise)
    if res is None:
        return None
    node, sp, replaced = res
    node["id"] = tag
    # the merged body takes the place of the first replaced node, so later cuts still cut it
    at = min(i for i, n in enumerate(tree["nodes"]) if n["id"] in replaced)
    nodes = [n for n in tree["nodes"] if n["id"] not in replaced]
    nodes.insert(at, node)
    t2 = dict(tree, nodes=nodes)
    p2 = {**params, **sp}
    r = evaluate(t2, p2)
    if not r["ok"]:
        return None
    moved = move_before_cuts(t2, tag, r["log"]["nodes"])
    if moved is not None:
        r2 = evaluate(moved, p2)
        if r2["ok"] and r2["m"]["J"] < r["m"]["J"]:
            t2, r = moved, r2
    info = {"replaced": sorted(replaced), "J_merge": r["m"]["J"], "repairs": []}
    if repair is not None and r["m"]["J"] > cur_J * (1 + OCCAM_TOL):
        bb = next((n.get("tool_bbox") for n in r["log"]["nodes"] if n["id"] == tag), None)
        t2, p2, r, info["repairs"], sp_extra = repair(t2, p2, r, bb, tag)
        sp = {**sp, **sp_extra}
    if r["m"]["J"] > cur_J * (1 + OCCAM_TOL):
        return None
    info.update(J=r["m"]["J"], faces=r["faces"], result=r, params=sp)
    return t2, p2, info
