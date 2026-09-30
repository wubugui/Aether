from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];run=R/'captures/validation_runs/lantern-receiver-28g-20260908T162958Z-96465cbb463e4092a4227359c38c71f4';prior=R/'captures/validation_runs/lantern-lighting-28f-20260908T162319Z-487bb5915c3e40169b6ec7339610e55e'
m=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert m['passed'] and m['status']=='passed'
def load(p):return np.array(Image.open(p).convert('RGB')).astype(np.int16)
def diff(a,b):
 d=a-b;mask=np.any(d!=0,axis=2);y,x=np.where(mask)
 return {'changed_pixels':int(mask.sum()),'max_abs_channel_difference':int(np.abs(d).max()),'abs_difference_sum':int(np.abs(d).sum()),'pixels_abs_difference_gt10':int((np.max(np.abs(d),axis=2)>10).sum()),'bbox_xyxy':None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]}
rois={'lamp-close':{'core':[787,424,864,527],'left_glass_receiver':[716,385,771,570],'right_glass_receiver':[904,385,946,559],'balcony_front_receiver':[696,614,984,680],'roof_receiver':[780,280,920,346],'tower_receiver':[802,757,882,910]},'reference':{'foreground_lantern':[289,536,352,610],'foreground_tower':[310,635,353,765],'middle_lantern':[1006,535,1041,570]},'beam-side':{'tower_a':[472,414,495,457],'island_a_house':[426,449,465,481],'tower_d':[708,428,732,476]}}
out={'run':run.name,'scope':'Independent saved PNG A/B decode and direct review; no new GPU run. ROIs are explicit image coordinates of visually selected lamp/receiver regions, not perfect object masks.','views':[]}
for view,old_name in [('reference','night-reference'),('lamp-close','night-lamp-close'),('beam-side','night-beam-side')]:
 paths={v:run/'images'/(view+'-'+v+'.png') for v in ['baseline','core-transmits','beam-boost']};arr={v:load(p) for v,p in paths.items()}
 row={'view':view,'artifacts':{},'core_off_vs_baseline':diff(arr['core-transmits'],arr['baseline']),'boost_vs_core_off':diff(arr['beam-boost'],arr['core-transmits']),'baseline_vs28f':diff(arr['baseline'],load(prior/'images'/(old_name+'.png'))),'receiver_rois':{}}
 for v,p in paths.items():
  j=json.loads(Path(str(p)+'.json').read_text(encoding='utf-8'));assert j['run_id']==run.name;assert len(j['core_nodes'])==4;assert all(c['bounds_contains_light_origin'] and c['cast_shadow']==(1 if v=='baseline' else 0) for c in j['core_nodes']);assert all(abs(b['energy']-(1.3 if v=='beam-boost' else .65))<1e-6 for b in j['beam_states'])
  row['artifacts'][v]={'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'camera':j['camera'],'core_shadow_states':[c['cast_shadow'] for c in j['core_nodes']],'beam_energies':[b['energy'] for b in j['beam_states']]}
 for name,box in rois[view].items():
  x0,y0,x1,y1=box;row['receiver_rois'][name]={'xyxy':box,'core_off_vs_baseline':diff(arr['core-transmits'][y0:y1,x0:x1],arr['baseline'][y0:y1,x0:x1]),'boost_vs_core_off':diff(arr['beam-boost'][y0:y1,x0:x1],arr['core-transmits'][y0:y1,x0:x1]),'baseline_vs28f':diff(arr['baseline'][y0:y1,x0:x1],load(prior/'images'/(old_name+'.png'))[y0:y1,x0:x1])}
 out['views'].append(row)
out['verdict']='Beam-only energy1.3 is a useful local readability improvement; no demonstrated native receiver-light benefit from core shadow OFF in these samples; full reference appearance remains unaccepted.'
(R/'reviews/round-28g-lantern-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for row in out['views']:
 print(row['view'],json.dumps({k:row[k] for k in ['core_off_vs_baseline','boost_vs_core_off','baseline_vs28f','receiver_rois']},indent=2))
