import sys, numpy as np, pickle
from occlib import *
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.TopAbs import TopAbs_EDGE, TopAbs_WIRE
from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds
from OCP.TopTools import TopTools_HSequenceOfShape
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
def loops(shp,z,defl=0.0005):
    sec=BRepAlgoAPI_Section(shp,gp_Pln(gp_Pnt(0,0,z),gp_Dir(0,0,1))); sec.Build()
    seq=TopTools_HSequenceOfShape()
    for e in sub(sec.Shape(),TopAbs_EDGE,TopoDS.Edge_s): seq.Append(e)
    wires=TopTools_HSequenceOfShape(); ShapeAnalysis_FreeBounds.ConnectEdgesToWires_s(seq,1e-5,False,wires)
    out=[]
    for i in range(1,wires.Length()+1):
        w=TopoDS.Wire_s(wires.Value(i)); pts=[]
        we=BRepTools_WireExplorer(w)
        while we.More():
            e=we.Current(); c=BRepAdaptor_Curve(e)
            qd=GCPnts_QuasiUniformDeflection(c,defl)
            ps=[c.Value(qd.Parameter(k)) for k in range(1,qd.NbPoints()+1)]
            ps=[(p.X(),p.Y()) for p in ps]
            if e.Orientation().name=="TopAbs_REVERSED": ps=ps[::-1]
            pts+=ps[:-1]; we.Next()
        out.append(np.array(pts))
    return out
if __name__=="__main__":
    s,core,C,ribs0=load_parts("in.stp")
    ribsA=solids(read("ribs_aligned.step"))
    res={}
    for z in [float(x) for x in sys.argv[1].split(",")]:
        res[z]={"C":loops(C,z),"Ro":[loops(r,z) for r in ribs0],"Ra":[loops(r,z) for r in ribsA]}
    pickle.dump(res,open(sys.argv[2],"wb"))
