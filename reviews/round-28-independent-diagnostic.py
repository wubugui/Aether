from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
root=Path(__file__).resolve().parents[1]
run=root/'captures/validation_runs/lantern-diagnostic-28c-20260908T160251Z-c743ec0d33cd491f939180c70c5dd7bf'
base=np.array(Image.open(run/'images/night-reference.png').convert('RGB')).astype(np.int16)
data={'run':run.name,'layers':[]}
for p in sorted((run/'images').glob('*debug*.png')):
 a=np.array(Image.open(p).convert('RGB')).astype(np.int16);d=a-base;mask=np.any(d!=0,axis=2);ys,xs=np.where(mask)
 item={'file':str(p.relative_to(root)),'different_pixels':int(mask.sum()),'rgb_sha256':hashlib.sha256(a.astype(np.uint8).tobytes()).hexdigest(),'max_abs_difference':int(np.abs(d).max()),'absolute_difference_sum':int(np.abs(d).sum()),'bbox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]}
 data['layers'].append(item)
(root/'reviews/round-28-independent-diagnostic.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data,indent=2))
run_d=root/'captures/validation_runs/lantern-diagnostic-28d-20260908T161054Z-dc3055c6b50e4023ac0899b86acd1cd3'
normal=np.array(Image.open(run_d/'images/night-reference.png').convert('RGB')).astype(np.int16)
data['28d']={'run':run_d.name,'comparisons':[]}
for mode in (1,5):
 p=run_d/('images/night-reference-debug-'+str(mode)+'.png');a=np.array(Image.open(p).convert('RGB')).astype(np.int16);d=a-normal;mask=np.any(d!=0,axis=2)
 data['28d']['comparisons'].append({'debug_mode':mode,'different_pixels':int(mask.sum()),'max_abs_difference':int(np.abs(d).max()),'absolute_difference_sum':int(np.abs(d).sum()),'pixels_abs_difference_gt_10':int((np.max(np.abs(d),axis=2)>10).sum()),'rgb_sha256':hashlib.sha256(a.astype(np.uint8).tobytes()).hexdigest()})
data['cause']='Godot 4.5.1-stable GLES3 scene.glsl lines2134-2144 selects ALBEDO only under MODE_UNSHADED. Existing beam shader ALBEDO zero and EMISSION color contributes black additive RGB. Debug5 ALBEDO-only renders broad orange cone volumes and halos.'
data['official_renderer_source']='https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/drivers/gles3/shaders/scene.glsl'
(root/'reviews/round-28-independent-diagnostic.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data['28d'],indent=2))
