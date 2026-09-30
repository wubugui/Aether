from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];run=R/'captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95';native=R/'captures/foreground_island_study_32b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
required=['reviews/round-32b-foreground-independent-review.md','reviews/round-32b-foreground-independent-review.json','reviews/round-32b-foreground-independent-geometry.md','reviews/round-32b-foreground-independent-geometry.json','reviews/round-32b-reopened-source.json','captures/foreground32b-visible-grass-localization.json','reviews/round-32c-foreground-design-brief.md']
assert all((R/p).exists() for p in required)
m=read(run/'manifest.json');site=read(run/'actual-site-rebuild.json');gate=read(native/'native-check.json');ind=read(R/'reviews/round-32b-foreground-independent-geometry.json')
assert m['status']=='failed' and 'Authored A trees were filtered' in m['error']
assert len(m['stages'])==2 and all(s['status']=='passed' for s in m['stages'])
for p,b in m['artifacts'].items():assert sha(run/p)==b['sha256'],p
assert ind['pass'] and ind['all_actual_building_footprints_continuously_supported_and_flat']
assert gate['passed'] and sha(native/'island_a.blend')==gate['source_sha256'] and sha(native/'island_a.glb')==gate['glb_sha256']
views=[]
for name in ['night-reference','day-reference','day-a-front','day-a-back','day-a-approach']:
 p=run/'images'/(name+'.png');s=Path(str(p)+'.json');d=read(s)
 assert d['run_id']==run.name and d['island_a_glb_sha256']==gate['glb_sha256']
 assert d['world_sha256']=='6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8'
 views.append(dict(name=name,path=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(s),root_directly_viewed=True,camera=d['camera']))
assert all(v['unaffected_placement_count']==46 and v['unaffected_position_delta_m']<.001 for v in site['views'])
assert all(len(v['tree_placement_check']['actual'])==7 and len(v['tree_placement_check']['expected'])==8 for v in site['views'])
findings=dict(status='rework_required_not_accepted',keep=['Two real keeper houses are readable beside the tower at the fixed reference camera.','Rebuilt source11closed positive-volume meshes and three actual full building footprint terrain regions, actual cap/core support at these sites.'],rework=['Foreground grass still occludes the required thick front rock faces.','Old horizontally compressed outcrops read as tall sharp wedges; broad near-vertical walls remain.','Four left rear trees exist but sit15-18m below high house plateaus in view; one of8planned trees is actually filtered at a69.58degree slope.','New house sites stand on steep isolated grass mounds; paths and left tree shoulder need integrated terrain form.'],scope='Only foreground A32b candidate in full continuous world. All20 references plus original opening remain incomplete; production unchanged.',next_design='reviews/round-32c-foreground-design-brief.md')
write(R/'reviews/round-32b-root-visual-findings.json',findings)
e=dict(run_id=run.name,manifest_sha256=sha(run/'manifest.json'),terminal_status=m['status'],terminal_passed=False,engine_stages_passed=True,failure_reason=m['error'],binding_count=len(m['artifacts']),all_bound_hashes_match=True,source_sha256=gate['source_sha256'],glb_sha256=gate['glb_sha256'],root_views=views,independent_geometry_pass=True,visual_accepted=False,production_modified=False,goal_status='active',all_reference_scope_retained=True,unaffected_placement_count=46,unaffected_position_delta_m=max(v['unaffected_position_delta_m'] for v in site['views']),planned_trees=8,actual_trees=7,root_processes_terminal=True,references={p:sha(R/p) for p in required},next_action=findings['next_design'])
write(R/'reviews/round-32b-root-evidence.json',e)
night=read(run/'images/night-reference.png.json')
write(R/'reviews/reference-view-1342-progress-32b.json',dict(reference='ref/1342.png',reference_sha256=sha(R/'ref/1342.png'),status='in_progress_not_accepted',scope=findings['scope'],camera=night['camera'],world_sha256=night['world_sha256'],run_id=run.name,run_terminal_status='failed',engine_stages_passed=True,reference_image=views[0],root_evidence='reviews/round-32b-root-evidence.json',independent_review=required[0],next_design=findings['next_design']))
note='''**最新32b前景A已完成原生、五GPU和独立审查，整体返工。** 两屋在固定主机位恢复完整可读；11件保存源与实际GLB一致、完整三建筑底足迹及其cap/core支承通过限定检查。32a新屋过渡误改塔脚的失败保留，32b已修正。五图实际46个非A落点差0；8计划树只落7，run因此明确failed，night/day引擎阶段均passed且全部进程已结束。左后四树仍存在但低坡被高屋坪遮挡，仅(-30,-3)一棵因陡坡被过滤。主图草舌仍遮崖、旧岩尖薄、宽直墙及两屋绿锥台仍需真正改形。下一稿按 `reviews/round-32c-foreground-design-brief.md` 仅重构A紧凑草肩/厚岩崖/短路和树肩；保留两屋与塔的入画进展，不继续全岛水平压缩、不回C/D隐藏面反复。实际源 `captures/foreground_island_study_32b/island_a.blend`，七主图源射线 `captures/foreground32b-visible-grass-localization.json`，审查和绑定见 `reviews/round-32b-worklog.md`。尚无32c模型，不重跑32a/b已结束的生成或引擎。生产17e/18c/19h未改，完整20参考及原开场Goal保持active。'''
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md','REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');head,tail=s.split('\n',1);assert note not in s;p.write_text(head+'\n\n'+note+'\n'+tail,encoding='utf-8')
log='''# 32a/b 前景A制作记录

本轮是实际建模、装配、GPU取证和独立审查进展；全部场景目标仍未完成。

32a以20l真实A源进行局部正向分段形变，重建两屋地坪和3段全实体地面拟合路；生成后发现新屋过渡影响塔脚，最大约0.470m，保存失败blend和native-check，没有GLB或GPU。32b显式保护三处完整地坪，11个独立编辑件保存并导出实际GLB。没有整体世界重建，没有生产覆盖。

两屋Blender锚点(-23,3,28)/(-8,19,28.5)，scale1/.85、yaw0/-.15，塔锚点(-3,6,30.0621)/yaw.25。固定相机不变。这些是有记录的设计坐标，不是已知原图地图坐标。

独立已重新打开实际保存源且源SHA保持，11件闭合正体积，实际GLB与源三角完全一致。三设计pad完整三角裁剪及真实资产底面并集支承检查见几何报告；塔最低阶梯部分超出设计方pad但实际地面有覆盖且平坦，不能把保守凸包跨空白或方pad超界当失支承。未做全岛自交、全树干底接触、完整步行/飞行验收。

GPU运行 `foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95` 两引擎阶段exit0，五原图和sidecar齐全，root与fidelity_reviewer全部直接查看。46个非A落点保持，三个建筑各9点运行时基础间隙符合原生嵌入深度。8计划树只实例化7，因此run总状态failed原样保留。树(-30,-3,scale.65)源法线z=.348916，另四棵左后树实际存在但在较低后坡被屋坪遮挡；不得写成全部缺失。

两屋入画可保留；完整美术返工。32b草台仍挡住前景厚岩，三旧岩压缩后呈尖楔，近崖是宽直大墙。下一稿重做仅A的紧凑草肩和厚岩分层，并同步短路及可见树肩，不继续缩放整岛以追求简单通过。具体设计简报 `round-32c-foreground-design-brief.md`；其前缘控制点是未验证草案，必须先与实际占用和完整支承相核对。

主参考与32b源的七条实际射线、树根投影已经输出 `captures/foreground32b-visible-grass-localization.json`；该定位只命中岛体网格，未包含建筑和树遮挡体，已选实际可见裸露地面/岩点，不做全场景遮挡结论。

证据入口：`round-32b-root-evidence.json`、`round-32b-root-visual-findings.json`、`round-32b-foreground-independent-review.md/json`、`round-32b-foreground-independent-geometry.md/json`、`reference-view-1342-progress-32b.json`。所有本轮root建模和引擎句柄都已结束，32b源重开独立进程也已结束，不重启旧版本。尚未制作32c；完整20参考、同一世界、Blender精细建模和跳过角色范围未变。'''
p=R/'reviews/round-32b-worklog.md';assert not p.exists();p.write_text(log+'\n',encoding='utf-8')
print(json.dumps(dict(bindings=len(m['artifacts']),native=gate['source_sha256'],glb=gate['glb_sha256'],run_status=m['status'],views=len(views),goal='active'),indent=2))
