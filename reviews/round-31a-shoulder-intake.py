from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'helpers','exec'))
from shapely.strtree import STRtree
helper=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(helper[helper.index('def triangles'):helper.index('road=unary_union')])
P=R/'captures/lantern_island_study_30k';e=json.loads((P/'geometry-evidence.json').read_text());tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';main=upper(e['new'][tn]);gp=[Polygon(t[:,:2]) for _,t in main];gc=[plane(t) for _,t in main];index=STRtree(gp);road=unary_union([Polygon(t[:,:2]) for _,t in upper(e['new'][pn])]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']]);axespath=R/'reviews/round-30k-current-tree-axes.json';ax=json.loads(axespath.read_text());axes=ax['current_C_D_tree_axes'];assert len(axes)==14
side=R/'captures/validation_runs'/ax['run_id']/'images/night-reference.png.json';assert sha(side)==ax['actual_sidecar_sha256'];trees=unary_union([Point(t['local_blender_xy']).buffer(2) for t in axes]);masks={'road':road,'expanded_pads':pads,'current14_tree_axis_2m_disks':trees};reports=[]
def height(xy):
 vals=[]
 for j in index.query(Point(xy)):
  if gp[j].buffer(1e-8).covers(Point(xy)):vals.append(float(np.dot(gc[j],[*xy,1])))
 return max(vals) if vals else None
for center in [[-12,-20],[3,-14]]:
 point=Point(center);row={'center_blender_xy':center,'actual30k_main_surface_z_m':height(center),'proposed7_to8m_top_rise_over_center_m':[7-height(center),8-height(center)],'center_horizontal_distances_m':{name:point.distance(mask) for name,mask in masks.items()},'diagnostic_probe_disks':[]}
 for radius in [3.,4.]:
  disk=point.buffer(radius);zones={}
  for name,mask in masks.items():
   region=disk.intersection(mask);vals=[];faces=[]
   for j in index.query(region):
    patch=region.intersection(gp[j])
    if patch.area<1e-10:continue
    vals.extend(float(np.dot(gc[j],[*xy,1])) for xy in coords(patch));faces.append(main[j][0])
   zones[name]={'projection_overlap_m2':region.area,'actual_support_z_min_max_m':[min(vals),max(vals)] if vals else None,'source_faces':faces,'nominal_8m_top_below_lowest_support_m':min(vals)-8 if vals else None}
  row['diagnostic_probe_disks'].append({'radius_m':radius,'not_a_final_shoulder_footprint':True,'protection':zones})
 reports.append(row)
report={'round':'31a_intake','source_geometry_sha256':sha(P/'geometry-evidence.json'),'ray_evidence':'reviews/round-31a-visible-slope-independent.json','current_tree_axes_file':str(axespath.relative_to(R)),'current_tree_axes_sha256':sha(axespath),'current_tree_axes_verified_against_actual_night_sidecar_sha':True,'probes':reports,'interpretation':['These radius3/4m disks are explicitly chosen diagnostic neighborhoods, not the eventual union solid footprint.','A positive support-projection overlap is not automatically interference: exact proposed upper surfaces versus current support heights decide.','A zero-overlap center/small probe does not establish a larger or oriented shoulder is safe.','Individual/near-coplanar patch areas do not quantify the entire visually broad slope.','Actual new union solid must overlap old main volume, remain a single closed exterior, and retain support/path17rocks; new exposed roof and GPU silhouette are separate checks.'],'full_reference_accepted':False}
(R/'reviews/round-31a-shoulder-intake.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(reports,indent=2))
