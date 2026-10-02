# 已有 form-v2 保存源 fresh-only 恢复窄复核

复核时间：2026-10-02 21:31 UTC。结论：可以称“现有 form-v2 诊断源独立 fresh-open 及内存编辑恢复通过”。仅接受旧真实成功 build 与本次新独立 fresh-only 的有限组合；原 form-v2 整体 source 阶段仍然失败，未改写其历史，也未接受完整 native、美术、接触、世界或全部 GOAL。

## 实际核验

- 在官方绑定 Python 3.11.15（执行文件 SHA-256 `60b08089c60cbe81827b135c8fd9e206ba2ee6bf54aa1dbd0d6f56ac2d5914f6`、NumPy 1.26.4）下，仅只读调用 `recovery58l.prior_recovery()`，实测通过，耗时 7.854856454 秒。本复核未启动 Blender，未重跑既有程序测试，未新增比较容差。
- 该调用重新精确核对原完整 raw validation 与完整 exercise 报告、所有 25 份新 native 输出 SHA、旧 build/fresh-open 全基线身份、冻结前件、实际 command、stage、PID、退出观察及终端 SHA 链。返回 `existing_saved_source_fresh_open_verified=true`。
- 外部实际 launcher：supervisor PID 6，worker PID 7，退出码 0，36.822512601997005 秒，未超时，`remaining_owned_pids=[]`。新 run 仅一个 native 子进程：verify PID 8，退出码 0，13.933329271007096 秒，30 秒 native 上限、CPU affinity `[0,1]`；实际命令与既定 fresh-only 命令完全相同。注册和所有权链与 wait4 完成一致。
- worker 保留 `passed=false / prepared_passed=true / awaiting_external_process_terminal`，实际 supervisor 为 `passed=true / completed`，外部观察 `recovery_chain_verified=true`，未把准备记录当作最终完成。
- 22 条 native 事件只含 verify 入口、候选校验、一次 fresh-open、8 组控制 begin/complete 及成功终端；没有 save/build/render/export 事件。入口实现仅 open/capture/exercise。native `source_saved=false`、`images=0`，raw `images=[]`、`autoexec_enabled=false`，无本次 build 子进程或图像输出。
- 7 个主控制、1 个次参数、手工编辑保留与组合控制、精确身份恢复均由原完整 exercise 校验通过。fresh-open 及每个编辑/恢复 capture 中的 8 个 Text 与旧 build 完全相同，名称、SHA、字节数及属性均保持原 form-v2 身份。
- 运行期 `protected-before.json` 与 `protected-after.json` 的 14,478 项完全相等，包含既有源；源当前复核仍为 324,985 字节，SHA-256 `33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a`。运行结束后的合法存储报告或进度更新不混入运行期保护判断。
- 冻结前件核验通过；旧 source-runner-v3、source-recovery-v1 两次失败及原 form-v2 source 失败 admission/terminal 均保持冻结字节和失败状态。原 form-v2 terminal SHA-256 仍为 `c4856a8ffeaf5b28280beab2316f32e5b02f52720fcfed39a546d3ab9b7e7531`；旧 build 成功与旧整体 source 失败明确分离。

## 范围与证据

接受模式仅为 `api_consistency_isolated_diagnostic_v1`；`original_source_stage=failed`，`full_native_acceptance=false`、`visual_acceptance=false`、`world_acceptance=false`、`global_GOAL=false`，原 corner geometry 未获通过。没有运行或授权新的渲染阶段。

- recovery admission SHA-256：`eb7cc48b731a0c916499bf0419f3020554d6620dbf6459fb1bc30629fa70af26`
- recovery worker terminal SHA-256：`6c1cbf38413f33b815a075901d0d1fbf78eefa86b60acd5e649d120ba136e00a`
- recovery supervisor SHA-256：`766756ea0501ecf7e389b69a3569bf972e7d9c99da606782956c08335738615b`
- recovery launch observation SHA-256：`f2dce989836af58ea1275bd52c8d61bbe66a9fdec03d99ad6b2b7cdb86028989`

本复核唯一写入为本文件；未修改 raw、源码、模型、原阶段记录或既有失败证据。
