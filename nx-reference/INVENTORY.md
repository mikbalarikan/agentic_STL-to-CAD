# NX reverse-engineering projects: intake inventory (20261105)

Agentic scan/STL-to-CAD projects done on this laptop with Siemens NX 2206, driven by Claude Code through NXOpen Python journals (headless `run_journal.exe`) and the NX MCP server. Collected for the build123d STL->STEP skill redesign in `mikbalarikan/agentic_STL-to-CAD`.

## How to read this package

- The package is split into 4 zips (each < 90 MB). Every zip holds this same `INVENTORY.md` at its root. Each project is one top-level folder:
  - `nx_re_projects_20261105_part1.zip`: `_harness/`, `chest_ch001/`, `lexus_seat_clip/`, `dreame_dustbin_air_inlet/`, `dreame_mop_early_nx/`
  - `nx_re_projects_20261105_part2.zip`: `left_thigh_outer_inner/`, `dreame_brush_core/`
  - `nx_re_projects_20261105_part3.zip`: `left_thigh_clean_rebuild/`, `r385_pump/`
  - `nx_re_projects_20261105_part4.zip`: `ulka_pump/`, `dreame_bottom_cover/`
- Inside a project: `work/` or `ws/<name>/` = NX work folder (journals, analysis scripts, logs, outputs); `project/...` = the client project folder; `drive_source/` = original source folder with scans; `transcripts/` = Claude Code session transcripts (`*.jsonl`, plus `<id>_subagents/` for sub-agent runs).
- Transcripts were cleaned: base64 images/documents replaced by `[image removed for size]`, any string longer than 20,000 characters cut with `[...truncated N chars]`. Tool calls, tool inputs and the agent's text are kept.
- `_meta/tool_stats.json` (in part 1) = per-project counts of tool calls, NXOpen API names and script names found in the transcripts.
- Secrets/privacy: no `.env`, licence, key or credential files were copied. Copies were scanned and matches replaced with `<REDACTED>` (see the redaction list at the end). Originals were not modified.
- Size rules: text files <= 3 MB, images <= 300 KB (12 MB per project), PDFs <= 1 MB (8 MB per project), JSON <= 512 KB; final/input CAD (STEP, PRT, scans) <= 20 MB each and <= 45 MB per project (priority: input scans, then newest STEP, then PRT). Intermediate CAD (iteration .prt/.stl/.stp) was not copied. Larger or over-budget final/input CAD files are listed with path, size and sha256.

## Projects at a glance

| Project | Zip | Files | Staged size | Transcripts |
|---|---|---|---|---|
| `_harness` | part1 | 301 | 6.8 MB | 0 |
| `dreame_bottom_cover` | part4 | 92 | 17.4 MB | 1 |
| `dreame_brush_core` | part2 | 187 | 42.9 MB | 2 |
| `dreame_dustbin_air_inlet` | part1 | 35 | 3.1 MB | 1 |
| `dreame_mop_early_nx` | part1 | 1 | 3.1 MB | 1 |
| `r385_pump` | part3 | 758 | 83.1 MB | 9 |
| `ulka_pump` | part4 | 524 | 68.6 MB | 5 |
| `lexus_seat_clip` | part1 | 141 | 27.1 MB | 1 |
| `left_thigh_outer_inner` | part2 | 1750 | 191.6 MB | 32 |
| `left_thigh_clean_rebuild` | part3 | 1716 | 135.3 MB | 30 |
| `chest_ch001` | part1 | 2588 | 190.5 MB | 27 |

## _harness (shared: NX MCP server + NX skills used by every project)
- **Purpose:** the tooling every project below ran on. Siemens NX 2206 on Windows, driven by Claude Code.
- **Source folders (original paths):** `H:\My Drive\NX HARNESS VERSIONS\v2\mcp-repo`, `...\v2\addin`, `...\v2\skills\nx-reverse-engineering`, `...\v2\skills\nx-journal-core`, `...\v2\skills\nx-modeling-strategy`

### NX MCP server (`mcp-repo/`)
- Architecture (`mcp-repo/README.md`, `docs/architecture.md`): `MCP client <-stdio-> Python sidecar (nx_mcp.server) <-authenticated loopback JSON-RPC-> NX bridge journal <-NXOpen-> NX`.
  The sidecar starts without NX; tools return `NX_BRIDGE_UNAVAILABLE` until a journal inside NX starts the bridge (`examples/start_nx_bridge.py`).
- Config used (`mcp-repo/.mcp.json`): server `nx-mcp`, stdio, `python -m nx_mcp.server`, env `NX_MCP_WORKSPACE=C:\NX_MCP_WORKSPACE`, `NX_MCP_STATE_DIR`.
- Default ("certified") tools, 16 (`src/nx_mcp/certified.py`): `nx_status`, `nx_create_part`, `nx_open_part`, `nx_save_part`, `nx_close_part`, `nx_export_step`,
  `nx_list_sketches`, `nx_list_bodies`, `nx_list_features`, `nx_create_sketch`, `nx_sketch_line`, `nx_sketch_rectangle`, `nx_finish_sketch`, `nx_extrude`, `nx_undo`, `nx_fit_view`.
- Experimental tools (hidden unless `NX_MCP_ENABLE_EXPERIMENTAL=1`; journal tools also need `NX_MCP_ENABLE_JOURNAL=1`; `src/nx_mcp/tools/*.py`):
  `nx_add_base_view nx_add_component nx_add_dimension nx_add_projection_view nx_blend nx_boolean nx_chamfer nx_create_drawing nx_delete_feature nx_edit_feature nx_export_drawing_pdf nx_fit_view nx_get_bounding_box nx_get_feature_info nx_hole nx_import_geometry nx_list_components nx_list_open_parts nx_mate_component nx_measure_angle nx_measure_distance nx_measure_volume nx_mirror_body nx_pattern nx_record_start nx_record_stop nx_reposition_component nx_revolve nx_run_journal nx_save_as nx_screenshot nx_set_view nx_sketch_arc nx_sketch_constraint nx_sweep`.
- GUI bridge (`addin/NxMcpGuiBridge.cs`, `mcp-repo/nx_gui_bridge/`, `docs/gui-bridge.md`): C# add-in loaded into a live interactive NX session so journals can run against the user's open part (used in the Left Thigh "live part" sessions).

### How the agent actually drove NX in the RE projects
- The certified MCP surface only covers sketch-rectangle-extrude. **For the scan-to-CAD work the agent almost always wrote NXOpen Python journals and ran them headless**
  with NX's `run_journal.exe` from Bash/PowerShell (see `_meta/tool_stats.json`: thousands of shell calls, hundreds of `run_journal` launches, near-zero `mcp__nx*` calls).
- Journals import the helper modules in `skills/nx-journal-core/scripts/` (`nxh.py` core + measurement, `nxf.py` feature helpers, `nxa.py` assembly helpers),
  print JSON results to a log, and the agent reads the log back. Mesh analysis (sections, primitive fits, deviation) runs **outside NX** in plain Python (numpy / trimesh / open3d).
- `skills/nx-reverse-engineering/SKILL.md` + `references/` + `scripts/`: STL import, scan alignment with fitted datums + Move Object, facet-region selection,
  Fit Surface (plane/cylinder/cone/sphere/freeform) with snapping, Section/Intersection curves of the mesh, Fit Curve, turning fitted surfaces into solids
  (sketch on fitted datum, Replace Face, Extend+Trim+Sew, Thicken), rounding to design intent, signed scan-to-CAD deviation check.
- `skills/nx-modeling-strategy/SKILL.md`: plan-before-journal rules (classify the job, base-shape approach, feature order, feature budget, checks).

### Files in package (_harness)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## dreame_bottom_cover
- **Purpose / part type:** Dreame robot-mop module bottom cover: injection-moulded open frame, scan extents about 195 x 89 x 26 mm (rail with channel wall, hook-side beam with 4 snap tabs plus a 5th short hook, grille end with stepped twin troughs, bowl end with two scoop bowls, cells and fins, rib combs, two latch housings, two separate latch sliders). Class "rebuild from scan": the deliverable is a native parametric NX 2206 part + STEP, not a surface wrap. The user asked for the NX route after three build123d iterations (it1-it3, outside NX) were judged not clean / not parametric.
- **Dates:** 2026-10-07 / 2026-10-08 (build + report). Later in the same session the result was copied into the v2 skill repo as `examples/dreame_bottom_cover`. User verdict on the result: "harika kalite onaylandi" (approved), although the numeric plastic band was not met.
- **Sessions:** `transcripts/8321884a-def9-457d-bea2-1af9aab9a19b.jsonl` (one long session, about 1350 events; Read 81, PowerShell 59, Write 41, Bash 33, Edit 27; about 65 python runs, 5 headless NX runs).
- **Source folders (original paths):** work `C:\NX_MCP_WORKSPACE\dreame_cover` (`build.py`, `nxlib\`, `an\`, `out\`); scan and earlier build123d run in `C:\Users\marya\Downloads\dreame_mop_assembly_bottom_cover\` (scan 242 MB / 4.84 M triangles; `run\intake\aligned_work.stl` = 400 k-triangle datum-aligned working copy; `run\intake\alignment.json`); delivery `...\dreame_mop_assembly_bottom_cover\nx_re\`; skill snapshot `H:\My Drive\NX HARNESS VERSIONS\v2\skills\nx-reverse-engineering\examples\dreame_bottom_cover`.

### Workflow (step by step, reconstructed from scripts + logs)
1. **Intake reuse.** The datum frame came from the earlier build123d run (`run/intake/alignment.json`): XY = top flange face (z=0, material at -Z, latch tongues +Z), XZ = outer face of the hook-side wall (y=0, part at -Y), YZ = grille-end face (x=0, part at +X). No new alignment was done; ICP was not used in this job.
2. **Scan cache + de-warp** (`an/common.py`, `an/overview.py`). Read the aligned 400 k STL with a numpy binary reader; fit a smooth field dz(x,y) (cubic in x, linear in y) to the flange top (rail and beam top faces, iterative 3-sigma clipping, `common.fit_warp`) and subtract it, because the real flange is bowed about 1.1 mm toward the bowl end. The CAD is built flat; the de-warped scan is used for measuring only (field saved as `an/warp.json`). Height maps `hmap_top/bot/thick.png` give the overview of regions.
3. **Sections outside NX** (`an/sec.py`, `an/zones.py`, `an/ztable.py`, `an/shade.py`). Plot x / y / z sections of the scan (optionally stacked over a station range with `avg W`) as PNGs that the agent reads visually, then decides primitives per region. NX was never asked to measure the 400 k mesh (`nxre.Scan` too slow).
4. **Primitive fits per region** (`an/fit.py`, `an/pw.py`, `an/m_rail*.py`, `m_beam.py`, `m_grille*.py`, `m_hook*.py`, `m_deck*.py`, `m_bowl*.py` x7). `fit.pts` stacks sections over a range into 2D points; `pw.env/fit` takes the top or bottom envelope and fits a piecewise line / flat / arc chain with junctions at the intersection of neighbouring primitives. Typical fit rms 0.004-0.04 mm. Results: rail channel wall = one arc R18.1 centred on the flange plane (rms 0.03); bowl B = surface of revolution about a vertical axis with a two-arc meridian (rms 0.018); bowl A = NOT a revolve (vertical axis sd 0.34 mm; tilted 25/30/35 deg axis in `m_bowl7.py` gave no clear optimum; its plan sections are circles whose centre drifts with depth) so it became a Through Curves loft through six plan sections; deck = two cones plus a cap plane; hook-side corner = skin whose straight generators run 17.5 deg to X (found from straight height contours), built as an Extrude along a skew vector; grille end = envelope block minus one "void" profile per x-zone (4 on the rail side, 3 on the hook side).
5. **Round values to design intent.** 109 named master expressions (e.g. `fl_t` 1.9, `ch_R` 18.1, `ch_t` 2.05, `tab_pitch` 28.2, `tab_w` 7.8, `bowl_t` 1.8, `rib_t` 1.4, `web_pitch` 8.05, `end_x` 192.6), values snapped to a 0.05 mm grid (scan noise floor 0.04 mm). Scale never verified by caliper.
6. **Probe the NX mechanics first** (`probe1.py`, `probe2.py`): one fully constrained profile sketch + extrude + regeneration; and a matrix of revolve-about-tilted-axis cases (see traps).
7. **Stage-wise journal** (`build.py` stage A: rail, beam, bead, tabs; stage B: grille end; `nxlib/st_c.py` stage C: bowl end, hook-side corner; `nxlib/st_d.py` stage D: rail underside, ribs/grid, latch housings, flange details, sliders; `run.ps1` runs it with a stop-after-stage argument). Every run builds the whole part from scratch in 1.5-4 min, exports an STL of all solids (`nxre.stl_export`) and writes `out/build.json` (checks, sketch states, solids). Thin shells: shell solid united first, then void subtracted, so later fins/walls are trimmed by the void.
8. **Overlay-correct loop** (`an/ovl.py`): CAD section (red) over scan section (black) in the same datum frame, e.g. `python an\ovl.py out\X.stl o.png x 50,115 lim -86 -64 -19 2 cols 2`; the agent reads the PNG, edits numbers in the stage file, reruns. This loop found, for example, that a straight tangent line from a wall corner to a bowl circle (the assumed intent) was 1.3-2 mm off and that a second arc was needed.
9. **Deviation** (`an/dev.py`, cadgenbench venv with open3d): sample 800 k scan points, closest-point distance to the CAD tessellation via `o3d.t.geometry.RaycastingScene`, sign from the CAD face normal, zone table by x, named single-sheet artefact masks (box predicates), masked and unmasked rows both reported. Series `dev_d1..d5`, `dev_probe1`, `dev_final` document the improvement per iteration.
10. **Finalize:** regeneration test (14 masters changed one by one, update, back; `tab_pitch` 28.2 -> 27.6 moved the last tab to x=136.0 as computed), `nxh.examine_geometry`, STEP AP242 export + `nxf.step_roundtrip_check`, OCP BRepCheck of the STEP, review part with the scan (`review.py`: copy of the prt, `nxre.stl_import` of the 137 k-facet datum-frame scan, moved to layer 10) so the user can overlay in NX, report in Turkish (`REPORT.md`).

### NX tools and NXOpen APIs used
- Launch: `run.ps1` -> skill launcher `run_journal.ps1 -Script build.py -WorkDir out -JArgs out <stage> -TimeoutSec 1500` (NX 2206 batch `run_journal.exe`, embedded Python 3.10). Env `NXH_DIR`, `NXRE_DIR` set by the launcher. Analysis in system Python 3.13 (numpy, scipy, trimesh, matplotlib) and the cadgenbench venv (open3d).
- Helper modules: `nxh` (new_part, Datums, expr, extrude, unite/subtract, datum_plane, point, volume, bbox, solids, examine_geometry, body_ok, feature_errors, undo_to/mark, write_json, Check), `nxf` (new_sketch, add, pdim, cg, help_at, vertical, revolve, through_curves, pattern_linear, datum_axis, to_reference, step_roundtrip_check), `nxre` (stl_export, stl_import). tool_stats shows no certified nx-mcp tools used.
- Job-local sketch layer `nxlib/ps.py` (`Sketch(part, dat, "yz"|"xz"|"xy", name, on=, origin=, vax=, hax=, shift=)` and `.profile(verts, arcs)`; `FREE`, `on(axis)` markers) plus `nxlib/geo.py` (2D line/circle intersections, `circ_circ`, `circ_at_v`). It draws a vertex chain of lines and arcs, then constrains it generically to DOF 0: inferred coincidence off; horizontal/vertical on axis-parallel lines; one distance dimension per tied vertex group from the datum axes; point-on-axis constraint instead of a zero dimension; one radius dimension per arc. Result: 71 sketches, 772 dimensions, 0 automatic dimensions.
- Features in the 269-feature tree: 71 sketches, 68 Extrude, 4 Revolve, 2 Through Curves, 4 Pattern Feature, 1 Pattern Geometry, 1 Mirror Geometry, 7 booleans, 14 datums. NXOpen classes seen: `Curves.CreateLine/CreateArc`, sketch constraint and dimension creation, RevolveBuilder, ThroughCurves builder, PatternFeature, Mirror, STLImportBuilder (via `nxre`).

### Accuracy / deviation results
Source: `work/an/dev_final.json`, `work/out/review.json`, REPORT.md. 800 k samples of the 400 k-triangle aligned working copy (+ = scan outside CAD); builder-run, not an independent QA, not on the full 4.84 M-triangle scan.

| Metric | rms | p50 | p90 | p95 | p99 | >0.3 | >0.8 |
|---|---|---|---|---|---|---|---|
| scan->CAD, de-warped, artefacts masked (5.1 %) | 0.308 | 0.084 | 0.432 | 0.595 | 1.231 | 19.1 % | 2.7 % |
| scan->CAD, de-warped, unmasked | 0.442 | 0.093 | 0.550 | 1.042 | 1.892 | 22.7 % | 6.6 % |
| scan->CAD, raw scan (rigid only), masked | 0.442 | 0.188 | - | 0.929 | 1.298 | 36.5 % | 9.3 % |
| CAD->scan, whole CAD | 0.443 | 0.076 | 0.605 | 1.064 | 1.897 | 19.4 % | 7.6 % |

- Plastic band (p95 <= 0.30, max <= 0.80 mm) NOT met. By x zone (`scan_to_cad_by_x`): p95 0.40 at x 0-20 up to 0.79 at x 160-180 (bowl end worst: hook-side run-out and floor round of bowl A, step between rail channel and bowl B, deck).
- Iteration series from `an/dev_d*.json` (masked p95): d1 1.33, d3 0.75, d5 0.594 (rms 0.58 -> 0.31). p50 stays about 0.085 mm (noise floor), so the p95 tail is localised feature error, not global misalignment.
- Comparison: the earlier build123d it3 (its own protocol with ICP and different masks) had p95 1.07 / p50 0.186; not like-for-like.
- Model checks: 61/61 journal checks (volume deltas, cut/add proofs, solid count, feature errors); 71/71 sketches WellConstrained DOF 0; 14/14 regeneration tests; Examine Geometry on the 3 native solids all counters 0; STEP round trip into NX 3 solids, volume diff <= 9e-6; OCP BRepCheck 3 solids valid.
- Open defect: Examine Geometry on the RE-IMPORTED frame from STEP reports 96 face-intersection findings (native 0); cause not investigated. Not modelled: edge blends, general draft, two small domes on the flange.

### What worked / what failed
- Worked: measuring entirely outside NX on the datum-aligned numpy mesh (sections -> line/arc/piecewise fits -> per-region intent), then building with fully constrained sketches driven by named expressions. Staged build-from-scratch plus CAD-over-scan section overlay after each stage. De-warping the scan for measuring only while keeping the CAD flat. Per-region intent discovery before modelling (revolve vs loft vs skew extrude decided from fit residuals and straight-contour directions). Artefact masks as explicit box predicates, with masked and unmasked rows side by side. Volume-delta proofs for every cut/add in the journal so silent boolean failures show up.
- Failed / traps:
  - `Sketch.AddGeometry` with inferred coincidence also ties arc CENTRES that coincide -> concentric shells OverConstrained; add with `infer=False` and create end-point coincidences yourself.
  - A measured arc centre is never equidistant from two computed junctions; draw every arc through BOTH end points and let the centre only choose the side, otherwise one end stays open (2 DOF).
  - A 180 deg arc given by end points + centre is ambiguous (it bulged the wrong way; flange recesses removed half the volume): split at the apex.
  - Revolve about a TILTED axis fails ("Unable to create revolved body from the specified section, axis and parameters") when on-axis vertices are held by rounded coordinate dimensions. `probe2.json`: a profile with vertices at 0.0 on the axis FAILED, the same profile 0.3 mm off the axis was OK, a plain on-axis rectangle was OK; `nxh.axis` and a datum axis behave the same. Fix: put on-axis vertices on the datum axis with a point-on-curve constraint (`ps.on(axis)`).
  - `nxh.bbox` of a body with tilted-revolve faces is padded by millimetres (z -19.5 vs about -15.7 computed): do not check positions from it.
  - STL export via `nxre.stl_export`: a name ending `.tmp` was not found afterwards; it must end `.stl`.
  - Pattern pitch changes do not change volume: prove pitch regeneration by a position.
  - Bowl A as a tilted revolve was abandoned (first attempt failed with the on-axis cause above, then the data showed it was not a revolve anyway).
  - Reasoned, never observed: a sketch on an offset plane dimensioned to absolute datum axes may be solved against them; the bowl sketches therefore take a datum axis through their own origin (`vax=`).
  - Assumptions flagged to the user: latch housings modelled as solid boxes (closed in the scan); foot pads (likely felt) added as separate features; scale not caliper-verified.

### Key files (path relative to STAGE\dreame_bottom_cover)
- `work/nxlib/ps.py` - generic fully-constrained line/arc profile sketcher (best idea to port to build123d: vertex chain + arcs -> sketch with named dims).
- `work/nxlib/geo.py` - 2D intersection helpers (circ_circ, circ_at_v, line-circle) used to compute junctions.
- `work/build.py` - journal skeleton: Ctx class (expressions, checks, sketch log), stage A rail/beam/tabs, final checks, STEP/regeneration block.
- `work/nxlib/st_c.py` - bowl end: revolve meridian, Through Curves loft for bowl A, deck cones, skew extrude.
- `work/nxlib/st_d.py` - rail underside, rib/grid patterns, mirrored latch housings, sliders.
- `work/probe2.py`, `work/out/probe2.json` - tilted-axis revolve experiment and its result matrix.
- `work/probe1.py`, `work/out/probe1.json` - sketch + extrude + regen smoke test.
- `work/an/common.py` - STL reader, Mesh.section slicer, polynomial warp fit and de-warp, sampling.
- `work/an/sec.py` - stacked section plotter (axis x|y|z, lim, avg, cols).
- `work/an/fit.py` - stacked-section point extraction and line/circle fitting.
- `work/an/pw.py` - piecewise line/flat/arc envelope fit with junction intersections.
- `work/an/m_bowl6.py`, `work/an/m_bowl7.py` - revolve-axis search (Nelder-Mead on radial spread) for tilted axes; shows how bowl A was rejected as a revolve.
- `work/an/ovl.py` - CAD-over-scan section overlay (the correction loop).
- `work/an/dev.py` - signed deviation with RaycastingScene, artefact masks, zone table, JSON output.
- `work/an/dev_final.json`, `dev_d1.json` ... `dev_d5.json` - deviation history.
- `work/out/build.json` and `work/out/dreame_mop_bottom_cover.log` - per-check results and the STEP translator log.
- `work/review.py` - open copy of the part, stl_import of the scan, move to layer 10, save.
- `work/run.ps1` - launcher that prints the build.json verdict (failed checks, sketches not DOF 0).
- `work/deliver/figures/overlay_plan_sections.png`, `overlay_y_sections.png` - what the overlay output looks like.
- v2 skill snapshot (outside STAGE, read-only): `...\skills\nx-reverse-engineering\examples\dreame_bottom_cover\README.md` and `REPORT.md` (Turkish) carry the same numbers and the trap list.

### Files in package (dreame_bottom_cover)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## dreame_brush_core
- **Purpose / part type:** Main brush of a Dreame robot vacuum (the black "with bristles" variant). A 170 mm long twisted
  hard core (flange r 16.45, 4 drive blades, 4 T-slots, 2 small + 2 wide grooves, twist lead 225.75 mm/turn, left hand,
  hex socket underneath, 54 tuft holes in 2 helical rows) plus soft parts: 4 silicone flaps with a bead on the free
  edge, and 54 bristle tufts. Deliverable: native parametric NX 2206 part + STEP, for a client demo
  (soft parts had to look real: the first delivery with "stick" bristles and no flaps was sent back).
- **Dates:** round 1 2026-10-08 (core + 54 one-piece conical tufts); round 2 2026-10-09/10 (4 flaps + 54 tufts x 61 filaments).
- **Sessions:** `transcripts/00db997d-dec5-46a3-8606-c7e627285bcd.jsonl` (round 1, Turkish chat),
  `transcripts/dd1460f7-90fd-471a-b6b0-87872f6e32f2.jsonl` (round 2).
- **Source folders (original paths):** work `C:\NX_MCP_WORKSPACE\dreame_brush` (build.py, build2.py, an\, nxlib\, qa\, qa2\, out\, out2\, fig\, fig2\);
  inputs under `Downloads\Projects\CAD_Projects` (three STLs: core-with-bristles 374 k tris, base/underside 223 k tris,
  assembled brush with flaps 6.5 M tris; plus a user reference CAD of a *different* 5-flap brush);
  delivery `Downloads\Projects\CAD_Projects\dreame_brush_core_with_bristles_nx`. STAGE copy: `dreame_brush_core\work\...`.
  The scans themselves are not in STAGE (only `out/scan_*_datum.stl` aligned copies).

### Workflow (step by step, reconstructed from scripts + logs)
Round 1 (core):
1. **Which scan is which.** `an/b0_baseline.py`, `an/b3_compare.py`, `an/f7_count_flaps.py`: the user's reference CAD (5 blades, lead 326.6, flange r 14.5)
   was compared with the scan (4 blades, lead 225.8, r 16.45) via r-z density and sections: two different cores. The reference was used only for
   feature order (discs, blades, cylinder, swept channel tools, blends, end details); its last body was an unsewn sheet. `b1_bristle_first.py` / `b2_base_first.py` = alignment trials.
2. **Datum frame of the core scan** `an/m1_align.py` -> `qa/T_bristles.json`: planes (blade tops, hub step, table), axis through hub-disc centre and idler
   counterbore centre, z0 = table plane under the rim, clock from the pinwheel blade edges. Residual: ridge centres <= 0.04 mm off axis over 140 mm.
3. **Twist + untwisted section** `an/m2_twist.py`: twist rate by slab-to-slab circular cross-correlation of r(theta) against a pooled profile (two passes),
   linear fit phase(z); then ALL core points are rotated back by -k(z-z0) and pooled, giving one sharp 2D section of a twisted part (`fig/m2_untwisted.png`).
4. **Section numbers** `an/m3_profile.py` (+ `m3_small`, `m3_vgroove`, `m3_zoom`): land radius, slot centre angles, neck width, foot width, floor radius, mouth round,
   small grooves, V-flats -> `qa/m3_profile.json`. Then `an/m4_base.py`, `m5_top.py` (flange, hub, rim, chamfer, idler bore, key notch),
   `m6_tufts.py` (27 roots per row, pitch, row angle, axial lean 40 deg, tip radius), `m7_hex.py`, `m7_underside.py`, `m8_misc.py`.
5. **Underside scan** `an/m7_base_align.py` -> `qa/T_base.json`: the base scan holds both brush ends (r 16.3 and r 14.3); only the r 16.3 end is used. It is aligned onto the
   already aligned core scan by trimmed point-to-plane ICP from 36 start clockings. The 180 deg ambiguity (2-fold core) is stated; `m7_recentre.py` found
   the underside bowl 0.23 mm off the hub disc.
6. **Build** `build.py` (779 lines): 13 sketches DOF 0, 61 top features, 76 named expressions; launched by `run.ps1` through run_journal, `show.py` prints the check table.
7. **Deviation** `an/dev.py` (full scan, every 2nd triangle), `dev_c2s.py` (CAD to scan), `dev_outliers.py`, `dev_under_icp.py`; render pairs scan/CAD `render.py`, `ovl.py` (section overlays).

Round 2 (flaps + fine bristles):
8. **Assembled scan -> core datum** `an/f1_align.py` -> `qa2/T_asm.json`: PCA axis + 36-clocking ICP of near-axis points onto the round-1 core CAD (hard surfaces only).
9. **Flap measurement** in the untwisted frame of the core: `an/f3_flap.py` (centre line y(x), thickness, tip radius per z band), `f4_flap_ends.py` (end tapers),
   `f8b_shoulder.py` (bead shoulder), `f9_flap_foot.py` (lower end sits on the drive blades), `f10_tuft_flap_gap.py`; `f0_view_ref.py` / `f2_look.py` for orientation.
10. **Build** `build2.py` (1304 lines; stages a-d = core unchanged, e = flaps, f = tufts, z = checks + regeneration + colours + STEP); `mk_build2.py` and `patch*.py` assembled it from build.py in pieces; `run2.ps1 -Stages abcdefz`.
11. **Checks** `an/f6_dev.py` (zone tables), `s1_step_check.py` (STEP re-import), `s2_flap_volume.py` + `s3_step_wall_probe.py` (independent volume/wall check of the twisted flap),
    `review2.py` / `asfound2.py` (re-open the delivered .prt, dump features, solids, expressions), `fixup_expr.py` (delete unused expressions), `test_pure.py` (NX-free test of the filament generator).
12. **Delivery** `deliver.py` / `deliver2.py` / `to_repo.py` + `fill_report.py` (REPORT.md / REPORT2.md, in Turkish).

### NX tools and NXOpen APIs used
- Headless journals through `run_journal.exe` (PowerShell `run.ps1` sets NXH_DIR / NXRE_DIR / NXBLADE_DIR, passes out dir + stage letters; 37 run_journal calls and 114 python calls in the logs). No NX MCP tools for the modelling.
- Helpers: `nxh` (new_part, expr, set_expr, solids, volume, bbox, examine_geometry, feature_errors, face_census, min_dist, mark/undo_to, save), `nxf` (revolve, extrude, datum_plane,
  datum_axis, axis_from, pattern_geometry, pattern_circular, move_object, trim_body, edge_blend, feature_group, step_export, step_roundtrip_check), `nxre`, `nxblade as nb`
  (`nb.swept(..., orientation="angular", angles=("-a","-a+twist_sweep"), solid=True)`), plus the project's own `nxlib/ps.py`.
- `nxlib/ps.py` `Sketch` class: `profile(verts, arcs)` with tangent constraints and formula-driven dimensions (DOF 0, no auto-dimensions), `centre_on`, `centre_dim`, `tangent(c1,c2,at=)` (fixed 4-argument
  `CreateTangentConstraint`), `circle`, `finish()` (solve + status), `section()` for downstream features. `nxlib/geo.py`: line/circle intersections and area helpers for corner formulas.
- NXOpen features seen: Revolve, Extrude, Swept (angular law), Pattern Geometry (circular + `Helix` layout, one body per pattern), Pattern Feature, Move Object, Trim Body, Edge Blend, Chamfer (dropped),
  Cylinder primitive with Unite/Subtract, Intersect, Datum Plane/Axis, Examine Geometry, feature groups, STEP/STL export (`CreateStlCreator` for sheet/convergent bodies).
- Scan side (plain Python, cadgenbench venv): numpy, scipy, open3d (RaycastingScene signed distance, ICP), matplotlib. `an/common.py` has a memory-mapped binary STL reader, a `Mesh` class
  (area-weighted sampling, plane_cut), `cyl()`, `rz_segments`, `closest()` and `stats()`.

### Accuracy / deviation results
- Round 1, hard surfaces, scan to CAD, 645 115 points (`qa/dev_final.json`): rms 0.088, p50 0.035, p90 0.105, **p95 0.159**, p99 0.37, **max 1.23 mm**; 0.04 % above 0.8 mm.
  p95 by zone: drive end 0.28, core z 6.5-30 0.14, 30-100 0.13, 100-160 0.12, idler end 0.20, lands 0.107, slots/grooves 0.143.
  Band used: p95 <= 0.30 / max <= 0.80 (borrowed from earlier jobs; the user gave no band): p95 met, max not met.
  Bristle zone (soft) scan to core+tufts p50 0.50, p95 1.33 mm (round-1 cones). 11 % of the CAD surface is not seen by any scan (T-slot feet, tuft holes).
- Round 2 (assembled scan, 1.39 M samples, each point assigned to its nearest part): core p50 0.033 / p95 0.165; flaps p50 0.20 / p95 0.97 (grows root to tip: p95 0.42 at r 7-10, 1.32 at r 15-18.5,
  which mirrors the flap flexing of -1..+2.4 mm in the scan); bristles p50 0.19 / p95 0.66. Alignment: 82 % of near-axis points within 0.3 mm, rms 0.074 (`qa2/T_asm.json`).
- Measured flap parameters (f3): body thickness 0.94 (0.91-0.95), bead 1.44, bead tip round R about 0.6, tip radius 17.15 to 16.25 over z 15-140.
- Model checks (report, from the build journal): 106/107 checks passed (the failing one = the dropped chamfer); 16/16 sketches DOF 0; Examine Geometry all 0; flap wall on the helix within 0.001-0.002 mm;
  11 master expressions changed and regenerated one by one, volumes returned to nominal within 1e-6; STEP re-import into NX 59 solids, max relative volume diff 3e-5; OpenCascade re-read 59 valid solids.
  Delivered: 59 solids (CORE 1, SILICONE_FLAP 4, BRISTLE_TUFT 54), 278 features, 97 expressions, STEP 9.1 MB. No independent QA, never opened in the NX GUI, no caliper data (scale from the scan only).

### What worked / what failed
- Worked: pooling all scan points untwisted (angle minus k*(z - z0)) gives a single crisp section of a helical part; twist rate by cross-correlation, not by feature tracking.
- Worked: one sketch of the section on an offset plane, Swept with an *angular law about a guide line on the axis*, Pattern Geometry, Subtract. The NX result matches the true helicoid to 0.004 mm; off-axis sections also work. Positive law angle = left-hand twist; start angle -a places the section at +a.
- Worked: every feature dimension is an expression or formula of about 100 masters, so the model regenerates; sketches are DOF 0 with tangent constraints and zero auto-dimensions.
- Worked: soft flap = twisted blank INTERSECT a revolved (r,z) outline envelope; bead = second, thicker blank INTERSECT a revolved band, Edge Blend on its outer helical edge chain, Unite, Trim Body at the end plane, Pattern Geometry x4.
- Worked: fine bristles = root plug + 61 Cylinder-Unite filaments (d 0.15) from a seeded generator that keeps every pair >= 0.02 mm apart; 3 tuft variants take every 3rd position (pattern count `ceiling((n-k)/3)`); 183 cylinders build in 30 s; 3294 filaments, part 14 MB.
- Worked: independent checks that do not trust NX measure: fine tessellation volume and wall-probe points on the STEP, because OpenCascade default VolumeProperties was 0.3 % off on a thin twisted body.
- Failed / traps:
  1. Scan file names are misleading ("core" scans are a sub-part; flaps exist only in the assembled scan; two different brushes share names). List every scan of the product and compare r-z density first.
  2. Two-offset Chamfer on a chain of 10 helical edges is not repeatable (removed volume 8.9 / 19.7 / 12.6 mm3 across three runs; STEP re-import 0.67 % short). Removed from the model; use a symmetric chamfer or a blend, or omit.
  3. Angles in sweep-law formulas must be unitless expressions ("Dimension mismatch" otherwise).
  4. Pattern Geometry Helix layout accepts ONE body per pattern. The old `ps.tangent(c1,c2)` 2-argument call is broken.
  5. Sheet/convergent bodies export to STL only via CreateStlCreator. `inspect_part.py` took 25 min with a multi-million-facet convergent body in the part.
  6. A feature limit given as an absolute height breaks when the overall length shrinks: tie it to the end face.
  7. A scan filter by the slot plane also catches drive-blade walls below the flap: separate by normal.
  8. ICP of a 2-fold symmetric core is 180 deg ambiguous; a single bump on the underside was therefore left unmodelled.
  9. Stage z (11 regenerations + STEP) took 18-40 min (RAM pressure). PowerShell 5.1 drops an empty-string argument to a native exe: pass "-".
  10. Soft parts sit up to 2.4 mm sideways in the scan, so scan-to-CAD bands do not apply; the model is nominal (radial, straight) and says so.

### Key files (path relative to STAGE\dreame_brush_core)
- `work/REPORT.md`, `work/REPORT2.md` - full Turkish reports: feature tables, master expressions, deviation tables, known simplifications.
- `work/an/common.py` - STL reader, Mesh, cylindrical coords, signed-distance helper, stats (reusable scan toolkit).
- `work/an/m1_align.py` - datum alignment of a cylindrical part (planes + axis stations + clocking).
- `work/an/m2_twist.py` - twist measurement by cross-correlation and the untwisted pooled section.
- `work/an/m3_profile.py` - numbers from the untwisted section (slots, grooves, lands).
- `work/an/m7_base_align.py` - trimmed ICP of a partial scan onto an aligned one, 36 clockings.
- `work/an/f1_align.py` - assembled scan to CAD datum by ICP on hard surfaces only.
- `work/an/f3_flap.py` - thin soft-part measurement in a local slot frame.
- `work/an/dev.py`, `work/an/f6_dev.py`, `work/an/dev_c2s.py` - zone-wise deviation tables, both directions.
- `work/an/s2_flap_volume.py`, `work/an/s3_step_wall_probe.py` - independent STEP volume / wall checks.
- `work/build.py` - round-1 journal (`twisted_cut` helper near line 340: Swept angular law, Trim, Pattern Geometry, Subtract).
- `work/build2.py` - flaps (stage e), filament tufts (stage f), checks / regeneration / STEP (stage z).
- `work/nxlib/ps.py` - Sketch class with tangent constraints, DOF-0 profiles, formula dimensions.
- `work/nxlib/geo.py` - corner geometry for formula-driven sketch vertices.
- `work/run.ps1`, `work/run2.ps1`, `work/show.py` - run_journal launchers with stage letters; check-table printer.
- `work/qa/dev_final.json`, `work/qa2/f6_dev.json`, `work/qa/T_bristles.json`, `work/qa2/T_asm.json` - results and alignment matrices.
- `work/out2/build2_abcdefz.json`, `work/out2/asfound2.json` - check table and as-found read-back of the delivered part.
- `work/fig/m2_untwisted.png`, `work/fig2/f8_flap_cad_sections.png`, `work/fig/ovl_final_rz.png` - untwisted section, flap CAD vs scan section, r-z overlay.

### Files in package (dreame_brush_core)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## dreame_dustbin_air_inlet
- **Purpose / part type:** NOT a full rebuild. An edit of an existing reverse-engineered Dreame dust bin NX part ("dreame_dust_bin CAD.prt", one solid, 882 faces, 204 history steps, 241 feature rows, plus 12 sheet bodies) where a colleague's note said the STEP "is missing the air entrance opening". The scan (`model1.prt`, 4.1 M-facet convergent body) was the authority used to locate and size one rounded-rectangular through-opening in the 45 deg sloped wall. User rule: make only that change; everything else is correct and must not change.
- **Dates:** 2026-10-07 (single session, about 1.5 h).
- **Sessions:** `transcripts/e7db2fb7-ddad-4bed-9a67-a86f3a7848b4.jsonl` (Read 30, PowerShell 21, Write 12, Grep 8, Edit 3; about 17 python runs, 9 headless NX runs).
- **Source folders (original paths):** problem `C:\Users\marya\Downloads\dream dust bin\` (prts: assembly, CAD, scan `model1.prt`; the note and two screenshots); work `C:\NX_MCP_WORKSPACE\dreame_air_inlet`; delivery `...\dream dust bin\air_inlet_fix\` (corrected prt + STEP + journal + PNGs + CHANGES.txt).

### Workflow (step by step, reconstructed from scripts + logs)
1. **Read the request and look at the part as found.** `required change.txt` + two screenshots; skill reference `nx-journal-core/references/existing-parts.md` (rules for editing somebody else's part: work on a copy, append at the end of the tree, no reorder). Originals copied to the job folder; hashes later shown identical.
2. **Inspect as found** with the skill script `inspect_part.py` (output `out/dreame_dust_bin CAD_asfound.txt/json`): 1 solid, 204 steps, 0 errors, mm. `probe1.py` lists assembly components and origins: CAD and scan share one coordinate frame (identity transforms), so no alignment step was needed.
3. **Get the scan out of NX** (`probe2.py`): `nxh.S.DexManager.CreateStlCreator()` with `ChordalTol=0.02`, `AdjacencyTol=0.02`, `AutoNormalGen=True`, body added to `ExportSelectionBlock`, `Commit()` -> `scan.stl` (4,102,821 triangles, not watertight; about 60 s). The CAD body went out with `nxre.stl_export` (`export_asfound.py`/`probe1.py`).
4. **Find the opening visually** (`render.py`, `depthview.py`, `sections.py`): depth-buffer views from +/-X, +/-Y, +/-Z of CAD and scan side by side (`out/cmp_*.png`; z-buffer from dense surface sampling, no GPU), then x/z sections of CAD vs scan (`sec_x.png`, `sec_z.png`). Finding: the scan has a rounded-rectangular through-opening about X 130-165 in the sloped wall; the CAD wall is solid there.
5. **Measure the opening in the plane of the wall** (`measure_opening.py`, `measure2.py`): build an orthonormal frame (eu = X, ev = cross(n, eu), n = outer wall normal (0,-0.7075,0.7068)); project the cropped scan (`scan_region.stl`) into (u, v, s); take area-weighted medians of the hole-wall facets (facet normals lying in the wall plane) for the left/right/bottom/top edges (p10/p90 reported); also fit a rounded rectangle to a 0.1 mm-pixel occupancy mask (binary closing, connected component holding the opening centre, `scipy.ndimage`). Result `opening_measure2.json`: left u 129.458, right 165.513, bottom v -19.690, top v 2.526; hole area 777 mm2; corner radii from the mask fit 1.6 / 2.1 / 3.5 (fourth not readable).
6. **Round to design values** (0.5 mm grid): width 36, height 22 along the wall, R2.5, centre X 147.5, centre Z 24.25 on the outer face, cut depth 3 (wall 1.5 + clearance). Stored as named expressions `inlet_w/h/r/x/z/depth`; `inlet_y` is derived so the centre stays on the sloped face.
7. **Probe sketch mechanics** (`probe_sketch.py` -> `probe_sketch.json`): five variants of putting a centred rectangle on the inclined face (see traps); chose "sketch point coincident with the smart-point centre".
8. **Journal `add_air_inlet.py`** (run via `run_journal.ps1` on a fresh copy of the prt, 5 iterations): finds the outer and inner wall faces by probing (`nxh.faces` by normal + `nxh.dist_to` + `UF.Modeling.AskPointContainment` just outside/inside), checks that the walls are parallel and 1.5 thick; creates 3 features appended after Edge Blend(205): sketch `AIR_INLET` on the outer face (DOF 0, 0 auto dims), `AIR_INLET_CUT` (Extrude Subtract from the sketch region, start -1, end `inlet_depth`; tries both directions and keeps the one whose volume delta equals -w*h*wall), `AIR_INLET_CORNERS` (Edge Blend R2.5 on the four wall-thickness edges, found by edge length and midpoint position).
9. **Verify** (journal checks + `verify_after.py`): 44 checks incl. volume deltas (cut -1188.000 = -36*22*1.5; blend +(4-pi)r^2*t; total -1179.952), single solid, point probes (centre open; 0.3 mm outside each edge still material; corner points), all 241 earlier feature rows unchanged (feature_state diff = additions only), 12 sheet bodies unchanged, Examine Geometry clean, regeneration (inlet_w 36->34 and inlet_x 147.5->146.5, back to nominal exactly). Outside NX: mesh before/after comparison (max difference outside the opening footprint 2e-6 mm on 120 k points each way), STEP re-imported into NX and read with OCP (1 solid, 890 faces, relative volume diff 2.1e-5). `export_asfound.py` exported the untouched part as the STEP baseline for the diff.
10. **Deliver:** corrected prt + STEP, before/after/scan PNG, outline-over-scan PNG, journal, `CHANGES.txt` (scope, features, dimensions with scan readings, checks, not-included list). A follow-up task was spawned to fix the two nxf helper limitations found (below).

### NX tools and NXOpen APIs used
- `run_journal.ps1` (skill launcher) for every NX run; helper modules `nxh`, `nxf`, `nxre`; skill scripts `inspect_part.py` and `prt_text.py` (reads .prt text without NX). No certified nx-mcp tools.
- `nxh`: open_part, Log, Check, expr, point (associative point from expressions), Datums, faces/face_data/dist_to, volume, one, feature_state, section_region, blend, set_expr/update, undo_to/mark, body_ok/examine_geometry, step_export, write_json. `nxf`: new_sketch (on a planar body face), add, cg, sketch_rect_centered, finish_sketch, extrude_ex (subtract, start/end by expression, reverse flag), step_roundtrip_check.
- NXOpen/UF: `Session.DexManager.CreateStlCreator`, `UF.Modeling.AskPointContainment` (inside/outside/boundary probe), `UF.Modeling.AskFaceData`, `Sketch.CreateCoincidentConstraint`, `Part.Points.CreatePoint`; extrude and edge-blend builders via the helpers; feature-state diff.

### Accuracy / deviation results
No global deviation metric (not a rebuild). Local fit of the added feature to the scan (`out/verify_after.json`, CHANGES.txt): CAD edge minus scan wall-facet edge: left +0.042, right -0.013, bottom -0.046, top -0.262 mm (top is thinly scanned; +0.082 against the mask fit). Width/height readings 36.0-36.05 and 21.9-22.2; centre X 147.44-147.49, Z 24.2-24.4; corner-radius readings disagree (1.6/2.1/3.5), so R2.5 is the weakest number. Everything else: surface identical before/after (<= 2e-6 mm). Existing mismatch left alone and reported: the scan wall around the opening is about 0.7 mm lower than the CAD wall, with a step at X=167.

### What worked / what failed
- Worked: minimal-change discipline (copy, append 3 features at the end, prove nothing else changed by feature-state diff and by mesh diff); finding wall faces by geometric probing instead of picking by index; measuring in the wall's own (u,v,s) frame with area-weighted medians of hole-wall facets (robust to scan holes at the rim); trying the extrude in both directions and accepting by exact volume delta; point-containment probes as a topology-independent check; expressions for every dimension; scan and CAD already in one frame.
- Failed / traps (measured on NX 2206 headless):
  - `nxf.sketch_rect_centered` with a smart-point centre on a sketch lying on an INCLINED plane (planar face normal (0,-0.7075,0.7068), also a datum plane at offset 0 on it) raised "Invalid object type" from the perpendicular dimension; `CreateMidpointConstraint` to the point failed the same way; CreatePointOnCurve to the point works. The existing self-tests only covered sketches on the absolute XY datum plane. Workaround that gave WellConstrained, DOF 0, 0 auto dims: create a plain sketch point, `CreateCoincidentConstraint` it to the smart-point centre, call the helper with the sketch point (`probe_sketch.json`, variant v3).
  - `nxh.section_feature(part, [sketch.Feature])` on a sketch that also holds a point gave "Cannot extrude. The section and direction may be incompatible"; use `nxh.section_region(part, sk, seed, curves=rect)` with the profile curves only.
  - Scan body is 4.1 M facets: the normal `nxre.stl_export` route is not suitable; use `CreateStlCreator` with 0.02 tolerances.
  - Reading the STEP in trimesh/OCP printed "StepReaderData: Unresolved Reference" but the solid was valid (benign).
  - Corner radius could not be read reliably from a thin noisy rim; flagged as a judgement call with `inlet_r` editable.
  - Rim left sharp although the rest of the part has R0.1/R0.2 edge breaks (stated in the report).

### Key files (path relative to STAGE\dreame_dustbin_air_inlet)
- `work/add_air_inlet.py` - the complete edit journal: plan header, face probing, sketch, cut with both-direction trial, corner blend, 44 checks, regeneration test.
- `work/probe_sketch.py`, `work/out/probe_sketch.json` - five placement variants on an inclined face and which one works.
- `work/measure_opening.py`, `work/measure2.py` - project scan into the wall frame, robust edge medians, rounded-rectangle fit to a pixel mask.
- `work/out/opening_measure2.json`, `opening_measure.json`, `opening_mask.png` - measured edges and the mask.
- `work/probe2.py` - STL export of a huge convergent body with `CreateStlCreator`.
- `work/depthview.py` - z-buffer style CAD-vs-scan view generator for six directions (no GPU).
- `work/sections.py` - CAD vs scan sections via trimesh `mesh_plane`.
- `work/verify_after.py`, `work/out/verify_after.json` - STEP validity, before/after mesh diff, edge-vs-scan table.
- `work/export_asfound.py` - baseline export of the untouched part for the diff.
- `work/render.py` - simple matplotlib mesh renderer.
- `work/CHANGES.txt` - delivery note (format worth copying: scope, features, dimensions with scan readings, checks, not included).
- `work/out/add_air_inlet.log`, `add_air_inlet.json` - run record.
- `work/out/air_inlet_outline_vs_scan.png`, `cmp_pX.png`, `cmp_mZ.png`, `sec_x.png` - sample visual evidence.

### Files in package (dreame_dustbin_air_inlet)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## dreame_mop_early_nx
- **Purpose / part type:** The same Dreame mop bottom cover as `dreame_bottom_cover`, but this is the EARLY attempt (iteration it3 of the build123d/OCCT run). NX was used only to import the STL and STEP and to assemble a review part; the modelling itself was build123d, so this is not an NX-native RE. Included for what the build123d loop achieved and for the NX import quirks.
- **Dates:** 2026-09-30 (single session).
- **Sessions:** `transcripts/8d295d90-dd65-45c3-82b9-62f39c1a092f.jsonl` (PowerShell 144, Read 59, Edit 39, Write 10; about 103 python runs, 11 headless NX runs; one nx-mcp call, `nx_status`, failed with `NX_BRIDGE_UNAVAILABLE` because NX GUI was not running).
- **Source folders (original paths):** `C:\Users\marya\Downloads\dreame_mop_assembly_bottom_cover\run\` (it2 inputs `build\model.py`, `measure\params.json`, `qa\`; new work in `run\it3\`, NX part in `run\it3\nx\`); session worktree `H:\My Drive\Agentic-NX\.claude\worktrees\dreame-mop-reverse-engineering-3a19f5`. Only the transcript is staged; no scripts were copied.

### Workflow (step by step, reconstructed from the transcript)
1. User request: use the NX skills, import the scan STL, take the existing `run\build` model and fix the errors so it fits the scan better. The agent read the prior verdict (`qa/VERDICT.md` = BAND_NOT_MET, scan->CAD p95 1.74 mm), `DECISIONS.md`, `MODELING_PLAN.md`, `measure/params.json` and the existing `alignment.json` / `registration.json` / masks.
2. `nx-mcp` bridge check failed (NX not running), so all NX work went through headless `run_journal.exe`; the certified MCP tools only cover sketch/extrude anyway.
3. Built a fast self-check evaluator `it3/ev.py`: build the build123d model from `params_it3.json`, tessellate (`export_stl` tol 0.02), rigid ICP onto the decimated datum-frame scan, cached 3 M surface samples, KD-tree distances, the QA masks MA1-MA3 copied verbatim as box predicates, and a "hot cell" grid listing the worst regions. It reproduced the QA number (p95 1.76) before anything was changed.
4. Iterated r1..r7 (`model.py`, `params_it3.py`, section/profile tools `sec.py`, `prof.py`, `tb*.py`, `tcell*.py`, `probe3.py`): rendered scan close-ups of the worst region, fitted true shapes (sloped hook-side floor, a fitted B-spline scoop surface, end-cell cavity, 5th hook, latch housing 2 mirrored, rail foot only where the scan has pads), fixed a wrong-way arc in the grille-end profile (1.5 mm) and a 2.6 mm step. OCCT split/fuse hangs on finer B-spline fits were isolated pairwise and cured by smoothing the roof surface and choosing tolerance/domain combinations.
5. Froze it3 when p95 moved by only 0.001 per tweak (0.912 -> 0.911). Exported STEP in the design (datum) frame and the original scan frame; ran the project's own QA (`deviation_gate.py`, `tier2_icp.py`, `step_check.py` of the stl-re-verify skill) on the full-resolution scan (ICP about 7 min).
6. NX review part (`it3/nx/build_nx_it3.py`, `scan_to_datum.py`): new part from `model-plain-1-mm-template.prt`, STEP import of the it3 and it2 solids, STL import of the scan transformed into the datum frame (4.84 M faces); layers 1 (it3), 10 (scan), 20 (it2, hidden); verified with a read-back journal listing bodies, layers and face counts.

### NX tools and NXOpen APIs used
- `run_journal.exe` (with `UGII_CUSTOM_DIRECTORY_FILE` and `UGII_STARTUP_MACRO` cleared). `Session.Parts.FileNew` with `TemplateFileName`, `Units`, `DisplayPartOption.AllowAdditional`; `Session.DexManager.CreateStep214Importer`; `Part.FacetedBodies.CreateSTLImportBuilder` (units mm, `FacetBodyTypes.Psm`, `AngularToleranceTypes.Fine`); a `Part.Bodies` diff to find new bodies; `Layer` / `Color` / `SetName` on bodies; `BasePart.SaveComponents`. The helper modules nxh/nxf were not used in this early session.

### Accuracy / deviation results
Self-run, not an independent verdict; full-resolution scan, same masks/ICP/settings as the it2 verdict (`it3/qa/deviation.json`, from the final report):

| | it2 | it3 |
|---|---|---|
| scan->CAD p95 | 1.738 mm | 1.066 mm |
| scan->CAD rms | 0.826 | 0.496 |
| scan->CAD max | 7.71 | 5.38 |
| scan points > 0.8 mm | 14.5 % | 8.8 % |
| CAD->scan p95 (visible) | 1.307 | 0.897 |

Plastic band (p95 <= 0.30, max <= 0.80 mm) not met. The it3 solid has 769-778 faces, 92.7 % analytic area, 10 B-spline faces (the fitted scoop). Remaining error attributed to the up-to-0.9 mm flange warp (model kept flat), two zero-thickness scan sheets, and simplified details; the agent said closing the gap would need a flat re-scan or acceptance of the warp, plus caliper values. For comparison the later NX job (`dreame_bottom_cover`) reached masked p95 0.595 mm on a de-warped scan with a feature-based NX build (protocols differ).

### What worked / what failed
- Worked: first reproducing the QA metric with a fast self-check evaluator, then fixing the worst-region error one cause at a time with each change measured; QA masks as verbatim box predicates; NX as viewing/hand-off container (solid + full scan + previous revision on separate layers).
- Failed / traps:
  - A `Step214Importer` created from NXOpen does not load `step214ug.def` by itself: it returned no objects (0 bodies) until `SettingsFile = <NX2206>\STEP214UG\step214ug.def`, an explicit scratch `OutputFile` and `ImportTo = WorkPart` (`FileOpenFlag = False`) were set; delete the scratch prt afterwards.
  - The scan STL held 5 shells (the part plus 4 small fragments), so the STL import builder yields 5 convergent bodies; find them by diffing `Part.Bodies` before/after rather than relying on `GetCommittedObjects()`, and move all of them to the scan layer.
  - OCCT boolean split/fuse hangs on fine B-spline fitted surfaces; smooth the fitted surface and test pairwise fuses to find the culprit. A cavity tool silently failed to cut until its roof was smoothed.
  - The rail profile was measured at one station that had foot pads and extruded along the whole rail, adding about 1 mm of nonexistent material (a recurring RE error: a profile measured at one station and extruded everywhere).
  - PowerShell `Remove-Item` on a path string containing "C:\Program" was blocked by the safety layer; use `-LiteralPath` with a variable.
  - The 125 MB review prt (4.84 M facets) is slow to open.

### Key files (path relative to STAGE\dreame_mop_early_nx)
- `transcripts/8d295d90-dd65-45c3-82b9-62f39c1a092f.jsonl` - the only artefact staged. Useful spots (event index): the `ev.py` write (~166), the Step214Importer probe (~1414-1429), the STL import builder edits (~1439-1451), the final report (~1517).

### Files in package (dreame_mop_early_nx)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## r385_pump
- **Purpose / part type:** Multi-part reverse engineering of an R385 5-chamber wobble-plate diaphragm pump (13 unique parts, 23 pieces: DC motor can, motor mount, eccentric hub+pin, wobble plate, diaphragm frame, 5-chamber elastomer diaphragm, valve plate, pump head, three small valve/gasket elastomers, screws) into ONE consistent parametric NX 2206 assembly. Quality target: replica-grade, "scans are the authority, no caliper requests". After the CAD, four consumer sessions used the model: 3D-print export, assembly drawing PDF, kinematic animation, theory/CFD report. The CAD part is what matters for build123d skills; the CFD/print/video material is only listed for context.
- **Dates:** 2026-10-08 (planning) to 2026-10-09 (CAD Rev A1, assembly PASS, consumer jobs). The `ep5_hs03` sub-folder is a separate in-NX pilot on a Ulka part (see end).
- **Sessions (transcripts/):**
  - `0bf7b833-...` and `ab80fb64-...`: planning + **R385-A Master** (control part, interface doc, independent QA, assembly)
  - `24f4f717-...`: **R385-B Tahrik** (MT01, HS01, DR01, DR02, HS02, SL01)
  - `d3aee339-...`: **R385-C Hidrolik** (HS03, HS04, SL02, SL03, SL04)
  - `9b75049a-...` D print, `a0755bdb-...` E drawing, `ca5a2a08-...` F animation, `522aa477-...` G theory (consumers; also `522aa477_subagents/`)
- **Source folders (original paths):** scans and project rules `H:\My Drive\Mini Pumps\r385` (part STLs, `outer.stl` = assembled pump, scanner project folders with Fused/Mesh/model.ply, labelled photos, BOM xlsx/pdf, `CLAUDE.md`, `R385_INTERFACES.md`, `sessions\`, `cr\`, `cad\`); NX work area `C:\NX_MCP_WORKSPACE\r385\` (`an\`, `parts\<code>\`, `parts\B_common\`, `parts\_C_an\`, `ctrl\`, `asm\`, `scan\`). Staged as `drive_source/` and `work/`.

### Workflow (step by step, reconstructed from scripts + logs)
1. **Plan the multi-part job (`0bf7b833`).** Not "one STL to one CAD": three parallel sessions share one frozen axis frame, one control part and one interface document. Rules in `drive_source/CLAUDE.md`: single writer per file, change requests `cr/CR-<session>-nn.md`, messages carry news only, unscanned values labelled "turetildi" (derived) with their source, gates fixed before modelling.
2. **Stage 1, per session, own parts: clean + align + measure** (numpy/scipy only, no NX):
   - `B_common/s0_inventory.py` (shell inventory), `B_common/s1_census.py`: part axis = area-weighted facet-normal mode on a Fibonacci half-sphere (antipodes folded, refined); axis position = least-squares meeting point of the wall-normal lines with robust MAD reweighting; census in the provisional frame: z-levels of +/-z-facing planes as area peaks, coaxial walls as r-peaks with boss/bore sign and angular coverage. Output `qa/s1_census.json`.
   - Per-part `<code>_align.py` / `<code>_measure.py` (e.g. `HS01/hs01_align.py`, `MT01/mt01_measure.py`, `HS02/hs02_detail*.py`) write the aligned scan `scan/R385-<code>_aligned.stl` and named measurements through `B_common/rb.py`: `level()` (plane height of facets facing +/-z in a window), `wall()` (radius by z = draft), `hole()`, `flat_edge()` (opening of a hole in a flat face), `fit_plane/circle/cylinder/cone` with clipping and robust iterations, `hist_peaks`.
   - Session C: `_C_an/cc.py` + `tools.py` (sections, plane levels, height maps from both sides), `a_flat.py` (single-sided scans lying on the scanner table: level on the table plane, split table/part, centre on the outer circle), `a_hs03.py`, `m_hs03*.py`, `m_ears_fit.py` (lug-pattern fits). Results written to `sessions/B_MEASURED.md`, `C_MEASURED.md`.
   - Session A measures the assembled pump `outer.stl`: `an/o1_overview.py`, `o2_axis.py` (housing axis vs motor-can axis, meridian density map), `o3_stack.py` (r(z) profiles = seams between HS01/02/03/04, lug/screw-head/nipple centres), `o4_seams.py`, `q3_outer_passes.py` (are the two raw scan passes consistent with the merged mesh?). This yields the axial stack and angular phases that no single-part scan can.
3. **Gate "Rev A".** A reconciles all measured values, freezes the frame (Z = motor shaft axis, +Z motor to head; chamber 1 on +X; keyed lug at +135 deg), builds the control part (`ctrl/ctrl_build.py` from `ctrl_params.json`: 71 named expressions, datum planes/axis; Rev A1 final) and publishes `R385_INTERFACES.md`. No part is modelled before Rev A.
4. **Stage 3, parametric rebuild per part (headless NX, one journal per part).** `parts/<code>/build.py` run through `B_common/run.ps1` (run_journal.ps1). Pattern: `rj.Ctx` opens the control part first; `c.link("name")` creates an interpart expression, `c.e()` part-internal masters (scan value in the comment), `c.d()` derived expressions; fully constrained profile sketches via `nxlib/ps.py` (DOF 0, no auto dims); features revolve / extrude / pattern_circular / hole / blend / datum axis. Every step carries a check: volume vs analytic value, `nxh.dist_to` probes at expected points, solid counts, regeneration test (change an expression, verify the volume moves by the analytic amount). `c.finish()` runs Examine Geometry, saves the .prt, exports one STL per body (chord 0.002) and a STEP with round-trip check.
5. **Deviation check, scan to CAD.** `B_common/dev.py` (open3d RaycastingScene): 200k scan samples, signed distance to the CAD STL, named zones as predicates on (point, normal), a **pose-vs-shape test** (`refit=`: small rigid motion that best fits a subset, then the residual), reverse coverage ("share of CAD with no scan within 0.3 mm") and worst 1 mm cells. Per part `dev_<code>.py`, `_C_an/dev_c.py`; `report.py` writes REPORT.md.
6. **Independent QA by A** (`an/qa_dev.py`): own registration (point-to-plane ICP, 2 percent trim) of the cleaned scan to the delivered STEP, deliberately ignoring the part builder's numbers; "as placed" vs "best fit" shares, fit motion, reverse coverage. Logged in `sessions/A_QA.md` (rounds 1-8).
7. **Integration** (`asm/asm_build.py`, NXOpen assemblies): 23 components in the pump frame, clearance analysis (Exact, 31 pairs), crank sweep (0..324 deg) with the wobble plate following the eccentric pin, STEP, re-read outside NX with OCP (`an/qa_step.py`: solids, validity, volumes vs NX).
8. **Revision loop:** findings go to CRs (CR-B-01 pin depth, CR-D-01 print groove, CR-F-01 kinematics, CR-G-01 stroke formula); A revises `ctrl_params.json`; `rebuild_all.ps1` re-runs the six B parts in about 3 minutes.

### NX tools and NXOpen APIs used
- Headless `run_journal` via `skills/nx-journal-core/scripts/run_journal.ps1` (`-Script -WorkDir -JArgs -TimeoutSec`; 11-87 s per part). A result JSON (`RESULT PASS/FAIL`, checks) is printed by `show.py`. Tool stats count only 24 direct run_journal calls because most were wrapped in `run.ps1`.
- Helper modules `nxh` (parts, expressions, bbox, volume, `dist_to`, `face_data`, Check), `nxf` (revolve, extrude, `pattern_circular` incl. negative pitch, `datum_axis`, `datum_plane`, hole, blend/chamfer, `cg`/`help_at`, `step_export` + `step_roundtrip_check`), `nxa` (`interpart_expr`, `load_fully`, `simple_interference`, clearance builder), `nxre.stl_export`; project-specific `rj.py`, `ps.py`, `geo.py` (2D tangent/intersection helpers for profile vertices).
- NXOpen names that appear directly: `STLCreator` (binary), `Expression.UnitsOption`, `Session.GetSession`, UF session, `AssemblyManager.CreateClearanceAnalysisBuilder`. **No Fit Surface / Replace Face / facet tools in this project**: the fits are done in numpy and rounded to design values, and the NX part is built from sketches + revolve/extrude + patterns. No certified nx-mcp tools were used for the build.
- Outside NX: cadgenbench venv (open3d, trimesh), system Python numpy/scipy/matplotlib, OCP for STEP read-back and overlap volumes (`B_common/overlap.py` Monte Carlo occupancy, `an/qa_step.py`).

### Accuracy / deviation results
(from `drive_source/sessions/B_STATUS.md`, `A_QA.md`, `cad/*_REPORT.md`)
- Gate set before modelling: functional surfaces within +/-0.05 mm, general surface >= 95 percent within +/-0.15 mm. **The 95 percent gate held for none of the parts**; it was not relaxed afterwards, results are reported as "did not hold" with causes.
- Share within +/-0.15 mm, as placed / after A's own best fit: MT01 77/90, HS01 89/91, DR01 88/93, DR02 84/91, HS02 67/79, SL01 68/71, HS03 82/84 (C's own number 85.7), HS04 77/80, SL03 80/88, SL04 14/91 (after a 0.37 mm z shift; thickness is derived), whole pump `outer_G0.stl` vs assembly STEP 60/84.
- Scan noise sd per part 0.07-0.16 mm, so a +/-0.15 band is largely filled by scan noise itself.
- Functional zones: mean deviation within +/-0.04 on every flat functional face (HS03 clamp face -0.001, pocket floors +0.001, wall tops +0.005; MT01 front face/pilot/bush mean 0.000 with 94-96 percent within 0.05; DR02 hub wall 99.3 percent; HS02 chamber holes 98.5 percent).
- **Pose-vs-shape finding:** three parts had a low share only because one group of faces is rigidly offset in the sample: wobble plate 1.08 deg/0.25 mm against its hub, HS02 outer shell 0.23 mm against its hole pattern, MT01 can 0.26 mm against its pilot. After the subset's own fit 91-99 percent lay within 0.15. Read as moulding/merge offsets, not model errors; the model stays concentric (design intent).
- Assembly: 23 components, 24 solids, 31 pairs (14 Touch, 17 Hard; all Hard = threads, designed elastomer squeeze, known DR02/SL01 mould-state overlap), 0 unexpected overlaps, no collision over the crank sweep. STEP re-read in OCP: 24 solids valid, volume diff 0.39 mm3 of 43688 mm3. Top-dead-centre clearance to the SL02 skirt only 0.05 mm (four derived values stacked).
- Stroke formula corrected (CR-G-01): 2*r*sin(alpha) = 3.770, not 2*r*tan(alpha) = 3.841.
- ep5_hs03 pilot (separate, failed): deviation rms 3.40 mm, 87 percent over threshold, 5 solids left (check FAIL).

### What worked / what failed
- Worked:
  - One control part + interface doc with interpart expressions, tested early (`ctrl/link_test.py`): a part opened alone keeps the last saved value, opened after the control part it follows (19.33 stayed vs 20.0 followed).
  - Every journal self-checks (analytic volume, probe-point distances, regeneration test), so wrong builds fail loudly.
  - Deviation reported per named zone with signed mean/sd/shares instead of one global number.
  - Gates fixed before seeing results; failures reported with causes.
  - "Does a rigid refit of a subset fix it?" asked before touching the model.
  - Checks the single scans cannot give: axial stack and phases from the assembled scan, crank sweep, clearance analysis, STEP read-back in OCP.
  - Derived (unscanned) values flagged and listed so later sessions know which numbers are guesses.
- Failed / traps:
  - **Scan merge symmetry trap** (HS03, session C): the scanner software merged the two passes of a two-sided scan a quarter turn (90 deg) apart; round outer wall + 4 ears hid it. Detected by: keyed lug sitting on neighbouring ears; 5-fold features of the two faces 18 deg (= 90 mod 72) apart; floating lip fragments over a flat face; through ports not coinciding until one face was turned 90 deg; contradiction with the assembled scan. Fix: rotate the chamber-side pass +90 deg in a working copy. Cross-pass dimensions (web 0.63 mm, total height) stay assumptions.
  - Hand-set orientation errors: HS02 delivered 180 deg off (keyed lug -45 instead of +135), corrected with `rev_a_turn.py`; a `ch_phase` check caught chamber 1 on the wrong side. A's own mis-reads (HS01 base-to-mouth 19.35 = groove bottom, true 18.8) show why A re-measures instead of trusting builders.
  - Thin or one-sided scans (elastomers SL01-SL04, wobble plate) give thickness only by derivation; scan shows 0.81/1.10 where the model used 1.1/1.5 (open point).
  - Scanner fills interior corners (pin root, hole mouths, shoulder corners): +0.15..+0.3 mm "errors" that are scan, not model; no radius was added to chase them.
  - Shrink sinks and thin-wall sinks at lug roots were left out as not design intent, reported by name.
  - Cylinders with < 180 deg coverage: the free circle centre drifts, so diameters are taken relative to an axis fitted on all surfaces.
  - Operational: only one NX process at a time (wait and retry); open3d exists only in the venv (system Python lacks it); `fit_cylinder` crashed on an empty selection (needs a minimum-count guard); several first-run journal failures were mere check failures (tilted-face count, terminal offset) fixed in the check, not the geometry.

### Key files (relative to `STAGE\r385_pump`)
- `drive_source/CLAUDE.md`: project rules, roles, consistency rules, control-part usage, acceptance gates (Turkish).
- `drive_source/R385_INTERFACES.md`: frozen frame, interface values, derived-value markers (Rev A1).
- `drive_source/sessions/A_QA.md`: independent QA rounds 1-8 with all shares, assembly checks, CR consequences.
- `drive_source/sessions/B_STATUS.md`, `C_STATUS.md`, `A_STATUS.md`: state, result tables, open points.
- `drive_source/sessions/C_MEASURED.md`: scan-merge-symmetry finding with all evidence; measurement tables with sd column.
- `work/parts/B_common/rb.py`: numpy STL, shells, plane/circle/cylinder/cone fits, level/wall/hole/flat_edge measurements.
- `work/parts/B_common/s1_census.py`: axis from normals + level/wall census (datum selection logic).
- `work/parts/B_common/dev.py`: signed scan-to-CAD deviation with zones, pose refit, reverse coverage, worst cells.
- `work/parts/B_common/nxlib/rj.py`: journal context (control part first, link/e/d expressions, finish with checks, STL + STEP).
- `work/parts/B_common/nxlib/ps.py`: fully constrained profile sketch builder (generic DOF 0 constraint scheme).
- `work/parts/HS02/build.py`: richest example journal (revolve profile, lips and chamber cones patterned x5, lugs, blends, holes, probe checks).
- `work/parts/HS03/build.py`, `work/parts/DR01/build.py`: valve plate and eccentric hub builds.
- `work/parts/_C_an/cc.py`, `tools.py`, `a_flat.py`, `a_hs03.py`: single-sided-scan levelling, two-pass fix, sections.
- `work/parts/B_common/rebuild_all.ps1`, `run.ps1`: re-run chain after a control-part revision.
- `work/an/qa_dev.py`, `qa_step.py`: independent registration/deviation and STEP read-back.
- `work/an/o2_axis.py`, `o3_stack.py`: axis and axial stack from the assembled scan.
- `work/ctrl/ctrl_build.py`, `link_test.py`: control part builder and interpart-link test.
- `work/asm/asm_build.py`: assembly, clearance analysis, crank sweep.
- `drive_source/cad/assembly/asm_build.json`, `drive_source/cad/R385-*_REPORT.md`: assembly result data and per-part zone tables.

### Sub-folder `ep5_hs03` (separate pilot; EP5 = the Ulka pump, part HS03 outlet flange)
- Files: `step1_describe_census.py`, `step2_align.py`, `step3_fit_table.py`, `step3_measure.py`, `step4_model.py`, `run_step4.ps1`, logs in `out1..out4`.
- No staged transcript mentions it, so provenance is the files only. It is an in-NX run of the generic `nxre` library (nx-reverse-engineering skill) on a 536k-facet scan imported as a convergent body: (1) import + `nxre.census` (planes, cylinders, noise 0.088 mm; reading the facet cache took 252 s), (2) alignment from two fitted datum planes (primary = flange back face, secondary = edge plane; squareness error 1.07 deg) applied with Move Object, (3) fit-and-snap table (plane fits snapped to a 0.5 mm grid, e.g. 5.506 to 5.5; `nxre.fit_surface` / `measure_plane`), (4) hand-written model (block + pipe cylinders + two Trim Body chamfers + two holes from snapped values) then `nxre.signed_deviation`.
- Result: step 3 crashed (missing `import time`); step 4 wrote RESULT PASS but its own checks show "one solid body" failed (5 solids left over) and deviation rms 3.40 mm (mean +2.08, p95 6.4, 87 percent over threshold; model bbox does not match the aligned scan). Abandoned attempt; the production EP5-HS03 was built by Ulka session D with the R385 toolchain (see ulka_pump). Useful as a negative example: Boolean leftovers (solids=5) and the global deviation number are what to check first.

### Files in package (r385_pump)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## ulka_pump
- **Purpose / part type:** Ulka EP5 (CEME type E) electromagnetic vibratory piston pump, 230 V 48 W espresso-type pump: 21 unique parts (23 pieces) from 13 STL scans, rebuilt as parametric native NX 2206 parts and one assembly (AS00 with sub-assemblies AS01 stator, AS02 cartridge, AS03 outlet valve). Part families: coil (EM01, bought part, envelope only), sheet-metal magnetic frame (EM02), flux sleeves (EM03 x2), plastic spacer ring (HS04), inlet body/armature tube (HS01), armature+piston (DR01), two compression springs (DR02, DR03), piston cylinder (HS02), outlet flange (HS03), washer (HS05), four O-rings (SL01-SL04), ball (VL01), ball spring (VL02), valve plug (VL03), valve spring (VL04), valve cage (VL05), flange screws (FS01). Second project built with the method proven in `r385_pump`; a theory/CFD stage (session E) followed.
- **Dates:** 2026-10-16 (all CAD, assembly PASS Rev H) to 2026-10-17 (theory report, CR-E-01).
- **Sessions (transcripts/):**
  - `e4e799fc-...`: **ULKA-A Master** (frame, control part, Rev A-H, independent QA, assembly)
  - `3b5db2ce-...`: **ULKA-B Stator** (EM01, EM02, EM03, HS04)
  - `10ee51b0-...`: **ULKA-C Tahrik** (HS01, DR01, DR02, DR03)
  - `bcea8ef0-...`: **ULKA-D Hidrolik** (HS02, HS03, HS05, SL01-04, VL01-05)
  - `136cb46e-...`: **ULKA-E Teori** (math model, fluid validation; consumer, not CAD)
- **Source folders (original paths):** scans and rules `H:\My Drive\Mini Pumps\ulka re` (13 STL scans from the scanner project folders `EP5-*` with model.ply/Fused.ply, labelled photos F01-F21, teardown videos, datasheet `E_high_pressure.pdf`, `CLAUDE.md`, `ULKA_INTERFACES.md`, `sessions\`, `cr\`, `cad\`, `theory\`, `cfd\`); NX work area `C:\NX_MCP_WORKSPACE\ulka\` (`an\`, `parts\<code>\`, `parts\C_common\`, `parts\D_common\`, `parts\D_an\`, `ctrl\`, `asm\`, `scan\`), later moved to `D:\C_Yedek_2026-10-15\...\ulka\` (this broke interpart links to the control part: a trap, see below). Staged as `drive_source/` and `work/`.

### Workflow (step by step, reconstructed from scripts + logs)
1. **Method inherited from R385.** `drive_source/CLAUDE.md` copies the R385 rules (control part with interpart expressions, single writer, CRs, derived-values labelled, rigid refit before blaming the model) and adds: gates K1-K3 fixed before modelling, NX lock + RAM check because the machine had 15.6 GB, instruction to check two-sided scans for a symmetry-step merge error (lesson from R385 HS03).
2. **Stage 1, measure (B, C, D in parallel, A too):**
   - A: `an/a01_inventory.py`, `a02_views.py`, `a03_axes.py` (remove the scanner table plane(s), find the revolution axis, write a rough frame with r(z) envelope), `a04_profile.py`, `a05_multi.py`, `a06_em02.py`, `a07_em02holes.py` (EM02 hole pattern), `a08_loops.py`, `a09_levels.py`, `a10_rings.py`, `a11_noise.py` (**per-feature noise table**: cone/cylinder residual sd on clean bands and planes, e.g. DR01 armature OD sd 0.022, HS01 tube sd 0.041, HS02 body sd 0.073, EM03 OD 0.034), `a12_hs02flat.py`. All use `ulkalib.py` (adapted `r385lib.py`).
   - A builds the **axial stack** without any assembled scan: from mating faces, hole/OD relations (e.g. EM03 18.9 + HS04 9.1 + EM03 18.9 = 46.9 vs frame inner depth 47.12), labelled photos, teardown video frames and the datasheet total length 122 mm (55+50+18). Result: Z table in `sessions/A_MEASURED.md` section 2; closed chain EM03-B, SL01, HS01 flange, socket, HS05, HS02 flange, SL03, HS03 shoulder (rigid 13.82 vs gap 16.37 so the two O-rings compress 15 percent).
   - D splits the **combined scans** (parts of several kinds scanned one-sided on a base plate): `parts/D_an/split.py` (RANSAC plane + least squares of the base plate, keep 0.25 mm above, connected components, match clusters to photos), then `axis.py` (axis = smallest eigenvector of the normal covariance, refined by normal-line fit), `cfit.py`, `m_rings.py` (torus fit for O-rings), `m_hs03*.py`, `m_vl03.py`, `m_vl05.py`, `thz.py` (unwrapped r(theta,z)).
   - C: `C_common/rb.py`, `s1_census.py`, `align_ax.py` (clean, refit axis on a chosen wall, set z origin on a chosen level), `prof.py`; spring work in `spring_fit.py`/`spring_fit2.py`/`spring_fit3.py`/`spring_realign.py` (see step 4).
3. **Gate Rev A..H (A).** A publishes `ULKA_INTERFACES.md` + control part `ctrl/EP5-AS00_CTRL.prt` (`mk_params.py` -> `ctrl_params.json` -> `ctrl_build.py`, 152-155 expressions, 14 datum planes, `PUMP_AXIS`). Frame: Z = common axis of the two big EM02 holes (+Z inlet to outlet), origin on the outer face of the EM02 outlet wall, +Y = strip width side with the coil terminals. Gates (INTERFACES section 6): K1 functional features +/-0.05 mm (band = max(0.05, 2 sd) for weak features), K2 >= 90 percent of scan samples within T = max(0.15, 2.5 sd_part) after rigid best fit, K3 no hard interference except listed ones plus stroke sweep. Revisions A..H each came from a CR (wire diameters given by the owner, spring OD, O-ring sizes, coil length, bend radius, coil offset), e.g. Rev F (CR-D-03): O-ring cross sections; Rev H: `z_em01_term` -3.30 after the assembly found a flange edge inside a bend radius.
4. **Stage 3, per-part journals** (`parts/<code>/build.py`, shared `nxlib/rj.py`, `ps.py`, `geo.py`, `D_common/nxlib/dsmall.py` for the small revolved parts HS05, VL01, VL03, VL05, SL01-SL04). Run through `C_common/nxrun.sh` / `an/nxrun_a.sh` (takes the `nx.lock` directory, waits for >= 2.5 GB free RAM, calls run_journal.ps1 headless).
   - Revolve-based parts: single revolve profile sketch (DR01: rear pilot, armature, front step, collar, piston, bores, ball seat), cross-hole Extrude Subtract, edge blends.
   - **Sheet metal EM02:** NX Sheet Metal Tab (inlet wall) -> 2 Flanges (flat walls, inner radius expression) -> 2 Flanges (outlet-wall halves) -> Normal Cutouts for holes/notches -> two window cuts as extrude-subtract; K factor 0.44 derived. Uses `NXOpen.Features.SheetMetal`, `SheetmetalManager.CreateMultiFlangeBuilder`, `FlangeBendPropertiesBuilder`, `NormalCutoutBuilder`, `sheet_metal_bracket.py` from the nx-sheet-metal skill.
   - **Springs DR02, DR03 (and VL02/VL04):** centre line = **Law Curve by equation** (`CreateLawCurveBuilder`, `LawBuilder.Type.ByEquation`, parameter `t`), x,y = coil_d/2 cos/sin(360 n_t t) and z piecewise: closed-end pitch = wire + gap for a1 turns, quadratic pitch ramp, active pitch, ramp, closed end; active pitch DERIVED from free length l0, so d, D, l0, n_t are the masters. `Tube` along it (`nxf.tube`), then two Trim Body at z = 0 and z = len for ground ends (`C_common/nxlib/spring_nx.py`, `spring_job.py`). Installed (compressed) copies share the same journal with `len` set by the assembly.
   - Control-part dependent re-runs after each Rev; every journal ends with `c.finish()` (Examine Geometry, STL per body, STEP round trip).
5. **Deviation + QA.** Builder side: `C_common/dev.py` / `D_common/dev_d.py` (signed deviation, zones, pose refit; `dev_spring.py` for wire sections). A side: `an/qa_dev.py` (own multi-start rigid fit: principal-axis starts x 4 sign cases + 24 turns for symmetric parts, point-to-plane ICP from every start, best trimmed median kept; K1 via same primitive fitted to scan and CAD from `an/qa/specs/<code>.json`; reverse coverage), `an/qa_holes.py` (off-axis holes/pins), `qa_dev_r385.py`. Output `sessions/A_QA.md`.
6. **Assembly** `cad/assembly/asm_build.py` (+ `ctrl/ctrl_build.py`): sub-assemblies AS01-03, AS00, clearance pairs, armature stroke sweep dz -8.13..+2.58 (13 steps; magnetic stroke 7.63 + 0.5 margin), compressed spring copies, STEP. Re-read outside NX with `an/qa_step.py` and `an/occ_common.py` (OCP Common volumes of STEP pairs).
7. **Theory (E, consumer):** `theory/calc/c1_geometry.py` (reads STEP geometry) .. `c7_fit.py` (magnetics, dynamic model, 48 W calibration, Q-p, losses, sensitivity); produced CR-E-01 (derived VL02 spring and chamber-bottom depth prevent the suction valve from opening). Not CAD; listed for completeness.

### NX tools and NXOpen APIs used
- Headless `run_journal` through `nxrun.sh` (bash wrapper with lock + RAM check) and `run.ps1`/`run_many.ps1`; 8 direct run_journal calls counted in the transcripts, the rest hidden in wrappers (482 python invocations in total). One NX process at a time by lock.
- Helper modules `nxh`, `nxf`, `nxa`, `nxre.stl_export` plus project `rj.py`/`ps.py`/`geo.py`/`dsmall.py`/`spring_nx.py`. `nxh.builder_doc` / `enum_names` were used to probe builder properties (`C_common/probe/helix_probe.py`).
- NXOpen API names seen: `Features.HelixBuilder` (`CreateHelixBuilder`, tried first: `Types.AlongVector`, pitch law Constant), `CreateLawCurveBuilder` / `Features.LawCurve` with `GeometricUtilities.LawBuilder.Type` (ByEquation, ByLawCurve, MultiTransition ...), `Features.SheetMetal` (MultiFlange, FlangeBendProperties, NormalCutout), `Preferences.PartSheetmetal.BendDefinitionMethodOptions.NeutralFactorValue`, `SmartObject.UpdateOption.WithinModeling`, `NXOpen.Matrix`, interpart expressions via `nxa.interpart_expr`. Also Tube, Trim Body, Revolve, Extrude, datum plane/axis, hole, blend, pattern.
- No Fit Surface / Replace Face anywhere: all geometry is modelled from numpy-fitted values; the facet body is never used inside NX. nx-mcp certified tools not used.

### Accuracy / deviation results
(from `sessions/A_QA.md`, `A_STATUS.md`, per-part `cad/*_REPORT.md`)
- K2 (share within T after A's own best fit; gate 90 percent), PASS: HS04 95.1, EM03 94.4 (second sleeve; first sleeve 93.7 once the unscanned end is excluded, listed before QA), DR01 **98.9** (K1 9/9, median deviation 0.011), HS01 96.2 (K1 7/7), HS02 95.4 (T 0.18), HS05 93.9, SL01 97.5 (after Rev F cross section 2.20), SL04 91.3, VL01 100, VL03 95.6.
- Did not hold (reported with measure): HS03 85.8-86.1 (K1 9/9 pass, noise limit sd 0.07-0.12), EM01 89.0-89.4 (K1 4/4, plate/Klixon moulding detail not modelled), EM02 89.8 (K1 10/10; sheet flatness and bend bulges not modelled), SL02 88.4 (K1 pass), SL03 85.4 (thin ring, K1 ID -0.015/OD -0.011 pass), DR02 71.0 and DR03 83.9 (wire bulge: CAD wire 1.0/1.3 given by the owner vs scan wire 1.22/1.43, +0.11 per side; the model keeps the true wire, the scan was not "fattened"), VL02 40, VL04 37, VL05 49 (fragmentary scans of 0.45-0.5 mm wire; dimensions from photos/outer diameter).
- Functional hole fits: EM02 big holes -0.004/+0.007, EM02 off-axis holes (FS01 seats, pins) +0.006..-0.057; DR01 armature OD +0.006, d_p -0.004; HS01 tube OD -0.021, collar +0.043.
- Assembly Rev H: 23 solids, STEP re-read in OCP: 23 solids, 0 invalid, total volume 103118.0 vs NX 103118.2 mm3, length 121.62 vs datasheet 122. Hard interferences only the expected ones (O-ring squeeze DR01/SL04 3.11, HS01/SL01 33.15, HS01/SL02 7.62, HS02/SL03 3.58, HS03/SL03 3.67 mm3, M4 thread in EM02 5.31). Stroke sweep: no collision; collar touches HS05 at +2.58 (designed stop).
- Functional check by E: with derived VL02 (wire 0.5) and chamber bottom (24.0), the suction valve does not open in the dynamic model (0 bar flow 405 vs datasheet 650 cm3/min): geometry passes, function fails; flagged as CR-E-01 and an owner measurement request list (6 items) instead of tuning the CAD.

### What worked / what failed
- Worked:
  - Reusing the R385 toolchain by copy (rb.py, rj.py, ps.py, dev.py, report.py, qa_dev.py) cut each part to one journal plus a one-line deviation script; revisions A..H were absorbed by re-running journals (about 1 min for the small parts).
  - Gates K1-K3 and the noise table set before modelling: failures to meet K2 are explained by noise or unscanned regions rather than hidden.
  - Axial stack reasoned from mating geometry, photos, videos and datasheet when no assembled scan existed, with every number tagged measured/derived.
  - Spring modelling by Law Curve equation + Tube + Trim Body gave a parametric, free-length-driven spring where the helix is exact; spring parameters (closed-end coils, ramp lengths, phase) were fitted to the scan by least squares to the centre line (`spring_fit3.py`, wire-centre cylinder rms 0.04-0.05 mm).
  - Two independent registrations (builder's own and A's multi-start ICP) agreeing, plus off-axis hole QA (`qa_holes.py`).
  - Sheet metal EM02 in real NX Sheet Metal with bend radius expressions, giving a flat-pattern-capable model.
  - Single-sided base-plate scans split by plane fit + connected components + photo matching (`split.py`).
- Failed / traps:
  - **Helix feature with a broken (piecewise) pitch chain does not feed one tube**; D noted that a chain of helix segments could not go into a single Tube and rewrote the spring on the Law Curve basis (log line "kirikli helis zinciri tek tupe girmiyor").
  - **Scan wire "bulge"**: fine wires (0.45-1.4 mm) scan 0.07-0.11 per side too thick, so K2 for springs and VL02/VL04 cannot pass if the model uses the true wire; the project decided to keep the real wire (owner-measured) instead of inflating CAD.
  - A's QA registration put HS02 upside down on the first Rev D run (75 percent) until the axial search range was widened to +/-7.5 mm; always check the fit motion and the reverse coverage, not just the share.
  - Free circle centre drifts on cylinders with < 180 deg coverage (HS04 OD free 20.44 vs 20.78): measure diameter relative to the whole-part axis (`D_axis`).
  - Combined one-sided scans lose the base-plate-side 0.25 mm and the lower half of elastomers; thickness checks on O-rings are not possible (bands +/-0.10 only for the upper half), SL03 appears flat on the table.
  - Weak scans (VL05 30-49 percent) cannot be validated by K2; shape came from photo F18.
  - Moving the workspace folder to another drive broke interpart links (parts search the control part at the old path); relink or move back needed. A also overwrote `ULKA_INTERFACES.md` by accident and restored it from a copy on D.
  - Resource trap: parallel sessions waited on a single NX lock; Rev publications queued behind journals for minutes (lock-poll every 30 s).
  - Inconsistencies between derived values and datasheet remain open (G1/8 thread length 4.8 vs datasheet "min 7", spring constants vs owner wire diameters, SL01 position).

### Key files (relative to `STAGE\ulka_pump`)
- `drive_source/CLAUDE.md`: project rules, roles, NX lock/RAM rules, tool list (Turkish).
- `drive_source/ULKA_INTERFACES.md`: frame, interface values, gates K1-K3 (section 6), open points (CR-E-01).
- `drive_source/sessions/A_MEASURED.md`: axial stack and frame derivation; noise table section.
- `drive_source/sessions/A_QA.md`: all QA tables (K1/K2) and assembly runs 2-4.
- `drive_source/sessions/D_MEASURED.md`: splitting combined scans, O-ring/valve measurements.
- `drive_source/sessions/C_STATUS.md`, `D_STATUS.md`, `B_STATUS.md`, `A_STATUS.md`: state, results, rev history.
- `work/an/qa_dev.py`: independent multi-start registration + K1/K2 + reverse coverage.
- `work/an/a11_noise.py` (+ `a11_noise.json`): per-feature noise measurement used to set tolerances.
- `work/an/a03_axes.py`: table removal and revolution axis from a raw scan.
- `work/parts/C_common/nxlib/spring_nx.py`: Law Curve + Tube + Trim Body compression spring (closed/ground ends, derived pitch).
- `work/parts/C_common/spring_fit3.py`: least-squares fit of spring centre-line parameters to a scan.
- `work/parts/EM02/build.py`: NX Sheet Metal frame journal (Tab, Flanges, Normal Cutouts).
- `work/parts/DR01/build.py`, `work/parts/HS01/build.py`: revolve-profile parts with linked expressions and checks.
- `work/parts/D_common/nxlib/dsmall.py`: builders for the small revolved parts (O-rings as torus, ball, plug, cage).
- `work/parts/D_an/split.py`, `axis.py`, `m_rings.py`: combined-scan splitting, axis from normals, torus fit.
- `work/parts/C_common/dev.py`, `D_common/dev_d.py`: builder-side deviation scripts.
- `work/ctrl/mk_params.py`, `ctrl_build.py`, `ctrl_params_revA..H.json`: parameter table to control part, revision history.
- `drive_source/cad/assembly/asm_build.py`, `drive_source/cad/assembly/asm_build.json` (logs in `work/asm/`): assembly and stroke sweep.
- `work/an/nxrun_a.sh`: lock + RAM guarded journal launcher.

### Files in package (ulka_pump)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## lexus_seat_clip
- **Purpose / part type:** Spare plastic clip from the back cover of a Lexus car seat (its twin broke), scanned with a CR-Scan Raptor
  (`Mesh_20261024135528.stl`, 500 604 triangles, the part lying on a non-flat surface). A thin-wall moulded part: 46.8 x 41.6 x 2.0 mm plate with
  R4.5 corners and a round locating ear, an upright bent strap (1.35 mm wall: leg 15 deg from vertical, outer bend R3.4, R9.6 top bend,
  55 deg incline, rolled tip bead), outer gusset + rib (2.15), inner lower fin (1.25), a spring tongue (1.35), root fillets. Deliverable: accurate native NX model + a 3D-printable STL (user's words), STEP too.
- **Dates:** 2026-10-24 (build, delivery RV01), small follow-up 2026-10-25. The transcript continues with unrelated video/film work after the CAD part; only the first part is relevant.
- **Sessions:** `transcripts/3d9eaa45-a683-4598-b6b8-8dd4c5d086b2.jsonl` (the film scripts such as plan_all.py, sound.py in its tool stats are not CAD).
- **Source folders (original paths):** work `C:\NX_MCP_WORKSPACE\lexus_seat` (an\ scan analysis, nx\build.py + nx\nxlib\); delivery `C:\Users\marya\Desktop\lexuspart\CAD_RV01`
  (prt, stp, stl, README, deviation map, src); input scan `Desktop\lexuspart\Mesh_20261024135528.stl` (not in STAGE).
  STAGE copies: `desktop_lexuspart\CAD_RV01\` (delivery incl. src), `work\` (an\ json/png, nx\out build log, view renders), `mesh_135528\` (see "Failed" below).

### Workflow (step by step, reconstructed from scripts + logs)
1. **Look and separate the part from the background.** Renders of the raw scan (`work/views0..3`, `mesh_135528/render_views.py`, `vtk_render.py`) show the part sits on a larger surface.
   `desktop_lexuspart/CAD_RV01/src/an/align.py`: RANSAC plane (400 random triples, +-0.3 mm inliers) refined by PCA -> table frame (`work/an/table_frame.json`), normal flipped so the part is above.
2. **Part frame.** `src/an/frame.py`: plate normal + clock from a plate-plane fit, plate extent from 0.2/99.8 percentiles -> centred rectangle, writes `T_scan_to_part` (`work/an/part_frame.json`),
   crops the part (`crop.stl`). `reframe.py` / `src/an/part_frame2.json` = second frame, re-aligned on the **upright** (strap/rib/tongue) because it is the functional part (see lean finding below).
3. **Section slices and profile points.** `src/an/slices.py`, `prof.py`, `side.py`, `strap.py`, `plate.py`/`plate2.py` (plate outline, corner radii, ear fit R3.83), `edge.py`, `outline.py`, `meas1.py`/`meas2.py` (thicknesses),
   `tonguerib.py`, `zoomx.py`/`zoom2.py` (zoom plots). Output = outer-surface line directions and wall thicknesses (leg 15.06 deg, mid 15.84 deg, incline 55.10 deg; walls 1.35 / 2.15 / 1.25).
4. **Chain fit.** `src/an/fitchain.py` (+ `fitR.py`, `fitprof.py`, `finenv.py`): `scipy.optimize.least_squares(loss="soft_l1", f_scale=0.1)` of a line + tangent-fillet chain
   (using the pure-Python builder `nx/nxlib/chain.py`) to the slice points via a point-to-polyline distance (`geo2.py polydist`). Fitted outer radii rA 3.36, rB 9.58, tip R1.3; tongue chain with 3 radii; result `work/an/chainfit.json`. Residual rms/p95 printed per chain.
   Points of ghost lines (neighbouring structure seen in the slice) and inner faces were masked by hand before fitting.
5. **Design values** `nx/nxlib/design.py` (`PARAMS` + `strap_profile`, `gusset_profile`, `fin_profile`, `tongue_profile`, `tongue_rib_profile`, `plate_outline`): every value is "measured -> chosen" with the scan number in a comment; undersides of the strap/tongue taken as offset by wall thickness from the scanned face.
6. **Build** `nx/build.py` (103 lines, headless): new part, `PARAMS` as named expressions; plate XY sketch (rounded rectangle + ear) extrude down `tp`; strap, GUSSET_RIB, LOWER_FIN, TONGUE as XZ-plane profile sketches
   extruded symmetric about y = 0 by width expressions (`ws`, `tg`, `tf`, `wt`) with Unite; TONGUE_RIB extruded asymmetrically (`trib_y0`..`trib_y1`); root fillet R0.6 on the 11 concave edges lying at z = 0
   (`nxf.sharp_edges` + `nxf.blend_chains`); then STL (`nxre.stl_export` chord 0.005, max edge 2.0) and STEP (`nxf.step_export`). Log `work/nx/out/build.log`: all 6 sketches WellConstrained DOF 0, one solid after every step, 8120.8 mm3, no feature errors.
7. **Deviation** `src/an/dev.py` (60 000 random scan vertices vs CAD STL, open3d RaycastingScene signed distance, hand-written zone classifier by x/y/z boxes; plus CAD->scan nearest-vertex coverage), `devmap.py` (coloured map), `cadview.py` / `render*.py` (CAD views), `overlay.py` (section overlay scan vs CAD).
8. **Delivery** README with dimensions, zone table, print advice (PETG/ASA/PA, supports under tongue, strap wings and tip, >= 3 perimeters), deviation map, six CAD views. `work/an/cmp_usta.py`: later compares the CAD STL with a copy on the Desktop edited by the user (volume, bounds, signed distance both ways, differing-region clusters).

### NX tools and NXOpen APIs used
- Headless NX 2206 via `run_journal.ps1` (3 run_journal calls in the transcript; 159 python calls for the scan analysis; the cadgenbench venv with open3d, trimesh, scipy).
- Helpers: `nxh` (new_part, expr, Datums, solids, volume, bbox, edge_points, body_ok, feature_errors, Log, write_json, save), `nxf` (`extrude_ex(section, dir, start, end, symmetric, op, target)`, `sharp_edges`,
  `blend_chains`, `step_export`), `nxre.stl_export`, and the project `ps.Sketch` (same class as in the Dreame job: `profile(V, arcs=...)`, `finish()` returns status + DOF, `section()`), `chain.py`.
- Only NXOpen type named directly in the journal: `GeometricUtilities.BooleanOperation.BooleanType.Unite`. Sketches on XY/XZ datum planes, Extrude (two-sided symmetric and asymmetric limits driven by expressions), Edge Blend. No Fit Surface, no facet selection in the delivered build.
- No NX MCP tools for modelling.

### Accuracy / deviation results
- `desktop_lexuspart/CAD_RV01/deviation_rv01.json` (60 000 scan points, signed distance scan - CAD, mm): all rms 0.269, p50 0.108, p95 0.592, max 1.48, 80 % within 0.3.
  By zone p95 (p50): gusset 0.22 (0.06), leg 0.35 (0.06), lower fin 0.29 (0.10), rib/strap centre 0.18 (0.07), strap top + incline 0.30 (0.08), tongue 0.21 (0.06), tip bead 0.62 (0.22), plate top 0.81 (0.30).
  Scan noise about 0.1 mm. CAD->scan nearest vertex: p50 0.34, share > 1 mm 34 % (the unscanned undersides and underside-facing walls; not an error measure).
- Before the final gusset fix (`work/an/dev_rv01_pre.json`): gusset p95 0.64, "other" p95 1.26, all p95 0.65; the final run improved gusset to 0.22 and tongue p95 0.23 -> 0.21.
- Plate top deviates on purpose: the scanned upright leans about 2 deg about X relative to the plate and the plate is twisted +-0.4 mm; CAD is square/flat, frame aligned on the upright.
- STEP: 1 valid solid, 8120.7 mm3; STL watertight, 1 shell. No print test and no fit feedback yet (open).

### What worked / what failed
- Worked: for a bent thin-wall strap, fit a *chain of lines + tangent fillets* (angle, radius per bend) to section points, then build the sketch from the same chain with exact offsets for the inner face (`chain.py`). Sketches came out DOF 0 on the first run.
- Worked: every width/thickness is a named expression (`t`, `tg`, `tf`, `ws`, `wt`, `tp`, `r_root`), so the README can say "raise `t` and re-run the journal".
- Worked: a feature-by-feature headless build that logs volume, DOF and solid count after each step (build.log); one-body invariant checked each time.
- Worked: choosing the datum on the functional feature (upright) instead of the plate, and saying so, with the plate-top number reported honestly (p95 0.81).
- Worked: ejector-pin marks and the unscanned undersides handled as explicit design-intent decisions in the README, not silently modelled.
- Failed / traps:
  1. First attempt `mesh_135528/` (an earlier or parallel run, not in the supplied transcript): NX-side `re_measure.py` imported the STL as a convergent body (197 k facets after cropping) and ran a census, then
     `nxre.measure_plane` crashed in `rule_facets` (`CreateRuleSingleFacet`: "First parameter is invalid"; `out/re_measure.log`). That path was dropped for pure numpy/trimesh planar census
     (`planes_final.py`, `identify_planes.py`, `datum_fit.py`, `part_extract.py`, `final_offline.py`) producing `offline_params.json`, pad frame `padframe2.json`, recess search (`recess.py`). The delivered build (work\lexus_seat) used trimesh slices + least-squares chain fits instead, with no facet fitting inside NX.
  2. The part rests on a surface that is not flat, so the table plane cannot define the datum; the plate is twisted too. Use the upright / functional feature.
  3. Thin walls (1.25-1.35 mm) are about 10x the scan noise; thickness is read from facing faces 1.38 apart, so error is a few hundredths only after averaging many slices. Undersides never scanned.
  4. Zone classifier in `dev.py` is a set of hand-set boxes in the part frame; the "other" zone (1181 points) stays at p95 0.47.
  5. Root fillet radius (0.6) is a guess from the scan (0.5-1 mm); STL export reported nerr = 1 (one tessellation error, not investigated).
  6. Fit hygiene: soft-L1 loss with f_scale 0.1 and manual masks around the tongue joint were needed so that adjacent faces did not pull the chain fit.

### Key files (path relative to STAGE\lexus_seat_clip)
- `desktop_lexuspart/CAD_RV01/README.md` - delivered summary: dimensions, zone table, print advice, unmodelled items.
- `desktop_lexuspart/CAD_RV01/src/nx/build.py` - complete headless NX journal (plate, strap, gusset, fin, tongue, rib, fillets, STL/STEP).
- `desktop_lexuspart/CAD_RV01/src/nx/nxlib/design.py` - all measured values and closed profile builders (measured -> chosen).
- `desktop_lexuspart/CAD_RV01/src/nx/nxlib/chain.py` - pure-Python line + tangent-fillet chain with exact offsets (usable in build123d too).
- `desktop_lexuspart/CAD_RV01/src/nx/nxlib/ps.py` - Sketch wrapper that returns DOF-0 sketches from vertex/arc lists.
- `desktop_lexuspart/CAD_RV01/src/an/align.py` - RANSAC plane + PCA refinement for the table/base plane.
- `desktop_lexuspart/CAD_RV01/src/an/frame.py` - part frame from the plate plane, extent centring, scan->part matrix.
- `desktop_lexuspart/CAD_RV01/src/an/fitchain.py` - least-squares fit of the line + fillet chains to section points.
- `desktop_lexuspart/CAD_RV01/src/an/geo2.py` - point-to-polyline distance used as the fit residual.
- `desktop_lexuspart/CAD_RV01/src/an/slices.py`, `plate2.py`, `meas1.py` - slice extraction, plate outline / radii, thickness measurements.
- `desktop_lexuspart/CAD_RV01/src/an/dev.py` - signed deviation per zone + CAD->scan coverage (open3d).
- `desktop_lexuspart/CAD_RV01/deviation_rv01.json` - final numbers; `work/an/dev_rv01_pre.json` - the pre-fix run for comparison.
- `work/an/chainfit.json`, `work/an/part_frame.json`, `desktop_lexuspart/CAD_RV01/src/an/part_frame2.json` - fit results and the two frame matrices.
- `work/nx/out/build.log` - per-step volume / DOF log of the delivered run.
- `work/an/cmp_usta.py` - compare two STLs (watertight, volume, bounds, signed distance both ways, difference clusters).
- `mesh_135528/re_measure.py`, `mesh_135528/out/re_measure.log` - the abandoned NX facet-census attempt and its failure.
- `mesh_135528/planes_final.py`, `datum_fit.py`, `part_extract.py` - offline planar census, datum RANSAC, part/background separation.
- `desktop_lexuspart/CAD_RV01/cad_views.png`, `work/an/overlay.png`, `work/an/prof.png` - visual evidence (CAD views, section overlay, fitted profile).

### Files in package (lexus_seat_clip)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## left_thigh_outer_inner
- **Purpose / part type:** Robot left-thigh housing: two mating aluminium (CNC) shells scanned separately and rebuilt as native NX parts, plus their assembly. LT-OUT-001 (outer: knee hub, hip ring, interior ribs/bosses), LT-INN-001 (inner, mates on a split plane), LT-ASM-001 (outer + inner, fit-gated). Deliverables per revision: NX prt, STEP AP214/AP242, x_t, STL, deviation report (PDF + maps), CNC drawings (PDF + DWG, GD&T), renders, zip. Scans: outer 7.27 M triangles, inner 7.44 M triangles (open, two-sided). The agent never sent anything to the client; a human lead hand-edited the NX parts between rounds and their edited "overlay" prt became the master each time.
- **Dates:** 2026-10-24 (first outer scan load) to 2026-11-02. Revisions: outer A (10-25), B (10-30, cancelled), C (10-31), F (11-02); inner A (10-29/30), B (10-31), E/E2 (11-02); assembly A (10-30), B (10-31), E (11-02).
- **Sessions:** transcripts/44064e17-92e5-4b7e-96c3-b3147b9c15fb.jsonl (outer Rev A origin, drawing rules), 3ab8288a-a0ca-44f8-a4cd-379fc50a1d56.jsonl (inner fix round rejected, "no auto blob fixes"), f71cbaea-f2f1-42f0-bb9c-9e1f593c2b75.jsonl (side window + 9 inner ribs in a live NX session), 59b5e9a2-b2fc-467f-b35e-53a9f8822d1b.jsonl (Rev F / inner E / assembly E packaging), plus 0b84b9d6, 0bc8682e, 0d2c6100, 16b5c31a, 31f00b73, 573cceaf, 73a8eec7, 8df73ba3, 95e57f8d, b1cdd1bf, cbeb69e1, ce4111eb, efca19c7, ff91f392 and the sub-agent folders `0d2c6100_subagents`, `16b5c31a_subagents`, `59b5e9a2_subagents`. Tool counts (tool_stats.json): Bash 3586, Read 1757, PowerShell 877, Write 522, Edit 380, about 586 headless `run_journal` launches, about 2736 Python script runs, 66 computer-use batches (GUI looks only), 25 Agent calls.
- **Source folders (original paths):** `C:\Users\marya\Desktop\Left Thight Reverse Engineer` (root; `part 1` outer, `part 2 - Inner`, `part 4 - Assembly`; `part 3 - Chest` is a separate project), NX work folders `C:\NX_MCP_WORKSPACE\lt_window`, `lt_ribs3`, `lt_conn`, `lt_inner_pins`, `lt_inner_win`, `lt_inner_ribs`, `lt_inner_r8`, `lt_inner_revB`, `lt_inner_revE`, `lt_inner_fitE`, `lt_revE2`. Staged as `project/` and `ws/`.

### Workflow (step by step, reconstructed from scripts + logs)
Phase 1 - automatic first build of each shell ("Rev A"):
1. Load and weld the scan: `project/part 1/an/s0_load.py` -> `work/scan.npz` (shared reader `an/common.py`: `load()`, `section()`, `tri_data`, `fit_plane_robust`, `fit_circle_robust`).
2. Datums from the scan itself: `an/s3_parting.py` (parting plane = Z), `s4_frame.py` (origin on the knee-bore axis at the parting plane, Z = plane normal, Y = hip-ring axis projected, knee -> hip), `s5_rim.py`, `s6_axes.py`, `s9_hip.py` -> `work/frame.json`. Inner shell: registered INTO the outer frame (inner = outer turned 180 deg about Y) by 13 boss-axis point pairs, RMS 0.041 mm (`part 2 - Inner/an/i2_rim.py` -> `i4_feats.py` -> `i5_cyl.py` -> `i7_register.py`, checks `i8_check.py`); held-out check with 3 pin/hole pairs 0.04-0.06 mm off-centre.
3. Feature census: `an/s2_census.py`, `s13_levels.py` (13 interior height levels), `s17_bosses.py`, `s18_holes.py`, `s14_inner.py` (cavity); inner `i1_census.py`, `i24_bosses.py`, `i29_holes.py`, `i27_windows.py`, `i28_grooves.py`.
4. Freeform outer skin: `an/s10_skin.py` / `s11_skin2.py` = tensor cubic B-spline least squares r(y, theta) about a centre line with a 2nd-difference penalty (8 mm x 4 deg knots); outer uses two-pass seam exclusion, inner uses "exclude only rows where the scan is INSIDE the fit" with 4 robust passes (`i20_skin.py`). `an/s12_sections.py 42 8 skin_fit sections` -> Through-Curves loft sections (clamped cubic B-spline, 42 poles, every 8 mm) in `work/sections.json`.
5. Plateaus/outlines (everything parallel to the parting plane): `an/hmap2.py` (0.2 mm height map seen from the open side), `s16_outlines.py` (loops -> line/arc segments via `arcfit.py`), `s19_platnx.py` (per-level loop groups for NX); windows `s20_windows.py`/`s21_winloops.py`; grooves `s22_grooves.py`/`s23_groove_paths.py`. Inner: `i14_hmap.py`, `i23_outlines.py`, `i26_rebate.py`, `i62_depthdiff.py` (finds missed plateaus).
6. Design values rounded into `nx/params.json` (inner `an/i30_params.py`).
7. NX build in staged journals, each stage saves the part so a later stage resumes from a copy: `project/part 1/nx/build2.py <out> H` (A envelope + hub via loft + block trim, B cavity shell, C plateaus/ribs/bosses/pads/tongue, D hip plate + ring, E bores/hole patterns, F bosses/pins/small holes, G/H windows + grooves; about 13 min); inner `project/part 2 - Inner/nx/build_inner.py` stages A..K (30-40 min per stage, booleans 5-12 min each on that body).
8. Finalize: `nx/finalize.py` (one solid, helper geometry to layer 200, reference set SOLID, exports AP214/AP242/x_t/STL, mass), inner `finalize_inner.py`.
9. QA: `an/dev2.py` / inner `i40_dev.py` (two-way signed deviation by zone), `an/hdiff.py`, `an/stepcheck.py` (OCP validity, volume, bbox on the STEP because NX re-import imports nothing), `an/report.py` -> REPORT_deviation.md + 7 maps.
10. Overlay for the human: `an/s30_scan_aligned.py` + `nx/overlay.py` copy the finished prt and add the scan as Convergent Body (orange, 50 % translucent, layer 10). The user then edits this overlay by hand (Replace Face, Offset Region, blends) and it becomes the master (outer: 3 Replace Face + Offset Region + 2 Edge Blend).

Phase 2 - "marked details" rounds appended on the user's master (dominant pattern from 10-30 on). The user marks spots in a screenshot; the agent measures the scan locally (`ws/lt_ribs3/a1..a9`, `ws/lt_inner_r8/a1..a10`; map the photo camera with a matched pyvista render `v7_match.py`), builds clean primitives at the END of the feature tree in a named feature group (FEATURES_R4, CLEANUP_R3, FIT_REVE ...), checks, saves a new file beside the master (never in place):
11. Journal pattern (`ws/lt_ribs3/j1_add.py`, `ws/lt_inner_r8/j2_r8.py`): helpers `sketch(name, origin, normal, hdir, curves_fn)`, `extrude(sk, vec, start, end, op, until, symmetric)`, `sketch_prism`, `g1_sheet`, `extend_all`, `trim_keep`, `unite`, and `step(key, fn, must_in, must_out)` which runs one feature, then asserts point containment (solid at must_in points, empty at must_out), body count and volume delta, and reports PASS/FAIL per feature. Radial ribs via polar placement, bosses on inclined mid-wall datum planes, pads buried along the wall mid-surface, holes as expressions-driven cylinders.
12. G1 wall transition: `ws/lt_ribs3/r2/j3_wall.py`, `j4_m1_lip.py` (two G1 Through Curves sheets trim a block, then unite).
13. Spec-driven rib networks: `ws/lt_inner_ribs/j1_ribs.py` (31 features) from `spec.json` made by measurers (`b1_spec.py`, hmap diff, straight-rib and arc-rib measurers); later `j2_more.py`, `j3_final.py`. Live-session side window and ribs: `ws/lt_window` (j2_win.py, j5_side_window.py, ribs/r5..r17; tangent line/arc profiles fitted to the scan outline in the wall's PCA plane).
14. Connector pad, slots, rim: `project/part 1/nx/conn_pad.py` (revolved sector about the hip axis, driven by CONN_* expressions), `revB_slots.py`, `fix_r2.py`, `fix_r3_rim.py`.
15. Inner cleanup after the "mud" feedback: find junk faces by owning feature (UF AskFaceFeats), Delete Face with a body-bbox-growth guard, lip facets -> spline sheet + Replace Face (`lt_inner_pins/round3, round4`; not all staged).
16. Finalize WITH history for packaging (user parts carry 400-620 features): `part 1/nx/finalize_revF.py`, `part 2 - Inner/nx/finalize_revE.py`, `finalize_inner_revB.py`, `ws/lt_inner_revB/j2_unscan.py`: replace scan Fit Surfaces by frozen copies (Replace Feature, re-point a dropped Replace Face), delete the scan, verify with 4000 point probes + difference booleans, ONE accurate volume at the end.
17. Fit gate between mating shells, in OCP and independent of NX: `project/part 4 - Assembly/an/fit_check.py` (boolean common, min distance, all coaxial cylinder pairs of any axis, joint planes, whole-part signed distance), `fit_summary.py`, `locate_common.py` (locates hair-line slivers), `grid_overlap.py` / `zstack.py` (0.25 mm ray stacks), `twoway_sd.py`. Assembly prt by `nx/build_asm.py` (components at origin, identity, no constraints, designed in place), STEP re-read with `an/stepasm_check.py`.
18. Drawings and package: `nx/dwg_main.py` (A1, 4-5 sheets, third angle), `nx/dwglib/ptdwg.py`, `gdt.py`, `m3d.py`, assembly `nx/dwg_asm.py`; renders `an/c8_renders.py` (Blender); zip scripts `an/c7_package.py`, `f7_package.py`, `part 4 - Assembly/an/e8_package_all.py`.

### NX tools and NXOpen APIs used
- Almost all headless: `run_journal.ps1` (nx-journal-core skill) running NXOpen Python journals; env vars `NXH_DIR`, `NXRE_DIR`, `NXCK_DIR` point at helper modules `nxh` (open_part, bbox, BOOL, boolean helpers), `nxf` (feature helpers incl. `_rib`), `nxre`, `curvekit`. These helper modules are not in this stage (names only). One output folder per run: two launches queue on the licence and clobber `build.json`.
- Builders seen: ThroughCurvesBuilder (loft of fit sections; G1 sheets), ExtrudeBuilder (sketch/curves, until-next, until-extended, symmetric), BlockFeatureBuilder, revolve (profiles, concentric sectors), BooleanBuilder, ExtendSheetBuilder, ExtractFaceBuilder (frozen wall copies), ReplaceFaceBuilder, ReplaceFeatureBuilder (scan Fit Surface -> frozen copy), AdmOffsetRegionBuilder, PointFeatureBuilder, Rib (Parallel to Section Plane), EdgeBlend (also variable radius), Chamfer, Hole, Delete Face, Trim Body, Fit Surface (user-made on the scan), Examine Geometry, SimpleInterference. Drawings: DraftingFeatureControlFrameBuilder, DraftingDatumFeatureSymbolBuilder, LinearDimension / RadialDimension builders, IdSymbol (balloons), DrawingEditViewLabelSettings, AssociativeOriginData.
- STL via `STLCreator` (Binary); STEP AP214 + AP242 through NX. NX's STEP re-import yields nothing on these parts, so STEP validity = OCP (`an/stepcheck.py`, `bboxcheck.py`).
- Computer use (66 batches) only to look at the user's NX GUI and to drive the live bridge (memory note `nx-live-session-gui-bridge`); the certified nx_* MCP tools were not used for the RE work.
- Non-NX stack: numpy, scipy, trimesh, open3d, pyvista, matplotlib, OCP (OpenCascade) for STEP/fit checks, Blender headless for renders.

### Accuracy / deviation results
Signed scan -> CAD (+ = scan material the CAD lacks), 1.5 M samples, from `REPORT_deviation.md` files and `STATUS*.md`:
- Outer Rev A: whole part p50 0.053, p90 0.541, p95 0.983 mm, 79.8 % within 0.2, 89.2 % within 0.5; outer freeform skin p50 0.021, p95 0.352, 97.4 % within 0.5; knee hub 83.9 %; hip ring 90.2 %; interior (ribs, pockets) 85.8 %. CAD -> scan unsigned p50 0.066, p95 1.98. Volume 385 943 mm3, 1.042 kg.
- Outer Rev C: 91.1 % within 0.5; Rev F: 89.0 % within 0.5 (`part 1/work/qaF`), lower only because the user's added features/design decisions differ from the scan (ribs A/B/G1 about 1 mm off, F2 pads stop at Z 29.3 vs scan ~35); reported, not changed. 378 954.7 mm3 (Rev F). Side window region p50 0.085 -> 0.048, within 0.5: 80.0 -> 93.3 % (Rev A -> F).
- Inner Rev A (first clean build runK10): skin p50 0.018 / p95 0.27 / 98.4 % within 0.5; whole 87.7 % within 0.5, p95 1.18; 335 389 mm3; registration RMS 0.041 mm.
- Inner review-fix round (stages L/M, auto fixes): whole 91.3-91.5 % within 0.5, but REJECTED by the user (see traps).
- Inner Rev B: whole p50 0.051 / p95 0.97 / 89.3 %, skin 98.6 %, interior p95 1.35 (Rev A 2.57); 338 012 mm3; STEP mesh volume within 0.007 % (AP242) / 0.04 % (AP214); every face within 0.1 mm of the NX surface.
- Fit gates (OCP): Rev A 0.0 mm3 interference, 21 coaxial pairs offset 0.0; assembly Rev B 0 of 600 000 inner points inside outer (deepest -0.004), common 0.0007 mm3 (hair-line slivers; NX SimpleInterference 5.4e-5); Rev E2 final gate PASS, 0 real interference (`project/part 4 - Assembly/work/revE2/final_gate.txt`). Drawings: 13-24 dimensions read back from the part per set, 0 errors, 0 view overlaps.

### What worked / what failed
- Worked: frame from scan datums (parting plane, knee axis, hip axis); second shell registered into the first with bosses/pins as fiducials, validated on held-out pairs. Fitted B-spline skin + loft (p50 0.02 mm, editable). Plateau levels from a height map viewed from the open side, loops converted to line/arc segments. Staged saves and resume-from-copy. Prototype a fix on the mesh first (`fixlib.py`, `i97_sim.py`). Per-feature `step()` with containment/volume assertions and a feature group per round. Independent OCP fit gate for two parts. Work on a copy of the user's master (always `cmp` source vs copy; the user once re-saved 16 s after a copy). Expression-driven extra features (CONN_*). Packaging by scripts; no README in client zips.
- Failed / traps:
  - Auto-generated fix pads from deviation clusters (A0xx, `nx/fixes_M.json`) raised statistics (87.5 -> 91.5 %) but the user rejected them as irregular "mud stain" extrusions; delivery restored to the first clean build (`_fixround_2026-10-30`). Build real features (rib, boss, pocket, slot), accept residual deviation, review CAD-alone renders.
  - Root fillets: NX refused 23 of 35 chains and the 12 accepted made the body invalid; stage I (fillets) dropped.
  - Inner loft starting at y < -30 gave BodyConsistency errors that poisoned later booleans; a 74x80-pole skin made the loft take 400 s and each boolean 8 min (use ~46x42 poles).
  - `revolve_profile` stored arc end angles as revolve limits (profiles with arcs revolved a few degrees); fixed 2026-10-29. A revolved profile touching the axis with an arc gave a 1 152 mm3 sub-loop: build hubs from cylinders + separate revolves, volume-check each.
  - Clearance cuts must be last; anything added later refills them (OCP showed 133 mm3 before re-clearing); auto adds after the clearance went into the mating part unnoticed -> fit-check every finalized part.
  - Scan Fit Surfaces under user points: scan deletion failed ("Update undo happened"); freeze those points first, assert solid volume (caught -46.68 mm3 loss). User's rolled-back tail features and loose bodies are intent: ask, never delete. Do not Update All (an inactive Cylinder in the user's tree breaks the tree).
  - Parallel Rib: material grows toward (curve direction x sketch normal); help point / ReverseRibDirection do not flip it, draw the profile the other way. Also "cannot cap" if a hole is under the footprint or an end is 0.01 above a boss top; perpendicular rib cannot end free; until-next that only touches the floor makes a second body; a rib crossing another rib keeps one side; refused attempts leave stale errors on the next feature (put risky steps last, try the working option first).
  - G1 join to an existing wall: solid Through Curves with G1 + PreserveShape fails; use two G1 sheets + trim block, real edge as first section, remove old material under the transition. Extending a wall face: Replace Face onto a FROZEN extracted+extended copy (associative copy -> circular dependency).
  - Block feature with Subtract + target bodies made a second body; NX CreateEllipse angles are polar; thin-extrude offset sign must be probed; "until next" sees the convergent scan body in the overlay part; accurate volume calls cost 7.5 min to 2 h per run, 0.99-accuracy volumes scatter 10-200 mm3 (useless as check): use point containment and one final volume.
  - OCP GProp volume is wrong on big trimmed B-spline faces (use mesh volume + per-face distance to NX surface); NX AP214 writer turned one 0.1 mm2 face into an unorientable cylinder (AP242 recommended); NX AP242 names the assembly root after the file (rename in text).
  - Drawing: cell text starting with "<" is dropped; long cell text grows the row past the overlap check (look by eye); user rules: larger dimension text in white space, balloons outside with arrows, GD&T frames, few short notes.
  - Numbering differences between the gate and the drawing table (boss B5/B6) - deliver with drawing numbering.

### Key files (path relative to STAGE\left_thigh_outer_inner)
- project/part 1/REBUILD.md - re-run chain and traps for the outer, Rev A to RIBS5 rounds.
- project/part 1/STATUS_RevC.md, STATUS_RevF.md - finalize recipe, STEP checks, deviation per revision.
- project/part 1/nx/build2.py - staged native NX build (loft + trim, plateaus, bores, bosses); values in nx/params.json.
- project/part 1/nx/finalize.py, finalize_revF.py - export chain, scan removal with history, volume asserts.
- project/part 1/nx/overlay.py - scan as Convergent Body overlay for the manual check.
- project/part 1/an/s10_skin.py, s11_skin2.py, s12_sections.py - B-spline skin fit and loft sections.
- project/part 1/an/s3_parting.py, s4_frame.py, common.py - frame from scan datums, mesh helpers.
- project/part 1/an/hmap2.py, s16_outlines.py, s19_platnx.py, arcfit.py - height map to line/arc plateaus for NX.
- project/part 1/an/dev2.py, report.py, stepcheck.py - two-way zoned deviation, report, STEP validation.
- project/part 1/nx/conn_pad.py, fix_r2.py, fix_r3_rim.py - expression-driven feature rounds appended to a user master.
- project/part 1/nx/dwglib/gdt.py, ptdwg.py - drawing and GD&T helpers.
- project/part 2 - Inner/REBUILD.md - inner chain, registration, long trap list.
- project/part 2 - Inner/STATUS.md - full history including the rejected fix round and restore.
- project/part 2 - Inner/an/i7_register.py, i50_fit.py - registration into the other part's frame, fit check.
- project/part 2 - Inner/an/i90_clusters.py, i97_sim.py, fixlib.py - cluster finder and mesh fix simulation (see blob lesson).
- project/part 2 - Inner/nx/build_inner.py, finalize_revE.py - staged inner build, finalize with history.
- project/part 4 - Assembly/an/fit_check.py, locate_common.py, zstack.py - OCP interference/clearance gate.
- project/part 4 - Assembly/work/revE2/final_gate.txt - final gate verdict and user-edit audit.
- ws/lt_ribs3/j1_add.py - per-feature step() journal with containment checks (best add-feature pattern).
- ws/lt_ribs3/r2/j3_wall.py - G1 wall transition journal.
- ws/lt_inner_r8/j2_r8.py - sketch_prism, g1_sheet, trim_keep helpers.
- ws/lt_inner_revB/j2_unscan.py - replace scan Fit Surfaces and delete the scan.

### Files in package (left_thigh_outer_inner)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## left_thigh_clean_rebuild
- **Purpose / part type:** From-scratch, clean feature-tree rebuilds in NX 2206 of a robot left-thigh pair of moulded/printed shells (outer shell LT-OUT-001, inner shell LT-INN-001, assembly LT-ASM-001; wall 3.1 mm, Al 6061 mass props) from two STL scans. The older "masters" (hand-edited by the user, 91.1 % / 89.5 % of scan area within 0.5 mm) were scan-tracing patchwork (outer: 502 feature rows, 123 cylinders, 95 splines, 60 Replace Face). The task: same fit, but a tree of few real design features (one cylinder per boss, revolve/loft envelope, ribs, patterns), exact mating between the two parts.
  - **Part 5** (v1, "loft fairing"): one shared envelope, scan checked only at the end. Clean, but fit fell to 79.6 % / 76.7 %.
  - **Part 7** (v2): zoned envelope plus every feature measured on the scan and gated per stage by a fresh verifier agent. Result 94.7 % / 94.1 %.
- **Dates:** part 5 2026-10-31 (11:48 to 16:35 session, packaged evening); part 7 2026-10-31 17:05 to 2026-11-01 (package + deviation overlay prts 11-01).
- **Sessions (transcripts/):** `beb3588c-...jsonl` and `3033883f-...jsonl` (part 5, two near-identical logs of the same Oct 31 morning run), `19347876-...jsonl` (short planning session for part 7, 16:53-17:32), `70a6170f-...jsonl` (part 7 orchestrator, 1491 events) plus `70a6170f_subagents/agent-*.jsonl` (28 subagent logs: measurers, inventory analysts, NX builders, fresh verifiers, drafter).
- **Source folders (original paths):** work `C:\NX_MCP_WORKSPACE\lt_clean` (part 5) and `C:\NX_MCP_WORKSPACE\lt_clean2` (part 7), each with `an\` (Python scan analysis), `nx\` (NXOpen journals), `work\` (data). Deliveries in `Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\` and `...\part 7 - Clean Rebuild v2\`. Staged as `ws/lt_clean`, `ws/lt_clean2`, `project/part 5...`, `project/part 7...`.

### Workflow (step by step, reconstructed from scripts + logs)
Part 7 (the version worth copying); part 5 differences noted at the end.
1. **Frame + data loader.** Both scans live in the assembly frame (origin on knee axis at knee floor plane, +Z knee axis, +Y to hip). `an/lib.py` loads a scan, decimates once to 1.5 M triangles with Open3D quadric decimation, caches `npz`; `lib.section(v,f,axis,val)` gives plane-section segments; `lib.tri_data` gives centres, normals, areas (area weights for every statistic).
2. **Zone measurement (parallel measurer agents, `an/m1_* ... m5_*`).** One agent per zone: m1 knee drum (`m1_h_cone.py`, `m1_q_fit.py`: two drafted cones R 68.85 at Z 36.07, draft 1.6 deg, top Z 83.60, bottom -13.90, fit 99.8-100 %), m2 body loft (`m2_g_fit.py`, `m2_loft.py`, 10-station loft, 72 poles), m3 hip end (`m3_*`: shoulder cones, mouth circle R 70.9 at Y 287.39, a real crease at Y 253-268 that part 5 had faired away), m4 joint band (`m4_*`: rim 34.80, tongue 36.05 w 1.6, lip 35.31, rebate 36.08 w 1.85), m5 the +X band (`m5_a..w`): found to be an exterior recessed panel 1.1-1.2 mm deep, Y 54.5-259, boundary an arc in angle about the hip axis. This panel explained most of part 5's loss (its envelope sat on the recess floor, so the wall behind was 1.2 mm too deep).
3. **Baseline zone table** (`z0_baseline_zones.py` / `an/g_gates.py`): where part 5 lost points per zone (exterior, inner wall, 1-2.4 mm band under the envelope, interior features), so the new plan targeted zones, not one number.
4. **Feature inventory** (inventory analysts, `an/i1_*`, `an/i2_*`): `FEATURES_out.json` (57 rows) and `FEATURES_inn.json` (102-103 rows): id, type, parameters, scan mask file, source. Scan masks are triangle-index arrays in `work/masks/<out|inn>_f_<name>.npy`. `an/dt_tighten.py` tightened 51 masks; design table `nx/design2.py` (607 lines) plus `nx/masters2.json`.
5. **Envelope preview in Python first** (`an/s1_*.py`, spec `work/s1/envelope_spec.json`): drum revolve + ONE 26-section loft (periodic B-spline sections, 72 poles) intersected with a shoulder cone, united with the drum; tail wall as a separate sheet (`s1_tail*.py`, `r1_tail*.py`), zebra (`s1_zebra.py`), curvature radius (`s1_curv*.py`), Shell proxy tests (`s1_shell*.py`, OCC cannot shell the union, NX can).
6. **NX base build** `nx/b_base2.py`: masters as expressions (`ltenv.masters`), sketch revolve DRUM, 26 periodic studio splines through poles (`curvekit.studio_spline(poles=True, periodic=True)`), Through Curves BODY_LOFT, cone SHOULDER_CONE, Intersect, Unite, blanked ENVELOPE_REF copy, Shell 3.1 (tolerance 0.2), tail wall `nx/ltail.py` (revolve skin + TAIL_BLOCK).
7. **Split + joint** `nx/p_stageA2.py`: Trim Body at the joint plane per part, tongue/rebate, panel cut (`xpanel_cut`, 17-pt spline boundary, planar run-out).
8. **Feature stages** `nx/p_build3.py` runs named stage functions from `nx/stages2.py` (1593 lines, `STAGES2` dict): 5a knee/hip adds+cuts, 5b bosses/pins/ear/ribs/tabs/pads + `clip` (Intersect with the ENVELOPE_REF copy), 5c mating cuts, holes, hub, side openings, pins, 5d `root_blends` and `seams`. Each stage logs volume, solid count, face census, feature errors into `build_<which>.json`; the part is saved after each batch.
9. **Gate after every stage** (builder numbers, then a FRESH verifier agent with its own measurement, `work/v3..v5e/VERDICT.txt`): `an/g_gates.py <out|inn> cad.stl envelope.stl tag`. At most 3 fix rounds per stage, remaining defects listed as open points.
10. **Finalize + assembly + fit** `nx/finalize_p5d.py` (attributes, helper layer, Rev E/D, STEP AP214/AP242, STL), `nx/P6/build_asm.py` (both parts at origin, no constraints, "designed in place"), `nx/P6/fit_check.py` (OCP on STEP: interference by 40 M random points, coaxial pairs, joint planes).
11. **QA + drawings + package** `an/q7_*.py` (zones, surface, trough slots, joint, STEP validity), drawings by `nx/dwg_out.py / dwg_inn.py / dwg_asm.py` (PDF + DWG), renders, zip (100 files), client draft not sent. P9: `nx/P9/overlay.py` + `an/p9_overlay.py` build CAD + full scan facet-body overlay prts for the user's own hand check.
- Part 5 chain (`ws/lt_clean`): `an/b2_fit.py` (section fit; env LAMK, INSET_TB) -> `an/b3_smooth.py` (longitudinal pole fairing + zebra preview) -> `an/b4_curv.py` (min curvature radius) -> `nx/run_all.ps1` (b_base.py, p_stageA.py, p_build.py + stages.py) -> `nx/run_deliver.ps1` -> `an/d1_dev.py`, `d3_fit.py`.

### NX tools and NXOpen APIs used
- Headless only: `run_journal.ps1` (nx-journal-core skill) launching NXOpen Python journals; 319 run_journal calls in the two main sessions, 2285 plain `python` runs for scan analysis, zero certified NX MCP tools. Journals add `NXH_DIR/NXCK_DIR/NXRE_DIR` to `sys.path` and import helper modules `nxh` (new_part, expr/set_expr, section_feature, volume, bbox, body_ok, feature_errors, examine_geometry, mark/undo_to, subtract, face_census), `nxf` (new_sketch, finish_sketch, revolve, extrude_ex, through_curves, edge_blend, tube, feature_group, sketch constraints), `nxre` (stl_import, stl_export), `nxa` (assembly), `curvekit` (studio_spline by poles, spline_data), plus project modules `ltenv` (masters + datums), `ltint` (sketch/extrude helpers, `main_body`, `envelope_ref`), `stages`, `stages2`.
- Main builders: Sketch + Revolve (drum, knee/hip revolves about knee/hip axis), Studio Spline by poles + Through Curves (envelope), Cone primitive, Boolean Unite/Intersect/Subtract, Trim Body (joint plane), Shell (`CreateShellBuilder`, 10 uses), Thicken (tail wall), Extract Body/Face, Extrude with Boolean+target, Rib-style `ramp_rib` (extrude of a sketched ramp profile), Pattern Feature (bolt circles), Edge Blend with overflow switches, Project Curve (`CreateProjectCurveBuilder`, 20 uses, for panel-line seams) plus Tube (`nxf.tube`) subtract, Offset Region / Divide Face (tongue/rebate in part 5), Datum planes/axes, Expressions as masters.
- Export/measure: STEP AP214/AP242 via `NXOpen.StepCreator`, STL via `nxre.stl_export(chord=0.01)`, mass props at accuracy 0.99 (0.999999 costs minutes), Examine Geometry, `NXOpen.GeometricAnalysis`.
- Python side: numpy, scipy (CubicSpline, sparse least squares), trimesh, Open3D (`RaycastingScene.compute_distance` for unsigned distances; sample_surface), pyvista (offscreen zebra/gloss/overlay renders), shapely, matplotlib (sections), OCP/OpenCascade (STEP read, validity, boolean fit check) in the `cadgenbench` venv.
- Drawings: `nx-drafting` skill libs (`dwglib`), sheets A3/A2, Parts List, tables; NX drops table cells "0.00" (print as "-").

### Accuracy / deviation results
All numbers: area-weighted scan->CAD fraction within 0.5 mm unless stated (`work/gates/*.json`, `QA/REPORT.txt`).
| | outer | inner | source |
|---|---|---|---|
| old hand-edited masters (Rev C / Rev B) | 91.1 | 89.5 | STATUS.md, g_gates `old` column |
| part 5 clean rebuild (Rev D/C) | 79.6 (p50 0.106, 90.8 % <1 mm) | 76.7 (p50 0.113, 88.5 % <1) | part 5 HANDOVER |
| part 7 v2 (Rev E / Rev D) | 94.7 | 94.1 | QA/REPORT.txt (fresh verifier q7) |
- v2 gates: G-ext 97.3/97.7, G-wall 96.1/97.2, G-band 97.2/97.6, G-total pass; G-feat (each interior-feature mask p90 <= 0.5 mm) FAILS: 54/57 outer, 86/103 inner (11 inner fails are sharp variable-radius roots). CAD->scan p90 0.54 / 0.63 mm. Interference 0.0 mm^3 (40 M points), all coaxial pairs 0.00.
- Zone table v2 (old / part 5 / v2, outer): drum 88.5/87.1/97.8, body 91.6/76.1/95.0, hip end 92.4/84.2/91.5 (below old), tail 86.4/81.7/97.9, ribs 90.4/64.2/96.6, roots 52/50/82.
- NX-side overlay check (P9): 400 random scan points to CAD, p50 0.06 / 0.05, p95 0.48 / 0.76 mm.
- STEP validity: outer valid; inner AP242 OCC-invalid (2 hub faces), AP214 valid.
- Part 5 volumes: outer 392 576, inner 347 792 mm^3; v2: 390 880 / 342 907 mm^3 (QA), fit 0.0 mm^3.

### What worked / what failed
- Worked:
  - Per-zone gates + a fresh verifier agent after every build stage: caught CAD-only material that scan->CAD gates cannot see (a post built from a see-through projection, rectangle vs obround stem, filled pad, a CAD-only slot).
  - Zoned envelope (drum revolve + one loft + shoulder cone + tail revolve skin) instead of one loft forced through hidden sections; every feature value measured from its own scan mask, rounded to 0.05 mm / 0.5 deg.
  - Preview every surface in Python (zebra, min curvature radius > 2 x wall) before NX; NX vs preview max difference 0.24 mm, p99 0.084.
  - Stage-function architecture with a log per feature (volume, solid count, face census, errors), undo on failure (`nxh.mark/undo_to`), tools overshoot the skin and one `clip` Intersect trims them to the envelope copy.
  - Edge Blend strategy: one feature per (family, radius), split halves on refusal, check examine-geometry + volume growth against analytic fillet area (`(v1-v0) <= 1.6*expected+40`).
  - Panel-line seams: spline in a far sketch plane, Project Curve along Z onto the skin faces, Tube subtract; re-collect skin faces for each groove (stale faces left gaps).
  - Conflict rule: miss the scan -> fix the feature's type/size/position or add one more clean feature; after 3 tries document as open point (never a blob; see memory re-no-auto-blob-fixes).
- Failed / traps:
  - Part 5: hidden loft sections whose top sat 3 mm below the drum top next to real sections that sat on it produced a fold at the knee-body junction; fix = convex hull of hidden + real data, per-pole fairing across stations with keep-inside-drum constraint, min radius >= 8 mm. Shell fails ("Cannot apply Shell") if the loft's min curvature radius is near the wall. Part 5 also had no recessed +X panel and smoothed away the real hip crease: fit dropped ~12 points.
  - Shell tolerance: 0.05-0.15 silently corrupted the body in v2 (use 0.2); 0.01 makes every later boolean 3-6x slower.
  - Root blends in the hip joint zone (Y>258, Z 30-50) made the two parts overlap 0.5 mm.
  - Fix-round cap of 3 left residues; round 3 itself created the CAD-only trough slots (builder must section-check its own last fix).
  - NX cannot be trusted to keep mask lists consistent: CH_CAP_RING mask was empty; the gate script counts it as a failure.
  - Closed-section solid loft / seam tubes: stale face objects after earlier subtract; B seam gaps traced to that bug.
  - Subagent Write refuses `.md` reports (use `.txt`); only kill run_journal processes whose command line holds your own work folder (several NX sessions shared the licence).
  - NX table text "0.00" printed as "-"; drawing note 'INTERNAL CORNERS R3 MAX' went stale after v2 roots R5/R7.1.
  - Open at delivery: trough-end CAD-only slots (<=8.6 mm deep), 0.3-0.45 mm skin step at y -38, hip end below old master, envelope 1.2 mm proud at hip side (162/219 mm^2).

### Key files (path relative to STAGE\left_thigh_clean_rebuild)
- `project/part 7 - Clean Rebuild v2/PLAN.md` - the v2 plan: user decisions, gate definitions (G-ext, G-wall, G-band, G-feat, G-total, G-surf, G-clean, G-fit), agent roles, rules.
- `project/part 7 - Clean Rebuild v2/STATUS.md` - phase-by-phase log with every verifier verdict and fix round; best narrative of the loop.
- `project/part 5 - Clean Rebuild/PLAN.md` and `HANDOVER.md` - v1 method, exterior-quality rule, re-run chain, traps.
- `ws/lt_clean2/COMMON.md` - brief given to every subagent (frame, data loaders, mask conventions, hard design-intent rule).
- `ws/lt_clean2/an/lib.py` - scan loader/decimator/section/tri_data (area weights); tiny, reusable.
- `ws/lt_clean2/an/g_gates.py` - zone-gate evaluator (scan->CAD area-weighted, per-mask p90, CAD->scan) comparing new vs old vs part 5.
- `ws/lt_clean2/nx/b_base2.py` - NX envelope build from a JSON spec: revolve drum, periodic studio-spline sections by poles, Through Curves, Shell.
- `ws/lt_clean2/nx/stages2.py` - stage functions (ramp_rib, root_blends with split-on-refusal, seams via Project Curve + Tube, bosses, clip).
- `ws/lt_clean2/nx/p_build3.py` - stage runner: stage list -> log JSON -> save -> pure STL export.
- `ws/lt_clean2/nx/ltint.py` - sketch/extrude helpers, main_body / envelope_ref lookup.
- `ws/lt_clean2/nx/ltenv.py`, `design2.py`, `masters2.json` - masters and design table (feature values as data).
- `ws/lt_clean2/nx/finalize_p5d.py` and `nx/P6/build_asm.py`, `nx/P6/fit_check.py` - finalize, assembly in place, OCP fit check.
- `ws/lt_clean2/nx/P9/overlay.py` - CAD + scan facet-body overlay part for hand checking in NX.
- `ws/lt_clean2/work/s1/` (envelope_spec.json) and `FEATURES_out.json`, `FEATURES_inn.json` - spec/inventory formats.
- `ws/lt_clean2/work/v5e/VERDICT.txt`, `work/q7/` (via `QA/REPORT.txt`) - example verifier verdicts.
- `ws/lt_clean/an/b2_fit.py`, `b3_smooth.py`, `b4_curv.py`, `d5_surf.py`, `d1_dev.py`, `d3_fit.py` - part 5 section fit, pole fairing + zebra, curvature radius, two-way deviation, mesh fit.
- `ws/lt_clean/an/a8_drum_fit.py` - drum (cone with draft) fit by least_squares on drum-only directions.
- `ws/lt_clean/nx/ltenv.py`, `stages.py`, `p_stageA.py`, `finalize.py`, `build_asm.py` - part 5 NX modules.
- `project/part 7 - Clean Rebuild v2/.../QA/REPORT.txt` - gate + zone table, open points.
- `project/part 7 - Clean Rebuild v2/.../Deviation_Check/README.md` - how the overlay deliverable is described.

### Files in package (left_thigh_clean_rebuild)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## chest_ch001
- **Purpose / part type:** CH-001, the chest shell of a printed humanoid robot (client Paul Clark job family, same as the left thigh): one large moulded/printed housing, ~333 x 391 x 142 mm, constant wall 3.25 mm, shoulder flanges 4.35, mirror-symmetric about x = 0 with a few one-sided features; shoulder bores D110, front panel with pocket + D63 recess + D37.4 hole, vent pockets with slot patterns, neck U opening with a flange, bottom (hip) joint end with screw bosses, ribs/bosses/tabs/latches inside. Source: one 14.7 M-triangle, 738 MB STL (`share-Chest.stl`).
  - **Part 3** (first RE + deviation check): scan -> native NX "Rev A" (radial-map skin loft + Shell + scan-measured features), then a feature-clean re-do of Rev A, then Rev B/C patches from the user's marks on a scan overlay.
  - **Part 6** (clean rebuild from scratch): new skin fit, stage-by-stage (skin, Shell, interfaces, interior, styling), delivered as Rev B, then Rev C = the user's hand-edited master.
- **Dates:** part 3: 2026-10-29 (first build) to 2026-10-31 (Rev B/C patching, overlay). Part 6: 2026-10-31 evening to 2026-11-02 (Rev B zipped 11-02 morning; Rev C 11-02 21:19, user's file is final).
- **Sessions (transcripts/, assignment inferred from timestamps + first messages):** part 3: `f204f22c-...` (10-29 21:07, first build), `c5865595-...` (10-30 morning), `9c3a8bea-...` (10-30 PM, rounds and lead review), `d432d364-...` (10-30 22:02 to 10-31 11:17, clean rebuild + Rev B), `0ba74d23-...` and `6db96a5a-...` (10-31, overlay/neck/bottom-end fixes and drawing hand-off). Part 6: `d9bb7563-...` (10-31 16:52 to 11-02 20:27, main lead session) and `8330b7d3-...` (same span, handover/companion copy).
- **Source folders (original paths):** `Desktop\Left Thight Reverse Engineer\part 3 - Chest` (an/, nx/, work/, Deviation_Check/, deliver/) and `...\part 6 - Chest Clean Rebuild` (BRIEF/HISTORY/DESIGN_INTENT/PLAN.md); work `C:\NX_MCP_WORKSPACE\ch_clean` (an/, nx/, work/, deliver/, deliver_RevC/). Staged as `project/part 3 - Chest`, `project/part 6 - Chest Clean Rebuild`, `ws/ch_clean`.

### Workflow (step by step, reconstructed from scripts + logs)
Part 3, first RE (Rev A), re-run order in `project/part 3 - Chest/REBUILD.md`:
1. **Load + clean:** `an/s0_load.py` (weld 1e-3 mm, connected components -> main shell, 2 118 crumbs dropped), `an/s1b_quick.py 0.6` (vertex-cluster 0.6 mm copy, 2.5 M faces; quadric decimation of 14.7 M faces took > 25 min).
2. **Symmetry + frame:** `an/s2_symmetry.py` (mirror plane by ICP of the reflected scan: residual p50 0.090, 92.8 % within 0.5 mm), `an/s5_frame.py` (Z = normal of interior mounting-pad plane, X = mirror normal, Y = Z x X; rim plane z = 0), `an/s8_datums.py` (front through-hole, recess, shoulder ring faces + bore circles, rim levels, pad plane via `common.fit_plane_robust / fit_circle_robust`), `an/s8b_rim.py`.
3. **Height maps:** `an/s6_hmap.py` (z seen from +Z = interior, from -Z = exterior, 0.25 mm raster).
4. **Skin:** `an/s10_skin.py` radial map r(p,q) from a centre point above the opening (azimuthal-equidistant p,q; rays cast from outside inward, first hit = exterior; tensor cubic B-spline with robust reweighting, mirror symmetric); `an/s12_sections.py` converts iso-q curves into 82 clamped cubic loft sections.
5. **Segmentation / features from the scan:** `an/s14_raised.py` (heights above inner skin), `s16_*/s17_*` (plateau levels, manually curated ladder of false levels), `s19/s20/s21` (shoulder, neck, panel params -> `nx/params.json`), `s22_through.py` (openings), `s23_holes.py` (hole candidates re-measured by circle fit, paired with mirror, 18 real of 170), `s24_grooves.py` (styling grooves; only the shield line survived), `s25_recesses.py`, `r1_segment.py` (face segmentation by region growing on normals + plane/cylinder fit).
6. **NX Rev A build** `nx/build.py` (835 lines; ~6 min with fast volume): A Through Curves skin -> trim to right half -> Shell (rim, mid-plane and neck faces open, shoulder face alternate thickness) + panel + bottom/notch cuts; F right-half features; M Mirror Geometry + Unite; G one-sided. Then `nx/finalize.py` (STEP AP214/242, x_t, STL, ref set), QA `an/dev2.py`, `an/stepcheck.py`, `an/report.py`, drawings `nx/dwg_chest.py` + `dwg_annot.py`, `an/make_zip.py`.
7. **Clean re-do of Rev A (10-30):** user rejected rounds 2-4 (stepped pads, terraces, traced plateau outlines, "lego"); `CLEAN_PLAN.md` + `work/clean/make_spec.py -> features.json` -> `nx/build_clean.py` + `clean_feat.py` (91 features, 762 faces, ribs t1.5 with flat tops, drafted cones for bosses, pocket + constant wall, Pattern Feature slots 8 x 5.4 / 15 x 5.2, Mirror).
8. **Deviation overlay for the user:** `an/ov_probe.py` + `nx/overlay.py` make `CH-001_Chest_vs_SCAN.prt` (CAD + scan as one convergent facet body, layer 10, orange 50 %). User marks missing features; Rev B features by `nx/revB_feat.py` (tab notches, rim lip, side pad + rib, boss lobe + pin; spec from `an/r1_prep.py`, measured with `an/r1_sec.py`, `r1_crops.py`, `r1_relief.py`, `r1_clusters.py`). Then `revB2_end.py`, `revB3_post.py`, `revB4_neck.py`, ... `revC1_neck.py`, `revC2_end.py` appended on the user's hand-edited master (`inspect_user.py` lists the user's Replace Face / Delete Face / Offset Region / Chamfer edits).
Part 6, clean rebuild (`ws/ch_clean`, plan in `project/part 6.../PLAN.md`):
9. **Stage 1 skin (exterior first):** `an/c3_ext.py` (exterior points + normals), `c7_crease.py` (groove/crease lines), `chlib.py` (plain-skin masks, stations, B-spline basis), `f1h_fit.py` (linear polar model r(y,theta) with cardinal-spline weights across 38-40 stations, mirror-symmetric radial control values, Cauchy robust weights, 2nd/3rd difference penalties, pseudo targets for rim extension and neck gap bowl) -> `f2_eval.py` (vs scan and vs old skin), `f3_surf.py` (zebra, gloss, curvature), `f4_secs.py`, `f10_areas.py`, `export_sections.py` -> `sections_F_fair2.json`. NX: `nx/ch_s1a.py` (38 studio splines by exact poles + ONE Through Curves, Preserve Shape ON), `ch_s1b.py` (4 Trim Body by plane + neck U extrude along rule direction D), `chneck.py` (DOF-0 neck sketch with named expressions), `ch_s1c_shell.py` (Shell feasibility), `ch_s1d_grid.py` (NX face evaluated on grid for zebra).
10. **Stage 2-3:** Shell 3.25 (`ch_s2.py`), `ch_s3a.py` (shoulder bores D110, notch, rim lip from Project Curve + thin extrude, rim band), `ch_s3b.py` (neck flange plate = extract of neck-cut face trimmed by a cylinder, Thicken 3.5, outer R10/inner R5 blends, sill+ledge one profile, pads, bottom end band + socket, teardrop boss+web in ONE sketch with one Draft, bores), `ch_s3c.py` (hook lip, barb rib, clip tab, latches, cup).
11. **Stage 4-5:** interior (`make_s4.py` / `make_s5.py` generate `ch_s4.py`, `ch_s5a.py`, `ch_s5b.py` from `*_body.txt` tables of ribs/bosses; pockets, slot Patterns, panel, front hole cut LAST so interior tools cannot refill voids). Stage 6 pre-cleanup (`S6pre`): neck tools clipped by an inset envelope copy `ENVELOPE_REF_NECK`, sliver reduction 90 -> 45 small faces (`an/s6_small.py`, `_rules.json`), then styling (shield V groove, triangular side recesses).
12. **QA/finalize:** `an/m9_zones.py` zone deviation (shoulders/rim/bottom/neck/skin/interior), `an/s6_qa_all.sh`, `s6_stepcheck.py` (OCP validity + volume), `s6_devmap.py`, `nx/ch_finalize.py`, drawings `nx/dwg_ch*.py`. Rev C: user hand-edits (Replace Face, Offset Face recesses via Project Curve > Divide Face > Offset Face) are the master; `nx/run_c_final.ps1`, `ch_finalize_c.py`.

### NX tools and NXOpen APIs used
- Same pattern as the thigh job: headless NXOpen Python journals via `run_journal.ps1` (685 calls in the chest sessions, 2550 plain python runs), helper modules `nxh`, `nxf`, `nxre`, `curvekit` (studio spline by poles); `chenv.py` holds masters; no certified NX MCP tools were used (tool stats: Bash/Read/PowerShell/Write/Edit/Agent only).
- APIs seen: `CreateThroughCurvesBuilder` (20 uses), `CreateExtrudeBuilder`, `CreateShellBuilder`, `CreateProjectCurveBuilder` (AlongVector), `CreateExtractFaceBuilder`, `CreateConeBuilder` (DiametersAndHeight), `CreateFaceBlendBuilder`, `CreateUntrimBuilder`, `DatumPlane` / `DatumAxis`, `Section.AllowTypes.OnlyCurves`, `Expression` objects, `NXOpen.Step` (AP214/AP242 export), Drawings (`DetailViewBuilder`, `DraftingDatumFeatureSymbolBuilder` for GD&T), `UF` session. Features used in journals: Trim Body by plane, Mirror Geometry/Mirror Feature, Pattern Feature, Draft, Thicken of trimmed sheets, Offset Region (inset envelope copy), Edge Blend, Subtract/Unite/Intersect with ENVELOPE_REF clip.
- Python side: numpy/scipy sparse least squares for the skin fit, Open3D RaycastingScene for distances and ray casting, pyvista renders (zebra, CAD-vs-scan crop views with `CROP_SPLIT`), shapely masks, OCP for STEP checks, matplotlib section overlays (`r2_secs.py`: scan orange vs CAD grey, any plane `x=`,`y=`,`z=`,`n=...@...`).

### Accuracy / deviation results
(scan->CAD fraction within 0.5 mm, area-weighted; Rev A numbers from `deliver/Deviation Analysis/REPORT_deviation.md`, part 6 from `PLAN.md`)
| build | whole | skin | interior | neck | bottom | other |
|---|---|---|---|---|---|---|
| Rev A first build (patch-heavy) | 71.8 | 92.9 | 58.7 | - | - | rim 57.3, shoulders 80.8 |
| Rev A clean (outD4, 762 faces) | 74.4 (p50 0.108, p95 2.11 mm) | 93.1 | 62.5 | 67.5 | 63.3 | rim 70.5, shoulders 79.3 |
| Rev B overlay patch r1b | 78.0 | - | interior >1 mm 17.2 % (was 24.8) | | | |
| part 6 Rev B (S6_2, 747 faces) | 75.8 | 91.1 | 69.2 | 63.5 | 81.6 | rim 76.4, shoulders 84.6 |
| part 6 Rev C (user master, 779 faces) | 76.0 | 91.1 | 69.5 | 63.5 | 80.9 | rim 76.7, shoulders 84.7 |
- Skin fit alone (stage 1): p50 0.099-0.103, 94.3-94.4 % < 0.5, 98.8 % < 1 vs old radial skin 92.3 / 97.7; symmetric bound 96.5 % because the scan has ~1 mm print warp on the lower flanks (a symmetric CAD cannot follow it); whole-loft min radius 10-19 mm; Shell trial wall 3.239-3.278.
- NX vs Python preview of the skin: max 0.24 mm. CAD->scan (Rev A): p50 0.116, p90 1.67 mm.
- STEP: OCC reads AP214 + AP242 as valid (volume within 0.006 %); NX re-import of AP242 works, AP214 gives "nothing imported" (3x) -> ship AP242. Rev A volume 593 405 mm^3, Rev B 626 315, Rev C 625 842.
- Neck zone stayed below Rev A (63.5 vs 67.5): 47 % of failed neck points sit in the shoulder-vent box where even the plain outer skin is 43 %: a stage-1 loft issue, not a feature error. Lead accepted.

### What worked / what failed
- Worked:
  - Exterior first: fit sections to plain-skin exterior points only, pole fairing, zebra + curvature preview in Python, loft once in NX, then Shell. Beat the old skin with margin.
  - Stage-by-stage chain with a per-stage log (faces, small faces, Examine, volume), a rollback of failed stages (`stage_failed`), and values kept in `*_body.txt` tables so journals are generated, not hand-edited.
  - Fast volume (accuracy 0.99): the 5-hour runs of Rev A were volume measurements, not modelling; full A..G build then ran in 6 min.
  - Neck opening modelled as ONE ruled flange round the U with bend blends, bottom end as a thickened joint flange + boss/web in one sketch + one Draft (instead of five rounds of patches).
  - Zone deviation as regression guard (never as target): any feature that makes its zone worse than Rev A is placed/sized wrong.
  - Scan overlay prt (CAD + facet body) as the way the user marks missing features; hand edits by the user are treated as the master and re-measured, not overwritten.
  - Cutting voids/bores last; clip interior tools by an inset envelope copy so they leave no edge lines on the outside.
- Failed / traps:
  - Radial-map skin extrapolates where the scan has no data: 22 mm past the real bottom edge, 1-3 mm bulge at neck arms; always compare CAD bbox with scan bbox (NX bbox of B-surface bodies is padded up to 23 mm; use STL bbox).
  - User rejected stepped pads/terraces/cluster outlines ("lego"), then neck U and bottom end patched 5x ("paramparca"): patches on patches produce slivers, 0.05-0.3 mm steps, internal voids, knife edges.
  - `nxf.trim_body` keep_point is a bbox test (wrong for bowls): decide sides by volume. Trim of an analytic offset inner skin failed; Shell worked first time. Shell face sort by area failed; sort by type/normal/bbox (UF face data has no point for extruded faces).
  - Loft with curvature near the wall -> "Cannot apply Shell"; Thicken of a large B-surface 10-15 mm fails on concave areas; Subtract of a block coplanar with the rim -> touch condition; separate tool bodies sometimes refused by Unite (give the extrude its own Unite).
  - Edge Blend of a crease made of several edges against small faces fails; Offset Face/Region lift of the lower inner skin fails > 0.2 mm; Face Blend refused rib/wall pair; cross-rib blend works only right after its own unite.
  - Styling in stage 5 (shield V groove, triangular side recesses) was silently never built; only the scan->CAD colour map of the whole outside revealed it. Review the whole outer colour map before packaging.
  - Closed deep bores read as filled in the scan (scanner closes them): not a CAD error. Boss-hole candidates from plateau fill are mostly noise (170 -> 18 real).
  - `python - <<EOF` / stdin scripts hang the shell: every script is a file. `-JA a,b,c` is split at commas.
  - Open at delivery: 1.3 mm cosmetic step at the neck receiver cup (fix idea: neck blend flange_Ro 10 -> 5-6, ~3 h re-run), 23 slivers, interior only ~69.5 %, centre logo bulge not modelled.

### Key files (path relative to STAGE\chest_ch001)
- `project/part 3 - Chest/REBUILD.md` - re-run chain of the first RE, all traps (best single doc for the first RE).
- `project/part 3 - Chest/CLEAN_PLAN.md` - modeling-strategy plan with masters, datums, feature table (values), budget, "left out on purpose".
- `project/part 3 - Chest/deliver/Deviation Analysis/REPORT_deviation.md` - zone deviation table format and "where the remaining deviation is".
- `project/part 3 - Chest/an/common.py` - scan loader, plane section, robust plane/circle fits.
- `project/part 3 - Chest/an/s10_skin.py`, `s12_sections.py` - radial-map skin fit and loft sections (the version with the extrapolation trap).
- `project/part 3 - Chest/an/dev2.py` - two-way zoned deviation with maps.
- `project/part 3 - Chest/an/r1_segment.py`, `s23_holes.py`, `s24_grooves.py`, `s5_frame.py`, `s8_datums.py` - segmentation, hole re-measure, groove extraction, framing from functional features, datum fits.
- `project/part 3 - Chest/an/r2_secs.py`, `r1_cadmap.py`, `r1_crops.py` - scan-vs-CAD sections and CAD-coloured-by-distance renders.
- `project/part 3 - Chest/nx/build.py` - Rev A NX build (stages A, F, M, G); `build_clean.py` + `clean_feat.py` - spec-driven clean version.
- `project/part 3 - Chest/nx/overlay.py` - CAD + scan facet-body overlay part.
- `project/part 3 - Chest/nx/revB_feat.py`, `revB3_post.py`, `revC1_neck.py` - example "append features to a user-edited master" journals.
- `project/part 6 - Chest Clean Rebuild/HISTORY.md` - timeline, root causes, traps; `BRIEF.md` - the method and rules handed to the new session; `DESIGN_INTENT.md` - measured value list; `PLAN.md` - decision log per stage with numbers.
- `ws/ch_clean/an/README.md` and `ws/ch_clean/nx/README.md` - stage-by-stage chain and traps of the clean rebuild.
- `ws/ch_clean/an/f1h_fit.py`, `chlib.py`, `f2_eval.py`, `f3_surf.py`, `export_sections.py` - skin fit model, preview, evaluation, zebra/curvature, pole export.
- `ws/ch_clean/an/m9_zones.py` - zone deviation tool with exclusive zone definitions; `s6_stepcheck.py` - OCP STEP validity.
- `ws/ch_clean/nx/ch_s1a.py`, `ch_s1b.py`, `chneck.py`, `chenv.py` - skin loft, trims, DOF-0 neck sketch with expression-driven dimensions.
- `ws/ch_clean/nx/ch_s3b.py`, `ch_s3c.py`, `make_s4.py`, `make_s5.py`, `s5a_body.txt` - interface/interior stages generated from body tables.
- `ws/ch_clean/nx/run_s6_all.ps1`, `run_c_final.ps1` - chain runners (`-Tag`, `-From stage`).

### Files in package (chest_ch001)
Full list: Appendix A. Large / over-budget final+input CAD: Appendix B.

## Reusable for build123d skills

These patterns came out of the NX projects above and do not depend on NX. Most of the analysis code is plain Python (numpy / scipy / trimesh / open3d / OCP) and can be ported as it is. The paths are relative to the zip root.

### 1. Measure outside the CAD kernel, on a datum-aligned scan
- **The loop that worked in every project:**
  1. Align the scan to fitted datums.
  2. Cut stacked sections.
  3. Fit lines, arcs and primitives to them.
  4. Turn the fits into a parameter table (design intent, rounded within the noise band).
  5. Build the CAD.
  6. Export STL/STEP.
  7. Overlay the CAD on scan sections and run a signed deviation.
  8. Adjust the parameter table and repeat.
- **Scripts:** `dreame_bottom_cover/work/an/{sec.py, zones.py, pw.py, fit.py, ovl.py, dev.py}` and `r385_pump/work/parts/B_common/rb.py` (primitive fits).
- **Intent from residuals:** choose the feature type from the fit residuals. Example: a revolve-axis search rejected a revolve for the bowl in the Dreame cover, so it became a loft. Every scan-derived value is stored as a named parameter, with a comment giving the measured value and its source.

### 2. Datum selection
- Pick datums from functional features, not support surfaces:
  - Parting plane → Z.
  - Main bore axis → origin.
  - Second bore or ring axis projected into the plane → Y.

  Examples: Left Thigh (`left_thigh_outer_inner`), the Lexus clip (re-framed on the upright, not the table plane), R385 (axis from the mode of the area-weighted normals, `s1_census.py`).
- **Mating parts:** register the second scan into the first frame with fiducials (boss and pin axes; 13 pairs, RMS 0.041 mm on the Left Thigh). Validate on held-out pairs.
- **Symmetric parts:**
  - Run a multi-start ICP, for example 36 clocking starts (Dreame brush), and state the symmetry ambiguity.
  - Two-sided scans of symmetric parts can be merged a symmetry step apart (R385 valve plate, 90°). Check for this before measuring.

### 3. Feature recognition recipes
- **Profiles from sections:**
  - Piecewise line/arc fits (`pw.py`).
  - A chain of lines and tangent fillets fitted with `least_squares(soft_l1)` on a point-to-polyline residual (`lexus_seat_clip/.../chain.py, fitchain.py, geo2.py`).
- **Twisted or helical parts:** estimate the twist per z slab by circular cross-correlation of r(θ), un-twist the points and pool them into one sharp section (`dreame_brush_core/work/an/m2_twist.py`). The build123d equivalent is a twisted extrude or a helical sweep.
- **Flat features (plateaus, pockets, windows):** make a 0.2 mm height map from the open side and split it into line/arc outlines (`left_thigh_outer_inner/.../hmap2.py, s16_outlines.py`). A depth-diff map finds missed plateaus.
- **Freeform skins:**
  1. Fit station sections to plain-exterior scan points only.
  2. Fair the poles across stations.
  3. Check zebra stripes and the minimum curvature radius in Python before lofting (`chest_ch001/ws/ch_clean/an/f1h_fit.py, f3_surf.py`; `left_thigh_clean_rebuild/ws/lt_clean/an/b3_smooth.py, b4_curv.py`; tensor B-spline r(y,θ) in `left_thigh_outer_inner/.../s10_skin.py, s12_sections.py`).

  Never extrapolate a skin past the real edges. A curvature radius near the wall thickness makes Shell fail.
- **Known scan artefacts to budget for:**
  - Wires and O-rings scan 0.07–0.11 mm too thick.
  - Interior corners get filled.
  - Cylinders with less than 180° of coverage drift in centre.
  - Single-sheet regions need masks.

### 4. Deviation-analysis loop and gates
- **Core metric:** signed, area-weighted, two-way distances with Open3D `RaycastingScene` against a decimated scan, with an npz cache (`left_thigh_clean_rebuild/ws/lt_clean2/an/lib.py`). Report p50/p95/max and the "% of area within ±band" per named zone, plus CAD-to-scan coverage. CAD-only material shows phantom features.
- **Zone and feature-mask gates after every stage:** see `g_gates.py` and `m9_zones.py`. The thigh clean rebuild that was only checked at the end fell from 91.1/89.5 % to 79.6/76.7 % within 0.5 mm. Staged gates plus a fresh verifier agent after each stage reached 94.7/94.1 %.
- **Pose-vs-shape test:** a rigid refit of a part subset, plus a second, independent registration (R385 `dev.py`). It tells misalignment apart from a modelling error. On the R385 pump, three low scores were rigid offsets, not model errors.
- **Masked plus unmasked reporting:** report both rows. For the Dreame cover, masked p95 was 0.595 mm and unmasked 1.04 mm. Measure noise per feature and set the band from it, never just loosen the band.
- **Check the exported STEP independently of the kernel:** volume and wall thickness. OCC's default volume was 0.3 % off on a thin twisted body.
- **Review the whole colour map before delivery.** The chest's styling features were silently never built, and only the full map showed it.

### 5. Build discipline (maps directly to build123d)
- **Named parameters:**
  - Each feature is a named stage function driven by a data table (`stages2.py`, `design2.py`, `masters2.json`).
  - Every sketch is fully constrained from a vertex/arc chain (`dreame_bottom_cover/work/nxlib/ps.py`):
    - an arc is drawn through its end points, and the centre only picks the side;
    - a 180° arc is split at its apex;
    - coincidences are not inferred.
- **Checks after every feature:** volume delta, solid count, face census and point containment. Roll back on failure. Try both directions and keep the one with the expected volume sign (dustbin inlet, `left_thigh_outer_inner/ws/lt_ribs3/j1_add.py` `step()` helper).
- **Feature order:**
  1. Clip tools against an envelope copy so they never overshoot the skin.
  2. Cut voids and bores last.
  3. Apply fillets per (family, radius). Split a refused set in halves, and accept it only if the volume change matches the analytic fillet area.
- **Mating-part fit gate in OCP, independent of the modeller:** `left_thigh_outer_inner/project/part 4 - Assembly/an/fit_check.py`. It does a boolean common, pairs coaxial cylinders, compares joint planes and builds a signed gap map.
- **Multi-part assemblies:**
  - One control document holds the frame, interfaces and master parameters, and only one writer edits it.
  - Changes come in as numbered change-request files.
  - The same rebuild chain re-runs after each revision (R385 / Ulka; NX did this with a control part plus interpart expressions).

### 6. Policy lessons from the user
- Do not auto-fix deviation clusters with irregular pads that trace the cluster outline. The numbers improved (87.5 → 91.5 %), but the user rejected the result ("mud stains"). Fix a miss by changing a real feature's type, size or position. After 3 rounds, report it as an open point.
- The user's hand-edited file is the master. A later revision adds features to that file and re-measures; it does not rebuild from scratch.
- A clean rebuild must keep or beat the old scan fit. Gate it per stage, not only at the end.

### 7. How the agent drove NX (for comparison with a build123d agent)
- **Tooling:** Claude Code wrote NXOpen Python journals and ran them headless with `run_journal.exe`. Each journal printed a JSON log, which the agent read back. The certified NX MCP tools were almost never used for reverse engineering. Hundreds of `run_journal` launches appear per large project (`_meta/tool_stats.json`).
- **Helpers:** `_harness/skills/nx-journal-core/scripts/{nxh,nxf,nxa}.py`, `_harness/skills/nx-reverse-engineering/scripts/nxre.py` and `_harness/skills/nx-curves-and-sketches/scripts/curvekit.py`.
- **Native NX RE features** (Fit Surface, Replace Face) were used on the freeform shells. On the pumps the agent used numpy measurement plus sketch/revolve/pattern rebuilds.
- **Negative example:** the in-NX `nxre` pilot on `r385_pump/ep5_hs03` ended at 3.4 mm RMS with 5 leftover solids. Measuring outside the kernel with a strict parameter table did better.

## Appendix A: file list per project (one line per file: path in zip, size, source date)

### _harness (nx_re_projects_20261105_part1.zip)
```
_harness/addin/NX-KESINTISI-2026-09-21.md  2 KB  2026-09-24
_harness/addin/NxMcpGuiBridge.cs  104 KB  2026-09-24
_harness/addin/rollback-63d33d1/NxMcpGuiBridge.cs  87 KB  2026-09-24
_harness/mcp-repo/.github/workflows/ci.yml  5 KB  2026-09-18
_harness/mcp-repo/.github/workflows/real-nx.yml  5 KB  2026-09-18
_harness/mcp-repo/.github/workflows/star-history.yml  1 KB  2026-09-18
_harness/mcp-repo/.mcp.json  0 KB  2026-09-18
_harness/mcp-repo/.pre-commit-config.yaml  1 KB  2026-09-18
_harness/mcp-repo/CLAUDE.md  2 KB  2026-09-18
_harness/mcp-repo/README.md  10 KB  2026-09-18
_harness/mcp-repo/docs/architecture.md  5 KB  2026-09-18
_harness/mcp-repo/docs/gui-bridge.md  6 KB  2026-09-18
_harness/mcp-repo/docs/migration-0.2.md  3 KB  2026-09-18
_harness/mcp-repo/docs/migration-mcp-sdk-2.md  5 KB  2026-09-18
_harness/mcp-repo/docs/real-nx-validation.md  8 KB  2026-09-18
_harness/mcp-repo/docs/usd-validation.md  7 KB  2026-09-18
_harness/mcp-repo/examples/assembly_demo.py  1 KB  2026-09-18
_harness/mcp-repo/examples/create_block.py  1 KB  2026-09-18
_harness/mcp-repo/examples/nx_main_thread_probe.py  1 KB  2026-09-18
_harness/mcp-repo/examples/nx_runtime_probe.py  1 KB  2026-09-18
_harness/mcp-repo/examples/nx_sketch_api_probe.py  3 KB  2026-09-18
_harness/mcp-repo/examples/start_nx_bridge.py  1 KB  2026-09-18
_harness/mcp-repo/examples/stop_nx_bridge.py  0 KB  2026-09-18
_harness/mcp-repo/examples/validate_step_to_usd.py  9 KB  2026-09-18
_harness/mcp-repo/nx_gui_bridge/NxMcpGuiBridge.cs  85 KB  2026-09-18
_harness/mcp-repo/nx_gui_bridge/build.ps1  1 KB  2026-09-18
_harness/mcp-repo/pyproject.toml  2 KB  2026-09-18
_harness/mcp-repo/skills/nx-modeling/SKILL.md  5 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/__init__.py  0 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/bridge.py  24 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/certified.py  7 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/contracts.py  2 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/experimental.py  6 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/journal/__init__.py  0 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/nx_bridge.py  25 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/nx_session.py  3 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/real_smoke.py  7 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/response.py  2 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/runtime.py  2 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/server.py  2 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/__init__.py  0 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/assembly.py  10 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/drawing.py  12 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/feature_tree.py  5 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/file_ops.py  11 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/measure.py  7 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/modeling.py  22 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/registry.py  2 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/sketch.py  13 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/tools/utility.py  8 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/utils/__init__.py  0 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/utils/geometry.py  1 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/utils/selection.py  2 KB  2026-09-18
_harness/mcp-repo/src/nx_mcp/workspace.py  1 KB  2026-09-18
_harness/mcp-repo/tests/__init__.py  0 KB  2026-09-18
_harness/mcp-repo/tests/conftest.py  3 KB  2026-09-18
_harness/mcp-repo/tests/test_bridge.py  5 KB  2026-09-18
_harness/mcp-repo/tests/test_bridge_import.py  1 KB  2026-09-18
_harness/mcp-repo/tests/test_bridge_safety.py  10 KB  2026-09-18
_harness/mcp-repo/tests/test_certified_server.py  6 KB  2026-09-18
_harness/mcp-repo/tests/test_mcp_v2.py  4 KB  2026-09-18
_harness/mcp-repo/tests/test_nx_executor.py  21 KB  2026-09-18
_harness/mcp-repo/tests/test_nx_safety.py  8 KB  2026-09-18
_harness/mcp-repo/tests/test_nx_session.py  2 KB  2026-09-18
_harness/mcp-repo/tests/test_object_registry.py  2 KB  2026-09-18
_harness/mcp-repo/tests/test_real_nx.py  4 KB  2026-09-18
_harness/mcp-repo/tests/test_real_nx_restart.py  3 KB  2026-09-18
_harness/mcp-repo/tests/test_real_smoke.py  5 KB  2026-09-18
_harness/mcp-repo/tests/test_registry.py  1 KB  2026-09-18
_harness/mcp-repo/tests/test_response.py  1 KB  2026-09-18
_harness/mcp-repo/tests/test_server.py  4 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_assembly.py  10 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_drawing.py  13 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_feature_tree.py  9 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_file_ops.py  10 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_measure.py  10 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_modeling.py  17 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_sketch.py  13 KB  2026-09-18
_harness/mcp-repo/tests/test_tools/test_utility.py  12 KB  2026-09-18
_harness/mcp-repo/tests/test_usd_validation.py  12 KB  2026-09-18
_harness/mcp-repo/tests/test_usd_validation_runtime.py  5 KB  2026-09-18
_harness/mcp-repo/tests/test_workspace.py  2 KB  2026-09-18
_harness/skills/nx-curves-and-sketches/SKILL.md  52 KB  2026-10-07
_harness/skills/nx-curves-and-sketches/references/course-notes.md  14 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/references/nxopen-recipes.md  105 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/references/user-practice.md  12 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/cast_curve_checks.py  56 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/course_checks.py  36 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/curve_activities.py  20 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/curve_features.py  26 KB  2026-10-04
_harness/skills/nx-curves-and-sketches/scripts/curvekit.py  15 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/datum_recipes.py  17 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/inclined_port.py  17 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/law_curve_gear.py  17 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/offset_checks.py  33 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/round3_checks.py  48 KB  2026-10-04
_harness/skills/nx-curves-and-sketches/scripts/sketch_recipes.py  23 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/sketch_rules.py  44 KB  2026-10-06
_harness/skills/nx-curves-and-sketches/scripts/spline_rules.py  32 KB  2026-10-06
_harness/skills/nx-journal-core/SKILL.md  27 KB  2026-10-07
_harness/skills/nx-journal-core/references/existing-parts.md  27 KB  2026-10-07
_harness/skills/nx-journal-core/references/expressions-and-update.md  12 KB  2026-10-06
_harness/skills/nx-journal-core/references/import-export.md  6 KB  2026-10-04
_harness/skills/nx-journal-core/references/nxf-helpers.md  49 KB  2026-10-07
_harness/skills/nx-journal-core/references/skill-set-overview.md  6 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/dump_part.py  18 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/edit_in_the_middle.py  15 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/inspect_part.py  15 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/nxa.py  34 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/nxa_selftest.py  40 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/nxf.py  173 KB  2026-10-07
_harness/skills/nx-journal-core/scripts/nxf_selftest.py  153 KB  2026-10-07
_harness/skills/nx-journal-core/scripts/nxh.py  68 KB  2026-10-07
_harness/skills/nx-journal-core/scripts/nxh_selftest.py  22 KB  2026-10-07
_harness/skills/nx-journal-core/scripts/prt_text.py  59 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/prt_text_selftest.py  10 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/run_all_examples.ps1  3 KB  2026-10-06
_harness/skills/nx-journal-core/scripts/run_journal.ps1  3 KB  2026-10-06
_harness/skills/nx-modeling-strategy/SKILL.md  38 KB  2026-10-06
_harness/skills/nx-modeling-strategy/examples/README.md  5 KB  2026-10-06
_harness/skills/nx-modeling-strategy/examples/battery_dock_and_scan_rebuild/a_build.py  32 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/battery_dock_and_scan_rebuild/a_reopen.py  7 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/battery_dock_and_scan_rebuild/b_probe.py  11 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/battery_dock_and_scan_rebuild/b_rebuild.py  17 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/enclosure_half_and_knob/acc_lib.py  16 KB  2026-10-06
_harness/skills/nx-modeling-strategy/examples/enclosure_half_and_knob/part1_enclosure.py  23 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/enclosure_half_and_knob/part2_knob.py  11 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/extend_existing_parts/edits.py  26 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/extend_existing_parts/stepcheck.py  2 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/imported_bracket_and_surfaced_grip/a1_census.py  5 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/imported_bracket_and_surfaced_grip/a2_build.py  16 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/imported_bracket_and_surfaced_grip/a2_plan.txt  2 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/imported_bracket_and_surfaced_grip/b1_build.py  32 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/topdown_enclosure_around_pcb/PLAN.md  3 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/topdown_enclosure_around_pcb/acc3_lib.py  9 KB  2026-10-04
_harness/skills/nx-modeling-strategy/examples/topdown_enclosure_around_pcb/build.py  38 KB  2026-10-04
_harness/skills/nx-modeling-strategy/references/cast-project-plans.md  7 KB  2026-10-06
_harness/skills/nx-modeling-strategy/references/course-method.md  11 KB  2026-10-04
_harness/skills/nx-modeling-strategy/references/user-practice-overview.md  7 KB  2026-10-06
_harness/skills/nx-reverse-engineering/SKILL.md  22 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/README.md  10 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/REPORT.md  8 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/common.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/dev.py  6 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/fit.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_beam.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_bowl.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_bowl2.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_bowl3.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_bowl4.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_bowl5.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_bowl6.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_bowl7.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_deck.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_deck2.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_deck3.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_grille.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_grille2.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_hook.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_hook2.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_rail.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/m_rail2.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/overview.py  3 KB  2026-10-07
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/ovl.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/pw.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/render.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/sec.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/shade.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/zones.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/analysis/ztable.py  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/figures/overlay_plan_sections.png  244 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/figures/overlay_y_sections.png  283 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/figures/render_iso_bowl_end_cad.png  228 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/figures/render_iso_top_cad.png  252 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/figures/render_iso_underside_cad.png  226 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/figures/render_iso_underside_rail_cad.png  220 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/build.py  26 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/nxlib/geo.py  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/nxlib/ps.py  14 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/nxlib/st_c.py  16 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/nxlib/st_d.py  11 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/probe1.py  3 KB  2026-10-07
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/probe2.py  3 KB  2026-10-07
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/review.py  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/journal/run.ps1  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/qa/build_checks.json  24 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/qa/deviation_dewarped.json  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/qa/deviation_raw.json  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/qa/masters.json  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/qa/review_part.json  0 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_bottom_cover/qa/warp_field.json  0 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/README.md  8 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/REPORT.md  19 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/b0_baseline.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/b1_bristle_first.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/b2_base_first.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/b3_compare.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/common.py  6 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/dev.py  7 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/dev_c2s.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/dev_outliers.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/dev_under_icp.py  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m1_align.py  7 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m2_twist.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m3_profile.py  7 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m3_small.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m3_vgroove.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m3_zoom.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m4_base.py  7 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m5_top.py  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m6_tufts.py  6 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m6_tufts_view.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m7_base_align.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m7_hex.py  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m7_recentre.py  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m7_underside.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/m8_misc.py  7 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/ovl.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/render.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/scans_datum.py  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/stlstat.py  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/analysis/view.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/01_referans_ve_killi_tarama_farkli_cekirdek.png  172 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/04_render_tahrik_ucu_cad.png  292 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/05_render_alt_yuz_cad.png  179 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/06_render_rulman_ucu_cad.png  191 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/09_kesit_bindirme_z.png  196 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/10_kesit_bindirme_yari_kesit.png  92 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/11_olcum_acilmis_cekirdek_kesiti.png  257 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/figures/12_olcum_kil_demetleri_acilim.png  291 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/build.py  42 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/export_ref.py  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/nxlib/ps.py  14 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/probe1.py  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/probe2.py  7 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/probe3.py  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/probe_ref.py  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/review.py  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/run.ps1  0 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/journal/show.py  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/T_base.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/T_base_icp.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/T_bristles.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/b0_baseline.json  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/build_checks.json  62 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/dev_final.json  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/dev_final_cad_to_scan.json  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/dev_final_outliers.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/dev_final_underside_icp.json  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/export_a.json  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/export_b.json  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m1_align.json  8 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m2_twist.json  3 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m3_profile.json  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m4_base.json  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m5_top.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m6_tufts.json  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m7_base_align.json  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m7_hex.json  4 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m7_recentre.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m7_underside.json  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/m8_misc.json  2 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/masters.json  8 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/probe1.json  7 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/probe2.json  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/probe3.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/probe_a.json  111 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/prt_text_ref_a.json  9 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/prt_text_ref_b.json  8 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/ref_a_asfound.json  35 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/ref_a_asfound.txt  5 KB  2026-10-08
_harness/skills/nx-reverse-engineering/examples/dreame_brush_core_with_bristles/qa/review.json  1 KB  2026-10-08
_harness/skills/nx-reverse-engineering/references/nxopen-recipes.md  28 KB  2026-10-04
_harness/skills/nx-reverse-engineering/references/user-practice.md  12 KB  2026-10-04
_harness/skills/nx-reverse-engineering/scripts/nxre.py  46 KB  2026-10-04
_harness/skills/nx-reverse-engineering/scripts/re_fit_surfaces.py  16 KB  2026-10-04
_harness/skills/nx-reverse-engineering/scripts/re_rebuild_compare.py  15 KB  2026-10-04
_harness/skills/nx-reverse-engineering/scripts/re_sections_fitcurve.py  12 KB  2026-10-04
_harness/skills/nx-reverse-engineering/scripts/re_unknown_part.py  13 KB  2026-10-04
_harness/skills/nx-surface-modeling/SKILL.md  43 KB  2026-10-06
_harness/skills/nx-surface-modeling/references/blades.md  18 KB  2026-10-06
_harness/skills/nx-surface-modeling/references/course-notes.md  12 KB  2026-10-06
_harness/skills/nx-surface-modeling/references/nxopen-recipes.md  79 KB  2026-10-06
_harness/skills/nx-surface-modeling/references/option-semantics.md  33 KB  2026-10-06
_harness/skills/nx-surface-modeling/references/user-practice.md  12 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/blade_centrifugal.py  14 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/blade_edit_count.py  9 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/blade_helicoid.py  12 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/blade_sections.py  10 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/nxblade.py  36 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/surf_blend_trim_offset.py  54 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/surf_build.py  22 KB  2026-10-04
_harness/skills/nx-surface-modeling/scripts/surf_course_checks.py  41 KB  2026-10-04
_harness/skills/nx-surface-modeling/scripts/surf_edit.py  24 KB  2026-10-04
_harness/skills/nx-surface-modeling/scripts/surf_law_extension.py  27 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/surf_loft_options.py  39 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/surf_mould_repair.py  18 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/surf_nsided.py  20 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/surf_round3_checks.py  49 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/surf_section_surface.py  24 KB  2026-10-06
_harness/skills/nx-surface-modeling/scripts/swept_twist.py  8 KB  2026-10-06
```

### dreame_bottom_cover (nx_re_projects_20261105_part4.zip)
```
dreame_bottom_cover/transcripts/8321884a-def9-457d-bea2-1af9aab9a19b.jsonl  3.4 MB  
dreame_bottom_cover/work/an/C_hook5.png  172 KB  2026-10-07
dreame_bottom_cover/work/an/C_tab.png  176 KB  2026-10-07
dreame_bottom_cover/work/an/C_tab_x.png  218 KB  2026-10-07
dreame_bottom_cover/work/an/C_tab_z.png  167 KB  2026-10-07
dreame_bottom_cover/work/an/D_latch2_y.png  178 KB  2026-10-07
dreame_bottom_cover/work/an/D_latch_x.png  186 KB  2026-10-07
dreame_bottom_cover/work/an/D_latch_z.png  191 KB  2026-10-07
dreame_bottom_cover/work/an/E_grille_x.png  272 KB  2026-10-07
dreame_bottom_cover/work/an/F_bowl_z.png  228 KB  2026-10-07
dreame_bottom_cover/work/an/G_grid_x.png  164 KB  2026-10-07
dreame_bottom_cover/work/an/G_grid_y.png  161 KB  2026-10-07
dreame_bottom_cover/work/an/G_rail_y1.png  267 KB  2026-10-07
dreame_bottom_cover/work/an/G_rail_y2.png  271 KB  2026-10-07
dreame_bottom_cover/work/an/bowl_meridians.png  58 KB  2026-10-07
dreame_bottom_cover/work/an/bowl_rtheta.png  205 KB  2026-10-07
dreame_bottom_cover/work/an/chk.py  0 KB  2026-10-07
dreame_bottom_cover/work/an/common.py  5 KB  2026-10-07
dreame_bottom_cover/work/an/dev.py  6 KB  2026-10-08
dreame_bottom_cover/work/an/dev_d1.json  2 KB  2026-10-07
dreame_bottom_cover/work/an/dev_d2.json  3 KB  2026-10-08
dreame_bottom_cover/work/an/dev_d3.json  3 KB  2026-10-08
dreame_bottom_cover/work/an/dev_d4.json  3 KB  2026-10-08
dreame_bottom_cover/work/an/dev_d5.json  3 KB  2026-10-08
dreame_bottom_cover/work/an/dev_final.json  3 KB  2026-10-08
dreame_bottom_cover/work/an/dev_final_raw.json  3 KB  2026-10-08
dreame_bottom_cover/work/an/dev_probe1.json  2 KB  2026-10-07
dreame_bottom_cover/work/an/fit.py  5 KB  2026-10-07
dreame_bottom_cover/work/an/hmap_bot.png  167 KB  2026-10-07
dreame_bottom_cover/work/an/hmap_thick.png  228 KB  2026-10-07
dreame_bottom_cover/work/an/hmap_top.png  198 KB  2026-10-07
dreame_bottom_cover/work/an/hmap_top_fine.png  110 KB  2026-10-07
dreame_bottom_cover/work/an/m_beam.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_bowl.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_bowl2.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_bowl3.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_bowl4.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/m_bowl5.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_bowl6.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_bowl7.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/m_deck.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_deck2.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_deck3.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/m_grille.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/m_grille2.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/m_hook.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/m_hook2.py  2 KB  2026-10-08
dreame_bottom_cover/work/an/m_rail.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/m_rail2.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/o_a_rail.png  119 KB  2026-10-07
dreame_bottom_cover/work/an/o_a_x.png  138 KB  2026-10-07
dreame_bottom_cover/work/an/o_a_y.png  210 KB  2026-10-07
dreame_bottom_cover/work/an/o_b_corner.png  280 KB  2026-10-07
dreame_bottom_cover/work/an/o_b_cz.png  141 KB  2026-10-07
dreame_bottom_cover/work/an/o_b_x.png  268 KB  2026-10-07
dreame_bottom_cover/work/an/o_c_x.png  231 KB  2026-10-07
dreame_bottom_cover/work/an/o_c_y.png  226 KB  2026-10-07
dreame_bottom_cover/work/an/o_e_x.png  170 KB  2026-10-08
dreame_bottom_cover/work/an/o_e_x2.png  144 KB  2026-10-08
dreame_bottom_cover/work/an/o_e_y.png  110 KB  2026-10-08
dreame_bottom_cover/work/an/overview.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/ovl.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/pw.py  5 KB  2026-10-07
dreame_bottom_cover/work/an/render.py  2 KB  2026-10-08
dreame_bottom_cover/work/an/sec.py  3 KB  2026-10-07
dreame_bottom_cover/work/an/shade.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/sx_mid.png  119 KB  2026-10-07
dreame_bottom_cover/work/an/sz_all.png  201 KB  2026-10-07
dreame_bottom_cover/work/an/warp.json  0 KB  2026-10-07
dreame_bottom_cover/work/an/zones.py  2 KB  2026-10-07
dreame_bottom_cover/work/an/ztable.py  1 KB  2026-10-07
dreame_bottom_cover/work/build.py  26 KB  2026-10-08
dreame_bottom_cover/work/deliver/figures/overlay_plan_sections.png  244 KB  2026-10-08
dreame_bottom_cover/work/deliver/figures/overlay_y_sections.png  283 KB  2026-10-08
dreame_bottom_cover/work/deliver/figures/render_iso_bowl_end_cad.png  228 KB  2026-10-08
dreame_bottom_cover/work/deliver/figures/render_iso_top_cad.png  252 KB  2026-10-08
dreame_bottom_cover/work/deliver/figures/render_iso_underside_cad.png  226 KB  2026-10-08
dreame_bottom_cover/work/deliver/figures/render_iso_underside_rail_cad.png  220 KB  2026-10-08
dreame_bottom_cover/work/nxlib/geo.py  4 KB  2026-10-07
dreame_bottom_cover/work/nxlib/ps.py  14 KB  2026-10-07
dreame_bottom_cover/work/nxlib/st_c.py  16 KB  2026-10-08
dreame_bottom_cover/work/nxlib/st_d.py  11 KB  2026-10-08
dreame_bottom_cover/work/out/build.json  24 KB  2026-10-08
dreame_bottom_cover/work/out/dreame_mop_bottom_cover.log  10 KB  2026-10-08
dreame_bottom_cover/work/out/probe1.json  2 KB  2026-10-07
dreame_bottom_cover/work/out/probe2.json  1 KB  2026-10-07
dreame_bottom_cover/work/out/review.json  0 KB  2026-10-08
dreame_bottom_cover/work/out/scan_datum_frame_137k.stl  6.6 MB  2026-10-08
dreame_bottom_cover/work/probe1.py  3 KB  2026-10-07
dreame_bottom_cover/work/probe2.py  3 KB  2026-10-07
dreame_bottom_cover/work/review.py  1 KB  2026-10-08
dreame_bottom_cover/work/run.ps1  1 KB  2026-10-07
```

### dreame_brush_core (nx_re_projects_20261105_part2.zip)
```
dreame_brush_core/transcripts/00db997d-dec5-46a3-8606-c7e627285bcd.jsonl  3.4 MB  
dreame_brush_core/transcripts/dd1460f7-90fd-471a-b6b0-87872f6e32f2.jsonl  2.9 MB  
dreame_brush_core/work/REPORT.md  19 KB  2026-10-08
dreame_brush_core/work/REPORT2.md  19 KB  2026-10-10
dreame_brush_core/work/an/b0_baseline.py  3 KB  2026-10-08
dreame_brush_core/work/an/b1_bristle_first.py  2 KB  2026-10-08
dreame_brush_core/work/an/b2_base_first.py  5 KB  2026-10-08
dreame_brush_core/work/an/b3_compare.py  3 KB  2026-10-08
dreame_brush_core/work/an/common.py  6 KB  2026-10-08
dreame_brush_core/work/an/common2.py  2 KB  2026-10-09
dreame_brush_core/work/an/dev.py  7 KB  2026-10-08
dreame_brush_core/work/an/dev_c2s.py  2 KB  2026-10-08
dreame_brush_core/work/an/dev_outliers.py  2 KB  2026-10-08
dreame_brush_core/work/an/dev_under_icp.py  1 KB  2026-10-08
dreame_brush_core/work/an/f0_view_ref.py  2 KB  2026-10-09
dreame_brush_core/work/an/f10_tuft_flap_gap.py  2 KB  2026-10-09
dreame_brush_core/work/an/f1_align.py  6 KB  2026-10-09
dreame_brush_core/work/an/f2_look.py  4 KB  2026-10-09
dreame_brush_core/work/an/f3_flap.py  5 KB  2026-10-09
dreame_brush_core/work/an/f4_flap_ends.py  7 KB  2026-10-09
dreame_brush_core/work/an/f5_scan_datum.py  1 KB  2026-10-09
dreame_brush_core/work/an/f6_dev.py  4 KB  2026-10-09
dreame_brush_core/work/an/f7_count_flaps.py  2 KB  2026-10-09
dreame_brush_core/work/an/f8_flap_cad_section.py  2 KB  2026-10-09
dreame_brush_core/work/an/f8b_shoulder.py  1 KB  2026-10-09
dreame_brush_core/work/an/f9_flap_foot.py  4 KB  2026-10-09
dreame_brush_core/work/an/m1_align.py  7 KB  2026-10-08
dreame_brush_core/work/an/m2_twist.py  5 KB  2026-10-08
dreame_brush_core/work/an/m3_profile.py  7 KB  2026-10-08
dreame_brush_core/work/an/m3_small.py  2 KB  2026-10-08
dreame_brush_core/work/an/m3_vgroove.py  2 KB  2026-10-08
dreame_brush_core/work/an/m3_zoom.py  3 KB  2026-10-08
dreame_brush_core/work/an/m4_base.py  7 KB  2026-10-08
dreame_brush_core/work/an/m5_top.py  4 KB  2026-10-08
dreame_brush_core/work/an/m6_tufts.py  6 KB  2026-10-08
dreame_brush_core/work/an/m6_tufts_view.py  2 KB  2026-10-08
dreame_brush_core/work/an/m7_base_align.py  5 KB  2026-10-08
dreame_brush_core/work/an/m7_hex.py  4 KB  2026-10-08
dreame_brush_core/work/an/m7_recentre.py  4 KB  2026-10-08
dreame_brush_core/work/an/m7_underside.py  5 KB  2026-10-08
dreame_brush_core/work/an/m8_misc.py  7 KB  2026-10-08
dreame_brush_core/work/an/ovl.py  3 KB  2026-10-08
dreame_brush_core/work/an/r2_render.py  3 KB  2026-10-09
dreame_brush_core/work/an/r3_compose.py  2 KB  2026-10-09
dreame_brush_core/work/an/render.py  3 KB  2026-10-08
dreame_brush_core/work/an/s1_step_check.py  4 KB  2026-10-09
dreame_brush_core/work/an/s2_flap_volume.py  3 KB  2026-10-09
dreame_brush_core/work/an/s3_step_wall_probe.py  3 KB  2026-10-09
dreame_brush_core/work/an/scans_datum.py  1 KB  2026-10-08
dreame_brush_core/work/an/stlstat.py  1 KB  2026-10-08
dreame_brush_core/work/an/view.py  2 KB  2026-10-08
dreame_brush_core/work/asfound2.py  3 KB  2026-10-10
dreame_brush_core/work/build.py  42 KB  2026-10-08
dreame_brush_core/work/build2.py  70 KB  2026-10-09
dreame_brush_core/work/build2_tail.py  37 KB  2026-10-09
dreame_brush_core/work/deliver.py  4 KB  2026-10-08
dreame_brush_core/work/deliver2.py  4 KB  2026-10-10
dreame_brush_core/work/export_ref.py  3 KB  2026-10-08
dreame_brush_core/work/fig/b0_rz.png  108 KB  2026-10-08
dreame_brush_core/work/fig/b0_sections.png  240 KB  2026-10-08
dreame_brush_core/work/fig/b1_rz.png  115 KB  2026-10-08
dreame_brush_core/work/fig/b1_sections.png  122 KB  2026-10-08
dreame_brush_core/work/fig/iki_farkli_cekirdek.png  172 KB  2026-10-08
dreame_brush_core/work/fig/m2_untwisted.png  257 KB  2026-10-08
dreame_brush_core/work/fig/m3_small.png  57 KB  2026-10-08
dreame_brush_core/work/fig/m3_vgroove.png  232 KB  2026-10-08
dreame_brush_core/work/fig/m3_zoom.png  284 KB  2026-10-08
dreame_brush_core/work/fig/m4_base.png  161 KB  2026-10-08
dreame_brush_core/work/fig/m5_top.png  134 KB  2026-10-08
dreame_brush_core/work/fig/m6_shells.png  291 KB  2026-10-08
dreame_brush_core/work/fig/m6_tufts.png  201 KB  2026-10-08
dreame_brush_core/work/fig/ovl_final_rz.png  92 KB  2026-10-08
dreame_brush_core/work/fig/ovl_final_z.png  196 KB  2026-10-08
dreame_brush_core/work/fig/ovl_it1_rz.png  92 KB  2026-10-08
dreame_brush_core/work/fig/ovl_it1_z.png  198 KB  2026-10-08
dreame_brush_core/work/fig/render_drive_end_cad.png  292 KB  2026-10-08
dreame_brush_core/work/fig/render_idler_end_cad.png  191 KB  2026-10-08
dreame_brush_core/work/fig/render_underside_cad.png  179 KB  2026-10-08
dreame_brush_core/work/fig2/delivery_figures.json  1 KB  2026-10-09
dreame_brush_core/work/fig2/f0_reference_sections.png  125 KB  2026-10-09
dreame_brush_core/work/fig2/f2_envelope.png  127 KB  2026-10-09
dreame_brush_core/work/fig2/f2_sections.png  191 KB  2026-10-09
dreame_brush_core/work/fig2/f3_flap_tip_by_z.png  143 KB  2026-10-09
dreame_brush_core/work/fig2/f4_bead.png  144 KB  2026-10-09
dreame_brush_core/work/fig2/f4_flap_end_sections.png  242 KB  2026-10-09
dreame_brush_core/work/fig2/f6_untwisted_overlay.png  154 KB  2026-10-09
dreame_brush_core/work/fig2/f7_flap_count.png  75 KB  2026-10-09
dreame_brush_core/work/fig2/f8_flap_cad_sections.png  157 KB  2026-10-09
dreame_brush_core/work/fig2/f8_flap_cad_sections_trial.png  156 KB  2026-10-09
dreame_brush_core/work/fill_report.py  4 KB  2026-10-10
dreame_brush_core/work/fixup_expr.py  2 KB  2026-10-09
dreame_brush_core/work/mk_build2.py  3 KB  2026-10-09
dreame_brush_core/work/names.py  1 KB  2026-10-08
dreame_brush_core/work/nxlib/geo.py  4 KB  2026-10-07
dreame_brush_core/work/nxlib/ps.py  14 KB  2026-10-08
dreame_brush_core/work/out/asfound/delivered_copy.prt  2.1 MB  2026-10-08
dreame_brush_core/work/out/asfound/delivered_copy_asfound.json  62 KB  2026-10-08
dreame_brush_core/work/out/asfound/delivered_copy_asfound.txt  13 KB  2026-10-08
dreame_brush_core/work/out/asfound/names.json  4 KB  2026-10-08
dreame_brush_core/work/out/build_a.json  7 KB  2026-10-08
dreame_brush_core/work/out/build_b.json  14 KB  2026-10-08
dreame_brush_core/work/out/build_d.json  21 KB  2026-10-08
dreame_brush_core/work/out/build_z.json  62 KB  2026-10-08
dreame_brush_core/work/out/dreame_brush_core_with_bristles.log  9 KB  2026-10-08
dreame_brush_core/work/out/export_a.json  2 KB  2026-10-08
dreame_brush_core/work/out/export_b.json  4 KB  2026-10-08
dreame_brush_core/work/out/nb/export_nb.json  3 KB  2026-10-09
dreame_brush_core/work/out/probe1.json  7 KB  2026-10-08
dreame_brush_core/work/out/probe2.json  5 KB  2026-10-08
dreame_brush_core/work/out/probe3.json  1 KB  2026-10-08
dreame_brush_core/work/out/probe_a.json  111 KB  2026-10-08
dreame_brush_core/work/out/review.json  1 KB  2026-10-08
dreame_brush_core/work/out/scan_base_end_datum.stl  10.9 MB  2026-10-08
dreame_brush_core/work/out2/asfound2.json  3 KB  2026-10-10
dreame_brush_core/work/out2/build2_abcd.json  20 KB  2026-10-09
dreame_brush_core/work/out2/build2_abcdefz.json  55 KB  2026-10-09
dreame_brush_core/work/out2/build2_f.json  44 KB  2026-10-09
dreame_brush_core/work/out2/dreame_brush_with_bristles.log  10 KB  2026-10-09
dreame_brush_core/work/out2/fixup_expr.json  0 KB  2026-10-09
dreame_brush_core/work/out2/review2.json  1 KB  2026-10-09
dreame_brush_core/work/out2/scan_brush_with_bristles_datum.stl  17.2 MB  2026-10-09
dreame_brush_core/work/out2/step_first_run.log  5 KB  2026-10-09
dreame_brush_core/work/out2e/build2_e.json  37 KB  2026-10-10
dreame_brush_core/work/patch1.py  2 KB  2026-10-08
dreame_brush_core/work/patch2.py  1 KB  2026-10-08
dreame_brush_core/work/patch3.py  3 KB  2026-10-08
dreame_brush_core/work/patch4.py  6 KB  2026-10-08
dreame_brush_core/work/patch5.py  2 KB  2026-10-08
dreame_brush_core/work/patch_e.py  3 KB  2026-10-09
dreame_brush_core/work/patch_fil.py  5 KB  2026-10-09
dreame_brush_core/work/patch_final.py  3 KB  2026-10-09
dreame_brush_core/work/patch_report.py  1 KB  2026-10-08
dreame_brush_core/work/patch_z.py  4 KB  2026-10-09
dreame_brush_core/work/probe1.py  4 KB  2026-10-08
dreame_brush_core/work/probe2.py  7 KB  2026-10-08
dreame_brush_core/work/probe3.py  4 KB  2026-10-08
dreame_brush_core/work/probe_ref.py  5 KB  2026-10-08
dreame_brush_core/work/qa/T_base.json  1 KB  2026-10-08
dreame_brush_core/work/qa/T_base_icp.json  1 KB  2026-10-08
dreame_brush_core/work/qa/T_bristles.json  1 KB  2026-10-08
dreame_brush_core/work/qa/b0_baseline.json  3 KB  2026-10-08
dreame_brush_core/work/qa/base_end0_T0.json  0 KB  2026-10-08
dreame_brush_core/work/qa/base_end1_T0.json  0 KB  2026-10-08
dreame_brush_core/work/qa/dev_final.json  5 KB  2026-10-08
dreame_brush_core/work/qa/dev_final_cad_to_scan.json  2 KB  2026-10-08
dreame_brush_core/work/qa/dev_final_outliers.json  1 KB  2026-10-08
dreame_brush_core/work/qa/dev_final_underside_icp.json  3 KB  2026-10-08
dreame_brush_core/work/qa/dev_it1.json  5 KB  2026-10-08
dreame_brush_core/work/qa/m1_align.json  8 KB  2026-10-08
dreame_brush_core/work/qa/m2_twist.json  3 KB  2026-10-08
dreame_brush_core/work/qa/m3_profile.json  4 KB  2026-10-08
dreame_brush_core/work/qa/m4_base.json  2 KB  2026-10-08
dreame_brush_core/work/qa/m5_top.json  1 KB  2026-10-08
dreame_brush_core/work/qa/m6_tufts.json  4 KB  2026-10-08
dreame_brush_core/work/qa/m7_base_align.json  2 KB  2026-10-08
dreame_brush_core/work/qa/m7_hex.json  4 KB  2026-10-08
dreame_brush_core/work/qa/m7_recentre.json  1 KB  2026-10-08
dreame_brush_core/work/qa/m7_underside.json  2 KB  2026-10-08
dreame_brush_core/work/qa/m8_misc.json  2 KB  2026-10-08
dreame_brush_core/work/qa/prt_text_brush_no_bristles_cad.json  5 KB  2026-10-08
dreame_brush_core/work/qa/prt_text_ref_a.json  9 KB  2026-10-08
dreame_brush_core/work/qa/prt_text_ref_b.json  8 KB  2026-10-08
dreame_brush_core/work/qa/prt_text_rejected.json  1 KB  2026-10-08
dreame_brush_core/work/qa/ref_a_asfound.json  35 KB  2026-10-08
dreame_brush_core/work/qa/ref_a_asfound.txt  5 KB  2026-10-08
dreame_brush_core/work/qa2/T_asm.json  1 KB  2026-10-09
dreame_brush_core/work/qa2/f10_tuft_flap_gap.json  1 KB  2026-10-09
dreame_brush_core/work/qa2/f1_align.json  4 KB  2026-10-09
dreame_brush_core/work/qa2/f3_flap.json  86 KB  2026-10-09
dreame_brush_core/work/qa2/f4_flap_ends.json  185 KB  2026-10-09
dreame_brush_core/work/qa2/f6_dev.json  4 KB  2026-10-09
dreame_brush_core/work/qa2/f8_flap_cad_section.json  9 KB  2026-10-09
dreame_brush_core/work/qa2/f8_flap_cad_section_trial.json  10 KB  2026-10-09
dreame_brush_core/work/qa2/f9_flap_foot.json  2 KB  2026-10-09
dreame_brush_core/work/qa2/s1_step_check.json  1 KB  2026-10-09
dreame_brush_core/work/qa2/s2_flap_volume.json  1 KB  2026-10-10
dreame_brush_core/work/qa2/s3_step_wall_probe.json  3 KB  2026-10-09
dreame_brush_core/work/review.py  2 KB  2026-10-08
dreame_brush_core/work/review2.py  2 KB  2026-10-09
dreame_brush_core/work/run.ps1  0 KB  2026-10-08
dreame_brush_core/work/run2.ps1  1 KB  2026-10-09
dreame_brush_core/work/show.py  1 KB  2026-10-08
dreame_brush_core/work/show2.py  2 KB  2026-10-09
dreame_brush_core/work/test_pure.py  3 KB  2026-10-09
dreame_brush_core/work/to_repo.py  2 KB  2026-10-08
dreame_brush_core/work/to_repo_figs.py  1 KB  2026-10-08
dreame_brush_core/work/verify_repo.py  1 KB  2026-10-08
```

### dreame_dustbin_air_inlet (nx_re_projects_20261105_part1.zip)
```
dreame_dustbin_air_inlet/transcripts/e7db2fb7-ddad-4bed-9a67-a86f3a7848b4.jsonl  1.3 MB  
dreame_dustbin_air_inlet/work/CHANGES.txt  3 KB  2026-10-07
dreame_dustbin_air_inlet/work/add_air_inlet.py  15 KB  2026-10-07
dreame_dustbin_air_inlet/work/depthview.py  4 KB  2026-10-07
dreame_dustbin_air_inlet/work/export_asfound.py  0 KB  2026-10-07
dreame_dustbin_air_inlet/work/measure2.py  4 KB  2026-10-07
dreame_dustbin_air_inlet/work/measure_opening.py  6 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/add_air_inlet.json  10 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/add_air_inlet.log  1 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/air_inlet_outline_vs_scan.png  221 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/asfound_check.log  5 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/cmp_mX.png  211 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/cmp_mZ.png  293 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/cmp_pX.png  237 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/dreame_dust_bin CAD_asfound.json  63 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/dreame_dust_bin CAD_asfound.txt  9 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/dust_bin_dreame.log  5 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/export_asfound.json  0 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/opening_mask.png  46 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/opening_measure.json  1 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/opening_measure2.json  1 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/probe1.json  345 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/probe2.json  1 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/probe_sketch.json  3 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/scan_0.stl  0 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/sec_x.png  166 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/sec_z.png  137 KB  2026-10-07
dreame_dustbin_air_inlet/work/out/verify_after.json  2 KB  2026-10-07
dreame_dustbin_air_inlet/work/probe1.py  3 KB  2026-10-07
dreame_dustbin_air_inlet/work/probe2.py  1 KB  2026-10-07
dreame_dustbin_air_inlet/work/probe_sketch.py  4 KB  2026-10-07
dreame_dustbin_air_inlet/work/render.py  3 KB  2026-10-07
dreame_dustbin_air_inlet/work/sections.py  3 KB  2026-10-07
dreame_dustbin_air_inlet/work/ugstep242.log  0 KB  2026-10-07
dreame_dustbin_air_inlet/work/verify_after.py  7 KB  2026-10-07
```

### dreame_mop_early_nx (nx_re_projects_20261105_part1.zip)
```
dreame_mop_early_nx/transcripts/8d295d90-dd65-45c3-82b9-62f39c1a092f.jsonl  3.1 MB  
```

### r385_pump (nx_re_projects_20261105_part3.zip)
```
r385_pump/drive_source/385 Water-Pump.pdf  605 KB  2026-10-08
r385_pump/drive_source/CLAUDE.md  9 KB  2026-10-09
r385_pump/drive_source/R385-DR01 Eksantrik gobek.stl  3.6 MB  2026-10-09
r385_pump/drive_source/R385-DR01 Eksantrik gobek/plzUe_qmJK_HtMZ_HUwC/result/Mesh.ply  1.8 MB  2026-10-09
r385_pump/drive_source/R385-DR01 Eksantrik gobek/se5SApQ_5jOO7n_rM63ph_vaQpOw/result/Fused.ply  1.4 MB  2026-10-09
r385_pump/drive_source/R385-DR01 Eksantrik gobek/se5SApQ_5jOO7n_rM63ph_vaQpOw/result/model.ply  250 KB  2026-10-09
r385_pump/drive_source/R385-DR01 Eksantrik gobek/sghW9GA_laar0I_E656Jr_IbTfWy/result/Fused.ply  1.5 MB  2026-10-09
r385_pump/drive_source/R385-DR01 Eksantrik gobek/sghW9GA_laar0I_E656Jr_IbTfWy/result/model.ply  271 KB  2026-10-09
r385_pump/drive_source/R385-DR01 Eksantrik gobek/thumbnail.png  6 KB  2026-10-09
r385_pump/drive_source/R385-DR02 Salinim Plakasi/s6xqhhQ_ibWE1o_9GC3eT_IgUFES/result/model.ply  746 KB  2026-10-09
r385_pump/drive_source/R385-DR02 Salinim Plakasi/sFFmJt0_hCp6Bp_ENvx42_6tz0pE/result/Fused.ply  3.0 MB  2026-10-09
r385_pump/drive_source/R385-DR02 Salinim Plakasi/sFFmJt0_hCp6Bp_ENvx42_6tz0pE/result/model.ply  554 KB  2026-10-09
r385_pump/drive_source/R385-DR02 Salinim Plakasi/sZzCUKI_cMeYcj_FoYpIf_whfMYL/result/model.ply  413 KB  2026-10-09
r385_pump/drive_source/R385-DR02 Salinim Plakasi/thumbnail.png  5 KB  2026-10-09
r385_pump/drive_source/R385-HS01 Motor yuvası/sYnHPNH_sLxMZU_p0myKu_5YU2C8/result/model.ply  1.2 MB  2026-10-09
r385_pump/drive_source/R385-HS01 Motor yuvası/sfem2Az_2N8Nb0_xHlkxl_zqafj7/result/model.ply  1.5 MB  2026-10-09
r385_pump/drive_source/R385-HS01 Motor yuvası/thumbnail.png  7 KB  2026-10-09
r385_pump/drive_source/R385-HS02 Diyafram Cercevesi/sGpbYYy_4GRN3m_d1DclC_RhpdAl/result/model.ply  1.2 MB  2026-10-09
r385_pump/drive_source/R385-HS02 Diyafram Cercevesi/swPh6uV_y9qc6X_vN5ARp_KeR6jf/result/model.ply  1.4 MB  2026-10-09
r385_pump/drive_source/R385-HS02 Diyafram Cercevesi/thumbnail.png  5 KB  2026-10-09
r385_pump/drive_source/R385-HS03 Valf Plakasi/skYlpzl_nFd1As_KWMYar_qxvB1N/result/model.ply  3.2 MB  2026-10-09
r385_pump/drive_source/R385-HS03 Valf Plakasi/sliJ45a_AH6W25_punYbr_k2JGBs/result/model.ply  3.0 MB  2026-10-09
r385_pump/drive_source/R385-HS03 Valf Plakasi/thumbnail.png  52 KB  2026-10-09
r385_pump/drive_source/R385-HS04 Pompa kafasi/s1yqBrq_opo2oQ_lL5b4j_0LUt4o/result/model.ply  1.1 MB  2026-10-09
r385_pump/drive_source/R385-HS04 Pompa kafasi/s3SZUFm_KTtWGw_d8DOxd_OHWu08/result/model.ply  965 KB  2026-10-09
r385_pump/drive_source/R385-HS04 Pompa kafasi/sqGhFaM_2cj4Xe_HPoVF7_W4M8Ek/result/model.ply  992 KB  2026-10-09
r385_pump/drive_source/R385-HS04 Pompa kafasi/thumbnail.png  6 KB  2026-10-09
r385_pump/drive_source/R385-MT01 DC motor/sOQi5yc_KSAIxA_9o1HsY_JjmJa8/result/model.ply  1.5 MB  2026-10-09
r385_pump/drive_source/R385-MT01 DC motor/thumbnail.png  11 KB  2026-10-09
r385_pump/drive_source/R385-SL01 Diyafram/sDLJ99K_Rq6CvI_fVxzpz_pFq6Bl/result/model.ply  1.5 MB  2026-10-09
r385_pump/drive_source/R385-SL01 Diyafram/thumbnail.png  15 KB  2026-10-09
r385_pump/drive_source/R385-SL03 Basma valfi/sERVIhd_OdhLLk_hAE987_qbrPnw/result/model.ply  832 KB  2026-10-09
r385_pump/drive_source/R385-SL03 Basma valfi/thumbnail.png  12 KB  2026-10-09
r385_pump/drive_source/R385-SL04 Kafa contasi/shxnCCC_rvKoUx_J5QcT5_VPdqjL/result/model.ply  817 KB  2026-10-09
r385_pump/drive_source/R385-SL04 Kafa contasi/thumbnail.png  16 KB  2026-10-09
r385_pump/drive_source/R385_INTERFACES.md  15 KB  2026-10-09
r385_pump/drive_source/cad/R385-DR01_ECCENTRIC_REPORT.md  5 KB  2026-10-09
r385_pump/drive_source/cad/R385-DR02_WOBBLE_REPORT.md  6 KB  2026-10-09
r385_pump/drive_source/cad/R385-HS01_MOUNT_REPORT.md  6 KB  2026-10-09
r385_pump/drive_source/cad/R385-HS02_FRAME_REPORT.md  9 KB  2026-10-09
r385_pump/drive_source/cad/R385-HS03_VALVE-PLATE_REPORT.md  6 KB  2026-10-09
r385_pump/drive_source/cad/R385-HS04_HEAD_REPORT.md  6 KB  2026-10-09
r385_pump/drive_source/cad/R385-MT01_MOTOR_REPORT.md  6 KB  2026-10-09
r385_pump/drive_source/cad/R385-SL01_DIAPHRAGM_REPORT.md  5 KB  2026-10-09
r385_pump/drive_source/cad/R385-SL02_VALVE-IN_REPORT.md  2 KB  2026-10-09
r385_pump/drive_source/cad/R385-SL03_VALVE-OUT_REPORT.md  2 KB  2026-10-09
r385_pump/drive_source/cad/R385-SL04_GASKET_REPORT.md  1 KB  2026-10-09
r385_pump/drive_source/cad/assembly/asm_build.json  19 KB  2026-10-09
r385_pump/drive_source/cfd/CLOUD_HANDOFF.md  7 KB  2026-10-09
r385_pump/drive_source/cfd/README.md  19 KB  2026-10-09
r385_pump/drive_source/cfd/REPO_COMPARISON.md  12 KB  2026-10-09
r385_pump/drive_source/cfd/SIMULATION_PLAN.md  18 KB  2026-10-09
r385_pump/drive_source/cfd/STAGE1_RESULTS.md  35 KB  2026-10-09
r385_pump/drive_source/cfd/bench/bench_reference.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/bench/c025_np16/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/bench/c025_np16/results/console.Allsmoke.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/bench/c025_np6/results/console.Allsmoke.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/bench/c050_np1/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/bench/c050_np1/results/console.Allsmoke.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_single_chamber/README.md  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_single_chamber/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_single_chamber/results/console.Allcheck.txt  3 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_single_chamber/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_single_chamber/results/stage1_check.png  143 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_single_chamber/results/stage1_summary.json  2 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/c_8cyc/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/c_8cyc/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f01_vaka.png  125 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f02_ag.png  137 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f04_cevrim.png  143 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f05_ag_basinc.png  174 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f06_ag_yakinsama.png  191 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f07_zaman_adimi.png  162 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f08_cevrim_yakinsama.png  204 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f09_turbulans.png  106 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f10_tarama.png  273 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f11_tarama_basinc.png  173 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f12_cfd_0b_fark.png  92 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f14_basinc_cevrim.png  91 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f15_ag_270.png  273 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f16_ag_090.png  275 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f17_ag_profiller.png  219 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f18_sst_alan.png  239 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/f19_5000.png  94 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/fig/fields_summary.json  6 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/m_c025/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/m_c025/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/m_c050/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/m_c050/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/m_c100/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/m_c100/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp000/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp000/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp000/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp030/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp030/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp030/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp100/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp100/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp100/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp150/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp150/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n1000_dp150/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp000/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp000/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp000/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp030/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp030/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp030/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp100/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp100/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp100/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp150/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp150/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n2000_dp150/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp000/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp000/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp000/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp100/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp100/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp100/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp150/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp150/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n3000_dp150/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp000/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp000/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp000/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp030/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp030/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp030/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp100/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp100/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp100/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp150/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp150/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n4000_dp150/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp000/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp000/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp000/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp030/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp030/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp030/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp100/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp100/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp100/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp150/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp150/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/p_n5000_dp150/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/report_notes.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/run_log.json  3 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/s_c050_sst/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/s_c050_sst/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/s_c050_sst/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/s_c100_sst/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/s_c100_sst/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/s_c100_sst/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/smoke_summary.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/study_results.json  78 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/sweep_table.json  20 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co0125/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co0125/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co0125/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co025/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co025/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co025/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co100/case_params.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co100/results/console.Allrun.txt  1 KB  2026-10-09
r385_pump/drive_source/cfd/cases/stage1_study/t_co100/run_config.json  0 KB  2026-10-09
r385_pump/drive_source/cfd/cloud/CLAUDE.md  6 KB  2026-10-09
r385_pump/drive_source/cfd/cloud/KICKOFF_PROMPT.md  1 KB  2026-10-09
r385_pump/drive_source/cfd/cloud/README.md  2 KB  2026-10-09
r385_pump/drive_source/cfd/cloud/setup.sh  3 KB  2026-10-09
r385_pump/drive_source/cfd/foamlib_smoke_result.json  1 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/fluid_closed_chamber1_neutral.stl  604 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/fluid_closed_discharge.stl  838 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/fluid_closed_suction.stl  1.0 MB  2026-10-09
r385_pump/drive_source/cfd/geometry/fluid_geometry.json  4 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/fluid_stage3.stl  2.2 MB  2026-10-09
r385_pump/drive_source/cfd/geometry/log.surfaceCheck.fluid_stage3.stl  3 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_in_1.stl  51 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_in_2.stl  51 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_in_3.stl  52 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_in_4.stl  52 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_in_5.stl  52 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_out_1.stl  24 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_out_2.stl  24 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_out_3.stl  24 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_out_4.stl  24 KB  2026-10-09
r385_pump/drive_source/cfd/geometry/zone_out_5.stl  24 KB  2026-10-09
r385_pump/drive_source/cfd/tools/bench_stage1.py  6 KB  2026-10-09
r385_pump/drive_source/cfd/tools/extract_fluid.py  12 KB  2026-10-09
r385_pump/drive_source/cfd/tools/figs_stage1.py  45 KB  2026-10-09
r385_pump/drive_source/cfd/tools/figstyle.py  4 KB  2026-10-09
r385_pump/drive_source/cfd/tools/foamlib_smoke.py  5 KB  2026-10-09
r385_pump/drive_source/cfd/tools/make_stage1.py  23 KB  2026-10-09
r385_pump/drive_source/cfd/tools/post_stage1.py  11 KB  2026-10-09
r385_pump/drive_source/cfd/tools/repo_sync.py  5 KB  2026-10-09
r385_pump/drive_source/cfd/tools/report_stage1.py  52 KB  2026-10-09
r385_pump/drive_source/cfd/tools/study_stage1.py  9 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_case.py  4 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_fields_all.sh  1 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_fields_stage1.sh  3 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_foamlib_smoke.sh  0 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_inspect_study.sh  1 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_run.sh  4 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_setup_foamlib.sh  1 KB  2026-10-09
r385_pump/drive_source/cfd/tools/wsl_surface_check.sh  1 KB  2026-10-09
r385_pump/drive_source/cr/CR-B-01.md  3 KB  2026-10-09
r385_pump/drive_source/cr/CR-D-01.md  4 KB  2026-10-09
r385_pump/drive_source/cr/CR-F-01.md  3 KB  2026-10-09
r385_pump/drive_source/cr/CR-G-01.md  4 KB  2026-10-09
r385_pump/drive_source/docs/scripts/00_env_check.py  2 KB  2026-10-09
r385_pump/drive_source/docs/scripts/01_prep_geometry.py  5 KB  2026-10-09
r385_pump/drive_source/docs/scripts/01b_cut.py  2 KB  2026-10-09
r385_pump/drive_source/docs/scripts/02_measure.py  8 KB  2026-10-09
r385_pump/drive_source/docs/scripts/03_section_data.py  2 KB  2026-10-09
r385_pump/drive_source/docs/scripts/04_render.py  5 KB  2026-10-09
r385_pump/drive_source/docs/scripts/05_hlr.py  5 KB  2026-10-09
r385_pump/drive_source/docs/scripts/06_check_explode.py  3 KB  2026-10-09
r385_pump/drive_source/docs/scripts/07_build_pdf.py  45 KB  2026-10-09
r385_pump/drive_source/docs/scripts/bl_render.py  6 KB  2026-10-09
r385_pump/drive_source/docs/scripts/prev_overlay.py  1 KB  2026-10-09
r385_pump/drive_source/docs/scripts/r385draw.py  12 KB  2026-10-09
r385_pump/drive_source/docs/scripts/views.py  7 KB  2026-10-09
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.39.43.jpeg  79 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.39.51.jpeg  56 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.41.10.jpeg  113 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.43.40.jpeg  102 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.45.07.jpeg  99 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.46.06.jpeg  98 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.49.03.jpeg  100 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.51.54.jpeg  114 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.58.09.jpeg  157 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-08 at 22.58.21.jpeg  105 KB  2026-10-08
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-09 at 08.57.25.jpeg  207 KB  2026-10-09
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-09 at 08.59.20.jpeg  157 KB  2026-10-09
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-09 at 08.59.33.jpeg  143 KB  2026-10-09
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-09 at 09.03.56.jpeg  175 KB  2026-10-09
r385_pump/drive_source/kurgu için input/WhatsApp Image 2026-10-09 at 09.23.29 (1).jpeg  160 KB  2026-10-09
r385_pump/drive_source/outer/thumbnail.png  6 KB  2026-10-08
r385_pump/drive_source/print/README.md  27 KB  2026-10-09
r385_pump/drive_source/print/flex/R385-SL02_VALVE-IN.stl  94 KB  2026-10-09
r385_pump/drive_source/print/flex/R385-SL03_VALVE-OUT.stl  47 KB  2026-10-09
r385_pump/drive_source/print/flex/R385-SL04_GASKET.stl  71 KB  2026-10-09
r385_pump/drive_source/print/img/R385-DR01_ECCENTRIC_hub_orient.png  51 KB  2026-10-09
r385_pump/drive_source/print/img/R385-DR02_WOBBLE_orient.png  67 KB  2026-10-09
r385_pump/drive_source/print/img/R385-HS01_MOUNT_orient.png  72 KB  2026-10-09
r385_pump/drive_source/print/img/R385-HS02_FRAME_orient.png  77 KB  2026-10-09
r385_pump/drive_source/print/img/R385-HS03_VALVE-PLATE_orient.png  91 KB  2026-10-09
r385_pump/drive_source/print/img/R385-HS04_HEAD_orient.png  75 KB  2026-10-09
r385_pump/drive_source/print/img/R385-SL01_DIAPHRAGM_orient.png  88 KB  2026-10-09
r385_pump/drive_source/print/img/R385-SL02_VALVE-IN_orient.png  45 KB  2026-10-09
r385_pump/drive_source/print/img/R385-SL03_VALVE-OUT_orient.png  50 KB  2026-10-09
r385_pump/drive_source/print/img/R385-SL04_GASKET_orient.png  58 KB  2026-10-09
r385_pump/drive_source/print/printability.json  73 KB  2026-10-09
r385_pump/drive_source/print/rigid/R385-DR01_ECCENTRIC_hub.stl  467 KB  2026-10-09
r385_pump/drive_source/print/rigid/R385-HS01_MOUNT.stl  1.4 MB  2026-10-09
r385_pump/drive_source/print/rigid/R385-HS02_FRAME.stl  1.6 MB  2026-10-09
r385_pump/drive_source/print/rigid/R385-HS03_VALVE-PLATE.stl  941 KB  2026-10-09
r385_pump/drive_source/print/rigid/R385-HS04_HEAD.stl  806 KB  2026-10-09
r385_pump/drive_source/print/tools/nx_export.json  123 KB  2026-10-09
r385_pump/drive_source/print/tools/nx_export.py  7 KB  2026-10-09
r385_pump/drive_source/print/tools/package.py  7 KB  2026-10-09
r385_pump/drive_source/print/tools/printability.py  8 KB  2026-10-09
r385_pump/drive_source/print/tools/r385print.py  5 KB  2026-10-09
r385_pump/drive_source/print/tools/recommend.py  2 KB  2026-10-09
r385_pump/drive_source/print/tools/render_orient.py  2 KB  2026-10-09
r385_pump/drive_source/print/tools/validate.py  11 KB  2026-10-09
r385_pump/drive_source/print/validation.json  30 KB  2026-10-09
r385_pump/drive_source/projede 2. gün kurgu input/WhatsApp Image 2026-10-10 at 18.33.55.jpeg  92 KB  2026-10-10
r385_pump/drive_source/projede 2. gün kurgu input/WhatsApp Unknown 2026-10-10 at 16.55.00/WhatsApp Image 2026-10-10 at 14.51.13 (1).jpeg  196 KB  2026-10-10
r385_pump/drive_source/projede 2. gün kurgu input/WhatsApp Unknown 2026-10-10 at 16.55.00/WhatsApp Image 2026-10-10 at 14.51.13.jpeg  198 KB  2026-10-10
r385_pump/drive_source/r385-dc-9-12v-water-pump-maximum-lift-3-meters.pdf  92 KB  2026-10-08
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/bench/c025_np16/case_params.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/bench/c050_np1/case_params.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/kwin.sh  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/launch.sh  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/peek.sh  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/profile.sh  2 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/scale.sh  2 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/sidecase.sh  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/speedtest.sh  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/speedtest2.sh  2 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/st.sh  3 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/coarse_dis_k1_n3000_sst/case.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/coarse_dis_k1_n3000_sst/done.json  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/coarse_suc_k1_n3000_sst/case.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/coarse_suc_k1_n3000_sst/done.json  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/smoke_discharge/case.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/smoke_discharge/done.json  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/smoke_suction/case.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/smoke_suction/done.json  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/x_safe_coarse_dis/case.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/cases/x_safe_coarse_suc/case.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/env.json  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_chanD.stl  164 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_cyl_1.stl  66 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_cyl_2.stl  64 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_cyl_3.stl  66 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_cyl_4.stl  68 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_cyl_5.stl  65 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_nipB_root.stl  39 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_bot_1.stl  64 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_bot_2.stl  42 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_bot_3.stl  53 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_bot_4.stl  54 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_bot_5.stl  44 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_top_1.stl  64 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_top_2.stl  42 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_top_3.stl  53 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_top_4.stl  54 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/constant/triSurface/plate_win_top_5.stl  44 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_discharge/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_chanS.stl  382 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_bot_1.stl  58 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_bot_2.stl  76 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_bot_3.stl  69 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_bot_4.stl  70 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_bot_5.stl  77 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_top_1.stl  58 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_top_2.stl  76 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_top_3.stl  69 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_top_4.stl  70 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_kid_top_5.stl  77 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_nipA_root.stl  41 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/constant/triSurface/plate_sl04.stl  47 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/coarse_suction/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/fine/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/fine_discharge/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/fine_suction/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/medium/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/medium_discharge/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/meshes/medium_suction/mesh_info.json  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/stage2a/smoke_speed.json  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/sync.sh  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385-cfd/waitjob.sh  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/BENIOKU.md  10 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/bench.log  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/bench/bench_okul.json  2 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/bench/bench_reference.json  1 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/cases/bench/c025_np16/results/console.Allsmoke.txt  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/cases/bench/c025_np6/results/console.Allsmoke.txt  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/cases/bench/c050_np1/results/console.Allsmoke.txt  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/cases/stage2a/geometry_stage2a.json  19 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/geometry/fluid_geometry.json  3 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/tools/figs_stage2a.py  10 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/tools/figstyle.py  4 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/tools/make_stage1.py  22 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/tools/make_stage2a.py  46 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/tools/pack_stage2a.py  2 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/tools/post_stage2a.py  13 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/cfd/tools/run_stage2a.py  36 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/mesh.log  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/mesh2.log  1 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/meshc.log  0 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/runc.log  2 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/smoke.log  7 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/smoke_1.log  3 KB  2026-10-10
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/design.json  11 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/displacement.json  7 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/geometry.json  3 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/kinematics.json  2 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/lumped.json  13 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/motor_qh.json  132 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/sensitivity.json  6 KB  2026-10-09
r385_pump/drive_source/r385_stage2a_paket/r385_stage2a/theory/calc/out/valves.json  2 KB  2026-10-09
r385_pump/drive_source/sessions/A_MEASURED.md  7 KB  2026-10-09
r385_pump/drive_source/sessions/A_QA.md  17 KB  2026-10-09
r385_pump/drive_source/sessions/A_STATUS.md  3 KB  2026-10-09
r385_pump/drive_source/sessions/B_MEASURED.md  22 KB  2026-10-09
r385_pump/drive_source/sessions/B_STATUS.md  5 KB  2026-10-09
r385_pump/drive_source/sessions/C_MEASURED.md  25 KB  2026-10-09
r385_pump/drive_source/sessions/C_STATUS.md  4 KB  2026-10-09
r385_pump/drive_source/sessions/D_STATUS.md  3 KB  2026-10-09
r385_pump/drive_source/sessions/E_STATUS.md  4 KB  2026-10-09
r385_pump/drive_source/sessions/F_STATUS.md  3 KB  2026-10-09
r385_pump/drive_source/sessions/G_STATUS.md  10 KB  2026-10-09
r385_pump/drive_source/theory/R385_DESIGN_PROCESS.md  19 KB  2026-10-09
r385_pump/drive_source/theory/R385_THEORY_REPORT.md  73 KB  2026-10-09
r385_pump/drive_source/theory/calc/build_report.py  9 KB  2026-10-09
r385_pump/drive_source/theory/calc/c1_geometry.py  7 KB  2026-10-09
r385_pump/drive_source/theory/calc/c2_kinematics.py  8 KB  2026-10-09
r385_pump/drive_source/theory/calc/c3_displacement.py  16 KB  2026-10-09
r385_pump/drive_source/theory/calc/c4_valves.py  8 KB  2026-10-09
r385_pump/drive_source/theory/calc/c5_lumped.py  13 KB  2026-10-09
r385_pump/drive_source/theory/calc/c6_motor_qh.py  17 KB  2026-10-09
r385_pump/drive_source/theory/calc/c7_sensitivity.py  7 KB  2026-10-09
r385_pump/drive_source/theory/calc/c8_design.py  7 KB  2026-10-09
r385_pump/drive_source/theory/calc/common.py  8 KB  2026-10-09
r385_pump/drive_source/theory/calc/inputs/ctrl_build.json  3 KB  2026-10-09
r385_pump/drive_source/theory/calc/inputs/ctrl_params.json  12 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/design.json  11 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/displacement.json  7 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/geometry.json  3 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/kinematics.json  2 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/lumped.json  14 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/motor_qh.json  136 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/sensitivity.json  6 KB  2026-10-09
r385_pump/drive_source/theory/calc/out/valves.json  3 KB  2026-10-09
r385_pump/drive_source/theory/calc/run_all.py  1 KB  2026-10-09
r385_pump/drive_source/theory/calc/steplib.py  6 KB  2026-10-09
r385_pump/drive_source/theory/fig/d1_diyafram.png  94 KB  2026-10-09
r385_pump/drive_source/theory/fig/d2_debi.png  159 KB  2026-10-09
r385_pump/drive_source/theory/fig/d3_emis.png  72 KB  2026-10-09
r385_pump/drive_source/theory/fig/g1_kesit.png  138 KB  2026-10-09
r385_pump/drive_source/theory/fig/k1_kinematik.png  196 KB  2026-10-09
r385_pump/drive_source/theory/fig/l1_cevrim.png  186 KB  2026-10-09
r385_pump/drive_source/theory/fig/l2_verim.png  144 KB  2026-10-09
r385_pump/drive_source/theory/fig/q1_qh.png  195 KB  2026-10-09
r385_pump/drive_source/theory/fig/q2_kuvvet.png  89 KB  2026-10-09
r385_pump/drive_source/theory/fig/s1_duyarlilik.png  98 KB  2026-10-09
r385_pump/drive_source/theory/fig/t1_tasarim.png  103 KB  2026-10-09
r385_pump/drive_source/theory/fig/v1_valf.png  138 KB  2026-10-09
r385_pump/drive_source/video/README.md  10 KB  2026-10-09
r385_pump/drive_source/video/check/check.json  5 KB  2026-10-09
r385_pump/drive_source/video/check/ffprobe.json  0 KB  2026-10-09
r385_pump/drive_source/video/check/interference.json  2 KB  2026-10-09
r385_pump/drive_source/video/scripts/01_check.py  14 KB  2026-10-09
r385_pump/drive_source/video/scripts/02_render.py  20 KB  2026-10-09
r385_pump/drive_source/video/scripts/03_interference.py  4 KB  2026-10-09
r385_pump/drive_source/video/scripts/04_encode.py  2 KB  2026-10-09
r385_pump/drive_source/video/scripts/contact.py  1 KB  2026-10-09
r385_pump/drive_source/video/scripts/explore_cut.py  1 KB  2026-10-09
r385_pump/drive_source/video/scripts/explore_morph.py  3 KB  2026-10-09
r385_pump/drive_source/video/scripts/explore_sections.py  4 KB  2026-10-09
r385_pump/drive_source/video/scripts/r385_geom.py  5 KB  2026-10-09
r385_pump/drive_source/video/scripts/r385_kin.py  3 KB  2026-10-09
r385_pump/drive_source/video/scripts/r385_morph.py  12 KB  2026-10-09
r385_pump/drive_source/video/scripts/r385_overlay.py  7 KB  2026-10-09
r385_pump/drive_source/video/scripts/r385_scene.py  17 KB  2026-10-09
r385_pump/drive_source/video/scripts/r385_sec.py  2 KB  2026-10-09
r385_pump/drive_source/video/scripts/test_scene.py  2 KB  2026-10-09
r385_pump/ep5_hs03/out1/step1.json  14 KB  2026-10-18
r385_pump/ep5_hs03/out1/step1.log  6 KB  2026-10-18
r385_pump/ep5_hs03/out2/step2.json  14 KB  2026-10-18
r385_pump/ep5_hs03/out2/step2.log  1 KB  2026-10-18
r385_pump/ep5_hs03/out3/step3.json  0 KB  2026-10-18
r385_pump/ep5_hs03/out3/step3.log  0 KB  2026-10-18
r385_pump/ep5_hs03/out3b/step3.log  0 KB  2026-10-18
r385_pump/ep5_hs03/out4/step4.json  1 KB  2026-10-18
r385_pump/ep5_hs03/out4/step4.log  0 KB  2026-10-18
r385_pump/ep5_hs03/run_step4.ps1  0 KB  2026-10-18
r385_pump/ep5_hs03/step1_describe_census.py  3 KB  2026-10-18
r385_pump/ep5_hs03/step2_align.py  3 KB  2026-10-18
r385_pump/ep5_hs03/step3_fit_table.py  4 KB  2026-10-18
r385_pump/ep5_hs03/step3_measure.py  5 KB  2026-10-18
r385_pump/ep5_hs03/step4_model.py  8 KB  2026-10-18
r385_pump/transcripts/0bf7b833-7f88-45b9-bc61-a6dced9c59d4.jsonl  658 KB  
r385_pump/transcripts/24f4f717-b6aa-4139-ac02-ef2070f50638.jsonl  3.4 MB  
r385_pump/transcripts/522aa477-6fb2-4f96-a095-2abb78cc04f8.jsonl  7.0 MB  
r385_pump/transcripts/522aa477_subagents/agent-aecef3f37b215ce6d.jsonl  894 KB  
r385_pump/transcripts/9b75049a-d4a4-4500-8f9c-1952a9ea4e9d.jsonl  2.1 MB  
r385_pump/transcripts/a0755bdb-3cc6-4a03-9189-b5f1abb0c20a.jsonl  1.7 MB  
r385_pump/transcripts/ab80fb64-1226-4408-9d6d-6f70caddfdf5.jsonl  3.1 MB  
r385_pump/transcripts/ca5a2a08-3ac3-4d22-a41c-3d0e4a1e8db3.jsonl  2.0 MB  
r385_pump/transcripts/d3aee339-abd1-49b0-b2ee-f7a321a3a628.jsonl  3.2 MB  
r385_pump/work/an/fig/o3_profile.png  227 KB  2026-10-09
r385_pump/work/an/fig/o4_lugprof.png  90 KB  2026-10-09
r385_pump/work/an/fig/o5_lugzoom.png  94 KB  2026-10-09
r385_pump/work/an/fig/o5_meridians.png  174 KB  2026-10-09
r385_pump/work/an/fig/q1_hs01_holes.png  80 KB  2026-10-09
r385_pump/work/an/fig/q5_stack_overlay.png  284 KB  2026-10-09
r385_pump/work/an/fig/q6_zoom.png  240 KB  2026-10-09
r385_pump/work/an/o1_overview.py  2 KB  2026-10-09
r385_pump/work/an/o2_axis.py  4 KB  2026-10-09
r385_pump/work/an/o3_stack.py  8 KB  2026-10-09
r385_pump/work/an/o4_seams.py  2 KB  2026-10-09
r385_pump/work/an/o5_meridians.py  3 KB  2026-10-09
r385_pump/work/an/o6_frameG0.py  5 KB  2026-10-09
r385_pump/work/an/outer_stack.json  11 KB  2026-10-09
r385_pump/work/an/p0_contact.py  1 KB  2026-10-09
r385_pump/work/an/p1_part.py  3 KB  2026-10-09
r385_pump/work/an/q1_hs01_holes.py  2 KB  2026-10-09
r385_pump/work/an/q2_keyed_lug.py  1 KB  2026-10-09
r385_pump/work/an/q3_outer_passes.py  3 KB  2026-10-09
r385_pump/work/an/q4_stack_detail.py  2 KB  2026-10-09
r385_pump/work/an/q5_lib.py  0 KB  2026-10-09
r385_pump/work/an/q5_stack_overlay.py  3 KB  2026-10-09
r385_pump/work/an/q6_zoom.py  2 KB  2026-10-09
r385_pump/work/an/q7_heads.py  3 KB  2026-10-09
r385_pump/work/an/qa/ASSY_outer.json  3 KB  2026-10-09
r385_pump/work/an/qa/DR01.json  3 KB  2026-10-09
r385_pump/work/an/qa/DR01_t2.json  3 KB  2026-10-09
r385_pump/work/an/qa/DR02_r0.json  3 KB  2026-10-09
r385_pump/work/an/qa/DR02_r0.png  296 KB  2026-10-09
r385_pump/work/an/qa/DR02_r180.json  3 KB  2026-10-09
r385_pump/work/an/qa/DR02_t2.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS01_t2.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS02_t2.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS02_t3.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS02_t4.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS03_t3.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS04_t4.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS04_t5.json  3 KB  2026-10-09
r385_pump/work/an/qa/HS04_t6.json  3 KB  2026-10-09
r385_pump/work/an/qa/MT01.json  3 KB  2026-10-09
r385_pump/work/an/qa/MT01_t2.json  3 KB  2026-10-09
r385_pump/work/an/qa/SL01_t2.json  3 KB  2026-10-09
r385_pump/work/an/qa/SL03_t5.json  3 KB  2026-10-09
r385_pump/work/an/qa/SL04_t5.json  3 KB  2026-10-09
r385_pump/work/an/qa/SL04_t5.png  241 KB  2026-10-09
r385_pump/work/an/qa_dev.py  9 KB  2026-10-09
r385_pump/work/an/qa_step.py  1 KB  2026-10-09
r385_pump/work/an/r385lib.py  10 KB  2026-10-09
r385_pump/work/asm/R385-AS00_ASSY.log  26 KB  2026-10-09
r385_pump/work/asm/asm_build.py  10 KB  2026-10-09
r385_pump/work/cfd/README.md  17 KB  2026-10-09
r385_pump/work/cfd/cases/stage1_single_chamber/case_params.json  1 KB  2026-10-09
r385_pump/work/cfd/fields/m_c025/fields_run.txt  0 KB  2026-10-09
r385_pump/work/cfd/fields/m_c050/fields_run.txt  0 KB  2026-10-09
r385_pump/work/cfd/fields/m_c100/fields_run.txt  0 KB  2026-10-09
r385_pump/work/cfd/fields/p_n5000_dp030/fields_run.txt  0 KB  2026-10-09
r385_pump/work/cfd/fields/s_c050_sst/fields_run.txt  0 KB  2026-10-09
r385_pump/work/cfd/tools/wsl_dbg.sh  0 KB  2026-10-09
r385_pump/work/cfd/tools/wsl_fields_progress.sh  0 KB  2026-10-09
r385_pump/work/cfd/tools/wsl_ps.sh  1 KB  2026-10-09
r385_pump/work/cfd/tools/wsl_repo_test.sh  1 KB  2026-10-09
r385_pump/work/ctrl/ctrl_build.py  2 KB  2026-10-09
r385_pump/work/ctrl/link_test.py  3 KB  2026-10-09
r385_pump/work/docs/work/asm_build.json  19 KB  2026-10-09
r385_pump/work/docs/work/bom.json  18 KB  2026-10-09
r385_pump/work/docs/work/explode_check.json  2 KB  2026-10-09
r385_pump/work/docs/work/hlr_cutaway.json  44 KB  2026-10-09
r385_pump/work/docs/work/hlr_exploded.json  170 KB  2026-10-09
r385_pump/work/docs/work/hlr_front.json  22 KB  2026-10-09
r385_pump/work/docs/work/hlr_head.json  26 KB  2026-10-09
r385_pump/work/docs/work/hlr_iso.json  39 KB  2026-10-09
r385_pump/work/docs/work/hlr_section.json  64 KB  2026-10-09
r385_pump/work/docs/work/hlr_top.json  26 KB  2026-10-09
r385_pump/work/docs/work/hlr_valves.json  25 KB  2026-10-09
r385_pump/work/docs/work/job_cutaway.json  3 KB  2026-10-09
r385_pump/work/docs/work/job_exploded.json  6 KB  2026-10-09
r385_pump/work/docs/work/job_front.json  4 KB  2026-10-09
r385_pump/work/docs/work/job_head.json  4 KB  2026-10-09
r385_pump/work/docs/work/job_iso.json  4 KB  2026-10-09
r385_pump/work/docs/work/job_section.json  3 KB  2026-10-09
r385_pump/work/docs/work/job_top.json  4 KB  2026-10-09
r385_pump/work/docs/work/job_valves.json  1 KB  2026-10-09
r385_pump/work/docs/work/measure.json  5 KB  2026-10-09
r385_pump/work/docs/work/measure_0615.json  5 KB  2026-10-09
r385_pump/work/docs/work/measure_log.txt  3 KB  2026-10-09
r385_pump/work/docs/work/page1_dims.json  0 KB  2026-10-09
r385_pump/work/docs/work/parts.json  7 KB  2026-10-09
r385_pump/work/docs/work/parts_0615.json  7 KB  2026-10-09
r385_pump/work/docs/work/section_y0.json  11 KB  2026-10-09
r385_pump/work/docs/work/views.json  7 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/README.md  19 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/REPO_COMPARISON.md  11 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/SIMULATION_PLAN.md  18 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/cases/stage1_single_chamber/case_params.json  1 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/cases/stage1_study/fig/fields_summary.json  5 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/cases/stage1_study/report_notes.json  1 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/cases/stage1_study/run_log.json  2 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/cases/stage1_study/study_results.json  76 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/cases/stage1_study/sweep_table.json  19 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/tools/extract_fluid.py  12 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/tools/foamlib_smoke.py  5 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/tools/post_stage1.py  11 KB  2026-10-09
r385_pump/work/oguz-cfd/cfd/tools/study_stage1.py  9 KB  2026-10-09
r385_pump/work/oguz-cfd/sessions/G_STATUS.md  10 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/c1_geometry.py  7 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/c2_kinematics.py  8 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/c3_displacement.py  16 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/c5_lumped.py  13 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/c6_motor_qh.py  17 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/common.py  8 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/inputs/asm_build.json  18 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/inputs/ctrl_build.json  3 KB  2026-10-09
r385_pump/work/oguz-cfd/theory/calc/inputs/ctrl_params.json  11 KB  2026-10-09
r385_pump/work/parts/B_common/bom_dump.py  0 KB  2026-10-09
r385_pump/work/parts/B_common/dev.py  7 KB  2026-10-09
r385_pump/work/parts/B_common/hs_fit.py  2 KB  2026-10-09
r385_pump/work/parts/B_common/nxlib/geo.py  4 KB  2026-10-07
r385_pump/work/parts/B_common/nxlib/ps.py  14 KB  2026-10-08
r385_pump/work/parts/B_common/nxlib/rj.py  6 KB  2026-10-09
r385_pump/work/parts/B_common/overlap.py  2 KB  2026-10-09
r385_pump/work/parts/B_common/rb.py  22 KB  2026-10-09
r385_pump/work/parts/B_common/rebuild_all.ps1  1 KB  2026-10-09
r385_pump/work/parts/B_common/report.py  5 KB  2026-10-09
r385_pump/work/parts/B_common/rev_a_turn.py  1 KB  2026-10-09
r385_pump/work/parts/B_common/run.ps1  1 KB  2026-10-09
r385_pump/work/parts/B_common/s0_inventory.py  2 KB  2026-10-09
r385_pump/work/parts/B_common/s1_census.py  5 KB  2026-10-09
r385_pump/work/parts/B_common/secfig.py  2 KB  2026-10-09
r385_pump/work/parts/B_common/shade.py  2 KB  2026-10-09
r385_pump/work/parts/B_common/show.py  1 KB  2026-10-09
r385_pump/work/parts/B_common/view.py  2 KB  2026-10-09
r385_pump/work/parts/DR01/R385-DR01_ECCENTRIC_build.json  7 KB  2026-10-09
r385_pump/work/parts/DR01/build.py  9 KB  2026-10-09
r385_pump/work/parts/DR01/dev_dr01.py  1 KB  2026-10-09
r385_pump/work/parts/DR01/dr01.py  9 KB  2026-10-09
r385_pump/work/parts/DR01/out/R385-DR01_ECCENTRIC.log  17 KB  2026-10-09
r385_pump/work/parts/DR01/qa/align.json  1 KB  2026-10-09
r385_pump/work/parts/DR01/qa/dev.json  4 KB  2026-10-09
r385_pump/work/parts/DR01/qa/measure.json  4 KB  2026-10-09
r385_pump/work/parts/DR01/qa/s0_inventory.json  2 KB  2026-10-09
r385_pump/work/parts/DR01/qa/s1_census.json  3 KB  2026-10-09
r385_pump/work/parts/DR01/report_notes.md  2 KB  2026-10-09
r385_pump/work/parts/DR02/R385-DR02_WOBBLE_build.json  8 KB  2026-10-09
r385_pump/work/parts/DR02/build.py  11 KB  2026-10-09
r385_pump/work/parts/DR02/dev_dr02.py  2 KB  2026-10-09
r385_pump/work/parts/DR02/dr02.py  9 KB  2026-10-09
r385_pump/work/parts/DR02/dr02_profile.py  3 KB  2026-10-09
r385_pump/work/parts/DR02/out/R385-DR02_WOBBLE.log  14 KB  2026-10-09
r385_pump/work/parts/DR02/qa/align.json  1 KB  2026-10-09
r385_pump/work/parts/DR02/qa/dev.json  6 KB  2026-10-09
r385_pump/work/parts/DR02/qa/measure.json  7 KB  2026-10-09
r385_pump/work/parts/DR02/qa/profile.json  3 KB  2026-10-09
r385_pump/work/parts/DR02/qa/s0_inventory.json  2 KB  2026-10-09
r385_pump/work/parts/DR02/qa/s1_census.json  2 KB  2026-10-09
r385_pump/work/parts/DR02/report_notes.md  1 KB  2026-10-09
r385_pump/work/parts/FS/R385-FS01_SCR-MOTOR.log  4 KB  2026-10-09
r385_pump/work/parts/FS/R385-FS02_SCR-BODY.log  4 KB  2026-10-09
r385_pump/work/parts/FS/fs_build.json  2 KB  2026-10-09
r385_pump/work/parts/FS/fs_build.py  4 KB  2026-10-09
r385_pump/work/parts/HS01/R385-HS01_MOUNT_build.json  8 KB  2026-10-09
r385_pump/work/parts/HS01/build.py  10 KB  2026-10-09
r385_pump/work/parts/HS01/dev_hs01.py  3 KB  2026-10-09
r385_pump/work/parts/HS01/hs01_align.py  4 KB  2026-10-09
r385_pump/work/parts/HS01/hs01_lug.py  2 KB  2026-10-09
r385_pump/work/parts/HS01/hs01_measure.py  4 KB  2026-10-09
r385_pump/work/parts/HS01/out/R385-HS01_MOUNT.log  14 KB  2026-10-09
r385_pump/work/parts/HS01/qa/align.json  1 KB  2026-10-09
r385_pump/work/parts/HS01/qa/dev.json  7 KB  2026-10-09
r385_pump/work/parts/HS01/qa/ear_joint.json  4 KB  2026-10-09
r385_pump/work/parts/HS01/qa/measure.json  8 KB  2026-10-09
r385_pump/work/parts/HS01/qa/s0_inventory.json  1 KB  2026-10-09
r385_pump/work/parts/HS01/qa/s1_census.json  2 KB  2026-10-09
r385_pump/work/parts/HS01/report_notes.md  2 KB  2026-10-09
r385_pump/work/parts/HS02/R385-HS02_FRAME_build.json  11 KB  2026-10-09
r385_pump/work/parts/HS02/build.py  16 KB  2026-10-09
r385_pump/work/parts/HS02/dev_hs02.py  4 KB  2026-10-09
r385_pump/work/parts/HS02/hs02_align.py  3 KB  2026-10-09
r385_pump/work/parts/HS02/hs02_centre.py  1 KB  2026-10-09
r385_pump/work/parts/HS02/hs02_detail.py  3 KB  2026-10-09
r385_pump/work/parts/HS02/hs02_detail2.py  3 KB  2026-10-09
r385_pump/work/parts/HS02/hs02_fence.py  2 KB  2026-10-09
r385_pump/work/parts/HS02/hs02_measure.py  7 KB  2026-10-09
r385_pump/work/parts/HS02/out/R385-HS02_FRAME.log  32 KB  2026-10-09
r385_pump/work/parts/HS02/qa/align.json  1 KB  2026-10-09
r385_pump/work/parts/HS02/qa/align0.json  0 KB  2026-10-09
r385_pump/work/parts/HS02/qa/dev.json  8 KB  2026-10-09
r385_pump/work/parts/HS02/qa/measure.json  17 KB  2026-10-09
r385_pump/work/parts/HS02/qa/s0_inventory.json  2 KB  2026-10-09
r385_pump/work/parts/HS02/qa/s1_census.json  3 KB  2026-10-09
r385_pump/work/parts/HS02/report_notes.md  3 KB  2026-10-09
r385_pump/work/parts/HS03/build.py  25 KB  2026-10-09
r385_pump/work/parts/HS03/out/R385-HS03_VALVE-PLATE.log  9 KB  2026-10-09
r385_pump/work/parts/HS03/out/build.json  20 KB  2026-10-09
r385_pump/work/parts/HS03/out/dev.json  9 KB  2026-10-09
r385_pump/work/parts/HS04/build.py  24 KB  2026-10-09
r385_pump/work/parts/HS04/out/R385-HS04_HEAD.log  23 KB  2026-10-09
r385_pump/work/parts/HS04/out/build.json  19 KB  2026-10-09
r385_pump/work/parts/HS04/out/dev.json  12 KB  2026-10-09
r385_pump/work/parts/MT01/R385-MT01_MOTOR_build.json  8 KB  2026-10-09
r385_pump/work/parts/MT01/build.py  10 KB  2026-10-09
r385_pump/work/parts/MT01/dev_mt01.py  2 KB  2026-10-09
r385_pump/work/parts/MT01/mt01_align.py  2 KB  2026-10-09
r385_pump/work/parts/MT01/mt01_detail.py  3 KB  2026-10-09
r385_pump/work/parts/MT01/mt01_measure.py  6 KB  2026-10-09
r385_pump/work/parts/MT01/out/R385-MT01_MOTOR.log  18 KB  2026-10-09
r385_pump/work/parts/MT01/qa/align.json  1 KB  2026-10-09
r385_pump/work/parts/MT01/qa/align0.json  0 KB  2026-10-09
r385_pump/work/parts/MT01/qa/detail.json  5 KB  2026-10-09
r385_pump/work/parts/MT01/qa/dev.json  6 KB  2026-10-09
r385_pump/work/parts/MT01/qa/measure.json  6 KB  2026-10-09
r385_pump/work/parts/MT01/qa/s0_inventory.json  1 KB  2026-10-09
r385_pump/work/parts/MT01/qa/s1_census.json  2 KB  2026-10-09
r385_pump/work/parts/MT01/report_notes.md  1 KB  2026-10-09
r385_pump/work/parts/SL01/R385-SL01_DIAPHRAGM_build.json  7 KB  2026-10-09
r385_pump/work/parts/SL01/build.py  8 KB  2026-10-09
r385_pump/work/parts/SL01/dev_sl01.py  2 KB  2026-10-09
r385_pump/work/parts/SL01/out/R385-SL01_DIAPHRAGM.log  9 KB  2026-10-09
r385_pump/work/parts/SL01/qa/align.json  1 KB  2026-10-09
r385_pump/work/parts/SL01/qa/dev.json  6 KB  2026-10-09
r385_pump/work/parts/SL01/qa/measure.json  10 KB  2026-10-09
r385_pump/work/parts/SL01/qa/s0_inventory.json  1 KB  2026-10-09
r385_pump/work/parts/SL01/qa/s1_census.json  3 KB  2026-10-09
r385_pump/work/parts/SL01/report_notes.md  1 KB  2026-10-09
r385_pump/work/parts/SL01/sl01.py  10 KB  2026-10-09
r385_pump/work/parts/SL02/build.py  5 KB  2026-10-09
r385_pump/work/parts/SL02/out/R385-SL02_VALVE-IN.log  8 KB  2026-10-09
r385_pump/work/parts/SL02/out/build.json  5 KB  2026-10-09
r385_pump/work/parts/SL03/build.py  6 KB  2026-10-09
r385_pump/work/parts/SL03/out/R385-SL03_VALVE-OUT.log  4 KB  2026-10-09
r385_pump/work/parts/SL03/out/build.json  6 KB  2026-10-09
r385_pump/work/parts/SL03/out/dev.json  4 KB  2026-10-09
r385_pump/work/parts/SL04/build.py  3 KB  2026-10-09
r385_pump/work/parts/SL04/out/R385-SL04_GASKET.log  4 KB  2026-10-09
r385_pump/work/parts/SL04/out/build.json  3 KB  2026-10-09
r385_pump/work/parts/SL04/out/dev.json  3 KB  2026-10-09
r385_pump/work/parts/_C_an/a_flat.py  3 KB  2026-10-09
r385_pump/work/parts/_C_an/a_hs03.py  7 KB  2026-10-09
r385_pump/work/parts/_C_an/a_hs04.py  8 KB  2026-10-09
r385_pump/work/parts/_C_an/bom_dump.py  0 KB  2026-10-09
r385_pump/work/parts/_C_an/cc.py  11 KB  2026-10-09
r385_pump/work/parts/_C_an/dev_c.py  17 KB  2026-10-09
r385_pump/work/parts/_C_an/m_ears_fit.py  4 KB  2026-10-09
r385_pump/work/parts/_C_an/m_flat.py  11 KB  2026-10-09
r385_pump/work/parts/_C_an/m_hs03.py  8 KB  2026-10-09
r385_pump/work/parts/_C_an/m_hs03_b.py  9 KB  2026-10-09
r385_pump/work/parts/_C_an/m_hs03_c.py  8 KB  2026-10-09
r385_pump/work/parts/_C_an/m_hs04.py  12 KB  2026-10-09
r385_pump/work/parts/_C_an/q_hs04_throat.py  3 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/a_SL03_level.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/a_SL04_level.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/a_hs03.json  2 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/a_hs04.json  3 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/a_hs04_level.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/a_sl03.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/a_sl04.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_ears_fit.json  2 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_ears_fit.log  4 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs03_a.json  16 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs03_a.log  7 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs03_b.json  5 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs03_b.log  6 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs03_c.json  4 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs03_c.log  3 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs04.json  24 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_hs04.log  11 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_sl03.json  6 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_sl03.log  3 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_sl04.json  3 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/m_sl04.log  3 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/s0_stat.json  2 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/s1_HS03_pca.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/s1_HS04_pca.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/s1_SL03_pca.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/s1_SL04_pca.json  0 KB  2026-10-09
r385_pump/work/parts/_C_an/qa/v_ears.log  1 KB  2026-10-09
r385_pump/work/parts/_C_an/run.ps1  1 KB  2026-10-09
r385_pump/work/parts/_C_an/s0_stat.py  1 KB  2026-10-09
r385_pump/work/parts/_C_an/s1_look.py  1 KB  2026-10-09
r385_pump/work/parts/_C_an/s2_explore.py  2 KB  2026-10-09
r385_pump/work/parts/_C_an/tools.py  9 KB  2026-10-09
r385_pump/work/parts/_C_an/v_ears.py  3 KB  2026-10-09
r385_pump/work/parts/_C_an/v_hs02_check.py  1 KB  2026-10-09
r385_pump/work/parts/_C_an/v_hs03.py  1 KB  2026-10-09
r385_pump/work/parts/_C_an/v_hs03_lobes.py  3 KB  2026-10-09
r385_pump/work/parts/_C_an/v_hs03_seat.py  2 KB  2026-10-09
r385_pump/work/parts/_C_an/v_outer_check.py  1 KB  2026-10-09
r385_pump/work/print/nx_out/printability_raw.json  73 KB  2026-10-09
r385_pump/work/print/nx_out/validation_delivered_A1_first.json  30 KB  2026-10-09
r385_pump/work/print/nx_out/validation_raw.json  47 KB  2026-10-09
r385_pump/work/print/probe/check_probe.py  1 KB  2026-10-09
r385_pump/work/print/probe/dr01_pairs.py  2 KB  2026-10-09
r385_pump/work/print/probe/dr01_top.py  3 KB  2026-10-09
r385_pump/work/print/probe/dump_nx.py  1 KB  2026-10-09
r385_pump/work/print/probe/explore.py  1 KB  2026-10-09
r385_pump/work/print/probe/hs04_groove.py  1 KB  2026-10-09
r385_pump/work/print/probe/hs04_sliver.py  2 KB  2026-10-09
r385_pump/work/print/probe/look.py  2 KB  2026-10-09
r385_pump/work/print/probe/probe.json  14 KB  2026-10-09
r385_pump/work/print/probe/probe_stl.py  4 KB  2026-10-09
r385_pump/work/print/probe/sections.py  4 KB  2026-10-09
r385_pump/work/scan/outer_G0_transform.json  0 KB  2026-10-09
```

### ulka_pump (nx_re_projects_20261105_part4.zip)
```
ulka_pump/drive_source/CLAUDE.md  10 KB  2026-10-16
ulka_pump/drive_source/EP5-DR01 Armatur/plrjY_Pytl_jlcH_ZGEN/result/Mesh.ply  5.7 MB  2026-10-16
ulka_pump/drive_source/EP5-DR01 Armatur/s1UT26S_6i4i5u_r0duQj_5FPDdn/result/model.ply  525 KB  2026-10-16
ulka_pump/drive_source/EP5-DR01 Armatur/thumbnail.png  7 KB  2026-10-16
ulka_pump/drive_source/EP5-DR02 On yay/sGMGmDd_JiCFFc_PAdxrQ_UrjvLg/result/model.ply  627 KB  2026-10-16
ulka_pump/drive_source/EP5-DR02 On yay/thumbnail.png  12 KB  2026-10-16
ulka_pump/drive_source/EP5-DR03 Arka yay/srlHYXT_rpu3ez_IV8H9C_AhkMut/result/model.ply  819 KB  2026-10-16
ulka_pump/drive_source/EP5-DR03 Arka yay/thumbnail.png  11 KB  2026-10-16
ulka_pump/drive_source/EP5-EM01 Bobin/sLMUqPH_4mO0Mk_QZacHv_qYFdFx/result/model.ply  4.3 MB  2026-10-16
ulka_pump/drive_source/EP5-EM01 Bobin/thumbnail.png  11 KB  2026-10-16
ulka_pump/drive_source/EP5-EM02 Manyetik Cerceve/sZiRKYm_VsBawH_oOhgE2_OSG7Yc/result/model.ply  4.3 MB  2026-10-16
ulka_pump/drive_source/EP5-EM02 Manyetik Cerceve/thumbnail.png  9 KB  2026-10-16
ulka_pump/drive_source/EP5-EM03 Aki burcu/srTNIc0_HnN3f9_tG1q4B_hV5h9E/result/model.ply  1.3 MB  2026-10-16
ulka_pump/drive_source/EP5-EM03 Aki burcu/thumbnail.png  9 KB  2026-10-16
ulka_pump/drive_source/EP5-HS01 armatur tupu/sGfgC9t_rzsnRV_4Mvn7f_kLRO5B/result/model.ply  1.7 MB  2026-10-16
ulka_pump/drive_source/EP5-HS01 armatur tupu/thumbnail.png  8 KB  2026-10-16
ulka_pump/drive_source/EP5-HS02 Piston silindiri/sq9fVGJ_XMcCab_BU9Iha_R6urKF/result/model.ply  1.3 MB  2026-10-16
ulka_pump/drive_source/EP5-HS02 Piston silindiri/thumbnail.png  8 KB  2026-10-16
ulka_pump/drive_source/EP5-HS03 Cikis Flansi/ssODnCK_1Rg0qx_kuvDOV_CCkDvC/result/model.ply  2.4 MB  2026-10-16
ulka_pump/drive_source/EP5-HS03 Cikis Flansi/svpUU3h_vjgpm6_5vcKSG_Ai7lCo/result/model.ply  2.9 MB  2026-10-16
ulka_pump/drive_source/EP5-HS03 Cikis Flansi/thumbnail.png  8 KB  2026-10-16
ulka_pump/drive_source/EP5-HS04 Plastik ara halka/seBTi3n_2rJTmp_3TrQP3_2ps8qv/result/model.ply  1.5 MB  2026-10-16
ulka_pump/drive_source/EP5-HS04 Plastik ara halka/thumbnail.png  11 KB  2026-10-16
ulka_pump/drive_source/EP5-HS05 Plastik pul + EP5-VL02 Bilya yayi + EP5-VL03 cikis valfi + EP5-VL04/shyL4DH_p9KrpY_Z5PgTO_U1Z8fG/result/model.ply  1.6 MB  2026-10-16
ulka_pump/drive_source/EP5-HS05 Plastik pul + EP5-VL02 Bilya yayi + EP5-VL03 cikis valfi + EP5-VL04/thumbnail.png  15 KB  2026-10-16
ulka_pump/drive_source/EP5-SL04 Piston O-ringi + EP5-VL01 Piston cek valf + EP5-SL01O-ring + EP5-SL02O-ring + EP5-SL03O-ring/thumbnail.png  10 KB  2026-10-16
ulka_pump/drive_source/EP5-VL05 Valf kafesi.stl  4.3 MB  2026-10-16
ulka_pump/drive_source/EP5-VL05 Valf kafesi/pjb3S_vTBL_pegR_XyWK/result/Mesh.ply  2.2 MB  2026-10-16
ulka_pump/drive_source/EP5-VL05 Valf kafesi/s0vUO1R_zsN0K3_BMoOSn_i4u3EG/result/Fused.ply  2.4 MB  2026-10-16
ulka_pump/drive_source/EP5-VL05 Valf kafesi/s0vUO1R_zsN0K3_BMoOSn_i4u3EG/result/model.ply  442 KB  2026-10-16
ulka_pump/drive_source/EP5-VL05 Valf kafesi/sWyuxRW_YmPlEr_o45qEf_9rRxPs/result/model.ply  1.4 MB  2026-10-16
ulka_pump/drive_source/EP5-VL05 Valf kafesi/thumbnail.png  9 KB  2026-10-16
ulka_pump/drive_source/E_high_pressure.pdf  290 KB  2026-10-16
ulka_pump/drive_source/ULKA_INTERFACES.md  25 KB  2026-10-17
ulka_pump/drive_source/cad/EP5-DR01_ARMATURE-PISTON_REPORT.md  5 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-DR02_SPRING-FRONT_REPORT.md  5 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-DR03_SPRING-REAR_REPORT.md  5 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-EM01_COIL_REPORT.md  12 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-EM02_FRAME_REPORT.md  7 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-EM03_FLUX-SLEEVE_REPORT.md  4 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-FS01_REPORT.md  1 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-HS01_INLET-BODY_REPORT.md  5 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-HS02_CYLINDER_REPORT.md  6 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-HS03_OUTLET-FLANGE_REPORT.md  7 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-HS04_SPACER-RING_REPORT.md  4 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-HS05_WASHER_REPORT.md  2 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-SL01_ORING-L_REPORT.md  2 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-SL02_ORING-M_REPORT.md  2 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-SL03_ORING-S_REPORT.md  2 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-SL04_ORING-PISTON_REPORT.md  2 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-VL01_BALL_REPORT.md  2 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-VL02_SPRING-BALL_REPORT.md  3 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-VL03_VALVE-PLUG_REPORT.md  3 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-VL04_SPRING-VALVE_REPORT.md  3 KB  2026-10-16
ulka_pump/drive_source/cad/EP5-VL05_VALVE-CAGE_REPORT.md  3 KB  2026-10-16
ulka_pump/drive_source/cad/assembly/EP5-AS00_REPORT.md  1 KB  2026-10-16
ulka_pump/drive_source/cad/assembly/asm_build.json  12 KB  2026-10-16
ulka_pump/drive_source/cad/assembly/asm_build.py  11 KB  2026-10-16
ulka_pump/drive_source/cfd/SIMULATION_PLAN.md  11 KB  2026-10-16
ulka_pump/drive_source/cr/CR-B-01.md  1 KB  2026-10-16
ulka_pump/drive_source/cr/CR-B-02.md  2 KB  2026-10-16
ulka_pump/drive_source/cr/CR-C-01.md  3 KB  2026-10-16
ulka_pump/drive_source/cr/CR-C-02.md  3 KB  2026-10-16
ulka_pump/drive_source/cr/CR-D-01.md  3 KB  2026-10-16
ulka_pump/drive_source/cr/CR-D-02.md  2 KB  2026-10-16
ulka_pump/drive_source/cr/CR-D-03.md  2 KB  2026-10-16
ulka_pump/drive_source/cr/CR-E-01.md  2 KB  2026-10-17
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.01.jpeg  220 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.02 (1).jpeg  156 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.02 (2).jpeg  182 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.02 (3).jpeg  194 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.02.jpeg  159 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.03 (1).jpeg  141 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.03 (2).jpeg  145 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.03.jpeg  224 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.04.jpeg  165 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.05 (1).jpeg  219 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.05.jpeg  157 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.06 (1).jpeg  162 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.06 (2).jpeg  164 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.06 (3).jpeg  166 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.06.jpeg  159 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.07 (1).jpeg  162 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.07 (2).jpeg  164 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.07.jpeg  203 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.08 (1).jpeg  257 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.08 (2).jpeg  274 KB  2026-10-16
ulka_pump/drive_source/kurgu input/WhatsApp Image 2026-10-16 at 15.24.08.jpeg  219 KB  2026-10-16
ulka_pump/drive_source/sessions/A_MEASURED.md  9 KB  2026-10-16
ulka_pump/drive_source/sessions/A_OLCUM_ONERISI.md  3 KB  2026-10-17
ulka_pump/drive_source/sessions/A_QA.md  12 KB  2026-10-16
ulka_pump/drive_source/sessions/A_STATUS.md  4 KB  2026-10-17
ulka_pump/drive_source/sessions/B_MEASURED.md  10 KB  2026-10-16
ulka_pump/drive_source/sessions/B_STATUS.md  2 KB  2026-10-16
ulka_pump/drive_source/sessions/C_MEASURED.md  13 KB  2026-10-16
ulka_pump/drive_source/sessions/C_STATUS.md  3 KB  2026-10-16
ulka_pump/drive_source/sessions/D_MEASURED.md  12 KB  2026-10-16
ulka_pump/drive_source/sessions/D_STATUS.md  3 KB  2026-10-16
ulka_pump/drive_source/sessions/E_STATUS.md  2 KB  2026-10-17
ulka_pump/drive_source/theory/ULKA_DESIGN_PROCESS.md  11 KB  2026-10-17
ulka_pump/drive_source/theory/ULKA_THEORY_REPORT.md  40 KB  2026-10-17
ulka_pump/drive_source/theory/calc/build_report.py  9 KB  2026-10-16
ulka_pump/drive_source/theory/calc/c1_geometry.py  7 KB  2026-10-17
ulka_pump/drive_source/theory/calc/c2_magnetics.py  18 KB  2026-10-17
ulka_pump/drive_source/theory/calc/c3_model.py  20 KB  2026-10-17
ulka_pump/drive_source/theory/calc/c4_qp.py  7 KB  2026-10-17
ulka_pump/drive_source/theory/calc/c5_losses.py  7 KB  2026-10-17
ulka_pump/drive_source/theory/calc/c6_sensitivity.py  6 KB  2026-10-17
ulka_pump/drive_source/theory/calc/c7_fit.py  5 KB  2026-10-17
ulka_pump/drive_source/theory/calc/common.py  13 KB  2026-10-16
ulka_pump/drive_source/theory/calc/inputs.json  11 KB  2026-10-16
ulka_pump/drive_source/theory/calc/inputs/ctrl_build.json  5 KB  2026-10-16
ulka_pump/drive_source/theory/calc/inputs/ctrl_values_py.json  3 KB  2026-10-16
ulka_pump/drive_source/theory/calc/out/c2_log.txt  3 KB  2026-10-16
ulka_pump/drive_source/theory/calc/out/c4_log.txt  18 KB  2026-10-17
ulka_pump/drive_source/theory/calc/out/c6_log.txt  3 KB  2026-10-17
ulka_pump/drive_source/theory/calc/out/c7_log.txt  26 KB  2026-10-17
ulka_pump/drive_source/theory/calc/out/fit.json  23 KB  2026-10-17
ulka_pump/drive_source/theory/calc/out/geometry.json  4 KB  2026-10-17
ulka_pump/drive_source/theory/calc/out/losses.json  10 KB  2026-10-17
ulka_pump/drive_source/theory/calc/out/magnetics.json  1 KB  2026-10-16
ulka_pump/drive_source/theory/calc/out/qp.json  20 KB  2026-10-17
ulka_pump/drive_source/theory/calc/out/sensitivity.json  14 KB  2026-10-17
ulka_pump/drive_source/theory/calc/run_all.py  2 KB  2026-10-17
ulka_pump/drive_source/theory/fig/d1_hacim_dokumu.png  67 KB  2026-10-17
ulka_pump/drive_source/theory/fig/f1_ayar.png  103 KB  2026-10-17
ulka_pump/drive_source/theory/fig/l1_cevrim.png  201 KB  2026-10-17
ulka_pump/drive_source/theory/fig/m1_alan.png  187 KB  2026-10-16
ulka_pump/drive_source/theory/fig/m2_kuvvet_aki.png  177 KB  2026-10-16
ulka_pump/drive_source/theory/fig/q1_qp.png  74 KB  2026-10-17
ulka_pump/drive_source/theory/fig/q2_guc_strok.png  53 KB  2026-10-17
ulka_pump/drive_source/theory/fig/s1_duyarlilik.png  95 KB  2026-10-17
ulka_pump/drive_source/theory/fig/v1_valf.png  41 KB  2026-10-17
ulka_pump/transcripts/10ee51b0-aca3-4c97-81e6-1cf43e417574.jsonl  2.9 MB  
ulka_pump/transcripts/136cb46e-e1f4-4036-8670-cc4f129b1641.jsonl  2.5 MB  
ulka_pump/transcripts/3b5db2ce-db29-450a-a69e-d5b72703fbb0.jsonl  2.9 MB  
ulka_pump/transcripts/bcea8ef0-e1c2-446b-a3ac-946c5b1c03a9.jsonl  3.0 MB  
ulka_pump/transcripts/e4e799fc-342d-4a7b-8226-88448721a5cd.jsonl  3.4 MB  
ulka_pump/work/an/a01_inventory.json  8 KB  2026-10-16
ulka_pump/work/an/a01_inventory.py  2 KB  2026-10-16
ulka_pump/work/an/a02_views.py  1 KB  2026-10-16
ulka_pump/work/an/a03_axes.json  10 KB  2026-10-16
ulka_pump/work/an/a03_axes.py  2 KB  2026-10-16
ulka_pump/work/an/a04_profile.py  2 KB  2026-10-16
ulka_pump/work/an/a05_multi.py  1 KB  2026-10-16
ulka_pump/work/an/a06_em02.py  1 KB  2026-10-16
ulka_pump/work/an/a07_em02holes.py  3 KB  2026-10-16
ulka_pump/work/an/a08_loops.py  1 KB  2026-10-16
ulka_pump/work/an/a09_levels.py  1 KB  2026-10-16
ulka_pump/work/an/a10_rings.py  1 KB  2026-10-16
ulka_pump/work/an/a11_noise.json  2 KB  2026-10-16
ulka_pump/work/an/a11_noise.py  3 KB  2026-10-16
ulka_pump/work/an/a12_hs02flat.py  1 KB  2026-10-16
ulka_pump/work/an/fig/p_DR01.png  63 KB  2026-10-16
ulka_pump/work/an/fig/p_DR01.txt  3 KB  2026-10-16
ulka_pump/work/an/fig/p_EM01.txt  4 KB  2026-10-16
ulka_pump/work/an/fig/p_EM03.txt  1 KB  2026-10-16
ulka_pump/work/an/fig/p_HS01.png  40 KB  2026-10-16
ulka_pump/work/an/fig/p_HS01.txt  4 KB  2026-10-16
ulka_pump/work/an/fig/p_HS01_all.png  63 KB  2026-10-16
ulka_pump/work/an/fig/p_HS01_all.txt  6 KB  2026-10-16
ulka_pump/work/an/fig/p_HS02.png  86 KB  2026-10-16
ulka_pump/work/an/fig/p_HS02.txt  3 KB  2026-10-16
ulka_pump/work/an/fig/p_HS03.png  270 KB  2026-10-16
ulka_pump/work/an/fig/p_HS03.txt  2 KB  2026-10-16
ulka_pump/work/an/fig/p_HS04.png  250 KB  2026-10-16
ulka_pump/work/an/fig/p_HS04.txt  1 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-DR01.png  183 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-DR03.png  192 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-EM03.png  253 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-HS01.png  213 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-HS02.png  292 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-HS04.png  205 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-HS05.png  270 KB  2026-10-16
ulka_pump/work/an/fig/v_EP5-SL04.png  208 KB  2026-10-16
ulka_pump/work/an/nxrun_a.sh  1 KB  2026-10-16
ulka_pump/work/an/occ_common.py  1 KB  2026-10-16
ulka_pump/work/an/qa/DR01_qa.json  6 KB  2026-10-16
ulka_pump/work/an/qa/DR02_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/DR03_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/DR03_r385.json  3 KB  2026-10-16
ulka_pump/work/an/qa/EM01_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/EM02_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/EM03_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/EM03_s1_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/EM03_s2_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/HS01_qa.json  6 KB  2026-10-16
ulka_pump/work/an/qa/HS02_qa.json  5 KB  2026-10-16
ulka_pump/work/an/qa/HS03_qa.json  9 KB  2026-10-16
ulka_pump/work/an/qa/HS04_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/HS05_qa.json  4 KB  2026-10-16
ulka_pump/work/an/qa/SL01_qa.json  3 KB  2026-10-16
ulka_pump/work/an/qa/SL01_qa.png  172 KB  2026-10-16
ulka_pump/work/an/qa/SL02_qa.json  3 KB  2026-10-16
ulka_pump/work/an/qa/SL02_qa.png  209 KB  2026-10-16
ulka_pump/work/an/qa/SL03_qa.json  3 KB  2026-10-16
ulka_pump/work/an/qa/SL03_qa.png  131 KB  2026-10-16
ulka_pump/work/an/qa/SL04_qa.json  3 KB  2026-10-16
ulka_pump/work/an/qa/SL04_qa.png  285 KB  2026-10-16
ulka_pump/work/an/qa/VL01_qa.json  1 KB  2026-10-16
ulka_pump/work/an/qa/VL02_qa.json  2 KB  2026-10-16
ulka_pump/work/an/qa/VL03_qa.json  3 KB  2026-10-16
ulka_pump/work/an/qa/VL04_qa.json  2 KB  2026-10-16
ulka_pump/work/an/qa/VL05_qa.json  2 KB  2026-10-16
ulka_pump/work/an/qa/specs/DR01.json  1 KB  2026-10-16
ulka_pump/work/an/qa/specs/DR02.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/DR03.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/EM01.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/EM02.json  1 KB  2026-10-16
ulka_pump/work/an/qa/specs/EM02_holes.json  1 KB  2026-10-16
ulka_pump/work/an/qa/specs/EM03.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/HS01.json  1 KB  2026-10-16
ulka_pump/work/an/qa/specs/HS02.json  1 KB  2026-10-16
ulka_pump/work/an/qa/specs/HS03.json  1 KB  2026-10-16
ulka_pump/work/an/qa/specs/HS03_holes.json  1 KB  2026-10-16
ulka_pump/work/an/qa/specs/HS04.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/HS05.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/SL01.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/SL02.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/SL03.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/SL04.json  0 KB  2026-10-16
ulka_pump/work/an/qa/specs/VL03.json  0 KB  2026-10-16
ulka_pump/work/an/qa_dev.py  13 KB  2026-10-16
ulka_pump/work/an/qa_dev_r385.py  9 KB  2026-10-16
ulka_pump/work/an/qa_holes.py  2 KB  2026-10-16
ulka_pump/work/an/qa_step.py  1 KB  2026-10-16
ulka_pump/work/an/ulkalib.py  11 KB  2026-10-16
ulka_pump/work/asm/EP5-AS00_ASSY.log  20 KB  2026-10-16
ulka_pump/work/asm/run1.log  0 KB  2026-10-16
ulka_pump/work/asm/run2.log  0 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_build.py  2 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params.json  23 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params_revA.json  22 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params_revB.json  22 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params_revC.json  22 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params_revD.json  23 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params_revE.json  23 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params_revF.json  23 KB  2026-10-16
ulka_pump/work/ctrl/ctrl_params_revG.json  23 KB  2026-10-16
ulka_pump/work/ctrl/interfaces_head.md  11 KB  2026-10-16
ulka_pump/work/ctrl/mk_params.py  14 KB  2026-10-16
ulka_pump/work/ctrl/mk_table.py  1 KB  2026-10-16
ulka_pump/work/ctrl/table.md  13 KB  2026-10-16
ulka_pump/work/parts/C_common/align_ax.py  3 KB  2026-10-16
ulka_pump/work/parts/C_common/dev.py  7 KB  2026-10-16
ulka_pump/work/parts/C_common/dev_spring.py  2 KB  2026-10-16
ulka_pump/work/parts/C_common/look.py  1 KB  2026-10-16
ulka_pump/work/parts/C_common/nxlib/geo.py  4 KB  2026-10-16
ulka_pump/work/parts/C_common/nxlib/ps.py  14 KB  2026-10-16
ulka_pump/work/parts/C_common/nxlib/rj.py  6 KB  2026-10-16
ulka_pump/work/parts/C_common/nxlib/spring_job.py  3 KB  2026-10-16
ulka_pump/work/parts/C_common/nxlib/spring_nx.py  5 KB  2026-10-16
ulka_pump/work/parts/C_common/nxrun.sh  1 KB  2026-10-16
ulka_pump/work/parts/C_common/ovl_rz.py  1 KB  2026-10-16
ulka_pump/work/parts/C_common/ovl_z.py  1 KB  2026-10-16
ulka_pump/work/parts/C_common/probe/helix_probe.py  1 KB  2026-10-16
ulka_pump/work/parts/C_common/probe/out/probe.json  19 KB  2026-10-16
ulka_pump/work/parts/C_common/prof.py  2 KB  2026-10-16
ulka_pump/work/parts/C_common/rb.py  22 KB  2026-10-16
ulka_pump/work/parts/C_common/report.py  5 KB  2026-10-16
ulka_pump/work/parts/C_common/s1_census.py  5 KB  2026-10-16
ulka_pump/work/parts/C_common/secfig.py  2 KB  2026-10-16
ulka_pump/work/parts/C_common/shade.py  2 KB  2026-10-16
ulka_pump/work/parts/C_common/spring1.py  2 KB  2026-10-16
ulka_pump/work/parts/C_common/spring2.py  2 KB  2026-10-16
ulka_pump/work/parts/C_common/spring3.py  1 KB  2026-10-16
ulka_pump/work/parts/C_common/spring_fit.py  3 KB  2026-10-16
ulka_pump/work/parts/C_common/spring_fit2.py  3 KB  2026-10-16
ulka_pump/work/parts/C_common/spring_fit3.py  3 KB  2026-10-16
ulka_pump/work/parts/C_common/spring_realign.py  1 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v10_1.jpg  40 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v11_1.jpg  278 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v11_3.jpg  107 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v1_1.jpg  96 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v2_1.jpg  252 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v3_1.jpg  257 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v4_1.jpg  264 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v4_3.jpg  175 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v4f/crop116.jpg  134 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v4f/sheet96.jpg  245 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v4f/t136.png  290 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v5_1.jpg  78 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v6_1.jpg  57 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v7_1.jpg  88 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v8_1.jpg  89 KB  2026-10-16
ulka_pump/work/parts/C_common/vid/v9_1.jpg  50 KB  2026-10-16
ulka_pump/work/parts/DR01/EP5-DR01_ARMATURE-PISTON_build.json  5 KB  2026-10-16
ulka_pump/work/parts/DR01/build.py  7 KB  2026-10-16
ulka_pump/work/parts/DR01/dev_dr01.py  1 KB  2026-10-16
ulka_pump/work/parts/DR01/dry/EP5-DR01_ARMATURE-PISTON.log  13 KB  2026-10-16
ulka_pump/work/parts/DR01/dry/build.json  6 KB  2026-10-16
ulka_pump/work/parts/DR01/fig/collar_z.png  98 KB  2026-10-16
ulka_pump/work/parts/DR01/fig/look.png  259 KB  2026-10-16
ulka_pump/work/parts/DR01/fig/ovl_win.png  45 KB  2026-10-16
ulka_pump/work/parts/DR01/fig/prof_-21.0638_25.581.png  49 KB  2026-10-16
ulka_pump/work/parts/DR01/fig/prof_-21.5_-14.png  75 KB  2026-10-16
ulka_pump/work/parts/DR01/fig/prof_-2_10.png  106 KB  2026-10-16
ulka_pump/work/parts/DR01/fig/prof_19_26.png  71 KB  2026-10-16
ulka_pump/work/parts/DR01/out/EP5-DR01_ARMATURE-PISTON.log  4 KB  2026-10-16
ulka_pump/work/parts/DR01/qa/align.json  1 KB  2026-10-16
ulka_pump/work/parts/DR01/qa/dev.json  4 KB  2026-10-16
ulka_pump/work/parts/DR01/qa/dry.json  4 KB  2026-10-16
ulka_pump/work/parts/DR01/qa/s1_census.json  2 KB  2026-10-16
ulka_pump/work/parts/DR01/report_notes.md  2 KB  2026-10-16
ulka_pump/work/parts/DR02/EP5-DR02_SPRING-FRONT_build.json  5 KB  2026-10-16
ulka_pump/work/parts/DR02/build.py  2 KB  2026-10-16
ulka_pump/work/parts/DR02/fig/helix_u_z.png  12 KB  2026-10-16
ulka_pump/work/parts/DR02/fig/look.png  78 KB  2026-10-16
ulka_pump/work/parts/DR02/fig/wire_sections.png  37 KB  2026-10-16
ulka_pump/work/parts/DR02/out/EP5-DR02_SPRING-FRONT.log  9 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/align.json  1 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/dev_pose_dev.json  0 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/helix_fit.json  0 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/helix_u_z.txt  3 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/pre.json  3 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/s1_census.json  5 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/spring_fit2.json  0 KB  2026-10-16
ulka_pump/work/parts/DR02/qa/spring_fit3_dtrue.json  0 KB  2026-10-16
ulka_pump/work/parts/DR02/report_notes.md  2 KB  2026-10-16
ulka_pump/work/parts/DR03/EP5-DR03_SPRING-REAR_build.json  5 KB  2026-10-16
ulka_pump/work/parts/DR03/build.py  2 KB  2026-10-16
ulka_pump/work/parts/DR03/dry/EP5-DR03_SPRING-REAR.log  4 KB  2026-10-16
ulka_pump/work/parts/DR03/dry/build.json  5 KB  2026-10-16
ulka_pump/work/parts/DR03/fig/helix_u_z.png  12 KB  2026-10-16
ulka_pump/work/parts/DR03/fig/look.png  98 KB  2026-10-16
ulka_pump/work/parts/DR03/fig/wire_sections.png  33 KB  2026-10-16
ulka_pump/work/parts/DR03/out/EP5-DR03_SPRING-REAR.log  17 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/align.json  1 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/dev_pose_dev.json  0 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/dev_pose_dry.json  0 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/dry.json  3 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/helix_fit.json  0 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/helix_u_z.txt  4 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/pre.json  3 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/s1_census.json  4 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/spring_fit2.json  0 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/spring_fit2_dtrue.json  0 KB  2026-10-16
ulka_pump/work/parts/DR03/qa/spring_fit3_dtrue.json  0 KB  2026-10-16
ulka_pump/work/parts/DR03/report_notes.md  2 KB  2026-10-16
ulka_pump/work/parts/D_an/C1_plane.json  0 KB  2026-10-16
ulka_pump/work/parts/D_an/C2_plane.json  0 KB  2026-10-16
ulka_pump/work/parts/D_an/D_scan_index.json  6 KB  2026-10-16
ulka_pump/work/parts/D_an/HS02_T.json  1 KB  2026-10-16
ulka_pump/work/parts/D_an/HS02_axis.json  0 KB  2026-10-16
ulka_pump/work/parts/D_an/HS02_meas.json  2 KB  2026-10-16
ulka_pump/work/parts/D_an/HS03_T.json  1 KB  2026-10-16
ulka_pump/work/parts/D_an/HS03_axis.json  0 KB  2026-10-16
ulka_pump/work/parts/D_an/HS03_meas.json  2 KB  2026-10-16
ulka_pump/work/parts/D_an/VL05_plane.json  0 KB  2026-10-16
ulka_pump/work/parts/D_an/al_hs02.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/al_hs02b.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/al_hs03.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/axis.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/cfit.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/fig/C1_A.png  282 KB  2026-10-16
ulka_pump/work/parts/D_an/fig/HS03_pockets.png  76 KB  2026-10-16
ulka_pump/work/parts/D_an/fin_hs02.py  3 KB  2026-10-16
ulka_pump/work/parts/D_an/fin_hs03.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/fin_hs03b.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/m_base.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_hs03.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_hs03b.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_hs03c.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_hs03d.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/m_hs05.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_hs05b.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_rings.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/m_rings2.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_vl03.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/m_vl05.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/rb.py  22 KB  2026-10-16
ulka_pump/work/parts/D_an/rem_hs02.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/rz.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/s0.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/secs.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/sheet.py  0 KB  2026-10-16
ulka_pump/work/parts/D_an/split.py  2 KB  2026-10-16
ulka_pump/work/parts/D_an/thz.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/tools.py  9 KB  2026-10-16
ulka_pump/work/parts/D_an/vid/v10.jpg  39 KB  2026-10-16
ulka_pump/work/parts/D_an/view.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/view2.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/viewc.py  1 KB  2026-10-16
ulka_pump/work/parts/D_an/write_split.py  3 KB  2026-10-16
ulka_pump/work/parts/D_common/dev_d.py  4 KB  2026-10-16
ulka_pump/work/parts/D_common/notes_write.py  7 KB  2026-10-16
ulka_pump/work/parts/D_common/nxlib/dsmall.py  15 KB  2026-10-16
ulka_pump/work/parts/D_common/nxlib/rj.py  6 KB  2026-10-16
ulka_pump/work/parts/D_common/rb.py  22 KB  2026-10-16
ulka_pump/work/parts/D_common/report.py  5 KB  2026-10-16
ulka_pump/work/parts/D_common/run.ps1  2 KB  2026-10-16
ulka_pump/work/parts/D_common/run_many.ps1  0 KB  2026-10-16
ulka_pump/work/parts/D_common/show.py  1 KB  2026-10-16
ulka_pump/work/parts/EM01/EP5-EM01_COIL_build.json  18 KB  2026-10-16
ulka_pump/work/parts/EM01/build.py  20 KB  2026-10-16
ulka_pump/work/parts/EM01/dev_bad.py  1 KB  2026-10-16
ulka_pump/work/parts/EM01/dev_em01.py  3 KB  2026-10-16
ulka_pump/work/parts/EM01/out/EP5-EM01_COIL.log  81 KB  2026-10-16
ulka_pump/work/parts/EM01/qa/dev.json  6 KB  2026-10-16
ulka_pump/work/parts/EM01/qa/dev_fit.json  4 KB  2026-10-16
ulka_pump/work/parts/EM01/qa/dev_tmp.json  4 KB  2026-10-16
ulka_pump/work/parts/EM01/qa/m_em01_T.json  0 KB  2026-10-16
ulka_pump/work/parts/EM01/qa/s0_inventory.json  1 KB  2026-10-16
ulka_pump/work/parts/EM01/qa/s1_census.json  2 KB  2026-10-16
ulka_pump/work/parts/EM01/report_notes.md  3 KB  2026-10-16
ulka_pump/work/parts/EM02/EP5-EM02_FRAME_build.json  9 KB  2026-10-16
ulka_pump/work/parts/EM02/build.py  13 KB  2026-10-16
ulka_pump/work/parts/EM02/dev_em02.py  2 KB  2026-10-16
ulka_pump/work/parts/EM02/out/EP5-EM02_FRAME.log  85 KB  2026-10-16
ulka_pump/work/parts/EM02/qa/dev.json  5 KB  2026-10-16
ulka_pump/work/parts/EM02/qa/dev_fit.json  4 KB  2026-10-16
ulka_pump/work/parts/EM02/qa/m_em02a.json  0 KB  2026-10-16
ulka_pump/work/parts/EM02/qa/m_em02b.json  1 KB  2026-10-16
ulka_pump/work/parts/EM02/qa/s0_inventory.json  1 KB  2026-10-16
ulka_pump/work/parts/EM02/report_notes.md  2 KB  2026-10-16
ulka_pump/work/parts/EM03/EP5-EM03_FLUX-SLEEVE_build.json  5 KB  2026-10-16
ulka_pump/work/parts/EM03/build.py  6 KB  2026-10-16
ulka_pump/work/parts/EM03/dev_em03.py  1 KB  2026-10-16
ulka_pump/work/parts/EM03/out/EP5-EM03_FLUX-SLEEVE.log  4 KB  2026-10-16
ulka_pump/work/parts/EM03/qa/dev.json  4 KB  2026-10-16
ulka_pump/work/parts/EM03/qa/dev_sleeve1.json  4 KB  2026-10-16
ulka_pump/work/parts/EM03/qa/m_em03.json  12 KB  2026-10-16
ulka_pump/work/parts/EM03/qa/s0_inventory.json  1 KB  2026-10-16
ulka_pump/work/parts/EM03/report_notes.md  1 KB  2026-10-16
ulka_pump/work/parts/FS01/EP5-FS01_SCR-FLANGE.log  4 KB  2026-10-16
ulka_pump/work/parts/FS01/fs_build.json  1 KB  2026-10-16
ulka_pump/work/parts/FS01/fs_build.py  4 KB  2026-10-16
ulka_pump/work/parts/HS01/EP5-HS01_INLET-BODY_build.json  5 KB  2026-10-16
ulka_pump/work/parts/HS01/build.py  6 KB  2026-10-16
ulka_pump/work/parts/HS01/dev_hs01.py  1 KB  2026-10-16
ulka_pump/work/parts/HS01/dry/EP5-HS01_INLET-BODY.log  4 KB  2026-10-16
ulka_pump/work/parts/HS01/dry/build.json  5 KB  2026-10-16
ulka_pump/work/parts/HS01/out/EP5-HS01_INLET-BODY.log  13 KB  2026-10-16
ulka_pump/work/parts/HS01/qa/align.json  1 KB  2026-10-16
ulka_pump/work/parts/HS01/qa/dev.json  4 KB  2026-10-16
ulka_pump/work/parts/HS01/qa/dry.json  4 KB  2026-10-16
ulka_pump/work/parts/HS01/qa/s1_census.json  3 KB  2026-10-16
ulka_pump/work/parts/HS01/report_notes.md  2 KB  2026-10-16
ulka_pump/work/parts/HS01/run.log  0 KB  2026-10-16
ulka_pump/work/parts/HS02/EP5-HS02_CYLINDER_build.json  7 KB  2026-10-16
ulka_pump/work/parts/HS02/build.py  9 KB  2026-10-16
ulka_pump/work/parts/HS02/out/EP5-HS02_CYLINDER.log  26 KB  2026-10-16
ulka_pump/work/parts/HS02/qa/dev.json  7 KB  2026-10-16
ulka_pump/work/parts/HS02/report_notes.md  2 KB  2026-10-16
ulka_pump/work/parts/HS03/EP5-HS03_OUTLET-FLANGE_build.json  11 KB  2026-10-16
ulka_pump/work/parts/HS03/build.py  14 KB  2026-10-16
ulka_pump/work/parts/HS03/out/EP5-HS03_OUTLET-FLANGE.log  30 KB  2026-10-16
ulka_pump/work/parts/HS03/qa/dev.json  5 KB  2026-10-16
ulka_pump/work/parts/HS03/report_notes.md  2 KB  2026-10-16
ulka_pump/work/parts/HS04/EP5-HS04_SPACER-RING_build.json  4 KB  2026-10-16
ulka_pump/work/parts/HS04/build.py  4 KB  2026-10-16
ulka_pump/work/parts/HS04/dev_hs04.py  1 KB  2026-10-16
ulka_pump/work/parts/HS04/out/EP5-HS04_SPACER-RING.log  4 KB  2026-10-16
ulka_pump/work/parts/HS04/qa/dev.json  4 KB  2026-10-16
ulka_pump/work/parts/HS04/qa/m_hs04.json  2 KB  2026-10-16
ulka_pump/work/parts/HS04/qa/s0_inventory.json  1 KB  2026-10-16
ulka_pump/work/parts/HS04/qa/s1_census.json  1 KB  2026-10-16
ulka_pump/work/parts/HS04/report_notes.md  1 KB  2026-10-16
ulka_pump/work/parts/HS05/EP5-HS05_WASHER_build.json  3 KB  2026-10-16
ulka_pump/work/parts/HS05/build.py  1 KB  2026-10-16
ulka_pump/work/parts/HS05/out/EP5-HS05_WASHER.log  13 KB  2026-10-16
ulka_pump/work/parts/HS05/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/HS05/report_notes.md  0 KB  2026-10-16
ulka_pump/work/parts/SL01/EP5-SL01_ORING-L_build.json  3 KB  2026-10-16
ulka_pump/work/parts/SL01/build.py  1 KB  2026-10-16
ulka_pump/work/parts/SL01/out/EP5-SL01_ORING-L.log  11 KB  2026-10-16
ulka_pump/work/parts/SL01/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/SL01/report_notes.md  0 KB  2026-10-16
ulka_pump/work/parts/SL02/EP5-SL02_ORING-M_build.json  3 KB  2026-10-16
ulka_pump/work/parts/SL02/build.py  1 KB  2026-10-16
ulka_pump/work/parts/SL02/out/EP5-SL02_ORING-M.log  11 KB  2026-10-16
ulka_pump/work/parts/SL02/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/SL02/report_notes.md  0 KB  2026-10-16
ulka_pump/work/parts/SL03/EP5-SL03_ORING-S_build.json  3 KB  2026-10-16
ulka_pump/work/parts/SL03/build.py  1 KB  2026-10-16
ulka_pump/work/parts/SL03/out/EP5-SL03_ORING-S.log  11 KB  2026-10-16
ulka_pump/work/parts/SL03/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/SL03/report_notes.md  0 KB  2026-10-16
ulka_pump/work/parts/SL04/EP5-SL04_ORING-PISTON_build.json  3 KB  2026-10-16
ulka_pump/work/parts/SL04/build.py  1 KB  2026-10-16
ulka_pump/work/parts/SL04/out/EP5-SL04_ORING-PISTON.log  11 KB  2026-10-16
ulka_pump/work/parts/SL04/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/SL04/report_notes.md  0 KB  2026-10-16
ulka_pump/work/parts/VL01/EP5-VL01_BALL_build.json  2 KB  2026-10-16
ulka_pump/work/parts/VL01/build.py  1 KB  2026-10-16
ulka_pump/work/parts/VL01/out/EP5-VL01_BALL.log  8 KB  2026-10-16
ulka_pump/work/parts/VL01/qa/dev.json  2 KB  2026-10-16
ulka_pump/work/parts/VL01/report_notes.md  0 KB  2026-10-16
ulka_pump/work/parts/VL02/EP5-VL02_SPRING-BALL_build.json  5 KB  2026-10-16
ulka_pump/work/parts/VL02/build.py  1 KB  2026-10-16
ulka_pump/work/parts/VL02/out/EP5-VL02_SPRING-BALL.log  12 KB  2026-10-16
ulka_pump/work/parts/VL02/report_notes.md  1 KB  2026-10-16
ulka_pump/work/parts/VL03/EP5-VL03_VALVE-PLUG_build.json  3 KB  2026-10-16
ulka_pump/work/parts/VL03/build.py  1 KB  2026-10-16
ulka_pump/work/parts/VL03/out/EP5-VL03_VALVE-PLUG.log  9 KB  2026-10-16
ulka_pump/work/parts/VL03/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/VL03/report_notes.md  1 KB  2026-10-16
ulka_pump/work/parts/VL04/EP5-VL04_SPRING-VALVE_build.json  5 KB  2026-10-16
ulka_pump/work/parts/VL04/build.py  1 KB  2026-10-16
ulka_pump/work/parts/VL04/out/EP5-VL04_SPRING-VALVE.log  12 KB  2026-10-16
ulka_pump/work/parts/VL04/report_notes.md  1 KB  2026-10-16
ulka_pump/work/parts/VL05/EP5-VL05_VALVE-CAGE_build.json  4 KB  2026-10-16
ulka_pump/work/parts/VL05/build.py  1 KB  2026-10-16
ulka_pump/work/parts/VL05/out/EP5-VL05_VALVE-CAGE.log  21 KB  2026-10-16
ulka_pump/work/parts/VL05/qa/dev.json  3 KB  2026-10-16
ulka_pump/work/parts/VL05/report_notes.md  1 KB  2026-10-16
ulka_pump/work/parts/_B_common/bm.py  3 KB  2026-10-16
ulka_pump/work/parts/_B_common/m_em01.py  3 KB  2026-10-16
ulka_pump/work/parts/_B_common/m_em02a.py  2 KB  2026-10-16
ulka_pump/work/parts/_B_common/m_em02b.py  3 KB  2026-10-16
ulka_pump/work/parts/_B_common/m_em03.py  4 KB  2026-10-16
ulka_pump/work/parts/_B_common/m_hs04.py  3 KB  2026-10-16
ulka_pump/work/parts/_B_common/nxlib/rj.py  6 KB  2026-10-16
ulka_pump/work/parts/_B_common/occ.py  1 KB  2026-10-16
ulka_pump/work/parts/_B_common/qa/aligned_transforms.json  1 KB  2026-10-16
ulka_pump/work/parts/_B_common/rebuild_all.ps1  1 KB  2026-10-16
ulka_pump/work/parts/_B_common/report.py  5 KB  2026-10-16
ulka_pump/work/parts/_B_common/run.ps1  2 KB  2026-10-16
ulka_pump/work/parts/_B_common/s0_inventory.py  2 KB  2026-10-16
ulka_pump/work/parts/_B_common/s2_aligned.py  2 KB  2026-10-16
ulka_pump/work/parts/_B_common/view.py  2 KB  2026-10-16
ulka_pump/work/ref/video/fr/w_104.jpg  10 KB  2026-10-16
```

### lexus_seat_clip (nx_re_projects_20261105_part1.zip)
```
lexus_seat_clip/desktop_lexuspart/CAD_RV01/LEXUS_SEAT_CLIP_RV01.prt  696 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/LEXUS_SEAT_CLIP_RV01.stl  705 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/LEXUS_SEAT_CLIP_RV01.stp  159 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/README.md  3 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/cad_views.png  207 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/deviation_rv01.json  2 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/align.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/cadview.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/dev.py  2 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/devmap.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/edge.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/finenv.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/fitR.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/fitchain.py  2 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/fitprof.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/frame.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/geo2.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/hmap.py  0 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/meas1.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/meas2.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/outline.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/overlay.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/part_frame2.json  0 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/plate.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/plate2.py  2 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/prof.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/reframe.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/render.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/render2.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/render3.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/side.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/slices.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/stats.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/stats2.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/strap.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/tonguerib.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/zoom2.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/an/zoomx.py  1 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/nx/build.py  5 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/nx/nxlib/chain.py  4 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/nx/nxlib/design.py  7 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/nx/nxlib/im01.py  17 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/CAD_RV01/src/nx/nxlib/ps.py  14 KB  2026-10-24
lexus_seat_clip/desktop_lexuspart/thumbnail.png  15 KB  2026-10-24
lexus_seat_clip/mesh_135528/arm_sections.png  188 KB  2026-10-28
lexus_seat_clip/mesh_135528/arm_sections.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/census_offline.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/compare.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/components.json  1 KB  2026-10-28
lexus_seat_clip/mesh_135528/components.py  2 KB  2026-10-28
lexus_seat_clip/mesh_135528/datum_fit.py  6 KB  2026-10-28
lexus_seat_clip/mesh_135528/decide.png  114 KB  2026-10-28
lexus_seat_clip/mesh_135528/decide.py  2 KB  2026-10-28
lexus_seat_clip/mesh_135528/describe.json  1 KB  2026-10-28
lexus_seat_clip/mesh_135528/describe.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/final_offline.py  5 KB  2026-10-28
lexus_seat_clip/mesh_135528/focus.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/identify_planes.py  2 KB  2026-10-28
lexus_seat_clip/mesh_135528/measure_a.py  5 KB  2026-10-28
lexus_seat_clip/mesh_135528/measure_b.py  6 KB  2026-10-28
lexus_seat_clip/mesh_135528/nxrun.ps1  2 KB  2026-10-28
lexus_seat_clip/mesh_135528/offline_params.json  0 KB  2026-10-28
lexus_seat_clip/mesh_135528/out/part_raw.stl  9.5 MB  2026-10-28
lexus_seat_clip/mesh_135528/out/re_measure.json  10 KB  2026-10-28
lexus_seat_clip/mesh_135528/out/re_measure.log  1 KB  2026-10-28
lexus_seat_clip/mesh_135528/p_alongA1.png  178 KB  2026-10-28
lexus_seat_clip/mesh_135528/p_alongA2.png  221 KB  2026-10-28
lexus_seat_clip/mesh_135528/p_frombottom.png  299 KB  2026-10-28
lexus_seat_clip/mesh_135528/p_iso.png  282 KB  2026-10-28
lexus_seat_clip/mesh_135528/p_iso2.png  266 KB  2026-10-28
lexus_seat_clip/mesh_135528/p_side_low.png  211 KB  2026-10-28
lexus_seat_clip/mesh_135528/padframe2.json  1 KB  2026-10-28
lexus_seat_clip/mesh_135528/part_extract.py  4 KB  2026-10-28
lexus_seat_clip/mesh_135528/planes_final.json  2 KB  2026-10-28
lexus_seat_clip/mesh_135528/planes_final.py  5 KB  2026-10-28
lexus_seat_clip/mesh_135528/re_measure.py  13 KB  2026-10-28
lexus_seat_clip/mesh_135528/recess.py  4 KB  2026-10-28
lexus_seat_clip/mesh_135528/recesses.json  0 KB  2026-10-28
lexus_seat_clip/mesh_135528/render_views.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/rough.py  4 KB  2026-10-28
lexus_seat_clip/mesh_135528/sections.png  123 KB  2026-10-28
lexus_seat_clip/mesh_135528/sections.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/seg.py  5 KB  2026-10-28
lexus_seat_clip/mesh_135528/segment.json  0 KB  2026-10-28
lexus_seat_clip/mesh_135528/slab.py  2 KB  2026-10-28
lexus_seat_clip/mesh_135528/v_iso.png  251 KB  2026-10-28
lexus_seat_clip/mesh_135528/vtk_render.py  3 KB  2026-10-28
lexus_seat_clip/mesh_135528/write_stl_fix.py  2 KB  2026-10-28
lexus_seat_clip/transcripts/3d9eaa45-a683-4598-b6b8-8dd4c5d086b2.jsonl  6.1 MB  
lexus_seat_clip/work/an/chainfit.json  0 KB  2026-10-24
lexus_seat_clip/work/an/cmp_usta.py  2 KB  2026-10-25
lexus_seat_clip/work/an/dev_rv01_pre.json  2 KB  2026-10-24
lexus_seat_clip/work/an/edge.png  77 KB  2026-10-24
lexus_seat_clip/work/an/ov_bendA.png  66 KB  2026-10-24
lexus_seat_clip/work/an/ov_tip.png  50 KB  2026-10-24
lexus_seat_clip/work/an/ov_tongue.png  48 KB  2026-10-24
lexus_seat_clip/work/an/overlay.png  192 KB  2026-10-24
lexus_seat_clip/work/an/part_frame.json  0 KB  2026-10-24
lexus_seat_clip/work/an/prof.png  186 KB  2026-10-24
lexus_seat_clip/work/an/strap.png  88 KB  2026-10-24
lexus_seat_clip/work/an/table_frame.json  0 KB  2026-10-24
lexus_seat_clip/work/an/xsec.png  104 KB  2026-10-24
lexus_seat_clip/work/an/ysec.png  119 KB  2026-10-24
lexus_seat_clip/work/an/zoom2.png  107 KB  2026-10-24
lexus_seat_clip/work/an/zoomx.png  79 KB  2026-10-24
lexus_seat_clip/work/an/zsec.png  83 KB  2026-10-24
lexus_seat_clip/work/nx/out/LEXUS_SEAT_CLIP_RV01.log  14 KB  2026-10-24
lexus_seat_clip/work/nx/out/build.json  1 KB  2026-10-24
lexus_seat_clip/work/nx/out/build.log  1 KB  2026-10-24
lexus_seat_clip/work/views0/iso1.png  184 KB  2026-10-24
lexus_seat_clip/work/views0/iso4.png  179 KB  2026-10-24
lexus_seat_clip/work/views0/ny.png  241 KB  2026-10-24
lexus_seat_clip/work/views0/py.png  262 KB  2026-10-24
lexus_seat_clip/work/views1/iso1.png  299 KB  2026-10-24
lexus_seat_clip/work/views1/iso3.png  281 KB  2026-10-24
lexus_seat_clip/work/views1/iso4.png  269 KB  2026-10-24
lexus_seat_clip/work/views1/nx.png  141 KB  2026-10-24
lexus_seat_clip/work/views1/ny.png  188 KB  2026-10-24
lexus_seat_clip/work/views1/px.png  149 KB  2026-10-24
lexus_seat_clip/work/views1/py.png  185 KB  2026-10-24
lexus_seat_clip/work/views2/a.png  280 KB  2026-10-24
lexus_seat_clip/work/views2/b.png  262 KB  2026-10-24
lexus_seat_clip/work/views2/c.png  284 KB  2026-10-24
lexus_seat_clip/work/views2/d.png  263 KB  2026-10-24
lexus_seat_clip/work/views2/e.png  267 KB  2026-10-24
lexus_seat_clip/work/views2/f.png  208 KB  2026-10-24
lexus_seat_clip/work/views2/g.png  292 KB  2026-10-24
lexus_seat_clip/work/views2/h.png  266 KB  2026-10-24
lexus_seat_clip/work/views3/fromMinusXlow.png  300 KB  2026-10-24
lexus_seat_clip/work/views_cad/iso_back.png  32 KB  2026-10-24
lexus_seat_clip/work/views_cad/iso_front.png  32 KB  2026-10-24
lexus_seat_clip/work/views_cad/iso_left.png  45 KB  2026-10-24
lexus_seat_clip/work/views_cad/iso_right.png  33 KB  2026-10-24
lexus_seat_clip/work/views_cad/side.png  23 KB  2026-10-24
lexus_seat_clip/work/views_cad/top.png  20 KB  2026-10-24
lexus_seat_clip/work/views_dev/A.png  241 KB  2026-10-24
lexus_seat_clip/work/views_dev/B.png  260 KB  2026-10-24
lexus_seat_clip/work/views_dev/C.png  263 KB  2026-10-24
lexus_seat_clip/work/views_dev/D.png  246 KB  2026-10-24
lexus_seat_clip/work/views_dev/E.png  200 KB  2026-10-24
lexus_seat_clip/work/views_dev/F.png  204 KB  2026-10-24
```

### left_thigh_outer_inner (nx_re_projects_20261105_part2.zip)
```
left_thigh_outer_inner/project/LT-ASM-001_RevE/03_LT-INN-001_RevE_Inner/Deviation Report/LT-INN-001_deviation_side_nx.png  290 KB  2026-11-02
left_thigh_outer_inner/project/LT-ASM-001_RevE/03_LT-INN-001_RevE_Inner/Deviation Report/LT-INN-001_deviation_side_px.png  272 KB  2026-11-02
left_thigh_outer_inner/project/part 1/CLIENT_MESSAGE.txt  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/CLIENT_MESSAGE_RevB.txt  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/CLIENT_MESSAGE_RevC.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/Deviation_Check/LT-OUT-001_Left_Thigh_Outer_vs_SCAN_overlay.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/Deviation_Check/LT-OUT-001_RevB_Left_Thigh_Outer_vs_SCAN_CONN_conn_pad.json  3 KB  2026-10-31
left_thigh_outer_inner/project/part 1/Deviation_Check/LT-OUT-001_RevB_Left_Thigh_Outer_vs_SCAN_CONN_fix_r2.json  5 KB  2026-10-31
left_thigh_outer_inner/project/part 1/Deviation_Check/LT-OUT-001_RevB_Left_Thigh_Outer_vs_SCAN_CONN_fix_r2_scancheck.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/Deviation_Check/LT-OUT-001_RevC_Left_Thigh_Outer_vs_SCAN_fix_r3.json  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevA_Left_Thigh_Outer/LT-OUT-001_RevA/Deviation Report/REPORT_deviation.md  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevA_Left_Thigh_Outer/LT-OUT-001_RevA/Renders/LT-OUT-001_side_px.png  217 KB  2026-10-25
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevB_Left_Thigh_Outer/LT-OUT-001_RevB/Deviation Report/REPORT_deviation.md  3 KB  2026-10-30
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevB_Left_Thigh_Outer/LT-OUT-001_RevB/README.md  7 KB  2026-10-30
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevB_Left_Thigh_Outer/LT-OUT-001_RevB/Renders/LT-OUT-001_RevB_hip_slots.png  121 KB  2026-10-30
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevB_Left_Thigh_Outer/LT-OUT-001_RevB/Renders/LT-OUT-001_iso_bottom.png  247 KB  2026-10-30
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevB_Left_Thigh_Outer/LT-OUT-001_RevB/Renders/LT-OUT-001_side_px.png  179 KB  2026-10-30
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevC_Left_Thigh_Outer/LT-OUT-001_RevC/Deviation Report/REPORT_deviation.md  4 KB  2026-10-31
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevC_Left_Thigh_Outer/LT-OUT-001_RevC/README.md  8 KB  2026-10-31
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevC_Left_Thigh_Outer/LT-OUT-001_RevC/Renders/LT-OUT-001_RevC_connector_pad.png  205 KB  2026-10-31
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevC_Left_Thigh_Outer/LT-OUT-001_RevC/Renders/LT-OUT-001_RevC_hip_slots.png  121 KB  2026-10-31
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevC_Left_Thigh_Outer/LT-OUT-001_RevC/Renders/LT-OUT-001_iso_bottom.png  246 KB  2026-10-31
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevC_Left_Thigh_Outer/LT-OUT-001_RevC/Renders/LT-OUT-001_side_px.png  181 KB  2026-10-31
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevF_Left_Thigh_Outer/LT-OUT-001_RevF/Drawings/LT-OUT-001_SH1.pdf  238 KB  2026-11-02
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevF_Left_Thigh_Outer/LT-OUT-001_RevF/Drawings/LT-OUT-001_SH2.pdf  146 KB  2026-11-02
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevF_Left_Thigh_Outer/LT-OUT-001_RevF/Drawings/LT-OUT-001_SH3.pdf  200 KB  2026-11-02
left_thigh_outer_inner/project/part 1/LT-OUT-001_RevF_Left_Thigh_Outer/LT-OUT-001_RevF/Drawings/LT-OUT-001_SH5.pdf  245 KB  2026-11-02
left_thigh_outer_inner/project/part 1/REBUILD.md  10 KB  2026-11-01
left_thigh_outer_inner/project/part 1/STATUS.md  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/STATUS_RevB.md  5 KB  2026-10-30
left_thigh_outer_inner/project/part 1/STATUS_RevC.md  8 KB  2026-10-31
left_thigh_outer_inner/project/part 1/STATUS_RevF.md  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/an/arcfit.py  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/b1_slots.py  3 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/b2_measure.py  5 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/b3_proto.py  5 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/b4_protochk.py  4 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/b5_slotdev.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/b6_fit.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/b7_package.py  2 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/b8_renders.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/c5_localdev.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/an/c7_package.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/an/c8_renders.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/an/cfit.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/common.py  3 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/dev.py  3 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/dev2.py  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/devzoom.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/f7_package.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/an/hdiff.py  3 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/hmap.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/hmap2.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/ovl.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/plot_secs.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/report.py  2 KB  2026-10-30
left_thigh_outer_inner/project/part 1/an/rzloc.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/rzprof.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s0_load.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s10_skin.py  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s11_skin2.py  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s12_sections.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s13_levels.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s14_inner.py  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s15_masks.py  3 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s16_outlines.py  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s17_bosses.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s18_holes.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s19_platnx.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s1_views.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s20_windows.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s21_winloops.py  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s22_grooves.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s23_groove_paths.py  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s24_missing.py  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s2_census.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s30_scan_aligned.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s31_outline.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s3_parting.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s4_frame.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s5_rim.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s6_axes.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s7_polar.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s7b_plot.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s8_knee_outline.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/s9_hip.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/sec.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/shot.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/stepcheck.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/wallmap.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/an/walltop.py  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/deliver/CAD/_finalize.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/deliver/README.md  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/deliver_RevB/CAD/LT-OUT-001_Left_Thigh_Outer_AP214.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/deliver_RevB/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.log  5 KB  2026-10-30
left_thigh_outer_inner/project/part 1/deliver_RevB/CAD/_finalize.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/deliver_RevC/CAD/LT-OUT-001_Left_Thigh_Outer_AP214.log  12 KB  2026-10-31
left_thigh_outer_inner/project/part 1/deliver_RevC/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.log  10 KB  2026-10-31
left_thigh_outer_inner/project/part 1/deliver_RevC/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.step  3.0 MB  2026-10-31
left_thigh_outer_inner/project/part 1/deliver_RevC/CAD/_finalize.json  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/deliver_RevF/CAD/LT-OUT-001_Left_Thigh_Outer_AP214.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/deliver_RevF/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 1/deliver_RevF/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.step  2.7 MB  2026-11-02
left_thigh_outer_inner/project/part 1/deliver_RevF/CAD/_finalize.json  9 KB  2026-11-02
left_thigh_outer_inner/project/part 1/nx/build.py  13 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/build2.py  21 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/conn_pad.py  10 KB  2026-10-31
left_thigh_outer_inner/project/part 1/nx/dwg_main.py  28 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/dwg_main_v1.py  18 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/dwg_revB.py  34 KB  2026-10-30
left_thigh_outer_inner/project/part 1/nx/dwg_revC.py  37 KB  2026-10-31
left_thigh_outer_inner/project/part 1/nx/dwg_revF.py  60 KB  2026-11-02
left_thigh_outer_inner/project/part 1/nx/dwglib/_patch.py  3 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/dwglib/gdt.py  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/dwglib/m3d.py  19 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/dwglib/nxd2.py  10 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/dwglib/ptdwg.py  12 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/finalize.py  8 KB  2026-10-31
left_thigh_outer_inner/project/part 1/nx/finalize_revF.py  30 KB  2026-11-02
left_thigh_outer_inner/project/part 1/nx/finalize_revF_full.py  28 KB  2026-11-02
left_thigh_outer_inner/project/part 1/nx/fix_r2.py  13 KB  2026-10-31
left_thigh_outer_inner/project/part 1/nx/fix_r3_rim.py  8 KB  2026-10-31
left_thigh_outer_inner/project/part 1/nx/inspect_final.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/j1_skin.py  3 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/j2_probe.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/j4_examine.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/j5_loftcheck.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/make_dwg_revB.py  8 KB  2026-10-30
left_thigh_outer_inner/project/part 1/nx/make_dwg_revC.py  7 KB  2026-10-31
left_thigh_outer_inner/project/part 1/nx/out1/j1.json  0 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outA/build.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outA2/build.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outB/build.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outC/build.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outD/build.json  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outE/build.json  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outE/examine.json  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outF/build.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outP/loftcheck_inner.json  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outP/loftcheck_outer.json  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outP/probe.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/outRevB1/revB_slots.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/nx/outRevB1/run.log  0 KB  2026-10-30
left_thigh_outer_inner/project/part 1/nx/outRevB2/revB_slots.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/nx/overlay.py  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/params.json  8 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/probe_gdt.py  8 KB  2026-10-25
left_thigh_outer_inner/project/part 1/nx/revB_slots.py  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/LT-OUT-001_Left_Thigh_Outer_AP214.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/LT-OUT-001_Left_Thigh_Outer_AP242.log  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/LT-OUT-001_SH1.log  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/LT-OUT-001_SH2.log  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/LT-OUT-001_SH3.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/LT-OUT-001_SH4.log  4 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/_finalize.json  1 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/_tmp.png  10 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/all_secs.png  215 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/boltholes.json  9 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/bosses.json  3 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dev2_b1.json  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dev2_bH.json  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dev2_final.json  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dev2_revA2.json  2 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dev2_revB.json  2 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dev2_revC.json  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dev2_revC2.json  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dev_env1.json  0 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH1.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH1_bk.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH2.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH2_bk.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH3.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH3_bk.log  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH4.log  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/LT-OUT-001_SH4_bk.log  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/dwg_result.json  13 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v1_p1.png  205 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v1_p2.png  137 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v1_p3.png  106 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v1_p4.png  174 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v2_p1.png  206 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v2_p2.png  136 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v2_p3.png  114 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v2_p4.png  179 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v3_det.png  69 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v3_p2.png  136 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v3_p3.png  118 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v3_p4.png  180 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v4_det.png  73 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwg2/v4_p3.png  118 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/dwgB1/LT-OUT-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/LT-OUT-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/LT-OUT-001_SH3.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/LT-OUT-001_SH4.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/dwg_result.json  16 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/p-1.png  192 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/p-2.png  140 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/p-3.png  130 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/p-4.png  222 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/run.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/z4-4.png  3 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/zH-4.png  26 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB1/zJ-4.png  34 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/LT-OUT-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/LT-OUT-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/LT-OUT-001_SH3.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/LT-OUT-001_SH4.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/dwg_result.json  15 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/p-1.png  192 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/p-3.png  130 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/p-4.png  223 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/run.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/zJ-4.png  57 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB2/zR-1.png  55 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/LT-OUT-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/LT-OUT-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/LT-OUT-001_SH3.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/LT-OUT-001_SH4.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/dwg_result.json  15 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/p-1.png  192 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/p-2.png  140 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/p-4.png  223 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/run.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB3/zJ-4.png  57 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/LT-OUT-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/LT-OUT-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/LT-OUT-001_SH3.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/LT-OUT-001_SH4.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/dwg_result.json  15 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/p-4.png  223 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/run.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgB4/zJ-4.png  57 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/dwgC1/LT-OUT-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC1/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC1/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC1/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC1/_launcher.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC1/dwg_result.json  17 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC2/LT-OUT-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC2/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC2/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC2/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC2/_launcher.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC2/dwg_result.json  16 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC3/LT-OUT-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC3/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC3/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC3/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC3/_launcher.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC3/dwg_result.json  16 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC4/LT-OUT-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC4/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC4/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC4/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC4/_launcher.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC4/dwg_result.json  16 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC5/LT-OUT-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC5/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC5/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC5/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC5/_launcher.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgC5/dwg_result.json  16 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/dwgF/_funcs.txt  9 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/_sh4.txt  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/_sh5.txt  5 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/check_pdf.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/diag_views.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/dwg_result.txt  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/final_prt_hash_before.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/model/_finalize.json  7 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/probe_F.json  156 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/probe_F.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/ref/c5_p1.png  284 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/ref/c5_p2.png  188 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/ref/c5_p3.png  194 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/ref/chk/p1.png  183 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/ref/chk/p2.png  123 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/ref/chk/p3.png  125 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/ref/chk/p4.png  197 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/rib_spec_src.json  13 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run.ps1  0 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH1.pdf  234 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH2.pdf  145 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH3.pdf  201 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH4.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH5.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/LT-OUT-001_SH5.pdf  246 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/dwg_result.json  27 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p1.png  268 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p1_t00.png  190 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p1_t01.png  120 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p1_t02.png  155 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p1_t10.png  53 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p1_t11.png  136 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p1_t12.png  155 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p2.png  179 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p2_t00.png  176 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p2_t01.png  138 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p2_t02.png  16 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p2_t10.png  68 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p2_t11.png  55 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p2_t12.png  67 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run1/png/p3.png  185 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH1.pdf  239 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH2.pdf  146 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH3.pdf  200 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH4.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH5.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/LT-OUT-001_SH5.pdf  245 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run2/dwg_result.json  24 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH1.pdf  239 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH2.pdf  147 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH3.pdf  200 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH4.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH5.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/LT-OUT-001_SH5.pdf  244 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/run3/dwg_result.json  24 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF/wait_final.sh  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/LT-OUT-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/LT-OUT-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/LT-OUT-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/LT-OUT-001_SH4.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/LT-OUT-001_SH5.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/dwg_result.json  24 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH1.pdf  238 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH2.pdf  146 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH3.pdf  200 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH4.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH5.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/LT-OUT-001_SH5.pdf  245 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_a/dwg_result.json  24 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH1.pdf  238 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH2.pdf  146 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH3.pdf  200 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH4.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH5.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/LT-OUT-001_SH5.pdf  245 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwgF_final/run_b/dwg_result.json  24 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/dwg_result.json  12 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/final_rt/LT-OUT-001_Left_Thigh_Outer_AP214.log  12 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/final_rt/LT-OUT-001_Left_Thigh_Outer_AP242.log  10 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/frame.json  0 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/frame_prov.json  0 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/gdt_probe/probe.json  6 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/gdt_probe/probe.pdf  14 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/grooves.json  15 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/hdiff_b1.json  7 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/hdiff_bH.json  9 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/inner_sections.json  159 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/missing_b1.json  45 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/overlay/inspect_final.json  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/overlay/probe_pts.json  12 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/parting_raw.json  0 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/plan_outline.json  5 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/plateaus.json  112 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/plateaus_nx.json  83 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/qaF/diff_0645_final.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/diff_A_F0645.json  16 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/notes.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/q1_diff.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/q2_qa.py  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/q3_worse.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/q4_maps.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/q5_pdf.py  11 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/q6_ribs.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/q7.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/qa_0645.json  13 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/qaF/qa_final.json  13 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/renderF/bl_render.py  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/renderF/compose.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/renderF/final/framing.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/renderF/prev/framing.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/renderF/run_final.sh  0 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/renderF/trial/framing.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/renderF/views.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revB/README_template.md  6 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/revB/chk_proto.json  0 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/revB/chk_revB.json  0 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/revB/fit_revB_inner242.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/revB/measure.json  7 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/revB/proto.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/revB/slotdev.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 1/work/revC/bboxcheck.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC/circ.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC/cyl.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC/localdev.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC/stepcheck_revC.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC/v1/CAD/LT-OUT-001_Left_Thigh_Outer_AP214.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC/v1/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.log  5 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC/v1/CAD/_finalize.json  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC2/dev2.log  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC2/fit_revC2.json  111 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC2/fit_revC_base.json  112 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC2/localdev_rim.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC2/plan.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC2/rimsec.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revC2/ysec.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 1/work/revF/bboxcheck.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/cmp_stl.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/diag_revF.json  13 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/diag_revF.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/dumb_ref/LT-OUT-001_Left_Thigh_Outer_AP214.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/dumb_ref/LT-OUT-001_Left_Thigh_Outer_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/dumb_ref/_finalize.json  6 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/final_run2/_finalize.json  5 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/final_run3/_finalize.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/finalize_result.txt  7 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv561.json  5 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv561.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv561b.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv561b.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv561c.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv561c.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv_revF.json  29 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/inv_revF.py  7 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/opt_revF.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/opt_revF2.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/opt_revF4.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/probe_revF.json  49 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/probe_revF.py  7 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/probe_revF_try1_recheck_broke.json  94 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/probes_saved.json  116 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/revF/stepcheck_revF.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 1/work/s0_describe.json  0 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/sections.json  158 KB  2026-10-25
left_thigh_outer_inner/project/part 1/work/windows.json  7 KB  2026-10-25
left_thigh_outer_inner/project/part 2 - Inner/CLIENT_MESSAGE.txt  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/CLIENT_MESSAGE_RevB.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/Deviation_Check/LT-INN-001_Left_Thigh_Inner_vs_SCAN_overlay.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/Deviation_Check/RIBS4_spot_deviation.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/HANDOFF.md  4 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/LT-INN-001_RevA_Left_Thigh_Inner/LT-INN-001_RevA/Deviation Report/REPORT_deviation.md  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/LT-INN-001_RevA_Left_Thigh_Inner/LT-INN-001_RevA/README.md  7 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/LT-INN-001_RevB_Left_Thigh_Inner/LT-INN-001_RevB/Deviation Report/REPORT_deviation.md  4 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/LT-INN-001_RevB_Left_Thigh_Inner/LT-INN-001_RevB/README.md  8 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/LT-INN-001_RevE_Left_Thigh_Inner/LT-INN-001_RevE/Drawings/LT-INN-001_SH1.pdf  312 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/LT-INN-001_RevE_Left_Thigh_Inner/LT-INN-001_RevE/Drawings/LT-INN-001_SH2.pdf  185 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/LT-INN-001_RevE_Left_Thigh_Inner/LT-INN-001_RevE/Drawings/LT-INN-001_SH3.pdf  250 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/REBUILD.md  12 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/STATUS.md  40 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/CLIENT_MESSAGE.txt  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/Deviation_Check/LT-INN-001_Left_Thigh_Inner_vs_SCAN_overlay.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/LT-INN-001_RevA_Left_Thigh_Inner/LT-INN-001_RevA/Deviation Report/REPORT_deviation.md  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/LT-INN-001_RevA_Left_Thigh_Inner/LT-INN-001_RevA/README.md  8 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/deliver/CAD/LT-INN-001_Left_Thigh_Inner_AP214.log  36 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/deliver/CAD/LT-INN-001_Left_Thigh_Inner_AP242.log  29 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/deliver/CAD/_finalize.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/dwg_inner_fixround.py  35 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/i70_report_fixround.py  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/_fixround_2026-10-30/plan_outline_fixround.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/an/_dbg.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/_hs.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/cfit.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/common.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/dev.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/dev2.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/devzoom.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/fixlib.py  12 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/hdiff.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/hmap.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/hmap2.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i100_table.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i10_levels.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i11_step.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i12_kneerz.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i13_levels.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i14_hmap.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i15_topmap.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i16_hipend.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i1_census.py  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i20_skin.py  8 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i20lib.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i21_cavity.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i22_kneetop.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i23_outlines.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i24_bosses.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i25_rebate.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i26_rebate.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i27_windows.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i28_grooves.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i29_holes.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i2_rim.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i30_params.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i31_ramp.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i32_outer_band.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i3_rimmap.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i40_dev.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i4_feats.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i50_fit.py  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i5_cyl.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i60_renders.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i60_renders_revB.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/an/i61_look.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i62_depthdiff.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i6_tops.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i71_readme.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i7_register.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i80_package.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i80_package_revB.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/an/i8_check.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i90_clusters.py  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i91_crops.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i92_secs.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i93_depth.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i93top.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i94_zoom.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i95_realdiff.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i96_reconcile.py  11 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i97_nxprep.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i97_sim.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i98_showfix.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i99_autofix.py  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/i9_joint.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/m1_planesec.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/m2_rwin.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/m3_fixes.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/m4_clear.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/an/masklib.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/outer.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/ovl.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/report.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/rzloc.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/rzprof.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s0_load.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s10_skin.py  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s11_skin2.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s12_sections.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s13_levels.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s14_inner.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s15_masks.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s17_bosses.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s18_holes.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s19_platnx.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s1_views.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s20_windows.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s22_grooves.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s23_groove_paths.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s24_missing.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s2_census.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s30_scan_aligned.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s31_outline.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s3_parting.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s5_rim.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s6_axes.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s7_polar.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s7b_plot.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s8_knee_outline.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/s9_hip.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/sec.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/shot.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/stepcheck.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/stepcheck_revE.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/an/wallmap.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/an/walltop.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/deliver/CAD/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/deliver/CAD/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/deliver/CAD/_finalize.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevB/CAD/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevB/CAD/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevB/CAD/_finalize.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE/CAD/LT-INN-001_Left_Thigh_Inner_AP214.log  12 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE/CAD/LT-INN-001_Left_Thigh_Inner_AP214.step  6.2 MB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE/CAD/LT-INN-001_Left_Thigh_Inner_AP242.log  9 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE/CAD/LT-INN-001_Left_Thigh_Inner_AP242.step  2.9 MB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE/CAD/_finalize.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/CAD/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/CAD/LT-INN-001_Left_Thigh_Inner_AP214.step  8.4 MB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/CAD/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/CAD/LT-INN-001_Left_Thigh_Inner_AP242.step  2.9 MB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/CAD/_finalize.json  4 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/Drawings/LT-INN-001_SH1.pdf  326 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/Drawings/LT-INN-001_SH2.pdf  185 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE2/Drawings/LT-INN-001_SH3.pdf  281 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE_fit/CAD/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE_fit/CAD/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE_fit/CAD/LT-INN-001_Left_Thigh_Inner_AP242.step  3.2 MB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/deliver_RevE_fit/CAD/_finalize.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/nx/ap214_tol.py  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/build.py  13 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/build2.py  21 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/build_inner.py  42 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/build_inner_v1.py  19 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwg_inner.py  34 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwg_inner_head.py  10 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwg_inner_revB.py  35 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/nx/dwg_inner_revE.py  57 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/nx/dwg_main.py  29 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwg_main_v1.py  18 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwglib/_patch.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwglib/gdt.py  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwglib/m3d.py  19 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/dwglib/ptdwg.py  12 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/envL/export_env.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/export_env.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/finalize.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/finalize_inner.py  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/finalize_inner_revB.py  5 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/nx/finalize_revE.py  28 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/nx/fix_sliver.py  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/fixes_L.json  148 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/fixes_M.json  161 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/fixes_M2.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/inspect_final.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/j1_skin.py  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/j2_probe.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/j4_examine.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/j5_loftcheck.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/overlay.py  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/params.json  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/params_runC7.json  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/probe_gdt.py  8 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runA4/build.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runA5/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runC1/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runC2/build.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runC3/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runC6/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runC7/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runI8/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runJ9/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runK10/build.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runL11/build.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/runM12/build.json  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/runM13/build.json  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/runM14/fix_sliver.json  122 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/runM15/build.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/runM16/build.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/nx/tmpF/fin/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/tmpF/fin/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/tmpF/fin/_finalize.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/tmp_fin/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/tmp_fin/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/nx/tmp_fin/_finalize.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/autofix_revA.json  107 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/autofix_revA_report.json  14 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/autofix_top_sim2.json  14 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/autofix_top_sim2_report.json  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/boss_census.json  11 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/boss_tops.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_L11.json  186 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_M12.json  194 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_finalM.json  192 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_finalM13.json  190 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_revA.json  150 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_sim1.json  191 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_sim2.json  167 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_sim3.json  190 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_sim4.json  188 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_sim5.json  183 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/clusters_simM.json  187 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/cyl_inner.json  10 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/cyl_outer.json  10 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_C6.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_F.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_J.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_K.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_L11.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_envB.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_final.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_final2.json  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_final3.json  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_restoreK.json  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_revB.json  2 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_revB2.json  2 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_sim1.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_sim2.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_sim3.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_sim4.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev2_sim5.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev_K.log  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev_final.log  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dev_restoreK.log  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/diag/v_chan.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/diag/v_hip.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/diag/v_open.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/diag/v_user.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/master_hash_before.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/plan_outline_E.json  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/probe_E.json  193 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/probe_E.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/probe_feat.json  94 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/probe_feat.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run.ps1  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run1/dwg_result.json  17 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH1.pdf  312 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH2.pdf  185 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH3.pdf  250 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH4.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/LT-INN-001_SH5.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run2/dwg_result.json  37 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run3/LT-INN-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run3/LT-INN-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run3/LT-INN-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run3/LT-INN-001_SH4.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run3/LT-INN-001_SH5.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/run3/dwg_result.json  36 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE/s31_outline_E.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/md5_before.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/plan_outline_E.json  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run.ps1  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH1.pdf  326 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH2.pdf  185 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH3.pdf  279 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH4.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/LT-INN-001_SH5.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run1/dwg_result.json  36 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run2/LT-INN-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run2/LT-INN-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run2/LT-INN-001_SH3.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run2/LT-INN-001_SH4.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run2/LT-INN-001_SH5.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/run2/dwg_result.json  36 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/s31_outline_E.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgE2/volume_E2.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/dwgM/LT-INN-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwgM/LT-INN-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwgM/LT-INN-001_SH3.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwgM/LT-INN-001_SH4.log  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwgM/dwg_result.json  7 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwgM/run_journal.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB/LT-INN-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB/LT-INN-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB/LT-INN-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB/LT-INN-001_SH4.log  5 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB/dwg_result.json  7 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB2/LT-INN-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB2/LT-INN-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB2/LT-INN-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB2/LT-INN-001_SH4.log  5 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB2/dwg_result.json  7 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB3/LT-INN-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB3/LT-INN-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB3/LT-INN-001_SH3.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB3/LT-INN-001_SH4.log  5 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwgRevB3/dwg_result.json  7 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K/dwg_result.json  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K2/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K2/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K2/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K2/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K2/dwg_result.json  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K3/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K3/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K3/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K3/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K3/dwg_result.json  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K4/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K4/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K4/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K4/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K4/dwg_result.json  8 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K5/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K5/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K5/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K5/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K5/dwg_result.json  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K6/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K6/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K6/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K6/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_K6/dwg_result.json  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/LT-INN-001_SH1.log  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/LT-INN-001_SH2.log  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/LT-INN-001_SH2.pdf  71 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/LT-INN-001_SH3.log  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/LT-INN-001_SH4.log  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/dump_sh1_front.json  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/dump_sh1_right.json  47 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/dump_sh1_top.json  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/dump_sh2_ksec.json  68 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/dump_sh3_bot.json  131 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/dump_sh3_csec.json  61 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_dump/dwg_result.json  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final/dwg_result.json  10 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final2/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final2/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final2/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final2/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final2/dwg_result.json  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final3/LT-INN-001_SH1.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final3/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final3/LT-INN-001_SH3.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final3/LT-INN-001_SH4.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_final3/dwg_result.json  7 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_restore/LT-INN-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_restore/LT-INN-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_restore/LT-INN-001_SH3.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_restore/LT-INN-001_SH4.log  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_restore/dwg_result.json  7 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_restore/run_journal.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_t1/LT-INN-001_SH1.log  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_t1/LT-INN-001_SH2.log  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_t1/LT-INN-001_SH3.log  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_t1/LT-INN-001_SH4.log  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/dwg_t1/dwg_result.json  24 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fit_F.json  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fit_F.log  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fit_K.json  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fit_K.log  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fit_M.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_M13_revA.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_M242.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_final.json  5 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fit_final.log  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fit_restoreK.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_restoreK.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_revB.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_revB.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_revB_AP242.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_revB_AP242.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fit_tmp.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fixes.json  41 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/fixes_M_all.json  163 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/fixes_all.json  146 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/frame.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/grooves.json  26 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/holes.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/inner_feats_raw.json  8 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/inner_sections.json  187 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/outer_band_nx.json  62 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/outer_pad_nx.json  2 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/overlay/probe_pts.json  12 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/parting_raw.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/plan_outline.json  5 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/plan_outline_revA.json  5 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/plateaus.json  209 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/plateaus_nx.json  159 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/diff_BE.json  7 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/e2_qa.log  3 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/e2_qa.py  8 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/e3_diff.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/e4_maps.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/e5_pdf.py  17 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/fixenc.py  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/patch1.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/patch2.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/qa_revE.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE/render.py  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/diff_BE.json  7 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/e2_qa.log  3 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/e2_qa.py  8 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/e3.log  4 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/e3_diff.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/e4.log  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/e5_pdf.py  18 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/patch_e5.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/qaE2/qa_revE.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/ramp_nx.json  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/real_revA.json  6 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/rebate_nx.json  105 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/reconcile_nx.json  3 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/reconcile_revA.json  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/register.json  4 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/bl_render2.py  8 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/final/framing.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/final2/framing.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/run_final.sh  1 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/scene.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/trial/framing.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/trial2/framing.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renderE/views.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/renders_restore.log  0 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/revB/dev.txt  2 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB/fit_outRevB.json  4 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB/fit_outRevB.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB/stepcheck.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB2/dev.txt  2 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB2/fit_RevC.json  85 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB2/fit_RevC.txt  59 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB2/renders.txt  0 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revB2/stepcheck.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 2 - Inner/work/revE/finalize_result.txt  3 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/revE/run3_unite/_finalize.json  13 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/revE/stepcheck_RevB_ref.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/revE/stepcheck_RevE.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 2 - Inner/work/s0_describe.json  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/sections.json  187 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/HANDOFF_before_M.md  4 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/README_before_revB.md  8 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/README_revA_before_M.md  7 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/STATUS_before_M.md  27 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/ap214/ap214_tol.json  0 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/ap214/ap214_tol0.0001.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/ap214/ap214_tol0.01.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/badface2.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/badfaces.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/build_inner_before_M.py  38 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/bump_clear.py  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/bump_clear_revB.json  0 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/bump_plot.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/bumps.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/clusters_finalM.log  8 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/clusters_finalM13.log  8 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/cmp.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/common_loc.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/dev_final2.log  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/dev_final3.log  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/dev_finalM.log  0 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/f02chk.py  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/fit_M.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/fit_M13_revA.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/fit_M242.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/merge_table.py  2 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/p3fit.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/q.py  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/ramp.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/ramp2.py  0 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/rwin_fixes.json  13 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/s0opt.py  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stageM/table.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/stepcheck_final.log  1 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/stepcheck_restore.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/table_revA_L11.md  18 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/table_revA_L11_final.md  19 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/table_revA_finalM.md  19 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/table_revA_finalM_merged.md  19 KB  2026-10-30
left_thigh_outer_inner/project/part 2 - Inner/work/table_revA_sim5.md  18 KB  2026-10-29
left_thigh_outer_inner/project/part 2 - Inner/work/windows.json  9 KB  2026-10-29
left_thigh_outer_inner/project/part 4 - Assembly/CLIENT_MESSAGE.txt  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/CLIENT_MESSAGE_RevB.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/LT-ASM-001_RevA_Left_Thigh_Assembly/LT-ASM-001_RevA/README.md  5 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/LT-ASM-001_RevB_Left_Thigh_Assembly/LT-ASM-001_RevB/README.md  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/LT-ASM-001_RevE_Left_Thigh_Assembly/LT-ASM-001_RevE/CAD/LT-ASM-001_Left_Thigh_Assembly.prt  101 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/LT-ASM-001_RevE_Left_Thigh_Assembly/LT-ASM-001_RevE/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242.step  5.8 MB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/STATUS.md  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/clash_faces.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/diff_clash.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/e7_package.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/e8_package_all.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/exact_bbox.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/an/fit_check.py  7 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/fit_summary.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/grid_overlap.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/joint_profile.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/locate_common.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/package.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/probe_clash.py  2 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/raster.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/an/renders.py  2 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/an/scan_probe.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/sec_check.py  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/an/sec_clash.py  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/an/sec_multi.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/stepasm_check.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/twoway_sd.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/an/zstack.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver/CAD/LT-ASM-001_Left_Thigh_Assembly.prt  69 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevB/CAD/LT-ASM-001_Left_Thigh_Assembly.prt  71 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevB/CAD/LT-ASM-001_Left_Thigh_Assembly_AP214.log  8 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevB/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242.log  5 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE/CAD/LT-ASM-001_Left_Thigh_Assembly.prt  71 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE/CAD/LT-ASM-001_Left_Thigh_Assembly_AP214.log  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE/CAD/LT-ASM-001_Left_Thigh_Assembly_AP214_check.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242_check.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE2/CAD/LT-ASM-001_Left_Thigh_Assembly.prt  101 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE2/CAD/LT-ASM-001_Left_Thigh_Assembly_AP214.log  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE2/CAD/LT-ASM-001_Left_Thigh_Assembly_AP214_check.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE2/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE2/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242.step  5.7 MB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/deliver_RevE2/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242_check.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/nx/asm1/LT-ASM-001_Left_Thigh_Assembly_AP214.log  8 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/nx/asm1/LT-ASM-001_Left_Thigh_Assembly_AP242.log  5 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/nx/asm1/build_asm.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/nx/asmB1/build_asm.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/nx/build_asm.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/nx/dwg_asm.py  29 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/nx/dwg_asm_revA.py  28 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/nx/dwg_asm_revE.py  34 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/nx/dwg_probe.py  7 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/nx/dwglib/m3d.py  19 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/nx/dwglib/ptdwg.py  12 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/LT-ASM-001_Left_Thigh_Assembly_AP214_check.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/LT-ASM-001_Left_Thigh_Assembly_AP242_check.json  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/common_revB.txt  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dump_sh1_front.json  210 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dump_sh1_iso.json  228 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dump_sh1_right.json  97 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dump_sh1_top.json  161 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dump_sh2_plan.json  160 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dump_sh2_secE.json  9 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB1/dwg_result.json  18 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB2/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB2/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB2/dump_sh1_front.json  210 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB2/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB2/dump_sh2_secE.json  9 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB2/dwg_result.json  18 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB3/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB3/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB3/dump_sh2_plan.json  160 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB3/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB3/dump_sh2_secE.json  9 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB3/dwg_result.json  18 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB4/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB4/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB4/dump_sh1_right.json  97 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB4/dump_sh1_top.json  161 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB4/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgB4/dwg_result.json  18 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run.ps1  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dump_sh1_front.json  203 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dump_sh1_iso.json  220 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dump_sh1_right.json  90 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dump_sh1_top.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dump_sh2_plan.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dump_sh2_secD.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dump_sh2_secE.json  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run1/dwg_result.json  21 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run2/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run2/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run2/dump_sh1_front.json  203 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run2/dump_sh1_iso.json  220 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run2/dump_sh1_top.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run2/dump_sh2_secE.json  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run2/dwg_result.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run3/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run3/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run3/dump_sh1_front.json  203 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run3/dump_sh2_secD.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run3/dump_sh2_secE.json  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run3/dwg_result.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run4/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run4/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run4/dump_sh1_top.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run4/dump_sh2_secD.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE/run4/dwg_result.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run.ps1  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run1/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run1/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run1/dump_sh1_right.json  489 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run1/dump_sh2_secD.json  421 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run1/dump_sh2_secE.json  415 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run1/dwg_result.json  22 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/dump_sh1_front.json  203 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/dump_sh1_iso.json  219 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/dump_sh1_right.json  89 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/dump_sh1_top.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/dump_sh2_plan.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/dump_sh2_secD.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run2/dwg_result.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/dump_sh1_right.json  89 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/dump_sh1_top.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/dump_sh2_plan.json  161 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/dump_sh2_secD.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/dump_sh2_secE.json  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run3/dwg_result.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run4/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run4/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run4/dump_sh1_front.json  203 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run4/dump_sh1_iso.json  219 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run4/dump_sh2_secD.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run4/dwg_result.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run5/LT-ASM-001_SH1.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run5/LT-ASM-001_SH2.log  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/run5/dwg_result.json  20 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/unblank.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwgE2/unblank.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_notes.md  2 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_probe1/probe_result.json  20 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/LT-ASM-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/LT-ASM-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dump_sh1_front.json  217 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dump_sh1_iso.json  233 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dump_sh1_right.json  111 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dump_sh1_top.json  161 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dump_sh2_plan.json  161 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dump_sh2_secD.json  15 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dump_sh2_secE.json  10 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run1/dwg_result.json  18 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/LT-ASM-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/LT-ASM-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/dump_sh1_front.json  217 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/dump_sh1_right.json  111 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/dump_sh2_plan.json  161 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/dump_sh2_secD.json  15 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/dump_sh2_secE.json  10 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run2/dwg_result.json  18 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run3/LT-ASM-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run3/LT-ASM-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run3/dump_sh1_top.json  161 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run3/dump_sh2_secD.json  15 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run3/dwg_result.json  18 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run4/LT-ASM-001_SH1.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run4/LT-ASM-001_SH2.log  6 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/dwg_run4/dwg_result.json  18 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/fit_AP242.json  5 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/fit_AP242.log  1 KB  2026-10-30
left_thigh_outer_inner/project/part 4 - Assembly/work/fit_revB2_AP242.json  85 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/fit_revB2_AP242.log  59 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/fit_revB_AP242.json  85 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/fit_revB_AP242.log  60 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/pre/fit_A_A.json  113 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/pre/fit_A_A.txt  79 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/pre/fit_C_A.json  112 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/pre/fit_C_A.txt  78 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/pre/fit_C_B.json  86 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/pre/fit_C_B.txt  60 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/a1_maps.log  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/a1_maps.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/a2_secs.py  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/a3_plots.py  7 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/a4_pdf.py  17 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/joint_rows.json  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/maps_summary.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/patch3.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/patch4.py  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE/patch5_renumber.py  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/a1.log  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/a1_maps.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/a2.log  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/a2_secs.py  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/a3.log  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/a3_plots.py  7 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/a4_pdf.py  18 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/joint_rows.json  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/maps_summary.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/patch_a4.py  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/patch_b.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/patch_c.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/qaE2/setup_e2.py  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/bl_render2.py  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/final/framing.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/final2/framing.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/make_section.py  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/run_final.sh  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/scene.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/trial/framing.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/renderE/views.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revB/LT-ASM-001_Left_Thigh_Assembly_AP214_check.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/revB/LT-ASM-001_Left_Thigh_Assembly_AP242_check.json  1 KB  2026-10-31
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/axes_pts.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/clash_faces_F0645.json  25 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/clash_faces_F0645.txt  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/common_revE_F0645.txt  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/build_asm_revE.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/common_final.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/fit_final_AP242.json  85 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/fit_final_AP242.log  59 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/grid_final.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/grid_final.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/joint_profile_final.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/joint_profile_final.txt  11 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/stations.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/twoway_final.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/twoway_final.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/zstack_axes_final.json  12 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final/zstack_axes_final.txt  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/final_gate.txt  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/findings_revE.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fit_report.txt  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fit_revE_F0645_AP242.json  79 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fit_revE_F0645_AP242.log  54 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/b1web_probe.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/b1web_pts.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/common_fixE_F0645.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/fit_fix.json  15 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/fit_fixE_F0645.log  58 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/fit_fixE_F0645_AP242.json  83 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/fit_report_fix.txt  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/fit_web_F0645.log  59 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/fit_web_F0645_AP242.json  85 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/grid_run2.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/grid_run3_F0645.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/grid_run4_F0645.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/grid_run5_F0645.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/j1_fit.py  18 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/j2_export.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/j3_web.py  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/jp_pxh_run2.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/pre_web/_finalize_fit_only.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/sec_ba.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/sec_res.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/sec_web.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/st_pxh.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/twoway_fixE_F0645.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/twoway_fixE_F0645.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/twoway_web_F0645.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/twoway_web_F0645.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/zstack_axes_fixE.json  11 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/zstack_axes_fixE.txt  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/zstack_axes_web.json  11 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/fix/zstack_axes_web.txt  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/grid_B_F0645.json  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/grid_B_F0645.txt  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/grid_E_C.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/grid_E_C.txt  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/grid_E_F0645.json  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/grid_E_F0645.txt  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/joint_profile_F0645.json  17 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/scan_probe_E.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/scan_pts.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/sec_spec.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/sec_spec2.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/secs.log  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/twoway_F0645.json  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/twoway_F0645.txt  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/zstack_F0645.json  9 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/zstack_F0645.txt  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/zstack_axes_F0645.json  12 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE/zstack_pts.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/asm_step/LT-ASM-001_Left_Thigh_Assembly_AP214.log  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/asm_step/LT-ASM-001_Left_Thigh_Assembly_AP242.log  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/diff/diff.json  63 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/asm_show_fix.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/build_asm_revE2.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/build_asm_revE2_try1_searchdirs.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/build_asm_revE2_try2_default.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/build_asm_revE2_try3_resaved.json  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/build_asm_revE2_try4_nospace.json  2 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/common_final.txt  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/edit_region_gaps.json  6 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/fit_final_AP242.json  80 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/fit_final_AP242.log  56 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/grid_final.json  1 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/joint_profile_final.json  14 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/joint_profile_final.txt  11 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/twoway_final.json  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/twoway_final.txt  0 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/zstack_axes_final.json  12 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final/zstack_axes_final.txt  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/final_gate.txt  7 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/j1_diff.py  8 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/j2_export_inner.py  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/j3_asm.py  4 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/j4_asm_step.py  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/j5_asm_probe.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/j6_asm_step_unblank.py  5 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/j7_asm_show.py  3 KB  2026-11-02
left_thigh_outer_inner/project/part 4 - Assembly/work/revE2/nx/run_gate.sh  1 KB  2026-11-02
left_thigh_outer_inner/transcripts/0b84b9d6-468c-4bf1-9825-a9fe39872df6.jsonl  4.9 MB  
left_thigh_outer_inner/transcripts/0bc8682e-8d44-448b-9c3f-686fd5afee34.jsonl  5.3 MB  
left_thigh_outer_inner/transcripts/0d2c6100-1580-43b6-ae46-f06fbae67218.jsonl  3.6 MB  
left_thigh_outer_inner/transcripts/0d2c6100_subagents/agent-a69b35c50e352c28a.jsonl  1.6 MB  
left_thigh_outer_inner/transcripts/0d2c6100_subagents/agent-a8527fec524aae6ac.jsonl  1.6 MB  
left_thigh_outer_inner/transcripts/0d2c6100_subagents/agent-a9f3fdca69a647d11.jsonl  1.9 MB  
left_thigh_outer_inner/transcripts/16b5c31a-0cec-4207-8e7d-60a54256edfb.jsonl  2.2 MB  
left_thigh_outer_inner/transcripts/16b5c31a_subagents/agent-aaf75a600e7d1255e.jsonl  1.6 MB  
left_thigh_outer_inner/transcripts/31f00b73-005b-4211-8150-b6bb1997b62c.jsonl  3.2 MB  
left_thigh_outer_inner/transcripts/3ab8288a-a0ca-44f8-a4cd-379fc50a1d56.jsonl  4.2 MB  
left_thigh_outer_inner/transcripts/44064e17-92e5-4b7e-96c3-b3147b9c15fb.jsonl  8.2 MB  
left_thigh_outer_inner/transcripts/573cceaf-803b-47ea-9fd7-d1253614714b.jsonl  3.3 MB  
left_thigh_outer_inner/transcripts/59b5e9a2-b2fc-467f-b35e-53a9f8822d1b.jsonl  4.0 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a015b760bf899cd9a.jsonl  1.1 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a17db94dcdc878cdc.jsonl  2.3 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a4d9243bc63901190.jsonl  1.7 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a4e79182b3cd6c571.jsonl  1.3 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a5cadabf215805765.jsonl  2.0 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a8f49338ffe7f796f.jsonl  1.2 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-aa4084d79b8aa0105.jsonl  1.4 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-ab076834102ef5892.jsonl  2.4 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-ac935ab5a17b45bee.jsonl  2.1 MB  
left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-ace49ba6f69bf9ea8.jsonl  2.5 MB  
left_thigh_outer_inner/transcripts/73a8eec7-2f5f-4c5c-9197-d0335b8bd7e9.jsonl  4.2 MB  
left_thigh_outer_inner/transcripts/8df73ba3-5f57-4b8f-9817-3ffd2b7d1b48.jsonl  4.8 MB  
left_thigh_outer_inner/transcripts/95e57f8d-20aa-48f7-b606-7603564c4149.jsonl  6.8 MB  
left_thigh_outer_inner/transcripts/b1cdd1bf-e83d-45d5-b41a-7c77300df7ed.jsonl  6.6 MB  
left_thigh_outer_inner/transcripts/cbeb69e1-3925-4bc3-a39e-ca3ccf77ef15.jsonl  2.0 MB  
left_thigh_outer_inner/transcripts/ce4111eb-7800-4338-93cc-82432a64c70b.jsonl  3.8 MB  
left_thigh_outer_inner/transcripts/efca19c7-6606-43a7-bebe-4b6e6a2431cd.jsonl  6.6 MB  
left_thigh_outer_inner/transcripts/f71cbaea-f2f1-42f0-bb9c-9e1f593c2b75.jsonl  4.8 MB  
left_thigh_outer_inner/transcripts/ff91f392-c6c7-4a37-9c44-40e4960ba29f.jsonl  2.7 MB  
left_thigh_outer_inner/ws/lt_conn/Thight_conn_pad.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/cfit.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/cfit2.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/close.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/cplot.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/cplot2.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/crop.py  0 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/deps.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/deps2.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/dev.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/dfit.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/fit.py  1 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/fit2.json  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/fit2.py  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/fit3.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/hfit.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/hmap.py  1 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/hmap2.py  1 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/lab.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/probe.py  2 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/probe/probe.json  5 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/r2/out_fix_r2.json  5 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/r2/probe.json  8 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/r4/deps.json  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/r4/deps2.json  5 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/rend.py  1 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/rnew.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/rview.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/sec.py  1 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/sec2.py  2 KB  2026-10-30
left_thigh_outer_inner/ws/lt_conn/secs.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_conn/verify2.py  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_fitE/deliver/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_fitE/deliver/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_fitE/deliver/LT-INN-001_Left_Thigh_Inner_AP242.step  3.2 MB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_fitE/run2/fit_fix.json  16 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_fitE/run3/fit_fix.json  15 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_fitE/run4/fit_fix.json  15 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_pins/a1_probe.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/a2_radial.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/a3_side.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/a4_fit.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/a5_sec.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/a6_zmap.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/fits.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/fitsA.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/j1_inspect.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/j2_add.py  11 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/r1/inspect.json  8 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/r2/add.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/r3/add.json  14 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/r3/verify.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/a5b_sec.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/a6b_zmap.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/a7_oblique.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/j1b_look.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/j3_add.py  7 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/r1/look.json  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/r2/add.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/r3/add.json  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round2/r4/add.json  8 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/a5c_sec.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/a9_radial.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/clusters_hi.json  16 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/hl_low.json  12 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/j4_faces.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/j4b_faces.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/j5_owner.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/j6_band.py  8 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/j7_knee.py  6 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/j8_knee_bool.py  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/j9_group.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/lab_all.json  41 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/lab_hi.json  7 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/owners_m.json  297 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r1/owners.json  371 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r2/band.json  12 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r2i/hl.json  14 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r2i/small_ids.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r3/knee.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r4/kneeb.json  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r5/kneeb.json  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r5i/small_ids.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/r6/group.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/small_groups.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/small_ids.json  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/v3_crop.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round3/v4_persp.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/j10_lip.py  5 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/j11_delete.py  6 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/j12_targets.py  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/j9b_group.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/lab5.json  6 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/lip_chains.json  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r1/lip.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r1i/small_ids.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r2/del_knee.json  7 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r3/del_knee2.json  5 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r4/del_knee3.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r5/del_band.json  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r5i/faces.json  511 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r6/targets.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/r7/group.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/targets1.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/zone_band.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/zone_knee.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/zone_knee2.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/round4/zone_knee3.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/spots.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/spots2.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/v1_overview.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_pins/v2_verify.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_r8/a10_check.py  3 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a1_dev.py  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a2_m1.py  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a3_hm.py  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a4_sec.py  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a4m_sec.py  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a5_lug.py  3 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a6_hole.py  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a7_knee.py  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a8_rsec.py  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/a9_lugcap.py  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/c5_dev.json  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/j0_inspect.py  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/j1_faces.py  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/j2_r8.py  20 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/lugcap.json  0 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/m1_lug.json  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r0/inspect.json  7 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r0b/inspect.json  7 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r1/j0.json  47 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r1b/j0.json  47 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r2/j2.json  4 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r3/j2.json  3 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r4/j2.json  3 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/r5/j2.json  3 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/run.ps1  0 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/t0_dev.json  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_r8/v1_user.py  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_revB/deps.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/f1/lipfix.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/f2/lipfix_end.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/h1/hipfix.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/j1_deps.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/j2_unscan.py  4 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/j3_lipfix.py  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/j4_lipfix_end.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/j5_hipfix.py  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/lipfix/chain3_fixed.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/lipfix/chain3_fixed2.json  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/mkrender.py  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/old_cad/_finalize.json  0 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/old_cad2/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/old_cad2/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/old_cad2/_finalize.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/old_cad3/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/old_cad3/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/old_cad3/_finalize.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/status_revB.md  3 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/stepdbg/cmp_step.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/stepdbg/common_loc.py  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/stepdbg/vol_step.py  2 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/u1/unscan.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/u2/unscan.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/u3/unscan.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/u4/unscan.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/u5/unscan.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revB/u6/unscan.json  1 KB  2026-10-31
left_thigh_outer_inner/ws/lt_inner_revE/_outer_finalize_revF_ref.py  28 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_revE/i1_inspect.json  5 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_revE/i1_inspect.py  5 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/a10_arc.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a11_rail.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a12_view2.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a13_zone_map.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a14_view3.py  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/a15_blends.py  5 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/a1_missing.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a2_hmap.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a3_zone.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a4_secs.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a5_user_view.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a6_feat.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a6b_feat.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a7_polar.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a8_skel.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/a9_rib.py  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/b1_spec.py  12 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/b2_spec.py  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/b3_slab.py  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/b4_slab.py  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/dbg_dof.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/dbg_run.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/j1_ribs.py  12 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/j2_more.py  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/j3_final.py  10 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/m0/missing_clusters.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/arc_ARC.json  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/arc_KBAND.json  13 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/arc_KIN.json  11 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/arc_KOUT.json  13 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_ABAR.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_ASMALL.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_CROSS.json  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_DIAG.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_DWALL.json  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_END.json  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_F10.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_F65.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_F97.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_FM24.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_LONG.json  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_OR108.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_OR155.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_OR160.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_OR20.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_OR327.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_R108.json  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_RAILI.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_RAILO.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_S130.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_S193.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_SP108.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_SP160.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_SP20.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_SP225.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_SP230.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m1/rib_SP325.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/m6/rail_holes.json  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/r1/dbg.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r1/dbg2.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r1/dof.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r1/j1.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r2/inspect.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r3/j2.json  6 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r4/j2.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r5/j2.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r6/j2.json  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/r7/inspect.json  7 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/r8/j3.json  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/run.ps1  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec.json  19 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec2.json  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec3.json  20 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec4.json  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec5.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec6.json  9 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec7.json  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_inner_ribs/spec_dbg.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_ribs/spec_knee.txt  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a10_inside.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a11_tip.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a12_chain.py  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a13_checks.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a14_compare.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a15_boss.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a15b.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a1_diff.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a2_show.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a3_win.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a4_wall.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a5_sec.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a6_outline.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a7_fit.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a8_tongue.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/a9_secz.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/j0b_tube.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/j0c_bodies.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/j1_windows.py  9 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/checks.json  34 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/clusters.json  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/inspect.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/outlines.json  106 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/profiles.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/tip.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/tip75.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r0/tube.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r1/j1.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r2/bodies.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/r2/j1.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_inner_win/run.ps1  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_revE2/probe/B_AP214.log  4 KB  2026-11-02
left_thigh_outer_inner/ws/lt_revE2/probe/probe.json  1 KB  2026-11-02
left_thigh_outer_inner/ws/lt_revE2/testE/LT-ASM-001_Left_Thigh_Assembly_AP214.log  8 KB  2026-11-02
left_thigh_outer_inner/ws/lt_revE2/testE/LT-ASM-001_Left_Thigh_Assembly_AP242.log  5 KB  2026-11-02
left_thigh_outer_inner/ws/lt_revE2/testE/test.json  2 KB  2026-11-02
left_thigh_outer_inner/ws/lt_ribs3/a1_missing.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a2_devmap.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a3_sec.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a4_zsl.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a5_fit4.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a6_polar.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a7_cont.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a8_attach.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/a9_dev.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/j1_add.py  15 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/missing.json  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/pad_wall.json  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r0.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r0_state.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r1/dev_zones.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r1/j1.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/a1.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/a2.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/a3_sec.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/a4_zsl.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/b1_wall.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j0.json  33 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j0_faces.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j0b.json  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j0b_endface.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j2.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j2_wall.py  13 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j3.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j3_wall.py  11 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j4.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/j4_m1_lip.py  6 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/v4.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/v5_match.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/v6_wall.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/r2/v7_final.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/run.ps1  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v10_zoom.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v10b.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v1_views.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v2_views.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v3_persp.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v4_zone.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v5_grid.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v6_match.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v7_match.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v8_block.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/v9_check.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_ribs3/zones.sh  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a10_extra.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a11_through.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a12_show.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a13_show.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a1_gap.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a2_plot.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a3_gapn.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a4_plot.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a5_wall.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a6_sec.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a7_render.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a8_close.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/a9_rays.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b1_prof.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b2_ysec.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b3_wall.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b4_fit.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b5_cmp.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b6_island.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b7_fill.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b8_ask.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/b9_check.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/bottom_fit.json  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/c1_outline.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/c2_wallprof.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/c3_edge.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/c4_fit.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/c5_tool.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/c6_show.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/clusters.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f10_render.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f1_map.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f2_view.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f3_zoom.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f3_zoom2.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f4_slices.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f5_label.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f6_side.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f7_meas.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f8.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f8_build.py  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/f9_check.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat2/meas.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/clusters.json  8 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/f4_slices.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g10_render.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g1_view.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g2_land.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g3_polar.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g4_padmask.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g5.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g5_build.py  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g6.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g6_g18.py  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g7_check.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g8.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g8_cutfix.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g9.json  24 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/feat3/g9_diff.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/fit.json  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j0.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j0_export.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j0w.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j0w_export.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j1.json  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j1_probe.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j2.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j2_live.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j2_win.py  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j3.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j3_state.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j4_live.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j4_undo_recheck.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j5.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j5_live.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j5_side_window.py  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j6_live.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j6_state.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j7_live.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j7_undo_side.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j8_live.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/j8_redo.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/notch_edge.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/missing_clusters.json  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r0.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r10_faces.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r11_spec.py  6 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r12.json  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r12_ribs.py  5 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r13.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r13_debug.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r14.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r14_debug2.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r15.json  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r15_debug3.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r16_check.py  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r17_render.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r1_missing.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r2_map.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r3_top.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r4_sections.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r5_measure.py  4 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r6_side.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r7_side1.py  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r8_zoom.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/r9_render.py  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/rib_check.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/rib_faces.json  2 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/rib_lines.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/rib_meas.json  17 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/rib_spec_report.json  3 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/ribs/rib_tops.json  7 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/run.ps1  0 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/window_checks.json  1 KB  2026-11-01
left_thigh_outer_inner/ws/lt_window/window_poly.json  40 KB  2026-11-01
```

### left_thigh_clean_rebuild (nx_re_projects_20261105_part3.zip)
```
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/CLIENT_MESSAGE.txt  2 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/HANDOVER.md  6 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/LT-ASM-001_RevC_Left_Thigh_Clean_Rebuild/LT-ASM-001_RevC/QA/REPORT.md  3 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/LT-ASM-001_RevC_Left_Thigh_Clean_Rebuild/LT-ASM-001_RevC/QA/fit_check_AP242.json  58 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/LT-ASM-001_RevC_Left_Thigh_Clean_Rebuild/LT-ASM-001_RevC/README.md  5 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/LT-ASM-001_RevC_Left_Thigh_Clean_Rebuild/LT-ASM-001_RevC/Renders/LT-ASM-001_assembly_side.png  207 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/LT-ASM-001_RevC_Left_Thigh_Clean_Rebuild/LT-ASM-001_RevC/Renders/LT-ASM-001_assembly_top.png  247 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/LT-ASM-001_RevC_Left_Thigh_Clean_Rebuild/LT-ASM-001_RevC/Renders/LT-OUT-001_open_side.png  271 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/LT-ASM-001_RevC_Left_Thigh_Clean_Rebuild/LT-ASM-001_RevC/Renders/exterior_knee_junction_gloss.png  172 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/PLAN.md  6 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/deliver/CAD/LT-ASM-001_Left_Thigh_Assembly.prt  69 KB  2026-10-31
left_thigh_clean_rebuild/project/part 5 - Clean Rebuild/knee_junction_zebra_before_after.png  252 KB  2026-10-31
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/CLIENT_MESSAGE.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/CAD/fit_check_AP214.json  62 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/CAD/fit_check_AP242.json  62 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/CAD/fit_check_AP242.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Deviation_Check/README.md  2 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Deviation_Check/overlay_inn_side_MX.png  151 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Deviation_Check/overlay_inn_side_PX.png  157 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Deviation_Check/overlay_out_inside_iso.png  297 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Deviation_Check/overlay_out_side_MX.png  191 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Deviation_Check/overlay_out_side_PX.png  196 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Drawings/LT-ASM-001_SH2.pdf  288 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Drawings/LT-INN-001_SH1.pdf  260 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Drawings/LT-INN-001_SH2.pdf  172 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Drawings/LT-INN-001_SH3.pdf  249 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Drawings/LT-OUT-001_SH1.pdf  293 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Drawings/LT-OUT-001_SH2.pdf  208 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Drawings/LT-OUT-001_SH3.pdf  231 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/REPORT.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/c4_out_trough_end.png  70 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_inn_inside_a.png  181 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_inn_inside_b.png  213 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_inn_outside_MX.png  72 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_inn_outside_PX.png  78 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_inn_outside_end.png  151 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_out_inside_a.png  182 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_out_inside_b.png  199 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_out_outside_MX.png  87 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_out_outside_PX.png  88 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/cad_out_outside_end.png  155 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/clean.txt  17 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/curv_inn_PX.png  201 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/curv_out_PX.png  164 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_cad_inn_MX.png  199 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_cad_inn_PX.png  207 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_cad_out_MX.png  219 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_cad_out_PX.png  207 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_scan_inn_MX.png  244 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_scan_inn_PX.png  252 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_scan_out_MX.png  284 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/dev_scan_out_PX.png  247 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/fit.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/gates_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/gates_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/joint.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/scanonly.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/step.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/surf.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/trough_map_above.png  35 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/trough_slots.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_inn_A_side_PX.png  78 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_inn_B_side_MX.png  71 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_inn_C_knee_end.png  202 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_inn_D_hip_end.png  169 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_oldmaster_inn_PX.png  92 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_oldmaster_out_PX.png  95 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_out_A_side_PX.png  72 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_out_B_side_MX.png  74 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_out_C_knee_end.png  182 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zebra_out_D_hip_end.png  166 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/QA/zones.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/README.md  3 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Renders/LT-ASM-001_assembly_side.png  216 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Renders/LT-ASM-001_assembly_top.png  232 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Renders/LT-INN-001_open_side.png  282 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/LT-ASM-001_RevD_Left_Thigh_Clean_Rebuild_v2/LT-ASM-001_RevD/Renders/LT-OUT-001_open_side.png  236 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/PLAN.md  7 KB  2026-10-31
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/STATUS.md  16 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/deliver/CAD/LT-ASM-001_Left_Thigh_Assembly.prt  69 KB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/deliver/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242.step  11.6 MB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/deliver/CAD/LT-INN-001_Left_Thigh_Inner_AP242.step  6.3 MB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/deliver/CAD/LT-OUT-001_Left_Thigh_Outer_AP214.step  19.6 MB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/deliver/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.step  5.2 MB  2026-11-01
left_thigh_clean_rebuild/project/part 7 - Clean Rebuild v2/deliver/Drawings/LT-ASM-001_dwg.prt  2.0 MB  2026-11-01
left_thigh_clean_rebuild/transcripts/19347876-9481-4f4e-a75e-2bc6cabc101a.jsonl  1.2 MB  
left_thigh_clean_rebuild/transcripts/3033883f-e5da-49aa-ba46-0959f5877aec.jsonl  8.5 MB  
left_thigh_clean_rebuild/transcripts/70a6170f-431d-4fc0-badb-2b1e168f4d7f.jsonl  6.6 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a0041aff47ce0c215.jsonl  969 KB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a0106b85c7018d2e2.jsonl  1.8 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a1f9995a5aed39338.jsonl  1.3 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a238c3bedad6c3592.jsonl  1.3 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a3f4779099fc8bf66.jsonl  1.5 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a4bb719d1bfac111b.jsonl  1.2 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a4d5a2fad8d59856e.jsonl  842 KB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a4fdaaae73467fe3a.jsonl  981 KB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a57c16b73c34e232a.jsonl  980 KB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a59c429d64bbc449f.jsonl  966 KB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a5d35caf06aa5ff17.jsonl  3.1 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a71c83d601930cb5f.jsonl  1.2 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a748ed694cc3b3530.jsonl  1.3 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a8533e0a9cca368f3.jsonl  948 KB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a88e863a39fceae05.jsonl  1.5 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a8f17b3695fc6bbc1.jsonl  1.2 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a9ae09921d8e7b173.jsonl  1.9 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-aa5db575c1cb6bef1.jsonl  1.6 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-aad929d033d65989c.jsonl  2.0 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ab344e8350c227d9d.jsonl  2.1 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ab42ed3d5133aa6a1.jsonl  1.7 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ab67c709a0a5ddc3b.jsonl  1.3 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-abae97bf9c7754c80.jsonl  2.5 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ac18347f832f8473e.jsonl  1.6 MB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ac71346f34d4e9028.jsonl  974 KB  
left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-afc6285e6fb7ed567.jsonl  1.8 MB  
left_thigh_clean_rebuild/transcripts/beb3588c-5290-4dc4-bb96-26eae9eebd4c.jsonl  9.4 MB  
left_thigh_clean_rebuild/ws/lt_clean/an/a1_views.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a2_secs.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a3_drum.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a4_wall.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a5_ext.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a6_look.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a7_hmap.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a8_drum_fit.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/a9_joint.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b1_fit.py  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b2_fit.py  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b3_envdev.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b3_smooth.py  8 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b4_curv.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b4_zoom.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b5_jointmap.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b6_plan.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b7_rz.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b8_hiprz.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/b9_tongue.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c1_depth.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c2_plan2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c3_xsec.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c4_rib.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c5_levels.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c6_depthzoom.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c7_ribtop.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c8_side.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/c9_render.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/d1_dev.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/d2_seams.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/d3_fit.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/d4_cmp.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/d5_surf.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/e1_show.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/lib.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/package.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/an/rays.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/LT-ASM-001_Left_Thigh_Assembly_AP214.log  16 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/LT-ASM-001_Left_Thigh_Assembly_AP242.log  10 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/LT-INN-001_Left_Thigh_Inner_AP214.log  12 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/LT-INN-001_Left_Thigh_Inner_AP242.log  10 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/LT-OUT-001_Left_Thigh_Outer_AP214.log  12 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/LT-OUT-001_Left_Thigh_Outer_AP242.log  10 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/_finalize_inn.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/deliver/CAD/_finalize_out.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A1/stageA_inn.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A1/stageA_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A3/stageA_inn.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A3/stageA_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A4/stageA_inn.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A5/stageA_inn.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A6/stageA_inn.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A8/stageA_inn.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A8/stageA_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A9/stageA_inn.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/A9/stageA_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P1/build_inn.json  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P1/build_out.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P10/build_inn.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P10/build_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P11/build_inn.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P11/build_out.json  8 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P12/build_inn.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P12/build_out.json  8 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P13/build_inn.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P13/build_out.json  8 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P14/build_inn.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P14/build_out.json  8 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P15/build_inn.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P15/build_out.json  9 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P2/build_inn.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P2/build_out.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P3/build_inn.json  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P3/build_out.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P4/build_inn.json  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P4/build_out.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P5/build_inn.json  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P5/build_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P6/build_inn.json  12 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P6/build_out.json  9 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P7/build_inn.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P7/build_out.json  8 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P8/build_inn.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P8/build_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P9/build_inn.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/P9/build_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/T5/build_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/T6/build_out.json  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/T7/build_out.json  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/T8/build_out.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/_edit_dims.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/_edit_tables.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/_seams_add.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/_tabs_add.py  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/asm/asm.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/b_base.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base1/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base2/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base3/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base4/base.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base5/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base6/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base7/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base8/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/base9/base.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/build_asm.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/design.py  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dump_sh1_front.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dump_sh1_iso.json  82 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dump_sh1_right.json  64 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dump_sh1_top.json  51 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dump_sh2_plan.json  52 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dump_sh2_secE.json  10 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA1/dwg_result.json  18 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dump_sh1_front.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dump_sh1_iso.json  83 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dump_sh1_right.json  64 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dump_sh1_top.json  53 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dump_sh2_plan.json  53 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dump_sh2_secE.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA2/dwg_result.json  18 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/dump_sh1_right.json  64 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/dump_sh1_top.json  53 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/dump_sh2_plan.json  53 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/dump_sh2_secE.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA3/dwg_result.json  18 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA4/LT-ASM-001_SH1.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA4/LT-ASM-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA4/dump_sh1_front.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA4/dump_sh2_secD.json  13 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA4/dump_sh2_secE.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgA4/dwg_result.json  18 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI1/LT-INN-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI1/LT-INN-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI1/LT-INN-001_SH2.pdf  151 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI1/LT-INN-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI1/LT-INN-001_SH4.log  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI1/dwg_result.json  10 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI2/LT-INN-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI2/LT-INN-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI2/LT-INN-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI2/LT-INN-001_SH4.log  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI2/dwg_result.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI3/LT-INN-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI3/LT-INN-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI3/LT-INN-001_SH2.pdf  151 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI3/LT-INN-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI3/LT-INN-001_SH4.log  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI3/dwg_result.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI5/LT-INN-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI5/LT-INN-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI5/LT-INN-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI5/LT-INN-001_SH4.log  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgI5/dwg_result.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO1/LT-OUT-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO1/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO1/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO1/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO1/dwg_result.json  18 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO2/LT-OUT-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO2/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO2/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO2/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO2/dwg_result.json  17 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO3/LT-OUT-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO3/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO3/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO3/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO3/dwg_result.json  17 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO5/LT-OUT-001_SH1.log  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO5/LT-OUT-001_SH2.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO5/LT-OUT-001_SH3.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO5/LT-OUT-001_SH4.log  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwgO5/dwg_result.json  17 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwg_asm.py  29 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwg_inn.py  37 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/dwg_out.py  38 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/finalize.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/insp/insp.json  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/insp_stl.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/ltenv.py  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/ltint.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/ltjoint.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/p_build.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/p_stageA.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/p_stageB.py  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_A3_parts.ps1  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_all.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_base_A.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_deliver.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_dwgs.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_dwgs_parts.ps1  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_finalize.ps1  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_from_base.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_parts.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/run_parts_only.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/stages.py  47 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t1/t1.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t1_env.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t2/t2.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t2_drum.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t3/t3.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t3_eval.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t4/t4_0.05.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/nx/t4_speed.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/qa/fit_AP242.log  41 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/drum.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/fit_P11.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/fit_P12.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/fit_P13.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/fit_P14.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/fit_P15.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/fit_P3.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/fit_P4.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/knee_rz.png  65 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_nu1_mu1.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_nu1_mu3.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_nu3_mu1.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_nu3_mu3.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_v8_wv20.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_v8_wv5.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_wb1.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_wb1000.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/s_wb3.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/seams.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/seams_pts.json  20 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_lk1e-2.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_lk1e-2_s.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_lk3e-3.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_lk3e-3_s.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_np24.json  37 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_np24rc24.json  37 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_np40.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v2.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_mu0.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_mu1.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_mu10.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_mu3.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_mu30.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_mu300.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_wv0.1.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3_wv0.3.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v3raw.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v5.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v5_nu0.05.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v5_nu0.5.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v5raw.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v6.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v7.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v7raw.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/sections_v9raw.json  60 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/tmp.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean/work/tmp_v1.json  59 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/COMMON.md  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/FEATURES_inn.json  108 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/FEATURES_out.json  56 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/dt_tighten.py  10 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/g_gates.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_a0.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_a1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_a2.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_blk1.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_blk2.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_blk3.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_blk4.py  10 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_blk5.py  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_blk6.py  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_common.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_core.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_dump.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_final.py  9 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_fit.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_help.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_res.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_rib.py  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_run.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_run_t.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t1.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t10.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t11.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t12.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t13.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t14.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t15.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t16.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t17.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t18.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t19.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t20.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t3.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t4.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t5.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t6.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t7.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t8.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i1_t9.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_00_overview.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_01_zoom.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_02_levels.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_03_ring.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_10_bosses.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_11_ribs.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_12_pins.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_13_knee.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_14_knee_b.py  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_15_knee_c.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_16_hip_tabs.py  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_17_seams_lip.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_18_missing.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_18b_missing2.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_19_roots.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_20_residual.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_21_resmap.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_30_collect.py  16 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_31_plots.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_32_uncov.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_33_report.py  9 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_common.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_fit.py  15 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_rows.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_sec.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t1.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t10.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t11.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t12.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t13.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t14.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t15.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t16.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t17.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t18.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t19.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t22.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t23.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t24.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t25.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t26.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t27.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t28.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t29.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t3.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t30.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t31.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t32.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t33.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t34.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t35.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t36.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t4.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t40.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t5.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t6.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t7.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t8.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_t9.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/i2_view.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/lib.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_a_explore.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_b_sec.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_c_axis.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_d_profile.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_e_ends.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_f_planes.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_g_top.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_h_cone.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_i_joint.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_j_edges.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_k_map.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_l_zoom.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_m_axis2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_n_boundary.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_o_rtheta.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_p_edges2.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_q_fit.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_r_design.py  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_s_grid.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_t_centres.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_u_grid0.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_w_runs.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_x_final.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_y_outputs.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_z_boundary.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_zz_p5.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m1_zzz_write.py  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_a_view.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_b2_chk.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_b_ext.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_c_ext.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_d_secs.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_e_ext.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_f_data.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_g_fit.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_h_map.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_i_secchk.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_j_sweep.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_k_zoom.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_l_groove.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_loft.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_m_band.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_n_edges.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_o_fitband.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_p_bandwall.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_q_env.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_r_curv.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_s_map.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_t_drum.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_u_knee.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_v_pxarc.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_w_wall.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_x_early.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_y_wallstat.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_z_hip.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_za_ext2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_zb_long.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_zc_feat.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_zd_hipband.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_ze_hipmap.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_zf_gaps.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_zg_json.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m2_zz_final.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_a_ysec.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_b_rprof.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_c_rprof2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_d_mask.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_e_ry.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_f_mouth.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_g_circ.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_h_dev.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_i_polar.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_j_resid.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_k_zoom.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_l_svd.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_m_prof.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_n_cmp.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_o_four.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_p_ell.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_q_quad.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_r_ellres.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_s_loft.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_t_feat.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_u_flank.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_v_shade.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_w_flprof.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_x_flank2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_y_seam.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_z_plate.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_za_ring.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zb_wall.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zc_wall2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zd_search.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_ze_holes.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zf_hz.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zg_join.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zh_kink.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zi_crease.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zj_cone.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zk_cone2.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zl_int.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zm_innplate.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zn_ruled.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m3_zo_plots.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_a_planes.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_b_tilt.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_c_plan.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_d_xsec.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_e_stations.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_f_profiles.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_g_maps.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_h_extract.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_i_masks.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_j_dev.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_k_break.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_l_p5cmp.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_m_lostmap.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_n_perim.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_p_segs.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_q_zoom.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_r_json.py  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_s_edge.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_t_cause.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_u_levels.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_v_final.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m4_x.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_a.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_b.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_c.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_d.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_e.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_f.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_g.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_h.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_i.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_j.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_k.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_l.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_m.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_n.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_o.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_p.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_q.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_r.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_s.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_t.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_u.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_v.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/m5_w.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/p3_cmp.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/p3_thick.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_cad2scan.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_cone.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_fit.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_masks.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_panel.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_pts.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_render2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p4_tt.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_hip.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_loc.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_loc2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_loc3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_loc4.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_pin.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_ray.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_rayxy.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_sub.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_tab.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5a_table.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5b_ear.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5b_loc.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5b_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5b_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5b_table.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5c_breach.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5c_render.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5c_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5c_secs.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5c_table.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_bowl.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_clip.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_loops.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_open.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_overlap.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_rootfit.py  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_rootmeas.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_roottable.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam0.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam1.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam3.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam4.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam5.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam6.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seam7.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_seamchk.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_show.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_trough.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_trough_end.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p5d_write_design.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/p9_overlay.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_clean.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_fit.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_joint.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_maps.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_scanonly.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_step.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_surf.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_trough.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_trough2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_zebra_old.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/q7_zones.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_check.py  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_cyl.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_edge.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_ends.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_fit.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_fit2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_fit3.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_meas.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_plane.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_plane2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_pts.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_strip.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_tail.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_tail2.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_tailchk.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/r1_zones.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_bad.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_bad2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_base.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_build.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_c2s.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_cells.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk1.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk2.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk3.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk4.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk5.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk6.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk7.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk8.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_chk9.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_cone.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_cone2.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_conedef.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_crease.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_curv.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_curv2.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_data.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_eval.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_final.py  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_fine.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_fit.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_fit2.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_geo.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_hip0.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_knee_secs.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_lib.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_map.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_pershell.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_secs.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell3.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell4.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell5.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell6.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell7.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell8.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shell9.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_shellproxy.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_snap.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_t0.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_t1.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_t3.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_t4.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_tail.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_tail2.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_tail3.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_tailsheet.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_view0.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_view1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/s1_zebra.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/stages_consts.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_a.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_bot.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_c.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_chk.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_d.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_e.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_end.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_f.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_fit.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_g.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_h.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_i.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_j.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_junc.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_junc2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_k.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_l.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_panel.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_probe.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_r.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_si.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_tail.py  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t5_ys.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_chain.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_cmp.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_env.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_fit.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_hole.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_hole2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_log.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/t6_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_curv.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_curv2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_curv3.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_hipmiss.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_nxprev.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_render.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_ridge.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_sec_px.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_seccurv.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_selfint.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_selfint2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_tail.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_tailwall.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_valid.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_valid2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_wall.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_wallmiss.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_zebra.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v3_zones.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_edge.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_hipjoint.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_joint.py  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_ledge.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_panel.py  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_panel2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_render2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_tail.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_tail2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_valid.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_zones.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_zones_ext.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4_zones_ext2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_axial.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_corner.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_depthmap.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_edge.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_edge2.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_edge3.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_panel.py  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_render2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_render3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_render4.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_runout.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_selfx.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_strip.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_tail.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_tail2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_tip.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_zones_ext.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v4r1_zones_ext2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m1.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m10.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m11.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m11b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m1b.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m1c.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m4.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m5.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m5b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m6.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m6b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m6d.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m6e.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m6f.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m6g.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m7.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m8.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m8b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m9.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_m9b.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_masks.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_mlib.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_ray.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_reg.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_reg2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_reg3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_render.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_sec3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_valid.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5a_valid2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_corner.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_grid.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_hole.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_hole2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_hole3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_hole4.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_lib.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m1.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m4.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m5.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m5b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m6.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m6b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m7.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m8.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m9.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m9b.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_masks.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_pad.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_reg.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_render.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_step.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_step2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_tail.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_valid.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_dip.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_dipcmp.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_dipfit.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_dipsk.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_extra.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_loops.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_lug.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_m3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_m4.py  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_m4b.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_masks.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_mxprof.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_open.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_pad.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_post.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_seam.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_seam2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_skin.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_thick.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_valid.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5c_wall.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_extra.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_extra2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_loops.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_lug.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_m4.py  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_mxprof.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_occ.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_open.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_overlap.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_overlap_prev.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_pad.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_render2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_roots.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_seam.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_sec.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_skin.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_thick.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_v4.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5d_wall.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_clip.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_dip.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_extra2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_loops.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_lug.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_m4.py  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_mx.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_mxprof.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_open.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_overlap_prev.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_pad.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_render2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_roots.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_seam.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_skin.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_thick.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_trough.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_trough2.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_trough3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_v4.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_valid.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/v5e_wall.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/an/z0_baseline_zones.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/an/z0b.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/BUILD_P4.txt  16 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/BUILD_P4_r0.txt  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/cad2scan.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/fit_check.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/masks_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/masks_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/panel_pts.json  21 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/panel_pts_r0.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/stageA_inn.json  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/stageA_inn_r0.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/stageA_out.json  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/A_v2/stageA_out_r0.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/BUILD_P5a.txt  18 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/build_inn.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/build_out.json  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/gates_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/gates_inn_v2.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/gates_inn_x.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/gates_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/gates_out_v2.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/gates_out_x.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/mask_table.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a/run_p5a.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a_prev/build_inn.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a_prev/build_out.json  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a_prev_r1/build_inn.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5a_prev_r1/build_out.json  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/BUILD_P5b.txt  9 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/block_p5b.py  13 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/build_inn.json  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/build_out.json  9 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/chain.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/chain.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/chain2.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/chain2.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/chain2_done.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/chain_done.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/dbg.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/dbg2.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/design2_before_P5b.py  27 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/design2_before_P5c.py  31 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/edit2.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_inn_r1.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_inn_x.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_inn_x_r1.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_out_r1.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_out_x.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/gates_out_x_r1.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/mask_table_inn.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/mask_table_inn_r1.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/mask_table_out.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/mask_table_out_r1.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/p5a_regression.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/prev_block.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/run_inn.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/run_p5b.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/splice.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/stages2_before_P5b.py  27 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/stages2_before_P5c.py  44 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b/stages2_pre_dbg.py  44 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b_prev/build_inn.json  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b_prev/build_out.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b_prev/run_p5b.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b_prev2/build_inn.json  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5b_prev2/build_out.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/BUILD_P5c.txt  11 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/block_p5c.py  17 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/build_inn.json  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/build_out.json  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/chain.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/chain_b.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/chain_inn.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/chain_r1.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/chain_r1.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/design2_pre_lug.py  35 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_c2_done.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_done.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_inn_c2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_inn_c3.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_inn_c4.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_out_c2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_out_c3.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/gates_out_c4.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/mask_table_inn.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/mask_table_inn_c3.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/mask_table_inn_c4.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/mask_table_out.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/mask_table_out_c3.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/mask_table_out_c4.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/rpt.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c/run_p5c.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c_prev/build_inn.json  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5c_prev/build_out.json  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/BUILD_P5d.txt  25 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/build_inn.json  17 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/build_out.json  11 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/chain_c2.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/chain_d.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/chain_e.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/chain_e.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/chain_f.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/chain_g.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/chain_h.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/design2_before_P5d.py  35 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/finalize_inn.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/finalize_out.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/finalize_run.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/gates_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/gates_inn_full.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/gates_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/gates_out_full.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/mask_table_inn.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/mask_table_out.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/out_keep/build_out.json  9 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/probe2/out_faces.json  84 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/probe_edges.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/probe_faces.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/run_p5d.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/run_probe.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/run_probe_faces.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/show_build.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d/stages2_before_P5d.py  66 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev/BUILD_P5d.txt  16 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev/build_inn.json  17 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev/finalize_inn.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev/finalize_out.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev/mask_table_inn.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev/mask_table_out.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev/run_p5d.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/BUILD_P5d.txt  21 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/build_inn.json  17 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/build_out.json  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/finalize_inn.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/finalize_out.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/gates_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/gates_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/mask_table_inn.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P5d_prev2/mask_table_out.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/asm_result.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/bad.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/build_asm.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/LT-ASM-001_Left_Thigh_Assembly_AP214.log  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/LT-ASM-001_Left_Thigh_Assembly_AP242.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/LT-INN-001_Left_Thigh_Inner_AP214.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/LT-INN-001_Left_Thigh_Inner_AP242.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/LT-OUT-001_Left_Thigh_Outer_AP214.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/LT-OUT-001_Left_Thigh_Outer_AP242.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/_export_inn.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/cad/_export_out.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/exp_part.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/fit214.log  44 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/fit_check.py  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/fit_summary.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/rt.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/rt_inn.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/run_asm.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/run_asm.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/run_p6.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/run_p6.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/t242.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/t242/inn_ap242_tol0.0001.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/t242/inn_ap242_tol0.01.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/valid.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P6/wd/rt_ap214_check_tmp.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain1.log  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain1.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain2.log  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain2.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain3.log  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain3.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain4.log  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/chain4.ps1  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/data/outline_inn.json  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/data/outline_out.json  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/data/params_inn.json  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/data/params_out.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/LT-ASM-001_SH1.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/LT-ASM-001_SH1.pdf  332 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/LT-ASM-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/LT-ASM-001_SH2.pdf  288 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dump_sh1_front.json  88 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dump_sh1_iso.json  104 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dump_sh1_right.json  87 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dump_sh1_top.json  71 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dump_sh2_plan.json  71 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dump_sh2_secD.json  14 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dump_sh2_secE.json  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA1/dwg_result.json  18 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA2/LT-ASM-001_SH1.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA2/LT-ASM-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA2/dump_sh1_iso.json  104 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA2/dump_sh2_plan.json  71 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA2/dump_sh2_secD.json  14 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgA2/dwg_result.json  18 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/LT-INN-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/LT-INN-001_SH1.pdf  256 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/LT-INN-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/LT-INN-001_SH2.pdf  157 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/LT-INN-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/LT-INN-001_SH3.pdf  250 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/LT-INN-001_SH4.log  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI1/dwg_result.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/LT-INN-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/LT-INN-001_SH1.pdf  259 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/LT-INN-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/LT-INN-001_SH2.pdf  157 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/LT-INN-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/LT-INN-001_SH3.pdf  249 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/LT-INN-001_SH4.log  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI2/dwg_result.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/LT-INN-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/LT-INN-001_SH1.pdf  259 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/LT-INN-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/LT-INN-001_SH2.pdf  172 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/LT-INN-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/LT-INN-001_SH3.pdf  249 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/LT-INN-001_SH4.log  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI3/dwg_result.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/LT-INN-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/LT-INN-001_SH1.pdf  259 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/LT-INN-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/LT-INN-001_SH2.pdf  172 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/LT-INN-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/LT-INN-001_SH3.pdf  249 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/LT-INN-001_SH4.log  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI4/dwg_result.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/LT-INN-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/LT-INN-001_SH1.pdf  259 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/LT-INN-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/LT-INN-001_SH2.pdf  172 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/LT-INN-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/LT-INN-001_SH3.pdf  249 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/LT-INN-001_SH4.log  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI5/dwg_result.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI6/LT-INN-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI6/LT-INN-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI6/LT-INN-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI6/LT-INN-001_SH4.log  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgI6/dwg_result.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/LT-OUT-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/LT-OUT-001_SH1.pdf  295 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/LT-OUT-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/LT-OUT-001_SH2.pdf  194 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/LT-OUT-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/LT-OUT-001_SH3.pdf  236 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/LT-OUT-001_SH4.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO1/dwg_result.json  17 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/LT-OUT-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/LT-OUT-001_SH1.pdf  292 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/LT-OUT-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/LT-OUT-001_SH2.pdf  193 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/LT-OUT-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/LT-OUT-001_SH3.pdf  232 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/LT-OUT-001_SH4.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO2/dwg_result.json  17 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/LT-OUT-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/LT-OUT-001_SH1.pdf  292 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/LT-OUT-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/LT-OUT-001_SH2.pdf  208 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/LT-OUT-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/LT-OUT-001_SH3.pdf  231 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/LT-OUT-001_SH4.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO3/dwg_result.json  16 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO6/LT-OUT-001_SH1.log  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO6/LT-OUT-001_SH2.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO6/LT-OUT-001_SH3.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO6/LT-OUT-001_SH4.log  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwgO6/dwg_result.json  16 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwg_asm.py  29 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwg_inn.py  37 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/dwg_out.py  37 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/fixb.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_asm/_patch.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_asm/gdt.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_asm/m3d.py  19 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_asm/nxd2.py  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_asm/ptdwg.py  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_inn/ptdwg.py  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_out/_patch.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_out/gdt.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/lib_out/ptdwg.py  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch1.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch2.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch3.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch4.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch5.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch6.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch7.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch8.py  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch9.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch_params.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/patch_params_inn.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/render.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/render.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/run_dwg.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/run_dwg_inn4.log  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/run_dwg_inn5.log  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P8/run_dwg_out1.log  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P9/mk_probe.py  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P9/overlay.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P9/ovl_inn/LT-INN-001_Left_Thigh_Inner_vs_SCAN_overlay.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P9/ovl_out/LT-OUT-001_Left_Thigh_Outer_vs_SCAN_overlay.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P9/probe_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P9/probe_out.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/P9/run_ovl.ps1  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/_seams_add.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/_tabs_add.py  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/b_base.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/b_base2.py  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/b_base2_r0.py  14 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_stage/base.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_stage/t_sh.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_v2/BUILD_P3.txt  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_v2/base.json  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_v2/base_r0.json  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_v2/base_r1.json  11 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_v2/gates_inn.txt  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_v2/gates_out.txt  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/base_v2/tail_dev.json  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/design.py  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/design2.py  58 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/design2_r0.py  26 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/dwg_inn.py  37 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/finalize.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/finalize_p5d.py  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/insp_stl.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/ltail.py  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/ltail_r1.py  6 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/ltenv.py  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/ltint.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/masters2.json  15 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/masters2_r0.json  14 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/p4_explore.py  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/p_build.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/p_build2.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/p_build3.py  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/p_stageA.py  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/p_stageA2.py  26 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/p_stageA2_r0.py  23 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/p_stageB.py  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_A3_parts.ps1  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_all.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_base_A.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_deliver.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_dwgs.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_dwgs_parts.ps1  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_finalize.ps1  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_from_base.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_parts.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/run_parts_only.ps1  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/stages.py  46 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/stages2.py  86 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/nx/t1_env.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t2_drum.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t3_eval.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t4_speed.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t_names.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t_sh.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t_thk.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t_thk2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/t_un.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/nx/tail_dev.py  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/CHANGES.md  20 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/bore1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/bore2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/chh.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome3.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome4.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome5.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome6.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome7.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome8.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dome9.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dp_inn.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/dump.py  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/ear1.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/ear2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/ear3.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/floor1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/gus1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/hip1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/mate1.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/open1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/open2.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/open3.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/open4.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/open5.py  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/open6.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/open_outlines.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/pad1.py  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/padl.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/panel1.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/prof.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/prof2.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/thk.py  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/dt/tighten_report.json  13 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/P5test_out.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/dipinn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/dipout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p3inn_inn.json  12 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p3out_out.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p3r1inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p3r1out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p3r2inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p3r2out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4binn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4bout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4inn_masks_inn.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4inn_panelzone_inn.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4out_masks_out.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4out_panelzone_out.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4r1_panel_check.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4r1inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4r1inn_masks_inn.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4r1out_masks_out.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4r1out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p4r1out_panelzone_out.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5a2inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5a2out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5achkout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5ainn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5ainnx_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5aout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5aoutx_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5binn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5binnx_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5bout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5boutx_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5br1inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5br1out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5br1xinn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5br1xout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5c2inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5c2out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5c3inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5c3out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5c4inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5c4out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5cinn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5cout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5cr1inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5cr1out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5d2inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5d2out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5d3inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5d3out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5d4inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5d4out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5d5out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5dinn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5dout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/p5dt1out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/q7inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/q7out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v3inn_inn.json  12 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v3out_out.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v4inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v4out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v4r1inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v4r1out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5a2inn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5a2out_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5ainn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5aout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5binn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5binnx_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5bout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5boutx_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5cinn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5cout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5dinn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5dout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5einn_inn.json  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/gates/v5eout_out.json  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/i1/REPORT.md  14 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i1/missing.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/REPORT.md  39 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/dropped.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/extra_arch.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/oldtree.txt  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/bosses.json  14 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/hip_tabs.json  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/knee_a.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/knee_b.json  11 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/knee_c.json  15 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/missing.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/missing2.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/missing3.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/pins.json  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/ribs.json  18 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/roots.json  8 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/rows/seams_lip.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/i2/uncovered_lost_clusters.json  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/REPORT.md  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_boundary.json  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_boundary_raw.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_cands.json  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_cmp_part5.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_designfit.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_edges.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_final_partial.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/_final_scores.json  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m1/drum_fit.json  17 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/_final_stats.json  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/body_fit.json  107 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/curv_U72.txt  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/early_U72.log  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/early_V72.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/features_raw.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/fin_S8.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/fin_S9.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/fin_U56.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/fin_U64.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/fin_U72.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/long_T72.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/long_T72b.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/long_T72c.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/long_T72d.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/sweep2.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/sweep3.log  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/wall_U72.txt  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/wall_stats.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m2/wallstat_U72.txt  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/REPORT.md  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/cone_fit.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/hip_fit.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/holes_tmp.json  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/int_dev.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/join_slopes.json  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/loft_search.json  3 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/planes.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m3/ruled_test.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/edge_break.json  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/joint.json  30 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/loss_by_cause.json  5 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/masks_summary.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/p5_face_segments.json  16 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/patches.json  14 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/stations.csv  205 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m4/tilt.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m5/band.json  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m5/edge_pts.json  7 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m5/edge_theta.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m5/p_run1.txt  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m5/r_run1.txt  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m5/test1.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/m5/v_run.txt  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/p4snap/fit_check.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/c2/open.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootfit_inn.json  157 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootfit_inn.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootfit_out.json  97 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootfit_out.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootmeas_inn.json  111 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootmeas_inn.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootmeas_out.json  98 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/rootmeas_out.txt  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/roottable_inn.json  19 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/roottable_inn.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/roottable_out.json  11 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/roottable_out.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/seam_inn.json  19 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/seam_out.json  18 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/p5d/seam_paths.json  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/r1/corners.json  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/r1/meas.json  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/r1/panel_fit.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/r1/runout_plane.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/RESULT.md  9 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/curv_H6.json  4 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/envelope_spec.json  268 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/eval_part5.txt  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/eval_v1.txt  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/fine.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/fit_H2.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/fit_H3.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/fit_H4.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/fit_H5.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/fit_H6.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/fit_H7.log  0 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/pershell.txt  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/s1/shellproxy_H7.json  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/t5/FIX1.txt  7 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/t5/FIX2.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/t5/gates_p3r1.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/t5/gates_p3r2.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/t5/t5_tail.json  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/t5/t6_chain.json  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v3/VERDICT.txt  6 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/v3/gates_inn.txt  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/v3/gates_out.txt  2 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/v3/zones.txt  1 KB  2026-10-31
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/VERDICT.txt  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/gates_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/gates_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/joint.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/panel.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/panel2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/tail.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/tail2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/valid.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/zones_ext.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/zones_inn.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4/zones_out.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/VERDICT.txt  11 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/axial.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/edge.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/edge2.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/edge3.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/gates_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/gates_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/inn_corner_c.png  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/joint.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/ledge.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/panel.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/panel2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/runout.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/selfx.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/strip.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/tail.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/tail2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/tip.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/valid.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/zones_ext.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/zones_ext2.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/zones_inn.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v4r1/zones_out.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/VERDICT.txt  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/gates_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/gates_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m1.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m10.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m11.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m11b.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m1b.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m1c.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m3.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m4.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m5.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m5b.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m6.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m6b.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m6c.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m6d.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m6e.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m6f.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m6g.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m7.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m8.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m8b.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m9.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/m9b.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/masks.txt  16 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/reg.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/reg2.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/reg3.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/valid.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5a/valid2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/VERDICT.txt  18 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/corner.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/gates_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/gates_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/gates_p5a2_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/gates_p5a2_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/gates_x_inn.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/gates_x_out.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/hole1.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/hole2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/hole3.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m1.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m2.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m4.txt  12 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m5.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m5b.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m6.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m7.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/m8.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/masks.txt  20 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/reg.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/tail.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5b/valid.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/VERDICT.txt  23 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/extra.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/gates_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/gates_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/loops.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/m4.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/masks.txt  10 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/skin.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/thick.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5c/valid.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/VERDICT.txt  11 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/extra.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/extra2.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/gates_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/gates_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/loops.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/m4.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/masks.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/mxprof.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/open.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/overlap_prevcheck.txt  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/roots.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/seam.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/skin.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/thick.txt  2 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/valid.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5d/wall.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/VERDICT.txt  5 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/dip_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/dip_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/extra2.txt  8 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/gates_inn.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/gates_out.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/loops.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/open.log  0 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/seam.txt  1 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/skin.txt  4 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/valid.txt  3 KB  2026-11-01
left_thigh_clean_rebuild/ws/lt_clean2/work/v5e/wall.txt  1 KB  2026-11-01
```

### chest_ch001 (nx_re_projects_20261105_part1.zip)
```
chest_ch001/project/part 3 - Chest/CLEAN_PLAN.md  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/CLIENT_MESSAGE.txt  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_CLEAN2_build.json  4 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean12.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_END_POSTS_post.json  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_END_end.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_NECK2_finish.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_NECK_neck.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_overlay.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevC_vs_SCAN_end.json  4 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_RevC_vs_SCAN_neck.json  5 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CH-001_Chest_vs_SCAN_overlay.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CLEAN_end_check.png  271 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CORNER_CLEAN2_vs_scan_slices.png  213 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/CORNER_scan_slices.png  187 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/RevC_checks/c1_A_top_in.png  196 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/RevC_checks/c2_sec_joint.png  275 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/RevC_checks/c2_sec_seam.png  290 KB  2026-10-31
chest_ch001/project/part 3 - Chest/Deviation_Check/maps_2026-10-31/deviation_stats.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/HANDOFF.md  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/REBUILD.md  22 KB  2026-10-31
chest_ch001/project/part 3 - Chest/STATUS.md  33 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/CLIENT_MESSAGE.txt  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/HANDOFF_session4.md  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/CAD/CH-001_Chest_AP214.log  48 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/CAD/CH-001_Chest_AP242.log  38 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/CAD/_finalize.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/QA/REPORT_deviation.md  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/QA/thin_steps_top10_a.png  134 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/QA/thin_steps_top10_b.png  136 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/README.md  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/Renders/CH-001_side.png  237 KB  2026-10-30
chest_ch001/project/part 3 - Chest/_rounds2-4_2026-10-30/deliver/Renders/CH-001_top.png  270 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/_balloon_sim.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_boxmax.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_budget.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_chk.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_crops.py  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_d.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_dbg.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_dump.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_dump2.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_eneg.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_facestats.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_far.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_missmap.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_near.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/_neck.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_p50.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_padvol.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_poledist.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_q.py  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_rim.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_rimdiff.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_tbudget.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_tmap.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_w.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/_zoom.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/arcfit.py  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/c10_pockets.py  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/c10_sheets.py  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/c10_sheets_C11.py  16 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/c10_sheets_lib.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/clean_boss.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/clean_mapview.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/clean_recess.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/clean_relief.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/clean_rib.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/clean_tile.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/common.py  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/dev2.py  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/fin_bbox.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/make_zip.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/ov_probe.py  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_belt.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_cadmap.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_clusters.py  7 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_contour.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_cornerfit.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_cornerz.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_crops.py  4 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_curl.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_endface.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_lipcov.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_lipmap.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_necklip.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_post.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_prep.py  8 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_prof.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_relief.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_sec.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r1_segment.py  5 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_edge.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_endfit.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_lower.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_neckspec.py  9 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_prof.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_profcheck.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_ruled.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_secs.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/r2_tipdist.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/an/readme_c14.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/readme_steps.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/render.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/render_cadonly.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/render_zoom.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/report.py  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/report_C8.py  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/s0_load.py  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s10_skin.py  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s12_sections.py  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s13_fold.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s14_raised.py  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s15_probe.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s16_outline.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s16_plateaus.py  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s17_plateaus.py  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s17a_levels.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s17b_curate.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s19_params.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s1_views.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s1b_quick.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s20_panel.py  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s20b_circles.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s21_panel_params.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s22_through.py  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s23_holes.py  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s23b_hole_caps.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s24_grooves.py  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s24b_groove_pick.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s25_recesses.py  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s2_symmetry.py  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s30_tmap.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s31_pads.py  11 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/s31_pads_C8.py  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/s32_extdepth.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s33_tongue.py  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s3_census.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s3b_normals.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s40_plugs.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/s41_floor.py  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/s4_probe.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s5_frame.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s6_hmap.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s7_wall.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s8_datums.py  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/s8b_rim.py  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/sec.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/sec_cmp.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/an/secc.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/stepcheck.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/an/zones.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/deliver/CAD/CH-001_Chest_AP214.log  12 KB  2026-10-30
chest_ch001/project/part 3 - Chest/deliver/CAD/CH-001_Chest_AP242.log  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/deliver/Deviation Analysis/REPORT_deviation.md  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/deliver/Renders/CH-001_side.png  200 KB  2026-10-30
chest_ch001/project/part 3 - Chest/deliver/Renders/CH-001_top.png  195 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/_ref_build2_outer.py  21 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/build.py  45 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/build_C11.py  41 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/build_C12.py  44 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/build_C8.py  37 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/build_clean.py  19 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/build_fast.py  18 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/build_revA_B12.py  21 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/c10_feat.py  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/clean_feat.py  11 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/diag_band.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/diag_crease.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/diag_leftlip.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/dump_edges.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/dump_neck_edge.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/dwg_annot.py  24 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/dwg_annot_C8.py  23 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/dwg_annot_clean.py  25 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/dwg_annot_revA0.py  16 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwg_chest.py  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/dwg_chest_C8.py  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/dwg_chest_clean.py  10 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/dwg_chest_revA0.py  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwglib/gdt.py  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwglib/m3d.py  19 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwglib/nxd2.py  10 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwglib/ptdwg.py  12 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/cad/CH-001_Chest_AP214.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/cad/CH-001_Chest_AP242.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/cad/_finalize.json  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/CH-001_SH1.log  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/CH-001_SH2.log  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/CH-001_SH3.log  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/CH-001_SH4.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh1_front.json  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh1_right.json  9 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh1_top.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh2_front.json  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh2_secB.json  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh2_secC.json  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh3_right.json  9 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh3_secD.json  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dump_sh4_back.json  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/dwg_result.json  10 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/t_p1.png  91 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/t_p2.png  90 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/t_p3.png  67 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg/t_p4.png  219 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/CH-001_SH1.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/CH-001_SH2.log  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/CH-001_SH3.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/CH-001_SH4.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/dump_sh1_top.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/dwg_result.json  10 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/t_p1.png  106 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/t_p2.png  111 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/t_p3.png  87 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg2/t_p4.png  160 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/CH-001_SH1.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/CH-001_SH2.log  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/CH-001_SH3.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/CH-001_SH4.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/dwg_result.json  10 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/t_p1.png  106 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/t_p3.png  89 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/dwg3/t_p4.png  162 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/fin.log  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/dwgtest/model/_finalize.json  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/fin_C15p.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/finalize.py  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/heal_sliver.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/inspect_user.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/locate_bad.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outA1 A/build.json  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outA2/build.json  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outA3/build.json  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outA4/build.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB1.log  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB1/build.json  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB10/build.json  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB11/build.json  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB12/build.json  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB2/build.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB3/build.json  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB4.log  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB4/build.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB5/build.json  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB6.log  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB6/build.json  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB7/build.json  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB8/build.json  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outB9/build.json  8 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC1,G/build.json  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC1.log  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC1/diag_crease.json  13 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outC10/build.json  45 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC11/build.json  44 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC12/build.json  43 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC12p/build.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC13/build.json  40 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC14/build.json  45 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC14p/build.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC15p/build.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC16p/build.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC2/build.json  9 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC3/build.json  40 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC4/build.json  76 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC5/build.json  119 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC5p/build.json  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC5q/build.json  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC5r/build.json  23 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC6/build.json  42 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC7/build.json  135 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outC8/build.json  141 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC8h/heal.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outC9/build.json  141 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outD1.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outD1/build.json  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outD2/build.json  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outD3/build.json  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outD4/build.json  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outR1/CH-001_Chest_RevB_revB_feat.json  5 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR10/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean10.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR11/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean11.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR13/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean13.json  4 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR2/inspect_user.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR4/edges_end.json  34 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR4/edges_top.json  10 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR4/edges_topL.json  9 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR4/inspect_user.json  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR5/diag_band.json  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR5/diag_leftlip.json  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR5/neck_edge.json  22 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR6/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR7/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean7.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR8/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean8.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outR9/CH-001_Chest_RevB_vs_SCAN_CLEAN_clean9.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/outT1/build.json  21 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outT10/t.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10b/t.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10c/t.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10d/t.json  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10e/t.json  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10f/t.json  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10g/t.json  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10h/t.json  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10i/t.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT10j/t.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT12a/t.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT12b/t.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT12c/t.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT13a/t.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT13b/t.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT13c/t.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT13d/t.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT13e/t.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/outT2/build.json  9 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/outT3/build.json  19 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/overlay.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/params.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/pdf2png.py  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/pdfcrop.py  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/post_fix.py  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/post_plugs.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/post_recess.py  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/nx/revB10_clean.py  12 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB11_clean.py  14 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB12_clean.py  14 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB13_clean.py  16 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB14_clean.py  18 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB2_end.py  7 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB3_post.py  6 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB4_neck.py  11 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB5_finish.py  13 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB6_clean.py  9 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB7_clean.py  12 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB8_clean.py  11 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB9_clean.py  12 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revB_feat.py  18 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revC1_neck.py  18 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/revC2_end.py  24 KB  2026-10-31
chest_ch001/project/part 3 - Chest/nx/t_c10.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/nx/t_shell.py  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/review_2026-10-30/CLUSTERS.md  16 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/REVIEW.md  24 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/cad/_finalize.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/cad/sha256.txt  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/cad_C8/sha256.txt  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/k024_missing.png  255 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/k040_missing.png  250 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/k042_extra.png  284 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/k054_missing.png  240 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/f_00.jpg  177 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/f_01.jpg  142 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/f_02.jpg  152 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/f_03.jpg  106 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/f_04.jpg  42 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_00.jpg  170 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_01.jpg  204 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_02.jpg  152 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_03.jpg  150 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_04.jpg  96 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_05.jpg  132 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_06.jpg  131 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_07.jpg  151 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_08.jpg  119 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_09.jpg  115 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_10.jpg  153 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_11.jpg  132 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_12.jpg  138 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_13.jpg  109 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_14.jpg  169 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_15.jpg  161 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_16.jpg  180 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_17.jpg  147 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_18.jpg  160 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_19.jpg  162 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_20.jpg  161 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/s_21.jpg  51 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/t_00.jpg  151 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/t_01.jpg  154 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/t_02.jpg  155 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/t_03.jpg  157 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/t_04.jpg  137 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/sheets/t_05.jpg  156 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/small/k001_missing.jpg  82 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/crops/small/k003_missing.jpg  73 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/census.json  271 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/diff_ZE_lowvent.png  153 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/diff_ZE_text.png  275 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/flange.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/measure.json  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/probe_105_-207_-21.png  31 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r0_check.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r1_dev.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r2_clusters.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r3_maps.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r5_crops.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r5b.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r5v.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r6_census.log  47 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/r8_thin.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/sym_ZI_comps.json  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/text_T800.png  80 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/text_glyphs.png  59 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/text_inner.png  109 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data/thin.json  166 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/census.json  191 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/clusters.json  459 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/measure.json  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r4.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r6.log  31 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/r8.log  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/text_T800.png  66 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/text_glyphs.png  59 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/text_inner.png  109 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_B12/thin.json  33 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/census.json  325 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/measure.json  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/r6.log  54 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/text_T800.png  74 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/text_inner.png  108 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C10/thin.json  151 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/GATES.txt  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/census.json  323 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/measure.json  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/r6.log  54 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C11/thin.json  146 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/GATES12.txt  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/census.json  323 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/measure.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/r6.log  56 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/text_inner.png  108 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C12/thin.json  149 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/GATES13.txt  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/census.json  322 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/measure.json  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/r6.log  53 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C13/thin.json  151 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/GATES14.txt  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/census.json  328 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/r6.log  55 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14/thin.json  148 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/GATES14p.txt  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/census.json  328 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C14p/thin.json  148 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/GATES15p.txt  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/census.json  328 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/r6.log  55 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C15p/thin.json  152 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/GATES16p.txt  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/census.json  329 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/r6.log  55 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/r8.log  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C16p/thin.json  155 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/census.json  281 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/measure.json  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_C8/r6.log  49 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/census.json  189 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/clusters.json  480 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/measure.json  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/r6.log  31 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/r8.log  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D1/thin.json  35 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/census.json  189 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/clusters.json  496 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/r6.log  31 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/r8.log  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D2/thin.json  34 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/census.json  194 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/measure.json  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/r1.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/r10.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/r1_dev.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/r2.log  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/r3.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/r6.log  32 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/r8.log  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/data_D3/thin.json  37 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/gate_c10.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/gate_c12.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/i90_clusters.py  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/i91_crops.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/i92_secs.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/i93_depth.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/i93top.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/i94_zoom.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r0_check.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r10_measure.py  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r11_flange.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r12_table.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r13_smallthin.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r1_dev.py  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r2_clusters.py  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r3_maps.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r4_diffmaps.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r5_crops.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r6_census.py  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r7_sym.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r8_thin.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r8b_probe.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/r9_secfill.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/rc.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/run_c10.sh  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/run_c8.sh  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/secs/s4_c14spike.png  25 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/sheet.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/shrink.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/review_2026-10-30/views.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/bumps.json  28 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/BRIEF_COMMON.md  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1.json  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/NOTES.md  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/bore_depth.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/crop.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/crop2.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/evidence.py  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f04_explore.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f04_explore2.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f04_explore3.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f04_plan.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f04_stem.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f04_wally.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f11_explore.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f11_fit.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f11_pit.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f11_shade.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f14_explore.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f14_explore2.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f14_radial.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f14_wall.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f22_maps.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f22_sec.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f22_sec2.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f22_thick.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f23_explore.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f23_plane.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f23_prof.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f23_xsec.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f23_zoom.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f24_explore.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f24_prof.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f24_prof2.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f26_flange.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f26_flange.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f26_flange_plane.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f26_plane.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/f26_ring.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/fit_bosses.json  21 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/fit_bosses.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/g1lib.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/kq.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/make_g1.py  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/make_g1_extra.py  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/npzkeys.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/padscan.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/plotfeat.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/qpoly.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/query.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/tmapq.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1/validate.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G1_orig.json.txt  22 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2.json  27 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/NOTES.md  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/chk.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/crop.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/diffv.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/evid.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09b.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09d.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09e.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09f.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09g.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f09h.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f10a.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f10b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f10c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f10d.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f10e.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f10f.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f12a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f12b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f12c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f19a.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f19b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f20_segs.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f20a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f20b.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f20c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f20d.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f20e.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f21_fit.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f21a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f21b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f21c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f21d.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f21e.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f21f.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f25a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f25b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f25c.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/f25d.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/g2_extra.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/g2lib.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/inv.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/make_g2.py  10 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/mapview.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/notes_short.txt  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/xrview.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G2/zoom.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3.json  38 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/F15b_windows.json  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/NOTES.md  13 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/blobs.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/blobs_boss75L.json  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/blobs_boss75R.json  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/blobs_pins88L.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/blobs_pins88R.json  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/check.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/crop.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/ev.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03b.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03d.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03e.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03p2.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03p3.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03p4.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03p5.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f03pocket.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f06a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f06b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f06c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f07a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f07b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f07c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f07d.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f07e.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f07f.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f07g.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f15a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f15b_rad.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f15bw.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f15bx.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f15c.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f15d.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18bar.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18d.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18e.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18f.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18g.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f18h.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f28_inner.json  11 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f28a.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f28b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/f28c.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/g3lib.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/gen_f03_f18.py  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/gen_f06_f07.py  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/gen_f15a.py  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/gen_f28.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/hook_fit.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/merge.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/ov.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/ov2.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/part_F03F18.json  18 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/part_F06F07.json  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/part_F15a.json  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/part_F28.json  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/part_zz_notes.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/patch1.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/pocket_E.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/raycast.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/secplot.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G3/viz.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G4.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/G4_rejected.json.txt  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/SCHEMA.md  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/c10_sheets_zonly.py  12 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/chk_outline.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/chk_sheet.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/chk_win.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/list_feats.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/mk_g4.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/mk_recess.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/pads_C10.json  393 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/pads_C8.json  363 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/params_C8.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/patch_build.py  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/patch_sheets.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/pockets_loops.json  69 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/recess_C8.json  159 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/recess_c10.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/s31_patch.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/sheets_tail.py  9 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/skin_cmp.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/splice.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/st_b.json  333 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/st_s15.json  333 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/st_s25.json  187 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c10/st_sb.json  256 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/cut_spikes.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/floor.json  121 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/pads_C11.json  381 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/plugs.json  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/plugs_c15.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/plugs_c16.json  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/plugs_manual.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/plugs_rim.json  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/c12/st_scoop2.json  205 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/bal_cal.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/check_bal.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/crop.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/dimlines.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/features.json  24 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/fix_h15.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/fix_h21.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/fix_left.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/holes_clean.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/m_sv.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/m_sv2.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/m_sv3.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/m_sv4.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/m_uv.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/m_uv2.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/m_uv3.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/make_spec.py  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/pdf_boxes.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/pdf_text.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/plan_balloons.py  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/plan_balloons2.py  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/plan_balloons_out.py  10 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/plot_spec.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/q.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/q2.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/restore_d6b.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/rib_ends.json  3 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/rib_ends.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/rib_prof.py  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/sh4_balloons.json  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/sheetmap.py  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/spec_add.txt  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clean/upd_docs.py  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/clusters_r1.json  417 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/datums.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/datums.log  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_A4half.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_B10.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_B11.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_B12full.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dev2_B12full.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dev2_B12half.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_B6.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_C5.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_C5r.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_C7.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_C8.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dev2_T3half.json  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dev2_clean.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dev2_clean.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dev2_r1b.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/dev2_r2.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/dev2_revA.json  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dev2_revA.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dev2_ru.json  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/dev_revA.log  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/CH-001_SH1.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/CH-001_SH2.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/CH-001_SH3.log  7 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/CH-001_SH4.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh1_front.json  78 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh1_right.json  55 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh1_top.json  61 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh2_front.json  78 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh2_secB.json  128 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh2_secC.json  121 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh3_secD.json  94 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dump_sh4_back.json  271 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg1/dwg_result.json  11 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh1_front.json  165 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh1_right.json  135 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh1_top.json  200 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh2_front.json  164 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh2_secB.json  488 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh2_secC.json  468 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh3_boreL.json  179 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh3_boreR.json  169 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dump_sh3_secD.json  391 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg10/dwg_result.json  8 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11/dump_sh2_secB.json  488 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11/dump_sh2_secC.json  468 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg11/dwg_result.json  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12/dump_sh2_secB.json  488 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12/dump_sh2_secC.json  468 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg12/dwg_result.json  13 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh1_front.json  165 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh1_right.json  134 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh1_top.json  200 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh2_front.json  163 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh2_secB.json  489 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh2_secC.json  468 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh3_boreL.json  179 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dump_sh3_secD.json  391 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg13/dwg_result.json  13 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg2.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/CH-001_SH1.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/CH-001_SH2.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/CH-001_SH3.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/CH-001_SH4.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh1_front.json  73 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh1_right.json  53 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh1_top.json  58 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh2_front.json  73 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh2_secB.json  128 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh2_secC.json  122 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh3_secD.json  94 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dump_sh4_back.json  270 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg2/dwg_result.json  11 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg3.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg3/CH-001_SH1.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg3/CH-001_SH2.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg3/CH-001_SH3.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg3/CH-001_SH4.log  5 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg3/dwg_result.json  11 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4/CH-001_SH1.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4/CH-001_SH2.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4/CH-001_SH3.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4/CH-001_SH4.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4/dump_sh3_boreL.json  63 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4/dump_sh3_boreR.json  65 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg4/dwg_result.json  14 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg5.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg5/CH-001_SH1.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg5/CH-001_SH2.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg5/CH-001_SH3.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg5/CH-001_SH4.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg5/dump_sh2_secB.json  128 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg5/dwg_result.json  14 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg6.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg6/CH-001_SH1.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg6/CH-001_SH2.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg6/CH-001_SH3.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg6/CH-001_SH4.log  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg6/dwg_result.json  14 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/dwg7.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh1_front.json  496 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh1_right.json  298 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh1_top.json  469 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh2_front.json  498 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh2_secB.json  476 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh2_secC.json  378 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh3_boreL.json  372 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh3_boreR.json  361 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dump_sh3_secD.json  282 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg7/dwg_result.json  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh1_front.json  165 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh1_right.json  135 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh1_top.json  202 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh2_front.json  164 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh2_secB.json  488 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh2_secC.json  468 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh3_boreL.json  181 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dump_sh3_boreR.json  171 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg8/dwg_result.json  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/dump_sh2_secB.json  488 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/dump_sh2_secC.json  468 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/dump_sh3_boreR.json  169 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwg9/dwg_result.json  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/CH-001_SH1.pdf  201 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/CH-001_SH3.log  7 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/CH-001_SH3.pdf  171 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/CH-001_SH4.log  5 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh1_front.json  86 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh1_right.json  26 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh1_top.json  16 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh2_front.json  86 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh2_secB.json  79 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh2_secC.json  69 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh3_secD.json  44 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dump_sh4_back.json  109 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3/dwg_result.json  11 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/CH-001_SH1.pdf  205 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/dump_sh3_boreL.json  33 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/dump_sh3_boreR.json  33 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3b/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c/CH-001_SH1.pdf  205 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3c/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/CH-001_SH1.pdf  205 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/dump_sh2_secB.json  79 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD3d/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/CH-001_SH1.pdf  205 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh1_front.json  86 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh1_right.json  26 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh1_top.json  16 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh2_front.json  86 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh2_secB.json  79 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh2_secC.json  70 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh3_boreL.json  33 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh3_boreR.json  33 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh3_secD.json  44 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dump_sh4_back.json  109 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4/dwg_result.json  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4b.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4b/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4b/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4b/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4b/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4b/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4b/dwg_result.json  14 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4c.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4c/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4c/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4c/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4c/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4c/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4c/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d/dump_sh2_secB.json  79 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4d/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4e.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4e/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4e/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4e/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4e/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4e/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4e/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4f.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4f/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4f/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4f/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4f/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4f/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4f/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4g.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4g/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4g/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4g/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4g/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4g/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4g/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4h.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4h/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4h/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4h/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4h/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4h/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4h/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i/CH-001_SH1.pdf  205 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i/CH-001_SH3.pdf  188 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4i/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4j.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4j/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4j/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4j/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4j/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4j/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4j/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4k.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4k/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4k/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4k/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4k/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4k/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD4k/dwg_result.json  15 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5/dwg_result.json  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5b.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5b/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5b/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5b/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5b/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5b/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5b/dwg_result.json  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5c.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5c/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5c/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5c/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5c/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5c/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5c/dwg_result.json  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5d.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5d/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5d/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5d/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5d/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5d/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD5d/dwg_result.json  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6/dwg_result.json  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6b.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6b/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6b/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6b/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6b/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6b/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6b/dwg_result.json  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6c.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6c/CH-001_SH1.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6c/CH-001_SH2.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6c/CH-001_SH3.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6c/CH-001_SH3.pdf  193 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6c/CH-001_SH4.log  6 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/dwgD6c/dwg_result.json  17 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/fin_bbox_revA.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/frame.json  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/grooves.json  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/holes.json  3 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/inner_sections.json  469 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/levels.json  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/outline.json  164 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/overlay/probe_pts.json  6 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/pads.json  375 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/panel.json  4 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/plateaus.json  159 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/r1/clusters.log  8 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/con_R10.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/con_R2.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/corner_block.py  6 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/curl_plane.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/dev2_r1b.log  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/dev2_r2.log  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/dev2_ru.log  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch.py  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch10.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch11.py  4 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch12.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch13.py  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch14.py  4 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch15.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch16.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch2.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch3.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch4.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch5.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch6.py  5 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch7.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch8.py  4 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/patch9.py  2 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/rel_L.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/rel_R.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/rel_R2.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/seg_cR.json  5 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/seg_endR.json  8 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/seg_neckR.json  3 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/spec_r1.json  92 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/t_meet.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/t_outer.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/t_probe.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/t_sign.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/t_wall.py  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_a.json  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_b.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_b2.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_c.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_d.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_e.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_f.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_g.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_h.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_i.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r1/views_v.json  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/edge_neckR.json  6 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/lower_neckR.json  13 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/neckspec.json  30 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/prof_neckR.json  7 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/ruled_neckR.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/views_a.json  1 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/views_b.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/views_c.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/views_e.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/views_f.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/r2/views_g.json  0 KB  2026-10-31
chest_ch001/project/part 3 - Chest/work/recesses.json  12 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/render_revA.log  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/report_revA.log  4 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/rv/bad_C8.json  0 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/rv/dev_B12half.log  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/rv/dev_C5.log  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/rv/dev_C5r.log  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/rv/dev_C7.log  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/rv/dev_C8.log  2 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/rv/dev_T3half.log  2 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/rv/why_p50_legend.png  6 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/s0.log  8 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/s0_describe.json  8 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/s1.log  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/s10.log  1 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/s2.log  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/sections.json  469 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/stepcheck_revA.log  1 KB  2026-10-30
chest_ch001/project/part 3 - Chest/work/symmetry_ax0.json  0 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/through.json  17 KB  2026-10-29
chest_ch001/project/part 3 - Chest/work/tongue.json  52 KB  2026-10-29
chest_ch001/project/part 6 - Chest Clean Rebuild/BRIEF.md  7 KB  2026-10-31
chest_ch001/project/part 6 - Chest Clean Rebuild/CH-001_RevC_Chest_Clean_Rebuild/CH-001_RevC_Chest_Clean/Drawings/CH-001.pdf  338 KB  2026-11-02
chest_ch001/project/part 6 - Chest Clean Rebuild/CLIENT_MESSAGE.txt  3 KB  2026-11-02
chest_ch001/project/part 6 - Chest Clean Rebuild/CLIENT_MESSAGE_RevC.txt  1 KB  2026-11-02
chest_ch001/project/part 6 - Chest Clean Rebuild/DESIGN_INTENT.md  7 KB  2026-10-31
chest_ch001/project/part 6 - Chest Clean Rebuild/Deviation_Check/CH-001_Chest_RevB_vs_SCAN_overlay.json  1 KB  2026-11-02
chest_ch001/project/part 6 - Chest Clean Rebuild/Deviation_Check/Deviation_Check/CH-001_Chest_RevC_vs_SCAN_overlay.json  1 KB  2026-11-02
chest_ch001/project/part 6 - Chest Clean Rebuild/Deviation_Check/Deviation_Check/README.md  3 KB  2026-11-02
chest_ch001/project/part 6 - Chest Clean Rebuild/Deviation_Check/README.md  3 KB  2026-11-02
chest_ch001/project/part 6 - Chest Clean Rebuild/HISTORY.md  5 KB  2026-10-31
chest_ch001/project/part 6 - Chest Clean Rebuild/PLAN.md  19 KB  2026-11-02
chest_ch001/transcripts/0ba74d23-fece-4ac7-bbfa-d8a13f52a7e9.jsonl  3.6 MB  
chest_ch001/transcripts/6db96a5a-7a10-4372-b24e-f1f409ba4256.jsonl  3.5 MB  
chest_ch001/transcripts/8330b7d3-5c61-4c7f-9dea-7d21232eb168.jsonl  4.7 MB  
chest_ch001/transcripts/8330b7d3_subagents/agent-a3ed442a6b632cb72.jsonl  2.7 MB  
chest_ch001/transcripts/8330b7d3_subagents/agent-a4d43a292eaaf5937.jsonl  2.2 MB  
chest_ch001/transcripts/8330b7d3_subagents/agent-a7033c0c6c6ecbe28.jsonl  3.0 MB  
chest_ch001/transcripts/8330b7d3_subagents/agent-a81a692c8a16729b1.jsonl  2.3 MB  
chest_ch001/transcripts/8330b7d3_subagents/agent-a962c3e41b5a56092.jsonl  1.6 MB  
chest_ch001/transcripts/8330b7d3_subagents/agent-abecf289784105525.jsonl  4.0 MB  
chest_ch001/transcripts/8330b7d3_subagents/agent-ae6eecf4e194e43fe.jsonl  3.2 MB  
chest_ch001/transcripts/9c3a8bea-4387-4d6e-ba59-f3194a39fa09.jsonl  6.3 MB  
chest_ch001/transcripts/c5865595-c8de-4b74-8830-0c775b0d089c.jsonl  4.4 MB  
chest_ch001/transcripts/d432d364-cec5-4dfa-930b-026d8aa6d8b5.jsonl  5.4 MB  
chest_ch001/transcripts/d9bb7563-2d16-40ea-98ba-9539917e17e8.jsonl  6.4 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a32c8a1e0e2bdee88.jsonl  2.3 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a3ed442a6b632cb72.jsonl  2.7 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a4d43a292eaaf5937.jsonl  2.2 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a5beac23e42419635.jsonl  804 KB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a7033c0c6c6ecbe28.jsonl  3.0 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a81a692c8a16729b1.jsonl  2.3 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a91e480b93d2ed465.jsonl  2.6 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-a962c3e41b5a56092.jsonl  1.6 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-abecf289784105525.jsonl  4.0 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-ad0fe98993a8eec63.jsonl  1.4 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-adc79fb602e712fb8.jsonl  1.2 MB  
chest_ch001/transcripts/d9bb7563_subagents/agent-ae6eecf4e194e43fe.jsonl  3.2 MB  
chest_ch001/transcripts/f204f22c-b209-48a9-8b63-56240f021786.jsonl  2.0 MB  
chest_ch001/ws/ch_clean/an/README.md  3 KB  2026-10-31
chest_ch001/ws/ch_clean/an/_d1.py  0 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d10.py  0 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d11.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d12.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d13.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d14.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d15.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d16.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d17.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d3.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d4.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d5.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d6.py  0 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d7.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d8.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_d9.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_ed.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_p.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/_p2.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/_rules.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_rules_S6_1_backup.json  4 KB  2026-11-02
chest_ch001/ws/ch_clean/an/_x1.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/_x2.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/_x3.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/_x4.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/_x5.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/c1_height.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/c2_secview.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/c3_ext.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/c4_look.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/c5_mask.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/c6_xsec.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/c7_crease.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/chlib.py  13 KB  2026-10-31
chest_ch001/ws/ch_clean/an/common.py  4 KB  2026-10-31
chest_ch001/ws/ch_clean/an/export_sections.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f10_areas.py  4 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f11_oldcad.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f12_fit.py  10 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f13_clusters.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f13_lines.py  5 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f14_islands.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f15_nxcheck.py  3 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f16_sweepsheet.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f1h_fit.py  15 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f2_eval.py  8 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f3_surf.py  6 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f4_secs.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f4b_zoom.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f5_resmap.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f6_asym.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f7_metrics.py  3 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f8_roughmap.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/f9_checks.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/g0_faces.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g0_show.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g10_wall.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g11_top.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g12_final_imgs.py  4 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g13_wall.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g14_lip.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g14b_lip.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g15_band.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g16_bandfit.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g17_bore.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g17b_bore.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g17c_bore.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g18_notch.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g19_bandface.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g19b_fit.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g1_uv.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/g20_dev2way.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g21_renders.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g22_neck2.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g23_sock.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g24_neckzone.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g25_renders3b.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g26_neckbad.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g2_neckfit.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g2b_neckfit.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g2c_neckround.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g3_nxvsprev.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g4_param.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g4b_loc.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g4c_fitT.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g5_split.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g6_nxsurf.py  7 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g7_neckedge.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g7b_neckedge.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g7c_neckedge.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g8_renders.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g9_ext.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g9_tips.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/g9b_extcurv.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h10_final_c.sh  4 KB  2026-11-02
chest_ch001/ws/ch_clean/an/h10_final_s6.sh  4 KB  2026-11-02
chest_ch001/ws/ch_clean/an/h1_view.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h1_viewb.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h2_top.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h4_final.sh  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h5_dof.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h6_meas.py  8 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h7_final4.sh  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h8_final5.sh  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/h9_final6.sh  4 KB  2026-11-01
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/b1_fit.py  7 KB  2026-10-31
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/b2_fit.py  7 KB  2026-10-31
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/b3_smooth.py  8 KB  2026-10-31
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/b4_curv.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/d1_dev.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/d5_surf.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/lib.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/lt_toolkit_copy/rays.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/m0_lib.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m10_B1.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m11_tipfit.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m12_circ.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m13_rib.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m14_pads.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m15_box.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m16_cfit.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m17_bend.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m18_bendR.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m1_look.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m20_userdiff.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m21_userview.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m22_end_sec.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m23_endthick.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m24_end_x.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m25_end_y.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m26_endthick2.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m27_boss.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m2_flange.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m30_neckmodel.py  9 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m31_tipscan.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m32_L.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m33_tip2arc.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m34_neckplots.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m35_armend.py  4 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m36_bendR.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m3_stations.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m3b.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m40_corner.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m41_endfits.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m42_rib.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m43_socket.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m44_socketfit.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m45_endplots.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m4_flange.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m5_tip.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m6_unroll.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m7_tipzoom.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m8_lamsec.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m8b_armend.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m9_B4.log  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m9_RevA.log  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m9_tipyz.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/m9_zones.py  6 KB  2026-11-01
chest_ch001/ws/ch_clean/an/old/_fixlib.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch1.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch10.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch11.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch12.py  4 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch13.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch14.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch15.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch16.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch2.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch3.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch4.py  4 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch5.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch6.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch7.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch8.py  3 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_patch9.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q1.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q10.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q11.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q2.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q3.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q4.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q5.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q6.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q7.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q8.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_q9.py  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/_t1.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/f1_fit.py  12 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/f1_fit_old_v5.py  10 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/f1c_fit.py  13 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/f1d_fit.py  13 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/f1e_fit.py  12 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/f1f_fit.py  10 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/f1g_fit.py  13 KB  2026-10-31
chest_ch001/ws/ch_clean/an/old/scan.py  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/patch_zones.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/r1_crops.py  5 KB  2026-10-31
chest_ch001/ws/ch_clean/an/run_final.sh  1 KB  2026-10-31
chest_ch001/ws/ch_clean/an/run_final2.sh  0 KB  2026-10-31
chest_ch001/ws/ch_clean/an/s5_log.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s5_panel_fit.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s5_pocket_fit.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_badbox.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_bandfit.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_devmap.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_diffmap.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_local.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_log.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_neckexact.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_neckmap.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_neckreg.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_qa_all.sh  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_qa_c.sh  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_report.py  4 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_report_S6_1_backup.py  4 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_shvbox.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_shvskin.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_small.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_stages.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_stepcheck.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_wall.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s6_webfit.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/an/s6_zebra.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_cadmap.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_cadprof.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_hf.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_prof.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_scanview.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_sdev.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_sec.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_shade.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_shieldchk.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_shieldfit.py  4 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_smap.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/s7_zmap.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/an/sweep.sh  1 KB  2026-10-31
chest_ch001/ws/ch_clean/deliver/CAD/CH-001_Chest_AP214.log  12 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/CAD/CH-001_Chest_AP214.step  13.7 MB  2026-11-02
chest_ch001/ws/ch_clean/deliver/CAD/CH-001_Chest_AP242.log  9 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/CAD/CH-001_Chest_AP242.step  10.8 MB  2026-11-02
chest_ch001/ws/ch_clean/deliver/CAD/_finalize.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/CAD/_steprt.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/CH-001.pdf  323 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/CH-001_SH1.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/CH-001_SH1.pdf  323 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/dump_front.json  62 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/dump_right.json  15 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/dump_secA.json  35 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/dump_secB.json  45 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/dump_top.json  21 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/Drawings/dwg_result.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/QA/DEVIATION_REPORT.md  2 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/QA/SMALL_FACES.md  5 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/QA/STAGES_S6_2.md  0 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/QA/WALL_CHECK.md  1 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/QA/step_check_occ.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/QA/wall_S6_2.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver/README.md  12 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/CAD/CH-001_Chest_AP214.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/CAD/CH-001_Chest_AP242.log  5 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/CAD/CH-001_Chest_AP242.step  10.8 MB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/CAD/_finalize.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/CAD/_steprt.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/Drawings/CH-001_SH1.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/Drawings/CH-001_SH1.pdf  338 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/Drawings/dump_front.json  62 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/Drawings/dump_secA.json  35 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/Drawings/dump_secB.json  45 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/Drawings/dump_top.json  21 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/Drawings/dwg_result.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/QA/DEVIATION_REPORT.md  2 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/QA/SMALL_FACES.md  5 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/QA/WALL_CHECK.md  1 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/QA/step_check_occ.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/QA/wall_RevC.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/deliver_RevC/README.md  3 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/README.md  14 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S1_A1/s1a.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_A2/s1a.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_A3/s1a.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B1/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B1/neck_edge_pts.json  115 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B1/s1b.json  10 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B2/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B2/neck_edge_pts.json  115 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B2/s1b.json  7 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B3/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B3/neck_edge_pts.json  174 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B3/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B3/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B4/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B4/neck_edge_pts.json  192 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B4/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B4/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B5/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B5/neck_edge_pts.json  115 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B5/s1b.json  7 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B5/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B6/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B6/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B6/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B7/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B7/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_B7/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_C1/shell.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_C3/shell.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_C4/shell.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_D1/grid.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_D2/grid.json  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_D3/grid.json  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S1_D4/grid.json  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_1/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_1/s2.json  7 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_2/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_2/s2.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_3/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_3/s2.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_3/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_4/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_4/s2.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S2_4/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s1a/s1a.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s1b/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s1b/neck_edge_pts.json  115 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s1b/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s1b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s2/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s2/s2.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3a/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3a/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3a/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3b/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3b/s3b.json  53 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3c/CH_S3c.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3c/s3c.json  95 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3_1/s3c/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_1/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_1/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_2/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_2/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_3/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_3/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_3/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_4/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_4/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_4/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_5/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_5/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_5/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_6/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_6/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_6/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_7/s3a.json  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_8/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_8/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3a_8/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_1/s3b.json  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_10/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_10/s3b.json  46 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_10/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_11/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_11/s3b.json  51 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_11/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_12/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_12/s3b.json  53 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_12/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_2/s3b.json  9 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_3/s3b.json  10 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_4/s3b.json  12 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_5/s3b.json  12 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_6/s3b.json  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_7/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_7/s3b.json  51 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_7/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_8/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_8/s3b.json  54 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_8/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_9/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_9/s3b.json  65 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3b_9/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3c_1/CH_S3c.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3c_1/s3c.json  50 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3c_1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3c_2/CH_S3c.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3c_2/s3c.json  93 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S3c_2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s1a/s1a.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s1b/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s1b/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s1b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s2/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s2/s2.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3a/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3a/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3a/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3b/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3b/s3b.json  53 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3c/CH_S3c.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3c/s3c.json  95 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s3c/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s4/CH_S4.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s4/s4.json  99 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_1/s4/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_t1/CH_S4.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_t1/s4.json  102 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S4_t1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s1a/s1a.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s1b/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s1b/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s1b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s2/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s2/s2.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3a/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3a/s3a.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3a/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3b/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3b/s3b.json  53 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3c/CH_S3c.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3c/s3c.json  95 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s3c/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s4/CH_S4.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s4/s4.json  99 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s4/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s5a/s5a.json  64 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s5b/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s5b/s5b.json  279 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_1/s5b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_2/s5a/export.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_2/s5a/s5a.json  139 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_2/s5b/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_2/s5b/s5b.json  226 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_2/s5b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5_2export/CH_S5a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_1/s5a.json  24 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_2/s5a.json  24 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_3/s5a.json  26 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_4/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_4/s5b.json  226 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_4/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_5/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_5/s5b.json  59 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_5/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_6/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_6/s5b.json  30 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_6/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_7/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_7/s5b.json  30 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_7/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_8/s5a.json  12 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S5d_9/s5a.json  26 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6_1/s1a/s1a.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s1b/CH_S1.log  5 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s1b/s1b.json  8 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s1b/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s2/CH_S2.log  5 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s2/s2.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s2/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3a/CH_S3a.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3a/s3a.json  28 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3a/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3b/CH_S3b.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3b/s3b.json  43 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3b/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3c/CH_S3c.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3c/s3c.json  65 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3c/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3c_neckclip_cup_test/CH_S3c.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s3c_neckclip_cup_test/s3c.json  69 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s4/CH_S4.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s4/s4.json  86 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s4/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s5a/s5a.json  69 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s5b/CH_S5b.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s5b/s5b.json  119 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_1/s5b/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6_2/s5a/s5a.json  89 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6d_1/s5a.json  24 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6d_2/s5a.json  17 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6d_3/s3b.json  13 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6d_4/s3b.json  12 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6d_5/s5a.json  24 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6d_6/s5a.json  24 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6pre_1/s1a/s1a.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s1b/CH_S1.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s1b/neck_edge_pts.json  115 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s1b/s1b.json  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s1b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s2/CH_S2.log  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s2/s2.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3a/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3a/s3a.json  28 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3a/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3b/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3b/s3b.json  43 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3c/CH_S3c.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3c/s3c.json  65 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s3c/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s4/CH_S4.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s4/s4.json  86 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s4/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s5a/s5a.json  75 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s5b/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s5b/s5b.json  122 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_1/s5b/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/S6pre_2/s5a/s5a.json  69 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6pre_2/s5b/CH_S5b.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6pre_2/s5b/s5b.json  119 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/S6pre_2/s5b/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/_ed2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/_ed3.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/_ins.py  7 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_export.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_finalize.py  5 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_finalize_c.py  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_neck_test.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s1a.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s1b.py  11 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s1c_shell.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s1d_grid.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s2.py  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3a.py  20 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3a_v1_backup.py  17 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3a_v5_S5_backup.py  18 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3b.py  30 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3b_v1_backup.py  25 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3b_v2_backup.py  28 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3b_v3_S3b11.py  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3b_v4_S5_backup.py  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3c.py  22 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_s3c_v1_backup.py  14 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3c_v6_S5_backup.py  22 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s3c_v7_S6pre_backup.py  22 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_s3c_v8_neckclip_cup_test.py  22 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_s4.py  16 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ch_s5a.py  33 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_s5b.py  38 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ch_steprt.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/chain_b7.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/chenv.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/chneck.py  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/chneck_v1_backup.py  8 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/a1/CH_S3a.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/a1/s3a.json  28 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/a1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/b1/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/b1/s5b.json  31 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/b1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/b2/CH_S5b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/b2/s5b.json  72 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/b2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/d1/neck_faces.json  7 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/d2/web_faces.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/d3/face_at.json  7 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/d4/erib_faces.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/d5/hole_faces.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/d6/web_final.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/docs.py  7 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/dump_faces.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/e-76.6/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/e-76.6/s3b.json  21 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/e-76.6/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/e-77.9/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/e-77.9/s3b.json  21 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/e-77.9/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/face_at.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/l36/CH_S3b.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/l36/s3b.json  25 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/l36/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/l38/CH_S3b.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/l38/s3b.json  25 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/l38/ugstep214.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dev/n1/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/n1/s3b.json  20 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/n1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/p49/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/p49/s3b.json  24 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/p49/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/p50.5/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/p50.5/s3b.json  24 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/p50.5/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch1.py  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch2.py  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch3.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch4.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch5.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch6.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch7.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/patch8.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sA/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sA/s3b.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sA/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sB/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sB/s3b.json  27 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sB/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sB2/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sB2/s3b.json  24 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sB2/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sC/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sC/s3b.json  28 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sC/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sD/CH_S3b.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sD/s3b.json  28 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/sD/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/x1/CH_S4.log  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/x1/s4.json  52 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dev/x1/ugstep214.log  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/dwg_ch.py  4 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dwg_ch_annot.py  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dwg_ch_annot_S6_1_backup.py  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dwg_ch_annot_c.py  6 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dwg_ch_c.py  4 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dwglib/m3d.py  19 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/dwglib/ptdwg.py  12 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/make_s4.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/make_s5.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/ovl/imgs.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/imgs_c.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/mk_probe.py  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/overlay.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/probe.json  12 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/run2.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/run3.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/run_ovl.ps1  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/verify.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/ovl/verify.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/patch_s3b_b.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/patch_s3b_socket.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/patch_s3c.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/NT1/neck_test.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/NT2/neck_test.json  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P10/p10.json  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P11/p11.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P12/p12.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P13/p13.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P2/p2.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P3/p3.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P4/p4.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P5/p5.json  5 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P6/p6.json  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P7/p7.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P8/p8.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/P9/p9.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/Q1/q1.json  220 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/Q1b/q1.json  206 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/Q2/q2.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/Q3/q3.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p1.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/nx/probe/p1.py  2 KB  2026-10-31
chest_ch001/ws/ch_clean/nx/probe/p10.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p11.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p12.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p13.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p2.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p3.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p4.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p5.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p6.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p7.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p8.py  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/p9.py  0 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/q1.py  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/q2.py  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/probe/q3.py  3 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/rt2.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/run_c_dwg.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/run_c_final.ps1  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/run_s1.ps1  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/run_s1_all.ps1  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/run_s3_all.ps1  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/run_s3a_all.ps1  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/run_s3b_all.ps1  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/run_s4_all.ps1  1 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/run_s5_all.ps1  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/run_s6_all.ps1  2 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/run_s6_final.ps1  1 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/run_s6pre_all.ps1  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/s3c_expr_block.txt  2 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/s3c_stages_block.txt  6 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/s4_body.txt  7 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/s4_body_S5_2_backup.txt  4 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/s5a_body.txt  26 KB  2026-11-02
chest_ch001/ws/ch_clean/nx/s5a_body_S5_2_backup.txt  19 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/s5b_body.txt  22 KB  2026-11-01
chest_ch001/ws/ch_clean/nx/s5b_body_S5_2_backup.txt  16 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1/F_fair2_sweep.md  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_A_bal.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_F_asym.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_F_close.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_F_fair.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_F_fair.md  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_G0.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_G1.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_G2.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_G3.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_S_bal.json  22 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_S_bal.md  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_S_close.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_S_fair.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T1.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T10.json  21 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T10.md  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T11.json  20 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T11.md  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T12.json  20 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T12.md  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T13.json  19 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T13.md  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T2.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T3.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T5.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T6.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T7.json  20 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T7.md  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_T8.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_c1.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_h1.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_h2.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_h3.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_h4.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_h5.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_h6.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_h7.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_k1.json  3 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_k2.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_k3.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_k4.json  3 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_m1.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_m2.json  3 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_p1.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_p2.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_p3.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_p4.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_q1.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_q2.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_q3.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_q4.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_r1.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_r2.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_r4.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_s1.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_s2.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_s3.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_v2.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_v5.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_v7.json  3 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_v8.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/areas_v9.json  3 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_A_bal.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_G0.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_G1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_G2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_G3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_S_bal.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_S_close.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_S_fair.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T10.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T11.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T12.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T13.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T5.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T6.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T7.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_T8.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_c1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_h1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_h2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_h3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_h4.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_q1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_q2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_q4.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_r1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_r2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_r4.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_s1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_s2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_s3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_v2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_v5.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_v7.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_v8.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/curv_v9.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_A_bal.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_G0.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_G1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_G2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_G3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_S_bal.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_S_close.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_S_fair.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T10.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T11.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T12.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T13.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T5.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T6.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T7.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T8.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_T9.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_c1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_h1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_h2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_h3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_h4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_h5.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_h6.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_h7.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_k1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_k2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_k3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_k4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_m1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_m2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_p1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_p2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_p3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_p4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_q1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_q2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_q3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_q4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_r1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_r2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_r4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_s1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_s2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_s3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_v2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_v5.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_v7.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_v8.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/eval_v9.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_A.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_A_bal.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_B.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_C.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_D.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_E.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_F.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_F_fair2_asym.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_G.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_G0.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_G1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_G2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_G3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_H1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_S_bal.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_S_close.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_S_fair.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T10.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T11.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T12.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T13.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T5.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T6.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T7.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T8.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_T9.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_V1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_V2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_V3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_W1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_W2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_W3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_W4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_W5.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_W6.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_X_0.3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_X_100.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_X_3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_X_30.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Y1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Y2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Y3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Y4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Y5.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Y6.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Z1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Z2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Z3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Z4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Z5.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_Z6.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_h2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_h3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_h4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_h5.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_h6.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_h7.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_k1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_k2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_k3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_k4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_m1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_m2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_p1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_p2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_p3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_p4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_q1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_q2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_q3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_q4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_r1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_r2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_r4.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_s1.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_s2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/_experiments/log_s3.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_F_fair2.json  18 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_F_fair2.md  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_F_fair2_asym.json  10 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_F_sym.json  18 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_F_sym.md  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_V1.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_V2.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_V3.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_W1.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_W2.json  9 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_W3.json  9 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_W4.json  10 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_W5.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_W6.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_X_0.3.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_X_100.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_X_3.json  9 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_X_30.json  6 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Y1.json  11 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Y2.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Y3.json  4 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Y4.json  7 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Y5.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Y6.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Z1.json  10 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Z2.json  9 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Z3.json  9 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Z4.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Z5.json  8 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/areas_Z6.json  9 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_F_asym.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_F_close.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_F_fair.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_F_fair2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_V1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_V2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_V3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_W1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_W2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_W3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_W4.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_W5.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_W6.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_X_0.3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_X_100.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_X_3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_X_30.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Y1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Y2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Y3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Y4.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Y5.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Y6.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Z1.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Z2.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Z3.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Z4.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/curv_Z6.json  0 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_F_asym.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_F_close.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_F_fair.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_F_fair2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_F_fair2_asym.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_F_sym.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_V1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_V2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_V3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_W1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_W2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_W3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_W4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_W5.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_W6.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_X_0.3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_X_100.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_X_3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_X_30.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Y1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Y2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Y3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Y4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Y5.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Y6.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Z1.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Z2.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Z3.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Z4.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Z5.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/eval_Z6.json  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/lines_table.json  5 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/lines_table.md  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/log_F_asym.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/log_F_close.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/log_F_fair.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/log_F_fair2.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/log_F_sym.txt  1 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/sections.json  172 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/sections_F_asym.json  173 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/sections_F_close.json  196 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/sections_F_fair.json  172 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1/sections_F_fair2.json  173 KB  2026-10-31
chest_ch001/ws/ch_clean/work/s1nx/curv_b2.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/curv_b3.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/curv_b4.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/dev_b2.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/dev_b3.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/dev_b4.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/neck_profile.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/rowjump_b2.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/rowjump_b3.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/rowjump_b4.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/sections_F_fair2_ext.json  114 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/wall_b3.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s1nx/wall_b4.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3/PARAMS_3a.md  3 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3/bore_fit.json  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3/dev2way.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3/faces_S2_S3a.md  4 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3/final/CH_S3c.stp  9.4 MB  2026-11-01
chest_ch001/ws/ch_clean/work/s3/final/SMALL_FACES.md  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3/wall_s2.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3b/faces_S3b.md  7 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3c/PARAMS_3c.md  3 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/END_SPEC.md  8 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/NECK_SPEC.md  8 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/m11_tipfit.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/m33_tip2arc.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/neck_armend.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/neckmodel_REC.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/neckmodel_S1VAL.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/userdiff.json  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_RevA.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_RevA.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_RevC.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s3spec/zones_RevC.md  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s3spec/zones_S1_B4.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S1_B4.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3_1.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3_1.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3b.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3b.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3b_9.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3b_9.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3b_probe.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3b_probe.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3c.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3c.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3c_1.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S3c_1.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S4_1.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S4_1.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S4_t1.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S4_t1.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S5_1.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S5_1.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S5_2.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S5_2.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S6_1.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s3spec/zones_S6_1.md  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s3spec/zones_S6_2.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s3spec/zones_S6_2.md  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s3spec/zones_S6pre.json  2 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S6pre.md  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s3spec/zones_S6pre_2.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s3spec/zones_S6pre_2.md  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s4/PARAMS_4.md  6 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s4/meas_s4.json  12 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s4/meas_s4.md  5 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s5/PARAMS_5.md  9 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s5/final/h8.log  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s6/PARAMS_6.txt  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/README_S6_1_backup.md  9 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/devtest.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/CH-001.pdf  176 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/CH-001_SH1.log  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/CH-001_SH1.pdf  176 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/dump_front.json  55 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/dump_right.json  11 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/dump_secA.json  28 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/dump_secB.json  47 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/dump_top.json  21 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t1/dwg_result.json  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/CH-001.pdf  260 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/CH-001_SH1.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/CH-001_SH1.pdf  260 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/dump_front.json  55 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/dump_right.json  11 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/dump_secA.json  28 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/dump_secB.json  47 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/dump_top.json  21 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t2/dwg_result.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t3/CH-001.pdf  256 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t3/CH-001_SH1.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t3/CH-001_SH1.pdf  256 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t3/dump_secB.json  45 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/dwg_t3/dwg_result.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/fin_test/CAD/CH-001_Chest_AP214.log  6 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/fin_test/CAD/CH-001_Chest_AP242.log  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/fin_test/CAD/_finalize.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/fin_test/dwgtest.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/fin_test/dwgtest2.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/fin_test/dwgtest3.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/fin_test/occ.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/final/dev.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/final/overlays.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/final/qa_done.txt  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/final/wall.log  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/final/wall_S6_1.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/final/zebra.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/final/zones.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/stepcheck_S6_2.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/sty/shield_fit.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6/wall_test.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6pre/SMALL_FACES.md  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6pre/neckmap_S5_2.txt  0 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s6pre/neckmap_S6pre_2.txt  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6pre/overlays_run.log  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s6pre/overlays_run2.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s6pre/zones_run.log  1 KB  2026-11-01
chest_ch001/ws/ch_clean/work/s6pre/zones_run2.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/inspect/own.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/inspect/rf.json  12 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a0.py  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a3.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a4.py  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a5.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a6.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a7.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a8.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/a9.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/b1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/b2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/b3.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/b4.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/b5.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/b6.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/b7.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/c1.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/c2.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/c3.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/c4.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/c5.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/c6.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/d1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/d2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/depth_vs_cad.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/e1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/edge_pos.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/edge_steps.json  7 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/edge_steps2.json  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/f1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/f2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/floor_planes.json  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/measure/floor_planes3d.json  7 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/diag1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/diag2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/diag3.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/diag4.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/diag5.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/ex1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/ex2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/go.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/insp.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j01_wall.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j02_sketches.py  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j02b_sketches.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j03_project.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j04_mirror_divide.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j05_divide.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j06_offset.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j07a_skin_divide.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j07b_probe.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j07b_skin_offset.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j07c_variants.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j07d_probe.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j07e_probe.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/j08_final.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/diag1.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/diag2.json  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/diag3.json  7 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/diag4.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/diag5.json  6 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j01.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j01.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j02.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j02.log  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j02b.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j02b.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j03.json  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j03.log  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j04.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j04.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j05_L1.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j05_L1.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j05_L2.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j05_L2.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j05_L3.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j05_L3.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j06_1.json  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j06_1.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j06_2.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j06_2.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j06_3.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j06_3.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07a.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07a.log  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07b.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07b.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07c.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07c.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07d.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j07e.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/j08.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/probe1.json  7 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/probe2.json  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/s7_01_wall_faces.json  14 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/out/s7_11_off_T_faces.json  28 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/own.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/probe1.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/probe2.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/rf.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/run.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/s7ctx.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/s7lib.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/s7proj.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/s7sk.py  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/seeds_big.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/seeds_skin.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/seeds_skin_z.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/seeds_skin_z2.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/step.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/step2.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/nx/step3.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/dev.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/dmap.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/mk_full.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/plane2.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions.py  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions_s00.json  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions_s01.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions_s01.txt  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions_s11.json  4 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions_s11.txt  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions_sF.json  5 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/regions_sF.txt  3 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/render.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/sec.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/seeds.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/seeds2.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/seeds_L1.json  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s7/qa/seeds_skin.json  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/diff_stl.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/dwg2.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/dwg_done.txt  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/fin.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/after_rt.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/go.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/insp8.py  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/insp_both.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/refstl.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/run2.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/small.ps1  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/nx/small.py  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/qa/dev.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/qa/overlays.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/qa/qa_done.txt  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/qa/wall.log  2 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/qa/zones.log  1 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/refstl_done.txt  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/rt.log  0 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/small.json  8 KB  2026-11-02
chest_ch001/ws/ch_clean/work/s8/work/ref_main.stl.json  0 KB  2026-11-02
```

## Appendix B: final/input CAD not in the zip (too large or over the per-project budget)

| Project | Original path | Size | sha256 | Why |
|---|---|---|---|---|
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver\CAD\CH-001_Chest.prt` | 12.9 MB | `0db4fdb28f89db8b5f5aa725b0a152b1afb18722df1ab5cfa0049cbca5c6f905` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver\CAD\CH-001_Chest.stl` | 38.6 MB | `c77ca526c58a018bc73a6daa529035cc331148f8d4686db20e4d03120ae1459a` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver\CAD\CH-001_Chest.x_t` | 2.3 MB | `e73f66922757f16d06f4d4574f4dcd771099e350cefc99f89bf6b71d09c2ed36` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver\Deviation_Check\CH-001_Chest_RevB_vs_SCAN.prt` | 43.0 MB | `1d844db5157083c89a29f93200a6b50811cb81fde75ee7c50990f3f87aaf813e` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver\Drawings\CH-001_dwg.prt` | 1010 KB | `a339d1517f6f85dfd88ed9f46d2d18887859bed40b3dae38cffe7963376baa48` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver_RevC\CAD\CH-001_Chest.prt` | 14.5 MB | `fa9ca321a777e283814c9069158989e523af24108b8e33120bcda67f4d523c61` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver_RevC\CAD\CH-001_Chest.stl` | 38.5 MB | `0b07967bdd18255471cacb01af00a5a71ccc2c8a265d6c7a007e75f19fcf380a` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver_RevC\CAD\CH-001_Chest.x_t` | 2.3 MB | `72869779638a74d119d1965d0448d0c5ff08cbaed407c93710137f792c5d68ce` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver_RevC\CAD\CH-001_Chest_AP214.step` | 13.7 MB | `559a8961907852cd38b8a20b6dfb8ab88a5f5d483a95a972df5cff7594b94c1e` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver_RevC\Deviation_Check\CH-001_Chest_RevC_vs_SCAN.prt` | 44.5 MB | `0200ee337cdbfcd76be89a3929e9ad83914ed72e1bbb5c1092c3fd6a07411826` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\deliver_RevC\Drawings\CH-001_dwg.prt` | 1.0 MB | `6e789cf4e69faf8f38e963b18b47298ef60d5dd13a970650909ac53b3c9bcbb8` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S1_A1\loft_raw.stl` | 22.8 MB | `c23a0b9a34f4de1cc151e4ae640f21cdfab585c7e6e42dfa3cee28a6bba8b3f9` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S1_A2\loft_raw.stl` | 25.6 MB | `2b410c6a441a542308ee86c76efcd2f3ffddffa2eaaa9e4b45c3491850d7cfe1` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S1_A3\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S3_1\s1a\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S4_1\s1a\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S5_1\s1a\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S6_1\s1a\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S6_2\s1a\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S6pre_1\s1a\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\nx\S6pre_2\s1a\loft_raw.stl` | 25.8 MB | `5bc1ab37a8e5746b1f23e8a007f5534d9c7939d11b9f1e32b77821ee3ab37a92` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s3\final\CH_S3c.prt` | 5.4 MB | `9048be067387987be80ee989759c605a0e22b6278128f7ee1b51a323a1b034b3` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s3\final\CH_S3c.stl` | 13.5 MB | `258dfc9450e85c298ed500b498877f16f9b7cb8c29a36526ca17840c6bc5dc77` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s4\final\CH_S4.prt` | 7.2 MB | `0c7b0b234852946e611995c7c7013655355ad53b317f753f72d81fa03787056f` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s4\final\CH_S4.stl` | 14.7 MB | `bc09beb31181b08a4dd3407672655f455e8b47a00eadd2a19c2a3606b1342487` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s4\final\CH_S4.stp` | 10.0 MB | `eefba6b9f65775d68187c65001966efba22b6b6353199fb9d27c4abc4d2ab833` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s5\final\CH_S5.prt` | 12.3 MB | `02477853f8c0e4fe3b60485760242182a9e3dc0dd4d18f11efde9d857d65cfa5` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s5\final\CH_S5.stl` | 17.3 MB | `61cf3dc0b9f2f2aad2f9e6bc63472b5a5b4a2448e4ba735546a90b64d3c7cbec` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\NX_MCP_WORKSPACE\ch_clean\work\s5\final\CH_S5.stp` | 11.3 MB | `6ecdb26adc037ca9fcec88e79475d6c9663213db1e63c9b81cb561f7f037d6fb` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\Deviation_Check\CH-001_scan_in_part_frame_0p6mm.stl` | 121.2 MB | `185d34a7e931ad4db59e584b3e22326505cea407aa438801447b1cba3bcbeeb0` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\_rounds2-4_2026-10-30\deliver\CAD\CH-001_Chest.prt` | 331.3 MB | `bff62932d4d59beee9c734fa67b8b5666ebfcaafa281707ee954bc28349d4a1c` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\_rounds2-4_2026-10-30\deliver\CAD\CH-001_Chest.stl` | 60.1 MB | `90ae6c6d7d6f0c9e1223a84bbd530f1b01a5477024ce8d8f97219dfe18ae9538` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\_rounds2-4_2026-10-30\deliver\CAD\CH-001_Chest.x_t` | 268.5 MB | `aa7756a2645024a69d8f568d71eb29dd80f2d5a814eb28c52afca041be8d7e60` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\_rounds2-4_2026-10-30\deliver\CAD\CH-001_Chest_AP214.step` | 193.3 MB | `ea4df60e777f5ae646f7a1834242333640bd25ad06cb08c0ef6b122269fcb1e5` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\_rounds2-4_2026-10-30\deliver\CAD\CH-001_Chest_AP242.step` | 76.5 MB | `0bd2019f42ea880fe8481644646c3a8f98ee709288d4b8365d8d0fed35160c05` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\_rounds2-4_2026-10-30\deliver\Drawings\CH-001_dwg.prt` | 8.9 MB | `3a53c499c8f579a464cbcdb9e5c0786c852cf6ad68ba0361826d52673fd6d9c4` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\deliver\CAD\CH-001_Chest.prt` | 34.3 MB | `d7c4846a9bf31bc0e9e117feccc6c4f483d7cc516a5e2646b8ba281c08ca3eb3` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\deliver\CAD\CH-001_Chest.stl` | 33.4 MB | `6e0be422fa81127440a82bd3c2a4fe2ef8748642d5847f304e6781c7c631380d` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\deliver\CAD\CH-001_Chest.x_t` | 3.6 MB | `b04b5f91bad5d529af8d35013a091b09f573eb979b57adccadc674e61de27b9a` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\deliver\CAD\CH-001_Chest_AP214.step` | 18.9 MB | `fdf1bc3d866b74240f12e6012d9e25a9802d03bb3139c8eab219e5ab4ddbe3cd` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\deliver\CAD\CH-001_Chest_AP242.step` | 7.2 MB | `193001dd8b21a548e05bb493be5cfa68294e3113501d94d09058f86b1b204491` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\deliver\Drawings\CH-001_dwg.prt` | 2.3 MB | `12ace5866c82614ef1dd3c750a78c816521fee8d801367890aded8fcfc1f61c4` | final/input CAD over project size budget |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\share-Chest.stl` | 704.6 MB | `2333e5fe7064991b1cb19bc5c567e2e4b5dd43f599db53c539e0d035faebb694` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\work\scan_600k_f.ply` | 21.5 MB | `45d8d85c2d1b0352982aab3a99799a795eaca5011c1bc384ec15152c12045bd2` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\work\scan_vc.ply` | 89.0 MB | `e01fbe2a0fb3f7d5902d503be72d922bc01c7322fdccb73e304be2995977500f` | final/input CAD > 20 MB |
| chest_ch001 | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 3 - Chest\work\scan_vc_f.ply` | 89.0 MB | `dab2c10c850c8fd2fc4ba6d4618c0ff7ccd04a74e527c400bb8a4e8229124a6c` | final/input CAD > 20 MB |
| dreame_brush_core | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\dreame_brush\out\scan_core_with_bristles_datum.stl` | 18.0 MB | `6d21d0b93df780262be99003492e8521b54d198f19d68a8888e233a353bfced3` | final/input CAD over project size budget |
| dreame_dustbin_air_inlet | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\dreame_air_inlet\out\scan.stl` | 195.6 MB | `1bba528d5b9c4d0bb2518bfa5caedd29fc0e7eb97ad8bc88e84788c7ce6b49f1` | final/input CAD > 20 MB |
| dreame_dustbin_air_inlet | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\dreame_air_inlet\out\scan_region.stl` | 46.6 MB | `ed7b5c24fdd1b00e0b852885de5500b954b0cf089866bb34158f41b01ae7738d` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `C:\NX_MCP_WORKSPACE\lt_clean\deliver\CAD\LT-ASM-001_Left_Thigh_Assembly_AP214.step` | 21.4 MB | `7b48a26af4c30bbb610fae198bb517a33f034e9fb0bbd44c549e70b8d872019a` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `C:\NX_MCP_WORKSPACE\lt_clean\deliver\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 29.0 MB | `1f28e314d0bab011c2ef7223df244e24600c54e728fcab78f780103c0785fcce` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `C:\NX_MCP_WORKSPACE\lt_clean\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 28.1 MB | `ba359250c0c65edb662778e2981e35a3f9f75af2b41ea2a85d1c11087ebffc92` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-ASM-001_Left_Thigh_Assembly_AP214.step` | 21.4 MB | `7b48a26af4c30bbb610fae198bb517a33f034e9fb0bbd44c549e70b8d872019a` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-ASM-001_Left_Thigh_Assembly_AP242.step` | 8.2 MB | `30b196e49645aaf924d2d5390942d08047c0575c9b16e013bb235ce52f852fa9` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 6.5 MB | `88e10dae69ac1e5ef30bfc972f9972673ca98d7b54739c9840088939797ca1f0` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 29.0 MB | `1f28e314d0bab011c2ef7223df244e24600c54e728fcab78f780103c0785fcce` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 2.2 MB | `301d7c3b3092d55198e4b07dcd983e1072aba71a1d3815b43e0c6996b7086bec` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-INN-001_Left_Thigh_Inner_AP214.step` | 11.7 MB | `a620520209f108b4f6df3d0c77a1867a059669fac26b9bc9daa7cdf7eeb9e721` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-INN-001_Left_Thigh_Inner_AP242.step` | 4.5 MB | `7bf9e07233dd9c449b3eed92cad0731bb7199cfd9f6db1d9ab3915ef37ad32d7` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.prt` | 5.2 MB | `ce4c497cfab697b411dd3ae509af5827f3d6d48c175c46170248b6ab1f707df0` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 28.1 MB | `ba359250c0c65edb662778e2981e35a3f9f75af2b41ea2a85d1c11087ebffc92` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.x_t` | 1.9 MB | `4d8f82670ae602b4d9e5c75f7a5ca188a9586e38b48eedf99b18c53fe2938c74` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-OUT-001_Left_Thigh_Outer_AP214.step` | 9.5 MB | `bbb2c5bd23d01e526f1fddb5b8d26c1385224e4e31f3d1a406b66e3c4d3c35a5` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\CAD\LT-OUT-001_Left_Thigh_Outer_AP242.step` | 3.6 MB | `0bfa424f5e9fdd353500077201fbaee7eb11f37e02bdd847cc453107d891294d` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\Drawings\LT-ASM-001_dwg.prt` | 1.8 MB | `f410bb53b8c5ae5753202528cefc4eb9521a3faec215ceac5f6db0105c8946f0` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\Drawings\LT-INN-001_dwg.prt` | 2.6 MB | `a2a319c2b1b8555004eeead849779e5dfab370914ccc7fd5d2e6669761c24a25` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 5 - Clean Rebuild\deliver\Drawings\LT-OUT-001_dwg.prt` | 2.9 MB | `b7ebdf89646f67f076bdcb2055c00673eff482237f5a1e53c61e673dcf57d8de` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-ASM-001_Left_Thigh_Assembly_AP214.step` | 45.2 MB | `e12ab0df3d8554063fe56dfdad1c17bbf5606b56982889c4916e075cf07c6438` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 9.1 MB | `f4f348a5d957ad9133179cbfbe5103229ee4962eb62059653d766ac964bb3ec1` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 26.3 MB | `3a8c1035fcd32a8dfbb70c9fbc032209c65f621a993f5b75949194a82146665a` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 2.7 MB | `3194b722d34d9723bd46135f69360bdc63733aff7d1b45c6556df868dab6adb2` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-INN-001_Left_Thigh_Inner_AP214.step` | 25.4 MB | `3985309143c41ab1dc9a6eb25773ef1950b8b4013c61d0739977c7187b94c8f7` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.prt` | 8.2 MB | `2e1d813717053114767db144ce09ce27b25a4b88b0e5cbd336f4fdd5943fc415` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 24.4 MB | `bf6e9425458c9b05627d291bb5723b261c8025ea3d203b1a5bfd096e78b4c357` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.x_t` | 2.5 MB | `adb6296effdcc4c67fcb857f35a3c1e9add275c790c2ba42cce2cc0732d52aad` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\Deviation_Check\LT-INN-001_Left_Thigh_Inner_vs_SCAN.prt` | 165.4 MB | `6d2933ee2596f0ec08cbe0d579de8f882838eb37a5f62dccd32ff78ecf9a2610` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\Deviation_Check\LT-OUT-001_Left_Thigh_Outer_vs_SCAN.prt` | 163.9 MB | `20b36e6ee0bbc43aa868c6a09691f70be50570c2471e93fadca524f45be13c0f` | final/input CAD > 20 MB |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\Drawings\LT-INN-001_dwg.prt` | 2.6 MB | `6d0b8885a29adfde699235b8d99f1f506d45bf0fcfc54ba77e0e1df4d87034f2` | final/input CAD over project size budget |
| left_thigh_clean_rebuild | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 7 - Clean Rebuild v2\deliver\Drawings\LT-OUT-001_dwg.prt` | 2.8 MB | `4773368c892aae73eb782c5bc9e309af316af154ea3668537aa3d1699486c383` | final/input CAD over project size budget |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_inner_fitE\deliver\LT-INN-001_Left_Thigh_Inner.prt` | 49.4 MB | `56aa51d02bca47a98a57a3038feba09f49efdd9c12e96863c8f96d0a42a827b9` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_inner_fitE\deliver\LT-INN-001_Left_Thigh_Inner.stl` | 22.6 MB | `23c1d638dc92966695afc9f5a0b44303c430dc1f3688facdfb20823054941284` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_inner_fitE\deliver\LT-INN-001_Left_Thigh_Inner.x_t` | 15.6 MB | `d824ed80e1d9c0b95728c2960058d4fb31097359bd809961e371aaaa9a86d78f` | final/input CAD over project size budget |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_inner_fitE\deliver\LT-INN-001_Left_Thigh_Inner_AP214.step` | 9.0 MB | `0c6f5a9d574be584bb97876cda3ba15276157325706f2397509e9e78694feaaf` | final/input CAD over project size budget |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_inner_fitE\deliver_web\LT-INN-001_Left_Thigh_Inner.prt` | 49.5 MB | `fe9046a17f5254a123f9817cfbf6e79ef5fad314076472405859866a75aab6b5` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_inner_fitE\deliver_web\LT-INN-001_Left_Thigh_Inner.stl` | 22.7 MB | `77f0b0fefb4f1ab1147303e229315f49f5cad83f4f0341269f4debbcc6983e81` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_inner_r8\scan_dec.ply` | 35.7 MB | `914ecf85a53c3911bc254ad0425ca06d371bb1e26eceb26b51b756d42c4376c8` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `C:\NX_MCP_WORKSPACE\lt_window\scan_roi.stl` | 52.7 MB | `8b6e68cfa5df8e6321513feb6d903dd8a08275ba9ea6fa2240d5548f9b9a6c43` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\SHARE -  Left Thigh - Outer.stl` | 346.5 MB | `49fdbd4ea9f918bbfde9a1b11e87365da43faa06caf602c959903e4e110c248c` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\SHARE -  Left Thigh - Outer.stl` | 346.5 MB | `49fdbd4ea9f918bbfde9a1b11e87365da43faa06caf602c959903e4e110c248c` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.prt` | 12.7 MB | `d465ecca9bc0f2b78b22b95115053abe4a2c01b71f3c46fa66cf9db450e1f976` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.0 MB | `c6c6e4fe2937c9b6265b7546aa9346e618b509a01b47ce1938443fcb5d25f06d` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.x_t` | 3.5 MB | `5a6aab1da3f3b7ab3653843145705440b2f3499caefff7284908d90913458145` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver\CAD\LT-OUT-001_Left_Thigh_Outer_AP214.step` | 10.3 MB | `7fbf0e2f9e6412b16beecb9e71fcd552c88df12101d0ccc3f26cabb3c412eb0a` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver\CAD\LT-OUT-001_Left_Thigh_Outer_AP242.step` | 3.2 MB | `d6a9f2b72627a1649e06ad1d04a1fae85510f2707d6be9ffc6d2185f9887f3db` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver\Drawings\LT-OUT-001_dwg.prt` | 2.2 MB | `267cdc4f6496bfe92315de27acf7070d32028d6cb6ce4023a41cfce42c8cb724` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevB\CAD\LT-OUT-001_Left_Thigh_Outer.prt` | 12.7 MB | `b5a949dd5383772c89e226815014ba902feff6a2ac72e2fbcc8893c19692f14e` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevB\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.1 MB | `d4c543ed66b329b2bec2051fe8ec865ca78b5e5d9c7311176b75a990a9f99404` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevB\CAD\LT-OUT-001_Left_Thigh_Outer.x_t` | 3.5 MB | `08743d44ab35eeca5b2ba8378e350e0e1054aee7a14af91315677f29464e3c29` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevB\CAD\LT-OUT-001_Left_Thigh_Outer_AP214.step` | 10.4 MB | `ff2943882e9f36a89a43cd7ea0c94a3cb8670a8e4661c23a48816b8acf137bf9` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevB\CAD\LT-OUT-001_Left_Thigh_Outer_AP242.step` | 3.2 MB | `27c9163d6b3aa8f28daff51f5761487ccd83b65b873e7f5d2dbf439f87cdc455` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevB\Drawings\LT-OUT-001_dwg.prt` | 2.5 MB | `90d160f38a27c7e540970d6d3f63f0e346ddca7ce2e41e313b426d8e70cb5b6e` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevC\CAD\LT-OUT-001_Left_Thigh_Outer.prt` | 17.5 MB | `7c48a941c7313f5fc2b908adcf9546483917ccee2062b355b82b907a8c156070` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevC\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.7 MB | `2d653a2126c9b7ad02aecc96c563721a81ea7ffb876b6fc4873c3f724b0888a5` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevC\CAD\LT-OUT-001_Left_Thigh_Outer.x_t` | 5.0 MB | `6b81a67cd2e46315befd9f49627078d357754fbb4b887330f6cf27f3a73018c3` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevC\CAD\LT-OUT-001_Left_Thigh_Outer_AP214.step` | 9.3 MB | `1c1ee769473c76bc48a60fc5411a31a69be3a652374f5ae0255ca51787a0cb2a` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevC\Drawings\LT-OUT-001_dwg.prt` | 2.7 MB | `159fbc9873c199565bc3678412ba329159870e1abe7c7720c2cac3a0d7bff1a1` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevF\CAD\LT-OUT-001_Left_Thigh_Outer.prt` | 15.4 MB | `86ae45be30c695b0f9c3ff623e7c7c670c4f93442e102f5af27c3025b24dbb15` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevF\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.2 MB | `645fa820a279c962bb1dba05d5052f0404bf7b0a341fbf405d26d46f2253a78e` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevF\CAD\LT-OUT-001_Left_Thigh_Outer.x_t` | 9.3 MB | `ec34db48558d35000090070dc7898f6d4876e27fc71cce327307a3c94ee6080f` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevF\CAD\LT-OUT-001_Left_Thigh_Outer_AP214.step` | 9.0 MB | `b503630391461ed6676418e24cb7c1d4f8d57cd5adb6dc032befc0c8e1e7e655` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\deliver_RevF\Drawings\LT-OUT-001_dwg.prt` | 3.0 MB | `2f351045de2df9216064db377a5aca21c5a9274a5fa68cb271c50b2ccd0b5cb9` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\final_rt\RevA_before_user_edit.prt` | 11.9 MB | `a0a8aaec998305dcdbfac3986a7f995edfd70b7afa094f38ba7ae1531592fba3` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\overlay\scan_in_part_frame.stl` | 346.5 MB | `78474a9308f189011a789cc128f96bb270ec6ea6df831ec0d357a7ef424afdc7` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\revF\final_run2\LT-OUT-001_Left_Thigh_Outer.prt` | 172.1 MB | `a50d5f076d3a4af80dcd9f138058a81f93fec350db318c32c0137988ba3596dc` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\revF\final_run3\LT-OUT-001_Left_Thigh_Outer.prt` | 172.1 MB | `a50d5f076d3a4af80dcd9f138058a81f93fec350db318c32c0137988ba3596dc` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\revF\final_run4\LT-OUT-001_Left_Thigh_Outer.stl` | 22.2 MB | `645fa820a279c962bb1dba05d5052f0404bf7b0a341fbf405d26d46f2253a78e` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\revF\final_run4\_main_before_unite.stl` | 22.0 MB | `fbc56f1066ae23f66cd83af45a9476e46248940dd1ed17255d91e9caa523308a` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\revF\final_run4_main_before_unite.stl` | 22.0 MB | `fbc56f1066ae23f66cd83af45a9476e46248940dd1ed17255d91e9caa523308a` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\scan_600k.ply` | 21.5 MB | `d6c55b4d2a5918f2659f83ada8628a07196f16e243dbd125542eb483ae9986d3` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 1\work\scan_600k_framed.ply` | 14.5 MB | `42b4c35bbeb3d57b97b4f83769d73d50ce49f04b77cc6235498f9f93e74e65a0` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\_fixround_2026-10-30\deliver\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 31.9 MB | `5f77bc03af4eda9ba7fddde2d8c4a26cdc5524dfafe4273890f741ef37a92a09` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\_fixround_2026-10-30\deliver\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 24.4 MB | `6c1da2fb7061996c33cf587ecccf2038d0637171ac771351d629655c42492af2` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\_fixround_2026-10-30\deliver\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 8.3 MB | `c6b55ce936d5788dd929008a64e7b743f41ef000f02f58e82e2a187dd1ae2f12` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\_fixround_2026-10-30\deliver\CAD\LT-INN-001_Left_Thigh_Inner_AP214.step` | 17.1 MB | `1e46220e36b309dbb71e535056aac3cc93a88db338bc9c4de63b4cd8d86e1fcb` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\_fixround_2026-10-30\deliver\CAD\LT-INN-001_Left_Thigh_Inner_AP242.step` | 6.8 MB | `a2adb31a732cf0b09bf96e1e1ca5d40e9089d81bb3b1def43e396f71cd2f31f0` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\_fixround_2026-10-30\deliver\Drawings\LT-INN-001_dwg.prt` | 3.1 MB | `ad2f52dda55243ac5058e7a8b091a0b9444df29e93bca9422089e7895bdefa7c` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 20.1 MB | `31089bebf049ec33ff0827ba7809363ec594778fe3304b15cdcc82ac392df973` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 23.8 MB | `39463197eb4123b0aefb833b221590bdff1d2e0b0e9c08014b19f04a20fc3f8e` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 5.2 MB | `cbe9eea3521818e9d9bdad03763c93deec6fddff32a70d53ff16e139d6cfbfe8` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver\CAD\LT-INN-001_Left_Thigh_Inner_AP214.step` | 9.0 MB | `7147484453a08ca36581d91669f63eeaa4f8db035cc8f7bd1ff060f4647d1404` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver\CAD\LT-INN-001_Left_Thigh_Inner_AP242.step` | 4.5 MB | `90833805d02fa28bea020872aa2bc3cecd69ddb94f80e4b6e0fb1b0a4b222cab` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver\Drawings\LT-INN-001_dwg.prt` | 2.7 MB | `6c54c131a932b13be6ade7490f5d9089a89ff63d33659865fc6cd4d409422bcf` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevB\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 31.5 MB | `85f7d945c43dbea46e25f33d7d3ce6eeea236bfb653a204b07f3e6c35db28ad9` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevB\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 23.2 MB | `968dcc29cc1f21458dae4329cc8cee813cd1f699c870f256ad7b91ec2123016f` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevB\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 4.0 MB | `324fa57ebc55f914cbc95ec3bed0d5a0a1f40e1182df2ae6a78133ba6e141c57` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevB\CAD\LT-INN-001_Left_Thigh_Inner_AP214.step` | 7.8 MB | `61e1daf1b86d9432c319156940138b074d607f1bc6f4083111989142d9092796` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevB\CAD\LT-INN-001_Left_Thigh_Inner_AP242.step` | 3.2 MB | `354c0dc09dd60a3b0881032754ac8708c112dedc527723dcd0d499314c199e62` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevB\Drawings\LT-INN-001_dwg.prt` | 2.5 MB | `b98883b48e89d44a235d5d86f9fccb2b29b32cb53456c9d2f37a3289f9c1b990` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE2\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 50.9 MB | `ea91482bc4e244aeb49cff323c5c9ad2600a1c2218e9055051b3b44384178a6a` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE2\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 22.7 MB | `5b25e30e0a7fd2320cde65213429d752a794e2a454059eb1aa379338c5af4af4` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE2\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 13.3 MB | `dd338214523f93e7970d02579df4f8c5aa99ce80e24ab27e3b3df76ee40da60a` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE2\Drawings\LT-INN-001_dwg.prt` | 3.3 MB | `d2fb8948c4a6efaad18dfc3196d3861e6da6a674ff08e7d4c44fc80b63dddad7` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 20.1 MB | `0cf0eb6688d9df3ccacbd246232a2d08f856a6b6cf3620fca9e557571e19a084` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 22.3 MB | `089e0f56fa9bc8689457b9a86fc7dc6ca177ef822b7dc15ed41a85a2d82aa8e1` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 13.0 MB | `24d1515b774e21510db9178513ce6c9a0d7e45f902e6bbc697d5950239d5fed3` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE\CAD\_main_before_unite.stl` | 22.3 MB | `089e0f56fa9bc8689457b9a86fc7dc6ca177ef822b7dc15ed41a85a2d82aa8e1` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE\CAD\_start_main.stl` | 14.0 MB | `5349a14bba5f65ca7d0acd6f5f77197b1cb4abe466d7bb5a85ff1365b1d098b9` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE\CAD\_start_main.x_t` | 13.0 MB | `90454738dc51c439e11ee5de758c90f66c36a866d5fd7f6491043e3235ed8429` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE_fit\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 49.5 MB | `fe9046a17f5254a123f9817cfbf6e79ef5fad314076472405859866a75aab6b5` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE_fit\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 22.7 MB | `77f0b0fefb4f1ab1147303e229315f49f5cad83f4f0341269f4debbcc6983e81` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE_fit\CAD\LT-INN-001_Left_Thigh_Inner.x_t` | 15.6 MB | `9ee9d86a79d6d592646d1fa20a605ff89bb93c68d072ba1d57ff9072b30edb77` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE_fit\CAD\LT-INN-001_Left_Thigh_Inner_AP214.step` | 9.0 MB | `5e8ab0ce43e7ddfe8aedb00e46e05b3e3bacae1c25cee412eb2e7daf672626e4` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\deliver_RevE_fit\Drawings\LT-INN-001_dwg.prt` | 3.3 MB | `951639417b986a0676613584bf8c4a68879a7d0f0124b4c4ce699d1dddb33e58` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\share-Left Thigh - Inner.stl` | 354.9 MB | `3af29afd4222eebfdbefbdf01ed734eabfabd0b4b83846bbaabadc8bb0e5a3d6` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\work\overlay\scan_in_part_frame.stl` | 354.9 MB | `3a2593fa3bc6363a23ec4407444e5bdd19b69cbef977f71def76611c8f8f6929` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\work\scan_600k.ply` | 21.4 MB | `7833ba683d29f56a65f697a68b917f22f9ed2357db96372418dd7f24adbfb926` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 2 - Inner\work\scan_600k_framed.ply` | 14.4 MB | `3723352057739c3e99754ec31cf9e4e87868a9960a1921d819742ff15461ba76` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\LT-ASM-001_RevE_Left_Thigh_Assembly\LT-ASM-001_RevE\CAD\LT-ASM-001_Left_Thigh_Assembly.stl` | 44.9 MB | `850ab839f86543e88a569755b07613be72d2e396c321a674b155b6e7e74b4ba7` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\LT-ASM-001_RevE_Left_Thigh_Assembly\LT-ASM-001_RevE\CAD\LT-ASM-001_Left_Thigh_Assembly_AP214.step` | 18.2 MB | `c7cefe3cbfc9174e7c484c5a2d47f28e36bc87e632cf5431e3d9e9905b3897ea` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\LT-ASM-001_RevE_Left_Thigh_Assembly\LT-ASM-001_RevE\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 50.9 MB | `ea91482bc4e244aeb49cff323c5c9ad2600a1c2218e9055051b3b44384178a6a` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\LT-ASM-001_RevE_Left_Thigh_Assembly\LT-ASM-001_RevE\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 22.7 MB | `77f0b0fefb4f1ab1147303e229315f49f5cad83f4f0341269f4debbcc6983e81` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\LT-ASM-001_RevE_Left_Thigh_Assembly\LT-ASM-001_RevE\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.2 MB | `645fa820a279c962bb1dba05d5052f0404bf7b0a341fbf405d26d46f2253a78e` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\LT-ASM-001_RevE_Left_Thigh_Assembly\LT-ASM-001_RevE\Drawings\LT-ASM-001_dwg.prt` | 2.2 MB | `0f4e27a80c09e4c4af93f63df75cec15c261f41506545e055c10488a7387d895` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver\CAD\LT-ASM-001_Left_Thigh_Assembly.stl` | 45.9 MB | `cd35341f933013673941d369fa01c8965b2f5531f840c60238d5b0b6235de626` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver\CAD\LT-ASM-001_Left_Thigh_Assembly_AP214.step` | 19.5 MB | `5159e2562c765cfbd1b204113c094180d98f957a55d7330bd3ff87b412790560` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver\CAD\LT-ASM-001_Left_Thigh_Assembly_AP242.step` | 7.8 MB | `22c7baa279152c0e09ebdbf32a5cd77e753f7e701b681c157667df516bae9f97` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 20.1 MB | `31089bebf049ec33ff0827ba7809363ec594778fe3304b15cdcc82ac392df973` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 23.8 MB | `39463197eb4123b0aefb833b221590bdff1d2e0b0e9c08014b19f04a20fc3f8e` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.0 MB | `c6c6e4fe2937c9b6265b7546aa9346e618b509a01b47ce1938443fcb5d25f06d` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver\Drawings\LT-ASM-001_dwg.prt` | 2.1 MB | `91593cf02f8a72a23ee0023e8e5a1be9c2b6b52a8d2b70768fe021ef233eaa03` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevB\CAD\LT-ASM-001_Left_Thigh_Assembly.stl` | 45.9 MB | `5e3a849253a39b823fb6ebf7281ee5f108572059d124ab3880e13cdfecd59274` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevB\CAD\LT-ASM-001_Left_Thigh_Assembly_AP214.step` | 17.4 MB | `79fc96417708662a2d12d64b64748cf12594432df9cc786d78403ddc6ab13197` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevB\CAD\LT-ASM-001_Left_Thigh_Assembly_AP242.step` | 6.1 MB | `065aa829bea0df2f600b20fdc98ebf784f0aaf180fed693570602aa86f244769` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevB\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 31.5 MB | `85f7d945c43dbea46e25f33d7d3ce6eeea236bfb653a204b07f3e6c35db28ad9` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevB\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 23.2 MB | `968dcc29cc1f21458dae4329cc8cee813cd1f699c870f256ad7b91ec2123016f` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevB\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.7 MB | `2d653a2126c9b7ad02aecc96c563721a81ea7ffb876b6fc4873c3f724b0888a5` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevB\Drawings\LT-ASM-001_dwg.prt` | 2.1 MB | `c9254f6d7342bf9667a6b5c98d56fe3d198142f36f493cbde75bfb15a6d090a1` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE2\CAD\LT-ASM-001_Left_Thigh_Assembly.stl` | 44.9 MB | `c4098e9b1dd552b5046f83efc030fda7abd0cbbbe710bcd1c11b29df40c87779` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE2\CAD\LT-ASM-001_Left_Thigh_Assembly_AP214.step` | 17.7 MB | `4960814738ded7d89e8b547975fb937839ddb96277b10c28f852269d6b50150f` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE2\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 50.9 MB | `ea91482bc4e244aeb49cff323c5c9ad2600a1c2218e9055051b3b44384178a6a` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE2\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 22.7 MB | `5b25e30e0a7fd2320cde65213429d752a794e2a454059eb1aa379338c5af4af4` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE2\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.2 MB | `645fa820a279c962bb1dba05d5052f0404bf7b0a341fbf405d26d46f2253a78e` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE2\Drawings\LT-ASM-001_dwg.prt` | 2.3 MB | `6a91be225fca98da201a729b747b11ffd1c0fa342780189622be700c96d29944` | final/input CAD over project size budget |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE\CAD\LT-ASM-001_Left_Thigh_Assembly.stl` | 44.9 MB | `850ab839f86543e88a569755b07613be72d2e396c321a674b155b6e7e74b4ba7` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE\CAD\LT-INN-001_Left_Thigh_Inner.prt` | 49.5 MB | `fe9046a17f5254a123f9817cfbf6e79ef5fad314076472405859866a75aab6b5` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE\CAD\LT-INN-001_Left_Thigh_Inner.stl` | 22.7 MB | `77f0b0fefb4f1ab1147303e229315f49f5cad83f4f0341269f4debbcc6983e81` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\part 4 - Assembly\deliver_RevE\CAD\LT-OUT-001_Left_Thigh_Outer.stl` | 22.2 MB | `645fa820a279c962bb1dba05d5052f0404bf7b0a341fbf405d26d46f2253a78e` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\share-Chest.stl` | 704.6 MB | `2333e5fe7064991b1cb19bc5c567e2e4b5dd43f599db53c539e0d035faebb694` | final/input CAD > 20 MB |
| left_thigh_outer_inner | `D:\C_Tasinan_2026-11-04\Users\marya\Desktop\Left Thight Reverse Engineer\share-Left Thigh - Inner.stl` | 354.9 MB | `3af29afd4222eebfdbefbdf01ed734eabfabd0b4b83846bbaabadc8bb0e5a3d6` | final/input CAD > 20 MB |
| lexus_seat_clip | `C:\NX_MCP_WORKSPACE\lexus_seat\an\scan_part.stl` | 23.9 MB | `d77b678e62c762c991bcdef4a67c1ee39bf2013d0bd00a9091ab315e6da8f072` | final/input CAD > 20 MB |
| lexus_seat_clip | `C:\NX_MCP_WORKSPACE\lexus_seat\an\scan_part2.stl` | 23.9 MB | `120907f6fc6441cbad04e53eecf0db7d02f2702977b5657e6d889271036556ff` | final/input CAD > 20 MB |
| lexus_seat_clip | `C:\NX_MCP_WORKSPACE\lexus_seat\an\scan_tableframe.stl` | 23.9 MB | `2dcc4f070ea4a6db4b41eb8511fd139a29a0fa95a29c7f0eb645e6b537b721ee` | final/input CAD > 20 MB |
| lexus_seat_clip | `C:\NX_MCP_WORKSPACE\mesh_135528\scan.stl` | 23.9 MB | `1448e911a9dd1fa3fa7dd85b10a43c50ae738c7e7dfebeab9e89ed56b0530146` | final/input CAD > 20 MB |
| lexus_seat_clip | `C:\Users\marya\Desktop\lexuspart\Mesh_20261024135528.stl` | 23.9 MB | `1448e911a9dd1fa3fa7dd85b10a43c50ae738c7e7dfebeab9e89ed56b0530146` | final/input CAD > 20 MB |
| r385_pump | `C:\NX_MCP_WORKSPACE\ep5_hs03\scan.stl` | 25.9 MB | `bbe13fdfcbb1e02cb482d52c7d514ac8b0e826f7425fc83179dc380138cb86a4` | final/input CAD > 20 MB |
| r385_pump | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\r385\scan\R385-HS03_scan_aligned.stl` | 27.5 MB | `101a6b5ade19ddc559893f237b7297f3347434ec7cf2e35435f7de211ac40adc` | final/input CAD > 20 MB |
| r385_pump | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\r385\scan\R385-HS03_scan_aligned_as_merged.stl` | 27.5 MB | `9702b163241465a9d0f4b81c2c21381b8df07bfa5bb379ded1d33a39924f0e45` | final/input CAD > 20 MB |
| r385_pump | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\r385\scan\R385-HS04_scan_aligned.stl` | 37.0 MB | `b5deabf3eaf1ef26644b40fc3262000251c8d738c5fba25f11a274993ae007f2` | final/input CAD > 20 MB |
| r385_pump | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\r385\scan\R385-SL03_scan_aligned.stl` | 2.9 MB | `66281c57f1fad28dc7c4d7689b76a3eb7e8372c99f3a27514b9dc24ed938afef` | final/input CAD over project size budget |
| r385_pump | `D:\C_Yedek_2026-10-15\02_Tam_Yedek\C_NX_MCP Workspace\r385\scan\R385-SL04_scan_aligned.stl` | 4.6 MB | `876afeb606e38fe2536aabbe1c307d812785b6e50aaa1a08d3f255319f7b4e2c` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-DR02 Salinim Plakasi.stl` | 8.9 MB | `d63dabdb65d12034ae7eb6b35ebf683c83b644bacadc54d13c347411e41d288f` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-DR02 Salinim Plakasi\pS2sB_knsI_wjKk_Vzmw\result\Mesh.ply` | 4.5 MB | `51695c27c052b58fc3edfd9c0d49dfe3c5653f0b703f7abf0f302f98248d24eb` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-DR02 Salinim Plakasi\s6xqhhQ_ibWE1o_9GC3eT_IgUFES\result\Fused.ply` | 4.1 MB | `5c249e941a3d8c6ce389d01ece268d3bbc668dab6377e644620bb55d82ca2d7c` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS01 Motor yuvası.stl` | 14.3 MB | `51113108e685d5cd656f7077f363e8298ecd7b8acf26e1fecb2720f3bb8c2502` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS01 Motor yuvası\pCGW3_zXKb_Oomy_hkVH\result\Mesh.ply` | 7.2 MB | `4aea2a4bd764149740e5e069fb78150869c4dca24eef60202c4c684d933cddb6` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS01 Motor yuvası\sYnHPNH_sLxMZU_p0myKu_5YU2C8\result\Fused.ply` | 14.3 MB | `82225ff9b86458e76b8cfec1bcc2c05a96c861e8cb82b5f08472a2dd58cf4644` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS01 Motor yuvası\sfem2Az_2N8Nb0_xHlkxl_zqafj7\result\Fused.ply` | 17.9 MB | `b9ea040d36c1a6207fe2601569b4b4dcf9614588e01d0d4065dc7341eccd2ae1` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS02 Diyafram Cercevesi.stl` | 28.3 MB | `dedf13838b79d2101604cd24be6e7cc6a0f1e96b2b4e90145ed3a7af98619b91` | final/input CAD > 20 MB |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS02 Diyafram Cercevesi\p4nam_1ikD_z3l7_0mTK\result\Mesh.ply` | 14.2 MB | `4a6897d590120be6f70dca462e8fca864f13e601604171b8695073ba2720e525` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS02 Diyafram Cercevesi\sGpbYYy_4GRN3m_d1DclC_RhpdAl\result\Fused.ply` | 15.0 MB | `3637f9d62b708e2334a7df277a0ee2c96d788b8434d8955ecf72850a07029bd1` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS02 Diyafram Cercevesi\swPh6uV_y9qc6X_vN5ARp_KeR6jf\result\Fused.ply` | 17.5 MB | `e88a211fb2b8ad1d7e76bbd9bbae9a125d17963f707d2b9779421ae2ba2e521f` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS03 Valf Plakasi\puspJ_0aGN_yW4F_AFZO\result\Mesh.ply` | 13.9 MB | `2d69b26a3621a96a8da28de44c001d2d5923f9fade5f42b7f51b708d8f176c4f` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS03 Valf Plakasi\skYlpzl_nFd1As_KWMYar_qxvB1N\result\Fused.ply` | 17.2 MB | `5b3d2ec9165f604fd1589bc8a59e744db85d853c542a5d50b8c92102caea0703` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS03 Valf Plakasi\sliJ45a_AH6W25_punYbr_k2JGBs\result\Fused.ply` | 17.6 MB | `335cbaf6cf8e60474bae8d8aeae81489bb24e937b9399c064295d0674db330c2` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS03 Valf plakasi.stl` | 27.6 MB | `a67e7416f1720c949235afbbd55ced2dacd5054d38e82f7a1175e9b16b8b9f92` | final/input CAD > 20 MB |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS04 Pompa kafasi.stl` | 37.7 MB | `b8e49fb1efca51164789c7cd32a63811bd96220fa10a227127767f256cd7e867` | final/input CAD > 20 MB |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS04 Pompa kafasi\pvsAj_n6kV_hl5y_d1Ca\result\Mesh.ply` | 18.9 MB | `153921f136f7bd5fe7ef33e1ff10ae4fb97f1ecea9e37f68fcad2f03a91d27c0` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS04 Pompa kafasi\s1yqBrq_opo2oQ_lL5b4j_0LUt4o\result\Fused.ply` | 13.8 MB | `02984944fb8d8e41b5b27228a53221586b96ed6b96512b04f4b578746c9db108` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS04 Pompa kafasi\s3SZUFm_KTtWGw_d8DOxd_OHWu08\result\Fused.ply` | 12.3 MB | `da7d1b3a590546eded7beed0446079fd2dd499808afdd6a125f628b8aee0ac81` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-HS04 Pompa kafasi\sqGhFaM_2cj4Xe_HPoVF7_W4M8Ek\result\Fused.ply` | 11.9 MB | `3055d30fbecfd0f892ca1af7eaac0c616a0c77d845fdcc7b7d06a206af4d0aca` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-MT01 DC motor.stl` | 14.3 MB | `9ac497b58336949e750cb3b5285909bfdbc6389851e63093de55425c6ca41e19` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-MT01 DC motor\piSjF_FjBr_J8B0_LcWd\result\Mesh.ply` | 7.2 MB | `08bde67a0a07270a053027a0e9b411d3ed33ded4fbfa69bb5ea67e369ca3cdca` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-MT01 DC motor\sOQi5yc_KSAIxA_9o1HsY_JjmJa8\result\Fused.ply` | 18.3 MB | `1d346df75986d3da37c9bd63f33a3a31223587e8f50347a313b00e1aa51bfdfe` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL01 Diyafram.stl` | 19.1 MB | `0c3ec982146aef2cf021fab91bcf2f81626592b14731ea69e9f86219b9d1d7a1` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL01 Diyafram\pQLE5_GndY_1FEp_xdoN\result\Mesh.ply` | 9.6 MB | `0bd96cbdaaf151cbecabc47b475c40ab63867090df3673100280c527d86689cc` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL01 Diyafram\sDLJ99K_Rq6CvI_fVxzpz_pFq6Bl\result\Fused.ply` | 18.2 MB | `d1051edad47ba4f106af54856b86cd5e460d72d57a9df178fa1defeaabafd33d` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL03 Basma valfi.stl` | 7.7 MB | `f710a2452cd01fbea7a6dc5f81f93213ec89d8ea48b43ff526931260b58d7995` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL03 Basma valfi\pYgIb_J7iA_Hydo_tTlA\result\Mesh.ply` | 3.9 MB | `dee156c5a81b201b1833d5cddd71fd191e9c62fd24cedf0efc3882a3f338bbd5` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL03 Basma valfi\sERVIhd_OdhLLk_hAE987_qbrPnw\result\Fused.ply` | 4.3 MB | `a2e0c4427e30ba39b7701b4a407685dd9457dc3308183fe0ca8e6a47152e9471` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL04 Kafa contasi.stl` | 9.5 MB | `ab9a248154c09cd1de7ea62248406826e7e9aaf5d5a1ab2aa5d684fa7a79af3e` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL04 Kafa contasi\pHykP_lKCw_w1MU_CmAc\result\Mesh.ply` | 4.8 MB | `d0b15a7f69ca6907886cbfa38bc6502c359716641331c07f5ec1c2e0a1796631` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\R385-SL04 Kafa contasi\shxnCCC_rvKoUx_J5QcT5_VPdqjL\result\Fused.ply` | 10.1 MB | `065e32fad6c7466b851cb2cfc9a25cc935de61cd1c08662cd7a095536f35ed59` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\outer.stl` | 23.2 MB | `aff8900c5791297120a2129d33783e79d7daf2f5076fbc780a781308029aec69` | final/input CAD > 20 MB |
| r385_pump | `H:\My Drive\Mini Pumps\r385\outer\pAlAX_Jk8j_xP9v_tDK0\result\Mesh.ply` | 11.7 MB | `9f92800939ba923dbfbdcf25ce8a986758f54efc541c2f7c11f0e939f84ca6b3` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\outer\sOP82eu_5MljvC_jQTZzM_QLrlEs\result\Fused.ply` | 41.0 MB | `9f1a7ad60ef66c2538ff57116e2b0a893943e508b904f96c407a711fb7f5f7f2` | final/input CAD > 20 MB |
| r385_pump | `H:\My Drive\Mini Pumps\r385\outer\sOP82eu_5MljvC_jQTZzM_QLrlEs\result\model.ply` | 3.4 MB | `9dc826adea66a677bad59a3f8f93cb08141cb913360c23e78c0c8e203844ccf8` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\outer\snMC8eX_70Ftp0_OpKoxq_cEyc0t\result\Fused.ply` | 54.4 MB | `718f1a34807d10c3ad37f56972a9e62f26450784083286cf01542c41a49ce49a` | final/input CAD > 20 MB |
| r385_pump | `H:\My Drive\Mini Pumps\r385\outer\snMC8eX_70Ftp0_OpKoxq_cEyc0t\result\model.ply` | 4.4 MB | `0d37858f237e9d06f1e3c48b6821126fe084a7cda0bb337895d4d563be3630d0` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\print\flex\R385-SL01_DIAPHRAGM.stl` | 7.6 MB | `d367a4237876c239c0fdc7efeb2cd067e2ff3408c0d36f0a202420f4e4c468bb` | final/input CAD over project size budget |
| r385_pump | `H:\My Drive\Mini Pumps\r385\print\rigid\R385-DR02_WOBBLE.stl` | 7.3 MB | `6f1efa873c62a0fb085fb4263ea72cc0d3dd9f0240546c4ad3ffcdc6bd25197b` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR01 Armatur.stl` | 11.4 MB | `02c9898d4cb439c46bec72cb59247502917dd5050d2b95fa1b0b2e49a60e7124` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR01 Armatur\s1UT26S_6i4i5u_r0duQj_5FPDdn\result\Fused.ply` | 6.3 MB | `25a74c5a2b55dfcd9c1211f4bc54016f56406546a10a05031680b23e17d24ef6` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR02 On yay.stl` | 11.9 MB | `ddd300c36ca0340550df2c2a24b83fe17f67b15882a0e69d0caa9545c25dcb54` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR02 On yay\pMMDz_sO4w_zBYi_HunY\result\Mesh.ply` | 6.0 MB | `7ce17510fdda4f8fcc0201db96877836eee6c7c64b246ec8b9c0478f75cdecf3` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR02 On yay\sGMGmDd_JiCFFc_PAdxrQ_UrjvLg\result\Fused.ply` | 8.3 MB | `7f51d87a1486330de47df0fc6904fffbbb4ffd06fa264d106a69f10b756bc844` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR03 Arka yay.stl` | 14.3 MB | `8e10c92d1b476fad34946c63929b8d0f734cc8131241ffad345b775dfdcc0d79` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR03 Arka yay\pa9Hm_GJNr_Ihro_ij7t\result\Mesh.ply` | 7.3 MB | `5044461e013837348a7cf72ac26bbe3874ca90ca8ddad44f257b7e752df4635b` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-DR03 Arka yay\srlHYXT_rpu3ez_IV8H9C_AhkMut\result\Fused.ply` | 10.3 MB | `625a4145e071f55a925a3d197403de7a22a5d87a15f79f0d3f75581e9f30dedd` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM01 Bobin.stl` | 23.9 MB | `e9ea4e9a2901073c3fcf02185bde90405d1568003dcc3ce7d08de5db846a3ab9` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM01 Bobin\prHCG_V7ms_tPuE_fGus\result\Mesh.ply` | 12.0 MB | `989f1bb16362e3cf96a7397538dd0a669bcdfc40370f68812536e8ce1a66e37a` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM01 Bobin\sLMUqPH_4mO0Mk_QZacHv_qYFdFx\result\Fused.ply` | 50.8 MB | `674c9ad3228e66d2fc4051bb6cbdc657de2cb15c9ed0d0373e27d2010a935467` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM02 Manyetik Cerceve.stl` | 23.8 MB | `17ff330b1e01d98135db6550d4248f84ccc5168e161f8b4ea19e8a75a1caa9d1` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM02 Manyetik Cerceve\p30SB_T7jO_QhLW_HuT5\result\Mesh.ply` | 12.0 MB | `dd7dd9ac320cb22851e2b3ebb27d3c7826d8a3de3b5ec19bc5692a652696a197` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM02 Manyetik Cerceve\sZiRKYm_VsBawH_oOhgE2_OSG7Yc\result\Fused.ply` | 52.9 MB | `7a75d82d1131dcc89f4380f3dade750839a0839aa61a878a2a7d54ff55787765` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM03 Aki burcu.stl` | 19.1 MB | `fd748e6fc9fe69546f3290448369427efb0c7d0e733d0a452642e897fd8d3aee` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM03 Aki burcu\poWRX_pIPA_aSPx_2LpD\result\Mesh.ply` | 9.6 MB | `fe5f8e40b2edc54d396a4e7b5d2f271a78cad2d5ad21e1503fae55b2c0a0cb05` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-EM03 Aki burcu\srTNIc0_HnN3f9_tG1q4B_hV5h9E\result\Fused.ply` | 16.6 MB | `9b0b1e658321cd7bc58a104162123f33ecd244111bd82bf721634e0742c26eab` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS01 armatur tupu.stl` | 23.9 MB | `cc1d5f63440e8289ced6b969da9391682cbae898f0be28267daa5e1889973f8a` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS01 armatur tupu\pm5Mu_7cSR_1zPH_LK41\result\Mesh.ply` | 12.0 MB | `d2cdb684d09109b8e1d1c830681c82e8bcf0dfeb08016ae297a89c9acf3bf1b9` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS01 armatur tupu\sGfgC9t_rzsnRV_4Mvn7f_kLRO5B\result\Fused.ply` | 21.6 MB | `ac191f454eed508b72eb361532b6755d0d085f5fbbc2287a3c7095234318d091` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS02 Piston silindiri.stl` | 14.0 MB | `a218ae340a2f5323937dbc87e2560f5446d13b7c3e5437ba0864ca7a75be168a` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS02 Piston silindiri\pIlPR_M6oE_ljpX_OXSH\result\Mesh.ply` | 7.0 MB | `1fbb04911a57933a7cb7285ceed0c41f0fe2667bf206f2821f08aa5a8a51b071` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS02 Piston silindiri\sq9fVGJ_XMcCab_BU9Iha_R6urKF\result\Fused.ply` | 7.7 MB | `1ee3dfe40a30eeb3c08c051894eb81febc6cf6b02eb433e53c9c9172e934cc55` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS03 Cikis Flansi.stl` | 25.9 MB | `bbe13fdfcbb1e02cb482d52c7d514ac8b0e826f7425fc83179dc380138cb86a4` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS03 Cikis Flansi\pnY3E_dVjo_lD5h_20JX\result\Mesh.ply` | 13.0 MB | `d96d50fac7cb9ff8c2997ec2bc6686daa3edbfc73da2fee92f9374dafe96e285` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS03 Cikis Flansi\ssODnCK_1Rg0qx_kuvDOV_CCkDvC\result\Fused.ply` | 13.4 MB | `1c8940058e4e36812385f2f00ef1a6553bf06da41893aa0b02d876994e1cbf0d` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS03 Cikis Flansi\svpUU3h_vjgpm6_5vcKSG_Ai7lCo\result\Fused.ply` | 16.3 MB | `b9d9ee148d3b69938d44d4b700bc939b61c81d99a12c393fd61b2cefb62f37ce` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS04 Plastik ara halka.stl` | 14.3 MB | `d2d1ca71217b2ffc122b12e33a4b3f3c4616fc0a9b0e683a7fb5066f2bed8f4f` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS04 Plastik ara halka\psrFa_3bBD_bNr1_B8Qc\result\Mesh.ply` | 7.2 MB | `5f6dabba15e5fb3ef3a6bef550e91f452e85fb7d0ee17bd8f4ee8996c01a3c0d` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS04 Plastik ara halka\seBTi3n_2rJTmp_3TrQP3_2ps8qv\result\Fused.ply` | 19.5 MB | `72a2c1cd530a7cc7088d4f696ecee1995eb211e924130943f43e0ce4b1c05d9b` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS05 Plastik pul + EP5-VL02 Bilya yayi + EP5-VL03 cikis valfi + EP5-VL04.stl` | 17.2 MB | `7a1730d0aed7208c424ae9cd0eb6c595166181a367e96cf0b36b7e11b2bc340f` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS05 Plastik pul + EP5-VL02 Bilya yayi + EP5-VL03 cikis valfi + EP5-VL04\pVE11_xRt9_GT2L_GgiO\result\Mesh.ply` | 8.6 MB | `303668e9e61ead17d75082433d5ac6b7d49a69304b97a69d281ddbf8b37ee23a` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-HS05 Plastik pul + EP5-VL02 Bilya yayi + EP5-VL03 cikis valfi + EP5-VL04\shyL4DH_p9KrpY_Z5PgTO_U1Z8fG\result\Fused.ply` | 9.4 MB | `b1c8f937a005b8bf8e059e05578f84bb017c665029dd8555f868c97537f735e4` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-SL04 Piston O-ringi + EP5-VL01 Piston cek valf + EP5-SL01O-ring + EP5-SL02O-ring + EP5-SL03O-ring.stl` | 23.8 MB | `674d75ff8370a26c84a1f1901c68ee3e6d3b68249c1a41fa326e0efa7739e0ba` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-SL04 Piston O-ringi + EP5-VL01 Piston cek valf + EP5-SL01O-ring + EP5-SL02O-ring + EP5-SL03O-ring\pcK3F_ufvr_6dqn_Wim5\result\Mesh.ply` | 12.0 MB | `4dc8e666957a230f5974ad5eb8fb08f49edf0abcef60218e856f142bc37e28ed` | final/input CAD over project size budget |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-SL04 Piston O-ringi + EP5-VL01 Piston cek valf + EP5-SL01O-ring + EP5-SL02O-ring + EP5-SL03O-ring\sB3WPvI_vhKQJV_gerOqg_UIDkVa\result\Fused.ply` | 30.0 MB | `06e904ed35efb13107dd35ad1c56f7702d71b6c73514a1817c667e5d3913db27` | final/input CAD > 20 MB |
| ulka_pump | `H:\My Drive\Mini Pumps\ulka re\EP5-SL04 Piston O-ringi + EP5-VL01 Piston cek valf + EP5-SL01O-ring + EP5-SL02O-ring + EP5-SL03O-ring\sB3WPvI_vhKQJV_gerOqg_UIDkVa\result\model.ply` | 5.8 MB | `681305701e92b0eb63f715115fc2a53bae2cd6e2bce31156145aad5bcbf3edec` | final/input CAD over project size budget |

## Appendix C: what was left out, by reason (counts and original size)

| Project | Reason | Files | Size |
|---|---|---|---|
| _harness | duplicate content (one copy kept) | 2 | 4 KB |
| _harness | image too large or image budget used | 14 | 7.5 MB |
| _harness | intermediate CAD | 6 | 18.6 MB |
| _harness | other binary/data (.dll) | 2 | 98 KB |
| _harness | other binary/data (noext) | 2 | 0 KB |
| _harness | secret-like filename | 1 | 1 KB |
| chest_ch001 | duplicate content (one copy kept) | 516 | 31.4 MB |
| chest_ch001 | final/input CAD > 20 MB | 26 | 2441.6 MB |
| chest_ch001 | final/input CAD over project size budget | 20 | 180.4 MB |
| chest_ch001 | image too large or image budget used | 4214 | 1701.6 MB |
| chest_ch001 | intermediate CAD | 1442 | 28924.1 MB |
| chest_ch001 | json > 512 KB (data dump) | 27 | 23.5 MB |
| chest_ch001 | large pdf | 1 | 3.2 MB |
| chest_ch001 | other binary/data (.bin) | 4 | 125.0 MB |
| chest_ch001 | other binary/data (.dwg) | 163 | 111.9 MB |
| chest_ch001 | other binary/data (.err) | 2 | 0 KB |
| chest_ch001 | other binary/data (.npy) | 131 | 3889.3 MB |
| chest_ch001 | other binary/data (.npz) | 299 | 5210.8 MB |
| chest_ch001 | other binary/data (.out) | 44 | 310 KB |
| chest_ch001 | other binary/data (.stdout) | 14 | 0 KB |
| chest_ch001 | other binary/data (.zip) | 4 | 751.7 MB |
| chest_ch001 | other binary/data (noext) | 13 | 0 KB |
| chest_ch001 | pdf over size budget | 156 | 74.7 MB |
| dreame_bottom_cover | image too large or image budget used | 31 | 16.3 MB |
| dreame_bottom_cover | intermediate CAD | 7 | 15.7 MB |
| dreame_bottom_cover | other binary/data (.npy) | 20 | 6.0 MB |
| dreame_bottom_cover | other binary/data (.npz) | 10 | 133.8 MB |
| dreame_brush_core | final/input CAD over project size budget | 1 | 18.0 MB |
| dreame_brush_core | image too large or image budget used | 48 | 39.6 MB |
| dreame_brush_core | intermediate CAD | 52 | 665.2 MB |
| dreame_brush_core | other binary/data (.npy) | 3 | 47.0 MB |
| dreame_brush_core | other binary/data (.npz) | 4 | 81.8 MB |
| dreame_dustbin_air_inlet | final/input CAD > 20 MB | 2 | 242.2 MB |
| dreame_dustbin_air_inlet | image too large or image budget used | 7 | 7.5 MB |
| dreame_dustbin_air_inlet | intermediate CAD | 11 | 196.4 MB |
| dreame_dustbin_air_inlet | other binary/data (.npz) | 1 | 313.4 MB |
| left_thigh_clean_rebuild | duplicate content (one copy kept) | 439 | 98.3 MB |
| left_thigh_clean_rebuild | final/input CAD > 20 MB | 12 | 607.6 MB |
| left_thigh_clean_rebuild | final/input CAD over project size budget | 18 | 88.4 MB |
| left_thigh_clean_rebuild | image too large or image budget used | 1342 | 301.6 MB |
| left_thigh_clean_rebuild | intermediate CAD | 336 | 2814.8 MB |
| left_thigh_clean_rebuild | json > 512 KB (data dump) | 8 | 7.1 MB |
| left_thigh_clean_rebuild | other binary/data (.dwg) | 134 | 56.6 MB |
| left_thigh_clean_rebuild | other binary/data (.err) | 6 | 0 KB |
| left_thigh_clean_rebuild | other binary/data (.npy) | 342 | 445.5 MB |
| left_thigh_clean_rebuild | other binary/data (.npz) | 179 | 5899.6 MB |
| left_thigh_clean_rebuild | other binary/data (.pkl) | 3 | 889 KB |
| left_thigh_clean_rebuild | other binary/data (.zip) | 2 | 488.7 MB |
| left_thigh_clean_rebuild | other binary/data (noext) | 4 | 0 KB |
| left_thigh_clean_rebuild | pdf over size budget | 73 | 37.1 MB |
| left_thigh_outer_inner | duplicate content (one copy kept) | 316 | 226.9 MB |
| left_thigh_outer_inner | final/input CAD > 20 MB | 57 | 4604.8 MB |
| left_thigh_outer_inner | final/input CAD over project size budget | 53 | 454.9 MB |
| left_thigh_outer_inner | image too large or image budget used | 2123 | 1401.4 MB |
| left_thigh_outer_inner | intermediate CAD | 544 | 24423.2 MB |
| left_thigh_outer_inner | json > 512 KB (data dump) | 9 | 5.6 MB |
| left_thigh_outer_inner | large pdf | 6 | 51.6 MB |
| left_thigh_outer_inner | other binary/data (.brep) | 1 | 1.1 MB |
| left_thigh_outer_inner | other binary/data (.dwg) | 279 | 106.8 MB |
| left_thigh_outer_inner | other binary/data (.npy) | 76 | 1347.5 MB |
| left_thigh_outer_inner | other binary/data (.npz) | 88 | 1573.4 MB |
| left_thigh_outer_inner | other binary/data (.out) | 7 | 0 KB |
| left_thigh_outer_inner | other binary/data (.vtk) | 1 | 91.9 MB |
| left_thigh_outer_inner | other binary/data (.zip) | 13 | 938.6 MB |
| left_thigh_outer_inner | pdf over size budget | 212 | 93.3 MB |
| lexus_seat_clip | duplicate content (one copy kept) | 40 | 9.8 MB |
| lexus_seat_clip | final/input CAD > 20 MB | 5 | 119.4 MB |
| lexus_seat_clip | image too large or image budget used | 39 | 25.0 MB |
| lexus_seat_clip | intermediate CAD | 11 | 134.9 MB |
| lexus_seat_clip | other binary/data (.dat) | 2 | 3 KB |
| lexus_seat_clip | other binary/data (.npy) | 19 | 75.8 MB |
| lexus_seat_clip | other binary/data (.obmc) | 1 | 660.6 MB |
| lexus_seat_clip | other binary/data (.obp) | 1 | 0 KB |
| lexus_seat_clip | other binary/data (.obproj) | 1 | 24 KB |
| lexus_seat_clip | other binary/data (.obscan) | 1 | 456.3 MB |
| r385_pump | duplicate content (one copy kept) | 363 | 28.4 MB |
| r385_pump | final/input CAD > 20 MB | 10 | 330.1 MB |
| r385_pump | final/input CAD over project size budget | 36 | 392.0 MB |
| r385_pump | image too large or image budget used | 1828 | 1597.6 MB |
| r385_pump | intermediate CAD | 207 | 410.2 MB |
| r385_pump | large pdf | 4 | 27.7 MB |
| r385_pump | large text | 1 | 3.6 MB |
| r385_pump | other binary/data (.allrun) | 6 | 0 KB |
| r385_pump | other binary/data (.allsubset) | 6 | 1 KB |
| r385_pump | other binary/data (.bak) | 3 | 6 KB |
| r385_pump | other binary/data (.blockmesh) | 73 | 333 KB |
| r385_pump | other binary/data (.brep) | 18 | 2.0 MB |
| r385_pump | other binary/data (.c) | 11 | 47 KB |
| r385_pump | other binary/data (.check) | 2 | 238 KB |
| r385_pump | other binary/data (.checkmesh) | 79 | 353 KB |
| r385_pump | other binary/data (.close) | 12 | 60 KB |
| r385_pump | other binary/data (.dat) | 363 | 113.8 MB |
| r385_pump | other binary/data (.decomposepar) | 16 | 75 KB |
| r385_pump | other binary/data (.dep) | 9 | 427 KB |
| r385_pump | other binary/data (.digest) | 56 | 122 KB |
| r385_pump | other binary/data (.emesh) | 3 | 323 KB |
| r385_pump | other binary/data (.extendedfeatureedgemesh) | 3 | 1.1 MB |
| r385_pump | other binary/data (.fields) | 5 | 111 KB |
| r385_pump | other binary/data (.foamtovtk) | 5 | 65 KB |
| r385_pump | other binary/data (.h) | 9 | 42 KB |
| r385_pump | other binary/data (.j2) | 2 | 154 KB |
| r385_pump | other binary/data (.motion) | 2 | 47 KB |
| r385_pump | other binary/data (.movedynamicmesh) | 2 | 2.0 MB |
| r385_pump | other binary/data (.mp4) | 29 | 345.1 MB |
| r385_pump | other binary/data (.npy) | 2 | 3.8 MB |
| r385_pump | other binary/data (.npz) | 55 | 156.6 MB |
| r385_pump | other binary/data (.o) | 9 | 23.4 MB |
| r385_pump | other binary/data (.obmc) | 20 | 4003.8 MB |
| r385_pump | other binary/data (.obp) | 11 | 2 KB |
| r385_pump | other binary/data (.obproj) | 11 | 264 KB |
| r385_pump | other binary/data (.obscan) | 12 | 1310.6 MB |
| r385_pump | other binary/data (.orig) | 5 | 6 KB |
| r385_pump | other binary/data (.pid) | 6 | 0 KB |
| r385_pump | other binary/data (.pimplefoam) | 2 | 13.3 MB |
| r385_pump | other binary/data (.reconstructpar) | 4 | 7 KB |
| r385_pump | other binary/data (.reconstructparmesh) | 1 | 4 KB |
| r385_pump | other binary/data (.renumbermesh) | 6 | 12 KB |
| r385_pump | other binary/data (.safe) | 15 | 17 KB |
| r385_pump | other binary/data (.sections) | 12 | 63 KB |
| r385_pump | other binary/data (.series) | 5 | 6 KB |
| r385_pump | other binary/data (.simplefoam) | 5 | 4.8 MB |
| r385_pump | other binary/data (.smoke) | 12 | 3.4 MB |
| r385_pump | other binary/data (.snappyhexmesh) | 3 | 239 KB |
| r385_pump | other binary/data (.so) | 11 | 14.8 MB |
| r385_pump | other binary/data (.subsetmesh) | 6 | 10 KB |
| r385_pump | other binary/data (.surfacefeatureextract) | 3 | 8 KB |
| r385_pump | other binary/data (.vtm) | 200 | 187 KB |
| r385_pump | other binary/data (.vtp) | 956 | 361.3 MB |
| r385_pump | other binary/data (.vtu) | 100 | 235.1 MB |
| r385_pump | other binary/data (.xlsx) | 2 | 4.7 MB |
| r385_pump | other binary/data (.zip) | 5 | 1241.2 MB |
| r385_pump | other binary/data (noext) | 2270 | 1899.0 MB |
| r385_pump | pdf over size budget | 1 | 2.9 MB |
| ulka_pump | duplicate content (one copy kept) | 64 | 350 KB |
| ulka_pump | final/input CAD > 20 MB | 9 | 276.6 MB |
| ulka_pump | final/input CAD over project size budget | 28 | 322.3 MB |
| ulka_pump | image too large or image budget used | 226 | 75.5 MB |
| ulka_pump | intermediate CAD | 307 | 515.4 MB |
| ulka_pump | large pdf | 1 | 3.1 MB |
| ulka_pump | other binary/data (.dat) | 26 | 33 KB |
| ulka_pump | other binary/data (.j2) | 1 | 36 KB |
| ulka_pump | other binary/data (.mp4) | 30 | 249.1 MB |
| ulka_pump | other binary/data (.npy) | 8 | 10.9 MB |
| ulka_pump | other binary/data (.npz) | 3 | 5.0 MB |
| ulka_pump | other binary/data (.obmc) | 15 | 2118.1 MB |
| ulka_pump | other binary/data (.obp) | 13 | 2 KB |
| ulka_pump | other binary/data (.obproj) | 13 | 312 KB |
| ulka_pump | other binary/data (.obscan) | 16 | 2966.2 MB |
| ulka_pump | other binary/data (.pkl) | 4 | 15.0 MB |
| ulka_pump | other binary/data (.xlsx) | 1 | 1.8 MB |
| ulka_pump | other binary/data (.zip) | 2 | 84.4 MB |
| ulka_pump | pdf over size budget | 1 | 1.7 MB |

Also excluded on purpose: `__pycache__`, `.git`, virtual envs and caches; NX install files; the NX GUI bridge `.dll` binary (its C# source is included); the Hublot watch film-kit project (STL->DXF, not chosen); build123d-only Dreame sessions (no NX); SolidWorks->NX and from-drawing parts (no scans).

## Appendix D: redacted files

| File in zip | What was redacted (count) |
|---|---|
| `_harness/mcp-repo/src/nx_mcp/nx_bridge.py` | token assignment (1) |
| `chest_ch001/transcripts/0ba74d23-fece-4ac7-bbfa-d8a13f52a7e9.jsonl` | email (3) |
| `chest_ch001/transcripts/6db96a5a-7a10-4372-b24e-f1f409ba4256.jsonl` | email (3) |
| `chest_ch001/transcripts/8330b7d3-5c61-4c7f-9dea-7d21232eb168.jsonl` | email (12) |
| `chest_ch001/transcripts/8330b7d3_subagents/agent-a3ed442a6b632cb72.jsonl` | email (3) |
| `chest_ch001/transcripts/8330b7d3_subagents/agent-a4d43a292eaaf5937.jsonl` | email (3) |
| `chest_ch001/transcripts/8330b7d3_subagents/agent-a7033c0c6c6ecbe28.jsonl` | email (3) |
| `chest_ch001/transcripts/8330b7d3_subagents/agent-a81a692c8a16729b1.jsonl` | email (3) |
| `chest_ch001/transcripts/8330b7d3_subagents/agent-a962c3e41b5a56092.jsonl` | email (3) |
| `chest_ch001/transcripts/8330b7d3_subagents/agent-abecf289784105525.jsonl` | email (3) |
| `chest_ch001/transcripts/8330b7d3_subagents/agent-ae6eecf4e194e43fe.jsonl` | email (3) |
| `chest_ch001/transcripts/9c3a8bea-4387-4d6e-ba59-f3194a39fa09.jsonl` | email (3) |
| `chest_ch001/transcripts/c5865595-c8de-4b74-8830-0c775b0d089c.jsonl` | email (3) |
| `chest_ch001/transcripts/d432d364-cec5-4dfa-930b-026d8aa6d8b5.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563-2d16-40ea-98ba-9539917e17e8.jsonl` | email (15) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a32c8a1e0e2bdee88.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a3ed442a6b632cb72.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a4d43a292eaaf5937.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a5beac23e42419635.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a7033c0c6c6ecbe28.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a81a692c8a16729b1.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a91e480b93d2ed465.jsonl` | email (5) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-a962c3e41b5a56092.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-abecf289784105525.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-ad0fe98993a8eec63.jsonl` | email (3) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-adc79fb602e712fb8.jsonl` | email (9) |
| `chest_ch001/transcripts/d9bb7563_subagents/agent-ae6eecf4e194e43fe.jsonl` | email (3) |
| `chest_ch001/transcripts/f204f22c-b209-48a9-8b63-56240f021786.jsonl` | email (3) |
| `chest_ch001/ws/ch_clean/work/s7/measure/b4.py` | email (1) |
| `chest_ch001/ws/ch_clean/work/s7/measure/b5.py` | email (1) |
| `chest_ch001/ws/ch_clean/work/s7/measure/b6.py` | email (1) |
| `dreame_bottom_cover/transcripts/8321884a-def9-457d-bea2-1af9aab9a19b.jsonl` | email (6) |
| `dreame_brush_core/transcripts/00db997d-dec5-46a3-8606-c7e627285bcd.jsonl` | email (2) |
| `dreame_brush_core/transcripts/dd1460f7-90fd-471a-b6b0-87872f6e32f2.jsonl` | email (2) |
| `dreame_dustbin_air_inlet/transcripts/e7db2fb7-ddad-4bed-9a67-a86f3a7848b4.jsonl` | email (2) |
| `dreame_mop_early_nx/transcripts/8d295d90-dd65-45c3-82b9-62f39c1a092f.jsonl` | email (2), flexlm port@host (2) |
| `left_thigh_clean_rebuild/transcripts/19347876-9481-4f4e-a75e-2bc6cabc101a.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/3033883f-e5da-49aa-ba46-0959f5877aec.jsonl` | email (4) |
| `left_thigh_clean_rebuild/transcripts/70a6170f-431d-4fc0-badb-2b1e168f4d7f.jsonl` | email (12) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a0041aff47ce0c215.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a0106b85c7018d2e2.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a1f9995a5aed39338.jsonl` | email (5) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a238c3bedad6c3592.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a3f4779099fc8bf66.jsonl` | email (7) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a4bb719d1bfac111b.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a4d5a2fad8d59856e.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a4fdaaae73467fe3a.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a57c16b73c34e232a.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a59c429d64bbc449f.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a5d35caf06aa5ff17.jsonl` | email (5) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a71c83d601930cb5f.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a748ed694cc3b3530.jsonl` | email (5) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a8533e0a9cca368f3.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a88e863a39fceae05.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a8f17b3695fc6bbc1.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-a9ae09921d8e7b173.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-aa5db575c1cb6bef1.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-aad929d033d65989c.jsonl` | email (4) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ab344e8350c227d9d.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ab42ed3d5133aa6a1.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ab67c709a0a5ddc3b.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-abae97bf9c7754c80.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ac18347f832f8473e.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-ac71346f34d4e9028.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/70a6170f_subagents/agent-afc6285e6fb7ed567.jsonl` | email (3) |
| `left_thigh_clean_rebuild/transcripts/beb3588c-5290-4dc4-bb96-26eae9eebd4c.jsonl` | email (5) |
| `left_thigh_clean_rebuild/ws/lt_clean2/an/m2_q_env.py` | email (1) |
| `left_thigh_clean_rebuild/ws/lt_clean2/an/t5_k.py` | email (2) |
| `left_thigh_clean_rebuild/ws/lt_clean2/an/v5b_m7.py` | email (1) |
| `left_thigh_outer_inner/transcripts/0b84b9d6-468c-4bf1-9825-a9fe39872df6.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/0bc8682e-8d44-448b-9c3f-686fd5afee34.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/0d2c6100-1580-43b6-ae46-f06fbae67218.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/0d2c6100_subagents/agent-a69b35c50e352c28a.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/0d2c6100_subagents/agent-a8527fec524aae6ac.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/0d2c6100_subagents/agent-a9f3fdca69a647d11.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/16b5c31a-0cec-4207-8e7d-60a54256edfb.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/16b5c31a_subagents/agent-aaf75a600e7d1255e.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/31f00b73-005b-4211-8150-b6bb1997b62c.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/3ab8288a-a0ca-44f8-a4cd-379fc50a1d56.jsonl` | email (6) |
| `left_thigh_outer_inner/transcripts/44064e17-92e5-4b7e-96c3-b3147b9c15fb.jsonl` | email (8) |
| `left_thigh_outer_inner/transcripts/573cceaf-803b-47ea-9fd7-d1253614714b.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2-b2fc-467f-b35e-53a9f8822d1b.jsonl` | email (6) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a015b760bf899cd9a.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a17db94dcdc878cdc.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a4d9243bc63901190.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a4e79182b3cd6c571.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a5cadabf215805765.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-a8f49338ffe7f796f.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-aa4084d79b8aa0105.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-ab076834102ef5892.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-ac935ab5a17b45bee.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/59b5e9a2_subagents/agent-ace49ba6f69bf9ea8.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/73a8eec7-2f5f-4c5c-9197-d0335b8bd7e9.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/8df73ba3-5f57-4b8f-9817-3ffd2b7d1b48.jsonl` | email (6) |
| `left_thigh_outer_inner/transcripts/95e57f8d-20aa-48f7-b606-7603564c4149.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/b1cdd1bf-e83d-45d5-b41a-7c77300df7ed.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/cbeb69e1-3925-4bc3-a39e-ca3ccf77ef15.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/ce4111eb-7800-4338-93cc-82432a64c70b.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/efca19c7-6606-43a7-bebe-4b6e6a2431cd.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/f71cbaea-f2f1-42f0-bb9c-9e1f593c2b75.jsonl` | email (3) |
| `left_thigh_outer_inner/transcripts/ff91f392-c6c7-4a37-9c44-40e4960ba29f.jsonl` | email (3) |
| `lexus_seat_clip/transcripts/3d9eaa45-a683-4598-b6b8-8dd4c5d086b2.jsonl` | email (3) |
| `r385_pump/transcripts/0bf7b833-7f88-45b9-bc61-a6dced9c59d4.jsonl` | email (2) |
| `r385_pump/transcripts/24f4f717-b6aa-4139-ac02-ef2070f50638.jsonl` | email (2) |
| `r385_pump/transcripts/522aa477-6fb2-4f96-a095-2abb78cc04f8.jsonl` | email (6) |
| `r385_pump/transcripts/522aa477_subagents/agent-aecef3f37b215ce6d.jsonl` | email (3), key/secret/password assignment (2) |
| `r385_pump/transcripts/9b75049a-d4a4-4500-8f9c-1952a9ea4e9d.jsonl` | email (2) |
| `r385_pump/transcripts/a0755bdb-3cc6-4a03-9189-b5f1abb0c20a.jsonl` | email (2) |
| `r385_pump/transcripts/ab80fb64-1226-4408-9d6d-6f70caddfdf5.jsonl` | email (2) |
| `r385_pump/transcripts/ca5a2a08-3ac3-4d22-a41c-3d0e4a1e8db3.jsonl` | email (2) |
| `r385_pump/transcripts/d3aee339-abd1-49b0-b2ee-f7a321a3a628.jsonl` | email (2) |
| `ulka_pump/transcripts/10ee51b0-aca3-4c97-81e6-1cf43e417574.jsonl` | email (2) |
| `ulka_pump/transcripts/136cb46e-e1f4-4036-8670-cc4f129b1641.jsonl` | email (2) |
| `ulka_pump/transcripts/3b5db2ce-db29-450a-a69e-d5b72703fbb0.jsonl` | email (2) |
| `ulka_pump/transcripts/bcea8ef0-e1c2-446b-a3ac-946c5b1c03a9.jsonl` | email (4) |
| `ulka_pump/transcripts/e4e799fc-342d-4a7b-8226-88448721a5cd.jsonl` | email (2), license-server folder name (2) |
