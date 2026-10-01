extends SceneTree
const SOURCE="res://scenes/candidate53d-west/Game53dWest.tscn"
const PAYLOAD="/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/final-source/cirque54v2-payload.json"
const EXPECTED="6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18"
var failures=[]
var phase_log:FileAccess
var material_checks=[]
var encoded_color_hashes={}
func phase(name:String,details:Dictionary={}):
 var record={"phase":name,"ticks_msec":Time.get_ticks_msec(),"details":details}
 var line="CIRQUE54_PHASE "+JSON.stringify(record)
 print(line);printerr(line)
 if phase_log:phase_log.store_line(JSON.stringify(record));phase_log.flush()
func inspect_materials(label:String,nodes:Array,expected):
 var rows=[];var passed=true
 for n in nodes:
  var row={"node":str(n.name),"node_valid":is_instance_valid(n)}
  if row.node_valid:
   row.mesh_valid=is_instance_valid(n.mesh)
   row.override_valid=is_instance_valid(n.material_override)
   row.override_same=expected==n.material_override
   if row.override_valid:
    var mm=n.material_override
    row.material_path=mm.resource_path;row.material_instance=mm.get_instance_id();row.material_rid=str(mm.get_rid());row.material_rid_valid=mm.get_rid().is_valid()
    row.shader_valid=mm is ShaderMaterial and is_instance_valid(mm.shader)
    if row.shader_valid:row.shader_path=mm.shader.resource_path;row.shader_instance=mm.shader.get_instance_id();row.shader_rid=str(mm.shader.get_rid());row.shader_rid_valid=mm.shader.get_rid().is_valid()
   if row.mesh_valid:row.active_matches=n.get_active_material(0)==expected;row.mesh_rid=str(n.mesh.get_rid());row.surface_count=n.mesh.get_surface_count()
  var okay=row.get("mesh_valid",false) and row.get("override_valid",false) and row.get("override_same",false) and row.get("material_rid_valid",false) and row.get("shader_valid",false) and row.get("shader_rid_valid",false) and row.get("active_matches",false)
  row.passed=okay;passed=passed and okay;rows.append(row)
 material_checks.append({"phase":label,"passed":passed,"nodes":rows});phase(label,{"material_checks":rows,"passed":passed})
 if not passed:failures.append("Material reference check: "+label)

func v(p):return Vector3(p[0],p[1],p[2])
func frames(n):for i in range(n):await process_frame
func freeze(n):
 n.set_process(false);n.set_physics_process(false);n.set_process_input(false);n.set_process_unhandled_input(false);n.set_process_unhandled_key_input(false)
 if n is AnimationPlayer:n.pause()
 if n is Timer:n.paused=true
 for c in n.get_children():freeze(c)
func scatter_digest(g):
 var state=[]
 for n in g.get_node("World/Vegetation").get_children():
  if n is MultiMeshInstance3D:
   var row=[str(n.name),n.multimesh.instance_count,n.multimesh.use_colors,n.multimesh.use_custom_data,n.multimesh.buffer]
   for i in n.multimesh.instance_count:row.append(n.multimesh.get_instance_transform(i))
   state.append(row)
 return var_to_bytes(state).hex_encode().sha256_text()
func west_digest(g):
 var a=g.get_node("World/Mountains/massif_west_spur");var rows=[]
 for n in a.get_node("Model").get_children():
  if n is MeshInstance3D:
   var surfaces=[]
   for i in n.mesh.get_surface_count():surfaces.append(n.mesh.surface_get_arrays(i))
   rows.append([str(n.name),n.transform,n.visible,n.mesh.resource_path,surfaces,n.material_override.get_instance_id() if n.material_override else 0])
 rows.append(a.get_node("Collision/Shape").shape.get_faces())
 return var_to_bytes(rows).hex_encode().sha256_text()
func raw_world_rows(node):
 var positions=PackedVector3Array();var colors=PackedColorArray()
 for surface in node.mesh.get_surface_count():
  var arrays=node.mesh.surface_get_arrays(surface);var indices=arrays[Mesh.ARRAY_INDEX]
  var count=indices.size() if indices!=null and indices.size()>0 else arrays[Mesh.ARRAY_VERTEX].size()
  for i in count:
   var j=indices[i] if indices!=null and indices.size()>0 else i
   positions.append(node.global_transform*arrays[Mesh.ARRAY_VERTEX][j]);colors.append(arrays[Mesh.ARRAY_COLOR][j])
 return {"positions":positions,"colors":colors}
func collision_digest(game):
 var rows=[]
 for n in game.find_children("*","CollisionShape3D",true,false):
  if n.shape==null:
   rows.append([str(game.get_path_to(n)),n.transform,n.disabled,"null"]);continue
  var shape=n.shape;var geometry=shape.get_faces() if shape is ConcavePolygonShape3D else var_to_bytes(shape)
  rows.append([str(game.get_path_to(n)),n.transform,n.disabled,shape.get_instance_id(),geometry])
 return var_to_bytes(rows).hex_encode().sha256_text()
func other_mesh_digest(game,except_node):
 var rows=[]
 for n in game.find_children("*","MeshInstance3D",true,false):
  if n==except_node or n.has_meta("cirque54v2_diagnostic_added"):continue
  if n.mesh==null:
   rows.append([str(game.get_path_to(n)),n.transform,n.visible,n.layers,"null"]);continue
  var surfaces=[]
  for surface in n.mesh.get_surface_count():surfaces.append([n.mesh.surface_get_arrays(surface),n.get_active_material(surface).get_instance_id() if n.get_active_material(surface) else 0])
  rows.append([str(game.get_path_to(n)),n.transform,n.visible,n.layers,n.mesh.get_instance_id(),surfaces])
 return var_to_bytes(rows).hex_encode().sha256_text()
func payload_matches(node,part):
 var rows=raw_world_rows(node);var positions=PackedVector3Array();var colors=PackedColorArray()
 for p in part.vertices:positions.append(v(p))
 for c in part.colors:colors.append(Color(c[0],c[1],c[2],c[3]))
 return rows.positions.to_byte_array()==positions.to_byte_array() and rows.colors.to_byte_array().hex_encode().sha256_text()==encoded_color_hashes[part.name]
func triangle_key(rows,index):
 var alternatives=[]
 for shift in 3:
  var points=PackedVector3Array();var colors=PackedColorArray()
  for j in 3:
   var i=index*3+(j+shift)%3;points.append(rows.positions[i]);colors.append(rows.colors[i])
  alternatives.append(points.to_byte_array().hex_encode()+colors.to_byte_array().hex_encode())
 alternatives.sort();return alternatives[0]
func preserved_native_faces(old_rows,new_rows):
 var candidates={}
 for i in new_rows.positions.size()/3:candidates[triangle_key(new_rows,i)]=true
 var wet_count=0;var missing_wet=[];var protection_count=0;var missing_protected=[]
 for i in old_rows.positions.size()/3:
  if min(old_rows.positions[i*3].y,old_rows.positions[i*3+1].y,old_rows.positions[i*3+2].y)<=0.0:
   wet_count+=1
   if not candidates.has(triangle_key(old_rows,i)):missing_wet.append(i)
 var ledger=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/final-source/surface-and-wet-ledger.json"))
 for row in ledger.protected_original_faces:
  protection_count+=1
  if not candidates.has(triangle_key(old_rows,int(row.original_triangle))):missing_protected.append(row.original_triangle)
 return {"wet_original_faces":wet_count,"protected_original_faces":protection_count,"missing_wet":missing_wet,"missing_protected":missing_protected,"oriented_native_world_geometry_rgba_exact":wet_count==432 and protection_count==19 and missing_wet.is_empty() and missing_protected.is_empty()}
func make_mesh(part,inv,mat):
 var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
 for i in part.vertices.size():
  var c=part.colors[i];st.set_color(Color(c[0],c[1],c[2],c[3]));st.add_vertex(inv*v(part.vertices[i]))
 st.generate_normals();var mesh=st.commit();mesh.surface_set_material(0,mat)
 return mesh
func _initialize():call_deferred("run")
func run():
 if DisplayServer.get_name()=="headless":quit(2);return
 var out=OS.get_environment("CIRQUE54_WORLD_OUT")
 if out.is_empty():quit(3);return
 phase_log=FileAccess.open(out.get_base_dir()+"/phases.jsonl",FileAccess.WRITE)
 phase("startup.before_load")
 if FileAccess.get_sha256(SOURCE)!=EXPECTED:push_error("Frozen saved53west authority mismatch");quit(4);return
 root.size=Vector2i(1180,664)
 var packed=load(SOURCE);var game=packed.instantiate();packed=null
 root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
 await frames(20);await RenderingServer.frame_post_draw;freeze(game)
 phase("baseline.before_digests")
 var asset=game.get_node("World/Mountains/massif_cirque_wall");var model=asset.get_node("Model")
 var original=asset.get_node("Model/massif_cirque_wall");var mat=asset.get("surface_material")
 var leaves=[]
 for n in model.get_children():leaves.append(str(n.name))
 if leaves!=["massif_cirque_wall"]:push_error("Unexpected saved53 cirque leaves; refusing broader replacement");quit(5);return
 var original_rows=raw_world_rows(original)
 var authority=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/native-authority/cirque-native-authority.json"))
 var authority_positions=PackedVector3Array()
 for point in authority.faces:authority_positions.append(v(point))
 var original_native_exact=original_rows.positions.to_byte_array()==authority_positions.to_byte_array()
 if not original_native_exact:push_error("Original raw saved root disagrees with native source authority");quit(6);return
 var original_properties=[original.transform,original.visible,original.layers,original.cast_shadow,original.material_override,original.get_surface_override_material(0),original.owner]
 var old_path=original.mesh.resource_path;var old_triangles=original_rows.positions.size()/3
 var initial_scatter=scatter_digest(game);var initial_west=west_digest(game);var initial_collision=collision_digest(game);var initial_others=other_mesh_digest(game,original)
 inspect_materials("baseline.cirque_original_binding",[original],mat)
 phase("baseline.after_digests")
 var encodings=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/world-diagnostic/native-mesh-encoding.json"))
 for row in encodings:encoded_color_hashes[row.component]=row.native_color_float32_hex_sha256
 var data=JSON.parse_string(FileAccess.get_file_as_string(PAYLOAD))
 if data.baseline_sha256!=EXPECTED or data.mountains.size()!=1 or data.mountains[0].name!="massif_cirque_wall":push_error("Source scope mismatch");quit(7);return
 var components=data.mountains[0].components
 var names=[]
 for part in components:names.append(part.name)
 if names!=["remodeled_cirque_body","snow_gully_a","snow_gully_b","upper_snow_basin"]:push_error("Source component set/order mismatch");quit(8);return
 var inserted=[];var changed=[];var payload_checks=[];var inv=asset.global_transform.affine_inverse()
 phase("replacement.before_root_mesh_assignment")
 # Same native root node; the old692triangle ArrayMesh is replaced, never overlaid.
 # No extra reference to the old mesh is held beyond assignment. Source proof preserves its432wet/19protected faces inside the new862triangle body.
 for part in components:
  var node=original
  if part.name!="remodeled_cirque_body":
   node=MeshInstance3D.new();node.name=part.name;node.set_meta("cirque54v2_diagnostic_added",true);node.material_override=mat
   node.mesh=make_mesh(part,inv,mat);model.add_child(node);inserted.append(node)
  else:node.mesh=make_mesh(part,inv,mat)
  var exact=payload_matches(node,part);payload_checks.append({"component":part.name,"raw_world_positions_and_native_encoded_rgba_exact":exact,"triangles":part.vertices.size()/3})
  if not exact:failures.append("Raw runtime payload differs: "+part.name)
  changed.append({"source_component":part.name,"runtime_node":str(game.get_path_to(node)),"action":"replace original mesh" if node==original else "add temporary snow leaf","triangles":part.vertices.size()/3})
 var native_faces=preserved_native_faces(original_rows,raw_world_rows(original))
 if not native_faces.oriented_native_world_geometry_rgba_exact:failures.append("Native wet/protected face preservation")
 phase("replacement.after_root_and_snow_assignment",{"payload_checks":payload_checks,"wet_and_protected_native_faces":native_faces})
 var active=[original]+inserted;inspect_materials("replacement.active_materials",active,mat)
 if not failures.is_empty():push_error("Runtime replacement gates failed");quit(9);return
 var layer=CanvasLayer.new();layer.layer=100;root.add_child(layer)
 var panel=PanelContainer.new();panel.position=Vector2(14,112);layer.add_child(panel)
 var label=Label.new();label.add_theme_font_size_override("font_size",17);label.modulate=Color(1,.76,.4);panel.add_child(label)
 var controller=game.get_node("World/LakeReflection51");var depth=game.get_node("World/LakeDepth50");var captures=[]
 for reference in ["1128","1129"]:
  game.observe_reference(reference)
  var expected=Vector3(1150,10,-1000) if reference=="1128" else Vector3(1300,7,-950)
  if not game.camera.global_position.is_equal_approx(expected) or not is_equal_approx(game.camera.fov,64.0 if reference=="1128" else 66.0):failures.append("original camera "+reference)
  var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(.35);weather._process(0.0);RenderingServer.global_shader_parameter_set("world_time",.35)
  controller.set_effect_flags(true,true);depth.set_depth_enabled(true);controller.refresh_now()
  label.text="UNINTEGRATED CIRQUE54v2 | "+reference+" ORIGINAL CAMERA\nRoot mesh REPLACED. Old collision and scatter retained; shape diagnostic only."
  phase("capture."+reference+".before_settle")
  await frames(5);await physics_frame;controller.refresh_now();await frames(3);await RenderingServer.frame_post_draw
  inspect_materials("capture."+reference+".after_draw",active,mat)
  var im=root.get_texture().get_image();var dest=out+"/UNINTEGRATED-cirque54v2-reference-"+reference+".png";var err=im.save_png(dest)
  if err!=OK:failures.append("save:"+reference)
  captures.append({"reference":reference,"file":dest,"sha256":FileAccess.get_sha256(dest),"actual_png_size":[im.get_width(),im.get_height()],"logical_viewport":str(game.camera.get_viewport().get_visible_rect().size),"camera":str(game.camera.global_transform),"fov":game.camera.fov,"main_projection":str(game.camera.get_camera_projection()),"reflection":controller.get_diagnostic_state(),"error":err})
  phase("capture."+reference+".after_png",{"png_error":err})
 var scatter_same=initial_scatter==scatter_digest(game);var west_same=initial_west==west_digest(game);var collision_same=initial_collision==collision_digest(game);var others_same=initial_others==other_mesh_digest(game,original)
 var properties_same=original_properties==[original.transform,original.visible,original.layers,original.cast_shadow,original.material_override,original.get_surface_override_material(0),original.owner]
 var root_replaced=original.mesh.resource_path!=old_path and raw_world_rows(original).positions.size()/3==862 and model.get_child_count()==4
 var scene_same=FileAccess.get_sha256(SOURCE)==EXPECTED
 if not scatter_same or not west_same or not collision_same or not others_same or not properties_same or not root_replaced or not scene_same:failures.append("Replacement or preservation gate failed")
 phase("preservation.after_final_digests")
 var report={"baseline":SOURCE,"baseline_sha256":EXPECTED,"source_payload_sha256":FileAccess.get_sha256(PAYLOAD),"scope":"Temporary raw-native visual replacement of original cirque root ArrayMesh with862triangle remodeled body plus3temporary closed snow leaves;1554triangles total. Original432whole wet/cross-water and19protected dry faces are in the new body, not a second old root. No scene save or integration. All original collision/scatter remain intentionally unmatched to new visible upper geometry. Original1128/1129 cameras only.","visual_acceptance":false,"integrated":false,"old_cirque_leaves":leaves,"old_root_resource":old_path,"old_root_triangles":old_triangles,"original_raw_native_authority_exact":original_native_exact,"removed53_added_cirque_leaves":[],"preserved53_west_added_leaves":["ridge_shoulders","snow_cap","snow_gully","shore_rock_apron"],"root_mesh_actually_replaced":root_replaced,"original_root_other_properties_preserved":properties_same,"payload_checks":payload_checks,"wet_and_protected_native_faces":native_faces,"all_runtime_payload_raw_positions_native_encoded_rgba_exact":payload_checks.all(func(r):return r.raw_world_positions_and_native_encoded_rgba_exact),"scatter_unchanged":scatter_same,"all_collision_unchanged":collision_same,"saved53west_file_unchanged":scene_same,"all_west_meshes_collision_material_bindings_unchanged":west_same,"all_other_mesh_geometry_bindings_unchanged":others_same,"material_checks":material_checks,"material_checks_all_passed":material_checks.all(func(r):return r.passed),"parts":changed,"captures":captures,"failures":failures,"renderer":RenderingServer.get_video_adapter_name()}
 var f=FileAccess.open(out.get_base_dir()+"/diagnostic-report.json",FileAccess.WRITE)
 if f:f.store_string(JSON.stringify(report,"  "));f.flush();f.close()
 else:failures.append("report write")
 phase("preservation.report_saved_before_cleanup",{"report_sha256":FileAccess.get_sha256(out.get_base_dir()+"/diagnostic-report.json")})
 await frames(3);await RenderingServer.frame_post_draw
 phase("cleanup.before_temporary_snow_queue_free")
 for temporary in inserted:temporary.queue_free()
 await frames(3);await RenderingServer.frame_post_draw;inserted.clear();active.clear();original_properties.clear()
 phase("cleanup.before_queue_free")
 game.queue_free();layer.queue_free();await frames(8)
 phase("cleanup.after8frames");phase("quit.requested",{"failures":failures})
 if phase_log:phase_log.close()
 quit(0 if failures.is_empty() else 5)
