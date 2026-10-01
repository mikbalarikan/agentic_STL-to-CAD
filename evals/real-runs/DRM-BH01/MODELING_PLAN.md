# MODELING PLAN: dreame_brushes_housing  (iteration it2 of 3; it1 in _it1_SUPERSEDED/, verdict REVISE)

## 0. Build deviations
| Item | Planned | Built | Why | Declared |
|---|---|---|---|---|
| Fillets / chamfers | none planned as separate ops | none | moulded blends left sharp; a few chamfers exist as measured prism faces in region features | yes (fillets.json: empty) |
| Detached pieces | every feature attached | 15 small detached pieces dropped (largest 100 mm³, total ≈300 mm³), listed in build_log.txt | rib/boss primitives whose measured extents do not touch the body | yes, build_log.txt |
| Enclosed cavities | none | 3 internal void shells filled (x≈11.8, R1 back-face pockets sealed by R2 material) | single-shell solid required by export_frames | yes, build_log.txt |
| Slab/tab connection | — | rib slabs below the troughs extended 3 mm up (trough voids re-cut afterwards); -Y tab roots extended 0.5 mm into the upstand | measured patches stop at the root blend | yes, params `slab_top_extension` (assumed), make_params.py |
| R2 band cut | polygon bands (region agent v1) | exact cylinder "diff" | avoid faceted (patchwork) outer surfaces | yes, region_generators/R2_gen.py |
| R3 motor end trim | plain cut | diff (trim minus boss) | plain cut detached the boss | yes, region_generators/orchestrator_patch.py (folded into R3_build.py in it2) |
| it2: validity | it1 STEP: 2 non-manifold edges at the +X window/latch area | R4 features overlap/separate by >= 0.05 mm; 0 non-manifold edges | it1 verify REVISE | yes |
| it2: face division | — | faces > 1500 mm2 split (ShapeUpgrade_ShapeDivideArea + ShapeFix), 1832 -> 1873 faces, same geometry | the 6,476 mm2 T2 outer cylinder triangulated with holes in the datum frame | yes, build_log.txt |
| it2: region fixes | — | R1 sockets/back pockets, R2 trough-start walls + clip box, R3 brackets + motor end/groove, R4 end floor/wall + corner | verifier clusters 0,1,2,4,6,7,8,10,11 | yes, measure/REGION_R*.md "Iteration 2" |

## 1. Strategy summary
Thin-walled moulded tray (two half-bore troughs) + gearbox block + motor can, scanned as one assembly; delivered as one
fused solid (DECISIONS PART-CLASS). Dominant silhouette = the constant YZ cross-section (lines + measured circles),
extruded along x per trough group, each group placed on its measured axis line (warp declared). The gearbox block is
a fitted YZ sketch (lines + arcs) extruded and cut by the measured end-face plane; the motor is stepped x-cylinders;
the +X end uses measured drafted planes. Everything else is measured add/cut primitives (boxes, cylinders, few-vertex
prisms) per region R1–R5 with their own scripts and reports (measure/REGION_R*.md).

## 2. Expectations (reported, not gated)
Ops ≈ 30 base + 133 slabs + 185 region features. Face count 1,200–2,000 (built 1,873 after face division). Surface types: planes and
cylinders only (built it2: 1,714 planes / 159 cylinders, analytic share 1.0, ruled_like 0). The high plane count comes
from ribs, slabs, the 150-edge gearbox outline and region prisms — not from faceting a curved face (the only curved
surfaces in the part are modelled as true cylinders; the gearbox outline arcs are true arcs).

## 3. Ordered feature list
| F## | Operation | Driving params (params.json / geometry.json) | Acceptance |
|---|---|---|---|
| F01 | T1 shell: x-cylinders R t1_ro − t1_ri, top cut at py_top | t1_ri, t1_ro, t1_line | 1 solid |
| F02 | T1 offset strip (R t1_rec_ri/ro) on −y side of the step plane | t1_rec_ri/ro, rec_y0, rec_slope | |
| F03 | T2 shell, rounded pocket end | t2_ri/ro, t2_cy/cz, t2_line, xend | |
| F04 | +Y flange + lip (YZ polygon of measured flats) | py_* | |
| F05 | −Y labyrinth edge (YZ polygon of measured flats) | my_* | |
| F05b | ridge cut, +X drafted end planes, ridge end, window | ridge_top_z, end_*_plane, window, xend | |
| F06 | gearbox block sketch + end-face plane | gearbox_outline, endface_plane, x0 | |
| F08 | motor can cylinders | motor_cy/cz, motor_segments | |
| F10 | end plate, boxes, top-view corners, tabs, flange holes/slots | xend, corner_*_r, tabs, flange_holes/slots | |
| F09 | planar rib slabs | slabs, slab_top_extension | |
| R1–R5 | region add/cut primitives (adds, then cuts clipped to the region box) | features_R1..R5 | region reports |

## 4. Intake feature map (CHK-ENUM)
F01 T1 → F01/F02; F02 T2 → F03 (+R4 end); F03 ridge → F05b/R4; F04 +Y flange → F04/F10/R5; F05 −Y edge → F05/R5;
F06 gearbox → F06/R1; F07 trough start → R2; F08 motor → F08/R3; F09 underside → F09/R3; F10 +X end → F05b/F10/R4;
F11 wires → out of scope (non-rigid, declared).

## 5. Fillet plan
None (sharp blends; their deviation is part of the gate numbers).

## 6. Unscanned or invented geometry
| Item | Value | Source tag | Why |
|---|---|---|---|
| slab top extension | 3 mm | assumed | attach ribs to the trough wall |
| −Y tab root extension | 0.5 mm into the upstand | assumed | attach tabs |
| filled enclosed cavities | 3 small voids at x≈11.8 | assumed | single shell |
| gearbox/motor interiors | solid | assumed | scanned as closed outer skins |
