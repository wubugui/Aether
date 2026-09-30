"""Cloud bank44: editable closed low-poly lobes, fixed world-neutral pivot.
No camera-derived geometry. New outputs only. Blender 4.5 LTS, CPU Cycles QA.
"""
import bpy,bmesh,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
ASSETS=P.parent.parent/'project/assets/clouds44';ASSETS.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mat=bpy.data.materials.new('Cloud44 chalk-white diffuse');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=.12
vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='CloudTone';mat.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
report={'version':44,'construction':'Three asymmetric archipelago groups per bank, closed crown/shoulder/belly/taper lobes; no common base slab. Fixed origin and axes compatible with banks41; placements unchanged. Colors are restrained near-white diffuse, no emissive or camera inputs.','render_note':'CPU Cycles isolated asset previews only; no Godot GPU visual acceptance.','assets':[]}
def lobe(col,name,center,radii,seed,detail=2):
 rng=random.Random(seed);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=detail,radius=1)
 for v in bm.verts:
  p=v.co.copy();a=math.atan2(p.y,p.x);wig=1+.065*math.sin(3*a+seed)+.035*math.sin(5*a+2*p.z+seed*.17)
  # Unequal crown and convex, gently scalloped underside. Never planar-clamp z.
  z=p.z*(1+.055*math.sin(a*3+seed))
  if z<0:z*=.72+.10*math.sin(a+seed)
  v.co=Vector((p.x*radii[0]*wig + .13*p.z*radii[0],p.y*radii[1]*wig,z*radii[2]))+Vector(center)
 mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free();mesh.update()
 cols=mesh.color_attributes.new(name='CloudTone',type='FLOAT_COLOR',domain='CORNER')
 for f in mesh.polygons:
  tone=rng.uniform(-.012,.012)
  for li in f.loop_indices:cols.data[li].color=(.82+tone,.835+tone,.855+tone,1)
  f.use_smooth=False
 mesh.materials.append(mat);o=bpy.data.objects.new(name,mesh);col.objects.link(o);o['part_role']=name.split('_')[-2]
 return o
for var in range(3):
 col=bpy.data.collections.new(f'cloud_bank_44_{var}');bpy.context.scene.collection.children.link(col)
 rng=random.Random(4400+var*133);seed=4400+var*100
 # Skeleton is staggered in 3-D and bent, rather than a two-row carpet.
 groups=[(-435,-110,1.0),(30,150,.83),(530,-65,.51)]
 if var==1:groups=[(-440,90,.73),(-15,-100,1.05),(495,220,.55)]
 if var==2:groups=[(-475,-20,.61),(10,90,.98),(505,-180,.69)]
 for g,(cx,cy,scale) in enumerate(groups):
  defs=[('crown',(0,0,140),(220,180,235),3),('shoulderL',(-155,-28,43),(195,130,128),2),('shoulderR',(170,15,29),(167,142,115),2),('back',(-12,138,42),(145,142,124),2),('belly',(-38,-40,-18),(157,131,119),2),('taperL',(-295,-57,-2),(140,75,42),2),('taperR',(287,40,1),(122,80,48),2)]
  for i,(role,cen,rad,detail) in enumerate(defs):
   c=Vector((cx+cen[0]*scale,cy+cen[1]*scale,cen[2]*scale+rng.uniform(-12,12)))
   rr=[x*scale for x in rad]
   lobe(col,f'bank44_{var}_group{g}_{role}_{i}',c,rr,seed+g*17+i,detail)
 bpy.ops.object.select_all(action='DESELECT')
 for o in col.objects:o.select_set(True)
 name=col.name
 bpy.ops.export_scene.gltf(filepath=str(P/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
 (ASSETS/(name+'.glb')).write_bytes((P/(name+'.glb')).read_bytes())
 vv=[v.co for o in col.objects for v in o.data.vertices]
 bounds=[[min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)]]
 nonmanifold=0
 for o in col.objects:
  bm=bmesh.new();bm.from_mesh(o.data);nonmanifold+=sum(not e.is_manifold for e in bm.edges);bm.free()
 report['assets'].append({'name':name,'parts':len(col.objects),'triangles':sum(len(o.data.polygons) for o in col.objects),'bounds':bounds,'nonmanifold_edges':nonmanifold,'glb_sha256':hashlib.sha256((P/(name+'.glb')).read_bytes()).hexdigest()})
# Save modeling scene with all editable groups and no baked runtime layout.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank44.blend'))
# Dedicated CPU preview rig. Saved separately to retain reproducible review.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=768;s.render.resolution_y=512;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Cloud44 preview sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.37,.53,.7,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN',location=(0,0,1500));bpy.context.object.rotation_euler=(.4,-.6,-.4);bpy.context.object.data.energy=2.5;bpy.context.object.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2050;cam.data.clip_end=50000
for var in range(3):
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=not o.name.startswith(f'bank44_{var}_')
 for name,pos in [('front',(0,-5000,700)),('back',(2500,4500,800)),('underside',(1800,-2500,-2400))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,90))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/f'bank44-{var}-{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank44_preview.blend'))
(P/'cloud_bank44-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
