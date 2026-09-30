# 36b 完整候选 World 保存/重开接续审查

**建议从未进入 SceneTree 的原始 World 实例构建候选，只替换改动地形 PackedScene 和散布资源，再保留原场景实例边界保存。不要直接给已经运行的 World 全部后代递归设置 owner 后打包。** 当前仓库已有明确的边界实现，可沿用其规则，不必运行整体生成器。

本项只读检查实际源码与保存场景，不修改代码、不启动引擎/GPU/Blender、不运行全世界检查。以下是候选保存的必要契约与最小后续验证方案，**不是已完成36b保存/重开证明**。

## 必须保留的原生装配契约

| 对象/路径 | 实际依赖与必要字段 |
|---|---|
| 候选根 `World` | 保留 `scripts/open_world.gd`。根不设置自己为自己的 owner；World下持久分类与直接实例属于候选World，保持场景级所有权。 |
| `World/Terrain` | 原208个保存tile实例与原名称/全局变换保留。`open_world.gd:48–55` 读取每tile的第一个Mesh并把 `tile/Collision` 注册为core terrain body；cell按全局位置+0.01计算。保留 `metadata/terrain_cell` 作为原编辑语义。 |
| 每个 `Terrain/Ground_*` | 保留 `asset_instance.gd`、`asset_kind`、`surface_material`。根原型为 `Node3D`；显示分支应为唯一 `Model`，碰撞分支为唯一 `Collision/Shape`。默认ground body layer5/mask2，Shape使用新实际三角；模型及shape所在局部坐标必须相同或正确转换。 |
| `Vegetation/<grove>` | `MultiMeshInstance3D`，保留实际MultiMesh、grove变换、材质/可见距离；保留 `scatter_group.gd`，`metadata/asset_kind` 与内容一致，`model_scene` 指向相应完整prefab。新增pine组也必须补齐这些字段。 |
| grove 的 `owner` | 必须指向具有 `Settlements` 子节点的候选World；`scatter_group.gd:extract_selected()` 实际用 `owner.get_node_or_null("Settlements")`。不能把它改成Vegetation分组、tile或外层Game。 |
| `Settlements` | 所有保存实例保留 `asset_kind`/prefab脚本/原变换。World按 `asset_kind==mill_rotor` 单独初始化rotors，其余作为landmarks；不能换成无字段的普通Node3D。 |
| `Ports` | Marker保留 `world_port.gd` 和导出字段 `port_id/display_name/landmark_style/ground_offset/inner_radius/outer_radius`。World直接调用每个marker的 `definition()`，不是仅靠名称。 |
| `FlightRings` | 保留原节点、显隐状态的作者值及 `metadata/ring_index`。World按此索引排序。 |
| `Ocean/SeaCollision/Shape` | World `_ready()` 取 `$Ocean`，`update_focus()` 会移动它。保留原Ocean场景、海面shape与层设置，不把只用于验证的海面状态当新的地理原点。 |
| `LandDetails/Cliffs/Mountains/Routes/Clouds` | 原保存实例、curve/width、asset_origin等编辑字段保持。它们虽不都参与World `_ready()` 的分类循环，仍属于保存装配和后续编辑工具的真值。 |

`Model` 名称对当前 `open_world.first_mesh()` 不是硬编码，但对后续工具是：`tools/install_cliff_kit.gd:38–39` 直接取 `Model` 和 `Collision/Shape`；`tools/export_land_detail_layout.gd` 直接取 `Model.scene_file_path`。因此不能以“游戏初始化只递归找mesh所以没报错”认为 `NativeModel36a` 与自动生成的 `@CollisionShape3D@…` 已兼容原编辑流程。

36a 的本地tile输出没有恢复 `asset_instance` 字段，显示分支叫 `NativeModel36a`，保存Shape没有显式标准名；新增pine没有scatter脚本/model_scene。36b完整候选应补齐这些契约。`asset_instance.gd` 是 `@tool`，其 `_ready()` 会用 `surface_material` 重设子mesh材质；这个行为需要与作者材质选择一致，不能只保存临时shader override却忽略surface_material。

## 全递归 owner + runtime 打包的具体风险

**1. 临时树/岩碰撞会回载重复。** `open_world.gd:289–330 refresh_collisions()` 在World根新增StaticBody；树使用CapsuleShape，岩石由 `mesh_body()` 建立。它们原本是运行时派生节点，不是编辑World持久布局。`prop_colliders` 是普通脚本Dictionary，没有导出存储。若强设owner把这些body保存，重开字典为空，`_ready()`→`update_focus(...,true)`→`refresh_collisions()` 会再次创建新body；旧保存body不被新字典登记，成为孤立重复碰撞。不能按所有StaticBody一刀删除，原 `Terrain/*/Collision`、prefab Collision 和Ocean碰撞必须保留。

**2. 动态扩展地形/散布不会按保存core重新注册。** `apply_chunk_data()` 把 `Generated_ground_*` 直接加到World根，附带运行时grove/近场碰撞；`_ready()`只从 `Terrain` 登记原生core、从 `Vegetation`重建props。把这些派生分支保存到根，会留下显示资产却缺少正确的字典登记，并可能被新流式生成重建。应排除这类runtime生成分支，而不是为了方便把它们挪入Terrain冒充本轮新原生块。

**3. prefab/GLB实例边界被抹平。** 实际 `tools/assemble_world.gd:16–21 own_all()` 给直接child设置owner，**遇到 `child.scene_file_path` 非空就停止向下递归**，注释明确要求保留导入/prefab边界，避免World嵌入/复制它们的mesh。36a的 `set_owner_recursive()` 是用于一个新建、局部、需内嵌模型的tile输出，不能无条件推广到整个既有World。改变嵌套owner会把导入子树作为World持久内容/覆盖保存，削弱原prefab和重导入关联；是否具体重建旧Model必须以重开检查为准，不能预先声称必然重复。

**4. 从旧tile运行实例改子树，不等于干净的候选tile引用。** 36a仍基于原production tile实例，隐藏/queue_free其 `Model`，另加 `NativeModel36a`。直接打包这个运行树可能保存旧实例引用加局部改动；新开PackedScene是否只恢复新Model，不能靠当前内存里“旧节点已隐藏”推断。应先保存符合上述契约的新tile PackedScene，然后在干净World中用它替换整个受影响tile实例，保留原tile名称/变换/metadata。

**5. 状态快照不应成为作者状态。** 运行时会改变Ocean位置、core碰撞layer（近场5、远场4）、rotor/ring姿态、材质override，并可能增加wireframe线；36a调用了 `world.set_process(false)`。这些状态需要从原保存作者值恢复或在重开明确检查。这里不假定所有内部process flag必定序列化，只明确不能把运行末态当编辑基准。`layout/chunks/core/terrain_samples/prop_buckets/prop_transforms/prop_colliders` 等为非导出运行缓存；不要用metadata把它们强制保存以掩盖回载初始化问题。

**6. 运行天气/检查节点不是World的通用持久作者内容。** 在当前任务中，新云/雨/光等有独立adapter，部分挂在外层Game，部分override会落到World mesh。将整个Game一起保存又会包含测试视角、HUD/音频等派生状态；只保存World也不意味着这些外层天气内容已经保存。应明确“候选World资产”与“候选Game/天气装配入口”的边界。

## 最小可验证的保存做法

1. 在原生制作结束且变换/shape/散布资源已取得后，重新加载原始 `scenes/world/World.tscn`，实例化为**未进入运行SceneTree**的干净候选。只应用14（或本版明确记录数量）个tile替换与已审查的散布变更；其余实例、顺序、脚本/metadata保留。不要运行 `assemble_world.build()` 重新生成整个世界。
2. 每个新tile先制作并保存独立PackedScene，恢复 `asset_instance`、标准 `Model`、`Collision/Shape`。本版生成模型若没有合法导入scene_file_path，可以明确把实际ArrayMesh内嵌到这个tile里；owner递归仅限此新局部tile。不要把整个旧GLB/prefab树的ownership改成World。
3. 新pine grove设 `owner=candidate_world`、`scatter_group.gd`、`model_scene=res://scenes/prefabs/pine.tscn`、`metadata/asset_kind="pine"`，复制必要材质与显示字段。沿用 `copy_data()` 的先分配后复制流程。保存新资源/候选场景采用独立路径，不能take_over原production资源路径。
4. 在候选World层使用已有 `own_all` 的实例边界策略：分类和新普通节点属于World，外部PackedScene实例根属于World，实例内部维持其原owner。新候选World保存路径与原路径分离；候选资源引用必须指向本版有效副本。
5. 若必须使用运行树作为输入，应先做**持久节点白名单重建/复制**，根据已知作者分类、原实例路径与本轮新实例记录选择内容；仅检查名称前缀不足以排除全部匿名临时body。以新建干净根重组通常比“复制全部后再猜哪些该删”更容易验证。

## 文件路径与飞行初始化边界

实际存在 `captures/.gdignore`，validation run也有 `.gdignore`。当前 `GLTFDocument.append_from_file()` 能读GLB，不证明该目录的GLB可以作为常规编辑器导入PackedScene自动重导入。可选的最小范围做法：保留candidate TSCN内嵌网格并显式保留 `.blend/.glb` 源路径与重生成入口；或把候选模型置于一个明确可导入、独立于production的候选资产目录，再引用实际导入PackedScene。不要为此移除整个captures的忽略策略或全量重导入。

候选World本身没有Airship/Camera/Game。当前 `scenes/game.tscn` 固定实例化 production `World.tscn`；保留原Game也不会自动运行新候选。需要一个候选Game入口只替换World PackedScene引用，继续保留 `World`、`Airship/Visuals/Propeller`、`Camera`、`Sun`、`Environment` 等路径。`scripts/game.gd` 的onready路径、`reset_flight()` 与World `_ready()` 应自然初始化，不能依赖验证adapter手动填入旧缓存。

编辑器dock的“Open World”和 `validate_editor()` 也硬编码production World/scratch路径（`addons/skyfarer_tools/plugin.gd:21,67`）。现有按钮的成功不能证明候选已经进入编辑流程；最小方案是明确打开候选场景并做候选定向检查，避免把旧production测试误记为新候选重开。

## 后续一次限定重开应验证什么（本项未执行）

- 保存后fresh resource load/instantiate候选：根脚本、208原地形实例数和原分类保持；每个改动tile恰有一个正确Model、一份Collision/Shape，mesh/shape摘要与本版一致，没有旧Model重现；新mesh不同时隐藏或重复。
- 所有grove脚本、owner、model_scene、asset_kind正确，全部实例总数/改动索引摘要与保存前一致；选一个新增pine验证 `Read/Apply/Extract` 所需字段与owner目标路径即可，不需要重复全世界编辑套件。实际按钮/保存再开证明若未执行就保持未验证。
- 持久World中没有本轮临时prop collider、Generated_ground、wireframe或报告节点；运行一次正常 `_ready()` 后，新增近场prop body应仅来自当前登记表，没有保存遗留孤立body。确认自然恢复正常process初始化，不保留36a冻结状态。
- 通过候选Game入口确认World/ship/camera路径和 Ports.definition 初始化成功，再用少量本版改动块的真实terrain/collision点核对新geometry绑定；这不需要重跑整体生成、全部支承或全世界路线。载具扫掠/前方净空仍是后续实际飞行验收范围，不能由保存成功代替。

此报告只列出实际代码契约与最小可审查方案。文件已完成并稳定；未修改原代码/模型，未启动新的运行进程。
