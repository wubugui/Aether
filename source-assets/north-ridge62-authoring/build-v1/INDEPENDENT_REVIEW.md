# North ridge62 build-v1：独立源码审查

审查完成：2026-10-02 UTC。范围为当前实际作者源码、冻结 binding 和 offline-mapping；未运行 Blender/Godot，未创建 `.blend` 或 PNG，未修改原 preparation/candidate、世界项目或源码实现。

## 结论

**在本次静态、纯 Python 和负测试范围内，已发现的问题均已修复并复核；没有剩余的已知源码阻塞。** 可进入作者的最终 SHA 冻结与默认只读 preflight，再由父任务另行安排有限的 native 阶段。

这不是 native/source-form/视觉/世界集成通过。当前没有 native build、fresh-reopen、真实 raw、四图或实际资源预算成功证据。167 项 instance support 仍未解决，world integration / weather / visual acceptance 仍必须为 false。

## 已发现并关闭的问题

1. **绑定门禁原先存在自我引用。** 独立负测曾证明：改坏 tile→master vertex、tile→master face、原 local XYZ、packed vertex bytes、1131 眼位、changed mask，`check_binding` 仍能通过。当前 `check_authority` 从 SHA 固定的 preparation、mapping summary 和全部 mapping artifacts 独立关联来源；九类复测均拒绝，包括以上六类、control triangulation、source resource 标签、weight/collar 补偿篡改。
2. **source byte 基线保护不足。** 早期 wrapper 未在 views 第一个 child 前维持旧 source SHA，并逐 child 更新基线。当前 views 在入口确立 SHA；source 仅在首次成功 build 后确立；每次 child 前后及 finally 都要求相同字节。`.blend` 不再只依赖被排除后的 protected manifest。
3. **Edit Mode 数据可能过期。** 早期 rebuild 直接读取 `control.data.vertices`，而编辑态数据可能尚未写回。当前对 master control、shared evaluated 和四个 derivative 全部要求 Object Mode 且 `is_editmode == False`，在写网格前拒绝；README 明确要求先退出 Edit Mode。此处选择拒绝，避免自动切模式导致 RNA 引用失效。参见 [Blender mesh-mode API说明](https://docs.blender.org/api/dev/info_gotchas_meshes.html)。
4. **来源标签与作者场可被改坏而维持当前几何。** 当前 source node/resource/origin 分别与 mapping 对照；actual raw 含 source properties；非零 barycentric rows 归一、collar 限于 [0,1]；control IDs、weights64、collar64、canonical Y 的完整指定 dtype 字节分别 SHA 固定。纯重建还与存储 binding 全等。
5. **对象级误移不属于允许的高度编辑。** 最后加入的 six-mesh `matrix_world == identity` 门在任何重建写入前执行；native raw 也增加 control matrix 检查。纯替身测试分别对六个对象的平移与缩放做负测，均拒绝且零网格写入。
6. **最终保护哈希需要计入总预算。** 完整 protected manifest 的独立只读测量为 7,284 文件、约 4.95 秒，当时的 3 秒预留不足。当前 native 子进程可用余量扣除 8 秒，60/90 秒总上限未提高；实际 native 阶段仍可能因时间不足失败，不能预称预算通过。

## 独立执行的检查

- 当前 `test_source62.py`：普通模式 21/21、`python -O` 21/21 通过；最终复跑分别约 8.707/8.878 秒
- `offline-mapping/test_mapping62.py`：普通模式 9/9、`python -O` 9/9 通过；含原四块重新提取、24,576 有序 corners、artifact SHA、反向 slot membership 和格式/base64/尾随属性负测
- 当前所有相关 Python 文件 AST 可解析
- 原 `preparation-v1/FINAL_SHA256.json` 仍为 `12d9f492d3ae1251d37f6b8b94e9e5877eb85dd96f723f97542a5c4885818702`；其中列出的全部 11 个原文件逐个 SHA 相同
- 原冻结 candidate Y 未变，完整 float32 world-Y SHA 为 `2eca5d39aedc03678f7d4611aa8aa497bb616ec9e7b5bade5da16db5284d13d5`
- 当前 binding：27 控制点、12 固定边界点、15 relief；shared master 4,326 顶点和 8,192 三角形；四 derivative 保持 6,144 / 6,144 / 6,058 / 6,009 原属性 slot
- 每个 derivative face 经原 index sequence 展开后精确对应其 master face；2,479 changed original triangles、1,246 per-tile frozen overrides；未变顶点完整 float32 字节不变
- 轴映射、local origin 往返与 Godot triangle 反向正确；初始 native float32 控制高度代入不会改变冻结 candidate

### 可复现的纯替身作者逻辑测试

审查者另外提供 `test_rebuild_mock62.py` 与 `REVIEW_MOCK_TESTS.log`。普通及 `-O` 均 8/8 通过，覆盖：初始冻结输出、五个 derivative write 调用、handle 改高、重复执行不重复累加、master/handle 差值叠加、边界及水平编辑拒绝、六对象的十二个 Edit Mode 负例、六对象的十二个 transform 负例。

**该测试主动替换 `sys.modules['bpy']`、对象存储、embedded loader 和 `write_mesh`，完全不导入真实 bpy，不执行网格写入。它只证明 Python 作者逻辑，不能替代 RNA、Blender 保存重开或 GPU/native 证据。**

从 Aether 运行：

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python source-assets/north-ridge62-authoring/build-v1/test_source62.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -O source-assets/north-ridge62-authoring/build-v1/test_source62.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python source-assets/north-ridge62-authoring/build-v1/test_rebuild_mock62.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -O source-assets/north-ridge62-authoring/build-v1/test_rebuild_mock62.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python source-assets/north-ridge62-authoring/build-v1/offline-mapping/test_mapping62.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -O source-assets/north-ridge62-authoring/build-v1/offline-mapping/test_mapping62.py
```

## Native 路径静态复核

- `write_mesh` 先完成 material/group/全部 CustomData 分配，再逐个按名字重新取属性并写入；未保留 attribute RNA 句柄跨后续分配
- actual raw 先落盘并记录 hash，之后才 `validate_raw`；verify 必须为不同 PID，fresh-open 使用 `use_scripts=False`，不会再保存。该参数与 [Blender 4.5 wm API](https://docs.blender.org/api/4.5/bpy.ops.wm.html) 一致
- polygon normals、corner normals 分别与几何法线容差对照，只对同一三角形内三个实际 corner normal 要求一致；不把 polygon/corner float32 逐 bit 相同作为前提。[Blender 4.5 RNA 实现](https://raw.githubusercontent.com/blender/blender/v4.5.0/source/blender/makesrna/intern/rna_mesh.cc) 确认所用 corner-normal API 存在，但真实运行仍待检查
- 原 compressed vertex/index/color storage 保留；每个原 split slot 的 local XYZ、RGBA 和 index 来源明确。UV/UV2 缺席，normal/tangent 仅保留原 packed bytes，不声称已语义解码或 Godot roundtrip
- wrapper 只使用既有 `bounded_support58k.run_child`；该 helper 拥有 child PID、进程组 kill、wait4/reap 和退出状态，CPU affinity 两核、RSS 上限 1,572,864 KiB。未重新实现生命周期框架
- source 最多 build + verify 两个进程，总 60 秒；views 最多四个 named render，总 90 秒。持久 exclusive attempt + terminal 门禁止重复/并发同阶段；默认分支没有 native launch
- 1131/1347 eye、target、FOV55 独立对照冻结 intake，side/back 诊断位置固定；四图 1179×664、100%、pixel aspect 1。没有缩图逃预算路径
- main candidate project 整树、source-assets、blender、assets、ref 和 root project.godot 在保护清单内；运行期间其他作者任务也不得修改这些被保护树，否则必须失败，不能把差异忽略

## 受审最终源码 SHA256

| 文件 | SHA256 |
| --- | --- |
| contract62.py | `f1ac7098eb511bdc6d292c18ae233bb13fbcd798719a73a314fba7d2fc8363ac` |
| prepare_bindings62.py | `32e7d0da85639db8893f6167b9c8c4245986343da20bade6af9d39f18e4dcf29` |
| rebuild62.py | `56cecf1c8cebefa986de3d7301a620eafecad0004ce29e6e03a2b92711c27159` |
| native62.py | `56a047e91c27e6ae715cae0dc86dad40ebaddc3663045b93797d536d700f7fec` |
| run_source62.py | `68e93934f3add9eb47e6bc3b998d9287d3794bbe1e7cac0d85b359a0bc2dcad1` |
| test_source62.py | `9af06be437ed1872cf38574c32d3c5bf86d2187f27762287a26918d2ed9062b9` |
| test_rebuild_mock62.py | `bc542d99c1a0621a3eae797b9ee50dca52631d7a9ca74d67507275f4ceca8458` |
| bindings62.json | `a8b634d10c5e1dd57884f9a782b43853ffac9119a290609351c225ddb4df3c27` |
| SOURCE_README.txt | `124b4227e8c3883eee9247e94996827b12b8b4d55cb84ddeb8185bfc7d2ec0cd` |

本报告只覆盖上列版本。最终 build-v1 manifest 与默认 preflight 是作者接下来的封存步骤；任何此后源码变化都不能自动继承本审查。审查结束时未发现 source/view attempt 或 terminal，也没有 `north-ridge62.blend`。
