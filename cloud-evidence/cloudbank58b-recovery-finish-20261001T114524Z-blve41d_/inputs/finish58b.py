"""Bounded phase2: simplify a verified native union while retaining it exactly.

No rendering/world. Volume and bidirectional vertex/centroid surface offsets
limit simplification; none of these is a visual acceptance metric.
"""
import datetime,hashlib,json,sys,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent;ROOT=A.parents[1]
sys.path[:0]=[str(P),str(B),str(A)]
from build58 import world_coordinate,ORIGIN,MATERIAL
from intake58 import native_intake
from verify_final58b import geometry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=time.monotonic();stages=[]


def stage(name,state):
    row=dict(operation=name,state=state,elapsed_seconds=time.monotonic()-start,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());stages.append(row)
    (P/'facet-stage58b.json').write_text(json.dumps(dict(complete=False,current_operation=name,stages=stages),indent=2)+'\n');print(json.dumps(row),flush=True)


assert not(P/'cloud_bank58b.blend').exists(),'Never overwrite a completed recovered B source'
proof=json.loads((P/'union-fresh-readback58b.json').read_text())
assert proof['passed'] and proof['union_sha256']==sha(P/'cloud_bank58b_union.blend')
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_bank58b_union.blend'))
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
bank=bpy.data.objects['CloudBank58B_four_root_folded_volume'];controls=bpy.data.collections['EDIT58B_closed_3d_fold_volumes']
stage('preserve_exact_unreduced_union','running')
raw=bpy.data.objects.new('EDIT58B_continuous_union_before_facets',bank.data.copy());controls.objects.link(raw);raw.hide_render=True
raw['fold_name']='continuous_union_review_mesh';raw['not_a_loft_rebuild_input']=True
base,bv,bi,bt,btree=geometry(raw);assert base['closed_geometry_passed']
stage('preserve_exact_unreduced_union','finished')
bpy.ops.object.select_all(action='DESELECT');bank.select_set(True);bpy.context.view_layer.objects.active=bank
stage('native_decimate_9000_triangle_target','running')
target=9000
if base['triangles']>target:
    modifier=bank.modifiers.new('Bounded native collapse of saved3D union','DECIMATE');modifier.decimate_type='COLLAPSE';modifier.ratio=target/base['triangles'];modifier.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
tri=bank.modifiers.new('Final native flat facets','TRIANGULATE');tri.quad_method='BEAUTY';tri.ngon_method='BEAUTY';bpy.ops.object.modifier_apply(modifier=tri.name)
stage('native_decimate_9000_triangle_target','finished')
stage('measure_native_volume_and_bidirectional_surface_offsets','running')
reduced,rv,ri,rt,rtree=geometry(bank)
def surface_samples(vertices,triangles,tree):
    points=np.concatenate([vertices,triangles.mean(1)]);dist=[]
    for point in points:
        nearest=tree.find_nearest(Vector(point));assert nearest[0] is not None;dist.append(float(nearest[3]))
    return dict(samples=len(points),kinds='Every native vertex and every native triangle centroid',max_m=max(dist),p95_m=float(np.percentile(dist,95)),median_m=float(np.median(dist)))
raw_to_reduced=surface_samples(bv,bt,rtree);reduced_to_raw=surface_samples(rv,rt,btree)
volume_change=(reduced['signed_volume_m3']-base['signed_volume_m3'])/base['signed_volume_m3']
passed=reduced['closed_geometry_passed'] and abs(volume_change)<.03 and max(raw_to_reduced['max_m'],reduced_to_raw['max_m'])<35
deviation=dict(passed=bool(passed),raw_geometry=base,reduced_geometry=reduced,relative_signed_volume_change=volume_change,
               raw_to_reduced=raw_to_reduced,reduced_to_raw=reduced_to_raw,volume_tolerance_fraction=.03,max_sampled_surface_offset_tolerance_m=35,
               is_continuous_Hausdorff_bound=False,visual_acceptance=False)
(P/'facet-deviation58b.json').write_text(json.dumps(deviation,indent=2)+'\n')
stage('measure_native_volume_and_bidirectional_surface_offsets','finished')
if not passed:
    bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58b_failed_facets.blend'))
    raise AssertionError('Retained native facets fail bounded geometry/deviation gate; do not export/promote')
stage('preserve_material_law_and_export_native_root_local_meshes','running')
bank.data.materials.clear();bank.data.materials.append(bpy.data.materials[MATERIAL])
for f in bank.data.polygons:f.use_smooth=False
for attr in list(bank.data.color_attributes):bank.data.color_attributes.remove(attr)
col=bank.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in bank.data.polygons:
    y=sum(world_coordinate(bank.data.vertices[i].co)[1] for i in f.vertices)/len(f.vertices)
    v=.76+.16*max(0,min(1,((y-700)+190)/460));linear=((v+.055)/1.055)**2.4
    for li in f.loop_indices:col.data[li].color=(linear,linear,linear,1)
intake,_=native_intake();roots={r['name']:r for r in intake['roots']};rows=[]
upper=[bpy.data.objects[n] for n in ('CloudBank58_upper_west_layer','CloudBank58_upper_east_layer','CloudBank58_upper_far_veil')]
for ob in [bank]+upper:
    world=[Vector(world_coordinate(ob.matrix_world@v.co)) for v in ob.data.vertices]
    root=roots[ob['original_root']];inv=Matrix(root['basis_rows']).inverted();pos=Vector(root['position'])
    export=ob.data.copy()
    for v,p in zip(export.vertices,world):
        q=inv@(p-pos);v.co=(q.x,-q.z,q.y)
    temp=bpy.data.objects.new('EXPORT58B_'+ob.name,export);scene.collection.objects.link(temp)
    bpy.ops.object.select_all(action='DESELECT');temp.select_set(True);bpy.context.view_layer.objects.active=temp
    filename=ob.name+'.glb';bpy.ops.export_scene.gltf(filepath=str(P/filename),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(export)
    rows.append(dict(name=ob.name,file=filename,sha256=sha(P/filename),root=root['name'],native_root_basis_rows=root['basis_rows'],native_root_position=root['position'],kind=ob['kind'],
                     world_bounds=[[min(p[k] for p in world) for k in range(3)],[max(p[k] for p in world) for k in range(3)]]))
stage('preserve_material_law_and_export_native_root_local_meshes','finished')
for filename in ('fill_cavity58b.py','finish58b.py'):
    txt=bpy.data.texts.new(filename);txt.write((P/filename).read_text())
txt=bpy.data.texts.new('lofts58b.py');txt.write((B/'lofts58b.py').read_text())
stage('save_native_source_pending_fresh_readback','running')
bpy.ops.object.select_all(action='DESELECT');bank.select_set(True);bpy.context.view_layer.objects.active=bank
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58b.blend'))
stage('save_native_source_pending_fresh_readback','finished')
construction=dict(source_method=scene['source_method']+' Native bounded Decimate instead of QuadriFlow.',native_control_count=11,voxel_size_m=26,
                  facet_target_triangles=9000,decimate_deviation_gate_passed=True,native_controls_retained=True,raw_union_retained=True,rectangular_domain=False,
                  heightfield=False,common_bottom_cap=False,coplanar_seam_caps=False,origin=ORIGIN,meshes=rows,source_sha256=sha(P/'cloud_bank58b.blend'),
                  rendered=False,world_loaded=False,visual_acceptance=False,native_readback_pending=True)
(P/'construction58b.json').write_text(json.dumps(construction,indent=2)+'\n')
(P/'facet-stage58b.json').write_text(json.dumps(dict(complete=True,current_operation='facets_source_saved_pending_fresh_readback',stages=stages,world_loaded=False,visual_acceptance=False),indent=2)+'\n')
print('Native recovered B saved with quantified simplification and original shell; fresh readback pending',flush=True)
