extends SceneTree
var rows=[]
var material_ids={}
var materials=[]
var layers={}
var material_refs=[]
func v(p:Vector3):return [p.x,p.y,p.z]
func mat(m:Material):
 if m==null:return -1
 var id=m.get_instance_id()
 if material_ids.has(id):return material_ids[id]
 var index=materials.size();material_ids[id]=index
 var r={"index":index,"class":m.get_class(),"resource_path":m.resource_path,"name":m.resource_name}
 if m is StandardMaterial3D:
  for key in ['transparency','shading_mode','diffuse_mode','specular_mode','cull_mode','vertex_color_use_as_albedo','vertex_color_is_srgb','albedo_color','metallic','roughness','emission_enabled','normal_enabled','subsurf_scatter_enabled','refraction_enabled','no_depth_test','billboard_mode','proximity_fade_enabled','distance_fade_mode','disable_receive_shadows']:
   r[key]=str(m.get(key))
 if m is ShaderMaterial:
  r['shader_path']=m.shader.resource_path;r['shader_code']=m.shader.code
  var params={}
  for p in m.shader.get_shader_uniform_list():params[str(p.name)]=str(m.get_shader_parameter(p.name))
  r['parameters']=params
 materials.append(r);material_refs.append(m);return index
func walk(n:Node,t:Transform3D,p:String):
 if n is Node3D:t=t*n.transform
 p+='/'+str(n.name)
 if n is VisualInstance3D:layers[str(n.layers)]=int(layers.get(str(n.layers),0))+1
 if n is MeshInstance3D and n.mesh:
  var a=t*n.mesh.get_aabb();var active=[]
  for i in n.mesh.get_surface_count():active.append(mat(n.get_active_material(i)))
  var runtime=-1
  var parent=n.get_parent()
  while parent and parent!=get_root():
   for prop in parent.get_property_list():
    if str(prop.name)=='surface_material':runtime=mat(parent.get('surface_material'));break
   if runtime>=0:break
   parent=parent.get_parent()
  rows.append({'path':p,'aabb_min':v(a.position),'aabb_max':v(a.end),'active_materials':active,'asset_instance_runtime_material':runtime,'layers':n.layers,'straddles_y0':a.position.y<0 and a.end.y>0,'fully_below_y0':a.end.y<=0})
 for c in n.get_children():walk(c,t,p)
func _initialize():
 var g=load('res://scenes/candidate49/Game49.tscn').instantiate();walk(g,Transform3D.IDENTITY,'')
 var f=FileAccess.open('/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection50-material-intake/saved49-materials.json',FileAccess.WRITE)
 f.store_string(JSON.stringify({'scene_sha':FileAccess.get_sha256('res://scenes/candidate49/Game49.tscn'),'meshes':rows,'materials':materials,'visual_layer_masks':layers,'scope':'Read-only off-tree saved scene inventory. No Standard shader conversion, no MM transforms or renderer acceptance inferred.'},'  '));f.close();export_groups();g.free();quit()

func encoded(value):
 if value is Resource:return {"type":value.get_class(),"path":value.resource_path}
 if value is Color:return [value.r,value.g,value.b,value.a]
 if value is Vector2:return [value.x,value.y]
 if value is Vector3:return [value.x,value.y,value.z]
 if value is Vector4:return [value.x,value.y,value.z,value.w]
 if value is Dictionary:
  var d={}
  for k in value:d[str(k)]=encoded(value[k])
  return d
 if value is Array:
  var a=[]
  for v in value:a.append(encoded(v))
  return a
 return value
func export_groups():
 var needed={};var groups={}
 for row in rows:
  if row.aabb_min[1]>=0:continue
  var ids=row.active_materials.duplicate();ids.append(row.asset_instance_runtime_material)
  for id in ids:
   if id>=0 and material_refs[id] is StandardMaterial3D:
    if not needed.has(id):needed[id]=[]
    needed[id].append({"node":row.path,"runtime_surface_material":row.asset_instance_runtime_material,"active_materials":row.active_materials})
 for id in needed:
  var m=material_refs[id];var feature={};var full={};var resources=[]
  for prop in m.get_property_list():
   var key=str(prop.name)
   if prop.usage & PROPERTY_USAGE_STORAGE and key not in ['resource_path','resource_name','resource_local_to_scene','script']:
    var value=m.get(key);full[key]=encoded(value)
    if value is Resource:resources.append({"property":key,"resource":encoded(value)})
    if key!='albedo_color':feature[key]=encoded(value)
  var key=JSON.stringify(feature).sha256_text()
  if not groups.has(key):groups[key]={"feature_sha256":key,"feature_configuration":feature,"members":[],"representative_index":id,"non_null_resource_features":resources}
  groups[key].members.append({"material_index":id,"original_path":m.resource_path,"original_name":m.resource_name,"all_storage_properties":full,"uses":needed[id]})
 var dest='res://assets/reflection50_intake/'
 DirAccess.make_dir_recursive_absolute(dest)
 var output=[];var number=0
 for key in groups:
  number+=1;var group=groups[key];var path=dest+'native_group_%02d.tres'%number
  if FileAccess.file_exists(path):push_error('Refuse overwrite representative '+path);quit(3);return
  var copy=material_refs[group.representative_index].duplicate(false)
  if ResourceSaver.save(copy,path)!=OK:push_error('save failed');quit(4);return
  group['representative_path']=path;group['representative_sha256']=FileAccess.get_sha256(path);group['count']=group.members.size();output.append(group)
 var f=FileAccess.open('/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection50-material-intake/native-feature-groups.json',FileAccess.WRITE)
 f.store_string(JSON.stringify({'scene_sha':FileAccess.get_sha256('res://scenes/candidate49/Game49.tscn'),'grouping':'All STORAGE properties retained except resource identity/localness and albedo_color. Color is the sole varying shader uniform excluded from feature key, and is recorded per member. No conversion or injection performed.','negative_y_material_count':needed.size(),'groups':output},'  '));f.close();print('NATIVE GROUPS ',groups.size(),' MATERIALS ',needed.size())
