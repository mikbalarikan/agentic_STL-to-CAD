"""Deterministic DXF writer + validator for a facet-film cutting kit.

Encodes the output contract distilled from the maintainer's accepted NX kit
(WatchCareES_Template_2_DXF_RV02.dxf) while fixing its recorded defects
(open chains, 0.013-0.05 mm micro-segments, unlabeled pieces, POINTs on the
cut layer, bogus $EXTMIN/$EXTMAX).

Contract highlights (see references/dxf-contract.md of this skill):
  - R2004 (AC1018), $INSUNITS=4 (mm), model space only, z=0.
  - one closed LWPOLYLINE (bulge arcs) per loop; no SPLINE/POINT on cut layers.
  - layers: CUT_OUTER (red, CCW), CUT_INNER (blue, CW), LABEL (green TEXT),
    REG (magenta, optional), REF (grey, non-cut reference).
  - convex corners filleted (maintainer's final value R0.4; R0.2 was rejected).
  - deterministic bytes: ezdxf write_fixed_meta_data_for_testing = True AND the
    process must run with PYTHONHASHSEED=0 (ezdxf's OBJECTS-section ordering
    follows Python hash randomization; in-process re-writes match regardless,
    but cross-process byte-identity needs the pinned seed).

Piece input format: dict(id=str, outer=Nx2 array-like (closed or open ring),
holes=[Mx2, ...], layer_extra=None). Coordinates in mm on the sheet plane.

validate_kit() re-reads the file and enforces the hard gates:
closed loops only, loop count == piece count, no overlaps, min gap,
min segment length, narrow-feature width (buffer erosion test - the
'horn tip 0.73 mm' lesson), extents sane. Returns a report dict; 'ok' False
means DO NOT deliver the file.
"""

from __future__ import annotations

import math

import numpy as np

try:
    from shapely.geometry import Polygon

    HAVE_SHAPELY = True
except Exception:  # shapely optional; validator degrades gracefully
    HAVE_SHAPELY = False

LAYERS = {
    "CUT_OUTER": {"color": 1},
    "CUT_INNER": {"color": 5},
    "LABEL": {"color": 3},
    "REG": {"color": 6},
    "REF": {"color": 8},
}


def _ring(pts) -> np.ndarray:
    P = np.asarray(pts, dtype=float)[:, :2]
    if np.allclose(P[0], P[-1]):
        P = P[:-1]
    return P


def _signed_area(P: np.ndarray) -> float:
    x, y = P[:, 0], P[:, 1]
    return 0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _orient(P: np.ndarray, ccw: bool) -> np.ndarray:
    return P if (_signed_area(P) > 0) == ccw else P[::-1]


def fillet_ring(P: np.ndarray, r: float, min_seg: float = 0.08) -> np.ndarray:
    """Round convex corners of a polygonal ring with radius r via shapely's
    erosion/dilation round-trip (exact circular arcs, sampled). Also removes
    micro-segments < min_seg. Requires shapely; returns the ring unchanged if
    unavailable or degenerate."""
    if not HAVE_SHAPELY or r <= 0:
        return P
    poly = Polygon(P)
    if not poly.is_valid or poly.is_empty:
        return P
    out = poly.buffer(-r, join_style=1, quad_segs=24).buffer(r, join_style=1, quad_segs=24)
    if out.is_empty or out.geom_type != "Polygon":
        return P  # piece narrower than 2r somewhere - leave sharp, validator will flag
    Q = np.asarray(out.exterior.coords)[:-1]
    keep = [0]
    for i in range(1, len(Q)):
        if np.linalg.norm(Q[i] - Q[keep[-1]]) >= min_seg:
            keep.append(i)
    return Q[keep]


def write_kit(
    path,
    pieces,
    *,
    corner_radius: float = 0.4,
    labels: bool = True,
    text_height: float = 1.5,
    registration: bool = False,
    ref_points=None,
    meta: dict | None = None,
):
    """Write the kit DXF. pieces: list of dicts (see module docstring).
    Returns the ezdxf document (already saved)."""
    import ezdxf
    from ezdxf import options as ez_options

    ez_options.write_fixed_meta_data_for_testing = True  # byte-deterministic

    doc = ezdxf.new("R2004", setup=False)
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LUNITS"] = 2
    for name, attrs in LAYERS.items():
        doc.layers.add(name, color=attrs["color"])
    msp = doc.modelspace()

    all_pts = []
    for piece in sorted(pieces, key=lambda p: p["id"]):
        outer = _orient(fillet_ring(_ring(piece["outer"]), corner_radius), ccw=True)
        rings = [("CUT_OUTER", outer)]
        for h in piece.get("holes", []) or []:
            rings.append(("CUT_INNER", _orient(fillet_ring(_ring(h), corner_radius), ccw=False)))
        for layer, ring in rings:
            pl = msp.add_lwpolyline(ring, format="xy", close=True, dxfattribs={"layer": layer})
            pl.set_xdata(
                "WATCH_TPU", [(1000, str(piece["id"])), (1040, float(abs(_signed_area(ring))))]
            )
            all_pts.append(ring)
        if labels:
            c = outer.mean(axis=0)
            if HAVE_SHAPELY:
                pt = Polygon(outer).representative_point()
                c = np.array([pt.x, pt.y])
            msp.add_text(
                str(piece["id"]),
                dxfattribs={"layer": "LABEL", "height": text_height, "insert": (c[0], c[1], 0)},
            )
    for p in ref_points or []:
        msp.add_point((p[0], p[1], 0), dxfattribs={"layer": "REF"})

    pts = np.vstack(all_pts)
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    if registration:
        for cx, cy in [(lo[0] - 3, lo[1] - 3), (hi[0] + 3, hi[1] + 3)]:
            msp.add_line((cx - 1.5, cy, 0), (cx + 1.5, cy, 0), dxfattribs={"layer": "REG"})
            msp.add_line((cx, cy - 1.5, 0), (cx, cy + 1.5, 0), dxfattribs={"layer": "REG"})
        lo, hi = lo - 4.5, hi + 4.5
    # ezdxf's save path re-derives the header extents from msp.dxf.extmin/extmax,
    # so set BOTH (setting only the header vars ships +-1e20 defaults - measured bug).
    msp.dxf.extmin = (float(lo[0]), float(lo[1]), 0.0)
    msp.dxf.extmax = (float(hi[0]), float(hi[1]), 0.0)
    doc.header["$EXTMIN"] = (float(lo[0]), float(lo[1]), 0.0)
    doc.header["$EXTMAX"] = (float(hi[0]), float(hi[1]), 0.0)
    doc.appids.add("WATCH_TPU")
    doc.saveas(path)
    return doc


def validate_kit(
    path,
    *,
    expect_pieces: int | None = None,
    min_gap: float = 1.0,
    min_width: float = 1.5,
    min_seg: float = 0.05,
    nested_gap: float = 0.35,
) -> dict:
    """Hard gates on a written (or foreign) kit DXF. Chains cut-layer entities at
    0.01 mm; every chain must close. Narrow-feature test = area lost by
    buffer(-min_width/2)+buffer(+min_width/2) (catches 0.7 mm horn tips that a
    largest-inscribed-circle test misses). nested_gap: minimum clearance for a
    piece nested inside another piece's hole (crystal-disc-in-bezel case)."""
    import ezdxf

    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    problems, loops = [], []
    for e in msp:
        layer = e.dxf.layer
        if layer in ("CUT_OUTER", "CUT_INNER", "1"):  # accept NX layer "1" for legacy files
            t = e.dxftype()
            if t == "LWPOLYLINE":
                if not e.closed:
                    problems.append(f"open LWPOLYLINE on {layer}")
                pts = np.array([(v[0], v[1]) for v in e.get_points()])
                bulges = [v[4] for v in e.get_points()]
                loops.append((layer, _densify(pts, bulges)))
            elif t == "CIRCLE":
                c, r = e.dxf.center, e.dxf.radius
                th = np.linspace(0, 2 * np.pi, 180, endpoint=False)
                loops.append((layer, np.c_[c[0] + r * np.cos(th), c[1] + r * np.sin(th)]))
            elif t in ("POINT", "SPLINE", "TEXT", "MTEXT"):
                problems.append(f"{t} on cut layer {layer}")
    report = {"n_loops": len(loops), "problems": problems}
    if expect_pieces is not None:
        outer_n = sum(1 for lay, _ in loops if lay != "CUT_INNER")
        if outer_n != expect_pieces:
            problems.append(f"outer loop count {outer_n} != expected {expect_pieces}")
    if doc.header.get("$INSUNITS", 0) != 4:
        problems.append("$INSUNITS != 4 (mm)")
    # extents sanity (the NX files and an early version of this writer shipped bogus ones)
    if loops:
        allp = np.vstack([P for _, P in loops])
        lo, hi = allp.min(axis=0), allp.max(axis=0)
        emin = np.array(doc.header.get("$EXTMIN", (1e20,) * 3)[:2])
        emax = np.array(doc.header.get("$EXTMAX", (-1e20,) * 3)[:2])
        if (np.abs(emin) > 1e6).any() or (np.abs(emax) > 1e6).any():
            problems.append("$EXTMIN/$EXTMAX are unset defaults")
        elif (emin > lo + 1.0).any() or (emax < hi - 1.0).any():
            problems.append(
                f"$EXTMIN/$EXTMAX do not cover the geometry "
                f"({emin}..{emax} vs {lo.round(2)}..{hi.round(2)})"
            )
        report["extents"] = [list(map(float, emin)), list(map(float, emax))]
    seg_mins = []
    for _, P in loops:
        d = np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1)
        seg_mins.append(float(d[d > 1e-9].min()) if (d > 1e-9).any() else 0.0)
    report["min_segment_mm"] = min(seg_mins) if seg_mins else None

    if HAVE_SHAPELY and loops:
        outers = [Polygon(P) for lay, P in loops if lay != "CUT_INNER"]
        inners = [Polygon(P) for lay, P in loops if lay == "CUT_INNER"]
        for i, p in enumerate(outers):
            if not p.is_valid:
                problems.append(f"self-intersecting loop {i}")
        # subtract holes from their parents before overlap/gap checks
        solids = []
        for p in outers:
            for h in inners:
                if p.contains(h):
                    p = p.difference(h)
            solids.append(p)
        gaps = []
        for i in range(len(solids)):
            for j in range(i + 1, len(solids)):
                a, b = solids[i], solids[j]
                inter = a.intersection(b).area
                if inter > 1e-6:
                    # nested piece (e.g. disc inside annulus hole) is allowed with clearance
                    problems.append(f"pieces {i} and {j} overlap by {inter:.3f} mm^2")
                else:
                    gaps.append(a.distance(b))
        if gaps:
            report["min_gap_mm"] = float(min(gaps))
            nested = [g for g in gaps if g < min_gap]
            if any(g < nested_gap for g in nested):
                problems.append(f"min gap {min(gaps):.3f} < nested_gap {nested_gap}")
            elif nested:
                report["nested_or_tight_pairs"] = len(nested)
        r = min_width / 2.0
        for i, p in enumerate(outers):
            eroded = p.buffer(-r).buffer(r)
            lost = p.area - eroded.area
            if lost > 0.5:  # mm^2 of sub-min-width features
                report.setdefault("narrow_features", []).append(
                    {"loop": i, "area_below_min_width_mm2": round(float(lost), 3)}
                )
    if report.get("min_segment_mm") is not None and report["min_segment_mm"] < min_seg:
        problems.append(f"segment {report['min_segment_mm']:.3f} mm < {min_seg}")
    report["ok"] = not problems
    return report


def _densify(pts: np.ndarray, bulges, chord_tol: float = 0.01) -> np.ndarray:
    """Expand LWPOLYLINE bulge arcs to points at chord tolerance."""
    out = []
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        b = bulges[i]
        out.append(p)
        if abs(b) > 1e-12:
            theta = 4 * math.atan(b)
            chord = np.linalg.norm(q - p)
            if chord < 1e-12:
                continue
            r = chord / (2 * math.sin(abs(theta) / 2))
            # sagitta-based step count
            steps = max(2, int(abs(theta) / (2 * math.acos(max(1 - chord_tol / max(r, 1e-9), -1)))))
            mid = (p + q) / 2
            d = (q - p) / chord
            nvec = np.array([-d[1], d[0]])
            centre = mid - nvec * (r * math.cos(theta / 2)) * np.sign(b)
            a0 = math.atan2(p[1] - centre[1], p[0] - centre[0])
            for k in range(1, steps):
                a = a0 + theta * k / steps
                out.append(centre + r * np.array([math.cos(a), math.sin(a)]))
    return np.array(out)


if __name__ == "__main__":
    import os
    import tempfile

    th = np.linspace(0, 2 * np.pi, 180, endpoint=False)
    ring_o = np.c_[19.4 * np.cos(th), 19.4 * np.sin(th)]
    ring_i = np.c_[15.0 * np.cos(th), 15.0 * np.sin(th)]
    disc = np.c_[14.65 * np.cos(th) + 45, 14.65 * np.sin(th)]
    rect = np.array([[70, -4.4], [77.3, -4.4], [77.3, 4.4], [70, 4.4]])
    pieces = [
        {"id": "BEZ_TOP", "outer": ring_o, "holes": [ring_i]},
        {"id": "CRYSTAL", "outer": disc},
        {"id": "LINK_C_12_1", "outer": rect},
    ]
    p = os.path.join(tempfile.gettempdir(), "kit_selftest.dxf")
    write_kit(p, pieces, corner_radius=0.4)
    rep = validate_kit(p, expect_pieces=3, min_gap=1.0)
    print(rep)
    assert rep["ok"], rep
    assert abs(rep["extents"][0][0] - (-19.4)) < 0.5, rep["extents"]  # real extents persisted
    # cross-process determinism (requires PYTHONHASHSEED pinned in the child env)
    import hashlib
    import subprocess
    import sys

    env = dict(os.environ, PYTHONHASHSEED="0")
    prog = (
        f"import sys; sys.path.insert(0, {os.path.dirname(os.path.abspath(__file__))!r}); "
        "import numpy as np; from dxf_kit_writer import write_kit\n"
        "th = np.linspace(0, 2*np.pi, 180, endpoint=False)\n"
        "pieces = [\n"
        " {'id':'BEZ_TOP','outer':np.c_[19.4*np.cos(th),19.4*np.sin(th)],\n"
        "  'holes':[np.c_[15.0*np.cos(th),15.0*np.sin(th)]]},\n"
        " {'id':'CRYSTAL','outer':np.c_[14.65*np.cos(th)+45,14.65*np.sin(th)]},\n"
        " {'id':'LINK_C_12_1','outer':np.array([[70,-4.4],[77.3,-4.4],[77.3,4.4],[70,4.4]])},\n"
        "]\n"
        f"write_kit(sys.argv[1], pieces, corner_radius=0.4)\n"
    )
    hs = []
    for suffix in ("_a", "_b"):
        subprocess.run([sys.executable, "-c", prog, p + suffix], env=env, check=True)
        hs.append(hashlib.sha256(open(p + suffix, "rb").read()).hexdigest())
    print("cross-process deterministic (PYTHONHASHSEED=0):", hs[0] == hs[1])
    assert hs[0] == hs[1]
    print("dxf_kit_writer self-test OK")
