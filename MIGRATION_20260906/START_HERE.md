# 换电脑后先读这里

**请带走本目录 archives/ 下的完整 ZIP、SHA256SUMS.txt 和 VERIFY_RESULT.json。整个项目和迁移资料都在 ZIP 内。**
也可以直接把整个 D:\test6 文件夹拷走；外部 Python/游戏用户数据已嵌入 ZIP，使用时应先完整解压 ZIP。

1. 用支持 ZIP64 的解压软件或 Windows 解压功能，完整解压 Aether_Full_Migration_20260906.zip。
2. 解压后最外层是 test6。推荐放回 D:\test6，保留大量现有制作脚本的绝对路径。
3. 检查迁移完整性：在项目根打开 PowerShell，运行下面命令：
   
   .\MIGRATION_20260906\Verify_Extracted.ps1

4. 启动源工程：双击根目录 open-editor.cmd；它使用随项目携带的 Godot 4.5.1。运行源游戏用 run-3d.cmd。Blender源资产通过 open-assets.cmd 或 .tools 中的 Blender 4.5.0 打开。
5. build/RunAether.cmd 是较早的09n验证包，当前源是10l几何加材质所有权修复，不能把两者混当同一版本。
6. 制作/验证脚本可用随包Python：
   
   .\MIGRATION_20260906\python-portable.cmd tools\compare_reference.py --candidate captures\round-13b-study-opening.png --round restored-check

   首次运行建议先执行：
   
   .\MIGRATION_20260906\python-portable.cmd -c "import numpy, scipy, cv2, PIL, shapely; print('Python dependencies OK')"

7. 游戏存档和用户截图在 external/godot_userdata/。需要时将其下两个 Aether 文件夹复制到新电脑的 %APPDATA%\Godot\app_userdata\；已有存档请先另存备份。
8. 在新电脑的 Codex 打开本项目，让新任务首先读取 HANDOFF.md、GOAL_SNAPSHOT.json、history/HISTORY_INDEX.json、reviews/LOOP.md。完整原始对话在 history/raw/，可读版本在 history/readable/。它们已经在包里，不能只依赖这个摘要。
9. 本地历史数据库备份位于 history/metadata/，保存原记录供恢复和检索，不要直接覆盖新电脑已有的 Codex 全局数据库。新任务可直接读取项目内的记录继续工作；本包不声称自动把旧任务插入新电脑侧栏。

可直接粘贴给新任务：

> 这是从另一台电脑迁移的 Aether Godot/Blender 飞艇游戏。先读取 MIGRATION_20260906/HANDOFF.md、GOAL_SNAPSHOT.json、history/HISTORY_INDEX.json 和 reviews/LOOP.md，并按需读取完整 history/raw/。用户要求真实自由飞行3D、独立Blender资产和Godot原生场景拼装，按 assets/reference.jpg 精确还原开场、颜色和UI，必须有独立审查agent，不达标就返工循环。当前视觉未过，生产为10l+原生材质修复，11/12/13/14仅研究稿，Windows包09n。不要跑旧全世界重建脚本覆盖原生编辑，先验证迁移状态，再恢复原完整目标。

当前美术制作暂停是因为换电脑；目标没有完成。

