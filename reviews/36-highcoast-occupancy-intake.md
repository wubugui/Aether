# 36 高海岸：实际保存占用与局部同步入口

**候选域没有保存的道路、田地、建筑或地标模型进入，但有 2,580 个实际散布轴心，需要随最终局部地形处理。** 这不是空域许可或新支承通过，最终编辑范围尚须对这些索引精确筛选。

坐标为 Godot 世界 XYZ、Y 向上。初始候选为 X[-2600,-900]、Z[-4400,-2150]；根从真实保存地形确认海岸更偏西后，只把西界扩至 **X=-3750**，增加 Ground_-5_-6/-5/-4/-3，来源从 12 块扩为 16 块。东、南北界不变。扩界地形依据是根的 `reviews/36-terrain-savedmesh-intake.json` 和保存 npz，本审查不重复 Blender 读取。33f 港村最北 Z=-2050，仍在区域外，保持不动。

World.tscn SHA 为 `6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8`，与根 intake 一致。本次仅写本报告、同名 JSON 和有限 Python 提取脚本，没有生产编辑、引擎、Blender、GPU、物理查询或整体生成。

## 保存道路、田地、建筑及地标

直接解析 World 保存节点的 ExtResource 和 Transform3D，递归读取实际 prefab/model 变换，再用真实 GLB 三角投影与矩形比较，检查了：

| 保存类别 | 节点数 | 进入最终候选矩形的模型投影 |
|---|---:|---:|
| LandDetails（12 Field + 3 Trail） | 15 | 0 |
| Settlements（含 rotor 等保存实例） | 172 | 0 |
| Cliffs | 7 | 0 |
| Mountains | 11 | 0 |

这里没有用节点原点代替模型范围：LandDetails 的世界坐标可能直接烘焙在 GLB 顶点，已按实际模型检查。最近的保存建筑为 `Settlements/cottage_57227`，整个模型 AABB 最北 Z≈-2109.4418，与本矩形南界相距 **40.5582m**，仍在外侧。JSON 保留所有被排除模型的实际世界 bounds 与距候选域距离，便于以后局部扩大时复查。

`World/Routes` 中 3 个实际 Path3D/Curve3D 也在外侧。检查使用所有真实 Bezier 锚点及入/出 handles 构成的保守包络，加保存宽度半径：Crownreach 15 点/宽2.4m；Amberfield 6点/宽2m；HillHamlet 3点/宽1.35m。它们的控制包络都不碰本域，故无需新道路重贴。6 个保存 Ports marker 原点也全部在外侧。

历史 `assets/land_detail_authoring.json` 仍包含当前 World 未引用的旧 `Roads` 条目，不能拿它替代当前 LandDetails 装配真值。需未来导出时，入口是 `tools/export_land_detail_layout.gd` 的实际保存节点遍历；本轮不运行它。

## 实际散布资源与索引

World/Vegetation 主要按 **kind + 768m chunk** 分组；World 保存 grove 变换，实际 MultiMesh 指向 `assets/scatter/Grounded_<kind>_<cx>_<cz>.res` 等资源，内部 mesh 另引用 `assets/meshes/<kind>.res`。当前精确实例位置属于这些保存资源，`world_layout.props` 不是当前实际落点真值。

本审查不借助 Godot 加载，直接解析实际未压缩 RSRC v4.5/format6 的命名属性表、外部 mesh 路径、instance_count 和每实例 12-float、3×4 行序 buffer；断言终止标记、格式、有限值、非零 basis 行列式。world transform = grove world transform × instance resource transform。资源和变换均记录在 JSON 中。

- 16 个候选块内有 55 个保存 chunk 组；另读取 14 个非 chunk 作者组，共 69 组、3,579 个实际实例。
- 14 个作者组共 208 实例，全部在区域外；不是按它们的名字推断位置。
- 49 个组有轴心进入矩形，合计 **2,580**：oak 1,353；poplar 652；bush 199；rock 376；pine 0。
- 初始矩形内为 1,731 个；仅西侧扩界增加 849 个。
- Ground_-5_-4 和 Ground_-5_-3 没有保存 Vegetation 组，不虚构空组资源；四个实际保存的零实例组也保留 count=0。

| Chunk | 资源内全部实例 | 本矩形内实际轴心 |
|---|---:|---:|
| -5,-6 | 309 | 163 |
| -5,-5 | 81 | 81 |
| -5,-4 / -5,-3 | 0 | 0 |
| -4,-6 | 335 | 315 |
| -4,-5 | 511 | 511 |
| -4,-4 | 246 | 246 |
| -4,-3 | 1 | 1 |
| -3,-6 | 121 | 102 |
| -3,-5 | 407 | 407 |
| -3,-4 | 176 | 176 |
| -3,-3 | 238 | 19 |
| -2,-6 | 467 | 286 |
| -2,-5 | 250 | 197 |
| -2,-4 | 70 | 59 |
| -2,-3 | 159 | 17 |

每组 JSON 含真实 `multimesh_resource`、SHA、`actual_referenced_arraymesh`、`model_scene`、grove 世界变换、完整 count、实际域内 `index/world_origin/world_basis_rows`。这可直接提供最终选区的稳定输入，不应重新生成全部实例。

另用对应当前 prefab GLB 计算了 **2,585 个代理 AABB 交域候选**，比实际轴心多 5 个边界实例：oak_-5_-6 索引3/32/139、oak_-2_-6 索引84、oak_-2_-5 索引32。这些是边界复查候选，**不是已测得真实树根域**。本审查未解码 `assets/meshes/*.res` 的 ArrayMesh 顶点并证明它与 prefab GLB 完全等价，因此不把该代理界称为实际所有树冠/基部的完备相交证明。精确轴心/变换与代理几何在 JSON 分开记录。

## 局部改形的明确同步入口

1. **确定实际改形面域后按 index 筛选。** 不要对整个 768m 块内所有实例统一升降。保留每个原 basis；按改形后实际最高可支承面重贴或明确重布，记录 old/new origin、最终命中来源、改动原因。轴心附近的真实树干底部/岩底支承由最终候选检查，不能只用当前轴心计数通过。
2. **只复制和保存受影响 MultiMesh。** `scripts/scatter_group.gd:12 copy_data()` 显式先分配 instance_count 再复制变换；`apply_selected()` 是编辑入口。世界变换必须用 grove 的 affine inverse 转回资源局部，不能把 world origin 直接写入 buffer。保留 colors/custom data 的机制，不盲用 `MultiMesh.duplicate()`。
3. **现有局部落地逻辑可参考，阈值不能照搬。** `tools/cliff_refresh.gd:74 reseat_grove()` 按改动域筛实例，已有碰撞层4、射线Y2200→-100和删除逻辑。其水面<0.6、normal.y<0.60，以及北部树木Y>170删除，是现有作者假设，不能当用户约束，否则新高海岸可能整片删树。需要按新地形风格和实际支承改为明确的局部决定。
4. **保存绑定与运行碰撞一起接续。** `tools/install_cliff_kit.gd:115–124` 展示保存 changed grove 的实际 `.res`、更新其 World 绑定的方式；仅参考局部步骤，不运行整个 kit。`scripts/open_world.gd:64` 从保存的全部真实 grove transforms 重建 `layout.props`、`prop_transforms` 和 prop_buckets；这是重新装载后的实际碰撞入口。只改 world_layout 的旧 props 不会改变这些保存实例。

地形本身的新模型、碰撞和块边界同步仍由根负责。本报告只界定实际现有占用，未认可新地形造型或执行新支承测试；原 33f 港村及其它区域保持。文件完成并稳定，无本审查启动的活进程。
