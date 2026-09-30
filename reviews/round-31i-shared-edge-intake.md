# 31i 真实共享边与支承预审

只分析31h原生两肩目标面及完整边邻面/端点一环；使用31h实际运行14树轴变换原生六边形干底，旧2m盘未冻结。

## 目标面2142

- 边[1108, 1104]，相邻面[2141, 2142]，其他共边。
- 边[1104, 1106]，相邻面[2142, 2143]，拟split边。
- 边[1106, 1108]，相邻面[2136, 2142]，拟split边。

完整边邻面：[2136, 2141, 2142, 2143]；各实际坐标、面积、支承相交和净距在JSON。

## 目标面2158

- 边[1109, 1107]，相邻面[2158, 2159]，拟split边。
- 边[1107, 1105]，相邻面[2158, 2168]，拟split边。
- 边[1105, 1109]，相邻面[2157, 2158]，其他共边。

完整边邻面：[2157, 2158, 2159, 2168]；各实际坐标、面积、支承相交和净距在JSON。

## 正确切分边界

- Use one BMesh edge_split on the shared edge so both incident faces use exactly the same inserted vertex; face_split only after both original edge splits exist.

- 2142 cut creates one quad and one triangle locally; its neighbors acquire the same boundary points. Their final tessellation may change even if the new point stays on the old edge. Record and check that entire changed set.

- If the split point is displaced out of the old edge to create shoulder thickness, both incident faces change shape. Treat the opposite neighbor as part of the authored patch; do not preserve its old triangle while moving only target geometry.

- Keep retained occupied upper support linear patches or explicitly repartition their boundary; exact31i candidate support remains necessary even though this bounded one-ring intake has no occupied intersections.

- Quads with four authored noncoplanar vertices need explicit intended diagonal or actual exported tessellation review, not a claim that quad existence proves broad shoulder shape.

- Shared edge checks use actual31h source indices; after BMesh split/reindex match coordinates or lineage, not stale numbers.

- East split-edge choice in this intake is provisional; actual parent plan takes precedence.

当前只作拓扑预审，不能把未碰支承的一环当作任意移动许可。31i实际GLB仍需闭合、支承、离散相交与视觉审查。
