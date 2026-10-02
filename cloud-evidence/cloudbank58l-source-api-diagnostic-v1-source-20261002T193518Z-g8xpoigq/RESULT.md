# L 首份 API 一致性隔离诊断源已真实保存及 fresh-open

2026-10-02 19:35:18.428116 UTC 实际启动。准备 `f23d427ab4b4d0b0322a4d052d72d5791688ec0d` 已完整插件发布/22路径逐字节远端核回、窄审接受后才运行。

**本项有限结果成立：API 隔离诊断源可编辑保存及独立 fresh-open 恢复通过。** 尚未渲染；0 PNG。原 corner→数学几何3e-5门仍失败；full_native_acceptance、视觉/接触/世界/全部GOAL均false。

## 原生源与实际过程

唯一源：`source-assets/cloud-bank58/revision-l/source-api-diagnostic-v1/cloud_bank58l_api_diagnostic_v1.blend`，**319519B**，SHA256 **7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7**。本文件直接按原字节普通Git blob保存，无LFS或恢复分块，不是占位指针。

- 外调用方真实Popen/wait：launcher6 exit0，总59.299956210001255秒；worker7真实exit0/59.22318726600497秒，全部阶段字节链复核通过，remaining_owned_pids=[]
- 官方Blender4.5.14 build PID8 exit0/15.097158213000512秒，真正一次保存；独立fresh-open PID30 exit0/14.70170624399907秒，无第二次save
- CPU2，native峰325496KiB；全自有树采样峰415088KiB，保守三层峰和458528KiB。120秒总界/build80/verify30/1.5GiB门未触发，无timeout/SIGKILL；15秒native与59秒总体差包含保护、独立完整raw复验和终态写盘，不全归于渲染
- 14154受保护原文件共4584610202B的前后manifest字节相同；295冻结输入同；66原source输出的完整SHA绑定。两旧失败及其准入原字节仍保留，新准入一次消耗，禁止删除重跑
- 1567顶点/3130三角、一个共享master/export网格、七组和八个非自动执行内嵌Text真实捕获；七主控制+一个谷宽次控制、manual/combined/restored实际执行，两次source进程均有独立实际raw，包装层重新计算完整几何与API诊断验证

## 身份比较的精确范围

[窄结果复核](NARROW_RESULT_REVIEW.md)直接只读调用原prior_source与两套validate_exercise（14.079秒），实际stage/PID/command/SHA和控制/manual恢复链通过。

这里的原identity定义是排除pid、cpu_affinity、opened_filepath后的**数值/结构相等**。build与fresh的控制C01 value存在1005.0→1005的JSON数值表示差，manual恢复也有这种差异；不能称整份raw字节或数值类型逐位相同。原始raw未归一化/重写，每一不同字节版本全部保留并各自SHA存储。真正保存的.blend文件在fresh-open前后SHA相同。

## 法线结果与旧失败继续公开

实际默认polygon→几何最大差2.7049721644800684e-06，flat/三corner相同/向外/单位长度门过；corner→float32 Newell最大差5.960464477539063e-08。每控制和手动状态都重新检查并保留单独结果。

**原默认corner→数学几何3e-5仍22面失败，最大分量差0.00015941344933428914，最大角差0.009158468662372497°。** 各编辑态超限面数量可不同，历史默认失败不可被新模式或某态true抹掉。源内scene/README、raw、child/worker/receipt均明确API诊断scope及full_native_acceptance=false。

## 完整外存与下一步

44个大JSON原路径合计包含27唯一字节对象。14唯一gzip流15块5276689B；13份fresh数据只以已存build字节对象加明确PID/打开路径literal byte splice表达，最终全文件SHA/大小严格核实。相同restored/保护manifest只存一份表示，详见[STORAGE.md](STORAGE.md)。其它日志、实际调用方脚本、原进程/阶段证据和Text输入直接保存。

先将本模型/全部真实成功和未达旧门记录/复核与权威入口完整插件发布，远端逐字读回并从远端存储包新目录恢复44原JSON。之后才一次四原固定机位诊断图，不重新构造源，不改材质/相机或替换世界。若图像造型仍不理想照实打回；本工程结果不等于艺术或全部GOAL验收。
