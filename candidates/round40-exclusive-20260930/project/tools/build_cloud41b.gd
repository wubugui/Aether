extends SceneTree
const DEST := "res://scenes/candidate41b/"
func _initialize() -> void: call_deferred("build")
func own(node: Node, root_node: Node) -> void:
	node.scene_file_path = ""
	if node != root_node: node.owner = root_node
	for child in node.get_children(): own(child,root_node)
func source(name: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file("res://assets/clouds41/"+name+".glb",state)==OK)
	var cloud: Node3D = document.generate_scene(state)
	own(cloud,cloud)
	var packed := PackedScene.new()
	assert(packed.pack(cloud)==OK)
	assert(ResourceSaver.save(packed,DEST+name+".tscn")==OK)
	return cloud
func build() -> void:
	assert(not FileAccess.file_exists(DEST+"Game41b.tscn"))
	var sources: Array[Node3D] = []
	var banks: Array[Node3D] = []
	for variant in range(3):
		sources.append(source("cloud_sea_41_"+str(variant)))
		banks.append(source("cloud_bank_41_"+str(variant)))
	var game: Node3D = load("res://scenes/candidate40/Game40c.tscn").instantiate()
	var region: Node3D = game.get_node("SkyRegion39")
	var count := 0
	for old in region.get_children():
		if not str(old.name).begins_with("CloudSea_"): continue
		var replacement: Node3D = sources[posmod(count*7+count/5,3)].duplicate()
		replacement.name = old.name
		replacement.transform = old.transform
		region.remove_child(old);old.free();region.add_child(replacement)
		count += 1
	# Physical distant banks surrounding the entire authored region, visible
	# from any side and from cabin windows. Different LOD sources retain editability.
	var distant := 0
	for x in range(-4,5):
		for z in range(-4,5):
			if absi(x)<3 and absi(z)<3: continue
			var variant := posmod(x*3+z,3)
			var bank: Node3D = banks[variant].duplicate()
			bank.name = "DistantCloudBank41_"+str(x)+"_"+str(z)
			bank.position = Vector3(3200+x*1400,650+posmod(x*13+z*7,5)*27,3000+z*1400)
			bank.rotation.y = float(posmod(x*17+z*11,31))*.21
			region.add_child(bank)
			distant += 1
	# Upper banks are distinct real cloud groups, not a screen-space sky texture.
	for i in range(12):
		var high: Node3D = banks[i%3].duplicate()
		high.name = "UpperCloudBank41_"+str(i)
		var angle := TAU*float(i)/12
		high.position = Vector3(3200+cos(angle)*6500,1650+posmod(i*7,4)*120,3000+sin(angle)*6500)
		high.scale = Vector3(1.5,.7,1.15)
		high.rotation.y = angle
		region.add_child(high)
	for cloud in sources+banks: cloud.free()
	own(game,game)
	var packed := PackedScene.new()
	assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,DEST+"Game41b.tscn")==OK)
	var report := {"baseline_sha256":FileAccess.get_sha256("res://scenes/candidate40/Game40c.tscn"),"candidate_sha256":FileAccess.get_sha256(DEST+"Game41b.tscn"),"near_cloud_instances":count,"distant_cloud_banks":distant,"upper_cloud_banks":12,"scope":"Shared editable modeled clouds, preserved terrain/cabins/collision/lights. No environment switching or camera-specific assets."}
	var file := FileAccess.open(DEST+"build-report-41b.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	game.free()
	print("CLOUD41 BUILT ",report.candidate_sha256)
	quit()
