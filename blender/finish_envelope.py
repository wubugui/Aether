"""Set the authored ivory envelope palette without changing its geometry."""
from pathlib import Path
import bpy,numpy as np,math
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def linear(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
envelope=bpy.data.objects['Envelope'];sun=Vector((-.48,-.30,.82)).normalized()
colors=envelope.data.color_attributes['Palette']
for face in envelope.data.polygons:
    light=max(0,face.normal.dot(sun))
    pigment=rgb('b4a48c')*(1-light)+rgb('d0c2b1')*light
    bounce=math.sin(math.pi*light)
    pigment+=np.array([4*bounce-11*light**5,10*bounce-5*light**4,13*bounce])/255
    for k in face.loop_indices:colors.data[k].color=(*linear(pigment),1)
root=bpy.data.objects['Airship'];old=root.matrix_world.copy();root.matrix_world=Matrix.Identity(4)
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.collections['Airship'].objects:obj.hide_set(False);obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/airship.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
root.matrix_world=old
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Assets.blend'))
print('IVORY ENVELOPE PALETTE; actual envelope and compound collider geometry unchanged',flush=True)
