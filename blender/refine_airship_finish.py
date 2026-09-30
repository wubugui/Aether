"""Refine the complete hero asset, keeping its independent Godot placement."""
from pathlib import Path
import math,bpy,numpy as np
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def linear(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def srgb(c):return np.where(c<=.0031308,c*12.92,1.055*np.maximum(c,0)**(1/2.4)-.055)
group=bpy.data.collections['Airship'];root=bpy.data.objects['Airship']
sun=Vector((-.48,-.30,.82)).normalized()
envelope=bpy.data.objects['Envelope'];colors=envelope.data.color_attributes['Palette']
for face in envelope.data.polygons:
    light=max(0,face.normal.dot(sun))
    pigment=rgb('a18e70')*(1-light)+rgb('d9c9bc')*light
    bounce=math.sin(math.pi*light)
    pigment+=np.array([4*bounce-11*light**5,10*bounce-5*light**4,13*bounce])/255
    for k in face.loop_indices:colors.data[k].color=(*linear(pigment),1)
for obj in group.objects:
    if obj.type!='MESH' or obj.get('round_07_hull_finish',False):continue
    if obj.name.startswith('Hull plank') or obj.name in ['Gondola','Closed wooden keel']:
        # A raised prow and continuous curved plank courses on both sides.
        for vertex in obj.data.vertices:
            if vertex.co.z< -1.1 and vertex.co.x< -1.8:
                t=np.clip((-vertex.co.x-1.8)/2.2,0,1)
                vertex.co.z+=.8*t;vertex.co.x+=.18*t
        obj.data.update()
        colors=obj.data.color_attributes.get('Palette')
        if colors:
            for face in obj.data.polygons:
                tint=np.array([.79,.79,.82])
                if obj.name=='Gondola' and face.center.z> -1.55:tint=np.array([.68,.63,.67])
                for k in face.loop_indices:
                    c=srgb(np.array(colors.data[k].color[:3]))*tint
                    colors.data[k].color=(*linear(c),1)
        obj['round_07_hull_finish']=True
    elif obj.name.startswith(('Cabin upright','Cabin lintel','Window crossbar')):
        colors=obj.data.color_attributes.get('Palette')
        if colors:
            for c in colors.data:c.color=(*linear(srgb(np.array(c.color[:3]))*.76),1)
        obj['round_07_hull_finish']=True
    elif obj.name.startswith('Rope swag'):
        colors=obj.data.color_attributes.get('Palette')
        if colors:
            for c in colors.data:c.color=(*linear(srgb(np.array(c.color[:3]))*.72),1)
        obj['round_07_hull_finish']=True
old=root.matrix_world.copy();root.matrix_world=Matrix.Identity(4)
bpy.ops.object.select_all(action='DESELECT')
for obj in group.objects:obj.hide_set(False);obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/airship.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
root.matrix_world=old
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Assets.blend'))
print('UPDATED HERO: ivory cloth response, raised wooden prow, darker planks and cabin framing',flush=True)
