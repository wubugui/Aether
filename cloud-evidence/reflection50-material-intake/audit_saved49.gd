extends SceneTree
var rows=[]
var material_ids={}
var materials=[]
var layers={}
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
 materials.append(r);return index
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
 f.store_string(JSON.stringify({'scene_sha':FileAccess.get_sha256('res://scenes/candidate49/Game49.tscn'),'meshes':rows,'materials':materials,'visual_layer_masks':layers,'scope':'Read-only off-tree saved scene inventory. No Standard shader conversion, no MM transforms or renderer acceptance inferred.'},'  '));f.close();g.free();quit()
