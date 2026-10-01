extends SceneTree
var output=""
var height_texture_path=""
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
  var stored={};var feature={}
  for prop in m.get_property_list():
   var key=str(prop.name)
   if prop.usage & PROPERTY_USAGE_STORAGE and key not in ['resource_path','resource_name','resource_local_to_scene','script']:
    stored[key]=encoded(m.get(key))
    if key!='albedo_color':feature[key]=encoded(m.get(key))
  r['all_storage_properties']=stored;r['feature_configuration']=feature;r['feature_sha256']=JSON.stringify(feature).sha256_text()
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
func _initialize():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with('--output-dir='):output=arg.trim_prefix('--output-dir=')
  if arg.begins_with('--height-texture='):height_texture_path=arg.trim_prefix('--height-texture=')
 call_deferred('run')
func run():
 if DisplayServer.get_name()=='headless':push_error('Ready-state audit requires real renderer');quit(2);return
 if output.is_empty() or not FileAccess.file_exists(height_texture_path):push_error('Missing diagnostic output/height texture');quit(3);return
 DirAccess.make_dir_recursive_absolute(output)
 root.size=Vector2i(1180,664)
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
 var f=FileAccess.open(output.path_join('ready49-materials.json'),FileAccess.WRITE);f.store_string(JSON.stringify(report,'  '));f.close()
 print('READY49 MATERIAL AUDIT saved=',before.meshes_and_multimeshes.size(),' ready=',after.meshes_and_multimeshes.size(),' switched=',bindings.size())
 var ok=await depth_controls(g,sha)
 g.queue_free()
 for i in range(8):await process_frame
 quit(0 if ok else 1)

func freeze(node):
 node.process_mode=Node.PROCESS_MODE_DISABLED
 for child in node.get_children():freeze(child)
func shot(name):
 for i in range(8):await process_frame
 await RenderingServer.frame_post_draw
 var path=output.path_join(name+'.png');var im=root.get_texture().get_image();var error=im.save_png(path)
 return {'path':path,'sha256':FileAccess.get_sha256(path),'width':im.get_width(),'height':im.get_height(),'saved':error==OK}
func depth_controls(g,source_sha):
 var ocean=g.get_node('World/Ocean');var original=ocean.material_override as ShaderMaterial
 if original==null:push_error('Expected native saved Ocean ShaderMaterial');return false
 var needle='float water_depth=max(world_point.y-bottom_world.y,0.);'
 if original.shader.code.count(needle)!=1:push_error('Exact saved49 depth assignment changed');return false
 var height_image=load(height_texture_path) as Image
 if height_image==null or height_image.get_width()!=769 or height_image.get_height()!=1537 or height_image.get_format()!=Image.FORMAT_RF:push_error('Expected 769x1537 independent R32F height Image resource');return false
 var height_texture=ImageTexture.create_from_image(height_image)
 var material=original.duplicate(false) as ShaderMaterial
 var shader=Shader.new()
 var declarations='\nuniform sampler2D lake50_height : filter_linear, repeat_disable;\n'
 var replacement=needle+"""
    // DIAGNOSTIC ONLY: same water styling, substitute true vertical highest
    // ground-support height at this fragment's own world XZ inside two tiles.
    vec2 lake50_grid=world_point.xz-vec2(768.,-2304.);
    if(lake50_grid.x>=0. && lake50_grid.x<=768. && lake50_grid.y>=0. && lake50_grid.y<=1536.){
        vec2 lake50_uv=(lake50_grid+vec2(.5))/vec2(769.,1537.);
        water_depth=max(0.,world_point.y-textureLod(lake50_height,lake50_uv,0.).r);
    }
"""
 shader.code=original.shader.code.replace('shader_type spatial;','shader_type spatial;'+declarations).replace(needle,replacement)
 material.shader=shader
 var uniform_checks=[]
 for p in original.shader.get_shader_uniform_list():
  var name=str(p.name);var value=original.get_shader_parameter(name);material.set_shader_parameter(name,value)
  uniform_checks.append({'name':name,'preserved':material.get_shader_parameter(name)==value})
 material.set_shader_parameter('lake50_height',height_texture)
 freeze(g)
 var images=[];var rows=[]
 for reference in ['1128','1129']:
  ocean.material_override=original;g.observe_reference(reference)
  for i in range(3):await process_frame
  images.append(await shot(reference+'-A-original-depth'))
  ocean.material_override=material
  images.append(await shot(reference+'-B-world-vertical-depth'))
  ocean.material_override=original
  images.append(await shot(reference+'-A2-restored-depth'))
  rows.append({'reference':reference,'camera_transform':str(g.camera.global_transform),'fov':g.camera.fov})
 var restored=ocean.material_override==original
 var unchanged=FileAccess.get_sha256('res://scenes/candidate49/Game49.tscn')==source_sha
 var good=restored and unchanged
 for row in uniform_checks:good=good and row.preserved
 var report={'diagnostic_completed':good,'candidate_written':false,'game49_sha256':source_sha,'game49_unchanged':unchanged,'ocean_original_material_restored':restored,'height_texture':height_texture_path,'height_texture_sha256':FileAccess.get_sha256(height_texture_path),'bounds':[768,-2304,1536,-768],'grid_spacing_m':1,'texel_centers':'((world_x-768+0.5)/769,(world_z+2304+0.5)/1537)','source_water_shader_sha256':original.shader.code.sha256_text(),'diagnostic_water_shader_sha256':shader.code.sha256_text(),'uniform_checks':uniform_checks,'images':images,'cameras':rows,'visual_acceptance':false,'scope':'Read-only runtime A/B/A water-depth causal test. Geometry, original materials, opacity, colors, lighting and reference cameras not changed. Only water_depth input inside bounded two-tile region is substituted. Runtime processing frozen for comparison. No saved candidate modification.'}
 var f=FileAccess.open(output.path_join('depth-diagnostic-report.json'),FileAccess.WRITE);f.store_string(JSON.stringify(report,'  '));f.close()
 f=FileAccess.open(output.path_join('diagnostic-water.gdshader'),FileAccess.WRITE);f.store_string(shader.code);f.close()
 print('DEPTH50 DIAGNOSTIC completed=',good,' original_restored=',restored,' candidate_written=false')
 return good

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
