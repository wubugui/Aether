from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-island-30h-20260908T191003Z-b60fbd9ddc33459aa01a7396a355b6db'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');inc=read(R/'reviews/round-30h-runtime-incremental.json')
review=R/'reviews/round-30h-island-independent-review.md';assert review.exists()
assert m['passed'] and m['status']=='passed' and inc['passed'] and inc['run_id']==m['run_id']
assert inc['all_bound_hashes_match'] and inc['binding_count']==len(m['artifacts'])
views=[]
for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
    p=run/'images'/(name+'.png');q=Path(str(p)+'.json');d=read(q)
    views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(q),root_directly_viewed=True,camera=d['camera']))
findings=['Southern/eastern visible grey slope changes, but new dense vertical pointed triangles and fan-shaped recesses remain unlike reference short broad rock shoulders.', 'Protected occupied surfaces, path and17rocks retained; geometry/runtime checks do not imply visual acceptance.', 'Do not retain30e/f/g failed meshes or repeat their GPU runs.30h successful native pipeline can inform a revised authoring method, but the new fluted slope is not visually accepted.', 'Next sculpt broad staggered facets and transitions from actual occupied plateau to coast. Avoid adding further dense cutter rim samples or only lowering nominal floor planes. Existing narrow straight back slot also remains.']
out=dict(run_id=m['run_id'],manifest_sha256=sha(run/'manifest.json'),terminal_passed=True,binding_count=inc['binding_count'],all_bound_hashes_match=True,incremental_runtime_report='reviews/round-30h-runtime-incremental.json',root_views=views,independent_review=str(review.relative_to(R)),independent_review_sha256=sha(review),independent_geometry='reviews/round-30h-independent-geometry.json',near_protection='reviews/round-30h-near-protection.json',visual_accepted=False,production_installed=False,full_goal_status='active',root_findings=findings)
p=R/'reviews/round-30h-root-evidence.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
d=read(run/'images/night-reference.png.json');registry=read(R/'reviews/reference-view-1342-progress-30d.json')
registry.update(run_id=m['run_id'],camera=d['camera'],reference_image=views[0],environment_before_lantern_adapter=d['environment_study'],environment_report_source=str((run/'images/night-reference.png.json').relative_to(R)),final_lantern_configuration=d['lantern_lighting'],geometry_basis={'islands':'A/B20l; C/D30h southern/eastern faceted Boolean cuts from30d;17rocks/path/native buildings and authored D placement retained','lighthouse':'19h native','harbor':'22g','village_and_headland':'26b','production':'17e/18c/19h unchanged'},evidence=['reviews/round-30-worklog.md','reviews/round-30h-root-evidence.json','reviews/round-30h-island-independent-review.md','reviews/round-30h-independent-geometry.json','reviews/round-30h-near-protection.json','reviews/round-30h-runtime-incremental.json'],remaining=findings+['All20references plus original opening, other island/mainland geometry, village, cloud/water/warm light, weather/time and free-flight spatial checks remain incomplete.'])
(R/'reviews/reference-view-1342-progress-30h.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
position=max(v['maximum_position_delta_m'] for v in inc['views']);footing=max(v['maximum_footing_delta_m'] for v in inc['views'])
note=f'**最新30h原生与五GPU、独立检查完成，造型仍打回。** 南/东实际可见坡切削后产生密集竖向尖三角和折扇凹面，不能以闭合/支承检查通过当成参考达标。30e/f/g失败未跑GPU，失败证据保留；30h独立刀具面划分成功保存19件，主壳2550三角，路径/17岩及完整道路/pad/树支承保持。六目标实际切深约2.933/2.878/0.104/1.261/0/2.562m，不沿用名义平面削深。196绑定核对，59落点相对30a最大差{position:.9f}m、基础差{footing:.9f}m。下一稿改实际大面组织和短宽错位肩，避免继续加密刀具边界造成竖向褶皱；旧背面直窄槽仍待改。接续 `reviews/round-30-worklog.md`、`reviews/round-30h-island-independent-review.md`、`reviews/reference-view-1342-progress-30h.json`。本轮原生和GPU进程均结束，无待等句柄，不重跑已通过检查。生产17e/18c/19h未改，全部20参考及原场景Goal active。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '**最新30h原生' not in s;first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '30h分面切削接续' not in s;p.write_text(s+'\n\n30h分面切削接续：三次失败几何证据保留；30h成功原生与五GPU、独立支承/切深检查完成，但南东坡新增竖向尖三角与折扇凹面，视觉打回。下一稿需改变大面组织与短宽肩，不能继续以更多细面或更低名义刀具高度替代造型改进。详见 `reviews/reference-view-1342-progress-30h.json` 与独立报告，全部20参考及原场景Goal active，生产未变。\n',encoding='utf-8')
print('30h evidence and full-scope reference registry saved; Goal active')
