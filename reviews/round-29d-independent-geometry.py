from pathlib import Path
from shapely.geometry import LineString
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
P=R/'captures/lantern_island_study_29d';B=R/'captures/lantern_island_study_29b';e=json.loads((P/'geometry-evidence.json').read_text());b=json.loads((B/'geometry-evidence.json').read_text());plan=json.loads((P/'terrain-plan.json').read_text());d=glb(P/'island_c.glb');db=glb(B/'island_c.glb');alltris=counter(np.concatenate(list(d.values())));allpoints={pointkey(p) for t in np.concatenate(list(d.values())) for p in t}
pn='island_c terrain fitted keeper paths';tn='island_c grass and exposed rock terrain';cn='island_c faulted bedrock';pk=next(k for k in d if 'footpath' in k);tk=next(k for k in d if 'olive grass' in k)
assert e['new'][pn]==b['new'][pn];assert counter(d[pk])==counter(db[pk]);t=e['new'][tn];v=np.array(t['vertices']);v0=np.array(b['new'][tn]['vertices']);nv=len(v)//2;top=[(i,p) for i,p in enumerate(t['polygons']) if max(p)<nv]
edges=collections.Counter(tuple(sorted((p[k],p[(k+1)%3]))) for _,p in top for k in range(3));boundary=sorted({i for edge,n in edges.items() if n==1 for i in edge});assert len(boundary)==18;assert np.array_equal(v[boundary],v0[boundary])
road=unary_union([Polygon(p) for p in e['protection']['path_top_triangles']]);mask=unary_union([road.buffer(1.2)]+[Polygon(p) for p in e['protection']['pads']]+[Point(p).buffer(2) for p in e['protection']['trees']]);protected=[i for i,p in top if Polygon(v0[p,:2]).intersects(mask)];assert set(protected)==set(e['protected_face_indices']);assert len(protected)==515
for i in protected:
    p=t['polygons'][i];assert np.array_equal(v[p],v0[p]);assert t['materials'][i]==b['new'][tn]['materials'][i];assert tri_key(v[p]) in alltris
assert all(pointkey(p) in allpoints for p in v)
unchanged=[]
for name,obj in b['new'].items():
    if name in [pn,tn,cn]:continue
    assert e['new'][name]==obj;verts=np.array(obj['vertices']);assert all(tri_key(verts[f]) in alltris for f in obj['polygons']);unchanged.append(name)
assert len(unchanged)==17
c=e['new'][cn];cv=np.array(c['vertices']);assert np.array_equal(cv[54:],v[nv:]);assert np.array_equal(cv[:36],np.array(b['new'][cn]['vertices'])[:36]);assert all(pointkey(p) in allpoints for p in cv)
edge_counts=collections.Counter();directed=collections.Counter();volume=0.;minarea=1e99
for f in c['polygons']:
    for x,y in zip(f,f[1:]+f[:1]):edge_counts[tuple(sorted((x,y)))]+=1;directed[(x,y)]+=1
    for k in range(1,len(f)-1):
        q=cv[[f[0],f[k],f[k+1]]];volume+=float(np.dot(q[0],np.cross(q[1],q[2]))/6);minarea=min(minarea,float(np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))/2))
    if len(f)==3:assert tri_key(cv[f]) in alltris
assert all(n==2 for n in edge_counts.values());assert all(directed[(x,y)]==directed[(y,x)]==1 for x,y in edge_counts);assert volume>0
mapping=plan['core_boundary_map'];rings=[cv[:18,:2],cv[18:36,:2],cv[36:54,:2],cv[[54+j for j in mapping],:2]];ringpolys=[Polygon(r) for r in rings];bands=[]
for band in range(3):
    quads=[];bad=[]
    for i in range(18):
        j=(i+1)%18;p=Polygon([rings[band][i],rings[band][j],rings[band+1][j],rings[band+1][i]])
        if not p.is_valid:bad.append(i)
        quads.append(p)
    bands.append({'band':band,'invalid_projected_quad_indices':bad,'sum_projected_quad_area_m2':sum(p.area for p in quads),'projected_quad_union_area_m2':unary_union(quads).area if not bad else None,'inner_ring_outside_outer_area_m2':ringpolys[band+1].difference(ringpolys[band]).area})
folds=[]
for band in bands:
    level=band['band']
    for i in band['invalid_projected_quad_indices']:
        j=(i+1)%18;ids=[level*18+i,level*18+j,(level+1)*18+j if level<2 else 54+mapping[j],(level+1)*18+i if level<2 else 54+mapping[i]];q=cv[ids];crossings=[]
        for a,b in [(0,2),(1,3)]:
            a1=(a+1)%4;b1=(b+1)%4;intersection=LineString([q[a,:2],q[a1,:2]]).intersection(LineString([q[b,:2],q[b1,:2]]))
            if intersection.geom_type!='Point':continue
            p=np.array(intersection.coords[0]);heights=[]
            for c1,c2 in [(a,a1),(b,b1)]:
                edge=q[c2,:2]-q[c1,:2];f=np.dot(p-q[c1,:2],edge)/np.dot(edge,edge);heights.append(float(q[c1,2]+f*(q[c2,2]-q[c1,2])))
            crossings.append({'crossing_xy':p.tolist(),'edge_heights_m':heights,'vertical_separation_m':abs(heights[0]-heights[1])})
        folds.append({'band':level,'edge':i,'source_vertex_indices':ids,'xyz':q.tolist(),'projected_edge_crossings':crossings})
report={'scope':'Independent actualGLB cross-check plus saved source core topology and projected boundary strips. Not proof of all 3D triangle intersections or visual acceptance.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',B/'island_c.glb']},'path_actual_glb_triangles_unchanged':True,'protected_faces_exact':len(protected),'boundary_vertices_exact':len(boundary),'changed_top_vertices':int(np.sum(np.any(v[:nv]!=v0[:nv],axis=1))),'unchanged_rock_parts':unchanged,'core_cap_interface_exact':True,'core_edges_twice_and_opposite':True,'core_signed_volume_m3':volume,'core_min_fan_triangle_area_m2':minarea,'core_rings_projected_simple':[p.is_valid for p in ringpolys],'core_band_projection_checks':bands,'fold_details':folds}
(R/'reviews/round-29d-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','unchanged_rock_parts']},indent=2))
