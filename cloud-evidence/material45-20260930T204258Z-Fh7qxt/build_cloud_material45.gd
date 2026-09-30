extends SceneTree
## One-variable experiment: native Lambert Wrap, with no geometry or light edits.
const BASE := "res://scenes/candidate44/Game44.tscn"
const DEST := "res://scenes/candidate45/"
const TARGET := DEST + "Game45.tscn"
var copies := {}
var resource_cache := {}

func _initialize() -> void: call_deferred("build")
func digest(value: Variant) -> String: return var_to_bytes(value).hex_encode().sha256_text()
func targeted(path: String) -> bool:
	for prefix in ["UpperCloudBank43_", "DistantCloudBank41_", "CloudSea_"]:
		if path.begins_with("SkyRegion39/" + prefix): return true
	return false
func canonical(value: Variant) -> Variant:
	if value is Resource:
		var id: int = value.get_instance_id()
		if resource_cache.has(id): return resource_cache[id]
		if value is Script: return [value.get_class(),value.resource_path,FileAccess.get_sha256(value.resource_path)]
		var state := {"class":value.get_class()}
		for property in value.get_property_list():
			var key: String = property.name
			if property.usage & PROPERTY_USAGE_STORAGE and key not in ["resource_path"]:
				state[key] = canonical(value.get(key))
		var result := digest(state)
		resource_cache[id] = result
		return result
	if value is Node: return str(value.name)
	if value is Array:
		var array := []
		for item in value: array.append(canonical(item))
		return array
	if value is Dictionary:
		var dictionary := {}
		for key in value: dictionary[key] = canonical(value[key])
		return dictionary
	return value
func material_state(material: Material, omit_diffuse := false) -> Dictionary:
	var state := {"class":material.get_class()}
	for property in material.get_property_list():
		var key: String = property.name
		if property.usage & PROPERTY_USAGE_STORAGE and key != "resource_path" and not (omit_diffuse and key == "diffuse_mode"):
			state[key] = canonical(material.get(key))
	return state
func snapshot(game: Node) -> Dictionary:
	resource_cache.clear()
	var data := {}
	var nodes: Array[Node] = [game]
	nodes.append_array(game.find_children("*","",true,false))
	for node in nodes:
		var path := str(game.get_path_to(node))
		var row := {"class":node.get_class()}
		for property in node.get_property_list():
			var key: String = property.name
			if not property.usage & PROPERTY_USAGE_STORAGE or key in ["owner","scene_file_path"]: continue
			if node is MeshInstance3D and targeted(path) and (key == "material_override" or key.begins_with("surface_material_override/")): continue
			row[key] = canonical(node.get(key))
		if node is MultiMeshInstance3D and node.multimesh != null:
			var mm: MultiMesh = node.multimesh
			row.exact_multimesh_buffer = digest(mm.buffer)
			row.exact_multimesh_config = [mm.instance_count,mm.visible_instance_count,mm.transform_format,mm.use_colors,mm.use_custom_data]
		if node is MeshInstance3D and targeted(path):
			var active := []
			for surface in range(node.mesh.get_surface_count()):
				active.append(material_state(node.get_active_material(surface),true))
			row.active_materials_except_diffuse = active
		data[path] = row
	return data
func wrapped(source: Material) -> StandardMaterial3D:
	assert(source is StandardMaterial3D,"Stop: unsupported target material, do not replace shader/ORM/null materials")
	var original := source as StandardMaterial3D
	assert(original.roughness == 1.0,"Scope requires existing roughness=1, do not modify it")
	assert(original.shading_mode != BaseMaterial3D.SHADING_MODE_UNSHADED and not original.emission_enabled)
	var id := original.get_instance_id()
	if not copies.has(id):
		var copy := original.duplicate(false) as StandardMaterial3D
		copy.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
		assert(material_state(copy,true)==material_state(original,true),"Only diffuse mode may change")
		copies[id] = copy
	return copies[id]
func own(node: Node, scene: Node) -> void:
	node.scene_file_path = ""
	if node != scene: node.owner = scene
	for child in node.get_children(): own(child,scene)
func settle() -> void:
	for i in range(3): await process_frame
	await RenderingServer.frame_post_draw
func validate_targets(game: Node) -> Array:
	var rows := []
	for node in game.find_children("*","MeshInstance3D",true,false):
		var path := str(game.get_path_to(node))
		if not targeted(path): continue
		assert(node.mesh != null and node.mesh.get_surface_count()>0)
		for surface in range(node.mesh.get_surface_count()):
			var material: Material = node.get_active_material(surface)
			assert(material is StandardMaterial3D and material.diffuse_mode==BaseMaterial3D.DIFFUSE_LAMBERT_WRAP)
			assert(material.roughness==1.0 and not material.emission_enabled and material.shading_mode!=BaseMaterial3D.SHADING_MODE_UNSHADED)
			rows.append({"node":path,"surface":surface,"material":material_state(material)})
	return rows
func build() -> void:
	if DisplayServer.get_name()=="headless":
		push_error("Refusing headless build: exact MultiMesh data and deferred Sky require renderer")
		quit(2); return
	assert(FileAccess.file_exists(BASE) and not FileAccess.file_exists(TARGET),"Missing 44 or existing 45: never overwrite")
	assert(BaseMaterial3D.DIFFUSE_LAMBERT_WRAP==2)
	var base_sha := FileAccess.get_sha256(BASE)
	var game: Node3D = load(BASE).instantiate()
	await settle()
	var before := snapshot(game)
	var inventory := []
	# Validate every target before changing even the in-memory scene.
	for node in game.find_children("*","MeshInstance3D",true,false):
		var path := str(game.get_path_to(node))
		if not targeted(path): continue
		assert(node.mesh != null and node.mesh.get_surface_count()>0)
		for surface in range(node.mesh.get_surface_count()):
			var material: Material = node.get_active_material(surface)
			wrapped(material)
			inventory.append({"node":path,"surface":surface,"source":material_state(material),"route":"material_override" if node.material_override != null else "surface_override"})
	assert(inventory.size()==1808 and copies.size()==9,"44 preflight inventory changed; review scope before building")
	for node in game.find_children("*","MeshInstance3D",true,false):
		if not targeted(str(game.get_path_to(node))): continue
		if node.material_override != null:
			node.material_override = wrapped(node.material_override)
		else:
			for surface in range(node.mesh.get_surface_count()):
				node.set_surface_override_material(surface,wrapped(node.get_active_material(surface)))
	var expected := validate_targets(game)
	assert(before==snapshot(game),"World or non-diffuse material property changed")
	own(game,game)
	var packed := PackedScene.new()
	assert(packed.pack(game)==OK)
	DirAccess.make_dir_recursive_absolute(DEST)
	assert(ResourceSaver.save(packed,TARGET)==OK)
	var reloaded: Node3D = ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	await settle()
	assert(before==snapshot(reloaded),"Reload changed world geometry/collision/transforms/MM/material properties")
	assert(expected==validate_targets(reloaded),"Reload changed target material properties")
	assert(FileAccess.get_sha256(BASE)==base_sha,"44 must remain untouched")
	var report := {"baseline":BASE,"baseline_sha256":base_sha,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"node_count":before.size(),"world_fingerprint":digest(before),"unique_material_copies":copies.size(),"surface_count":inventory.size(),"inventory":inventory,"reload_exact":true,"renderer":RenderingServer.get_video_adapter_name(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"scope":"Only target cloud native material diffuse_mode changes to Lambert Wrap (2). All other stored node/resource properties, surface material properties and exact MultiMesh buffers are fingerprinted. No geometry/placement/light/environment/camera edits."}
	var file := FileAccess.open(DEST+"build-report-45.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	game.free(); reloaded.free()
	for i in range(8): await process_frame
	print("MATERIAL45 BUILT AND RELOADED ",report.candidate_sha256)
	quit()
