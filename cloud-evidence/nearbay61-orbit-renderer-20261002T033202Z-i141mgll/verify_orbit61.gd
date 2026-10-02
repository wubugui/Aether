extends SceneTree
## First bounded item: anchored native right-mouse orbit. NO flight keys.
## Actual camera process segments are queued, then queried during physics.
const SCENE := "res://scenes/candidate61-coast/Game61Coast.tscn"
const SCENE_SHA := "dff06de665e1fa1f6ab74ff3cdf4e91442e1ac322839a37718e799f0d7fa44d8"
const VISUAL_AUDIT = preload("visible_geometry61.gd")
const FIXTURE_LIFECYCLE = preload("fixture_lifecycle61.gd")
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
   harness.delivered.append({"kind":"motion","relative":[event.relative.x,event.relative.y],"right":Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT),"process_frame":Engine.get_process_frames()})
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

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
 call_deferred("run")

func vec(p: Vector3) -> Array:
 return [p.x,p.y,p.z]

func current_state() -> Dictionary:
 if not is_instance_valid(game): return {}
 return {"ship_position":vec(game.airship.global_position),"ship_transform_hex":var_to_bytes(game.airship.global_transform).hex_encode(),"velocity":vec(game.airship.velocity),"camera_position":vec(game.camera.global_position),"camera_transform_hex":var_to_bytes(game.camera.global_transform).hex_encode(),"camera_scale":vec(game.camera.scale),"orbit":[game.orbit.x,game.orbit.y],"heading":game.heading,"speed":game.speed,"throttle":game.throttle,"anchored":game.anchored,"photo_mode":game.photo_mode,"reference_observation":game.reference_observation,"test_frozen":game.test_frozen,"testing":game.testing,"test_override_input":game.test_override_input,"auto_pilot":game.auto_pilot,"docked":game.docked,"travelled":game.travelled,"right_button":Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT),"process_frame":Engine.get_process_frames(),"physics_frame":Engine.get_physics_frames()}

func report(complete: bool) -> void:
 if output.is_empty() or not DirAccess.dir_exists_absolute(output): return
 var result := {"version":"61-anchored-orbit-preparation-v1","complete":complete,"stage":stage,"failed":failed,"first_item_runtime_passed":passed and complete and not failed,"fixture_excluded_from_distance":fixture,"checks":checks,"failures":failures,"events":events,"delivered":delivered,"process_samples":process_samples,"audited_segments":audited,"preflight":preflight,"captures":captures,"near_plane_envelope_radius_m":sphere.radius,"actual_camera_path_m":process_path,"actual_ship_path_after_fixture_m":ship_path,"flight_attempted":false,"short_flight_passed":false,"nearshore_pixel_coverage_passed":false,"manual_normal_material_png_review_required":true,"nearest_ray_scope_m":LOCAL_RAY_METERS,"gui_focus_verified":false,"hardware_gpu_acceptance":false,"reference_visual_acceptance":false,"total_acceptance_passed":false,"scene_saved":false,"state":current_state(),"visual_inventory":visual.rows if visual!=null else [],"visual_inventory_failures":visual.failures if visual!=null else [],"visual_triangle_count":visual.triangle_count if visual!=null else 0,"visual_method":"Actual static indexed surfaces in an isolated physics query space, complete shader/ship animated envelopes. Envelope hits are conservative; no pixel visibility inferred.","source_count":source_hashes.size()}
 var file := FileAccess.open(output.path_join("orbit-report.json.tmp"),FileAccess.WRITE)
 if file==null: push_error("Cannot write orbit report"); return
 file.store_string(JSON.stringify(result,"  "));file.flush();file.close()
 if DirAccess.rename_absolute(output.path_join("orbit-report.json.tmp"),output.path_join("orbit-report.json"))!=OK: push_error("Cannot replace orbit report")

func mark(label: String) -> void:
 stage=label
 print("ORBIT61 ",label)
 report(false)

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
 var event := InputEventMouseButton.new()
 event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
 event.button_mask=MOUSE_BUTTON_MASK_RIGHT if pressed else 0
 event.position=Vector2(root.size)*.5;event.global_position=event.position
 Input.parse_input_event(event);Input.flush_buffered_events()
 events.append({"kind":"right_button","pressed":pressed,"observed":Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT),"process_frame":Engine.get_process_frames()})
 return Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)==pressed

func motion(radians: float) -> bool:
 var before: Vector2=game.orbit
 var event := InputEventMouseMotion.new()
 event.relative=Vector2(-radians/.004,0)
 event.button_mask=MOUSE_BUTTON_MASK_RIGHT
 event.position=Vector2(root.size)*.5;event.global_position=event.position
 Input.parse_input_event(event);Input.flush_buffered_events()
 events.append({"kind":"native_mouse_motion","relative":[event.relative.x,event.relative.y],"before":[before.x,before.y],"after":[game.orbit.x,game.orbit.y],"process_frame":Engine.get_process_frames()})
 return check(absf(game.orbit.x-before.x-radians)<.00001 and absf(game.orbit.y-before.y)<.00001,"Native orbit event applied exact bounded increment")

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
 var query := PhysicsRayQueryParameters3D.create(from,to,1,[game.airship.get_rid()])
 var hit: Dictionary=game.get_world_3d().direct_space_state.intersect_ray(query)
 if hit.is_empty(): return {}
 return {"path":str(hit.collider.get_path()) if hit.collider is Node else str(hit.collider),"position":vec(hit.position),"distance":from.distance_to(hit.position)}

func sweep(space: PhysicsDirectSpaceState3D, a: Vector3, b: Vector3, mask: int, visual_query: bool) -> Dictionary:
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
 return {"clear":clear,"from":vec(a),"to":vec(b),"radius_m":sphere.radius,"mask":mask,"fractions":Array(fractions),"endpoint_hits":hit_rows}

func sample_process(delta: float) -> void:
 if not active or failed or finishing: return
 var frame:=Engine.get_process_frames()
 var position: Vector3=game.camera.global_position
 var ship: Vector3=game.airship.global_position
 if last_frame>=0 and frame!=last_frame+1:
  abort("Missing actual camera process sample",[last_frame,frame]);return
 if Time.get_ticks_msec()-start_wall>MAX_WALL_SECONDS*1000:
  abort("Stationary orbit wall watchdog");return
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
 var row := {"process_frame":frame,"physics_frame":Engine.get_physics_frames(),"dt":delta,"from":vec(last_camera),"to":vec(position),"target":vec(target),"desired":vec(desired),"orbit":[game.orbit.x,game.orbit.y],"camera_transform_hex":var_to_bytes(game.camera.global_transform).hex_encode()}
 process_path+=last_camera.distance_to(position);ship_path+=last_ship.distance_to(ship)
 process_samples.append(row)
 pending.append({"row":row,"from":last_camera,"to":position,"target":target,"desired":desired})
 last_frame=frame;last_camera=position;last_ship=ship

func audit_pending() -> void:
 if not active or failed or finishing or not inventory_ready: return
 if not visual.unchanged(false): abort("Visual candidate inventory changed",visual.failures);return
 for node in new_geometry:
  if is_instance_valid(node) and node is GeometryInstance3D:
   if not visual.accept_distant_new_node(node):
    abort("New visual candidate after inventory; sequence cannot claim coverage",visual.failures);return
 new_geometry.clear()
 var space: PhysicsDirectSpaceState3D=game.get_world_3d().direct_space_state
 var visual_space: PhysicsDirectSpaceState3D=PhysicsServer3D.space_get_direct_state(visual.space)
 if visual_space==null: abort("Isolated visual query space unavailable");return
 while not pending.is_empty():
  var item: Dictionary=pending.pop_front()
  var native_before:=raw_native_ray(item.target,item.desired)
  var native_after:=raw_native_ray(item.target,item.to)
  var physical:=sweep(space,item.from,item.to,0xffffffff,false)
  var drawn:=sweep(visual_space,item.from,item.to,1,true)
  var row := {"process_frame":item.row.process_frame,"physical":physical,"visible_geometry":drawn,"native_desired_blocker":native_before,"native_actual_blocker":native_after}
  audited.append(row)
  if not native_before.is_empty() or not native_after.is_empty() or not physical.clear or not drawn.clear:
   abort("Actual process camera path or native line of sight blocked",row);return
 if not captures.is_empty() and not audited.is_empty():
  var latest: Dictionary=captures[-1]
  if audited[-1].process_frame>=latest.state.process_frame:
   latest.actual_frame_segment_audited=true
   captured=latest.name

func wait_settled() -> bool:
 var began:=Time.get_ticks_msec()
 var stable:=0
 while not failed:
  await witness.processed
  if failed: return false
  if game.camera.global_position.distance_to(native_desired(game.orbit.x))<=SETTLE_METERS: stable+=1
  else: stable=0
  if stable>=2:
   await witness.physics_checked
   if not failed and pending.is_empty(): return true
  if Time.get_ticks_msec()-began>15000:
   abort("Native orbit smoothing did not settle within15s");return false
 return false

func local_rays() -> Array:
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
 return result

func after_draw() -> void:
 if requested_capture.is_empty() or failed or finishing: return
 var name:=requested_capture
 requested_capture=""
 var image: Image=root.get_texture().get_image()
 var path:=output.path_join(name+".png")
 if not check(image!=null and image.save_png(path)==OK,"Actual normal-material image saved",name): return
 captures.append({"name":name,"path":path,"sha256":FileAccess.get_sha256(path),"size":[image.get_width(),image.get_height()],"state":current_state(),"nearest_local_rays":local_rays(),"pixel_review":"not reviewed by renderer harness"})
 mark("captured_pending_frame_audit_"+name)

func capture(name: String) -> bool:
 requested_capture=name
 var began:=Time.get_ticks_msec()
 while captured!=name and not failed:
  await witness.processed
  if Time.get_ticks_msec()-began>20000: abort("Actual capture timeout",name)
 return not failed

func finish() -> void:
 if finishing: return
 finishing=true;active=false;release_all()
 if visual!=null and not failed:
  if not visual.unchanged(true): failed=true;failures.append({"reason":"Final visual buffers changed","details":visual.failures})
 for path in source_hashes:
  if FileAccess.get_sha256(path)!=source_hashes[path]: failed=true;failures.append({"reason":"Frozen input changed","path":path})
 passed=not failed and captures.size()==4 and audited.size()==process_samples.size() and ship_path==0 and inputs_released()
 stage="complete" if passed else "failed_or_incomplete"
 report(true)
 if is_instance_valid(game):
  for i in range(3): await process_frame
  await RenderingServer.frame_post_draw
  game.queue_free()
 if visual!=null: visual.close()
 for i in range(8): await process_frame
 quit(0 if passed else 1)

func paused_fixture_unchanged() -> bool:
 if not is_instance_valid(game): return false
 return game.reference_observation and game.photo_mode and not game.test_frozen and game.anchored and game.airship.velocity==Vector3.ZERO and game.speed==0 and game.throttle==0 and game.airship.global_transform==fixture_pause_state.ship and game.camera.global_transform==fixture_pause_state.camera and game.travelled==fixture_pause_state.travelled and inputs_released()

func run() -> void:
 start_wall=Time.get_ticks_msec()
 if output.is_empty() or not output.is_absolute_path() or DirAccess.dir_exists_absolute(output): push_error("Use new absolute output directory");quit(2);return
 if DirAccess.make_dir_recursive_absolute(output)!=OK: quit(2);return
 if not check(DisplayServer.get_name()!="headless","Actual display required"): return
 if not check(not ProjectSettings.get_setting("physics/3d/run_on_separate_thread",false),"Queries use main-thread physics; threaded mode is not silently overridden"): return
 source_hashes=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("ORBIT61_INPUTS")))
 for path in source_hashes:
  if not check(FileAccess.get_sha256(path)==source_hashes[path],"Exact frozen input",path): return
 if not check(FileAccess.get_sha256(SCENE)==SCENE_SHA,"Exact saved Game61"): return
 root.size=Vector2i(1180,664);release_all()
 var packed: PackedScene=load(SCENE)
 if not check(packed!=null,"Saved scene loaded"): return
 game=packed.instantiate();packed=null;root.add_child(game)
 witness=Witness.new();witness.harness=self;witness.process_priority=100000;witness.process_physics_priority=100000;root.add_child(witness)
 RenderingServer.frame_post_draw.connect(after_draw)
 for i in range(3): await process_frame
 await RenderingServer.frame_post_draw
 game.observe_reference("1131")
 # ONLY explicit fixture writes to ship/camera. No direct orbit write anywhere.
 game.airship.position=START
 game.airship.rotation=Vector3(0,atan2(FORWARD.z,-FORWARD.x),0)
 game.heading=game.airship.rotation.y-deg_to_rad(13)
 game.altitude=START.y;game.clearance=START.y-game.world.ground_height(START)
 game.camera.position=native_desired(0)
 game.camera.look_at(native_target())
 game.world.update_focus(START,true)
 fixture={"classification":"one initial fixture, excluded from all motion; no flight in this first item","state":current_state()}
 fixture_pause_state={"ship":game.airship.global_transform,"camera":game.camera.global_transform,"travelled":game.travelled}
 var lifecycle=FIXTURE_LIFECYCLE.new()
 var drained: Dictionary=await lifecycle.drain(game,paused_fixture_unchanged)
 fixture.deletion_settle=drained
 if not check(drained.get("ok",false),"Fixture queued deletions completed in unchanged native reference pause",drained): return
 if not check(game.orbit==Vector2.ZERO and game.zoom==1 and not game.cockpit,"Fresh native orbit defaults"): return
 if not check(game.airship.collision_layer==2,"Own ship collision layer2 present"): return
 base_ship=game.airship.global_transform;base_travelled=game.travelled
 # The near-plane corners are computed from the ACTUAL camera projection.
 var viewport_size: Vector2=game.camera.get_viewport().get_visible_rect().size
 var radius: float=game.camera.near
 for pixel in [Vector2.ZERO,Vector2(viewport_size.x,0),viewport_size,Vector2(0,viewport_size.y)]:
  radius=maxf(radius,game.camera.global_position.distance_to(game.camera.project_position(pixel,game.camera.near)))
 sphere.radius=radius+.02
 visual=VISUAL_AUDIT.new()
 # All450m screenshot rays, camera orbit and near-plane fit in this domain.
 var domain:=AABB(START-Vector3.ONE*550,Vector3.ONE*1100)
 if not check(visual.prepare(game,domain),"Complete classified visible candidate inventory",visual.failures): return
 inventory_ready=true
 node_added.connect(func(node: Node):
  if inventory_ready and node is GeometryInstance3D: new_geometry.append(node))
 # Allow isolated server bodies to register before querying, while still in
 # native reference pause. No live scene or material is changed for auditing.
 await witness.physics_checked
 await witness.physics_checked
 var visual_space: PhysicsDirectSpaceState3D=PhysicsServer3D.space_get_direct_state(visual.space)
 if not check(visual_space!=null,"Isolated visual query space active"): return
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
  row.physical=physical;row.from_angle=angle;row.to_angle=next
  preflight.append(row)
  if not check(row.clear and physical.clear,"Proposed desired orbit arc clears full visible/physical volumes",row): return
  previous=destination;angle=next
 sphere.radius=base_radius
 # Check the baseline after server-registration waits and before any F2 input.
 if not check(visual.unchanged(true),"Complete frozen inventory unchanged before native F2",visual.failures): return
 for node in new_geometry:
  if not check(is_instance_valid(node),"New geometry survives until pre-input classification"): return
  if not check(visual.accept_distant_new_node(node),"New pre-input geometry remains outside query domain",visual.failures): return
 new_geometry.clear()
 mark("initial_orbit_preflight_complete")
 last_camera=game.camera.global_position;last_ship=game.airship.global_position;last_frame=-1
 active=true
 if not check(key(KEY_F2,true) and key(KEY_F2,false),"Native F2 exits observation"): return
 if not await wait_settled(): return
 if not await capture("01-default-native-camera"): return
 for index in range(ORBIT_TARGETS.size()):
  if not check(mouse_button(true),"Native right mouse pressed"): return
  var goal: float=ORBIT_TARGETS[index]
  while game.orbit.x<goal-.000001 and not failed:
   var amount:=minf(STEP_RADIANS,goal-game.orbit.x)
   if not motion(amount): return
   if not await wait_settled(): return
  if not check(mouse_button(false),"Native right mouse released"): return
  if not await wait_settled(): return
  if not await capture(["02-shore-candidate","03-ship-side-candidate","04-further-side-candidate"][index]): return
 await witness.physics_checked
 await finish()
