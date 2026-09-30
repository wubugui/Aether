from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
runs={'34a':'water-34a-20260908T233808Z-05bd651c68574ef79ba9b59ab98506bb','34b':'water-34b-20260908T234145Z-bcb3451587f949d8b6faa363cf23622d'}
required=['reviews/round-33f-root-evidence.json','reviews/round-34c-water-design-brief.md']
for label in runs:
 required.extend('reviews/round-'+label+'-water-independent-review'+ext for ext in ['.md','.json'])
 required.extend('reviews/'+label+'-water-independent-technical'+ext for ext in ['.md','.json'])
assert all((R/p).exists() for p in required),[p for p in required if not (R/p).exists()]
entries=[]
for label,rid in runs.items():
 run=R/'captures/validation_runs'/rid;m=read(run/'manifest.json');plan=read(R/'captures'/('water_study_'+label)/'design-plan.json')
 assert m['status']=='passed' and all(s['status']=='passed' for s in m['stages'])
 for p,b in m['artifacts'].items():assert sha(run/p)==b['sha256'],(label,p)
 views=[]
 for name in ['night-reference','night-water-near','night-water-shift','night-time18','day-reference']:
  p=run/'images'/(name+'.png');side=Path(str(p)+'.json');d=read(side)
  assert d['run_id']==rid and d['water_shader_sha256']==plan['shader_sha256'] and not d['production_modified']
  assert d['rightcoast_glb_sha256']=='dcef43b72ef7732c54321d2c522c4d22292283a835fb6248a8f5d0142af38da6'
  assert d['world_sha256']=='6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8'
  assert d['environment_study']['sampled_world_time']==(18 if name=='night-time18' else 0)
  views.append(dict(name=name,path=str(p.relative_to(R)),sha256=sha(p),sidecar_sha256=sha(side),camera=d['camera'],sample_time=d['environment_study']['sampled_world_time'],root_directly_viewed=True))
 entries.append(dict(label=label,run_id=rid,run_status='passed',binding_count=len(m['artifacts']),all_bound_sha_match=True,shader_sha256=plan['shader_sha256'],views=views,visual_accepted=False,root_gpu_terminal=True))
def write(p,d):
 assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(R/'reviews/round-34-root-evidence.json',dict(runs=entries,bindings={p:sha(R/p) for p in required},goal='active',production_modified=False,all_reference_goal_complete=False,coast_candidate='33f',water_status='34a/b visual rework required',next_action='reviews/round-34c-water-design-brief.md'))
write(R/'reviews/reference-view-1342-progress-34.json',dict(reference='ref/1342.png',reference_sha256=sha(R/'ref/1342.png'),status='in_progress_not_accepted',coast='33f',latest_water_run=runs['34b'],water_accepted=False,root_evidence='reviews/round-34-root-evidence.json',next_action='reviews/round-34c-water-design-brief.md'))
note='''**最新34a/b海面已各完成五GPU与独立审查，均需视觉返工；海岸接续33f。** 34a较宽片面/反射过滤消减细梳纹但变近处大软斑、远光不足；34b增加坡度分布并反射有限月盘，软斑消失但成稀疏纯白碎片，缺少参考蓝白水光层。两run均passed，固定日夜/近水/侧移/18秒实际身份核验，土地/岛屿保持；继承33f屋路支承，未重复8839铺地检查。水仍平几何，材质共享高度场提供分片法线，不能称真实位移波面。34b月盘是固定方向/参考距离角度近似，下一稿需实际月心逐水点方向、粗糙反射与亮核心层次、实际港岸灯源倒影/遮挡。详见 `reviews/round-34c-water-design-brief.md`、`reviews/round-34-root-evidence.json`，尚无34c产物；34a/b准备与GPU已结束，不重启。当前原生海岸 `captures/rightcoast_study_33f/mainland_headland.blend`，保留12件可编辑源、A32f/B20l/C-D31i/27d云/28h灯。生产17e/18c/19h未改，全部20参考及原开场Goal active，其他区域、天气和内景仍未完成。以下历史不能覆盖最新状态。'''
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md','REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');head,tail=s.split('\n',1);assert note not in s;p.write_text(head+'\n\n'+note+'\n'+tail,encoding='utf-8')
p=R/'reviews/round-34-worklog.md';assert not p.exists();p.write_text('# 34 海面阶段记录\n\n'+note+'\n\n根与独立均直接检查十张原图。34a/b失败画面、源码、同版冻结输入及报告全部保留。有限反射模型与着色器变化有真实移动/时间证据，但没有因此接受艺术效果。34c设计说明详细记录返工方向及有限距离月球、当地灯光、实际场景反射和海面平几何的限制。\n',encoding='utf-8')
print(json.dumps(dict(runs=[dict(label=e['label'],bindings=e['binding_count']) for e in entries],goal='active',water='rework')))
