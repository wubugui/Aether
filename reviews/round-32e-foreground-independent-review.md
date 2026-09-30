# 32e 前景 A 独立增量审查

**支持保留32e作为阶段构图候选，继续右岸与水光工作。** 左屋方向、右屋高差和最高树调整在实图中有效，32d已得到的窄草肩与厚岩前景也保持。A的大墙和按钮状凸块仍未接受；本报告不代替同版几何审计，也不授权据此原生安装或宣称完整场景通过。

本次直接查看以下五张同版原图，与本审查线程刚实际看过的32d五图及1342对照；没有重复运行引擎：

- [night-reference](../captures/validation_runs/foreground-island-32e-20260908T223609Z-ac0259d9ba184d03b996e8edae4e4dc9/images/night-reference.png)
- [day-reference](../captures/validation_runs/foreground-island-32e-20260908T223609Z-ac0259d9ba184d03b996e8edae4e4dc9/images/day-reference.png)
- [day-a-front](../captures/validation_runs/foreground-island-32e-20260908T223609Z-ac0259d9ba184d03b996e8edae4e4dc9/images/day-a-front.png)
- [day-a-back](../captures/validation_runs/foreground-island-32e-20260908T223609Z-ac0259d9ba184d03b996e8edae4e4dc9/images/day-a-back.png)
- [day-a-approach](../captures/validation_runs/foreground-island-32e-20260908T223609Z-ac0259d9ba184d03b996e8edae4e4dc9/images/day-a-approach.png)

## 三项改动的实际效果

左屋现在在主图约x150–280/y690–801露出山墙和小门廊，同时保留斜侧墙。转向正确，消除了32d两栋平行长侧墙的重复感，也更接近参考左屋的紧凑山墙关系。实际runtime yaw为1.5707963267949，不能只凭设计脚本里的PI/2认定完成；这里有同版实图支持。房屋细节和塔的相对尺寸并未与参考完全一致，本轮不要求再做一轮无明确收益的微小转角。

右屋实际地坪实例Y从32d的28.4998016变为26.9998932m，变化约−1.4999084m。主图屋顶与上墙仍可读，塔右形成较低的建筑肩部，没有回到31i的底边裁断。day-a-front/back也能看出高差已进入实际场地关系。此项可保留；不把几个视角可读解释为所有入口坡度已通过。

最高左树缩为1.2，主图树尖约y606，相较32d约y560已不再升到灯室；左群仍存在，右側下降树组也保持。其余左树现在与它形成较均衡的群落，塔重新是主要竖向锚。实际五图均8计划/8树存在，不是少树造成的视觉变轻。

## 保留未完成项与有限几何边界

主图厚岩前面、收回的草顶和消失的旧尖楔都保持，足以保留当前阶段。day-a-front/approach中，大岩坡面仍很整，两个凸块像附在主壁上的按钮，参考中的不等宽岩肩、错位裂面和岩脚体量尚未达到。将这几项保留到后续美术列表，不能把主图改善说成岛岸全部接受。

day-a-back约x756–830/y388–418，两屋间靠塔脚能看到一小段细碎尖折的灰绿地坪过渡。已经向父代理明确定位，交同版几何检查判断；单凭图像不称其裂缝、穿透或浮空，也不为此扩成无参考背面精雕任务。冻结计划里塔pad已是half[5.4,5.1]，但完整真实底面、台阶足迹和cap/core界面的检查由另一个几何审查承担，本文落盘时没有提前宣布它们全部通过。

32e manifest实际passed，night/day底层引擎均exit0。已核对五PNG及五sidecar的manifest SHA、run_id；A的sidecar SHA、冻结GLB、当前候选GLB一致，冻结BLEND与候选源一致。未受影响实例位移记录为0，五图均production_modified=false。来源、实际yaw/高度/树scale及图像SHA见同名JSON。

32d旧报告的面积口径已同步修正：整个受影响相交片0.014907206m²，其中真实误差超过1mm区域0.014411437m²，设计pad外的底投影约0.0277593m²；不再将整个相交片写成超过1mm面积。

下一阶段可在必要同版几何结果确认后冻结本轮构图，转向主图更大的右岸岩岬港村和海面反射差距。未修改生产或候选，未启动引擎，未审C/D背坡。全部20参考及原始场景目标仍未完成。
