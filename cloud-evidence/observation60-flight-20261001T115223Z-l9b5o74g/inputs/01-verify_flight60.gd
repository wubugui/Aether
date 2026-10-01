extends SceneTree
## Scoped player-input evidence. Loads one ordinary scene; never saves a scene.
## Physics events, including timed key release, run after the actual game callback.
const SCENE := "res://scenes/candidate60-observation/Game60Observation.tscn"
const SHA := "8fcb0d24d503133a7e6ba29645291a73314c88b40ab447e0802937f1c802ac45"
const ROOT := "/workspace/scratch/a29d03198654/Aether"
const INTAKE := ROOT + "/cloud-evidence/free-flight51b-readonly-plan/source-intake.json"
const BUILD := "res://scenes/candidate51b/build-report-51b.json"
const AUDIT := ROOT + "/cloud-evidence/reflection51b-motion-20261001T041545Z-WCymsr/images/reflection-motion-report.json"
const FULL_AUDIT := ROOT + "/cloud-evidence/reflection51b-verify-full-20261001T032554Z-975juK/images/report.json"
const LOCKED_REPORTS := {
	INTAKE: "84ef75d0f2a35e10a4f1347eadc5d5c104659a5eb61dce323a88e3b4cd4f2534",
	BUILD: "8c22fe4b9074cdfcb8c64831f7e3281569568d423f74bdf7eb1495fb9d593f73",
	AUDIT: "a3c8bdbc0e2cfad0bd41588b414c948b1f71aeab0e0617bc747d89646769131a",
	FULL_AUDIT: "9affd0c22226f5a208337ea4fd239f07e7b3a2fc13e478ab62d10175db56db7d"
}
const KEYS := [KEY_W, KEY_S, KEY_A, KEY_D, KEY_E, KEY_Q, KEY_SHIFT, KEY_SPACE, KEY_F2]
const CORRIDOR_METERS := 25.0
const MAX_METERS := 20.0
const MAX_SIM_SECONDS := 5.0
const POWER_SECONDS := 0.75
const COAST_SECONDS := 0.50
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
		"camera_is_current": game.camera.is_current(), "physics_frame": Engine.get_physics_frames(),
		"time_scale": Engine.time_scale, "flight_sim_seconds": sim_seconds, "phase": flight_phase}

func mark(label: String, details: Variant = null) -> void:
	stage = label
	milestones.append({"stage": label, "wall_ms": Time.get_ticks_msec(), "flight_sim_seconds": sim_seconds, "details": details})
	print("FLIGHT60 STAGE ", label)
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
	if not require(FileAccess.get_sha256(ROOT + "/cloud-evidence/coast56-verify-20261001T101445Z-xvmw5o3r/verify-report56.json")=="bd3274627132a3b45157772b58717df21fe0d4990585b444f107cb1b1af49eb2", "Pinned56 actual native verification verify-report56.json"):return false
	if not require(FileAccess.get_sha256(ROOT + "/cloud-evidence/coast56-verify-20261001T101445Z-xvmw5o3r/wrapper-report.json")=="7cba95d8ff58a49ab36692a2469890336f20a05ebd9b70d4f3cb6491900ace46", "Pinned56 actual native verification wrapper-report.json"):return false
	var coast_gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(ROOT + "/cloud-evidence/coast56-verify-20261001T101445Z-xvmw5o3r/verify-report56.json"))
	if not require(coast_gate.get("passed",false) and coast_gate.get("strict_saved_readback",false) and coast_gate.get("live_support_cache_collision",false),"Fresh56 native and actual collision/cache gates passed"):return false
	var scoped_path := OS.get_environment("OBSERVATION60_SCOPE")
	var scoped: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(scoped_path))
	if not require(scoped.get("passed",false), "Fresh60 inherited scope external gate passed"): return false
	var scope_inputs: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(scoped_path.get_base_dir().path_join("input-sha256.json")))
	for path in scope_inputs:
		if not require(FileAccess.get_sha256(path)==scope_inputs[path], "60 scope exact source "+path):return false
		source_hashes[path]=scope_inputs[path]
	if not require(FileAccess.get_sha256(SCENE)==SHA,"Pinned independent60 observation scene"):return false
	for path in LOCKED_REPORTS:
		if not require(FileAccess.get_sha256(path) == LOCKED_REPORTS[path], "Pinned evidence identity " + path): return false
	var intake: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(INTAKE))
	var build: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BUILD))
	var audit: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AUDIT))
	if not require(audit.candidate_sha256 == "b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1" and audit.limited_reflection_motion_runtime_passed and not audit.total_acceptance_passed,
		"Reuse51b reflection dependency audit plus fresh55 scoped inheritance proof; its open failures remain open"): return false
	for relative in intake.sources:
		source_hashes["res://" + relative] = intake.sources[relative]
	for asset in build.independent_assets: source_hashes[asset.path] = asset.sha256
	source_hashes["res://scripts/lake_reflection51b.gd"] = build.controller_source_sha256
	source_hashes[BUILD] = LOCKED_REPORTS[BUILD]
	for path in source_hashes:
		var actual := FileAccess.get_sha256(path)
		source_checks.append({"path": path, "expected": source_hashes[path], "actual": actual})
		if not require(actual == source_hashes[path], "Exact current source " + path): return false
	return true

func collider_hits(hits: Array) -> Array:
	var rows := []
	for hit in hits:
		var object = hit.get("collider")
		rows.append({"path": str(object.get_path()) if object is Node else str(object), "shape_index": hit.get("shape", -1), "collider_id": hit.get("collider_id", 0)})
	return rows

func query_volume(shape: Shape3D, pose: Transform3D, motion: Vector3, label: String) -> Dictionary:
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = pose
	query.motion = motion
	query.margin = game.airship.safe_margin
	query.collision_mask = game.airship.collision_mask
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
	var result := {"label": label, "shape_type": shape.get_class(), "transform": str(pose), "motion": vec(motion), "start_hits": collider_hits(overlaps), "end_hits": collider_hits(end_overlaps), "cast_fractions": Array(fractions), "clear": clear}
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
	var box := BoxShape3D.new()
	box.size = bounds.size
	shapes.append({"label": "all_visible_mesh_bounds_plus_0.5m_each", "shape": box, "local_transform": Transform3D(Basis.IDENTITY, bounds.get_center())})
	var rows := []
	var clear := true
	for yaw in [0.0, -0.20, 0.20]:
		for lift in [0.0, 3.0]:
			var pose := Transform3D(Basis(Vector3.UP, yaw) * ship.global_basis, ship.global_position + Vector3.UP * lift)
			for item in shapes:
				var row := query_volume(item.shape, pose * item.local_transform, forward * CORRIDOR_METERS, item.label + " yaw=" + str(yaw) + " lift=" + str(lift))
				rows.append(row)
				clear = clear and row.clear
	var motion_result := KinematicCollision3D.new()
	var body_blocked := ship.test_move(ship.global_transform, forward * CORRIDOR_METERS, motion_result, ship.safe_margin, true, 8)
	var combined_hits := []
	for index in range(motion_result.get_collision_count()):
		var collider = motion_result.get_collider(index)
		combined_hits.append({"path": str(collider.get_path()) if collider is Node else str(collider), "point": vec(motion_result.get_position(index)), "normal": vec(motion_result.get_normal(index))})
	var terrain_shape_classes := {}
	for node in game.world.find_children("*", "CollisionShape3D", true, false):
		if node.disabled or node.shape == null: continue
		var kind: String = node.shape.get_class()
		terrain_shape_classes[kind] = int(terrain_shape_classes.get(kind, 0)) + 1
	preflight = {"distance_m": CORRIDOR_METERS, "origin": vec(origin), "forward": vec(forward), "body_shapes": collision_shapes,
		"visible_mesh_count": visible_count, "full_revolution_propeller_mesh_count": propeller_mesh_count,
		"padded_visible_envelope_local": str(bounds), "query_mask": ship.collision_mask,
		"active_world_shape_classes": terrain_shape_classes, "queries": rows, "combined_body_test_move_blocked": body_blocked,
		"combined_body_contacts": combined_hits, "passed": clear and not body_blocked,
		"method": "Actual PhysicsDirectSpaceState3D intersects/casts and CharacterBody3D.test_move against active scene solids; bounding box is only the conservative ship query shape, not a substitute for world triangles. Extra yaw/lift sweeps are clearance checks, not control-flight evidence."}
	mark("preflight_complete", preflight.passed)
	return require(clear and not body_blocked and int(terrain_shape_classes.get("ConcavePolygonShape3D", 0)) > 0,
		"Full body and visible-envelope25m corridor clears actual loaded triangle solids", preflight)

func capture_after_draw() -> void:
	if pending_capture.is_empty() or failed or finished: return
	var label := pending_capture
	pending_capture = ""
	var snapshot := state()
	if label == "02-moving" and not require(game.speed > 0.1 and not game.test_frozen and sim_seconds > 0, "Moving screenshot records live physics motion", snapshot): return
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

func observe_tick(delta: float) -> void:
	if not flight_active or failed or finished: return
	sim_seconds += delta
	var position: Vector3 = game.airship.global_position
	var step: Vector3 = position - previous_position
	previous_position = position
	path_metres += step.length()
	peak_speed = maxf(peak_speed, game.speed)
	var expected_step: Vector3 = game.airship.velocity * delta
	var step_error := step.distance_to(expected_step)
	max_step_velocity_error = maxf(max_step_velocity_error, step_error)
	var sample := state()
	sample["dt"] = delta
	sample["step_m"] = vec(step)
	sample["step_velocity_error_m"] = step_error
	sample["distance_from_start_m"] = position.distance_to(origin)
	sample["path_m"] = path_metres
	samples.append(sample)
	if sim_seconds > MAX_SIM_SECONDS or position.distance_to(origin) > MAX_METERS or path_metres > MAX_METERS:
		abort_test("20m displacement/path cap or5s simulation watchdog", sample); return
	if game.airship.get_slide_collision_count() > 0 or game.health < float(flight_start.health) - 0.000001 or game.shield < float(flight_start.shield) - 0.000001:
		abort_test("Collision or damage during player-control flight", sample); return
	if not is_equal_approx(Engine.time_scale, 1.0) or game.testing or game.test_override_input or game.test_frozen or game.photo_mode or game.reference_observation or game.auto_pilot or game.docked:
		abort_test("Normal actual player-control loop changed or was bypassed", sample); return
	if not game.is_physics_processing() or not game.can_process():
		abort_test("Actual game physics callback disabled or paused", sample); return
	for code in KEYS:
		var expected_pressed: bool = code == KEY_W and flight_phase == "power"
		if Input.is_physical_key_pressed(code) != expected_pressed:
			abort_test("Unexpected or stuck physical key", {"key": OS.get_keycode_string(code), "expected_pressed": expected_pressed, "state": sample}); return
	if step_error > 0.05 or absf(game.speed - Vector2(game.airship.velocity.x, game.airship.velocity.z).length()) > 0.001:
		abort_test("Actual displacement/velocity mismatch or unexpected teleport/rescue", sample); return
	if absf(position.y - origin.y) > 0.1 or absf(float(game.heading) - float(flight_start.heading)) > 0.001:
		abort_test("Uncommanded altitude or heading change", sample); return
	if flight_phase == "power" and sim_seconds >= POWER_SECONDS - 0.000001:
		if not require(key(KEY_W, false), "Physical W release delivered"): return
		power_end = state()
		if not require(game.speed > 5.0 and absf(game.throttle - POWER_SECONDS * 0.34) < 0.015 and not game.anchored,
			"Existing W polling accelerates and releases anchor", power_end): return
		flight_phase = "coast"
		phase_start = sim_seconds
		mark("W_released_coasting", power_end)
		request_capture("02-moving")
	elif flight_phase == "coast" and sim_seconds - phase_start >= COAST_SECONDS - 0.000001:
		coast_end = state()
		if not require(absf(game.throttle - float(power_end.throttle)) < 0.00001 and game.speed > float(power_end.speed) + 1,
			"Released W retains throttle and actual acceleration", coast_end): return
		if not require(key(KEY_SPACE, true) and key(KEY_SPACE, false), "Physical Space press and release delivered"): return
		if not require(game.anchored and game.throttle == 0, "Existing unhandled Space input engages braking and resets throttle", state()): return
		flight_phase = "braking"
		phase_start = sim_seconds
		mark("Space_braking")
	elif flight_phase == "braking":
		if game.speed < 0.1 and absf(game.vertical_speed) < 0.1:
			if stable_seconds == 0: stable_origin = position
			stable_seconds += delta
			if position.distance_to(stable_origin) > 0.02:
				abort_test("Position drift during requested stable stop", sample); return
			if stable_seconds >= STABLE_SECONDS - 0.000001:
				stop_state = state()
				flight_phase = "stopped"
				mark("stable_stop", stop_state)
				request_capture("03-stopped")
		else: stable_seconds = 0.0
	elif flight_phase == "stopped" and capture_completed == "03-stopped":
		flight_active = false
		call_deferred("finish")

func write_report(complete: bool) -> void:
	if output.is_empty(): return
	var report := {"version": "60-native-cloud-observation-flight-v1", "stage": stage, "complete": complete,
		"actual_player_input_flight_passed": complete and not failed, "candidate": SCENE, "candidate_sha256": SHA,
		"prior_matching_motion_audit": AUDIT, "prior_motion_audit_sha256": LOCKED_REPORTS[AUDIT],
		"prior_full_audit": FULL_AUDIT, "prior_full_audit_sha256": LOCKED_REPORTS[FULL_AUDIT],
		"renderer": renderer, "checks": checks, "failures": failures, "milestones": milestones, "boot": boot,
		"navigation_teleport": navigation, "preflight": preflight, "source_checks": source_checks,
		"input_events": input_events, "input_deliveries": input_deliveries, "samples": samples,
		"captures": captures, "flight_start": flight_start, "power_end": power_end, "coast_end": coast_end, "stop": stop_state,
		"sim_seconds": sim_seconds, "path_m": path_metres, "peak_speed_mps": peak_speed,
		"max_displacement_velocity_error_m": max_step_velocity_error, "all_keys_released": keys_released(),
		"failure_freeze_used": failed and is_instance_valid(game) and game.test_frozen,
		"time_scale": Engine.time_scale, "distance_cap_m": MAX_METERS, "simulation_watchdog_seconds": MAX_SIM_SECONDS,
		"gui_keyboard_focus_verified": false, "full_route_flight_passed": false, "hardware_gpu_acceptance": false,
		"conversion_pixel_gate_passed": false, "known1344_conversion_difference_pixels": 2,
		"requested350m_motion_passed": false, "total_acceptance_passed": false, "scene_saved": false,
		"scope": "One normally booted inherited saved60 coast/lake/cloud-observation scene with exact scoped55/53west base. Candidate60 observe_reference1216 is explicitly a navigation teleport; subsequent motion uses physical Input.parse_input_event W/F2/Space, unchanged player physics and move_and_slide. Full-body and padded visual25m cast is against actual active solids. No test override, transform-driven flight, full verifier rerun, GUI keyboard-focus or hardware/full-route claim."}
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

func finish() -> void:
	if finished: return
	flight_active = false
	release_keys()
	if not failed:
		require(captures.size() == 3, "Three actual start/moving/stopped images recorded", captures.size())
		require(sim_seconds < MAX_SIM_SECONDS and path_metres > 5 and path_metres < MAX_METERS,
			"Actual flight remains within bounded prechecked corridor", {"seconds": sim_seconds, "path_m": path_metres})
		require(game.fuel < float(flight_start.fuel), "Actual forward flight consumes fuel", {"start": flight_start.fuel, "end": game.fuel})
		require(game.airship.global_position.distance_to(origin) > 5 and (game.airship.global_position - origin).normalized().dot(forward) > 0.99,
			"Actual body displacement follows modeled ship nose", state())
		require(game.anchored and game.throttle == 0 and game.speed < 0.1 and stable_seconds >= STABLE_SECONDS - 0.000001 and keys_released(),
			"Physical Space reaches a stable stop with every key released", state())
		var controller = game.get_node("World/LakeReflection51")
		require(game.camera.is_current() and controller.main_camera == game.camera and controller.viewport.world_3d == game.get_world_3d() and controller.effective_reflection,
			"Follow camera and live reflection remain bound to actual scene")
		var camera_start := Vector3(flight_start.camera_position[0], flight_start.camera_position[1], flight_start.camera_position[2])
		require(game.camera.global_position.distance_to(camera_start) > 1, "Existing following camera moves with actual flight")
	for path in source_hashes:
		if FileAccess.get_sha256(path) != source_hashes[path]: require(false, "Source changed during isolated run: " + path)
	if not failed: require(true, "All locked gameplay/scene/material sources remain unchanged")
	finished = true
	stage = "failed" if failed else "complete"
	write_report(true)
	print("ACTUAL PLAYER INPUT FLIGHT60 COMPLETE passed=", not failed, " total_acceptance=false")
	if is_instance_valid(game): game.queue_free()
	await process_frame
	await process_frame
	quit(1 if failed else 0)

func run() -> void:
	if output.is_empty() or not output.is_absolute_path() or DirAccess.dir_exists_absolute(output):
		push_error("Use a new absolute --output-dir"); quit(2); return
	if DirAccess.make_dir_recursive_absolute(output) != OK: quit(2); return
	mark("before_identity")
	if not require(DisplayServer.get_name() != "headless", "Renderer required for actual three-image flight evidence"): return
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
	if not require(packed != null, "Exact60 observation inherited packed scene loaded"): return
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
	boot["reflection"] = {"camera_is_current": game.camera.is_current(), "bound_to_main_camera": boot_reflection.main_camera == game.camera,
		"shares_world": boot_reflection.viewport.world_3d == game.get_world_3d(), "effective": boot_reflection.effective_reflection,
		"clip_enabled": boot_reflection.clip_enabled, "requested": boot_reflection.reflection_enabled}
	if not require(not game.testing and not game.test_override_input and not game.test_frozen and not game.photo_mode and not game.reference_observation and not game.auto_pilot and game.anchored,
		"Ordinary ready state uses current gameplay without test/observation override", boot): return
	if not require(game.airship.global_position.distance_to(home_position) < 0.01 and game.speed == 0 and boot.hud_present and boot.physics_processing,
		"Ordinary boot has live HUD/physics and anchored no-drift start", boot): return
	mark("boot_verified")
	var before_navigation := state()
	game.observe_reference("1216")
	origin = game.airship.global_position
	forward = -game.airship.global_basis.x.normalized()
	navigation = {"operation": "existing observe_reference1216", "classification": "explicit navigation teleport; never counted as flight", "before": before_navigation, "after": state()}
	game.world.update_focus(origin + forward * CORRIDOR_METERS * 0.5, true)
	await wait_seconds(0.05)
	if failed: return
	mark("navigation1216_settled", navigation)
	if not require(game.photo_mode and game.reference_observation and game.anchored and game.airship.velocity == Vector3.ZERO, "Existing observation pauses player flight before preflight"): return
	if not check_corridor(): return
	var observation_camera: Vector3 = game.camera.global_position
	var before_f2_basis: Basis = game.airship.global_basis
	if not require(key(KEY_F2, true) and key(KEY_F2, false), "Physical F2 press and release delivered"): return
	await wait_seconds(0.25)
	if failed: return
	if not require(not game.photo_mode and not game.reference_observation and game.camera.global_position.distance_to(observation_camera) > 1,
		"Existing F2 unhandled-input path exits both observation flags and resumes follow camera", state()): return
	if not require(game.airship.global_basis.is_equal_approx(before_f2_basis), "F2 resumes synchronized saved55 heading without a turn", {"before":str(before_f2_basis),"after":str(game.airship.global_basis)}):return
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
