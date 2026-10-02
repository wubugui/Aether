# L 隔离诊断源四原机位实图：工程成像完成，实体美术打回

2026-10-02 19:50:58.584769 UTC 启动。原生源与完整保存/fresh-open证据已插件发布 `aa3c54c378eea644968bf0a95532f1300a6d3a51`，68路径/65唯一blob完整远端核回，并从新bare导出的存储包在新空目录恢复44原JSON、原319519B模型SHA精确相同，之后才运行本views。

## 真实四图与执行

- launcher5真实exit0，44.497547680002754秒，views_chain_verified=true，remaining_owned_pids=[]
- 四独立Blender子进程7/26/45/64全部exit0，5.169122121/5.049636506/5.368207437/6.442035989秒；各低于原27秒界，总低于120秒
- CPU2、Cycles8 samples、无降噪、1179×664、原校准pixel aspect、原材料和源灯光；固定原绝对机位，不居中重框取好看图
- 14265受保护原文件4660636369B的前后记录一致，295冻结输入保持；全树采样峰432052KiB，无timeout/RSS触发
- 只打开原319519B诊断.blend，不save/rebuild/export/world装配；源SHA始终7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7
- 每图实际baseline/rendered/restored raw齐全，实际命名camera与render filepath已绑定；四renderer末态恢复原source数值/结构身份，每个baseline/restored原字节也分别相同

四张原PNG：

1. `outputs/01-original61-front.png` 764893B
2. `outputs/02-k-trial-front.png` 764890B
3. `outputs/03-k-fixed-side-back.png` 856438B
4. `outputs/04-k-fixed-near.png` 837671B

总3223892B，全部原样直接普通Git blob。原前两camera记录本来一致，本次两图RGBA像素SHA也完全一致；不声称四个不同视角。保留两次独立运行的原PNG元数据与证据，不改图或把一图复制伪装另一运行。尺寸/原文件SHA/RGBA SHA详见 `original-png-decode.json`。

## 亲看后的结论

已逐张看原图，并做[独立视觉/真实性复核](INDEPENDENT_VISUAL_REVIEW.md)，对照ref/1216及本孤立源合同。

成立的有限改善是连续厚主体、主冠/副冠之间确有宽谷、侧背与近角看到实体体积。没有用背景图或单机位薄片代替新网格。

**源实体美术仍打回。** 侧背读成两座截顶山体接长陡壁；近角肩部被长斜带/大片面主导，主冠—肩—腹的分面尺度和转折节奏不够像目标云岸。前图虽出现大云冠轮廓，部分谷侧尖陡、块面仍偏岩山。没有因缺森林/世界背景、软件采样噪声或“存在三角面”本身否决低多边形风格；这些是不理想的真实体块比例与面片组织。

本次是API一致性隔离诊断图。原默认corner→数学几何3e-5仍22面失败/max0.00015941344933428914/角0.009158468662372497°，full_native_acceptance=false。成像流程完成不意味着原完整native、参考美术、接触、世界或全部GOAL验收；没有运行世界试验。

## 保存和下一项

14个大原JSON按9唯一原字节版本保存：2唯一gzip流/3部件927261B，7版本仅原PID/实际render设置/临时image-state literal byte splice，逐份完整SHA验证；原工作raw不改，不JSON重写。所有真实日志、观察脚本、阶段失败/成功范围、四原PNG与复核一起外存。

先全部插件发布、远端逐字核回、原PNG解码及新空目录恢复14原JSON，再依据本组实际侧背/近图做限定形体修正。不能重复同模型/同机位碰运气或只换灯光材质掩盖山壁造型，也不扩大无关证明而一直没有新可看图。未外存核回前不开始下一模型/开发/渲染。
