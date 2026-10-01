extends SceneTree
const BASE="res://scenes/candidate51b/Game51b.tscn"
const BASE_SHA="b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1"
const PROBES="/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/integration-west53/runtime-probes.json"
var game:Node3D
var output=""
var failures=[]
func _initialize():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--report-dir="):output=arg.trim_prefix("--report-dir=")
 call_deferred("run")
func frames(n):for i in range(n):await process_frame
func settle():await frames(3);await RenderingServer.frame_post_draw
func freeze(n):
 n.set_process(false);n.set_physics_process(false);n.set_process_input(false);n.set_process_unhandled_input(false);n.set_process_unhandled_key_input(false)
 if n is AnimationPlayer:n.pause()
 if n is Timer:n.paused=true
 for c in n.get_children():freeze(c)
func collisions()->Dictionary:
 var out={}
 for n in game.find_children("*","CollisionObject3D",true,false):out[str(game.get_path_to(n))]=[n.process_mode,n.disable_mode,n.can_process(),n.collision_layer,n.collision_mask,str(n.get_rid())]
 return out
func run():
 if DisplayServer.get_name()=="headless":quit(2);return
 if not output.is_absolute_path() or not DirAccess.dir_exists_absolute(output):quit(3);return
 if FileAccess.get_sha256(BASE)!=BASE_SHA:quit(4);return
 var default_sha=FileAccess.get_sha256("res://project.godot")
 var probes:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PROBES))
 var packed:PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed.instantiate();await settle();packed=null
 root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
 await frames(5);await RenderingServer.frame_post_draw
 var before=collisions();freeze(game);await physics_frame;await physics_frame
 var freeze_ok=before==collisions()
 if not freeze_ok:failures.append("Freeze changed actual collision modes/layers/RIDs")
 var rows=[];var max_ground_error=0.0;var index=0
 for row in probes.buildings:
  var start=Vector3(row.x,1500,row.z);var end=Vector3(row.x,-100,row.z)
  var hit=game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,end,4))
  if hit.is_empty():failures.append("No baseline support at index"+str(index));index+=1;continue
  var ground=game.get_node("World").ground_height(start);max_ground_error=maxf(max_ground_error,absf(ground-hit.position.y))
  rows.append({"index":index,"source_region":row.node,"x":row.x,"z":row.z,"old_partial_expected_y":row.expected_y,"full_scene_baseline_physics_y":hit.position.y,"full_scene_ground_height":ground,"old_expected_difference_m":hit.position.y-row.expected_y,"collider":str(game.get_path_to(hit.collider)),"ray_start":str(start),"ray_end":str(end),"mask":4})
  index+=1
 if rows.size()!=probes.buildings.size() or max_ground_error>=.03:failures.append("Baseline ray/ground query incomplete or inconsistent")
 if FileAccess.get_sha256(BASE)!=BASE_SHA or FileAccess.get_sha256("res://project.godot")!=default_sha:failures.append("Saved baseline/default changed")
 var report={"passed":failures.is_empty(),"baseline":BASE,"baseline_sha256":BASE_SHA,"probe_input":PROBES,"probe_input_sha256":FileAccess.get_sha256(PROBES),"scope":"Independent real-renderer whole saved51b physics world; exact same171building/buffer layer4rays as failed verifier. No six-tile geometry filter. No candidate loaded or scene saved.","rows":rows,"all_171_rays_complete":rows.size()==171,"freeze_preserves_physics":freeze_ok,"collision_objects":before.size(),"max_ray_ground_error_m":max_ground_error,"failures":failures,"renderer":RenderingServer.get_video_adapter_name()}
 var file=FileAccess.open(output+"/full-baseline-building-probes.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
 print("WEST53 FULL_BASELINE_BUILDING_PROBES ",report.passed," rows=",rows.size()," max_ground_error=",max_ground_error)
 await settle();game.queue_free();game=null;await frames(8);quit(0 if report.passed else 1)
