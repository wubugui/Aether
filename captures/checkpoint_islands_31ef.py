from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
runs={'31e':'lantern-island-31e-20260908T203322Z-c8a7a40b1ae5442c8aeba5858633afbd',
      '31f':'lantern-island-31f-20260908T204147Z-c8f8aed2cd5f43a7be28d18f0f9ba891'}
findings={'31e':['Original long wall has a real middle oblique break and lower junction turns with the old union shell; preserve this direction.',
                 'Narrow vertical strip, side seams, fixed straight sea mouth and isolated front stones remain unresolved.',
                 '46 original source points and64 new bisect points moved. Original high point997 moved only0.14mm, not meaningful upper-slope change.'],
          '31f':['Original high flank and local sea mouth visibly change, retaining31e joint original-slope reform.',
                 'Middle remains narrow and long, adjacent broad slopes and longitudinal junctions remain unresolved; fronts retain isolated-stone appearance.',
                 'Old2m tree-disk linear surfaces are not entirely preserved:2.835297m2 changes, up to40.461mm lower. Actual runtime centers remain stable; all14 real native trunk footprints retain continuous original ground coverage, not entire flat-bottom contact.',
                 'Historical three convex operands are construction inputs only; final editable whole island mesh is authoritative.']}
for rev,run_id in runs.items():
    run=R/'captures/validation_runs'/run_id;m=read(run/'manifest.json');inc=read(R/f'reviews/round-{rev}-runtime-incremental.json')
    assert m['passed'] and m['status']=='passed' and inc['passed'] and inc['run_id']==run_id
    assert inc['all_bound_hashes_match'] and inc['binding_count']==len(m['artifacts'])==200
    reports=[f'reviews/round-{rev}-{s}' for s in ['island-native-check.json','authoring-workspace-check.json','independent-geometry.json','local-intersections.json','island-independent-review.md','island-independent-review.json','runtime-incremental.json']]
    if rev=='31e':reports+=['reviews/round-31e-anchor-change-check.json','reviews/round-31e-topology-intake.md','reviews/round-31e-topology-intake.json']
    else:
        extras=set((R/'reviews').glob('round-31f-*tree*.json'))|set((R/'reviews').glob('round-31f-*pine*.json'))
        reports+=sorted(str(p.relative_to(R)).replace('\\','/') for p in extras)
        reports+=['reviews/round-31f-anchor-rock-contact.json']
    bindings=[dict(path=p,sha256=sha(R/p)) for p in reports]
    views=[]
    for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
        p=run/'images'/(name+'.png');q=Path(str(p)+'.json');d=read(q)
        views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(q),root_directly_viewed=True,camera=d['camera']))
    d=read(run/'images/night-reference.png.json');axes=[]
    for p in d['placements']:
        if p['kind']!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
        origin,yaw=([-3050,-2650],0.) if p['island']=='island_c' else ([-2372,-1812],2.)
        dx,dz=p['position'][0]-origin[0],p['position'][2]-origin[1]
        axes.append(dict(island=p['island'],world_position=p['position'],local_blender_xy=[math.cos(yaw)*dx-math.sin(yaw)*dz,-math.sin(yaw)*dx-math.cos(yaw)*dz],
                         scale=p['scale'],ground_normal=p['ground_normal'],ground_collider=p['ground_collider'],island_root=p['island_root']))
    assert len(axes)==14
    axis=f'reviews/round-{rev}-current-tree-axes.json'
    save(R/axis,dict(run_id=run_id,actual_sidecar_sha256=views[0]['sidecar_sha256'],current_C_D_tree_axes=axes,
                    scope='Actual runtime axes.2m terrain disks are an authoring support-check region, not the actual trunk footprint or a permanent user freeze.'))
    native=R/f'captures/lantern_island_study_{rev}';root_rel=f'reviews/round-{rev}-root-evidence.json'
    save(R/root_rel,dict(run_id=run_id,manifest_sha256=sha(run/'manifest.json'),terminal_passed=True,binding_count=200,all_bound_hashes_match=True,
        root_views=views,reports=bindings,current_tree_axes=axis,
        native_assets=[dict(path=str((native/n).relative_to(R)),sha256=sha(native/n)) for n in ['island_c.blend','island_c.glb','reform-plan.json','shoulder_operands.blend','shoulder_authoring.blend']],
        source_basis='31e reforms actual31d original slope plus union;31f sculpts actual31e high/mid/seaward shell without adding topology or new filler',
        historical_operand_role='Three native convex operands are retained history only, not final sculpted exterior definition.',
        old_2m_tree_disk_linear_surfaces_preserved=(rev=='31e'),
        actual_tree_base_support=(read(R/'reviews/round-31f-actual-tree-support.json')['actual_tree_base_support'] if rev=='31f' else None),
        visual_accepted=False,production_installed=False,full_goal_status='active',root_findings=findings[rev]))
    registry=read(R/'reviews/reference-view-1342-progress-31d.json')
    registry.update(run_id=run_id,camera=d['camera'],reference_image=views[0],environment_before_lantern_adapter=d['environment_study'],
        environment_report_source=str((run/'images/night-reference.png.json').relative_to(R)),final_lantern_configuration=d['lantern_lighting'],
        geometry_basis=dict(islands=f'A/B20l; C/D{rev} actual native original-slope/union sculpt.17rocks/path retained, actual runtime7trees per island recorded; D placement unchanged.',
                            lighthouse='19h native',harbor='22g',village_and_headland='26b',production='17e/18c/19h unchanged'),
        evidence=['reviews/round-31e-worklog.md',root_rel,axis]+reports,
        remaining=findings[rev]+['All20references plus original opening, other regions, clouds/water/light, weather/time and full free-flight spatial acceptance remain incomplete.'])
    save(R/f'reviews/reference-view-1342-progress-{rev}.json',registry)
note='**最新31f原生、五GPU与独立审查已完成，整体仍未接受。** 31e把原长陡面和旧后体共同稀疏切分/偏移，中层斜折和低根转向可保留；31f进一步雕刻高坡、中层及局部海口，海口参与转向，但窄长条、纵向侧缝和前部孤立凸石仍需改形。最终实体为各版island_c.blend，三凸包仅是历史输入。两版各200绑定、五原图、59实际落点相对30k位置最大差0.000137329m。31f原2m树盘有2.835297m²旧线性面变化、最大降低0.040461m，实际树中心保持；按真实pine六边形底部核验，14棵干底投影下连续覆盖且旧面保持，old_tree_disk_surface_preserved=false、actual_tree_base_support=true，不能声称整树盘不变或平底与斜面处处贴合。路径17岩、道路/pad保持；实际局部三角自交/法线检查已完成。原生/GPU进程均结束，不重跑已通过检查。接续 `reviews/round-31e-worklog.md`、`reviews/round-31f-island-independent-review.md`、`reviews/reference-view-1342-progress-31f.json`；当前树轴 `reviews/round-31f-current-tree-axes.json`。生产17e/18c/19h未改，全部20参考及原场景Goal active。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '**最新31f原生' not in s
    first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '31f原壳雕刻接续' not in s
    p.write_text(s+'\n\n31f原壳雕刻接续：31e/31f直接联动原坡与已有后体，中层折面、高坡及海口方向有实际变化；整体因窄长条、侧缝及前部孤立凸石仍未接受。31f树旁2m检查盘局部旧平面变化需与实际干底接触分开记录。见 `reviews/reference-view-1342-progress-31f.json`、`reviews/round-31e-worklog.md`。生产未变，完整20参考及原开场Goal active。\n',encoding='utf-8')
print('31e/f actual native and five-view records saved; entire goal active.')
