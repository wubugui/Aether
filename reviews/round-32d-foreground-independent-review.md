# 32d 前景 A 独立审查

**支持保留“窄草肩、可见厚崖、两屋入画和左侧树群”的阶段进展。先修已知塔足迹小区，再做屋向、右屋高差与最高树的有限调整；当前不作安装或整岛美术接受。** 完成这些局部修正后，可以转向主图的右岸与水光，不必把A无参考背面精细到任意程度。

本次直接比较 [1342参考](../ref/1342.png)、[32b夜景](../captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95/images/night-reference.png)，并查看32d五张原图：

- [night-reference](../captures/validation_runs/foreground-island-32d-20260908T223053Z-7b50ece5f52041238e7bb2fc49dd4936/images/night-reference.png)
- [day-reference](../captures/validation_runs/foreground-island-32d-20260908T223053Z-7b50ece5f52041238e7bb2fc49dd4936/images/day-reference.png)
- [day-a-front](../captures/validation_runs/foreground-island-32d-20260908T223053Z-7b50ece5f52041238e7bb2fc49dd4936/images/day-a-front.png)
- [day-a-back](../captures/validation_runs/foreground-island-32d-20260908T223053Z-7b50ece5f52041238e7bb2fc49dd4936/images/day-a-back.png)
- [day-a-approach](../captures/validation_runs/foreground-island-32d-20260908T223053Z-7b50ece5f52041238e7bb2fc49dd4936/images/day-a-approach.png)

## 主机位进展与差距

32b下部草坡占据了参考中的岩崖，32d约x0–730/y790–941已转为活动层下面可见的厚岩前面。右前高尖楔消失，沿岸树变为递减的侧向轮廓。这是实图可见的主要改善，不是仅凭闭合指标接受。塔与两屋仍可读，32b已经解决的底边裁断没有回来。

草岩顶沿仍偏平齐，下面大岩面也比参考整得多：参考厚崖是大小不同、前后错位的体块，草肩嵌在它们之间；32d看起来更像一个大坡壁上面放完整草盖。day-a-front/approach显示两块独立凸岩从大坡壁中部突出，读成附着按钮，体量没有很好地接到上肩和下部岩脚。应记录为后续岩壁造型缺项；不要把它们直接说成漂浮或零厚度，本次没有重算实体接合。背图只用来确认真实岛体存在、坡面连续和没有32b那种显眼尖片，不据其推断参考隐藏地理。

左群树终于在主机位显形，实际报告为8计划/8存在。最高树尖约y560，参考左最高树约y607，当前树冠几乎升到灯室区，并比其余群树粗大很多；它已经接近和塔争夺重心。降低这一棵的高度/冠幅有根据，保留左右群落与高低错落则有助于参考关系。右侧三棵由大到小下降的关系可保留，不需统一缩小所有树。

两屋虽完整，但都以长侧墙、近乎平行屋脊面对机位，参考左屋有更显著的山墙形状，右屋更低、更紧凑。支持下一稿让左屋山墙转向机位，联动真实pad与门阶路；yaw约pi/2只是可试的设计值，具体正负与角度应由新图判断。右屋降约1.5m也是合理的局部试值，有利于分开高低层次，但应保持墙面可读并处理真实入口高差，不能仅移屋体。最高树1.6→1.2可作为试值，实图以不抢塔、仍构成左侧群落为准。

## 证据与未解决的小几何问题

32d manifest实际passed，night/day两个底层引擎阶段均exit0。五图PNG及sidecar的manifest SHA、run_id已逐一核对，sidecar的A GLB SHA与冻结GLB和候选GLB相同，冻结BLEND也与候选源一致。五图实际树数均8/8，未受影响实例位移记录均0，production_modified=false。本次未扩展全世界检查，也未重新执行引擎。

另独立读取现有 [32d几何报告](round-32d-foreground-independent-geometry.json)，没有冒称本审查重跑了源检查。该报告区分了：塔实际底投影在设计pad外约0.027759m²；受影响的整个实际相交片约0.014907206m²，其中真正高度误差超过1mm的区域约0.014411437m²，地面相对目标高度最低约−0.059634m。前者不是悬空面积，后者也不是已证明悬空：灯塔底部本在目标地坪以下0.5m。它是实际阶梯足迹没有完整纳入平地约束的问题，仍应修正；三建筑各9点GPU基础采样通过不足以覆盖这个小区。两屋旋转/降高后也要重新按实际底面与门阶外沿处理，不能继续只检查旧矩形pad。

当前可保留的是真实可见的构图改善，不是闭合、run passed或9点采样替代美术接受。完成上述有界修正后，支持阶段冻结并转向更大主图差距；A大岩面与附着凸块继续保留“美术未完成”记录。未审C/D背坡，未修改源或生产，全部20参考及原始场景目标仍未完成。
