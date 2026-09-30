# 场景还原迭代记录

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

**当前24n已完成五GPU图与独立限定接受，整体美术继续返工。** 24m铺地1486可编辑实体配24l岸体，保留原134岸界/底侧/11岩肩。真实run `village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7` terminal passed、146绑定核对；根与独立看完五图，全12083实际cap无地形穿透。但高而光滑路基、重复扇贝台阶、大灰岩面和规则水光不符合参考，不装生产。下一步街边真实填坡/砌筑层次/台阶造型及主岩岸、水光，全部20参考Goal保持active。见 `round-24-worklog.md`、`round-24n-village-paving-independent-review.md`、`reference-view-1342-progress-24n.json`；本轮root全部进程结束，不重复旧失败运行。

**最新23g：真实右岸岬角、九屋两组团及28松树已完成五GPU视角和独立增量复核。** 23d长墙定位并在23e消除，23e未锁低岸问题在23g分别约束岩脊/pad外影响后修正；23f原生中间稿保留、未跑GPU。独立实际GLB确认57岸点误差≤0.000000636m、九pad完整区域误差≤0.00000876m；11岩肩几何与23e不变，两新屋GLB字节相同。23g run `headland-assembly-23g-20260908T121755Z-4ca247af11bb4af2a7bba06fe2383718` 五阶段passed、126绑定，根/独立均看完五图。岸高修复局部保留，齐整崖裙、巨大裸岩面、岩鼻和无共享道路的屋群仍未接受，不装生产。接续 `round-23-worklog.md`、`round-23g-headland-independent-review.md` 与 `reference-view-1342-progress-23g.json`，继续真实岸壁断面、共享阶梯/街巷和低湾工作区；全20参考Goal仍active。旧轮次记录保留，不重复旧运行。

**2026-09-08最新目标扩展：以根目录 `GOAL.md` / `REFERENCE_SCENES.md` 为准，覆盖ref全部20图与原图，属于同一可飞行3D世界，含多天气/时段及室内场景。只实现场景、跳过人物角色，不新增参考UI。下方旧单图与UI内容保留为历史。当前生产已完成17e两资产、18c地表材质及19h共享灯塔的阶段集成复核；总目标未完成。19h最终run十阶段/八图/36游戏项通过，两个失败前驱保留，详见round-19h-native-integration-independent-review.md。20轮岛礁已接续到20l，并开始21轮真实昼夜环境，当前状态见下条与round-20-worklog.md。**

**当前最新候选20l，岛礁仍未生产集成。** 20i/j实拍及独立量测打回陡峭路基；20k缩小塔平台保护范围，新增经实际SeaCollision中心核实的D中景岛（C资产旋转复用），调整近景机位。20l真实连续路基混合修复A汇合口同一三角61.86°→6.01°；独立实际GLB和21a昼景支持有限保留。B坡道仍有较大陡坡比例，台阶/步行未验收。C/D高灰墙、沿岸规则叠层、大片草盖与右岸聚落仍待返工。详见 `reviews/round-20-worklog.md`。

**最新环境候选21c已经完成两个受影响GPU夜视角。** 21a过黑/密星/方格月盘/条纹水光打回；21b用Blender保存4套实体月球/三类云体，实际重开源验证和三GPU图完成，星域/月体有限保留，整体仍打回。21c经本机Godot运行时核实，把夜间环境光来源从SKY明确改为COLOR，真实图恢复原生塔/屋/岩体层次；保存来源/颜色、四灯世界位置及已遍历未映射材质列表。两夜图根已直接看完，独立范围以 `reviews/round-21c-environment-independent-review.md` 为准。全部21a/b/c引擎会话已结束，不重复旧运行。1342候选机位登记 `reviews/reference-view-1342-progress-21c.json`，状态明确未接受。生产仍17e/18c/19h，所有岛礁/天空/环境为临时候选。流式环境、其他天气、暖束光、完整岸村与自然岩岸/水光尚待制作，详见 `reviews/round-21-worklog.md`。

**最新22g港岸：22b木构修复、22f四套Blender石阶3516部件/28平台已完成22g七GPU图与独立审查。** 23屋/4码头/4船/54灯位于同一临时世界；每图4路1758组实际上下碰撞和原地形检查passed，船外移后低位顶点不再穿入浅滩。保留真实接口/厚基础/灯链与泊位修复；长阶梯孤立同型屋、空坡及缺失的近右岩岸聚落使整岸继续打回，不能直接安装生产。下一步优先按固定1342机位测量并建立Blender局部岬角/岩湾与房屋组团。独立 `round-22g-harbor-independent-review.md` 和 `round-22f-path-independent-geometry-review.md` 均完成；失败生成/音频失败前驱保留，所有本轮引擎句柄已结束。详细状态见 `round-22-worklog.md`，当前机位登记 `reference-view-1342-progress-22g.json`，全20参考Goal继续active。

历史单图目标：真正可自由飞行的 Godot 3D 游戏，在参考截图视角达到同样的场景、色彩与 UI 表现。最新范围以GOAL.md为准，不新增UI。不能以能运行或功能测试通过替代画面验收。

流程：固定机位和动画时间 → Blender 实体建模 → Godot 实际渲染 → 全分辨率比较 → 独立审查 agent → 未通过则继续返工。

| 轮次 | 实际渲染 | 独立审查 | 结果与下一步 |
|---|---|---|---|
| 01 | `captures/packaged-game.png` | `reviews/round-01.md` | 打回。RGB MAE 21.85/255，SSIM 0.7441。海陆轮廓、山体、云群、色彩与额外 UI 均明显偏离。 |
| 02 | `captures/round-02-opening.png` | `reviews/round-02.md` | 打回。RGB MAE 15.5127/255，SSIM 0.7637。天空、云群位置、默认 UI 改善；河湾拓扑、无关雪山、岩壁、城堡高架底座和飞艇细节仍不合格。 |
| 03 | `captures/round-03-opening.png` | `reviews/round-03.md` | 打回。MAE15.1215、SSIM0.7591；修复沙锯齿和水道连续性，岸线本身仍错、山体仍简单。 |
| 04 | `captures/round-04-opening.png` | `reviews/round-04.md` | 画面打回，MAE16.0740、SSIM0.75135。原生 Godot 预制体与场景实例改造通过核心审查；GPU持久化14项、实际编辑器工作流13项、游戏32项均通过。不能以工程通过抵扣画面回退。 |
| 05 | `captures/round-05-opening.png` 与侧后图 | `reviews/round-05.md` | 打回。MAE16.9089、SSIM0.77474；完整六块岩体和18项飞艇碰撞成立，岩崖形态、水系、尺度与颜色未通过。 |
| 06 | `captures/round-06-opening.png` 与侧后图 | `reviews/round-06.md` | 打回。MAE16.2138、SSIM0.76804。湖湾、小聚落和海色改善；最终草地明暗处理比06b中间稿15.2587/0.78290回退。35项游戏检查、18项碰撞及1139.86米安全绕行通过，不能抵扣造型失败。 |
| 07 | `captures/round-07-opening.png` 与侧后图 | `reviews/round-07.md` | 打回。MAE13.3952、SSIM0.78349。连续山脚、11个独立山体、船板与色彩改善；17模块几何检查、35游戏项、18+33碰撞项通过。峰谷、柱列、岸线与道路断带仍需修正。 |
| 08 | `captures/round-08-opening.png` 与侧后图 | `reviews/round-08.md` | 打回。MAE13.3776、SSIM0.78521。道路40,642三角内部采样通过；海岸远峰回退、小岛尖锥、山体和UI未过。该轮HUD仍为UI图集；两次Windows打包均有实际脚本错误。 |
| 09 | 09n 冻结版五视图，源工程/运行包开场一致 | `reviews/round-09.md` | 打回。MAE14.3837、SSIM0.76036。原生UI、完整岩体、新城堡和树组改善；前景碎三角山坡、雪峰/台地大形、水陆尺度仍不匹配。原先包测试误读工程目录失败；修复显式PCK与工作目录后，新完整同版本运行通过，源游戏36项、包37项及几何/物理导览通过。 |
| 10 | 10l 冻结源工程四视图，唯一运行 `10l-cliff-terrain-edit-20260905T222858Z-e09be6fff0384003802bf7994a07d749` | `reviews/round-10.md` | 视觉继续打回。MAE14.07868、SSIM0.761939。六块独立岩体、四块局部地形与两条道路已整合；11个限定源检查阶段通过，包括4,472脚线与40,642路面采样。首次道路失败因西侧邻块未同步，补齐后另建运行通过。前景柱壁、雪峰、岸线、飞艇、云和UI仍有差距。Windows包保持09n。 |
| 11 | 制作中：11g显式肩谷网格、11h前伸支脊与雪沟、11i中性雪面三视图 | `reviews/round-11-wip-notes.md`，后续候选待复核 | 11g独立几何检查通过，显式肩谷方向可继续，但连续白坡和基座仍被打回。11h/i保留完整独立模型并继续细修；均未集成或完成。 |
| 12 | 12b/12c真实地理分区材质两视图 | 待独立视觉复核 | 12a被运行时材质覆盖，实际未生效。修复原生材质所有权后，12c整图MAE13.18821、SSIM0.762477；配色仍为临时研究。独立的材质流程源修复已在唯一限定运行中通过4项保存/重开/启动检查、默认截图与10l逐像素相同及36游戏项。 |
| 13 | 制作中：原生矢量UI线条、圆形状态徽章与面板透明度 | 待实际图审查 | 保持真实状态和点击逻辑，先以临时HUD脚本检查外观，不使用截图图集。 |

当前总体验收：**未通过，目标仍在进行中**。

新增硬约束：Blender只供独立资产；地形、地貌、建筑、植被、飞艇等在Godot中以可持久编辑的场景/实例拼装。不得重新退回整包世界模型入口。

参照 `round-01.md` 中的地标、区域、色彩及真实三维要求复审。`tools/compare_reference.py` 只记录未修改的原始渲染数据，不作完成判定。每轮也需检查反向等实际三维视角。

## 2026-09-08：在 E:\FeiTing 恢复并继续

迁移校验全部 220,703 原文件通过；原始快照与迁移补录完整保留。新机器源运行 `restore-20260908-20260908T014334Z-65c6290b091c4a99806b7cf3b9c2db9b` 完成导入、四个 GPU 视角及 36/36 源游戏检查。没有更新 09n Windows 包。生产几何继续保持 10l 与原生材质修复。恢复细节见根目录 `WORKSPACE_RESUME.md`。

新独立审查已经实际复核 10l 和 11i/12c/13b/14c 原图，均不作为完成稿接收。见 `restore-20260908-candidate-review.md`。

| 轮次 | 同版本实图目录 | 独立审查 | 结论 |
|---|---|---|---|
| 16a | `captures/validation_runs/foreground-16a-20260908T014632Z-2519ed7bd0c948c5845bc7e6fa0664a2` | `reviews/round-16a-independent-visual-review.md`、`round-16a-independent-geometry-review.md` | 打回。三件原生 Blender 候选的 30 个上部控制真实移动，完整接地边界保持；但峰体出现陡绿墙，中央暗壁仍为尖片。模型与失败证据保留。 |
| 16b | `captures/validation_runs/foreground-16b-20260908T015118Z-c8ff6b7fed9d4c7dad11c4ffb2dac90d` | `reviews/round-16b-independent-review.md`、`round-16b-independent-geometry-audit.json` | 新增 8 个真实台肩点和 16 个三角，恢复上部裸岩；可保留为下一稿，视觉仍未通过。草肩窄折带、横向陡面与尖长暗壁需继续返工，未集成生产。 |
| 16c | `captures/validation_runs/foreground-16c-20260908T044445Z-c8470ae2ac4c4908bb4ed853001e78e1` | `round-16c-independent-review.md`、`round-16c-independent-geometry-audit.json` | 横向陡面修缓成立，视觉仍打回；诊断出crown前缘12–20m悬挑与横向错位。 |
| 16d | `captures/validation_runs/foreground-16d-20260908T044954Z-1577d1ffdda64be881de773769a52a8c` | `round-16d-independent-review.md`、`round-16d-independent-geometry-audit.json` | 前悬收回、真实峰体后退及中央壁解除遮挡成立；保留为制作底稿，视觉未过。 |
| 16e | `captures/validation_runs/foreground-16e-20260908T045337Z-fb6e18a6381f4ff3a999a777ef89b566` | `round-16e-independent-review.md`、`round-16e-independent-geometry-audit.json` | 中央新增双排实体岩台产生连续灰色台阶带，上段局部悬挑；打回并保留失败证据。16f改为单排坡折和较低上帽。 |
| 16f | `captures/validation_runs/foreground-16f-20260908T045736Z-e74eb3b4aef7419f99ddd9ad5405864d` | `round-16f-independent-review.md`、`round-16f-downward-localization.json` | 单排坡折与低上帽有局部视觉改善；3件GLB不满足既有表面门禁，8处候选折返已精确定位，不能原样集成。 |
| 16g | `captures/validation_runs/foreground-16g-20260908T050716Z-0831944f67c2433c95b8fdc2f0721364` | `round-16g-independent-review.md`、`round-16g-independent-repair-checks.json` | 8处折返真实修好，五件表面门禁全过；局部实图改善保持，独立接受为下一阶段前景底稿，完整视觉仍未过。 |
| 16g原生集成 | `captures/validation_runs/16g-native-integration-20260908T051154Z-276e28776e864ea7bdffae2d9da929d5` | `round-16g-native-integration-independent-review.md`及audit JSON | 12阶段全passed：36游戏/6岩区巡游/21接触/4472接地/40642道路/18地貌等；14项源文件变化，World/地形/道路/scatter源未变。独立核验66项绑定产物后接受当前阶段底稿。开场和侧图与候选完全相同，背图远景有1549像素差异，原因未确认。完整视觉未过，源已更新，09n包保持。 |

下一步承接当前已集成16g原生底稿，优先western左草肩和宽暖壁，再整理中央碎三角/沟壁/双绿带，不重复16b已修问题。之后仍需完成雪山、岸线、多尺度地表、飞艇、云体与UI的完整审查循环。16g阶段接受和技术集成通过均不等于完整视觉验收。禁止以迁移恢复、几何拓扑或三视图生成成功替代原目标。

## 17系列与18系列：左肩实体和多尺度平原材质

以下记录17/18系列从16g开始的研究历史；当前生产已是17e两件岩体与18c原生地形材质，完整运行目录见 `WORKSPACE_RESUME.md`。

| 轮次 | 实际内容与证据 | 当前结论 |
|---|---|---|
| 17a | 两件独立Blender资产，左草肩峰脊后移；同版三图与独立审查完成 | 前肩拓宽，后肩形成69–83°亮绿陡屋面，返工。 |
| 17b | 中部后肩协调、按坡向收回亮度、暖壁新增2点/4三角凸脊 | 中部与色彩改善，右端77–78°及盾状暖壁未过，返工。 |
| 17c | 右端ridge14/shoulder19联动，同版三图及独立报告完成 | 前两面约44°，但接地face30/31仍75.72/75.30°；face31不含19，定位到18与原rear24/rim，返工。 |
| 17d | 收回端肩XY并让暖壁凸脊不对称；native/GLB保留 | 实际triangle41（14/29/19）翻折，投影重叠0.79279m²，表面门禁失败，未渲染三视图。 |
| 17e | 保持17c安全XZ、降低后肩17/18，暖壁不对称凸脊；五件表面门禁和三视图通过 | 独立接受局部阶段并已原生集成：12阶段passed、64绑定产物、11项实际变更；完整视觉仍未过。 |
| 18a | 208原生地块临时应用世界坐标生境色域；opening/side/reverse三图 | 独立确认宏观绿黄分区改善，但云斑过软、分面被压弱，材质不集成。 |
| 18b | 生境128/45m、保留原facet亮度0.70、草色替换0.72；完整三图 | 独立确认分面恢复但软云斑仍需改，未集成。 |
| 18c | 在18b基础上以flat varying保持实际三角内生境一致；完整三图及后续原生四图 | 已原生集成并独立复核，reverse偏碎仍需收敛；原收集失败和恢复通过分别保留，见下。 |

18系列研究只改变临时材质，后续18c原生安装也未改地形顶点、地貌模型、海岸轮廓、道路或碰撞。18c取实际三角的provoking vertex样本，不能写成面中心烘焙。所有研究均保存失败/通过门禁和冻结输入，不能将局部技术通过写成参考整体完成。

17e集成完整run为 `captures/validation_runs/17e-native-integration-20260908T060301Z-07dc7a9c264c45aab408ab67177a7dfd`。独立报告与audit为 `round-17e-native-integration-independent-*`。本次2模型/2实例刷新，terrain0，实际散布岩石1块重贴地（不是植被树木）；`round-17e-rock-refresh-verification.json`证实30实例仅index2改Y，62.27490234375→54.01611328125，XZ/basis保持，当前碰撞面误差0。原生截图与候选有岩石范围差异及背图未解释的远景差异，详情见 `round-17e-native-image-comparison.json`，不宣称全部逐像素相同。

## 18c原生地形材质与新增20参考场景

18c原生运行 `18c-native-material-20260908T062423Z-e13cc07350264b9d800603025868e010` 保持failed，原因是收集器最后读取了错误stream报告文件名；8个底层引擎进程都exit0。另建 `18c-material-evidence-recovery-20260908T063226Z-ce87559c6bcd43c188f89f7c2d233c20`，核对原run身份、SHA、时间和原产物后恢复正确报告绑定，passed，重执行引擎阶段0。原失败manifest和错误制作器保留。

`round-18c-native-material-final-review.md`及final-audit独立复核251个恢复绑定文件、213项准确安装差异，并确认底层7材质/36游戏/4方向飞行结果。208个地块仅材质路径改变，新增terrain.tres/shader与运行接入；几何、碰撞、17e岩体和岩石保持。当前支持保留局部生产底稿，反向材质偏碎及部分候选/原生像素差原因仍未解决。

新增任务以根目录 `GOAL.md` 为准：全部20参考属于一个世界，覆盖场景实体、天气时段、内景与云海，人物角色跳过，不新增UI任务。逐图清单 `REFERENCE_SCENES.md`，真实世界锚点与拟议区域设计 `WORLD_SCENE_PLAN.md`。原始单图目标不再限制任务范围。

19系列共享灯塔已迭代至19d，详细制作/失败/返工日志见 `round-19-worklog.md`。19a黄板/偏白打回；19b真实玻璃/灯芯/透镜改善成立；19c按审查缩短拓宽并加厚承托，但一根固定杆变换错误，候选保留为有问题；19d修复后四图完成，独立核对43个绑定文件和218节点，接受为后续建筑底稿。当前仍需细化石材横带、玻璃/灯芯和门口。候选不覆盖生产，不把建筑研究写成海雾或月夜场景已完成。
