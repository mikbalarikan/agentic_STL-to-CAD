---
name: stl-re-verify
description: Independently verify a reverse-engineered STEP against its scan and calipers. Covers hash freeze, datum audit, validity, surface census, Tier-1 re-measure on the STEP, own ICP, two-way full-res deviation with zones, named masks, sensitivity, observability, over-band clusters, overlays, then a verdict under the declared regime. Use after a rebuild and before delivery, ideally in a fresh agent.
---

# stl-re-verify

Independent QA for one part's STEP. Inputs are the frozen `build/` STEP, the raw scan,
`intake/alignment.json`, `input/MEASUREMENTS.md` and photos. Outputs are `qa/gate.json`,
`qa/VERDICT.md` and `qa/overlays/`. The contract is in
`../stl-re-orchestrate/references/run-contract.md` (§6 gate.json, §7 verdicts, §8 check ids).

**Stance.** Never trust a builder-reported number. Re-derive everything with the scripts in
`scripts/`. Never import `build/model.py`, builder helpers, or `params.json` values as
"expected" results. A result checked against itself proves nothing:
- the OD validator passed 13/13 against expected values taken from the same scan;
- P03 refined its datum by ICP to its own CAD
  (`analysis/SYNTHESIS.md` CHK-CIRCULAR; facet-film T12, T18).

**Independence.** Run in a fresh agent/context that did not build the model. If you cannot,
write that in `review.json` → `independence` and set CHK-INDEP to `finding`. B02 ran QA in the
builder's own context and declared it (A13, `analysis/golden/OOM-B02.md` §2, §10).

**Honesty.**
- A miss is reported with its number, per region, with its cause and options. Never loosen a
  band, never add a mask after the fact to clear it, never re-grade on a decimated scan
  (SYNTHESIS F1, §0.1).
- Of six golden parts, only the DRM screw passed a scan band unmasked and uncaveated. Limitation
  states are the normal case. Use them.

## 0. Before you start

1. Copy `intake/regime.json` to `qa/regime.json` (`cp intake/regime.json qa/regime.json`), the
   canonical declaration written at intake (run-contract §12). Never edit it. It must name the
   regime and its source.
   - If `intake/regime.json` is missing, **stop and ask the human.** There is no default
     (QUESTIONS.md Q1).
   - Regimes and their sources: see [references/gate-protocol.md](references/gate-protocol.md) §1.
     In short:
     - **RE_SPEC:** Tier-1 ±0.15, Tier-2 p95 ≤1.6 / max ≤4.0, interfaces ≤0.8
       (`RE_SPEC.md:170-175`).
     - **baseline-skill:** p95 ≤0.30 / max ≤0.80 plastic, ≤0.15 / ≤0.50 machined
       (`baseline/skills/stl2step-build123d/SKILL.md:87`).
     - **project-spec:** from the spec's path.
2. Confirm that the scan is the **full-resolution original**.
   - With only a decimated copy, every deviation number is labelled INSPECTION ONLY and no
     official grade is possible (`golden-examples/README.md`).
   - This is a declared **limitation**, not a blocker: the verdict can still be
     `APPROVED_WITH_LIMITATIONS` (DRM screw golden: scan-only, decimated, approved with the
     limitation declared) with re-run trigger "full-res scan available" — it is never forced to
     REVISE/HALT for this reason alone. Plain `APPROVED` still needs the full-res original.
3. `pip install trimesh scipy numpy matplotlib rtree build123d`. Scripts need Python ≥ 3.10.
   Every script prints its numbers and writes JSON with the run-contract §2 header.

## 1. Hash freeze (heuristic, n=1: M02)

```bash
S=~/.claude/skills/stl-re-verify/scripts
python $S/step_check.py freeze --step build/<part>_datum.step build/<part>.step --out qa/hash_freeze.json
```

Do all QA against these files. At the very end, run `step_check.py verify --freeze qa/hash_freeze.json`.
A changed hash invalidates QA, so re-run it (M02 `qa_report.json` checks[0], [21]).

## 2. Datum audit, REPORT-ONLY

1. Write `qa/datum_spec.json` from the datum description in `INTAKE_CARD.md` / `alignment.json`,
   not from builder code. Format: gate-protocol §2.
2. Run it:
   ```bash
   python $S/datum_audit.py --scan input/scan.stl --align intake/alignment.json --spec qa/datum_spec.json --out qa/datum_audit.json
   ```
3. Report the rotation difference, origin offset, and point disagreement (mean / p95 / max)
   against ≤0.3° / ≤0.15 mm (`RE_SPEC.md:241`). It is **never blocking**
   (QUESTIONS.md Q2, run-contract §9). Both approved OOM goldens exceeded it: B02 0.429° /
   0.451 mm, P03 0.154° / 0.600 mm.
4. If the offset is large compared with the bands, say so in the verdict. It also explains ICP
   deltas.
5. The builder matrix only *selects* named regions. All fits are QA code on the raw scan: normal
   vote, SVD plane, IRLS Cauchy circle with the wall side fixed empirically, k-fold Fourier clock
   (`q03_datum_full.py`, generalised).
6. `position.wall` (`inner`/`outer`) needs a real outer/inner wall **pair** inside `position.region`
   to fix its sign convention off. If `region` is deliberately a single wall (a bore or a boss with
   no counter-wall), write `position.single_wall: "inner"|"outer"` instead — `datum_audit.py` will
   otherwise either refuse with a clear error (no wall pair detected) or crash. See gate-protocol §2
   (review D6, and the "bore-only, wall inner" fix).

## 3. Validity and surface census

```bash
python $S/step_check.py check --step build/<part>_datum.step build/<part>.step --out qa/step_check.json
```

- **Validity** needs exactly one solid, BRepCheck valid, closed shells, 0 naked edges, V > 0, and a
  watertight fine tessellation (0.005 mm / 0.05 rad) in **both** frames (SYNTHESIS D12, D14;
  B02 `q10`, `q01`). A failure here is a geometry fail → **REVISE (or HALT at loop 3), never
  BAND_NOT_MET** (review V6: a non-solid STEP is not a band a human can accept).
- **Census** gives face count and count/area per surface type, and the analytic area share. It is
  **reported, not gated** (QUESTIONS.md Q3).
- Use the census to answer CHK-PATCHWORK in `review.json`:
  - Are there B-spline/ruled faces the plan did not call for?
  - Are there thousands of planar facets?
  - Evidence: W01 had 5,485 faces; M02 had 2354 planar facets from a polygonal involute.
  - Also check that `build/MODELING_PLAN.md` / `model.py` has no `loft(ruled=True)` or
    polyline stack of scan slices.
- **CHK-FILLET.** Compare every fillet in `build/export_check.json` (target vs used, OK/FAILED).
  A silently skipped or shrunk fillet is a finding (B02 fallback, P03 skip).

## 4. Tier-1: re-measure every caliper/operator dim on the STEP

1. List **every** dim in `input/MEASUREMENTS.md` in `qa/dims.json`, with `total_requested` and
   `absent`. For each, choose a method:
   - `jaw`: simulated two-parallel-jaw caliper on a section. Use `envelope` for lobed ODs,
     `innermost` for pockets, `dir` for a width along a direction.
   - `bore`
   - `height`: medians on a meridian.
   - `analytic_cylinder`: a B-rep face query.
   Place the jaws where the operator placed them (photo/guide), not where the CAD is easiest.
2. Run it:
   ```bash
   python $S/sim_caliper.py --step build/<part>_datum.step --dims qa/dims.json --regime qa/regime.json --out qa/tier1.json
   ```
3. Read the results:
   - Band: the regime's `tier1_abs` (RE_SPEC ±0.15, `RE_SPEC.md:170`).
   - Uncalipered dims are **ABSENT, not passed**. B02 gated 5 of 24 and declared it
     (`analysis/golden/OOM-B02.md` §9 L1).
   - A pass whose margin is below the reading's uncertainty is flagged `grey_zone` (facet-film
     T15). Photo-transcribed readings carry ±0.1 effective (`MEASUREMENTS.md:10` via SYNTHESIS §4).
4. On a Tier-1 miss, check achievability before blaming the geometry. Run the same jaw on the
   **scan** section (CHK-ACHIEVABLE).
   - B02 F06 caliper 24.84 lay 1.15 mm below the achievable window 25.99…27.08 on a 3-lobed
     skirt. That was attribution, not modelling (`OOM-B02.md` §8; window disputed: `QUESTIONS.md`
     §C records this skill's own jaw on the full-res scan giving 24.99–27.25).
   - Record which it is in the miss explanation.

## 5. Tier-2: independent registration

```bash
python $S/tier2_icp.py --scan input/scan.stl --scan-kind full --align intake/alignment.json \
  --cad build/<part>_datum.step --scan-masks qa/icp_scan_masks.json --out qa/registration.json
```

- ICP is point-to-point with masked correspondences (B02 `q20_tier2.py`; its parameters are the
  defaults).
- **converged = false ⇒ the gate is INVALID** (`re-qa-verifier.md:37-38`; the W01 ICP hit its cap).
  You may raise `--max-iter` once and record both runs, with the reason (e.g. "axisymmetric part,
  slides slowly": a DRM new-skill replay needed 90 where the default 60 was not enough). `--max-iter`
  is a parameter, not a threshold to tune until it passes -- never invent a new default; keep raising
  it (and recording why) only as far as the part's geometry actually explains. Axisymmetric parts
  slide about their axis and converge slowly.
- Report iterations, Δ° and Δmm.
- **Always run ICP, in every regime** (run-contract §12): independence means verify never grades in
  the builder's alignment frame alone. The DRM official gates were graded after ICP too --
  `registration_converged: true` is recorded
  (`golden-examples/dreame_brush-caps/report/screw_official_gate.json:5`,
  `snap_official_gate.json:5`), not "graded in the alignment frame".
- Run `deviation_gate.py` **twice**: once without `--registration` (`--out qa/deviation_datum.json`,
  the builder's datum frame) and once with it (`--out qa/deviation.json`). `qa/deviation.json` is
  the gate; `verdict.py` reports both and flags a limitation when the two frames' p95 differ by
  more than the regime's p95 band (a large gap is a datum finding, not something ICP should quietly
  absorb).
- Passing `--registration` is required for a run to be labelled `OFFICIAL`. Without it,
  `deviation_gate.py` labels the run `NO QA REGISTRATION` and `gate_valid: false`.
- **CHK-CIRCULAR.** `T_refine` is QA-only. Never write it back into `alignment.json`, and never
  let the builder re-gate with it (P03).

## 6. Tier-2: two-way deviation on the full-res scan

1. Write `qa/zones.json`. Zones are predicates in the datum frame (gate-protocol §2). Include:
   - every **named functional interface** from `INTAKE_CARD.md` (`kind: functional_interface`,
     gated at `interface_max`);
   - interior/occluded zones (`kind: interior`, reported only, `RE_SPEC.md:176`);
   - region buckets such as z-bands (OD `gate.py:30-37`).
2. Write `qa/masks.json`. Every mask is named, with why and evidence. Read
   [references/mask-policy.md](references/mask-policy.md) first.
3. Run it:
   ```bash
   python $S/deviation_gate.py --scan input/scan.stl --scan-kind full --align intake/alignment.json \
     --cad build/<part>_datum.step --registration qa/registration.json --regime qa/regime.json \
     --zones qa/zones.json --masks qa/masks.json --out qa/deviation.json --save-arrays qa/dev_arrays.npz
   ```
   - Distance is exact point-to-triangle over KD candidates, seeded. The defaults reproduce the OD
     golden bit-exact **when `--cad` is `OD-H12-Pump_datum.stl`**, the builder's own tessellation, as
     OD did; passing the STEP instead re-tessellates at 0.005 mm and will not match bit-exact. It
     can only over-estimate.
   - Stats: n, rms, mean, p50, p95, p99, max, with sampling and seeds (SYNTHESIS E1–E3).
4. Read the output in this order:
   1. **Unmasked vs masked**, both directions, side by side.
      `mask_dependent_passes` non-empty ⇒ CHK-MASK finding ⇒ at best APPROVED_WITH_LIMITATIONS,
      and the limitation quotes the unmasked number (B02 hex 1.624).
   2. **Sensitivity.** Leave-one-out per mask plus the open-boundary radius sweep. A pass that
      flips inside the sweep is fragile, so say so.
   3. **Observability split** of CAD→scan (heuristic, n=1: OD; B02 used the open-boundary mask
      for the same purpose).
      - The unobservable fraction is a coverage fact, not a pass. OD: 25.65 % unobservable, and
        the observable p95 0.567 still missed.
      - Parameters are recorded; they are OD's (0.5 mm, 60°, 6 rays, 20k seed 5).
   4. **Over-band clusters** (CHK-CLUSTER, CHK-ENUM). Treat every scan→CAD cluster as a real
      missing feature until disproven: count the points, look for a flat top, check the photos.
      - P03 it1 dismissed a coherent axis cluster as "occlusion". It was the drive stem:
        158k raw verts and 4907 skin points > 4 mm (`OOM-P03.md` §8).
      - Explain each cluster in `review.json` → `cluster_explanations`. Unexplained clusters stay
        findings.
   5. **Zones.** Every functional interface passes or misses on its own. A zone passing does not
      excuse the whole part, and the reverse also holds.
5. `label` must read `OFFICIAL (full-res)` for a grade. `INSPECTION ONLY` (decimated) or
   `INVALID` (unconverged ICP) means no grade.

## 7. Overlays (CHK-OVERLAY)

```bash
python $S/overlay.py --scan input/scan.stl --align intake/alignment.json --cad build/<part>_datum.step \
  --z=-1,2,5 --theta 0,90,150,270 --out qa/overlays/overlay.png --json qa/overlays/overlay.json
```

- Choose Z planes through every functional level and radial half-planes through every clocked
  feature and every over-band cluster.
- **Look at the PNG.** Any panel flagged `NO SCAN TRACE` proves nothing. Move it, or say why the
  scan is absent there (DRM snap 150° panel, SYNTHESIS E12).

## 8. Photo plausibility and the remaining checks → `qa/review.json`

- **Photo plausibility / CHK-ENUM** (SYNTHESIS E15, A8). Walk every photo. Every photographed
  feature must exist in the CAD, and no CAD feature may be absent from photos and scan (nothing
  hallucinated). P03 G4 listed 8 kidneys, the hex, ~51 tread slots, the pad boss, the stem and the
  socket. Tick each one against the intake feature list.
- **CHK-CIRCULAR**:
  - `fail` if the grading gate itself compares the result with itself: datum ICP'd to own CAD
    and graded in that frame, or expected values derived from this scan.
  - `finding` if the builder's record contains such a check but QA's numbers are independent.
    Label such validators "consistency check, not independent evidence" (OD 13/13).
- **CHK-LIKE4LIKE.** When comparing with a previous iteration (`_itN_SUPERSEDED/qa/gate.json`),
  compare only runs with the same protocol: same regime, masks, ICP and sampling.
  - Otherwise report both runs and say which part of the "improvement" came from protocol. B02
    it1 → it2: hex 1.846 → 0.316 came from masking, not geometry (`OOM-B02.md` §8).
- **CHK-INDEP, CHK-FILLET, CHK-PATCHWORK**: from §0, §3.
- **Limitations.** Each needs `rerun_trigger`, e.g. "one caliper reading on F01 → re-run" (B02 L3).
  Also add a **claim boundary**: what this result is not fit for.

## 9. Verdict

```bash
python $S/step_check.py verify --freeze qa/hash_freeze.json
python $S/verdict.py assemble --qa qa      # exit 2 = your proposed verdict is not allowed by the evidence
python $S/verdict.py render --qa qa        # VERDICT.md; every number from gate.json (CHK-NUMBERS)
```

`assemble` derives the **allowed** verdict set. See
[references/verdict-template.md](references/verdict-template.md) §2 for the table.
- A blocker leaves only REVISE / HALT.
- A band fail leaves only BAND_NOT_MET / REVISE / HALT.
- Any limitation leaves only APPROVED_WITH_LIMITATIONS / REVISE / HALT.

Choose inside that set:
- **REVISE**: the miss is fixable in measurement or geometry (P03 stem, B02 F06). Loop back to
  measure/rebuild; this counts toward the 3-loop limit (`RE_SPEC.md:248-250`). Before looping, the
  orchestrator moves this `qa/` into `_itN_SUPERSEDED/`.
- **BAND_NOT_MET**: the miss is real and explained, and more geometry cannot fix it without data
  (OD: no calipers; DRM snap: scan flap). Give per-region cause and options. Delivery needs a
  recorded human acceptance.
- **HALT**: 3 loops are used, or only a human can clear the blocker.
- **APPROVED_WITH_LIMITATIONS**: every gate passes and each limitation has a re-run trigger (B02,
  P03).
- **APPROVED**: everything passes unmasked, with no limitations (DRM screw).

If `assemble` refuses your verdict, change the verdict, not the evidence. Never edit gate.json by
hand. Never delete a mask-dependent or grey-zone flag. Never re-run with looser parameters
without reporting both runs.

## Script index

| Script | Lifted from | Writes |
|---|---|---|
| `step_check.py` | M02 hash freeze; B02 `q10` QA-1/2, `q01` naked edges | hash_freeze.json, step_check.json |
| `datum_audit.py` | B02 `q03_datum_full.py` | datum_audit.json |
| `sim_caliper.py` | B02 `q10_solid_tess_tier1.py` jaws (QA's own copy) | tier1.json |
| `tier2_icp.py` | B02 `q20_tier2.py` ICP | registration.json |
| `deviation_gate.py` | DRM `fastgate.py:dist_to_mesh` + OD `gate.py` | deviation.json |
| `observability.py` | OD `gate.py:57-84` (helper vector fixed) | via deviation_gate |
| `overlay.py` | DRM `overlay.py` + OD `ovl.py` | overlays/*.png, *.json |
| `verdict.py` | new | gate.json, VERDICT.md |

**Test record** (see verdict-template §4):
- The OD-H12 full-res gate reproduces `report/deviation_gate.json` with **zero** difference in
  every statistic (with `--cad OD-H12-Pump_datum.stl`, as OD did).
- B02 datum audit, ICP, Tier-1 and STEP checks agree with the golden QA JSONs.
- The DRM screw was run on the decimated scan, labelled inspection only.

## Open questions (not decided here)

- The ICP cap/tolerance (60, 1e-6) comes from one project (B02). The DRM decimated screw needed 109
  iterations. (Non-convergence is reported and invalidates the Tier-2 gate regardless of cap;
  run-contract §12.)
