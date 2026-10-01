"""Read one E source fresh and render one saved camera, without saving source."""
import argparse,json,os,sys,time
from collections import Counter
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import layouts58e as layouts
import common58d as c


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--layout',choices=list(layouts.LAYOUTS),required=True)
    parser.add_argument('--view',choices=['1216-source-front','shared-side-back'],required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);start=time.monotonic()
    source=P/(args.layout+'.blend');digest=c.sha(source);build=json.loads((args.out/'build-result58e.json').read_text())
    saved=next(r for r in build['layouts'] if r['layout']==args.layout)
    assert build['passed'] and digest==saved['source_sha256'] and build['pid']!=os.getpid()
    proof_path=args.out/(args.layout+'-'+args.view+'-proof.json');image=args.out/(args.layout+'-'+args.view+'.png')
    assert not proof_path.exists() and not image.exists()
    state=dict(state='running',passed=False,layout=args.layout,view=args.view,pid=os.getpid(),source_sha256=digest,single_shell=False,visual_acceptance=False)
    c.write(proof_path,state);bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
    frame=json.loads(c.PLAN.read_text());settings=json.loads(c.SETTINGS.read_text());parts=[];vertices=[]
    assert scene['layout_id']==args.layout and not scene['single_shell'] and scene['layout_script_sha256']==c.sha(P/'layouts58e.py')
    collection=bpy.data.collections['EDIT58E_four_layout_parts'];layer=scene.view_layers[0].layer_collection.children[collection.name]
    assert not collection.hide_render and not collection.hide_viewport and not layer.exclude and not layer.hide_viewport
    assert sorted(o.name for o in bpy.data.objects if o.type=='MESH')==sorted(s['id'] for s in layouts.LAYOUTS[args.layout])
    for spec in layouts.LAYOUTS[args.layout]:
        ob=bpy.data.objects[spec['id']];world,faces=layouts.world_vertices(spec,frame)
        expected=c.source_coordinates(world,frame).astype(np.float32).astype(float);actual=np.asarray([list(v.co) for v in ob.data.vertices],float)
        actual_faces=[list(f.vertices) for f in ob.data.polygons]
        assert np.array_equal(actual,expected) and actual_faces==faces and len(faces)>0
        assert np.array_equal(np.asarray(ob.matrix_world),np.eye(4)) and not ob.modifiers
        assert ob.visible_get() and not ob.hide_render and all(not f.use_smooth for f in ob.data.polygons)
        assert json.loads(ob['design_json'])==spec
        edges=Counter(tuple(sorted((a,b))) for f in actual_faces for a,b in zip(f,f[1:]+f[:1]))
        assert all(value==2 for value in edges.values()),'Individual control part has an open/nonmanifold edge'
        parts.append(dict(id=spec['id'],vertices=len(actual),triangles=len(faces),float32_identity_exact=True,edge_incidence_two=True,visible=True))
        vertices.extend(ob.matrix_world@v.co for v in ob.data.vertices)
    camera=bpy.data.objects['VIEW58E_'+args.view];camera_report=c.camera_proof(scene,camera,vertices,frame,settings)
    expected=next(r for r in saved['cameras'] if r['name']==args.view)
    assert camera_report['passed'] and camera_report['matrix_world']==expected['matrix_world'] and camera_report['projection']==expected['projection']
    if args.view=='shared-side-back':
        cameras=[next(r for r in candidate['cameras'] if r['name']==args.view) for candidate in build['layouts']]
        assert cameras[0]['matrix_world']==cameras[1]['matrix_world'] and cameras[0]['projection']==cameras[1]['projection']
    assert len(bpy.data.materials)==1 and len(bpy.data.images)==0 and len(bpy.data.libraries)==0
    material=bpy.data.materials[0];bsdf=material.node_tree.nodes['Principled BSDF']
    assert sorted(n.bl_idname for n in material.node_tree.nodes)==['ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial']
    assert np.array_equal(np.asarray(bsdf.inputs['Base Color'].default_value),np.asarray(settings['material_linear_rgba'],np.float32).astype(float))
    assert abs(bsdf.inputs['Roughness'].default_value-settings['material_roughness'])<1e-7
    background=scene.world.node_tree.nodes['Background'];sun=bpy.data.objects['58E fixed Sun']
    assert np.array_equal(np.asarray(background.inputs['Color'].default_value),np.asarray(settings['world_linear_rgba'],np.float32).astype(float))
    assert abs(background.inputs['Strength'].default_value-settings['world_strength'])<1e-7 and sun.data.energy==settings['sun_energy']
    assert abs(sun.data.angle-settings['sun_angle_radians'])<1e-7 and np.array_equal(np.asarray(sun.rotation_euler),np.asarray(settings['sun_source_rotation_xyz_radians'],np.float32).astype(float))
    assert scene.render.engine=='CYCLES' and scene.cycles.device=='CPU' and scene.cycles.samples==8 and not scene.cycles.use_denoising
    assert scene.render.threads_mode=='FIXED' and scene.render.threads==2 and not scene.use_nodes
    assert scene.view_settings.view_transform=='Standard' and scene.view_settings.look=='None' and scene.view_settings.exposure==0 and scene.view_settings.gamma==1
    scene.render.use_compositing=False;scene.render.use_sequencer=False;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8';scene.render.filepath=str(image)
    state.update(parts=parts,camera=camera_report,renderer=dict(engine='CYCLES',device='CPU',samples=8,threads=2,denoising=False),
                 material_and_lighting_match_frozen_settings=True,front_crop_measured_not_reframed=args.view=='1216-source-front')
    c.write(proof_path,state);bpy.ops.render.render(write_still=True)
    assert image.exists() and c.sha(source)==digest
    state.update(state='completed',passed=True,image_sha256=c.sha(image),image_bytes=image.stat().st_size,source_saved=False,source_unchanged=True,
                 elapsed_seconds=time.monotonic()-start,final_intersection_or_valley_validation_performed=False,world_loaded=False,visual_acceptance=False)
    c.write(proof_path,state);print(json.dumps(dict(layout=args.layout,view=args.view,passed=True)),flush=True)


if __name__=='__main__':main()
