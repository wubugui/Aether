from pathlib import Path
import sys,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'blender'))
import terrain_topology as T
s=T.SurfaceSampler()
for cx,cz in [(-1,-1),(0,-1),(0,0)]:
    v,f=T.chunk_mesh(cx,cz);s.add(cx,cz,v,f)
    center=v[f].mean(axis=1)
    y=s.height(center[:,0]+cx*768,center[:,2]+cz*768)
    error=float(np.max(np.abs(center[:,1]-y)))
    assert error<.002,(cx,cz,error)
    print('CDT VERIFIED',cx,cz,len(v),'vertices',len(f),'triangles; sampling error',error,flush=True)
assert s.misses==0,s.misses
