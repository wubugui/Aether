# 21轮：同世界环境制作

## 21a 实际昼夜基底，视觉打回

run `coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0` 四GPU图：day-paths/day-reference/night-reference/night-back。全部几何冻结20l原生资产，与同一生产World临时装配，无生产修改。根与独立均直接看完4图，53绑定SHA一致，日志无ERROR/WARNING。20l局部道路可保留，夜景打回。

实际候选处理方向光、环境光、雾、world/terrain/cliff/ship自发光与haze、cloud实际法线照度、sky星月、水面实际视线+波法线镜向月光，及PBR玻璃窗/灯芯发光。四塔Omni位于实际GLB灯芯19.6m。独立核查支持这些真实变化，但不等于全世界无漏材质，也未实现后续流式节点自动重适配。sidecar顶层daytime措辞是旧模板，night字段及图显示夜景，待后续模板修正。

失败：画面过暗，大块地貌难读；星点过密，月盘方格；水光等距梳条。暖窗出现但聚落、投射束光和岸边暖光未完成。参考1342仍差大，不能以真昼夜替代画面完成。独立报告 `round-21a-environment-independent-review.md/audit.json`。

## 21b Blender实体天空与照度返工

新建 `blender/model_coastal_sky_21b.py`，生成实体月球（细分三角面和浅盆地雕刻）、三种3/5/4部件分层云体，共4套独立BLEND/GLB。重新打开保存源进行闭边/正体积/面面积/范围检查，`round-21b-sky-native-check.json` passed。云瓣作为体积云相叠，不宣称无相交。

环境候选 `captures/coast_environment_study_21b`、`captures/coast_environment_21b.gd`：提高真实环境填光和月光，稀疏星点，移除sky方格月盘，放置固定世界位置的原生月球和7组实际云。反射采用两组交叉波法线/破碎波相位。月球距参考机位约9000m，是有限距离的天体表现近似，非全世界严格无视差天文学。

run `coast-environment-21b-20260908T101600Z-709d602169834795a1574acc1bacafd1` 正在执行day-reference/night-reference/night-back三个实际GPU视角，session46724。不能按构建通过预先接受，也不能在句柄仍活时重启。


21b后续：上述session46724已完成，无待等句柄。三图passed，根与独立均直接看完；61绑定SHA一致。稀疏星域和真实分面月体获有限保留，云体仍有薄片/相似横排，水光为规则网纹且偏抢眼，前景原生PBR建筑过暗，整体打回。模型和shader原样保留。独立报告 `round-21b-environment-independent-review.md/audit.json`。

## 21c：实际环境光来源修正

当前Godot4.5.1 console运行时常量实际输出background0/color2/disabled1/sky3，证据 `captures/environment-sources-runtime.log` 和诊断脚本。game.tscn继承3=SKY；21b只改颜色/能量，没有改来源。21c只在临时夜间明确切换AMBIENT_SOURCE_COLOR，并增记实际来源/颜色、4盏Omni全局位置、未映射shader路径；岛屿、月球、云与全部21bshader字节沿用。夜景sidecar旧daytime措辞已纠正，生产game.tscn未修改。

run `coast-environment-21c-20260908T102214Z-b866a4fcb0724d3ba6755f194b342f8b` 两个受影响夜视角完成，session10692结束。根直接看完两张原图，前景塔/屋和岛岩明显恢复受光与体量；不再把原生PBR大部压成黑色。实际ambient_source2、ambient_color(.36,.46,.70)、energy1、四灯记录、已遍历材质未映射列表为空。一次性遍历不证明后续流式节点全覆盖，未捕获sky_contribution属性值，不据默认值作额外实测声明。

全参考仍未通过：岛崖层叠与大片草盖、水光网纹、云片排列、两岸村镇/码头/船和暖光链、实际灯塔束光、其余天气以及原生生产集成仍缺。独立21c复核另存同轮报告，当前以报告文件为准。已登记 `reviews/reference-view-1342-progress-21c.json`，明确status=in_progress_not_accepted并绑定实际机位、世界SHA、临时岛位/原海面证据和环境参数；没有把候选写成已安装或已完成场景。

21c独立复核已完成：根和审查者均直接看完两图，支持保留COLOR来源填光修复作为局部夜景底稿，整体场景仍未接受。59绑定SHA一致；所有21b shader、4天空源与岛屋礁全部保留原字节。两图实际source2，4盏Omni位置与塔位+19.6m最大误差1.53e-6m，当前遍历未映射列表均空。详见 `round-21c-environment-independent-review.md/audit.json`；sky_contribution未记录，不用未知默认值否定实际修复，也不重复无新变化的渲染。下一步应继续真实岛岸/聚落与灯塔束光、云形和水光，不把限定工程检查代替参考完成。
