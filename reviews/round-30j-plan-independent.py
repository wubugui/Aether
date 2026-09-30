from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30i-plan-independent.py').read_text(encoding='utf-8').replace('island-30i-authored-cut-plan.json','island-30j-authored-cut-plan.json').replace('round-30i-plan-independent.json','round-30j-plan-independent.json').replace("'round':'30i_plan'","'round':'30j_plan'")
exec(compile(src,'30j_linear_plan','exec'))
# Build actual predicted upper envelope inside each small trunk-foot disk:
# Boolean minima for main-shell cuts followed by maxima with all17 old rocks.
def overlay(cells,poly,co,label,maximum=False):
 result=[];oldcover=unary_union([g for g,c,l in cells])
 for g,c,l in cells:
  overlap=g.intersection(poly)
  if overlap.area<1e-12:result.append((g,c,l));continue
  difference=(co-c) if maximum else (c-co);take=overlap.intersection(halfplane(difference))
  rest=g.difference(take)
  if rest.area>1e-12:result.append((rest,c,l))
  if take.area>1e-12:result.append((take,co,label))
 if maximum:
  uncovered=poly.difference(oldcover)
  if uncovered.area>1e-12:result.append((uncovered,co,label))
 return result
def points_any(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return list(g.exterior.coords)
 if hasattr(g,'geoms'):return [p for sub in g.geoms for p in points_any(sub)]
 return list(g.coords)
rock_roofs=[(name,i,t) for name,o in e['new'].items() if name not in [tn,pn] for i,t in upper(o)]
checks=[]
tree_cases=[dict(old_xy=t['local_blender_xy'],new_xy=t['local_blender_xy'],scale=t['native_instance_scale'],case='existing_old_axis') for t in treeinfo]+[dict(t,case='proposed_new_axis') for t in plan['tree_relocations']]
for relocation in tree_cases:
 xy=relocation['new_xy'];disk=Point(xy).buffer(.3,resolution=64);cells=[]
 for fi,t in ground:
  poly=Polygon(t[:,:2]).intersection(disk)
  if poly.area>1e-12:cells=overlay(cells,poly,plane(t),f'main30d_face_{fi}',maximum=True)
 for comp,ts in zip(plan['components'],cuttris):
  for i,t in enumerate(ts):
   poly=Polygon(t[:,:2]).intersection(disk)
   if poly.area>1e-12:cells=overlay(cells,poly,plane(t),f'planned_main_{comp["name"]}_bottom_{i}')
 for name,i,t in rock_roofs:
  poly=Polygon(t[:,:2]).intersection(disk)
  if poly.area>1e-12:cells=overlay(cells,poly,plane(t),f'{name}_face_{i}',maximum=True)
 coverage=unary_union([p for p,c,l in cells]);allheights=[float(np.dot(c,[*p,1])) for g,c,l in cells for p in points_any(g)];owners=collections.defaultdict(float)
 for g,c,l in cells:owners[l]+=g.area
 center=[{'surface':l,'height_m':float(np.dot(c,[*xy,1])),'slope_deg':math.degrees(math.atan(float(np.linalg.norm(c[:2])))),'normal_up':(np.array([-c[0],-c[1],1])/np.linalg.norm([-c[0],-c[1],1])).tolist()} for g,c,l in cells if g.buffer(1e-8).covers(Point(xy))]
 jumps=[]
 for i,(a,ac,al) in enumerate(cells):
  for b,bc,bl in cells[i+1:]:
   shared=a.boundary.intersection(b.boundary)
   if shared.length<1e-7:continue
   values=[abs(float(np.dot(ac-bc,[*p,1]))) for p in points_any(shared)]
   if values:jumps.append({'a':al,'b':bl,'shared_length_m':shared.length,'max_height_jump_m':max(values)})
 checks.append({'case':relocation['case'],'new_blender_xy':xy,'old_blender_xy':relocation['old_xy'],'instance_scale':relocation['scale'],'radius_m':.3,'expected_disk_area_m2':disk.area,'covered_area_m2':coverage.intersection(disk).area,'unsupported_area_m2':disk.difference(coverage).area,'center_upper_surface':center,'upper_envelope_height_min_max_m':[min(allheights),max(allheights)],'upper_envelope_max_slope_deg':max(math.degrees(math.atan(float(np.linalg.norm(c[:2])))) for g,c,l in cells),'max_internal_height_jump_m':max([j['max_height_jump_m'] for j in jumps],default=0.),'surface_projection_owners':dict(owners),'internal_boundaries':jumps,'note':'Includes true17 retained rock meshes and predicted main-shell after planned cuts. Slope/height range are measured; no invented universal tree-slope acceptance threshold.'})
out=R/'reviews/round-30j-plan-independent.json';report=json.loads(out.read_text());report['new_tree_trunk_radius_0_3m_top_envelope_support']=[c for c in checks if c['case']=='proposed_new_axis'];report['old_tree_trunk_radius_0_3m_top_envelope_support']=[c for c in checks if c['case']=='existing_old_axis'];report['tree_support_method']='0.3m disk clipped actual30d main upper triangles, lowered by24 planned cutter triangles; maximum envelope with all17 actual unchanged rock upward triangles. Records linear slopes and height continuity at exposed cell boundaries.';report['limits'].append('Tree support is predicted from plan plus actual retained rocks; final GLB and actual runtime grounding remain required.');out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'trunk_support_summary':[{'case':c['case'],'xy':c['new_blender_xy'],'center':c['center_upper_surface'],'unsupported_area':c['unsupported_area_m2']} for c in checks]},indent=2))
