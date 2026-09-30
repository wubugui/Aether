# 30d 独立造型审查

结论：三处短肩真实露出增加，应保留为局部进展；day-c-front 最显眼的中正面宽灰坡几乎没变，整体仍未达到1342。`full_reference_accepted=false`，全参考 Goal 未完成。下一步必须先按可见像素定位实际源三角，不能继续把正面问题笼统归到West/Southwest/North。

已逐张直接查看本轮五张原始GPU图，对照30c同相机原图与1342。完整路径、SHA256见同名JSON。

## 五图

- **night-reference**：Central D now shows several additional lower rock turns and recessed breaks; original 30a building proportions and house-right layout are retained. The island remains a rather broad regular upper mound compared with 1342. Local improvement only.
- **day-reference**：The fixed reference view makes the newly cut recesses more legible around the central island, with lower shoulders appearing as part of the coast. Still sparse, broad main planes and a simple upper mound; not a complete reference match.
- **day-d-front**：The central/front grey slope is largely retained. Differences concentrate near the left peripheral edge and other partly hidden sides. The foreground low crags remain unchanged. Do not infer that the large middle slope was cut merely because three rocks gained exposure.
- **day-d-back**：Clearer local change: left and right rear areas now contain additional recessed breaks and shorter ledges. The new cuts expose underlying shoulder surfaces, but several cut edges remain straight and pocket-like, and two broad grey lobes still dominate. No obvious new open mesh seam is visible in this image.
- **day-c-front**：The most conspicuous middle/front grey slope remains almost unchanged from30c, roughly across x650-950,y495-605 in the original1672x941 image. Some change is visible at the far-left perimeter, but there is no substantial new division across the middle slope. Camera is from Blender local(+X,-Y), so this is an east/southeast-facing view; screen center cannot be assigned to West/Southwest/North by object names.

## 区分露出证据与屏幕问题

本轮实际GLB独立量测的肩顶Z≥0.5m露出投影：West从约0增至51.832m²，Southwest从约0增至43.206m²，North从0.508增至58.213m²；对应新露出朝上表面总面积63.409/53.208/77.436m²。这证明被包裹的真实岩面露出了，不证明它在某个镜头中可见，也不证明主坡造型已经解决。

实际day-c-front侧车相机换算到Blender局部为[65.0, -70.0, 40.0]，位于+X/-Y的东南侧。原图约x650–950/y495–605的中正面宽灰坡仍占主要面积，此矩形仅是人工视觉定位。不能根据West/Southwest/North这些岩块名称给该区域分配方向或源面；镜头方向只能约束大方向，准确归属应靠实际像素射线命中。Root正在做该定位，此报告不复用尚未得到的射线结果为独立证据。

固定参考及day-d-back可看到更短的后侧/边缘坡折；day-c-front则只有较远左岸等局部变化。后侧切削仍有一些直边与凹槽感，但未见明显敞开的网格裂缝。下一稿应改善被确认的可见中前坡，而不是为追求露出数量继续盲挖西侧。

## 保持与验证范围

独立几何报告证明道路25.572388m²、两pad123.98m²、当前C/D树轴盘77.465743m²的原支承线性面全部保持；路径和17岩块保持；实际GLB闭合，有向体积21674.484839m³。该证明不依赖已经失效的旧top索引。详细见 `round-30d-independent-geometry.json`。

Root运行增量报告196绑定匹配，59落点相对30a最大差0.00027465820311967093m；基础采样最大差0m。这些数值已读取其JSON，归属Root的实测，不重复计作本审查独立运行。不能把落点差写成全零。

## 下一步

依据当前真实相机对中前坡像素的射线命中，找到主壳源面后，再与实际道路、基础、树轴支承范围裁切。针对那一局部做短而错位的坡折或克制改面，保留低宽岩肩和原生建筑尺度。不要统一外移17岩，不扩大西侧切削来解决一个尚未定位的正面大坡。下一候选仍应同时看固定参考、正面、背面，避免只改善被遮挡的一面却误认为正面已经改变。

本次没有启动Blender/GPU、没有重跑全场覆盖或飞行测试；真实几何有效、局部露出和最终造型接受分别判断。
