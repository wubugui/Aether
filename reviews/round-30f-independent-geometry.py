from pathlib import Path
# Reuse the validated decoder and bounded support-check procedure, applied to
# this new30f asset against30d. Do not execute30d exposure/full-scene checks.
R=Path(__file__).resolve().parents[1]
procedure=(R/'reviews/round-30d-independent-geometry.py').read_text(encoding='utf-8').split('exposed=[]')[0]
procedure=procedure.replace("P=R/'captures/lantern_island_study_30d';B=R/'captures/lantern_island_study_30c'", "P=R/'captures/lantern_island_study_30f';B=R/'captures/lantern_island_study_30d'")
# Use30d current tree axes from the six-pixel review, not older30c axes.
procedure=procedure.replace("trees=unary_union([Point(p['xy']).buffer(2) for p in intake['tree_axes']])", "trees=unary_union([Point(p).buffer(2) for p in json.loads((R/'reviews/round-30d-visible-slope-independent.json').read_text())['actual_C_D_tree_local_axes']])")
exec(compile(procedure,'bounded_30f_geometry','exec'))
plan=json.loads((P/'proportion-plan.json').read_text());loc=json.loads((R/'reviews/round-30d-visible-slope-localization.json').read_text());ep=json.loads((R/'captures/island-30e-faceted-cut-plan.json').read_text());protect=unary_union(list(masks.values()))
def height(ts,xy):
 point=Point(xy);values=[]
 for t in ts:
  poly=Polygon(t[:,:2])
  if poly.area>1e-10 and poly.buffer(1e-8).covers(point):values.append(float(np.dot(plane(t),[*xy,1])))
 return max(values) if values else None
cutters=[];cts=[]
for i,c in enumerate(e['cutbacks']):
 assert c['polygon']==ep['components'][i]['polygon'] and c['holes']==ep['components'][i]['holes']
 verts=np.array(c['actual_lower_vertices']);ct=verts[c['actual_lower_triangles']];cts.append(ct);coverage=unary_union([Polygon(t[:,:2]) for t in ct]);expected=Polygon(c['polygon'],c['holes']);difference=coverage.symmetric_difference(expected).area;gap=coverage.distance(protect)
 assert difference<1e-4 and gap>=.35
 cutters.append({'name':c['name'],'actual_bottom_vertices':len(verts),'actual_bottom_triangles':len(ct),'actual_projection_area_m2':coverage.area,'projection_difference_from_validated30e_plan_m2':difference,'actual_bottom_projection_min_protection_gap_m':gap,'actual_bottom_z_min_max_m':[float(verts[:,2].min()),float(verts[:,2].max())]})
targets=[]
for s in loc['samples']:
 xy=s['hit_blender_xyz'][:2];oldz=height(og,xy);newz=height(ng,xy);floors=[{'component':c['name'],'actual_linear_bottom_height_m':height(ct,xy)} for c,ct in zip(e['cutbacks'],cts)];expected=min([oldz]+[r['actual_linear_bottom_height_m'] for r in floors if r['actual_linear_bottom_height_m'] is not None]);error=None if newz is None else newz-expected;assert error is not None and abs(error)<1e-4
 targets.append({'pixel_30d':s['pixel'],'old_source_face':s['source']['face'],'xy':xy,'old_actual_main_surface_z_m':oldz,'new_actual_main_surface_z_m':newz,'actual_vertical_cut_depth_m':oldz-newz,'native_cutter_bottoms':floors,'expected_boolean_surface_z_m':expected,'actual_minus_expected_m':error})
report={'round':'30f','scope':'Actual30f GLB versus30d; required support masks, closed native shell, actual faceted cutter coverage, and six previously visible target XY heights only.30e failed model is not accepted or used as an asset baseline.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',B/'island_c.glb',R/'captures/island-30e-faceted-cut-plan.json']},'joint_builder_changes':{'boolean_solver':plan['boolean_solver'],'lower_floor_clamped_to_source':plan['lower_floor_clamped_to_source'],'causality':'Two simultaneous changes; success cannot isolate a single failure cause.'},'native_objects':len(e['new']),'actual_glb_terrain_triangle_count':len(ts),'source_terrain_all_triangles_equal_actual_glb':True,'actual_glb_closed_oppositely_paired_edges_at_1e_5m':True,'actual_glb_min_triangle_area_m2':float(min(areas)),'actual_glb_volume_m3':volume,'path_and_17_rocks_source_exact_actual_triangles_present':preserved,'actual_path_glb_counter_exact':True,'required_support_surfaces':supports,'actual_native_cutter_bottoms':cutters,'six_target_actual_cut_depths':targets,'pass':all(x['pass'] for x in supports),'full_reference_accepted':False,'limits':['New runtime placements/footings are separate root evidence. Support masks here use latest30d actual C/D axes.','Six-point depths prove actual change at those ground coordinates, not new camera visibility or complete visual quality.','No full3D self-intersection/walking proof or GPU run by reviewer.','Failed30e topology remains failed;30f joint changes do not establish a unique root cause.']}
(R/'reviews/round-30f-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','path_and_17_rocks_source_exact_actual_triangles_present']},indent=2))
