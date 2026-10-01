import bpy,json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent;d=json.loads((D/'candidate-native.json').read_text());a=d['surface_arrays']
source=bpy.data.objects['Ground_-5_-5_AUTHORITY'];source.hide_render=True;source.hide_set(True)
obj=source.copy();obj.data=source.data.copy();obj.name='Ground_-5_-5_COAST57B';obj.data.name='Ground_-5_-5_explicit_profile_bay57b';bpy.context.collection.objects.link(obj);obj.hide_render=False;obj.hide_set(False)
p=np.asarray(a[0],np.float32);coords=np.column_stack((p[:,0],-p[:,2],p[:,1]));obj.data.vertices.foreach_set('co',coords.ravel());obj.data.update()
obj.data.attributes['godot_normal'].data.foreach_set('vector',np.asarray(a[1],np.float32).ravel())
tan=np.asarray(a[2],np.float32).reshape(-1,4);obj.data.attributes['godot_tangent_xyz'].data.foreach_set('vector',tan[:,:3].ravel());obj.data.attributes['godot_tangent_w'].data.foreach_set('value',tan[:,3])
normal=np.asarray(a[1],np.float32);bn=np.column_stack((normal[:,0],-normal[:,2],normal[:,1]));face=np.asarray(a[12],np.int32).reshape(-1,3)[:,[0,2,1]];obj.data.normals_split_custom_set(bn[face.ravel()].tolist())
mask=obj.data.attributes.new('coast57b_changed_vertex','BOOLEAN','POINT');values=np.zeros(len(p),bool);values[d['moved_vertex_indices']]=True;mask.data.foreach_set('value',values)
obj['edit_scope']='Current53 Ground_-5_-5 interior; world X[-3440,-3090], Z[-3816,-3430]. Exact original XZ/topology, material/colors, exterior and tile boundary including inherited seam differences preserved.'
obj['design_inference']='One broad shallow bay and unequal low shoulder; northern high plateau and southern lower slope retained behind the bench. Native profile changes Y only. Reference-informed inference, not measured reference coordinates.'
obj['collision_data']='candidate-native.json collider_faces; original corners preserved unless their authoritative native vertex moved'
obj['scatter_data']='scatter-replacements.json; 60 roots in expanded box; scatter-replacements-seated.json records physical-foot seating and seven individually recorded bounded XZ relocations'
for ob in bpy.context.selected_objects:ob.select_set(False)
obj.select_set(True);bpy.context.view_layer.objects.active=obj
exec(compile((D/'add_editable_props57b.py').read_text(),str(D/'add_editable_props57b.py'),'exec'))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'Ground_-5_-5_coast57b.blend'),check_existing=False)
print('COAST57B_NATIVE_SAVED',len(obj.data.vertices),len(obj.data.polygons))
