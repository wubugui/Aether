from pathlib import Path
import json,math,struct,hashlib
from collections import defaultdict,Counter
import numpy as np
from shapely.geometry import Polygon,Point,mapping
from shapely.ops import unary_union
from shapely.affinity import affine_transform
R=Path(__file__).resolve().parents[1]
RUN=R/'captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2';S=RUN/'study-inputs';O=np.array([-2180.,0.,-1830.])
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
decoder=(R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8').replace('def asset_world_triangles(path):','def decoded_rows(path):').replace('tris.extend(x[ix])',"tris.extend((t,doc.get('materials',[{}])[prim.get('material',0)].get('name',''),node.get('name','')) for t in x[ix])").replace('return np.array(tris)','return tris')
exec(decoder)
intake=read(R/'reviews/round-33-rightcoast-intake.json');native=read(R/'captures/rightcoast33-native-intake.json');layout=read(S/'headland/layout.json');paving=read(S/'village-paving/paving-design.json');runtime=read(RUN/'images/night-reference.png.json')['headland_study'];bindings={}
def bind(p):bindings[str(p.relative_to(R))]=sha(p)
for p in [R/'captures/rightcoast33-native-intake.json',R/'reviews/round-33-rightcoast-intake.json',S/'headland/layout.json',S/'village-paving/paving-design.json',RUN/'images/night-reference.png.json']:bind(p)
assert sha(R/native['source'])==native['source_sha256']==intake['native_source_sha256']
assert sha(R/'captures/rightcoast33-native-intake.json')==intake['native_intake_sha256']
assert layout['houses']==intake['houses'];assert np.array_equal(layout['origin'],O)
def world_to_local(p):return [p[0]-O[0],-(p[2]-O[2]),p[1]-O[1]]
def transform_geometry(poly,yaw,xy):
 c,s=math.cos(yaw),math.sin(yaw)
 return affine_transform(poly,[c,-s,s,c,*xy])
assets={};houses=[]
for asset in sorted(set(h['asset'] for h in layout['houses'])):
 path=S/('keeper_house.glb' if asset=='keeper_house' else 'headland/'+asset+'.glb');bind(path);rows=decoded_rows(path)
 foundation=[t for t,mat,node in rows if mat=='Keeper sandstone foundations' and np.max(t[:,2])<=.181]
 assert foundation
 pp=[Polygon(t[:,:2]) for t in foundation if Polygon(t[:,:2]).area>1e-12]
 poly=unary_union(pp)
 assets[asset]=dict(poly=poly,sha=sha(path),triangle_count=len(foundation),height_range=[float(np.min([t[:,2].min() for t in foundation])),float(np.max([t[:,2].max() for t in foundation]))])
for i,h in enumerate(layout['houses']):
 rec=runtime['assets'][i+1];assert rec['asset']==h['asset'];assert rec['sha256']==assets[h['asset']]['sha'];assert np.linalg.norm(np.array(rec['position'])-h['position'])<1e-5;assert abs(rec['yaw']-h['yaw'])<1e-9
 center=world_to_local(rec['position']);asset=assets[h['asset']];poly=transform_geometry(asset['poly'],h['yaw'],center[:2]);hx,hy=h['pad_half_size'];pad=transform_geometry(Polygon([(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]),h['yaw'],center[:2]);outside=poly.difference(pad)
 houses.append(dict(name=h['name'],asset=h['asset'],asset_sha256=asset['sha'],actual_runtime_node=rec['node'],world_godot_position=rec['position'],local_blender_position=center,yaw_blender_radians=h['yaw'],scale=1,actual_foundation_triangle_count=asset['triangle_count'],foundation_selection='Actual transformed asset faces material Keeper sandstone foundations with every vertex localZ<=0.181m; whole projection includes the forward doorstep. Matches26b independent base method; not a convex hull.',asset_foundation_height_range_m=asset['height_range'],actual_foundation_projection=mapping(poly),actual_foundation_area_m2=poly.area,layout_pad_half_size=h['pad_half_size'],layout_pad_projection=mapping(pad),layout_pad_area_m2=pad.area,actual_foundation_outside_layout_pad=mapping(outside),actual_foundation_outside_layout_pad_area_m2=outside.area,layout_pad_is_design_buffer_not_actual_bottom=True))
pavegroups=[];allactual=[];solidrows=[]
for group in paving['groups']:
 path=S/'village-paving'/('village_'+group['name']+'.glb');bind(path);parts=defaultdict(list);vertexowners=defaultdict(set)
 for item in group['solids']:
  xy=(np.array(item['vertices_xz'])-np.array(group['origin'])[[0,2]])*np.array([1,-1])
  for heights in [item['bottom_heights'],item['top_heights']]:
   for v in np.column_stack([xy,heights]).astype(np.float32).astype(float):vertexowners[tuple(v)].add(item['name'])
 unmatched=[];ambiguous=[];nodes=set()
 for ti,(t,mat,node) in enumerate(decoded_rows(path)):
  nodes.add(node);owners=set.intersection(*(vertexowners[tuple(v)] for v in t))
  if not owners:unmatched.append(ti);continue
  if len(owners)>1:ambiguous.append(dict(triangle=ti,owners=sorted(owners),projected_area_m2=Polygon(t[:,:2]).area))
  for owner in owners:
   if Polygon(t[:,:2]).area>1e-12:parts[owner].append(t)
 assert not unmatched,('unmatched_actual_triangles',group['name'],len(unmatched),unmatched[:5])
 assert all(a['projected_area_m2']<1e-12 for a in ambiguous),('ambiguous_nonzero_projection_actual_triangles',group['name'],ambiguous[:5])
 assert len(parts)==len(group['solids']),(group['name'],len(parts),len(group['solids']))
 actualpolys={name:unary_union([Polygon(t[:,:2]) for t in ts]) for name,ts in parts.items()}
 origin=group['origin'];shift=np.array([origin[0]-O[0],-(origin[2]-O[2])]);assert np.linalg.norm(shift)<1e-9
 designmap={p['name']:p for p in group['solids']};missing=set(actualpolys)-set(designmap);assert not missing,list(missing)[:3]
 diffs=[];polys=[]
 for name,poly in actualpolys.items():
  item=designmap[name];xy=np.array(item['vertices_xz']);xy=(xy-O[[0,2]])*np.array([1,-1]);designpoly=unary_union([Polygon(xy[f]) for f in item['cap_triangles']]);delta=poly.symmetric_difference(designpoly).area;diffs.append(delta);polys.append(poly);allactual.append(poly)
  solidrows.append(dict(group=group['name'],name=name,kind=item['kind'],actual_glb_projection=mapping(poly),actual_projected_area_m2=poly.area,design_projection_difference_area_m2=delta,actual_glb_z_min_max_m=[float(np.min([t[:,2].min() for t in parts[name]])),float(np.max([t[:,2].max() for t in parts[name]]))],planned_top_height_min_max_m=[min(item['top_heights']),max(item['top_heights'])],planned_bottom_height_min_max_m=[min(item['bottom_heights']),max(item['bottom_heights'])]))
 union=unary_union(polys);pavegroups.append(dict(name=group['name'],actual_glb_sha256=sha(path),solid_count=len(parts),export_merged_node_count=len(nodes),actual_triangle_assignment='ActualGLB triangles assigned by exact float32 authoring vertexXYZ membership; all3 vertices share a unique designed solid owner for every nonzero-XY-area triangle; shared vertical zero-projection triangles are separately reported.',unmatched_actual_triangles=unmatched,ambiguous_actual_triangles=ambiguous,kind_counts=dict(Counter(p['kind'] for p in group['solids'])),actual_union_projection=mapping(union),actual_union_area_m2=union.area,largest_solid_design_vs_export_symmetric_difference_area_m2=max(diffs),sum_solid_design_vs_export_symmetric_difference_area_m2=sum(diffs)))
trees=[]
for t in runtime['trees']:
 trees.append(dict(node=t['node'],world_godot_position=t['position'],local_blender_position=world_to_local(t['position']),scale=t['scale'],ground_collider=t['ground_collider'],geometry_role='Actual runtime tree root axis point. No2m disk or canopy footprint implied.',may_reproject_to_new_highest_ground=True))
views=[]
for view in ['night-reference','day-reference','day-a-front','day-a-back','day-a-approach']:
 p=RUN/'images'/f'{view}.png.json';bind(p);rr=read(p)['headland_study']['trees'];views.append(dict(view=view,actual_tree_count=len(rr),tree_records_exactly_match_night=rr==runtime['trees']))
assert all(v['tree_records_exactly_match_night'] for v in views)
houseunion=unary_union([assets[h['asset']]['poly'] if False else transform_geometry(assets[h['asset']]['poly'],h['yaw'],world_to_local(h['position'])[:2]) for h in layout['houses']]);paveunion=unary_union(allactual);occupied=unary_union([houseunion,paveunion])
result=dict(scope='Round33 bounded occupied-region extraction from32f frozen actual GLBs, existing native intake, layout and actual runtime records. No new Blender reopen, GPU or world scan.',coordinate_system=dict(units='meters',space='Blender headland local XYZ',origin_world_godot=O.tolist(),world_to_local='Blender(x,y,z)=(GodotX+2180,-(GodotZ+1830),GodotY); XY GeoJSON is local horizontal plane; Godot yaw around+Y maps to Blender yaw around+Z.',coast_native_source=native['source'],coast_native_source_sha256=native['source_sha256']),basis_runtime=RUN.name,bindings=bindings,houses=houses,house_actual_foundation_union=mapping(houseunion),house_actual_foundation_union_area_m2=houseunion.area,paving=dict(actual_solid_count=len(solidrows),groups=pavegroups,solids=solidrows,actual_union_projection=mapping(paveunion),actual_union_area_m2=paveunion.area,role='Complete actual GLB XY projections of all922solids including paver caps and buried bedding; not all922are individual surface pavers. No dilation applied.'),hard_occupied_house_and_paving_union=mapping(occupied),hard_occupied_union_area_m2=occupied.area,trees=trees,tree_runtime_view_consistency=views,other_runtime_scatter=dict(records=runtime['scatter_changes'],limitation='These runtime adjustments give mesh instance index and vertical changes only, without fullXYZ. They are not included as invented tree axes. Named28headland pines are not an exhaustive census of existing procedural world vegetation.'),conservative_buffers=dict(applied_to_actual_union_m=0,tree_disk_applied=False,layout_pads='Only existing per-house design rectangles, recorded separately; any12–28m deformation fade is a new design choice and not actual occupied ground.'),limits=['This report extracts regions, not a new full surface support or self-intersection acceptance.','Actual foundation selected by complete low sandstone foundation geometry, including doorstep, following verified26b method; roof/eaves and decorative facade projections are excluded.','Preserving every triangle that only touches a region also freezes its other vertices outside; this is stricter than these true projected masks and is a modeling choice, not a user constraint.','922solid projections are decoded actual GLB; small float32 differences from world-coordinate design polygons are explicitly reported.','Tree roots can be resited or regrounded under the goal. Actual root points do not imply whole trunk-base support or fixed2m disks.'],full_reference_accepted=False)
assert len(houses)==9 and len(solidrows)==922
(R/'reviews/round-33-occupied-regions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
outside=[(h['name'],h['actual_foundation_outside_layout_pad_area_m2']) for h in houses]
md=f'''右岸33占用域已从32f冻结实际资产与运行记录提取，未启动Blender或GPU，也未修改任何源模型。

所有GeoJSON都是岸体Blender局部XY，原点为Godot(-2180,0,-1830)。转换为：局部(x,y,z)=(世界X+2180,-(世界Z+1830),世界Y)。平面方向反转不能遗漏；Godot yaw与此Blender局部绕Z角数值一致。

九屋基础从实际冻结GLB中完整低位砂岩基础三角面投影并集获得，包括前门阶梯，沿用26b独立验证的真实基础选择规则；不是屋顶凸包或仅主屋矩形。每屋均给实际基础GeoJSON、实际运行位置、设计pad GeoJSON以及实际基础超pad差集。九屋基础总并集面积{houseunion.area:.6f}m²；逐屋超pad面积为{outside}。设计pad只是额外设计范围，不可替代真实基础。

两组铺地实际解码为{len(solidrows)}独立实体（前景469、海湾453），分别包含路面及埋入式基础。每件完整XY投影、分组并集和总并集均保存为GeoJSON；总并集面积{paveunion.area:.6f}m²。导出按材质合并为每组5节点；以实际三角的三个float32 XYZ点归属恢复922原生实体域，非零投影三角均唯一归属，每组另有4片共用垂直零投影三角，不影响XY域。实际GLB投影与设计cap投影的微小float32差异单列，保护用实际GLB域。九屋与铺地合并真实占用面积{occupied.area:.6f}m²，没有自动膨胀。

32f五个实际视图的headland_study.trees均记录{len(trees)}棵已实例化命名松树，节点、实际XYZ、scale和collider完全一致；这次28棵数量来自实际记录，不是直接采用28个计划点。每棵保存局部XYZ，允许在新地形上重贴。未添加2m硬保护盘。原世界散布植被调整日志另存，因仅含实例index/高度缺少XY，不能冒充完整世界树根普查；因此命名松树清单不是全部程序化植被的完整清单。

本报告只提供几何占用输入。父任务计划的12–28m渐变或冻结所有相交原生面顶点，会扩大实际冻结范围，应作为本轮设计策略单独记录；不把仅一角碰到占用域的整面都解释为真实被建筑占用。完整新地坪支承、受影响树重贴及视觉效果待33候选本版检查。
'''
(R/'reviews/round-33-occupied-regions.md').write_text(md,encoding='utf-8')
print(json.dumps(dict(houses=9,outside_pad=outside,paving_solids=len(solidrows),paving_area=paveunion.area,trees=len(trees),groups=[{k:v for k,v in g.items() if k!='actual_union_projection'} for g in pavegroups]),indent=2))
