# 30k-r1 独立造型审查

结论：保留少量宽面的方向与东侧低肩树组；30h密集折扇确已消除。整体仍未通过1342：前左部变成过大的整片斜板，中部仍有尖窄切口，背面长槽没有解决。`full_reference_accepted=false`，全参考Goal未完成。

已直接逐张查看30k-r1五张原始GPU图及1342，对照30h/30d实际图。原图SHA与路径见同名JSON。

## 五图

- **night-reference**：Corrected tree group is lower on the east shoulder and the compact tower/house composition remains. The central island reads more simply than30h, but its upper mound and limited short convex block layering still differ from1342. Night scale alone is insufficient for acceptance.
- **day-reference**：Fewer broad surfaces replace the fluted front, preserving building proportions and house-right composition. However the island still reads as a regular upper mass above a small number of peripheral fragments; short staggered convex shoulders are not yet clearly expressed.
- **day-d-front**：Dense vertical fan recesses are removed. There are now fewer large concave/slope faces and the two relocated trees occupy a lower east ledge. The left main face is too large and plate-like; central straight cuts and pointed notches remain. This is a valid direction, not complete shape acceptance.
- **day-d-back**：Old broad rear lobes and long narrow central cleft remain. Tree relocation is visible from the reverse side without an obvious floating whole tree, but this does not prove complete trunk-base contact. The south/east change did not fix the rear cleft.
- **day-c-front**：Most direct improvement over30h: no repeated line of narrow vertical fan facets. The left/front surface around x530-770,y495-590 is instead an oversized continuous inclined slab; a straight seam and narrow pointed cut remain near its inner/right side. The lower tree group adds vertical layering, but wider concave planes alone do not create the reference short broad convex block structure.

## 保留和剩余差异

前坡从30h反复排列的细尖凹面，变为更少的宽折面，这是明确改善。两棵东树落到较低的肩面，画面层次更清楚；没有必要为降低后的树位再保留旧圆筒保护壁。

但day-c-front左侧约x530–770/y495–590仍是一块很大的连续斜板，内部直分缝和尖窄口仍明显。参考中央岛的宽块面具有短、厚、凸起和错位关系；“把很多窄凹面换成几块更宽的凹面”仍不等于实现这种层次。此处应保留/重塑有真实宽度的主岩凸肩，接到两三块高程和方向不同的大面，缩短或错开长直切口。不要继续只增加凹面宽度、深度或数量。

背面原来的长窄深槽和两片宽坡瓣基本没有变化，需要单独定位处理。前侧更好不能使后侧自动通过。仍应按真实相机/源面定位修改前左斜板与中间分缝，避免再按岩块名字猜方向。

## 树组落位

直接读取五份本版原图侧车：C、D每视图各7棵松树，五保留与两移位的数量关系保持。20条移位记录（两树×两岛×五视图）局部坐标匹配(17,-1.5)/(17.6,-5)，尺度0.8/0.55保持，实际ground_collider均处于所记录island_root之下。它们在正背面未见明显整树悬空。原生几何已验证0.3m盘连续上向支承，第一棵约21.31°、盘高差0.1909m，第二约4.41°。这不等于整树干底面与坡面全部贴合，不作该声明。

## 运行与证据范围

审查对象为30k-r1。首次30k运行因Root的碰撞根检查误将逻辑island_d字符串当实际节点名而失败；该失败保留，Root修复为实际island_root/collider ancestry检查后重跑，原生模型没有重建。R1侧车中的D根为复用C资产的实际根，不能再用逻辑名字子串要求它。

Root的本版增量JSON已读取并归属其运行证据；独立报告没有启动新GPU/Blender。道路/pad/五保留树支承与17岩、路径保持、六点实际切深见 `round-30k-independent-geometry.json`。运行passed、原生闭合与局部美术改善不替代完整场景/全参考验收。
