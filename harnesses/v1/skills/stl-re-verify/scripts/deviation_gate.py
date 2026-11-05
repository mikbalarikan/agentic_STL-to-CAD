#!/usr/bin/env python3
"""Two-way scan<->CAD deviation gate with zones, named masks, sensitivity, observability and
over-band clusters. Writes the `deviation` block of qa/gate.json (run-contract.md §6).

Provenance:
  - dist_to_mesh(): golden-examples/OD-H12_delonghi-dedica-pump/report/src/gate.py:8-17
    (KD-tree on n_samp seeded surface samples -> exact closest point on the k candidate
    triangles) with the optional vertex augmentation of
    golden-examples/dreame_brush-caps/report/source/fastgate.py:dist_to_mesh (`--vertex-candidates`).
    Chunked over points (identical per-point result, bounded memory) and returns the winning
    triangle id so normal/boundary masks can be applied.
  - stats and z-band regions: OD gate.py:19-37, generalised to JSON zones (see _common.select).
  - named masks with fraction + inside-stats: dreame_brush-caps/report/snap_masked_gate.json
    (format) and OOM-B02 6_RE_work/qa/q20_tier2.py:35-44,63-66 (M1-M4 incl. open-boundary and
    normal-agreement masks) -- mask types "region", "open_boundary", "normal_disagreement".
  - sensitivity sweep: OOM-B02 q20_tier2.py:171-190 (open-boundary radius 0..2.5, named interfaces
    masked vs unmasked), generalised to leave-one-out per mask + radius sweep.
  - observability: observability.py (OD gate.py:57-84).
  - over-band localisation: dreame fastgate.py:62-71 (bad-point (r,z) histogram) and the P03 it1
    finding (4907 pts at r<6.4 revealed the missing stem, analysis/golden/OOM-P03.md §8);
    clustering by KD radius graph is NEW CODE.

Defaults reproduce the OD golden gate exactly: all scan vertices, k=8, 3M samples seed 0,
300k CAD samples seed 2 (OD gate.py:24-27). They are parameters, not thresholds.

Honesty rules enforced here:
  - `--scan-kind decimated` makes the run INSPECTION ONLY: gate_valid=false, never an official
    grade (golden-examples/README.md "official deviation gates must re-run against the original").
  - a registration record with converged=false makes the gate invalid
    (baseline/agents/re-qa-verifier.md:37-38 as cited in analysis/baseline/oomwoo-re-pipeline.md §3).
  - masked AND unmasked numbers are always both written; mask-dependent passes are listed
    (CHK-MASK).
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (RegimeError, band_result, header, load_matrix, load_mesh, merge_into_gate,  # noqa: E402
                     normalise_bands, read_json, select, sha256_file, stats, step_to_mesh, write_json)

TOOL = "deviation_gate.py"


# --------------------------------------------------------------------------- distance
def dist_to_mesh(pts: np.ndarray, mesh: Any, k: int = 8, n_samp: int = 3_000_000, seed: int = 0,
                 vertex_candidates: bool = False, chunk: int = 100_000) -> tuple[np.ndarray, np.ndarray]:
    """Unsigned distance from pts to mesh surface and the id of the closest candidate triangle.

    Can only OVER-estimate: the true closest triangle may lie outside the k candidates
    (analysis/golden/OD-H12.md §11).
    """
    import trimesh
    from scipy.spatial import cKDTree

    samp, fid = trimesh.sample.sample_surface(mesh, n_samp, seed=seed)
    if vertex_candidates:
        vf = mesh.vertex_faces[:, 0]
        ok = vf >= 0
        samp = np.vstack([samp, mesh.vertices[ok]])
        fid = np.concatenate([fid, vf[ok]])
    tree = cKDTree(samp)
    tris = mesh.triangles
    best = np.empty(len(pts))
    best_f = np.empty(len(pts), dtype=np.int64)
    for c0 in range(0, len(pts), chunk):
        P = pts[c0:c0 + chunk]
        _, idx = tree.query(P, k=k)
        cand = fid[idx]                                        # (n, k)
        cp = trimesh.triangles.closest_point(tris[cand.reshape(-1)], np.repeat(P, k, axis=0))
        d = np.linalg.norm(cp - np.repeat(P, k, axis=0), axis=1).reshape(-1, k)
        j = d.argmin(1)
        best[c0:c0 + chunk] = d[np.arange(len(P)), j]
        best_f[c0:c0 + chunk] = cand[np.arange(len(P)), j]
    return best, best_f


def boundary_vertices(mesh: Any) -> np.ndarray:
    """Open-boundary vertices (edges used by exactly one face). Needs a welded mesh (B02 q20:27)."""
    eu, ct = np.unique(np.sort(mesh.edges, axis=1), axis=0, return_counts=True)
    return mesh.vertices[np.unique(eu[ct == 1])]


# --------------------------------------------------------------------------- clusters
def over_band_clusters(P: np.ndarray, d: np.ndarray, thr: float, eps: float, min_pts: int,
                       top: int = 12) -> dict[str, Any]:
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree

    sel = np.where(d > thr)[0]
    out: dict[str, Any] = {"threshold_mm": thr, "eps_mm": eps, "min_pts": min_pts,
                           "n_over": int(len(sel)), "fraction_over": float(len(sel) / max(len(d), 1)),
                           "clusters": []}
    if len(sel) == 0:
        return out
    Q = P[sel]
    pairs = cKDTree(Q).query_pairs(eps, output_type="ndarray")
    g = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(Q), len(Q)))
    _, lab = connected_components(g, directed=False)
    ids, cnt = np.unique(lab, return_counts=True)
    order = np.lexsort((ids, -cnt))
    small = 0
    for o in order:
        if cnt[o] < min_pts:
            small += int(cnt[o])
            continue
        m = lab == ids[o]
        C, dd = Q[m], d[sel][m]
        r = np.hypot(C[:, 0], C[:, 1])
        th = (np.degrees(np.arctan2(C[:, 1], C[:, 0])) + 360) % 360
        if len(out["clusters"]) < top:
            out["clusters"].append({
                "n": int(m.sum()), "centroid": C.mean(0).round(3).tolist(),
                "bbox_min": C.min(0).round(3).tolist(), "bbox_max": C.max(0).round(3).tolist(),
                "r_range": [round(float(r.min()), 3), round(float(r.max()), 3)],
                "theta_deg_range": [round(float(th.min()), 1), round(float(th.max()), 1)],
                "d_p50": float(np.median(dd)), "d_max": float(dd.max())})
    out["n_clusters_ge_min"] = int((cnt >= min_pts).sum())
    out["points_in_small_clusters"] = small
    return out


# --------------------------------------------------------------------------- masks
def eval_masks(masks: list[dict[str, Any]], direction: str, P: np.ndarray, N: np.ndarray,
               Nref: np.ndarray, near_ref: np.ndarray, btree: Any,
               radius_override: dict[str, float] | None = None) -> dict[str, np.ndarray]:
    """Boolean 'inside mask' arrays for masks that apply to this direction.

    direction 's2c': P = scan points, N = scan normals, Nref = normal of the closest CAD triangle,
                     near_ref = closest point on the CAD.
    direction 'c2s': P = CAD points,  N = CAD normals,  Nref = normal of the closest scan triangle,
                     near_ref = closest point on the scan (used by the open-boundary mask).
    """
    res: dict[str, np.ndarray] = {}
    for mk in masks:
        applies = mk.get("applies_to", "scan")
        want = {"s2c": ("scan", "both"), "c2s": ("cad", "both")}[direction]
        if applies not in want:
            continue
        t = mk.get("type", "region")
        if t == "region":
            res[mk["name"]] = select(mk["select"], P, N)
        elif t == "open_boundary":
            rad = (radius_override or {}).get(mk["name"], float(mk["radius_mm"]))
            if btree is None:
                res[mk["name"]] = np.zeros(len(P), bool)
            else:
                ref = near_ref if direction == "c2s" else P
                res[mk["name"]] = btree.query(ref, workers=-1)[0] <= rad
        elif t == "normal_disagreement":
            c = np.cos(np.radians(float(mk["angle_deg"])))
            res[mk["name"]] = np.abs((N * Nref).sum(1)) < c
        else:
            raise KeyError(f"mask {mk['name']}: unknown type {t}")
    return res


def masked_block(d: np.ndarray, inside: dict[str, np.ndarray], masks: list[dict[str, Any]],
                 band: tuple[float | None, float | None]) -> dict[str, Any]:
    union = np.zeros(len(d), bool)
    per = []
    for mk in masks:
        if mk["name"] not in inside:
            continue
        m = inside[mk["name"]]
        union |= m
        per.append({"name": mk["name"], "type": mk.get("type", "region"), "why": mk.get("why", ""),
                    "evidence": mk.get("evidence", ""), "fraction": float(m.mean()) if len(m) else 0.0,
                    "stats_inside": stats(d[m])})
    un, ms = stats(d), stats(d[~union])
    return {"unmasked": un, "masked": ms, "masked_fraction": float(union.mean()) if len(d) else 0.0,
            "masks": per, "band_unmasked": band_result(un, *band), "band_masked": band_result(ms, *band),
            "_union": union}


# --------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    import trimesh
    from scipy.spatial import cKDTree

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scan", required=True, help="raw scan STL (never modified)")
    ap.add_argument("--scan-kind", required=True, choices=["full", "decimated"],
                    help="decimated => inspection only, never an official grade")
    ap.add_argument("--align", help="raw scan -> datum 4x4 (alignment.json / alignment_T1.json / .npy)")
    ap.add_argument("--cad", required=True, help="CAD as STEP (tessellated here) or STL")
    ap.add_argument("--cad-matrix", help="optional 4x4 applied to the CAD to bring it to the datum frame")
    ap.add_argument("--registration", help="qa/registration.json from tier2_icp.py (T_refine applied). "
                    "run-contract §12: verify always runs its own ICP, in every regime; omitting this "
                    "makes the run NO QA REGISTRATION, never OFFICIAL.")
    ap.add_argument("--regime", required=True, help="qa/regime.json; canonical flat bands "
                    "{p95_mm,max_mm,tier1_abs_mm,interface_max_mm} (run-contract §12). Required: a "
                    "missing regime never falls back to a default.")
    ap.add_argument("--zones", help="zones JSON (list or {zones:[...]})")
    ap.add_argument("--masks", help="masks JSON (list or {masks:[...]})")
    ap.add_argument("--s2c-points", default="all", help="'all' scan vertices or an integer subsample")
    ap.add_argument("--s2c-seed", type=int, default=0)
    ap.add_argument("--c2s-samples", type=int, default=300_000)
    ap.add_argument("--c2s-seed", type=int, default=2)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--n-samp", type=int, default=3_000_000)
    ap.add_argument("--dist-seed", type=int, default=0)
    ap.add_argument("--vertex-candidates", action="store_true", help="DRM fastgate variant")
    ap.add_argument("--no-observability", action="store_true")
    ap.add_argument("--obs-subsample", type=int, default=20000)
    ap.add_argument("--obs-seed", type=int, default=5)
    ap.add_argument("--obs-far-mm", type=float, default=0.5)
    ap.add_argument("--obs-cone-deg", type=float, default=60.0)
    ap.add_argument("--obs-max-range-mm", type=float, default=None)
    ap.add_argument("--obs-method", choices=["sky", "cone"], default="sky",
                    help="v1 default sky (two lines of sight, fixes bores counted observable); cone = v0/OD")
    ap.add_argument("--obs-tri-deg", type=float, default=20.0)
    ap.add_argument("--obs-max-incidence-deg", type=float, default=65.0)
    ap.add_argument("--sweep-radii", default="0,0.2,0.4,0.8,1.5,2.5",
                    help="open-boundary radius sweep (B02 q20_tier2.py:181-190 used these)")
    ap.add_argument("--cluster-threshold", type=float, default=None,
                    help="default: regime max band; else 0.8")
    ap.add_argument("--cluster-eps-mm", type=float, default=1.0)
    ap.add_argument("--cluster-min-pts", type=int, default=20)
    ap.add_argument("--out", required=True, help="deviation block JSON (e.g. qa/deviation.json)")
    ap.add_argument("--gate", help="also merge the block into this gate.json under 'deviation'")
    ap.add_argument("--save-arrays", help="optional .npz with points and distances")
    ap.add_argument("--supersede", action="store_true", help="review V9: an existing --out is never "
                    "silently overwritten (an earlier looser/unmasked run must not disappear). Pass "
                    "this to rename the existing file to deviation_runN.json before writing the new one.")
    a = ap.parse_args(argv)

    out_path = Path(a.out)
    if out_path.exists():
        if not a.supersede:
            print(f"ERROR: {out_path} already exists; pass --supersede to keep it as deviation_runN.json "
                 "(review V9: never add a mask after the fact / never let an earlier run disappear)",
                 file=sys.stderr)
            return 2
        n = 1
        while (out_path.parent / f"deviation_run{n}.json").exists():
            n += 1
        out_path.rename(out_path.parent / f"deviation_run{n}.json")

    # ---- regime / bands (run-contract §12; review V1/V2: canonical keys only, no default)
    regime = read_json(a.regime)
    try:
        bands = normalise_bands(regime.get("bands", {}))
    except RegimeError as e:
        print(f"ERROR: regime refused: {e}", file=sys.stderr)
        return 2
    whole_band = (bands["p95_mm"], bands["max_mm"])
    iface_max = bands["interface_max_mm"]

    # ---- scan (evidence is never written back)
    scan = load_mesh(a.scan)
    n_raw_v, n_raw_f = len(scan.vertices), len(scan.faces)
    T = load_matrix(a.align)
    scan.apply_transform(T)
    reg: dict[str, Any] = {"method": "alignment only (no QA registration)", "iterations": None,
                           "converged": None, "delta_deg": None, "delta_mm": None}
    if a.registration:
        rj = read_json(a.registration)
        Tr = np.asarray(rj["T_refine"], float)
        scan.apply_transform(np.linalg.inv(Tr))          # moves scan onto the design frame
        reg = {k: rj.get(k) for k in ("method", "iterations", "max_iterations", "converged",
                                     "delta_deg", "delta_mm")}
        reg["file"] = a.registration

    # ---- CAD
    cad_path = Path(a.cad)
    tess = None
    if cad_path.suffix.lower() in (".step", ".stp"):
        tess = Path(tempfile.mkdtemp(prefix="qa_tess_")) / (cad_path.stem + "_qa_tess.stl")
        cad = step_to_mesh(cad_path, tess)
    else:
        cad = load_mesh(cad_path)
    if a.cad_matrix:
        cad.apply_transform(load_matrix(a.cad_matrix))

    zones = read_json(a.zones) if a.zones else []
    zones = zones.get("zones", zones) if isinstance(zones, dict) else zones
    masks = read_json(a.masks) if a.masks else []
    masks = masks.get("masks", masks) if isinstance(masks, dict) else masks

    # ---- scan -> CAD
    SV = scan.vertices
    if a.s2c_points == "all":
        s_idx = np.arange(len(SV))
    else:
        rng = np.random.default_rng(a.s2c_seed)
        s_idx = np.sort(rng.choice(len(SV), min(int(a.s2c_points), len(SV)), replace=False))
    sp, sn = SV[s_idx], scan.vertex_normals[s_idx]
    print(f"scan->CAD: {len(sp)} scan points", flush=True)
    d1, f1 = dist_to_mesh(sp, cad, a.k, a.n_samp, a.dist_seed, a.vertex_candidates)

    # ---- CAD -> scan
    cp, cfi = trimesh.sample.sample_surface(cad, a.c2s_samples, seed=a.c2s_seed)
    cn = cad.face_normals[cfi]
    print(f"CAD->scan: {len(cp)} CAD samples", flush=True)
    d2, f2 = dist_to_mesh(cp, scan, a.k, a.n_samp, a.dist_seed, a.vertex_candidates)
    near_scan = trimesh.triangles.closest_point(scan.triangles[f2], cp)

    need_b = any(m.get("type") == "open_boundary" for m in masks)
    btree = cKDTree(boundary_vertices(scan)) if need_b else None

    in1 = eval_masks(masks, "s2c", sp, sn, cad.face_normals[f1], sp, btree)
    in2 = eval_masks(masks, "c2s", cp, cn, scan.face_normals[f2], near_scan, btree)
    b1 = masked_block(d1, in1, masks, whole_band)
    b2 = masked_block(d2, in2, masks, whole_band)
    u1, u2 = b1.pop("_union"), b2.pop("_union")

    res: dict[str, Any] = {
        "scan": {"path": a.scan, "sha256": sha256_file(a.scan), "kind": a.scan_kind,
                 "full_res": a.scan_kind == "full", "vertices": n_raw_v, "faces": n_raw_f},
        "cad": {"path": a.cad, "sha256": sha256_file(a.cad), "tessellated_by_qa": tess is not None,
                "tessellation": {"tolerance": 0.005, "angular_tolerance": 0.05} if tess else None,
                "faces": len(cad.faces)},
        "frame": "datum" if a.align or a.cad_matrix else "as loaded",
        "registration": reg,
        "sampling": {"s2c_points": a.s2c_points, "s2c_seed": a.s2c_seed, "c2s_samples": a.c2s_samples,
                     "c2s_seed": a.c2s_seed, "k": a.k, "n_samp": a.n_samp, "dist_seed": a.dist_seed,
                     "vertex_candidates": a.vertex_candidates,
                     "method": "KD candidates -> exact point-to-triangle (OD gate.py:8-17)"},
        "regime": {"name": regime.get("name"), "source": regime.get("source"), "bands": bands},  # bands: canonical, normalised (run-contract §12)
        "scan_to_cad": b1["unmasked"], "cad_to_scan": b2["unmasked"],
        "scan_to_cad_masked": b1["masked"], "cad_to_scan_masked": b2["masked"],
        "unmasked": {"scan_to_cad": b1["unmasked"], "cad_to_scan": b2["unmasked"]},
        "masked_fraction": {"scan_to_cad": b1["masked_fraction"], "cad_to_scan": b2["masked_fraction"]},
        "bands": {"scan_to_cad": {"unmasked": b1["band_unmasked"], "masked": b1["band_masked"]},
                  "cad_to_scan": {"unmasked": b2["band_unmasked"], "masked": b2["band_masked"]}},
        "masks": [{**m, "direction": "scan_to_cad"} for m in b1["masks"]]
                 + [{**m, "direction": "cad_to_scan"} for m in b2["masks"]],
    }

    # ---- observability (CAD->scan split)
    if not a.no_observability:
        from observability import observable_split, observable_split_sky

        if a.obs_method == "sky":
            ob = observable_split_sky(cad, cp, cfi, d2, a.obs_subsample, a.obs_seed, a.obs_far_mm,
                                      max_incidence_deg=a.obs_max_incidence_deg, tri_deg=a.obs_tri_deg,
                                      max_range_mm=a.obs_max_range_mm)
        else:
            ob = observable_split(cad, cp, cfi, d2, a.obs_subsample, a.obs_seed, a.obs_far_mm, a.obs_cone_deg,
                                  max_range_mm=a.obs_max_range_mm)
        res["cad_to_scan_observable"] = ob["observable"]
        res["unobservable_fraction"] = ob["unobservable_fraction"]
        res["observability"] = {k: v for k, v in ob.items() if not k.startswith("_")}
        res["bands"]["cad_to_scan_observable"] = band_result(ob["observable"], *whole_band)

    # ---- zones
    zres: dict[str, Any] = {}
    for z in zones:
        kind = z.get("kind", "region")
        if kind == "functional_interface":
            zb: tuple[float | None, float | None] = (None, z.get("band_max", iface_max))
        elif kind == "whole":
            zb = whole_band
        else:
            zb = (None, None)                              # interior / region: reported, not gated
        entry: dict[str, Any] = {"kind": kind, "note": z.get("note", ""), "band": list(zb)}
        for dname, P, N, d, un in (("scan_to_cad", sp, sn, d1, u1), ("cad_to_scan", cp, cn, d2, u2)):
            if dname not in z.get("directions", ["scan_to_cad", "cad_to_scan"]):
                continue
            m = select(z["select"], P, N)
            su, sm = stats(d[m]), stats(d[m & ~un])
            entry[dname] = {"unmasked": su, "masked": sm,
                            "masked_fraction": float((m & un).sum() / max(m.sum(), 1)),
                            "band_unmasked": band_result(su, *zb), "band_masked": band_result(sm, *zb)}
        zres[z["name"]] = entry
    res["zones"] = zres

    # ---- sensitivity (CHK-MASK)
    sens: list[dict[str, Any]] = []
    for dname, d, inside in (("scan_to_cad", d1, in1), ("cad_to_scan", d2, in2)):
        if not inside:
            continue
        names = list(inside)
        allm = np.zeros(len(d), bool)
        for n_ in names:
            allm |= inside[n_]
        for n_ in names:                                   # leave-one-out
            rest = np.zeros(len(d), bool)
            for o in names:
                if o != n_:
                    rest |= inside[o]
            s_ = stats(d[~rest])
            sens.append({"direction": dname, "variant": f"all masks except {n_}", "stats": s_,
                         "band": band_result(s_, *whole_band)})
    radii = [float(t) for t in a.sweep_radii.split(",") if t.strip()]
    for mk in masks:
        if mk.get("type") != "open_boundary" or btree is None:
            continue
        for rad in radii:
            for dname, P, N, Nref, near, d in (("scan_to_cad", sp, sn, cad.face_normals[f1], sp, d1),
                                               ("cad_to_scan", cp, cn, scan.face_normals[f2], near_scan, d2)):
                ins = eval_masks(masks, "s2c" if dname == "scan_to_cad" else "c2s", P, N, Nref, near,
                                 btree, {mk["name"]: rad})
                if mk["name"] not in ins:
                    continue
                un = np.zeros(len(d), bool)
                for v in ins.values():
                    un |= v
                s_ = stats(d[~un])
                row: dict[str, Any] = {"direction": dname, "variant": f"{mk['name']} radius {rad} mm",
                                       "stats": s_, "band": band_result(s_, *whole_band), "zones": {}}
                for z in zones:
                    if z.get("kind") != "functional_interface":
                        continue
                    zm = select(z["select"], P, N)
                    zs = stats(d[zm & ~un])
                    row["zones"][z["name"]] = {"stats": zs, "band": band_result(zs, None, z.get("band_max", iface_max))}
                sens.append(row)
    res["sensitivity"] = sens

    # mask-dependent passes: pass masked, fail unmasked
    mdp: list[str] = []
    for dname in ("scan_to_cad", "cad_to_scan"):
        bu, bm = res["bands"][dname]["unmasked"], res["bands"][dname]["masked"]
        if bu and bm and bm["pass"] and not bu["pass"]:
            mdp.append(f"whole part {dname}")
    for zn, e in zres.items():
        for dname in ("scan_to_cad", "cad_to_scan"):
            if dname in e and e[dname]["band_masked"] and e[dname]["band_unmasked"]:
                if e[dname]["band_masked"]["pass"] and not e[dname]["band_unmasked"]["pass"]:
                    mdp.append(f"zone {zn} {dname}")
    # review V5: CHK-MASK also applies to the observability split -- a whole-part pass that exists
    # only because unobservable points were excluded is mask-dependent too, not a clean pass.
    obs_band = res["bands"].get("cad_to_scan_observable")
    if obs_band and res["bands"]["cad_to_scan"]["unmasked"] and obs_band["pass"] and \
            not res["bands"]["cad_to_scan"]["unmasked"]["pass"]:
        mdp.append(f"whole part cad_to_scan (observable-only pass; "
                   f"{100 * res.get('unobservable_fraction', 0):.2f}% unobservable excluded)")
    res["mask_dependent_passes"] = mdp

    # ---- over-band clusters (CHK-ENUM / CHK-CLUSTER evidence)
    thr = a.cluster_threshold if a.cluster_threshold is not None else (whole_band[1] or 0.8)
    res["over_band_clusters"] = {
        "scan_to_cad": over_band_clusters(sp, d1, thr, a.cluster_eps_mm, a.cluster_min_pts),
        "cad_to_scan": over_band_clusters(cp, d2, thr, a.cluster_eps_mm, a.cluster_min_pts),
        "reading": "scan_to_cad clusters = scan material the CAD lacks (missing feature or artefact); "
                   "cad_to_scan clusters = CAD material with no scan (invented or unobservable)"}

    # ---- validity of the gate itself
    # run-contract §12 / review V3: verify always runs its own ICP, in EVERY regime, and grades
    # after ICP. An alignment-only run (no --registration) is never OFFICIAL, regardless of regime.
    reasons = []
    if a.scan_kind != "full":
        reasons.append("decimated scan: INSPECTION ONLY, not an official grade")
    if a.registration is None:
        reasons.append("no independent QA registration (ICP) recorded: run-contract §12 requires "
                       "verify's own ICP in every regime; this run cannot be labelled OFFICIAL")
    elif reg.get("converged") is False:
        reasons.append("registration did not converge: gate invalid")
    res["gate_valid"] = not reasons
    res["gate_invalid_reasons"] = reasons
    if a.scan_kind != "full":
        label = "INSPECTION ONLY"
    elif a.registration is None:
        label = "NO QA REGISTRATION"
    elif reg.get("converged") is False:
        label = "INVALID"
    else:
        label = "OFFICIAL (full-res)"
    res["label"] = label

    inputs = [a.scan, a.cad] + [p for p in (a.align, a.cad_matrix, a.registration, a.regime, a.zones, a.masks) if p]
    out = {**header("deviation", TOOL, inputs, a.dist_seed), **res}
    write_json(a.out, out)
    if a.gate:
        merge_into_gate(a.gate, "deviation", out)
    if a.save_arrays:
        np.savez_compressed(a.save_arrays, s2c_pts=sp, s2c_d=d1, c2s_pts=cp, c2s_fid=cfi, c2s_d=d2)

    for k in ("scan_to_cad", "cad_to_scan", "scan_to_cad_masked", "cad_to_scan_masked", "cad_to_scan_observable"):
        if k in res and res[k]["n"]:
            s = res[k]
            print(f"{k:24s} n {s['n']:8d} rms {s['rms']:.4f} p50 {s['p50']:.4f} p95 {s['p95']:.4f} "
                  f"p99 {s['p99']:.4f} max {s['max']:.4f}")
    if "unobservable_fraction" in res:
        print(f"unobservable CAD fraction {100 * res['unobservable_fraction']:.2f}%")
    for zn, e in zres.items():
        for dname in ("scan_to_cad", "cad_to_scan"):
            if dname in e:
                s = e[dname]["unmasked"]
                if s["n"]:
                    print(f"  zone {zn:30s} {dname:12s} n {s['n']:7d} p95 {s['p95']:.3f} max {s['max']:.3f}")
    print("label:", res["label"], "| mask-dependent passes:", mdp or "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
