extends SceneTree
## Scoped player-input evidence. Loads one ordinary scene; never saves a scene.
## Physics events, including timed key release, run after the actual game callback.
const SCENE := "res://scenes/candidate61-coast/Game61Coast.tscn"
const SHA := "dff06de665e1fa1f6ab74ff3cdf4e91442e1ac322839a37718e799f0d7fa44d8"
const ROOT := "/workspace/scratch/a29d03198654/Aether"
const KEYS := [KEY_W,KEY_S,KEY_A,KEY_D,KEY_E,KEY_Q,KEY_SHIFT,KEY_SPACE,KEY_F2]
const START := Vector3(-3480,18,-3740)
const END := Vector3(-3360,18,-3560)
const CORRIDOR_METERS := 216.33307652783935
const MAX_METERS := 260.0
const MAX_SIM_SECONDS := 20.0
const POWER_SECONDS := 1.0
const LIFT_SECONDS := 0.85
const STABLE_SECONDS := 0.25

class PhysicsWitness extends Node:
 signal ticked
 var owner_harness
 var simulation_seconds := 0.0
 func _physics_process(delta: float) -> void:
  simulation_seconds += delta
  owner_harness.observe_tick(delta)
  ticked.emit()
 func _input(event: InputEvent) -> void:
  if event is InputEventKey and event.physical_keycode in KEYS:
   owner_harness.input_deliveries.append({"physical_keycode": event.physical_keycode, "pressed": event.pressed, "physics_frame": Engine.get_physics_frames()})

var game
var witness: PhysicsWitness
var output := ""
var stage := "initializing"
var failed := false
var finished := false
var flight_active := false
var flight_phase := "not_started"
var sim_seconds := 0.0
var phase_start := 0.0
var stable_seconds := 0.0
var origin := Vector3.ZERO
var forward := Vector3.ZERO
var previous_position := Vector3.ZERO
var path_metres := 0.0
var peak_speed := 0.0
var max_step_velocity_error := 0.0
var stable_origin := Vector3.ZERO
var flight_start := {}
var power_end := {}
var coast_end := {}
var stop_state := {}
var checks := []
var failures := []
var samples := []
var input_events := []
var input_deliveries := []
var captures := []
var milestones := []
var preflight := {}
var source_hashes := {}
var source_checks := []
var boot := {}
var navigation := {}
var pending_capture := ""
var capture_completed := ""
var renderer := {}
var expected_keys := {}
var envelope_bounds := AABB()
var camera_shape := SphereShape3D.new()
var altitude_levels := []
var inherited_poses := []
var motion_complete := false
var ordinary_ui_pose_passed := false
var baseline_ui_pose_passed := true
var concluding := false

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-dir="): output = arg.trim_prefix("--output-dir=")
 call_deferred("run")

func vec(v: Vector3) -> Array:
 return [v.x, v.y, v.z]

func state() -> Dictionary:
 if not is_instance_valid(game) or not is_instance_valid(game.airship): return {}
 return {"position": vec(game.airship.global_position), "velocity": vec(game.airship.velocity), "speed": game.speed,
  "vertical_speed": game.vertical_speed, "throttle": game.throttle, "heading": game.heading,
  "fuel": game.fuel, "shield": game.shield, "health": game.health, "travelled": game.travelled,
  "anchored": game.anchored, "photo_mode": game.photo_mode, "reference_observation": game.reference_observation,
  "testing": game.testing, "test_override_input": game.test_override_input, "test_frozen": game.test_frozen,
  "auto_pilot": game.auto_pilot, "docked": game.docked, "slide_collisions": game.airship.get_slide_collision_count(),
  "camera_position": vec(game.camera.global_position), "camera_fov": game.camera.fov,
  "camera_transform_hex": var_to_bytes(game.camera.transform).hex_encode(), "camera_scale_hex": var_to_bytes(game.camera.scale).hex_encode(), "camera_scale":vec(game.camera.scale), "camera_is_current": game.camera.is_current(), "physics_frame": Engine.get_physics_frames(),
  "time_scale": Engine.time_scale, "flight_sim_seconds": sim_seconds, "phase": flight_phase}

func mark(label: String, details: Variant = null) -> void:
 stage = label
 milestones.append({"stage": label, "wall_ms": Time.get_ticks_msec(), "flight_sim_seconds": sim_seconds, "details": details})
 print("FLIGHT61 STAGE ", label)
 write_report(false)

func require(ok: bool, label: String, details: Variant = null) -> bool:
 checks.append({"passed": ok, "name": label, "details": details})
 print("PASS " if ok else "FAIL ", label)
 if not ok: abort_test(label, details)
 return ok

func abort_test(reason: String, details: Variant = null) -> void:
 if failed or finished: return
 failed = true
 flight_active = false
 release_keys()
 if is_instance_valid(game): game.test_frozen = true
 failures.append({"reason": reason, "details": details, "state": state()})
 mark("failed_frozen", reason)
 call_deferred("finish")

func key(code: Key, pressed: bool) -> bool:
 expected_keys[code]=pressed
 var event := InputEventKey.new()
 event.physical_keycode = code
 event.keycode = code
 event.pressed = pressed
 Input.parse_input_event(event)
 Input.flush_buffered_events()
 var observed := Input.is_physical_key_pressed(code)
 input_events.append({"key": OS.get_keycode_string(code), "physical_keycode": code, "pressed": pressed, "observed_pressed": observed, "flight_sim_seconds": sim_seconds, "physics_frame": Engine.get_physics_frames()})
 return observed == pressed

func release_keys() -> void:
 for code in KEYS: key(code, false)

func keys_released() -> bool:
 for code in KEYS:
  if Input.is_physical_key_pressed(code): return false
 return true

func wait_seconds(seconds: float) -> void:
 var start: float = witness.simulation_seconds
 while not failed and witness.simulation_seconds - start < seconds - 0.000001:
  await witness.ticked

func identity() -> bool:
 source_hashes=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("FLIGHT61_INPUTS")))
 for path in source_hashes:
  if not require(FileAccess.get_sha256(path)==source_hashes[path],"Exact frozen source "+path):return false
 if not require(FileAccess.get_sha256(SCENE)==SHA,"Exact inherited61 scene"):return false
 var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://scenes/candidate61-coast/verified61.json"))
 return require(gate.native_build_passed and gate.fresh_native_saved_scope_passed and gate.full_foot_native_reconciliation_passed and gate.inherited_1128_1216_exact_pose_and_toggle_passed,"61 actual native and full-foot prerequisites")

func collider_hits(hits: Array) -> Array:
 var rows := []
 for hit in hits:
  var object = hit.get("collider")
  rows.append({"path": str(object.get_path()) if object is Node else str(object), "shape_index": hit.get("shape", -1), "collider_id": hit.get("collider_id", 0)})
 return rows

func query_volume(shape: Shape3D, pose: Transform3D, motion: Vector3, label: String, mask: int = 5) -> Dictionary:
 var query := PhysicsShapeQueryParameters3D.new()
 query.shape = shape
 query.transform = pose
 query.motion = motion
 query.margin = game.airship.safe_margin
 query.collision_mask = mask
 query.exclude = [game.airship.get_rid()]
 query.collide_with_bodies = true
 query.collide_with_areas = false
 var space: PhysicsDirectSpaceState3D = game.get_world_3d().direct_space_state
 var overlaps := space.intersect_shape(query, 32)
 var fractions := space.cast_motion(query)
 query.transform.origin += motion
 query.motion = Vector3.ZERO
 var end_overlaps := space.intersect_shape(query, 32)
 var clear := overlaps.is_empty() and end_overlaps.is_empty() and fractions.size() == 2 and fractions[0] >= 0.999999 and fractions[1] >= 0.999999
 var result := {"label": label, "shape_type": shape.get_class(), "mask":mask, "transform": str(pose), "motion": vec(motion), "start_hits": collider_hits(overlaps), "end_hits": collider_hits(end_overlaps), "cast_fractions": Array(fractions), "clear": clear}
 if not clear and fractions.size() == 2:
  query.transform = pose
  query.transform.origin += motion * minf(1.0, fractions[1] + 0.0001)
  result["sweep_contact_hits"] = collider_hits(space.intersect_shape(query, 32))
 return result

func check_corridor() -> bool:
 var ship: CharacterBody3D = game.airship
 var collision_shapes := []
 var shapes := []
 for node in ship.find_children("*", "CollisionShape3D", true, false):
  collision_shapes.append({"path": str(node.get_path()), "shape_type": node.shape.get_class() if node.shape else "null", "disabled": node.disabled, "transform": str(node.global_transform)})
  if not node.disabled and node.shape != null:
   shapes.append({"label": str(node.name), "shape": node.shape, "local_transform": ship.global_transform.affine_inverse() * node.global_transform})
 if not require(shapes.size() == 2 and ship.collision_layer == 2 and ship.collision_mask == 1,
  "Two actual body collision shapes and saved collision filters", collision_shapes): return false
 var visible_count := 0
 var propeller_mesh_count := 0
 var bounds := AABB()
 var first := true
 for mesh in ship.find_children("*", "MeshInstance3D", true, false):
  if mesh.mesh == null or not mesh.is_visible_in_tree(): continue
  visible_count += 1
  var local: Transform3D = ship.global_transform.affine_inverse() * mesh.global_transform
  var mesh_bounds: AABB = mesh.get_aabb().grow(0.5)
  for corner in range(8):
   var point: Vector3 = local * mesh_bounds.get_endpoint(corner)
   if first: bounds = AABB(point, Vector3.ZERO); first = false
   else: bounds = bounds.expand(point)
  # The ordinary _process rotates the propeller continuously. Bound its
  # complete local-X revolution, so the current screenshot pose is not
  # mistaken for the maximum moving silhouette during the flight.
  if game.propeller.is_ancestor_of(mesh):
   propeller_mesh_count += 1
   var to_prop: Transform3D = game.propeller.global_transform.affine_inverse() * mesh.global_transform
   var to_ship: Transform3D = ship.global_transform.affine_inverse() * game.propeller.global_transform
   var radial := 0.0
   var min_x := INF
   var max_x := -INF
   for corner in range(8):
    var point: Vector3 = to_prop * mesh_bounds.get_endpoint(corner)
    radial = maxf(radial, Vector2(point.y, point.z).length())
    min_x = minf(min_x, point.x)
    max_x = maxf(max_x, point.x)
   var revolution := AABB(Vector3(min_x, -radial, -radial), Vector3(max_x - min_x, radial * 2, radial * 2))
   for corner in range(8): bounds = bounds.expand(to_ship * revolution.get_endpoint(corner))
 if not require(visible_count > 0 and not first, "Conservative external envelope uses all visible ship mesh bounds", visible_count): return false
 # Bound all possible native visual bank (+/-.12), lift pitch (+/-.084)
 # and .08m bob as well as the full propeller revolution already collected.
 var enlarged:=bounds
 for bank in [-0.12,0.0,0.12]:
  for pitch in [-0.084,0.0,0.084]:
   var visual_rotation:=Basis.from_euler(Vector3(bank,0,pitch))
   for corner in range(8):
    var point:=visual_rotation*bounds.get_endpoint(corner)
    enlarged=enlarged.expand(point+Vector3.UP*.08);enlarged=enlarged.expand(point-Vector3.UP*.08)
 envelope_bounds=enlarged
 var box:=BoxShape3D.new();box.size=envelope_bounds.size
 shapes.append({"label":"full_visible_propeller_bank_pitch_bob_envelope","shape":box,"local_transform":Transform3D(Basis.IDENTITY,envelope_bounds.get_center())})
 var rows:=[];var clear:=true;var body_rows:=[]
 var right:=Vector3(-forward.z,0,forward.x)
 for altitude in [18.0,37.0,56.0,62.0]:
  for lateral in [-10.0,0.0,10.0]:
   var pose:=Transform3D(ship.global_basis,origin+right*lateral);pose.origin.y=altitude
   for item in shapes:
    for mask in [1,5]:
     var row:=query_volume(item.shape,pose*item.local_transform,forward*CORRIDOR_METERS,item.label+" y="+str(altitude)+" lateral="+str(lateral),mask)
     rows.append(row);clear=clear and row.clear
   var motion_result:=KinematicCollision3D.new()
   var blocked:=ship.test_move(pose,forward*CORRIDOR_METERS,motion_result,ship.safe_margin,true,8)
   body_rows.append({"pose":str(pose),"blocked":blocked,"contacts":motion_result.get_collision_count()});clear=clear and not blocked
 # Vertical connecting sweeps close the space between horizontal altitude slabs.
 for along in [0.0,CORRIDOR_METERS*.5,CORRIDOR_METERS]:
  var pose:=Transform3D(ship.global_basis,origin+forward*along)
  for item in shapes:
   var row:=query_volume(item.shape,pose*item.local_transform,Vector3.UP*44,item.label+" vertical along="+str(along));rows.append(row);clear=clear and row.clear
 # Native following-camera offset, without altering its actual runtime logic.
 camera_shape.radius=maxf(.35,game.camera.near)
 var camera_relative:Vector3=(game.HOME_CAMERA-game.HOME_SHIP).rotated(Vector3.UP,game.heading)
 for altitude in [18.0,37.0,56.0,62.0]:
  var cp:=origin+camera_relative;cp.y=altitude+camera_relative.y
  var row:=query_volume(camera_shape,Transform3D(Basis.IDENTITY,cp),forward*CORRIDOR_METERS,"native_follow_camera y="+str(altitude));rows.append(row);clear=clear and row.clear
 var cp:=origin+camera_relative
 var camera_vertical:=query_volume(camera_shape,Transform3D(Basis.IDENTITY,cp),Vector3.UP*44,"native_follow_camera vertical");rows.append(camera_vertical);clear=clear and camera_vertical.clear
 preflight={"distance_m":CORRIDOR_METERS,"origin":vec(origin),"forward":vec(forward),"body_shapes":collision_shapes,"visible_mesh_count":visible_count,"full_revolution_propeller_mesh_count":propeller_mesh_count,"original_visible_envelope_local":str(bounds),"bank_pitch_bob_envelope_local":str(envelope_bounds),"queries":rows,"combined_body_queries":body_rows,"passed":clear,"minimum_sea_clearance_from_conservative_visual_bounds_m":18+envelope_bounds.position.y,"method":"All actual native shape and conservative complete rendered-body/propeller/bank/pitch/bob volumes swept against actual active solids, masks1/5; includes native following-camera sphere. Initial navigation excluded from flight."}
 mark("preflight_complete",preflight)
 return require(clear and propeller_mesh_count>0 and 18+envelope_bounds.position.y>=8.0,"Entire bounded low/mid/high water corridor clears actual body and rendered envelope plus camera",preflight)

func capture_after_draw() -> void:
 if pending_capture.is_empty() or failed or finished: return
 var label := pending_capture
 pending_capture = ""
 var snapshot := state()
 if label in ["02-low-moving","03-mid-moving","04-high-moving"] and not require(game.speed > 0.1 and not game.test_frozen and sim_seconds > 0, "Moving screenshot records live physics motion", snapshot): return
 var controller = game.get_node("World/LakeReflection51")
 var image: Image = root.get_texture().get_image()
 var path := output.path_join(label + ".png")
 if not require(image != null and image.save_png(path) == OK, "Saved actual rendered screenshot " + label): return
 captures.append({"name": label, "path": path, "sha256": FileAccess.get_sha256(path), "size": str(image.get_size()), "state": snapshot,
  "reflection_enabled": controller.effective_reflection, "reflection_bound_to_follow_camera": controller.main_camera == game.camera,
  "reflection_shares_world": controller.viewport.world_3d == game.get_world_3d()})
 capture_completed = label
 mark("captured_" + label)

func request_capture(label: String) -> void:
 if not pending_capture.is_empty():
  abort_test("A previous requested screenshot was not rendered before the next capture", pending_capture)
  return
 pending_capture = label

func observe_tick(delta:float)->void:
 if not flight_active or failed or finished:return
 sim_seconds+=delta
 var position:Vector3=game.airship.global_position;var step:=position-previous_position;previous_position=position;path_metres+=step.length();peak_speed=maxf(peak_speed,game.speed)
 var step_error:=step.distance_to(game.airship.velocity*delta);max_step_velocity_error=maxf(max_step_velocity_error,step_error)
 var offset:=position-origin;var along:=offset.dot(forward);var lateral:=Vector2(offset.x-forward.x*along,offset.z-forward.z*along).length()
 var sample:=state();sample.dt=delta;sample.step_m=vec(step);sample.step_velocity_error_m=step_error;sample.along_m=along;sample.lateral_m=lateral;sample.path_m=path_metres;samples.append(sample)
 if sim_seconds>MAX_SIM_SECONDS or path_metres>MAX_METERS or along>CORRIDOR_METERS or along<-.05 or lateral>.1 or position.y<17.9 or position.y>62:
  abort_test("Bounded corridor/altitude/20s simulation watchdog",sample);return
 if game.airship.get_slide_collision_count()>0 or game.health<float(flight_start.health)-.000001 or game.shield<float(flight_start.shield)-.000001:
  abort_test("Collision or damage during ordinary flight",sample);return
 if Engine.time_scale!=1.0 or game.testing or game.test_override_input or game.test_frozen or game.photo_mode or game.reference_observation or game.auto_pilot or game.docked or not game.is_physics_processing() or not game.can_process():
  abort_test("Native control loop bypassed",sample);return
 for code in KEYS:
  if Input.is_physical_key_pressed(code)!=bool(expected_keys.get(code,false)):abort_test("Physical key state mismatch",[code,sample]);return
 if step_error>.05 or absf(game.speed-Vector2(game.airship.velocity.x,game.airship.velocity.z).length())>.001 or absf(game.heading-float(flight_start.heading))>.001:
  abort_test("Uncommanded pose/velocity/heading discontinuity",sample);return
 if absf(game.clearance-position.y)>.001 or position.y+envelope_bounds.position.y<8.0:
  abort_test("Actual runtime water height or conservative sea clearance violated",sample);return
 var camera_query:=PhysicsShapeQueryParameters3D.new();camera_query.shape=camera_shape;camera_query.transform=Transform3D(Basis.IDENTITY,game.camera.global_position);camera_query.collision_mask=5;camera_query.exclude=[game.airship.get_rid()]
 if not game.get_world_3d().direct_space_state.intersect_shape(camera_query).is_empty():abort_test("Actual follow camera intersects solid",sample);return
 if flight_phase=="power" and sim_seconds>=POWER_SECONDS-.000001:
  if not require(key(KEY_W,false),"Physical W released"):return
  power_end=state()
  if not require(game.speed>10 and absf(game.throttle-.34)<.015 and not game.anchored,"Ordinary W establishes native throttle/acceleration",power_end):return
  flight_phase="low_coast";mark("low_coast")
 elif flight_phase=="low_coast" and along>=30:
  request_capture("02-low-moving");flight_phase="low_capture"
 elif flight_phase=="low_capture" and capture_completed=="02-low-moving":
  if not require(key(KEY_E,true),"First physical E ascent"):return
  altitude_levels.append(position.y);flight_phase="first_lift";phase_start=sim_seconds
 elif flight_phase=="first_lift" and sim_seconds-phase_start>=LIFT_SECONDS-.000001:
  if not require(key(KEY_E,false),"First E release"):return
  flight_phase="first_settle"
 elif flight_phase=="first_settle" and absf(game.vertical_speed)<.1:
  if not require(position.y>=34 and position.y<=40,"First native lift plateau within predicted bounded band",state()):return
  altitude_levels.append(position.y);request_capture("03-mid-moving");flight_phase="mid_capture"
 elif flight_phase=="mid_capture" and capture_completed=="03-mid-moving":
  if not require(key(KEY_E,true),"Second physical E ascent"):return
  flight_phase="second_lift";phase_start=sim_seconds
 elif flight_phase=="second_lift" and sim_seconds-phase_start>=LIFT_SECONDS-.000001:
  if not require(key(KEY_E,false),"Second E release"):return
  flight_phase="second_settle"
 elif flight_phase=="second_settle" and absf(game.vertical_speed)<.1:
  if not require(position.y>=52 and position.y<=60,"Second native lift plateau within predicted bounded band",state()):return
  altitude_levels.append(position.y);request_capture("04-high-moving");flight_phase="high_coast"
 elif flight_phase=="high_coast" and along>=185:
  if not require(capture_completed=="04-high-moving","High layer rendered before braking"):return
  coast_end=state()
  if not require(key(KEY_SPACE,true) and key(KEY_SPACE,false),"Physical Space braking"):return
  if not require(game.anchored and game.throttle==0,"Native Space engages anchor and clears throttle"):return
  flight_phase="braking";mark("braking")
 elif flight_phase=="braking":
  if game.speed<.1 and absf(game.vertical_speed)<.1:
   if stable_seconds==0:stable_origin=position
   stable_seconds+=delta
   if position.distance_to(stable_origin)>.02:abort_test("Stopped body drifts",sample);return
   if stable_seconds>=STABLE_SECONDS-.000001:
    stop_state=state();flight_phase="stopped";request_capture("05-stopped");mark("stable_stop")
  else:stable_seconds=0
 elif flight_phase=="stopped" and capture_completed=="05-stopped":
  flight_active=false;motion_complete=true;call_deferred("finish")

func compare_inherited(id:String,phase:String)->bool:
 var path="res://assets/observation55/lake_observation_poses.json" if id=="1128" else "res://assets/observation60/cloud_observation_pose.json"
 var expected:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))[id]
 var ch:=var_to_bytes(game.camera.transform).hex_encode();var sh:=var_to_bytes(game.airship.transform).hex_encode()
 var passed:bool=ch==expected.expected_camera_transform_hex and sh==expected.expected_ship_transform_hex
 inherited_poses.append({"phase":phase,"reference":id,"camera_actual_hex":ch,"camera_expected_hex":expected.expected_camera_transform_hex,"ship_actual_hex":sh,"ship_expected_hex":expected.expected_ship_transform_hex,"camera_scale_hex":var_to_bytes(game.camera.scale).hex_encode(),"passed":passed})
 write_report(false);return passed

func write_report(complete: bool) -> void:
 if output.is_empty(): return
 var report := {"version":"61-nearbay-ordinary-input-v1","stage":stage,"complete":complete,"actual_player_input_flight_passed":motion_complete,"ordinary_ui_observation_pose_passed":ordinary_ui_pose_passed,"passed":complete and not failed and motion_complete and ordinary_ui_pose_passed,"candidate":SCENE,"candidate_sha256":SHA,"renderer":renderer,"checks":checks,"failures":failures,"milestones":milestones,"boot":boot,"initial_fixture_not_flown":navigation,"preflight":preflight,"source_checks":source_checks,"input_events":input_events,"input_deliveries":input_deliveries,"samples":samples,"captures":captures,"flight_start":flight_start,"power_end":power_end,"coast_end":coast_end,"stop":stop_state,"altitude_levels_m":altitude_levels,"inherited_pose_transitions":inherited_poses,"sim_seconds":sim_seconds,"path_m":path_metres,"peak_speed_mps":peak_speed,"max_displacement_velocity_error_m":max_step_velocity_error,"all_keys_released":keys_released(),"failure_freeze_used":failed and is_instance_valid(game) and game.test_frozen,"time_scale":Engine.time_scale,"distance_cap_m":MAX_METERS,"simulation_watchdog_seconds":MAX_SIM_SECONDS,"gui_keyboard_focus_verified":false,"full_world_route_passed":false,"hardware_gpu_acceptance":false,"reference_visual_acceptance":false,"total_acceptance_passed":false,"scene_saved":false,"scope":"One explicit initial waterway fixture outside flight distance, then real W/E/Space physical events in unchanged controller and move_and_slide. No later direct flight pose/velocity writes. Post-flight native1128/1216 observations are separate navigation, excluded from flight. Byte-exact pose checks are not loosened or camera-restored."}

 var destination := output.path_join("player-flight-report.json")
 var temporary := destination + ".tmp"
 var file := FileAccess.open(temporary, FileAccess.WRITE)
 if file == null:
  push_error("Cannot write partial report: " + temporary)
  return
 file.store_string(JSON.stringify(report, "  "))
 file.flush()
 file.close()
 var result := DirAccess.rename_absolute(temporary, destination)
 if result != OK: push_error("Atomic report rename failed: " + str(result))

func finish()->void:
 if finished or concluding:return
 concluding=true;flight_active=false;release_keys()
 if not failed:
  require(captures.size()==5 and altitude_levels.size()==3,"Five actual near-bay level/stop frames",captures.size())
  var along:float=(game.airship.global_position-origin).dot(forward)
  require(sim_seconds<MAX_SIM_SECONDS and path_metres>190 and path_metres<MAX_METERS and along>=195 and along<=CORRIDOR_METERS,"Actual continuous route reaches bounded near-bay endpoint",{"along_m":along,"path_m":path_metres})
  require(game.fuel<float(flight_start.fuel),"Native ordinary motion consumed fuel")
  require(game.anchored and game.throttle==0 and game.speed<.1 and stable_seconds>=STABLE_SECONDS-.000001 and keys_released(),"Native brake stable with all keys released")
  if failed:motion_complete=false
 if not failed:
  mark("ordinary_UI_transition_checks")
  var ui_ok:=baseline_ui_pose_passed
  for id in ["1128","1216"]:
   game.observe_reference(id);await wait_seconds(.05)
   if not compare_inherited(id,"after actual near-bay flight"):
    ui_ok=false;failures.append({"reason":"Real normal-flight/observation exact pose differs; native source untouched", "reference":id,"classification":"separate real UI camera-scale/pose issue; completed near-bay motion remains recorded"})
   var before_basis:Basis=game.airship.global_basis
   if not key(KEY_F2,true) or not key(KEY_F2,false):ui_ok=false
   await wait_seconds(.05)
   if game.photo_mode or game.reference_observation or not game.anchored or game.speed!=0 or not game.airship.global_basis.is_equal_approx(before_basis):ui_ok=false
   inherited_poses.append({"phase":"ordinary F2 resumed after "+id,"state":state()})
  ordinary_ui_pose_passed=ui_ok
  if not ui_ok:failed=true;game.test_frozen=true
 for path in source_hashes:
  if FileAccess.get_sha256(path)!=source_hashes[path]:failed=true;failures.append({"reason":"Immutable source changed","path":path})
 release_keys();finished=true;stage="failed" if failed else "complete";write_report(true)
 print("ACTUAL PLAYER INPUT FLIGHT61 COMPLETE motion=",motion_complete," ui_pose=",ordinary_ui_pose_passed," passed=",not failed)
 if is_instance_valid(game):game.queue_free()
 await process_frame;await process_frame;quit(1 if failed else 0)

func run() -> void:
 if output.is_empty() or not output.is_absolute_path() or DirAccess.dir_exists_absolute(output):
  push_error("Use a new absolute --output-dir"); quit(2); return
 if DirAccess.make_dir_recursive_absolute(output) != OK: quit(2); return
 mark("before_identity")
 if not require(DisplayServer.get_name() != "headless", "Renderer required for actual five-image flight evidence"): return
 if not require(is_equal_approx(Engine.time_scale, 1.0), "Simulation begins at native time_scale1"): return
 for arg in OS.get_cmdline_user_args():
  if not require(arg.begins_with("--output-dir="), "Only output argument supplied; no game-test/capture/tour flags", arg): return
 if not identity(): return
 renderer = {"display_server": DisplayServer.get_name(), "adapter": RenderingServer.get_video_adapter_name(),
  "vendor": RenderingServer.get_video_adapter_vendor(), "api": RenderingServer.get_video_adapter_api_version(),
  "godot": Engine.get_version_info(), "physics_ticks_per_second": Engine.physics_ticks_per_second,
  "user_data_dir": OS.get_user_data_dir()}
 if not require(OS.get_user_data_dir().begins_with("/workspace/scratch/a29d03198654/tools-feiting/"), "Isolated userdata is outside project", OS.get_user_data_dir()): return
 root.size = Vector2i(1180, 664)
 release_keys()
 mark("before_single_scene_load")
 var packed: PackedScene = load(SCENE)
 if not require(packed != null, "Exact61 coast inherited packed scene loaded"): return
 game = packed.instantiate()
 packed = null
 root.add_child(game)
 mark("ordinary_boot_ready", state())
 witness = PhysicsWitness.new()
 witness.name = "PlayerFlightWitness"
 witness.owner_harness = self
 witness.process_physics_priority = 100000
 root.add_child(witness)
 RenderingServer.frame_post_draw.connect(capture_after_draw)
 var home_position: Vector3 = game.airship.global_position
 await wait_seconds(0.1)
 if failed: return
 boot = state()
 boot["hud_present"] = is_instance_valid(game.hud) and game.hud.is_inside_tree()
 boot["physics_processing"] = game.is_physics_processing()
 boot["root_script"] = game.get_script().resource_path
 var boot_reflection = game.get_node("World/LakeReflection51")
 boot["reflection"] = {"camera_transform_hex": var_to_bytes(game.camera.transform).hex_encode(), "camera_scale_hex": var_to_bytes(game.camera.scale).hex_encode(), "camera_scale":vec(game.camera.scale), "camera_is_current": game.camera.is_current(), "bound_to_main_camera": boot_reflection.main_camera == game.camera,
  "shares_world": boot_reflection.viewport.world_3d == game.get_world_3d(), "effective": boot_reflection.effective_reflection,
  "clip_enabled": boot_reflection.clip_enabled, "requested": boot_reflection.reflection_enabled}
 if not require(not game.testing and not game.test_override_input and not game.test_frozen and not game.photo_mode and not game.reference_observation and not game.auto_pilot and game.anchored,
  "Ordinary ready state uses current gameplay without test/observation override", boot): return
 if not require(game.airship.global_position.distance_to(home_position) < 0.01 and game.speed == 0 and boot.hud_present and boot.physics_processing,
  "Ordinary boot has live HUD/physics and anchored no-drift start", boot): return
 mark("boot_verified")
 # Baseline exact native poses, prior to any new fixture or ordinary flight.
 for id in ["1128","1216"]:
  game.observe_reference(id);await wait_seconds(.05)
  if not compare_inherited(id,"before fixture"):
   baseline_ui_pose_passed=false
   failures.append({"reason":"Ordinary boot already changes inherited exact pose before fixture","reference":id,"classification":"independent UI pose regression; bounded flight may still be evaluated"})
   mark("baseline_UI_pose_diff",id)
 var before_navigation:=state()
 game.observe_reference("1131")
 origin=START;forward=(END-START).normalized()
 # The following one-time setup is explicitly excluded from all motion evidence.
 game.airship.position=origin;game.airship.rotation=Vector3(0,atan2(forward.z,-forward.x),0)
 game.heading=game.airship.rotation.y-deg_to_rad(13);game.altitude=origin.y;game.clearance=origin.y-game.world.ground_height(origin)
 game.camera.position=origin+(game.HOME_CAMERA-game.HOME_SHIP).rotated(Vector3.UP,game.heading)
 game.camera.look_at(origin+Vector3(4.15,4.2,1.1).rotated(Vector3.UP,game.heading))
 navigation={"operation":"one-time bounded near-bay fixture after native1131 weather/navigation","classification":"initial pose setup only; not flown distance","before":before_navigation,"after":state()}
 game.world.update_focus(origin + forward * CORRIDOR_METERS * 0.5, true)
 await wait_seconds(0.05)
 if failed: return
 mark("nearbay_fixture_settled", navigation)
 if not require(game.photo_mode and game.reference_observation and game.anchored and game.airship.velocity == Vector3.ZERO, "Existing observation pauses player flight before preflight"): return
 if not check_corridor(): return
 var observation_camera: Vector3 = game.camera.global_position
 var before_f2_basis: Basis = game.airship.global_basis
 if not require(key(KEY_F2, true) and key(KEY_F2, false), "Physical F2 press and release delivered"): return
 await wait_seconds(0.25)
 if failed: return
 if not require(not game.photo_mode and not game.reference_observation and game.camera.global_position.distance_to(observation_camera) < 1,
  "Existing F2 exits observation and retains continuous native follow camera", state()): return
 if not require(game.airship.global_basis.is_equal_approx(before_f2_basis), "F2 resumes synchronized fixture heading without a turn", {"before":str(before_f2_basis),"after":str(game.airship.global_basis)}):return
 request_capture("01-start")
 while capture_completed != "01-start" and not failed: await witness.ticked
 if failed: return
 if not require(game.airship.global_position.distance_to(origin) < 0.01 and game.speed == 0, "F2/capture preparation leaves anchored navigation start unchanged"): return
 flight_start = state()
 previous_position = game.airship.global_position
 flight_phase = "power"
 flight_active = true
 if not require(key(KEY_W, true), "Physical W press delivered to existing input polling"): return
 mark("W_pressed", flight_start)
