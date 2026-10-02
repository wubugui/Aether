# form-v2-recovery-v1：仅既有保存源的独立 fresh-open 准备

2026-10-02 UTC。仅新增本目录；**0 Blender / save / fresh-open / render / PNG / 新实际准入**。尚未提交或上传。本包及父入口必须先经 GitHub 插件完整发布、远端逐字节核回，才允许另行一次真实 fresh-open；本包不是执行许可。

## 前件与有限目标

前件为已完整外存的 `bd403f0b8ec262cdb6e1c627d11999ac35fa2533`。原 run `cloudbank58l-form-v2-source-20261002T203132Z-gplbz9_7` 的 build PID8 exit0 / 14.152000秒，真正一次保存并完成七主+谷宽/manual/combined及恢复；原整 source launcher6 exit1 / 29.545004秒、fresh-open未启动的失败终态完整保留。

唯一被读源仍是 `form-v2/cloud_bank58l_form_v2.blend`，324985B，SHA256 `33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a`。没有第二模型路径，不生成或复制新 `.blend`。源缺失、大小或SHA变化立即拒绝，绝不build/rebuild-on-missing/save/export。

新独立阶段身份为 `saved-source-fresh-open`、runner `cloudbank58l-form-v2-recovery-v1`。新 attempt/terminal 留在本目录，一次准入只消费本次验证。原 source-attempt/source-terminal 不删除、不复用、不改成成功。新原生 mode 明确 `verify`，其 admission、原生终态、wrapper、外监督均标实际恢复阶段；raw 的 `version=cloudbank58l-form-v2` 是所读源的真实模型版本，不伪改源内身份。

## 最小实现及原逻辑复用

- `verify_saved58l.py` 是显式 verify-only 原生入口，仅 open_mainfile 后调用原 `capture`、`exercise`、完整原validator。入口没有 create_source/save/render/export 分支；build/source/views/render参数全部拒绝
- 原 `native58l.capture/exercise/rebuild_from_controls`、`native_support58l`、`geometry58l` 和 `run58l_form_v2.validate_exercise` 均直接导入原文件，不重写编辑、捕获或任何几何/API门。exercise中的控制更新仅在内存中，包含原七主+谷宽/manual/combined及完整数值/结构恢复；不是重造源或保存
- 原 `g.HERE` 始终为 form-v2，8份原生Text仍按原 form-v2期望字节逐份核对；不向已有源加入任何新恢复代码或Text，不修改旧 `.blend`
- `run_saved58l.py` 是原 wrapper 的缩减适配，只有一次 verify任务，使用原 child helper与 `source-runner-v3/deadline58l_v3.py`。无新监督体系。原阶段时间120秒、native verify≤30秒、CPU2、aggregate 1572864KiB、20秒收尾余量保留；worker写完终态后由真实wait4和外Popen/wait决定成功
- 保护仍遍历全仓，**已有form-v2 `.blend` 明确包含在 before/after**，不会因“source”命名把它排除。仅排除当前新run与尚不存在的本次terminal/tmp；immutable新admission也纳入保护。`PREDECESSOR_SHA256.json` 624项冻结原准备/完整旧失败run及其全部raw/源
- `observe_saved58l.py` 复用原实际外观察路径：Popen正PID、完整launcher墙钟、wait、原Owned后代检查、receipt SHA核对；观察和后续全部完整报告重算也固定官方3.11，不交给3.12复算

## 官方 Python 与最小 pidfd 兼容点

解释器固定：

`/workspace/scratch/a29d03198654/tools-feiting/blender-4.5.14-linux-x64/4.5/python/bin/python3.11`

版本必须精确 `3.11.15 (main, Apr 25 2025, 12:39:20) [GCC 11.2.1 20220127 (Red Hat 11.2.1-9)]`，执行文件SHA256 `60b08089c60cbe81827b135c8fd9e206ba2ee6bf54aa1dbd0d6f56ac2d5914f6`；官方bundled NumPy1.26.4位置检查。源码中 `runtime()` 在wrapper/外观察入口检查实际解释器路径；native检查同一Python版本与bundled依赖，Blender可执行文件仍按原SHA检查。

实测该Python构建缺 `os.pidfd_open`，原v3 Owned未经适配会在fork前拒绝；`signal.pidfd_send_signal`可用。父批准的唯一兼容桥在 `recovery58l.install_pidfd_bridge()`，只给原deadline模块的os命名空间提供当前libc已有 `pidfd_open(int,unsigned int)->int`。负返回读取errno并抛OSError；fd不可继承，设置失败会close；既有Owned继续做实际PID/starttime/PPid检查、pidfd发送及关闭回收。符号不存在即停止，**不猜syscall号、不回退裸PID、不改OS权限、不改原v3文件**。桥在wrapper及外观察均安装。

## 有限纯测结果

- normal / `-O` 各24项通过：18个新范围/前件/重复/缺源/错SHA/源保护/桥测试，6个原Owned身份安全测试。实际自有pidfd可signal0且关闭后EBADF；不存在PID返回ESRCH且fd数不变；缺符号拒绝。测试内故意超时的原stderr保留，不把它误记为测试未过
- `COMPATIBILITY.json`：原完整build报告精确相等及原完整validate_exercise一次重放通过（7.299秒）；没有改任何report相等条件。官方3.11对21实际raw的完整normal报告21/21逐字段精确相同；原3.12对照仍43处差，三个派生统计字段保持原失败事实
- 直接复用原 process_fixture.py 的7个短自有Python例：normal/registered_normal exit0；registered_tree/register_failure/missing_metadata/late_receipt/rss_limit exit1均符合原预期，所有可观测自有后代已回收。全部真实Popen、wait、日志及receipt保存在COMPATIBILITY，未启动任何引擎
- 原外层 `original.prior_source(g)` 仍拒绝，测试专门防止把旧整source包装成成功。正常两个入口不带批准参数均no-op
- **这不是fresh-open成功，也没有用合成fixture声称已读保存源。** 新真实恢复仍未启动，最终源是否能fresh-open及编辑恢复只由后续实际进程成立

数值口径没有新容差/rounding。原数学polygon、flat、outward、同面3corner、API一致性各门保持；旧corner→数学几何3e-5每实际态继续测，新默认23面/max0.0005249128728819219/角0.03410575291451074°失败，历史默认22面也保留。`full_native_acceptance / visual_acceptance / contact_acceptance / world_acceptance / global_GOAL` 全false。

## 发布后唯一准确调用

只在本准备完整发布及父明确准入后，从仓库根运行：

`/workspace/scratch/a29d03198654/tools-feiting/blender-4.5.14-linux-x64/4.5/python/bin/python3.11 -B source-assets/cloud-bank58/revision-l/form-v2-recovery-v1/observe_saved58l.py --run-approved saved-source-fresh-open`

不要用默认 `python` 调用，不直接运行原 `form-v2/run58l_form_v2.py --run-approved source`，不移除原失败记录或已有源。若失败，保留新attempt/所有终态并停止，不能同准入重试。

## 后续views的组合证据

`recovery58l.prior_recovery()` 专门核“旧真实成功build + 本次独立fresh-only真实成功”，包括完整旧失败前件、真实新Popen/wait、原监督receipt/正PID/时间/输出SHA、源before/after保护、完整原raw精确报告、8Text和exercise、与旧build原baseline的完整数值/结构身份。只有两者组合成立才返回有限 `existing_saved_source_fresh_open_verified=true`，同时 `original_source_stage='failed'` 永久不变。

原 `original.prior_source` 不能被冒充为通过。后续views须另做窄适配使用此组合前件，绑定原build成功证据和新恢复全部SHA，而不是构造虚假“原source两stage成功”的对象。**本次只fresh-open**；真实新结果、完整失败/成功raw/日志及入口先经GitHub插件外存核回，然后才允许原四输出/三方向机位views。此包没有render入口、不改变candidate/geometry/材料/灯光/机位或任何旧源。
