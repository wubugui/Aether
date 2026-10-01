extends SceneTree
var rows=[]
var material_ids={}
var materials=[]
var layers={}
var camera_rows=[]
var light_rows=[]
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
 if n is Camera3D:camera_rows.append({'path':p,'cull_mask':n.cull_mask,'near':n.near,'far':n.far,'keep_aspect':n.keep_aspect,'current':n.current})
 if n is Light3D:light_rows.append({'path':p,'light_cull_mask':n.light_cull_mask,'shadow_enabled':n.shadow_enabled})
 if n is MultiMeshInstance3D and n.multimesh and n.multimesh.mesh:
  var a=t*n.multimesh.get_aabb();var active=[]
  for i in n.multimesh.mesh.get_surface_count():active.append(mat(n.material_override if n.material_override else n.multimesh.mesh.surface_get_material(i)))
  rows.append({'path':p,'class':'MultiMeshInstance3D','aabb_min':v(a.position),'aabb_max':v(a.end),'active_materials':active,'layers':n.layers,'instance_count':n.multimesh.instance_count,'visible_instance_count':n.multimesh.visible_instance_count,'straddles_y0':a.position.y<0 and a.end.y>0,'fully_below_y0':a.end.y<=0})
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

func collect(g):
 rows=[];material_ids={};materials=[];layers={};camera_rows=[];light_rows=[]
 walk(g,Transform3D.IDENTITY,'')
 return {'meshes_and_multimeshes':rows.duplicate(true),'materials':materials.duplicate(true),'visual_layer_masks':layers.duplicate(true),'cameras':camera_rows.duplicate(true),'lights':light_rows.duplicate(true)}
func settle():
 for i in range(3):await process_frame
 await RenderingServer.frame_post_draw
func _initialize():call_deferred('run')
func run():
 if DisplayServer.get_name()=='headless':push_error('Ready-state audit requires real renderer');quit(2);return
 var source='res://scenes/candidate49/Game49.tscn'
 var sha=FileAccess.get_sha256(source)
 var g=load(source).instantiate();await settle()
 var before=collect(g)
 root.add_child(g)
 for i in range(8):await process_frame
 g.observe_reference('1128')
 for i in range(20):await process_frame
 await RenderingServer.frame_post_draw
 var after=collect(g)
 var bindings=[];var bnodes={}
 for row in before.meshes_and_multimeshes:bnodes[row.path]=row
 for row in after.meshes_and_multimeshes:
  if not bnodes.has(row.path):continue
  var old=bnodes[row.path];var bm=[];var am=[]
  for i in old.active_materials:bm.append(before.materials[i].get('resource_path','')+' | '+before.materials[i]['class'])
  for i in row.active_materials:am.append(after.materials[i].get('resource_path','')+' | '+after.materials[i]['class'])
  if bm!=am:bindings.append({'path':row.path,'saved_bindings':bm,'ready_bindings':am,'saved_parent_authority_index':old.get('asset_instance_runtime_material',-1),'ready_parent_authority_index':row.get('asset_instance_runtime_material',-1)})
 var report={'source':source,'source_sha256':sha,'source_unchanged':sha==FileAccess.get_sha256(source),'renderer':RenderingServer.get_video_adapter_name(),'before_ready':before,'after_ready_1128':after,'changed_material_bindings':bindings,'scope':'Read-only instantiated runtime material/layer inventory, including MM. No material conversion, no save of candidate, no claim of visual acceptance.'}
 var f=FileAccess.open('/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection50-material-intake/ready49-materials.json',FileAccess.WRITE);f.store_string(JSON.stringify(report,'  '));f.close()
 print('READY49 MATERIAL AUDIT saved=',before.meshes_and_multimeshes.size(),' ready=',after.meshes_and_multimeshes.size(),' switched=',bindings.size())
 g.queue_free()
 for i in range(8):await process_frame
 quit(0)
