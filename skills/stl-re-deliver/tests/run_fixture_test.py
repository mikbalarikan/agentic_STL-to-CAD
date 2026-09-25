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
    # Real shape (run-contract.md section 12, step_check.py verify): {before, after, unchanged},
    # each of before/after keyed by the STEP path. A STEP's hash is only known after the build
    # runs, so this replaces the generator's placeholder hash_frozen block.
    shas = {f"build/{p.name}": sha256_file(p) for p in exports.values()}
    g["hash_frozen"] = {"before": shas, "after": shas, "unchanged": True}
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
    # D14: the old assertion was `A or B` where B alone is already implied by the earlier
    # "repro_check reproducible" case, so this could never fail. Assert the STEP-hash claim on
    # its own: raw sha256 differs (STEP headers carry a timestamp) for every produced STEP.
    case("repro raw sha differs (timestamps) but geometry identical",
         bool(repro.get("files")) and all(not f["raw_sha256_equal"] for f in repro["files"]))
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

    BAND_FAIL = "tier1 F01 plate_x: delta +0.550 vs ±0.15"

    def band(r: Path) -> None:
        def mut(d: dict) -> None:
            d["verdict"] = "BAND_NOT_MET"
            d["proposed_verdict"] = "BAND_NOT_MET"
            d["allowed_verdicts"] = ["BAND_NOT_MET", "REVISE", "HALT"]
            d["band_fails"] = [BAND_FAIL]
            d["miss_explanations"] = [{"region": "F01 plate_x", "cause": "caliper reading outside the "
                                       "±0.15 mm Tier-1 band (fixture)", "options": ["re-measure F01", "accept the miss"]}]
            d["errors"] = []
        edit_json(r / "qa" / "gate.json", mut)
        (r / "qa" / "VERDICT.md").write_text("**VERDICT: BAND_NOT_MET** (fixture)\n")
    neg("BAND_NOT_MET without ACCEPT-BAND", band, "make_readme.py", 2, "ACCEPT-BAND")
    neg("literal decimal in limitations", lambda r: edit_json(
        r / "deliver" / "limitations.json",
        lambda d: d["limitations"][0].update(text=d["limitations"][0]["text"] + " Bore is 8.00 mm, assumed.")),
        "make_readme.py", 2, "CHK-NUMBERS", with_repro=True)
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
    gate_sha = sha256_file(rr / "qa" / "gate.json")
    # D4: the evidence must live outside every pipeline stage folder (decisions/ or the run
    # root), and must name both this gate (by sha256 prefix) and the missed band.
    (rr / "decisions").mkdir(exist_ok=True)
    (rr / "decisions" / "accept_band_miss.md").write_text(
        f"Owner accepts the fixture band miss ({BAND_FAIL.split(':')[0]}) for pipeline testing.\n"
        f"Gate: qa/gate.json sha256 {gate_sha}\n")
    with (rr / "DECISIONS.md").open("a") as fh:
        fh.write(f"- 1970-01-02 | fixture-owner | ACCEPT-BAND | accept {BAND_FAIL.split(':')[0]} "
                 f"miss, gate {gate_sha[:12]} | decisions/accept_band_miss.md\n")
    ok = sh("repro_check.py", rr).returncode == 0 and sh("make_readme.py", rr).returncode == 0
    txt = (rr / "deliver" / "README.md").read_text() if ok else ""
    case("BAND_NOT_MET with ACCEPT-BAND delivers and says so", ok and "was NOT met" in txt and "fixture-owner" in txt)

    # D4: an ACCEPT-BAND entry whose evidence lives under a pipeline stage folder (here qa/) is
    # refused even though the file exists and the text otherwise looks right.
    rr = prepare(work / "band_accepted_qa_evidence")
    band(rr)
    gate_sha2 = sha256_file(rr / "qa" / "gate.json")
    (rr / "qa" / "acceptance_note.md").write_text(f"Owner accepts. Gate sha256 {gate_sha2}\n")
    with (rr / "DECISIONS.md").open("a") as fh:
        fh.write(f"- 1970-01-02 | fixture-owner | ACCEPT-BAND | accept {BAND_FAIL.split(':')[0]} "
                 f"miss, gate {gate_sha2[:12]} | qa/acceptance_note.md\n")
    p = sh("make_readme.py", rr)
    case("refuse: ACCEPT-BAND evidence under qa/", p.returncode == 2 and "pipeline output" in p.stderr and
         not (rr / "deliver" / "README.md").exists(), f"rc={p.returncode} {p.stderr.strip()[-200:]}")

    # D4: an ACCEPT-BAND entry that does not cite this gate (by sha or by naming its band) is
    # refused even though its evidence file is a real, otherwise-valid decisions/ document.
    rr = prepare(work / "band_accepted_stale")
    band(rr)
    (rr / "decisions").mkdir(exist_ok=True)
    (rr / "decisions" / "old_note.md").write_text("Owner accepts some earlier miss.\n")
    with (rr / "DECISIONS.md").open("a") as fh:
        fh.write("- 1970-01-02 | fixture-owner | ACCEPT-BAND | accept an old miss | decisions/old_note.md\n")
    p = sh("make_readme.py", rr)
    case("refuse: ACCEPT-BAND does not cite this gate", p.returncode == 2 and
         "does not reference this gate" in p.stderr and not (rr / "deliver" / "README.md").exists(),
         f"rc={p.returncode} {p.stderr.strip()[-200:]}")

    # non-deterministic model -> repro fails
    rr = prepare(work / "nondeterministic")
    mp = rr / "build" / "model.py"
    mp.write_text(mp.read_text().replace('P["plate_x"], P["plate_y"]',
                                         'P["plate_x"] + (__import__("time").time_ns() % 997) * 1e-4, P["plate_y"]'))
    p = sh("repro_check.py", rr)
    case("non-deterministic rebuild detected", p.returncode == 1 and
         json.loads((rr / "deliver" / "repro.json").read_text())["reproducible"] is False)

    # D3: deliver/repro.json is stale once build/model.py changes after the repro check ran.
    neg("model.py changed after repro (stale repro.json)",
        lambda r: (r / "build" / "model.py").write_text(
            (r / "build" / "model.py").read_text().replace("plate_x\"], P[\"plate_y", "plate_x\"] * 2, P[\"plate_y")),
        "make_readme.py", 2, "stale", with_repro=True)

    # D5: repro_check.py's default --cwd run supports the rebuild skill's own "library use"
    # pattern (`from export_frames import export_frames`, run-root-relative paths) -- not just
    # the model_template.py CLI style. tests/fixture_extra/model_library_style.py produces the
    # identical geometry through that path.
    rr = prepare(work / "library_style_rebuild")
    (rr / "build" / "model.py").write_text((HERE / "fixture_extra" / "model_library_style.py").read_text())
    p = sh("repro_check.py", rr)
    repro_lib = json.loads((rr / "deliver" / "repro.json").read_text()) if (rr / "deliver" / "repro.json").exists() else {}
    case("library-use model.py (run-root-relative export_frames) reproduces under --cwd run",
         p.returncode == 0 and repro_lib.get("reproducible") is True and repro_lib.get("cwd") == "run",
         p.stderr.strip()[-300:])

    # D7: Ø8.00 / AF7.358-style tokens must be caught, not just a plain decimal.
    neg("Ø-diameter literal in limitations", lambda r: edit_json(
        r / "deliver" / "limitations.json",
        lambda d: d["limitations"][0].update(text=d["limitations"][0]["text"] + " Bore Ø8.00 mm.")),
        "make_readme.py", 2, "CHK-NUMBERS", with_repro=True)
    neg("AF-hex literal in limitations", lambda r: edit_json(
        r / "deliver" / "limitations.json",
        lambda d: d["limitations"][0].update(text=d["limitations"][0]["text"] + " Hex AF7.358.")),
        "make_readme.py", 2, "CHK-NUMBERS", with_repro=True)

    # D9: --runs 0 must be refused, not silently reported as reproducible.
    rr = prepare(work / "runs_zero")
    p = sh("repro_check.py", rr, "--runs", "0")
    case("refuse: repro_check --runs 0", p.returncode == 2 and "--runs" in p.stderr and
         not (rr / "deliver" / "repro.json").exists(), f"rc={p.returncode} {p.stderr.strip()[-200:]}")

    # D10: qa/gate.json#hash_frozen.unchanged: false is a hard CHK-PUBLISH refusal, even though
    # build/ still holds the STEPs QA hashed.
    neg("hash_frozen.unchanged is false", lambda r: edit_json(
        r / "qa" / "gate.json", lambda d: d["hash_frozen"].update(unchanged=False)),
        "make_readme.py", 2, "hash_frozen.unchanged")

    # D2: a limitation verify declared (qa/gate.json#limitations) that never made it into
    # deliver/limitations.json must not be silently dropped.
    neg("gate limitation missing from limitations.json", lambda r: edit_json(
        r / "qa" / "gate.json",
        lambda d: d["limitations"].append({"id": "L2", "text": "a second limitation verify found",
                                           "rerun_trigger": "x", "evidence": "y"})),
        "make_readme.py", 2, "missing verify's declared limitation", with_repro=True)

    # D2: an automatic finding (qa/gate.json#auto_limitations) must be covered by some declared
    # limitation's text or evidence, not disappear.
    neg("auto_limitations not covered", lambda r: edit_json(
        r / "qa" / "gate.json", lambda d: d["auto_limitations"].append("mask-dependent pass: whole part scan_to_cad")),
        "make_readme.py", 2, "auto_limitations", with_repro=True)

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed; workdir {work}")
    if not a.keep and not failed:
        shutil.rmtree(work, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
