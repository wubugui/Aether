# L source-runner-v2：只修原 runner 的三个缺口

2026-10-02 UTC。独立新 wrapper `cloudbank58l-source-runner-v2`；原候选、geometry、native adapter、材质、相机、原 freeze、原 source-v1 36文件和独审均未改。原包已发布 d9356dc5ee85e2846569332561e34ee9b9174f6e；本项只准备修复，**未准入或运行 Blender/Godot/native/source/views/render，未生成模型、.blend 或 PNG**。本项冻结后停止，先独审，再 GitHub 插件完整发布/远端核回，才可另行准入一次 source。

## 最小差异

- R1：在原完整 `native_support58l.validate_capture` 之外，逐份实际 raw 的全部主控制和 secondary 数值必须等于指定 probe 状态。其余控制均为 defaults；manual 必须全部 defaults；combined 必须原第一项 C01 的 exercise_value 加规定手工基底，实际 vertices 必须响应，并单独调用未改的真实 `geometry58l.validate_evaluated` 重算空间门。错误标签、错误/额外控制、额外 secondary、combined 未变化都拒绝。原 PID、法线/属性/材质/相机/Text、还原检查继续执行。
- R2：取消跨阶段宽泛 MUTABLE。新阶段只精确排除事先确认不存在的该阶段 terminal、它的原子写临时文件，以及 source 阶段唯一新 .blend。本次新 evidence 目录由 mkdtemp 唯一分配，才按目录排除。attempt 写好后纳入 before/after 全保护，且独立 SHA 在 child 前与最后重复核验。views 保护 source-attempt、source-terminal、source-launch-observation、source 原文件以及所有 prior evidence。旧 source-v1 的同名历史文件也不豁免。
- R3：`deadline58l.py` 是该单项的 Linux fork/wait4 外监督。worker 使用原 bounded_support58k 启动/管理 native；准入 wrapper_pid 是实际启动 native 的 worker PID。worker 的末尾 source SHA、完整保护核验、两份 flush/fsync/replace 阶段记录、末尾输出及真实退出全受同一绝对120秒门与外监督覆盖。外监督必须观察真实 worker exit0，检查总预算、无存活后代和两份记录 SHA，才能写监督收据。最后写收据也受 deadline，写完再检查时钟；顶层 CLI 到 os._exit 仍有硬 alarm，成功路径不关闭 alarm，也不再做成功磁盘写入。

默认仍 no-op。source/views 分别120秒，CPU2，build80/verify30/render27，分配 child 时原20秒收尾余量不变。原子进程支持仍 kill+reap；外监督异常也杀所拥有的后代并实际 wait4，失败证据保留。RSS 每次只读取自己的 `/proc/PID/status` 及该进程各 task 的 children 来递归本人后代，采样覆盖 supervisor+worker+native 全树；最后还用三层各自真实峰值的保守和卡 1,572,864 KiB。没有系统全局进程/环境/命令行读取或资源门扩大。

## 成功的准确含义与外部观察

避免“给最后一笔成功写盘无限补时间”的假闭环：

1. worker 写出的 run/wrapper-report.json 和本目录 source-terminal.json **始终 passed=false**。正常结果仅 `prepared_passed=true`、`state=awaiting_external_process_terminal`，不能单独当成功。
2. run/supervisor-terminal.json 记录真实 wait4 的 worker_pid/returncode/worker_observed_wall_seconds，及两份阶段记录 SHA。此处 elapsed 是实际退出被观察的时间，绝不是末尾 hash 前的截断时间。`receipt_ready_wall_seconds` 是收据写盘前观察点，不宣称已测自己的最终进程退出。父监督写完收据后再次测时并决定 exit code。
3. **还必须由真正调用者实际启动、等待整个 launcher，用自己的 monotonic 计时并观察真实退出。** 只认可 actual_exit_code=0 且整体 wall_seconds<120；不可用工具 wait 的等待时长、prepared 字段或 supervisor 收据单独替代。最后一个进程的实际结束由外部调用者观察，收据事后记录不反过来冒称原运行的完成时间。
4. 若失败、超时、异常、信号或证据缺失，source 不接受，原始记录保留。不重试一次性 source、不 fallback 旧 runner、不补写伪通过。

调用者成功核验后，在本目录新建 `source-launch-observation.json`（独立外部事实，不能由还没退出的 runner 自签）。最小结构：

```json
{
  "process_exit_observed": true,
  "actual_exit_code": 0,
  "wall_seconds": 0.0,
  "supervisor_pid": 0,
  "supervisor_terminal_sha256": "真实收据完整SHA256"
}
```

以上数字是 schema 示例，**不可照填**。wall_seconds 是调用前启动计时至实际 wait 完整返回，必须真实 >0 且 <120；supervisor_pid 是真实 Popen.pid，必须等于原监督收据。建议同时保存真实 command、启动/退出 monotonic、wait 状态和超时处理。views 的 prior_source 硬核此观察、对应收据 SHA/PID、worker真实终态、两份阶段原字节 SHA、source与attempt SHA及版本。外观察也进入 views 保护集合。

推荐未来执行方式：调用者使用 Python subprocess.Popen 执行下面唯一 command，立即记录真实 PID；从调用前的 monotonic 算剩余120秒执行 wait。超过120先请求 supervisor 终止让它杀/reap 后代；必要时只对本次拥有的进程做有界强杀/reap。任何超时/清理都记录失败，不能把清理时间当作成功预算扩展。不在此包加入另一个通用 observer 框架。

```text
PYTHONDONTWRITEBYTECODE=1 python -B source-assets/cloud-bank58/revision-l/source-runner-v2/run58l_v2.py --run-approved source
```

此命令在本准备中**没有执行**。运行代码本身不是发布或准入证据；必须先本项独审+完整外存核回。source 保存/fresh-open完成、外观察和全部产物又外存核回后，views 仍另行一次准入。

## 固定输入、原生与输出路径

不复制原2MB准备包，不造候选/模型备份。SOURCE_BINDING.json 以完整大小/SHA绑定原105 freeze输入、原freeze/manifest/SHA清单与独审共109个唯一原文件。额外4个已有本地 pycache 仅记录前后观察，不是需发布或恢复的依赖。FINAL_SHA256.json 加上本新包代码/文档/日志，独立冻结所有实际 source 依赖；绝不修改原freeze。

- 新 wrapper：本目录 `run58l_v2.py`，直接使用本目录 `deadline58l.py`
- 固定 native：`../source-v1/native58l.py`；实际命令明确引用它，不调用/导入被拒的旧 run58l.py 执行流程。测试中才显式导入旧 runner重现反证
- 固定 candidate/bindings/geometry/support：原 `../source-v1/`，字节不变；其嵌入 Text 仍绑定原文件
- 唯一未来 .blend：`../source-v1/cloud_bank58l.blend`，与未改 geometry58l.SOURCE/native admission 一致。它此前不存在，仅 source 明确准入后允许创建；不是修改任何旧文件
- 新一次性准入/阶段记录：本目录 source-attempt/source-terminal 与 views-attempt/views-terminal。任一版本已有对应 attempt/terminal 即停，绝不重新尝试
- 外部事实观察：本目录 source-launch-observation.json
- 本次唯一新 evidence：`cloud-evidence/cloudbank58l-source-runner-v2-{stage}-{UTC}-{unique}/`；含 outputs、原native/process/log/raw、保护清单、两层终态与退出意向；没有原包冗余备份

## 实际回归与边界

最终 normal 与 -O 各42项全通过（6.371/6.475秒，exit0）。全程显式禁止 support.run_child，真实短进程测试只 fork Python 的写盘/超时函数，**不是引擎或原生成功**。测试包括：

- 原R1完整合法四面体raw八标签复用+combined不变，旧runner真实接受，新runner拒绝；正确八probe+manual+combined用未mock的完整raw validator通过。fixture几何 oracle 清楚标为fixture，不充当候选几何证明
- 原R2确实漏source两文件，新保护集合覆盖source、当前admission、旧证据，并只允许精确新输出；符号链接拒绝
- 原R3从旧文件逐字提取尾代码，原119.9+1.6=121.5仍passed=true；新外监督在实际worker迟至121.5退出、或119.9再花1.6进行收据收尾时均失败；fsync异常失败。真实短Python正常两次耐久写入后wait4，及超时强杀/收尸也验证
- 复用原完整正常raw与篡改拒绝、实际既有候选各控制/手工/组合空间门、非累计/还原、PID、no-op、once、原caps等。沒有重写几何算法或全J_i

第一次本地测试在合成 wait4 mock 被错误设为无限返回而未结束，已中断，保留 tests-normal-attempt01.log；修正的只是测试mock返回序列，随后40项初步通过的 tests-normal-attempt02.log保留，最终42项两模式日志另存。未运行或修改任何原生文件，不把测试脚本问题冒称原候选/engine失败。

原候选11有限状态通过的含义不扩大；PCHIP/PL及实际float32非零误差保留；contact_acceptance=false、world_acceptance=false、global_GOAL=false，视觉/天气亦未验收。此小包完成即冻结，不延展造型、全接触或native工作。
