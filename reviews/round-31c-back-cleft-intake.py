from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-31b-back-cleft-independent.json';r=json.loads(p.read_text(encoding='utf-8-sig'))
notes=[
'31c源是30k：31b面309/1454/1467及点939索引只作定位证据，不直接用作30k索引；应按实际XYZ/三角匹配确认源壳。',
'已测近塔槽壁本身与道路/pad/14树盘没有投影接触，但面1467距pad仅1.374832m。此距离不是可用的填补半径；新实体全部向上表面的XY域和线性高度必须按实际pad边界重查。',
'关键高点(-1.387008,5.015520,11.690657)接近塔基高程。填补应针对槽中段，勿将整个高点拉低、向塔方向扩展高屋顶，或把连到pad边的共享三角一起抬动。保存原支承面优于冻结不相交大面。',
'与旧壳有正交集、主壳单连通并不能证明两侧都接上：一个操作数可能只吃进左壁，右侧仍留长细裂缝。用几个避开源顶点高程的有限截面分别确认两侧接触，再从D背图检查是否留有不合理夹缝。',
'短宽连接体也可能呈一条横跨槽的桥板或规则堵头。让一侧较高较后、另一侧较低较前，以非水平宽面和钝折前端接续，保留有方向变化的局部凹口；不要把整条深槽全部填成平直坡。',
'背面现有塔脚到水线的大片灰坡仍需层次。填补若仅把两侧拼成更大同向面，虽消除了贯通黑线，仍是造型失败；新外露面积或交叠体积大小不作接受指标。',
'31c五图应区分两前肩和背槽：C前视两顶面应缩短且错向，D背视应消除直长切口而不出现横板。保留紧凑岛/原生建筑比例、当前树组，不用远夜图代替近图。'
]
report={'round':'31c','scope':'Bounded design intake from independently verified31b rear-cleft source and current occupied boundaries. No31c artifact acceptance; no Blender/GPU or full support rerun.','source_report':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'near_pad_sample_face_minimum_gap_m':min(x['protection_relations']['expanded_pads']['face_horizontal_distance_m'] for x in r['samples']),'key_high_point_blender_xyz':[-1.3870079517364502,5.015520095825195,11.690656661987305],'design_risks_and_constraints':notes,'current14tree_disks_status':'Current measurement envelope only; not permanent user prohibition on moving/re-grounding trees.31c intention is to keep them, so verify exact current envelope in actual candidate.','candidate_geometry_pending':True,'candidate_visual_pending':True,'full_reference_accepted':False}
(R/'reviews/round-31c-back-cleft-intake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'reviews/round-31c-back-cleft-intake.md').write_text('# 31c 背槽连接体独立设计风险\n\n本报告基于已独立核验的31b背槽三源面和当前占用区，尚未接收31c正式候选，不是几何放行。\n\n'+'\n\n'.join('- '+n for n in notes)+'\n\n当前2m树盘是检查范围，不是用户永久硬约束；本稿既然计划保持当前树组，就应按真实候选复核。未运行Blender、GPU或全支承检查。\n',encoding='utf-8')
print('31c bounded intake written; actual candidate remains pending.')
