from pathlib import Path
import hashlib,json
from PIL import Image
R=Path(__file__).resolve().parents[1]
run='lantern-island-31b-20260908T195540Z-dc0f57e0a037461484c11dba7dcb8b57'
folder=R/'captures/validation_runs'/run/'images'
obs={
'night-reference':'新增形态在中景夜图中较弱，中央塔/右侧屋、较低树组与紧凑岛体比例保留。前沿分面存在，但上台到水线的岩块层次仍不如1342自然，不能用夜间低可见度隐藏近图问题。',
'day-reference':'岛身轮廓仍紧凑，没有恢复高圆台；新增肩在这个尺度上融入灰色岩群。全景未提供足够证据区分短肩与斜板，评价必须结合三个近视图。',
'day-d-front':'31a闭合多边帽面和同XY竖壁明显消除。左大肩呈偏斜的宽根块石，中肩不再是小按钮，与主坡的承接比31a自然。仍可读出两块独立轮廓感很强的凸包；后接处直暗缝、上台整块灰坡仍在，未形成参考里多方向错位的岩面组织。',
'day-d-back':'后侧长直深槽与大面积整灰坡未被本轮处理，槽从塔基附近贯向水边，侧壁仍像直切面。本视角不能因正面按钮消除而被标记为改形完成。',
'day-c-front':'两颗平顶按钮确实消除，但左肩约x560–690/y490–588读成一张偏长的宽斜面，中肩约x716–812/y522–618也是同向斜板；两个后接位置留有窄直暗缝。比31a自然且宽根有厚度，没有29c极长尖楔的程度；相对30k也确实产生凸肩，不只是原灰坡换色。可是连续面纵深与走向仍相似，参考里的短宽钝折、前后错位尚不足。'
}
def file(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
images=[{'view':n,**file(folder/(n+'.png')),'size_px':list(Image.open(folder/(n+'.png')).size),'directly_viewed':True,'judgment':s} for n,s in obs.items()]
g=json.loads((R/'reviews/round-31b-independent-geometry.json').read_text());rt=json.loads((R/'reviews/round-31b-runtime-incremental.json').read_text())
actions=[
'保留31b取消平顶柱、宽根倾斜及真实主壳连接的方向，作为继续修改的候选；整体仍不接受。不要重新叠加31a两柱。',
'缩短左肩可见连续顶面的纵深，在海侧形成短厚、偏转的钝折前端；中肩改变平面走向与前后位置，避免两块并排同向坡板。应修改少量真实宽面关系，不增加密集小面或整圈碎岩。',
'保留根部厚度，检查肩后缘和旧坡交接暗缝，不把后端无限抬高或向塔基延长；那会重新形成长楔/支撑斜板。',
'分开处理后侧旧长直深槽：依据该视角的实际源三角与占用关系重新设计短、偏转、有落差的沟谷或凸肩，不能从正面无关区域推断后侧已好。',
'下一稿仍需实际GLB支承和同机位近图；新增外露面积、相交体积或19件总数均不是美术优化指标。'
]
report={'round':'31b','run_id':run,'visual_verdict':'retain_oblique_broad_root_direction_rework_long_parallel_top_faces_and_rear_cleft','candidate_retained_for_iteration':True,'visual_complete':False,'full_reference_accepted':False,'all_reference_goal_complete':False,'reference':{**file(R/'ref/1342.png'),'directly_viewed_in_current_continuing_review':True},'comparison_images':[file(R/'captures/validation_runs'/rr/'images/day-c-front.png') for rr in ['lantern-island-31a-20260908T194852Z-ac4f6f47286b4774afd18b8206e9f9ca','lantern-island-30k-r1-20260908T193210Z-09e7ff871c9941519a561b4fede063ee']],'comparisons_directly_viewed_in_current_continuing_review':True,'images':images,'improvements':['31a两个规则平顶帽柱消除','宽根和倾斜侧面使凸肩较自然地接入主壳','相对30k有真实凸肩，部分大斜板被打断','未形成29c那样极长尖薄楔'],'remaining':['C前视两顶面偏长且方向相近','肩后缘窄直暗缝','上台宽灰坡','后侧长直深槽'],'next_actions':actions,'geometry_evidence':{'path':'reviews/round-31b-independent-geometry.json','passed':g['pass'],'main_triangles':g['actual_main_triangles'],'union_volume_gain_m3':g['added_union_volume_m3'],'upward_geometric_exterior_area_m2':[a['actual_upward_operand_exterior_3d_area_m2'] for a in g['additions']],'road_pad_current14tree_supports_preserved':all(s['pass'] for s in g['required_supports']),'nonvertex_section_levels_m':[2.137,4.137,6.137]},'root_runtime_report_read':{'path':'reviews/round-31b-runtime-incremental.json','passed':rt['passed'],'binding_count':rt['binding_count'],'placements_each_view':59,'maximum_position_delta_m':max(v['maximum_position_delta_m'] for v in rt['views']),'maximum_footing_delta_m':max(v['maximum_footing_delta_m'] for v in rt['views'])},'limits':['No GPU or Blender rerun by independent reviewer.','Manual pixel ranges only; not segmentation or exposed screen area.','Geometric plane area does not measure all former slab area or artistic quality.','Root runtime audit was read rather than independently rerun.','No whole walking, complete tree-base contact, or full-reference completion claim.']}
(R/'reviews/round-31b-island-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='# 31b 岛体独立造型审查\n\n保留31b的斜根和取消帽柱方向继续修改，整体不接受。两颗平顶按钮已消除，但C前视的两块连续顶面仍偏长且方向相近；背面旧长直深槽未变。\n\n本次直接查看五张1672×941原图；对照同一持续审查中直接查看的31a、30k前视及ref/1342.png。运行：`'+run+'`。未重跑引擎或Blender。\n\n'
for name,s in obs.items():md+='## '+name+'\n\n'+s+'\n\n'
md+='## 保留范围与下一步\n\n'+'\n'.join('- '+s for s in actions)+'\n\n'
md+='## 证据边界\n\n实际GLB独立检查：主壳2156三角、闭合单连通，完整道路/pad/当前14树盘支承保持，17岩/path不变。实际外壳体积增量332.706m³、向上外露几何面积168.648/105.743m²。这些只证明实际模型与连接，不能作为视觉评分。截面使用2.137/4.137/6.137m非顶点高度，未出现31a旧严格跨面算法的零截面误读。\n\n已读取root运行审计：199绑定匹配、每视角59落点，最大位置差'+str(report['root_runtime_report_read']['maximum_position_delta_m'])+'m，最大基础样本差'+str(report['root_runtime_report_read']['maximum_footing_delta_m'])+'m。未将这份审计伪称独立复跑。\n\n像素范围是人工定位，不是精确面积分割；不宣称完整行走、所有树干底面贴合或全参考完成。`full_reference_accepted=false`。\n'
(R/'reviews/round-31b-island-independent-review.md').write_text(md,encoding='utf-8')
print('31b MD/JSON written: five views reviewed; direction retained; visual/full-reference false.')
