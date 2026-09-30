import json,collections,math
import numpy as np
from scipy.spatial import cKDTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake48'
b=json.load(open(D+'/base47.json'));p=json.load(open(D+'/lake48-payload.json'));out={'meshes':[],'corridor':[],'shore_samples':[],'scatter_support':[]};meshes={m['name']:np.array(m['vertices']).reshape(-1,3,3) for m in p['meshes']}
for k,v in json.load(open(D+'/support47.json'))['meshes'].items():
 if k not in meshes:meshes[k]=np.array(v['faces']).reshape(-1,3,3)
def height(x,z,names=None):
 best=-1e10
 for name,tri in meshes.items():
  if names and name not in names:continue
  a,c,d=tri[:,0],tri[:,1],tri[:,2];den=(c[:,2]-d[:,2])*(a[:,0]-d[:,0])+(d[:,0]-c[:,0])*(a[:,2]-d[:,2]);valid=np.abs(den)>1e-8
  den=np.where(valid,den,1);u=((c[:,2]-d[:,2])*(x-d[:,0])+(d[:,0]-c[:,0])*(z-d[:,2]))/den;v=((d[:,2]-a[:,2])*(x-d[:,0])+(a[:,0]-d[:,0])*(z-d[:,2]))/den;w=1-u-v;valid &= (u>=-1e-6)&(v>=-1e-6)&(w>=-1e-6)
  y=u*a[:,1]+v*c[:,1]+w*d[:,1]
  if valid.any():best=max(best,float(y[valid].max()))
 return None if best<-1e9 else best
def edges(v):
 cnt=collections.Counter()
 for t in v:
  for i in range(3):cnt[tuple(sorted((tuple(round(x,3) for x in t[i]),tuple(round(x,3) for x in t[(i+1)%3]))))]+=1
 return cnt
for name,v in list(meshes.items()):
 if name not in b['meshes']:continue
 old=np.array(b['meshes'][name]['faces']).reshape(-1,3,3);e=edges(v);oe=edges(old);cross=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);ocross=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);boundary=[k for k,c in e.items() if c==1]
 row={'name':name,'triangles':len(v),'degenerate':int((np.linalg.norm(cross,axis=1)<1e-8).sum()),'original_degenerate':int((np.linalg.norm(ocross,axis=1)<1e-8).sum()),'nonmanifold_edges':sum(c>2 for c in e.values()),'open_edges':len(boundary),'original_open_edges':sum(c==1 for c in oe.values()),'upward_cross':int((cross[:,1]>1e-5).sum()),'original_upward_cross':int((ocross[:,1]>1e-5).sum())}
 if name.startswith('Ground'):
  vflat=v.reshape(-1,3);oflat=old.reshape(-1,3);xmin,xmax=768,1536;zmin=-1536 if name.endswith('-2') else -2304;zmax=zmin+768
  # all four original boundary locations, including shared edge, remain horizontal-coordinate equivalent
  outer=lambda a:a[(abs(a[:,0]-xmin)<.03)|(abs(a[:,0]-xmax)<.03)|((abs(a[:,2]-zmin)<.03)&(abs(zmin+1536)>.03))|((abs(a[:,2]-zmax)<.03)&(abs(zmax+1536)>.03))]
  original=outer(oflat);new=outer(vflat);tree=cKDTree(new[:,[0,2]]);ds,idx=tree.query(original[:,[0,2]])
  row['boundary_horizontal_max_m']=float(ds.max());row['boundary_height_max_change_m']=float(abs(original[:,1]-new[idx,1]).max())
 out['meshes'].append(row)
# broad corridor follows actual asymmetric lake axis; record all obstructed samples for rejection
for z in range(-1050,-2131,-20):
 candidates=[(height(x,z),x) for x in range(1000,1241,10)];candidates=[q for q in candidates if q[0]!=None];h,x=min(candidates)
 out['corridor'].append({'x':x,'z':z,'highest_actual_surface':h,'submerged':h<-2})
for z in [-1100,-1300,-1536,-1750,-1950,-2100]:
 for x in [810,850,900,950,1000,1100,1200,1300,1400,1480,1510]:out['shore_samples'].append({'x':x,'z':z,'height':height(x,z)})
report=json.load(open(D+'/sculpt-report.json'));changed={(r['node'].replace('/Skyfarer/',''),r['index']):r for r in report['scatter']}
for group in b['scatter']:
 for rec in group['instances']:
  key=(group['node'].replace('/Skyfarer/',''),rec['index']);r=changed.get(key);x,y,z=r['new'] if r else rec['position'];h=height(x,z);out['scatter_support'].append({'node':key[0],'index':rec['index'],'height':h,'anchor_y':y,'gap':None if h==None else y-h,'changed':r is not None})
out['shared_edge_max_gap_m']=max(abs(height(x,-1536,['Ground_1_-2'])-height(x,-1536,['Ground_1_-3'])) for x in range(770,1535,5))
out['north_limit_probe']=[{'x':1070,'z':z,'height':height(1070,z)} for z in [-2130,-2150,-2170]]
path_samples=[]
for a,c in zip(out['corridor'],out['corridor'][1:]):
 for t in np.linspace(0,1,11):
  x=a['x']*(1-t)+c['x']*t;z=a['z']*(1-t)+c['z']*t;path_samples.append(height(x,z))
out['continuous_polyline_probe_count']=len(path_samples)
out['continuous_polyline_max_height']=max(path_samples)
out['corridor_all_submerged']=all(r['submerged'] for r in out['corridor']) and max(path_samples)<-2;json.dump(out,open(D+'/geometry-verification.json','w'),indent=2);print(json.dumps({k:v for k,v in out.items() if k in ['meshes','corridor_all_submerged']},indent=2))
