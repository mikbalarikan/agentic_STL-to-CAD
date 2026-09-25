#!/usr/bin/env python3
"""Generate tests/fixture_run/qa/gate.json (and _it1_SUPERSEDED/qa/gate.json) the way a real run
gets one: write the QA block files verify's own tools produce (regime.json, hash_freeze.json,
step_check.json, datum_audit.json, tier1.json, registration.json, deviation.json, review.json,
overlay1.json) in verify's real schema, then call stl-re-verify/scripts/verdict.py's own
`assemble()` and `render()` -- unmodified -- to compose gate.json and VERDICT.md.

This exists because make_readme.py must consume verify's REAL gate shape (review D1), and a
hand-written gate.json fixture cannot be trusted to match it. The block contents below are
synthetic but schema-accurate (checked against sim_caliper.py, deviation_gate.py, tier2_icp.py,
step_check.py, datum_audit.py and verdict.py itself, see reviews/stl-re-deliver.md D1).

Usage: python3 gen_gate.py            # regenerates both qa/ folders under tests/fixture_run/
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("SOURCE_DATE_EPOCH", "0")
os.environ.setdefault("PYTHONHASHSEED", "0")

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture_run"
VERIFY_SCRIPTS = HERE.parent.parent / "stl-re-verify" / "scripts"
sys.path.insert(0, str(VERIFY_SCRIPTS))
import verdict as V  # noqa: E402  (the real stl-re-verify/scripts/verdict.py)
from _common import write_json  # noqa: E402  (verify's own header()/write_json())

REGIME = {
    "schema": "stl-re/regime@1", "tool": "intake.py", "tool_version": "fixture",
    "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
    "name": "RE_SPEC", "source": "baseline/oomwoo-re-pipeline/RE_SPEC.md:170-175",
    "bands": {"p95_mm": 1.6, "max_mm": 4.0, "tier1_abs_mm": 0.15, "interface_max_mm": 0.8},
    "why": "fixture: calipers exist for F01/F02 (run-contract.md section 12 canonical band keys)",
}

HASH_FREEZE = {
    "schema": "stl-re/hash_freeze@1", "tool": "step_check.py", "tool_version": "fixture",
    "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
    # placeholder: tests/run_fixture_test.py overwrites gate.json#hash_frozen at test time with the
    # real sha256 of the STEPs it just built (a STEP's hash is only known after the build runs).
    "before": {"build/fixture_part_datum.step": "0" * 64, "build/fixture_part.step": "0" * 64},
    "after": {"build/fixture_part_datum.step": "0" * 64, "build/fixture_part.step": "0" * 64},
    "unchanged": True,
}


def _validity(volume: float) -> dict[str, Any]:
    return {
        "validity": {"counts": {"solid": 1, "shell": 1, "face": 7, "edge": 15, "vertex": 10},
                     "brepcheck_valid": True, "shells_closed": [True], "naked_edges": 0,
                     "volume_mm3": volume, "area_mm2": 1200.0, "bbox": [[-20.0, -15.0, -2.5], [20.0, 15.0, 2.5]],
                     "single_valid_closed_solid": True},
        "tessellation": {"tolerance": 0.005, "angular_tolerance": 0.05, "tris": 400, "watertight": True,
                         "winding": True, "euler": 2, "components": 1, "degenerate_faces": 0,
                         "volume_mm3": volume, "volume_vs_brep_mm3": 0.0},
        "surface_census": {"faces": 7, "by_type": {"plane": {"count": 6, "area_mm2": 1150.0},
                                                    "cylinder": {"count": 1, "area_mm2": 50.0}},
                           "analytic_area_share": 1.0, "gated": False,
                           "note": "reported, not gated (QUESTIONS.md Q3)"},
    }


def step_check(volume: float = 5975.0) -> dict[str, Any]:
    steps = {"build/fixture_part_datum.step": _validity(volume),
             "build/fixture_part.step": _validity(volume)}
    return {"schema": "stl-re/step_check@1", "tool": "step_check.py", "tool_version": "fixture",
            "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
            "steps": steps, "all_single_valid_closed_solid": True}


DATUM_AUDIT = {
    "schema": "stl-re/datum_audit@1", "tool": "datum_audit.py", "tool_version": "fixture",
    "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
    "independence": "builder matrix used only to select named regions; all fits are QA code on raw scan",
    "primary": {"type": "plane", "method": "region SVD", "faces": 120, "fit_rms_mm": 0.004, "fit_max_mm": 0.01},
    "angle_deg": 0.05, "axis_angle_deg": 0.05, "clock_audited": False,
    "origin_offset_mm": 0.02, "origin_offset_vec_mm": [0.01, 0.01, 0.0],
    "point_disagreement_mean_mm": 0.01, "point_disagreement_p95_mm": 0.03, "point_disagreement_max_mm": 0.05,
    "reference_band": "≤0.3° / ≤0.15 mm (RE_SPEC.md:241)",
    "reference": {"angle_deg": 0.3, "origin_offset_mm": 0.15, "source": "baseline/oomwoo-re-pipeline/RE_SPEC.md:241"},
    "within_reference": True, "blocking": False,
    "note": "REPORT-ONLY (QUESTIONS.md Q2).",
}


def tier1(f01_pass: bool = True) -> dict[str, Any]:
    delta_x = -0.02 if f01_pass else 0.55
    dims = {
        "F01": {"name": "plate_x", "caliper": 40.02 if f01_pass else 40.55, "cad": 40.0,
                "source": "caliper", "gated": True, "uncertainty_mm": 0.02, "method": "jaw",
                "detail": {"value": 40.0, "reduce": "max"}, "delta": delta_x, "pass": f01_pass,
                "grey_zone": False},
        "F02": {"name": "plate_t", "caliper": 5.01, "cad": 5.0, "source": "caliper", "gated": True,
                "uncertainty_mm": 0.02, "method": "jaw", "detail": {"value": 5.0, "reduce": "max"},
                "delta": -0.01, "pass": True, "grey_zone": False},
        "F03": {"name": "bore_d", "caliper": None, "cad": 8.0, "source": "assumed", "gated": False,
                "uncertainty_mm": None, "method": "bore", "detail": {"value": 8.0}, "delta": None, "pass": None},
    }
    worst = max(abs(dims["F01"]["delta"]), abs(dims["F02"]["delta"]))
    return {"schema": "stl-re/tier1@1", "tool": "sim_caliper.py", "tool_version": "fixture",
            "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
            "band_abs_mm": 0.15, "band_source": "baseline/oomwoo-re-pipeline/RE_SPEC.md:170",
            "tessellation": {"tolerance": 0.005, "angular_tolerance": 0.05},
            "dims": dims, "worst_gated_abs_delta": worst,
            "coverage": {"gated": 2, "requested_total": 3, "absent": ["F03 bore_d: not observable on the scan"]},
            "all_pass": f01_pass}


REGISTRATION = {
    "schema": "stl-re/registration@1", "tool": "tier2_icp.py", "tool_version": "fixture",
    "inputs": {}, "seed": 11, "created": "1970-01-01T00:00:00+00:00",
    "method": "point-to-point ICP, CAD samples -> scan samples, masked correspondences (B02 q20_tier2.py)",
    "scan_kind": "full", "iterations": 12, "max_iterations": 60, "converged": True,
    "delta_deg": 0.01, "delta_mm": 0.004, "max_point_move_mm": 0.05, "final_kept_fraction": 0.97,
    "T_refine": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "T_refine_meaning": "maps datum-frame CAD onto the aligned scan; deviation_gate applies its inverse "
                        "to the scan. QA-only: never written back to alignment.json (CHK-CIRCULAR).",
    "trace_tail": [{"it": 11, "step": 1e-7, "rot_deg": 0.0001, "trans_mm": 0.0001,
                    "kept_fraction": 0.97, "mean_d_kept": 0.03}],
    "reference_masks_removed": [],
    "params": {"ns": 3000000, "scan_seed": 11, "nc": 300000, "cad_seed": 13, "normal_deg": 70.0,
              "boundary_mm": 0.8, "max_corr_mm": 3.0, "max_iter": 60, "tol": 1e-6},
    "notes": ["welded: 20000 verts / 40000 faces"],
}


def _stats(n: int, rms: float, p50: float, p95: float, p99: float, mx: float) -> dict[str, Any]:
    return {"n": n, "rms": rms, "mean": rms, "p50": p50, "p95": p95, "p99": p99, "max": mx}


def deviation(band_ok: bool = True) -> dict[str, Any]:
    s2c = _stats(20000, 0.041, 0.03, 0.088, 0.12, 0.31 if band_ok else 4.2)
    c2s = _stats(20000, 0.9, 0.02, 3.9, 4.0, 4.0)
    c2s_obs = _stats(18000, 0.05, 0.02, 0.09, 0.14, 0.29)
    zone_stats = _stats(900, 0.05, 0.03, 0.1, 0.2, 0.4)
    return {
        "schema": "stl-re/deviation@1", "tool": "deviation_gate.py", "tool_version": "fixture",
        "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
        "scan": {"path": "input/scan.stl", "sha256": "0" * 64, "kind": "full", "full_res": True,
                 "vertices": 20000, "faces": 40000},
        "cad": {"path": "build/fixture_part_datum.step", "sha256": "0" * 64, "tessellated_by_qa": True,
                "tessellation": {"tolerance": 0.005, "angular_tolerance": 0.05}, "faces": 400},
        "frame": "datum",
        "registration": {"method": "trimmed ICP", "iterations": 12, "max_iterations": 60, "converged": True,
                         "delta_deg": 0.01, "delta_mm": 0.004, "file": "qa/registration.json"},
        "sampling": {"s2c_points": "all", "s2c_seed": 0, "c2s_samples": 300000, "c2s_seed": 2, "k": 8,
                    "n_samp": 3000000, "dist_seed": 0, "vertex_candidates": False,
                    "method": "KD candidates -> exact point-to-triangle (OD gate.py:8-17)"},
        "regime": {"name": "RE_SPEC", "source": REGIME["source"], "bands": REGIME["bands"]},
        "scan_to_cad": s2c, "cad_to_scan": c2s,
        "scan_to_cad_masked": s2c, "cad_to_scan_masked": c2s,
        "unmasked": {"scan_to_cad": s2c, "cad_to_scan": c2s},
        "masked_fraction": {"scan_to_cad": 0.0, "cad_to_scan": 0.0},
        "bands": {"scan_to_cad": {"unmasked": None, "masked": None}, "cad_to_scan": {"unmasked": None, "masked": None}},
        "masks": [],
        "cad_to_scan_observable": c2s_obs, "unobservable_fraction": 0.1,
        "observability": {"note": "fixture"},
        "zones": {
            "bore_wall": {
                "kind": "functional_interface", "note": "bore wall vs mating shaft", "band": [None, 0.8],
                "scan_to_cad": {"unmasked": zone_stats, "masked": zone_stats, "masked_fraction": 0.0,
                                "band_unmasked": None, "band_masked": None},
                "cad_to_scan": {"unmasked": zone_stats, "masked": zone_stats, "masked_fraction": 0.0,
                                "band_unmasked": None, "band_masked": None},
            },
        },
        "sensitivity": [],
        "mask_dependent_passes": [],
        "over_band_clusters": {
            "scan_to_cad": {"threshold_mm": 0.8, "eps_mm": 1.0, "min_pts": 20, "n_over": 0,
                           "fraction_over": 0.0, "clusters": [], "n_clusters_ge_min": 0, "points_in_small_clusters": 0},
            "cad_to_scan": {"threshold_mm": 0.8, "eps_mm": 1.0, "min_pts": 20, "n_over": 0,
                           "fraction_over": 0.0, "clusters": [], "n_clusters_ge_min": 0, "points_in_small_clusters": 0},
            "reading": "scan_to_cad clusters = scan material the CAD lacks (missing feature or artefact); "
                      "cad_to_scan clusters = CAD material with no scan (invented or unobservable)",
        },
        "gate_valid": True, "gate_invalid_reasons": [], "label": "OFFICIAL (full-res)",
    }


def review(verdict_word: str, tier1_ok: bool = True) -> dict[str, Any]:
    checks = {c: {"ran": True, "result": "pass", "note": "fixture"}
             for c in ("CHK-CIRCULAR", "CHK-LIKE4LIKE", "CHK-INDEP", "CHK-FILLET", "CHK-PATCHWORK")}
    checks["CHK-ENUM"] = ({"ran": True, "result": "pass", "note": "fixture: matches photo"} if tier1_ok else
                          {"ran": True, "result": "finding", "note": "fixture: bore too small vs photo"})
    if not tier1_ok:
        checks["CHK-ACHIEVABLE"] = {"ran": True, "result": "finding",
                                    "note": "fixture: F01 plate_x miss is a caliper reading, not an "
                                            "unachievable geometry"}
    d: dict[str, Any] = {
        "schema": "stl-re/review@1", "tool": "review", "tool_version": "fixture",
        "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
        "verdict": verdict_word, "photos": [], "checks": checks,
        "independence": "verify ran in a fresh agent (CHK-INDEP)",
        "cluster_explanations": {},
        "claim_boundary": "Not fit for any physical use; the bore is not calipered. Fit for "
                          "pipeline testing of stl-re-deliver only.",
        "miss_explanations": [],
    }
    if verdict_word == "APPROVED_WITH_LIMITATIONS":
        d["limitations"] = [{"id": "L1",
                             "text": "Bore diameter is assumed; the scan does not resolve it.",
                             "rerun_trigger": "One caliper reading of the bore diameter; a value "
                                              "different from the model triggers a re-run.",
                             "evidence": "measure/params.json#bore_d"}]
    else:
        d["limitations"] = []
    return d


OVERLAY = {"schema": "stl-re/overlay@1", "tool": "overlay.py", "tool_version": "fixture",
          "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00",
          "panels": ["top", "side"], "empty_scan_panels": []}


def build_qa(qa: Path, *, verdict_word: str, tier1_ok: bool) -> None:
    qa.mkdir(parents=True, exist_ok=True)
    write_json(qa / "regime.json", REGIME)
    write_json(qa / "hash_freeze.json", HASH_FREEZE)
    write_json(qa / "step_check.json", step_check())
    write_json(qa / "datum_audit.json", DATUM_AUDIT)
    write_json(qa / "tier1.json", tier1(f01_pass=tier1_ok))
    write_json(qa / "registration.json", REGISTRATION)
    write_json(qa / "deviation.json", deviation(band_ok=True))
    write_json(qa / "review.json", review(verdict_word, tier1_ok=tier1_ok))
    write_json(qa / "overlay1.json", OVERLAY)
    for stale in ("gate.json", "VERDICT.md"):
        (qa / stale).unlink(missing_ok=True)
    rc = V.assemble(qa)
    gate = json.loads((qa / "gate.json").read_text())
    if gate.get("verdict") != verdict_word or gate.get("errors"):
        raise SystemExit(f"{qa}: assemble did not produce a clean {verdict_word}: "
                         f"verdict={gate.get('verdict')} errors={gate.get('errors')}")
    rc2 = V.render(qa)
    if rc or rc2:
        raise SystemExit(f"{qa}: verdict.py assemble/render exited non-zero")
    print(f"{qa}: verdict {gate['verdict']} (assembled by the real stl-re-verify/scripts/verdict.py)")


def main() -> None:
    build_qa(FIXTURE / "qa", verdict_word="APPROVED_WITH_LIMITATIONS", tier1_ok=True)
    build_qa(FIXTURE / "_it1_SUPERSEDED" / "qa", verdict_word="REVISE", tier1_ok=False)


if __name__ == "__main__":
    main()
