from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-lighting-28f-20260908T162319Z-487bb5915c3e40169b6ec7339610e55e'
prior=R/'captures/validation_runs/lantern-lighting-28e-20260908T161327Z-30f38fcb128c469db1a26b76deef33dd'
m=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert m['passed'] and m['status']=='passed'
data={'run':run.name,'verdict':'Retain local numerical and density-profile improvement; reference visual acceptance rejected','scope':'Independent direct review of five original28f GPU images against28e and original1342; no rendering launched or implementation modified','images':[]}
for name in ['night-reference','night-beam-side','night-lamp-close','night-reverse','day-reference']:
 p=run/'images'/(name+'.png');q=Path(str(p)+'.json');j=json.loads(q.read_text(encoding='utf-8'));assert j['run_id']==run.name
 old=prior/'images'/(name+'.png');a=np.array(Image.open(p).convert('RGB')).astype(np.int16);b=np.array(Image.open(old).convert('RGB')).astype(np.int16);d=a-b
 beam_count=len(j['lantern_lighting']['beams']);assert beam_count==(0 if name.startswith('day') else 4)
 data['images'].append({'view':name,'image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sidecar_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'camera':j['camera'],'actual_beams':beam_count,'world_sha256':j['world_sha256'],'prior28e_difference':{'changed_pixels':int(np.any(d!=0,axis=2).sum()),'max_abs_channel_difference':int(np.abs(d).max()),'identical_png_bytes':p.read_bytes()==old.read_bytes()}})
data['verified_local_improvements']=['ALBEDO output repair remains effective.','Broad far-end orange pools from28e are much reduced in actual reference, side and close views.','Beams remain associated with world-space lighthouse directions and continuous near-source wedges are more legible than28e in side/reference views.','Night warm core/halo remains; day has zero beam instances and no added volume field.']
data['rejected_or_unproven']=['Reference1342 beam is stronger and grows from a much brighter warm lamp;28f remains too faint against the dark water.','Native receiver lighting self-shadow hypothesis is unproven until controlled28g comparison.','No full dynamic weather/rotation/flight or complete camera/light-space occlusion acceptance.','Cloud, water, rock/island shapes and village density remain materially unlike1342; full world goal remains active.']
data['core_shadow_hypothesis']={'source_center_y_m':19.6,'source_radius_m':.3,'source_height_m':1.38,'native_light_origin_inside_authored_core':True,'native_receiver_effect':'Plausible; not proven by enclosure alone','direct_volume_effect':'Core cast_shadow flag does not directly drive unshaded beam shader or its separate CPU collision map; own tower is excluded from that map'}
(R/'reviews/round-28f-lantern-independent-review.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({'run':run.name,'images':len(data['images']),'day_difference':data['images'][-1]['prior28e_difference'],'verdict':data['verdict']},indent=2))
