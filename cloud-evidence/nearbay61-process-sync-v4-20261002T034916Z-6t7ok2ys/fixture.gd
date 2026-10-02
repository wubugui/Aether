extends SceneTree
const Audit=preload("../visible_geometry61.gd")

class Follower:
 extends Node
 var ship: Node3D
 var rain: MeshInstance3D
 var updates:=0
 func _process(_delta: float) -> void:
  rain.global_position=ship.global_position.snapped(Vector3(64,32,64))
  updates+=1

class LateWitness:
 extends Node
 signal processed
 func _process(_delta: float) -> void:
  processed.emit()

var checks:=[]
var failed:=false
var output: String

func record(name: String, ok: bool, details: Variant=null) -> void:
 checks.append({"name":name,"passed":ok,"details":details})
 if not ok: failed=true

func _initialize() -> void:
 output=OS.get_cmdline_user_args()[0]
 call_deferred("run")

func evidence_complete(detail: Dictionary, path: String, id: int) -> bool:
 if detail.get("path")!=path or detail.get("instance_id")!=id or not detail.has("before") or not detail.has("current"): return false
 for side in ["before","current"]:
  for key in ["path","instance_id","own_visible","tree_visible","effective_visible","layers","camera_cull_mask","transform_hex","position","bounds_position","bounds_size","bounds_intersects_domain","effective_query_candidate"]:
   if not detail[side].has(key): return false
 return true

func new_guard(node: MeshInstance3D, camera: Camera3D):
 var guard=Audit.new()
 guard.owner_game={"camera":camera}
 guard.domain=AABB(Vector3(-200,-100,-200),Vector3(400,200,400))
 var bounds: AABB=guard.world_bounds(node.get_aabb(),node.global_transform).grow(.002)
 var visible: bool=node.is_visible_in_tree() and (node.layers & camera.cull_mask)!=0
 guard.watches.append(guard.watch_entry(node,visible,0.0,bounds))
 return guard

func run() -> void:
 var scene:=Node3D.new();scene.name="ProcessSyncOnly";root.add_child(scene)
 var ship:=Node3D.new();ship.name="ShipFixture";scene.add_child(ship)
 var rain:=MeshInstance3D.new();rain.name="HiddenFollower";rain.mesh=BoxMesh.new();rain.visible=false;scene.add_child(rain)
 var camera:=Camera3D.new();scene.add_child(camera)
 var follower:=Follower.new();follower.ship=ship;follower.rain=rain;scene.add_child(follower)
 var witness:=LateWitness.new();witness.process_priority=100000;root.add_child(witness)
 await witness.processed
 ship.position=Vector3(101,28,75)
 var expected:=Vector3(128,32,64)
 var old_position:=rain.global_position
 var previous_updates:=follower.updates
 await process_frame
 var begin: Dictionary={"phase":"process_frame_signal_start","process_frame":Engine.get_process_frames(),"follower_updates":follower.updates,"rain_position":[rain.global_position.x,rain.global_position.y,rain.global_position.z]}
 record("process_signal_precedes_native_follower_update",follower.updates==previous_updates and rain.global_position==old_position,begin)
 var premature=new_guard(rain,camera)
 await witness.processed
 var end: Dictionary={"phase":"after_late_witness","process_frame":Engine.get_process_frames(),"follower_updates":follower.updates,"rain_position":[rain.global_position.x,rain.global_position.y,rain.global_position.z]}
 record("late_witness_observes_native_follower_update",follower.updates==previous_updates+1 and rain.global_position==expected,end)
 record("premature_hidden_inventory_still_fails_after_follow",not premature.unchanged(true),premature.failures)
 var detail: Dictionary=premature.failures[-1].details
 record("hidden_follow_failure_has_complete_before_current",evidence_complete(detail,str(rain.get_path()),rain.get_instance_id()) and not detail.before.tree_visible and not detail.current.tree_visible and detail.before.position!=detail.current.position,detail)
 var settled=new_guard(rain,camera)
 await witness.processed
 record("post_process_baseline_remains_exact_for_stationary_ship",settled.unchanged(true) and rain.global_position==expected)
 camera.rotation.y=1.0
 await witness.processed
 record("camera_rotation_does_not_move_ship_grid_follower",settled.unchanged(true) and rain.global_position==expected)
 rain.visible=true
 record("hidden_to_visible_still_fails_with_diagnostics",not settled.unchanged(true) and evidence_complete(settled.failures[-1].details,str(rain.get_path()),rain.get_instance_id()),settled.failures)
 var visible_guard=new_guard(rain,camera)
 rain.visible=false
 record("visible_to_hidden_still_fails",not visible_guard.unchanged(true),visible_guard.failures)
 var layer_guard=new_guard(rain,camera)
 rain.layers=2
 record("hidden_layer_change_still_fails",not layer_guard.unchanged(true) and layer_guard.failures[-1].details.before.layers!=layer_guard.failures[-1].details.current.layers,layer_guard.failures)
 rain.layers=1;rain.visible=true
 var transform_guard=new_guard(rain,camera)
 rain.position.x+=1
 record("visible_candidate_transform_still_fails",not transform_guard.unchanged(true) and evidence_complete(transform_guard.failures[-1].details,str(rain.get_path()),rain.get_instance_id()),transform_guard.failures)
 var mask_guard=new_guard(rain,camera)
 camera.cull_mask=0
 record("effective_visibility_mask_change_still_fails",not mask_guard.unchanged(true) and mask_guard.failures[-1].details.before.camera_cull_mask!=mask_guard.failures[-1].details.current.camera_cull_mask,mask_guard.failures)
 camera.cull_mask=1048575
 var deletion_guard=new_guard(rain,camera)
 var saved_id:=rain.get_instance_id();var saved_path:=str(rain.get_path())
 follower.queue_free();rain.queue_free()
 record("queued_deletion_keeps_full_live_diagnostics",not deletion_guard.unchanged(true) and evidence_complete(deletion_guard.failures[-1].details,saved_path,saved_id),deletion_guard.failures)
 await process_frame
 await process_frame
 deletion_guard.failures.clear()
 record("actual_deletion_preserves_before_and_marks_current_unavailable",not deletion_guard.unchanged(true) and deletion_guard.failures[-1].details.before.instance_id==saved_id and deletion_guard.failures[-1].details.current.exists==false,deletion_guard.failures)
 witness.queue_free();scene.queue_free()
 await process_frame
 await process_frame
 var result: Dictionary={"version":"orbit61-process-sync-v4","engine":Engine.get_version_info(),"passed":not failed,"checks":checks,"scope":"Real synthetic _process signal/witness ordering and unchanged strict inventory gates. No game, MultiMesh, input, world render or production post_draw claim."}
 var file:=FileAccess.open(output,FileAccess.WRITE)
 file.store_string(JSON.stringify(result,"  ")+"\n");file.close()
 print("ORBIT61_PROCESS_SYNC ",not failed," checks=",checks.size())
 quit(1 if failed else 0)
