from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-33a-rightcoast-independent-geometry.json';d=json.loads(p.read_text(encoding='utf-8'))
d['actual_support_geometry_preserved']=d['old_actual_surface_over_occupied']['changed_count']==0 and d['new_actual_surface_over_occupied']['changed_count']==0
d['changed_external_faces_intrude_actual_support_domain']=d['new_actual_surface_over_occupied']['changed_count']!=0
d['planned_occupied_domain_complete']=all(x['outside_plan_occupied_area_m2']<1e-8 for x in d['domain_containment'])
d['actual_frozen_face_region_covers_complete_occupied_domain']=all(x['outside_frozen_face_region_area_m2']<1e-8 for x in d['domain_containment'])
d['failure_classification']='Design occupancy mask incomplete due pad yaw sign; actual full projected support geometry nevertheless retained by the larger whole-face freeze. No actual foundation excavation or new support intrusion found.'
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md='''33a实际屋路支承几何保持，但计划占用域方向存在错误，不能将本轮设计约束整体记为通过。

独立重开正式源一次，12件网格闭合、体积为正，源文件未修改。GLB实际16534三角与本次重开源的三角几何集合完全一致。主岸体909点实际改动，最大35.541445m；所有计划冻结点保持，原生面顶点集合保持。用本版实际三角顶点索引对照旧源，未出现非垂直三角XY符号反转；最低正面积比0.115752。这不是全局三维自交不存在的证明。

真正的占用真值来自独立提取的九座完整基础（含门阶梯）及922件实际铺地GLB投影。33a计划中的pad旋转方向与实例不符，导致九屋真实基础均有部分超出occupied_region，其中fore_keeper为13.833962m²、bay_upper为9.852436m²、fore_fisher为3.588055m²。计划占用域不完整，这一失败保留。

然而更大的整面冻结区覆盖了九屋完整真实基础及全部铺地域。逐片裁剪旧/新实际完整三角后，凡与真实屋路域有正面积交集的旧三角均保持原几何；新三角中也没有改动外部面移入该域。这个检查同时包含原有支承保持和外部新侵入，不能用锁点计数替代。只忽略小于等于1e-10m²的数值交片。结论是实际支承几何保持，未发现因本次改形挖坏屋基；并不是计划pad旋转正确。

JSON明确分为actual_support_geometry_preserved=true、planned_occupied_domain_complete=false、actual_frozen_face_region_covers_complete_occupied_domain=true，整体pass_result=false指计划约束错误。下一版直接采用独立真实占用GeoJSON，避免再自行旋转pad或依赖整面冻结的额外覆盖碰巧补偿。

证据为round-33a-reopened-source.json及round-33a-rightcoast-independent-geometry.json。本项没有重复GPU，没有重新全验26b铺地接触/步行或程序化植被；旧屋路下完整面保持允许继承原有限证据，受影响树需按新地表重贴。没有艺术或全参考完成声明。
'''
(R/'reviews/round-33a-rightcoast-independent-geometry.md').write_text(md,encoding='utf-8')
