# Form-v2 原机位实图：独立视觉与有限真实性复核

复核时间：2026-10-02 22:20 UTC。结论：**本次隔离源成像链有限接受；造型有局部改善，但实体造型视觉仍打回。** 不接受 full-native、真实 GPU 世界、接触、天气或全部 GOAL 通过。

## 范围与亲看依据

先读 `CLOUD_RESUME.md` 当前区及 `GOAL.md`。实际用图像查看工具逐张查看本 run 的四张原 PNG，并逐张查看旧 run `cloudbank58l-source-api-diagnostic-v1-views-20261002T195101Z-3kmu_0dz/outputs/` 的同名四图；另亲看 `ref/1216.png` 与辅助 `ref/1218.png`。没有以文字报告或相似度代替看图，没有裁切、改光、重编码或重渲染。

本项只评价隔离源的体块和分面语言。无世界背景、没有飞船/天气、CPU 8 samples 噪点不是否认真正几何的理由。前两机位相同；四个输出只提供三个观察方向，不算四个独立视角。现有前/近图右侧与下方有画框截断，因此不推断画外全体造型或世界接触。

## 分图视觉判断

### 01-original61-front / 02-k-trial-front

- 两张都亲看，且解码 RGBA 完全相同。相对旧图，中央后冠从较尖的截顶峰变得更钝圆、肩部抬高；前景冠肩也更饱满，旧的长斜带不再同样明显。这是可见的局部形体改善，不能说完全没进步。
- 但前景块体仍呈一个大而单一的宽坡面，向下突然收成腹部。后冠、前肩、低谷之间仍主要是“大峰—整坡—窄转折”的关系，缺少足以在这个机位读出来的中小从属体块与错落搭接。
- 右侧可见大平缓连接面和直长分界，未形成参考 1216 云冠、肩团、腹团之间有变化的节奏。变圆本身不等于达到参考。

### 03-k-fixed-side-back

- 两个主要冠部轮廓比旧图更钝、更丰满；中央偏左的肩块更突出，旧中央冠的一条尖长面有所弱化。
- 主要问题仍清楚存在：左下近处大块的长陡壁占据很大面积，中央右侧宽暗壁接着较平的顶沿，再接远侧近直立的截面。轮廓和明暗组织仍首先读成厚台地、岩壁与山峰，局部肩块没有改变整体阅读。
- 这不是“有三角面便不合格”。参考也有陡面和清晰棱线；差距在于这里几个连续大壁面和长坡支配了体量，大小不一、相互咬合的团块层次不足。不能通过提升采样、换灯或只增加三角面数量来宣布该问题解决。

### 04-k-fixed-near

- 最明确的改善：旧图从中左肩部一直斜向右下的细长尖带明显减少，冠到肩的过渡更宽、更饱满。
- 但新图的前景几乎由一片连续的大整坡承担，旧斜带减少并没有同时带来清晰的中小肩团层次；前肩与后冠之间仍是宽鞍/宽坡。这个机位可见的局部更像钝化的大石块，尚未达到参考中有主次、相互遮挡而又连成厚体的云块结构。
- 不把噪点或低对比度误称为几何破损，也不凭单张图断言数学平面。这里的“大整坡”是实际图像中的造型阅读，已与同灯同材质的旧图对照。

## 参考与独立判定

1216 的目标并非光滑球形云：它使用克制分面、大小不一的冠肩团块、层叠转折与有宽窄变化的谷部，厚体之中仍有清楚的节奏。1218 的晴天云也允许尖收边与大面，因此不能把所有尖角或所有大面一律判错。

本源已具连续厚体与宽谷的有限可见基础，form-v2 对长斜带和部分尖冠作了可辨的改善。但近肩连续大坡、侧背长陡壁及台地式关系仍是主要轮廓，**尚不满足 GOAL 的“明确体块、大小层次和克制分面”；低多边形不等于粗糙锥体、平板或随意碎三角。** 本次应保留改善与失败证据，不能转写为源造型合格，更不能据此进入世界验收通过。

## 有限真实性与原文件核实

以下是对既有实际记录和文件的只读交叉核实，不是另起原生进程，不把日志复核包装成新的实际运行。

- 外部实际观察 `external-caller/external-process-result.json`：launcher PID 5、exit 0、53.140906416 秒，`process_exit_observed=true`、`views_chain_verified=true`、剩余自有 PID 为 `[]`。监督记录 worker PID 6、exit 0、52.916257100 秒。外部记录绑定的 supervisor SHA 与实际文件相符；supervisor 绑定的 wrapper SHA 也与实际文件相符。
- 四次 renderer 的 process/result/pre/rendered/restored/events PID 一致，且都能在 supervisor 采样找到，父 PID 均为 worker 6；worker 6 的父 PID 为 supervisor 5。每个 PID 的 starttime 在现有采样中唯一。PID 7/26/45/64 的实测进程时长依次为 5.318059854、5.157777960、5.531925259、6.446971811 秒，均真实观察 exit 0；无 timeout 或 RSS 触界。每个事件序列均为 native entry、校验、fresh-open、render、native terminal，没有 save/build/export 事件。
- 实际保存源 `source-assets/cloud-bank58/revision-l/form-v2/cloud_bank58l_form_v2.blend` 为 324985 bytes，SHA-256 `33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a`，与本次前件、wrapper、supervisor、外部终态及四个 native result 全部相符；四个 result 均 `source_saved=false`。
- `input-sha256.json` 中 722 项、331204149 bytes 实际逐项重新读取核 SHA，全相同。前后保护清单 14557 项，其文件字节完全相同，SHA `41e944b62f2d1141dbd10a12f3b9e23786b08c88dc589383d7d501dfd809c0db`。此处是保护记录的独立比较，未再对全仓所有被保护字节额外重扫；不夸大为第二次全仓核验。
- wrapper 记录的 28 个本次输出 SHA 均实际核同；每个 native result 指向的 pre/rendered/restored 原 JSON SHA 均核同。每组 pre 与 restored 原文件字节相同。rendered 除 output filepath、active camera 和实际 Render Result 图像状态外，其余原 capture 身份与 pre 精确相同，包括 mesh、objects、controls、八个 Text 身份、材质与灯光。
- 四组相机的完整记录（matrix、projection、sampling、原 declared transform/projection hex 与其它镜头属性）在本次 pre/rendered/restored 和旧 run 同名 pre 间精确相同，材质、灯光也与旧图精确相同；rendered 的 active camera 与命名输出逐一匹配。该比较支持公平的原机位形体对照，不是换光换镜头后的主观比较。
- 实际渲染设置仍为 Cycles CPU、固定 2 threads、8 samples、无 denoise，1179×664、100%，pixel aspect 为 [1.0006932020187378, 1.0]；没有 compositor/sequencer。四原 PNG 均重新校验所有 chunk CRC，并实际解码检查尺寸；总 3215974 bytes。前两 RGBA 完全相同，其余两份不同，共三个图像方向。

### 四张原 PNG 身份

| 输出 | bytes | SHA-256 |
| --- | ---: | --- |
| 01-original61-front.png | 766134 | fd60e737b439854dae8e66ddd520ec3927e1995b937b7c17f250ef2c11e327b7 |
| 02-k-trial-front.png | 766131 | f811cb4bba7c6955955a0eb34a7e2cdd713541c11c61a644be4ba7e1f21fc648 |
| 03-k-fixed-side-back.png | 859673 | 910a89719f530c2c81f3c6f0b177394330accfb644534b4d735bc2c73d95309c |
| 04-k-fixed-near.png | 824036 | 6c2757c993ed8ac953459ca7cf21754aa16d66aeed619087e1a55cf8d1ee9525 |

亲看参考 SHA：1216 `f705cb5de0664e9189bdc66b8ed116fc6db5f6ec1f541606df2b399dbde3aa4f`；1218 `774d8f62f8fa48a93ed15650c3bc21971b08b55262dea9421de36f3368f556b6`。

## 成功与失败边界保持

- 原 `cloudbank58l-form-v2-source-20261002T203132Z-gplbz9_7` 的 supervisor 仍为 `state=failed, passed=false`；本次各层仍明确 `original_source_stage=failed`。不得把后来恢复的成功反写为原 source 整体成功。
- 后续 fresh-only 的真实外部终态 `cloudbank58l-form-v2-recovery-v1-saved-source-fresh-open-20261002T212506Z-7knis0f3/external-caller/external-process-result.json` 为 exit 0、`recovery_chain_verified=true`；其 supervisor SHA 实核为 `766756ea0501ecf7e389b69a3569bf972e7d9c99da606782956c08335738615b`，与本次组合前件相符。仅“原成功保存 + 后续独立 fresh-open + 本次原机位 views”的有限组合成立。
- 本次 wrapper 仍保留写出时的 `awaiting_external_process_terminal/passed=false`，完成依据是随后真实监督和外部 wait 终态；这不是把 wrapper 的预写状态当最终失败，也不能反向篡改它。恢复阶段同类预终态记录也不替代其真实外部终态。
- 四视图 pre/rendered/restored 的已绑定法线报告均保持：原 corner 数学几何比较阈值 3e-5 下 **23 面失败**，max abs `0.0005249128728819219`，最大角差 `0.03410575291451074°`。本次只核记录一致及其 SHA，没有重新定义容差或另造数学证明。历史旧默认 22 面失败记录仍另列保留，不能与新默认 23 面混称。
- API diagnostic 的有限成功不是 full-native 成功；`full_native_acceptance=false`，视觉、接触、world、weather、global_GOAL 均不能升级。当前图像是 Blender 隔离源 CPU 成像，不是真实 GPU 世界验收。

## 本次复核动作边界

结果已先报告，再写本文件。只读取既有工程/证据和图像，并新增本 run 内这一份报告；未运行 Blender/Godot/engine，未建模、改候选或旧文件，未启动新开发或设计，未做 Git/Slack 操作。下一项必须等待本项全部成果按现行发布闸门完整核回；本报告不构成开启下一项的许可。
