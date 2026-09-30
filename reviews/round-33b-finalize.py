from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-33b-rightcoast-independent-geometry.json';d=json.loads(p.read_text(encoding='utf-8'))
d['planned_occupied_domain_complete']=all(x['outside_plan_occupied_area_m2']<1e-8 for x in d['domain_containment'])
d['explicit_frozen_face_region_covers_complete_occupied_domain']=all(x['outside_frozen_face_region_area_m2']<1e-8 for x in d['domain_containment'])
d['explicit_frozen_region_missing_area_is_not_actual_changed_ground']=True
d['pass_result']=d['actual_support_geometry_preserved'] and d['planned_occupied_domain_complete'] and d['native_closed_positive_pass'] and not d['xy_orientation_reversals'] and d['identity']['actual_glb_vs_reopened_source_missing_triangles']==0 and d['identity']['actual_glb_vs_reopened_source_extra_triangles']==0 and all(r['frozen_vertex_max_displacement_m']==0 and r['polygon_vertex_sets_preserved'] for r in d['object_increments'])
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md='''33b限定实际支承复核通过。真实占用域方向已改正，九屋完整基础及922铺地均包含于本版occupied_region；实际旧支承面保持，也未发现改动外部面移入占用域。

独立只读重开正式源一次，12件闭合且体积为正，未保存或修改源。实际GLB16534三角与本次重开源三角几何集合完全相同。所有计划锁定点保持，原生面顶点集合不变；本版实际三角与旧源同索引三点比较，XY无符号反转。各件包括低岸岩脚的最低正面积比为0.080562；不能将此投影门禁写成全局三维自交证明。

完整旧主上表面在真实屋路域覆盖约899.210279m²，高程6.420538–15.620000m。只存在约6.09×10⁻¹⁰m²的数值未覆盖和5.55×10⁻⁸m²三角叠片误差。全部与真实域有面积交集的旧面均保持；新面检查中也没有发生几何变化的交片，因此无需把埋底变化假设成支承问题。原水上向上支承保持、外部面新侵入及改变的垂直线投影均独立检查，后两项没有反例。

必须保留一项描述限制：显式frozen_face_region未覆盖前景铺地域0.211736840m²、海湾铺地域0.009946560m²，以及bay_upper约1.14×10⁻⁸m²数值小片。准备脚本以原面前三点叉积和面积阈值筛选显式冻结面，另有8m不变缓冲；实际这些漏片所在三角依然完全保持。故报告记planned_occupied_domain_complete=true、actual_support_geometry_preserved=true，而explicit_frozen_face_region_covers_complete_occupied_domain=false，不以支承通过掩盖显式冻结域并非全覆盖。

JSON和实际重开证据分别是round-33b-rightcoast-independent-geometry.json、round-33b-reopened-source.json。本报告没有重复GPU、全世界扫描、完整步行或程序化植被验证。28个命名树根允许重贴，其他散布植被的全XYZ记录缺口仍在占用报告中明确。33a错误计划及其实际支承保持结论未改写；艺术与全参考完成仍为false。
'''
(R/'reviews/round-33b-rightcoast-independent-geometry.md').write_text(md,encoding='utf-8')
