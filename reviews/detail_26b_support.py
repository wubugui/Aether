from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
from scipy.spatial import cKDTree
path=R/'reviews/round-26b-village-sloped-paving-independent-review.json';d=json.loads(path.read_text());design=json.loads((R/'captures/village_paving_study_26b/paving-design.json').read_text())
for gi,g in enumerate(d['groups']):
    rr,_=load(R/('captures/village_paving_study_26b/village_'+g['name']+'.glb'));top=np.array([[p[0]-O[0],h,p[1]-O[2]] for s in design['groups'][gi]['solids'] for p,h in zip(s['vertices_xz'],s['top_heights'])]);vt=cKDTree(top);cp,ch,ct,cr=prepare([r for r in rr if max(vt.query(r['v'])[0])<=.0001]);bed=[i for i,r in enumerate(cr) if 'buried rubble' in r['material']];bt=shapely.STRtree([cp[i] for i in bed]);pv=[i for i,r in enumerate(cr) if 'buried rubble' not in r['material']];significant=[];thin=[];angles=[]
    for i in pv:
        p=cp[i];v=cr[i]['v'];longest=max(float(np.linalg.norm(a-b)) for a,b in zip(v[:,[0,2]],np.roll(v[:,[0,2]],-1,axis=0)));altitude=2*p.area/longest
        if p.area>=.001 and altitude>=.005:angles.append(math.degrees(math.atan(float(np.linalg.norm(ch[i][:2])))))
        for jj in bt.query(p):
            j=bed[jj];inter=p.intersection(cp[j])
            if inter.area<1e-10:continue
            points=np.array(vertices(inter));df=ch[i]-ch[j];delta=points@df[:2]+df[2];record={'min_gap_m':float(np.min(delta)),'max_gap_m':float(np.max(delta)),'area_m2':inter.area,'eroded1mm_area_m2':inter.buffer(-.001).area}
            (significant if record['eroded1mm_area_m2']>.0001 else thin).append(record)
    g['support_at_resolved_width']={'criterion':'Intersection retains >0.0001m2 after1mm inward buffer; all raw extrema separately retained.','intersections':len(significant),'minimum_paver_top_minus_bedding_top_m':min(r['min_gap_m'] for r in significant),'maximum_paver_top_minus_bedding_top_m':max(r['max_gap_m'] for r in significant),'micro_or_edge_intersections':len(thin)}
    g['resolved_paver_face_slope']={'criterion':'Paver cap projected area>=0.001m2 and minimum projected altitude>=5mm; does not discard abnormal microcaps from full clearance audit.','faces':len(angles),'maximum_degrees':max(angles)}
    if gi==0:
        raw=d['raw_upward_faces_before_sidewall_classification'][0]['worst_terrain'];v=np.array(raw['cap_triangle_world_xyz'])-O;normal=np.cross(v[1]-v[0],v[2]-v[0]);normal/=np.linalg.norm(normal);xz=np.array(raw['world_xz'])-O[[0,2]];point=Point(xz);heights=[float(xz@ch[i][:2]+ch[i][2]) for i in ct.query(point.buffer(.0001)) if cp[i].distance(point)<.0001];raw['classification']={'role':'Slightly tilted vertical stone thickness wall: vertices include declared bottom and top; not all vertices match top role.','normalized_actual_face_normal_xyz':normal.tolist(),'actual_same_xz_upper_envelope_y':max(heights),'raw_side_point_below_actual_upper_envelope_m':max(heights)-raw['cap_y']}
path.write_text(json.dumps(d,indent=2),encoding='utf-8');print([(g['name'],g['support_at_resolved_width'],g['resolved_paver_face_slope']) for g in d['groups']])
