extends SceneTree
## Material-only composition: candidate46 geometry + candidate45 Lambert Wrap policy.
## Only native diffuse_mode changes; no geometry, placement, brightness or light edits.
const BASE := "res://scenes/candidate46/Game46.tscn"
const DEST := "res://scenes/candidate47/"
const TARGET := DEST + "Game47.tscn"
var copies := {}
var resource_cache := {}
var resource_debug := {}
var diagnostic_dir := ""
var failures := []

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--diagnostic-dir="): diagnostic_dir=arg.trim_prefix("--diagnostic-dir=")
	call_deferred("build")
func differences(before: Variant, after: Variant, path := "") -> Array:
	var result := []
	if before==after: return result
	if before is Dictionary and after is Dictionary:
		for key in before:
			if not after.has(key): result.append({"path":path+"/"+str(key),"before":str(before[key]),"after":"<missing>"})
			else: result.append_array(differences(before[key],after[key],path+"/"+str(key)))
		for key in after:
			if not before.has(key): result.append({"path":path+"/"+str(key),"before":"<missing>","after":str(after[key])})
	elif before is Array and after is Array and before.size()==after.size():
		for i in range(before.size()): result.append_array(differences(before[i],after[i],path+"/"+str(i)))
	else: result.append({"path":path,"before":str(before),"after":str(after),"before_type":typeof(before),"after_type":typeof(after)})
	return result
func require(ok: bool, message: String, details: Variant=null) -> bool:
	if ok: return true
	var row := {"error":message,"details":details}
	failures.append(row)
	push_error(message)
	print("MATERIAL47 FAILURE ",JSON.stringify(row))
	if not diagnostic_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(diagnostic_dir)
		var file := FileAccess.open(diagnostic_dir.path_join("build47-failure.json"),FileAccess.WRITE)
		if file!=null: file.store_string(JSON.stringify({"failures":failures,"candidate_written":FileAccess.file_exists(TARGET)},"  "));file.close()
	return false
func abort_build(nodes: Array) -> void:
	for node in nodes:
		if is_instance_valid(node): node.free()
	for i in range(8): await process_frame
	quit(1)

func stable_variant(value: Variant) -> Variant:
	# Godot 4.5.1 var_to_bytes(NodePath) contains non-deterministic alignment
	# padding. Preserve exact path text + explicit type, never those unused bytes.
	if value is NodePath: return {"__godot_variant_type__":TYPE_NODE_PATH,"path":str(value)}
	# Dictionary key ordering is not content. Make its representation stable
	# while retaining every key/value, including dictionaries nested in arrays.
	# The observed resource drift was NodePath padding, handled above.
	if value is Dictionary:
		var keys: Array = value.keys()
		keys.sort_custom(func(a: Variant,b: Variant) -> bool: return str(typeof(a))+":"+str(a)<str(typeof(b))+":"+str(b))
		var result := {}
		for key in keys: result[key]=stable_variant(value[key])
		return result
	if value is Array:
		var result := []
		for item in value: result.append(stable_variant(item))
		return result
	return value
func digest(value: Variant) -> String: return var_to_bytes(stable_variant(value)).hex_encode().sha256_text()
func dictionary_orders(value: Variant, path := "") -> Dictionary:
	var result := {}
	if value is Dictionary:
		result[path]=value.keys()
		for key in value: result.merge(dictionary_orders(value[key],path+"/"+str(key)))
	elif value is Array:
		for i in range(value.size()): result.merge(dictionary_orders(value[i],path+"/"+str(i)))
	return result
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
		if value is PackedScene or value is Material or value is Shader:
			resource_debug[str(id)]={"class":value.get_class(),"path":value.resource_path,"hash":result,"state":state}
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
	resource_debug.clear()
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
func resource_differences(before: Dictionary, after: Dictionary) -> Array:
	var result := []
	for id in before:
		if not after.has(id) or before[id].hash==after[id].hash: continue
		var left: Dictionary=before[id]
		var right: Dictionary=after[id]
		result.append({"resource_id":id,"class":left["class"],"path":left.path,"before_hash":left.hash,"after_hash":right.hash,"semantic_equal":left.state==right.state,"before":left.state,"after":right.state,"before_keys":left.state.keys(),"after_keys":right.state.keys(),"before_dictionary_orders":dictionary_orders(left.state),"after_dictionary_orders":dictionary_orders(right.state),"differences":differences(left.state,right.state)})
	return result
func wrapped(source: Material) -> StandardMaterial3D:
	if not require(source is StandardMaterial3D,"Unsupported target material"): return null
	var original := source as StandardMaterial3D
	if not require(original.roughness == 1.0,"Scope requires existing roughness=1"): return null
	if not require(original.shading_mode != BaseMaterial3D.SHADING_MODE_UNSHADED and not original.emission_enabled,"Expected shaded non-emissive material"): return null
	var id := original.get_instance_id()
	if not copies.has(id):
		var copy := original.duplicate(false) as StandardMaterial3D
		copy.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
		if not require(material_state(copy,true)==material_state(original,true),"Only diffuse mode may change",differences(material_state(original,true),material_state(copy,true))): return null
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
		if not require(node.mesh != null and node.mesh.get_surface_count()>0,"Target missing mesh/surfaces",path): return []
		for surface in range(node.mesh.get_surface_count()):
			var material: Material = node.get_active_material(surface)
			if not require(material is StandardMaterial3D and material.diffuse_mode==BaseMaterial3D.DIFFUSE_LAMBERT_WRAP,"Expected wrapped StandardMaterial3D",path): return []
			if not require(material.roughness==1.0 and not material.emission_enabled and material.shading_mode!=BaseMaterial3D.SHADING_MODE_UNSHADED,"Target material roughness/shading changed",path): return []
			rows.append({"node":path,"surface":surface,"material":material_state(material)})
	return rows
func build() -> void:
	if DisplayServer.get_name()=="headless":
		push_error("Refusing headless build: exact MultiMesh data and deferred Sky require renderer")
		quit(2); return
	if not require(FileAccess.file_exists(BASE) and not FileAccess.file_exists(TARGET),"Missing 46 or existing 47: never overwrite"):
		await abort_build([]);return
	if not require(BaseMaterial3D.DIFFUSE_LAMBERT_WRAP==2,"Unexpected Godot Lambert Wrap enum"):
		await abort_build([]);return
	var base_sha := FileAccess.get_sha256(BASE)
	var game: Node3D = load(BASE).instantiate()
	await settle()
	var before := snapshot(game)
	var before_resources := resource_debug.duplicate(true)
	var control := snapshot(game)
	var control_resources := resource_debug.duplicate(true)
	if not require(before==control,"Unmodified double-snapshot control drift",{"node_differences":differences(before,control),"resource_differences":resource_differences(before_resources,control_resources)}):
		await abort_build([game]);return
	var inventory := []
	# Validate every target before changing even the in-memory scene.
	for node in game.find_children("*","MeshInstance3D",true,false):
		var path := str(game.get_path_to(node))
		if not targeted(path): continue
		if not require(node.mesh != null and node.mesh.get_surface_count()>0,"Target missing mesh/surfaces",path):
			await abort_build([game]);return
		for surface in range(node.mesh.get_surface_count()):
			var material: Material = node.get_active_material(surface)
			if wrapped(material)==null:
				await abort_build([game]);return
			inventory.append({"node":path,"surface":surface,"source":material_state(material),"route":"material_override" if node.material_override != null else "surface_override"})
	if not require(inventory.size()==1333 and copies.size()==9,"46 preflight inventory changed",{"surfaces":inventory.size(),"copies":copies.size()}):
		await abort_build([game]);return
	for node in game.find_children("*","MeshInstance3D",true,false):
		if not targeted(str(game.get_path_to(node))): continue
		if node.material_override != null:
			node.material_override = wrapped(node.material_override)
		else:
			for surface in range(node.mesh.get_surface_count()):
				node.set_surface_override_material(surface,wrapped(node.get_active_material(surface)))
	var expected := validate_targets(game)
	var after_edit := snapshot(game)
	if not require(expected.size()==1333 and before==after_edit,"World or non-diffuse material property changed",{"node_differences":differences(before,after_edit),"resource_differences":resource_differences(before_resources,resource_debug)}):
		await abort_build([game]);return
	own(game,game)
	var packed := PackedScene.new()
	if not require(packed.pack(game)==OK,"Pack failed"):
		await abort_build([game]);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"Candidate save failed"):
		await abort_build([game]);return
	var reloaded: Node3D = ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	await settle()
	var after_reload := snapshot(reloaded)
	if not require(before==after_reload,"Reload changed world geometry/collision/transforms/MM/material properties",differences(before,after_reload)):
		await abort_build([game,reloaded]);return
	var actual := validate_targets(reloaded)
	if not require(expected==actual,"Reload changed target material properties",differences(expected,actual)):
		await abort_build([game,reloaded]);return
	if not require(FileAccess.get_sha256(BASE)==base_sha,"46 must remain untouched"):
		await abort_build([game,reloaded]);return
	var report := {"baseline":BASE,"baseline_sha256":base_sha,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"node_count":before.size(),"world_fingerprint":digest(before),"unique_material_copies":copies.size(),"surface_count":inventory.size(),"inventory":inventory,"reload_exact":true,"renderer":RenderingServer.get_video_adapter_name(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"scope":"Only target cloud native material diffuse_mode changes to Lambert Wrap (2). All other stored node/resource properties, surface material properties and exact MultiMesh buffers are fingerprinted. No geometry/placement/light/environment/camera edits."}
	var file := FileAccess.open(DEST+"build-report-47.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	game.free(); reloaded.free()
	for i in range(8): await process_frame
	print("MATERIAL47 BUILT AND RELOADED ",report.candidate_sha256)
	quit()
