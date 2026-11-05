#!/usr/bin/env python3
"""Regression selftests for stl-re-measure-intent (review round 1, harnesses/v0/reviews/stl-re-measure-intent.md).

Covers:
  - B1: sim_caliper.py inside-jaw mode on an OPEN scan section (bore), reporting real
    angular coverage instead of assuming full coverage. B02 F03 must no longer be struck.
  - B2: sim_caliper.py CHK-ACHIEVABLE per-scan `--scan-offset` (measured, never a constant),
    with the third UNPROVEN state. B02 F06 must be UNPROVEN (not STRUCK) within the offset,
    and still STRIKE beyond it. No offset given -> UNPROVEN, never STRIKE.
  - M1-M4: param_table.py refuses the C9/C10/C11/§11 violations it is meant to refuse, and
    handles list values element-wise + mean-of-n.
  - A rerun of the pattern_count M02 (30/17) and P03 (8 kidneys) checks from validation.md,
    to show the sim_caliper/param_table changes did not regress the untouched script.

Needs the golden-examples/ fixtures (read-only) and build123d (to tessellate the M02 STEP).
Exit 0 = every case passed. Never modifies golden-examples/ or baseline/.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
# Repo root = first ancestor holding golden-examples/ (layout moved to harnesses/v0/skills/).
REPO = next((p for p in SKILL.parents if (p / "golden-examples").is_dir()), SKILL.parent.parent)
GOLD = REPO / "golden-examples"

B02_MESH = GOLD / "OOM-B02_side-brush-3-arm/2_mesh_cleaned/OOM-B02.stl"
B02_ALIGN = GOLD / "OOM-B02_side-brush-3-arm/2_mesh_cleaned/alignment.json"
M02_STEP = GOLD / "M02-02-03_watertight-design-intent/M02-02-03_WATERTIGHT_SOLID.step"
P03_MESH = GOLD / "OOM-P03_mop-pad-bracket/2_mesh_cleaned/OOM-P03_scan_decimated.stl"
P03_ALIGN = GOLD / "OOM-P03_mop-pad-bracket/2_mesh_cleaned/alignment.json"

PASS = 0
FAIL = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"PASS  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


def sim_caliper(tmp: Path, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    out = tmp / f"cal_{len(list(tmp.glob('cal_*.json')))}.json"
    cp = run([str(SCRIPTS / "sim_caliper.py"), *args, "--out", str(out)])
    doc = json.loads(out.read_text()) if out.exists() else {}
    return cp, doc


def test_b1_inside_jaw_bore(tmp: Path) -> None:
    """B1: F03 cup bore (20.75) on the B02 full-res scan must no longer be struck."""
    cp, doc = sim_caliper(tmp, "--mesh", str(B02_MESH), "--alignment", str(B02_ALIGN),
                           "--z", "1.0", "--mode", "inside", "--r-band", "9.5,11",
                           "--reading", "20.75", "--reading-unc", "0.1", "--name", "F03_bore")
    check("B1: sim_caliper inside-jaw runs on B02 full-res scan", cp.returncode == 0, cp.stderr)
    readings = doc.get("result", {}).get("readings", [])
    check("B1: F03=20.75 reported", len(readings) == 1, str(readings))
    if readings:
        r = readings[0]
        check("B1: F03 is achievable (not struck)", r.get("achievable") is True, str(r))
        check("B1: F03 state is PASS", r.get("state") == "PASS", str(r))
    cov = doc.get("result", {}).get("angular_coverage")
    check("B1: reports real (partial) angular coverage, not 1.0", cov is not None and cov < 1.0, str(cov))


def test_b1_inside_requires_rband(tmp: Path) -> None:
    cp, _ = sim_caliper(tmp, "--mesh", str(B02_MESH), "--alignment", str(B02_ALIGN),
                         "--z", "1.0", "--mode", "inside", "--reading", "20.75", "--name", "no_rband")
    check("B1: --mode inside without --r-band refuses (no picking an arbitrary polyline)",
          cp.returncode != 0, cp.stdout + cp.stderr)


def test_b2_outside_window_unchanged(tmp: Path) -> None:
    """Regression: the B02 outside-jaw scan window from validation.md must be unchanged."""
    cp, doc = sim_caliper(tmp, "--mesh", str(B02_MESH), "--alignment", str(B02_ALIGN),
                           "--z", "1.0", "--mode", "outside", "--r-band", "12,14",
                           "--reading", "24.84", "--reading-unc", "0.1", "--name", "F06_window")
    check("B2: outside-jaw run OK", cp.returncode == 0, cp.stderr)
    res = doc.get("result", {})
    check("B2: window_min matches validation.md (24.988)", abs(res.get("window_min", 0) - 24.988) < 1e-3,
          str(res.get("window_min")))
    check("B2: window_max matches validation.md (27.246)", abs(res.get("window_max", 0) - 27.246) < 1e-3,
          str(res.get("window_max")))


def test_b2_no_offset_is_unproven(tmp: Path) -> None:
    """No --scan-offset given: a below-window reading is UNPROVEN, never STRUCK (B2)."""
    cp, doc = sim_caliper(tmp, "--mesh", str(B02_MESH), "--alignment", str(B02_ALIGN),
                           "--z", "1.0", "--mode", "outside", "--r-band", "12,14",
                           "--reading", "24.84", "--reading-unc", "0.1", "--name", "F06_no_offset")
    r = doc.get("result", {}).get("readings", [{}])[0]
    check("B2: F06 with unknown offset is UNPROVEN", r.get("state") == "UNPROVEN", str(r))
    check("B2: F06 with unknown offset is not struck", r.get("achievable") is not False, str(r))


def test_b2_offset_unproven_within(tmp: Path) -> None:
    """d = 0.56 mm (B02 F10: scan mean 5.89 - caliper 5.33, MEASUREMENTS.md:61 / PARAM_TABLE.md:41).
    F06's margin (0.148, validation.md) is below that offset -> UNPROVEN, not struck (B2)."""
    cp, doc = sim_caliper(tmp, "--mesh", str(B02_MESH), "--alignment", str(B02_ALIGN),
                           "--z", "1.0", "--mode", "outside", "--r-band", "12,14",
                           "--reading", "24.84", "--reading-unc", "0.1", "--scan-offset", "0.56",
                           "--name", "F06_offset")
    r = doc.get("result", {}).get("readings", [{}])[0]
    check("B2: F06 within the measured offset is UNPROVEN", r.get("state") == "UNPROVEN", str(r))
    check("B2: F06 within the measured offset is not struck", r.get("achievable") is not False, str(r))


def test_b2_offset_strike_beyond(tmp: Path) -> None:
    """A miss clearly beyond the measured offset still STRIKEs (B2: 'only a clear miss beyond
    the offset is struck')."""
    cp, doc = sim_caliper(tmp, "--mesh", str(B02_MESH), "--alignment", str(B02_ALIGN),
                           "--z", "1.0", "--mode", "outside", "--r-band", "12,14",
                           "--reading", "23.0", "--reading-unc", "0.1", "--scan-offset", "0.56",
                           "--name", "F06_beyond_offset")
    r = doc.get("result", {}).get("readings", [{}])[0]
    check("B2: a miss beyond the offset still STRIKEs", r.get("state") == "STRIKE", str(r))
    check("B2: struck reading has achievable=False", r.get("achievable") is False, str(r))


def pt_validate(tmp: Path, doc: dict, name: str) -> subprocess.CompletedProcess[str]:
    p = tmp / f"{name}.json"
    p.write_text(json.dumps(doc))
    return run([str(SCRIPTS / "param_table.py"), str(p), "--out", str(tmp / f"{name}_TABLE.md")])


CHECKS_OK = {"CHK-COUNT": {"ran": True, "result": "pass"}, "CHK-ACHIEVABLE": {"ran": True, "result": "pass"},
             "CHK-CLUSTER": {"ran": True, "result": "pass"}, "CHK-FRAME": {"ran": True, "result": "pass"}}


def row(**kw) -> dict:
    base = {"unit": "mm", "estimator": "test", "uncertainty_mm": 0.05, "evidence": "f.json", "critical": False}
    base.update(kw)
    return base


def test_m1_symmetry_and_critical_scan_bypass(tmp: Path) -> None:
    """M1: a critical, uncalipered value must not be moved by `symmetry` beyond its
    uncertainty (B02 hex AF 7.358, VERDICT.md:28-30)."""
    doc = {"part": "t", "frame": "f", "scan_noise_mm": 0.05,
           "params": {"HEX_SYM": row(value=7.0, measured=7.358, rule="symmetry", source="scan",
                                       critical=True, uncertainty_mm=0.037)},
           "checks": CHECKS_OK}
    cp = pt_validate(tmp, doc, "m1a")
    check("M1: symmetry snap on a critical uncalipered scan value is refused", cp.returncode == 1, cp.stdout)
    check("M1: refusal names the critical/noise breach", "beyond scan" in cp.stdout or "scatter_mm" in cp.stdout,
          cp.stdout)


def test_m1_scan_assumed_refused(tmp: Path) -> None:
    """M1/M4: a `scan` source with an `assumed` rule must be refused (C11)."""
    doc = {"part": "t", "frame": "f", "scan_noise_mm": 0.05,
           "params": {"SCAN_ASSUMED": row(value=5.0, measured=None, rule="assumed", source="scan",
                                            uncertainty_mm=0.5)},
           "checks": CHECKS_OK}
    cp = pt_validate(tmp, doc, "m1b")
    check("M1: scan source + assumed rule is refused", cp.returncode == 1, cp.stdout)


def test_m2_list_elementwise(tmp: Path) -> None:
    """M2: list values (run-contract §11) are checked element-wise, never by their mean."""
    doc = {"part": "t", "frame": "f", "scan_noise_mm": 0.05,
           "params": {
               "LIST_ROUND": row(value=[0, 100], measured=[49, 51], rule="round-within-noise", source="scan"),
               "LIST_KEEP_BAD": row(value=[10, 20, 30], measured=[60, 150, -60], rule="keep-measured", source="scan"),
               "LIST_SNAP": row(value=[10.0, 20.0], measured=[10.05, 20.5], rule="std-size-snap",
                                 source="caliper", uncertainty_mm=0.02),
           }, "checks": CHECKS_OK}
    cp = pt_validate(tmp, doc, "m2")
    check("M2: mean-of-list bypass (round-within-noise) is refused", cp.returncode == 1, cp.stdout)
    check("M2: mean-of-list bypass (keep-measured) is refused",
          "LIST_KEEP_BAD" in cp.stdout, cp.stdout)
    check("M2: list value under std-size-snap does not crash and flags the bad element",
          "[LIST_SNAP][1]" in cp.stdout, cp.stdout)


def test_m2_list_valid_case(tmp: Path) -> None:
    """A legitimate per-instance list (DRM legs 60/150/-60) must still validate cleanly."""
    doc = {"part": "t", "frame": "f", "scan_noise_mm": 0.05,
           "params": {"LEG_THETA": row(value=[60.0, 150.0, -60.0], measured=[60.0, 150.0, -60.0],
                                         rule="keep-measured", source="scan", unit="deg", frame="datum")},
           "checks": CHECKS_OK}
    cp = pt_validate(tmp, doc, "m2valid")
    check("M2: a valid per-instance list value passes", cp.returncode == 0, cp.stdout)


def test_m3_mean_of_n(tmp: Path) -> None:
    """M3: `mean-of-n` must be checked (P03 hex AF 13.96/13.92/13.97 -> 13.95, intent-rules.md §1)."""
    doc_bad = {"part": "t", "frame": "f", "scan_noise_mm": 0.05,
               "params": {"MEAN_BAD": row(value=14.5, measured=[13.96, 13.92, 13.97], rule="mean-of-n",
                                            source="caliper", uncertainty_mm=0.02)},
               "checks": CHECKS_OK}
    cp = pt_validate(tmp, doc_bad, "m3bad")
    check("M3: mean-of-n value that doesn't match the mean is refused", cp.returncode == 1, cp.stdout)

    doc_good = {"part": "t", "frame": "f", "scan_noise_mm": 0.05,
                "params": {"MEAN_GOOD": row(value=13.95, measured=[13.96, 13.92, 13.97], rule="mean-of-n",
                                              source="caliper", uncertainty_mm=0.02)},
                "checks": CHECKS_OK}
    cp2 = pt_validate(tmp, doc_good, "m3good")
    check("M3: mean-of-n value matching the mean passes", cp2.returncode == 0, cp2.stdout)


def test_m4_c11_tagging(tmp: Path) -> None:
    """M4: C11 tagging enforced both ways: assumed/photo-inferred rule needs an unmeasured
    source, and an unmeasured source needs measured: null."""
    doc = {"part": "t", "frame": "f", "scan_noise_mm": 0.05,
           "params": {
               "INFERRED_WITH_MEAS": row(value=5.5, measured=5.5, rule="keep-measured",
                                           source="photo-inferred", uncertainty_mm=0.5),
           }, "checks": CHECKS_OK}
    cp = pt_validate(tmp, doc, "m4")
    check("M4: photo-inferred source with non-null measured is refused", cp.returncode == 1, cp.stdout)


def test_pattern_count_regression(tmp: Path) -> None:
    """Rerun the M02 (30/17) and P03 (8 kidneys) pattern_count checks from validation.md:
    pattern_count.py is untouched by this round, so these must reproduce exactly."""
    try:
        from build123d import export_stl, import_step
    except Exception as exc:  # pragma: no cover
        check("pattern_count regression: build123d available to tessellate M02", False, str(exc))
        return
    m02_stl = tmp / "M02.stl"
    export_stl(import_step(str(M02_STEP)), str(m02_stl), tolerance=0.005)

    def count(*args: str) -> dict:
        out = tmp / f"pc_{len(list(tmp.glob('pc_*.json')))}.json"
        cp = run([str(SCRIPTS / "pattern_count.py"), *args, "--out", str(out)])
        return json.loads(out.read_text()) if out.exists() else {"error": cp.stderr}

    big = count("--mesh", str(m02_stl), "--stations", "0.5,1.5,2.5", "--orders", "10,40",
                "--tol", "0.002")
    check("pattern_count: M02 big gear = 30", big.get("count") == 30, str(big.get("count")))
    small = count("--mesh", str(m02_stl), "--stations", "3.5,6.5,9.5", "--orders", "10,40",
                  "--tol", "0.002")
    check("pattern_count: M02 small gear = 17", small.get("count") == 17, str(small.get("count")))

    kidneys = count("--mesh", str(P03_MESH), "--alignment", str(P03_ALIGN), "--signal", "mass",
                    "--stations", "0.5,1.4,2.2", "--z-half", "0.3", "--r-band", "35,44",
                    "--rays", "3600")
    check("pattern_count: P03 kidneys = 8", kidneys.get("count") == 8, str(kidneys.get("count")))


def main() -> None:
    for p, label in ((B02_MESH, "B02 mesh"), (B02_ALIGN, "B02 alignment"),
                      (M02_STEP, "M02 STEP"), (P03_MESH, "P03 mesh"), (P03_ALIGN, "P03 alignment")):
        if not p.is_file():
            sys.exit(f"fixture missing: {label} not found at {p}")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        test_b1_inside_jaw_bore(tmp)
        test_b1_inside_requires_rband(tmp)
        test_b2_outside_window_unchanged(tmp)
        test_b2_no_offset_is_unproven(tmp)
        test_b2_offset_unproven_within(tmp)
        test_b2_offset_strike_beyond(tmp)
        test_m1_symmetry_and_critical_scan_bypass(tmp)
        test_m1_scan_assumed_refused(tmp)
        test_m2_list_elementwise(tmp)
        test_m2_list_valid_case(tmp)
        test_m3_mean_of_n(tmp)
        test_m4_c11_tagging(tmp)
        test_pattern_count_regression(tmp)

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
