import json,sys,numpy as np
from OCP.gp import gp_Vec, gp_Ax2, gp_Pnt, gp_Dir
from occlib import *
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from shapely.geometry import Polygon
def wire_from_poly(coords,z):
    P=Polygon(coords).simplify(0.002)
    mp=BRepBuilderAPI_MakePolygon()
    for x,y in list(P.exterior.coords)[:-1]: mp.Add(gp_Pnt(x,y,z))
    mp.Close(); return mp.Wire()
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
RC=7.6222338; Z0,Z1=float(sys.argv[1]),float(sys.argv[2])
kb=json.load(open(sys.argv[3] if len(sys.argv)>3 else "kbase_525.json"))
cyl=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,3.0),gp_Dir(0,0,1)),RC,5.0).Shape()
out=[]
for j,e in enumerate(kb["K"]):
    w=wire_from_poly(e["K"],Z0)
    f=BRepBuilderAPI_MakeFace(w,True).Face()
    pr=BRepPrimAPI_MakePrism(f,gp_Vec(0,0,Z1-Z0)).Shape(); p=solids(pr)[0]
    if vol(p)<0: p=TopoDS.Solid_s(p.Reversed())
    c=solids(BRepAlgoAPI_Common(p,cyl).Shape())
    print(j,"prism %.3f (area*h %.3f) capped %s valid %s"%(vol(p),e["area"]*(Z1-Z0),[round(vol(x),3) for x in c],valid(c[0]) if c else None),flush=True)
    out.append(c[0])
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
cp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(cp); [bb.Add(cp,x) for x in out]; write(cp,f"Kbase_{Z0}_{Z1}.step")
