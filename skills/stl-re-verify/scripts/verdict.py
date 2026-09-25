#!/usr/bin/env python3
"""Assemble qa/gate.json from the QA block files, check the proposed verdict against the evidence,
and render qa/VERDICT.md with every number read from gate.json.

Subcommands
  assemble  --qa <run>/qa   reads regime.json, hash_freeze.json, step_check.json, datum_audit.json,
                            tier1.json, registration.json, deviation.json, overlay*.json, review.json
                            -> gate.json (run-contract.md §6). Exit 2 if the proposed verdict is not
                            allowed by the evidence (the script never picks a friendlier verdict).
  render    --qa <run>/qa   gate.json -> VERDICT.md (structure: ../references/verdict-template.md)

Provenance: NEW CODE. Rules it enforces and their evidence:
  - regime declared at intake and named in the verdict, no silent default (QUESTIONS.md Q1, run-contract §9)
  - verdict vocabulary (run-contract §7; analysis/SKILL_ARCHITECTURE.md §4)
  - a miss is never loosened: any failed band => APPROVED* is refused (analysis/SYNTHESIS.md F1;
    facet-film T13/T16, analysis/baseline/facet-film-transferable.md)
  - mask-dependent pass => not APPROVED (CHK-MASK; OOM-B02 hex 1.624 unmasked)
  - every limitation carries a re-run trigger (SYNTHESIS F10; B02 "one caliper reading on F01")
  - decimated scan / unconverged ICP / changed hash => no official grade (golden-examples/README.md;
    re-qa-verifier ICP rule; M02 hash freeze)
  - numbers only from JSON (CHK-NUMBERS; B02 verdict drift <=0.02 mm)
  - datum audit and surface census are report-only (QUESTIONS.md Q2, Q3)
Deterministic: sorted iteration where order matters; no wall-clock in computation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CANONICAL_BAND_KEYS, RegimeError, band_result, header, normalise_bands, read_json, write_json  # noqa: E402

TOOL = "verdict.py"
VERDICTS = ("APPROVED", "APPROVED_WITH_LIMITATIONS", "BAND_NOT_MET", "REVISE", "HALT")
REVIEW_CHECKS = ("CHK-CIRCULAR", "CHK-LIKE4LIKE", "CHK-INDEP", "CHK-FILLET", "CHK-PATCHWORK", "CHK-ENUM",
                 "CHK-ACHIEVABLE", "PHOTO-PLAUSIBILITY")


def _opt(qa: Path, name: str) -> Any:
    p = qa / name
    return read_json(p) if p.is_file() else None


def _strip(block: Any) -> Any:
    if isinstance(block, dict):
        return {k: v for k, v in block.items() if k not in ("schema", "tool", "tool_version", "created")}
    return block


def gated_results(dev: dict[str, Any], regime: dict[str, Any], bands: dict[str, Any]) -> list[dict[str, Any]]:
    """Band results that the regime gates. Default: whole part both directions (CAD->scan on the
    observable subset when the split ran), plus every functional-interface AND whole-part zone
    (review V13).

    Bands are recomputed HERE from qa/regime.json's canonical keys (review V2), never trusted from
    deviation.json's cached `band_result`: deviation.json may have been produced by an earlier run
    of deviation_gate.py against a since-changed regime.json, and a stale cached pass must not
    survive into the verdict.
    """
    p95, mx, iface = bands["p95_mm"], bands["max_mm"], bands["interface_max_mm"]
    keys = regime.get("gated") or ["scan_to_cad:masked",
                                   "cad_to_scan_observable" if "cad_to_scan_observable" in dev
                                   else "cad_to_scan:masked"]
    out = []
    for k in keys:
        if k.startswith("zone:"):
            _, zn, dn = k.split(":", 2)                  # review V16: a zone name may contain ":"
            e = dev["zones"][zn]
            s = e[dn]["masked"]
            b = band_result(s, None, iface) if e["kind"] == "functional_interface" else band_result(s, p95, mx)
            out.append({"item": k, "result": b, "stats": s})
            continue
        if ":" in k:
            d, which = k.split(":", 1)
            s = dev[d] if which == "unmasked" else dev.get(f"{d}_masked", dev[d])
        else:
            s = dev[k]
        out.append({"item": k, "result": band_result(s, p95, mx), "stats": s})
    for zn, e in sorted(dev.get("zones", {}).items()):
        if e["kind"] not in ("functional_interface", "whole"):
            continue
        for dn in ("scan_to_cad", "cad_to_scan"):
            if dn not in e:
                continue
            s_m, s_u = e[dn]["masked"], e[dn]["unmasked"]
            if e["kind"] == "functional_interface":
                bm, bu = band_result(s_m, None, iface), band_result(s_u, None, iface)
            else:
                bm, bu = band_result(s_m, p95, mx), band_result(s_u, p95, mx)
            if bm is not None:
                out.append({"item": f"zone:{zn}:{dn}", "result": bm, "stats": s_m,
                            "unmasked": s_u, "band_unmasked": bu})
    return out


def assemble(qa: Path) -> int:
    regime = _opt(qa, "regime.json")
    review = _opt(qa, "review.json") or {}
    errors: list[str] = []
    if not regime or not regime.get("name") or not regime.get("source"):
        errors.append("regime.json missing or without name+source: the regime must be declared at intake "
                      "(QUESTIONS.md Q1). Ask the human; do not pick one.")
        regime = regime or {"bands": {}}
    # review V1/V2 + run-contract §12: read only the canonical flat band keys; refuse to grade
    # (error recorded here, verdict forced to null below) rather than fall back to a default.
    try:
        bands = normalise_bands(regime.get("bands", {}))
    except RegimeError as e:
        errors.append(f"regime.json: {e}")
        bands = {k: None for k in CANONICAL_BAND_KEYS}
    hf, sc, da = _opt(qa, "hash_freeze.json"), _opt(qa, "step_check.json"), _opt(qa, "datum_audit.json")
    t1, reg, dev = _opt(qa, "tier1.json"), _opt(qa, "registration.json"), _opt(qa, "deviation.json")
    dev_datum = _opt(qa, "deviation_datum.json")           # run-contract §12: builder-datum-frame stats
    overlays = [read_json(p) for p in sorted(qa.glob("overlays/*.json"))] + \
               [read_json(p) for p in sorted(qa.glob("overlay*.json"))]
    # review V9: an earlier deviation.json a --supersede run displaced is still shown, so a looser
    # or unmasked run cannot quietly disappear.
    deviation_runs = [{"file": p.name, "label": d.get("label"), "scan_to_cad": d.get("scan_to_cad"),
                       "cad_to_scan": d.get("cad_to_scan")}
                      for p in sorted(qa.glob("deviation_run*.json")) for d in [read_json(p)]]

    blockers: list[str] = []          # evidence problems, fixable by re-running QA/measurement:
                                       # counts toward the 3-loop limit (review V7)
    evidence_blockers: list[str] = [] # evidence is simply missing/invalid: HALT only, re-run QA;
                                       # does NOT count toward the 3-loop limit (review V7)
    geom_fails: list[str] = []        # review V6: geometry validity failures -> REVISE/HALT only,
                                       # never BAND_NOT_MET
    fails: list[str] = []             # band misses
    limits_auto: list[str] = []       # facts that force a declared limitation
    if hf is None or "after" not in hf:
        evidence_blockers.append("hash freeze not run before/after QA")
    elif not hf.get("unchanged"):
        evidence_blockers.append("STEP hash changed during QA")
    if sc is None:
        evidence_blockers.append("step_check not run")
    elif not sc["all_single_valid_closed_solid"]:
        # review V6: an invalid/non-closed solid can never be delivered as BAND_NOT_MET; it is a
        # geometry fail that only REVISE or HALT can follow (never "band accepted by a human").
        geom_fails.append("validity: not a single valid closed solid")
    if dev is None:
        evidence_blockers.append("deviation gate not run")
    else:
        # deviation_gate.py itself flags a missing "--registration" (run-contract §12, review V3:
        # verify always runs its own ICP, in every regime -- dropped the old RE_SPEC-only
        # condition) as an evidence problem: the run must simply be redone with the right inputs,
        # so it does not count toward the 3-loop limit. ICP non-convergence stays a normal blocker
        # (review V7): it may need re-measurement, not just a re-run.
        for reason in dev.get("gate_invalid_reasons", []):
            if "decimated" in reason:
                # DRM new-skill replay: a decimated-only scan is a declared LIMITATION, not a
                # blocker -- it must still be able to reach APPROVED_WITH_LIMITATIONS (the DRM
                # screw golden: scan-only, decimated, APPROVED_WITH_LIMITATIONS), never forced to
                # REVISE/HALT. Plain APPROVED stays out of reach because limits_auto is non-empty.
                limits_auto.append(f"{reason}; re-run trigger: full-res scan available")
            elif "no independent QA registration" in reason:
                evidence_blockers.append(reason)
            else:
                blockers.append(reason)
    if t1 is None:
        if bands.get("tier1_abs_mm") is not None:
            # review V4(ii): Tier-1 is per-dim, blocking whenever the regime bands it.
            blockers.append("Tier-1 not run, but the regime bands tier1_abs_mm: no Tier-1 grade is possible")
        else:
            limits_auto.append("no Tier-1 (no calipers run)")
    else:
        if t1.get("band_abs_mm") is not None and bands.get("tier1_abs_mm") is not None and \
                t1["band_abs_mm"] != bands["tier1_abs_mm"]:
            errors.append(f"tier1.json band_abs_mm {t1['band_abs_mm']} != regime.json tier1_abs_mm "
                          f"{bands['tier1_abs_mm']}: tier1.json was produced under a different regime")
        if t1.get("all_pass") is False:
            fails += [f"tier1 {k}: delta {v['delta']:+.4f} vs ±{t1['band_abs_mm']}" for k, v in sorted(t1["dims"].items())
                      if v.get("pass") is False]
        # review V4(i): a gated dim that cannot be measured on the STEP is a finding, not a silent
        # pass -- the verdict cannot be APPROVED while one exists.
        unmeasurable = [k for k, v in sorted(t1["dims"].items()) if v.get("gated") and v.get("unmeasurable")]
        if unmeasurable:
            blockers.append(f"tier1 not measurable on STEP: {', '.join(unmeasurable)}")
        if any(v.get("grey_zone") for v in t1["dims"].values()):
            limits_auto.append("tier1 grey zone: margin to band < reading uncertainty (facet-film T15)")
        if t1["coverage"].get("requested_total") and \
                t1["coverage"]["gated"] < t1["coverage"]["requested_total"]:
            limits_auto.append(f"tier1 partial: {t1['coverage']['gated']} of {t1['coverage']['requested_total']} gated")

    gres: list[dict[str, Any]] = []
    if dev is not None:
        gres = gated_results(dev, regime, bands)
        for g in gres:
            if g["result"] and g["result"]["pass"] is False:
                fails.append(f"{g['item']}: p95 {g['stats']['p95']:.3f} max {g['stats']['max']:.3f} vs "
                             f"{g['result']['p95_band']}/{g['result']['max_band']}")
        if dev.get("mask_dependent_passes"):
            limits_auto.append("mask-dependent pass: " + "; ".join(dev["mask_dependent_passes"]))
        if dev_datum is not None and bands.get("p95_mm") is not None:
            # run-contract §12: report stats in both the builder's datum frame and after ICP; a
            # large gap between the two is a datum finding, not silently absorbed by ICP.
            try:
                gap = abs(dev["scan_to_cad"]["p95"] - dev_datum["scan_to_cad"]["p95"])
                if gap > bands["p95_mm"]:
                    limits_auto.append(f"datum-frame vs post-ICP scan_to_cad p95 differ by {gap:.3f} mm "
                                       f"(> band {bands['p95_mm']} mm): large ICP correction is a datum finding")
            except (KeyError, TypeError):
                pass

    checks: dict[str, Any] = {}
    if dev is not None:
        checks["CHK-MASK"] = {"ran": True, "result": "finding" if dev["mask_dependent_passes"] else "pass",
                              "note": "; ".join(dev["mask_dependent_passes"]) or "no pass depends on a mask"}
        missing_why = [m["name"] for m in dev["masks"] if not m.get("why")]
        if missing_why:
            errors.append(f"masks without a 'why': {missing_why} (CHK-MASK)")
        cl = dev["over_band_clusters"]["scan_to_cad"]["clusters"]
        expl = review.get("cluster_explanations", {})
        unexpl = [i for i in range(len(cl)) if str(i) not in expl]
        checks["CHK-CLUSTER"] = {"ran": True, "result": "pass" if not cl else ("finding" if unexpl else "pass"),
                                 "note": f"{len(cl)} scan->CAD over-band clusters; unexplained: {unexpl}"}
    if overlays:
        empty = sorted({p for o in overlays for p in o.get("empty_scan_panels", [])})
        checks["CHK-OVERLAY"] = {"ran": True, "result": "finding" if empty else "pass",
                                 "note": ("no scan trace: " + ", ".join(empty)) if empty else "every panel shows scan"}
    else:
        checks["CHK-OVERLAY"] = {"ran": False, "result": "fail", "note": "no overlay panels produced"}
    tier1_miss = any(f.startswith("tier1 ") for f in fails)
    achievable_default = ({"ran": True, "result": "n/a", "note": "no Tier-1 miss to attribute (§4 CHK-ACHIEVABLE)"}
                          if not tier1_miss else {"ran": False, "result": "fail",
                                                   "note": "Tier-1 missed but CHK-ACHIEVABLE not recorded in review.json"})
    # DRM new-skill replay: a run with no photos has nothing for PHOTO-PLAUSIBILITY to check.
    # review.json declares this with an empty "photos" list; otherwise the check must be recorded.
    no_photos = review.get("photos") == []
    photo_default = ({"ran": True, "result": "n/a", "note": "no photos taken for this run"} if no_photos
                     else {"ran": False, "result": "fail", "note": "not recorded in review.json"})
    defaults = {"CHK-ACHIEVABLE": achievable_default, "PHOTO-PLAUSIBILITY": photo_default}
    for c in REVIEW_CHECKS:
        checks[c] = review.get("checks", {}).get(c, defaults.get(c, {"ran": False, "result": "fail",
                                                                      "note": "not recorded in review.json"}))
    for c, v in checks.items():
        if not v.get("ran"):
            errors.append(f"{c} not run")
    if checks.get("CHK-CIRCULAR", {}).get("result") == "fail":
        blockers.append("CHK-CIRCULAR: a gate checks the result against itself")
    if checks.get("CHK-LIKE4LIKE", {}).get("result") == "fail":
        errors.append("CHK-LIKE4LIKE: iteration comparison uses a changed protocol; label it, do not claim improvement")

    limitations = review.get("limitations", [])
    for L in limitations:
        if not L.get("rerun_trigger"):
            errors.append(f"limitation {L.get('id')} has no re-run trigger (SYNTHESIS F10)")
    verdict = review.get("verdict")
    allowed: set[str]
    if evidence_blockers:
        # review V7: evidence is simply missing or invalid (decimated scan, no ICP, hash changed,
        # step_check/deviation never run) -- HALT and re-run QA; this is not a measurement/geometry
        # fix, so it does not count toward the 3-loop limit.
        allowed = {"HALT"}
    elif geom_fails:
        # review V6: an invalid/non-closed solid can never reach BAND_NOT_MET (which implies a human
        # can accept the miss); only REVISE (fix the geometry) or HALT.
        allowed = {"REVISE", "HALT"}
    elif blockers:
        allowed = {"REVISE", "HALT"}
    elif fails:
        allowed = {"BAND_NOT_MET", "REVISE", "HALT"}
    elif limits_auto or limitations:
        allowed = {"APPROVED_WITH_LIMITATIONS", "REVISE", "HALT"}
    else:
        # review V8: nothing failed, so BAND_NOT_MET (a band was missed) cannot apply.
        allowed = {"APPROVED", "REVISE", "HALT"}
    if verdict not in VERDICTS:
        errors.append(f"review.json verdict {verdict!r} is not one of {VERDICTS}")
    elif verdict not in allowed:
        errors.append(f"verdict {verdict} not allowed by the evidence; allowed: {sorted(allowed)}")
    if verdict == "APPROVED_WITH_LIMITATIONS" and not limitations:
        errors.append("APPROVED_WITH_LIMITATIONS needs declared limitations in review.json")
    if limits_auto and verdict == "APPROVED_WITH_LIMITATIONS":
        declared = " ".join(L.get("text", "") for L in limitations).lower()
        if "mask" in " ".join(limits_auto) and "mask" not in declared:
            errors.append("a mask-dependent pass exists but no limitation mentions the mask")
    if verdict == "BAND_NOT_MET" and not review.get("miss_explanations"):
        errors.append("BAND_NOT_MET needs per-region miss_explanations with options (SYNTHESIS F1)")

    # review V12 / O-1 (orchestrate review): a refused verdict is never written into gate.json#verdict.
    # On refusal (errors non-empty) write verdict: null and keep the reviewer's proposal separately
    # under proposed_verdict, so a downstream reader (deliver, a human skimming gate.json) cannot
    # mistake a refused proposal for a trustworthy verdict.
    final_verdict = None if errors else verdict

    gate = {
        **header("gate", TOOL, [str(p) for p in sorted(qa.glob("*.json")) if p.name != "gate.json"], None),
        "regime": {"name": regime.get("name"), "source": regime.get("source"), "bands": regime.get("bands", {}),
                   "declared_in": regime.get("declared_in")},
        "hash_frozen": _strip(hf),
        "datum_audit": {**(_strip(da) or {}), "blocking": False} if da else {"ran": False, "blocking": False},
        "validity": _strip(sc),
        "surface_census": {k: v["surface_census"] for k, v in sc["steps"].items()} if sc else None,
        "tier1": _strip(t1),
        "registration": _strip(reg),
        "deviation": _strip(dev),
        "deviation_datum_frame": _strip(dev_datum),
        "deviation_runs": deviation_runs,
        "gated_results": gres,
        "overlays": [_strip(o) for o in overlays],
        "checks": checks,
        "blockers": blockers, "evidence_blockers": evidence_blockers, "geom_fails": geom_fails,
        "band_fails": fails, "auto_limitations": limits_auto,
        "limitations": limitations, "miss_explanations": review.get("miss_explanations", []),
        "claim_boundary": review.get("claim_boundary"), "independence": review.get("independence"),
        "cluster_explanations": review.get("cluster_explanations", {}),
        "allowed_verdicts": sorted(allowed), "proposed_verdict": verdict, "verdict": final_verdict,
        "errors": errors,
    }
    write_json(qa / "gate.json", gate)
    if errors and (qa / "VERDICT.md").is_file():
        # a stale VERDICT.md next to an erroring gate.json would let a reader trust an old verdict
        # that this assemble no longer stands behind.
        (qa / "VERDICT.md").unlink()
    print(f"regime {gate['regime']['name']} | blockers {len(blockers)} | evidence_blockers "
          f"{len(evidence_blockers)} | geom_fails {len(geom_fails)} | band fails {len(fails)} | "
          f"allowed {sorted(allowed)} | proposed {verdict} | verdict {final_verdict}")
    for e in errors:
        print("ERROR:", e)
    return 2 if errors else 0


def _s(s: dict[str, Any] | None) -> str:
    if not s or not s.get("n"):
        return "n 0"
    return f"n {s['n']} · rms {s['rms']:.3f} · p50 {s['p50']:.3f} · p95 {s['p95']:.3f} · p99 {s['p99']:.3f} · max {s['max']:.3f}"


def render(qa: Path) -> int:
    g = read_json(qa / "gate.json")
    if g.get("errors"):
        print("gate.json has errors; fix them before rendering:", *g["errors"], sep="\n  ")
        return 2
    L: list[str] = []
    rg, dev = g["regime"], g.get("deviation")
    L += [f"# VERDICT: {g['verdict']}", "",
          f"Regime: **{rg['name']}** ({rg['source']}); bands {rg['bands']}.",
          f"Independence: {g.get('independence') or 'NOT DECLARED'}", ""]
    if dev:
        L += [f"Scan: `{dev['scan']['path']}` ({'full-res' if dev['scan']['full_res'] else 'DECIMATED, inspection only'}), "
              f"label **{dev['label']}**.", ""]
    L += ["## Gate table", "", "| Gate | Band | Measured | Result |", "|---|---|---|---|"]
    hf = g.get("hash_frozen") or {}
    L.append(f"| Hash freeze | unchanged | {'unchanged' if hf.get('unchanged') else 'CHANGED/not run'} | "
             f"{'PASS' if hf.get('unchanged') else 'BLOCKER'} |")
    for st, v in ((g.get("validity") or {}).get("steps") or {}).items():
        vv = v["validity"]
        L.append(f"| Validity `{Path(st).name}` | 1 valid closed solid | solids {vv['counts']['solid']}, valid "
                 f"{vv['brepcheck_valid']}, naked edges {vv['naked_edges']}, V {vv['volume_mm3']:.3f} mm³ | "
                 f"{'PASS' if vv['single_valid_closed_solid'] else 'FAIL'} |")
    da = g.get("datum_audit") or {}
    if da.get("angle_deg") is not None:
        L.append(f"| Datum audit (report-only) | {da['reference_band']} | {da['angle_deg']:.3f}° / origin "
                 f"{da['origin_offset_mm']:.3f} mm / points p95 {da['point_disagreement_p95_mm']:.3f} max "
                 f"{da['point_disagreement_max_mm']:.3f} mm | {'within' if da['within_reference'] else 'outside'} (not blocking) |")
    t1 = g.get("tier1")
    if t1:
        for k, v in sorted(t1["dims"].items()):
            if v["caliper"] is None:
                L.append(f"| Tier-1 {k} {v['name']} | ungated | CAD {v['cad']:.3f} | reported |")
            else:
                res = "PASS" if v["pass"] else "FAIL" if v["pass"] is False else "reported"
                L.append(f"| Tier-1 {k} {v['name']} | ±{t1['band_abs_mm']} | caliper {v['caliper']} CAD {v['cad']:.3f} "
                         f"Δ {v['delta']:+.3f}{' (grey zone)' if v.get('grey_zone') else ''} | {res} |")
    if g.get("registration"):
        r = g["registration"]
        L.append(f"| Registration (ICP) | converged | {r['iterations']}/{r['max_iterations']} its, "
                 f"{r['delta_deg']:.3f}° / {r['delta_mm']:.3f} mm | {'PASS' if r['converged'] else 'INVALID'} |")
    for gr in g.get("gated_results", []):
        b = gr["result"] or {}
        res = "PASS" if b.get("pass") else "FAIL" if b.get("pass") is False else "reported"
        L.append(f"| {gr['item']} | p95 ≤{b.get('p95_band')} / max ≤{b.get('max_band')} | {_s(gr['stats'])} | {res} |")
    L += [""]
    if dev:
        L += ["## Deviation detail (masked and unmasked side by side)", "",
              f"- scan→CAD unmasked: {_s(dev['scan_to_cad'])}", f"- scan→CAD masked: {_s(dev['scan_to_cad_masked'])}",
              f"- CAD→scan unmasked: {_s(dev['cad_to_scan'])}", f"- CAD→scan masked: {_s(dev['cad_to_scan_masked'])}"]
        if "cad_to_scan_observable" in dev:
            L.append(f"- CAD→scan observable only: {_s(dev['cad_to_scan_observable'])}; unobservable fraction "
                     f"{100 * dev['unobservable_fraction']:.2f} %")
        L += ["", "Masks:", ""] + [f"- **{m['name']}** ({m['direction']}): {m['why']}; fraction "
                                     f"{100 * m['fraction']:.2f} %; inside {_s(m['stats_inside'])}" for m in dev["masks"]]
        if not dev["masks"]:
            L.append("- none")
        L += ["", "Zones:", ""]
        for zn, e in dev["zones"].items():
            for dn in ("scan_to_cad", "cad_to_scan"):
                if dn in e:
                    L.append(f"- {zn} [{e['kind']}] {dn}: unmasked {_s(e[dn]['unmasked'])} | masked {_s(e[dn]['masked'])}")
        ob = dev["over_band_clusters"]["scan_to_cad"]
        L += ["", f"Over-band scan→CAD points (> {ob['threshold_mm']} mm): {ob['n_over']} "
                  f"({100 * ob['fraction_over']:.3f} %) in {ob.get('n_clusters_ge_min', 0)} clusters ≥ {ob['min_pts']} pts.", ""]
        for i, c in enumerate(ob["clusters"]):
            L.append(f"- cluster {i}: n {c['n']}, centroid {c['centroid']}, r {c['r_range']}, θ {c['theta_deg_range']}, "
                     f"max {c['d_max']:.3f} — {g['cluster_explanations'].get(str(i), 'UNEXPLAINED')}")
    L += ["", "## Checks", "", "| Check | Result | Note |", "|---|---|---|"]
    L += [f"| {k} | {v['result']} | {v.get('note', '')} |" for k, v in g["checks"].items()]
    if g["band_fails"] or g["miss_explanations"]:
        L += ["", "## Misses, per region", ""] + [f"- {f}" for f in g["band_fails"]]
        L += [f"- **{m.get('region')}**: {m.get('cause')} Options: {m.get('options')}" for m in g["miss_explanations"]]
    L += ["", "## Declared limitations (each with its re-run trigger)", ""]
    L += [f"{i + 1}. {x['text']} — **Re-run trigger:** {x['rerun_trigger']}" for i, x in enumerate(g["limitations"])] or ["None."]
    if g["blockers"]:
        L += ["", "## Blockers (no official grade)", ""] + [f"- {b}" for b in g["blockers"]]
    L += ["", "## Claim boundary", "", g.get("claim_boundary") or "NOT STATED", "",
          f"_All numbers above are read from `qa/gate.json` (CHK-NUMBERS). Allowed verdicts given the evidence: "
          f"{', '.join(g['allowed_verdicts'])}._", ""]
    (qa / "VERDICT.md").write_text("\n".join(L), encoding="utf-8")
    print("wrote", qa / "VERDICT.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["assemble", "render"])
    ap.add_argument("--qa", required=True, help="the run's qa/ folder")
    a = ap.parse_args(argv)
    qa = Path(a.qa)
    return assemble(qa) if a.cmd == "assemble" else render(qa)


if __name__ == "__main__":
    raise SystemExit(main())
