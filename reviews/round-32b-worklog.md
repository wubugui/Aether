# 32a/b 前景A制作记录

本轮是实际建模、装配、GPU取证和独立审查进展；全部场景目标仍未完成。

32a以20l真实A源进行局部正向分段形变，重建两屋地坪和3段全实体地面拟合路；生成后发现新屋过渡影响塔脚，最大约0.470m，保存失败blend和native-check，没有GLB或GPU。32b显式保护三处完整地坪，11个独立编辑件保存并导出实际GLB。没有整体世界重建，没有生产覆盖。

两屋Blender锚点(-23,3,28)/(-8,19,28.5)，scale1/.85、yaw0/-.15，塔锚点(-3,6,30.0621)/yaw.25。固定相机不变。这些是有记录的设计坐标，不是已知原图地图坐标。

独立已重新打开实际保存源且源SHA保持，11件闭合正体积，实际GLB与源三角完全一致。三设计pad完整三角裁剪及真实资产底面并集支承检查见几何报告；塔最低阶梯部分超出设计方pad但实际地面有覆盖且平坦，不能把保守凸包跨空白或方pad超界当失支承。未做全岛自交、全树干底接触、完整步行/飞行验收。

GPU运行 `foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95` 两引擎阶段exit0，五原图和sidecar齐全，root与fidelity_reviewer全部直接查看。46个非A落点保持，三个建筑各9点运行时基础间隙符合原生嵌入深度。8计划树只实例化7，因此run总状态failed原样保留。树(-30,-3,scale.65)源法线z=.348916，另四棵左后树实际存在但在较低后坡被屋坪遮挡；不得写成全部缺失。

两屋入画可保留；完整美术返工。32b草台仍挡住前景厚岩，三旧岩压缩后呈尖楔，近崖是宽直大墙。下一稿重做仅A的紧凑草肩和厚岩分层，并同步短路及可见树肩，不继续缩放整岛以追求简单通过。具体设计简报 `round-32c-foreground-design-brief.md`；其前缘控制点是未验证草案，必须先与实际占用和完整支承相核对。

主参考与32b源的七条实际射线、树根投影已经输出 `captures/foreground32b-visible-grass-localization.json`；该定位只命中岛体网格，未包含建筑和树遮挡体，已选实际可见裸露地面/岩点，不做全场景遮挡结论。

证据入口：`round-32b-root-evidence.json`、`round-32b-root-visual-findings.json`、`round-32b-foreground-independent-review.md/json`、`round-32b-foreground-independent-geometry.md/json`、`reference-view-1342-progress-32b.json`。所有本轮root建模和引擎句柄都已结束，32b源重开独立进程也已结束，不重启旧版本。尚未制作32c；完整20参考、同一世界、Blender精细建模和跳过角色范围未变。
