extends SceneTree
## Depth-only Game50. The sole old-node change is Ocean.material_override.
const BASE := "res://scenes/candidate49/Game49.tscn"
const BASE_SHA := "52d13fcb7ea412d3a0fae2eedb1d0f9c369dbe06c0da320d786c26c97c475ec8"
const DEST := "res://scenes/candidate50/"
const TARGET := DEST+"Game50.tscn"
const ASSETS := "res://assets/lake_depth50/"
const NEW_GROUP := "World/LakeDepth50"
const CONTROLLER := "res://scripts/lake_depth50.gd"
const WATER_SOURCE := ASSETS+"lake_water_depth50.gdshader"
const IMAGE_SOURCE := "/workspace/scratch/a29d03198654/Aether/source-assets/lake50-intake/"
var diagnostic_dir := ""
var resource_cache := {}
var failures := []
var asset_inventory := []
var mesh_edits := {}
var shape_edits := {}
var scatter_edits := {}
var ocean_ledger := {}
var image_ledger := []
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--diagnostic-dir="): diagnostic_dir=arg.trim_prefix("--diagnostic-dir=")
	call_deferred("build")
func require(ok: bool, message: String, details: Variant=null) -> bool:
	if ok: return true
	var row := {"error":message,"details":details}
	failures.append(row)
	push_error(message)
	print("LAKE50 FAILURE ",JSON.stringify(row))
	if not diagnostic_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(diagnostic_dir)
		var file := FileAccess.open(diagnostic_dir.path_join("lake50-failure.json"),FileAccess.WRITE)
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
			if mask_edits and path=="World/Ocean" and key=="material_override": continue
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
func material_parameters(material: ShaderMaterial) -> Dictionary:
	var values := {}
	for uniform in material.shader.get_shader_uniform_list(): values[str(uniform.name)]=material.get_shader_parameter(uniform.name)
	return values
func stored_properties(resource: Resource, excludes: Array=[]) -> Dictionary:
	var data := {}
	for prop in resource.get_property_list():
		var key: String=prop.name
		if prop.usage & PROPERTY_USAGE_STORAGE and key!="resource_path" and key not in excludes: data[key]=resource.get(key)
	return data
func image_data_state(image: Image) -> Dictionary:
	return {"size":[image.get_width(),image.get_height()],"format":image.get_format(),"mipmaps":image.has_mipmaps(),"data_digest":digest(image.get_data())}
func remove_insertion(code: String, begin: String, end: String) -> String:
	if not require(code.count(begin)==1 and code.count(end)==1,"Exact depth shader sentinels missing",[begin,end]): return ""
	var first := code.find(begin)
	var last := code.find(end,first)+end.length()
	return code.substr(0,first)+code.substr(last)
func prepare_water(source: ShaderMaterial) -> ShaderMaterial:
	if not require(source!=null and FileAccess.file_exists(WATER_SOURCE),"Missing original Ocean or source depth shader"): return null
	var code := FileAccess.get_file_as_string(WATER_SOURCE)
	var injection_path := "/workspace/scratch/a29d03198654/Aether/source-assets/lake_depth50/shader-change-ledger.json"
	var injection: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(injection_path))
	if not require(injection.get("baseline_scene_sha256","")==BASE_SHA and injection.get("original_ocean_shader_sha256","")==source.shader.code.sha256_text() and injection.get("new_shader_sha256","")==code.sha256_text(),"Depth insertion provenance/hash mismatch"): return null
	var head: String=injection.get("inserted_declarations_and_helpers","")
	var body: String=injection.get("inserted_depth_assignment","")
	if not require(not head.is_empty() and not body.is_empty() and code.count(head)==1 and code.count(body)==1,"Exact author-declared shader insertions absent or duplicated"): return null
	var restored := code.replace(head,"").replace(body,"")
	if not require(restored==source.shader.code,"Depth shader changed bytes outside two exact insertion blocks",{"original_sha256":source.shader.code.sha256_text(),"stripped_sha256":restored.sha256_text(),"input_sha256":code.sha256_text()}): return null
	var material := source.duplicate(false) as ShaderMaterial
	var shader := source.shader.duplicate(false) as Shader
	shader.code=code
	material.shader=shader
	var before := material_parameters(source)
	for name in before: material.set_shader_parameter(name,source.get_shader_parameter(name))
	material.set_shader_parameter("lake50_depth_enabled",true)
	var after := material_parameters(material)
	var new_names := []
	for name in after:
		if not before.has(name): new_names.append(name)
	for name in before:
		if not require(canonical(before[name])==canonical(material.get_shader_parameter(name)),"Original Ocean uniform changed",name): return null
	var allowed_new := ["lake50_depth_enabled","lake50_height","lake50_patch0","lake50_patch1","lake50_patch2","lake50_patch3","lake50_patch_bounds0","lake50_patch_bounds1","lake50_patch_bounds2","lake50_patch_bounds3","lake50_patch_size0","lake50_patch_size1","lake50_patch_size2","lake50_patch_size3"]
	for name in new_names:
		if not require(name in allowed_new,"Unknown new water uniform",name): return null
	var excludes := ["shader"]
	for name in new_names: excludes.append("shader_parameter/"+name)
	resource_cache.clear()
	if not require(canonical(stored_properties(source,["shader"]))==canonical(stored_properties(material,excludes)),"Ocean copy changed original stored properties beyond shader/new-depth uniforms"): return null
	if not require(canonical(stored_properties(source.shader,["code"]))==canonical(stored_properties(shader,["code"])),"Ocean shader copy changed non-code stored properties"): return null
	ocean_ledger={"source_material_fingerprint":digest(canonical(source)),"source_shader_sha256":source.shader.code.sha256_text(),"source_shader_flags":canonical(stored_properties(source.shader,["code"])),"new_shader_sha256":code.sha256_text(),"stripped_source_exact":true,"old_uniforms":canonical(before),"old_stored_properties_except_shader":canonical(stored_properties(source,["shader"])),"new_uniform_names":new_names,"new_material_fingerprint":digest(canonical(material)),"source_shader_file":WATER_SOURCE,"source_shader_file_sha256":FileAccess.get_sha256(WATER_SOURCE),"insertion_ledger_sha256":FileAccess.get_sha256(injection_path),"sole_old_node_binding":"World/Ocean.material_override"}
	return material
func copy_height_image(path: String, expected_sha: String, name: String, expected_size: Vector2i) -> Image:
	if not require(FileAccess.file_exists(path) and FileAccess.get_sha256(path)==expected_sha,"Height source hash differs",path): return null
	var source: Image=ResourceLoader.load(path,"Image",ResourceLoader.CACHE_MODE_IGNORE)
	if not require(source!=null and source.get_format()==Image.FORMAT_RF and source.get_size()==expected_size and not source.has_mipmaps(),"Expected unmodified R32F height image",path): return null
	var copy := source.duplicate(true) as Image
	var dest := ASSETS+name+".res"
	if not save_asset(copy,dest): return null
	copy.take_over_path(dest)
	if not require(image_data_state(copy)==image_data_state(source),"Copied image float data differs",path): return null
	image_ledger.append({"source_path":path,"source_sha256":expected_sha,"asset_path":dest,"asset_sha256":FileAccess.get_sha256(dest),"data_state":image_data_state(source)})
	return copy
func add_controller(game: Node3D) -> bool:
	if not require(game.get_node_or_null(NEW_GROUP)==null and FileAccess.file_exists(CONTROLLER),"New controller already exists or script missing"): return false
	var script := load(CONTROLLER) as Script
	var node := Node3D.new()
	node.name="LakeDepth50";node.set_script(script)
	node.set("depth_enabled",true)
	node.set("ocean_path",NodePath("../Ocean"))
	var base_manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(IMAGE_SOURCE+"image-package-report.json"))
	var base_sha := ""
	for row in base_manifest.images:
		if row.label=="height": base_sha=row.resource_sha256
	var base_image := copy_height_image(IMAGE_SOURCE+"height49-1m-rf.res",base_sha,"lake_height_base_1m",Vector2i(769,1537))
	if base_image==null: node.free();return false
	node.set("base_height_image",base_image)
	var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(IMAGE_SOURCE+"patch025/patches.json"))
	var package: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(IMAGE_SOURCE+"patch025/image-package-report.json"))
	var images: Array[Image]=[]
	var bounds: Array[Vector4]=[]
	var sizes: Array[Vector2i]=[]
	for patch in manifest.patches:
		var expected := ""
		for item in package.images:
			if item.name==patch.name: expected=item.resource_sha256
		var size := Vector2i(patch.size[0],patch.size[1])
		var image := copy_height_image(IMAGE_SOURCE+"patch025/"+patch.image_resource,expected,patch.name+"_height_025m",size)
		if image==null: node.free();return false
		images.append(image);sizes.append(size)
		bounds.append(Vector4(patch.world_bounds[0],patch.world_bounds[1],patch.world_bounds[2],patch.world_bounds[3]))
	node.set("patch_images",images);node.set("patch_bounds",bounds);node.set("patch_sizes",sizes)
	game.get_node("World").add_child(node);node.owner=game
	return require(node.has_method("set_depth_enabled") and node.has_method("refresh_now") and node.has_method("get_diagnostic_state"),"Controller interface mismatch")
func verify_new_inventory(game: Node) -> bool:
	var node := game.get_node_or_null(NEW_GROUP)
	return require(node!=null and node is Node3D and node.get_child_count()==0 and node.get_script()!=null and node.get_script().resource_path==CONTROLLER,"Strict new depth-controller inventory mismatch: exactly oneNode3D, no camera/viewport/other child")
func new_state(game: Node) -> Dictionary:
	resource_cache.clear()
	var all := snapshot(game,false)
	return {"controller":all.get(NEW_GROUP,{}),"ocean_material":canonical(game.get_node("World/Ocean").material_override)}
func build() -> void:
	if not require(DisplayServer.get_name()!="headless","Refuse headless scene/material-MM save; real renderer required"): quit(2);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET),"Changed baseline or existing50 target; never overwrite"): await abort_build([]);return
	DirAccess.make_dir_recursive_absolute(ASSETS)
	var original: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var game: Node3D=original.instantiate()
	await settle()
	var before := graph_state(game,original)
	var weather := weather_state(game)
	if weather.is_empty() or not require(before==graph_state(game,original),"Canonical unmodified double-snapshot failed"): await abort_build([game]);return
	var material := prepare_water(game.get_node("World/Ocean").material_override)
	if material==null: await abort_build([game]);return
	if not save_asset(material.shader,ASSETS+"water_depth_shader.tres"): await abort_build([game]);return
	material.shader.take_over_path(ASSETS+"water_depth_shader.tres")
	if not save_asset(material,ASSETS+"ocean_depth50.tres"): await abort_build([game]);return
	material.take_over_path(ASSETS+"ocean_depth50.tres")
	game.get_node("World/Ocean").material_override=material
	if not add_controller(game) or not verify_new_inventory(game): await abort_build([game]);return
	if not require(before==graph_state(game,original),"Depth-only integration changed any non-allowlisted49 state",differences(before,graph_state(game,original))): await abort_build([game]);return
	var expected := new_state(game)
	var packed := PackedScene.new()
	if not require(packed.pack(game)==OK,"Game50 packing failed"): await abort_build([game]);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"Game50 save failed"): await abort_build([game]);return
	var reload_packed: PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var reloaded: Node3D=reload_packed.instantiate()
	await settle()
	if not verify_new_inventory(reloaded): await abort_build([game,reloaded]);return
	var after := graph_state(reloaded,reload_packed)
	if not require(before==after,"Saved50 changed old49 state outside Ocean binding",differences(before,after)) or not require(expected==new_state(reloaded),"Saved50 controller/Ocean state changed on reload",differences(expected,new_state(reloaded))): await abort_build([game,reloaded]);return
	if not require(weather==weather_state(reloaded),"Saved50 changed48000 weather floats") or not require(FileAccess.get_sha256(BASE)==BASE_SHA,"Baseline49 changed"): await abort_build([game,reloaded]);return
	var file := FileAccess.open(TARGET,FileAccess.READ)
	var bytes := file.get_length();file.close()
	if not require(bytes<100*1024*1024,"Game50 exceeded100MiB",bytes): await abort_build([game,reloaded]);return
	var report := {"depth_only_build_reload_passed":true,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"candidate_bytes":bytes,"baseline":BASE,"baseline_sha256":BASE_SHA,"unaffected_graph_fingerprint":digest(before),"old_node_count":before.nodes.size(),"new_state_fingerprint":digest(expected),"ocean_ledger":ocean_ledger,"image_ledger":image_ledger,"asset_inventory":asset_inventory,"controller_script_sha256":FileAccess.get_sha256(CONTROLLER),"weather":weather,"normal_pass_zero_diff":false,"limited_geometry_runtime_passed":false,"requested_motion_all_passed":false,"total_acceptance_passed":false,"visual_acceptance":false,"hardware_gpu_acceptance":false,"scope":"One old binding World/Ocean.material_override plus one newWorld/LakeDepth50 controller. All other stored49 node/resource values, exact MM buffers, camera/layers/geometry/collision/materialauthority/ownership/groups/connections unchanged. Only exact marked shader insertions, all original Ocean uniforms and stored flags retained. Five copied RF Images preserve original float bytes. No scene entered tree during real-renderer build; all deferred Sky resources settled."}
	file=FileAccess.open(DEST+"build-report-50.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	await settle();game.free();reloaded.free()
	for i in range(8): await process_frame
	print("DEPTH50 BUILT_RELOADED ",report.candidate_sha256)
	quit(0)
