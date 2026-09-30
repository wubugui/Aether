from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'helpers','exec'))
from shapely.geometry import mapping
from shapely.strtree import STRtree
helper=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(helper[helper.index('def triangles'):helper.index('road=unary_union')])
P=R/'captures/island-30i-authored-cut-plan.json';plan=json.loads(P.read_text());e=json.loads((R/'captures/lantern_island_study_30d/geometry-evidence.json').read_text());tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';ground=upper(e['new'][tn]);gp=[Polygon(t[:,:2]) for _,t in ground];gc=[plane(t) for _,t in ground];index=STRtree(gp)
road=unary_union([Polygon(t[:,:2]) for _,t in upper(e['new'][pn])]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']]);treeinfo=json.loads((R/'reviews/round-30i-form-intake.json').read_text())['actual_C_tree_groups'];axes=json.loads((R/'reviews/round-30d-visible-slope-independent.json').read_text())['actual_C_D_tree_local_axes'];masks={'actual_road':road,'expanded_pads':pads,'all_actual_CD_tree_axis_2m_disks':unary_union([Point(p).buffer(2) for p in axes])};rows=[];cuttris=[]
for c in plan['components']:
 v=np.array(c['actual_lower_vertices']);ts=v[c['actual_lower_triangles']];assert len(v)==9 and len(ts)==8;assert all(np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-9 for t in ts);cuttris.append(ts);regions={}
 for name,mask in masks.items():
  overlaps=[];cutparts=[];details=[];depths=[];alldeltas=[]
  for ci,t in enumerate(ts):
   fp=plane(t);foot=Polygon(t[:,:2]).intersection(mask)
   if foot.is_empty:continue
   for j in index.query(foot):
    patch=foot.intersection(gp[j])
    if patch.area<1e-10:continue
    overlaps.append(patch);delta=gc[j]-fp;alldeltas.extend(float(np.dot(delta,[*xy,1])) for xy in coords(patch));cut=patch.intersection(halfplane(delta-[0,0,.0001]))
    if cut.area<1e-10:continue
    values=[float(np.dot(delta,[*xy,1])) for xy in coords(cut)];depths.extend(values);cutparts.append(cut);details.append({'source30d_face':ground[j][0],'cutter_bottom_face':ci,'cut_projection_area_m2':cut.area,'cut_depth_min_max_m':[min(values),max(values)],'cut_projection':mapping(cut)})
  regions[name]={'support_footprint_overlap_m2':unary_union(overlaps).area,'actual_predicted_support_cut_projection_m2':unary_union(cutparts).area,'max_predicted_cut_depth_m':max(depths) if depths else 0.,'old_ground_minus_bottom_min_max_over_entire_overlap_m':[min(alldeltas),max(alldeltas)] if alldeltas else None,'cut_patches':details}
 rows.append({'component':c['name'],'nine_vertices_eight_upward_triangles':True,'protection_linear_height_intersections':regions})
def height(ts,xy):
 values=[]
 for t in ts:
  if Polygon(t[:,:2]).buffer(1e-8).covers(Point(xy)):values.append(float(np.dot(plane(t),[*xy,1])))
 return max(values) if values else None
treechecks=[]
for tree in treeinfo:
 xy=tree['local_blender_xy'];oz=height([t for _,t in ground],xy);floors=[{'component':c['name'],'bottom_z_m':height(ts,xy)} for c,ts in zip(plan['components'],cuttris)];nz=min([oz]+[r['bottom_z_m'] for r in floors if r['bottom_z_m'] is not None]);mask=Point(xy).buffer(2);patches=[];values=[]
 for ts in cuttris:
  for t in ts:
   foot=Polygon(t[:,:2]).intersection(mask);fp=plane(t)
   if foot.is_empty:continue
   for j in index.query(foot):
    delta=gc[j]-fp;cut=foot.intersection(gp[j]).intersection(halfplane(delta-[0,0,.0001]))
    if cut.area<1e-10:continue
    patches.append(cut);values.extend(float(np.dot(delta,[*xy,1])) for xy in coords(cut))
 treechecks.append({'local_C_blender_xy':xy,'instance_scale':tree['native_instance_scale'],'old_axis_ground_z_m':oz,'predicted_axis_ground_z_m':nz,'axis_height_drop_m':oz-nz,'disk_cut_area_m2':unary_union(patches).area,'max_disk_cut_depth_m':max(values) if values else 0.,'component_floor_at_axis':floors,'axis_requires_refit':oz-nz>1e-4,'old_2m_disk_no_longer_preserved':unary_union(patches).area>1e-5})
target=[]
for s in json.loads((R/'reviews/round-30d-visible-slope-localization.json').read_text())['samples']:
 xy=s['hit_blender_xyz'][:2];oz=height([t for _,t in ground],xy);floor=[height(ts,xy) for ts in cuttris];nz=min([oz]+[z for z in floor if z is not None]);target.append({'pixel30d':s['pixel'],'xy':xy,'old_ground_z_m':oz,'predicted_cut_depth_m':oz-nz})
report={'round':'30i_plan','source_plan_sha256':sha(P),'scope':'Exact linear height clipping of24 planned bottom triangles against actual30d support triangles. Plan only, not finalBoolean/GPU acceptance.','components':rows,'tree_axes_and_disks':treechecks,'six_visible_target_predicted_depths':target,'road_pad_true_cut_free':all(r['protection_linear_height_intersections'][m]['actual_predicted_support_cut_projection_m2']<1e-5 for r in rows for m in ['actual_road','expanded_pads']),'limits':['Trees are allowed to refit/relocate; changed old2m disks are reported rather than automatic user-constraint failure.','C exact axes used for per-tree localization, union masks also include actualD roundoff positions.','FutureBoolean output can differ numerically; actual GLB support and depths must be checked before GPU.']}
(R/'reviews/round-30i-plan-independent.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'road_pad_true_cut_free':report['road_pad_true_cut_free'],'component_summary':[{'component':r['component'],'regions':{k:{a:b for a,b in v.items() if a!='cut_patches'} for k,v in r['protection_linear_height_intersections'].items()}} for r in rows],'affected_trees':[t for t in treechecks if t['old_2m_disk_no_longer_preserved']],'six_targets':target},indent=2))
