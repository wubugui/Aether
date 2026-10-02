# L source-runner-v2 独立审查

审查日期：2026-10-02 UTC。仅审原 runner 三项最小修复及新增监督的实际安全边界。先读 CLOUD_RESUME 当前硬闸、完整 GOAL、原 source-v1/INDEPENDENT_REVIEW 三项反证、新 README、runner、deadline、全部测试及所用原支持代码。

## 结论

**R1 完整实际试验状态绑定、R2 跨阶段文件保护通过本项有限复核；原 R3 最后 hash/两份阶段终态写盘漏计时的具体缺口已关闭。但 source 与 views 均 HOLD，v2 整体准备不接受。**

新增外监督在当前执行环境中，无法通过 `/proc/PID/task/TID/children` 枚举真实后代，却静默把缺文件当作没有后代。实际纯 Python 三层进程反证表明：运行时 aggregate RSS 仅采到 supervisor；超时只杀已知 worker，孙进程没有被杀，直到其自行结束才被 wait4 收回。此问题影响首次 source 的资源/清理安全边界，不能由调用方事后核一个成功退出或 stage 字段消除。

另有较小、独立的 views 准入缺口：`prior_source` 未比较阶段字段，能接受 source receipt 与 `stage=views` 的阶段记录。这一处本身原可通过调用方独立严格核 source 链，限制为 source-only；但当前真实后代监督缺口使本次 source-only 也不能放行。

没有运行 Blender、Godot、native build/fresh-open/render；没有创建或修改候选、模型、.blend、PNG、世界或原生参数。未操作 Git、Slack。当前原 13 文件、失败记录和本报告必须先完整经插件发布并远端核回，之后才能另项最小环境适配/阶段断言修复。不能在冻结 v2 内偷偷改代码或先碰碰 native。完整接触、视觉、天气、世界、全 GOAL 均未接受。

## 1. 冻结与操作范围

逐项读实际字节并核大小/SHA-256：

- 原新包：13 文件，122,839 B
- PACKAGE_MANIFEST：`37ef33c2b8a2b187ec9e5e19761a544216c3b0932204c8902ae557156c838828`，列出的 11 文件 120,073 B 全同；manifest 与 SHA 清单为另外两个原文件
- FINAL_SHA256：`538c6786899d6357d5d8bcfd52fec79cd43af81cb110d90d5e0c527599952a25`，119 输入 113,273,056 B 全同
- SOURCE_BINDING：`cd1e8ec00534b1c32e3a0c08e12c0a9ec77704c22382930f5d7dfdd43c133b75`，109 原依赖 113,175,986 B 全同
- 4 份已存在的本地 bytecode 观察值均与 binding 大小/SHA 相同；未生成新的 bytecode

只在 /tmp 创建本次专属、明确非 engine 的短进程/文件 fixture，并在测试完成后清理。测试里将新测试模块的临时目录根重定向到 /tmp，未让其默认在冻结包内创建 test-*。所有 Python 均 `-B` / PYTHONDONTWRITEBYTECODE；真实支持的 `run_child` 在回归与模拟 launcher 中明确设为禁止调用。项目内唯一新增本报告。

本次独立重跑原测试集合 normal 42/42，6.542442830 秒；-O 42/42，6.725379770 秒，均 exit0。此计时来自测试进程自己的 monotonic，绝非工具 wait 耗时。包括原三反证的真正重放与作者新负控；另做了下述独立进程/文件验证。42 项全过不等于 native 完成，也没有覆盖新增后代枚举的环境失配。

## 2. R1：实际 raw 与规定 probe 绑定已关闭

`run58l_v2.py:51–59,75–101`：

- 每个主/次试验按候选 defaults 构造完整 expected state，只改该试验指定字段，实际 raw 全主/次状态必须逐项相同
- 保留原完整 `validate_capture`，包括真实点/属性/法线/材料/相机/Text 身份；不是只看 label 或自报布尔
- restored 全 defaults、原 PID 与完整 identity 恢复继续要求
- manual 为 defaults 与指定唯一手工基底，combined 必须 C01 exercise_value 加同一手工基底；实际 vertices 必须不同于 manual，并独立调用原 `validate_evaluated` 验 combined 空间门

原“同一合法 C01 raw 复用全部八标签、combined 不变化”四面体反证再次由旧 runner 接受、新 runner 拒绝。正确八 probe/manual/combined 的完整 raw validator 通过；错误 label、额外主/次控制、manual 非默认、combined 错控制/不变化/空间门失败、法线/PID/还原破坏均拒绝。四面体的 geometry oracle 明确仅 fixture，未冒称真实候选空间证明。复用的原候选有限控制纯测试也通过；没有重审或扩张原 11 态几何结论、参数域或全 J_i。

## 3. R2：精确新输出豁免与既有 source 保护已关闭

`run58l_v2.py:18–37,106–117,126,163–170,207–213`：新阶段仅豁免事先不存在的本阶段 terminal/tmp、source 阶段唯一新源路径，以及实际 mkdtemp 新 run 目录。admission 创建后进入完整 before/after；另有独立 SHA 在 child 前及最后复核。views 不再豁免旧 source 证据。

除重放旧集合漏保护反证外，独立 /tmp 文件 inventory 包含八个既有身份：source-attempt、source-terminal、source-launch-observation、当前 views-attempt、旧目录的 source-attempt/source-terminal、prior run 的 supervisor-terminal、源占位文件。实际新 protected_manifest 全部包含；逐个改动实际字节均使清单不同，随后恢复 fixture。符号链接负控拒绝；只有精确新阶段输出/当前新 run 被排除。

原 native/geometry/candidate/bindings/阈值字节全未变。默认 no-op、一次准入、无 fallback 与 120 秒/1.5 GiB/CPU2/build80/verify30/render27/20秒收尾余量均未放宽。

## 4. R3：旧尾操作漏计时关闭，但当前后代监督有实证阻点

### 4.1 已验证的修复成果

worker 的最后源 hash、保护核验、两份 `atomic_json` flush/fsync/replace、末尾输出和实际退出都置于真实 fork/wait4 外监督之内。阶段记录仅 `prepared_passed=true`、`passed=false`、`state=awaiting_external_process_terminal`，不是成功终态。父监督收据绑定真实 worker PID/返回码及两份阶段 SHA；收据本身的写盘也受截止约束，正常 CLI 最后保持硬 alarm 并 os._exit。

原逐字提取尾代码的 119.9+1.6=121.5 秒仍 passed=true 反证再次成立；新迟到 worker exit、迟到收据及 fsync 异常都失败。独立真实短 Python launcher 测试在 /tmp 替换资产操作为明确非原生 fixture，保留实际 main/finish/supervise：两份耐久阶段写入后再 sleep 0.05，worker 真实 wait4 观察为 0.063201982 秒；外部 Popen 实际 launcher PID6、worker PID7、exit0、0.159284443 秒。阶段 passed 均 false，收据 SHA 与实际 Popen.pid 一致。这里只证明监督/落盘/外观察路径，不是 source 保存/fresh-open。

独立真实失败路径（缩短的是 fixture 的测试截止值，未改生产 120 秒门）：

- worker 尾等待超过 0.15 秒：外部 exit1/0.204652147 秒，worker -9，第一份已写证据保留、第二份未写，失败收据保留
- 收据异常：外部 exit1/0.064702980 秒，worker 实际 exit0，两份证据与失败收据保留
- 收据写入前迟延超过 0.15 秒：外部 exit1/0.190622294 秒，worker 实际 exit0，失败收据保留

这些成功地避免旧“正常收尾超120仍假成功”，不抵销以下真实监督缺口。

### 4.2 当前环境后代枚举失败：首个 source 也必须 HOLD

位置：`deadline58l.py:13–26 process_tree`，特别是读取各 task/children 时吞掉 FileNotFoundError；同函数同时用于 RSS 全树采样、kill_owned 和“无后代”判断。

在当前执行环境只读检查真实自有 PID/task：`/proc/5/task/5/children` 不存在，is_file=false；task 5 本身和 status 可读。没有推测缺文件的系统/namespace原因，也没有遍历全系统进程。独立直接 fork 的 root5→worker6→grandchild7，在孙实际存活时：worker 的 process_tree(6) 仅 `{6:7016}`，root 的 process_tree(5) 仅 `{5:10036}`，自有 task 下的 `*/children` 为空。也就是说返回单节点不是“后代已无”，而是后代入口不可用。

第一次实际 supervise 测试：0.15 秒门，已知 worker 被 -9 杀死，但另 fork/setsid 的纯 Python 孙 sleep2 未被杀，最终自然 exit0；父真正外部 Popen exit1 在 2.045386262 秒才返回。失败证据确实保留、最终也确实收尸，但不能宣称超时已经 kill 了所有拥有的进程。

为排除 fixture 误解，随后一次有界复核仅在原函数外加观察记录，原 process_tree 返回值/kill/wait4 行为未替换：

- 外部 Popen.pid = supervisor 6；worker 自报实际 PID7/PPID6；孙实际 PID8/PPID7，sleep0.5 秒
- 测试门 0.08 秒；从 0.000908471 到 0.073531757 秒的每次树采样都仅返回 supervisor6（RSS 13844–13872 KiB）
- 超时清理时 0.082989339 秒的原 process_tree 仍仅 `{6:14144}`
- 唯一 kill 调用：0.082997300 秒 `kill(7,SIGKILL)`；没有 kill(8,...) 调用
- 0.084078196 秒 wait4(-1) 实际回收 PID7，returncode=-9
- 0.503319918 秒 wait4(-1) 才回收 PID8，returncode=0；孙完整睡完，自行退出
- supervisor 实际结束点 0.503918181 秒；外部完整 Popen wait 返回 exit1/0.542538450 秒
- 当时 `/proc/6/task/6/children` 不存在。最终 all_owned_children_reaped=true 是收完之后的事实，不能反推已按截止杀死所有子孙

此反证是有限、真实、纯 Python 进程，不包含 native。`kill_owned` 明确补杀已知 worker，因此它的 -9 成立；孙 PID 只存在于测试独立观察，不被当前原枚举发现。父随后阻塞 wait4，碰巧在孙自然结束后返回。若孙更慢，当前代码没有从这个缺失树恢复拥有 PID 的途径。

同一缺口使运行期 `max_aggregate_rss_kib` 实际只采 supervisor。最终 supervisor+worker+native 的保守峰值和仍然存在且未放宽，但不是全程三层 RSS 监督，也无法修复漏杀。因此不能仅以最终退出码、原 42 项、收据自报 all_owned_children_reaped，或工具等待时长批准当前 source。

所需最小后续范围：在当前环境中可验证、仅针对本次实际拥有 PID/进程组的登记、全层 RSS 与安全清理；缺失必需观察能力时必须在 native 准入前 fail closed。恢复真实超时 kill/reap 的负控，而非扩大预算、扫描不相关进程或替换候选。没有在本报告阶段实施任何修复。

## 5. views 的 source 阶段关联漏检

位置：`run58l_v2.py:187–200 prior_source`。当前核真实外观察的 PID、收据 SHA、exit0、0<wall<120，以及 receipt worker PID/两终态 SHA/runner版本/source与admission SHA，但未比较 `prior.stage`、`receipt.stage`，也未显式把 wrapper-report/admission 的阶段关联读回作为准入要求。

独立 /tmp 非原生 fixture 保持真实 source launcher、真实 Popen/wait4、两次耐久写盘和全部 SHA，仅令 worker 两阶段记录的 `stage='views'`，监督收据仍 `stage='source'`。实际 launcher PID8/worker9、exit0、外部0.143661930秒，worker wait4 0.063484279秒；随后未修改的 prior_source 仍接受。这不是伪造实际 PID/退出/外观察，也不是运行 engine；只故意提供不一致的阶段 metadata，验证准入是否发现。

正确 source 记录正控通过；只改变外观察 supervisor_pid、receipt SHA、actual_exit_code、wall=120、process_exit_observed=false 的五个负控均被拒绝。故现有外观察绑定有效，但不能声称所有阶段关联已闭合。此缺口须在后续 views 前补最小断言/正负控；没有必要因此重做模型或新增接触门。

即使这一小缺口单独存在，调用方独立首轮 source 核验至少也必须包括：

1. 调用前启动 monotonic，实际记录 Popen.pid，真正等待 launcher；actual exit0 且从启动前至 wait 返回的 wall 严格 >0、<120；超时/信号/清理均不能记成功
2. 读取实际 admission、source-terminal、run/wrapper-report、run/supervisor-terminal，全部 stage='source'，runner_version为本版本，run 与实际新 evidence 目录一致
3. admission.wrapper_pid = 两阶段记录.worker_pid = receipt.worker_pid；admission.supervisor_pid = receipt.supervisor_pid = 实际 Popen.pid
4. receipt 真正观察 worker exit0、within budget、无 error/timeout/RSS 触发、实际清理完整；两阶段 prepared_passed=true、passed=false、awaiting_external_process_terminal；实际 stages 对应一次 build 与独立 PID verify
5. receipt 的 terminal_sha256、wrapper_report_sha256 逐个等于读到的原字节 SHA，两阶段记录为同一内容；admission_sha256、源 SHA/大小、输入冻结与原生/raw/process证据关联全部实际核同
6. 外观察文件由调用方在整个 launcher 真正退出后写；使用真实 Popen.pid、实际 exit、自己的 wall 和最终 receipt SHA；不照填 schema 示例，不把收据写盘前时间冒称 launcher 结束

这些是将来正确调用方的必要核验，不是当前后代清理缺口的替代修复，也不授权本轮 source。assets worker 的完整操作与 launcher 真正退出须被覆盖；调用方事后写自己的观察范围如实披露即可，无需无限递归地为最后一笔观察再制造终态。

## 6. 下一步与完整性复核

本次停止在唯一新增审查报告。原 R1/R2 修复成果保留，原 R3 尾操作覆盖成果保留，真实失败与 views 小缺口均保留，不把有限通过抹成全失败，也不把 42 项通过写成可 native。

先完整插件发布原 v2 全部文件、原失败日志、本独审与进度，并远端逐字节核回；之后仅做自有进程监督环境适配和 source stage 关联断言，重新有限独审。通过与再次外存核回前，不执行 source；真实 source 保存/fresh-open及所有结果外存核回后，views 仍需单独准入。

报告写入前后再次逐字节核原 13 文件、全部 119 freeze输入、109旧依赖及4已有cache，均保持上述原身份。所有 /tmp fixture 已随 TemporaryDirectory 正常清理；未改原 source-v1、候选、native、geometry、任何阈值或旧证据。
