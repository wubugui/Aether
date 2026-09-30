# 30b 独立造型审查

结论：保留降低、内移外围岩肩和重建低岸侧片的方向，整体仍未达到 1342。`full_reference_accepted=false`，全参考 Goal 未完成。

已直接逐张查看本轮五张原始 GPU PNG，并对照 1342 与 30a。原图路径和 SHA256 见同名 JSON。运行完成、装配门禁、支承几何分别是证据，不替代视觉判断。

## 五视图

- **night-reference**：Lower coastal double band is reduced and outlying tall fragments are lower. The retained 30a tower/land proportions and house-right composition remain. Broad upper grey slope and narrow perimeter belt still read as a manufactured tier.
- **day-reference**：Daylight confirms lower shoulders are closer to the island. Unchanged upper surface still has a broad orderly slope; lower changes alone do not deliver the irregular central island in 1342.
- **day-d-front**：Shorter shoulders avoid the 29c long wedge ramps, but several are substantially buried. Main slope remains wide and relatively uninterrupted; overlap is not proof of visible rock interlock.
- **day-d-back**：Rear coast has more local height variation, yet the upper land rim still forms an almost continuous ledge. Original top surface preserves its broad connected planes.
- **day-c-front**：Clearest remaining defect: narrow dark band follows the boundary of the broad grey upper slope. Lower rocks are less bead-like than 30a, but some read as separate low pieces and others disappear into the body.

## 独立几何与暗带定位

实际 GLB 与源几何对应：地表/道路保持；core-cap 接口一致；18 个局部侧片投影有效，中心之间没有连边；边成对且方向相反，主岩有正体积。17 岩块真实编辑存在。完整记录在 `round-30b-independent-geometry.json`。继承已经通过的 30a pad/路径覆盖，没有重跑全套覆盖。

18 个地表侧裙面仍存在，源面索引 2940–2957，顶部与底部 XY 完全相同，厚度 0.649999619–0.650000572m。实际 day-c-front 相机/FOV 投影坐标见 `round-30b-cap-skirt-localization.json`；投影边界贴合原图可见细暗带。结合 core 已无中间环，支持该暗带来自保留的人工地表侧裙。此处是源、投影与原图的定位，尚未用单独材质隔离渲染作因果实验。

编辑岩肩上表面与道路/pad 没有投影交集，净空为 null。两块岩肩与树轴 2m 盘有小片区投影交集，线性面裁切最小地表下净距分别 9.872537m、8.232923m；这是指定支承片区的有界检查，不能扩张为整棵树网格无碰撞或完整行走通过。

七主肩均在所取 z=0.5/2/4m 中至少一个水上截面与主岩重合。West/Southwest 等部分截面近乎整块都被主岩覆盖：证明接触也提示埋入过深，不能称可见咬合成功。Southwest wash ledge、South low reef、North tidal end、South low satellite、East tidal satellite 五个父子对未在这些截面证明重合；前四在 z=0.5m 的间距约 0.8993/0.4641/2.1743/1.2924m，最后一块在三个高度均无截面。不能据此声称各高度都分离；局部水隙也不自动构成缺陷。

## 后续

先将主地表与主岩焊成可编辑实体，移除内部重合 cap 和 0.65m 人工侧裙，保留真实地表、路径、基础；这针对已定位的细环带。随后必须看同相机真实 GPU 图。如果宽大上坡仍然遮住短低岩肩，应局部削改实体包裹坡面、形成错位转折，并有选择地露出岩肩；不要再以全体截面相交或追加外围碎石代替可见造型。

本轮没有由审查者启动 Blender/GPU；没有宣称完整自交检查、全体接触、完整行走或全场景完成。Root 的 59 落点差 0 与 196 绑定核验保留为其 `round-30b-runtime-incremental.json`，没有重复计作本审查的独立实测。
