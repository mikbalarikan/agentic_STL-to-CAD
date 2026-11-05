"""classify.py - turn one red cluster into ranked feature hypotheses (harness v1 refine loop).

Input: the cluster's scan points and normals (datum frame), its sign (+ = material missing in
the CAD, - = extra CAD material), the current CAD mesh, the scan noise and spacing, and the
tree's sketch profiles. Output: candidate tree nodes, each carrying its own named params
(source "scan", estimator "classify.py ..."), so the tree has no literals.

A cluster may hold several features (for example two ports joined through a rib). Every
hypothesis is fitted by RANSAC to the SUBSET of the cluster it explains. The loop adds one
feature per round, and what is left becomes the next round's cluster. Hypotheses:

  cylinder      2-point RANSAC (axis = n1 x n2, centre from the two normal lines), refined on
                the inliers. Concave = hole/bore (cut), convex = boss (add).
  revolve       on a convex cylinder's axis: every point whose normal line meets the axis,
                plus the annular faces. The (t, r) meridian is fitted as at most 6 radius steps.
  prism         an extrude direction d (datum axes, normal eigen-directions) whose walls are
                perpendicular to d and caps parallel to it. The footprint along d is fitted as
                a line/arc chain (v1 measure sketchfit.auto_topology), a rectangle, or a
                circle. Optional draft from the wall normals.
  offset-pocket an existing sketch profile of the tree, offset by a fitted wall thickness and
                cut from a fitted floor (the OD-H12 hull+offset idiom).

Footprints that need more than MAX_SEG segments are refused: no pads that trace a cluster
outline ("mud stains", owner decision, nx-reference left_thigh). Directions within SNAP_DEG of
a datum axis snap to it, and axis coordinates within SNAP_MM of 0 snap to 0. Per-instance
angles stay as measured.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "stl-re-measure-intent" / "scripts"))

MAX_SEG = 12
SNAP_DEG = 2.0
SNAP_MM = 0.05
WALL_DEG = 12.0
AXES = {"X": np.array([1.0, 0, 0]), "Y": np.array([0, 1.0, 0]), "Z": np.array([0, 0, 1.0])}


# --------------------------------------------------------------------------- small math
def unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def unit_rows(A: np.ndarray) -> np.ndarray:
    return A / np.maximum(np.linalg.norm(A, axis=1), 1e-12)[:, None]


def snap_dir(a: np.ndarray, snap_deg: float = SNAP_DEG) -> tuple[np.ndarray, str | None]:
    a = unit(np.asarray(a, float))
    for name, e in AXES.items():
        if abs(abs(a @ e) - 1) < 1 - math.cos(math.radians(snap_deg)):
            return e * np.sign(a @ e), name
    b = a.copy()
    b[np.abs(b) < math.sin(math.radians(snap_deg))] = 0.0
    return unit(b), None


def snap_axis_point(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Snap the axis position (perpendicular to a) to datum planes; keep the along-axis part."""
    t = c @ a
    q = c - t * a
    q[np.abs(q) < SNAP_MM] = 0.0
    return q + t * a


def basis(d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h = min(AXES.values(), key=lambda e: abs(e @ d))
    u = unit(np.cross(h, d))
    v = np.cross(d, u)
    return u, v


def circle_fit(xy: np.ndarray) -> tuple[np.ndarray, float, float]:
    A = np.c_[2 * xy, np.ones(len(xy))]
    b = (xy ** 2).sum(1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    c = sol[:2]
    r = math.sqrt(max(sol[2] + c @ c, 1e-12))
    res = np.linalg.norm(xy - c, axis=1) - r
    return c, r, float(np.sqrt(np.mean(res ** 2)))


def angular_coverage(xy: np.ndarray, c: np.ndarray) -> float:
    th = np.sort(np.arctan2(xy[:, 1] - c[1], xy[:, 0] - c[0]))
    gaps = np.diff(np.r_[th, th[0] + 2 * np.pi])
    return float(360 - math.degrees(gaps.max()))


def line_line_dist(P: np.ndarray, N: np.ndarray, c: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Distance between each normal line (P_i, N_i) and the axis line (c, a)."""
    cr = np.cross(N, a)
    nn = np.linalg.norm(cr, axis=1)
    return np.abs(((P - c) * cr).sum(1)) / np.maximum(nn, 1e-9)


class Namer:
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.params: dict[str, dict[str, Any]] = {}

    def p(self, field: str, value: Any, unit_: str, estimator: str, evidence: str) -> str:
        name = f"{self.tag}_{field}"
        if isinstance(value, (list, tuple, np.ndarray)):
            v = np.round(np.asarray(value, float), 4).tolist()
        else:
            v = round(float(value), 4)
        self.params[name] = {"value": v, "unit": unit_, "source": "scan", "rule": "keep-measured",
                             "estimator": estimator, "evidence": evidence, "measured": v,
                             "uncertainty_mm": None, "critical": False}
        return name


def frame_params(nm: Namer, c: np.ndarray, d: np.ndarray, est: str, ev: str) -> dict[str, str]:
    u, _ = basis(d)
    return {"origin": nm.p("c", c, "mm", est, ev), "z_dir": nm.p("d", d, "-", est, ev),
            "x_dir": nm.p("u", u, "-", est, ev)}


# --------------------------------------------------------------------------- RANSAC cylinder
def ransac_cylinder(P: np.ndarray, N: np.ndarray, tol: float, iters: int = 400, seed: int = 0,
                    r_max: float = 50.0) -> dict[str, Any] | None:
    from scipy.spatial import cKDTree
    n = len(P)
    if n < 60:
        return None
    rng = np.random.default_rng(seed)
    tree = cKDTree(P)
    best = None
    sin_w = math.sin(math.radians(10))
    for _ in range(iters):
        i = rng.integers(n)
        nb = tree.query_ball_point(P[i], 4.0)
        if len(nb) < 5:
            continue
        j = nb[rng.integers(len(nb))]
        a = np.cross(N[i], N[j])
        if np.linalg.norm(a) < 0.2:
            continue
        a = unit(a)
        u, v = basis(a)
        p1, p2 = np.array([P[i] @ u, P[i] @ v]), np.array([P[j] @ u, P[j] @ v])
        d1, d2 = unit(np.array([N[i] @ u, N[i] @ v])), unit(np.array([N[j] @ u, N[j] @ v]))
        M = np.c_[d1, -d2]
        if abs(np.linalg.det(M)) < 1e-3:
            continue
        s, _ = np.linalg.solve(M, p2 - p1)
        c2 = p1 + s * d1
        r = float(np.linalg.norm(p1 - c2))
        if r < 0.3 or r > r_max:
            continue
        c3 = c2[0] * u + c2[1] * v
        inl = _cyl_inliers(P, N, c3, a, r, tol, sin_w)
        k = int(inl.sum())
        if best is None or k > best["k"]:
            best = {"k": k, "c": c3, "a": a, "r": r}
    if best is None or best["k"] < 60:
        return None
    # refine on the inliers: axis = least-normal direction, then a circle fit
    c, a, r = best["c"], best["a"], best["r"]
    for _ in range(2):
        inl = _cyl_inliers(P, N, c, a, r, tol, sin_w)
        if inl.sum() < 60:
            return None
        w, V = np.linalg.eigh(N[inl].T @ N[inl])
        a = V[:, 0] * np.sign(V[:, 0] @ a)
        u, v = basis(a)
        m = P[inl].mean(0)
        uv = np.c_[(P[inl] - m) @ u, (P[inl] - m) @ v]
        cc, r, rms = circle_fit(uv)
        c = m + cc[0] * u + cc[1] * v
    inl = _cyl_inliers(P, N, c, a, r, tol, sin_w)
    if inl.sum() < 60:
        return None
    rel = (P[inl] - c) - np.outer((P[inl] - c) @ a, a)
    concave = float(np.mean(np.einsum("ij,ij->i", unit_rows(rel), N[inl]))) < 0
    u, v = basis(a)
    uv = np.c_[(P[inl] - c) @ u, (P[inl] - c) @ v]
    return {"c": c, "a": a, "r": float(r), "inliers": inl, "n": int(inl.sum()), "rms": rms,
            "concave": concave, "coverage": angular_coverage(uv, np.zeros(2))}


def _cyl_inliers(P, N, c, a, r, tol, sin_w):
    rel = (P - c) - np.outer((P - c) @ a, a)
    dist = np.linalg.norm(rel, axis=1)
    radial = np.abs(np.einsum("ij,ij->i", rel / np.maximum(dist, 1e-9)[:, None], N))
    return (np.abs(dist - r) < tol) & (np.abs(N @ a) < sin_w) & (radial > math.cos(math.radians(20)))


# --------------------------------------------------------------------------- meridian steps
def meridian_steps(t: np.ndarray, r: np.ndarray, bin_w: float, tol: float, min_len: float) -> list[list[float]]:
    lo, hi = float(t.min()), float(t.max())
    nb = max(int(math.ceil((hi - lo) / bin_w)), 1)
    edges = lo + bin_w * np.arange(nb + 1)
    idx = np.clip(((t - lo) / bin_w).astype(int), 0, nb - 1)
    env = np.full(nb, np.nan)
    for b in range(nb):
        rb = r[idx == b]
        if len(rb) >= 3:
            env[b] = np.percentile(rb, 90)
    ok = ~np.isnan(env)
    if ok.sum() < 2:
        return []
    env = np.interp(np.arange(nb), np.where(ok)[0], env[ok])
    steps: list[list[float]] = []
    s0, vals = 0, [env[0]]
    for b in range(1, nb):
        if abs(env[b] - np.median(vals)) > tol:
            steps.append([edges[s0], edges[b], float(np.median(vals))])
            s0, vals = b, [env[b]]
        else:
            vals.append(env[b])
    steps.append([edges[s0], edges[nb], float(np.median(vals))])
    while len(steps) > 1:
        short = [i for i, s in enumerate(steps) if s[1] - s[0] < min_len]
        if not short:
            break
        i = short[0]
        j = i + 1 if i == 0 else (i - 1 if i == len(steps) - 1 else
                                  (i - 1 if abs(steps[i - 1][2] - steps[i][2]) <= abs(steps[i + 1][2] - steps[i][2]) else i + 1))
        a_, b_ = sorted((i, j))
        keep = steps[a_][2] if steps[a_][1] - steps[a_][0] >= steps[b_][1] - steps[b_][0] else steps[b_][2]
        steps[a_] = [steps[a_][0], steps[b_][1], keep]
        del steps[b_]
    steps[0][0], steps[-1][1] = lo, hi            # ends at the measured extremes, not at bin edges
    return steps


# --------------------------------------------------------------------------- hypotheses
MIN_COVER = 200.0      # deg: a real hole/boss/revolve wraps most of the way round
BLEND_COVER = 120.0    # deg: a short arc of small radius is an edge blend (fillet), not a body


def hyp_blend(cyl, sign, noise, big) -> list[dict[str, Any]]:
    """Fillet-like region: recorded for the finishing stage, never built as a body."""
    if cyl is None or cyl["coverage"] > BLEND_COVER or cyl["r"] > min(3.0, 0.08 * big) or \
            cyl["rms"] > max(3 * noise, 0.06):
        return []
    return [{"kind": "blend", "variant": "concave" if cyl["concave"] else "convex", "geom_score": -10.0,
             "size": [cyl["r"]], "axis": cyl["a"].tolist(), "node": None, "params": {}, "explains": cyl["n"],
             "note": f"edge blend r~{cyl['r']:.3f} over {cyl['coverage']:.0f} deg: finishing-stage fillet"}]


def hyp_cylinder(cyl, Pc, sign, noise, tag, ev, big) -> list[dict[str, Any]]:
    if cyl is None or cyl["coverage"] < MIN_COVER or cyl["rms"] > max(4 * noise, 0.1) or cyl["r"] < 0.75:
        return []
    kind = "hole" if cyl["concave"] else "boss"
    if (kind == "hole") != (sign < 0):
        return []
    a, aname = snap_dir(cyl["a"])
    c = snap_axis_point(cyl["c"], a)
    t = (Pc[cyl["inliers"]] - c) @ a
    t0, t1 = float(t.min()), float(t.max())
    out = []
    exts = ["exact", "up", "down", "through"] if kind == "hole" else ["exact"]
    for e in exts:
        nm = Namer(tag)
        est = (f"classify.py RANSAC cylinder along {aname or np.round(a, 3).tolist()}: r {cyl['r']:.3f}, "
               f"rms {cyl['rms']:.3f}, {cyl['n']} inliers, coverage {cyl['coverage']:.0f} deg")
        lo = {"exact": t0, "up": t0, "down": t0 - big, "through": t0 - big}[e]
        hi = {"exact": t1, "up": t1 + big, "down": t1, "through": t1 + big}[e]
        node = {"op": "cylinder", "combine": "cut" if kind == "hole" else "add",
                "frame": frame_params(nm, c, a, est, ev),
                "r": nm.p("r", cyl["r"], "mm", est, ev), "h": nm.p("h", hi - lo, "mm", est, ev),
                "at": [0, 0, nm.p("t0", lo, "mm", est, ev)],
                "name": f"{kind} r={cyl['r']:.3f} along {aname or 'skew axis'} ({e})"}
        out.append({"kind": f"cyl-{kind}", "variant": e, "geom_score": cyl["rms"] / noise - cyl["n"] / len(Pc),
                    "size": [cyl["r"]], "axis": a.tolist(), "node": node, "params": nm.params,
                    "explains": cyl["n"], "members": cyl["inliers"]})
    return out


def hyp_revolve(cyl, Pc, Nc, sign, noise, spacing, tag, ev, cad_contains) -> list[dict[str, Any]]:
    if cyl is None or sign < 0 or cyl["concave"] or cyl["coverage"] < MIN_COVER or cyl["r"] < 0.75:
        return []
    a, aname = snap_dir(cyl["a"])
    c = snap_axis_point(cyl["c"], a)
    tol = max(5 * noise, 0.15)
    lat = np.abs(Nc @ a) < 0.95
    ll = line_line_dist(Pc, Nc, c, a)
    rel = (Pc - c) - np.outer((Pc - c) @ a, a)
    r = np.linalg.norm(rel, axis=1)
    t = (Pc - c) @ a
    # stay near the seed cylinder: radius and axial span limited around its inliers
    rc = cyl["r"]
    t_in = t[cyl["inliers"]]
    near = (r < 1.6 * rc + 1.0) & (t > t_in.min() - 2 * rc) & (t < t_in.max() + 2 * rc)
    side = (ll < tol) & lat & near
    if side.sum() < 100:
        return []
    rmax = np.percentile(r[side], 99) + tol
    tlo, thi = t[side].min() - 1.0, t[side].max() + 1.0
    ann = (~lat) & (r < rmax) & (t > tlo) & (t < thi) & near
    S = side | ann
    steps = meridian_steps(t[S], r[S], max(spacing, 0.1), max(3 * noise, 0.12), max(4 * spacing, 0.5))
    if not steps or len(steps) > 6:
        return []
    probe = np.array([c + (steps[0][0] - 0.6) * a, c + (steps[-1][1] + 0.6) * a])
    inside = cad_contains(probe)
    if inside[1] and not inside[0]:
        a = -a
        steps = [[-s[1], -s[0], s[2]] for s in reversed(steps)]
        inside = inside[::-1]
    ts = [s[0] for s in steps] + [steps[-1][1]]
    if inside[0]:
        ts[0] -= 0.5                                  # bury the root into the host body
    rs = [s[2] for s in steps]
    nm = Namer(tag)
    est = (f"classify.py revolve on RANSAC axis {aname or np.round(a, 3).tolist()}: {int(S.sum())} points, "
           f"{len(rs)} radius steps")
    fr = frame_params(nm, c, a, est, ev)
    tn, rn = nm.p("t", ts, "mm", est, ev), nm.p("r", rs, "mm", est, ev)
    pts = [[0, f"{tn}[0]"]]
    for k in range(len(rs)):
        pts += [[f"{rn}[{k}]", f"{tn}[{k}]"], [f"{rn}[{k}]", f"{tn}[{k + 1}]"]]
    pts.append([0, f"{tn}[{len(rs)}]"])
    node = {"op": "revolve", "combine": "add", "frame": fr, "profile": {"items": [{"type": "polygon", "pts": pts}]},
            "name": f"revolve boss ({len(rs)} steps) about {aname or 'skew axis'}"}
    return [{"kind": "revolve", "variant": f"{len(rs)}steps", "geom_score": -int(S.sum()) / len(Pc) + 0.05 * len(rs),
             "size": rs, "axis": a.tolist(), "node": node, "params": nm.params, "explains": int(S.sum()),
             "members": S}]


def outline_chain(fp, noise: float):
    """Shapely polygon -> (pts, arcs) line/arc chain via sketchfit.auto_topology, or None."""
    try:
        from sketchfit import auto_topology
    except Exception:
        return None
    ring = np.asarray(fp.exterior.coords)
    topo = auto_topology(ring, line_tol=max(3 * noise, 0.1), arc_tol=max(4 * noise, 0.15))
    if len(topo["verts"]) > MAX_SEG or len(topo["verts"]) < 3:
        return None
    arcs = {str(i): {"sagitta": None} for i, t in enumerate(topo["types"]) if t == "A"}
    return topo, arcs


def footprint(uv: np.ndarray, r: float, simp: float):
    from shapely.geometry import MultiPoint, Polygon
    from shapely.ops import unary_union
    if len(uv) > 5000:
        uv = uv[np.random.default_rng(0).choice(len(uv), 5000, replace=False)]
        r *= 1.4
    g = unary_union(MultiPoint(uv).buffer(r, quad_segs=2)).buffer(-0.8 * r)
    if g.is_empty:
        return None
    if g.geom_type == "MultiPolygon":
        g = max(g.geoms, key=lambda p: p.area)
    return Polygon(g.exterior).simplify(simp, preserve_topology=True)


def dominant_normals(N: np.ndarray, min_frac: float = 0.08, ang: float = 10.0) -> list[np.ndarray]:
    """Greedy clustering of normals on the sphere (a box gives its 6 face directions)."""
    rng = np.random.default_rng(0)
    rest = np.arange(len(N))
    out = []
    c = math.cos(math.radians(ang))
    for _ in range(8):
        if len(rest) < min_frac * len(N):
            break
        sub = rest[rng.choice(len(rest), min(400, len(rest)), replace=False)]
        counts = [(N[rest] @ N[i] > c).sum() for i in sub]
        i = sub[int(np.argmax(counts))]
        m = N[rest] @ N[i] > c
        if m.sum() < min_frac * len(N):
            break
        out.append(unit(N[rest][m].mean(0)))
        rest = rest[~m]
    return out


def candidate_dirs(N: np.ndarray) -> list[tuple[np.ndarray, str]]:
    w, V = np.linalg.eigh(N.T @ N / len(N))
    out = [(e, k) for k, e in AXES.items()]
    cands = [(V[:, i], f"eig{i}") for i in range(3)] + [(n, f"n{j}") for j, n in enumerate(dominant_normals(N))]
    for v_, nm_ in cands:
        d, name = snap_dir(v_)
        if name is None and all(abs(abs(d @ e) - 1) > math.sin(math.radians(3)) for e, _ in out):
            out.append((d, nm_))
    return out


def cad_silhouette(cad: Any, m: np.ndarray, d: np.ndarray, u: np.ndarray, v: np.ndarray, t0: float, t1: float):
    """Projection along d of the CAD triangles that reach into the slab t0..t1 (shapely)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    T = cad.triangles - m
    tt = T @ d
    keep = (tt.max(1) >= t0) & (tt.min(1) <= t1)
    polys = []
    for tri in T[keep]:
        q = np.c_[tri @ u, tri @ v]
        pg = Polygon(q)
        if pg.area > 1e-9:
            polys.append(pg)
    return unary_union(polys) if polys else None


def hyp_prism(Pc, Nc, sign, noise, spacing, tag, ev, big, cad=None) -> list[dict[str, Any]]:
    out = []
    cw, sw = math.cos(math.radians(WALL_DEG)), math.sin(math.radians(WALL_DEG))
    for d, dname in candidate_dirs(Nc):
        c = np.abs(Nc @ d)
        inl = (c < sw) | (c > cw)
        frac = float(inl.mean())
        if frac < 0.6 or inl.sum() < 60:
            continue
        P, N = Pc[inl], Nc[inl]
        u, v = basis(d)
        m = P.mean(0)
        uv = np.c_[(P - m) @ u, (P - m) @ v]
        fp = footprint(uv, max(2.5 * spacing, 0.15), max(noise, 0.03))
        if fp is None or fp.area < 1.0:
            continue
        t = (P - m) @ d
        t0, t1 = float(t.min()), float(t.max())
        caps_n = (Nc[inl] @ d)[c[inl] > cw]
        one_sided = float(abs(np.mean(np.sign(caps_n)))) if len(caps_n) > 20 else 0.0
        walls = c[inl] < sw
        draft = float(np.degrees(np.median(np.arcsin(np.clip(c[inl][walls], 0, 1))))) if walls.sum() > 30 else 0.0
        drafts = [0.0] + ([draft, -draft] if draft > 0.5 else [])
        shapes = []
        if sign > 0 and cad is not None:
            # bridge: grow the footprint by 0.5 mm only where it lies over the CAD silhouette, so the
            # add fuses with its host without adding visible material
            sil = cad_silhouette(cad, m, d, u, v, t0, t1)
            if sil is not None and not sil.is_empty:
                g = fp.union(fp.buffer(0.5).intersection(sil))
                if g.geom_type == "Polygon":
                    from shapely.geometry import Polygon as _Pg
                    fp = _Pg(g.exterior).simplify(max(noise, 0.03), preserve_topology=True)
        mrr = fp.minimum_rotated_rectangle
        if fp.area / max(mrr.area, 1e-9) > 0.92:
            shapes.append(("rect", mrr))
        else:
            # fragmented footprint (a body split by an earlier feature): its convex hull may be the rect
            from shapely.geometry import MultiPoint as _MP
            hull = _MP(uv).convex_hull
            hm = hull.minimum_rotated_rectangle
            if hull.area / max(hm.area, 1e-9) > 0.9 and hull.area > 1.5 * fp.area:
                shapes.append(("rect", hm))
        ch = outline_chain(fp, noise)
        if ch is not None:
            shapes.append(("chain", ch))
        if not shapes:
            continue
        exts = ["bury", "exact"] if sign > 0 else ["exact", "up", "down", "through"]
        for sname, geo in shapes:
            for e in exts:
                for dr in drafts:
                    nm = Namer(tag)
                    est = f"classify.py prism along {dname}: inlier frac {frac:.2f}, footprint {fp.area:.2f} mm2 ({sname})"
                    lo = {"exact": t0, "bury": t0 - 0.5, "up": t0, "down": t0 - big, "through": t0 - big}[e]
                    hi = {"exact": t1, "bury": t1 + 0.5, "up": t1 + big, "down": t1, "through": t1 + big}[e]
                    fr = {"origin": nm.p("c", m + lo * d, "mm", est, ev), "x_dir": nm.p("u", u, "-", est, ev),
                          "z_dir": nm.p("d", d, "-", est, ev)}
                    if sname == "rect":
                        rc = np.asarray(geo.exterior.coords)[:4]
                        e1, e2 = rc[1] - rc[0], rc[2] - rc[1]
                        item = {"type": "rect", "c": nm.p("rc", rc.mean(0), "mm", est, ev),
                                "w": nm.p("w", np.linalg.norm(e1), "mm", est, ev),
                                "h": nm.p("hh", np.linalg.norm(e2), "mm", est, ev),
                                "angle": nm.p("ang", math.degrees(math.atan2(e1[1], e1[0])), "deg", est, ev)}
                        nseg = 4
                    else:
                        topo, _ = geo
                        vn = nm.p("v", topo["verts"], "mm", est, ev)
                        arcs = {}
                        for i, (tp, b) in enumerate(zip(topo["types"], topo["bulges"])):
                            if tp == "A":
                                a_, b_ = np.asarray(topo["verts"][i]), np.asarray(topo["verts"][(i + 1) % len(topo["verts"])])
                                arcs[str(i)] = {"sagitta": nm.p(f"s{i}", b * np.linalg.norm(b_ - a_) / 2, "mm", est, ev)}
                        item = {"type": "chain", "pts": vn, "arcs": arcs}
                        nseg = len(topo["verts"])
                    node = {"op": "extrude", "combine": "add" if sign > 0 else "cut",
                            "sketch": {"plane": fr, "profile": {"items": [item]}},
                            "amount": nm.p("len", hi - lo, "mm", est, ev),
                            "name": f"prism {sname}({nseg}) along {dname} ({e}{', draft %.1f' % dr if dr else ''})"}
                    if dr:
                        node["draft_deg"] = nm.p("draft", dr, "deg", est, ev)
                    gs = -frac + 0.02 * nseg + (0.1 if dr else 0) + 0.1 * (1 - one_sided)
                    out.append({"kind": f"prism-{sname}", "variant": e + (f"/dr{dr:+.1f}" if dr else ""),
                                "geom_score": gs, "size": [float(fp.area)], "axis": d.tolist(), "node": node,
                                "params": nm.params, "explains": int(inl.sum()), "members": inl})
    return out


def hyp_offset_pocket(Pc, Nc, sign, noise, tag, ev, profiles2d) -> list[dict[str, Any]]:
    """profiles2d: [(ref, shapely polygon in XY, z_top_expr, parent node id)] for XY-plane extrude
    nodes. The pocket is inserted right after its parent node, so later bodies (a collar, a tube)
    refill it instead of being cut by it (v0 OD-H22 order: tray pocket before the core)."""
    if sign > 0 or not profiles2d:
        return []
    from shapely.geometry import Point
    out = []
    sw = math.sin(math.radians(WALL_DEG))
    walls = np.abs(Nc[:, 2]) < sw
    floor = Nc[:, 2] > math.cos(math.radians(WALL_DEG))
    if walls.sum() < 50 or floor.sum() < 50:
        return []
    for ref, poly, ztop, parent in profiles2d:
        bd = poly.exterior
        W = Pc[walls]
        sub = W[np.random.default_rng(0).choice(len(W), min(len(W), 3000), replace=False)]
        dist = np.array([bd.distance(Point(p[0], p[1])) for p in sub])
        inside = np.array([poly.contains(Point(p[0], p[1])) for p in sub])
        if inside.mean() < 0.9:
            continue
        # the wall thickness is the densest distance (other walls, e.g. a collar, are outliers)
        bw = max(2 * noise, 0.05)
        hist, edges = np.histogram(dist, bins=np.arange(0, dist.max() + bw, bw))
        k = int(hist.argmax())
        near_mode = np.abs(dist - (edges[k] + bw / 2)) < 3 * bw
        if near_mode.mean() < 0.3:
            continue
        tw = float(np.median(dist[near_mode]))
        spread = float(np.percentile(dist[near_mode], 90) - np.percentile(dist[near_mode], 10))
        if tw < 0.2:
            continue
        zf = float(np.median(Pc[floor][:, 2]))
        nm = Namer(tag)
        est = f"classify.py offset pocket of profile {ref}: wall {tw:.3f} (p10-p90 spread {spread:.3f}), floor z {zf:.3f}"
        node = {"op": "extrude", "combine": "cut", "name": f"pocket = {ref} offset -{tw:.3f}, floor z {zf:.3f}",
                "sketch": {"plane": "XY", "profile": {"ref": ref, "offset": "-" + nm.p("wall", tw, "mm", est, ev)}},
                "z0": nm.p("floor", zf, "mm", est, ev), "z1": ztop}
        out.append({"kind": "offset-pocket", "variant": ref, "geom_score": -2.0 + spread - near_mode.mean(), "size": [tw],
                    "axis": [0, 0, 1], "node": node, "params": nm.params, "explains": int(walls.sum() + floor.sum()),
                    "members": walls | floor,
                    "insert_after": parent})
    return out


def hyp_lathe_cut(Pc, Nc, sign, noise, spacing, tag, ev, axes, big) -> list[dict[str, Any]]:
    """Turned envelope cut about a known axis: remove the CAD material outside the scan's outer
    radius r_env(t). Covers shoulders, turned discs and cones on a prismatic stock."""
    if sign > 0:
        return []
    out = []
    for c, a, name in axes:
        ll = line_line_dist(Pc, Nc, c, a)
        par = np.abs(Nc @ a) > 0.95
        rev = (ll < max(5 * noise, 0.15)) | par
        if rev.mean() < 0.6:
            continue
        t = (Pc - c) @ a
        r = np.linalg.norm((Pc - c) - np.outer(t, a), axis=1)
        steps = meridian_steps(t[rev], r[rev], max(spacing, 0.1), max(3 * noise, 0.1), max(3 * spacing, 0.3))
        if not steps or len(steps) > 6:
            continue
        nm = Namer(tag)
        est = f"classify.py lathe cut about {name}: {int(rev.sum())} points, {len(steps)} radius steps"
        ts = [s_[0] for s_ in steps] + [steps[-1][1]]
        rs = [s_[2] for s_ in steps]
        tn, rn = nm.p("t", ts, "mm", est, ev), nm.p("r", rs, "mm", est, ev)
        Rb = nm.p("rout", big, "mm", est, ev)
        pts = []
        for k in range(len(rs)):
            pts += [[f"{rn}[{k}]", f"{tn}[{k}]"], [f"{rn}[{k}]", f"{tn}[{k + 1}]"]]
        pts += [[Rb, f"{tn}[{len(rs)}]"], [Rb, f"{tn}[0]"]]
        node = {"op": "revolve", "combine": "cut", "frame": frame_params(nm, c, a, est, ev),
                "profile": {"items": [{"type": "polygon", "pts": pts}]},
                "name": f"lathe cut about {name} ({len(rs)} steps)"}
        out.append({"kind": "lathe-cut", "variant": f"{len(rs)}steps", "geom_score": -rev.mean() + 0.05 * len(rs),
                    "size": rs, "axis": a.tolist(), "node": node, "params": nm.params,
                    "explains": int(rev.sum()), "members": rev})
    return out


def hyp_plane_cut(Pc, Nc, sign, noise, tag, ev) -> list[dict[str, Any]]:
    """Planar cut (chamfer, flat, facet): RANSAC plane on the cluster; the tool is a box on the
    outward side of the plane, bounded laterally by the plane inliers."""
    if sign > 0 or len(Pc) < 60:
        return []
    rng = np.random.default_rng(0)
    tol = max(3 * noise, 0.05)
    best = None
    for _ in range(300):
        i = rng.integers(len(Pc))
        n = Nc[i]
        inl = (np.abs((Pc - Pc[i]) @ n) < tol) & (Nc @ n > math.cos(math.radians(10)))
        if best is None or inl.sum() > best[1].sum():
            best = (i, inl)
    i, inl = best
    if inl.mean() < 0.5 or inl.sum() < 60:
        return []
    Q = Pc[inl]
    m = Q.mean(0)
    w, V = np.linalg.eigh(np.cov((Q - m).T))
    n = V[:, 0] * np.sign(V[:, 0] @ Nc[inl].mean(0))
    n, nname = snap_dir(n)
    u, v = basis(n)
    uq, vq = (Q - m) @ u, (Q - m) @ v
    margin = max(2 * noise, 0.05)
    depth = float(np.abs((Pc - m) @ n).max()) + 1.0
    nm = Namer(tag)
    est = f"classify.py RANSAC plane cut: {int(inl.sum())} inliers ({inl.mean():.2f}), normal {np.round(n, 3).tolist()}"
    cu, cv = (uq.max() + uq.min()) / 2, (vq.max() + vq.min()) / 2
    org = m + cu * u + cv * v
    node = {"op": "box", "combine": "cut", "frame": {"origin": nm.p("c", org, "mm", est, ev),
                                                     "z_dir": nm.p("d", n, "-", est, ev),
                                                     "x_dir": nm.p("u", u, "-", est, ev)},
            "size": [nm.p("w", uq.max() - uq.min() + 2 * margin, "mm", est, ev),
                     nm.p("hh", vq.max() - vq.min() + 2 * margin, "mm", est, ev), nm.p("dep", depth, "mm", est, ev)],
            "align": ["center", "center", "min"],
            "name": f"plane cut, normal {nname or np.round(n, 2).tolist()}"}
    return [{"kind": "plane-cut", "variant": "box", "geom_score": -inl.mean(), "size": [float(np.ptp(uq)), float(np.ptp(vq))],
             "axis": n.tolist(), "node": node, "params": nm.params, "explains": int(inl.sum()),
             "members": inl}]


def classify(Pc: np.ndarray, Nc: np.ndarray, sign: int, noise: float, spacing: float, tag: str,
             evidence: str, cad: Any, profiles2d: list | None = None,
             axes: list | None = None) -> list[dict[str, Any]]:
    """All hypotheses for one cluster, best geometric score first."""
    big = float(np.linalg.norm(cad.bounds[1] - cad.bounds[0]))
    tol = max(3 * noise, 0.08)
    cyl = ransac_cylinder(Pc, Nc, tol, r_max=0.5 * big)
    H = hyp_blend(cyl, sign, noise, big)
    if H and cyl["n"] > 0.5 * len(Pc):
        return H                      # the cluster is mostly a fillet: leave it to the finishing stage
    H += hyp_offset_pocket(Pc, Nc, sign, noise, tag, evidence, profiles2d or [])
    H += hyp_cylinder(cyl, Pc, sign, noise, tag, evidence, big)
    H += hyp_revolve(cyl, Pc, Nc, sign, noise, spacing, tag, evidence, cad.contains)
    H += hyp_prism(Pc, Nc, sign, noise, spacing, tag, evidence, big, cad)
    H += hyp_lathe_cut(Pc, Nc, sign, noise, spacing, tag, evidence,
                       axes or [(np.zeros(3), AXES["Z"], "Z")], big)
    H += hyp_plane_cut(Pc, Nc, sign, noise, tag, evidence)
    H.sort(key=lambda h: h["geom_score"])
    return H
