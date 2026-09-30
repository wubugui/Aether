"""Consolidate coastal progress headings without rewriting historical evidence."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
resume=root/'WORKSPACE_RESUME.md';text=resume.read_text(encoding='utf-8')
start=text.index('**下一步：从共享建筑推进到灯塔岛礁场景。**')
end=text.index('## 已完成的迁移恢复',start)
text=text[:start]+'''**最新候选20h已完成四张受影响GPU图，仍未集成岛礁。** run `lantern-islands-20h-20260908T092421Z-1fa033d6cf29424fbea2c3ab935069bb` passed，房屋前/背、岛链与C岛近景均已由根代理直接查看。20g七图已确认C屋平台内移修复，七建筑共63个独立包围基础位置全负；20h保留全部6地质资产字节，只修瓦片搭接行高差、凸起和屋脊。保存源371部件封闭/正体积/窗向通过；1620个瓦顶搭接采样最小上层高差0.010017m，0非正，真实图黑三角已消失。采样不等于全屋相交、全基础/台阶或步行验收。独立接受范围以 `reviews/round-20h-coast-independent-review.md` 为准；完整记录见 `reviews/round-20-worklog.md`。

**接下来继续细化岛岸与场地。** 已保留20e独立凹湾、高崖/低岸和低板/长脊/断峰三类礁石，但宽而齐整的崖墙、大片草面和切口式湾壁仍不符参考。需要真实岩体分层/斜断面、草地与裸岩交错、门廊至灯塔与岸边的实际路线、自然树组，再推进海岸城镇、水面和真实环境光照。不能以屋顶修复或几何通过接受整个场景。20a的三岛心是经真实SeaCollision勘察后的设计提案，不是已知原地图地理事实；mask4包括海碰撞，详见 `reviews/round-20a-coast-survey.md`。

20b窗向、20c整体盘形、20d C塔、20e C屋、20f瓦朝向、20g瓦相交的失败证据均保留。不要重复迁移、19h一次性安装或已完成20g/h渲染。所有20h渲染exec已结束，无待等引擎会话；会话Goal仍为全部20参考范围active，实际更新回读记录在 `captures/goal-update-20260908`。

'''+text[end:]
resume.write_text(text,encoding='utf-8')
loop=root/'reviews/LOOP.md';text=loop.read_text(encoding='utf-8')
start=text.index('**20轮最新：');end=text.index('历史单图目标：',start)
text=text[:start]+'''**20轮最新为20h：四张受影响GPU图完成，全部6地质资产保留20g，修复了实际错缝瓦片相穿，根代理直接看完四图。20g七图已经确认C屋/C塔基础样本修复。岛岸宽直崖面、大片草地与缺少场地路线仍未通过，整组未安装；下一步细化这些真实地形与通路。** 详见 `round-20-worklog.md` 和20h独立报告的实际接受范围。20b/c/d/e/f/g所有失败保留；不重复已完成渲染或19h安装。

'''+text[end:]
text=text.replace('下一步按20a真实海岸勘察制作连续岛礁，见round-20a-coast-survey.md。','20轮岛礁已接续到20h，当前状态见下条与round-20-worklog.md。')
loop.write_text(text,encoding='utf-8')
print('Coastal resume and loop current through 20h; historical sections retained.')
