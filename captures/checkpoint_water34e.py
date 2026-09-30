from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[1]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

runs = {
    '34c': 'water-34c-20260908T235317Z-847760e1994442d085ed8c6e530e5ce9',
    '34d': 'water-34d-20260909T000325Z-9d52dcd583c84d04a34254a8eab8e9e3',
    '34e': 'water-34e-20260909T000818Z-086f9efe84964e12b961d88e6587cb3b',
}
required = ['reviews/round-34-root-evidence.json', 'reviews/round-33f-root-evidence.json', 'reviews/round-35-storm-coast-intake.md']
for label in runs:
    for stem in [f'reviews/round-{label}-water-independent-review', f'reviews/{label}-water-independent-technical']:
        required.extend(stem + ext for ext in ['.md', '.json'])
assert all((R / p).exists() for p in required), [p for p in required if not (R / p).exists()]
outputs = ['reviews/round-34e-root-evidence.json', 'reviews/reference-view-1342-progress-34e.json', 'reviews/round-34e-worklog.md']
assert not any((R / p).exists() for p in outputs)
entries = []
for label, rid in runs.items():
    run = R / 'captures/validation_runs' / rid
    manifest = read(run / 'manifest.json')
    plan = read(R / 'captures' / f'water_study_{label}' / 'design-plan.json')
    assert manifest['status'] == 'passed' and all(s['status'] == 'passed' for s in manifest['stages'])
    for p, binding in manifest['artifacts'].items():
        assert sha(run / p) == binding['sha256'], (label, p)
    views = []
    for name in ['night-reference', 'night-water-near', 'night-water-shift', 'night-time18', 'day-reference']:
        p = run / 'images' / (name + '.png')
        side = Path(str(p) + '.json')
        data = read(side)
        assert data['run_id'] == rid and data['water_shader_sha256'] == plan['shader_sha256']
        assert not data['production_modified']
        assert data['rightcoast_glb_sha256'] == 'dcef43b72ef7732c54321d2c522c4d22292283a835fb6248a8f5d0142af38da6'
        assert data['world_sha256'] == '6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8'
        assert data['environment_study']['sampled_world_time'] == (18 if name == 'night-time18' else 0)
        views.append(dict(name=name, path=str(p.relative_to(R)), sha256=sha(p), sidecar_sha256=sha(side),
                          camera=data['camera'], sampled_world_time=data['environment_study']['sampled_world_time'],
                          root_directly_viewed=True))
    entries.append(dict(label=label, run_id=rid, run_status='passed', binding_count=len(manifest['artifacts']),
                        all_bound_sha_match=True, shader_sha256=plan['shader_sha256'], views=views,
                        visual_accepted=False, root_gpu_terminal=True))

note = '''**最新34c/d/e海面均完成五张真实GPU图与独立审查，整体仍需视觉返工；海岸接续33f。** 34c改为按水面点反射实际月心/半径，恢复蓝色粗糙反射层；34d绑定4塔与9村灯真实灯芯，并以真实塔身不透明面替代反射查询中的粗碰撞体；34e加入54港岸灯至67源。暖反射仍是零星点/软橙片，海面横纹与近处宽片仍未达到参考。34e的.024/.006粗糙度、18倍增益是显式艺术参数，不能称物理标定；静态64×32遮挡图每源只覆盖450m，细遮挡边界近似，仍无完整云/岛/屋窗场景反射。34c重复记录材质绑定的问题在34d/e按实例去重为1，不能把34c的两条记录说成两个独立材质。三run均passed，15原图根已直接查看，全部GPU进程结束；继承33f土地支承，不重复8839铺地检查。水仍为平几何配材质分片法线。详见 `reviews/round-34e-root-evidence.json` 与 `reviews/round-34e-worklog.md`。当前33f/A32f/B20l/C-D31i保留为未完成候选，生产17e/18c/19h未改。下一步围绕参考可见差距继续真实场景制作，并推进同世界其他参考区域和天气；不能用灯点参数循环代替全部20参考。完整20参考及原开场Goal active，未接受、未完成。以下历史不能覆盖本段。'''

evidence = dict(runs=entries, bindings={p: sha(R / p) for p in required}, goal='active',
                production_modified=False, all_reference_goal_complete=False, coast_candidate='33f',
                water_status='34c/d/e visual rework required',
                inherited_land_checks='33f; no repeated paving or whole-world suite',
                retained_limitations=['flat ocean geometry', 'no complete scene reflection',
                                      'finite static occlusion atlas', 'artistic roughness and gain'],
                next_action='reviews/round-35-storm-coast-intake.md; preserve unfinished coast and water candidates.')
(R / outputs[0]).write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
progress = dict(reference='ref/1342.png', reference_sha256=sha(R / 'ref/1342.png'),
                status='in_progress_not_accepted', coast='33f', latest_water_run=runs['34e'],
                water_accepted=False, root_evidence=outputs[0], complete_goal='active')
(R / outputs[1]).write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(R / outputs[2]).write_text('# 34c/d/e 海面阶段记录\n\n' + note + '\n\n'
    '34c修复有限月盘方向；34d验证13实际发光表面/26624静态射线；34e扩大到67实际表面/137216静态射线。'
    '各版独立审查、五原图与冻结输入均绑定在根证据中。所有视觉失败保留，技术通过不等于艺术接受。'
    '34d视觉报告曾因长JSON输出截断误判Omni字段缺失，独立审查已直接读取13条记录纠正后才纳入本检查点。'
    'manifest中的历史expected_counts不是此次实际执行的全套测试，不作通过声明。\n', encoding='utf-8')
for name in ['WORKSPACE_RESUME.md', 'reviews/LOOP.md', 'REFERENCE_SCENES.md', 'WORLD_SCENE_PLAN.md']:
    p = R / name
    s = p.read_text(encoding='utf-8')
    head, tail = s.split('\n', 1)
    assert note not in s
    p.write_text(head + '\n\n' + note + '\n' + tail, encoding='utf-8')
print(json.dumps(dict(runs=[dict(label=e['label'], bindings=e['binding_count']) for e in entries], goal='active', water='rework')))
