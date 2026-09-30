# 38 场景生成与渲染（在 Hub 上运行，不在本机）

`main.py` 用程序化方法生成参考场景，每个预设对应一张参考，并用 EEVEE 渲染。每个场景输出一张 PNG 和一个可编辑的 `.blend`。

- **地形**：mathutils 噪声高度场 → Decimate（塌陷）低多边形面片 → 按面着色（沙、草、林、岩、雪、浅水）。
- **植被**：几何节点按 `tree_density` 属性散布树集合。
- **云**：多个球体合并后 Remesh 体素化，再 Decimate。
- **大气**：有界体积雾盒。
- **效果**：灯塔、风车、雨、闪电、星月、彩虹、灯火。
- **室内**：导入 `cabin_*.glb`，加 Bevel 修改器，用暖色点光源和室内体积光照明。

## 运行

```
E:/GameDev/GameDraft/.tools/venv/Scripts/python.exe hub_run.py <新tag> 1343 1128 1218 ...
```

- 会把 `main.py` 和目录下全部 `*.glb` 打成 ZIP 上传，用 Blender 4.5.13 在 GPU 上运行，结果下载到 `out_<tag>/` 并核对 SHA256。
- `<tag>` 不要复用：已有 `hub_task_<tag>.json` 时，脚本只会取回旧任务，不会重新提交。

## 状态

每张参考的最新一版汇总在 `final/`（20 张的 PNG 和 .blend，加对照总览 `overview_a/b.png`）。镜湖类预设（1128/1129）用 Cycles 渲染，其余用 EEVEE。如实评分和下一步见 `reviews/round-38-worklog.md`：最好的约 35～40 分，没有一张达到 60 分。
