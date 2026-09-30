# 35b 风暴增量独立视觉审查

结论：运行failed，视觉亦需返工，不接受或升级。八张PNG已经生成，可以支持有限视觉比较；不能用它们覆盖GLES运行错误，也不能把局部改善说成风暴场景完成。

本次直接查看 `captures/validation_runs/storm-35b-20260909T003744Z-443b5747f7fa4c3a9164f2609d8d953a/images/` 八原图：`storm-high.png`、`storm-coast-low.png`、`storm-inside.png`、`storm-edge.png`、`storm-clear.png`、`storm-flash.png`、`storm-cloud-back.png`、`storm-inside-flash.png`。只作相对上一轮已看35a/1125/1341的增量判断，没有重读旧全套或重复引擎。

## 可保留的进展

inside原来横穿风暴下方的亮橙带消失，现在暴雨侧为冷灰、晴侧保留较弱暖色；这比35a协调。high上方云体抬高，主视野不再被几个巨黑囊压住一半。旧原生云不再纯白，说明统一天气着色的方向产生了可见效果，但当前颜色和形制仍不合格。

水面原先满海白色划线显著减少，尤其左侧暗海不再满铺亮碎纹。新增inside-flash约 x620–910/y235–565 可直接看见三处闪电折线和较弱分支，顶部有紫色照亮；不再只能依据运行记录认定闪电存在。普通flash主机位仍主要看到左云照亮，是观察方向差异，不能据此说闪电消失。

外移后的cloud-back终于能看见云体外轮廓与下方海岸，结束了35a近乎全屏近面遮挡。它用了不同相机，只是诊断可读性改善，不能当同机位形制改善量测。

## 仍需返工的优先级

1. 云体仍是首要问题。inside上半部是很大的暗平顶板，狭长亮灰接缝像板件边；edge/clear露出的边形是一串近重复弯折岩片。cloud-back直接显示两层宽平波纹带和整齐暗夹层，像层叠板，而非风暴锋面连续而多尺度的云体。这不是仅调亮、修雨条或消除材质错误能够解决的造型差距。
2. low/high右上原云成为不透明褐灰岩球，旧纯白虽消除，却没有形成合理的远灰云和受光边。晴侧天空仍以平灰—土黄渐变为主，风暴边界像大块竖向柔化分区；应保留1125允许的暖晴侧，同时建立真正的云层深度和天光差异，不能全域一刀切成灰或橙。
3. 实际高海岸未动：仍是广阔平原、远处孤立山峰、近海一小片既有村岸，与参考临海山脊、水道、高岩肩组合相差很大。本稿没有改地貌，既不把它当35b新增回归，也不把天气进步当成已补齐地形。
4. 雨线变斜，但部分又长又直、跨大段屏幕，缺近远粗细与雨幕体积感；是否源于wrap须代码与运行证据确认，静帧不作根因诊断。白浪减少是进步，真实有起伏感的大暗波、浪峰和岸边碎沫仍不足。inside-flash闪电目前更像细折线，分支/远近层次与云内光晕可继续完善，优先级低于巨大的云板和岸体。

## 失败记录与身份边界

直接读取manifest：`status=failed, passed=false`。错误日志保留四条 `Parameter "material" is null`，分别来自GLES3的 `material_casts_shadows`、`material_is_animated`、`material_get_instance_shader_parameters`、`material_update_dependency`。本代理没有独立定位生命周期根因，不把父代理正在做的35c修复写成已修复35b。

失败manifest尚未把八PNG及八sidecar登记到artifacts。因此本报告JSON独立保存它们的实际SHA，明确 `manifest_matches=false`；不可写作八图已获完整manifest产物绑定。所有sidecar run ID一致，runtime/water SHA均与冻结源相同；27项本轮冻结源/渲染器/错误日志均匹配其已有manifest记录。runtime SHA `ba0a1d0155d1cd2418a92692d5dea25fe12d99ee28f27eb27e6b83a99eadb5f7`。

inside-flash记录time2.04、flash1、60段闪电和3灯，样本386材质绑定。这些值与可见闪电一起构成有限证据，不等于整场景功能通过。全部视点为离散样本，未做连续飞行验收。

未启动GPU/Blender、未修改生产或候选，只写本审查MD/JSON。全20参考目标保持未完成。
