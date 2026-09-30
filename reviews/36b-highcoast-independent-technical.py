"""Bounded36b actual assets, terrain, scatter and recorded flight; no engine."""
from pathlib import Path
import json,struct,re,hashlib,ast,math
from collections import Counter,defaultdict
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon,Point,LineString,box,mapping
from shapely import union_all
R=Path(__file__).resolve().parents[1]
N=R/'captures/highcoast_study_36b'
RUN=R/'captures/validation_runs/highcoast-36b-20260909T015215Z-0c71bb650bcf43d890987772791f1dff'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def text(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exec(text(R/'reviews/round-32b-asset-footprint-decoder.py'),globals())
plan=read(N/'model-report.json');runtime=read(RUN/'images/highcoast-runtime.json');flight=read(RUN/'images/flight-traverse.json')
meshes={};npz={}
for row in plan['native_tiles']:
    name=row['name'];d=np.load(N/(name+'-mesh.npz'));npz[name]={k:d[k] for k in d.files};b=asset_world_triangles(N/(name+'.glb'));t=b[:,:,[0,2,1]]*np.array([1,1,-1])+np.array(row['origin']);meshes[name]=t
def heights(x,z):
    found=[]
    for name,t in meshes.items():
        lo=t[:,:,[0,2]].min(axis=1);hi=t[:,:,[0,2]].max(axis=1);indices=np.flatnonzero((lo[:,0]<=x+1e-6)&(hi[:,0]>=x-1e-6)&(lo[:,1]<=z+1e-6)&(hi[:,1]>=z-1e-6))
        if not len(indices):continue
        q=t[indices];a=q[:,0];b=q[:,1];c=q[:,2];den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2]);ok=np.abs(den)>1e-8
        for j in np.flatnonzero(ok):
            wa=((b[j,2]-c[j,2])*(x-c[j,0])+(c[j,0]-b[j,0])*(z-c[j,2]))/den[j];wb=((c[j,2]-a[j,2])*(x-c[j,0])+(a[j,0]-c[j,0])*(z-c[j,2]))/den[j];wc=1-wa-wb
            if min(wa,wb,wc)>=-1e-5:found.append(dict(tile=name,face=int(indices[j]),y=float(wa*a[j,1]+wb*b[j,1]+wc*c[j,1])))
    return sorted(found,key=lambda h:h['y'],reverse=True)
records=[]
for p in flight['samples']:
    x,y,z=p['position'];hit=heights(x,z)
    records.append(dict(step=p['step'],position=p['position'],recorded=p['actual_mesh_height'],actual_glb_highest=hit[0] if hit else None,error=None if not hit else max(0,hit[0]['y'])-p['actual_mesh_height'],real_vertical_clearance=None if not hit else y-hit[0]['y']))
F=RUN/'study-inputs/highcoast36b';local=RUN/'images/native-scenes';collision={};tile_checks=[]
old_intake=read(R/'reviews/36-terrain-savedmesh-intake.json');old_by={x['name']:x for x in old_intake['tiles']}
seams=defaultdict(list);native_seams=defaultdict(list)
def counter_indices(faces):return Counter(tuple(sorted(map(int,t))) for t in faces)
for row in plan['native_tiles']:
    name=row['name'];old=np.load(R/'captures/highcoast36-saved-inputs'/(name+'.npz'));new=npz[name];v=new['vertices_world'];orig=old['vertices_world'];faces=new['triangles'];actual=meshes[name]
    distances,ids=cKDTree(v).query(actual.reshape(-1,3));actualids=ids.reshape(-1,3)
    s=text(local/(name+'.tscn'));data=re.search(r'^data = PackedVector3Array\((.*?)\)',s,re.M)[1]
    col=np.fromstring(data,sep=',').reshape(-1,3,3)+np.array(row['origin']);collision[name]=col
    dist2,ids2=cKDTree(v).query(col.reshape(-1,3));cid=ids2.reshape(-1,3)
    outside=(orig[:,0]<=-3750)|(orig[:,0]>=-900)|(orig[:,2]<=-4400)|(orig[:,2]>=-2150)
    changed=np.abs(v[:,1]-orig[:,1])>1e-5
    for i,point in enumerate(v):
        localxz=point[[0,2]]-np.array(row['origin'])[[0,2]]
        if min(abs(localxz[0]),abs(localxz[0]-768),abs(localxz[1]),abs(localxz[1]-768))<.001:
            key=tuple(np.round(point[[0,2]],4));seams[key].append((name,float(point[1])))
            ys=col.reshape(-1,3)[ids2==i,1]
            if len(ys):native_seams[key].append((name,float(np.mean(ys))))
    tile_checks.append(dict(name=name,source_blend_matches_intake=sha(R/old_by[name]['source'])==old_by[name]['source_sha256']==row['source_sha256'],saved_blend_glb_frozen_match=all(sha(N/(name+'.'+e))==row[e+'_sha256']==sha(F/(name+'.'+e)) for e in ['blend','glb']),npz_frozen_same=sha(N/(name+'-mesh.npz'))==sha(F/(name+'-mesh.npz')),source_xz_and_topology_exact=np.array_equal(v[:,[0,2]],orig[:,[0,2]]) and np.array_equal(faces,old['triangles']),outside_region_vertices_exact=np.array_equal(v[outside],orig[outside]),changed_vertices_actual=int(changed.sum()),recorded_changed_vertices=row['changed_vertices'],changed_mask_exact=np.array_equal(changed,new['changed_vertices']),glb_nearest_native_vertex_max_error_m=float(distances.max()),glb_triangle_index_counter_exact=counter_indices(actualids)==counter_indices(faces),collision_nearest_native_vertex_max_error_m=float(dist2.max()),collision_triangle_index_counter_exact=counter_indices(cid)==counter_indices(faces),collision_triangles=len(col),runtime_collision_count_matches=next(t for t in runtime['tiles'] if t['name']==name)['collision_faces']==len(col),native_scene_sha_bound=sha(local/(name+'.tscn'))==next(t for t in runtime['tiles'] if t['name']==name)['native_scene_sha256'],native_scene_embeds_mesh_shape=all(token in s for token in ['type="ArrayMesh"','type="ConcavePolygonShape3D"','collision_layer = 5','backface_collision = true']),external_resources=re.findall(r'^\[ext_resource .*?path="([^"]+)"',s,re.M)))
allcol=np.concatenate(list(collision.values()));allnames=np.concatenate([np.full(len(t),n,dtype=object) for n,t in collision.items()]);lo=allcol[:,:,[0,2]].min(axis=1);hi=allcol[:,:,[0,2]].max(axis=1)
def collision_height(x,z):
    ix=np.flatnonzero((lo[:,0]<=x+1e-5)&(hi[:,0]>=x-1e-5)&(lo[:,1]<=z+1e-5)&(hi[:,1]>=z-1e-5));result=[]
    for i in ix:
        a,b,c=allcol[i];den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
        if abs(den)<1e-8:continue
        wa=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den;wb=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den;wc=1-wa-wb
        if min(wa,wb,wc)>=-1e-5:result.append((float(wa*a[1]+wb*b[1]+wc*c[1]),int(i)))
    return sorted(result,reverse=True)
for p in records:
    x,y,z=p['position'];h=collision_height(x,z);p['saved_collision_height']=h[0][0] if h else None;p['saved_collision_vs_record_error_m']=None if not h else max(0,h[0][0])-p['recorded'];p['saved_collision_vertical_clearance_m']=None if not h else y-h[0][0]
def ray(origin,direction):
    direction=np.array(direction);direction/=np.linalg.norm(direction);a=allcol[:,0];e1=allcol[:,1]-a;e2=allcol[:,2]-a;p=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,p);ok=np.abs(det)>1e-9;inv=np.divide(1,det,out=np.zeros_like(det),where=ok);s=np.array(origin)-a;u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,e1);vv=q@direction*inv;tt=np.einsum('ij,ij->i',e2,q)*inv
    hit=np.flatnonzero(ok&(u>=-1e-7)&(vv>=-1e-7)&(u+vv<=1+1e-7)&(tt>0))
    if not len(hit):return None
    i=hit[np.argmin(tt[hit])];return dict(distance_m=float(tt[i]),tile=str(allnames[i]),global_collision_triangle_index=int(i),position=(np.array(origin)+tt[i]*direction).tolist(),normal=(np.cross(e1[i],e2[i])/np.linalg.norm(np.cross(e1[i],e2[i]))).tolist())
cam=read(RUN/'images/flight-end.png.json')['camera'];origin=cam['position'];forward=np.array([1710,0,-20],float);forward=forward/np.linalg.norm(forward)*180+np.array([0,-15,0]);forward=np.array(forward,float);forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward);rays=[]
for px,py in [(836,470),(418,470),(1254,470),(836,235),(836,705)]:
    d=forward+(2*px/1672-1)*math.tan(math.radians(35))*1672/941*right+(1-2*py/941)*math.tan(math.radians(35))*up
    rays.append(dict(pixel=[px,py],hit=ray(origin,d)))
def water_projection(triangles):
    polygons=[]
    for t in triangles:
        if np.min(t[:,1])>=0:continue
        output=[]
        for a,b in zip(t,np.roll(t,-1,axis=0)):
            if a[1]<=0:output.append(a[[0,2]])
            if (a[1]<0 and b[1]>0) or (a[1]>0 and b[1]<0):output.append((a+(b-a)*(-a[1]/(b[1]-a[1])))[[0,2]])
        if len(output)>=3:
            poly=Polygon(output)
            if poly.area>1e-10:polygons.append(poly)
    return union_all(polygons)
water_native=water_projection(np.concatenate(list(meshes.values())))
water_collision=water_projection(allcol)
line=LineString([p[:2] for p in plan['tidal_estuary_controls']]);first7=LineString([p[:2] for p in plan['tidal_estuary_controls'][:7]])
from_sea=LineString([[-3500,-3190]]+[p[:2] for p in plan['tidal_estuary_controls'][:7]])
river=dict(controls=[dict(xz=p[:2],glb_height=heights(*p[:2])[0]['y'],saved_collision_height=collision_height(*p[:2])[0][0],runtime_probe=runtime['estuary_probes'][i]) for i,p in enumerate(plan['tidal_estuary_controls'])],method='Clip actual terrain triangles at Y=0 and union their XZ polygons; intersect continuous authored centerline, not Ocean rays or isolated height samples.',first_seven_centerline_length_m=first7.length,first_seven_dry_length_glb_m=first7.difference(water_native).length,first_seven_dry_length_collision_m=first7.difference(water_collision).length,sea_to_seventh_dry_length_glb_m=from_sea.difference(water_native).length,sea_to_seventh_dry_length_collision_m=from_sea.difference(water_collision).length,whole_nine_control_centerline_length_m=line.length,whole_line_dry_length_glb_m=line.difference(water_native).length,whole_line_dry_length_collision_m=line.difference(water_collision).length,dry_line_segments_glb=mapping(line.difference(water_native)),waterbody_note='First seven controls connect to actual negative sea-bed at(-3500,-3190). Final controls require measured results below; no full river width proof.')
# Reuse only the strict pure MultiMesh parser class, not old inventory execution.
tree=ast.parse(text(R/'reviews/36-highcoast-occupancy-intake.py'))
class_node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MultiReader')
parser_source=ast.get_source_segment(text(R/'reviews/36-highcoast-occupancy-intake.py'),class_node)
parser_source=parser_source.replace("assert len(internals)==1;self.i=internals[0][1]","self.internal_table=internals;self.i=internals[-1][1]")
parser_source=parser_source.replace('assert sub==3,sub','if sub==2:\n                index=self.u32();return dict(path="embedded_internal://"+str(index),internal_table=self.internal_table)\n            assert sub==3,sub')
exec(parser_source,globals())
occupancy=read(R/'reviews/36-highcoast-occupancy-intake.json');changes=runtime['scatter_changes'];bygroup=defaultdict(dict)
for c in changes:
    assert c['source_index'] not in bygroup[c['source_grove']];bygroup[c['source_grove']][c['source_index']]=c
scatter=[];axis=[];actual_new_resources={}
for g in occupancy['scatter_groups']:
    name=g['path'].split('/')[-1]
    if name not in bygroup:continue
    source=R/g['multimesh_resource'].removeprefix('res://');old=MultiReader(source);m=np.eye(4);m[:3]=g['world_group_transform'];base=local/(name+'.res');after=MultiReader(base);actual_new_resources[name]=after
    pine_path=local/(name+'_CoastalPines36b.res');pine=MultiReader(pine_path) if pine_path.exists() else None
    if pine:actual_new_resources[name+'_CoastalPines36b']=pine
    remaining=0;converted=0;max_basis=0.;max_position=0.;max_reportold=0.;unchanged_exact=True
    for i,tr in enumerate(old.transforms):
        original=np.eye(4);original[:3]=tr;world_old=m@original;c=bygroup[name].get(i)
        ispine=c is not None and c['new_grove'].endswith('_CoastalPines36b')
        destination=(pine.transforms[converted] if ispine else after.transforms[remaining]);expected_index=converted if ispine else remaining
        if ispine:converted+=1
        else:remaining+=1
        target=np.eye(4);target[:3]=destination;world_new=m@target
        max_basis=max(max_basis,float(np.max(np.abs(world_new[:3,:3]-world_old[:3,:3]))))
        if c:
            assert c['new_index']==expected_index
            max_position=max(max_position,float(np.max(np.abs(world_new[:3,3]-c['new_position']))));max_reportold=max(max_reportold,float(np.max(np.abs(world_old[:3,3]-c['old_position']))))
            p=c['new_position'];hit=collision_height(p[0],p[2]);axis.append(dict(global_prop_index=c['global_prop_index'],tile=str(allnames[hit[0][1]]) if hit else None,saved_collision_height=hit[0][0] if hit else None,reported_ground_y=c['ground_y'],ground_error_m=abs(hit[0][0]-c['ground_y']) if hit else None,axis_clearance_error_m=abs(p[1]-c['clearance']-hit[0][0]) if hit else None))
        else:unchanged_exact &= np.array_equal(destination,tr)
    scatter.append(dict(source_grove=name,source_res_sha_matches_intake=sha(source)==g['multimesh_sha256'],source_count=len(old.transforms),remaining_count=len(after.transforms),pine_count=len(pine.transforms) if pine else 0,total_preserved=len(old.transforms)==len(after.transforms)+(len(pine.transforms) if pine else 0),changed_records=len(bygroup[name]),unchanged_transform_rows_exact=bool(unchanged_exact),max_changed_world_position_vs_runtime_m=max_position,max_old_position_vs_runtime_m=max_reportold,max_basis_delta=max_basis,new_resource_paths=[str(base.relative_to(RUN))]+([str(pine_path.relative_to(RUN))] if pine else []),actual_pine_mesh_reference=pine.mesh if pine else None))
manifest=read(RUN/'manifest.json');bindings=[]
for name,entry in manifest['artifacts'].items():
    if name.startswith('images/') or name.startswith('study-inputs/highcoast36b/'):
        bindings.append(dict(path=name,sha_matches=sha(RUN/name)==entry['sha256']))
prior=R/'captures/validation_runs/storm-35c-20260909T004220Z-c4392024b9a4475faaff26f81d9cbcab';old_view=read(prior/'images/storm-high.png.json');view_checks=[]
for p in sorted((RUN/'images').glob('*.png.json')):
    d=read(p);full=not p.name.startswith('flight')
    view_checks.append(dict(view=d['view'],run_identity=d['run_id']==RUN.name,world_sha_retained=d['world_sha256']==old_view['world_sha256'],revision_report_sha=d['highcoast_revision']['report_sha256']==sha(RUN/'images/highcoast-runtime.json'),old_assembly_fields_retained=None if not full else all(d[k]==old_view[k] for k in ['rightcoast_glb_sha256','island_a_glb_sha256','island_c_glb_sha256','lighthouse_sha256','placements']),old_headland_trees_retained=None if not full else d['headland_study']['trees']==old_view['headland_study']['trees']))
# Forward terrain checks from actual saved collision, not a second physics run.
direction=np.array([1710.,-20.]);direction/=np.linalg.norm(direction)
envelopes=[]
for p in flight['samples']:
    x,y,z=p['position'];sampled=[]
    for advance in range(0,241,20):
        q=np.array([x,z])+direction*advance;hits=collision_height(*q)
        sampled.append(max(0,hits[0][0]) if hits else None)
    seg=LineString([[x,z],np.array([x,z])+direction*240]);bounds=seg.bounds
    ix=np.flatnonzero((lo[:,0]<=bounds[2])&(hi[:,0]>=bounds[0])&(lo[:,1]<=bounds[3])&(hi[:,1]>=bounds[1]))
    maximum=0.;crossings=0
    for index in ix:
        t=allcol[index];poly=Polygon(t[:,[0,2]])
        if poly.area<1e-9:continue
        inter=poly.intersection(seg)
        if inter.is_empty:continue
        components=list(inter.geoms) if hasattr(inter,'geoms') else [inter]
        for component in components:
            for q in component.coords:
                a,b,c=t;matrix=np.array([[a[0]-c[0],b[0]-c[0]],[a[2]-c[2],b[2]-c[2]]]);weights=np.linalg.solve(matrix,np.array(q)-c[[0,2]])
                h=weights[0]*a[1]+weights[1]*b[1]+(1-weights.sum())*c[1];maximum=max(maximum,float(h));crossings+=1
    envelopes.append(dict(step=p['step'],all13_samples_have_terrain=all(h is not None for h in sampled),sampled_collision_max_m=max(h for h in sampled if h is not None),recorded_max_m=p['ahead_240m_max_mesh_height'],recorded_error_m=max(h for h in sampled if h is not None)-p['ahead_240m_max_mesh_height'],camera_above_sampled_max_m=y-max(h for h in sampled if h is not None),continuous_240m_centerline_max_m=maximum,camera_above_continuous_centerline_max_m=y-maximum,continuous_minus_sampled_max_m=maximum-max(h for h in sampled if h is not None),linear_intersection_endpoints=crossings))
native_sv=[max(x[1] for x in v)-min(x[1] for x in v) for v in seams.values() if len({x[0] for x in v})>1]
collision_sv=[max(x[1] for x in v)-min(x[1] for x in v) for v in native_seams.values() if len({x[0] for x in v})>1]
logs='\n'.join(text(p) for p in RUN.glob('*error.log'));errors=[s for s in logs.splitlines() if 'ERROR:' in s]
candidate=read(RUN/'images/candidate-scenes.json');world_text=text(local/'World36b.tscn')
paths=re.findall(r'^\[ext_resource .*?path="([^"]+)"',world_text,re.M);mixed=[s for s in paths if 'E:' in s and chr(92) in s]
pngs=[dict(path=p.relative_to(RUN).as_posix(),sha256=sha(p),manifest_bound=p.relative_to(RUN).as_posix() in manifest['artifacts']) for p in sorted((RUN/'images').glob('*.png'))]
checks=dict(native_source_export_frozen_identity=all(t['source_blend_matches_intake'] and t['saved_blend_glb_frozen_match'] and t['npz_frozen_same'] for t in tile_checks),native_xz_topology_outside_region_exact=all(t['source_xz_and_topology_exact'] and t['outside_region_vertices_exact'] and t['changed_mask_exact'] and t['changed_vertices_actual']==t['recorded_changed_vertices'] for t in tile_checks),native10659_changed=sum(t['changed_vertices_actual'] for t in tile_checks)==10659,actual_glb_and_saved_collision_connectivity=all(t['glb_triangle_index_counter_exact'] and t['collision_triangle_index_counter_exact'] and t['runtime_collision_count_matches'] and t['native_scene_sha_bound'] for t in tile_checks),native_shared_border_heights=max(native_sv)<.002,actual_scatter_resource_delta=all(s['total_preserved'] and s['unchanged_transform_rows_exact'] and s['source_res_sha_matches_intake'] and s['max_changed_world_position_vs_runtime_m']<.002 and s['max_old_position_vs_runtime_m']<.002 and s['max_basis_delta']<1e-6 for s in scatter),actual_scatter_axis_support=all(a['axis_clearance_error_m'] is not None and a['axis_clearance_error_m']<.03 for a in axis),flight65_ground_height_matches_collision=len(records)==65 and all(p['saved_collision_height'] is not None and abs(p['saved_collision_vs_record_error_m'])<.002 for p in records),flight65_forward13_samples_match_collision=len(envelopes)==65 and all(p['all13_samples_have_terrain'] and abs(p['recorded_error_m'])<.002 and abs(p['camera_above_sampled_max_m']-65)<.002 for p in envelopes),frozen_input_bindings=bool(bindings) and all(b['sha_matches'] for b in bindings),actual12_sidecar_identity=len(view_checks)==12 and all(v['run_identity'] and v['world_sha_retained'] and v['revision_report_sha'] and v['old_assembly_fields_retained'] is not False and v['old_headland_trees_retained'] is not False for v in view_checks))
report=dict(scope='Bounded36b actual source/GLB/collision/scatter/river and65 recorded cameras. No Blender, engine, physics or unrelated wholeworld rerun.36c excluded.',run=RUN.name,manifest_status=manifest['status'],stage_exit_codes=[s['exit_code'] for s in manifest['stages']],tile_checks=tile_checks,changed_native_vertices=sum(t['changed_vertices_actual'] for t in tile_checks),native_builder_identity=sha(N/'builder.py')==sha(R/'blender/sculpt_highcoast_36b.py')==sha(F/'builder.py'),runtime_source_identity=sha(R/'tools/highcoast_runtime_36b.gd')==sha(F/'highcoast_runtime_36b.gd'),seams=dict(native_max_height_delta_m=max(native_sv),saved_collision_max_height_delta_m=max(collision_sv),shared_keys=len(native_sv)),import_geometry_error=dict(glb_vs_native_max_m=max(t['glb_nearest_native_vertex_max_error_m'] for t in tile_checks),saved_collision_vs_native_max_m=max(t['collision_nearest_native_vertex_max_error_m'] for t in tile_checks),limit='Imported coordinate quantization measured separately from native exactXZ/topology. No byte-exact collision coordinate assertion.'),river=river,scatter=dict(change_count=len(changes),global_total_recorded=runtime['scatter_total_preserved'],global_indices_unique=len({c['global_prop_index'] for c in changes})==len(changes),groups=scatter,new_resource_count=len(actual_new_resources),kinds_after=dict(Counter(c['kind'] for c in changes)),max_horizontal_move_m=max(c['horizontal_move_m'] for c in changes),max_actual_axis_error_m=max(a['axis_clearance_error_m'] for a in axis),axis_checks=axis,source_destination_inside_rectangle=all(-3750<=p[0]<=-900 and -4400<=p[2]<=-2150 for c in changes for p in [c['old_position'],c['new_position']]),unresolved=runtime['unresolved'],runtime_support_failures=runtime['support_failures'],runtime_physics_max_axis_error_m=runtime['max_axis_support_error_m'],limit='Whole affected resource rows and unchanged rows checked.54800 derives from unchanged outside resources plus zero affected-group count delta, not all54800 redecoded. Axis support is not full trunk/rock footprint, canopy, mutual overlap or vehicle support.'),flight=dict(records=records,forward_envelopes=envelopes,max_saved_collision_terrain_height_error_m=max(abs(p['saved_collision_vs_record_error_m']) for p in records),max_forward_sample_record_error_m=max(abs(p['recorded_error_m']) for p in envelopes),max_unsampled_centerline_peak_over13_samples_m=max(p['continuous_minus_sampled_max_m'] for p in envelopes),minimum_camera_above_actual_continuous240m_centerline_m=min(p['camera_above_continuous_centerline_max_m'] for p in envelopes),end_five_saved_collision_rays=rays,end_camera=cam,limit='65 savedcamera positions,13forward20m samples plus independent continuous240m centerline clipping. This proves neither whole image frustum nor lateral or swept vehicle corridor. Sea-clamped terrain_height intentionally differs from underwater bed.'),candidate_editability=dict(native14tile_contract=all(all(token in text(local/(row['name']+'.tscn')) for token in ['scripts/asset_instance.gd','name="Model"','name="Collision"','name="Shape"','surface_material =']) for row in plan['native_tiles']),embedded_mesh_collision=all(t['native_scene_embeds_mesh_shape'] for t in tile_checks),candidate_report=candidate,world_game_file_hashes_match_report=sha(local/'World36b.tscn')==candidate['world_sha256'] and sha(local/'Game36b.tscn')==candidate['game_sha256'],world_external_mixed_path_count=len(mixed),mixed_path_examples=mixed[:3],world_game_reload_accepted=False,notes='Fresh unready World avoids transient prop-collider cache persistence; ownership stops at instance boundaries and saver restores scatter helpers/model_scene. Actual World/Game serialization failed due malformed external references; file hashes and ResourceSaver returns do not establish reload. No independent source reopen, embedded ArrayMesh vertex-buffer decode or candidate ready/reload execution.'),run_failure=dict(error_count=len(errors),error_examples=errors[:3],texture_leaks=[s for s in errors if 'Texture with GL ID' in s],manifest_error=manifest.get('error'),png_count=len(pngs),png_manifest_bound_count=sum(p['manifest_bound'] for p in pngs),note='Engine exited0 but error gate failed.12PNG/sidecars exist and independently hashed here; failed manifest binds no images. No successful whole run or World/Game reload claim.'),images=pngs,view_checks=view_checks,artifact_bindings=bindings,checks=checks,bounded_geometry_axis_and_route_checks_pass=all(checks.values()),overall_technical_accepted=False,visual_accepted=False,full_reference_accepted=False,all_reference_goal_complete=False)
(R/'reviews/36b-highcoast-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=checks,scatter=report['scatter']['kinds_after'],changes=len(changes),resources=len(actual_new_resources),import_error=report['import_geometry_error'],seams=report['seams'],river={k:v for k,v in river.items() if isinstance(v,(float,int))},flight={k:v for k,v in report['flight'].items() if isinstance(v,(float,int))},end_rays=rays,errorcount=len(errors),contract=report['candidate_editability']['native14tile_contract']),ensure_ascii=False))
