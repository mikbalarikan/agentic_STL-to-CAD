"""Design-intent sketch fitting (it2): a closed sketch of LINES and ARCS with a topology chosen by the
modeller, fitted by least squares to an AVERAGED section point cloud (de-warped scan points of a whole
constant x- or y-range projected onto the section plane).

Spec: {"verts": [[u,v],...], "types": ["L"|"A"|"Lh"...], "fixed": [idx,...]} (closed; segment i goes
verts[i] -> verts[i+1]; "Lh" = line hidden in the scan (not fitted, kept as given)).
Arcs are parametrised by a bulge b = sagitta / half-chord (b=0 -> straight). Only cloud points within
`band` mm of the initial sketch are used; vertices are softly regularised toward their initial position
so occluded corners stay where the modeller put them.
Output: fitted verts, bulges, and per-segment residual stats (rms / p95 / n)."""
from __future__ import annotations

import json
import sys

import numpy as np
from scipy.optimize import least_squares

P_ALL = None


def cloud(axis, lo, hi, box):
    global P_ALL
    if P_ALL is None:
        P_ALL = np.load("measure/figures/dewarped_pts.npy")
    ai = "xyz".index(axis)
    o = [i for i in range(3) if i != ai]
    s = (P_ALL[:, ai] > lo) & (P_ALL[:, ai] < hi)
    Q = P_ALL[s][:, o]
    k = (Q[:, 0] > box[0]) & (Q[:, 0] < box[1]) & (Q[:, 1] > box[2]) & (Q[:, 1] < box[3])
    return Q[k]


def arc_geom(a, b, bulge):
    """centre, radius, start angle, sweep for an arc from a to b with bulge (sagitta/half chord)."""
    ch = b - a
    L = np.linalg.norm(ch)
    h = L / 2
    s = bulge * h
    m = (a + b) / 2
    n = np.array([-ch[1], ch[0]]) / L          # left normal
    R = (h * h + s * s) / (2 * s)
    c = m + n * (s - R)
    a0 = np.arctan2(a[1] - c[1], a[0] - c[0])
    a1 = np.arctan2(b[1] - c[1], b[0] - c[0])
    mid = m + n * s
    am = np.arctan2(mid[1] - c[1], mid[0] - c[0])
    ccw = (a1 - a0) % (2 * np.pi)
    sweep = ccw if (am - a0) % (2 * np.pi) < ccw else -((a0 - a1) % (2 * np.pi))
    return c, abs(R), a0, sweep


def seg_dist(Q, a, b, typ, bulge):
    if typ.startswith("L") or abs(bulge) < 1e-6:
        ab = b - a
        t = np.clip(((Q - a) @ ab) / (ab @ ab), 0, 1)
        return np.linalg.norm(Q - (a + t[:, None] * ab), axis=1)
    c, R, a0, sw = arc_geom(a, b, bulge)
    ang = np.arctan2(Q[:, 1] - c[1], Q[:, 0] - c[0])
    rel = (ang - a0) % (2 * np.pi) if sw > 0 else (a0 - ang) % (2 * np.pi)
    inside = rel <= abs(sw)
    d_arc = np.abs(np.linalg.norm(Q - c, axis=1) - R)
    d_end = np.minimum(np.linalg.norm(Q - a, axis=1), np.linalg.norm(Q - b, axis=1))
    return np.where(inside, d_arc, d_end)


def dist_all(Q, V, types, bul):
    n = len(V)
    D = np.stack([seg_dist(Q, V[i], V[(i + 1) % n], types[i], bul[i]) for i in range(n)], axis=1)
    return D


def fit(spec, Q, band=0.6, reg=0.3):
    V0 = np.asarray(spec["verts"], float)
    types = spec["types"]
    n = len(V0)
    fixed = set(spec.get("fixed", []))
    B0 = np.zeros(n)
    # initial arc bulges from the data: points near each chord, signed offset at the chord middle
    for i, t in enumerate(types):
        if t != "A":
            continue
        a, b = V0[i], V0[(i + 1) % n]
        ab = b - a; L = np.linalg.norm(ab); u = ab / L; nrm = np.array([-u[1], u[0]])
        tt = (Q - a) @ u; off = (Q - a) @ nrm
        k = (tt > 0.35 * L) & (tt < 0.65 * L) & (np.abs(off) < max(0.35 * L, 1.0))
        if k.sum() > 5:
            # the offset cluster nearest the chord middle on either side
            o = off[k]
            s_ = float(np.median(o[np.abs(o) <= np.percentile(np.abs(o), 40)]))
            B0[i] = np.clip(s_ / (L / 2), -0.95, 0.95)
    D0 = dist_all(Q, V0, types, B0)
    own = D0.argmin(1)
    keep = D0.min(1) < band
    # points owned by hidden segments are not fitted
    for i, t in enumerate(types):
        if t == "Lh":
            keep &= own != i
    Qk, ownk = Q[keep], own[keep]
    if len(Qk) > 12000:  # seeded subsample: speed only, stats below use the same subset
        sel = np.random.default_rng(0).choice(len(Qk), 12000, replace=False)
        Qk, ownk = Qk[sel], ownk[sel]
    free_v = [i for i in range(n) if i not in fixed]
    arc_i = [i for i in range(n) if types[i] == "A"]

    def unpack(x):
        V = V0.copy()
        V[free_v] = x[:2 * len(free_v)].reshape(-1, 2)
        B = B0.copy()
        B[arc_i] = x[2 * len(free_v):]
        return V, B

    def res(x):
        V, B = unpack(x)
        r = [seg_dist(Qk[ownk == i], V[i], V[(i + 1) % n], types[i], B[i]) for i in range(n) if types[i] != "Lh"]
        r = np.concatenate(r) if r else np.zeros(0)
        return np.concatenate([r, reg * (V[free_v] - V0[free_v]).ravel()])

    x0 = np.concatenate([V0[free_v].ravel(), B0[arc_i]])
    from scipy.sparse import lil_matrix
    col_v = {v: 2 * j for j, v in enumerate(free_v)}
    col_b = {a: 2 * len(free_v) + j for j, a in enumerate(arc_i)}
    rows = []
    for i in range(n):
        if types[i] == "Lh":
            continue
        cols = []
        for v in (i, (i + 1) % n):
            if v in col_v:
                cols += [col_v[v], col_v[v] + 1]
        if i in col_b:
            cols.append(col_b[i])
        rows += [cols] * int((ownk == i).sum())
    rows += [[2 * j] for j in range(len(free_v))] + []
    J = lil_matrix((len(rows) + len(free_v), len(x0)), dtype=int)
    for r_, cols in enumerate(rows[:-len(free_v)] if free_v else rows):
        for c_ in cols:
            J[r_, c_] = 1
    base = len(rows) - len(free_v)
    for j in range(len(free_v)):
        J[base + 2 * j, 2 * j] = 1
        J[base + 2 * j + 1, 2 * j + 1] = 1
    J = J[:base + 2 * len(free_v)]
    sol = least_squares(res, x0, loss="soft_l1", f_scale=0.05, max_nfev=200, jac_sparsity=J)
    V, B = unpack(sol.x)
    stats = []
    for i in range(n):
        m = ownk == i
        if types[i] == "Lh" or m.sum() == 0:
            stats.append({"seg": i, "type": types[i], "n": int(m.sum())})
            continue
        d = seg_dist(Qk[m], V[i], V[(i + 1) % n], types[i], B[i])
        stats.append({"seg": i, "type": types[i], "n": int(m.sum()), "rms": round(float(np.sqrt(np.mean(d ** 2))), 3),
                      "p95": round(float(np.percentile(d, 95)), 3)})
    alld = np.concatenate([seg_dist(Qk[ownk == i], V[i], V[(i + 1) % n], types[i], B[i]) for i in range(n)
                           if types[i] != "Lh" and (ownk == i).sum()])
    return {"verts": V.round(3).tolist(), "types": types, "bulges": B.round(4).tolist(),
            "fit": {"n_points": int(len(Qk)), "rms": round(float(np.sqrt(np.mean(alld ** 2))), 3),
                    "p95": round(float(np.percentile(alld, 95)), 3)}, "segments": stats}


def polyline(sk):
    V = np.asarray(sk["verts"], float); n = len(V); segs = []
    for i in range(n):
        a, b = V[i], V[(i + 1) % n]; bu = sk["bulges"][i]
        if sk["types"][i] == "A" and abs(bu) > 1e-4:
            c, R, a0, sw = arc_geom(a, b, bu); t = a0 + np.linspace(0, sw, 40)
            segs.append(np.c_[c[0] + R * np.cos(t), c[1] + R * np.sin(t)])
        else:
            segs.append(np.array([a, b]))
    return segs


def crossings(sk):
    """Pairs of sketch segments that intersect other than at their shared vertex (face would be invalid)."""
    from shapely.geometry import LineString, Polygon
    segs = polyline(sk); n = len(segs); bad = []
    for i in range(n):
        for j in range(i + 1, n):
            inter = LineString(segs[i]).intersection(LineString(segs[j]))
            if inter.is_empty:
                continue
            adjacent = j == i + 1 or (i == 0 and j == n - 1)
            if adjacent and inter.geom_type == "Point":
                continue
            bad.append((i, j))
    ring = np.vstack([s[:-1] for s in segs])
    if not Polygon(ring).is_valid:
        bad.append("ring")
    return bad


def plot(spec_fit, Q, out, box):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    V = np.asarray(spec_fit["verts"]); n = len(V)
    w = box[1] - box[0]; h = box[3] - box[2]; sc = 14 / max(w, h)
    fig, a = plt.subplots(figsize=(w * sc + 1, h * sc + 1))
    a.plot(Q[:, 0], Q[:, 1], "k.", ms=0.4, alpha=0.3)
    for i in range(n):
        A, Bp = V[i], V[(i + 1) % n]
        t, b = spec_fit["types"][i], spec_fit["bulges"][i]
        if t.startswith("L") or abs(b) < 1e-6:
            a.plot([A[0], Bp[0]], [A[1], Bp[1]], "r-" if t == "L" else "b--", lw=1)
        else:
            c, R, a0, sw = arc_geom(A, Bp, b)
            tt = a0 + np.linspace(0, sw, 60)
            a.plot(c[0] + R * np.cos(tt), c[1] + R * np.sin(tt), "r-", lw=1)
        a.text(A[0], A[1], str(i), fontsize=7, color="b")
    a.set_xlim(box[0], box[1]); a.set_ylim(box[2], box[3]); a.set_aspect("equal"); a.grid(True, lw=0.3); a.minorticks_on()
    a.set_title(f"fit rms {spec_fit['fit']['rms']} p95 {spec_fit['fit']['p95']}")
    plt.tight_layout(); plt.savefig(out, dpi=70)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    Q = cloud(spec["axis"], spec["range"][0], spec["range"][1], spec["box"])
    r = fit(spec, Q, band=spec.get("band", 0.6), reg=spec.get("reg", 0.3))
    bad = crossings(r)
    r["valid_sketch"] = not bad
    if bad:
        print("SELF-INTERSECTING segments:", bad)
    r.update({k: spec[k] for k in ("axis", "range", "box", "name")})
    json.dump(r, open(sys.argv[1].replace(".spec.json", ".fit.json"), "w"), indent=1)
    plot(r, Q, sys.argv[1].replace(".spec.json", ".fit.png"), spec["box"])
    print(json.dumps(r["fit"]), [s for s in r["segments"] if s.get("p95", 0) > 0.1])


def auto_topology(ring, corner_deg=28.0, line_tol=0.06, arc_tol=0.08, min_seg=0.25):
    """Closed loop points -> design sketch topology: corners where the tangent turns > corner_deg,
    each corner-to-corner chain = line (if within line_tol of its chord), else one arc (if within arc_tol),
    else split recursively at the worst point. Returns verts, types, bulges."""
    from shapely.geometry import LineString, Polygon
    q = np.asarray(ring, float)
    if np.linalg.norm(q[0] - q[-1]) < 1e-9:
        q = q[:-1]
    # resample uniformly
    ls = LineString(np.vstack([q, q[:1]]))
    n = max(200, int(ls.length / 0.1))
    q = np.array([ls.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, n, endpoint=False)])
    if Polygon(q).area < 0:
        q = q[::-1]
    k = 4
    tang = np.roll(q, -k, 0) - np.roll(q, k, 0)
    ang = np.unwrap(np.arctan2(tang[:, 1], tang[:, 0]))
    turn = np.degrees(np.abs(np.roll(ang, -k) - np.roll(ang, k)))
    turn = np.minimum(turn, 360 - turn)
    cand = np.where(turn > corner_deg)[0]
    corners = []
    for c in cand:  # local maxima of turn
        w = turn[max(0, c - k):c + k + 1]
        if turn[c] >= w.max() - 1e-9 and (not corners or c - corners[-1] > k):
            corners.append(c)
    if len(corners) < 3:
        corners = list(np.linspace(0, n, 4, endpoint=False).astype(int))
    verts, types, bulges = [], [], []

    def chord_fit(pts):
        a, b = pts[0], pts[-1]
        ab = b - a
        L = np.linalg.norm(ab)
        if L < 1e-9:
            return "L", 0.0, 0.0
        nrm = np.array([-ab[1], ab[0]]) / L
        dev = (pts - a) @ nrm
        if np.abs(dev).max() <= line_tol:
            return "L", 0.0, float(np.abs(dev).max())
        # three-point arc through a, mid, b
        m = pts[len(pts) // 2]
        s = float((m - a) @ nrm)
        # sagitta at chord midpoint from the circle through a,m,b
        A = np.array([[2 * (m[0] - a[0]), 2 * (m[1] - a[1])], [2 * (b[0] - a[0]), 2 * (b[1] - a[1])]])
        rhs = np.array([m @ m - a @ a, b @ b - a @ a])
        try:
            c = np.linalg.solve(A, rhs)
        except np.linalg.LinAlgError:
            return "L", 0.0, float(np.abs(dev).max())
        R = np.linalg.norm(a - c)
        h = L / 2
        sag = R - np.sqrt(max(R * R - h * h, 0))
        side = np.sign((( (a + b) / 2 - c) @ nrm)) * -1
        mid_c = (a + b) / 2 - c
        # sagitta sign: arc bulges toward the side where m is
        bul = np.sign(s) * sag / h if np.dot(m - (a + b) / 2, nrm) * np.dot(-mid_c, nrm) >= 0 else np.sign(s) * (2 * R - sag) / h
        err = np.abs(np.linalg.norm(pts - c, axis=1) - R).max()
        return "A", float(bul), float(err)

    def emit(i0, i1):
        idx = np.arange(i0, i1 + 1) % n if i1 >= i0 else np.r_[np.arange(i0, n), np.arange(0, i1 + 1)]
        pts = q[idx]
        if len(pts) < 3 or np.linalg.norm(pts[-1] - pts[0]) < min_seg:
            verts.append(pts[0]); types.append("L"); bulges.append(0.0); return
        t, b, err = chord_fit(pts)
        if (t == "A" and err > arc_tol) or abs(b) > 0.9:
            j = (len(idx)) // 2
            emit(idx[0], idx[j]); emit(idx[j], idx[-1]); return
        verts.append(pts[0]); types.append(t); bulges.append(b)

    for i in range(len(corners)):
        emit(corners[i], corners[(i + 1) % len(corners)])
    return {"verts": np.round(verts, 3).tolist(), "types": types, "bulges": np.round(bulges, 4).tolist()}
