extends Node
## Shared live environment. The capture tool calls this same public interface.
var game: Node3D
var materials: Array[ShaderMaterial] = []
var uniform_names: Dictionary = {}
var sky_material: ShaderMaterial
var plan: Array = []
var current_reference := "1343"
var lamps: Array[Light3D] = []
var lamp_energy: Dictionary = {}

func _ready() -> void:
	game = get_parent()
	plan = JSON.parse_string(FileAccess.get_file_as_string("res://assets/reference_views40.json"))
	collect(game)
	var world: Node3D = game.get_node("World")
	register(world.stream_terrain_material)
	register(world.stream_world_material)
	register(world.stream_cloud_material)
	var sky := Sky.new()
	sky_material = ShaderMaterial.new()
	sky_material.shader = preload("res://scripts/environment39_sky.gdshader")
	sky.sky_material = sky_material
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.fog_enabled = true
	env.fog_sky_affect = 0.0
	game.get_node("Environment").environment = env
	for node in game.find_children("*", "Light3D", true, false):
		if node is OmniLight3D or node is SpotLight3D:
			lamps.append(node)
			# These inherited lamps were serialized with their daylight energy=0.
			# Restore authored night energy from harbor_assembly_22g and 23g.
			var baseline: float = node.light_energy
			if str(node.name) in ["HarborWarmLight", "VillageWarmLight"]: baseline = 1.8
			lamp_energy[node.get_instance_id()] = baseline
	apply_reference("1343")

func collect(node: Node) -> void:
	if node is GeometryInstance3D:
		register(node.material_override)
		var mesh: Mesh = null
		if node is MeshInstance3D:
			mesh = node.mesh
			for i in range(node.get_surface_override_material_count()):
				register(node.get_surface_override_material(i))
		elif node is MultiMeshInstance3D and node.multimesh != null:
			mesh = node.multimesh.mesh
		if mesh != null:
			for i in range(mesh.get_surface_count()): register(mesh.surface_get_material(i))
	for child in node.get_children(): collect(child)

func register(material: Material) -> void:
	if material is ShaderMaterial and not materials.has(material):
		materials.append(material)
		var names := PackedStringArray()
		if material.shader != null:
			for u in material.shader.get_shader_uniform_list(): names.append(u["name"])
		uniform_names[material.get_instance_id()] = names
	if material != null and material.next_pass != null: register(material.next_pass)

func set_materials(name: String, value: Variant) -> int:
	var count := 0
	for material in materials:
		if uniform_names[material.get_instance_id()].has(name):
			material.set_shader_parameter(name, value)
			count += 1
	return count

func vector(value: Array) -> Vector3:
	return Vector3(value[0], value[1], value[2])

func color(value: Array) -> Color:
	return Color(value[0], value[1], value[2])

func reference(id: String) -> Dictionary:
	for entry in plan:
		if str(entry["ref"]) == id: return entry
	return {}

func apply_reference(id: String) -> Dictionary:
	var entry := reference(id)
	assert(not entry.is_empty(), "Unknown environment reference: " + id)
	current_reference = id
	var e: Dictionary = entry["env"]
	var env: Environment = game.get_node("Environment").environment
	var direction := vector(e.get("sun_dir", [-.48, .82, .30])).normalized()
	var sun: DirectionalLight3D = game.get_node("Sun")
	var up := Vector3.UP if absf(direction.y) < .98 else Vector3.FORWARD
	sun.basis = Basis.looking_at(-direction, up)
	sun.light_color = color(e.get("sun_color", [1, .97, .89]))
	sun.light_energy = float(e.get("sun_energy", .85))
	env.ambient_light_color = color(e.get("ambient_color", [.84, .91, 1]))
	env.ambient_light_energy = float(e.get("ambient_energy", .60))
	env.fog_light_color = color(e.get("fog_color", [.76, .85, .89]))
	env.fog_density = float(e.get("fog_density", .00028))
	for pair in [["zenith", "sky_zenith", [.44, .63, .837]], ["horizon", "sky_horizon", [.815, .905, .94]], ["glow", "sky_glow", [.13, .12, .07]]]:
		sky_material.set_shader_parameter(pair[0], vector(e.get(pair[1], pair[2])))
	sky_material.set_shader_parameter("sun_dir", direction)
	sky_material.set_shader_parameter("disc", float(e.get("disc", 0)))
	sky_material.set_shader_parameter("stars", float(e.get("stars", 0)))
	var fill := vector(e.get("study_fill", [1, 1, 1]))
	var haze := vector(e.get("study_haze", [.76, .80, .78]))
	var night := float(e.get("water_night", 0))
	var bindings := {
		"scene_fill": set_materials("scene_fill", fill),
		"study_fill": set_materials("study_fill", fill),
		"scene_haze": set_materials("scene_haze", haze),
		"study_haze": set_materials("study_haze", haze),
		"study_night": set_materials("study_night", night),
		"scene_sun_direction": set_materials("scene_sun_direction", direction),
		"storm_strength": set_materials("storm_strength", 0.0)
	}
	# Spatial storm assets stay in the inherited world, but are activated only
	# by a future weather controller; daylight never initializes a storm renderer.
	var old_sky := game.get_node_or_null("NativeCoastalSky27f")
	if old_sky != null:
		for child in old_sky.get_children():
			if "moon" in str(child.name).to_lower(): child.visible = night > .5
	for lamp in lamps:
		var cabin := "SkyRegion39/Cabin" in str(lamp.get_path()) or "CarriageLamp40" in str(lamp.name)
		lamp.light_energy = float(lamp_energy[lamp.get_instance_id()]) * (1.0 if cabin else night)
	return {"reference": id, "night": night, "materials": materials.size(), "bindings": bindings,
		"sun_direction": [direction.x, direction.y, direction.z], "fog_density": env.fog_density,
		"scope": "Live shared environment; storm/rain/snow/rainbow implementation still pending."}
