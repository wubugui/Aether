from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'reviews/round-32f-foreground-independent-geometry.json';d=json.loads(p.read_text(encoding='utf-8'));inc=json.loads((R/'reviews/round-32f-incremental.json').read_text(encoding='utf-8'))
d['limits']=[
 'Full actual building bottom triangle unions, full design pads and cap/core interfaces are checked by triangle clipping with1mm tolerance, not nine-point samples.',
 'All8 actual tree-base support results are inherited from32e only after exact comparison of the full old/new mesh-face geometry intersecting each actual pine hexagon XY footprint; no repeat full upper-envelope scan.',
 'Eight independent rocks are geometrically exact. Terrain/core polygon indices and XY coordinates are exact but Z changed. The re-fitted path has126changed vertices and non-identical polygon index lists, so whole-path identity is not claimed.',
 'Pad edge function repair is verified at the prior12largest sampled edge jumps. Regularization and inside snapping imply numerical near-continuity; exact C1 continuity is not claimed.',
 'Actual local steep faces880/884remain unchanged at89.149/85.223degrees. Repairing pad-boundary mixing does not prove all thin groove artifacts are removed. These source faces have not been projected to the reported image pixels.',
 'No whole-island self-intersection, extra GPU, runtime instance/contact or visual acceptance is claimed.'
]
d['incremental_report']='reviews/round-32f-incremental.json'
d['actual_tree_base_report_inherited']='reviews/round-32e-actual-tree-bases.json'
d['all8_actual_tree_bases_supported']=inc['all8_real_tree_bases_support_inherited']
d['all8_actual_tree_bases_flat']=inc['all8_real_tree_bases_support_inherited']
d['all_reference_goal_complete']=False
d['pass']=d['pass'] and inc['all8_real_tree_bases_support_inherited']
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md='''32f 前景 A 的限定结构复核通过；地坪混合跳变已显著修复，但部分真实尖窄面仍存在，不能据此声称画面中的沟面已全部消除。

独立后台重新打开正式 Blender 文件，未保存源、未调用 builder，源 SHA 保持。实际 11 件 GLB 各自闭合、有向边成对且体积为正；各件三角几何集合与本次源重开结果完全一致。完整三座实际建筑底域、整个设计 pad 及这些区域 cap/core 接合全部通过，与32e同样完整覆盖平坦。三建筑底域均未超出设计pad。

增量核验确认八件独立岩石逐点逐面保持。地表与主岩 XY 和原生面索引保持，地表274点、主岩137点仅高程改变，最大位移0.756083 m。贴地路径126点相应改变，最大位移0.756081 m，其 polygon 索引列表不完全相同，故不声称路径逐点逐面不变。

八棵树的计划位置、尺度与32e相同。对每棵实际 pine 最低六边形底域，比较全部11件旧/新网格中与它有实际投影面积交集的每一片面：所有几何集合完全相同。因此继承32e已完整验证的最高上表面连续、平坦、无最高道路命中结果，没有再做一次完整上包络扫描。实际运行中的实例朝向、落地高度及碰撞归属另由runtime记录验证。

旧塔pad边缘 (-3.484789,11.139847) 外0.1 mm处，32e函数相对pad高度为-0.765552895 m；32f同点仅-1.37483×10⁻⁹ m。此前最突出的12个边界样点都按相同位置复查，见增量JSON。新权重趋于很大，修复了有限权重平均与inside直接返回之间的数值跳变；由于分母正则项和inside阈值仍存在，不写成数学上无限权重或严格C1连续。

实际源面880(268,531,545)及884(357,268,545)却完全未变，坡度仍为89.149°和85.223°，投影面积分别仅0.05904和0.01677 m²。面705仍约87.450°。它们证实局部还有极瘦三角跨较大高差，不能把所有尖沟都归因于此次已修复的多pad混合。这里没有将源面回投到指定GPU像素，也没有据此声称穿透、裂缝或完整定位。若实际画面仍出现尖沟，下一步应只定位可见面，再决定补充局部采样或重排瘦面，不扩展整岛扫描。

证据：`round-32f-reopened-source.json`、`round-32f-foreground-independent-geometry.json`、`round-32f-incremental.json`；实际干底继承来源为`round-32e-actual-tree-bases.json`。32e既有最终报告和32d失败记录保持原样。此报告不含GPU或艺术验收，`full_reference_accepted=false`，`all_reference_goal_complete=false`。
'''
(R/'reviews/round-32f-foreground-independent-geometry.md').write_text(md,encoding='utf-8')
print('32f finalized pass=',d['pass'])
