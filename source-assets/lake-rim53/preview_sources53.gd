extends SceneTree
const DIR="/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/"
func v(p):return Vector3(p[0],p[1],p[2])
func _initialize():call_deferred("run")
func run():
 if DisplayServer.get_name()=="headless":quit(2);return
 root.size=Vector2i(1280,960)
 var saved=load("res://scenes/candidate51b/Game51b.tscn").instantiate()
 var source_material=saved.get_node("World/Mountains/massif_west_spur").get("surface_material")
 var mat=source_material.duplicate(true)
 for i in range(3):await process_frame
 await RenderingServer.frame_post_draw
 saved.free()
 for i in range(8):await process_frame
 var stage=Node3D.new();root.add_child(stage)
 var env=WorldEnvironment.new();var e=Environment.new()
 e.background_mode=Environment.BG_COLOR;e.background_color=Color(0.14,0.18,0.22)
 e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;e.ambient_light_color=Color(0.64,0.73,0.85);e.ambient_light_energy=0.65
 e.tonemap_mode=Environment.TONE_MAPPER_FILMIC
 env.environment=e;stage.add_child(env)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-47,-37,0);sun.light_color=Color(1,0.9,0.79);sun.light_energy=1.3;sun.shadow_enabled=true;stage.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=940;camera.far=5000;stage.add_child(camera);camera.make_current()
 var data=JSON.parse_string(FileAccess.get_file_as_string(DIR+"rim53-payload.json"))
 var out=OS.get_environment("RIM53_PREVIEW_OUT")
 if out.is_empty():push_error("RIM53_PREVIEW_OUT required for immutable run output");quit(3);return
 DirAccess.make_dir_recursive_absolute(out)
 var failed=false
 var names=["massif_west_spur"]
 var args=OS.get_cmdline_user_args()
 if "--all" in args:names=["massif_west_spur","massif_cirque_wall","massif_east_foothill","massif_frost_crown"]
 for mountain in data.mountains:
  if not mountain.name in names:continue
  var body=Node3D.new();stage.add_child(body)
  for piece in mountain.components:
   var mesh=MeshInstance3D.new();mesh.name=piece.name
   var st=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
   for i in piece.vertices.size():
    var c=piece.colors[i];st.set_color(Color(c[0],c[1],c[2],c[3]));st.add_vertex(v(piece.vertices[i]))
   st.generate_normals();mesh.mesh=st.commit();mesh.material_override=mat;body.add_child(mesh)
  var center=Vector3(440,125,-1850);camera.size=940
  if mountain.name=="massif_cirque_wall":center=Vector3(800,90,-1790);camera.size=910
  if mountain.name=="massif_east_foothill":center=Vector3(1660,100,-1820);camera.size=1270
  if mountain.name=="massif_frost_crown":center=Vector3(1235,180,-2900);camera.size=1280
  var views={"front_lake_south":Vector3(0,0.45,1),"lake_facing_east":Vector3(1,0.35,0),"back_north":Vector3(0,0.45,-1),"outer_west":Vector3(-1,0.35,0),"top":Vector3(0.1,1,0.001)}
  for label in views:
   camera.position=center+views[label].normalized()*1300;camera.look_at(center,Vector3.UP)
   for frame in range(4):await process_frame
   await RenderingServer.frame_post_draw
   var path=out+"/"+mountain.name+"--"+label+".png"
   var err=root.get_texture().get_image().save_png(path)
   if err!=OK:failed=true
   print("RIM53_SOURCE_PREVIEW ",path," err=",err)
  body.queue_free();await process_frame
 stage.queue_free()
 for i in range(8):await process_frame
 quit(4 if failed else 0)
