from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
import ast
from scipy.spatial import cKDTree
mod=ast.parse((R/'reviews/audit_25c_actual.py').read_text());f=next(n for n in mod.body if isinstance(n,ast.FunctionDef) and n.name=='core_rows');exec(compile(ast.Module(body=[f],type_ignores=[]),'independent-core','exec'))
terrain,tsha=load(R/'captures/village_grading_study_26b/mainland_headland.glb');tp,th,tt,tr=prepare(terrain)
plan=json.loads((R/'captures/village_street_layout_24a/layout.json').read_text());design=json.loads((R/'captures/village_paving_study_26b/paving-design.json').read_text());out={'scope':'Actual inclined AND horizontal upward face audit; upper surface role requires all actual vertices within0.1mm of declared top vertices, thereby excluding slightly tilted buried sidewalls without a permissive normal cutoff. All actual cap planes/intersections are measured from GLB. Not final art/full walking acceptance.','terrain_glb_sha256':tsha,'groups':[]}
old_report=R/'reviews/round-26b-village-sloped-paving-independent-review.json'
if old_report.exists():out['raw_upward_faces_before_sidewall_classification']=json.loads(old_report.read_text())['groups']
for gi,name in enumerate(['foreground','bay']):
    rows,sha=load(R/('captures/village_paving_study_26b/village_'+name+'.glb'))
    top_vertices=np.array([[xz[0]-O[0],y,xz[1]-O[2]] for s in design['groups'][gi]['solids'] for xz,y in zip(s['vertices_xz'],s['top_heights'])]);tree=cKDTree(top_vertices)
    top_rows=[r for r in rows if max(tree.query(r['v'])[0])<=.0001];cp,ch,ct,cr=prepare(top_rows);worst=None;intersections=0;slopes=[]
    for i,p in enumerate(cp):
        kind='foundation' if 'buried rubble' in cr[i]['material'] else 'paver'
        if p.area>.0001:slopes.append({'angle_deg':math.degrees(math.atan(float(np.linalg.norm(ch[i][:2])))),'kind':kind,'projected_area_m2':p.area,'world_xz_centroid':(np.array(p.centroid.coords)[0]+O[[0,2]]).tolist()})
        for j in tt.query(p):
            inter=p.intersection(tp[j])
            if inter.area<1e-10:continue
            vv=np.array(vertices(inter));plane=th[j]-ch[i];delta=vv@plane[:2]+plane[2];k=int(np.argmax(delta));value=float(delta[k]);intersections+=1
            if worst is None or value>worst['terrain_above_cap_m']:
                xz=vv[k];worst={'terrain_above_cap_m':value,'world_xz':(xz+O[[0,2]]).tolist(),'kind':kind,'cap_y':float(xz@ch[i][:2]+ch[i][2]),'terrain_y':float(xz@th[j][:2]+th[j][2]),'intersection_area_m2':inter.area,'cap_triangle_world_xyz':(cr[i]['v']+O).tolist(),'cap_projected_area_m2':p.area}
    print(name,'cap check',len(cp),'faces',worst,flush=True)
    entries=[]
    for h in [h for h in plan['houses'] if h['name'].startswith('fore_' if name=='foreground' else 'bay_')]:
        c,s=math.cos(h['yaw']),math.sin(h['yaw'])
        for lateral in [-.6,0,.6]:
            xz=np.array([h['entry'][0]+c*lateral+s*.02,h['entry'][1]-s*lateral+c*.02]);point=Point(xz-O[[0,2]]);hs=[float(np.array(point.coords)[0]@ch[i][:2]+ch[i][2]) for i in ct.query(point) if cp[i].distance(point)<1e-7];top=max(hs) if hs else None
            entries.append({'house':h['name'],'lateral_m':lateral,'world_xz':xz.tolist(),'expected_y':h['entry_y'],'actual_top_y':top,'difference_m':top-h['entry_y'] if top is not None else None})
    pp=[i for i,r in enumerate(cr) if 'buried rubble' not in r['material']];bed=[i for i,r in enumerate(cr) if 'buried rubble' in r['material']];bedtree=shapely.STRtree([cp[i] for i in bed]);pvtree=shapely.STRtree([cp[i] for i in pp]);support=[];topover=[];unsupported=[]
    for index in pp:
        p=cp[index];covered=[]
        for jj in bedtree.query(p):
            j=bed[jj];inter=p.intersection(cp[j])
            if inter.area<1e-10:continue
            covered.append(inter);vv=np.array(vertices(inter));df=ch[index]-ch[j];delta=vv@df[:2]+df[2];support.append({'min_gap_m':float(np.min(delta)),'max_gap_m':float(np.max(delta)),'overlap_area_m2':inter.area})
        missing=p.difference(shapely.union_all(covered))
        if missing.area>1e-6:unsupported.append({'area_m2':missing.area,'after_1mm_erosion_m2':missing.buffer(-.001).area,'world_xz':(np.array(missing.representative_point().coords)[0]+O[[0,2]]).tolist()})
        for jj in pvtree.query(p):
            j=pp[jj]
            if j<=index:continue
            inter=p.intersection(cp[j])
            if inter.area<1e-6:continue
            vv=np.array(vertices(inter));df=ch[index]-ch[j];delta=vv@df[:2]+df[2];maximum=float(np.max(np.abs(delta)))
            if maximum>.005:topover.append({'height_mismatch_m':maximum,'overlap_area_m2':inter.area,'world_xz':(np.array(inter.representative_point().coords)[0]+O[[0,2]]).tolist()})
    group={'name':name,'glb_sha256':sha,'actual_upward_cap_faces':len(cp),'inclined_upward_cap_faces':sum(bool(np.linalg.norm(h[:2])>.0001) for h in ch),'terrain_intersections':intersections,'worst_terrain':worst,'entry_transverse_samples':entries,'steepest_caps':sorted(slopes,key=lambda r:r['angle_deg'],reverse=True)[:5],'paver_bedding_gap_min_m':min(r['min_gap_m'] for r in support),'paver_bedding_gap_max_m':max(r['max_gap_m'] for r in support),'unsupported_projection_fragments':unsupported,'paver_paver_mismatch_over5mm':topover};out['groups'].append(group)
    print(json.dumps({k:v for k,v in group.items() if k not in ['entry_transverse_samples','unsupported_projection_fragments','steepest_caps']},indent=2),flush=True)
    (R/'reviews/round-26b-village-sloped-paving-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
