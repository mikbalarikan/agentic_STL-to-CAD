# stl2dxf-facet-film skill validation — 3-piece mini kit, Daytona 126500

Date: 2026-08-23. Input: `Daytone 126500 v2.stl` (734,459 faces, 2,203,377 verts, never read into context).
Deliverables: `C:/spk/skilltest/mini_kit.dxf` (sha256 `8fdfa19357601f4fa546617c05fd93dbe01388ff051e50b6c2ed8d94c6de5e3f`, with `PYTHONHASHSEED=0`), `mini_kit.png`, `kit_manifest.json`, `aligned.stl` + `T_canonical.npy`.

## Stage 0 — canonical frame (measured vs reference)

| quantity | measured | reference | delta |
|---|---|---|---|
| raw scan tilt | 12.3 deg | 12.3 deg | 0 |
| raw origin (scan coords) | (61.5, 40.5, -239.1) | z ~ -240 | ok |
| crystal flat radius | 14.50 (silhouette-ring fit) / 14.59 (0.07 mm z-drop crossing) / 14.10-14.36 (strict 0.07 plane-inlier ring) | 14.65-14.70 | -0.06..-0.55 method-dependent |
| caseback z | -12.197 | ~ -12.14 | -0.06 |
| lug-to-lug | 47.4-47.6 (probe), flank-tip chord 46.0 (trimmed) / 47.9 (raw) | ~46.9 | +-1.0 |
| crown side | +X protrusion +23.40 vs 9-side -19.65 | crown = +X | ok |

Method: PCA thickness axis -> dominant top flat cluster -> LSQ plane 0.07 mm rejection -> boundary-ring Kasa circle -> in-plane PCA for 12-6 -> crown-protrusion sign test. Worked first try; reference tilt/origin/caseback all reproduced.

## Recipe A — discs

- **CRYSTAL D29.30**: bezel bore is **not fittable from this scan** — the crystal->bezel groove is bridged/blended (radial profile drops smoothly r14.4->16.4, no separate loop at any z in -1.6..-2.4). Used the record's *typed* bore D30.0 - 2x0.35. Crosscheck: measured crystal-flat boundary D29.01.
- **CASEBACK D26.84**: fitted flat-boundary R 13.618 (operator's 3-point pick: 13.469; the rim is a smooth dome->chamfer blend, +-0.15 mm subjectivity) - 0.2 inset. Expected ~D26.5, delta +0.30.

## Recipe C — FLANK_9

Boundary curves via angular outer-silhouette (0.5 deg bins), top edge = highest wall point with nz <= +0.30 capped z <= -4.0, bottom = lowest with nz >= -0.60 capped z >= -11.5, median-continuity filter, degree-5 smoothing splines (max resid 0.46/0.44 mm — boundary-criterion noise, not scan noise), tips trimmed at width >= 2.5 mm; `ruled_sheet.unroll_strip` on 200 matched samples.

| quantity | measured | reference |
|---|---|---|
| lug-tip chord | 46.01 | 46.9 |
| developed bbox | 48.88 x 7.79 | 49.0 x 7.1-7.7 |
| developed area | 252.8 mm2 | 244-251 |
| K_abs_mean | 2.93e-4 | 5.7e-4 (gate <= 1.5e-2) PASS |
| K_abs_max | 2.50e-2 | (script docstring gate 6.5e-2) PASS |
| flattening area err / edge err | 0.0000 % / 0.0000 mm | gates 0.4 % / 0.09 mm PASS (vacuous — finding #3) |

Constant-z sections at z=-4/-11.5 (the task's literal hint) span only y +-17.8/+-11.5 -> a 23 mm piece, half the reference; the flank edges are curved ridges dipping at the lugs. Four plausible boundary-parameter choices gave 151-302 mm2 pieces, **all passing every gate**.

## Stage 5 — kit

`write_kit` (R2004, labels on, fillet 0.4) + `validate_kit(expect_pieces=3)`:

    {"n_loops": 3, "problems": [], "min_segment_mm": 0.0513, "min_gap_mm": 1.500, "ok": true}

Sheet 57.64 x 38.22 mm. PNG inspected: two clean discs + bowed flank strip with squared, filleted ends — shapes sane.

## Skill findings (ordered by severity)

1. **BUG — `write_kit` never persists $EXTMIN/$EXTMAX.** ezdxf's save path (`Drawing.update_extents()`, document.py:663) overwrites the header vars from `msp.dxf.extmin/extmax`, which the writer never sets; the shipped file carries the +-1e20 defaults — exactly the "bogus extents" NX defect the contract promises to fix. Fix: set `msp.dxf.extmin/extmax` or call `ezdxf.appsettings.update_extents(doc)` before `saveas`. And `validate_kit` doesn't check extents despite its docstring listing "extents sane".
2. **BUG — byte-determinism claim incomplete.** Two identical runs in separate processes produce different bytes: OBJECTS-section ordering (LAYOUT vs ACDBPLACEHOLDER) follows Python hash randomization. The self-test passes only because it writes twice in-process. Requires pinning PYTHONHASHSEED (or sorting in the writer); the pitfall card should say so.
3. **GATE HOLE — `flattening_report` is vacuous in the documented Recipe C flow.** `unroll_strip` is per-triangle isometric to the sampled strip, so comparing the strip to its own development always yields ~0 area/length error; the gate can only catch gross self-folding. The historical 0.4 %/0.09 mm numbers measured NX's *solver* against the sheet. To be a real gate it must compare sheet (or development) against the *mesh* (e.g. sheet-to-scan deviation, or strain of a projected fit).
4. **GAP — Recipe C step 1 (boundary extraction) is underspecified and is where all the difficulty lives.** "face_adjacency_angles > 30-40 deg or sections just inside the edges" fails on this real scan: ridges are blend-rounded and the top boundary changes feature type along its length (bezel groove at the belly, convex chamfer ridge on the lugs). I needed: outer-silhouette binning, normal thresholds + catalogue z-caps, a median continuity filter, and tip trimming at min width — none of it in the skill. Since all sheet gates pass regardless of boundary choice, piece dimensions are effectively ungated; promote the catalogue bbox/area comparison to a hard regression gate on the reference watches.
5. **DOC — catalogue "flank z-range -11.5..-4.0" misleads:** the edges are curved; z=-4 is only the belly top and -11.5 only the lug underside. (The task hint inherited this misreading.) State it as curves, with belly and tip values.
6. **DOC — "fit the bezel bore" overpromises:** on this scan the bore/groove doesn't exist as geometry (scanner bridging); D30.0 was typed knowledge. Say explicitly the bore is typed unless a groove is resolvable. Similarly "crystal flat radius 14.65-14.70" lacks a measurement definition — three sane methods gave 14.10-14.59.
7. **DOC — caseback "flat-centre boundary" is a smooth blend** on the scan; define the boundary criterion (e.g. radius where surface leaves the caseback plane fit by X mm), else +-0.15 mm subjectivity (my D26.84 vs 26.54).
8. **INCONSISTENCY — developability gates:** SKILL.md gives only K_abs_mean <= 1.5e-2; ruled_sheet's docstring adds K_abs_max <= 6.5e-2; the parameter card omits the max; `developability()` returns no pass flag. Pick one contract and enforce it in code.
9. **NIT — `fillet_ring`'s min_seg filter (0.05) equals `validate_kit`'s min-segment gate (0.05)** — output can land at the boundary (mine: 0.0513 mm). Filter at ~0.08-0.1 for margin.
10. **GAP — no bundled smoothing/fit helper** although Recipe B pseudocode calls `fit_smoothing_spline(..., reject=0.07)`; implementers roll their own (scipy splprep here). Note that boundary-criterion noise (0.2-0.5 mm) dominates the 0.07 value, which only applies to raw scan-point fits.
11. **FRAME TRAP:** the task said the 9-side flank is on "+Y"; in the skill's canonical frame it is -X (the NX R1 record's bracelet-along-X frame had 9-side = +Y — the confusion's source). One sanity line in Stage 0 ("after alignment: 9-flank -X, crown +X") would prevent it. Also: K spikes at degenerate strip tips — add "trim ends where width < ~2.5 mm before gating".

## What worked as advertised

`unroll_strip`/`developability` numerics (self-tests pass; K in the record's range); `write_kit`/`validate_kit` API and defect gates; parameter card values (0.35/0.2 clearances, R0.4 fillet, 1.0 gap) all directly usable; Stage-0 recipe reproduced tilt/origin/caseback-z to 0.06 mm; "never read raw STL" workflow held (35 MB loads in ~1.3 s).
