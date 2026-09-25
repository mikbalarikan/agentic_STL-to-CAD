# FreeCAD equivalents (appendix, **untested here**)

Every golden project was built with build123d/OCP. None used FreeCAD
(`analysis/baseline/stl2step-skills.md` §8), and the build123d-vs-FreeCAD bake-off is closed
(`baseline/oomwoo-re-pipeline/RE_SPEC.md:26-27`). This page is for when build123d is
unavailable. **No entry below was run in this repo.** The mappings come from the baseline
FreeCAD skill (`baseline/skills/stl2step-freecad/SKILL.md`, cited as `F:<line>`).

## Invocation

- Run headless: `freecadcmd script.py`. The bundled Python does not see system pip
  packages. numpy ships with it and scipy usually does; matplotlib often does not. Split the
  geometry work from the plotting and exchange `.npy`/`.csv` (F:8, F:94).
- Record the FreeCAD version in `build_log.txt`. The baseline assumed 1.1 and flagged an
  unverified `decimate` signature (F:8, F:23).

## API map (build123d → FreeCAD)

| Job | build123d (this skill) | FreeCAD (unverified) |
|---|---|---|
| Sections | trimesh `section_multiplane` | `Mesh.crossSections(planes, tol)`: loop order arbitrary, match by centroid (F:47-51, F:95) |
| Planar segments | datum scripts in `stl-re-intake-datum` | `getPlanarSegments(tol)` (F:40) |
| Profile → solid | `Face(Wire.make_polygon(...))`, `revolve`, `extrude` | `Part.Wire` / `Part.Face` / `.extrude` / `.revolve` (F:63-68) |
| Booleans | `+ - &` | `.fuse` / `.cut` / `.common` (F:63-68) |
| Fillet | `FilletLog.apply` → `shape.fillet` | `shape.makeFillet(r, edges)` in try/except, logged the same way (F:71) |
| Validity | `validate_step.py` | `shape.check()`, `isValid()`, `removeSplitter()` (F:73) |
| Exact point → B-rep | verify skill | `distToShape`, slow (~2k points) (F:85, F:96) |
| STEP export | `export_frames.py` | `shape.exportStep(path)` (F:91); run `validate_step.py` on the result |

The same rules apply: plan first, params only, logged fillets, dual-frame export (apply
the inverse matrix with an orthonormal rotation), and re-import validation.

## Never carry over

- **`Part.makeShapeFromMesh` / `Reen.approxSurface` as a deliverable.** They produce a
  tessellated or re-tiled scan skin, which is the W01 patchwork that RE_SPEC forbids
  (`RE_SPEC.md:258-273`; F:72, F:98).
- **The vertex-to-vertex deviation gate** (F:82). It is not a surface distance
  (`analysis/SYNTHESIS.md` §3).
- **The revolve axis as the smallest eigenvector of Σ(I − nnᵀ)** (F:41). Wrong: the axis
  is the smallest eigenvector of Σ nnᵀ (`analysis/SYNTHESIS.md` §3).
- **Default mesh repair on the evidence** (F:17-18). Repair a working copy only, and log it.
- **The bake-off protocol** (F:101-102).
