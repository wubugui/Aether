from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
run=root/'captures/validation_runs/headland-assembly-23g-20260908T121755Z-4ca247af11bb4af2a7bba06fe2383718'
manifest=read(run/'manifest.json');assert manifest['passed']
rows=[]
for path in sorted((run/'images').glob('*.png.json')):
    data=read(path);head=data['headland_study'];gaps=[p['gap_m'] for h in head['footings'] for p in h['samples']]
    rows.append({'image':str(path)[:-5],'view':data['view'],'camera':data['camera'],'house_count':len(head['footings']),'foundation_samples':len(gaps),'foundation_gap_range_m':[min(gaps),max(gaps)],'trees':len(head['trees']),'lights':len(head['lights']),'scatter_changes':head['scatter_changes']})
target=root/'reviews/round-23g-root-evidence.json';assert not target.exists()
target.write_text(json.dumps({'status':'in_progress_not_accepted','production_installed':False,'run':str(run),'world_sha256':data['world_sha256'],'native_gate':'reviews/round-23g-headland-native-check.json','source_assets':read(root/'captures/headland_study_23g/model-report.json')['assets'],'views':rows,'root_visual_review':{'directly_viewed_images':5,'improved':['Near and middle right mainland village placement','23d interior long-wall discontinuity visibly removed in day-seam view','Real closed rocky coast, raised back ridges and28 native pines','Shore constraint restored separately from ridge and outside-pad blend;57 nontransition design vertices checked'],'unresolved':['Large planar bare slopes and regular village terrace edges','Buttresses still read as separate block noses against the continuous coast wall','Nine village houses still lack shared courtyards, stairs and coastal access','Window and lantern warmth insufficient compared with reference1342','Original20l islands,21c sky/moon/water and22g distant harbor remain visually incomplete'],'limits':'Closed source meshes and81 house-foundation rays per view do not prove every contact, old-terrain seam, pine root, buttress intersection, flight route, reference fidelity or production integration.'}},ensure_ascii=False,indent=2),encoding='utf-8')
prior=read(root/'reviews/reference-view-1342-progress-22g.json')
prior['status']='in_progress_not_accepted';prior['headland_candidate_23g']={'frozen_run':str(run),'evidence':str(target),'production_installed':False,'images':[r['image'] for r in rows],'scope':'23g continuous mainland headland,9 houses in2 clusters,28 native pines; whole scene and streets still incomplete.'}
night=read(run/'images/night-reference.png.json')
prior['previous_harbor_run']=prior['frozen_run']
prior['frozen_run']=str(run.relative_to(root)).replace('\\','/')
prior['frozen_preview']=str((run/'study-inputs/preview.gd').relative_to(root)).replace('\\','/')
prior['current_evidence_run']=prior['frozen_run']
for key,filename in [('current_image','night-reference.png'),('current_sidecar','night-reference.png.json')]:
    path=run/'images'/filename
    prior[key]=str(path.relative_to(root)).replace('\\','/')
    prior[key+'_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
prior['camera']=night['camera'];prior['environment_study']=night['environment_study']
prior['outstanding']=[s.replace('Right foreground rocky village composition remains absent; surveyed harbor modules and paths exist as temporary candidates','Near and middle right rocky village now exists as23g; natural cliff cross sections, shared streets and working shoreline remain incomplete') for s in prior['outstanding']]
prior['next_visual_priority']='Refine mainland cliff cross sections and joined rock shoulders; build shared village courtyards/stairs and low working waterfront around the nine existing houses. Continue all20 references.'
prior['remaining_reference_failures']=['Main cliff wall and rock noses remain too regular; broad bare rock planes need better composition','Village houses lack shared stairs, courtyards and waterfront links','Original islands, clouds, moon, water and light beams remain incomplete','Complete20-reference world and production integration not accepted']
target=root/'reviews/reference-view-1342-progress-23g.json';assert not target.exists();target.write_text(json.dumps(prior,ensure_ascii=False,indent=2),encoding='utf-8')
print('RECORDED23E '+str(len(rows))+' GPU VIEWS')
