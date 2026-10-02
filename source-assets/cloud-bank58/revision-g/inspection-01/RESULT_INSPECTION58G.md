# 只读G源检查：保存源images/libraries均为空，原触发类别仍未知

实际运行：2026-10-02 03:31 UTC，
`cloud-evidence/cloudbank58g-readonly-20261002T033107Z-vx7uspi2`。

## 结论先行

新进程打开既有失败源后，**images=0、libraries=0**，原合并条件的两个子门
在这次读回中都通过。原生ID引用图没有强链接ID，也没有文件型图像依赖。
这是保存源当前状态的检查，不证明原build保存前是哪一类数据块触发了失败。
原build的`no_external_data=false`保持不变，不回写、不跳门、不猜测根因。

## 实际证据

- child exit0、wrapper exit0，实际0.475103969秒，CPU2
- wait4 child峰247244KiB；wrapper峰14208KiB；分开峰值保守和261452KiB，
  同时采样合计峰257748KiB，低于原受限窗口预算
- 唯一源仍为`../field_patch58g.blend`，152743字节；检查前后SHA均为：
  `a30f3b267a4de95a9d3fb2514ab99ca22e416607087e9b80cf9bfc5407999b15`
- 1个网格的float32顶点/有向三角身份与原build吻合，8个Empty持久控制参数
  与原build吻合；2相机概要已记录，没有重新取景或改变投影
- 打开后两台相机数据保留指向E源的`library_weak_reference`来源元数据，但
  它们的`library`均为null，`all_strongly_linked_ids=[]`。这不是实际强链接依赖；
  没有跟随该路径读取E或其它外部文件
- stdout保留完整原生清单，stderr为空；原G失败冻结项及此次准备输入全部未变

## 启动状态与原失败不得混为一谈

本次独立进程在打开源之前的factory-startup中，观察到Render Result与Viewer
Node两个VIEWER类图像，路径均为空、没有原生ID/节点引用；打开G源后它们均
不在images中。这个前后差异只属于本次只读进程。

原build曾执行不同的初始化和相机导入步骤，而且没有记录保存前两类数据块
的分别数量/身份；因此上述启动观察**不能确证原失败由Render Result、Viewer
Node或某个Library块造成**。报告明确保持`retrospective_original_subgate_attribution_proved=false`。

## 操作边界

仅调用一次`wm.open_mainfile`，关闭自动脚本，没有重建、保存、渲染、清理、
读取图像像素或手动跟随外部路径。未复制blend，没有生成任何PNG；原G构建
结果依然失败，造型与世界验收仍未发生。这一只读检查的通过不等于G原构建
或视觉通过。

窗口已释放，未自行继续两图。源码、清单、原始日志和实际退出证据冻结后
交父任务发布；任何下一步由父任务另行安排。
