# L 恢复源第二次实际运行：旧 corner 几何门失败

2026-10-02 18:38:36.925755 UTC 启动。准备已由 GitHub 插件发布并完整核回 `c9c4a2dd98d38810efd62315afb76f625c3b35da` 后才运行。本次不是新视觉成果：**0 .blend 保存、0 fresh-open、0 PNG**。

## 真实终态和保护

- 调用方真实 Popen/wait：launcher PID28 exit1，15.955015258994536 秒；worker29 exit1，15.843376027987688 秒
- Blender4.5.14 build PID30 exit1，2.0063839909998933 秒，CPU2 affinity[0,1]；native 峰284300KiB，全自有树采样峰347312KiB
- 未触及120秒总界、80秒build界或1.5GiB门；全部自有后代真实回收，外观察 remaining_owned_pids=[]，没有后续 engine 自动运行
- 14081 个受保护原文件共4573863631B前后完全相同；222冻结输入同。归档前再次逐文件SHA读取核实，见 `preservation-audit.json`。墙钟包含全仓前后保护，不能全归于 Blender
- wrapper/source-terminal、admission、supervisor receipt 与外调用结果的原字节SHA关联均核实；source 缺失，所以 saved_source_unchanged=false 不是旧模型受损

## 两处修复真实成立

共享唯一mesh的master/export实际均恰好七个原名控制组，不再各自创建重复 .001。真实采样 pixel_aspect=[1.0006932020187378,1.0]，四相机 P00 均0.9366548657417297，与冻结原投影相同；capture 使用实际 render RNA。其它几何/姿态/材料未改。

## 原 native 门拒绝

原 `native_support58l.py:196` 正确拒绝 `Actual outward flat polygon/corner normals`，阈值仍3e-5。原 raw 1510879B，SHA256 `0b39aa841519b65874e24d219c4e74d3063daa8dfd9bdf86b15fdb90e9b5a99c`；失败 raw 与它逐字节相同。1567顶点、3130三角及8个真实内嵌Text读回已记录，但运行在保存/控制实验/独立fresh-open之前停止，不能推定后续门过。

[逐float32只读诊断](normal-diagnosis.json)和[窄复核](NARROW_REVIEW.md)确认：Blender polygon API 的三角叉乘与 flat corner 缓存的 Newell 算法存在实际float32舍入差。所有corner与Newell重放最大差5.960464477539063e-08；旧/新法线位型相同，非本次组/投影修复造成的新几何变化。

**旧 corner→数学几何 3e-5 门仍失败：22面，最大分量差0.00015941344933428914、最大角差0.009158468662372497°。** polygon→几何最大差2.7049721644800684e-06；每面3corner完全相同且所有面flat，最小归一化dot0.999999987224719，长度误差最大1.3277417698631666e-07。API一致性绝不能取代或冒充旧几何精度验收。

## 存储与下一步

原日志、真实调用方代码、过程观察、Text输入及读回、两种诊断与阶段记录全部保留。[STORAGE.md](STORAGE.md)说明四大JSON只存两个唯一无损gzip流，重拉必须恢复原字节后重放；无LFS、无额外项目备份。

先完整插件发布本失败和入口并实际核回/新目录恢复。之后另立“API一致性隔离诊断源”模式准备，保留本次旧门失败、不改几何/机位/原阈值掩盖差异；准备也先外存再实际保存。现无可看的新源图；完整源/视觉/接触/世界/全部GOAL仍未通过。本次一次准入保持消耗，禁止删除记录直接重试或接views。
