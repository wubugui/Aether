from pathlib import Path
import json,struct,hashlib,math
from collections import Counter
import numpy as np
from shapely.geometry import Polygon,shape,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
exec((R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8'))
old=read('captures/rightcoast33-native-intake.json');new=read('reviews/round-33a-reopened-source.json');plan=read('captures/rightcoast_study_33a/design-plan.json');occ=read('reviews/round-33-occupied-regions.json');mask=shape(occ['hard_occupied_house_and_paving_union']);frozen=shape(plan['frozen_face_region']);designocc=shape(plan['occupied_region'])
def key(t):return tuple(sorted(map(tuple,t)))
def native_tris(objects):return [(name,i,np.array(obj['vertices'])[f]) for name,obj in objects.items() for i,f in enumerate(obj['triangles'])]
oldts=native_tris(old['objects']);newts=native_tris(new['objects']);oc=Counter(key(t) for name,i,t in oldts);nc=Counter(key(t) for name,i,t in newts)
glb=asset_world_triangles(R/'captures/rightcoast_study_33a/mainland_headland.glb');gc=Counter(key(t) for t in glb)
identity=dict(source_reopened_unchanged=new['source_file_unchanged'],source_sha256=new['source_sha256'],glb_sha256=sha('captures/rightcoast_study_33a/mainland_headland.glb'),actual_glb_triangle_count=len(glb),reopened_native_triangle_count=len(newts),actual_glb_vs_reopened_source_missing_triangles=sum((nc-gc).values()),actual_glb_vs_reopened_source_extra_triangles=sum((gc-nc).values()))
rows=[];changedfaces=[];flips=[];ratios=[]
for name,a in old['objects'].items():
 b=new['objects'][name];av,bv=np.array(a['vertices']),np.array(b['vertices']);samepoly=Counter(tuple(sorted(f)) for f in a['polygons'])==Counter(tuple(sorted(f)) for f in b['polygons']);changes=np.flatnonzero(np.any(av!=bv,axis=1));fids=plan['objects'][name]['frozen_vertices'];fdiff=np.linalg.norm(av[fids]-bv[fids],axis=1) if fids else np.array([0.]);countflip=0
 # For actual current triangles, use the same3vertexindices in the old source;
 # polygon/vertex topology retained, and current source triangulation is measured.
 for ti,f in enumerate(b['triangles']):
  a3=av[f];b3=bv[f];ao=float(np.cross(a3[1]-a3[0],a3[2]-a3[0])[2]);bn=float(np.cross(b3[1]-b3[0],b3[2]-b3[0])[2])
  if abs(ao)>1e-8:
   ratios.append(bn/ao)
   if bn*ao<=0:flips.append(dict(object=name,actual_current_triangle=ti,indices=f,old_signed_twice_xy_area=ao,new_signed_twice_xy_area=bn));countflip+=1
 rows.append(dict(object=name,vertex_count=len(bv),polygon_vertex_sets_preserved=samepoly,actual_changed_vertices=len(changes),maximum_vertex_displacement_m=float(np.linalg.norm(bv-av,axis=1).max()),frozen_vertex_count=len(fids),frozen_vertex_max_displacement_m=float(fdiff.max()),xy_orientation_reversals=countflip))
def localized(ts,othercounter):
 count=0;changed=[];cover=[];old_upcover=[]
 for name,i,t in ts:
  poly=Polygon(t[:,:2]);area=poly.area
  if area<=1e-12:continue
  cut=poly.intersection(mask)
  if cut.area>1e-10:
   count+=1;cover.append(cut)
   if np.cross(t[1]-t[0],t[2]-t[0])[2]>0:old_upcover.append(cut)
   if key(t) not in othercounter:changed.append(dict(object=name,actual_triangle=i,vertices=t.tolist(),occupied_intersection_area_m2=cut.area,occupied_intersection=mapping(cut)))
 return dict(all_surface_triangles_over_occupied=count,changed_triangles_over_occupied=changed,changed_count=len(changed),covered_area_m2=unary_union(cover).area,upward_surface_union_area_m2=unary_union(old_upcover).area,upward_surface_missing_occupied_area_m2=mask.difference(unary_union(old_upcover)).area)
oldloc=localized(oldts,nc);newloc=localized(newts,oc)
domains=[]
for h in occ['houses']:
 p=shape(h['actual_foundation_projection']);domains.append(dict(name=h['name'],kind='actual_house_foundation',area_m2=p.area,outside_plan_occupied_area_m2=p.difference(designocc).area,outside_frozen_face_region_area_m2=p.difference(frozen).area))
for g in occ['paving']['groups']:
 p=shape(g['actual_union_projection']);domains.append(dict(name=g['name'],kind='actual_complete_paving_projection',area_m2=p.area,outside_plan_occupied_area_m2=p.difference(designocc).area,outside_frozen_face_region_area_m2=p.difference(frozen).area))
passed=new['native_closed_positive_pass'] and identity['actual_glb_vs_reopened_source_missing_triangles']==0 and identity['actual_glb_vs_reopened_source_extra_triangles']==0 and all(r['polygon_vertex_sets_preserved'] and r['frozen_vertex_max_displacement_m']==0 for r in rows) and not flips and oldloc['changed_count']==0 and newloc['changed_count']==0 and all(d['outside_plan_occupied_area_m2']<1e-8 and d['outside_frozen_face_region_area_m2']<1e-8 for d in domains)
report=dict(round='33a',scope='Actual saved source reopen, currentGLB identity, complete actual9foundation/922paving protection and outside-face movement into their projected support domains; no newGPU or wholeworld scan.',identity=identity,native_closed_positive_pass=new['native_closed_positive_pass'],native_parts=new['native'],object_increments=rows,domain_containment=domains,old_actual_surface_over_occupied=oldloc,new_actual_surface_over_occupied=newloc,xy_orientation_reversals=flips,minimum_signed_current_vs_old_xy_area_ratio=min(ratios),actual_occupied_union_area_m2=mask.area,frozen_region_area_m2=frozen.area,plan_occupied_region_area_m2=designocc.area,pass_result=passed,full_reference_accepted=False,all_reference_goal_complete=False,limits=['Complete projected intersections include all nonvertical native layers; a changednewtriangle over occupied area would fail even if all original frozenvertices remainfixed. Only zero/tiny<=1e-10m² intersection remnants are ignored.','ActualGLB triangulation is independently compared to reopenednative; current triangles use same vertexindex triples on old source for signedXYorientation comparisons. Original vertical triangles are excluded from orientation-ratio division.','NoXYsignflip is not proof that arbitrary distant triangles never self-intersect. This bounded report checks support intrusion, not global3Dself-intersection.','Preservedgroundunderroad does not rerun complete26bpaving contact, floating-base, entirewalking or visual checks; same actual occupiedgroundgeometry permits prior scoped evidence to be inherited.','Trees may reground; this report does not freeze28rootheights or certify all procedural worldscatter support.'])
(R/'reviews/round-33a-rightcoast-independent-geometry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(pass_result=passed,identity=identity,domains=domains,old_changed=oldloc['changed_count'],new_changed=newloc['changed_count'],xyflips=len(flips),ratio=min(ratios),objects=rows),indent=2))
