# 32b 前景 A 独立审查

**结论：保留两屋重新入画的构图进展，整份候选返工，不支持安装或完整视觉接受。** 草台在主机位仍挡住应可见的岩崖；新前缘的尖楔和大片直壁也不接近参考。保存源闭合通过不能替代这些实图问题。

本次直接查看 [1342参考](../ref/1342.png)、[31i夜景基准](../captures/validation_runs/lantern-island-31i-20260908T214100Z-02d75d5cf747426d88e00816dda55bd0/images/night-reference.png)，以及32b以下五张原图：

- [night-reference](../captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95/images/night-reference.png)
- [day-reference](../captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95/images/day-reference.png)
- [day-a-front](../captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95/images/day-a-front.png)
- [day-a-back](../captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95/images/day-a-back.png)
- [day-a-approach](../captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95/images/day-a-approach.png)

## 可以保留的进展

31i近屋只剩画面底边屋顶，32b两屋已在塔两侧完整可读：左屋约x120–285/y680–800，右屋约x380–500/y675–768。塔仍是主竖向锚，近景独立大树的强遮挡减弱；这比31i更接近参考的“塔—两屋”关系。两屋脚下有实体地面与可见连接线，当前三建筑各9点实际基础间隙也分别接近塔−0.5m、左屋−0.65m、右屋−0.5525m，没有从这些图和采样得出整体悬空结论。

但两栋仍像平行摆放的同类长条屋，主要露出相似长侧墙；参考左屋的山墙与右屋较紧凑的屋顶/暖墙更有深度差。下一稿可调朝向和相互叠压，不必推翻已解决的入画关系。

## 必须返工的实体关系

1. **草顶仍替代了主图的厚岩前景。** 日夜主图约x0–700/y800–941仍是大片连续斜长草坡。参考同区在小草肩下面很快转为大块厚岩面。day-a-front证明当前岛有真实厚度，并非缺少整座岩体；问题是这部分直壁在参考机位下被向前延伸的顶面遮住。下一稿应联动屋坪、塔脚外围和临海前缘的实际断面，收回草舌，露出宽岩前面及不等高的小草肩。涂灰或继续仅作水平压缩都不能保证解决。
2. **右前岩变成过尖的立楔，岩墙仍过宽直。** 主图约x640–785/y765–941可见高窄三角岩楔；day-a-approach左侧大尖峰及右侧连续尖峰更清楚。day-a-front/approach下方是几块从顶沿直落水线的大墙，少有自然中段退让，参考的近崖则是宽而错位的体块。这里独立确认的是尖楔外观，不是测得零厚度或已证明某个压缩参数为唯一原因。应直接重塑这些现有岩件的横向厚度、峰高、前后坡与落脚，做非贯穿全宽的中段坡折，避免把直墙切成等距横带。
3. **左树群的主图缺席包含遮挡问题和实际少一棵，两者须分开。** 已读取actual-site-rebuild.json：五视图均计划8棵、实际7棵；并非8棵都被过滤。day-a-back能直接看见左后四树，其实际根部Y分别约16.19/17.89/18.33/15.11m，低于约28m的屋坪，主机位被高坪与屋遮住。主机位中右侧三树可见，左侧框景仍空。应让左树群落在真正可见的有支承肩部，并使全部计划实例都有明确成功或失败记录；仅恢复缺失一棵不会自动恢复四树的轮廓。不能把它们拉长成高干树、绕过地面条件或拿树遮住未成立的岩崖。

A-back另显示两屋像立在突起的短陡草台上，外侧草坡依然很整片。这是本次屋坪重塑需留意的体量过渡：可在侧背保证地面连续和支承，不能据无对应参考的背图追求任意精确隐蔽造型。下一稿主判据仍是固定参考机位中的岩草比例和塔屋树遮挡，不回到C/D背坡。

## 运行和身份边界

实际manifest是failed，error为“Authored A trees were filtered; inspect actual site report and retain failure”。两个底层引擎阶段night-views/day-views均passed、exit0，五张图与sidecar已经齐全；末尾计划树存在性检查失败，不能把本run改称passed，也不能说它未渲染成功。父代理关于被过滤树坡度原因另有定位，本报告独立确认数量和现有树位置；未自行重跑该过滤探针。

本次对五PNG、五sidecar逐一核对manifest SHA及run_id；它们绑定的A GLB与冻结GLB、当前32b源GLB一致。冻结BLEND也与候选源逐字节一致。保存源native-check列11件、无nonmanifold/tiny缺陷且正体积，本次只读取该门禁，没有重跑或将其当视觉接受。三个建筑的9点基础只证明采样位置，不等于全接触面、道路通行或整个场景已通过。五图均记录production_modified=false，未受影响实例位置差记录为0；未扩展全世界审计。

仅写本报告及同名JSON，未修改候选或生产，未启动引擎。全部20参考及原始场景目标仍未完成。
