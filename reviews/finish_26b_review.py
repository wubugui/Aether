from pathlib import Path
import json,hashlib
R=Path(r'E:\FeiTing');path=R/'reviews/round-26b-village-sloped-paving-independent-review.json';d=json.loads(path.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();d['house_and_shore_protection']=json.loads((R/'reviews/round-26b-village-protection-independent.json').read_text())
pg=json.loads((R/'reviews/round-26b-village-paving-native-check.json').read_text());tg=json.loads((R/'reviews/round-26b-village-grading-native-check.json').read_text());d['native_identity']={'paving_gate_passed':pg['passed'],'terrain_gate_passed':tg['passed'],'terrain_glb_matches':tg['glb_sha256']==d['terrain_glb_sha256'],'terrain_blend_matches':tg['source_sha256']==sha(R/'captures/village_grading_study_26b/mainland_headland.blend'),'paving':[]}
for g in d['groups']:
    a=next(a for a in pg['assets'] if a['asset']=='village_'+g['name']);d['native_identity']['paving'].append({'group':g['name'],'glb_matches':a['glb_sha256']==g['glb_sha256'],'blend_matches':a['source_sha256']==sha(R/('captures/village_paving_study_26b/village_'+g['name']+'.blend')),'parts':len(a['parts'])})
run=R/'captures/validation_runs/village-paving-26b-20260908T143321Z-441bad8ec7bd4024b195dca93cc8bd82';m=json.loads((run/'manifest.json').read_text());d['gpu_run']={'run_id':m['run_id'],'status':m['status'],'passed':m['passed'],'views':[],'frozen_asset_identity':[]}
for p in sorted((run/'images').glob('*.png')):
    j=json.loads(p.with_suffix('.png.json').read_text());v=j['village_paving_study'];d['gpu_run']['views'].append({'image':p.name,'sha256':sha(p),'run_matches':j['run_id']==m['run_id'],'paving_passed':v['passed'],'failures':len(v['failures'])})
for p in (run/'study-inputs').rglob('*.glb'):
    expected=next((g['glb_sha256'] for g in d['groups'] if p.stem=='village_'+g['name']),None)
    if p.parent.name=='village-grading':expected=d['terrain_glb_sha256']
    if expected:d['gpu_run']['frozen_asset_identity'].append({'path':str(p.relative_to(run)),'matches_actual_audit':sha(p)==expected})
d['visual_review']={'directly_viewed':['day-foreground.png','day-bay.png','door-junction.png','upper-street.png','night-reference.png'],'bounded_result':'Continuous sloped paving is visually clearer than repeated scalloped contour stairs. Door aprons and courts read as connected. No recurrence of large spike/long black crease defects is visible in these five views.','remaining':'Some narrow exposed roadbed edges, irregular terrain facets, broad original rock faces, regular water glints and overall reference-art gaps remain. Five static views do not prove character traversal over every lane.','reference_art_accepted':False}
d['status']='PASS bounded slope-lane improvement, meaningful support/overlap, body-foundation and shoreline preservation, and five-view regression. Retain raw microcap anomalies and 0.961mm bedding/terrain overlap; not exact zero-intersection or full gameplay/reference-art acceptance.'
path.write_text(json.dumps(d,indent=2),encoding='utf-8');print(d['native_identity']);print(d['gpu_run']['status'])
