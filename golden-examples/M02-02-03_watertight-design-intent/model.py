#!/usr/bin/env python3
"""Parametric design-intent compound spur gear rebuild.

Semantic chain:
- BIG_INVOLUTE_TOOTH_SKETCH -> BIG_EXTRUDE -> CIRCULAR_PATTERN_30X
- SMALL_INVOLUTE_TOOTH_SKETCH -> SMALL_EXTRUDE -> CIRCULAR_PATTERN_17X
- CONTINUOUS_CORE / BOOLEAN_UNION -> THROUGH_BORE_CUT

STEP is a neutral exact B-Rep and does not retain native SolidWorks history.
"""
from __future__ import annotations
import json, math
from pathlib import Path
from build123d import Cylinder, Face, Pos, Rot, Solid, Vector, Wire, export_step, export_stl, import_step
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer

HERE=Path(__file__).resolve().parent
PART_ID='M02-02-03_CORRECTED'
COMMON_MODULE=0.6
PRESSURE_ANGLE_DEG=20.0
BORE_DIAMETER=1.95
BIG={"name":"big","teeth":30,"tip_diameter":19.05,"width":3.0,"z0":0.0,"phase_deg":0.0}
SMALL={"name":"small","teeth":17,"tip_diameter":11.2,"width":6.95,"z0":3.0,"phase_deg":0.0}
FLANK_SAMPLES=20
TIP_SAMPLES=7

def gear_radii(g):
    rp=COMMON_MODULE*g['teeth']/2.0
    rb=rp*math.cos(math.radians(PRESSURE_ANGLE_DEG))
    ra=g['tip_diameter']/2.0
    rf=rp-1.25*COMMON_MODULE
    return {"pitch":rp,"base":rb,"tip":ra,"root":rf}

def tooth_face(g):
    z=g['teeth']; r=gear_radii(g)
    rb,rp,ra,rf=r['base'],r['pitch'],r['tip'],r['root']
    attach=rf-0.04
    tp=math.sqrt((rp/rb)**2-1.0)
    invp=tp-math.atan(tp)
    half=math.pi/(2*z)
    def angle(rad):
        t=math.sqrt(max(0.0,(rad/rb)**2-1.0)); inv=t-math.atan(t)
        return half+invp-inv
    ba,ta=angle(rb),angle(ra)
    def polar(rad,a): return (rad*math.cos(a),rad*math.sin(a))
    pts=[polar(attach,-ba),polar(rb,-ba)]
    for i in range(1,FLANK_SAMPLES+1):
        rad=rb+(ra-rb)*i/FLANK_SAMPLES; pts.append(polar(rad,-angle(rad)))
    for i in range(1,TIP_SAMPLES+1): pts.append(polar(ra,-ta+2*ta*i/TIP_SAMPLES))
    for i in range(FLANK_SAMPLES-1,-1,-1):
        rad=rb+(ra-rb)*i/FLANK_SAMPLES; pts.append(polar(rad,angle(rad)))
    pts.append(polar(attach,ba))
    return Face(Wire.make_polygon([Vector(x,y,0) for x,y in pts],close=True))

def gear_solid(g):
    r=gear_radii(g); z0=g['z0']; width=g['width']
    core=Cylinder(r['root'],width).moved(Pos(0,0,z0+width/2))
    one=Solid.extrude(tooth_face(g).moved(Pos(0,0,z0)),Vector(0,0,width))
    body=core
    for i in range(g['teeth']):
        body=body.fuse(one.moved(Rot(0,0,g['phase_deg']+i*360/g['teeth'])))
    return body.clean()

def topo_counts(shape):
    out=[]
    for kind in (TopAbs_SOLID,TopAbs_SHELL):
        ex=TopExp_Explorer(shape.wrapped,kind); n=0
        while ex.More(): n+=1; ex.Next()
        out.append(n)
    return out

def build():
    big=gear_solid(BIG); small=gear_solid(SMALL)
    # A continuous root-radius core creates positive-volume connectivity across
    # the coplanar axial transition without altering either specified envelope.
    min_root=min(gear_radii(BIG)['root'],gear_radii(SMALL)['root'])
    total=BIG['width']+SMALL['width']
    bridge=Cylinder(min_root,total).moved(Pos(0,0,total/2))
    body=big.fuse(bridge).fuse(small).clean()
    bore=Cylinder(BORE_DIAMETER/2,total+2).moved(Pos(0,0,total/2))
    return body.cut(bore).clean()

def main():
    body=build(); step=HERE/f'{PART_ID}.step'; stl=HERE/f'{PART_ID}.stl'
    export_step(body,step); export_stl(body,stl,tolerance=0.01,angular_tolerance=0.05)
    reopened=import_step(step); solids,shells=topo_counts(reopened); bb=reopened.bounding_box()
    report={
      'schema':'oguz-designer-selfcheck-v1','status':'MODELING_SELFCHECK_COMPLETE_NOT_QA',
      'step_path':str(step),'brep_valid':bool(BRepCheck_Analyzer(reopened.wrapped).IsValid()),
      'solid_count':solids,'shell_count':shells,'shell_closed':bool(reopened.solids()[0].shells()[0].wrapped.Closed()) if solids==1 and shells==1 else False,
      'volume_mm3':reopened.volume,'bbox_mm':[bb.size.X,bb.size.Y,bb.size.Z],
      'parameters':{'common_module_mm':COMMON_MODULE,'pressure_angle_deg':PRESSURE_ANGLE_DEG,'bore_diameter_mm':BORE_DIAMETER,'big':BIG,'small':SMALL},
      'derived':{'big':gear_radii(BIG),'small':gear_radii(SMALL),'overall_height_mm':BIG['width']+SMALL['width']},
      'feature_chain':['BIG_INVOLUTE_TOOTH_SKETCH','BIG_EXTRUDE','CIRCULAR_PATTERN_30X','SMALL_INVOLUTE_TOOTH_SKETCH','SMALL_EXTRUDE','CIRCULAR_PATTERN_17X','CONTINUOUS_CORE_UNION','THROUGH_BORE_CUT'],
      'assumptions':['Common module 0.6 mm and 20 degree pressure angle; operator supplied tip diameters govern tooth truncation.','Zero profile shift/backlash/tip relief; compact polygonal involute approximation in the semantic sketch.','Axial bands are adjacent: large Z=0..3.00 mm and small Z=3.00..9.95 mm.','Relative angular phase is set to 0 degrees because no phase datum was supplied.','No extra hub projection is modeled because its diameter and height were not supplied.'],
      'claim_boundary':'Design-intent CAD matching supplied tooth counts, outside diameters, face widths and bore. Physical mesh fit/interchangeability remains unapproved.'
    }
    (HERE/'model_params.json').write_text(json.dumps(report,indent=2)+'\n')
    if not(report['brep_valid'] and solids==1 and shells==1 and report['shell_closed'] and report['volume_mm3']>0): raise RuntimeError(report)
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
