# REPLAY REPORT — DRM brush screw cap (new_skills, blind replay)

Run folder: `DRM/new_run/` (init_run.py, iteration 1 of 3, no loops used). Final verdict **HALT**
(`qa/gate.json#verdict`). Only blocker: the scan is decimated → inspection only. Every inspection
band passes, unmasked. `deliver/` was not created (CHK-PUBLISH respected).

## 1. Intake card summary (`intake/INTAKE_CARD.md`)
- Scan: 949,999 faces, 1,017 bodies (the decimated copy splits into fragments); the largest body was kept
  (931,220 faces, 1.98 % removed). Open mesh: 84 boundary loops raw, 22 on the kept body. Ray vote says the
  normals point outward. Work copy decimated to 300k faces (work-vs-full p95 0.0009 / max 0.0099 mm).
- Declared: regime **baseline-skill, consumer plastic, p95 ≤ 0.30 / max ≤ 0.80** (`intake/regime.json`,
  DECISIONS REGIME). Declared scan-only (MEASUREMENTS decision). Scan is DECIMATED, so any gate is inspection
  only (OTHER). No human acceptance exists (OTHER). Single solid (PART-CLASS).
- CHK-SCALE: FLAG. No dimensions to check against, so units are assumed mm and no scale was applied.
- Noise floor: plane 0.00715 mm rms (top face). Circle 0.0306 mm rms (bottom bore).
- Features (11): top face, round boss with one large edge round, shoulder, pentagon body (vertical flat ends,
  corners turned at r 5.42), a drafted recessed panel in the middle of each flat, a lower pentagonal frustum
  (29.3°) with rounded edges, bottom face, a blind double-D drive hole, a rounded neck through the web
  (largely unscanned), the bottom counterbore, and blends.
- Open questions: dip or flattening on the boss at θ ≈ 30–80°; the double-D sits at −87.1°, not aligned to
  the pentagon; neck radius; the top face is about 0.5° off the other planes. No photos exist, so the
  photo side of CHK-ENUM could not run.

## 2. Datum plan and alignment (`intake/alignment.json`, status OK)
- Primary: top face → XY at z = 0, material −z. RANSAC+SVD over 18,450 faces; rms 0.00715 / max 0.0472 mm.
- Secondary / origin: bottom-bore axis. Kåsa fit, 9 stations z −4.95…−4.15, r 2.0439 ± 0.0071, rms 0.0288 /
  max 0.091. Origin = bore axis ∩ top face.
- Clock: polygon_flat n = 5 at z = −2.5, a flat centre on +X, **−34.081°**. The line-fit flat phase in the
  frozen frame is +0.47°; that phase was kept as a parameter.
- CHK-TILT = finding. Bore alone gives 2.08° ± 0.31° over 0.8 mm (too short to trust). Bore + double-D gives
  0.64° ± 0.09° over 4.45 mm, but that spec STOPs. Plane-to-plane angles against the top face are 0.2–0.6°.
  The part was not re-levelled; modelled perpendicular to the top face.
- Landmarks: primary lands at z −0.0003 (ok); bottom z −5.151 against −5.12 ± 0.05 (ok).
- Rejected attempt (logged): boss OD + bore gave tilt 1.37°. The boss is non-round (rms 0.066, a 0.1 mm
  offset), so it was dropped as an origin feature.

## 3. Feature tree and key parameters (`build/MODELING_PLAN.md`, `measure/PARAM_TABLE.md`)
All parameters are `source: scan`, and all are keep-measured or round-within-noise.
| F | Op | Key params (measured → chosen) |
|---|---|---|
| F01 | pentagon prism, z −5.107…−0.487 | apothem 4.497..4.515 → 4.506; phase 0.469 → 0.47°; count 5 (FFT, 3 stations, CHK-COUNT pass) |
| F02 | ∩ vertical cylinder | corner r 5.39..5.45 → 5.42 |
| F03 | ∩ pentagonal frustum from 5 half-space boxes; inclined edges filleted first | a(z) = 6.1282 + 0.5613 z (29.3°); edge R 1.31, derived from a measured corner setback of 0.24–0.27 |
| F04 | 5 drafted panel cuts (one tool, polar) | a(z) = 4.5448 + 0.09313 z (draft 5.32°); half-width 1.68..1.85 → 1.75 |
| F05 | boss revolve (flat + one arc) | arc centre (3.7329, −0.5879), R 0.5961 → 3.733 / −0.588 / 0.596 |
| F06 | double-D cut | arc R 1.962; half-flats 1.664 / 1.606 → 1.635 (symmetry, scatter noted); normal −87.1°; floor −2.6072 → −2.607 |
| F07 | inner revolve cut (neck + bore) | neck r 1.0928 → 1.093, blends 0.584 / 0.508; bore r 2.04478 → 2.045; ceiling z −3.983 |
| F08 | fillets | bore ceiling 0.203, bore entry 0.216, double-D top 0.198, bottom outer edge 0.528: all OK. **Transition 0.548 → 0.3 REDUCED** (declared) |

Result: 1 valid closed solid in both frames, 98 faces (planned 70–110), V 268.40 mm³. Surface mix: plane 40 /
cylinder 36 / torus 7 / B-spline 15 (fillet blends only). ruled_like_faces 0; analytic area 98.6 %.

## 4. Gate results (`qa/gate.json`, label INSPECTION ONLY)
- Regime: baseline-skill (p95_mm 0.3 / max_mm 0.8). Hash freeze: unchanged. Validity: PASS in both frames.
- ICP: not converged at the 60-iteration cap (`registration_cap60.json`). Converged at 90/200; correction
  0.242° / 0.035 mm.
- Deviation, all mm:

  | Direction | Mask | rms | p95 | max |
  |---|---|---|---|---|
  | scan→CAD (n 475,724) | unmasked = masked | 0.038 | 0.078 | 0.309 |
  | CAD→scan (n 300k) | unmasked | 0.032 | 0.066 | 0.280 |
  | CAD→scan | masked (M1 open boundary 0.5 mm, 23.2 %) | 0.029 | 0.061 | 0.272 |
  | CAD→scan observable | — | — | 0.066 | 0.277 |

  Unobservable fraction 0 %. No over-band clusters. No mask-dependent passes.
- Zones, scan→CAD / CAD→scan max:
  - Double-D: 0.195 / 0.170
  - Bore: 0.092 / 0.091
  - Pentagon faces: 0.199 / 0.156
  - Top: 0.041
  - Boss: p95 0.104–0.136, max 0.281
  - Neck (interior): max 0.302
- **Whole-part band was reported as `≤None` in gate.json and not gated** (defect D1). A workaround re-run
  with the band keys renamed (`work/deviation_keysfix.json`) gives PASS in every direction.
- Datum audit (report-only): 1.262° (clock only; axis 0.055°), origin 0.0015 mm, point disagreement
  p95 0.117 / max 0.123 mm. Outside the 0.3° reference.
- Tier-1: 0 of 10 dimensions gated (all ABSENT).
- Checks:
  - CHK-INDEP: finding (same agent).
  - CHK-FILLET: finding (one REDUCED fillet).
  - CHK-ENUM: finding (no photos; boss simplified).
  - CHK-MASK, CHK-CLUSTER, CHK-OVERLAY, CHK-CIRCULAR, CHK-PATCHWORK: pass.

## 5. Verdict and limitations
**HALT.** `verdict.py` allowed only HALT or REVISE, because the decimated scan is a blocker. REVISE would be
dishonest, since nothing in the geometry needs fixing. The owner decision (inspection only) plus the skill rule
("cannot be better than REVISE/HALT") means no delivery.

Limitations, each with a re-run trigger (listed in `qa/review.json`):
- L1: inspection only. Trigger: supply the full-resolution scan.
- L2: Tier-1 not run. Trigger: calipers.
- L3: scale not verified. Trigger: three envelope dimensions.
- L4: verify was not independent. Trigger: run verify in a fresh agent.
- L5: reduced transition fillet, round boss, neck radius inferred. Trigger: photos or a pin gauge.

Claim boundary: inspection-grade model; not fit for tooling.

## 6. Skill defects found (most important)
**D1 — Band keys mismatch; the whole-part gate never runs (critical).**
- `stl-re-intake-datum/scripts/intake.py regime` writes `bands: {"p95_mm", "max_mm"}`.
- `stl-re-verify/scripts/deviation_gate.py:227` reads `bands.get("p95")` / `bands.get("max")`, and
  `verdict.py` does the same. The gate-protocol.md §1 example also uses `p95`/`max`.
- Result: under the default baseline-skill path, the whole-part p95/max band is silently ungated. The gate
  table prints `p95 ≤None / max ≤None` with result "reported", and `band_fails` stays 0.
- A failing part could therefore reach APPROVED. The skills also forbid editing `qa/regime.json`, so the only
  workaround is an out-of-band copy.

**D2 — Blindness leaks.**
- `stl-re-intake-datum/references/datum-cookbook.md` §2.1 contains the full DRM screw datum spec and its
  answers: pentagon clock −34.23°, double-D r 1.873, bottom z −5.12, tilt 0.72°.
- `SKILL.md` step 8 repeats "DRM pentagon −34.23°" and "part bottom z = −5.12".
- `stl-re-rebuild-build123d/SKILL.md` gives the DRM feature tree: "pentagon ∩ cylinder", "filleted the
  frustum corners before intersecting", a "tilted-cylinder finger dimple, 5.15° tilt".
- `orchestrate/references/verdict-examples.md` gives the DRM gate numbers (p95 0.0851 / max 0.2448).
- `verify/SKILL.md` gives "DRM screw decimated needed 109 ICP iterations".
- I measured everything myself, and my numbers disagree in places (clock −34.08°, and I found panels, not
  a dimple). But a replay on DRM cannot be blind with these skills.

**D3 — Decimated-scan policy dead-ends the run.**
- verify §0.2 forces REVISE or HALT on a decimated scan, but the orchestrator has no path for an owner who
  only has a decimated scan. HALT is the only honest option.
- No verdict or ACCEPT decision exists for "inspection-only delivery". The owner decision "inspection only"
  therefore guarantees no deliverable.

**D4 — `datum_audit.py` fails or mislabels in two ways.**
- (a) `position.wall: "inner"` on a selection that contains only a bore wall raises ZeroDivisionError at
  `circle_irls` (line ~102). The sign convention is taken from the outermost 10 % of the selection, which
  assumes an outer wall is also in the selection. Workaround: `wall: "any"`.
- (b) The Fourier clock applies `offset_deg` after picking the candidate nearest the builder's +X. With a
  corner-mass region and offset −36° it picked the wrong flat: a 73.26° "rotation difference". Offset +36°
  was needed, and the choice is arbitrary. It should offset before labelling.

**D5 — `verdict.py` refuses `PHOTO-PLAUSIBILITY ran=false`** (error "not run"), even when no photos exist.
The skill expects `n/a`. Workaround: I marked it ran=true, result n/a, with a note.

**D6 — `init_run.py status` never reads DECISIONS.md.** It keeps reporting "calipers missing, scan-only needs
a MEASUREMENTS decision" after that decision is recorded (lines 223–225 check only the file).

**D7 — ICP cap.** The default of 60 does not converge on this part (90 needed). The skill allows one raise,
but the default is known to fail on DRM, as its own open question says.

**D8 — `overlay.py` has no `--registration`.** The overlays are drawn in the builder frame while the gate is
evaluated after ICP. That is not stated.

**D9 — Negative-range CLI examples break argparse.** Examples such as `fits.py --z lo,hi` and
`sections.py --z-band lo,hi` fail with values like `-4.8,-4.2`, which every datum-frame part below z = 0 has.
You must write `--z=-4.8,-4.2`. Neither the skills nor the `--help` text say so.

**D10 — `param_table.py` rounding rules.**
- `keep-measured` requires value == measured exactly. Even 3-decimal presentation needs `round-within-noise`.
- Rounding a deg value is validated against the mm noise floor (unit mismatch).
- There is no unit for dimensionless slopes, so the draft slope was stored as "mm".

**D11 — build123d `extrude(taper=)` makes B-spline side faces.**
- Checked on 0.13: planar draft faces come out as BSPLINE.
- The strategy catalogue recommends sketch + extrude for prismatic shapes and never warns about this, so a
  tapered frustum inflates the B-spline census.
- Workaround: intersect half-space boxes.

**D12 — The align.py STOP check uses the median of all origin features.**
- A symmetric but non-circular drive feature (double-D), which the cookbook recommends for tilt span, always
  STOPs once `noise_secondary` is set.
- There is no per-feature "centre-only / residual-exempt" flag. So tilt over a long span and the STOP rule
  cannot both be honoured.
- In addition, measuring `noise_secondary` on the same bore used as the origin makes the STOP check circular,
  and the skill does not warn about this.

**D13 — `intake.py regime` source string.** It records `baseline/skills/stl2step-build123d/SKILL.md:87`, a
path outside the run that a blind agent is not allowed to open. The band's provenance cannot be checked.

**D14 — Verify requires a fresh context.** The skill offers no mechanism: this session had no subagent tool.
It falls back to declaring an INDEP finding, which works, but independence is structurally unattainable here.

**D15 — Minor gaps.**
- `deviation_gate.py` scan→CAD uses all raw vertices, including the 1.98 % fragment bodies that intake
  removed. That is not stated.
- Baseline-skill has no `interface_max`, so functional_interface zones gate at None unless `band_max` is set
  by hand. I set 0.8 = regime max.
- The measure skill requires "every INTAKE_CARD feature gets a row", but params are per-parameter; there is no
  feature→param map field.
