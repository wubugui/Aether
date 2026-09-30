from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
path=R/'reviews/round-25c-village-earthworks-independent-review.json';d=json.loads(path.read_text());new,_=load(R/'captures/village_grading_study_25c/mainland_headland.glb');old,_=load(R/'captures/headland_study_23g/mainland_headland.glb');op,oh,ot,orr=prepare(old)
paving=json.loads((R/'captures/village_paving_design_24m/paving.json').read_text());foot=shapely.union_all([shapely.from_geojson(g['footprint_geojson']) for g in paving['groups']])
for row in d['changed_surface_slope_scan']['steepest']:
    xz=np.array(row['world_xz_centroid'])-O[[0,2]];match=min(new,key=lambda r:np.linalg.norm(np.mean(r['v'][:,[0,2]],axis=0)-xz));assert np.linalg.norm(np.mean(match['v'][:,[0,2]],axis=0)-xz)<1e-5
    row['actual_triangle_world_xyz']=(match['v']+O).tolist();row['original_height_at_triangle_vertices']=[]
    for v in match['v']:
        p=Point(v[[0,2]]);heights=[float(v[[0,2]]@oh[i][:2]+oh[i][2]) for i in ot.query(p.buffer(.0001)) if op[i].distance(p)<.0001];row['original_height_at_triangle_vertices'].append(max(heights))
    row['centroid_distance_outside_paving_m']=foot.distance(Point(row['world_xz_centroid']));worldpoly=Polygon((match['v']+O)[:,[0,2]]);row['projected_area_outside_paving_m2']=worldpoly.difference(foot).area
gate=json.loads((R/'reviews/round-25c-village-grading-native-check.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();d['reopened_native_gate']={'passed':gate['passed'],'glb_matches':gate['glb_sha256']==d['identity']['new_glb_sha256'],'blend_matches':gate['source_sha256']==sha(R/'captures/village_grading_study_25c/mainland_headland.blend')}
run=R/'captures/validation_runs/village-paving-25c-20260908T140040Z-542f147b2e5043ea9e91bb591f0cb494';m=json.loads((run/'manifest.json').read_text());d['gpu_run']={'run_id':m['run_id'],'status':m['status'],'passed':m['passed'],'images':[]}
for image in sorted((run/'images').glob('*.png')):
    s=json.loads(image.with_suffix('.png.json').read_text());v=s['village_paving_study'];d['gpu_run']['images'].append({'name':image.name,'sha256':sha(image),'paving_passed':v['passed'],'failure_count':len(v['failures'])})
d['status']='REJECT as final earthworks geometry/art: new near-vertical exposed slope faces and visible radial creases despite no cap penetration and preserved body foundations/shoreline.'
d['visual_review']={'directly_viewed':['day-foreground.png','door-junction.png','night-reference.png'],'improvement':'Tall smooth roadbed sidewalls are substantially buried.','rejection':'Door-junction and foreground views reveal long dark radial creases and fan-like skinny triangular terrain faces, matching the independently measured steep surface risk. Night overview does not negate close-view defects.','full_reference_acceptance':False}
path.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps(d['changed_surface_slope_scan']['steepest'][:2],indent=2))
