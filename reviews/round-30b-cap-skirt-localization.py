from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
P=R/'captures/lantern_island_study_30b'
e=json.loads((P/'geometry-evidence.json').read_text())
o=e['new']['island_c grass and exposed rock terrain'];v=np.array(o['vertices']);n=len(v)//2
faces=[(i,f) for i,f in enumerate(o['polygons']) if any(j<n for j in f) and any(j>=n for j in f)]
run=R/'captures/validation_runs/lantern-island-30b-20260908T181107Z-79169d5784aa499ea0429f797ff3fc6e'
im=run/'images/day-c-front.png';side=json.loads(im.with_suffix('.png.json').read_text());w,h=Image.open(im).size
camera=np.array(side['camera']['position'])-[-3050,0,-2650];camera=np.array([camera[0],-camera[2],camera[1]])
forward=np.array([0,0,10])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);focal=(h/2)/math.tan(math.radians(side['camera']['fov']/2))
def project(q):
 d=q-camera;depth=np.dot(d,forward);return [w/2+np.dot(d,right)*focal/depth,h/2-np.dot(d,up)*focal/depth]
rows=[{'source_face':i,'indices':f,'screen_xy':[project(v[j]) for j in f]} for i,f in faces]
out={'source':str((P/'geometry-evidence.json').relative_to(R)),'source_sha256':hashlib.sha256((P/'geometry-evidence.json').read_bytes()).hexdigest(),'image':str(im.relative_to(R)),'image_sha256':hashlib.sha256(im.read_bytes()).hexdigest(),'resolution':[w,h],'projection_method':'Actual sidecar camera position/FOV; local C target (0,10,0) Godot from driver; perspective vertical FOV, no pixel segmentation or controlled isolated-material render.','top_bottom_xy_exact':bool(np.array_equal(v[:n,:2],v[n:,:2])),'thickness_min_max_m':[float(x) for x in [np.min(v[:n,2]-v[n:,2]),np.max(v[:n,2]-v[n:,2])]],'skirt_source_faces':rows,'interpretation':'Unchanged constant-thickness terrain perimeter is still present in 30b and projects at the visible narrow ring. Core has no middle-ring edges. Geometry plus original image supports attribution to this collar, but the proposed weld needs its own real render to demonstrate removal.'}
(R/'reviews/round-30b-cap-skirt-localization.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'skirt_faces':len(rows),'thickness':out['thickness_min_max_m'],'screen_samples':rows[:3]},indent=2))
