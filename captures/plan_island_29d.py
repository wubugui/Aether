"""Solve connected terrain shoulders on actual editable mesh, with saved support fixed."""
from pathlib import Path
import json,math,collections
import numpy as np
from scipy.sparse import lil_matrix,diags
from scipy.sparse.linalg import spsolve
from scipy.optimize import linear_sum_assignment
R=Path(__file__).resolve().parents[1];e=json.loads((R/'captures/lantern_island_study_29b/geometry-evidence.json').read_text());prior=json.loads((R/'captures/lantern_island_study_29b/terrain-plan.json').read_text())
t=e['new']['island_c grass and exposed rock terrain'];v=np.array(t['vertices']);n=len(v)//2;top=[(i,p) for i,p in enumerate(t['polygons']) if max(p)<n]
edges=collections.Counter(tuple(sorted((p[j],p[(j+1)%3]))) for _,p in top for j in range(3))
boundary=sorted({i for edge,count in edges.items() if count==1 for i in edge});assert len(boundary)==18
fixed=sorted(set(prior['protected_vertex_indices'])|set(boundary));free=sorted(set(range(n))-set(fixed))
# Integrated squared slope uses actual triangle gradients and projected area;
# unequal path tessellation does not become an arbitrary per-edge weight.
A=lil_matrix((n,n));mass=np.zeros(n)
for _,p in top:
 q=v[p];mat=np.column_stack([q[:,:2],np.ones(3)]);inv=np.linalg.inv(mat);gradient=inv[:2,:];area=abs(np.linalg.det(mat))*.5
 local=area*(gradient.T@gradient)
 for a,i in enumerate(p):
  mass[i]+=area/3
  for b,j in enumerate(p):A[i,j]+=local[a,b]
A=A.tocsr();new=v.copy();z=v[:n,2].copy()
# Four short offset knuckles, expressed as broad local height constraints on
# the original connected surface. No added long roof slabs or detached pylons.
knuckles=[(-9,-25,5.5,4.,12.5),(7,-17,4.5,5.5,13.8),(17,6,5.,4.,12.2),(-2,19,4.5,6.,11.8)]
weights=np.zeros(n);targets=np.zeros(n)
for i,(x,y,_) in enumerate(v[:n]):
 for cx,cy,sx,sy,h in knuckles:
  d=((x-cx)/sx)**2+((y-cy)/sy)**2
  w=max(0.,1-d)**2*.10*mass[i]
  weights[i]+=w;targets[i]+=w*h
M=A+diags(weights);rhs=targets[free]-M[free,:][:,fixed]@z[fixed]
z[free]=spsolve(M[free,:][:,free],rhs)
new[:n,2]=z;new[n:,2]=z-.65
assert np.array_equal(new[prior['protected_vertex_indices']],v[prior['protected_vertex_indices']])
def steep(vertices):
 result=[]
 for i,p in top:
  q=vertices[p];normal=np.cross(q[1]-q[0],q[2]-q[0]);normal/=np.linalg.norm(normal)
  if q[:,2].mean()>10 and normal[2]<.5:result.append(i)
 return result
# Recover the true source boundary correspondence, then replace the original
# two intermediate closed bands with one unequal, inward-tucked fracture row.
c=e['new']['island_c faulted bedrock'];cv=np.array(c['vertices']);coast=cv[18:36];cost=np.sum((coast[:,None,:2]*.90-v[boundary][None,:,:2])**2,axis=2)
rows,cols=linear_sum_assignment(cost);mapping=[boundary[j] for j in cols]
assert rows.tolist()==list(range(18))
mid=[]
fractions=[.70,.38,.64,.28,.75,.44,.30,.67,.39,.76,.48,.29,.71,.36,.62,.43,.78,.32]
for i,j in enumerate(mapping):
 cxy=coast[i,:2];rim=new[j,:2];p=cxy*.48+rim*.52
 # Offset alternates in authored groups without making a full parallel ledge.
 tangent=coast[(i+1)%18,:2]-coast[(i-1)%18,:2];tangent/=np.linalg.norm(tangent)
 p+=tangent*[.8,-.5,.2,-.7,.4,.6][i%6]
 mid.append([*p,max(1.7,(new[n+j,2])*fractions[i])])
coreverts=np.concatenate([cv[:36],np.array(mid),new[n:]])
faces=[list(reversed(range(18)))]
for level in range(3):
 for i in range(18):
  j=(i+1)%18;a=level*18+i;b=level*18+j
  c1=(level+1)*18+j if level<2 else 54+mapping[j];d=(level+1)*18+i if level<2 else 54+mapping[i]
  faces.extend([[a,b,d],[b,c1,d]] if (i+level)%2 else [[a,b,c1],[a,c1,d]])
faces += [[54+i for i in p] for _,p in top]
out={'terrain_vertices':new.tolist(),'core_vertices':coreverts.tolist(),'core_faces':faces,'core_cap_offset':54,'core_boundary_map':mapping,'protected_face_indices':prior['protected_face_indices'],'protected_vertex_indices':prior['protected_vertex_indices'],'top_vertex_count':n,'changed_top_vertices':int(np.sum(np.abs(new[:n,2]-v[:n,2])>1e-5)),'maximum_height_delta_m':float(np.max(np.abs(z-v[:n,2]))),'old_selected_steep_faces':steep(v),'new_selected_steep_faces':steep(new),'knuckles':knuckles,'scope':'Connected actual terrain remesh heights.515 protected terrain triangles and18 shoreline XY/Z controls retained from29b. Replace two intermediate bedrock bands with one uneven row; editable native construction required. Geometry metrics not visual acceptance.'}
(R/'captures/island-29d-terrain-plan.json').write_text(json.dumps(out,indent=2));print({k:out[k] for k in ['changed_top_vertices','maximum_height_delta_m']},'selected high steep faces',len(out['old_selected_steep_faces']),len(out['new_selected_steep_faces']))
