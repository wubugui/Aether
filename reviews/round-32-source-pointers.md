# 固定1342主视图的原生接续入口

本页是实际路径与运行锚点定位，不是新模型、重做方案或视觉验收。当前完整候选运行是 `captures/validation_runs/lantern-island-31i-20260908T214100Z-02d75d5cf747426d88e00816dda55bd0`；其`images/night-reference.png.json`与`study-inputs/preview.gd`记录本页坐标。

- 固定相机Godot世界坐标(-2278,60,-1632)，yaw约0.606833，FOV70。主视图参考`ref/1342.png`。背面附加相机没有对应用户原图，供实体/穿插/风格诊断，不应成为独立的未知原图还原目标。
- A前景源：`captures/lantern_islands_study_20l/island_a.blend`，实际已存在1105609字节；世界原点(-2350,0,-1650)。塔(-2353,30.062103,-1656)，两屋(-2372,22.308502,-1648)、(-2331,27.513779,-1644)。原生建筑共享源19h；房屋scale分别1/.85。
- B源：同目录`island_b.blend`，已存在904528字节；原点(-2700,0,-2200)，塔(-2700,21.645508,-2202)。不要重新运行20l整套生成器覆盖已有候选。
- C/D当前源：`captures/lantern_island_study_31i/island_c.blend`；C(-3050,0,-2650)，D(-2372,0,-1812)、yaw2。保留31i实际肩带成果及失败说明；不能用它们的局部进展接受整图。
- 当前右岸地形：`captures/village_grading_study_26b/mainland_headland.blend`，已存在1460747字节；保留街巷配套坡地。更早`captures/headland_study_23g/mainland_headland.blend`已存在904766字节，属原形底稿，不能当成最新26b地表直接覆盖。26b脚本`blender/grade_village_earthworks_26b.py`保留11原岩肩；街巷922分件为另套26b原生资产。

本页坐标是当前作者设计与实际运行事实，不是已知原游戏地图的精确地理。下一次主要场景改形的优先级由`round-32-reference-priorities.md/json`在直接对图后给出，空间改动仍需实际模型、散布、道路和碰撞接续。
