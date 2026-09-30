from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=R/'captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2'
native=R/'captures/foreground_island_study_32f'
required=['reviews/round-32f-foreground-independent-review.md','reviews/round-32f-foreground-independent-review.json','reviews/round-32f-foreground-independent-geometry.md','reviews/round-32f-foreground-independent-geometry.json','reviews/round-32f-reopened-source.json','reviews/round-32f-incremental.json','reviews/round-32e-actual-tree-bases.json','reviews/round-32e-pad-transition-local.json','reviews/round-33-rightcoast-intake.md','reviews/round-33-rightcoast-intake.json','captures/rightcoast33-main-view-localization.json']
assert all((R/p).exists() for p in required)
m=read(run/'manifest.json');site=read(run/'actual-site-rebuild.json');gate=read(native/'native-check.json');ind=read(R/'reviews/round-32f-foreground-independent-geometry.json')
assert m['status']=='passed' and all(s['status']=='passed' for s in m['stages'])
for p,b in m['artifacts'].items():assert sha(run/p)==b['sha256'],p
assert ind['pass'] and ind['all8_actual_tree_bases_supported'] and ind['all8_actual_tree_bases_flat']
assert gate['passed'] and sha(native/'island_a.blend')==gate['source_sha256'] and sha(native/'island_a.glb')==gate['glb_sha256']
views=[]
for name in ['night-reference','day-reference','day-a-front','day-a-back','day-a-approach']:
 p=run/'images'/(name+'.png');s=Path(str(p)+'.json');d=read(s)
 assert d['run_id']==run.name and d['island_a_glb_sha256']==gate['glb_sha256']
 assert d['world_sha256']=='6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8'
 views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(s),root_directly_viewed=True,camera=d['camera']))
assert all(v['unaffected_placement_count']==46 and v['unaffected_position_delta_m']<.001 for v in site['views'])
assert all(len(v['tree_placement_check']['actual'])==8 and len(v['tree_placement_check']['expected'])==8 for v in site['views'])
def write(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
findings=dict(status='stage_candidate_retained_not_final_art_accepted',keep=['Compact upper grass shoulder exposes thick foreground cliff.','Both keeper houses fully readable; left gable and porch turned toward main view, right house lowered1.5m.','All8trees present; tallest left pine reduced to retain tower emphasis.','Three complete actual building foot domains and8actual pine base support validated.'],remaining=['Broad planar rock walls and button-like outcrops are not final art accepted.','Local narrow steep faces880/884 remain89.149/85.223degrees despite fixing the height-function discontinuity; no claim all visible gullies removed.','C/D art, right coast depth, water/reflections/weather and other reference regions remain incomplete.'],next_action='33 right coast unequal headlands/low coves/setback ridges, then water and warm light; see round-33-rightcoast-intake.md.',production_modified=False,full_reference_accepted=False,all_reference_goal_complete=False)
write(R/'reviews/round-32f-root-visual-findings.json',findings)
e=dict(run_id=run.name,manifest_sha256=sha(run/'manifest.json'),terminal_status=m['status'],engine_stages_passed=True,binding_count=len(m['artifacts']),all_bound_hashes_match=True,source_sha256=gate['source_sha256'],glb_sha256=gate['glb_sha256'],root_views=views,independent_geometry_pass=True,visual_accepted=False,production_modified=False,goal_status='active',all_reference_scope_retained=True,unaffected_placement_count=46,unaffected_position_delta_m=max(v['unaffected_position_delta_m'] for v in site['views']),planned_trees=8,actual_trees=8,root_and_independent_processes_terminal=True,references={p:sha(R/p) for p in required},next_action=findings['next_action'])
write(R/'reviews/round-32f-root-evidence.json',e)
write(R/'reviews/reference-view-1342-progress-32f.json',dict(reference='ref/1342.png',reference_sha256=sha(R/'ref/1342.png'),status='in_progress_not_accepted',camera=views[0]['camera'],run_id=run.name,run_terminal_status='passed',reference_image=views[0],root_evidence='reviews/round-32f-root-evidence.json',next_action=findings['next_action']))
note='''**最新32f前景A保留为阶段候选，下一步33右岸。** 32c跨界约束失败未导出；32d重建紧凑草肩、错位厚崖与树肩，完整塔阶极小区域未平；32e扩大塔坪、左屋转向、右屋降低1.5m和左树降低，三建筑完整底面及八棵真实树干底支承通过；32f修复屋坪混合的高度跳变。32d/e/f各五张真实GPU原图均已直接审查，32f运行passed，全部绑定SHA核对，46非A落点差0、8/8树存在。32f实际尖瘦面880/884仍为89.149°/85.223°，不能称沟坡全修；宽岩墙/按钮凸块仍未美术接受。当前原生 `captures/foreground_island_study_32f/island_a.blend`，完整冻结装配和最终审查见 `reviews/round-32f-worklog.md`、`reviews/round-32f-root-evidence.json`。下一步依据 `reviews/round-33-rightcoast-intake.md` 与 `captures/rightcoast33-main-view-localization.json` 制作不等宽岩岬、低湾和后山，再处理水面；右岸以26b保存源和真实9屋/922铺地为准，不回23g。全部32阶段及只读33进程结束，无待等句柄，不重跑旧生成/验证。生产17e/18c/19h保持，全部20参考及原开场Goal active。以下旧阶段记录为历史，不能覆盖本段最新状态。'''
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md','REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');head,tail=s.split('\n',1)
 assert note not in s
 p.write_text(head+'\n\n'+note+'\n'+tail,encoding='utf-8')
log='''# 32c–f 前景A制作与接续

32f保留为构图阶段候选，完整参考尚未接受。实际源11独立件，保留编辑材料和实体路面，不修改生产或整体生成世界。

32c重建草肩时CDT外部三角断言失败，未保存blend/glb，不跑GPU。32d过滤实际草肩外三角后保存厚岩/草肩/短路/8树；GPU五视图完成，但独立完整塔阶底域检查发现0.014411437m²区域误差大于1mm、最大0.059634m，保留失败报告。不能把9点基础通过代替完整底域。

32e扩大塔pad为半宽5.4/5.1，左屋yaw转PI/2、右屋降至27m、最高左树scale降至1.2；三建筑完整真实底域和八棵真实六边形干底完整支承通过。五实图保留紧凑草肩/厚崖、两屋入画及树群关系，但背视屋间沟坡还有尖折。独立定位证明旧塔pad边缘外0.1mm发生0.765553m高度跳变。

32f只修改外部重叠pad权重，修正上述数值跳变至约1.37e-9m；274地表点、137主岩点及126贴地路径点随高程改变。八独立岩件保持；八干底与所有网格投影相交的实际三角几何集合逐一保持，因此继承32e完整最高表面支承，不重复完整扫描。三建筑完整域和cap/core同版源/GLB独立复核通过。实际源面880/884仍89.149°/85.223°，因此不宣称可见尖沟全消失、严格C1连续或全岛几何验收。

32d/e/f五原图均由root和独立视觉代理直接查看。32f run为 foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2，night/day引擎和总run均passed，46非A落点差0，8计划树全部存在。冻结输入、PNG和sidecar绑定由root证据记录；全部建模/源重开/实际GPU进程均已终止。独立最终报告写完后才冻结审查SHA。

右岸33接续已只读打开当前26b原生：12件，主壳8192点/16380三角，九屋、两组922铺地，28原树。完整原生坐标与八主视图射线已保存，七条命中具体岸面、一条无岸体命中。射线仅含该岸体，不包含所有世界遮挡，不由点命中推断整面可编辑。下一步在真实占用约束下制作不等岩岬、低湾、后山层次；不得伪造铺地历史来源绑定。尚无33新模型。

证据入口：round-32f-root-evidence.json、round-32f-root-visual-findings.json、round-32f-foreground-independent-geometry.md/json、round-32f-incremental.json、round-32f-foreground-independent-review.md/json、reference-view-1342-progress-32f.json、round-33-rightcoast-intake.md/json。早期32c/d失败、32e过渡诊断保留。总Goal继续active：同一连续真实3D世界、全部20参考及开场、Blender精细建模、仅场景跳过角色。
'''
p=R/'reviews/round-32f-worklog.md';assert not p.exists();p.write_text(log,encoding='utf-8')
print(json.dumps(dict(bindings=len(m['artifacts']),views=len(views),run_status=m['status'],goal='active'),indent=2))
