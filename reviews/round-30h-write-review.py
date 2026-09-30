from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];run='lantern-island-30h-20260908T191003Z-b60fbd9ddc33459aa01a7396a355b6db'
views={'night-reference':'Central D retains correct scale direction and keeper-house-right layout, but the new south/east facets contribute little clear short broad shoulder structure at this distance. The upper island mass remains orderly compared with1342. Night darkness cannot establish acceptance.','day-reference':'Central island remains a broad compact mound with several low peripheral fragments. Local cuts exist, but at reference framing they do not yet produce the reference rhythm of irregular broad blocks and interlocking slope breaks.','day-d-front':'The front slope is now visibly modified. However, a row of tall narrow concave bays and straight near-vertical separators replaces the broad slope. Several triangular tips terminate along a similar low edge, creating a fluted retaining-wall appearance rather than short staggered natural rock shoulders.','day-d-back':'Essentially retains the earlier broad rear lobes and long narrow deep central cleft. Rear geometry was not meaningfully fixed by the south/east cuts. Existing straight cuts still read as a separate unresolved form problem.','day-c-front':'Clearest new failure: roughly x555-1005,y495-605 shows repeated pointed vertical facets/fan-like concave faces. South/east source regions have genuinely changed, but the connected row of similarly directed recesses is too regular. The occupied upper platform and near-tree high material remain; the unchanged low detached rocks do not repair the middle slope rhythm.'}
images=[]
for v,j in views.items():
 p=R/'captures/validation_runs'/run/'images'/f'{v}.png';images.append({'view':v,'directly_viewed':True,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'judgment':j})
ref=R/'ref/1342.png';geom=json.loads((R/'reviews/round-30h-independent-geometry.json').read_text());runtimepath=R/'reviews/round-30h-runtime-incremental.json'
runtime={'owner':'root','available_at_review':runtimepath.exists(),'independently_rerun_here':False}
if runtimepath.exists():
 rt=json.loads(runtimepath.read_text());runtime.update(path=str(runtimepath.relative_to(R)),sha256=hashlib.sha256(runtimepath.read_bytes()).hexdigest(),passed=rt['passed'],matching_bindings=rt['binding_count'],placements_per_view=59,maximum_position_delta_from30a_m=max(v['maximum_position_delta_m'] for v in rt['views']),maximum_footing_delta_m=max(v['maximum_footing_delta_m'] for v in rt['views']))
report={'round':'30h','run_id':run,'visual_verdict':'reject_current_fluted_slope_form_retain_valid_shell_and_visible_region_localization','full_reference_accepted':False,'all_reference_goal_complete':False,'reference':{'path':'ref/1342.png','sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'directly_viewed_this_review':True},'images':images,'compared_to':['30d actual original front/back/reference views','ref/1342.png'],'geometry_evidence':'reviews/round-30h-independent-geometry.json','near_protection_evidence':'reviews/round-30h-near-protection.json','retained_value':['Valid native closed exterior and verified support/protection method.','Correct south/east visible target localization and proof of real cuts.','Existing building scale/placement direction and removed0.65m collar.'],'shape_not_accepted':['Repeated tall narrow concave bays and pointed radial facets on front.','Similar bottom edge and parallel vertical separators read as a fluted wall.','Upper regular plateau and rear narrow deep cleft remain.'],'six_actual_depths_m':[t['actual_vertical_cut_depth_m'] for t in geom['six_target_actual_cut_depths']],'next_actions':['Change the authored transition geometry and footprint layout rather than lowering nominal floor planes again.','Use two or three broader offset patches with unequal heights/widths; deliberately retain convex short shoulders between them. Avoid a connected row of similarly oriented concave pockets.','Replace whole-boundary distance blending as the sole shape rule with explicit broad intermediate facets/knees at staggered heights, locally connected to protected support. This is a design recommendation, not a proven unique cause.','Rebuild front patch triangulation around intended broad planes; dense curved protective-hole boundaries should not fan directly into a few low interior anchors. Preserve exact support using a local joining band.','Treat rear narrow deep cleft separately after front form is readable. Do not uniformly move17rocks or accept a higher changed-volume/triangle count as visual progress.'],'runtime_evidence':runtime,'limits':['No new GPU/Blender launched by reviewer.','Geometric cut depths are measured at old targetXY, not new pixel-height estimates.','Image rectangle is a visual locator, not segmentation.','30e/f/g remain failed builds.30h valid output does not isolate a single earlier Boolean failure cause.']}
report['constraint_provenance']={'user_goal':'Unified scene style, editable native Blender scene construction, no characters; affected trees may be refitted or moved within the ongoing goal.','current_validation_assumption':'Existing tree axes plus2m disks and0.35m extra band are current candidate protection assumptions, not a permanent user prohibition on tree relocation.','next_candidate_option':'If retaining an old east tree disk forces a cylindrical wall or narrow fan transition, propose a localized tree-group relocation/refit on the newly sculpted actual support surface, with old/new transforms and support evidence.'}
report['next_actions'].insert(3,'Do not make old2m tree disks permanent: if an affected east-side tree group forces artificial round walls or dense transition fans, relocate/refit that specific group after sculpting, then verify actual native tree transforms/support and both views. Other trees need not move.')
(R/'reviews/round-30h-island-independent-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md='''# 30h 独立造型审查

结论：当前南东坡折扇状凹面造型不接受。保留正确可见区域定位、闭合原生壳体和保护检验方法，不能将本次前坡形状作为已完成美术。`full_reference_accepted=false`，全参考Goal未完成。

已直接查看1342及本轮五张原始GPU图，并对照30d原图。路径、SHA256及逐视图记录见同名JSON。30e/f/g失败不进入成功基线。

## 五图观察

'''+''.join(f'- **{v}**：{j}\n' for v,j in views.items())+'''
## 改到了正确位置，但形态仍不对

与30d不同，day-c-front南东坡已明显变化。其约x555–1005/y495–605区域出现连续纵向尖三角、狭长凹面、近乎平行的竖向分隔，许多面又落到相近的低缘，形成折扇或带凹槽的挡墙观感。day-d-front的阴影使这个问题更明显。1342中央岛读起来是宽短、错位、相互承接的块面；本版虽增加细面，方向和节奏反而更机械。

不是“30h完全没有改变”，也不是单纯“切深不足”。实际六目标切深分别2.932650、2.877592、0.104291、1.260622、约0、2.562331m，均已独立核验与真实分面底网格吻合。第三处实际只削10.4cm，旧名义2.888m不能再使用；第五处因树保护余量保留。继续降低名义底面可能只加深同一排凹槽，不能自动变成短宽交错岩肩。

近树孔周边已有0.35m局部保护带完整保留，实际刀具底面近树1m带最大坡度75.81°；此数是刀具底面角度，不是已经分离测得的可见主壳角度。它提供检查陡过渡的线索，但不能作为视觉错误唯一成因。

## 下一稿具体方向

建议重排前坡的实际分面与过渡，而非继续整体降低这三把刀。选两三块宽度、高程不等、横向错位的短区段，保留其间的凸肩，避免连接成同方向连续凹槽排。给中段显式安排宽的折点/面，控制坡折在哪个高度、沿哪个方向发生，不再只让整个边界按统一距离混合到低底面。

近保护孔的密集曲边不应直接向少量低位内点作长尖扇形连接；本版精确支承保持已经验证，但不要求未来永远冻结这些旧树位。2m树盘及额外0.35m带是我们对当前候选设定的保护假设，并非用户永久要求。Goal允许受影响树木重新贴地或移动。如果东侧旧树盘迫使主坡保留圆筒护壁、细密过渡，可局部重布受影响树组：先定短宽岩面，将该组移到真实可支承的坡台，记录原/新变换并核验实际原生树落点、支承与正背面画面；其余树无需一起移动。

若该树位仍可合理保留，再用局部连接带接到按美术指定的宽面。这是依据源构造和实际图提出的设计建议，不是证明了唯一成因。下一稿应以相同前视图中“狭长尖面减少、短宽凸凹转折可读”来验收，不能只看修改体积或三角形数。

背面的直窄深槽与大坡瓣仍是另一处未完成形态，南东改形没有解决它。先把前坡面关系做对，再单独处理背槽；不要统一外移17岩，也不要靠补一圈碎岩掩盖主实体问题。

## 保留范围与证据限制

30h真实GLB为19件、2550主壳三角，闭合、正体积21410.772729m³；路径与17岩保持，指定道路/pad/树支承完整。保留这些工程证据、30a以来建筑/陆体比例方向、30c消除人工细裙以及实际可见区定位。它们不意味着接受本版折扇前坡。

已读取Root的本版运行增量JSON：passed，196绑定，59落点相对30a最大差约0.000228882m，详细值及文件SHA见独立JSON，归属Root实测。本审查者没有启动GPU或Blender，没有宣称全场景、完整行走或全部参考完成。
'''
(R/'reviews/round-30h-island-independent-review.md').write_text(md,encoding='utf-8');print('30h final visual MD/JSON written')
