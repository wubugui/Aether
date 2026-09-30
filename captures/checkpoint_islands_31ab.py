from pathlib import Path
import json, hashlib, math

R = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write_new(p, data):
    assert not p.exists(), p
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

runs = {
    '31a': 'lantern-island-31a-20260908T194852Z-ac4f6f47286b4774afd18b8206e9f9ca',
    '31b': 'lantern-island-31b-20260908T195540Z-dc0f57e0a037461484c11dba7dcb8b57',
}
findings = {
    '31a': ['Rejected: both added shoulders read as repeated flat capped polygonal buttons in front views.',
            '31b is rebuilt from30k, not an accumulation on31a. Preserve31a failure evidence.',
            'The old rear long cleft is unchanged.'],
    '31b': ['Flat caps removed; irregular slanted roots improve the front silhouette and connection.',
            'Left continuous top remains too long and the middle shoulder has a similar direction; both require shorter, blunt, staggered facets.',
            'Rear narrow straight cleft remains. Four actual rays locate faces309/1454/1467/1467; occupied-boundary review is saved separately.',
            'Do not infer the entire cleft history from four points: face1454 extends to y17.908 despite a hit near y12.282.'],
}
for rev, run_id in runs.items():
    run = R/'captures/validation_runs'/run_id
    m = read(run/'manifest.json')
    inc = read(R/f'reviews/round-{rev}-runtime-incremental.json')
    assert m['passed'] and m['status'] == 'passed' and inc['passed']
    assert inc['run_id'] == m['run_id'] == run_id
    assert inc['all_bound_hashes_match'] and inc['binding_count'] == len(m['artifacts']) == 199
    views = []
    for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
        p = run/'images'/(name+'.png'); q = Path(str(p)+'.json'); d = read(q)
        views.append(dict(name=name, path=str(p.relative_to(R)), png_sha256=sha(p),
                          sidecar_sha256=sha(q), root_directly_viewed=True, camera=d['camera']))
    d = read(run/'images/night-reference.png.json')
    axes = []
    for p in d['placements']:
        if p['kind'] != 'existing_native_pine' or p.get('island') not in ['island_c','island_d']:
            continue
        origin, yaw = ([-3050,-2650],0.) if p['island']=='island_c' else ([-2372,-1812],2.)
        dx,dz = p['position'][0]-origin[0],p['position'][2]-origin[1]
        axes.append(dict(island=p['island'], world_position=p['position'],
                         local_blender_xy=[math.cos(yaw)*dx-math.sin(yaw)*dz,-math.sin(yaw)*dx-math.cos(yaw)*dz],
                         scale=p['scale'], ground_normal=p['ground_normal'],
                         ground_collider=p['ground_collider'], island_root=p['island_root']))
    assert len(axes)==14
    axis_rel = f'reviews/round-{rev}-current-tree-axes.json'
    write_new(R/axis_rel, dict(run_id=run_id, actual_sidecar_sha256=views[0]['sidecar_sha256'],
                             current_C_D_tree_axes=axes,
                             scope='Actual current runtime axes; inherited30k design with submillimeter engine differences. A2m protection disk is an authoring assumption, not a user freeze.'))
    reports = [f'reviews/round-{rev}-{suffix}' for suffix in
               ['island-native-check.json','authoring-workspace-check.json','independent-geometry.json',
                'island-independent-review.md','island-independent-review.json','runtime-incremental.json']]
    if rev=='31b':
        reports += ['reviews/round-31b-back-cleft-localization.json',
                    'reviews/round-31b-back-cleft-independent.json','reviews/round-31b-back-cleft-independent.md']
    report_bindings = [dict(path=p,sha256=sha(R/p)) for p in reports]
    model_dir = R/f'captures/lantern_island_study_{rev}'
    native = [dict(path=str((model_dir/n).relative_to(R)),sha256=sha(model_dir/n)) for n in
              ['island_c.blend','island_c.glb','shoulder_operands.blend','shoulder_authoring.blend']]
    root_rel = f'reviews/round-{rev}-root-evidence.json'
    write_new(R/root_rel, dict(run_id=run_id, manifest_sha256=sha(run/'manifest.json'),
              terminal_passed=True, binding_count=199, all_bound_hashes_match=True,
              root_views=views, reports=report_bindings, native_assets=native,
              current_tree_axes=axis_rel, source_basis='30k actual main exterior;31b does not inherit31a buttons',
              visual_accepted=False, production_installed=False, full_goal_status='active',
              root_findings=findings[rev]))
    registry = read(R/'reviews/reference-view-1342-progress-30k.json')
    registry.update(run_id=run_id, camera=d['camera'], reference_image=views[0],
        environment_before_lantern_adapter=d['environment_study'],
        environment_report_source=str((run/'images/night-reference.png.json').relative_to(R)),
        final_lantern_configuration=d['lantern_lighting'],
        geometry_basis=dict(islands=f'A/B20l; C/D{rev} actual convex-shoulder union from30k.17rocks/path and current7trees per island retained; D authored placement unchanged.',
                            lighthouse='19h native',harbor='22g',village_and_headland='26b',production='17e/18c/19h unchanged'),
        evidence=['reviews/round-31-worklog.md',root_rel,axis_rel]+reports,
        remaining=findings[rev]+['All20references plus original opening, other geometry, cloud/water/light, weather/time and free-flight spatial acceptance remain incomplete.'])
    write_new(R/f'reviews/reference-view-1342-progress-{rev}.json', registry)

note = '**最新31b斜肩已完成原生、五GPU和独立审查，整体仍未接受。** 31a平顶按钮造型被打回；31b从30k原壳重新制作，已消除柱帽，但左肩连续顶面偏长、中肩同向及背面旧长槽仍需返工。两版各199冻结绑定、59实际落点，位置最大差0.000167847m；31b基础样本最大差0.000045776m。道路/pad/当前14树盘支承、路径和17岩保持。全部原生和GPU进程已结束，不重复已通过检查。背槽四实际射线与独立复核匹配，三源面无实质占用，最近距扩张pad约1.375m；需按真实边界设计，不能据四点推断整槽成因。接续 `reviews/round-31-worklog.md`、`reviews/round-31b-island-independent-review.md`、`reviews/round-31b-back-cleft-independent.md` 和 `reviews/reference-view-1342-progress-31b.json`。当前树轴记录为 `reviews/round-31b-current-tree-axes.json`。生产17e/18c/19h未改，全部20参考及原图Goal active。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name; s=p.read_text(encoding='utf-8'); assert '**最新31b斜肩' not in s
    first, rest=s.split('\n',1); p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name; s=p.read_text(encoding='utf-8'); assert '31b斜肩接续' not in s
    p.write_text(s+'\n\n31b斜肩接续：31a平顶按钮被打回，31b从30k重新制作后消除柱帽；前肩纵深和走向、旧背槽仍需修改。两版实际五图与独立审查已保存，生产未改。见 `reviews/reference-view-1342-progress-31b.json` 与 `reviews/round-31b-back-cleft-independent.md`。全部20参考及原开场Goal active。\n',encoding='utf-8')
p=R/'reviews/round-31-worklog.md'
with p.open('a',encoding='utf-8') as f:
    f.write('\n\n## 31b终态、独立审查与接续\n\n31b根28261已exit0，五张实际GPU原图根与独立均已直接查看。199冻结绑定匹配，每视角59实际落点相对30k最大差0.000167846680m，基础样本最大差0.000045776367m。原生/常规编辑源、完整支承和GPU检查均结束，不重复运行。\n\n31b消除31a平顶按钮，斜根更自然，保留此改进；左肩x560–690/y490–588连续顶面偏长，中肩x716–812/y522–618走向相近，后接暗缝和背面旧长槽仍未解决。主壳2156三角闭合及面积/体积仅为几何证据，整体视觉未接受。\n\n背槽实际定位脚本 `captures/localize_island_31b_back_cleft.py` 将D相机反转到Blender约(-70,65,35)，四像素最近命中主面309/1454/1467/1467。独立源面与一环核验见 `round-31b-back-cleft-independent.md/json`：三整面不碰道路、扩张pad或当前14树盘，距pad分别1.774687/6.342076/1.374832m。近塔共享点939一环仅有浮点边界微碎片，不应冻结整面，也不允许无限扩大刀具；候选改形须保留真实旋转pad支承。1454整面延伸y17.908，不能由命中点y12.282排除所有North域关联，也不能归因整槽历史。未重跑全支承或GPU。\n\n本轮root-evidence、1342逐图注册及当前14树轴已分别保存31a/31b版本，环境/最终灯具取各自实际夜图sidecar。接续短宽偏转肩面与背槽有界重塑。全部20参考及原开场仍未完成，生产未改。\n')
print('31a/31b checkpoints saved; complete goal remains active; no Blender/GPU rerun.')
