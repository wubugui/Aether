# H原失败保存源的独立post-save严格读回＋两图准备

本目录是新阶段的准备，没有启动Blender，没有H post-save读回或PNG结果。
原H build依然passed=false，156243字节源、原失败报告及全部原输入保持原样。
本入口既不伪造passed build-result，也不调用旧build/render入口。

## 已记录事实与尚待验证条件

H原build已精确记录：保存前images=0、libraries=1；唯一Library为
B_staggered_crowns.blend、users=1、direct_id_references=[]、linked_datablock_count=0，
另有两台Camera的弱引用来源元数据，强链接ID为空。startup没有images/libraries，
没有执行默认VIEWER删除。此事实只解释H当次严格数量门，不回推G旧失败。

新保存源是否仍有Library必须由真实fresh-open确定，不能由G旧结果推断。
每视角各开独立新进程，完整验证后才允许该视角渲染：

1. 导入共享只读检查函数前逐字核所有传递依赖SHA、原源、原H失败与原始日志。
   wrapper同时核原build/wrapper终态1、原passed=false及源身份，不能重标旧失败
2. 记录factory初始库存，禁用自动脚本，打开同一H源；立即记录完整loaded
   images/libraries/强链接/弱来源库存。images或libraries非零或有强链接即停，
   不清理、豁免、重新保存、重建或继续下一图
3. 严格核同一802点/1600有向三角float32字节签名、组名/权重、八Empty持久变换/
   参数、三个内嵌文本、h_field_parameters_json和h_blend_parameters_json，
   无modifier/中间网格、平面着色、可见性及所有原已通过子门
4. 两台E相机完整矩阵/投影与H原build记录完全相等，固定前836×471、侧后836×586，
   侧后余边仍至少7%；原光材、Standard、Cycles CPU2/8samples/无去噪不变
5. 每图直接输出RGB8原PNG，不过滤、重采样、改像素或换机位。渲染后的内存
   Render Result块单独如实记录，不保存进源，不改图前门。每图及wrapper再核源SHA

结合readback+render允许省去第三个只读进程，但每图都必须从fresh-open重复全门。
任何失败即时保留实际阶段/异常/退出/耗时与已有PNG并停止，无自动重试。

## 纯静态准备与排程

静态检查只读旧数据与Python AST，不导入bpy、不运行原生/任何提取减面：

```sh
python3 -B source-assets/cloud-bank58/revision-h/preview-01/check_preview58h.py \
  --write-preparation-report
```

父任务批准错峰CPU窗口后仅执行一次：

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-h/preview-01/run_preview58h.py \
  --run-approved-saved-source-preview
```

总30秒、wrapper和child同CPU2；采样合计RSS并用实际分开峰值之和保守执行1.5GiB。
记录wait4真实退出、时间、峰值，PNG尺寸/CRC/SHA验证。原失败和所有旧文件保护SHA；
不修改CLOUD_RESUME、Git、Slack、世界或默认入口。此目录准备不是源已通过读回、
视觉接受、世界集成、连续谷带/自交/路径或硬件GPU验收。实际两图后仍须实看1216参考。
