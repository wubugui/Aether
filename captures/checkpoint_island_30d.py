from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
run=R/'captures/validation_runs/lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(run/'manifest.json');inc=read(R/'reviews/round-30d-runtime-incremental.json')
review=R/'reviews/round-30d-island-independent-review.md';assert review.exists()
assert m['passed'] and m['status']=='passed' and inc['passed'] and inc['run_id']==m['run_id']
assert inc['all_bound_hashes_match'] and inc['binding_count']==len(m['artifacts'])
views=[]
for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
    p=run/'images'/(name+'.png');q=Path(str(p)+'.json');d=read(q)
    views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(q),root_directly_viewed=True,camera=d['camera']))
out=dict(run_id=m['run_id'],manifest_sha256=sha(run/'manifest.json'),terminal_passed=True,binding_count=inc['binding_count'],all_bound_hashes_match=True,incremental_runtime_report='reviews/round-30d-runtime-incremental.json',root_views=views,independent_review=str(review.relative_to(R)),independent_review_sha256=sha(review),independent_geometry='reviews/round-30d-independent-geometry.json',visible_slope_localization='reviews/round-30d-visible-slope-localization.json',visual_accepted=False,production_installed=False,full_goal_status='active',root_findings=['Three real cutbacks expose retained shoulders and add short recesses in reference/back views; locally useful, some cut edges still too straight.','Day-c-front broad main grey slope remains; actual camera is Blender(65,-70,40). Six selected unobstructed pixel rays hit southern-to-eastern main terrain, not the three targeted west/north rock shoulders.','Choose next authored cuts from actual visible source faces and exact occupied boundaries; preserve compact island/native-building scale and collar-free exterior.'])
p=R/'reviews/round-30d-root-evidence.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
d=read(run/'images/night-reference.png.json');registry=read(R/'reviews/reference-view-1342-progress-30c.json')
registry.update(run_id=m['run_id'],camera=d['camera'],reference_image=views[0],environment_before_lantern_adapter=d['environment_study'],environment_report_source=str((run/'images/night-reference.png.json').relative_to(R)),final_lantern_configuration=d['lantern_lighting'],geometry_basis={'islands':'A/B20l; C/D30d three local Boolean cutbacks of30c welded exterior;17rocks/path/native buildings and authored D placement retained','lighthouse':'19h native','harbor':'22g','village_and_headland':'26b','production':'17e/18c/19h unchanged'},evidence=['reviews/round-30-worklog.md','reviews/round-30d-root-evidence.json','reviews/round-30d-island-independent-review.md','reviews/round-30d-independent-geometry.json','reviews/round-30d-cutback-intake.json','reviews/round-30d-runtime-incremental.json'],remaining=['Read latest30d independent visual conclusions before choosing retained cutbacks/refinement; measured exposure is not natural-rock visual acceptance.','Refine wide upper rock planes, short staggered shoulders, cliff/cut transitions and shoreline; preserve actual occupied support, refit affected path/scatter/collision.','Fixed reference position/orientation, cloud/water/warm light, other islands/mainland/villages, all20 references plus original opening and weather/time/flying-space observations remain incomplete.'])
registry['evidence'].append('reviews/round-30d-visible-slope-localization.json')
registry['evidence'].append('reviews/round-30d-visible-slope-independent.json')
registry['remaining'][0]='Retain30d local short recesses as work-in-progress. Correct too-straight cut edges and directly located south/east-facing broad slope; do not keep attributing day-c-front grey wall to West/Southwest/North.'
(R/'reviews/reference-view-1342-progress-30d.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
position=max(v['maximum_position_delta_m'] for v in inc['views']);footing=max(v['maximum_footing_delta_m'] for v in inc['views'])
note=f'**最新30d已完成三处实体切削、五GPU及独立审查，整体仍未接受。** 从30c焊接源用Blender真实切削露出West/Southwest/North低肩，17岩和路径保持；完整道路/pad/现有树轴支承区域几何保持，水上肩露出投影约51.832/43.206/58.213m²。19原生件、196绑定核对，59落点相对30a最大差{position:.9f}m、基础差{footing:.9f}m。固定参考/背面新增短凹折可保留，但局部切口仍直；day-c-front正面宽灰坡基本未变。**方向纠正：该相机Blender(65,-70,40)，六处灰坡像素实际射线命中南到东侧mainterrain；不能继续全归West/SW/North。** 以 `reviews/round-30d-visible-slope-localization.json` 的真实源面及保护边界决定下一稿，不盲目扩大旧刀具。接续 `reviews/round-30-worklog.md`、`reviews/round-30d-island-independent-review.md`、`reviews/reference-view-1342-progress-30d.json`。全部30d建模/重开/GPU已结束，无待等句柄，不重跑已通过检查。生产17e/18c/19h未改，全部20参考及原场景Goal active。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '**最新30d已完成' not in s;first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;s=p.read_text(encoding='utf-8');assert '30d局部切削接续' not in s;p.write_text(s+'\n\n30d局部切削接续：实际露出三个短低岩肩，完整支承保留，五GPU与独立审查完成；新增凹折局部可保留，直切口及正面大灰坡仍需改。day-c-front相机在东南，六像素射线定位主坡位于南/东侧，后续按真实源面与保护边界改形。详见 `reviews/reference-view-1342-progress-30d.json`、`reviews/round-30d-visible-slope-localization.json`，完整20参考及原开场Goal active，生产未变。\n',encoding='utf-8')
print('30d evidence and reference registry saved; Goal active')
