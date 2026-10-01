import json,re,math,hashlib
from pathlib import Path
import numpy as np
ROOT=Path('/workspace/scratch/a29d03198654/Aether');D=ROOT/'source-assets/lake-rim53';O=D/'revision-d'
source=ROOT/'cloud-evidence/rim53b-world-diagnostic-20261001T052441Z-zv0suI/images/diagnostic-report.json';j=json.loads(source.read_text())
cameras={}
for cap in j['captures']:
 st=cap['reflection'];rows=[list(map(float,a.split(','))) for a in re.findall(r'\(([^)]+)\)',st['primary_transform'])]
 proj=[list(map(float,a.split(','))) for a in re.findall(r'\(([^)]+)\)',st['projection'])]
 cameras[cap['reference']]={'origin':rows[3],'basis_columns':rows[:3],'projection_x':proj[0][0]*st['optical_overscan'],'projection_y':proj[1][1]*st['optical_overscan'],'size':cap['size'],'keep_aspect':st['keep_aspect'],'fov':cap['fov'],'source_primary_transform':st['primary_transform'],'source_reflection_projection':st['projection'],'optical_overscan':st['optical_overscan']}
def project(p,cam):
 B=np.column_stack(cam['basis_columns']);a=(np.asarray(p)-np.array(cam['origin']))@B;depth=-a[...,2]
 return np.stack([.5+.5*a[...,0]/depth*cam['projection_x'],.5-.5*a[...,1]/depth*cam['projection_y']],axis=-1)
rows=[]
for rev in ['revision-b','revision-c','revision-d']:
 data=json.loads((D/rev/'rim53-payload.json').read_text());f=np.array(data['mountains'][0]['collision_vertices']);f=np.unique(f,axis=0)
 q=f[np.argmax(f[:,1])];r={'revision':rev,'highest_world_vertex':q.tolist(),'references':{}}
 for ref,cam in cameras.items():
  xy=project(f,cam);ii=np.argmin(xy[:,1]);inside=(xy[:,0]>=0)&(xy[:,0]<=1);chosen=np.where(inside)[0];iii=chosen[np.argmin(xy[chosen,1])]
  r['references'][ref]={'highest_world_vertex_projection_normalized':project(q,cam).tolist(),'uppermost_projected_vertex_world':f[ii].tolist(),'uppermost_projected_vertex_normalized':xy[ii].tolist(),'uppermost_inside_vertex_world':f[iii].tolist(),'uppermost_inside_vertex_normalized':xy[iii].tolist()}
 rows.append(r)
report={'actual_runtime_report':str(source.relative_to(ROOT)),'actual_runtime_report_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Use the recorded actual optical camera transforms. Recover main projection diagonal by multiplying recorded reflection projection by its1.08 optical overscan. The basis values in runtime text are rounded to6decimals; this analysis predicts projection, not occlusion or graphical acceptance. The next diagnostic records main get_camera_projection and engine unproject_position directly.','approximate_reference_image_anchors':{'1128':{'pixel':[82,278],'image_size':[1672,941],'note':'Visually identified left peak apex, approximate, not a calibrated world correspondence.'},'1129':{'pixel':[94,281],'image_size':[1672,941],'note':'Visually identified left peak apex, approximate; do not assert it is the exact same world point as1128.'}},'cameras':cameras,'candidate_vertex_projections':rows,'selected_design':{'main_rock_crest':[245,323.5,-1880],'north_rock_crest':[222,283,-2045],'basis':'The visible silhouette problem is the closer southern shoulder, not merely the highest world-space vertex. Move the nearer crest about70–97m north and reshape its height to place the snowy main apex inside original1128 at roughly5% width/30% height. Reduce the farther crest to a secondary shoulder. Retain the same dry footprint and actual buildings.','remaining_gap':'Projected1129 peak remains farther right/lower than the approximate reference left apex. No claim of matching one mountain to both reference peak anchors; wider surrounding ridge composition remains incomplete.'},'graphical_acceptance':False}
json.dump(report,open(O/'projection-analysis.json','w'),indent=2)
for row in rows:
 print(row['revision'],row['highest_world_vertex'])
 for ref,q in row['references'].items():print(ref,q['uppermost_projected_vertex_normalized'],q['uppermost_projected_vertex_world'])
