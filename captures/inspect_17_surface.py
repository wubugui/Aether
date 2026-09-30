"""Read-only localization of candidate facets against original Blender IDs."""
import ast,json,sys
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
label=sys.argv[1]
syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text())
reader={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'reader','exec'),reader)
item=json.loads((root/'captures'/('foreground_study_'+label)/'manifest.json').read_text())[0]
data=next(x for x in json.loads((root/'captures/foreground-16-source-inspection.json').read_text()) if x['name']==item['name'])
points={x['index']:np.array(x['xyz']) for x in data['controls']}
for edit in item['controls']:points[edit['index']]=np.array(edit['after'])
_,tri=reader['triangles'](root/item['path'])
for i,t in enumerate(tri):
    n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n)
    if t[:,1].max()>0 and n[1]<-.001:
        print('DOWNWARD',i,t.tolist())
        for p in t:
            d={j:np.linalg.norm(p-v[[0,2,1]]*[1,1,-1]) for j,v in points.items()}
            match=min(d,key=d.get);print('NATIVE',match,'error',d[match])
for i in range(20,32):
    ids=data['faces_first'][i]['indices']
    if all(j in points for j in ids):
        t=np.array([points[j] for j in ids]);n=np.cross(t[1]-t[0],t[2]-t[0]);n/=np.linalg.norm(n)
        print('PROFILE',i,ids,'slope',round(float(np.degrees(np.arccos(np.clip(n[2],-1,1)))),2))
