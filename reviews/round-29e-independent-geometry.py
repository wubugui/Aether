from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
from shapely.strtree import STRtree
P=R/'captures/lantern_island_study_29e';B=R/'captures/lantern_island_study_29d';e=json.loads((P/'geometry-evidence.json').read_text());b=json.loads((B/'geometry-evidence.json').read_text());plan=json.loads((P/'terrain-plan.json').read_text());d=glb(P/'island_c.glb');db=glb(B/'island_c.glb');alltris=counter(np.concatenate(list(d.values())))
pn='island_c terrain fitted keeper paths';tn='island_c grass and exposed rock terrain';cn='island_c faulted bedrock';pk=next(k for k in d if 'footpath' in k);tk=next(k for k in d if 'olive grass' in k)
t=e['new'][tn];v=np.array(t['vertices']);v0=np.array(b['new'][tn]['vertices']);nv=len(v)//2;top=[(i,p) for i,p in enumerate(t['polygons']) if max(p)<nv]
sites=unary_union([Polygon(p) for p in e['protection']['pads']]+[Point(p).buffer(2) for p in e['protection']['trees']]);protected=[i for i,p in top if Polygon(v0[p,:2]).intersects(sites)];assert set(protected)==set(e['protected_face_indices']);assert len(protected)==234
for i in protected:
    p=t['polygons'][i];assert np.array_equal(v[p],v0[p]);assert t['materials'][i]==b['new'][tn]['materials'][i];assert tri_key(v[p]) in alltris
oldpath=b['new'][pn];newpath=e['new'][pn];assert oldpath['polygons']==newpath['polygons'];assert np.array_equal(np.array(oldpath['vertices'])[:,:2],np.array(newpath['vertices'])[:,:2])
assert all(tri_key(np.array(newpath['vertices'])[f]) in alltris for f in newpath['polygons'] if len(f)==3)
def upward(ts):return [t for t in ts if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-10]
paths=upward(d[pk]);ground=upward(d[tk]);assert len(paths)==259
gpoly=[Polygon(t[:,:2]) for t in ground];gindex=STRtree(gpoly)
def plane(t):return np.linalg.solve(np.c_[t[:,:2],np.ones(3)],t[:,2])
gplane=[plane(t) for t in ground]
def coords(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return list(g.exterior.coords)+[p for r in g.interiors for p in r.coords]
    if hasattr(g,'geoms'):return [p for sub in g.geoms for p in coords(sub)]
    return list(g.coords)
gaps=[];uncovered=0.;overlap_area=0.;slopes=[];patches=0
for q in paths:
    p=Polygon(q[:,:2]);pp=plane(q);covered=[];normal=np.cross(q[1]-q[0],q[2]-q[0]);normal/=np.linalg.norm(normal);slopes.append(float(np.degrees(np.arccos(normal[2]))))
    for j in gindex.query(p):
        overlap=p.intersection(gpoly[j])
        if overlap.is_empty:continue
        covered.append(overlap);patches+=1
        for x,y in coords(overlap):gaps.append(float(np.dot(pp-gplane[j],[x,y,1])))
    region=unary_union(covered);uncovered+=p.difference(region).area;overlap_area+=region.area
assert uncovered<1e-6;assert min(gaps)>.0449 and max(gaps)<.0451
unchanged=[]
for name,obj in b['new'].items():
    if name in [pn,tn,cn]:continue
    assert e['new'][name]==obj;verts=np.array(obj['vertices']);assert all(tri_key(verts[f]) in alltris for f in obj['polygons']);unchanged.append(name)
assert len(unchanged)==17
c=e['new'][cn];cv=np.array(c['vertices']);assert np.array_equal(cv[54:],v[nv:]);mapping=plan['core_boundary_map'];rings=[cv[:18,:2],cv[18:36,:2],cv[36:54,:2],cv[[54+j for j in mapping],:2]]
bad=[]
for level in range(3):
    for i in range(18):
        j=(i+1)%18;poly=Polygon([rings[level][i],rings[level][j],rings[level+1][j],rings[level+1][i]])
        if not poly.is_valid:bad.append([level,i])
report={'scope':'Independent actual exported GLB path/terrain triangle overlay;234 occupied tower/house/tree-support faces only. No old515 road-face or old road-height preservation claim. Projected core crossings not3D intersection proof.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',B/'island_c.glb']},'occupied_support_faces_exact':len(protected),'changed_top_vertices':int(np.sum(np.any(v[:nv]!=v0[:nv],axis=1))),'path_top_triangles':len(paths),'path_xy_and_topology_preserved':True,'path_heights_unchanged':np.array_equal(np.array(oldpath['vertices'])[:,2],np.array(newpath['vertices'])[:,2]),'actual_path_max_slope_deg':max(slopes),'actual_path_terrain_overlap_patches':patches,'actual_path_projected_covered_area_m2':overlap_area,'actual_path_uncovered_projected_area_m2':uncovered,'actual_path_gap_min_m':min(gaps),'actual_path_gap_max_m':max(gaps),'intersection_extrema_samples':len(gaps),'unchanged_rock_parts':unchanged,'core_cap_interface_exact':True,'projected_ring_simple':[Polygon(r).is_valid for r in rings],'projected_invalid_side_quads':bad}
report['changed_top_vertices_over_1e_5_m']=int(np.sum(np.abs(v[:nv,2]-v0[:nv,2])>1e-5))
(R/'reviews/round-29e-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','unchanged_rock_parts']},indent=2))
