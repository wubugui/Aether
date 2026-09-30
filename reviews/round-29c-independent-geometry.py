from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
NEW=R/'captures/lantern_island_study_29c';PREV=R/'captures/lantern_island_study_29b'
old=glb(PREV/'island_c.glb');new=glb(NEW/'island_c.glb');a=json.loads((PREV/'geometry-evidence.json').read_text());e=json.loads((NEW/'geometry-evidence.json').read_text())
assert all(e['new'][name]==obj for name,obj in a['new'].items())
oldtris=counter(np.concatenate(list(old.values())));newall=np.concatenate(list(new.values()));newtris=counter(newall);assert not (oldtris-newtris)
lookup={tri_key(t):t for t in newall};pk=next(k for k in new if 'footpath' in k);tk=next(k for k in new if 'olive grass' in k)
assert counter(old[pk])==counter(new[pk]);assert counter(old[tk])==counter(new[tk])
def upward(ts):return [t for t in ts if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-10]
roads=upward(new[pk]);assert len(roads)==259
protect=unary_union([Polygon(t[:,:2]) for t in roads]+[Polygon(p) for p in e['protection']['pads']]+[Point(p).buffer(2) for p in e['protection']['trees']])
def plane(t):return np.linalg.solve(np.c_[t[:,:2],np.ones(3)],t[:,2])
support=[]
for t in upward(new[tk]):
    region=Polygon(t[:,:2]).intersection(protect)
    if not region.is_empty:support.append((region,plane(t)))
def coords(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return list(g.exterior.coords)+[p for r in g.interiors for p in r.coords]
    if hasattr(g,'geoms'):return [p for sub in g.geoms for p in coords(sub)]
    return list(g.coords)
results=[]
for spec in e['shoulders']['meshes']:
    obj=e['new'][spec['name']];v=np.array(obj['vertices']);assert all(tri_key(v[f]) in lookup for f in obj['polygons'])
    roof=[lookup[tri_key(v[f])] for f in spec['roof_faces']];gaps=[];pieces=[]
    for t in roof:
        rp=plane(t);poly=Polygon(t[:,:2])
        for region,sp in support:
            overlap=poly.intersection(region)
            if overlap.is_empty:continue
            pieces.append(overlap)
            for x,y in coords(overlap):gaps.append(float(np.dot(sp-rp,[x,y,1])))
    union=unary_union(pieces)
    results.append({'name':spec['name'],'actual_glb_all_triangles_present':True,'actual_roof_triangles':len(roof),'protected_projection_overlap_area_m2':float(union.area),'intersection_vertex_samples':len(gaps),'minimum_measured_vertical_gap_m':min(gaps) if gaps else None,'maximum_measured_vertical_gap_m':max(gaps) if gaps else None,'note':'No protected projection intersection; no measured clearance.' if not gaps else 'Exact linear plane difference extrema on all clipped intersection vertices; actual exported roof and terrain.'})
    if gaps:assert min(gaps)>.11998
report={'scope':'Independent actual GLB surface decode. Protected region actual road footprint (not its1.2m buffer), padded foundations and2m tree-axis disks. Upper rock roof versus existing support terrain; not physical player or tree-branch clearance.','files':{str(p.relative_to(R)):sha(p) for p in [PREV/'island_c.glb',NEW/'island_c.glb',NEW/'geometry-evidence.json',NEW/'island_c.blend']},'old_source_objects_preserved':len(a['new']),'old_glb_all_triangles_retained_at_1e_5_m':True,'path_and_terrain_actual_glb_unchanged':True,'path_top_triangles':259,'shoulders':results}
(R/'reviews/round-29c-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(results,indent=2))
