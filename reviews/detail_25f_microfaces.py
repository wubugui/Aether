from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
p=R/'reviews/round-25f-village-earthworks-independent-review.json';d=json.loads(p.read_text());rows,_=load(R/'captures/village_grading_study_25f/mainland_headland.glb');centers=np.array([r['v'][:,[0,2]].mean(axis=0) for r in rows]);paving=json.loads((R/'captures/village_paving_design_24m/paving.json').read_text());foot=shapely.union_all([shapely.from_geojson(g['footprint_geojson']) for g in paving['groups']])
for r in d['actual_gradient_limit_review']['worst_all']+d['actual_gradient_limit_review']['worst_area_at_least_1e4_m2']:
    xz=np.array(r['world_xz_centroid'])-O[[0,2]];i=int(np.argmin(np.linalg.norm(centers-xz,axis=1)));v=rows[i]['v'];assert np.linalg.norm(centers[i]-xz)<1e-5
    r['actual_world_xyz']=(v+O).tolist();r['height_range_m']=float(np.ptp(v[:,1]));r['longest_projected_edge_m']=max(float(np.linalg.norm(a-b)) for a,b in zip(v[:,[0,2]],np.roll(v[:,[0,2]],-1,axis=0)));r['centroid_inside_paving_footprint']=foot.covers(Point(r['world_xz_centroid']))
p.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps(d['actual_gradient_limit_review']['worst_all'][:2],indent=2))
