"""One scheduled source image in one fresh Blender process; never save source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import bpy
import numpy as np

P=Path(__file__).resolve().parent
N=P.parent/'native-01'
sys.path.insert(0,str(N))
import common58d as c

NATIVE_RUN=c.ROOT/'cloud-evidence/cloudbank58d-native-20261001T162033Z-y035f3f3'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--view',choices=['1216-source-front','back','side','underside','top'],required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert args.out.is_dir()
    image=args.out/('cloudbank58d-'+args.view+'.png')
    proof_path=args.out/(args.view+'-image-proof.json')
    assert not image.exists() and not proof_path.exists(),'Preserve existing image evidence'
    start=time.monotonic()
    state=dict(state='running',passed=False,view=args.view,pid=os.getpid(),world_loaded=False,visual_acceptance=False)
    c.write(proof_path,state)
    digest=c.sha(c.SOURCE)
    native=json.loads((NATIVE_RUN/'outputs/fresh-readback58d.json').read_text())
    assert native['passed'] and native['source_sha256']==digest
    plan,cage,settings=c.frozen_inputs()
    assert bpy.app.version[:3]==(4,5,14)
    bpy.ops.wm.open_mainfile(filepath=str(c.SOURCE))
    scene=bpy.context.scene
    bank=bpy.data.objects[c.MESH_NAME]
    cam=bpy.data.objects['VIEW58D_'+args.view]
    expected=next(row for row in native['cameras'] if row['name']==args.view)
    vertices=[bank.matrix_world@v.co for v in bank.data.vertices]
    camera=c.camera_proof(scene,cam,vertices,plan,settings)
    assert camera['passed'] and camera['matrix_world']==expected['matrix_world']
    assert camera['projection']==expected['projection']
    assert len(bank.data.vertices)==325 and len(bank.data.polygons)==646 and len(bank.modifiers)==0
    assert all(not face.use_smooth for face in bank.data.polygons)
    actual=np.asarray([tuple(v.co) for v in bank.data.vertices],float)
    assert np.array_equal(actual,c.source_coordinates(cage['vertices'],plan).astype(np.float32).astype(float))
    assert [list(f.vertices) for f in bank.data.polygons]==cage['faces']
    source_collection=bpy.data.collections['SOURCE58D']
    source_layer=scene.view_layers[0].layer_collection.children['SOURCE58D']
    guides=bpy.data.collections['EDIT58D_authored_curve_guides']
    visibility=dict(mesh_visible=bank.visible_get() and not bank.hide_get() and not bank.hide_render and not bank.hide_viewport,
                    source_collection_visible=not source_collection.hide_render and not source_collection.hide_viewport,
                    source_layer_visible=not source_layer.exclude and not source_layer.hide_viewport,
                    guide_collection_hidden=guides.hide_render,all_guide_objects_hidden=all(ob.hide_render for ob in guides.objects))
    assert all(visibility.values())
    mat=bank.data.materials[0]
    bsdf=mat.node_tree.nodes['Principled BSDF']
    assert sorted(node.bl_idname for node in mat.node_tree.nodes)==['ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial']
    assert [(l.from_node.bl_idname,l.from_socket.name,l.to_node.bl_idname,l.to_socket.name) for l in mat.node_tree.links]==[('ShaderNodeBsdfPrincipled','BSDF','ShaderNodeOutputMaterial','Surface')]
    assert np.array_equal(np.asarray(bsdf.inputs['Base Color'].default_value),np.asarray(settings['material_linear_rgba'],dtype=np.float32).astype(float))
    assert abs(bsdf.inputs['Roughness'].default_value-settings['material_roughness'])<1e-7
    background=scene.world.node_tree.nodes['Background']
    assert np.array_equal(np.asarray(background.inputs['Color'].default_value),np.asarray(settings['world_linear_rgba'],dtype=np.float32).astype(float))
    assert abs(background.inputs['Strength'].default_value-settings['world_strength'])<1e-7
    sun=bpy.data.objects['58D fixed Sun']
    assert sun.data.type=='SUN' and sun.data.energy==settings['sun_energy'] and abs(sun.data.angle-settings['sun_angle_radians'])<1e-7
    assert np.array_equal(np.asarray(sun.rotation_euler),np.asarray(settings['sun_source_rotation_xyz_radians'],dtype=np.float32).astype(float))
    assert len(bpy.data.images)==0 and len(bpy.data.libraries)==0
    assert scene.render.engine=='CYCLES' and scene.cycles.device=='CPU' and scene.cycles.samples==8
    assert not scene.cycles.use_denoising and scene.render.threads_mode=='FIXED' and scene.render.threads==2
    assert not scene.use_nodes,'No compositor postprocessing permitted'
    assert scene.view_settings.view_transform=='Standard' and scene.view_settings.look=='None'
    assert scene.view_settings.exposure==0 and scene.view_settings.gamma==1
    # Output controls only. Geometry, lighting, cameras and color settings stay saved.
    scene.render.use_compositing=False
    scene.render.use_sequencer=False
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    scene.render.image_settings.color_depth='8'
    scene.render.filepath=str(image)
    state.update(source_sha256=digest,source_bytes=c.SOURCE.stat().st_size,camera=camera,
                 effective_visibility=visibility,geometry_exact=True,material_and_lighting_unchanged=True,
                 renderer=dict(engine=scene.render.engine,device=scene.cycles.device,samples=scene.cycles.samples,
                               denoising=scene.cycles.use_denoising,threads=scene.render.threads,
                               resolution_xy=[scene.render.resolution_x,scene.render.resolution_y],
                               pixel_aspect_xy=[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],
                               view_transform=scene.view_settings.view_transform,look=scene.view_settings.look,
                               exposure=scene.view_settings.exposure,gamma=scene.view_settings.gamma,
                               compositor=False,sequencer=False,output='Blender-rendered RGB8 PNG, no external image processing'),
                 front_crop_notice='The exact 1216 front crops the underside; full shape is assessed in the other four views.' if args.view=='1216-source-front' else None)
    c.write(proof_path,state)
    print(json.dumps(dict(view=args.view,state='rendering',pid=os.getpid(),source_sha256=digest)),flush=True)
    bpy.ops.render.render(write_still=True)
    assert image.exists() and c.sha(c.SOURCE)==digest
    state.update(state='completed',passed=True,source_unchanged=True,source_saved=False,
                 image_name=image.name,image_sha256=c.sha(image),image_bytes=image.stat().st_size,
                 elapsed_seconds=time.monotonic()-start,hardware_gpu_acceptance=False,visual_acceptance=False)
    c.write(proof_path,state)
    print(json.dumps(dict(view=args.view,state='completed',image_sha256=state['image_sha256'],seconds=state['elapsed_seconds'])),flush=True)


if __name__=='__main__':
    main()
