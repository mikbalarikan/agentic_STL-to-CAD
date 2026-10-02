import pickle,json,numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.validation import make_valid
d=pickle.load(open("polys_base.pkl","rb")); z=5.25; STRIP=0.42; RC=7.6222338
def poly(loops):
    ps=sorted([make_valid(Polygon(l)) for l in loops if len(l)>3],key=lambda p:-p.area); P=ps[0]
    for q in ps[1:]: P=P.symmetric_difference(q)
    return P
S=poly(d[z]["C"]); Rs=[poly(L) for L in d[z]["Ra"]]
disk=Point(0,0).buffer(RC+0.6,resolution=256)
free=disk.difference(S); fc=list(free.geoms) if hasattr(free,"geoms") else [free]
out=[]
fig,axs=plt.subplots(1,2,figsize=(16,8))
for j,R in enumerate(Rs):
    G=max(fc,key=lambda g:g.intersection(R).area)
    others=[g for g in fc if not g.equals(G)]
    from shapely.ops import unary_union
    Fo=unary_union(others+[Point(0,0).buffer(30).difference(disk)])  # other free space incl. outside disk
    K=G.buffer(STRIP,join_style=1,resolution=32).intersection(S.union(G)).difference(Fo.buffer(0.1,resolution=32))
    if hasattr(K,"geoms"): K=max(K.geoms,key=lambda g:g.area)
    out.append(dict(K=np.array(K.exterior.coords).tolist(),area=K.area,holes=len(K.interiors)))
    print(j,"G area %.3f K area %.3f holes %d R-uncovered(r<RC) %.5f"%(G.area,K.area,len(K.interiors),R.intersection(Point(0,0).buffer(RC-0.01,resolution=256)).difference(K).area))
    for ax in axs:
        ax.fill(*np.array(K.exterior.coords).T,color="orange",alpha=.5)
for ax in axs:
    for l in d[z]["C"]: ax.plot(l[:,0],l[:,1],"k",lw=.8)
    for L in d[z]["Ra"]:
        for l in L: ax.plot(l[:,0],l[:,1],"b",lw=.8)
    ax.plot(*np.array(Point(0,0).buffer(RC,resolution=256).exterior.coords).T,"g--",lw=.6); ax.set_aspect("equal")
P=np.vstack(d[z]["Ra"][0]); q=P[np.linalg.norm(P,axis=1).argmax()]
axs[1].set_xlim(q[0]-2.5,q[0]+1); axs[1].set_ylim(q[1]-1.5,q[1]+2)
plt.tight_layout(); plt.savefig("kbase.png",dpi=60)
json.dump(dict(z=z,K=out),open("kbase_525b.json","w"))
