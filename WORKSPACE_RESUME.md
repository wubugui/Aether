# Aether：当前工作区接续入口

**云端当前权威入口：[CLOUD_RESUME.md](CLOUD_RESUME.md)。** 每次开工先读该文档与GOAL，核当前HEAD/远端/运行状态；完成一个可验证项即更新进度，与源码和证据同提交、立即push并核验。下文是2026-09-30完整迁移之前的本机历史快照；旧“最新”标记、Hub-only路线和本机入口不覆盖现行云端进度。不要从下文推断当前候选或重复已终态任务。

**最新38（2026-09-28）：方向改为“整体→局部、20场景先到60分”，主路线改为在 Hub 上用 Blender 建模并渲染；如实评估仍远不到60分。** 制作人要求：旧实现要审查；参考是设定图，目标是在原画机位上与原画七八成相似；建模要用 Blender 的正经功能。本轮做了四件事：（1）审查确认 36c 候选的地形、岩崖、水面 shader 里乘了暖色系数，这是画面偏黄褐的根因。已在新候选 `captures/candidate_opening38/` 中修正，并换入 37c 城堡；生产未改。（2）Godot 20 机位渲染器 `captures/opening_study_38/render_refs38.gd`：受限于 GL 兼容渲染器和 4GB 显存，效果不及格，只保留为工具。（3）Hub 场景生成器 `blender/lookdev_38/main.py`：程序化地形 + Decimate 低多边形面片 + 几何节点植被 + Remesh 云 + 体积雾 + EEVEE，后来又加了几何节点散布的村镇和岩石，镜湖改用 Cycles 渲染出真实倒影。20 张参考全部有了对应场景，每张最新一版（PNG 和 .blend）及对照总览在 `blender/lookdev_38/final/`，最好的是 1128/1129 镜湖，约 35～40 分，其余约 10～30 分。（4）天空套件（舱室、浮岛、云海）在 `blender/sky_kit_38/`。详细记录、如实评分、共性差距和复现方法见 `reviews/round-38-worklog.md`。下一轮优先补地表内容资产（村镇、道路、岩石、成片森林、浪线），按原画布置构图，修镜湖反射和风暴/云海体积，并请制作人拍板最终落地路线（Blender 目标图还是导回 Godot）。全部 20 参考的目标仍未完成。以下旧阶段不能覆盖本段。

**最新36b地形与36c完整原生候选已接续，36g新进程重开/短程控制通过，整体美术仍未接受。** 36b在14个保存Blender块中改形10659点，拓宽河谷、降低并后退山脊；2537个散布增量保持高岸装配阶段54800总数。12张实际GPU显示中段河岸和终点视野改善，但沿岸长直高边、大草坡、云板/旧云块与水面仍需返工。36b额外保存完整World时14条Windows外链错误，伴随2条纹理泄漏，run failed；12图未在失败manifest绑定，根/独立另行记录。36c只修新World/Game副本的外链和天气目录，保留几何。完整候选继承港路避让的2松1岩删除，实际773组54797实例，与逐项记录一致。36g通过新进程自然初始化、14块网格/碰撞、22新增松组owner/编辑辅助和现有控制器240物理帧；约88.955m是Z约-1910港湾的起终点位移，不是新高岸路线或完整走廊验收。入口为 `run-highcoast-candidate.cmd` / `open-highcoast-candidate.cmd`；原生World/Game在 `captures/candidate_highcoast36c/`，Blender源在 `captures/highcoast_study_36b/`。运行入口已实际加载；编辑器界面提取/重存和自动重导入仍未验。全部本轮进程已结束，不重跑旧版；生产保持，全部20参考与原开场Goal active。证据见 `reviews/round-36bg-root-evidence.json`、`reviews/round-36bg-worklog.md`。以下旧阶段不能覆盖本段。

**最新36a高岸已完成14个Blender地形块、同世界网格/碰撞/散布装配及10张真实GPU图，视觉仍不接受。** 依据16块实际保存网格和独立占用核对，将编辑域西扩为X[-3750,-900]、Z[-4400,-2150]；14块共9410点改变，原XZ拓扑保持，2276个实际散布实例重新落地或移至干坡，总54800保持。原生源在 `captures/highcoast_study_36a/`，候选原生地形场景/散布资源在36a run的 `images/native-scenes/`。运行passed、错误日志为空，根与独立审查直接查看10图；近海连续大陡坡、暗部细节丢失、云板/旧云岩球和水光仍需返工。65步是自动相机观察，不是载具输入验收；末点虽有50m竖向净距，前方约25m的真实陡壁仍遮满画面。河口确有海面下床，但第8个上游控制点实际为约238.5m山坡，不能称8点全部潮汐通道。接续 `reviews/round-36b-highcoast-design-brief.md`：调整低岬/草肩/林坡/远峰层次，增加沿岸观察并改正前方爬升路线。独立结论和绑定见 `reviews/round-36-root-evidence.json`、`reviews/round-36-worklog.md`。36a原生/GPU均已结束，不重跑旧版；生产17e/18c/19h未改，全部20参考与原开场Goal保持active。以下历史不能覆盖本段。

**最新35风暴空间候选已完成两版Blender云体与三轮真实GPU，整体仍未视觉接受。** 35a三资产17件为厚黑囊串，七图打回，独立发现雨条按顶点循环可从9m拉长到891m；35b改为三资产六件连续云体，改善橙色漏光并增加可见闪电，但八图仍有大云板/重复边形/旧云褐岩球，且四条GLES材质null错误令run failed。35c保留35b真实云几何，按实例统一雨条循环、flash场中心对齐实际Omni，并把原/新材质引用保留在场景；八图运行passed，先前材质错误未再现但根因未隔离。根直接看完23张原图，各版独立报告已完成；35b失败图无manifest绑定，另在根证据中绑定，不伪改其状态。阴/锋/晴三世界位置、空间雨与闪电可复现，仍非完整连续飞行证明。三资产源在 `captures/storm_cloud_assets_35b/`，运行接续35c；地形/33f港岸/岛屿保持未完成候选，生产17e/18c/19h未改。下一步按 `reviews/round-36-highcoast-design-brief.md` 制作真实近海高岸、河口和山体纵深；12候选地形块仅完成来源清单，尚无36模型。云、水、其他天气、内景及全部20参考/原开场仍在Goal active范围。详见 `reviews/round-35-root-evidence.json`、`reviews/round-35-worklog.md`。全部35 GPU/Blender进程已结束，不重跑旧版。以下历史不能覆盖本段。

**最新34c/d/e海面均完成五张真实GPU图与独立审查，整体仍需视觉返工；海岸接续33f。** 34c改为按水面点反射实际月心/半径，恢复蓝色粗糙反射层；34d绑定4塔与9村灯真实灯芯，并以真实塔身不透明面替代反射查询中的粗碰撞体；34e加入54港岸灯至67源。暖反射仍是零星点/软橙片，海面横纹与近处宽片仍未达到参考。34e的.024/.006粗糙度、18倍增益是显式艺术参数，不能称物理标定；静态64×32遮挡图每源只覆盖450m，细遮挡边界近似，仍无完整云/岛/屋窗场景反射。34c重复记录材质绑定的问题在34d/e按实例去重为1，不能把34c的两条记录说成两个独立材质。三run均passed，15原图根已直接查看，全部GPU进程结束；继承33f土地支承，不重复8839铺地检查。水仍为平几何配材质分片法线。详见 `reviews/round-34e-root-evidence.json` 与 `reviews/round-34e-worklog.md`。当前33f/A32f/B20l/C-D31i保留为未完成候选，生产17e/18c/19h未改。下一步围绕参考可见差距继续真实场景制作，并推进同世界其他参考区域和天气；不能用灯点参数循环代替全部20参考。完整20参考及原开场Goal active，未接受、未完成。以下历史不能覆盖本段。

**最新34a/b海面已各完成五GPU与独立审查，均需视觉返工；海岸接续33f。** 34a较宽片面/反射过滤消减细梳纹但变近处大软斑、远光不足；34b增加坡度分布并反射有限月盘，软斑消失但成稀疏纯白碎片，缺少参考蓝白水光层。两run均passed，固定日夜/近水/侧移/18秒实际身份核验，土地/岛屿保持；继承33f屋路支承，未重复8839铺地检查。水仍平几何，材质共享高度场提供分片法线，不能称真实位移波面。34b月盘是固定方向/参考距离角度近似，下一稿需实际月心逐水点方向、粗糙反射与亮核心层次、实际港岸灯源倒影/遮挡。详见 `reviews/round-34c-water-design-brief.md`、`reviews/round-34-root-evidence.json`，尚无34c产物；34a/b准备与GPU已结束，不重启。当前原生海岸 `captures/rightcoast_study_33f/mainland_headland.blend`，保留12件可编辑源、A32f/B20l/C-D31i/27d云/28h灯。生产17e/18c/19h未改，全部20参考及原开场Goal active，其他区域、天气和内景仍未完成。以下历史不能覆盖最新状态。

**最新33f海岸阶段候选已完成原生、五GPU和独立审查；下一步34海面与灯火。** 33d以真实占用外168面重拓扑宽湾，改善33c高窄切面，但仍是宽陡扇坡/窄岸唇。33e四组86点试改，前两屋前长灰片减轻，主图两组反而碎化，且beautify产生一处真实XY折回，整版拒绝。33f从33d精确XYZ映射，仅合并前两命中同连通组55点，排除主图31点，恢复旧对角线；实际12件/16804GLB三角同版，165改动面无新增XY叠片和真实占用侵入，屋路支承与33d湾底保持。三个run各五GPU均passed，每版81基础探针、8839铺地样本和28命名树核验，岛屿落点保持；程序通过不等于美术接受。当前源 `captures/rightcoast_study_33f/mainland_headland.blend`，同世界装配在33f run，A32f/B20l/C-D31i保持。证据 `reviews/round-33f-root-evidence.json`、`reviews/round-33f-worklog.md`。本阶段原生/GPU/独立均结束，不重跑旧版；34运行状态以最新run/句柄为准。生产17e/18c/19h未改，全部20参考及原开场Goal active。以下旧阶段为历史。

**最新33右岸已完成三版原生、各五GPU与独立审查；以33b未完成底稿接续，33c不升级。** 33a提高岸肩/后山但近坡过大；九pad旋转方向错误已记录，实际完整屋路支承碰巧由更大冻结面保持。33b改用独立九真实基础+922实际铺地投影，降低后退山脊；完整实际支承与外部侵入检查通过，显式冻结域仍有约0.221683m²漏片但其真实面保持。33c从33b仅降17点试低工作岸，结构范围内支承保持，实图新增高窄切面/低岸唇，视觉拒绝。三run都passed；各8839铺地样本、81屋基探针和28命名树记录核对，岛屿落点保持；不是艺术接受。部分屋旁尖面已确认来自保留26b源，不能继续只改新山脊。接续 `reviews/round-33d-rightcoast-design-brief.md`，在真实占用外缘重排低岸—坡脚局部网格。当前右岸源 `captures/rightcoast_study_33b/mainland_headland.blend`；完整同世界装配在33b run，A32f/B20l/C-D31i保持。全部33建模/GPU和独立进程结束，不重启旧版。证据 `reviews/round-33-root-evidence.json`、`reviews/round-33-worklog.md`。尚无33d，生产17e/18c/19h未改，完整20参考及原开场Goal active。以下旧阶段是历史。

**最新32f前景A保留为阶段候选，下一步33右岸。** 32c跨界约束失败未导出；32d重建紧凑草肩、错位厚崖与树肩，完整塔阶极小区域未平；32e扩大塔坪、左屋转向、右屋降低1.5m和左树降低，三建筑完整底面及八棵真实树干底支承通过；32f修复屋坪混合的高度跳变。32d/e/f各五张真实GPU原图均已直接审查，32f运行passed，全部绑定SHA核对，46非A落点差0、8/8树存在。32f实际尖瘦面880/884仍为89.149°/85.223°，不能称沟坡全修；宽岩墙/按钮凸块仍未美术接受。当前原生 `captures/foreground_island_study_32f/island_a.blend`，完整冻结装配和最终审查见 `reviews/round-32f-worklog.md`、`reviews/round-32f-root-evidence.json`。下一步依据 `reviews/round-33-rightcoast-intake.md` 与 `captures/rightcoast33-main-view-localization.json` 制作不等宽岩岬、低湾和后山，再处理水面；右岸以26b保存源和真实9屋/922铺地为准，不回23g。全部32阶段及只读33进程结束，无待等句柄，不重跑旧生成/验证。生产17e/18c/19h保持，全部20参考及原开场Goal active。以下旧阶段记录为历史，不能覆盖本段最新状态。

**最新32b前景A已完成原生、五GPU和独立审查，整体返工。** 两屋在固定主机位恢复完整可读；11件保存源与实际GLB一致、完整三建筑底足迹及其cap/core支承通过限定检查。32a新屋过渡误改塔脚的失败保留，32b已修正。五图实际46个非A落点差0；8计划树只落7，run因此明确failed，night/day引擎阶段均passed且全部进程已结束。左后四树仍存在但低坡被高屋坪遮挡，仅(-30,-3)一棵因陡坡被过滤。主图草舌仍遮崖、旧岩尖薄、宽直墙及两屋绿锥台仍需真正改形。下一稿按 `reviews/round-32c-foreground-design-brief.md` 仅重构A紧凑草肩/厚岩崖/短路和树肩；保留两屋与塔的入画进展，不继续全岛水平压缩、不回C/D隐藏面反复。实际源 `captures/foreground_island_study_32b/island_a.blend`，七主图源射线 `captures/foreground32b-visible-grass-localization.json`，审查和绑定见 `reviews/round-32b-worklog.md`。尚无32c模型，不重跑32a/b已结束的生成或引擎。生产17e/18c/19h未改，完整20参考及原开场Goal保持active。

**下一步按固定参考总图推进32轮：先前景A，再右岸层次，再海面光色。** 独立直接对31i夜/昼主图与ref1342，确认前景A的大平草台、被遮住的岩崖和塔/两屋/树群关系是第一项主要场景差距；其次右岸岩岬/低湾/后山与港村纵深，第三为密集横向水光和暖灯层次。C/D31i保留为未接受候选，其背图仅为结构诊断，不能以无原图的隐藏面假精度无限阻塞主视图和全部20参考。请从 `captures/lantern_islands_study_20l/island_a.blend` 做独立新版本的精细原生前景地形，先核实际建筑/树/路与参考投影，不重跑旧整套生成器或覆盖生产。原生路径和实际世界锚点见 `reviews/round-32-source-pointers.md`；独立优先级 `reviews/round-32-reference-priorities.md/json`。尚无32新模型；31i全部原生/GPU/审查已结束。完整20参考及原开场Goal保持active，未减少场景或天气范围。

**最新31i真实宽肩、五GPU及独立审查完成，整体仍未接受。** 从31h实际壳体移动5控制点、切4共享边点，形成2片有前后缘的肩顶与前断面；主壳1116点/2228三角。西肩净宽3.630m、顶24.834m²、前折28.104度；东肩净宽2.280m、顶9.928m²、前折93.978度。共点、road/pad/14真实干底支承及60变化三角对整壳1053候选的局部自交检查通过，不能以此当美术接受。大灰罩坡、强暗口/突檐、低根与旧岩分离、前部孤立石仍待改。201绑定、五图59落点最大差0.076294mm、基础0.030518mm；原生/GPU/审计均结束。实际31j前后缘调查 `captures/island-31j-edge-intake.json`仅定位，未生成31j。接续 `reviews/round-31i-worklog.md`、`reviews/round-31i-island-independent-review.md`、`reviews/reference-view-1342-progress-31i.json`；完整参考总图优先级另由fidelity_reviewer复核，不能以无参考背面局部打磨代替全图及全部20场景。生产17e/18c/19h未改，完整Goal active。

**最新31h材质修订、五GPU与独立审查已完成，整体仍未接受。** 31g真实重接已删除448选面与637旧内部边，70边界保留；31h仅把其中72面草材质改为裸岩，12上坡面保留草。19原生件及3624实际GLB三角与31g按原浮点逐三角完全相同，可继承31g局部自交和road/pad/14真实干底支承结果，不重复全扫。大绿板错误修复，但背面仍是大灰罩坡，上方草三角零碎，中层短肩/错高折面、低根与旧岩接续及前部两孤立凸石仍需真正改形。31h实际201绑定、五图59落点最大差0.152588mm，基础差见runtime JSON。31g/h原生/GPU/审计均结束，失败原图保留；下一步从31h实体的8实际控制点继续，`captures/island-31i-control-intake.json`已记完整一环，仅调查未生成31i。接续 `reviews/round-31g-worklog.md`、`reviews/round-31h-island-independent-review.md`、`reviews/reference-view-1342-progress-31h.json`。生产17e/18c/19h未改，完整20参考及原开场Goal active。

**最新31g真实拓扑重接、五GPU与独立审查已完成，整体仍未接受。** 从31f后坡至水下低根删除448选面与637内部旧边，70边界保持，8控制点重接84面；实际旧窄条/纵向长缝消失，但新面误统一草材质0，造成大绿罩坡。31h正在从相同几何修正材料，不把换色当造型接受。19分件、2220主壳三角，实际局部自交与road/pad/14真实干底支承通过；201绑定、五图59落点相对30k最大差0.228882mm、基础0.106812mm。31g原生/GPU/审计均结束，不重跑；前部孤立凸石及低根与旧岩关系仍需改形。接续 `reviews/round-31g-worklog.md`、`reviews/round-31g-island-independent-review.md`、`reviews/reference-view-1342-progress-31g.json`。生产17e/18c/19h未改，全部20参考及原场景Goal active。

**最新31f原生、五GPU与独立审查已完成，整体仍未接受。** 31e把原长陡面和旧后体共同稀疏切分/偏移，中层斜折和低根转向可保留；31f进一步雕刻高坡、中层及局部海口，海口参与转向，但窄长条、纵向侧缝和前部孤立凸石仍需改形。最终实体为各版island_c.blend，三凸包仅是历史输入。两版各200绑定、五原图、59实际落点相对30k位置最大差0.000137329m。31f原2m树盘有2.835297m²旧线性面变化、最大降低0.040461m，实际树中心保持；按真实pine六边形底部核验，14棵干底投影下连续覆盖且旧面保持，old_tree_disk_surface_preserved=false、actual_tree_base_support=true，不能声称整树盘不变或平底与斜面处处贴合。路径17岩、道路/pad保持；实际局部三角自交/法线检查已完成。原生/GPU进程均结束，不重跑已通过检查。接续 `reviews/round-31e-worklog.md`、`reviews/round-31f-island-independent-review.md`、`reviews/reference-view-1342-progress-31f.json`；当前树轴 `reviews/round-31f-current-tree-axes.json`。生产17e/18c/19h未改，全部20参考及原场景Goal active。

**最新31d原生、五GPU与独立审查已完成，整体仍未接受。** 31c缩短错向前肩但独立凸石感回升，背槽第三体仅接一岸，主斜截残缝1.241701m；31d仅重做第三体，目标中段已实际接两岸，低/高Y岸进入0.791512/1.464791m，但外围/高位仍有缺口，背图仍是长条塞在两大片灰坡之间。下一步联动重塑原坡面与新体交界，形成2–3个前后错位短宽连接面，不继续无条件扩大一个填槽凸包。两版各199绑定、五图及59实际落点，相对30k位置最大差0.000137329m、基础差0；道路/pad/14树盘和17岩/path保持。所有原生/GPU进程已结束，不重跑已通过检查。接续 `reviews/round-31c-worklog.md`、`reviews/round-31d-island-independent-review.md`、`reviews/round-31d-rear-flank-localization.json`、`reviews/reference-view-1342-progress-31d.json`；当前树轴 `reviews/round-31d-current-tree-axes.json`。生产17e/18c/19h未改，全部20参考及原图Goal active。

31d六面有界核验补记：六实际射线与源面全部匹配，六整面均无占用投影；但共享点435一环1107/1108实际碰树盘0.460161/0.008055m²，点408一环24/25/26碰树盘2.533776/5.486331/2.159220m²。不能因命中面无交区就自由拖共享点；沿真实支承边界重划面，或有记录地重贴受影响树。面1973/2181已按整三角的实际凸包支持平面和半空间确认属于第三操作数外壳；1507近竖直，XY投影1.91e-7m²但真实面积8.035m²，不是无面。见 `reviews/round-31d-rear-flank-independent.md/json`。这是下一步原坡联动重塑的边界证据，不是模型或全参考接受。

**最新31b斜肩已完成原生、五GPU和独立审查，整体仍未接受。** 31a平顶按钮造型被打回；31b从30k原壳重新制作，已消除柱帽，但左肩连续顶面偏长、中肩同向及背面旧长槽仍需返工。两版各199冻结绑定、59实际落点，位置最大差0.000167847m；31b基础样本最大差0.000045776m。道路/pad/当前14树盘支承、路径和17岩保持。全部原生和GPU进程已结束，不重复已通过检查。背槽四实际射线与独立复核匹配，三源面无实质占用，最近距扩张pad约1.375m；需按真实边界设计，不能据四点推断整槽成因。接续 `reviews/round-31-worklog.md`、`reviews/round-31b-island-independent-review.md`、`reviews/round-31b-back-cleft-independent.md` 和 `reviews/reference-view-1342-progress-31b.json`。当前树轴记录为 `reviews/round-31b-current-tree-axes.json`。生产17e/18c/19h未改，全部20参考及原图Goal active。

**最新30k宽面与树组重贴已完成原生、五GPU和独立审查，整体仍未接受。** 30h密集折扇已消除，显式宽折面和低肩树组可保留为接续；正面左侧大斜板、中部尖窄切口、背面老直槽仍需返工。19原生件、1936主壳三角；完整道路/pad、路径17岩和五保留树组支承保持。每岛东侧两棵树移位，59实际落点中55保留（最大差0.000122070m），4移位按真实全网格上表面验证，基础样本最大差0.000061035m。当前树轴以 `reviews/round-30k-current-tree-axes.json` 为准，不沿用30d旧东树位置。首次GPU因根节点名检查错误失败，修为实际island_root后r1完成196绑定/五图；所有进程已结束，不重跑已通过原生或GPU。接续 `reviews/round-30-worklog.md`、`reviews/round-30k-island-independent-review.md`、`reviews/reference-view-1342-progress-30k.json`，下一步做短宽凸块和横向错位折面，不继续放大凹面。生产17e/18c/19h未改，全部20参考及原图Goal active。

**最新30h原生与五GPU、独立检查完成，造型仍打回。** 南/东实际可见坡切削后产生密集竖向尖三角和折扇凹面，不能以闭合/支承检查通过当成参考达标。30e/f/g失败未跑GPU，失败证据保留；30h独立刀具面划分成功保存19件，主壳2550三角，路径/17岩及完整道路/pad/树支承保持。六目标实际切深约2.933/2.878/0.104/1.261/0/2.562m，不沿用名义平面削深。196绑定核对，59落点相对30a最大差0.000228882m、基础差0.000076294m。下一稿改实际大面组织和短宽错位肩，避免继续加密刀具边界造成竖向褶皱；旧背面直窄槽仍待改。接续 `reviews/round-30-worklog.md`、`reviews/round-30h-island-independent-review.md`、`reviews/reference-view-1342-progress-30h.json`。本轮原生和GPU进程均结束，无待等句柄，不重跑已通过检查。生产17e/18c/19h未改，全部20参考及原场景Goal active。

**最新30d已完成三处实体切削、五GPU及独立审查，整体仍未接受。** 从30c焊接源用Blender真实切削露出West/Southwest/North低肩，17岩和路径保持；完整道路/pad/现有树轴支承区域几何保持，水上肩露出投影约51.832/43.206/58.213m²。19原生件、196绑定核对，59落点相对30a最大差0.000274658m、基础差0.000000000m。固定参考/背面新增短凹折可保留，但局部切口仍直；day-c-front正面宽灰坡基本未变。**方向纠正：该相机Blender(65,-70,40)，六处灰坡像素实际射线命中南到东侧mainterrain；不能继续全归West/SW/North。** 以 `reviews/round-30d-visible-slope-localization.json` 的真实源面及保护边界决定下一稿，不盲目扩大旧刀具。接续 `reviews/round-30-worklog.md`、`reviews/round-30d-island-independent-review.md`、`reviews/reference-view-1342-progress-30d.json`。全部30d建模/重开/GPU已结束，无待等句柄，不重跑已通过检查。生产17e/18c/19h未改，全部20参考及原场景Goal active。

**最新30c已完成焊接外壳、五实际GPU及独立限定审查，整体仍需返工。** 30b删除主岩中间环并缩短/嵌合岩肩；30c进一步移除真实0.65m地表侧裙和内部重合cap，19原生可编辑分件，实际五图连续细带消除。745地表顶点、全部原顶面/路径及17岩块保持；相对30a的59落点最大差0.000091553m、基础样本最大差0.000000000m，196绑定SHA核验。部分岩肩被主岛包裹，相交不等于可见岩根；下一步以30c源局部重塑外露短肩及相邻大灰坡，优先West/Southwest/North，不能所有岩块统一外移。全部30b/c原生和GPU进程均已结束，无待等引擎，不重跑已通过检查。接续 `reviews/round-30-worklog.md`、`reviews/round-30c-island-independent-review.md`、`reviews/reference-view-1342-progress-30c.json`。生产17e/18c/19h未改，全部20参考及原场景Goal active。

**最新30a已完成原生保存重开、五实际GPU及独立审查，总目标继续active。** C/D实际网格水平缩至0.72、高度0.65，建筑原生尺寸保留，切分重建两个完整pad及315路径顶面；实际路径约45mm贴地、最大坡10.863°。D位置/朝向为有记录的设计调整，守塔屋在固定参考视角中已转至塔右，岛体比例方向改善；上台大岩板、连续双层水线与规则岩根仍需返工，未装生产。196冻结绑定SHA匹配；四受影响建筑重新落地、每座九基础样本通过，未改区域落点最大差0.000000000m、基础差0.000000000m。全部30a原生/GPU进程已结束，无待等引擎句柄，不重跑已通过检查。接续 `reviews/round-30-worklog.md`、`reviews/round-30a-island-independent-review.md`、`reviews/reference-view-1342-progress-30a.json`；以30a保存源继续岸线/中段拓扑，不回到29e过大比例。生产17e/18c/19h未改，全部20参考及原图仍未完成。

**最新29e C/D地表与道路联动改形完成五GPU及独立审查，整体仍需返工。** 234塔屋/树根支承面保持，223显著地表点变化，实际道路贴地44.9986–45.0014mm、最大坡9.6545°；29d三处侧带投影反折消除，局部错位岩肩可保留。196冻结绑定SHA核对，61落点差最大0.1984mm、基础抽样差0.1221mm。**下一步优先纠正C/D陆体相对建筑的高度/宽度，再改岸线断裂拓扑。** 独立人工投影复核显示岛身偏高偏宽，不能把像素比当精确3D缩放值；保持建筑原生尺度，重做合适pad并联动重贴道路/树/建筑与派生碰撞。参考中央守塔屋在塔右，本版塔左，也需校正D朝向/布置。原18岸线/旧61落点是候选设计，不是永久用户约束；其他区域不变。所有29d/e建模、重开、GPU进程已结束，不重启旧失败运行。接续 `reviews/round-29-worklog.md`、`reviews/round-29e-island-independent-review.md`、`reviews/reference-view-1342-progress-29e.json`。生产17e/18c/19h未改；全部20参考及原图Goal active。

**最新29c C/D岛岩完成五实际GPU及独立审查，造型仍打回。** 29a外围尖柱失败；29b改形121地表点、降低主肩、减少压扁礁体，保护证据保留，但上台灰盾/水线带仍不符；29c四斜肩形成长楔斜撑，不作为下一稿底稿。**下一步回到保存29b源，沿真实道路/基础/树根边界切分主岩与地表，重塑错位短肩/宽台/低根，不再叠加长楔。** 最新197冻结绑定SHA匹配，61实际落点最大差0.244mm、9×9基础抽样最大差0.610mm，不能称逐点零差或完整通行验收。所有29a/b/c原生及GPU进程已结束，无待等句柄，不重启旧失败版本。接续 `reviews/round-29-worklog.md`、`reviews/round-29c-island-independent-review.md`、`reviews/reference-view-1342-progress-29c.json`。生产17e/18c/19h未改；完整20参考及原图Goal active。

独立陡面定位补充：按实际29b中心高于10m、normal.z<0.5选出81面，只有13面属于515整面冻结，另68面未冻结；保留道路1.2m缓冲仍有184.24m²投影区域可改。灰盾不能主要归咎于保护限制，下一稿优先改外围高度场过陡衔接和面组织，少数擦边面才需精确切分。定位 `reviews/round-29c-independent-wall-localization.json`，不把该阈值选区当作全部可见灰墙像素。

**最新28h灯塔体积光候选完成三个实际GPU视角和独立限定审查，整体仍未达标。** 修复无光照材质错误输出，使用真实锥体积分、近体积原点求交与宽度/距离衰减，保留光束能量1.3。28e远端橙雾打回；28g对照不支持“灯芯投影挡住自身暖光”的原因判断，28h已保留原灯芯投影。当前184项冻结绑定SHA匹配。所有28原生/GPU进程已结束，不重启旧失败版本。接续 `reviews/round-28-worklog.md`、`reviews/round-28h-lantern-independent-review.md` 与 `reviews/reference-view-1342-progress-28h.json`；继续灯源/暖水光、云水、主岩岸/群岛/聚落与完整20参考范围。生产仍17e/18c/19h，Goal active。

**最新27d云体＋27f水面完成实际GPU及独立限定审查，整体美术仍打回。** 27d三组Blender云/12可编辑体块保留圆肩与真实底面方向；27c尖峰、27d大水斑、27e大三角和27f重复横纹均有失败证据。27d五视图含新云后下方观察，27f四视图含0/18秒，27h仅补两夜图并与27f PNG逐字节相同；全部原生/引擎进程已结束。**先前“月球缺失/等待恢复”是根与初版独立的观察错误，已撤回：27e/f/g/h共7张月区像素完全一致，月球一直存在。** 不再追查这个错误命题。接续 `reviews/round-27-worklog.md`、`reviews/round-27h-moon-observation-correction.json`、修订后的 `reviews/round-27h-cloud-water-independent-review.md` 和 `reviews/reference-view-1342-progress-27h.json`。继续云层/水光/灯塔暖束光、主岩岸和完整20参考范围；27d/e/h均无整图接受。生产仍17e/18c/19h，26b街巷/岸体未改也未重跑。会话Goal已实际读回全部20参考及原图范围，保持active。

**最新26b连贯石铺坡巷完成原生重开、五GPU及独立限定复核，保留改进，整图仍未接受。** 922独立石板/路床替换重复扇贝状台阶边；门口/院落保持水平接口，原九主体屋基、134岸界及底侧几何保留。实际倾斜顶面已单独识别检查；局部薄基床cap有不足1mm土越过，不能沿用25f全cap约48mm净空结论，也不声称全宽通行验收。run `village-paving-26b-20260908T143321Z-441bad8ec7bd4024b195dca93cc8bd82` terminal passed、146绑定SHA核对，根/独立均看完五图。所有26原生/GPU进程结束，不重跑旧版本。当前26b铺地＋26b岸体仅候选，生产仍17e/18c/19h。接续 `reviews/round-26-worklog.md`、`reviews/round-26b-village-sloped-paving-independent-review.md`、`reviews/reference-view-1342-progress-26b.json` 和 `reviews/round-27-next-visual-priorities.md`，继续大岩岸/群岛轮廓、水光、云层与灯塔光束等完整20参考目标。会话Goal已实际读回完整新范围并保持active。

**最新24n已完成五GPU图及独立限定审查，完整Goal保持active。** 当前候选为24m两套铺地1486可编辑实体＋24l局部岸体＋原23g九屋/28松树；原134岸界、底侧面及11岩肩保留。旧窄槽、点接触非流形与旋转复杂轮廓造成的大块石板越层已修复。run `village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7` terminal passed，session19018结束；146绑定SHA匹配，根/独立看完五图，全12083实际cap地形净空≥47.97mm。**仅保留局部修正，整体美术未接受，不装生产。** 高路基像架空连续石带、重复扇贝台阶、巨大灰岩面、规则水光和灯塔束光仍待返工。下一步真实街边填坡/路基砌筑/台阶造型，继续主岩岸及全部20参考。接续 `reviews/round-24-worklog.md`、`reviews/round-24n-village-paving-independent-review.md` 和 `reviews/reference-view-1342-progress-24n.json`；所有本轮root生成/引擎已结束，不重启旧失败版本。生产仍17e/18c/19h。

**2026-09-08 最新接续为23g右岸岬角与九屋组团。** 从23c测量布局制作了独立Blender实体岸体、渔屋、工坊；23d内部长墙经实际三角证据定位为最近岸段高度跳变，23e改连续插值并新增真实背脊、11潮间岩肩和28松树。23f只限pad影响仍未锁岸，未跑GPU；23g同时约束岩脊和pad外影响，实际GLB57个非过渡岸点误差≤0.000000636m，九pad完整裁剪区域高度误差≤0.00000876m。23g五GPU视角run `headland-assembly-23g-20260908T121755Z-4ca247af11bb4af2a7bba06fe2383718` 已terminal passed，126绑定匹配，根与独立均直接看完五图。支持保留局部修正，大片裸岩斜板、齐整台缘/岩鼻、村路与低岸工作区仍未达标；不安装生产。下一步从23g实体继续重做真实岩岸断面及共享街巷/阶梯，不重新生成旧布局和旧采样。详见 `reviews/round-23-worklog.md`、`reviews/round-23g-headland-independent-review.md`、`reviews/reference-view-1342-progress-23g.json`。23d/e/g引擎句柄均已结束；全部20参考Goal保持active，生产仍17e/18c/19h。

2026-09-08 从完整迁移包恢复到 **E:\FeiTing**。主工程直接位于本目录，没有额外的 `test6/` 嵌套。

**最新目标已扩展，优先阅读 [GOAL.md](GOAL.md) 和 [REFERENCE_SCENES.md](REFERENCE_SCENES.md)。** 用户要求在同一个可飞行3D大世界中实现 `ref/` 全部20张参考及原场景，覆盖天气、时段光照、群岛、雪山、湖海、港口、云海与舱室内景；继续Blender精细建模并统一风格。只实现场景，人物/角色跳过；不新增参考UI制作。20张图均已直接查看，连同原图共21份图像身份已记录 `reviews/reference-catalog-20260908.json`。后文旧单图/UI目标为历史，不覆盖最新用户范围。

**当前生产为17e两件岩体 + 18c独立地表材质 + 19h共享灯塔，均完成相应阶段的原生集成复核。** western_slab/front_columns来自17e，crown/central_wall仍16g，其余几何承接10l。19h修改7个灯塔相关文件，原生源/模型/材质/派生网格与碰撞已安装，两位置不变。各阶段接受均不代表全部参考场景完成。不要从旧16b/17a/旧灯塔重复制作。

**最新完成：19h最终run `19h-native-lighthouse-final-20260908T082434Z-482422f7fede4b64b58f197a71159771` 十阶段全部passed，独立复核支持保留建筑底稿。** 两实例24表面、3988三角、32墙面射线、完整派生网格/碰撞顶点误差均0；八张GPU图和36游戏项完成，根代理与独立代理均直接查看全部八图。报告 `reviews/round-19h-native-integration-independent-review.md`，80绑定文件审计同前缀JSON。首次081741安装因空切线数组失败；082039修复成功派生后，因透明枚举检查过窄失败。两个失败包原样保留，最终082434只验证，不重复安装/导入。正式导入8玻璃alpha.27、5透镜alpha.10、ALPHA_DEPTH_PRE_PASS已确认。不要再执行一次性安装或重复通过的验证。远端高首阶/裸草地入口仍需场地设计，不作步行验收。

**当前最新候选20l，岛礁仍未生产集成。** 20i/j实拍及独立量测打回陡峭路基；20k缩小塔平台保护范围，新增经实际SeaCollision中心核实的D中景岛（C资产旋转复用），调整近景机位。20l真实连续路基混合修复A汇合口同一三角61.86°→6.01°；独立实际GLB和21a昼景支持有限保留。B坡道仍有较大陡坡比例，台阶/步行未验收。C/D高灰墙、沿岸规则叠层、大片草盖与右岸聚落仍待返工。详见 `reviews/round-20-worklog.md`。

**最新环境候选21c已经完成两个受影响GPU夜视角。** 21a过黑/密星/方格月盘/条纹水光打回；21b用Blender保存4套实体月球/三类云体，实际重开源验证和三GPU图完成，星域/月体有限保留，整体仍打回。21c经本机Godot运行时核实，把夜间环境光来源从SKY明确改为COLOR，真实图恢复原生塔/屋/岩体层次；保存来源/颜色、四灯世界位置及已遍历未映射材质列表。两夜图根已直接看完，独立范围以 `reviews/round-21c-environment-independent-review.md` 为准。全部21a/b/c引擎会话已结束，不重复旧运行。1342候选机位登记 `reviews/reference-view-1342-progress-21c.json`，状态明确未接受。生产仍17e/18c/19h，所有岛礁/天空/环境为临时候选。流式环境、其他天气、暖束光、完整岸村与自然岩岸/水光尚待制作，详见 `reviews/round-21-worklog.md`。

**最新接续22g港岸候选已完成七GPU视角与独立复核。** 22b六港口模块的板梁/钉头修复保留；22f新增4套Blender石阶，3516独立部件、586分格、28组实际约1.19m平台，连接既有码头与门阶。4路长约50–82m，不再是22b尚未建成的旧直线调查。22g装配23屋/4码头/4船/54港岸灯，每图1758组实际上下碰撞与原地面射线通过；4船外移后138低顶点/船最小原地形净空约0.576m。原世界和生产保持不变。所有22c/d调查、22d/e失败生成、22f检查、22f失败GPU及22g最终GPU句柄均已结束，无待等进程。

**整岸仍不符合1342，不得直接安装或标记完成。** 当前长灰阶梯直通孤立同型屋、大片空草坡及缺失的近右岩岸村落必须继续返工；优先实际相机投影/原地形测量、Blender局部岬角/岩湾与住宅组团、沿岸短街巷，之后继续岛壁/水光/灯塔束光。独立 `reviews/round-22g-harbor-independent-review.md`、`round-22f-path-independent-geometry-review.md` 已完成。冻结run `harbor-assembly-22g-20260908T112011Z-00f0a7b4c813446e842b280476463e21`，当前参考登记 `reviews/reference-view-1342-progress-22g.json`；完整范围、失败前驱和实测限制见 `reviews/round-22-worklog.md`。22f首次GPU因WASAPI设备失效保持failed；22g仅视觉采样用Dummy音频、真实GTX970/OpenGL不变，不等于音频恢复验收。

所有旧迁移、19h安装及20/21/22已完成运行均不得无原因重跑。会话Goal仍为全部20参考范围active，包含同一连续大世界、多天气时段、Blender精细建模、统一风格及跳过角色。实际Goal更新回读记录位于 `captures/goal-update-20260908`。

## 已完成的迁移恢复

- 用户给出的旧路径 `E:\Aether\_Migration\_20260906` 不存在；最终交付目录实际为 `E:\Aether_Migration_20260906`，与交付入口说明和历史用户确认一致。
- 主 ZIP 和全部 16 项校验清单在本机重新计算 SHA256，全部一致。主包保留在原交付目录。
- 完整展开 220,703 个原文件及 2 个控制文件，包含隐藏工具、导入缓存、Blender 源模型、试稿、旧构建、截图、运行日志、历史、附件、Python 和存档备份。
- 首次 Godot 导入前，按原清单检查所有 220,703 个文件的大小和 SHA256：缺失/损坏 0。迁移包附带的 `Verify_Extracted.ps1` 也完成并打印全量 PASS。
- 随包 Python 3.10.1 及 numpy、scipy、cv2、PIL、shapely 已在本机运行通过。本机默认 `python` 是 2.7，因此 `tools/validate_demo.ps1` 已改为优先选择包内 Python。
- 核对四份原始会话快照的大小与 SHA 后，把主任务 307 条补录追加到新建副本，得到 8,088 条合法 JSON 记录。没有改写四份原始快照或本机 Codex 全局数据库。

恢复总报告：[RESTORE_COMPLETE_20260908.json](MIGRATION_20260906/RESTORE_COMPLETE_20260908.json)。首次字节核验：[RESTORE_BYTE_VERIFY_20260908.json](MIGRATION_20260906/RESTORE_BYTE_VERIFY_20260908.json)。历史补录与合并副本位于 [restored_history_20260908](MIGRATION_20260906/restored_history_20260908/)。原交付旁文件的副本在 `MIGRATION_20260906/delivery_sidecars/`。

**工程已经继续工作。** 后续 Godot 导入缓存、运行报告和验证入口修改是预期变化；不要再为匹配迁移清单而还原新工作。首次全量校验报告记录的是导入前状态。

## 本机源工程运行证据

运行目录：

`captures/validation_runs/restore-20260908-20260908T014334Z-65c6290b091c4a99806b7cf3b9c2db9b/`

Godot 4.5.1 使用 NVIDIA GTX 970 的真实 OpenGL 渲染器，导入、开场/侧/背/反向四视图、36/36 项源游戏检查通过。包括飞行、转向升降、碰撞相关检查、停靠补给、流式地形、环绕相机与隔离文件的保存恢复；详细范围以本轮报告为准。

开场与旧 10l 冻结图大小相同，最大通道差为 1/255，平均绝对通道差约 0.000000847。新旧 PNG 字节 SHA 不相同，没有宣称逐像素完全相等。比较文件为本轮 `machine-render-comparison.json`。

这次是源工程恢复检查，没有重新发布 Windows 包，也不代表美术验收通过。

## 已接续的制作与审查

**16g集成历史：三件前景资产完成12个限定检查阶段。** 当时crown/front_columns/central_wall来自16g，其余几何承接10l；之后western_slab/front_columns又由17e更新，见本页最新状态。运行 `captures/validation_runs/16g-native-integration-20260908T051154Z-276e28776e864ea7bdffae2d9da929d5/` 保存旧三件blend/GLB与kit备份、独立16g阶段接受报告、实际变更和完整passed manifest。

实际刷新3个独立prefab实例的网格及派生碰撞；地形刷新0，受影响植被检查后移位0/移除0。源依赖变更恰为14项：三blend、三GLB、三mesh、三collision和两份catalog；World、prefab文本、地形、道路、scatter资源SHA没有改变。原生刷新自己的派生资源备份在 `captures/edit_backups/2026-09-08T13-12-21-2551/`。

本轮包括导入、限定刷新、开场/侧/背/反向4个真实GPU视图、36/36游戏项、6/6岩区巡游、21/21岩体接触、4,472个rim接地采样、40,642个道路采样和18/18地貌几何检查。导入/刷新之后冻结输入，所有检查与截图完成后全输入和证据SHA仍一致。没有重复整世界生成，也没有发布Windows包。

原生开场、侧图与16g临时审查图逐像素及PNG字节相同；背图有1,549像素差异，最大通道差15，局限于[208,93,616,227]远景范围，前景无差异。`reviews/round-16g-native-image-comparison.json`记录量测；不能称三图全部完全相同。这些限定技术结果不代表参考视觉目标完成。

原生集成最终独立审查也已完成：`reviews/round-16g-native-integration-independent-review.md`与对应audit JSON。独立核验66项绑定产物、12阶段/6报告、三件GLB与blend身份、表面门禁SHA及14项变更，支持保留当前生产阶段底稿。World、208个地形场景、1,546个scatter文件与原记录相同。背图差异原因尚未确认，不能臆测；y≥300区域逐像素相同。完整目标保持active。

`build/` 保持历史 **09n**。11i 雪山、12c 地表、13b UI、14c 云体均保留为未集成研究。原生材质所有权修复保留。

重新建立独立审查 agent，实际检查参考和上述候选的 13 张原图，仍未通过。报告：[restore-20260908-candidate-review.md](reviews/restore-20260908-candidate-review.md)。随后以实际 GLB 定位前景齐腰色界、直柱和接地边界，见 `reviews/restore-20260908-cliff-upper-control-audit.json`。

新的独立 Blender 制作：

| 候选 | 实际内容 | 状态 |
|---|---|---|
| 16a | crown、front_columns、central_wall 三件独立资产；30 个上部控制移动，完整 253 个接地边界点和封底不变 | 三视图已生成，独立几何核对完成；视觉打回，陡绿墙和尖片感仍明显。模型及失败审查保留。 |
| 16b | crown 新增 8 个实际台肩点与 16 个三角，把低处草肩与上部裸岩分开；原 8 个 ridge 控制与完整 rim/floor 不变，减弱中央凹沟尖折 | 独立复核确认真实坡折和相较 16a 的进步，可保留为下一稿；视觉仍未通过，草肩窄折带与尖长暗壁需继续改。未集成到生产。 |
| 16c | crown 修正横向高差，分别调整各列草肩宽度 | 两处约52°陡面降到14.77°/13.71°，真实改善；视觉打回，前缘相对原脚部仍悬挑12–20m。 |
| 16d | crown 前缘收回，峰体8个ridge沿固定轮廓后退4–16m，向后取得实际草肩宽度 | 独立核对前悬收回及中央壁解除遮挡，可保留为后续底稿；中央长壁、绿帽、左肩仍不合格。 |
| 16e | central_wall 增加两排共10个顶点、20三角，制作不同宽度/高度的真实中段岩台；crown保持16d | 实图出现连续灰色台阶带，独立打回；局部上段还有悬挑。保留失败稿，不作为后续默认底稿。 |
| 16f | central_wall 改为单排5点/10三角，并降低4个上帽控制 | 局部视觉改善保留，但3件候选均未通过既有投影表面门禁，不能直接集成。 |
| 16g | 修复8处折返，crown前两列XZ归位，9个中段控制收回foot/front之间，减少中央凹沟后退 | 既有五件表面门禁全通过；独立接受三件组合作为下一阶段前景底稿，已完成原生集成和12个限定阶段。完整视觉仍未通过。 |

同版本实拍目录：

- `captures/validation_runs/foreground-16a-20260908T014632Z-2519ed7bd0c948c5845bc7e6fa0664a2/`
- `captures/validation_runs/foreground-16b-20260908T015118Z-c8ff6b7fed9d4c7dad11c4ffb2dac90d/`
- `captures/validation_runs/foreground-16c-20260908T044445Z-c8470ae2ac4c4908bb4ed853001e78e1/`
- `captures/validation_runs/foreground-16d-20260908T044954Z-1577d1ffdda64be881de773769a52a8c/`
- `captures/validation_runs/foreground-16e-20260908T045337Z-fb6e18a6381f4ff3a999a777ef89b566/`
- `captures/validation_runs/foreground-16f-20260908T045736Z-e74eb3b4aef7419f99ddd9ad5405864d/`
- `captures/validation_runs/foreground-16g-20260908T050716Z-0831944f67c2433c95b8fdc2f0721364/`

每次目录包含三张原始 GPU 图、场景/运行输入 SHA、冻结的三件 GLB 和 `.blend`、制作脚本及完整日志。Godot 在临时实例中替换独立模型，并从实际网格派生碰撞；没有保存覆盖原生 World 或生产 prefab。

16c 已解决16b两块特别陡的横面；16d又收回前悬。不要重复从16b开始。16d开始的8个ridge确实变化，不能再声称峰顶点不变；完整rim/floor仍保持。16e中段阶梯失败；16f单排方向保留但表面门禁失败；16g已修掉定位的8处折返，既有门禁全过。最新独立证据为 `reviews/round-16g-independent-review.md`、`round-16g-independent-geometry-audit.json`、`round-16g-independent-repair-checks.json`。中央草帽仍有43.83/60.46/47.31°面，碎三角、双绿色带、western左肩及整体造型仍未完成。

表面门禁入口 `tools/check_foreground_surface.py` 读取实际GLB，并沿用历史5件section的投影重叠/负Y检查；闭合与正体积不能替代它。已运行16f失败、16g通过，各报告保存于reviews。三角投影门禁不等同完整3D自交或跨资产检查。

制作入口：`blender/sculpt_foreground_16.py`。临时原生组装：`captures/preview_foreground_16.gd`。拍摄驱动：`tools/render_foreground_study.py`。每一版制作脚本另随候选冻结，不要覆盖已有候选目录或失败运行。

## 在本工作区继续

### 17系列左肩与18系列平原研究（17e与18c已集成）

17系列从当时16g生产的western_slab和front_columns分别制作，入口 `blender/sculpt_foreground_17.py`；目前17e已集成，不能继续假设制作器读取的源仍为17a时的原件。各版完整原件和制作脚本保存在 `captures/foreground_study_17*/`，后续改形应显式承接当前源或冻结版，不覆盖已有证据。

- 17a把左肩峰脊加深，前草面拓宽，但后肩压成约69–83°亮绿屋面；独立打回。
- 17b联动中部后肩，按实际坡向收回亮度，并在暖壁增加2点/4三角真实凸折。中部改善，右端仍约77–78°，暖壁仍大盾形；独立打回。
- 17c协调ridge14/shoulder19，前端两面44.63/44.42°、中后两面约69°；最后接地面却仍75.72/75.30°。独立审查定位face31直接包含shoulder18与固定rear24/rim，并不包含19，当前组合不集成。
- 17d试图把端肩收回原XY，实际导出triangle41（原生14/29/19）发生翻折，投影重叠0.79279m²。门禁失败，未启动三视图；候选/日志/门禁完整保留。
- 17e保留17c安全XZ，联动降低shoulder17/18，暖壁凸脊改成不对称的主宽面/窄侧面。五件表面门禁通过，三视图完整，独立接受为局部阶段底稿，已完成原生集成。最后接地两面约71.18/65.06°，中段另两面60.29/52.27°反而略陡，不声称全部回缓。
- 18a仅在临时原生场景的208地块和新生成地形上应用实际世界坐标材质，绿黄分区改善但平原过于柔滑；独立打回。18b保留更多原生角面明暗并缩小色块，三视图已完整通过，独立仍要求改软云斑。18c用flat varying让实际三角内生境保持一致，独立接受局部材质阶段，**已安装生产**，reverse偏碎需继续收敛。三版临时冻结图基底均为16g，不含17e；最终原生组合图含17e。没有改变地形几何，不能声称岸线或坡体已修复。

同版证据目录：

| 研究 | captures/validation_runs 下的完整目录名 |
|---|---|
| 17a | foreground-17a-20260908T052533Z-6a401f176d114e479ab5df42a62ce079 |
| 17b | foreground-17b-20260908T053151Z-3df2be38da6c491cb2077411e3b0b2f6 |
| 17c | foreground-17c-20260908T054044Z-525badfcbf934a50930e08761a168a5c |
| 17e | foreground-17e-20260908T055006Z-348ac27ec16f49c6bc196accd90eba32 |
| 18a | terrain-18a-20260908T054408Z-468a16d6942b49f7bfe0c6fb4d301c28 |
| 18b | terrain-18b-20260908T055159Z-5102c364e52c495d8f7dfaeda1c4637f |
| 18c | terrain-18c-20260908T055452Z-686b396248a042c1900b69a901eb18a3 |
| 17e原生集成 | 17e-native-integration-20260908T060301Z-07dc7a9c264c45aab408ab67177a7dfd |

独立报告按 `reviews/round-17*-independent-review.md` 与 `round-18*-independent-review.md` 保存，已完成和待审查以实际文件及上述状态为准。材质入口 `captures/terrain_grade_18*.gdshader`，临时组装 `captures/preview_terrain_18.gd`，冻结三视图驱动 `tools/render_terrain_study.py`。后续应继续这些已定位问题，不要重复从17a或18a原样运行。

17e原生集成12阶段完整passed：导入、2件限定刷新、4张GPU图、36游戏项、6岩区巡游、21接触、4472接地、40642道路采样、18地貌检查。实际源变化11项：两blend、两GLB、两mesh、两collision、两catalog及 `assets/scatter/Grounded_rock_0_-1.res`；World、地形和其他1545个scatter文件保持。源备份在集成run及 `captures/edit_backups/2026-09-08T14-03-19-2182/`，一次性集成器 `tools/integrate_foreground_17e.py` 不应重复运行。

独立集成报告 `reviews/round-17e-native-integration-independent-review.md` / audit JSON核对64项绑定产物、12阶段和11项变更，支持保留局部生产底稿。原生/候选差分为opening1121、side3226、back1839像素，不能称图像完全相同。背图1546像素属y<300远景，原因未知；293为近景。实际有一块散布**岩石**重贴地（不是树）：GPU只读核验 `reviews/round-17e-rock-refresh-verification.json` 确认30实例中仅index2的Y从62.27490234375变54.01611328125，XZ和basis不变，当前原生碰撞表面误差0。技术和局部阶段接受不代表旧单图或新增20图完成。

运行源游戏：双击 `run-3d.cmd`。编辑源工程：双击 `open-editor.cmd`。Blender 资产库：`open-assets.cmd`。

```powershell
.\MIGRATION_20260906\python-portable.cmd tools\validate_restored_workspace.py
.\MIGRATION_20260906\python-portable.cmd tools\render_foreground_study.py 16g
```

这两项验证都会创建新的唯一运行目录；只在有新改动或需要明确复核时运行，不要重复已经通过的同版关卡。`tools/integrate_foreground_16g.py`是本次一次性有备份的集成记录，不应重复执行：它检查原始源SHA，当前已是新源。完整功能/物理/发布验证继续使用 `tools/validate_demo.ps1`，按实际改动选择是否导出。

完整用户目标以最新 GOAL.md 为准：统一大世界全部20张参考及原场景，覆盖真实建模、天气和时段光照，角色跳过，不新增UI还原。不能把迁移成功、功能通过、几何闭合或某个局部研究当成总目标完成。

下一阶段从当前17e几何与18c材质底稿继续。区域设计见 `WORLD_SCENE_PLAN.md`，采用现有原生港口/山系锚点，新增地理关系明确作为设计提案。共享灯塔已迭代19a/b/c/d，19a黄板/偏白打回、19b透明和中灰修正保留继续、19c缩短拓宽但一根杆件变换有误、19d修正该错误后四图及独立审查完成，支持保留作后续建筑底稿，尚未集成生产。详见 `reviews/round-19-worklog.md` 及 `round-19d-lighthouse-independent-review.md`。下一稿先收敛石材横带、玻璃和灯芯可读性，并优化多岛实例的导出分件组织；然后继续岛礁/港岸与天气时段、雪山沿岸/镜湖/峡谷、云海/舱室，持续精修旧开场。只把经过同版本审查的局部改进送入原生流程，同步派生碰撞和实际受影响的地形、道路、散布物。不重跑整体世界生成器，不覆盖手工权威 `cliff_eastern_plateau.blend`。

### 18c原生材质安装：原收集失败、独立恢复证据通过

原运行 `captures/validation_runs/18c-native-material-20260908T062423Z-e13cc07350264b9d800603025868e010` 保持failed：8个引擎阶段均实际完成，但最后stream报告收集器错写成 `captures/stream-validation.json`；生产者实际写 `captures/stream-flight-validation.json`。没有改写原manifest。

恢复包 `captures/validation_runs/18c-material-evidence-recovery-20260908T063226Z-ce87559c6bcd43c188f89f7c2d233c20` 为passed，重执行引擎阶段0。独立最终报告 `reviews/round-18c-native-material-final-review.md` / final-audit.json核验251个绑定文件、原失败manifest原样副本、原stream身份/源SHA/执行时间窗及正确报告。底层结果为7项原生材质检查、36项游戏检查、四方向飞行通过；导入和四张GPU图也完整。不要称原运行manifest通过。

安装差异213项：208地块场景只替换地形材质路径，其余为独立terrain材质/shader、open_world接入、验证脚本及shader UID。几何、地形碰撞、world共享材质和17e岩体/重贴地岩石保持。单独地形材质覆盖原生208块及Generated_ground，树/道具继续world材质。一次性 `tools/integrate_terrain_18c.py` 已修正确报告文件名，但不应重复安装当前源。候选与原生有像素差异，反向部分差异原因尚未确认，不声明完全一致或20场景完成。
