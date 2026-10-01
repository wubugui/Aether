extends SceneTree
## Independent51b preparation only. Never overwrites51 or runs its controller.
const BASE := "res://scenes/candidate51/Game51.tscn"
const BASE_SHA := "53e07e91b1bfafd0160749c5d90022d73029287cd36c51d54683339451a75408"
const DEST := "res://scenes/candidate51b/"
const TARGET := DEST+"Game51b.tscn"
const ASSETS := "res://assets/reflection51b/"
const CTRL := "World/LakeReflection51"
const NEW_GROUP := "__NO_ADDED_NODES_IN_51B__"
const OLD_CONTROLLER := "res://scripts/lake_reflection51.gd"
const NEW_CONTROLLER := "res://scripts/lake_reflection51b.gd"
const WATER_SOURCE := ASSETS+"lake_water_reflection51b.gdshader"
const SOURCE_LEDGER := "/workspace/scratch/a29d03198654/Aether/source-assets/reflection51b/source-change-ledger.json"
var diagnostic_dir := ""
var resource_cache := {}
var failures := []
var asset_inventory := []
var mesh_edits := {}
var shape_edits := {}
var scatter_edits := {}
var property_masks := {CTRL:["script","clip_enabled","reflection_enabled","optical_overscan"]}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--diagnostic-dir="): diagnostic_dir=arg.trim_prefix("--diagnostic-dir=")
	call_deferred("build")
func require(ok: bool, message: String, details: Variant=null) -> bool:
	if ok: return true
	var row := {"error":message,"details":details}
	failures.append(row)
	push_error(message)
	print("LAKE51B FAILURE ",JSON.stringify(row))
	if not diagnostic_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(diagnostic_dir)
		var file := FileAccess.open(diagnostic_dir.path_join("lake51b-failure.json"),FileAccess.WRITE)
		if file!=null:
			file.store_string(JSON.stringify({"failures":failures,"candidate_written":FileAccess.file_exists(TARGET)},"  "))
			file.close()
	return false
func abort_build(nodes: Array) -> void:
	await settle()
	for node in nodes:
		if is_instance_valid(node): node.free()
	for i in range(8): await process_frame
	quit(1)
func settle() -> void:
	for i in range(3): await process_frame
	await RenderingServer.frame_post_draw
func stable_variant(value: Variant) -> Variant:
	if value is NodePath: return {"__godot_variant_type__":TYPE_NODE_PATH,"path":str(value)}
	if value is Dictionary:
		var keys: Array=value.keys()
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
func canonical(value: Variant) -> Variant:
	if value is Resource:
		var id: int=value.get_instance_id()
		if resource_cache.has(id): return resource_cache[id]
		if value is Script: return [value.get_class(),value.resource_path,FileAccess.get_sha256(value.resource_path)]
		var state := {"class":value.get_class()}
		for property in value.get_property_list():
			var key: String=property.name
			if property.usage & PROPERTY_USAGE_STORAGE and key!="resource_path": state[key]=canonical(value.get(key))
		var result := digest(state)
		resource_cache[id]=result
		return result
	if value is Node: return str(value.name)
	if value is Array:
		var array := []
		for item in value: array.append(canonical(item))
		return array
	if value is Dictionary:
		var dictionary := {}
		for key in value: dictionary[key]=canonical(value[key])
		return dictionary
	return value
func resource_except(value: Resource, exclusions: Array) -> Dictionary:
	var state := {"class":value.get_class()}
	for property in value.get_property_list():
		var key: String=property.name
		if property.usage & PROPERTY_USAGE_STORAGE and key!="resource_path" and key not in exclusions: state[key]=canonical(value.get(key))
	return state
func differences(before: Dictionary, after: Dictionary) -> Array:
	var rows := []
	for key in before:
		if not after.has(key) or before[key]!=after[key]: rows.append({"node":key,"before":before[key],"after":after.get(key,"<missing>")})
	for key in after:
		if not before.has(key): rows.append({"added":key})
	return rows
func snapshot(game: Node, mask_edits := true) -> Dictionary:
	resource_cache.clear()
	var data := {}
	var nodes: Array[Node]=[game]
	nodes.append_array(game.find_children("*","",true,false))
	for node in nodes:
		var path := str(game.get_path_to(node))
		if mask_edits and (path==NEW_GROUP or path.begins_with(NEW_GROUP+"/")): continue
		var row := {"class":node.get_class()}
		for property in node.get_property_list():
			var key: String=property.name
			if not property.usage & PROPERTY_USAGE_STORAGE or key in ["owner","scene_file_path"]: continue
			if mask_edits and property_masks.has(path) and key in property_masks[path]: continue
			if mask_edits and ((mesh_edits.has(path) and key=="mesh") or (shape_edits.has(path) and key=="shape") or (scatter_edits.has(path) and key=="multimesh")): continue
			row[key]=canonical(node.get(key))
		if mask_edits and mesh_edits.has(path):
			var materials := []
			for surface in range(node.mesh.get_surface_count()): materials.append([canonical(node.mesh.surface_get_material(surface)),canonical(node.get_active_material(surface))])
			row.retained_materials=materials
			row.mesh_resource_flags=[node.mesh.resource_local_to_scene,node.mesh.resource_name]
		if mask_edits and shape_edits.has(path): row.shape_except_faces=resource_except(node.shape,["data"])
		if node is MultiMeshInstance3D and node.multimesh!=null:
			var mm: MultiMesh=node.multimesh
			var buffer: PackedFloat32Array=mm.buffer
			if mask_edits and scatter_edits.has(path):
				row.multimesh_except_buffer=resource_except(mm,["buffer"])
				var stride := 12 + (4 if mm.use_colors else 0) + (4 if mm.use_custom_data else 0)
				for index in scatter_edits[path]:
					for offset in range(12): buffer[int(index)*stride+offset]=0.0
			row.exact_multimesh_buffer=digest(buffer)
			row.exact_multimesh_config=[mm.instance_count,mm.visible_instance_count,mm.transform_format,mm.use_colors,mm.use_custom_data]
		data[path]=row
	return data

func v3(values: Array) -> Vector3: return Vector3(float(values[0]),float(values[1]),float(values[2]))
func transform_from(values: Array) -> Transform3D:
	return Transform3D(Basis(Vector3(values[0],values[1],values[2]),Vector3(values[3],values[4],values[5]),Vector3(values[6],values[7],values[8])),Vector3(values[9],values[10],values[11]))
func transform_values(value: Transform3D) -> Array:
	return [value.basis.x.x,value.basis.x.y,value.basis.x.z,value.basis.y.x,value.basis.y.y,value.basis.y.z,value.basis.z.x,value.basis.z.y,value.basis.z.z,value.origin.x,value.origin.y,value.origin.z]
func world_transform(node: Node) -> Transform3D:
	var chain := []
	var current: Node=node
	while current!=null:
		chain.push_front(current)
		current=current.get_parent()
	var result := Transform3D.IDENTITY
	for item in chain:
		if item is Node3D: result=result*item.transform
	return result
func finite_values(values: Variant, count: int) -> bool:
	if not values is Array or values.size()!=count: return false
	for value in values:
		if not (value is float or value is int) or not is_finite(float(value)): return false
	return true

func weather_state(game: Node) -> Dictionary:
	var data := {}
	for pair in [["Rain",1800],["Snow",1200]]:
		var node := game.get_node_or_null("Weather42b/"+str(pair[0])) as MultiMeshInstance3D
		if not require(node!=null and node.multimesh!=null,"Missing weather MultiMesh",pair[0]): return {}
		var mm: MultiMesh=node.multimesh
		if not require(mm.instance_count==int(pair[1]) and mm.buffer.size()==int(pair[1])*16 and mm.get_instance_transform(0).basis.determinant()!=0,"Weather buffer lost or degenerate",pair[0]): return {}
		data[pair[0]]={"floats":mm.buffer.size(),"buffer_sha256":digest(mm.buffer),"canonical":canonical(mm)}
	return data

func own(node: Node, scene: Node) -> void:
	node.scene_file_path=""
	if node!=scene: node.owner=scene
	for child in node.get_children(): own(child,scene)
func packed_scene_semantics(packed: PackedScene) -> Dictionary:
	# Text scene serialization is allowed to reorder its private string table and
	# encode parent references as paths. Compare the entire resulting native graph,
	# plus ownership, sibling order, persistent groups, connections and flags.
	var node: Node=packed.instantiate()
	var result := {"resource_properties":resource_except(packed,["_bundled"]),"nodes":snapshot(node,false),"node_order":[],"ownership":{},"child_scene_paths":{},"persistent_groups":{},"connections":[]}
	var nodes: Array[Node]=[node]
	nodes.append_array(node.find_children("*","",true,false))
	for child in nodes:
		var path := str(node.get_path_to(child))
		result.node_order.append(path)
		result.ownership[path]=str(node.get_path_to(child.owner)) if child.owner!=null else "<none>"
		if child!=node: result.child_scene_paths[path]=child.scene_file_path
	var state := packed.get_state()
	for i in range(state.get_node_count()):
		var groups := state.get_node_groups(i)
		groups.sort()
		result.persistent_groups[str(state.get_node_path(i))]=groups
	for i in range(state.get_connection_count()):
		result.connections.append([str(state.get_connection_source(i)),str(state.get_connection_signal(i)),str(state.get_connection_target(i)),str(state.get_connection_method(i)),state.get_connection_flags(i),canonical(state.get_connection_binds(i)),state.get_connection_unbinds(i)])
	var bundle: Dictionary=packed.get("_bundled")
	result.editable_instances=canonical(bundle.get("editable_instances",[]))
	node.free()
	return result
func save_asset(resource: Resource, path: String) -> bool:
	if not require(not FileAccess.file_exists(path),"Refuse overwrite independent lake asset",path): return false
	if not require(ResourceSaver.save(resource,path)==OK,"Independent asset save failed",path): return false
	var reload := ResourceLoader.load(path,"",ResourceLoader.CACHE_MODE_IGNORE)
	if not require(reload!=null,"Independent asset reload failed",path): return false
	resource_cache.clear()
	var row := {"path":path,"sha256":FileAccess.get_sha256(path),"class":resource.get_class()}
	if resource is PackedScene and reload is PackedScene:
		var before_raw := resource_except(resource,[])
		var after_raw := resource_except(reload,[])
		var before := packed_scene_semantics(resource)
		var after := packed_scene_semantics(reload)
		if not require(before==after,"Independent prefab native graph reload differs",{"path":path,"semantic_differences":differences(before,after),"packing_table_differences":differences(before_raw,after_raw)}): return false
		row.native_graph_fingerprint=digest(before)
		row.native_node_count=before.nodes.size()
		row.raw_packing_tables_equal=before_raw==after_raw
		row.packing_table_differences=differences(before_raw,after_raw)
	else:
		if not require(canonical(resource)==canonical(reload),"Independent asset reload differs",{"path":path,"differences":differences(resource_except(resource,[]),resource_except(reload,[]))}): return false
	asset_inventory.append(row)
	return true
func graph_state(game: Node, packed: PackedScene, mask_new := true) -> Dictionary:
	var result := {"nodes":snapshot(game,mask_new),"order":[],"owners":{},"groups":{},"connections":[],"scene_paths":{}}
	var nodes: Array[Node]=[game]
	nodes.append_array(game.find_children("*","",true,false))
	for node in nodes:
		var path := str(game.get_path_to(node))
		if mask_new and (path==NEW_GROUP or path.begins_with(NEW_GROUP+"/")): continue
		result.order.append(path)
		result.owners[path]=str(game.get_path_to(node.owner)) if node.owner!=null else "<none>"
		if node!=game: result.scene_paths[path]=node.scene_file_path
	var state := packed.get_state()
	for i in range(state.get_node_count()):
		var path := str(state.get_node_path(i)).trim_prefix("./")
		if mask_new and (path==NEW_GROUP or path.begins_with(NEW_GROUP+"/")): continue
		var groups := state.get_node_groups(i)
		groups.sort()
		result.groups[path]=groups
	for i in range(state.get_connection_count()):
		var source := str(state.get_connection_source(i)).trim_prefix("./")
		var target := str(state.get_connection_target(i)).trim_prefix("./")
		if mask_new and (source==NEW_GROUP or source.begins_with(NEW_GROUP+"/") or target==NEW_GROUP or target.begins_with(NEW_GROUP+"/")): continue
		result.connections.append([source,str(state.get_connection_signal(i)),target,str(state.get_connection_method(i)),state.get_connection_flags(i),canonical(state.get_connection_binds(i)),state.get_connection_unbinds(i)])
	result.connections.sort_custom(func(a: Variant,b: Variant) -> bool: return str(a)<str(b))
	var bundle: Dictionary=packed.get("_bundled")
	result.editable_instances=canonical(bundle.get("editable_instances",[]))
	return result
func export_state(node: Node) -> Dictionary:
	var values := {}
	for prop in node.get_property_list():
		if (prop.usage & PROPERTY_USAGE_STORAGE) and (prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE): values[str(prop.name)]=node.get(prop.name)
	return values
func changed_state(game: Node) -> Dictionary:
	var controller := game.get_node(CTRL)
	resource_cache.clear()
	return {"controller_script":canonical(controller.get_script()),"controller_exports":canonical(export_state(controller)),"ocean":canonical(game.get_node("World/Ocean").material_override),"ocean_material_path":game.get_node("World/Ocean").material_override.resource_path,"ocean_shader_path":game.get_node("World/Ocean").material_override.shader.resource_path}
func build() -> void:
	if not require(DisplayServer.get_name()!="headless","51b requires real renderer for save/48000-MM verification"):quit(2);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET),"51 source mismatch or existing51b target; never overwrite"):await abort_build([]);return
	var ledger: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SOURCE_LEDGER))
	if not require(FileAccess.get_sha256(OLD_CONTROLLER)==ledger.base_controller_sha256 and FileAccess.get_sha256(NEW_CONTROLLER)==ledger.new_controller_sha256 and FileAccess.get_sha256(WATER_SOURCE)==ledger.new_shader_sha256,"51b independent source inputs differ from approved ledger"):await abort_build([]);return
	var source: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var game: Node3D=source.instantiate();await settle()
	var before := graph_state(game,source);var weather := weather_state(game)
	if weather.is_empty() or not require(before==graph_state(game,source),"51off canonical control drift"):await abort_build([game]);return
	var controller := game.get_node(CTRL)
	var exports := export_state(controller)
	if not require(controller.get_script().resource_path==OLD_CONTROLLER and controller.get("clip_enabled")==false and controller.get("reflection_enabled")==false,"Expected untouched51off controller"):await abort_build([game]);return
	controller.set_script(load(NEW_CONTROLLER))
	for key in exports: controller.set(key,exports[key])
	controller.set("clip_enabled",true);controller.set("reflection_enabled",true);controller.set("optical_overscan",1.08)
	var after_exports := export_state(controller)
	for key in exports:
		if key in ["clip_enabled","reflection_enabled"]:continue
		if not require(canonical(exports[key])==canonical(after_exports.get(key)),"51b changed retained controller export/reference",key):await abort_build([game]);return
	if not require(after_exports.size()==exports.size()+1 and after_exports.has("optical_overscan"),"Unexpected new controller exports",after_exports.keys()):await abort_build([game]);return
	var original: ShaderMaterial=game.get_node("World/Ocean").material_override
	if not require(FileAccess.get_file_as_string(WATER_SOURCE)==original.shader.code,"51b shader must be byte-identical to51 source"):await abort_build([game]);return
	var material := original.duplicate(false) as ShaderMaterial
	var shader := original.shader.duplicate(false) as Shader
	shader.code=FileAccess.get_file_as_string(WATER_SOURCE);material.shader=shader
	resource_cache.clear()
	if not require(canonical(material)==canonical(original),"51b Ocean copy changed any shader code/uniform/flag"):await abort_build([game]);return
	DirAccess.make_dir_recursive_absolute(ASSETS)
	if not save_asset(shader,ASSETS+"ocean_reflection_shader51b.tres"):await abort_build([game]);return
	shader.take_over_path(ASSETS+"ocean_reflection_shader51b.tres")
	if not save_asset(material,ASSETS+"ocean_reflection_material51b.tres"):await abort_build([game]);return
	material.take_over_path(ASSETS+"ocean_reflection_material51b.tres")
	game.get_node("World/Ocean").material_override=material
	# Ocean is NOT excluded from canonical comparison: only resource paths differ.
	if not require(before==graph_state(game,source),"51b changed any old51 semantic outside script/flags/new optical export",differences(before,graph_state(game,source))):await abort_build([game]);return
	var expected := changed_state(game)
	var packed := PackedScene.new()
	if not require(packed.pack(game)==OK,"51b pack failed"):await abort_build([game]);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"51b save failed"):await abort_build([game]);return
	var reload_packed: PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var reloaded: Node3D=reload_packed.instantiate();await settle()
	var after := graph_state(reloaded,reload_packed)
	if not require(before==after,"51b reload changed retained51 graph",differences(before,after)) or not require(expected==changed_state(reloaded),"51b reload changed intended script/exports/independent Ocean paths",differences(expected,changed_state(reloaded))):await abort_build([game,reloaded]);return
	if not require(weather==weather_state(reloaded),"51b changed48000 weather floats") or not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(OLD_CONTROLLER)==ledger.base_controller_sha256,"51 source files altered"):await abort_build([game,reloaded]);return
	var f:=FileAccess.open(TARGET,FileAccess.READ);var bytes:=f.get_length();f.close()
	if not require(bytes<100*1024*1024,"51b exceeds100MiB",bytes):await abort_build([game,reloaded]);return
	var report := {"build_saved_reload_passed":true,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"candidate_bytes":bytes,"unaffected_graph_fingerprint":digest(before),"changed_state_fingerprint":digest(expected),"exact_property_masks":property_masks,"source_change_ledger_sha256":FileAccess.get_sha256(SOURCE_LEDGER),"controller_source_sha256":ledger.new_controller_sha256,"old_controller_exports":canonical(exports),"new_controller_exports":canonical(after_exports),"shader_bytes_identical":true,"ocean_full_semantics_unchanged":true,"independent_assets":asset_inventory,"weather":weather,"default_clip_enabled":true,"default_reflection_requested":true,"optical_overscan":1.08,"normal_pass_zero_diff":false,"required_motion_all_passed":false,"total_acceptance_passed":false,"visual_acceptance":false,"hardware_gpu_acceptance":false,"scope":"Independent51b paths from immutable51off; only controller script, clip/reflection defaults and new optical_overscan export differ semantically. Existing controller references/114materials/all50depth data, geometry/collision/MM/cameras/layers/world unchanged. Ocean shader/material get independent paths but complete canonical semantics and shader bytes match51. No new nodes or duplicate world, no runtime controllers executed during build."}
	f=FileAccess.open(DEST+"build-report-51b.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close()
	await settle();game.free();reloaded.free();for i in range(8):await process_frame
	print("REFLECTION51B BUILT_RELOADED ",report.candidate_sha256);quit(0)
