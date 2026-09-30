from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B='highcoast-36b-20260909T015215Z-0c71bb650bcf43d890987772791f1dff'
G='highcoast-reopen36g-20260909T023100Z-805ece112b8a42bcb3639d99f9e39ad6'
required=['reviews/round-36b-highcoast-independent-review.md','reviews/round-36b-highcoast-independent-review.json',
          'reviews/36b-highcoast-independent-technical.md','reviews/36b-highcoast-independent-technical.json',
          'reviews/36c-candidate-native-independent.md','reviews/36c-candidate-native-independent.json',
          'reviews/36b-candidate-world-save-intake.md','captures/candidate_highcoast36c/repair-report.json',
          'captures/candidate_highcoast36c/README.md','run-highcoast-candidate.cmd','open-highcoast-candidate.cmd']
assert all((R/p).exists() for p in required)
outputs=['reviews/round-36bg-root-evidence.json','reviews/round-36bg-worklog.md','reviews/reference-1125-1341-progress-36bg.json']
assert not any((R/p).exists() for p in outputs)
entries=[]
for rid,expected in [(B,'failed'),(G,'passed')]:
    run=R/'captures/validation_runs'/rid;m=read(run/'manifest.json')
    assert m['status']==expected
    for name,record in m['artifacts'].items():assert sha(run/name)==record['sha256'],name
    views=[]
    for image in sorted((run/'images').glob('*.png')):
        side=Path(str(image)+'.json')
        if side.exists():assert read(side)['run_id']==rid
        views.append(dict(path=str(image.relative_to(R)),sha256=sha(image),root_directly_viewed=True,
                          manifest_bound=('images/'+image.name) in m['artifacts'],sidecar_sha256=sha(side) if side.exists() else None))
    assert len(views)==(12 if rid==B else 2)
    entries.append(dict(run_id=rid,status=expected,binding_count=len(m['artifacts']),all_existing_bindings_match=True,views=views,root_process_terminal=True))
actual=read(R/'captures/validation_runs'/G/'images/candidate-reopen.json')
assert actual['scatter_total']==54797 and len(actual['tile_checks'])==14
assert (R/'captures/validation_runs'/G/'native-candidate-reopen-error.log').stat().st_size==0
note='''**最新36b地形与36c完整原生候选已接续，36g新进程重开/短程控制通过，整体美术仍未接受。** 36b在14个保存Blender块中改形10659点，拓宽河谷、降低并后退山脊；2537个散布增量保持高岸装配阶段54800总数。12张实际GPU显示中段河岸和终点视野改善，但沿岸长直高边、大草坡、云板/旧云块与水面仍需返工。36b额外保存完整World时14条Windows外链错误，伴随2条纹理泄漏，run failed；12图未在失败manifest绑定，根/独立另行记录。36c只修新World/Game副本的外链和天气目录，保留几何。完整候选继承港路避让的2松1岩删除，实际773组54797实例，与逐项记录一致。36g通过新进程自然初始化、14块网格/碰撞、22新增松组owner/编辑辅助和现有控制器240物理帧；约88.955m是Z约-1910港湾的起终点位移，不是新高岸路线或完整走廊验收。入口为 `run-highcoast-candidate.cmd` / `open-highcoast-candidate.cmd`；原生World/Game在 `captures/candidate_highcoast36c/`，Blender源在 `captures/highcoast_study_36b/`。运行入口已实际加载；编辑器界面提取/重存和自动重导入仍未验。全部本轮进程已结束，不重跑旧版；生产保持，全部20参考与原开场Goal active。证据见 `reviews/round-36bg-root-evidence.json`、`reviews/round-36bg-worklog.md`。以下旧阶段不能覆盖本段。'''
data=dict(runs=entries,bindings={p:sha(R/p) for p in required},native_model_report=read(R/'captures/highcoast_study_36b/model-report.json'),
          candidate_reopen=actual,goal='active',visual_accepted=False,all_reference_goal_complete=False,production_modified=False,
          latest_native_world='captures/candidate_highcoast36c/World36c.tscn',latest_game='captures/candidate_highcoast36c/Game36c.tscn',
          failures_preserved=['36b GPU completed12views but scene-save errors',
              'highcoast-reopen36c-20260909T020226Z-40a1914bea154022805eaf6f61e2a120: wrapper binding preflight failed before engine',
              'highcoast-reopen36d-20260909T020325Z-29dcab33c8924d80a887207b5aaa08e6: stale54800 assertion; orphan cleanup leaked and process ended3221225477'],
          scope_limits=['New65point camera route is not physical vehicle playback.','36g port flight does not cover edited highcoast terrain.',
                        'World streaming was frozen only by checker after natural initialization.','Read/apply sampled one pine; editor extract/re-save remains unverified.'])
(R/outputs[0]).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/outputs[1]).write_text('# 36b–g 高岸与完整候选接续\n\n'+note+'\n\n'
    '36b建模没有覆盖旧原生源或整体生成世界。新增机位按本世界岸线设计，不能称参考原地图方位。原两机位继续保留。独立连续中线审查证明相机前方240m最小竖直净高约64.744m，但不是完整视锥/载具体积扫掠。九河控最后约284.286m仍为陆上过渡，不能称九点全部潮汐水道。\n\n'
    '36c路径修复基于原36b保存TSCN副本，只修改14个World外链、2个Game外链与天气目录字段。局部TSCN内嵌ArrayMesh，captures继续忽略自动导入；源.blend/GLB保留。36g后再次确认源/冻结场景SHA一致。根直接查看本阶段14张GPU原图。\n\n'
    '原生候选World来自未运行的生产实例，只替换本轮地形和真实散布并保留作者字段，不保存运行缓存与临时root碰撞。Game另外保留先前候选港岸/岛屿等区域，启动35c空间天气并继承既有操作。没有新增角色或载具。\n\n'
    '下一步继续精细化长直岸边/低岩岬与草肩，修正云体和明暗层次，同时推进中央河湾/城堡平原等其余参考区域；已能运行的完整候选作为可继续工作的入口，不把单一区域无止境微调当作全部世界进展。\n',encoding='utf-8')
(R/outputs[2]).write_text(json.dumps(dict(status='in_progress_not_accepted',root_evidence=outputs[0],latest_geometry='36b',latest_native_candidate='36c',latest_reopen_run=G),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md','REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');heading,tail=s.split('\n',1)
    p.write_text(heading+'\n\n'+note+'\n'+tail,encoding='utf-8')
print(json.dumps(dict(runs=[dict(run=e['run_id'],status=e['status'],bindings=e['binding_count']) for e in entries],images=14,goal='active')))
