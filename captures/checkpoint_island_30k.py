from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-island-30k-r1-20260908T193210Z-09e7ff871c9941519a561b4fede063ee'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');inc=read(R/'reviews/round-30k-runtime-incremental.json')
review=R/'reviews/round-30k-island-independent-review.md';assert review.exists()
assert m['passed'] and m['status']=='passed' and inc['passed'] and inc['run_id']==m['run_id']
assert inc['all_bound_hashes_match'] and inc['binding_count']==len(m['artifacts'])
views=[]
for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
    p=run/'images'/(name+'.png');q=Path(str(p)+'.json');d=read(q)
    views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(q),root_directly_viewed=True,camera=d['camera']))
d=read(run/'images/night-reference.png.json');axes=[]
for p in d['placements']:
    if p['kind']!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
    origin,yaw=([-3050,-2650],0.) if p['island']=='island_c' else ([-2372,-1812],2.)
    dx,dz=p['position'][0]-origin[0],p['position'][2]-origin[1]
    axes.append(dict(island=p['island'],world_position=p['position'],local_blender_xy=[math.cos(yaw)*dx-math.sin(yaw)*dz,-math.sin(yaw)*dx-math.cos(yaw)*dz],scale=p['scale'],ground_normal=p['ground_normal'],ground_collider=p['ground_collider'],island_root=p['island_root']))
assert len(axes)==14
axis_path=R/'reviews/round-30k-current-tree-axes.json';assert not axis_path.exists()
axis_path.write_text(json.dumps(dict(run_id=m['run_id'],actual_sidecar_sha256=views[0]['sidecar_sha256'],current_C_D_tree_axes=axes,scope='Actual30k runtime positions converted with authored C/D transforms. Supersedes30d old axes for new support studies. Any2m protection radius remains an authoring assumption, not a permanent user requirement.'),indent=2))
findings=['30h repeated narrow fan-shaped recesses removed;30k fewer broad facets and lower east tree group are useful progress.', 'Near front left slope around x530-770/y495-590 remains an oversized continuous inclined slab; central thin incision and old rear narrow deep cleft remain unresolved.', 'Next form shorter staggered convex blocks and irregular cross-slope breaks within actual main exterior; do not just enlarge/deepen concave cutter planes, uniformly shift17rocks, or add a loose masking ring.', 'Keep actual roads/pads and sync any changed tree grounding/collision. Use current30k tree-axis evidence instead of freezing old30d eastern positions.']
out=dict(run_id=m['run_id'],manifest_sha256=sha(run/'manifest.json'),terminal_passed=True,binding_count=inc['binding_count'],all_bound_hashes_match=True,incremental_runtime_report='reviews/round-30k-runtime-incremental.json',root_views=views,independent_review=str(review.relative_to(R)),independent_review_sha256=sha(review),independent_geometry='reviews/round-30k-independent-geometry.json',current_tree_axes=str(axis_path.relative_to(R)),visual_accepted=False,production_installed=False,full_goal_status='active',root_findings=findings)
p=R/'reviews/round-30k-root-evidence.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
registry=read(R/'reviews/reference-view-1342-progress-30h.json')
registry.update(run_id=m['run_id'],camera=d['camera'],reference_image=views[0],environment_before_lantern_adapter=d['environment_study'],environment_report_source=str((run/'images/night-reference.png.json').relative_to(R)),final_lantern_configuration=d['lantern_lighting'],geometry_basis={'islands':'A/B20l; C/D30k authored broad bent cuts from30d, road/pad constrained; native17rocks/path retained. Two eastern trees per island re-grounded at new lower shoulders; other five trees retained. D authored placement unchanged.','lighthouse':'19h native','harbor':'22g','village_and_headland':'26b','production':'17e/18c/19h unchanged'},evidence=['reviews/round-30-worklog.md','reviews/round-30k-root-evidence.json','reviews/round-30k-island-independent-review.md','reviews/round-30k-independent-geometry.json','reviews/round-30k-runtime-incremental.json','reviews/round-30k-current-tree-axes.json'],remaining=findings+['All20references plus original opening, other island/mainland geometry, village, cloud/water/warm light, weather/time and free-flight spatial checks remain incomplete.'])
(R/'reviews/reference-view-1342-progress-30k.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
position=max(v['maximum_unchanged_position_delta_m'] for v in inc['views']);footing=max(v['maximum_footing_delta_m'] for v in inc['views'])
note=f'**最新30k宽面与树组重贴已完成原生、五GPU和独立审查，整体仍未接受。** 30h密集折扇已消除，显式宽折面和低肩树组可保留为接续；正面左侧大斜板、中部尖窄切口、背面老直槽仍需返工。19原生件、1936主壳三角；完整道路/pad、路径17岩和五保留树组支承保持。每岛东侧两棵树移位，59实际落点中55保留（最大差{position:.9f}m），4移位按真实全网格上表面验证，基础样本最大差{footing:.9f}m。当前树轴以 `reviews/round-30k-current-tree-axes.json` 为准，不沿用30d旧东树位置。首次GPU因根节点名检查错误失败，修为实际island_root后r1完成196绑定/五图；所有进程已结束，不重跑已通过原生或GPU。接续 `reviews/round-30-worklog.md`、`reviews/round-30k-island-independent-review.md`、`reviews/reference-view-1342-progress-30k.json`，下一步做短宽凸块和横向错位折面，不继续放大凹面。生产17e/18c/19h未改，全部20参考及原图Goal active。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '**最新30k宽面' not in s;first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '30k宽面接续' not in s;p.write_text(s+'\n\n30k宽面接续：实际五图中30h密集折扇消除，两东树/岛移到低肩并重新碰撞落地；完整道路/pad和其他五树组保持。正面大斜板、尖切口和背面长槽仍未达标，下一稿重排凸块与横向错位折面。当前C/D树轴已更新，见 `reviews/round-30k-current-tree-axes.json` 与 `reviews/reference-view-1342-progress-30k.json`。全20参考及原图Goal active，生产未变。\n',encoding='utf-8')
print('30k actual evidence/current tree axes and full-scope registry saved; Goal active')
