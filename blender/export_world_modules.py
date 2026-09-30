"""Export independent terrain/land-detail modules from a native assembly.

Called directly during authoring. --migrate-once imports the previous packed
GLB only to split its existing meshes without changing any geometry/colors.
Godot assembles the exported modules; it never loads the former world GLB.
"""
from pathlib import Path
import bpy,json,sys,numpy as np
ROOT=Path(__file__).resolve().parents[1]

def export_modules(objects):
    result={}
    for index,o in enumerate(objects):
        folder='terrain' if o.name.startswith('Ground_') else 'land_details'
        target=ROOT/'assets'/folder;target.mkdir(exist_ok=True)
        position=o.location.copy()
        o.location=(0,0,0)
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(target/(o.name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
        o.location=position
        result[o.name]={'path':f'assets/{folder}/{o.name}.glb','position':[float(position.x),float(position.z),float(-position.y)]}
        if index%32==0:print('EXPORTED MODULE',index,'/',len(objects),flush=True)
    (ROOT/'assets/world_modules.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/open_world.glb'))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    export_modules(objects)
    print('INDEPENDENT WORLD MODULES',len(objects),flush=True)
