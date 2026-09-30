from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parents[1]
run='lantern-island-31f-20260908T204147Z-c8f8aed2cd5f43a7be28d18f0f9ba891'
folder=R/'captures/validation_runs'/run/'images'
obs={
'night-reference':'中央岛比例和右侧守塔屋维持，夜间全景仍读作一组较大的灰岩面。背面局部变化在此视角不足以判定；不能把灯光遮蔽下的轮廓当成近面造型完成。',
'day-reference':'原生建筑与岛体相对比例维持。中央岛前沿有不同大小的岩块，但主坡与短宽岩根的连续关系仍弱，不能仅凭全景紧凑感接受。',
'day-d-front':'与前稿相同的两前肩仍像附在大坡上的独立凸石；上部大片灰面、较直的暗接缝和下部板状台面保持。背部雕刻没有解决这一面。',
'day-d-back':'直接对照31e：塔左下方原坡凹折更明显，中层亮面下端和海口确实偏转，直向海口有所减弱。这些是可以保留的主壳变化。但塔脚向下的中央亮窄条仍可一眼连续追踪，旁边暗缝贯入海口，左右两块大坡继续夹住它；尚未成为短宽交错的承重岩肩。',
'day-c-front':'两前肩短而孤立，后缘仍缺少与上坡共同构成的大面，附近锐暗缝仍明显。没有出现31h密集折扇，但参考要求的短宽岩根组织依然未达成。'
}
actions=[
'保留31f原高坡和海口实际参与变形的方向；保留其真实支承，不因自定2m树盘外围变化退回旧稿。',
'下一稿应先改背面中央窄条及两侧夹壁的局部面组织：选择覆盖窄条、左右相邻原坡的一个连续面区，删除或重接在该区内贯穿上下的纵向边链，用少量跨过旧接缝的斜向宽面重新组织，而非继续对同一条带施加球形位移。新顶点和边界必须从实际GLB/原生源确认。',
'中层做一个偏向一侧的短宽斜肩，另一侧在不同高度形成短断面；让旧暗缝在中层宽面内终止，另一个断口向侧边错开。不能让两条平行接缝继续从塔脚直达水边，也不要形成整齐的一条水平环阶。',
'低根保留本版海口偏转，并把中央窄根与一侧原坡连接成钝宽的海侧端面；局部切口只能短距离延续，不能仍是从中层到底的狭长深口。这需要连同相邻旧面重接，不再新增填槽凸包。',
'保护真实道路、建筑基础与实际树干支承区域；边界外可在面内切分重接。2m树盘和旧水线不是用户永久硬约束。若后续必须改变实际树干支承，显式重新落地并核验，不能仅靠旧盘冻结锁死宽面。',
'前面两孤立凸石仍单独待改，应把肩后缘与主坡一起组织为宽接续，不用再加一批小石遮盖。'
]
def evidence(p):
    return {'path':str(p.relative_to(R)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
g=json.loads((R/'reviews/round-31f-independent-geometry.json').read_text())
rt=json.loads((R/'reviews/round-31f-runtime-incremental.json').read_text())
report={
'round':'31f','run_id':run,'visual_verdict':'retain_actual_high_flank_and_mouth_reform_but_retopologize_central_longitudinal_strip_with_adjacent_faces',
'candidate_retained_for_iteration':True,'visual_complete':False,'full_reference_accepted':False,'all_reference_goal_complete':False,
'reference':{**evidence(R/'ref/1342.png'),'directly_viewed':True},
'comparison_images':[{**evidence(R/'captures/validation_runs/lantern-island-31e-20260908T203322Z-c8a7a40b1ae5442c8aeba5858633afbd/images/day-d-back.png'),'directly_viewed':True}],
'images':[{'view':n,**evidence(folder/(n+'.png')),'directly_viewed':True,'judgment':s} for n,s in obs.items()],
'retained_changes':['High original rear flank has a stronger visible concave break.','Middle lower end and seaward mouth visibly turn compared with31e.'],
'remaining':['continuous central narrow bright strip','dark side seam extending into the seaward mouth','large flanking grey faces','front isolated convex stones'],
'next_actions':actions,
'geometry':{'report':evidence(R/'reviews/round-31f-independent-geometry.json'),'passed':g['pass'],'triangles':2342,'vertices':1173,'moved_vertices':72,'moved_triangles':192,'minimum_changed_normal_cosine':0.5577746903882042,'normal_reversals':0,'local_intersection_report':evidence(R/'reviews/round-31f-local-intersections.json'),'AABB_pairs_tested':2071,'illegal_intersections_found_at_stated_tolerance':0},
'tree_support':{'report':evidence(R/'reviews/round-31f-actual-tree-support.json'),'old_tree_disk_surface_preserved':False,'actual_tree_base_support':True,'changed_old_disk_area_m2':2.835297221203243,'maximum_old_disk_lowering_m':0.0404610397654,'affected_instances':'C and D local approximately(8.28,6.48), scale0.7','actual_frozen_pine_bottom_circumradius_m':0.43000000715,'affected_real_base_area_each_m2':0.235388308166846,'all14_actual_base_regions_continuously_covered_and_unchanged':True,'whole_flat_bottom_contact_claimed':False},
'anchor_and_rock_contact':{'report':evidence(R/'reviews/round-31f-anchor-rock-contact.json'),'anchor997_displacement_m':2.278705865,'anchor409_displacement_m':1.791647148,'anchor388_displacement_m':2.307054609,'sampled_rock_names':['North broken ridge','Northwest split buttress','North tidal end'],'sampled_overlap_positive':True,'whole_contact_or_visible_integration_proven':False},
'root_runtime_report_read':{'report':evidence(R/'reviews/round-31f-runtime-incremental.json'),'passed':rt['passed'],'bindings':rt['binding_count'],'positions_per_view':59,'maximum_position_delta_m':max(v['maximum_position_delta_m'] for v in rt['views']),'maximum_footing_delta_m':max(v['maximum_footing_delta_m'] for v in rt['views'])},
'limits':['No Blender/GPU/support/intersection rerun during this visual review.','Local finite-triangle sweep excludes unchanged/unchanged baseline pairs and uses0.1mm legal-shared-feature tolerance.','Historical operands are provenance, not the final31f hull/exterior.','Native tree-base continuous support does not mean a flat tree bottom touches sloped ground everywhere.','Positive sampled rock-section overlap may include buried rock and does not establish complete contact or visible artistic integration.','Reference1342 supplies style/form comparison, not an unseen rear-side reconstruction or exact3D measurement.','No full walking, whole-world or20reference completion claim.']}
(R/'reviews/round-31f-island-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='# 31f 岛体独立造型审查\n\n保留高坡和海口实际参与改形的方向，整体仍不接受。背面较31e有更明显凹折和偏转，但中央窄条及两侧长缝仍主导造型。下一稿应重接中央条带与相邻大坡的局部宽面，而不是继续在同一边链上加雕刻位移。\n\n直接逐张查看五张31f原图，并直接对照31e背面与ref/1342。运行：`'+run+'`。\n\n'
for n,s in obs.items(): md+='## '+n+'\n\n'+s+'\n\n'
md+='## 有界返工方向\n\n'+'\n\n'.join('- '+x for x in actions)+'\n\n## 几何与实际支承边界\n\n实际主壳2342三角、1173点，72点位移影响192三角，闭合单连通。997/409/388实际位移约2.279/1.792/2.307m；6个原始z≤0.2m点实际移动，海口改形不是只移动内部高处。道路、pad、路径与17岩保持。改变三角最小前后法线cos0.557775、无反转；2071对实际局部候选未发现合法共享特征0.1mm容差外的三角自交。未重跑未变/未变对，也不以连续映射可逆替代离散检查。\n\nC/D各一棵约(8.28,6.48)、scale0.7树旁的旧2m盘外围发生最多4.046cm降低，总改变面积2.835297m²。按冻结pine.glb实际六边形底面及真实实例变换核验，14棵实际树干底域均完整连续覆盖且旧支承面不变；受影响两棵底域各0.235388m²，轴心高度误差约0.25–0.26mm。`old_tree_disk_surface_preserved=false`，`actual_tree_base_support=true`；连续支承不等于水平干底与斜面处处贴合。\n\n以海口整片受影响三角的前后包围域筛选原岩，在North broken ridge、Northwest split buttress、North tidal end的报告所列高度截面仍有正交叠。此证据限定于这些截面，不证明全部接触、更不证明岩肩可见咬合成功。历史三个凸包仅作为来源，不定义最终31f外露。\n\n读取本版root运行审计：200绑定、每视角59落点，位置最大差'+str(report['root_runtime_report_read']['maximum_position_delta_m'])+'m，基础样本最大差'+str(report['root_runtime_report_read']['maximum_footing_delta_m'])+'m。几何与运行通过均不等于造型完成。`full_reference_accepted=false`；全部20张参考目标仍未完成。\n'
(R/'reviews/round-31f-island-independent-review.md').write_text(md,encoding='utf-8')
print('31f five-view independent MD/JSON written; retain iteration direction, visual/full reference false.')
