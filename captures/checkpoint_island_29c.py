from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
run=R/'captures/validation_runs/lantern-island-29c-20260908T170924Z-4d7e5928e9e74d1ca0621a44e963b02d';m=read(run/'manifest.json');assert m['status']=='passed' and m['passed']
ind=R/'reviews/round-29c-island-independent-review.md';assert ind.exists()
for name,row in m['artifacts'].items():assert sha(run/name)==row['sha256'],name
views=[]
for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
 p=run/'images'/(name+'.png');s=Path(str(p)+'.json');d=read(s)
 assert d['world_sha256']==sha(R/'scenes/world/World.tscn')
 views.append({'name':name,'path':str(p.relative_to(R)),'png_sha256':sha(p),'sidecar_sha256':sha(s),'camera':d['camera'],'root_directly_viewed':True})
site=read(run/'actual-site-preservation.json')
out={'run_id':m['run_id'],'manifest_sha256':sha(run/'manifest.json'),'terminal_passed':True,'binding_count':len(m['artifacts']),'all_bound_hashes_match':True,'actual_site_preservation':site,'root_views':views,'independent_review':str(ind.relative_to(R)),'visual_accepted':False,'reason':'Long straight wedges read as structural ramps over old terraced island. Next iteration returns to29b and remodels original terrain/core topology outside exact protection boundaries.','production_installed':False,'full_goal_status':'active'}
(R/'reviews/round-29c-root-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
registry=read(R/'reviews/reference-view-1342-progress-28h.json')
registry.update(run_id=m['run_id'],camera=views[0]['camera'],reference_image=views[0],geometry_basis={'islands':'A/B20l; C/D29b+29c4failed wedge buttresses; NEXT return to29b source','lighthouse':'19h native','harbor':'22g','village_and_headland':'26b','production':'17e/18c/19h unchanged'},evidence=['reviews/round-29-worklog.md','reviews/round-29c-root-evidence.json','reviews/round-29c-island-independent-review.md','reviews/round-29c-independent-geometry.json'],remaining=['Remove failed29c long wedges from next candidate by starting saved29b; split actual terrain/core outside protection boundaries and author short offset rock shoulders','Upper grey wall, broad skirts and tidal bands still artificial; exact reference composition and all-weather lighting incomplete','Warm light/water, clouds, mainland/village and all20 references plus opening continue'])
registry['final_lantern_configuration']=read(run/'images/night-reference.png.json')['lantern_lighting']
(R/'reviews/reference-view-1342-progress-29c.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
note=f'**最新29c C/D岛岩完成五实际GPU及独立审查，造型仍打回。** 29a外围尖柱失败；29b改形121地表点、降低主肩、减少压扁礁体，保护证据保留，但上台灰盾/水线带仍不符；29c四斜肩形成长楔斜撑，不作为下一稿底稿。**下一步回到保存29b源，沿真实道路/基础/树根边界切分主岩与地表，重塑错位短肩/宽台/低根，不再叠加长楔。** 最新{len(m["artifacts"])}冻结绑定SHA匹配，61实际落点最大差0.244mm、9×9基础抽样最大差0.610mm，不能称逐点零差或完整通行验收。所有29a/b/c原生及GPU进程已结束，无待等句柄，不重启旧失败版本。接续 `reviews/round-29-worklog.md`、`reviews/round-29c-island-independent-review.md`、`reviews/reference-view-1342-progress-29c.json`。生产17e/18c/19h未改；完整20参考及原图Goal active。'
correction='独立陡面定位补充：按实际29b中心高于10m、normal.z<0.5选出81面，只有13面属于515整面冻结，另68面未冻结；保留道路1.2m缓冲仍有184.24m²投影区域可改。灰盾不能主要归咎于保护限制，下一稿优先改外围高度场过陡衔接和面组织，少数擦边面才需精确切分。定位 `reviews/round-29c-independent-wall-localization.json`，不把该阈值选区当作全部可见灰墙像素。'
note+='\n\n'+correction
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
 p=R/name;s=p.read_text(encoding='utf-8');assert '**最新29c C/D岛岩' not in s;first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');assert '29c岛岩接续' not in s;p.write_text(s+'\n\n29c岛岩接续：29b真实外围地表重塑/低肩及保护证据保留，但整图未接受；29c新增四长楔造型失败。下一稿回到29b源，沿准确保护边界切分主岩/地表，制作非共线短肩、错位宽台与低根，不能再加长斜撑遮住旧墙。五GPU与独立证据 `reviews/round-29-worklog.md`、`reviews/reference-view-1342-progress-29c.json`。候选未装生产，完整20参考Goal active。\n',encoding='utf-8')
p=R/'reviews/round-29-worklog.md';s=p.read_text(encoding='utf-8');s=s.replace('## 29c：正在验证斜向承重岩肩','## 29c：长楔造型失败，改用主体拓扑返工')
s=s.replace('该结论等待独立复算，零投影交集的肩不称有实测净空。','独立实际GLB复算：西南肩交集12.4624m²、最小净距28.0647cm；东肩交集19.8177m²、最小约12cm。东南与北肩无保护投影交集，净距为null。')
s=s.replace('新GPU运行 `lantern-island-29c-20260908T170924Z-4d7e5928e9e74d1ca0621a44e963b02d`，root会话68709已启动，须按实际句柄查询，不因观察超时重启。造型尚未接受；完成后更新本节。所有29a/b原生、GPU及29c原生建模/重开进程已终止。',f'五GPU运行 `lantern-island-29c-20260908T170924Z-4d7e5928e9e74d1ca0621a44e963b02d` 已terminal passed，root68709终止；根/独立直接看完五图，{len(m["artifacts"])}绑定SHA核对。61落点最大差0.244mm，9×9基础抽样差0.610mm，并非零差。长楔像斜撑板，上台与水线仍规则，造型打回。所有29a/b/c原生及GPU结束，不重启。')
s+='\n\n## 下一稿执行入口\n\n从 `captures/lantern_island_study_29b/island_c.blend` 接续，不带29c四楔。29b的515整三角冻结是实现选择，不是用户要求；沿真实保护多边形剪开擦边的大面，保留保护内原线性支承面，释放外部改形。主岩/地表要同步真实拓扑：短上肩—中段错位宽台—偏向低根，不共线、不全高贯通长脊；实际改变旧灰墙和水线折带。继续检查保存源、实际GLB保护区域高度/接缝、受影响碰撞与同版昼夜/侧背图；无改动部分不重跑整套验证。29c仅失败证据与垂直净空算法参考。\n'
p.write_text(s+'\n\n'+correction+'\n',encoding='utf-8')
print('29c checkpoint',len(m['artifacts']),'bindings, full Goal active')
