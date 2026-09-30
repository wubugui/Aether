# 22轮：真实港口模块、岸上聚落与连接路线

本轮接续20l临时岛礁和21c昼夜环境。生产仍为17e岩体、18c地表、19h共享灯塔；所有22轮港口候选尚未安装生产。会话Goal已通过get_goal实际读回，仍是全部20张ref与原图、同一可飞行世界、多天气时段、Blender精细建模、统一风格、跳过角色，状态active。不能以本轮模块检查通过代替完整目标。

## 22a：六种原生场景资产

`blender/model_harbor_kit_22a.py`生成`captures/harbor_kit_study_22a`：timber_pier、pier_landing、repair_awning、harbor_lantern、harbor_cargo、moored_fishing_boat，共504个独立可编辑部件。包括厚木板与桩梁/铁箍/绳栏、红帆布修整棚与工作台工具、四面薄玻璃铜灯、分木条桶箱、具有真实内腔和船壳厚度/座板/桅杆/有厚度曲帆的小船。只作场景物件，不增角色或载具玩法。保存后重开检查见`round-22a-harbor-native-check.json`，只证明所列闭合/正体积/面面积/玻璃方向，不证明全部接触或视觉。

参考1135原图已重新直接查看；独立场地建议见`round-22a-port-site-independent-review.md`及audit。原海岸与1342所需右前景岬岸关系不符，当前房屋放在原岸平坦位置不等于构图已满足。

实际细地形调查run：`harbor-sites-22a-20260908T103705Z-af34540b52054103be479e592bea4f7d`。16条岸线横断面、真实碰撞海陆交界/房屋3×3基础点，选出23屋位及4处2.15m高码头岸端。房屋保持原生尺寸，不压缩屋型。调查依据原World SHA `6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8`，SeaCollision=海面而非海床。

实际装配run：`harbor-assembly-22a-20260908T104332Z-7bb7bd47c7e846a0b285e9a5dcfd5654`。`tools/render_harbor_assembly_22a.py`冻结候选；`captures/harbor_assembly_22a.gd`在同一世界临时装配23房、4木栈桥/平台/棚/货物/小船、39盏真实局部灯。完成day-reference、night-reference、dock-front、dock-back、boat-close、night-dock六张GPU原图，根与独立审查均直接看完。所有引擎会话已结束。

独立报告`round-22a-harbor-independent-review.md`、绑定audit和geometry-audit：98登记SHA一致；23屋207基础样点均低于原生地面，间隙-0.630至-0.209m；四码头岸端仍有19.25–20.77cm台差。灯位从父变换重算最大误差0.000161m，夜间暖光有效。六图vegetation_adjustments全部为空，没有登记树木移除。船底最低约Y=-0.38m，未采样真实船底/海床，不能宣称不搁浅或完成系泊。

保留木构、棚布、船内腔和暖灯模块方向；整岸及直接安装仍打回。房屋同型成排、码头到房区无路、原岸过直、1342右前景岸缺失、岛岩/云水仍不符。

## 22b：木构接触修复与真实路线调查

`blender/model_harbor_kit_22b.py`仅重建两种码头：梁中心上调0.01m，使梁顶2.20m与板底2.20m接合；钉头中心2.346m、厚0.008m，使顶2.35m与甲板齐平。其余4件资产直接复制22a，待独立身份复核。源位于`captures/harbor_kit_study_22b`，build日志`captures/harbor-22b-build.*`；保存后原生重开`round-22b-harbor-native-check.json` passed，检查进程已结束。尚无22b实际装配GPU图，不能称视觉通过。独立木构修复审查已派发，结果以同轮报告为准。

新调查run `harbor-routes-22b-20260908T104909Z-0a67b81f537747abb4e04931b7a0ea02`完成，原exec session79760已结束。冻结脚本、原调查身份、`survey/routes.json`及`routes-before.png`均保留，根已直接看过原地形图。四岸端向内陆0–2.4m每0.2m取5个横向点；4条直线候选走廊每不大于0.4m取3点（宽3m），连至最近房屋门前。直线拓扑是设计提案，原碰撞采样是实测，两者不可混称已知地图事实。

| 码头 | 走廊水平长 | 起点中线地面 | 终点中线地面 | 房屋低阶顶 |
|---|---:|---:|---:|---:|
| 0 | 78.851m | 2.932m | 18.954m | 19.279m |
| 1 | 47.689m | 2.932m | 14.913m | 15.200m |
| 2 | 47.452m | 2.932m | 15.000m | 15.200m |
| 3 | 48.676m | 2.938m | 14.737m | 15.200m |

岸端地面约2.15m，在0.6m内陆处已接近/超过甲板2.35m；2.4m内陆约2.93m。连接件不能简单铺水平板掩盖台差。候选路线尤其0横坡显著，需要石阶/局部整地、转向平台、门阶和岸端连续衔接；长直阶梯及完全同型屋排仍需村落设计。当前没有新增坡道/石阶模型或原生碰撞，没有完整步行检查。

下一步：根据独立22b量测确定实际石阶及岸端接合；Blender分件建模并保留源；新增受影响GPU视角和独立复核；检查船底真实地形深度，再调整岸村分组/前景岸地形。不得重复迁移、旧19h安装或无新变化的20/21/22a完整运行。完整Goal继续active。

以上为22b历史状态，以下22c–22g已经完成新接续，不要重新执行旧待办。

## 22c/22d：连续曲线路线的实际原地形调查

22b独立复核已完成：实际两码头板底/梁顶同为2.200000048，钉顶/板顶同为2.349999905；其余四件BLEND/GLB与22a字节一致。详见`round-22b-harbor-independent-review.md/audit.json`。

22c新路径对齐码头入口及房屋最低阶外缘Godot局部Z6.40m，宽4.4→3→2m，按等弧长≤0.4m做每排5横向点的原地形采样。run `harbor-paths-22c-20260908T110155Z-db9f99b15ea84c5ab8351d26bdc58f1d`完成，session25466结束。0号12m曲线手柄最小解析曲率半径4.513m、侧边最短0.222m，独立建议放缓，设计初审`round-22c-path-design-independent-notes.md`。

22d仅把0号手柄改20m，最小半径12.536m、最短侧边0.330m，其他三路形状保留。新原地形调查run `harbor-paths-22d-20260908T110627Z-a72a69931ce84a6ea250c34715f018ad`已完成，session41682结束；`survey/paths.json`为最终石阶唯一实测输入。比较见`round-22d-curve-independent-comparison.md/json`。路径拓扑/计划高程为设计，实际剖面为原World碰撞测量，不混称原参考地理事实。

## 22d/22e失败及22f原生石阶

`blender/model_harbor_paths_22d.py`首次生成因门前抬高公式误作用整条路线，被固定首阶断言拦下（2.35→9.294m），没有可用导出。22e将门前抬高限定最后4m，完成0/1/2资产，但3号首格4.5cm设计露出包络与固定首顶冲突6.707mm，生成再次被拦下，不能称四路完成。失败源、部分产物及`harbor-paths-22d/22e-build.*`全部保留。

22f首格明确使用最低25mm露出界（实际3号38.29mm），其余仍45mm；保留包络及首尾断言。同时限定沿途不下降，消除门前反复降阶；首/末踏石取消接口方向退入和端边倒角，保留侧部实际小倒角。生成四套独立BLEND/GLB在`captures/harbor_paths_study_22f`，完整源`blender/model_harbor_paths_22f.py`，3516个可编辑部件（1758踏石、586厚基座、1172挡边）。保存后实际重开检查`round-22f-harbor-paths-native-check.json` passed，检查进程39224已结束。

| 路线 | 水平曲线长 | 分格 | 平台组 | 首顶 | 末顶 |
|---|---:|---:|---:|---:|---:|
| 0 | 82.508m | 207 | 10 | 2.35m | 19.2794m |
| 1 | 50.000m | 126 | 6 | 2.35m | 15.1999m |
| 2 | 49.757m | 125 | 6 | 2.35m | 15.1999m |
| 3 | 51.023m | 128 | 6 | 2.35m | 15.1999m |

独立实际GLB检查：四路无降阶，最大级差0.180000305m；最小实际平面踏深约0.330/0.371/0.382/0.346m；端部顶点与接口平面误差≤2.1e-6m；基座顶/踏石底接触误差<1e-6m。28组平台实际长1.190–1.196m，不能写成严格1.200m。详见`round-22f-path-independent-geometry-review.md/audit.json`。单独原生检查不等于完整接触、步行或参考视觉通过。

## 22f首次GPU失败、22g受影响恢复与浅滩修复

22f run `harbor-assembly-22f-20260908T111709Z-e545b9625bb042049b0ad4d1c3e868fd`在第一张path-approach图后被WASAPI设备失效ERROR拦下，session20433已结束；图片和sidecar已产生并由根直接看过，失败包原样保存，不过滤或删除错误。该图4路实际碰撞检查passed，但排除SeaCollision的原地面探针证实旧船位每船48–49个低顶点穿地，最小约-0.99m；船先外移3.1m仍每船2负点约-0.15m。

22g只把船相对22a总外移4.0m（pier局部Z0.4→4.4），四路线/全部岛礁/港口模块字节不变；图像采样采用本机Godot实际支持的`--audio-driver Dummy`避免失效系统音频设备，GPU仍为GTX970原OpenGL3.3，不作音频验收。driver `tools/render_harbor_assembly_22g.py`，runtime `captures/harbor_assembly_22g.gd`与`harbor_path_runtime_22g.gd`。

最终run `harbor-assembly-22g-20260908T112011Z-00f0a7b4c813446e842b280476463e21`七视角全部完成：path-approach、path-door、paths-overview、path0-curve、dock-repair、night-path、night-reference；原session72068已结束。根直接看完七张1672×941原图并重看ref1342。每图4路1758组向下踏面/向上基座/同点原地面射线，顶高最大误差0.322mm，基座比原地面低0.2374–1.0636m。运行时所采踏面最小净空44.861mm，不能泛称所有运行时点严格≥45mm。

实际54盏港岸灯=23屋旁+16码头+15沿路；独立重算位置误差<0.161mm。路径冲突清理只改临时MultiMesh副本：`oak_-4_-4 index9`及`rock_-4_-4 index5`共2个散布物（不是两棵树），屋区清理仍0。

4船每船138个实际导出网格低位顶点在新位置均得到排除SeaCollision后的原地面hit，负间隙0，最小净空0.576–0.584m。独立实际船首最大pier局部Z7.93549，距平台名义边Z8仅64.5mm；实际船/平台三角表面最近约0.2545m，三角AABB无重叠。仅当前静态与采样范围，不代表全船面海床/浮力/动态系泊余量完成，桩端海床锚固也未补。

根汇总`round-22g-root-evidence.json`；独立7图/120产物绑定SHA全一致，详见`round-22g-harbor-independent-audit.json`及同轮review；船距另存`round-22g-boat-landing-independent-distance.json`。当前机位登记`reference-view-1342-progress-22g.json`明确未接受，旧21c登记保留。

## 视觉结论与下一步

保留本轮真实接口、厚石阶、基座、弯道、暖灯链和船位修复作为局部资产/工程底稿。**整个港岸仍打回，不能直接安装生产或标记1342完成。** 七图表明当前50–82m长阶梯跨越空草坡直达孤立同型房屋，缺少参考中近右岩岸、凹湾和密疏有别的低层滨水屋群；旧岛崖直墙/分层、水光网纹、灯塔束光缺失依然明显。

下一阶段应优先依据固定1342机位，用实际相机投影和原地形测量定位近右岬角/村屋组团，再用Blender建立有内陆连续衔接的局部岩岸与住宅变体、沿岸短街巷和码头。新地理必须标为设计提案；不要只继续堆同型屋或在错误整体岸线上重复润色。现有22f通路模型可作为精细构件与连接方法保留，若新地形/屋位改变应重新按真实场地建路。生产仍17e/18c/19h；全20参考目标active，所有本轮引擎与Blender生成/检查进程已经结束，不重复无新变化的完成运行。
