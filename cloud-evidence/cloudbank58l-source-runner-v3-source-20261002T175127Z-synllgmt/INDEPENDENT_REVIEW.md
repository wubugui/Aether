# 58L 首次真实 source：独立失败复核

复核时间：2026-10-02 18:00 UTC。结论：**真实 source 失败，原门正确拒绝；不接受源保存、fresh-open 或 views。** 读完 `GOAL.md` 与 `CLOUD_RESUME.md` 当前硬闸后，仅做现有代码、完整 raw、日志与观察记录的只读复核。没有启动 Blender/Godot，没有修改源、候选、validator、原 raw/log，没有重试 admission，没有 Git/Slack 操作。本报告为复核唯一 repo 写入。

当前运行：`cloudbank58l-source-runner-v3-source-20261002T175127Z-synllgmt`。调用方记录上一个完整发布 commit 为 `cc4cce48963459683ea6ae5c72e3d12439571f2a`；本复核未进行远端发布验证。必须先将本次实际失败的代码、全部原始证据/必要可逐字节恢复表示、观察和报告经指定插件发布并完整读回，才可另项修复。

## 1. 实际发生了什么

- 外部调用方实际 `Popen/wait` 观察 launcher PID 5：exit **1**，2026-10-02 17:51:27.572968 至 17:51:43.686964 UTC，完整墙钟 **16.11345301999245 秒**，无 timeout。
- worker PID 6：真实 wait4 returncode **1**，观察墙钟 16.037445594003657 秒。唯一 Blender build PID 7：exit **1**，墙钟 **2.1075929810031084 秒**；实际 CPU affinity `[0,1]`、`-t 2`，80 秒 build cap 未触发。
- 24 条 `outputs/build-events.jsonl` 与 stdout 中 24 条结构化事件内容逐条相同，全部 PID 7、时间单调；最终事件与 `outputs/build-progress.json` 相同。记录依次到达候选检查完成、8 个内嵌 Text 完成、`create.complete`（1567 vertices / 3130 triangles）、capture、`raw.persisted`，随后 failed terminal。
- `native58l.py:213` 调用原 `geometry58l.validate_native_raw`；原 `native_support58l.py:112` 抛出 `ValueError: Actual vertex group identities`。stderr、build-result 的 traceback 与该源码位置一致。wrapper 随即因 `Native child failed build` 失败，没有发起第二个 native。
- build raw 与 failure raw 均 **1,556,139 bytes**，逐字节相同，SHA-256 均为 `73dfbbf9a376d4c32d29f27f02ff3ca99d72e1e7686f4e4a2a11de55b2e7182a`。失败捕获保留的是同一真实默认状态，未偷换成纯 Python recipe。
- 新 `source-v1/cloud_bank58l.blend` 实际不存在；0 次保存、0 PNG，控制/手工编辑 exercise、save、fresh-open 和 render 均未开始。原 raw `opened_filepath` 为空。`saved_source_unchanged=false` 源于新源尚未保存、`source_sha` 为空，**不表示损坏旧源文件**。

16.11 秒不能全部算为 Blender 工作。进程记录明确给出 Blender 2.11 秒；自有采样首次见 native 为整体约 7.58 秒，末次约 9.59 秒。runner 在 native 前后执行冻结输入、官方 Blender 可执行文件及全项目保护散列/落盘。没有各 hash 步骤的独立时段日志，不能更精确拆分其余约 14 秒；但其主要是外围验证/收尾，而非一次 16 秒 native build。

## 2. 已实证的直接根因：共享网格上的重复组创建

`native58l.py:99–102` 创建一张网格并赋予 master 与 derived export；`:109–113` 对每个控制执行：

```python
group = master.vertex_groups.new(name=name)
export.vertex_groups.new(name=name)
```

随后仅向第一个返回的 group 写权重。实际 raw 证明 `canonical_mesh_shared=true`、`mesh_names=['L58_CANONICAL_MESH']`，两个 mesh 对象与 mesh 捕获的组名表均为 14 项，按每一原名后紧随同名 `.001` 排列。

七个原名索引为 **0,2,4,6,8,10,12**；额外 `.001` 索引为 **1,3,5,7,9,11,13**。对全部 1567 顶点的 dense weights 和 sparse memberships 检查，七个额外组均为 **0 非零权重、0 membership**。七个原组的非零权重数及 membership 数依次均为 **122、99、61、43、231、682、474**。

这把实际 14 名表与重复 `new` 代码关联起来。原七身份门正确阻止接受不符合单一可编辑母版契约的源。不能通过接受 `.001`、忽略额外组或放宽 validator 宣称解决。

## 3. 限定内存假设探针又发现一个独立阻点

为避免把第一个异常后的字段一概当作通过，本复核进行了**一个仅内存、非 native、非修复、非准入**探针：

1. 先完整调用未修改的 `geometry58l.validate_native_raw(actual_raw,candidate,binding)`，复现原 `Actual vertex group identities`。
2. `deepcopy` 原 raw，仅在此内存副本去掉已证实为空的七个 `.001` 组；dense weights 保留偶数索引，sparse memberships 将原偶数索引重映射至 0–6；两个 mesh 对象组名表相应改成原七名。所有其它 raw 字段不变。
3. 再调用**同一个原版完整 validator**，不替换 require，不关闭任何门。它在 `native_support58l.py:139` 再次拒绝：**`Actual fixed camera numerical transform/projection`**。探针在此停止，没有跳过第二门继续冒充全通过。原 raw 再读 SHA 保持不变。

四个相机逐元素独立比较：

- 实际投影 P00：**0.9373040795326233**
- 冻结原始投影 P00：**0.9366548657417297**
- 四相机 P00 差均为 **0.0006492137908935547**，约为原 `2e-5` 门的 **32.46 倍**；其余 15 个投影矩阵元素与原矩阵相同
- 姿态矩阵最大绝对差依相机次序为 **2.2351741790771484e-7、2.2351741790771484e-7、5.960464477539063e-8、7.450580596923828e-8**，均低于原 `2e-6` 门

`native58l.py:133` 由原 P11 设置垂直镜头，`:162` 用固定 `x=1179,y=664,scale_x=scale_y=1` 求 Blender 投影。原 P11/P00 为约 **1.7768331984151413**，接近 **1672/941 = 1.7768331562167907**；实际图幅为 **1179/664 = 1.7756024096385543**，由此计算 P00 约 **0.9373041238695813**，与实际 float32 值吻合。证据支持**冻结原投影与当前方形像素采样宽高比不一致**的诊断；不是姿态误差或 .001 组的影响。绑定同时声明 1179×664 与原投影，后续修复须保留原绝对机位/投影意图并明确处理该冲突，不能换机位重构图或放宽数值门。

实际 native 原本没有到达相机门；这是保留真实相机字段的假设组修复探针揭示的后续阻点，不是一次已经修好的 source。不保证修掉这两项后其它门、编辑、保存或 fresh-open 就会通过。

## 4. 完整性、进程与资源闭环

- `protected-before.json` 与 `protected-after.json`：各 14,014 项、2,823,330 bytes，内容及字节完全相同，SHA `023502e456db2b606c673d8397726296b401e22d6b40b41d734038a28511e866`。
- 本复核另路逐文件重新读取这 **14,014 文件、4,563,172,519 bytes**，对照 before SHA：**0 缺失、0 改变**，实耗 5.967947729994194 秒。`input-sha256.json` 的 **152** 冻结输入亦全部当前 SHA 相同。该观察是在本报告及后续进度文档写入之前完成。
- 8 份 embedded-text-inputs 原文件全部与当前未改 `expected_texts` 原字节一致；每份 readback 的实际/预期 SHA、大小以及 raw 的 Text SHA相符。它们是运行中创建的内嵌重建证据，不是 `.blend` 保存证据。
- `source-terminal.json` 与 `wrapper-report.json` 原字节相同；supervisor 中两项 terminal/wrapper SHA 均绑定该文件。source admission SHA、native/candidate/binding/runner SHA、PID 5→6→7 关联及唯一 build process row 全部核对一致。
- `source-launch-observation.json` 与 `external-caller/external-process-result.json` 原字节相同；其 supervisor receipt SHA 与现有文件相同，source-launch-validation 的 external result SHA 也相同。`source_chain_verified=false` 是正确结果，不能升格为成功。
- supervisor 记录的最高实际采样总 RSS **346,924 KiB**，原 native process 最高 RSS **284,080 KiB**，native+wrapper 采样峰值 **321,040 KiB**，均未触 1,572,864 KiB 门；timeout/rss_limit_triggered 均 false。采样最高值不是未采样瞬间的内核硬上限证明。
- 211 条保留的过程样本包含自有 PID 5、6、7，以及实际短后代 PID 25（PPid 7）；因此本次不是只看 wrapper 的空树。日志只留成员变化和创新高样本，末条 9.683 秒不代表监督在后续 hash 阶段停止。
- supervisor 正常观测 worker exit 后通过“只剩自己”的自有扫描及 `wait4(-1,WNOHANG)` 无子进程判定，`all_owned_children_reaped=true`。外部调用方独立扫描 `remaining_owned_pids=[]`，没有 cleanup signal/强杀/外部收养残留。证据支持本次无泄漏；并不替代既有监督器压力试验或建立所有未来运行的保证。

## 5. 验证边界与下一步

实际原完整 validator 在组身份门停止。门前实际检查通过不等于门后的控制属性、材质、相机、对象、设置、灯光、内嵌内容与法线全部实际通过；`geometry58l.py:174` 的 actual-raw spatial gate 也未执行。内存探针到相机门后同样停止，不能据此给余下门背书。初始 candidate 检查曾实际完成，但不能替代实际源的全部验收。

本次没有接触/世界/天气/视觉/总 GOAL 接受，没有源保存或 fresh-open 接受。保留当前唯一 attempt、失败终态和原 raw/log；不删除 admission 重跑。先完成当前失败全套插件发布及远端原字节核回，再另项做最小源码修复。修复范围须同时正视重复共享组创建与原投影/采样比例冲突，完整 validator 不放宽；其后的实际编辑、保存、独立 fresh-open 仍待真实证据。

### 关键证据 SHA-256

- `outputs/build-raw.json` 与 `outputs/build-failure-raw.json`：`73dfbbf9a376d4c32d29f27f02ff3ca99d72e1e7686f4e4a2a11de55b2e7182a`
- `outputs/build-events.jsonl`：`975c50a3e2fb47093e87b2b8555ea0234d9440e41088e960d7bb03c3376133cf`
- `outputs/build-result.json`：`4f687938534b5848dc3c68b872b368d8efb981f547956627d8bb0041369bebaf`
- `build.stderr.log`：`6ff0d8dcb09c8767f3643c3f14e8348d1331fb8adf927caa4cd7b619842bdd07`
- `build.process.json`：`1628892cd53ab39610ee392b29fce707304564712f863f160e593d1acea81341`
- `supervisor-terminal.json`：`cbee31c9fa37ae431c17cae9a596f57706b40b0d0167ef5279f9f380b2d05205`
- `wrapper-report.json`：`19bd0c016af2cb4ebae751e27f250408bdd30327e56792a69bb5c52e99102dc4`
- `external-caller/external-process-result.json`：`568f3ab81b5f047137d335f3923bf7539c3ffdba5d054f6378541407431aa166`
- 原 `native58l.py`：`a0d9059d2d94f14bd7890b6835674f45a2d8b6fc9a0d8d69ee3440376b1007ad`
- 原 `native_support58l.py`：`e8cd215f0170453d9fd7c38b68641c0dfb8fa09f59b3eb4e91b1b1f627932ff1`
- 原 `geometry58l.py`：`5342902d33ceead7213b558a265d36da92686649a0487035409abdcb383d4b7d`

