from pathlib import Path
import json,hashlib,math
from shapely.geometry import Polygon,Point
R=Path(__file__).resolve().parents[1];base=R/'captures/lantern_island_study_30d/geometry-evidence.json';e=json.loads(base.read_text());loc=json.loads((R/'reviews/round-30d-visible-slope-localization.json').read_text());sidepath=R/'captures/validation_runs/lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c/images/day-c-front.png.json';side=json.loads(sidepath.read_text());previous=json.loads((R/'captures/island-30e-faceted-cut-plan.json').read_text());east=Polygon(previous['original_specs'][2]['polygon']);trees=[]
for p in side['placements']:
 if p.get('kind')!='existing_native_pine' or p.get('island')!='island_c':continue
 x,y,z=p['position'];xy=[x+3050,-(z+2650)];disk=Point(xy).buffer(2)
 trees.append({'island':'island_c','local_blender_xy':xy,'actual_ground_y_m':y,'native_instance_scale':p['scale'],'old_east_design_intersection_with_2m_disk_m2':east.intersection(disk).area,'distance_to_old_east_design_m':east.distance(Point(xy))})
affected=[p for p in trees if p['old_east_design_intersection_with_2m_disk_m2']>1e-5]
proposal=[{'segment':'southern lip','measured_anchor_pixels':[[620,548],[700,550]],'measured_anchor_xy':[s['hit_blender_xyz'][:2] for s in loc['samples'][:2]],'minimum_form':'One broad shoulder plane with a short inner slope and one unequal seaward drop; no parallel row of deep recesses.','conceptual_shelf_height_range_m':[3.2,4.1],'height_status':'Design suggestion, not measured future geometry or fixed requirement.'},{'segment':'southeast middle shoulder','measured_anchor_pixels':[[770,552],[825,570]],'measured_anchor_xy':[s['hit_blender_xyz'][:2] for s in loc['samples'][2:4]],'minimum_form':'Keep a higher broad convex intermediate block and cut only one side obliquely; set its inner/outer knees laterally offset from the southern lip.','conceptual_shelf_height_range_m':[4.0,4.7],'height_status':'Design suggestion; final source heights/support intersections must decide.'},{'segment':'east returning shoulder','measured_anchor_pixels':[[900,548],[970,548]],'measured_anchor_xy':[s['hit_blender_xyz'][:2] for s in loc['samples'][4:]],'minimum_form':'One low wide returning face plus a higher short inner shoulder, after moving/refitting only the obstructing two-tree group if necessary; avoid a protective cylindrical wall.','conceptual_shelf_height_range_m':[2.9,3.8],'height_status':'Design suggestion. Old tree disks are not a permanent user constraint.'}]
report={'round':'30i_intake','source':str(base.relative_to(R)),'source_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'actual_tree_source':str(sidepath.relative_to(R)),'actual_tree_source_sha256':hashlib.sha256(sidepath.read_bytes()).hexdigest(),'review_basis':'reviews/round-30h-island-independent-review.md','measured_targets':loc['samples'],'minimal_main_plane_organization':proposal,'actual_C_tree_groups':trees,'east_group_to_reconsider':affected,'D_counterparts':'Same authored local tree group also instantiated on island_d; preserve instance scale while recording any revised C/D placements explicitly.','constraint_provenance':'2m tree disks were earlier candidate QA protection, not a permanent user requirement. Building/path support must be checked against actual30i plan; affected trees may be relocated/refitted.','recommendations':['Use at most two or three main planes per segment, plus needed closure; triangulation may subdivide them but should not create a visible repeating fan.','Make three shelf levels and along-coast directions unequal. Leave two finite-width convex joins between segments, not thin knife-edge separators.','Place inner and end cutter rims above source as proposed, but choose explicit intermediate broad knees so the transition does not remain a single tall wall.','Do not set final destination tree positions before actual new support exists. Move/refit the identified east pair to a real interior/side shoulder, checking existing nearby trees, building/road footprint and actual native tree support.','Retain western three and northeastern two trees unless actual new plan intersects them; no blanket relocation.'],'limits':['Proposed shelf ranges are art concepts, not approved30i plan elevations or measured target reconstruction.','Old east design used only to identify the interacting tree group; new30i cutter intersections must be independently recalculated.','No GPU/Blender or30d full-geometry rerun.']}
(R/'reviews/round-30i-form-intake.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md='''# 30i 最小大面组织建议

以实际30d为形体基线，舍弃30h连续折扇凹面的美术形态。六个可见射线命中已独立回检，南侧约(-8.40,-22.85)/(-2.20,-17.61)，东南约(4.53,-14.30)/(9.77,-12.01)，东侧约(14.15,-6.03)/(17.60,0.88)；均为Blender局部XY米，不能再笼统指向West/SW/North。

最小可行组织是三个区段，每段只定义两到三个主面与必要封口：南段一块宽短肩面接短内坡、低外落面；东南段保留较高的宽凸块，斜切其一侧；东段低宽转折面接较高短内肩。三段高程、沿岸方向、内外折点错位，段间保留有宽度的凸接头，不能用细刃分隔出连续同向凹槽。

可供起稿的肩面高度概念：南3.2–4.1m、东南4.0–4.7m、东2.9–3.8m。这只是美术组织建议，并非已测得或固定的30i参数；实际源坡、刀具面和支承交集应决定最后高程。不要把这些值当待再次统一压低的底平面。内侧和两端升出原坡可避免沿整圈挖直槽，但仍须显式给中间宽折点，避免从高边一次跌到低面。

## 应重新考虑的东侧树组

实际C侧车中的东侧两棵为：Blender XY约(14.04004,-1.80005)，scale0.8；(15.12012,-3.95996)，scale0.55。D有同一组局部布置的对应实例。它们是旧东刀具保护内孔/局部绕行的来源；附近(8.28003,6.47998)、(10.80005,5.04004)两棵属于另一组，不应为了简化而全部搬走，西侧三棵也无需跟随。

2m树盘是旧候选检查假设，并非用户要求永久不动。若保留这两棵导致圆筒护壁或尖细扇面，先定东侧宽面，再将该组局部移位或重贴到真实内部/侧部支承面，保持现有原生尺度，记录C/D旧新变换并核验实际支承。当前不编造最终落点；待30i实体面和道路/基础投影已知，再选不与其他树组、建筑和道路冲突的位置。

JSON记录每棵实际树与旧东侧刀具范围的交集，作为组别定位证据。30i新刀具仍须重新算自身交集，不能继承旧设计的净距。本次未启动GPU/Blender或重跑30d整套检查。
'''
(R/'reviews/round-30i-form-intake.md').write_text(md,encoding='utf-8');print(json.dumps({'affected_tree_group':affected,'files':['round-30i-form-intake.md','round-30i-form-intake.json']},indent=2))
