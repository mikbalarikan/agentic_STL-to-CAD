---
name: stl2step-build123d
description: Reverse engineer a scanned STL mesh into a clean parametric STEP solid using trimesh (mesh analysis) + build123d (rebuild) — datum-plane alignment, section-curve extraction, primitive fitting, tri-axis extrude-intersect, revolve-axis detection, and a blocking CAD-vs-STL deviation gate. Use for any STL/scan-to-CAD, mesh-to-parametric, or scan-based spare-part remodeling task where the deliverable is design-intent CAD, not a surface wrap.
---

# stl2step-build123d

Rebuild **design intent**, don't wrap triangles. A scanned STL is a noisy, discrete record of an engineered part; the deliverable is the clean parametric solid the original designer intended. The workflow mirrors the proven NX manual method (datum from a flat face → section point clouds per datum plane → fitted sketches → extrude/intersect or revolve/trim), automated with `trimesh` + `numpy` for analysis and `build123d` for the rebuild. **Success is measured, not judged: the rebuilt CAD must pass a CAD-vs-STL deviation gate** (the "sapma analizi" step).

## Pipeline (follow in order)

### 1. Mesh intake & hygiene
```python
import trimesh, numpy as np

m = trimesh.load_mesh(stl_path)
# units sanity: a vacuum housing should be ~50-500mm; if bbox ~0.05-0.5, it's meters -> x1000
print("bbox", m.bounds, "watertight", m.is_watertight, "faces", len(m.faces))
work = m.simplify_quadric_decimation(int(len(m.faces) * 0.2)) if len(m.faces) > 400_000 else m
```
Keep the ORIGINAL mesh for the deviation gate; decimate only the working copy. Scan meshes are often not watertight — that's fine for sectioning/fitting; do not "repair" away real geometry.

### 2. Datum establishment (the part's coordinate system)
Fit a plane to the largest flat region → that's the primary datum (align to XY). Lock rotation with a second feature (large cylinder axis or second plane); set origin at a feature intersection (e.g. bore axis ∩ base plane).
```python
# facets = coplanar face patches trimesh already found
i_big = int(np.argmax(m.facets_area))
n = m.facets_normal[i_big]
p = m.vertices[m.facets[i_big]].reshape(-1, 3).mean(axis=0)
T = trimesh.geometry.align_vectors(n, [0, 0, -1])  # base normal -> -Z (base on floor)
work.apply_transform(T)
work.apply_translation([0, 0, -work.bounds[0][2]])
```
Refine with RANSAC (sample facet triangles, fit plane, keep max inliers at tol≈scan noise, e.g. 0.05–0.1 mm) when the flat is noisy. Record the full transform — apply the SAME transform to the original mesh for the final deviation check.

### 3. Segmentation & revolution-axis detection
Classify regions before choosing rebuild strategies:
- **Planes**: facet normal clusters (already in `m.facets`).
- **Cylinders/cones (revolve surfaces)**: all surface normals of a revolute intersect its axis. Fit the axis by least squares: for points `p_i` with normals `n_i`, the axis (point `a`, direction `d`) minimizes distance to all lines `(p_i, n_i)`. `d` ≈ eigenvector of smallest eigenvalue of `Σ(I − n_i n_iᵀ)`; then solve `a` linearly. Radius = mean distance of points to axis; cone if radius varies linearly along axis.
- **Freeform**: what's left (blends, styled surfaces) — handled last by loft or left to fillets.

### 4. Section curves (the heart — matches the NX datum-plane method)
```python
zs = np.linspace(z0, z1, n_stations)  # denser where geometry changes
sections = work.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=zs)
# each section: Path2D -> .discrete = list of polyline point arrays (the "point clouds per plane")
```
Slice along ALL THREE axes for prismatic parts (X, Y, Z stacks) — these become the three sketches for extrude-intersect. For a revolute region, slice with HALF-PLANES through the fitted axis to get the revolve profile.

### 5. Primitive fitting + design-intent snapping (what makes it CAD, not tracing)
Fit each section polyline to lines + arcs/circles (least-squares circle: Kåsa/Taubin fit; corner detection by turning angle). Then SNAP to intent:
- Round dimensions to sensible steps (0.1 / 0.5 / 1.0 mm) when within scan noise.
- Snap near-equal radii equal, near-concentric circles concentric, near-parallel/perpendicular lines exactly so, near-symmetric profiles symmetric about the datum.
- Recognize standards: hole Ø → drill/thread sizes, hex A/F, common fillets. A scanned 8.03 mm hole IS Ø8.0 (or Ø8 H7). Record every snap in the report (measured → chosen).

### 6. Rebuild in build123d (strategy per region)
```python
from build123d import *

with BuildPart() as part:
    with BuildSketch(Plane.XY):  # fitted primitives, not raw points
        with BuildLine():
            Line((x0, y0), (x1, y1))
            RadiusArc((x1, y1), (x2, y2), r_snap)  # ...
        make_face()
    extrude(amount=h)
```
- **Prismatic**: 3 sketches (from the 3 section stacks) → 3 extrudes → boolean **intersect** (`&`) — the tri-axis NX trick.
- **Revolute**: fitted half-profile → `revolve(axis=fitted_axis)` → boolean union/cut with the prismatic body (revolve-then-trim).
- **Pattern features**: detect repeated bosses/holes (equal radius, equal angular/linear pitch) → model ONE + `PolarLocations`/`GridLocations`. Never model pattern instances individually.
- **Fillets/chamfers LAST**, radii measured from sections; leave tiny scan-noise blends out unless functional.
- Freeform patches that resist everything: `loft()` through section curves; flag them in the report.

### 7. DEVIATION GATE (blocking — this is the quality bar)
Compare the rebuilt solid against the ORIGINAL (undecimated, datum-aligned) mesh, two-way:
```python
part.part.export_stl(tmp_stl)  # or export_step + mesh it
rebuilt = trimesh.load_mesh(tmp_stl)
d1 = trimesh.proximity.closest_point(rebuilt, m.vertices)[1]  # scan -> CAD
d2 = trimesh.proximity.closest_point(m, rebuilt.sample(20000))[1]  # CAD -> scan
for name, d in [("scan->CAD", d1), ("CAD->scan", d2)]:
    print(
        name,
        "RMS %.3f  p95 %.3f  max %.3f" % (np.sqrt((d**2).mean()), np.percentile(d, 95), d.max()),
    )
```
**PASS bands** (default; tighten per project): p95 ≤ 0.15 mm and max ≤ 0.5 mm for machined parts; p95 ≤ 0.3 mm, max ≤ 0.8 mm for scanned consumer plastics (scan noise + intent-snapping legitimately deviate from the scan — a snapped Ø8.0 vs scanned 8.03 is CORRECT deviation; report it, don't chase it). Worn/damaged zones: exclude by region and note the restoration.

### 8. Deliverables
STEP (+ STL) of the rebuilt solid; a parameter table (every fitted dim: measured → snapped); the deviation report (RMS/p95/max both ways + per-region notes); section overlay images (fitted sketch ON the section point cloud — visual proof, use [[cad-section]] framing rules).

## Traps
- **Don't fit sketches to raw vertices of one slice** — slice position noise biases dims; average 2–3 nearby stations or fit on the densest station and verify on neighbors.
- **Extrude-intersect over-cuts** concave prismatic parts (intersection can only remove) — decompose into sub-bodies + union, or add back bosses after.
- **Revolve axis from bbox center is WRONG** — always fit from normals (§3); bbox center ≠ functional axis.
- **Units**: STL has none. Verify against a caliper-known dimension when available.
- `trimesh.proximity` needs `rtree`; fall back to `scipy.spatial.cKDTree` on vertices (approximate but adequate for the gate).
- Heavy meshes on cloud-synced paths: copy to LOCAL scratch first (Drive-streamed H: stalls).

## Companions
[[stl2step-freecad]] — same methodology, FreeCAD implementation; run BOTH on the shared benchmark (identical input + PASS bands + report format) and compare deviation stats, wall time, and failure modes to pick the project tool. [[cad-qa-gate]] runs the loop; [[cad-section]] frames the overlays.
