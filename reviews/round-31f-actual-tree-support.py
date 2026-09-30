from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'actual_decoder','exec'))
helper=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(helper[helper.index('def triangles'):helper.index('road=unary_union')])
helper=(R/'reviews/round-30j-plan-independent.py').read_text(encoding='utf-8');exec(helper[helper.index('def overlay'):helper.index('rock_roofs=')])
run=R/'captures/validation_runs/lantern-island-31f-20260908T204147Z-c8f8aed2cd5f43a7be28d18f0f9ba891';side=json.loads((run/'images/night-reference.png.json').read_text());inputs=json.loads((run/'inputs.json').read_text());pinepath=R/'assets/models/pine.glb'
def find_binding(o,k):
 if isinstance(o,dict):
  if k in o:return o[k]
  for v in o.values():
   a=find_binding(v,k)
   if a is not None:return a
 if isinstance(o,list):
  for v in o:
   a=find_binding(v,k)
   if a is not None:return a
for rel in ['assets/models/pine.glb','scenes/prefabs/pine.tscn','scripts/asset_instance.gd']:
 binding=find_binding(inputs,'res://'+rel);assert binding['sha256']==sha(R/rel)
pine=glb(pinepath);pverts=np.concatenate(list(pine.values())).reshape(-1,3);zmin=float(pverts[:,2].min());foot_points=pverts[abs(pverts[:,2]-zmin)<1e-6,:2];foot=MultiPoint(foot_points).convex_hull
e=json.loads((R/'captures/lantern_island_study_31f/geometry-evidence.json').read_text());pn='island_c terrain fitted keeper paths';oldroofs=[(name,i,t) for name,o in e['old'].items() if name!=pn for i,t in upper(o)];newroofs=[(name,i,t) for name,o in e['new'].items() if name!=pn for i,t in upper(o)]
def envelope(roofs,mask):
 cells=[]
 for name,fi,t in roofs:
  poly=Polygon(t[:,:2]).intersection(mask)
  if poly.area>1e-12:cells=overlay(cells,poly,plane(t),name+':'+str(fi),maximum=True)
 return cells
def compare(mask,oldcells,newcells):
 vals=[];changed=[]
 for a,ac,al in oldcells:
  for b,bc,bl in newcells:
   g=a.intersection(b)
   if g.area<1e-12:continue
   delta=bc-ac;vs=[float(np.dot(delta,[*p,1])) for p in points_any(g)];vals.extend(vs)
   if max(abs(v) for v in vs)>1e-4:changed.append({'old_source':al,'new_source':bl,'patch_area_m2':g.area,'height_delta_min_max_m':[min(vs),max(vs)]})
 cover=unary_union([a for a,c,l in newcells]);return {'height_delta_min_max_m':[min(vals),max(vals)] if vals else None,'old_plane_changed_patches':changed,'new_unsupported_area_m2':mask.difference(cover).area}
checks=[]
for p in side['placements']:
 if p.get('kind')!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
 island=p['island'];angle=0 if island=='island_c' else 2.;origin=np.array([-3050,0,-2650]) if island=='island_c' else np.array([-2372,0,-1812]);delta=np.array(p['position'])-origin;c,s=math.cos(angle),math.sin(angle);xy=np.array([c*delta[0]-s*delta[2],-(s*delta[0]+c*delta[2])]);rot=np.array([[c,s],[-s,c]]);scale=p['scale'];fp=Polygon([xy+rot@np.array(q)*scale for q in foot.exterior.coords]);oldbase=envelope(oldroofs,fp);newbase=envelope(newroofs,fp);basecheck=compare(fp,oldbase,newbase);disk=Point(xy).buffer(2);diskcheck=compare(disk,envelope(oldroofs,disk),envelope(newroofs,disk));newvals=[float(np.dot(co,[*q,1])) for g,co,l in newbase for q in points_any(g)];center=[{'source':l,'ground_height_m':float(np.dot(co,[*xy,1])),'slope_deg':math.degrees(math.atan(float(np.linalg.norm(co[:2]))))} for g,co,l in newbase if g.buffer(1e-8).covers(Point(xy))];jumps=[]
 for i,(a,ac,al) in enumerate(newbase):
  for b,bc,bl in newbase[i+1:]:
   edge=a.boundary.intersection(b.boundary)
   if edge.length>1e-7:jumps.extend(abs(float(np.dot(ac-bc,[*q,1]))) for q in points_any(edge))
 gap=float(p['position'][1])-max(x['ground_height_m'] for x in center);record={'island':island,'xy_blender':xy.tolist(),'scale':scale,'actual_trunk_footprint_xy':list(fp.exterior.coords),'trunk_footprint_area_m2':fp.area,'old2m_disk':diskcheck,'actual_tree_base':basecheck,'new_base_surface_height_min_max_m':[min(newvals),max(newvals)],'runtime_flat_tree_bottom_to_surface_gap_min_max_m':[float(p['position'][1]+zmin*scale-max(newvals)),float(p['position'][1]+zmin*scale-min(newvals))],'actual_axis_ground':center,'runtime_axis_ground_error_m':gap,'base_internal_height_jump_m':max(jumps,default=0.),'base_support_pass':basecheck['new_unsupported_area_m2']<1e-8 and abs(gap)<.001 and max(jumps,default=0.)<1e-4,'old_base_surface_preserved_within0_1mm':max(abs(x) for x in basecheck['height_delta_min_max_m'])<1e-4};checks.append(record)
assert len(checks)==14
report={'scope':'Actual frozen pine GLB bottom vertices/prefab/runtime scale and world-zero yaw transformed to each C/D local frame. Full actual trunk footprint upper envelope from main shell+all17rocks; compare old2m disk separately. Grounding/continuity is not entire flat trunk bottom contact.','pine_asset_sha256':sha(pinepath),'bound_prefab_and_asset_script_checked':True,'native_pine_bottom_z_m':zmin,'native_bottom_polygon_xy':list(foot.exterior.coords),'native_bottom_max_radius_m':float(np.max(np.linalg.norm(foot_points,axis=1))),'actual_CD_tree_count':len(checks),'checks':checks,'old_tree_disk_surface_preserved':all(not x['old2m_disk']['old_plane_changed_patches'] for x in checks),'actual_tree_base_support':all(x['base_support_pass'] for x in checks),'all_actual_base_old_surfaces_preserved':all(x['old_base_surface_preserved_within0_1mm'] for x in checks)}
(R/'reviews/round-31f-actual-tree-support.json').write_text(json.dumps(report,indent=2),encoding='utf-8');p=R/'reviews/round-31f-independent-geometry.json';r=json.loads(p.read_text());r['old_tree_disk_surface_preserved']=report['old_tree_disk_surface_preserved'];r['actual_tree_base_support']=report['actual_tree_base_support'];r['actual_tree_base_report']='reviews/round-31f-actual-tree-support.json';r['base_geometry_and_support_pass']=all(x['pass'] for x in r['required_supports'] if x['region']!='current_CD_tree_axis_2m_disks') and report['actual_tree_base_support'];r['pass']=r['base_geometry_and_support_pass'] and r['local_triangle_intersections']['local_self_intersection_pass'] and r['changed_triangles_normal_reversal_count']==0;p.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps({'native_base_polygon':report['native_bottom_polygon_xy'],'base_radius':report['native_bottom_max_radius_m'],'actual_base_support':report['actual_tree_base_support'],'base_old_surface_unchanged':report['all_actual_base_old_surfaces_preserved'],'changed_disks':[{'island':x['island'],'xy':x['xy_blender'],'scale':x['scale'],'disk_delta':x['old2m_disk']['height_delta_min_max_m'],'base_delta':x['actual_tree_base']['height_delta_min_max_m'],'base_area':x['trunk_footprint_area_m2'],'axis_error':x['runtime_axis_ground_error_m']} for x in checks if x['old2m_disk']['old_plane_changed_patches']]},indent=2))
