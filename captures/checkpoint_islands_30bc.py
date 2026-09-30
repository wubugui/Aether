from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runs={'30b':'lantern-island-30b-20260908T181107Z-79169d5784aa499ea0429f797ff3fc6e','30c':'lantern-island-30c-20260908T181715Z-31c81298860748f3ac9257c092e5f4b5'}
for label,name in runs.items():
    run=R/'captures/validation_runs'/name;m=read(run/'manifest.json')
    inc=read(R/f'reviews/round-{label}-runtime-incremental.json')
    review=R/f'reviews/round-{label}-island-independent-review.md';geometry=R/f'reviews/round-{label}-independent-geometry.json'
    assert review.exists() and geometry.exists()
    assert m['passed'] and m['status']=='passed' and inc['passed'] and inc['run_id']==m['run_id']
    assert inc['binding_count']==len(m['artifacts']) and inc['all_bound_hashes_match']
    views=[]
    for view in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
        p=run/'images'/(view+'.png');q=Path(str(p)+'.json');d=read(q)
        views.append(dict(name=view,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(q),root_directly_viewed=True,camera=d['camera']))
    findings=['30b removes the middle ring and lowers/clusters short shoulders; low double bands diminish, but continuous0.65m terrain collar remains.','30c welds actual terrain and rock exterior, deleting collar and internal caps; directly viewed five images confirm narrow band removed.','Broad upper slopes, insufficient exposed short interlocking rock shoulders, overly uniform waterline and full lighting/environment/reference differences remain.']
    out=dict(run_id=m['run_id'],manifest_sha256=sha(run/'manifest.json'),terminal_passed=True,binding_count=inc['binding_count'],all_bound_hashes_match=True,incremental_runtime_report=f'reviews/round-{label}-runtime-incremental.json',root_views=views,independent_review=str(review.relative_to(R)),independent_review_sha256=sha(review),independent_geometry=str(geometry.relative_to(R)),visual_accepted=False,production_installed=False,full_goal_status='active',root_findings=findings[:1] if label=='30b' else findings[1:])
    p=R/f'reviews/round-{label}-root-evidence.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    registry=read(R/'reviews/reference-view-1342-progress-30a.json')
    d=read(run/'images/night-reference.png.json')
    registry.update(run_id=name,camera=d['camera'],reference_image=views[0],final_lantern_configuration=d['lantern_lighting'],geometry_basis={'islands':f'A/B20l; C/D{label} compact land with local coast topology;30a top/path/pads/Dplacement retained','lighthouse':'19h native','harbor':'22g','village_and_headland':'26b','production':'17e/18c/19h unchanged'},evidence=['reviews/round-30-worklog.md',f'reviews/round-{label}-root-evidence.json',str(review.relative_to(R)),str(geometry.relative_to(R)),f'reviews/round-{label}-runtime-incremental.json'],remaining=['Retain30c collar-free welded exterior and compact30a proportions. Refine actual exposed rock shoulders and adjacent broad terrain slopes; intersection alone is not visible contribution.','West/Southwest shoulders fully contained in core at sampled0.5/2/4m sections; North mostly contained. Adjust only necessary local exposure/cutbacks; East/Northwest already largely exposed, do not move all rocks uniformly outward.','Maintain complete actual occupied supports and refit affected collision/scatter if changing terrain. Fixed reference view still slightly narrow/left.','All20 references plus original opening, weather/time, water/clouds/warm lights, other islands/mainland/villages and flying-space review remain unfinished.'])
    registry['environment_before_lantern_adapter']=d['environment_study']
    registry['environment_report_source']=str((run/'images/night-reference.png.json').relative_to(R))
    (R/f'reviews/reference-view-1342-progress-{label}.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
inc=read(R/'reviews/round-30c-runtime-incremental.json')
position=max(v['maximum_position_delta_m'] for v in inc['views']);footing=max(v['maximum_footing_delta_m'] for v in inc['views'])
note=f'**最新30c已完成焊接外壳、五实际GPU及独立限定审查，整体仍需返工。** 30b删除主岩中间环并缩短/嵌合岩肩；30c进一步移除真实0.65m地表侧裙和内部重合cap，19原生可编辑分件，实际五图连续细带消除。745地表顶点、全部原顶面/路径及17岩块保持；相对30a的59落点最大差{position:.9f}m、基础样本最大差{footing:.9f}m，196绑定SHA核验。部分岩肩被主岛包裹，相交不等于可见岩根；下一步以30c源局部重塑外露短肩及相邻大灰坡，优先West/Southwest/North，不能所有岩块统一外移。全部30b/c原生和GPU进程均已结束，无待等引擎，不重跑已通过检查。接续 `reviews/round-30-worklog.md`、`reviews/round-30c-island-independent-review.md`、`reviews/reference-view-1342-progress-30c.json`。生产17e/18c/19h未改，全部20参考及原场景Goal active。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '**最新30c已完成' not in s;first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '30c焊接岸体接续' not in s;p.write_text(s+'\n\n30c焊接岸体接续：30b局部侧片和短肩之后，30c移除0.65m地表裙与内部cap，五GPU确认细带消除，限定原生/实际几何和59落点核验通过。整体未接受；下一步按实际外露贡献重塑局部肩根与宽灰坡，不把完全包裹的岩块交叠当视觉成功。详见 `reviews/reference-view-1342-progress-30c.json` 与 `reviews/round-30-worklog.md`。全部20参考及原图Goal active，生产未改。\n',encoding='utf-8')
print('30b/30c evidence and latest resume saved; full Goal active; deltas',position,footing)
