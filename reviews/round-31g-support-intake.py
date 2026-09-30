from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'decoder','exec'))
from shapely.ops import nearest_points
from shapely.strtree import STRtree
P=R/'captures/lantern_island_study_31f'
e=json.loads((P/'geometry-evidence.json').read_text());d=glb(P/'island_c.glb');tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths'
ob=e['new'][tn];v=np.array(ob['vertices']);faces=np.array(ob['polygons']);ts=v[faces];actual=d[next(k for k in d if 'olive grass' in k)];assert counter(ts)==counter(actual)
po=e['new'][pn];pv=np.array(po['vertices']);road=unary_union([Polygon(pv[f][:,:2]) for f in po['polygons'] if np.cross(pv[f][1]-pv[f][0],pv[f][2]-pv[f][0])[2]>1e-9]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']]);tree=json.loads((R/'reviews/round-31f-actual-tree-support.json').read_text());trunks=[Polygon(a['actual_trunk_footprint_xy']) for a in tree['checks']];treeunion=unary_union(trunks)
plan=json.loads((P/'reform-plan.json').read_text());centers=[(997,[.214399934,10.327761650,8.323335648]),(409,[-5.370585918,7.894711971,5.714765549]),(388,[-7.193421841,10.683920860,.900911212])]
near=[]
for label,pos in centers:
 ix=int(np.argmin(np.linalg.norm(v-np.array(pos),axis=1)));assert np.linalg.norm(v[ix]-pos)<1e-6
 p=Point(v[ix,:2]);row={'historical_anchor_label':label,'actual31f_vertex':ix,'actual_xyz':v[ix].tolist(),'boundary_distances':{},'nearby_tree_instances':[]}
 for name,mask in [('road',road),('pads',pads),('actual_trunks',treeunion)]:
  a,b=nearest_points(p,mask);row['boundary_distances'][name]={'distance_m':p.distance(mask),'nearest_xy':list(b.coords)[0]}
 for j in sorted(range(len(trunks)),key=lambda j:p.distance(trunks[j]))[:4]:
  a=tree['checks'][j];row['nearby_tree_instances'].append({'instance':j,'island':a['island'],'axis_xy':a['xy_blender'],'scale':a['scale'],'real_base_distance_m':p.distance(trunks[j]),'actual_footprint_xy':a['actual_trunk_footprint_xy'],'ground_height_range':a['new_base_surface_height_min_max_m']})
 near.append(row)
# Bounded diagnostic selection only: centroid inside this rear slope box. It is not a selected replacement patch.
c=ts.mean(axis=1);sel=np.flatnonzero((c[:,0]>-12)&(c[:,0]<5)&(c[:,1]>2)&(c[:,1]<16)&(c[:,2]>.2)&(c[:,2]<10.3))
Q=np.array([[1/np.sqrt(2),1/np.sqrt(2),0],[0,0,1],[-1/np.sqrt(2),1/np.sqrt(2),0]])
pt=ts[sel]@Q.T;polys=[Polygon(t[:,:2]) for t in pt];norm=np.cross(ts[sel,1]-ts[sel,0],ts[sel,2]-ts[sel,0]);ratio=np.array([p.area for p in polys])/(np.linalg.norm(norm,axis=1)/2);sgn=np.cross(pt[:,1,:2]-pt[:,0,:2],pt[:,2,:2]-pt[:,0,:2]);index=STRtree(polys);overlaps=[]
for i,p in enumerate(polys):
 if p.area<1e-10:continue
 for j in index.query(p):
  j=int(j)
  if j<=i or polys[j].area<1e-10:continue
  inter=p.intersection(polys[j])
  if inter.area<1e-6:continue
  q=inter.representative_point();uv=np.array([q.x,q.y,1]);co1=np.linalg.solve(np.column_stack([pt[i,:,:2],np.ones(3)]),pt[i,:,2]);co2=np.linalg.solve(np.column_stack([pt[j,:,:2],np.ones(3)]),pt[j,:,2]);gap=float(abs(uv@(co1-co2)));overlaps.append({'face_pair':[int(sel[i]),int(sel[j])],'overlap_uz_area_m2':inter.area,'sample_uz':[q.x,q.y],'sample_depth_separation_m':gap})
overlaps.sort(key=lambda a:a['overlap_uz_area_m2'],reverse=True)
fields={'road_and_pad':['expected_support_projection_area_m2','same_linear_height_coverage_m2','unpreserved_area_m2','higher_than_old_by_over_0_1mm_area_m2','all_intersecting_up_surface_height_delta_min_max_m'], 'each_actual_tree_base':['actual_trunk_footprint_xy','actual_tree_base.new_unsupported_area_m2','actual_tree_base.height_delta_min_max_m','actual_axis_ground','runtime_axis_ground_error_m','base_internal_height_jump_m','runtime_flat_tree_bottom_to_surface_gap_min_max_m','base_support_pass'], 'must_separate':['old_tree_disk_surface_preserved','actual_tree_base_support']}
report={'round':'31g','scope':'31f current support boundary intake and bounded rear-slope oblique-projection diagnostic; no31g candidate or repeat full31f support test.','input_sha256':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',R/'reviews/round-31f-actual-tree-support.json']},'actual_source_triangles_match_GLB':True,'road_projection_area_m2':road.area,'road_geometry_geojson':road.__geo_interface__,'pads':e['sites'],'actual_tree_base_source':'reviews/round-31f-actual-tree-support.json','all14_actual_tree_footprints_xy':[x['actual_trunk_footprint_xy'] for x in tree['checks']],'nearby_anchor_constraints':near,'reusable_exact_report_fields':fields,'projection_diagnostic':{'definition':'u=(x+y)/sqrt2; vertical=z; depth=(-x+y)/sqrt2','selection':'triangle centroid -12<x<5,2<y<16,.2<z<10.3; diagnostic only, not replacement patch','selected_face_count':len(sel),'selected_source_faces':sel.tolist(),'positive_projected_winding_count':int(sum(sgn>1e-10)),'negative_projected_winding_count':int(sum(sgn<-1e-10)),'projected_to_3D_area_ratio_min':float(min(ratio)),'near_edgeon_ratio_below0_05_faces':[int(sel[i]) for i in np.flatnonzero(ratio<.05)],'positive_area_projected_overlap_pairs':len(overlaps),'largest20_overlap_examples':overlaps[:20],'conclusion':'Do not assume this whole rear region is a single valued depth graph in(u,z). Positive-area overlaps at separated depths mean projected CDT requires an actually isolated patch/boundary check, not a whole-region flatten-and-lift.'},'candidate_checks_pending':['Deleted patch must be connected and report each oriented boundary loop; edges used once by patch require exact counterpart in kept shell.','Actual triangles removed/retained/new are compared against31f counters; old longitudinal chain interior must really disappear, not merely receive new vertices.','For chosen patch alone test signed projection Jacobians, projected boundary simplicity, internal overlap and multiple-depth boundary vertices before adopting this parameterization.','New support uses true trunk polygons and full upper envelope(main+17rocks), with old2m disk retained only as nearby-ground history.','Final actual shell closure/orientation/local triangle self-intersection and runtime views remain necessary.'],'full_reference_accepted':False}
(R/'reviews/round-31g-support-intake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
md='# 31g 真实支承与斜投影有界审查\n\n保留31f实际道路、两建筑pad和14棵真实六边形树干底域。旧2m树盘仅作旁地形变化记录，不作为重接冻结范围。JSON包含道路完整GeoJSON、pad多边形、14底域及可直接继承的验收字段；没有重跑31f完整支承。\n\n|历史锚点|实际31f点号|道路净距m|pad净距m|真实树干底域净距m|\n|---|---:|---:|---:|---:|\n'
for a in near:md+='|'+str(a['historical_anchor_label'])+'|'+str(a['actual31f_vertex'])+'|'+ '|'.join(f"{a['boundary_distances'][k]['distance_m']:.6f}" for k in ['road','pads','actual_trunks'])+'|\n'
md+='\n上述距离只描述当前点，不是允许移动半径。JSON列出最近边界实际XY和各近树实例多边形。C/D树世界yaw为0而岛D yaw为2，故两者局部底域旋转不同，不应用同一局部圆或多边形代替。\n\n对中央后坡诊断盒内'+str(len(sel))+'个实际面做(u,z)投影，有'+str(len(overlaps))+'对正面积投影重合；这不是3D自交结论。部分重合面有实际深度差，不能直接把整个盒内坡面当单值高度图。根选定准确面片后，需对该片单独检验投影边界简单性、绕向、折返及同(u,z)不同depth边界；若不满足，可缩小/分成少量面片，或直接3D重接。\n\n后续实际候选需报告：删面连通和有向边界环、保留壳对应边、旧内部纵向边链是否真实消失、原三角保留/删除及新增三角。支承用实际线性面与真实树干底域，不以点心或整旧2m盘替代；连续支承不等于水平干底全接触。31g几何与造型仍待实际产物。\n'
(R/'reviews/round-31g-support-intake.md').write_text(md,encoding='utf-8')
print(json.dumps({'nearby':[{k:a[k] for k in ['historical_anchor_label','actual31f_vertex','boundary_distances']} for a in near],'projection':{k:v for k,v in report['projection_diagnostic'].items() if k not in ['selected_source_faces','largest20_overlap_examples']},'overlap_examples':overlaps[:3]},indent=2))
