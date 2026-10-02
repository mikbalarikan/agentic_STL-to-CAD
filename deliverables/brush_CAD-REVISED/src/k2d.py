import pickle, numpy as np, sys, json
from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from shapely.validation import make_valid
from shapely.ops import unary_union, nearest_points
from shapely import affinity
d=pickle.load(open(sys.argv[1],"rb")); z=float(sys.argv[2]); STRIP=float(sys.argv[3])
def poly(loops):
    ps=sorted([make_valid(Polygon(l)) for l in loops if len(l)>3],key=lambda p:-p.area)
    P=ps[0]
    for q in ps[1:]: P=P.symmetric_difference(q)
    return P
S=poly(d[z]["C"]); Rs=[poly(L) for L in d[z]["Ra"]]
CL=S.buffer(0.8,join_style=1,resolution=64).buffer(-0.8,join_style=1,resolution=64)
chan=CL.difference(S)
comps=list(chan.geoms) if hasattr(chan,"geoms") else [chan]
out=[]
for j,R in enumerate(Rs):
    ch=max(comps,key=lambda c:c.intersection(R).area)
    # bridge arc = part of CL boundary not on S boundary
    bd=CL.exterior
    pts=np.array(bd.coords)
    on=np.array([S.exterior.distance(Point(p))<1e-4 for p in pts])
    # find run of off-S points adjacent to channel ch
    near=np.array([ch.distance(Point(p))<1e-6 for p in pts])
    idx=np.where((~on)&near)[0]
    arc=pts[idx]
    # endpoints: the arc points farthest apart
    from scipy.spatial.distance import cdist
    D=cdist(arc,arc); a,b=np.unravel_index(D.argmax(),D.shape); A,B=arc[a],arc[b]
    # half plane on channel side
    v=B-A; n=np.array([-v[1],v[0]]); n/=np.linalg.norm(n)
    c=np.array(ch.representative_point().coords[0])
    if (c-A)@n<0: n=-n
    big=50
    H=Polygon([A-v*big, B+v*big, B+v*big+n*big, A-v*big+n*big])
    from shapely.geometry import box
    free=H.intersection(box(-30,-30,30,30)).difference(S)
    fc=list(free.geoms) if hasattr(free,"geoms") else [free]
    chf=max(fc,key=lambda g:g.intersection(R).area)
    ch=chf
    K=chf.buffer(STRIP,join_style=1,resolution=32).intersection(H).intersection(S.union(chf))
    if hasattr(K,"geoms"): K=max(K.geoms,key=lambda g:g.area)
    cover=R.intersection(H).difference(K).area
    out.append(dict(K=np.array(K.exterior.coords).tolist(),A=A.tolist(),B=B.tolist(),
                    area=K.area, chan_below=ch.intersection(H).area, rib_below_uncovered=cover, mouth=float(np.linalg.norm(v))))
    print(j,"K area %.4f chan %.4f mouth %.3f rib-below-chord not covered %.6f"%(K.area,ch.intersection(H).area,np.linalg.norm(v),cover))
json.dump(dict(z=z,K=out),open(sys.argv[4],"w"))
