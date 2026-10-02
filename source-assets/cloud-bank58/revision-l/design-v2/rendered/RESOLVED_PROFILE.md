# 机器定义生成的修订剖面记录

仅离线设计一致性；不是实体、接缝或原生验收。

权威定义 SHA256：`4d6e3c1126569e5cb9a9a28204ee04ad467edef7c9e10482e617ca126b4dfc30`

## 三项修正

- A冠点：[4140.0, 1005.0, 3910.0]；near t=0顶高 1005m
- near t=225：顶 780m、底 625m、厚 155m
- 主/支谷共同节点 V2：[4480.0, 740.0, 4070.0]（XYZ顺序）；两条路径引用同一节点

## 全段有限空间门与分段多项式极值

- near_A：465个≤1m参数区间，414个按内域守门；守门区间最小厚 155.000000m，腹面范围 [560.0, 625.0]m；明确边缘豁免范围 [[-240.0, -189.0]]
- D_A_valley_B：1161个≤1m参数区间，1161个按内域守门；守门区间最小厚 160.000000m，腹面范围 [565.0, 625.0]m；明确边缘豁免范围 []

Two explicitly located 1D sections plus the shared junction. Whole-interval numerical extrema of the piecewise-cubic top-minus-bottom and bottom curves. Spatial classification uses <=1m section-parameter intervals, actual world-motion radii and conservative bounds relative to the finite 5m external-empty-cell surrogate. Near direction is the inherited rounded, almost-unit vector, so a 1m parameter interval is about 1.0000242m in XZ; central uses true polyline arc length. Filled 20 internal cells cannot grant outer-edge exemptions. No directed-rounding proof, analytic true mesh distance, 2D/3D candidate, contact, self-occlusion, native or pixel proof.

内域分类仅依据归档5m掩码；内存填20个内部空格以识别外缘。外缘距离与多项式连续极值不是实际新三维网格证明。

## 位于剖面上的权威节点

- near_A / A：弧距 0.000000000m，XYZ=[4140.0, 1005.0, 3910.0]
- D_A_valley_B / D：弧距 0.000000000m，XYZ=[4470.0, 845.0, 3690.0]
- D_A_valley_B / A：弧距 396.610640301m，XYZ=[4140.0, 1005.0, 3910.0]
- D_A_valley_B / V1：弧距 659.669569060m，XYZ=[4180.0, 755.0, 4170.0]
- D_A_valley_B / B：弧距 1004.053076215m，XYZ=[4330.0, 1040.0, 4480.0]
- D_A_valley_B / B_exit：弧距 1147.231286848m，XYZ=[4390.0, 835.0, 4610.0]
