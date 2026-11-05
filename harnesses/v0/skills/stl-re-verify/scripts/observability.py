#!/usr/bin/env python3
"""CAD->scan observability split: which CAD surface points could a scanner have seen?

Provenance: lifted from golden-examples/OD-H12_delonghi-dedica-pump/report/src/gate.py:57-84
(heuristic, n=1: OD-H12 -- OOM-B02 served the same purpose with an open-boundary mask, see
deviation_gate.py mask type "open_boundary").

Method (unchanged from OD): take a seeded subsample of the CAD->scan sample points; the points
whose CAD->scan distance exceeds `far_mm` are ray-tested: one ray along the outward CAD normal
plus `n_ring` rays on a cone of half-angle `cone_deg` around it, each starting `offset_mm` off the
surface. If EVERY ray hits the CAD again, no line of sight existed and the point is
"unobservable". Observable stats are computed over the subsample minus the unobservable points.

Changes vs the golden, all recorded in the output `params`:
  1. Degenerate helper vector fixed. OD built the cone basis from cross(n, [0.3,0.5,0.8]); for a
     normal parallel to that vector the basis is NaN. Here the same helper is used (so results
     are identical wherever the golden was well defined) and only near-parallel normals
     (|n.h| > 0.9) switch to a second helper.
  2. Optional ray range `max_range_mm`. The OD comment says "within 60 mm" but the code has no
     range (intersects_any is unbounded). Default None = the golden's actual behaviour.
  3. Parameters are explicit CLI/API arguments, not literals.

The golden parameters are the defaults: subsample 20000, seed 5, far 0.5 mm, cone 60 deg,
6 ring rays, offset 0.05 mm (OD gate.py:62-72). They are parameters, not thresholds
(analysis/SYNTHESIS.md §4 last paragraph).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import header, load_mesh, stats, write_json  # noqa: E402

TOOL = "observability.py"
LEGACY_HELPER = np.array([0.3, 0.5, 0.8])
ALT_HELPER = np.array([1.0, 0.0, 0.0])


def cone_basis(nrm: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    """Orthonormal (a, b) perpendicular to each normal. Returns count of helper switches."""
    h = np.tile(LEGACY_HELPER, (len(nrm), 1))
    hn = LEGACY_HELPER / np.linalg.norm(LEGACY_HELPER)
    bad = np.abs(nrm @ hn) > 0.9
    h[bad] = ALT_HELPER
    still = bad & (np.abs(nrm @ ALT_HELPER) > 0.9)
    h[still] = np.array([0.0, 1.0, 0.0])
    a = np.cross(nrm, h)
    a /= np.linalg.norm(a, axis=1)[:, None]
    b = np.cross(nrm, a)
    return a, b, int(bad.sum())


def observable_split(cad: Any, pts: np.ndarray, face_idx: np.ndarray, d: np.ndarray,
                     subsample: int = 20000, seed: int = 5, far_mm: float = 0.5,
                     cone_deg: float = 60.0, n_ring: int = 6, offset_mm: float = 0.05,
                     max_range_mm: float | None = None, chunk: int = 2000) -> dict[str, Any]:
    """Return observable stats, unobservable fraction and the per-subsample mask."""
    from trimesh.ray.ray_triangle import RayMeshIntersector

    rng = np.random.default_rng(seed)
    sub = rng.choice(len(pts), min(subsample, len(pts)), replace=False)
    far = sub[d[sub] > far_mm]
    nrm = cad.face_normals[face_idx[far]]
    a, b, switched = cone_basis(nrm)
    c, s = np.cos(np.radians(cone_deg)), np.sin(np.radians(cone_deg))
    dirs = [nrm] + [c * nrm + s * (np.cos(t) * a + np.sin(t) * b)
                    for t in np.linspace(0, 2 * np.pi, n_ring, endpoint=False)]
    rmi = RayMeshIntersector(cad)
    hit_all = np.ones(len(far), bool)
    for D in dirs:
        for c0 in range(0, len(far), chunk):
            sl = slice(c0, c0 + chunk)
            todo = np.where(hit_all[sl])[0]
            if len(todo) == 0:
                continue
            O = pts[far][sl][todo] + offset_mm * nrm[sl][todo]
            Dd = D[sl][todo]
            if max_range_mm is None:
                h = rmi.intersects_any(O, Dd)
            else:
                loc, ray_i, _ = rmi.intersects_location(O, Dd, multiple_hits=False)
                h = np.zeros(len(todo), bool)
                if len(ray_i):
                    dist = np.linalg.norm(loc - O[ray_i], axis=1)
                    h[ray_i[dist <= max_range_mm]] = True
            idx = np.arange(len(far))[sl][todo]
            hit_all[idx[~h]] = False
    unobs = far[hit_all]
    obs_mask = ~np.isin(sub, unobs)
    return {
        "observable": stats(d[sub][obs_mask]),
        "unobservable_fraction": float(1.0 - obs_mask.mean()),
        "n_subsample": int(len(sub)),
        "n_far_tested": int(len(far)),
        "params": {"method": "ray cone on CAD (OD gate.py:57-84)", "subsample": subsample, "seed": seed,
                   "far_mm": far_mm, "cone_deg": cone_deg, "n_ring": n_ring, "offset_mm": offset_mm,
                   "max_range_mm": max_range_mm, "helper": LEGACY_HELPER.tolist(),
                   "helper_switched_for_n_points": switched,
                   "ray_engine": "trimesh.ray.ray_triangle.RayMeshIntersector"},
        "_sub": sub, "_obs_mask": obs_mask,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cad", required=True, help="CAD mesh (STL) in the same frame as the points")
    ap.add_argument("--points", required=True,
                    help=".npz from deviation_gate.py --save-arrays (keys c2s_pts, c2s_fid, c2s_d)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--subsample", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--far-mm", type=float, default=0.5)
    ap.add_argument("--cone-deg", type=float, default=60.0)
    ap.add_argument("--n-ring", type=int, default=6)
    ap.add_argument("--offset-mm", type=float, default=0.05)
    ap.add_argument("--max-range-mm", type=float, default=None)
    a = ap.parse_args(argv)
    cad = load_mesh(a.cad)
    z = np.load(a.points)
    res = observable_split(cad, z["c2s_pts"], z["c2s_fid"], z["c2s_d"], a.subsample, a.seed, a.far_mm,
                           a.cone_deg, a.n_ring, a.offset_mm, a.max_range_mm)
    res = {k: v for k, v in res.items() if not k.startswith("_")}
    write_json(a.out, {**header("observability", TOOL, [a.cad, a.points], a.seed), **res})
    print(f"observable CAD->scan n {res['observable']['n']} p95 {res['observable']['p95']:.3f} "
          f"max {res['observable']['max']:.3f} | unobservable {100 * res['unobservable_fraction']:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
