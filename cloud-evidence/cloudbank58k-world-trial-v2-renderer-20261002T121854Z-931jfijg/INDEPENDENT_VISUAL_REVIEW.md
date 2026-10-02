# K 首次真实世界四图独立审查

审查时间：2026-10-02 12:25 UTC。审查对象：本目录原始四张 PNG、原生 `images/report.json`、renderer 进程/日志与 wrapper 报告；对照 `ref/1216.png`。先读当前 `GOAL.md`、`CLOUD_RESUME.md` 与 world-trial-v1/v2 说明及原 capture/trial/validator 源码。四张原图和参考均由本审查者直接逐张打开检查，未以父审意见代替图像检查。

## 结论

**拒绝此固定单单元 K 世界替换方案的视觉验收。** 四张原始图确实完成，且能提供有效的失败画面和局部原生证据；原 renderer / wrapper 仍为失败，不能将四图存在、离线部分门通过或源资产通过改写成整体通过。

- 首个成对正面视角直接暴露布局不成立：移除原 CloudSea_1_1 后，右下云体位置出现大块近黑空区；K 是其中较小、与周边比例不协调的三冠物体，不能接替原大云体的覆盖和连接
- 正面及近景的 K 大面积暗面过于单一，冠顶窄亮边、近直线坡段和硬折角形成厚纸片/折板式读形，未达到参考有厚度层级的团簇、宽肩、体块明暗和连续深谷
- 侧背确实显出不同的亮面与分面，但主体下半部被前方邻云遮住；不能从这一角度宣布完整底腹、邻接和任意角度可观察性通过
- 本轮无新的源资产或世界保存。本报告仅评审现有结果，不修改原冻结输入、源资产、原生报告和失败记录；没有启动 engine、重跑四图、运行 Git 或发送 Slack

## 图像身份与尺寸

PNG 字节 SHA256、长度、IHDR 宽高均独立读取；Pillow 完整解码尺寸一致。四图均为 RGBA，参考为 RGB。

| 文件 | 字节 | 实际尺寸 | SHA256 |
|---|---:|---|---|
| `1216.png` | 1721327 | 1672×941 | `f705cb5de0664e9189bdc66b8ed116fc6db5f6ec1f541606df2b399dbde3aa4f` |
| `01-original61-front.png` | 420967 | 1179×664 | `c96edfa27bad139649d7184785ce0e7ede7d4a7a25540e1e246c308b85ee9c95` |
| `02-k-trial-front.png` | 414964 | 1179×664 | `e1537b4ed21d62defdc67c7896f7e84704ecc168a8277beb579d09f89527a0db` |
| `03-k-fixed-side-back.png` | 267170 | 1179×664 | `8f8779678765a52e373efec6b8e874e34dd13d29488a696c40fcb75005013018` |
| `04-k-fixed-near.png` | 299361 | 1179×664 | `2ec646e4c111fae2668805372912ef2225c10c8b5d359695ef16c44815c4af1a` |

四图长度与 SHA 均与同一 native 报告的 capture 行一致。`images/report.json` SHA256 为 `5d410f92fb116a027257e679b75d45463d8e7080423a69b9359d0291c059934d`；`wrapper-report.json` SHA256 为 `e287913fb32af8cbf025d2ceccc9e49ce19601609aac1d2c87742628b5d80e44`。

native 的实际 Image 与 PNG 是 **1179×664**。各图还记录：请求/实际窗口 1180×664、visible rect 和 content scale 1672×941、texture metadata 831×468。后三者不是 PNG 尺寸，不能混用。native 投影点记录明确为 viewport 坐标，不把其数值直接标为 PNG 像素位置。

## 逐图视觉观察

### 参考 `1216.png`

参考是纵深很强的连续云海：前中后不同大小的厚团簇相互覆盖，云冠亮面由不规则宽分面组成，深槽与下腹承接暗部和紫色局部闪电，远处层层收敛至亮地平线。低多边形边缘仍保持膨起的体积，既不是整齐重复的球串，也不是孤立的单色折板。此描述只针对参考可见的美术目标，不给参考补造精确空间坐标。

### 01 原世界正面

船和近处大型亮云可辨，现有世界仍有明显的重复球团、浅色大坡与参考的深谷/层次差距。中央偏右原本已有一处近黑的圆形开口，天空也有独立球串；这些既存现象并非本次 K 新造成。原画面右下仍被原 CloudSea_1_1 的亮云体大面积占据。

### 02 同机位 K 正面

船、天空、上半部背景和前景左侧与 01 对齐。移除原大体后，右下出现宽阔近黑空区，从 K 右侧一直延至画幅右下。K 可见部分约在原图 x573–789、y381–482 附近，前缘一部分埋在近云后。其大暗面、三座带短亮顶的硬冠及有限覆盖，与周围巨大的亮团比例失配。仅就固定正面看已满足原计划“露洞或脱离的小物体则拒绝”的条件。

独立 RGB 逐像素比较有 129499 / 782856 像素不同（约 16.54%），不同像素的最小包围框为 `(573,294)`–`(1178,663)`，坐标端点均包含；这只是原始像素差，不是洞面积、K 可见面积或视觉合格分数。变化局限在右下区域支持成对比较的有效性，实际判定依据仍是直接看图及下面的相机/场景证据。

### 03 固定侧背诊断

中部可见较亮的分面 K 冠体，轮廓与正面不同、可见面亮度也不同，说明当前画面至少提供了非单正面读形。可见冠体下部受大块近邻云遮挡，左侧仍有大块近黑空区。此图不能证明完整下腹和邻云接合已经成立；局部厚度可辨也不足以弥补前视覆盖失败。未凭这一截图推断云壳真正开口、自交或几何为薄板。

### 04 固定近景诊断

K 三冠成为中央主体。大片几乎同色的灰蓝暗面与极窄、分段亮顶造成硬纸皇冠/折板观感，缺乏参考的冠肩膨起与暗部层次；近景放大了这个问题。底部仍被前景云遮挡，右侧大空区持续存在。它确实是实体渲染的视觉不足，“像纸板”是画面读形判断，不是将 3D 网格误认成图板的技术结论。

## 原生证据及成对条件

- native 报告 PID **227195** 与 renderer 进程记录相同，Godot **4.5.1-stable official**；实际图形设备为 **llvmpipe (LLVM 19.1.7, 256 bits)**。可称实际原生图形渲染，不能称硬件 GPU 验收
- child exit **1**，58.631302 秒；wrapper 71.492864 秒，`passed:false`。未触发 timeout、RSS limit 或 signal；aggregate RSS 1869596 KiB 低于原 3145728 KiB 限制
- native 四 capture 顺序正确，四个 PNG 保存门为 true。原生 checks 共 22 项，21 true、1 false，唯一 false 是末尾复合恢复门
- 01/02 `camera_transform` 和 `camera_projection` 序列化字节**完全相同**，原 front camera 标志 true，位置 `(3000,1150,4300)`、FOV62。四图 reference 都为 `1216`、实际 weather time 都为 `.35`，near 约 .35、far18000，分辨率相同
- 03 位置 `(4637.952,975.8685,3126.689)`、04 位置 `(3523.8,828.0205,4063.668)`，与预设中心/方向/900m、600m诊断流程相符。它们只是固定静态诊断，不是连续飞行或完整轨道
- 每 capture 的旧路径都是 `CloudSea_1_1/cloud_sea_46_0_continuous_crown`，world unit count1、trial failure空；01 old=true/K=false/enabled=false，02–04相反。四次 K world transform 字节完全相同，为 identity basis 加单一 `(3958,0,3667)` anchor；没有旧 root 旋转、缩放或附加平移证据
- 四次实际 stored surface 格式 **34359742471**，1152 render vertices / 1152 indices（384三角），vertex data SHA `6d3e3be9014ae790556976d1e40cf60ee460e9aa869efca6b9abce397f9b8262`、index data SHA `ea7db52bc6c7f11cafcbaeb3043feac4593f2eed131d0a0ce9fe11e59fd46a2d` 全同已接受 native 资产。该 native code 从实际 mesh surface storage 取 hash，不是由截图猜几何身份。它不能替代本轮不存在的完整连续碰撞/移动验收
- K 真实 material 是 opaque、two-sided 的 lit StandardMaterial：albedo约 `(0.7735731,0.7977378,0.8378605,1)`，roughness约.9，metallic0；diffuse_mode0，shading_mode1，无 vertex-color albedo、texture、emission、next pass，fog未禁用，四次与原 native 材质门一致
- 旧云 material 为 white、diffuse_mode2、roughness1、vertex-color albedo=true。因此作者材料忠实保存成立，但这并不说明当前世界光照下的外观协调。不能仅凭截图把暗面精确归因于单一材质参数、法线错误或某个灯光设置
- 四次同步 toggle witness 均 true，证明所实现的同步开关比较范围内，其余节点 transform / visibility / mesh 与 material resource binding 未变；没有将此窄观察夸大为每一帧/全部资源冻结

## 遮挡证据的边界

本轮原生 ray 是 **12 个固定 K 三角形心到相机的线段，测试四个相关旧云的真实 indexed triangles**，不是 AABB，也不是整个世界的可见像素率。

- 01：0_1命中4条、1_0命中1条、1_1命中4条；去重后7/12条有旧云命中（此时 K 隐藏）
- 02：0_1命中4条、1_0命中1条，后者与前者重叠；去重后4/12条有命中
- 03：1_0命中6条，6/12有命中
- 04：0_1命中3条、1_0命中1条，后者重叠；去重后3/12有命中

这些记录支持邻云确实阻挡若干 K 方向，与实图部分埋入相符；不能把“其余射线未命中”写成可见，因其不测 K 自遮挡、船、其他世界节点或整屏覆盖。所有1152个投影点在相机前也只表示投影方向成立，不能证明 K 露出面积。

已有 placement 几何设计记录中 K XZ AABB 面积仅旧单元 **7.486%**。图像现已实证这次固定替换的覆盖/衔接失败，不能反过来把 AABB 比例当作精确表面空缺比或遮挡面积。不能用移动 anchor、加高/放大 K、隐藏邻云或换验收相机来追认本轮通过。

## 离线原 validator 重放：只验证可独立成立的既有断言

本审查在 Python 内导入未改的 v2 `run_renderer58k.py`，调用原 `validate_images(run, row)`。仅在内存把 `b.require` 临时替换为记录器：保留并记录以下两项已知 false，允许继续检查后面的原谓词；其他任一 false 仍立即抛错。随后恢复原函数。没有修改 source、JSON、判据或 epsilon，没有运行 main/engine。

1. `Complete actual four-view result/PID` 为 false，因为 `native.passed` 是 false；独立拆读 PID 匹配及 capture=4 均成立
2. `Original camera and opt-out verified` 为 false，因为 `restored_to_original` 是 false；独立拆读 `front_camera_is_inherited_1216` 为 true

共执行 **30 个原谓词：28 true、上述2 false**。其余原门涵盖固定顺序、四图SHA/长度、每次实际 native geometry storage、原 material values 和属性、可见性切换、IHDR/Image尺寸、成对相机/投影字节和固定reference/time。

**这是独立离线诊断，不是原 wrapper 的通过结果。原 wrapper 在 `Actual native process failed` 就中止，未走到 `validate_images`，其 `images:0` 是该字段未更新的状态，不能解释为磁盘无图。** 原 wrapper、native与所有视觉/硬件/flight flags 保持 false。

## 末尾恢复失败：未分解，根因未证

原脚本的实际表达式为：

`not trial.enabled and trial.old_mesh.visible and not trial.unit.visible and game.camera.global_transform == front`

native 只存了这整个合取的 false，没有存四个子谓词、恢复后实际 camera matrix 或各 visibility 原始值。虽然前一个同步 toggle witness 为 true，也不能据此把未记录的全部恢复条件补成真。现有证据不够判明到底哪一项失败，更不能宣布是 float roundoff、transform setter、visibility 或恢复时序的确定根因。

不得改旧报告为 passed、减去恢复门、放宽原精确相等或擅定 epsilon。需要恢复诊断时，应另立独立且有限的诊断记录，首先分别采集这些实际值并保留原精确判据；本审查不重跑原四图，且恢复技术问题即使解决也不会消除已实证的视觉拒绝。

## 保护与后续使用范围

本审查逐项复核 v1 **47**、v2 **27** 冻结文件长度/SHA，零差异。freeze SHA 分别为 `4c99da76ec61bae16a3ec445f187286ef68471d1261bef989eb1c2bb352ae148` 与 `3287dd78bdd6cb4bde5e684d7e9cd3178ad0533a68c5ddd23fb8a8ddd178e3d3`。

run 记录的 before/after manifests 全相等：main4884成员、shared4889成员；wrapper 的 main/frozen保护均true。本审查核了已存 manifest 相等，未冒称又对当前全部4884主工程文件做了一次独立live hash扫查。四图和原始报告身份已经单独核实。

可保留为：**固定真实世界布局失败证据、忠实 native 资产/材质试放证据、成对静态视图及有限邻云遮挡证据。** 不可保留为：K世界美术接受、完整恢复通过、任意角度/飞行接受、硬件GPU通过或全部GOAL完成。

下一设计工作应针对原替换单元的大覆盖、邻接与云群层级先作明确新布局/体块提案，并独立解决当前主暗面的读形和冠肩层次；原单anchor单unit方案和四图失败原样封存。此建议不是授权本轮缩放、挪机位或向其他云根推广。
