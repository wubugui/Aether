# Aether — Skyfarer 飞艇游戏 Demo

2026-09-08 已迁移恢复到 `E:\FeiTing`。本机完整性校验、运行证据和最新制作接续请先读 [WORKSPACE_RESUME.md](WORKSPACE_RESUME.md)。

这是持续制作中的 Godot 3D 飞艇游戏。当前使用独立 Blender 资产、Godot 预制场景和持久化世界布置。**画面尚未通过原图精确还原审查，不能视为美术完成。**

## 运行和编辑

- `run.cmd`：运行当前源工程。
- `open-editor.cmd`：打开 Godot 4.5.1 工程。
- `open-blender.cmd` / `open-assets.cmd`：打开 Blender 独立资产库。
- Godot 主场景：`scenes/game.tscn`；世界：`scenes/world/World.tscn`；玩家：`scenes/prefabs/Airship.tscn`。
- `build/Aether.exe`：第九轮 **09n** Windows 试玩包，37 项游戏检查通过，包内开场与同版本源工程截图 SHA256 完全一致。`build/RunAether.cmd` 显式加载同目录 PCK，避免从工程工作目录误读源文件。源码后续模型迭代可能领先于此包；美术仍未通过。
- `blender/Aether_OpenWorld.blend` 是停用的早期整体世界，不是当前工程的资产入口。

## 游戏开发流程和工程边界

1. 按 `BUILD_PLAN.md` 拆解飞艇、地形、水系、山脉、植被、建筑、天空、UI 与玩法。
2. Blender 制作独立资产。`blender/Assets.blend` 保存飞艇及环境资产，`blender/cliff_kit/` 保存六个近景岩山和一个西侧台地，`blender/mountain_kit/` 保存十一座独立山体，`blender/terrain_modules/` 保存全部 208 个独立地形块。独立道路和农田源位于 `blender/road_kit/`、`blender/land_details/`。当前城堡的权威源是 `blender/settlement_kit/castle.blend`，保留 117 个具名建筑部件。
3. Godot 的 `scenes/prefabs/` 和 `scenes/terrain/` 为导入模型配置原生节点、材质、碰撞和属性。海洋由 Godot PlaneMesh、材质和碰撞构成。
4. 在 **Godot `World.tscn`** 中摆放、复制、旋转和保存实例。Terrain、Cliffs、Mountains、Settlements、Vegetation、Clouds、Ports 是独立类别节点；Routes 保存原生 Path3D/Curve3D，道路实例放在 LandDetails。208 块地形各自引用独立 GLB；世界文件不嵌入整世界模型。
5. 飞行、相机、停靠、任务状态、进度和 UI 由 Godot 脚本运行。当前场景中的港口和植被变换驱动游戏位置及碰撞，运行时不会用旧 JSON 重置编辑结果。
6. 使用真实 Godot GPU 渲染和物理测试验收，再进行固定机位原图对比与独立 agent 审查。

`assets/world_layout.json` 是地理参数和初次组装种子；已保存的 Godot 场景才是当前布置。`tools/assemble_world.gd` 是从种子创建初始世界的一次性工具，**会重建场景，不应在普通模型重导入时运行**。局部地形/岩崖修改使用 `blender/rebuild_terrain_modules.py` 和 `tools/install_cliff_kit.gd`，保留原有布置。早期 `tools/create_game_scene.py` 与整世界 GLB 流程不再使用。

## 在编辑器里调整

打开 World，选择独立房屋、岩崖、云或地形实例，直接调整 Transform 并保存。模型、材质覆盖和碰撞属于各自预制场景。重新导入一个 GLB 不会运行世界组装脚本。

地形的 `surface_material` 由原生预制体保存。第十二轮修复了游戏启动时统一材质覆盖该属性的问题；GPU 实际保存、重开、启动四项检查通过，默认开场截图与10l逐像素相同，36项游戏检查通过。验收目录为 `captures/validation_runs/12-native-material-fix-20260906T024121Z-d0138bf180464f7798f1584131f66fb5/`。新的区域地表配色、雪山和UI研究仍在captures中，尚未作为正式美术版本集成。

植被使用保存到资源文件的 MultiMesh。选择一组植被后，可在 Inspector 中通过 Read selected instance / Apply selected transform 修改单棵位置，或 Extract to editable prefab 提取成普通可编辑实例。这些操作接入编辑器撤销重做。Skyfarer 面板提供世界/飞艇入口和编辑流程验证。

第九轮另外布置了 14 组近景标志树、树林和灌木，位于 Vegetation 下的 `Authored_*` 节点。它们与其他植被一样保存真实世界变换，参与游戏碰撞。`tools/author_vegetation_groves.gd` 是初次测定并布置这些树组的作者工具；运行游戏不会执行，普通编辑也不应重跑它覆盖已调整的树组。

城堡局部重导出使用 `blender/model_castle.py`，导入后由 `tools/refresh_model_prefabs.gd` 更新同名 prefab 的派生网格和碰撞；World 中的实例变换保留。飞艇布料当前配色由 `blender/finish_envelope.py` 写入顶点颜色，不改变气囊几何或碰撞形状。

第十轮源工程中的五块近景岩体使用 `blender/cliff_sections.py` 的独立断面模型。每个 `.blend` 保留 Grass、Wall、Slope、Buried 顶点组与面上的 Geological section 属性，用来分别编辑草顶、裸岩、后坡和地下封底。`blender/model_cliff_kit.py` 的 `--` 后可指定一个或多个完整资产名；未指定时重导出整个岩体库。模型导入后，`tools/install_cliff_kit.gd -- --asset=cliff_crown` 可只刷新该预制体及派生碰撞，并用真实地面射线重新贴合其范围内的植被，保留 World 中的实例变换。当前 Windows 试玩包仍是已经完整验证的 09n，未包含这些后续造型修改。

第十轮 10l 源工程已整合六块近景岩体与四块局部地形。`cliff_eastern_plateau.blend` 保留原生顶点配色和重新拓扑的接地带，其当前手工修订版本以该 `.blend` 为准；批量重建时只选择需要更新的断面资产。地形控制点的改动会影响相邻三角面，必须按完整受影响面域更新地形块，包含共享边界两侧。`tools/install_cliff_kit.gd -- --asset=cliff_crown --include-terrain` 将显式纳入 `assets/terrain_updates.json`，刷新派生碰撞并重新贴合植被。未加该标志的资产选择刷新不会更新地形。

道路在 Godot 的 Routes 下编辑曲线。保存后，使用 `tools/export_road_routes.gd` 导出当前曲线，Blender 执行 `blender/build_road_kit.py`；可在 `--` 后重复指定 `--road=Trail_Crownreach --road=Trail_HillHamlet`，只更新指定的独立 `.blend` / GLB。初次建立道路场景使用 `tools/install_road_kit.gd`，现有场景的模型引用在重新导入后自动更新。道路构建器当前使用相同地形作者数据生成三角面，因此相关地形模块必须先同步导出、导入并刷新碰撞，再做实际场景路面采样。路面沿地形三角边切分；这不是运行游戏时重建世界。`tools/author_road_routes.gd` 是初次布线工具，重新执行会重置这三条曲线，普通编辑不要调用。

物理层：1 = 世界实体，2 = 飞艇，3 = 地面高度探测。地形、岩崖和海面同时属于层 1、3，离地高度读取实际几何。

## 操作

| 按键 | 功能 |
|---|---|
| W / S | 增加 / 减少油门，松开后保持 |
| A / D | 左转 / 右转 |
| E / Q | 上升 / 下降 |
| Shift | 加速 |
| 空格 | 制动悬停 / 继续 |
| 右键拖动 / 滚轮 | 环绕 / 缩放 |
| C | 第三人称 / 驾驶视角 |
| F | 低速接近码头后停靠、维修、补给 |
| M / Tab | 地图 / 切换目的地 |
| H / F1 | 导航信息 / 操作帮助 |
| F4 | 自动导览，飞行输入可接管 |
| R | 回到出发空域 |
| F5 / F9 | 保存 / 恢复航行 |
| F2 / F3 | 暂停飞艇 / 地形线框 |
| N / F11 / F12 | 声音 / 全屏 / 游戏截图 |

六个港口和十二个航标构成探索循环。初始区域之外持续生成真实地形、植被和碰撞。存档与截图位于 `%APPDATA%/Godot/app_userdata/Aether — Skyfarer/`。

## 当前验证状态

最新源工程 10l 的限定范围运行 `10l-cliff-terrain-edit-20260905T222858Z-e09be6fff0384003802bf7994a07d749` 已通过 11 个阶段：六块岩体接地 4,472 个采样、全部道路 40,642 个采样、四张原始 GPU 视图、36 项游戏控制检查、连续六点绕崖、21 项岩体接触和 18 个地貌资产几何检查。首次运行因西侧相邻地形版本未同步而失败，日志与失败报告已保留；补齐两个邻块后才通过新运行。当前首屏 MAE 14.07868、SSIM 0.761939，独立视觉审查仍未通过。本次没有重新验收 Windows 包或远距离跨区飞行；`build/` 仍为 09n。

- 第七轮 GPU 游戏检查：35 / 35，包括三种近岩崖镜头插值阻挡。原生场景保存重载：第四轮 14 / 14。
- 真实 Godot 编辑器工作流：13 / 13，覆盖 Inspector 按钮、撤销重做、提取实例、保存、GLB 重导入和重新打开场景。报告 `captures/editor-assembly-validation.json`，错误日志为空。
- 第七轮实际飞艇复合碰撞体三方向接近六个岩崖：18 / 18；十一座山体：33 / 33。连续物理绕行 1124.75 米、六个航点通过，最低离地 53.23 米；安全绕行不等于贴山接缝全部验证。
- 十七个地貌 GLB 的独立拓扑、体积、无图像资源检查通过，见 `captures/geology-asset-validation.json`。
- 第八轮道路改为真实地形三角裁切，40,642 个路面内部/边缘 GPU 物理采样通过；最高误差 1.45 厘米，见 `captures/road-surface-validation.json`。后续地形变动需要重跑。
- 第八轮画面仍被独立审查打回：整图 MAE 13.378，SSIM 0.78521。第九轮修复海岸回退、重做山脊和近景岩崖，改用原生矢量 HUD；视觉指标尚未通过。持续记录于 `reviews/LOOP.md`。
- 第八轮新版导览 11.539 公里、7 航点、最低离地 124.58 米通过；四向跨区飞行 16.162 公里、生成 318 地形块，未采样到缺失地形/碰撞。后续山体修改需同版本复测。
- 第九轮 09b Windows 包 37 / 37，包含 HUD 初始化和排除历史世界/参考图片资源；运行与截图错误日志为空。第八轮两次失败包的日志保留，不能引用其打印的通过数量作为成功证据。

Godot MultiMesh 验证与组装必须使用实际渲染器，不能传 `--headless`。仅资源导入可以使用 headless：

```powershell
& ./.tools/godot/Godot_v4.5.1-stable_win64_console.exe --headless --editor --path . --import --quit
& ./.tools/godot/Godot_v4.5.1-stable_win64_console.exe --path . -- --game-test
& ./.tools/godot/Godot_v4.5.1-stable_win64_console.exe --path . --script tools/verify_game_assembly.gd
```

完整同版本验证使用：

```powershell
.\tools\validate_demo.ps1 -Round current -ExportWindows -CaptureViews
```

每次运行创建独立的 `captures/validation_runs/<run_id>/`，其中 `manifest.json` 记录该次资源与导入缓存哈希、全部阶段、新生成报告和原始图片。包位于该目录的 `package/`。脚本要求报告数量及每项结果符合预期、输入在运行期间不变，并比较本次源工程和包内开场的 SHA256；它不会自动把技术通过判为视觉通过，也不会覆盖旧 `build/Aether.exe`。

当前发布到 `build/` 的 09n 对应运行 `09n-20260905T164818Z-6f175b5518a34328b8f2fda87b661244`。该次源游戏 36/36、独立包 37/37、7 点长距离导览、4 向跨区飞行、6 点绕崖、21+33 项山体接触、40,642 路面采样和 18 个地貌资产检查均通过。源/包开场 SHA256 均为 `0a6a9184ceb8c09c55900017134d8ecbec6332da6737eee2b4a62c814a16d8bb`。原始失败运行和隔离诊断保留；正式视觉结论仍是 `reviews/round-09.md` 的未通过。运行截图时有临时模型预览使用同一 GPU，帧时只作运行日志，不作为独占性能基准。
