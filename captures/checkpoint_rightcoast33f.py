from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
runs={'33d':'rightcoast-33d-20260908T232040Z-ea61879316ae487487e34e2f5d2c313b','33e':'rightcoast-33e-20260908T232445Z-bbca56df959f4c63ae2e2de7566c1163','33f':'rightcoast-33f-20260908T233517Z-9aac3867c5f340208c238c9e2b83fc1e'}
required=['reviews/round-33-occupied-regions.json','reviews/round-33d-visible-transition-domain.json','reviews/round-33f-transition-component-intake.json']
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
 assert gate['source_sha256']==sha(native/'mainland_headland.blend') and gate['glb_sha256']==sha(native/'mainland_headland.glb')
 views=[]
 for name in ['night-reference','day-reference','day-coast-front','day-coast-bay','day-coast-back']:
  p=run/'images'/(name+'.png');side=Path(str(p)+'.json');d=read(side)
  assert d['run_id']==rid and d['rightcoast_glb_sha256']==gate['glb_sha256'] and not d['production_modified']
  assert d['world_sha256']=='6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8'
  views.append(dict(name=name,image=str(p.relative_to(R)),png_sha256=sha(p),sidecar_sha256=sha(side),camera=d['camera'],root_directly_viewed=True))
 assert all(v['actual_trees']==28 and v['paver_samples']==8839 and v['paving_passed'] and v['islands_unchanged'] for v in site['views'])
 evidence.append(dict(label=label,run_id=rid,run_status='passed',all_bound_sha_match=True,binding_count=len(m['artifacts']),native_source_sha256=gate['source_sha256'],glb_sha256=gate['glb_sha256'],views=views,actual_runtime=site['views'][0],independent_geometry_pass=(label!='33e'),visual_accepted=False))
write(R/'reviews/round-33f-root-evidence.json',dict(round='33d/e/f',runs=evidence,references={p:sha(R/p) for p in required},goal_status='active',production_modified=False,preferred_unfinished_candidate='captures/rightcoast_study_33f/mainland_headland.blend',rejected_experiment='33e whole four-group version: new diagonal XY fold and main-view fragmentation',next_action='34 water reflection and local warm lights',all_reference_goal_complete=False))
write(R/'reviews/reference-view-1342-progress-33f.json',dict(reference='ref/1342.png',reference_sha256=sha(R/'ref/1342.png'),status='in_progress_not_accepted',preferred_run=runs['33f'],root_evidence='reviews/round-33f-root-evidence.json',next_design='reviews/round-34-water-intake.md'))
note='''**最新33f海岸阶段候选已完成原生、五GPU和独立审查；下一步34海面与灯火。** 33d以真实占用外168面重拓扑宽湾，改善33c高窄切面，但仍是宽陡扇坡/窄岸唇。33e四组86点试改，前两屋前长灰片减轻，主图两组反而碎化，且beautify产生一处真实XY折回，整版拒绝。33f从33d精确XYZ映射，仅合并前两命中同连通组55点，排除主图31点，恢复旧对角线；实际12件/16804GLB三角同版，165改动面无新增XY叠片和真实占用侵入，屋路支承与33d湾底保持。三个run各五GPU均passed，每版81基础探针、8839铺地样本和28命名树核验，岛屿落点保持；程序通过不等于美术接受。当前源 `captures/rightcoast_study_33f/mainland_headland.blend`，同世界装配在33f run，A32f/B20l/C-D31i保持。证据 `reviews/round-33f-root-evidence.json`、`reviews/round-33f-worklog.md`。本阶段原生/GPU/独立均结束，不重跑旧版；34运行状态以最新run/句柄为准。生产17e/18c/19h未改，全部20参考及原开场Goal active。以下旧阶段为历史。'''
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md','REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');head,tail=s.split('\n',1);assert note not in s;p.write_text(head+'\n\n'+note+'\n'+tail,encoding='utf-8')
p=R/'reviews/round-33f-worklog.md';assert not p.exists();p.write_text('''# 33d/e/f 海岸阶段记录

33f保留为未完成的同世界接续，已进入34海面工作。全部参考未完成，生产未安装本阶段资产。

33d在真实屋路占用外重接宽湾坡脚，168旧面变438新三角，12个可编辑实体保留；实际宽坡缓解33c高窄暗片，仍缺清楚的低工作岸与自然断面。独立238m²设计框分析只证明局部较低范围，不代表整框1.6m平面。

33e从33b对四命中的86自由点调高程并换边，五实图确认两front处灰片缩短，但主图两处更碎。独立发现四点域换边产生0.000516m²真实XY折回与投影叠片；屋路支承通过不能掩盖此反例，本版不升级。

33f从33d实体只转入两front命中所在共享顶点连通组55点，按33b实际XYZ唯一映射，不依靠33d已重编号的旧索引。两主图独立组31点不采用。恢复四点域旧对角线后，新拓扑XY正向；独立确认实际GLB16804三角与12件源完全匹配，165新/旧改变面各投影494.955700m²、无新增投影重叠或实际屋路入侵。完整支承与湾底继承33d，并非重新全世界自交检查。

三版各五真实GPU原图已被根和独立视觉直接查看。33f宽湾与两front处改进保留，主图两处没有采用33e碎化增量；整体仍有大灰坡、窄岸唇、规则崖块和局部尖面，未获整体艺术接受。每版81屋基探针、8839铺地实际样本和28命名树核验，岛屿落点保持。33f保留26b历史报告，身份链真实为26b→33b→33d→33f；不伪造旧报告为新网格。

后续34优先修复固定主图密集横向水光、蓝色层次和实际当地暖灯倒影，并以主图/近水/移动观察验证。云、岩体、屋群及其他19参考天气场景仍在完整Goal范围内，不以本阶段进展替代它们。详见round-33f-root-evidence.json及三版独立报告。
''',encoding='utf-8')
print(json.dumps(dict(runs=[{'label':e['label'],'bindings':e['binding_count']} for e in evidence],preferred='33f',goal='active')))
