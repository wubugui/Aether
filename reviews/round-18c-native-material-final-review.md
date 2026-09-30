# 18c 原生材质最终有界审查：支持保留；原失败与恢复通过分别保留

支持保留18c原生地表材质作为当前阶段底稿。本次安装范围、原始产物身份、报告时序和恢复包绑定经独立核对成立；结合此前实际看过的四张原生GPU图，材质增量及17e已有局部进展保持。该结论不表示原运行变成passed，不表示发布完成，也不表示新增20张多时段/天气场景目标完成。

原始运行：`E:\FeiTing\captures\validation_runs\18c-native-material-20260908T062423Z-e13cc07350264b9d800603025868e010`。

恢复包：`E:\FeiTing\captures\validation_runs\18c-material-evidence-recovery-20260908T063226Z-ce87559c6bcd43c188f89f7c2d233c20`。

独立核验数据：`E:\FeiTing\reviews\round-18c-native-material-final-audit.json`；前期实际四图与差异记录：`E:\FeiTing\reviews\round-18c-native-material-preliminary-review.md` 及同名preliminary-audit.json。本代理未启动GPU、引擎、飞行或全量工作区校验，只读取本次绑定产物并核对必要安装文件。

## 失败记录与恢复证据

原manifest仍为failed，error仍是 `stream-test: missing or stale report`。八个底层引擎进程均exit0；前七阶段passed，stream阶段的收集状态仍failed。原冻结收集器期待 `stream-validation.json`，生产脚本实际写 `stream-flight-validation.json`。独立比较恢复包corrected-collector.py与原冻结收集器，唯一文本差异就是该文件名。未将其他失败改成成功。

恢复manifest为passed，stages为空、engine_stages_reexecuted为0。读取恢复程序可见它验证并复制原产物、绑定正确的现存stream报告，没有调用引擎阶段。恢复包251个绑定文件SHA全部独立重算匹配；复制的原产物逐一与原文件及原manifest的SHA一致，original-failed-manifest.json与原manifest字节一致。恢复开始时间06:32:26 UTC晚于原运行完成06:28:05 UTC，原失败证据没有被覆盖。

stream报告仍携带原run_id而非恢复run_id，所列源SHA全部对应原冻结inputs。报告时间06:27:58 UTC及保留的mtime 1788848878787478600ns均位于原stream引擎执行窗口1788848824149161900至1788848879135020100ns内。原stdout含east/west/north/south各自PASS与最终STREAM FLIGHT PASS，stderr为空。原冻结后的七阶段输入SHA都绑定同一inputs文件。因此恢复报告来自已完成的原始飞行，不是旧结果借用或新飞行替代。

## 底层结果

| 结果 | 独立确认 |
|---|---|
| 材质持久化 |7项全部passed；原run_id、运行脚本SHA及World SHA匹配冻结输入|
| 游戏 |36项全部passed；原run_id、报告时间及源SHA匹配|
| 四方向流式飞行 |east/west/north/south全部passed，250采样全部地形及碰撞已加载，缺失0|

四方向实际距离分别4068.50、4004.02、4015.53、4062.69m，总计16150.73m，生成352个地块。每段只在起点设置位置，其余为连续物理飞行；不是四段无缝单次飞行，也不是逐路点传送。这些是父代理引擎产生、由本代理读取核验的结果。

7项材质结果覆盖保存/重开后选定材质、世界启动保留艺术材质、其他208原生地块默认材质、生成地形使用同一原生地面材质、非地面scatter继续用独立world材质等。本次无Windows导出，不作打包发布声明。

## 安装差异与保留对象

重新从准备前及冻结后inputs计算差异，恰为213项并与preparation-changes一致。其中208个地块场景逐文本核对都仅将材质路径 `res://materials/world.tres` 换成 `res://materials/terrain.tres`，其模型、碰撞及变换文本保持；备份SHA匹配准备前、当前SHA匹配冻结后。

另外5项为materials/terrain.tres、scripts/terrain_native.gdshader及其uid、scripts/open_world.gd、tools/verify_native_terrain_material.gd，当前SHA均匹配冻结值。运行代码给生成地形使用TERRAIN_MATERIAL；独立world材质继续用于其他对象。native shader与已审18c候选字节相同，SHA为 `f98fc817bb6c217870144daff7d53a0ecb1da96e29e6b2315a24301aea858384`。

冻结前后416项地形资产、238碰撞资源、78模型记录、1546项scatter和World场景SHA全部未变。本次未重新扫描这些全部当前资源；前期已针对五件cliff GLB、17e重贴地岩石及world材质核对当前身份保持。本次是地面材质接入，未重做17e岩体或再挪动岩石。

## 实图结论及后续边界

本轮实际已查看原运行images目录的opening.png、cliff-side.png、cliff-back.png、reverse.png，恢复包绑定的四图与这些原图SHA相同，故无需重新捕获。生境绿色/黄绿区域与清晰角面保持，17e宽草肩、暖壁主次面及重贴地岩石保持；反向左中局部仍有碎面拼片倾向，原有地形/植被/聚落造型不足继续存在。

原生相对18c候选不是逐像素相同，候选基底仍16g，当前基底17e；前期记录了opening/side/reverse的17210/63584/83123个不同像素。不能把全部差异都解释成17e前景修改，反向还存在地表差异及小幅通道差，具体原因未确认。当前实图支持本轮局部保留，不撤销这一不确定性。

原运行failed、恢复包passed、底层有界结果通过这三个事实分别保留。全世界统一美术与20张多时段/天气参考场景仍按新权威目标继续实施，不能以本次材质接入结束完整目标。
