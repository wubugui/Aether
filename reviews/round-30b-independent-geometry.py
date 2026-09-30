from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
from shapely.geometry import LineString
from shapely.ops import polygonize
from shapely.strtree import STRtree
P=R/'captures/lantern_island_study_30b';B=R/'captures/lantern_island_study_30a';e=json.loads((P/'geometry-evidence.json').read_text());plan=json.loads((P/'proportion-plan.json').read_text());d=glb(P/'island_c.glb');db=glb(B/'island_c.glb');allactual=np.concatenate(list(d.values()));actual=counter(allactual)
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';cn='island_c faulted bedrock'
for name,needle in [(tn,'olive grass'),(pn,'footpath')]:
    assert e['old'][name]==e['new'][name];key=next(k for k in d if needle in k);assert counter(d[key])==counter(db[key])
def triangulate(o):
    v=np.array(o['vertices']);return np.array([v[[f[0],f[j],f[j+1]]] for f in o['polygons'] for j in range(1,len(f)-1)])
objects={}
for name,o in e['new'].items():
    q=triangulate(o)
    for f in o['polygons']:
        if len(f)==3:assert tri_key(np.array(o['vertices'])[f]) in actual
    objects[name]=q
tv=np.array(e['new'][tn]['vertices']);cv=np.array(e['new'][cn]['vertices']);nv=len(tv)//2;assert np.array_equal(cv[54:],tv[nv:]);assert not any(36<=a<54 and 36<=b<54 for f in e['new'][cn]['polygons'] for a,b in zip(f,f[1:]+f[:1]))
ec=collections.Counter();directed=collections.Counter()
for f in e['new'][cn]['polygons']:
    for a,b in zip(f,f[1:]+f[:1]):ec[tuple(sorted((a,b)))]+=1;directed[(a,b)]+=1
assert all(n==2 for n in ec.values());assert all(directed[(a,b)]==directed[(b,a)]==1 for a,b in ec)
corevol=sum(float(np.dot(t[0],np.cross(t[1],t[2]))/6) for t in objects[cn]);assert corevol>0
mapping=plan['core_boundary_map'];panels=[]
for i in range(18):
    j=(i+1)%18;ids=[18+i,18+j,54+mapping[j],54+mapping[i]];poly=Polygon(cv[ids,:2]);center=Point(cv[36+i,:2]);panels.append({'sector':i,'quad_projection_valid':poly.is_valid,'center_covered_by_projected_quad':poly.covers(center),'projected_area_m2':poly.area})
def upper(ts):return [t for t in ts if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-10]
def plane(t):return np.linalg.solve(np.c_[t[:,:2],np.ones(3)],t[:,2])
def coords(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return list(g.exterior.coords)
    if hasattr(g,'geoms'):return [p for sub in g.geoms for p in coords(sub)]
    return list(g.coords)
road=unary_union([Polygon(t[:,:2]) for t in upper(objects[pn])]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']])
run=R/'captures/validation_runs/lantern-island-30a-20260908T180129Z-961944bd320b46a4bb5f15256ceb5c8f/images/day-d-front.png.json';side=json.loads(run.read_text());tree_points=[]
for p in side['placements']:
    if p.get('kind')!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
    origin=np.array([-3050,0,-2650]) if p['island']=='island_c' else np.array(plan['d_world_position']);yaw=0 if p['island']=='island_c' else plan['d_yaw'];delta=np.array(p['position'])-origin;co,si=math.cos(yaw),math.sin(yaw);tree_points.append({'island':p['island'],'xy':[co*delta[0]-si*delta[2],-(si*delta[0]+co*delta[2])],'runtime_scale':p['scale']})
trees=unary_union([Point(p['xy']).buffer(2) for p in tree_points]);masks={'road':road,'pads':pads,'tree_axis_2m_disks':trees}
ground=upper(objects[tn]);gpoly=[Polygon(t[:,:2]) for t in ground];gplane=[plane(t) for t in ground];index=STRtree(gpoly)
clearance=[]
for name,ts in objects.items():
    if name in [tn,pn]:continue
    roofts=upper(ts)
    if name==cn:
        cap_keys={pointkey(v) for v in cv[54:]}
        # Only actual authored triangular side panels: exclude the concave
        # bottom n-gon fan used solely for signed volume and horizontal slices.
        side_triangles=[cv[f] for f in e['new'][cn]['polygons'] if len(f)==3 and not all(i>=54 for i in f)]
        roofts=upper(side_triangles)
    row={'name':name,'regions':{}}
    for kind,mask in masks.items():
        vals=[];patch=[]
        for q in roofts:
            poly=Polygon(q[:,:2]).intersection(mask)
            if poly.is_empty:continue
            qp=plane(q)
            for j in index.query(poly):
                overlap=poly.intersection(gpoly[j])
                if overlap.is_empty:continue
                patch.append(overlap)
                for x,y in coords(overlap):vals.append(float(np.dot(gplane[j]-qp,[x,y,1])))
        row['regions'][kind]={'intersection_area_m2':unary_union(patch).area,'extrema_samples':len(vals),'minimum_gap_below_support_terrain_m':min(vals) if vals else None}
    clearance.append(row)
def section(ts,z):
    lines=[]
    for t in ts:
        points=[]
        for a,b in zip(t,np.roll(t,-1,axis=0)):
            if (a[2]<z<b[2]) or (b[2]<z<a[2]):
                p=a+(b-a)*(z-a[2])/(b[2]-a[2]);points.append(tuple(np.round(p[:2],6)))
        if len(set(points))==2:lines.append(LineString(points))
    return unary_union(list(polygonize(unary_union(lines))))
levels=[.5,2.,4.];slices={(name,z):section(ts,z) for name,ts in objects.items() if name not in [tn,pn] for z in levels};contacts=[]
for edit in plan['rock_edits']:
    name=edit['name'];parent=edit.get('root_toward',cn);samples=[]
    for z in levels:
        a=slices[name,z];b=slices[parent,z];samples.append({'z_m':z,'rock_section_area_m2':a.area,'parent_section_area_m2':b.area,'overlap_area_m2':a.intersection(b).area,'gap_m':a.distance(b) if not a.is_empty and not b.is_empty else None})
    contacts.append({'rock':name,'parent':parent,'sampled_water_above_sections':samples,'has_measured_above_water_section_overlap':any(s['overlap_area_m2']>1e-5 for s in samples)})
report={'scope':'Bounded actualGLB/source increment. Inherit unchanged30a pad/path coverage, do not rerun it. Protective height checks compare edited roofs to unchanged terrain within actual road/pads/runtime tree-axis disks. Contact evidence is three actual mesh sections above water, not full intersection-free proof or all-volume measurement.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',B/'island_c.glb',run]},'terrain_path_source_exact_and_glb_same_at_1e_5_m':True,'core_cap_interface_exact':True,'core_edges_oppositely_paired':True,'core_signed_volume_m3':corevol,'no_center_to_center_edges':True,'core_projection_panels':panels,'runtime_tree_localizations':tree_points,'edited_roof_protective_clearance':clearance,'sampled_contacts':contacts}
(R/'reviews/round-30b-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'core_signed_volume_m3':corevol,'invalid_panels':[p for p in panels if not p['quad_projection_valid'] or not p['center_covered_by_projected_quad']],'clearance':[r for r in clearance if any(v['extrema_samples'] for v in r['regions'].values())],'contact_without_sampled_overlap':[r for r in contacts if not r['has_measured_above_water_section_overlap']]},indent=2))
