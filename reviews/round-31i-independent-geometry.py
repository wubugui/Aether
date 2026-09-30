from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30d-independent-geometry.py').read_text(encoding='utf-8').split('def exposure')[0].replace("P=R/'captures/lantern_island_study_30d';B=R/'captures/lantern_island_study_30c'","P=R/'captures/lantern_island_study_31i';B=R/'captures/lantern_island_study_31h'")
src=src.replace("masks={'road_footprint':road,'padded_sites':pads,'current_CD_tree_axis_2m_disks':trees}","masks={'road_footprint':road,'padded_sites':pads}")
exec(compile(src,'31i_actual_support','exec'))
adj=collections.defaultdict(set)
for a,b in edge:adj[a].add(b);adj[b].add(a)
remaining=set(adj);components=[]
while remaining:
 stack=[remaining.pop()];count=0
 while stack:
  a=stack.pop();count+=1
  for b in adj[a]:
   if b in remaining:remaining.remove(b);stack.append(b)
 components.append(count)
assert len(components)==1
plan=json.loads((P/'reform-plan.json').read_text());newpoints={pointkey(x) for t in ts for x in t};moved=[]
for a in plan['actual_moved_vertices']:
 assert pointkey(a['after']) in newpoints;moved.append({'source_index':a['index'],'before':a['before'],'after':a['after'],'displacement_m':float(np.linalg.norm(np.array(a['after'])-a['before']))})
for a in plan['actual_band_split_points']:assert pointkey(a['after']) in newpoints
report={'round':'31i','scope':'Actual31h to31i shared-edge shelf creation and5control changes; no old same-topology normal inversion and no31g deletion-count reuse.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',P/'reform-plan.json',B/'island_c.glb']},'native_objects':len(e['new']),'actual_main_triangles':len(ts),'closed_oppositely_paired_edges':True,'connected_components_vertices':components,'minimum_actual_triangle_area_m2':float(min(areas)),'actual_volume_m3':volume,'path_and17rocks_source_exact_actual_triangles_present':preserved,'actual_path_glb_counter_exact':True,'required_supports':supports,'actual_moved_vertices_present_in_GLB':moved,'actual_new_split_vertices_present_in_GLB':4,'base_geometry_and_support_pass':all(x['pass'] for x in supports),'local_triangle_intersection_check_pending':True,'actual_tree_upper_envelope_pending':True,'shoulder_shared_edge_check_pending':True,'pass':None,'full_reference_accepted':False,'limits':['Actual tree upper envelope and shelf adjacency supplements required before final pass.','No same-topology normal-cosine assertion after edge splits and BEAUTY triangulation.','Native shape names/counts do not establish visual short-shoulder success.']}
(R/'reviews/round-31i-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','path_and17rocks_source_exact_actual_triangles_present']},indent=2))
