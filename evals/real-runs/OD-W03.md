# Real run: OD-W03 water tank valve (2026-09-28)

The second real run of the v1 skills, on a part with no golden record. Ikbal supplied a scan and
one catalogue photo. There were no calipers. Records are copied under `OD-W03/`, including the
verifier's workaround scripts (`OD-W03/qa_scripts/`). The full run folder was delivered as
`OD-W03_RE_BAND_NOT_MET_2026-09-28.zip` (deliverables + all sources, `package_zip.py`).

## Inputs and decisions
- Scan: 400,657 faces, one body, not watertight, 25 open loops, mean edge 0.184 mm. Only the outer
  skin was scanned: no underside, no cup/boss interiors. Ikbal confirmed it is the original
  full-resolution export (decision card).
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm ("p95 plastik parça toleransı").
- No calipers (decision card: scan-only). The photo has no scale reference.
- Interior design intent: hollow moulded shell with assumed 1.2 mm walls (decision card; the
  alternative was a solid body closed at the skirt).

## Result
- Datum: flange top (z = 0); origin = midpoint of the two cup axes; +X from cup A to cup B.
  Needed two new `align.py` options (defects 1–2 below). The first cup-wall datum STOPped on
  0.0815 vs 0.0708 (barb circle noise). Barb shanks as the origin were worse (0.089), so the run
  took the self-referential noise path (OD-H22 D1 precedent) and recorded it in `DECISIONS.md`.
- Measure: 45 params, `param_table.py` valid with 0 warnings. Cup A/B and ear −X/+X kept as
  per-instance lists, because they differ beyond noise. After a builder self-check (scan→CAD
  p95 0.308), the cup and boss tops were re-measured as cones (8.5° / 3.7°); self-check p95
  then 0.299.
- Build: one valid closed solid, 106 faces (98.6 % analytic), all 5 fillets at target, reproducible.
- Independent verify (fresh agent, own ICP 0.086° / 0.027 mm, datum audit 0.020° / 0.003 mm):
  - scan→CAD unmasked p95 0.320 / max 1.113; masked (M1 barb-tip bridging film, M2 tab/lug
    junk facets) p95 0.307 / max 0.785. **p95 misses in both.**
  - observable CAD→scan p95 1.512 / max 3.063: the invented hollow interior, which the ray test
    counts as observable through the open underside (only 1.35 % unobservable).
- Verdict `BAND_NOT_MET`. Options offered: REVISE (cup B upper wall reads ~0.11 short; p95 would
  still be marginal and CAD→scan unchanged), accept, HALT. Ikbal accepted now (`ACCEPT-BAND`
  cites gate `2fe9569f1fa0`).

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-intake-datum/scripts/align.py` origin | The pooled median over two origin features lands on the centre of whichever feature keeps more stations, not their midpoint | fixed: `origin.combine: "midpoint"` |
| 2 | `stl-re-intake-datum/scripts/align.py` clock | No two-feature clock; `fourier_mass` n=2 was 0.7° off the cup line (necks, ears, webs) | fixed: `clock.rule: "feature_line"` |
| 3 | `stl-re-verify/scripts/tier2_icp.py:52` | The normal-agreement test ignores sign, so the inner walls of a hollow CAD pair with the outer scan skin; ICP converged to a +z 0.659 mm shifted frame (p95 0.588 there) | open; workaround `OD-W03/qa_scripts/tier2_icp_signed.py` |
| 4 | `stl-re-verify/scripts/datum_audit.py:163-251` | No two-circle midpoint origin and no `feature_line` clock (mirror of 1–2) | open; workaround `OD-W03/qa_scripts/datum_audit_pair.py` |
| 5 | `stl-re-verify/scripts/observability.py` | Unscanned surfaces with a line of sight (open underside, bores) count as observable; same as OD-H22 #3 and again the main CAD→scan driver | open |
| 6 | `stl-re-verify/scripts/sim_caliper.py:92-95` | `outermost` picks the loop farthest from the origin, which can be another body; an empty region then crashes `jaws()` (line 58) | open |
| 7 | `stl-re-verify/scripts/deviation_gate.py` | `mask_dependent_passes` does not flag a max that passes only masked while the p95 of the same band fails | open |
| 8 | `stl-re-verify/scripts/overlay.py` | No `--registration` option, so overlays are always in the builder's frame | open |
| 9 | `stl-re-verify/scripts/verdict.py render` | The datum-frame result and `deviation_runs` are left out of VERDICT.md | open |
| 10 | `stl-re-intake-datum/scripts/align.py` STOP rule | No tie margin (OD-H22 D1 again): a 0.011 mm excess stopped a datum whose per-cup centres scatter ≤ 0.007 mm | open |
| 11 | `stl-re-deliver/scripts/package_zip.py` | The 25 MB cutoff shipped two 20 MB working meshes and three 16 MB `qa/dev_arrays*.npz` dumps (an 82 MB zip) | fixed: default 10 MB, `qa/dev_arrays*.npz` regenerable (11 MB zip) |
| 12 | `stl-re-deliver/scripts/make_manifest.py` | `decisions/*` (ACCEPT-BAND evidence) had no role (`unclassified`) | fixed |

Method notes for the next scan-only job on a shell-only scan: the owner's interior choice decides
the CAD→scan outcome before any geometry is built. Say so when you ask, and expect
`BAND_NOT_MET` until defect 5 is fixed.
