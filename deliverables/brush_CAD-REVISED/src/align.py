import numpy as np, math, sys
from occlib import *
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
s,core,C,ribs=load_parts("in.stp")
d=np.array([7.089e-4,-3.785e-4,0.9999997]); d/=np.linalg.norm(d); p0=np.array([-0.00232,0.00039,0.0])
z0=float(sys.argv[1]) if len(sys.argv)>1 else 86.5
piv=p0+d*(z0/d[2])            # point on rib axis at height z0
ax=np.cross(d,[0,0,1]); th=math.asin(np.linalg.norm(ax)); ax/=np.linalg.norm(ax)
T1=gp_Trsf(); T1.SetRotation(gp_Ax1(gp_Pnt(*piv),gp_Dir(*ax)),th)
T2=gp_Trsf(); T2.SetTranslation(gp_Vec(-piv[0],-piv[1],0))
T=T2.Multiplied(T1)
def planes(r):
    out=[]
    for f in faces(r):
        a=BRepAdaptor_Surface(f)
        if a.GetType()==GeomAbs_Plane:
            n=a.Plane().Axis().Direction()
            if abs(n.Z())>0.99:
                g=GProp_GProps(); BRepGProp.SurfaceProperties_s(f,g); c=g.CentreOfMass(); out.append((round(c.Z(),5),round(n.X(),7),round(n.Y(),7)))
    return out
newribs=[TopoDS.Solid_s(BRepBuilderAPI_Transform(r,T,True).Shape()) for r in ribs]
for r in newribs: print(planes(r))
T3=gp_Trsf(); T3.SetTranslation(gp_Vec(0,0,0.00008-0.0000022)); TT=T3.Multiplied(T)
newribs=[TopoDS.Solid_s(BRepBuilderAPI_Transform(r,TT,True).Shape()) for r in ribs]
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
cp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(cp); [bb.Add(cp,r) for r in newribs]
write(cp,"ribs_aligned.step"); print("planes",[planes(r) for r in newribs][0])
import pickle; pickle.dump([[TT.Value(i,j) for j in range(1,5)] for i in range(1,4)],open("T_align.pkl","wb"))
