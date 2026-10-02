# L form-v2：单一冠肩曲率候选与最小原生准备

2026-10-02 UTC。**这是一项新形体变体，不是旧API成功源或其完成views的失败重试。当前仅纯准备：0 engine / native / save / fresh-open / render / PNG / 新阶段准入；未commit或上传。** 父任务窄审、GitHub插件全量上传和实际远端字节核回后，才可另行准入一次source。

## 亲看及真实成因

已亲看 `ref/1216.png`、已发布API诊断源的03侧背、04近角、01正面，以及同run的 `INDEPENDENT_VISUAL_REVIEW.md`。接受连续主体、宽谷、厚腹的已有进展，针对被打回的截顶冠—长斜坡—陡壁组织改形。未因背景、CPU8sample颗粒、三角面本身打回低poly。

旧 `source-v1/prepare_candidate58l.py` 每25m绑定两条PCHIP顶剖面，随后在95m范围向四个最近权威点插值；这容易把本应转折的肩拉成同向长斜带。其余主冠取4个Gaussian的最大值，中尺度肩的起伏仅来自小幅正弦场。最外侧统一0–45m smoothstep集中回收，容易形成大段陡面。

`VISIBLE_WALL_DIAGNOSIS.json` 用亲看原图选定的像素、原相机字节和原float32候选计算最近射线交点。侧背4个大壁样本均命中顶片，距真正外岸22.7/35.4/33.6/26.9m，确在旧45m回收区；不是将底腹误称可由顶面解决。近角两个长肩样本也命中顶片。此文件不是新渲染或视觉验收。

## 唯一形体改动

- **同1567V / 3130tri，拓扑零改动，全部XZ零改动，203段真非凸岸所有顶点XYZ与全部底腹字节数值相同**。24其他world根、anchor、材料、天气、相机未动
- 4主冠保原中心/冠高；以有限上半椭球曲线和8个有名、大小不同的从属肩块形成冠—肩层次，只在16m高差交界带有限混合，不用均匀串珠、噪声碎面、smooth shader或整世界重生成
- 顶面最外回收由0–45m smoothstep改为0–75m四分之一正弦。**旧80m实体核心门完全保留**，不是把豁免带扩到75m以外或放宽厚度；底回收不动
- 谷线55m内原顶顶点完全保留，55–110m区向新肩渐接；4主冠及全部命名谷节点/出口不动，保持宽谷和厚腹
- 571个顶点仅Y改变，最大绝对位移110.8035888671875m，范围−110.8035888671875至+97.028076171875m；新候选的明确硬界是120m，超界拒绝，不夹紧
- 原7主控制及谷宽的默认/范围/权重/位移字段完整不变。C07仍是旧小幅肩面编辑场，不是用碎面噪声替代主造型

### 明确设计语义变更

**解除旧两条PCHIP的中间顶高精确身份。** 实际23个旧权威剖面点中17个顶高变了；每个旧值、新值与差值均在 `FORM_CHANGE_REPORT.json` 和新 `bindings.json` 中。新绑定直接绑定本候选顶高，不能称旧剖面继续通过。旧底剖面、全部底网格、主冠/谷命名节点仍完整相同。

`geometry58l.py`沿用source-v1的整个有限heightfield几何门，仅更换新身份/输出和本次基线绑定，加一个明确的局部scope检查。`spatial_gate`、`planar_certificate`、`evaluate`、`validate_evaluated`、`validate_native_raw`函数字节级源码不改，测试逐函数比对。不扩展J_i、世界接触或新的形式证明框架。

`preparation-history/`保留本候选未冻结首遍的真实候选/绑定/几何与射线报告，首遍已过几何但近肩覆盖不足。依据同一组原图射线，只将一个未覆盖前景的从属肩重新定位到近角前肩，形成当前唯一待制作候选。没有第二个native路径、可运行分支或可选方案；首遍和日志未删除或伪称失败。

## 必要纯测与有限结果

`GEOMETRY_RESULT.json`：单组件、Euler2、所有边双面反向、全顶点link单环、上下同XZ/正厚、实际非重叠盘与非自交结构检查通过；原腹560–630/厚≥120/真外岸80m门通过，实际违规子域到外岸上界仍77.93207968880047m。所有7主+谷宽指定状态、手工+0.125m、组合及恢复纯测过；C06=560仍因实际核心几何拒绝，不谎称整参数范围都可行。

normal / Python `-O` 各63项通过。复用API组/采样/normal/完整raw与控制fixture测试，另检查实际新候选确定重建、位移/底腹/谷底/拓扑保护、原核心源码、原相机/灯光材料、真实旧失败normal重放和完整嵌入几何。合成fixture不是实际Blender结果。现存两次失败原raw仍保22面旧corner→几何3e-5失败；新图是否改善只有下一次真实原机位才可判断。

报告面坡分布只是描述。新形体的最高坡角仍81.66°，不能用超过70°面数下降或任何离线数值宣告云感/视觉通过。

## 最小原生绑定与保护

`SOURCE_BINDING.json`精确绑定已发布 `96b1384814c4d8fc1622ca3d17b8a3faa2883781` 的旧成功source、四输出/三方向实图与视觉打回报告，旧两次失败链也原样保留。旧成功源319519B / SHA256 `7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7`。成功source与views的四个消耗记录只以精确SHA允许作为历史前件，不能冒充失败、删除或作为本项准入复用。未知/重复的新attempt仍拒绝。

唯一新未来源：`source-assets/cloud-bank58/revision-l/form-v2/cloud_bank58l_form_v2.blend`

`native58l.py`只调整新runner身份；`native_support58l.py`只改嵌入新本地geometry与README的形体语义，normal/API oracle不变。`run58l_form_v2.py`只改新runner/文件/输出身份，直接调用原 `source-runner-v3/deadline58l_v3.py`。`diagnostic58l.py`仅增已发布旧成功形体的精确保护前件和新变体准入，不新造监督器。

API隔离模式仍为 `api_consistency_isolated_diagnostic_v1`：polygon→数学几何3e-5、flat/向外/同面3corner，以及corner→逐float32 Newell API3e-5分别验证；**每个实际控制/manual/恢复态继续测旧corner→数学几何门**。历史22面失败永久保留；`full_native_acceptance=false`不因API通过而变化。

原生保存/独立fresh-open、7主+谷宽、manual/combined/完整恢复、真实raw/八Text及全仓保护不改。source总120秒/CPU2/build80/verify30/aggregate1.5GiB/20秒完成余量；views每图27/总120秒/CPU2/1179×664/8samples。四原机位完整冻结，前两相同所以只有三个不同方向；不重框镜头、改灯或材料。

父完成本包外存闭环后，唯一source入口：

`python -B source-assets/cloud-bank58/revision-l/form-v2/run58l_form_v2.py --run-approved source`

实际保存结果也必须全部外存核回后，才能另行一次 `--run-approved views`。source/views默认调用均no-op。准备包不授予执行权。

`DEPENDENCY_SHA256.json`冻结全部499旧输入/完整L源和前件证据；`FINAL_SHA256.json`再加入本项执行源码、候选、绑定与报告。运行时全仓保护除.git/唯一新输出/当前新证据目录之外所有文件；旧任何模型、代码或证据不排除。

当前 `full_native_acceptance=false / visual_acceptance=false / contact_acceptance=false / world_acceptance=false / global_GOAL=false`。没有世界整合、GPU天气/飞行或全部参考完成结论。
