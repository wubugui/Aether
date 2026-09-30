import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'hub-cloud41/cloud_sea41.blend'))
report={}
for col in bpy.data.collections:
 if col.name.startswith('cloud_bank_41'):
  vv=[o.matrix_world@v.co for o in col.objects if o.type=='MESH' for v in o.data.vertices]
  report[col.name]={'parts':len(col.objects),'bounds':[[min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)]],'parts_detail':[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'dimensions':list(o.dimensions)} for o in col.objects]}
for o in bpy.data.objects:o.hide_render=not o.name.startswith('cloud_bank_41_0')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=768;s.render.resolution_y=512;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Inspection44');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.37,.53,.7,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN',location=(0,0,1500));bpy.context.object.rotation_euler=(.4,-.6,-.4);bpy.context.object.data.energy=2.5;bpy.context.object.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=3400;cam.data.clip_end=50000
for name,pos in [('front',(0,-5000,700)),('back',(2500,4500,800)),('underside',(1800,-2500,-2400))]:
 cam.location=pos;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/f'original41-{name}.png');bpy.ops.render.render(write_still=True)
(P/'original41-inspection.json').write_text(json.dumps(report,indent=2))
