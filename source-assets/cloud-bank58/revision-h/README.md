# 58H：单核union＋局部肩根融合，单源两图准备

当前只准备源码、控制表、转换证据与轻量纯静态检查。没有启动Blender，
没有H的blend/PNG；G及更早源码、源、图、失败报告全部保持冻结，不修改
CLOUD_RESUME、世界/默认入口，不自行Git或Slack交付。

## 有限设计假设

保持同样八个命名控制、两处独立下腹与1600三角目标，不新增小球或噪声。
两冠沿局部Y压薄23%，各自保持原单核零面实际顶高及完整U/V投影椭圆；右中肩
中心由(181,9,687)移至(181,102,687)，现有左前小肩由(-192,-43,702)升到
(-192,-43,735)。连接核和两腹的中心/转换后零面保持，避免共同腰环与齐底。
所有位置和融合窗口都是本次待实图检验的设计假设，不是参考反推的真实尺寸。

## G支撑半轴不能直接当成H零面半轴

G单核密度为 strength×max(0,1-q²)³，iso=0.125，支撑半轴是名义半轴×sqrt(2)。
对应的单独等值面半轴必须是：

`G_support_axes × sqrt(1 - (0.125 / G_strength)^(1/3))`

仅strength=1时它才等于G名义半轴。H控制表保存的全部half_axes已换算成真正
单核零面的半轴，**没有density strength或support multiplier属性**。

冠部并非简单改旋转椭球的一个主轴半径。先用A=R×diag(零面半轴)，对局部
Y施加S=diag(1,1,0.77)，新协方差为S×A×Aᵀ×Sᵀ，再作正交主轴重分解。
这样完整U/V投影保持；中心Y增加原竖向范围的23%，使顶高保持。两腹完全
保留转换后的独立椭球。具体数值、误差、G/H组合壳包络和输入SHA均在
`conversion58h.json`，它不把单核包络不变冒充组合轮廓不变。

## 局部融合，不全局累加

每个单核使用 `d_i=min(half_axes_i)×(norm(local_i/half_axes_i)-1)`。这是有米制
尺度的**pseudo-distance，不是到椭球的真实欧氏有符号距离**，零面则精确。

hard union取min(d_i)。仅三个指定肩根建立独立候选，初始width均12：
前肩—主冠、侧后右肩—后冠、高小肩—主冠；各有明确紧支撑椭球窗口。
每个候选从自己的两个原始d_i计算一次平滑min，再与全部原始单核一起取min。
不把前一次融合结果喂入下一次soft-min，不做全局多核密度相加。

单候选相对hard min的标量降低不超过width/4；这**不是空间外扩3米的证明**。
窗口外严格回到hard union。面朝向依据每个四面体的线性插值梯度，避免用
hard-min不可导交界的解析梯度决定绕序。分组使用最近原始核归属，不称密度。

## 原生可编辑结构与固定观察

- 八个Empty的平移、旋转、缩放分别控制中心/主轴/零面半轴；没有旧G strength
- 场景自定义JSON `h_blend_parameters_json`保存可编辑肩根pair、width和窗口
  参数；`h_field_parameters_json`记录模型语义。两者构建和新进程读回均核对
- 内嵌CONTROL58H.json、FIELD58H_patch.py和EDIT58H_rebuild.py；可明确手动
  重建，不需外部代码。重建不会自动保存或渲染；失败保留原有H表面
- 仍仅一次18米提取和一次原生Collapse到1600三角，无Smooth/Subdivision；
  不保存密度格或中间高模，压缩blend硬门200000字节，超限保留失败并停止
- 原E两相机/投影、前836×471与侧后836×586、侧后7%门、原中性光材/
  Standard/Cycles CPU2/8samples/无去噪全部固定；每图新进程开源再核完整身份

## 新空场景的VIEWER初始化

经明确授权，仅在本次全新、未保存且没有对象的factory空场景中，导入任何
旧相机之前，逐项记录启动图像name/type/source/users/packed/filepath/user_map
及实际节点引用。仅已观察的默认Render Result/RENDER_RESULT或Viewer Node/
COMPOSITING，且source=VIEWER、无路径、无packed、无ID/节点引用、无fake user、
无像素数据，才移除本次运行时默认块；记录前后数量与名单。

不删除任何旧文件、G源、其它图像或Library。未满足条件的块保持原样，并
继续受最终images==0/libraries==0/无强外链严格门约束。门失败仍保存实际
失败源/报告并停止；不拿分类结果豁免。H的初始化不反推G原build具体触发类别。

## 命令与边界

纯静态准备检查，不运行Blender：

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-h/check_preparation58h.py \
  --write-preparation-report
```

父任务完成发布闭环并安排CPU窗口后，仅执行一次：

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-h/run_patch58h.py \
  --run-approved-patch-trial
```

总30秒、wrapper与child共用CPU2、保守合计1.5GiB，顺序build→front→side-back；
每阶段wait4真实退出/峰值、输入SHA、源前后身份、原日志/PNG完整保留。任一
失败立即停止，无自动重试、改门、换机位、截底或下一版。输出原PNG不改像素。

静态基本连通/包络只是执行准备，实际减面、源尺寸和视觉尚待运行。即便两图
执行成功，也必须实际看过参考与两图后判断中尺度肩腹是否成立，不扩大世界
集成范围，不称连续谷带、自交、路径或硬件GPU验收通过。
