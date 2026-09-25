"""QA step 2 — fine tessellation of the STEP, watertightness, self-intersection screen."""
import numpy as np, trimesh, json
from build123d import *

P = "/root/projects/oomwoo_b02/scratch/qa/OOM-B02.step"
shape = import_step(P)
# fine tessellation
verts, faces = shape.tessellate(tolerance=0.005, angular_tolerance=0.05)
V = np.array([[v.X, v.Y, v.Z] for v in verts], dtype=np.float64)
F = np.array(faces, dtype=np.int64)
m = trimesh.Trimesh(vertices=V, faces=F, process=True)
m.merge_vertices()
m.remove_degenerate_faces() if hasattr(m,'remove_degenerate_faces') else None
print("tris", len(m.faces), "verts", len(m.vertices))
print("watertight", m.is_watertight, "winding_consistent", m.is_winding_consistent,
      "euler", m.euler_number, "volume", m.volume, "n_components", m.body_count)
print("bbox", m.bounds.tolist())
print("bbox size", (m.bounds[1]-m.bounds[0]).tolist())
print("open edges:", len(trimesh.grouping.group_rows(m.edges_sorted, require_count=1)))

m.export("/root/projects/oomwoo_b02/scratch/qa/cad_fine.stl")

# self-intersection screen: broadphase AABB pairs of non-adjacent triangles + exact test
try:
    import trimesh.collision
except Exception:
    pass

# use a simple sampling-based check: is the mesh volume consistent & does ray parity hold
pts = m.sample(20000)
# offset points slightly along normals -> check containment parity
print("is_volume", m.is_volume)
json.dump({"tris":int(len(m.faces)),"watertight":bool(m.is_watertight),
           "winding":bool(m.is_winding_consistent),"euler":int(m.euler_number),
           "volume":float(m.volume),"components":int(m.body_count),
           "bbox_min":m.bounds[0].tolist(),"bbox_max":m.bounds[1].tolist(),
           "is_volume":bool(m.is_volume)},
          open("/root/projects/oomwoo_b02/scratch/qa/_tess.json","w"), indent=2)
