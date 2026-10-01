import json,numpy as np,math
R='/workspace/scratch/a29d03198654/Aether';scope={};exec(open(R+'/source-assets/lake48/verify_geometry.py').read().split('for name,v in list(meshes.items()):')[0],scope)
height=scope['height'];p=json.load(open(R+'/source-assets/lake49/lake49-payload.json'));tris=[];labels=[]
for island in p['islands']:
 for m in island['meshes']:
  t=np.array(m['vertices']).reshape(-1,3,3);tris.append(t);labels.extend([m['name']]*len(t))
T=np.concatenate(tris);labels=np.array(labels);E1=T[:,1]-T[:,0];E2=T[:,2]-T[:,0]
O=np.array([1150.,10.,-1000.]);F=np.array([0.,150.,-1600.]);F/=np.linalg.norm(F);RIGHT=np.cross(F,[0,1,0]);RIGHT/=np.linalg.norm(RIGHT);UP=np.cross(RIGHT,F)
def probe(px,py):
 d=F+RIGHT*((2*(px+.5)/1180-1)*(1180/664)*math.tan(math.radians(32)))+UP*((1-2*(py+.5)/664)*math.tan(math.radians(32)));d/=np.linalg.norm(d);water=O+d*(-O[1]/d[1]);h=height(water[0],water[2]);q=np.cross(np.broadcast_to(d,E2.shape),E2);det=np.sum(E1*q,axis=1);valid=abs(det)>1e-9;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);tv=O-T[:,0];u=np.sum(tv*q,axis=1)*inv;qq=np.cross(tv,E1);v=np.sum(qq*d,axis=1)*inv;t=np.sum(E2*qq,axis=1)*inv;valid&=(u>=0)&(v>=0)&(u+v<=1)&(t>0);t=np.where(valid,t,np.inf);i=np.argmin(t)
 if not np.isfinite(t[i]):return {'pixel':[px,py],'water_point':water.tolist(),'vertical_lake_depth':-h if h is not None else None,'ray_hit':None}
 hit=O+d*t[i];return {'pixel':[px,py],'water_point':water.tolist(),'vertical_lake_depth':-h if h is not None else None,'ray_hit':labels[i],'hit_point':hit.tolist(),'shader_screen_depth_approx':max(0,-hit[1]),'xz_mismatch_m':float(np.linalg.norm((hit-water)[[0,2]]))}
rows=[probe(x,y) for x,y in [(980,474),(980,485),(980,497),(980,510),(200,426),(200,435),(200,447)]]
json.dump({'scope':'Analytic camera rays using fixed1128 pose/FOV and actual saved49 source triangles; no rendered depth-buffer readback. Confirms screen ray sidewall depth is not vertical water-column depth at same XZ.','probes':rows},open(R+'/cloud-evidence/reflection50-material-intake/root-depth-ray-probes.json','w'),indent=2)
print(json.dumps(rows,indent=2))
