# 17e 原生集成独立审计：支持保留当前局部生产底稿

两件已审的17e原生资产及其派生资源身份一致，11项实际变更符合本次范围，完整12阶段通过，四张实际GPU原图保住候选的局部造型进展。支持保留当前17e western_slab/front_columns生产底稿；其余16g已集成部分继续保留。完整还原目标仍未完成。本审计不把新增加的ref目录20张场景目标纳入已完成范围，也不将18c临时材质研究视为已集成。

运行：`E:\FeiTing\captures\validation_runs\17e-native-integration-20260908T060301Z-07dc7a9c264c45aab408ab67177a7dfd`。独立数据：`E:\FeiTing\reviews\round-17e-native-integration-independent-audit.json`，复核脚本：`E:\FeiTing\reviews\audit_17e_integration.py`。本审查未启动Godot/Blender、未修改生产源。

## 源、派生资源及变化范围

独立重算64个run绑定文件SHA均匹配manifest；12阶段均passed、exit0；冻结后的10阶段均绑定本轮inputs.json同一SHA。两件当前GLB/blend与此前已实际审图的17e冻结候选逐SHA一致，run/source-backup中的原GLB/blend与preparation-inputs原SHA一致。kit顶点/面/体积与候选匹配。两件当前mesh和collision资源SHA与本轮冻结值一致，原生prefab文本未改变且引用对应模型及碰撞。闭合/rim/floor证据复用已审的相同GLB身份；没有重复渲染或相交扫描。

| 资产 | GLB SHA256 | 三角 |
|---|---|---:|
| western_slab | af3c37cca1f4019fbbfa7920da528cbd99f2f2501884105cb7ddd5d8c2842856 |312|
| front_columns | 0c798b85a75abc891cd1764f34ae5c719ddf9a43a69996adc812a2b99773950c |352|

重新从准备前/冻结后inputs计算diff，恰好11项，和preparation-changes完全一致：2 blend、2 GLB、2 mesh、2 collision、asset_catalog与cliff_kit两catalog，以及 `assets/scatter/Grounded_rock_0_-1.res`。没有新增非cache输入。World场景与208地块场景冻结SHA未变，并已复查当前文件；其他1545项scatter冻结SHA未变，本次没有重复扫描这些全部当前资源。

本轮刷新日志为2个prefab/2个实例、terrain updated 0、1组中1个scatter实例重贴地、removed0。日志把scatter泛称foliage，但唯一变化资源名是散布岩石，不能写成移动了一棵树。岩石资源准备前SHA `49b162b6d73e600a9ad01e089b6f2a760081044f7faff609508c0375c6ec3b0b`，冻结后及当前SHA `bb1b91de0e9e389d1d6d2295059ad14d4fa3bbb21e0b2307751facc683309e1a`。精确实例变换需结合父代理另行读取的MultiMesh记录；本次独立审计不从截图推算位移米数或宣称已解码该二进制资源。

## 实际四图与差异

实际查看本run的 `images/opening.png`、`images/cliff-side.png`、`images/cliff-back.png`、`images/reverse.png`。对照候选run `E:\FeiTing\captures\validation_runs\foreground-17e-20260908T055006Z-348ac27ec16f49c6bc196accd90eba32` 的三张原图，重新计算差分如下（bbox含端点）：

| 视图 | 不同像素 | 最大通道差 | bbox |
|---|---:|---:|---|
| opening |1121|76|[1233,689,1268,742]|
| cliff-side |3226|81|[627,542,678,624]|
| cliff-back |1839|81|[202,93,962,416]|

开场与侧面差异集中于同一个可见散布岩石原位置与新位置。原生侧图中岩石现在落在左草肩表面，未见明显漂浮；宽草肩和暖壁主次面整体保持。差异框外的相同像素支持本次未改变主要资产外观，而不能据此写三张图完全相同。

背图进一步分区：y<300的1546像素位于[202,93,616,226]上部远景；y>=300的293像素位于[944,387,962,416]近岩群上缘。后者与岩石所在方位一致；上部远景差异原因尚未确认，不能把它也归因于岩石重贴地。reverse没有17e候选同视图，只审当前实图，不声明相等。

17e原有侧肩尖折、大盾形暖壁、后缘陡窄面仍可见，未因集成而解决；也没有观察到本轮新增整体穿洞、严重脱地或大范围造型回退。阶段保留的理由仍是前部真实宽肩、克制草色及暖壁主次面改善，非完整美术验收。

## 同轮功能与结构证据

六份结果报告全部passed，报告run_id及所列源SHA匹配冻结inputs：36项game checks、6个cliff-tour路点、21项cliff contact、4472个rim采样、40642个road采样、18件geology资产。cliff-tour持续物理飞行约1127.35m、相机遮挡采样0、health/shield均1。geology所有GLB身份匹配当前文件。

本轮五件section表面门禁均passed，门禁文件SHA匹配manifest绑定，五件GLB又与冻结和当前源三方匹配。派生碰撞已更新且原生接触报告通过；没有宣称独立二进制重建了collision面集。未执行Windows导出，以上是本次原生工作区集成证据，不是打包发布验证。

结论只支持保留当前局部底稿并继续后续场景工作。新的多时段/天气、20张参考场景与整体统一风格目标均保持未完成。

## 补充：散布岩石GPU只读证据已独立读取确认

父代理执行了 `E:\FeiTing\captures\verify_17e_rock_refresh.gd`；本独立审查代理没有启动GPU。已读取 `E:\FeiTing\reviews\round-17e-rock-refresh-verification.json`、`E:\FeiTing\captures\round-17e-rock-check.stdout.log` 与同名stderr日志。stdout包含Godot/OpenGL设备信息及PASS，内嵌JSON与报告完全一致，stderr为空；脚本成功路径以quit(0)结束，父代理报告实际exit0。

结果明确为asset_kind=rock、30实例中仅index2在脚本近似比较下有变化。局部Y由62.27490234375降至54.01611328125，下降8.2587890625m；局部XZ数值不变，basis通过is_equal_approx比较，XZ断言阈值0.0001m。新世界位置为[114.664001464844,54.01611328125,-26.5659790039063]。当前原生collision ray记录接地误差0m（脚本门限0.01m），支持截图中岩石落到真实草肩的判断。

已独立重算原备份与当前资源SHA，分别匹配报告的 `49b162b6d73e600a9ad01e089b6f2a760081044f7faff609508c0375c6ec3b0b` 与 `bb1b91de0e9e389d1d6d2295059ad14d4fa3bbb21e0b2307751facc683309e1a`。该证据补齐前述变换读取边界，不改变背图上部远景差异原因尚未确认的结论，也不扩大整体美术验收范围。
