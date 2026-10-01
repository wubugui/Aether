extends SceneTree
## Runtime-only A/B/A2 composition study in one saved53west world. No flight.
const ROOT := "/workspace/scratch/a29d03198654/Aether"
const SCENE := "res://scenes/candidate53d-west/Game53dWest.tscn"
const SHA := "6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18"
const BUILD := "res://scenes/candidate53d-west/build-report-west53.json"
const MANIFEST := ROOT + "/source-assets/lake-rim53/integration-west53/integration-manifest.json"
const PREP := ROOT + "/source-assets/near-ship53west/"
const AUDIT := ROOT + "/cloud-evidence/rim53d-west-verify-v2-20261001T064631Z-OrTCQY/verify-report-west53-v2.json"
const LOCKS := {
	SCENE: SHA,
	BUILD: "d21b7ba86b781431fd08cfa5bd5857760e8d888818a0e741ece092010c92cfa0",
	MANIFEST: "9bca63c34b214a7a3176a0a139c1a35cea946b88aea10e99385956387f021a7d",
	AUDIT: "89ada2a6dffbcadb1a7482a40ae64a4e204079937048204ced7a30bdf54fce7a",
	PREP + "reference-measurements.json": "3a899488152acf3d3602f75e098fdecd9a9ee45278aa83be055bfa07052c19fc"
}
var game
var controller
var output := ""
var source_hashes := {}
var checks := []
var failures := []
var captures := []
var comparisons := []
var selections := []
var stage := "before_load"
var original_ship: Transform3D
var original_camera: Transform3D
var original_fov := 0.0
var original_scale := Vector3.ONE
var have_original := false
var snapshot_before := ""
var collision_before := ""
var local_points := PackedVector3Array()
var visual_box := AABB()
var native_shapes := []
var mesh_count := 0
var propeller_mesh_count := 0
var measurements := {}

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output = arg.trim_prefix("--output-dir=")
	call_deferred("run")

func v3(v: Vector3) -> Array: return [v.x, v.y, v.z]
func v2(v: Vector2) -> Array: return [v.x, v.y]
func check(ok: bool, name: String, details: Variant = null) -> bool:
	checks.append({"passed": ok, "name": name, "details": details})
	print("PASS " if ok else "FAIL ", name)
	if not ok: failures.append({"name": name, "details": details})
	return ok

func frames(n: int) -> void:
	for i in range(n): await process_frame

func checkpoint(label: String) -> void:
	stage = label
	print("NEAR_SHIP53WEST STAGE ", stage)
	write_report(false)

func digest(value: Variant) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(var_to_bytes(value))
	return h.finish().hex_encode()

func bytes_digest(value: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(value)
	return h.finish().hex_encode()

func freeze(n: Node) -> void:
	n.set_process(false)
	n.set_physics_process(false)
	n.set_process_input(false)
	n.set_process_unhandled_input(false)
	if n is AnimationPlayer: n.pause()
	if n is Timer: n.paused = true
	for child in n.get_children(): freeze(child)

func invariants(exclude_ship_transform: bool) -> String:
	# No geometry buffer or material is edited. Keep exact transforms, resource
	# identities, visibility, collision modes and environment properties stable.
	var rows := []
	for node in game.find_children("*", "", true, false):
		var row := {"path": str(game.get_path_to(node)), "process_mode": node.process_mode,
			"process": node.is_processing(), "physics": node.is_physics_processing()}
		if node is Node3D:
			if node != game.airship or not exclude_ship_transform: row["transform"] = node.transform
			row["visible"] = node.visible
		if node is MeshInstance3D:
			row["mesh"] = node.mesh.get_instance_id() if node.mesh else 0
			row["override"] = node.material_override.get_instance_id() if node.material_override else 0
		if node is MultiMeshInstance3D:
			row["multimesh"] = node.multimesh.get_instance_id() if node.multimesh else 0
			if node.multimesh: row["buffer_sha256"] = digest(node.multimesh.buffer)
		if node is CollisionObject3D:
			row["collision"] = [node.collision_layer, node.collision_mask, node.disable_mode, str(node.get_rid())]
		if node is CollisionShape3D: row["shape"] = [node.disabled, node.shape.get_instance_id() if node.shape else 0]
		if node is Camera3D: row["camera"] = [node.fov, node.near, node.far, node.keep_aspect, node.cull_mask, node.projection, node.h_offset, node.v_offset]
		if node is WorldEnvironment and node.environment:
			var env := {}
			for property in node.environment.get_property_list():
				if int(property.usage) & PROPERTY_USAGE_STORAGE: env[property.name] = node.environment.get(property.name)
			row["environment"] = env
		rows.append(row)
	return digest(rows)

func collisions() -> String:
	var rows := []
	for node in game.find_children("*", "CollisionObject3D", true, false):
		rows.append([str(game.get_path_to(node)), node.process_mode, node.disable_mode, node.can_process(), node.collision_layer, node.collision_mask, str(node.get_rid())])
	return digest(rows)

func collect_ship() -> bool:
	local_points.clear()
	native_shapes.clear()
	mesh_count = 0
	propeller_mesh_count = 0
	var first := true
	var inverse: Transform3D = game.airship.global_transform.affine_inverse()
	for mesh in game.airship.find_children("*", "MeshInstance3D", true, false):
		if mesh.mesh == null or not mesh.is_visible_in_tree(): continue
		mesh_count += 1
		var local: Transform3D = inverse * mesh.global_transform
		# Actual mesh vertices drive projection, while a padded enclosing box
		# independently drives conservative physics clearance.
		for surface in range(mesh.mesh.get_surface_count()):
			var arrays: Array = mesh.mesh.surface_get_arrays(surface)
			if arrays.is_empty(): continue
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			for vertex in vertices: local_points.append(local * vertex)
		var padded: AABB = mesh.get_aabb().grow(0.5)
		for corner in range(8):
			var point: Vector3 = local * padded.get_endpoint(corner)
			if first: visual_box = AABB(point, Vector3.ZERO); first = false
			else: visual_box = visual_box.expand(point)
		if game.propeller.is_ancestor_of(mesh):
			propeller_mesh_count += 1
			var to_prop: Transform3D = game.propeller.global_transform.affine_inverse() * mesh.global_transform
			var to_ship: Transform3D = inverse * game.propeller.global_transform
			var radius := 0.0
			var min_x := INF
			var max_x := -INF
			for corner in range(8):
				var point: Vector3 = to_prop * padded.get_endpoint(corner)
				radius = maxf(radius, Vector2(point.y, point.z).length())
				min_x = minf(min_x, point.x)
				max_x = maxf(max_x, point.x)
			var revolution := AABB(Vector3(min_x, -radius, -radius), Vector3(max_x - min_x, 2 * radius, 2 * radius))
			for corner in range(8): visual_box = visual_box.expand(to_ship * revolution.get_endpoint(corner))
	for shape in game.airship.find_children("*", "CollisionShape3D", true, false):
		if not shape.disabled and shape.shape:
			native_shapes.append({"name": str(shape.name), "shape": shape.shape, "local": inverse * shape.global_transform})
	return check(mesh_count > 0 and local_points.size() > 0 and native_shapes.size() == 2, "Actual visible geometry and two body shapes collected", {"mesh_count": mesh_count, "vertex_count": local_points.size(), "full_revolution_propeller_meshes": propeller_mesh_count, "conservative_bounds": str(visual_box)})

func projection(pose: Transform3D) -> Dictionary:
	var low := Vector2(INF, INF)
	var high := Vector2(-INF, -INF)
	var front := true
	var transform: Transform3D = game.camera.get_camera_transform().affine_inverse() * pose
	var optical: Projection = game.camera.get_camera_projection()
	for vertex in local_points:
		var point := transform * vertex
		var clip := optical * Vector4(point.x, point.y, point.z, 1)
		if clip.w <= game.camera.near: front = false; continue
		var uv := Vector2(clip.x / clip.w * 0.5 + 0.5, 0.5 - clip.y / clip.w * 0.5)
		low = low.min(uv)
		high = high.max(uv)
	return {"min": v2(low), "max": v2(high), "center": v2((low + high) * 0.5), "size": v2(high - low), "all_forward": front,
		"inside": front and low.x > 0 and low.y > 0 and high.x < 1 and high.y < 1}

func fit_pose(depth: float, yaw: float, center: Vector2) -> Transform3D:
	var size: Vector2 = root.get_visible_rect().size
	var basis := Basis(Vector3.UP, yaw).scaled(original_scale)
	var pose := Transform3D(basis, game.camera.project_position(center * size, depth) - basis * visual_box.get_center())
	for i in range(3):
		var bounds := projection(pose)
		var actual := Vector2(bounds.center[0], bounds.center[1])
		pose.origin += game.camera.project_position(center * size, depth) - game.camera.project_position(actual * size, depth)
	return pose

func hits(rows: Array) -> Array:
	var result := []
	for row in rows:
		var body = row.get("collider")
		result.append({"collider": str(body.get_path()) if body is Node else str(body), "shape_index": row.get("shape", -1)})
	return result

func clearance(pose: Transform3D) -> Dictionary:
	var space: PhysicsDirectSpaceState3D = game.get_world_3d().direct_space_state
	var volumes: Array = native_shapes.duplicate()
	var box := BoxShape3D.new()
	box.size = visual_box.size
	volumes.append({"name": "all_visible_meshes_plus_padding_and_propeller_revolution", "shape": box, "local": Transform3D(Basis.IDENTITY, visual_box.get_center())})
	var rows := []
	var clear := true
	var min_drop := INF
	for mask in [int(game.airship.collision_mask), 5]:
		for volume in volumes:
			var q := PhysicsShapeQueryParameters3D.new()
			q.shape = volume.shape
			q.transform = pose * volume.local
			q.margin = game.airship.safe_margin
			q.collision_mask = mask
			q.exclude = [game.airship.get_rid()]
			var overlap := space.intersect_shape(q, 32)
			q.motion = Vector3.DOWN * 500.0
			var fraction := space.cast_motion(q)
			var drop: float = fraction[0] * 500.0 if fraction.size() == 2 else -1.0
			var supported := fraction.size() == 2 and fraction[0] < 1.0
			var valid := overlap.is_empty() and supported and drop >= 0.25
			clear = clear and valid
			min_drop = minf(min_drop, drop)
			rows.append({"volume": volume.name, "shape_type": volume.shape.get_class(), "mask": mask, "overlaps": hits(overlap), "downward_safe_fraction": Array(fraction), "conservative_vertical_clearance_m": drop, "actual_solid_found_below_500m": supported, "passed": valid})
	var world_box: AABB = pose * visual_box
	var support := []
	for offset in [Vector2(0, 0), Vector2(-0.5, -0.5), Vector2(-0.5, 0.5), Vector2(0.5, -0.5), Vector2(0.5, 0.5)]:
		var start: Vector3 = world_box.get_center() + Vector3(offset.x * world_box.size.x, 0, offset.y * world_box.size.z)
		start.y = world_box.position.y + 0.1
		var ray := PhysicsRayQueryParameters3D.create(start, start + Vector3.DOWN * 500, 5, [game.airship.get_rid()])
		var hit := space.intersect_ray(ray)
		support.append({"ray_from": v3(start), "hit": not hit.is_empty(), "support_y": hit.position.y if not hit.is_empty() else null, "bottom_gap_m": world_box.position.y - hit.position.y if not hit.is_empty() else null, "collider": str(hit.collider.get_path()) if not hit.is_empty() else "none"})
	var sight_hits := []
	for i in range(8):
		var endpoint: Vector3 = pose * visual_box.get_endpoint(i)
		var ray := PhysicsRayQueryParameters3D.create(game.camera.global_position, endpoint, 5, [game.airship.get_rid()])
		var hit := space.intersect_ray(ray)
		if not hit.is_empty(): sight_hits.append({"corner": i, "collider": str(hit.collider.get_path()), "position": v3(hit.position)})
	var local_camera: Vector3 = pose.affine_inverse() * game.camera.global_position
	var nearest_local := local_camera.clamp(visual_box.position, visual_box.end)
	var camera_gap: float = game.camera.global_position.distance_to(pose * nearest_local)
	clear = clear and sight_hits.is_empty() and camera_gap > maxf(2.0, game.camera.near + 0.5)
	return {"passed": clear, "volumes": rows, "minimum_conservative_vertical_clearance_m": min_drop,
		"footprint_support_rays": support, "silhouette_sightline_hits": sight_hits, "camera_to_padded_envelope_m": camera_gap,
		"camera_to_ship_origin_m": game.camera.global_position.distance_to(pose.origin), "world_visible_box": str(world_box),
		"scope": "Actual intersect_shape and whole-volume downward casts against loaded native solids, masks1/5; five support rays and eight silhouette sightlines. This proves pose clearance/support distances, not travel from A to B or flown control."}

func choose_pose(reference: String) -> Dictionary:
	var target: Dictionary = measurements[reference]
	var desired_center := Vector2(target.ship_center_uv[0], target.ship_center_uv[1])
	var desired_size := Vector2(target.ship_size_uv[0], target.ship_size_uv[1])
	var right: Vector3 = game.camera.global_basis.x.normalized()
	var yaw := atan2(-right.z, right.x)
	var candidates := []
	# Hypothetical projection only; the scene is not moved while searching.
	for step in range(53):
		var depth := 25.0 + float(step) * 1.25
		var pose := fit_pose(depth, yaw, desired_center)
		var bounds := projection(pose)
		var actual := Vector2(bounds.size[0], bounds.size[1])
		var error := pow(log(actual.x / desired_size.x), 2) + pow(log(actual.y / desired_size.y), 2)
		candidates.append({"pose": pose, "optical_depth_m": depth, "yaw": yaw, "projection": bounds, "size_log_error": error})
	candidates.sort_custom(func(a, b): return a.size_log_error < b.size_log_error)
	var attempts := []
	for candidate in candidates:
		if not candidate.projection.inside: continue
		var physics := clearance(candidate.pose)
		attempts.append({"depth_m": candidate.optical_depth_m, "score": candidate.size_log_error, "projection": candidate.projection, "physics": physics})
		if not physics.passed: continue
		var delta: Vector3 = candidate.pose.origin - game.camera.global_position
		var forward: Vector3 = -game.camera.global_basis.z
		var planar := Vector3(forward.x, 0, forward.z)
		var dist := Vector3(delta.x, 0, delta.z).dot(planar) / planar.length_squared()
		candidate["existing_formula_parameters"] = {"dist": dist, "right": delta.dot(right), "up": delta.y - forward.y * dist, "yaw": yaw}
		candidate["physics"] = physics
		candidate["attempts"] = attempts
		candidate["measurement_target"] = target
		candidate["rationale"] = "Broadside nose points toward screen left. Preserve original scale and fixed camera/FOV; balance relative width/height errors from approximate reference silhouette, then align screen center. Different source/model proportions can prevent simultaneous exact width and height. Only physically clear candidates may be selected."
		return candidate
	return {"failed": true, "attempts": attempts}

func capture(reference: String, label: String) -> Dictionary:
	controller.refresh_now()
	await frames(3)
	await physics_frame
	controller.refresh_now()
	await RenderingServer.frame_post_draw
	var row := {"reference": reference, "label": label, "ship_transform": str(game.airship.global_transform),
		"camera_transform": str(game.camera.global_transform), "camera_fov": game.camera.fov,
		"ship_projection": projection(game.airship.global_transform), "reflection_effective": controller.effective_reflection}
	for reflection in [false, true]:
		var image: Image = controller.viewport.get_texture().get_image() if reflection else root.get_texture().get_image()
		image.convert(Image.FORMAT_RGBA8)
		var tag := "reflection" if reflection else "main"
		var file := output.path_join(reference + "--" + label + "--" + tag + ".png")
		check(image.save_png(file) == OK, "Saved actual " + reference + "/" + label + "/" + tag)
		row[tag] = {"file": file, "sha256": FileAccess.get_sha256(file), "pixel_sha256": bytes_digest(image.get_data()), "size": [image.get_width(), image.get_height()]}
	captures.append(row)
	checkpoint(reference + "_" + label)
	return row

func restore() -> bool:
	if not have_original or not is_instance_valid(game): return true
	game.airship.global_transform = original_ship
	controller.refresh_now()
	var ok: bool = game.airship.global_transform == original_ship and game.camera.global_transform == original_camera and game.camera.fov == original_fov and game.airship.scale == original_scale
	return check(ok and invariants(false) == snapshot_before and collisions() == collision_before, "Exact complete A runtime state restored; original camera/FOV/geometry/environment/collision retained")

func write_report(complete: bool) -> void:
	if output.is_empty(): return
	var report := {"stage": stage, "complete": complete, "limited_near_side_comparison_passed": complete and failures.is_empty(),
		"candidate": SCENE, "candidate_sha256": SHA, "matching_saved_audit": AUDIT, "matching_saved_audit_sha256": LOCKS[AUDIT],
		"renderer": RenderingServer.get_video_adapter_name(), "checks": checks, "failures": failures, "captures": captures,
		"selections": selections, "comparisons": comparisons, "reference_measurements": measurements,
		"scene_saved": false, "presets_modified": false, "ship_scaled": false, "world_geometry_changed": false,
		"actual_player_input_flight_repeated": false, "actual_player_input_flight_passed": false,
		"reference_composition_accepted": false, "hardware_gpu_acceptance": false, "full_route_flight_passed": false,
		"known1344_conversion_gate_passed": false, "known350m_route_passed": false, "total_acceptance_passed": false,
		"scope": "Only same-ship runtime translation/yaw in one saved53west world. A/original, B/near-side study, A2/exact restoration at each original1128/1129 camera/FOV. Approximate measured reference proportions guide placement; geometry/environment/preset are not reshaped or saved. Full body and padded visible/rotating-propeller solid clearance/support distances are tested. Teleport comparison is not flight or final GOAL acceptance."}
	var path := output.path_join("near-ship-report.json")
	var file := FileAccess.open(path + ".tmp", FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(report, "  ")); file.flush(); file.close()
		DirAccess.rename_absolute(path + ".tmp", path)

func finish() -> void:
	restore()
	for path in source_hashes:
		check(FileAccess.get_sha256(path) == source_hashes[path], "Source preserved " + path)
	stage = "complete" if failures.is_empty() else "failed"
	write_report(true)
	if is_instance_valid(game): game.queue_free()
	await frames(4)
	quit(0 if failures.is_empty() else 1)

func run() -> void:
	if not output.is_absolute_path() or DirAccess.dir_exists_absolute(output): quit(2); return
	DirAccess.make_dir_recursive_absolute(output)
	checkpoint("identity")
	if not check(DisplayServer.get_name() != "headless", "Actual rendered A/B/A2 needs a renderer"): await finish(); return
	for path in LOCKS:
		if not check(FileAccess.get_sha256(path) == LOCKS[path], "Exact locked identity " + path): await finish(); return
		source_hashes[path] = LOCKS[path]
	var build: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BUILD))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	var audit: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AUDIT))
	if not check(audit.verification_passed and audit.saved_native_verified and audit.candidate_sha256 == SHA and audit.checks.size() == 202, "Reuse completed202-check saved53west audit without loading another scene"): await finish(); return
	for row in manifest.immutable_inputs: source_hashes[row.path] = row.sha256
	for row in build.inventory: source_hashes[row.path] = row.sha256
	var intake: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PREP + "source-intake.json"))
	for path in intake.sources: source_hashes["res://" + path] = intake.sources[path]
	for path in source_hashes:
		if not check(FileAccess.get_sha256(path) == source_hashes[path], "Current source hash " + path): await finish(); return
	measurements = JSON.parse_string(FileAccess.get_file_as_string(PREP + "reference-measurements.json"))
	for reference in measurements:
		if not check(FileAccess.get_sha256(measurements[reference].source) == measurements[reference].source_sha256, "Measured original reference source " + reference): await finish(); return
	root.size = Vector2i(1180, 664)
	checkpoint("before_single_scene_load")
	game = load(SCENE).instantiate()
	root.add_child(game)
	game.test_frozen = true
	await frames(8)
	await RenderingServer.frame_post_draw
	controller = game.get_node("World/LakeReflection51")
	var live_collisions := collisions()
	freeze(game)
	await physics_frame
	if not check(collisions() == live_collisions, "Callback freeze retains live collision modes/layers/RIDs"): await finish(); return
	for reference in ["1128", "1129"]:
		have_original = false
		game.observe_reference(reference)
		var weather = game.get_node("Weather42b")
		weather.seek_time(0.0); weather.seek_time(0.35); weather._process(0.0)
		RenderingServer.global_shader_parameter_set("world_time", 0.35)
		controller.refresh_now()
		await frames(3)
		await physics_frame
		original_ship = game.airship.global_transform
		original_camera = game.camera.global_transform
		original_fov = game.camera.fov
		original_scale = game.airship.scale
		var expected_camera := Vector3(1150, 10, -1000) if reference == "1128" else Vector3(1300, 7, -950)
		if not check(game.camera.global_position.is_equal_approx(expected_camera) and is_equal_approx(original_fov, 64.0 if reference == "1128" else 66.0), "Original reference camera position and FOV " + reference): await finish(); return
		have_original = true
		snapshot_before = invariants(false)
		collision_before = collisions()
		var unaffected := invariants(true)
		if not collect_ship(): await finish(); return
		var a := await capture(reference, "A-original")
		var original_physics := clearance(original_ship)
		if not check(original_physics.passed, "Original A body/full-visible volume is physically clear " + reference, original_physics): await finish(); return
		var chosen := choose_pose(reference)
		if not check(not chosen.has("failed"), "Physically clear fixed-camera near-side candidate found " + reference, chosen): await finish(); return
		var selected: Transform3D = chosen.pose
		chosen["reference"] = reference
		chosen["original_physics"] = original_physics
		chosen["pose"] = str(selected)
		selections.append(chosen)
		checkpoint(reference + "_candidate_prechecked")
		game.airship.global_transform = selected
		await physics_frame
		controller.refresh_now()
		if not check(game.camera.global_transform == original_camera and game.camera.fov == original_fov and game.airship.scale.is_equal_approx(original_scale) and invariants(true) == unaffected and collisions() == collision_before, "B changes only same ship position/yaw; complete unrelated state remains exact " + reference): await finish(); return
		var actual_physics := clearance(game.airship.global_transform)
		if not check(actual_physics.passed, "Actual placed B full body and rotating visual envelope remain physically clear " + reference, actual_physics): await finish(); return
		var b := await capture(reference, "B-near-side-study")
		if not restore(): await finish(); return
		await physics_frame
		var a2 := await capture(reference, "A2-restored")
		var restored_physics := clearance(game.airship.global_transform)
		var comparison := {"reference": reference, "A_A2_main_pixels_equal": a.main.pixel_sha256 == a2.main.pixel_sha256,
			"A_A2_reflection_pixels_equal": a.reflection.pixel_sha256 == a2.reflection.pixel_sha256,
			"B_main_changed": a.main.pixel_sha256 != b.main.pixel_sha256, "B_reflection_changed": a.reflection.pixel_sha256 != b.reflection.pixel_sha256,
			"restored_physics": restored_physics, "restored_state_exact": invariants(false) == snapshot_before}
		comparisons.append(comparison)
		if not check(comparison.A_A2_main_pixels_equal and comparison.A_A2_reflection_pixels_equal and comparison.B_main_changed and comparison.B_reflection_changed and comparison.restored_state_exact and restored_physics.passed, "A/B/A2 real main/reflection contrast and full restoration " + reference, comparison): await finish(); return
		checkpoint(reference + "_restoration_verified")
	await finish()
