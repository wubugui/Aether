# D主冠运行时A/B/A2：代码已准备，实际世界结果待父任务运行

D完整组合五面 `cloudsea52g-d-combination-source-v0-20261001T075235Z-prnccf1i` 已由父任务实际检查。层级有变化，整体球/盘感仍失败；仅授权原10个v0主冠临时世界对照，不扩三变体、不保存scene、不改光照/材质、不以提亮代替几何。

## 固定输入与唯一范围

- Game52f SHA256：`201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c`
- D真实GLB：`revision-d-combination/cloud_sea_52g_d_main_only.glb`
- GLB SHA256：`a399fac8726ab341757a7249d17773e14a28002337eb86ae5e159d9436438624`
- 精确十条路径来自 `revision-d-combination/temporary-world-comparison-contract.json`

每次仅加载一个完整Game52f；原PackedScene引用在入树前释放。原十个main节点的mesh引用全程保留。真实D用GLTFDocument独立解析，小型源节点只读回mesh及完整祖先Transform3D，不挂入World3D，然后释放。

只替换十个既有main节点的mesh。若真实GLB祖先变换与原节点不同，仅应用这个实际变换，不重设根。保持25根、其他115云件、原三活动材质的资源身份，以及节点路径/所有权/渲染flag等。没有使用已判退52g第一版的次肩或尾体。

## 父任务GUI入口

在现有云桌面终端，先单独运行front，核查外部gate后再依次side/back：

```sh
python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52g/runtime-d-ab/run52g_d_ab.py front
python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52g/runtime-d-ab/run52g_d_ab.py side
python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52g/runtime-d-ab/run52g_d_ab.py back
```

每段只有1216的一个方向：front原机位、side原机位+50°、back原机位180°；同一相机依次拍A原版、B十件换D、A2精确恢复。每段3张1180×664主图，不在同一进程加载第二个完整世界，不重渲染旧终态图集。观察期间不要手动操纵游戏窗口。

只作解析检查：

```sh
python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52g/runtime-d-ab/run52g_d_ab.py parse
```

脚本与包装器都在本目录，直接绝对路径启动，不修改project/tools、project/assets、project.godot或任何保存scene。图形阶段要求DISPLAY，使用原cloudsea52f-stage锁防重复。每方向600秒上限是失败保护，不是完成证明；遇原生/脚本ERROR会终止并保留失败证据，不让中断函数留下假成功或无限挂起。

## 原生完整比较与A2恢复

全状态比较包括全部储存属性与资源指纹、所有脚本变量、节点身份/父子顺序/所有权/分组/场景路径/连接、各Node3D的position/rotation/rotation_order/scale/local/global transform、mesh和活动材质资源身份、碰撞状态、48,000天气浮点、原248 guard字段/114材质路径、所有光照/环境、相机实际投影以及gameplay状态。

只留一次完整A原生二进制基线 `A-native-baseline.bin`；JSON保存摘要、精确变更列表与逐目标证据，避免每阶段重复百万行快照。比较发生在原生Variant/稳定类型编码摘要之间。JSON仅作报告运输与外部布尔/数量/哈希gate，不直接拿JSON字符串/float与原生NodePath/AABB/flag相等比较。

A2从原position/rotation/order/scale逐项恢复，不从global_transform重新推导scale。每个目标的六组组件值都保存实际类型及精确字节，并核对local/global矩阵、mesh原资源身份、原活动材质与flag。随后A2整份状态执行不遮罩比较，不能通过删scale或放宽误差通过。

相机及光照设定在A前只执行一次。反射Viewport维持原UPDATE_ALWAYS共享世界绘制；三次截图不重复调用refresh_now，避免改动controller.sync_count等非scope状态。A/B/A2相机、实际投影、环境、反射同步计数、世界chunk/core数量须一致。

## 必须精确处理的引擎内生mesh连接

纯原生小探针 `probe_mesh_signal_bookkeeping.gd` 没有加载游戏或图形世界，实测：给MeshInstance3D更换mesh时，Godot把唯一 `mesh.changed → MeshInstance3D::_mesh_changed` 连接的源资源身份改为新mesh；恢复时精确回到旧资源。这是mesh赋值自带的内部绑定，不是额外业务连接修改。

实际观察对每个目标、每个A/B/A2阶段共30条逐项要求：源必须恰为当前mesh资源、目标必须为同一节点、signal为changed、method为该原生回调、flags=0、无bound参数、unbind=0且唯一。B非scope摘要只规范化这一条已完整验证的源身份，仍保护该连接的其余所有字段以及全部其他连接。A2全状态无规范化，必须恢复完全相同。探针输出保存在 `probe-mesh-signals.log`。

未纳入此内生连接前的准备脚本存于 `superseded-before-intrinsic-signal-proof/`，没有用它运行完整世界。

## 外部完成gate

Godot报告只写provisional结果。独立Python包装器必须同时确认：

- 原生进程0，无ERROR/SCRIPT ERROR/FAIL/泄漏/崩溃，全部固定输入SHA不变
- 3张实际PNG尺寸、哈希和阶段顺序正确，source/state/三个phase函数都明确正常返回
- 一份真实2200三角GLB源证明，精确十目标，B恰有十条mesh变化
- B完整非scope原生状态精确，20组B/A2目标证明与30条内生连接证明完整
- 十目标的六组组件、mesh身份、材质及flag全部恢复，A2整份未遮罩状态精确等于A
- A/A2实际RGBA及外部PNG哈希相同，B实际主图有变化
- 125云件始终在同一World3D中可见，仍使用原三活动材质

仅全部通过才写 `external-gate.json passed=true`，并绑定实际process-report和native report SHA。过程保存真实return code/信号、RSS/HWM采样、输入SHA、每帧原子partial report及PNG。不会把所有137都叫作OOM，也不会因Godot进程0就忽略函数中断/缺图。

## 当前验证与限制

最终官方Godot4.5.1 `--headless --check-only` 和Python编译通过。最终wrapper parse目录：`cloud-evidence/cloudsea52g-d-ab-parse-20261001T081519Z-yfwux3_i`，0、无错误、输入SHA不变。该parse没有实例化游戏。

首次直接parse因默认用户数据/字体缓存目录不可写而启动失败，保留 `parse-v1.log`；随后使用现有workspace userdata目录修复启动，`parse-v2.log`及最终wrapper parse成功。不能把首次失败改记成功。

源工作者没有启动GUI或实际世界对照。实际front/side/back gate尚待父任务运行；代码解析成功不是运行成功，更不是云形、飞行或总GOAL通过。旧球盘感、下腹天花板与475→650→850m两段穿云仍未解决。
