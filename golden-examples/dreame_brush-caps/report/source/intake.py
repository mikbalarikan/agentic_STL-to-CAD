"""Intake: stats + decimated working copies for both scans."""
import sys, time, json
from pathlib import Path
import numpy as np, trimesh

SRC = Path(r"C:\Users\marya\Downloads\dreame_brush_screw_cap")
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
report = {}
for name in ["dreame_brush_screw_cap", "dreame_brush_snap_cap"]:
    t0 = time.time()
    m = trimesh.load_mesh(SRC / f"{name}.stl", process=True)
    info = {
        "faces": int(len(m.faces)), "verts": int(len(m.vertices)),
        "bounds": m.bounds.tolist(), "extents": m.extents.tolist(),
        "watertight": bool(m.is_watertight), "euler": int(m.euler_number),
        "load_s": round(time.time() - t0, 1),
    }
    if m.is_watertight:
        info["volume"] = float(m.volume)
    # body count
    try:
        parts = m.split(only_watertight=False)
        info["bodies"] = len(parts)
        info["body_faces_top5"] = sorted([int(len(p.faces)) for p in parts], reverse=True)[:5]
    except Exception as e:
        info["split_err"] = str(e)
    # largest planar facets
    try:
        fa = m.facets_area
        order = np.argsort(fa)[::-1][:8]
        info["top_facets"] = [
            {"area": float(fa[i]), "normal": m.facets_normal[i].round(4).tolist(),
             "centroid": m.vertices[m.faces[m.facets[i]]].reshape(-1, 3).mean(axis=0).round(3).tolist()}
            for i in order
        ]
    except Exception as e:
        info["facet_err"] = str(e)
    # save compact working copies
    target = 300_000
    if len(m.faces) > target:
        t1 = time.time()
        w = m.simplify_quadric_decimation(face_count=target)
        info["work_faces"] = int(len(w.faces)); info["decimate_s"] = round(time.time() - t1, 1)
    else:
        w = m
    w.export(OUT / f"{name}_work.stl")
    # also a lighter one for quick plots
    w2 = w.simplify_quadric_decimation(face_count=60_000) if len(w.faces) > 60_000 else w
    w2.export(OUT / f"{name}_lite.stl")
    report[name] = info
    print(name, json.dumps(info, indent=1), flush=True)
(OUT / "intake.json").write_text(json.dumps(report, indent=1))
print("DONE")
