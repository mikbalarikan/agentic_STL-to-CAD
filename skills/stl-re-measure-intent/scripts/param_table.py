#!/usr/bin/env python3
"""Validate measure/params.json and render measure/PARAM_TABLE.md from it.

Provenance: NEW code. Schema = skills/stl-re-orchestrate/references/run-contract.md §4
(binding). Validation rules encode analysis/SYNTHESIS.md rows C4-C11, C13-C14 and checks
CHK-COUNT / CHK-ACHIEVABLE / CHK-CLUSTER / CHK-FRAME; the table layout follows the golden
PARAM_TABLEs (golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/PARAM_TABLE.md,
golden-examples/OOM-P03_mop-pad-bracket/6_RE_work/PARAM_TABLE.md: value, SOURCE, measured,
chosen, rule/notes) and facet-film T8 (name, value, unit, provenance, source, estimator).
PARAM_TABLE.md is generated, never hand-edited (run-contract §4).

Exit code 0 = valid; 1 = errors (listed). Warnings never fail unless --strict.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_alignment, scan_noise_mm, sha256  # noqa: E402

UNITS = {"mm", "deg", "count"}
RULES = {"caliper-direct", "round-within-noise", "std-size-snap", "symmetry", "mean-of-n",
         "keep-measured", "photo-inferred", "assumed"}
SOURCES = {"caliper", "caliper-photo", "operator-spec", "scan", "photo-inferred", "standard", "assumed"}
REQUIRED = ["value", "unit", "measured", "rule", "source", "estimator", "uncertainty_mm", "evidence", "critical"]
MEASURED_SOURCES = {"caliper", "caliper-photo", "operator-spec", "scan"}
CHECKS = ["CHK-COUNT", "CHK-ACHIEVABLE", "CHK-CLUSTER", "CHK-FRAME"]
STD_SNAP_WINDOW = 0.1        # RE_SPEC.md:92 (baseline/oomwoo-re-pipeline)
PHOTO_UNC = 0.1              # OOM-B02 5_reference/MEASUREMENTS.md:24; TRACKER.md:13


def _num(x: Any) -> Optional[float]:
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, list) and x and all(isinstance(v, (int, float)) for v in x):
        return sum(x) / len(x)
    return None


def _numlist(x: Any) -> Optional[list[float]]:
    """x as a list[float] iff it IS a list and every element is a plain number; else None."""
    if isinstance(x, list) and x and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in x):
        return [float(v) for v in x]
    return None


_RANGE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*(?:\.\.|…|–)\s*(-?\d+(?:\.\d+)?)\s*$")


def _range(x: Any) -> Optional[tuple[float, float]]:
    """(lo, hi) for a number, a list of numbers or an 'a..b' string; None for prose/null."""
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)):
        return (float(x), float(x))
    if isinstance(x, list) and x and all(isinstance(v, (int, float)) for v in x):
        return (float(min(x)), float(max(x)))
    if isinstance(x, str):
        m = _RANGE.match(x)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            return (min(a, b), max(a, b))
    return None


def validate(doc: dict[str, Any], noise: Optional[float]) -> tuple[list[str], list[str]]:
    E: list[str] = []
    W: list[str] = []
    params = doc.get("params")
    if not isinstance(params, dict) or not params:
        return ["'params' missing or empty"], W
    for name, p in params.items():
        tag = f"[{name}]"
        miss = [k for k in REQUIRED if k not in p]
        if miss:
            E.append(f"{tag} missing keys {miss}")
            continue
        if p["unit"] not in UNITS:
            E.append(f"{tag} unit '{p['unit']}' not in {sorted(UNITS)}")
        if p["rule"] not in RULES:
            E.append(f"{tag} rule '{p['rule']}' not in {sorted(RULES)}")
        if p["source"] not in SOURCES:
            E.append(f"{tag} source '{p['source']}' not in {sorted(SOURCES)}")
        if not str(p["estimator"]).strip():
            E.append(f"{tag} empty estimator (C13: every value records how it was measured)")
        v, meas, src, rule = p["value"], _num(p["measured"]), p["source"], p["rule"]
        raw_meas = p["measured"]
        is_list_value = isinstance(v, list)
        if src in MEASURED_SOURCES and p["measured"] is None and rule not in ("assumed",):
            E.append(f"{tag} source '{src}' but measured is null")
        if src in ("photo-inferred", "assumed", "standard") and rule in ("caliper-direct", "round-within-noise", "mean-of-n"):
            E.append(f"{tag} rule '{rule}' needs a measurement, but source is '{src}' (C11: never call unscanned geometry measured)")
        if rule in ("assumed", "photo-inferred") and src in MEASURED_SOURCES:
            E.append(f"{tag} rule '{rule}' but source '{src}' is a measured source (C11: never tag "
                     "unscanned/unmeasured geometry as measured; e.g. a scan source can't also be 'assumed')")
        if src in ("photo-inferred", "assumed", "standard") and p["measured"] is not None:
            E.append(f"{tag} source '{src}' but measured is not null (C11: unscanned/unmeasured geometry "
                     "keeps measured: null)")
        if rule == "caliper-direct" and src not in ("caliper", "caliper-photo", "operator-spec"):
            E.append(f"{tag} caliper-direct with source '{src}'")
        if src == "caliper-photo":
            if not str(p["evidence"]).strip():
                E.append(f"{tag} caliper-photo needs the photo id in evidence (C5)")
            if not str(p.get("attribution", "")).strip():
                E.append(f"{tag} caliper-photo needs 'attribution' = who confirmed which feature/jaw placement (C5; see analysis/golden/OOM-B02.md for a case with unconfirmed readings left unused)")
            if (p["uncertainty_mm"] or 0) < PHOTO_UNC:
                E.append(f"{tag} caliper-photo uncertainty {p['uncertainty_mm']} < {PHOTO_UNC} mm effective (B02 MEASUREMENTS.md:24)")
        if rule == "std-size-snap" and src not in ("caliper", "caliper-photo", "operator-spec"):
            E.append(f"{tag} std-size-snap only for caliper values (RE_SPEC.md:92); source is '{src}'" +
                     (" - C9: never snap an uncalipered critical interface (see analysis/golden/OOM-B02.md)" if p["critical"] else ""))
        if rule == "std-size-snap":
            W.append(f"{tag} std-size-snap is a heuristic: no golden applied it (SYNTHESIS §6)")
        if rule == "round-within-noise" and noise is None:
            E.append(f"{tag} round-within-noise but no scan noise floor (alignment.json scan_noise_mm) was supplied (C8)")
        if rule == "symmetry":
            sc = p.get("scatter_mm")
            if sc is None:
                E.append(f"{tag} symmetry without 'scatter_mm' (C10: enforce only when measured scatter is "
                         "within noise; scatter_mm is required for this rule, param-table-schema.md §2)")
            if raw_meas is not None and _numlist(raw_meas) is None:
                E.append(f"{tag} symmetry needs a per-instance 'measured' list (the raw reads), not a "
                         f"scalar/prose value ({raw_meas!r})")
            if sc is not None:
                if p["unit"] != "mm" and p.get("scatter_note") is None:
                    W.append(f"{tag} symmetry on a {p['unit']} value: scatter cannot be compared with the mm noise floor; "
                             "add 'scatter_note' (design-intent reason + residual it leaves)")
                elif p["unit"] == "mm" and noise is not None and sc > noise and p.get("scatter_note") is None:
                    E.append(f"{tag} symmetry enforced with scatter {sc} > noise {noise}: keep measured and declare, "
                             "or give 'scatter_note' with the design-intent reason and its deviation cost (C10)")
        if rule == "mean-of-n":
            if is_list_value:
                E.append(f"{tag} mean-of-n needs a scalar 'value' (the mean), not a list")
            else:
                mnums = _numlist(raw_meas)
                if mnums is None or len(mnums) < 2:
                    E.append(f"{tag} mean-of-n needs 'measured' as a list of >=2 numbers (the reads); got {raw_meas!r}")
                elif _num(v) is not None:
                    mean_ = sum(mnums) / len(mnums)
                    tol = noise if (src == "scan" and noise is not None) else p.get("uncertainty_mm")
                    if tol is None:
                        E.append(f"{tag} mean-of-n: no tolerance (uncertainty_mm, or scan noise) to verify the mean")
                    elif abs(_num(v) - mean_) > float(tol) + 1e-9:
                        E.append(f"{tag} mean-of-n: value {v} != mean of measured {raw_meas} ({mean_:g}) "
                                 f"within +/-{tol}")
        if is_list_value and rule not in ("symmetry", "mean-of-n"):
            # Element-wise checks for a per-instance list value (run-contract §11), e.g. DRM legs
            # at unequal angles. Never reduce a list to its mean here (M2).
            vnums = _numlist(v)
            if vnums is None:
                E.append(f"{tag} list value must be all-numeric")
            else:
                mnums = _numlist(raw_meas)
                if mnums is None or len(mnums) != len(vnums):
                    E.append(f"{tag} list value needs 'measured' as a same-length list of numbers "
                             f"(run-contract §11); value has {len(vnums)}, measured is {raw_meas!r}")
                else:
                    for i, (vi, mi) in enumerate(zip(vnums, mnums)):
                        itag = f"{tag}[{i}]"
                        if rule == "keep-measured" and abs(vi - mi) > 1e-9:
                            E.append(f"{itag} keep-measured but value {vi:g} != measured {mi:g}")
                        if rule == "caliper-direct" and abs(vi - mi) > 1e-9 and not p.get("derivation"):
                            E.append(f"{itag} caliper-direct but value {vi:g} != measured {mi:g} and no 'derivation'")
                        if rule == "round-within-noise" and noise is not None and abs(vi - mi) > noise + 1e-9:
                            E.append(f"{itag} rounding moves {mi:g} -> {vi:g}: outside +/-{noise} noise (C8)")
                        if (rule == "std-size-snap" and src in ("caliper", "caliper-photo", "operator-spec")
                                and abs(vi - mi) > STD_SNAP_WINDOW + 1e-9):
                            E.append(f"{itag} std-size-snap moves {mi:g} -> {vi:g}, outside "
                                     f"+/-{STD_SNAP_WINDOW} mm (RE_SPEC.md:92)")
                        if p["critical"] and src == "scan" and noise is not None and abs(vi - mi) > noise + 1e-9:
                            E.append(f"{itag} critical scan-authority value moved {mi:g} -> {vi:g}, beyond "
                                     f"scan noise {noise} (C9): rule '{rule}' does not license this")
        elif not is_list_value:
            # Scalar value: the original range/mean checks, restricted to rules where they apply.
            if rule == "round-within-noise" and noise is not None:
                if _range(raw_meas) is not None and _num(v) is not None:
                    lo, hi = _range(raw_meas)  # type: ignore[misc]
                    if not (lo - noise - 1e-9 <= _num(v) <= hi + noise + 1e-9):  # type: ignore[operator]
                        E.append(f"{tag} rounding moves {raw_meas} -> {v}: outside measured range +/- noise {noise} "
                                 "(C8: no fixed 0.1/0.5/1.0 step)")
                else:
                    E.append(f"{tag} round-within-noise but 'measured' is not numeric/range: cannot verify the move")
            if rule == "caliper-direct" and meas is not None and _num(v) is not None and abs(_num(v) - meas) > 1e-9 \
                    and not p.get("derivation"):
                E.append(f"{tag} caliper-direct but value {v} != measured {raw_meas} and no 'derivation' (e.g. 'radius = D/2')")
            if rule == "std-size-snap" and src in ("caliper", "caliper-photo", "operator-spec") \
                    and meas is not None and _num(v) is not None and abs(_num(v) - meas) > STD_SNAP_WINDOW + 1e-9:
                E.append(f"{tag} std-size-snap moves {meas} -> {v}, outside +/-{STD_SNAP_WINDOW} mm (RE_SPEC.md:92)")
            if rule == "keep-measured" and _range(raw_meas) is not None and _num(v) is not None:
                lo, hi = _range(raw_meas)  # type: ignore[misc]
                if not (lo - 1e-9 <= _num(v) <= hi + 1e-9):  # type: ignore[operator]
                    E.append(f"{tag} keep-measured but value {v} is outside measured {raw_meas}")
            if p["critical"] and src == "scan" and noise is not None and meas is not None and _num(v) is not None \
                    and abs(_num(v) - meas) > noise + 1e-9:
                E.append(f"{tag} critical scan-authority value moved {meas:g} -> {_num(v):g}, beyond scan "
                         f"noise {noise} (C9): rule '{rule}' does not license this, even with a scatter_note")
        if p["critical"] and src == "scan" and rule not in ("keep-measured", "round-within-noise", "mean-of-n", "symmetry"):
            E.append(f"{tag} critical scan-authority value with rule '{rule}': hold the scan fit (C9)")
        if p["critical"] and src in ("scan", "photo-inferred", "assumed") and not p.get("rerun_trigger"):
            W.append(f"{tag} critical and not calipered: add 'rerun_trigger' (e.g. 'one caliper reading -> re-run'; B02 VERDICT.md:28-30)")
        if p["unit"] == "count":
            if not isinstance(v, int):
                E.append(f"{tag} count value must be an integer")
            if src == "scan" and "order" not in str(p["estimator"]).lower() and "fft" not in str(p["estimator"]).lower():
                E.append(f"{tag} scan count must come from rotational order / FFT (CHK-COUNT), not peaks")
        if p["unit"] == "deg" and "frame" not in p and "theta" in name.lower():
            W.append(f"{tag} angle without 'frame' note (CHK-FRAME: datum frame + sign convention)")
    for s in doc.get("struck", []):
        for k in ("name", "reading", "window", "proof", "rerun_trigger"):
            if k not in s:
                E.append(f"[struck {s.get('name', '?')}] missing '{k}' (CHK-ACHIEVABLE: proof + re-measure hook)")
    for s in doc.get("simplifications", []):
        if not s.get("deviation_cost"):
            E.append(f"[simplification {s.get('name', '?')}] missing deviation_cost (C14)")
    checks = doc.get("checks", {})
    for c in CHECKS:
        if c not in checks:
            W.append(f"check {c} not recorded")
        elif checks[c].get("result") == "fail":
            E.append(f"check {c} = fail: resolve before handing to the rebuild ({checks[c].get('note', '')})")
    if "frame" not in doc:
        W.append("top-level 'frame' (datum frame, theta sign convention) missing (CHK-FRAME)")
    return E, W


def _fmt(x: Any) -> str:
    if x is None:
        return "—"
    if isinstance(x, list):
        return " / ".join(_fmt(v) for v in x)
    if isinstance(x, float):
        return f"{x:g}"
    return str(x).replace("|", "\\|").replace("\n", " ")


def render(doc: dict[str, Any], src_path: str, noise: Optional[float]) -> str:
    L = [f"# PARAM_TABLE — {doc.get('part', '')}".rstrip(" —"), "",
         f"> Generated by `param_table.py` from `{src_path}` (sha256 `{sha256(src_path)[:16]}…`). "
         "Do not edit by hand; edit params.json and re-render.", ""]
    if "frame" in doc:
        L += [f"**Frame:** {_fmt(doc['frame'])}", ""]
    L += [f"**Scan noise floor:** {_fmt(noise)} mm (rounding is allowed only within this)", "",
          "| name | value | unit | measured | rule | source | ± mm | estimator | evidence | critical |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for n, p in doc["params"].items():
        crit = "**yes**" if p.get("critical") else ""
        L.append(f"| `{n}` | **{_fmt(p.get('value'))}** | {_fmt(p.get('unit'))} | {_fmt(p.get('measured'))} | "
                 f"{_fmt(p.get('rule'))} | {_fmt(p.get('source'))} | {_fmt(p.get('uncertainty_mm'))} | "
                 f"{_fmt(p.get('estimator'))} | {_fmt(p.get('evidence'))} | {crit} |")
    notes = [(n, p) for n, p in doc["params"].items() if p.get("note") or p.get("rerun_trigger") or p.get("attribution")]
    if notes:
        L += ["", "## Notes, attributions and re-run triggers", ""]
        for n, p in notes:
            bits = [f"{k}: {_fmt(p[k])}" for k in ("note", "attribution", "rerun_trigger") if p.get(k)]
            L.append(f"- `{n}` — " + "; ".join(bits))
    if doc.get("struck"):
        L += ["", "## Struck readings (CHK-ACHIEVABLE) — not built to", "",
              "| reading | value | achievable window | proof | re-measure hook |", "|---|---|---|---|---|"]
        for s in doc["struck"]:
            L.append(f"| {_fmt(s.get('name'))} | {_fmt(s.get('reading'))} | {_fmt(s.get('window'))} | "
                     f"{_fmt(s.get('proof'))} | {_fmt(s.get('rerun_trigger'))} |")
    if doc.get("simplifications"):
        L += ["", "## Declared simplifications", "", "| what | modelled as | deviation cost |", "|---|---|---|"]
        for s in doc["simplifications"]:
            L.append(f"| {_fmt(s.get('name'))} | {_fmt(s.get('modelled_as'))} | {_fmt(s.get('deviation_cost'))} |")
    if doc.get("checks"):
        L += ["", "## Checks", "", "| check | ran | result | note |", "|---|---|---|---|"]
        for c, r in doc["checks"].items():
            L.append(f"| {c} | {_fmt(r.get('ran'))} | {_fmt(r.get('result'))} | {_fmt(r.get('note'))} |")
    if doc.get("open_questions"):
        L += ["", "## Open questions", ""] + [f"- {_fmt(q)}" for q in doc["open_questions"]]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("params", help="measure/params.json")
    ap.add_argument("--alignment", help="intake/alignment.json (reads scan_noise_mm)")
    ap.add_argument("--out", help="PARAM_TABLE.md path (default: next to params.json)")
    ap.add_argument("--strict", action="store_true", help="warnings fail too")
    a = ap.parse_args()
    doc = json.load(open(a.params))
    noise = scan_noise_mm(load_alignment(a.alignment)) if a.alignment else None
    if noise is None and isinstance(doc.get("scan_noise_mm"), (int, float)):
        noise = float(doc["scan_noise_mm"])
    E, W = validate(doc, noise)
    for w in W:
        print("WARN ", w)
    for e in E:
        print("ERROR", e)
    if E or (a.strict and W):
        print(f"INVALID: {len(E)} errors, {len(W)} warnings — PARAM_TABLE.md not written")
        sys.exit(1)
    out = Path(a.out) if a.out else Path(a.params).with_name("PARAM_TABLE.md")
    out.write_text(render(doc, a.params, noise))
    print(f"valid ({len(W)} warnings) -> {out}")


if __name__ == "__main__":
    main()
