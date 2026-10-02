from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.TopTools import TopTools_ListOfShape
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepLib import BRepLib
def sub(s,T,cast):
    out=[];e=TopExp_Explorer(s,T)
    while e.More(): out.append(cast(e.Current())); e.Next()
    return out
solids=lambda s: sub(s,TopAbs_SOLID,TopoDS.Solid_s)
shells=lambda s: sub(s,TopAbs_SHELL,TopoDS.Shell_s)
faces=lambda s: sub(s,TopAbs_FACE,TopoDS.Face_s)
def vol_fast(s): g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
def vol(s, eps=1e-6):
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g,eps,False); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def bbox(s):
    b=Bnd_Box(); BRepBndLib.Add_s(s,b); p,q=b.CornerMin(),b.CornerMax(); return [round(v,3) for v in (p.X(),p.Y(),p.Z(),q.X(),q.Y(),q.Z())]
def read(fn):
    r=STEPControl_Reader(); r.ReadFile(fn); r.TransferRoots(); return r.OneShape()
def write(s,fn):
    w=STEPControl_Writer(); w.Transfer(s,STEPControl_AsIs); return w.Write(fn)
def mksolid(sh):
    so=BRepBuilderAPI_MakeSolid(sh).Solid()
    if vol(so)<0: so=TopoDS.Solid_s(so.Reversed())
    return so
def fuse(args,tools,tol=0.0,glue=None):
    a=TopTools_ListOfShape(); [a.Append(x) for x in args]; t=TopTools_ListOfShape(); [t.Append(x) for x in tools]
    op=BRepAlgoAPI_Fuse(); op.SetArguments(a); op.SetTools(t)
    if tol: op.SetFuzzyValue(tol)
    if glue is not None: op.SetGlue(glue)
    op.SetRunParallel(False); op.Build()
    return op
def load_parts(fn):
    s=read(fn); sol=solids(s)
    core=[x for x in sol if vol(x)>4000][0]; ribs=[x for x in sol if vol(x)<4000]
    outer=max(shells(core),key=lambda sh: len(faces(sh)))
    return s,core,mksolid(outer),ribs
