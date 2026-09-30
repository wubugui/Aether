"""Read current exported native terrain, compare to the revised authoring cage."""
from pathlib import Path
import ast,sys,json,hashlib,numpy as np
root=Path('D:/test6');sys.path.insert(0,str(root/'blender'))
import terrain_topology as T
syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text());ns={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'reader','exec'),ns)
rows=[]
for cx,cz in [(-1,-1),(-1,0)]:
 path=root/f'assets/terrain/Ground_{cx}_{cz}.glb'
 _,old=ns['triangles'](path);old=np.unique(old.reshape(-1,3),axis=0)
 v,f=T.chunk_mesh(cx,cz);sampler=T.SurfaceSampler();sampler.add(cx,cz,v,f)
 current=[]
 for q in old:
  distances=np.sum((v[:,[0,2]]-q[[0,2]])**2,axis=1);i=int(distances.argmin());assert distances[i]<.001**2
  current.append(v[i,1])
 current=np.asarray(current)
 delta=current-old[:,1];mask=abs(delta)>.001;changed=old[mask]+[cx*768,0,cz*768]
 row={'name':path.stem,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'samples':len(old),'changed':int(mask.sum()),'max_abs_delta':float(abs(delta).max()),'changed_bounds':[changed.min(0).tolist(),changed.max(0).tolist()] if mask.any() else None,'sampler_misses':sampler.misses,'changes':np.c_[changed,delta[mask]].tolist()}
 rows.append(row);print(json.dumps(row),flush=True)
(root/'captures/round-10l-neighbor-vertex-delta.json').write_text(json.dumps(rows,indent=2))
