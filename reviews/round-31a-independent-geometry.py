from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30d-independent-geometry.py').read_text(encoding='utf-8').split('def exposure')[0].replace("P=R/'captures/lantern_island_study_30d';B=R/'captures/lantern_island_study_30c'","P=R/'captures/lantern_island_study_31a';B=R/'captures/lantern_island_study_30k'")
src=src.replace("trees=unary_union([Point(p['xy']).buffer(2) for p in intake['tree_axes']])", "current_axes=json.loads((R/'reviews/round-30k-current-tree-axes.json').read_text())['current_C_D_tree_axes'];trees=unary_union([Point(p['local_blender_xy']).buffer(2) for p in current_axes])")
exec(compile(src,'31a_actual_required_support','exec'))
from scipy.spatial import ConvexHull
from shapely.geometry import LineString
from shapely.ops import polygonize
helper=(R/'reviews/round-30b-independent-geometry.py').read_text();exec(helper[helper.index('def section'):helper.index('levels=')])
adj=collections.defaultdict(set)
for a,b in edge:
 adj[a].add(b);adj[b].add(a)
remaining=set(adj);components=[]
while remaining:
 start=remaining.pop();stack=[start];count=0
 while stack:
  q=stack.pop();count+=1
  for nxt in adj[q]:
   if nxt in remaining:remaining.remove(nxt);stack.append(nxt)
 components.append(count)
assert len(components)==1
oldvol=float(np.sum(np.einsum('ij,ij->i',baseline[:,0],np.cross(baseline[:,1],baseline[:,2]))/6));levels=[2.137,4.137,6.137];oldsections={z:section(baseline,z) for z in levels};additions=[];footprints=[];total_operand_volume=0
assert all(s.area>0 for s in oldsections.values())
for add in e['additions']:
 ob=add['actual_operand_geometry'];v=np.array(ob['vertices']);hull=ConvexHull(v);total_operand_volume+=hull.volume;footprints.append(MultiPoint(v[:,:2]).convex_hull);tris=np.array([v[[f[0],f[j],f[j+1]]] for f in ob['polygons'] for j in range(1,len(f)-1)])
 intersections=[]
 for z in levels:
  assert min(np.min(abs(baseline[:,:,2]-z)),np.min(abs(v[:,2]-z)))>1e-5
  ss=section(tris,z);assert ss.area>0
  inter=ss.intersection(oldsections[z]);intersections.append({'z_m':z,'operand_section_area_m2':ss.area,'old_main_section_area_m2':oldsections[z].area,'overlap_area_m2':inter.area})
 assert any(s['overlap_area_m2']>1e-5 for s in intersections)
 eq=hull.equations;distance=np.einsum('tvc,pc->tvp',ts,eq[:,:3])+eq[:,3];on_plane=np.any(np.max(np.abs(distance),axis=1)<1e-4,axis=1);inside=np.max(distance,axis=(1,2))<1e-4;surface=ts[on_plane&inside];norm=np.cross(surface[:,1]-surface[:,0],surface[:,2]-surface[:,0]);sareas=np.linalg.norm(norm,axis=1)/2;tops=surface[norm[:,2]>1e-9]
 exposedarea=float(sareas.sum());assert exposedarea>0
 additions.append({'name':add['name'],'native_operand_vertices':len(v),'native_operand_faces':len(ob['polygons']),'convex_operand_volume_m3':float(hull.volume),'old_main_real_section_intersections':intersections,'actual_union_exterior_on_operand_planes_triangles':len(surface),'actual_union_exterior_on_operand_planes_3d_area_m2':exposedarea,'actual_upward_operand_exterior_3d_area_m2':float(sareas[norm[:,2]>1e-9].sum()),'actual_upward_operand_exterior_projection_area_m2':unary_union([Polygon(t[:,:2]) for t in tops]).area,'exterior_area_scope':'Actual new GLB exterior triangles on native convex operand supporting planes within0.1mm. Geometric exposed surface, not screen visibility or all broad-slab area.'})
disjoint=all(a.intersection(b).area<1e-8 for i,a in enumerate(footprints) for b in footprints[i+1:]);addedvolume=volume-oldvol;aggregate_overlap=total_operand_volume-addedvolume if disjoint else None;assert addedvolume>0 and aggregate_overlap>0
report={'round':'31a','scope':'Actual31a GLB/native union versus30k. Required road/pad/current14tree support, path17rocks, connected shell, two native operand intersection and exposed exterior only. No GPU/Blender rerun.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',P/'shoulder_operands.blend',B/'island_c.glb',R/'reviews/round-30k-current-tree-axes.json']},'native_scene_objects':len(e['new']),'actual_main_triangles':len(ts),'actual_main_closed_oppositely_paired_edges':True,'actual_main_connected_components_by_welded_position':components,'actual_min_triangle_area_m2':float(min(areas)),'old_main_volume_m3':oldvol,'new_main_volume_m3':volume,'added_union_volume_m3':addedvolume,'operand_XY_domains_disjoint':disjoint,'aggregate_actual_intersection_volume_with_old_main_m3':aggregate_overlap,'intersection_volume_method':'For disjoint operand projections, sum operand convex volumes minus actual main-union volume gain. Individual sampled section intersections also shown.','path_and17rocks_source_exact_actual_triangles_present':preserved,'actual_path_counter_exact':True,'required_supports':supports,'additions':additions,'pass':all(r['pass'] for r in supports),'full_reference_accepted':False,'limits':['Native operand scene existence/hash is recorded; Blender re-open by root is separate.','Positive solid overlap and exposed geometric area are not visual acceptance.','No exhaustive triangle-level self-intersection or whole walking claim.','Individual/coplanar subset areas do not estimate all visible slab area.']}
(R/'reviews/round-31a-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','path_and17rocks_source_exact_actual_triangles_present']},indent=2))
