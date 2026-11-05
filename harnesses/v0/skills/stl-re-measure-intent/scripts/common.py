"""Shared helpers for the stl-re-measure-intent scripts.

Provenance: NEW helper module. `densify` is lifted unchanged in behaviour from
golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/qa/q10_solid_tess_tier1.py:densify
(also 40_verify.py:densify). Mesh loading + raw->datum transform follows the
convention of golden-examples/dreame_brush-caps/report/source/align.py (row-major
matrix_4x4, scan -> datum). JSON header per harnesses/v0/skills/stl-re-orchestrate/references/
run-contract.md §2. Changes: typed, no hard-coded paths, `created` is the only
wall-clock value and never feeds a computation.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
import trimesh

TOOL_VERSION = "stl-re-measure-intent@1.0.0"


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def header(schema_file: str, tool: str, inputs: Iterable[str | Path], seed: int = 0) -> dict[str, Any]:
    """Common JSON header (run-contract §2). `created` is provenance only."""
    return {
        "schema": f"stl-re/{schema_file}@1",
        "tool": tool,
        "tool_version": TOOL_VERSION,
        "inputs": {str(p): sha256(p) for p in inputs if p is not None and Path(p).is_file()},
        "seed": seed,
        "created": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
    }


def load_alignment(path: Optional[str | Path]) -> Optional[dict[str, Any]]:
    if path is None:
        return None
    with open(path) as f:
        return json.load(f)


def scan_noise_mm(alignment: Optional[dict[str, Any]]) -> Optional[float]:
    """alignment.json scan_noise_mm.value (run-contract §3); None if absent."""
    if not alignment:
        return None
    v = alignment.get("scan_noise_mm")
    if isinstance(v, dict) and v.get("value") is not None:
        return float(v["value"])
    if isinstance(v, (int, float)):
        return float(v)
    return None


def load_mesh(mesh_path: str | Path, alignment: Optional[dict[str, Any]] = None,
              keep_largest: bool = False) -> trimesh.Trimesh:
    """Load an STL (welded) and, if given, apply alignment.json matrix_4x4 (raw -> datum).

    Pass alignment=None when the mesh is already in the datum frame
    (e.g. intake/aligned_work.stl). scale_factor is NOT applied here: the intake skill
    owns CHK-SCALE; a non-unit scale_factor is reported by the caller.
    """
    m = trimesh.load_mesh(str(mesh_path), process=True)
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate(list(m.geometry.values()))
    if keep_largest:
        lab = face_components(m, np.arange(len(m.faces)))
        if lab.max() > 0:
            big = np.bincount(lab).argmax()
            m = m.submesh([np.where(lab == big)[0]], append=True)
    if alignment is not None:
        T = np.asarray(alignment["matrix_4x4"], dtype=float)
        m.apply_transform(T)
    return m


def face_components(m: trimesh.Trimesh, faces: np.ndarray) -> np.ndarray:
    """Connected-component label per face in `faces` (edge adjacency; scipy, no networkx)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    faces = np.asarray(faces)
    idx = -np.ones(len(m.faces), dtype=int)
    idx[faces] = np.arange(len(faces))
    adj = m.face_adjacency
    k = (idx[adj[:, 0]] >= 0) & (idx[adj[:, 1]] >= 0)
    a, b = idx[adj[k, 0]], idx[adj[k, 1]]
    g = coo_matrix((np.ones(len(a)), (a, b)), shape=(len(faces), len(faces)))
    return connected_components(g, directed=False)[1]


def densify(p: np.ndarray, ds: float = 0.02) -> np.ndarray:
    """Resample a polyline so statistics are not vertex-limited (B02 q10::densify, ds 0.02 mm)."""
    p = np.asarray(p, dtype=float)
    if len(p) < 2:
        return p
    seg = np.diff(p, axis=0)
    L = np.linalg.norm(seg, axis=1)
    n = np.maximum((L / ds).astype(int), 1)
    idx = np.repeat(np.arange(len(seg)), n)
    k = np.concatenate([np.arange(c) for c in n]) / np.repeat(n, n)
    out = p[idx] + seg[idx] * k[:, None]
    return np.vstack([out, p[-1:]])


def section_polylines(mesh: trimesh.Trimesh, origin, normal) -> list[np.ndarray]:
    """3D polylines of a plane section (one per path entity); [] when the plane misses."""
    s = mesh.section(plane_origin=np.asarray(origin, float), plane_normal=np.asarray(normal, float))
    if s is None:
        return []
    # entities are already chained polylines; avoid Path.discrete (needs networkx)
    return [np.asarray(s.vertices[e.points], dtype=float) for e in s.entities]


def z_section_xy(mesh: trimesh.Trimesh, z: float) -> list[np.ndarray]:
    return [p[:, :2] for p in section_polylines(mesh, [0, 0, z], [0, 0, 1])]


def is_closed(p: np.ndarray, tol: float = 1e-6) -> bool:
    return len(p) >= 4 and float(np.linalg.norm(p[0] - p[-1])) <= tol


def shoelace(xy: np.ndarray) -> tuple[float, np.ndarray]:
    """Signed area and centroid of a closed 2D polyline."""
    x, y = xy[:, 0], xy[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    c = x * y1 - x1 * y
    a = 0.5 * c.sum()
    if abs(a) < 1e-12:
        return 0.0, xy.mean(axis=0)
    cx = ((x + x1) * c).sum() / (6 * a)
    cy = ((y + y1) * c).sum() / (6 * a)
    return float(a), np.array([cx, cy])


def wrap_deg(a):
    return (np.asarray(a) + 180.0) % 360.0 - 180.0


def write_json(path: str | Path, obj: dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=_np_default)
        f.write("\n")


def _np_default(o: Any) -> Any:
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


def rnd(x: float, nd: int = 6) -> Optional[float]:
    """Round for JSON output only (never used in a computation)."""
    if x is None or not np.isfinite(x):
        return None
    return round(float(x), nd)
