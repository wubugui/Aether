"""Render only the standalone native source; preview sea/light/camera are never saved.
These are CPU source previews, not Godot world captures or acceptance images.
"""
import bpy,math,sys
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent;(D/'previews').mkdir(exist_ok=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
scene.world.color=(.65,.7,.8);scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.63,.71,.83,1);bg.inputs['Strength'].default_value=.6
scene.view_settings.view_transform='AgX'
# Opaque diagnostic sea establishes actual Y=0 crossing of the source mesh.
bpy.ops.mesh.primitive_plane_add(size=4000,location=(384,-384,0));water=bpy.context.object;water.name='PREVIEW_ONLY_sea_level_0'
mat=bpy.data.materials.new('PREVIEW_ONLY blue water');mat.diffuse_color=(.025,.18,.3,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.025,.18,.3,1);bs.inputs['Roughness'].default_value=.6;water.data.materials.append(mat)
light=bpy.data.lights.new('PREVIEW_ONLY Sun','SUN');light.energy=2.;light.angle=.14;sun=bpy.data.objects.new('PREVIEW_ONLY Sun',light);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(27),math.radians(-25),math.radians(-35))
cam=bpy.data.cameras.new('PREVIEW_ONLY camera');ob=bpy.data.objects.new('PREVIEW_ONLY camera',cam);scene.collection.objects.link(ob);scene.camera=ob;cam.type='ORTHO';cam.clip_end=6000
views=[('sea_south',(260,-590,300),(550,-230,22),560),('sea_north',(180,100,305),(530,-235,24),560),('overhead',(550,-230,850),(550,-230,0),570),('land_back',(950,-200,330),(550,-230,18),570),('low_shore',(200,-400,105),(570,-250,8),500)]
auth=bpy.data.objects['Ground_-5_-5_AUTHORITY'];cand=bpy.data.objects['Ground_-5_-5_COAST57']
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for name,pos,target,scale in views:
 if selected and name not in selected:continue
 cam.type='PERSP' if name=='low_shore' else 'ORTHO';cam.lens=45
 ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale
 auth.hide_render=True;cand.hide_render=False;scene.render.filepath=str(D/'previews'/('candidate_'+name+'.png'));bpy.ops.render.render(write_still=True)
 if name in ['sea_south','overhead','low_shore']:
  auth.hide_render=False;cand.hide_render=True;scene.render.filepath=str(D/'previews'/('original_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('COAST57_SOURCE_PREVIEWS_COMPLETE; standalone tile only; no scene save')
