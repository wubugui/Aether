"""Read-only source preview: no save_mainfile, CPU Cycles, asset QA only."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
base=Path('/workspace/scratch/a29d03198654/Aether/candidates/round40-exclusive-20260930')
source=base/'source-assets/hub-upper43/upper_cloud43.blend'
out=base/'evidence/upper43-cpu-native-preview';out.mkdir(exist_ok=True)
sha=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16
s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('QA_world');s.render.image_settings.file_format='PNG';s.world.color=(.55,.62,.72)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.64,.74,.9,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
s.view_settings.view_transform='Standard'
light=bpy.data.lights.new('QA_sun','SUN');light.energy=2;obj=bpy.data.objects.new('QA_sun',light);s.collection.objects.link(obj);obj.rotation_euler=(.3,-.5,-.35)
camdata=bpy.data.cameras.new('QA_camera');cam=bpy.data.objects.new('QA_camera',camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=930;camdata.clip_end=10000
views={'front':(0,-1600,260),'side':(1600,0,200),'underside':(0,-900,-1100)}
report={'source_sha256_before':sha,'engine':'Blender 4.5.14 Cycles CPU','scope':'Asset-only native source inspection; not Godot GPU acceptance','images':[]}
for variant in range(3):
 for o in s.objects:
  if o.type=='MESH':o.hide_render=not o.name.startswith(f'upper_cloud43_{variant}_')
 for name,xyz in views.items():
  cam.location=xyz;cam.rotation_euler=(Vector((0,0,40))-cam.location).to_track_quat('-Z','Y').to_euler()
  path=out/f'variant{variant}-{name}.png';s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
  report['images'].append(str(path))
report['source_sha256_after']=hashlib.sha256(source.read_bytes()).hexdigest();assert report['source_sha256_after']==sha
(out/'report.json').write_text(json.dumps(report,indent=2))
