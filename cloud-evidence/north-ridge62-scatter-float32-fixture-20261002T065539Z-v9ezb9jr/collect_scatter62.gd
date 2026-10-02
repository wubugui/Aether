extends "collect_saved62.gd"
## Correction01: exact binary32 identity, checked hashing. Old collector remains immutable.
## Uses inherited unchanged SceneState merge and transform helpers.
## No node instantiation, per-instance renderer getters, setters or resource saves.
var expected: Dictionary = {}
var expected_transform_bytes: Dictionary = {}
var transform_witnesses: Dictionary = {}
var group_results: Array = []
var mesh_results: Dictionary = {}
var material_results: Dictionary = {}
var total_instances: int = 0
var query_instances: int = 0
var design_instances: int = 0
var all_bounds: Variant = null

func bytes_sha(value: PackedByteArray) -> String:
	var context: HashingContext = HashingContext.new()
	var start_code: Error = context.start(HashingContext.HASH_SHA256)
	if start_code != OK:
		issues.append({"kind":"sha256_start_failed","code":start_code}); return ""
	if not value.is_empty():
		var update_code: Error = context.update(value)
		if update_code != OK:
			issues.append({"kind":"sha256_update_failed","code":update_code}); return ""
	var output: PackedByteArray = context.finish()
	if output.size() != 32:
		issues.append({"kind":"sha256_finish_failed","bytes":output.size()}); return ""
	return output.hex_encode()

func digest(value: Variant) -> String:
	return bytes_sha(var_to_bytes(value))

func transform_columns(value: Transform3D) -> Array:
	return [value.basis.x.x,value.basis.x.y,value.basis.x.z,value.basis.y.x,value.basis.y.y,value.basis.y.z,value.basis.z.x,value.basis.z.y,value.basis.z.z,value.origin.x,value.origin.y,value.origin.z]

func finite_transform_array(value: Variant) -> bool:
	if not value is Array or value.size() != 12: return false
	for component in value:
		if not (typeof(component) == TYPE_FLOAT or typeof(component) == TYPE_INT) or not is_finite(component): return false
	var converted: PackedFloat32Array = PackedFloat32Array(value)
	for component in converted:
		if not is_finite(component): return false
	return true

func transform_identity(actual: Variant, parsed_expected: Variant, canonical_hex: Variant) -> Dictionary:
	# Valid only for the fixed 12 ordered finite binary32 components of Transform3D.
	# Numeric JSON is transport; the independent immutable source oracle supplies bytes.
	var result: Dictionary = {"layout":"basis_columns_xyz_then_origin_xyz","component_count":12,"comparison":"exact_binary32_bytes","passed":false}
	if not finite_transform_array(actual) or not finite_transform_array(parsed_expected):
		result.reason = "invalid_finite12_layout"; return result
	if not canonical_hex is String or canonical_hex.length() != 96:
		result.reason = "invalid_canonical_hex_length"; return result
	for index in range(canonical_hex.length()):
		if not canonical_hex[index] in "0123456789abcdef":
			result.reason = "invalid_canonical_hex_character"; return result
	var canonical_bytes: PackedByteArray = canonical_hex.hex_decode()
	if canonical_bytes.size() != 48 or canonical_bytes.hex_encode() != canonical_hex:
		result.reason = "invalid_canonical_hex"; return result
	var actual32: PackedByteArray = PackedFloat32Array(actual).to_byte_array()
	var expected32: PackedByteArray = PackedFloat32Array(parsed_expected).to_byte_array()
	var actual64: PackedByteArray = PackedFloat64Array(actual).to_byte_array()
	var expected64: PackedByteArray = PackedFloat64Array(parsed_expected).to_byte_array()
	result.actual_float32_hex = actual32.hex_encode()
	result.parsed_expected_float32_hex = expected32.hex_encode()
	result.canonical_expected_float32_hex = canonical_hex
	result.actual_float64_hex = actual64.hex_encode()
	result.parsed_expected_float64_hex = expected64.hex_encode()
	result.actual_float32_sha256 = bytes_sha(actual32)
	result.expected_float32_sha256 = bytes_sha(canonical_bytes)
	result.json_float64_equal = actual64 == expected64
	# Native values MUST already be binary32; otherwise narrowing could hide a change.
	result.actual_already_binary32 = actual64 == PackedFloat64Array(Array(PackedFloat32Array(actual))).to_byte_array()
	result.passed = result.actual_already_binary32 and actual32 == canonical_bytes and expected32 == canonical_bytes
	return result

func transform_record(value: Transform3D) -> Dictionary:
	var flat: Array = transform_columns(value)
	return {"basis_columns":[vec(value.basis.x),vec(value.basis.y),vec(value.basis.z)],"origin":vec(value.origin),"native_variant_hex":var_to_bytes(value).hex_encode(),"layout":"basis_columns_xyz_then_origin_xyz","float32_hex":PackedFloat32Array(flat).to_byte_array().hex_encode(),"float64_hex":PackedFloat64Array(flat).to_byte_array().hex_encode()}

func valid_box(box: AABB) -> bool:
	return box.position.is_finite() and box.size.is_finite() and box.end.is_finite() and box.size.x >= 0.0 and box.size.y >= 0.0 and box.size.z >= 0.0

func resource_identity(resource: Resource) -> Dictionary:
	var uri: String = resource.resource_path
	var file: String = uri.split("::")[0]
	return {"resource":uri,"class":resource.get_class(),"source_file":file,"source_sha256":FileAccess.get_sha256(file) if FileAccess.file_exists(file) else ""}

func material_info(material: Material) -> String:
	if material == null: return ""
	var uri: String = material.resource_path
	if material_results.has(uri): return uri
	var item: Dictionary = resource_identity(material)
	item.deformation_envelope_proved = false
	item.next_pass = material.next_pass.resource_path if material.next_pass != null else ""
	if material is ShaderMaterial:
		var shader_material: ShaderMaterial = material
		if shader_material.shader != null:
			item.shader = resource_identity(shader_material.shader)
			item.shader_code_utf8_sha256 = bytes_sha(shader_material.shader.code.to_utf8_buffer())
		item.reason = "Shader vertex displacement and instance custom-data interpretation require separate bounded-envelope review."
	elif material is BaseMaterial3D:
		var base_material: BaseMaterial3D = material
		item.billboard_mode = base_material.billboard_mode
		item.grow_enabled = base_material.grow
		item.grow_amount = base_material.grow_amount
		item.reason = "Saved material fields retained; billboard/grow/next-pass effects not assumed to fit undeformed mesh."
	else: item.reason = "Unknown material deformation behavior."
	material_results[uri] = item
	return uri

func model_bounds(mesh: Mesh, active: Dictionary = {}) -> Variant:
	var uri: String = mesh.resource_path
	if active.has(uri):
		issues.append({"kind":"shadow_mesh_cycle","resource":uri}); return null
	if mesh_results.has(uri): return mesh_results[uri].combined_box
	active[uri] = true
	if not mesh is ArrayMesh:
		issues.append({"kind":"unsupported_bound_mesh_class","resource":uri,"class":mesh.get_class()}); return null
	var array_mesh: ArrayMesh = mesh
	var box: AABB = array_mesh.get_aabb()
	var surfaces: Array = array_mesh.get("_surfaces")
	if surfaces.is_empty() or not valid_box(box):
		issues.append({"kind":"invalid_or_empty_model_bounds","resource":uri}); return null
	var surface_union: Variant = null
	var surface_rows: Array = []
	for index in range(surfaces.size()):
		var surface: Dictionary = surfaces[index]
		if not surface.get("aabb") is AABB or not valid_box(surface.aabb):
			issues.append({"kind":"invalid_surface_aabb","resource":uri,"surface":index}); return null
		var surface_box: AABB = surface.aabb
		surface_union = surface_box if surface_union == null else surface_union.merge(surface_box)
		var material: Material = array_mesh.surface_get_material(index)
		surface_rows.append({"index":index,"bounds":bounds(surface_box),"format":surface.get("format"),"vertex_count":surface.get("vertex_count"),"index_count":surface.get("index_count",0),"lod_storage_sha256":digest(surface.get("lods",{})),"lod_policy":"Saved LOD index alternatives share this surface vertex domain; no independent generated LOD geometry assumed.","material":material_info(material)})
	if box != surface_union:
		issues.append({"kind":"mesh_aabb_not_exact_surface_union","resource":uri}); return null
	var item: Dictionary = resource_identity(mesh)
	item.base_bounds = bounds(box)
	item.surfaces = surface_rows
	item.surface_storage_sha256 = digest(geometry_storage(mesh))
	item.blend_shape_count = array_mesh.get_blend_shape_count()
	item.arraymesh_custom_culling_aabb = bounds(array_mesh.custom_aabb)
	item.undeformed_saved_geometry_only = true
	item.vertex_payload_bounds_independently_recomputed = false
	item.shadow_mesh = ""
	if array_mesh.shadow_mesh != null:
		item.shadow_mesh = array_mesh.shadow_mesh.resource_path
		var shadow_box: Variant = model_bounds(array_mesh.shadow_mesh,active)
		if shadow_box == null: return null
		box = box.merge(shadow_box)
	if not valid_box(box):
		issues.append({"kind":"nonfinite_shadow_union","resource":uri}); return null
	item.combined_bounds_including_shadow = bounds(box)
	item.combined_box = box
	mesh_results[uri] = item
	active.erase(uri)
	return box

func checked_transform(path: String, want: Dictionary) -> Variant:
	for ancestor in want.transform_provenance:
		var ancestor_path: String = ancestor.path
		if not rows.has(ancestor_path):
			issues.append({"kind":"missing_scatter_ancestor","path":path,"ancestor":ancestor_path}); return null
		var ap: Dictionary = rows[ancestor_path].properties
		if bool(ap.get("disable_scale",false)):
			issues.append({"kind":"unsupported_scatter_disable_scale","path":path,"ancestor":ancestor_path}); return null
		for key in ["position","rotation","rotation_degrees","scale","quaternion"]:
			if ap.has(key):
				issues.append({"kind":"unsupported_scatter_transform_property","path":path,"ancestor":ancestor_path,"property":key}); return null
	var value: Transform3D = global_transform(path)
	var flat: Array = transform_columns(value)
	var witness: Dictionary = transform_identity(flat,want.get("world_transform_columns"),expected_transform_bytes.get(path))
	transform_witnesses[path] = witness
	if not value.is_finite() or not witness.passed:
		issues.append({"kind":"independent_saved_transform_mismatch","path":path,"actual":flat,"expected":want.get("world_transform_columns"),"identity":witness}); return null
	return value

func collect_group(path: String, want: Dictionary) -> void:
	var row: Dictionary = rows[path]
	var p: Dictionary = row.properties
	var mm: MultiMesh = p.multimesh
	var item: Dictionary = {"path":path,"resource":mm.resource_path,"saved_property_source":row.property_source.get("multimesh",""),"saved_data_complete":false,"unsupported_reasons":[],"instances_overlapping_query":[]}
	group_results.append(item)
	if mm.resource_path != want.resource or item.saved_property_source != want.saved_property_source:
		issues.append({"kind":"native_binding_mismatch","path":path}); return
	var node_transform: Variant = checked_transform(path,want)
	if node_transform == null: return
	item.world_transform = transform_record(node_transform)
	item.transform_identity = transform_witnesses[path]
	item.source = want.saved_buffer
	item.saved_visible = p.get("visible",true)
	item.saved_process_mode = p.get("process_mode",0)
	item.saved_visible_instance_count = mm.visible_instance_count
	item.saved_node_custom_culling_aabb = bounds(p.get("custom_aabb",AABB()))
	item.saved_multimesh_custom_culling_aabb = bounds(mm.custom_aabb)
	item.model_scene_runtime_binding = want.model_scene
	item.material_override = material_info(p.get("material_override"))
	item.material_overlay = material_info(p.get("material_overlay"))
	item.shader_deformation_envelope_proved = false
	item.runtime_model_scene_and_collision_proved = false
	item.unsupported_reasons.append("Runtime/generated scatter, collision proxies and script-swapped model_scene bounds are not proved by this saved read.")
	item.unsupported_reasons.append("Shader/billboard/grow/next-pass deformation envelope is not proved; bounds are saved affine bound-mesh AABBs.")
	var buffer: PackedFloat32Array = mm.buffer
	var stride: int = 12 + (4 if mm.use_colors else 0) + (4 if mm.use_custom_data else 0)
	var saved: Dictionary = want.saved_buffer
	if mm.transform_format != MultiMesh.TRANSFORM_3D or mm.instance_count != int(saved.instance_count) or mm.use_colors != bool(saved.use_colors) or mm.use_custom_data != bool(saved.use_custom_data) or mm.visible_instance_count != int(saved.visible_instance_count) or buffer.size() != mm.instance_count*stride or buffer.size() != int(saved.buffer_float_count):
		issues.append({"kind":"native_saved_buffer_shape_mismatch","path":path}); return
	var native_sha: String = bytes_sha(buffer.to_byte_array())
	if native_sha != saved.buffer_sha256:
		issues.append({"kind":"native_saved_buffer_hash_mismatch","path":path,"native":native_sha,"expected":saved.buffer_sha256}); return
	item.buffer_sha256 = native_sha
	item.buffer_float_count = buffer.size()
	item.instance_count = mm.instance_count
	item.stride_floats = stride
	item.transform_format = mm.transform_format
	item.use_colors = mm.use_colors
	item.use_custom_data = mm.use_custom_data
	for value in buffer:
		if not is_finite(value):
			issues.append({"kind":"nonfinite_saved_buffer","path":path}); return
	if mm.mesh == null or mm.mesh.resource_path != saved.mesh_resource:
		issues.append({"kind":"native_mesh_binding_mismatch","path":path,"actual":mm.mesh.resource_path if mm.mesh != null else "","expected":saved.mesh_resource}); return
	item.mesh_resource = mm.mesh.resource_path
	var local_box: Variant = model_bounds(mm.mesh)
	if local_box == null: return
	item.local_model_bounds_including_shadow = bounds(local_box)
	var group_box: Variant = null
	var query_count: int = 0
	var design_count: int = 0
	for index in range(mm.instance_count):
		var start: int = index*stride
		# Saved buffer is three matrix ROWS with origin at slots3,7,11.
		# Basis constructor accepts COLUMNS; this swizzle is intentional.
		var local: Transform3D = Transform3D(Basis(Vector3(buffer[start],buffer[start+4],buffer[start+8]),Vector3(buffer[start+1],buffer[start+5],buffer[start+9]),Vector3(buffer[start+2],buffer[start+6],buffer[start+10])),Vector3(buffer[start+3],buffer[start+7],buffer[start+11]))
		var world: Transform3D = node_transform * local
		var box: AABB = world * local_box
		if not world.is_finite() or not valid_box(box):
			issues.append({"kind":"nonfinite_composed_instance","path":path,"index":index}); return
		group_box = box if group_box == null else group_box.merge(box)
		if not valid_box(group_box):
			issues.append({"kind":"nonfinite_group_union","path":path}); return
		var design_hit: bool = hits(box,expected.design_box)
		if design_hit: design_count += 1
		if hits(box,expected.query_box_with_40m):
			query_count += 1
			item.instances_overlapping_query.append({"index":index,"local_transform":transform_record(local),"world_transform":transform_record(world),"world_origin":vec(world.origin),"world_bounds_including_shadow":bounds(box),"hits_design":design_hit,"saved_color":Array(buffer.slice(start+12,start+16)) if mm.use_colors else [],"saved_custom_data":Array(buffer.slice(start+12+(4 if mm.use_colors else 0),start+stride)) if mm.use_custom_data else []})
	item.world_bounds_including_shadow = bounds(group_box) if group_box != null else null
	item.query_instance_count = query_count
	item.design_instance_count = design_count
	item.saved_empty_group = mm.instance_count == 0
	item.saved_data_complete = true
	total_instances += mm.instance_count
	query_instances += query_count
	design_instances += design_count
	if group_box != null:
		all_bounds = group_box if all_bounds == null else all_bounds.merge(group_box)
		if not valid_box(all_bounds): issues.append({"kind":"nonfinite_global_union"})

func save_scatter(complete: bool) -> void:
	var mesh_export: Dictionary = {}
	for uri in mesh_results:
		var item: Dictionary = mesh_results[uri].duplicate()
		item.erase("combined_box")
		mesh_export[uri] = item
	var output: Dictionary = {"status":"complete" if complete else "partial","mode":"SceneState + retained bulk buffers; no instantiation, world or resource save","expected_inputs_sha256":FileAccess.get_sha256(OS.get_environment("SCATTER62_INPUTS")),"expected_transform_bytes_sha256":FileAccess.get_sha256(OS.get_environment("SCATTER62_TRANSFORMS")),"transform_identity_policy":"exact_binary32_bytes_with_independent_source_oracle","undeformed_saved_bound_mesh_metadata_only":true,"vertex_payload_bounds_independently_recomputed":false,"runtime_model_scene_and_collision_proved":false,"baseline_native_intake_sha256":expected.get("baseline_native_intake_sha256",""),"scene_sources":scene_sources,"design_box":expected.get("design_box",[]),"query_box_with_40m":expected.get("query_box_with_40m",[]),"groups":group_results,"mesh_resources":mesh_export,"material_resources":material_results,"issues":issues,"saved_group_count":group_results.size(),"saved_instance_count":total_instances,"query_instance_count":query_instances,"design_instance_count":design_instances,"world_bounds_including_shadow":bounds(all_bounds) if all_bounds != null else null,"saved_affine_bound_mesh_aabbs_complete":complete and issues.is_empty(),"saved_data_read_complete":complete and issues.is_empty(),"all_occupancy_complete":false,"shader_deformation_envelopes_proved":false,"runtime_generated_entities_proved":false,"road_width_proved":false,"visual_acceptance":false}
	var output_path: String = OS.get_environment("SCATTER62_OUTPUT")
	var temporary_path: String = output_path + ".partial.tmp"
	var file: FileAccess = FileAccess.open(temporary_path,FileAccess.WRITE)
	if file == null:
		printerr("Unable to write collector evidence"); quit(2); return
	file.store_string(JSON.stringify(output,"\t",true,true));file.flush();file.close()
	if DirAccess.rename_absolute(temporary_path,output_path) != OK:
		printerr("Unable to finalize collector evidence"); quit(2); return

func _initialize() -> void:
	var value: Variant = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("SCATTER62_INPUTS")))
	if not value is Dictionary: printerr("Invalid prepared scatter inputs"); quit(2); return
	expected = value
	var identity_inputs: Variant = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("SCATTER62_TRANSFORMS")))
	if not identity_inputs is Dictionary or identity_inputs.get("prepared_inputs_sha256") != FileAccess.get_sha256(OS.get_environment("SCATTER62_INPUTS")) or identity_inputs.get("layout") != "basis_columns_xyz_then_origin_xyz" or not identity_inputs.get("groups") is Dictionary:
		printerr("Invalid prepared transform byte identities"); quit(2); return
	expected_transform_bytes = identity_inputs.groups
	var packed: PackedScene = load(expected.entry)
	if packed == null: printerr("Unable to load saved scene"); quit(2); return
	merge_state(packed.get_state(),".",packed.resource_path)
	var wanted: Dictionary = {}
	for item in expected.groups: wanted[item.path] = item
	var found: Dictionary = {}
	for path in rows:
		if rows[path].properties.get("multimesh") is MultiMesh: found[path] = true
	if wanted.size() != 775 or found.size() != 775 or expected_transform_bytes.size() != 775:
		issues.append({"kind":"exact775group_count_mismatch","expected":wanted.size(),"actual":found.size()})
	for path in found:
		if not wanted.has(path): issues.append({"kind":"unexpected_native_group","path":path})
	for path in wanted:
		if not expected_transform_bytes.has(path): issues.append({"kind":"missing_transform_byte_identity","path":path})
		if not found.has(path): issues.append({"kind":"missing_native_group","path":path})
	if not issues.is_empty(): save_scatter(false); quit(2); return
	for path in wanted:
		collect_group(path,wanted[path])
		if group_results.size()%25 == 0: save_scatter(false)
		if not issues.is_empty(): save_scatter(false); quit(2); return
	if scene_sources != expected.scene_sources:
		issues.append({"kind":"native_scene_source_identity_mismatch"})
	save_scatter(true)
	print("NORTH62_SCATTER_END groups=",group_results.size()," instances=",total_instances," query=",query_instances," issues=",issues.size())
	quit(0 if issues.is_empty() else 2)
