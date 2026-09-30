"""Read-only feasibility study: can end slopes improve with heights alone?"""
import ast,hashlib,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

root=Path(__file__).resolve().parents[1]
source=root/'captures/foreground_study_17e'
output=root/'reviews/round-17e-end-height-feasibility.json'
assert not output.exists()
item=json.loads((source/'manifest.json').read_text())[0]
syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text())
reader={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'reader','exec'),reader)
path=source/'cliff_western_slab.glb'
_,tri=reader['triangles'](path)
control={x['index']:np.array(x['after'])[[0,2,1]]*[1,1,-1] for x in item['controls']}
ids=[13,14,17,18,19]
matches=np.array([np.linalg.norm(tri-control[i],axis=2)<1e-5 for i in ids])
active=matches.any(axis=(0,2))
normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
active &= normal[:,1]>1e-6
indices=np.where(active)[0]
xy=tri[active][:,:,[0,2]]
matrix=np.stack([xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]],axis=1)
inverse=np.linalg.inv(matrix)
match=matches[:,active,:]
base=tri[active,:,1]
initial=np.array([control[i][1] for i in ids])
def gradients(y):
    heights=base.copy()
    for k in range(len(ids)):heights[match[k]]=y[k]
    delta=np.stack([heights[:,1]-heights[:,0],heights[:,2]-heights[:,0]],axis=1)
    return np.linalg.norm(np.einsum('nij,nj->ni',inverse,delta),axis=1)
before=gradients(initial)
def constraint(x):return x[-1]-gradients(x[:-1])
result=minimize(lambda x:x[-1]+1e-5*np.sum((x[:-1]-initial)**2),
    np.r_[initial,max(before)],method='SLSQP',
    bounds=[(47.,55.),(43.,48.),(39.,50.),(39.,47.),(39.5,44.),(0.,10.)],
    constraints=[{'type':'ineq','fun':constraint}],options={'ftol':1e-10,'maxiter':200})
after=gradients(result.x[:-1])
report={'scope':'Read-only constrained minimax height feasibility on the actual 17e western GLB. No assets modified, no visual acceptance. XZ and all unlisted vertices fixed.',
    'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'solver_success':bool(result.success),'solver_message':result.message,
    'min_constraint':float(min(constraint(result.x))),
    'controls':[{'native_id':i,'before_y':float(initial[k]),'proposed_y':float(result.x[k])} for k,i in enumerate(ids)],
    'maximum_affected_slope_before_deg':float(np.degrees(np.arctan(max(before)))),
    'maximum_affected_slope_after_deg':float(np.degrees(np.arctan(max(after)))),
    'affected_faces':[{'exported_triangle':int(i),'before_deg':float(np.degrees(np.arctan(a))),
        'proposed_deg':float(np.degrees(np.arctan(b)))} for i,a,b in zip(indices,before,after)]}
output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='affected_faces'},indent=2))
