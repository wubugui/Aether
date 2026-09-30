# 20i 海岸独立实图复审

**结论：继续返工，整岛海岸不接受集成。** 可以保留真实斜向崖面、裸岩进入草坡的方向，以及已接受的 20h 守塔屋和三礁。小路贴合正确，但当前陡坡与入口连接不足；分件门禁通过不构成美术或步行验收。

本次直接查看 7 张原始 GPU 图，重新查看 ref/1218.png 与 ref/1342.png，并沿用此前直接看过的 1126 对照。未启动 Blender/Godot，未更改生产或候选。运行目录 `E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19`。

- [archipelago](E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19/images/archipelago.png) / [island-front](E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19/images/island-front.png)：岩壁增加真实斜向明暗面，比单整面有结构；裸岩肩开始进入草面，打断了完整绿盖，这是可保留的局部方向。但正面中央和两翼仍是很长的直边、齐整墙面，凹湾上缘仍像整齐切槽。灰石面积变化尚未变成参考那种由高崖、斜肩、低岸交错组成的轮廓。远近岛群仍偏“几个孤立物件排列”，环境构图未过。
- [island-back](E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19/images/island-back.png)：前方低岸形成几道几乎连续的窄岩带，沿岸线包围大绿盖。它们有真实偏移，不能说只是画出的色条，但连续性仍太强；需要在局部将岩带终止、换向、并入宽斜岩台，另处让草坡下探，而不是继续全周加层数。裸岩块在草坪中仍有独立规则补片感。
- [shoreline](E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19/images/shoreline.png)：最明确的拒绝视角。中央 x≈450–1210/y≈330–640 是宽直崖面；新增三角分面改变了明暗，未充分改变大尺度墙体轮廓。塔前 x≈630–865/y≈228–315 的裸岩肩像单个三角尖丘，与后方塔和边缘尖岩一起增强了锥体重复感。应降低或错开部分峰点，拉成长短不一的倾斜脊，增加宽的不对称肩面；不要单纯把更多小山头涂灰。
- [paths](E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19/images/paths.png)：两屋与塔之间路线清楚，但颜色、等宽边界和尖折转角组成偏干净的浅色带；细节并未沿地形演变成自然步道。路的存在补足场地关系，值得继续，但门口收头和坡折仍需真实处理。保留屋顶本轮并未重建，不能将它再次计为新增建筑进展。
- [b-site](E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19/images/b-site.png)：左侧降向低岸的小路穿过明显横坡/裸岩折面，塔旁折返段仍贴着较陡地表。草肩体量有变化，但步道缺少稳定路基。先修纵横坡，再看是否需要台阶与边坡，不只降低路径材质亮度。
- [c-site](E:/FeiTing/captures/validation_runs/lantern-islands-20i-20260908T094048Z-9edbdd72d73d466b91c08395dfb8ba19/images/c-site.png)：屋前 x≈870–1040/y≈610–755 的路段跨过尖折岩草面，右侧往塔的长带贴在陡肩上；形状足以直接否定“已完成可步行连接”。屋周裸岩大多是几个相接三角块，过渡仍急。C 屋本体保持可用，但路基需独立剖面与连续落脚面。

参考 1218 中的岩草关系不要求所有地形都碎：宽岩面、宽草肩同样存在，但它们通过不同岸高、宽窄不一的斜面与低岸相连。1342 的岛群也不是全周等宽横带。白日背景与月夜本身不作为本轮建筑/几何打回原因；本轮不足在实际形体与组合，天气、灯束、水面和聚落仍属于后续任务。

已绑定之前的 [独立路径几何审计](E:/FeiTing/reviews/round-20i-path-independent-audit.json)：三岛源与 GLB SHA 均与新 run 冻结输入相同。A/B/C 顶面分别 614/400/288 个顶点、重心和边中点样本全部找到实际底层 terrain，间距约 +0.045 m，偏差小于 4e-6 m。这意味着“固定抬高的贴坡实体”，不是零高差。实际路面最大三角坡 A 36.32°、B 42.58°、C 57.36°；B 超过 30° 的面积 43.30%，C 超过 45° 的面积 26.56%。端点平均纵坡会遗漏真实横坡和局部尖折。C 最陡位置为 Blender XY≈(-9.6,-19.9)，正是近屋第一段。A 西屋路径端帽与最低阶外边还有约 0.3312 m 水平间隙；其余门口平面接近不证明垂直连接。

58 个 manifest 产物重新计算 SHA 全匹配；7 捕获阶段 passed、exit 0 且绑定同一 inputs。父代理保存源 gate 记录 374 分件通过，全部 7 源 SHA 已独立核对；未重复执行该 gate。屋和三礁 blend/GLB 与 20h 字节不变。各视图中的 7 栋×9 基础样本相同，共 63 个独立点，均为负间隙；C 屋范围变为 [-0.463270,-0.231184] m，不能套用旧稿数值。它们只证明外包底部采样，不能覆盖台阶和步道。非 .godot 缓存生产输入与 20h 冻结快照无变化。

下一稿最优先处理：① C/B 的真实路基纵横剖面和入口落脚面；② 水线大墙的轮廓断开与宽斜肩，不以更多三角材质代替；③ 低岸连续岩带局部终止、换向、与草坡衔接；④ 把尖丘式裸岩改成有主脊、偏心低肩和不等边界的真实隆起。道路修正可以作为下一轮独立增量审查，不能自动使旧崖壁问题通过。20 张参考的完整目标仍未完成。

绑定信息见 [20i 独立 audit](E:/FeiTing/reviews/round-20i-coast-independent-audit.json)。
