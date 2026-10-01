extends SceneTree
const SOURCE="res://scenes/candidate53d-west/Game53dWest.tscn"
const PAYLOAD="/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v1/cirque54-payload.json"
const EXPECTED="6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18"
var failures=[]
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
 if FileAccess.get_sha256(SOURCE)!=EXPECTED:push_error("Frozen saved53west authority mismatch");quit(4);return
 root.size=Vector2i(1180,664)
 var packed=load(SOURCE)
 var game=packed.instantiate()
 packed=null
 root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
 await frames(20);await RenderingServer.frame_post_draw
 freeze(game)
 var original_scatter=scatter_digest(game)
 var original_west=west_digest(game)
 var asset=game.get_node("World/Mountains/massif_cirque_wall")
 var model=asset.get_node("Model")
 var original_model=asset.get_node("Model/massif_cirque_wall")
 var old_collision=asset.get_node("Collision/Shape").shape
 var old_collision_hash=var_to_bytes(old_collision.get_faces()).hex_encode().sha256_text()
 var mat=asset.get("surface_material")
 var data=JSON.parse_string(FileAccess.get_file_as_string(PAYLOAD))
 var changes=[]
 var inserted=[]
 for mountain in data.mountains:
  if mountain.name!="massif_cirque_wall":continue
  var inv=asset.global_transform.affine_inverse()
  for part in mountain.components:
   if part.name=="rock_body":continue # Retain the exact original saved native692triangle mesh.
   var mesh=MeshInstance3D.new();mesh.name=part.name
   var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
   for i in part.vertices.size():
    var c=part.colors[i];st.set_color(Color(c[0],c[1],c[2],c[3]));st.add_vertex(inv*v(part.vertices[i]))
   st.generate_normals();mesh.mesh=st.commit();mesh.material_override=mat;model.add_child(mesh)
   inserted.append(mesh)
   changes.append({"name":part.name,"triangles":part.vertices.size()/3,"material":mat.resource_path})
 var original_root_mesh=original_model.mesh
 var original_root_visible=original_model.visible
 var layer=CanvasLayer.new();layer.layer=100;root.add_child(layer)
 var panel=PanelContainer.new();panel.position=Vector2(14,112);layer.add_child(panel)
 var label=Label.new();label.add_theme_font_size_override("font_size",17);label.modulate=Color(1,.76,.4);panel.add_child(label)
 var controller=game.get_node("World/LakeReflection51")
 var depth=game.get_node("World/LakeDepth50")
 var captures=[]
 for reference in ["1128","1129"]:
  game.observe_reference(reference)
  var expected=Vector3(1150,10,-1000) if reference=="1128" else Vector3(1300,7,-950)
  if not game.camera.global_position.is_equal_approx(expected) or not is_equal_approx(game.camera.fov,64.0 if reference=="1128" else 66.0):failures.append("original camera "+reference)
  var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(.35);weather._process(0.0)
  RenderingServer.global_shader_parameter_set("world_time",.35)
  controller.set_effect_flags(true,true);depth.set_depth_enabled(true);controller.refresh_now()
  var pose=game.camera.global_transform
  for view in ["front","approach200m"]:
   game.camera.global_transform=pose
   if view=="approach200m":game.camera.global_position-=game.camera.global_basis.z*200.0
   label.text="UNINTEGRATED CIRQUE54 ONLY | "+reference+" "+view+"\nCollision and all scatter remain saved53west. Shape diagnostic only."
   await frames(5);await physics_frame;controller.refresh_now();await frames(3);await RenderingServer.frame_post_draw
   var im=root.get_texture().get_image();var dest=out+"/UNINTEGRATED-cirque54-reference-"+reference+"--"+view+".png";var err=im.save_png(dest)
   if err!=OK:failures.append("save:"+reference+"/"+view)
   var logical=game.camera.get_viewport().get_visible_rect().size
   var calibration={"upper_shoulder":[795,231,-1956],"low_saddle":[815,196,-1845],"gully_a_open_outlet":[906,62,-1720]}
   var anchors={}
   for key in calibration:
    var pixel=game.camera.unproject_position(v(calibration[key]));var norm=Vector2(pixel.x/logical.x,pixel.y/logical.y)
    anchors[key]={"world":calibration[key],"logical_pixel":[pixel.x,pixel.y],"normalized":[norm.x,norm.y],"physical_png_pixel":[norm.x*im.get_width(),norm.y*im.get_height()]}
   captures.append({"main_projection":str(game.camera.get_camera_projection()),"keep_aspect":game.camera.keep_aspect,"projected_authored_anchors":anchors,"reference":reference,"view":view,"file":dest,"actual_png_size":[im.get_width(),im.get_height()],"logical_viewport":[logical.x,logical.y],"camera":str(game.camera.global_transform),"fov":game.camera.fov,"reflection":controller.get_diagnostic_state(),"error":err})
   print("CIRQUE54_WORLD_DIAGNOSTIC ",dest," err=",err)
  game.camera.global_transform=pose
 var scatter_same=original_scatter==scatter_digest(game)
 var collision_same=old_collision_hash==var_to_bytes(asset.get_node("Collision/Shape").shape.get_faces()).hex_encode().sha256_text()
 var scene_same=FileAccess.get_sha256(SOURCE)==EXPECTED
 var west_same=original_west==west_digest(game)
 var root_same=original_model.mesh==original_root_mesh and original_model.visible==original_root_visible
 if not scatter_same or not collision_same or not scene_same or not west_same or not root_same:failures.append("diagnostic preservation")
 var report={"baseline":SOURCE,"baseline_sha256":EXPECTED,"source_payload_sha256":FileAccess.get_sha256(PAYLOAD),"scope":"Temporary addition of8cirque visual layers over the exact retained692triangle original root. Original1128/1129 and200m approaches, weather0.35, depth and reflection. No scene save. All collision and scatter remain saved53west, deliberately unintegrated.","visual_acceptance":false,"integrated":false,"scatter_unchanged":scatter_same,"collision_unchanged":collision_same,"saved53west_file_unchanged":scene_same,"all_west_meshes_collision_material_bindings_unchanged":west_same,"cirque_original_native_root_retained":root_same,"parts":changes,"captures":captures,"failures":failures,"renderer":RenderingServer.get_video_adapter_name()}
 var f=FileAccess.open(out.get_base_dir()+"/diagnostic-report.json",FileAccess.WRITE)
 if f:f.store_string(JSON.stringify(report,"  "));f.close()
 else:failures.append("report write")
 await frames(3);await RenderingServer.frame_post_draw
 game.queue_free();layer.queue_free();await frames(8)
 quit(0 if failures.is_empty() else 5)
