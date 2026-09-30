from pathlib import Path
import json,struct,hashlib,math,ast
from collections import Counter
import numpy as np
from shapely.geometry import Polygon,shape,mapping,box,MultiPoint
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
exec((R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8'))
h=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(h[h.index('def plane'):h.index('road=unary_union')])
h=(R/'reviews/round-30j-plan-independent.py').read_text(encoding='utf-8');exec(h[h.index('def overlay'):h.index('rock_roofs=')])
s=(R/'reviews/round-33c-rightcoast-independent-geometry.py').read_text(encoding='utf-8');fn=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='shore');exec(ast.get_source_segment(s,fn))
old=read('reviews/round-33b-reopened-source.json');new=read('reviews/round-33d-reopened-source.json');prior=read('reviews/round-33b-rightcoast-independent-geometry.json');plan=read('captures/rightcoast_study_33d/design-plan.json');occ=read('reviews/round-33-occupied-regions.json');mask=shape(occ['hard_occupied_house_and_paving_union']);rect=box(*read('captures/rightcoast33c-design-plan.json')['working_shore']['bounds_blender_xy']);assert rect.area==238
assert prior['actual_support_geometry_preserved'];assert plan['source_sha256']==old['source_sha256']==sha(plan['source']);assert plan['source_reopen_sha256']==sha(plan['source_reopen'])
def collect(d):
 rows=[]
 for name,o in d['objects'].items():
  vertices=np.array(o['vertices']);rows.extend((name,i,vertices[f]) for i,f in enumerate(o['triangles']))
 return rows
key=lambda t:tuple(sorted(map(tuple,t)))
oldts,newts=collect(old),collect(new);oc=Counter(key(t) for n,i,t in oldts);nc=Counter(key(t) for n,i,t in newts);removed=oc-nc;added=nc-oc;gc=Counter(key(t) for t in asset_world_triangles(R/'captures/rightcoast_study_33d/mainland_headland.glb'))
identity=dict(source_sha256=new['source_sha256'],source_reopened_unchanged=new['source_file_unchanged'],actual_glb_sha256=sha('captures/rightcoast_study_33d/mainland_headland.glb'),actual_glb_triangle_count=sum(gc.values()),reopened_native_triangle_count=len(newts),missing_export_triangles=sum((nc-gc).values()),extra_export_triangles=sum((gc-nc).values()),immediate33b_source_matches_independent_reopen=True)
def changed_info(ts,counter):
 result=[]
 for name,i,t in ts:
  if key(t) not in counter:continue
  p=Polygon(t[:,:2]);foot=p if p.is_valid and p.area>1e-12 else MultiPoint(t[:,:2]).convex_hull;cut=foot.intersection(mask);n=np.cross(t[1]-t[0],t[2]-t[0]);result.append(dict(object=name,actual_triangle=i,vertices=t.tolist(),xy_area_m2=p.area,occupied_intersection_area_m2=cut.area,occupied_line_intersection_length_m=cut.length if cut.area==0 else None,distance_to_occupied_m=foot.distance(mask),normal_z=float(n[2]/np.linalg.norm(n))))
 return result
oldchange=changed_info(oldts,removed);newchange=changed_info(newts,added);nointrusion=all(c['occupied_intersection_area_m2']<1e-10 and (c['occupied_line_intersection_length_m'] or 0)<1e-8 for c in oldchange+newchange)
patch=shape(plan['patch']);selected=plan['selected_polygons'];obj=old['objects'][plan['object']];ov=np.array(obj['vertices']);selectedpolys=[Polygon(ov[obj['polygons'][i],:2]) for i in selected];selectedunion=unary_union(selectedpolys)
before=shore(oldts);after=shore(newts);cells=after['highest_surface_cells'];above_slope_area={};boundary=[];maxjump=0.;maxcrease=0.
for row in cells:
 p=unary_union(polygons(shape(row['projection'])));c=np.array(row['height_plane_abc']);surface=p.intersection(halfplane(c));slope=row['slope_degrees'];band='0_to15deg' if slope<=15 else '15_to30deg' if slope<=30 else '30_to45deg' if slope<=45 else 'over45deg';above_slope_area.setdefault(band,[]).append(surface);edge=p.intersection(rect.boundary)
 if edge.length>1e-8:
  points=points_any(edge);vals=[float(np.dot(c,[*xy,1])) for xy in points];boundary.append(dict(source=row['source'],intersection=mapping(edge),length_m=edge.length,height_min_max_m=[min(vals),max(vals)],surface_slope_degrees=slope))
for i,a in enumerate(cells):
 p=unary_union(polygons(shape(a['projection'])));c=np.array(a['height_plane_abc']);na=np.r_[-c[:2],1];na/=np.linalg.norm(na)
 for b in cells[i+1:]:
  other=unary_union(polygons(shape(b['projection'])));edge=p.boundary.intersection(other.boundary)
  if edge.length<=1e-8:continue
  cb=np.array(b['height_plane_abc']);nb=np.r_[-cb[:2],1];nb/=np.linalg.norm(nb);vals=[abs(float(np.dot(c-cb,[*q,1]))) for q in points_any(edge)];maxjump=max(maxjump,max(vals,default=0));maxcrease=max(maxcrease,math.degrees(math.acos(np.clip(np.dot(na,nb),-1,1))))
after['above_water_area_by_slope_band_m2']={k:unary_union(ps).area for k,ps in above_slope_area.items()};after['rectangle_boundary_surface_pieces']=boundary;after['maximum_internal_cell_height_jump_m']=maxjump;after['maximum_internal_cell_normal_angle_degrees']=maxcrease
selectedactualcounter=Counter(key(ov[f]) for f in obj['triangles'] if any(set(f).issubset(set(obj['polygons'][p])) for p in selected))
selectedstill=sum((selectedactualcounter & nc).values())
support=nointrusion and prior['actual_support_geometry_preserved'];passed=support and new['native_closed_positive_pass'] and identity['missing_export_triangles']==identity['extra_export_triangles']==0
report=dict(round='33d',scope='Actual local retopology geometry-counter difference, old/new actual occupied projection intrusion and238m²lowshore highestsurface; one source reopen,noGPU,noold-index topology comparison.',identity=identity,native_closed_positive_pass=new['native_closed_positive_pass'],native_parts=new['native'],retopology=dict(old_selected_polygon_count=len(selected),old_selected_triangle_geometry_count=sum(selectedactualcounter.values()),old_selected_triangles_still_exact_in_new=selectedstill,old_removed_triangle_geometry_count=sum(removed.values()),new_added_triangle_geometry_count=sum(added.values()),selected_old_xy_union_area_m2=selectedunion.area,plan_patch_area_m2=patch.area,selected_vs_plan_patch_difference_area_m2=selectedunion.symmetric_difference(patch).area,plan_patch_distance_to_actual_occupied_m=patch.distance(mask)),old_removed_actual_triangles=oldchange,new_added_actual_triangles=newchange,changed_old_or_new_actual_occupied_intersection_count=sum(c['occupied_intersection_area_m2']>1e-10 for c in oldchange+newchange),minimum_changed_old_or_new_actual_triangle_distance_to_occupied_m=min(c['distance_to_occupied_m'] for c in oldchange+newchange),can_inherit_33b_actual_complete_support=support,low_shore_bounds_order='xmin,ymin,xmax,ymax',low_shore_rectangle_projection=mapping(rect),actual_plan_floor_projection=plan['floor'],low_shore_before=before,low_shore_after=after,pass_result=passed,full_reference_accepted=False,all_reference_goal_complete=False,limits=['Triangle coordinates, not indices, compare33bto33d. Exact unchanged triangles inherit33bcomplete support; removedandadded triangles are checked individually for projected occupation including vertical-line intersections.','Selected168sourcepolygons are compared toactualnewtrianglegeometry; indicescanchange afterdeleteunused/retriangulation. No topologycount used as visualacceptance.','Lowshore upperenvelope includesall12actualnativeparts insideexact238m²designrectangle. It doesnot include oldWorld terrain overlay, water effects, navigation or camera visibility.','Nativeclosedpositive and sameGLB/source geometry are not global3Dselfintersection proof. No wholeworldscan or repeated33bfullsurface/support scan.'])
(R/'reviews/round-33d-rightcoast-independent-geometry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(pass_result=passed,identity=identity,retopology=report['retopology'],minchanged_distance=report['minimum_changed_old_or_new_actual_triangle_distance_to_occupied_m'],intrusions=report['changed_old_or_new_actual_occupied_intersection_count'],after={k:v for k,v in after.items() if k not in ['highest_surface_cells','rectangle_boundary_surface_pieces']}),indent=2))
