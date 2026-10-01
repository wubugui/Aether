extends SceneTree
## Independent additive island integration. Never changes a Game48 node/resource.
const BASE := "res://scenes/candidate48/Game48.tscn"
const BASE_SHA := "3034e74f33087f8eb843ffc19e170bb14bbe85d1c7a272edfa01af614bd18fcd"
const DEST := "res://scenes/candidate49/"
const TARGET := DEST + "Game49.tscn"
const ASSETS := "res://assets/lake49/"
const PREFABS := "res://scenes/candidate49/prefabs/"
const NEW_GROUP := "World/LakeIslands49"
const ISLAND_NAMES := ["island_near_left","island_far_middle","island_near_right","foreground_rock"]
const BED_PATHS := ["World/Terrain/Ground_1_-2/Model/Ground_1_-2","World/Terrain/Ground_1_-3/Model/Ground_1_-3"]
var payload_path := ""
var diagnostic_dir := ""
var payload := {}
var resource_cache := {}
var failures := []
var asset_inventory := []
var source_inventory := []
var expected_inventory := {}
var mesh_entries := {}
var collision_entries := {}
var mesh_edits := {}
var shape_edits := {}
var scatter_edits := {}

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
	print("LAKE49 FAILURE ",JSON.stringify(row))
	if not diagnostic_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(diagnostic_dir)
		var file := FileAccess.open(diagnostic_dir.path_join("lake49-failure.json"),FileAccess.WRITE)
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
func safe_name(value: Variant) -> bool:
	return value is String and not value.is_empty() and value.validate_node_name()==value and value not in [".",".."]
func island_path(name: String) -> String: return NEW_GROUP+"/"+name
func mesh_path(island: String, name: String) -> String: return island_path(island)+"/Meshes/"+name
func collision_path(island: String, name: String) -> String: return island_path(island)+"/Collision_"+name+"/Shape"
func load_payload() -> bool:
	if not require(not payload_path.is_empty() and FileAccess.file_exists(payload_path),"--payload JSON required",payload_path): return false
	var parsed: Variant=JSON.parse_string(FileAccess.get_file_as_string(payload_path))
	if not require(parsed is Dictionary,"Invalid payload JSON"): return false
	payload=parsed
	if not require(int(payload.get("schema_version",0))==1 and payload.get("baseline_sha256","")==BASE_SHA,"Payload schema/baseline mismatch"): return false
	if not require(payload.get("islands") is Array and payload.islands.size()==4,"Expected exactly four independent island/rock prefabs"): return false
	mesh_entries.clear();collision_entries.clear();expected_inventory.clear();source_inventory.clear()
	expected_inventory[NEW_GROUP]="Node3D"
	var seen := []
	var trees := 0
	for island in payload.islands:
		var name: String=island.get("name","")
		if not require(name in ISLAND_NAMES and name not in seen,"Unexpected or duplicate island",name): return false
		seen.append(name)
		if not require(finite_values(island.get("anchor"),3) and island.get("meshes") is Array and island.meshes.size()>0,"Missing anchor or meshes",name): return false
		if not require(str(island.get("source_blend","")).begins_with("source-assets/lake49/") and str(island.get("source_glb","")).begins_with("source-assets/lake49/"),"Missing independent editable source links",name): return false
		for kind in ["source_blend","source_glb"]:
			var source: String=payload_path.get_base_dir().path_join(str(island[kind]).get_file())
			if not require(FileAccess.file_exists(source),"Missing linked independent Blender/GLB source",source): return false
			source_inventory.append({"island":name,"kind":kind,"source_link":island[kind],"absolute_path":source,"sha256":FileAccess.get_sha256(source)})
		expected_inventory[island_path(name)]="Node3D"
		expected_inventory[island_path(name)+"/Meshes"]="Node3D"
		var roots := 0
		for entry in island.meshes:
			var mesh_name: String=entry.get("name","")
			var path := mesh_path(name,mesh_name)
			if not require(safe_name(mesh_name) and not mesh_entries.has(path),"Invalid or duplicate mesh name",path): return false
			if not require(entry.get("vertices") is Array and entry.vertices.size()>=3 and entry.vertices.size()%3==0,"Triangle soup required",path): return false
			for point in entry.vertices:
				if not require(finite_values(point,3),"Invalid triangle corner",path): return false
			if not require(entry.get("colors") is Array and (entry.colors.size()==1 or entry.colors.size()==entry.vertices.size()),"One color or per-corner colors required",path): return false
			for color in entry.colors:
				if not require(finite_values(color,4),"Invalid RGBA",path): return false
			if entry.has("normals"):
				if not require(entry.normals is Array and entry.normals.size()==entry.vertices.size(),"Normal count mismatch",path): return false
				for normal in entry.normals:
					if not require(finite_values(normal,3) and v3(normal).length_squared()>.5,"Invalid normal",path): return false
			mesh_entries[path]=entry
			expected_inventory[path]="MeshInstance3D"
			if entry.get("collision",false):
				collision_entries[collision_path(name,mesh_name)]=entry
				expected_inventory[island_path(name)+"/Collision_"+mesh_name]="StaticBody3D"
				expected_inventory[collision_path(name,mesh_name)]="CollisionShape3D"
			if str(entry.get("role","")).replace("_","")=="rockroot":
				roots+=1
				if not require(entry.get("collision",false),"Closed rock root must have matching collision",path): return false
		if not require(roots==1,"Each independent prefab needs exactly one closed rockroot",name): return false
		if not require(island.get("trees") is Array and island.get("bedroot_samples") is Array and island.bedroot_samples.size()>=4,"Tree/support and root burial probes required",name): return false
		for tree in island.trees:
			if not require(safe_name(tree.get("name")) and finite_values(tree.get("foot_world"),3) and mesh_entries.has(mesh_path(name,str(tree.get("support_mesh","")))),"Invalid tree support declaration",tree): return false
			trees+=1
		for sample in island.bedroot_samples:
			if not require(finite_values(sample.get("world"),3),"Invalid bedroot sample",sample): return false
	return require(trees==7,"Expected exactly seven sparse modeled pines",trees)
func make_mesh(entry: Dictionary, anchor: Vector3) -> ArrayMesh:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	for point in entry.vertices: vertices.append(v3(point)-anchor)
	for i in range(vertices.size()):
		var rgba: Array=entry.colors[0 if entry.colors.size()==1 else i]
		colors.append(Color(rgba[0],rgba[1],rgba[2],rgba[3]))
		if entry.has("normals"): normals.append(v3(entry.normals[i]).normalized())
	if not entry.has("normals"):
		for i in range(0,vertices.size(),3):
			var normal := (vertices[i+2]-vertices[i]).cross(vertices[i+1]-vertices[i]).normalized()
			if not require(normal.length_squared()>.5,"Degenerate new mesh triangle",{"mesh":entry.name,"triangle":i/3}): return null
			for j in range(3): normals.append(normal)
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals;arrays[Mesh.ARRAY_COLOR]=colors
	var material := StandardMaterial3D.new()
	material.resource_name="Lake49_"+str(entry.get("role","rock"))
	material.vertex_color_use_as_albedo=true
	material.roughness=.96
	material.diffuse_mode=BaseMaterial3D.DIFFUSE_LAMBERT
	var mesh := ArrayMesh.new()
	mesh.resource_name="Lake49_"+str(entry.name)
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	mesh.surface_set_material(0,material)
	return mesh
func add_islands(game: Node3D) -> bool:
	if not require(game.get_node_or_null(NEW_GROUP)==null,"New islands group already exists"): return false
	var group := Node3D.new()
	group.name="LakeIslands49"
	game.get_node("World").add_child(group)
	group.set_meta("source_authoring","source-assets/lake49")
	group.set_meta("baseline_sha256",BASE_SHA)
	for island in payload.islands:
		var anchor := v3(island.anchor)
		var root_node := Node3D.new()
		root_node.name=island.name
		root_node.position=anchor
		root_node.set_meta("source_blend",island.source_blend)
		root_node.set_meta("source_glb",island.source_glb)
		root_node.set_meta("world_anchor",anchor)
		for source in source_inventory:
			if source.island==island.name: root_node.set_meta(str(source.kind)+"_sha256",source.sha256)
		group.add_child(root_node)
		var meshes := Node3D.new()
		meshes.name="Meshes"
		root_node.add_child(meshes)
		for entry in island.meshes:
			var node := MeshInstance3D.new()
			node.name=entry.name
			node.mesh=make_mesh(entry,anchor)
			if node.mesh==null: node.free();return false
			node.set_meta("authoring_role",entry.get("role",""))
			meshes.add_child(node)
			if entry.get("collision",false):
				var body := StaticBody3D.new()
				body.name="Collision_"+str(entry.name)
				body.collision_layer=5;body.collision_mask=2
				root_node.add_child(body)
				var shape_node := CollisionShape3D.new()
				shape_node.name="Shape"
				var shape := ConcavePolygonShape3D.new()
				shape.set_faces(node.mesh.get_faces())
				shape.backface_collision=true
				shape_node.shape=shape
				body.add_child(shape_node)
	# Own ONLY new nodes, preserving every baseline owner's stored identity.
	own(group,game)
	return true
func group_inventory(game: Node) -> Dictionary:
	var result := {}
	var group := game.get_node_or_null(NEW_GROUP)
	if group==null: return result
	var nodes: Array[Node]=[group]
	nodes.append_array(group.find_children("*","",true,false))
	for node in nodes: result[str(game.get_path_to(node))]=node.get_class()
	return result
func target_state(game: Node) -> Dictionary:
	resource_cache.clear()
	var data := {}
	var nodes: Array[Node]=[game.get_node(NEW_GROUP)]
	nodes.append_array(game.get_node(NEW_GROUP).find_children("*","",true,false))
	var all := snapshot(game,false)
	for node in nodes:
		var path := str(game.get_path_to(node))
		data[path]=all[path]
	return data
func verify_payload_result(game: Node) -> bool:
	if not require(group_inventory(game)==expected_inventory,"Strict additive group inventory mismatch",differences(expected_inventory,group_inventory(game))): return false
	for path in mesh_entries:
		var node: MeshInstance3D=game.get_node(path)
		var expected: Dictionary=mesh_entries[path]
		var faces := node.mesh.get_faces()
		if not require(node.mesh.get_surface_count()==1 and faces.size()==expected.vertices.size(),"Saved new mesh triangle count mismatch",path): return false
		var arrays := node.mesh.surface_get_arrays(0)
		var normals: PackedVector3Array=arrays[Mesh.ARRAY_NORMAL]
		var colors: PackedColorArray=arrays[Mesh.ARRAY_COLOR]
		if not require(normals.size()==faces.size() and colors.size()==faces.size(),"New mesh normal/color arrays missing",path): return false
		var max_error := 0.0
		for i in range(faces.size()):
			max_error=maxf(max_error,(world_transform(node)*faces[i]).distance_to(v3(expected.vertices[i])))
			var rgba: Array=expected.colors[0 if expected.colors.size()==1 else i]
			if not require(absf(colors[i].r-float(rgba[0]))<=.00393 and absf(colors[i].g-float(rgba[1]))<=.00393 and absf(colors[i].b-float(rgba[2]))<=.00393 and absf(colors[i].a-float(rgba[3]))<=.00393,"Saved color differs",{"path":path,"index":i}): return false
		if not require(max_error<.002,"Saved mesh/source differs >2mm",{"path":path,"max_error":max_error}): return false
	for path in collision_entries:
		var node: CollisionShape3D=game.get_node(path)
		var expected: Array=collision_entries[path].vertices
		if not require(node.shape is ConcavePolygonShape3D and node.get_parent().collision_layer==5 and node.get_parent().collision_mask==2,"Wrong new collision type/layers",path): return false
		var faces: PackedVector3Array=node.shape.get_faces()
		if not require(faces.size()==expected.size(),"Saved collision triangle count differs",path): return false
		var max_error := 0.0
		for i in range(faces.size()): max_error=maxf(max_error,(world_transform(node)*faces[i]).distance_to(v3(expected[i])))
		if not require(max_error<.002,"Saved collider/source differs >2mm",{"path":path,"max_error":max_error}): return false
	return true
func save_independent_assets(game: Node) -> bool:
	DirAccess.make_dir_recursive_absolute(ASSETS)
	DirAccess.make_dir_recursive_absolute(PREFABS)
	for island in payload.islands:
		for entry in island.meshes:
			var node: MeshInstance3D=game.get_node(mesh_path(island.name,entry.name))
			var file: String=ASSETS+island.name+"__"+entry.name
			if not save_asset(node.mesh,file+".mesh"): return false
			node.mesh.take_over_path(file+".mesh")
			if entry.get("collision",false):
				var shape: CollisionShape3D=game.get_node(collision_path(island.name,entry.name))
				if not save_asset(shape.shape,file+"_collision.res"): return false
				shape.shape.take_over_path(file+"_collision.res")
		var prefab: Node3D=game.get_node(island_path(island.name)).duplicate()
		prefab.transform=Transform3D.IDENTITY
		own(prefab,prefab)
		var packed := PackedScene.new()
		if not require(packed.pack(prefab)==OK,"Independent prefab packing failed",island.name): prefab.free();return false
		var ok := save_asset(packed,PREFABS+island.name+".tscn")
		prefab.free()
		if not ok: return false
	return true
func build() -> void:
	if not require(DisplayServer.get_name()!="headless","Refuse headless save: exact weather MultiMesh buffers and deferred Sky need real renderer"):
		quit(2);return
	if not require(FileAccess.file_exists(BASE) and FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET),"Baseline SHA mismatch, missing baseline or existing target; never overwrite") or not load_payload():
		await abort_build([]);return
	var protected_script_sha := FileAccess.get_sha256("res://scripts/open_world.gd")
	var baseline_packed: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var game: Node3D=baseline_packed.instantiate()
	await settle()
	var weather := weather_state(game)
	if weather.is_empty(): await abort_build([game]);return
	var before := graph_state(game,baseline_packed)
	if not require(before==graph_state(game,baseline_packed),"Unmodified canonical47 double-snapshot control drift"):
		await abort_build([game]);return
	if not add_islands(game) or not verify_payload_result(game): await abort_build([game]);return
	if not require(before==graph_state(game,baseline_packed),"Additive integration changed old graph/resource/ownership/group state",differences(before,graph_state(game,baseline_packed))):
		await abort_build([game]);return
	var expected := target_state(game)
	if not save_independent_assets(game): await abort_build([game]);return
	var packed := PackedScene.new()
	if not require(packed.pack(game)==OK,"Candidate pack failed"): await abort_build([game]);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"Candidate save failed"): await abort_build([game]);return
	var scene_file := FileAccess.open(TARGET,FileAccess.READ)
	var scene_bytes := scene_file.get_length()
	scene_file.close()
	if not require(scene_bytes<100*1024*1024,"Game49 exceeds 100 MiB",scene_bytes): await abort_build([game]);return
	var reload_packed: PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var reloaded: Node3D=reload_packed.instantiate()
	await settle()
	var actual := graph_state(reloaded,reload_packed)
	if not require(before==actual,"Reload changed old Game48 graph/resource values",differences(before,actual)) or not require(expected==target_state(reloaded),"Reload changed new islands exact stored state",differences(expected,target_state(reloaded))):
		await abort_build([game,reloaded]);return
	if not verify_payload_result(reloaded) or not require(weather==weather_state(reloaded),"Exact 48000-float weather buffers changed"):
		await abort_build([game,reloaded]);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256("res://scripts/open_world.gd")==protected_script_sha,"Baseline or open_world.gd changed"):
		await abort_build([game,reloaded]);return
	var report := {"build_saved_reload_passed":true,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"payload":payload_path,"payload_sha256":FileAccess.get_sha256(payload_path),"source_metadata":payload.get("source_metadata",{}),"source_files":source_inventory,"candidate_bytes":scene_bytes,"baseline_node_count":before.nodes.size(),"unaffected_fingerprint":digest(before),"old_node_resource_fingerprint":digest(before.nodes),"new_group_fingerprint":digest(expected),"new_group_inventory":expected_inventory,"mesh_count":mesh_entries.size(),"collider_count":collision_entries.size(),"weather":weather,"independent_assets":asset_inventory,"reload_exact":true,"renderer":RenderingServer.get_video_adapter_name(),"limited_geometry_runtime_passed":false,"requested_motion_all_passed":false,"total_acceptance_passed":false,"hardware_gpu_acceptance":false,"visual_acceptance":false,"scope":"Only additive World/LakeIslands49. Every old Game48 stored node/resource value, exact MultiMesh float buffer, ownership, node order, persistent group and connection matched canonical47 methodology. Scene never entered runtime tree during build. Four independent prefabs and externalized new mesh/collider resources reloaded. Deferred Sky settled 3 frames + post_draw. Build success does not imply motion, visual or total acceptance."}
	var file := FileAccess.open(DEST+"build-report-49.json",FileAccess.WRITE)
	if not require(file!=null,"Could not write build report"): await abort_build([game,reloaded]);return
	file.store_string(JSON.stringify(report,"  "));file.close()
	await settle()
	game.free();reloaded.free()
	for i in range(8): await process_frame
	print("LAKE49 BUILT AND RELOADED ",report.candidate_sha256)
	quit(0)
