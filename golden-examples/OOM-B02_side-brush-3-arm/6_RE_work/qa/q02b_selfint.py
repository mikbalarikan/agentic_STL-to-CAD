"""QA step 2b — BRep self-intersection check (OCC BOPAlgo_CheckerSI) on the delivered STEP."""
from build123d import *
from OCP.BOPAlgo import BOPAlgo_ArgumentAnalyzer, BOPAlgo_CheckerSI
from OCP.TopTools import TopTools_ListOfShape

shape = import_step("/root/projects/oomwoo_b02/scratch/out_it2/OOM-B02.step")
tds = shape.wrapped

ck = BOPAlgo_CheckerSI()
ls = TopTools_ListOfShape(); ls.Append(tds)
ck.SetArguments(ls)
ck.SetRunParallel(True)
ck.SetLevelOfCheck(9)
ck.Perform()
try:
    err = ck.HasErrors()
except Exception:
    err = ck.ErrorStatus() != 0
print("CheckerSI HasErrors:", err)
res = ck.DS()
print("n interferences (VV,VE,EE,VF,EF,FF):")
tot = 0
for nm in ["VV","VE","EE","VF","EF","FF"]:
    try:
        it = getattr(res, "Interferences"+nm)()
        n = it.Size() if hasattr(it,'Size') else it.Extent()
    except Exception as e:
        n = f"n/a ({e})"
    print("  ", nm, n)
    if isinstance(n,int): tot += n
print("total:", tot)
