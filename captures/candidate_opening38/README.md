# 候选38：去暖色系数与水面/雾修正（Godot）

从 `captures/candidate_highcoast36c/` 复制并做文本替换。36c 原件和生产文件都未改动。

- `install38.py`：写入 v12 研究变体（`captures/opening_study_38/variants_run5.json`）。
  - 去掉 storm=0 端的暖色系数；
  - 草色和面片对比调整；
  - 雾色和雾距离调整；
  - 水面浅水带和噪声浪花；
  - 去掉水面暖色调和橙色高光。
- `install38_castle.py`：把 `castle_57174` 换成 37c 的浅石灰岩城堡（`castle37c.tscn`），位置不变，缩放 1。
- `install-report.json`：记录每条替换的命中次数和前后 SHA256。

从候选副本实渲的开场图与研究图逐像素一致。独立审查结论和已知遗留问题见 `reviews/round-38-worklog.md` 的 A 节。

注意：本候选的 Game 场景自带的是暗灰环境光加橙色太阳，并且在 `_ready` 里会加载 35c 风暴天气。直接运行时的画面，和本轮使用日光环境做的渲染不同。
