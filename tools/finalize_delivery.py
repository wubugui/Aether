"""Create the delivery record and portable package from verified artifacts."""
from pathlib import Path
import json, re, zipfile, hashlib

ROOT=Path(__file__).resolve().parents[1]
def report(name):
    result=json.loads((ROOT/'captures'/name).read_text(encoding='utf-8'))
    assert result['passed'], name
    return result

assets=report('asset-validation.json')
game=report('game-validation.json')
tour=report('flight-tour-validation.json')
stream=report('stream-flight-validation.json')
startup=(ROOT/'captures/packaged-startup.log').read_text(encoding='utf-8')
assert 'status=0' in startup
assert f"{assets['model_placements']} modeled placements" in startup
assert (ROOT/'captures/packaged-startup.log').stat().st_mtime >= (ROOT/'build/Aether.pck').stat().st_mtime
for name in ['packaged-startup-error.log','normal-startup-error.log']:
    assert not (ROOT/'captures'/name).read_text(encoding='utf-8').strip(), name
assert 'WORLD READY' in (ROOT/'captures/normal-startup.log').read_text(encoding='utf-8')

readme=ROOT/'README.md'
text=readme.read_text(encoding='utf-8')
text=text.replace('21,865',f"{assets['model_placements']:,}")
text=text.replace('27 项功能检查',f"{len(game['checks'])} 项功能检查")
text=text.replace('三角面插值','不规则三角面的重心插值')
text=text.replace('- `captures/game-opening.png`',f"- `captures/stream-flight-validation.json`：东、西、南、北四段独立的连续物理飞行，每段约 4 公里，合计 {stream['distance_metres']/1000:.2f} 公里；采样时飞艇所在区块的地形与碰撞均已加载。\n- `captures/packaged-startup.log`、`normal-startup.log`：最终 Windows 独立运行包的截图与正常游戏（含声音初始化路径）启动验证，退出码为 0，错误日志为空。\n- `captures/game-opening.png`")
text=text.replace("-- --tour-test\n", "-- --tour-test\n& ./.tools/godot/Godot_v4.5.1-stable_win64_console.exe --headless --path . -- --stream-test\n")
readme.write_text(text,encoding='utf-8')

plan=ROOT/'BUILD_PLAN.md'
text=plan.read_text(encoding='utf-8').replace('- [ ]','- [x]')
text=text[:text.index('## 已完成与记录')]+f'''## 完成记录与实际证据

| 步骤 | 已交付内容 | 验证依据 |
|---|---|---|
| 1. 拆解 | 上面的资产、世界、交互、视觉清单 | 本文逐项要求 |
| 2. 资产 | 完整飞艇及 16 种环境模型；原生 Blender 文件 | `blender/Assets.blend`、`captures/asset-library.png`、`captures/asset-validation.json` |
| 3. 世界 | 208 块连续地形、425,984 个地形三角面、{assets['model_placements']:,} 个模型实例 | `blender/Aether_OpenWorld.blend`、`captures/blender-world-validation.json` |
| 4. 游戏 | 物理飞行、实体碰撞、停靠补给、导航、地图、存档、声音 | `captures/game-validation.json`，{len(game['checks'])} / {len(game['checks'])} 项通过 |
| 5. 视觉整合 | 独立顶点配色、实时光照、阴影、浅滩水色、三维云、UI | 开场、反向、山顶、港口、风车村、远处及线框渲染 |
| 6. 运行与游玩 | 正式 Windows 运行包、完整源工程、操作说明 | 下方连续飞行与启动记录 |

### 连续飞行

- 导览航线：同一个物理飞行控制器，连续 {tour['distance_metres']/1000:.2f} 公里，通过七个三维航路点，途中不传送；最小采样离地高度 {tour['minimum_clearance_metres']:.1f} 米，船体及护盾未受损。测试时钟加速 8 倍。
- 地图延续：东、西、南、北四段独立飞行，每段约 4 公里，每段只在起飞前设置一次起点；合计 {stream['distance_metres']/1000:.2f} 公里，跨出 Blender 初始区域。采样时下方地形与碰撞缺失次数为 0。测试时钟加速 4 倍。
- 功能测试还覆盖了真实按键、刹车、海面碰撞伤害、停靠速度与距离限制、码头表面、补给、进度、航标、存档，以及 Blender 地形与新生成地形的高度和面朝向一致性。

### 可复查画面

- `captures/packaged-game.png`：最终独立运行包的开场。
- `captures/game-reverse.png`：完整背面与另一侧世界。
- `captures/game-summit.png`：从山顶往下看。
- `captures/game-harbor.png`：接近实体港口。
- `captures/game-village.png`：风车、村屋与道路。
- `captures/game-remote.png`：初始区域外约 8 公里处，后台地形加载完成后的远景。
- `captures/game-wire.png`：真实地形三角网格。
- `captures/game-map.png`：由实际地理数据绘制的导航地图。

最终包在 RTX 4070 SUPER、1672 × 941、GL Compatibility 下的开场采样，中位帧耗时约 16.7 ms。该数字是短时开场采样，不是全地图性能保证。远处地形会随飞行加载；直接恢复到尚未加载的远处存档时，需要等待外围区域陆续出现。

### 尚未达成的原图美术验收

- [ ] 开场画面与参考截图逐像素一致。

当前版本完成了可飞行、可探索的三维游戏基础和分步制作清单，但地形布局、云形、植被密度、建筑精细程度与最终配色仍有差异。新增的导航、速度高度读数等游戏 UI 也与参考图不同。不能把本次功能和几何验证作为“画面完全一致”的证明。
'''
plan.write_text(text,encoding='utf-8')

controls='''AETHER — SKYFARER 飞艇游戏 Demo

双击 Aether.exe。Aether.exe 和 Aether.pck 必须保留在同一个文件夹中。

W / S：增加 / 减少油门，松开后保持
A / D：左右转向
E / Q：上升 / 下降
Shift：加速
空格：制动悬停
右键拖动、滚轮：环绕与缩放
C：驾驶视角
F：接近码头并减速后停靠，维修和补给
M / Tab：地图 / 切换目的地
F4：自动导览，操作飞行键可接管
R：回出发空域
F5 / F9：保存 / 恢复
F1：操作帮助
N / F11：声音开关 / 全屏
F12：截图

存档及截图：%APPDATA%/Godot/app_userdata/Aether — Skyfarer/

以参考截图为美术方向，所有世界物体为三维模型。
本版可自由飞行，但视觉效果尚未达到原图逐像素一致。
Godot Engine 4.5.1，授权及第三方声明附在同目录。
'''
(ROOT/'build/README.txt').write_text(controls,encoding='utf-8-sig')
files=['Aether.exe','Aether.pck','README.txt','GODOT-LICENSE.txt','THIRD-PARTY-NOTICES.txt']
with zipfile.ZipFile(ROOT/'build/Aether-Windows.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as package:
    for name in files:package.write(ROOT/'build'/name,arcname='Aether/'+name)
manifest={name:{'bytes':(ROOT/'build'/name).stat().st_size,'sha256':hashlib.sha256((ROOT/'build'/name).read_bytes()).hexdigest()} for name in files}
(ROOT/'build/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('DELIVERY READY',len(game['checks']),'checks;',assets['model_placements'],'placements;', (ROOT/'build/Aether-Windows.zip').stat().st_size,'zip bytes')
