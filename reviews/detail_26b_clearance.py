from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
from scipy.spatial import cKDTree
path=R/'reviews/round-26b-village-sloped-paving-independent-review.json';d=json.loads(path.read_text());design=json.loads((R/'captures/village_paving_study_26b/paving-design.json').read_text());terrain,_=load(R/'captures/village_grading_study_26b/mainland_headland.glb');tp,th,tt,tr=prepare(terrain)
for gi,g in enumerate(d['groups']):
    rows,_=load(R/('captures/village_paving_study_26b/village_'+g['name']+'.glb'));top=np.array([[xz[0]-O[0],y,xz[1]-O[2]] for s in design['groups'][gi]['solids'] if s['kind']=='paver' for xz,y in zip(s['vertices_xz'],s['top_heights'])]);vt=cKDTree(top);cp,ch,ct,cr=prepare([r for r in rows if 'buried rubble' not in r['material'] and max(vt.query(r['v'])[0])<=.0001]);worst=None
    for i,p in enumerate(cp):
        for j in tt.query(p):
            inter=p.intersection(tp[j])
            if inter.area<1e-10:continue
            vv=np.array(vertices(inter));df=th[j]-ch[i];delta=vv@df[:2]+df[2];k=int(np.argmax(delta));value=float(delta[k])
            if worst is None or value>worst['terrain_above_true_paver_top_m']:worst={'terrain_above_true_paver_top_m':value,'world_xz':(vv[k]+O[[0,2]]).tolist(),'overlap_area_m2':inter.area,'actual_paver_top_y':float(vv[k]@ch[i][:2]+ch[i][2]),'actual_terrain_y':float(vv[k]@th[j][:2]+th[j][2])}
    g['true_paver_top_terrain_worst']=worst;print(g['name'],worst,flush=True)
g=d['groups'][0];w=g['worst_terrain'];v=np.array(w['cap_triangle_world_xyz'])-O;p=Polygon(v[:,[0,2]]);point=Point(np.array(w['world_xz'])-O[[0,2]]);candidates=[]
for i in tt.query(point.buffer(1e-7)):
    if tp[i].distance(point)<1e-7:
        y=float(np.array(point.coords)[0]@th[i][:2]+th[i][2]);candidates.append((abs(y-w['terrain_y']),i))
_,i=min(candidates);inter=p.intersection(tp[i]);hull=np.array(inter.convex_hull.exterior.coords)[:-1];widths=[]
for a,b in zip(hull,np.roll(hull,-1,axis=0)):
    e=b-a;n=np.array([-e[1],e[0]])/np.linalg.norm(e);proj=hull@n;widths.append(float(np.ptp(proj)))
w['intersection_minimum_caliper_width_m']=min(widths);w['intersection_world_xz']=(hull+O[[0,2]]).tolist()
path.write_text(json.dumps(d,indent=2),encoding='utf-8');print('bedding-overlap-width',w['intersection_minimum_caliper_width_m'],flush=True)
