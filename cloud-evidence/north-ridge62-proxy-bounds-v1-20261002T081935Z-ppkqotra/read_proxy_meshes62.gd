extends SceneTree
## Saved resource arrays only. No world, scene instantiation, collision activation or saves.
var issues: Array = []
var request: Dictionary = {}
var result: Dictionary = {"passed":false,"issues":[],"visual_meshes":[],"world_instantiated":false,"runtime_collision_observed":false,"all_occupancy_complete":false}

func check(ok: bool, label: String) -> bool:
	if not ok: issues.append(label)
	return ok

func sha(value: PackedByteArray) -> String:
	var h := HashingContext.new()
	if not check(h.start(HashingContext.HASH_SHA256) == OK,"sha start"): return ""
	if not value.is_empty() and not check(h.update(value) == OK,"sha update"): return ""
	var b: PackedByteArray = h.finish()
	if not check(b.size() == 32,"sha finish"): return ""
	return b.hex_encode()

func vec(v: Vector3) -> Array:
	return [v.x,v.y,v.z]

func extrema(vertices: PackedVector3Array) -> Dictionary:
	if not check(not vertices.is_empty(),"empty vertices"): return {}
	var low: Vector3 = vertices[0]
	var high: Vector3 = vertices[0]
	for v in vertices:
		if not check(v.is_finite(),"nonfinite vertices"): return {}
		low = low.min(v)
		high = high.max(v)
	return {"min":vec(low),"max":vec(high)}

func combined(a: Dictionary,b: Dictionary) -> Dictionary:
	if a.is_empty(): return b
	if b.is_empty(): return a
	return {"min":[minf(a.min[0],b.min[0]),minf(a.min[1],b.min[1]),minf(a.min[2],b.min[2])],"max":[maxf(a.max[0],b.max[0]),maxf(a.max[1],b.max[1]),maxf(a.max[2],b.max[2])]}

func storage_sha(mesh: ArrayMesh) -> String:
	var records: Array = []
	for surface in mesh.get("_surfaces"):
		var record: Dictionary = surface.duplicate()
		record.erase("material")
		records.append(record)
	return sha(var_to_bytes(records))

func mesh_summary(mesh: ArrayMesh) -> Dictionary:
	var item: Dictionary = {"mesh_resource":mesh.resource_path,"surface_storage_sha256":storage_sha(mesh),"surfaces":[],"vertex_count":0,"vertex_bounds":{},"shadow_mesh_resource":"","shadow_surface_storage_sha256":""}
	if not check(mesh.get_blend_shape_count() == 0,"blend shapes unsupported"): return item
	for index in range(mesh.get_surface_count()):
		if not check(mesh.surface_get_primitive_type(index) == Mesh.PRIMITIVE_TRIANGLES,"nontriangle mesh"): return item
		var a: Array = mesh.surface_get_arrays(index)
		if not check(a.size() == Mesh.ARRAY_MAX and a[Mesh.ARRAY_VERTEX] is PackedVector3Array,"native arrays unavailable"): return item
		var vertices: PackedVector3Array = a[Mesh.ARRAY_VERTEX]
		var box: Dictionary = extrema(vertices)
		var s: Dictionary = {"index":index,"primitive":mesh.surface_get_primitive_type(index),"format":mesh.surface_get_format(index),"index_count":mesh.surface_get_array_index_len(index),"vertex_count":vertices.size(),"vertex_bytes_sha256":sha(vertices.to_byte_array()),"vertex_bounds":box}
		item.surfaces.append(s)
		item.vertex_count += vertices.size()
		item.vertex_bounds = combined(item.vertex_bounds,box)
	var faces: PackedVector3Array = mesh.get_faces()
	check(not faces.is_empty() and faces.size() % 3 == 0,"invalid mesh faces")
	item.face_vertex_count = faces.size()
	item.face_bytes_sha256 = sha(faces.to_byte_array())
	item.face_bounds = extrema(faces)
	item.combined_vertex_bounds = item.vertex_bounds
	if mesh.shadow_mesh != null:
		if not check(mesh.shadow_mesh.shadow_mesh == null,"nested shadow unsupported"): return item
		var shadow: Dictionary = mesh_summary(mesh.shadow_mesh)
		item.shadow_mesh_resource = mesh.shadow_mesh.resource_path
		item.shadow_surface_storage_sha256 = shadow.surface_storage_sha256
		item.shadow = shadow
		item.combined_vertex_bounds = combined(item.vertex_bounds,shadow.vertex_bounds)
	return item

func property_value(state: SceneState,index: int,name: String) -> Variant:
	for j in range(state.get_node_property_count(index)):
		if state.get_node_property_name(index,j) == name: return state.get_node_property_value(index,j)
	return null

func read_visual(want: Dictionary) -> void:
	var mm: MultiMesh
	var uri: String = want.saved_multimesh
	if uri.contains("::"):
		var source: String = uri.split("::")[0]
		var packed: PackedScene = load(source)
		if not check(packed != null,"visual scene load"): return
		var state: SceneState = packed.get_state()
		if not check(state.get_base_scene_state() == null,"visual source unexpectedly inherited"): return
		for i in range(state.get_node_count()):
			if str(state.get_node_path(i)).trim_prefix("./") == want.group_path:
				mm = property_value(state,i,"multimesh")
	else:
		mm = load(uri)
	if not check(mm != null and mm.resource_path == uri,"visual multimesh identity"): return
	if not check(mm.mesh is ArrayMesh and mm.mesh.resource_path == want.mesh_resource,"visual mesh binding"): return
	var item: Dictionary = mesh_summary(mm.mesh)
	check(item.surface_storage_sha256 == want.primary_surface_storage_sha256,"primary surface storage changed")
	check(item.shadow_mesh_resource == want.shadow_mesh_resource,"shadow resource changed")
	check(item.shadow_surface_storage_sha256 == want.shadow_surface_storage_sha256,"shadow surface storage changed")
	result.visual_meshes.append(item)

func read_rock() -> void:
	var prefab: PackedScene = load(request.rock_prefab)
	if not check(prefab != null,"rock prefab load"): return
	var state: SceneState = prefab.get_state()
	if not check(state.get_base_scene_state() == null and state.get_node_count() == 4,"rock prefab topology changed"): return
	var imported: PackedScene
	for i in range(state.get_node_count()):
		check(state.get_node_type(i) != "MeshInstance3D","unexpected earlier prefab mesh")
		var nested: PackedScene = state.get_node_instance(i)
		if nested != null:
			if not check(str(state.get_node_path(i)).trim_prefix("./") == "Model" and imported == null,"rock prefab first-child source changed"): return
			imported = nested
	if not check(imported != null and imported.resource_path == request.rock_model_scene,"rock imported binding changed"): return
	var model: SceneState = imported.get_state()
	if not check(model.get_base_scene_state() == null,"rock imported inheritance unsupported"): return
	var mesh: ArrayMesh
	var path: String = ""
	var transform: Variant = Transform3D.IDENTITY
	var nodes: Array = []
	var count: int = 0
	for i in range(model.get_node_count()):
		if not check(model.get_node_instance(i) == null and not model.get_node_instance_placeholder(i),"nested rock imported scene unsupported"): return
		if not check(property_value(model,i,"script") == null,"scripted imported rock unsupported"): return
		nodes.append({"index":i,"path":str(model.get_node_path(i)),"type":str(model.get_node_type(i))})
		if model.get_node_type(i) == "MeshInstance3D":
			count += 1
			mesh = property_value(model,i,"mesh")
			path = "Model" if str(model.get_node_path(i)) == "." else "Model/" + str(model.get_node_path(i)).trim_prefix("./")
			nodes[-1]["mesh_resource"] = mesh.resource_path if mesh != null else ""
			var saved: Variant = property_value(model,i,"transform")
			if saved != null: transform = saved
	if not check(count == 1 and mesh != null,"rock first mesh not uniquely established"): return
	if not check(mesh.resource_path == request.rock_expected_primary_resource,"pinned rock primary identity changed"): return
	var item: Dictionary = mesh_summary(mesh)
	item.prefab = request.rock_prefab
	item.imported_scene = imported.resource_path
	item.imported_node_inventory = nodes
	item.mesh_node_count = count
	item.first_mesh_node_path = path
	item.mesh_node_transform_variant_hex = var_to_bytes(transform).hex_encode()
	item.mesh_node_transform_applied_to_proxy = false
	item.source_rule = "open_world.gd first_mesh(scene).mesh, mesh_body(mesh).get_faces(), then full saved body transform"
	result.rock = item

func _initialize() -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("PROXY62_REQUEST")))
	if not check(parsed is Dictionary,"request JSON missing"): finish(); return
	request = parsed
	if not check(str(Engine.get_version_info().string).begins_with("4.5.1.stable.official"),"fixed engine version"): finish(); return
	result.engine_version = Engine.get_version_info().string
	result.request_sha256 = FileAccess.get_sha256(OS.get_environment("PROXY62_REQUEST"))
	for want in request.visual_meshes:
		read_visual(want)
		if not issues.is_empty(): finish(); return
	read_rock()
	finish()

func finish() -> void:
	result.issues = issues
	result.passed = issues.is_empty() and result.visual_meshes.size() == 6 and result.has("rock")
	var file: FileAccess = FileAccess.open(OS.get_environment("PROXY62_OUTPUT"),FileAccess.WRITE)
	if file == null: push_error("proxy report open failed"); quit(2); return
	file.store_string(JSON.stringify(result,"\t"))
	file.flush()
	file.close()
	print("NORTH62_PROXY_MESH_READ_END ",result.passed)
	quit(0 if result.passed else 2)
