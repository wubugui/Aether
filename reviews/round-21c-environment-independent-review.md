# 21c 环境独立增量审查

**接受 ambient source 切到 COLOR 的局部修正，可作为下一轮夜景底稿；不接受完整夜景/海岸为成品。** 本次实际查看两张原始GPU图，没有重跑引擎/Blender、没有改生产。

- [night-reference](E:/FeiTing/captures/validation_runs/coast-environment-21c-20260908T102214Z-b866a4fcb0724d3ba6755f194b342f8b/images/night-reference.png)：与21b同机位相比，前景塔身、左侧房墙/屋顶、D岛岩壁和草肩显著更易辨认。塔的主面从接近黑色恢复为蓝灰，受光侧和背侧关系仍保留；不是只有灯芯与暖窗悬在黑暗里。修正有效。水光依然规则、偏亮，前景阴影偏硬，暖光束和邻近灯塔/聚落的照明联系尚缺。
- [night-back](E:/FeiTing/captures/validation_runs/coast-environment-21c-20260908T102214Z-b866a4fcb0724d3ba6755f194b342f8b/images/night-back.png)：岛岸、独立礁石、房屋和塔同时恢复可读体积，能看出岸坡和岩面分区。这个反向视角支持改善确实来自环境照明而非单机位偶然。原沿岸层带、大片草盖与路基齐墙也因此更清楚，不会因为夜景变亮就获得造型通过。

证据控制：与21b的两机位记录相同；七组岛/屋/礁blend及GLB全部字节相同，全部既有环境shader及四组天空源/GLB也字节相同，只新增 ambient-mode-derivation.py 作为派生来源记录。运行脚本实质照明差异只有 environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR，其他改动为输出source/color、局部灯和未映射shader记录。59个绑定产物SHA重新核对零不一致（不是69），两阶段passed/exit0/同inputs，非.godot缓存生产输入与21b冻结快照无变化。

两图sidecar均实际记录ambient_source=2，ambient_color≈(.36,.46,.70)，ambient_energy=1，directional_energy=.85。父代理运行的Godot4.5.1枚举日志此前已独立读取，COLOR=2、SKY=3；21b源码继承SKY，21c明确COLOR。这些源差异、运行值与真实画面共同支持修正，不需要猜测是否有效。

本轮sky_contribution未记录，不能把前轮文档/默认值讨论外推成“3→2一定无效”。21c实拍明显改善是当前直接证据。该数值可在之后统一环境控制器正常迭代中明确记录，不要求为一个未改字段重跑本轮；也不将文档讨论当作本轮已测量值。

四盏Omni已有真实运行记录：

|实例|全局XYZ（m）|能量/半径|
|---|---|---|
|A|(-2353,49.662102,-1656)|2 / 13m|
|B|(-2700,41.245506,-2202)|2 / 13m|
|C|(-3049,37.585518,-2651)|2 / 13m|
|D|(-2339.670166,37.585472,-1811.375244)|2 / 13m|

独立将每盏全局坐标与同侧车塔实例坐标+(0,19.6,0)比较，两个视角各4记录最大误差1.53e-6m，与原19h真实GLB灯芯中心一致。4盏光是两图重复记录，不是8盏不同灯；Omni局部补光不是方向性灯塔束光。

两个侧车unmapped_shader_paths均为空，源检查确认遍历实际遇到的ShaderMaterial时收集未映射路径，排除已经属于候选shader_cache的对象。这补上了21b当前遍历缺少遗漏清单的证据，但仅限这次临时加载内容；不能扩展为未来流式区域全部已覆盖。材质绑定仍7条/6shader基名，另有天空与新云月材质；6 emissive变体不计作灯或窗实例。

有限接受内容是环境光来源修正及其当前夜间可读性改善。后续仍需暖束光、村镇与灯光层次、岸体雕刻、更自然的水光与云体分布。未批准本候选生产安装，不代表全部20参考完成。来源与逐灯误差见[独立audit](E:/FeiTing/reviews/round-21c-environment-independent-audit.json)。
