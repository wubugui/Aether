from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
run='lantern-island-31a-20260908T194852Z-ac4f6f47286b4774afd18b8206e9f9ca'
folder=R/'captures/validation_runs'/run/'images'
observations={
'night-reference':'建筑原生比例和守塔屋位于右侧的固定构图仍保留。中景岛前沿的灰色块面变得更分段，但夜景尺度掩盖了两新增肩的规则外轮廓，不能据此接受。参考1342的中央岛是交错斜向岩根承接上台，本版仍是较整齐上台配外围块体。',
'day-reference':'两处前肩在全景中增加了凸起层次，岛体没有恢复为旧高圆台；但中景仍读成规则上台和灰色裙坡。远景只证明形态有变化，无法消除近景暴露的圆帽和柱侧面问题。',
'day-d-front':'新增两肩明确可见，覆盖了部分原连续大斜板。然而两者都有闭合多边形帽面、近直立侧壁及相似收边，读成两颗平顶多边柱或按钮。它们在几何上并入主壳，视觉上却仍像放在坡面上的独立制品。后接上坡的直缝与上台宽灰坡仍在。',
'day-d-back':'新增肩在这一侧没有解决原有后侧问题。塔基以下宽整灰坡和直窄深槽仍明显，槽两侧像直切开的大片岩体；边缘细碎低岩也没有形成参考中的错位承重关系。本视角不能因前面添加实体而标记改善。',
'day-c-front':'与本次直接重新查看的30k同视角相比，左前大斜板被一个宽帽柱打断，中间增加了一个稍小帽柱，确实不是被主岛完全吞没。但约x580–670/y505–578和x720–800/y530–610两处重复的多边帽与竖壁是主要失败。原斜板残部、上台陡坡及中央狭长切缝仍存在；局部遮挡没有形成从上台斜压向海的自然短宽岩肩。'
}
def evidence(p):
 return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
images=[]
for name,judgment in observations.items():
 p=folder/(name+'.png');images.append({'view':name,**evidence(p),'size_px':list(Image.open(p).size),'directly_viewed':True,'judgment':judgment})
geometry=json.loads((R/'reviews/round-31a-independent-geometry.json').read_text())
runtime=json.loads((R/'reviews/round-31a-runtime-incremental.json').read_text())
actions=[
'从30k原壳替换两新增肩，不继承31a柱体。保留两处短宽凸面打断大坡的定位方向。',
'不要再次使用同XY竖向环加统一内缩帽：顶面改为少量方向明确、非水平的宽斜面，两处方向和高程错开；侧面倾斜且宽根进入旧坡。',
'后端应接入旧主坡并逐段露出，前端短厚偏转，避免一个完整封闭圆帽轮廓在所有前视角都可辨认，也避免重新拉成长楔或尖脊。',
'验证真实上包络仍保持道路、pad和当前树轴支承，同时在近图检查宽根和原坡相接的视觉关系。正体积交集或新外露面积都不能替代该检查。',
'后侧直窄深槽作为独立剩余项保留，不能用正面替换宣称全岛完成；全场照明、云、海岸和其他参考仍不在本轮完成范围。'
]
report={'round':'31a','run_id':run,'visual_verdict':'reject_two_capped_polygonal_shoulders_replace_from30k','full_reference_accepted':False,'all_reference_goal_complete':False,'reference':{**evidence(R/'ref/1342.png'),'directly_viewed_this_review':True},'comparison':{**evidence(R/'captures/validation_runs/lantern-island-30k-r1-20260908T193210Z-09e7ff871c9941519a561b4fede063ee/images/day-c-front.png'),'directly_viewed_this_review':True},'images':images,'actual_improvement':'两肩真实外露并遮断部分原连续大斜板，新增体积不是完全嵌入无贡献；但形态本身失败。','remaining':['重复平顶多边柱/按钮轮廓','近竖直同XY侧壁和均匀收帽','两肩与上台的视觉接续生硬','上台宽灰坡及中央直窄切缝','后侧旧长深槽'],'next_actions':actions,'geometry_evidence':{'path':'reviews/round-31a-independent-geometry.json','passed':geometry['pass'],'main_triangles':geometry['actual_main_triangles'],'added_union_volume_m3':geometry['added_union_volume_m3'],'aggregate_solid_overlap_m3':geometry['aggregate_actual_intersection_volume_with_old_main_m3'],'geometric_upward_exterior_areas_m2':[a['actual_upward_operand_exterior_3d_area_m2'] for a in geometry['additions']],'section_correction':'Exact z4/z6 zero reconstruction superseded by nonvertex levels2.137/4.137/6.137. Original zeros retained as failed reconstruction, not actual empty section. No support rerun.'},'root_runtime_report_read':{'path':'reviews/round-31a-runtime-incremental.json','passed':runtime['passed'],'binding_count':runtime['binding_count'],'placements_each_view':59,'maximum_position_delta_m':max(v['maximum_position_delta_m'] for v in runtime['views']),'maximum_footing_delta_m':max(v['maximum_footing_delta_m'] for v in runtime['views'])},'limits':['直接查看参考和五张原图；未启动GPU或Blender。','像素范围为人工定位区间，不是精确分割或可见面积测量。','几何外露面积不是屏幕可见面积，也不是整块原大斜板的面积。','运行审计由root完成，本次读取报告，不伪称独立复跑。','31a已失败的形态与截面纠正证据保留。']}
(R/'reviews/round-31a-island-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='# 31a 岛体独立造型审查\n\n31a 不接受为造型候选完成。两新增肩实际外露，但近景读成两颗平顶多边柱／按钮。保留短宽凸面打断主坡的定位方向，从30k原壳替换柱形设计；完整参考目标仍为 false。\n\n'
md+='本次直接查看 ref/1342.png、31a 五张原始1672×941图片，以及30k的 day-c-front。运行：`'+run+'`。未启动引擎或 Blender。\n\n'
for name,j in observations.items():md+='## '+name+'\n\n'+j+'\n\n'
md+='## 几何与运行证据的边界\n\n实际主壳2150三角，单连通、闭合；道路、pad、当前14树盘支承和17岩/path保持。两肩 UNION 增量281.650m³，合计旧壳交集381.021m³；向上外露几何面83.374/44.908m²。这证明相交和实际外露，不证明它们在视觉上像自然岩肩。\n\n原 z=4/6 的零截面积来自严格截线函数在顶点高程漏线，已保留为 superseded 并用2.137/4.137/6.137m非顶点截面纠正，没有重跑支承检查。详见 round-31a-independent-geometry.json 和 round-31a-section-correction.py。\n\n已读取 root runtime 增量报告：199绑定匹配、每视角59落点，位置最大差0.00016784667969m、基础样本差0；这些是装配/支承证据，不是造型完成证据。\n\n## 下一稿\n\n'
md+='\n'.join('- '+x for x in actions)+'\n\n人工像素区间只用于定位；本轮不估计全片大斜板面积，不宣称完整行走、全场参考或所有树干底面贴合。\n'
(R/'reviews/round-31a-island-independent-review.md').write_text(md,encoding='utf-8')
print('Wrote 31a MD/JSON with five original-image hashes; visual rejected, full_reference_accepted=false.')
