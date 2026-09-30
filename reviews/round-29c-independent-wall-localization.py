from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
P=R/'captures/lantern_island_study_29b';e=json.loads((P/'geometry-evidence.json').read_text());t=e['new']['island_c grass and exposed rock terrain'];v=np.array(t['vertices']);nv=len(v)//2;frozen=set(e['protected_face_indices']);data=glb(P/'island_c.glb');terrain=data[next(k for k in data if 'olive grass' in k)];actual=counter(terrain)
road=unary_union([Polygon(p) for p in e['protection']['path_top_triangles']]);other=[Polygon(p) for p in e['protection']['pads']]+[Point(p).buffer(2) for p in e['protection']['trees']]
masks={'29b_road_buffer_1_2m':unary_union([road.buffer(1.2)]+other),'actual_road_footprint':unary_union([road]+other)}
selected=[]
for i,p in enumerate(t['polygons']):
    if max(p)>=nv:continue
    q=v[p];normal=np.cross(q[1]-q[0],q[2]-q[0]);norm=normal/np.linalg.norm(normal)
    if q[:,2].mean()<=10 or norm[2]>=.5:continue
    assert tri_key(q) in actual
    poly=Polygon(q[:,:2]);rec={'source_face_index':i,'source_vertex_indices':p,'xyz':q.tolist(),'center_z_m':float(q[:,2].mean()),'normal_z':float(norm[2]),'slope_deg':float(np.degrees(np.arccos(norm[2]))),'surface_area_m2':float(np.linalg.norm(normal)/2),'xy_area_m2':poly.area,'xy_bounds':list(poly.bounds),'frozen_as_whole_face_in_29b':i in frozen,'masks':{}}
    for name,mask in masks.items():
        inside=poly.intersection(mask);outside=poly.difference(mask)
        rec['masks'][name]={'inside_xy_area_m2':inside.area,'outside_xy_area_m2':outside.area,'outside_fraction':outside.area/poly.area,'intersects':poly.intersects(mask)}
    selected.append(rec)
union=unary_union([Polygon(np.array(r['xyz'])[:,:2]) for r in selected]);fr=[r for r in selected if r['frozen_as_whole_face_in_29b']]
summary={name:{'total_selected_inside_xy_area_m2':sum(r['masks'][name]['inside_xy_area_m2'] for r in selected),'total_selected_outside_xy_area_m2':sum(r['masks'][name]['outside_xy_area_m2'] for r in selected),'frozen_face_outside_xy_area_m2':sum(r['masks'][name]['outside_xy_area_m2'] for r in fr),'frozen_partially_intersecting_face_count':sum(r['masks'][name]['inside_xy_area_m2']>1e-10 and r['masks'][name]['outside_xy_area_m2']>1e-10 for r in fr),'frozen_face_entirely_outside_current_mask_count':sum(r['masks'][name]['inside_xy_area_m2']<=1e-10 for r in fr)} for name in masks}
examples=sorted(fr,key=lambda r:r['masks']['actual_road_footprint']['outside_xy_area_m2'],reverse=True)[:8]
report={'scope':'Actual29b GLB-matched source terrain top triangles with arithmetic center height>10m and upward normal z<0.5. This is a reproducible geometric selection, not all visible wall pixels or an instruction to alter protected geometry. Source indices refer to29b geometry-evidence terrain object.','glb_sha256':sha(P/'island_c.glb'),'selected_faces':len(selected),'whole_frozen_selected_faces':len(fr),'selected_surface_area_m2':sum(r['surface_area_m2'] for r in selected),'selected_xy_area_m2':union.area,'selected_xy_bounds':list(union.bounds),'selected_xy_region_wkt':union.wkt,'mask_summaries':summary,'highest_release_area_examples':examples,'all_faces':selected}
(R/'reviews/round-29c-independent-wall-localization.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['all_faces','selected_xy_region_wkt','highest_release_area_examples']},indent=2));print('EXAMPLES',[(r['source_face_index'],r['source_vertex_indices'],r['xy_area_m2'],r['masks']['actual_road_footprint']['outside_xy_area_m2']) for r in examples])
