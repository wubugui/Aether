from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
P=R/'captures/lantern_island_study_30c';B=R/'captures/lantern_island_study_30b'
e=json.loads((P/'geometry-evidence.json').read_text());b=json.loads((B/'geometry-evidence.json').read_text());plan=json.loads((P/'proportion-plan.json').read_text());d=glb(P/'island_c.glb');db=glb(B/'island_c.glb');actual=counter(np.concatenate(list(d.values())))
tn='island_c grass and exposed rock terrain';cn='island_c faulted bedrock';pn='island_c terrain fitted keeper paths';n=e['retained_surface_vertex_count'];nf=e['retained_surface_face_count'];new=e['new'];old=b['new'];o=new[tn];v=np.array(o['vertices']);ov=np.array(old[tn]['vertices'])
assert e['old']==old and len(new)==19 and cn not in new
topfaces=[f for f in old[tn]['polygons'] if all(i<n for i in f)];topm=[m for f,m in zip(old[tn]['polygons'],old[tn]['materials']) if all(i<n for i in f)]
assert n==745 and nf==len(topfaces) and len(v)==n+54
assert np.array_equal(v[:n],ov[:n]);assert o['polygons'][:nf]==topfaces and o['materials'][:nf]==topm
assert np.array_equal(v[n:],np.array(old[cn]['vertices'])[:54])
preserved=[]
for name,ob in new.items():
 if name!=tn:assert ob==old[name];preserved.append(name)
 for face in ob['polygons']:
  if len(face)==3:assert tri_key(np.array(ob['vertices'])[face]) in actual,(name,face)
# Retained path and rocks exactly match corresponding actual GLB geometry,
# independent of new material grouping on welded terrain.
for k,tris in db.items():
 if 'olive grass' not in k and 'bedrock' not in k:
  for key,count in counter(tris).items():assert actual[key]>=count
edges=collections.Counter();directions=collections.Counter()
for f in o['polygons']:
 for a,z in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,z)))]+=1;directions[(a,z)]+=1
assert all(c==2 for c in edges.values());assert all(directions[a,z]==directions[z,a]==1 for a,z in edges)
key=next(k for k in d if 'olive grass' in k);tris=d[key]
assert all(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-10 for t in tris)
volume=sum(float(np.dot(t[0],np.cross(t[1],t[2]))/6) for t in tris);assert volume>0
actualedges=collections.Counter()
for t in tris:
 for a,z in zip(t,np.roll(t,-1,axis=0)):actualedges[tuple(sorted((pointkey(a),pointkey(z))))]+=1
assert all(c==2 for c in actualedges.values())
assert not any(all(i<n for i in f) for f in o['polygons'][nf:])
mapping=plan['core_boundary_map'];panels=[]
for i in range(18):
 j=(i+1)%18;poly=Polygon(v[[n+18+i,n+18+j,mapping[j],mapping[i]],:2]);ok=poly.is_valid and poly.covers(Point(v[n+36+i,:2]));assert ok;panels.append({'sector':i,'valid_with_center_inside':bool(ok)})
report={'round':'30c','scope':'Actual GLB/source bounded welded-exterior increment. Inherit unchanged 30b path/pad/rock protective and sampled-contact results; no repeated full section or support test.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',B/'island_c.glb']},'native_objects':len(new),'top_vertices_exact':n,'top_faces_order_materials_exact':nf,'path_and_17_rocks_source_exact_and_actual_triangles_present':preserved,'welded_vertices':len(v),'welded_faces':len(o['polygons']),'no_old_bottom_cap_or_constant_thickness_skirt':True,'coast54_vertices_exact':True,'source_edges_oppositely_paired':True,'actual_glb_position_welded_edges_all_paired':True,'actual_glb_triangles_nonzero_area':True,'actual_glb_signed_volume_m3':volume,'coast_projection_panels':panels,'visual_acceptance':None,'limits':['Not an exhaustive 3D self-intersection test.','Topology validity and deleted skirt do not establish visible success.','Existing sampled shoulder overlap does not prove visible exposure.']}
(R/'reviews/round-30c-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['coast_projection_panels','path_and_17_rocks_source_exact_and_actual_triangles_present']},indent=2))
