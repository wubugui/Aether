from pathlib import Path
from shapely.prepared import prep
from shapely.strtree import STRtree
R=Path(__file__).resolve().parents[1]
s=(R/'reviews/round-33a-rightcoast-independent-geometry.py').read_text(encoding='utf-8').split('passed=')[0]
s=s.replace('rightcoast_study_33a','rightcoast_study_33b').replace('round-33a-reopened-source','round-33b-reopened-source')
s=s.replace('frozen=shape(plan', 'pmask=prep(mask);frozen=shape(plan')
s=s.replace('cut=poly.intersection(mask)','if not pmask.intersects(poly):continue\n  cut=poly.intersection(mask)')
exec(compile(s,'33b_actual_geometry_increment','exec'))
def coords(p):
 if p.is_empty:return []
 if p.geom_type=='Polygon':return list(p.exterior.coords)+[q for ring in p.interiors for q in ring.coords]
 if hasattr(p,'geoms'):return [q for sub in p.geoms for q in coords(sub)]
 return list(p.coords)
def plane(t):return np.linalg.solve(np.column_stack([t[:,:2],np.ones(3)]),t[:,2])
# Occupied ground is old main upper shell, independently retain its full clipped
# footprint and check potential new surfaces against that ground, not buried Z.
roofs=[];coefs=[];clipped=[];groundz=[]
for name,i,t in oldts:
 if not name.startswith('Mainland') or np.cross(t[1]-t[0],t[2]-t[0])[2]<=1e-9:continue
 p=Polygon(t[:,:2])
 if not pmask.intersects(p):continue
 cut=p.intersection(mask)
 if cut.area<=1e-10:continue
 roofs.append(p);coefs.append(plane(t));clipped.append(cut);groundz.extend(float(np.dot(coefs[-1],[*q,1])) for q in coords(cut))
roofunion=unary_union(clipped);tree=STRtree(roofs);overlaparea=sum(p.area for p in clipped)-roofunion.area
old_support_changes=[r for r in oldloc['changed_triangles_over_occupied'] if np.cross(np.array(r['vertices'])[1]-np.array(r['vertices'])[0],np.array(r['vertices'])[2]-np.array(r['vertices'])[0])[2]>1e-9 and max(v[2] for v in r['vertices'])>0]
checks=[]
for row in newloc['changed_triangles_over_occupied']:
 t=np.array(row['vertices']);poly=shape(row['occupied_intersection']);c=plane(t);vals=[];cover=[]
 for j in tree.query(poly):
  cut=poly.intersection(roofs[j])
  if cut.area<=1e-10:continue
  cover.append(cut);vals.extend(float(np.dot(c-coefs[j],[*q,1])) for q in coords(cut))
 uncovered=poly.difference(unary_union(cover)).area
 checks.append(dict(object=row['object'],actual_triangle=row['actual_triangle'],occupied_intersection_area_m2=poly.area,old_main_surface_uncovered_intersection_area_m2=uncovered,new_surface_minus_old_main_surface_min_max_m=[min(vals),max(vals)] if vals else None,new_surface_rises_above_original_support=bool(vals and max(vals)>1e-5)))
intrusions=[c for c in checks if c['new_surface_rises_above_original_support'] or c['old_main_surface_uncovered_intersection_area_m2']>1e-8]
vertical_risks=[]
from shapely.geometry import MultiPoint
for name,i,t in newts:
 if key(t) in oc or Polygon(t[:,:2]).area>1e-12 or max(t[:,2])<min(groundz):continue
 p=MultiPoint(t[:,:2]).convex_hull
 if pmask.intersects(p) and p.intersection(mask).length>1e-8:vertical_risks.append(dict(object=name,actual_triangle=i,vertices=t.tolist()))
passidentity=identity['actual_glb_vs_reopened_source_missing_triangles']==0 and identity['actual_glb_vs_reopened_source_extra_triangles']==0
passdomains=all(d['outside_plan_occupied_area_m2']<1e-8 and d['outside_frozen_face_region_area_m2']<1e-8 for d in domains)
supportpass=not old_support_changes and not intrusions and not vertical_risks and mask.difference(roofunion).area<1e-7 and abs(overlaparea)<1e-7
passed=new['native_closed_positive_pass'] and passidentity and passdomains and supportpass and not flips and all(r['polygon_vertex_sets_preserved'] and r['frozen_vertex_max_displacement_m']==0 for r in rows)
report=dict(round='33b',scope='Bounded actual source/GLB check of complete9foundations/922paving support and new external intrusion; buried projection changes are permitted when proven below old ground.',identity=identity,occupied_report_sha256_matches_plan=sha('reviews/round-33-occupied-regions.json')==plan['actual_occupied_report_sha256'],native_closed_positive_pass=new['native_closed_positive_pass'],native_parts=new['native'],object_increments=rows,domain_containment=domains,planned_occupied_domain_complete=passdomains,old_actual_surface_over_occupied=oldloc,new_actual_surface_over_occupied=newloc,actual_old_upward_above_water_support_changes=old_support_changes,changed_new_surface_vs_original_ground=checks,actual_support_intrusions=intrusions,changed_vertical_projected_line_risks=vertical_risks,old_main_upper_ground_coverage=dict(area_m2=roofunion.area,missing_actual_occupied_area_m2=mask.difference(roofunion).area,overlapping_surface_projected_area_m2=overlaparea,height_min_max_m=[min(groundz),max(groundz)]),actual_support_geometry_preserved=supportpass,xy_orientation_reversals=flips,minimum_signed_current_vs_old_xy_area_ratio=min(ratios),pass_result=passed,full_reference_accepted=False,all_reference_goal_complete=False,limits=['Original positive-Z upward support faces must remain geometrically identical. Changed buried/downward faces are reported and their complete clipped linear heights compared to the original unique main upper surface; they are not automatically failures.','ActualGLB triangles match native source; noXYsignflip does not prove arbitrary global3D self-intersection absent.','Complete projection uses the actual9foundation/922paving domains, not originalwrong-yaw33apads. Frozenvertex count is supplemental only.','No newGPU, fullterrain/pathwalking or proceduralworldscatter checks. Trees can reground; prior26b contact evidence remains limited to its original scope.'])
(R/'reviews/round-33b-rightcoast-independent-geometry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(pass_result=passed,identity=identity,domainpass=passdomains,old_positive_support_changes=len(old_support_changes),changed_new_surfaces=len(checks),intrusions=intrusions[:3],vertical_risks=len(vertical_risks),ground=report['old_main_upper_ground_coverage'],minxy=min(ratios),flips=len(flips)),indent=2))
