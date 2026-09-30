"""Refine standalone cloud volumes and the airship's cloth palette in Blender.
Run on Assets.blend; scene layout is deliberately left to Godot.
"""
from pathlib import Path
import bpy,math,numpy as np
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def linear(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
sun=Vector((-.48,-.30,.82)).normalized()
o=bpy.data.objects['Envelope'];colors=o.data.color_attributes['Palette']
for face in o.data.polygons:
    light=max(0,face.normal.dot(sun))
    c=linear(rgb('a18e70')*(1-light)+rgb('d9c9bc')*light)
    for k in face.loop_indices:colors.data[k].color=(*c,1)
group=bpy.data.collections['Airship'];root=bpy.data.objects['Airship']
old=root.matrix_world.copy();root.matrix_world=Matrix.Identity(4)
bpy.ops.object.select_all(action='DESELECT')
for obj in group.objects:obj.hide_set(False);obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/airship.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
root.matrix_world=old
for name,floor,scale in [('cloud_primary',-22,.90),('cloud_middle',-21,.96),('cloud_low',-15,.98),('cloud_edge',-20,.60)]:
    obj=bpy.data.objects[name]
    if not obj.get('round_05_volume_refined',False):
        for vertex in obj.data.vertices:
            h=vertex.co.z
            if h<floor:vertex.co.z=floor+(h-floor)*.15
            elif h>10:vertex.co.z=10+(h-10)*scale
        obj.data.update();obj['round_05_volume_refined']=True
    pos=obj.location.copy();obj.location=(0,0,0)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/models'/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    obj.location=pos
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Assets.blend'))
print('UPDATED AIRSHIP CLOTH AND FOUR COMPLETE CLOUD ASSETS',flush=True)
