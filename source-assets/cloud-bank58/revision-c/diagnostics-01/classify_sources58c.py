"""Read-only truecoarsecavity containment and actualcycle/control correspondence."""
import json
from pathlib import Path
import numpy as np
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parent/'recovery-01';n=np.load(P/'coarse15-actual-triangles58c.npz');v=n['vertices'];f=n['indices'];g=json.loads((P/'coarse15-geometry58c.json').read_text());big=max(g['components'],key=lambda c:c['vertices']);small=min(g['components'],key=lambda c:c['vertices']);main=v[f[big['triangle_ids']]];inner=v[np.unique(f[small['triangle_ids']])]

def ray(p,t,d):
 d=np.array(d,float);d/=np.linalg.norm(d);a=t[:,0];e1=t[:,1]-a;e2=t[:,2]-a;h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);valid=abs(det)>1e-10;inv=np.zeros(len(t));inv[valid]=1/det[valid];s=np.array(p)-a;u=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);w=inv*(q@d);dist=inv*np.einsum('ij,ij->i',e2,q);ids=np.flatnonzero(valid&(u>=-1e-9)&(w>=-1e-9)&(u+w<=1+1e-9)&(dist>1e-5));hits=sorted(float(dist[i]) for i in ids);unique=[]
 for h in hits:
  if not unique or abs(h-unique[-1])>1e-4:unique.append(h)
 return dict(hit_count=len(unique),inside=bool(len(unique)%2),hit_distances_m=unique)

def distances(p,t):
 a,b,c=t[:,0],t[:,1],t[:,2];u=b-a;v=c-a;normal=np.cross(u,v);nn=np.einsum('ij,ij->i',normal,normal);ap=np.array(p)-a;dot=np.einsum('ij,ij->i',ap,normal);plane=dot*dot/nn;proj=ap-normal*(dot/nn)[:,None]
 uu=np.einsum('ij,ij->i',u,u);uv=np.einsum('ij,ij->i',u,v);vv=np.einsum('ij,ij->i',v,v);wu=np.einsum('ij,ij->i',proj,u);wv=np.einsum('ij,ij->i',proj,v);det=uu*vv-uv*uv;beta=(vv*wu-uv*wv)/det;gamma=(uu*wv-uv*wu)/det;inside=(beta>=0)&(gamma>=0)&(beta+gamma<=1);best=np.where(inside,plane,np.inf)
 for x,y in [(a,b),(b,c),(c,a)]:
  edge=y-x;frac=np.clip(np.einsum('ij,ij->i',np.array(p)-x,edge)/np.einsum('ij,ij->i',edge,edge),0,1);q=x+edge*frac[:,None];best=np.minimum(best,np.einsum('ij,ij->i',q-p,q-p))
 return np.sqrt(best)
controls=json.loads((R/'native-control-input58c.json').read_text())['controls'];meshes=[(s['id'],np.array(s['vertices'])[np.array(s['faces'])]) for s in controls];directions=[[.817,.431,.382],[-.239,.881,.408],[.337,-.287,.897]];rows=[]
for p in [inner.mean(0),*inner]:rows.append(dict(world=p.tolist(),main_shell_rays=[ray(p,main,d) for d in directions]))
center=inner.mean(0);nearest=sorted([dict(id=name,actual_triangle_distance_m=float(distances(center,t).min()),contains_center=ray(center,t,directions[0])['inside']) for name,t in meshes],key=lambda r:r['actual_triangle_distance_m'])
cavity=dict(negative_volume_m3=small['signed_volume_m3'],vertices=small['vertices'],world_bounds=[inner.min(0).tolist(),inner.max(0).tolist()],all_vertices_and_center_inside_main=all(q['inside'] for r in rows for q in r['main_shell_rays']),main_inner_nonadjacent_contacts=g['nonadjacent_contact_or_intersection_count'],rows=rows,closest_control_surfaces=nearest[:8],no_cleanup_performed=True)
cycles=json.loads((P/'actual-topology-cycles58c.json').read_text())['root_trials'][0]['cycles'];cycle_rows=[]
for cycle in cycles:
 points=np.array(cycle['points_world']);attribution=[]
 for p in points:
  matches=sorted([(float(distances(p,t).min()),name) for name,t in meshes]);attribution.append(dict(world=p.tolist(),closest_control=matches[0][1],surface_distance_m=matches[0][0]))
 cycle_rows.append(dict(world_bounds=cycle['world_bounds'],length_m=cycle['length_m'],nearest_control_counts=dict(Counter(a['closest_control'] for a in attribution)),points=attribution))
(P/'cavity-and-cycle-sources58c.json').write_text(json.dumps(dict(cavity=cavity,cycles=cycle_rows,attribution_limit='Nearest originalcontrolsurfaces are measured distances aftervoxelization, not exact semantic surfaceownership.'),indent=2)+'\n')
print('CAVITY',cavity['all_vertices_and_center_inside_main'],'nearest',nearest[:4])
for r in cycle_rows:print(r['world_bounds'],r['nearest_control_counts'])
