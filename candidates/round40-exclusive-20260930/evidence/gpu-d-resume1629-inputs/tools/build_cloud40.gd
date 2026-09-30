extends SceneTree
const DEST := "res://scenes/candidate40/"
func _initialize() -> void: call_deferred("build")
func own(node: Node, owner_node: Node) -> void:
	node.scene_file_path = ""
	if node != owner_node: node.owner = owner_node
	for child in node.get_children(): own(child,owner_node)
func build() -> void:
	assert(not FileAccess.file_exists(DEST+"Game40c.tscn"))
	var sources: Array[Node3D] = []
	var parts: Array = []
	for variant in range(3):
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		var name := "cloud_sea_40_"+str(variant)
		assert(document.append_from_file("res://assets/clouds40/"+name+".glb",state)==OK)
		var cloud: Node3D = document.generate_scene(state)
		own(cloud,cloud)
		var packed := PackedScene.new()
		assert(packed.pack(cloud)==OK)
		assert(ResourceSaver.save(packed,DEST+name+".tscn")==OK)
		sources.append(cloud)
		parts.append({"variant":variant,"mesh_parts":cloud.find_children("*","MeshInstance3D",true,false).size(),"source_sha256":FileAccess.get_sha256("res://assets/clouds40/"+name+".glb")})
	var game: Node3D = load(DEST+"Game40b.tscn").instantiate()
	var region: Node3D = game.get_node("SkyRegion39")
	var count := 0
	for old in region.get_children():
		if not str(old.name).begins_with("CloudSea_"): continue
		var variant := posmod(count*7+count/5,3)
		var replacement: Node3D = sources[variant].duplicate()
		replacement.name = old.name
		replacement.transform = old.transform
		region.remove_child(old)
		old.free()
		region.add_child(replacement)
		count += 1
	for cloud in sources: cloud.free()
	# Persist the already-configured native sky; runtime adjusts its uniforms,
	# never swaps a second environment into this scene during normal boot.
	var env: Environment = game.get_node("Environment").environment
	var sky := Sky.new()
	var material := ShaderMaterial.new()
	material.shader = load("res://scripts/environment39_sky.gdshader")
	sky.sky_material = material
	env.sky = sky
	env.background_mode = Environment.BG_SKY
	own(game,game)
	var packed := PackedScene.new()
	assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,DEST+"Game40c.tscn")==OK)
	var report := {"baseline_game40b_sha256":FileAccess.get_sha256(DEST+"Game40b.tscn"),"candidate_sha256":FileAccess.get_sha256(DEST+"Game40c.tscn"),"cloud_instances":count,"native_cloud_sources":parts,"scope":"Replace shared native cloud resources; same positions, terrain, cabins and islands. Persist shared environment, no world regeneration or camera-specific scenery."}
	var output := FileAccess.open(DEST+"build-report-c.json",FileAccess.WRITE)
	output.store_string(JSON.stringify(report,"  "));output.close()
	game.free()
	print("SHARED CLOUD40 NATIVE BUILT ",report.candidate_sha256)
	quit()
