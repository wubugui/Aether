# 第24轮：九屋共享院地、石阶与村内街巷（进行中）

完整目标仍为同一世界全部20张参考及原开场；23g生产未安装，原17e/18c/19h生产基底保持。本轮承接23g局部岸高修复与仍未通过的整体岩岸美术，继续把两组村屋连成具有共享空间的聚落。

## 24a 实际地形和门阶选线

`village-grid-24a-20260908T122557Z-901d701fb6c6490989941a6f2e047718` 实际GPU碰撞采样完成并terminal passed。原World与23g真实GLB同场存在，独立mask256查询两处1米网格：foreground7371点、bay6536点，共13907点。源 `captures/survey_village_grid_24a.gd`，驱动 `tools/survey_village_grid_24a.py`。不是完整路宽或通行验收。

独立实际GLB门阶/基础/廊柱和28pine检查见 `round-24a-village-route-independent-notes.md/json`。九门阶外沿：keeper localZ6.4、宽2m；fisher4.95、宽1.7m；workshop4.25、宽3m；均top=地坪+.18。workshop柱内净宽2.85m，因此不能让全3米路宽穿柱排。独立七条建议连线只作参考，其中前组upper→back有49.28°既有坡面，不能当现成步行路。

根按实际网格做避开基础/树干的选线，九门阶向两处共享小院连接。方案 `captures/village_street_layout_24a/layout.json/png`，工具 `tools/plan_village_streets_24a.py`。两小院中心(-2254,-1751)和(-2238,-1878)，九初始路线约6–31米。网格折线不是建成路；转角与整个路带在下一步处理。

## 24b / 24c Blender铺地生成

在实际23g GLB顶面上求高，圆滑初选折线、联合每组街道区域，并把小院/各门口与共享等高台阶作为同一个高度场处理。每处交叉区域只有一套分层地表，不叠几条不同高度的路。固定小院高度分别10.8和8.1米；一般等高层最大间隔.15m，门阶精确高度加入分层。两组约141.05/134.18平方米；初选曲线实体宽1.7米，没有与保守基础障碍相交。完整路宽、踏面深度和通行仍待独立/实际验证。

24b生成遇到少量近共线轮廓造成的零面积面，在第一组源检查失败；保留 `captures/village_paving_study_24b` 的部分BLEND/GLB与 `village-paving-24b.stderr.log`，未启动GPU，不当成完整候选。

24c用0.5mm保拓扑简化清理裁剪毛刺，填缝基层提高到踏面下12mm，厚10cm的石板嵌入基层；不能误写成所有石板仅在底面与基层相切。两套资产合计1807个独立编辑实体，全部Blender实际重开闭合/正体积检查通过，源 `blender/model_village_paving_24c.py`，资产 `captures/village_paving_study_24c/`，门禁 `round-24c-village-paving-native-check.json`。

实际GPU运行 `village-paving-24c-20260908T124319Z-d34facaf42ac49c1afb4d96f072e3375` 已terminal failed，session71099结束。计划5视角中只完成day-foreground一图及sidecar，原地面穿出铺石导致停止，不能写成五图完成。碰撞检查为实际cap三角重心（内切半径≥4mm）、原23g地面和每门3横点，不代表完整脚掌行走或所有细缝接触。根已直接看首图。独立 `round-24c-village-paving-independent-review.md/audit.json` 进一步确认最长约7cm的15cm深槽，以及实际GLB局部12.12cm/8.64cm穿透；24c打回。

## 24d–24g 离线修复与仍未接受的候选

24d将路基改为0.30斜率约束、一般15cm分层、入口固定高度，准备局部实体岸体修整。离线设计两组完成（session52663结束），但opening/closing可能把高路边侵蚀至全组最低层，未启动Blender或GPU。

24e去掉opening并显式保留原superlevel，设计1676实体完成（session7976结束）。独立从真实设计cap重建发现fore_upper入院口约37cm长的2.10m深坑，及bay_fisher偏移线约6cm长的15cm窄槽，明确打回。其Blender生成已在反馈到达前启动，PID13220现已终止并因两个nonmanifold和两个zero-area失败，只保留部分foreground源，未启动GPU。离线 `village_grading_design_24e/grading.json` 已生成；进程句柄27101现已不可用，没有启动该失败版本的Blender地形装配。

24f取消任何最低层补洞，改精确半平面逐层划分并核验原始分层覆盖；1mm精度清理后出现MultiPolygon而生成器仍假设单polygon，session55579 terminal failed。24g将清理后的各component分别保存为独立实体，两组879/795项离线完成（session73730 terminal exit0），等待独立踏面/高差审查，尚未启动Blender或GPU。沿用完整失败证据，不认为分层覆盖检查即可证明通行。

新增 `blender/grade_headland_for_village.py` 是未执行的局部岸体修整器：保留23g十一岩肩和原顶面三角约束、读取实际可编辑岸体求高，在路带/外侧过渡带下切并重建闭合实体。仍需正确铺地方案、实际源重开与碰撞/图像证据，不当成已完成地形修复。

## 24h–24l：设计纵坡、两点接触修复与局部岸体

上段“未执行修整器”为24g时状态，下述为更新。24g根侧27剖面证实2.1m深坑解除，但仍五条剖面有15cm窄槽，未Blender/GPU。24h不再追随原山坡每处凹地，按门口至院地设计纵坡并保留0.30限制；剩两处路边短槽。24i把高层区域延到路外后再closing，27中心/±.6m剖面与27入口横点由独立复核通过，四历史反例改善。但1521实体中的两件在同一XZ(-2219.105,-1858.989)轮廓点接触，挤出为4面共竖边，实际Blender失败，未GPU。独立 `round-24i-village-paving-independent-design-review.md/json` 完成。

24j仅修这两个轮廓并从实际清理后的基础cap建立地形约束。1521实体完整BLEND/GLB保存，实际重开全部通过 `round-24j-village-paving-native-check.json`；独立增量 `round-24j-village-paving-independent-increment-review.md/json` 确认1519实体逐字段不变、两点竖边解除，变化不交既有27剖面与入口点。根准备器repair metadata的面积不是实际cap总变化：独立cap重算基础新增6.544e-5m²、石板3.094e-5m²，两者删除5.444e-6m²，变化沿原边延至Z=-1858.143；不声称改动严格限于4mm菱形。两套编辑源 `captures/village_paving_study_24j/`。

局部岸体24j因底面微小三角zero-area失败，未保存模型；24k增加0.1mm几何退化清理后仍两张底面小三角失败，保存 `rejected-headland.blend`。失败表面与日志保留，均未GPU。原因是把道路密集顶面剖分无必要地复制到底面。

24l沿用24j的7177顶点/14218三角平面约束设计，只替换顶面，直接保留23g底面、侧壁和134原边界顶点；未改11岩肩。实际完成358顶点下切并保存 `captures/village_grading_study_24l/mainland_headland.blend/glb`，重开 `round-24l-village-grading-native-check.json` 的edge/vertex manifold、面积≥1e-9、正体积及11岩肩逐面几何/材质比较全部通过。134边界映射后直接复用原顶点，不是近似新造岸线。独立原生岸体/全cap地形检查进行中。

实际GPU `village-paving-24l-20260908T133935Z-a85da8d179904470851864e01545b1c3` 已启动，session25284；5视角结果待真实manifest。驱动 `tools/render_village_paving_24l.py` 冻结24j铺地与24l岸体，原23g模型/报告另存original-23g且替换清单写新身份。检查地形mask4同时包含原World和新岸体，不只查新候选。生产未安装，整体视觉、全脚掌通行和全部参考Goal仍未完成。

### 24l实拍打回；24m石板裁切修正与24n复拍

上述24l run已terminal failed，session25284结束；只完成day-foreground一图，根已直接看图。192失败记录中21条地形净空为负，其余主要为石板叠层，最大top误差约1.05m；不能写五图完成。独立 `round-24l-village-grading-independent-review.md/json` 确认前组10.5/10.65石板完全重叠0.115773m²，后组9.75石板越出基础区域，实际地形高0.750003m。原134岸界顶点与2937底/侧三角坐标和材质精确保留可沿用，但组合仍打回，九基础完整区域检查未继续扩大。

根追踪 `captures/trace_24j_paver_region.py` 复现：原复杂等高band是Valid Geometry，旋转后出现Self-intersection；rotated区域不覆盖反例点，但与tile的intersection错误覆盖，导致越层石板。24m保持24j基础实体逐字段完全不变，只旋转简单凸矩形tile，在原世界坐标与未旋转的有效基础区域裁切。两组802/684、共1486编辑实体完成 `.blend/.glb`，`round-24m-village-paving-native-check.json` 实际重开通过；原24l岸体继续使用，不重做地形。生成器检查每个cap只能在所属路基的3.1mm包络内，包络仅容纳精度清理/点接触局部填实，不允许旧大面积越层；真正全cap净空和交叠以独立actual GLB为准。

第二次实拍 `village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7` session19018已启动。驱动 `tools/render_village_paving_24n.py` 冻结24m铺地和24l岸体，并逐字段核原24j基础未改；运行时同时记录地面/铺石实际碰撞对象。5视角与独立actual GLB结果尚待完成，不作为整体接受。全部20参考Goal保持active。

### 24n最终状态：限定修正保留，整体视觉继续返工

24n已terminal passed，session19018 exit0。五视角全部完成，根及独立均直接看完；146绑定产物SHA根已核对。每视角同一组6639个铺石碰撞采样、145基础采样及9门×3点通过，420个细小cap因内切半径<4mm被运行时省略；不能当成五份不同覆盖。运行时最小地形净空0.06025696m、最大顶高误差0.00033265m。

独立实际GLB全12083水平cap与24l地形交集顶点极值核查无穿透：foreground7177三角/10367区域交集、bay4906三角/6585交集，最小净空47.9985/47.9739mm。大块跨层重叠消失，剩余最大重叠0.000318741/0.000059899m²均在内缩3mm后为空。原134岸界、2937原底侧三角与11岩肩已证明保留，没有重复整套旧审查。报告 `round-24n-village-paving-independent-review.md/json` 已完成，支持保留限定几何修正。

根与独立一致认为**整体美术未接受、不装生产**：近景仍有高而光滑单色的路基侧墙，街路像架高石带；等高台阶边缘重复扇贝/锯齿形明显；巨大平灰岩面、稀疏岩岛、水面规则交叉反光和缺少灯塔束光仍远离参考。下一步修真实街边填坡、路基砌筑层次与台阶造型，继续主岩岸/低湾工作区/水光和全部20参考。九基础完整区域比较、全路宽行走、流式天气和完整生产集成仍未验收，不用当前采样替代。

最新机位登记 `reference-view-1342-progress-24n.json`，根证据 `round-24n-root-evidence.json`。本轮全部已启动root生成/Blender/GPU进程均已结束；没有待等引擎或准备器。旧失败、24j/24k未通过地形、24c/24l只一图运行全部保留。当前候选铺地明确24m、岸体24l、整体装配24n，不回到旧24c/24j越层石板。完整Goal保持active。
