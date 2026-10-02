import sys,time,json,numpy as np
from occlib import *
from kloft import twist_loft
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
def log(*a): print(time.strftime("%H:%M:%S"),*a,flush=True)
z0,z1=-1.0,40.0; KB0=4.25
s,core,C,_=load_parts("in.stp"); ribs=solids(read("ribs_aligned.step")); km=json.load(open("k2d_85.json"))
KB=[TopoDS.Solid_s(k.Reversed()) if vol(k)<0 else k for k in solids(read("Kbase_4.38_6.3.step"))]
box=BRepPrimAPI_MakeBox(gp_Pnt(-40,-40,z0),gp_Pnt(40,40,z1)).Shape()
import os
cur=solids(BRepAlgoAPI_Common(C,box).Shape())[0]; Cb=solids(BRepAlgoAPI_Common(C,box).Shape())[0]
Ks=[]
RESUME=os.path.exists('base_Kmid.step')
if RESUME: cur=solids(read('base_Kmid.step'))[0]; log('resumed Kmid stage vol %.3f'%vol(cur))
for j in ([] if RESUME else range(5)):
    done=False
    for top in [40.0]:
        for step in [5.0,4.0,2.5]:
            a=twist_loft(km["K"][j]["K"],85.0,KB0,top,step)
            if vol(a)<0: a=TopoDS.Solid_s(a.Reversed())
            r=solids(fuse([cur],[a]).Shape()); add=vol(r[0])-vol(cur) if len(r)==1 else -1
            exp=2.9713*(top-KB0)-1.2
            log("K%d top %.1f step %.1f add %.3f exp~%.2f"%(j,top,step,add,exp))
            if len(r)==1 and abs(add-exp)<1.5: cur=r[0]; Ks.append(a); done=True; break
        if done: break
    if not done: log("FAIL K",j); sys.exit(1)

if not RESUME: write(cur,'base_Kmid.step')
KBV=[[TopoDS.Solid_s(k.Reversed()) if vol(k)<0 else k for k in solids(read(f))] for f in ['Kbase_rot.step','Kbase_4.36_6.28.step']]
for j in range(5):
    ok=False
    for vi,KBs in enumerate(KBV):
        for tol in [0.0,1e-4,1e-3]:
            r=solids(fuse([cur],[KBs[j]],tol).Shape()); add=vol(r[0])-vol(cur) if len(r)==1 else -1
            log("Kb%d variant %d tol %g add %.3f solids %d"%(j,vi,tol,add,len(r)))
            if len(r)==1 and 0.8<add<1.5 and len(shells(r[0]))==1: cur=r[0]; ok=True; break
        if ok: break
    if not ok: log("FAIL Kb",j); sys.exit(1)
write(cur,'base_CK.step')
cur=solids(BRepAlgoAPI_Common(cur,box).Shape())[0]; log('cut to box: vol %.3f  (Cb %.3f)'%(vol(cur),vol(Cb)))
Rs=[x for r in ribs for x in solids(BRepAlgoAPI_Common(r,box).Shape())]
for j,R in enumerate(Rs):
    for tol in [0.0,1e-4,1e-3]:
        r=solids(fuse([cur],[R],tol).Shape())
        ok=len(r)==1 and len(shells(r[0]))==1
        log("R%d tol %g solids %d shells %s add %.3f"%(j,tol,len(r),[len(shells(x)) for x in r],vol(r[0])-vol(cur) if r else -1))
        ov=vol(cur)+vol(R)-vol(r[0]) if len(r)==1 else -1
        log("   overlap %.3f (R %.3f)"%(ov,vol(R)))
        if ok and 0<ov<0.5*vol(R): cur=r[0]; break
    else:
        log("FAIL R",j); sys.exit(1)
write(cur,"S_-1_40.step"); log("vol %.3f"%vol(cur))
