extends SceneTree
const DEST := "res://scenes/candidate40/"
func _initialize() -> void: call_deferred("build")
func own(node: Node, owner_node: Node) -> void:
	node.scene_file_path = ""
	if node != owner_node: node.owner = owner_node
	for child in node.get_children(): own(child,owner_node)
func model(name: String) -> Node3D:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file("res://assets/clouds41/"+name+".glb",state)==OK)
	var node: Node3D = document.generate_scene(state)
	own(node,node)
	var packed := PackedScene.new()
	assert(packed.pack(node)==OK)
	assert(ResourceSaver.save(packed,DEST+name+".tscn")==OK)
	return node
func build() -> void:
	assert(not FileAccess.file_exists(DEST+"Game41.tscn"))
	var clouds: Array[Node3D] = []
	var banks: Array[Node3D] = []
	for variant in range(3):
		clouds.append(model("cloud_sea_41_"+str(variant)))
		banks.append(model("cloud_bank_41_"+str(variant)))
	var game: Node3D = load(DEST+"Game40c.tscn").instantiate()
	var region: Node3D = game.get_node("SkyRegion39")
	var count := 0
	for old in region.get_children():
		if not str(old.name).begins_with("CloudSea_"): continue
		var replacement: Node3D = clouds[posmod(count*7+count/5,3)].duplicate()
		replacement.name = old.name
		replacement.transform = old.transform
		region.remove_child(old);old.free();region.add_child(replacement)
		count += 1
	# Independent physical far banks connect the finite near field to the
	# atmosphere in every direction. They remain present during normal flight.
	var far_count := 0
	for x in range(-4,5):
		for z in range(-4,5):
			if abs(x)<3 and abs(z)<3: continue
			var bank: Node3D = banks[posmod(x*11+z*7,3)].duplicate()
			bank.name = "DistantCloudBank41_"+str(x)+"_"+str(z)
			bank.position = Vector3(3200+x*1500,640+posmod(x*5+z*7,5)*30,3000+z*1500)
			bank.rotation.y = float(posmod(x*17+z*13,20))*.31
			bank.scale = Vector3(1.3,1.2,1.3)
			region.add_child(bank);far_count += 1
	var upper_count := 0
	for i in range(8):
		var bank: Node3D = banks[i%3].duplicate()
		bank.name = "HighCloudBand41_"+str(i)
		var angle := TAU*float(i)/8
		bank.position = Vector3(3200+cos(angle)*6500,1600+float(i%3)*180,3000+sin(angle)*6500)
		bank.rotation.y = angle
		bank.scale = Vector3(2.8,.30,.42)
		region.add_child(bank);upper_count += 1
	for node in clouds+banks: node.free()
	own(game,game)
	var packed := PackedScene.new()
	assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,DEST+"Game41.tscn")==OK)
	var report := {"baseline_sha256":FileAccess.get_sha256(DEST+"Game40c.tscn"),"candidate_sha256":FileAccess.get_sha256(DEST+"Game41.tscn"),"near_clouds":count,"distant_banks":far_count,"upper_bands":upper_count,"scope":"Only shared native cloud model and persistent physical region expansion; existing terrain, cabin, collision and light assembly retained."}
	var file := FileAccess.open(DEST+"build-report-41.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	game.free()
	print("SHARED CLOUD41 NATIVE BUILT ",report.candidate_sha256)
	quit()
