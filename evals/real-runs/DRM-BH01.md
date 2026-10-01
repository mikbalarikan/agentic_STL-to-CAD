# Real run: DRM-BH01 Dreame brushes housing (2026-09-30 → 2026-10-01)

Second real run of the v1 skills, on a part with no golden record. The owner supplied only a decimated
scan (`dreame_brushes_housing_decimated_20MB.stl`, 391,997 faces) and the instruction "p95 plastik parça
toleransı kullan". No calipers, no photos. Records are copied under `DRM-BH01/`; the full run folder lived
in the session scratchpad and was delivered as one zip (`dreame_brushes_housing_RE_BAND_NOT_MET_2026-10-01.zip`,
sha256 `595b7f8c…`, 26 MB).

## Inputs and decisions
- Regime: baseline-skill plastic, p95 ≤ 0.30 / max ≤ 0.80 mm (owner wording → CLAUDE.md shorthand).
- Scan-only and decimated → inspection-only; best possible verdict APPROVED_WITH_LIMITATIONS.
- The scan is an **assembly** (housing + gearbox cover + motor + screws + loose wires). Owner chose one fused
  solid of housing + gearbox block + motor envelope (decision card, PART-CLASS).
- After the first main-geometry model (self-check p95 ≈ 2.9 mm) the owner chose "continue detailing".

## How the model was built
- Datum: T1 bore axis (align.py axis primary on a documented crop; STOP rule met at 0.0128 vs circle noise
  0.0133), gearbox end face (origin), flange-top normal (clock). Model frame = fixed permutation of the datum frame.
- Main body: measured constant cross-section (two bores, offset strip, flanges, labyrinth edge) extruded per
  trough group, each placed on its measured axis line (warp ~0.1–0.3°). Gearbox block: fitted line+arc
  sketch. Motor: stepped cylinders. 133 rib slabs from paired opposite plane patches.
- Details: five parallel region agents (R1 gearbox, R2 trough start, R3 underside/motor, R4 +X end, R5 upper
  edge) wrote measured add/cut primitives with their own scripts; a second round fixed verifier clusters.

## Result
| | it1 | it2 |
|---|---|---|
| Validity | FAIL (2 non-manifold edges at the +X end) | PASS, both frames, watertight 0.005/0.05 |
| scan→CAD masked p95 / max | 1.937 / 16.303 | 1.161 / 5.965 |
| observable CAD→scan p95 / max | 1.309 / 7.709 | 1.004 / 7.693 |
| Verdict | REVISE | BAND_NOT_MET, owner ACCEPT-BAND (gate `6a97111efe32`) |

Trough body (x 66–150) p95 0.597 mm. Verifier estimate: even with every listed cluster perfect, masked p95
stays ~0.80 (sharp blends, warp, scanned interior/inter-part surfaces: 4.6 % of scan vertices lie inside the
solid). Delivered with 11 limitations and re-run triggers; "not fit for tooling/fit-checking".

## Skill defects and gaps found (status on this branch)
| # | Where | Finding | Status |
|---|---|---|---|
| 1 | `stl-re-intake-datum/scripts/align.py` | axis-primary crop is an infinite cylinder; on a long tray it takes end blocks and biases the normals point solve (pass-1 radial rms 0.33 mm). Needed a run-local face crop (`intake/datum_crop.py`) | open |
| 2 | `stl-re-intake-datum/scripts/datum_fit.py noise --circle-z` | needs a closed section loop; an open half-bore has none, so circle noise came from a run helper | open |
| 3 | `stl-re-intake-datum/scripts/align.py` | exports `aligned_work.stl` from the spec mesh (the crop), not from `work.stl`; a helper re-applied the matrix | open |
| 4 | `stl-re-measure-intent/scripts/param_table.py` | rejects structured geometry (fitted edge lists, boxes, region primitives); moved to `measure/geometry.json` pinned by sha256 in `params.json#geometry_tables` | open (contract extension used in this run) |
| 5 | `stl-re-rebuild-build123d/scripts/validate_step.py` / `export_frames.py` | `nonmanifold_edges` is report-only, so it1 exported "pass" with 2 non-manifold edges that verify then failed | open |
| 6 | rebuild (OCC mesher) | a large cylinder face crossed by many rib intersections triangulated with holes in one frame only; fixed in model.py by `ShapeUpgrade_ShapeDivideArea` (faces > 1500 mm²) + `ShapeFix_Shape` | worked around in run |
| 7 | `stl-re-deliver/scripts/package_zip.py` | `*.npz` QA arrays were not treated as regenerable, so the zip was 90 MB, over the 30 MiB SendUserFile limit | **fixed**: `*.npz` added to REGENERABLE; delivery-package.md documents the limit |
| 8 | region-agent workflow | "all adds, then all cuts" ordering forced a polygon-band workaround (faceted cylinders) until an exact `diff` primitive was added | worked around in run (`diff` type) |
