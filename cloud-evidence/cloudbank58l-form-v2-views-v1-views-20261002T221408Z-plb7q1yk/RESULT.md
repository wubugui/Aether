# form-v2原机位四实图：成像完成，局部改善但造型仍打回

2026-10-02 22:13:59.850153 UTC实际启动。薄适配准备先经GitHub插件发布823de40b1cdb1378b0ebb2af817cd7105b3af05a，17路径/17blob新空bare逐字回核且同树clean后才执行。原现存源恢复已fa8607bc完整外存；没有再建模或重新保存源。

## 实际终态和四张原图

- launcher5真实exit0，53.14090641599614秒，views_chain_verified=true，remaining_owned_pids=[]；worker6 exit0/52.91625710000517秒
- 四独立Blender进程7/26/45/64全部exit0：5.318059854、5.157777960、5.531925259、6.446971811秒；各低于27秒，总120秒门未触发
- 固定官方Python3.11.15/原pidfd兼容桥/v3监督复用。CPU2、Cycles8 samples、不降噪、1179×664、校准pixel aspect，原绝对相机/材料/灯光不变
- 14557受保护文件4779459703B前后记录相同，722冻结同；全树采样峰540304KiB/保守三级峰591268KiB，无timeout或RSS门触发
- 唯一源324985B/SHA33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a始终不变。仅open/render/capture/restore，无build/save/export/world装配
- 每张实际baseline/rendered/restored raw、命名camera、render filepath、原PNG的SHA与真实进程链接齐全。末态原数值/结构身份恢复；各baseline/restored文件字节也分别完全相同

原PNG总3215974B，直接普通Git blob，不重封装：

1. outputs/01-original61-front.png，766134B
2. outputs/02-k-trial-front.png，766131B
3. outputs/03-k-fixed-side-back.png，859673B
4. outputs/04-k-fixed-near.png，824036B

原前两camera姿态/投影本来相同，两独立运行PNG的RGBA SHA也相同。因此四个命名输出只有三方向，未宣称四个不同视角。尺寸/原字节SHA/完整解码RGBA SHA在original-png-decode.json。

## 真实图像结论

亲看全部新原图、旧同机位图及ref/1216，并由独立审查再看原图，详见INDEPENDENT_VISUAL_REVIEW.md。

有限改善：前冠更饱满，近处旧贯穿肩部的尖长斜带明显减少，副肩确实抬出体积。这是实际形体变化，不是换光照或图片处理。

**源造型仍打回。** 新近肩变成更大的连续整坡，冠—肩—腹之间缺中小块团和明确层次；侧背虽两冠更钝圆，长陡壁与平台边缘仍占主导，整体仍读成岩山/厚台。没有因隔离源缺世界背景或CPU低采样噪点否认真几何，也不把存在三角面本身当问题。需要修的是可见大形分组与转折节奏。

## 资格边界与保存

本次只证明API一致性隔离诊断源可按原机位真实成像。原form-v2 source整体失败保持failed，组合前件是其真实成功build和后来的独立成功fresh-only，未伪造原整阶段成功。

原corner→数学几何3e-5在每张默认态仍23面失败，max0.0005249128728819219、角0.03410575291451074°；历史旧22面单独保留。API/Newell、flat、朝外和polygon几何是各自有限门，不能替代旧角点几何门。full_native、参考视觉、接触、天气、世界及全部GOAL均未通过。

14大原JSON保存为9唯一原字节版本：2gzip流/3部件939502B、7严格literal-byte-splice版本，完整原大小/SHA与原literal核对；原工作raw未改，未JSON重写。原源已完整Git存储，此项不复制它。

先把本项所有真实结果/原图/复核及进度通过GitHub插件完整发布，远端逐字核回、新空目录恢复14JSON并解码原PNG，再开始下一有限造型修正。禁止同一失败形体再跑碰运气或只改变光照材质遮盖大整坡/长壁，保持世界与旧源保护。
