extends SceneTree
## Actual native Game39 boot. No script, shader, Environment or scenery replacement.
var output := ""
var checks: Array = []
var captures: Array = []
var game: Node3D
var checks_only := false

func _initialize() -> void: call_deferred("run")

func check(ok: bool, label: String, evidence: Variant = null) -> void:
	checks.append({"passed": ok, "name": label, "evidence": evidence})
	print("PASS " if ok else "FAIL ", label)

func frames(count: int) -> void:
	for i in range(count): await process_frame

func capture(name: String) -> void:
	if checks_only: return
	await frames(18)
	await RenderingServer.frame_post_draw
	var path := output.path_join(name + ".png")
	var image: Image = root.get_texture().get_image()
	check(image.save_png(path) == OK, "GPU image saved " + name)
	var p: Vector3 = game.camera.position
	captures.append({"name": name, "image": path, "sha256": FileAccess.get_sha256(path),
		"position": [p.x,p.y,p.z], "camera_transform": str(game.camera.transform),
		"reference": game.scene_environment.current_reference,
		"fov": game.camera.fov, "world_instance": game.world.get_instance_id(),
		"game_script": game.get_script().resource_path, "pixels": [image.get_width(),image.get_height()]})

func run() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output = arg.trim_prefix("--output-dir=")
		if arg == "--checks-only": checks_only = true
	assert(not output.is_empty())
	DirAccess.make_dir_recursive_absolute(output)
	game = load("res://scenes/candidate39/Game39.tscn").instantiate()
	root.add_child(game)
	game.sound_enabled = false
	game.test_frozen = true
	await frames(30)
	check(game.get_script().resource_path == "res://scripts/game39.gd", "Native game script active")
	check(game.scene_environment.current_reference == "1343", "Normal boot starts in daylight")
	check(game.world.core.size() == 208, "Existing 208 authored terrain tiles retained")
	check(game.world.layout.props.size() >= 54797, "Authored scatter retained", game.world.layout.props.size())
	var region: Node3D = game.get_node("SkyRegion39")
	var cabins := [region.get_node("CabinA"), region.get_node("CabinB")]
	for cabin in cabins:
		var colliders: Array = cabin.find_children("*", "CollisionShape3D", true, false)
		check(not colliders.is_empty(), "Native cabin collision " + str(cabin.name), colliders.size())
		var max_error := 0.0
		for shape_node in colliders:
			var mesh: MeshInstance3D = shape_node.get_parent().get_parent()
			var faces: PackedVector3Array = mesh.mesh.get_faces()
			var collision_faces: PackedVector3Array = shape_node.shape.get_faces()
			if faces != collision_faces: max_error = 1.0
		check(max_error == 0, "Cabin mesh and collision equality " + str(cabin.name))
	var islands := 0
	var cloud_tiles := 0
	for node in region.get_children():
		if str(node.name).begins_with("FloatingIsland_"): islands += 1
		if str(node.name).begins_with("CloudSea_"): cloud_tiles += 1
	check(islands == 9 and cloud_tiles == 25, "Persistent same-world high-altitude assets", {"islands":islands,"cloud_tiles":cloud_tiles})
	var daylight: Dictionary = game.scene_environment.apply_reference("1343")
	check(daylight.bindings.scene_fill > 0 and daylight.bindings.storm_strength > 0, "Live material environment bindings", daylight)
	game.photo_mode = true
	game.reference_observation = true
	game.camera.position = Vector3(0,145,250)
	game.camera.rotation_degrees = Vector3(-3.5,0,0)
	await capture("boot-day")
	game.scene_environment.apply_reference("1342")
	var ship_meshes: Array = game.airship.get_node("Visuals").find_children("*", "MeshInstance3D", true, false)
	var ship_bound := true
	for mesh in ship_meshes:
		var expected: Material = game.airship.cloth_material if str(mesh.name) == "Flag" else game.airship.hull_material
		ship_bound = ship_bound and mesh.material_override == expected
	check(ship_bound and game.airship.hull_material.shader.code.contains("scene_fill"), "Airship authoritative material survives ready and receives environment")
	check(game.airship.hull_material.get_shader_parameter("scene_fill").is_equal_approx(Vector3(.12,.15,.26)), "Airship fill changes in moonlight")
	var extension: MeshInstance3D = game.world.build_chunk(Vector2i(20,20))
	check(extension.material_override == game.world.stream_terrain_material, "Streamed terrain uses candidate environment material")
	check(extension.material_override.get_shader_parameter("scene_fill").is_equal_approx(Vector3(.12,.15,.26)), "Newly streamed terrain inherits current night state")
	var streamed_groves := 0
	var streamed_bound := true
	# The engine reparents generated groves below their terrain mesh. Query
	# actual extension subtrees rather than assuming they stay world children.
	for terrain in game.world.find_children("Generated_ground_*", "MeshInstance3D", true, false):
		for node in terrain.find_children("*", "MultiMeshInstance3D", true, false):
			streamed_groves += 1
			streamed_bound = streamed_bound and node.material_override in [game.world.stream_world_material,game.world.stream_cloud_material]
	check(streamed_groves > 0 and streamed_bound, "Streamed vegetation/clouds use environment materials", streamed_groves)
	var night_lamps := 0
	for lamp in game.scene_environment.lamps:
		if str(lamp.name) in ["HarborWarmLight","VillageWarmLight"] and lamp.light_energy > 0: night_lamps += 1
	check(night_lamps == 63, "Authored harbor and village night lamps restored", night_lamps)
	await capture("same-camera-night")
	game.scene_environment.apply_reference("1343")
	await capture("same-camera-day-restored")
	var original: Image = Image.load_from_file(output.path_join("boot-day.png"))
	var restored: Image = Image.load_from_file(output.path_join("same-camera-day-restored.png"))
	# Propeller/cloud animation can change; record exact image identity but do
	# not require pixel equality to a moving world. Environment uniforms reset.
	check(is_equal_approx(game.get_node("Sun").light_energy, .85), "Daylight energy restored after night", game.get_node("Sun").light_energy)
	for id in ["1342", "1274", "1278", "1216"]:
		var state: Dictionary = game.observe_reference(id)
		check(state.reference == id, "Public observation navigation " + id)
		await capture("reference-" + id)
		if id in ["1274", "1278"]:
			var home: Transform3D = game.camera.transform
			game.camera.translate_object_local(Vector3(.6,0,0))
			await capture("reference-" + id + "-side")
			game.camera.transform = home
			game.camera.rotate_y(PI)
			await capture("reference-" + id + "-back")
	# Verify F2 really returns to the existing controller after observation.
	var event := InputEventKey.new()
	event.physical_keycode = KEY_F2
	event.keycode = KEY_F2
	event.pressed = true
	game._unhandled_input(event)
	check(not game.photo_mode and not game.reference_observation, "F2 leaves observation")
	for source_state in ["flight", "high-speed", "docked"]:
		game.docked = source_state == "docked"
		game.throttle = .95 if source_state == "high-speed" else .4
		game.heading = 1.7
		game.vertical_speed = 30
		game.airship.velocity = Vector3(60,30,40)
		game.observe_reference("1342")
		game._unhandled_input(event)
		check(not game.docked and game.anchored and game.throttle == 0 and game.vertical_speed == 0 and game.airship.velocity == Vector3.ZERO and is_equal_approx(game.heading,game.airship.rotation.y-deg_to_rad(13)), "Observation restores safe hover from " + source_state)
	game.test_frozen = false
	game.testing = true
	game.test_override_input = true
	game.airship.position = Vector3(3550,1200,3300)
	game.world.update_focus(game.airship.position,true)
	game.test_input = Vector3(.12,.2,1)
	game.anchored = false
	game.throttle = .5
	var start: Vector3 = game.airship.position
	for i in range(240): await physics_frame
	var finish: Vector3 = game.airship.position
	check(start.distance_to(finish) > 10, "Physical flight in native high-altitude region", {"distance_m":start.distance_to(finish), "start":str(start), "finish":str(finish)})
	game.test_frozen = true
	await capture("high-altitude-flight")
	var passed := true
	for row in checks: passed = passed and row.passed
	var report := {"passed":passed,"checks":checks,"captures":captures,
		"source_game":"res://scenes/candidate39/Game39.tscn", "source_sha256":FileAccess.get_sha256("res://scenes/candidate39/Game39.tscn"),
		"display_driver":DisplayServer.get_name(), "renderer":RenderingServer.get_video_adapter_name(),
		"scope":"Live boot, native high-altitude assembly, environment switching, observation exit and 240 physical flight frames. Visual fidelity and full 21-view acceptance remain pending."}
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	game.queue_free()
	await frames(4)
	print("CANDIDATE39 CHECKS COMPLETE ",passed)
	quit(0 if passed else 1)
