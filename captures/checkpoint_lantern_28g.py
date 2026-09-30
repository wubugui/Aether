from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-receiver-28g-20260908T162958Z-96465cbb463e4092a4227359c38c71f4'
prior=R/'captures/validation_runs/lantern-lighting-28f-20260908T162319Z-487bb5915c3e40169b6ec7339610e55e'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');assert m['passed'] and m['status']=='passed'
for name,row in m['artifacts'].items():assert sha(run/name)==row['sha256'],name
def pixels(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def diff(a,b):
    d=np.abs(a-b);mask=np.any(d>0,axis=2);ys,xs=np.where(mask)
    return {'changed_pixels':int(mask.sum()),'max_channel_difference':int(d.max()),'mean_absolute_channel_difference':float(d.mean()),'bbox':None if not mask.any() else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]}
views=[]
for view,old in [('reference','night-reference'),('lamp-close','night-lamp-close'),('beam-side','night-beam-side')]:
    ims={v:run/'images'/(view+'-'+v+'.png') for v in ['baseline','core-transmits','beam-boost']}
    data={v:read(Path(str(p)+'.json')) for v,p in ims.items()}
    for d in data.values():
        assert d['world_sha256']==sha(R/'scenes/world/World.tscn')
        assert d['camera']==data['baseline']['camera']
    arrays={k:pixels(p) for k,p in ims.items()}
    row={'view':view,'camera':data['baseline']['camera'],'baseline_vs_28f':diff(arrays['baseline'],pixels(prior/'images'/(old+'.png'))),'core_only_delta':diff(arrays['baseline'],arrays['core-transmits']),'beam_energy_only_delta':diff(arrays['core-transmits'],arrays['beam-boost']),'files':{k:{'path':str(p.relative_to(R)),'sha256':sha(p),'sidecar_sha256':sha(Path(str(p)+'.json')),'root_directly_viewed':k!='baseline'} for k,p in ims.items()}}
    if view=='lamp-close':row['core_only_lamp_frame_roi_620_360_1050_700']=diff(arrays['baseline'][360:700,620:1050],arrays['core-transmits'][360:700,620:1050])
    views.append(row)
assert sha(run/'images/final-beam-side.png')==sha(run/'images/beam-side-beam-boost.png')
out={'run_id':m['run_id'],'terminal_passed':True,'binding_count':len(m['artifacts']),'all_bound_sha256_verified':True,'manifest_sha256':sha(run/'manifest.json'),'views':views,'production_installed':False,'visual_acceptance':False,'full_goal_status':'active','scope':'Root directly viewed six core-transmits/beam-boost PNGs; three baseline images compared to previously directly viewed28f originals. Final-beam-side duplicate has exact PNG identity. One real scene, three cameras and three actual parameter states. Core caster A/B and beam energy A/B are separate.'}
(R/'reviews/round-28g-root-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'bindings':len(m['artifacts']),'views':[{k:r[k] for k in ['view','core_only_delta','beam_energy_only_delta']} for r in views]},ensure_ascii=False))
