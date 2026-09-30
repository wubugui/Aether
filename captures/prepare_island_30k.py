from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
p=json.loads((R/'captures/island-30j-authored-cut-plan.json').read_text())
e=json.loads((R/'captures/lantern_island_study_30d/geometry-evidence.json').read_text())
def upward(o):
    v=np.array(o['vertices']);return [v[f] for f in o['polygons'] if len(f)==3 and np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]])[2]>1e-9]
surface=upward(e['new']['island_c grass and exposed rock terrain'])
mask=unary_union([*[Polygon(t[:,:2]) for t in upward(e['new']['island_c terrain fitted keeper paths'])],*[Polygon(s['polygon']) for s in e['sites']]])
protected=[(t,Polygon(t[:,:2]).intersection(mask)) for t in surface]
protected=[(t,q) for t,q in protected if q.area>1e-9]
def coordinates(g):
    if g.geom_type=='Polygon':
        yield from list(g.exterior.coords)[:-1]
        for ring in g.interiors:yield from list(ring.coords)[:-1]
    elif hasattr(g,'geoms'):
        for child in g.geoms:yield from coordinates(child)
records=[]
for c in p['components']:
    v=np.array(c['actual_lower_vertices'],dtype=float);rows=[];rhs=[]
    for face in c['actual_lower_triangles']:
        tri=v[face];poly=Polygon(tri[:,:2]);basis=np.linalg.inv(np.vstack([tri[:,:2].T,np.ones(3)]))
        for old,q in protected:
            patch=poly.intersection(q)
            if patch.area<1e-9:continue
            height=np.linalg.solve(np.column_stack([old[:,:2],np.ones(3)]),old[:,2])
            for xy in coordinates(patch):
                b=basis@np.array([*xy,1]);row=np.zeros(len(v));row[face]=-b
                rows.append(row);rhs.append(-float(height@np.array([*xy,1]))-.15)
    if rows:
        result=linprog([.05,.05,.05,1,1,1,2,2,2],A_ub=rows,b_ub=rhs,bounds=[(float(z),max(16.,float(z)+6)) for z in v[:,2]],method='highs')
        assert result.success,(c['name'],result.message)
        minimum=min(float(-np.dot(a,result.x)-(-b)) for a,b in zip(rows,rhs))
        assert minimum>=-1e-7
        before=v[:,2].tolist();v[:,2]=result.x
        records.append(dict(name=c['name'],constraints=len(rows),before_heights=before,after_heights=v[:,2].tolist(),minimum_constraint_slack_m=minimum))
    c['actual_lower_vertices']=v.tolist();c['rows']=[v[i:i+3].tolist() for i in range(0,9,3)]
p['scope']='30k authored30j broad-face XY layout with upward-only inner/support height constraints (0.15m above actual30d road/pad planes). Three broad middle rows preserved; no distance-based dense blending. Eastern tree pair re-grounded on proposed lower shoulder; checks pending.'
p['tree_relocations'][0]['new_xy']=[17,-1.5]
p['support_height_adjustments']=records
dst=R/'captures/island-30k-authored-cut-plan.json';assert not dst.exists();dst.write_text(json.dumps(p,indent=2))
for a,b in [('blender/model_lantern_island_30j.py','blender/model_lantern_island_30k.py'),('captures/check_island_30j.py','captures/check_island_30k.py'),('tools/render_lantern_island_30j.py','tools/render_lantern_island_30k.py')]:
    dst=R/b;assert not dst.exists();dst.write_text((R/a).read_text().replace('30j','30k'))
print(json.dumps(records,indent=2))
