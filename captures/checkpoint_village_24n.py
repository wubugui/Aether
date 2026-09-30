from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
run=root/'captures/validation_runs/village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(run/'manifest.json');assert manifest['passed'] and manifest['status']=='passed'
for relative,record in manifest['artifacts'].items():assert sha(run/relative)==record['sha256'],relative
views=[]
for name in ['day-foreground','day-bay','door-junction','upper-street','night-reference']:
    path=run/'images'/(name+'.png');sidecar=Path(str(path)+'.json');d=read(sidecar);p=d['village_paving_study']
    assert p['passed'] and not p['failures']
    views.append({'name':name,'image':str(path.relative_to(root)),'image_sha256':sha(path),'sidecar_sha256':sha(sidecar),'samples':len(p['paver_collision_samples']),'minimum_actual_world_ground_clearance_m':min(s['ground_clearance_m'] for s in p['paver_collision_samples']),'maximum_paving_top_error_m':max(abs(s['top_error_m']) for s in p['paver_collision_samples']),'door_interfaces':len(p['door_interfaces']),'camera':d['camera'],'root_directly_viewed':True})
root_report={'run_id':run.name,'run_terminal_passed':True,'manifest_sha256':sha(run/'manifest.json'),'binding_count':len(manifest['artifacts']),'all_artifact_sha256_verified':True,'views':views,'paving_source':'captures/village_paving_study_24m','graded_headland_source':'captures/village_grading_study_24l','production_modified':False,'full_reference_accepted':False,'root_visual_findings':['Nine houses now share two connected courtyard/street systems; geometry penetration and gross upper-paver overlap corrected.','Near views still show high smooth continuous bedding walls, exaggerated repeated scalloped tread boundaries and sparse open space.','Large bare mainland planes, regular island terraces, moon/cloud composition, crossed water shimmer and absent warm lighthouse beams remain unlike1342.'],'next_work':'Refine real earth grading around raised village streets and the road-side masonry/flight shapes; continue rocky shoreline, working waterfront, water/light composition and all20 references.'}
(root/'reviews/round-24n-root-evidence.json').write_text(json.dumps(root_report,indent=2),encoding='utf-8')
registry=read(root/'reviews/reference-view-1342-progress-23g.json');night=read(run/'images/night-reference.png.json')
registry['previous_headland_run']=registry['frozen_run']
for key in ['frozen_run','current_evidence_run']:registry[key]=str(run.relative_to(root))
registry['frozen_preview']=str((run/'study-inputs/preview.gd').relative_to(root))
registry['current_image']=str((run/'images/night-reference.png').relative_to(root));registry['current_image_sha256']=sha(run/'images/night-reference.png')
registry['current_sidecar']=str((run/'images/night-reference.png.json').relative_to(root));registry['current_sidecar_sha256']=sha(run/'images/night-reference.png.json')
registry['camera']=night['camera'];registry['environment_study']=night['environment_study']
registry['village_progress_24n']={'paving_source':root_report['paving_source'],'headland_source':root_report['graded_headland_source'],'editable_paving_solids':1486,'native_grading_original_border_count':134,'status':'limited_geometry_repairs_retained_whole_art_not_accepted','root_evidence':'reviews/round-24n-root-evidence.json','independent_review':'reviews/round-24n-village-paving-independent-review.md'}
registry['outstanding']=[s.replace('Near and middle right rocky village now exists as23g; natural cliff cross sections, shared streets and working shoreline remain incomplete','Near and middle right villages have shared24n courtyards/streets; raised smooth road walls, repetitive scalloped treads, natural cliff sections and working shoreline still require refinement') for s in registry['outstanding']]
registry['remaining_reference_failures']=[s.replace('Village houses lack shared stairs, courtyards and waterfront links','Shared stairs/courtyards now exist; road bedding needs natural ground contact and detailed sides, tread shapes need refinement, waterfront links remain absent') for s in registry['remaining_reference_failures']]
registry['next_visual_priority']=root_report['next_work']
(root/'reviews/reference-view-1342-progress-24n.json').write_text(json.dumps(registry,indent=2),encoding='utf-8')
print(json.dumps({'views':views,'binding_count':root_report['binding_count']},indent=2),flush=True)
