"""Bind the completed27c/d local study evidence; no automatic art acceptance."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
label=sys.argv[1];run=R/'captures/validation_runs'/sys.argv[2]
out=R/'reviews'/('round-'+label+'-root-evidence.json');assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
samples=[('night-reference',0),('night-reverse',0),('day-reference',0),('night-reference-later',18)]
if label=='27d':samples.append(('day-cloud-back',0))
assert m['status']=='passed' and m['passed'] and len(m['stages'])==len(samples)
for name,record in m['artifacts'].items():assert sha(run/name)==record['sha256'],name
views=[]
for name,t in samples:
    p=run/'images'/(name+'.png');side=p.with_suffix('.png.json')
    d=json.loads(side.read_text(encoding='utf-8'));e=d['environment_study']
    assert e['sampled_world_time']==t
    assert d['world_sha256']==sha(R/'scenes/world/World.tscn')
    views.append({'name':name,'image':str(p.relative_to(R)),'image_sha256':sha(p),'sidecar_sha256':sha(side),'camera':d['camera'],'reported_world_time':t,'native_sky_asset_count':len(e['native_sky_assets']),'root_directly_viewed':True})
a=np.asarray(Image.open(run/'images/night-reference.png').convert('RGB')).astype(np.int16)
b=np.asarray(Image.open(run/'images/night-reference-later.png').convert('RGB')).astype(np.int16)
assert a.shape==b.shape
diff=np.abs(a-b)
regions={}
for name,(x0,y0,x1,y1) in {'open_water_patch':(1120,760,1220,890),'upper_sky_control':(10,10,600,100)}.items():
    d=diff[y0:y1,x0:x1]
    regions[name]={'pixel_rectangle':[x0,y0,x1,y1],'changed_pixels':int(np.count_nonzero(np.max(d,axis=2))),'total_pixels':int(d.shape[0]*d.shape[1]),'mean_absolute_channel_difference_255':float(d.mean()),'max_absolute_channel_difference_255':int(d.max())}
result={'run_id':m['run_id'],'run_terminal_passed':True,'manifest_sha256':sha(run/'manifest.json'),'binding_count':len(m['artifacts']),'all_artifact_sha256_verified':True,'views':views,'time_sample_comparison':regions,'scope':'Actual GPU samples and frozen artifact identities only. Time-separated stills establish a changing sampled water pattern, not smooth animation quality or full weather. Prior26b geometry not resampled. Root direct-view field is written only after every listed actual image was inspected.','visual_acceptance':False,'production_installed':False,'full_goal_status':'active'}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(out),'bindings':len(m['artifacts']),'time_comparison':regions},ensure_ascii=False))
