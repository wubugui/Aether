# API 隔离诊断源的原始数据存储

原生 `.blend` 319519B直接按原路径/原字节存入普通Git，无LFS，不用分块恢复模型。其完整SHA为7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7。

44个大运行JSON原路径有27个不同原始字节版本。为不重复保存相同数据：

- 14个唯一gzip(mtime=0)流，15个≤500000B普通Git部件，总5276689B
- 13个fresh-open原字节版本与已有build版本只差顶层真实PID和opened_filepath；保存精确offset/待删除literal/插入literal与base/full SHA，绝不按JSON重新序列化
- verify-raw的原精确base是build-manual-baseline-restored字节，不是类型表示不同的最初build-raw。记录这种真实差异，不强行把数值等价说成字节相同
- 所有重复保护/恢复路径只引用同一唯一对象。原工作raw不改，仅44个精确路径gitignore，不另存冗余整包

重拉运行 `python -B restore_storage.py` 恢复原路径；或 `--out /新的空目录`。每块/压缩流/base/字节patch删除内容/最终全文件大小及SHA全核，拒绝依赖循环、越界路径、不同现有文件覆盖。`--verify-only`不写缺失文件；本地44原路径全部已核一致。

只有从新bare实际回取的Git对象导出本包，在新空目录完整恢复/解析44原JSON并核原模型直接blob，才算完整远端外存。其它小型JSON/日志/内嵌Text、原调用方脚本和有限成功报告都直接Git保存；源码不得把原raw大小变小后冒称原证据。完整source stage继续关联原66个实际输出SHA，归档工具未修改它们。
