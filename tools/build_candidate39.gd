extends SceneTree
## Offline native assembly only. Never attaches input source to SceneTree.
const DEST := "res://scenes/candidate39/"
const KIT := "res://blender/sky_kit_38/hub_output_v2/"
var shader_cache: Dictionary = {}
var material_cache: Dictionary = {}
var report: Dictionary = {"source_game": "res://captures/candidate_opening38/Game38.tscn", "assets": [], "shaders": [], "geometry_changed": false}

func _initialize() -> void: call_deferred("build")

func owner_tree(node: Node, owner_node: Node) -> void:
	# Flatten instance membership when expanding all descendants under the
	# candidate owner. Retaining the old scene_file_path alongside expanded
	# nodes makes PackedScene instantiate replacement subtrees and orphan RIDs.
	node.scene_file_path = ""
	node.owner = owner_node
	for child in node.get_children(): owner_tree(child, owner_node)

func asset(name: String, collide: bool) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file(KIT + name + ".glb", state) == OK)
	var node: Node3D = doc.generate_scene(state)
	node.name = name
	var triangles := 0
	for mesh in node.find_children("*", "MeshInstance3D", true, false):
		triangles += mesh.mesh.get_faces().size() / 3
		if collide:
			var body := StaticBody3D.new()
			body.name = "Solid"
			body.collision_layer = 5
			body.collision_mask = 2
			mesh.add_child(body)
			var shape := CollisionShape3D.new()
			shape.name = "Shape"
			shape.shape = mesh.mesh.create_trimesh_shape()
			body.add_child(shape)
	owner_tree_children(node)
	var packed := PackedScene.new()
	assert(packed.pack(node) == OK)
	var destination := DEST + name + ".tscn"
	assert(ResourceSaver.save(packed, destination) == OK)
	report.assets.append({"name": name, "source": KIT + name + ".glb", "source_sha256": FileAccess.get_sha256(KIT + name + ".glb"), "triangles": triangles, "collision": collide, "native": destination})
	node.free()
	return load(destination).instantiate()

func owner_tree_children(node: Node) -> void:
	node.scene_file_path = ""
	for child in node.get_children(): owner_tree(child, node)

func patch_shader(original: Shader) -> Shader:
	if shader_cache.has(original): return shader_cache[original]
	var code := original.code
	if not code.contains("shader_type spatial"):
		shader_cache[original] = original
		return original
	# Explicit material uniforms are persisted in the native candidate, never
	# injected by the screenshot script. Source resources stay unchanged.
	var header := "\nuniform vec3 scene_fill=vec3(1.);\nuniform vec3 scene_haze=vec3(.76,.80,.78);\nuniform vec3 scene_sun_direction=vec3(-.48,.82,.30);\n"
	code = code.replace("shader_type spatial;", "shader_type spatial;" + header)
	if code.contains("float storm35_mask(vec3 p){"):
		code = code.replace("float storm35_mask(vec3 p){", "uniform float storm_strength=0.;\nfloat storm35_mask(vec3 p){")
		code = code.replace("return (1.-smoothstep(-450.,450.,p.x-edge))", "return storm_strength*(1.-smoothstep(-450.,450.,p.x-edge))")
	# Native materials baked by 35c still carry its clear-side yellow tint.
	code = code.replace("mix(vec3(1.,.87,.59),vec3(.45,.52,.63),storm)", "mix(vec3(1.),vec3(.45,.52,.63),storm)")
	code = code.replace("mix(vec3(.65,.55,.35),vec3(.05,.085,.13),storm)", "mix(vec3(.65),vec3(.05,.085,.13),storm)")
	code = code.replace("vec3(.40,.53,.65)*haze", "scene_haze*haze")
	code = code.replace("normalize(vec3(.97,.11,-.20))*13000.", "normalize(scene_sun_direction)*13000.")
	code = code.replace("normalize(vec3(-.48,.82,.30))", "normalize(scene_sun_direction)")
	var start := code.find("void fragment()")
	if start >= 0:
		var opening := code.find("{", start)
		var depth := 0
		var closing := -1
		for i in range(opening, code.length()):
			if code[i] == "{": depth += 1
			elif code[i] == "}":
				depth -= 1
				if depth == 0:
					closing = i
					break
		assert(closing >= 0)
		# study_fill already governs existing authored fill; all remaining
		# materials gain the same night response. Emissive lamp shaders keep glow.
		var tail := "\nALBEDO*=mix(vec3(1.),scene_fill,.35);\n"
		if not code.contains("uniform vec3 study_fill"):
			tail += "EMISSION=(EMISSION-source_emission)*scene_fill+source_emission;\n" if code.contains("uniform vec3 source_emission") else "EMISSION*=scene_fill;\n"
		if code.contains("render_mode unshaded") and not code.contains("uniform float study_night"):
			tail = "\nALBEDO*=scene_fill;\n"
		code = code.substr(0, closing) + tail + code.substr(closing)
	var shader := Shader.new()
	shader.code = code
	shader_cache[original] = shader
	report.shaders.append({"source": original.resource_path, "input_hash": original.code.hash(), "output_hash": code.hash()})
	return shader

func material(original: Material) -> Material:
	if original == null: return null
	if material_cache.has(original): return material_cache[original]
	var changed: Material = original
	if original is ShaderMaterial:
		changed = original.duplicate()
		changed.shader = patch_shader(original.shader)
	material_cache[original] = changed
	return changed

func patch_tree(node: Node) -> void:
	# AssetInstance._ready reapplies its exported authoritative material. Patch
	# that saved export as well, so startup cannot silently undo the candidate.
	if node.get_script() == load("res://scripts/asset_instance.gd") and node.surface_material != null:
		node.surface_material = material(node.surface_material)
	if node.get_script() == load("res://scripts/airship_body.gd"):
		node.hull_material = material(node.hull_material)
		node.cloth_material = material(node.cloth_material)
	if node is GeometryInstance3D:
		if node.material_override != null:
			node.material_override = material(node.material_override)
		elif node is MeshInstance3D and node.mesh != null:
			for i in range(node.mesh.get_surface_count()):
				node.set_surface_override_material(i, material(node.get_active_material(i)))
		elif node is MultiMeshInstance3D and node.multimesh != null:
			var multi: MultiMesh = preload("res://scripts/scatter_group.gd").copy_data(node.multimesh)
			multi.mesh = multi.mesh.duplicate()
			for i in range(multi.mesh.get_surface_count()):
				multi.mesh.surface_set_material(i, material(multi.mesh.surface_get_material(i)))
			node.multimesh = multi
	for child in node.get_children(): patch_tree(child)

func lamp(parent: Node3D, position: Vector3, energy: float, radius: float) -> void:
	var light := OmniLight3D.new()
	light.name = "WarmLamp" + str(parent.get_child_count())
	light.position = position
	light.light_color = Color(1, .68, .34)
	light.light_energy = energy
	light.omni_range = radius
	parent.add_child(light)

func build() -> void:
	assert(not FileAccess.file_exists(DEST + "Game39.tscn"), "Use a new version to preserve previous evidence.")
	DirAccess.make_dir_recursive_absolute(DEST)
	var sky := Node3D.new()
	sky.name = "SkyRegion39"
	var tile := asset("cloud_sea_tile", false)
	for x in range(-2, 3):
		for z in range(-2, 3):
			var cloud: Node3D = tile.duplicate()
			cloud.name = "CloudSea_%s_%s" % [x, z]
			cloud.position = Vector3(3200 + x * 1150, 700, 3000 + z * 1150)
			cloud.rotation.y = (x * 3 + z) * 1.1
			sky.add_child(cloud)
	tile.free()
	var islands := [[3, Vector3(-420,905,-120),0.], [1,Vector3(-260,960,160),1.2], [2,Vector3(-170,1010,-40),2.3], [1,Vector3(-700,1030,-420),.6], [2,Vector3(-520,1120,260),4.], [3,Vector3(-1100,880,300),2.9], [2,Vector3(260,980,-300),1.7], [1,Vector3(420,900,-120),5.1], [3,Vector3(-300,860,-700),3.3]]
	for kind in range(1, 4):
		var source := asset("floating_island_" + str(kind), true)
		for i in range(islands.size()):
			var entry: Array = islands[i]
			if entry[0] != kind: continue
			var island: Node3D = source.duplicate()
			island.name = "FloatingIsland_%s" % i
			island.position = Vector3(3200, 0, 3000) + entry[1]
			island.rotation.y = entry[2]
			sky.add_child(island)
		source.free()
	var cabin_a := asset("cabin_a", true)
	cabin_a.name = "CabinA"
	cabin_a.position = Vector3(3200, 930, 3000)
	sky.add_child(cabin_a)
	lamp(cabin_a, Vector3(-.9,2.05,-.2), 3.2, 7)
	lamp(cabin_a, Vector3(1.2,.6,-.9), 3, 4.5)
	var cabin_b := asset("cabin_b", true)
	cabin_b.name = "CabinB"
	cabin_b.position = Vector3(3350, 960, 3700)
	cabin_b.rotation.y = PI
	sky.add_child(cabin_b)
	lamp(cabin_b, Vector3(-.9,1.9,-1.9), 2.6, 5)
	lamp(cabin_b, Vector3(2.4,1.1,1), 2.8, 5)
	lamp(cabin_b, Vector3(-2.4,.6,.3), 3.2, 4.5)
	owner_tree_children(sky)
	var sky_scene := PackedScene.new()
	assert(sky_scene.pack(sky) == OK)
	assert(ResourceSaver.save(sky_scene, DEST + "SkyRegion39.tscn") == OK)
	sky.free()
	# Load serialized content without _ready: no weather conversion or world
	# regeneration runs during this material-only native assembly.
	var game: Node3D = load(report.source_game).instantiate()
	patch_tree(game)
	var world: Node3D = game.get_node("World")
	world.set_script(load("res://scripts/world39.gd"))
	world.stream_terrain_material = material(load("res://materials/terrain.tres"))
	world.stream_world_material = material(load("res://materials/world.tres"))
	world.stream_cloud_material = material(load("res://materials/cloud.tres"))
	game.set_script(load("res://scripts/game39.gd"))
	var region: Node3D = load(DEST + "SkyRegion39.tscn").instantiate()
	game.add_child(region)
	var controller := Node.new()
	controller.name = "SceneEnvironment39"
	controller.set_script(load("res://scripts/environment39.gd"))
	game.add_child(controller)
	owner_tree_children(game)
	var packed := PackedScene.new()
	assert(packed.pack(game) == OK)
	assert(ResourceSaver.save(packed, DEST + "Game39.tscn") == OK)
	report.source_sha256 = FileAccess.get_sha256(report.source_game)
	report.candidate_sha256 = FileAccess.get_sha256(DEST + "Game39.tscn")
	report.materials = material_cache.size()
	var file := FileAccess.open(DEST + "build-report.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	game.free()
	print("NATIVE39 BUILT: ", report.materials, " materials, ", report.shaders.size(), " shaders")
	shader_cache.clear()
	material_cache.clear()
	await process_frame
	await process_frame
	quit()
