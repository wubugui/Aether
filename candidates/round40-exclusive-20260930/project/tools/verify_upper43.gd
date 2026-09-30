extends SceneTree
## Native Game42d regression checks plus allocation and actual transform-motion checks.
## GPU captures are required for visual evidence; checks-only never claims visibility.
const MultiMeshCopy = preload("res://tools/multimesh_copy42d.gd")
var output := ""
var checks: Array = []
var captures: Array = []
var game: Node3D
var checks_only := false
var sky_identity: int
var full_scan := false
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
	check(image.save_png(path) == OK, "Rendered image saved " + name)
	var p: Vector3 = game.camera.position
	captures.append({"name": name, "image": path, "sha256": FileAccess.get_sha256(path),
		"position": [p.x,p.y,p.z], "camera_transform": str(game.camera.transform),
		"reference": game.scene_environment.current_reference, "reference_identity": "assets/reference.jpg" if name in ["boot-controller-original","boot-day"] else "ref/"+game.scene_environment.current_reference,
		"fov": game.camera.fov, "world_instance": game.world.get_instance_id(),
		"game_script": game.get_script().resource_path, "pixels": [image.get_width(),image.get_height()]})

func run_full() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Use an actual rendering server even for --checks-only; dummy MultiMesh storage cannot validate allocation")
		quit(2)
		return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output = arg.trim_prefix("--output-dir=")
		if arg == "--checks-only": checks_only = true
	assert(not output.is_empty())
	assert(not DirAccess.dir_exists_absolute(output), "Use a new evidence directory; never overwrite historical captures")
	DirAccess.make_dir_recursive_absolute(output)
	var main_scene: String = 'res://scenes/candidate43/Game43.tscn'
	print('Project default (not modified by verifier): ',main_scene)
	# Explicit candidate path permits testing without changing the project default.
	game = load('res://scenes/candidate43/Game43.tscn').instantiate()
	await verify_particle_payloads()
	root.add_child(game)
	game.sound_enabled = false
	game.test_frozen = true
	await frames(30)
	check(game.get_script().resource_path == "res://scripts/game42b.gd", "Native game script active")
	check(game.scene_environment.current_reference == "1343", "Normal boot starts in daylight")
	check(game.world.core.size() == 208, "Existing 208 authored terrain tiles retained")
	check(game.world.layout.props.size() >= 54797, "Authored scatter retained", game.world.layout.props.size())
	await capture('boot-controller-original')
	var weather: Node3D = game.get_node('Weather42b')
	check(not weather.get_node('Rain').visible and not weather.get_node('Snow').visible,'Daylight default has no precipitation')
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
		if str(node.name).begins_with('UpperCloudBank43_'): upper_count += 1
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
	# Propeller/cloud animation can change; record exact image identity but do
	# not require pixel equality to a moving world. Environment uniforms reset.
	check(is_equal_approx(game.get_node("Sun").light_energy, .85), "Daylight energy restored after night", game.get_node("Sun").light_energy)
	for id in ["1342", "1274", "1278", "1216"]:
		var state: Dictionary = game.observe_reference(id)
		check(state.reference == id, "Public observation navigation " + id)
		await capture("reference-" + id)
		if id == "1342" and not checks_only:
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
	await verify_upper43()
	await verify_weather()
	await verify_particle_motion()
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
		"source_game":"res://scenes/candidate43/Game43.tscn", "source_sha256":FileAccess.get_sha256("res://scenes/candidate43/Game43.tscn"),
		"hardware_gpu_acceptance": false, "visual_acceptance": false, "software_renderer": is_software43(), "display_driver":DisplayServer.get_name(), "renderer":RenderingServer.get_video_adapter_name(),
		"scope":"Live boot, native high-altitude assembly, environment switching, observation exit and 240 physical flight frames. Visual fidelity and full 21-view acceptance remain pending."}
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	game.queue_free()
	await frames(4)
	print("CANDIDATE42D CHECKS COMPLETE ",passed)
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

func image_difference(a_path: String,b_path: String) -> float:
	var a := Image.load_from_file(a_path)
	var b := Image.load_from_file(b_path)
	var result := 0.0
	for y in range(180,a.get_height()-70,2):
		for x in range(60,a.get_width()-60,2):
			var av := a.get_pixel(x,y);var bv := b.get_pixel(x,y)
			result += absf(av.r-bv.r)+absf(av.g-bv.g)+absf(av.b-bv.b)
	return result

func verify_weather() -> void:
	var weather: Node3D = game.get_node('Weather42b')
	weather.time_scale = 0.0
	game.observe_reference('1216');weather.seek_time(.05)
	check(weather.cloud_lightning and not weather.coastal_lightning and weather.phase == 1,'Cloud-region lightning controls real persistent storm nodes')
	await capture('reference-1216-lightning-lit')
	weather.local_illumination_enabled = false
	await capture('reference-1216-lightning-local-light-off')
	if not checks_only:
		var illumination_difference := image_difference(output.path_join('reference-1216-lightning-lit.png'),output.path_join('reference-1216-lightning-local-light-off.png'))
		check(illumination_difference > .1,'Actual lightning local light changes rendered cloud illumination',illumination_difference)
	weather.local_illumination_enabled = true
	game.observe_reference('1341');weather.seek_time(.05)
	check(weather.get_node('Rain').visible and weather.get_node('Rain').multimesh.visible_instance_count == 1800 and weather.coastal_lightning,'Storm state activates native rain and coastal bolts')
	await capture('reference-1341-lightning')
	weather.time_scale = 1.0
	var before_time: float = weather.time_seconds
	await frames(60)
	check(weather.time_seconds > before_time and weather.get_node('Rain').material_override.get_shader_parameter('precipitation_time') > before_time,'Rain simulation progresses in normal live controller')
	weather.time_scale = 0.0
	game.observe_reference('1276')
	check(weather.get_node('Snow').visible and weather.get_node('Snow').multimesh.visible_instance_count == 600 and not weather.get_node('Rain').visible,'Snow changes actual particle field and stops rain')
	game.observe_reference('1344')
	check(weather.get_node('Rainbow').visible and not weather.get_node('Snow').visible,'Rainbow has physical native spectrum mesh in the same world')
	for entry in game.scene_environment.plan:
		var id := str(entry.ref)
		if not full_scan and id not in ["1343","1128","1216","1342"]: continue
		if id in ['1342','1274','1278','1216']: continue
		var state: Dictionary = game.observe_reference(id)
		check(state.reference == id,'Full public observation navigation '+id)
		await capture('reference-'+id)
	weather.time_scale = 1.0
func verify_particle_payloads() -> void:
	var baseline: Node3D = load('res://scenes/candidate42b/Game42b.tscn').instantiate()
	var previous: Node3D = load('res://scenes/candidate42c/Game42c.tscn').instantiate()
	for name in ['Rain','Snow']:
		var actual: MultiMesh = game.get_node('Weather42b/'+name).multimesh
		var source: MultiMesh = baseline.get_node('Weather42b/'+name).multimesh
		var prior: MultiMesh = previous.get_node('Weather42b/'+name).multimesh
		check(actual.transform_format == source.transform_format and actual.use_colors == source.use_colors and actual.use_custom_data == source.use_custom_data, name+' format and payload flags preserved')
		check(actual.instance_count == source.instance_count, name+' allocation count preserved', actual.instance_count)
		var stride := 12 + (4 if actual.use_colors else 0) + (4 if actual.use_custom_data else 0)
		check(actual.buffer.size() == actual.instance_count*stride, name+' complete allocated buffer', actual.buffer.size())
		var expected: MultiMesh = MultiMeshCopy.copy(source)
		MultiMeshCopy.restore_weather_custom_data(expected)
		MultiMeshCopy.place_weather42c(expected)
		var payload_ok := true
		var transforms_ok := actual.instance_count == expected.instance_count
		for i in range(actual.instance_count):
			if source.use_colors: payload_ok = payload_ok and source.get_instance_color(i).is_equal_approx(actual.get_instance_color(i))
			if source.use_custom_data: payload_ok = payload_ok and expected.get_instance_custom_data(i).is_equal_approx(actual.get_instance_custom_data(i))
			transforms_ok = transforms_ok and actual.get_instance_transform(i).is_equal_approx(expected.get_instance_transform(i))
		check(payload_ok,name+' all original colors and authored 42b seeded custom payloads retained')
		check(transforms_ok,name+' all authored 42c seeded initial transforms recovered')
		check(actual.mesh.get_aabb().is_equal_approx(prior.mesh.get_aabb()),name+' 42c particle mesh size retained')
	# Off-tree historical Sky allocations must finish before releasing copies.
	for frame in range(3): await process_frame
	await RenderingServer.frame_post_draw
	baseline.free()
	previous.free()

func verify_particle_motion() -> void:
	var weather: Node3D = game.get_node('Weather42b')
	weather.time_scale = 0.0
	for entry in [{'name':'Rain','reference':'1341','speed':36.0,'drift':.22},{'name':'Snow','reference':'1276','speed':5.0,'drift':.12}]:
		game.observe_reference(entry.reference)
		weather.seek_time(1.0)
		var node: MultiMeshInstance3D = weather.get_node(entry.name)
		var before: Transform3D = node.multimesh.get_instance_transform(0)
		weather.seek_time(1.5)
		var after: Transform3D = node.multimesh.get_instance_transform(0)
		var expected := before.origin
		expected.y = fposmod(expected.y+80.0-.5*float(entry.speed),160.0)-80.0
		expected.x = fposmod(expected.x+110.0+.5*float(entry.speed)*float(entry.drift),220.0)-110.0
		check(not before.is_equal_approx(after) and expected.is_equal_approx(after.origin),entry.name+' actual instance transforms move at expected speed',{'before':str(before.origin),'after':str(after.origin)})
		await capture('particles-'+entry.name.to_lower()+'-time-1_5')
		weather.seek_time(1.0)
		check(before.is_equal_approx(node.multimesh.get_instance_transform(0)),entry.name+' seek deterministically restores particle transform')
		await capture('particles-'+entry.name.to_lower()+'-time-1_0')
	weather.time_scale = 1.0


func verify_upper43() -> void:
	var region: Node3D = game.get_node("SkyRegion39")
	for i in range(12):
		var cloud: Node3D = region.get_node("UpperCloudBank43_%d" % i)
		check(cloud.find_children("*","MeshInstance3D",true,false).size()==11,"Native 11-part upper cloud %d" % i)
		check(cloud.scale.is_equal_approx(Vector3.ONE*2.0),"Undistorted volumetric upper cloud %d" % i)
	# All views share one world. Side/back/translation catches view-specific tricks.
	for entry in game.scene_environment.plan:
		var id := str(entry.ref)
		if not full_scan and id not in ["1343","1128","1216","1342"]: continue
		game.observe_reference(id)
		await capture("upper43-all-reference-"+id)
		if not full_scan and id != "1216": continue
		var home: Transform3D = game.camera.transform
		game.camera.rotate_y(deg_to_rad(55))
		await capture("upper43-all-reference-"+id+"-side")
		game.camera.transform = home
		game.camera.rotate_y(PI)
		await capture("upper43-all-reference-"+id+"-back")
		game.camera.transform = home
		if id not in ["1274","1278"]:
			game.camera.global_position += game.camera.global_basis.x*350
			await capture("upper43-all-reference-"+id+"-translated")
	game.scene_environment.apply_reference("1343")
	for i in range(3 if full_scan else 0):
		var cloud: Node3D = region.get_node("UpperCloudBank43_%d" % i)
		for pair in [["front",Vector3(0,0,1800)],["side",Vector3(1800,0,0)],["back",Vector3(0,0,-1800)],["underside",Vector3(0,-1000,850)]]:
			game.camera.global_position = cloud.global_position+pair[1]
			game.camera.look_at(cloud.global_position,Vector3.UP)
			await capture("upper43-native-%d-%s" % [i,pair[0]])
	# Diagnostic-only group isolation. Visibility is fully restored after each capture.
	# These images are explicitly excluded from candidate beauty/acceptance evidence.
	for id in ["1343","1128","1216"]:
		game.observe_reference(id)
		await capture("diagnostic43-"+id+"-all-clouds")
		var groups := {"upper":[],"sea":[],"distant":[],"world":[game.get_node("World/Clouds")],"coastal":[]}
		for n in region.get_children():
			if str(n.name).begins_with("UpperCloudBank43_"): groups.upper.append(n)
			if str(n.name).begins_with("CloudSea_"): groups.sea.append(n)
			if str(n.name).begins_with("DistantCloudBank41_"): groups.distant.append(n)
		for n in game.get_node("NativeCoastalSky27f").get_children():
			if "cloud" in str(n.name).to_lower(): groups.coastal.append(n)
		for label in groups:
			var visibility := []
			for n in groups[label]:
				visibility.append(n.visible)
				n.visible = false
			await capture("diagnostic43-"+id+"-without-"+label)
			for j in range(groups[label].size()): groups[label][j].visible = visibility[j]


func is_software43() -> bool:
	var adapter := RenderingServer.get_video_adapter_name().to_lower()
	return "llvmpipe" in adapter or "softpipe" in adapter or DisplayServer.get_name()=="headless"

func run() -> void:
	if DisplayServer.get_name()=="headless":
		push_error("Use a rendering backend for capture; static parse is --check-only")
		quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg == "--full": full_scan = true
	if full_scan:
		await run_full()
		return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	assert(not output.is_empty())
	assert(not FileAccess.file_exists(output.path_join("report.json")),"Do not overwrite existing evidence")
	DirAccess.make_dir_recursive_absolute(output)
	game=load("res://scenes/candidate43/Game43.tscn").instantiate()
	root.add_child(game)
	game.sound_enabled=false
	game.test_frozen=true
	await frames(30)
	check(game.world.core.size()==208,"Existing 208 authored terrain tiles retained")
	check(game.world.layout.props.size()>=54797,"Authored scatter retained")
	for pair in [["Rain",1800],["Snow",1200]]:
		var mm: MultiMesh=game.get_node("Weather42b/"+pair[0]).multimesh
		check(mm.instance_count==pair[1] and mm.buffer.size()==pair[1]*16,"Persisted weather buffer "+pair[0],mm.buffer.size())
	await capture("boot-controller-original")
	await verify_upper43()
	var passed := true
	for row in checks: passed=passed and row.passed
	var report := {"passed":passed,"functional_passed":passed,"hardware_gpu_acceptance":false,"visual_acceptance":false,"software_renderer":is_software43(),"renderer":RenderingServer.get_video_adapter_name(),"source_game":"res://scenes/candidate43/Game43.tscn","source_sha256":FileAccess.get_sha256("res://scenes/candidate43/Game43.tscn"),"checks":checks,"captures":captures,"scope":"Focused diagnostic pass only. Use --full for inherited regression and all-reference side/back/translation evidence. Diagnostic isolation is temporary and fully restored; excluded from fidelity acceptance."}
	var f := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"  "));f.close()
	game.queue_free();await frames(4)
	quit(0 if passed else 1)
