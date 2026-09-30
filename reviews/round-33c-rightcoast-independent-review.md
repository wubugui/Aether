# 33c 右岸低湾独立视觉复核

**视觉拒绝33c，不升级；建议33b继续作为未完成底稿。** 新低岸的主图收益有限，近距湾图却增加了显眼的陡长暗切面。此结论不等待几何结果，也不把33b改称整体美术通过。

已直接查看本run五张原图，并与刚审过的33b同机位图及33简报对照：

- [night-reference](../captures/validation_runs/rightcoast-33c-20260908T230636Z-171cc57e608641cfb0e39cbcb89fbcaf/images/night-reference.png)
- [day-reference](../captures/validation_runs/rightcoast-33c-20260908T230636Z-171cc57e608641cfb0e39cbcb89fbcaf/images/day-reference.png)
- [day-coast-front](../captures/validation_runs/rightcoast-33c-20260908T230636Z-171cc57e608641cfb0e39cbcb89fbcaf/images/day-coast-front.png)
- [day-coast-bay](../captures/validation_runs/rightcoast-33c-20260908T230636Z-171cc57e608641cfb0e39cbcb89fbcaf/images/day-coast-bay.png)
- [day-coast-back](../captures/validation_runs/rightcoast-33c-20260908T230636Z-171cc57e608641cfb0e39cbcb89fbcaf/images/day-coast-back.png)

bay图约x940–1008/y260–403出现高而窄的暗切面，其下折到湾底，取代33b较连续的斜坡观感；水线附近约x927–1020/y456–483仅露出很窄的灰色岸唇。尚不能读成可供作业的低地面，也没有清楚的向上短连接。front图左边约x0–115/y230–650的新长暗三角是同类副作用的另一诊断证据。这里描述的是实际陡折外观，不是未经测量就认定非流形、裂缝或浮空。

日夜主图的大构图、屋群和岛体关系基本保持，但低湾改动占幅很小，看不出足以兑现简报的低岸空间。不能因为主图变化有限就说模型没有改变；同样不能因为确实降低了若干顶点，就称低湾目标已达。后续若继续，应从低岸宽度、后坡脚和两侧接续的完整断面重做，不只降低稀疏点而把周边拉成高窄切面。暂以33b接续，保留33c作为失败的艺术尝试。

## 屋旁尖面的来源限定

已直接读取 [33b源面定位](../captures/rightcoast33b-visible-transition-localization.json)。front(884,535)、主图(1375,850)与(1400,868)命中三角的全部顶点相对26b位移均为0；front(843,528)两个顶点不变、第三仅约0.006714m。因此部分屋旁尖面是26b保留形体，不能把所有可见尖折归于33新增高程。33b原报告已保留“旧源可能贡献”的限定，此处补上实证。

front(890,378)源射线命中的是约20.55°后方地面。该工具不含屋、树、铺地和原World遮挡，不能用它给画面暗立片作准确归属，也不能据此说立片坡度仅20.55°。本审查读取现有结果，没有重新发射射线或扩展全区归因。

33c实际manifest和底层渲染为passed；是本次视觉审查拒绝，不应把GPU运行包改写为failed。五图及五sidecar的manifest SHA、run_id已核对，右岸sidecar/冻结/候选GLB一致，BLEND源与冻结一致，五图均production_modified=false。完整增量几何由另一代理审，本文不提前宣布它通过或失败。

未修改源/生产或启动引擎。背图只作真实三维连续性的诊断，不要求无参考背面达到任意艺术精度。A和右岸的大岩面等旧缺项继续保留，全部20参考与原场景目标仍未完成。
