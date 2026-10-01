"""Small shared-skin source build or one fresh raw source image, no world."""
import argparse,json,os,sys,time
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import patch58f as patch
import common58d as c
SOURCE=P/'shared_patch58f.blend'
E_SOURCE=P.parent/'revision-e/B_staggered_crowns.blend'
E_RUN=c.ROOT/'cloud-evidence/cloudbank58e-layouts-20261001T165946Z-yove55lx'
NAME='CloudBank58F_shared_crown_shoulder_belly_skin'
VIEWS=['1216-source-front','shared-side-back']


def expected_inputs():
    frame=json.loads(c.PLAN.read_text());settings=json.loads(c.SETTINGS.read_text())
    reference=next(r for r in json.loads((E_RUN/'outputs/build-result58e.json').read_text())['layouts'] if r['layout']=='B_staggered_crowns')
    assert c.sha(E_SOURCE)==reference['source_sha256']
    return frame,settings,reference,patch.make_patch(frame)


def native_identity(bank,spec,frame):
    actual=np.asarray([list(v.co) for v in bank.data.vertices],float)
    expected=c.source_coordinates(spec['vertices'],frame).astype(np.float32).astype(float)
    faces=[list(f.vertices) for f in bank.data.polygons]
    checks=dict(vertices_exact=np.array_equal(actual,expected),ordered_oriented_faces_exact=faces==spec['faces'],
                nonempty=len(actual)==182 and len(faces)==360,no_modifiers=len(bank.modifiers)==0,
                flat_faces=all(not f.use_smooth for f in bank.data.polygons),matrix_identity=np.array_equal(np.asarray(bank.matrix_world),np.eye(4)),
                effective_visible=bank.visible_get() and not bank.hide_render and not bank.hide_viewport and not bank.hide_get())
    groups=[]
    for name,ids in spec['groups'].items():
        group=bank.vertex_groups[name]
        actual_weights=[[v.index,float(g.weight)] for v in bank.data.vertices for g in v.groups if g.group==group.index]
        groups.append(dict(name=name,passed=actual_weights==[[i,1.] for i in sorted(set(ids))]))
    checks['edit_groups_exact']=all(r['passed'] for r in groups)
    checks['edit_group_inventory_exact']=sorted(g.name for g in bank.vertex_groups)==sorted(spec['groups'])
    return dict(checks=checks,groups=groups,passed=all(checks.values()),basic_shared_edge_incidence_two=spec['basic_edge_incidence_two'],
                final_self_intersection_validation=False,final_continuous_valley_validation=False)


def build(out):
    assert not SOURCE.exists(),'Preserve existing candidate and failure evidence'
    frame,settings,reference,spec=expected_inputs()
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    for store in [bpy.data.meshes,bpy.data.materials,bpy.data.cameras,bpy.data.lights,bpy.data.images]:
        for block in list(store):
            if block.users==0:store.remove(block)
    scene=bpy.context.scene
    collection=bpy.data.collections.new('EDIT58F_shared_surface');scene.collection.children.link(collection)
    view=bpy.data.collections.new('VIEW58F_frozen_camera_lighting');scene.collection.children.link(view)
    # Import only the two established cameras. No E mesh, material or scene is
    # reused. Their source-native transforms/projections remain untouched.
    with bpy.data.libraries.load(str(E_SOURCE),link=False) as (src,dst):
        dst.objects=['VIEW58E_'+name for name in VIEWS]
    assert all(ob is not None and ob.type=='CAMERA' for ob in dst.objects)
    assert len(bpy.data.meshes)==0,'Unexpected E geometry import'
    for ob in dst.objects:
        view.objects.link(ob);ob.name='VIEW58F_'+ob['view_name']
    mesh=bpy.data.meshes.new(NAME);mesh.from_pydata(c.source_coordinates(spec['vertices'],frame).astype(np.float32).tolist(),[],spec['faces']);mesh.update()
    bank=bpy.data.objects.new(NAME,mesh);collection.objects.link(bank)
    for name,ids in spec['groups'].items():bank.vertex_groups.new(name=name).add(sorted(set(ids)),1,'REPLACE')
    for face in mesh.polygons:face.use_smooth=False
    bank['patch_source_sha256']=c.sha(P/'patch58f.py');bank['source_method']='One shared outer skin, explicitly authored top/side/belly cells; no union, old E geometry, smoothing or flat cap'
    bank['shared_top_boundary_json']=json.dumps(spec['ring_indices'][0]);bank['authored_scope']='Small visual shape trial only; no final self-intersection or continuous valley proof'
    scene['source_origin_godot_world']=frame['anchor_godot_world_xyz'];scene['source_u_world']=frame['local_u_world'];scene['source_v_world']=frame['local_v_world'];scene['visual_acceptance']=False
    material=bpy.data.materials.new('58F same neutral source inspection');material.use_nodes=True
    bsdf=material.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=settings['material_linear_rgba'];bsdf.inputs['Roughness'].default_value=settings['material_roughness'];mesh.materials.append(material)
    world=bpy.data.worlds.new('58F same fixed neutral world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=settings['world_linear_rgba'];world.node_tree.nodes['Background'].inputs['Strength'].default_value=settings['world_strength'];scene.world=world
    light=bpy.data.lights.new('58F fixed Sun','SUN');light.energy=settings['sun_energy'];light.angle=settings['sun_angle_radians'];sun=bpy.data.objects.new(light.name,light);view.objects.link(sun);sun.rotation_euler=settings['sun_source_rotation_xyz_radians']
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=2
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    bpy.context.view_layer.update();checks=native_identity(bank,spec,frame);assert checks['passed']
    cameras=[]
    for name in VIEWS:
        cam=bpy.data.objects['VIEW58F_'+name];row=c.camera_proof(scene,cam,[bank.matrix_world@v.co for v in mesh.vertices],frame,settings)
        expected=next(r for r in reference['cameras'] if r['name']==name)
        row['same_E_camera_matrix']=row['matrix_world']==expected['matrix_world'];row['same_E_camera_projection']=row['projection']==expected['projection']
        row['passed']=row['passed'] and row['same_E_camera_matrix'] and row['same_E_camera_projection'];cameras.append(row)
    c.write(out/'pre-save-check58f.json',dict(passed=checks['passed'] and all(r['passed'] for r in cameras),native_identity=checks,cameras=cameras,
                                            actual_world_bounds=[np.min(spec['vertices'],axis=0),np.max(spec['vertices'],axis=0)],actual_local_uv_y_bounds=[np.min(spec['local_uv_y'],axis=0),np.max(spec['local_uv_y'],axis=0)],visual_acceptance=False))
    # Keep a native checkpoint even if the inherited full-shape camera cannot
    # frame this new form. Stop before rendering instead of silently reframing.
    c.camera_resolution(scene,bpy.data.objects['VIEW58F_1216-source-front'])
    text=bpy.data.texts.new('EDIT58F_control_structure.py');text.write((P/'patch58f.py').read_text())
    bpy.context.view_layer.objects.active=bank;bank.select_set(True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=True,check_existing=True)
    report=dict(passed=checks['passed'] and all(r['passed'] for r in cameras),build_pid=os.getpid(),source_sha256=c.sha(SOURCE),source_bytes=SOURCE.stat().st_size,
                vertices=182,triangles=360,groups=len(spec['groups']),cameras=cameras,source_identity=checks,
                final_geometry_pass=False,rendered=False,visual_acceptance=False)
    c.write(out/'build-result58f.json',report);print(json.dumps(dict(passed=report['passed'],source_bytes=report['source_bytes'])),flush=True)
    assert report['passed'],'Preserve source/checks; camera or source gate failed. No auto-reframe or repair'


def render(out,name):
    frame,settings,reference,spec=expected_inputs();digest=c.sha(SOURCE);build_result=json.loads((out/'build-result58f.json').read_text())
    assert build_result['passed'] and digest==build_result['source_sha256'] and os.getpid()!=build_result['build_pid']
    image=out/('58F-'+name+'.png');proof=out/(name+'-proof.json');assert not image.exists() and not proof.exists()
    state=dict(state='running',passed=False,view=name,pid=os.getpid(),source_sha256=digest,visual_acceptance=False);c.write(proof,state)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;bank=bpy.data.objects[NAME]
    identity=native_identity(bank,spec,frame);assert identity['passed'] and bank['patch_source_sha256']==c.sha(P/'patch58f.py')
    layer=scene.view_layers[0].layer_collection.children['EDIT58F_shared_surface'];collection=bpy.data.collections['EDIT58F_shared_surface']
    assert not layer.exclude and not layer.hide_viewport and not collection.hide_render and not collection.hide_viewport
    assert sum(ob.type=='MESH' for ob in bpy.data.objects)==1 and len(bpy.data.images)==0 and len(bpy.data.libraries)==0
    camera=bpy.data.objects['VIEW58F_'+name];camera_report=c.camera_proof(scene,camera,[bank.matrix_world@v.co for v in bank.data.vertices],frame,settings)
    expected=next(r for r in reference['cameras'] if r['name']==name)
    assert camera_report['passed'] and camera_report['matrix_world']==expected['matrix_world'] and camera_report['projection']==expected['projection']
    material=bank.data.materials[0];bsdf=material.node_tree.nodes['Principled BSDF']
    assert len(bpy.data.materials)==1 and sorted(n.bl_idname for n in material.node_tree.nodes)==['ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial']
    assert np.array_equal(np.asarray(bsdf.inputs['Base Color'].default_value),np.asarray(settings['material_linear_rgba'],np.float32).astype(float)) and abs(bsdf.inputs['Roughness'].default_value-settings['material_roughness'])<1e-7
    bg=scene.world.node_tree.nodes['Background'];sun=bpy.data.objects['58F fixed Sun']
    assert np.array_equal(np.asarray(bg.inputs['Color'].default_value),np.asarray(settings['world_linear_rgba'],np.float32).astype(float)) and abs(bg.inputs['Strength'].default_value-settings['world_strength'])<1e-7
    assert sun.data.energy==settings['sun_energy'] and abs(sun.data.angle-settings['sun_angle_radians'])<1e-7 and np.array_equal(np.asarray(sun.rotation_euler),np.asarray(settings['sun_source_rotation_xyz_radians'],np.float32).astype(float))
    assert scene.render.engine=='CYCLES' and scene.cycles.device=='CPU' and scene.cycles.samples==8 and not scene.cycles.use_denoising and scene.render.threads==2
    assert not scene.use_nodes and scene.view_settings.view_transform=='Standard' and scene.view_settings.look=='None' and scene.view_settings.exposure==0 and scene.view_settings.gamma==1
    scene.render.use_compositing=False;scene.render.use_sequencer=False;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8';scene.render.filepath=str(image)
    state.update(native_identity=identity,camera=camera_report,material_and_lighting_unchanged=True,renderer=dict(engine='CYCLES',device='CPU',samples=8,threads=2,denoising=False));c.write(proof,state)
    bpy.ops.render.render(write_still=True);assert image.exists() and c.sha(SOURCE)==digest
    state.update(state='completed',passed=True,image_sha256=c.sha(image),image_bytes=image.stat().st_size,source_unchanged=True,source_saved=False,world_loaded=False,final_geometry_pass=False)
    c.write(proof,state);print(json.dumps(dict(passed=True,view=name,image_bytes=image.stat().st_size)),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['build','render'],required=True);parser.add_argument('--view',choices=VIEWS);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);assert args.out.is_dir() and bpy.app.version[:3]==(4,5,14)
    c.write(args.out/'current-stage.json',dict(state='running',mode=args.mode,view=args.view,pid=os.getpid()))
    if args.mode=='build':build(args.out)
    else:assert args.view;render(args.out,args.view)
    c.write(args.out/'current-stage.json',dict(state='completed',mode=args.mode,view=args.view,pid=os.getpid()))


if __name__=='__main__':main()
