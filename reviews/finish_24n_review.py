from pathlib import Path
import json,hashlib
R=Path(r'E:\FeiTing');p=R/'reviews/round-24n-village-paving-independent-review.json';d=json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gate=json.loads((R/'reviews/round-24m-village-paving-native-check.json').read_text());d['reopened_native_gate']={'passed':gate['passed'],'assets':[]}
for g in d['groups']:
    a=next(a for a in gate['assets'] if a['asset']=='village_'+g['name']);root=R/'captures/village_paving_study_24m'
    d['reopened_native_gate']['assets'].append({'name':g['name'],'glb_identity_matches':g['glb_sha256']==a['glb_sha256'],'blend_identity_matches':sha(root/(a['asset']+'.blend'))==a['source_sha256'],'parts':len(a['parts'])})
run=R/'captures/validation_runs/village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7';m=json.loads((run/'manifest.json').read_text());d['gpu_run']={'run_id':m['run_id'],'status':m['status'],'passed':m['passed'],'images':[],'frozen_asset_identities':[]}
for image in sorted((run/'images').glob('*.png')):
    a=json.loads(image.with_suffix('.png.json').read_text());v=a['village_paving_study'];d['gpu_run']['images'].append({'name':image.name,'sha256':sha(image),'run_id':a['run_id'],'paving_passed':v['passed'],'failure_count':len(v['failures']),'door_interface_count':len(v['door_interfaces']),'foundation_sample_count':len(v['foundation_samples']),'paver_collision_sample_count':len(v['paver_collision_samples']),'omitted_tiny_cap_triangles':v['omitted_tiny_cap_triangles']})
for a in (run/'study-inputs').rglob('*.glb'):
    expected=next((g['glb_sha256'] for g in d['groups'] if a.stem=='village_'+g['name']),None)
    if a.parent.name=='village-grading':expected=d['terrain_glb_sha256']
    if expected:d['gpu_run']['frozen_asset_identities'].append({'path':str(a.relative_to(run)),'matches_independently_audited_glb':sha(a)==expected})
d['visual_review']={'viewed_images':['day-foreground.png','day-bay.png','door-junction.png','upper-street.png','night-reference.png'],'conclusion':'No recurrence of the rejected overlapping tile blocks or terrain penetration is visible in these five views. House paths and shared courts read as connected.','remaining_art_limitations':['Door-junction and upper-street views show high smooth uniform roadbed side walls, giving the path a raised ribbon/platform appearance.','Repeated scalloped/zigzag step edges remain conspicuous in close view.','Night reference is a distant composition view; it cannot independently establish detailed tread or doorway quality.'],'not_full_art_acceptance':True}
d['status']='PASS bounded corrected-cap/terrain/overlap geometry and five-view regression checks; final art, full-width locomotion and nine-foundation-region comparisons remain outside this acceptance.'
p.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps({'native':d['reopened_native_gate'],'gpu':d['gpu_run']},indent=2))
