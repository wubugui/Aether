extends SceneTree
var camera: Camera3D
var reflected: Camera3D
var viewport: SubViewport
var water: ShaderMaterial
var world: Node3D
var cube: MeshInstance3D
var out := "/workspace/scratch/a29d03198654/reflection-test50/evidence"
func _initialize(): call_deferred("run")
func box(p:Vector3,size:Vector3,color:Color):
 var n=MeshInstance3D.new();var m=BoxMesh.new();m.size=size;n.mesh=m;n.position=p
 var mat=StandardMaterial3D.new();mat.albedo_color=color;n.material_override=mat;world.add_child(n);return n
func sync():
 reflected.fov=camera.fov;reflected.near=camera.near;reflected.far=camera.far
 var p=camera.global_position;p.y=-p.y
 var target=camera.global_position-camera.global_basis.z*10;target.y=-target.y
 reflected.global_position=p;reflected.look_at(target,Vector3.UP)
 water.set_shader_parameter("reflection_view",reflected.global_transform.affine_inverse())
 water.set_shader_parameter("reflection_projection",reflected.get_camera_projection())
func shot(name):
 sync()
 for i in range(10):await process_frame
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(out+"/"+name+".png")
 viewport.get_texture().get_image().save_png(out+"/"+name+"-reflection.png")
func run():
 if DisplayServer.get_name()=="headless":quit(2);return
 DirAccess.make_dir_recursive_absolute(out)
 world=Node3D.new();root.add_child(world)
 var env=WorldEnvironment.new();env.environment=Environment.new();env.environment.background_mode=Environment.BG_COLOR;env.environment.background_color=Color(.45,.65,.85);env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.environment.ambient_light_color=Color.WHITE;env.environment.ambient_light_energy=.8;world.add_child(env)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-45,-30,0);world.add_child(sun)
 cube=box(Vector3(-2,2,-5),Vector3(2,4,2),Color(.9,.15,.07));box(Vector3(3,1,-9),Vector3(2,2,2),Color(.05,.7,.2));box(Vector3(0,4,-16),Vector3(12,8,2),Color(.4,.35,.6))
 box(Vector3(5,5,-4),Vector3(2,2,2),Color(.05,.15,.95));box(Vector3(-4,-2,2),Vector3(3,2,3),Color(1,.85,0))
 camera=Camera3D.new();world.add_child(camera);camera.position=Vector3(0,4,10);camera.look_at(Vector3(0,1,-8));camera.current=true;camera.fov=65;camera.far=100
 viewport=SubViewport.new();viewport.size=Vector2i(800,600);viewport.world_3d=root.world_3d;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
 reflected=Camera3D.new();viewport.add_child(reflected);reflected.current=true;reflected.cull_mask=1
 var plane=MeshInstance3D.new();var mesh=PlaneMesh.new();mesh.size=Vector2(100,100);plane.mesh=mesh;plane.layers=2;world.add_child(plane)
 water=ShaderMaterial.new();water.shader=Shader.new();water.shader.code="""shader_type spatial;
render_mode unshaded,cull_disabled;
uniform sampler2D reflection_texture:filter_linear,repeat_disable;
uniform mat4 reflection_view;
uniform mat4 reflection_projection;
varying vec3 world_point;
void vertex(){world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){vec4 q=reflection_projection*reflection_view*vec4(world_point,1.);vec2 uv=q.xy/q.w*.5+.5;uv.y=1.-uv.y;ALBEDO=mix(texture(reflection_texture,uv).rgb,vec3(.04,.15,.22),.12);}
""";plane.material_override=water;water.set_shader_parameter("reflection_texture",viewport.get_texture())
 await shot("front")
 camera.position.x=3;camera.look_at(Vector3(0,1,-8));await shot("lateral")
 cube.position.x+=3;await shot("moving-object")
 print("SAME WORLD ",viewport.world_3d==root.world_3d)
 viewport.queue_free();world.queue_free()
 for i in range(8):await process_frame
 quit()
