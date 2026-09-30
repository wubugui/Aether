from pathlib import Path
import json,hashlib
R=Path(r'E:\FeiTing');run=R/'captures/validation_runs/coast-environment-27b-20260908T145749Z-86704eae999c425590f3ff5cadced574'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
views=['night-reference','night-reverse','day-reference'];sides={v:read(run/'images'/f'{v}.png.json') for v in views}
assets=[]
for name in ['cloud_bank_0','cloud_bank_1','cloud_bank_2','moon']:
 for ext in ['blend','glb']:
  p=R/'captures/coastal_sky_assets_27b'/f'{name}.{ext}';f=run/'study-inputs/new-environment27b/sky-assets'/p.name
  row={'name':p.name,'sha256':sha(p),'matches_frozen':sha(p)==sha(f),'differs_27a':sha(p)!=sha(R/'captures/coastal_sky_assets_27a'/p.name)}
  if name=='moon':row['matches_21b_bytes']=p.read_bytes()==(R/'captures/coastal_sky_assets_21b'/p.name).read_bytes()
  assets.append(row)
obs={'night-reference':'云确已更新并被消费，但主视野两云仍是长薄碟托山丘，浅圆底未解决最终薄厚比例和过于简单轮廓。水光比27a粗而断裂，但近处巨大平亮多边形有冰面/拼片感，远处仍横向密集排列，未达到1342不规则且有层次的波光。',
'night-reverse':'反光带随观察方向消失，地形遮挡和同世界关系维持。大范围海面仍平滑暗蓝，波形难读；近云底仍有岩石折面，天空反复小圆团。后者包含原World云，不能全部归因于新云。',
'day-reference':'实际新云为白色浅圆底块，但主体仍是均匀平底、几团孤立山丘，天空密度/层次远少于参考。海面基本平蓝，仅近岸青色深度带可读。'}
manifest=read(run/'manifest.json');gate=read(R/'reviews/round-27b-sky-native-check.json')
report={'round':'27b','reviewer':'independent village_floor_review','verdict':'reject_cloud_water_art_candidate','scope':'Bounded direct review of all three actual GPU images, ref1342,26b/27a context, actual frozen identity and cloud projection. No production edits or repeated26b collision tests.',
'gpu_status':manifest['status'],'gpu_stages':[{k:x.get(k) for k in ['name','status','exit_code']} for x in manifest['stages']], 'native_gate_passed':gate['passed'],'asset_identity':assets,
'same_world_hash':len({s['world_sha256'] for s in sides.values()})==1,
'same_cloud_placements':all([a for a in s['environment_study']['native_sky_assets'] if a['asset']!='moon']==[a for a in sides['night-reference']['environment_study']['native_sky_assets'] if a['asset']!='moon'] for s in sides.values()),
'shader_identity':[{'name':n+'.gdshader','sha256':sha(R/'captures/coast_environment_study_27b'/(n+'.gdshader')),'matches_frozen':sha(R/'captures/coast_environment_study_27b'/(n+'.gdshader'))==sha(run/'study-inputs/new-environment27b'/(n+'.gdshader'))} for n in ['cloud_surface','open_water']],
'images':{v:{'path':str(run/'images'/f'{v}.png'),'sha256':sha(run/'images'/f'{v}.png'),'camera':sides[v]['camera'],'observation':obs[v]} for v in views},
'cloud_consumption':{'preview_uses_new_environment27b':True,'actual_glb_projection':read(R/'reviews/round-27b-cloud-screen-projection.json'),'projection_scope':'GLB vertices with recorded scale/position and adapter y rotation0.35; camera projection in1672x941. Global cloud shader drift up to9world-m not included; bounding boxes are approximate, sufficient to identify visible main clouds.'},
'water_mechanism':'Shared continuous noise height field sampled at jittered Voronoi sites in world space; a constant sampled normal per facet. cell_size=(10.5,3.6)m. Observer changes reflection, not facet placement. This yields discontinuous visible normal/facet boundaries despite continuous source heights. No actual mesh-wave displacement.',
'limits':['Large-wave sine removed, but base ripple, foam and day normal still include sinusoidal terms.','World-space implementation and reverse view support real view relationships, but do not prove temporal quality or arbitrary flight.','Cloud shading remains surface light/haze approximation, not density scattering.','Native closed-solid and GPU success do not confer visual acceptance.'],
'overall_accepted':False,'production_modified_by_reviewer':False,'remaining':['Replace ice-tile/facet read with a better hierarchy of irregular wave glints.','Cloud thickness silhouette and underside remain slab-like; refine final viewed volumes not merely topology.','Beams and broader coast/reference fidelity remain unaccepted.']}
(R/'reviews/round-27b-cloud-water-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='''# 27b 云与水面独立限定审查

结论：**本轮云、水面美术仍打回。** 水光有变粗、断裂的变化，但近处更像大片多边形冰面，远处仍有横排条纹；云的最终比例仍显薄碟托山丘。整体参考未接受，未装生产。

三张实际 GPU 图均直接查看，与原 `ref/1342.png` 及 26b/27a 比较。run 终态 passed，三个 exit code 为 0；新云 native 重开 gate 通过。三个新云源与冻结输入一致，月球 BLEND/GLB 与 21b 逐字节相同。三图同 World SHA、同新增云布局。具体路径、SHA 与视角写入同名 JSON。

| 视角 | 独立观察 |
| --- | --- |
'''
for v in views:md+=f'| {v} | {obs[v]} |\n'
md+='''
## 新云确实进入画面

冻结 preview 明确加载 `new-environment27b`。实际 GLB 顶点结合 sidecar 相机和实例变换独立投影：主 cloud_bank_0 约在像素 (698,261)–(912,314)，主 cloud_bank_1 在 (1055,305)–(1341,367)，正对应画面中仍扁薄的两云。近似框未计 shader 的至多 9m 全局横移，足以辨认对象；不是根据生成器拓扑就推断视觉改善。完整投影见 `round-27b-cloud-screen-projection.json`。

## 水光与边界

shader 以世界空间 10.5×3.6m 基础单元的抖动 Voronoi 点选择法线；法线采自同一连续高度场，但一个面区使用一个采样法线，区域边界仍不连续。这与实际巨大拼片观感吻合。反向不保持屏幕固定亮带，世界空间反射关系成立；它不能证明波面造型已经自然。大波正弦已移除，底色 ripple、泡沫和白天法线仍含正弦；不声称一切周期因素消失。水面无真实顶点波浪，三张静图也不证明运动品质。

本轮不重复 26b 道路/屋基/岸体碰撞。灯塔光束仍未实现，整体场景参考忠实度仍不接受。继续改最终云形厚度、轮廓层次与波光尺度；不用再重跑本轮已完成的三图来证明 native 通过。
'''
(R/'reviews/round-27b-cloud-water-independent-review.md').write_text(md,encoding='utf-8')
print(json.dumps({'status':manifest['status'],'native':gate['passed'],'assets_match':all(x['matches_frozen'] for x in assets),'world_same':report['same_world_hash'],'cloud_same':report['same_cloud_placements']},indent=2))
