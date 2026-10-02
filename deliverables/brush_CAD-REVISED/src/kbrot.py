import math
from occlib import *
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
KB=[TopoDS.Solid_s(k.Reversed()) if vol(k)<0 else k for k in solids(read("Kbase_4.38_6.3.step"))]
def ang(s):
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); c=g.CentreOfMass(); return math.atan2(c.Y(),c.X())
a0=ang(KB[0]); out=[KB[0]]
for j in range(1,5):
    d=ang(KB[j])-a0; k=round(d/(2*math.pi/5)); th=k*2*math.pi/5
    T=gp_Trsf(); T.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),th)
    r=TopoDS.Solid_s(BRepBuilderAPI_Transform(KB[0],T,True).Shape())
    print(j,"delta %.4f deg -> rot %d*72; centroid err %.2e deg vol %.4f valid %s"%(math.degrees(d),k,math.degrees(ang(r)-ang(KB[j]))%360 if True else 0,vol(r),valid(r)))
    out.append(r)
cp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(cp); [bb.Add(cp,x) for x in out]; write(cp,"Kbase_rot.step")
