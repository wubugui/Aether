extends "../version-guard-v2/read_proxy_meshes62_v2.gd"
## Version initialization and source/first-rock bindings remain inherited unchanged.
## Call only the existing helper's pure audit/decode methods, never prepare/add_shape.
const ShadowAudit = preload("visible_geometry61.gd")
const AUDIT_SHA: String = "966c863a02d136aefacb78e76d7301649b96c628408c589d3a4345fac30086f7"
const GEOMETRY_POLICY: String = "strict_existing_shadow_indexed_arrays_plus_actual_get_faces_v3"

func oriented_sha(auditor: Variant, faces: PackedVector3Array) -> String:
	var triangles: Dictionary = auditor.oriented_triangles(faces)
	var keys: Array = triangles.keys()
	keys.sort()
	var ordered: Array = []
	for key in keys: ordered.append([key,triangles[key]])
	return sha(var_to_bytes(ordered))

func empty_mesh_summary(mesh: ArrayMesh) -> Dictionary:
	return {"mesh_resource":mesh.resource_path,"surface_storage_sha256":storage_sha(mesh),"surfaces":[],"vertex_count":0,"vertex_bounds":{},"face_method":"actual_indexed_base_faces","face_vertex_count":0,"face_bounds":{},"face_bytes_sha256":"","indexed_visual_bounds":{},"shadow_mesh_resource":"","shadow_surface_storage_sha256":"","combined_vertex_bounds":{},"get_faces_observed":false,"get_faces_bounds":null,"get_faces_vertex_count":0,"get_faces_bytes_sha256":"","get_faces_snap_proof":null,"combined_clearance_bounds":{}}

func read_one_mesh(mesh: ArrayMesh, auditor: Variant, shadow_only: bool) -> Dictionary:
	var item: Dictionary = empty_mesh_summary(mesh)
	var raw: Array = mesh.get("_surfaces")
	var base_faces := PackedVector3Array()
	for index in range(raw.size()):
		var audit: Dictionary = auditor.audit_surface(mesh,index,raw[index])
		if audit.is_empty() or not auditor.failures.is_empty():
			issues.append({"kind":"strict_surface_audit_failed","mesh":mesh.resource_path,"failures":auditor.failures.duplicate(true)})
			return item
		var vertices: PackedVector3Array = auditor.surface_positions(raw[index],mesh.resource_path+"/surface"+str(index))
		if not check(not vertices.is_empty() and auditor.failures.is_empty(),"strict raw vertex decode failed"): return item
		var box: Dictionary = extrema(vertices)
		var surface: Dictionary = {"index":index,"primitive":mesh.surface_get_primitive_type(index),"format":mesh.surface_get_format(index),"index_count":mesh.surface_get_array_index_len(index),"vertex_count":vertices.size(),"vertex_bytes_sha256":sha(vertices.to_byte_array()),"vertex_bounds":box,"api_vertex_missing":audit.api_vertex_missing,"levels":[]}
		for threshold in audit.levels:
			var drawn: PackedVector3Array = audit.levels[threshold]
			var drawn_box: Dictionary = extrema(drawn)
			surface.levels.append({"threshold":threshold,"face_vertex_count":drawn.size(),"face_bytes_sha256":sha(drawn.to_byte_array()),"source_faces_hex_text_sha256":drawn.to_byte_array().hex_encode().sha256_text(),"oriented_faces_sha256":oriented_sha(auditor,drawn),"bounds":drawn_box})
			item.indexed_visual_bounds = combined(item.indexed_visual_bounds,drawn_box)
			if threshold == 0.0: base_faces.append_array(drawn)
		item.surfaces.append(surface)
		item.vertex_count += vertices.size()
		item.vertex_bounds = combined(item.vertex_bounds,box)
	item.face_vertex_count = base_faces.size()
	item.face_bytes_sha256 = sha(base_faces.to_byte_array())
	item.face_bounds = extrema(base_faces)
	item.combined_vertex_bounds = item.vertex_bounds
	item.combined_clearance_bounds = combined(item.vertex_bounds,item.indexed_visual_bounds)
	if not shadow_only:
		# Runtime rocks really use Mesh.get_faces(). Preserve that snapped product
		# separately from the actual indexed visual triangles, with exact proof.
		var actual: PackedVector3Array = mesh.get_faces()
		var predicted := PackedVector3Array()
		predicted.resize(base_faces.size())
		var step := Vector3(0.0001,0.0001,0.0001)
		for i in range(base_faces.size()): predicted[i] = base_faces[i].snapped(step)
		var actual_sha: String = sha(actual.to_byte_array())
		var predicted_sha: String = sha(predicted.to_byte_array())
		var proof_passed: bool = actual.size() == base_faces.size() and actual_sha == predicted_sha
		item.get_faces_observed = true
		item.get_faces_vertex_count = actual.size()
		item.get_faces_bytes_sha256 = actual_sha
		item.get_faces_bounds = extrema(actual)
		item.get_faces_snap_proof = {"passed":proof_passed,"method":"exact_float32_Vector3_snapped_base_indexed_faces","step_float32_hex":PackedFloat32Array([step.x]).to_byte_array().hex_encode(),"predicted_face_bytes_sha256":predicted_sha,"predicted_bounds":extrema(predicted)}
		if not check(proof_passed,"actual get_faces not exactly the fixed-step indexed-face product"): return item
		item.combined_clearance_bounds = combined(item.combined_clearance_bounds,item.get_faces_bounds)
	return item

func mesh_summary(mesh: ArrayMesh) -> Dictionary:
	var empty: Dictionary = empty_mesh_summary(mesh)
	if not check(request.get("geometry_policy") == GEOMETRY_POLICY and request.get("shadow_audit_sha256") == AUDIT_SHA,"v3 geometry request mismatch"): return empty
	if not check(FileAccess.get_sha256(ShadowAudit.resource_path) == AUDIT_SHA,"existing shadow audit source changed"): return empty
	var auditor: Variant = ShadowAudit.new()
	var proof: Dictionary = auditor.audit_array_mesh(mesh)
	if proof.is_empty() or not auditor.failures.is_empty():
		issues.append({"kind":"strict_shadow_coverage_failed","mesh":mesh.resource_path,"failures":auditor.failures.duplicate(true)})
		return empty
	var item: Dictionary = read_one_mesh(mesh,auditor,false)
	if not issues.is_empty(): return item
	if mesh.shadow_mesh != null:
		var shadow: Dictionary = read_one_mesh(mesh.shadow_mesh,auditor,true)
		item.shadow = shadow
		item.shadow_mesh_resource = mesh.shadow_mesh.resource_path
		item.shadow_surface_storage_sha256 = shadow.surface_storage_sha256
		item.combined_vertex_bounds = combined(item.vertex_bounds,shadow.vertex_bounds)
		item.combined_clearance_bounds = combined(item.combined_clearance_bounds,shadow.combined_clearance_bounds)
	item.shadow_coverage_proof = {"passed":auditor.failures.is_empty(),"method":"existing_audit_array_mesh_exact_oriented_multiset_all_base_lods","helper_sha256":AUDIT_SHA,"shadow_present":proof.shadow_equivalent,"surfaces":proof.surfaces}
	item.geometry_policy = GEOMETRY_POLICY
	return item

# Same terminal writer, but retain full float32-to-double decimal precision.
# This is the existing scatter collector serialization contract, no epsilon.
func finish() -> void:
	result.issues = issues
	result.passed = issues.is_empty() and result.visual_meshes.size() == 6 and result.has("rock")
	var file: FileAccess = FileAccess.open(OS.get_environment("PROXY62_OUTPUT"),FileAccess.WRITE)
	if file == null: push_error("proxy report open failed"); quit(2); return
	file.store_string(JSON.stringify(result,"\t",true,true))
	file.flush()
	file.close()
	print("NORTH62_PROXY_MESH_READ_END ",result.passed)
	quit(0 if result.passed else 2)
