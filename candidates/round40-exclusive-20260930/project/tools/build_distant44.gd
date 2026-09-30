extends SceneTree
## Additive distant-bank candidate. Only 56 original DistantCloudBank41 placements change meshes.
const BASE := "res://scenes/candidate43/Game43.tscn"
const DEST := "res://scenes/candidate44/"
const TARGET := DEST + "Game44.tscn"
var resource_cache := {}
func _initialize() -> void: call_deferred("build")
func own(node: Node, root_node: Node) -> void:
	node.scene_file_path = ""
	if node != root_node: node.owner = root_node
	for child in node.get_children(): own(child, root_node)
func digest(value: Variant) -> String:
	return var_to_bytes(value).hex_encode().sha256_text()
func snapshot(game: Node) -> Dictionary:
	var data := {}
	resource_cache.clear()
	for node in game.find_children("*", "", true, false):
		var path := str(game.get_path_to(node))
		if path.begins_with("SkyRegion39/DistantCloudBank41_"): continue
		var row := {"class":node.get_class(),"script":node.get_script().resource_path if node.get_script() != null else ""}
		if node is Node3D: row.transform = node.transform
		if node is MultiMeshInstance3D:
			var mm: MultiMesh = node.multimesh
			row.multimesh = [mm.instance_count,mm.visible_instance_count,mm.transform_format,mm.use_colors,mm.use_custom_data,digest(mm.buffer)]
		if node is MeshInstance3D and node.mesh != null:
			var mesh: Mesh = node.mesh
			if not resource_cache.has(mesh.get_instance_id()): resource_cache[mesh.get_instance_id()] = digest(mesh.get_faces())
			row.mesh = resource_cache[mesh.get_instance_id()]
		if node is CollisionShape3D:
			row.collision_type = node.shape.get_class() if node.shape != null else "none"
			if node.shape is ConcavePolygonShape3D: row.collision_faces = digest(node.shape.get_faces())
		data[path] = row
	return data
func weather_valid(game: Node) -> bool:
	for pair in [["Rain",1800],["Snow",1200]]:
		var mm: MultiMesh = game.get_node("Weather42b/"+pair[0]).multimesh
		if mm.instance_count != pair[1] or mm.buffer.size() != pair[1]*16: return false
		if mm.get_instance_transform(0).basis.determinant() == 0: return false
	return true
func build() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Game44 refuses headless serialization: MultiMesh buffers require a renderer")
		quit(2); return
	if not FileAccess.file_exists(BASE) or FileAccess.file_exists(TARGET):
		push_error("43 is missing or Game44 already exists; no old candidate will be overwritten")
		quit(2); return
	var game: Node3D = load(BASE).instantiate()
	# Sky radiance allocation is deferred by the Compatibility renderer.
	# A newly instantiated off-tree Environment must survive at least 3 frames.
	for frame in range(3): await process_frame
	await RenderingServer.frame_post_draw
	assert(weather_valid(game), "43 rain/snow buffer validation failed")
	var before := snapshot(game)
	DirAccess.make_dir_recursive_absolute(DEST)
	var sources: Array[Node3D] = []
	for i in range(3):
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		assert(doc.append_from_file("res://assets/clouds44/cloud_bank_44_%d.glb" % i,state)==OK)
		var cloud: Node3D = doc.generate_scene(state)
		assert(cloud.find_children("*","MeshInstance3D",true,false).size()==21)
		own(cloud,cloud)
		var prefab := PackedScene.new()
		assert(prefab.pack(cloud)==OK)
		assert(ResourceSaver.save(prefab,DEST+"cloud_bank_44_%d.tscn" % i)==OK)
		sources.append(cloud)
	var region: Node3D = game.get_node("SkyRegion39")
	var replaced := []
	for x in range(-4,5):
		for z in range(-4,5):
			if absi(x)<3 and absi(z)<3: continue
			var name := "DistantCloudBank41_%d_%d" % [x,z]
			var old: Node3D = region.get_node(name)
			var variant := posmod(x*3+z,3)
			var cloud: Node3D = sources[variant].duplicate()
			cloud.name = old.name
			cloud.transform = old.transform
			cloud.set_meta("source_asset44","res://assets/clouds44/cloud_bank_44_%d.glb" % variant)
			replaced.append({"node":name,"transform":old.transform,"variant":variant,"parts":21})
			region.remove_child(old); old.free(); region.add_child(cloud)
	assert(replaced.size()==56,"Exact original distant-bank placement count required")
	for cloud in sources: cloud.free()
	own(game,game)
	assert(before == snapshot(game), "Unrelated world data changed before serialization")
	var packed := PackedScene.new()
	assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,TARGET)==OK)
	var reloaded: Node3D = ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	# CACHE_MODE_IGNORE creates a second Sky; allow its renderer allocation
	# to complete before freeing, or two 349524-byte GL textures can leak.
	for frame in range(3): await process_frame
	await RenderingServer.frame_post_draw
	var after := snapshot(reloaded)
	assert(before == after, "Reload changed unrelated geometry/transforms/scripts/MultiMesh/collision")
	assert(weather_valid(reloaded), "Reloaded weather buffer missing")
	for row in replaced:
		var restored: Node3D = reloaded.get_node("SkyRegion39/"+row.node)
		assert(restored.transform==row.transform,"Exact distant-bank transform was not preserved")
		assert(restored.find_children("*","MeshInstance3D",true,false).size()==21,"Distant-bank parts missing after reload")
	var report := {"baseline":BASE,"baseline_sha256":FileAccess.get_sha256(BASE),"candidate_sha256":FileAccess.get_sha256(TARGET),"replaced":replaced,"preserved_node_count":before.size(),"preserved_fingerprint":digest(before),"reloaded_preservation":true,"renderer":RenderingServer.get_video_adapter_name(),"visual_acceptance":false,"hardware_gpu_acceptance":false,"sky_lifecycle":"3 process frames + frame_post_draw after each scene instantiate, 8 process frames after freeing","scope":"Only 56 exact DistantCloudBank41 assemblies replaced; original node names, transforms and variant pattern preserved. All upper43 clouds, terrain, ports, cabins, world clouds, cloud sea, weather, environment and cameras retained. No default scene change. Native .blend source retained."}
	var f := FileAccess.open(DEST+"build-report-44.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"  ")); f.close()
	game.free(); reloaded.free()
	for frame in range(8): await process_frame
	print("DISTANT44 BUILT AND RELOADED ", report.candidate_sha256)
	quit()
