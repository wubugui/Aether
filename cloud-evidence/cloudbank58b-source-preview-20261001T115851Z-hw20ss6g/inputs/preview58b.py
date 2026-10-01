"""Explicitly scheduled SOURCE previews; no world or source save is possible."""
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;A=P.parent;sys.path.insert(0,str(A))
from build58 import source_coordinate

parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=P);parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--reference-camera',action='store_true',help='Optional sixth source-only perspective requires separate scheduling')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(args.source/'cloud_bank58b.blend'))
proof=json.loads((args.source/'geometry-context58b.json').read_text())
assert proof['native_source_geometry_passed'],'Source structure must pass before preview'
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('58 source same neutral Cloud46 light');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.37,.53,.7,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');light=bpy.context.object;light.rotation_euler=(.4,-.6,-.4);light.data.energy=2.5;light.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_end=50000
objects=[o for o in bpy.data.collections['CloudBank58B_local_four_root_field'].objects if o.type=='MESH']
bpy.data.collections['EDIT58B_closed_3d_fold_volumes'].hide_render=True
vertices=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
low=Vector([min(v[k] for v in vertices) for k in range(3)]);high=Vector([max(v[k] for v in vertices) for k in range(3)]);target=(low+high)*.5
framing=[];args.out.mkdir(parents=True,exist_ok=True)
views=[('front',(0,-6500,1100)),('back',(2000,6500,1500)),('side',(6500,200,1100)),('underside',(2300,-2700,-5200)),('top',(0,-1300,6500))]
for name,offset in views:
    cam.data.type='ORTHO';cam.data.ortho_scale=6500
    cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    points=[world_to_camera_view(scene,cam,p) for p in vertices]
    span=max(max(p.x for p in points)-min(p.x for p in points),max(p.y for p in points)-min(p.y for p in points))
    cam.data.ortho_scale*=span/.82;bpy.context.view_layer.update()
    points=[world_to_camera_view(scene,cam,p) for p in vertices]
    cx=(min(p.x for p in points)+max(p.x for p in points))*.5
    cy=(min(p.y for p in points)+max(p.y for p in points))*.5
    right=cam.matrix_world.to_quaternion()@Vector((1,0,0));up=cam.matrix_world.to_quaternion()@Vector((0,1,0))
    cam.location+=right*((cx-.5)*cam.data.ortho_scale)+up*((cy-.5)*cam.data.ortho_scale*700/1000)
    bpy.context.view_layer.update();points=[world_to_camera_view(scene,cam,p) for p in vertices]
    bound=[[min(p[k] for p in points) for k in range(2)],[max(p[k] for p in points) for k in range(2)]]
    margin=min(bound[0]+[1-x for x in bound[1]])
    assert margin>.05,f'Insufficient source framing in {name}: {bound}'
    row=dict(view=name,projection='orthographic',bounds=bound,minimum_margin=margin,all_four_sources_visible=True,world_loaded=False)
    framing.append(row);(args.out.parent/'camera-framing.json').write_text(json.dumps(framing,indent=2)+'\n')
    scene.render.filepath=str(args.out/f'cloudbank58b-{name}.png');bpy.ops.render.render(write_still=True)
# Default stops after exactly five full-volume source faces.
if not args.reference_camera:
    print('Five complete source faces rendered; no context/world preview or save')
    raise SystemExit(0)
# Exact research camera, containing only the NEW bounded source assets. It must
# never be mistaken for the reference/world camera image with ship, sea, weather,
# other21 roots and the rest of the original world, which are deliberately absent.
intake=json.loads((A/'native-intake58.json').read_text());basis=intake['camera_transform'];position=basis[9:]
forward=Vector((-basis[6],basis[8],-basis[7]))
cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=32
cam.data.lens=32/(2*math.tan(math.radians(intake['camera_fov'])/2))
cam.location=source_coordinate(position);cam.rotation_euler=forward.to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
framing.append(dict(view='1216-source-only',projection='perspective',camera_world=position,vertical_fov_degrees=intake['camera_fov'],
                    view_is_cropped_by_design=True,world_loaded=False,ship_present=False,old21_roots_present=False,reference_or_world_acceptance=False))
(args.out.parent/'camera-framing.json').write_text(json.dumps(framing,indent=2)+'\n')
scene.render.filepath=str(args.out/'cloudbank58b-1216-source-only.png');bpy.ops.render.render(write_still=True)
# Never save this temporary lighting/camera setup to the editable source.
