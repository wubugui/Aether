extends SceneTree
## Compile-only real-renderer diagnostic. Not a game-scene or visual acceptance.
const ROOT_PATH := "/workspace/scratch/a29d03198654/Aether/"
var output := ""
var rows := []
func _initialize():call_deferred("run")
func run():
 if DisplayServer.get_name()=="headless":push_error("Real renderer required");quit(2);return
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
 if output.is_empty() or DirAccess.dir_exists_absolute(output):push_error("New output directory required");quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 var manifest=JSON.parse_string(FileAccess.get_file_as_string(ROOT_PATH+"source-assets/reflection51/injection-report.json"))
 var scene=Node3D.new();root.add_child(scene)
 var environment=WorldEnvironment.new();environment.environment=Environment.new();environment.environment.background_mode=Environment.BG_COLOR;environment.environment.background_color=Color(.14,.18,.25);environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;environment.environment.ambient_light_color=Color.WHITE;environment.environment.ambient_light_energy=.8;scene.add_child(environment)
 var light=DirectionalLight3D.new();light.rotation_degrees=Vector3(-55,-30,0);scene.add_child(light)
 var camera=Camera3D.new();scene.add_child(camera);camera.position=Vector3(0,5,20);camera.look_at(Vector3(0,1,-4));camera.current=true;camera.cull_mask=1;camera.far=100
 RenderingServer.global_shader_parameter_set("world_time",0.35)
 var shaders=[]
 var originals=[]
 var materials=[]
 for i in range(manifest.sources.size()):
  var entry=manifest.sources[i];var path=ROOT_PATH+entry.file
  var shader=Shader.new();shader.code=FileAccess.get_file_as_string(path);shaders.append(shader)
  var original=Shader.new();original.code=FileAccess.get_file_as_string(ROOT_PATH+"source-assets/reflection51/original-shaders/"+str(entry.source_sha256)+".gdshader");originals.append(original)
  var material=ShaderMaterial.new();material.shader=original;materials.append(material)
  var mesh=MeshInstance3D.new();var box=BoxMesh.new();box.size=Vector3(1.5,2,1.5);mesh.mesh=box;mesh.material_override=material;mesh.position=Vector3((i%4)*3-4.5,1.0 if i%2==0 else -1.0,-floori(float(i)/4)*4);scene.add_child(mesh)
  rows.append({"file":entry.file,"source_sha256":entry.source_sha256,"injected_sha256":FileAccess.get_sha256(path),"expected_injected_sha256":entry.output_sha256})
 for i in range(16):await process_frame
 await RenderingServer.frame_post_draw
 var original_image=root.get_texture().get_image();original_image.convert(Image.FORMAT_RGBA8);original_image.save_png(output+"/original-main-diagnostic.png")
 for i in range(materials.size()):materials[i].shader=shaders[i]
 for i in range(8):await process_frame
 await RenderingServer.frame_post_draw
 var passed=true
 for i in range(shaders.size()):
  var names=[]
  for uniform in shaders[i].get_shader_uniform_list():names.append(str(uniform.name))
  var valid=names.has("lake51_reflection_clip_enabled") and names.has("lake51_reflection_plane_y") and rows[i].injected_sha256==rows[i].expected_injected_sha256
  rows[i].uniforms=names;rows[i].compiled_uniforms_present=valid;passed=passed and valid
 var injected_image=root.get_texture().get_image();injected_image.convert(Image.FORMAT_RGBA8);injected_image.save_png(output+"/normal-marker-off-diagnostic.png")
 var main_equal=original_image.get_data()==injected_image.get_data()
 passed=passed and main_equal
 camera.cull_mask=1|524288
 for i in range(8):await process_frame
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(output+"/reflection-marker-on-diagnostic.png")
 var f=FileAccess.open(output+"/report.json",FileAccess.WRITE);f.store_string(JSON.stringify({"source_count":rows.size(),"primitive_main_rgba_exact":main_equal,"source_checks_passed":passed,"sources":rows,"renderer":RenderingServer.get_video_adapter_name(),"scope":"Compile/resource-binding diagnostic only; primitive boxes do not validate native material parameters, all runtime dynamic geometry, or reference fidelity. Confirm stderr separately.","visual_acceptance":false,"hardware_gpu_acceptance":false},"  "));f.close()
 scene.queue_free()
 for i in range(8):await process_frame
 print("REFLECTION51 SOURCE COMPILE CHECK ",passed)
 quit(0 if passed else 1)
