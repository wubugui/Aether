"""Author one reusable hill-town castle, without rebuilding the world/library.

The Blender source keeps named architectural parts. The GLB is one merged
render mesh; Godot owns its material, collision and each placed instance.
"""
from pathlib import Path
import ast,json,math
import bpy,bmesh,numpy as np
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
library=bpy.data.collections.new('Castle architecture');bpy.context.scene.collection.children.link(library)
material=bpy.data.materials.new('Castle stone and roof pigment');material.use_nodes=True
color=material.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='Palette'
bsdf=material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=1
material.node_tree.links.new(color.outputs['Color'],bsdf.inputs['Base Color'])
parts=[]
# Reuse only the primitive authoring functions. Never execute the legacy
# bootstrap, which would erase the current catalog and replace the airship.
tree=ast.parse((ROOT/'blender/create_assets.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['bl','lin','rgb','finish','box','cone','rod','mesh','roof']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<asset primitives>','exec'),globals())
stone='bfb68f';trim='aaa27e';light_stone='cdc29b';roof_color='b9a780'
def name(obj,label):obj.name=label;return obj
def tower(x,z,height,radius,label):
    name(cone((x,height*.5,z),height,radius,radius*.83,stone,7),label+' stone')
    name(cone((x,height+.45,z),.9,radius*1.08,radius*1.05,light_stone,7),label+' cornice')
    name(cone((x,height+3.2,z),5.6,radius*1.02,.08,roof_color,7),label+' spire')
    for y in [height*.45,height*.77]:
        name(box((x,y,z+radius*.88),(.42,1.6,.10),'827f66'),label+' window')
    name(rod((x,height+5.8,z),(x,height+7.0,z),.10,'8d8060'),label+' finial')

# Thin, unequal towers rise from a cluster of low roofs rather than four
# identical oversized turrets around an empty rectangular courtyard.
for values in [(-20,-9,32,1.65,'West watchtower'),(-12,4,24,1.5,'Gate tower'),(-5,-4,37,2.1,'Keep spire'),(4,-10,43,1.7,'High tower'),(12,2,27,1.7,'East tower'),(22,-2,21,1.4,'Outer turret')]:tower(*values)
name(box((-2,8,-5),(9,16,11),stone),'Main keep')
name(roof(-2,-5,10.5,12,16,22,roof_color),'Keep pitched roof')
name(box((7,5,-5),(8,10,12),light_stone),'East hall')
name(roof(7,-5,9,13,10,15,'b2a37d'),'East hall roof')
for i,(x,z,w,d,h) in enumerate([(-13,-3,6,7,8),(-11,11,5,6,5),(1,10,7,5,6),(12,11,6,6,6),(18,-8,6,7,5),(-20,10,4,6,4),(20,9,5,6,4),(-1,-17,6,5,5),(10,-17,7,5,5)]):
    name(box((x,h*.5,z),(w,h,d),stone),'Courtyard house %02d'%i)
    name(roof(x,z,w+.8,d+.8,h,h+3,['ad9c78','b6aa88','a69d7f'][i%3]),'Courtyard roof %02d'%i)
    name(box((x,h*.38,z+d*.5+.05),(.9,h*.65,.1),'8c866d'),'Courtyard door %02d'%i)
# An irregular low enclosing wall, with a real central gap at the gate.
for x,z,w,d,h in [(-23,0,1.5,30,7),(24,0,1.5,26,6),(0,-19,44,1.5,7),(-14,16,17,1.5,5),(15,15,16,1.5,5)]:
    name(box((x,h*.5,z),(w,h,d),stone),'Curtain wall')
    length=max(w,d)
    for j in range(max(2,int(length/3))):
        q=(j/(max(2,int(length/3))-1)-.5)*(length-1)
        name(box((x+(q if w>d else 0),h+.5,z+(q if d>w else 0)),(1.1,1.0,1.1),trim),'Wall merlon')
for x in [-5,5]:
    name(box((x,4,16),(2.1,8,3),light_stone),'Gate pier')
name(box((0,7.5,16),(8,1.7,3),stone),'Gate lintel')

for p in parts:p.select_set(False)
native=ROOT/'blender/settlement_kit';native.mkdir(exist_ok=True)
bpy.ops.object.camera_add(location=(80,-95,70));camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,14))-camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.camera=camera
bpy.ops.object.light_add(type='SUN',location=(-80,-80,100));bpy.context.object.rotation_euler=(.4,-.4,-.5);bpy.context.object.data.energy=2
bpy.context.scene.world.color=(.3,.35,.4)
bpy.ops.wm.save_as_mainfile(filepath=str(native/'castle.blend'))
bpy.ops.object.select_all(action='DESELECT')
for p in parts:p.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
obj=bpy.context.object;obj.name='castle';obj.data.name='CastleGeometry';obj.asset_mark()
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/models/castle.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
item={'name':'castle','path':'assets/models/castle.glb','native_source':'blender/settlement_kit/castle.blend','vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'parts_in_source':len(parts)}
(ROOT/'assets/settlement_kit.json').write_text(json.dumps([item],indent=2))
print('CASTLE KIT',json.dumps(item),flush=True)
