# Form-v2 source 窄失败复核

2026-10-02 UTC；准备提交 `b171d34071225ddf74b21a441e33118a5c1930c3`。

## 结论

原 source 链 **仍为终态失败**。实际 Blender build PID 8 已 exit 0（14.152000181 秒），完成一次保存；外层 launcher exit 1（29.545003899 秒），卡在 `run58l_form_v2.py:147` 原有完整报告精确相等检查。独立 fresh-open **没有启动，更未通过**，没有图像或世界集成验收。

只读重放全部 **21 份实际 raw**（默认 1、控制/secondary moved/restored 16、manual 4），未经修改的实际几何、RNA/API、状态门均返回成功；完整 raw 数值身份恢复也成立。但原报告逐字段精确相等确实失败，不能改写成原链通过。

## 差异范围

默认 `build-raw` 独立重放仅有原先发现的两项：

- `/normals/geometric_direction_dot_min`：native `0.9999998228341509`，外部 `0.999999822834151`；绝对差 `1.1102230246251565e-16`
- `/normals/original_corner_geometry_max_angle_degrees`：native `0.03410575291451074`，外部 `0.03410575291451075`；绝对差 `6.938893903907228e-18`

这两处差异出现在全部 21 份 raw 的报告中；另有 **一处**：

- `build-control-1-moved.json`（C02_Crown_B）的 `/normals/unit_length_error_max`：native `1.346539575397543e-07`，外部 `1.346539577617989e-07`；绝对差 `2.220446049250313e-16`

总计 **43 处，限于三个派生统计字段**，各字段最大绝对差就是上列数值。所有其它报告字段精确相等，全部 9 份已记录的 exercise geometry 报告重放精确相等。只处理前两字段不足以走完已有 exercise 检查。unit residual 是接近 1 的长度减 1 后的误差，其最终小数的 ULP 计数不能与原长度计算的 ULP 混淆。

### 同一 raw 的 Python 运行环境对照

使用实际存在的官方 Blender 目录内 `4.5/python/bin/python3.11`，**只运行 Python，没有启动 Blender**：

- Bundled：`3.11.15 (main, Apr 25 2025, 12:39:20) [GCC 11.2.1 20220127 (Red Hat 11.2.1-9)]`；21/21 完整 normals 报告逐字段精确等于保存的 native 报告
- 外部 wrapper 的 Python：`3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]`；同一原始 raw/validator 重现上述 43 处差异

此对照建立的是跨这两个实际运行环境的重算差异；没有隔离具体 Python 算法、编译器或数学库，因此 **确切 libm 根因未知**。

## 独立核对实际门与身份

- 7 主控制、1 secondary 的规定非默认状态及完整默认恢复逐一核对；manual 指定顶点和 float32 偏移、combined control 响应、manual offset 保留、最终 baseline 恢复均成立
- 每份 raw 的完整身份采用原 `identity()` 定义：只排除 PID、CPU affinity、opened_filepath，然后比较其余全部结构与数值；不拿 JSON 序列化字节/数字类型差异冒充身份失败，也不加入数值容差
- 原 raw SHA、exercise SHA、每个 moved/restored/manual SHA 与输出边界、PID 8、CPU `[0,1]` 均核实；8 份 embedded Text 输入与被冻结源字节相同
- 21 状态实际三角布局、正厚度、固定 XZ、封闭拓扑、80m 例外域等原几何门分别重算；默认实际 1567 顶点/3130 面、单连通体、Euler 2、正体积 `292482216.4166949 m³`
- 全状态 polygon→几何最大分量误差至多 `2.7049721644800684e-06`，corner→Newell API 至多 `5.960464477539063e-08`，unit residual 至多 `1.354468625036631e-07`；原 `3e-5` 门未改，flat/三角三 corners 相等/outward 均独立成立

### 旧 corner→数学几何门仍失败

新默认为 **23 面超 `3e-5`**，最大分量误差 `0.0005249128728819219`，最大角误差 native `0.03410575291451074°` / 外部 `0.03410575291451075°`。

历史默认仍记录为 22 面、`0.00015941344933428914`、`0.009158468662372497°`；不能用 API-consistency 通过替代这项失败。此次 moved 状态超限数依次为 25、23、23、23、25、27、24、23；manual 23、combined 25，全部恢复回默认 23。所有状态本项都未通过。

## 保存与退出/保护

- 仅一个实际 build process、一个 save.begin/save.complete；目标目录仅有一个 `.blend`，没有重新构建或覆盖保存
- 已保存 `source-assets/cloud-bank58/revision-l/form-v2/cloud_bank58l_form_v2.blend`：**324985 B**，SHA256 **`33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a`**；本次重新读取与 native、failed wrapper 记录一致
- 原 `protected-before/after` 全 14370 项精确相同，诊断时当前 14370 项再次逐文件匹配；532 个冻结输入及 208 个旧源保护项均再次匹配
- 旧 API-diagnostic `.blend` SHA仍为 `7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7`
- 原 wrapper/source-terminal SHA相同且与 supervisor 所封存值匹配；supervisor SHA与 external-caller记录匹配。实际 worker/launcher exit 1、owned children 全 reaped、external remaining-owned-PIDs 空；无 timeout/RSS-trigger 证据
- wrapper 的 `saved_source_unchanged=false`、`source_output_sha256={}` 与 supervisor 的 `source_sha256=null` 保持原样。它们不能被离线核对覆盖：完整相等检查失败时还没执行后续 source/output 成功登记。只读 SHA证明已有源字节身份，**不等于 fresh-open 成功**

## 后续建议，不在本诊断实施

先完整发布本次失败、唯一已保存源及所有 raw/诊断证据并读回核实。若另行准备恢复，只能消费这份已有 `.blend` 做一次独立 no-save fresh-open，不能删除源、重做模型、重跑 build 或把旧失败改成成功。

后续已选择 **固定使用已有官方 bundled Python 3.11 观察/验证，保留原完整报告精确比较，不新增容差分支**。单独恢复项仍须先确认该解释器所需依赖、外层监督及完整验证可用；本次证据仅建立该解释器对 21 份 normals 报告的精确重放，不把这点扩称完整恢复 runner 已通过。向量/raw 数值身份、所有 `3e-5` 实际门、保护 SHA及原失败状态均保持不变。本诊断没有实施恢复、修复或阈值改变。

## 可重放证据

- `replay_narrow_failure.py`：只读、不启动引擎、不写运行时文件；结果 `narrow-failure-diagnostic.json`
- `replay_normal_runtime.py`：同一只读 normal validator 分别用两个 Python 执行；结果 `bundled-python-normal-replay.json`、`external-python-normal-replay.json`
- `runtime-replay-attempt01.json`：保留诊断元数据打印时遇到 built-in math 无 `__file__` 的失败；只修诊断脚本元数据读取，不涉及验证器

本次仅新增本 run 诊断文件；原 runtime、validator、raw、报告、源和 CLOUD 文档均未改动。
