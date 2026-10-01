extends SceneTree
const SOURCE="res://scenes/candidate53d-west/Game53dWest.tscn"
const PAYLOAD="/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v1/cirque54-payload.json"
const EXPECTED="6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18"
var failures=[]
var phase_log:FileAccess
var material_checks=[]
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
func _initialize():call_deferred("run")
func run():
 if DisplayServer.get_name()=="headless":quit(2);return
 var out=OS.get_environment("CIRQUE54_WORLD_OUT")
 if out.is_empty():quit(3);return
 phase_log=FileAccess.open(out.get_base_dir()+"/phases.jsonl",FileAccess.WRITE)
 phase("startup.before_load")
 if FileAccess.get_sha256(SOURCE)!=EXPECTED:push_error("Frozen saved53west authority mismatch");quit(4);return
 root.size=Vector2i(1180,664)
 var packed=load(SOURCE)
 phase("startup.before_instantiate")
 var game=packed.instantiate()
 phase("startup.after_instantiate")
 packed=null
 phase("startup.before_add_to_tree")
 root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
 phase("startup.before20frames")
 await frames(20);await RenderingServer.frame_post_draw
 phase("startup.after20frames_and_draw")
 freeze(game)
 phase("baseline.before_digests")
 var original_scatter=scatter_digest(game)
 var original_west=west_digest(game)
 phase("baseline.after_digests")
 var asset=game.get_node("World/Mountains/massif_cirque_wall")
 var model=asset.get_node("Model")
 var original_model=asset.get_node("Model/massif_cirque_wall")
 var old_collision=asset.get_node("Collision/Shape").shape
 var old_collision_hash=var_to_bytes(old_collision.get_faces()).hex_encode().sha256_text()
 var mat=asset.get("surface_material")
 inspect_materials("baseline.cirque_original_binding",[original_model],mat)
 var data=JSON.parse_string(FileAccess.get_file_as_string(PAYLOAD))
 if data.baseline_sha256!=EXPECTED or data.mountains.size()!=1:failures.append("payload scope/baseline")
 phase("additive_meshes.before_creation")
 var changes=[]
 var inserted=[]
 for mountain in data.mountains:
  if mountain.name!="massif_cirque_wall":continue
  var inv=asset.global_transform.affine_inverse()
  for part in mountain.components:
   if part.name=="rock_body":continue # Retain the exact original saved native692triangle mesh.
   phase("additive_mesh."+part.name+".before_creation")
   var mesh=MeshInstance3D.new();mesh.name=part.name
   var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
   for i in part.vertices.size():
    var c=part.colors[i];st.set_color(Color(c[0],c[1],c[2],c[3]));st.add_vertex(inv*v(part.vertices[i]))
   st.generate_normals();mesh.mesh=st.commit();mesh.material_override=mat;model.add_child(mesh)
   inserted.append(mesh)
   inspect_materials("additive_mesh."+part.name+".after_binding",[mesh],mat)
   changes.append({"name":part.name,"triangles":part.vertices.size()/3,"material":mat.resource_path})
 phase("additive_meshes.after_creation")
 var original_root_mesh=original_model.mesh
 var original_root_visible=original_model.visible
 var layer=CanvasLayer.new();layer.layer=100;root.add_child(layer)
 var panel=PanelContainer.new();panel.position=Vector2(14,112);layer.add_child(panel)
 var label=Label.new();label.add_theme_font_size_override("font_size",17);label.modulate=Color(1,.76,.4);panel.add_child(label)
 var controller=game.get_node("World/LakeReflection51")
 var depth=game.get_node("World/LakeDepth50")
 var captures=[]
 phase("captures.before_reference_loop")
 for reference in ["1128"]:
  phase("reference."+reference+".before_observe")
  game.observe_reference(reference)
  var expected=Vector3(1150,10,-1000) if reference=="1128" else Vector3(1300,7,-950)
  if not game.camera.global_position.is_equal_approx(expected) or not is_equal_approx(game.camera.fov,64.0 if reference=="1128" else 66.0):failures.append("original camera "+reference)
  var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(.35);weather._process(0.0)
  RenderingServer.global_shader_parameter_set("world_time",.35)
  controller.set_effect_flags(true,true);depth.set_depth_enabled(true);controller.refresh_now()
  var pose=game.camera.global_transform
  for view in ["front"]:
   game.camera.global_transform=pose
   if view=="approach200m":game.camera.global_position-=game.camera.global_basis.z*200.0
   phase("capture."+reference+"."+view+".before_settle")
   label.text="UNINTEGRATED CIRQUE54 ONLY | "+reference+" "+view+"\nCollision and all scatter remain saved53west. Shape diagnostic only."
   await frames(5);await physics_frame;controller.refresh_now();await frames(3);await RenderingServer.frame_post_draw
   inspect_materials("capture."+reference+"."+view+".after_draw",inserted,mat)
   var im=root.get_texture().get_image();var dest=out+"/UNINTEGRATED-cirque54-reference-"+reference+"--"+view+".png";var err=im.save_png(dest)
   if err!=OK:failures.append("save:"+reference+"/"+view)
   phase("capture."+reference+"."+view+".after_png",{"png_error":err})
   var logical=game.camera.get_viewport().get_visible_rect().size
   var calibration={"upper_shoulder":[795,231,-1956],"low_saddle":[815,196,-1845],"gully_a_open_outlet":[906,62,-1720]}
   var anchors={}
   for key in calibration:
    var pixel=game.camera.unproject_position(v(calibration[key]));var norm=Vector2(pixel.x/logical.x,pixel.y/logical.y)
    anchors[key]={"world":calibration[key],"logical_pixel":[pixel.x,pixel.y],"normalized":[norm.x,norm.y],"physical_png_pixel":[norm.x*im.get_width(),norm.y*im.get_height()]}
   captures.append({"main_projection":str(game.camera.get_camera_projection()),"keep_aspect":game.camera.keep_aspect,"projected_authored_anchors":anchors,"reference":reference,"view":view,"file":dest,"actual_png_size":[im.get_width(),im.get_height()],"logical_viewport":[logical.x,logical.y],"camera":str(game.camera.global_transform),"fov":game.camera.fov,"reflection":controller.get_diagnostic_state(),"error":err})
   print("CIRQUE54_WORLD_DIAGNOSTIC ",dest," err=",err)
  game.camera.global_transform=pose
 phase("preservation.before_final_digests")
 var scatter_same=original_scatter==scatter_digest(game)
 var collision_same=old_collision_hash==var_to_bytes(asset.get_node("Collision/Shape").shape.get_faces()).hex_encode().sha256_text()
 var scene_same=FileAccess.get_sha256(SOURCE)==EXPECTED
 var west_same=original_west==west_digest(game)
 var root_same=original_model.mesh==original_root_mesh and original_model.visible==original_root_visible
 if not scatter_same or not collision_same or not scene_same or not west_same or not root_same:failures.append("diagnostic preservation")
 phase("preservation.after_final_digests")
 inspect_materials("cleanup.before_resource_release",inserted,mat)
 var report={"material_checks":material_checks,"material_checks_all_passed":material_checks.all(func(r):return r.passed),"baseline":SOURCE,"baseline_sha256":EXPECTED,"source_payload_sha256":FileAccess.get_sha256(PAYLOAD),"scope":"Temporary addition of8cirque visual layers over the exact retained692triangle original root. One1128front phase probe only, weather0.35, depth and reflection. Source v1 shape is already visually rejected; no repeated4image shape review. No scene save. All collision and scatter remain saved53west, deliberately unintegrated.","visual_acceptance":false,"integrated":false,"scatter_unchanged":scatter_same,"collision_unchanged":collision_same,"saved53west_file_unchanged":scene_same,"all_west_meshes_collision_material_bindings_unchanged":west_same,"cirque_original_native_root_retained":root_same,"parts":changes,"captures":captures,"failures":failures,"renderer":RenderingServer.get_video_adapter_name()}
 var f=FileAccess.open(out.get_base_dir()+"/diagnostic-report.json",FileAccess.WRITE)
 if f:f.store_string(JSON.stringify(report,"  "));f.close()
 else:failures.append("report write")
 phase("cleanup.before3frames_and_draw")
 await frames(3);await RenderingServer.frame_post_draw
 phase("cleanup.before_queue_free")
 game.queue_free();layer.queue_free();await frames(8)
 phase("cleanup.after8frames")
 phase("quit.requested",{"failures":failures})
 if phase_log:phase_log.close()
 quit(0 if failures.is_empty() else 5)
