# 共享灯塔建筑研究：19系列

当前范围是参考1126/1342重复出现的灯塔建筑族。不是完成海雾、月夜、岛链场景；现阶段在已有港口灯塔位置 (162,15.773,410) 做临时真实世界替换。生产原生prefab、模型、碰撞及地图不覆盖。正式装配前还需独立审查、材料所有权与派生碰撞接入。

19a：Blender原生保留201个独立建筑分件、2060顶点/1280多边形（原生计数，非导出三角总数）。八角收分塔体、四段石面、真实内凹窗洞与门、检修梯、挑檐走廊、上下栏杆、八角灯室和屋顶屋脊。候选在 `captures/lighthouse_study_19a`，制作入口 `blender/model_lighthouse_19a.py`，拒绝覆盖已有候选。

首次运行 `lighthouse-19a-20260908T064531Z-5975be6d5f99415eabc3df7555f0378a` 因临时新灯塔根节点缺少原生 asset_kind 属性，World启动报错。虽生成front图，整轮保持failed，不作为技术通过。随后临时节点使用原有AssetInstance脚本，并保持surface_material为空，保留建筑不同材质。

修正后的运行 `lighthouse-19a-20260908T064640Z-0c75ff6bc76845788c86f67e6f327ade` 四张front/back/gallery/context GPU图完整passed。运行冻结.blend/GLB/制作器/预览器和20张新增参考原图；原生世界输入SHA保持。根代理实际看过全部四图：窗洞、梯子、栏杆和实体多方向可见，但石材过白，灯室是不透明黄板，未满足细致建筑表现，交独立审查并制作19b。

19b制作入口 `blender/model_lighthouse_19b.py`：降低石材固有颜色，改为真正半透明灯室玻璃，内部增加灯芯、九层透镜、透镜支架及上下支座。216分件、2444顶点/1502原生多边形。四图运行 `lighthouse-19b-20260908T065252Z-138a4744b39045f8b2f84312d76f02d0` 完整passed。

独立报告 `round-19ab-lighthouse-independent-review.md` 及两个audit JSON：19a打回；19b透明修正、中心灯/透镜可见和中灰石色改善成立，支持继续修形。整体建筑仍未接受：石塔偏细长、环廊承托薄；玻璃像开放亭，存在感偏弱，透镜内部条栅偏密。没有用白日背景或尚无夜景光束否定建筑局部修正。

19c针对独立意见制作：石塔高度压缩18%、下端拓宽10%、环廊下新增真实厚暗八角承托及外挑唇边。四图运行 `lighthouse-19c-20260908T065924Z-5b93f97580854906973bc81e46797ee3` 图像阶段passed，但追加导出检查发现最后一根 `Ladder anchor.009` 错落在原点、最低-0.15m，因此候选不能当模型技术通过。原因是最后创建的杆件变换未在读取matrix_world前显式刷新。`round-19abc-export-inspection.json` 保留failed结果；不覆盖19c模型或图片。

19d只修正上述制作器变换刷新：在坐标烘焙前执行 `bpy.context.view_layer.update()`。218分件、2476顶点/1522原生多边形。`round-19d-export-inspection.json` 实际遍历GLB全部节点和POSITION，确认范围[-4.015,0,-4.015]至[4.015,24.5,4.015]，无原点下错误杆件；玻璃alphaMode=BLEND、alpha约0.16。GLB SHA `375b72a1696d0d08baee54dcef2eb8568ef170fee1755963ae5f88cfd4367151`。这个边界/透明检查不等于整体碰撞或视觉通过。

19d四图运行 `lighthouse-19d-20260908T070403Z-a2a794dd4f8a4f77a48e2bb30c08245e` 完整passed，根代理与独立审查均直接看过全部四图。独立报告 `round-19d-lighthouse-independent-review.md` / independent-audit.json核对43个绑定文件，支持保留作下一阶段建筑底稿：比例更稳，实际0.86m厚暗八角承托可见，透明灯室保持。独立GLB遍历确认218节点、高24.499998m/宽8.030001m/底部0；错误固定杆已回到Y14.863859–14.908140m，无节点落地下。

仍有玻璃偏隐、细白灯芯/条栅、石塔规则横带和门口可读性弱，后续细化不应从19a重来。局部接受不等于原生集成或1126/1342完整场景通过。所有19系列只是临时世界实例，原生位置没有改动；旧灯塔的生产GLB/prefab未覆盖。

后续原生集成还需要考虑材质与成本：当前候选GLB保留218个独立渲染分件，适合检查细节，但不能未经评估就作为岛链多实例的最终渲染组织。Blender原生保留分件，导出时可按不透明材质合并渲染分件；透明玻璃及透镜的排序和多方向动态表现另行检查。原生AssetInstance的统一surface_material会覆盖GLB所有材质，集成时需明确保留灯室/石材/金属的不同材质，不可直接复用旧灯塔的world单材质覆盖。

19e承接19d进一步细化：石色改为同一大面连续，去掉四段规律横带；门窗增加实体石套、门口增加三个石阶；灯室玻璃alpha升至0.27，光学透镜单独alpha0.10，透镜从9层减到5层，中心灯芯拓宽并降低白色过曝。Blender保留225分件/2500顶点/1596多边形；不透明导出按材质合并，GLB共24个渲染节点，透明件仍分开。但原生face检查发现两个窗套底部零面积面，`round-19e-source-face-check.json`为failed，未进行GPU拍摄或生产安装，保留候选。

19f已修正石套底部边界的宽度，保留19e其他改进，候选在 `captures/lighthouse_study_19f`，制作入口 `blender/model_lighthouse_19f.py`。Blender构建及原生零面积面检查已完成，`round-19f-source-face-check.json` passed/issues空，源SHA `d27fa4be85bb9a662ffb728da08ea32af033ea4f5a35aff847e0d6e10efa9c6f`；日志 `captures/lighthouse-19f-source-check.stdout.log`。尚未进行19f四图或独立审查。下一步核验实际GLB边界/透明契约后运行 `tools/render_lighthouse_study.py 19f`，不要重做19a/d。

19f后续五图运行 `lighthouse-19f-20260908T074544Z-abed842a35434e13b1c75c0863afca12` passed，但独立审查确认三阶绕序反向及局部基础空隙，不安装。19g仅反转三个台阶面绕序并把基础/阶底延至-0.5m，正体积/朝上顶面、40底点全负gap及五图成立；run `lighthouse-19g-20260908T075734Z-b268458c16d946e39ecdd123ed563286`。独立报告明确港口最低踏面仍埋8.0–12.7cm，等19h再安装。不能将底面进入地表当作踏面露出。

19h将下两阶原始顶高0.24/0.48改为0.44/0.58m，最高阶实际0.7164m、门槛、水平足迹、基础和其余建筑不变。源SHA10540b562966c58df68f6bd7e5030cb0b5e991d0aceb292a318c88215876f000，GLB79b5fd32ec06a3c3cf0fc948e31333c9d374fb018437f2fa630293e266382eb1。225parts/2500verts/1596polygons，24GLB节点。源零面积、台阶闭合/正体积/顶面朝向及实际GLB边界/透明检查通过。

19h新GPU踏面检查最初因Godot导入顶点精度与匹配容差过紧，触发预期12点计数断言；失败日志保留在lighthouse-19h-footing及footing-diagnostic，自己的失败进程已终止。匹配容差从0.1mm改为1mm后实际匹配12角点，增加三个踏面中心；两处各15点，港口最小/最大露出0.072924/0.468212m，远端0.367886/0.737568m。40个基础底点仍全部地下。这只证明采样处的几何衔接，不证明连续面无穿插或入口通行；远端第一阶偏高，留待岛岸场地处理。

19h五张同机位GPU实拍run `lighthouse-19h-20260908T081136Z-5ae8b9c9b2f2432da9e2c4c3ab60f54f`全部passed，根代理直接查看全部五张：三级踏面和门槛可见，主体/灯室/厚承托保持。冻结4项gate及候选/参考。独立代理已接19h审查，未收到接受前不安装。原生集成准备脚本tools/integrate_lighthouse_19h.py及captures/native_lighthouse_19.gd/capture_native_lighthouse_19.gd已编写，后两者Godot语法检查通过；准备了备份、模型/源/两个catalog、仅移除灯塔材质覆盖、24表面派生网格与全模型碰撞、两落点32墙面射线/材质检查、七张局部图+开场及36游戏项，尚未执行。

19h原生集成最终完成并获独立接受。首次 `19h-native-lighthouse-20260908T081741Z-013b2ef8a2624aa0ad6d56d22e4e0fbe` 因ARRAY_TANGENT空PackedFloat32Array格式错误failed；改为null后 `19h-native-lighthouse-repair-20260908T082039Z-7c31371c56954044b4576030f27feea3` 派生成功，但native-check仅接受ALPHA枚举，未识别正式导入ALPHA_DEPTH_PRE_PASS而failed。诊断实际8玻璃alpha.27、5透镜.10，均enum4。新检查接受两种透明模式且核验明确材质/个数/alpha，没有取消透明检查；最终独立验证不重复导入或安装，两失败包原样保留。

最终run `19h-native-lighthouse-final-20260908T082434Z-482422f7fede4b64b58f197a71159771` 十阶段passed，native-check +8GPU+36game。24表面、3988三角，保存的组合网格与碰撞全顶点相对导入模型误差均0；两个原位置各16墙体射线命中。仅7生产文件变化：新blender/settlement_kit/lighthouse.blend、GLB/mesh/collision、prefab及两catalog，World/地形/道路/散布保持。根代理直接查看8张安装后图，独立代理核对80绑定文件并看全部8图，支持保留已安装建筑底稿。报告round-19h-native-integration-independent-review.md与audit.json。不是全参考、场地入口步行或Windows发布验收；远端高首阶仍待场地适配。无需再运行安装/派生/最终通过的检查。

制作转向20a海岸勘察，2565点/两图只读run已passed。发现原Lantern Coast灯塔实际在距该横截面海岸约1.1km的内陆，所需海礁岛链尚不存在。详见round-20a-coast-survey.md的实际collider解释和A/B/C岛链设计坐标；下一轮继续Blender岛岩/草台/守塔屋实体制作，不回头重做19a–h。
