extends SceneTree
## Offline copy of verified native world: no generator or ready callbacks.
const DEST := "res://scenes/candidate40/"
var shaders := {}
var materials := {}
var report := {"baseline_sha256":"", "changes":[], "ship_bounds":[]}

func _initialize() -> void: call_deferred("build")

func own(node: Node, root_node: Node) -> void:
	node.scene_file_path = ""
	if node != root_node: node.owner = root_node
	for child in node.get_children(): own(child, root_node)

func shaded(source: Material) -> Material:
	if source == null: return null
	if materials.has(source): return materials[source]
	var result: Material = source
	if source is ShaderMaterial:
		result = source.duplicate()
		if not shaders.has(source.shader):
			var code: String = source.shader.code
			var before := code
			# Restore real engine ambient on native lit surfaces. Environment
			# changes lighting, rather than painting the viewport or moving a rig.
			code = code.replace(",ambient_light_disabled", "").replace(", ambient_light_disabled", "")
			if code.contains("EMISSION=ALBEDO*.93;"):
				code = code.replace("EMISSION=ALBEDO*.93;", "EMISSION=vec3(0.);")
				code = code.replace("max(dot(NORMAL,LIGHT),0.)*.10/PI", "max(dot(NORMAL,LIGHT),0.)/PI")
				# Scene fill is retained for metadata/other materials, while hull
				# colour now receives blue moon and warm carriage lights directly.
				code = code.replace("ALBEDO*=mix(vec3(1.),scene_fill,.35);", "")
				code = code.replace("EMISSION*=scene_fill;", "")
			var shader := Shader.new()
			shader.code = code
			shaders[source.shader] = shader
			if code != before: report.changes.append({"type":"shader", "from_hash":before.hash(), "to_hash":code.hash()})
		result.shader = shaders[source.shader]
	materials[source] = result
	return result

func visit(node: Node) -> void:
	if node.get_script() == load("res://scripts/asset_instance.gd"):
		node.surface_material = shaded(node.surface_material)
	if node.get_script() == load("res://scripts/airship_body.gd"):
		node.hull_material = shaded(node.hull_material)
		node.cloth_material = shaded(node.cloth_material)
	if node is GeometryInstance3D:
		if node.material_override != null: node.material_override = shaded(node.material_override)
		if node is MeshInstance3D:
			for i in range(node.get_surface_override_material_count()):
				if node.get_surface_override_material(i) != null:
					node.set_surface_override_material(i, shaded(node.get_surface_override_material(i)))
	for child in node.get_children(): visit(child)

func cabin(name: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file("res://assets/cabins40/"+name+".glb",state)==OK)
	var node: Node3D = document.generate_scene(state)
	for part in node.find_children("*","MeshInstance3D",true,false):
		var body := StaticBody3D.new()
		body.name = "Solid"
		body.collision_layer = 5
		body.collision_mask = 2
		var shape := CollisionShape3D.new()
		shape.name = "Shape"
		shape.shape = part.mesh.create_trimesh_shape()
		shape.shape.backface_collision = true
		body.add_child(shape)
		part.add_child(body)
	own(node,node)
	var packed := PackedScene.new()
	assert(packed.pack(node)==OK)
	assert(ResourceSaver.save(packed,DEST+name+".tscn")==OK)
	return node

func warm_light(parent: Node3D, name: String, position: Vector3, energy: float, radius: float) -> void:
	var light := OmniLight3D.new()
	light.name = name
	light.position = position
	light.light_color = Color(1,.60,.22)
	light.light_energy = energy
	light.omni_range = radius
	parent.add_child(light)

func carriage_lantern(parent: Node3D, position: Vector3, index: int) -> void:
	var fixture := MeshInstance3D.new()
	fixture.name = "CarriageLantern40_"+str(index)
	fixture.position = position
	var globe := CylinderMesh.new()
	globe.top_radius = .16
	globe.bottom_radius = .16
	globe.height = .42
	globe.radial_segments = 6
	fixture.mesh = globe
	var glow := StandardMaterial3D.new()
	glow.albedo_color = Color(1,.68,.24)
	glow.emission_enabled = true
	glow.emission = Color(1,.45,.11)
	glow.emission_energy_multiplier = 2
	fixture.material_override = glow
	parent.add_child(fixture)
	warm_light(parent,"CarriageLamp40_"+str(index),position,2.2,5.5)

func build() -> void:
	assert(not FileAccess.file_exists(DEST+"Game40.tscn"))
	DirAccess.make_dir_recursive_absolute(DEST)
	report.baseline_sha256 = FileAccess.get_sha256("res://scenes/candidate39/Game39.tscn")
	var game: Node3D = load("res://scenes/candidate39/Game39.tscn").instantiate()
	visit(game)
	game.set_script(load("res://scripts/game40.gd"))
	var environment: Node = game.get_node("SceneEnvironment39")
	environment.name = "SceneEnvironment40"
	environment.set_script(load("res://scripts/environment40.gd"))
	var world: Node3D = game.get_node("World")
	world.stream_terrain_material = shaded(world.stream_terrain_material)
	world.stream_world_material = shaded(world.stream_world_material)
	world.stream_cloud_material = shaded(world.stream_cloud_material)
	var sky: Node3D = game.get_node("SkyRegion39")
	for pair in [["CabinA","cabin_a"],["CabinB","cabin_b"]]:
		var old: Node3D = sky.get_node(pair[0])
		var replacement := cabin(pair[1])
		replacement.name = pair[0]
		replacement.transform = old.transform
		# Keep original actual point-light locations/energy, not camera lights.
		for child in old.get_children():
			if child is Light3D: replacement.add_child(child.duplicate())
		sky.remove_child(old)
		old.free()
		sky.add_child(replacement)
	var airship: Node3D = game.get_node("Airship")
	for part in airship.get_node("Visuals").find_children("*","MeshInstance3D",true,false):
		report.ship_bounds.append({"name":str(part.name),"aabb":str(part.get_aabb()),"transform":str(part.transform)})
	carriage_lantern(airship.get_node("Visuals"),Vector3(-2.4,-2.1,-1.3),0)
	carriage_lantern(airship.get_node("Visuals"),Vector3(2.4,-2.1,-1.3),1)
	own(game,game)
	var packed := PackedScene.new()
	assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,DEST+"Game40.tscn")==OK)
	report.candidate_sha256 = FileAccess.get_sha256(DEST+"Game40.tscn")
	var file := FileAccess.open(DEST+"build-report.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	game.free()
	print("ROUND40 NATIVE BUILT ",report.candidate_sha256)
	quit()
