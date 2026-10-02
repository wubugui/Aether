# form-v2 已真实保存，原完整报告相等门因跨Python末位差失败

2026-10-02 20:31:31.865872 UTC 实际启动。准备 `b171d34071225ddf74b21a441e33118a5c1930c3` 已38路径完整插件发布/远端逐字核回后才运行。本轮**source整体失败，fresh-open没有启动，0PNG**；不能称完整保存恢复通过。

## 实際保存与失败终态

- launcher6真实exit1/29.545003898994764秒；worker7 exit1/29.466245514006005秒；无timeout/RSS触界，所有自有后代回收，remaining_owned_pids=[]
- 官方Blender4.5.14 build PID8真实exit0/14.152000180998584秒，完成七主+谷宽、manual/combined和恢复，并真正一次save
- 新源 `source-assets/cloud-bank58/revision-l/form-v2/cloud_bank58l_form_v2.blend` **324985B**，SHA256 **33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a**，直接原字节Git blob，无LFS；禁止删除或重新build此已存源
- native峰344884KiB、全树采样峰409812KiB，原CPU2/总120/build80/verify30门未改。14370受保护原文件4690931090B前后同，532冻结及208旧L保护文件实际复验无变化
- 外层 `run58l_form_v2.py:147` 的原 `terminal.validation == g.validate_native_raw(raw,...)` 精确比较拒绝。它发生在源SHA接纳和fresh-open启动之前；因此supervisor.source_sha256=null、saved_source_unchanged=false以及外调用摘要source_bytes=null表示整阶段没有接纳源，**不表示未保存或已损坏**。原build结果/真实文件SHA明确存在，所有原终态不改

## 只读诊断，保留原失败

[窄失败复核](NARROW_FAILURE_REVIEW.md)独立逐项检查21份真实完整raw与所有控制/manual/原数值身份恢复。实际几何/API各门独立通过，原report精确相等门仍失败。

外部实际Python3.12.14重算只出现3个派生诊断统计的43处差异：21状态各dot_min与max_angle，加C02 moved的一次unit residual。其余报告字段和9份已记exercise geometry完全相等。

- 默认dot_min：native0.9999998228341509，外算0.999999822834151，差1.1102230246251565e-16
- 默认max_angle_degrees：native0.03410575291451074，外算0.03410575291451075，差6.938893903907228e-18
- C02 moved unit_length_error_max：native1.346539575397543e-7，外算1.346539577617989e-7，差2.220446049250313e-16

**不启动Blender**，使用已经安装的官方bundled Python3.11.15对同21原raw重放：全部完整normals报告21/21与native逐字段精确相同。实际解释器/版本/math模块路径及所有结果在两个runtime-replay JSON。证据只确认两个Python运行环境的重算差异，具体底层Python/数学库运算根因没有建立，不能猜定。

新默认的旧corner→数学几何3e-5判据仍失败**23面**，最大分量0.0005249128728819219、最大角0.03410575291451075°。历史旧L默认22面失败仍另行保留；API一致性和工程保存不替代这些原几何要求。full_native、视觉/接触/world/GOAL均false。

## 完整外存与限定恢复方向

原已保存源、21原mesh raw、两保护manifest、实际进程/调用代码/内嵌Text/失败及跨Python重放全保留。23大JSON按14唯一gzip流/15普通Git部件5286180B存储，相同恢复状态只存一个原字节对象；其它原文件直接保存，详见STORAGE.md。

先插件完整发布并远端核回、新目录恢复23JSON及核原模型blob。后续新恢复准备优先固定已有官方bundled3.11执行观察与验证，保原完整精确报告比较，**不新增任何容差分支**。先确认该解释器的所需依赖/原监督可用，仅对现有SHA33cc763源进行独立fresh-open，绑定原真实保存前件和失败终态，不重构模型、不伪装旧整阶段成功。恢复准备和实际恢复结果均分别外存核回后，才原固定机位图。
