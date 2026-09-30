import sys,ast,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/test6/blender')
from cliff_terrace_topology import ground_at
root=Path('D:/test6')
syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text());reader={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'reader','exec'),reader)
cache={}
def exported_height(x,z):
    cell=(int(np.floor(x/768)),int(np.floor(z/768)))
    if cell not in cache:
        _,t=reader['triangles'](root/'assets/terrain'/f'Ground_{cell[0]}_{cell[1]}.glb');t+=np.array([cell[0]*768,0,cell[1]*768]);cache[cell]=t
    t=cache[cell];a,b,c=t[:,0],t[:,1],t[:,2]
    den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2])
    valid=abs(den)>1e-10;den=np.where(valid,den,1)
    u=((b[:,2]-c[:,2])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,2]))/den
    v=((c[:,2]-a[:,2])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,2]))/den
    keep=valid&(u>=-1e-5)&(v>=-1e-5)&(u+v<=1+1e-5)
    return float((u*a[:,1]+v*b[:,1]+(1-u-v)*c[:,1])[keep].max())
for x,z in [(29.93,31.30),(35.84,35.71),(46.44,26.46),(62.81,16.19),(75.16,6.71),(117.84,-12.72)]:
    print('TERRAIN',x,z,'author',ground_at(x,z),'exported',exported_height(x,z),flush=True)
