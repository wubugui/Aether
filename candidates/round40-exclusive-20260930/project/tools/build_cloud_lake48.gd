extends SceneTree
## Four source-authored lake meshes, matching collision and explicitly recorded
## scatter translations. Scene remains off-tree while built and compared.
const BASE := "res://scenes/candidate47/Game47.tscn"
const BASE_SHA := "ba236fdb78f662351ad8e89d82df4642b27721638412c833f86f6e8f682caa32"
const DEST := "res://scenes/candidate48/"
const TARGET := DEST + "Game48.tscn"
const ASSETS := "res://assets/lake48/"
const PREFABS := "res://scenes/lake48/"
const MESH_PATHS := ["World/Terrain/Ground_1_-2/Model/Ground_1_-2", "World/Terrain/Ground_1_-3/Model/Ground_1_-3", "World/Mountains/massif_cirque_wall/Model/massif_cirque_wall", "World/Mountains/massif_east_foothill/Model/massif_east_foothill"]
const SCATTER_COUNTS := {"oak_1_-2":48,"poplar_1_-2":20,"bush_1_-2":17,"rock_1_-2":26,"oak_1_-3":227,"poplar_1_-3":94,"pine_1_-3":2,"bush_1_-3":23,"rock_1_-3":43}
var payload_path := ""
var diagnostic_dir := ""
var payload := {}
var mesh_edits := {}
var shape_edits := {}
var scatter_edits := {}
var resource_cache := {}
var failures := []
var asset_inventory := []

func _initialize() -> void:
	parse_arguments()
	call_deferred("build")
func parse_arguments() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--payload="): payload_path=arg.trim_prefix("--payload=")
		if arg.begins_with("--diagnostic-dir="): diagnostic_dir=arg.trim_prefix("--diagnostic-dir=")
func require(ok: bool, message: String, details: Variant=null) -> bool:
	if ok: return true
	var row := {"error":message,"details":details}
	failures.append(row)
	push_error(message)
	print("LAKE48 FAILURE ",JSON.stringify(row))
	if not diagnostic_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(diagnostic_dir)
		var file := FileAccess.open(diagnostic_dir.path_join("lake48-failure.json"),FileAccess.WRITE)
		if file!=null:
			file.store_string(JSON.stringify({"failures":failures,"candidate_written":FileAccess.file_exists(TARGET)},"  "))
			file.close()
	return false
func abort_build(nodes: Array) -> void:
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
		var row := {"class":node.get_class()}
		for property in node.get_property_list():
			var key: String=property.name
			if not property.usage & PROPERTY_USAGE_STORAGE or key in ["owner","scene_file_path"]: continue
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
func clean_path(value: String) -> String:
	return value.trim_prefix("/Skyfarer/").trim_prefix("Skyfarer/")
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
func load_payload() -> bool:
	if not require(not payload_path.is_empty() and FileAccess.file_exists(payload_path),"--payload JSON required",payload_path): return false
	var parsed: Variant=JSON.parse_string(FileAccess.get_file_as_string(payload_path))
	if not require(parsed is Dictionary,"Invalid payload JSON"): return false
	payload=parsed
	if not require(int(payload.get("schema_version",0))==1 and payload.get("baseline_sha256","")==BASE_SHA,"Payload schema/baseline mismatch"): return false
	if not require(payload.get("meshes") is Array and payload.meshes.size()==4 and payload.get("scatter") is Array,"Expected four meshes and scatter edit array"): return false
	mesh_edits.clear();shape_edits.clear();scatter_edits.clear()
	for entry in payload.meshes:
		var path := clean_path(str(entry.get("node_path","")))
		var collision := path.get_base_dir().get_base_dir()+"/Collision/Shape"
		if not require(path in MESH_PATHS and not mesh_edits.has(path),"Mesh outside four permitted entities or duplicate",path): return false
		if not require(clean_path(str(entry.get("collision_path",collision)))==collision,"Unexpected collision target",entry): return false
		if not require(entry.get("vertices") is Array and entry.vertices.size()>=3 and entry.vertices.size()%3==0,"Triangle vertices missing",path): return false
		for point in entry.vertices:
			if not require(finite_values(point,3),"Non-finite or invalid vertex",path): return false
		var colors: Variant=entry.get("colors",[])
		if not require(colors is Array and (colors.size()==1 or colors.size()==entry.vertices.size()),"Colors must be one RGBA or per vertex",path): return false
		for color in colors:
			if not require(finite_values(color,4),"Invalid color",path): return false
		if entry.has("normals"):
			if not require(entry.normals is Array and entry.normals.size()==entry.vertices.size(),"Normal count mismatch",path): return false
			for normal in entry.normals:
				if not require(finite_values(normal,3) and v3(normal).length_squared()>.5,"Invalid normal",path): return false
		mesh_edits[path]=entry
		shape_edits[collision]=entry
	for entry in payload.scatter:
		var path := clean_path(str(entry.get("node_path","")))
		var index := int(entry.get("index",-1))
		if not require(path.begins_with("World/Vegetation/") and SCATTER_COUNTS.has(path.get_file()) and index>=0 and index<int(SCATTER_COUNTS.get(path.get_file(),0)),"Scatter target outside bounded 500 instances",entry): return false
		if not require(finite_values(entry.get("before_transform"),12) and finite_values(entry.get("after_transform"),12),"Scatter transforms require 12 finite numbers",entry): return false
		if not scatter_edits.has(path): scatter_edits[path]={}
		if not require(not scatter_edits[path].has(index),"Duplicate scatter edit",entry): return false
		var before := transform_from(entry.before_transform)
		var after := transform_from(entry.after_transform)
		if not require(before.basis==after.basis and absf(after.basis.determinant())>0.000001,"Scatter may translate only; retain exact basis",entry): return false
		scatter_edits[path][index]=entry
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
func preflight(game: Node, check_original_transforms: bool) -> bool:
	for path in mesh_edits:
		var node := game.get_node_or_null(path) as MeshInstance3D
		var collision := game.get_node_or_null(path.get_base_dir().get_base_dir()+"/Collision/Shape") as CollisionShape3D
		if not require(node!=null and node.mesh!=null and node.mesh.get_surface_count()==1 and collision!=null and collision.shape is ConcavePolygonShape3D,"Unsupported mesh/collider",path): return false
		if not require(collision.get_parent().collision_layer==5 and collision.get_parent().collision_mask==2,"Collision layers changed",path): return false
	var total := 0
	for name in SCATTER_COUNTS:
		var path: String="World/Vegetation/"+name
		var node := game.get_node_or_null(path) as MultiMeshInstance3D
		if not require(node!=null and node.multimesh!=null and node.multimesh.instance_count==SCATTER_COUNTS[name] and node.multimesh.transform_format==MultiMesh.TRANSFORM_3D,"Scatter count/format changed",path): return false
		var mm := node.multimesh
		var stride := 12+(4 if mm.use_colors else 0)+(4 if mm.use_custom_data else 0)
		if not require(mm.buffer.size()==stride*mm.instance_count,"Scatter buffer unavailable",path): return false
		total+=mm.instance_count
		if check_original_transforms and scatter_edits.has(path):
			for index in scatter_edits[path]:
				if not require(mm.get_instance_transform(index)==transform_from(scatter_edits[path][index].before_transform),"Original scatter transform differs from payload",{"path":path,"index":index,"actual":transform_values(mm.get_instance_transform(index))}): return false
	return require(total==500,"Expected exactly 500 existing target-tile instances",total)
func copy_multimesh(source: MultiMesh) -> MultiMesh:
	var result := MultiMesh.new()
	result.transform_format=source.transform_format
	result.use_colors=source.use_colors
	result.use_custom_data=source.use_custom_data
	result.mesh=source.mesh
	result.custom_aabb=source.custom_aabb
	result.physics_interpolation_quality=source.physics_interpolation_quality
	result.instance_count=source.instance_count
	result.buffer=source.buffer
	result.visible_instance_count=source.visible_instance_count
	result.resource_local_to_scene=source.resource_local_to_scene
	result.resource_name=source.resource_name
	return result
func apply_edits(game: Node) -> bool:
	for path in mesh_edits:
		var entry: Dictionary=mesh_edits[path]
		var node: MeshInstance3D=game.get_node(path)
		var shape_node: CollisionShape3D=game.get_node(path.get_base_dir().get_base_dir()+"/Collision/Shape")
		var inverse := world_transform(node).affine_inverse()
		var vertices := PackedVector3Array()
		var normals := PackedVector3Array()
		var colors := PackedColorArray()
		for point in entry.vertices: vertices.append(inverse*v3(point))
		for i in range(vertices.size()):
			var color: Array=entry.colors[0 if entry.colors.size()==1 else i]
			colors.append(Color(color[0],color[1],color[2],color[3]))
			if entry.has("normals"): normals.append((world_transform(node).basis.transposed()*v3(entry.normals[i])).normalized())
		if not entry.has("normals"):
			for i in range(0,vertices.size(),3):
				# Godot front faces use clockwise order. get_faces() / Blender export
				# payload must retain that order; outward normal is (c-a)x(b-a).
				var normal := (vertices[i+2]-vertices[i]).cross(vertices[i+1]-vertices[i]).normalized()
				if not require(normal.length_squared()>.5,"Degenerate target triangle",{"path":path,"triangle":i/3}): return false
				for j in range(3): normals.append(normal)
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals;arrays[Mesh.ARRAY_COLOR]=colors
		var mesh := ArrayMesh.new()
		mesh.resource_name=node.mesh.resource_name
		mesh.resource_local_to_scene=node.mesh.resource_local_to_scene
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
		mesh.surface_set_material(0,node.mesh.surface_get_material(0))
		node.mesh=mesh
		var collision_vertices := PackedVector3Array()
		var shape_inverse := world_transform(shape_node).affine_inverse()
		for point in entry.vertices: collision_vertices.append(shape_inverse*v3(point))
		var shape := shape_node.shape.duplicate(false) as ConcavePolygonShape3D
		shape.set_faces(collision_vertices)
		shape_node.shape=shape
	for path in scatter_edits:
		var node: MultiMeshInstance3D=game.get_node(path)
		var original := node.multimesh
		var copy := copy_multimesh(original)
		resource_cache.clear()
		if not require(canonical(original)==canonical(copy) and original.buffer==copy.buffer,"MultiMesh copy changed untouched data",path): return false
		for index in scatter_edits[path]: copy.set_instance_transform(index,transform_from(scatter_edits[path][index].after_transform))
		node.multimesh=copy
	return true
func targets_state(game: Node) -> Dictionary:
	resource_cache.clear()
	var result := {}
	for path in mesh_edits: result[path]=canonical(game.get_node(path).mesh)
	for path in shape_edits: result[path]=canonical(game.get_node(path).shape)
	for path in scatter_edits: result[path]=canonical(game.get_node(path).multimesh)
	return result
func verify_payload_result(game: Node) -> bool:
	for path in mesh_edits:
		var node: MeshInstance3D=game.get_node(path)
		var collision: CollisionShape3D=game.get_node(path.get_base_dir().get_base_dir()+"/Collision/Shape")
		var faces: PackedVector3Array=node.mesh.get_faces()
		var collision_faces: PackedVector3Array=collision.shape.get_faces()
		var expected: Array=mesh_edits[path].vertices
		if not require(faces.size()==expected.size() and collision_faces.size()==expected.size(),"Mesh/collision triangle counts mismatch",path): return false
		var transform := world_transform(node)
		var collision_transform := world_transform(collision)
		var max_error := 0.0
		for i in range(faces.size()):
			max_error=maxf(max_error,(transform*faces[i]).distance_to(v3(expected[i])))
			max_error=maxf(max_error,(collision_transform*collision_faces[i]).distance_to(v3(expected[i])))
		if not require(max_error<0.002,"Mesh/collision/source geometry differs >2mm",{"path":path,"max_error":max_error}): return false
	for path in scatter_edits:
		for index in scatter_edits[path]:
			if not require(game.get_node(path).multimesh.get_instance_transform(index)==transform_from(scatter_edits[path][index].after_transform),"Saved scatter edit mismatch",{"path":path,"index":index}): return false
	return true
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
func save_independent_assets(game: Node) -> bool:
	DirAccess.make_dir_recursive_absolute(ASSETS)
	DirAccess.make_dir_recursive_absolute(PREFABS)
	for path in mesh_edits:
		var node: MeshInstance3D=game.get_node(path)
		var shape: CollisionShape3D=game.get_node(path.get_base_dir().get_base_dir()+"/Collision/Shape")
		var name: String=node.name
		if not save_asset(node.mesh,ASSETS+name+".mesh"): return false
		if not save_asset(shape.shape,ASSETS+name+"_collision.res"): return false
		# Externalize only new resources so the native scene remains below 100 MiB.
		node.mesh.take_over_path(ASSETS+name+".mesh")
		shape.shape.take_over_path(ASSETS+name+"_collision.res")
		var prefab: Node3D=node.get_parent().get_parent().duplicate()
		prefab.transform=Transform3D.IDENTITY
		own(prefab,prefab)
		var packed := PackedScene.new()
		if not require(packed.pack(prefab)==OK,"Independent prefab pack failed",name): prefab.free();return false
		var ok := save_asset(packed,PREFABS+name+".tscn")
		prefab.free()
		if not ok: return false
	for name in SCATTER_COUNTS:
		var mm: MultiMesh=game.get_node("World/Vegetation/"+name).multimesh
		var copy := copy_multimesh(mm)
		if not save_asset(copy,ASSETS+"Grounded_"+name+".res"): return false
		if scatter_edits.has("World/Vegetation/"+name):
			copy.take_over_path(ASSETS+"Grounded_"+name+".res")
			game.get_node("World/Vegetation/"+name).multimesh=copy
	return true
func build() -> void:
	if not require(DisplayServer.get_name()!="headless","Refuse headless save: exact MultiMesh buffers and deferred Sky require real renderer"):
		quit(2);return
	if not require(FileAccess.file_exists(BASE) and FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET),"Baseline SHA mismatch, missing baseline or existing target; never overwrite") or not load_payload():
		await abort_build([]);return
	var protected_script_sha := FileAccess.get_sha256("res://scripts/open_world.gd")
	var game: Node3D=load(BASE).instantiate()
	await settle()
	if not preflight(game,true): await abort_build([game]);return
	var weather := weather_state(game)
	if weather.is_empty(): await abort_build([game]);return
	var before := snapshot(game)
	if not require(before==snapshot(game),"Unmodified double-snapshot control drift"):
		await abort_build([game]);return
	if not apply_edits(game) or not verify_payload_result(game): await abort_build([game]);return
	var edited := snapshot(game)
	if not require(before==edited,"Out-of-scope scene/resource change",differences(before,edited)):
		await abort_build([game]);return
	var expected := targets_state(game)
	if not save_independent_assets(game): await abort_build([game]);return
	own(game,game)
	var packed := PackedScene.new()
	if not require(packed.pack(game)==OK,"Candidate pack failed"): await abort_build([game]);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"Candidate save failed"): await abort_build([game]);return
	var scene_file := FileAccess.open(TARGET,FileAccess.READ)
	var scene_bytes := scene_file.get_length()
	scene_file.close()
	if not require(scene_bytes<100*1024*1024,"Game48 exceeds 100 MiB",scene_bytes): await abort_build([game]);return
	var reloaded: Node3D=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	await settle()
	var actual := snapshot(reloaded)
	if not require(before==actual,"Reload changed unaffected state",differences(before,actual)) or not require(expected==targets_state(reloaded),"Reload changed edited meshes/collision/scatter"):
		await abort_build([game,reloaded]);return
	if not preflight(reloaded,false) or not verify_payload_result(reloaded) or not require(weather==weather_state(reloaded),"Exact 48000-float weather buffers changed"):
		await abort_build([game,reloaded]);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256("res://scripts/open_world.gd")==protected_script_sha,"Baseline or open_world.gd changed"):
		await abort_build([game,reloaded]);return
	var report := {"passed":true,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"payload":payload_path,"payload_sha256":FileAccess.get_sha256(payload_path),"source_metadata":payload.get("source_metadata",{}),"candidate_bytes":scene_bytes,"node_count":before.size(),"unaffected_fingerprint":digest(before),"edited_targets":expected,"mesh_count":mesh_edits.size(),"scatter_total":500,"scatter_relocated":payload.scatter.size(),"scatter_groups_changed":scatter_edits.size(),"weather":weather,"independent_assets":asset_inventory,"reload_exact":true,"renderer":RenderingServer.get_video_adapter_name(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"scope":"Only four named mesh/collision resources and explicitly listed scatter translation slots changed. All other stored node/resource values and untouched MultiMesh float slots matched canonical47. No scene entered the tree during build; deferred Sky settled 3 frames + post_draw. Native scene references new independent mesh/collider/scatter resources to stay below 100 MiB; all assets/prefabs saved and reloaded. No open_world edits."}
	var file := FileAccess.open(DEST+"build-report-48.json",FileAccess.WRITE)
	if not require(file!=null,"Could not write build report"): await abort_build([game,reloaded]);return
	file.store_string(JSON.stringify(report,"  "));file.close()
	game.free();reloaded.free()
	for i in range(8): await process_frame
	print("LAKE48 BUILT AND RELOADED ",report.candidate_sha256)
	quit(0)
