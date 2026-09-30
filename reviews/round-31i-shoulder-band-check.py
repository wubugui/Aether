from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'decoder','exec'))
from shapely.geometry import LineString
P=R/'captures/lantern_island_study_31i';e=json.loads((P/'geometry-evidence.json').read_text());plan=json.loads((P/'reform-plan.json').read_text());tn='island_c grass and exposed rock terrain';v=np.array(e['new'][tn]['vertices']);faces=e['new'][tn]['polygons'];oldv=np.array(e['old'][tn]['vertices']);actual=counter(np.concatenate(list(glb(P/'island_c.glb').values())));changed={a['index']:np.array(a['after']) for a in plan['actual_moved_vertices']};ed=collections.defaultdict(list)
for fi,ids in enumerate(faces):
 for a,b in zip(ids,ids[1:]+ids[:1]):ed[tuple(sorted([a,b]))].append(fi)
def locate(x):
 dist=np.linalg.norm(v-np.array(x),axis=1);idx=np.flatnonzero(dist<1e-5);assert len(idx)==1;return int(idx[0])
def info(fi):
 t=v[faces[fi]];n=np.cross(t[1]-t[0],t[2]-t[0]);area=np.linalg.norm(n)/2;n/=np.linalg.norm(n);assert tri_key(t) in actual;return {'face':fi,'vertices':faces[fi],'xyz':t.tolist(),'area_m2':float(area),'normal':n.tolist(),'slope_from_horizontal_deg':math.degrees(math.acos(np.clip(n[2],-1,1)))}
rows=[]
for band in plan['bands']:
 splitids=[];segments=[]
 common=set(band['edge_splits'][0]['edge'])&set(band['edge_splits'][1]['edge']);assert len(common)==1;apex=common.pop();high=[a for a in band['face_vertices'] if a!=apex]
 endpoints={a:locate(changed.get(a,oldv[a])) for a in band['face_vertices']}
 for step in band['edge_splits']:
  k=locate(step['xyz']);splitids.append(k);a,b=[endpoints[x] for x in step['edge']]
  pieces=[]
  for pair in [[a,k],[k,b]]:
   inc=ed[tuple(sorted(pair))];assert len(inc)==2;pieces.append({'edge_vertices':pair,'incident_faces':inc})
  segments.append({'old_source_edge':step['edge'],'new_unique_vertex':k,'actual_xyz':v[k].tolist(),'old_endpoint_edge_retained_as_diagonal':tuple(sorted([a,b])) in ed,'old_endpoint_edge_incident_faces':ed.get(tuple(sorted([a,b])),[]),'two_shared_segments':pieces})
 back=[endpoints[x] for x in high];capset=set(back+splitids);capids=[fi for fi,ids in enumerate(faces) if set(ids)<=capset];assert len(capids)==2;cap=[info(fi) for fi in capids];frontids=ed[tuple(sorted(splitids))];assert len(frontids)==2;front=[info(fi) for fi in frontids];assert len(set(frontids)&set(capids))==1
 angle=math.degrees(math.acos(np.clip(np.dot(front[0]['normal'],front[1]['normal']),-1,1)));capangle=math.degrees(math.acos(np.clip(np.dot(cap[0]['normal'],cap[1]['normal']),-1,1)));frontv=v[splitids];backv=v[back];width=LineString(frontv[:,:2]).distance(LineString(backv[:,:2]));assert width>0
 rows.append({'band':band['name'],'old_source_face_vertices':band['face_vertices'],'shared_split_segments':segments,'back_edge_vertices':back,'back_edge_xyz':backv.tolist(),'front_edge_vertices':splitids,'front_edge_xyz':frontv.tolist(),'front_edge_length3d_m':float(np.linalg.norm(frontv[1]-frontv[0])),'back_edge_length3d_m':float(np.linalg.norm(backv[1]-backv[0])),'front_to_back_minimum_XY_segment_distance_m':width,'shoulder_cap_actual_triangles':cap,'cap_surface_area_m2':sum(a['area_m2'] for a in cap),'cap_internal_dihedral_angle_deg':capangle,'front_edge_actual_incident_triangles':front,'front_crease_normal_angle_deg':angle,'finite_width_and_shared_faces_pass':True})
r={'round':'31i','scope':'Actual native and GLB shelf-cap triangles, shared split vertices and finite band width. Distances are finite XY segment measurements; normal angles use actual final BEAUTY triangles.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',P/'reform-plan.json']},'bands':rows,'pass':all(x['finite_width_and_shared_faces_pass'] for x in rows),'full_reference_accepted':False,'limits':['Geometric width/crease is not a visual short-shoulder acceptance score.','Cap triangles may be noncoplanar; actual internal diagonal and its normal change reported instead of ideal quad plane.','This bounded check does not rerun prior31i complete support/intersection checks.']}
(R/'reviews/round-31i-shoulder-band-check.json').write_text(json.dumps(r,indent=2),encoding='utf-8');p=R/'reviews/round-31i-independent-geometry.json';g=json.loads(p.read_text());g['shoulder_shared_edge_check_pending']=False;g['shoulder_band_report']='reviews/round-31i-shoulder-band-check.json';g['actual_tree_base_report']='reviews/round-31i-actual-tree-support.json';g['limits'][0]='Actual14tree upper-envelope and shelf shared-edge/width/crease supplements completed. Runtime instance grounding separately checked by root.';g['pass']=g['base_geometry_and_support_pass'] and g['local_triangle_intersections']['local_self_intersection_pass'] and r['pass'];p.write_text(json.dumps(g,indent=2),encoding='utf-8');print(json.dumps({'bands':[{k:x[k] for k in ['band','front_edge_length3d_m','back_edge_length3d_m','front_to_back_minimum_XY_segment_distance_m','cap_surface_area_m2','cap_internal_dihedral_angle_deg','front_crease_normal_angle_deg']} for x in rows],'combined_geometry_pass':g['pass']},indent=2))
md='# 31i 实际GLB几何与肩带核验\n\n本版有界几何通过，造型待五原图。主壳2228三角/1116点，有向闭合单连通；5个原控制点移动及4个共享边新点均在实际GLB中确认，路径和17岩保持。道路与pad线性支承保持，按31h冻结实例实际干底重算31i主壳+17岩最高面，14棵连续覆盖且旧面不变。\n\n|肩带|前缘长m|后缘长m|前后缘最小XY净宽m|实际肩顶面积m²|肩顶内部折角°|前缘折角°|\n|---|---:|---:|---:|---:|---:|---:|\n'
for x in rows:md+='|'+x['band']+'|'+ '|'.join(f'{x[k]:.6f}' for k in ['front_edge_length3d_m','back_edge_length3d_m','front_to_back_minimum_XY_segment_distance_m','cap_surface_area_m2','cap_internal_dihedral_angle_deg','front_crease_normal_angle_deg'])+'|\n'
md+='\n4条切分边均形成两个共点小边，每个小边都有两个实际邻面。BEAUTY可能将旧端点连线重新用作相邻quad内部对角线，报告列出其实际邻面；不能把这种合法内对角线误判为未切边或T形接缝。两个新肩前缘各由实际肩顶三角与前断面三角共享。BEAUTY导出的两肩顶均为实际2三角，内部对角线和折角已记录，不把非平面quad理想化。\n\n60个改变/新切分三角对整壳1053候选对未发现共享特征0.1mm容差外的离散相交；未重跑未变/未变基线对。没有使用旧637边删除检查或同拓扑法线倒推代替本次验证。\n\n真实肩宽和折角不代表参考形体已达到；连续树干支承也不等于平底与斜面处处贴合。`full_reference_accepted=false`。\n';(R/'reviews/round-31i-independent-geometry.md').write_text(md,encoding='utf-8')

