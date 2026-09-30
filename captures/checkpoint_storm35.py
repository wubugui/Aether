from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runs={'35a':'storm-35a-20260909T003123Z-b7154d45310e4e2482e9aff200346918','35b':'storm-35b-20260909T003744Z-443b5747f7fa4c3a9164f2609d8d953a','35c':'storm-35c-20260909T004220Z-c4392024b9a4475faaff26f81d9cbcab'}
required=['reviews/round-34e-root-evidence.json','reviews/35-storm-world-camera-intake.md','reviews/35-storm-world-camera-intake.json','reviews/round-36-highcoast-design-brief.md','reviews/36-highcoast-source-intake.json']
for label in runs:
    required.extend(f'reviews/round-{label}-storm-independent-review'+ext for ext in ['.md','.json'])
for label in ['35a','35c']:
    required.extend(f'reviews/{label}-storm-independent-technical'+ext for ext in ['.md','.json'])
assert all((R/p).exists() for p in required),[p for p in required if not (R/p).exists()]
outputs=['reviews/round-35-root-evidence.json','reviews/reference-1125-1341-progress-35.json','reviews/round-35-worklog.md']
assert not any((R/p).exists() for p in outputs)
entries=[]
for label,rid in runs.items():
    run=R/'captures/validation_runs'/rid;m=read(run/'manifest.json')
    assert m['status']==('failed' if label=='35b' else 'passed')
    for p,b in m['artifacts'].items():assert sha(run/p)==b['sha256'],(label,p)
    names=['storm-high','storm-coast-low','storm-inside','storm-edge','storm-clear','storm-flash']
    if label!='35a':names.append('storm-inside-flash')
    names.append('storm-cloud-back')
    views=[]
    for name in names:
        p=run/'images'/(name+'.png');side=Path(str(p)+'.json');d=read(side)
        assert d['run_id']==rid and not d['production_modified']
        assert d['world_sha256']=='6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8'
        assert d['rightcoast_glb_sha256']=='dcef43b72ef7732c54321d2c522c4d22292283a835fb6248a8f5d0142af38da6'
        assert len(d['storm_setup']['assets'])==12
        assert d['storm_sample']['flash']==(1 if 'flash' in name else 0)
        manifest_bound=('images/'+p.name) in m['artifacts']
        assert manifest_bound==(label!='35b')
        views.append(dict(name=name,path=str(p.relative_to(R)),sha256=sha(p),sidecar_sha256=sha(side),
                          manifest_bound=manifest_bound,root_directly_viewed=True,camera=d['camera'],sample=d['storm_sample']))
    errors=run/'storm-world-views-error.log'
    if label=='35b':assert errors.read_text().count('ERROR: Parameter "material" is null.')==4
    else:assert 'ERROR:' not in errors.read_text()
    entries.append(dict(label=label,run_id=rid,run_status=m['status'],binding_count=len(m['artifacts']),
                        all_existing_manifest_bindings_match=True,views=views,root_gpu_terminal=True,
                        error_log_sha256=sha(errors),visual_accepted=False,
                        failed_run_image_binding_note='35b images absent from failed manifest; explicitly bound here without changing its failure status.' if label=='35b' else None))
note='''**最新35风暴空间候选已完成两版Blender云体与三轮真实GPU，整体仍未视觉接受。** 35a三资产17件为厚黑囊串，七图打回，独立发现雨条按顶点循环可从9m拉长到891m；35b改为三资产六件连续云体，改善橙色漏光并增加可见闪电，但八图仍有大云板/重复边形/旧云褐岩球，且四条GLES材质null错误令run failed。35c保留35b真实云几何，按实例统一雨条循环、flash场中心对齐实际Omni，并把原/新材质引用保留在场景；八图运行passed，先前材质错误未再现但根因未隔离。根直接看完23张原图，各版独立报告已完成；35b失败图无manifest绑定，另在根证据中绑定，不伪改其状态。阴/锋/晴三世界位置、空间雨与闪电可复现，仍非完整连续飞行证明。三资产源在 `captures/storm_cloud_assets_35b/`，运行接续35c；地形/33f港岸/岛屿保持未完成候选，生产17e/18c/19h未改。下一步按 `reviews/round-36-highcoast-design-brief.md` 制作真实近海高岸、河口和山体纵深；12候选地形块仅完成来源清单，尚无36模型。云、水、其他天气、内景及全部20参考/原开场仍在Goal active范围。详见 `reviews/round-35-root-evidence.json`、`reviews/round-35-worklog.md`。全部35 GPU/Blender进程已结束，不重跑旧版。以下历史不能覆盖本段。'''
data=dict(runs=entries,bindings={p:sha(R/p) for p in required},goal='active',all_reference_goal_complete=False,production_modified=False,
          root_images_directly_viewed=23,latest_weather_candidate='35c',latest_cloud_native='captures/storm_cloud_assets_35b',
          native_cloud_sets={'35a':read(R/'captures/storm_cloud_assets_35a/model-report.json'),'35b_and_35c':read(R/'captures/storm_cloud_assets_35b/model-report.json')},
          technical_status={'35a':'rejected: vertex rain wrap','35b':'run failed: GLES material null','35c':'bounded incremental checks passed; visual rejected'},
          inherited_land='33f; no repeat whole-world or paving suite',next_action='reviews/round-36-highcoast-design-brief.md')
(R/outputs[0]).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/outputs[1]).write_text(json.dumps(dict(references={str(p.relative_to(R)):sha(p) for p in [R/'ref/1125.png',R/'ref/1341.png']},status='in_progress_not_accepted',root_evidence=outputs[0],latest_run=runs['35c'],next_action='reviews/round-36-highcoast-design-brief.md'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/outputs[2]).write_text('# 35 风暴阶段记录\n\n'+note+'\n\n'
    '35a共享天气场作用于地表/水/天空/空气与世界定向雨，闪电有60段实体和3个原生Omni。35c额外统一flash衰减中心Y230，仍是艺术衰减场而不是物理辐射度；云阴影使用有记录的空间天气场近似，没有云内部光学传输。35b/c原云31个网格也接入天气着色，形体仍需返工。\n\n'
    '三个run保持同一World及33f/A32f/B20l/C-D31i装配。35a第一次准备脚本因wood材质没有world varying停止，未运行GPU；部分文件保存在captures/storm_study_35a_prepare_failure1，补齐对应材质后才完整准备。35b引擎实际完成8图但错误gate拒绝，错误与未收集图像继续保留。35c通过不能抹除35a/b失败，也不能代表参考视觉完成。\n\n'
    '新增地形调查使用World实际Transform3D和保存.blend/GLB/碰撞来源；12块矩形候选还需真实占用和边界调查，不得直接整块抬升。旧production及全部其他参考仍未完成，不导出旧包冒充新版完成。\n',encoding='utf-8')
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md','REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');head,tail=s.split('\n',1);assert note not in s
    p.write_text(head+'\n\n'+note+'\n'+tail,encoding='utf-8')
print(json.dumps(dict(runs=[dict(label=e['label'],status=e['run_status'],bindings=e['binding_count']) for e in entries],images=23,goal='active')))
