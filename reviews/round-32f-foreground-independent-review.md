# 32f 前景 A 最终有限视觉复核

**支持保留32f为本阶段候选，转入33右岸。** 五张实际图保持了32e的主机位进展，没有出现需要退回上一构图的视觉回归。A的大岩面、按钮状凸块和局部灰绿沟坡仍未作最终美术接受，全部参考目标也没有完成。

直接查看本run五张原图：

- [night-reference](../captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2/images/night-reference.png)
- [day-reference](../captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2/images/day-reference.png)
- [day-a-front](../captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2/images/day-a-front.png)
- [day-a-back](../captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2/images/day-a-back.png)
- [day-a-approach](../captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2/images/day-a-approach.png)

左屋山墙和门廊仍朝主机位，较低右屋完整可读；左群树没有再次升到灯室抢重心，右侧递减树组保持。两屋不再被底边裁断，塔屋活动层下面可见厚岩前面；32b的草舌遮崖和尖立楔没有回来。与本线程刚审过的32e及1342关系相比，这次主要是保住已得进展，不是又完成了一次大幅美术提升。

day-a-back两屋间靠塔脚约x756–830/y388–418仍可辨灰绿折面和局部尖折感。32e→32f在完整画面尺度下变化有限，不能仅因高度函数变为连续，就宣布所有沟坡已经自然平缓。该视角用于发现真实结构问题；没有对应参考，本文不要求把隐藏背面精细到任意造型。day-a-front/approach仍显示宽大连续坡壁和两个按钮状凸岩，参考的错位岩肩、岩脚和裂面关系继续留作美术待细化项。

父代理另行报告32e旧函数在pad边界外0.1mm发生约0.765553m高度骤降、实际局部面约89.15°，32f已改连续外部权重。本视觉复核没有重算这组函数诊断，因此将其与直接看图结论分开。已独立读取 [32f同版几何报告](round-32f-foreground-independent-geometry.json)：报告pass=true，三处建筑实际底面地表检查均通过、底面在设计pad外面积均0，并保留其自身检查范围；不冒称本次启动了源重开或重跑全套几何。

实际manifest为passed，night/day底层阶段均exit0。逐一核对五PNG、五sidecar的manifest SHA及run_id，A的sidecar/冻结/候选GLB身份相同，冻结BLEND与候选源一致。实际五图均8计划/8树存在，未受影响实例位移记录0，production_modified=false。与32e的原始像素差统计仅作为变化定位记录于同名JSON，不把像素数量当质量评分或声称五图逐字节相同。

32阶段可在保留这些限定的情况下冻结进展，后续主要工作转向33右岸，再处理真实海面与反射。本文没有将阶段保留解释为原生安装验收，没有检查C/D背坡、运行引擎或修改生产/候选；只写这两份review。
