"""Final round28 evidence and continuation docs; run after actual three-view review."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-lighting-28h-20260908T163354Z-e69c09f62fc547389d39adbbd0011225'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');assert m['passed'] and m['status']=='passed'
ind=R/'reviews/round-28h-lantern-independent-review.md';assert ind.is_file(),'Independent final review still pending'
for name,row in m['artifacts'].items():assert sha(run/name)==row['sha256'],name
views=[]
for view in ['reference','lamp-close','beam-side']:
    im=run/'images'/(view+'-beam-only.png');d=read(Path(str(im)+'.json'))
    assert d['world_sha256']==sha(R/'scenes/world/World.tscn')
    assert len(d['core_nodes'])==4 and all(c['cast_shadow']==1 and c['bounds_contains_light_origin'] for c in d['core_nodes'])
    assert len(d['beam_states'])==4 and all(abs(b['energy']-1.3)<1e-5 for b in d['beam_states'])
    views.append({'name':view,'path':str(im.relative_to(R)),'png_sha256':sha(im),'sidecar_sha256':sha(Path(str(im)+'.json')),'camera':d['camera'],'root_directly_viewed':True,'core_nodes':d['core_nodes'],'beam_states':d['beam_states']})
assert sha(run/'images/final-beam-side.png')==sha(run/'images/beam-side-beam-only.png')
whole=read(run/'images/final-beam-side.png.json')
assert all(abs(b['beam_meshes'][0]['energy']-1.3)<1e-5 for b in whole['lantern_lighting']['beams'])
out={'run_id':m['run_id'],'terminal_passed':True,'all_artifact_sha256_verified':True,'binding_count':len(m['artifacts']),'manifest_sha256':sha(run/'manifest.json'),'views':views,'independent_review':str(ind.relative_to(R)),'scope':'Three final actual GPU views from one loaded continuous World. Original core shadow casters retained, only beam energy doubled over28f. Final shader28f already independently checked for finite-cone interval precision; native28a controls unchanged. No full-day/reverse recapture at final energy, no moving/animated thin-object occlusion or full-reference acceptance.','visual_acceptance':False,'production_installed':False,'full_goal_status':'active'}
(R/'reviews/round-28h-root-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
registry={'reference':'ref/1342.png','reference_sha256':sha(R/'ref/1342.png'),'status':'in_progress_not_accepted','scope':'All20 references and original opening remain the goal; this is temporary1342 coast work in the same continuous World. No characters/HUD reconstruction.','camera':views[0]['camera'],'world_sha256':whole['world_sha256'],'run_id':m['run_id'],'reference_image':views[0],'final_lantern_configuration':whole['lantern_lighting'],'world_time':0,'environment_basis':'27d editable clouds and27f water; environment_report is before28 lantern adapter, so its old local-light values are superseded by final_lantern_configuration.','environment_before_lantern_adapter':whole['environment_study'],'geometry_basis':{'islands':'20l','lighthouse':'19h native','harbor':'22g','village_and_headland':'26b','production':'17e/18c/19h unchanged'},'evidence':['reviews/round-28-worklog.md','reviews/round-28h-root-evidence.json','reviews/round-28h-lantern-independent-review.md','reviews/round-28g-lantern-independent-review.md','reviews/round-28f-independent-interval-check.json'],'remaining':['Source focal glow and warm receiver/water response below reference','Cloud shape/layer composition, repetitive water streaks, regular island silhouettes and barren headland require refinement','Full flying-space observation, dynamic weather/time coupling, other19 references and original opening not accepted'],'production_installed':False,'full_goal_status':'active'}
(R/'reviews/reference-view-1342-progress-28h.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
note='**最新28h灯塔体积光候选完成三个实际GPU视角和独立限定审查，整体仍未达标。** 修复无光照材质错误输出，使用真实锥体积分、近体积原点求交与宽度/距离衰减，保留光束能量1.3。28e远端橙雾打回；28g对照不支持“灯芯投影挡住自身暖光”的原因判断，28h已保留原灯芯投影。当前184项冻结绑定核对以 `reviews/round-28h-root-evidence.json` 实际数量为准。所有28原生/GPU进程已结束，不重启旧失败版本。接续 `reviews/round-28-worklog.md`、`reviews/round-28h-lantern-independent-review.md` 与 `reviews/reference-view-1342-progress-28h.json`；继续灯源/暖水光、云水、主岩岸/群岛/聚落与完整20参考范围。生产仍17e/18c/19h，Goal active。'
note=note.replace('当前184项冻结绑定核对以 `reviews/round-28h-root-evidence.json` 实际数量为准。',f'当前{len(m["artifacts"])}项冻结绑定SHA匹配。')
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '**最新28h灯塔' not in s
    first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '28h光束接续' not in s
    p.write_text(s+'\n\n28h光束接续：同一1342机位保留28f真实锥体积分和最终能量1.3，原灯芯投影保持；三实际GPU、独立审查和冻结SHA检查完成，仅局部改进。暖源/暖水光、云水与岸岛聚落仍不符，完整20参考目标未完成。最新登记 `reviews/reference-view-1342-progress-28h.json`，完整过程 `reviews/round-28-worklog.md`。未安装生产。\n',encoding='utf-8')
print(json.dumps({'run':m['run_id'],'bindings':len(m['artifacts']),'root_views':3,'goal':'active'},ensure_ascii=False))
