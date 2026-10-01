"""C57-native-control checkpoint, coarse15 snapshot, raw57 voxel union.

Source-only scheduled byparent. No rendering, export, simplification or world.
All stages are explicit and preservefailed nativecheckpoints.
"""
import datetime,hashlib,json,sys,time
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(P))
from geometry58c import source_coordinate,ORIGIN
from native_geometry58c import geometry
start=time.monotonic();events=[]

def stage(name,state):
 row=dict(operation=name,state=state,elapsed_seconds=time.monotonic()-start,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());events.append(row)
 (P/'build-stage58c.json').write_text(json.dumps(dict(complete=False,current_operation=name,events=events,world_loaded=False,rendered=False),indent=2)+'\n');print(json.dumps(row),flush=True)

def union_copy(items,collection,name):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in items:
  temp=bpy.data.objects.new('WORK_'+ob.name,ob.data.copy());collection.objects.link(temp);temp.select_set(True);bpy.context.view_layer.objects.active=temp
 bpy.ops.object.join();ob=bpy.context.object;ob.name=name
 ob.data.remesh_voxel_size=26.;ob.data.use_remesh_preserve_volume=False
 bpy.ops.object.voxel_remesh()
 for face in ob.data.polygons:face.use_smooth=False
 ob['preserve_volume']=False;ob['voxel_size_m']=26.;ob['visual_acceptance']=False;return ob

for name in ('cloud_bank58c_controls.blend','cloud_bank58c_coarse15.blend','cloud_bank58c_union.blend'):assert not(P/name).exists(),'Do not overwrite a C checkpoint'
specs=json.loads((P/'native-control-input58c.json').read_text());assert len(specs['controls'])==57
stage('create_57_editable_native_control_volumes','running')
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
scene['source_origin_godot_world']=list(ORIGIN);scene['authored_scope']='Independent4-root52fcloudresearch,57nativecontrolsolids;no56/60/61integration';scene['visual_acceptance']=False
controls=bpy.data.collections.new('EDIT58C_57_native_3d_controls');scene.collection.children.link(controls)
results=bpy.data.collections.new('SOURCE58C_local_density_and_folds');scene.collection.children.link(results)
items=[];rows=[]
for spec in specs['controls']:
 mesh=bpy.data.meshes.new('EDIT58C_'+spec['id']);mesh.from_pydata([source_coordinate(v) for v in spec['vertices']],[],spec['faces']);mesh.update()
 ob=bpy.data.objects.new(mesh.name,mesh);controls.objects.link(ob);ob['control_id']=spec['id'];ob['role']=spec['role'];ob['parent_form']=spec['parent_form'] or '';ob['design_json']=json.dumps(spec['design']);ob['native_edit_instructions']='Editthese meshvertices inEditMode. Preserveauthoredcontrolsand rebuildtoanewsourcecandidate.'
 for face in mesh.polygons:face.use_smooth=False
 items.append(ob)
for filename in ('authoring-plan58c.json','native-control-input58c.json','geometry58c.py','triangle_checks58c.py','build58c.py'):
 txt=bpy.data.texts.new(filename);txt.write((P/filename).read_text())
stage('create_57_editable_native_control_volumes','finished');stage('save_57_native_control_checkpoint','running')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58c_controls.blend'));stage('save_57_native_control_checkpoint','finished')
stage('check_each_closed_native_control','running')
for ob in items:
 report,*_=geometry(ob);rows.append(report)
(P/'native-control-geometry58c.json').write_text(json.dumps(dict(controls=rows,all_passed=all(r['closed_geometry_passed'] for r in rows)),indent=2)+'\n')
assert all(r['closed_geometry_passed'] for r in rows),'An authoredcontrolfails; stopbeforeunion'
stage('check_each_closed_native_control','finished');stage('coarse15_native_union_26m_preserveFalse','running')
coarse=union_copy([ob for ob in items if ob['role'] in ('lower_density','primary_crown')],results,'EDIT58C_coarse15_union')
stage('coarse15_native_union_26m_preserveFalse','finished');stage('save_unvalidated_coarse15_checkpoint','running')
controls.hide_render=True;controls.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58c_coarse15.blend'));stage('save_unvalidated_coarse15_checkpoint','finished')
coarse.hide_render=True;coarse.hide_viewport=True
stage('full57_native_union_26m_preserveFalse','running')
bank=union_copy(items,results,'CloudBank58C_four_root_density_and_folds');stage('full57_native_union_26m_preserveFalse','finished')
bank['kind']='continuous_lower_density_with_primary_medium_small_folds';bank['original_root']='CloudSea_0_0';bank['internal_caps']=0
stage('save_unvalidated_full57_union_checkpoint','running')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58c_union.blend'));stage('save_unvalidated_full57_union_checkpoint','finished')
(P/'build-stage58c.json').write_text(json.dumps(dict(complete=True,current_operation='raw_union_saved_pending_independent_geometry',events=events,
 finished_source=False,world_loaded=False,rendered=False,visual_acceptance=False),indent=2)+'\n')
print('C57rawunion saved; every uniongeometry/ray/section gate awaits freshprocess',flush=True)
