# Cirque54源审查检查点

原生源身份和数据不变：9分件、1624三角；原692三角下部源保留；主岩肩231m、雪最高232.383m。未保存Game54、未修改碰撞或散布。

## 实际五面与坐标修正

父任务已实际运行并逐张查看 `cloud-evidence/cirque54-source-preview-20261001T073318Z-Q7tgAL/images/` 的5张图，本源作者也全看。雪沟避免了旧横向白带，但上肩仍偏单一高块，有较长三角和侧背大面，A沟开放出口需在世界里观察。源图展示整个原地下/水下根，不能把其暴露壁面直接当成世界可见区域。

该次原始exit6和报告原样保留。原因是 `unproject_position()` 返回1672×941逻辑viewport坐标，却除以1280×720物理PNG尺寸。附加证据 `cloud-evidence/cirque54-framing-correction-20261001T073636Z/corrected-framing.json` 从原未舍入边距及两组原始尺寸完整重建投影坐标，再按同一逻辑坐标系归一化；5面最小边距9.0199907%，原7%门全过。PNG逐一SHA固定，未重画，也未把旧exit6改成0。

改正脚本另存 `preview_cirque54_framing_v2.gd` 和 `launch_preview54_v2.sh`，headless check-only parse exit0。不需要为此立即重渲染。

## 逐件实际三角自交结论

最终证据是 `actual-triangle-self-intersection-proof-v3.json` 和 `zero-area-candidates-diagnostic.json`，两次均用新的Blender进程、`--python-exit-code 1`并真实exit0。

- 从本.blend实际loop triangles取原生float32坐标，以float64计算，不改变源坐标、不放宽1e-5m距离阈值及1e-7m²共面投影面积阈值
- 各分件穷举AABB筛选共15113对。以三角平面/边相交与重心包含检查非共面交叉，以凸多边形裁切检查共面正面积重叠；普通共享边/共享点只有整个交集仍在该边界上才排除
- 9分件自穿插及正面积重叠均0。与其他分件的正常埋根/贴岩厚雪交叠没有混入自交统计
- 4个原生几何对照：非共面交叉、共面重叠均检出；正常共享边、相离三角均不误报
- 8个共面零面积候选通过单独GEOS距离进一步区分，全部实际分离，最小投影间距1.0684m
- 首个仅BVH候选版本保留但不作为完整依据；第二版穷举+float32运算的共享端点舍入误报保留，最终v3使用更精确运算解决，没有放宽阈值或编辑实体以消除报告

## 已授权下一项：4张未整合世界诊断

入口已解析通过：

```sh
bash source-assets/lake-cirque54/v1/launch_world54.sh
```

只在内存中对冻结的保存53west场景增加cirque的8个新视觉件。原692三角mesh节点直接保留，原collision、全部scatter、west全部mesh/碰撞/绑定保持不变。分别拍1128/1129的原前视及沿原相机朝向200m接近，共4图；显著UNINTEGRATED标注。当前尚未拿这4图做源造型通过判断。

入口记录唯一run、SHA、stdout/stderr/exit、实际物理PNG/逻辑viewport、相机和作者锚点。投影归一化采用逻辑viewport；不改变原机位或自动构图。前后比较scatter实际buffers+transforms、west mesh数组/绑定/碰撞、cirque原root/碰撞和保存场景SHA。所有原碰撞与落位仍是53，报告明确未整合；不会保存场景或先迁移散布。

下一步根据4张世界图决定是否返工源，后续真实候选保存仍需完整实际mesh体积散布影响、严格资源scope与新原生/运行时验证。源闭合、自交、干地和建筑支承的通过不代替视觉验收。
