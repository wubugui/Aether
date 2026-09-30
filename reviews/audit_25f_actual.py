from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
from collections import defaultdict
old,osha=load(R/'captures/headland_study_23g/mainland_headland.glb');new,nsha=load(R/'captures/village_grading_study_25f/mainland_headland.glb');op,oh,ot,orr=prepare(old);np_,nh,nt,nr=prepare(new)
rep=json.loads((R/'captures/village_grading_study_25f/build-report.json').read_text());out={'scope':'Independent actual25f GLB vs actual23g GLB and actual24m paving caps. Plane extrema over polygon intersections, not only point sampling. No GPU/full-art acceptance.','identity':{'old_glb_sha256':osha,'new_glb_sha256':nsha,'build_passed':rep['passed'],'glb_matches_build_report':nsha==rep['glb_sha256'],'blend_matches_build_report':hashlib.sha256((R/'captures/village_grading_study_25f/mainland_headland.blend').read_bytes()).hexdigest()==rep['source_sha256']},'paving':[]}
import sys
if '--finish-only' in sys.argv:out=json.loads((R/'reviews/round-25f-village-earthworks-independent-review.json').read_text())
for group in ([] if '--finish-only' in sys.argv else ['foreground','bay']):
    caps,csha=load(R/('captures/village_paving_study_24m/village_'+group+'.glb'));bands=defaultdict(list);count=0
    for r in caps:
        v=r['v']
        if np.cross(v[1]-v[0],v[2]-v[0])[1]<=1e-9 or np.ptp(v[:,1])>1e-5:continue
        key=('foundation' if 'buried rubble' in r['material'] else 'paver',round(float(v[0,1]),6));bands[key].append(Polygon(v[:,[0,2]]));count+=1
    worst=None;overlaps=0
    for (kind,y),pp in bands.items():
        poly=shapely.union_all(pp)
        for i in nt.query(poly):
            inter=poly.intersection(np_[i])
            if inter.area<1e-10:continue
            vv=np.array(vertices(inter));err=vv@nh[i][:2]+nh[i][2]-y;k=int(np.argmax(err));value=float(err[k]);overlaps+=1
            if worst is None or value>worst['terrain_above_cap_m']:worst={'terrain_above_cap_m':value,'world_xz':(vv[k]+O[[0,2]]).tolist(),'kind':kind,'cap_y':y,'terrain_y':y+value,'intersection_area_m2':inter.area}
    row={'group':group,'paving_sha256':csha,'cap_triangles':count,'terrain_intersections':overlaps,'worst':worst};out['paving'].append(row);print(json.dumps(row),flush=True)
    (R/'reviews/round-25f-village-earthworks-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    if worst['terrain_above_cap_m']>.01:print('REJECT CAP PENETRATION',flush=True)

# Compare the actual core component to the original core, avoiding buried rock
# shoulder top faces as false candidate terrain heights. Rock faces are checked
# separately by unchanged actual geometry, rather than comparing every layer.
def core_rows(rows):
    parent=list(range(len(rows)));lookup={}
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,row in enumerate(rows):
        for v in row['v']:
            k=tuple(v)
            if k in lookup:parent[find(i)]=find(lookup[k])
            else:lookup[k]=i
    cc=Counter(find(i) for i in range(len(rows)));core=max(cc,key=cc.get)
    return [r for i,r in enumerate(rows) if find(i)==core]
oldcore=core_rows(old);newcore=core_rows(new)
op,oh,ot,orr=prepare(oldcore);np_,nh,nt,nr=prepare(newcore)
out['core_layer_selection']={'method':'Largest coordinate-connected actual mesh triangle component; avoids buried rock top layers in old/new core height comparison.','old_core_triangles':len(oldcore),'new_core_triangles':len(newcore)}
# Actual house foundation material faces restricted to the base, whose upper
# surface is at local y=0.18m. No preparer hard-coded footprint is imported.
run=R/'captures/validation_runs/village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7/study-inputs';plan=json.loads((R/'captures/village_street_layout_24a/layout.json').read_text());assets={};out['foundations']=[]
for asset,path in [('keeper_house',run/'keeper_house.glb'),('fisher_cottage',run/'headland/fisher_cottage.glb'),('quay_workshop',run/'headland/quay_workshop.glb')]:
    rr,sha=load(path);base=[r for r in rr if r['material']=='Keeper sandstone foundations' and np.max(r['v'][:,1])<=.181];pp=[Polygon(r['v'][:,[0,2]]) for r in base if Polygon(r['v'][:,[0,2]]).area>1e-10];assets[asset]=(shapely.union_all(pp),sha)
    print('ACTUAL BASE',asset,len(base),assets[asset][0].bounds,assets[asset][0].area,flush=True)
for h in plan['houses']:
    p,sha=assets[h['asset']];c,s=math.cos(h['yaw']),math.sin(h['yaw']);xy=np.array([h['position'][0]-O[0],h['position'][2]-O[2]])
    bx,bz,ex,ez=p.bounds
    body=Polygon([(bx,bz),(ex,bz),(ex,-bz),(bx,-bz)])
    body=shapely.transform(body,lambda v:v@np.array([[c,-s],[s,c]])+xy)
    p=shapely.transform(p,lambda v:v@np.array([[c,-s],[s,c]])+xy);worst=None;overlaps=0;body_worst=None
    for ni in nt.query(p):
        cut=p.intersection(np_[ni])
        if cut.area<1e-10:continue
        for oi in ot.query(cut):
            inter=cut.intersection(op[oi])
            if inter.area<1e-10:continue
            vv=np.array(vertices(inter));diff=nh[ni]-oh[oi];errors=vv@diff[:2]+diff[2];k=int(np.argmax(np.abs(errors)));err=float(errors[k]);overlaps+=1
            if worst is None or abs(err)>abs(worst['height_change_m']):worst={'height_change_m':err,'world_xz':(vv[k]+O[[0,2]]).tolist(),'intersection_area_m2':inter.area}
            interior=inter.intersection(body)
            if interior.area>1e-10:
                vb=np.array(vertices(interior));eb=vb@diff[:2]+diff[2];kb=int(np.argmax(np.abs(eb)));errb=float(eb[kb])
                if body_worst is None or abs(errb)>abs(body_worst['height_change_m']):body_worst={'height_change_m':errb,'world_xz':(vb[kb]+O[[0,2]]).tolist(),'intersection_area_m2':interior.area}
    row={'house':h['name'],'asset_glb_sha256':sha,'actual_base_projection_area_m2':p.area,'intersection_cells':overlaps,'worst':worst,'main_body_excluding_forward_doorstep_worst':body_worst};out['foundations'].append(row);print(json.dumps(row),flush=True)
    (R/'reviews/round-25f-village-earthworks-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

facekey=lambda r:(r['material'],tuple(sorted(tuple(v) for v in r['v'])))
old_nonup=[r for r in old if np.cross(r['v'][1]-r['v'][0],r['v'][2]-r['v'][0])[1]<=1e-10]
out['preserved_lower_side']={'original_triangles':len(old_nonup),'missing_exact_geometry_and_material':sum((Counter(facekey(r) for r in old_nonup)-Counter(facekey(r) for r in new)).values())}
edges=Counter()
for r in orr:
    for a,b in zip(r['v'],np.roll(r['v'],-1,axis=0)):edges[tuple(sorted((tuple(a),tuple(b))))]+=1
adj={}
for e,n in edges.items():
    if n==1:
        a,b=e;adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
todo=set(adj);components=[];actual={tuple(v) for r in new for v in r['v']}
while todo:
    start=todo.pop();found={start};stack=[start]
    while stack:
        for v in adj[stack.pop()]:
            if v not in found:found.add(v);todo.discard(v);stack.append(v)
    components.append(found)
core=max(components,key=len);out['original_border']={'component_vertex_counts':sorted([len(c) for c in components],reverse=True),'core_vertex_count':len(core),'core_missing_exact_coordinates':len(core-actual)}

# Changed surface slope scan: exclude microscopic slivers from the main slope
# risk metric, but retain the exact constraints used for that distinction.
risks=[]
for ni,p in enumerate(np_):
    if p.area<.01:continue
    vv0=nr[ni]['v'][:,[0,2]];minedge=min(np.linalg.norm(a-b) for a,b in zip(vv0,np.roll(vv0,-1,axis=0)))
    if minedge<.05:continue
    delta_max=0.;old_slopes=[]
    for oi in ot.query(p):
        inter=p.intersection(op[oi])
        if inter.area<1e-10:continue
        vv=np.array(vertices(inter));delta=nh[ni]-oh[oi];delta_max=max(delta_max,float(np.max(np.abs(vv@delta[:2]+delta[2]))));old_slopes.append(float(np.linalg.norm(oh[oi][:2])))
    if delta_max>.01:
        grade=float(np.linalg.norm(nh[ni][:2]));risks.append({'slope_ratio':grade,'slope_degrees':math.degrees(math.atan(grade)),'original_max_slope_ratio':max(old_slopes or [0]),'max_height_change_m':delta_max,'projected_area_m2':p.area,'world_xz_centroid':(np.array(p.centroid.coords)[0]+O[[0,2]]).tolist(),'minimum_projected_edge_m':float(minedge)})
out['changed_surface_slope_scan']={'minimum_projected_triangle_area_m2':.01,'minimum_projected_edge_m':.05,'changed_threshold_m':.01,'eligible_changed_triangles':len(risks),'steepest':sorted(risks,key=lambda r:r['slope_ratio'],reverse=True)[:10]}
out['status']='Geometry review complete; GPU/visual review pending'
(R/'reviews/round-25f-village-earthworks-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'preserved':out['preserved_lower_side'],'border':out['original_border'],'steepest':out['changed_surface_slope_scan']['steepest'][:3]},indent=2),flush=True)

