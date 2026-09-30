from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];run=R/'captures/validation_runs/village-paving-26b-20260908T143321Z-441bad8ec7bd4024b195dca93cc8bd82'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');assert m['status']=='passed' and m['passed'] and len(m['stages'])==5
for path,record in m['artifacts'].items():assert sha(run/path)==record['sha256'],path
rows=[]
for name in ['day-foreground','day-bay','door-junction','upper-street','night-reference']:
    p=run/'images'/(name+'.png');d=read(Path(str(p)+'.json'));v=d['village_paving_study'];s=v['paver_collision_samples']
    assert v['passed'] and not v['failures'] and d['run_id']==m['run_id']
    rows.append({'name':name,'image':str(p.relative_to(R)),'image_sha256':sha(p),'sidecar_sha256':sha(Path(str(p)+'.json')),'samples':len(s),'minimum_actual_world_ground_clearance_m':min(x['ground_clearance_m'] for x in s),'maximum_paving_top_error_m':max(abs(x['top_error_m']) for x in s),'door_interfaces':len(v['door_interfaces']),'foundation_samples':len(v['foundation_samples']),'omitted_tiny_caps':v['omitted_tiny_cap_triangles'],'camera':d['camera'],'root_directly_viewed':True})
e={'run_id':m['run_id'],'run_terminal_passed':True,'manifest_sha256':sha(run/'manifest.json'),'binding_count':len(m['artifacts']),'all_artifact_sha256_verified':True,'views':rows,'native_gates':['reviews/round-26b-village-grading-native-check.json','reviews/round-26b-village-paving-native-check.json'],'independent_review':'reviews/round-26b-village-lanes-independent-review.md','root_visual_conclusion':'Repeated scalloped stair fronts replaced by coherent laid-stone sloped lanes. Fixed door aprons remain; prior large spikes/black radial crease do not visibly recur. Smaller planar facets, formal circular courtyard and bare cliff walls remain; full1342/20-reference art not accepted.','production_installed':False}
(R/'reviews/round-26b-root-evidence.json').write_text(json.dumps(e,indent=2),encoding='utf-8')
reg=read(R/'reviews/reference-view-1342-progress-25f.json');night=read(run/'images/night-reference.png.json')
reg.update(frozen_run=str(run.relative_to(R)),frozen_preview=str((run/'study-inputs/preview.gd').relative_to(R)),current_evidence_run=str(run.relative_to(R)),current_image=rows[-1]['image'],current_image_sha256=rows[-1]['image_sha256'],current_sidecar=rows[-1]['image']+'.json',current_sidecar_sha256=rows[-1]['sidecar_sha256'],camera=night['camera'],world_sha256=night['world_sha256'])
reg['village_progress_26b']={'paving_source':'captures/village_paving_study_26b','headland_source':'captures/village_grading_study_26b','status':'root_local_lane_repair_supported_independent_review_pending_whole_art_not_accepted','editable_lane_solids':922,'root_evidence':'reviews/round-26b-root-evidence.json','production_installed':False}
reg['next_visual_priority']='After independent lane review, continue main rock shoreline and island silhouettes, water/moon/light composition and the other reference scenes. Avoid repeating passed local street checks without a relevant change.'
(R/'reviews/reference-view-1342-progress-26b.json').write_text(json.dumps(reg,indent=2),encoding='utf-8')
print(json.dumps({'run':m['run_id'],'bindings':len(m['artifacts']),'views':len(rows),'per_view_samples':rows[0]['samples'],'per_view_foundations':rows[0]['foundation_samples'],'minimum_runtime_clearance_m':min(x['minimum_actual_world_ground_clearance_m'] for x in rows),'max_top_error_m':max(x['maximum_paving_top_error_m'] for x in rows)}))
