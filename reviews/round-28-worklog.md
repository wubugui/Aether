# 28：灯塔暖光和真实空间光束

范围保持全部20参考及原开场。当前处理1342夜间海岸的灯塔光束；26b道路/岸体、27d云和27f水保持原候选，生产未安装本轮资产。

## 原生实体与28a/b结果

`blender/model_lantern_volumes_28a.py` 制作独立闭合560m光学锥台与半径1.45m灯晕控制体；源位于 `captures/lantern_volume_assets_28a/`，保存可编辑BLEND和GLB。实际重开检查 `round-28a-lantern-native-check.json` 已通过。19h灯塔主体未改。

28a五实际GPU图 run `lantern-lighting-28a-20260908T155358Z-3417ba65aa8a47ad8c3d4faa1969df63`，28b五图 run `lantern-lighting-28b-20260908T155820Z-3e43e974e919427cabd2e867be27facf` 均terminal passed；各196绑定文件经根SHA检查。28a独立审查只保留灯芯/琥珀玻璃暖光，光束不可读，整体打回。28b只关闭光束背面的硬件深度测试，图中仍不明显，不能将其宣称为根因修复。

四盏灯采用固定世界位置/方向，实际Spot/Omni接收面光，32步视线密度积分和33×33灯位碰撞射线图。自身灯塔碰撞排除以允许光学外壳透光；静态有限角采样不能证明薄物精确遮挡或完整动画。灯芯、玻璃和透镜的实际材质参数有侧车记录。

## 28c/d诊断与确定原因

28c run `lantern-diagnostic-28c-20260908T160251Z-c743ec0d33cd491f939180c70c5dd7bf` 已正常结束。原本期望显示体积、射线区间与密度的4张EMISSION调试图均无明显彩色场；独立解码发现仅少量下半图像素变化，不把“看不明显”说成PNG完全一致。

`captures/inspect_lantern_runtime_28d.gd` 实际导入两个GLB，确认每个Node3D根各有一个MeshInstance3D子节点、一张表面；锥台范围x/y±51.2、z[-560,0]，可见。无导入轴错误或根网格漏遍历证据。

28d run `lantern-diagnostic-28d-20260908T161054Z-dc3055c6b50e4023ac0899b86acd1cd3` 已terminal passed，同一真实场景分别输出EMISSION诊断1、ALBEDO诊断5和正常0。实际8个光束/灯晕覆盖材质数量断言通过，均visible=true、layer=1。诊断5中四个大橙色锥台清晰可见；该诊断故意不作深度/密度裁切，不能当作美术图。

确定根因是 `unshaded` 模式下把可见颜色仅写入EMISSION，ALBEDO为0。Godot4.5 Compatibility的实际无光照输出使用ALBEDO，EMISSION在有光照分支才叠加；独立核对源位于 https://raw.githubusercontent.com/godotengine/godot/4.5/drivers/gles3/shaders/scene.glsl 。官方说明 https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html 。因此此前正常和EMISSION调试体积输出黑色加法RGB，密度亮度调整不能解决该根因。

## 28e修正

`captures/lantern_volume_28e.gdshader` 将无光照最终颜色改为 `ALBEDO=warm_color*light_energy`。保留原生控制体、密度、空间变换、手动场景深度裁切、静态遮挡；`captures/lantern_lighting_28e.gd` 新增每个控制体实际绑定网格/表面/可见性/颜色能量/着色器SHA记录和数量断言。

五GPU运行 `lantern-lighting-28e-20260908T161327Z-30f38fcb128c469db1a26b76deef33dd` 已terminal passed、进程结束。根和独立均直接看完全部五PNG，根核对196绑定SHA；见 `round-28e-root-evidence.json` 与 `round-28e-lantern-independent-review.md/json`。光束实际出现，灯室近景可保留；远端橙色光带/雾团过亮，近灯光束偏弱，视觉仍打回。

## 28f有限锥体积分与衰减

`captures/lantern_volume_28f.gdshader` 在AABB区间内进一步求有限锥台/球的真实进入与退出距离，32步只采实际体积。求交先把原点移至AABB进入位置，避免远距离细锥尖的判别式大数相减。密度由常量改为 `.065/radius * exp(-along/260)`，补偿扩张后的横截面光程并逐渐衰减。这是有记录的美术散射近似，不是校准过的物理大气。

独立CPU检查12,030条射线：未重定位版本最大区间长度误差0.994m、516条超过5cm；重定位后最大0.02544m、无超过5cm误差，且无超过1mm的命中分类差异。报告 `round-28f-independent-interval-check.json` 保留前后shader身份；这不是GPU图像、薄物遮挡或全宽飞行通过证据。

28f五GPU运行 `lantern-lighting-28f-20260908T162319Z-487bb5915c3e40169b6ec7339610e55e` 已terminal passed，根会话44980正常结束。根和独立直接看完全部五图，196绑定SHA匹配，报告 `round-28f-root-evidence.json` 与 `round-28f-lantern-independent-review.md/json`。远端大橙色雾团消除、近源连续性改善，保留这个方向；整体光束仍偏弱，完整美术未接受。原生模型与26b/27几何不变。

## 28g灯芯遮光与束光强度分开对照

实际19h不透明 `Lamp core` 位于光源中心，可能遮住原生Omni/Spot出射；该现象与无光照体积材质的亮度是不同问题。`tools/diagnose_lantern_receivers_28g.py` 用一次真实场景载入，分别捕获baseline28f、仅四灯芯关闭投影、再将体积光能量0.65→1.3三个状态，每个状态都有参考/灯室近景/光束侧景。保留实际灯源是否位于灯芯AABB、投影枚举、能量和每张图的相机侧车。

run `lantern-receiver-28g-20260908T162958Z-96465cbb463e4092a4227359c38c71f4` 已terminal passed，根会话81397结束，195绑定SHA匹配。根直接看了6张变化后的PNG，另3张baseline解码与已看过的28f图比较；独立审查和精确ROI数据见 `round-28g-lantern-independent-review.md/json`，根证据 `round-28g-root-evidence.json`。

**对照不支持灯芯遮光是暖接收面偏弱的原因。** 灯室玻璃、栏台、屋顶、塔身主要ROI在core-OFF与baseline间逐像素相同，整图仅少量稀疏差异；不把这个负结果包装为修复。独立体积光能量加倍则产生明确大范围可读光束变化；这是另一项独立参数变化。完整参考仍不接受。

## 28h本轮最终保留候选

`captures/lantern_lighting_28h.gd` 仅在28f基础上把光束能量0.65改为1.3，灯晕仍1.7；保留原四灯芯投影，未采用未经支持的core-OFF。使用原 `captures/lantern_volume_28f.gdshader` 和28a Blender控制体。

一次实际场景载入的三个最终GPU视角 run `lantern-lighting-28h-20260908T163354Z-e69c09f62fc547389d39adbbd0011225` 已terminal passed，根会话5412结束。根/独立直接查看参考、灯室近景、光束侧景三张原图，侧车确认四灯芯投影均1、四束能量均1.3。限定支持保留光束颜色输出/有限体积积分/衰减/强度修正，远端橙色雾团未恢复；灯源焦点、暖接收面/水面与整体参考仍不足。报告 `round-28h-lantern-independent-review.md/json`；根冻结验证和最新1342登记由 `captures/checkpoint_lantern_28h.py` 写入。

最终28h未重拍更高光束强度下的背面和白昼；28f已有对应五视角证据，不能冒称其为28h同参数全部视角通过。动态光束/精细遮挡、移动飞行、天气仍未验证。所有本轮原生/引擎进程均已结束，不因旧状态文件或锁存在重启；不改生产，不重跑整体生成器，不覆盖手工权威岩体。

仍需处理光束实际衰减和遮挡、灯周围暖光与水面响应；云层形状、水面重复横纹、规则岛岩和空裸主岸、聚落工作区仍明显不符。连续飞行、动态天气和其他参考范围都保持未完成，总Goal active。
