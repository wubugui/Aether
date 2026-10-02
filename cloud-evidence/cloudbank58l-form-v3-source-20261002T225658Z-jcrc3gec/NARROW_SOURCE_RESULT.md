# Form-v3实际source窄独立复核

2026-10-02 23:02 UTC。结论：**本次真实build、独立fresh-open与内存编辑恢复的API诊断链成立；原corner数学门仍失败，不能升级为full_native或视觉/世界/GOAL验收。**

复核先读CLOUD_RESUME/GOAL及本包入口，只读取既有实际文件，并使用既有官方bundled Python 3.11.15以`-B`导入原`run58l_form_v3`，调用一次`prior_source(g)`，耗时**15.028426164994016秒**，通过。未调用observer/main、未消费准入、未启动Blender/Godot、未保存源、渲染、改形、Git或Slack。本复核只新增本文。

## 真实进程与完成权威

- 外部caller 2实际Popen/wait launcher **5**，exit **0**，**73.12697763800679秒**；观测UTC为22:56:43.363594至22:57:56.491146。无timeout、caller/cleanup错误、kill信号或残留，`remaining_owned_pids=[]`
- supervisor 5实际wait4 worker **6**，exit **0**，**72.97920543600048秒**，`all_owned_children_reaped=true`；完成权威为真实wait4加launcher exit0，不能拿worker的预写终态冒充完成
- build native **7**，parent 6，starttime 12122264，exit **0**，**13.947567101000459秒**；verify native **29**，parent 6，starttime 12124453，exit **0**，**13.357884974000626秒**。两者独立PID/注册记录、实际命令、CPU2、原native terminal和raw PID均匹配
- 原总120秒、CPU2、build80/verify30、aggregate1.5GiB及20秒尾余量保持。实际build分配75.99492927800748秒，verify30秒；全树采样峰483880KiB，三层保守峰561672KiB，未触发超时/RSS门
- supervisor终态SHA `be9cc9beff4bf8c4430881cbf53e551abff9fb06842ca1fe81fae89b1092ddbc`；worker终态与wrapper原文件字节相同，SHA `3db4b539b17aeb0fa9c764adfb3188ef8a9bc6effdfa9009919f9667d587db78`
- 原source-terminal仍正确记`passed=false/state=awaiting_external_process_terminal`；最终supervisor及外观察验证才通过。原source-launch-observation的`source_chain_verified=false`是当时尚未重放的事实，独立validation绑定external-result的SHA；external-result的完整combined_evidence与本次重放结果精确相等，最终`source_chain_verified=true`

## 文件、保护及原生编辑证据

唯一新源为`source-assets/cloud-bank58/revision-l/form-v3/cloud_bank58l_form_v3.blend`，**324179B**，SHA256 **`c36c7517ed10540cda20bbd849f35f0e449595a96e960cc60c52ba00f4747e4c`**。admission、worker、supervisor、两个native terminal及external-result均绑定该身份。build events有且仅有一次save.complete；verify没有保存事件，实际opened_filepath为此源。run内**0 PNG**，无render/export事件。

本次亲读并重算完整原oracle：每阶段21态（baseline、7主控制和1谷宽的8组moved/restored、manual/combined/manual-restored/baseline-restored），共**42态**。完整报告和exercise的逐字段精确相等门通过，无新容差、rounding、向量改写或夹值；每个规定控制实际改变网格，指定恢复回原numeric identity，manual +0.125m保留、组合控制有响应、最后恢复基线。实际1567顶点/3130三角的原闭壳、定向、正厚、非自交与真外岸80m规则按原实际几何门重算通过。

build与fresh-open的完整numeric identity相同（仅原函数排除pid/cpu_affinity/opened_filepath）；这**不是raw文件字节相同**。原build-raw SHA为`3c9a563225a3e0205dec2caee37521169756489b2e7183dbf4654b298e01113b`，verify-raw为`55e5fdc09ac82bb07e3779202d76e79743e0f74930b638b032066e4c694547cc`；各原raw字节分别由本次66个native输出SHA完整集合绑定，恢复态也保留自己的原文件身份。

8个内存Text为BINDINGS58L、CANDIDATE58L、EDIT58L、GEOMETRY58L、NATIVE58L、NATIVE_SUPPORT58L、POLY58K、README58L。全部42态中的名称/长度/SHA/内存与非自动运行标志符合原expected_texts；落盘embedded-text-inputs逐字节等于原期望，8份readback大小/SHA亦核同。

`protected-before.json`与`protected-after.json`完整文件字节相同；含**14671文件、4810140898B**。复核又逐文件读取当前内容核SHA，**0变化/缺失**。833项冻结输入含FINAL自身核同；SOURCE_BINDING中790旧文件及28旧准入/终态全部按大小/SHA核同，旧成功、失败、raw、图和源没有被此次复核覆盖。

## 本次新corner数学门仍失败

原阈值仍为**3e-5**。build和fresh-open各自21态的结果一致：

- 新默认baseline及全部8个控制恢复态：**24面失败**
- C01主冠moved：27；C02：24；C03：24；C04：24；C05主谷value：25；C06腹：30；C07中尺度：26；C05谷宽：24
- manual：24；manual+control组合：27；manual-control-restored：24；最终baseline-restored：24
- **42/42态均未过原corner→数学几何门**；每态最大绝对差均为**0.0005249128728819219**，最大角差均为**0.03410575291451074°**

polygon→数学几何、单位长度、朝外、flat三角三corner相等及corner→float32-Newell API诊断门分别通过；不能用它们替代上述失败标准。历史最早默认22面失败与form-v2默认23面失败仍独立保留，不能把它们误写成当前默认24面，亦不能把当前API诊断通过倒填成旧source成功。

## 范围与下一闸门

三次历史source失败与form-v2原整体`original_source_stage=failed`保留；原真实成功build、后来fresh-only及views仅作为已绑定前件。本次只成立可编辑诊断源的真实保存、fresh-open与指定内存恢复，不证明任意参数组合，也不证明肩团可见或造型改善。`full_native/visual/contact/world/weather/global_GOAL=false`，世界默认未动。

本次模型、完整实际成功/失败记录、本文和进度入口仍需先经GitHub插件全部发布并实际远端完整核回；之后才可另做最窄原机位views适配并以真实图像判断。本文不替代该外存闸门，也不授权重复native/source或直接渲染。
