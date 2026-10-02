"""Explicit embedded authoring rebuild. Never saves, exports, integrates or renders.
Edit the shared master control vertices OR one of the 15 semantic height handles,
then run this Text. Changes are additive if both are edited before one rebuild.
The frozen source build uses unchanged controls; edited results need new gates.
"""
import json
from types import ModuleType
import bpy
import numpy as np

def modules():
    c=ModuleType('embedded_contract62');c.__file__=bpy.data.filepath or '/embedded/ridge/build-v1/contract62.py'
    exec(compile(bpy.data.texts['CONTRACT62.py'].as_string(),'CONTRACT62.py','exec'),c.__dict__)
    return c,json.loads(bpy.data.texts['BINDINGS62.json'].as_string())

def write_mesh(ob,vertices,faces,material_ids,b,master_ids,source_triangles,tile_ids,tile=None):
    """Finish ALL CustomData allocations before retaining any attribute handle."""
    mesh=bpy.data.meshes.new(ob.name+'_mesh');mesh.from_pydata(vertices,[],faces);mesh.update()
    old=ob.data;ob.data=mesh
    if old and old.users==0:bpy.data.meshes.remove(old)
    for g in list(ob.vertex_groups):ob.vertex_groups.remove(g)
    for material in b['materials']:mesh.materials.append(bpy.data.materials[material['name']])
    for i in range(len(mesh.polygons)):
        mesh.polygons[i].use_smooth=False;mesh.polygons[i].material_index=material_ids[i]
    for control in b['controls']:ob.vertex_groups.new(name=control['name'])
    for local_id,mid in enumerate(master_ids):
        for ci,w in zip(b['control_ids'][mid],b['weights64'][mid]):
            if w>0:ob.vertex_groups[ci].add([local_id],float(w),'REPLACE')
    schemas=[('source_master_vertex','INT','POINT'),('original_source_vertex','INT','POINT'),('original_color','FLOAT_COLOR','POINT'),('original_local','FLOAT_VECTOR','POINT'),('original_world','FLOAT_VECTOR','POINT'),('canonical_base_y','FLOAT','POINT'),('collar','FLOAT','POINT'),('changed','BOOLEAN','POINT'),('source_triangle','INT','FACE'),('source_tile','INT','FACE'),('material_region','INT','FACE')]
    for name,kind,domain in schemas:mesh.attributes.new(name=name,type=kind,domain=domain)
    values=dict(source_master_vertex=master_ids,original_source_vertex=list(range(len(master_ids))) if tile else [-1]*len(master_ids),original_color=tile['original_color_float32'] if tile else [[0.,0.,0.,0.]]*len(master_ids),original_local=tile['original_source_local_xyz'] if tile else [[0.,0.,0.]]*len(master_ids),original_world=[b['before_xyz'][i]for i in master_ids],canonical_base_y=[b['canonical_base_y'][i]for i in master_ids],collar=[b['collar64'][i]for i in master_ids],changed=[b['changed'][i]for i in master_ids],source_triangle=source_triangles,source_tile=tile_ids,material_region=material_ids)
    for name,kind,domain in schemas:
        attr=mesh.attributes[name]
        for i,value in enumerate(values[name]):
            if kind=='FLOAT_VECTOR':attr.data[i].vector=value
            elif kind=='FLOAT_COLOR':attr.data[i].color=value
            else:attr.data[i].value=value
        del attr
    mesh.update()

def rebuild(initial=False):
    c,b=modules();bpy.context.view_layer.update();control=bpy.data.objects['R62_MASTER_CONTROL'];targets=[]
    for name in ['R62_MASTER_CONTROL','R62_MASTER_EVALUATED']+['R62_'+x for x in c.TILES]:
        ob=bpy.data.objects[name]
        c.require(ob.mode=='OBJECT' and not ob.data.is_editmode,'Exit Edit Mode on every ridge mesh before running REBUILD62.py')
        c.require(np.array_equal(np.asarray(ob.matrix_world,float),np.eye(4)),'Ridge object transforms must stay identity; edit master vertices or semantic handle Z instead')
    for i,row in enumerate(b['controls']):
        v=control.data.vertices[i];planned=c.local([[row['xz'][0],row['target_y'],row['xz'][1]]])[0]
        c.require(c.digest(list(v.co)[:2])==c.digest(planned[:2]),'Control XZ locked; shape revision requires a new binding')
        height=float(v.co.z)
        if i<12:c.require(c.digest([height])==c.digest([row['target_y']]),'Boundary height locked')
        else:
            handle=bpy.data.objects['R62_HANDLE_'+row['name']]
            c.require(c.digest(list(handle.location)[:2])==c.digest(planned[:2]),'Semantic XZ locked')
            height+=float(handle.location.z)-float(handle['last_synced_height'])
        targets.append(height)
    # Boundary source target heights are stored as original doubles; native points
    # are float32. Preserve their original zero-delta values in the evaluator.
    targets[:12]=[row['target_y']for row in b['controls'][:12]]
    candidate=c.expected(b,targets)
    if initial:c.require(c.digest(candidate['vertices'])==c.digest(c.expected(b)['vertices']),'Exact initial frozen candidate')
    master=bpy.data.objects['R62_MASTER_EVALUATED']
    write_mesh(master,candidate['vertices'],candidate['faces'],candidate['materials'],b,list(range(len(b['before_xyz']))),b['master_source_triangles'],b['master_tile_ids'])
    for ti,tile in enumerate(b['tiles']):
        ids=tile['master_vertex_ids'];face_ids=tile['master_face_ids']
        write_mesh(bpy.data.objects['R62_'+tile['name']],[candidate['vertices'][i]for i in ids],tile['faces_blender'],[candidate['materials'][i]for i in face_ids],b,ids,list(range(len(face_ids))),[ti]*len(face_ids),tile)
    for i in range(12,27):
        row=b['controls'][i];control.data.vertices[i].co.z=targets[i];handle=bpy.data.objects['R62_HANDLE_'+row['name']];handle.location.z=targets[i];handle['last_synced_height']=targets[i]
    control.data.update();bpy.context.view_layer.update()
    bpy.context.scene['edited_after_frozen_build']=not initial
    bpy.context.scene['world_integration_allowed']=False
    return candidate

if __name__=='__main__':
    rebuild();print('Shared ridge control surface and four derivative tiles updated. Unsaved; integration and visual acceptance remain blocked.')
