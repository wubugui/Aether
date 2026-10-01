"""Bounded recovery phase1: save native controls, join, voxel union, save shell.

No QuadriFlow, decimation, rendering, export, world, or completed-source claim.
"""
import datetime,hashlib,json,shutil,sys,time
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent;ROOT=A.parents[1]
sys.path[:0]=[str(B),str(A)]
from build58 import source_coordinate,ORIGIN,MATERIAL
from geometry58 import signed_volume
from build58b import object_geometry
from verify58b import geometry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=time.monotonic();stages=[]


def stage(name,state):
    row=dict(operation=name,state=state,elapsed_seconds=time.monotonic()-start,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());stages.append(row)
    (P/'union-stage58b.json').write_text(json.dumps(dict(complete=False,current_operation=name,stages=stages),indent=2)+'\n')
    print(json.dumps(row),flush=True)


assert not(P/'cloud_bank58b_union.blend').exists(),'Do not overwrite a saved union checkpoint'
freeze=json.loads((B/'failed-build-freeze58b.json').read_text())
assert all(sha(ROOT/f)==r['sha256'] for f,r in freeze['files'].items()),'Failed B evidence changed'
frozen_A=json.loads((A/'revision-a-freeze.json').read_text())
assert all(sha(ROOT/f)==r['sha256'] for f,r in frozen_A['files'].items()),'Rejected A evidence changed'
specs=json.loads((B/'native-control-input58b.json').read_text())
shutil.copy2(B/'native-control-input58b.json',P/'native-control-input58b.json')
stage('restore_exact_recorded_native_loft_controls','running')
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=2
scene['cloudbank58b_native3d_folds']=True;scene['source_origin_godot_world']=ORIGIN;scene['visual_acceptance']=False
scene['source_method']='Eleven exact frozenB3D loft controls joined and voxel-unioned at26m; bounded staged recovery. No rectangular domain or common bottom cap.'
controls=bpy.data.collections.new('EDIT58B_closed_3d_fold_volumes');scene.collection.children.link(controls)
finals=bpy.data.collections.new('CloudBank58B_local_four_root_field');scene.collection.children.link(finals)
upper_names=['CloudBank58_upper_west_layer','CloudBank58_upper_east_layer','CloudBank58_upper_far_veil']
with bpy.data.libraries.load(str(A/'cloud_bank58.blend'),link=False) as (src,dst):dst.objects=upper_names
for ob in dst.objects:finals.objects.link(ob)
items=[];rows=[]
for spec in specs['loft_specs']:
    faces=spec['faces']
    if signed_volume(spec['vertices'],faces)<0:faces=[tuple(reversed(f)) for f in faces]
    me=bpy.data.meshes.new('EDIT58B_'+spec['name']);me.from_pydata([source_coordinate(v) for v in spec['vertices']],[],faces);me.update()
    ob=bpy.data.objects.new(me.name,me);controls.objects.link(ob);ob.hide_render=True
    ob['fold_name']=spec['name'];ob['initial_knots_json']=json.dumps(spec['knots']);ob['section_count']=spec['section_count']
    ob['edit_instruction']='These are exact recovered nativeB loft controls. Edit mesh vertices and rebuild to a new source revision.'
    items.append(ob);rows.append(object_geometry(ob))
assert all(not(r['boundary'] or r['nonmanifold'] or r['nonadjacent_self_overlap_count']) and r['signed_volume']>0 for r in rows)
stage('restore_exact_recorded_native_loft_controls','finished')
stage('save_native_control_checkpoint','running')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58b_controls.blend'))
stage('save_native_control_checkpoint','finished')
stage('join_temporary_control_copies','running')
bpy.ops.object.select_all(action='DESELECT')
for ob in items:
    temp=bpy.data.objects.new('WORK58B_'+ob['fold_name'],ob.data.copy());finals.objects.link(temp);temp.select_set(True);bpy.context.view_layer.objects.active=temp
bpy.ops.object.join();bank=bpy.context.object;bank.name='CloudBank58B_four_root_folded_volume'
stage('join_temporary_control_copies','finished')
stage('voxel_union_26m','running')
bank.data.remesh_voxel_size=26.;bank.data.use_remesh_preserve_volume=True;bpy.ops.object.voxel_remesh()
stage('voxel_union_26m','finished')
bank['kind']='continuous_lower_folded_volume';bank['original_root']='CloudSea_0_0';bank['internal_caps']=0;bank['visual_acceptance']=False
bank.data.materials.clear();bank.data.materials.append(bpy.data.materials[MATERIAL]);controls.hide_render=True;controls.hide_viewport=True
stage('save_unvalidated_union_checkpoint','running')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58b_union.blend'))
stage('save_unvalidated_union_checkpoint','finished')
stage('check_union_native_geometry','running')
row,*_=geometry(bank)
(P/'union-geometry58b.json').write_text(json.dumps(dict(native_union_geometry_passed=bool(row['closed_geometry_passed']),geometry=row,source_sha256=sha(P/'cloud_bank58b_union.blend'),
    controls_checkpoint_sha256=sha(P/'cloud_bank58b_controls.blend'),controls=rows,quadriFlow_ran=False,rendered=False,world_loaded=False,visual_acceptance=False),indent=2)+'\n')
stage('check_union_native_geometry','finished')
assert row['closed_geometry_passed'],'Preserve failed union and native controls; no facets stage'
(P/'union-stage58b.json').write_text(json.dumps(dict(complete=True,current_operation='union_source_checkpoint_complete',stages=stages,world_loaded=False,visual_acceptance=False),indent=2)+'\n')
print('BOUNDed58B UNION CHECKPOINT COMPLETE; no finished source, GLB, renderer or world',flush=True)
