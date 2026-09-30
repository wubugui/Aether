"""Solve the actual terrain surface with bounded face gradients and cap envelopes.

All original-edge constraints are retained. The optimization acts on real final
mesh heights, so skinny triangles cannot amplify an analytic sampled field.
"""
from pathlib import Path
exec(Path(__file__).resolve().parents[1].joinpath('reviews/audit_24l_actual.py').read_text().split('old,oldsha=')[0])
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
label='25d';folder=R/'captures'/('village_grading_design_'+label)
path=folder/'grading.json';d=json.loads(path.read_text());assert 'resolved_heights' not in d
rows,sha=load(R/'captures/headland_study_23g/mainland_headland.glb');assert sha==d['source_headland_glb_sha256']
op,oh,ot,orr=prepare(rows);xy=np.array(d['vertices_xz_local']);n=len(xy)
def old_height(x):
    p=Point(x);indices=ot.query(p.buffer(.0001));candidates=[]
    for i in indices:
        if op[i].distance(p)<.0001:candidates.append(float(x@oh[i][:2]+oh[i][2]))
    assert candidates,('Original height unavailable',x)
    return max(candidates)
old=np.array([old_height(x) for x in xy]);upper=old.copy();fixed=np.ones(n,dtype=bool)
for i,cs in enumerate(d['grading_constraints']):
    if cs and max(w for h,w in cs)>1e-8:
        upper[i]=min(old[i]+w*(h-old[i]) for h,w in cs);fixed[i]=False
ri=[];ci=[];vv=[];rhs=[];objective=np.zeros(n);slope_rows=0;cap_rows=0
def constraint(ids,coeff,value):
    idx=len(rhs)
    ri.extend([idx]*len(ids));ci.extend(ids);vv.extend(coeff);rhs.append(value)
# Native float coordinates make microscopic planar discrepancies. Retain a
# 0.1% allowance for pre-existing slopes, rather than demanding they be flattened.
for ids in d['triangles']:
    pts=xy[ids];e=pts[1:]-pts[0];det=np.linalg.det(e);area=abs(det)*.5
    assert area>1e-12
    objective[ids]+=area/3
    if all(fixed[i] for i in ids):continue
    inv=np.linalg.inv(e);grad=np.column_stack([-inv.sum(axis=1),inv]);prior=grad@old[ids]
    for axis in range(2):
        limit=max(.75,abs(float(prior[axis]))+.001)
        constraint(ids,grad[axis],limit);constraint(ids,-grad[axis],limit);slope_rows+=2
print('Gradient rows',slope_rows,'vertices',n,'free',int((~fixed).sum()),flush=True)
# Use exact planar intersections with all actual authored bedding bands. Every
# vertex of each intersection is constrained; the resulting linear faces stay
# below the cap across their entire overlap, not just at terrain vertices.
paving=json.loads((R/'captures/village_paving_design_24m/paving.json').read_text());bands=[]
for g in paving['groups']:
    for row in g['grading_bands']:
        poly=shapely.transform(shapely.from_geojson(row['geojson']),lambda a:a-O[[0,2]])
        bands.append((row['height'],poly))
bt=shapely.STRtree([p for h,p in bands])
for ids in d['triangles']:
    pts=xy[ids];poly=Polygon(pts);inv=np.linalg.inv((pts[1:]-pts[0]).T)
    for bi in bt.query(poly):
        y,b=bands[bi];inter=poly.intersection(b)
        if inter.area<1e-10:continue
        for point in vertices(inter):
            uv=inv@(np.array(point)-pts[0]);coeff=np.array([1-uv.sum(),uv[0],uv[1]])
            if all(fixed[i] for i in ids):
                assert coeff@old[ids]<=y-.06+.001,('Fixed terrain crosses cap',point,y,float(coeff@old[ids]))
                continue
            constraint(ids,coeff,y-.06);cap_rows+=1
print('Cap rows',cap_rows,'total',len(rhs),flush=True)
bounds=[(float(old[i]),float(old[i])) if fixed[i] else (max(-8.,float(old[i]-6)),float(upper[i])) for i in range(n)]
a=coo_matrix((vv,(ri,ci)),shape=(len(rhs),n)).tocsr()
if '--diagnose' in __import__('sys').argv:
    from scipy.sparse import hstack
    no_slope=linprog(-objective,A_ub=a[slope_rows:],b_ub=np.array(rhs)[slope_rows:],bounds=bounds,method='highs')
    print('Without slope constraints:',no_slope.message,flush=True)
    relaxed=hstack([a,coo_matrix(([-1.]*slope_rows,(range(slope_rows),[0]*slope_rows)),shape=(len(rhs),1))]).tocsr()
    res=linprog(np.r_[np.zeros(n),1.],A_ub=relaxed,b_ub=np.array(rhs),bounds=bounds+[(0,None)],method='highs')
    print('Uniform slope slack:',res.message,float(res.x[-1]) if res.success else None,flush=True)
    if res.success:
        records=[]
        for ids in d['triangles']:
            pts=xy[ids];inv=np.linalg.inv(pts[1:]-pts[0]);grad=np.column_stack([-inv.sum(axis=1),inv]);slope=grad@res.x[ids]
            if np.linalg.norm(slope)>1.5:
                centroid=pts.mean(axis=0);records.append({'world_xz':(centroid+O[[0,2]]).tolist(),'slope':float(np.linalg.norm(slope)),'projected_area':float(Polygon(pts).area),'vertices':[{'xz':xy[i].tolist(),'old':float(old[i]),'result':float(res.x[i]),'fixed':bool(fixed[i]),'upper':float(upper[i])} for i in ids]})
        records.sort(key=lambda r:-r['slope'])
        (folder/'infeasibility-diagnostic.json').write_text(json.dumps({'without_slope_success':bool(no_slope.success),'minimum_slope_slack':float(res.x[-1]),'worst':records[:30]},indent=2))
        print(json.dumps(records[:3]),flush=True)
    raise SystemExit(0)
result=linprog(-objective,A_ub=a,b_ub=np.array(rhs),bounds=bounds,method='highs',options={'dual_feasibility_tolerance':1e-8,'primal_feasibility_tolerance':1e-8})
report={'label':label,'success':bool(result.success),'message':result.message,'vertices':n,'free_vertices':int((~fixed).sum()),'face_gradient_inequalities':slope_rows,'cap_inequalities':cap_rows,'method':'Maximize area-weighted ground height subject to desired cut/fill upper envelope, fixed original outside/protected vertices, exact cap-overlap constraints and per-face gradient-component limits max(0.75, abs(original component)+0.001).','source_glb_sha256':sha}
if result.success:
    report.update(max_inequality_error_m=float(np.max(a@result.x-np.array(rhs))),maximum_height_change_m=float(np.max(abs(result.x-old))),maximum_lowering_below_desired_m=float(np.max(upper-result.x)))
(folder/'surface-solve.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
assert result.success,result.message
assert np.max(a@result.x-np.array(rhs))<.0001
(folder/'grading-unresolved.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
d['resolved_heights']=result.x.tolist();d['original_actual_heights']=old.tolist();d['surface_solver']=report
path.write_text(json.dumps(d,indent=2),encoding='utf-8')
