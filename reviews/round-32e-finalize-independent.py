import json
from pathlib import Path
R = Path(__file__).resolve().parents[1]
p = R / 'reviews/round-32e-foreground-independent-geometry.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['scope'] += ' Full actual pine six-sided bottom footprints against highest surface of all11exported meshes, eight planned instances.'
d['limits'] = [
    'Building footprint is the union of actual lowest-Z horizontal triangles after complete glTF node transforms and planned scale/yaw; no convex-hull substitution and no nine-point-only coverage.',
    'Full design pads, actual building base footprints and their cap/core interfaces are checked by triangle clipping with1mm height tolerance; tiny reported residual areas are numerical.',
    'Eight actual pine bottom hexagons are fully clipped against the highest surface of all11actual GLB meshes, using planned local scale and no additional tree yaw. Axis rays are supplemental, not the full support proof.',
    'Flat supporting terrain does not by itself prove runtime instance height, embedding depth, collision ancestry, canopy clearance or full rendered tree contact; runtime placement remains a separate check.',
    'Closed positive-volume meshes and exact source/export triangle identity do not prove absence of all3D self-intersections. No whole-island self-intersection or cap/core scan outside the three building regions was added.',
    'No GPU, whole-world flight or art acceptance is claimed by this report.'
]
d['all_actual_building_footprints_inside_design_pads'] = all(s['actual_asset_base_outside_pad_area_m2'] < 1e-9 for s in d['sites'])
d['tower_32d_actual_stair_footprint_defect_resolved'] = True
d['all_reference_goal_complete'] = False
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md = '''32e 前景 A 独立几何复核通过，限于本次原生资产、三处建筑地坪和八棵树的真实干底支承。32d 报告及其塔阶梯底域失败证据保持原样；这里没有进行视觉验收。

独立以 Blender 后台重新打开正式 `island_a.blend`，未调用建模脚本，也没有保存修改源文件，前后 SHA 一致。实际导出的 11 件网格分别闭合、有向边成对且体积为正；每件 GLB 的三角形计数集合与本次重开源的实际三角化完全一致。地表为 1128 点/2252 三角，主岩为 644 点/1284 三角。最小三角面积约 0.00003946 m²，未发现本项门禁失败。

建筑检查采用实际资产经过完整节点变换的最低水平三角面并集，再施加本版实例尺度和方向；逐片裁剪整个足迹与地坪，未用凸包或九点采样替代真实底域。

|建筑|本版布置|实际底域面积|底域在设计 pad 外|完整底域地面结果|
|---|---|---:|---:|---|
|左屋|(-23,3)，yaw π/2，scale 1，高程 28 m|84.240004 m²|0|完整覆盖、平坦|
|右屋|(-8,19)，yaw -0.15，scale 0.85，高程 27 m|60.863403 m²|0|完整覆盖、平坦|
|塔|(-3,6)，yaw 0.25，scale 1，高程 30.062103 m|48.566508 m²|0|完整覆盖、平坦|

塔 pad 的半宽 [5.4,5.1] 已覆盖实际外伸阶梯底面。此前 32d 实际底域中最大约 5.963 cm 的地面下降，本版整个底域高度误差仅为浮点噪声（最大绝对值 2.85×10⁻¹⁴ m）。完整塔 pad 的最大高度误差约 0.001726 mm；三座建筑完整 pad 和实际足迹下的 cap 底面/core 顶面都连续吻合，界面最大误差同属浮点噪声。报告保留约 10⁻¹¹ m² 的裁剪残差，没有将其改写成精确零。

八棵树均使用生产 pine 资产的实际最低六边形底域，按本版尺度逐一检查全部 11 件 GLB 的最高上表面。全部底域完整覆盖、连续、平坦，最高支承均为地表 cap，无最高道路命中。(-35,0) 的尺度为本版 1.2。完整干底区域的高度变化为 0 或约 3.55×10⁻¹⁵ m，结论不是仅依据树轴射线。实际 Godot 实例朝向、落地高度和碰撞归属仍由运行记录另行验证。

本次不扩展到全岛三角自交、建筑区外 cap/core 接缝、树冠净空或全世界检查。原生闭合及地坪通过不代表草岩风格、构图、海岸造型或参考画面完成；`full_reference_accepted=false`，`all_reference_goal_complete=false`。

证据：`round-32e-reopened-source.json`、`round-32e-foreground-independent-geometry.json`、`round-32e-actual-tree-bases.json`；对应独立脚本均在 reviews 中。正式源 SHA256：2e8d50ceefa9776634aaa2286a6ede88f47fa1f18ecd7a6f80bb8557377267de；GLB SHA256：8cb8bdf399ae1068ee40230a2ad7282d93fa9d06a8d67cb3c145e192ba90a7b9。
'''
(R/'reviews/round-32e-foreground-independent-geometry.md').write_text(md,encoding='utf-8')
print('32e independent geometry finalized:',d['pass'])
