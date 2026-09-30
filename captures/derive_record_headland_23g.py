from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'captures/record_headland_23e.py').read_text(encoding='utf-8').replace('23e','23g').replace('20260908T121015Z-1eb47cc3dc3444f2a119ebd128e10b58','20260908T121755Z-4ca247af11bb4af2a7bba06fe2383718')
code=code.replace("'Real closed rocky coast, raised back ridges and28 native pines'","'Real closed rocky coast, raised back ridges and28 native pines','Shore constraint restored separately from ridge and outside-pad blend;57 nontransition design vertices checked'")
anchor="target=root/'reviews/reference-view-1342-progress-23g.json'"
insert='''night=read(run/'images/night-reference.png.json')
prior['previous_harbor_run']=prior['frozen_run']
prior['frozen_run']=str(run.relative_to(root)).replace('\\\\','/')
prior['frozen_preview']=str((run/'study-inputs/preview.gd').relative_to(root)).replace('\\\\','/')
prior['current_evidence_run']=prior['frozen_run']
for key,filename in [('current_image','night-reference.png'),('current_sidecar','night-reference.png.json')]:
    path=run/'images'/filename
    prior[key]=str(path.relative_to(root)).replace('\\\\','/')
    prior[key+'_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
prior['camera']=night['camera'];prior['environment_study']=night['environment_study']
prior['outstanding']=[s.replace('Right foreground rocky village composition remains absent; surveyed harbor modules and paths exist as temporary candidates','Near and middle right rocky village now exists as23g; natural cliff cross sections, shared streets and working shoreline remain incomplete') for s in prior['outstanding']]
prior['next_visual_priority']='Refine mainland cliff cross sections and joined rock shoulders; build shared village courtyards/stairs and low working waterfront around the nine existing houses. Continue all20 references.'
prior['remaining_reference_failures']=['Main cliff wall and rock noses remain too regular; broad bare rock planes need better composition','Village houses lack shared stairs, courtyards and waterfront links','Original islands, clouds, moon, water and light beams remain incomplete','Complete20-reference world and production integration not accepted']
'''
assert anchor in code;code=code.replace(anchor,insert+anchor)
target=root/'captures/record_headland_23g.py';assert not target.exists();target.write_text(code,encoding='utf-8')
