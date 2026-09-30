# 21b 环境独立审查

**夜景仍打回；稀疏星域、真实分面月体可保留，云层仅作形体草稿。** 三张实际图已经直接查看，未运行引擎/Blender、未改生产。

- [day-reference](E:/FeiTing/captures/validation_runs/coast-environment-21b-20260908T101600Z-709d602169834795a1574acc1bacafd1/images/day-reference.png)：新增横向云块打破此前天空过空，但多数接近薄平台、相似水平排列；右边界两层尖长片被截断。保留宽面云的方向，下一步调整厚度、不同高度/前后错位及边缘衰减形体，不宜堆相同层片。岛岸旧问题不变。
- [night-reference](E:/FeiTing/captures/validation_runs/coast-environment-21b-20260908T101600Z-709d602169834795a1574acc1bacafd1/images/night-reference.png)：21a方格噪点月面已经解除，月球有清楚三角分面，星点明显稀疏，这是有效进展。月面仍略呈重复菱面纹理，但已适合作后续低多边形月体基底。前景塔/屋继续明显过黑，只剩侧边蓝光和暖窗；远处shader大陆比PBR前景更亮，画面层级不合理。水光由等距长条变成许多相似斜菱碎斑，仍像规则网纹，并且亮区抢走了前景建筑注意力。云夜间读为宽暗片，明暗层次不足。
- [night-back](E:/FeiTing/captures/validation_runs/coast-environment-21b-20260908T101600Z-709d602169834795a1574acc1bacafd1/images/night-back.png)：相较21a能辨更多地面和山体，但近岛仍偏暗，海面大面积深蓝缺少细微层次。当前灯芯/暖窗真实存在，却不能补足整体环境照明。不能因为后向图比上一稿稍亮而接受全夜景。

实际来源：本run为61项绑定产物，独立SHA核对零不一致；三阶段passed、exit0、同inputs。不是71项，也不是61个材质绑定。sidecar仍为7条材质绑定，对应6种既有shader；天空/新云/月体另行分配材质。6个emissive_material_variants是材质变体数，不是灯/窗实例数。旧无映射清单不足的问题仍在，21b未提供全材质遗漏证明。

4个天空资产保存源gate为passed，源和GLB SHA逐项核对一致，并独立读取实际GLB坐标边界。月体1件162点320面，半径约330m；三云源分别3/5/4个原生分件，实际运行复用为7云实例，夜间再加1月体。门禁证明单件闭合/体积及来源，不证明云群艺术。月体固定世界坐标约(-3933.251,3478.453,-9791.309)，由指定参考相机基点+moon_direction*9000构建，属于有限距离近似；不是随相机无限远天空月，飞行时视差与方向光不完全重合应保留限制。三岛与屋/礁全继承20l字节。

环境光问题现在有独立交叉证据：父代理执行的 [当前引擎日志](E:/FeiTing/captures/environment-sources-runtime.log) 明确为Godot4.5.1，输出background0/color2/disabled1/sky3；我已读取 [诊断源](E:/FeiTing/captures/inspect_environment_sources.gd) 与日志并保存SHA，没有自己运行引擎。game.tscn实际写ambient_light_source=3，21b只duplicate环境并修改color/energy，没有写source。因此21b按源码继承的是SKY，而不是预期COLOR；该参数误解属实。

[Godot4.5官方Environment文档](https://docs.godotengine.org/en/4.5/classes/class_environment.html)也定义SKY=3、COLOR=2，并说明ambient_light_sky_contribution默认1.0，该值为1时颜色/能量参数不提供预期环境补光。当前场景和21b未显式写此贡献值，默认继承是源码推断，21b sidecar没有实测记录，不能伪称已读取实时值。建议下一稿明确记录source与sky_contribution和最终颜色，控制一个变量比较PBR塔/房与shader地表。这个配置问题可以解释部分夜景失衡，但不是已经排除所有材质/方向/阴影问题的唯一根因证明。

结论：保留星域和月体结构；返工夜间前景可读性、水面规则高亮、薄片云群。21c尚在运行，本报告不提前评价。整体岛岸、束光、聚落与20参考完整目标仍未过。数值与身份见[独立audit](E:/FeiTing/reviews/round-21b-environment-independent-audit.json)。
