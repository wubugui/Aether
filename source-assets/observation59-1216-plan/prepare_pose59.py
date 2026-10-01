from pathlib import Path
import json,hashlib,itertools,math
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
ref=ROOT/'ref/1216.png';width,height=Image.open(ref).size
prior=ROOT/'cloud-evidence/near-ship53west-v2-renderer-20261001T072841Z-i9rjqlen/images/near-ship-report.json'
assert hashlib.sha256(prior.read_bytes()).hexdigest()=='fefe96426b846e92c17120a97b752757273d59d19eb7b88a85a26d4063887dac'
aabb=np.array([-7.388751,-4.837,-5.499367]);size=np.array([17.13647,16.75201,10.9737]);corners=np.array([aabb+size*np.array(v) for v in itertools.product([0,1],repeat=3)])
report=ROOT/'cloud-evidence/cloudsea52h-d-ab-front-20261001T102736Z-svczz9fo/images/report.json';capture=json.loads(report.read_text())['captures'][0];t=capture['camera_transform'];R=np.array(t[:9]).reshape(3,3).T;cam=np.array(t[9:]);aspect=1672/941;tan=math.tan(math.radians(62)/2)
target=np.array([[188/width,266/height],[723/width,692/height]]);tc=target.mean(axis=0);ts=target[1]-target[0];rows=[]
for yaw in np.linspace(105,160,111):
 angle=math.radians(yaw);rot=np.array([[math.cos(angle),0,math.sin(angle)],[0,1,0],[-math.sin(angle),0,math.cos(angle)]]);pts=corners@rot.T@R
 for depth in np.linspace(25,70,181):
  offset=np.array([(tc[0]-.5)*2*depth*tan*aspect,(.5-tc[1])*2*depth*tan,-depth])-pts.mean(axis=0)
  for _ in range(3):
   q=pts+offset;uv=np.column_stack([.5+q[:,0]/(-2*q[:,2]*tan*aspect),.5-q[:,1]/(-2*q[:,2]*tan)])
   mid=(uv.min(axis=0)+uv.max(axis=0))/2;offset[0]+=(tc[0]-mid[0])*2*depth*tan*aspect;offset[1]-=(tc[1]-mid[1])*2*depth*tan
  q=pts+offset;uv=np.column_stack([.5+q[:,0]/(-2*q[:,2]*tan*aspect),.5-q[:,1]/(-2*q[:,2]*tan)])
  bounds=np.array([uv.min(axis=0),uv.max(axis=0)]);sz=bounds[1]-bounds[0];error=float(np.sum(np.log(sz/ts)**2));pos=cam+R@offset
  rows.append({'yaw_degrees':float(yaw),'position_world':pos.tolist(),'depth_m':float(depth),'projected_aabb_uv':bounds.tolist(),'size_relative_error':(sz/ts-1).tolist(),'score':error})
rows.sort(key=lambda x:x['score']);j={'status':'CPU-only AABB proposal; NOT renderer, silhouette, mesh, occlusion or physics accepted','reference_size_actual':[width,height],'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'approximate_reference_ship_bounds_px':[188,266,723,692],'measurement_uncertainty_px':8,'method':'Actual original pixels visually inspected, manually estimated full ship including flag/propeller; not automatic segmentation','camera_transform':t,'camera_fov':62,'logical_aspect':aspect,'ship_scale_unchanged':True,'candidate_scene_changed':False,'best_five':rows[:5],'requirements':['Verify actual same hull mesh/resource identity in52f before using prior AABB','AABB includes empty corners and does not certify silhouette fit','Runtime full mesh/propeller envelope, optical-cloud outside/inside, physical clearance required','A/A2 exact state and pixel restoration, F2 continuity before any saved preset','Keep all camera/ship changes out of58 geometry experiment'],'rejected_initial_record':'proposal-rejected-wrong-reference-width.json used1664 not actual1672; preserved as invalid, not implementation'}
(OUT/'proposal.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(rows[0],indent=2))
