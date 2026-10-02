# 法线 API 路径窄只读复核

2026-10-02 19:02 UTC。复核范围仅已失败源的原始数据、逐 float32 重放及官方实现；没有修改模型、原 raw、旧 validator 或启动新 Blender。

## 直接核实

- 亲读官方 Blender v4.5.14 `rna_mesh.cc` 498–506：polygon RNA getter 调用 `face_normal_calc`
- 亲读同版本 `mesh_normals.cc` 141–144：单三角调用叉乘法线；166–175：缓存 face normal 对三角也走 Newell 累积；417–443：flat corner 取缓存 face normal
- 亲读 `normal_diagnosis.py` 并实际执行 `python -B normal_diagnosis.py --verify` 成功；原 raw SHA256 为 `0b39aa841519b65874e24d219c4e74d3063daa8dfd9bdf86b15fdb90e9b5a99c`
- 全 3130 面实际 corner 与逐步 float32 Newell 最大分量差 `5.960464477539063e-08`；每面的三个 corner 相同，旧第一次失败与本次 polygon/corner float32 位型相同

官方源码仅网页读取，没有本地源码副本。准确 URL 与行号在 [normal-diagnosis.json](normal-diagnosis.json)，不是凭常识猜测 API 算法。

## 必须保留的验收差异

**原 corner 对数学几何的 3e-5 门仍然失败。** 22 面超限，最大分量误差 `0.00015941344933428914`、最大角差 `0.009158468662372497°`。API 重放吻合不等于原几何门通过；改比较对象属于明确的验收口径变化，不能因数字阈值同为 3e-5 就声称原要求未变。

另列成立事实：polygon 对数学几何最大差 `2.7049721644800684e-06`；所有面 flat；同面三 corner 完全一致；corner 单位长度差最多 `1.3277417698631666e-07`，归一化方向与几何法线 dot 最小 `0.999999987224719`。

## 结论与下一范围

接受本失败证据和 API 路径诊断完整外存。它没有保存源文件，没有 fresh-open 或图像，不构成完整 native、视觉、接触、世界或 GOAL 验收。

失败完整插件发布及远端读回后，允许另立明确命名的“API 一致性隔离诊断源”准备：保持原几何、姿态、polygon 数学/方向/flat 的独立检查，显式保留旧 corner→几何门失败与实际误差；新模式仅用于真实保存及隔离诊断图，不冒称旧完整 native 门通过。新准备本身也须先插件上传核回，再实际运行，不复用本次已经消耗的一次准入。
