from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
from shapely.strtree import STRtree
P=R/'captures/lantern_island_study_30a';e=json.loads((P/'geometry-evidence.json').read_text());plan=json.loads((P/'proportion-plan.json').read_text());d=glb(P/'island_c.glb');alltris=counter(np.concatenate(list(d.values())))
pn='island_c terrain fitted keeper paths';tn='island_c grass and exposed rock terrain';cn='island_c faulted bedrock';pk=next(k for k in d if 'footpath' in k);tk=next(k for k in d if 'olive grass' in k)
def upward(ts):return [t for t in ts if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-11]
paths=upward(d[pk]);ground=upward(d[tk]);assert len(paths)==315
gpoly=[Polygon(t[:,:2]) for t in ground];gindex=STRtree(gpoly)
def plane(t):return np.linalg.solve(np.c_[t[:,:2],np.ones(3)],t[:,2])
gplane=[plane(t) for t in ground]
def coords(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return list(g.exterior.coords)+[p for r in g.interiors for p in r.coords]
    if hasattr(g,'geoms'):return [p for sub in g.geoms for p in coords(sub)]
    return list(g.coords)
gaps=[];uncovered=0.;area=0.;slopes=[];patches=0
for q in paths:
    p=Polygon(q[:,:2]);pp=plane(q);covered=[];normal=np.cross(q[1]-q[0],q[2]-q[0]);normal/=np.linalg.norm(normal);slopes.append(float(np.degrees(np.arccos(normal[2]))))
    for j in gindex.query(p):
        overlap=p.intersection(gpoly[j])
        if overlap.is_empty:continue
        covered.append(overlap);patches+=1
        for x,y in coords(overlap):gaps.append(float(np.dot(pp-gplane[j],[x,y,1])))
    region=unary_union(covered);uncovered+=p.difference(region).area;area+=region.area
assert uncovered<1e-6;assert min(gaps)>.0449 and max(gaps)<.0451
sites=[]
for site in e['sites']:
    polygon=Polygon(site['polygon']);heights=[];parts=[]
    for j in gindex.query(polygon):
        overlap=polygon.intersection(gpoly[j])
        if overlap.is_empty:continue
        parts.append(overlap)
        for x,y in coords(overlap):heights.append(float(np.dot(gplane[j],[x,y,1])))
    gap=polygon.difference(unary_union(parts)).area;error=max(abs(h-site['height']) for h in heights)
    sites.append({'site':site,'actual_projection_area_m2':polygon.area,'uncovered_area_m2':gap,'actual_surface_height_min_m':min(heights),'actual_surface_height_max_m':max(heights),'maximum_target_height_error_m':error,'clipped_vertex_samples':len(heights)})
    assert gap<1e-6 and error<2e-5
scale=np.array(e['land_scale']);rocks=[]
for name,obj in e['old'].items():
    if name in [pn,tn,cn]:continue
    new=e['new'][name];expected=np.array(obj['vertices'])*scale;actual=np.array(new['vertices']);assert obj['polygons']==new['polygons'];error=float(abs(actual-expected).max());assert error<6e-6
    assert all(tri_key(actual[f]) in alltris for f in new['polygons']);rocks.append({'name':name,'max_applied_vertex_scale_error_m':error,'actual_glb_all_triangles_present':True})
assert len(rocks)==17
tv=np.array(e['new'][tn]['vertices']);nv=len(tv)//2;cv=np.array(e['new'][cn]['vertices']);assert np.array_equal(cv[54:],tv[nv:]);mapping=plan['core_boundary_map'];rings=[cv[:18,:2],cv[18:36,:2],cv[36:54,:2],cv[[54+j for j in mapping],:2]];bad=[]
for level in range(3):
    for i in range(18):
        j=(i+1)%18
        if not Polygon([rings[level][i],rings[level][j],rings[level+1][j],rings[level+1][i]]).is_valid:bad.append([level,i])
report={'scope':'Independent actual30a GLB decode:full new pad coverage/height, re-fit path triangle overlay, applied land proportions. Native buildings are separate assets not in thisGLB; no proof of new world fixture placement until runtime.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',P/'proportion-plan.json']},'land_scale_xyz':scale.tolist(),'terrain_top_vertices':nv,'path_top_triangles':len(paths),'actual_path_max_slope_deg':max(slopes),'actual_path_gap_min_m':min(gaps),'actual_path_gap_max_m':max(gaps),'path_uncovered_projection_area_m2':uncovered,'path_covered_projection_area_m2':area,'path_overlap_patches':patches,'path_intersection_vertex_extrema_samples':len(gaps),'pads':sites,'scaled_rock_parts':rocks,'core_cap_interface_exact':True,'projected_rings_simple':[Polygon(r).is_valid for r in rings],'projected_invalid_side_quads':bad}
(R/'reviews/round-30a-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','scaled_rock_parts']},indent=2))
