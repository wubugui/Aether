extends SceneTree
const BASE := "res://scenes/candidate44/Game44.tscn"
const DEST := "res://scenes/candidate46/"
const TARGET := DEST+"Game46.tscn"
var resource_cache := {}
var game: Node3D
var reloaded: Node3D
var sources: Array[Node3D] = []
var report := {"passed":false,"hardware_gpu_acceptance":false,"visual_acceptance":false,"baseline":BASE,"failures":[]}
var report_path := ""
func _initialize() -> void: call_deferred("build")
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
func settle() -> void:
	for i in range(3): await process_frame
	await RenderingServer.frame_post_draw
func own(node: Node, scene: Node) -> void:
	node.scene_file_path=""
	if node!=scene: node.owner=scene
	for child in node.get_children(): own(child,scene)
func finish(ok: bool, reason: String) -> void:
	report.passed=ok
	if not ok: report.failures.append(reason)
	if not report_path.is_empty():
		var f:=FileAccess.open(report_path,FileAccess.WRITE)
		if f!=null: f.store_string(JSON.stringify(report,"  "));f.close()
	print("CLOUDSEA46 BUILT AND RELOADED" if ok else "CLOUDSEA46 FAILED: "+reason)
	if DisplayServer.get_name()!="headless": await settle()
	for source in sources:
		if is_instance_valid(source): source.free()
	if is_instance_valid(game): game.free()
	if is_instance_valid(reloaded): reloaded.free()
	for i in range(8): await process_frame
	quit(0 if ok else 1)
func weather_valid(node: Node) -> bool:
	for pair in [["Rain",1800],["Snow",1200]]:
		var mm:MultiMesh=node.get_node("Weather42b/"+pair[0]).multimesh
		if mm.instance_count!=pair[1] or mm.buffer.size()!=pair[1]*16 or mm.get_instance_transform(0).basis.determinant()==0: return false
	return true
func differences(a: Dictionary,b: Dictionary) -> Array:
	var rows:=[]
	for key in a:
		if not b.has(key) or a[key]!=b[key]: rows.append(key)
	for key in b:
		if not a.has(key): rows.append("added:"+key)
	return rows
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
func snapshot(game: Node) -> Dictionary:
	resource_cache.clear()
	var data := {}
	var nodes: Array[Node] = [game]
	nodes.append_array(game.find_children("*","",true,false))
	for node in nodes:
		var path := str(game.get_path_to(node))
		if path.begins_with("SkyRegion39/CloudSea_") and path.split("/").size()>2: continue
		var row := {"class":node.get_class()}
		for property in node.get_property_list():
			var key: String = property.name
			if not property.usage & PROPERTY_USAGE_STORAGE or key in ["owner","scene_file_path"]: continue
			row[key] = canonical(node.get(key))
		if node is MultiMeshInstance3D and node.multimesh != null:
			var mm: MultiMesh = node.multimesh
			row.exact_multimesh_buffer = digest(mm.buffer)
			row.exact_multimesh_config = [mm.instance_count,mm.visible_instance_count,mm.transform_format,mm.use_colors,mm.use_custom_data]
		data[path] = row
	return data
func build() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--report-path="): report_path=arg.trim_prefix("--report-path=")
	if report_path.is_empty(): report_path="res://build-failure46-%d.json" % Time.get_unix_time_from_system()
	if DisplayServer.get_name()=="headless": await finish(false,"Renderer required; no headless serialization");return
	if not FileAccess.file_exists(BASE) or FileAccess.file_exists(TARGET): await finish(false,"Missing44 or existing46; refusing overwrite");return
	report.baseline_sha256=FileAccess.get_sha256(BASE)
	game=load(BASE).instantiate()
	await settle()
	if not weather_valid(game): await finish(false,"Original weather buffers invalid");return
	var before:=snapshot(game)
	var control:=snapshot(game)
	if before!=control: report.differences=differences(before,control);await finish(false,"Unmodified double-snapshot control drift; audit invalid");return
	var region:Node3D=game.get_node("SkyRegion39")
	var inventory:=[]
	var expression:=RegEx.new()
	expression.compile("^cloud_sea_41_([012])_")
	for node in region.get_children():
		if not str(node.name).begins_with("CloudSea_"): continue
		var meshes:=node.find_children("*","MeshInstance3D",true,false)
		if meshes.size()!=20: await finish(false,"Original sea must contain20 meshes: "+str(node.name));return
		var variant:=-1
		var evidence:=[]
		var material:Material=meshes[0].get_active_material(0)
		for mesh in meshes:
			var match_result:=expression.search(str(mesh.name))
			if match_result==null: await finish(false,"Cannot identify original variant from "+str(mesh.name));return
			var found:=int(match_result.get_string(1))
			if variant!=-1 and found!=variant: await finish(false,"Mixed original variant in "+str(node.name));return
			variant=found;evidence.append(str(mesh.name))
			if material==null or canonical(mesh.get_active_material(0))!=canonical(material): await finish(false,"Mixed/null original sea material");return
		inventory.append({"node":str(node.name),"variant":variant,"transform":node.transform,"mesh_names":evidence,"original_material_fingerprint":canonical(material)})
	if inventory.size()!=25: await finish(false,"Expected exactly25 sea assemblies");return
	DirAccess.make_dir_recursive_absolute(DEST)
	for variant in range(3):
		var doc:=GLTFDocument.new();var state:=GLTFState.new()
		if doc.append_from_file("res://assets/clouds46/cloud_sea_46_%d.glb" % variant,state)!=OK: await finish(false,"GLB parse failure");return
		var cloud:Node3D=doc.generate_scene(state)
		if cloud==null: await finish(false,"GLB scene generation failed");return
		sources.append(cloud)
		if cloud.find_children("*","MeshInstance3D",true,false).size()!=1: await finish(false,"46 variant must contain1 mesh");return
		own(cloud,cloud)
		var prefab:=PackedScene.new()
		if prefab.pack(cloud)!=OK or ResourceSaver.save(prefab,DEST+"cloud_sea_46_%d.tscn" % variant)!=OK: await finish(false,"Prefab save failure");return
	for row in inventory:
		var node:Node3D=region.get_node(row.node)
		var old_mesh:MeshInstance3D=node.find_children("*","MeshInstance3D",true,false)[0]
		var material:Material=old_mesh.get_active_material(0)
		var source:MeshInstance3D=sources[row.variant].find_children("*","MeshInstance3D",true,false)[0]
		var mesh:MeshInstance3D=source.duplicate()
		mesh.material_override=material
		for child in node.get_children(): node.remove_child(child);child.free()
		node.add_child(mesh)
	if before!=snapshot(game): report.differences=differences(before,snapshot(game));await finish(false,"Unrelated state changed before serialization");return
	own(game,game)
	var packed:=PackedScene.new()
	if packed.pack(game)!=OK or ResourceSaver.save(packed,TARGET)!=OK: await finish(false,"Candidate pack/save failure");return
	reloaded=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	await settle()
	var after:=snapshot(reloaded)
	if before!=after: report.differences=differences(before,after);await finish(false,"Reload changed unrelated stored state");return
	if not weather_valid(reloaded): await finish(false,"Reload changed weather buffers");return
	for row in inventory:
		var node:Node3D=reloaded.get_node("SkyRegion39/"+row.node)
		var meshes:=node.find_children("*","MeshInstance3D",true,false)
		if node.transform!=row.transform or meshes.size()!=1: await finish(false,"Reload changed placement/count");return
		if canonical(meshes[0].get_active_material(0))!=row.original_material_fingerprint: await finish(false,"Reload changed original active material");return
	if FileAccess.get_sha256(BASE)!=report.baseline_sha256: await finish(false,"Original44 changed");return
	report.inventory=inventory;report.candidate=TARGET;report.candidate_sha256=FileAccess.get_sha256(TARGET)
	report.preserved_node_count=before.size();report.preserved_fingerprint=digest(before);report.reload_exact=true
	report.renderer=RenderingServer.get_video_adapter_name()
	report.scope="Game44 geometry candidate: only children of25 original CloudSea roots replaced, variant identified from all20 original mesh names. Original root properties/transforms, all unrelated stored state and exact48000-float precipitation buffers preserved. Original44 active sea materials retained; no45 changes."
	await finish(true,"")
