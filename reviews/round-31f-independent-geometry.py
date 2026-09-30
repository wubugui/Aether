from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30d-independent-geometry.py').read_text(encoding='utf-8').split('def exposure')[0].replace("P=R/'captures/lantern_island_study_30d';B=R/'captures/lantern_island_study_30c'","P=R/'captures/lantern_island_study_31f';B=R/'captures/lantern_island_study_31e'")
src=src.replace("trees=unary_union([Point(p['xy']).buffer(2) for p in intake['tree_axes']])", "current_axes=json.loads((R/'reviews/round-31d-rear-flank-independent.json').read_text())['actual_C_D_tree_local_axes'];trees=unary_union([Point(p).buffer(2) for p in current_axes])")
exec(compile(src,'31f_actual_required_support','exec'))
adj=collections.defaultdict(set)
for a,b in edge:adj[a].add(b);adj[b].add(a)
remaining=set(adj);components=[]
while remaining:
 start=remaining.pop();stack=[start];count=0
 while stack:
  q=stack.pop();count+=1
  for nxt in adj[q]:
   if nxt in remaining:remaining.remove(nxt);stack.append(nxt)
 components.append(count)
assert len(components)==1
plan=json.loads((P/'reform-plan.json').read_text());moved=plan['actual_moved_vertices'];lookup={pointkey(x['after']):np.array(x['before']) for x in moved};newpoints=set(pointkey(x) for t in ts for x in t);assert all(k in newpoints for k in lookup)
pre=np.array([[lookup.get(pointkey(x),x) for x in t] for t in ts]);bn=np.cross(pre[:,1]-pre[:,0],pre[:,2]-pre[:,0]);nn=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);cos=np.einsum('ij,ij->i',bn,nn)/(np.linalg.norm(bn,axis=1)*np.linalg.norm(nn,axis=1));changes=np.max(np.linalg.norm(ts-pre,axis=2),axis=1)>1e-7
assert counter(pre)==counter(baseline)
selected=[]
for i in np.flatnonzero(changes):selected.append({'actual_GLb_triangle':int(i),'normal_dot_cosine_before_after':float(cos[i]),'minimum_area_before_after_m2':float(min(np.linalg.norm(bn[i])/2,np.linalg.norm(nn[i])/2))})
report={'round':'31f','scope':'Actual31e to31f bounded sculpt including local waterline and height changes. Historical shoulder operands are not the final hull model. Required supports, real GLB manifold/connectedness and finite triangle normal change only; local intersection supplement pending.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',P/'reform-plan.json',B/'island_c.glb']},'native_objects':len(e['new']),'actual_main_triangles':len(ts),'closed_oppositely_paired_edges':True,'connected_components_vertices':components,'minimum_actual_triangle_area_m2':float(min(areas)),'actual_volume_m3':volume,'path_and17rocks_source_exact_actual_triangles_present':preserved,'actual_path_glb_counter_exact':True,'required_supports':supports,'actual_moved_vertices_present_in_GLB':len(moved),'pre_sculpt_discrete_triangles_equal_actual31e_baseline':True,'moved_triangles':int(sum(changes)),'minimum_normal_cosine_before_after_on_changed_triangles':float(min(cos[changes])),'changed_triangles_normal_reversal_count':int(sum(cos[changes]<=0)),'changed_triangles_normal_results':selected,'normal_comparison_method':'Reconstruct pre-shear positions of final discrete triangles from actual moved before/after records matched to realGLB positions. Same triangulation reconstructed to actual31e baseline. Dot sign is local normal change, not a self-intersection proof.','local_triangle_intersection_check_pending':True,'base_geometry_and_support_pass':all(s['pass'] for s in supports),'pass':None,'full_reference_accepted':False,'limits':['Historical three operands not used for final exterior or union-volume claims.','No continuum-injectivity argument used as proof of discrete mesh non-intersection.','No Blender/GPU rerun.']}
(R/'reviews/round-31f-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','path_and17rocks_source_exact_actual_triangles_present','changed_triangles_normal_results']},indent=2))
