import bpy,bmesh,json,sys,struct,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/scratch/a29d03198654/Aether');D=R/'source-assets/lake-cirque54/v2/final-source';I=R/'source-assets/lake-cirque54/intake';sys.path.insert(0,str(I));import land_support as land
auth=json.load(open(D.parent/'native-authority/cirque-native-authority.json'));attrs=json.load(open(I/'cirque-saved53-native-attributes.json'))['surfaces'][0]['expanded_attributes'];intake=json.load(open(D.parent/'native-authority/upper-remesh-intake-c.json'));p=json.load(open(D/'cirque54v2-payload.json'))['mountains'][0];org=p['origin']
def b(p):return struct.pack('<fff',*p)
def key(t):
 q=[b(v) for v in t];return min(tuple(q[i:]+q[:i]) for i in range(3))
def color_key(t,c):
 q=[b(v)+struct.pack('<ffff',*col) for v,col in zip(t,c)];return min(tuple(q[i:]+q[:i]) for i in range(3))
def world(v):return [v.x+org[0],v.z+org[1],-v.y+org[2]]
def tree(ff):return BVHTree.FromPolygons([Vector(v) for v in ff],[(i,i+1,i+2) for i in range(0,len(ff),3)],all_triangles=True)
def h(tr,x,z):
 q,_,_,_=tr.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
 return q.y if q is not None else None
bpy.ops.wm.open_mainfile(filepath=str(D/'massif_cirque_wall_cirque54v2.blend'));report={'authority':'Raw saved53 GPU surface arrays and original collider arrays, proven byte equal; derived Mesh.get_faces is not used as native source authority','baseline_sha256':auth['baseline_sha256'],'gpu_original_collider_arrays_exact':auth['gpu_collision_exact'],'reopened_components':[]}
for c in p['components']:
 o=bpy.data.objects[c['name']];m=o.data;m.calc_loop_triangles();a=m.color_attributes.active_color;ff=[];cc=[]
 for t in m.loop_triangles:
  for vi,li in zip(reversed(t.vertices),reversed(t.loops)):ff.append(world(m.vertices[vi].co));cc.append(list(a.data[li].color))
 exact=collections.Counter(color_key(ff[i:i+3],cc[i:i+3]) for i in range(0,len(ff),3))==collections.Counter(color_key(c['vertices'][i:i+3],c['colors'][i:i+3]) for i in range(0,len(ff),3))
 bm=bmesh.new();bm.from_mesh(m);r={'component':c['name'],'triangles':len(ff)//3,'native_reopen_geometry_and_rgba_exact_float32':exact,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-8 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free();report['reopened_components'].append(r)
 assert exact and not any(r[k] for k in ['boundary_edges','nonmanifold_edges','degenerate_faces']) and r['signed_volume']>0,r
body=p['components'][0];vf=body['vertices'];vc=body['colors'];allnew=collections.Counter(key(vf[i:i+3]) for i in range(0,len(vf),3));allcol=collections.Counter(color_key(vf[i:i+3],vc[i:i+3]) for i in range(0,len(vf),3));oldf=auth['faces'];oldwet=collections.Counter();oldwetcol=collections.Counter();wetids=[]
for i in range(0,len(oldf),3):
 if min(v[1] for v in oldf[i:i+3])<=0:
  oldwet[key(oldf[i:i+3])]+=1;oldwetcol[color_key(oldf[i:i+3],[r['color'] for r in attrs[i:i+3]])]+=1;wetids.append(i//3)
newwet=collections.Counter(key(vf[i:i+3]) for i in range(0,len(vf),3) if min(v[1] for v in vf[i:i+3])<=0);newwetcol=collections.Counter(color_key(vf[i:i+3],vc[i:i+3]) for i in range(0,len(vf),3) if min(v[1] for v in vf[i:i+3])<=0)
report['wet_surface']={'original_touch_water_triangles':sum(oldwet.values()),'new_touch_water_triangles':sum(newwet.values()),'oriented_geometry_float32_bytes_exact':oldwet==newwet,'rgba_float32_bytes_exact':oldwetcol==newwetcol,'y0_intersection_and_lake_cutout_exact':'Every full original triangle that can intersect or lie belowY0 is identical, including winding. Therefore its plane, Y0intersection and under-water geometry are unchanged; no new waterline coordinate was rounded or serialized.','new_snow_min_y':min(q[1] for c in p['components'][1:] for q in c['vertices'])};assert oldwet==newwet and oldwetcol==newwetcol and sum(oldwet.values())==432
protected=[]
for r in intake['protected_faces']:
 fi=r['original_triangle'];f=oldf[fi*3:fi*3+3];c=[r['color'] for r in attrs[fi*3:fi*3+3]];row={'old_triangle':fi,'whole_oriented_triangle_exact':allnew[key(f)]==1,'whole_rgba_triangle_exact':allcol[color_key(f,c)]==1};protected.append(row);assert row['whole_oriented_triangle_exact'] and row['whole_rgba_triangle_exact']
report['protected_original_dry_faces']=protected;report['protected_dry_faces_exact_count']=len(protected);assert len(protected)==19
tr=tree(p['collision_vertices'])
def without_old_cirque(x,z):
 hits=[0.0] # Actual unchanged globalOcean mask4plane, Y0; excluded only from dryland proofs.
 for row in land.INVENTORY['land_shapes']:
  if '/massif_cirque_wall/' in row['path'] or not land.in_box(row,x,x,z,z):continue
  if row['path'] not in land.TREES:land.highest(x,z)
  value=h(land.TREES[row['path']],x,z)
  if value is not None:hits.append(value)
 return max(hits)
def candidate_height(x,z):
 old_without=without_old_cirque(x,z);value=h(tr,x,z)
 return max(old_without,value) if value is not None else old_without
runtimepath=R/'cloud-evidence/rim53d-west-verify-v2-20261001T064631Z-OrTCQY/verify-report-west53-v2.json';runtime=json.load(open(runtimepath));buildings=[]
for q in runtime['runtime_support']['mountain_building_rows']:
 if q['kind']!='buildings':continue
 x,z=q['x'],q['z'];old,owner=land.highest(x,z);new=candidate_height(x,z);buildings.append({'x':x,'z':z,'actual_saved53_physics_y':q['physics_y'],'full_native_support_owner':owner,'full_native_support_y':old,'candidate_support_y':new,'intake_vs_actual_runtime_error_m':abs(old-q['physics_y']),'source_change_m':new-old})
report['full_buildings']={'count':len(buildings),'max_intake_vs_saved_runtime_error_m':max(r['intake_vs_actual_runtime_error_m'] for r in buildings),'max_source_change_m':max(abs(r['source_change_m']) for r in buildings),'rows':buildings,'runtime_authority_report_sha256':hashlib.sha256(runtimepath.read_bytes()).hexdigest()};assert len(buildings)==171 and report['full_buildings']['max_intake_vs_saved_runtime_error_m']<.03 and report['full_buildings']['max_source_change_m']<.000001
scatter=json.load(open(R/'source-assets/lake-rim53/integration-west53/runtime-probes.json'))['scatter'];sr=[];counts=collections.Counter();changed_previous=[]
for s in scatter:
 x,y,z=s['position'];old,_=land.highest(x,z);old=max(0,old);new=candidate_height(x,z);delta=new-old;status='root_support_changed_pending_full_volume_reconcile' if abs(delta)>.015 else 'root_support_unchanged';counts[status]+=1
 row={'node':s['node_path'],'index':s['index'],'saved53_position':s['position'],'saved53_support_y':old,'candidate_support_y':new,'delta_m':delta,'was_west120':s['status']!='unchanged','status':status};sr.append(row)
 if row['was_west120'] and abs(delta)>.015:changed_previous.append(row)
report['scatter']={'total':len(sr),'counts':dict(counts),'prior_west120_count':sum(r['was_west120'] for r in sr),'prior_west120_support_changed':changed_previous,'rows':sr,'mesh_volume_intersections_complete':False,'transforms_written':False};assert len(sr)==1261 and not changed_previous
report['integrated']=False;report['visual_acceptance']=False
json.dump(report,open(D/'native-reopen-water-support-proof.json','w'),indent=2)
print('CIRQUE54V2_NATIVE_PROOF_PASS',len(report['reopened_components']),'components; wet432RGBA exact; protected19RGBA exact;171buildings maxchange',report['full_buildings']['max_source_change_m'],'scatter',dict(counts),flush=True)
