extends SceneTree
## Actual native Game40c cloud integration boot. No script, shader, Environment or scenery replacement.
var output := ""
var checks: Array = []
var captures: Array = []
var game: Node3D
var checks_only := false
var sky_identity: int
var environment_identity: int

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
	var main_scene: String = ProjectSettings.get_setting('application/run/main_scene')
	check(main_scene == 'res://scenes/candidate41b/Game41b.tscn', 'Default project resource is this candidate',main_scene)
	game = load(main_scene).instantiate()
	root.add_child(game)
	game.sound_enabled = false
	game.test_frozen = true
	await frames(30)
	check(game.get_script().resource_path == "res://scripts/game40.gd", "Native game script active")
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
	environment_identity = game.get_node('Environment').environment.get_instance_id()
	sky_identity = game.get_node('Environment').environment.sky.get_instance_id()
	var cloud_parts := []
	for node in region.get_children():
		if str(node.name).begins_with('CloudSea_'): cloud_parts.append(node.find_children('*','MeshInstance3D',true,false).size())
	check(cloud_parts.size() == 25 and cloud_parts.count(20) == 25, 'Shared modeled cloud masses retained in all 25 placements', cloud_parts)
	var distant_count := 0
	var upper_count := 0
	for node in region.get_children():
		if str(node.name).begins_with('DistantCloudBank41_'): distant_count += 1
		if str(node.name).begins_with('UpperCloudBank41_'): upper_count += 1
	check(distant_count == 56 and upper_count == 12, 'Native cloud perimeter and upper banks retained', {'distant':distant_count,'upper':upper_count})
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
		if mesh.get_meta("persistent_material40",false): continue
		var expected: Material = game.airship.cloth_material if str(mesh.name) == "Flag" else game.airship.hull_material
		ship_bound = ship_bound and mesh.material_override == expected
	check(ship_bound and game.airship.hull_material.shader.code.contains("scene_fill"), "Airship authoritative material survives ready and receives environment")
	var lanterns := 0
	var live_carriage_lights := 0
	for mesh in ship_meshes:
		if mesh.get_meta("persistent_material40",false):
			if mesh.material_override is StandardMaterial3D and mesh.material_override.emission_enabled and mesh.material_override.emission_energy_multiplier > 0: lanterns += 1
	for light in game.scene_environment.lamps:
		if str(light.name).begins_with("CarriageLamp40_") and light.light_energy > 0: live_carriage_lights += 1
	check(lanterns == 2 and live_carriage_lights == 2, "Both physical carriage lamps retain glow material and active point light", {"glowing_fixtures":lanterns,"point_lights":live_carriage_lights})
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
	check(game.get_node('Environment').environment.get_instance_id() == environment_identity and game.get_node('Environment').environment.sky.get_instance_id() == sky_identity, 'Environment and Sky stay identical across daylight and night')
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
		if id == "1342":
			var energies := {}
			for light in game.scene_environment.lamps:
				if str(light.name).begins_with("CarriageLamp40_"):
					energies[light.get_instance_id()] = light.light_energy
					light.light_energy = 0
			await capture("reference-1342-carriage-lights-off")
			var lit := Image.load_from_file(output.path_join("reference-1342.png"))
			var unlit := Image.load_from_file(output.path_join("reference-1342-carriage-lights-off.png"))
			var center: Vector2 = game.camera.unproject_position(game.airship.global_position)
			var difference := 0.0
			for y in range(maxi(0,int(center.y)-150),mini(lit.get_height(),int(center.y)+150)):
				for x in range(maxi(0,int(center.x)-140),mini(lit.get_width(),int(center.x)+140)):
					var a := lit.get_pixel(x,y)
					var b := unlit.get_pixel(x,y)
					difference += absf(a.r-b.r)+absf(a.g-b.g)+absf(a.b-b.b)
			check(difference > .1, "Actual carriage point lights change rendered ship lighting", difference)
			for light in game.scene_environment.lamps:
				if energies.has(light.get_instance_id()): light.light_energy = energies[light.get_instance_id()]
		if id in ["1274", "1278"]:
			check(camera_clear(), "Effective indoor front camera free of collision " + id)
			var home: Transform3D = game.camera.transform
			game.camera.translate_object_local(Vector3(.35,0,0))
			await physics_frame
			check(camera_clear(), "Effective indoor side camera free of collision " + id)
			await capture("reference-" + id + "-side")
			game.camera.transform = home
			game.camera.rotate_y(PI)
			await capture("reference-" + id + "-back")
	game.observe_reference('1216')
	var cloud_camera: Transform3D = game.camera.transform
	game.camera.global_position += game.camera.global_basis.x*350
	await capture('reference-1216-translated-350m')
	game.camera.transform = cloud_camera
	game.camera.rotate_y(deg_to_rad(55))
	await capture('reference-1216-side')
	game.camera.transform = cloud_camera
	game.camera.rotate_y(PI)
	await capture('reference-1216-back')
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
	await verify_solids()
	var passed := true
	for row in checks: passed = passed and row.passed
	var report := {"passed":passed,"checks":checks,"captures":captures,
		"source_game":"res://scenes/candidate41b/Game41b.tscn", "source_sha256":FileAccess.get_sha256("res://scenes/candidate41b/Game41b.tscn"),
		"display_driver":DisplayServer.get_name(), "renderer":RenderingServer.get_video_adapter_name(),
		"scope":"Live boot, native high-altitude assembly, environment switching, observation exit and 240 physical flight frames. Visual fidelity and full 21-view acceptance remain pending."}
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	game.queue_free()
	await frames(4)
	print("CANDIDATE39 CHECKS COMPLETE ",passed)
	quit(0 if passed else 1)


func camera_clear() -> bool:
	var shape := SphereShape3D.new()
	shape.radius = .12
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = Transform3D(Basis.IDENTITY,game.camera.global_position)
	query.collision_mask = 5
	query.exclude = [game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()

func verify_solids() -> void:
	# Real existing player body moved against actual scene colliders; no probe
	# surrogate or changed collision settings. Test snapshots are restorable.
	game.photo_mode = true
	game.test_frozen = true
	var original: Transform3D = game.airship.transform
	var sky: Node3D = game.get_node("SkyRegion39")
	for name in ["CabinA", "CabinB"]:
		var cabin: Node3D = sky.get_node(name)
		game.airship.rotation = Vector3.ZERO
		# Approach a closed end wall from outside, above ground/cloud sea.
		game.airship.global_position = cabin.to_global(Vector3(0,1.5,25))
		await physics_frame
		var motion: Vector3 = cabin.global_basis * Vector3(0,0,-45)
		var hit: KinematicCollision3D = game.airship.move_and_collide(motion)
		check(hit != null and str(hit.get_collider().get_path()).contains("/"+name+"/"), "Player body blocked by real cabin solid " + name, {"collider":str(hit.get_collider().get_path()) if hit != null else "none", "travel":str(hit.get_travel()) if hit != null else "none"})
	var island: Node3D = sky.get_node("FloatingIsland_0")
	game.airship.rotation = Vector3.ZERO
	game.airship.global_position = island.global_position + Vector3(0,140,0)
	await physics_frame
	var island_hit: KinematicCollision3D = game.airship.move_and_collide(Vector3(0,-260,0))
	check(island_hit != null and str(island_hit.get_collider().get_path()).contains("FloatingIsland_0"), "Player body blocked by real floating island", {"collider":str(island_hit.get_collider().get_path()) if island_hit != null else "none", "travel":str(island_hit.get_travel()) if island_hit != null else "none"})
	game.airship.transform = original
	# Physical rays inside both cabins must hit opaque wall lining between
	# boards while the offset window aperture retains a real exterior ray.
	for name in ["CabinA","CabinB"]:
		var cabin: Node3D = sky.get_node(name)
		var origin: Vector3 = cabin.to_global(Vector3(0,1.5,0))
		var closed := PhysicsRayQueryParameters3D.create(origin,cabin.to_global(Vector3(0,1.5,5)),5,[game.airship.get_rid()])
		var hit := game.get_world_3d().direct_space_state.intersect_ray(closed)
		check(not hit.is_empty() and str(hit.collider.get_path()).contains(name), "Cabin closed wall physically opaque " + name)
		# Approach from just outside: identify true closed end wall lining,
		# including the previous bottom-corner slit, not furniture or roof.
		var width: float = 6.0 if name == "CabinA" else 6.2
		var depth: float = 4.4 if name == "CabinA" else 4.6
		var samples := 0
		var lining_hits := 0
		var failed_rays: Array = []
		for height in [.015,.15,1.4,2.5]:
			for x in [-width/2-.01,-width/2+.04,-1.5,-.24,0.,.24,1.5,width/2-.04,width/2+.01]:
				var start: Vector3 = cabin.to_global(Vector3(x,height,depth/2+.22))
				var end: Vector3 = cabin.to_global(Vector3(x,height,depth/2-.18))
				var query := PhysicsRayQueryParameters3D.create(start,end,5,[game.airship.get_rid()])
				var result := game.get_world_3d().direct_space_state.intersect_ray(query)
				samples += 1
				if not result.is_empty() and str(result.collider.get_path()).contains("_end_wall_lining40_"): lining_hits += 1
				else: failed_rays.append({"x":x,"height":height,"collider":str(result.collider.get_path()) if not result.is_empty() else "none"})
		check(lining_hits == samples, "Cabin end-wall and bottom/corner seams backed by actual lining " + name, {"samples":samples,"lining_hits":lining_hits,"failed":failed_rays})
		var side := -1.0 if name == "CabinA" else 1.0
		# The prior A sample struck its slanted structural window bar. Select a
		# pane opening, retain the failure and additionally test that bar solid.
		var pane_z := .1 if name == "CabinA" else -.45
		var hole_start: Vector3 = cabin.to_global(Vector3(side*(width/2-.2),2.0,pane_z))
		var hole_end: Vector3 = cabin.to_global(Vector3(side*(width/2+4),2.0,pane_z))
		var window_query := PhysicsRayQueryParameters3D.create(hole_start,hole_end,5,[game.airship.get_rid()])
		var window_hit := game.get_world_3d().direct_space_state.intersect_ray(window_query)
		check(window_hit.is_empty(), "Cabin genuine window aperture remains open " + name, str(window_hit.collider.get_path()) if not window_hit.is_empty() else "clear exterior ray")
		if name == "CabinA":
			var bar_query := PhysicsRayQueryParameters3D.create(cabin.to_global(Vector3(side*(width/2-.2),2.0,-.45)),cabin.to_global(Vector3(side*(width/2+4),2.0,-.45)),5,[game.airship.get_rid()])
			var bar_hit := game.get_world_3d().direct_space_state.intersect_ray(bar_query)
			check(not bar_hit.is_empty() and str(bar_hit.collider.get_path()).contains("winbar_v"), "CabinA original slanted window bar remains genuinely solid", str(bar_hit.collider.get_path()) if not bar_hit.is_empty() else "none")
