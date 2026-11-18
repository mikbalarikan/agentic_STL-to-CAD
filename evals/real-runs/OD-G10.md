# Real run: OD-G10 porta filter holder (2026-09-28)

The second real run of the v1 skills. Ikbal supplied a scan and two photos, but no calipers, and
asked for "p95 plastik parça toleransı" plus one zip holding the deliverables and all source files.
Records are copied under `OD-G10/`. The full run folder and the zip went to the owner; the scan,
STEP files and zip are not committed.

## Inputs and decisions
- Scan: 400,123 faces in one body, not watertight. It is a cup, Ø 80.2 mm, 31 mm scanned height,
  with three bayonet lugs. Full resolution is an agent declaration, not an owner statement.
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm (owner). Scan-only.
- Coverage: there is no underside and no outer wall over θ 38–151° (the photos show the housing on
  that side). The scan ends at z −27.84 and there is no plate interior. The plate keyhole and
  bosses were inferred from an oblique photo that has no scale reference.

## Result
- Datum: primary = the lug top pads, axis = the outer wall, clock = the 3-fold lug phase. Tilt 0.20°.
- Build: one solid, 182 analytic faces, 7 fillets all OK, reproducible in fresh processes.
  The under-lug floors are fitted concave horizontal-axis cylinders (R ≈ 170–240 mm, rms
  0.03–0.10 mm). Inside it1, the builder self-check (NOT QA) drove four attempts; each change went
  back through measure (`MODELING_PLAN.md` §8).
- Independent verify returned **HALT**. Its own ICP did not converge (60 and then 500 iterations),
  so the gate is INVALID. Datum-frame numbers are inspection only:
  - scan→CAD: p95 0.244 / max 0.878. The max comes from 6 points at the lug-3 end.
  - CAD→scan: p95 0.357 / max 5.13 masked.
  - Datum audit: axis 0.010° / origin 0.005 mm; the clock differs by 1.89°.
- The owner chose "bu haliyle deliver et". The verdict stays HALT. The delivery scripts ran
  through a run-local wrapper that adds HALT to the deliverable list for this run only
  (`OD-G10/owner_override_2026-09-28.md`). The zip is `OD-G10_porta_filter_holder_RE_HALT_2026-09-28.zip`.

## Skill defects found

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `stl-re-verify/scripts/tier2_icp.py` | Cannot exclude CAD-side coverage regions, and its normal test is sign-free. On a part with large unscanned areas, ~13 % of pairs join a CAD face to the opposite wall with antiparallel normals, and ICP slides about the axis without converging. | open (main blocker of this run) |
| 2 | `stl-re-verify/scripts/observability.py` | Surfaces that are unscanned but have a line of sight count as observable (same as OD-H22 #3); only 4 % read unobservable here. | open |
| 3 | `stl-re-verify/scripts/verdict.py` render | VERDICT.md leaves out the datum-frame deviation block. | open |
| 4 | `stl-re-deliver` | No sanctioned owner-override path for HALT; every script refuses. The run used a run-local wrapper and recorded the override. | open (owner decision needed) |
| 5 | `stl-re-deliver/scripts/package_zip.py` | `qa/dev_arrays*.npz` (2 × 15 MB) was not treated as regenerable, and the 52.9 MiB zip exceeded the 30 MiB `SendUserFile` limit. | fixed: npz added to REGENERABLE; size rule in `references/delivery-package.md` |
| 6 | `stl-re-intake-datum/scripts/align.py` | The self-referential-noise finding only fires when the region description string matches; it did not fire here (noise and primary were both on the lug pads). | open |
| 7 | `stl-re-intake-datum` | `origin.xy` / axis primary crop cannot select one wall of a multi-wall cup (the crop is a cylinder about the axis), so an axis primary could not be used. | open |
| 8 | intake (this run) | The measurement request header said 16 rows; the tables hold 15. | run-local |
