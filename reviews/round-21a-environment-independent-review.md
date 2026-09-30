# 21a 海岸环境独立审查

**夜景视觉打回；可以保留真实环境/材质改造作为试验基底。** 20l汇合修正的昼景可保留为道路局部进展。整体海岸及20参考场景均未完成。审查者直接查看四张原始GPU图，仅读文件，不启动引擎/Blender、不改生产。

- [day-paths](E:/FeiTing/captures/validation_runs/coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0/images/day-paths.png)：相对20k，修好的道路汇合处没有新增明显断口或大范围异常，房屋和塔仍清楚；已独立测得的同一三角61.86°→6.01°可作为有限道路修复保留。此机位较远，不能替代踏面高度/实走。塔前密集灰色路基切面、大片绿坡和背景D台地问题仍在。
- [day-reference](E:/FeiTing/captures/validation_runs/coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0/images/day-reference.png)：近景A塔、D中景和远岛链保持。昼景未因夜景试验被整体压暗；岸线构图、绿盖和层带不足继续保留。
- [night-reference](E:/FeiTing/captures/validation_runs/coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0/images/night-reference.png)：下半幅大面积近黑，前景树和远岛形体失去区分；前景塔仅一面蓝光条，整体体量难读。星点过密且接近均匀铺满，月面内部为清楚的方格噪块，与参考1342的宽低多边形面不符。月光反射从远处到近处组成很多近似等距平行亮条，呈梳状/条纹带；未形成参考中宽窄错落、破碎变化的水面光斑。暖窗/灯芯真实可见，但房屋周围和灯塔方向性光束尚未形成完整照明关系。
- [night-back](E:/FeiTing/captures/validation_runs/coast-environment-21a-20260908T100942Z-e446ce77bb9c4a19b675264956c26ce0/images/night-back.png)：反方向也明显过黑，说明问题不只是第一镜头背光。塔和裸岩上有少量蓝面、窗有暖点，但近岸/水面/远地形普遍难分；云成为深色剪影，缺少参考可读的月照分面。不能用夜色隐藏旧几何不足作为接受理由。

实现核查：冻结 coast_environment_21a.gd 实际复制 Environment，夜间改方向光方向/颜色/能量0.5、环境光能量0.28、雾密度0.00038；不是全屏滤色。当前运行侧车记录7个材质绑定，覆盖 terrain_native/world_surface/cloud_surface/open_water/cliff_surface/ship_surface 六个shader基名（ship与flag两材质），另行替换sky。世界/地形/悬崖等原固定EMISSION改为受study_fill调节；天空是方向采样shader，水面使用实际world_point、波面法线、观察方向与moon_direction计算反射。真实PBR窗玻璃与灯芯启用emission。可保留这条实际场景改造路径，不能把代码存在等同画面合格。

月面方格和条纹可由冻结源定位：天空使用 floor(sphere*vec2(2200,1100)) 的哈希调制月盘，产生方形噪块；星点使用650×325方向网格及seed阈值，当前密度过高。水面几个固定正弦频率与单条broken_wave组合形成规则重复波纹；目前仍是程序材质反射近似，不能称物理海浪/月光反射完成。优先提高夜间可读的环境/方向明暗层次、分开天空与地面亮度关系，再重做更稀疏有疏密的星域、宽分面的月体/云体与不等距破碎水光。不是简单把全图一起提亮即可。

灯位核查：实际原生 lighthouse.glb 的Lamp core顶点包围框Y=[18.9100,20.2900]m，中心Y=19.6000004m；源中为临时region每个Lighthouse_*新增子OmniLight3D，局部位置(0,19.6,0)、energy2、range13，父级旋转/平移后仍在灯芯位置。没有发现这里把压缩前23.2m误作灯位的问题。sidecar未记录每盏Omni的全局变换，本结论是实际GLB与冻结源的独立核对，没有假称新运行灯位探针。Omni是局部球形光，并不等价灯塔投射光束，当前未实现束光不能忽略。

覆盖边界：emissive_material_variants=6是缓存后改造材质变体数，不等于6窗或6灯。wood_surface候选存在但本帧binding列表无它；这不能单独证明漏了可见材质。记录没有列出所有未映射ShaderMaterial，因此只能确认所列类别成功绑定，不能确认全世界全材质无遗漏。配置是一次性遍历，后续流入节点未见自动重适配机制，流式夜景/其他天气尚未实现。侧车顶层scope还保留“daytime”文字，night标志和实际图明确是夜间，报告模板应修正该文字，不能据旧文字否认实拍状态。

身份：53个manifest产物SHA全部核对，零不一致；四阶段passed/exit0并绑定相同inputs。七对资产blend/GLB全部等于20l，原shader来源SHA与当前生产文件相符。日志ERROR/WARNING/Invalid/not found检索无匹配。日图与20k机位相同，但不是逐像素相同：day-paths3635像素变化、最大通道差51，day-reference7398像素、最大57。变化不能全部归于道路，因为环境材质/动态场景也参与；此处只作受控机位下有限视觉比较，不作全部像素因果断言。

后续应保留20l路径几何和真实环境系统方向，返工21a夜景画面；旧崖壁、草台、岛链与聚落差距仍在。未批准生产安装。审计数据及SHA见[独立audit](E:/FeiTing/reviews/round-21a-environment-independent-audit.json)。
