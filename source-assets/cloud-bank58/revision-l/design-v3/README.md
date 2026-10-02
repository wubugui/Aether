# L design-v3：释放旧内部下接缝，固定真实外岸 XZ

这是一个完成即停的**设计契约**，不含候选网格、recipe、原生源、GLB、PNG、引擎运行或世界改动。父已确认上一包 `0dafbe77d665f7574ebc08ce2c0dbbe2053ead20` 全部22路径/22blob插件发布及远端原字节核回；本作者没有自行执行Git，也不把父的核定写成自己另行验证。

本次只选B。撤销的是v1作者自设的“旧内部下接缝/下包络几何身份锁”，不是用户要求的四邻连接、原不规则外岸、厚度、内域腹高或观察条件。旧v1拒绝、v2有限通过、build-v1严格锁下接缝的不可能见证都保持原样。

先读 [CONTRACT.md](CONTRACT.md)，机器权威为 [contact-contract.json](contact-contract.json)。只有本项独审、完整GitHub插件发布及实际远端核回之后，才可开另一个真正作者源准备项；本包不会解除旧build-v1的任何拒绝入口。

## 文件与复核

- `external-rim.json`：203个真实外投影边界的有序有限数值段，每段绑定旧源焊接边XYZ和裁剪参数；XYZ中的Y是来源定位，不是锁值。保留约3.8879e−9m接点残差，没有偷偷焊成“精确”曲线
- `contact-evidence.json`：七个既有投影分量各一处非零面积局部见证，另加原530×4706冲突点邻域；包含完整旧/邻垂直命中、三角索引、四角区间、边界距离和原v2剖面的新有限相容检查
- `replay_contract.py`：只读复算上述两JSON，旧场景只解码选中根+四邻；复用build-v1边界提取函数，不调用旧 `analyze()`/survey/52点射线。没有写文件、候选或engine入口
- `check_contract.py`、`test_contract.py`：纯契约一致性及26个正/负控；所有真实候选准入明确拒绝，局部区间程序不能发放全实体通过
- `dependencies.json`：61旧依赖/107585882B原身份；包括v1/v2/build-v1全部成员、旧场景/解码器与四survey。当前进度文件不属于禁止父更新的输入冻结
- `replay-result.json`、`tests-normal.log`、`tests-optimized.log`：实际只读复算和普通/`-O`各26项测试成功；没有把工具等待时间写成精确运行耗时
- `PACKAGE_MANIFEST.json`、`SHA256SUMS.txt`：本包内容身份。checksum覆盖内容与manifest，自身不递归；父添加的独审属于后续发布范围，不改作者manifest

在已恢复依赖的Aether根运行最少命令（只读）：

```sh
PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-l/design-v3/replay_contract.py --verify
PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-l/design-v3/check_contract.py
PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-l/design-v3/test_contract.py
PYTHONDONTWRITEBYTECODE=1 python -O source-assets/cloud-bank58/revision-l/design-v3/test_contract.py
```

Python3.12、NumPy2.3.5、SciPy1.17.0；不需要Shapely、Blender、Godot、绘图库或新的安装。原NPZ按已有checkpoint恢复工具恢复；本包不隐式恢复或重采样它。`--emit boundary/evidence`只向stdout输出重算值，不覆盖权威文件；正常审查只需 `--verify`。

## 接受范围

设计内矛盾检查通过，有限局部可行性成立。**新接触整体验收、可编辑源、float32实际几何、native/fresh-open、原四图美术、世界/飞行与全部GOAL均未通过。** 八个小方形不是新云表面，也没有证明把它们拼起来就会形成合格云岸。
