from pathlib import Path
import json,numpy as np
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-33d-rightcoast-independent-geometry.json';d=json.loads(p.read_text(encoding='utf-8'));cells=d['low_shore_after']['highest_surface_cells']
def polys(g):
 if g.geom_type=='Polygon':return [g]
 return [p for child in getattr(g,'geoms',[]) for p in polys(child)]
def coords(g):
 if g.is_empty:return []
 if hasattr(g,'geoms'):return [p for child in g.geoms for p in coords(child)]
 return list(g.coords)
worst=None
for i,a in enumerate(cells):
 pa=unary_union(polys(shape(a['projection'])));ca=np.array(a['height_plane_abc'])
 for b in cells[i+1:]:
  pb=unary_union(polys(shape(b['projection'])));edge=pa.boundary.intersection(pb.boundary)
  if edge.length<=1e-8:continue
  cb=np.array(b['height_plane_abc'])
  for xy in coords(edge):
   z1,z2=float(ca@[*xy,1]),float(cb@[*xy,1]);gap=abs(z1-z2)
   if worst is None or gap>worst['height_difference_m']:worst=dict(first_source=a['source'],second_source=b['source'],xy=list(xy),height_values_m=[z1,z2],height_difference_m=gap,shared_projected_edge=mapping(edge))
d['low_shore_after']['maximum_projected_upper_envelope_step_witness']=worst
d['limits'].append('Projected upper-envelope step metrics include coast/water gaps where a vertical exterior edge joins distinct heights; they are not automatically cracks or3Dmeshdiscontinuities. Witness retained for actualvisualinterpretation.')
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=f'''33d限定结构增量通过，湾底实际重拓扑成立；低岸仍有陡面，几何通过不代表视觉完成。

正式源独立只读重开一次，12件闭合、体积为正，源未改写。实际GLB16804三角与本次重开源完全相同。用真实三角坐标集合比较33b与33d，未沿用删除后已变化的旧索引。原选168面投影并集6514.992579m²与设计patch完全一致；其中6张三角由新CDT重新生成了相同几何，不能宣称168张旧几何全消失。包括海岸邻面及岩脚改动后，旧差集179三角、新差集449三角。

对所有移除和新增实际三角检查完整九屋基础及922铺地真实域，面积交区和垂直线入侵均为0，最近距离2.011218m。其余实际几何保持，可以继承33b完整支承，未再全扫原占用区，也未重复GPU。源闭合及几何集合一致不证明全局三维自交不存在。

低岸采用正确Shapely bounds(-28,-7,-14,10)，即x[-28,-14]、y[-7,10]，面积238m²。全部12件原生资产最高上表面在其中覆盖237.912025m²，缺覆盖0.087975m²；水上表面229.571142m²，其中高程≤2m为119.389425m²，1.6m±1mm为66.717205m²。最高原生表面9.342149m，未形成全矩形1.6m平地。

水上最高表面按实际面坡度分区：0–15°为92.247734m²、15–30°为1.319867m²、30–45°为50.931825m²、超过45°为85.071716m²。矩形边界实际最高面的分段投影、高程范围和坡度保存在rectangle_boundary_surface_pieces中。举例，实际主壳三角16638、16642的边界坡度分别52.434°、55.365°，边界最高达到9.342149m。宽过渡面仍有陡边，不能只用新增面积或低点数量判断改善。

投影最高表面相邻区域检测的最大高度差11.600031m，见JSON的maximum_projected_upper_envelope_step_witness：来源{worst['first_source']}与{worst['second_source']}，局部XY{worst['xy']}，高度{worst['height_values_m']}。这类上表面投影跳变可发生于海岸垂直外缘和水下表面之间，并不自动等于网格裂缝或三维穿透；原生闭合门禁依然通过。记录供实际画面解释，不以该数值直接推断破面。

证据：round-33d-reopened-source.json及round-33d-rightcoast-independent-geometry.json。World原地形覆盖、可见水线、可达性和树重贴仍由root运行验证。父任务判断宽坡方向可保留，但扇形坡与低岸未达标；本报告full_reference_accepted=false、all_reference_goal_complete=false。
'''
(R/'reviews/round-33d-rightcoast-independent-geometry.md').write_text(md,encoding='utf-8')
print(worst)
