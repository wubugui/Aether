"""Build two tiny editable layout sources; no rendering or union validation."""
import argparse,json,math,os,sys,time
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import layouts58e as layouts
import common58d as c


def camera(name,collection):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);collection.objects.link(ob)
    data.clip_start=.35;data.clip_end=18000
    return ob


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);start=time.monotonic()
    assert args.out.is_dir() and bpy.app.version[:3]==(4,5,14)
    assert not any((P/(name+'.blend')).exists() for name in layouts.LAYOUTS)
    frame=json.loads(c.PLAN.read_text());settings=json.loads(c.SETTINGS.read_text())
    # Geometry of E is independent; only the established world frame/camera and
    # neutral light/material settings are reused from the frozen D design.
    all_positions=[]
    for specs in layouts.LAYOUTS.values():
        for spec in specs:
            world,_=layouts.world_vertices(spec,frame);all_positions.extend(c.source_coordinates(world,frame))
    all_positions=[Vector(p) for p in all_positions]
    low=Vector([min(v[k] for v in all_positions) for k in range(3)])
    high=Vector([max(v[k] for v in all_positions) for k in range(3)])
    target=(low+high)/2;common_matrix=None;common_scale=None;common_location=None;common_rotation=None;results=[]
    for name,specs in layouts.LAYOUTS.items():
        c.write(args.out/'build-stage.json',dict(state='running',passed=False,layout=name,pid=os.getpid()))
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
        for store in [bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights,bpy.data.images]:
            for block in list(store):
                if block.users==0:store.remove(block)
        scene=bpy.context.scene;scene['layout_id']=name;scene['single_shell']=False
        scene['scope']='Four editable intersecting closed polyhedra for shape selection; no continuous-shell or flight proof'
        scene['design_dimensions_are_hypotheses']=True;scene['visual_acceptance']=False
        scene['layout_script_sha256']=c.sha(P/'layouts58e.py')
        collection=bpy.data.collections.new('EDIT58E_four_layout_parts');scene.collection.children.link(collection)
        view=bpy.data.collections.new('VIEW58E_shared_setup');scene.collection.children.link(view)
        material=bpy.data.materials.new('58E same neutral inspection');material.use_nodes=True
        bsdf=material.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=settings['material_linear_rgba'];bsdf.inputs['Roughness'].default_value=settings['material_roughness']
        rows=[]
        for spec in specs:
            world,faces=layouts.world_vertices(spec,frame);source=c.source_coordinates(world,frame).astype(np.float32)
            mesh=bpy.data.meshes.new(spec['id']);mesh.from_pydata(source.tolist(),[],faces);mesh.update()
            ob=bpy.data.objects.new(spec['id'],mesh);collection.objects.link(ob);mesh.materials.append(material)
            ob['role']=spec['role'];ob['design_json']=json.dumps(spec);ob['native_edit_instructions']='Edit this closed part directly; each part has its own crown, shoulders and underside'
            for face in mesh.polygons:face.use_smooth=False
            rows.append(dict(id=spec['id'],vertices=len(source),triangles=len(faces),closed_control_part=True))
        world=bpy.data.worlds.new('58E same fixed neutral world');world.use_nodes=True
        world.node_tree.nodes['Background'].inputs['Color'].default_value=settings['world_linear_rgba'];world.node_tree.nodes['Background'].inputs['Strength'].default_value=settings['world_strength'];scene.world=world
        sun_data=bpy.data.lights.new('58E fixed Sun','SUN');sun_data.energy=settings['sun_energy'];sun_data.angle=settings['sun_angle_radians'];sun=bpy.data.objects.new(sun_data.name,sun_data);view.objects.link(sun);sun.rotation_euler=settings['sun_source_rotation_xyz_radians']
        scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False
        scene.render.threads_mode='FIXED';scene.render.threads=2;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
        front=camera('VIEW58E_1216-source-front',view);front['view_name']='1216-source-front';front['resolution_xy']=[836,471];front['pixel_aspect_xy']=[942/941,1]
        basis=frame['camera']['camera_transform'];godot=Matrix([basis[:3],basis[3:6],basis[6:9]]).transposed();conversion=Matrix(((1,0,0),(0,0,-1),(0,1,0)));matrix=(conversion@godot).to_4x4();matrix.translation=Vector(c.source_coordinates(basis[9:],frame));front.matrix_world=matrix
        front.data.type='PERSP';front.data.sensor_fit='VERTICAL';front.data.sensor_height=32;front.data.lens=32/(2*math.tan(math.radians(frame['camera']['camera_fov'])/2));front.data.clip_start=frame['camera']['camera_near'];front.data.clip_end=frame['camera']['camera_far']
        side=camera('VIEW58E_shared-side-back',view);side['view_name']='shared-side-back';side['resolution_xy']=[836,586];side['pixel_aspect_xy']=[1,1];side.data.type='ORTHO';side.data.ortho_scale=1600
        if common_matrix is None:
            side.location=target+Vector((1800,1400,650));side.rotation_euler=(target-side.location).to_track_quat('-Z','Y').to_euler();c.camera_resolution(scene,side);bpy.context.view_layer.update()
            points=[world_to_camera_view(scene,side,p) for p in all_positions];span=max(max(p.x for p in points)-min(p.x for p in points),max(p.y for p in points)-min(p.y for p in points));side.data.ortho_scale*=span/.82;bpy.context.view_layer.update()
            points=[world_to_camera_view(scene,side,p) for p in all_positions];cx=(min(p.x for p in points)+max(p.x for p in points))/2;cy=(min(p.y for p in points)+max(p.y for p in points))/2
            right=side.matrix_world.to_quaternion()@Vector((1,0,0));up=side.matrix_world.to_quaternion()@Vector((0,1,0));side.location+=right*((cx-.5)*side.data.ortho_scale)+up*((cy-.5)*side.data.ortho_scale*586/836);bpy.context.view_layer.update();common_matrix=side.matrix_world.copy();common_scale=side.data.ortho_scale;common_location=tuple(side.location);common_rotation=tuple(side.rotation_euler)
        else:side.location=common_location;side.rotation_euler=common_rotation;side.data.ortho_scale=common_scale
        verts=[ob.matrix_world@v.co for ob in collection.objects for v in ob.data.vertices]
        cameras=[c.camera_proof(scene,front,verts,frame,settings),c.camera_proof(scene,side,verts,frame,settings)]
        assert all(row['passed'] for row in cameras),'Keep camera failure; do not render'
        c.camera_resolution(scene,front)
        note=bpy.data.texts.new('58E_LAYOUT_README');note.write(scene['scope']+'\nAll dimensions are design hypotheses. Four individually editable intersecting solids, not a single shell. No union, reference texture, common bottom plate, smoothing or final geometry acceptance.\n')
        source=P/(name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True,check_existing=True)
        results.append(dict(layout=name,source_sha256=c.sha(source),source_bytes=source.stat().st_size,parts=rows,cameras=cameras))
    c.write(args.out/'build-result58e.json',dict(passed=True,pid=os.getpid(),layouts=results,elapsed_seconds=time.monotonic()-start,single_shell=False,rendered=False,visual_acceptance=False))
    print(json.dumps(dict(saved_layouts=2,source_bytes=[r['source_bytes'] for r in results],rendered=False)),flush=True)


if __name__=='__main__':main()
