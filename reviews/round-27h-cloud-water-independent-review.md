# 27h 独立云水视觉复核：已纠正月盘误判，美术仍打回

更正说明：本报告初版错误声称两张27h保存图缺月、并与门禁矛盾。该结论现明确撤回。这是本审查者的视觉观察错误，不能归因引擎或显示UI，也没有“延长等待恢复月亮”的成立证据。下面内容已按独立原PNG解码复核更正；27d/e云水意见不变。

直接打开 `ref/1342.png` 和本轮两张保存 PNG，并与已直接观察的27e夜图比较。本轮：`captures/validation_runs/coast-moon-readiness-27h-20260908T153333Z-8b7579b40e2d437a8b1142c3bfdb7403`。

| 保存图 | 直接观察 |
| --- | --- |
| images/night-reference.png | 月盘明确存在，独立解码后的原尺寸月区裁剪可见完整多面月球，且该区与27e逐字节相同。水高光相对27e更细、更横向，属于局部改善；亮带仍密集规则，前景仍出现分段亮团，与参考不规则波光存在差距。 |
| images/night-reference-later.png | 月盘明确存在，月区与 t0、27e逐字节相同。前景亮团、细条反光与 t0 的分布确实不同；两张静帧只能证明水图案改变，不能认证连续动画质量。云群层次问题未见解决。 |

两份 `.png.json` 的 `sky_mesh_diagnostic.pixel_readiness` 均报告 `ready=true`、`bright_samples=25/25`、`attempt=0`、最低要求20、投影中心约 `[1126.065,165.984]`。更正复核中，本审查独立使用 PIL 解码27e/27h的 t0/t18 四张原PNG，提取 `[1080,120,1170,212]` 的90×92区域：四区全部8280个像素逐字节相同，RGB SHA256均为 `a641b1483067ab29f855f3b7773b09e71386c6ae590d97184d220488df1676d6`；中心RGB为 `[172,188,227]`，每区有3036个像素三通道均大于128。保存图与月盘门禁没有所称矛盾。

独立证据为 `round-27h-independent-moon-decode.py`、`round-27h-independent-moon-decode.json` 和两张 `round-27h-independent-*-moon-crop.png`。两张原尺寸裁剪均已直接观察，显示完整月盘；原PNG没有修改。另读取root的 `round-27h-saved-moon-pixels.json` 和 `round-27h-moon-observation-correction.json`，后者报告27e/f/h的 t0/t18与27g共7张图月区一致，并报告27f/h对应整图SHA相同；这部分跨轮全量比较来源于root，独立复算范围为27e/h四张。

已观察 PNG SHA256：

- night-reference.png：`e287a25ab46c79b50446437e3fa655684e7b5d97e74f6ac4e2ed718562f5ee7f`
- night-reference-later.png：`78bf5000fc506b3a35849e039ff16a5425b42add368bdd7dae5e4eb7109b86b1`

曾读取 `round-27f-moon-missing-input-diagnostic.json`，但其中“缺月”的观察前提现已被更正。不得继续从该前提推断渲染、编译或等待恢复原因；相关旧结论已撤回。

结论：月盘存在，不需依据本次误判修复月亮或门禁。水尺度调整可保留为继续迭代方向；水高光与云群美术仍未达标，整体继续打回。未安装生产，完整 20 参考 Goal 保持 active。此次纠错没有重跑GPU。
