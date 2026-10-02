# L source-runner-v3：仅自有进程监督适配与 source 阶段关联

2026-10-02 UTC。原 v2 全包及独审已发布 `3549fb37b4a584c277a4c5358d048b2cc2b98b79` 并由调用方核回后，才开始本项。只新增本目录；原 source-v1/source-runner-v2、候选、geometry/native/support、模型、相机、材质及阈值未改。**只是准备，未执行 Blender/Godot/native build/fresh-open/render，未产生真实 .blend/PNG，未准入 source/views。** 本包冻结即停，必须独审、全部插件发布并远端逐字节核回后，才能另准入一次真正 source。

## 修复范围

### 当前环境的自有进程关系

`deadline58l_v3.py` 不再读缺失的 `/proc/PID/task/TID/children`。

- Linux subreaper 监督者先核自己没有既存孩子。实际 fork 的 worker 建立独立 session，通过私有 socketpair 送出身份，父核 PID/PPid/PGID/SID/starttime 并打开 pidfd 后才放行操作
- 仅在原 `support.run_child` 的 Popen 返回点加 `registered_native_launches(support)`。不改原 native command、preexec、CPU、new-session、超时、日志或 wait4 语义；新 native 的实际 PID/PPid/PGID/SID/starttime 必须由监督者核收确认，才返回原支持继续监督。登记失败立即 kill 自己刚创建且尚未回收的直接 Popen 孩子，有界 waitpid，错误保留实际 PID/returncode；不能变成成功
- 使用当前可用的 `/proc/PID/stat`，只抽取 PID、PPid、PGID、SID、state、starttime、RSS。为找到孙及收养关系，枚举 PID 项并按已核 PPid 做有限关系闭包；无关行立刻丢弃，不保留、不输出。不读环境、命令行、文件句柄、私人内容或系统配置；不改系统限制、权限、网络
- 原身份用 starttime 重核，并在 pidfd 打开前后核整个身份元组。所有后代信号只发向已绑定确切进程的 pidfd，绝不对猜测 PID 或身份不明进程组发信号；元数据中保留实际独立 PGID/SID。PID 复用会退役旧记录，不向替代进程发信号
- 每 5ms 循环采样 supervisor+worker+全部当时可观测后代的 RSS；身份缺失/拒绝/结构错误 fail closed。它是明确采样监督，不能宣称内核级连续瞬时硬内存限制。每次 aggregate 包含所有实际层，1,572,864 KiB 原门不变；最后原三层各自实际峰值的保守和仍检查
- 超时/信号/异常后反复重新观测、kill、`wait4(-1,WNOHANG)`，直到真实内核报告没有孩子且只剩 supervisor。父先死而后代被 subreaper 收养也会纳入，不靠单次 snapshot，不用无界阻塞 wait4
- 失败清理与失败收据共同最多 1 秒；它仅是已判失败的有限收尾，不增加任何成功预算。清理超时/不可观测即明确失败、exit1，可能来不及写完整失败收据；绝不能凭此前文件声称成功。操作系统强杀监督者或不可中断 IO 不在软件可保证范围

### 阶段/身份绑定

`run58l_v3.py` 保留 R1 全 actual 主/次状态、manual/combined raw 与空间门，以及 R2 精确新输出豁免。R3 worker 最后 hash、两份耐久记录、真实退出、监督收据 IO 仍全部处于真实 deadline；成功路径硬 alarm 不关闭，调用方仍须观察真正 launcher 退出。

新 `prior_source` 同时读实际 admission、source-terminal、run/wrapper-report、receipt：四者全部 `stage=source`，同 v3 runner SHA/version、run、原 source 路径；两份 prepared 记录必须原字节相同，receipt 的两 SHA、admission SHA、源大小/SHA、实际 worker/supervisor/外观察 PID 完整关联。实际 build→verify 两条完整 process 记录/命令及 native result/raw/输出 SHA 也核回，并要求独立 PID、一次 save/一次 no-save fresh-open、无图片。它不把 views 记录改标签当 source。

任意 source-v1 或 `source-runner-v*` 兄弟目录已有对应阶段 attempt/terminal（包括坏 symlink），均拒绝重试；不删除旧记录，不 fallback 旧 runner。唯一未来源仍是原 `source-v1/cloud_bank58l.blend`。新 admission/terminal/外观察在 v3，本次新 run 只在 `cloud-evidence/cloudbank58l-source-runner-v3-{stage}-{UTC}-{unique}`。

CPU2、source/views 各120秒、build80/verify30/render27、原20秒收尾余量保持不变。contact/world/visual/weather/global_GOAL 均未接受。

## 实际纯回归证据

normal 与 `-O` 最终各 **154项通过**：78项原回归/新进程检查 + 76项实际文件 stage-chain 检查。日志分别 `tests-normal.log`、`tests-optimized.log`、`tests-stage-normal.log`、`tests-stage-optimized.log`。

78项包含原 v2 的42项（旧 R1/R2/R3真正反证保留）、同 R1/R2测试直接指向 v3、pidfd/身份/无关既存孩子保护、清理有界失败，以及13个外部 Popen 实际短 Python 场景。只对 Python fixture 调用了原 `run_child`，从未调用 engine。76项 stage 测试在 `/tmp` 使用明确非 native 的文本占位，不是模型/native 验收；包括16种旧/未来 runner 一次性准入拒绝。所有原字节/精确SHA fixture确实读写，并未以 permissive native validator 替换正式检验。

`process-evidence-{normal,optimized}.json` 保留实际 Popen PID/exit/wall、原 receipt bytes/SHA、身份采样、kill/reap 和 fixture 日志。外部 wall 从 Popen 前计至实际 wait 返回，并非工具等待时长：

- 当前环境原 v2 反例：0.08秒门后仅 worker -9；孙睡满0.5秒自然0，外层约0.565秒。运行期旧树采样仅 root。反例未被改写为通过
- v3 三层：0.08秒门后 worker/独立 session 孙均实际-9，约0.089秒回收；外层约0.164秒，远早于孙2秒自然睡眠；实际三层 RSS 相加
- v3 原支持的四层：supervisor→worker→独立 native-like Python→独立 session 孙，0.2秒门后全部3个后代实际-9，约0.209秒回收；外层约0.264秒；实际四层 RSS 相加
- worker先退出的孤儿：被本 subreaper 收养后记录真实 PPid，随后-9回收；即使孙尚未写自己的第一条日志，也以父实际 fork 结果和监督身份/内核wait证明
- 正常实际 main/finish/supervise 路径：替换资产操作为纯 Python两份耐久文本记录，外部真实 Popen exit0，两记录SHA与最终 receipt SHA/PID一致；prepared记录仍 passed=false。此项不是源保存或 Blender
- 最后 worker 写盘后的延迟、收据延迟、收据异常、登记失败、必需元数据缺失、缩小 fixture RSS门，都真实失败。模拟不可杀 WNOHANG 的纯单元负控确认清理限时后仍失败；不冒称该模拟是实际强杀

初轮和中间成功/失败日志均保留。`tests-optimized-attempt01.log` 的唯一测试问题是成功清理过快、孙还没写可选自报文件，测试曾误读缺文件；实际进程已经被杀回。改为父 durable fork PID 作必有证据后两模式通过；未因此放宽生产门。所有 `process-evidence-*-attempt*.json` 是当时记录，不覆盖为最终代码结果。

## 冻结与复核

SOURCE_BINDING 完整绑定原123文件/113,312,816 B：v2 FINAL的119输入及其全部包文件/独审的并集。原4个已有pycache只记录相同大小/SHA，不作为可分发依赖。没有复制旧2MB准备包、模型或候选。FINAL_SHA256 冻结旧依赖与本次代码/README/日志，PACKAGE_MANIFEST/SHA256SUMS 描述完整新包。

默认命令仍 no-op。纯回归建议在独审时将输出放到已有 `/tmp` 专属目录，避免改冻结包：

```text
PYTHONDONTWRITEBYTECODE=1 AETHER_V3_EVIDENCE_DIR=/tmp/your-owned-existing-directory python -B source-assets/cloud-bank58/revision-l/source-runner-v3/test_runner58l_v3.py
PYTHONDONTWRITEBYTECODE=1 python -B source-assets/cloud-bank58/revision-l/source-runner-v3/test_stage58l_v3.py
```

对 `-O` 同样适用。测试临时进程目录为 `/tmp/aether-v3-*`，记录保留；旧v2测试的包内临时目录已重定向 `/tmp`。无新增bytecode。

未来 source 的唯一正式 runner 是本目录 run58l_v3.py，但此准备没有执行 `--run-approved source/views`。真实调用方必须从启动前计时，记录真正 Popen.pid/完整实际 wait/exit0且总wall严格小于120，再读回本 v3 全source链的 stage/PID/完整SHA。外观察在 launcher真正退出之后新建 source-launch-observation.json，至少含 process_exit_observed、actual_exit_code、wall_seconds、supervisor_pid、supervisor_terminal_sha256；不能由尚未退出的 runner自签，不能照填示例数字。任何超时/清理/非0/证据缺失都不通过且不重试。source全部产物再次插件发布核回之后，views还需独立一次准入。
