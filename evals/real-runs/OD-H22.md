# Real run: OD-H22 DeLonghi 3-way valve (2026-09-25)

The first run of the v1 skills (HEAD `b8d9c97`) on a part with no golden record. Ikbal supplied a
scan and four product photos. There were no calipers. Records are copied under `OD-H22/`; the full run
folder (with the STEP files) lives in the project's shared files.

## Inputs and decisions
- Scan: 495,881 faces, one body, not watertight, 40 × 42 × 48 mm, mean edge 0.154 mm.
  Ikbal confirmed it is the original full-resolution export (decision card, 11:41).
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm, confirmed by Ikbal (decision card, 10:54).
- No calipers, so Tier-1 did not run. The photos are catalogue images without a scale reference.

## Result
- Build: one valid closed solid, 162 faces, all analytic, 12 features. All 5 fillets were built at
  their target radius. The build took one loop.
- Independent verify (a separate agent with its own ICP; ICP delta 0.384° / 0.014 mm):
  - scan→CAD: p95 0.235 (passes), max 1.427 (misses). The max comes from about 130 scan
    points inside the +X ear hole, which the photos show open, so it is probably a scan artefact.
  - Observable CAD→scan: p95 1.484 / max 4.858 (misses). Almost all of it is interior bore,
    slot and port surfaces that the scanner never reached.
  - Datum audit (report-only): 0.216° / 0.046 mm.
- Verdict: `BAND_NOT_MET`. Ikbal accepted it for delivery (decision card, 11:48; `ACCEPT-BAND`
  cites the gate sha256 `89a14a86f4d4…`). Deliver produced README, MANIFEST and repro.json
  (reproducible).
- The builder's self-check agreed with verify on the raw numbers. Its "damaged ear excluded"
  figure (max 0.765) came from a zone much wider than the one declared at intake. Verify did not use it.

## Skill defects found (status on this branch)

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-verify/scripts/deviation_gate.py:190`, `tier2_icp.py:92` | No `unknown` scan kind, so the verifier had to use `decimated` for the inspection-only label | open |
| 2 | `stl-re-verify/scripts/verdict.py` | The reason for the verdict is not carried into VERDICT.md (it had to be added as a miss entry) | open |
| 3 | `stl-re-verify/scripts/observability.py` (ray test) | Open-mouthed bores the scanner never reached count as observable, so CAD→scan "observable" is inflated | open; this was the main driver of the CAD→scan miss |
| 4 | `stl-re-intake-datum/scripts/align.py:404` | The datum STOP check has no tie margin, so a clean face stopped the run | open |
| 5 | `stl-re-measure-intent/scripts/param_table.py:37-44,199-200` | Some checks still use the mean of a per-instance list | open |
| 6 | `stl-re-intake-datum/scripts/intake.py` | Cannot re-open its own freshly written work.stl on a FUSE mount; ran in a scratch mirror | open (environment) |
| 7 | `stl-re-deliver/scripts/repro_check.py` | `--cmd` could not carry a command with its own flags | fixed: command after a bare `--` |
| 8 | `stl-re-deliver/scripts/make_readme.py` | CAD→scan cluster rows showed the scan→CAD cluster explanations | fixed: explanations looked up per direction; README regenerated |

The builder also logged smaller items in `OD-H22/BUILDER_REPORT.md`: fits.py arc fits,
pattern_count's mass signal, and negative-number CLI arguments.
