import bpy,bmesh,math,json,shutil,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
A=P.parent.parent/'project/assets/clouds46'; A.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mat=bpy.data.materials.new('Cloud46 diffuse warm crown cool belly');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Col';mat.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=1
# Unequal, directionally stretched lobes; no common flat underbody or coplanar skirt.
layouts=[
[(-240,130,30,390,330,245),(170,100,60,350,290,285),(-70,-230,-5,355,260,180),(-480,-170,-40,245,265,120),(420,270,-25,240,250,140),(340,-300,-30,255,195,115),(-160,450,-40,240,205,135),(-560,250,-65,170,145,85),(570,-10,-45,185,135,90),(40,-500,-45,250,135,90),(-400,-480,-60,190,140,80),(360,520,-65,195,115,75),(620,370,-40,105,85,60)],
[(-310,-30,55,370,295,270),(10,190,45,330,300,210),(325,60,-5,325,250,180),(-60,-290,-20,320,245,165),(-410,330,-30,255,215,140),(370,-290,-50,250,200,105),(-500,-310,-55,230,190,105),(100,480,-40,290,190,100),(545,350,-40,170,175,95),(-640,130,-60,130,170,65),(-210,-520,-55,195,135,80),(525,-480,-40,125,90,60)],
[(-100,-80,85,400,310,280),(310,165,-5,325,280,185),(-390,210,-15,330,240,175),(-290,-350,-25,275,230,155),(225,-350,-45,300,220,125),(15,440,-25,305,240,145),(555,-90,-40,210,225,100),(-610,-145,-50,185,230,105),(-420,485,-60,215,115,75),(390,490,-60,205,145,90),(70,-550,-50,210,140,70),(635,270,-40,110,140,70)]]
report={'scope':'CloudSea mesh only; original 25 world anchors and scenes untouched','hardware_gpu_acceptance':False,'visual_acceptance':False,'variants':[]}
for vi,rows in enumerate(layouts):
 col=bpy.data.collections.new(f'cloud_sea_46_{vi}');bpy.context.scene.collection.children.link(col)
 controls=bpy.data.collections.new(f'Editable46_{vi}_lobe_controls');bpy.context.scene.collection.children.link(controls)
 obs=[]
 for j,(x,y,z,rx,ry,rz) in enumerate(rows):
  bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1)
  for v in bm.verts:
   a=math.atan2(v.co.y,v.co.x);t=v.co.z
   radial=1+.065*math.sin(3*a+vi+j*.7)+.035*math.sin(5*a+t*2+j)
   # modest coherent curvature, no independent random rocky vertex displacements
   belly=1-.32*max(0,-t)
   depth=1 if t>=0 else (.55+.35*((j+vi)%3)/2)
   v.co=Vector((x+v.co.x*rx*radial*belly+30*t*t*math.sin(j),y+v.co.y*ry*radial*belly,z+t*rz*depth*(1+.08*math.sin(a*2+j))))
  me=bpy.data.meshes.new(f'Lobe46_{vi}_{j}');bm.to_mesh(me);bm.free()
  ob=bpy.data.objects.new(me.name,me);col.objects.link(ob);obs.append(ob)
  cp=ob.copy();cp.data=me.copy();cp.name=f'CONTROL46_{vi}_{j}';controls.objects.link(cp);cp.hide_render=True;cp.hide_set(True)
 controls.hide_render=True;controls.hide_viewport=True
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=f'cloud_sea_46_{vi}_continuous_crown'
 mod=ob.modifiers.new('Union lobes into continuous volume','REMESH');mod.mode='VOXEL';mod.voxel_size=20;mod.use_smooth_shade=False;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=ob.modifiers.new('Soft crown transitions','SMOOTH');mod.factor=1.3;mod.iterations=4;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=ob.modifiers.new('Restrained broad facets','DECIMATE');mod.ratio=.19;bpy.ops.object.modifier_apply(modifier=mod.name)
 me=ob.data;me.materials.append(mat)
 ca=me.color_attributes.new('Col','FLOAT_COLOR','CORNER')
 for f in me.polygons:
  f.use_smooth=False
  z=sum(me.vertices[k].co.z for k in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
  for li in f.loop_indices:ca.data[li].color=(linear,linear,linear,1)
 bm=bmesh.new();bm.from_mesh(me);bounds=[[min(v.co[k] for v in me.vertices) for k in range(3)],[max(v.co[k] for v in me.vertices) for k in range(3)]]
 record={'name':col.name,'bounds_blender_xyz':bounds,'triangles':sum(len(f.vertices)-2 for f in me.polygons),'vertices':len(me.vertices),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'editable_lobe_controls':len(rows)};bm.free();report['variants'].append(record)
 bpy.ops.export_scene.gltf(filepath=str(P/(col.name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
 shutil.copy2(P/(col.name+'.glb'),A/(col.name+'.glb'))
 ob.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea46.blend'))
(P/'model-report46.json').write_text(json.dumps(report,indent=2))
# CPU-only isolated turntable; no scene/world acceptance claim
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=640;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Preview46 sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.37,.53,.7,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.4,-.6,-.4);bpy.context.object.data.energy=2.5;bpy.context.object.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1950;cam.data.clip_end=50000
for vi in range(3):
 for ob in bpy.data.objects:
  if ob.type=='MESH':ob.hide_render=ob.name!=f'cloud_sea_46_{vi}_continuous_crown'
 for name,pos in [('front',(0,-5000,700)),('back',(2500,4500,800)),('side',(4800,0,600)),('underside',(1800,-2500,-2400)),('top',(0,-1500,4200))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/f'sea46-{vi}-{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea46_preview.blend'))
print('SEA46 COMPLETE',json.dumps(report))
