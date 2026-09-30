extends SceneTree
## Additive candidate only. Requires a successfully serialized 42d and a rendering backend.
const BASE := "res://scenes/candidate42d/Game42d.tscn"
const DEST := "res://scenes/candidate43/"
const TARGET := DEST + "Game43.tscn"
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
		if path.begins_with("SkyRegion39/UpperCloudBank41_") or path.begins_with("SkyRegion39/UpperCloudBank43_"): continue
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
		push_error("Game43 refuses headless serialization: MultiMesh buffers require a renderer")
		quit(2); return
	if not FileAccess.file_exists(BASE) or FileAccess.file_exists(TARGET):
		push_error("42d is missing or Game43 already exists; no old candidate will be overwritten")
		quit(2); return
	var game: Node3D = load(BASE).instantiate()
	# Sky radiance allocation is deferred by the Compatibility renderer.
	# A newly instantiated off-tree Environment must survive at least 3 frames.
	for frame in range(3): await process_frame
	await RenderingServer.frame_post_draw
	assert(weather_valid(game), "42d rain/snow buffer validation failed")
	var before := snapshot(game)
	DirAccess.make_dir_recursive_absolute(DEST)
	var sources: Array[Node3D] = []
	for i in range(3):
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		assert(doc.append_from_file("res://assets/upper43/upper_cloud43_%d.glb" % i,state)==OK)
		var cloud: Node3D = doc.generate_scene(state)
		assert(cloud.find_children("*","MeshInstance3D",true,false).size()==11)
		own(cloud,cloud)
		var prefab := PackedScene.new()
		assert(prefab.pack(cloud)==OK)
		assert(ResourceSaver.save(prefab,DEST+"upper_cloud43_%d.tscn" % i)==OK)
		sources.append(cloud)
	var region: Node3D = game.get_node("SkyRegion39")
	var replaced := []
	for i in range(12):
		var old: Node3D = region.get_node("UpperCloudBank41_%d" % i)
		var cloud: Node3D = sources[i%3].duplicate()
		cloud.name = "UpperCloudBank43_%d" % i
		cloud.transform = Transform3D(old.basis.orthonormalized().scaled(Vector3.ONE*2.0),old.position)
		cloud.set_meta("source_asset43","res://assets/upper43/upper_cloud43_%d.glb" % (i%3))
		replaced.append({"old":str(old.name),"new":str(cloud.name),"position":str(old.position),"scale":"uniform 2.0","parts":11})
		region.remove_child(old); old.free(); region.add_child(cloud)
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
	var report := {"baseline":BASE,"baseline_sha256":FileAccess.get_sha256(BASE),"candidate_sha256":FileAccess.get_sha256(TARGET),"replaced":replaced,"preserved_node_count":before.size(),"preserved_fingerprint":digest(before),"reloaded_preservation":true,"renderer":RenderingServer.get_video_adapter_name(),"visual_acceptance":false,"hardware_gpu_acceptance":false,"sky_lifecycle":"3 process frames + frame_post_draw after each scene instantiate, 8 process frames after freeing","scope":"Only 12 upper cloud assemblies replaced. Full terrain, ports, cabins, world clouds, cloud sea, weather, shared environment and cameras retained. No default scene change. Native .blend source retained."}
	var f := FileAccess.open(DEST+"build-report-43.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"  ")); f.close()
	game.free(); reloaded.free()
	for frame in range(8): await process_frame
	print("UPPER43 BUILT AND RELOADED ", report.candidate_sha256)
	quit()
