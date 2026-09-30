from pathlib import Path
import json,hashlib
R=Path(r'E:\FeiTing')
run=R/'captures/validation_runs/coast-environment-27a-20260908T145044Z-a01744c1b93444ce9c8d80e533918f2d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
views=['night-reference','night-reverse','day-reference']
sides={v:read(run/'images'/f'{v}.png.json') for v in views}
assets=[]
for name in ['cloud_bank_0','cloud_bank_1','cloud_bank_2','moon']:
 for ext in ['blend','glb']:
  source=R/'captures/coastal_sky_assets_27a'/f'{name}.{ext}'
  frozen=run/'study-inputs/new-environment27a/sky-assets'/source.name
  row={'name':source.name,'sha256':sha(source),'frozen_matches':sha(source)==sha(frozen)}
  if name=='moon':row['matches_21b_bytes']=source.read_bytes()==(R/'captures/coastal_sky_assets_21b'/source.name).read_bytes()
  assets.append(row)
shaders=[]
for name in ['cloud_surface','open_water']:
 p=R/'captures/coast_environment_study_27a'/f'{name}.gdshader'
 shaders.append({'name':p.name,'sha256':sha(p),'frozen_matches':sha(p)==sha(run/'study-inputs/new-environment27a'/p.name)})
observations={
'night-reference':'相对26b蓝色受光增强；云仍有山石般硬顶和薄平板底。旧粗菱格减弱，但月光反射变成密集、较连续的横向细亮纹，近处有扫描线感。未达到1342中较粗、破碎、宽度变化明显的亮片。',
'night-reverse':'岸岛遮挡和视角变化正确；离开朝月观察方向后亮反射带消失，符合世界空间反射关系。水面此时近乎平滑暗蓝。左上近云底部厚硬折面、重复圆团及右上分离圆球影响自然层次；不将所有这些形状归因于新增7个云实例，原World云仍参与材质替换。',
'day-reference':'云体较亮，但白色山丘式硬块和灰蓝平底仍明显，形体变化不足；海面除近岸青色带外几乎无可读波形。'}
report={'round':'27a','reviewer':'independent village_floor_review','verdict':'reject_cloud_water_art_candidate_keep_limited_findings','scope':'Actual three GPU stills against ref/1342.png and26b night; frozen asset identity and shader mechanism. No repeated road/foundation/terrain collision audit. No production modification.',
'gpu_manifest':{'path':str(run/'manifest.json'),'status':read(run/'manifest.json')['status'],'stages':[{k:s.get(k) for k in ['name','status','exit_code']} for s in read(run/'manifest.json')['stages']]},
'native_gate_passed':read(R/'reviews/round-27a-sky-native-check.json')['passed'],'asset_identity':assets,'shader_identity':shaders,
'same_world_hash':len({s['world_sha256'] for s in sides.values()})==1,
'same_cloud_world_placements':all([a for a in s['environment_study']['native_sky_assets'] if a['asset']!='moon']==[a for a in sides['night-reference']['environment_study']['native_sky_assets'] if a['asset']!='moon'] for s in sides.values()),
'images':{v:{'path':str(run/'images'/f'{v}.png'),'sha256':sha(run/'images'/f'{v}.png'),'camera':sides[v]['camera'],'world_sha256':sides[v]['world_sha256'],'observations':observations[v]} for v in views},
'mechanism_limits':['Cloud shader is unshaded surface normal lighting plus distance haze, not volumetric density scattering.','Water uses world-coordinate noise, finite-difference surface normals and camera-dependent reflection; screenshot depth is used for shore depth, not an image backdrop.','27a still contains sinusoidal height/base-color terms; visual periodicity is not eliminated merely by adding noise.','Three stills support view-dependent world relationships but do not establish motion quality or unrestricted flight behavior.'],
'overall_accepted':False,'remaining':['Cloud underside/shape still resembles stone slabs.','Water replaces coarse grid with thin-band repetition; away from highlight water is too flat.','Lighthouse beams are absent and full scene reference fidelity remains unaccepted.']}
(R/'reviews/round-27a-cloud-water-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='''# 27a 云与水面独立限定审查

结论：**云、水面美术候选打回；保留蓝色受光增强与反光随视角变化的局部进展。整图未接受，未装生产。**

独立直接查看本轮 night-reference、night-reverse、day-reference 三张实际 GPU 图，并与原 `ref/1342.png`、26b 夜图比较。三 GPU 终态通过；这只证明运行完成，不代表视觉通过。实际源/冻结输入 SHA、三图路径和身份记录在同名 JSON。

| 视角 | 直接观察 |
| --- | --- |
'''
for v in views:md+=f'| {v} | {observations[v]} |\n'
md+='''
新云 3 套 BLEND/GLB 与 run 冻结输入相同；原生重开 gate 通过。月球 BLEND/GLB 与 21b 逐字节相同。三图 World SHA 相同，7 个新增云体位置与尺度相同；反向机位中的世界遮挡和反光方向变化成立。渲染天空也包含原 World 的云形，不将所有圆球形状擅自归因于新模型。

着色器实现是世界空间噪声法线、视线月光反射和表面云照明/远距雾色；云不是体积密度散射，水面也未以顶点位移构造真实波浪。27a 仍含正弦项，不能宣称周期性已消除。三张静图不足以证明运动和任意飞行路径效果。

本轮不重复已保留的 26b 道路、屋基、岸体碰撞审查。灯塔光束仍缺，岩岸、组团和整图风格仍有差距。建议下一次只围绕云的真实厚度/底部形体与水光断裂尺度推进，不把 native/GPU 绿灯当作参考美术验收。
'''
(R/'reviews/round-27a-cloud-water-independent-review.md').write_text(md,encoding='utf-8')
print(json.dumps({'world_same':report['same_world_hash'],'cloud_placements_same':report['same_cloud_world_placements'],'assets_all_match':all(a['frozen_matches'] for a in assets),'shaders_all_match':all(s['frozen_matches'] for s in shaders),'status':report['gpu_manifest']['status']},indent=2))
