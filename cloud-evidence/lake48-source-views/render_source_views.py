import bpy,json,math,os
from mathutils import Vector
R='/workspace/scratch/a29d03198654/Aether';D=R+'/source-assets/lake48';OUT=R+'/cloud-evidence/lake48-source-views'
bpy.ops.wm.read_factory_settings(use_empty=True)
base=json.load(open(D+'/base47.json'))
for name,r in base['meshes'].items():
 with bpy.data.libraries.load(D+'/'+name+'_lake48.blend',link=False) as (src,dst):dst.objects=src.objects
 for o in dst.objects:
  if o and o.type=='MESH':
   bpy.context.collection.objects.link(o);o.location+=Vector((r['origin'][0],-r['origin'][2],r['origin'][1]))
   mat=bpy.data.materials.new(name+'_diagnostic');mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92
   color=o.data.color_attributes.active_color
   if color:
    a=nodes.new('ShaderNodeVertexColor');a.layer_name=color.name;mat.node_tree.links.new(a.outputs['Color'],bs.inputs['Base Color'])
   else:bs.inputs['Base Color'].default_value=(.39,.43,.33,1)
   o.data.materials.clear();o.data.materials.append(mat)
# Exact Y0 coastline intersections as cyan curves, no inferred shoreline painting.
payload=json.load(open(D+'/lake48-payload.json'));cur=bpy.data.curves.new('actual_y0_intersection','CURVE');cur.dimensions='3D';cur.bevel_depth=1.0;cur.bevel_resolution=0
for m in payload['meshes']:
 v=m['vertices']
 for i in range(0,len(v),3):
  t=v[i:i+3];pts=[]
  for j in range(3):
   a,b=t[j],t[(j+1)%3]
   if a[1]*b[1]<0:
    f=-a[1]/(b[1]-a[1]);pts.append(Vector((a[0]+f*(b[0]-a[0]),-(a[2]+f*(b[2]-a[2])),.35)))
  if len(pts)==2:
   sp=cur.splines.new('POLY');sp.points.add(1)
   for p,co in zip(sp.points,pts):p.co=(*co,1)
o=bpy.data.objects.new('Actual Y0 shoreline',cur);bpy.context.collection.objects.link(o)
mat=bpy.data.materials.new('shore contour');mat.diffuse_color=(.07,.65,.75,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.03,.6,.8,1);bs.inputs['Emission Color'].default_value=(.03,.3,.6,1);bs.inputs['Emission Strength'].default_value=.5;cur.materials.append(mat)
# Inset transparent reference water level shows actual bathymetry beneath.
bpy.ops.mesh.primitive_plane_add(size=2,location=(1152,1536,0));o=bpy.context.object;o.name='Diagnostic Ocean Y0';o.scale=(384,768,1)
mat=bpy.data.materials.new('Transparent diagnostic level');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.18;tr=n.new('ShaderNodeBsdfTransparent');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(.08,.4,.55,1);bs.inputs['Roughness'].default_value=.7;mat.node_tree.links.new(tr.outputs[0],mix.inputs[1]);mat.node_tree.links.new(bs.outputs[0],mix.inputs[2]);mat.node_tree.links.new(mix.outputs[0],out.inputs['Surface']);o.data.materials.append(mat)
bpy.ops.object.light_add(type='SUN',location=(1000,1200,1000));sun=bpy.context.object;sun.rotation_euler=(math.radians(25),math.radians(-25),math.radians(-35));sun.data.energy=2.3;sun.data.angle=.1
world=bpy.data.worlds.new('neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.42,.52,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;bpy.context.scene.world=world
bpy.ops.object.camera_add();camera=bpy.context.object;bpy.context.scene.camera=camera
camera.data.clip_end=10000;camera.data.clip_start=.1
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
views=[('top',(1152,1550,2200),(1152,1550,0),'ORTHO',1810,900,1100),('front',(1150,600,450),(1150,1680,0),'PERSP',55,1100,700),('east-side',(2150,1700,400),(1100,1700,0),'ORTHO',1750,1100,700)]
for name,loc,target,typ,scale,w,h in views:
 camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type=typ
 if typ=='ORTHO':camera.data.ortho_scale=scale
 else:camera.data.lens=scale
 scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=OUT+'/'+name+'.png';bpy.ops.render.render(write_still=True)
print('SOURCE_VIEWS_DONE')
