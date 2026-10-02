import sys,time,json
from occlib import *
from kloft import twist_loft
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Pnt
def log(*a): print(time.strftime("%H:%M:%S"),*a,flush=True)
s,core,C,_=load_parts("in.stp"); ribs=solids(read("ribs_aligned.step")); km=json.load(open("k2d_85.json"))
KBOT,KTOP=4.25,168.61
def build(z0,z1,depth=0):
    tag=f"{z0:g}_{z1:g}"
    box=BRepPrimAPI_MakeBox(gp_Pnt(-40,-40,z0),gp_Pnt(40,40,z1)).Shape()
    cur=solids(BRepAlgoAPI_Common(C,box).Shape())[0]; c0=vol(cur)
    k0,k1=max(z0,KBOT),min(z1,KTOP); expK=2.9713*(k1-k0)
    for j in range(5):
        ok=False
        for step in [5.0,4.0,3.0]:
            a=twist_loft(km["K"][j]["K"],85.0,k0,k1,step)
            if vol(a)<0: a=TopoDS.Solid_s(a.Reversed())
            r=solids(fuse([cur],[a]).Shape()); add=vol(r[0])-vol(cur) if len(r)==1 else -1
            # in the base slab the part of K under z=4.5 overlaps the disk: allow small deficit
            tolr=0.03*expK+2+(1.0 if k0<4.6 else 0)
            log(tag,"K%d step %.0f add %.3f exp~%.2f"%(j,step,add,expK))
            if len(r)==1 and abs(add-expK)<tolr: cur=r[0]; ok=True; break
        if not ok:
            if depth>=3 or z1-z0<6: log("FAIL",tag); sys.exit(1)
            m=round((z0+z1)/2,1)+0.37; log(tag,"split at",m)
            return build(z0,m,depth+1)+build(m,z1,depth+1)
    Rs=[x for r in ribs for x in solids(BRepAlgoAPI_Common(r,box).Shape())]
    for j,R in enumerate(Rs):
        r=solids(fuse([cur],[R]).Shape())
        ov=vol(cur)+vol(R)-vol(r[0]) if len(r)==1 else -1
        log(tag,"R%d overlap/mm %.3f solids %d shells %s"%(j,ov/(k1-k0),len(r),[len(shells(x)) for x in r]))
        if len(r)!=1 or len(shells(r[0]))!=1 or not (1.0<ov/(k1-k0)<4.5):
            if depth>=3 or z1-z0<6: log("FAIL R",tag); sys.exit(1)
            m=round((z0+z1)/2,1)+0.37; log(tag,"split at",m)
            return build(z0,m,depth+1)+build(m,z1,depth+1)
        cur=r[0]
    write(cur,f"S_{tag}.step"); log(tag,"OK vol %.3f"%vol(cur)); return [(z0,z1)]
z0,z1=float(sys.argv[1]),float(sys.argv[2])
log("RESULT",build(z0,z1))
