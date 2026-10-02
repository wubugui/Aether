# G失败源：只读数据块诊断

这是一项新的只读检查，不是G构建重试。打开既有152743字节源，明确关闭
自动脚本；不重建、保存、渲染、清理数据块或复制blend。只读images/libraries
元数据和原生ID引用图，不访问图像像素，不跟随报告中的外部路径读文件。

分别记录启动状态和打开后的数量及name/type/source/users/packed/filepath/
library；以原生`bpy.data.user_map`列直接引用、活动scene引用链、实际链接ID，
补充图像节点引用与弱引用来源元数据。引用链不等于渲染可见性。只对这两类
依赖范围作结论，不声称审计了任意外部资产或证明外部文件实际存在。

新进程打开后的状态可能不同于原build保存前。若两类都空，应明确说保存源
当前无这类数据块，原合并门触发类别仍不确定；不能回写旧失败或猜成某个
默认图像。检查同时记录网格/八控制/两相机概要，并比对原build网格身份、
持久变换与源文件前后SHA。

父任务安排窗口后，仅执行一次：

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-g/inspection-01/run_inspection58g.py \
  --run-approved-readonly-inspection
```

总限15秒、wrapper与child共用CPU2、合计RSS保守1.5GiB。唯一运行目录保存
stdout/stderr、实际wait4退出/峰值、输入SHA和终态；失败同样保留，不自动重试。
不运行后续两张图、不改变原门限或G源码；结果先报告给父任务，再冻结发布。

API依据：
- https://docs.blender.org/api/4.5/bpy.ops.wm.html
- https://docs.blender.org/api/4.5/bpy.types.Library.html
- https://docs.blender.org/api/4.5/bpy.types.BlendData.html
