# K 四图运行：最终恢复门的只读诊断

诊断日期：2026-10-02。范围仅为本 run 的实际报告、原字节、冻结脚本、场景父链及已有本地官方源码。未运行引擎、复拍图片、修改冻结脚本或创建模型；原失败保持失败。唯一新增文件为本说明。

## 结论与证据边界

本次 22 个 native check 中 21 个通过，唯一失败为 `Opt-out and original observation camera restored`。PID 227195 真实 exit 1，58.631302 秒；wrapper exit 1，71.492864 秒。没有超时或 RSS 触界。

最后一次 `toggle(false)` 的同步 witness 比较已通过，支持旧 CloudSea_1_1 mesh 可见性恢复、该次 toggle 中其它被记录节点的 local transform / visibility / resource binding 不变。它只比较 toggle 前后，不能证明相机回到了原始观察值：相机赋值在这个 witness 的 before 之前；原始相机值也不在 witness 内。

冻结 `deactivate()` 在无 await 路径中将 `unit.visible = false`、`enabled = false`，原 native K root 无脚本。结合最后 toggle 成功，按该绑定脚本的执行语义，前三个合取项应成立，问题范围收窄到最终 `camera.global_transform == front` 精确比较。**这是由绑定代码和检查顺序作出的归因范围，不是分别记录的终态四项 raw；实际失败矩阵、失败分量和数值误差均缺失，不能声称其根因或误差大小已证明。**

没有证据允许把失败追改为 pass，也没有理由重跑这四张已被世界造型审查拒绝的图片。观察工具的恢复修正应随下一个已批准的造型观察一起验证。

## 实际已证与未记录

| 项目 | 现有证据与限制 |
| --- | --- |
| 原始观察位置 / FOV | native check 为 true：位置 `(3000,1150,4300)`、FOV `62`；不包含原 `front` 变量全矩阵的持久化记录 |
| 前图 01 与 02 的相机 | 两份 global Transform3D hex 完全相等，两份 projection hex 也完全相等；四图 FOV、near、far、reference `1216`、time `0.35` 相同 |
| 最终旧云可见 | 最后 `toggle(false)` witness passed；其 expected old visibility 被明确设为 true，原 old mesh 在 witness 覆盖内 |
| 最终 trial disabled / K hidden | 冻结 `deactivate()` 的顺序赋值与成功执行路径支持；没有另存最终 `trial.state()` 或两个独立 bool，trial 子树被 witness 明确排除 |
| 最终相机 local / global | 均未保存；仅合取结果 false。04 的相机值在复位之前采集，不能冒充复位后的值 |
| 比较右侧 `front` | 第 165 行局部 Transform3D 值未独立序列化。01 capture 在后续等待帧后读取当前 global，不能仅凭两张前图一致就宣称它逐位等于更早的 `front` |
| 原父链是否逐位不变 | 场景静态结构已核；运行时 parent identity、transform、top_level、is_scale_disabled 没有单独记录。witness 只覆盖 game 的 Node3D 后代，不含 game 自身 |
| 实际最终返回 | `report.restored_to_original=false`、`passed=false`、stage failed；随后 game.free()，没有保存世界场景 |

01/02 相机 global 的实际原 hex 为：

`1200000010742f3f8ebcf53d00df37bf0000000035807c3f91ba283e506b3a3f1048e7bd1f0e2d3f00803b4500c08f4400608645`

52 字节 Variant：4 字节 Transform3D 类型头加 12 个 float32。原生文本为 `[X: (0.685365, 0.0, 0.7282), Y: (0.119989, 0.986331, -0.11293), Z: (-0.718246, 0.164774, 0.675997), O: (3000.0, 1150.0, 4300.0)]`；文本只是展示，不能用六位小数重新构建精确复位值。

## 场景与脚本路径

实际绑定链为 CloudKTrial → Game61Coast → Game60Observation → Game56Coast → Game55Observation → Game53dWest。基础场景第 58665 行的 Skyfarer 为 Node3D，未声明 transform，Camera 是它的直接子节点（第 59300 行），无单独脚本；上层继承场景没有 Camera 或根 transform 覆盖。没有从 cloud root 到 Camera 的父链，也没有可据此认定的云 root 双旋转或 camera rig 缩放。

`game.gd:11` 的 camera 绑定 `$Camera`。1216 经 `game60_observation.gd` → `game55_observation.gd` → `game42b.gd`；后者第 63–65 行设置 local position、look_at、FOV，55 仅为 1128/1129 改相机，60 的 1216 分支只改飞艇姿态并刷新反射。`lake_reflection51b.gd` 读取主相机 camera transform 并写反射相机，不直接赋主相机 transform。这些是代码层面的路径证据，不补造本次缺失的运行时父矩阵。

关键冻结代码：

- `world-trial-v1/observe58k.gd:36–58`：witness 与同步 toggle；第 165 行保存 global front；第 180 行把 global front 写回；第 182 行一次计算四项合取
- `world-trial-v1/trial58k.gd:61–64`：deactivate 原可见性 / K 隐藏 / enabled 复位
- 原 `observe58k.gd` SHA256 `2002eee20544c9df89f2d52b1cae73e8df6b24f07f6be5afb2c6178954214309`
- 原 `trial58k.gd` SHA256 `aef681dbebe86d804293195651b1ce77a488d586cd2e974c51103f6056cd9a1c`

## 浮点路径：可解释候选，尚非根因证明

仅使用已存在的 Godot 4.5.1-stable `source-assets/north-ridge62-intake/scatter-readonly-v1/upstream/scene__3d__node_3d.cpp`，54002 字节，SHA256 `456d3ca794e76cfd5d26f08b8f07ddc53e7d8153402e874851497096d563f3da`，与其已保存 source-manifest 一致。未下载任何新引擎源码。

该文件的 `set_global_transform` 使用父 global 的 affine_inverse 乘输入，再 set_transform；`get_global_transform` 第 620–649 行在 dirty 时重算 parent × local，并在 `data.disable_scale` 条件下 orthonormalize。这证明 global 读回/写回不是一般性的“复制同一 local 存储值”。但本次没有保存 camera 的 disable_scale 状态、前后 local、原 front 与复位后的 global；本地此证据也不含 Camera3D 构造函数。因此不能断言本次经过哪条条件分支，不能将失败叫作“已证的一次 orthonormalize 舍入”，更不能按未经测量的差值新增 epsilon。

## 下一观察工具的最小修正建议

1. 在转去诊断机位前，同时保留 native `Transform3D` 原值 `front_local = camera.transform`、`front_global = camera.global_transform`，立即把两者的 `var_to_bytes(...).hex_encode()` 存进报告。另记相机路径 / instance ID / parent 路径与 ID、父 local/global、top_level、is_scale_disabled、原 projection 字节及 FOV/near/far。使用实际 float32 原值；不从 str、JSON 小数、Euler 或重新 look_at 构建原姿态。
2. 最后按保存的 native local 原值执行 `camera.transform = front_local`，避免把已计算的 global 再作为 local 推导输入；先要求父路径、身份与父矩阵仍精确相等。该建议未在本次失败进程验证，不能预先声称一定解决。
3. deactivation 后立即收集最终 `trial.state()`、实际 local/global/projection 字节，分别计算并记录 disabled、old_visible_restored、k_hidden、local_exact、global_exact、projection_exact、parent_exact。全部计算而不使用短路合取代替记录，先保存 raw，再执行独立 checks 与最终总合取。保留原 `global_transform == front_global` 精确门；额外字节证据可分辨符号零或数据表示，不能用近似相等掩盖失败。
4. 原 witness、单单位范围、原机位/天气/材质、PNG/IHDR 和几何原门不改。失败时输出具体分量 / 原始 float32 bits / 数值差，仍退出失败。仅做新观察所需的有限修正，不为本次再建相机夹具、复拍四图或新增一套宽泛浮点框架。

## 文件复核与实际图片

只读重新核实：v1 47 项 freeze 全同，SHA256 `4c99da76ec61bae16a3ec445f187286ef68471d1261bef989eb1c2bb352ae148`；v2 27 项全同，SHA256 `3287dd78bdd6cb4bde5e684d7e9cd3178ad0533a68c5ddd23fb8a8ddd178e3d3`。本 run 的 main before/after 4884 项完全相同；共享副本 before/after 的 4889 项及目录列表完全相同。实际共享 observe/trial/base scene/game script 也与两份 manifest 的 SHA 精确相同。

| 实际 PNG | 字节 | SHA256 |
| --- | ---: | --- |
| 01-original61-front.png | 420967 | c96edfa27bad139649d7184785ce0e7ede7d4a7a25540e1e246c308b85ee9c95 |
| 02-k-trial-front.png | 414964 | e1537b4ed21d62defdc67c7896f7e84704ecc168a8277beb579d09f89527a0db |
| 03-k-fixed-side-back.png | 267170 | 8f8779678765a52e373efec6b8e874e34dd13d29488a696c40fcb75005013018 |
| 04-k-fixed-near.png | 299361 | 2ec646e4c111fae2668805372912ef2225c10c8b5d359695ef16c44815c4af1a |

四 PNG 的真实 IHDR 均为 1179×664，与 native Image resolution / bytes / SHA 对应；window 为 1180×664，visible rect / content scale 为 1672×941，ViewportTexture metadata 为 831×468，均分别记录。wrapper 的 `images:0` 是 child 失败后未进入图像验证分支，不代表没出图；本说明也不冒充 wrapper 完整图像门通过或视觉接受。

原始记录身份：

- `images/report.json`：359381 字节，SHA256 `5d410f92fb116a027257e679b75d45463d8e7080423a69b9359d0291c059934d`
- `wrapper-report.json`：4396 字节，SHA256 `e287913fb32af8cbf025d2ceccc9e49ce19601609aac1d2c87742628b5d80e44`
- `renderer.process.json`：941 字节，SHA256 `a829bebec2d9c638242c6688f275f1ae0b17b891f7ced7e9a1861b08efd8d29d`
- `renderer.stderr.log`：503 字节，SHA256 `178be442f82d7ea2dbd9b4e32ebcf11ed272e7292677af8e1ddc5796ef2b28af`

本诊断只界定最后恢复失败及下一次可观测的复位方法；大洞、小硬皇冠的世界造型拒绝不受影响，尚未准备新的 K 模型。
