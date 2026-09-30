from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-lighting-28h-20260908T163354Z-e69c09f62fc547389d39adbbd0011225'
prior=R/'captures/validation_runs/lantern-receiver-28g-20260908T162958Z-96465cbb463e4092a4227359c38c71f4'
basis=R/'captures/validation_runs/lantern-lighting-28f-20260908T162319Z-487bb5915c3e40169b6ec7339610e55e'
m=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert m['passed'] and m['status']=='passed'
out={'run':run.name,'local_acceptance':True,'local_acceptance_scope':'Retain visible world-space lantern beam implementation, improved finite-interval sampling/distance profile and energy1.3 with original core shadow casters ON. This accepts a useful local study basis, not finished reference fidelity or production integration.','full_reference_acceptance':False,'full_world_acceptance':False,'directly_viewed_originals':[],'unchanged_basis_artifacts':[]}
for name in ['lantern_volume.gdshader','lantern_beam.glb','lantern_halo.glb']:
 p=run/'study-inputs/lantern-optics'/name;q=basis/'study-inputs/lantern-optics'/name
 assert p.read_bytes()==q.read_bytes();out['unchanged_basis_artifacts'].append({'file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for view in ['reference','lamp-close','beam-side']:
 p=run/'images'/(view+'-beam-only.png');q=Path(str(p)+'.json');j=json.loads(q.read_text(encoding='utf-8'));assert j['run_id']==run.name and j['variant']=='beam-only';assert len(j['core_nodes'])==4 and len(j['beam_states'])==4;assert all(c['cast_shadow']==1 for c in j['core_nodes']);assert all(abs(b['energy']-1.3)<1e-6 for b in j['beam_states'])
 old=prior/'images'/(view+'-beam-boost.png');a=np.array(Image.open(p).convert('RGB')).astype(np.int16);b=np.array(Image.open(old).convert('RGB')).astype(np.int16);d=a-b
 out['directly_viewed_originals'].append({'view':view,'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sidecar_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'camera':j['camera'],'actual_core_shadow_enums':[c['cast_shadow'] for c in j['core_nodes']],'actual_beam_energies':[b['energy'] for b in j['beam_states']],'world_sha256':j['world_sha256'],'versus28g_boost':{'changed_pixels':int(np.any(d!=0,axis=2).sum()),'max_channel_difference':int(np.abs(d).max()),'pixels_max_difference_gt10':int((np.max(np.abs(d),axis=2)>10).sum())}})
out['findings']=['All three actual originals retain the readable fixed world-space beams without28e detached far orange pools.','Close lamp retains warm core/glass and opaque roof/frame silhouette in front of distant haze.','Original core casters are ON as intended; unsupported core-OFF receiver repair is not retained.','Lamp focal brightness and native nearby receiver illumination remain weaker than original1342; whole scene has substantial water/cloud/rock/settlement gaps.','No claim of full dynamic weather, beam rotation, continuous flight, warm water reflection or all-angle/thin-object shadow acceptance.']
(R/'reviews/round-28h-lantern-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'run':run.name,'local_acceptance':out['local_acceptance'],'full_reference_acceptance':False,'views':[{'view':x['view'],'versus28g_boost':x['versus28g_boost']} for x in out['directly_viewed_originals']]},indent=2))
