"""Reconstruct exactly the current saved Godot tile as a separately editable Blender asset.
No legacy GLB is read. Godot local (x,y,z) -> Blender local (x,-z,y).
Faces reverse winding only for Blender display; readback reverses it again.
Original packed arrays remain independently available under native-authority.
"""
import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
src=json.loads((D/'native-authority/authority.json').read_text())
a=src['surfaces'][0]['arrays'];p=np.asarray(a[0],np.float32);idx=np.asarray(a[12],np.int32).reshape(-1,3)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
verts=np.column_stack((p[:,0],-p[:,2],p[:,1]));faces=idx[:,[0,2,1]]
mesh=bpy.data.meshes.new('Ground_-4_-4_current53_authority');mesh.from_pydata(verts.tolist(),[],faces.tolist());mesh.update()
obj=bpy.data.objects.new('Ground_-4_-4_AUTHORITY',mesh);bpy.context.collection.objects.link(obj)
for name,typ,values,prop in [
 ('godot_normal','FLOAT_VECTOR',a[1],'vector'),
 ('godot_tangent_xyz','FLOAT_VECTOR',np.asarray(a[2],np.float32).reshape(-1,4)[:,:3],'vector'),
 ('godot_tangent_w','FLOAT',np.asarray(a[2],np.float32).reshape(-1,4)[:,3],'value')]:
 att=mesh.attributes.new(name,typ,'POINT');att.data.foreach_set(prop,np.asarray(values,np.float32).ravel())
col=mesh.color_attributes.new(name='NativeColor',type='FLOAT_COLOR',domain='POINT');col.data.foreach_set('color',np.asarray(a[3],np.float32).ravel())
orig=mesh.attributes.new('native_vertex_index','INT','POINT');orig.data.foreach_set('value',np.arange(len(p),dtype=np.int32))
face_id=mesh.attributes.new('native_triangle_index','INT','FACE');face_id.data.foreach_set('value',np.arange(len(idx),dtype=np.int32))
# Custom Blender split normals are display data; exact native normals are above.
n=np.asarray(a[1],np.float32);bn=np.column_stack((n[:,0],-n[:,2],n[:,1]));mesh.normals_split_custom_set(bn[faces.ravel()].tolist())
mat=bpy.data.materials.new('Meadow stone and shore.080 [native identity; preview shader]');mat.use_nodes=True
nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
color=nodes.new('ShaderNodeVertexColor');color.layer_name='NativeColor';mat.node_tree.links.new(color.outputs['Color'],bs.inputs['Base Color']);mesh.materials.append(mat)
obj['source_scene']=src['source'];obj['source_sha256']=src['source_sha256'];obj['native_mesh_resource']=src['mesh'];obj['native_collision_resource']=src['shape'];obj['world_origin_godot']=[-3072,0,-3072]
obj['axis_contract']='Godot(x,y,z) -> Blender(x,-z,y); reverse triangle corners 1 and 2 for display; invert both on native readback'
obj['authority_fields']='Godot normals/tangents retain exact packed float32 values in explicit POINT attributes; NativeColor is FLOAT_COLOR; UV absent in source'
obj['open_heightfield']='Retain original open terrain sheet; no bottom or side walls added'
obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=2
bpy.ops.wm.save_as_mainfile(filepath=str(D/'Ground_-4_-4_authority56.blend'),check_existing=False)
print('AUTHORITY56_SAVED',len(mesh.vertices),len(mesh.polygons))
