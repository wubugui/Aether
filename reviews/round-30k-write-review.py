from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1];run='lantern-island-30k-r1-20260908T193210Z-09e7ff871c9941519a561b4fede063ee'
views={'night-reference':'Corrected tree group is lower on the east shoulder and the compact tower/house composition remains. The central island reads more simply than30h, but its upper mound and limited short convex block layering still differ from1342. Night scale alone is insufficient for acceptance.','day-reference':'Fewer broad surfaces replace the fluted front, preserving building proportions and house-right composition. However the island still reads as a regular upper mass above a small number of peripheral fragments; short staggered convex shoulders are not yet clearly expressed.','day-d-front':'Dense vertical fan recesses are removed. There are now fewer large concave/slope faces and the two relocated trees occupy a lower east ledge. The left main face is too large and plate-like; central straight cuts and pointed notches remain. This is a valid direction, not complete shape acceptance.','day-d-back':'Old broad rear lobes and long narrow central cleft remain. Tree relocation is visible from the reverse side without an obvious floating whole tree, but this does not prove complete trunk-base contact. The south/east change did not fix the rear cleft.','day-c-front':'Most direct improvement over30h: no repeated line of narrow vertical fan facets. The left/front surface around x530-770,y495-590 is instead an oversized continuous inclined slab; a straight seam and narrow pointed cut remain near its inner/right side. The lower tree group adds vertical layering, but wider concave planes alone do not create the reference short broad convex block structure.'}
images=[];tree_rows=[];geom=json.loads((R/'reviews/round-30k-independent-geometry.json').read_text());plan=json.loads((R/'captures/lantern_island_study_30k/proportion-plan.json').read_text())
for v,j in views.items():
 p=R/'captures/validation_runs'/run/'images'/f'{v}.png';images.append({'view':v,'directly_viewed':True,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'judgment':j});sp=Path(str(p)+'.json');side=json.loads(sp.read_text());trees=[t for t in side['placements'] if t.get('kind')=='existing_native_pine' and t.get('island') in ['island_c','island_d']];assert len(trees)==14
 for island in ['island_c','island_d']:assert sum(t['island']==island for t in trees)==7
 for t in trees:
  assert t['ground_collider'].startswith(t['island_root']+'/');origin=[-3050,0,-2650] if t['island']=='island_c' else plan['d_world_position'];yaw=0 if t['island']=='island_c' else plan['d_yaw'];dx=t['position'][0]-origin[0];dz=t['position'][2]-origin[2];c,s=math.cos(yaw),math.sin(yaw);xy=[c*dx-s*dz,-(s*dx+c*dz)]
  for wanted in geom['two_relocated_tree_supports']:
   if math.dist(xy,wanted['new_blender_xy'])<.002:
    assert t['scale']==wanted['native_instance_scale'];tree_rows.append({'view':v,'island':t['island'],'actual_local_blender_xy':xy,'actual_world_position':t['position'],'scale':t['scale'],'normal':t['ground_normal'],'normal_slope_deg':math.degrees(math.acos(t['ground_normal'][1])),'island_root':t['island_root'],'ground_collider':t['ground_collider'],'actual_collider_is_descendant_of_recorded_root':True})
assert len(tree_rows)==20
runtimepath=R/'reviews/round-30k-runtime-incremental.json';runtime=json.loads(runtimepath.read_text());ref=R/'ref/1342.png'
report={'round':'30k','run_id':run,'visual_verdict':'retain_sparse_broad_face_direction_and_lower_tree_group_continue_convex_block_and_rear_cleft_rework','full_reference_accepted':False,'all_reference_goal_complete':False,'reference':{'path':'ref/1342.png','directly_viewed_this_review':True,'sha256':hashlib.sha256(ref.read_bytes()).hexdigest()},'images':images,'compared_to':['30h and30d actual original views','ref/1342.png'],'geometry_evidence':'reviews/round-30k-independent-geometry.json','local_visual_success':['30h dense repeated fluted facets removed.','South/east visible slope actually changes to fewer broader planes.','Two east trees visibly move to lower supported shoulders; preserved native scales and7trees per C/D confirmed in actual sidecars.'],'remaining':['Left/front oversized smooth sloping slab.','Central narrow notch/straight cut and insufficient short convex rock shoulders.','Long narrow rear cleft and broad rear lobes unchanged.','Upper platform/landmass still looks too orderly relative to1342.'],'next_actions':['Use the existing actual camera/source localization to select the oversized left slope and its central seam; add a short convex shoulder relationship by retaining/rebuilding a finite-width main-rock block between staggered cuts.','Break the large slab into two or three unequal connected broad planes with a visible convex knee and unequal contour heights, not a larger set of concave bowls.','Shorten or offset the straight internal seam so it does not run as a deep narrow incision from upper platform toward shore; identify its actual source region before editing.','Retain the improved lower tree grouping and sparse face organization while checking real support for any affected trees.','Handle the rear deep cleft as a separate targeted edit after front convex hierarchy is readable.'],'actual_tree_sidecar_readback':{'method':'Read existing actual five image sidecars, no new runtime.14C/D trees per view,7each;20 relocated-tree records across5views validated by localXY, scale and collider ancestry.','relocated_records':tree_rows,'full_trunk_base_contact_claimed':False},'runtime_audit_attribution':{'owner':'root','path':str(runtimepath.relative_to(R)),'sha256':hashlib.sha256(runtimepath.read_bytes()).hexdigest(),'reported_passed':runtime.get('passed'),'same_run':runtime.get('run_id')==run},'first_run_failure':{'run_id':'lantern-island-30k-20260908T192949Z-41ba6a989146416bad656363cee4a501','attribution':'Root reported checker falsely required logical island_d substring in actual collision path; D asset instance root is IslandD_CVariant. R1 actual sidecars record island_root and ancestry.','native_geometry_changed_for_retry':False,'failed_run_retained':True},'limits':['Geometry continuity and sidecar ground hits do not prove entire flat trunk base touches a sloping surface.','Manual image rectangle is a visual locator, not segmentation.','No reviewer GPU/Blender launched. Fullreference remains false.']}
(R/'reviews/round-30k-island-independent-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md='''# 30k-r1 独立造型审查

结论：保留少量宽面的方向与东侧低肩树组；30h密集折扇确已消除。整体仍未通过1342：前左部变成过大的整片斜板，中部仍有尖窄切口，背面长槽没有解决。`full_reference_accepted=false`，全参考Goal未完成。

已直接逐张查看30k-r1五张原始GPU图及1342，对照30h/30d实际图。原图SHA与路径见同名JSON。

## 五图

'''+''.join(f'- **{v}**：{j}\n' for v,j in views.items())+'''
## 保留和剩余差异

前坡从30h反复排列的细尖凹面，变为更少的宽折面，这是明确改善。两棵东树落到较低的肩面，画面层次更清楚；没有必要为降低后的树位再保留旧圆筒保护壁。

但day-c-front左侧约x530–770/y495–590仍是一块很大的连续斜板，内部直分缝和尖窄口仍明显。参考中央岛的宽块面具有短、厚、凸起和错位关系；“把很多窄凹面换成几块更宽的凹面”仍不等于实现这种层次。此处应保留/重塑有真实宽度的主岩凸肩，接到两三块高程和方向不同的大面，缩短或错开长直切口。不要继续只增加凹面宽度、深度或数量。

背面原来的长窄深槽和两片宽坡瓣基本没有变化，需要单独定位处理。前侧更好不能使后侧自动通过。仍应按真实相机/源面定位修改前左斜板与中间分缝，避免再按岩块名字猜方向。

## 树组落位

直接读取五份本版原图侧车：C、D每视图各7棵松树，五保留与两移位的数量关系保持。20条移位记录（两树×两岛×五视图）局部坐标匹配(17,-1.5)/(17.6,-5)，尺度0.8/0.55保持，实际ground_collider均处于所记录island_root之下。它们在正背面未见明显整树悬空。原生几何已验证0.3m盘连续上向支承，第一棵约21.31°、盘高差0.1909m，第二约4.41°。这不等于整树干底面与坡面全部贴合，不作该声明。

## 运行与证据范围

审查对象为30k-r1。首次30k运行因Root的碰撞根检查误将逻辑island_d字符串当实际节点名而失败；该失败保留，Root修复为实际island_root/collider ancestry检查后重跑，原生模型没有重建。R1侧车中的D根为复用C资产的实际根，不能再用逻辑名字子串要求它。

Root的本版增量JSON已读取并归属其运行证据；独立报告没有启动新GPU/Blender。道路/pad/五保留树支承与17岩、路径保持、六点实际切深见 `round-30k-independent-geometry.json`。运行passed、原生闭合与局部美术改善不替代完整场景/全参考验收。
'''
(R/'reviews/round-30k-island-independent-review.md').write_text(md,encoding='utf-8');print(json.dumps({'written':['round-30k-island-independent-review.md','round-30k-island-independent-review.json'],'runtime_same_run':report['runtime_audit_attribution']['same_run'],'actual_relocated_tree_records':len(tree_rows),'full_reference_accepted':False}))
