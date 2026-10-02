extends SceneTree
# Resource-array validation only; no scene is added to a viewport and no images.
var report: Dictionary = {"version":"cloud58k-import-v1", "passed":false, "world_loaded":false, "images":0}
var destination: String

func check(ok: bool, message: String) -> bool:
	if not ok:
		report["error"] = message
		finish(1)
	return ok

func finish(code: int) -> void:
	var file := FileAccess.open(destination, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(report, "\t") + "\n")
		file.close()
	quit(code)

func vec(value: Vector3) -> Array:
	return [value.x, value.y, value.z]

func scan(node: Node, output: Array) -> void:
	output.append(node)
	for child in node.get_children():
		scan(child, output)

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var mode: String = args[0]
	destination = args[1]
	report["mode"] = mode
	report["pid"] = OS.get_process_id()
	report["engine"] = Engine.get_version_info()
	if not check(Engine.get_version_info().major == 4 and Engine.get_version_info().minor == 5 and Engine.get_version_info().patch == 1, "Pinned Godot 4.5.1"):
		return
	if not check(mode in ["import", "reload"], "Explicit import/reload mode"):
		return
	var path: String = "res://cloud58k.glb" if mode == "import" else "res://roundtrip.tscn"
	var packed = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE)
	if not check(packed is PackedScene, "PackedScene load"):
		return
	var instance: Node = packed.instantiate()
	if not check(instance != null, "PackedScene instance"):
		return
	var all_nodes: Array = []
	scan(instance, all_nodes)
	var meshes: Array = []
	var transforms: Array = []
	for node in all_nodes:
		if not check(node is Node3D and node.get_script() == null, "Native Node3D only, no external scripts"):
			instance.free()
			return
		var t: Transform3D = node.transform
		transforms.append({"name":str(node.name), "class":node.get_class(), "origin":vec(t.origin), "basis":[vec(t.basis.x),vec(t.basis.y),vec(t.basis.z)]})
		if not check(t == Transform3D.IDENTITY, "Identity transform / unshifted origin"):
			instance.free()
			return
		if node is MeshInstance3D:
			meshes.append(node)
		elif not check(node.get_class() == "Node3D", "No control/camera/light/character nodes"):
			instance.free()
			return
	if not check(meshes.size() == 1 and all_nodes.size() <= 2, "One selected mesh and optional native root"):
		instance.free()
		return
	var mesh_node: MeshInstance3D = meshes[0]
	var mesh: ArrayMesh = mesh_node.mesh as ArrayMesh
	if not check(mesh != null and mesh.get_surface_count() == 1 and mesh.get_blend_shape_count() == 0 and mesh.shadow_mesh == null, "One unchanged ArrayMesh surface, no morph or shadow mesh"):
		instance.free()
		return
	if not check(mesh.surface_get_primitive_type(0) == Mesh.PRIMITIVE_TRIANGLES and mesh_node.material_override == null and mesh_node.material_overlay == null and mesh_node.get_surface_override_material(0) == null, "Triangles and native material only"):
		instance.free()
		return
	var arrays: Array = mesh.surface_get_arrays(0)
	var channels: Array = []
	for index in range(Mesh.ARRAY_MAX):
		if arrays[index] != null and arrays[index].size() > 0: channels.append(index)
	if not check(channels == [Mesh.ARRAY_VERTEX, Mesh.ARRAY_NORMAL, Mesh.ARRAY_INDEX], "Only positions, normals and indices"):
		instance.free()
		return
	var positions: Array = []
	var normals: Array = []
	for value in arrays[Mesh.ARRAY_VERTEX]: positions.append(vec(value))
	for value in arrays[Mesh.ARRAY_NORMAL]: normals.append(vec(value))
	var indices: Array = []
	for value in arrays[Mesh.ARRAY_INDEX]: indices.append(value)
	var material: StandardMaterial3D = mesh.surface_get_material(0) as StandardMaterial3D
	if not check(material != null, "Native StandardMaterial3D"):
		instance.free()
		return
	var textures: int = 0
	for slot in range(BaseMaterial3D.TEXTURE_MAX):
		if material.get_texture(slot) != null: textures += 1
	var color: Color = material.albedo_color
	report["geometry"] = {"positions":positions, "normals":normals, "indices":indices}
	report["material"] = {"albedo_srgb_rgba":[color.r,color.g,color.b,color.a], "roughness":material.roughness, "metallic":material.metallic, "texture_count":textures, "shader_material":false, "emission_enabled":material.emission_enabled, "emission_rgb":[material.emission.r,material.emission.g,material.emission.b], "transparency":material.transparency, "cull_mode":material.cull_mode}
	report["transforms"] = transforms
	var box: AABB = mesh.get_aabb()
	report["aabb"] = [vec(box.position), vec(box.end)]
	report["dependencies"] = Array(ResourceLoader.get_dependencies(path))
	if mode == "import":
		var config := ConfigFile.new()
		if not check(config.load("res://cloud58k.glb.import") == OK, "Actual importer sidecar"):
			instance.free()
			return
		var settings: Dictionary = {}
		for key in config.get_section_keys("params"): settings[key] = config.get_value("params", key)
		report["import_settings"] = settings
		# A separate, native editable snapshot, with embedded duplicate resources.
		# No array/material values are changed. Fresh-process reload checks equality.
		instance.scene_file_path = ""
		var copied_mesh: ArrayMesh = mesh.duplicate(true) as ArrayMesh
		copied_mesh.resource_path = ""
		var copied_material: StandardMaterial3D = material.duplicate(true) as StandardMaterial3D
		copied_material.resource_path = ""
		copied_mesh.surface_set_material(0, copied_material)
		mesh_node.mesh = copied_mesh
		for node in all_nodes:
			if node != instance: node.owner = instance
		var saved := PackedScene.new()
		if not check(saved.pack(instance) == OK and ResourceSaver.save(saved, "res://roundtrip.tscn") == OK, "Native PackedScene roundtrip save"):
			instance.free()
			return
		report["roundtrip_saved"] = true
	instance.free()
	report["passed"] = true
	finish(0)
