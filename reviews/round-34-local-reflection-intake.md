# 34 暖水光独立接续调查

**只补原生 `SPECULAR_LIGHT` 不足以实现这组暖倒影。** 它适合真实灯光范围内的直接镜面照明；发光灯体的可见倒影需要场景反射，或明确标注为近似的有限发光体反射。以下依据是 34b/33f 已冻结源码、实际夜间报告及 GLB；没有启动引擎、Blender 或改动制作文件。完整精度、来源 SHA 和可复现提取脚本在同名 JSON/Python 中。

## 最终灯位与范围

九岸灯和四塔最终记录与 33f 完全一致。注意：`environment_study.local_light_records` 是较早快照，四塔 energy=2/range=13 随后由 `lantern_lighting_28h.gd` 改成 **4/28**；最终值已由 `lantern_lighting.beams` 实际记录。海面为 Godot Y=0。

| 来源 | 最终世界 X, Y, Z（m） | 能量 | Omni 范围（m） |
|---|---|---:|---:|
| fore_fisher | -2266.121, 11.440, -1753.480 | 1.8 | 11 |
| fore_workshop | -2249.955, 13.240, -1749.251 | 1.8 | 11 |
| fore_keeper | -2251.996, 14.940, -1762.292 | 1.8 | 11 |
| fore_upper | -2235.974, 16.940, -1762.027 | 1.8 | 11 |
| fore_back_cottage | -2232.141, 17.940, -1738.737 | 1.8 | 11 |
| bay_fisher | -2246.046, 8.940, -1872.017 | 1.8 | 11 |
| bay_keeper | -2236.504, 10.940, -1887.721 | 1.8 | 11 |
| bay_upper | -2223.904, 12.940, -1873.573 | 1.8 | 11 |
| bay_workshop | -2217.955, 10.940, -1858.251 | 1.8 | 11 |
| tower A | -2353.000, 49.662, -1656.000 | 4 | 28 |
| tower B | -2700.000, 41.246, -2202.000 | 4 | 28 |
| tower C | -3048.500, 31.291, -2649.200 | 4 | 28 |
| tower D | -2371.897, 31.291, -1813.697 | 4 | 28 |

表中 Y 同时为灯高。四塔 Omni 全部高于范围，九岸灯中六盏也高于范围。仅 bay_fisher、bay_keeper、bay_workshop 的照明球与无限海平面相交，交圆半径分别为 6.409、1.147、1.147 m；这些圆可能仍在陆地或被遮挡，不能叫作已照亮的水域。Godot 的 Omni 范围是硬照明截断；**并不截断发光网格被反射看见的距离**。[Godot 4.5 OmniLight3D](https://docs.godotengine.org/en/4.5/classes/class_omnilight3d.html)

四塔另各有同位 Spot：energy=8、range=560 m、半角 5.22395°、阴影开启。忽略遮挡的理想光锥最早可在约 380/372/282/270 m 射线距离抵达海平面；这只支持“部分远处水面可能接收直接镜面照明”，不能代替灯体倒影。岸灯颜色为 (1,.47,.12)、衰减1.3；塔 Omni 为 (1,.48,.12)、衰减1.5；Spot 为 (1,.62,.20)、衰减.65。岸灯范围/颜色来自冻结创建语句，报告未保存所有最终属性；其完整节点路径也由实际屋节点名和固定子节点名重建，不冒称本轮重新读取了活动节点树。

## 原生路径能做什么

当前水 `light()` 仅累加 .18 系数的 Lambert 漫反射。可增加非 Directional 的介电镜面项，直接用同一视图坐标系 `NORMAL/LIGHT/VIEW`，并把 `SPECULAR_AMOUNT`、`LIGHT_COLOR`、`ATTENUATION` 各计一次，以沿用引擎的距离/聚光锥/阴影约束；不要重复乘灯能量或再叠月光。着色器内只设置 `SPECULAR=.3` 并不能代替自定义 `SPECULAR_LIGHT`。这些是接口可行性，不是本轮已编译实现。[Godot 4.5 spatial light 接口](https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html#light-built-ins)

现海面是单个 100000×100000 m PlaneMesh。Compatibility 默认每物体最多8个 Omni，项目未见此限制的覆写；当前还存在其他港口灯，不能保证目标13个 Omni 全部进入该海面绘制。若选择原生路径，须实际记录灯选择/限制或合理划分海面接收区域，而不是直接扩大所有灯 range。[Godot Omni 限制](https://docs.godotengine.org/en/4.5/classes/class_omnilight3d.html)

## 真实发光面尺寸：34d 不应凭空放大亮球

已解码实际索引三角、所有 GLB 节点变换，坐标均为资产本地 Godot。塔资产 SHA 与实际运行 `lighthouse_sha256` 相同，村灯与冻结绑定相同。

| 发光面 | 本地中心 | 实际 bbox 尺寸（m） | 包围实际顶点的球半径 |
|---|---|---|---:|
| `Opaque_Lamp core` / `Lamp core` | (0,19.600000,0) | (.600000,1.380001,.600000) | .752397 m |
| `harbor_lantern_Harbor lantern flame` / `Harbor lantern flame` | (.840000,2.440000,0) | (.110000,.260000,.104616) | .141156 m |

两个中心都与原生 Omni 的局部灯位吻合。它们是细长形体；包围球仅保守包围，不能当成相同半径的真实宽亮球。可用实际面投影，或明确使用半轴 (.3,.6900005,.3) 和 (.055,.13,.052308) 的体近似，再保留资产 yaw。塔芯最终发光倍率是 **6**、发光色 (1,.58,.16)，与 Omni 的能量4不同；村灯 GLB emissiveFactor 约 (.9,.342,.0585)，没有额外 KHR 发光强度倍率。透明塔玻璃和透镜另有 .75/1.2 发光倍率及各自形体，详细 bbox 已保存在 JSON；不要将灯芯代理说成包含整个透镜/玻璃的精确光学外观。

## 可实施的分工及 34d 遮挡边界

当前 34d 拟做的13发光体世界注册表，是可控的低成本近似：从最终节点采集位置、源网格形状和实际发光材质；逐水点计算反射射线与有限角域，微粗糙项控制展宽。Omni range 只管照明，不用于该倒影的存在判定。粗糙展宽应保留能量和真实发光尺寸区别，不能靠扩大发光球面积增加亮带。

拟议每灯64×32下半球、450 m径向碰撞深度贴图，应明确：

- 逐灯记录生成位置、角域映射、实际最近碰撞深度、far sentinel、源/遮挡物身份及排除节点/RID。超450 m是未验证遮挡区域，应作明确覆盖边界或渐隐，不能默认畅通。
- 准确排除无限 `Sea level collision`。现塔 prefab 用一个整体 `Collision/Shape`，既有光束代码也是排除塔下全部碰撞体；**排除整个塔不等于仅排除光学 housing**，会漏掉塔柱本应产生的遮挡。要么为此项使用可区分光学件的真实网格/碰撞采样，要么保留明确误差，不能写成精确实体遮挡。
- 下半球仅覆盖灯下方水点；处理方位接缝、极点、深度偏置。64×32 是有限采样，不能保证细栏杆、窄墙和遮挡边缘精确；碰撞体也不等同透明玻璃的光学透射。
- 固定遮挡图可随观察者复用，但灯位、实体或潮位改变时需失效更新。观察者能看见灯，不等于该水点到灯的反射路径无遮挡。

若需要真实发光体形状及场景倒影，后续优先局部低分辨率平面反射视口：同一 World3D、摄像机关于Y=0镜像、排除海面递归、正确裁掉水下侧，实际灯芯与岸/房屋进入反射绘制。它不受 Omni 照明半径限制，但增加绘制成本；法线扰动采样仍是对平面镜的近似，且要避免重复累加已有解析天空/月亮。另一选择是局部 ReflectionProbe；Compatibility 支持，但每mesh至多两个探针，有限位置视差也不等于精确海面镜像。[Godot 4.5 ReflectionProbe](https://docs.godotengine.org/en/4.5/tutorials/3d/global_illumination/reflection_probes.html)

当前 Compatibility 不能直接启用内置 SSR 作为解决方案。[Godot 4.5 Environment](https://docs.godotengine.org/en/4.5/classes/class_environment.html)

下一版只需受影响证据：最终13发光体注册表/形体来源、指定灯关闭、灯照明range变化与发光面显隐的不同结果、相机移动和真实遮挡对照。这里没有实施这些验证；`full_reference_accepted=false`、`all_reference_goal_complete=false`。
