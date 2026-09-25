# DRM screw cap blind replay — honest report

Part: Dreame brush screw cap (pentagon body, double-D drive hole, web bore + counterbore). This
report compares the golden record, a blind replay of the new `stl-re-*` skills, and a blind
replay of the baseline skill.

Replay artifacts (reports, gate.json, verdicts) are copied under `evals/replay/artifacts/`. Paths below like `B02/new_run/qa/gate.json` map to `artifacts/B02/new/gate.json`.

## 1. Setup

- **Inputs given to each blind run:** a **decimated** scan only (`DRM/new_run/input/scan.stl`,
  949,999 faces, 1,017 fragment bodies, largest kept at 931,220 faces) — the original full-res
  scan (1,831,231 faces per the golden, `analysis/golden/dreame_brush-caps.md` §1) was withheld.
  Inspection-only was declared as an owner decision (`DRM/new_run/DECISIONS.md` OTHER entry). No
  calipers and no photos exist (`DECISIONS.md` MEASUREMENTS entry).
- **New skills used:** `stl-re-intake-datum`, `stl-re-measure-intent`, `stl-re-rebuild-build123d`,
  `stl-re-verify`, orchestrated by `stl-re-orchestrate`. Frozen at commit `ccbb063` — before the
  Phase 4 review-fix commits.
- **Baseline skill used:** `baseline/skills/stl2step-build123d`, one agent, no separate
  intake/measure/verify stages (`baseline_notes.md`).

## 2. Side-by-side

| Item | Golden (`analysis/golden/dreame_brush-caps.md`) | New skills (`DRM/new_run/...`) | Baseline (`baseline_notes.md`, `gate_drm.json`) |
|---|---|---|---|
| Datum choice / clock | Peak-area offset bin near an approximate normal + RANSAC+SVD; pentagon 5-fold phase clock, mode `pent@zc`, **−34.23°** (`screw_alignment.json#clock_deg`) | RANSAC+SVD top-face plane, rms 0.00715 mm; `polygon_flat` n=5 clock, **−34.081°** (`DRM/new_run/intake/alignment.json`) | Largest-flat RANSAC 33.6 mm² rms 0.007; one flat normal on +X, **−2.69°** (different clock convention/feature) |
| Tilt handling | `tilt_deg` **hard-coded to 0.0**; bore axis assumed parallel to the plane normal, never measured (`align.py:79`) | CHK-TILT finding: bore alone 2.08°±0.31° (too short, untrustworthy); bore+double-D 0.64°±0.09° over 4.45 mm but that spec STOPs the check; not re-levelled (`DRM_new_report_saved.md` §2) | Bore axis tilt 0.51° (measured, but no cross-check against a second feature) |
| Double-D / bore | Bore r_mean 1.873 (10 stations); double-D arc r 1.949, flats 3.28 A/F (`screw_alignment.json#bore`, README F06) | Bore r 2.0439±0.0071 (9 stations); double-D arc R 1.962, half-flats 1.635 (`DRM_new_report_saved.md` §3) | Lower bore Ø3.9 + double-D 3.3 at 52.5° |
| Pentagon apothem | 4.48–4.52 measured → 4.50 (README F01) | 4.497–4.515 measured → 4.506 (`DRM_new_report_saved.md` §3, F01) | Pentagon apothem 4.50 |
| Feature count / faces | 56 faces, 1 solid (README; NX import 0 faults) | 98 faces, 1 valid closed solid both frames, V 268.40 mm³ (`DRM/new_run/qa/gate.json#validity`) | 36 faces, 1 valid solid, V 267.35 mm³ |
| Fillets | R1.15 chamfer-corner fillet, standard rounding (README F03) | Bore ceiling 0.203, bore entry 0.216, double-D top 0.198, bottom outer 0.528: OK; **transition 0.548→0.3 REDUCED**, declared (`DRM_new_report_saved.md` §3, F08) | R0.5 / R0.3 rounds, no declared reduction |
| Band / regime | p95≤0.30 / max≤0.80, "repo re-deviation gate, consumer plastic" (`screw_official_gate.json#limits`) | baseline-skill regime, same p95≤0.30/max≤0.80 (`DRM/new_run/intake/regime.json`) | Same consumer-plastic band |
| scan→CAD p95/max | 0.0851 / 0.2448 (50k official gate, full-res raw scan) (`screw_official_gate.json#scan_to_cad`) | 0.078 / 0.309 (475,724 pts, decimated scan, **inspection only**) (`qa/gate.json`) | 0.1445 / 0.2573 |
| CAD→scan p95/max | 0.0757 / 0.2683 (`screw_official_gate.json#cad_to_scan`) | Observable 0.066 / 0.277 (masked 0.061/0.272) (`qa/gate.json`) | 0.1322 / 0.2322 |
| Masks | None recorded for the screw part (only the snap sibling used masks) | M1 open boundary 0.5 mm, 23.2% fraction (`qa/gate.json#masks`) | 65 debris fragments dropped (main-component only) |
| Named interfaces | Not itemised for the screw part beyond the whole-part gate | Z-DD (double-D) 0.195/0.170 max, Z-BORE 0.092/0.091 max, both PASS, unmasked (`qa/gate.json#zones`) | not produced |
| Registration/ICP | `registration_converged: true`, method not recorded (`screw_official_gate.json`) | Not converged at the 60-iteration default cap; converged at 90/200, correction 0.242°/0.035 mm (`DRM/new_run/qa/registration_cap60.json`) | not produced |
| Datum audit | Not run for either part (no F00 independent audit in this golden) | 1.262° (clock only)/origin 0.0015 mm, outside the ≤0.3° reference (`qa/gate.json#datum_audit`) | not produced |
| Tier-1 | Not run (no calipers, README assumptions) | 0/10 requested dims gated, all ABSENT (`qa/VERDICT.md`) | not produced |
| Verdict | PASS (official gate `overall_pass: true`, `screw_official_gate.json`) | **HALT** — decimated scan is the only blocker; all inspection bands pass unmasked (`qa/VERDICT.md`) | PASS (plastic band, "barely" for the machined band per `baseline_notes.md`) |

## 3. What the new skills did better, and worse

Better: the new run correctly refused to grade on a decimated scan and returned an honest **HALT**
rather than a false PASS, per the skill's own decimated-scan rule — this is the single reason for
the verdict, stated plainly ("Only blocker: the scan is decimated → inspection only. Every
inspection band passes, unmasked", `DRM_new_report_saved.md` header). The new run's inspection
numbers (p95 0.078/max 0.309 mm, `qa/gate.json`) are close to the golden's official full-res
numbers (p95 0.0851/max 0.2448 mm) despite working from a lower-resolution mesh with 1,017
fragment bodies, which suggests the datum and rebuild methods generalised reasonably well. It also
measured bore-axis tilt explicitly (two ways, and flagged the shorter span as untrustworthy)
where the golden's own `align.py` hard-codes `tilt_deg = 0.0` and never actually measures it
(`analysis/golden/dreame_brush-caps.md` §3.3, lesson 4) — a real improvement in honesty over the
golden method itself.

Worse: the new run's fillet handling silently reduced a transition fillet from 0.548 to 0.3 mm and
only declared it after the fact (`DRM_new_report_saved.md` §3, F08), a fallback pattern the golden
also uses but logs per-feature OK/FAILED (`analysis/golden/dreame_brush-caps.md` §6, "every
fillet/chamfer is wrapped in try/except and logs OK or FAILED"). The new run's ICP did not
converge at the skill's own 60-iteration default and needed 90 (`registration_cap60.json`), a gap
the skill's own documentation had already flagged as a known DRM failure mode before this replay
(`DRM_new_report_saved.md` D7). And critically, **the DRM new run said HALT only because of the
decimated-scan rule** — nothing about the geometry itself needed fixing, and the report says so
directly ("REVISE would be dishonest, since nothing in the geometry needs fixing",
`DRM_new_report_saved.md` §5). That is a correct, honest outcome, but it also means this replay
never tested whether the new skills would have reached the golden's PASS verdict on the actual
full-resolution scan.

## 4. Integrity caveats

- **Not fully blind.** Defect **D1** in `DRM_new_report_saved.md`: `stl-re-intake-datum/references/datum-cookbook.md`
  §2.1 and `SKILL.md` step 8 give this part's exact pentagon clock (−34.23°), double-D radius
  (1.873), bottom z (−5.12) and tilt (0.72°); `stl-re-rebuild-build123d/SKILL.md` gives the DRM
  feature tree; `orchestrate/references/verdict-examples.md` gives the DRM gate numbers; the agent
  reports its own numbers disagree in places (clock −34.08° vs −34.23°, panels vs a dimple) but
  cannot claim the run was blind.
- **CHK-INDEP:** verify ran in the same agent context that built the model, no subagent tool was
  available (`DRM/new_run/DECISIONS.md` INDEP entry).
- **The baseline agent built its own gate.** The baseline notes do not report an OOM for DRM
  specifically (that happened on B02); the DRM baseline gate (`gate_drm.json`) was produced by the
  agent's own script, not an official tool, same caveat as B02.
- **The gate code differs between runs.** The golden used an external tool,
  "oguz-re-deviation-report-v0" (50k samples, method and registration undocumented,
  `analysis/golden/dreame_brush-caps.md` Questions 4); the new run used `stl-re-verify`'s
  `deviation_gate.py` on 475,724 raw points; the baseline used a hand-written KD-tree script that
  dropped 65 debris fragments. None of the three ran on the same scan resolution as another —
  the golden ran on the full-res raw scan (1,831,231 faces), the new run and baseline both ran on
  the decimated scan (949,999 faces) — so the numbers above are directionally comparable only, not
  strictly like-for-like.

## 5. Skill defects found, and current status

Known fixed (Phase 4, before this replay's commit or by later commits on this branch):
- **Band-key mismatch** (D1 in this report: intake wrote `p95_mm`/`max_mm` for baseline-skill,
  verify read `p95`/`max`, so the whole-part gate silently never ran and printed `p95 ≤None`) —
  **fixed**. `intake.py` writes canonical band keys and `verify`'s `normalise_bands()` refuses an
  unrecognised key (`skills/stl-re-intake-datum/scripts/intake.py:301-317`; `reviews/stl-re-verify.md` V1).
- **sim_caliper inside mode** — not directly exercised on DRM (no calipers were used), but the
  same defect (**fixed** in measure round 1, `reviews/stl-re-measure-intent.md` B1) would have
  affected this part's bore measurement had calipers existed.
- **Decimated-scan inspection-only path** (D3 in this report: the orchestrator had no path for an
  owner with only a decimated scan) — **fixed**, `stl-re-orchestrate/SKILL.md` row added in commit
  `a542434`.
- **Extrude taper note** (D11: `extrude(taper=)` produces B-spline side faces on planar draft
  surfaces, inflating the surface census) — **fixed**, added to
  `skills/stl-re-rebuild-build123d/references/build123d-idioms.md` in commit `a542434`, explicitly
  from this DRM replay ("taper idiom from DRM replay", commit message).

Fix in progress (verify round 1) — code changes exist in the working tree as of this replay but
are uncommitted:
- **datum_audit wall/clock/crash** (D4a: `wall: "inner"` on a bore-only selection raised
  `ZeroDivisionError`; D4b: the Fourier clock applied `offset_deg` after picking the nearest
  candidate, picking the wrong flat by 73.26°) — `skills/stl-re-verify/scripts/datum_audit.py` now
  adds a `single_wall` escape and folds `offset_deg` in before the nearest-candidate choice.
- **PHOTO-PLAUSIBILITY with no photos** (D5: `verdict.py` refused `ran=false` even with zero
  photos) — `verdict.py` now defaults to `n/a` when `review.json#photos == []`.
- **ICP cap guidance** (D7: the default 60-iteration cap is known to fail on DRM, needing 90) —
  `SKILL.md` §5 now requires recording the reason for any raised cap, rather than silently raising
  it until it passes.

Open:
- **Answer-key leakage (D2/D1).** Confirmed still present in `datum-cookbook.md`, `SKILL.md` and
  `references/verdict-examples.md`, as quoted above. **Scrub planned.**
- **The cut-removes-volume check (D12 in the sibling B02 report; same rebuild skill).** No
  `assert` for "every cut removes volume" was found in `skills/stl-re-rebuild-build123d/`. Still
  **open**.
- **`init_run.py status` ignores DECISIONS.md (D6).** Confirmed: `init_run.py:335-338` checks only
  whether `input/MEASUREMENTS.md` exists on disk, never whether a MEASUREMENTS decision has
  already been recorded in `DECISIONS.md`. Still **open**.
- **Negative-range argparse examples (D9).** Confirmed: `sections.py --z-band`, `--theta-band` and
  `fits.py --z`/`--r` still take `lo,hi` with no `=` guidance, and this argument shape breaks
  argparse on a negative `lo` (every datum-frame part below z=0, including this one, z −5.107 to
  −0.487). This was explicitly **skipped** in the measure-intent round-1 fix
  (`reviews/stl-re-measure-intent.md` m8). Still **open**.

Other defects from this replay checked against the branch:
- **D8 (`overlay.py` has no `--registration`, so overlays are drawn pre-ICP while the gate is
  post-ICP)** and **D12 (the STOP check on a symmetric, non-circular origin feature like the
  double-D is structurally circular)**: not found addressed in any commit or diff on the branch.
  Still **open**.
- **D10 (`param_table.py` rounding rules mismatch units for dimensionless slopes)**: partially
  touched by measure's round-1 M2/M3 fixes (element-wise list validation, `mean-of-n` branch,
  `reviews/stl-re-measure-intent.md`), but the unit-mismatch case for a draft slope stored as "mm"
  is not named in that review. Treated as **open**.
