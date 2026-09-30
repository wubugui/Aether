extends Node3D

const HOME_CAMERA = Vector3(0.0, 145.0, 250.0)
const HOME_SHIP = Vector3(-4.15, 136.8, 184.0)
const PITCH = -3.5
var camera: Camera3D
var airship: Node3D
var propeller: Node3D
var hud: Control
var sea_material: ShaderMaterial
var elapsed := 0.0
var speed := 0.0
var throttle := 0.0
var heading := 0.0
var altitude := 0.0
var fuel := 0.62
var shield := 0.71
var health := 0.74
var anchored := true
var photo_mode := false
var help_open := false
var orbit := Vector2.ZERO
var screenshot_pending := false
var wireframe := false
var wire_items: Array[Dictionary] = []

func _ready() -> void:
	# Use the same authored nodes visible in the editor; edits carry into play.
	var world := get_node("World3D")
	airship = world.get_node("Airship")
	propeller = airship.get_node("Propeller")
	camera = world.get_node("ReferenceCamera")
	sea_material = world.get_node("Landscape/Landscape/Water").material_override
	camera.make_current()
	var canvas := CanvasLayer.new()
	canvas.name = "Interface"
	add_child(canvas)
	hud = preload("res://scripts/hud.gd").new()
	hud.game = self
	canvas.add_child(hud)
	reset_view()
	if "--orbit" in OS.get_cmdline_user_args(): orbit = Vector2(0.42,0.10)
	if "--wireframe" in OS.get_cmdline_user_args():
		set_wireframe(true)
	if "--capture" in OS.get_cmdline_user_args():
		photo_mode = true
		capture_after_frames()
	if "--smoke-test" in OS.get_cmdline_user_args():
		run_smoke_test()
	if "--integration-test" in OS.get_cmdline_user_args():
		run_integration_test()

func reset_view() -> void:
	heading = 0
	altitude = 0
	elapsed = 0
	speed = 0
	throttle = 0
	orbit = Vector2.ZERO
	anchored = true
	airship.position = HOME_SHIP
	airship.rotation_degrees = Vector3(0, 13, 0)
	propeller.rotation = Vector3(0.15,deg_to_rad(20),0)
	camera.position = HOME_CAMERA
	camera.rotation_degrees = Vector3(PITCH, 0, 0)
	fuel = 0.62
	shield = 0.71
	health = 0.74
	if is_instance_valid(hud): hud.queue_redraw()

func _process(delta: float) -> void:
	if not photo_mode:
		elapsed += delta
		var turn := float(Input.is_physical_key_pressed(KEY_A)) - float(Input.is_physical_key_pressed(KEY_D))
		var lift := float(Input.is_physical_key_pressed(KEY_E)) - float(Input.is_physical_key_pressed(KEY_Q))
		var power := float(Input.is_physical_key_pressed(KEY_W)) - float(Input.is_physical_key_pressed(KEY_S))
		if power != 0 or turn != 0 or lift != 0:
			anchored = false
		throttle = clampf(throttle + power * delta * 0.30, 0.0, 1.0)
		heading += turn * delta * 0.28
		altitude = clampf(altitude + lift * delta * 8, -55, 120)
		speed = move_toward(speed, 0.0 if anchored else throttle * 26.0, delta * 5.0)
		var forward := Vector3(-sin(heading), 0, -cos(heading))
		airship.position += forward * speed * delta
		airship.position.y = HOME_SHIP.y + altitude + sin(elapsed * 0.7) * 0.065
		airship.rotation_degrees = Vector3(sin(elapsed * 0.6) * 0.25, 13 + rad_to_deg(heading), -turn * 2.4)
		propeller.rotation.x += delta * (1.2 + speed * 0.9)
		if speed > 0:
			fuel = maxf(0.0, fuel - delta * throttle * 0.0004)
			if fuel == 0: throttle = 0
		sea_material.set_shader_parameter("phase", elapsed)
	var offset := airship.position - HOME_SHIP
	camera.position = HOME_CAMERA + offset
	if orbit.length() > 0.001:
		var relative := (HOME_CAMERA - HOME_SHIP).rotated(Vector3.UP, orbit.x)
		relative = relative.rotated(Vector3.RIGHT, orbit.y)
		camera.position = airship.position + relative
		camera.look_at(airship.position + Vector3(0, 4, 0))
	else:
		camera.rotation_degrees = Vector3(PITCH, 0, 0)
	hud.queue_redraw()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_R: reset_view()
			KEY_SPACE:
				anchored = not anchored
			KEY_F1: help_open = not help_open
			KEY_F2: photo_mode = not photo_mode
			KEY_F3:
				set_wireframe(not wireframe)
			KEY_F12: save_screenshot()
			KEY_ESCAPE:
				if help_open: help_open = false
				else: orbit = Vector2.ZERO
			KEY_F11:
				var mode := DisplayServer.window_get_mode()
				DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if mode == DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		orbit += event.relative * Vector2(-0.004, -0.003)
		orbit.y = clampf(orbit.y, -0.55, 0.5)

func activate_ability(index: int) -> void:
	match index:
		0: altitude = minf(altitude + 8, 120)
		1:
			anchored = false
			throttle = 1.0 if throttle < 0.99 else 0.3
		2: fuel = minf(1.0, fuel + 0.10)
		3: anchored = not anchored

func collect_meshes(node: Node, result: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D and node.is_visible_in_tree() and not node.has_meta("wire_debug"):
		result.append(node)
	for child in node.get_children(): collect_meshes(child,result)

func set_wireframe(enabled: bool) -> void:
	wireframe = enabled
	if wire_items.is_empty() and enabled:
		var surfaces: Array[MeshInstance3D] = []
		collect_meshes(get_node("World3D"),surfaces)
		var line_material := StandardMaterial3D.new()
		line_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		line_material.albedo_color = Color("294e61")
		line_material.no_depth_test = true
		var clay := StandardMaterial3D.new()
		clay.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		clay.albedo_color = Color("d7e0dd")
		clay.cull_mode = BaseMaterial3D.CULL_DISABLED
		for source in surfaces:
			var faces := source.mesh.get_faces()
			var edges := PackedVector3Array()
			for i in range(0,faces.size(),3):
				edges.append_array(PackedVector3Array([faces[i],faces[i+1],faces[i+1],faces[i+2],faces[i+2],faces[i]]))
			var arrays := []
			arrays.resize(Mesh.ARRAY_MAX)
			arrays[Mesh.ARRAY_VERTEX] = edges
			var edge_mesh := ArrayMesh.new()
			edge_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_LINES,arrays)
			var instance := MeshInstance3D.new()
			instance.name = "TopologyEdges"
			instance.set_meta("wire_debug",true)
			instance.mesh = edge_mesh
			instance.material_override = line_material
			source.add_child(instance)
			wire_items.append({"source":source,"edges":instance,"material":source.material_override,"clay":clay})
	for item in wire_items:
		item.edges.visible = enabled
		item.source.material_override = item.clay if enabled else item.material

func save_screenshot() -> void:
	if screenshot_pending: return
	screenshot_pending = true
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var folder := ProjectSettings.globalize_path("res://captures")
	DirAccess.make_dir_recursive_absolute(folder)
	var stamp := Time.get_datetime_string_from_system().replace(":", "-")
	var path := folder.path_join("airship-" + stamp + ".png")
	var err := img.save_png(path)
	print("SCREENSHOT ", path, " status=", err)
	screenshot_pending = false

func capture_after_frames() -> void:
	if "--flight" in OS.get_cmdline_user_args():
		heading = 0.8
		altitude = 22
		throttle = 0.7
		photo_mode = false
		for i in range(90): await get_tree().process_frame
		photo_mode = true
	for i in range(12): await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var output := "res://captures/preview.png"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
	var err := img.save_png(ProjectSettings.globalize_path(output))
	print("CAPTURE ", output, " ", img.get_size(), " status=", err)
	get_tree().quit(err)

func run_smoke_test() -> void:
	await get_tree().process_frame
	assert(camera.current)
	assert(airship.get_child_count() == 2)
	activate_ability(0)
	assert(altitude == 8)
	activate_ability(1)
	assert(throttle == 1.0 and not anchored)
	activate_ability(2)
	assert(is_equal_approx(fuel, 0.72))
	activate_ability(3)
	assert(anchored)
	reset_view()
	assert(airship.position == HOME_SHIP and camera.position == HOME_CAMERA)
	assert(heading == 0 and speed == 0 and throttle == 0)
	print("SMOKE PASS: scene, camera, lift, throttle, fuel, anchor, reset")
	get_tree().quit()

func simulated_key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = code
	event.keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)

func run_integration_test() -> void:
	await get_tree().process_frame
	Engine.max_fps = 60
	simulated_key(KEY_W,true)
	simulated_key(KEY_E,true)
	simulated_key(KEY_D,true)
	await get_tree().create_timer(0.5).timeout
	simulated_key(KEY_W,false)
	simulated_key(KEY_E,false)
	simulated_key(KEY_D,false)
	assert(speed > 0 and throttle > 0)
	assert(altitude > 0 and heading < 0)
	assert(airship.position.distance_to(HOME_SHIP) > 0.1)
	simulated_key(KEY_F3,true)
	simulated_key(KEY_F3,false)
	await get_tree().process_frame
	assert(wireframe)
	assert(wire_items.size() > 30)
	simulated_key(KEY_R,true)
	simulated_key(KEY_R,false)
	await get_tree().process_frame
	assert(altitude == 0 and heading == 0 and throttle == 0)
	simulated_key(KEY_F3,true)
	simulated_key(KEY_F3,false)
	await get_tree().process_frame
	assert(not wireframe)
	print("INTEGRATION PASS: W/E/D input, 3D flight motion, wireframe inspection, R reset")
	get_tree().quit()
