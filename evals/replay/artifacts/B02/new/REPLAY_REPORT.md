# REPLAY REPORT: OOM-B02 side brush (3 arms), blind replay of the `new_skills` pipeline

Run folder: `B02/new_run/`. Iterations: 2 of 2 (the owner's time-box; the skill allows 3). it1 is kept intact in `_it1_SUPERSEDED/`.
**Final verdict: `BAND_NOT_MET`** under the RE_SPEC regime. No human acceptance exists, so `deliver/` was not created.
Every number below is copied from the run's JSON files (`intake/*.json`, `measure/params.json`, `qa/gate.json`, `qa/deviation.json`).

---

## 1. Intake card summary (`intake/INTAKE_CARD.md`)

- **Scan.** `input/scan.stl`, sha256 `05a62a32…2714`, 798,874 faces, 1 body, not watertight, 16 open loops.
  - Normals: outward by ray vote (7 % along the normal, 73.2 % against it). The signed volume of −2434 mm³ was ignored because the mesh is open.
  - Work copy: 199,999 faces. Work-vs-full deviation p95 0.0034 mm, max 0.137 mm.
- **Regime.** RE_SPEC, declared at intake in `intake/regime.json` and in the `REGIME` line of `DECISIONS.md`.
  - Tier-1 ±0.15.
  - Tier-2 p95 ≤ 1.6 / max ≤ 4.0.
  - Interfaces max ≤ 0.8.
- **Measurements.** No caliper session (owner decision; `MEASUREMENTS` entry). The 12 photo readings were transcribed into `input/MEASUREMENTS.md`:
  - 7 are rigid and owner-confirmed.
  - D-04 is soft.
  - 4 are unassigned (D-06, 09, 10, 12) and were not used.
- **CHK-SCALE.** FLAG: there are 0 envelope dimensions, so no scale was applied.
  - D-03 ratio 1.001, D-08 ratio 0.999.
  - D-02 ratio 0.943: thin-section dilation.
  - D-01 is not a like-for-like pair.
- **Noise floor.** 0.0185 mm rms on the rim annulus (RANSAC+SVD, 6,085 faces). This is the same surface as the primary datum, so the STOP rule is trivially met.
- **Features (CHK-ENUM pass, 12 features).**
  - Rim seat, cup bore, cup floor with an annular groove, hex pocket.
  - Screw through-hole: occluded.
  - Torus dome with a flat top, and a screw counterbore.
  - Skirt Ø26.8 with 3 reduced-radius reliefs under the arms.
  - Key: a skirt flat at about 59°, a blind radial hole with a black tuft (photo 182215), and a cup key block plus rib.
  - 3 arms with tuft collars.
  - Out of scope: bristles and the COTS screw.
- **Coverage.**
  - 21 loops.
  - The skirt is unscanned over θ 96–142°.
  - The collar undersides (r 33.5–38.3) are unscanned.
  - The hex walls are partial; one face has only 40 faces.

## 2. Datum plan and alignment numbers (`intake/alignment.json`, status OK)

| DOF | Feature | Result |
|---|---|---|
| Primary A | Cup rim annulus → XY, z = 0, material +Z. WHY: owner-declared axial seat | Plane rms 0.0185 / max 0.099 mm, 6,085 faces, 138.6 mm² |
| Secondary B | Cup bore axis from a wall-face IRLS fit, 5 stations, z 0.42–2.18 | r_mean 10.386 (std 0.095); station residual median 0.170 / worst 2.41 (key block and draft) |
| Clock C | 3-fold `fourier_mass` on the arms, r 20–34; arm 1 → +X | Candidate −16.88° chosen |
| Origin | Cup bore axis ∩ rim plane | Primary landmark z = −0.0011 (ok) |
| CHK-TILT | Line through the bore centres | **13.7° ± 4.0° over 1.76 mm: not resolvable** (finding; not re-levelled) |

- **QA datum audit (report-only).** 0.046° rotation, 0.019 mm origin offset, point p95 0.050 / max 0.059 mm. This is within ≤0.3° / ≤0.15 mm.
  - The audit uses the same method family on the same regions, so it is a consistency check.
- **QA ICP.**
  - it1: 1.197° / 0.065 mm, converged in 46 of 60 iterations.
  - it2: 0.394° / 0.069 mm, converged in 44 of 60 iterations.
- **Frame note.** The hub features (hex flats, key) sit at −1.1° in this frame. The arms and reliefs sit at 0°. The model uses two clocks for this (§3).

## 3. Feature tree and key parameters (`build/MODELING_PLAN.md`, `measure/PARAM_TABLE.md`)

The model is one revolved hub profile, a set of cut tools, added key solids, and 3 arms. Each arm is its side (r,z) profile, built from fitted Splines, extruded tangentially and intersected with a plan taper. No loft is used.
- Result: 75 faces, 0 ruled-like faces, V 5818.0 mm³, 1 valid closed solid in both frames.
- There are no fillets because no radius was measured.

| Parameter | Measured | Chosen | Rule / source |
|---|---|---|---|
| SKIRT_R | 26.85 / 26.80 (scan 13.34–13.47) | 13.4125 | caliper-direct, D-03/D-07 |
| BORE_R | 20.75 (scan inside width 19.9–21.1, draft) | 10.375 | caliper-direct, D-08 |
| HEX_DEPTH | 3.44 (scan predicts 3.61) | 3.44 | caliper-direct, D-11 (CHK-ACHIEVABLE finding) |
| HEX_AF | 7.381 / 7.325 (third pair occluded) | 7.353 | keep-measured, scan, **critical, uncalipered** |
| ARM_WIDTH_COLLAR / COLLAR_THICK | 5.33 / 4.07 (scan 5.65, dilated) | 5.33 / 4.07 | caliper-direct, D-02/D-01 |
| ARM_DILATION | (5.65 − 5.33)/2 | 0.16 per side | Applied to the arm top, bottom and width |
| ARM_TOP / ARM_BOT | Mean of 3 arms; per-arm sd ≤ 0.35 | Spline through the deg-4 fit | mean-of-n, scan |
| DOME_ARC_R / DOME_TOP_Z | Circle fit R 8.238, rms 0.036; top 10.839 | Same; tangent to the skirt | keep-measured, scan |
| CUP_FLOOR_Z | 2.436–2.528 | 2.453 | scan p50 |
| ARM_RELIEF_R | 12.43–12.56 | 12.49 | mean-of-n, scan |
| ARM_RELIEF_HALF_DEG | it1: 17 (step midpoint) | **it2: 16** (end of the constant arc) | scan, `relief_measure.json` |
| ARM_RELIEF_RAMP_END_DEG | 22–26 | **it2 new: 24** | scan |
| ARM_CLOCK / PATTERN_CLOCK | 0 / −1.19, −1.2, −0.85 | **it2 new: 0.0** / −1.1 (hub only) | scan |
| KEY_FLAT_D, KEY_THETA | 12.49–12.52; 58.0–58.8° | 12.50; 60 + clock | scan; symmetry |
| KEY_BLOCK / KEY_RIB | [8.5, 4.2] / [2.8, 1.44] | Same | scan |
| SKIRT_KEY_HOLE | Boundary loops only | Ø1.6, z 3.0, to r 10.9 | photo-inferred |
| SCREW_HOLE_D / CBORE_FLOOR_Z | Hidden | 3.2 / 8.9 | assumed |
| D-05 skirt OD min 24.84 | Scan window 24.944–25.078 | **STRUCK** | CHK-ACHIEVABLE (margin 0.004–0.14) |

**it1 → it2 parameter diff.** ARM_RELIEF_HALF_DEG changed 17 → 16. ARM_RELIEF_RAMP_END_DEG (24) and ARM_CLOCK (0.0) are new.
- The relief tool changed from a revolved sector with radial walls to an arc plus a chamfer.
- The cause is it1's findings: the D-05 CAD window was 25.36 against the scan's 24.98, the Z-SEAT corner read 0.808, and ICP rotated the CAD by 1.13°.

## 4. Gate results (`qa/gate.json`, it2, OFFICIAL full-res, hash unchanged)

- **Regime.** RE_SPEC. The adapter keys were added in `qa/regime.json` (see defect D2).

**Tier-1: 7 of 12 readings gated.**

| Dim | Caliper | CAD | Δ | Result |
|---|---|---|---|---|
| D-01 | 4.07 | 4.0746 | +0.005 | PASS |
| D-02 | 5.33 | 5.3634 | +0.033 | PASS |
| D-03 | 26.85 | 26.825 | −0.025 | PASS |
| D-05 | 24.84 | 25.0137 | **+0.174** | **FAIL** (struck; the CAD is 0.03 from the scan window minimum) |
| D-07 | 26.80 | 26.825 | +0.025 | PASS |
| D-08 | 20.75 | 20.750 | 0.000 | PASS |
| D-11 | 3.44 | 3.440 | 0.000 | PASS |

D-04, D-06, D-09, D-10 and D-12 are absent, not passed.

**Tier-2, whole part.**

| Statistic | p95 | max | Result |
|---|---|---|---|
| scan→CAD, masked | 0.544 | 1.167 | PASS |
| scan→CAD, unmasked | 22.1 | 29.0 | Bristles, so this pass is mask-dependent |
| CAD→scan, observable | 1.063 | 3.049 | PASS (unobservable 0.20 %) |
| CAD→scan, masked | 0.737 | 2.503 | — |

**Interfaces (max ≤ 0.8).**

| Zone | Masked s2c / c2s max | Unmasked c2s max | Result |
|---|---|---|---|
| Z-SEAT | 0.289 / 0.386 | — | PASS (it1 c2s was 0.808, FAIL) |
| Z-HEX | 0.732 / 0.347 | 1.824 | PASS, **masked** |
| Z-BORE | 0.475 / 0.497 | 1.141 | PASS, **masked** |
| Z-KEY | **1.167 / 1.606** | — | **FAIL** |

**Masks** (fraction removed):

| Mask | Fraction |
|---|---|
| M1 bristles | 19.1 % |
| M2 key tuft | 0.28 % |
| M3 screw head | 1.72 % |
| M4 screw tip | 0.28 % |
| M5 CAD hidden under screw | 2.91 % |
| M6 open boundary 0.8 mm | 18.3 % |
| M7 skin normal 70° | 6.7 % |

**Checks.**
- Clusters: 3 scan→CAD clusters, all bristle tufts.
- CHK-MASK finding.
- CHK-INDEP finding.
- CHK-LIKE4LIKE finding: one protocol change, the D-01/D-02 jaw azimuth.
- CHK-PATCHWORK, CHK-FILLET, CHK-ENUM, PHOTO and CHK-CIRCULAR pass.
- Overlays: every panel has a scan trace.

**it1 for comparison (`_it1_SUPERSEDED/qa/gate.json`): `REVISE`.**
- D-05: Δ +0.521.
- Z-KEY: 1.158 / 1.587.
- Z-SEAT CAD→scan: 0.808.
- Whole part: scan→CAD masked 0.543 / 1.158; CAD→scan observable 1.048 / 3.060.

## 5. Verdict and limitations

**Verdict: BAND_NOT_MET.** `verdict.py assemble` allowed {BAND_NOT_MET, REVISE, HALT}. REVISE is not available because the owner's 2-loop budget is used.

Misses:
1. **D-05, +0.174.** This is an attribution problem, not a geometry one. The reading is below the scan's achievable two-jaw window, and the CAD reproduces that window.
2. **Z-KEY, 1.17 / 1.61.** The key is approximated with boxes and a photo-inferred hole.

Options: (a) human ACCEPT-BAND; (b) a jaw-placement photo for D-05 plus key calipers, then re-run; (c) HALT.

The agent accepts this verdict for reporting only. **No human acceptance exists.** Therefore there is no `deliver/`; this is recorded in `DECISIONS.md` as an OTHER entry.

Limitations (each has a re-run trigger in `qa/review.json`):
- **L1.** Tier-1 is partial; D-05 fails.
- **L2.** Scale is unverified.
- **L3.** Hex AF is uncalipered, and the hex and bore passes are **masked** passes (unmasked 1.824 and 1.141).
- **L4.** The screw hole and counterbore floor are assumed.
- **L5.** Verification was not independent.
- Also: there are no fillets, the arms are the mean of three free-state-deformed arms, and the collar underside is unscanned.

**Claim boundary.** Fit for visualisation and fit-up studies. Not fit for tooling.

---

## 6. Skill defects found (most important section)

### Blind-test contamination (critical)

**D1. The skills contain the B02 answers.** Several skill files carry this part's golden results in the text, which defeats a blind replay. I read these before I could avoid them, so this run is not fully blind.
- `stl-re-orchestrate/references/verdict-examples.md` §4 gives:
  - F06 caliper 24.84 unachievable, with window 25.99…27.08;
  - `SKIRT_R_FLAT 12.420 → 12.550`;
  - hex AF 7.358;
  - Tier-2 0.740 / 2.524;
  - datum audit 0.429° / 0.451.
- `stl-re-intake-datum/references/datum-cookbook.md` §2.2 gives the complete B02 `align.py` spec: the raw approximate normal `[0.3207,-0.3428,-0.8830]`, bore r_hint 10.35, and z_range. It also gives loop radii (hex r 2.45–4.09, cup 9.67–10.59, SAF-1 hole) and the dome apex z 10.97.
- `stl-re-measure-intent/SKILL.md` §7, §8, §11 and Open questions give:
  - `SKIRT_R_FLAT 12.550`;
  - hex 7.358 "NOT snapped";
  - SAF-1 at +59° and hex phase 59.04°;
  - the scan window 24.99–27.25.
- `stl-re-intake-datum/SKILL.md` gives the "arms 0.4–0.8 mm oversize" and "B02 intake −71° vs frozen +59°" figures.

What I did: I derived my own values. The rim normal came from the `planes` survey (0.3153, −0.3454, −0.8839). R_hint came from D-08. The results agree with the leaked values, but that agreement cannot be claimed as blind. **Fix:** move part-specific numbers into a held-out appendix, or redact them when the skills are used as a test.

**D1b. Provenance citations tell the agent to read forbidden paths.** Nearly every rule cites `golden-examples/...` or `analysis/...`, which were forbidden in this run. Examples: "Read `analysis/SYNTHESIS.md`" in run-contract §8, and "Definitions and evidence: `analysis/SYNTHESIS.md` §2". The check-id definitions (CHK-*) exist **only** in that forbidden file. There is no in-skill glossary, so several checks are defined only by their usage.

### Contract and script mismatches (silent failure risk)

**D2 (critical). The regime keys do not match between stages, so the gates silently disappear.**
- `stl-re-intake-datum/scripts/intake.py regime` writes the bands as `tier1_abs_mm`, `tier2_p95_mm`, `tier2_max_mm` and `interface_max_mm`.
- `stl-re-verify/scripts/{sim_caliper,deviation_gate,verdict}.py` read `tier1_abs`, `p95`, `max` and `interface_max`. The key names are in `gate-protocol.md` §1.
- The verify skill says "cp intake/regime.json qa/regime.json … never edit". Following that literally gives **no bands at all**. Band results come back `None`, which is not `False`, so `verdict.py` would not count any fail. The result is a silent APPROVED path.
- Workaround: I added alias keys, left the originals unchanged, and wrote an `adapter_note`.

**D3. `stl-re-measure-intent/scripts/sim_caliper.py --mode inside` returns garbage.**
- It picks the "innermost loop" with `min(polys, key=max r)`, after `--r-band` has chopped the loops into fragments.
- For the B02 bore it returned a window of 0.377–0.99 with `--r-band 9,11`, and 1.14–5.61 without it. It then "STRUCK" a valid 20.75 reading and set CHK-ACHIEVABLE to **fail**.
- Workaround: `measure/bore_inside_workaround.py`, which computes the diametral inside width r(θ)+r(θ+180): 19.9–21.1.

**D4. `sim_caliper.py --reading` uses `action=append`,** so it must be repeated for each value. The SKILL text (`--reading <value>`) and the help text ("reading(s)") suggest it takes a list. My first call exited 2 with "unrecognized arguments".

**D5. The CHK-ACHIEVABLE rule conflicts with the dilation rule.** Measure §7 says to strike a reading below the scan window. Measure §6 and intake step 2 say thin-section oversize is dilation and the caliper governs.
- Taken literally, D-02 (5.33 against a scan width of 5.65) would be struck.
- The skill gives no rule for deciding which applies. I kept D-02 and recorded the conflict.

**D6. `stl-re-verify/scripts/datum_audit.py` circle position depends on an undocumented region requirement.**
- It fixes the inner/outer wall sign from the outermost 10 % of the *selected* faces.
- If the region contains only the bore, as the natural spec does, "inner" keeps the wrong side. In this run that left 26 faces, R 3.06, and a false **17.8° / 9.2 mm** datum disagreement.
- `gate-protocol.md` §2 does not say the region must include an outer wall such as the skirt.
- Workaround: widen r to [9.8, 14]. The audit then gave 0.046° / 0.019 mm.

**D7. `datum_fit.py noise --circle-z` needs a closed section loop.** It has no open-arc or IRLS option. On B02 the bore never closes, so the secondary noise floor cannot be measured.
- `align.py` then only notes "secondary circle residual not compared". The STOP rule for the secondary datum is effectively skipped, even though the bore station residuals (median 0.17, worst 2.41) are 10× the plane noise.

**D8. The `param_table.py` keep-measured check has no tolerance.** It rejected `RIM_Z` value 0.0 against measured −0.0011, even though that is 17× inside the noise floor. I had to relabel the row `round-within-noise`.
- Conversely, it does **not** check list-valued params. KEY_BLOCK, KEY_RIB and ARM_TOP passed with any value.

**D9. Contract drift.**
- run-contract §4 lists 8 rule values, but no rule fits "derived from a caliper value plus a scan delta" (for example the hex floor = CUP_FLOOR + D-11).
- §10 says the regime lives in `intake.json#regime`; §12 moves it to `intake/regime.json`.
- `init_run.py status` treats `max_loops` as 3. It has no way to record an owner's tighter budget.

### Procedural gaps and unclear steps

**D10. Independence (CHK-INDEP) is impossible in a single-agent session.** The orchestrator requires a fresh context but gives no fallback beyond "declare it". I declared it.
- Worse, nothing stops QA from reading builder numbers. My it1 `dims.json` used the arm azimuth −1.1° from `params.json` without my noticing.
- **Fix:** verify should derive the jaw placement from the scan, not from the builder's parameters.

**D11. Struck readings and Tier-1.** Measure says a struck reading is "not built to". Verify says to list *every* dim and explain misses. Neither says whether a struck reading stays **gated**.
- I kept it gated, which is the honest choice. As a result a correctly handled attribution error forces BAND_NOT_MET forever.
- The skills need an explicit rule: for example, keep the dim gated but classify the miss as `attribution`, or ungate it with a mandatory limitation.

**D12. The rebuild skill has no acceptance self-check loop.** The MODELING_PLAN template asks for per-feature acceptance criteria, but nothing makes the agent evaluate them.
- In it2 my relief cut tool was wound clockwise. `extrude()` went to −Z and the boolean removed **nothing**, with no error and a valid single solid.
- Only the Tier-1 D-05 value (25.94) exposed it. I added a volume-delta self-check to `model.py`.
- **Fix:** `model_template.py` should assert that every cut removes volume and every add adds volume.

**D13. `verdict.py` gates the whole part and interfaces only.** It does not gate the named interface "not covered by calipers" rule selectively. Interfaces that *are* calipered (the bore, D-08) are still gated at 0.8.
- The p95 band shows as `None` in the zone rows of VERDICT.md (`p95 ≤None`), which reads like an error.

**D14. Cluster report bug.** An over-band cluster that crosses θ = 0 is reported with `theta_deg_range [0.0, 360.0]` (it2 cluster 0, arm 1 bristles). It needs circular-range handling.

**D15. Minor script and UX issues.**
- `init_run.py init` prints the full INPUT_HASHES JSON: about 200 lines, against the "compact summaries" rule.
- `intake.py regime` prints its JSON twice.
- `intake.py coverage` lists only the top 15 of the 21 loops.
- `face_stats.py` reports the revolved 3-point-arc dome as `revolution`, not `torus`.
- `align.py` reports `clock.angle_deg` as +16.88 while `chosen_deg` is −16.88, with no sign-convention note (a CHK-FRAME hazard).
- The dilation per side (0.16) was computed from a scan width I typed in by hand (5.65), not read from a JSON. The skills have no helper for local caliper-vs-scan offsets.

**D16. The deliver stage was not exercised,** because BAND_NOT_MET had no human ACCEPT-BAND. Its scripts are untested in this replay.

**D17. `B02/baseline_run/` sits inside R.** It was not opened, but the replay harness places a prior answer next to the blind inputs.
