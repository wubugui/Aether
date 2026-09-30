# 36c 完整候选原生保存补充审查

**实际保存的 World36c 有 773 个 Vegetation 组，总数 54797。54800 只对应更早的高岸 adapter 阶段，不能继续作为完整候选回载数量断言。** 本项只读文件/资源，不启动引擎、Blender 或 GPU，不重复地形支承/全世界几何检查；36b 已完成报告保持原样。

## 三个删除的真实资源对应

读取 World36c 每组实际引用的外部 MultiMesh 或嵌入资源，汇总总数；仅对两个受影响组逐行比较变换。实际 36b 原生资源到完整保存 World 的差异为：

| 组 | adapter 资源数量 | 完整 World 数量 | 删除的原索引 | 剩余变换行 |
|---|---:|---:|---|---|
| rock_-4_-4 | 26 | 25 | 5 | 删除对应行后全部 float32 精确一致 |
| oak_-4_-4_CoastalPines36b | 144 | 142 | 9、77 | 删除对应行后全部 float32 精确一致 |

从原资源行和保存组变换计算出的三个世界位置分别为：

- (-2657.116943359375, 17.938129425048828, -2674.6630859375)
- (-2512.6201171875, 47.195526123046875, -2523.573974609375)
- (-2527.592041015625, 45.167118072509766, -2511.77587890625)

均与实际 alongshore-high sidecar 的 harbor_study.stone_paths.vegetation_adjustments 对应；最大数值差约 5×10⁻¹²m。明确属于后续港路避让，不能把这三个删除记为高岸 adapter 丢失实例。总数差正好为 3。

## 保存结构与修改范围

World36c 与旧 World36b 的源/输出 SHA 均符合 repair-report；逐文本应用记录的 14 条外链修复后，与实际新文件完整一致。Game36c 的两条外链及 weather-folder 修复同样完整一致；weather 字段按 TSCN 字符串的反斜线转义处理。没有额外模型或变换修改证据。

World 的直接子节点仍是 Terrain、LandDetails、Settlements、Vegetation、Clouds、FlightRings、Ports、Ocean、Cliffs、Mountains、Routes。没有直接挂在 World 下的临时 StaticBody3D/CollisionShape3D。这里只核持久保存结构，不声称自然启动后的临时碰撞缓存已经实测。

14 个新地形外部场景存在，具有 asset_instance.gd、surface_material、Model、Collision/Shape、layer5/mask2、ConcavePolygonShape3D。22 个新增 pine 组都具有 scatter_group.gd、pine.tscn 的 model_scene、pine 元数据，直接保存在 Vegetation 下。没有把 owner 显式指向 Vegetation 或 Game；当前平面保存声明使用场景根所有权语义。实际实例化 owner 与自然初始化已由下述独立核对的 36g 证据补充；GUI Extract/重存不在已测范围。

## 36g 实际自然回载补充

实际运行 highcoast-reopen36g-20260909T023100Z-805ece112b8a42bcb3639d99f9e39ad6 已终态 passed，exit0，错误日志为 0 字节。独立复算 manifest 全部 **16 项**绑定的 SHA 和字节数，全部对应；World/Game/候选脚本与冻结副本相同，实际命令执行的工作区 check 脚本也与 frozen check.gd 同 SHA。两张 PNG 与 candidate-reopen.json 均有成功清单绑定。本补充不另跑引擎，也不把父代理的图像查看当独立美术验收。

检查脚本在全新 World 实例上断言 208 个 Terrain、14 块的 mesh.get_faces() 与 shape.get_faces() 完整数组相等、每块唯一 Model 和 Collision/Shape、无直接临时根 StaticBody；随后逐组断言 owner==author、scatter_group.gd 和 model_scene 非空。报告中 14 块三角数与此前实际保存碰撞对应；总数 **54797**、22 新 pine 和三个港路删除与本报告静态资源证据一致。

全新 Game 加入 SceneTree，执行正常 _ready，实际 World 初始 processing、chunks>=208、layout.props=54797 断言通过。脚本随后主动冻结 World._process，以限定本轮检查；这不是持续流式生成或后台更新耐久测试。

对 poplar_-2_-3_CoastalPines36b 的 index0 调用 read_selected、apply_selected，实际产生不同 MultiMesh，同时选中变换保持相同。这证明一例无变化读写辅助调用成功，不等于 GUI 按钮交互、Extract、改位重存及再次回载流程全部验证。

现有 test_override_input 驱动物理飞行 **240 帧**，8 个间隔 30 帧样本（0至210）及最终位置被记录；起终点位移独立重算为 **88.955116679m**，与报告 88.955116272m 对应。此数是位移，不是累计路程。起点 (-2280,230,-1910)，终点 (-2366.681152,249.628586,-1906.243774)；全部记录位于高岸编辑区域南界 Z=-2150 之外。因此它验证港湾附近现有控制器启动移动，不是 36b 的 65 点高岸路线或新地形载具走廊。

**bounded fresh reload 现为 true**；整候选完成、完整路线/足迹/走廊与美术接受仍为 false。36b 原失败运行保持失败，36g 是另一轮有界成功回载证据。报告 MD/JSON 已补完并稳定，本审查没有活跃进程。
