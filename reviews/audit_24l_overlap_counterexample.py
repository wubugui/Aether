from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
d=json.loads((R/'captures/village_paving_design_24j/paving.json').read_text());solids=d['groups'][0]['solids']
names=['foreground worn stair paver 10.500 -3185 -2823 component 0','foreground worn stair paver 10.650 -3185 -2823 component 0']
ss=[next(s for s in solids if s['name']==n) for n in names]
polys=[shapely.union_all([Polygon([s['vertices_xz'][i] for i in t]) for t in s['cap_triangles']]) for s in ss]
p=Point(-2257.72192382813,-1750.06359863281)
actual,sha=load(R/'captures/village_paving_study_24j/village_foreground.glb');hits=[]
for row in actual:
    v=row['v'];poly=Polygon(v[:,[0,2]]);lp=Point(p.x-O[0],p.y-O[2])
    if poly.area<1e-12 or not poly.covers(lp):continue
    plane=np.linalg.solve(np.column_stack([v[:,0],v[:,2],np.ones(3)]),v[:,1]);y=plane[0]*lp.x+plane[1]*lp.y+plane[2]
    if y>10.4:hits.append({'y':y,'material':row['material'],'normal_y':float(np.cross(v[1]-v[0],v[2]-v[0])[1]),'triangle_world_xyz':(v+O).tolist()})
out={'xz':list(p.coords)[0],'design_names':names,'design_height':[s['top_y'] for s in ss],'design_overlap_area_m2':polys[0].intersection(polys[1]).area,'design_overlap_bounds':polys[0].intersection(polys[1]).bounds,'point_distance_to_both_boundaries_m':[pp.boundary.distance(p) for pp in polys],'actual_glb_sha256':sha,'actual_faces_above10_4':hits,'verdict':'Design and actual exported GLB both contain upper 10.65m paver above lower 10.5m paver; runtime upper hit is supported by actual artifact geometry.'}
(R/'reviews/round-24l-independent-paving-overlap-counterexample.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
