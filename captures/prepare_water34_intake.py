from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];f=R/'captures/validation_runs/rightcoast-33d-20260908T232040Z-ea61879316ae487487e34e2f5d2c313b/study-inputs';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[f/'new-environment27f/open_water.gdshader',f/'coast_environment_27f.gd',f/'lantern_lighting_28h.gd',f/'harbor_assembly_22g.gd',f/'headland_runtime_23g.gd']
out=dict(scope='Read-only34 water/light source intake while33 geometry reviews run. No34 shader/model/runtime edit yet; latest accepted-stage coast must be resolved from33 final records.',bindings={str(p.relative_to(R)):sha(p) for p in files},water_observed_current_code=dict(surface_geometry='Existing sea geometry stays flat; sea_facet_normal changes material normals only.',facet_cell_m=[3.2,1.1],jitter_fraction=.32,reflection='Actual world point/view direction/moon direction reflected about a world-space planar facet normal, then exponent220.',night_reflection_rgb=[.98,1.28,2.05],roughness=.38,day_emission_albedo_factor=.82,shore_depth='OpenGLCompatibility depth reconstruction; actual underlying geometry drives foam/shallow color.',reflection_limits='Sky reflection currently analytic color gradient, no actual cloud/island/house scene reflections. Moon highlight is a lobe, local lantern/house reflection not implemented in this shader.'),visual_priorities=['Current night main view has dense thin horizontal bright comb lines; reference has larger irregular bright facets, varied gaps, richer blue water and many warm harbor reflections.','Preserve actual world-space view/light-dependent reflection and real depth shoreline; no reference-image overlay or camera-facing water cards.','Evaluate broad facet/swell scale, rough reflection lobe and screen-footprint filtering from the actual main/low-water/moving observer views.','Keep source clouds, coast/island geometry and positions fixed during initial water iteration so visual cause is attributable.'],next_action='After33 stage checkpoint, build actual world sea material/surface revision and same-version main/near-water/shifted-view capture; later add warm local-light reflection with actual scene light inputs. All20references+opening goal remainsactive.')
p=R/'reviews/round-34-water-intake.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
text='''# 34 海面与灯火接续入口

本次只读现有同版代码，尚无34模型或shader修改。右岸最终接续以33最新检查点为准；本入口不表示33整体美术已经通过。

当前实际open_water.gdshader仍使用平海面几何，世界坐标下3.2×1.1m抖动三角高度场仅提供法线。月光反射按真实视线/法线/月光方向计算，指数220；夜色反射RGB(.98,1.28,2.05)，白日自发光为albedo*.82。实际固定夜景呈密集细亮横梳线，参考是更宽、疏密变化的不规则亮水片，并有较多暖灯倒影。需要改真实波面尺度、反射瓣和屏幕足迹采样，不能换成按相机摆放的光带图板。

当前天空反射是解析颜色梯度，没有真实云、岛、房屋场景反射；水shader没有接入当地港岸灯具位置。后续暖色倒影要来自真实灯源输入，与场景距离和视角一致。水岸浅色/泡沫已经从实际深度重建，不能回退为统一岸线假边。精确源码SHA见同名JSON。

初轮水面修改保持海岸、灯塔岛、云与机位不动，验证日夜主图、近水和移动观察下反射变化；不要同时重做全世界。后续再协调灯具/环境受光与其他天气、时段。完整20参考与原开场仍未完成。
'''
p=R/'reviews/round-34-water-intake.md';assert not p.exists();p.write_text(text,encoding='utf-8');print('34 source intake saved; no rendering changes')
