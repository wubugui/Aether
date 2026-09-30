# 35c 风暴有限增量独立审查

结论：保留雨条wrap修正与本轮运行稳定的进展，整体视觉继续打回。下一轮建议优先制作近海高岸与河口地貌；云体问题保持未过，不能当作已经接受或无限期放弃。

直接查看 `captures/validation_runs/storm-35c-20260909T004220Z-c4392024b9a4475faaff26f81d9cbcab/images/` 的八原图：`storm-high.png`、`storm-coast-low.png`、`storm-inside.png`、`storm-edge.png`、`storm-clear.png`、`storm-flash.png`、`storm-cloud-back.png`、`storm-inside-flash.png`。仅比较35b已看图的有限增量，不重复35a全套来源检查。

high/inside相对35b贯穿大段屏幕的长雨丝明显减少，雨成为分离短条，背景更容易辨认。近处仍有少量较长投影片，不能把任意长雨线都归因wrap，也不能仅凭静图证明所有时间均无拉伸。实际冻结雨shader从实例 `MODEL_MATRIX[3]` 求一次900m循环位移，给所有顶点加同一偏移；代码与实图共同支持本次修正方向。

clear晴侧未见明显雨线；edge左侧雨更可见、右侧渐弱；inside阴侧保留冷灰雨景，35b已修的橙色横带没有回来。high/coast-low的大片暖灰天空、褐色原云仍不自然，未因本稿雨修正而消失。

inside-flash三道闪电与分支可读，云和下方场地有紫色照亮，较普通inside能清楚区分闪光状态；普通flash机位也保留左云照亮。冻结公共闪光场Y=230与本稿声明一致，但本审查未额外启动GPU验证全部空间光照，不把颜色改善扩展为物理光输运通过。

## 未改变的主要问题

三份云GLB与35b逐字节相同。inside大平顶板、edge/clear重复折叠层边、cloud-back两层宽平夹带以及low右上的褐灰岩球仍明显。海面过暗、白沫稀少，缺有尺度变化的浪峰与近岸碎沫。地形仍是宽平岸配遥远孤峰，尚无参考临海山脊、高岩肩、河口水道的基本组合。这些是保留问题，不是本稿新增回归。

下一轮优先实际近海高岸/河口：以low/high已见的大陆临海带建立山脊向海下降、高低岩岸交替及深入陆内的水道，验证前中后景关系。当前天气功能增量已有可接续基底，而原平岸与远山仍缺基本场景结构，继续只调雨/云材质无法代替。云体仍是后续明确返工项，尤其应改实体比例与多层体量，不只重新着色。

## 运行与身份

manifest `status=passed, passed=true`，引擎阶段exit0，`storm-world-views-error.log`为空；35b的四条GLES material-null错误本轮未复现。冻结runtime确实把旧材质、新材质和shader cache保存在game metadata。该次通过仅证明本轮未复现，根因未隔离，不能宣称已经证明某一唯一生命周期原因。

八图及八sidecar全部匹配本轮manifest，run ID、runtime与水shader绑定一致。定向核对本轮runtime、雨shader、公共场、水shader、日志、报告SHA，未重新扫描旧全世界。runtime SHA `27289529fb375309d058fccd4bfaf235fbd256f377caa394b0110206a30ec9bb`。三云GLB哈希对比35b相同，详细证据存同名JSON。

本代理未启动GPU/Blender或修改生产与候选，只写审查文件。离散八图不等于连续天气飞行，35b失败包仍保留失败；本轮通过不等于完整风暴艺术、地形或全20参考完成。
