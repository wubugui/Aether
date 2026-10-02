# G保存源的独立post-save两图入口

当前仅准备，未运行本入口或生成图片。原G构建`passed=false`与其源码、源、
所有日志保持原样；没有生成假成功build-result，也没有给旧render入口伪造
前提。

## 本质条件差异

原入口要求当次build成功后才能渲染。现在真实的独立只读新进程已证明保存源
当前images/libraries均为空，网格和八控制身份吻合。因此设立新的**保存后
完整验证阶段**，并不恢复或改写旧构建结果。

该readback只是进入新阶段的前提，并不替代完整检查。每张图各用一个新进程：

0. wrapper启动子进程前和每个新进程导入共享检查器前，逐字验证完整传递依赖
   的SHA，包括旧脚本、控制表、E参考源/报告、原光材/坐标配置与原失败/只读
   证据；不是只验证冻结JSON本身
1. 绑定原失败build、真实readback及其wrapper的字节SHA和退出；断言原build
   仍为false，且使用原152743字节、SHA未变的唯一G源
2. 打开该源、禁用自动脚本；重新核完整网格float32顶点/有向面、编辑组名称
   与权重签名、8个Empty持久变换/参数、3个内嵌文本身份、无modifier、平面
   着色、可见性与无中间网格
3. 两台相机逐项匹配原E矩阵/投影与原G实际证据，侧后仍7%门；原太阳、世界、
   材质、Standard、曝光/gamma、Cycles CPU2/8samples/无去噪均不变
4. 图前明确images=0、libraries=0、无强外链ID，然后才使用原固定机位直接
   输出RGB8 PNG；无后处理、滤镜、重采样或像素修改
5. 渲染生成的内存图像块如实列在post_render_datablocks中，不另存源。每图
   与wrapper都重新核原源SHA，原build的false始终保留

共享旧检查器/配置只调用身份、光材及相机检查函数；不调用旧build或render，
不重建、不修补、不另存、不清理数据块、不自动换机位。图前检查一项失败
立即停，保留部分图和真实日志；不自动重试。

## 排程命令

等待父任务确认只读项发布闭环并安排错峰窗口，才执行一次：

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-g/preview-01/run_preview58g.py \
  --run-approved-saved-source-preview
```

总20秒，两个独立进程，wrapper与child共用CPU2，采样合计RSS并以实际分开
峰值之和保守执行1.5GiB。每阶段记录wait4真实退出、时间、峰值及输入SHA；
两原PNG与CRC/尺寸/SHA检验保留。可再生缓存不进入终态冻结清单。

仍只是CPU源资产观察，不是世界集成、硬件GPU或视觉验收；真实两图完成后
必须与1216参考实看比较，再决定造型结论。
