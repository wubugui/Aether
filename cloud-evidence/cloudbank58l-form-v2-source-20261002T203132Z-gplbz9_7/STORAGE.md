# form-v2 保存后失败的完整原始证据

实际新.blend 324985B直接按原路径/原字节普通Git blob保存，SHA256 33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a，无LFS，不分块模型，不另造模型备份。

23大JSON（21份mesh raw+2保护manifest）有14唯一原字节版本。每个唯一版本gzip(mtime=0)，分15个≤500000B普通Git部件，总5286180B；别名引用同一压缩流。未重新序列化JSON，原工作raw未修改，只按23精确路径gitignore避免两份存储。

重拉运行 `python -B restore_storage.py`，或 `--out /新的空目录`；核每块/拼接流/完整原文件大小SHA，拒不同现有证据覆盖。`--verify-only`只核不生成缺失文件，本地全部23原字节已核通过。

从新bare真实Git对象导出存储包并在新空目录恢复/解析23JSON，另精确读取原模型直接blob，才算完整外存。跨Python诊断两replay脚本/JSON、第一轮诊断脚本环境组装失误、全部真实日志/进程和native原输出也保留；诊断不是新native或fresh-open。
