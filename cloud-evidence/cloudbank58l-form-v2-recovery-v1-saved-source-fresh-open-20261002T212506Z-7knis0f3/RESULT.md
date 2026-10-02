# 现有 form-v2 诊断源独立 fresh-open 与内存编辑恢复通过

2026-10-02 21:25:05.425039 UTC启动。准备已由插件发布 `1ce6a139a3f46693d506a257eea2c76e8fb843ce`，21路径/20唯一blob完整远端逐字核回后才一次准入。

## 有限真实结果

本次 `saved-source-fresh-open` 独立阶段通过：官方Python3.11观察/验证，Blender只重新打开原已保存源并进行内存控制/手工编辑及恢复。**没有build、save、render或export，0PNG**。

- launcher6真实exit0，总36.822512601997005秒；worker7真实exit0/36.55012605400407秒；实际verify PID8 exit0/13.933329271007096秒
- CPU2、native原30秒界、全阶段120秒、1.5GiB均保留且未触发；native峰326892KiB、全树采样峰414924KiB、保守三层峰和487868KiB。自有后代全回收，外观察remaining_owned_pids=[]
- 唯一源仍 `form-v2/cloud_bank58l_form_v2.blend`，324985B、SHA256 **33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a**，全程before/after保护及显式SHA均不变。没有生成第二模型或重新构造
- 14478项运行期保护、4735760197B的before/after原记录相同；642冻结输入保持。实际21个完整raw、原8 Text、七主+谷宽/manual/combined及数值/结构恢复完整核实
- [窄独立复核](NARROW_RECOVERY_RESULT.md)在官方3.11下只读调用prior_recovery()成功（7.855秒），完整实际进程/PID/command/SHA/输入与raw/exercise精确比较过。原stage失败不会被此调用修改

## 历史状态与比较口径

原form-v2 source整体仍是failed：其唯一build实际成功且一次保存，但Python3.12派生统计的末位差使原外层精确报告门失败。本次保该原记录，组合“原真实成功build + 本次真实fresh-only成功”得到existing_saved_source_fresh_open_verified=true，original_source_stage='failed'仍明确。

本次固定已有官方Python3.11.15，沿用原全部精确报告比较，**未新增容差、rounding或改变实际向量/raw**。原报告中的三个派生统计在同3.11运行环境精确重放；旧3.12的43处差记录仍在。原v3监督保持，仅局部libc pidfd兼容桥支持缺失的Python绑定。

恢复identity是原定义下的数值/结构相同，不宣称不同时刻整份raw字节相同；PID、opened_filepath、某些数值JSON类型可不同，全部原字节各自保存。原8内嵌Text与.blend文件SHA精确不变。

API一致性诊断通过不改旧几何要求：本form-v2默认旧corner→数学几何3e-5仍23面失败/max0.0005249128728819219/角0.03410575291451074°，历史旧L默认22面另保留。full_native、visual/contact/world/global_GOAL均false。当前没有本form-v2的新图，因此不认定形体改善。

## 外存与下一步

23大JSON原路径保14唯一gzip流/15个普通Git部件5291924B，同次相同恢复状态/保护manifest只存一套原字节。原源已经上一提交直接保存，本run不复制模型。所有真实过程/成功与未达旧门范围、原观察及四新恢复记录、复核和权威入口完整外存。

插件全部发布并实际远端核回、新空目录恢复解析23原JSON之后，下一只做原固定机位views的窄适配，使用上述真实组合前件，不能调用或伪造原已失败source的成功路径。views准备也先发布核回再真实图，不改变已存模型/几何/材质/光照/相机。
