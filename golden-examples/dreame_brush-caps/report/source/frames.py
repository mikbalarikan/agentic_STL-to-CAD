"""Export a freshly built body in the datum frame and in the original STL frame (rigid inverse of F00)."""
import json
from pathlib import Path
import numpy as np
from build123d import *
from OCP.gp import gp_Trsf

def stl_frame_location(name: str) -> Location:
    T = np.array(json.load(open(f"{name}_alignment.json"))["matrix_4x4"]); Ti = np.linalg.inv(T)
    U, S, Vt = np.linalg.svd(Ti[:3, :3]); R = U @ Vt
    tr = gp_Trsf(); tr.SetValues(*[float(v) for v in np.c_[R, Ti[:3, 3]].ravel()])
    return Location(tr)

def export_frames(body, name: str, stl_name: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    export_step(body, str(out_dir / f"{stl_name}_datum_frame.step"))
    moved = body.moved(stl_frame_location(name))
    export_step(moved, str(out_dir / f"{stl_name}.step"))
    export_stl(moved, str(out_dir / f"{stl_name}_cad.stl"), tolerance=0.003, angular_tolerance=0.05)
    bb = moved.bounding_box()
    return {"stl_frame_bbox_min": [bb.min.X, bb.min.Y, bb.min.Z], "stl_frame_bbox_max": [bb.max.X, bb.max.Y, bb.max.Z]}
