#!/usr/bin/env python3
"""Render <run>/deliver/README.md from the run's JSON artefacts. Every number is read from JSON.

Provenance:
- "Every number is READ FROM THE SAVED QA JSON, never retyped" -- lifted in spirit from
  golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/70_report.py:1-5,17-19 (json.load of the QA
  outputs). CHK-NUMBERS was earned by the B02 verdict drift (6_RE_work/VERDICT.md:95-99).
- Section list: references/readme-template.md (RE_SPEC §9 DoD item 3,
  baseline/oomwoo-re-pipeline/RE_SPEC.md:330-333; OD-H12 and dreame_brush-caps README structure;
  M02 claim boundary golden-examples/M02-02-03_watertight-design-intent/README.md:29-31;
  B02 fitness golden-examples/OOM-B02_side-brush-3-arm/6_RE_work/VERDICT.md:204-213).
- Inputs: run-contract §3-§6 (skills/stl-re-orchestrate/references/run-contract.md).

Prose in deliver/limitations.json may cite numbers only through placeholders such as
{{gate:deviation.scan_to_cad.p95}}; a literal decimal in prose fails CHK-NUMBERS.
BAND_NOT_MET acceptance is read from the ACCEPT-BAND entry of <run>/DECISIONS.md (run-contract §10).
Prefixes: gate (qa/gate.json), params (measure/params.json), export (build/export_check.json),
align (intake/alignment.json), repro (deliver/repro.json).

Exit codes: 0 written; 2 refused (message names the check and the next action).
Deterministic: output depends only on the input files (no timestamps in README.md).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (MAX_LOOPS, DeliverError, check_repro_fresh, fail, load_json, preflight,  # noqa: E402
                     run_main, sha256_file)

PLACEHOLDER = re.compile(r"\{\{(gate|params|export|align|repro):([A-Za-z0-9_.\-\[\] ]+)\}\}")
# D7: the old lookbehind `(?<![\w.])` treated letters, digits and the diameter sign as "word"
# characters, so `Ø8.00`, `AF7.358`, `M3.5` and `x8.5` slipped through uncaught. Only a
# preceding digit or '.' should suppress a match now (that is what protects a placeholder's own
# digits and a number already flagged by an earlier match), so any decimal reachable through a
# letter, `Ø`, `x`, whitespace or punctuation is still caught.
LITERAL_DECIMAL = re.compile(r"(?<![\d.])[-+]?\d+\.\d+")
STAT_KEYS = ("n", "rms", "p50", "p95", "p99", "max")
ASSUMED_SOURCES = ("assumed", "photo-inferred", "standard")


def fmt(v: Any) -> str:
    """Display format only. JSON remains the authority (4 decimals, trailing zeros stripped)."""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    if isinstance(v, int):
        return str(v)
    if v is None:
        return "—"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(fmt(x) for x in v) + "]"
    if isinstance(v, dict):
        return "; ".join(f"{k}: {fmt(x)}" for k, x in v.items())
    return str(v).replace("|", "\\|").replace("\n", " ")


def dig(obj: Any, dotted: str) -> Any:
    cur = obj
    for part in dotted.strip().split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            raise KeyError(dotted)
    return cur


class Renderer:
    def __init__(self, run: Path, docs: dict[str, Any], files: dict[str, Path]) -> None:
        self.run = run
        self.docs = docs
        self.files = files
        self.lines: list[str] = []
        self.sec = 0

    def h2(self, title: str) -> None:
        self.sec += 1
        self.w(f"## {self.sec}. {title}", "")

    # -- prose with placeholders ------------------------------------------------------------
    def prose(self, text: str, where: str) -> str:
        def sub(m: re.Match[str]) -> str:
            key, path = m.group(1), m.group(2)
            try:
                root = self.docs[key]
                if key == "params" and isinstance(root, dict) and "params" in root:
                    root = root["params"]  # {{params:<name>.value}}
                return fmt(dig(root, path))
            except KeyError:
                raise DeliverError(
                    f"CHK-NUMBERS fail: placeholder {{{{{key}:{path}}}}} in {where} does not resolve "
                    f"in {self.files[key].relative_to(self.run)}"
                ) from None

        stripped = PLACEHOLDER.sub("", text)
        lit = LITERAL_DECIMAL.findall(stripped)
        if lit:
            raise DeliverError(
                f"CHK-NUMBERS fail: literal number(s) {lit} in {where}. Cite them with a placeholder "
                "such as {{gate:deviation.scan_to_cad.p95}} so the README cannot drift from the JSON."
            )
        return PLACEHOLDER.sub(sub, text)

    def w(self, *ls: str) -> None:
        self.lines.extend(ls)

    def table(self, head: list[str], rows: list[list[Any]]) -> None:
        self.w("| " + " | ".join(head) + " |", "|" + "---|" * len(head))
        for r in rows:
            self.w("| " + " | ".join(fmt(c) if not isinstance(c, str) else c.replace("|", "\\|") for c in r) + " |")
        self.w("")


def _s(s: Any) -> str:
    """Compact one-line stats summary (display only; the table above carries the real numbers)."""
    if not isinstance(s, dict) or not s.get("n"):
        return "n 0"
    return f"n {fmt(s['n'])} · p95 {fmt(s.get('p95'))} · max {fmt(s.get('max'))}"


def stats_row(label: str, s: Any, src: str) -> list[Any]:
    if not isinstance(s, dict):
        return [label] + ["—"] * len(STAT_KEYS) + ["not reported", src]
    extra = []
    for k in ("sampling", "seed", "scan", "full_res"):
        if k in s:
            extra.append(f"{k} {fmt(s[k])}")
    return [label] + [s.get(k) for k in STAT_KEYS] + ["; ".join(extra) or "—", src]


def render(run: Path, limitations_path: Path, out: Path) -> str:
    pf = preflight(run)  # CHK-PUBLISH, ACCEPT-BAND, CHK-SUPERSEDED, inputs, hash freeze, regime
    verdict, gate, acc = pf["verdict"], pf["gate"], pf["acceptance"]
    files = {
        "gate": run / "qa" / "gate.json",
        "params": run / "measure" / "params.json",
        "export": run / "build" / "export_check.json",
        "align": run / "intake" / "alignment.json",
        "repro": run / "deliver" / "repro.json",
    }
    docs: dict[str, Any] = {"gate": gate}
    if not files["repro"].is_file():
        raise DeliverError("deliver/repro.json missing: run repro_check.py before make_readme.py")
    for k in ("params", "export", "align", "repro"):
        docs[k] = load_json(files[k])
    lim = load_json(limitations_path)

    # ---- structural checks (refuse, never paper over) ---------------------------------------
    limits = lim.get("limitations") or []
    if verdict == "APPROVED" and limits:
        raise DeliverError(
            "verdict APPROVED but limitations.json declares limitations; per run-contract §7 that is "
            "APPROVED_WITH_LIMITATIONS. Return to stl-re-verify; do not change the verdict here."
        )
    if verdict in ("APPROVED_WITH_LIMITATIONS", "BAND_NOT_MET") and not limits:
        raise DeliverError(f"verdict {verdict} needs at least one declared limitation (SYNTHESIS F10).")
    for i, L in enumerate(limits):
        if not str(L.get("rerun_trigger", "")).strip():
            raise DeliverError(f"limitation #{i + 1} ({L.get('id')}) has no rerun_trigger (SYNTHESIS F10).")
    cb = lim.get("claim_boundary") or {}
    if not cb.get("not_fit_for"):
        raise DeliverError("claim_boundary.not_fit_for is empty; state what the result is NOT (SYNTHESIS F7).")

    # D2: every limitation verify actually found (qa/gate.json#limitations, written by
    # verdict.py from review.json) must reach the README, matched by id (or by text when a
    # limitation carries no id) -- it must not be re-typed from memory and silently dropped.
    declared_ids = {str(L["id"]) for L in limits if L.get("id")}
    declared_texts = {str(L["text"]) for L in limits if L.get("text")}
    missing_gate_lims = [L.get("id") or L.get("text") for L in gate.get("limitations") or []
                         if not ((L.get("id") and str(L["id"]) in declared_ids) or
                                 (L.get("text") and str(L["text"]) in declared_texts))]
    if missing_gate_lims:
        raise DeliverError(f"deliver/limitations.json is missing verify's declared limitation(s) "
                           f"{missing_gate_lims} (qa/gate.json#limitations); every limitation verify "
                           "found must reach the README with the same id, not be re-typed or dropped.")
    # Every automatic finding (mask-dependent pass, partial Tier-1, grey zone, decimated scan, ...)
    # needs a declared limitation that actually covers it, identified by its keyword (the phrase
    # before the first ':', e.g. "tier1 partial", "mask-dependent pass").
    auto_limits = gate.get("auto_limitations") or []
    declared_blob = " ".join(f"{L.get('text', '')} {L.get('evidence', '')}" for L in limits).lower()
    uncovered = [a for a in auto_limits if a.split(":", 1)[0].strip().lower() not in declared_blob]
    if uncovered:
        raise DeliverError(f"deliver/limitations.json does not cover qa/gate.json#auto_limitations "
                           f"{uncovered}; declare each one (mention its keyword in a limitation's text "
                           "or evidence) instead of letting it disappear.")
    # D11: rebuild says a failed or shrunk fillet must be declared as a limitation
    # (stl-re-rebuild-build123d/SKILL.md:194, CHK-FILLET). export_check.json's per-frame
    # `fillets` list is written by export_frames.py; any entry not `OK` is a geometry deviation.
    bad_fillets = []
    ex_doc = docs.get("export") or {}
    for frame_name, frame in (ex_doc.get("exports", ex_doc) if isinstance(ex_doc, dict) else {}).items():
        if not isinstance(frame, dict):
            continue
        for f in frame.get("fillets") or []:
            if f.get("status") != "OK":
                bad_fillets.append(f"{frame_name}: {f.get('feature', f)}")
    if bad_fillets:
        declared_blob_fillet = " ".join(f"{L.get('text', '')} {L.get('evidence', '')}" for L in limits)
        if "export_check.json" not in declared_blob_fillet:
            raise DeliverError(f"CHK-FILLET fail: build/export_check.json has non-OK fillet(s) "
                               f"{bad_fillets}; declare a limitation whose evidence names "
                               "export_check.json (stl-re-rebuild-build123d/SKILL.md:194).")

    if verdict == "BAND_NOT_MET" and not gate.get("miss_explanations"):
        raise DeliverError("qa/gate.json#miss_explanations is empty for BAND_NOT_MET; verdict.py should "
                           "have refused this already (SYNTHESIS F1). Return to stl-re-verify.")
    repro = docs["repro"]
    if repro.get("reproducible") is not True:
        raise DeliverError(
            "deliver/repro.json says the rebuild is not reproducible. Fix determinism in build/ "
            "(loop back to stl-re-rebuild-build123d); do not deliver a model that cannot be rebuilt."
        )
    check_repro_fresh(run, repro)

    R = Renderer(run, docs, files)
    part = lim.get("part") or {}
    name = part.get("name") or run.name
    regime = gate.get("regime") or {}

    # 1. headline ------------------------------------------------------------------------
    R.w(f"# {name} — STL → STEP reverse-engineering delivery", "")
    R.w(f"**Verdict: `{verdict}`** (from `qa/gate.json`; full reasoning in `qa/VERDICT.md`).  ")
    R.w(f"**Band regime:** {fmt(regime.get('name'))} — source `{fmt(regime.get('source'))}`.  ")
    sup = pf["checks"]["CHK-SUPERSEDED"]
    R.w(f"**Iteration:** {sup['iteration']} of {MAX_LOOPS} (earlier iterations kept: "
        f"{', '.join('`' + x + '/`' for x in sup['superseded']) or 'none'}).  ")
    indep = (gate.get("checks") or {}).get("CHK-INDEP")
    if indep:
        R.w(f"**Verification independence (CHK-INDEP):** {fmt(indep.get('result'))} — {fmt(indep.get('note'))}  ")
    else:
        # D2: CHK-INDEP is not always recorded as a named check; fall back to gate.json#independence
        # (verify's own free-text statement) rather than saying nothing about independence.
        R.w(f"**Verification independence:** {fmt(gate.get('independence')) or 'NOT DECLARED'}  ")
    R.w("")
    if verdict == "BAND_NOT_MET" and acc:
        R.w("> **A deviation band was NOT met.** Delivered only under the recorded human acceptance "
            f"below (by {fmt(acc.get('who'))}, {fmt(acc.get('date'))}, record `{acc.get('evidence')}`).", "")

    # 2. the part -------------------------------------------------------------------------
    R.h2("The part")
    photo = part.get("reference_photo")
    if photo:
        if not (run / photo).is_file():
            raise DeliverError(f"reference_photo {photo!r} does not exist in the run folder.")
        R.w(f"![reference photo](../{photo})", "")
    else:
        R.w("_No reference photo was supplied with the scan._", "")
    if part.get("what_it_is"):
        R.w(R.prose(part["what_it_is"], "part.what_it_is"), "")

    # 3. deliverables ---------------------------------------------------------------------
    R.h2("Deliverables")
    ex = docs["export"]
    frames = ex.get("exports", ex)
    rows = []
    for fr in ("datum", "scan"):
        e = frames.get(fr)
        if not isinstance(e, dict):
            raise DeliverError(f"build/export_check.json has no '{fr}' frame entry (run-contract §5, SYNTHESIS D14).")
        rows.append([f"`build/{e.get('step', '?')}`", fr, e.get("solids"), e.get("valid"), e.get("closed"),
                     e.get("faces"), e.get("volume_mm3"), e.get("bbox") if "bbox" in e else
                     [e.get("bbox_min"), e.get("bbox_max")]])
    R.table(["file", "frame", "solids", "valid", "closed", "faces", "volume mm³", "bbox mm"], rows)
    R.w("Source of the table: `build/export_check.json`. The editable design intent is `build/model.py` "
        "driven by `measure/params.json`.", "")

    # 4. method ---------------------------------------------------------------------------
    R.h2("Method")
    for i, step in enumerate(lim.get("method_summary") or [], 1):
        R.w(f"{i}. {R.prose(step, f'method_summary[{i}]')}")
    R.w("")

    # 5. frames ---------------------------------------------------------------------------
    al = docs["align"]
    R.h2("Coordinate frames")
    R.w("Two STEP files carry the same solid (SYNTHESIS D14): the **datum frame** (design frame, below) "
        "and the **scan frame** (the original STL coordinates; the CAD overlays the raw scan).", "")
    R.table(["element", "definition", "fit residual (rms / max mm)", "why"], [
        ["origin", fmt((al.get("origin") or {}).get("definition")), "—", "—"],
        [f"primary ({fmt((al.get('primary') or {}).get('type'))})", fmt((al.get("primary") or {}).get("mesh_region_desc")),
         f"{fmt((al.get('primary') or {}).get('fit_rms_mm'))} / {fmt((al.get('primary') or {}).get('fit_max_mm'))}",
         fmt((al.get("primary") or {}).get("why"))],
        [f"secondary ({fmt((al.get('secondary') or {}).get('type'))})", fmt((al.get("secondary") or {}).get("mesh_region_desc")),
         f"{fmt((al.get('secondary') or {}).get('fit_rms_mm'))} / {fmt((al.get('secondary') or {}).get('fit_max_mm'))}",
         fmt((al.get("secondary") or {}).get("why"))],
        ["clock", f"{fmt((al.get('clock') or {}).get('rule'))} (angle {fmt((al.get('clock') or {}).get('angle_deg'))}°)", "—", "—"],
    ])
    if isinstance(al.get("axes"), dict):
        R.table(["axis", "meaning"], [[k, fmt(v)] for k, v in al["axes"].items()])
    R.w(f"Measured tilt: {fmt((al.get('tilt_deg') or {}).get('value'))}° ({fmt((al.get('tilt_deg') or {}).get('method'))}). "
        f"Scale factor applied: {fmt(al.get('scale_factor'))}. "
        f"Scan noise floor: {fmt((al.get('scan_noise_mm') or {}).get('value'))} mm ({fmt((al.get('scan_noise_mm') or {}).get('method'))}).", "")
    if al.get("matrix_4x4"):
        R.w("Scan → datum matrix (row-major, `intake/alignment.json#matrix_4x4`); the scan-frame STEP uses its inverse:", "")
        R.w("```")
        for row in al["matrix_4x4"]:
            R.w("  ".join(f"{float(x): .6f}" for x in row))
        R.w("```", "")

    # 6. parameters -----------------------------------------------------------------------
    params = (docs["params"] or {}).get("params") or {}
    R.h2("Parameters")
    counts: dict[str, int] = {}
    for p in params.values():
        counts[str(p.get("source"))] = counts.get(str(p.get("source")), 0) + 1
    R.w("Sources: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) +
        f" (total {len(params)}). Rendered from `measure/params.json`; never edited by hand.", "")
    R.table(["name", "value", "unit", "measured", "rule", "source", "± mm", "critical", "evidence"],
            [[f"`{k}`", p.get("value"), p.get("unit"), p.get("measured"), p.get("rule"), p.get("source"),
              p.get("uncertainty_mm"), p.get("critical"), p.get("evidence")] for k, p in sorted(params.items())])

    # 6b. model tree (design intent) --------------------------------------------------------
    # D6: OD README.md:46-60 (6 features) and DRM README.md:27-54 (F01-F09 per part) both
    # deliver a feature tree; M02 README.md:12 states the editable source and that the STEP
    # carries no native feature history. `limitations.json#feature_tree` is optional (a run may
    # have none written yet), but when present it is rendered here rather than left to prose.
    ftree = lim.get("feature_tree") or []
    R.h2("Model tree (design intent)")
    R.w("The STEP is a neutral B-Rep; it carries no feature history. The editable design intent "
        "is `build/model.py` driven by `measure/params.json`, and the ordered feature plan is "
        "`build/MODELING_PLAN.md`.", "")
    if ftree:
        R.table(["id", "feature", "params"],
                [[f.get("id", i), f.get("feature"), fmt(f.get("params"))] for i, f in enumerate(ftree, 1)])
    else:
        R.w("_No `feature_tree` was declared in `deliver/limitations.json`; see `build/MODELING_PLAN.md` "
            "for the ordered feature plan._", "")

    # 7. tier-1 ---------------------------------------------------------------------------
    # Real shape (sim_caliper.py): {band_abs_mm, band_source, coverage:{gated,requested_total,
    # absent}, dims:{id: {name,caliper,cad,delta,pass,gated,unmeasurable?,grey_zone?,...}}}.
    R.h2("Tier-1 — caliper dims re-measured on the STEP")
    t1 = gate.get("tier1") or {}
    dims = t1.get("dims") or {}
    if dims:
        cov = t1.get("coverage") or {}
        R.w(f"Band: ±{fmt(t1.get('band_abs_mm'))} mm (`{fmt(t1.get('band_source'))}`, from "
            "`qa/gate.json#tier1.band_abs_mm`). Coverage: "
            f"{fmt(cov.get('gated'))} of {fmt(cov.get('requested_total'))} gated"
            + (f"; absent: {fmt(cov.get('absent'))}" if cov.get("absent") else "") + ".", "")
        rows = []
        for k, d in sorted(dims.items()):
            flags = []
            if d.get("unmeasurable"):
                flags.append("**UNMEASURABLE on the STEP**")
            if d.get("grey_zone"):
                flags.append("grey zone (margin < reading uncertainty)")
            res = "PASS" if d.get("pass") else "FAIL" if d.get("pass") is False else \
                ("ungated" if not d.get("gated") else "reported")
            rows.append([f"{k} {d.get('name', '')}", d.get("caliper"), d.get("cad"), d.get("delta"),
                        res, "; ".join(flags) or "—"])
        R.table(["dim", "caliper", "CAD re-measured", "Δ", "result", "flags"], rows)
        unmeasurable = [k for k, d in dims.items() if d.get("gated") and d.get("unmeasurable")]
        if unmeasurable:
            R.w(f"**{fmt(unmeasurable)} gated but not measurable on the STEP: this is a finding, "
                "never a silent pass (review V4).**", "")
    else:
        R.w("**Tier-1 not run: no caliper dimensions exist.** Every dimension is scan authority "
            "(or operator spec); see the source column in §5. Absent is not passed.", "")

    # 8. deviation ------------------------------------------------------------------------
    # Real shape (deviation_gate.py): `scan_to_cad`/`cad_to_scan` are UNMASKED; the masked
    # numbers are the separate `scan_to_cad_masked`/`cad_to_scan_masked` keys (review D1c). Never
    # swap those labels: that is exactly the CHK-MASK dishonesty this skill exists to prevent.
    R.h2("Deviation gate (scan ↔ CAD)")
    R.w(f"Regime **{fmt(regime.get('name'))}** (`{fmt(regime.get('source'))}`); bands: {fmt(regime.get('bands'))}.", "")
    dev = gate.get("deviation") or {}
    reg = dev.get("registration") or {}
    R.w(f"Registration: {fmt(reg.get('method'))}, iterations {fmt(reg.get('iterations'))}"
        f"{'/' + fmt(reg.get('max_iterations')) if reg.get('max_iterations') is not None else ''}, converged "
        f"{fmt(reg.get('converged'))}, correction {fmt(reg.get('delta_deg'))}° / {fmt(reg.get('delta_mm'))} mm.  ")
    R.w(f"Unobservable CAD fraction: {fmt(dev.get('unobservable_fraction'))}.", "")
    src = "`qa/gate.json#deviation`"
    R.table(["direction", *STAT_KEYS, "sampling", "source"], [
        stats_row("scan → CAD **unmasked**", dev.get("scan_to_cad"), src),
        stats_row("scan → CAD (masked)", dev.get("scan_to_cad_masked"), src),
        stats_row("CAD → scan **unmasked** (all)", dev.get("cad_to_scan"), src),
        stats_row("CAD → scan (masked)", dev.get("cad_to_scan_masked"), src),
        stats_row("CAD → scan (observable)", dev.get("cad_to_scan_observable"), src),
    ])

    # Gate table: the actual per-item PASS/FAIL the verdict was graded on (gate.json#gated_results,
    # verdict.py's own gated_results(); review D1d -- this was not rendered at all before).
    gres = gate.get("gated_results") or []
    if gres:
        R.w("### Gate results (what the verdict was graded on)", "")
        rows = []
        for g_ in gres:
            b = g_.get("result") or {}
            res = "PASS" if b.get("pass") else "FAIL" if b.get("pass") is False else "reported"
            s = g_.get("stats") or {}
            rows.append([g_["item"], f"p95 ≤{fmt(b.get('p95_band'))} / max ≤{fmt(b.get('max_band'))}",
                        f"p95 {fmt(s.get('p95'))} max {fmt(s.get('max'))} (n {fmt(s.get('n'))})", res])
        R.table(["item", "band", "measured", "result"], rows)

    zones = dev.get("zones") or {}
    if zones:
        R.w("### Per zone (unmasked and masked side by side)", "")
        rows = []
        for zn, e in sorted(zones.items()):
            for dn in ("scan_to_cad", "cad_to_scan"):
                if dn not in e:
                    continue
                bu, bm = (e[dn].get("band_unmasked") or {}), (e[dn].get("band_masked") or {})
                rows.append([zn, e.get("kind"), dn,
                            "PASS" if bu.get("pass") else "FAIL" if bu.get("pass") is False else "reported",
                            "PASS" if bm.get("pass") else "FAIL" if bm.get("pass") is False else "reported",
                            _s(e[dn].get("unmasked")), _s(e[dn].get("masked")), e.get("note") or "—"])
        R.table(["zone", "kind", "direction", "unmasked", "masked", "unmasked stats", "masked stats", "note"], rows)
    masks = dev.get("masks") or []
    R.w("### Masks (masked and unmasked are both shown above)", "")
    if masks:
        R.table(["mask", "direction", "why", "fraction removed", "stats inside"],
                [[m.get("name"), m.get("direction"), m.get("why"), m.get("fraction"), m.get("stats_inside")]
                 for m in masks])
    else:
        R.w("No masks were applied.", "")
    if dev.get("mask_dependent_passes"):
        R.w(f"**CHK-MASK: mask-dependent pass(es):** {fmt(dev['mask_dependent_passes'])}.", "")
    if dev.get("sensitivity"):
        rows_ = dev["sensitivity"]
        cols = sorted({c for r in rows_ for c in r if c != "zones"})
        R.w("### Mask sensitivity", "")
        R.table(cols, [[r.get(c) for c in cols] for r in rows_])
    # over_band_clusters is a dict keyed by direction (deviation_gate.py), not a list of rows.
    obc = dev.get("over_band_clusters") or {}
    for dn in ("scan_to_cad", "cad_to_scan"):
        ob = obc.get(dn)
        if not ob:
            continue
        dn_label = "scan → CAD" if dn == "scan_to_cad" else "CAD → scan"
        R.w(f"### Over-band point clusters, {dn_label} (> {fmt(ob.get('threshold_mm'))} mm)", "")
        R.w(f"{fmt(ob.get('n_over'))} points ({fmt(ob.get('fraction_over'))} fraction) in "
            f"{fmt(ob.get('n_clusters_ge_min'))} clusters ≥ {fmt(ob.get('min_pts'))} pts.", "")
        if ob.get("clusters"):
            expl = gate.get("cluster_explanations") or {}
            R.table(["#", "n", "centroid", "r range", "θ range (deg)", "d max", "explanation"],
                    [[i, c.get("n"), c.get("centroid"), c.get("r_range"), c.get("theta_deg_range"),
                      c.get("d_max"), expl.get(str(i), "**UNEXPLAINED**")] for i, c in enumerate(ob["clusters"])])
    da = gate.get("datum_audit") or {}
    if da.get("angle_deg") is not None:
        R.w(f"**Datum audit (report-only, QUESTIONS Q2):** angle {fmt(da.get('angle_deg'))}°, origin offset "
            f"{fmt(da.get('origin_offset_mm'))} mm, point disagreement p95 {fmt(da.get('point_disagreement_p95_mm'))} mm; "
            f"reference band {fmt(da.get('reference_band'))} ({'within' if da.get('within_reference') else 'OUTSIDE'}).", "")

    # 8b. band miss: where and what next (required for BAND_NOT_MET) ------------------------
    # D6/D2: OD README.md:43-44 and the honesty rule (RE_SPEC.md:181-183) give the miss a
    # per-region cause and options, not a bare "NOT MET" line. gate.json#miss_explanations is
    # verify's own structured record (verdict.py refuses BAND_NOT_MET without it).
    miss = gate.get("miss_explanations") or []
    if verdict == "BAND_NOT_MET" or miss:
        R.h2("Band miss: where and what next")
        R.table(["region", "cause", "options"],
                [[m.get("region"), m.get("cause"), fmt(m.get("options"))] for m in miss])
        if gate.get("band_fails"):
            R.w("Missed band(s): " + "; ".join(f"`{b}`" for b in gate["band_fails"]) + ".", "")

    # 9. checks ---------------------------------------------------------------------------
    checks = gate.get("checks") or {}
    R.h2("Named checks")
    R.table(["check", "stage", "ran", "result", "note"],
            [[k, "verify (`qa/gate.json#checks`)", c.get("ran"), c.get("result"), c.get("note")]
             for k, c in sorted(checks.items())] +
            [[k, "deliver (preflight)", c.get("ran"), c.get("result"), c.get("note")]
             for k, c in pf["checks"].items()])

    # 10. limitations ---------------------------------------------------------------------
    R.h2("Declared limitations (each with its re-run trigger)")
    if limits:
        R.table(["id", "limitation", "re-run trigger", "evidence"],
                [[L.get("id", f"L{i}"), R.prose(L["text"], f"limitations[{i}].text"),
                  R.prose(L["rerun_trigger"], f"limitations[{i}].rerun_trigger"), L.get("evidence", "—")]
                 for i, L in enumerate(limits, 1)])
    else:
        R.w("None declared (verdict APPROVED).", "")

    # 11. assumptions ---------------------------------------------------------------------
    R.h2("Assumptions and invented geometry")
    inv = [[f"`{k}`", p.get("value"), p.get("source"), p.get("evidence")]
           for k, p in sorted(params.items()) if p.get("source") in ASSUMED_SOURCES]
    if inv:
        R.w("Parameters not measured on the scan or by caliper (source tag from `measure/params.json`):", "")
        R.table(["parameter", "value", "source", "evidence"], inv)
    for i, a in enumerate(lim.get("assumptions") or [], 1):
        R.w(f"- {R.prose(a['text'], f'assumptions[{i}]')} _(source: {fmt(a.get('source'))}; {fmt(a.get('evidence'))})_")
    if not inv and not lim.get("assumptions"):
        R.w("Nothing unmeasured was invented.")
    R.w("")

    # 12. claim boundary ------------------------------------------------------------------
    R.h2("Claim boundary — what this result is NOT")
    for x in cb.get("not_fit_for") or []:
        R.w(f"- **Not fit for:** {R.prose(x, 'claim_boundary.not_fit_for')}")
    for x in cb.get("fit_for") or []:
        R.w(f"- Fit for: {R.prose(x, 'claim_boundary.fit_for')}")
    R.w(f"- The verdict covers only the Tier-1, deviation and named-check gates above, under the **{fmt(regime.get('name'))}** regime.", "")
    if gate.get("claim_boundary"):
        R.w(f"- Verify's own claim boundary (`qa/gate.json#claim_boundary`): {fmt(gate['claim_boundary'])}", "")

    if acc:
        R.h2("Human acceptance of the band miss")
        R.w(f"Accepted by **{fmt(acc.get('who'))}** on {fmt(acc.get('date'))} (`DECISIONS.md`, ACCEPT-BAND): "
            f"{fmt(acc.get('decision'))}. Record: `{acc.get('evidence')}` (sha256 `{sha256_file(run / acc['evidence'])}`).", "")

    # 13. reproduction --------------------------------------------------------------------
    R.h2("Reproduction")
    R.w("```")
    cmds = lim.get("repro_commands") or [
        "cd build && python model.py",
        "python <skills>/stl-re-deliver/scripts/repro_check.py --run <run>",
    ]
    for c in cmds:
        R.w(c)
    R.w("```", "")
    R.w(f"Fresh-process rebuild check (`deliver/repro.json`): reproducible **{fmt(repro.get('reproducible'))}**; "
        f"method {fmt(repro.get('method'))}; environment {fmt(repro.get('environment'))}.", "")
    rrows = []
    for f in repro.get("files") or []:
        rrows.append([f.get("file"), f.get("original_volume_mm3"), f.get("volume_abs_delta_mm3"),
                      f.get("bbox_max_abs_delta_mm"), f.get("faces_equal"), f.get("geometry_measurements_identical"),
                      f.get("raw_sha256_equal")])
    if rrows:
        R.table(["file", "volume mm³", "|Δ volume|", "max |Δ bbox|", "faces equal", "identical", "raw sha equal"], rrows)
        R.w("_Raw STEP hashes differ between runs because STEP headers carry a timestamp; the geometry is compared._", "")

    # 14. provenance ----------------------------------------------------------------------
    R.h2("Provenance of every number in this file")
    R.table(["file", "sha256"], [[f"`{p.relative_to(run).as_posix()}`", sha256_file(p)]
                                  for p in [*files.values(), limitations_path]])
    R.w("Generated by `stl-re-deliver/scripts/make_readme.py`. Do not edit numbers by hand; fix the JSON and re-render.")
    text = "\n".join(R.lines).rstrip() + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True, type=Path, help="run folder (run-contract §1)")
    ap.add_argument("--limitations", type=Path, default=None, help="default <run>/deliver/limitations.json")
    ap.add_argument("--out", type=Path, default=None, help="default <run>/deliver/README.md")
    a = ap.parse_args()
    run = a.run.resolve()
    lim = (a.limitations or run / "deliver" / "limitations.json").resolve()
    out = (a.out or run / "deliver" / "README.md").resolve()
    try:
        render(run, lim, out)
    except DeliverError as exc:
        fail(str(exc))
    print(f"wrote {out}")


if __name__ == "__main__":
    run_main(main)
