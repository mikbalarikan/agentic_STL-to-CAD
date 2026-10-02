import sys,time,json
from occlib import *
from kloft import twist_loft
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Pnt
def log(*a): print(time.strftime("%H:%M:%S"),*a,flush=True)
part=sys.argv[1]; ZS=150.0
z0,z1,k0,k1=(-1,ZS,4.25,ZS+1.0) if part=="low" else (ZS,180,ZS,168.61)
s,core,C,_=load_parts("in.stp"); ribs=solids(read("ribs_aligned.step")); km=json.load(open("k2d_85.json"))
box=BRepPrimAPI_MakeBox(gp_Pnt(-40,-40,z0),gp_Pnt(40,40,z1)).Shape()
cur=C if part=="low" else solids(BRepAlgoAPI_Common(C,box).Shape())[0]
log(part,"C part %.3f"%vol(cur))
expK=2.9713*(k1-k0)
for j in range(5):
    done=False
    for step in [5.0,4.0,6.0,3.0]:
        a=twist_loft(km["K"][j]["K"],85.0,k0,k1,step)
        if vol(a)<0: a=TopoDS.Solid_s(a.Reversed())
        t=time.time(); r=solids(fuse([cur],[a]).Shape())
        add=vol(r[0])-vol(cur) if len(r)==1 else -1
        log(part,"K%d step %.0f add %.3f exp~%.1f (%.0fs)"%(j,step,add,expK,time.time()-t))
        if len(r)==1 and abs(add-expK)<0.03*expK+2: cur=r[0]; done=True; break
    if not done: log("FAIL K",j); sys.exit(1)
if part=="low":
    cur=solids(BRepAlgoAPI_Common(cur,box).Shape())[0]; log("low cut at 150: vol %.3f (C_low %.3f, exp add %.1f)"%(vol(cur),vol(solids(BRepAlgoAPI_Common(C,box).Shape())[0]),5*2.9713*(ZS-k0)))
    k1=ZS
write(cur,f"CK_{part}.step")
Rs=[x for r in ribs for x in solids(BRepAlgoAPI_Common(r,box).Shape())]
for j,R in enumerate(Rs):
    t=time.time(); r=solids(fuse([cur],[R]).Shape())
    ok=len(r)==1 and len(shells(r[0]))==1
    ov=vol(cur)+vol(R)-vol(r[0]) if len(r)==1 else -1
    log(part,"R%d vol %.3f add %.3f overlap %.3f per-mm %.3f solids %d (%.0fs)"%(j,vol(R),vol(r[0])-vol(cur) if r else -1,ov,ov/(k1-k0),len(r),time.time()-t))
    if not ok or not (1.5<ov/(k1-k0)<4.5): log("FAIL R",j); sys.exit(1)
    cur=r[0]
write(cur,f"T_{part}.step"); log(part,"DONE vol %.3f valid %s"%(vol(cur),valid(cur)))
