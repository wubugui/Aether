from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
runs={'33a':'rightcoast-33a-20260908T225810Z-0d4a29733a15418f8530539d615fdfa4','33b':'rightcoast-33b-20260908T230223Z-8cfad99a2e374240853a864447c92c75','33c':'rightcoast-33c-20260908T230636Z-171cc57e608641cfb0e39cbcb89fbcaf'}
required=['reviews/round-33-occupied-regions.json','reviews/round-33-occupied-regions.md','reviews/round-33-rightcoast-design-review.md','reviews/round-33d-rightcoast-design-brief.md','captures/rightcoast33b-visible-transition-localization.json','captures/rightcoast33-low-cove-localization.json']
for label in runs:
 required.extend('reviews/round-'+label+'-rightcoast-independent-'+kind+ext for kind in ['geometry','review'] for ext in ['.md','.json'])
 required.append('reviews/round-'+label+'-reopened-source.json')
assert all((R/p).exists() for p in required)
def write(p,d):
 assert not p.exists(),str(p);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
evidence=[]
for label,rid in runs.items():
 run=R/'captures/validation_runs'/rid;native=R/'captures'/('rightcoast_study_'+label);m=read(run/'manifest.json');gate=read(native/'native-check.json');site=read(run/'actual-coast-rebuild.json')
 assert m['status']=='passed' and all(s['status']=='passed' for s in m['stages'])
 for p,b in m['artifacts'].items():assert sha(run/p)==b['sha256'],(label,p)
 assert gate['passed'] and gate['source_sha256']==sha(native/'mainland_headland.blend') and gate['glb_sha256']==sha(native/'mainland_headland.glb')
 views=[]
 for name in ['night-reference','day-reference','day-coast-front','day-coast-bay','day-coast-back']:
  p=run/'images'/(name+'.png');side=Path(str(p)+'.json');d=read(side)
  assert d['run_id']==rid and d['rightcoast_glb_sha256']==gate['glb_sha256'] and not d['production_modified']
  assert d['world_sha256']=='6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8'
  views.append(dict(name=name,image=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(side),camera=d['camera'],root_directly_viewed=True))
 assert all(v['actual_trees']==28 and v['paver_samples']==8839 and v['paving_passed'] and v['islands_unchanged'] for v in site['views'])
 evidence.append(dict(label=label,run_id=rid,run_status='passed',all_bound_sha_match=True,binding_count=len(m['artifacts']),native_source_sha256=gate['source_sha256'],glb_sha256=gate['glb_sha256'],views=views,actual_runtime=site['views'][0],root_processes_terminal=True,visual_accepted=False))
write(R/'reviews/round-33-root-evidence.json',dict(round='33a/b/c',runs=evidence,references={p:sha(R/p) for p in required},goal_status='active',production_modified=False,preferred_unfinished_candidate='captures/rightcoast_study_33b/mainland_headland.blend',rejected_latest_experiment='captures/rightcoast_study_33c/mainland_headland.blend',next_action='reviews/round-33d-rightcoast-design-brief.md',all_reference_goal_complete=False))
write(R/'reviews/round-33-root-visual-findings.json',dict(status='rework_required',keep=['33b lower and setback ridges reduce33a dominating near rock slope.','Real inter-headland water opening and nine houses/streets readable.'],reject=['33a large near slopes and visible narrow ground transitions.','33b retained26b long triangles, broad straight shore cliffs and repeated protruding rocks remain.','33c new tall narrow dark cut face; low shore appears only as a narrow lip and main-view gain is limited.'],causality_limit='Three selected33b transition triangles retain all26b vertex positions; one nearby triangle has only6.7mm single-vertex displacement. Not all visible wedges were introduced by33.',preferred_candidate='33b',full_reference_accepted=False))
write(R/'reviews/reference-view-1342-progress-33.json',dict(reference='ref/1342.png',reference_sha256=sha(R/'ref/1342.png'),status='in_progress_not_accepted',preferred_run=runs['33b'],latest_failed_visual_experiment=runs['33c'],root_evidence='reviews/round-33-root-evidence.json',next_design='reviews/round-33d-rightcoast-design-brief.md'))
note='''**最新33右岸已完成三版原生、各五GPU与独立审查；以33b未完成底稿接续，33c不升级。** 33a提高岸肩/后山但近坡过大；九pad旋转方向错误已记录，实际完整屋路支承碰巧由更大冻结面保持。33b改用独立九真实基础+922实际铺地投影，降低后退山脊；完整实际支承与外部侵入检查通过，显式冻结域仍有约0.221683m²漏片但其真实面保持。33c从33b仅降17点试低工作岸，结构范围内支承保持，实图新增高窄切面/低岸唇，视觉拒绝。三run都passed；各8839铺地样本、81屋基探针和28命名树记录核对，岛屿落点保持；不是艺术接受。部分屋旁尖面已确认来自保留26b源，不能继续只改新山脊。接续 `reviews/round-33d-rightcoast-design-brief.md`，在真实占用外缘重排低岸—坡脚局部网格。当前右岸源 `captures/rightcoast_study_33b/mainland_headland.blend`；完整同世界装配在33b run，A32f/B20l/C-D31i保持。全部33建模/GPU和独立进程结束，不重启旧版。证据 `reviews/round-33-root-evidence.json`、`reviews/round-33-worklog.md`。尚无33d，生产17e/18c/19h未改，完整20参考及原开场Goal active。以下旧阶段是历史。'''
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md','REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');head,tail=s.split('\n',1);assert note not in s;p.write_text(head+'\n\n'+note+'\n'+tail,encoding='utf-8')
log='''# 33 右岸三版制作记录

本轮实际推进原生建模、同世界装配、十五张GPU原图、独立几何/美术复核。全部参考目标没有完成；33b保留为未完成接续，33c是保存的失败实验。

从26b已修地原生开始，没有回退23g、覆盖生产或整体生成世界。独立首先提取九屋完整实际基础（含门阶梯）及922铺地真实GLB域，合并约899.210279m²，五视图实际28棵命名松树。九屋原设计pad均包含实际基础，但33a准备脚本自己旋转pad方向错误，不能混淆这两个结论。

33a实际改变939点，主壳909点最大35.541m，12件原生闭合正体积。实际三角与保存源同版；真实屋路完整支承面保持，没有外部面移入，但计划occupied域未覆盖九屋真实足域，整体设计约束失败保留。实图显示大近坡压屋、旧/新地坪尖折，视觉返工。

33b直接使用独立实际GeoJSON，冻结水上向上相交面，增加8m不变坡脚及30m过渡，降低后退山脊；1115点变动，主壳1082点最大23.212m。完整旧支承和外面新侵入检查通过。显式冻结面域约0.221683m²铺地漏片实际仍完全保持，报告单列这一描述限制。源12件、GLB16534三角完全匹配，没有XY反向；不是全局三维自交或全部步行证明。

33c从33b保存源继续，17点只降Z、XY拓扑保持，想在湾底形成1.6m岩岸。实际源/GLB和受影响面支承检查由独立报告给出；设计矩形238m²并非全由陆体覆盖，也不是全平面。实图新增高窄切面，低岸只读到窄唇，故不升级。需要局部面组织与坡脚断面联动，不再只压低少量点。

三版真实GPU总run及night/day引擎均passed，root和独立视觉审查均直接看各五张原图。每版81基础探针相对32f最大差分别约0.000732/0.000336/0.000336m；8839铺地碰撞样本通过、28命名树存在并重贴、岛屿落点全保持。树最大抬高33a35.44m、33b/c18.52m，存在不代表艺术布置接受。程序化散布已按实际最高terrain重贴，可见树及旧散布日志不是全世界植被普查。

运行保留26b修地报告和铺地原设计，另加真实revision身份链绑定新网格；33c是26b→33b→33c，未伪造旧报告为新资产。不再沿用旧preview中“cloud/water-only无需检查道路”的报告，本轮确实调用了village_adapter.validate。

实际源射线进一步发现：三处33b屋前/主图尖面三点均与26b相同，一处仅6.7mm变化，表明这些尖面不是全由33山脊生成。第五射线可能命中被遮挡后的坡，已限制归属。下一稿详见round-33d-rightcoast-design-brief.md，局部重排真实低岸、坡脚和完整支承边界，并联动受影响散布；不回A/C-D隐藏面无限修整。

证据入口round-33-root-evidence.json、round-33-root-visual-findings.json、reference-view-1342-progress-33.json、三版独立MD/JSON和各保存源重开JSON。全部本轮进程已结束，审查最终落盘后核对冻结SHA；未完成所有场景的生产安装或Windows发布。
'''
p=R/'reviews/round-33-worklog.md';assert not p.exists();p.write_text(log,encoding='utf-8')
print(json.dumps(dict(runs=[{'label':e['label'],'bindings':e['binding_count'],'status':e['run_status']} for e in evidence],preferred='33b',goal='active'),indent=2))
