from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'reviews/round-20-worklog.md';s=p.read_text()
s+='''

## 20i /20j后续：实际道路坡度打回

20i七图run `lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19` 已结束，根与独立审查均看完；上文exec30408进行中已是历史。真实GLB贴地+0.045m，但A/B/C最大坡36.32/42.58/57.36°，C门口实际道路陡峭，不能以贴地当通路验收。裸岩肩有尖丘、沿岸层带仍人工整齐。

20j增加真实纵向路基和道路两侧地形约束，同时四屋路线端点延长到最低台阶的平面投影内。374部件保存源通过，run `lantern-islands-20j-20260908T095046Z-40396a05903943f883b5b24772194f44` 四图完成，根全部直接查看。C最大坡降至19.39°，但过大的6.3m塔保护平台覆盖路基过渡，A/B增至63.68/54.46°。独立定位发生在平台外1.2m过渡区。未接收整体，保留失败源与图。

## 20k：塔平台范围与中景岛

最终塔保护范围缩至4.2m，原pad_height6.3m不变，实际19h基础边界4.015m。三岛保存源通过，房屋+三礁保留20h字节。独立量测C9.65°、B39.02°，原塔边尖折大幅消退；A支路汇合口残留一块0.078m²、61.86°的尖折面，不能忽略。

run `lantern-islands-20k-20260908T100303Z-f0acc3aa5ea3410b82358e15dcd9b4e3` 五GPU图完成，根与独立审查均看完。近机位使前景灯塔靠左；D岛在(-2340,0,-1810)旋转.55复用C原生资产，所有建筑/树用本地→世界变换。装配前D中心实际射线命中SeaCollision，sidecar保存证据；只是候选位置，不证明原地图地理。四塔五屋共9基础包围采样组，非步行验收。独立48绑定通过，构图改善可保留，C/D高灰墙、层叠岸壁和大片绿盖仍打回。

## 20l：汇合口高度连续化

以平滑距离权重混合相交道路纵剖面，替换最近路线硬切换，三岛重新保存，房屋/三礁不变，374部件native通过。独立匹配同一投影三角，原A61.8638°实际降至6.01045°，水平匹配误差0；不是删去问题面。三岛最大坡30.50/39.02/9.65°，>45°面积均0，B仍49.60%面积>20°，不称舒适步行。实际3914/2271/1254地形采样保持+0.045m。

20l真实GPU归入21a环境run：`coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0` 的day-paths/day-reference提供同版昼景；另两张夜景。根与独立均看完四图。独立支持局部道路改进，未批准整体岛岸。见 `round-20l-path-independent-review.md`、`round-21a-environment-independent-review.md`。所有20k和21a执行已结束，无待等旧进程。
''';p.write_text(s)
latest='''**当前最新候选20l，岛礁仍未生产集成。** 20i/j实拍及独立量测打回陡峭路基；20k缩小塔平台保护范围，新增经实际SeaCollision中心核实的D中景岛（C资产旋转复用），调整近景机位。20l真实连续路基混合修复A汇合口同一三角61.86°→6.01°；独立实际GLB和21a昼景支持有限保留。B坡道仍有较大陡坡比例，台阶/步行未验收。C/D高灰墙、沿岸规则叠层、大片草盖与右岸聚落仍待返工。详见 `reviews/round-20-worklog.md`。

**已开始同世界真实昼夜环境21a，夜景打回。** 四图run `coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0` 完成，实际方向光/环境/雾、世界地形材质自发光、云、水面镜向月光、窗灯与塔内真实Omni同步变化；不是全屏滤色。根与独立均看完。过暗、星密、方格月盘与梳状波光不合参考。21b在独立候选中提高真实环境填光、改交叉波法线，并用Blender生成实体月球与三类分层云体；同版GPU正在独立run验证，完成状态以manifest/最新21轮记录为准。生产仍17e/18c/19h；天气流式更新、海雾/雷雨等、完整参考场景未完成。

'''
p=root/'WORKSPACE_RESUME.md';s=p.read_text();start=s.index('**最新候选20h');end=s.index('## 已完成的迁移恢复',start);s=s[:start]+latest+'所有旧迁移、19h安装、20h/i/j/k与21a完成运行均不得无原因重跑。会话Goal仍为全部20参考范围active；实际Goal更新回读记录位于 `captures/goal-update-20260908`。\n\n'+s[end:];p.write_text(s)
p=root/'reviews/LOOP.md';s=p.read_text();start=s.index('**20轮最新为20h');end=s.index('历史单图目标',start);s=s[:start]+latest+s[end:];s=s.replace('20轮岛礁已接续到20h','20轮岛礁已接续到20l，并开始21轮真实昼夜环境');p.write_text(s)
p=root/'WORLD_SCENE_PLAN.md';s=p.read_text();s+='''

2026-09-08增量：20k经运行前SeaCollision中心探针新增D(-2340,0,-1810)，以C岛旋转.55复用，形成前景A—中景D—远景B/C的可飞行空间层次，仍为地理设计提案。20l完成局部道路汇合修正，整体岛岸未验收。21a首次在同版20l连续World里切换真实昼夜灯光、天空、材质填光、云、水面反射与窗灯，夜景因黑压/星密/规则波光被独立打回。21b独立候选进一步制作Blender实体月球/云层及实际填光；详见21轮工作记录。所有候选均未安装生产，不宣称流式环境或其他天气完成。
''';p.write_text(s)
p=root/'reviews/round-21-worklog.md';assert not p.exists();p.write_text('''# 21轮：同世界环境制作

## 21a 实际昼夜基底，视觉打回

run `coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0` 四GPU图：day-paths/day-reference/night-reference/night-back。全部几何冻结20l原生资产，与同一生产World临时装配，无生产修改。根与独立均直接看完4图，53绑定SHA一致，日志无ERROR/WARNING。20l局部道路可保留，夜景打回。

实际候选处理方向光、环境光、雾、world/terrain/cliff/ship自发光与haze、cloud实际法线照度、sky星月、水面实际视线+波法线镜向月光，及PBR玻璃窗/灯芯发光。四塔Omni位于实际GLB灯芯19.6m。独立核查支持这些真实变化，但不等于全世界无漏材质，也未实现后续流式节点自动重适配。sidecar顶层daytime措辞是旧模板，night字段及图显示夜景，待后续模板修正。

失败：画面过暗，大块地貌难读；星点过密，月盘方格；水光等距梳条。暖窗出现但聚落、投射束光和岸边暖光未完成。参考1342仍差大，不能以真昼夜替代画面完成。独立报告 `round-21a-environment-independent-review.md/audit.json`。

## 21b Blender实体天空与照度返工

新建 `blender/model_coastal_sky_21b.py`，生成实体月球（细分三角面和浅盆地雕刻）、三种3/5/4部件分层云体，共4套独立BLEND/GLB。重新打开保存源进行闭边/正体积/面面积/范围检查，`round-21b-sky-native-check.json` passed。云瓣作为体积云相叠，不宣称无相交。

环境候选 `captures/coast_environment_study_21b`、`captures/coast_environment_21b.gd`：提高真实环境填光和月光，稀疏星点，移除sky方格月盘，放置固定世界位置的原生月球和7组实际云。反射采用两组交叉波法线/破碎波相位。月球距参考机位约9000m，是有限距离的天体表现近似，非全世界严格无视差天文学。

run `coast-environment-21b-20260908T101600Z-709d602169834795a1574acc1bacafd1` 正在执行day-reference/night-reference/night-back三个实际GPU视角，session46724。不能按构建通过预先接受，也不能在句柄仍活时重启。
''')
print('Resume and worklogs updated through20l/21a;21b explicitly pending')
