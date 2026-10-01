from pathlib import Path
import json,numpy as np
D=Path(__file__).resolve().parent;raw=json.loads((D/'native-coast.json').read_text());scope=json.loads((D/'scope.json').read_text());tris={v['node'].split('/')[-1]:np.array(v['faces']).reshape(-1,3,3) for v in raw['terrain']}
def height(k,x,z):
 t=tris[k];a=t[:,0];b=t[:,1];c=t[:,2];d=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2]);n=np.abs(d)>1e-8
 u=np.divide((b[:,2]-c[:,2])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,2]),d,out=np.zeros_like(d),where=n)
 v=np.divide((c[:,2]-a[:,2])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,2]),d,out=np.zeros_like(d),where=n);w=1-u-v
 ok=n&(u>=-1e-6)&(v>=-1e-6)&(w>=-1e-6)
 h=u*a[:,1]+v*b[:,1]+w*c[:,1]
 return float(h[ok].max()) if ok.any() else None
out={'profiles':[],'scatter_origin_support':[],'neighbor_meshes':[],'nearest_other_mesh_groups':[]}
for z in [-3000,-2950,-2900,-2850,-2800]:
 x=.641329667*z-964.807821
 row={'z':z,'fitted_shore_x':x,'samples':[]}
 for delta in [-50,-25,-10,0,10,25,50,75,100]:row['samples'].append({'x_offset_from_fitted_shore':delta,'height':height('Ground_-4_-4',x+delta,z)})
 out['profiles'].append(row)
for group in scope['scatter']:
 for entry in group['instances_in_box']:
  x,y,z=entry['position'];h=height('Ground_-4_-4',x,z)
  out['scatter_origin_support'].append({'node':group['node'],'index':entry['index'],'position':entry['position'],'surface_y':h,'origin_delta_y':y-h if h is not None else None})
for k in ['Ground_-5_-4','Ground_-3_-4','Ground_-4_-5','Ground_-4_-3']:
 t=tris[k];out['neighbor_meshes'].append({'name':k,'min':t.min(axis=(0,1)).tolist(),'max':t.max(axis=(0,1)).tolist(),'triangles':len(t)})
xmin,xmax,zmin,zmax=scope['proposed_intake_box_xmin_xmax_zmin_zmax'];groups={}
for m in raw['other_meshes']:
 a,b=m['min'],m['max'];dx=max(xmin-b[0],a[0]-xmax,0);dz=max(zmin-b[2],a[2]-zmax,0);dist=(dx*dx+dz*dz)**.5;k='/'.join(m['node'].split('/')[:4])
 if k not in groups or dist<groups[k]['distance_from_box']:groups[k]={'node':k,'distance_from_box':dist,'nearest_mesh_min':a,'nearest_mesh_max':b}
out['nearest_other_mesh_groups']=sorted(groups.values(),key=lambda m:m['distance_from_box'])[:12]
(D/'support.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['profiles'],indent=2));print('nearby:',json.dumps(out['nearest_other_mesh_groups'][:8],indent=2))
print('scatter origin deltas:',min(v['origin_delta_y'] for v in out['scatter_origin_support']),max(v['origin_delta_y'] for v in out['scatter_origin_support']))
