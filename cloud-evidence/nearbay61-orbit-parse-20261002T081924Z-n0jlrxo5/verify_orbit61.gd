extends SceneTree
## First bounded item: anchored native right-mouse orbit. NO flight keys.
## Actual camera process segments are queued, then queried during physics.
const SCENE := "res://scenes/candidate61-coast/Game61Coast.tscn"
const SCENE_SHA := "dff06de665e1fa1f6ab74ff3cdf4e91442e1ac322839a37718e799f0d7fa44d8"
const VISUAL_AUDIT = preload("visible_geometry61.gd")
const FIXTURE_LIFECYCLE = preload("fixture_lifecycle61.gd")
const NATIVE_MOUSE = preload("native_mouse61.gd")
const TELEMETRY = preload("orbit_telemetry61.gd")
const SEQUENCE = preload("native_sequence61.gd")
const CONTROL_PROTOCOL := "v6 continuous: each <=.05rad native event waits for a newer actual late-process sample and its exact physics audit; settle twice <=.02m only at capture goals and startup"
const LIVE_RESOURCE_IDENTITY_SCOPE := {
 "universal_live_resource_freeze_proved":false,
 "multimesh_observation":"Complete CPU transform/color/custom-data buffer, binding, counts, formats and bounds at late-process/physics/final witnesses, including hidden/outside-domain nodes",
 "mesh_content_limit":"Same-resource Mesh vertex/index/LOD/shadow arrays can mutate without ID, surface-count or AABB changes; these arrays are not rehashed at every witness",
 "mesh_instance_binding_limit":"MeshInstance3D bindings and all same-resource mutable fields are not universally frozen by the MultiMesh-specific guard",
 "material_shader_limit":"Material/shader rebindings, code, parameters and arbitrary shader semantics lack a complete live fingerprint; native weather legitimately changes time uniforms",
 "ship_limit":"Animated ship descendants retain documented conservative envelopes, not universal live resource identity",
 "observation_limit":"Rendering-server-only mutation or changes reverted between every observed boundary are not generally detected by CPU snapshots",
 "dependency_limit":"Wrapper verifies exact reviewed saved loading closure and reviewed absence controls before/after; this is not live geometry/material or pixel coverage acceptance"
}
const START := Vector3(-3430,28,-3665)
const FORWARD := Vector3(0.5547001962252291,0,0.8320502943378437)
const ORBIT_TARGETS := [2.6,PI,4.0]
const STEP_RADIANS := .05
const KEYS := [KEY_W,KEY_S,KEY_A,KEY_D,KEY_E,KEY_Q,KEY_SHIFT,KEY_SPACE,KEY_F2]
const MAX_WALL_SECONDS := 600.0
const SETTLE_METERS := .02
const LOCAL_RAY_METERS := 450.0

class Witness extends Node:
 signal processed
 signal physics_checked
 var harness
 func _process(delta: float) -> void:
  harness.sample_process(delta)
  processed.emit()
 func _physics_process(_delta: float) -> void:
  harness.audit_pending()
  physics_checked.emit()
 func _input(event: InputEvent) -> void:
  if event is InputEventMouseMotion:
   harness.delivered.append({"kind":"motion","relative":[event.relative.x,event.relative.y],"position":[event.position.x,event.position.y],"global_position":[event.global_position.x,event.global_position.y],"right":Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT),"button_mask":event.button_mask,"window_id":event.window_id,"input_mapping":NATIVE_MOUSE.snapshot(get_tree().root),"process_frame":Engine.get_process_frames()})
  elif event is InputEventMouseButton:
   harness.delivered.append({"kind":"button","button":event.button_index,"pressed":event.pressed,"process_frame":Engine.get_process_frames()})
  elif event is InputEventKey and event.physical_keycode in KEYS:
   harness.delivered.append({"kind":"key","code":event.physical_keycode,"pressed":event.pressed,"process_frame":Engine.get_process_frames()})

var game
var witness: Witness
var visual
var output := ""
var stage := "initializing"
var failed := false
var finishing := false
var active := false
var inventory_ready := false
var passed := false
var start_wall := 0
var observation_budget_seconds := 600
var observation_budget_valid := false
var settle_wait_budget_seconds := 15
var settle_budget_valid := false
var source_hashes := {}
var failures := []
var checks := []
var events := []
var delivered := []
var process_samples := []
var pending := []
var audited := []
var captures := []
var preflight := []
var fixture := {}
var sphere := SphereShape3D.new()
var last_camera := Vector3.ZERO
var last_frame := -1
var process_path := 0.0
var ship_path := 0.0
var last_ship := Vector3.ZERO
var base_ship := Transform3D.IDENTITY
var base_travelled := 0.0
var requested_capture := ""
var captured := ""
var new_geometry := []
var fixture_pause_state := {}
var telemetry=TELEMETRY.new()
var sequence=SEQUENCE.new()
var last_progress_usec := -1000000
var angular_index := -1
var angular_goal := 0.0
var motion_index := 0
var source_hash_completed := 0
var wall_deadline_checks := 0
var wall_deadline_last := {}
var wall_deadline_exceeded_at := {}
var verification_completed_wall_seconds: Variant = null

func wall_deadline_snapshot() -> Dictionary:
 return {"limit_seconds":observation_budget_seconds,"historical_performance_limit_seconds":MAX_WALL_SECONDS,"clock":"Time.get_ticks_msec monotonic; no supplied/mock clock","start_scope":"run entry before initial source hashes, scene load, fixture synchronization, inventory and preflight","completion_scope":"Final native check after report write/hash and receipt flush/rename/hash, before emitting terminal clock metadata and cleanup; actual child exit is separately bounded by the wrapper (default720s; explicit long observation1020s)","completion_receipt":"orbit-completion.json","checks":wall_deadline_checks,"last_check":wall_deadline_last.duplicate(true),"first_exceeded_at":wall_deadline_exceeded_at.duplicate(true),"verification_completed_wall_seconds":verification_completed_wall_seconds}

func within_wall_deadline(boundary: String, completing: bool=false) -> bool:
 # A late process sample cannot license an expensive phase to finish after the requested finite budget.
 # The only clock is the actual native monotonic clock, never an argument.
 var elapsed_msec: int=Time.get_ticks_msec()-start_wall
 wall_deadline_checks+=1
 wall_deadline_last={"boundary":boundary,"elapsed_msec":elapsed_msec,"wall_seconds":elapsed_msec/1000.0}
 if completing: verification_completed_wall_seconds=elapsed_msec/1000.0
 if elapsed_msec>=0 and elapsed_msec<=observation_budget_seconds*1000 and wall_deadline_exceeded_at.is_empty(): return true
 if wall_deadline_exceeded_at.is_empty(): wall_deadline_exceeded_at=wall_deadline_last.duplicate(true)
 passed=false
 if not failed:
  if finishing:
   failed=true;active=false
   failures.append({"reason":"Stationary orbit wall watchdog","details":wall_deadline_exceeded_at.duplicate(true),"state":current_state()})
   if is_instance_valid(game): game.test_frozen=true
  else:
   abort("Stationary orbit wall watchdog",wall_deadline_exceeded_at.duplicate(true))
 return false

func progress(force: bool=false) -> void:
 var now:=Time.get_ticks_usec()
 if not force and now-last_progress_usec<1000000: return
 if output.is_empty() or not DirAccess.dir_exists_absolute(output): return
 last_progress_usec=now
 var state: Dictionary={"version":"orbit61-progress-v6","diagnostic_only":true,"completion_authority":"orbit-report.json plus wrapper-report.json; this heartbeat is never acceptance","stage":stage,"failed":failed,"finishing":finishing,"angular_index":angular_index,"angular_goal":angular_goal,"native_motion_count":motion_index,"pending_segments":pending.size(),"last_sampled_process_frame":last_frame,"last_audited_process_frame":sequence.last_audit,"process_samples":process_samples.size(),"audited_segments":audited.size(),"captures":captures.size(),"preflight_segments":preflight.size(),"source_hash_completed":source_hash_completed,"source_hash_total":source_hashes.size(),"sequence":sequence.snapshot(),"telemetry":telemetry.snapshot()}
 if is_instance_valid(game): state.orbit=[game.orbit.x,game.orbit.y]
 var file:=FileAccess.open(output.path_join("orbit-progress.json.tmp"),FileAccess.WRITE)
 if file==null: push_error("Cannot write orbit diagnostic heartbeat");return
 file.store_string(JSON.stringify(state));file.flush();file.close()
 if DirAccess.rename_absolute(output.path_join("orbit-progress.json.tmp"),output.path_join("orbit-progress.json"))!=OK: push_error("Cannot replace orbit diagnostic heartbeat")

func _initialize() -> void:
 var budget_arguments:=0
 var settle_arguments:=0
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
  if arg.begins_with("--observation-budget-seconds="):
   budget_arguments+=1
   var value:=arg.trim_prefix("--observation-budget-seconds=")
   observation_budget_valid=value in ["600","900"]
   if observation_budget_valid: observation_budget_seconds=int(value)
  if arg.begins_with("--settle-wait-budget-seconds="):
   settle_arguments+=1
   var value:=arg.trim_prefix("--settle-wait-budget-seconds=")
   settle_budget_valid=value in ["15","30"]
   if settle_budget_valid: settle_wait_budget_seconds=int(value)
 observation_budget_valid=observation_budget_valid and budget_arguments==1
 settle_budget_valid=settle_budget_valid and settle_arguments==1 and ((observation_budget_seconds==600 and settle_wait_budget_seconds==15) or (observation_budget_seconds==900 and settle_wait_budget_seconds==30))
 call_deferred("run")

func vec(p: Vector3) -> Array:
 return [p.x,p.y,p.z]

func current_state() -> Dictionary:
 if not is_instance_valid(game): return {}
 return {"ship_position":vec(game.airship.global_position),"ship_transform_hex":var_to_bytes(game.airship.global_transform).hex_encode(),"velocity":vec(game.airship.velocity),"camera_position":vec(game.camera.global_position),"camera_transform_hex":var_to_bytes(game.camera.global_transform).hex_encode(),"camera_scale":vec(game.camera.scale),"orbit":[game.orbit.x,game.orbit.y],"heading":game.heading,"speed":game.speed,"throttle":game.throttle,"anchored":game.anchored,"photo_mode":game.photo_mode,"reference_observation":game.reference_observation,"test_frozen":game.test_frozen,"testing":game.testing,"test_override_input":game.test_override_input,"auto_pilot":game.auto_pilot,"docked":game.docked,"travelled":game.travelled,"right_button":Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT),"process_frame":Engine.get_process_frames(),"physics_frame":Engine.get_physics_frames()}

func report(complete: bool) -> void:
 var began:=telemetry.begin("full_report_write")
 if output.is_empty() or not DirAccess.dir_exists_absolute(output): return
 var result := {"version":"61-anchored-orbit-v6","requested_observation_budget_seconds":observation_budget_seconds,"settle_wait_budget_seconds":settle_wait_budget_seconds,"strict_600_performance_authority":"Completion receipt and final terminal wall only; this report precedes those clock observations","wall_deadline":wall_deadline_snapshot(),"display_backend":DisplayServer.get_name(),"rendering_method":RenderingServer.get_current_rendering_method(),"rendering_driver":RenderingServer.get_current_rendering_driver_name(),"control_protocol":CONTROL_PROTOCOL,"sequence":sequence.snapshot(),"telemetry":telemetry.snapshot(),"complete":complete,"stage":stage,"failed":failed,"first_item_runtime_passed":passed and complete and not failed,"fixture_excluded_from_distance":fixture,"checks":checks,"failures":failures,"events":events,"delivered":delivered,"process_samples":process_samples,"audited_segments":audited,"preflight":preflight,"captures":captures,"near_plane_envelope_radius_m":sphere.radius,"actual_camera_path_m":process_path,"actual_ship_path_after_fixture_m":ship_path,"flight_attempted":false,"short_flight_passed":false,"nearshore_pixel_coverage_passed":false,"manual_normal_material_png_review_required":true,"nearest_ray_scope_m":LOCAL_RAY_METERS,"gui_focus_verified":false,"hardware_gpu_acceptance":false,"reference_visual_acceptance":false,"total_acceptance_passed":false,"scene_saved":false,"state":current_state(),"visual_inventory":visual.rows if visual!=null else [],"visual_inventory_failures":visual.failures if visual!=null else [],"visual_triangle_count":visual.triangle_count if visual!=null else 0,"visual_method":"Actual static indexed surfaces in an isolated physics query space, classified shader and animated ship conservative envelopes. Envelope hits do not imply pixel visibility or universal live resource freezing.","live_resource_identity_scope":LIVE_RESOURCE_IDENTITY_SCOPE,"source_count":source_hashes.size()}
 var file := FileAccess.open(output.path_join("orbit-report.json.tmp"),FileAccess.WRITE)
 if file==null: push_error("Cannot write orbit report"); return
 file.store_string(JSON.stringify(result,"  "));file.flush();file.close()
 if DirAccess.rename_absolute(output.path_join("orbit-report.json.tmp"),output.path_join("orbit-report.json"))!=OK: push_error("Cannot replace orbit report")
 telemetry.end("full_report_write",began)
 progress(true)

func mark(label: String) -> void:
 stage=label
 progress(true)
 print("ORBIT61 ",label)
 report(false)
 within_wall_deadline("report_"+label)

func check(ok: bool, label: String, detail: Variant=null) -> bool:
 checks.append({"passed":ok,"name":label,"details":detail})
 if not ok: abort(label,detail)
 return ok

func abort(reason: String, detail: Variant=null) -> void:
 if failed or finishing: return
 failed=true;active=false
 failures.append({"reason":reason,"details":detail,"state":current_state()})
 release_all()
 if is_instance_valid(game): game.test_frozen=true
 mark("failed_frozen")
 call_deferred("finish")

func key(code: Key, pressed: bool) -> bool:
 var event := InputEventKey.new()
 event.physical_keycode=code;event.keycode=code;event.pressed=pressed
 Input.parse_input_event(event);Input.flush_buffered_events()
 events.append({"kind":"key","code":code,"pressed":pressed,"observed":Input.is_physical_key_pressed(code),"process_frame":Engine.get_process_frames()})
 return Input.is_physical_key_pressed(code)==pressed

func mouse_button(pressed: bool) -> bool:
 var mapping:=NATIVE_MOUSE.snapshot(root)
 var center:=root.get_visible_rect().get_center()
 var converted:=NATIVE_MOUSE.convert(root.get_final_transform(),center,Vector2.ZERO)
 # Emergency releases must still clear native held state if mapping is invalid.
 if pressed and not check(converted.ok,"Finite nonsingular native button coordinate mapping",mapping): return false
 var event := InputEventMouseButton.new()
 event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
 event.button_mask=MOUSE_BUTTON_MASK_RIGHT if pressed else 0
 event.position=converted.position if converted.ok else Vector2.ZERO
 event.global_position=event.position;event.window_id=root.get_window_id()
 Input.parse_input_event(event);Input.flush_buffered_events()
 events.append({"kind":"right_button","pressed":pressed,"observed":Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT),"intended_viewport_center":NATIVE_MOUSE.pair(center),"sent_window_position":NATIVE_MOUSE.pair(event.position),"input_mapping":mapping,"emergency_release_position_fallback":not converted.ok,"process_frame":Engine.get_process_frames()})
 return Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)==pressed

func motion(radians: float) -> bool:
 if not within_wall_deadline("before_native_motion"): return false
 if not check(radians>0 and radians<=STEP_RADIANS,"Native event stays within unchanged .05rad bound",radians): return false
 if not check(pending.is_empty() and sequence.begin_event(Engine.get_process_frames()),"Native event starts only after all previous exact segments audited",sequence.snapshot()): return false
 motion_index+=1
 telemetry.count("native_motion_events")
 progress()
 var before: Vector2=game.orbit
 var mapping_before:=NATIVE_MOUSE.snapshot(root)
 var center:=root.get_visible_rect().get_center()
 var intended:=Vector2(-radians/.004,0)
 var converted:=NATIVE_MOUSE.convert(root.get_final_transform(),center,intended)
 if not check(converted.ok,"Finite nonsingular native motion coordinate mapping",mapping_before): return false
 var event := InputEventMouseMotion.new()
 event.relative=converted.relative
 event.button_mask=MOUSE_BUTTON_MASK_RIGHT
 event.position=converted.position;event.global_position=event.position;event.window_id=root.get_window_id()
 var delivery_start:=delivered.size()
 Input.parse_input_event(event);Input.flush_buffered_events()
 var mapping_after:=NATIVE_MOUSE.snapshot(root)
 var received:=delivered.slice(delivery_start)
 var delivery:=NATIVE_MOUSE.delivery_check(received,intended,center,mapping_before,mapping_after)
 var detail: Dictionary={"kind":"native_mouse_motion","requested_radians":radians,"intended_viewport_relative":NATIVE_MOUSE.pair(intended),"sent_window_relative":NATIVE_MOUSE.pair(event.relative),"intended_viewport_center":NATIVE_MOUSE.pair(center),"sent_window_position":NATIVE_MOUSE.pair(event.position),"input_mapping_before":mapping_before,"input_mapping_after":mapping_after,"delivered":received,"delivery_check":delivery,"before":[before.x,before.y],"after":[game.orbit.x,game.orbit.y],"process_frame":Engine.get_process_frames()}
 events.append(detail)
 if not check(delivery.passed,"One native motion delivered in intended viewport units with stable mapping",detail): return false
 return check(absf(game.orbit.x-before.x-radians)<.00001 and absf(game.orbit.y-before.y)<.00001,"Native orbit event applied exact bounded increment",detail)

func release_all() -> void:
 mouse_button(false)
 for code in KEYS: key(code,false)

func inputs_released() -> bool:
 if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT): return false
 for code in KEYS:
  if Input.is_physical_key_pressed(code): return false
 return true

func native_target() -> Vector3:
 return game.airship.global_position+Vector3(4.15,4.2,1.1).rotated(Vector3.UP,game.heading)

func native_desired(angle: float) -> Vector3:
 var relative: Vector3=(game.HOME_CAMERA-game.HOME_SHIP)*game.zoom
 relative=relative.rotated(Vector3.RIGHT,-game.orbit.y)
 return game.airship.global_position+relative.rotated(Vector3.UP,game.heading+angle)

func raw_native_ray(from: Vector3, to: Vector3) -> Dictionary:
 var began:=telemetry.begin("native_los_ray")
 var query := PhysicsRayQueryParameters3D.create(from,to,1,[game.airship.get_rid()])
 var hit: Dictionary=game.get_world_3d().direct_space_state.intersect_ray(query)
 telemetry.end("native_los_ray",began);telemetry.count("native_los_rays")
 if hit.is_empty(): return {}
 return {"path":str(hit.collider.get_path()) if hit.collider is Node else str(hit.collider),"position":vec(hit.position),"distance":from.distance_to(hit.position)}

func sweep(space: PhysicsDirectSpaceState3D, a: Vector3, b: Vector3, mask: int, visual_query: bool) -> Dictionary:
 var label: String="visible_sweep" if visual_query else "physical_sweep"
 var began:=telemetry.begin(label)
 var q := PhysicsShapeQueryParameters3D.new()
 q.shape=sphere;q.transform=Transform3D(Basis.IDENTITY,a);q.collision_mask=mask
 q.margin=.005;q.collide_with_bodies=true;q.collide_with_areas=false
 # No excluded ship RID: own layer2 must participate in camera clearance.
 var start_hits: Array=space.intersect_shape(q,32)
 q.motion=b-a
 var fractions: PackedFloat32Array=space.cast_motion(q)
 q.transform.origin=b;q.motion=Vector3.ZERO
 var end_hits: Array=space.intersect_shape(q,32)
 var hit_rows:=[]
 for hit in start_hits+end_hits:
  if visual_query: hit_rows.append(visual.decode(hit))
  else: hit_rows.append({"source":str(hit.collider.get_path()) if hit.collider is Node else str(hit.collider),"shape":hit.get("shape",-1)})
 var clear: bool=start_hits.is_empty() and end_hits.is_empty() and fractions.size()==2 and fractions[0]>=.999999 and fractions[1]>=.999999
 telemetry.end(label,began);telemetry.count(label+"_queries")
 return {"clear":clear,"from":vec(a),"to":vec(b),"radius_m":sphere.radius,"mask":mask,"fractions":Array(fractions),"endpoint_hits":hit_rows}

func sample_process(delta: float) -> void:
 telemetry.process(delta)
 progress()
 if not active or failed or finishing: return
 var frame:=Engine.get_process_frames()
 var position: Vector3=game.camera.global_position
 var ship: Vector3=game.airship.global_position
 if last_frame>=0 and frame!=last_frame+1:
  abort("Missing actual camera process sample",[last_frame,frame]);return
 if not within_wall_deadline("process_begin"): return
 if game.airship.global_transform!=base_ship or game.airship.velocity!=Vector3.ZERO or game.speed!=0 or game.throttle!=0 or not game.anchored or game.travelled!=base_travelled:
  abort("Stationary item moved the ship",current_state());return
 if game.photo_mode or game.reference_observation or game.testing or game.test_override_input or game.test_frozen or game.auto_pilot or game.docked or game.cockpit or game.zoom!=1 or Engine.time_scale!=1:
  abort("Ordinary native control invariant changed",current_state());return
 for code in KEYS:
  if Input.is_physical_key_pressed(code): abort("Unexpected held flight key",code);return
 var target:=native_target()
 var desired:=native_desired(game.orbit.x)
 var expected: Vector3=last_camera.lerp(desired,1-exp(-delta*9))
 # No correction is accepted silently: native source is frozen, and the
 # exact unobstructed smoothing step must explain this actual position.
 if expected.distance_to(position)>.002:
  abort("Native camera correction or unexplained process displacement",{"expected":vec(expected),"actual":vec(position),"dt":delta});return
 if not classify_new_geometry(): return
 # Full CPU MM state is read now, at the same late-process witness as this
 # camera endpoint. Endpoint-only final hashes cannot replace this observation.
 if not visual.unchanged(true,"late_process",frame): abort("Late-process visual identity changed",visual.failures);return
 if visual.last_identity_witness.get("ok")!=true or visual.last_identity_witness.get("process_frame")!=frame:
  abort("Missing explicit same-process identity witness");return
 if not within_wall_deadline("process_after_identity"): return
 if not sequence.sample(frame): abort("Process sequence guard failed",sequence.snapshot());return
 var row := {"identity_witness":visual.last_identity_witness.duplicate(true),"event_index":motion_index,"process_wall_usec":Time.get_ticks_usec(),"process_frame":frame,"physics_frame":Engine.get_physics_frames(),"dt":delta,"from":vec(last_camera),"to":vec(position),"target":vec(target),"desired":vec(desired),"orbit":[game.orbit.x,game.orbit.y],"camera_transform_hex":var_to_bytes(game.camera.global_transform).hex_encode()}
 process_path+=last_camera.distance_to(position);ship_path+=last_ship.distance_to(ship)
 process_samples.append(row)
 pending.append({"row":row,"from":last_camera,"to":position,"target":target,"desired":desired})
 last_frame=frame;last_camera=position;last_ship=ship

func classify_new_geometry() -> bool:
 # Run at both observed boundaries, before the identity witness. New geometry
 # must not be absent from a segment's endpoint inventory until next physics.
 for node in new_geometry:
  if not is_instance_valid(node): abort("New geometry removed before runtime classification");return false
  if not node is GeometryInstance3D: abort("Unclassified queued geometry type");return false
  if not visual.accept_distant_new_node(node):
   abort("New visual candidate after inventory; sequence cannot claim coverage",visual.failures);return false
 new_geometry.clear()
 return true

func audit_pending() -> void:
 if not active or failed or finishing or not inventory_ready: return
 if not within_wall_deadline("audit_begin"): return
 if not classify_new_geometry(): return
 if not visual.unchanged(true,"physics_before_segments",last_frame): abort("Visual candidate inventory changed",visual.failures);return
 if not within_wall_deadline("audit_after_identity"): return
 var space: PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
 var visual_space: PhysicsDirectSpaceState3D=PhysicsServer3D.space_get_direct_state(visual.space)
 if visual_space==null: abort("Isolated visual query space unavailable");return
 while not pending.is_empty():
  var item: Dictionary=pending.pop_front()
  var native_before:=raw_native_ray(item.target,item.desired)
  var native_after:=raw_native_ray(item.target,item.to)
  var physical:=sweep(space,item.from,item.to,0xffffffff,false)
  var drawn:=sweep(visual_space,item.from,item.to,1,true)
  if not within_wall_deadline("audit_after_segment_queries"): return
  var row := {"identity_witness_serial":item.row.identity_witness.serial,"identity_process_frame":item.row.identity_witness.process_frame,"physics_identity_witness":visual.last_identity_witness.duplicate(true),"process_frame":item.row.process_frame,"physical":physical,"visible_geometry":drawn,"native_desired_blocker":native_before,"native_actual_blocker":native_after}
  audited.append(row)
  if not native_before.is_empty() or not native_after.is_empty() or not physical.clear or not drawn.clear:
   abort("Actual process camera path or native line of sight blocked",row);return
  if item.row.identity_witness.get("ok")!=true or item.row.identity_witness.process_frame!=item.row.process_frame:
   abort("Queued segment has no exact late-process identity witness",item.row);return
  if not sequence.audit(item.row.process_frame): abort("Physics audit sequence guard failed",sequence.snapshot());return
 telemetry.count("physics_audit_callbacks");progress()
 if not within_wall_deadline("audit_before_capture_completion"): return
 if not captures.is_empty() and not audited.is_empty():
  var latest: Dictionary=captures[-1]
  if audited[-1].process_frame>=latest.state.process_frame and sequence.capture_ready(latest.state.process_frame):
   latest.actual_frame_segment_audited=true
   captured=latest.name

func wait_event_audited() -> bool:
 # Do not settle the intermediate desired angle: retain every actual Lerp
 # segment, then wait for its associated physics queries before next input.
 var began:=Time.get_ticks_msec()
 await witness.processed
 while not failed:
  if not within_wall_deadline("wait_event_after_process_or_physics"): return false
  if sequence.event_ready():
   return check(pending.is_empty() and sequence.complete_event(),"Native event has newer actual process and exact successful physics audit",sequence.snapshot())
  if not sequence.failure.is_empty(): abort("Native sequence guard failed",sequence.snapshot());return false
  if Time.get_ticks_msec()-began>15000:
   abort("Native event process/physics audit did not finish within15s",sequence.snapshot());return false
  await witness.physics_checked
 return false

func within_settle_budget(began: int, boundary: String) -> bool:
 var elapsed_msec:=Time.get_ticks_msec()-began
 if elapsed_msec>=0 and elapsed_msec<=settle_wait_budget_seconds*1000: return true
 abort("Native orbit smoothing exceeded selected settle wait budget",{"boundary":boundary,"elapsed_msec":elapsed_msec,"settle_wait_budget_seconds":settle_wait_budget_seconds})
 return false

func wait_settled() -> bool:
 var began:=Time.get_ticks_msec()
 var stable:=0
 while not failed:
  await witness.processed
  if failed: return false
  if not within_wall_deadline("settle_after_process"): return false
  if not within_settle_budget(began,"after_process"): return false
  if game.camera.global_position.distance_to(native_desired(game.orbit.x))<=SETTLE_METERS: stable+=1
  else: stable=0
  if stable>=2:
   await witness.physics_checked
   if not within_wall_deadline("settle_after_physics"): return false
   if not within_settle_budget(began,"after_physics_before_success"): return false
   if not failed and pending.is_empty(): return true
  if not within_settle_budget(began,"before_next_process_wait"): return false
 return false

func local_rays() -> Array:
 var began:=telemetry.begin("capture_local_rays")
 var result:=[]
 var space: PhysicsDirectSpaceState3D=PhysicsServer3D.space_get_direct_state(visual.space)
 var viewport_size: Vector2=game.camera.get_viewport().get_visible_rect().size
 # Supplementary nearest blockers. The center may correctly hit the ship.
 for uv in [Vector2(.25,.35),Vector2(.5,.35),Vector2(.75,.35),Vector2(.25,.5),Vector2(.5,.5),Vector2(.75,.5),Vector2(.25,.65),Vector2(.5,.65),Vector2(.75,.65)]:
  var pixel: Vector2=uv*viewport_size
  var from: Vector3=game.camera.project_ray_origin(pixel)
  var to: Vector3=from+game.camera.project_ray_normal(pixel)*LOCAL_RAY_METERS
  var query:=PhysicsRayQueryParameters3D.create(from,to,1)
  query.hit_back_faces=true;query.hit_from_inside=true
  var hit: Dictionary=space.intersect_ray(query)
  result.append({"viewport_pixel":[pixel.x,pixel.y],"uv":[uv.x,uv.y],"nearest_geometry_or_envelope":visual.decode(hit),"distance_m":from.distance_to(hit.position) if not hit.is_empty() else null,"ray_limit_m":LOCAL_RAY_METERS,"pixel_visibility_proved":false})
 telemetry.end("capture_local_rays",began);telemetry.count("capture_local_rays",result.size())
 return result

func after_draw() -> void:
 if requested_capture.is_empty() or failed or finishing: return
 if not within_wall_deadline("capture_before_image"): return
 var name:=requested_capture
 requested_capture=""
 var began:=telemetry.begin("capture_image")
 var image: Image=root.get_texture().get_image()
 var path:=output.path_join(name+".png")
 if not check(image!=null and image.save_png(path)==OK,"Actual normal-material image saved",name): return
 if not within_wall_deadline("capture_after_image_write"): return
 telemetry.end("capture_image",began);telemetry.count("captures_saved")
 captures.append({"name":name,"path":path,"sha256":FileAccess.get_sha256(path),"size":[image.get_width(),image.get_height()],"state":current_state(),"nearest_local_rays":local_rays(),"pixel_review":"not reviewed by renderer harness"})
 if not within_wall_deadline("capture_after_hash_and_rays"): return
 mark("captured_pending_frame_audit_"+name)

func capture(name: String) -> bool:
 requested_capture=name
 var began:=Time.get_ticks_msec()
 while captured!=name and not failed:
  # Completion is established in physics; returning from processed would
  # enqueue a new unaudited segment before the next event starts.
  await witness.physics_checked
  if not within_wall_deadline("capture_after_physics"): return false
  if Time.get_ticks_msec()-began>20000: abort("Actual capture timeout",name)
 return not failed and within_wall_deadline("capture_return")

func finish() -> void:
 if finishing: return
 finishing=true;active=false;release_all()
 within_wall_deadline("finish_begin")
 if visual!=null and not failed:
  if not visual.unchanged(true,"final",last_frame): failed=true;failures.append({"reason":"Final visual buffers changed","details":visual.failures})
 within_wall_deadline("finish_after_identity")
 var source_began:=telemetry.begin("final_source_hash")
 source_hash_completed=0
 for path in source_hashes:
  source_hash_completed+=1;telemetry.count("source_files_hashed");progress()
  if FileAccess.get_sha256(path)!=source_hashes[path]: failed=true;failures.append({"reason":"Frozen input changed","path":path})
  within_wall_deadline("finish_source_hash")
 telemetry.end("final_source_hash",source_began)
 var deadline_ok:=within_wall_deadline("finish_after_final_hash_before_pass")
 passed=deadline_ok and not failed and sequence.capture_ready(last_frame) and captures.size()==4 and audited.size()==process_samples.size() and ship_path==0 and inputs_released()
 stage="complete" if passed else "failed_or_incomplete"
 report(true)
 var report_sha:=FileAccess.get_sha256(output.path_join("orbit-report.json"))
 within_wall_deadline("finish_after_final_report_and_sha",true)
 write_completion_receipt(report_sha)
 var receipt_sha:=FileAccess.get_sha256(output.path_join("orbit-completion.json"))
 var receipt_in_time:=within_wall_deadline("finish_after_receipt_flush_rename_and_sha",true)
 if not receipt_in_time:
  # Exactly one failed rewrite; no recursion or retry can restore success.
  passed=false;stage="failed_or_incomplete"
  report(true)
  report_sha=FileAccess.get_sha256(output.path_join("orbit-report.json"))
  write_completion_receipt(report_sha)
  receipt_sha=FileAccess.get_sha256(output.path_join("orbit-completion.json"))
  within_wall_deadline("finish_after_failed_evidence_rewrite",true)
 within_wall_deadline("finish_before_cleanup",true)
 # This clock is sampled AFTER the receipt flush/rename/hash. It is deliberately
 # recorded outside that receipt, rather than labelling a pre-write tick post-write.
 print("ORBIT61_TERMINAL_WALL ",JSON.stringify({"version":"orbit61-terminal-wall-v1","requested_observation_budget_seconds":observation_budget_seconds,"settle_wait_budget_seconds":settle_wait_budget_seconds,"strict_600_performance_passed":strict_600_performance_passed(),"first_item_runtime_passed":passed and not failed,"native_report_sha256":report_sha,"completion_receipt_sha256":receipt_sha,"wall_deadline":wall_deadline_snapshot()}))
 if is_instance_valid(game):
  for i in range(3): await process_frame
  await RenderingServer.frame_post_draw
  game.queue_free()
 if visual!=null: visual.close()
 for i in range(8): await process_frame
 quit(0 if passed else 1)

func strict_600_performance_passed() -> bool:
 return passed and not failed and verification_completed_wall_seconds!=null and verification_completed_wall_seconds>=0 and verification_completed_wall_seconds<=MAX_WALL_SECONDS

func write_completion_receipt(report_sha: String) -> void:
 var receipt:=FileAccess.open(output.path_join("orbit-completion.json.tmp"),FileAccess.WRITE)
 if receipt==null:
  push_error("Cannot write orbit completion receipt");passed=false
 else:
  receipt.store_string(JSON.stringify({"version":"orbit61-completion-v1","requested_observation_budget_seconds":observation_budget_seconds,"settle_wait_budget_seconds":settle_wait_budget_seconds,"strict_600_performance_passed":strict_600_performance_passed(),"first_item_runtime_passed":passed and not failed,"native_report_sha256":report_sha,"wall_deadline":wall_deadline_snapshot()}));receipt.flush();receipt.close()
  if DirAccess.rename_absolute(output.path_join("orbit-completion.json.tmp"),output.path_join("orbit-completion.json"))!=OK:
   push_error("Cannot replace orbit completion receipt");passed=false

func fixture_sync_snapshot(phase: String, lifecycle) -> Dictionary:
 var weather:=[]
 for path in ["Weather42b/Rain","Weather42b/Snow"]:
  var node=game.get_node_or_null(path)
  if not node is GeometryInstance3D:
   weather.append({"path":path,"exists":is_instance_valid(node),"classified_geometry":false})
   continue
  var bounds: AABB=visual.world_bounds(node.get_aabb(),node.global_transform)
  var row: Dictionary=visual.geometry_state(node,bounds)
  row.bounds_scope="Undeformed native AABB diagnostic; not visible-shader coverage"
  if node is MultiMeshInstance3D and node.multimesh!=null:
   row.instance_count=node.multimesh.instance_count
   row.visible_instance_count=node.multimesh.visible_instance_count
  weather.append(row)
 return {"phase":phase,"ticks_msec":Time.get_ticks_msec(),"process_frame":Engine.get_process_frames(),"physics_frame":Engine.get_physics_frames(),"native_state":current_state(),"weather":weather,"queued_deletions":lifecycle.queued_snapshot(game)}

func paused_fixture_unchanged() -> bool:
 if not is_instance_valid(game): return false
 return game.reference_observation and game.photo_mode and not game.test_frozen and game.anchored and game.airship.velocity==Vector3.ZERO and game.speed==0 and game.throttle==0 and game.airship.global_transform==fixture_pause_state.ship and game.camera.global_transform==fixture_pause_state.camera and game.travelled==fixture_pause_state.travelled and inputs_released()

func run() -> void:
 start_wall=Time.get_ticks_msec()
 if not observation_budget_valid or not settle_budget_valid: push_error("Require one explicit matching600/15 or900/30 observation/settle budget pair");quit(2);return
 if output.is_empty() or not output.is_absolute_path() or DirAccess.dir_exists_absolute(output): push_error("Use new absolute output directory");quit(2);return
 if DirAccess.make_dir_recursive_absolute(output)!=OK: quit(2);return
 if not check(DisplayServer.get_name()!="headless","Actual display required"): return
 if not check(not ProjectSettings.get_setting("physics/3d/run_on_separate_thread",false),"Queries use main-thread physics; threaded mode is not silently overridden"): return
 stage="preparing_source_hashes";progress(true)
 var prep_began:=telemetry.begin("preparation")
 var hash_began:=telemetry.begin("initial_source_hash")
 source_hashes=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("ORBIT61_INPUTS")))
 for path in source_hashes:
  source_hash_completed+=1;telemetry.count("source_files_hashed");progress()
  if not check(FileAccess.get_sha256(path)==source_hashes[path],"Exact frozen input",path): return
  if not within_wall_deadline("initial_source_hash"): return
 telemetry.end("initial_source_hash",hash_began)
 if not check(FileAccess.get_sha256(SCENE)==SCENE_SHA,"Exact saved Game61"): return
 root.size=Vector2i(1180,664);release_all()
 stage="loading_saved_world";progress(true)
 var load_began:=telemetry.begin("scene_load_instantiate")
 var packed: PackedScene=load(SCENE)
 if not check(packed!=null,"Saved scene loaded"): return
 game=packed.instantiate();packed=null;root.add_child(game)
 telemetry.end("scene_load_instantiate",load_began)
 if not within_wall_deadline("after_scene_load_instantiate"): return
 witness=Witness.new();witness.harness=self;witness.process_priority=100000;witness.process_physics_priority=100000;root.add_child(witness)
 RenderingServer.frame_post_draw.connect(after_draw)
 for i in range(3): await process_frame
 await RenderingServer.frame_post_draw
 if not within_wall_deadline("after_initial_process_and_draw"): return
 game.observe_reference("1131")
 # ONLY explicit fixture writes to ship/camera. No direct orbit write anywhere.
 game.airship.position=START
 game.airship.rotation=Vector3(0,atan2(FORWARD.z,-FORWARD.x),0)
 game.heading=game.airship.rotation.y-deg_to_rad(13)
 game.altitude=START.y;game.clearance=START.y-game.world.ground_height(START)
 game.camera.position=native_desired(0)
 game.camera.look_at(native_target())
 game.world.update_focus(START,true)
 if not within_wall_deadline("after_fixture_and_focus_update"): return
 fixture={"classification":"one initial fixture, excluded from all motion; no flight in this first item","state":current_state()}
 fixture_pause_state={"ship":game.airship.global_transform,"camera":game.camera.global_transform,"travelled":game.travelled}
 visual=VISUAL_AUDIT.new()
 visual.telemetry=telemetry;visual.progress_callback=progress
 visual.owner_game=game
 visual.domain=AABB(START-Vector3.ONE*550,Vector3.ONE*1100)
 var lifecycle=FIXTURE_LIFECYCLE.new()
 var sync_began:=Time.get_ticks_msec()
 var drained: Dictionary=await lifecycle.drain(game,paused_fixture_unchanged)
 if not within_wall_deadline("after_fixture_deletion_drain"): return
 fixture.deletion_settle=drained
 if not check(drained.get("ok",false),"Fixture queued deletions completed in unchanged native reference pause",drained): return
 fixture.process_sync=[fixture_sync_snapshot("drain_return_at_process_frame_signal_start",lifecycle)]
 # process_frame is emitted before node _process. Let native game/weather run
 # through the late witness and then post_draw; do not freeze or move weather.
 await witness.processed
 if not within_wall_deadline("fixture_after_late_process"): return
 fixture.process_sync.append(fixture_sync_snapshot("after_late_witness_processed",lifecycle))
 if not check(paused_fixture_unchanged() and Time.get_ticks_msec()-sync_began<FIXTURE_LIFECYCLE.MAX_WALL_MSEC,"Native paused fixture unchanged after full process witness",fixture.process_sync[-1]): return
 await RenderingServer.frame_post_draw
 if not within_wall_deadline("fixture_after_post_draw"): return
 fixture.process_sync.append(fixture_sync_snapshot("after_frame_post_draw_before_inventory",lifecycle))
 if not check(paused_fixture_unchanged() and Time.get_ticks_msec()-sync_began<FIXTURE_LIFECYCLE.MAX_WALL_MSEC,"Native paused fixture unchanged after post_draw",fixture.process_sync[-1]): return
 var final_queue: Dictionary=fixture.process_sync[-1].queued_deletions
 if not check(final_queue.queued_nodes.is_empty() and final_queue.affected_geometry.is_empty(),"Fixture deletion queue remains empty after process and post_draw",final_queue): return
 if not check(game.orbit==Vector2.ZERO and game.zoom==1 and not game.cockpit,"Fresh native orbit defaults"): return
 if not check(game.airship.collision_layer==2,"Own ship collision layer2 present"): return
 base_ship=game.airship.global_transform;base_travelled=game.travelled
 # The near-plane corners are computed from the ACTUAL camera projection.
 var viewport_size: Vector2=game.camera.get_viewport().get_visible_rect().size
 var radius: float=game.camera.near
 for pixel in [Vector2.ZERO,Vector2(viewport_size.x,0),viewport_size,Vector2(0,viewport_size.y)]:
  radius=maxf(radius,game.camera.global_position.distance_to(game.camera.project_position(pixel,game.camera.near)))
 sphere.radius=radius+.02
 # All450m screenshot rays, camera orbit and near-plane fit in this domain.
 var domain:=AABB(START-Vector3.ONE*550,Vector3.ONE*1100)
 telemetry.end("preparation",prep_began)
 stage="preparing_visible_inventory";progress(true)
 var inventory_began:=telemetry.begin("inventory_prepare")
 if not check(visual.prepare(game,domain),"Complete classified visible candidate inventory",visual.failures): return
 if not within_wall_deadline("after_inventory_prepare"): return
 telemetry.end("inventory_prepare",inventory_began)
 inventory_ready=true
 node_added.connect(func(node: Node):
  if inventory_ready and node is GeometryInstance3D: new_geometry.append(node))
 # Allow isolated server bodies to register before querying, while still in
 # native reference pause. No live scene or material is changed for auditing.
 await witness.physics_checked
 await witness.physics_checked
 if not within_wall_deadline("after_inventory_server_registration"): return
 var visual_space: PhysicsDirectSpaceState3D=PhysicsServer3D.space_get_direct_state(visual.space)
 if not check(visual_space!=null,"Isolated visual query space active"): return
 stage="preflight_desired_arc";progress(true)
 var preflight_began:=telemetry.begin("preflight")
 var previous: Vector3=game.camera.global_position
 # Conservative full disk tessellation: each chord grows by its exact arc
 # sagitta, so the true desired arc between .05rad points is not skipped.
 var base_radius:=sphere.radius
 var angle:=0.0
 while angle<4.0-.000001:
  var next:=minf(4.0,angle+STEP_RADIANS)
  var destination:=native_desired(next)
  var orbit_radius: float=Vector2((game.HOME_CAMERA-game.HOME_SHIP).x,(game.HOME_CAMERA-game.HOME_SHIP).z).length()
  sphere.radius=base_radius+orbit_radius*(1-cos((next-angle)*.5))
  var row:=sweep(visual_space,previous,destination,1,true)
  var physical:=sweep(game.get_world_3d().direct_space_state,previous,destination,0xffffffff,false)
  if not within_wall_deadline("preflight_after_segment_queries"): return
  row.physical=physical;row.from_angle=angle;row.to_angle=next
  preflight.append(row);telemetry.count("preflight_segments");progress()
  if not check(row.clear and physical.clear,"Proposed desired orbit arc clears full visible/physical volumes",row): return
  previous=destination;angle=next
 sphere.radius=base_radius
 telemetry.end("preflight",preflight_began)
 # Check the baseline after server-registration waits and before any F2 input.
 if not check(visual.unchanged(true,"before_f2",Engine.get_process_frames()),"Complete frozen inventory unchanged before native F2",visual.failures): return
 for node in new_geometry:
  if not check(is_instance_valid(node),"New geometry survives until pre-input classification"): return
  if not check(visual.accept_distant_new_node(node),"New pre-input geometry remains outside query domain",visual.failures): return
 new_geometry.clear()
 mark("initial_orbit_preflight_complete")
 if failed or not within_wall_deadline("before_native_f2"): return
 last_camera=game.camera.global_position;last_ship=game.airship.global_position;last_frame=-1
 active=true
 if not check(key(KEY_F2,true) and key(KEY_F2,false),"Native F2 exits observation"): return
 if not await wait_settled(): return
 if not await capture("01-default-native-camera"): return
 for index in range(ORBIT_TARGETS.size()):
  angular_index=index;angular_goal=ORBIT_TARGETS[index];stage="continuous_native_orbit";progress(true)
  if not check(mouse_button(true),"Native right mouse pressed"): return
  var goal: float=ORBIT_TARGETS[index]
  while game.orbit.x<goal-.000001 and not failed:
   var amount:=minf(STEP_RADIANS,goal-game.orbit.x)
   if not motion(amount): return
   if not await wait_event_audited(): return
  if not check(mouse_button(false),"Native right mouse released"): return
  stage="settling_capture_goal";progress(true)
  if not await wait_settled(): return
  if not await capture(["02-shore-candidate","03-ship-side-candidate","04-further-side-candidate"][index]): return
 await witness.physics_checked
 await finish()
