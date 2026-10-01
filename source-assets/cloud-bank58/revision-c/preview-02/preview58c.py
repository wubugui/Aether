"""Five physicallylit actualnative Cviews, scheduled sourceonly; neversave."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;C=P.parent;A=C.parent;ROOT=C.parents[2];R=C/'recovery-02';sys.path.insert(0,str(R));from geometry58c import source_coordinate,world_coordinate
parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(parents=True,exist_ok=True)
source=R/'cloud_bank58c_union.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();proof=json.loads((R/'union-fresh-readback58c.json').read_text());assert proof['passed'] and proof['source_sha256']==before
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;bank=bpy.data.objects['CloudBank58C_four_root_density_and_folds']
for ob in scene.objects:ob.hide_render=ob!=bank
bpy.data.collections['EDIT58C_57_native_3d_controls'].hide_render=True;bank.hide_render=False
# Load the same oldnative material and worldheight colour law used byA/B previews.
# No IDcolour, reference image, custom brightening, skycard or geometryrepair.
material_name='Cloud46 diffuse warm crown cool belly';material_source=ROOT/'source-assets/cloud-sea52f/variants/cloud_sea52f_variants.blend'
with bpy.data.libraries.load(str(material_source),link=False) as (src,dst):dst.materials=[material_name]
material=dst.materials[0];assert material is not None;bank.data.materials.clear();bank.data.materials.append(material)
if 'Col' in bank.data.color_attributes:bank.data.color_attributes.remove(bank.data.color_attributes['Col'])
col=bank.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for face in bank.data.polygons:
 y=sum(world_coordinate(bank.matrix_world@bank.data.vertices[i].co)[1] for i in face.vertices)/len(face.vertices)
 value=.76+.16*max(0,min(1,((y-700)+190)/460));linear=((value+.055)/1.055)**2.4
 for li in face.loop_indices:col.data[li].color=(linear,linear,linear,1)
 face.use_smooth=False
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Same neutral A B source lighting');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.37,.53,.7,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.4,-.6,-.4);sun.data.energy=2.5;sun.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_start=.35;cam.data.clip_end=18000
report=json.loads((ROOT/'cloud-evidence/cloudsea52h-d-ab-front-20261001T102736Z-svczz9fo/images/report.json').read_text())['captures'][0];basis=report['camera_transform'];G=Matrix([basis[0:3],basis[3:6],basis[6:9]]).transposed();S=Matrix(((1,0,0),(0,0,-1),(0,1,0)));M=(S@G).to_4x4();M.translation=Vector(source_coordinate(basis[9:]));cam.matrix_world=M
cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=32;cam.data.lens=32/(2*math.tan(math.radians(report['camera_fov'])/2));scene.render.resolution_x=836;scene.render.resolution_y=471;scene.render.pixel_aspect_x=942/941;scene.render.pixel_aspect_y=1;bpy.context.view_layer.update()
project=cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=836,y=471,scale_x=scene.render.pixel_aspect_x,scale_y=scene.render.pixel_aspect_y)
expected=Matrix(report['camera_projection_columns']).transposed();projection_error=max(abs(project[i][j]-expected[i][j]) for i in range(4) for j in range(4));assert projection_error<2e-6,(project,expected,projection_error)
framing=[dict(view='1216-source-front',actual_saved_camera_transform=basis,blender_source_camera_matrix=[list(r) for r in cam.matrix_world],actual_projection_matrix=[list(r) for r in project],saved_projection_matrix=[list(r) for r in expected],maximum_projection_matrix_error=projection_error,resolution=[836,471],reference_resolution=[1672,941],pixel_aspect_xy=[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],world_loaded=False,ship_present=False,external21roots_present=False,upperclouds_present=False,view_is_cropped_by_original_camera=True,source_visual_acceptance=False)]
(args.out.parent/'runtime-render-settings.json').write_text(json.dumps(dict(engine=scene.render.engine,device=scene.cycles.device,samples=scene.cycles.samples,use_denoising=scene.cycles.use_denoising,denoiser=getattr(scene.cycles,'denoiser',None),denoising_use_gpu=getattr(scene.cycles,'denoising_use_gpu',None),threads=scene.render.threads,resolution=[scene.render.resolution_x,scene.render.resolution_y],pixel_aspect=[scene.render.pixel_aspect_x,scene.render.pixel_aspect_y],memory_cause_unproven=True),indent=2)+'\n')
(args.out.parent/'camera-framing.json').write_text(json.dumps(framing,indent=2)+'\n');scene.render.filepath=str(args.out/'cloudbank58c-1216-source-front.png');bpy.ops.render.render(write_still=True)
vertices=[bank.matrix_world@v.co for v in bank.data.vertices];low=Vector([min(v[k] for v in vertices) for k in range(3)]);high=Vector([max(v[k] for v in vertices) for k in range(3)]);target=(low+high)*.5
scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.pixel_aspect_x=1;scene.render.pixel_aspect_y=1
for name,offset in [('back',(2000,6500,1500)),('side',(6500,200,1100)),('underside',(2300,-2700,-5200)),('top',(0,-1300,6500))]:
 cam.data.type='ORTHO';cam.data.ortho_scale=6500;cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();points=[world_to_camera_view(scene,cam,p) for p in vertices]
 span=max(max(p.x for p in points)-min(p.x for p in points),max(p.y for p in points)-min(p.y for p in points));cam.data.ortho_scale*=span/.82;bpy.context.view_layer.update();points=[world_to_camera_view(scene,cam,p) for p in vertices];cx=(min(p.x for p in points)+max(p.x for p in points))*.5;cy=(min(p.y for p in points)+max(p.y for p in points))*.5
 right=cam.matrix_world.to_quaternion()@Vector((1,0,0));up=cam.matrix_world.to_quaternion()@Vector((0,1,0));cam.location+=right*((cx-.5)*cam.data.ortho_scale)+up*((cy-.5)*cam.data.ortho_scale*700/1000);bpy.context.view_layer.update();points=[world_to_camera_view(scene,cam,p) for p in vertices];bounds=[[min(p[k] for p in points) for k in range(2)],[max(p[k] for p in points) for k in range(2)]];margin=min(bounds[0]+[1-x for x in bounds[1]]);assert margin>.05
 framing.append(dict(view=name,projection='orthographic',bounds=bounds,minimum_margin=margin,all_actual_union_vertices_inside=True,resolution=[1000,700],world_loaded=False,visual_acceptance=False));(args.out.parent/'camera-framing.json').write_text(json.dumps(framing,indent=2)+'\n');scene.render.filepath=str(args.out/f'cloudbank58c-{name}.png');bpy.ops.render.render(write_still=True)
assert before==hashlib.sha256(source.read_bytes()).hexdigest();(args.out.parent/'preview-proof.json').write_text(json.dumps(dict(passed=True,source_sha256=before,source_unchanged=True,views=5,material_source=str(material_source.relative_to(ROOT)),material_source_sha256=hashlib.sha256(material_source.read_bytes()).hexdigest(),lighting='SameA/Bneutralworld0.7 andsun2.5;noaddedlightsormaterialbrightening',all_faces_flat_shaded=True,raw_union_triangles=52864,source_saved=False,world_loaded=False,hardware_gpu_acceptance=False,visual_acceptance=False),indent=2)+'\n')
print('Five actualCsourceimages complete; no source save or world',flush=True)
