# 33 右岸接续：实际26b原生入口

本次只读取当前原生源和已运行装配，尚无33模型。按主参考优先级，前景A32阶段保留构图改进后，下一项是右岸岩岬、低湾与后山的纵深，再处理水面与暖灯。A和C/D整体美术仍未完成，全部20参考及原开场目标不变。

权威岸体是 `captures/village_grading_study_26b/mainland_headland.blend`，不是更早23g。已用Blender只读打开，源SHA未变，12独立件：主壳 `Mainland headland continuous bedrock and grass terraces`，8192点/16380实际三角，另11原岩肩。局部主壳边界范围Blender(-94,-190,-10.00003)..(190,220,44.48182)，世界原点(-2180,0,-1830)。完整坐标、面、材质和变换在 `captures/rightcoast33-native-intake.json`，不需再次开源只为列数。

九座主体屋、28棵原生松树的装配由冻结 `headland_runtime_23g.gd` 和 `headland/layout.json` 驱动。两组街巷共922实体来自 `captures/village_paving_study_26b/village_foreground.blend` 与 `village_bay.blend`；地形已配合这些真实路面修整，不能用旧23g地表覆盖。屋世界位置、路组原点和完整资产SHA见同名JSON。

当前 `village_paving_runtime_26b.gd` 对铺地原设计、26b修地报告和实际岸体GLB有来源绑定。将来替换33岸体时必须如实记录新的直接源、保留的旧铺地设计以及受影响范围，并同步运行时契约。不能为了运行通过伪造23g来源、删除身份检查或把旧报告绑定到新网格。

下一步先从同版主图把可见的大平灰台、湾口和内陆坡脊定位到当前实际三角与九屋/922铺地占用。随后制作不等宽、不等高、前后退让的岩岬和低湾，并在屋后建立有实体厚度的后山层次；受影响的道路、树和原地形衔接随形体变化同步。主视图可读性优先，不以没有原图的背坡精度阻塞全景进展。不能只涂灰、堆重复石块或把全部背景换成贴图。

本次只读Blender进程37296已结束，所有结果已落盘。真实五图基线在JSON记录的32e运行中；32f仅修改A局部地坪混合，右岸资产身份仍相同。最终32阶段接续以 `WORKSPACE_RESUME.md` 和32f最新同版证据为准。
