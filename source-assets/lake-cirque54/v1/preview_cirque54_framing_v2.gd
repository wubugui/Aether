extends SceneTree
const DIR="/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v1/"
const SAVED="res://scenes/candidate53d-west/Game53dWest.tscn"
const SHA="6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18"
func v(p):return Vector3(p[0],p[1],p[2])
func _initialize():call_deferred("run")
func run():
 if DisplayServer.get_name()=="headless":push_error("Actual rendering required");quit(2);return
 if FileAccess.get_sha256(SAVED)!=SHA:push_error("Frozen saved53west SHA differs");quit(3);return
 var out=OS.get_environment("CIRQUE54_PREVIEW_OUT")
 if out.is_empty():push_error("Unique CIRQUE54_PREVIEW_OUT required");quit(4);return
 root.size=Vector2i(1280,960)
 DirAccess.make_dir_recursive_absolute(out)
 var packed=load(SAVED)
 var saved=packed.instantiate()
 var mat=saved.get_node("World/Mountains/massif_cirque_wall").get("surface_material").duplicate(true)
 for i in range(3):await process_frame
 await RenderingServer.frame_post_draw
 saved.free();saved=null;packed=null
 for i in range(8):await process_frame
 var stage=Node3D.new();root.add_child(stage)
 var env=WorldEnvironment.new();var e=Environment.new()
 e.background_mode=Environment.BG_COLOR;e.background_color=Color(.14,.18,.22)
 e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(.64,.73,.85);e.ambient_light_energy=.65
 e.tonemap_mode=Environment.TONE_MAPPER_FILMIC;env.environment=e;stage.add_child(env)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-47,-37,0);sun.light_color=Color(1,.9,.79);sun.light_energy=1.3;sun.shadow_enabled=true;stage.add_child(sun)
 var cam=Camera3D.new();cam.projection=Camera3D.PROJECTION_ORTHOGONAL;cam.keep_aspect=Camera3D.KEEP_HEIGHT;cam.far=5000;stage.add_child(cam);cam.make_current()
 var data=JSON.parse_string(FileAccess.get_file_as_string(DIR+"cirque54-payload.json"))
 if data.baseline_sha256!=SHA or data.mountains.size()!=1:push_error("Unexpected source scope");quit(5);return
 var points=[];var lo=Vector3(INF,INF,INF);var hi=Vector3(-INF,-INF,-INF)
 for piece in data.mountains[0].components:
  var mesh=MeshInstance3D.new();mesh.name=piece.name;var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
  for i in piece.vertices.size():
   var c=piece.colors[i];var p=v(piece.vertices[i]);st.set_color(Color(c[0],c[1],c[2],c[3]));st.add_vertex(p);points.append(p);lo=lo.min(p);hi=hi.max(p)
  st.generate_normals();mesh.mesh=st.commit();mesh.material_override=mat;stage.add_child(mesh)
 var center=(lo+hi)*.5
 var views={"front_lake_south":Vector3(0,.45,1),"lake_facing_east":Vector3(1,.35,0),"back_north":Vector3(0,.45,-1),"outer_west":Vector3(-1,.35,0),"top":Vector3(.1,1,.001)}
 for i in range(4):await process_frame
 var actual=root.get_visible_rect().size;var aspect=actual.x/actual.y;var required_size=700.0
 for label in views:
  cam.position=center+views[label].normalized()*1300;cam.look_at(center,Vector3.UP)
  for p in points:
   var rel=cam.global_transform.affine_inverse()*p
   required_size=max(required_size,2*abs(rel.y)/.82,2*abs(rel.x)/(.82*aspect))
 cam.size=ceil(required_size)
 var framing=[];var failed=false
 for label in views:
  cam.position=center+views[label].normalized()*1300;cam.look_at(center,Vector3.UP)
  for i in range(4):await process_frame
  await RenderingServer.frame_post_draw
  var minp=Vector2(INF,INF);var maxp=Vector2(-INF,-INF)
  for p in points:
   var q=cam.unproject_position(p);minp=minp.min(q);maxp=maxp.max(q)
  var image=root.get_texture().get_image();var dimensions=Vector2(image.get_width(),image.get_height())
  var projection_dimensions=cam.get_viewport().get_visible_rect().size
  var margins=[minp.x/projection_dimensions.x,minp.y/projection_dimensions.y,1-maxp.x/projection_dimensions.x,1-maxp.y/projection_dimensions.y]
  var path=out+"/SOURCE_ONLY-cirque54--"+label+".png";var error=image.save_png(path)
  var frame_ok=true
  for margin in margins:frame_ok=frame_ok and margin>=.07
  if error!=OK or not frame_ok:failed=true
  framing.append({"view":label,"image":path,"png_error":error,"actual_image_dimensions":[image.get_width(),image.get_height()],"actual_viewport_dimensions":[projection_dimensions.x,projection_dimensions.y],"logical_projection_min_px":[minp.x,minp.y],"logical_projection_max_px":[maxp.x,maxp.y],"all_vertices_frame_margins_left_top_right_bottom":margins,"framing_pass":frame_ok,"orthographic_height":cam.size,"camera_position":[cam.position.x,cam.position.y,cam.position.z]})
  print("CIRQUE54_SOURCE_PREVIEW ",label," png_error=",error," margins=",margins," size=",dimensions)
 var report={"baseline_sha256":SHA,"scope":"Independent cirque source only; saved world never added to live tree or modified. Original source root is shown including underwater part. No scatter reconciliation or visual acceptance asserted.","same_light_as_west53_source":true,"renderer":RenderingServer.get_video_adapter_name(),"bounds":[[lo.x,lo.y,lo.z],[hi.x,hi.y,hi.z]],"views":framing,"pass":not failed}
 var f=FileAccess.open(out.get_base_dir()+"/preview-framing.json",FileAccess.WRITE)
 if f:f.store_string(JSON.stringify(report,"  "));f.close()
 else:failed=true
 stage.queue_free();mat=null
 for i in range(8):await process_frame
 quit(6 if failed else 0)
