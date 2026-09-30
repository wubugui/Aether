# 19h 原生灯塔集成独立复核

**支持保留当前原生共享灯塔建筑底稿。** 最终运行已 passed：原生检查、八张 GPU 图与 36 项游戏检查均通过；安装资产与已接受的 19h 候选身份一致。此前两次失败继续保留为 failed，不能合称所有运行通过。远端入口首阶明显偏高，场地过渡和参考中的海礁、附属建筑、夜间灯光及天气环境尚未完成。本结论不是全部 20 张参考场景验收。

## 运行与失败链

最终证据目录：`E:\FeiTing\captures\validation_runs\19h-native-lighthouse-final-20260908T082434Z-482422f7fede4b64b58f197a71159771`。下文相对路径均相对此目录。

- `19h-native-lighthouse-20260908T081741Z-013b2ef8a2624aa0ad6d56d22e4e0fbe`：import passed，derived-install failed。冻结错误日志明确记录切线数组长度必须是顶点数的四倍；空 PackedFloat32Array 被识别为存在的错误流。该次已写碰撞，未完成合并网格。
- `19h-native-lighthouse-repair-20260908T082039Z-7c31371c56954044b4576030f27feea3`：切线流改为 null 后 derived-install passed；native-check failed，原因是检查只接受 ALPHA 枚举。正式导入的 13 张透明表面实际为枚举 4，即 ALPHA_DEPTH_PRE_PASS。保留的独立原生材质诊断日志确认该枚举及真实 alpha。
- 最终 run：只验证已经安装的资源，没有再次 import 或 install。修正后的检查接受两种透明模式，并实际逐项确认 8 张 pane 的 alpha 0.27、5 张 lens 的 alpha 0.10；未以删除透明检查来获得通过。

最终 manifest 有 10 个 passed/exit 0 阶段（native-check、8 capture、game-test）。独立重算 80 个绑定产物 SHA 均一致；repair 全部绑定产物与最终 installed-evidence 副本逐项相同，两份失败 manifest 也与原目录一致。最终 inputs 与 repair 安装后 inputs 的文件身份集合相同。详细结果见 `E:\FeiTing\reviews\round-19h-native-integration-independent-audit.json`。

## 安装范围和原生身份

安装前后非 `.godot` 生产资源的变化恰为 7 项，与 preparation-changes 一致：新增 `blender/settlement_kit/lighthouse.blend`，替换 `assets/models/lighthouse.glb`、`assets/collision/lighthouse.res`、`assets/meshes/lighthouse.res`、`scenes/prefabs/lighthouse.tscn`，更新 `assets/asset_catalog.json`、`assets/settlement_kit.json`。两份目录 JSON 的语义变化仅涉及 lighthouse。缓存输入在前后快照中收集口径不同，不把新增收录的 `.godot` 项误报为额外生产建模变更。

当前生产 BLEND SHA 为 `10540b562966c58df68f6bd7e5030cb0b5e991d0aceb292a318c88215876f000`，GLB SHA 为 `79b5fd32ec06a3c3cf0fc948e31333c9d374fb018437f2fa630293e266382eb1`，与 19h 冻结候选完全一致。可编辑源 225 分件的身份延续前次源审查；原生导出保持 24 个网格/材质表面。

父代理执行的重开原生检查确认完整 3988 三角，派生碰撞面相对模型的最大顶点误差 0 米，派生合并网格相对模型的最大顶点误差亦为 0 米。两处实例各有 24 张表面、13 张透明表面；8 张玻璃 pane 的实际 alpha 为约 0.27000001，5 张透镜约 0.100000001，透明枚举均为 4，其他 11 张不透明表面 alpha 为 1。prefab 已解除统一 world 材质覆盖。

两个实例位置保持 `[162,15.7729997634888,410]` 和 `[-1120,24.3579998016357,-1980]`。各 16 条墙体射线分别在局部高度 5、12 米的八个方向命中本灯塔碰撞体，共 32 条。它们证明这些墙体接触采样，不证明入口角色行走。

World SHA 仍为 `6bae76d50d5802971a51d8882d3c8e86fe5cdcd8ab250de2eae856d487f7d7e8`；已核对当前 World、18c 地表材质/着色器及 17e 重贴地散布岩石 SHA 均与安装前后记录一致。整体输入差异中没有地形、cliff 模型或 scatter 变更。

## 八张实图

本人实际查看 `images/harbor-front.png`、`harbor-back.png`、`harbor-gallery.png`、`harbor-context.png`、`harbor-door.png`、`remote-front.png`、`remote-door.png`、`opening.png`，没有通过只看指标替代实图。

港口五图保留了候选的石塔比例、暗色承托、透明灯室、可见灯芯和三阶入口；没有在原生导入后恢复黄板或全模型统一材质。与候选同机位原图的像素差并非零：front/back/gallery/context/door 分别有 1148/727/880/351/507 个不同像素，最大单通道差分别为 47/33/51/64/33，边界记录在 audit。实图没有观察到建筑造型或材质归属倒退；细小差异的全部原因未确认，不臆测为单一光照因素，也不声称图片字节一致。

remote-front 显示共享模型实际用于第二处原生位置，塔身、基础和灯室均成立。remote-door 的第一阶立面显著高于港口，基础侧面也更突出：这是已知局部地表较低造成的场地适配问题，不能因底面埋入和踏面露出就称入口已经自然、无障碍或步行通过。后续应在该场地组织台基和通路过渡，避免把裸阶直接放在草地上的状态当作最终景观。

opening 保留当前大世界、前景崖壁与地表基底，没有从本次局部建筑审查扩展为整体美术通过。参考 1126/1342 中的灯塔岛礁组合和不同天气时段仍需真正建模、布置和运行实现。

## 游戏结果与结论边界

`reports/game-test.json` 的 36 项全部 passed，provenance run_id 对应最终 run，报告中的源 SHA 与最终 inputs 对应，且 packaged=false。这是本地工程运行验证，不是 Windows 发布包验收。最终八图均绑定同版 inputs，不能借用前一包图像补齐最终关卡。

本审查未启动 Blender/Godot，没有再次运行测试或修改生产。原生 GPU、射线及派生数据检查由父代理执行，本人独立读取日志、身份、差异及实图确认。有限结论是保留已集成的 19h 共享建筑，继续场地与全世界制作；两次失败历史、远端入口问题及完整参考目标未完成均继续成立。
