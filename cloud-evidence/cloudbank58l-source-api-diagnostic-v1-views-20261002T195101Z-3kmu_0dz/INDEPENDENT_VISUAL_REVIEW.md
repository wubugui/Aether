# L 隔离源四视图：独立视觉与真实性窄审

2026-10-02 UTC。结论：**四张真实源诊断图及其完成链可信；造型视觉不通过，打回。** 不是世界试验，不能因此准入世界或宣布完整原生验收。

## 亲看范围与判断基准

已实际逐张打开本 run 的 `outputs/01-original61-front.png`、`02-k-trial-front.png`、`03-k-fixed-side-back.png`、`04-k-fixed-near.png`；另亲看 `ref/1216.png` 及既存 K world run `cloudbank58k-world-trial-v2-renderer-20261002T121854Z-931jfijg/images/` 的03侧背、04近角。

先读 GOAL、CLOUD_RESUME 当前区、revision-l/design-v3/CONTRACT.md 及 source-v1/README.md。按连续厚云岸、错位冠肩、宽底谷、冠—肩—腹的有层级克制分面评估。参考本来就有明显棱面和暗腹，不能把三角、深色或非照片棉花感本身当错误。

这是固定材料、固定源检查光照下的孤立作者源。K world 图只作既存缺陷背景，并非同渲染条件的前后 A/B；不作颜色、像素相似度或世界遮挡改善的定量结论。

## 可见成果与真实造型缺口

- **01/02 front：** 可见高冠、左右肩和冠间下凹面在同一片有厚度主体上延续；近侧凸出部分下面有实际回收腹面，不是只有一张屋顶轮廓。宽谷已能读出底面，而非仅尖锐 V 缝。这是可观察的整岸/厚度进展，但中央高冠仍更像窄顶山峰接陡坡，肩部出现长斜折带，右侧连片形体又被画面边界截断。不能据此认定全岸的层级已好。
- **03 side/back：** 从另一方向确能看到两个前后错位的大冠、其间连续低部及较厚的下部体积，排除只凭正面轮廓冒充立体的判断。可是两冠的截顶、长直下降侧面与近侧大段陡壁一起，形成明显山体/崖台观感；数个大面从肩连续拉到腹部，局部小三角转折夹在大片面之间，主次尺度不协调。问题是面片走向与体块转折组织，不是“三角形存在”。左、下边仍裁切，完整腹面没有全部展示。
- **04 near：** 近距离可见真实肩面宽度和顶部体积，不是 K 已存近角中那种薄屋顶式正面轮廓。然而主冠上部呈大截顶，长坡面跨越很大一段肩部，前肩巨大近乎平整的面与横斜折带占主导；冠、肩、腹仍不像参考里由大小不同的鼓起块面连续接成的厚云岸。底部出画，不能宣称下腹全角合格。

综合：连续主体、冠间宽谷和可从不同方向看见的厚度值得保留为本次真实成果；**决定性失败是山峰—长坡—陡壁的组织仍压过云冠—肩—腹的块面节奏，侧背和近角尤其明显。** 相比旧 K 截面/薄屋顶式可见缺陷，本源展示了真实更厚的作者体块；由于这里没有世界邻云，不能顺带宣称 K 的世界黑洞、接缝或遮挡已被修复。达到若干高度/厚度数值门，不等于美术已达到参考。

画面细颗粒来自本次 Cycles CPU 8 samples 且未降噪的检查条件，不以采样噪声否决几何；也不因缺森林、天空天气、邻云或完整世界背景打回。没有给无依据像素分数，没有要求照片写实棉花。

## 只读真实性核对

使用现有 helper 的 PNG CRC/scanline 检查、`validate_capture` 与 normal oracle，只读重算四份 pre-render、四份 restored raw，并核 rendered raw 的实际 active_camera、全部几何/材料/机位/lighting 身份及 SHA；未启动 Blender/Godot、未保存/重建源、未修改图像或新增证明框架。

- 外部实际观察：launcher PID5 exit0，44.497547680秒；worker PID6 exit0，四 native PID7/26/45/64 均真实观察 exit0，分别5.169122121/5.049636506/5.368207437/6.442035989秒。外部结果、准入、supervisor、terminal/wrapper 的原字节 SHA 链相符，`views_chain_verified=true`，所有自有后代已回收，残留为空
- wrapper 的 `passed=false / awaiting_external_process_terminal` 是保存于外部 wait 前的阶段记录；最终成功依据是随后真实外部观察及 supervisor/validation，不是把旧 prepared 状态冒充完成。`views-launch-observation.json` 的原始未验证值也未被事后改写，另份 validation 绑定最终 external result
- 唯一 .blend 当前319519字节，SHA256 `7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7`，与保存源及四子进程记录一致；四次 `source_saved=false`，pre/restored身份一致。14265文件的运行前后保护记录完全相等；另实际重新读取295冻结输入，全部SHA相同。此处不将保护记录比对称为再读全仓每一文件
- 四机位原 transform/projection 字节仍与冻结 binding 一致；实际RNA最大姿态误差2.235174179e-7，最大投影误差1.192092896e-7，在原门内。固定K线性材料、源lighting、采样与完整非自动运行Text均复核通过，无为居中/好看而重构机位
- 第1/2原机位本来相同，实际解码RGBA也逐字节相同；PNG文件SHA不同不能冒称造型A/B。因此是四份规定输出、三个不同观察方向，不是四个独立角度
- 四图原始1179×664 RGBA8，CRC与全scanline解码通过：

| PNG | 字节 | SHA256 |
|---|---:|---|
| 01-original61-front | 764893 | 3adacdda4c26e5612190742a403c86b0872d0c12b0ad39acd98bfad3d00100fa |
| 02-k-trial-front | 764890 | 24ee8921db730e3fd8877fa1874a4d0bc0f72d882efba5d186f6bf43d0f54687 |
| 03-k-fixed-side-back | 856438 | f1315d93a54a6ccb37c61b7180dbbc44822c0fd284b13200a7a44382ad771891 |
| 04-k-fixed-near | 837671 | 3316d83b822930067b16437f184aee1390e0215e672df7c782a7d19e1b799092 |

## 必须保留的未通过范围

新API一致性复核最大差5.960464478e-8通过；原corner→数学几何3e-5门仍失败22面，最大分量差0.0001594134493、最大角差0.009158468662°。**不能把API通过换名为旧门或full_native通过。** 此小数值问题也不作为上述岩山感的因果解释。

本次与本审查均 **0世界试验**。四邻全J_i接触、并集连通/缝隙、世界遮挡、天气光照、飞行和硬件GPU未由这四张隔离源图验证；保留 `full_native_acceptance=false`、`visual_acceptance=false`、`contact_acceptance=false`、`world_acceptance=false`、`global_GOAL=false`。只接收真实隔离图组的证据资格，**造型明确打回，不先设计下一模型**。本报告未声称本图组已远端发布，发布核回仍由父任务另行完成。
