---
name: stl2step-freecad
description: Reverse engineer a scanned STL mesh into a clean parametric STEP solid using headless FreeCAD (freecadcmd) — Mesh-module cross-sections, datum alignment, primitive fitting, Part-workbench extrude/revolve/common rebuild, optional Reen surface approximation, and a blocking CAD-vs-STL deviation gate via distToShape. Use for STL/scan-to-CAD or mesh-to-parametric tasks when evaluating or using the FreeCAD toolchain instead of build123d.
---

# stl2step-freecad

Same doctrine as [[stl2step-build123d]]: rebuild **design intent**, never wrap triangles; success = a measured **CAD-vs-STL deviation gate**, not eyeballing. This implementation runs headless via `freecadcmd` (FreeCAD 1.1 — exe path in the local-toolchain memory) and leans on FreeCAD's built-ins: the `Mesh` module's native cross-sections, the `Part` workbench b-rep kernel (same OCC as NX-class tools), and `MeshPart` for the final deviation meshing. FreeCAD ships its own Python + numpy — write ONE script, run `freecadcmd script.py`.

## Pipeline (follow in order)

### 1. Mesh intake & hygiene
```python
import Mesh, Part, MeshPart, numpy as np

msh = Mesh.Mesh(stl_path)
msh.harmonizeNormals()
msh.removeDuplicatedPoints()
bb = msh.BoundBox
print("bbox", bb.XLength, bb.YLength, bb.ZLength, "facets", msh.CountFacets)
# units: STL is unitless — if a housing reads 0.05-0.5, it's meters -> msh.transformGeometry(scale 1000)
```
Keep the ORIGINAL mesh for the deviation gate. If `CountFacets` > ~400k make a decimated working copy (`msh.decimate(...)` — check signature on 1.1) but fit dims on the fine mesh where it matters.

### 2. Datum establishment
Fit the primary plane on the largest flat region, align it to XY, origin at a feature intersection (bore axis ∩ base plane) — the NX "plane on a straight face → datum origin" step.
```python
pts = np.array([[p.x, p.y, p.z] for p in msh.Points])
# RANSAC plane: sample facets, plane from 3 pts, count inliers within scan noise (0.05-0.1mm),
# refine by SVD on inliers -> normal n, point c. Then build the aligning placement:
import FreeCAD as App

rot = App.Rotation(App.Vector(*n), App.Vector(0, 0, -1))  # base normal -> -Z
msh.Placement = App.Placement(App.Vector(0, 0, 0), rot).multiply(msh.Placement)
# translate so the base sits on Z=0 and record the TOTAL transform (reuse for the gate)
```
Lock the remaining rotation with a second feature (large bore axis → +Z/+X convention). RECORD the composite transform.

### 3. Segmentation & revolution-axis detection
- Planar regions: `msh.getPlanarSegments(tol)` (Mesh module) or normal clustering in numpy.
- Revolute surfaces: all normals intersect the axis → least-squares axis fit (direction = smallest-eigenvector of `Σ(I − n nᵀ)`, then solve the point). Radius from point-to-axis distances; cone if it trends linearly.
- Freeform leftovers: earmark for §6's `Reen` fallback or loft.

### 4. Section curves — FreeCAD's killer built-in
`Mesh.Mesh.crossSections` slices the mesh with a stack of planes in ONE call and returns clean polyline loops per plane (the per-datum-plane point clouds of the NX method):
```python
base = App.Vector(0, 0, 0)
nrm = App.Vector(0, 0, 1)
planes = [(App.Vector(0, 0, z), nrm) for z in z_stations]
secs = msh.crossSections(planes, 0.0001)  # -> per plane: list of closed point loops
```
Do the same along X and Y for the prismatic tri-axis method; for revolutes, section with half-planes through the fitted axis to get the revolve profile.

### 5. Primitive fitting + design-intent snapping
Fit each loop to lines + arcs (corner split by turning angle; least-squares circle fit in numpy). SNAP to intent — round dims (0.1/0.5/1.0), equalize radii, force concentric/parallel/perpendicular/symmetric, recognize standard sizes (drill Ø, hex A/F). Log every `measured → snapped` pair. Where a profile is genuinely sculpted, approximate with `Part.BSplineCurve()`:
```python
c = Part.BSplineCurve()
c.approximate(Points=loop_pts, DegMax=3, Tolerance=0.05)
```

### 6. Rebuild with the Part workbench
```python
wire = Part.Wire([Part.LineSegment(a, b).toShape(), Part.Arc(p1, pm, p2).toShape(), ...])
face = Part.Face(wire)
solidZ = face.extrude(App.Vector(0, 0, h))
prism = solidZ.common(solidX).common(solidY)  # tri-axis extrude + INTERSECT
rev = profile_face.revolve(axis_pt, axis_dir, 360)  # fitted axis, NOT bbox center
body = prism.fuse(rev)  # or .cut(rev) for trims
```
- Patterns: model ONE boss/hole, replicate with placements (rotate copies about the fitted axis / translate at fitted pitch), then fuse/cut once.
- Fillets LAST: `body.makeFillet(r_meas, edge_list)` with radii measured from sections.
- Freeform patches: `import Reen; surf = Reen.approxSurface(Points=region_pts, ...)` (Reverse Engineering module) → trim into the solid; or loft section wires `Part.makeLoft(wires, True)`. Flag every freeform patch in the report.
- Validate: `body.check()`, `body.isValid()`, single solid, `body.removeSplitter()` to clean coplanar seams.

### 7. DEVIATION GATE (blocking — the "sapma analizi" of the target-quality image)
Two-way distance between the rebuilt b-rep and the ORIGINAL aligned mesh:
```python
# CAD -> scan: sample the rebuilt shape, distance to mesh (KD-tree on mesh points)
cad_mesh = MeshPart.meshFromShape(Shape=body, LinearDeflection=0.05)
from scipy.spatial import cKDTree  # FreeCAD ships scipy; else pure-numpy chunks

d_cad = cKDTree(pts).query(np.array([[p.x, p.y, p.z] for p in cad_mesh.Points]))[0]
# scan -> CAD: exact b-rep distance on a subsample (distToShape is precise but slow — ~2000 pts)
idx = np.random.default_rng(0).choice(len(pts), 2000, replace=False)
d_scan = [Part.Vertex(*pts[i]).distToShape(body)[0] for i in idx]
report(d_scan, d_cad)  # RMS / p95 / max, both directions
```
**PASS bands** (defaults; tighten per project): p95 ≤ 0.15 mm & max ≤ 0.5 mm machined; p95 ≤ 0.3 mm & max ≤ 0.8 mm scanned consumer plastic. Intent-snapping deviation (scanned 8.03 → modeled Ø8.0) is CORRECT — report it, don't chase it. Exclude worn/damaged regions explicitly and note the restoration.

### 8. Deliverables
`body.exportStep(out)` (+ STL via MeshPart); parameter table (measured → snapped); deviation report (RMS/p95/max both ways, exclusions); section-overlay images — plot fitted sketch over section points with matplotlib per [[cad-section]] framing (run plots in system Python if FreeCAD's lacks matplotlib; exchange data as .npy/.csv).

## Traps
- `freecadcmd` runs a bundled Python — system pip packages are NOT visible. numpy ships in; scipy usually; matplotlib often NOT. Split: geometry in freecadcmd, plotting/analysis in system Python via saved arrays.
- `crossSections` returns loops per input plane in input order, but loop ORDER within a plane is arbitrary — match loops across stations by centroid proximity before lofting.
- `distToShape` on thousands of points is slow — subsample (~2k) for the exact direction; the meshed direction covers density.
- **Never derive a revolve axis from a bounding box** — fit it from normals (§3).
- `Part.makeShapeFromMesh(msh.Topology, tol)` + `removeSplitter` is the tessellated last resort — it produces a triangle-faced STEP (NOT the quality target); permitted only for regions everything else failed on, and it must be flagged.
- Heavy meshes on cloud-synced paths: copy to LOCAL scratch first (Drive-streamed H: stalls freecadcmd hard).

## Companions
[[stl2step-build123d]] — same methodology on trimesh+build123d. BAKE-OFF PROTOCOL: run both skills on the SAME benchmark STL with the SAME datum convention, PASS bands, and report format; compare p95/max deviation, wall time, lines-of-code, and failure modes; record the winner + rationale in BAKEOFF.md before committing the project to one tool. [[cad-qa-gate]] runs the loop; [[cad-section]] frames overlays.
