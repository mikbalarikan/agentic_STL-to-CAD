import json, numpy as np, math, sys
from occlib import *
from OCP.TColgp import TColgp_Array1OfPnt
from OCP.GeomAPI import GeomAPI_PointsToBSpline
from OCP.GeomAbs import GeomAbs_C2
from OCP.gp import gp_Pnt, gp_Trsf, gp_Ax1, gp_Dir, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_Transform, BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from shapely.geometry import Polygon
RATE=math.radians(1.10229)   # CCW per mm
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.TColgp import TColgp_HArray1OfPnt
def wire_from_poly(coords, zref, mode="bspline", n=360, rr=0.03):
    P=Polygon(coords).buffer(-rr,join_style=1,resolution=16).buffer(rr,join_style=1,resolution=16)
    ring=P.exterior
    L=ring.length; xy=np.array([ring.interpolate(t).coords[0] for t in np.linspace(0,L,n,endpoint=False)])
    arr=TColgp_HArray1OfPnt(1,n)
    for i,(x,y) in enumerate(xy): arr.SetValue(i+1,gp_Pnt(x,y,zref))
    it=GeomAPI_Interpolate(arr,True,1e-7); it.Perform()
    e=BRepBuilderAPI_MakeEdge(it.Curve()).Edge()
    return BRepBuilderAPI_MakeWire(e).Wire()
def twist_loft(coords,zref,z0,z1,step=5.0):
    w0=wire_from_poly(coords,0.0)
    zs=np.linspace(z0,z1,int(math.ceil((z1-z0)/step))+1)
    ts=BRepOffsetAPI_ThruSections(True,False,1e-6)
    for z in zs:
        T=gp_Trsf(); T.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),RATE*(z-zref))
        T2=gp_Trsf(); T2.SetTranslation(gp_Vec(0,0,z)); 
        w=TopoDS.Wire_s(BRepBuilderAPI_Transform(w0,T2.Multiplied(T),True).Shape()); ts.AddWire(w)
    ts.CheckCompatibility(False); ts.Build()
    return TopoDS.Solid_s(solids(ts.Shape())[0])
if __name__=="__main__":
    k=json.load(open(sys.argv[1])); z0,z1=float(sys.argv[2]),float(sys.argv[3])
    from OCP.TopoDS import TopoDS_Compound
    from OCP.BRep import BRep_Builder
    cp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(cp)
    for e in k["K"]:
        so=twist_loft(e["K"],k["z"],z0,z1); print("K vol %.3f valid %s faces %d"%(vol(so),valid(so),len(faces(so))),flush=True); bb.Add(cp,so)
    write(cp,sys.argv[4])
