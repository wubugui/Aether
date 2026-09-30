from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];run=R/'captures/validation_runs/village-paving-25f-20260908T142029Z-3a929b3fadd3459883fbdc78e6dae14e'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');assert m['status']=='passed' and m['passed'] and len(m['stages'])==5
for path,record in m['artifacts'].items():assert sha(run/path)==record['sha256'],path
rows=[]
for name in ['day-foreground','day-bay','door-junction','upper-street','night-reference']:
    p=run/'images'/(name+'.png');d=read(Path(str(p)+'.json'));v=d['village_paving_study'];s=v['paver_collision_samples']
    assert v['passed'] and not v['failures'] and d['run_id']==m['run_id']
    rows.append({'name':name,'image':str(p.relative_to(R)),'image_sha256':sha(p),'sidecar_sha256':sha(Path(str(p)+'.json')),'samples':len(s),'minimum_actual_world_ground_clearance_m':min(x['ground_clearance_m'] for x in s),'maximum_paving_top_error_m':max(abs(x['top_error_m']) for x in s),'door_interfaces':len(v['door_interfaces']),'camera':d['camera'],'root_directly_viewed':True})
e={'run_id':m['run_id'],'run_terminal_passed':True,'manifest_sha256':sha(run/'manifest.json'),'binding_count':len(m['artifacts']),'all_artifact_sha256_verified':True,'views':rows,'native_gate':'reviews/round-25f-village-grading-native-check.json','independent_review':'reviews/round-25f-village-earthworks-independent-review.md','root_visual_conclusion':'25c large exposed spikes and long black radial crease removed; support retaining this local fill repair. Roads still have scalloped repeated stair fronts; green fill has smaller triangular facets. Full1342/20-reference art remains unaccepted.','export_limit':'Independent review finds extremely thin exported triangles whose gradients exceed solver limits; no claim that every actual exported face exactly obeys design bounds.','production_installed':False}
(R/'reviews/round-25f-root-evidence.json').write_text(json.dumps(e,indent=2),encoding='utf-8')
old=read(R/'reviews/reference-view-1342-progress-24n.json');night=read(run/'images/night-reference.png.json')
old.update(frozen_run=str(run.relative_to(R)),frozen_preview=str((run/'study-inputs/preview.gd').relative_to(R)),current_evidence_run=str(run.relative_to(R)),current_image=rows[-1]['image'],current_image_sha256=rows[-1]['image_sha256'],current_sidecar=rows[-1]['image']+'.json',current_sidecar_sha256=rows[-1]['sidecar_sha256'],camera=night['camera'],world_sha256=night['world_sha256'])
old['village_progress_25f']={'paving_source':'captures/village_paving_study_24m','headland_source':'captures/village_grading_study_25f','status':'local_large_spike_repair_retained_whole_art_not_accepted','root_evidence':'reviews/round-25f-root-evidence.json','independent_review':'reviews/round-25f-village-earthworks-independent-review.md','all_exported_triangle_slope_bounds_proven':False,'production_installed':False}
old['next_visual_priority']='Replace repeated scalloped stair fronts with coherent authored lanes/flights and landings; continue shore massing, working waterfront, water/light composition and all20 references.'
(R/'reviews/reference-view-1342-progress-25f.json').write_text(json.dumps(old,indent=2),encoding='utf-8')
print(json.dumps({'run':m['run_id'],'bindings':len(m['artifacts']),'views':len(rows),'minimum_runtime_clearance_m':min(x['minimum_actual_world_ground_clearance_m'] for x in rows)}))
