extends SceneTree
## Independent Game51. Exact per-node binding whitelist; no generic material mask.
const BASE := "res://scenes/candidate50/Game50.tscn"
const BASE_SHA := "031b39ea75680e98fbed4882507251ec0ebfb3469300f82402891a0137351ff0"
const DEST := "res://scenes/candidate51/"
const TARGET := DEST+"Game51.tscn"
const ASSETS := "res://assets/reflection51/"
const NEW_GROUP := "World/LakeReflection51"
const CONTROLLER := "res://scripts/lake_reflection51.gd"
const WATER_SOURCE := ASSETS+"lake_water_reflection51.gdshader"
const SOURCE_ROOT := "/workspace/scratch/a29d03198654/Aether/source-assets/reflection51"
const SCOPE_PATH := "/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection50-material-intake/reflection50-binding-scope.json"
const MARKER := 524288
const WATER_LAYER := 262144
const Factory = preload("res://tools/reflection51_materials.gd")
var diagnostic_dir := ""
var resource_cache := {}
var failures := []
var asset_inventory := []
var mesh_edits := {}
var shape_edits := {}
var scatter_edits := {}
var property_masks := {}
var binding_specs := []
var runtime_scope := []
var material_factory: RefCounted
var binding_ledger := []
var ocean_ledger := {}
var scope_plan := {}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--diagnostic-dir="): diagnostic_dir=arg.trim_prefix("--diagnostic-dir=")
	call_deferred("build")
func require(ok: bool, message: String, details: Variant=null) -> bool:
	if ok: return true
	var row := {"error":message,"details":details}
	failures.append(row)
	push_error(message)
	print("LAKE51 FAILURE ",JSON.stringify(row))
	if not diagnostic_dir.is_empty():
		DirAccess.make_dir_recursive_absolute(diagnostic_dir)
		var file := FileAccess.open(diagnostic_dir.path_join("lake51-failure.json"),FileAccess.WRITE)
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
func property_exists(node: Object,key: String) -> bool:
	for prop in node.get_property_list():
		if str(prop.name)==key: return true
	return false
func permit(path: String,key: String) -> void:
	if not property_masks.has(path): property_masks[path]=[]
	if key not in property_masks[path]: property_masks[path].append(key)
func add_binding(game: Node,path: String,key: String,source: Material,reason: String) -> bool:
	if not require(source!=null,"Missing authoritative/active source material",{"path":path,"property":key}): return false
	for spec in binding_specs:
		if spec.path==path and spec.property==key: return require(spec.source_material==source,"Conflicting duplicate binding source",path+"/"+key)
	var node := game.get_node_or_null(path)
	if not require(node!=null and property_exists(node,key),"Binding node/property absent",path+"/"+key): return false
	binding_specs.append({"path":path,"property":key,"source_material":source,"old_binding_value":node.get(key),"reason":reason})
	permit(path,key)
	return true
func discover_bindings(game: Node) -> bool:
	scope_plan=JSON.parse_string(FileAccess.get_file_as_string(SCOPE_PATH))
	if not require(scope_plan.get("node_scope_count",0)==311 and scope_plan.get("baseline49_sha256","")=="52d13fcb7ea412d3a0fae2eedb1d0f9c369dbe06c0da320d786c26c97c475ec8","Unexpected explicitly approved binding scope"): return false
	binding_specs.clear();runtime_scope.clear();property_masks.clear()
	var generated := []
	for row in scope_plan.node_scope:
		var path: String=row.node_path
		var node := game.get_node_or_null(path)
		if node==null:
			if not require(path in ["World/Generated_ground_-7_0","World/Generated_ground_-7_1","World/Generated_ground_-7_-1"],"Missing non-generated allowlisted node",path): return false
			generated.append(path);runtime_scope.append({"path":path,"authority":"World","property":"stream_terrain_material","runtime_generated":true});continue
		var authority: String=str(row.get("authority_owner","")) if row.get("authority_owner")!=null else ""
		if path.begins_with("Airship/Visuals/") and node is MeshInstance3D and not node.get_meta("persistent_material40",false):
			var key := "cloth_material" if str(node.name)=="Flag" else "hull_material"
			if not add_binding(game,"Airship",key,game.get_node("Airship").get(key),"airship_body._ready actual authority"): return false
			runtime_scope.append({"path":path,"authority":"Airship","property":key,"runtime_generated":false});continue
		if not authority.is_empty():
			if not require(authority!="Airship" and property_exists(game.get_node(authority),"surface_material"),"Unknown material authority",authority): return false
			if not add_binding(game,authority,"surface_material",game.get_node(authority).get("surface_material"),"AssetInstance._ready surface_material authority"): return false
			runtime_scope.append({"path":path,"authority":authority,"property":"surface_material","runtime_generated":false});continue
		if node is MeshInstance3D:
			if node.material_override!=null:
				if not add_binding(game,path,"material_override",node.material_override,"direct material_override"): return false
			else:
				if not require(node.mesh!=null,"Missing direct mesh",path): return false
				for surface in range(node.mesh.get_surface_count()):
					if not add_binding(game,path,"surface_material_override/"+str(surface),node.get_active_material(surface),"per-surface active binding; original mesh remains immutable"): return false
		elif node is MultiMeshInstance3D:
			if not require(node.multimesh!=null and node.multimesh.mesh!=null,"Missing allowlisted MultiMesh",path): return false
			var source: Material=node.material_override
			if source==null:
				source=node.multimesh.mesh.surface_get_material(0)
				for i in range(node.multimesh.mesh.get_surface_count()):
					if not require(node.multimesh.mesh.surface_get_material(i)==source,"MultiMesh has distinct per-surface materials; cannot collapse",path): return false
			if not add_binding(game,path,"material_override",source,"Rain/Snow/direct MultiMesh binding, including invisible instances"): return false
		else: return require(false,"Unrecognized direct binding node type",path)
		runtime_scope.append({"path":path,"direct":true,"runtime_generated":false})
	for key in ["stream_terrain_material","stream_world_material","stream_cloud_material"]:
		if not add_binding(game,"World",key,game.get_node("World").get(key),"world39 authoritative future streamed geometry material"): return false
	permit("World/Ocean","material_override");permit("World/Ocean","layers");permit("Camera","cull_mask")
	return require(generated.size()==3 and runtime_scope.size()==311,"Expected exact311 runtime scope including3 generated names")
func validate_reserved_layers(game: Node) -> bool:
	for node in game.find_children("*","VisualInstance3D",true,false):
		if not require((node.layers & (MARKER|WATER_LAYER))==0,"Reserved reflection layer already used",str(game.get_path_to(node))): return false
	return true
func apply_materials(game: Node) -> bool:
	material_factory=Factory.new()
	if not material_factory.configure(SOURCE_ROOT,Callable(self,"digest"),Callable(self,"canonical")): return require(false,"Material factory configuration rejected",material_factory.failure)
	for spec in binding_specs:
		var copy: ShaderMaterial=material_factory.copy_material(spec.source_material)
		if copy==null: return require(false,"Exact material-copy preflight rejected",{"binding":spec.path+"/"+spec.property,"reason":material_factory.failure})
		game.get_node(spec.path).set(spec.property,copy)
		binding_ledger.append({"path":spec.path,"property":spec.property,"reason":spec.reason,"old_binding_fingerprint":digest(canonical(spec.old_binding_value)),"source_material_fingerprint":digest(canonical(spec.source_material)),"source_class":spec.source_material.get_class(),"new_material_instance_id":copy.get_instance_id(),"new_material_fingerprint":digest(canonical(copy))})
	return require(material_factory.materials.size()==114,"Expected exact114 scoped material copies (112 ready plus2 further stream authorities)",material_factory.materials.size())
func material_parameters(material: ShaderMaterial) -> Dictionary:
	var result := {}
	for uniform in material.shader.get_shader_uniform_list(): result[str(uniform.name)]=material.get_shader_parameter(uniform.name)
	return result
func stored_properties(resource: Resource,omit: Array=[]) -> Dictionary:
	var data := {}
	for prop in resource.get_property_list():
		var key: String=prop.name
		if prop.usage & PROPERTY_USAGE_STORAGE and key!="resource_path" and key not in omit: data[key]=resource.get(key)
	return data
func prepare_ocean(source: ShaderMaterial) -> ShaderMaterial:
	var path := SOURCE_ROOT+"/water-shader-ledger.json"
	var ledger: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))
	var code := FileAccess.get_file_as_string(WATER_SOURCE)
	var restored := code
	for key in ["global_insertion","normal_insertion","fragment_tail_insertion"]:
		var block: String=ledger.get(key,"")
		if not require(not block.is_empty() and restored.count(block)==1,"Exact51 water insertion missing",key): return null
		restored=restored.replace(block,"")
	if not require(restored==source.shader.code,"Reflection water source differs outside three exact insertion strings",{"source_sha":source.shader.code.sha256_text(),"restored_sha":restored.sha256_text()}): return null
	var copy := source.duplicate(false) as ShaderMaterial
	var shader := source.shader.duplicate(false) as Shader
	shader.code=code;copy.shader=shader
	var before := material_parameters(source)
	for name in before: copy.set_shader_parameter(name,source.get_shader_parameter(name))
	copy.set_shader_parameter("lake51_reflection_enabled",false)
	copy.set_shader_parameter("lake51_reflection_strength",.94)
	var after := material_parameters(copy)
	var extra := []
	for name in after:
		if not before.has(name): extra.append(name)
	var allowed := ["lake51_reflection_enabled","lake51_reflection_strength","lake51_reflection_texture","lake51_reflection_view","lake51_reflection_projection"]
	extra.sort();allowed.sort()
	if not require(extra==allowed,"Unexpected new51 Ocean uniform schema",extra): return null
	var omissions := ["shader"]
	for name in extra: omissions.append("shader_parameter/"+name)
	if not require(canonical(stored_properties(source,["shader"]))==canonical(stored_properties(copy,omissions)),"51 Ocean changed any old50 stored uniform/flag"): return null
	for name in before:
		if not require(canonical(before[name])==canonical(copy.get_shader_parameter(name)),"51 Ocean changed original50 declared uniform",name): return null
	ocean_ledger={"source_material_fingerprint":digest(canonical(source)),"new_material_fingerprint":digest(canonical(copy)),"source_shader_sha256":source.shader.code.sha256_text(),"new_shader_sha256":shader.code.sha256_text(),"exact_reverse_insertion_roundtrip":true,"original_uniforms":canonical(before),"new_uniform_names":extra,"source_ledger_sha256":FileAccess.get_sha256(path),"new_shader_source_sha256":FileAccess.get_sha256(WATER_SOURCE)}
	return copy
func save_material_assets(game: Node) -> bool:
	DirAccess.make_dir_recursive_absolute(ASSETS)
	var shader_paths := {}
	var index := 0
	for source_id in material_factory.shaders:
		var shader: Shader=material_factory.shaders[source_id]
		var path := ASSETS+"clip_shader_%03d.tres"%index
		if not save_asset(shader,path): return false
		shader.take_over_path(path);shader_paths[shader.get_instance_id()]=path;index+=1
	var material_paths := {}
	index=0
	for source_id in material_factory.materials:
		var material: ShaderMaterial=material_factory.materials[source_id]
		var path := ASSETS+"clip_material_%03d.tres"%index
		if not save_asset(material,path): return false
		material.take_over_path(path);material_paths[material.get_instance_id()]=path;index+=1
	for row in binding_ledger: row.new_material_path=material_paths[row.new_material_instance_id]
	for row in material_factory.material_ledger: row.new_material_path=material_paths[row.output_resource_instance_id]
	for row in material_factory.shader_ledger: row.new_shader_path=shader_paths[row.output_resource_instance_id]
	var ocean: ShaderMaterial=game.get_node("World/Ocean").material_override
	if not save_asset(ocean.shader,ASSETS+"ocean_reflection_shader.tres"): return false
	ocean.shader.take_over_path(ASSETS+"ocean_reflection_shader.tres")
	if not save_asset(ocean,ASSETS+"ocean_reflection_material.tres"): return false
	ocean.take_over_path(ASSETS+"ocean_reflection_material.tres")
	return true
func add_controller(game: Node) -> bool:
	if not require(game.get_node_or_null(NEW_GROUP)==null and FileAccess.file_exists(CONTROLLER),"Reflection controller input missing or existing"): return false
	var node := Node3D.new();node.name="LakeReflection51";node.set_script(load(CONTROLLER))
	node.set("main_camera_path",NodePath("../../Camera"));node.set("ocean_path",NodePath("../Ocean"))
	node.set("clip_enabled",false);node.set("reflection_enabled",false)
	var materials: Array[ShaderMaterial]=[]
	for material in material_factory.materials.values(): materials.append(material)
	node.set("clipping_materials",materials)
	var viewport := SubViewport.new();viewport.name="ReflectionViewport";viewport.size=Vector2i(1180,664)
	viewport.own_world_3d=false;viewport.world_3d=null;viewport.render_target_update_mode=SubViewport.UPDATE_DISABLED;viewport.gui_disable_input=true
	node.add_child(viewport)
	var camera := Camera3D.new();camera.name="ReflectionCamera";camera.current=true
	var main: Camera3D=game.get_node("Camera")
	for key in ["projection","fov","size","frustum_offset","near","far","keep_aspect"]: camera.set(key,main.get(key))
	camera.cull_mask=(main.cull_mask|MARKER)&~WATER_LAYER
	viewport.add_child(camera)
	game.get_node("World").add_child(node);own(node,game)
	return require(node.has_method("set_effect_flags") and node.has_method("refresh_now") and node.has_method("get_diagnostic_state"),"51 controller API mismatch")
func new_state(game: Node) -> Dictionary:
	var all := snapshot(game,false)
	var result := {"new_nodes":{},"bindings":{},"camera_mask":game.get_node("Camera").cull_mask,"ocean_layers":game.get_node("World/Ocean").layers,"ocean":canonical(game.get_node("World/Ocean").material_override)}
	for path in all:
		if path==NEW_GROUP or path.begins_with(NEW_GROUP+"/"): result.new_nodes[path]=all[path]
	for spec in binding_specs: result.bindings[spec.path+"|"+spec.property]=canonical(game.get_node(spec.path).get(spec.property))
	return result
func verify_new_inventory(game: Node) -> bool:
	var expected := {NEW_GROUP:"Node3D",NEW_GROUP+"/ReflectionViewport":"SubViewport",NEW_GROUP+"/ReflectionViewport/ReflectionCamera":"Camera3D"}
	var actual := {}
	var root_node := game.get_node_or_null(NEW_GROUP)
	if root_node==null: return require(false,"Missing51 new controller subtree")
	var nodes: Array[Node]=[root_node];nodes.append_array(root_node.find_children("*","",true,false))
	for node in nodes: actual[str(game.get_path_to(node))]=node.get_class()
	return require(expected==actual,"Strict51 subtree differs",differences(expected,actual))
func build() -> void:
	if not require(DisplayServer.get_name()!="headless","51 requires real renderer for scene save and exact MM fingerprints"): quit(2);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET),"51 source SHA mismatch or existing target; never overwrite"): await abort_build([]);return
	var source: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var game: Node3D=source.instantiate();await settle()
	if not discover_bindings(game) or not validate_reserved_layers(game): await abort_build([game]);return
	var before := graph_state(game,source)
	var weather := weather_state(game)
	if weather.is_empty() or not require(before==graph_state(game,source),"Source50 canonical control drift"): await abort_build([game]);return
	if not apply_materials(game): await abort_build([game]);return
	var ocean := prepare_ocean(game.get_node("World/Ocean").material_override)
	if ocean==null: await abort_build([game]);return
	game.get_node("World/Ocean").material_override=ocean
	game.get_node("World/Ocean").layers=WATER_LAYER
	game.get_node("Camera").cull_mask=game.get_node("Camera").cull_mask&~MARKER
	if not save_material_assets(game) or not add_controller(game) or not verify_new_inventory(game): await abort_build([game]);return
	if not require(before==graph_state(game,source),"51 changed non-allowlisted50 stored graph/resource state",differences(before,graph_state(game,source))): await abort_build([game]);return
	var expected := new_state(game)
	var packed := PackedScene.new()
	if not require(packed.pack(game)==OK,"51 pack failed"): await abort_build([game]);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"51 save failed"): await abort_build([game]);return
	var reload_packed: PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var reloaded: Node3D=reload_packed.instantiate();await settle()
	if not verify_new_inventory(reloaded): await abort_build([game,reloaded]);return
	var after := graph_state(reloaded,reload_packed)
	if not require(before==after,"Reloaded51 changed all-old50 state outside exact binding fields",differences(before,after)) or not require(expected==new_state(reloaded),"51 changed exact intended new bindings/subtree on reload",differences(expected,new_state(reloaded))): await abort_build([game,reloaded]);return
	if not require(weather==weather_state(reloaded),"51 weather48000 floats changed") or not require(FileAccess.get_sha256(BASE)==BASE_SHA,"50 source file changed"): await abort_build([game,reloaded]);return
	var file := FileAccess.open(TARGET,FileAccess.READ);var bytes := file.get_length();file.close()
	if not require(bytes<100*1024*1024,"51 exceeds100MiB",bytes): await abort_build([game,reloaded]);return
	var report := {"build_saved_reload_passed":true,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"candidate_bytes":bytes,"scope_plan_sha256":FileAccess.get_sha256(SCOPE_PATH),"injection_report_sha256":FileAccess.get_sha256(SOURCE_ROOT+"/injection-report.json"),"unaffected_graph_fingerprint":digest(before),"new_state_fingerprint":digest(expected),"exact_property_masks":property_masks,"binding_ledger":binding_ledger,"runtime_scope":runtime_scope,"material_ledger":material_factory.material_ledger,"shader_ledger":material_factory.shader_ledger,"ocean_ledger":ocean_ledger,"asset_inventory":asset_inventory,"weather":weather,"controller_script_sha256":FileAccess.get_sha256(CONTROLLER),"normal_pass_zero_diff":false,"clip_only_zero_diff":false,"limited_geometry_runtime_passed":false,"requested_motion_all_passed":false,"total_acceptance_passed":false,"hardware_gpu_acceptance":false,"visual_acceptance":false,"scope":"114 exact material copies using current51 injection files and strict official-native feature templates; original stored params unchanged except two clip uniforms and audited source insertion. Only explicit authority/direct binding list, stream3, Airship hull/cloth, Camera.cull_mask marker clear and Ocean layer/material changed. All50 geometry/collision/MM/weather48000, other materials/scripts/cameras and complete priorLakeDepth50 controller/images remain exact. New same-world reflection controller/viewport/camera. No scene entered tree during build; Sky settled3frames+postdraw."}
	file=FileAccess.open(DEST+"build-report-51.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	await settle();game.free();reloaded.free();for i in range(8): await process_frame
	print("REFLECTION51 BUILT_RELOADED ",report.candidate_sha256);quit(0)
