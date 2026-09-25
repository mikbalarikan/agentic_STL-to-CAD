"""QA step 1 — independent solid validity check on the delivered STEP."""
import json, numpy as np
from build123d import *
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box

P = "/root/projects/oomwoo_b02/scratch/qa/OOM-B02.step"
shape = import_step(P)
print("type:", type(shape))

tds = shape.wrapped

def count(t):
    exp = TopExp_Explorer(tds, t); n = 0
    while exp.More(): n += 1; exp.Next()
    return n

res = {}
res["n_solid"] = count(TopAbs_SOLID)
res["n_shell"] = count(TopAbs_SHELL)
res["n_face"] = count(TopAbs_FACE)
res["n_edge"] = count(TopAbs_EDGE)
res["n_vertex"] = count(TopAbs_VERTEX)

an = BRepCheck_Analyzer(tds)
res["brepcheck_valid"] = bool(an.IsValid())

props = GProp_GProps()
BRepGProp.VolumeProperties_s(tds, props)
res["volume_mm3"] = props.Mass()
com = props.CentreOfMass()
res["com"] = [com.X(), com.Y(), com.Z()]

sprops = GProp_GProps()
BRepGProp.SurfaceProperties_s(tds, sprops)
res["area_mm2"] = sprops.Mass()

bb = Bnd_Box(); BRepBndLib.Add_s(tds, bb)
xm,ym,zm,xM,yM,zM = bb.Get()
res["bbox_min"] = [xm,ym,zm]; res["bbox_max"] = [xM,yM,zM]
res["bbox_size"] = [xM-xm, yM-ym, zM-zm]

# closed shell check
from OCP.BRep import BRep_Tool
exp = TopExp_Explorer(tds, TopAbs_SHELL)
closed = []
while exp.More():
    from OCP.TopoDS import TopoDS
    sh = TopoDS.Shell_s(exp.Current())
    closed.append(bool(sh.Closed()))
    exp.Next()
res["shell_closed_flags"] = closed

# free/naked edges: an edge used by only one face => open
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCP.TopExp import TopExp
m = TopTools_IndexedDataMapOfShapeListOfShape()
TopExp.MapShapesAndAncestors_s(tds, TopAbs_EDGE, TopAbs_FACE, m)
naked = 0
for i in range(1, m.Extent()+1):
    if m.FindFromIndex(i).Extent() < 2:
        naked += 1
res["naked_edges"] = naked

print(json.dumps(res, indent=2))
json.dump(res, open("/root/projects/oomwoo_b02/scratch/qa/_solid.json","w"), indent=2)
