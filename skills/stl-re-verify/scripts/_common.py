"""Shared helpers for the stl-re-verify scripts (QA-owned; never import builder helpers).

Provenance:
  - stats(): golden-examples/OD-H12_delonghi-dedica-pump/report/src/gate.py:19-20 (rms/p95/p99/max/mean/n)
    + golden-examples/dreame_brush-caps/report/source/fastgate.py:stats (p50). Merged: n, rms, mean,
    p50, p95, p99, max.
  - JSON header: skills/stl-re-orchestrate/references/run-contract.md §2.
  - Predicate language for zones/masks: NEW CODE. Replaces the hard-coded boolean expressions in
    OD gate.py:30-37, B02 6_RE_work/qa/q20_tier2.py:35-44,139-151 and the mask strings of
    dreame_brush-caps/report/snap_masked_gate.json so zones and masks live in a JSON spec.
  - load_matrix(): accepts RE_SPEC alignment.json (`matrix_4x4`), OD alignment_T1.json
    (`T1_original_stl_to_datum`) and .npy (OD report/src/T1.npy).

Determinism: no randomness here; the only wall-clock value is the provenance field `created`
(set SOURCE_DATE_EPOCH to pin it).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

SKILL_VERSION = "stl-re-verify@1"


# --------------------------------------------------------------------------- files / header
def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def created_stamp() -> str:
    """Provenance-only timestamp (run-contract §2). Never used in a computation."""
    sde = os.environ.get("SOURCE_DATE_EPOCH")
    t = _dt.datetime.fromtimestamp(int(sde), _dt.timezone.utc) if sde else _dt.datetime.now(_dt.timezone.utc)
    return t.replace(microsecond=0).isoformat()


def header(schema: str, tool: str, inputs: Sequence[str | Path], seed: int | None) -> dict[str, Any]:
    return {
        "schema": f"stl-re/{schema}@1",
        "tool": tool,
        "tool_version": SKILL_VERSION,
        "inputs": {str(p): sha256_file(p) for p in inputs if p and Path(p).is_file()},
        "seed": seed,
        "created": created_stamp(),
    }


def _json_default(o: Any) -> Any:
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serialisable: {type(o)}")


def write_json(path: str | Path, obj: Mapping[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, default=_json_default) + "\n", encoding="utf-8")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def merge_into_gate(gate_path: str | Path, key: str, block: Any) -> None:
    """Read-modify-write one top-level key of qa/gate.json (run-contract §6)."""
    p = Path(gate_path)
    g: dict[str, Any] = read_json(p) if p.is_file() else {}
    g[key] = block
    write_json(p, g)


# --------------------------------------------------------------------------- statistics
def stats(d: np.ndarray) -> dict[str, Any]:
    d = np.asarray(d, float)
    if d.size == 0:
        return {"n": 0, "rms": None, "mean": None, "p50": None, "p95": None, "p99": None, "max": None}
    return {
        "n": int(d.size),
        "rms": float(np.sqrt((d ** 2).mean())),
        "mean": float(d.mean()),
        "p50": float(np.percentile(d, 50)),
        "p95": float(np.percentile(d, 95)),
        "p99": float(np.percentile(d, 99)),
        "max": float(d.max()),
    }


CANONICAL_BAND_KEYS = ("p95_mm", "max_mm", "tier1_abs_mm", "interface_max_mm")


class RegimeError(ValueError):
    """Raised when a regime's bands cannot be graded (run-contract §12)."""


def normalise_bands(bands: Mapping[str, Any] | None) -> dict[str, float | None]:
    """Read only the canonical flat band keys (run-contract §12, "Band keys (canonical)", fixed
    after review V1): `p95_mm`, `max_mm`, `tier1_abs_mm`, `interface_max_mm`, each `null` when the
    regime has no such band. Never falls back to a default and never accepts an old/aliased key
    (e.g. `tier2_p95_mm`, `p95`) -- an unknown key means the regime file is stale or wrong, which is
    exactly how the gate failed open in review V1.

    Raises RegimeError when a key outside `CANONICAL_BAND_KEYS` is present, or when every gated key
    (p95_mm/max_mm/tier1_abs_mm; interface_max_mm alone never grades the whole part) is null --
    a caller must refuse to grade (non-zero exit, error recorded in qa/gate.json#errors).
    """
    b = dict(bands or {})
    unknown = sorted(k for k in b if k not in CANONICAL_BAND_KEYS)
    if unknown:
        raise RegimeError(
            f"unknown band key(s) {unknown}; canonical keys are {CANONICAL_BAND_KEYS} (run-contract §12)")
    out = {k: b.get(k) for k in CANONICAL_BAND_KEYS}
    if out["p95_mm"] is None and out["max_mm"] is None and out["tier1_abs_mm"] is None:
        raise RegimeError("regime has no gated band (p95_mm, max_mm, tier1_abs_mm all null); "
                          "refusing to grade -- a missing regime never falls back to a default (run-contract §12)")
    return out


def band_result(s: Mapping[str, Any], p95: float | None, mx: float | None) -> dict[str, Any] | None:
    """Compare stats to a band. Returns None when no band applies (reported only)."""
    if p95 is None and mx is None:
        return None
    if s.get("n", 0) == 0:
        return {"p95_band": p95, "max_band": mx, "pass": None, "note": "no points"}
    ok = True
    over: dict[str, float] = {}
    if p95 is not None and s["p95"] > p95:
        ok = False
        over["p95_over_by"] = s["p95"] - p95
    if mx is not None and s["max"] > mx:
        ok = False
        over["max_over_by"] = s["max"] - mx
    return {"p95_band": p95, "max_band": mx, "pass": ok, **over}


# --------------------------------------------------------------------------- transforms
def load_matrix(path: str | Path | None) -> np.ndarray:
    if path is None:
        return np.eye(4)
    p = Path(path)
    if p.suffix == ".npy":
        T = np.load(p)
    else:
        j = read_json(p)
        for k in ("matrix_4x4", "T1_original_stl_to_datum", "T", "matrix"):
            if k in j:
                T = np.asarray(j[k], float)
                break
        else:
            raise KeyError(f"{p}: no matrix_4x4 / T1_original_stl_to_datum key")
    T = np.asarray(T, float)
    if T.shape != (4, 4):
        raise ValueError(f"{p}: matrix is {T.shape}, expected 4x4")
    return T


def rot_angle_deg(R: np.ndarray) -> float:
    c = (np.trace(R[:3, :3]) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


# --------------------------------------------------------------------------- predicates
_RANGE_KEYS = ("x", "y", "z", "r", "abs_x", "abs_y", "abs_z", "nx", "ny", "nz", "abs_nz", "d")


def _features(P: np.ndarray, N: np.ndarray | None, d: np.ndarray | None) -> dict[str, np.ndarray]:
    f: dict[str, np.ndarray] = {"x": P[:, 0], "y": P[:, 1], "z": P[:, 2]}
    f["r"] = np.hypot(P[:, 0], P[:, 1])
    f["abs_x"], f["abs_y"], f["abs_z"] = np.abs(P[:, 0]), np.abs(P[:, 1]), np.abs(P[:, 2])
    f["theta_deg"] = (np.degrees(np.arctan2(P[:, 1], P[:, 0])) + 360.0) % 360.0
    if N is not None:
        f["nx"], f["ny"], f["nz"] = N[:, 0], N[:, 1], N[:, 2]
        f["abs_nz"] = np.abs(N[:, 2])
    if d is not None:
        f["d"] = d
    return f


def select(pred: Mapping[str, Any], P: np.ndarray, N: np.ndarray | None = None,
           d: np.ndarray | None = None) -> np.ndarray:
    """Evaluate a JSON predicate on points (datum frame).

    Grammar (all keys AND-ed):
      {"z": [lo, hi]}            half-open [lo, hi); null = unbounded. Same for x y r abs_x abs_y
                                 abs_z nx ny nz abs_nz d (d = deviation, when available)
      {"theta_deg": [a, b]}      angular window a->b counter-clockwise, wraps through 360
      {"any_of": [pred, ...]}    OR
      {"not": pred}              negation
      {"all": true}              every point
    """
    f = _features(P, N, d)
    m = np.ones(len(P), bool)
    for k, v in pred.items():
        if k in ("all", "comment"):
            continue
        if k == "any_of":
            sub = np.zeros(len(P), bool)
            for q in v:
                sub |= select(q, P, N, d)
            m &= sub
        elif k == "not":
            m &= ~select(v, P, N, d)
        elif k == "theta_deg":
            a, b = float(v[0]) % 360.0, float(v[1]) % 360.0
            t = f["theta_deg"]
            m &= ((t >= a) & (t < b)) if a <= b else ((t >= a) | (t < b))
        elif k in _RANGE_KEYS:
            if k not in f:
                raise KeyError(f"predicate key {k!r} needs normals/deviations that are not available here")
            lo, hi = v
            if lo is not None:
                m &= f[k] >= float(lo)
            if hi is not None:
                m &= f[k] < float(hi)
        else:
            raise KeyError(f"unknown predicate key {k!r}")
    return m


# --------------------------------------------------------------------------- meshes
def load_mesh(path: str | Path, process: bool = True):  # -> trimesh.Trimesh
    import trimesh

    m = trimesh.load_mesh(str(path), process=process)
    if isinstance(m, trimesh.Scene):
        m = m.dump(concatenate=True)
    return m


def step_to_mesh(step: str | Path, out_stl: str | Path, tolerance: float = 0.005,
                 angular_tolerance: float = 0.05):
    """Tessellate a STEP with the QA's own call (B02 q10_solid_tess_tier1.py:52 used 0.005 / 0.05)."""
    from build123d import export_stl, import_step

    shape = import_step(str(step))
    export_stl(shape, str(out_stl), tolerance=tolerance, angular_tolerance=angular_tolerance)
    return load_mesh(out_stl)
