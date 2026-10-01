import json,math,collections,hashlib,os
import numpy as np
D=os.path.dirname(__file__);P=json.load(open(D+'/lake49-payload.json'));OLD=json.load(open(D+'/../lake48/lake48-payload.json'));SUP=json.load(open(D+'/../lake48/support47.json'))
terrain={m['name']:np.array(m['vertices']).reshape(-1,3,3) for m in OLD['meshes']}
for n,m in SUP['meshes'].items():
 if n not in terrain:terrain[n]=np.array(m['faces']).reshape(-1,3,3)
terr=np.concatenate(list(terrain.values()));allnew=np.concatenate([np.array(m['vertices']).reshape(-1,3,3) for s in P['islands'] for m in s['meshes']]);collision=np.concatenate([np.array(m['vertices']).reshape(-1,3,3) for s in P['islands'] for m in s['meshes'] if m['collision']])

def height(tri,x,z,top=True):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2]);valid=abs(den)>1e-8;den=np.where(valid,den,1);u=((b[:,2]-c[:,2])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,2]))/den;v=((c[:,2]-a[:,2])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,2]))/den;ww=1-u-v;valid &= (u>=-1e-6)&(v>=-1e-6)&(ww>=-1e-6)
 y=u*a[:,1]+v*b[:,1]+ww*c[:,1]
 if valid.any():return float(y[valid].max() if top else y[valid].min())
 return None

def pointdist(tri,p):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];ab=b-a;ac=c-a;ap=p-a;norm=np.cross(ab,ac);nn=(norm*norm).sum(1);dot=(ap*norm).sum(1);q=ap-norm*(dot/np.maximum(nn,1e-20))[:,None];uu=(ab*ab).sum(1);uv=(ab*ac).sum(1);vv=(ac*ac).sum(1);uq=(ab*q).sum(1);vq=(ac*q).sum(1);den=uu*vv-uv*uv;u=(uq*vv-vq*uv)/np.maximum(den,1e-20);v=(vq*uu-uq*uv)/np.maximum(den,1e-20);inside=(u>=0)&(v>=0)&(u+v<=1)&(nn>1e-16);best=np.where(inside,dot*dot/np.maximum(nn,1e-20),np.inf)
 for x,y in [(a,b),(b,c),(c,a)]:
  d=y-x;t=np.clip(((p-x)*d).sum(1)/np.maximum((d*d).sum(1),1e-20),0,1);sq=((p-x-d*t[:,None])**2).sum(1);best=np.minimum(best,sq)
 return math.sqrt(float(best.min()))

cameras=[{'name':'1128','position':[1150,10,-1000],'target':[1150,160,-2600],'fov':64},{'name':'1129','position':[1300,7,-950],'target':[1000,120,-2400],'fov':66}]
routes=[{'name':'1128-lateral150','start':[1150,10,-1000],'end':[1300,10,-1000]},{'name':'1128-approach200','start':[1150,10,-1000],'end':[1150,28.668,-1199.127]},{'name':'1129-lateral150','start':[1300,7,-950],'end':[1446.889,7,-980.391]},{'name':'1129-approach200','start':[1300,7,-950],'end':[1259.596,22.219,-1145.284]}]
out={'hardware_gpu_acceptance':False,'reference_visual_acceptance':False,'cameras':cameras,'islands':[],'route_clearances':[]}
for island in P['islands']:
 row={'name':island['name'],'projections':{},'trees':[]};geo=np.array([v for m in island['meshes'] for v in m['vertices']]);rock=np.array([v for m in island['meshes'] if m['role'] in ['rockroot','shoulder','wetshore','grasscap'] for v in m['vertices']]);row['world_bounds']=[geo.min(0).tolist(),geo.max(0).tolist()]
 for cam in cameras:
  p=np.array(cam['position']);f=np.array(cam['target'])-p;f=f/np.linalg.norm(f);r=np.cross(f,[0,1,0]);r/=np.linalg.norm(r);u=np.cross(r,f);s=332/math.tan(math.radians(cam['fov']/2));bb={}
  for label,a in [('all_above_water',geo),('rockshore_above_water',rock)]:
   v=a[a[:,1]>=0]-p;depth=v@f;v=v[depth>0];depth=depth[depth>0];x=590+s*(v@r)/depth;y=332-s*(v@u)/depth;bb[label]={'bbox':[float(x.min()),float(y.min()),float(x.max()),float(y.max())],'visible_width_px':float(max(0,min(1180,x.max())-max(0,x.min()))),'left_clipped':bool(x.min()<0),'fully_offscreen':bool(x.max()<0 or x.min()>1180)}
  row['projections'][cam['name']]=bb
 root=next(m for m in island['meshes'] if m['role']=='rockroot');rt=np.array(root['vertices']).reshape(-1,3,3);v=rt.reshape(-1,3);burials=[]
 for x in np.arange(v[:,0].min(),v[:,0].max()+.1,1.0):
  for z in np.arange(v[:,2].min(),v[:,2].max()+.1,1.0):
   floor=height(rt,x,z,False)
   if floor is not None and floor<-3:burials.append(height(terr,x,z)-floor)
 row['root_dense_burial']={'samples':len(burials),'min_m':min(burials),'max_m':max(burials),'all_1_to_2m':min(burials)>=1 and max(burials)<=2}
 for t in island['trees']:
  x,y,z=t['foot_world'];support=next(m for m in island['meshes'] if m['name']==t['support_mesh']);h=height(np.array(support['vertices']).reshape(-1,3,3),x,z);trunk=next(m for m in island['meshes'] if m['name']==t['trunk_mesh']);lo=np.array(trunk['vertices'])[:,1].min();row['trees'].append({'name':t['name'],'actual_support_y':h,'foot_y':y,'residual_m':y-h,'trunk_lowest_y':float(lo),'trunk_burial_m':y-float(lo)})
 out['islands'].append(row)
for route in routes:
 a,b=np.array(route['start']),np.array(route['end']);length=np.linalg.norm(b-a);steps=math.ceil(length/.5);samples=[pointdist(allnew,a+(b-a)*s/steps) for s in range(steps+1)];route['all_new_mesh_distance_lower_bound_m']=min(samples)-.25;route['sampling_interval_max_m']=.5;route['at_least_10m_clearance']=min(samples)-.25>=10;out['route_clearances'].append(route)
# Explicit curved corridor, not a falsely asserted straight north channel.
waypoints=[[1100,-1080],[1125,-1530],[1125,-1730],[1100,-1850],[1070,-2090]];samples=[]
for a,b in zip(waypoints,waypoints[1:]):
 a=np.array(a);b=np.array(b);steps=math.ceil(np.linalg.norm(b-a)/3)
 for t in np.linspace(0,1,steps+1):
  x,z=a*(1-t)+b*t
  for dx in [-10,0,10]:
   old=height(terr,x+dx,z);new=height(collision,x+dx,z);h=max([v for v in [old,new] if v is not None]);samples.append({'x':x+dx,'z':z,'highest_solid_y':h})
out['curved_water_corridor']={'waypoints_xz':waypoints,'width_m':20,'probe_count':len(samples),'max_highest_solid_y':max(s['highest_solid_y'] for s in samples),'all_submerged_at_least_2m':max(s['highest_solid_y'] for s in samples)<-2,'samples':samples}
P['cameras']=cameras;P['routes']=routes;P['nearshore_cameras']=[{'name':s['name']+'-near','position':[s['anchor'][0],16,s['anchor'][2]+max(30,s['size'][1]*1.6)],'target':[s['anchor'][0],4,s['anchor'][2]],'fov':64} for s in P['islands']]
json.dump(P,open(D+'/lake49-payload.json','w'));json.dump(out,open(D+'/geometry-verification.json','w'),indent=2)
print(json.dumps({**out,'curved_water_corridor':{k:v for k,v in out['curved_water_corridor'].items() if k!='samples'}},indent=2))
