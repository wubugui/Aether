# 34c 水面独立技术审查

限定技术检查通过：**34b 的固定月光方向/固定角半径问题已修正**。源码 shader SHA256 `444d9e9072ccaa127321716baf683f6c64db1f64000a7611f270a644eb9eede5`，adapter SHA256 `9633ea86ccbdaf3b6b78b6aaf6304c8e1597be972b372d72654fbff021027c0a`，与冻结输入同版。没有启动引擎、Blender、CPU 网格采样或陆地支承扫描。完整结果及复核脚本为同名 JSON/Python。

adapter 在真实月球创建后，把 `moon.global_position` 写入当前水 shader 参数并立即读回断言。夜间记录中心均为 Godot (-3933.2509766,3478.4533691,-9791.3085938)，半径330 m。半径来自已设计的330 m参数，本次没有重新量测月球网格。shader 每水点计算 `to_moon=center-world_point`，再以实际距离生成方向和 `asin(radius/distance)`，因此不再使用34b的参考距离方向近似。

`max(distance,radius+1)` 在距月心331 m内会令所谓方向不再单位化；现Y=0海面至少低于月心3478.453 m，该保护分支不激活，所以不影响本场景的外部球体角域结果。此结论只覆盖月球角域，不证明云遮月、实体遮挡、月面分面颜色或物理反射积分。

## 两条绑定记录不是两个独立材质的证据

四份夜间 sidecar 各有2条相同 `water_reflection_bindings`，都正确指向实际月球，但只有1条 `open_water` 源材质记录：`res://scenes/environment/Ocean.tscn::ShaderMaterial_sqy22`。记录缺少材质 instance_id 和接收节点。

实际 adapter 先处理 `material_override`，随后又处理 `get_active_material(surface)`；`adapted()` 可能先以旧ID缓存新材质，再以新ID缓存同一个新材质。于是 `material_cache.values()` 可包含重复对象，循环生成两条同值记录。**本报告验证2条读回记录，不能据此认证2个不同水材质。** 下次正常运行日志应按 `material.get_instance_id()` 去重、记录接收节点及绑定值；无需仅为计数另跑GPU。

沿该实际源记录确认，海面来自保存的 `scenes/environment/Ocean.tscn`，尺寸100000×100000 m，真实碰撞子节点叫 `SeaCollision`、layer5。此前暖水光intake引用旧 `scripts/open_world.gd::make_ocean()` 的创建代码，尺寸/Y=0结论未变，但旧名“Sea level collision”不是此场景应排除的实际节点。该来源修正在此明确保留。

## 蓝层与天空的边界

蓝色中间反射层使用 .045 rad（2.57831°）宽度的角域高斯肩，峰值由 `radius²/(radius²+width²)` 缩放，再加 .62 系数银色盘芯。数值分母正、反三角输入有clamp，在当前场景未发现新的奇点。它是可调的角响应与近似峰值补偿，不是归一化微表面卷积或由真实月面材质采集的辐亮度；对跨三角法线跳变也没有新增过滤机制。

夜空垂直渐变的颜色、归一高度和指数与实际 `open_sky.gdshader` 一致，月晕系数也一致；但水面月晕用局部有限月球方向，天空月晕仍用固定方向，所以并非完全相同的天空采样。星点没有进入反射，白天天空渐变也仍不同。没有读取实际云、岛、建筑、局部灯发光体或整个天空的反射图像。

共享波场/单元搜索/顶点函数与34b完整保持，岸深颜色泡沫块保持；原本被最终法线覆盖的旧正弦 `NORMAL` 语句已删除。海面真实几何、轮廓和碰撞依然平坦，岸水深仍是屏幕深度反投影方法。

实际运行 `water-34c-20260908T235317Z-847760e1994442d085ed8c6e530e5ce9` 于2026-09-08 23:54:10 UTC终态passed，两阶段exit0、错误日志为空。五份原始 sidecar 的run/shader、逐视图相机、0/0/0/18/0采样时间以及世界/岸体/建筑/命名岸树记录均通过增量核对；16个限定文件绑定一致。白天没有月球绑定记录，符合夜间创建逻辑。陆地完整支承继承33f，未重复测量。

`bounded_technical_checks_passed=true`；`distinct_material_instances_proven=false`；`full_reference_accepted=false`；`all_reference_goal_complete=false`。本报告不作直接审图或美术接受。
