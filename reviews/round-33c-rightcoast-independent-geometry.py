from pathlib import Path
import json,struct,hashlib,math
from collections import Counter
import numpy as np
from shapely.geometry import Polygon,shape,mapping,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
exec((R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8'))
h=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(h[h.index('def plane'):h.index('road=unary_union')])
h=(R/'reviews/round-30j-plan-independent.py').read_text(encoding='utf-8');exec(h[h.index('def overlay'):h.index('rock_roofs=')])
old=read('reviews/round-33b-reopened-source.json');new=read('reviews/round-33c-reopened-source.json');prior=read('reviews/round-33b-rightcoast-independent-geometry.json');plan=read('captures/rightcoast_study_33c/design-plan.json');occ=read('reviews/round-33-occupied-regions.json');mask=shape(occ['hard_occupied_house_and_paving_union']);rect=box(*plan['working_shore']['bounds_blender_xy'])
assert prior['actual_support_geometry_preserved'] and plan['source_sha256']==old['source_sha256']==sha(plan['source'])
key=lambda t:tuple(sorted(map(tuple,t)))
allnew=[];allold=[];objects=[];changes=[]
for name,a in old['objects'].items():
 b=new['objects'][name];av,bv=np.array(a['vertices']),np.array(b['vertices']);changed=np.flatnonzero(np.any(av!=bv,axis=1));samexy=np.array_equal(av[:,:2],bv[:,:2]);samepoly=Counter(tuple(sorted(f)) for f in a['polygons'])==Counter(tuple(sorted(f)) for f in b['polygons']);dz=bv[:,2]-av[:,2]
 objects.append(dict(object=name,changed_vertex_indices=changed.tolist(),changed_vertex_count=len(changed),all_xy_exact=samexy,polygon_vertex_sets_exact=samepoly,z_delta_min_max_m=[float(dz.min()),float(dz.max())]))
 for i,f in enumerate(b['triangles']):
  t=bv[f];allnew.append((name,i,t))
  if not any(v in changed for v in f):continue
  poly=Polygon(t[:,:2]);cut=poly.intersection(mask) if poly.is_valid else Polygon();changes.append(dict(object=name,actual_triangle=i,indices=f,old_vertices=av[f].tolist(),new_vertices=t.tolist(),distance_to_occupied_m=poly.distance(mask),occupied_intersection_area_m2=cut.area))
 allold.extend((name,i,av[f]) for i,f in enumerate(a['triangles']))
gc=Counter(key(t) for t in asset_world_triangles(R/'captures/rightcoast_study_33c/mainland_headland.glb'));nc=Counter(key(t) for n,i,t in allnew)
identity=dict(saved_source_sha256=new['source_sha256'],source_reopened_unchanged=new['source_file_unchanged'],actual_glb_sha256=sha('captures/rightcoast_study_33c/mainland_headland.glb'),actual_glb_triangle_count=sum(gc.values()),missing_export_triangles=sum((nc-gc).values()),extra_export_triangles=sum((gc-nc).values()),immediate33b_source_matches_independent_reopen=True)
def shore(ts):
 cells=[];candidate=0
 for name,i,t in ts:
  if np.max(t[:,0])<rect.bounds[0] or np.min(t[:,0])>rect.bounds[2] or np.max(t[:,1])<rect.bounds[1] or np.min(t[:,1])>rect.bounds[3] or np.cross(t[1]-t[0],t[2]-t[0])[2]<=1e-10:continue
  cut=Polygon(t[:,:2]).intersection(rect)
  if cut.area<1e-10:continue
  candidate+=1;cells=overlay(cells,cut,plane(t),name+':'+str(i),maximum=True)
 cover=unary_union([p for p,c,l in cells]);vals=[float(np.dot(c,[*q,1])) for p,c,l in cells for q in points_any(p)];water=[];low=[];flat=[];details=[]
 for p,c,l in cells:
  above=p.intersection(halfplane(c));band=above.intersection(halfplane(np.array([0,0,2.])-c));flatpart=p.intersection(halfplane(c-np.array([0,0,1.599]))).intersection(halfplane(np.array([0,0,1.601])-c));water.append(above);low.append(band);flat.append(flatpart);details.append(dict(source=l,projection=mapping(p),height_plane_abc=c.tolist(),area_m2=p.area,slope_degrees=math.degrees(math.atan(np.linalg.norm(c[:2])))))
 return dict(rectangle_area_m2=rect.area,projected_native_surface_covered_area_m2=cover.area,no_native_surface_area_m2=rect.difference(cover).area,upper_surface_height_min_max_m=[min(vals),max(vals)],native_surface_above_water_area_m2=unary_union(water).area,above_water_surface_up_to2m_area_m2=unary_union(low).area,upper_surface_at1_6m_within1mm_area_m2=unary_union(flat).area,highest_surface_cells=details,actual_candidate_upward_triangles=candidate)
before=shore(allold);after=shore(allnew);support=all(r['occupied_intersection_area_m2']<1e-10 for r in changes) and all(r['all_xy_exact'] and r['polygon_vertex_sets_exact'] for r in objects)
report=dict(round='33c',scope='Only actual17changed vertices/incidentfaces, same-version saved sourceGLB identity and the prescribed238m²low-shore rectangle.33bfullsupport inherited by exact unaffectedgeometry; no repeatwholeoccupiedscan.',identity=identity,native_closed_positive_pass=new['native_closed_positive_pass'],object_increments=objects,changed_incident_faces=changes,changed_face_count=len(changes),changed_faces_intersect_actual_occupied_count=sum(r['occupied_intersection_area_m2']>1e-10 for r in changes),minimum_changed_face_distance_to_actual_occupied_m=min(r['distance_to_occupied_m'] for r in changes),can_inherit_33b_actual_complete_support=support,low_shore_rectangle_projection=mapping(rect),low_shore_before=before,low_shore_after=after,pass_result=support and new['native_closed_positive_pass'] and identity['missing_export_triangles']==identity['extra_export_triangles']==0,full_reference_accepted=False,all_reference_goal_complete=False,limits=['NoXYcoordinatechange; old/newincidentfaceprojections are identical. Newexternalfaces therefore cannot movehorizontally intohouse/road domains. Fulltriangleintersection still checks thosedomains directly.','Lowest1.6m target is evaluated on actualupperenvelope ofall12nativeparts insideonlythegivenrectangle. Missingnativecoverage is allowed and reported, not filled by an inventedplane.','This nativeasset measurement does not establish highest finalWorld collision surface, exposedvisiblewaterline or navigability. ParentGPU/runtime verifies actualWorld overlay.','No global3Dselfintersection or repeatedfullpavingcontact/worldtrees scan. Only boundedincrementalgeometrypass, notvisualgoalcompletion.'])
(R/'reviews/round-33c-rightcoast-independent-geometry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(pass_result=report['pass_result'],identity=identity,changed_vertices=sum(o['changed_vertex_count'] for o in objects),changed_faces=len(changes),mindistance=report['minimum_changed_face_distance_to_actual_occupied_m'],intersections=report['changed_faces_intersect_actual_occupied_count'],before={k:v for k,v in before.items() if k!='highest_surface_cells'},after={k:v for k,v in after.items() if k!='highest_surface_cells'}),indent=2))
