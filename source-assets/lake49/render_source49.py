import bpy,math,os,json
from mathutils import Vector
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake49';os.makedirs(D+'/source-views',exist_ok=True)
specs=json.load(open(D+'/lake49-payload.json'))['islands']
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for spec in specs:
 if os.environ.get('ONLY_ASSET') and spec['name']!=os.environ['ONLY_ASSET']:continue
 name=spec['name'];bpy.ops.wm.open_mainfile(filepath=D+'/'+name+'.blend');sc=bpy.context.scene
 sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_x=800;sc.render.resolution_y=600;sc.render.resolution_percentage=100
 sc.world=bpy.data.worlds.new('Evidence_World');sc.world.color=(.5,.5,.5);sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.72,.82,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.7
 sc.view_settings.view_transform='Standard';sc.view_settings.exposure=0;sc.view_settings.gamma=1
 light=bpy.data.lights.new('Evidence_Sun','SUN');light.energy=2.2;light.angle=math.radians(16);o=bpy.data.objects.new('Evidence_Sun',light);sc.collection.objects.link(o);o.rotation_euler=(.5,-.6,-.7)
 camd=bpy.data.cameras.new('Evidence_Camera');cam=bpy.data.objects.new('Evidence_Camera',camd);sc.collection.objects.link(cam);sc.camera=cam;camd.type='ORTHO';w,d=spec['size'];radius=max(w,d)*.75;camd.ortho_scale=max(w*1.25,45)
 mat=bpy.data.materials.new('Evidence_Water');mat.diffuse_color=(.36,.52,.66,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.36,.52,.66,1);bs.inputs['Roughness'].default_value=.34
 bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.02));plane=bpy.context.object;plane.name='Evidence_Water_guide_only';plane.data.materials.append(mat)
 for view,loc,target in [('front',(0,-radius,max(10,radius*.20)),(0,0,4)),('side',(radius,0,radius*.30),(0,0,3)),('top',(0,0,radius),(0,0,0)),('anatomy',(radius*.8,-radius,15),(0,0,-7))]:
  plane.hide_render=view=='anatomy';direction=(Vector(loc)-Vector(target)).normalized();cam.location=Vector(target)+direction*600;aim(cam,target);camd.ortho_scale=max(w*1.25,45) if view!='anatomy' else max(w*1.25,64)
  sc.render.filepath=D+'/source-views/'+name+'-'+view+'.png';bpy.ops.render.render(write_still=True);print('RENDERED',name,view,flush=True)
