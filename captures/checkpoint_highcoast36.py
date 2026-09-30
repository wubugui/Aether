"""Bind the completed 36a evidence without rerunning native/GPU stages."""
from pathlib import Path
import json, hashlib

R = Path(__file__).resolve().parents[1]
RUN_ID = 'highcoast-36a-20260909T011148Z-9fccf1ba029c4825a86a43677bd1c019'
RUN = R / 'captures/validation_runs' / RUN_ID
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
required = [
    'reviews/round-36a-highcoast-independent-review.md',
    'reviews/round-36a-highcoast-independent-review.json',
    'reviews/36a-highcoast-independent-technical.md',
    'reviews/36a-highcoast-independent-technical.json',
    'reviews/36-highcoast-occupancy-intake.md',
    'reviews/36-highcoast-occupancy-intake.json',
    'reviews/36-terrain-savedmesh-intake.json',
    'reviews/round-36b-highcoast-design-brief.md',
]
assert all((R / p).exists() for p in required)
outputs = ['reviews/round-36-root-evidence.json',
           'reviews/reference-1125-1341-progress-36.json',
           'reviews/round-36-worklog.md']
assert not any((R / p).exists() for p in outputs)
manifest = read(RUN / 'manifest.json')
assert manifest['status'] == 'passed'
for p, binding in manifest['artifacts'].items():
    assert sha(RUN / p) == binding['sha256'], p
model = read(R / 'captures/highcoast_study_36a/model-report.json')
runtime = read(RUN / 'images/highcoast-runtime.json')
flight = read(RUN / 'images/flight-traverse.json')
assert len(model['native_tiles']) == len(runtime['tiles']) == 14
assert len(runtime['scatter_changes']) == 2276
assert runtime['scatter_total_preserved'] == 54800
assert not runtime['unresolved'] and not runtime['support_failures']
assert len(flight['samples']) == 65
views = []
for name in ['storm-high', 'storm-coast-low', 'estuary-high', 'shore-low',
             'highcoast-back', 'south-seam', 'river-mouth',
             'flight-start', 'flight-middle', 'flight-end']:
    p = RUN / 'images' / (name + '.png')
    side = Path(str(p) + '.json')
    data = read(side)
    assert data['run_id'] == RUN_ID and not data['production_modified']
    assert data['highcoast_revision']['report_sha256'] == sha(RUN / 'images/highcoast-runtime.json')
    assert 'images/' + p.name in manifest['artifacts']
    views.append(dict(name=name, path=str(p.relative_to(R)), sha256=sha(p),
                      sidecar_sha256=sha(side), camera=data['camera'],
                      root_directly_viewed=True))
errors = RUN / 'highcoast-world-views-error.log'
assert not errors.read_text(encoding='utf-8').strip()
note = '''**最新36a高岸已完成14个Blender地形块、同世界网格/碰撞/散布装配及10张真实GPU图，视觉仍不接受。** 依据16块实际保存网格和独立占用核对，将编辑域西扩为X[-3750,-900]、Z[-4400,-2150]；14块共9410点改变，原XZ拓扑保持，2276个实际散布实例重新落地或移至干坡，总54800保持。原生源在 `captures/highcoast_study_36a/`，候选原生地形场景/散布资源在36a run的 `images/native-scenes/`。运行passed、错误日志为空，根与独立审查直接查看10图；近海连续大陡坡、暗部细节丢失、云板/旧云岩球和水光仍需返工。65步是自动相机观察，不是载具输入验收；末点虽有50m竖向净距，前方约25m的真实陡壁仍遮满画面。河口确有海面下床，但第8个上游控制点实际为约238.5m山坡，不能称8点全部潮汐通道。接续 `reviews/round-36b-highcoast-design-brief.md`：调整低岬/草肩/林坡/远峰层次，增加沿岸观察并改正前方爬升路线。独立结论和绑定见 `reviews/round-36-root-evidence.json`、`reviews/round-36-worklog.md`。36a原生/GPU均已结束，不重跑旧版；生产17e/18c/19h未改，全部20参考与原开场Goal保持active。以下历史不能覆盖本段。'''
evidence = dict(
    run_id=RUN_ID, run_status=manifest['status'],
    binding_count=len(manifest['artifacts']), all_manifest_bindings_match=True,
    views=views, root_gpu_terminal=True, error_log_sha256=sha(errors),
    model_report=model, runtime_report_sha256=sha(RUN / 'images/highcoast-runtime.json'),
    flight_report_sha256=sha(RUN / 'images/flight-traverse.json'),
    bindings={p: sha(R / p) for p in required},
    visual_accepted=False, production_modified=False, goal='active',
    all_reference_goal_complete=False,
    limitations=['Axis support does not prove full trunk/rock footprint support.',
                 '65 automatic camera samples do not prove vehicle/free-flight gameplay.',
                 'Flight-end is blocked by a real forward cliff despite vertical clearance.',
                 'Local native scenes/resources are candidate assets, not an installed production world.',
                 'The last upstream control is a high slope, not a tidal bed.'],
    next_action='reviews/round-36b-highcoast-design-brief.md')
(R / outputs[0]).write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(R / outputs[1]).write_text(json.dumps(dict(
    references={str(p.relative_to(R)): sha(p) for p in [R / 'ref/1125.png', R / 'ref/1341.png']},
    status='in_progress_not_accepted', root_evidence=outputs[0], latest_run=RUN_ID,
    next_action=evidence['next_action']), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(R / outputs[2]).write_text('# 36 高岸与河口阶段记录\n\n' + note + '\n\n'
    '实际14块源保留为独立可编辑.blend，并导出GLB；本轮没有重跑整世界生成器。初稿12块/X最小值-2600只是来源调查前的暂定范围，实际岸线核对后扩为16块调查、14块修改。\n\n'
    '候选运行继续保留33f港岸、A32f/B20l/C-D31i与35c空间天气；程序绑定及未改落点由本轮运行检查。完整树干/石足迹、飞行体走廊及所有天气/内景尚无本轮完整证据。独立36a技术报告中的限制优先于运行passed字样。\n\n'
    '河口水体使用现有海平面，尚无真实河流坡降或瀑布；第8个控制点收束到陆上山坡。图像可读河湾并不等于全参考完成。下一版必须保留本轮终点遮挡和其他失败图，不用改相机掩盖实体坡形问题。\n', encoding='utf-8')
for name in ['WORKSPACE_RESUME.md', 'reviews/LOOP.md', 'REFERENCE_SCENES.md', 'WORLD_SCENE_PLAN.md']:
    p = R / name
    current = p.read_text(encoding='utf-8')
    heading, tail = current.split('\n', 1)
    assert note not in current
    p.write_text(heading + '\n\n' + note + '\n' + tail, encoding='utf-8')
print(json.dumps(dict(run=RUN_ID, bindings=len(manifest['artifacts']), images=len(views), goal='active')))
