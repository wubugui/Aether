extends SceneTree
const SOURCE="res://scenes/candidate51b/Game51b.tscn"
const PAYLOAD="/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/revision-d/rim53-payload.json"
const EXPECTED="b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1"
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
   var row=[str(n.name)]
   for i in n.multimesh.instance_count:row.append(str(n.multimesh.get_instance_transform(i)))
   state.append(row)
 return JSON.stringify(state).sha256_text()
func _initialize():call_deferred("run")
func run():
 if DisplayServer.get_name()=="headless":quit(2);return
 var out=OS.get_environment("RIM53_PREVIEW_OUT")
 if out.is_empty():quit(3);return
 if FileAccess.get_sha256(SOURCE)!=EXPECTED:push_error("51b authority mismatch");quit(4);return
 root.size=Vector2i(1180,664)
 var game=load(SOURCE).instantiate()
 root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
 await frames(20);await RenderingServer.frame_post_draw
 freeze(game)
 var original_scatter=scatter_digest(game)
 var asset=game.get_node("World/Mountains/massif_west_spur")
 var model=asset.get_node("Model")
 var original_model=asset.get_node("Model/massif_west_spur")
 var old_collision=asset.get_node("Collision/Shape").shape
 var old_collision_hash=var_to_bytes(old_collision.get_faces()).hex_encode().sha256_text()
 var mat=asset.get("surface_material")
 var data=JSON.parse_string(FileAccess.get_file_as_string(PAYLOAD))
 var changes=[]
 var inserted=[]
 for mountain in data.mountains:
  if mountain.name!="massif_west_spur":continue
  var inv=asset.global_transform.affine_inverse()
  for part in mountain.components:
   var mesh=MeshInstance3D.new();mesh.name=part.name
   var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
   for i in part.vertices.size():
    var c=part.colors[i];st.set_color(Color(c[0],c[1],c[2],c[3]));st.add_vertex(inv*v(part.vertices[i]))
   st.generate_normals();mesh.mesh=st.commit();mesh.material_override=mat;model.add_child(mesh)
   inserted.append(mesh)
   changes.append({"name":part.name,"triangles":part.vertices.size()/3,"material":mat.resource_path})
 original_model.visible=false
 var layer=CanvasLayer.new();layer.layer=100;root.add_child(layer)
 var panel=PanelContainer.new();panel.position=Vector2(14,112);layer.add_child(panel)
 var label=Label.new();label.add_theme_font_size_override("font_size",17);label.modulate=Color(1,.76,.4);panel.add_child(label)
 var controller=game.get_node("World/LakeReflection51")
 var depth=game.get_node("World/LakeDepth50")
 var captures=[]
 for reference in ["1128","1129"]:
  game.observe_reference(reference)
  var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(.35);weather._process(0.0)
  RenderingServer.global_shader_parameter_set("world_time",.35)
  controller.set_effect_flags(true,true);depth.set_depth_enabled(true);controller.refresh_now()
  label.text="UNINTEGRATED WEST53d ONLY | REFERENCE "+reference+"\nCollision and scatter remain51b. Shape diagnostic only."
  await frames(5);await physics_frame;controller.refresh_now();await frames(3);await RenderingServer.frame_post_draw
  var im=root.get_texture().get_image();var dest=out+"/UNINTEGRATED-west53d-reference-"+reference+".png";var err=im.save_png(dest)
  if err!=OK:failures.append("save:"+reference)
  var upper_inside={"pixel_y":INF}
  var upper_any={"pixel_y":INF}
  for mesh in inserted:
   for local in mesh.mesh.get_faces():
    var point=mesh.global_transform*local
    if game.camera.is_position_behind(point):continue
    var pixel=game.camera.unproject_position(point)
    if pixel.y<upper_any.pixel_y:upper_any={"world":str(point),"pixel":[pixel.x,pixel.y],"pixel_y":pixel.y,"component":str(mesh.name)}
    if pixel.x>=0 and pixel.x<im.get_width() and pixel.y<upper_inside.pixel_y:upper_inside={"world":str(point),"pixel":[pixel.x,pixel.y],"pixel_y":pixel.y,"component":str(mesh.name)}
  var calibration={"main_crest":[245,323.5,-1880],"north_crest":[222,283,-2045]}
  var anchors={}
  for key in calibration:
   var pixel=game.camera.unproject_position(v(calibration[key]));anchors[key]={"world":calibration[key],"pixel":[pixel.x,pixel.y],"normalized":[pixel.x/im.get_width(),pixel.y/im.get_height()]}
  captures.append({"main_projection":str(game.camera.get_camera_projection()),"keep_aspect":game.camera.keep_aspect,"highest_projected_any":upper_any,"highest_projected_inside":upper_inside,"projected_authored_anchors":anchors,"reference":reference,"file":dest,"size":[im.get_width(),im.get_height()],"camera":str(game.camera.global_transform),"fov":game.camera.fov,"reflection":controller.get_diagnostic_state(),"error":err})
  print("RIM53D_WORLD_DIAGNOSTIC ",dest," err=",err)
 var scatter_same=original_scatter==scatter_digest(game)
 var collision_same=old_collision_hash==var_to_bytes(asset.get_node("Collision/Shape").shape.get_faces()).hex_encode().sha256_text()
 var scene_same=FileAccess.get_sha256(SOURCE)==EXPECTED
 if not scatter_same or not collision_same or not scene_same:failures.append("diagnostic preservation")
 var report={"baseline":SOURCE,"baseline_sha256":EXPECTED,"source_payload_sha256":FileAccess.get_sha256(PAYLOAD),"scope":"Temporary visual mesh replacement of west only. Original fixed cameras, weather0.35, depth and live reflection. No scene save. Original collision and scatter remain deliberately unintegrated.","visual_acceptance":false,"integrated":false,"scatter_unchanged":scatter_same,"collision_unchanged":collision_same,"saved51b_unchanged":scene_same,"parts":changes,"captures":captures,"failures":failures,"renderer":RenderingServer.get_video_adapter_name()}
 var f=FileAccess.open(out+"/diagnostic-report.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close()
 await frames(3);await RenderingServer.frame_post_draw
 game.queue_free();layer.queue_free();await frames(8)
 quit(0 if failures.is_empty() else 5)
