from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];run='lantern-island-30c-20260908T181715Z-31c81298860748f3ac9257c092e5f4b5'
views={'night-reference':'The former thin terrain collar no longer separates the central island into an obvious extra tier. Tower/native building proportions and keeper-house-right composition remain. The broad upper mound remains too regular relative to 1342, so night view is still incomplete.','day-reference':'The narrow artificial dark rim has disappeared at the small central island. Broad unbroken grey surface remains dominant, with only small peripheral fragments visible; this is a local improvement rather than reference acceptance.','day-d-front':'Front collar is gone; coast panels meet upper terrain continuously. Dark lighting emphasizes a large connected slab-like grey slope below the occupied plateau. Shorter foreground crags remain visible, while several side shoulders are swallowed by the body.','day-d-back':'The previous thin band is absent around the rear. A large left/right skirt-like mass is still formed by actual broad sloping terrain, with a deep central cleft; the cleft is a useful asymmetric feature, but the two wide smooth lobes remain too simple.','day-c-front':'Most direct comparison with 30b: the thin dark line across the mid/lower slope is visibly removed. The unchanged wide upper grey plane and broad left shoulder are still evident. No new obvious open seam is visible, but visual absence of a seam is not a full 3D intersection proof.'}
images=[]
for v,j in views.items():
 p=R/'captures/validation_runs'/run/'images'/f'{v}.png';images.append({'view':v,'directly_viewed':True,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'judgment':j})
report={'round':'30c','run_id':run,'visual_verdict':'retain_welded_shell_and_collar_removal_continue_selective_main_body_sculpting','full_reference_accepted':False,'all_reference_goal_complete':False,'images':images,'compared_to':['30b same-camera actual GPU images','ref/1342.png'],'geometry_evidence':'reviews/round-30c-independent-geometry.json','local_visual_success':['Artificial 0.65m dark collar visibly removed in front/back views.','Preserves 30a native building/land proportions and D reference house-right placement.'],'remaining':['Broad upper grey slope remains visually dominant.','Several buried short shoulders provide little visible contribution.','Rear broad lobes and sparse low shoreline fragments do not yet match irregular reference fractures.'],'next_actions':['Prioritize selective cuts/reforming of the main-body slope enveloping West/Southwest and much of North, preserving short wide low shoulder character.','Use 30b sampled overlap ratios only as a starting localization; measure candidate exposed surface after sculpting. Do not translate every shoulder outward uniformly: East/Northwest have much lower overlap.','Create two or three offset changes of slope/short ledges reaching the shoreline, with unequal spans and elevations, rather than a circumferential ledge or a new ring of isolated rocks.','Preserve actual occupied support and native building dimensions. If a desired cut meets a road support area, revise and refit that local route with real geometry checks instead of freezing the whole broad plateau indefinitely.'],'runtime_evidence_attribution':{'owner':'root','path':'reviews/round-30c-runtime-incremental.json','reported_matching_bindings':196,'reported_placements':59,'reported_max_delta_from_30a_m':0.00009155273437,'independently_rerun_here':False},'limits':['No GPU/Blender launched by reviewer.','30b section intersections are prior bounded evidence, not new 30c section measurements.','No claim of exhaustive self-intersection, full walking, whole-scene/reference completion.']}
(R/'reviews/round-30c-island-independent-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md='''# 30c 独立造型审查

结论：保留焊接后的原生实体；0.65m 人工侧裙造成的细暗环已在真实图中消除。宽大灰坡仍然明显，整体未达到 1342，`full_reference_accepted=false`，全部参考 Goal 未完成。

已逐张直接查看本轮五张原始 GPU PNG，并与 30b 同相机图片、1342 对照。原图路径和 SHA256 见同名 JSON。

## 五视图判断

'''+''.join(f'- **{v}**：{j}\n' for v,j in views.items())+'''
## 实际几何增量

独立解码 GLB，核对原生证据：19 个对象；保留 745 个实际地表顶点、1470 个顶面顺序与材质，整道路和17块岩体保持。焊后主实体799点/1579面，原54个下部海岸顶点保持，上侧片直接接真实top边界，旧内部cap和0.65m侧裙删除。源边成对且方向相反；实际GLB按位置合并后的三角边全部成对，三角形面积非零，实际有向体积22521.044755m³。各侧片投影有效，局部中心在片区内。完整数据见 `round-30c-independent-geometry.json`；这不是全体三维自交证明。

Root 的运行增量报告为196绑定匹配、59落点相对30a最大差0.00009155273437m，不能写全零。这里保留来源 `round-30c-runtime-incremental.json`，未重复其运行实测。

## 下一步优先改主实体包裹坡面

实际图中细带消失，但宽灰坡没有消失，说明侧裙只解释那条细带。day-c-front 左侧大坡与中央面、day-d-back 两个宽大坡瓣仍主导轮廓。应先对包住 West/Southwest、较多 North 的主实体局部削改、形成错位坡折，露出已有短宽低肩的一部分。30b 截面中这些岩肩近乎全截面埋入，是定位起点而不是新30c实测；可见贡献仍必须看面和轮廓。

不要全部岩块统一外移。East/Northwest 先前截面重叠很低，再外移可能放大离体碎块。更有价值的是两三段长短不同、高低错位的短台阶或断面，连接上坡与海岸，并与保留岩肩有局部连续接触；避免重新做一圈连续阶沿或等距碎石珠链。

保留建筑原生尺度和实际占用支承区。如造型需要改到道路支承区，应局部调整真实地表并重新贴合道路、检验坡度/净空，不再把整块宽坡永久冻结为造型约束。此次不要求无差别移动建筑，也不应以全岩截面重叠替代露出面积。

本审查未启动引擎/Blender，没有重跑30b完整截面或30a全部pad/path检查；仅本轮增量核验和五原图直接审查。全参考、美术、行走与场景完成仍分别待满足。
'''
(R/'reviews/round-30c-island-independent-review.md').write_text(md,encoding='utf-8');print('30c final MD/JSON written')
