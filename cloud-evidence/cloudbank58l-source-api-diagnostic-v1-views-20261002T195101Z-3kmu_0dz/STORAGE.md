# 四原生诊断图的证据存储

四PNG保持完整原字节，直接普通Git blob（总3223892B），不裁切/再编码/叠字。`original-png-decode.json`记录尺寸、文件SHA、解码RGBA SHA；前两原固定camera一致，像素一致如实记录。

14大JSON原路径共9唯一原字节版本：2个gzip(mtime=0)流、3个≤500000B部件927261B，7个其它版本使用精确literal byte splice。唯一base是本次first-view baseline原raw；patch仅真实PID、render settings和临时image-state字段，整体每版全SHA核同。4份restored与各自baseline逐字節相同，before/after保护manifest也相同，别名只指向同一对象。

重拉运行 `python -B restore_storage.py`，或 `--out /新空目录`；脚本复用此前已经发布的精确存储恢复器，核所有part/压缩流/base/literal片段/最终完整大小SHA，拒覆盖不同证据。原JSON不按结构重新序列化。14原工作文件全部在场且本地verify-only已过，仅精确路径gitignore避免双份保存。

新bare公共Git逐字节核回后，还必须从那些实际远端对象导出存储包，在新空目录恢复并解析14原JSON、解码四原PNG，才算本次完整外存闭环。原模型已经前一提交直接存入Git，本轮不再复制模型或增加原项目备份。
