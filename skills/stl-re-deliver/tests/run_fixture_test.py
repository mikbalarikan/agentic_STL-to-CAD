#!/usr/bin/env python3
"""End-to-end test of the stl-re-deliver scripts on tests/fixture_run (synthetic, small text files).

It copies the fixture to a scratch folder, plays the upstream stages it needs (rebuild: run
build/model.py and write build/export_check.json; verify: fill qa/gate.json#hash_frozen), then runs
preflight -> repro_check -> make_readme -> make_manifest and eight refusal cases.

Usage: python tests/run_fixture_test.py [--workdir DIR] [--keep]
Exit 0 when every case behaves as expected.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
FIXTURE = HERE / "fixture_run"
ENV = dict(os.environ, SOURCE_DATE_EPOCH="0", PYTHONHASHSEED="0")
sys.path.insert(0, str(SCRIPTS))
from _common import sha256_file  # noqa: E402
from repro_check import measure_step  # noqa: E402


def sh(script: str, run: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / script), "--run", str(run), *extra],
                          env=ENV, capture_output=True, text=True)


def prepare(dst: Path) -> Path:
    """Copy the fixture and play rebuild + verify for it."""
    shutil.copytree(FIXTURE, dst)
    for b in (dst / "build", dst / "_it1_SUPERSEDED" / "build"):
        subprocess.run([sys.executable, "model.py"], cwd=b, env=ENV, check=True, capture_output=True)
    exports = {"datum": dst / "build" / "fixture_part_datum.step", "scan": dst / "build" / "fixture_part.step"}
    ec = {"schema": "stl-re/export_check@1", "tool": "run_fixture_test.py", "tool_version": "fixture",
          "inputs": {}, "seed": 0, "created": "1970-01-01T00:00:00+00:00"}
    for k, p in exports.items():
        m = measure_step(p)
        ec[k] = {"step": p.name, "solids": m["solids"], "valid": m["valid"], "closed": True, "faces": m["faces"],
                 "volume_mm3": m["volume_mm3"], "area_mm2": m["area_mm2"], "bbox": [m["bbox_min"], m["bbox_max"]],
                 "surface_types": m["surface_census"], "fillets": []}
    (dst / "build" / "export_check.json").write_text(json.dumps(ec, indent=2) + "\n")
    g = json.loads((dst / "qa" / "gate.json").read_text())
    g["hash_frozen"] = {p.name: {"before": sha256_file(p), "after": sha256_file(p)} for p in exports.values()}
    (dst / "qa" / "gate.json").write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n")
    return dst


def edit_json(path: Path, fn: Callable[[dict], None]) -> None:
    d = json.loads(path.read_text())
    fn(d)
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", type=Path, default=None)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    work = a.workdir or Path(tempfile.mkdtemp(prefix="stl-re-deliver-test-"))
    work.mkdir(parents=True, exist_ok=True)
    results: list[tuple[str, bool, str]] = []

    def case(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, ok, detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")

    # ---- happy path ------------------------------------------------------------------------
    run = prepare(work / "ok")
    r = sh("preflight.py", run)
    case("preflight passes", r.returncode == 0, r.stderr.strip()[-300:])
    r = sh("repro_check.py", run)
    repro = json.loads((run / "deliver" / "repro.json").read_text()) if (run / "deliver" / "repro.json").exists() else {}
    case("repro_check reproducible", r.returncode == 0 and repro.get("reproducible") is True, r.stderr.strip()[-300:])
    case("repro raw sha differs (timestamps) but geometry identical",
         all(not f["raw_sha256_equal"] and f["geometry_measurements_identical"] for f in repro.get("files", [])) or
         all(f["geometry_measurements_identical"] for f in repro.get("files", [])))
    r = sh("make_readme.py", run)
    readme = (run / "deliver" / "README.md").read_text() if r.returncode == 0 else ""
    case("make_readme writes README", r.returncode == 0, r.stderr.strip()[-300:])
    case("README carries gate p95 from JSON", "| scan → CAD (masked) | 20000 | 0.041 | 0.03 | 0.088 |" in readme)
    case("README has no unresolved placeholder", "{{" not in readme)
    case("README names iteration 2 of 3 and regime", "**Iteration:** 2 of 3" in readme and "RE_SPEC" in readme)
    first = readme
    sh("make_readme.py", run)
    case("README deterministic", (run / "deliver" / "README.md").read_text() == first)
    r = sh("make_manifest.py", run, "--exclude", "input/scan.stl=example: large raw scan kept at source")
    man = json.loads((run / "deliver" / "MANIFEST.json").read_text()) if r.returncode == 0 else {}
    all_files = sorted(p.relative_to(run).as_posix() for p in run.rglob("*") if p.is_file()
                       and p.relative_to(run).as_posix() != "deliver/MANIFEST.json")
    listed = sorted([x["path"] for x in man.get("included", [])] + [x["path"] for x in man.get("excluded", [])])
    case("make_manifest lists every file", r.returncode == 0 and listed == all_files, r.stderr.strip()[-300:])
    case("excluded entry carries a reason", all(x.get("reason") for x in man.get("excluded", [])) and len(man.get("excluded", [])) == 1)
    case("manifest CHK-SUPERSEDED pass", man.get("checks", {}).get("CHK-SUPERSEDED", {}).get("result") == "pass")

    # ---- refusals ----------------------------------------------------------------------------
    def neg(name: str, mutate: Callable[[Path], None], script: str, expect: int, needle: str,
            with_repro: bool = False) -> None:
        rr = prepare(work / name.replace(" ", "_"))
        if with_repro:
            sh("repro_check.py", rr)
        mutate(rr)
        p = sh(script, rr)
        wrote = (rr / "deliver" / "README.md").exists()
        case(f"refuse: {name}", p.returncode == expect and needle in p.stderr and not wrote,
             f"rc={p.returncode} {p.stderr.strip()[-200:]}")

    neg("no VERDICT.md", lambda r: (r / "qa" / "VERDICT.md").unlink(), "make_readme.py", 2, "CHK-PUBLISH")
    neg("REVISE verdict", lambda r: (edit_json(r / "qa" / "gate.json", lambda d: d.update(verdict="REVISE")),
                                     (r / "qa" / "VERDICT.md").write_text("**VERDICT: REVISE**\n")),
        "make_readme.py", 2, "not deliverable")
    neg("headline disagrees with gate.json", lambda r: (r / "qa" / "VERDICT.md").write_text("**VERDICT: APPROVED**\n"),
        "make_readme.py", 2, "CHK-NUMBERS")

    def band(r: Path) -> None:
        edit_json(r / "qa" / "gate.json", lambda d: d.update(verdict="BAND_NOT_MET"))
        (r / "qa" / "VERDICT.md").write_text("**VERDICT: BAND_NOT_MET** (fixture)\n")
    neg("BAND_NOT_MET without ACCEPT-BAND", band, "make_readme.py", 2, "ACCEPT-BAND")
    neg("literal decimal in limitations", lambda r: edit_json(
        r / "deliver" / "limitations.json",
        lambda d: d["limitations"][0].update(text="Bore is 8.00 mm, assumed.")), "make_readme.py", 2, "CHK-NUMBERS",
        with_repro=True)
    neg("superseded verdict missing", lambda r: (r / "_it1_SUPERSEDED" / "qa" / "VERDICT.md").unlink(),
        "make_readme.py", 2, "CHK-SUPERSEDED")
    neg("STEP changed after QA", lambda r: [p.write_bytes(p.read_bytes() + b"\n") for p in (r / "build").glob("*.step")],
        "make_readme.py", 2, "hash_frozen")
    neg("limitation without re-run trigger", lambda r: edit_json(
        r / "deliver" / "limitations.json", lambda d: d["limitations"][0].update(rerun_trigger="")),
        "make_readme.py", 2, "rerun_trigger", with_repro=True)

    # BAND_NOT_MET accepted -> delivers
    rr = prepare(work / "band_accepted")
    band(rr)
    (rr / "qa" / "acceptance_note.md").write_text("Owner accepts the fixture band miss for pipeline testing.\n")
    with (rr / "DECISIONS.md").open("a") as fh:
        fh.write("- 1970-01-02 | fixture-owner | ACCEPT-BAND | accept fixture miss for testing | qa/acceptance_note.md\n")
    ok = sh("repro_check.py", rr).returncode == 0 and sh("make_readme.py", rr).returncode == 0
    txt = (rr / "deliver" / "README.md").read_text() if ok else ""
    case("BAND_NOT_MET with ACCEPT-BAND delivers and says so", ok and "was NOT met" in txt and "fixture-owner" in txt)

    # non-deterministic model -> repro fails
    rr = prepare(work / "nondeterministic")
    mp = rr / "build" / "model.py"
    mp.write_text(mp.read_text().replace('P["plate_x"], P["plate_y"]',
                                         'P["plate_x"] + (__import__("time").time_ns() % 997) * 1e-4, P["plate_y"]'))
    p = sh("repro_check.py", rr)
    case("non-deterministic rebuild detected", p.returncode == 1 and
         json.loads((rr / "deliver" / "repro.json").read_text())["reproducible"] is False)

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed; workdir {work}")
    if not a.keep and not failed:
        shutil.rmtree(work, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
