"""Drape independent road/field models onto the actual triangulated terrain.

Uses the current saved Godot instance transforms, and returns local model
geometry without changing those engine placements.
"""
from pathlib import Path
import sys,json,bpy,bmesh,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'blender'))
import terrain_topology as T
import world_definition as W
sampler=T.SurfaceSampler();native=ROOT/'blender/land_details';native.mkdir(exist_ok=True)
for item in json.loads((ROOT/'assets/land_detail_authoring.json').read_text()):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/item['asset']))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    basis=np.asarray(item['basis']);origin=np.asarray(item['origin']);inverse=np.linalg.inv(basis)
    for obj in objects:
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        points=np.asarray([v.co[:] for v in obj.data.vertices])[:,[0,2,1]];points[:,2]*=-1
        world=points@basis.T+origin
        for cx,cz in np.unique(np.floor(world[:,[0,2]]/768).astype(int),axis=0):
            if (cx,cz) not in sampler.tiles:
                vertices,faces=T.chunk_mesh(cx,cz);sampler.add(cx,cz,vertices,faces)
        world[:,1]=sampler.height(world[:,0],world[:,2])+.14
        points=(world-origin)@inverse.T
        local=points[:,[0,2,1]];local[:,1]*=-1
        for v,p in zip(obj.data.vertices,local):v.co=p
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        obj.data.update();obj.asset_mark();obj['role']='Individually editable road or field; follows native Godot placement'
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(ROOT/item['asset']),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    bpy.ops.wm.save_as_mainfile(filepath=str(native/(item['name']+'.blend')))
    print('DRAPED INDEPENDENT LAND DETAIL',item['name'],flush=True)
print('Exact triangle sampler misses:',sampler.misses)
