# Cirque54 v1：独立单肩原生试形

当前只完成源制作与离线几何证明，**没有原生场景集成，也没有视觉通过**。父任务将运行五面真实渲染后决定是否进入临时世界观察。不能把本源或数字检查称为整体GOAL完成。

## 实体与依据

- 实际重新查看原 `ref/1128.png`、`ref/1129.png`，以及已保存53west的1128接近200m和1129前视图。将cirque处理为近中景冰蚀宽肩，未按远主峰的像素位置强抬近岸根部
- 源：`massif_cirque_wall_cirque54.blend`，9个可编辑mesh分件，共1624三角；GLB为额外交换副本；`cirque54-payload.json`保留世界坐标/顶点色/分件与候选碰撞三角
- 原48源692三角根体先映射到保存53的实际mesh，水下脚及穿水三角全部保留；原48、53west及51b资源均未写入
- 新岩肩最高231m，厚雪最高232.383m。以不规则原生约束点制作主肩、湖向岩台、两条下行沟及短背沟；没有沿同一断面逐排放样
- 分件：rock_body、upper_cirque_mass、snow_gully_a、snow_gully_b、snow_field_north、snow_field_saddle、snow_back_basin、lower_rock_shoulders、shore_rock_apron

## 已核对的范围

1. `native-readback-proof.json`：新进程Blender重开全部9分件，三角与payload在0.1mm量化下一致，边界边/非流形边/退化面均0，体积均正。原692三角逐三角匹配。岩雪分层有意埋入原根/主岩体，未做合并布尔
2. `continuous-footprint-proof.json`：从保存53west完整1096个非水layer4碰撞体取得实际世界面；未处理类型0，Ocean明确排除。按真实AABB安全裁选后，本源涉及4块terrain与4座山，无建筑/浮岛支承混入。所有新分件完整XZ投影在实际Y≥0干地三角并集之外面积均0。主岩体投影118842.2266m²
3. 主岩体为上下成对、顶面投影无内部重叠的单值高度场，最小厚度12m；外侧为简单多边形的竖向闭合面。配合GEOS投影重叠面积约1.6e-8m²的数值残差，证明新增主岩体自身不交叉。该证明不把不同岩雪分件的有意穿插当异常
4. 3065个间隔≤0.5m边间样本，最高边界相对完整实际支承为-4m；19个建筑保护区/保守村落范围与新增体完整包围盒分离
5. `channel-and-full-building-check.json`：完整171个建筑点与已真实验证的保存53west物理射线对照，最大误差0.0006103516m，新源带来的支承变化0。完整查询包括此前漏读的Ground_1_-4，没有沿用六tile的错误expected
6. 两条下沟实测：A沟前5个控制横断面岩槽均低于双岸18m；B沟5个控制横断面凹深9.10–13m；背沟9.10–13m。**A沟末端外侧岸超出干地footprint，被CDT裁去，保留为开放出口，不能声称末端双岸完整**。需要五面实图判断收尾是否自然
7. 当前已验证53的1261个落位逐项检查，126项根支承改变、1135项根支承未变；53west既有120项没有新支承变化。126项分布：oak_1_-3 63、poplar_1_-3 26、oak_0_-3 12、rock_1_-3 9、bush_1_-3 6、poplar_0_-3 5、rock_0_-3 5。**这只是根支承观察集；树冠/岩石实际mesh体积影响未完成，不是最终散布改动授权清单**。当前未修改任何实例

## 五面入口

父任务运行：

```sh
bash source-assets/lake-cirque54/v1/launch_preview54.sh
```

已通过Godot `--headless --check-only` 解析。wrapper仅实际Compatibility渲染，使用项目外XDG目录、Dummy音频、禁用VSync；写独立 `cloud-evidence/cirque54-source-preview-时间-随机/` 和 `tools-feiting/cirque54-preview-last.txt`，记录输入SHA、stdout、stderr、真实exit。

源舞台沿用53west五面的太阳/环境光，材质取冻结53实际cirque绑定。临时加载的完整PackedScene离树读取，等待3帧及frame_post_draw后释放，PackedScene引用置null，再清理8帧；完整世界不加入live树。根据真实viewport和全部顶点计算统一正交大小，实际截图四边至少7%余量；任何PNG错误/裁切门失败均返回非0。`preview-framing.json`记录真实分辨率、机位、边距，不能拿请求分辨率冒充实际输出。

## 保留的限制与错误记录

- 第一版附加沟槽探针在开放出口遇到空bank值，第二版误筛运行报告kind字段为building而非实际buildings；这两次只读诊断错误日志保留。第三版完整171点核对成功，未改源/阈值/资源
- 五面尚未看。单肩是否仍显陡墙、白片是否过宽、开放出口及旧绿根部是否自然，必须由真实图片判断；数量/闭合/干地包含都不是造型通过
- 所有原机位、water/depth、默认场景、boat、sky、west及其120落位保持冻结；未混入旧cirque/east/crown失败首稿
- 1275/1276巨斜面/粗锥群、全湖绿岸、旧天空球云和飞艇构图仍未解决

`frozen-baseline-sha256.txt`记录当前51b、保存53west、48cirque源和53dwest源身份。后续真实集成必须另建独立候选及严格scope清单，先完成实际mesh体积影响和落位核对，再保存/重开/运行物理与视图验收。
