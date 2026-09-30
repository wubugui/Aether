from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
from shapely.geometry import mapping
from shapely.strtree import STRtree
P=R/'captures/lantern_island_study_30c';ep=P/'geometry-evidence.json';e=json.loads(ep.read_text());plan=json.loads((P/'proportion-plan.json').read_text());prior=json.loads((R/'reviews/round-30c-independent-geometry.json').read_text());assert sha(ep)==prior['files'][str(ep.relative_to(R))]
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';objects=e['new'];main=objects[tn];mv=np.array(main['vertices']);names=['West broken shoulder','Southwest leaning crag','North broken ridge']
def triangles(ob):
 v=np.array(ob['vertices']);return [(i,v[f]) for i,f in enumerate(ob['polygons']) if len(f)==3]
def upper(ob):return [(i,t) for i,t in triangles(ob) if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-9]
def plane(t):return np.linalg.solve(np.c_[t[:,:2],np.ones(3)],t[:,2])
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for sub in getattr(g,'geoms',[]) for p in polygons(sub)]
def coords(g):return [xy for p in polygons(g) for xy in p.exterior.coords]
def halfplane(co):
 pts=[(-1000.,-1000.),(1000.,-1000.),(1000.,1000.),(-1000.,1000.)];out=[]
 for a,b in zip(pts,pts[1:]+pts[:1]):
  da=np.dot(co,[*a,1]);db=np.dot(co,[*b,1])
  if da>=0:out.append(a)
  if (da<0<db) or (db<0<da):out.append(tuple(np.array(a)+(np.array(b)-a)*da/(da-db)))
 return Polygon(out) if len(out)>=3 else Polygon()
road=unary_union([Polygon(t[:,:2]) for i,t in upper(objects[pn])]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']]);sidepath=R/'captures/validation_runs/lantern-island-30c-20260908T181715Z-31c81298860748f3ac9257c092e5f4b5/images/day-d-front.png.json';side=json.loads(sidepath.read_text());trees=[]
for p in side['placements']:
 if p.get('kind')!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
 origin=np.array([-3050,0,-2650]) if p['island']=='island_c' else np.array(plan['d_world_position']);yaw=0 if p['island']=='island_c' else plan['d_yaw'];d=np.array(p['position'])-origin;c,s=math.cos(yaw),math.sin(yaw);trees.append({'island':p['island'],'xy':[c*d[0]-s*d[2],-(s*d[0]+c*d[2])]})
tree_mask=unary_union([Point(p['xy']).buffer(2) for p in trees]);protect=unary_union([road,pads,tree_mask]);gt=upper(main);gp=[Polygon(t[:,:2]) for i,t in gt];gpl=[plane(t) for i,t in gt];idx=STRtree(gp);results=[]
for name in names:
 ob=objects[name];ov=np.array(ob['vertices']);roof=upper(ob);roofpoly=unary_union([Polygon(t[:,:2]) for i,t in roof]);free=roofpoly.difference(protect);rows=[];buried=[];gaps=[];heights=[];roofheights=[];waterburied=[];watergaps=[]
 waterroof=unary_union([Polygon(t[:,:2]).intersection(halfplane(plane(t)-[0,0,.5])) for i,t in roof]).difference(protect)
 for ri,rt in roof:
  rp=Polygon(rt[:,:2]);rc=plane(rt)
  for j in idx.query(rp):
   overlap=rp.intersection(gp[j]);allowed=overlap.difference(protect)
   if allowed.area<1e-8:continue
   diff=gpl[j]-rc;hidden=allowed.intersection(halfplane(diff))
   if hidden.area<1e-8:continue
   xy=coords(hidden);gg=[float(np.dot(diff,[*p,1])) for p in xy];zz=[float(np.dot(gpl[j],[*p,1])) for p in xy];rz=[float(np.dot(rc,[*p,1])) for p in xy];gaps.extend(gg);heights.extend(zz);roofheights.extend(rz);buried.append(hidden)
   wh=hidden.intersection(halfplane(rc-[0,0,.5]));waterburied.append(wh);watergaps.extend(float(np.dot(diff,[*p,1])) for p in coords(wh))
   rows.append({'main_face':gt[j][0],'main_vertex_indices':main['polygons'][gt[j][0]],'shoulder_roof_face':ri,'area_m2':hidden.area,'main_minus_shoulder_roof_min_max_m':[min(gg),max(gg)],'main_z_min_max_m':[min(zz),max(zz)],'shoulder_z_min_max_m':[min(rz),max(rz)],'allowed_buried_projection':mapping(hidden)})
 area=unary_union(buried);results.append({'name':name,'native_blender_bounds':{'min':ov.min(axis=0).tolist(),'max':ov.max(axis=0).tolist()},'roof_projection_area_m2':roofpoly.area,'protected_overlap_area_m2':roofpoly.intersection(protect).area,'free_roof_projection_area_m2':free.area,'main_over_roof_free_buried_projection_area_m2':area.area,'main_over_roof_free_fraction':area.area/free.area if free.area else None,'water_above_roof_z_ge_0_5m':{'free_projection_area_m2':waterroof.area,'buried_projection_area_m2':unary_union(waterburied).area,'buried_projection':mapping(unary_union(waterburied)),'main_minus_roof_min_max_m':[min(watergaps),max(watergaps)] if watergaps else None},'free_buried_bounds_xy':list(area.bounds),'free_buried_projection':mapping(area),'main_z_min_max_m':[min(heights),max(heights)] if heights else None,'shoulder_roof_z_min_max_m':[min(roofheights),max(roofheights)] if roofheights else None,'main_minus_shoulder_roof_min_max_m':[min(gaps),max(gaps)] if gaps else None,'main_face_indices':sorted({r['main_face'] for r in rows}),'clipped_surface_patches':rows,'minimum_roof_distance_m':{'road':roofpoly.distance(road),'pads':roofpoly.distance(pads),'tree_axis_disks':roofpoly.distance(tree_mask)}})
report={'round':'30d_intake','coordinate_system':'Blender local X/Y horizontal Z up, meters. C/D combined protection union for shared native island asset.','source_sha256':sha(ep),'baseline_glb_validation_inherited':'reviews/round-30c-independent-geometry.json','runtime_tree_source':str(sidepath.relative_to(R)),'runtime_tree_source_sha256':sha(sidepath),'method':'Only three native shoulder upper-triangle projections versus current welded shell upward triangles, clipped by actual path footprint, padded site polygons, and current C/D tree axes radius2m. Positive linear plane difference identifies locally buried shoulder roofs. No global coverage or GPU rerun.','protection_areas_m2':{'road':road.area,'pads':pads.area,'tree_disks_union':tree_mask.area},'tree_axes':trees,'regions':results,'limits':['Allowed means outside specified support projection only, not blanket collision-free construction authorization.','Min gap approaches zero at exposure boundary; range describes full clipped polygon vertices, not mean depth.','Roof projection differs from exposed 3D surface area and does not guarantee useful silhouette.','Cut only clipped free patch; faces touching supports must be split, not moved wholesale.','Do not lower whole covered region to roof minus a constant; select staggered short cuts and retain a joined exterior.']}
(R/'reviews/round-30d-cutback-intake.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
lines=['# 30d 局部削坡独立定位','','基于已核验 SHA 的30c原生几何与本版实际GPU侧车树轴，只计算West/Southwest/North三处；未重跑全场覆盖或启动GPU。所有坐标为Blender局部米，XY水平/Z向上。保护取实际道路顶面投影、已有扩张基础polygon、C与D实际树轴2m盘的并集。','']
for r in results:
 lines += ['## '+r['name'],'',f"岩肩XY范围 {r['native_blender_bounds']['min'][:2]} → {r['native_blender_bounds']['max'][:2]}。顶面投影 {r['roof_projection_area_m2']:.3f}m²；保护投影相交 {r['protected_overlap_area_m2']:.6f}m²；保护外被主实体覆盖的顶面投影 {r['main_over_roof_free_buried_projection_area_m2']:.3f}m²，占可用顶面投影 {100*r['main_over_roof_free_fraction']:.2f}%。",f"覆盖区域主坡Z {r['main_z_min_max_m']}，肩顶Z {r['shoulder_roof_z_min_max_m']}，主坡比肩顶高 {r['main_minus_shoulder_roof_min_max_m']}m。最小值可在露出边界接近0，不是平均削深。",f"主实体源面：{r['main_face_indices']}。完整裁切多边形、逐片顶点索引和高差见JSON。",'']
lines += ['## 水上可见部分与边界风险','']
for r in results:
 w=r['water_above_roof_z_ge_0_5m'];lines += [f"{r['name']}：仅取肩顶 Z≥0.5m，保护外投影 {w['free_projection_area_m2']:.3f}m²，被主坡覆盖 {w['buried_projection_area_m2']:.3f}m²；对应主坡高于肩顶 {w['main_minus_roof_min_max_m']}m。"]
lines += ['West 肩顶投影距扩张基础只有0.021262m；虽无相交，邻接面的共享顶点仍可能支承基础，应切分保护边界。上述全屋顶统计包含低至-3.25m的朝上斜面，不能用最大值当一般削深；应优先参考水上子区。','建议从上述保护外覆盖区选短段削开包裹坡面，保留部分岩肩埋合并形成可见转折。面片碰到保护边界时必须按边界切分，不应把整面或共享顶点直接降低。保留17岩块位置尺寸，在实体中形成非环状、长短高低错位的连接；此处不建议将所有覆盖面积都压到统一的肩顶以下。','', '这些是指定支承范围外的候选投影与线性高差，不是完整建模许可或3D自交证明。真正曝光面积、侧面闭合和支承高度仍需下一实际GLB检查；最终轮廓必须由实际GPU原图判断。']
(R/'reviews/round-30d-cutback-intake.md').write_text('\n\n'.join(lines),encoding='utf-8');print(json.dumps([{'name':r['name'],'water_above':{k:v for k,v in r['water_above_roof_z_ge_0_5m'].items() if k!='buried_projection'}} for r in results],indent=2))
