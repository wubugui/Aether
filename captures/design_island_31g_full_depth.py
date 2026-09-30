from pathlib import Path
import json,collections,math
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from shapely.geometry import Polygon
R=Path(__file__).resolve().parents[1]
exec(compile((R/'captures/inspect_island_31g_patch.py').read_text().split('out=[]')[0],'boundary_tools','exec'))
m=json.loads((R/'captures/island-31g-cut-patch-full-depth.json').read_text());v=np.array(m['vertices']);f=np.array(m['polygons']);ids=set(m['selected_faces'])
loops,bad=boundary(ids);assert bad is None and len(loops)==1,(bad,loops)
loop=loops[0];xyz=v[loop];theta=np.unwrap(np.arctan2(xyz[:,1],xyz[:,0]));q=np.column_stack([theta,xyz[:,2]])
p=Polygon(q)
print('PATCH',len(ids),'boundary',len(loop),'angle-z valid',p.is_valid,'area',p.area)
print('BOUNDARY',[(i,[round(x,3) for x in v[i]]) for i in loop])
# Use a convex topological disk parameterization, without flattening physical geometry.
lengths=np.linalg.norm(np.roll(xyz,-1,axis=0)-xyz,axis=1)
angle=np.r_[0,np.cumsum(lengths[:-1])]/sum(lengths)*2*math.pi
uv={i:np.array([math.cos(a),math.sin(a)]) for i,a in zip(loop,angle)}
adj=collections.defaultdict(set)
for i in ids:
 for a,b in zip(f[i],np.roll(f[i],-1)):adj[int(a)].add(int(b));adj[int(b)].add(int(a))
interior=sorted(set(adj)-set(loop));lookup={i:j for j,i in enumerate(interior)};A=lil_matrix((len(interior),len(interior)));rhs=np.zeros((len(interior),2))
for i in interior:
 j=lookup[i];A[j,j]=len(adj[i])
 for n in adj[i]:
  if n in lookup:A[j,lookup[n]]=-1
  else:rhs[j]+=uv[n]
sol=spsolve(A.tocsr(),rhs)
for i,pos in zip(interior,sol):uv[i]=pos
assert len(set(adj))-sum(1 for a,ns in adj.items() for b in ns if a<b)+len(ids)==1
report=dict(selected_faces=sorted(ids),boundary=loop,interior=interior,uv={str(i):uv[i].tolist() for i in uv},boundary_angle_z_simple=p.is_valid,parameterization='Positive uniform harmonic disk with 3D arc-length circle boundary. Only connectivity parameterization; no claim that actual rear surface is a single-valued planar depth graph.',source='captures/island-31g-cut-patch-full-depth.json')
(R/'captures/island-31g-disk-full-depth.json').write_text(json.dumps(report,indent=2))
for target in [(-5,6,8),(-3,11,5),(-8,12,2),(0,15,3),(-10,7,4)]:
 i=min(interior,key=lambda j:np.linalg.norm(v[j]-target));print('CONTROL_CANDIDATE',i,v[i].tolist(),uv[i].tolist())
