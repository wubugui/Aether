# API 隔离诊断 source 结果窄复核

复核时间：2026-10-02 19:42 UTC。仅检查本次 source 的既有文件、进程记录、SHA 与 raw；未启动 Blender、engine、save、render 或新测试框架，未修改原 raw、终态、模型和历史失败记录。

## 结论

**可以诚实表述：API 隔离诊断源可编辑保存及独立 fresh-open 恢复通过。**

这是 `api_consistency_isolated_diagnostic_v1` 的 source-only 结果。`full_native_acceptance=false`，旧 corner→数学几何 3e-5 判据仍失败；没有 source 视图渲染、视觉、contact、world、weather 或全局 GOAL 验收。本复核不新增 formal 门，不展开全 J_i，也不声称穷尽任意编辑值。

## 实际执行链与保存源

- 准备提交：`f23d427ab4b4d0b0322a4d052d72d5791688ec0d`，与外层 observation 的 publication commit 相符
- 外层实际命令：Python `-B .../source-api-diagnostic-v1/run58l_api_diagnostic.py --run-approved source`；launcher PID 6，真实观察退出码 0，总墙钟 59.299956210 秒，低于原 120 秒上限
- supervisor 的真实 wait4 记录：worker PID 7、退出码 0，59.223187266 秒；全部 owned children 已回收，无 timeout / RSS 越限 / 遗留 PID
- build PID 8：15.097158213 秒，exit 0，原 80 秒 cap；verify PID 30：14.701706244 秒，exit 0，原 30 秒 cap。两进程独立，CPU affinity 均为 `[0,1]`
- 两条实际 native 命令均为已冻结 Blender 4.5.14：`--factory-startup --disable-autoexec -b -t 2 --python-exit-code 1 --python .../native58l.py -- --mode build|verify --out <本run>/outputs --admission .../source-attempt.json`。逐项与原 native_command 生成的命令一致
- build events 记录唯一 save；verify events 记录 `fresh_open.complete` 与精确源路径，没有 save / render。模型实存 319,519 bytes，SHA256 `7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7`
- 原 wrapper/source-terminal 保持 `awaiting_external_process_terminal`、`passed=false`、`prepared_passed=true`，不能单独当完成凭据。实际完成由 supervisor-terminal 的 completed/pass 和外层实际 launcher exit 0 联合确认

## 原记录只读重算

实际调用原已审 `prior_source(g)` 成功，耗时 2.393 秒；它重新读取并绑定完整 admission、terminal、wrapper、observation、source SHA/size、命令/PID/CPU/限额、所有 source 输出 SHA、两个完整 raw 的 `validate_native_raw` 和 independent fresh-open numeric identity。

随后实际调用原 `validate_exercise`，分别重算 build、verify，结果与原 wrapper 的两项 exercise 完全相等（5.808 / 5.758 秒）。包括：

- 每阶段 7 主控制 + 1 次参数的指定非零值：实际位置响应、完整 raw、还原状态及 geometry 复验
- 顶点 374 的 `[0,0,0.125]` 手工偏移、叠加首控制、撤销控制保留手改、再撤销手改回到 baseline
- 共 42 份完整 raw 快照；每份实际基线 mesh 有 1,567 vertices、3,130 triangles、3,130 polygon normals、9,390 corner normals，12 个完整属性，14 objects、7 controls、4 cameras、8 embedded Texts。8 份 embedded Text readback 原记录在场且 SHA 绑定

**identity 的措辞必须保留原定义。** 原 identity 排除 pid / cpu_affinity / opened_filepath，使用解析后 Python 数值等值。build 与 fresh-open 的完整 raw SHA 本来不同；除 PID/path 外，C01 default 还存在 `1005.0` 与 `1005` 的 JSON 数值表示差异。手改/控制还原也可能保留数值等值而不同的表示。因此可称「原定义下完整 numeric identity 恢复」，不可称「全 raw 字节相同」或「所有数值存储类型/符号位逐位相同」。原字节均保留，未归一化写回。

## 保护与历史失败

- 原 protected-before / protected-after 各 14,154 项，映射与文件字节完全相同，双方 SHA256 均为 `1427a38240fd4eb289a019f231ca20395be9ef8c417ac7e341454b46be0a57bc`
- 19:41 UTC 又实际重哈希全部 14,154 项（4,584,610,202 bytes）：0 缺失、0 SHA 变化；295 个 frozen input 亦全部当前 SHA 相符。以后合法的 CLOUD_RESUME 进度更新应与这些原时点记录分开解释
- 实际调用原 `diagnostic58l.original_failures()` 成功；两次旧失败 admissions 仍为 `3fc9d27fe46f83fc279b0902a852ac895c8c59a2d77e93f66a1fa651c5fee597`、`b8cc9985e206be4fc8f69b80c6e51ebebccaac4e8b1eb177ad6ced4784efe814`；旧失败终态及其完整文件 SHA 未改，旧失败源文件仍不存在
- source raw 基线的旧 corner→数学几何 3e-5 指标，另以实际三角形坐标 cross-product 独立重算：build 和 verify 都是 **false / 22 faces**，max abs `0.00015941344933428914`。索引均为 `12,13,682,726,727,729,1198,1344,1403,1404,1435,1576,1577,1578,1870,2291,2292,2293,2294,2609,2610,2763`
- 新诊断的 polygon→geometry max abs `2.7049721644800684e-06`；corner→float32-Newell API max abs `5.960464477539063e-08`。它们通过不能替代或改写上面的旧失败

## 关键证据文件 SHA256

- `supervisor-terminal.json`：`75e2a09995b9a8a69b3137dd9f5f8aeb07fa238ca2fdee7dc18d608ec68be2ca`
- `wrapper-report.json` / 源目录 `source-terminal.json`：`0cc6e5196331de976b884f833634094afd5fa0f6bfc01b2d783e7aeabee6b128`
- `outputs/build-raw.json`：`5800ecafbe1829e75753d5312cc629dc8d2fdb3cd25db64b61ca44c7f1981541`
- `outputs/verify-raw.json`：`e0950c026d38f46a136a9e6f26bdf65f5a3aba25ced33fcb3fea19fe6abb1c4d`

无阻断该窄结论的问题。后续无损归档/发布由主任务处理；本报告不把尚未复核的归档或 Git 发布结果算入完成范围。
