extends SceneTree
## Runtime-only overscan A/B/A diagnostic, not full preservation or acceptance.
var out=""
var game:Node3D
var shots=[]
func _initialize():call_deferred("run")
func frames(n:int):
 for i in range(n):await process_frame
func freeze(n:Node):
 n.set_process(false);n.set_physics_process(false);n.set_process_input(false);n.set_process_unhandled_input(false)
 if n is AnimationPlayer:n.pause()
 if n is Timer:n.paused=true
 for c in n.get_children():freeze(c)
func capture(label:String):
 await frames(8);await RenderingServer.frame_post_draw
 var path=out+"/"+label+".png";root.get_texture().get_image().save_png(path)
 shots.append({"name":label,"sha256":FileAccess.get_sha256(path),"camera":str(game.camera.global_transform)})
func run():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-dir="):out=arg.trim_prefix("--output-dir=")
 if DisplayServer.get_name()=="headless" or out.is_empty() or DirAccess.dir_exists_absolute(out):quit(2);return
 DirAccess.make_dir_recursive_absolute(out);root.size=Vector2i(1180,664)
 var path="res://scenes/candidate51/Game51.tscn";var sha=FileAccess.get_sha256(path)
 game=load(path).instantiate();await frames(3);await RenderingServer.frame_post_draw;root.add_child(game);game.sound_enabled=false;game.test_frozen=true;await frames(20);await RenderingServer.frame_post_draw
 freeze(game)
 var control=game.get_node("World/LakeReflection51")
 var diagnostics=[]
 for reference in ["1128","1129"]:
  game.observe_reference(reference);game.get_node("Weather42b").seek_time(0.0);game.get_node("Weather42b").seek_time(.35);RenderingServer.global_shader_parameter_set("world_time",.35)
  control.set_effect_flags(true,true);await capture(reference+"-A51-original-frustum")
  var original_fov:float=control.reflection_camera.fov
  control.reflection_camera.fov=rad_to_deg(2.0*atan(tan(deg_to_rad(original_fov)*.5)*1.08))
  control.water.set_shader_parameter("lake51_reflection_projection",control.reflection_camera.get_camera_projection())
  await capture(reference+"-B-overscan108")
  control.viewport.get_texture().get_image().save_png(out+"/"+reference+"-overscan-viewport.png")
  diagnostics.append(control.get_diagnostic_state())
  control.set_effect_flags(true,true);await capture(reference+"-A51-restored-frustum")
 var f=FileAccess.open(out+"/report.json",FileAccess.WRITE);f.store_string(JSON.stringify({"candidate_sha256":sha,"scene_unchanged":FileAccess.get_sha256(path)==sha,"shots":shots,"controller_states":diagnostics,"renderer":RenderingServer.get_video_adapter_name(),"scope":"Runtime optical overscan108 only, restores original51 projection. No source or scene save. Does not replace full scene/material/motion verification.","visual_acceptance":false,"hardware_gpu_acceptance":false},"  "));f.close()
 game.queue_free();await frames(8);print("REFLECTION51 OVERSCAN DIAGNOSTIC CAPTURED");quit()
