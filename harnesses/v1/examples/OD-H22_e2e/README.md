# OD-H22 3-way valve: v1 end to end (M3-lite)

The first run of the installable v1 harness, on the same scan as the v0 worked example
(`harnesses/v0/examples/OD-H22_3-way-valve/`).

## Stages

| Stage | What ran | Record |
|---|---|---|
| init | `init_run.py init` (v1) | `DECISIONS.md` |
| intake, measure | v0 OD-H22 artefacts reused, because these stages are unchanged in v1 and the scan is the same (sha256 4ebbb8c4…). `work.stl` was regenerated with v1 `intake.py stats`. The regime (baseline-skill plastic) and the scan-only decision are carried over from the owner's decisions of 2026-09-25. | `DECISIONS.md` |
| refine | `loop.py` from `build/base_tree.json` (flange prism + core revolve): 14 accepted features in 15 rounds, 239 candidate builds, 25 min. The result is identical to the M2.1 development run, so the loop is deterministic. | `refine/` |
| review | All 14 nodes kept. 7 low-gain clusters are left as open points, and 4 blend candidates are not modelled. | `DECISIONS.md` |
| build | `build_tree.py`: 1 valid closed solid, 109 analytic faces, 0 tree literals. | `build/` |
| verify | An independent sub-agent in a fresh context, with its own ICP, two-way deviation and `sky` observability. | `qa/gate.json`, `qa/VERDICT.md` |
| deliver | Not reached, because the verdict is REVISE. Deliver refuses it, which is the correct behaviour. The feature-tree repro path is covered by `stl-re-deliver/tests/test_tree_repro.py`. | – |
| metrics | `run_metrics.py` | `run_metrics.json` |

## Verdict: REVISE

Full-resolution scan, regime: plastic p95 ≤ 0.30 / max ≤ 0.80 mm.

- **scan→CAD:** p50 0.078, p95 0.435, max 2.285 mm unmasked. Masked: p95 0.417, max 2.285 mm.
- **Observable CAD→scan:** p95 0.777, max 4.209 mm. The unobservable fraction is 0.8 %.
  (v0's hand-built model: 1.484 / 4.858.)
- **Blocker:** QA's ICP did not converge. The step size cycles between 5e-6 and 5e-5 against
  a tolerance of 1e-6, at both 60 and 300 iterations. The correction is small: 0.136° /
  0.023 mm. The gate is labelled INVALID.

The verifier found these causes:
- **The 4 drive-tube slots are missing.** The loop found them, but each lowered J by only
  0.35–0.56 %. The low-gain rule (`--min-feature-gain` 1 %) with `--arbiter auto` left them as
  open points.
- **The gussets are missing.** This is refine open point 2.
- **The clip blocks and clip slots do not match the scan.**
- **The bore floor inside the drive tube is assumed.** There is no scan behind it.
- **No blends are modelled.**

**What a REVISE run would do:** `supersede --route geometry`, then re-run refine with
`--arbiter agent` (or with a lower `--min-feature-gain`) so the slots are added. It would also
need a fix for the gussets.
