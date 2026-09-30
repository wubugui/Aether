from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];run=R/'captures/validation_runs/foreground-island-32e-20260908T223609Z-ac0259d9ba184d03b996e8edae4e4dc9';frozen=run/'study-inputs';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=read(R/'captures/rightcoast33-native-intake.json');layout=read(frozen/'headland/layout.json');paving=read(frozen/'village-paving/paving-design.json');grading=read(frozen/'village-grading/build-report.json');scene=read(run/'images/night-reference.png.json')
source=R/native['source'];assert sha(source)==native['source_sha256'];glb=source.with_suffix('.glb');assert sha(glb)==sha(frozen/'headland/mainland_headland.glb')==grading['glb_sha256'];assert sha(frozen/'village-paving/paving-design.json')==grading['paving_design_sha256'];assert paving['headland_glb_sha256']==grading['source_glb_sha256']
groups=[]
for g in paving['groups']:
 paths=[R/'captures/village_paving_study_26b'/('village_'+g['name']+ext) for ext in ['.blend','.glb']]
 assert all(p.exists() for p in paths);groups.append(dict(name=g['name'],origin=g['origin'],solids=len(g['solids']),assets={str(p.relative_to(R)):sha(p) for p in paths}))
assert len(layout['houses'])==9 and sum(g['solids'] for g in groups)==922
out=dict(scope='33 read-only actual26b right-coast intake following32foreground stage. Main goal all20references+original opening remains active. No33model produced and no production mutation.',native_source=native['source'],native_source_sha256=native['source_sha256'],native_intake_sha256=sha(R/'captures/rightcoast33-native-intake.json'),statistics=native['statistics'],origin=layout['origin'],houses=layout['houses'],paving_groups=groups,current_headland_glb_sha256=sha(glb),actual_camera=scene['camera'],basis_run=run.name,bindings={str(p.relative_to(R)):sha(p) for p in [frozen/'headland/layout.json',frozen/'headland_runtime_23g.gd',frozen/'village_paving_runtime_26b.gd',frozen/'village-grading/build-report.json',frozen/'village-paving/paving-design.json']},runtime_linkage='village_paving_runtime_26b checks retained paving design against grading.source_glb_sha256 (historical23g basis), actual headland GLB against grading.glb_sha256, and paving file SHA. Future33terrain revision must truthfully record new immediate native/source basis and update affected runtime binding contract instead of forging old provenance or disabling checks.',next_action='At the fixed reference camera, localize visible coast/front platforms and inland ridge against actual26b triangles and occupied9house/922paving regions. Design unequal headlands/low coves/setback ridges with coherent terrain/roads/scatter; retain current source, do not restore23g terrain or generate full world.')
p=R/'reviews/round-33-rightcoast-intake.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
text='''# 33 右岸接续：实际26b原生入口

本次只读取当前原生源和已运行装配，尚无33模型。按主参考优先级，前景A32阶段保留构图改进后，下一项是右岸岩岬、低湾与后山的纵深，再处理水面与暖灯。A和C/D整体美术仍未完成，全部20参考及原开场目标不变。

权威岸体是 `captures/village_grading_study_26b/mainland_headland.blend`，不是更早23g。已用Blender只读打开，源SHA未变，12独立件：主壳 `Mainland headland continuous bedrock and grass terraces`，8192点/16380实际三角，另11原岩肩。局部主壳边界范围Blender(-94,-190,-10.00003)..(190,220,44.48182)，世界原点(-2180,0,-1830)。完整坐标、面、材质和变换在 `captures/rightcoast33-native-intake.json`，不需再次开源只为列数。

九座主体屋、28棵原生松树的装配由冻结 `headland_runtime_23g.gd` 和 `headland/layout.json` 驱动。两组街巷共922实体来自 `captures/village_paving_study_26b/village_foreground.blend` 与 `village_bay.blend`；地形已配合这些真实路面修整，不能用旧23g地表覆盖。屋世界位置、路组原点和完整资产SHA见同名JSON。

当前 `village_paving_runtime_26b.gd` 对铺地原设计、26b修地报告和实际岸体GLB有来源绑定。将来替换33岸体时必须如实记录新的直接源、保留的旧铺地设计以及受影响范围，并同步运行时契约。不能为了运行通过伪造23g来源、删除身份检查或把旧报告绑定到新网格。

下一步先从同版主图把可见的大平灰台、湾口和内陆坡脊定位到当前实际三角与九屋/922铺地占用。随后制作不等宽、不等高、前后退让的岩岬和低湾，并在屋后建立有实体厚度的后山层次；受影响的道路、树和原地形衔接随形体变化同步。主视图可读性优先，不以没有原图的背坡精度阻塞全景进展。不能只涂灰、堆重复石块或把全部背景换成贴图。

本次只读Blender进程37296已结束，所有结果已落盘。真实五图基线在JSON记录的32e运行中；32f仅修改A局部地坪混合，右岸资产身份仍相同。最终32阶段接续以 `WORKSPACE_RESUME.md` 和32f最新同版证据为准。
'''
p=R/'reviews/round-33-rightcoast-intake.md';assert not p.exists();p.write_text(text,encoding='utf-8');print(json.dumps(dict(native_parts=len(native['statistics']),houses=len(layout['houses']),paving_parts=sum(g['solids'] for g in groups),source_sha256=native['source_sha256']),indent=2))
