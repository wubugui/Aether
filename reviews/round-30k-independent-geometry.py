from pathlib import Path
R=Path(__file__).resolve().parents[1]
procedure=(R/'reviews/round-30d-independent-geometry.py').read_text(encoding='utf-8').split('def exposure')[0]
procedure=procedure.replace("P=R/'captures/lantern_island_study_30d';B=R/'captures/lantern_island_study_30c'","P=R/'captures/lantern_island_study_30k';B=R/'captures/lantern_island_study_30d'")
procedure=procedure.replace("trees=unary_union([Point(p['xy']).buffer(2) for p in intake['tree_axes']])", "retained_axes=[p for p in json.loads((R/'reviews/round-30d-visible-slope-independent.json').read_text())['actual_C_D_tree_local_axes'] if min(math.dist(p,q) for q in [[14.04,-1.8],[15.12,-3.96]])>.01];trees=unary_union([Point(p).buffer(2) for p in retained_axes])")
exec(compile(procedure,'30k_actual_support','exec'))
helpers=(R/'reviews/round-30j-plan-independent.py').read_text(encoding='utf-8');exec(helpers[helpers.index('def overlay'):helpers.index('rock_roofs=')])
plan=json.loads((R/'captures/island-30k-authored-cut-plan.json').read_text());pp=json.loads((R/'reviews/round-30k-plan-independent.json').read_text());loc=json.loads((R/'reviews/round-30d-visible-slope-localization.json').read_text());all_roofs=[(name,i,t) for name,ob in e['new'].items() if name!=pn for i,t in upper(ob)]
def height(ts,xy):
 vals=[float(np.dot(plane(t),[*xy,1])) for t in ts if Polygon(t[:,:2]).buffer(1e-8).covers(Point(xy))];return max(vals) if vals else None
targets=[]
for s,pred in zip(loc['samples'],pp['six_visible_target_predicted_depths']):
 xy=s['hit_blender_xyz'][:2];oz=height(og,xy);nz=height(ng,xy);depth=oz-nz;error=depth-pred['predicted_cut_depth_m'];assert abs(error)<1e-4;targets.append({'pixel30d':s['pixel'],'xy':xy,'old_ground_z_m':oz,'actual30k_ground_z_m':nz,'actual_cut_depth_m':depth,'difference_from_plan_m':error})
treechecks=[]
for relocation in plan['tree_relocations']:
 xy=relocation['new_xy'];disk=Point(xy).buffer(.3,resolution=64);cells=[]
 for name,i,t in all_roofs:
  poly=Polygon(t[:,:2]).intersection(disk)
  if poly.area>1e-12:cells=overlay(cells,poly,plane(t),f'{name}_face_{i}',maximum=True)
 coverage=unary_union([g for g,c,l in cells]);missing=disk.difference(coverage).area;assert missing<1e-8;values=[float(np.dot(c,[*p,1])) for g,c,l in cells for p in points_any(g)];center=[{'source':l,'z_m':float(np.dot(c,[*xy,1])),'slope_deg':math.degrees(math.atan(float(np.linalg.norm(c[:2]))))} for g,c,l in cells if g.buffer(1e-8).covers(Point(xy))];jumps=[]
 for i,(a,ac,al) in enumerate(cells):
  for b,bc,bl in cells[i+1:]:
   shared=a.boundary.intersection(b.boundary)
   if shared.length<1e-7:continue
   jumps.extend(abs(float(np.dot(ac-bc,[*p,1]))) for p in points_any(shared))
 jump=max(jumps,default=0.);assert jump<1e-4;treechecks.append({'new_blender_xy':xy,'native_instance_scale':relocation['scale'],'trunk_disk_radius_m':.3,'supported_area_m2':coverage.intersection(disk).area,'unsupported_area_m2':missing,'actual_center_upper_surface':center,'actual_upper_envelope_height_min_max_m':[min(values),max(values)],'max_upper_envelope_slope_deg':max(math.degrees(math.atan(float(np.linalg.norm(c[:2])))) for g,c,l in cells),'max_internal_height_jump_m':jump,'includes_all17_retained_rocks':True})
report={'round':'30k','scope':'Actual30k GLB versus30d; source triangles match, closed shell, road/pad plus five retained C/D tree disks preserved. Two relocated trees use actual all17rock+main upper envelope at radius0.3m, not old2m frozen disks.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',B/'island_c.glb',R/'captures/island-30k-authored-cut-plan.json']},'native_objects':len(e['new']),'actual_main_triangles':len(ts),'source_native_main_matches_actual_glb':True,'actual_glb_edges_oppositely_paired_at_1e_5m':True,'actual_min_triangle_area_m2':float(min(areas)),'actual_main_signed_volume_m3':volume,'path_and17rocks_source_exact_and_actual_triangles_present':preserved,'actual_path_counter_exact':True,'required_retained_supports':supports,'retained_tree_axes_local_CD':retained_axes,'six_actual_target_depths':targets,'two_relocated_tree_supports':treechecks,'pass':all(r['pass'] for r in supports),'full_reference_accepted':False,'limits':['Tree relocation must also appear in actual runtime sidecars, checked separately by root.','Tree support geometry is continuous; slopes are reported without inventing an unconditional species/model slope threshold.','No exhaustive self-intersection, walking, or GPU visual acceptance from geometry alone.']}
(R/'reviews/round-30k-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','path_and17rocks_source_exact_and_actual_triangles_present','retained_tree_axes_local_CD']},indent=2))
