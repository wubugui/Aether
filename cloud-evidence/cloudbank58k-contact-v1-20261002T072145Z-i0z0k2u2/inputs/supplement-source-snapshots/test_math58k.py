"""Executed pure-math controls. No asserts, bpy, native assets or image work."""
import ast,copy,json,os,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import poly58k as poly
import check_coplanar_contacts58k as contact
from check_preparation58k import project,c,E_REPORT


def main():
    os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
    cfg=json.loads((P/'design58k.json').read_text());m=poly.build(cfg);V,F=m['vertices'],m['faces'];rows=[]
    def check(name,value):poly.require(value,name);rows.append(dict(name=name,passed=True))
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):rows.append(dict(name=name,passed=True));return
        raise ValueError(name+' unexpectedly accepted')
    def mutate(fn):
        d=copy.deepcopy(cfg);fn(d);return poly.build(d)
    check('single connected closed Euler-two shell',m['proof']['vertices']==194 and m['proof']['triangles']==384 and m['proof']['euler']==2)
    check('exact deterministic fingerprint',poly.build(cfg)['fingerprint']==m['fingerprint'])
    saved=json.loads((P/'candidate-probe58k.json').read_text())
    check('same one candidate as first probe',saved['fingerprint']==m['fingerprint'])
    check('unchanged original hard budgets',cfg['tolerances']==json.loads((P.parent/'revision-j2/design58j2.json').read_text())['tolerances'])
    check('six convex semantic weights',np.all(m['weights']>=0) and np.allclose(m['weights'].sum(axis=1),1,rtol=0,atol=1e-12))
    check('all six exposed semantic regions',set(m['owners'])==set(r['id'] for r in cfg['controls']))
    check('broad authored saddle sections',all(r['top_y_m']-r['bottom_y_m']>=140 for r in [cfg['authoring_recipe']['rings'][4],cfg['authoring_recipe']['rings'][9]]))
    check('no clipping fragments',m['proof']['minimum_triangle_area_m2']>200 and m['proof']['minimum_edge_m']>14)
    reject('hole rejected',lambda:poly.topology(V,F[:-1],cfg['tolerances']))
    reject('duplicate face rejected',lambda:poly.topology(V,np.vstack([F,F[0]]),cfg['tolerances']))
    reversed_face=F.copy();reversed_face[0]=reversed_face[0][::-1]
    reject('inconsistent winding rejected',lambda:poly.topology(V,reversed_face,cfg['tolerances']))
    degenerate=V.copy();degenerate[F[0,1]]=degenerate[F[0,0]]
    reject('degenerate triangle rejected',lambda:poly.topology(degenerate,F,cfg['tolerances']))
    reject('disconnected double envelope rejected',lambda:poly.topology(np.vstack([V,V+[1000,0,0]]),np.vstack([F,F+len(V)]),cfg['tolerances']))
    reject('zero-scale handle rejected',lambda:mutate(lambda d:d['controls'][0].update(scale=[0,1,1])))
    reject('reflected handle rejected',lambda:mutate(lambda d:d['controls'][0].update(scale=[-1,1,1])))
    reject('nonfinite handle rejected',lambda:mutate(lambda d:d['controls'][0].update(center=[float('nan'),0,0])))
    reject('collapsed section thickness rejected',lambda:mutate(lambda d:d['authoring_recipe']['rings'][3].update(top_y_m=700)))
    reject('crossed station order rejected',lambda:mutate(lambda d:d['authoring_recipe']['rings'][3].update(center_uvy_m=[100,-32,720])))
    reject('negative semantic influence rejected',lambda:mutate(lambda d:d['authoring_recipe']['rings'][3].update(control_weights=[-1,2,0,0,0])))
    reject('unordered angular stations rejected',lambda:mutate(lambda d:d['authoring_recipe']['rings'][3].update(angles_degrees=list(reversed(d['authoring_recipe']['rings'][3]['angles_degrees'])))))
    reject('invalid authored diagonals rejected',lambda:mutate(lambda d:d['authoring_recipe'].update(diagonal_rows=['invalid']*15)))
    for index,row in enumerate(cfg['controls']):
        d=copy.deepcopy(cfg);d['controls'][index]['center'][2]+=2
        moved=poly.build(d);delta=moved['vertices']-V
        check('editable '+row['id'],np.allclose(delta[:,2],m['weights'][:,index]*2,rtol=0,atol=2e-13) and float(delta[:,2].max())>0)
        poly.intersection_check(moved['vertices'],moved['faces'],eps=1e-8)
    # Reference checker rejects nonindexed noncoplanar penetration.
    vv=np.array([[0,0,0],[2,0,0],[0,2,0],[.5,.5,-1],[.5,.5,1],[1.5,.5,0]],float);ff=np.array([[0,1,2],[3,4,5]])
    reject('noncoplanar penetration rejected',lambda:poly.intersection_check(vv,ff,eps=1e-8))
    vv=np.array([[0,0,0],[2,0,0],[0,2,0],[2,0,0],[3,0,0],[2,-1,0]],float)
    check('nonindexed coplanar point contact detected',bool(contact.check_coplanar_contacts(vv,ff,eps=1e-8)['nonindexed_contact_violations']))
    vv[3:]=[[.5,0,0],[1.5,0,0],[1,-1,0]]
    check('nonindexed coplanar edge contact detected',bool(contact.check_coplanar_contacts(vv,ff,eps=1e-8)['nonindexed_contact_violations']))
    # Native transform decomposition is not simulated here; only float32 matrix arithmetic.
    frame=json.loads(c.PLAN.read_text());basis=poly.source_basis(frame);d=copy.deepcopy(cfg)
    for row in d['controls']:
        row['center']=(np.linalg.inv(basis)@(basis@row['center']).astype(np.float32).astype(float)).tolist()
        row['matrix3']=(np.linalg.inv(basis)@basis.astype(np.float32).astype(float)).tolist()
    prediction=poly.build(d);native=(prediction['vertices']@basis.T).astype(np.float32).astype(float)
    poly.topology(native,F,cfg['tolerances']);poly.intersection_check(native,F,eps=1e-8)
    check('float32 control matrix arithmetic prediction passes',not contact.check_coplanar_contacts(native,F,eps=1e-8)['nonindexed_contact_violations'])
    camera=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns')['cameras'][1]
    reject('fixed camera crop rejected',lambda:project(native*10,camera))
    # Copied geometry utilities have no implementation drift.
    old=(P.parent/'revision-j2/poly58j2.py').read_text();new=(P/'poly58k.py').read_text()
    def bodies(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    a,b=bodies(old),bodies(new)
    check('inherited topology and intersection bodies unchanged',all(a[k]==b[k] for k in ['require','topology','fingerprint','source_basis','intersection_check']))
    print(json.dumps(dict(passed=True,test_count=len(rows),tests=rows,optimized_python=not __debug__,native_started=False,images=[]),indent=2))
if __name__=='__main__':main()
