import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
S=np.array([[1,0,0],[0,0,-1],[0,1,0]],np.float32)
origin=np.array([-3840,0,-3840],np.float32)
out={'blend':bpy.data.filepath,'meshes':{},'placements':[]}
for collection in bpy.data.collections:
    if collection.name.startswith('Coast57B_'):collection.hide_viewport=False
bpy.context.view_layer.update()
for ob in bpy.data.objects:
    if 'source_instance_index' not in ob:continue
    mesh=ob.data;key=mesh['native_mesh_resource']
    if key not in out['meshes']:
        v=np.empty(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)@S
        idx=np.array([list(p.vertices) for p in mesh.polygons],np.int32)[:,[0,2,1]].ravel()
        c=np.empty(len(mesh.vertices)*4,np.float32);mesh.color_attributes['NativeColor'].data.foreach_get('color',c)
        n=np.empty(len(mesh.vertices)*3,np.float32);mesh.attributes['native_normal'].data.foreach_get('vector',n)
        out['meshes'][key]={'vertices':v.tolist(),'indices':idx.tolist(),'colors':c.reshape(-1,4).tolist(),'normals':n.reshape(-1,3).tolist()}
    matrix=np.array(ob.matrix_world,np.float32);buf=np.empty((3,4),np.float32);buf[:,:3]=S.T@matrix[:3,:3]@S
    buf[:,3]=((S.T@matrix[:3,3]).astype(float)+origin.astype(float)-np.array(ob['source_group_origin'],float)).astype(np.float32)
    out['placements'].append({'node':ob['source_node'],'index':int(ob['source_instance_index']),'phase':ob['phase'],'matrix_native_buffer':buf.ravel().tolist(),'stored_native_buffer':list(ob['native_buffer']),'mesh':key})
(D/'candidate-props-readback.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print('FRESH57B_PROP_READBACK',len(out['meshes']),'unique meshes',len(out['placements']),'placements')
