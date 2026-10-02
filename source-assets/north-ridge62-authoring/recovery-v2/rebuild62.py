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

def bulk_module():
    module=ModuleType('embedded_bulk62')
    exec(compile(bpy.data.texts['BULK62.py'].as_string(),'BULK62.py','exec'),module.__dict__)
    return module

def write_mesh(ob,vertices,faces,material_ids,b,master_ids,source_triangles,tile_ids,tile=None,progress=None):
    """Same native fields; batch operations never span structural RNA mutation."""
    emit=progress or (lambda stage,**details:None);bulk=bulk_module()
    emit('mesh.begin',mesh=ob.name,vertices=len(vertices),triangles=len(faces))
    mesh=bpy.data.meshes.new(ob.name+'_mesh');mesh.from_pydata(vertices,[],faces);mesh.update()
    old=ob.data;ob.data=mesh
    if old and old.users==0:bpy.data.meshes.remove(old)
    for group in list(ob.vertex_groups):ob.vertex_groups.remove(group)
    for material in b['materials']:mesh.materials.append(bpy.data.materials[material['name']])
    mesh.polygons.foreach_set('use_smooth',np.zeros(len(faces),dtype=np.bool_))
    mesh.polygons.foreach_set('material_index',np.asarray(material_ids,dtype=np.int32))
    for control in b['controls']:ob.vertex_groups.new(name=control['name'])
    batches=bulk.weight_batches(b,master_ids)
    emit('mesh.weights.begin',mesh=ob.name,batches=len(batches),memberships=sum(len(ids)for _,_,ids in batches))
    for j,(ci,weight,ids) in enumerate(batches):
        ob.vertex_groups[ci].add(ids,weight,'REPLACE')
        if (j+1)%1000==0:emit('mesh.weights.progress',mesh=ob.name,finished_batches=j+1,total_batches=len(batches))
    emit('mesh.weights.complete',mesh=ob.name,batches=len(batches))
    # Finish all CustomData allocations before any Attribute/data handle survives.
    for name,kind,domain in bulk.SCHEMAS:mesh.attributes.new(name=name,type=kind,domain=domain)
    buffers=bulk.attribute_buffers(b,master_ids,source_triangles,tile_ids,material_ids,tile)
    for name,kind,domain in bulk.SCHEMAS:
        attr=mesh.attributes[name]
        attr.data.foreach_set(bulk.KINDS[kind][0],buffers[name])
        del attr
    mesh.update();emit('mesh.complete',mesh=ob.name,attribute_collections=len(bulk.SCHEMAS))

def rebuild(initial=False,progress=None):
    emit=progress or (lambda stage,**details:None)
    emit('rebuild.begin');c,b=modules();emit('rebuild.embedded_data_loaded');bpy.context.view_layer.update();control=bpy.data.objects['R62_MASTER_CONTROL'];targets=[]
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
    emit('rebuild.evaluate.begin');candidate=c.expected(b,targets);emit('rebuild.evaluate.complete')
    if initial:c.require(c.digest(candidate['vertices'])==c.digest(c.expected(b)['vertices']),'Exact initial frozen candidate')
    master=bpy.data.objects['R62_MASTER_EVALUATED']
    write_mesh(master,candidate['vertices'],candidate['faces'],candidate['materials'],b,list(range(len(b['before_xyz']))),b['master_source_triangles'],b['master_tile_ids'],progress=emit)
    for ti,tile in enumerate(b['tiles']):
        ids=tile['master_vertex_ids'];face_ids=tile['master_face_ids']
        write_mesh(bpy.data.objects['R62_'+tile['name']],[candidate['vertices'][i]for i in ids],tile['faces_blender'],[candidate['materials'][i]for i in face_ids],b,ids,list(range(len(face_ids))),[ti]*len(face_ids),tile,progress=emit)
    for i in range(12,27):
        row=b['controls'][i];control.data.vertices[i].co.z=targets[i];handle=bpy.data.objects['R62_HANDLE_'+row['name']];handle.location.z=targets[i];handle['last_synced_height']=targets[i]
    control.data.update();bpy.context.view_layer.update()
    bpy.context.scene['edited_after_frozen_build']=not initial
    bpy.context.scene['world_integration_allowed']=False
    emit('rebuild.complete');return candidate

if __name__=='__main__':
    rebuild();print('Shared ridge control surface and four derivative tiles updated. Unsaved; integration and visual acceptance remain blocked.')
