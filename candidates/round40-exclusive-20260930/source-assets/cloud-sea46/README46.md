# Cloud Sea46：独立建模候选，未验收

## 定位证据

实际看过ref/1216.png，44的1216正面、1128/1343背面、1128 all/without-sea和1216 without-sea。1216近景大面积碎硬云海在without-sea中消失，故这部分可明确归属CloudSea。44既有分组诊断只用正面，不能用它证明1128/1343背面巨底责任；已提供独立只读project/tools/diagnose_sea46.gd补背面all/without-sea，当前shell无DISPLAY/Xvfb，需用已有实际桌面执行通道运行。

读取源hub-cloud41/cloud_sea41.blend并做CPU原版front/back/underside：每variant20个独立网格，底层是3个重叠宽薄connected_body。读取Game44的25个CloudSea节点真实变换，1150间距网格、同海拔700，未修改任何锚点或44/45场景。完整坐标和原mesh bounds在geometry-comparison46.json和original41-inspection.json。

## 制作

cloud_sea46.blend是独立可编辑源文件，3个variant各为一个经过真实体积并合的闭合网格。隐藏的Editable46_*_lobe_controls集合保留12–13个原始可编辑云瓣。model_sea46.py记录造型参数和重建过程。没有图片贴片、透明遮挡或镜头朝向逻辑。

顶部以2–3个主要偏置大冠与中型低肩连成整体，再过渡至不同长度小边叶；去掉旧三块超宽垫底。下半部收腹，局部深度不同；边叶错高、有真实缺口。没有逐顶点随机抖动和逐面随机色块，保持flat面的克制几何起伏。顶冠仍连通，侧背出现中层云腔。不是等大球串堆砌。

project/assets/clouds46内3个GLB已核对各仅1节点/1mesh，含POSITION/NORMAL/COLOR_0；Blender Z-up导出为glTF Y-up。集成应按旧variant映射替换网格并保留原Node3D名称/世界变换，不能重新布置25锚点。

## 验证与限制

- model-report46.json：每体约5千三角，边界边0、非流形边0、有正闭合体积
- geometry-comparison46.json：30单位网格实际BVH射线；投影面积分别为旧版85.5%、86.2%、94.8%；下腹中位高度由约-182升到约-88，顶冠最高约337–377。减少的是宽底部和边缘密实率，不是全体等比缩小
- sea46-{0,1,2}-{front,back,side,underside,top}.png：15张Cycles CPU预览，全部实际打开检查。顶部/侧面由碎石变为较连续冠肩，侧背弧腹能读形；纯下方在统一天光下仍有连片暗面读感，不能称巨灰底已消除
- first-pass目录保留首稿CPU图和报告作为失败比较。最终图与源.blend为第二稿收腹结果
- 原cloud_sea41.blend与cliff_eastern_plateau.blend的SHA256复核均OK，见protected-sources.sha256

这是可集成测试的模型候选，不是视觉通过。前两variant投影面积减少约14%，25个既有锚点下可能出现过宽空隙，必须以1216完整生产场景正侧背与合法位移复查连续性。1128/1343背面归属需上述隔离图确认。不能把CPU实图、闭合检查或面积数字称硬件GPU证据或世界总验收。未推送。

## 2026-09-30 20:46 UTC背面定位补证

实际逐对打开cloud-evidence/sea46-back-diagnosis-20260930T204051Z-qQSJnj/images/back-{1128,1343}-{all,without-sea}.png。1128上方大片厚灰底及1343左上巨底均随CloudSea单组关闭而消失，现已确认残留该组责任；不是仅凭bounds推测。其它云层仍在，因此关闭组的图只用于责任诊断，不用于视觉验收。

已准备project/tools/build_cloudsea46.gd及verify_cloudsea46.gd。基准固定Game44，不继承未通过的45；原25根节点本身不替换，保持其全部属性/transform/名字，按原20个mesh实际名称一致性识别variant，替换子mesh并沿用原组active材质。全非目标存储属性递归fingerprint与MM48000 floats读回核对；失败写报告退出；Sky实例均等待3frames+post_draw再释放。独立GUI运行入口/workspace/shared/s.sh，当前只完成官方Godot4.5.1 check-only parse双exit0，尚未运行46实际场景。

## 20:56 UTC 审计修正

首个实际46构建在写Game46之前因无关vegetation fingerprint差异退出。已保留cloud-evidence/cloudsea46-20260930T205153Z-NQsiMd的报告/日志，并把3个已生成prefab完整复制至该run/candidate46-partial，SHA核对。与45并行诊断实证为Godot4.5.1 var_to_bytes(NodePath)未初始化对齐填充导致非确定哈希，不是被保护世界遭更改。现digest同步经12独立进程24组验证的stable_variant：NodePath保持显式类型与完整路径，Dictionary规范排序，Array递归，MM/Packed*原始数据不改；不跳过PackedScene/model_scene内容。46build和verify均有完全未修改连续双snapshot对照门。修正代码parse双exit0，等待父实际GUI重跑。

位移验证补正：旧80m净空只是过度保守设计偏好，不能判定1128低空水面机位碰撞。当前verifier用实际物理sphere/ray：radius=max(0.12,camera.near)，起终点intersect_shape、cast_motion全程sweep和intersect_ray；地形仅检查sphere半径净空。原+350m会记录成功或阻挡，若阻挡再按+150/-150/+75/-75/+30/-30m找首条clear补充路径，保持原参考位置/高度不动。报告明确complete_flight_passed=false；此证据只证明那条camera路径。天气冻结time=0.05，光照预热30frames。

## 第二次实际生产运行结果

cloud-evidence/cloudsea46-20260930T210603Z-nd2yLv：build/verify/wrapper exit0，100检查/15图，保护SHA均OK；视觉仍打回。详见production-review46.md。1128+350m原路径被地形阻挡，原y10高度+150m补充路径通过，完整flight仍false。
