extends SceneTree
## Saved-data survey only. Never instantiate nodes, enter a world or save resources.
var rows: Dictionary = {}
var transforms: Dictionary = {}
var issues: Array = []
var scene_sources: Dictionary = {}
var active_states: Dictionary = {}
var plan: Dictionary = {}
var report: Dictionary = {}

func vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func digest(value: Variant) -> String:
	var context: HashingContext = HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(var_to_bytes(value))
	return context.finish().hex_encode()

func geometry_storage(mesh: Mesh) -> Variant:
	if not mesh is ArrayMesh: return null
	var records: Array = []
	for surface in mesh.get("_surfaces"):
		var record: Dictionary = surface.duplicate()
		# Resource IDs are process-local. Exclude only material from the GPU-data hash.
		record.erase("material")
		records.append(record)
	return records

func bounds(b: AABB) -> Dictionary:
	return {"min":vec(b.position), "max":vec(b.end)}

func joined(prefix: String, path: String) -> String:
	path = path.trim_prefix("./")
	if path == "." or path.is_empty(): return prefix
	return path if prefix == "." else prefix + "/" + path

func merge_state(state: SceneState, prefix: String, source: String) -> void:
	if state == null:
		issues.append({"kind":"null_scene_state", "source":source}); return
	var key: String = str(state.get_instance_id()) + "@" + prefix
	if active_states.has(key):
		issues.append({"kind":"scene_cycle", "source":source, "prefix":prefix}); return
	active_states[key] = true
	if not source.is_empty() and FileAccess.file_exists(source):
		scene_sources[source] = FileAccess.get_sha256(source)
	var base: SceneState = state.get_base_scene_state()
	if base != null: merge_state(base, prefix, base.get_path())
	for i in range(state.get_node_count()):
		var path: String = joined(prefix, str(state.get_node_path(i)))
		var instance: PackedScene = state.get_node_instance(i)
		if instance != null and not (i == 0 and base != null):
			merge_state(instance.get_state(), path, instance.resource_path)
		var placeholder: String = state.get_node_instance_placeholder(i)
		if not placeholder.is_empty():
			issues.append({"kind":"unexpanded_placeholder", "path":path, "value":placeholder})
		var row: Dictionary = rows.get(path, {"type":"", "properties":{}, "property_source":{}, "instance_root":false})
		var node_type: String = str(state.get_node_type(i))
		if not node_type.is_empty(): row.type = node_type
		if instance != null: row.instance_root = true
		for j in range(state.get_node_property_count(i)):
			var name: String = str(state.get_node_property_name(i,j))
			row.properties[name] = state.get_node_property_value(i,j)
			row.property_source[name] = source
		rows[path] = row
	active_states.erase(key)

func global_transform(path: String) -> Transform3D:
	if transforms.has(path): return transforms[path]
	if not rows.has(path):
		issues.append({"kind":"missing_transform_ancestor", "path":path}); return Transform3D.IDENTITY
	var node_type: String = str(rows[path].type)
	if not ClassDB.class_exists(node_type):
		issues.append({"kind":"unknown_native_node_type","path":path,"type":node_type}); return Transform3D.IDENTITY
	# Native Node3D inheritance stops at a direct parent which is not Node3D.
	if not ClassDB.is_parent_class(node_type,"Node3D"): return Transform3D.IDENTITY
	var p: Dictionary = rows[path].properties
	var value: Variant = p.get("transform", Transform3D.IDENTITY)
	if not value is Transform3D:
		issues.append({"kind":"non_3d_transform_ancestor","path":path}); return Transform3D.IDENTITY
	var local: Transform3D = value
	# Current native scenes store Transform3D. Do not silently ignore other forms.
	for alternative in ["position", "rotation", "rotation_degrees", "scale", "quaternion"]:
		if p.has(alternative): issues.append({"kind":"unsupported_transform_property", "path":path, "property":alternative})
	var parent: String = path.get_base_dir() if "/" in path else "."
	var result: Transform3D = local
	if path != "." and not bool(p.get("top_level",false)):
		result = global_transform(parent) * local
	transforms[path] = result
	return result

func has_geometry(row: Dictionary) -> bool:
	var p: Dictionary = row.properties
	var geometry: bool = p.get("mesh") is Mesh or p.get("shape") is Shape3D or p.get("multimesh") is MultiMesh or p.get("curve") is Curve3D
	if geometry and not ClassDB.class_exists(str(row.type)):
		issues.append({"kind":"unknown_geometry_node_type","type":str(row.type)})
	return geometry and ClassDB.is_parent_class(str(row.type),"Node3D")

func hits(b: AABB, box: Array) -> bool:
	return b.end.x >= float(box[0]) and b.position.x <= float(box[1]) and b.end.z >= float(box[2]) and b.position.z <= float(box[3])

func entity_root(path: String) -> String:
	var parts: PackedStringArray = path.split("/")
	if parts.size() >= 3 and parts[0] == "World" and parts[1] in ["Terrain", "Settlements", "Landmarks"]:
		return "/".join(parts.slice(0,3))
	var model: int = parts.find("Model")
	if model > 0: return "/".join(parts.slice(0,model))
	var current: String = path
	while current != ".":
		if rows.has(current) and bool(rows[current].instance_root): return current
		current = current.get_base_dir() if "/" in current else "."
	# Conservative ownership fallback can group several pieces; never split a house.
	return "/".join(parts.slice(0,mini(2,parts.size())))

func point_bounds(points: PackedVector3Array) -> Variant:
	if points.is_empty(): return null
	var b: AABB = AABB(points[0],Vector3.ZERO)
	for p in points: b = b.expand(p)
	return b

func shape_bounds(shape: Shape3D) -> Variant:
	if shape is BoxShape3D: return AABB(-shape.size * 0.5,shape.size)
	if shape is SphereShape3D:
		var s: Vector3 = Vector3.ONE * shape.radius * 2.0
		return AABB(-s*0.5,s)
	if shape is CapsuleShape3D or shape is CylinderShape3D:
		var radius: float = float(shape.get("radius"))
		var s: Vector3 = Vector3(radius*2.0,float(shape.get("height")),radius*2.0)
		return AABB(-s*0.5,s)
	if shape is ConvexPolygonShape3D: return point_bounds(shape.points)
	if shape is ConcavePolygonShape3D: return point_bounds(shape.get_faces())
	return null

func transform_record(value: Transform3D) -> Dictionary:
	return {"basis_columns":[vec(value.basis.x),vec(value.basis.y),vec(value.basis.z)],"origin":vec(value.origin),"native_variant_hex":var_to_bytes(value).hex_encode()}

func metadata_value(value: Variant) -> Dictionary:
	# Native encoding preserves Variant types without calling object _to_string().
	# Objects are encoded as process-local IDs, never serialized with full_objects.
	return {"variant_type":type_string(typeof(value)),"native_variant_hex":var_to_bytes(value).hex_encode(),"resource_path":value.resource_path if value is Resource else ""}

func saved_metadata(path: String) -> Dictionary:
	var result: Dictionary = {}
	for key in rows[path].properties:
		if str(key).begins_with("metadata/"):
			result[str(key).trim_prefix("metadata/")] = {"value":metadata_value(rows[path].properties[key]),"property_source":rows[path].property_source.get(key,"")}
	return result

func world_boundary_record(path: String, shape: WorldBoundaryShape3D, transform: Transform3D) -> Dictionary:
	# Separate global constraint: never assign a finite AABB or feed add_part/hits.
	var item: Dictionary = {"path":path,"class":shape.get_class(),"resource":shape.resource_path,"property_source":rows[path].property_source.get("shape",""),"classification":"unbounded_saved_world_boundary","classification_valid":false,"finite_bounds":null,"finite_occupancy_clearance_proved":false,"runtime_physics_behavior_proved":false,"query_policy":"Global half-space constraint retained without finite XZ filtering; no clearance inference.","physics_engine_setting":ProjectSettings.get_setting("physics/3d/physics_engine","DEFAULT"),"backend_caveat":"Godot Physics broadphase sentinels and Jolt finite backend proxies are not finite occupancy authority.","resource_metadata":{}}
	for key in shape.get_meta_list(): item.resource_metadata[str(key)] = metadata_value(shape.get_meta(key))
	var row: Dictionary = rows[path]
	var p: Dictionary = row.properties
	var body_path: String = path.get_base_dir() if "/" in path else "."
	if not ClassDB.is_parent_class(str(row.type),"CollisionShape3D") or not rows.has(body_path) or not ClassDB.is_parent_class(str(rows[body_path].type),"CollisionObject3D"):
		issues.append({"kind":"invalid_world_boundary_collision_parent","path":path,"parent":body_path}); return item
	var body: Dictionary = rows[body_path]
	var bp: Dictionary = body.properties
	var disabled: Variant = p.get("disabled",false)
	var layer: Variant = bp.get("collision_layer",1)
	var mask: Variant = bp.get("collision_mask",1)
	var disable_mode: Variant = bp.get("disable_mode",0)
	if not disabled is bool or not layer is int or not mask is int or not disable_mode is int:
		issues.append({"kind":"invalid_world_boundary_collision_flags","path":path}); return item
	if layer < 0 or layer > 4294967295 or mask < 0 or mask > 4294967295 or disable_mode not in [0,1,2]:
		issues.append({"kind":"invalid_world_boundary_collision_flags","path":path}); return item
	item.collision = {"parent":body_path,"parent_type":body.type,"shape_disabled_saved":disabled,"shape_enabled_saved":not disabled,"collision_layer":layer,"collision_mask":mask,"body_disable_mode":disable_mode,"effective_runtime_enabled_proved":false,"property_sources":{"disabled":row.property_source.get("disabled","Godot 4.5.1 native default false"),"collision_layer":body.property_source.get("collision_layer","Godot 4.5.1 native default 1"),"collision_mask":body.property_source.get("collision_mask","Godot 4.5.1 native default 1"),"disable_mode":body.property_source.get("disable_mode","Godot 4.5.1 native default 0")}}
	item.saved_ancestry = []
	var current: String = path
	while true:
		if not rows.has(current):
			issues.append({"kind":"missing_world_boundary_ancestor","path":path,"ancestor":current}); return item
		var ancestor: Dictionary = rows[current]
		var ap: Dictionary = ancestor.properties
		if not ClassDB.class_exists(str(ancestor.type)):
			issues.append({"kind":"unknown_world_boundary_ancestor_type","path":path,"ancestor":current}); return item
		if ClassDB.is_parent_class(str(ancestor.type),"Node3D"):
			if not ap.get("transform",Transform3D.IDENTITY) is Transform3D:
				issues.append({"kind":"invalid_world_boundary_ancestor_transform","path":path,"ancestor":current}); return item
			for alternative in ["position","rotation","rotation_degrees","scale","quaternion"]:
				if ap.has(alternative):
					issues.append({"kind":"unsupported_world_boundary_transform_property","path":path,"ancestor":current,"property":alternative}); return item
		var process_mode: Variant = ap.get("process_mode",0)
		if not process_mode is int or process_mode not in [0,1,2,3,4]:
			issues.append({"kind":"invalid_world_boundary_process_mode","path":path,"ancestor":current}); return item
		item.saved_ancestry.append({"path":current,"type":ancestor.type,"process_mode":process_mode,"process_mode_source":ancestor.property_source.get("process_mode","Godot 4.5.1 native default INHERIT"),"metadata":saved_metadata(current)})
		# Existing transform resolver does not model disable_scale. Do not clear it.
		if bool(ap.get("disable_scale",false)):
			issues.append({"kind":"unsupported_world_boundary_disable_scale","path":path,"ancestor":current}); return item
		if current == ".": break
		current = current.get_base_dir() if "/" in current else "."
	# CollisionShape3D passes its LOCAL transform to its direct shape owner.
	# Refuse top_level here rather than confuse scene-global and physics transforms.
	if bool(p.get("top_level",false)):
		issues.append({"kind":"unsupported_world_boundary_top_level","path":path}); return item
	var local_plane: Plane = shape.plane
	var normal_length_squared: float = local_plane.normal.length_squared()
	var determinant: float = transform.basis.determinant()
	if not local_plane.is_finite() or not is_finite(normal_length_squared) or normal_length_squared <= 0.0:
		issues.append({"kind":"invalid_world_boundary_plane","path":path}); return item
	# Godot Plane/xform requires a unit normal; silently normalizing bad source
	# would change what the pinned physics code receives. Preserve and reject it.
	if not local_plane.normal.is_normalized():
		issues.append({"kind":"non_unit_world_boundary_normal","path":path}); return item
	if not transform.is_finite() or not is_finite(determinant) or determinant == 0.0:
		issues.append({"kind":"invalid_world_boundary_transform","path":path}); return item
	var inverse_basis: Basis = transform.basis.inverse()
	if not inverse_basis.is_finite():
		issues.append({"kind":"invalid_world_boundary_inverse","path":path}); return item
	# Match 4.5.1 Transform3D::xform_fast(Plane): inverse-transpose normal,
	# transform one point on the unit-normal plane, then dot for world d.
	var world_normal_raw: Vector3 = inverse_basis.transposed() * local_plane.normal
	var world_length_squared: float = world_normal_raw.length_squared()
	if not world_normal_raw.is_finite() or not is_finite(world_length_squared) or world_length_squared <= 0.0:
		issues.append({"kind":"invalid_world_boundary_world_normal","path":path}); return item
	var world_normal: Vector3 = world_normal_raw.normalized()
	var world_point: Vector3 = transform * (local_plane.normal * local_plane.d)
	var world_d: float = world_normal.dot(world_point)
	if not world_normal.is_finite() or not world_normal.is_normalized() or not world_point.is_finite() or not is_finite(world_d):
		issues.append({"kind":"invalid_world_boundary_world_plane","path":path}); return item
	item.local_plane = {"normal":vec(local_plane.normal),"d":local_plane.d,"native_variant_hex":var_to_bytes(local_plane).hex_encode(),"equation":"normal.dot(local_position) = d"}
	item.world_transform = transform_record(transform)
	item.world_plane = {"normal":vec(world_normal),"d":world_d,"point_on_plane":vec(world_point),"equation":"normal.dot(world_position) = d","solid_half_space":"normal.dot(world_position) <= d","strict_interior":"normal.dot(world_position) < d","outward_side":"normal.dot(world_position) > d"}
	item.classification_valid = true
	return item

func add_part(entities: Dictionary, path: String, b: AABB, kind: String, resource: Resource) -> void:
	var root_path: String = entity_root(path)
	if not entities.has(root_path): entities[root_path] = {"box":b,"parts":[]}
	else: entities[root_path].box = entities[root_path].box.merge(b)
	entities[root_path].parts.append({"path":path,"kind":kind,"resource":resource.resource_path,"bounds":bounds(b),"transform_hex":var_to_bytes(global_transform(path)).hex_encode()})

func boundary_summary(mesh: Mesh, transform: Transform3D, box: AABB) -> Dictionary:
	var edges: Dictionary = {"west":{},"east":{},"north":{},"south":{}}
	var count: int = 0
	var formats: Array = []
	if transform.basis != Basis.IDENTITY:
		issues.append({"kind":"boundary_requires_unscaled_axis_aligned_tile","resource":mesh.resource_path})
	if mesh.get_surface_count() == 0:
		issues.append({"kind":"empty_terrain_mesh","resource":mesh.resource_path})
	for s in range(mesh.get_surface_count()):
		if mesh.surface_get_primitive_type(s) != Mesh.PRIMITIVE_TRIANGLES:
			issues.append({"kind":"non_triangle_terrain", "resource":mesh.resource_path}); continue
		var a: Array = mesh.surface_get_arrays(s)
		if a.size() != Mesh.ARRAY_MAX or not a[Mesh.ARRAY_VERTEX] is PackedVector3Array:
			issues.append({"kind":"unavailable_terrain_vertex_arrays", "resource":mesh.resource_path,"surface":s}); continue
		var vertices: PackedVector3Array = a[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array = a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX] is PackedInt32Array else PackedInt32Array()
		var used: PackedInt32Array = indices
		if used.is_empty():
			used.resize(vertices.size())
			for index in range(vertices.size()): used[index] = index
		if used.size() % 3 != 0: issues.append({"kind":"bad_triangle_count","resource":mesh.resource_path})
		count += used.size() / 3
		formats.append(mesh.surface_get_format(s))
		for index in used:
			if index < 0 or index >= vertices.size():
				issues.append({"kind":"bad_vertex_index","resource":mesh.resource_path}); continue
			var p: Vector3 = transform * vertices[index]
			# Exact native coordinates; no snapping, welding tolerance or source mutation.
			if p.x == box.position.x: edges.west[p] = true
			if p.x == box.end.x: edges.east[p] = true
			if p.z == box.position.z: edges.north[p] = true
			if p.z == box.end.z: edges.south[p] = true
	var result: Dictionary = {"drawn_base_triangles":count,"formats":formats,"edges":{}}
	if count == 0: issues.append({"kind":"empty_terrain_triangles","resource":mesh.resource_path})
	for side in edges:
		var points: Array = edges[side].keys()
		points.sort_custom(func(a: Vector3,b: Vector3) -> bool: return a.x < b.x or (a.x == b.x and (a.z < b.z or (a.z == b.z and a.y < b.y))))
		var packed: PackedVector3Array = PackedVector3Array(points)
		var values: Array = []
		for p in packed: values.append(vec(p))
		var span_ok: bool = points.size() >= 2
		if span_ok and side in ["west","east"]:
			span_ok = points[0].z == box.position.z and points[-1].z == box.end.z
		elif span_ok:
			span_ok = points[0].x == box.position.x and points[-1].x == box.end.x
		if not span_ok: issues.append({"kind":"incomplete_tile_boundary","resource":mesh.resource_path,"side":side,"point_count":points.size()})
		result.edges[side] = {"points":values,"native_vector_sha256":digest(packed)}
	return result

func finish(code: int) -> void:
	report.issues = issues
	report.saved_data_read_complete = code == 0 and issues.is_empty()
	report.runtime_generated_entities_proved = false
	report.dependency_load_time_initializers_excluded = false
	report.all_occupancy_complete = false
	report.visual_acceptance = false
	var out: String = OS.get_environment("NORTH62_OUTPUT")
	var f: FileAccess = FileAccess.open(out,FileAccess.WRITE)
	if f == null: printerr("Cannot write output: ",out); quit(3); return
	f.store_string(JSON.stringify(report,"  ")); f.close()
	print("NORTH62_SAVED_INTAKE_END saved_data_read_complete=",report.saved_data_read_complete," issues=",issues.size())
	quit(code if code != 0 else (0 if issues.is_empty() else 2))

func _initialize() -> void:
	var plan_path: String = OS.get_environment("NORTH62_PLAN")
	if plan_path.is_empty(): printerr("Explicit NORTH62_PLAN required"); quit(2); return
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(plan_path))
	if not data is Dictionary: printerr("Invalid plan"); quit(2); return
	plan = data
	report = {"mode":"SceneState only; no instantiation, world, render or resource save", "entry":plan.entry,"design_box":plan.design_box,"query_box_with_40m":plan.query_box_with_40m,"geometry_reuse":{},"terrain":[],"terrain_collision":[],"entities":[],"settlement_identity_catalog":[],"unbounded_world_boundaries":[],"scatter_unresolved":[],"curves":[],"scripted_node_count":0,"script_resources":{}}
	if FileAccess.get_sha256(plan.entry) != plan.entry_sha256:
		issues.append({"kind":"entry_sha_changed"}); finish(2); return
	if FileAccess.get_sha256(plan.reuse_source) != plan.reuse_source_sha256 or FileAccess.get_sha256(plan.reuse_geometry_file) != plan.reuse_geometry_sha256:
		issues.append({"kind":"reuse_input_sha_changed"}); finish(2); return
	var packed: PackedScene = load(plan.entry)
	if packed == null: issues.append({"kind":"entry_load_failed"}); finish(2); return
	merge_state(packed.get_state(),".",packed.resource_path)
	var effective: Dictionary = rows.duplicate(true)
	var effective_transforms: Dictionary = {}
	for path in rows:
		if has_geometry(rows[path]): effective_transforms[path] = global_transform(path)
	var current_sources: Dictionary = scene_sources.duplicate()
	rows = {}; transforms = {}; active_states = {}; scene_sources = {}
	var base: PackedScene = load(plan.reuse_source)
	if base == null: issues.append({"kind":"reuse_source_load_failed"}); finish(2); return
	merge_state(base.get_state(),".",base.resource_path)
	var base_rows: Dictionary = rows
	var base_transforms: Dictionary = {}
	for path in rows:
		if effective_transforms.has(path): base_transforms[path] = global_transform(path)
	rows = effective; transforms = effective_transforms
	report.scene_sources = current_sources
	var entities: Dictionary = {}
	var terrain_names: Array = plan.terrain_and_neighbor_names
	for path in rows:
		var row: Dictionary = rows[path]
		var p: Dictionary = row.properties
		if p.get("script") is Script:
			report.scripted_node_count += 1
			var script: Script = p.script
			report.script_resources[script.resource_path] = {"sha256":FileAccess.get_sha256(script.resource_path),"runtime_behavior":"Collector does not instantiate nodes or call their lifecycle. Dependency load-time initializers are not fully audited; generated descendants and deformation are unproved."}
		if not has_geometry(row): continue
		var transform: Transform3D = global_transform(path)
		if p.get("multimesh") is MultiMesh:
			# Dummy renderer MM buffers/AABBs are not native placement authority.
			var mm: MultiMesh = p.multimesh
			report.scatter_unresolved.append({"path":path,"resource":mm.resource_path,"saved_property_source":row.property_source.get("multimesh",""),"reason":"No headless buffer/AABB read. Existing saved-buffer parser or real renderer required before occupancy clearance."})
		if p.get("curve") is Curve3D:
			var curve: Curve3D = p.curve
			var points: PackedVector3Array = PackedVector3Array()
			for i in range(curve.get_point_count()):
				var center: Vector3 = curve.get_point_position(i)
				points.append(transform*center); points.append(transform*(center+curve.get_point_in(i))); points.append(transform*(center+curve.get_point_out(i)))
			var curve_box: Variant = point_bounds(points)
			if curve_box != null:
				report.curves.append({"path":path,"resource":curve.resource_path,"control_hull_bounds":bounds(curve_box),"hits_query":hits(curve_box,plan.query_box_with_40m),"road_width_and_generated_mesh_clearance_proved":false})
		if p.get("mesh") is Mesh:
			var mesh: Mesh = p.mesh
			var b: AABB = transform * mesh.get_aabb()
			if path.begins_with("World/Terrain/"):
				var tile: String = path.split("/")[2]
				if tile not in terrain_names: continue
				var unchanged: bool = base_rows.has(path) and base_rows[path].properties.get("mesh") == mesh and var_to_bytes(base_transforms[path]) == var_to_bytes(transform)
				var native_surfaces: Variant = geometry_storage(mesh)
				var item: Dictionary = {"path":path,"tile":tile,"resource":mesh.resource_path,"bounds":bounds(b),"transform_hex":var_to_bytes(transform).hex_encode(),"same_bound_resource_and_transform_as_sha_pinned_53d":unchanged,"surface_storage_sha256":digest(native_surfaces),"property_source":row.property_source.get("mesh","")}
				if tile in plan.reuse_geometry_tiles and unchanged and FileAccess.get_sha256(plan.reuse_source) == plan.reuse_source_sha256:
					item.geometry = {"reused_file":plan.reuse_geometry_file,"sha256":plan.reuse_geometry_sha256,"record_node":"/Skyfarer/"+path,"scope":"previous indexed world-space positions only; not full native editable GPU fields"}
				else:
					item.geometry = {"reuse_allowed":false,"boundary_only":boundary_summary(mesh,transform,b)}
				if tile in plan.target_tiles and not unchanged: issues.append({"kind":"target_changed_since_reuse_source","tile":tile})
				report.terrain.append(item)
			else:
				add_part(entities,path,b,"mesh_conservative_aabb",mesh)
		if p.get("shape") is Shape3D:
			var shape: Shape3D = p.shape
			if path.begins_with("World/Terrain/"):
				var tile: String = path.split("/")[2]
				if tile not in terrain_names: continue
				if not shape is ConcavePolygonShape3D:
					issues.append({"kind":"unsupported_terrain_shape","path":path}); continue
				var faces: PackedVector3Array = shape.get_faces()
				var local_shape_box: Variant = point_bounds(faces)
				if local_shape_box == null:
					issues.append({"kind":"empty_terrain_shape","path":path}); continue
				var unchanged: bool = base_rows.has(path) and base_rows[path].properties.get("shape") == shape and var_to_bytes(base_transforms[path]) == var_to_bytes(transform)
				report.terrain_collision.append({"path":path,"tile":tile,"resource":shape.resource_path,"bounds":bounds(transform*local_shape_box),"native_faces_sha256":digest(faces),"face_count":faces.size()/3,"same_bound_resource_and_transform_as_sha_pinned_53d":unchanged,"property_source":row.property_source.get("shape","")})
				if tile in plan.target_tiles and not unchanged: issues.append({"kind":"target_collision_changed_since_reuse_source","tile":tile})
				continue
			if shape is WorldBoundaryShape3D:
				report.unbounded_world_boundaries.append(world_boundary_record(path,shape,transform))
				continue
			var local_box: Variant = shape_bounds(shape)
			if local_box != null: add_part(entities,path,transform*local_box,"collision_bounds_including_disabled",shape)
			else: issues.append({"kind":"unbounded_saved_shape","path":path,"class":shape.get_class()})
	for root_path in entities:
		var e: Dictionary = entities[root_path]
		var b: AABB = e.box
		var item: Dictionary = {"root":root_path,"whole_bounds":bounds(b),"whole_bounds_plus_40m_xz":{"min":[b.position.x-40,b.position.y,b.position.z-40],"max":[b.end.x+40,b.end.y,b.end.z+40]},"hits_design":hits(b,plan.design_box),"hits_query":hits(b,plan.query_box_with_40m),"parts":e.parts}
		if hits(b,plan.query_box_with_40m): report.entities.append(item)
		if root_path.begins_with("World/Settlements/"): report.settlement_identity_catalog.append(item)
	var catalogued: Dictionary = {}
	for item in report.settlement_identity_catalog: catalogued[item.root] = true
	for path in rows:
		if not path.begins_with("World/Settlements/") or path.split("/").size() != 3 or catalogued.has(path): continue
		var descendants: Array = []
		for child_path in rows:
			if child_path == path or child_path.begins_with(path+"/"): descendants.append(child_path)
		report.settlement_identity_catalog.append({"root":path,"whole_bounds":null,"parts":[],"descendant_paths":descendants,"bounds_proved":false,"reason":"Saved settlement identity has no supported saved mesh/collision bounds; do not omit or locate from root alone."})
		issues.append({"kind":"saved_settlement_without_bounds","path":path})
	var found: Dictionary = {}
	var collisions_found: Dictionary = {}
	for item in report.terrain: found[item.tile] = int(found.get(item.tile,0))+1
	for item in report.terrain_collision: collisions_found[item.tile] = int(collisions_found.get(item.tile,0))+1
	for tile in terrain_names:
		if int(found.get(tile,0)) != 1: issues.append({"kind":"target_or_neighbor_mesh_count","tile":tile,"count":found.get(tile,0)})
		if int(collisions_found.get(tile,0)) != 1: issues.append({"kind":"target_or_neighbor_collision_count","tile":tile,"count":collisions_found.get(tile,0)})
	report.expected_northern_12 = {"expected_from_prior_notes":12,"exact_identity_match_proved":false,"instruction":"Inspect complete saved settlement catalog by actual bounds. Do not select the nearest 12 or invent missing houses; saved and runtime membership require independent confirmation."}
	report.geometry_reuse = {"file":plan.reuse_geometry_file,"sha256":plan.reuse_geometry_sha256,"source":plan.reuse_source,"source_sha256":FileAccess.get_sha256(plan.reuse_source),"old_nonterrain_filter_z_min":-5000,"old_nonterrain_inventory_not_reused":true}
	finish(0)
