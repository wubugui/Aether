"""Pure buffer/batch recipes. No Blender import and no native execution."""
import struct
import numpy as np
SCHEMAS=[('source_master_vertex','INT','POINT'),('original_source_vertex','INT','POINT'),('original_color','FLOAT_COLOR','POINT'),('original_local','FLOAT_VECTOR','POINT'),('original_world','FLOAT_VECTOR','POINT'),('canonical_base_y','FLOAT','POINT'),('collar','FLOAT','POINT'),('changed','BOOLEAN','POINT'),('source_triangle','INT','FACE'),('source_tile','INT','FACE'),('material_region','INT','FACE')]
KINDS={'INT':('value','<i4',1),'FLOAT':('value','<f4',1),'BOOLEAN':('value','?',1),'FLOAT_VECTOR':('vector','<f4',3),'FLOAT_COLOR':('color','<f4',4)}

def weight_batches(binding,master_ids):
    """No weight rounding policy change: group exactly equal native float32 bits.
    Original VertexGroup.add accepts one C float weight. Positive original slots
    alone have membership; no zero slots are introduced or tiny values dropped.
    """
    buckets={}
    for local_id,mid in enumerate(master_ids):
        for control,weight in zip(binding['control_ids'][mid],binding['weights64'][mid]):
            if weight>0:
                bits=struct.pack('<f',weight)
                buckets.setdefault((control,bits),[]).append(local_id)
    return [(control,struct.unpack('<f',bits)[0],vertices)for(control,bits),vertices in sorted(buckets.items())]

def attribute_buffers(b,master_ids,source_triangles,tile_ids,material_ids,tile=None):
    values=dict(source_master_vertex=master_ids,original_source_vertex=list(range(len(master_ids)))if tile else [-1]*len(master_ids),original_color=tile['original_color_float32']if tile else [[0.,0.,0.,0.]]*len(master_ids),original_local=tile['original_source_local_xyz']if tile else [[0.,0.,0.]]*len(master_ids),original_world=[b['before_xyz'][i]for i in master_ids],canonical_base_y=[b['canonical_base_y'][i]for i in master_ids],collar=[b['collar64'][i]for i in master_ids],changed=[b['changed'][i]for i in master_ids],source_triangle=source_triangles,source_tile=tile_ids,material_region=material_ids)
    return {name:np.ascontiguousarray(values[name],dtype=KINDS[kind][1]).reshape(-1)for name,kind,domain in SCHEMAS}

def read_collection(collection,prop,dtype,components=1):
    out=np.empty(len(collection)*components,dtype=dtype)
    collection.foreach_get(prop,out)
    return out.reshape(-1,components).tolist()if components>1 else out.tolist()
