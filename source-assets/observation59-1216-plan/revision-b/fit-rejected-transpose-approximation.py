from pathlib import Path
import numpy as np, json, math, hashlib
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parent;R=P.parents[2]
g=json.loads((P/'ship-static59.json').read_text());points=np.concatenate([np.array(x['vertices']) for x in g['rows']]);points=np.unique(points,axis=0);hull=ConvexHull(points);support=points[hull.vertices]
prop=np.concatenate([np.array(x['vertices']) for x in g['rows'] if '/Visuals/Propeller/' in x['path']]).mean(0)
env=np.array(next(x['vertices'] for x in g['rows'] if x['path'].endswith('/Envelope'))).mean(0)
old=json.loads((P.parent/'proposal.json').read_text());t=old['camera_transform'];basis=np.array(t[:9]).reshape(3,3).T;cam=np.array(t[9:]);aspect=1672/941;tan=math.tan(math.radians(62)/2);rect=np.array([[188/1672,266/941],[723/1672,692/941]]);target=(rect[0]+rect[1])/2;size=rect[1]-rect[0];rows=[]
for yaw in np.arange(0,360,2):
 a=math.radians(yaw);rot=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);local=support@rot.T@basis
 for depth in np.arange(22,70.001,.5):
  offset=np.array([(target[0]-.5)*2*depth*tan*aspect,(.5-target[1])*2*depth*tan,-depth])-local.mean(0)
  def project(pts):
   q=pts+offset
   return np.column_stack([.5+q[:,0]/(-2*q[:,2]*tan*aspect),.5-q[:,1]/(-2*q[:,2]*tan)])
  for _ in range(4):
   uv=project(local);center=(uv.min(0)+uv.max(0))/2;offset[0]+=(target[0]-center[0])*2*depth*tan*aspect;offset[1]-=(target[1]-center[1])*2*depth*tan
  uv=project(local);lo,hi=uv.min(0),uv.max(0);dim=hi-lo
  prop_env=project(np.array([prop,env])@rot.T@basis)
  if prop_env[0,0]>=prop_env[1,0]-.05 or lo.min()<.03 or hi.max()>.97:continue
  error=float(np.sum(np.log(dim/size)**2));rows.append({'yaw_degrees':float(yaw),'position_world':(cam+basis@offset).tolist(),'depth_m':float(depth),'projected_actual_vertex_bounds_uv':[lo.tolist(),hi.tolist()],'size_residual':(dim/size-1).tolist(),'score':error,'propeller_envelope_u':prop_env[:,0].tolist()})
rows.sort(key=lambda x:x['score']);best=rows[:8]
# The support hull has identical projection extrema for all-forward perspective.
for row in best:
 a=math.radians(row['yaw_degrees']);rot=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);q=(points@rot.T+np.array(row['position_world'])-cam)@basis;uv=np.column_stack([.5+q[:,0]/(-2*q[:,2]*tan*aspect),.5-q[:,1]/(-2*q[:,2]*tan)]);exact=np.array([uv.min(0),uv.max(0)]);row['full_vertex_extrema_hull_error']=float(np.max(abs(exact-np.array(row['projected_actual_vertex_bounds_uv']))));assert row['full_vertex_extrema_hull_error']<1e-10
out={'status':'CPU proposal only; actual runtime vertex/propeller pose and body/optical clearance untested','static_geometry_sha256':hashlib.sha256((P/'ship-static59.json').read_bytes()).hexdigest(),'mesh_count':g['mesh_count'],'stored_vertex_count':g['all_vertex_count'],'unique_vertices':len(points),'convex_support_vertices':len(support),'camera_and_scale_unchanged':True,'reference_rectangle':rect.tolist(),'best_eight':best,'pose_AABB_59A_visually_rejected':True,'notes':['Only existing unscaled geometry and yaw/translation searched','Bounds fit is not silhouette/reference acceptance','Static stored propeller angle differs from runtime0.35 pose; all original full-spin envelope must be tested','Do not resize hull to hide residuals before actual view and source identity are checked']};(P/'exact-proposal59b.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['best_eight'][0],indent=2));print('support',len(support),'vertices',len(points))
