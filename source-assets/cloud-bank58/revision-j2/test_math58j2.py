"""Small pure numerical negative controls; no native process or image."""
import copy
import json
from pathlib import Path
import sys
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));import poly58j2 as poly
from check_preparation58j2 import project


def main():
    config=json.loads((P/'design58j2.json').read_text());mesh=poly.build(config);V,F=mesh['vertices'],mesh['faces'];rows=[]
    def rejects(name,fn,contains):
        try:fn()
        except (ValueError,np.linalg.LinAlgError) as error:
            poly.require(contains in str(error),name+' rejected for an unexpected reason: '+str(error))
            rows.append(dict(name=name,passed=True,actual_error=str(error)))
        else:raise ValueError(name+' incorrectly accepted')
    def topology(f):return poly.topology(V,f,config['tolerances'])
    rejects('open shell',lambda:topology(F[:-1]),'Nonmanifold')
    rejects('duplicate triangle',lambda:topology(np.vstack((F,F[0]))),'Nonmanifold')
    reversed_face=F.copy();reversed_face[0]=reversed_face[0,::-1]
    rejects('reversed face',lambda:topology(reversed_face),'Directed edge')
    bad=copy.deepcopy(config);bad['controls'][0]['scale'][0]=0
    rejects('zero cage scale',lambda:poly.build(bad),'Nonpositive')
    duplicate=copy.deepcopy(config);duplicate['controls'][1]=copy.deepcopy(duplicate['controls'][0])
    rejects('coincident cages',lambda:poly.build(duplicate),'Coplanar')
    disconnected=copy.deepcopy(config);disconnected['controls'][-1]['center'][0]+=2000
    rejects('disconnected accent',lambda:poly.build(disconnected),'More than one surface')
    audit={'zero_dimensional_clip_outputs':0,'zero_area_clip_outputs':0}
    rejects('positive-area clipping sliver',lambda:poly.valid_polygon([np.array([0.,0,0]),np.array([.0001,0,0]),np.array([0,.0001,0])],config['tolerances'],audit),'sliver')
    a=np.array([[0.,0,0],[2,0,0],[0,2,0]])
    vertices=np.vstack((a,[[1,1,-1],[1,1,1]]))
    rejects('crossing pair shares one indexed vertex',lambda:poly.intersection_check(vertices,np.array([[0,1,2],[0,3,4]]),eps=1e-8),'Unexpected triangle')
    vertices=np.vstack((a,[[.5,.5,-1],[.5,.5,1],[1.5,.5,0]]))
    rejects('nonadjacent crossing pair',lambda:poly.intersection_check(vertices,np.array([[0,1,2],[3,4,5]]),eps=1e-8),'Unexpected disjoint')
    vertices=np.vstack((a,[[.2,.2,0],[1,.2,0],[.2,1,0]]))
    rejects('coplanar positive overlap',lambda:poly.intersection_check(vertices,np.array([[0,1,2],[3,4,5]]),eps=1e-8),'Coplanar overlap')
    reference=json.loads((P.parents[2]/'cloud-evidence/cloudbank58e-layouts-20261001T165946Z-yove55lx/outputs/build-result58e.json').read_text())
    camera=next(x for x in reference['layouts'] if x['layout']=='B_staggered_crowns')['cameras'][1]
    rejects('whole geometry moved outside fixed frame',lambda:project(V+np.array([0,0,-500.]),camera),'Fixed seven percent')
    good=np.vstack((a,[[2,2,0]]));poly.intersection_check(good,np.array([[0,1,2],[1,3,2]]),eps=1e-8)
    rows.append(dict(name='legal shared coplanar edge accepted',passed=True))
    report=dict(passed=True,test_count=len(rows),tests=rows,optimized_python=not __debug__,native_started=False)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
