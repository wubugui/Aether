from pathlib import Path
import json,struct,hashlib,math
from collections import Counter
import numpy as np
from shapely.geometry import Polygon,shape,Point,MultiPoint,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
exec((R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8'))
old=read('reviews/round-33b-reopened-source.json');new=read('reviews/round-33e-reopened-source.json');prior=read('reviews/round-33b-rightcoast-independent-geometry.json');plan=read('captures/rightcoast_study_33e/design-plan.json');domain=read('reviews/round-33d-visible-transition-domain.json');mask=shape(read('reviews/round-33-occupied-regions.json')['hard_occupied_house_and_paving_union'])
assert plan['source_sha256']==old['source_sha256']==sha(plan['source']);assert plan['domain_sha256']==sha(plan['source_domain']);assert prior['actual_support_geometry_preserved']
key=lambda t:tuple(sorted(map(tuple,t)))
def collect(d):
 rows=[]
 for name,o in d['objects'].items():
  v=np.array(o['vertices']);rows.extend((name,i,v[f]) for i,f in enumerate(o['triangles']))
 return rows
oldts,newts=collect(old),collect(new);oc=Counter(key(t) for n,i,t in oldts);nc=Counter(key(t) for n,i,t in newts);gc=Counter(key(t) for t in asset_world_triangles(R/'captures/rightcoast_study_33e/mainland_headland.glb'));removed=oc-nc;added=nc-oc
rows=[];main=plan['source_domain'];allowed=set(plan['free_vertices'])
for name,a in old['objects'].items():
 b=new['objects'][name];av,bv=np.array(a['vertices']),np.array(b['vertices']);changed=np.flatnonzero(np.any(av!=bv,axis=1));other=set(changed)-allowed if name.startswith('Mainland') else set(changed);polya=Counter(tuple(sorted(f)) for f in a['polygons']);polyb=Counter(tuple(sorted(f)) for f in b['polygons'])
 rows.append(dict(object=name,changed_vertex_count=len(changed),changed_vertex_indices=changed.tolist(),only_allowed_86_points_changed=not other,all_xy_exact=np.array_equal(av[:,:2],bv[:,:2]),max_displacement_m=float(np.linalg.norm(av-bv,axis=1).max()),old_removed_polygon_vertex_sets=sum((polya-polyb).values()),new_added_polygon_vertex_sets=sum((polyb-polya).values())))
name=next(n for n in old['objects'] if n.startswith('Mainland'));a,b=old['objects'][name],new['objects'][name];av,bv=np.array(a['vertices']),np.array(b['vertices']);kept=[dict(vertex=i,old_xyz=av[i].tolist(),new_xyz=bv[i].tolist(),exact=bool(np.array_equal(av[i],bv[i]))) for i in plan['kept_support_boundary_vertices']]
def diffs(ts,c):
 records=[];pp=[]
 for name,i,t in ts:
  if key(t) not in c:continue
  p=Polygon(t[:,:2]);foot=p if p.is_valid and p.area>1e-12 else MultiPoint(t[:,:2]).convex_hull;cut=foot.intersection(mask);normal=np.cross(t[1]-t[0],t[2]-t[0]);records.append(dict(object=name,actual_triangle=i,vertices=t.tolist(),occupied_intersection_area_m2=cut.area,occupied_line_intersection_length_m=cut.length if cut.area==0 else None,distance_to_actual_occupied_m=foot.distance(mask),normal_z=float(normal[2]/np.linalg.norm(normal))))
  if p.is_valid and p.area>1e-12:pp.append(p)
 return records,unary_union(pp)
oldchange,oldprojection=diffs(oldts,removed);newchange,newprojection=diffs(newts,added);delta=oldprojection.symmetric_difference(newprojection).area
intersections=[r for r in oldchange+newchange if r['occupied_intersection_area_m2']>1e-10 or (r['occupied_line_intersection_length_m'] or 0)>1e-8]
flips=[r for r in newchange if r['normal_z']<=0]
hitchecks=[]
for row in domain['hits']:
 xy=np.array(row['hit_blender_xyz'][:2]);candidates=[]
 for name,i,t in newts:
  if name!=row['actual_hit_face'].get('object',next(n for n in old['objects'] if n.startswith('Mainland'))):continue
  if xy[0]<t[:,0].min()-1e-9 or xy[0]>t[:,0].max()+1e-9 or xy[1]<t[:,1].min()-1e-9 or xy[1]>t[:,1].max()+1e-9:continue
  normal=np.cross(t[1]-t[0],t[2]-t[0]);p=Polygon(t[:,:2])
  if normal[2]<=1e-9 or not p.buffer(1e-10).covers(Point(xy)):continue
  co=np.linalg.solve(np.column_stack([t[:,:2],np.ones(3)]),t[:,2]);candidates.append(dict(actual_triangle=i,z=float(co@[*xy,1]),slope_degrees=math.degrees(math.acos(normal[2]/np.linalg.norm(normal)))))
 candidates.sort(key=lambda r:r['z'],reverse=True);hitchecks.append(dict(original_view=row['view'],original_pixel=row['pixel'],same_native_xy=xy.tolist(),old_hit_height=row['hit_blender_xyz'][2],old_triangle_slope_degrees=row['actual_hit_face']['slope_degrees'],new_highest_native_surface=candidates[0] if candidates else None,limitation='SameXY native height/slope check, not a new camera ray or proof of visible appearance.'))
identity=dict(source_sha256=new['source_sha256'],source_reopened_unchanged=new['source_file_unchanged'],actual_glb_sha256=sha('captures/rightcoast_study_33e/mainland_headland.glb'),actual_glb_triangle_count=sum(gc.values()),missing_export_triangles=sum((nc-gc).values()),extra_export_triangles=sum((gc-nc).values()),immediate33b_source_matches_independent_reopen=True)
support=not intersections and all(r['all_xy_exact'] and r['only_allowed_86_points_changed'] for r in rows) and all(k['exact'] for k in kept)
passed=support and new['native_closed_positive_pass'] and identity['missing_export_triangles']==identity['extra_export_triangles']==0 and delta<1e-8 and not flips
report=dict(round='33e',scope='Bounded86point native smoothing and innerdiagonal reordering from33b. Actual triangle-coordinate differences, no same-topology assumption and no repeatfulloccupied/GPUscan.',identity=identity,native_closed_positive_pass=new['native_closed_positive_pass'],native_parts=new['native'],object_increments=rows,three_support_boundary_vertices=kept,removed_old_triangle_geometry_count=sum(removed.values()),added_new_triangle_geometry_count=sum(added.values()),removed_old_triangles=oldchange,added_new_triangles=newchange,actual_changed_region_old_projection=mapping(oldprojection),actual_changed_region_new_projection=mapping(newprojection),actual_changed_region_old_projected_area_m2=oldprojection.area,actual_changed_region_new_projected_area_m2=newprojection.area,old_new_projection_symmetric_difference_area_m2=delta,changed_actual_support_intersections=intersections,minimum_changed_face_distance_to_actual_occupied_m=min(r['distance_to_actual_occupied_m'] for r in oldchange+newchange),new_changed_nonupward_triangles=flips,can_inherit_33b_actual_complete_support=support,same_xy_four_source_hit_diagnostics=hitchecks,pass_result=passed,full_reference_accepted=False,all_reference_goal_complete=False,limits=['Same XY vertex set alone doesnot prove retriangulated domain preservation; actual old/new changed triangle projection unions are explicitly compared, and every removed/added face is intersected withactualhouse/pavingdomain.','Actualchangedregion includesallneighborfacesincidentto86vertices, notjusttheoriginal94one-ringtriangles.','All11rocks exact and33bsource basis means33d bayretopology isnot included in33e. No claim the two candidates are already merged.','Positiveupward changedtriangles andclosedmesh are not an exhaustive3Dselfintersection test. Actualgroundsupport is inherited only outside the verifiedchangedregion.','SameXYheight/slope diagnostics cannot substitute for actualpixel/GPU/art review.'])
(R/'reviews/round-33e-rightcoast-independent-geometry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(pass_result=passed,identity=identity,changed_count=sum(r['changed_vertex_count'] for r in rows),kept=kept,oldtri=sum(removed.values()),newtri=sum(added.values()),oldarea=oldprojection.area,newarea=newprojection.area,xydiff=delta,intersections=len(intersections),min_distance=report['minimum_changed_face_distance_to_actual_occupied_m'],nonup=len(flips),hitchecks=hitchecks),indent=2))
