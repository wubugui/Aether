# API 隔离诊断准备的窄独立复核

2026-10-02 19:27 UTC。只读复核已冻结准备，不修改文件、不启动引擎。

## 实际检查

- 亲读完整新 normal 函数、diagnostic 双失败绑定、runner scope 传递及实际 native 差异
- 未发现写入normal或改变原几何/姿态门；scene、child、wrapper、receipt均显式full_native_acceptance=false，原corner几何要求逐状态实际重测保留
- 亲跑normal51项（1.852秒）与-O51项（1.895秒），全部通过；manifest18条逐项大小/SHA相同
- original_failures()实际返回精确3fc9d27fe46f83fc279b0902a852ac895c8c59a2d77e93f66a1fa651c5fee597与b8cc9985e206be4fc8f69b80c6e51ebebccaac4e8b1eb177ad6ced4784efe814
- 亲取原失败raw调用新validate_normals：旧corner→几何仍false、22面、max0.00015941344933428914；新API重放差5.960464477539063e-08
- 已审v3监督模块直接复用，不新造或重复扩展监督框架

## 结论边界

有限接受准备，先GitHub插件完整发布及远端核回，才一次source诊断保存/独立fresh-open。尚无native/source/图，纯测试不作真实RNA或保存通过。

若实际通过，只能称“隔离API诊断源可编辑保存恢复”。旧corner→数学几何3e-5门默认22面失败（最大角0.009158468662372497°）继续显式保留，不称原完整native、视觉、接触、世界或全部GOAL通过。全部source产物再外存核回后，才能另一次原机位诊断图。
