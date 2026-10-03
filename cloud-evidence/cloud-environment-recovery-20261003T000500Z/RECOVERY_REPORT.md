# Aether 新云环境原字节恢复报告

核验时间：2026-10-03 00:03 UTC。仓库起点/终点均为 `7c52378d53bc6c1e79339b4ec869061d398d3e53`。本报告只记录字节恢复和静态核验；没有启动引擎、生成新源、消费准入、重跑旧实验或改动任何 tracked 文件。

## 实际恢复

- 44份已存在的精确恢复合约，共恢复249个原路径、517,716,062字节；245个JSON也完成解析
- 所有恢复路径均命中仓库已有ignore规则；没有新增或修改ignore规则，没有不同内容覆盖
- 逐块、拼接压缩流、精确字节splice、完整原文件长度与SHA256均核验通过；恢复后再次读取实际文件核验，零错误
- 使用已审的原 `restore_storage.py` / `restore_native.py` / `restore_reports62.py` / `restore_grid.py`；无脚本旧合约只按其明示的gzip/XZ路径、长度、SHA纯解码，不执行清单中的shell文本
- 覆盖L所有source失败/诊断/form-v2/form-v3/source/fresh/views原大JSON，North源与报告、旧scatter/intake/world-trial报告及checkpoint原NPZ
- 唯一需编码恢复的原生源：`source-assets/north-ridge62-authoring/recovery-v2/north-ridge62.blend`，10,004,835B，SHA256 `dd1d3c12b8c3f98fdcd42a21057d519f1cac48eeab468cbc7721d1c1673ab502`
- 另核当前Git直接保存的L诊断、form-v2、form-v3三份原生源：319519B/324985B/324179B，工作文件和Git blob SHA逐字一致
- 原诊断、form-v2、form-v3共12张原PNG，9,704,347B；文件SHA、1179×664尺寸及解码RGBA SHA全部符合原记录

明细见 `restoration-results.json`、`RECOVERY_SUMMARY.json`、`original-png-verification.json`、`direct-native-model-verification.json`。原脚本输出及纯恢复脚本留在本独立报告目录，未写入工程树。

## 四个冻结字节缓存缺口

form-v3 FINAL实际列832项：828项精确、4项缺失、0项差异。包含FINAL自身是829/833可用。form-v3-views FINAL列958项：954项精确、相同4项缺失、0项差异；包含FINAL自身是955/959可用。旧文件保持原字节，不能写成旧833或959全冻结已经恢复。

以下目录中的四个原文件缺失：`source-assets/cloud-bank58/revision-l/source-v1/__pycache__/`

- `native58l.cpython-312.pyc` 与 `native58l.cpython-312.opt-1.pyc`：各60334B，SHA256 `15829257bc56154dca88996451bad0c30ff040927bda06bf196ecccd9dbb1410`
- `native_support58l.cpython-312.pyc` 与 `native_support58l.cpython-312.opt-1.pyc`：各30952B，SHA256 `aebc3398f801f747fe7d9a50c17eec12dfaf04461fe76d5224c5d676af2ac78b`

它们是CPython3.12派生缓存，不是权威工程源码，但旧FINAL和form-v3 SOURCE_BINDING确实将其冻结。当前clone全部tracked文件没有相同长度候选blob，所有storage合约没有这两SHA的精确存储表示。没有尝试新编译、mtime伪造、删除约束或以新字节冒充旧blob。此结论针对当前已拉取终态树及其明示恢复表示，不推断未拉取历史中不存在任何对象。

两个权威源仍精确在场：

- `source-v1/native58l.py`：25743B，SHA256 `a0d9059d2d94f14bd7890b6835674f45a2d8b6fc9a0d8d69ee3440376b1007ad`
- `source-v1/native_support58l.py`：15961B，SHA256 `e8cd215f0170453d9fd7c38b68641c0dfb8fa09f59b3eb4e91b1b1f627932ff1`

当前旧 `frozen_inputs()` / `verify_pins()` 仍会拒绝这四项缺失。新环境准入如何显式处理须由独立下一准备窄审；本次没有修改旧代码、清单或准入，也没有假称历史重放通过。

## 历史全仓保护与当前恢复的区别

原form-v3 source protected-before的14671项：当前13348项、4,724,599,663B逐SHA精确；1322项缺失；1项CLOUD_RESUME不同。views的14794项：当前13471项、4,800,708,683B逐SHA精确；同1322项缺失；1项CLOUD_RESUME不同。CLOUD_RESUME当前字节与HEAD完全相同，差异来自其在原实验之后已提交的正常进度更新，本次未改动。

1322个缺失路径已逐项保存原SHA并分类，未发现新的权威.py、必要原始JSON、模型或PNG缺失：

- Godot导入/编辑器缓存912项；shader缓存48项；编辑器设置1项
- fontconfig缓存219项；其它生成缓存103项；Blender扩展兼容缓存12项
- CPython派生缓存15项，包含上文4项冻结缺口
- Godot userdata运行日志9项：其中8项的精确原字节已存在其它已存日志；1项world-trial-v2 renderer userdata日志未找到精确日志别名，其原stdout/stderr和实际失败报告仍在Git
- North早期冗余gzip表示3项：对应完整原JSON已经通过后来的唯一XZ分块表示恢复，未为了补旧目录枚举而重新生成旧gzip副本

明细仅保存一次于 `common-missing-protected-paths.json`，每项都附原预期SHA；两个历史清单统计在 `historical-protected-path-audit.json`。不将历史保护计数当作当前全树可复现证明，也不伪造旧缓存。North views preparation-snapshot中忽略的模型副本没有另造，权威原生源已在唯一原路径恢复。

## 仓外依赖审计

当前form-v3/form-v3-views的工程模块依赖都在仓库内。所审source-assets/cloud-evidence的脚本、JSON、文档和日志未发现另一个必须从失去的绝对仓外路径恢复的自写Python脚本；旧标准库traceback路径不是工程源。唯一当前明确外置运行依赖为 `tools-feiting/blender-4.5.14-linux-x64` 中固定Blender、Python3.11.15及NumPy1.26.4，由并行工具恢复项负责，本次没有下载或宣称工具恢复完成。

旧design-v1绘图脚本按其README应在新临时staging中运行，取已存checkpoint的NPZ并显式设置AETHER_ROOT；其依赖原NPZ已精确恢复到checkpoint，不向design-v1加冗余副本，也不重跑旧调查。

## 最终边界

最终 `git status --porcelain=v1 --untracked-files=all` 为空。tracked字节未改；恢复文件均仍ignored；零新.bytecode、零引擎、零新native/视觉/world/GOAL验收。所有旧失败、已消费准入、源文件和冻结清单保持原样。必须在报告与恢复缺口诚实发布、远端核回及新环境准入窄审后，才由后续任务开始form-v4。
