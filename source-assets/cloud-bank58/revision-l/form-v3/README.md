# Form-v3：两处有限肩团与肩腹回转准备

2026-10-02 UTC。一个新候选，原 form-v2 与全部旧源/失败/准入原样保护。**仅纯准备，0 engine/native/save/fresh-open/render/PNG/新阶段准入。** 原图已完整发布核回 `3e4ff5c325ece6b4a3ab7dfa3492f3d1861040f6` 后才开始本项；本包还须父窄审、GitHub插件完整发布与实际远端字节核回，不能因本文或纯测启动引擎。

## 针对实际图的唯一改形

亲看 form-v2 全四原PNG、旧API全四同名PNG、独立视觉报告和 ref/1216。近肩旧尖带减少但变大整坡；侧背仍由两峰、长壁和平台支配。目标保留厚连体与主冠，把近肩形成不均等、偏轴错接的大/中/小肩团和浅宽鞍，把侧背三处形成不同高低、长度的肩腹回转。没有换灯、改材质、加采样或换镜头。

本轮只改两处现有点集，坐标为世界X/Z：

- 近肩 X3660–4090 / Z3800–4080
- 侧背 X3800–4630 / Z3430–3790

两区外全XYZ逐点精确保留。仍为1567顶点、3130三角，拓扑零变化，无细分或新球体。308个实际顶点改变：84个平面采样点的顶/底XZ成对变化，最大11.168034m（界35m）；198个顶Y改变，范围−112.270630至+71.760132m（界120m）；74个含共享外岸的底Y改变，范围−13.462646至+15.163391m（界35m），其中51个真实岸Y改变。逐点前后与delta见 FORM_CHANGE_REPORT.json。

释放的是两区的内部旧XZ、肩顶剖面与边缘腹/岸Y的精确身份。真实203段凹外岸XZ、整个投影外域、四主冠/谷节点的顶腹身份、七主控制及谷宽全部原字段、手工点位与恢复语义均保持。新绑定明确记录旧form-v2与当前顶/底坐标；不能称旧局部剖面还通过。

外缘Y/腹面只在旧和新位置均距真正外岸<80m时改动，实际底改形45m内已收回原腹。**原80m核心判定、腹560–630、厚≥120与绝对Y包围门不变。** 没有把内部谷或接缝当外缘；内部采样点侧移后重新计算实际外岸距离与完整原空间门。XZ改变是作者基线变化；之后七控制与手改仍对新基线采用原height-edit接口，不偷偷扩编辑权限。

首遍候选的主冠接界被下拉199.443m，触发原120m顶变化界，未进结构门。其候选/绑定/脚本/日志/报告全保在 preparation-history/attempt01。父确认后只收窄同一候选的冠侧混合权重，没有夹值、加大界或换方案；当前原空间门通过。首遍不是原生运行失败，不与历史真实source失败混称。

## 有限投影检查，不是新图或视觉通过

PROJECTION_SAMPLES.json 使用当前实际三角和原绝对相机检查少量肩/鞍点。侧背三个肩中心均在画内且该点无遮挡，实际表面Y约869.37/828.37/787.18m；一处谷鞍约735.87m。近肩中心和有限网格点有自遮挡，不能把六个命名峰当成六层可见。

NEAR_VISIBILITY_SAMPLES.json 明示：近肩大块16个有限顶点中7个可见、中块11中7个可见、小回转9个有限顶点全被遮挡，小块中心早期命中遮挡约206.67m。此有限点集不证明整个面片不可见，也不证明整体层次达标。按父要求冻结当前唯一候选，不再为中心可见扩设计；真实原机位图再决定能否接受。未生成示意图冒充原生证据。

第一遍投影辅助样本(4335,3630)实际落在外凹湾，被工具拒绝；projection-attempt01.log保留。改为真实域内(4335,3680)仅是读取样本修正，候选不变。第一次纯测有tuple/list序列化比较夹具差异，原失败日志保留，仅修正测试比较方式，候选未因此改变。

## 纯测与原生边界

原 spatial_gate、planar_certificate、evaluate、validate_evaluated、validate_native_raw 函数逐字保留。当前候选原完整闭壳g0/定向/非自交/正厚/真外岸核心规则通过，7主+谷宽指定态、manual+0.125m、组合及恢复通过；C06=560仍被拒绝，不声称整个参数笛卡尔积可用。

官方3.11完整 normal / -O 各81项通过（7.764/7.751秒），含16项形体、45项复用API/完整capture/exercise、20项最小运行适配检查。实际只读历史前件重算15.172秒通过，无新准入。复用原数学/API oracle与实际历史raw测试；原22面旧默认和form-v2 23面默认corner→数学几何3e-5失败分列保留。每个新实际control/manual/restored态仍必须重测原corner数学门，API诊断成功不代表full-native成功。所有 full_native/visual/contact/world/weather/global_GOAL 保持false。

SOURCE_BINDING.json 精确绑定790旧文件与28历史准入/终态记录，以及旧form-v2真实成功build、后续fresh-only和四原图组合。旧form-v2整体source仍failed，不调用其虚假成功路径。旧源324985B/SHA33cc763…不复制或改写。本包没有复制旧大raw或旧大资产。

## 最小source-only执行准备

- 官方bundled Python3.11.15及NumPy1.26.4，解释器SHA `60b08089c60cbe81827b135c8fd9e206ba2ee6bf54aa1dbd0d6f56ac2d5914f6`
- runtime58l.py作用域隔离加载旧recovery/views真实校验，再恢复当前模块；直接复用已审libc.pidfd桥及未改source-runner-v3监督，不重写进程框架
- observer真实Popen/wait，wrapper/native/observer三层明确新版本及原旧source失败；完整报告精确比较，不增容差/rounding
- 原CPU2/总120秒/build80/verify30/aggregate1.5GiB/20秒尾余量保持
- 所有旧源、runner、准入、raw、图、成功/失败纳入原全仓保护；仅唯一新源与当次新run/新终态临时文件依原规则排除
- 唯一新输出 source-assets/cloud-bank58/revision-l/form-v3/cloud_bank58l_form_v3.blend
- 本包公开准入仅source；observer、runner、diagnostic和native都拒绝views/render。旧内部render分支保留而不可达。新source全部结果先外存核回，才另做最窄原机位views适配

父窄审及完整插件外存核回之后唯一入口：

`../tools-feiting/blender-4.5.14-linux-x64/4.5/python/bin/python3.11 -B source-assets/cloud-bank58/revision-l/form-v3/observe_form58l.py --run-approved source`

该命令未运行。默认调用no-op。准备包和纯测不授予执行权；当前世界默认、材料、天气、24其它云根及相机均未修改。
