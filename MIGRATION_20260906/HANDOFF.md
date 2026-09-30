# Aether 项目迁移交接

本文件用于在另一台电脑恢复工作。用户于 2026-09-06 明确要求暂停制作，把目标、当前进度、所有对话和项目文件一起带走。此前的画面还原目标没有完成，不能宣布通过。

## 用户原始目标与硬要求

原始目标：依据 assets/reference.jpg，在 Godot 制作真实可自由飞行的 3D 飞艇游戏 demo，截图视角、构图、颜色和 UI 精确还原参考。

持续目标原文：

> 注意你要做的3d游戏demo，你要精确恢复这个场景，你必须有一个agent来审查你的结果，如果你的场景恢复出来差的太远就要打回去重做，给我loop起来不要轻易停止，除非你彻底做到了在截图视角下一样的表现。

用户强调：
- 必须是真正 3D 游戏，可以到处飞；地形、山、建筑、飞艇和元素都有实际模型。
- 使用 Blender 等专业软件建模。
- 先拆解制作步骤，再逐项完成并组合。
- Blender 提供独立资产；在 Godot 中用可编辑场景/预制体/实例、材质、碰撞和脚本拼装世界，不能把整个世界烘成一个模型放入引擎。
- 独立 agent 必须检查实际渲染及真实 3D；差得远就打回继续改，不能用功能测试或相似度指标代替画面验收。

当前目标状态由应用设为 paused（换电脑迁移），不是 complete；精确数值和原文见 GOAL_SNAPSHOT.json 和 history/metadata/goals_1.sqlite。恢复时继续完整目标。

## 全部历史在哪里

history/HISTORY_INDEX.json 列出原始会话、源路径、导出时间、字节数、SHA256、记录条数、相关数据库及附件。
history/raw/ 保存本项目及关联 agent 的完整原始本地 JSONL；包含历史工具记录、压缩前后的记录和原始资源数据。没有用摘要替代原始记录。
history/readable/ 保存便于浏览的用户/助手与工具记录。
history/metadata/ 保存按本项目筛选的任务、历史、目标、队列 SQLite 数据及索引。原数据库未被改写。
原始记录截至 HISTORY_INDEX.json 中的 snapshot_cutoff_utc；此后的迁移过程见 archives/migration.log，本交接和校验报告说明最终打包状态。
主任务 ID：01a06f81-bc4b-7db2-a58f-8cf029138711。
审查 agent：01a07095-c93a-7ca2-8362-45a0d234c378，/root/fidelity_reviewer，Curie。
飞艇 agent：01a074e3-3d08-7a81-ad99-1967fce18f8b，/root/airship_modeler，Godel。
同目录归档对话也一并保存，避免遗漏。它与游戏审查的作用不同，以 HISTORY_INDEX 为准。

## 当前生产工程

项目根目录原为 D:\test6，无 Git 仓库。
project.godot → scenes/game.tscn → 原生 World 与 Airship。
核心世界 scenes/world/World.tscn：208 个独立地形模块、7 个岩体（6 个前景岩体和西侧台地）、11 座独立山体、169 个聚落地标、751 个 MultiMesh 组、54,800 个保存的散布实例、6 港口、12 飞行环、3 条原生 Path3D 道路，以及独立云体和海洋。以实际源文件为权威，旧文档可能描述历史数量。
已实现油门/转向/升降、相机环绕、碰撞、港口补给、导航/地图/目标、长距离流式世界；参考机位可恢复。操作见项目 README 和 F1。
开场参考相机约 (0,145,250)，垂直 FOV50°、俯仰约 -3.526°；飞艇 (-4.15,136.8,184)，初始模型偏航13°。截图 1672×941，world_time固定。原生UI读真实游戏状态并可点击。

生产几何当前是已验证 10l 版，另加“运行时不覆盖原生地形材质”的源修复。11/12/13/14 研究稿均未正式集成。Windows build/ 仍是 09n，不是当前源工程截图。

## 已验证版本与证据边界

10l 成功冻结运行：
captures/validation_runs/10l-cliff-terrain-edit-20260905T222858Z-e09be6fff0384003802bf7994a07d749/

11 个限定源阶段通过：6 岩体脚线4472采样、3道路40642采样、4实际视角、源游戏36项、6点实际物理绕崖、21接触项、18地貌几何项等。绕崖1133.1781m，采样最小离地62.6717m。不是新版Windows发布或任意全世界物理证明。
开场 SHA256：
ee714e5973cfeab3dfe7abfbd1b53147b1259169b6e5b0d3a8a2d4db95294c2f
MAE14.07868148，SSIM0.7619390164。reviews/round-10.md 视觉仍打回。

首次 10l 失败运行完整保留：
captures/validation_runs/10l-cliff-terrain-edit-20260905T215314Z-9db8cfba59974a2f972ae3a2e65c2916/
原因是地形修改影响西侧邻块，但最初只更新东侧两块，造成 Crownreach 路面419个GPU超差采样。已补齐 Ground_-1_-1 与 Ground_-1_0 的真实变化，四块相关地形同步后新建运行通过；没有覆盖失败证据。道路原生路径没有重新创作。
reviews/round-10l-neighbor-geometry-audit.json 等保存独立旧/新GLB复核。
assets/terrain_updates.json 仅记录最后补的两块邻块，不是完整四块清单。

原生材质修复：
scripts/open_world.gd 删除 _ready 中强制 Terrain Mesh 材质改回 WORLD_MATERIAL 的赋值；材质由原生 prefab/AssetInstance.surface_material 拥有。流式新建地形仍有默认材质。
正式同版本限定运行：
captures/validation_runs/12-native-material-fix-20260906T024121Z-d0138bf180464f7798f1584131f66fb5/
4 项真实保存/重开/启动材质验证、36 游戏项通过；默认开场与10l逐像素一致。tools/verify_native_terrain_material.gd 为可复用检查。
早期 fixture 的 free() 时机触发错误，失败状态另记；后来修正 queue_free 并等待帧后才写通过报告。不要采用旧失败 fixture 的早写 passed 字段。

验证归档修复：
tools/validation_manifest.py 现在先归档新生成的报告，再拒绝非零退出/错误日志。4项针对性测试及20项原有回归通过，见 captures/failed-report-archive-fix.json。round-10.md 对归档缺口的描述是修复前历史，未重写冻结证据。

旧09n Windows包：
build/Aether.exe + Aether.pck + RunAether.cmd。
完整运行 captures/validation_runs/09n-20260905T164818Z-6f175b5518a34328b8f2fda87b661244/，19阶段，源36/包37项、长距离导览/流式/碰撞等通过，但视觉未过。
EXE SHA：78ccc576e8f8bffd7ef6ad6f36ebd72a41e609a1052225a55b3407c96ea84065
PCK SHA：b58d3705e97100704c745a358a179b7cddae69a1a38f9ed72e872cfb771c26ca
测试运行包必须显式 --main-pack 和独立工作目录，否则曾错误读到源工程。

## 最新未集成研究

详细迭代时间线见 reviews/LOOP.md；数值不是视觉完成证明。

11 雪山：captures/mountain_study_11a…11i、preview_alpine_*.gd 和原始三视图。
- 11a统一肩部加厚、11d整圈草裙被拒。
- 11b原雪色整体加红蓝，侧图粉白回退。
- 11g以具名主脊、鞍部、谷底重建完整 frost_crown，264三角；独立导出检查闭合等通过，但视觉仍是大白锥和连续蓝灰基座。reviews/round-11-wip-notes.md 与 round-11g-exported-geometry-audit.json。
- 11h增加实际前伸岩脊和两条雪沟，288三角。11i保留该几何，雪色恢复暖白/冷蓝的中性区分；root观察到侧图粉色回退消除。
- 11i全图MAE14.0590739，雪山ROI11.639；后续独立审查尚未完成，不可当成已通过或已集成。

12 地表配色：terrain_grade_12c.gdshader 等只用于临时 GPU 场景。
- 12a最初被运行时材质覆盖，实际是无变化截图，不能当作材质有效的证据。
- 修复所有权后12b/12c生效。12c以真实世界坐标和高度给沿海、田野等分区配色，并调整低空雾色；开场/反向图已渲染。
- 12c MAE13.18821323，SSIM0.762476886；root看到地表明显改善。只作用Terrain，若集成要检查与建筑/岩体/远景大气是否协调。独立视觉复核未完成。

13 UI：captures/hud_13a.gd、hud_13b.gd、game_hud_13b.gd、game_13b.gd、preview_ui_13b.gd。
- 原生Godot绘制，圆徽章、按钮宽高、状态条、图标和罗盘颜色调整；没有截图图集。
- 13b开场 captures/round-13b-study-opening.png；MAE13.9914873891，左上UI ROI10.374（10l约11.401）。保持真实状态、点击与地图。
- 仍是研究，生产scripts/hud.gd与game_hud.gd未替换；视觉审查未完成。

14 云体：captures/cloud_study_14a、14b、14c，完整独立 .blend/.glb，原生Godot实例位置保持。
- 14a重做完整截面体积，主隆起/肩部/云底，128顶点252三角；开场和侧后图暴露连续色带。
- 14b真实内部顶点不规则化、薄云底，但产生轮廓尖刺，root继续打回。
- 14c限制内环高低不越过轮廓，材质给高空云较弱的真实距离雾，保持世界坐标和完整厚度。GLB SHA f774fc668010d78676c02794a5d327d989e26bb342388a63e92d02c414ea170f。
- 14c开场/cloud-side/cloud-back已成功渲染，根在迁移前确认渲染进程结束；最终图片尚未完成视觉验收。原始中断日志 round-14c-interrupted-opening.* 保留，不与成功日志混用。
- 14a/b全图MAE仅小幅变化；不能据此宣称云体合格。14c也尚未集成。
- run_cloud_study.py、model_cloud_14*.py、game_cloud_study.gd 和材质都在 captures/，目录.gdignore避免作为生产资源导入。

15 飞艇：新 airship_modeler 已定位真实链：
blender/Assets.blend 的 Airship collection → assets/airship.glb；
Propeller 另一个GLB，由 Airship.tscn独立动画；finish_envelope.py只改顶点色。
计划重拓不等大面气囊、重贴包带、修正船体/舱体比例，保持原点、轴向和独立propeller接口。
迁移冻结时未发现任何 *15a* 文件，任务在实质建模前被中断。不要把计划写成已完成资产。其完整本地会话已打包。

## 接下来真正需要做的工作

1. 先读参考和真实10l/候选截图，恢复独立审查agent；根任务推进模型，审查不能替代实际修改。
2. 完成11i/12c/13b/14c实图复核，只把合适候选当下一版底稿，必要时返工。
3. 主要视觉差距：前景岩壁仍是规整柱/高帽、雪峰机械尖锥与连续基座、地形缺少参考的多尺度形态、岸线及浅水带不对、云与飞艇轮廓/材质/细节不匹配、UI线条/质感不完全一致。当前画面明显未达到原图。
4. 继续独立资产建模 → 原生prefab导入 → Godot场景装配 → 正面与侧后实渲染 → 独立审查循环。
5. 集成模型后同步真实碰撞、受影响地形/道路/植被布置；执行匹配改动的检查。完成同版本功能/物理/发布验证后再更新Windows包。不能拿09n包验证10l或候选版本。
6. 用户要求达到截图一致前不要轻易结束或降低目标。

## 重要工程陷阱

- 不要运行 assemble_world.gd / author_road_routes.gd / create_game_scene.py / build_scene / whole create_assets 重新覆盖原生编辑成果。它们是历史引导工具，不是当前完整再生入口。
- cliff_eastern_plateau.blend 是实际手工重拓权威文件。默认整体 model_cliff_kit 可能覆盖它；必须按资产选择。当前完整GLB SHA8348bd370539c17d683dd1e08031bb6824374dc82b06ea662d0b7534209816ab。
- 地形修改的三角影响可能超出控制点窗口；必须确定全部邻块。build_road_kit.py目前仍调用T.chunk_mesh，需要同一版本地形支持曲面，不能让新路跑在旧GLB上。
- 原生Routes是道路路径权威，不重新用旧generator布线。
- MultiMesh.duplicate(true)曾出错，使用scatter_group.gd.copy_data。
- headless Dummy renderer不能可靠写MM实例；编辑器导入可headless，真实场景/持久化/物理检查用GPU。
- Blender脚本应使用 --python-exit-code 1；普通退出0不一定表示脚本断言成功。检查日志、文件、状态和SHA。
- 同一个仍在运行的句柄超时不代表进程终止；先查原句柄/实际进程，不因观察超时重复启动。
- 失败运行、旧日志和旧图全部留存，不改成通过。
- tools/compare_reference.py仅对原始GPU图测量，不做重绘、配准或提交图处理。
- active water shader是scripts/open_water.gdshader；旧water/ocean脚本不是当前入口。
- 资料中的绝对路径D:/test6大量存在。最稳妥在新电脑仍解压到D:\test6；若改目录，需有范围地修改源脚本路径，历史与冻结证据不应批量重写。
- 当前没有任何制作进程需要在新机“接管”；两agent已中断，渲染已结束。新机重新启动所需任务。

## 迁移校验

archives/VERIFY_RESULT.json 只证明迁移包文件完整性，不是游戏画面验收。
archives/SHA256SUMS.txt 是整个ZIP的SHA256；FILE_MANIFEST.jsonl记录逐文件原始字节SHA、大小、原位置和ZIP位置。
ZIP包含整个冻结项目（含隐藏.godot/.tools、所有.blend/.blend1、GLB、失败试稿、截图、日志、build）以及迁移资料、完整Python310/用户包和Aether用户数据。
压缩包输出目录archives/自身不递归加入ZIP，防止自我包含；其校验报告在ZIP旁。FILE_MANIFEST与PACKAGE_INFO以控制文件形式加入ZIP。

