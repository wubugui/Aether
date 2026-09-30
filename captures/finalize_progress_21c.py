from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
for label,run_name in [('21b','coast-environment-21b-20260908T101600Z-709d602169834795a1574acc1bacafd1'),('21c','coast-environment-21c-20260908T102214Z-b866a4fcb0724d3ba6755f194b342f8b')]:
    m=json.loads((root/'captures/validation_runs'/run_name/'manifest.json').read_text(encoding='utf-8'));assert m['passed']
p=root/'reviews/round-21-worklog.md';s=p.read_text(encoding='utf-8')
s+='''

21b后续：上述session46724已完成，无待等句柄。三图passed，根与独立均直接看完；61绑定SHA一致。稀疏星域和真实分面月体获有限保留，云体仍有薄片/相似横排，水光为规则网纹且偏抢眼，前景原生PBR建筑过暗，整体打回。模型和shader原样保留。独立报告 `round-21b-environment-independent-review.md/audit.json`。

## 21c：实际环境光来源修正

当前Godot4.5.1 console运行时常量实际输出background0/color2/disabled1/sky3，证据 `captures/environment-sources-runtime.log` 和诊断脚本。game.tscn继承3=SKY；21b只改颜色/能量，没有改来源。21c只在临时夜间明确切换AMBIENT_SOURCE_COLOR，并增记实际来源/颜色、4盏Omni全局位置、未映射shader路径；岛屿、月球、云与全部21bshader字节沿用。夜景sidecar旧daytime措辞已纠正，生产game.tscn未修改。

run `coast-environment-21c-20260908T102214Z-b866a4fcb0724d3ba6755f194b342f8b` 两个受影响夜视角完成，session10692结束。根直接看完两张原图，前景塔/屋和岛岩明显恢复受光与体量；不再把原生PBR大部压成黑色。实际ambient_source2、ambient_color(.36,.46,.70)、energy1、四灯记录、已遍历材质未映射列表为空。一次性遍历不证明后续流式节点全覆盖，未捕获sky_contribution属性值，不据默认值作额外实测声明。

全参考仍未通过：岛崖层叠与大片草盖、水光网纹、云片排列、两岸村镇/码头/船和暖光链、实际灯塔束光、其余天气以及原生生产集成仍缺。独立21c复核另存同轮报告，当前以报告文件为准。已登记 `reviews/reference-view-1342-progress-21c.json`，明确status=in_progress_not_accepted并绑定实际机位、世界SHA、临时岛位/原海面证据和环境参数；没有把候选写成已安装或已完成场景。
''';p.write_text(s,encoding='utf-8')
old='**已开始同世界真实昼夜环境21a，夜景打回。**'
latest='''**最新环境候选21c已经完成两个受影响GPU夜视角。** 21a过黑/密星/方格月盘/条纹水光打回；21b用Blender保存4套实体月球/三类云体，实际重开源验证和三GPU图完成，星域/月体有限保留，整体仍打回。21c经本机Godot运行时核实，把夜间环境光来源从SKY明确改为COLOR，真实图恢复原生塔/屋/岩体层次；保存来源/颜色、四灯世界位置及已遍历未映射材质列表。两夜图根已直接看完，独立范围以 `reviews/round-21c-environment-independent-review.md` 为准。全部21a/b/c引擎会话已结束，不重复旧运行。1342候选机位登记 `reviews/reference-view-1342-progress-21c.json`，状态明确未接受。生产仍17e/18c/19h，所有岛礁/天空/环境为临时候选。流式环境、其他天气、暖束光、完整岸村与自然岩岸/水光尚待制作，详见 `reviews/round-21-worklog.md`。

'''
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=root/name;s=p.read_text(encoding='utf-8');start=s.index(old)
    end=s.index('\n\n',start)+2;s=s[:start]+latest+s[end:];p.write_text(s,encoding='utf-8')
print('Recorded completed21b/21c runs; whole goal remains active')
