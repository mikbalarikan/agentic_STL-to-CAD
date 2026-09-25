# Independent QA Verdict — M02-02-03_CORRECTED

**Gate status: PASS**

Frozen STEP: `/home/oguz/work/re/M02-02-03_CORRECTED/02_model/M02-02-03_CORRECTED.step`  
SHA-256 before and after QA: `457aa5d9fb68f454b63cf51415f235566f4f5e99853f80a1fa973271283449ac` / `457aa5d9fb68f454b63cf51415f235566f4f5e99853f80a1fa973271283449ac` (expected `457aa5d9fb68f454b63cf51415f235566f4f5e99853f80a1fa973271283449ac`)

| Mandatory gate | Measured | Status |
|---|---:|:---:|
| STEP readable / BRepCheck valid | true / true | PASS |
| Solids / shells / shell closed | 1 / 1 / true | PASS |
| Positive BREP volume | 1265.524954 mm³ | PASS |
| STEP re-tessellation | 0.010 mm linear deflection | PASS |
| Mesh watertight / components / boundary / non-manifold edges | true / 1 / 0 / 0 | PASS |
| Big gear count / OD / width | 30 T / 19.049997 mm / 3.000000 mm | PASS |
| Small gear count / OD / width | 17 T / 11.199999 mm / 6.950000 mm | PASS |
| Analytic bore diameter | 1.950000 mm | PASS |
| Overall Z | 9.950000 mm | PASS |
| Big / small maximum measured twist | 6.661e-16° / 1.332e-15° | PASS |
| Visual exposure / cropping / readability | inspected, no defects | PASS |

## Selector notes

- Measurements are from the exact disk STEP after independent OCP re-import; no source constants or filename semantics were used as measurements.
- Tooth counts use the maximal qualified rotational order of the isolated outer contour at three strictly interior stations per gear. The contour is selected by largest closed-section area; bore/core loops are excluded before 10,200 center-out rays. Full candidate-order residual tables are preserved in `qa_report.json`; crest peak counts are diagnostic only.
- Zero twist uses circular registration of those outer-contour radial signatures across all three stations in each axial band.
- Widths and overall Z use exact `BRepBndLib.AddOptimal_s` extrema and the independently selected interior Z-normal shoulder at Z=3.0 mm.
- Bore diameter uses the selected analytic Z-axis cylindrical STEP face (face index 1501).

Claim boundary: PASS establishes the listed local exported-artifact geometry, topology, mesh, dimensions, periodic counts, zero-twist, and visual-evidence gates only.
