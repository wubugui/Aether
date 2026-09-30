from pathlib import Path
# Reuse only the previously independently authored GLB decoder and helpers.
prefix=(Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0]
exec(compile(prefix,'round-29a-independent-geometry.py','exec'))
NEW=R/'captures/lantern_island_study_29b';OLD=R/'captures/lantern_island_study_29a/island_c.glb'
old=glb(OLD);new=glb(NEW/'island_c.glb');e=json.loads((NEW/'geometry-evidence.json').read_text());n=e['new']
pn='island_c terrain fitted keeper paths';tn='island_c grass and exposed rock terrain';cn='island_c faulted bedrock'
assert n[pn]==e['old']['path']
pathkey=next(k for k in old if 'footpath' in k);assert counter(old[pathkey])==counter(new[pathkey])
ts=new[pathkey];normal=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None];top=ts[normal[:,2]>.5];assert len(top)==259
road=unary_union([Polygon(t[:,:2]) for t in top]);pads=[Polygon(p) for p in e['protection']['pads']];trees=[Point(p) for p in e['protection']['trees']]
protection=unary_union([road.buffer(1.2)]+pads+[p.buffer(2) for p in trees])
tv0=np.array(e['old']['terrain']['vertices']);tv1=np.array(n[tn]['vertices']);polys=e['old']['terrain']['polygons'];assert polys==n[tn]['polygons'];nv=len(tv0)//2
protected=[i for i,p in enumerate(polys) if max(p)<nv and Polygon(tv0[p,:2]).intersects(protection)]
assert set(protected)==set(e['protected_face_indices'])
protected_vertices=sorted({v for i in protected for v in polys[i]});assert np.array_equal(tv0[protected_vertices],tv1[protected_vertices]);assert all(n[tn]['materials'][i]==e['old']['terrain']['materials'][i] for i in protected)
actualterrain=new[next(k for k in new if 'olive grass' in k)];actualcounter=counter(actualterrain);actualpoints={pointkey(p) for t in actualterrain for p in t}
assert all(pointkey(p) in actualpoints for p in tv1);assert all(tri_key(tv1[polys[i]]) in actualcounter for i in protected)
changed=np.flatnonzero(np.any(tv0[:nv]!=tv1[:nv],axis=1));assert not set(changed)&set(protected_vertices)
core=np.array(n[cn]['vertices']);assert np.array_equal(core[72:],tv1[nv:])
alltris=counter(np.concatenate(list(new.values())));allpoints={pointkey(p) for t in np.concatenate(list(new.values())) for p in t};crags=[]
for name,obj in n.items():
    if name in [pn,tn,cn]:continue
    verts=np.array(obj['vertices']);p=obj['polygons'];assert all(len(f)==3 for f in p)
    assert all(pointkey(v) in allpoints for v in verts);assert not (counter(verts[np.array(p)])-alltris)
    shape=MultiPoint(verts[:,:2]).convex_hull
    crags.append({'name':name,'actual_glb_present':True,'road_gap_m':shape.distance(road),'pad_gap_m':min(shape.distance(p) for p in pads),'tree_axis_gap_m':min(shape.distance(t) for t in trees),'min_z_m':float(verts[:,2].min()),'max_z_m':float(verts[:,2].max())})
assert len(crags)==17
report={'scope':'Independent actual GLB decode and source evidence check. No Blender/GPU run; no entire walking corridor or branch-volume clearance claim.','files':{str(p.relative_to(R)):sha(p) for p in [OLD,NEW/'island_c.glb',NEW/'island_c.blend',NEW/'geometry-evidence.json']},'path_export_triangles_unchanged_at_1e_5_m':True,'path_top_triangles':259,'path_max_slope_deg':float(np.degrees(np.arccos(normal[normal[:,2]>.5,2])).max()),'independent_protected_face_count':len(protected),'protected_faces_exact':True,'protection_definition':'Actual GLB path projection buffered1.2m, recorded expanded pads, tree axes buffered2m; all intersecting old top triangles.','changed_top_vertices':len(changed),'max_terrain_height_delta_m':float(abs(tv1[:,2]-tv0[:,2]).max()),'core_top_interface_exactly_matches_terrain_underside':True,'crags':crags,'min_road_gap_m':min(c['road_gap_m'] for c in crags),'min_padded_foundation_gap_m':min(c['pad_gap_m'] for c in crags),'min_tree_axis_gap_m':min(c['tree_axis_gap_m'] for c in crags)}
assert report['min_road_gap_m']>1.2 and report['min_padded_foundation_gap_m']>.2 and report['min_tree_axis_gap_m']>2
(R/'reviews/round-29b-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['files','crags']},indent=2))
