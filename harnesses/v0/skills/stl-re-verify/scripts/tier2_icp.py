#!/usr/bin/env python3
"""Independent QA registration: point-to-point ICP of the CAD onto the aligned scan with masked
correspondences, and an honest convergence record.

Provenance: lifted and generalised from
golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q20_tier2.py:23-110
  - weld the unwelded STL (merge_vertices) and invert inward normals (q20:26-30)
  - scan region masks (bristles, COTS screw) removed from the ICP reference (q20:32-46) -> JSON predicates
  - open-boundary vertices of the masked scan (q20:48-52)
  - dense seeded scan samples (3M, seed 11) and CAD samples (300k, seed 13) (q20:55-68)
  - correspondence filter: |n_cad . n_scan| > cos 70 deg, nearest scan sample > 0.8 mm from an
    open boundary, distance < 3.0 mm (q20:71-75)
  - Kabsch/SVD update, cap 60 iterations, stop when step < 1e-6 (q20:77-95)
All of these are the golden's PARAMETERS (recorded in the output), not thresholds.

Honesty rules (analysis/baseline/oomwoo-re-pipeline.md §3, citing baseline/agents/re-qa-verifier.md:37-38):
hitting the iteration cap => converged=false => deviation_gate.py marks the gate INVALID.
The W01 failure (ICP hit its 50-iteration cap at 3.645 deg / 0.973 mm) is why
(baseline/oomwoo-re-pipeline/TRACKER.md:32 via analysis/baseline/oomwoo-re-pipeline.md §5).

CHK-CIRCULAR: T_refine is QA's own evaluation registration. It is NEVER written back into
intake/alignment.json (OOM-P03 refined its datum by ICP to its own CAD; analysis/golden/OOM-P03.md §3).
"""
from __future__ import annotations

import argparse
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, load_matrix, load_mesh, merge_into_gate, read_json, rot_angle_deg, select, step_to_mesh, write_json  # noqa: E402,E501

TOOL = "tier2_icp.py"


def icp(cp: np.ndarray, cn: np.ndarray, sp: np.ndarray, sn: np.ndarray, btree: Any, normal_deg: float,
        boundary_mm: float, max_corr_mm: float, max_iter: int, tol: float) -> dict[str, Any]:
    from scipy.spatial import cKDTree

    stree = cKDTree(sp)
    cosang = math.cos(math.radians(normal_deg))

    def corr(P: np.ndarray, Nn: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        d, i = stree.query(P, workers=-1)
        ok = (np.abs((Nn * sn[i]).sum(1)) > cosang) & (d < max_corr_mm)
        if btree is not None:
            ok &= btree.query(sp[i], workers=-1)[0] > boundary_mm
        return d, i, ok

    T = np.eye(4)
    P, Nn = cp.copy(), cn.copy()
    trace: list[dict[str, float]] = []
    converged = False
    it = -1
    for it in range(max_iter):
        d, i, ok = corr(P, Nn)
        A_, B_ = P[ok], sp[i][ok]
        ca, cb = A_.mean(0), B_.mean(0)
        H = (A_ - ca).T @ (B_ - cb)
        U, _, Vt = np.linalg.svd(H)
        D = np.diag([1.0, 1.0, float(np.sign(np.linalg.det(Vt.T @ U.T)))])
        R = Vt.T @ D @ U.T
        t = cb - R @ ca
        P = P @ R.T + t
        Nn = Nn @ R.T
        rot = rot_angle_deg(R)
        step = float(np.linalg.norm(t) + rot)
        Tn = np.eye(4)
        Tn[:3, :3], Tn[:3, 3] = R, t
        T = Tn @ T
        trace.append({"it": it, "step": step, "rot_deg": rot, "trans_mm": float(np.linalg.norm(t)),
                      "kept_fraction": float(ok.mean()), "mean_d_kept": float(d[ok].mean())})
        if step < tol:
            converged = True
            break
    d, i, ok = corr(P, Nn)
    return {"T_refine": T, "iterations": it + 1, "converged": converged, "trace_tail": trace[-6:],
            "final_kept_fraction": float(ok.mean()), "max_point_move_mm": float(np.linalg.norm(P - cp, axis=1).max())}


def main(argv: list[str] | None = None) -> int:
    import trimesh
    from scipy.spatial import cKDTree

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scan", required=True)
    ap.add_argument("--scan-kind", required=True, choices=["full", "decimated"])
    ap.add_argument("--align", required=True, help="raw -> datum 4x4 from intake (read only)")
    ap.add_argument("--cad", required=True, help="STEP (tessellated here) or STL, datum frame")
    ap.add_argument("--cad-matrix", help="optional 4x4 bringing the CAD into the datum frame")
    ap.add_argument("--scan-masks", help="JSON list of region masks removed from the ICP reference")
    ap.add_argument("--ns", type=int, default=3_000_000)
    ap.add_argument("--scan-seed", type=int, default=11)
    ap.add_argument("--nc", type=int, default=300_000)
    ap.add_argument("--cad-seed", type=int, default=13)
    ap.add_argument("--normal-deg", type=float, default=70.0)
    ap.add_argument("--boundary-mm", type=float, default=0.8)
    ap.add_argument("--max-corr-mm", type=float, default=3.0)
    ap.add_argument("--max-iter", type=int, default=60)
    ap.add_argument("--tol", type=float, default=1e-6)
    ap.add_argument("--out", required=True, help="e.g. qa/registration.json")
    ap.add_argument("--gate", help="merge into gate.json under deviation.registration_detail")
    a = ap.parse_args(argv)

    s = load_mesh(a.scan, process=False)
    s.merge_vertices()
    notes = [f"welded: {len(s.vertices)} verts / {len(s.faces)} faces"]
    if s.volume < 0:
        s.invert()
        notes.append("scan normals were inward -> inverted on the QA copy (evidence file untouched)")
    s.apply_transform(load_matrix(a.align))
    masks = read_json(a.scan_masks) if a.scan_masks else []
    masks = masks.get("masks", masks) if isinstance(masks, dict) else masks
    removed = []
    if masks:
        fc, fn = s.triangles_center, s.face_normals
        drop = np.zeros(len(fc), bool)
        for mk in masks:
            m = select(mk["select"], fc, fn)
            removed.append({"name": mk["name"], "why": mk.get("why", ""), "faces": int(m.sum()),
                            "fraction": float(m.mean())})
            drop |= m
        s.update_faces(~drop)
        s.remove_unreferenced_vertices()
    eu, ct = np.unique(np.sort(s.edges, axis=1), axis=0, return_counts=True)
    bverts = s.vertices[np.unique(eu[ct == 1])]
    btree = cKDTree(bverts) if len(bverts) else None
    sp, sf = trimesh.sample.sample_surface(s, a.ns, seed=a.scan_seed)
    sn = s.face_normals[sf]

    cad_path = Path(a.cad)
    if cad_path.suffix.lower() in (".step", ".stp"):
        c = step_to_mesh(cad_path, Path(tempfile.mkdtemp(prefix="qa_tess_")) / "cad.stl")
    else:
        c = load_mesh(cad_path)
    if a.cad_matrix:
        c.apply_transform(load_matrix(a.cad_matrix))
    cp, cf = trimesh.sample.sample_surface(c, a.nc, seed=a.cad_seed)
    cn = c.face_normals[cf]

    r = icp(cp, cn, sp, sn, btree, a.normal_deg, a.boundary_mm, a.max_corr_mm, a.max_iter, a.tol)
    T = r["T_refine"]
    out = {
        **header("registration", TOOL, [p for p in (a.scan, a.align, a.cad, a.cad_matrix, a.scan_masks) if p],
                 a.scan_seed),
        "method": "point-to-point ICP, CAD samples -> scan samples, masked correspondences (B02 q20_tier2.py)",
        "scan_kind": a.scan_kind,
        "iterations": r["iterations"], "max_iterations": a.max_iter, "converged": r["converged"],
        "delta_deg": rot_angle_deg(T), "delta_mm": float(np.linalg.norm(T[:3, 3])),
        "max_point_move_mm": r["max_point_move_mm"], "final_kept_fraction": r["final_kept_fraction"],
        "T_refine": T.tolist(),
        "T_refine_meaning": "maps datum-frame CAD onto the aligned scan; deviation_gate applies its inverse "
                            "to the scan. QA-only: never written back to alignment.json (CHK-CIRCULAR).",
        "trace_tail": r["trace_tail"],
        "reference_masks_removed": removed,
        "params": {"ns": a.ns, "scan_seed": a.scan_seed, "nc": a.nc, "cad_seed": a.cad_seed,
                   "normal_deg": a.normal_deg, "boundary_mm": a.boundary_mm, "max_corr_mm": a.max_corr_mm,
                   "max_iter": a.max_iter, "tol": a.tol},
        "notes": notes,
    }
    write_json(a.out, out)
    if a.gate:
        merge_into_gate(a.gate, "registration", out)
    print(f"ICP {'converged' if r['converged'] else 'NOT CONVERGED'} in {r['iterations']}/{a.max_iter} its | "
          f"correction {out['delta_deg']:.4f} deg, {out['delta_mm']:.4f} mm | max point move "
          f"{r['max_point_move_mm']:.4f} mm | kept {100 * r['final_kept_fraction']:.1f}%")
    return 0 if r["converged"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
