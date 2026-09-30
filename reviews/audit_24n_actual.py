from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
from collections import defaultdict
terrain,terrain_sha=load(R/'captures/village_grading_study_24l/mainland_headland.glb');tp,th,tt,tr=prepare(terrain)
before=json.loads((R/'captures/village_paving_design_24j/paving.json').read_text());design=json.loads((R/'captures/village_paving_design_24m/paving.json').read_text());model=json.loads((R/'captures/village_paving_study_24m/model-report.json').read_text())
out={'scope':'Independent actual 24m GLB caps vs actual 24l GLB terrain for 24n composition. Cap triangles unioned by exact exported height and foundation/paver kind; full polygon/terrain-triangle intersections and linear height extrema. Not GPU or full visual/walking acceptance.','terrain_glb_sha256':terrain_sha,'groups':[]}
for gi,name in enumerate(['foreground','bay']):
    source=R/('captures/village_paving_study_24m/village_'+name+'.glb');rr,sha=load(source);bands=defaultdict(list);counts=Counter()
    for r in rr:
        v=r['v']
        if np.cross(v[1]-v[0],v[2]-v[0])[1]<=1e-9 or np.ptp(v[:,1])>1e-5:continue
        kind='foundation' if 'buried rubble' in r['material'] else 'paver';key=(kind,round(float(v[0,1]),6));bands[key].append(Polygon(v[:,[0,2]]));counts[kind]+=1
    bands={k:shapely.union_all(p) for k,p in bands.items()};worst=None;overlaps=0
    for (kind,y),poly in bands.items():
        for ii in tt.query(poly):
            inter=poly.intersection(tp[ii])
            if inter.area<1e-10:continue
            points=np.array(vertices(inter));vals=points@th[ii][:2]+th[ii][2]-y;k=int(np.argmax(vals));pen=float(vals[k]);overlaps+=1
            if worst is None or pen>worst['terrain_above_cap_m']:worst={'terrain_above_cap_m':pen,'world_xz':(points[k]+O[[0,2]]).tolist(),'kind':kind,'cap_y':y,'terrain_y':pen+y,'intersection_area_m2':inter.area}
    pv={y:p for (kind,y),p in bands.items() if kind=='paver'};crosslayer=[]
    for y,p in pv.items():
        for yy,q in pv.items():
            if yy-y<.12:continue
            x=p.intersection(q)
            if x.area>1e-10:crosslayer.append({'lower_y':y,'upper_y':yy,'area_m2':x.area,'area_after_3mm_inward_buffer_m2':x.buffer(-.003).area,'bounds_local_xz':x.bounds})
    historic=[]
    pts=[(-2257.72192382813,-1750.06359863281)] if name=='foreground' else [(-2224.3179219903564,-1872.8434267137125)]
    for point in pts:
        p=Point(point[0]-O[0],point[1]-O[2]);historic.append({'world_xz':point,'actual_cap_levels':[{'kind':kind,'y':y} for (kind,y),poly in bands.items() if poly.covers(p)]})
    oldf=[s for s in before['groups'][gi]['solids'] if s['kind']=='foundation'];newf=[s for s in design['groups'][gi]['solids'] if s['kind']=='foundation']
    asset=next(a for a in model['assets'] if a['name']=='village_'+name)
    row={'name':name,'glb_sha256':sha,'glb_hash_matches_saved_model_report':sha==asset['glb_sha256'],'blend_hash_matches_saved_model_report':hashlib.sha256(source.with_suffix('.blend').read_bytes()).hexdigest()==asset['source_sha256'],'foundation_dictionaries_identical_to24j':oldf==newf,'actual_cap_triangle_counts':dict(counts),'terrain_intersections':overlaps,'worst_terrain_cap_clearance':worst,'cross_layer_overlaps':crosslayer,'maximum_cross_layer_area_m2':max([r['area_m2'] for r in crosslayer]+[0]),'maximum_cross_layer_overlap_remaining_after3mm_erosion_m2':max([r['area_after_3mm_inward_buffer_m2'] for r in crosslayer]+[0]),'historic':historic};out['groups'].append(row)
    print(json.dumps({k:v for k,v in row.items() if k!='cross_layer_overlaps'},indent=2),flush=True)
out['status']='geometry checks complete; source native gate and GPU views pending'
(R/'reviews/round-24n-village-paving-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
