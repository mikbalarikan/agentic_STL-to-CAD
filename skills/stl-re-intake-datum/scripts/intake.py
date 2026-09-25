#!/usr/bin/env python3
"""intake.py - scan intake: stats + sha256, working copy, coverage map, CHK-SCALE evidence.

PROVENANCE
  * `stats` is lifted from golden-examples/dreame_brush-caps/report/source/intake.py
    (load, faces/verts/bounds/extents/watertight/euler, body split with top-5 face
    counts, quadric decimation to a working copy). Changed: no hard-coded paths or part
    names; sha256 of the input (SYNTHESIS A1); largest-body keep with REPORTED fractions
    and an optional scanner-table removal by direction + offset + up-normal (rule from
    dreame fastgate.py:36-38 and align.py:45-46; SYNTHESIS A4); weld + volume-sign
    normal flip on the WORKING COPY only (B02 INTAKE_CARD.md:36, q20_tier2.py:27;
    SYNTHESIS A5; never modify the input, facet-film T4); decimation provenance with a
    seeded work-vs-original deviation sample (SYNTHESIS A2); open-boundary loop count;
    "top facets by area" dropped (largest-facet datum rule is DROPPED, SYNTHESIS section 3).
  * `coverage` is new (no golden script exists): it computes, in the DATUM frame, the
    open-boundary loop list with r/z/theta ranges (the B02 occlusion-map columns,
    INTAKE_CARD.md:40-50), angular coverage per radial band (P03 partial ~270 deg,
    analysis/golden/OOM-P03.md section 3) and per-radius-band z extents (the P03 stem
    lesson: on-axis material above the expected top, OOM-P03.md section 8).
  * `scale` is new: tabulates caliper/scan ratios for CHK-SCALE (RE_SPEC.md:98-101;
    B02 alignment.json#scale_correction_note).

Determinism: sampling uses a fixed seed (default 0); quadric decimation is deterministic
for a given input and library version (library versions are recorded). Only the
`created` header field reads the clock.

Blind spots: this does not judge whether a component is scanner furniture or a real
separate part (you decide from photos), does not detect scanner dilation (an offset,
not a scale - B02 INTAKE_CARD.md R6), and the coverage map sees only open boundaries,
not scanner-bridged cavities (DRM hook underside, P03 socket).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datum_fit import json_header, sha256_file, unit  # noqa: E402


def _dump(obj: Any) -> str:
    return json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def boundary_loops(m: trimesh.Trimesh) -> list[np.ndarray]:
    """Vertex-index arrays of open-boundary loops (edges used by exactly one face)."""
    e = m.edges_sorted
    g = trimesh.grouping.group_rows(e, require_count=1)
    if len(g) == 0:
        return []
    be = e[g]
    graph: dict[int, list[int]] = {}
    for a, b in be:
        graph.setdefault(int(a), []).append(int(b))
        graph.setdefault(int(b), []).append(int(a))
    seen: set[int] = set()
    loops = []
    for start in sorted(graph):
        if start in seen:
            continue
        comp, stack = [], [start]
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            comp.append(v)
            stack.extend(graph[v])
        loops.append(np.asarray(comp))
    return loops


def components(m: trimesh.Trimesh) -> list[np.ndarray]:
    """Face-index arrays of connected bodies, largest first (scipy engine; no networkx)."""
    comps = trimesh.graph.connected_components(m.face_adjacency, nodes=np.arange(len(m.faces)),
                                               min_len=1, engine="scipy")
    return sorted((np.asarray(c) for c in comps), key=lambda c: (-len(c), int(c.min())))


def mesh_stats(m: trimesh.Trimesh) -> dict[str, Any]:
    info: dict[str, Any] = {
        "faces": int(len(m.faces)), "verts": int(len(m.vertices)),
        "bounds": m.bounds.tolist(), "extents": m.extents.tolist(),
        "watertight": bool(m.is_watertight), "winding_consistent": bool(m.is_winding_consistent),
        "euler": int(m.euler_number), "area_mm2": float(m.area),
        "signed_volume_mm3": float(m.volume),
    }
    loops = boundary_loops(m)
    info["open_boundary_edges"] = int(len(trimesh.grouping.group_rows(m.edges_sorted, require_count=1)))
    info["open_boundary_loops"] = int(len(loops))
    info["open_boundary_loops_note"] = "vertex-connected boundary components (touching loops merge)"
    return info


def orientation_vote(m: trimesh.Trimesh, n: int = 500, seed: int = 0) -> dict[str, Any]:
    """Local normal-orientation test for OPEN meshes. On a non-watertight scan the signed
    volume depends on the coordinate origin and can be negative with outward normals
    (measured on B02: raw normals outward - dome top n_z +0.93, rim n_z -0.99 in the
    datum frame - while volume is -2434 mm^3). Cast a ray from just off each sampled
    face centre along +n and along -n; outward normals hit the part less often along +n."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(m.faces), min(n, len(m.faces)), replace=False)
    c, nr = m.triangles_center[idx], m.face_normals[idx]
    eps = 1e-3 * float(np.linalg.norm(m.extents))
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(m)
    fwd = ray.intersects_any(c + eps * nr, nr)
    bwd = ray.intersects_any(c - eps * nr, -nr)
    f, b = float(fwd.mean()), float(bwd.mean())
    return {"samples": int(len(idx)), "seed": seed, "hit_along_normal": f, "hit_against_normal": b,
            "verdict": "outward" if f < b else ("inward" if f > b else "undecided")}


# ----------------------------------------------------------------------------- stats
def cmd_stats(a: argparse.Namespace) -> int:
    scan = a.scan.resolve()
    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    rep: dict[str, Any] = json_header("intake", "intake.py", {str(scan): sha256_file(scan)}, a.seed)
    rep["libs"] = {"trimesh": trimesh.__version__, "numpy": np.__version__}
    raw = trimesh.load_mesh(scan, process=False)
    if not isinstance(raw, trimesh.Trimesh):
        raise SystemExit(f"{scan}: not a single triangle mesh")
    rep["input_bytes"] = scan.stat().st_size
    rep["raw_unwelded"] = {"faces": int(len(raw.faces)), "verts": int(len(raw.vertices))}
    # weld on a copy (process=True merges duplicate vertices); input file is never written
    m = trimesh.Trimesh(vertices=raw.vertices.copy(), faces=raw.faces.copy(), process=True)
    rep["raw_welded"] = mesh_stats(m)
    rep["welded_vertex_reduction"] = int(len(raw.vertices) - len(m.vertices))

    # components
    parts = components(m)
    rep["bodies"] = int(len(parts))
    tot_f = float(len(m.faces))
    rep["body_faces_top5"] = [int(len(p)) for p in parts[:5]]
    removed: dict[str, Any] = {"fragments_pct": 0.0, "table_pct": 0.0, "method": []}
    if a.keep == "largest" and len(parts) > 1:
        m = m.submesh([parts[0]], append=True)
        removed["fragments_pct"] = round(100.0 * (1 - len(m.faces) / tot_f), 4)
        removed["method"].append(f"kept largest of {len(parts)} bodies ({len(m.faces)} faces)")
    elif len(parts) > 1:
        removed["method"].append(f"kept all {len(parts)} bodies (operator choice)")

    # optional scanner-table removal (golden rule: offset threshold + up-normal, dreame fastgate.py:36-38)
    if a.table_dir is not None:
        t = unit(a.table_dir)
        c = m.triangles_center @ t
        up = m.face_normals @ t > a.table_normal_min
        drop = up & (c < a.table_below)
        removed["table_pct"] = round(100.0 * drop.sum() / len(m.faces), 4)
        removed["method"].append(
            f"table: faces with n.{t.round(4).tolist()} > {a.table_normal_min} and offset < {a.table_below}")
        m = m.submesh([np.where(~drop)[0]], append=True)
    rep["removed"] = removed

    # decimated working copy (orientation-independent, so it runs first)
    work = m
    prov: dict[str, Any] = {"applied": False}
    if a.work_faces and len(m.faces) > a.work_faces:
        work = m.simplify_quadric_decimation(face_count=a.work_faces)
        prov = {"applied": True, "method": "trimesh.simplify_quadric_decimation (fast_simplification)",
                "from_faces": int(len(m.faces)), "to_faces": int(len(work.faces))}
        pts, _ = trimesh.sample.sample_surface(m, a.dev_samples, seed=a.seed)
        _, dist, _ = trimesh.proximity.closest_point(work, pts)
        prov["work_vs_full_dev_mm"] = {"n": int(len(dist)), "p95": float(np.percentile(dist, 95)),
                                       "max": float(dist.max()), "seed": a.seed,
                                       "direction": "full-surface samples -> work mesh"}

    # normals: volume sign only if watertight; otherwise a local ray vote on the (smaller)
    # working copy (see orientation_vote). The same flip is applied to the full clean copy.
    vol = float(m.volume)
    rep["normals_flipped"] = False
    if m.is_watertight:
        rep["orientation"] = {"method": "signed volume (watertight)", "signed_volume_mm3": vol,
                              "verdict": "outward" if vol > 0 else "inward"}
    else:
        rep["orientation"] = {"method": "ray vote on the working copy (open mesh: volume sign "
                                        "is origin-dependent)",
                              "signed_volume_mm3_unreliable": vol,
                              **orientation_vote(work, a.orient_samples, a.seed)}
    if rep["orientation"]["verdict"] == "inward":
        m.invert()
        if work is not m:
            work.invert()
        rep["normals_flipped"] = True
    rep["working_full"] = mesh_stats(m)
    rep["decimation"] = prov
    wpath = out / "work.stl"
    work.export(wpath)
    rep["work_mesh"] = {"path": str(wpath), "sha256": sha256_file(wpath), "faces": int(len(work.faces))}
    if a.save_full_clean:
        fpath = out / "work_full.stl"
        m.export(fpath)
        rep["work_full_mesh"] = {"path": str(fpath), "sha256": sha256_file(fpath)}
    rep["note"] = ("input file untouched; weld, fragment/table removal and normal flip applied to "
                   "the working copy only. Official gates run on the full-resolution original.")
    (out / "intake.json").write_text(_dump(rep))
    print(_dump({k: rep[k] for k in ("raw_welded", "bodies", "body_faces_top5", "removed",
                                     "orientation", "normals_flipped", "decimation", "work_mesh")}))
    return 0


# ----------------------------------------------------------------------------- coverage
def cmd_coverage(a: argparse.Namespace) -> int:
    m = trimesh.load_mesh(a.aligned, process=True)
    v = m.vertices
    r = np.hypot(v[:, 0], v[:, 1])
    th = np.degrees(np.arctan2(v[:, 1], v[:, 0]))
    res: dict[str, Any] = json_header("coverage", "intake.py", {str(a.aligned): sha256_file(a.aligned)}, a.seed)
    loops = boundary_loops(m)
    L = []
    for lp in sorted(loops, key=len, reverse=True)[: a.max_loops]:
        p = v[lp]
        rr, tt = np.hypot(p[:, 0], p[:, 1]), np.degrees(np.arctan2(p[:, 1], p[:, 0]))
        # circular theta range: largest empty gap complement
        ts = np.sort(tt)
        gaps = np.diff(np.r_[ts, ts[0] + 360])
        k = int(np.argmax(gaps))
        t0, span = ts[(k + 1) % len(ts)], 360 - gaps[k]
        L.append({"n_vertices": int(len(lp)), "r": [float(rr.min()), float(rr.max())],
                  "z": [float(p[:, 2].min()), float(p[:, 2].max())],
                  "theta_start_deg": float(t0), "theta_span_deg": float(span)})
    res["open_boundary_loops"] = {"count": int(len(loops)), "largest": L}
    # angular coverage per radial band
    rmax = float(r.max())
    edges = np.linspace(0, rmax, a.r_bands + 1)
    bands = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = (r >= lo) & (r < hi)
        if not s.any():
            bands.append({"r": [float(lo), float(hi)], "n": 0})
            continue
        occ = np.unique(np.floor((th[s] + 180.0) / a.theta_bin_deg).astype(int))
        nb = int(round(360 / a.theta_bin_deg))
        occ_mask = np.zeros(nb, bool)
        occ_mask[np.clip(occ, 0, nb - 1)] = True
        # largest circular run of empty bins
        e2 = np.r_[~occ_mask, ~occ_mask]
        run = best = 0
        for x in e2:
            run = run + 1 if x else 0
            best = max(best, run)
        bands.append({"r": [float(lo), float(hi)], "n": int(s.sum()),
                      "z": [float(v[s, 2].min()), float(v[s, 2].max())],
                      "theta_covered_deg": float(occ_mask.sum() * a.theta_bin_deg),
                      "largest_theta_gap_deg": float(min(best, nb) * a.theta_bin_deg)})
    res["radial_bands"] = bands
    res["note"] = ("datum frame. A band whose z-max exceeds the expected top of the part, or "
                   "material on the axis above the last enumerated feature, is a CHK-ENUM item "
                   "(P03 stem). theta_covered < 360 on a round part = partial angular coverage.")
    txt = _dump(res)
    if a.out:
        a.out.write_text(txt)
    print(txt)
    return 0


# ----------------------------------------------------------------------------- scale
def cmd_scale(a: argparse.Namespace) -> int:
    """CHK-SCALE evidence. Each --pair NAME CALIPER SCAN CALIPER_UNC.
    uniform = every ratio agrees with the pooled ratio within its own uncertainty
    (caliper uncertainty + scan noise, relative). No numeric threshold is invented here."""
    rows = []
    for name, cal, scn, unc in a.pair:
        cal, scn, unc = float(cal), float(scn), float(unc)
        rel = (unc + a.scan_noise) / cal
        rows.append({"name": name, "caliper": cal, "scan": scn, "ratio": cal / scn, "rel_unc": rel})
    ratios = np.array([r["ratio"] for r in rows])
    w = 1 / np.array([r["rel_unc"] for r in rows]) ** 2
    pooled = float((ratios * w).sum() / w.sum())
    consistent = all(abs(r["ratio"] - pooled) <= r["rel_unc"] for r in rows)
    differs_from_1 = all(abs(r["ratio"] - 1.0) > r["rel_unc"] for r in rows)
    n_env = sum(1 for r in rows if r["name"].upper().startswith("ENV"))
    if n_env < 3:
        decision = "FLAG: fewer than 3 envelope dims - scale unverified, no scale applied (RE_SPEC.md:98-101)"
    elif consistent and differs_from_1:
        decision = f"UNIFORM: apply ONE scale {pooled:.6f} before datum; log in alignment.json + param table"
    elif consistent:
        decision = "NO SCALE: ratios agree with 1.0 within uncertainty"
    else:
        decision = "FLAG: non-uniform disagreement - no scale applied; calipers drive their own dims (B02)"
    res = {**json_header("scale_check", "intake.py", {}, a.seed), "scan_noise_mm": a.scan_noise,
           "pairs": rows, "pooled_ratio": pooled, "ratios_consistent": consistent,
           "all_differ_from_1": differs_from_1, "envelope_dims": n_env, "decision": decision}
    txt = _dump(res)
    if a.out:
        a.out.write_text(txt)
    print(txt)
    return 0


# ----------------------------------------------------------------------------- regime
# Canonical band keys (run-contract SS12, fixed after review V1): one flat object with
# exactly these keys, in mm, null when the regime has no such band. A gated consumer that
# finds every key null, or an unknown key, must refuse to grade rather than fall back.
BAND_KEYS = ("p95_mm", "max_mm", "tier1_abs_mm", "interface_max_mm")


def _normalize_bands(bands: dict[str, Any]) -> dict[str, Any]:
    unknown = set(bands) - set(BAND_KEYS)
    if unknown:
        raise SystemExit(f"regime: unknown band key(s) {sorted(unknown)}; canonical keys are "
                         f"{BAND_KEYS} (run-contract SS12)")
    return {k: bands.get(k) for k in BAND_KEYS}


RE_SPEC_BANDS = _normalize_bands({"p95_mm": 1.6, "max_mm": 4.0, "tier1_abs_mm": 0.15,
                                  "interface_max_mm": 0.8})
RE_SPEC_SOURCE = "baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175"
# baseline-skill only gates p95/max; it has no tier1 or interface band (both null).
BASELINE_SKILL_BANDS = {"plastic": _normalize_bands({"p95_mm": 0.30, "max_mm": 0.80}),
                        "machined": _normalize_bands({"p95_mm": 0.15, "max_mm": 0.50})}
BASELINE_SKILL_SOURCE = "baseline/skills/stl2step-build123d/SKILL.md:87"


def cmd_regime(a: argparse.Namespace) -> int:
    """Write intake/regime.json (run-contract §12): the canonical band-regime declaration."""
    bands = _normalize_bands(json.loads(a.bands)) if a.bands else None
    source = a.source
    material_class = None
    if a.name == "RE_SPEC":
        if bands is None:
            bands = dict(RE_SPEC_BANDS)
            source = source or RE_SPEC_SOURCE
    elif a.name == "baseline-skill":
        # baseline-skill always picks ONE material class at intake (run-contract SS12),
        # even when --bands overrides the numbers, so the class is recorded either way.
        if a.klass is None and bands is None:
            ap_error = "baseline-skill without --bands requires --class plastic|machined"
            raise SystemExit(ap_error)
        material_class = a.klass
        if bands is None:
            bands = dict(BASELINE_SKILL_BANDS[a.klass])
            source = source or BASELINE_SKILL_SOURCE
    else:  # project-spec
        if bands is None or not source:
            raise SystemExit("project-spec requires --bands and --source")
    if not source:
        raise SystemExit("--source is required")
    out = a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    rep: dict[str, Any] = json_header("regime", "intake.py", {}, a.seed)
    rep["name"] = a.name
    rep["source"] = source
    rep["bands"] = bands
    rep["material_class"] = material_class
    rep["why"] = a.why or ""
    txt = _dump(rep)
    (out / "regime.json").write_text(txt)
    print(txt)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=0)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("stats", help="stats + sha256 + working copy -> intake/intake.json, intake/work.stl")
    p.add_argument("scan", type=Path)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--work-faces", type=int, default=0,
                   help="decimate the working copy to this many faces (golden used 300000 DRM, "
                        "199999 B02, 250000 P03); 0 = no decimation")
    p.add_argument("--dev-samples", type=int, default=20000,
                   help="seeded samples for the work-vs-full deviation (reported, not gated)")
    p.add_argument("--keep", choices=["largest", "all"], default="largest")
    p.add_argument("--table-dir", type=lambda s: [float(x) for x in s.split(",")],
                   help="unit direction pointing from the table into the part (x,y,z)")
    p.add_argument("--table-below", type=float, help="offset along --table-dir below which up-facing faces are table")
    p.add_argument("--table-normal-min", type=float, default=0.7,
                   help="min n.table_dir for a table face (golden dreame fastgate.py:37 used 0.7)")
    p.add_argument("--orient-samples", type=int, default=500,
                   help="faces sampled for the open-mesh orientation vote (seeded)")
    p.add_argument("--save-full-clean", action="store_true",
                   help="also write the cleaned undecimated copy (work_full.stl)")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("coverage", help="occlusion / angular-coverage map of an ALIGNED mesh")
    p.add_argument("aligned", type=Path)
    p.add_argument("--r-bands", type=int, default=10)
    p.add_argument("--theta-bin-deg", type=float, default=1.0)
    p.add_argument("--max-loops", type=int, default=15)
    p.add_argument("--out", type=Path)
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("scale", help="CHK-SCALE ratio table")
    p.add_argument("--pair", nargs=4, action="append", required=True,
                   metavar=("NAME", "CALIPER", "SCAN", "CALIPER_UNC"),
                   help="use ENV-* names for envelope dims; CALIPER_UNC e.g. 0.1 for photo-transcribed")
    p.add_argument("--scan-noise", type=float, required=True, help="measured noise floor (mm)")
    p.add_argument("--out", type=Path)
    p.set_defaults(func=cmd_scale)

    p = sub.add_parser("regime", help="declare the band regime -> intake/regime.json (run-contract §12)")
    p.add_argument("--name", choices=["RE_SPEC", "baseline-skill", "project-spec"], required=True)
    p.add_argument("--source", help="path:line evidence for the bands (required for project-spec; "
                                    "defaulted for RE_SPEC/baseline-skill when --bands is omitted)")
    p.add_argument("--bands", help="JSON string, e.g. '{\"p95_mm\": 0.3, \"max_mm\": 0.8}'")
    p.add_argument("--class", dest="klass", choices=["plastic", "machined"],
                   help="required for baseline-skill when --bands is omitted")
    p.add_argument("--why", help="why this regime applies to this run")
    p.add_argument("--out-dir", type=Path, required=True)
    p.set_defaults(func=cmd_regime)

    a = ap.parse_args(argv)
    if a.cmd == "stats" and (a.table_dir is None) != (a.table_below is None):
        ap.error("--table-dir and --table-below go together")
    return int(a.func(a))


if __name__ == "__main__":
    sys.exit(main())
