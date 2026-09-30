from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
import ast
module=ast.parse((R/'reviews/audit_25c_actual.py').read_text());func=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='core_rows');exec(compile(ast.Module(body=[func],type_ignores=[]),'independent-core-selection','exec'))
old,_=load(R/'captures/headland_study_23g/mainland_headland.glb');new,_=load(R/'captures/village_grading_study_25f/mainland_headland.glb');op,oh,ot,_=prepare(core_rows(old));np_,nh,nt,nr=prepare(core_rows(new));cache={}
def height(x):
    key=tuple(x)
    if key not in cache:
        point=Point(x);vv=[float(x@oh[i][:2]+oh[i][2]) for i in ot.query(point.buffer(.0001)) if op[i].distance(point)<.0001];assert vv,key;cache[key]=max(vv)
    return cache[key]
prior=json.loads((R/'reviews/round-25c-village-earthworks-independent-review.json').read_text());zones=[]
for case in prior['changed_surface_slope_scan']['steepest'][:4]:
    polygon=Polygon((np.array(case['actual_triangle_world_xyz'])-O)[:,[0,2]]);records=[]
    for i in nt.query(polygon):
        overlap=polygon.intersection(np_[i])
        if overlap.area>1e-8:records.append({'slope_degrees':math.degrees(math.atan(float(np.linalg.norm(nh[i][:2])))),'overlap_area_m2':overlap.area,'actual_triangle_world_xyz':(nr[i]['v']+O).tolist()})
    zones.append({'old_centroid_world_xz':case['world_xz_centroid'],'old25c_slope_degrees':case['slope_degrees'],'current_max_slope_degrees':max(r['slope_degrees'] for r in records),'intersecting_faces':len(records),'worst':max(records,key=lambda r:r['slope_degrees'])})
changed=[]
for i,row in enumerate(nr):
    v=row['v'];oldy=np.array([height(x) for x in v[:,[0,2]]]);delta=float(np.max(np.abs(oldy-v[:,1])))
    if delta<.001:continue
    priorplane=np.linalg.solve(np.column_stack([v[:,0],v[:,2],np.ones(3)]),oldy);limits=np.maximum(.8,np.abs(priorplane[:2])+.05);excess=float(np.max(np.abs(nh[i][:2])-limits));slope=float(np.linalg.norm(nh[i][:2]));minimum=min(float(np.linalg.norm(a-b)) for a,b in zip(v[:,[0,2]],np.roll(v[:,[0,2]],-1,axis=0)))
    changed.append({'component_limit_excess':excess,'actual_slope_degrees':math.degrees(math.atan(slope)),'prior_slope_degrees':math.degrees(math.atan(float(np.linalg.norm(priorplane[:2])))),'actual_gradient_components':nh[i][:2].tolist(),'old_gradient_components':priorplane[:2].tolist(),'limit_components':limits.tolist(),'projected_area_m2':np_[i].area,'shortest_projected_edge_m':minimum,'max_height_change_m':delta,'world_xz_centroid':(np.mean(v[:,[0,2]],axis=0)+O[[0,2]]).tolist()})
path=R/'reviews/round-25f-village-earthworks-independent-review.json';d=json.loads(path.read_text());d['old25c_counterexample_zones']=zones
d['actual_gradient_limit_review']={'scope':'Actual exported core triangles with >=1mm height change. Original gradient reconstructed at same actual XZ vertices. Limit per component max(.8, abs(original)+.05); records expose precision/collapse effects rather than trusting pre-export LP report.','changed_triangle_count':len(changed),'worst_all':sorted(changed,key=lambda x:x['component_limit_excess'],reverse=True)[:8],'worst_area_at_least_1e4_m2':sorted([r for r in changed if r['projected_area_m2']>=.0001],key=lambda x:x['component_limit_excess'],reverse=True)[:8],'max_current_angle_where_original_under45deg':max(r['actual_slope_degrees'] for r in changed if r['prior_slope_degrees']<45),'microtriangles_over70deg_with_original_under60deg':sum(r['actual_slope_degrees']>70 and r['prior_slope_degrees']<60 for r in changed)}
path.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps({'zones':zones,'gradient_summary':{k:v for k,v in d['actual_gradient_limit_review'].items() if k not in ['worst_all','worst_area_at_least_1e4_m2']},'worst_all':d['actual_gradient_limit_review']['worst_all'][:2],'worst_nontiny':d['actual_gradient_limit_review']['worst_area_at_least_1e4_m2'][:2]},indent=2))
