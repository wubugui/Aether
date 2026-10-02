# 原始运行字节的唯一无损存储

本轮没有保存原生模型。为避免重复且保留所有原始失败证据，以下4原路径以2个唯一gzip(mtime=0)流、3个不超过500000B的普通Git二进制部件保存，总920299B。路径filter为unspecified，不使用LFS；相同before/after及raw/failure共享唯一流，不另留压缩备份副本。

- protected-before.json、protected-after.json：各2837745B，SHA256 d0ae378b570387fa291278db0340a65ce1ae51bac2f245447e23f37e85f9dd74
- outputs/build-raw.json、outputs/build-failure-raw.json：各1510879B，SHA256 0b39aa841519b65874e24d219c4e74d3063daa8dfd9bdf86b15fdb90e9b5a99c

原工作raw未修改，仅精确路径gitignore避免重复。重拉后运行 `python -B restore_storage.py` 恢复原路径；亦可 `--out /新的空目录` 独立恢复。脚本核每块/拼接压缩流/完整原文件大小与SHA，拒覆盖不同现有证据，不重新序列化JSON。`--verify-only`只重建检查，不写缺失文件。

完整normal_diagnosis重放还需要此前175127Z原失败raw，按其原STORAGE恢复；脚本按仓库位置读取两次失败，不需启动Blender。当前本地恢复检查已过；只有从新bare远端对象导出的存储包在新空目录精确恢复后，才算此次完整外存核验。

其余小型原日志/JSON/嵌入Text/调用方观察直接Git保存。config下121B compat.dat 是本轮factory环境产生的Blender版本/平台缓存元数据，不含凭据。源码读取的官方URL在normal-diagnosis.json；没有下载的官方源码拷贝。
