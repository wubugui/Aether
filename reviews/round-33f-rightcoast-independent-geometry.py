from pathlib import Path
import json,struct,hashlib,math
from collections import Counter,defaultdict
import numpy as np
from shapely.geometry import Polygon,MultiPoint,shape,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
exec((R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8'))
base=read('reviews/round-33b-reopened-source.json');old=read('reviews/round-33d-reopened-source.json');new=read('reviews/round-33f-reopened-source.json');donor=read('reviews/round-33e-reopened-source.json');prior=read('reviews/round-33d-rightcoast-independent-geometry.json');plan=read('captures/rightcoast_study_33f/design-plan.json');intake=read('reviews/round-33f-transition-component-intake.json');mask=shape(read('reviews/round-33-occupied-regions.json')['hard_occupied_house_and_paving_union']);bay=shape(read('captures/rightcoast_study_33d/design-plan.json')['patch'])
assert prior['can_inherit_33b_actual_complete_support'];assert plan['source_sha256']==old['source_sha256']==sha(plan['source']);assert plan['base_sha256']==base['source_sha256'];assert plan['selected_source_vertices']==intake['selected_front_free_vertex_ids']
key=lambda t:tuple(sorted(map(tuple,t)))
def oriented(t):
 k=tuple(map(tuple,t));return min(k,k[1:]+k[:1],k[2:]+k[:2])
def collect(d):
 rows=[]
 for name,o in d['objects'].items():
  v=np.array(o['vertices']);rows.extend((name,i,v[f]) for i,f in enumerate(o['triangles']))
 return rows
oldts,newts=collect(old),collect(new);oc=Counter(key(t) for n,i,t in oldts);nc=Counter(key(t) for n,i,t in newts);export=asset_world_triangles(R/'captures/rightcoast_study_33f/mainland_headland.glb');gc=Counter(key(t) for t in export);ng=Counter(oriented(t) for n,i,t in newts);gg=Counter(oriented(t) for t in export);removed=oc-nc;added=nc-oc
name=next(n for n in old['objects'] if n.startswith('Mainland'));bv=np.array(base['objects'][name]['vertices']);dv=np.array(old['objects'][name]['vertices']);fv=np.array(new['objects'][name]['vertices']);ev=np.array(donor['objects'][name]['vertices']);lookup=defaultdict(list)
for i,xyz in enumerate(dv):lookup[tuple(xyz)].append(i)
maps=[];selected_current=set()
for i in intake['selected_front_free_vertex_ids']:
 match=lookup[tuple(bv[i])];assert len(match)==1;j=match[0];selected_current.add(j);maps.append(dict(source33b_vertex_index=i,current33d33f_vertex_index=j,plan_mapping_matches=int(plan['source_to_current_vertex_mapping'][str(i)])==j,old33d_xyz=dv[j].tolist(),new33f_xyz=fv[j].tolist(),donor33e_xyz=ev[i].tolist(),actual55point_donor_xyz_exact=bool(np.array_equal(fv[j],ev[i])),old33b_xyz_matches_33d=bool(np.array_equal(bv[i],dv[j]))))
excluded=[]
for c in intake['components']:
 if not c['contains_main_reference_hit']:continue
 for i in c['free_vertex_ids']:
  match=lookup[tuple(bv[i])];assert len(match)==1;j=match[0];excluded.append(dict(source33b_vertex_index=i,current33d33f_vertex_index=j,xyz=fv[j].tolist(),exactly_retains33d=bool(np.array_equal(dv[j],fv[j]))))
boundary=[]
for i in [3772,7152,7289]:
 match=lookup[tuple(bv[i])];assert len(match)==1;j=match[0];boundary.append(dict(source33b_vertex_index=i,current33d33f_vertex_index=j,exact=bool(np.array_equal(dv[j],fv[j]))))
objects=[]
for n,a in old['objects'].items():
 b=new['objects'][n];av,cv=np.array(a['vertices']),np.array(b['vertices']);changed=np.flatnonzero(np.any(av!=cv,axis=1));objects.append(dict(object=n,changed_vertex_count=len(changed),changed_vertex_indices=changed.tolist(),all_xy_exact=bool(np.array_equal(av[:,:2],cv[:,:2])),only_selected55_points_changed=bool(set(changed)<=selected_current) if n==name else len(changed)==0,maximum_vertex_displacement_m=float(np.linalg.norm(av-cv,axis=1).max())))
def differences(ts,counter):
 records=[];ps=[]
 for n,i,t in ts:
  if key(t) not in counter:continue
  poly=Polygon(t[:,:2]);p=poly if poly.is_valid and poly.area>1e-12 else MultiPoint(t[:,:2]).convex_hull;cut=p.intersection(mask);no=np.cross(t[1]-t[0],t[2]-t[0]);records.append(dict(object=n,actual_triangle=i,vertices=t.tolist(),projected_area_m2=poly.area,occupied_intersection_area_m2=cut.area,occupied_line_intersection_length_m=cut.length if cut.area==0 else None,distance_to_actual_occupied_m=p.distance(mask),bay33d_patch_intersection_area_m2=p.intersection(bay).area,normal_z=float(no[2]/np.linalg.norm(no))))
  if poly.is_valid and poly.area>1e-12:ps.append(poly)
 union=unary_union(ps);return records,union,sum(p.area for p in ps)-union.area
oldchange,op,oo=differences(oldts,removed);newchange,np_,no=differences(newts,added);delta=op.symmetric_difference(np_).area
quadsource=[2466,4346,4348,4350];qm={i:lookup[tuple(bv[i])][0] for i in quadsource};good=set([qm[2466],qm[4348]]);bad=set([qm[4346],qm[4350]]);triangles=new['objects'][name]['triangles'];goodfaces=[i for i,f in enumerate(triangles) if good.issubset(f)];badfaces=[i for i,f in enumerate(triangles) if bad.issubset(f)];quadexpected=[{qm[i] for i in f} for f in [[4348,2466,4346],[4350,2466,4348]]];actualquad=[dict(actual_triangle=i,indices=triangles[i],vertices=fv[triangles[i]].tolist()) for i in goodfaces];quadsetmatch=len(actualquad)==2 and all(set(q['indices']) in quadexpected for q in actualquad);quadpolys=[Polygon(np.array(q['vertices'])[:,:2]) for q in actualquad];qoverlap=quadpolys[0].intersection(quadpolys[1]).area if len(quadpolys)==2 else None;qsign=[float(np.cross(np.array(q['vertices'])[1]-np.array(q['vertices'])[0],np.array(q['vertices'])[2]-np.array(q['vertices'])[0])[2]) for q in actualquad]
quad=dict(source33b_to_current_vertex_mapping=qm,restored_current_diagonal=sorted(good),rejected_current_diagonal=sorted(bad),restored_diagonal_incident_actual_triangles=actualquad,bad_diagonal_incident_actual_triangle_ids=badfaces,expected_old_two_triangle_sets_restored=quadsetmatch,actual_two_triangle_xy_overlap_area_m2=qoverlap,actual_signed_twice_xy_areas=qsign,pass_result=quadsetmatch and not badfaces and qoverlap<1e-12 and all(x>0 for x in qsign))
intrusions=[r for r in oldchange+newchange if r['occupied_intersection_area_m2']>1e-10 or (r['occupied_line_intersection_length_m'] or 0)>1e-8];baychanges=[r for r in oldchange+newchange if r['bay33d_patch_intersection_area_m2']>1e-10];nonup=[r for r in newchange if r['normal_z']<=0]
identity=dict(source_sha256=new['source_sha256'],source_reopened_unchanged=new['source_file_unchanged'],actual_glb_sha256=sha('captures/rightcoast_study_33f/mainland_headland.glb'),actual_glb_triangle_count=sum(gc.values()),missing_export_triangles=sum((nc-gc).values()),extra_export_triangles=sum((gc-nc).values()),oriented_triangle_counters_exact=ng==gg,immediate33d_source_matches_independent_reopen=True)
support=not intrusions and all(r['only_selected55_points_changed'] and r['all_xy_exact'] for r in objects) and all(r['exactly_retains33d'] for r in excluded) and all(r['exact'] for r in boundary)
passed=support and new['native_closed_positive_pass'] and ng==gg and quad['pass_result'] and not nonup and not baychanges and delta<1e-8 and no<=oo+1e-8 and all(r['actual55point_donor_xyz_exact'] and r['plan_mapping_matches'] for r in maps)
report=dict(round='33f',scope='Incremental33dsource plus55mapped frontpoints;31rejected points, actualsupportprojection,33dbaypreservation and restored4pointdiagonal. One savedsource reopen;noGPUorwholeworldscan.',identity=identity,native_closed_positive_pass=new['native_closed_positive_pass'],native_parts=new['native'],selected55_mapping_checks=maps,excluded31_mapping_checks=excluded,three_support_boundary_vertices=boundary,object_increments=objects,old_removed_actual_triangle_count=sum(removed.values()),new_added_actual_triangle_count=sum(added.values()),old_removed_triangles=oldchange,new_added_triangles=newchange,changed_old_projection=mapping(op),changed_new_projection=mapping(np_),changed_old_projected_area_m2=op.area,changed_new_projected_area_m2=np_.area,old_new_projection_symmetric_difference_area_m2=delta,old_changed_triangle_summed_area_minus_union_m2=oo,new_changed_triangle_summed_area_minus_union_m2=no,actual_support_intrusions=intrusions,minimum_changed_face_distance_to_actual_occupied_m=min(r['distance_to_actual_occupied_m'] for r in oldchange+newchange),new_changed_nonupward_triangles=nonup,restored_four_point_domain=quad,actual_changed_triangles_touching33d_bay=baychanges,can_inherit_33d_actual_complete_support=support,can_inherit_33d_bay_geometry=not baychanges,pass_result=passed,full_reference_accepted=False,all_reference_goal_complete=False,limits=['The2front hits belong to1sharedvertexconnected component,55free points; the2mainreference components total31excluded points.','Nooldindexcopy: original33bcoordinates are independently rematched uniquely to actual33dpoints before confirming33fvalues against33edonor.','ChangedtriangleXYunions and summed-areaoverlap are both checked, alongsidepositiveXYorientation and specific4pointdomain pair overlap; unchangedworldnotrescanned.','Nativeclosedpositive and theseboundedprojectionchecks are not an exhaustive3Dselfintersection proof. Actualsource/GLBorientationidentity doesnot imply art acceptance.','33dbaygeometry inherited exactly where no changedgeometryenters its patch; lowshore/Worldcollision/visual metrics are not rerun or upgraded here.'])
(R/'reviews/round-33f-rightcoast-independent-geometry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(pass_result=passed,identity=identity,selected=len(maps),excluded=len(excluded),changed_points=sum(r['changed_vertex_count'] for r in objects),quad=quad,oldtri=sum(removed.values()),newtri=sum(added.values()),area=op.area,xydiff=delta,oldoverlap=oo,newoverlap=no,nonup=len(nonup),supportintrusions=len(intrusions),baychanged=len(baychanges)),indent=2))
