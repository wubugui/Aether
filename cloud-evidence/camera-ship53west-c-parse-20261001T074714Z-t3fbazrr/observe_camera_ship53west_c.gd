extends "res://tools/observe_near_ship53west_v2.gd"
## Independent C study. Frozen v2 remains unchanged; no preset or scene save.
const C_DIR := ROOT + "/source-assets/near-ship53west/c-study/"
const V2_SOURCE_SHA := "3963510027f02608c74ad6e83b112f35e45db17eb07ecaa24bcebc33d69ac5dd"
const C_MEASURE_SHA := "31349b160132c3c4e2f2c2e1a3b6e1fdcf24917cb231cce1fe1e8056f242bb7d"
const C_PROPOSALS_SHA := "2df9da712222e96941ac526d91beb515c6fda816712711a0bf227dd6864e9d17"
var c_proposals := {}
var camera_local: Transform3D
var camera_position := Vector3.ZERO
var camera_rotation := Vector3.ZERO
var camera_scale := Vector3.ONE
var camera_rotation_order := 0
var camera_target := Vector3.ZERO
var camera_properties := {}
var geometry_projection_points := PackedVector3Array()
var search_projection_points := PackedVector3Array()
var query_camera_position := Vector3.ZERO
var c_diagnostics := []
var evaluated_count := 0
var retained := []
var texture_sizes := []

func snapshot(exclude_controls: bool) -> Dictionary:
	var value := super.snapshot(false)
	if exclude_controls:
		# Exactly the C-permitted transforms, including derived mirror camera.
		# Every other property remains protected; A2 always uses the full state.
		for row in value.nodes:
			if row.path in ["Airship", "Camera", "World/LakeReflection51/ReflectionViewport/ReflectionCamera"]:
				row.erase("transform")
	return value

func collect_ship() -> bool:
	if not super.collect_ship(): return false
	geometry_projection_points = local_points.duplicate()
	# A temporary convex debug mesh supplies a small support-vertex set for
	# search. It is never inserted into the world or substituted for a collider.
	# Every finally considered candidate is rechecked with all original vertices.
	var hull := ConvexPolygonShape3D.new()
	hull.points = geometry_projection_points
	var mesh: ArrayMesh = hull.get_debug_mesh()
	var unique := {}
	if mesh:
		for i in range(mesh.get_surface_count()):
			var arrays: Array = mesh.surface_get_arrays(i)
			if arrays.is_empty(): continue
			for vertex in arrays[Mesh.ARRAY_VERTEX]: unique[vertex] = true
	search_projection_points.clear()
	for vertex in unique: search_projection_points.append(vertex)
	if search_projection_points.size() < 8: search_projection_points = geometry_projection_points.duplicate()
	check(true, "C search proxy and exact final geometry", {"exact_vertices": geometry_projection_points.size(), "temporary_convex_support_vertices": search_projection_points.size(), "original_geometry_or_collision_replaced": false})
	return true

func project_spec(ship: Transform3D, view_pose: Transform3D, optical: Projection, points: PackedVector3Array, mirror: bool) -> Dictionary:
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	var front := true
	var view := view_pose.affine_inverse()
	for vertex in points:
		var world := ship * vertex
		if mirror: world.y = -world.y
		var local := view * world
		var clip := optical * Vector4(local.x, local.y, local.z, 1)
		if clip.w <= game.camera.near: front = false; continue
		var uv := Vector2(clip.x / clip.w * 0.5 + 0.5, 0.5 - clip.y / clip.w * 0.5)
		lo = lo.min(uv); hi = hi.max(uv)
	return {"min": v2(lo), "max": v2(hi), "center": v2((lo + hi) * 0.5), "size": v2(hi - lo),
		"inside": front and lo.x >= 0.025 and lo.y >= 0.025 and hi.x <= 0.975 and hi.y <= 0.975, "all_forward": front}

func mirrored_camera(pose: Transform3D) -> Transform3D:
	var basis := Basis(controller.reflected_y(pose.basis.x), -controller.reflected_y(pose.basis.y), controller.reflected_y(pose.basis.z)).orthonormalized()
	return Transform3D(basis, controller.reflected_y(pose.origin))

func evaluate_spec(spec: Dictionary, points: PackedVector3Array) -> Dictionary:
	evaluated_count += 1
	var target: Dictionary = measurements[current_reference]
	var camera_basis := Basis.from_euler(Vector3(deg_to_rad(spec.camera_pitch_degrees), camera_rotation.y, camera_rotation.z), camera_rotation_order).scaled(camera_scale)
	var parent: Transform3D = game.camera.get_parent_node_3d().global_transform
	var optical_pose := parent * Transform3D(camera_basis, Vector3(camera_position.x, spec.camera_y, camera_position.z))
	var right: Vector3 = original_camera.basis.x.normalized()
	var flat_forward := Vector3(-original_camera.basis.z.x, 0, -original_camera.basis.z.z).normalized()
	var yaw := atan2(-right.z, right.x)
	var ship_basis := Basis(Vector3.UP, yaw).scaled(original_scale)
	var pos: Vector3 = Vector3(original_camera.origin.x, spec.ship_origin_y, original_camera.origin.z) + flat_forward * float(spec.horizontal_depth_m) + right * float(spec.right_m)
	var ship := Transform3D(ship_basis, pos)
	var desired_x: float = (float(target.ship_center_uv[0]) + float(target.reflection_center_uv[0])) * 0.5
	var optical: Projection = game.camera.get_camera_projection()
	var reflect_optical: Projection = controller.reflection_camera.get_camera_projection()
	var reflected := mirrored_camera(optical_pose)
	var real := {}
	var mirror := {}
	for i in range(3):
		real = project_spec(ship, optical_pose, optical, points, false)
		mirror = project_spec(ship, optical_pose, optical, points, true)
		var dx: float = desired_x - (float(real.center[0]) + float(mirror.center[0])) * 0.5
		ship.origin += right * dx * 2.0 * float(spec.horizontal_depth_m) / optical.x.x
	real = project_spec(ship, optical_pose, optical, points, false)
	mirror = project_spec(ship, optical_pose, optical, points, true)
	var raw := project_spec(ship, reflected, reflect_optical, points, false)
	var world_box: AABB = ship * visual_box
	var valid: bool = real.inside and mirror.inside and raw.inside and world_box.position.y >= 0.5
	var score := 0.0
	var residuals := {}
	for pair in [["main", real, target.ship_center_uv, target.ship_size_uv], ["water_mirror", mirror, target.reflection_center_uv, target.reflection_size_uv]]:
		var size_error := []
		var center_error := []
		for axis in range(2):
			var ratio: float = float(pair[1].size[axis]) / float(pair[3][axis])
			var offset: float = float(pair[1].center[axis]) - float(pair[2][axis])
			score += pow(log(maxf(ratio, 0.000001)), 2) + 64.0 * offset * offset
			size_error.append(ratio - 1.0); center_error.append(offset)
		residuals[pair[0]] = {"relative_size_residual": size_error, "center_uv_residual": center_error}
	return {"valid": valid, "score": score, "spec": spec.duplicate(true), "ship_pose": ship, "camera_pose": optical_pose,
		"yaw": yaw, "main": real, "water_mirror": mirror, "raw_reflection": raw, "residuals": residuals,
		"lowest_padded_visual_y": world_box.position.y, "search_points": points.size()}

func remember(row: Dictionary) -> void:
	if not row.valid: return
	retained.append(row)
	retained.sort_custom(func(a, b): return a.score < b.score)
	if retained.size() > 24: retained.pop_back()

func camera_and_water_clearance(row: Dictionary) -> Dictionary:
	var camera_pos: Vector3 = row.camera_pose.origin
	var space: PhysicsDirectSpaceState3D = game.get_world_3d().direct_space_state
	var sphere := SphereShape3D.new()
	sphere.radius = maxf(0.35, game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = sphere; query.transform.origin = camera_pos; query.collision_mask = 5; query.exclude = [game.airship.get_rid()]
	var camera_hits := space.intersect_shape(query, 32)
	var pose: Transform3D = row.ship_pose
	var main_sight := []
	var water_hits := []
	var footprint := AABB()
	var first := true
	for i in range(8):
		var point := pose * visual_box.get_endpoint(i)
		var main_ray := PhysicsRayQueryParameters3D.create(camera_pos, point, 5, [game.airship.get_rid()])
		var main_hit := space.intersect_ray(main_ray)
		if not main_hit.is_empty(): main_sight.append({"corner": i, "collider": str(main_hit.collider.get_path())})
		var virtual_point := Vector3(point.x, -point.y, point.z)
		var t := camera_pos.y / (camera_pos.y - virtual_point.y)
		var surface := camera_pos.lerp(virtual_point, t)
		if first: footprint = AABB(surface, Vector3.ZERO); first = false
		else: footprint = footprint.expand(surface)
	#25 actual first-hit rays across the whole conservative reflected footprint.
	# They expose coast/island obstruction instead of merely testing frustum fit.
	var all_water := true
	for ix in range(5):
		for iz in range(5):
			var point := Vector3(lerpf(footprint.position.x, footprint.end.x, float(ix) / 4.0), -0.05, lerpf(footprint.position.z, footprint.end.z, float(iz) / 4.0))
			var ray := PhysicsRayQueryParameters3D.create(camera_pos, point, 5, [game.airship.get_rid()])
			var hit := space.intersect_ray(ray)
			var is_water: bool = not hit.is_empty() and hit.collider == game.get_node("World/Ocean/SeaCollision") and absf(hit.position.y) < 0.05
			all_water = all_water and is_water
			water_hits.append({"grid": [ix, iz], "endpoint": v3(point), "actual_water_first_hit": is_water, "collider": str(hit.collider.get_path()) if not hit.is_empty() else "none", "position": v3(hit.position) if not hit.is_empty() else []})
	var local_camera: Vector3 = pose.affine_inverse() * camera_pos
	var nearest: Vector3 = local_camera.clamp(visual_box.position, visual_box.end)
	var distance := camera_pos.distance_to(pose * nearest)
	return {"passed": camera_hits.is_empty() and main_sight.is_empty() and all_water and distance > 2.0,
		"camera_sphere_radius": sphere.radius, "camera_sphere_hits": hits(camera_hits), "camera_envelope_distance_m": distance,
		"main_silhouette_occluders": main_sight, "reflected_water_footprint": str(footprint), "water_first_hits": water_hits,
		"scope": "Actual main camera sphere, eight full-envelope sightlines,25 first-hit rays across conservative reflected water footprint. Complete exact vertex frusta are checked separately; visual PNG review remains required."}

func choose_c() -> Dictionary:
	evaluated_count = 0; retained.clear()
	var best := {}
	for seed in c_proposals.references[current_reference].ranked_seeds:
		var row := evaluate_spec(seed, search_projection_points)
		remember(row)
		if row.valid and (best.is_empty() or row.score < best.score): best = row
	if best.is_empty(): return {"failed": true, "reason": "No exact-mesh search proxy candidate fits all three frusta"}
	# Local refinement can move away from the CPU box seed; this is explicitly a
	# bounded study, not a global optimum. Refine the initial upper pitch edge to3deg.
	var trace := []
	for level in [1.0, 0.5, 0.25]:
		for iteration in range(16):
			var old_score: float = best.score
			for change in [["horizontal_depth_m", 5.0 * level], ["ship_origin_y", 1.0 * level], ["camera_y", 0.5 * level], ["camera_pitch_degrees", 0.5 * level]]:
				for direction in [-1.0, 1.0]:
					var spec: Dictionary = best.spec.duplicate(true)
					spec[change[0]] = float(spec[change[0]]) + float(change[1]) * direction
					if spec.horizontal_depth_m < 30 or spec.horizontal_depth_m > 70 or spec.camera_y < 1 or spec.camera_y > 6 or spec.camera_pitch_degrees < -4 or spec.camera_pitch_degrees > 3 or spec.ship_origin_y < -visual_box.position.y + 0.5 or spec.ship_origin_y > 16: continue
					var row := evaluate_spec(spec, search_projection_points)
					remember(row)
					if row.valid and row.score < best.score: best = row
			trace.append({"level": level, "iteration": iteration, "score": best.score, "spec": best.spec})
			if best.score >= old_score - 0.00000001: break
	var full_rows := []
	for row in retained:
		var exact := evaluate_spec(row.spec, geometry_projection_points)
		if exact.valid: full_rows.append(exact)
	full_rows.sort_custom(func(a, b): return a.score < b.score)
	var trials := []
	for row in full_rows:
		# Base volume/support checks do not depend on camera orientation; their
		# old-camera sightline result is retained as an extra conservative test.
		var body := clearance(row.ship_pose)
		var camera_water := camera_and_water_clearance(row)
		trials.append({"score": row.score, "spec": row.spec, "body": body, "camera_and_water": camera_water})
		if body.passed and camera_water.passed:
			row["body_physics"] = body
			row["camera_and_water_physics"] = camera_water
			row["trials"] = trials
			row["search_trace"] = trace
			row["evaluated_count"] = evaluated_count
			row["global_optimum_claimed"] = false
			return row
	return {"failed": true, "trials": trials, "search_trace": trace, "evaluated_count": evaluated_count}

func restore() -> bool:
	if not have_original or not is_instance_valid(game): return true
	# Repeat the exact original look_at operation with its recorded source target.
	# Matrix-only writeback preserves matrix bytes but perturbs derived rotation/
	# scale caches; the tiny CPU camera probe verifies this source-operation restore.
	game.camera.position = camera_position
	game.camera.scale = camera_scale
	game.camera.look_at(camera_target, Vector3.UP)
	controller.refresh_now()
	var camera_exact: bool = game.camera.transform == camera_local and game.camera.position == camera_position and game.camera.rotation == camera_rotation and game.camera.scale == camera_scale and game.camera.rotation_order == camera_rotation_order
	check(camera_exact, "C camera exact local matrix and original derived components restored", {"position": diagnostic_value(game.camera.position), "rotation": diagnostic_value(game.camera.rotation), "scale": diagnostic_value(game.camera.scale)})
	return super.restore() and camera_exact

func write_report(complete: bool) -> void:
	super.write_report(complete)
	if output.is_empty(): return
	var path := output.path_join("near-ship-report.json")
	if not FileAccess.file_exists(path): return
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	report["version"] = "53west-independent-C-camera-and-ship-study-v3"
	report["C_diagnostics"] = c_diagnostics
	report["C_cpu_proposals"] = C_DIR + "c-math-proposals.json"
	report["C_cpu_proposals_sha256"] = C_PROPOSALS_SHA
	report["allowed_C_changes"] = ["main camera height and pitch", "same ship position and yaw", "derived reflected camera transform"]
	report["kept_original"] = ["main cameraXZ and FOV", "main/reflection optics and texture sizes", "ship scale", "world geometry", "materials", "environment", "saved presets"]
	report["limited_C_visibility_restore_physics_passed"] = complete and failures.is_empty() and c_diagnostics.size() == 2
	report["reference_composition_accepted"] = false
	report["scope"] = "Independent A/C/A2 same-world camera-height/pitch and ship-pose study. Full exact mesh vertices must fit main, main virtual-water-mirror and raw reflection frusta; native body/full-rotation envelope, main-camera and water-footprint physics checks remain mandatory. Width/height residuals are reported, never disguised with scaling/cropping/texture expansion. Complete original state and main/reflection pixels must restore exactly. No flown route, saved preset/world change, global optimum or final reference/GOAL acceptance."
	var file := FileAccess.open(path + ".tmp", FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(report, "  ")); file.flush(); file.close(); DirAccess.rename_absolute(path + ".tmp", path)

func run() -> void:
	if not output.is_absolute_path() or DirAccess.dir_exists_absolute(output): quit(2); return
	DirAccess.make_dir_recursive_absolute(output)
	checkpoint("C_identity")
	if not check(DisplayServer.get_name() != "headless", "C requires real renderer for final A/C/A2 images"): await finish(); return
	var extra := {"res://tools/observe_near_ship53west_v2.gd": V2_SOURCE_SHA, C_DIR + "reference-main-and-mirror-measurements.json": C_MEASURE_SHA, C_DIR + "c-math-proposals.json": C_PROPOSALS_SHA,
		ROOT + "/cloud-evidence/near-ship53west-v2-renderer-20261001T072841Z-i9rjqlen/images/near-ship-report.json": "fefe96426b846e92c17120a97b752757273d59d19eb7b88a85a26d4063887dac"}
	for path in LOCKS:
		source_hashes[path] = LOCKS[path]
	for path in extra: source_hashes[path] = extra[path]
	var build: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BUILD))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	for row in manifest.immutable_inputs: source_hashes[row.path] = row.sha256
	for row in build.inventory: source_hashes[row.path] = row.sha256
	var intake: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PREP + "source-intake.json"))
	for path in intake.sources: source_hashes["res://" + path] = intake.sources[path]
	for path in source_hashes:
		if not check(FileAccess.get_sha256(path) == source_hashes[path], "C exact locked source " + path): await finish(); return
	c_proposals = JSON.parse_string(FileAccess.get_file_as_string(C_DIR + "c-math-proposals.json"))
	measurements = JSON.parse_string(FileAccess.get_file_as_string(C_DIR + "reference-main-and-mirror-measurements.json"))
	root.size = Vector2i(1180, 664)
	checkpoint("C_before_single_scene_load")
	game = load(SCENE).instantiate(); root.add_child(game); game.test_frozen = true
	await frames(8); await RenderingServer.frame_post_draw
	controller = game.get_node("World/LakeReflection51")
	var live := collisions(); freeze(game); await physics_frame
	if not check(collisions() == live, "C callback freeze preserves actual physics"): await finish(); return
	for reference in ["1128", "1129"]:
		current_reference = reference; have_original = false
		game.observe_reference(reference)
		var weather = game.get_node("Weather42b")
		weather.seek_time(0.0); weather.seek_time(0.35); weather._process(0.0)
		RenderingServer.global_shader_parameter_set("world_time", 0.35)
		controller.refresh_now(); await frames(3); await physics_frame
		original_ship = game.airship.global_transform; original_camera = game.camera.global_transform
		original_fov = game.camera.fov; original_scale = game.airship.scale
		original_local = game.airship.transform; original_position = game.airship.position
		original_rotation = game.airship.rotation; original_rotation_order = game.airship.rotation_order
		camera_local = game.camera.transform; camera_position = game.camera.position
		camera_rotation = game.camera.rotation; camera_scale = game.camera.scale; camera_rotation_order = game.camera.rotation_order
		var entry: Dictionary = game.scene_environment.reference(reference).camera
		camera_target = Vector3(entry.tx, entry.ty_abs, entry.tz)
		var expected_camera := Vector3(1150, 10, -1000) if reference == "1128" else Vector3(1300, 7, -950)
		if not check(original_camera.origin.is_equal_approx(expected_camera) and original_fov == (64.0 if reference == "1128" else 66.0), "C starts from unchanged original reference camera " + reference): await finish(); return
		camera_properties = {"fov": game.camera.fov, "near": game.camera.near, "far": game.camera.far, "keep_aspect": game.camera.keep_aspect, "optical_overscan": controller.optical_overscan, "reflection_scale": controller.reflection_scale, "reflection_fov": controller.reflection_camera.fov}
		texture_sizes = [root.get_texture().get_size(), controller.viewport.get_texture().get_size()]
		have_original = true
		original_state = snapshot(false).duplicate(true); snapshot_before = digest(original_state); collision_before = collisions()
		var unaffected := invariants(true)
		save_state("A-original-full", original_state); save_state("A-original-ship-components", transform_components())
		save_state("A-original-camera-components", {"transform": camera_local, "position": camera_position, "rotation": camera_rotation, "scale": camera_scale, "rotation_order": camera_rotation_order, "source_look_at_target": camera_target, "properties": camera_properties})
		if not collect_ship(): await finish(); return
		var a := await capture(reference, "A-original")
		var chosen := choose_c()
		if not check(not chosen.has("failed"), "C full real/mirror visibility and actual physical candidate " + reference, chosen): await finish(); return
		var ship: Transform3D = chosen.ship_pose
		game.camera.position = Vector3(camera_position.x, chosen.spec.camera_y, camera_position.z)
		game.camera.rotation = Vector3(deg_to_rad(chosen.spec.camera_pitch_degrees), camera_rotation.y, camera_rotation.z)
		var ship_parent: Transform3D = game.airship.get_parent_node_3d().global_transform
		var local_ship: Transform3D = ship_parent.affine_inverse() * ship
		game.airship.position = local_ship.origin
		game.airship.rotation = Vector3(original_rotation.x, local_ship.basis.get_euler(original_rotation_order).y, original_rotation.z)
		await physics_frame; controller.refresh_now()
		if not check(invariants(true) == unaffected and collisions() == collision_before and game.camera.global_position.x == original_camera.origin.x and game.camera.global_position.z == original_camera.origin.z and game.camera.fov == original_fov and game.airship.scale == original_scale and controller.optical_overscan == camera_properties.optical_overscan and controller.reflection_scale == camera_properties.reflection_scale and controller.reflection_camera.fov == camera_properties.reflection_fov and root.get_texture().get_size() == texture_sizes[0] and controller.viewport.get_texture().get_size() == texture_sizes[1], "C changes only authorized camera/ship transforms; optics/textures/scale/world exact " + reference): await finish(); return
		var actual := {"ship_pose": game.airship.global_transform, "camera_pose": game.camera.global_transform}
		var body := clearance(game.airship.global_transform)
		var water := camera_and_water_clearance(actual)
		var main := camera_projection(game.camera, game.airship.global_transform, false)
		var mirror := camera_projection(game.camera, game.airship.global_transform, true)
		var raw := camera_projection(controller.reflection_camera, game.airship.global_transform, false)
		if not check(body.passed and water.passed and main.inside and mirror.inside and raw.inside, "Actual placed C has complete real/mirror frusta and physical clearance " + reference, {"main": main, "water_mirror": mirror, "raw": raw, "body": body, "water": water}): await finish(); return
		chosen.ship_pose = str(chosen.ship_pose); chosen.camera_pose = str(chosen.camera_pose)
		chosen["reference"] = reference
		chosen["actual_main"] = main; chosen["actual_water_mirror"] = mirror; chosen["actual_raw_reflection"] = raw
		chosen["actual_body_physics"] = body; chosen["actual_camera_and_water"] = water
		c_diagnostics.append(chosen)
		var c := await capture(reference, "C-camera-and-ship-study")
		save_state("C-full", snapshot(false))
		if not restore(): await finish(); return
		await physics_frame
		var a2 := await capture(reference, "A2-restored")
		var comparison := {"reference": reference, "A_A2_main_pixels_equal": a.main.pixel_sha256 == a2.main.pixel_sha256, "A_A2_reflection_pixels_equal": a.reflection.pixel_sha256 == a2.reflection.pixel_sha256, "C_main_changed": a.main.pixel_sha256 != c.main.pixel_sha256, "C_reflection_changed": a.reflection.pixel_sha256 != c.reflection.pixel_sha256, "state_exact": invariants(false) == snapshot_before, "full_C_geometric_visibility": c.both_full_ship_and_mirror_inside_frusta}
		comparisons.append(comparison)
		if not check(comparison.A_A2_main_pixels_equal and comparison.A_A2_reflection_pixels_equal and comparison.C_main_changed and comparison.C_reflection_changed and comparison.state_exact and comparison.full_C_geometric_visibility, "C A/C/A2 full-state and both-image strict restoration " + reference, comparison): await finish(); return
		checkpoint(reference + "_C_and_exact_restore_verified")
	await finish()
