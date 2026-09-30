from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(r'E:\FeiTing');run=R/'captures/validation_runs/coast-environment-27c-20260908T151320Z-766da6d8e2214d7f9879e2c4b050ad09'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
views=['night-reference','night-reverse','day-reference','night-reference-later'];sides={v:read(run/'images'/f'{v}.png.json') for v in views}
assets=[]
for name in ['cloud_bank_0','cloud_bank_1','cloud_bank_2','moon']:
 for ext in ['blend','glb']:
  p=R/'captures/coastal_sky_assets_27c'/f'{name}.{ext}';f=run/'study-inputs/new-environment27c/sky-assets'/p.name
  row={'name':p.name,'sha256':sha(p),'matches_frozen':sha(p)==sha(f)}
  if name=='moon':row['matches_21b_bytes']=p.read_bytes()==(R/'captures/coastal_sky_assets_21b'/p.name).read_bytes()
  assets.append(row)
layout=read(run/'study-inputs/new-environment27c/cloud-layout-27c.json');clouds=[a for a in sides['night-reference']['environment_study']['native_sky_assets'] if a['asset']!='moon']
layout_errors=[]
for d,a in zip(layout['records'],clouds):
 layout_errors.append({'asset':a['asset'],'asset_match':d['asset']==a['asset'],'position_max_error_m':float(np.max(np.abs(np.array(d['position'])-a['position']))),'scale_max_error':float(np.max(np.abs(np.array([d['uniform_scale'],d['uniform_scale']*d['vertical_aspect'],d['uniform_scale']])-a['scale'])))})
a=np.array(Image.open(run/'images/night-reference.png').convert('RGB')).astype(float);b=np.array(Image.open(run/'images/night-reference-later.png').convert('RGB')).astype(float)
temporal=[]
for name,box in [('near_water',[1060,755,1190,840]),('static_tower_wall',[301,620,324,710]),('central_cloud',[639,158,969,288]),('moon',[1090,130,1165,202])]:
 x0,y0,x1,y1=box;diff=np.abs(a[y0:y1,x0:x1]-b[y0:y1,x0:x1]);temporal.append({'roi':name,'box_xyxy':box,'mean_absolute_rgb_change_8bit':float(diff.mean()),'fraction_pixels_max_channel_change_gt_2':float((diff.max(axis=2)>2).mean())})
obs={'night-reference':'相对27b，近景冰面大块明显减少，水光更细碎；但亮带仍由密集细横纹组成，近处偏白，片宽/节奏变化不足。云布局填充更接近参考的大致层次，但中央和右侧主云形成尖金字塔山峰及平硬薄底，比27b更明显读作悬浮山脊，打回云形。',
'night-reverse':'原岸岛的遮挡关系保持，月光亮带不再固定在屏幕。反向水面已有轻微波纹和天空反射，比27b空平面改善，但读感很弱。该机位主要看到原World圆团云，不足以直接验收新云的反面细节。',
'day-reference':'白天海面已出现清楚的细波纹及远距天空反射，消除了27b几乎纯平蓝的显著问题。尖云在白天更像冰山/金字塔群，长薄底和统一斜面不合1342的丰富块状云体。',
'night-reference-later':'同相机18秒图中近处亮片位置/分布明显变化，中央云轻微横移；岸岛/月球位置维持。实际输出不是静止水光，但两个时刻不足以证明中间动画平顺、无跳变或足够自然。'}
manifest=read(run/'manifest.json');gate=read(R/'reviews/round-27c-sky-native-check.json')
report={'round':'27c','reviewer':'independent village_floor_review','verdict':'reject_cloud_candidate_retain_limited_water_improvement','scope':'Direct four GPU stills including t0/t18 and original ref1342; frozen identities/world layout/shader mechanism. No unchanged26b geometry re-audit, no production mutation.',
'gpu_status':manifest['status'],'gpu_stages':[{k:x.get(k) for k in ['name','status','exit_code']} for x in manifest['stages']], 'native_gate_passed':gate['passed'],'asset_identity':assets,
'same_world_hash':len({s['world_sha256'] for s in sides.values()})==1,'same_cloud_placements':all([x for x in s['environment_study']['native_sky_assets'] if x['asset']!='moon']==clouds for s in sides.values()),
'layout_identity':{'frozen_matches_source':sha(run/'study-inputs/new-environment27c/cloud-layout-27c.json')==sha(R/'captures/coast_environment_study_27c/cloud-layout-27c.json'),'design_count':len(layout['records']),'runtime_count':len(clouds),'source_scope':layout['scope'],'runtime_errors':layout_errors},
'shader_identity':[{'name':n+'.gdshader','sha256':sha(R/'captures/coast_environment_study_27c'/(n+'.gdshader')),'matches_frozen':sha(R/'captures/coast_environment_study_27c'/(n+'.gdshader'))==sha(run/'study-inputs/new-environment27c'/(n+'.gdshader'))} for n in ['cloud_surface','open_water']],
'images':{v:{'path':str(run/'images'/f'{v}.png'),'sha256':sha(run/'images'/f'{v}.png'),'camera':sides[v]['camera'],'sampled_world_time':sides[v]['environment_study']['sampled_world_time'],'observation':obs[v]} for v in views},
'temporal_comparison':{'same_camera':sides['night-reference']['camera']==sides['night-reference-later']['camera'],'roi_pixel_statistics':temporal,'scope':'Statistics are pixel measurements only, not aesthetic or motion-smoothness scores.'},
'water_mechanism':'3.2x1.15m jittered Voronoi normal sampling,28percent continuous slope mixture, world-space wave field, view-dependent moon reflection and a sky-color gradient.72percent facet slope remains discontinuous at site boundaries. No displaced wave mesh, no reflection of actual cloud geometry.',
'limits':['Authored layout uses fixed reference-camera composition but runtime7clouds remain world objects; no camera-following placement in adapter.','Reverse camera confirms world layout/render relationships but predominantly shows oldWorld cloud forms; new cloud backside not fully inspected.','Cloud surface lighting/haze is not volumetric density scattering.','Two time samples demonstrate actual change only, not temporal smoothness or unrestricted flight acceptance.','Base ripple and foam retain sinusoidal terms; periodicity is not mathematically eliminated.'],
'overall_accepted':False,'production_modified_by_reviewer':False,'remaining':['Sharp mountain-like cloud peaks and thin hard bases are a visual regression.','Water needs broader variation in glint scale/rhythm; thin dense bands persist.','Lighthouse beams and overall coast/reference fidelity remain unaccepted.']}
(R/'reviews/round-27c-cloud-water-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='''# 27c 云与水面独立限定审查

结论：**云形打回，水面保留局部改善；整图未接受，未装生产。** 新云的主要问题是过尖的金字塔山峰与平硬薄底，像悬浮山脊。水面减轻了27b近景巨型冰面拼片，并让白天和反向海面重新可读，但主月光带仍密集、细横纹偏多。

已直接查看实际 night-reference、night-reverse、day-reference、night-reference-later 四图，与原 `ref/1342.png` 对照。run 终态 passed，四个 exit code 为0；新云源重开 gate 通过。这些技术通过不代替视觉接受。

| 图 | 直接观察 |
| --- | --- |
'''
for v in views:md+=f'| {v} | {obs[v]} |\n'
md+='''
## 实际身份与时间

3套新云 BLEND/GLB 与冻结输入相同，月球与21b逐字节相同；shader与布局冻结输入也相同。四图 World SHA相同、7云固定位置与尺度一致，运行布局与设计只存在浮点舍入差。布局的作者采用1342参考相机设计构图，这是创作选择，不是原图地理还原证据；运行时世界坐标固定，不随相机重排。反向图主要看见原World旧云，不把它误称新云反面已经完整接受。

0秒/18秒 sidecar记录一致相机、各自时间，实际图像水光与云边发生变化。下表仅为指定图像区域的像素差，不能当作美术分数或连续运动质量证明。

| 区域 | 平均RGB绝对变化（0–255） | 最大通道差>2的像素比例 |
| --- | ---: | ---: |
'''
for q in temporal:md+=f"| {q['roi']} | {q['mean_absolute_rgb_change_8bit']:.4f} | {q['fraction_pixels_max_channel_change_gt_2']:.3%} |\n"
md+='''
## 机制与限定

水面3.2×1.15m世界空间Voronoi采样中混入28%连续坡度，能减轻大拼片，却仍有72%面区坡度在边界不连续。新增的是天空颜色渐变反射，不是对实际云/岸的完整反射；水面无真实顶点波浪，云也仍是表面照明/雾色近似。两张时间静图不能证明中间动画平顺或无跳变。

本轮没有重复未改26b道路、屋基和岸体检查，没有修改生成器或生产。灯塔光束未做，整体仍远未达到1342。下一步优先把尖山形主云改回有厚度、丰富而不规则的块状云团；保留本轮水面改善，继续调整亮片宽度、明暗和疏密层次。
'''
(R/'reviews/round-27c-cloud-water-independent-review.md').write_text(md,encoding='utf-8')
print(json.dumps({'status':manifest['status'],'native':gate['passed'],'world_same':report['same_world_hash'],'cloud_same':report['same_cloud_placements'],'max_layout_position_error':max(x['position_max_error_m'] for x in layout_errors),'temporal':temporal},indent=2))
