import time
from occlib import *
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.ShapeAnalysis import ShapeAnalysis_FreeBounds
from OCP.TopAbs import TopAbs_EDGE, TopAbs_WIRE
from OCP.BRepCheck import BRepCheck_Analyzer
def report(tag,S):
    so=solids(S); sh=shells(S)
    fb=ShapeAnalysis_FreeBounds(S,1e-6,False,False)
    nfree=len(sub(fb.GetClosedWires(),TopAbs_WIRE,TopoDS.Wire_s))+len(sub(fb.GetOpenWires(),TopAbs_WIRE,TopoDS.Wire_s))
    print(tag,"solids",len(so),"shells",len(sh),"faces",len(faces(S)),"free-boundary wires",nfree,"valid",BRepCheck_Analyzer(S).IsValid(),"bbox",bbox(S),flush=True)
J=solids(read("final_raw.step"))[0]
report("raw",J)
t=time.time(); u=ShapeUpgrade_UnifySameDomain(J,True,True,False); u.SetLinearTolerance(1e-6); u.SetAngularTolerance(1e-6); u.Build(); U=u.Shape()
report("unified(%.0fs)"%(time.time()-t),U)
write(solids(U)[0] if solids(U) else U,"final_unified.step")
