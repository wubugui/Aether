"""One bounded G native build, or one fresh unmodified source image.

Never run as preparation. Each invocation records a terminal stage on failure.
Only the scheduled wrapper may launch this script with Blender.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback
import bpy
import numpy as np
from mathutils import Matrix

P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import common58d as c
patch=c.load_pure(P/'patch58g.py')
rebuild=c.load_pure(P/'rebuild58g.py')
SOURCE=P/'field_patch58g.blend'
E_SOURCE=P.parent/'revision-e/B_staggered_crowns.blend'
E_REPORT=c.ROOT/'cloud-evidence/cloudbank58e-layouts-20261001T165946Z-yove55lx/outputs/build-result58e.json'
VIEWS=['1216-source-front','shared-side-back']
MAX_SOURCE_BYTES=200000
TEXT_FILES={'FIELD58G_patch.py':'patch58g.py','EDIT58G_rebuild.py':'rebuild58g.py','CONTROL58G.json':'controls58g.json'}


def inputs():
    frame=json.loads(c.PLAN.read_text());settings=json.loads(c.SETTINGS.read_text())
    config=json.loads((P/'controls58g.json').read_text())
    reference=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns')
    assert c.sha(E_SOURCE)==reference['source_sha256']
    assert settings['complete_shape_minimum_margin']==.07
    return frame,settings,config,reference


def text_digest(text):return hashlib.sha256(text.encode()).hexdigest()


def control_identity():
    # Persistent native transform components, rather than recomputed world
    # matrices whose last bits can differ after decomposition/readback.
    return [dict(name=ob.name,location=list(ob.location),rotation_mode=ob.rotation_mode,
                 rotation_euler=list(ob.rotation_euler),scale=list(ob.scale),
                 field_strength=float(ob['field_strength']),control_id=ob['control_id'],role=ob['role'])
            for ob in sorted(bpy.data.collections[rebuild.CONTROL_COLLECTION].objects,key=lambda ob:ob.name)]


def native_identity(bank):
    vertices,faces=rebuild.geometry_arrays(bank)
    controls=control_identity()
    texts={name:text_digest(bpy.data.texts[name].as_string()) for name in TEXT_FILES}
    group_names=sorted(g.name for g in bank.vertex_groups)
    config=json.loads((P/'controls58g.json').read_text())
    checks=dict(single_mesh=sum(ob.type=='MESH' for ob in bpy.data.objects)==1,
                no_intermediate_mesh=len(bpy.data.meshes)==1,nonempty=len(vertices)>3 and len(faces)>3,
                no_modifiers=len(bank.modifiers)==0,flat_faces=all(not f.use_smooth for f in bank.data.polygons),
                matrix_identity=np.array_equal(np.asarray(bank.matrix_world),np.eye(4)),
                effective_visible=bank.visible_get() and not bank.hide_render and not bank.hide_viewport and not bank.hide_get(),
                exact_control_names=[r['control_id'] for r in controls]==sorted(r['id'] for r in config['controls']),
                native_empty_controls=all(ob.type=='EMPTY' and ob.parent is None and len(ob.constraints)==0
                                         for ob in bpy.data.collections[rebuild.CONTROL_COLLECTION].objects),
                exact_edit_group_names=group_names==sorted('FIELD_'+r['id'] for r in config['controls']),
                embedded_texts_match_files=all(texts[name]==c.sha(P/file) for name,file in TEXT_FILES.items()),
                no_external_data=len(bpy.data.images)==0 and len(bpy.data.libraries)==0,
                autoexec_disabled=not bpy.context.preferences.filepaths.use_scripts_auto_execute)
    return dict(checks=checks,passed=all(checks.values()),mesh=patch.fingerprint(vertices,faces),
                group_sha256=rebuild.group_signature(bank),controls=controls,text_sha256=texts,
                final_geometry_pass=False,visual_acceptance=False)


def light_material_identity(scene,bank,settings):
    material=bank.data.materials[0];bsdf=material.node_tree.nodes['Principled BSDF']
    assert len(bpy.data.materials)==1 and len(bank.data.materials)==1
    assert sorted(n.bl_idname for n in material.node_tree.nodes)==['ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial']
    assert np.array_equal(np.asarray(bsdf.inputs['Base Color'].default_value),np.asarray(settings['material_linear_rgba'],np.float32).astype(float))
    assert abs(bsdf.inputs['Roughness'].default_value-settings['material_roughness'])<1e-7
    bg=scene.world.node_tree.nodes['Background'];sun=bpy.data.objects['58G fixed Sun']
    assert np.array_equal(np.asarray(bg.inputs['Color'].default_value),np.asarray(settings['world_linear_rgba'],np.float32).astype(float))
    assert abs(bg.inputs['Strength'].default_value-settings['world_strength'])<1e-7
    assert sun.data.energy==settings['sun_energy'] and abs(sun.data.angle-settings['sun_angle_radians'])<1e-7
    assert np.array_equal(np.asarray(sun.rotation_euler),np.asarray(settings['sun_source_rotation_xyz_radians'],np.float32).astype(float))
    assert scene.render.engine=='CYCLES' and scene.cycles.device=='CPU' and scene.cycles.samples==8
    assert not scene.cycles.use_denoising and scene.render.threads_mode=='FIXED' and scene.render.threads==2
    assert scene.view_settings.view_transform=='Standard' and scene.view_settings.look=='None'
    assert scene.view_settings.exposure==0 and scene.view_settings.gamma==1 and not scene.use_nodes
    return True


def cameras(scene,bank,frame,settings,reference):
    rows=[]
    for name in VIEWS:
        ob=bpy.data.objects['VIEW58G_'+name]
        row=c.camera_proof(scene,ob,[bank.matrix_world@v.co for v in bank.data.vertices],frame,settings)
        expected=next(r for r in reference['cameras'] if r['name']==name)
        row['same_E_camera_matrix']=row['matrix_world']==expected['matrix_world']
        row['same_E_camera_projection']=row['projection']==expected['projection']
        row['passed']=bool(row['passed'] and row['same_E_camera_matrix'] and row['same_E_camera_projection'])
        rows.append(row)
    return rows


def build(out):
    assert not SOURCE.exists(),'Preserve every existing candidate; never overwrite or retry in place'
    frame,settings,config,reference=inputs()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.context.preferences.filepaths.use_scripts_auto_execute=False
    for store in (bpy.data.meshes,bpy.data.materials,bpy.data.cameras,bpy.data.lights,bpy.data.images):
        for block in list(store):
            if block.users==0:store.remove(block)
    scene=bpy.context.scene
    for name in ('EDIT58G_surface',rebuild.CONTROL_COLLECTION,'VIEW58G_frozen_camera_lighting'):
        scene.collection.children.link(bpy.data.collections.new(name))
    scene['source_frame58g_json']=json.dumps({key:frame[key] for key in ('anchor_godot_world_xyz','local_u_world','local_v_world')})
    scene['visual_acceptance']=False;scene['world_loaded']=False
    view=bpy.data.collections['VIEW58G_frozen_camera_lighting']
    with bpy.data.libraries.load(str(E_SOURCE),link=False) as (src,dst):
        dst.objects=['VIEW58E_'+name for name in VIEWS]
    assert len(bpy.data.meshes)==0 and all(ob is not None and ob.type=='CAMERA' for ob in dst.objects)
    for ob in dst.objects:view.objects.link(ob);ob.name='VIEW58G_'+ob['view_name']
    material=bpy.data.materials.new('58G same neutral source inspection');material.use_nodes=True
    bsdf=material.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=settings['material_linear_rgba']
    bsdf.inputs['Roughness'].default_value=settings['material_roughness']
    world=bpy.data.worlds.new('58G same fixed neutral world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=settings['world_linear_rgba']
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=settings['world_strength'];scene.world=world
    lamp=bpy.data.lights.new('58G fixed Sun','SUN');lamp.energy=settings['sun_energy'];lamp.angle=settings['sun_angle_radians']
    sun=bpy.data.objects.new(lamp.name,lamp);view.objects.link(sun);sun.rotation_euler=settings['sun_source_rotation_xyz_radians']
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False
    scene.render.threads_mode='FIXED';scene.render.threads=2;scene.view_settings.view_transform='Standard'
    scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    for name,file in TEXT_FILES.items():bpy.data.texts.new(name).write((P/file).read_text())
    basis=patch.source_basis(frame)
    for row in config['controls']:
        ob=bpy.data.objects.new('CONTROL58G_'+row['id'],None)
        bpy.data.collections[rebuild.CONTROL_COLLECTION].objects.link(ob)
        matrix=np.eye(4);matrix[:3,:3]=basis@patch.rotation_xyz(row['rotation_xyz_degrees'])@np.diag(row['half_axes_m'])
        matrix[:3,3]=basis@np.asarray(row['center_uvy_m'])
        ob.matrix_world=Matrix(matrix.tolist());ob.empty_display_type='SPHERE';ob.empty_display_size=1.0
        ob.hide_render=True;ob['field_strength']=row['strength'];ob['control_id']=row['id'];ob['role']=row['role']
        ob['edit_instructions']='Translate/rotate/scale this Empty, then explicitly run embedded EDIT58G_rebuild.py. Scale is nominal half-axes in metres.'
    bpy.context.view_layer.update()
    report=dict(candidate='58G',state='running',passed=False,build_pid=os.getpid(),native_identity=None,cameras=[],
                field_design_hypothesis=True,world_loaded=False,final_geometry_pass=False,visual_acceptance=False)
    caught=None
    try:
        bank,geometry=rebuild.rebuild_from_controls();bpy.context.view_layer.update()
        report['geometry']=geometry;c.write(out/'pre-save-check58g.json',report)
        identity=native_identity(bank)
        report['native_identity']=identity;c.write(out/'pre-save-check58g.json',report)
        rows=cameras(scene,bank,frame,settings,reference)
        report['cameras']=rows;c.write(out/'pre-save-check58g.json',report)
        light_material_identity(scene,bank,settings)
        report.update(geometry=geometry,native_identity=identity,cameras=rows,
                      material_and_lighting_unchanged=True)
        report['passed']=bool(geometry['passed'] and identity['passed'] and all(r['passed'] for r in rows))
    except BaseException:
        caught=traceback.format_exc();report.update(error=caught,passed=False)
    finally:
        omitted=[]
        for ob in list(bpy.data.objects):
            if ob.type=='MESH' and not ob.get('collapse_applied58g',False):
                omitted.append(dict(name=ob.name,raw_extraction_proof=ob.get('raw_extraction_proof58g_json'),
                                    reason='Extraction intermediate is reproducible from embedded controls, never persisted as a high-poly asset'))
                intermediate=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
                if intermediate.users==0:bpy.data.meshes.remove(intermediate)
        if omitted:report['omitted_unsaved_raw_intermediates']=omitted
        c.camera_resolution(scene,bpy.data.objects['VIEW58G_1216-source-front'])
        c.write(out/'pre-save-check58g.json',report)
        bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=True,check_existing=True)
        report.update(state='completed',source_sha256=c.sha(SOURCE),source_bytes=SOURCE.stat().st_size,
                      source_within_200000_bytes=SOURCE.stat().st_size<=MAX_SOURCE_BYTES)
        report['passed']=bool(report['passed'] and report['source_within_200000_bytes'])
        if not report['source_within_200000_bytes']:
            report['stop_reason']='Source exceeds 200000 bytes; source/control data retained, no automatic stripping or renders'
        c.write(out/'build-result58g.json',report)
    print(json.dumps(c.native(report),indent=2),flush=True)
    assert report['passed'],'G native candidate saved but guard failed; preserve it and stop. No auto-fit or repair.'


def render(out,name):
    frame,settings,config,reference=inputs();before=c.sha(SOURCE)
    built=json.loads((out/'build-result58g.json').read_text())
    assert built['passed'] and before==built['source_sha256'] and os.getpid()!=built['build_pid']
    image=out/('58G-'+name+'.png');proof=out/(name+'-proof.json')
    assert not image.exists() and not proof.exists()
    state=dict(state='running',passed=False,view=name,pid=os.getpid(),source_sha256=before,
               world_loaded=False,final_geometry_pass=False,visual_acceptance=False)
    c.write(proof,state)
    try:
        bpy.context.preferences.filepaths.use_scripts_auto_execute=False
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;bank=bpy.data.objects[rebuild.BANK_NAME]
        identity=native_identity(bank)
        assert identity['passed'] and identity==built['native_identity'],'Fresh native geometry, controls, texts or identity changed'
        assert light_material_identity(scene,bank,settings)
        rows=cameras(scene,bank,frame,settings,reference)
        assert rows==built['cameras'] and all(r['passed'] for r in rows),'Camera or projection changed after source reload'
        camera=bpy.data.objects['VIEW58G_'+name];c.camera_resolution(scene,camera)
        scene.render.use_compositing=False;scene.render.use_sequencer=False
        scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
        scene.render.image_settings.color_depth='8';scene.render.filepath=str(image)
        state.update(native_identity=identity,camera=next(r for r in rows if r['name']==name),
                     material_and_lighting_unchanged=True,renderer=dict(engine='CYCLES',device='CPU',samples=8,threads=2,denoising=False))
        c.write(proof,state)
        bpy.ops.render.render(write_still=True)
        assert image.exists() and c.sha(SOURCE)==before
        state.update(passed=True,image_sha256=c.sha(image),image_bytes=image.stat().st_size)
    except BaseException:
        state.update(error=traceback.format_exc(),passed=False)
        raise
    finally:
        state.update(state='completed',source_sha256_after=c.sha(SOURCE),source_unchanged=c.sha(SOURCE)==before,source_saved=False)
        c.write(proof,state)
    print(json.dumps(c.native(state),indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['build','render'],required=True)
    parser.add_argument('--view',choices=VIEWS);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert args.out.is_dir() and bpy.app.version[:3]==(4,5,14)
    state=dict(state='running',mode=args.mode,view=args.view,pid=os.getpid(),passed=False)
    c.write(args.out/'current-stage.json',state)
    try:
        if args.mode=='build':build(args.out)
        else:
            assert args.view;render(args.out,args.view)
        state['passed']=True
    except BaseException:
        state['error']=traceback.format_exc();raise
    finally:
        state['state']='completed';c.write(args.out/'current-stage.json',state)


if __name__=='__main__':main()
