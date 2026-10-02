import sys,time
from occlib import *
def log(*a): print(time.strftime("%H:%M:%S"),*a,flush=True)
files=sys.argv[1:-1]; out=sys.argv[-1]
parts=[solids(read(f))[0] for f in files]
for f,p in zip(files,parts): log(f,"vol %.3f shells %d valid %s"%(vol(p),len(shells(p)),valid(p)))
cur=parts[0]
for f,p in zip(files[1:],parts[1:]):
    ok=False
    for tol in [0.0,1e-5,1e-4]:
        r=solids(fuse([cur],[p],tol).Shape())
        d=(vol(r[0])-vol(cur)-vol(p)) if len(r)==1 else 1e9
        log("join",f,"tol",tol,"solids",len(r),"shells",[len(shells(x)) for x in r],"additivity err %.4f"%d)
        if len(r)==1 and len(shells(r[0]))==1 and abs(d)<3e-5*vol(cur)+0.05: cur=r[0]; ok=True; break
    if not ok: log("FAIL join (keeping result for diagnosis)",f); cur=r[0]
write(cur,out); log("DONE vol %.3f valid %s"%(vol(cur),valid(cur)))
