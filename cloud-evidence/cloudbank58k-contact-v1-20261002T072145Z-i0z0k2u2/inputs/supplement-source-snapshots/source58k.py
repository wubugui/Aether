"""Scheduled native source build, independent saved-source verify, two views.

Never execute during preparation. Pre-save transient dependency counts are
recorded, not relabeled. Only a fresh open can mark the saved source valid.
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
poly=c.load_pure(P/'poly58k.py');rebuild=c.load_pure(P/'rebuild58k.py')
datablocks=c.load_pure(P.parent/'revision-g/inspection-01/inspect58g.py')
SOURCE=P/'authored_envelope58k.blend'
E_SOURCE=P.parent/'revision-e/B_staggered_crowns.blend'
E_REPORT=c.ROOT/'cloud-evidence/cloudbank58e-layouts-20261001T165946Z-yove55lx/outputs/build-result58e.json'
VIEWS=['1216-source-front','shared-side-back'];MAX_SOURCE_BYTES=200000
TEXT_FILES={'POLY58K_math.py':'poly58k.py','EDIT58K_rebuild.py':'rebuild58k.py','CONTROL58K.json':'design58k.json','CONTACT58K_check.py':'check_coplanar_contacts58k.py'}


def inputs():
    frame=json.loads(c.PLAN.read_text());settings=json.loads(c.SETTINGS.read_text());config=json.loads((P/'design58k.json').read_text())
    reference=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns')
    poly.require(c.sha(E_SOURCE)==reference['source_sha256'],'Original E source identity')
    poly.require(settings['complete_shape_minimum_margin']==.07,'Original seven percent margin')
    return frame,settings,config,reference


def native_identity(bank):
    V,F=rebuild.geometry_arrays(bank);config=json.loads((P/'design58k.json').read_text())
    controls=[dict(name=o.name,control_id=o['control_id'],role=o['role'],location=list(o.location),rotation_mode=o.rotation_mode,
                   rotation_euler=list(o.rotation_euler),scale=list(o.scale))
              for o in sorted(bpy.data.collections[rebuild.CONTROL_COLLECTION].objects,key=lambda o:o.name)]
    texts={name:hashlib.sha256(bpy.data.texts[name].as_string().encode()).hexdigest() for name in TEXT_FILES}
    attributes={name:[d.value for d in bank.data.attributes[name].data] for name in ('semantic_region','authored_patch','authored_station','authored_sector')}
    checks=dict(single_mesh=sum(o.type=='MESH' for o in bpy.data.objects)==1 and len(bpy.data.meshes)==1,
        no_modifiers=len(bank.modifiers)==0,flat_faces=all(not f.use_smooth for f in bank.data.polygons),
        matrix_identity=np.array_equal(np.asarray(bank.matrix_world),np.eye(4)),
        effective_visible=bank.visible_get() and not bank.hide_render and not bank.hide_viewport and not bank.hide_get(),
        six_controls=[r['control_id'] for r in controls]==sorted(r['id'] for r in config['controls']),
        native_empty_controls=all(o.type=='EMPTY' and o.parent is None and len(o.constraints)==0 for o in bpy.data.collections[rebuild.CONTROL_COLLECTION].objects),
        six_groups=sorted(g.name for g in bank.vertex_groups)==sorted('REGION_'+r['id'] for r in config['controls']),
        texts_match=all(texts[name]==c.sha(P/file) for name,file in TEXT_FILES.items()),
        autoexec_disabled=not bpy.context.preferences.filepaths.use_scripts_auto_execute)
    return dict(passed=all(checks.values()),checks=checks,mesh=poly.fingerprint(V,F),group_sha256=rebuild.group_signature(bank),
        attributes=attributes,controls=controls,text_sha256=texts,construction_proof=bank['construction_proof_json'],
        source_frame=bpy.context.scene['source_frame58k_json'],visual_acceptance=False)


def dependency_state():
    row=datablocks.inventory();row['strict_saved_source_dependencies_passed']=bool(not row['images'] and not row['libraries'] and not row['all_strongly_linked_ids'])
    return row


exec(compile((P/'native_helpers58k.py').read_bytes(),str(P/'native_helpers58k.py'),'exec'))


def build(out):
    poly.require(not SOURCE.exists(),'Never overwrite prior candidate source')
    frame,settings,config,reference=inputs()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.context.preferences.filepaths.use_scripts_auto_execute=False
    report=dict(candidate='58K',state='running',candidate_created=False,saved_source_validated=False,build_pid=os.getpid(),visual_acceptance=False)
    report['startup_datablocks']=dependency_state();c.write(out/'build-result58k.json',report)
    scene=bpy.context.scene
    for name in ('EDIT58K_surface',rebuild.CONTROL_COLLECTION,'VIEW58K_frozen_camera_lighting'):
        scene.collection.children.link(bpy.data.collections.new(name))
    scene['source_frame58k_json']=json.dumps({key:frame[key] for key in ('anchor_godot_world_xyz','local_u_world','local_v_world')})
    scene['visual_acceptance']=False;scene['world_loaded']=False
    view=bpy.data.collections['VIEW58K_frozen_camera_lighting']
    with bpy.data.libraries.load(str(E_SOURCE),link=False) as (src,dst):dst.objects=['VIEW58E_'+name for name in VIEWS]
    poly.require(all(o and o.type=='CAMERA' for o in dst.objects),'Two original cameras')
    for o in dst.objects:view.objects.link(o);o.name='VIEW58K_'+o['view_name']
    material=bpy.data.materials.new('58K same neutral source inspection');material.use_nodes=True
    bsdf=material.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=settings['material_linear_rgba'];bsdf.inputs['Roughness'].default_value=settings['material_roughness']
    world=bpy.data.worlds.new('58K same fixed neutral world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=settings['world_linear_rgba'];world.node_tree.nodes['Background'].inputs['Strength'].default_value=settings['world_strength'];scene.world=world
    lamp=bpy.data.lights.new('58K fixed Sun','SUN');lamp.energy=settings['sun_energy'];lamp.angle=settings['sun_angle_radians']
    sun=bpy.data.objects.new(lamp.name,lamp);view.objects.link(sun);sun.rotation_euler=settings['sun_source_rotation_xyz_radians']
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False
    scene.render.threads_mode='FIXED';scene.render.threads=2;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    for name,file in TEXT_FILES.items():bpy.data.texts.new(name).write((P/file).read_text())
    basis=poly.source_basis(frame)
    for row in config['controls']:
        angle=np.radians(row['yaw_degrees']);co,si=np.cos(angle),np.sin(angle);R=np.array([[co,-si,0],[si,co,0],[0,0,1]])
        ob=bpy.data.objects.new('CONTROL58K_'+row['id'],None);bpy.data.collections[rebuild.CONTROL_COLLECTION].objects.link(ob)
        m=np.eye(4);m[:3,:3]=basis@R@np.diag(row['scale']);m[:3,3]=basis@row['center'];ob.matrix_world=Matrix(m.tolist())
        ob.empty_display_type='CUBE';ob.empty_display_size=1;ob.hide_render=True;ob['control_id']=row['id'];ob['role']=row['role']
        ob['edit_instructions']='Edit this semantic transform, or the station rings and explicit patch diagonals in CONTROL58K.json; explicitly run EDIT58K_rebuild.py. No automatic save or render.'
    bpy.context.view_layer.update()
    try:
        bank,geometry=rebuild.rebuild_from_controls();bpy.context.view_layer.update()
        report.update(geometry=geometry,native_identity=native_identity(bank),cameras=cameras(scene,bank,frame,settings,reference))
        light_material_identity(scene,bank,settings)
        report['pre_save_datablocks']=dependency_state()
        report['pre_save_geometry_controls_views_passed']=bool(report['native_identity']['passed'] and all(r['passed'] for r in report['cameras']))
        poly.require(report['pre_save_geometry_controls_views_passed'],'Pre-save geometry/control/view guard')
        c.camera_resolution(scene,bpy.data.objects['VIEW58K_'+VIEWS[0]])
        # No datablock purge. Saved-source dependency identity is decided only
        # by a separate fresh process, regardless of this transient inventory.
        bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),compress=True,check_existing=True)
        report.update(candidate_created=True,source_sha256=c.sha(SOURCE),source_bytes=SOURCE.stat().st_size)
        poly.require(SOURCE.stat().st_size<=MAX_SOURCE_BYTES,'Source size exceeds 200000 bytes')
    except BaseException:
        report['error']=traceback.format_exc();raise
    finally:
        report['state']='completed';c.write(out/'build-result58k.json',report)


def fresh(out,mode,name=None):
    frame,settings,config,reference=inputs();built=json.loads((out/'build-result58k.json').read_text())
    before=c.sha(SOURCE);poly.require(built['candidate_created'] and before==built['source_sha256'],'Saved source exact identity')
    poly.require(os.getpid()!=built['build_pid'],'Fresh process required')
    file=out/('saved-source-verify58k.json' if mode=='verify' else name+'-proof.json')
    poly.require(not file.exists(),'Never replace previous readback evidence')
    state=dict(state='running',passed=False,pid=os.getpid(),source_sha256=before,source_saved=False,visual_acceptance=False)
    c.write(file,state)
    try:
        bpy.context.preferences.filepaths.use_scripts_auto_execute=False
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;bank=bpy.data.objects[rebuild.BANK_NAME]
        state['loaded_datablocks']=dependency_state();c.write(file,state)
        poly.require(state['loaded_datablocks']['strict_saved_source_dependencies_passed'],'Saved source has external/image dependency')
        identity=native_identity(bank);state['native_identity']=identity
        poly.require(identity['passed'] and identity==built['native_identity'],'Full saved identity differs')
        rows=cameras(scene,bank,frame,settings,reference);state['cameras']=rows
        poly.require(rows==built['cameras'] and all(r['passed'] for r in rows),'Fixed cameras/projection changed')
        light_material_identity(scene,bank,settings)
        if mode=='verify':
            V,F=rebuild.geometry_arrays(bank)
            state['readback_topology']=poly.topology(V,F,config['tolerances']);state['readback_intersections']=poly.intersection_check(V,F,eps=1e-8)
            state['saved_source_validated']=True
        else:
            verified=json.loads((out/'saved-source-verify58k.json').read_text())
            poly.require(verified['passed'] and verified['source_sha256']==before and verified['pid']!=os.getpid(),'Independent source verification required')
            camera=bpy.data.objects['VIEW58K_'+name];c.camera_resolution(scene,camera)
            image=out/('58K-'+name+'.png');poly.require(not image.exists(),'Never overwrite an image')
            scene.render.use_compositing=False;scene.render.use_sequencer=False
            scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8';scene.render.filepath=str(image)
            state.update(view=name,camera=next(r for r in rows if r['name']==name));c.write(file,state)
            bpy.ops.render.render(write_still=True)
            state.update(image_sha256=c.sha(image),image_bytes=image.stat().st_size)
        state['passed']=True
    except BaseException:
        state['error']=traceback.format_exc();raise
    finally:
        state.update(state='completed',source_sha256_after=c.sha(SOURCE),source_unchanged=c.sha(SOURCE)==before)
        state['passed']=bool(state['passed'] and state['source_unchanged']);c.write(file,state)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['build','verify','render'],required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--view',choices=VIEWS)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(parents=True,exist_ok=True)
    if args.mode=='build':build(args.out)
    else:fresh(args.out,args.mode,args.view)


if __name__=='__main__':main()
