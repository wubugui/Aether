from pathlib import Path
import json,hashlib,math,sys
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
run_id=sys.argv[1];run=R/'captures/validation_runs'/run_id;m=read(run/'manifest.json');inc=read(R/'reviews/round-31h-runtime-incremental.json')
assert m['passed'] and m['status']=='passed' and inc['passed'] and inc['run_id']==run_id
assert inc['all_bound_hashes_match'] and inc['binding_count']==len(m['artifacts'])==201
findings=read(R/'reviews/round-31h-root-visual-findings.json')
assert findings['run_id']==run_id and findings['directly_viewed']==['night-reference','day-reference','day-d-front','day-d-back','day-c-front']
reports=[f'reviews/round-31h-{s}' for s in ['island-native-check.json','authoring-workspace-check.json','material-identity.json','island-independent-review.md','island-independent-review.json','runtime-incremental.json','root-visual-findings.json']]
reports += ['reviews/round-31g-independent-geometry.json','reviews/round-31g-local-intersections.json','reviews/round-31g-actual-tree-support.json']
bindings=[dict(path=p,sha256=sha(R/p)) for p in reports]
views=[]
for name in findings['directly_viewed']:
 p=run/'images'/(name+'.png');q=Path(str(p)+'.json');d=read(q)
 views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(q),root_directly_viewed=True,camera=d['camera']))
d=read(run/'images/night-reference.png.json');axes=[]
for p in d['placements']:
 if p['kind']!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
 origin,yaw=([-3050,-2650],0.) if p['island']=='island_c' else ([-2372,-1812],2.)
 dx,dz=p['position'][0]-origin[0],p['position'][2]-origin[1]
 axes.append(dict(island=p['island'],world_position=p['position'],local_blender_xy=[math.cos(yaw)*dx-math.sin(yaw)*dz,-math.sin(yaw)*dx-math.cos(yaw)*dz],scale=p['scale'],ground_normal=p['ground_normal'],ground_collider=p['ground_collider'],island_root=p['island_root']))
assert len(axes)==14
axis='reviews/round-31h-current-tree-axes.json'
save(R/axis,dict(run_id=run_id,actual_sidecar_sha256=views[0]['sidecar_sha256'],current_C_D_tree_axes=axes,scope='Actual31h runtime centers. Native trunk footprint support independently checked; old2m disks are not permanent user constraints.'))
native=R/'captures/lantern_island_study_31h';root_rel='reviews/round-31h-root-evidence.json'
save(R/root_rel,dict(run_id=run_id,manifest_sha256=sha(run/'manifest.json'),terminal_passed=True,binding_count=201,all_bound_hashes_match=True,root_views=views,reports=bindings,current_tree_axes=axis,native_assets=[dict(path=str((native/n).relative_to(R)),sha256=sha(native/n)) for n in ['island_c.blend','island_c.glb','reform-plan.json','shoulder_operands.blend','shoulder_authoring.blend']],source_basis='31h material correction over actual31g identical native/GLB geometry. Only72 faces changed grass to exposed rock,12 upper faces retain grass. Exact identity report supports inherited31g geometric checks.',historical_operand_role='Three old convex native operands are history only; actual final editable surface is island_c.blend.',actual_tree_base_support=True,visual_accepted=False,production_installed=False,full_goal_status='active',root_findings=findings['findings']))
registry=read(R/'reviews/reference-view-1342-progress-31g.json')
registry.update(run_id=run_id,camera=d['camera'],reference_image=views[0],environment_before_lantern_adapter=d['environment_study'],environment_report_source=str((run/'images/night-reference.png.json').relative_to(R)),final_lantern_configuration=d['lantern_lighting'],geometry_basis=dict(islands='A/B20l; C/D31h material correction on unchanged31g actual rear topology, native17rocks/path retained, runtime7trees per island; D layout unchanged.',lighthouse='19h native',harbor='22g',village_and_headland='26b',production='17e/18c/19h unchanged'),evidence=['reviews/round-31h-worklog.md',root_rel,axis]+reports,remaining=findings['findings']+['All20 references and original opening, other regions, weather/time, cloud/water/light and full free-flight spatial acceptance remain incomplete.'])
save(R/'reviews/reference-view-1342-progress-31h.json',registry)
note=findings['resume_note']
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
 p=R/name;s=p.read_text(encoding='utf-8');assert '**最新31h' not in s
 first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');assert '31h真实拓扑重接接续' not in s
 p.write_text(s+'\n\n31h真实拓扑重接接续：'+note+'\n',encoding='utf-8')
print('31h actual native, five-view, independent and full-goal continuation records saved.')
