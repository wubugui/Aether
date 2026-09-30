from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];run='lantern-island-31d-20260908T201625Z-7575af2955e449b1a68d49f13e66c31a';folder=R/'captures/validation_runs'/run/'images'
obs={
'night-reference':'紧凑岛体、原生建筑比例和右侧守塔屋构图保留。本轮背槽修改在固定夜间全景中不可充分判断，不能因远图连贯就接受整个岛。相对1342，岛身仍缺自然错位的宽短岩根层次。',
'day-reference':'全景延续上一稿的体量与布置，前部小块和灰坡仍可辨识。它无法证明背面局部闭合已经产生符合参考的造型。',
'day-d-front':'两前肩与31c一致：短于31b、没有31a平顶帽柱，但呈两块轮廓独立的凸石，后方大灰坡和窄暗接缝保留。背槽改动没有修复前部大面的组织关系。',
'day-d-back':'第三体中段确实比31c厚，部分近塔缝被遮断/连上；然而整体仍读成一条纵向窄长塞条。塔脚下两侧大灰坡几乎围着这条石条展开，侧缘暗缝与海侧直口仍明显，没有形成短宽、前后错位的岩肩组织。局部实际连接成功，整体造型失败。',
'day-c-front':'前两凸块和接缝延续31c的独立凸石感，上台灰坡、左侧大斜面仍显。没有理由因为背面一个局部截面接上就提升前部视觉结论。'
}
def evidence(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
g=json.loads((R/'reviews/round-31d-independent-geometry.json').read_text());rt=json.loads((R/'reviews/round-31d-runtime-incremental.json').read_text());diag=json.loads((R/'reviews/round-31d-back-cleft-diagonal-check.json').read_text())
actions=[
'停止无条件扩大单一填槽凸包。下一轮应同时重排槽两侧原壳大坡面、已加连接体与交界，不能只让中间塞条继续长胖。',
'以已定位31b的309/1467面对应XYZ区域和新体交界为有界起点，在31d实际壳中重新定位。不要套旧面/点索引，也不要将整个北侧一次重塑。',
'将从塔脚贯到水边的纵向面带改成2–3个高度与前后位置错开的短宽连接面；在中段让接缝横向偏转并结束，海侧用较低宽根接续。两边不做相同高程的整齐台阶，不加入细密折扇。',
'把原309/1467附近的长陡面切分后与岩肩共用边界，使局部主坡真的改变；避免保留旧长槽壁、仅用一个凸包遮挡。新的接续应读成主岛岩根，而不是槽中独立贴条或桥板。',
'沿真实扩张pad边界保留原线性支承，道路与当前树支承按实际候选复核；近塔1.3748m旧面距离仅是定位证据，不是许可的改形半径。',
'前部继续保留短肩/错向的方向，但完整前部仍未通过。后续应将凸石后缘和原宽坡共同组织，减少封闭独立轮廓，不能靠加第三第四颗小岩块完成。'
]
report={'round':'31d','run_id':run,'visual_verdict':'reject_overall_rework_adjacent_native_slope_faces_and_seams_instead_of_enlarging_single_filler','visual_complete':False,'full_reference_accepted':False,'all_reference_goal_complete':False,'reference':{**evidence(R/'ref/1342.png'),'directly_viewed_in_current_continuing_review':True},'comparison_images':[evidence(R/'captures/validation_runs/lantern-island-31c-20260908T201128Z-28759710080745f9bea8113b6cf38f92/images'/n) for n in ['day-d-back.png','day-c-front.png']],'comparisons_directly_viewed_in_current_continuing_review':True,'images':[{'view':n,**evidence(folder/(n+'.png')),'directly_viewed':True,'judgment':s} for n,s in obs.items()],'local_improvement':'Back filler is thicker and declared central diagonal gap is truly closed. This does not imply all peripheral/high gaps are closed or the broad rock forms match1342.','next_bounded_remodel_direction':actions,'geometry_evidence':{'report':'reviews/round-31d-independent-geometry.json','base_geometry_and_support_pass':g['base_geometry_and_support_pass'],'bounded_primary_diagonal_bilateral_pass':g['back_cleft_bilateral_connection_pass'],'main_triangles':2184,'first_two_native_operands_exact_from31c':g['first_two_native_operands_exactly_preserved_from31c'],'primary_diagonal_unfilled_gap_m':diag['gaps'][0]['actual_new_unfilled_gap_length_m'],'primary_diagonal_operand_bank_penetration_m':[diag['gaps'][0]['operand_overlap_near_pad_bank_m'],diag['gaps'][0]['operand_overlap_far_bank_m']],'positive_local_Y_crosscuts':5,'total_local_Y_crosscuts':9,'scope':'Previously completed actual checks reused; no geometry rerun. Four outer/high crosscuts retain gaps. Neither5/9 nor diagonal closure is an art score.'},'root_runtime_report_read':{'path':'reviews/round-31d-runtime-incremental.json','passed':rt['passed'],'binding_count':rt['binding_count'],'placements_each_view':59,'maximum_position_delta_m':max(v['maximum_position_delta_m'] for v in rt['views']),'maximum_footing_delta_m':max(v['maximum_footing_delta_m'] for v in rt['views'])},'limits':['No new geometry checks, GPU or Blender run during this visual review.','No whole-crevice closure or full-reference acceptance claimed.','Bounded face reorganization is an authored design direction, not a validated31e candidate.','Runtime evidence read from root rather than independently rerun.']}
(R/'reviews/round-31d-island-independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='# 31d 岛体独立造型审查\n\n整体不接受。背槽局部连接真实改善，但中段仍是纵向窄长塞条；两侧原大坡和外围长缝使参考要求的短宽岩根关系没有成立。下一步应重排相邻原壳大面与岩肩接缝，不继续无条件扩大一个填槽凸包。\n\n本次直接查看五张原图，对照持续审查中直接看过的1342和31c。运行：`'+run+'`。\n\n'
for n,s in obs.items():md+='## '+n+'\n\n'+s+'\n\n'
md+='## 有界原壳重塑方向\n\n'+'\n\n'.join('- '+a for a in actions)+'\n\n## 几何改善与视觉失败分开记录\n\n既有独立证据：2184三角闭合单连通，完整道路/pad/14树盘支承与17岩/path保持，前两操作数与31c逐点相同。在既定斜截z5.137m，原主缝已闭合，低Y/高Y岸分别进入0.791512/1.464791m；局部Y截面5/9有双岸连接，另4个外侧/高位仍有缺口。这里只证明有限真实连接，不意味着全槽或艺术通过。\n\n已读取root审计：199绑定、每视角59落点，最大位置差'+str(report['root_runtime_report_read']['maximum_position_delta_m'])+'m、基础样本最大差'+str(report['root_runtime_report_read']['maximum_footing_delta_m'])+'m。没有重跑已通过几何或引擎，不按新增面积或截面通过比例评分。`full_reference_accepted=false`。\n'
(R/'reviews/round-31d-island-independent-review.md').write_text(md,encoding='utf-8');print('31d review MD/JSON written; local connection retained, overall art rejected.')
