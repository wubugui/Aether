"""Save already completed native/GPU/independent evidence; does not run validation."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
runs={'31c':'lantern-island-31c-20260908T201128Z-28759710080745f9bea8113b6cf38f92',
      '31d':'lantern-island-31d-20260908T201625Z-7575af2955e449b1a68d49f13e66c31a'}
findings={
 '31c':['Front shoulders are shorter and differently oriented but read as isolated convex stones against the old broad slope.',
        'Rear addition reads as a thin vertical insert. Same-position diagonal retains1.241701m main gap; far secondary closure is not target success.',
        'Base geometry/support valid but bilateral rear target and overall visual rejected.'],
 '31d':['Same-position middle rear target now connects both banks; this is bounded geometric progress, not entire cleft or visual acceptance.',
        'D back still reads as a narrow long insert between broad grey slopes, with high and outer seams continuing toward water.',
        'Fronts remain31c isolated convex stones. Next reshape adjacent original shell facets and operand junctions together into short staggered connections, not endlessly enlarge one filler.',
        'Six actual31d rear rays locate faces1038/1467/1507/39/1973/2181. Camera left/right is not Blender axis direction; check exact occupied footprints before moving shared vertices.']}
for rev,run_id in runs.items():
    run=R/'captures/validation_runs'/run_id;m=read(run/'manifest.json')
    inc=read(R/f'reviews/round-{rev}-runtime-incremental.json')
    assert m['passed'] and m['status']=='passed' and inc['passed'] and inc['run_id']==run_id
    assert inc['all_bound_hashes_match'] and inc['binding_count']==len(m['artifacts'])==199
    reports=[f'reviews/round-{rev}-{suffix}' for suffix in ['island-native-check.json','authoring-workspace-check.json',
             'independent-geometry.json','island-independent-review.md','island-independent-review.json','runtime-incremental.json',
             'back-cleft-local-crosscheck.json','back-cleft-diagonal-check.json']]
    if rev=='31d':reports+=['reviews/round-31d-rear-flank-localization.json']
    bindings=[dict(path=p,sha256=sha(R/p)) for p in reports]
    views=[]
    for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
        p=run/'images'/(name+'.png');q=Path(str(p)+'.json');d=read(q)
        views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(q),
                          root_directly_viewed=True,camera=d['camera']))
    d=read(run/'images/night-reference.png.json');axes=[]
    for p in d['placements']:
        if p['kind']!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
        origin,yaw=([-3050,-2650],0.) if p['island']=='island_c' else ([-2372,-1812],2.)
        dx,dz=p['position'][0]-origin[0],p['position'][2]-origin[1]
        axes.append(dict(island=p['island'],world_position=p['position'],
            local_blender_xy=[math.cos(yaw)*dx-math.sin(yaw)*dz,-math.sin(yaw)*dx-math.cos(yaw)*dz],
            scale=p['scale'],ground_normal=p['ground_normal'],ground_collider=p['ground_collider'],island_root=p['island_root']))
    assert len(axes)==14
    axis=f'reviews/round-{rev}-current-tree-axes.json'
    save(R/axis,dict(run_id=run_id,actual_sidecar_sha256=views[0]['sidecar_sha256'],current_C_D_tree_axes=axes,
                    scope='Actual current runtime axes.30k authored tree placement preserved with submillimeter engine differences;2m protection disks are authoring assumptions, not a user freeze.'))
    native=R/f'captures/lantern_island_study_{rev}'
    geometry=read(R/f'reviews/round-{rev}-independent-geometry.json')
    root_rel=f'reviews/round-{rev}-root-evidence.json'
    save(R/root_rel,dict(run_id=run_id,manifest_sha256=sha(run/'manifest.json'),terminal_passed=True,binding_count=199,
        all_bound_hashes_match=True,root_views=views,reports=bindings,current_tree_axes=axis,
        native_assets=[dict(path=str((native/n).relative_to(R)),sha256=sha(native/n)) for n in ['island_c.blend','island_c.glb','shoulder_operands.blend','shoulder_authoring.blend']],
        source_basis='30k actual main exterior;31c replaces both fronts and adds rear shoulder;31d retains31c fronts and replaces only rear operand',
        base_geometry_and_support_pass=geometry['base_geometry_and_support_pass'],
        bounded_back_cleft_bilateral_connection_pass=geometry['back_cleft_bilateral_connection_pass'],
        visual_accepted=False,production_installed=False,full_goal_status='active',root_findings=findings[rev]))
    registry=read(R/'reviews/reference-view-1342-progress-31b.json')
    registry.update(run_id=run_id,camera=d['camera'],reference_image=views[0],
        environment_before_lantern_adapter=d['environment_study'],
        environment_report_source=str((run/'images/night-reference.png.json').relative_to(R)),final_lantern_configuration=d['lantern_lighting'],
        geometry_basis=dict(islands=f'A/B20l; C/D{rev} three actual authored convex shoulders union into30k.17rocks/path and current7trees per island retained. D authored placement unchanged.',
                            lighthouse='19h native',harbor='22g',village_and_headland='26b',production='17e/18c/19h unchanged'),
        evidence=['reviews/round-31c-worklog.md',root_rel,axis]+reports,
        remaining=findings[rev]+['All20references plus original opening, other regions, cloud/water/light, weather/time and full free-flight spatial acceptance remain incomplete.'])
    save(R/f'reviews/reference-view-1342-progress-{rev}.json',registry)

note='**最新31d原生、五GPU与独立审查已完成，整体仍未接受。** 31c缩短错向前肩但独立凸石感回升，背槽第三体仅接一岸，主斜截残缝1.241701m；31d仅重做第三体，目标中段已实际接两岸，低/高Y岸进入0.791512/1.464791m，但外围/高位仍有缺口，背图仍是长条塞在两大片灰坡之间。下一步联动重塑原坡面与新体交界，形成2–3个前后错位短宽连接面，不继续无条件扩大一个填槽凸包。两版各199绑定、五图及59实际落点，相对30k位置最大差0.000137329m、基础差0；道路/pad/14树盘和17岩/path保持。所有原生/GPU进程已结束，不重跑已通过检查。接续 `reviews/round-31c-worklog.md`、`reviews/round-31d-island-independent-review.md`、`reviews/round-31d-rear-flank-localization.json`、`reviews/reference-view-1342-progress-31d.json`；当前树轴 `reviews/round-31d-current-tree-axes.json`。生产17e/18c/19h未改，全部20参考及原图Goal active。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '**最新31d原生' not in s
    first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '31d背槽接续' not in s
    p.write_text(s+'\n\n31d背槽接续：31c主缺口未接一岸，31d只重做第三体后目标中段真实连接两岸；外围高位余缝、背面窄长条感和前肩孤立凸块仍未接受。下一步结合原坡面共同重塑短宽错位连接面。见 `reviews/reference-view-1342-progress-31d.json` 和 `reviews/round-31c-worklog.md`。两版原生/五GPU/独立检查已结束，生产未改，完整20参考及原场景Goal active。\n',encoding='utf-8')
with (R/'reviews/round-31c-worklog.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## 31d终态与下一步\n\nroot45491已exit0，五张实际GPU原图根与独立均直接看完。199绑定/每视角59实际落点相对30k最大差0.000137329102m、基础样本差0。独立2184三角闭合单连通，全部道路/pad/当前14树盘、17岩/path保持；前两操作数逐点等同31c。\n\n31d同位z5.137主斜截目标缺口全填，低Y/高Y岸正进入0.791512/1.464791m。局部Y九截面5个双侧通过，外侧高位仍有4个缺口，不能宣称全槽闭合。实际D背虽中段厚了，仍呈长条塞入两大片灰坡，海侧和近塔接缝未形成短宽错位岩根；前部仍有孤立凸石感。几何有界进展、整体视觉未接受。下一步停止无条件扩大单一凸包，需联动原坡面/新体交界重塑2–3个高低前后错开的短宽面。\n\n根六条实际31d背面射线定位主面1038/1467/1507/39/1973/2181，具体见`round-31d-rear-flank-localization.json`。上右像素848510命中(-5.59,3.43,7.42)，需按真实pad和树盘边界判定，不能直接套旧31b面索引。804538命中面1973只是实际源面记录，不能凭肉眼把它当作新操作数面；后续应与实际操作数平面核对。31c/d root证据、当前14树轴和1342注册已保存。所有原生/GPU进程结束；生产与完整目标范围保持。\n')
print('31c/d actual checkpoints saved; full goal active; no engine or native check rerun.')
